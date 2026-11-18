import asyncio
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session

from .. import containers, progress, services
from ..auth import get_current_user
from ..checker import task_states
from ..db import get_session
from ..labs import COVER_TYPES, LabConfig, PreviewPort, all_labs, get_lab
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
    cover_url: str | None = None  # set when the lab ships its own cover; otherwise the UI draws one
    cover_credit: dict | None = None  # {by, url, source} for a stock photo


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
    has_setup: bool = False  # the lab page calls .../setup when the chapter opens


class LabDetail(LabInfo):
    preview: list[PreviewPort] = []
    services: list[str] = []
    check_mode: str = "fresh"
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


def _cover_url(lab: LabConfig) -> str | None:
    """The cover route plus a version from the file, so a new cover is never hidden by the browser cache."""
    if not lab.cover:
        return None
    st = (lab.root / lab.cover).stat()
    return f"/api/labs/{lab.id}/cover?v={st.st_mtime_ns:x}{st.st_size:x}"


def _info(lab: LabConfig) -> dict:
    return dict(
        subtitle=lab.subtitle,
        track=lab.track,
        tags=lab.tags,
        level=lab.level,
        estimated_minutes=lab.estimated_minutes,
        cover_url=_cover_url(lab),
        cover_credit=lab.cover_credit.model_dump() if lab.cover_credit else None,
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
        preview=lab.preview,
        services=[s.name for s in lab.services],
        check_mode=lab.check.mode,
        id=lab.id,
        title=lab.title,
        description=lab.description,
        language=lab.language,
        chapters=[
            ChapterOut(
                id=c.id,
                title=c.title,
                minutes=c.minutes,
                has_setup=bool(c.setup),
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


class ServiceStatus(BaseModel):
    name: str
    status: Literal["running", "starting", "stopped", "missing"]


class WorkspaceStatus(BaseModel):
    status: Literal["running", "stopped", "missing"]
    container: str | None = None
    services: list[ServiceStatus] | None = None  # only for labs with services


@router.post("/{lab_id}/workspace/start", response_model=WorkspaceStatus, response_model_exclude_none=True)
async def workspace_start(
    lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> WorkspaceStatus:
    ws = await asyncio.to_thread(containers.ensure_workspace, session, user, get_lab(lab_id))
    return WorkspaceStatus(status="running", container=ws.container_name)


@router.post("/{lab_id}/workspace/stop", response_model=WorkspaceStatus, response_model_exclude_none=True)
async def workspace_stop(
    lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> WorkspaceStatus:
    name = await asyncio.to_thread(containers.stop_group, session, user, get_lab(lab_id))
    return WorkspaceStatus(status="stopped", container=name)


@router.post("/{lab_id}/workspace/reset", response_model=WorkspaceStatus, response_model_exclude_none=True)
async def workspace_reset(
    lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> WorkspaceStatus:
    ws = await asyncio.to_thread(containers.reset_workspace, session, user, get_lab(lab_id))
    return WorkspaceStatus(status="running", container=ws.container_name)


@router.get("/{lab_id}/workspace/status", response_model=WorkspaceStatus, response_model_exclude_none=True)
async def workspace_status(
    lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> WorkspaceStatus:
    assert user.id is not None
    lab = get_lab(lab_id)
    name = containers.container_name(user.id, lab.id)
    status = await asyncio.to_thread(containers.container_status, name)
    svc: list[ServiceStatus] | None = None
    if lab.services:
        ws = containers.get_workspace(session, user, lab)
        svc = [ServiceStatus(**s) for s in await asyncio.to_thread(services.service_states, lab, ws)]
    return WorkspaceStatus(status=status, container=name, services=svc)


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


@public_router.get("/labs/{lab_id}/cover", include_in_schema=False)
def cover(lab_id: str) -> FileResponse:
    """A lab's own cover image (public: it is shown on the home page and in the catalog)."""
    lab = get_lab(lab_id)
    if not lab.cover:
        raise HTTPException(404, "This lab has no cover image")
    path = lab.root / lab.cover
    return FileResponse(
        path,
        media_type=COVER_TYPES[path.suffix.lower()],
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
            # An SVG opened directly must not run scripts on our origin.
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox",
        },
    )
