"""Jarvis, the learner's realtime voice assistant (owner, 28 November). See app/jarvis.py for the rules."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from .. import jarvis
from ..auth import get_current_user
from ..db import get_session
from ..models import User
from .admin_routes import require_admin

router = APIRouter(prefix="/api/jarvis", tags=["jarvis"])
admin_router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/status", response_model=jarvis.Status)
def status(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> jarvis.Status:
    return jarvis.status(session, user)


class StartIn(BaseModel):
    lab_id: str | None = None
    chapter_id: str | None = None
    step: int | None = Field(None, ge=0, le=500)
    reason: Literal["fails", "hints", "idle"] | None = None  # set when the learner accepted Jarvis's offer of help


@router.get("/nudge", response_model=jarvis.Nudge)
def nudge(lab_id: str, chapter_id: str, step: int, idle: int = 0, user: User = Depends(get_current_user),
          session: Session = Depends(get_session)) -> jarvis.Nudge:
    """Is this learner stuck on the task in front of them? Rules only, no model: the lab page asks after every check
    and now and then while they work."""
    return jarvis.nudge(session, user, lab_id, chapter_id, step, max(0, min(idle, 24 * 3600)))


@router.post("/session", response_model=jarvis.SessionOut)
async def start(body: StartIn, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> jarvis.SessionOut:
    return await jarvis.start(session, user, body.lab_id, body.chapter_id, body.step, body.reason)


@router.post("/session/{session_id}/heartbeat", response_model=jarvis.HeartbeatOut)
async def heartbeat(session_id: int, body: jarvis.Heartbeat, user: User = Depends(get_current_user),
                    session: Session = Depends(get_session)) -> jarvis.HeartbeatOut:
    return await jarvis.heartbeat(session, user, session_id, body)


class ToolIn(BaseModel):
    name: str = Field(..., max_length=40)
    step: int | None = Field(None, ge=0, le=500)  # the step on screen now (the learner may have moved on)


class ToolOut(BaseModel):
    output: str


@router.post("/session/{session_id}/tool", response_model=ToolOut)
def tool(session_id: int, body: ToolIn, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> ToolOut:
    js = jarvis.own_session(session, user, session_id)
    if js.ended_at is not None:
        raise HTTPException(409, "This conversation has ended")
    return ToolOut(output=jarvis.run_tool(session, user, js, body.name, body.step)[:12_000])


# ---------- admin ----------

@admin_router.get("/jarvis", response_model=jarvis.AdminSummary)
def admin_summary(session: Session = Depends(get_session)) -> jarvis.AdminSummary:
    return jarvis.admin_summary(session)


class JarvisSettings(BaseModel):
    jarvis_daily_usd: float | None = Field(None, ge=0, le=100)
    jarvis_monthly_usd: float | None = Field(None, ge=0, le=1000)
    jarvis_pro_minutes: float | None = Field(None, ge=0, le=240)
    jarvis_trial_minutes: float | None = Field(None, ge=0, le=30)
    jarvis_trials_per_day: float | None = Field(None, ge=0, le=1000)


@admin_router.put("/jarvis", response_model=jarvis.AdminSummary)
def set_settings(body: JarvisSettings, admin: User = Depends(require_admin), session: Session = Depends(get_session)) -> jarvis.AdminSummary:
    jarvis.set_settings(session, {k: v for k, v in body.model_dump().items() if v is not None}, admin.id)
    return jarvis.admin_summary(session)


class PlanIn(BaseModel):
    plan: Literal["free", "pro"]


@admin_router.put("/learners/{user_id}/plan", response_model=PlanIn)
def set_plan(user_id: int, body: PlanIn, admin: User = Depends(require_admin), session: Session = Depends(get_session)) -> PlanIn:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(404, "No such learner")
    user.plan = body.plan
    session.add(user)
    session.commit()
    jarvis.log.warning("Admin %s set the plan of %s to %s", admin.username, user.username, body.plan)
    return PlanIn(plan=user.plan)
