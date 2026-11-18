"""XP, levels and streaks (v2 spec section 5.1).

Everything is derived from the xp_event ledger. The rules are plain functions of
(events, timezone, now) so tests can run them with fixed clocks.
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from .labs import LabConfig
from .models import ChapterProgress, PredictAnswer, TaskProgress, UserProfile, XpEvent, utcnow

STREAK_MIN_XP = 20  # a day counts for the streak at this much XP
XP_PREDICT_FIRST_TRY = 10
XP_CHAPTER = 50
XP_LAB = 200
XP_DRILL = 20
DEFAULT_TZ = "UTC"


class XpAward(BaseModel):
    kind: str
    amount: int
    label: str = ""


# ---------- pure rules ----------


def xp_for_level(level: int) -> int:
    """Total XP needed to reach `level`. Everyone starts at level 1; level 2 needs 100, level 3 needs 283."""
    return 0 if level <= 1 else round(100 * (level - 1) ** 1.5)


def level_for(xp: int) -> int:
    level = 1
    while xp >= xp_for_level(level + 1):
        level += 1
    return level


def tz_or_default(name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(name or DEFAULT_TZ)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo(DEFAULT_TZ)


def valid_timezone(name: str) -> bool:
    try:
        ZoneInfo(name)
        return True
    except (ZoneInfoNotFoundError, ValueError):
        return False


def local_day(at_utc: datetime, tz_name: str | None) -> date:
    """The learner's calendar day for a naive-UTC timestamp."""
    return at_utc.replace(tzinfo=timezone.utc).astimezone(tz_or_default(tz_name)).date()


@dataclass
class Streak:
    current: int
    best: int
    freeze_available: bool  # this week's freeze not used yet
    frozen_days: list[date]


def _week(d: date) -> tuple[int, int]:
    iso = d.isocalendar()
    return iso[0], iso[1]


def compute_streak(day_xp: dict[date, int], today: date) -> Streak:
    """Consecutive days with at least STREAK_MIN_XP, ending today or yesterday.

    Today never breaks the streak (the day is not over yet). One freeze per ISO week
    (Monday to Sunday) covers a single missed day: two missed days in a row still break it.
    A frozen day keeps the streak alive but does not add to it.
    """
    qualifying = {d for d, xp in day_xp.items() if xp >= STREAK_MIN_XP and d <= today}
    run = best = 0
    used_weeks: set[tuple[int, int]] = set()
    frozen: list[date] = []
    if qualifying:
        d = min(qualifying)
        prev_qualified = False
        while d <= today:
            if d in qualifying:
                run += 1
                prev_qualified = True
            elif d == today:
                pass  # still time to practise today
            elif run > 0 and prev_qualified and _week(d) not in used_weeks:
                used_weeks.add(_week(d))
                frozen.append(d)
                prev_qualified = False
            else:
                run = 0
                prev_qualified = False
            best = max(best, run)
            d += timedelta(days=1)
    return Streak(current=run, best=best, freeze_available=_week(today) not in used_weeks, frozen_days=frozen)


# ---------- profile and ledger ----------


def get_profile(session: Session, user_id: int) -> UserProfile:
    """Get or create the profile.

    Users who existed before XP got a profile from migration 0004 with backfilled_at unset:
    the first time it is read here, their earlier progress is turned into XP. A profile
    created here is a brand new learner (onboarding not done, nothing to backfill).
    """
    profile = session.get(UserProfile, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id, backfilled_at=utcnow())
        session.add(profile)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            found = session.get(UserProfile, user_id)
            assert found is not None
            return found
        session.refresh(profile)
        return profile
    if profile.backfilled_at is None:
        profile.backfilled_at = utcnow()  # first, so awards made by the backfill do not start it again
        session.add(profile)
        session.commit()
        backfill(session, user_id)
        session.refresh(profile)
    return profile


