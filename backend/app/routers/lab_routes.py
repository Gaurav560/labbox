import asyncio
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from .. import containers
from ..auth import get_current_user
from ..checker import task_states
from ..db import get_session
from ..labs import all_labs, get_lab
from ..models import User

router = APIRouter(prefix="/api/labs", tags=["labs"])


class Progress(BaseModel):
    passed_tasks: int
    total_tasks: int


class LabSummary(BaseModel):
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


class ChapterOut(BaseModel):
    id: str
    title: str
    tasks: list[TaskOut]


class LabDetail(BaseModel):
    id: str
    title: str
    description: str
    language: str
    chapters: list[ChapterOut]
    progress: Progress


class ChapterContent(BaseModel):
    id: str
    title: str
    markdown: str


@router.get("", response_model=list[LabSummary])
def list_labs(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[LabSummary]:
    assert user.id is not None
    out = []
    for lab in all_labs():
        states = task_states(session, user.id, lab)
        out.append(
            LabSummary(
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
    return LabDetail(
        id=lab.id,
        title=lab.title,
        description=lab.description,
        language=lab.language,
        chapters=[
            ChapterOut(id=c.id, title=c.title, tasks=[TaskOut(id=t.id, title=t.title, passed=states.get(t.id)) for t in c.tasks])
            for c in lab.chapters
        ],
        progress=Progress(passed_tasks=sum(states.values()), total_tasks=lab.task_count),
    )


@router.get("/{lab_id}/chapters/{chapter_id}", response_model=ChapterContent)
def chapter(lab_id: str, chapter_id: str, user: User = Depends(get_current_user)) -> ChapterContent:
    lab = get_lab(lab_id)
    ch = lab.chapter(chapter_id)
    return ChapterContent(id=ch.id, title=ch.title, markdown=lab.chapter_markdown(chapter_id))


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
