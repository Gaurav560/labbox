"""The daily drill: one short multiple choice question per learner per local day."""
import hashlib
from datetime import date, datetime

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, col, select

from . import engagement
from .content import Drill, get_content
from .labs import all_labs
from .models import DrillAnswer, Workspace, utcnow


class PublicDrill(BaseModel):
    id: str
    kind: str
    track: str
    question: str
    options: list[str]


class DrillOut(BaseModel):
    day: date
    drill: PublicDrill | None  # None when there are no drills at all
    wrong: list[int] = []
    solved: bool = False
    answer: int | None = None  # only once solved
    explain: str | None = None
    xp: int = engagement.XP_DRILL
    xp_awarded: list[engagement.XpAward] = []


def studying_tracks(session: Session, user_id: int) -> set[str]:
    """Tracks of the labs this learner opened, plus the track of their goal."""
    opened = set(session.exec(select(Workspace.lab_id).where(Workspace.user_id == user_id)).all())
    tracks = {lab.track for lab in all_labs() if lab.id in opened}
    profile = engagement.get_profile(session, user_id)
    ob = get_content().onboarding
    goal = next((g for g in ob.goals if g.id == profile.goal), None) if ob else None
    if goal:
        tracks.add(goal.track)
    return tracks


def _pick(session: Session, user_id: int, day: date) -> tuple[str, Drill] | None:
    drills = get_content().drills
    if not drills:
        return None
    # Once answered today, the drill stays the same even if the learner's tracks change.
    first = session.exec(
        select(DrillAnswer).where(DrillAnswer.user_id == user_id, DrillAnswer.day == day).order_by(col(DrillAnswer.id))
    ).first()
    if first is not None:
        for t, d in drills:
            if d.id == first.drill_id:
                return t, d
    tracks = studying_tracks(session, user_id)
    pool = [(t, d) for t, d in drills if t in tracks] or drills
    n = int(hashlib.sha256(f"{user_id}:{day.isoformat()}".encode()).hexdigest(), 16)
    return pool[n % len(pool)]


def today(session: Session, user_id: int, now: datetime | None = None) -> DrillOut:
    profile = engagement.get_profile(session, user_id)
    day = engagement.local_day(now or utcnow(), profile.timezone)
    picked = _pick(session, user_id, day)
    if picked is None:
        return DrillOut(day=day, drill=None)
    track, d = picked
    out = DrillOut(day=day, drill=PublicDrill(id=d.id, kind=d.kind, track=track, question=d.question, options=d.options))
    for a in session.exec(
        select(DrillAnswer).where(DrillAnswer.user_id == user_id, DrillAnswer.day == day, DrillAnswer.drill_id == d.id)
        .order_by(col(DrillAnswer.id))
    ).all():
        if a.correct:
            out.solved, out.answer, out.explain = True, d.answer, d.explain
            break
        if a.choice not in out.wrong:
            out.wrong.append(a.choice)
    return out


def answer(session: Session, user_id: int, choice: int, now: datetime | None = None) -> DrillOut:
    now = now or utcnow()
    current = today(session, user_id, now)
    if current.drill is None:
        raise HTTPException(404, "There is no drill today")
    if current.solved:
        return current
    _, d = _pick(session, user_id, current.day)  # type: ignore[misc]
    if not 0 <= choice < len(d.options):
        raise HTTPException(422, f"Choice must be between 0 and {len(d.options) - 1}")
    session.add(DrillAnswer(user_id=user_id, day=current.day, drill_id=d.id, choice=choice, correct=choice == d.answer, created_at=now))
    session.commit()
    out = today(session, user_id, now)
    if out.solved:
        a = engagement.award(session, user_id, "drill", engagement.XP_DRILL, f"drill:{current.day.isoformat()}", at=now, label="Daily drill")
        out.xp_awarded = [a] if a else []
    return out