def award(
    session: Session,
    user_id: int,
    kind: str,
    amount: int,
    ref: str,
    *,
    lab_id: str | None = None,
    chapter_id: str | None = None,
    task_id: str | None = None,
    at: datetime | None = None,
    label: str = "",
    refresh: bool = True,
) -> XpAward | None:
    """Add a ledger entry once per (user, ref). Returns None if it was already awarded."""
    profile = get_profile(session, user_id)  # first: it may backfill, which can award this same ref
    if session.exec(select(XpEvent.id).where(XpEvent.user_id == user_id, XpEvent.ref == ref)).first() is not None:
        return None
    at = at or utcnow()
    session.add(
        XpEvent(
            user_id=user_id,
            kind=kind,
            amount=amount,
            ref=ref,
            day=local_day(at, profile.timezone),
            lab_id=lab_id,
            chapter_id=chapter_id,
            task_id=task_id,
            created_at=at,
        )
    )
    try:
        session.commit()
    except IntegrityError:
        session.rollback()  # the same award landed from another request
        return None
    if refresh:
        refresh_profile(session, user_id)
    return XpAward(kind=kind, amount=amount, label=label)


def _day_xp(session: Session, user_id: int) -> dict[date, int]:
    totals: dict[date, int] = {}
    for e in session.exec(select(XpEvent).where(XpEvent.user_id == user_id)).all():
        totals[e.day] = totals.get(e.day, 0) + e.amount
    return totals


class Stats(BaseModel):
    xp_total: int
    level: int
    level_xp: int  # XP at which the current level started
    next_level_xp: int
    streak_current: int
    streak_best: int
    freeze_available: bool
    today_xp: int
    streak_min_xp: int = STREAK_MIN_XP
    timezone: str | None
    goal: str | None
    needs_onboarding: bool


def stats(session: Session, user_id: int, now: datetime | None = None) -> Stats:
    profile = get_profile(session, user_id)
    today = local_day(now or utcnow(), profile.timezone)
    day_xp = _day_xp(session, user_id)
    total = sum(day_xp.values())
    level = level_for(total)
    streak = compute_streak(day_xp, today)
    return Stats(
        xp_total=total,
        level=level,
        level_xp=xp_for_level(level),
        next_level_xp=xp_for_level(level + 1),
        streak_current=streak.current,
        streak_best=streak.best,
        freeze_available=streak.freeze_available,
        today_xp=day_xp.get(today, 0),
        timezone=profile.timezone,
        goal=profile.goal,
        needs_onboarding=profile.onboarded_at is None,
    )


def refresh_profile(session: Session, user_id: int, now: datetime | None = None) -> UserProfile:
    """Store the derived totals on the profile (handy for admin views and leagues later)."""
    s = stats(session, user_id, now)
    profile = get_profile(session, user_id)
    last = session.exec(select(XpEvent.day).where(XpEvent.user_id == user_id).order_by(col(XpEvent.day).desc())).first()
    profile.xp_total, profile.level = s.xp_total, s.level
    profile.streak_current, profile.streak_best, profile.last_active_day = s.streak_current, s.streak_best, last
    session.add(profile)
    session.commit()
    return profile


def chapter_xp(session: Session, user_id: int, lab_id: str, chapter_id: str) -> int:
    rows = session.exec(
        select(XpEvent.amount).where(XpEvent.user_id == user_id, XpEvent.lab_id == lab_id, XpEvent.chapter_id == chapter_id)
    ).all()
    return sum(rows)


# ---------- what earns XP ----------


def _task_ref(lab_id: str, task_id: str) -> str:
    return f"task:{lab_id}:{task_id}"


