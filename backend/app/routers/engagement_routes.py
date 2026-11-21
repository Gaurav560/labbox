"""XP and streak stats, profile, daily drill, skill maps and onboarding."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, col, select

from .. import drills, engagement
from ..auth import get_current_user
from ..content import get_content
from ..db import get_session
from ..labs import all_labs
from ..models import ChapterProgress, User, utcnow

router = APIRouter(prefix="/api", tags=["engagement"])


def _uid(user: User) -> int:
    assert user.id is not None
    return user.id


# ---------- what to do next ----------


class NextOut(BaseModel):
    """The dashboard's first card: pick up where the learner left off, or where to start."""

    kind: Literal["continue", "start"]
    lab_id: str
    lab_title: str
    chapter_id: str
    chapter_title: str
    chapter_number: int
    chapters: int
    step: int  # 1-based, the step the learner will land on
    steps: int
    reason: str | None = None  # why this lab, for a new learner


def _id_number(chapter_id: str, fallback: int) -> int:
    """The number at the start of a chapter id ("11-reading-the-request" is 11)."""
    head = chapter_id.split("-", 1)[0]
    return int(head) if head.isdigit() else fallback


@router.get("/me/next", response_model=NextOut)
def my_next(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> NextOut:
    labs = {lab.id: lab for lab in all_labs()}
    rows = session.exec(
        select(ChapterProgress).where(ChapterProgress.user_id == _uid(user)).order_by(col(ChapterProgress.updated_at).desc())
    ).all()
    for row in rows:
        lab = labs.get(row.lab_id)
        ids = [c.id for c in lab.chapters] if lab else []
        if row.chapter_id not in ids:
            continue  # a lab or chapter that no longer exists
        i, step = ids.index(row.chapter_id), row.current_step
        if row.completed_at is not None and i + 1 < len(ids):
            i, step = i + 1, 0  # that chapter is done: the next one
        ch = lab.chapters[i]
        total = len(lab.chapter_steps(ch.id))
        # A course with a chapter 0 numbers chapters by their ids (the menu and the folders agree); "of N" is the last.
        zero = ids[0].startswith("00-")
        return NextOut(kind="continue", lab_id=lab.id, lab_title=lab.title, chapter_id=ch.id, chapter_title=ch.title,
                       chapter_number=_id_number(ch.id, i) if zero else i + 1,
                       chapters=_id_number(ids[-1], len(ids) - 1) if zero else len(ids),
                       step=min(step, total - 1) + 1, steps=total)
    # A new learner: the first lab of the goal they picked in onboarding, else the coding basics.
    goal_id = engagement.get_profile(session, _uid(user)).goal
    try:
        goals = _onboarding().goals
    except HTTPException:
        goals = []  # onboarding content missing: fall back to the coding basics
    goal = next((g for g in goals if g.id == goal_id), None)
    first = next((labs[s] for s in (goal.start if goal else []) if s in labs), None) or labs.get("python-basics") or next(iter(labs.values()))
    ch = first.chapters[0]
    return NextOut(kind="start", lab_id=first.id, lab_title=first.title, chapter_id=ch.id, chapter_title=ch.title,
                   chapter_number=0 if ch.id.startswith("00-") else 1,
                   chapters=_id_number(first.chapters[-1].id, len(first.chapters) - 1) if ch.id.startswith("00-") else len(first.chapters),
                   step=1, steps=len(first.chapter_steps(ch.id)),
                   reason=f"Picked for your goal: {goal.title}" if goal else "The best first lab: it builds the coding basics every track uses")


# ---------- stats and profile ----------


@router.get("/me/stats", response_model=engagement.Stats)
def my_stats(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> engagement.Stats:
    return engagement.stats(session, _uid(user))


class ProfileOut(BaseModel):
    display_name: str | None
    timezone: str | None
    goal: str | None
    placement_level: str | None


class ProfileBody(BaseModel):
    display_name: str | None = Field(default=None, max_length=60)
    timezone: str | None = Field(default=None, max_length=64)
    goal: str | None = None


def _profile_out(p) -> ProfileOut:
    return ProfileOut(display_name=p.display_name, timezone=p.timezone, goal=p.goal, placement_level=p.placement_level)


@router.get("/me/profile", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> ProfileOut:
    return _profile_out(engagement.get_profile(session, _uid(user)))


@router.put("/me/profile", response_model=ProfileOut)
def put_profile(body: ProfileBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> ProfileOut:
    p = engagement.get_profile(session, _uid(user))
    if body.timezone is not None:
        if not engagement.valid_timezone(body.timezone):
            raise HTTPException(422, f"Unknown timezone {body.timezone!r}")
        p.timezone = body.timezone  # only future XP uses it; past days stay as they were
    if body.goal is not None:
        ob = get_content().onboarding
        if not ob or body.goal not in {g.id for g in ob.goals}:
            raise HTTPException(422, f"Unknown goal {body.goal!r}")
        p.goal = body.goal
    if body.display_name is not None:
        p.display_name = body.display_name.strip() or None
    session.add(p)
    session.commit()
    return _profile_out(p)


# ---------- daily drill ----------


class DrillBody(BaseModel):
    choice: int = Field(ge=0)


@router.get("/drill/today", response_model=drills.DrillOut)
def drill_today(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> drills.DrillOut:
    return drills.today(session, _uid(user))


@router.post("/drill/today/answer", response_model=drills.DrillOut)
def drill_answer(body: DrillBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> drills.DrillOut:
    return drills.answer(session, _uid(user), body.choice)


# ---------- skill maps ----------


NodeState = Literal["done", "available", "locked", "coming_soon"]


class NodeChapter(BaseModel):
    lab_id: str
    chapter_id: str
    title: str
    done: bool


class NodeOut(BaseModel):
    id: str
    title: str
    requires: list[str]
    chapters: list[NodeChapter]
    state: NodeState


class SkillMap(BaseModel):
    track: str
    title: str
    nodes: list[NodeOut]


class TrackSummary(BaseModel):
    track: str
    title: str
    nodes: int
    done: int


def _skill_map(session: Session, user_id: int, track: str) -> SkillMap:
    t = get_content().tracks.get(track)
    if t is None:
        raise HTTPException(404, f"No skill map for track {track!r}")
    labs = {lab.id: lab for lab in all_labs()}
    done_by_lab = {lab_id: engagement.completed_chapters(session, user_id, lab_id) for lab_id in labs}
    chapters: dict[str, list[NodeChapter]] = {}
    for n in t.nodes:
        chapters[n.id] = []
        for ref in n.chapters:
            lab_id, chapter_id = ref.split("/", 1)
            ch = labs[lab_id].chapter(chapter_id)
            chapters[n.id].append(NodeChapter(lab_id=lab_id, chapter_id=chapter_id, title=ch.title, done=chapter_id in done_by_lab[lab_id]))
    done = {n.id for n in t.nodes if chapters[n.id] and all(c.done for c in chapters[n.id])}
    nodes = []
    for n in t.nodes:
        if n.id in done:
            state: NodeState = "done"
        elif not n.chapters:
            state = "coming_soon"
        elif set(n.requires) <= done:
            state = "available"
        else:
            state = "locked"
        nodes.append(NodeOut(id=n.id, title=n.title, requires=n.requires, chapters=chapters[n.id], state=state))
    return SkillMap(track=t.track, title=t.title, nodes=nodes)


@router.get("/tracks", response_model=list[TrackSummary])
def tracks(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[TrackSummary]:
    out = []
    for track in get_content().tracks:
        m = _skill_map(session, _uid(user), track)
        out.append(TrackSummary(track=m.track, title=m.title, nodes=len(m.nodes), done=sum(n.state == "done" for n in m.nodes)))
    return out


@router.get("/tracks/{track}/skills", response_model=SkillMap)
def skills(track: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> SkillMap:
    return _skill_map(session, _uid(user), track)


# ---------- onboarding ----------


class GoalOut(BaseModel):
    id: str
    title: str
    blurb: str


class QuestionOut(BaseModel):
    question: str
    options: list[str]


class OnboardingOut(BaseModel):
    goals: list[GoalOut]
    placement: list[QuestionOut]  # no answers: they are checked on the server


class OnboardingBody(BaseModel):
    goal: str
    answers: list[int]


class PlacementResult(BaseModel):
    correct: bool
    answer: int
    explain: str


class StartLab(BaseModel):
    lab_id: str
    title: str


class OnboardingResult(BaseModel):
    score: int
    level: Literal["beginner", "intermediate", "advanced"]
    results: list[PlacementResult]
    start: StartLab
    note: str | None  # e.g. no labs for this goal yet


def _onboarding():
    ob = get_content().onboarding
    if ob is None:
        raise HTTPException(404, "Onboarding is not set up")
    return ob


@router.get("/onboarding", response_model=OnboardingOut)
def onboarding(user: User = Depends(get_current_user)) -> OnboardingOut:
    ob = _onboarding()
    return OnboardingOut(
        goals=[GoalOut(id=g.id, title=g.title, blurb=g.blurb) for g in ob.goals],
        placement=[QuestionOut(question=q.question, options=q.options) for q in ob.placement],
    )


@router.post("/onboarding", response_model=OnboardingResult)
def finish_onboarding(
    body: OnboardingBody, user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> OnboardingResult:
    ob = _onboarding()
    goal = next((g for g in ob.goals if g.id == body.goal), None)
    if goal is None:
        raise HTTPException(422, f"Unknown goal {body.goal!r}")
    if len(body.answers) != len(ob.placement):
        raise HTTPException(422, f"Expected {len(ob.placement)} answers")
    results = [PlacementResult(correct=a == q.answer, answer=q.answer, explain=q.explain) for a, q in zip(body.answers, ob.placement)]
    score = sum(r.correct for r in results)
    level: Literal["beginner", "intermediate", "advanced"] = "advanced" if score >= 3 else "intermediate" if score == 2 else "beginner"

    labs = {lab.id: lab for lab in all_labs()}
    in_track = [lab for lab in labs.values() if lab.track == goal.track]
    first = next(labs[s] for s in goal.start if s in labs)
    note = None if in_track else f"{goal.title}: those labs are on the way. Start here: it builds the coding basics every track uses."

    p = engagement.get_profile(session, _uid(user))
    p.goal, p.placement_level, p.onboarded_at = goal.id, level, utcnow()
    session.add(p)
    session.commit()
    return OnboardingResult(score=score, level=level, results=results, start=StartLab(lab_id=first.id, title=first.title), note=note)


@router.post("/onboarding/skip", response_model=engagement.Stats)
def skip_onboarding(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> engagement.Stats:
    p = engagement.get_profile(session, _uid(user))
    if p.onboarded_at is None:
        p.onboarded_at = utcnow()
        session.add(p)
        session.commit()
    return engagement.stats(session, _uid(user))
