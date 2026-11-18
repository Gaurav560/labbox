"""Chapter setup (v2 spec 4.4): a script baked into the image runs once per learner per chapter,
as root, the first time the chapter is opened on a running machine. Seed data, injected failures."""
import logging

from docker.errors import APIError
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from . import containers, progress, services
from .labs import Chapter, LabConfig
from .models import User, Workspace, utcnow

log = logging.getLogger(__name__)

OUTPUT_TAIL_CHARS = 2000


class SetupResult(BaseModel):
    ran: bool  # this call ran the script
    setup_done: bool
    started_at: str | None  # ISO, UTC; incident countdowns start here


def exec_setup(lab: LabConfig, ws: Workspace, chapter: Chapter) -> None:
    """Run the chapter's setup command as root in its target container. Raises HTTPException on failure."""
    assert chapter.setup
    name = ws.container_name
    if chapter.setup_target != "workspace":
        svc = next(s for s in lab.services if s.name == chapter.setup_target)
        name = services.service_container_name(ws, svc)
    try:
        result = containers.client().containers.get(name).exec_run(chapter.setup, user="0")
    except APIError as e:
        raise HTTPException(500, f"Could not run the chapter setup: {e.explanation or e}")
    if result.exit_code != 0:
        output = result.output.decode("utf-8", errors="replace")[-OUTPUT_TAIL_CHARS:]
        log.warning("Setup failed in %s for chapter %s:\n%s", name, chapter.id, output)
        raise HTTPException(500, f"The chapter setup failed (exit {result.exit_code}). Try Reset lab.\n{output}")


def run_setup(session: Session, user: User, lab: LabConfig, chapter_id: str) -> SetupResult:
    assert user.id is not None
    chapter = lab.chapter(chapter_id)
    ws = containers.ensure_workspace(session, user, lab)  # machine and services up and ready
    cp = progress.chapter_progress(session, user.id, lab.id, chapter_id)
    ran = False
    with containers._locks[f"{ws.container_name}:setup"]:
        session.refresh(cp)
        if chapter.setup and not cp.setup_done:
            exec_setup(lab, ws, chapter)
            cp.setup_done = True
            ran = True
            log.info("Setup done user=%s lab=%s chapter=%s", user.id, lab.id, chapter_id)
        if cp.started_at is None:
            cp.started_at = utcnow()
        session.add(cp)
        session.commit()
    return SetupResult(ran=ran, setup_done=cp.setup_done or not chapter.setup, started_at=cp.started_at.isoformat() + "Z")