def award_for_check(session: Session, user_id: int, lab: LabConfig, chapter_id: str, passed: dict[str, bool]) -> list[XpAward]:
    """After a Check: first passes, a completed chapter, a completed lab."""
    from .progress import task_xp  # imported here: progress imports this module

    out: list[XpAward] = []
    chapter = lab.chapter(chapter_id)
    for t in chapter.tasks:
        if not passed.get(t.id):
            continue
        tp = session.get(TaskProgress, {"user_id": user_id, "lab_id": lab.id, "task_id": t.id})
        hints = tp.hints_used if tp else 0
        a = award(session, user_id, "task", task_xp(t.xp, hints), _task_ref(lab.id, t.id),
                  lab_id=lab.id, chapter_id=chapter_id, task_id=t.id, label=t.title, refresh=False)
        if a:
            out.append(a)
    if chapter.tasks and all(passed.get(t.id) for t in chapter.tasks):
        a = award(session, user_id, "chapter", XP_CHAPTER, f"chapter:{lab.id}:{chapter_id}",
                  lab_id=lab.id, chapter_id=chapter_id, label=f"Chapter complete: {chapter.title}", refresh=False)
        if a:
            out.append(a)
            cp = session.get(ChapterProgress, {"user_id": user_id, "lab_id": lab.id, "chapter_id": chapter_id})
            if cp is not None and cp.completed_at is None:
                cp.completed_at = utcnow()
                session.add(cp)
                session.commit()
        done = completed_chapters(session, user_id, lab.id)
        if all(c.id in done for c in lab.chapters):
            a = award(session, user_id, "lab", XP_LAB, f"lab:{lab.id}", lab_id=lab.id, label=f"Lab complete: {lab.title}", refresh=False)
            if a:
                out.append(a)
    if out:
        refresh_profile(session, user_id)
    return out


def award_for_predict(session: Session, user_id: int, lab_id: str, chapter_id: str, step_index: int) -> list[XpAward]:
    """+10 when the very first attempt at a predict step was right."""
    first = session.exec(
        select(PredictAnswer)
        .where(PredictAnswer.user_id == user_id, PredictAnswer.lab_id == lab_id,
               PredictAnswer.chapter_id == chapter_id, PredictAnswer.step_index == step_index)
        .order_by(col(PredictAnswer.id))
    ).first()
    if first is None or not first.correct:
        return []
    a = award(session, user_id, "predict", XP_PREDICT_FIRST_TRY, f"predict:{lab_id}:{chapter_id}:{step_index}",
              lab_id=lab_id, chapter_id=chapter_id, at=first.created_at, label="Right first time")
    return [a] if a else []


def completed_chapters(session: Session, user_id: int, lab_id: str) -> set[str]:
    rows = session.exec(select(XpEvent.chapter_id).where(XpEvent.user_id == user_id, XpEvent.kind == "chapter", XpEvent.lab_id == lab_id)).all()
    return {r for r in rows if r}


def backfill(session: Session, user_id: int) -> None:
    """Turn progress made before the ledger existed into XP, dated when it happened. Safe to run again."""
    from .labs import all_labs
    from .progress import task_xp

    for lab in all_labs():
        tps = {
            tp.task_id: tp
            for tp in session.exec(select(TaskProgress).where(TaskProgress.user_id == user_id, TaskProgress.lab_id == lab.id)).all()
        }
        finished: list[datetime] = []
        for ch in lab.chapters:
            passes = []
            for t in ch.tasks:
                tp = tps.get(t.id)
                if tp is None or tp.first_passed_at is None:
                    continue
                passes.append(tp.first_passed_at)
                award(session, user_id, "task", task_xp(t.xp, tp.hints_used), _task_ref(lab.id, t.id),
                      lab_id=lab.id, chapter_id=ch.id, task_id=t.id, at=tp.first_passed_at, refresh=False)
            if len(passes) == len(ch.tasks) and all(tps[t.id].passed for t in ch.tasks):
                at = max(passes)
                finished.append(at)
                award(session, user_id, "chapter", XP_CHAPTER, f"chapter:{lab.id}:{ch.id}",
                      lab_id=lab.id, chapter_id=ch.id, at=at, refresh=False)
        if len(finished) == len(lab.chapters):
            award(session, user_id, "lab", XP_LAB, f"lab:{lab.id}", lab_id=lab.id, at=max(finished), refresh=False)

    firsts: dict[tuple[str, str, int], PredictAnswer] = {}
    for pa in session.exec(select(PredictAnswer).where(PredictAnswer.user_id == user_id).order_by(col(PredictAnswer.id))).all():
        firsts.setdefault((pa.lab_id, pa.chapter_id, pa.step_index), pa)
    for (lab_id, chapter_id, step), pa in firsts.items():
        if pa.correct:
            award(session, user_id, "predict", XP_PREDICT_FIRST_TRY, f"predict:{lab_id}:{chapter_id}:{step}",
                  lab_id=lab_id, chapter_id=chapter_id, at=pa.created_at, refresh=False)
    refresh_profile(session, user_id)
