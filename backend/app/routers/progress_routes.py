from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from .. import progress
from ..auth import get_current_user
from ..db import get_session
from ..labs import LabConfig, get_lab
from ..models import User

router = APIRouter(prefix="/api/labs/{lab_id}/chapters/{chapter_id}", tags=["progress"])


class ChapterProgressOut(BaseModel):
    current_step: int
    step_count: int
    hints: dict[str, list[str]]  # task id -> hints revealed so far


class StepBody(BaseModel):
    current_step: int = Field(ge=0, le=1000)


class HintOut(BaseModel):
    task: str
    hints: list[str]  # revealed so far, oldest first
    hints_left: int
    xp: int  # what the task is worth now


def _out(session: Session, user_id: int, lab: LabConfig, chapter_id: str) -> ChapterProgressOut:
    row = progress.chapter_progress(session, user_id, lab.id, chapter_id)
    used = progress.hints_used(session, user_id, lab.id)
    tasks = lab.chapter(chapter_id).tasks
    return ChapterProgressOut(
        current_step=row.current_step,
        step_count=len(lab.chapter_steps(chapter_id)),
        hints={t.id: t.hints[: used.get(t.id, 0)] for t in tasks if used.get(t.id, 0)},
    )


@router.get("/progress", response_model=ChapterProgressOut)
def get_progress(
    lab_id: str, chapter_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> ChapterProgressOut:
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)  # 404 if unknown
    return _out(session, user.id, lab, chapter_id)


@router.put("/progress", response_model=ChapterProgressOut)
def put_progress(
    lab_id: str,
    chapter_id: str,
    body: StepBody,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChapterProgressOut:
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)
    progress.set_step(session, user.id, lab, chapter_id, body.current_step)
    return _out(session, user.id, lab, chapter_id)


@router.post("/tasks/{task_id}/hint", response_model=HintOut)
def hint(
    lab_id: str, chapter_id: str, task_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> HintOut:
    assert user.id is not None
    lab = get_lab(lab_id)
    task = lab.task(chapter_id, task_id)
    row = progress.reveal_hint(session, user.id, lab, chapter_id, task_id)
    return HintOut(
        task=task.id,
        hints=task.hints[: row.hints_used],
        hints_left=len(task.hints) - row.hints_used,
        xp=progress.task_xp(task.xp, row.hints_used),
    )
