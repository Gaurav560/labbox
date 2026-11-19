"""AI code completion for the editor: ghost text the learner accepts with Tab.

Uses the `lab-code` alias (a fill-in-the-middle code model) through the LLM gateway, with its own
per-user limits so typing never uses up the tutor's budget. A suggestion that would write a line of
the task's reference solution is dropped, the same guard the tutor uses.
"""
from fastapi import HTTPException
from pydantic import BaseModel, Field

from . import llm_gateway, tutor
from .config import get_settings
from .labs import LabConfig

PREFIX_CHARS = 2_000  # code before the cursor sent to the model
SUFFIX_CHARS = 600  # code after the cursor
MAX_LINES = 6
ALIAS = "lab-code"


class CompleteBody(BaseModel):
    path: str = Field(max_length=300)
    prefix: str = Field(max_length=20_000)
    suffix: str = Field(default="", max_length=20_000)


class CompleteOut(BaseModel):
    text: str  # empty: nothing to suggest


def _trim(text: str, suffix: str) -> str:
    """Keep a short, clean suggestion: at most a few lines, never repeating what follows the cursor."""
    text = "\n".join(l for l in text.split("\n") if not l.lstrip().startswith("```"))  # models sometimes add markdown fences
    text = text.lstrip("\n").split("\n\n", 1)[0]  # one block: stop before the model invents the next function
    lines = text.split("\n")[:MAX_LINES]
    while len(lines) > 1 and not lines[-1].strip():
        lines.pop()
    text = "\n".join(lines).rstrip() if len(lines) > 1 else lines[0].rstrip()
    after = suffix.lstrip("\n").split("\n", 1)[0].strip()
    if after and text.strip().endswith(after):
        text = text[: text.rstrip().rfind(after)].rstrip()
    return text


async def complete(user_id: int, lab: LabConfig, body: CompleteBody) -> CompleteOut:
    if not get_settings().AI_COMPLETION or ALIAS not in get_settings().llm_models:
        return CompleteOut(text="")
    # An empty suffix makes Ollama drop fill-in-the-middle and answer like a chat model, so send at least a newline.
    prefix, suffix = body.prefix[-PREFIX_CHARS:], body.suffix[:SUFFIX_CHARS] or "\n"
    req = {"model": ALIAS, "prompt": prefix, "suffix": suffix, "max_tokens": 64, "temperature": 0.1}
    try:
        out = await llm_gateway.completions(llm_gateway.Identity(user_id, lab.id), req, endpoint=llm_gateway.COMPLETION)
    except llm_gateway.GatewayError as e:
        raise HTTPException(e.status if e.status in (429, 503) else 502, e.message)
    text = _trim(((out.get("choices") or [{}])[0].get("text") or ""), suffix)
    current_line = prefix.rsplit("\n", 1)[-1]
    if not text.strip() or tutor.leaks(current_line + text, lab):
        return CompleteOut(text="")
    return CompleteOut(text=text)
