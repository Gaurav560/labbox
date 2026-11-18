import asyncio
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from .. import containers, progress
from ..auth import get_current_user
from ..checker import task_states
from ..db import get_session
from ..labs import LabConfig, all_labs, get_lab
from ..lessons import PublicStep, StepType, public_step, redact_markdown
from ..models import User

router = APIRouter(prefix="/api/labs", tags=["labs"])


class Progress(BaseModel):
    passed_tasks: int
    total_tasks: int


class LabInfo(BaseModel):
    """v2 catalog fields (defaults for v1 labs)."""

    subtitle: str = ""
    track: str = "languages"
    tags: list[str] = []
    level: str | None = None
    estimated_minutes: int | None = None


class LabSummary(LabInfo):
    id: str
    title: str
    description: str
    language: str
    chapter_count: int
    progress: Progress


class TaskOut(BaseModel):
    id: str
    title: str
    passed: bool | None  # None = never checked
    xp: int = 20  # what the task is worth now (hints reduce it)
    hint_count: int = 0
    hints_used: int = 0


class ChapterOut(BaseModel):
    id: str
    title: str
    tasks: list[TaskOut]
    minutes: int | None = None


class LabDetail(LabInfo):
    id: str
    title: str
    description: str
    language: str
    chapters: list[ChapterOut]
    progress: Progress


class ChapterContent(BaseModel):
    id: str
    title: str
    markdown: str  # predict answers redacted
    steps: list[PublicStep]


class OutlineStep(BaseModel):
    type: StepType
    title: str | None = None
    task: str | None = None


class Outline(BaseModel):
    steps: list[OutlineStep]


def _info(lab: LabConfig) -> dict:
    return dict(
        subtitle=lab.subtitle,
        track=lab.track,
        tags=lab.tags,
        level=lab.level,
        estimated_minutes=lab.estimated_minutes,
    )


@router.get("", response_model=list[LabSummary])
def list_labs(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[LabSummary]:
    assert user.id is not None
    out = []
    for lab in all_labs():
        states = task_states(session, user.id, lab)
        out.append(
            LabSummary(
                **_info(lab),
                id=lab.id,
                title=lab.title,
                description=lab.description,
                language=lab.language,
                chapter_count=len(lab.chapters),
                progress=Progress(passed_tasks=sum(states.values()), total_tasks=lab.task_count),
            )
        )
    return out


@router.get("/{lab_id}", response_model=LabDetail)
def lab_detail(lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> LabDetail:
    assert user.id is not None
    lab = get_lab(lab_id)
    states = task_states(session, user.id, lab)
    used = progress.hints_used(session, user.id, lab.id)
    return LabDetail(
        **_info(lab),
        id=lab.id,
        title=lab.title,
        description=lab.description,
        language=lab.language,
        chapters=[
            ChapterOut(
                id=c.id,
                title=c.title,
                minutes=c.minutes,
                tasks=[
                    TaskOut(
                        id=t.id,
                        title=t.title,
                        passed=states.get(t.id),
                        xp=progress.task_xp(t.xp, used.get(t.id, 0)),
                        hint_count=len(t.hints),
                        hints_used=used.get(t.id, 0),
                    )
                    for t in c.tasks
                ],
            )
            for c in lab.chapters
        ],
        progress=Progress(passed_tasks=sum(states.values()), total_tasks=lab.task_count),
    )


@router.get("/{lab_id}/chapters/{chapter_id}", response_model=ChapterContent)
def chapter(lab_id: str, chapter_id: str, user: User = Depends(get_current_user)) -> ChapterContent:
    lab = get_lab(lab_id)
    ch = lab.chapter(chapter_id)
    return ChapterContent(
        id=ch.id,
        title=ch.title,
        markdown=redact_markdown(lab.chapter_markdown(chapter_id)),
        steps=[public_step(s) for s in lab.chapter_steps(chapter_id)],
    )


@router.get("/{lab_id}/chapters/{chapter_id}/outline", response_model=Outline)
def outline(lab_id: str, chapter_id: str, user: User = Depends(get_current_user)) -> Outline:
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)
    return Outline(steps=[OutlineStep(type=s.type, title=s.title, task=s.task) for s in lab.chapter_steps(chapter_id)])


class WorkspaceStatus(BaseModel):
    status: Literal["running", "stopped", "missing"]
    container: str | None = None


@router.post("/{lab_id}/workspace/start", response_model=WorkspaceStatus)
async def workspace_start(
    lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> WorkspaceStatus:
    ws = await asyncio.to_thread(containers.ensure_workspace, session, user, get_lab(lab_id))
    return WorkspaceStatus(status="running", container=ws.container_name)


@router.post("/{lab_id}/workspace/stop", response_model=WorkspaceStatus)
async def workspace_stop(lab_id: str, user: User = Depends(get_current_user)) -> WorkspaceStatus:
    assert user.id is not None
    name = containers.container_name(user.id, get_lab(lab_id).id)
    await asyncio.to_thread(containers.stop_workspace, name)
    return WorkspaceStatus(status="stopped", container=name)


@router.post("/{lab_id}/workspace/reset", response_model=WorkspaceStatus)
async def workspace_reset(
    lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> WorkspaceStatus:
    ws = await asyncio.to_thread(containers.reset_workspace, session, user, get_lab(lab_id))
    return WorkspaceStatus(status="running", container=ws.container_name)


@router.get("/{lab_id}/workspace/status", response_model=WorkspaceStatus)
async def workspace_status(lab_id: str, user: User = Depends(get_current_user)) -> WorkspaceStatus:
    assert user.id is not None
    name = containers.container_name(user.id, get_lab(lab_id).id)
    return WorkspaceStatus(status=await asyncio.to_thread(containers.container_status, name), container=name)


# ---------- public catalog (home page, no login) ----------
# Only what a visitor may see: titles and catalog fields. Never chapters, tests, hints or solutions.

public_router = APIRouter(prefix="/api", tags=["public"])


class CatalogLab(LabInfo):
    id: str
    title: str
    chapter_count: int


@public_router.get("/catalog", response_model=list[CatalogLab])
def catalog() -> list[CatalogLab]:
    return [CatalogLab(**_info(lab), id=lab.id, title=lab.title, chapter_count=len(lab.chapters)) for lab in all_labs()]
