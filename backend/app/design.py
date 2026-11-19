"""Design steps (v2 spec 7.1): short written answers in system design labs, graded by the tutor model
against a rubric that stays on the server (`tests/rubric.yaml`). A grade gives XP and feedback but
never blocks finishing a chapter.

rubric.yaml:

    <chapter id>:
      <question id>:
        - id: fails_open_or_closed
          points: 2
          look_for: Says whether requests are allowed or blocked when Redis is down, and why.

One model call per question, asking for JSON. The reply is checked and clamped to the rubric (a model
cannot give more points than a criterion has); a reply that is not usable is retried once, then the
learner sees "could not grade right now" instead of a made-up score.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path

import yaml
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlmodel import Session, col, select

from . import engagement, llm_gateway
from .labs import LabConfig, LabError
from .models import DesignAnswer

log = logging.getLogger(__name__)

GRADER_ALIAS = "lab-chat-smart"
MIN_ANSWER_CHARS = 20  # shorter than this is not an answer yet: scored 0 without asking the model
MAX_ANSWER_CHARS = 2_000
XP_DESIGN = 30  # once per design step, the first time an attempt reaches half the points

GRADER_RULES = """You grade one short written answer from a learner in a hands-on system design lab.
Use only the rubric. Give partial credit for correct ideas said in plain words; do not require jargon.
Give 0 for a criterion the answer does not address. Feedback: one short sentence per criterion,
written to the learner as "you", saying what was good or what is missing. Never invent criteria.
Reply with JSON only, exactly this shape:
{"criteria": [{"id": "<criterion id>", "score": <integer from 0 to its points>, "feedback": "<one sentence>"}]}
"""


class Criterion(BaseModel):
    id: str
    points: int = Field(ge=1, le=10)
    look_for: str


class CriterionResult(BaseModel):
    id: str
    score: int
    max: int
    feedback: str


class QuestionResult(BaseModel):
    id: str
    score: int
    max: int
    criteria: list[CriterionResult]


class DesignResult(BaseModel):
    score: int
    max: int
    questions: list[QuestionResult]
    xp_awarded: list[engagement.XpAward] = []
    created_at: str = ""


def rubric_path(lab: LabConfig) -> Path:
    return lab.tests_dir / "rubric.yaml"


@lru_cache(maxsize=64)
def _load(path: str, mtime: float) -> dict[str, dict[str, list[Criterion]]]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    try:
        return {ch: {q: [Criterion(**c) for c in crits] for q, crits in qs.items()} for ch, qs in raw.items()}
    except (ValidationError, AttributeError, TypeError) as e:
        raise LabError(f"{path}: invalid rubric: {e}") from e


def rubric(lab: LabConfig) -> dict[str, dict[str, list[Criterion]]]:
    p = rubric_path(lab)
    return _load(str(p), p.stat().st_mtime) if p.is_file() else {}


def check_rubric(lab: LabConfig) -> list[str]:
    """Problems for `labbox validate`: every design question needs criteria, and nothing extra."""
    errors: list[str] = []
    try:
        r = rubric(lab)
    except LabError as e:
        return [str(e)]
    for ch in lab.chapters:
        for step in lab.chapter_steps(ch.id):
            for q in step.questions:
                if not r.get(ch.id, {}).get(q.id):
                    errors.append(f"chapter {ch.id}: design question {q.id!r} has no criteria in tests/rubric.yaml")
    return errors


def _parse(reply: str, criteria: list[Criterion]) -> list[CriterionResult] | None:
    """The model's JSON, matched to the rubric and clamped. None when it is not usable."""
    text = reply.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    try:
        data = json.loads(text[text.find("{"): text.rfind("}") + 1])
        given = {str(c["id"]): c for c in data["criteria"] if isinstance(c, dict) and "id" in c}
    except (ValueError, KeyError, TypeError):
        return None
    if not any(c.id in given for c in criteria):
        return None
    out = []
    for c in criteria:
        g = given.get(c.id, {})
        try:
            score = int(round(float(g.get("score", 0))))
        except (TypeError, ValueError):
            score = 0
        out.append(CriterionResult(id=c.id, score=max(0, min(c.points, score)), max=c.points,
                                   feedback=str(g.get("feedback", "")).strip()[:300]))
    return out


