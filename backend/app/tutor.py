"""The AI tutor (v2 spec 6.2), on top of the LLM gateway and the learner's own budget.

"Ask the tutor" on a task that is not passed yet: a Socratic nudge built from the task, the hints
already revealed, the last check result and the learner's files. "Review my code" after a task
passes: a short senior-engineer review. A tutor reply is never allowed to contain a line of the
reference solution; if the model writes one anyway, the reply is replaced by a safe nudge.
"""
import json
import re
from pathlib import Path

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, col, select

from . import llm_gateway, progress
from .labs import LabConfig
from .models import CheckRun, Workspace

FILE_MAX = 4_000  # characters per file sent to the model
FILES_MAX = 12_000  # all files together
TUTOR_ALIAS = "lab-chat-smart"
SKIP_SUFFIXES = {".xml", ".mod", ".md", ".json", ".lock", ".sum"}

TUTOR_RULES = """You are the LabBox tutor, helping a learner who is stuck on one task in a hands-on coding lab.
Rules, all of them, always:
- Be Socratic. Point to ONE thing to look at, then ask ONE question that helps them find the fix.
- Never write the solution, never write the fixed code, never give a complete command or line that solves the task.
- Do not write code blocks or commands. Name the concept or the command, never the full line with its values.
- At most 120 words. Plain, friendly English. No headings.
- If their code has a small bug, name where it is (file and what to look at), not the fix.
"""

REVIEW_RULES = """You are a senior engineer reviewing a learner's code that already passes its tests in a hands-on lab.
Give a short pull-request style review: 2 to 4 bullet points on naming, edge cases, performance or what
would matter in production. Be specific and kind. Start with one line on what is good. At most 150 words.
"""


class TutorReply(BaseModel):
    reply: str
    blocked: bool = False  # the model tried to give away the solution; this is a safe nudge instead
    tokens_used_today: int


