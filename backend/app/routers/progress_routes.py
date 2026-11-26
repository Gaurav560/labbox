import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from .. import containers, design, engagement, lab_setup, progress, tutor
from ..slots import lab_open
from ..auth import get_current_user
from ..db import get_session
from ..labs import LabConfig, get_lab
from ..models import User

router = APIRouter(prefix="/api/labs/{lab_id}/chapters/{chapter_id}", tags=["progress"], dependencies=[Depends(lab_open)])


class ChapterProgressOut(BaseModel):
    current_step: int
    step_count: int
    hints: dict[str, list[str]]  # task id -> hints revealed so far
    predicts: dict[int, progress.PredictState] = {}  # step index -> attempts so far
    xp_earned: int = 0  # in this chapter, for the recap card
    designs: dict[int, design.DesignAttempt] = {}  # step index -> last graded design attempt


class PredictBody(BaseModel):
    step: int = Field(ge=0)
    choice: int = Field(ge=0)


class StepBody(BaseModel):
    current_step: int = Field(ge=0, le=1000)


class DesignBody(BaseModel):
    step: int = Field(ge=0)
    answers: dict[str, str] = Field(max_length=5)


class TutorBody(BaseModel):
    question: str = Field(default="", max_length=500)


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
        predicts=progress.predict_states(session, user_id, lab, chapter_id),
        xp_earned=engagement.chapter_xp(session, user_id, lab.id, chapter_id),
        designs=design.latest(session, user_id, lab, chapter_id),
    )


@router.get("/progress", response_model=ChapterProgressOut)
def get_progress(
    lab_id: str, chapter_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> ChapterProgressOut:
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)  # 404 if unknown
    progress.opened(session, user.id, lab.id, chapter_id)
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


@router.post("/predict", response_model=progress.PredictState)
def predict(
    lab_id: str,
    chapter_id: str,
    body: PredictBody,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> progress.PredictState:
    """Check a predict answer. The right answer and explanation come back only once it is right."""
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)
    return progress.answer_predict(session, user.id, lab, chapter_id, body.step, body.choice)


@router.post("/setup", response_model=lab_setup.SetupResult)
async def setup(
    lab_id: str, chapter_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> lab_setup.SetupResult:
    """Called when a chapter opens: starts the machine if needed and runs the chapter's setup once."""
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)
    return await asyncio.to_thread(lab_setup.run_setup, session, user, lab, chapter_id)


@router.post("/tasks/{task_id}/tutor", response_model=tutor.TutorReply)
async def ask_tutor(
    lab_id: str, chapter_id: str, task_id: str, body: TutorBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> tutor.TutorReply:
    """A Socratic nudge for a task (counts against the learner's daily AI budget)."""
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.task(chapter_id, task_id)  # 404 if unknown
    ws = containers.get_workspace(session, user, lab)
    return await tutor.ask(session, user.id, lab, chapter_id, task_id, body.question, ws)


@router.post("/tasks/{task_id}/review", response_model=tutor.TutorReply)
async def review_code(
    lab_id: str, chapter_id: str, task_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> tutor.TutorReply:
    """A short code review once the task passes. No XP either way."""
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.task(chapter_id, task_id)
    ws = containers.get_workspace(session, user, lab)
    return await tutor.review(session, user.id, lab, chapter_id, task_id, ws)


@router.post("/design", response_model=design.DesignResult)
async def grade_design(
    lab_id: str, chapter_id: str, body: DesignBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> design.DesignResult:
    """Grade a design step's written answers against the lab's rubric (uses the daily AI budget)."""
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)
    return await design.grade(session, user.id, lab, chapter_id, body.step, body.answers)
