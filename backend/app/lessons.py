"""Split chapter markdown (v2) into steps.

A chapter is a list of `:::step{type=... title="..." task=...}` blocks. Inside a step,
other directives (`:::tip`, `:::character{...}`, ...) nest and close with `:::`. Those
inner directives are rendered by the frontend (remark-directive); here we only find the
step boundaries and pull out the parts the server must own (predict answers).

A chapter with no step markers (v1) is one `concept` step holding the whole file.
"""
import re
from typing import Literal

from pydantic import BaseModel

StepType = Literal["story", "concept", "example", "predict", "try", "task", "incident", "recap", "deep-dive", "design"]
STEP_TYPES: tuple[str, ...] = StepType.__args__  # type: ignore[attr-defined]

_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_OPEN_RE = re.compile(r"^\s{0,3}(:{3,})([a-z][a-z0-9-]*)(\{.*\})?\s*$")
_CLOSE_RE = re.compile(r"^\s{0,3}(:{3,})\s*$")
_ATTR_RE = re.compile(r'([a-zA-Z_][\w-]*)=(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'}]+))')
_OPTION_RE = re.compile(r"^\s{0,3}[-*] \[( |x|X)\] (.+)$")


class LessonError(ValueError):
    pass


class PredictOption(BaseModel):
    text: str


class Predict(BaseModel):
    question: str  # markdown
    options: list[PredictOption]
    answer: int  # index into options
    explain: str = ""  # markdown


class DesignQuestion(BaseModel):
    id: str
    text: str  # markdown


class Step(BaseModel):
    type: StepType
    title: str | None = None
    task: str | None = None
    minutes: int | None = None  # incident countdown
    markdown: str  # body, rendered by the frontend
    predict: Predict | None = None
    questions: list[DesignQuestion] = []  # design steps: short written answers, graded with tests/rubric.yaml


def _closes_fence(line: str, fence: str) -> bool:
    """A closing code fence: the same character, at least as long, nothing else on the line."""
    t = line.strip()
    return t.startswith(fence) and t.strip(fence[0]) == ""


