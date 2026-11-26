"""At most a few labs at a time (owner, 25 and 26 November), "so that they dont get overwhelmed by no of labs and
study nothing".

- An admin sets the limit for everyone (site_setting "lab_limit"; "0" or no row: every lab is open, the default)
  and may give one learner their own number (user.lab_limit: 0 is every lab). Admins are never limited.
- A learner unlocks a lab on its course page with a button. A locked lab shows that page only: its lessons,
  machine, terminal, editor, checks and tutor all answer 403.
- A lab counts as finished when 80% of its tasks have passed at least once. A finished lab no longer uses a slot
  and stays open for good.
- On Monday (00:00 to 24:00 India time) a learner may swap: release an unfinished lab to free its slot. Progress
  is kept; the lab is locked again until it is unlocked again.
- When an admin lowers the limit, labs already unlocked stay open; nothing new unlocks until a slot is free.
"""
from datetime import datetime, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, col, select

from . import shared
from .auth import get_current_user
from .db import get_session
from .labs import LabConfig, all_labs, get_lab
from .models import LabSlot, SiteSetting, TaskProgress, User, utcnow

IST = ZoneInfo("Asia/Kolkata")
FINISH_SHARE = 0.8  # of a lab's tasks, passed at least once
LIMIT_KEY = "lab_limit"
LOCKED = "This lab is locked. Unlock it on its course page to read its lessons and start its machine."

Access = Literal["open", "unlocked", "finished", "locked"]


def now() -> datetime:
    """The time (tests replace it to make a Monday)."""
    return datetime.now(timezone.utc)


# ---------- the limit ----------

def site_limit(session: Session) -> int | None:
    """The limit for everyone: None means every lab is open."""
    row = session.get(SiteSetting, LIMIT_KEY)
    try:
        n = int(row.value) if row else 0
    except ValueError:
        n = 0
    return n if n > 0 else None


def set_site_limit(session: Session, limit: int | None, admin_id: int | None) -> int | None:
    row = session.get(SiteSetting, LIMIT_KEY) or SiteSetting(key=LIMIT_KEY)
    row.value = str(limit or 0)
    row.updated_at = utcnow()
    row.updated_by = admin_id
    session.add(row)
    session.commit()
    return site_limit(session)


def user_limit(session: Session, user: User) -> int | None:
    """How many labs this learner may have unlocked at once: None means every lab."""
    if user.is_admin:
        return None
    if user.lab_limit is not None:
        return user.lab_limit if user.lab_limit > 0 else None
    return site_limit(session)


# ---------- finished labs and the Monday swap ----------

def _passed_by_lab(session: Session, user_id: int) -> dict[str, set[str]]:
    rows = session.exec(select(TaskProgress.lab_id, TaskProgress.task_id)
                        .where(TaskProgress.user_id == user_id, col(TaskProgress.first_passed_at).is_not(None))).all()
    out: dict[str, set[str]] = {}
    for lab_id, task_id in rows:
        out.setdefault(lab_id, set()).add(task_id)
    return out


def is_finished(lab: LabConfig, passed: set[str]) -> bool:
    ids = {t.id for c in lab.chapters for t in c.tasks}
    return bool(ids) and len(ids & passed) >= FINISH_SHARE * len(ids)


def swap_open(at: datetime | None = None) -> bool:
    return (at or now()).astimezone(IST).weekday() == 0


def next_swap(at: datetime | None = None) -> datetime:
    """When the next swap day starts (Monday 00:00 India time); today's, if today is Monday."""
    local = (at or now()).astimezone(IST)
    monday = (local - timedelta(days=local.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return monday if local.weekday() == 0 else monday + timedelta(days=7)


# ---------- a learner's labs ----------

class SlotsOut(BaseModel):
    limit: int | None  # None: every lab is open
    used: int  # unlocked labs that are not finished yet
    free: int | None  # None: no limit
    swap_open: bool  # today is Monday in India
    next_swap: datetime  # when the next swap day starts
    labs: dict[str, Access]  # every lab id


def _active(session: Session, user_id: int) -> dict[str, LabSlot]:
    rows = session.exec(select(LabSlot).where(LabSlot.user_id == user_id, col(LabSlot.released_at).is_(None))).all()
    return {r.lab_id: r for r in rows}


def _access(lab: LabConfig, limit: int | None, active: dict[str, LabSlot], passed: dict[str, set[str]]) -> Access:
    if is_finished(lab, passed.get(lab.id, set())):
        return "finished"
    if lab.id in active:
        return "unlocked"
    return "open" if limit is None else "locked"


def state(session: Session, user: User) -> SlotsOut:
    assert user.id is not None
    limit = user_limit(session, user)
    active = _active(session, user.id)
    passed = _passed_by_lab(session, user.id)
    labs = {lab.id: _access(lab, limit, active, passed) for lab in all_labs()}
    used = sum(1 for v in labs.values() if v == "unlocked")
    return SlotsOut(limit=limit, used=used, free=None if limit is None else max(0, limit - used),
                    swap_open=swap_open(), next_swap=next_swap(), labs=labs)


def access(session: Session, user: User, lab: LabConfig) -> Access:
    assert user.id is not None
    return _access(lab, user_limit(session, user), _active(session, user.id), _passed_by_lab(session, user.id))


def require_open(session: Session, user: User, lab: LabConfig) -> None:
    if access(session, user, lab) == "locked":
        raise HTTPException(403, LOCKED, headers={"X-Labbox-Locked": "1"})


def lab_open(lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> None:
    """A route dependency: 403 when the learner has not unlocked this lab."""
    require_open(session, user, get_lab(lab_id))


def unlock(session: Session, user: User, lab: LabConfig) -> SlotsOut:
    assert user.id is not None
    with shared.lock(f"slots-u{user.id}"):
        now_state = state(session, user)
        if now_state.labs.get(lab.id) == "locked":
            if now_state.free is not None and now_state.free <= 0:
                n = now_state.limit
                raise HTTPException(409, f"All {n} of your lab slots are in use. Finish a lab (80% of its tasks) "
                                         "or swap one on Monday to free a slot.")
            row = session.get(LabSlot, (user.id, lab.id)) or LabSlot(user_id=user.id, lab_id=lab.id)
            row.unlocked_at = utcnow()
            row.released_at = None
            row.released_reason = None
            session.add(row)
            session.commit()
        return state(session, user)


def swap(session: Session, user: User, lab: LabConfig) -> SlotsOut:
    """Release an unfinished lab on Monday (India time); its progress stays."""
    assert user.id is not None
    if not swap_open():
        raise HTTPException(409, "Swaps open on Monday, from 00:00 India time.")
    with shared.lock(f"slots-u{user.id}"):
        row = session.get(LabSlot, (user.id, lab.id))
        if row is None or row.released_at is not None or access(session, user, lab) != "unlocked":
            raise HTTPException(409, "Only an unlocked lab that is not finished can be swapped.")
        row.released_at = utcnow()
        row.released_reason = "swapped"
        session.add(row)
        session.commit()
        return state(session, user)
