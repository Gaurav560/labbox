"""At most a few labs at a time (owner, 26 November): the learner's slots, unlocking a lab and the Monday swap.
The rules are in app/slots.py."""
import asyncio
import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session

from .. import containers, slots
from ..auth import get_current_user
from ..db import get_session
from ..labs import get_lab
from ..models import User

log = logging.getLogger("labbox.slots")

router = APIRouter(prefix="/api", tags=["slots"])


@router.get("/slots", response_model=slots.SlotsOut)
def my_slots(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> slots.SlotsOut:
    return slots.state(session, user)


@router.post("/labs/{lab_id}/unlock", response_model=slots.SlotsOut)
def unlock(lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> slots.SlotsOut:
    out = slots.unlock(session, user, get_lab(lab_id))
    log.info("Lab unlocked user=%s lab=%s used=%s limit=%s", user.id, lab_id, out.used, out.limit)
    return out


@router.post("/labs/{lab_id}/swap", response_model=slots.SlotsOut)
async def swap(lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> slots.SlotsOut:
    lab = get_lab(lab_id)
    out = await asyncio.to_thread(slots.swap, session, user, lab)
    log.info("Lab swapped out user=%s lab=%s", user.id, lab_id)
    try:  # the lab is locked now: its machine stops (its files stay)
        await asyncio.to_thread(containers.stop_group, session, user, lab)
    except Exception:  # never started, or already gone
        pass
    return out
