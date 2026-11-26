"""Numbers for the admin page (Phase J). Most come from tables LabBox already keeps, so they cover the
past too; the time spent per step comes from analytics_event ("step" events, from Phase J on).

- funnel: sign up, opened a lab, first check passed, chapter 1 done, chapter 2 done.
- lab_report: per chapter, where learners stopped (the step an unfinished chapter was left on) and the
  average time per step; per task, pass rate, failed checks and hints, ranked so confusing tasks
  (a content bug, says the spec) come first.
"""
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, col, select

from .labs import LabConfig, all_labs
from .models import AnalyticsEvent, ChapterProgress, CheckRun, LlmRequest, TaskProgress, User, UserProfile, Workspace, utcnow

STALLED_AFTER = timedelta(days=2)  # an unfinished chapter untouched this long counts as "stopped here"
STEP_GAP_CAP = 30 * 60  # longer than this between two steps: they left, so the gap is not time spent


def since(window: str) -> datetime | None:
    days = {"7d": 7, "30d": 30, "90d": 90}.get(window)
    return utcnow() - timedelta(days=days) if days else None


# ---------- funnel ----------


class FunnelStep(BaseModel):
    key: str
    label: str
    count: int
    of_previous: float | None  # share of the step before, 0..1
    of_first: float | None


def funnel(session: Session, window: str = "30d") -> list[FunnelStep]:
    start = since(window)
    q = select(User.id)
    if start:
        q = q.where(User.created_at >= start)
    users = set(session.exec(q).all())
    if not users:
        return []
    ids = list(users)
    opened = set(session.exec(select(Workspace.user_id).where(col(Workspace.user_id).in_(ids))).all())
    passed = set(session.exec(select(TaskProgress.user_id).where(col(TaskProgress.user_id).in_(ids), TaskProgress.passed == True)).all())  # noqa: E712
    first_ch = {lab.id: lab.chapters[0].id for lab in all_labs() if lab.chapters}
    second_ch = {lab.id: lab.chapters[1].id for lab in all_labs() if len(lab.chapters) > 1}
    done = session.exec(select(ChapterProgress.user_id, ChapterProgress.lab_id, ChapterProgress.chapter_id).where(
        col(ChapterProgress.user_id).in_(ids), col(ChapterProgress.completed_at).is_not(None))).all()
    ch1 = {u for u, lab, ch in done if first_ch.get(lab) == ch}
    ch2 = {u for u, lab, ch in done if second_ch.get(lab) == ch}
    steps = [("signed_up", "Signed up", users), ("opened_lab", "Opened a lab", opened & users),
             ("first_pass", "Passed a first check", passed & users), ("chapter_1", "Finished a chapter 1", ch1 & users),
             ("chapter_2", "Finished a chapter 2", ch2 & users)]
    out, first, prev = [], len(users), None
    for key, label, group in steps:
        n = len(group)
        out.append(FunnelStep(key=key, label=label, count=n, of_previous=n / prev if prev else None, of_first=n / first))
        prev = n
    return out


# ---------- labs ----------


class StepReport(BaseModel):
    index: int
    title: str
    type: str
    stopped_here: int  # unfinished chapters left on this step for STALLED_AFTER
    avg_seconds: float | None  # time spent on the step (from step events)
    views: int


class ChapterReport(BaseModel):
    id: str
    title: str
    started: int
    completed: int
    steps: list[StepReport]


class TaskReport(BaseModel):
    id: str
    title: str
    chapter_id: str
    attempted: int  # learners who checked this task at least once
    passed: int
    pass_rate: float | None
    failed_checks_per_learner: float
    hints_per_learner: float
    hint_count: int
    confusion: float  # higher: look at this task first


class LabReport(BaseModel):
    id: str
    title: str
    learners: int
    chapters: list[ChapterReport]
    tasks: list[TaskReport]


class LabSummaryRow(BaseModel):
    id: str
    title: str
    learners: int
    chapters_completed: int
    pass_rate: float | None
    most_confusing_task: str | None


