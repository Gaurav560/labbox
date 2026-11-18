"""Per-user lesson progress: current step per chapter, hints revealed and first pass per task."""
from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, col, select

from .labs import LabConfig
from .lessons import Step
from .models import ChapterProgress, PredictAnswer, TaskProgress, utcnow

# XP share kept after 0, 1, 2 and 3 revealed hints (section 2.4 of the v2 spec).
HINT_XP_FACTORS = (1.0, 0.8, 0.6, 0.4)

M = TypeVar("M", bound=SQLModel)


def task_xp(base_xp: int, hints_used: int) -> int:
    return round(base_xp * HINT_XP_FACTORS[min(hints_used, len(HINT_XP_FACTORS) - 1)])


def _get_or_create(session: Session, model: type[M], key: dict, make: Callable[[], M]) -> M:
    row = session.get(model, key)
    if row is not None:
        return row
    row = make()
    session.add(row)
    try:
        session.commit()
    except IntegrityError:
        # Another request created it at the same moment.
        session.rollback()
        found = session.get(model, key)
        assert found is not None
        return found
    session.refresh(row)
    return row


def chapter_progress(session: Session, user_id: int, lab_id: str, chapter_id: str) -> ChapterProgress:
    key = {"user_id": user_id, "lab_id": lab_id, "chapter_id": chapter_id}
    return _get_or_create(session, ChapterProgress, key, lambda: ChapterProgress(**key))


def task_progress(session: Session, user_id: int, lab_id: str, chapter_id: str, task_id: str) -> TaskProgress:
    key = {"user_id": user_id, "lab_id": lab_id, "task_id": task_id}
    return _get_or_create(session, TaskProgress, key, lambda: TaskProgress(**key, chapter_id=chapter_id))


def set_step(session: Session, user_id: int, lab: LabConfig, chapter_id: str, step: int) -> ChapterProgress:
    row = chapter_progress(session, user_id, lab.id, chapter_id)
    row.current_step = max(0, min(step, len(lab.chapter_steps(chapter_id)) - 1))
    row.updated_at = utcnow()
    session.add(row)
    session.commit()
    return row


def hints_used(session: Session, user_id: int, lab_id: str) -> dict[str, int]:
    rows = session.exec(select(TaskProgress).where(TaskProgress.user_id == user_id, TaskProgress.lab_id == lab_id)).all()
    return {r.task_id: r.hints_used for r in rows}


def reveal_hint(session: Session, user_id: int, lab: LabConfig, chapter_id: str, task_id: str) -> TaskProgress:
    """Reveal the next hint (no-op once all are shown)."""
    task = lab.task(chapter_id, task_id)
    row = task_progress(session, user_id, lab.id, chapter_id, task_id)
    if row.hints_used < len(task.hints):
        row.hints_used += 1
        session.add(row)
        session.commit()
    return row


def record_check(session: Session, user_id: int, lab_id: str, chapter_id: str, passed: dict[str, bool]) -> None:
    """Remember the latest pass state per task and when each first passed."""
    for task_id, ok in passed.items():
        row = task_progress(session, user_id, lab_id, chapter_id, task_id)
        row.passed = ok
        if ok and row.first_passed_at is None:
            row.first_passed_at = utcnow()
        session.add(row)
    session.commit()


# ---------- predict steps (answers are checked here, never in the browser) ----------


class PredictState(BaseModel):
    wrong: list[int] = []  # wrong choices, in the order they were picked
    solved: bool = False
    answer: int | None = None  # only once solved
    explain: str | None = None  # only once solved


def predict_step(lab: LabConfig, chapter_id: str, step_index: int) -> Step:
    steps = lab.chapter_steps(chapter_id)
    if not 0 <= step_index < len(steps) or steps[step_index].predict is None:
        raise HTTPException(404, f"Step {step_index} is not a predict step")
    return steps[step_index]


def answer_predict(session: Session, user_id: int, lab: LabConfig, chapter_id: str, step_index: int, choice: int) -> PredictState:
    step = predict_step(lab, chapter_id, step_index)
    assert step.predict is not None
    if not 0 <= choice < len(step.predict.options):
        raise HTTPException(422, f"Choice must be between 0 and {len(step.predict.options) - 1}")
    session.add(
        PredictAnswer(
            user_id=user_id,
            lab_id=lab.id,
            chapter_id=chapter_id,
            step_index=step_index,
            choice=choice,
            correct=choice == step.predict.answer,
        )
    )
    session.commit()
    return predict_states(session, user_id, lab, chapter_id)[step_index]


def predict_states(session: Session, user_id: int, lab: LabConfig, chapter_id: str) -> dict[int, PredictState]:
    """Every predict step the user has tried in this chapter, keyed by step index."""
    rows = session.exec(
        select(PredictAnswer)
        .where(PredictAnswer.user_id == user_id, PredictAnswer.lab_id == lab.id, PredictAnswer.chapter_id == chapter_id)
        .order_by(col(PredictAnswer.id))
    ).all()
    steps = lab.chapter_steps(chapter_id)
    states: dict[int, PredictState] = {}
    for r in rows:
        if not (0 <= r.step_index < len(steps) and steps[r.step_index].predict):
            continue  # the chapter changed since this answer
        st = states.setdefault(r.step_index, PredictState())
        if st.solved:
            continue
        if r.correct:
            pr = steps[r.step_index].predict
            assert pr is not None
            st.solved, st.answer, st.explain = True, pr.answer, pr.explain
        elif r.choice not in st.wrong:
            st.wrong.append(r.choice)
    return states
