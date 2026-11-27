from functools import lru_cache
import asyncio
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session

import json
import time
from pathlib import Path

from .. import containers, ide, limits, progress, services, slots
from ..focus import chapter_focus, step_file, task_focus
from ..auth import get_current_user
from ..checker import task_states
from ..db import get_session
from ..labs import COVER_TYPES, LabConfig, PreviewPort, all_labs, get_lab
from ..slots import lab_open
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
    access: slots.Access = "open"  # locked: only the course page opens (app/slots.py)


class TaskOut(BaseModel):
    id: str
    title: str
    passed: bool | None  # None = never checked
    xp: int = 20  # what the task is worth now (hints reduce it)
    hint_count: int = 0
    hints_used: int = 0
    examples: list[dict[str, str | None]] = []  # the task card: call, gives, note


@lru_cache(maxsize=1024)
def _topics(path: str, mtime: float) -> tuple[tuple[str, int], ...]:
    from ..lessons import parse_steps

    with open(path, encoding="utf-8") as f:
        steps = parse_steps(f.read())
    return tuple((s.title, i) for i, s in enumerate(steps) if s.type in ("concept", "deep-dive") and s.title)


class TopicOut(BaseModel):
    title: str
    step: int  # the lesson step (0-based) it opens: /labs/<lab>?chapter=<id>&step=<step>


def chapter_topics(lab, chapter_id: str) -> list[TopicOut]:
    """The subtopics of a chapter: its concept steps (cached until the file changes)."""
    try:
        path = lab.root / lab.chapter(chapter_id).file
        return [TopicOut(title=t, step=i) for t, i in _topics(str(path), path.stat().st_mtime)]
    except Exception:  # a broken lesson must not break the lab page; validate reports it
        return []


class ChapterOut(BaseModel):
    id: str
    title: str
    tasks: list[TaskOut]
    minutes: int | None = None
    part: str | None = None  # the course part; null means "same part as the chapter before"
    topics: list[TopicOut] = []  # the lesson's concept steps (the skill map lists them under the chapter)
    has_setup: bool = False  # the lab page calls .../setup when the chapter opens
    folder: str | None = None  # the chapter's own top-level folder; the Files panel hides those of later chapters


class LabDetail(LabInfo):
    before_you_start: dict | None = None  # {summary, needs: [{know, why, lab, lab_title, where}]}
    preview: list[PreviewPort] = []
    services: list[str] = []
    check_mode: str = "fresh"
    id: str
    title: str
    description: str
    language: str
    chapters: list[ChapterOut]
    progress: Progress
    access: slots.Access = "open"  # locked: only the course page opens (app/slots.py)


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
    access = slots.state(session, user).labs
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
                access=access.get(lab.id, "open"),
            )
        )
    return out


def _before_you_start(lab: LabConfig) -> dict | None:
    """The lab's "Before you start" box, with each needed lab's title for the link."""
    if lab.before_you_start is None:
        return None
    titles = {other.id: other.title for other in all_labs()}
    out = lab.before_you_start.model_dump()
    for need in out["needs"]:
        need["lab_title"] = titles.get(need["lab"]) if need["lab"] else None
    return out


@router.get("/{lab_id}", response_model=LabDetail)
def lab_detail(lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> LabDetail:
    assert user.id is not None
    lab = get_lab(lab_id)
    states = task_states(session, user.id, lab)
    used = progress.hints_used(session, user.id, lab.id)
    return LabDetail(
        **_info(lab),
        before_you_start=_before_you_start(lab),
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
                part=c.part,
                topics=chapter_topics(lab, c.id),
                has_setup=bool(c.setup),
                folder=lab.chapter_folder(c),
                tasks=[
                    TaskOut(
                        id=t.id,
                        title=t.title,
                        passed=states.get(t.id),
                        xp=progress.task_xp(t.xp, used.get(t.id, 0)),
                        hint_count=len(t.hints),
                        hints_used=used.get(t.id, 0),
                        examples=[e.model_dump() for e in t.examples],
                    )
                    for t in c.tasks
                ],
            )
            for c in lab.chapters
        ],
        progress=Progress(passed_tasks=sum(states.values()), total_tasks=lab.task_count),
        access=slots.access(session, user, lab),
    )


@router.get("/{lab_id}/chapters/{chapter_id}", response_model=ChapterContent, dependencies=[Depends(lab_open)])
def chapter(lab_id: str, chapter_id: str, user: User = Depends(get_current_user)) -> ChapterContent:
    lab = get_lab(lab_id)
    ch = lab.chapter(chapter_id)
    return ChapterContent(
        id=ch.id,
        title=ch.title,
        markdown=redact_markdown(lab.chapter_markdown(chapter_id)),
        steps=[public_step(s) for s in lab.chapter_steps(chapter_id)],
    )


