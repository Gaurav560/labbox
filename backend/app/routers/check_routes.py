import asyncio
import time

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlmodel import Session

from .. import checker, limits, metrics, shared
from ..config import get_settings
from ..auth import get_current_user
from ..db import get_session
from ..labs import get_lab
from ..models import User

router = APIRouter(prefix="/api/labs/{lab_id}", tags=["check"])


class CheckBody(BaseModel):
    chapter_id: str


@router.post("/check", response_model=checker.CheckResponse)
async def check(
    lab_id: str, body: CheckBody, request: Request, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> checker.CheckResponse:
    assert user.id is not None
    key = f"check:ip:{limits.client_ip(request)}"
    limits.too_many(key, get_settings().CHECKS_PER_IP_MINUTE, 60, "Too many checks from your network. Wait a minute and try again.")
    shared.hit(key)
    lab = get_lab(lab_id)
    lab.chapter(body.chapter_id)  # 404 before taking the slot
    async with checker.check_slot(user.id):
        started = time.monotonic()
        try:
            out = await asyncio.to_thread(checker.run_check, session, user, lab, body.chapter_id)
        except Exception:
            metrics.count("labbox_checks_total", result="error")
            raise
        metrics.count("labbox_checks_total", result="passed" if out.passed_count == out.total_count else "failed")
        metrics.observe("labbox_check_duration_seconds", time.monotonic() - started, buckets=metrics.CHECK_BUCKETS)
        return out


@router.get("/checks", response_model=list[checker.CheckRunOut])
def checks(
    lab_id: str,
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[checker.CheckRunOut]:
    assert user.id is not None
    return checker.recent_checks(session, user.id, get_lab(lab_id), limit)