def _step_times(session: Session, lab_id: str) -> dict[tuple[str, int], list[float]]:
    rows = session.exec(select(AnalyticsEvent.user_id, AnalyticsEvent.chapter_id, AnalyticsEvent.step_index, AnalyticsEvent.created_at)
                        .where(AnalyticsEvent.kind == "step", AnalyticsEvent.lab_id == lab_id)
                        .order_by(AnalyticsEvent.user_id, AnalyticsEvent.created_at)).all()
    times: defaultdict[tuple[str, int], list[float]] = defaultdict(list)
    for (u, ch, step, at), nxt in zip(rows, rows[1:]):
        if nxt[0] == u and nxt[1] == ch:
            gap = (nxt[3] - at).total_seconds()
            if 0 < gap <= STEP_GAP_CAP:
                times[(ch or "", step or 0)].append(gap)
    return times


def _views(session: Session, lab_id: str) -> Counter:
    rows = session.exec(select(AnalyticsEvent.chapter_id, AnalyticsEvent.step_index, func.count())
                        .where(AnalyticsEvent.kind == "step", AnalyticsEvent.lab_id == lab_id)
                        .group_by(AnalyticsEvent.chapter_id, AnalyticsEvent.step_index)).all()
    return Counter({(ch or "", step or 0): n for ch, step, n in rows})


def _task_checks(session: Session, lab_id: str) -> tuple[dict[str, set[int]], Counter]:
    """Per task: learners who checked it, and how many checks it failed (from every check run)."""
    tried: defaultdict[str, set[int]] = defaultdict(set)
    fails: Counter = Counter()
    for user_id, results in session.exec(select(CheckRun.user_id, CheckRun.results_json).where(CheckRun.lab_id == lab_id)).all():
        try:
            for r in json.loads(results or "[]"):
                tried[r["task"]].add(user_id)
                if not r.get("passed"):
                    fails[r["task"]] += 1
        except (ValueError, KeyError, TypeError):
            continue
    return tried, fails


def lab_report(session: Session, lab: LabConfig) -> LabReport:
    now = utcnow()
    progress = session.exec(select(ChapterProgress).where(ChapterProgress.lab_id == lab.id)).all()
    times, views = _step_times(session, lab.id), _views(session, lab.id)
    chapters = []
    for ch in lab.chapters:
        rows = [p for p in progress if p.chapter_id == ch.id]
        stalled = Counter(p.current_step for p in rows if p.completed_at is None and now - p.updated_at > STALLED_AFTER)
        steps = [StepReport(index=i, title=s.title or s.type.capitalize(), type=s.type, stopped_here=stalled.get(i, 0),
                            avg_seconds=round(sum(t) / len(t), 1) if (t := times.get((ch.id, i))) else None,
                            views=views.get((ch.id, i), 0))
                 for i, s in enumerate(lab.chapter_steps(ch.id))]
        chapters.append(ChapterReport(id=ch.id, title=ch.title, started=len(rows),
                                      completed=sum(1 for p in rows if p.completed_at), steps=steps))
    tried, fails = _task_checks(session, lab.id)
    tp = session.exec(select(TaskProgress).where(TaskProgress.lab_id == lab.id)).all()
    tasks = []
    for ch in lab.chapters:
        for t in ch.tasks:
            rows = [r for r in tp if r.task_id == t.id]
            who = tried.get(t.id, set()) | {r.user_id for r in rows if r.passed}
            n = len(who)
            passed = sum(1 for r in rows if r.passed)
            hints = sum(r.hints_used for r in rows)
            rate = passed / n if n else None
            fails_pl = fails.get(t.id, 0) / n if n else 0.0
            hints_pl = hints / n if n else 0.0
            # Low pass rate, many failed checks and heavy hint use each push a task up the list.
            confusion = round((1 - (rate if rate is not None else 1)) * 2 + min(fails_pl, 5) / 5
                              + (hints_pl / len(t.hints) if t.hints else 0), 3) if n else 0.0
            tasks.append(TaskReport(id=t.id, title=t.title, chapter_id=ch.id, attempted=n, passed=passed, pass_rate=rate,
                                    failed_checks_per_learner=round(fails_pl, 2), hints_per_learner=round(hints_pl, 2),
                                    hint_count=len(t.hints), confusion=confusion))
    tasks.sort(key=lambda r: (-r.confusion, -r.attempted))
    learners = len(set(session.exec(select(Workspace.user_id).where(Workspace.lab_id == lab.id)).all()))
    return LabReport(id=lab.id, title=lab.title, learners=learners, chapters=chapters, tasks=tasks)