@router.get("/{lab_id}/chapters/{chapter_id}/outline", response_model=Outline, dependencies=[Depends(lab_open)])
def outline(lab_id: str, chapter_id: str, user: User = Depends(get_current_user)) -> Outline:
    lab = get_lab(lab_id)
    lab.chapter(chapter_id)
    return Outline(steps=[OutlineStep(type=s.type, title=s.title, task=s.task) for s in lab.chapter_steps(chapter_id)])


class FocusIn(BaseModel):
    ide: bool = False  # also open it in the learner's running VS Code
    step: int | None = None  # 0-based: open what this step talks about instead of the chapter's file


class FocusOut(BaseModel):
    path: str | None = None
    line: int = 1
    end_line: int | None = None  # with a step's line range: the lines to highlight


@router.post("/{lab_id}/chapters/{chapter_id}/focus", response_model=FocusOut, dependencies=[Depends(lab_open)])
async def chapter_focus_route(
    lab_id: str, chapter_id: str, body: FocusIn | None = None,
    user: User = Depends(get_current_user), session: Session = Depends(get_session),
) -> FocusOut:
    """The file and line this chapter (or one of its steps) is about. With ide=true, VS Code opens it
    too (the labbox-defaults extension watches /tmp/labbox-open.json in the machine). A step names
    its file in the lesson (file=, line=); a task step opens its own task's TODO. Only paths from the
    lab's own content are ever opened, never a path sent by the browser."""
    lab = get_lab(lab_id)
    ch = lab.chapter(chapter_id)
    ws = containers.get_workspace(session, user, lab, chapter_id)  # opening a chapter brings its folder in (plan A)
    await asyncio.to_thread(ide.show_chapter, lab, ws, lab.chapter_index(chapter_id))  # VS Code hides later chapters
    folder = Path(ws.volume_path)
    end: int | None = None
    if body and body.step is not None:
        steps = lab.chapter_steps(ch.id)
        if not 0 <= body.step < len(steps):
            raise HTTPException(404, f"Step {body.step} not found in chapter {chapter_id!r}")
        st = steps[body.step]
        hit = None
        if st.file and await asyncio.to_thread(step_file, lab, st.file, folder):
            # A step that names a line highlights it (a range: all of it); the chapter focus only moves there.
            hit, end = (st.file, st.line or 1), (st.end_line or st.line)
        elif st.task and not st.file:
            hit = await asyncio.to_thread(task_focus, lab, ch, st.task, folder)
    else:
        hit = await asyncio.to_thread(chapter_focus, lab, ch, folder)
    if not hit:
        return FocusOut()
    path, line = hit
    if body and body.ide and ide.available():
        await asyncio.to_thread(_tell_ide, ws.container_name, path, line, end)
    return FocusOut(path=path, line=line, end_line=end)


class StepCodeOut(BaseModel):
    path: str | None = None
    first_line: int = 1          # the number of the first line in `lines`
    lines: list[str] = []
    highlight: list[int] = []    # the step's own line or range (first and last), to mark in Read mode


STEP_CODE_MAX = 40  # lines shown for one step in Read mode


@router.get("/{lab_id}/chapters/{chapter_id}/steps/{step}/code", response_model=StepCodeOut, dependencies=[Depends(lab_open)])
async def step_code_route(
    lab_id: str, chapter_id: str, step: int,
    user: User = Depends(get_current_user), session: Session = Depends(get_session),
) -> StepCodeOut:
    """The lines a step talks about (file= and line= in the lesson, or a task's TODO), read from the learner's own
    files without a running machine: Read mode shows them under the step. Only paths from the lab's content."""
    lab = get_lab(lab_id)
    ch = lab.chapter(chapter_id)
    steps = lab.chapter_steps(ch.id)
    if not 0 <= step < len(steps):
        raise HTTPException(404, f"Step {step} not found in chapter {chapter_id!r}")
    st = steps[step]
    folder = Path(containers.get_workspace(session, user, lab, chapter_id).volume_path)
    if st.file and await asyncio.to_thread(step_file, lab, st.file, folder):
        path, start, end = st.file, st.line or 1, st.end_line or st.line or 1
    elif st.task and not st.file:
        hit = await asyncio.to_thread(task_focus, lab, ch, st.task, folder)
        if not hit:
            return StepCodeOut()
        path, start, end = hit[0], hit[1], hit[1]
    else:
        return StepCodeOut()
    text = await asyncio.to_thread(_read_lines, lab, folder, path)
    if text is None:
        return StepCodeOut()
    # Show the step's lines with a little room around them; a single line (a task's TODO) gets what follows it.
    lo = max(1, start - 2)
    hi = min(len(text), max(end + 2, start + 12), lo + STEP_CODE_MAX - 1)
    return StepCodeOut(path=path, first_line=lo, lines=text[lo - 1:hi], highlight=[start, end])


