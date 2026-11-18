import asyncio

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session

from .. import checker
from ..auth import get_current_user
from ..db import get_session
from ..labs import get_lab
from ..models import User

router = APIRouter(prefix="/api/labs/{lab_id}", tags=["check"])


class CheckBody(BaseModel):
    chapter_id: str


@router.post("/check", response_model=checker.CheckResponse)
async def check(
    lab_id: str, body: CheckBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> checker.CheckResponse:
    assert user.id is not None
    lab = get_lab(lab_id)
    lab.chapter(body.chapter_id)  # 404 before taking the slot
    async with checker.check_slot(user.id):
        return await asyncio.to_thread(checker.run_check, session, user, lab, body.chapter_id)


@router.get("/checks", response_model=list[checker.CheckRunOut])
def checks(
    lab_id: str,
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[checker.CheckRunOut]:
    assert user.id is not None
    return checker.recent_checks(session, user.id, get_lab(lab_id), limit)