def labs_summary(session: Session) -> list[LabSummaryRow]:
    out = []
    for lab in all_labs():
        r = lab_report(session, lab)
        tried = sum(t.attempted for t in r.tasks)
        out.append(LabSummaryRow(id=lab.id, title=lab.title, learners=r.learners,
                                 chapters_completed=sum(c.completed for c in r.chapters),
                                 pass_rate=(sum(t.passed for t in r.tasks) / tried) if tried else None,
                                 most_confusing_task=next((t.title for t in r.tasks if t.attempted and t.confusion > 0), None)))
    return sorted(out, key=lambda r: -r.learners)


# ---------- learners and AI spend ----------


class LearnerRow(BaseModel):
    id: int
    username: str
    joined: datetime
    is_admin: bool
    labs: int
    xp: int
    checks: int
    last_active: datetime | None
    lab_limit: int | None = None  # None: the site's setting; 0: every lab


def learners(session: Session, query: str = "", limit: int = 50) -> list[LearnerRow]:
    q = select(User).order_by(col(User.created_at).desc()).limit(limit)
    if query:
        q = select(User).where(col(User.username).ilike(f"%{query}%")).order_by(User.username).limit(limit)
    users = session.exec(q).all()
    ids = [u.id for u in users]
    if not ids:
        return []
    labs = dict(session.exec(select(Workspace.user_id, func.count()).where(col(Workspace.user_id).in_(ids)).group_by(Workspace.user_id)).all())
    active = dict(session.exec(select(Workspace.user_id, func.max(Workspace.last_active_at)).where(col(Workspace.user_id).in_(ids)).group_by(Workspace.user_id)).all())
    checks = dict(session.exec(select(CheckRun.user_id, func.count()).where(col(CheckRun.user_id).in_(ids)).group_by(CheckRun.user_id)).all())
    xp = dict(session.exec(select(UserProfile.user_id, UserProfile.xp_total).where(col(UserProfile.user_id).in_(ids))).all())
    return [LearnerRow(id=u.id, username=u.username, joined=u.created_at, is_admin=u.is_admin, labs=labs.get(u.id, 0),
                       xp=xp.get(u.id, 0), checks=checks.get(u.id, 0), last_active=active.get(u.id),
                       lab_limit=u.lab_limit) for u in users]


class SpendDay(BaseModel):
    day: str
    requests: int
    tokens: int
    cost_usd: float


class SpendBy(BaseModel):
    name: str
    requests: int
    tokens: int
    cost_usd: float


class Spend(BaseModel):
    days: list[SpendDay]
    by_model: list[SpendBy]
    top_learners: list[SpendBy]


def ai_spend(session: Session, days: int = 30) -> Spend:
    start = utcnow() - timedelta(days=days)
    rows = session.exec(select(LlmRequest.created_at, LlmRequest.model, LlmRequest.user_id, LlmRequest.prompt_tokens,
                               LlmRequest.completion_tokens, LlmRequest.cost_usd).where(LlmRequest.created_at >= start)).all()
    per_day: defaultdict[str, list[float]] = defaultdict(lambda: [0, 0, 0.0])
    per_model: defaultdict[str, list[float]] = defaultdict(lambda: [0, 0, 0.0])
    per_user: defaultdict[int, list[float]] = defaultdict(lambda: [0, 0, 0.0])
    for at, model, user_id, p, c, cost in rows:
        for bucket in (per_day[at.date().isoformat()], per_model[model], per_user[user_id]):
            bucket[0] += 1
            bucket[1] += p + c
            bucket[2] += cost
    names = dict(session.exec(select(User.id, User.username).where(col(User.id).in_(list(per_user) or [0]))).all())
    by = lambda items: [SpendBy(name=str(k), requests=int(v[0]), tokens=int(v[1]), cost_usd=round(v[2], 4)) for k, v in items]  # noqa: E731
    return Spend(
        days=[SpendDay(day=d, requests=int(v[0]), tokens=int(v[1]), cost_usd=round(v[2], 4)) for d, v in sorted(per_day.items())],
        by_model=sorted(by(per_model.items()), key=lambda r: -r.tokens),
        top_learners=sorted(by((names.get(u, f"#{u}"), v) for u, v in per_user.items()), key=lambda r: -r.tokens)[:10],
    )