def _key(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def _code(text: str) -> str:
    """Code with spaces and quotes removed, symbols kept: `HSET menu "a b" 1` and `hset menu a b 1`
    match, `n % 2 == 0` and `n % 2 != 0` do not."""
    return re.sub(r"[\s'\"`]+", "", text.lower())


def _words(text: str) -> str:
    """Lower-case words only: quotes, brackets and punctuation do not hide a copied line."""
    return " ".join(re.findall(r"[a-z0-9_.:]+", text.lower()))


# Shell wrappers in solution/apply.sh that are not part of what the learner would type.
_WRAPPERS = re.compile(r'^\s*("\$\{R\[@\]\}"|redis-cli|psql( -[a-zA-Z]+( [^ ]+)?)*|git)\s+')
_SHELL_NOISE = ("set ", "cd ", "for ", "done", "exit", "cat ", "sleep", "if ", "fi", "then", "export ", "R=(")


def solution_lines(lab: LabConfig) -> set[str]:
    """What the tutor must never write: meaningful solution lines (code files and the commands in
    apply.sh), minus anything the starter or the lesson text already shows. Compared with _code."""
    sol, starter = lab.root / "solution", lab.starter_dir
    shown = "\n".join(_code(line) for c in lab.chapters for line in lab.chapter_markdown(c.id).splitlines())
    out: set[str] = set()
    for f in sol.rglob("*") if sol.is_dir() else []:
        if not f.is_file() or f.suffix in SKIP_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        old = starter / f.relative_to(sol)
        before = {_code(x) for x in old.read_text(encoding="utf-8").splitlines()} if old.is_file() else set()
        for ln in text.splitlines():
            k = _key(ln)
            if f.name == "apply.sh":
                if not k or k.startswith(_SHELL_NOISE) or k.startswith("#"):
                    continue
                k = _WRAPPERS.sub("", k).split(" >")[0]
            if len(k) < 10 or k.startswith(("#", "//", "--", "import ", "package ", "from ")):
                continue
            c = _code(k)
            if len(_words(k).split()) >= 3 and c not in before and c not in shown:
                out.add(c)
    return out


def leaks(reply: str, lab: LabConfig) -> bool:
    text = _code(reply)
    return any(line in text for line in solution_lines(lab))


_FENCE = re.compile(r"```.*?(```|$)", re.S)


def strip_code(reply: str) -> str:
    """The tutor gives nudges, not code: small models write code blocks anyway, so they are removed."""
    return re.sub(r"\n{3,}", "\n\n", _FENCE.sub("", reply)).strip()


def learner_files(lab: LabConfig, ws: Workspace | None, chapter_id: str | None = None) -> str:
    """The learner's versions of the starter files, capped. In a lab where each chapter has its own folder
    (named like the chapter, as in Spring Boot), only that chapter's folder: the files the task is about,
    instead of the first chapters' files filling the budget."""
    if ws is None:
        return "(no files yet)"
    root = Path(ws.volume_path)
    base = lab.starter_dir
    if chapter_id and (lab.starter_dir / chapter_id).is_dir():
        base = lab.starter_dir / chapter_id
    parts, total = [], 0
    for f in sorted(base.rglob("*")) if base.is_dir() else []:
        if not f.is_file() or f.suffix in SKIP_SUFFIXES:
            continue
        rel = f.relative_to(lab.starter_dir).as_posix()
        mine = root / rel
        try:
            text = mine.read_text(encoding="utf-8")[:FILE_MAX] if mine.is_file() else "(missing)"
        except (UnicodeDecodeError, OSError):
            continue
        if total + len(text) > FILES_MAX:
            break
        total += len(text)
        parts.append(f"--- {rel} ---\n{text}")
    return "\n".join(parts) or "(no files)"


def last_check(session: Session, user_id: int, lab: LabConfig, task_id: str) -> str:
    runs = session.exec(
        select(CheckRun).where(CheckRun.user_id == user_id, CheckRun.lab_id == lab.id).order_by(col(CheckRun.id).desc()).limit(5)
    ).all()
    for run in runs:
        for r in json.loads(run.results_json or "[]"):
            if r.get("task") == task_id:
                bits = [f"passed: {r.get('passed')}", f"message: {r.get('message', '')}"]
                if r.get("expected") is not None:
                    bits += [f"expected: {r['expected']}", f"actual: {r.get('actual')}"]
                return "\n".join(bits) + f"\noutput tail:\n{(run.output_tail or '')[-1500:]}"
    return "(they have not pressed Check for this task yet)"


def task_text(lab: LabConfig, chapter_id: str, task_id: str) -> str:
    for step in lab.chapter_steps(chapter_id):
        if step.task == task_id:
            return step.markdown
    return lab.task(chapter_id, task_id).title


def _safe_nudge(lab: LabConfig, chapter_id: str, task_id: str, hints_used: int) -> str:
    """Used when the model wrote a solution line. Only repeats a hint they already paid for."""
    task = lab.task(chapter_id, task_id)
    if hints_used:
        return f"I nearly gave you the answer there, so let's go back to your last hint: {task.hints[hints_used - 1]} What happens when you try that?"
    return "I nearly gave you the answer there. Read the check message line by line: what does it expect that your code does not do yet?"


async def ask(session: Session, user_id: int, lab: LabConfig, chapter_id: str, task_id: str, question: str, ws: Workspace | None) -> TutorReply:
    task = lab.task(chapter_id, task_id)
    used = progress.hints_used(session, user_id, lab.id).get(task_id, 0)
    context = (
        f"Lab: {lab.title}\nTask: {task.title}\n\nWhat the task asks:\n{task_text(lab, chapter_id, task_id)}\n\n"
        f"Hints they have already seen:\n" + ("\n".join(f"- {h}" for h in task.hints[:used]) or "(none)") + "\n\n"
        f"Last check for this task:\n{last_check(session, user_id, lab, task_id)}\n\n"
        f"Their files:\n{learner_files(lab, ws, chapter_id)}\n\n"
        f"The learner asks: {question.strip() or 'I am stuck. What should I look at?'}"
    )
    reply = strip_code(await _complete(user_id, lab, TUTOR_RULES, context, "tutor"))
    if leaks(reply, lab) or len(_words(reply).split()) < 6:
        return TutorReply(reply=_safe_nudge(lab, chapter_id, task_id, used), blocked=True, tokens_used_today=llm_gateway.tokens_used_today(user_id))
    return TutorReply(reply=reply, tokens_used_today=llm_gateway.tokens_used_today(user_id))


async def review(session: Session, user_id: int, lab: LabConfig, chapter_id: str, task_id: str, ws: Workspace | None) -> TutorReply:
    task = lab.task(chapter_id, task_id)
    if not progress.task_progress(session, user_id, lab.id, chapter_id, task_id).passed:
        raise HTTPException(409, "Pass the task first; the review is for working code.")
    context = f"Lab: {lab.title}\nTask: {task.title}\n\nWhat the task asked:\n{task_text(lab, chapter_id, task_id)}\n\nTheir passing files:\n{learner_files(lab, ws, chapter_id)}"
    reply = await _complete(user_id, lab, REVIEW_RULES, context, "review")
    return TutorReply(reply=reply, tokens_used_today=llm_gateway.tokens_used_today(user_id))


async def _complete(user_id: int, lab: LabConfig, rules: str, context: str, endpoint: str) -> str:
    ident = llm_gateway.Identity(user_id, lab.id)
    body = {"model": TUTOR_ALIAS, "messages": [{"role": "system", "content": rules}, {"role": "user", "content": context}], "max_tokens": 300, "temperature": 0.3}
    try:
        out = await llm_gateway.chat(ident, body, endpoint=endpoint)
    except llm_gateway.GatewayError as e:
        raise HTTPException(e.status if e.status in (429, 503) else 502, e.message)
    return ((out.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip() or "Sorry, I have nothing useful to add. Try the next hint."