async def _grade_one(user_id: int, lab: LabConfig, question: str, answer: str, criteria: list[Criterion]) -> list[CriterionResult]:
    if len(answer.strip()) < MIN_ANSWER_CHARS:
        return [CriterionResult(id=c.id, score=0, max=c.points, feedback="Write a few sentences so this can be graded.") for c in criteria]
    rubric_text = "\n".join(f"- {c.id} ({c.points} points): {c.look_for}" for c in criteria)
    body = {
        "model": GRADER_ALIAS,
        "messages": [
            {"role": "system", "content": GRADER_RULES},
            {"role": "user", "content": f"Question:\n{question}\n\nRubric:\n{rubric_text}\n\nLearner's answer:\n{answer.strip()}"},
        ],
        "max_tokens": 400,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    ident = llm_gateway.Identity(user_id, lab.id)
    for _ in range(2):  # one retry when the reply is not usable JSON
        try:
            out = await llm_gateway.chat(ident, dict(body), endpoint="design")
        except llm_gateway.GatewayError as e:
            raise HTTPException(e.status if e.status in (429, 503) else 502, e.message)
        reply = ((out.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        parsed = _parse(reply, criteria)
        if parsed is not None:
            return parsed
        log.info("Design grader gave an unusable reply for lab %s, retrying", lab.id)
    raise HTTPException(503, "Could not grade your answers right now. Your answers are not lost: try again in a minute.")


async def grade(session: Session, user_id: int, lab: LabConfig, chapter_id: str, step_index: int, answers: dict[str, str]) -> DesignResult:
    steps = lab.chapter_steps(chapter_id)
    if not 0 <= step_index < len(steps) or steps[step_index].type != "design":
        raise HTTPException(404, "No design step there")
    step = steps[step_index]
    crits = rubric(lab).get(chapter_id, {})
    results = []
    for q in step.questions:
        cr = await _grade_one(user_id, lab, q.text, (answers.get(q.id) or "")[:MAX_ANSWER_CHARS], crits.get(q.id, []))
        results.append(QuestionResult(id=q.id, score=sum(c.score for c in cr), max=sum(c.max for c in cr), criteria=cr))
    score, max_score = sum(q.score for q in results), sum(q.max for q in results)
    row = DesignAnswer(user_id=user_id, lab_id=lab.id, chapter_id=chapter_id, step_index=step_index,
                       answers_json=json.dumps({q.id: (answers.get(q.id) or "")[:MAX_ANSWER_CHARS] for q in step.questions}),
                       result_json=json.dumps([q.model_dump() for q in results]), score=score, max_score=max_score)
    session.add(row)
    session.commit()
    session.refresh(row)
    xp: list[engagement.XpAward] = []
    if max_score and score * 2 >= max_score:
        a = engagement.award(session, user_id, "design", XP_DESIGN, f"design:{lab.id}:{chapter_id}:{step_index}",
                             lab_id=lab.id, chapter_id=chapter_id, label="Design review")
        xp = [a] if a else []
    return DesignResult(score=score, max=max_score, questions=results, xp_awarded=xp, created_at=row.created_at.isoformat() + "Z")


class DesignAttempt(BaseModel):
    answers: dict[str, str]
    result: DesignResult


def latest(session: Session, user_id: int, lab: LabConfig, chapter_id: str) -> dict[int, DesignAttempt]:
    """step index -> the last graded attempt, so the page can show it again."""
    rows = session.exec(
        select(DesignAnswer).where(DesignAnswer.user_id == user_id, DesignAnswer.lab_id == lab.id, DesignAnswer.chapter_id == chapter_id)
        .order_by(col(DesignAnswer.id))
    ).all()
    out: dict[int, DesignAttempt] = {}
    for r in rows:
        out[r.step_index] = DesignAttempt(
            answers=json.loads(r.answers_json),
            result=DesignResult(score=r.score, max=r.max_score, questions=[QuestionResult(**q) for q in json.loads(r.result_json)],
                                created_at=r.created_at.isoformat() + "Z"),
        )
    return out