def _read_lines(lab: LabConfig, folder: Path, path: str) -> list[str] | None:
    """The file from the learner's folder, else from the starter; never outside them."""
    for root in (folder, lab.starter_dir):
        p = (root / path).resolve()
        if p.is_relative_to(root.resolve()) and p.is_file():
            try:
                return p.read_text(errors="replace").splitlines()
            except OSError:
                return None
    return None


def _tell_ide(container: str, path: str, line: int, end_line: int | None = None) -> None:
    request = json.dumps({"path": path, "line": line, "end": end_line, "at": time.time()})
    try:
        containers.client().containers.get(container).exec_run(
            ["sh", "-c", 'printf "%s" "$LB_OPEN" > /tmp/labbox-open.json'],
            user=containers.LEARNER_USER, environment={"LB_OPEN": request},
        )
    except Exception:  # the machine is stopped or gone: the Lite editor still gets the answer
        pass


class ServiceStatus(BaseModel):
    name: str
    status: Literal["running", "starting", "stopped", "missing"]


class WorkspaceStatus(BaseModel):
    status: Literal["running", "stopped", "missing"]
    container: str | None = None
    services: list[ServiceStatus] | None = None  # only for labs with services
    stopped_reason: str | None = None  # a safety limit stopped it (Phase H5): the lab page says why


@router.post("/{lab_id}/workspace/start", response_model=WorkspaceStatus, response_model_exclude_none=True, dependencies=[Depends(lab_open)])
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


@router.post("/{lab_id}/workspace/reset", response_model=WorkspaceStatus, response_model_exclude_none=True, dependencies=[Depends(lab_open)])
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
    reason = await asyncio.to_thread(limits.stop_reason, name) if status != "running" else None
    return WorkspaceStatus(status=status, container=name, services=svc, stopped_reason=reason)


# ---------- public catalog (home page, no login) ----------
# Only what a visitor may see: titles and catalog fields. Never chapters, tests, hints or solutions.

public_router = APIRouter(prefix="/api", tags=["public"])


class CatalogLab(LabInfo):
    id: str
    title: str
    chapter_count: int
    # The course's part names, in order (its syllabus at a glance, for the home page's course details; owner,
    # 27 November: "show the description, do not send them to sign up directly"). Names only, never chapters.
    parts: list[str] = []


def _parts(lab) -> list[str]:
    seen: list[str] = []
    for c in lab.chapters:
        if c.part and c.part not in seen:
            seen.append(c.part)
    return seen


@public_router.get("/catalog", response_model=list[CatalogLab])
def catalog() -> list[CatalogLab]:
    return [CatalogLab(**_info(lab), id=lab.id, title=lab.title, chapter_count=len(lab.chapters), parts=_parts(lab))
            for lab in all_labs()]


# The AI courses' intro pages are public (owner, 27 November: the home page's AI rows open "the actual intro page
# where the skill map is", for visitors too; "only the AI courses"). Titles only, as a locked lab's course page shows
# them: parts, chapters, subtopics and task titles. Never lessons, hints, task cards, tests or solutions.
PUBLIC_COURSE_TRACKS = {"ai"}


@public_router.get("/courses/{lab_id}", response_model=LabDetail)
def public_course(lab_id: str) -> LabDetail:
    lab = get_lab(lab_id)
    if lab.track not in PUBLIC_COURSE_TRACKS:
        raise HTTPException(404, "Log in to see this course")
    return LabDetail(
        **_info(lab),
        before_you_start=_before_you_start(lab),
        id=lab.id,
        title=lab.title,
        description=lab.description,
        language=lab.language,
        chapters=[
            ChapterOut(
                id=c.id,
                title=c.title,
                minutes=c.minutes,
                part=c.part,
                topics=chapter_topics(lab, c.id),
                tasks=[TaskOut(id=t.id, title=t.title, passed=None, xp=t.xp) for t in c.tasks],
            )
            for c in lab.chapters
        ],
        progress=Progress(passed_tasks=0, total_tasks=lab.task_count),
        access="locked",
    )


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
