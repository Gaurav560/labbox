"""Per-user lesson progress: current step per chapter, hints revealed and first pass per task."""
from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from .labs import LabConfig
from .models import ChapterProgress, TaskProgress, utcnow

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
