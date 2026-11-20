"""The admin area (Phase J): funnel, labs, learners, machines, AI spend, recent errors.
Every route needs an account with is_admin (`scripts/labbox admin grant <name>`); others get 403.
Actions on machines are logged with the admin's name."""
import asyncio
import logging
from datetime import datetime
from typing import Literal

from docker.errors import NotFound
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, col, select

from .. import analytics, containers, limits, observability, services, shared
from ..auth import get_current_user
from ..db import get_session
from ..labs import get_lab
from ..models import User, Workspace

log = logging.getLogger("labbox.admin")


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "Only admins can open this")
    return user


router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])

Window = Literal["7d", "30d", "90d", "all"]


@router.get("/funnel", response_model=list[analytics.FunnelStep])
def funnel(window: Window = "30d", session: Session = Depends(get_session)) -> list[analytics.FunnelStep]:
    return analytics.funnel(session, window)


@router.get("/labs", response_model=list[analytics.LabSummaryRow])
def labs(session: Session = Depends(get_session)) -> list[analytics.LabSummaryRow]:
    return analytics.labs_summary(session)


@router.get("/labs/{lab_id}", response_model=analytics.LabReport)
def lab(lab_id: str, session: Session = Depends(get_session)) -> analytics.LabReport:
    return analytics.lab_report(session, get_lab(lab_id))


@router.get("/learners", response_model=list[analytics.LearnerRow])
def learners(q: str = Query("", max_length=40), session: Session = Depends(get_session)) -> list[analytics.LearnerRow]:
    return analytics.learners(session, q.strip())


@router.get("/ai-spend", response_model=analytics.Spend)
def ai_spend(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)) -> analytics.Spend:
    return analytics.ai_spend(session, days)


@router.get("/errors")
def errors() -> list[dict]:
    return observability.recent_errors()


class Machine(BaseModel):
    container: str
    user_id: int
    username: str
    lab_id: str
    lab_title: str
    started_at: datetime | None
    files_mb: float


def _machines(session: Session) -> list[Machine]:
    running = containers.running_workspace_containers()
    rows = session.exec(select(Workspace).where(col(Workspace.container_name).in_(list(running) or [""]))).all()
    names = dict(session.exec(select(User.id, User.username).where(col(User.id).in_([w.user_id for w in rows] or [0]))).all())
    out = []
    for ws in rows:
        c = running[ws.container_name]
        try:
            title = get_lab(ws.lab_id).title
        except HTTPException:
            title = ws.lab_id
        started = c.attrs.get("State", {}).get("StartedAt", "")[:19]
        out.append(Machine(container=ws.container_name, user_id=ws.user_id, username=names.get(ws.user_id, f"#{ws.user_id}"),
                           lab_id=ws.lab_id, lab_title=title, started_at=datetime.fromisoformat(started) if started else None,
                           files_mb=round(limits.learner_files_mb(ws.user_id), 1)))
    return sorted(out, key=lambda m: m.started_at or datetime.min)


@router.get("/machines", response_model=list[Machine])
async def machines(session: Session = Depends(get_session)) -> list[Machine]:
    return await asyncio.to_thread(_machines, session)


class MachineAction(BaseModel):
    action: Literal["stop", "kill"]


def _act(session: Session, admin: User, container: str, action: str) -> None:
    ws = session.exec(select(Workspace).where(Workspace.container_name == container)).first()
    if ws is None:
        raise HTTPException(404, "No such machine")
    if action == "stop":
        limits.stop_machine(ws, "Stopped by an admin. Your files are kept: start it again to continue.", "admin")
    else:
        # Kill: remove the machine and its service containers (files and database data stay on disk; the
        # next start builds a fresh machine from them).
        with shared.lock(ws.container_name, wait=60):
            try:
                containers.client().containers.get(ws.container_name).remove(force=True)
            except NotFound:
                pass
            try:
                services.remove_services(get_lab(ws.lab_id), ws, wipe_data=False)
            except HTTPException:
                pass
        limits.set_reason(ws.container_name, "Your machine was reset by an admin. Your files are kept: start it again.")
    log.warning("Admin %s did %s on %s", admin.username, action, container)


@router.post("/machines/{container}")
async def machine_action(container: str, body: MachineAction, admin: User = Depends(require_admin),
                         session: Session = Depends(get_session)) -> dict:
    await asyncio.to_thread(_act, session, admin, container, body.action)
    return {"ok": True}