def parse_attrs(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    return {m.group(1): next(g for g in m.groups()[1:] if g is not None) for m in _ATTR_RE.finditer(raw[1:-1])}


def _blocks(lines: list[str]) -> list[tuple[str, dict[str, str] | None, list[str]]]:
    """Top-level blocks: ("step", attrs, body lines) or ("text", None, lines)."""
    out: list[tuple[str, dict[str, str] | None, list[str]]] = []
    text: list[str] = []
    body: list[str] = []
    attrs: dict[str, str] | None = None
    depth = 0  # open directives, counting the step itself
    fence: str | None = None

    for line in lines:
        if fence is not None:
            # Inside a code block nothing is a directive.
            (body if depth else text).append(line)
            if _closes_fence(line, fence):
                fence = None
            continue
        m = _FENCE_RE.match(line)
        if m:
            fence = m.group(1)
            (body if depth else text).append(line)
            continue
        opened = _OPEN_RE.match(line)
        if depth == 0:
            if opened and opened.group(2) == "step":
                if any(t.strip() for t in text):
                    out.append(("text", None, text))
                text = []
                attrs, body, depth = parse_attrs(opened.group(3)), [], 1
            else:
                text.append(line)
            continue
        if opened:
            depth += 1
        elif _CLOSE_RE.match(line):
            depth -= 1
            if depth == 0:
                out.append(("step", attrs, body))
                continue
        body.append(line)
    if depth:
        out.append(("step", attrs, body))  # unclosed last step: forgive it
    if any(t.strip() for t in text):
        out.append(("text", None, text))
    return out


def _take_directive(lines: list[str], name: str) -> tuple[str | None, list[str]]:
    """Remove the first top-level `:::name ... :::` block; return (its inner markdown, other lines)."""
    for i, line in enumerate(lines):
        m = _OPEN_RE.match(line)
        if not (m and m.group(2) == name):
            continue
        depth = 1
        for j in range(i + 1, len(lines)):
            if _OPEN_RE.match(lines[j]):
                depth += 1
            elif _CLOSE_RE.match(lines[j]):
                depth -= 1
                if depth == 0:
                    return "\n".join(lines[i + 1 : j]).strip(), lines[:i] + lines[j + 1 :]
        return "\n".join(lines[i + 1 :]).strip(), lines[:i]
    return None, lines


def _parse_predict(lines: list[str]) -> tuple[Predict, list[str]]:
    question, rest = _take_directive(lines, "question")
    explain, rest = _take_directive(rest, "explain")
    options: list[PredictOption] = []
    answers: list[int] = []
    remaining: list[str] = []
    for line in rest:
        m = _OPTION_RE.match(line)
        if m:
            if m.group(1) in "xX":
                answers.append(len(options))
            options.append(PredictOption(text=m.group(2).strip()))
        else:
            remaining.append(line)
    if question is None:
        raise LessonError("predict step has no :::question block")
    if len(options) < 2:
        raise LessonError("predict step needs at least 2 options (- [ ] ...)")
    if len(answers) != 1:
        raise LessonError("predict step needs exactly one correct option (- [x] ...)")
    return Predict(question=question, options=options, answer=answers[0], explain=explain or ""), remaining


def _parse_design(lines: list[str]) -> tuple[list[DesignQuestion], list[str]]:
    """`:::ask{id=redis_down}` blocks are the questions; everything else is the step's intro."""
    questions: list[DesignQuestion] = []
    rest = lines
    while True:
        idx = next((i for i, l in enumerate(rest) if (m := _OPEN_RE.match(l)) and m.group(2) == "ask"), None)
        if idx is None:
            break
        qid = parse_attrs(_OPEN_RE.match(rest[idx]).group(3)).get("id", "")  # type: ignore[union-attr]
        text, rest = _take_directive(rest, "ask")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", qid):
            raise LessonError(f"design question needs an id like id=redis_down (got {qid!r})")
        if any(q.id == qid for q in questions):
            raise LessonError(f"design question id {qid!r} is used twice")
        questions.append(DesignQuestion(id=qid, text=text or ""))
    if not 1 <= len(questions) <= 5:
        raise LessonError("design step needs 1 to 5 :::ask{id=...} questions")
    return questions, rest


def _int_or_none(v: str | None) -> int | None:
    return int(v) if v and v.isdigit() else None


def parse_steps(markdown: str) -> list[Step]:
    """Raises LessonError on a malformed v2 chapter."""
    blocks = _blocks(markdown.splitlines())
    if not any(kind == "step" for kind, _, _ in blocks):
        return [Step(type="concept", markdown=markdown.strip())]

    steps: list[Step] = []
    for kind, attrs, lines in blocks:
        if kind == "text":
            # Loose text between steps becomes its own concept step instead of vanishing.
            steps.append(Step(type="concept", markdown="\n".join(lines).strip()))
            continue
        assert attrs is not None
        step_type = attrs.get("type", "concept")
        if step_type not in STEP_TYPES:
            raise LessonError(f"unknown step type {step_type!r} (use one of: {', '.join(STEP_TYPES)})")
        predict = None
        questions: list[DesignQuestion] = []
        if step_type == "predict":
            predict, lines = _parse_predict(lines)
        if step_type == "design":
            questions, lines = _parse_design(lines)
        if step_type in ("task", "incident") and not attrs.get("task"):
            raise LessonError(f"{step_type} step needs a task=... attribute")
        steps.append(
            Step(
                type=step_type,  # type: ignore[arg-type]
                title=attrs.get("title"),
                task=attrs.get("task"),
                minutes=_int_or_none(attrs.get("minutes")),
                markdown="\n".join(lines).strip(),
                predict=predict,
                questions=questions,
            )
        )
    return steps


# ---------- what the browser may see ----------
# Predict answers and explanations stay on the server until the learner answers correctly.


class PublicPredict(BaseModel):
    question: str
    options: list[PredictOption]


class PublicStep(BaseModel):
    type: StepType
    title: str | None = None
    task: str | None = None
    minutes: int | None = None
    markdown: str
    predict: PublicPredict | None = None
    questions: list[DesignQuestion] = []


def public_step(step: Step) -> PublicStep:
    return PublicStep(
        type=step.type,
        title=step.title,
        task=step.task,
        minutes=step.minutes,
        markdown=step.markdown,
        predict=PublicPredict(question=step.predict.question, options=step.predict.options) if step.predict else None,
        questions=step.questions,
    )


_CORRECT_RE = re.compile(r"^(\s{0,3}[-*] )\[[xX]\]")


def redact_markdown(markdown: str) -> str:
    """The raw chapter with predict answers hidden: every option unticked, :::explain blocks removed."""
    out: list[str] = []
    fence: str | None = None
    skip_depth = 0  # > 0 while inside an :::explain block
    for line in markdown.splitlines():
        if fence is not None:
            if _closes_fence(line, fence):
                fence = None
            if not skip_depth:
                out.append(line)
            continue
        m = _FENCE_RE.match(line)
        if m:
            fence = m.group(1)
            if not skip_depth:
                out.append(line)
            continue
        opened = _OPEN_RE.match(line)
        if skip_depth:
            if opened:
                skip_depth += 1
            elif _CLOSE_RE.match(line):
                skip_depth -= 1
            continue
        if opened and opened.group(2) == "explain":
            skip_depth = 1
            continue
        out.append(_CORRECT_RE.sub(r"\1[ ]", line))
    return "\n".join(out) + ("\n" if markdown.endswith("\n") else "")
