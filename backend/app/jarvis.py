"""Jarvis, each learner's realtime voice assistant (owner, 28 November: "the ultimate context abled jarvis").

The browser talks to OpenAI's realtime model directly over WebRTC (speech in, speech out, interruptible). This module
decides who may talk and for how long, builds what Jarvis knows about the learner (the session's instructions), mints
the short-lived pass the browser connects with (the real key never leaves the server), runs the tools Jarvis may call
(read-only: the lesson step, the task, the learner's code, their last check, their progress), and turns the usage
OpenAI reports after each reply into a cost, so the daily and monthly budgets hold.

Who: Pro learners (user.plan == "pro", and admins) talk up to JARVIS_PRO_DAILY_MINUTES a day. A free learner gets one
trial of JARVIS_TRIAL_MINUTES, once per account, at most JARVIS_TRIALS_PER_DAY trials a day across the site. When the
day's or the month's budget is spent, nobody starts a new conversation and running ones are asked to end.

Solutions stay safe the same way as the tutor's: the rules say never to give a solution line, and no tool ever returns
the reference solution. (A spoken reply cannot be filtered before it is heard, so the rules matter more here.)
"""
import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, col, func, select

from . import engagement, progress, tutor
from .config import get_settings
from .labs import LabConfig, all_labs, get_lab
from .models import Certificate, ChapterProgress, CheckRun, JarvisSession, SiteSetting, TaskProgress, User, UserProfile, Workspace, utcnow

log = logging.getLogger("labbox.jarvis")

CLIENT_SECRETS_URL = "https://api.openai.com/v1/realtime/client_secrets"
HANGUP_URL = "https://api.openai.com/v1/realtime/calls/{call_id}/hangup"

# Site settings an admin may change (Admin, Jarvis); the defaults come from config.
SETTING_KEYS = {
    "jarvis_daily_usd": "JARVIS_DAILY_BUDGET_USD",
    "jarvis_monthly_usd": "JARVIS_MONTHLY_BUDGET_USD",
    "jarvis_pro_minutes": "JARVIS_PRO_DAILY_MINUTES",
    "jarvis_trial_minutes": "JARVIS_TRIAL_MINUTES",
    "jarvis_trials_per_day": "JARVIS_TRIALS_PER_DAY",
}

PERSONA = """You are Jarvis, the personal assistant of one learner on LabBox, a site of hands-on coding labs (each lab
runs on the learner's own small machine in the browser, with an editor, a terminal and hidden checks behind a Check
button). You speak with the learner out loud, in real time.

How you speak:
- Calm, warm, quick and quietly witty, like a brilliant, polite butler who also happens to be a senior engineer.
  Composed when things break. Never gushing, never robotic.
- Short spoken turns: one to three sentences, then let them talk. This is a conversation, not a lecture.
- Use the learner's first name now and then, not every sentence. Do not call them sir or madam.
- Speak English with a refined British accent. If the learner speaks Hindi or Hinglish, answer in the same language.
- Plain words. Explain a technical term the first time you use it. Never read long code aloud; name the file and the
  line to look at instead.

How you help:
- Teach by guiding: point to one thing to look at, then ask one question that helps them find it themselves.
- Never give away the solution to a task: no complete solution line, no full fixed code, no exact command that
  solves it. You may explain any concept in full, with small examples that are not the task's answer.
- Use your tools before you guess: what the current lesson step says, what the task asks, what is in their files, what
  their last check printed, how far they are in their labs. Never invent their code or a check result.
- If they ask about something outside programming and learning, help briefly and kindly, then steer back.
- Celebrate real progress honestly and briefly.

When the conversation starts, you speak first: greet them by name in one or two sentences, using what you know (where
they are, what they did last), and offer help with what is in front of them. Do not list everything you know.
"""


# ---------- settings and limits ----------

def setting(session: Session, key: str) -> float:
    row = session.get(SiteSetting, key)
    default = float(getattr(get_settings(), SETTING_KEYS[key]))
    if row is None or row.value == "":
        return default
    try:
        return float(row.value)
    except ValueError:
        return default


def set_settings(session: Session, values: dict[str, float], admin_id: int | None) -> None:
    for key, value in values.items():
        if key not in SETTING_KEYS:
            continue
        row = session.get(SiteSetting, key) or SiteSetting(key=key)
        row.value = str(value)
        row.updated_at = utcnow()
        row.updated_by = admin_id
        session.add(row)
    session.commit()


def is_pro(user: User) -> bool:
    return user.is_admin or user.plan == "pro"


def _day_start(now: datetime) -> datetime:
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _month_start(now: datetime) -> datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def spent_usd(session: Session, since: datetime) -> float:
    return float(session.exec(select(func.coalesce(func.sum(JarvisSession.cost_usd), 0.0)).where(JarvisSession.started_at >= since)).one())


def seconds_used(session: Session, user_id: int, since: datetime, kind: str | None = None) -> int:
    q = select(func.coalesce(func.sum(JarvisSession.seconds), 0)).where(JarvisSession.user_id == user_id, JarvisSession.started_at >= since)
    if kind:
        q = q.where(JarvisSession.kind == kind)
    return int(session.exec(q).one())


def trial_used(session: Session, user_id: int) -> bool:
    return session.exec(select(JarvisSession.id).where(JarvisSession.user_id == user_id, JarvisSession.kind == "trial").limit(1)).first() is not None


def trials_today(session: Session, now: datetime) -> int:
    return int(session.exec(select(func.count()).select_from(JarvisSession).where(JarvisSession.kind == "trial", JarvisSession.started_at >= _day_start(now))).one())


class Status(BaseModel):
    enabled: bool
    plan: str  # "free" or "pro"
    kind: str  # what a new conversation would be: "pro", "trial", or "locked"
    reason: str = ""  # why it is locked, in a sentence the page can show
    seconds_left: int = 0  # for this conversation
    trial_used: bool = False
    mode: str = "tap"  # the learner's setting: "tap", "first" (Pro) or "off"
    note_seen: bool = False  # they read what Jarvis can see
    memories: int = 0  # notes Jarvis keeps from earlier conversations (Pro)


def status(session: Session, user: User, now: datetime | None = None) -> Status:
    now = now or utcnow()
    s = get_settings()
    plan = "pro" if is_pro(user) else "free"
    used_trial = trial_used(session, user.id)
    memories = int(session.exec(select(func.count()).select_from(JarvisSession)
                                .where(JarvisSession.user_id == user.id, col(JarvisSession.summary).is_not(None))).one())
    base = {"enabled": s.JARVIS_ENABLED, "plan": plan, "trial_used": used_trial, "mode": user.jarvis_mode or "tap",
            "note_seen": bool(user.jarvis_note_seen), "memories": memories}
    if not s.JARVIS_ENABLED or (s.JARVIS_PROVIDER == "openai" and not s.OPENAI_API_KEY):
        return Status(**base, kind="locked", reason="Jarvis is resting at the moment.")
    if spent_usd(session, _month_start(now)) >= setting(session, "jarvis_monthly_usd") or \
            spent_usd(session, _day_start(now)) >= setting(session, "jarvis_daily_usd"):
        return Status(**base, kind="locked", reason="Jarvis has talked a lot today and is off duty until tomorrow.")
    if plan == "pro":
        left = int(setting(session, "jarvis_pro_minutes") * 60) - seconds_used(session, user.id, _day_start(now))
        if left <= 0:
            return Status(**base, kind="locked", reason="You have used today's Jarvis minutes. They come back tomorrow.")
        return Status(**base, kind="pro", seconds_left=left)
    if used_trial:
        return Status(**base, kind="locked", reason="Talking with Jarvis is part of Pro.")
    if trials_today(session, now) >= setting(session, "jarvis_trials_per_day"):
        return Status(**base, kind="locked", reason="Today's free Jarvis trials are taken. Try again tomorrow.")
    return Status(**base, kind="trial", seconds_left=int(setting(session, "jarvis_trial_minutes") * 60))


# ---------- what Jarvis knows ----------

def _safe_lab(lab_id: str | None) -> LabConfig | None:
    if not lab_id:
        return None
    try:
        return get_lab(lab_id)
    except Exception:
        return None


def _chapter_number(lab: LabConfig, chapter_id: str) -> int:
    ids = [c.id for c in lab.chapters]
    first = 0 if lab.chapters and (lab.chapters[0].folder or lab.chapters[0].id).startswith("00") else 1
    return ids.index(chapter_id) + first if chapter_id in ids else 0


def goal_title(goal_id: str | None) -> str | None:
    """The onboarding goal's title ("Get a backend job"), from its id ("backend-job")."""
    if not goal_id:
        return None
    try:
        from .content import get_content
        ob = get_content().onboarding
        return next((g.title for g in (ob.goals if ob else []) if g.id == goal_id), goal_id)
    except Exception:
        return goal_id


def _local_time(profile: UserProfile, now: datetime) -> str:
    local = now.replace(tzinfo=timezone.utc).astimezone(engagement.tz_or_default(profile.timezone))
    part = "morning" if 5 <= local.hour < 12 else "afternoon" if local.hour < 17 else "evening" if local.hour < 22 else "night"
    return f"{local:%A, %d %B %Y, %H:%M} ({part}, {profile.timezone or 'Asia/Kolkata, assumed'})"


def _failed_recently(session: Session, user_id: int, since: datetime) -> list[str]:
    """Tasks failed at least twice in recent checks and not passed since: where they have been stuck."""
    passed = {(t.lab_id, t.task_id) for t in session.exec(select(TaskProgress).where(TaskProgress.user_id == user_id, TaskProgress.passed)).all()}
    fails: dict[tuple[str, str], int] = {}
    for run in session.exec(select(CheckRun).where(CheckRun.user_id == user_id, CheckRun.created_at >= since).order_by(col(CheckRun.id).desc()).limit(60)).all():
        for r in json.loads(run.results_json or "[]"):
            key = (run.lab_id, r.get("task", ""))
            if not r.get("passed") and key not in passed:
                fails[key] = fails.get(key, 0) + 1
    out = []
    for (lab_id, task_id), n in sorted(fails.items(), key=lambda x: -x[1])[:5]:
        if n < 2:
            continue
        lab = _safe_lab(lab_id)
        title = next((t.title for c in lab.chapters for t in c.tasks if t.id == task_id), task_id) if lab else task_id
        out.append(f"{lab.title if lab else lab_id}: \"{title}\" (failed {n} checks recently, not passed yet)")
    return out


def learner_context(session: Session, user: User, lab_id: str | None, chapter_id: str | None, step: int | None,
                    now: datetime | None = None) -> str:
    """Everything Jarvis should know when the conversation starts, in plain text (kept short: it is sent with every
    turn, though OpenAI bills the repeated part at the cheaper cached rate)."""
    now = now or utcnow()
    profile = engagement.get_profile(session, user.id)
    name = profile.display_name or profile.certificate_name or user.username
    lines = [
        f"Learner: {name} (username {user.username}); plan: {'Pro' if is_pro(user) else 'Free trial'}.",
        f"Their local time: {_local_time(profile, now)}.",
        f"Member since {user.created_at:%d %B %Y} ({(now - user.created_at).days} days).",
    ]
    if profile.goal:
        lines.append(f"Their goal, from sign-up: {goal_title(profile.goal)}.")
    if profile.placement_level:
        lines.append(f"Their level, from sign-up: {profile.placement_level}.")
    lines.append(f"Progress: level {profile.level}, {profile.xp_total} XP, a {profile.streak_current}-day streak (best {profile.streak_best}).")

    # Labs they have started, most recent first.
    chapters = session.exec(select(ChapterProgress).where(ChapterProgress.user_id == user.id).order_by(col(ChapterProgress.updated_at).desc())).all()
    passed = session.exec(select(TaskProgress).where(TaskProgress.user_id == user.id, TaskProgress.passed)).all()
    by_lab: dict[str, int] = {}
    for t in passed:
        by_lab[t.lab_id] = by_lab.get(t.lab_id, 0) + 1
    seen: list[str] = []
    for cp in chapters:
        if cp.lab_id not in seen:
            seen.append(cp.lab_id)
    labs_lines = []
    for lid in seen[:6]:
        lab = _safe_lab(lid)
        if not lab:
            continue
        last = next(cp for cp in chapters if cp.lab_id == lid)
        ch = next((c for c in lab.chapters if c.id == last.chapter_id), None)
        labs_lines.append(f"- {lab.title}: {by_lab.get(lid, 0)} of {lab.task_count} tasks passed; last opened chapter "
                          f"{_chapter_number(lab, last.chapter_id)} \"{ch.title if ch else last.chapter_id}\" on {last.updated_at:%d %b}")
    lines.append("Labs they have started:\n" + ("\n".join(labs_lines) if labs_lines else "- none yet: they are new here."))

    certs = session.exec(select(Certificate).where(Certificate.user_id == user.id)).all()
    if certs:
        lines.append("Certificates earned: " + ", ".join((_safe_lab(c.lab_id).title if _safe_lab(c.lab_id) else c.lab_id) for c in certs) + ".")
    stuck = _failed_recently(session, user.id, now - timedelta(days=7))
    if stuck:
        lines.append("Where they have struggled this week:\n" + "\n".join(f"- {s}" for s in stuck))

    if is_pro(user):
        memories = session.exec(select(JarvisSession).where(JarvisSession.user_id == user.id, col(JarvisSession.summary).is_not(None))
                                .order_by(col(JarvisSession.id).desc()).limit(MEMORY_COUNT)).all()
        if memories:
            lines.append("What you remember from your earlier conversations with them (newest first):\n"
                         + "\n".join(f"- {m.started_at:%d %b}: {m.summary}" for m in memories))

    lab = _safe_lab(lab_id)
    if lab:
        here = [f"Right now they are in the lab \"{lab.title}\"."]
        ch = next((c for c in lab.chapters if c.id == chapter_id), None)
        if ch:
            steps = lab.chapter_steps(ch.id)
            here.append(f"Chapter {_chapter_number(lab, ch.id)}: \"{ch.title}\" ({len(steps)} steps).")
            if step is not None and 0 <= step < len(steps):
                st = steps[step]
                here.append(f"They are on step {step + 1}: a {st.type} step titled \"{st.title or ''}\".")
                if st.task:
                    tp = progress.task_progress(session, user.id, lab.id, ch.id, st.task)
                    here.append(f"This step's task is \"{lab.task(ch.id, st.task).title}\" (id {st.task}): "
                                f"{'passed' if tp.passed else 'not passed yet'}, {tp.hints_used} hints used.")
        lines.append(" ".join(here))
    else:
        lines.append("Right now they are not inside a lab (on the dashboard or another page).")
    return "\n".join(lines)


def instructions(session: Session, user: User, lab_id: str | None, chapter_id: str | None, step: int | None, help_reason: str = "") -> str:
    text = PERSONA + "\n\nWhat you know about this learner right now:\n" + learner_context(session, user, lab_id, chapter_id, step)
    if help_reason.startswith(("WELCOME:", "CHEER:")):
        text += "\n\nWhy this conversation started: " + help_reason.split(":", 1)[1].strip()
    elif help_reason:
        text += ("\n\nWhy this conversation started: you noticed they might be stuck and offered help, and they accepted. "
                 + help_reason + " Open by acknowledging it in one short, kind sentence, then ask what they have tried.")
    return text


# ---------- tools ----------

TOOLS = [
    {"type": "function", "name": "get_current_step",
     "description": "The text of the lesson step the learner is reading right now, as markdown.",
     "parameters": {"type": "object", "properties": {}}},
    {"type": "function", "name": "get_task",
     "description": "What the task on the current step asks, and the hints the learner has already seen.",
     "parameters": {"type": "object", "properties": {}}},
    {"type": "function", "name": "get_my_code",
     "description": "The learner's current files for this chapter (their own work, not the solution).",
     "parameters": {"type": "object", "properties": {}}},
    {"type": "function", "name": "get_last_check",
     "description": "What the last press of Check said for the current task: passed or not, the message, expected and actual values, and the output.",
     "parameters": {"type": "object", "properties": {}}},
    {"type": "function", "name": "get_progress",
     "description": "The learner's progress in every lab they have started, and the labs LabBox offers.",
     "parameters": {"type": "object", "properties": {}}},
]


def _current(session: Session, js: JarvisSession, step: int | None):
    lab = _safe_lab(js.lab_id)
    if not lab or not js.chapter_id:
        return lab, None, None
    steps = lab.chapter_steps(js.chapter_id)
    if step is None:
        step = progress.chapter_progress(session, js.user_id, lab.id, js.chapter_id).current_step
    return lab, steps, (steps[step] if 0 <= step < len(steps) else None)


def run_tool(session: Session, user: User, js: JarvisSession, name: str, step: int | None) -> str:
    """Read-only answers for Jarvis's tools. Nothing here returns the reference solution."""
    lab, steps, st = _current(session, js, step)
    if name == "get_progress":
        others = ", ".join(f"{lab_.title} ({len(lab_.chapters)} chapters)" for lab_ in all_labs())
        return learner_context(session, user, js.lab_id, js.chapter_id, step).split("Right now")[0] + f"\nLabs on LabBox: {others}."
    if not lab or not js.chapter_id:
        return "They are not inside a lab right now, so there is no lesson, task or code to look at."
    if name == "get_current_step":
        return f"Step \"{st.title or ''}\" ({st.type}):\n{st.markdown[:6000]}" if st else "(no current step)"
    task_id = st.task if st and st.task else None
    if name == "get_task":
        if not task_id:
            return "The current step has no task. It is a reading or practice step."
        task = lab.task(js.chapter_id, task_id)
        used = progress.hints_used(session, user.id, lab.id).get(task_id, 0)
        hints = "\n".join(f"- {h}" for h in task.hints[:used]) or "(none yet)"
        return f"Task \"{task.title}\":\n{tutor.task_text(lab, js.chapter_id, task_id)[:6000]}\n\nHints they have already seen:\n{hints}"
    if name == "get_my_code":
        ws = session.exec(select(Workspace).where(Workspace.user_id == user.id, Workspace.lab_id == lab.id)).first()
        return tutor.learner_files(lab, ws, js.chapter_id)
    if name == "get_last_check":
        if not task_id:
            return "The current step has no task, so there is no check for it."
        return tutor.last_check(session, user.id, lab, task_id)
    return f"Unknown tool {name}."


# ---------- noticing when a learner is stuck (step 2) ----------

MEMORY_COUNT = 3  # earlier conversations' summaries given to a new one (Pro)
SUMMARY_MAX = 600  # characters kept from one summary

FAILS_TO_NUDGE = 3  # the same task failing this many checks in a row, without a pass
IDLE_TO_NUDGE = 8 * 60  # seconds on one task step without pressing Check


class Nudge(BaseModel):
    nudge: bool
    reason: str = ""  # "fails", "hints" or "idle": why Jarvis offers help
    task_id: str | None = None
    line: str = ""  # what the orb says, in a sentence
    detail: str = ""  # what Jarvis is told when the learner accepts (added to his instructions)


def _fail_streak(session: Session, user_id: int, lab_id: str, chapter_id: str, task_id: str) -> tuple[int, str]:
    """How many of the latest checks of this chapter failed this task in a row, and the last failure message."""
    n, message = 0, ""
    runs = session.exec(select(CheckRun).where(CheckRun.user_id == user_id, CheckRun.lab_id == lab_id, CheckRun.chapter_id == chapter_id)
                        .order_by(col(CheckRun.id).desc()).limit(10)).all()
    for run in runs:
        r = next((x for x in json.loads(run.results_json or "[]") if x.get("task") == task_id), None)
        if r is None:
            continue
        if r.get("passed"):
            break
        n += 1
        message = message or str(r.get("message") or "")
    return n, message


def nudge(session: Session, user: User, lab_id: str | None, chapter_id: str | None, step: int | None, idle_seconds: int = 0) -> Nudge:
    """Rules, not a model (so it costs nothing): the same check failing again and again, every hint used, or a long
    pause on a task. Only on a task step whose task is not passed yet."""
    lab = _safe_lab(lab_id)
    if user.jarvis_mode == "off" or not lab or not chapter_id or step is None or not any(c.id == chapter_id for c in lab.chapters):
        return Nudge(nudge=False)
    steps = lab.chapter_steps(chapter_id)
    st = steps[step] if 0 <= step < len(steps) else None
    if not st or not st.task:
        return Nudge(nudge=False)
    tp = session.get(TaskProgress, (user.id, lab.id, st.task))  # read only: asking never creates a row
    if tp is not None and tp.passed:
        return Nudge(nudge=False)
    hints_used = tp.hints_used if tp else 0
    task = lab.task(chapter_id, st.task)
    first = (engagement.get_profile(session, user.id).display_name or user.username).split()[0]
    fails, message = _fail_streak(session, user.id, lab.id, chapter_id, st.task)
    if fails >= FAILS_TO_NUDGE:
        return Nudge(nudge=True, reason="fails", task_id=st.task,
                     line=f"{first}, \"{task.title}\" has failed {fails} checks in a row. Want to go through it together?",
                     detail=f"They asked for help because the task \"{task.title}\" failed {fails} checks in a row. "
                            f"The last check said: {message[:300]}")
    if task.hints and hints_used >= len(task.hints):
        return Nudge(nudge=True, reason="hints", task_id=st.task,
                     line=f"You have used every hint on \"{task.title}\". Shall we look at it together?",
                     detail=f"They asked for help after using all {len(task.hints)} hints on the task \"{task.title}\".")
    if idle_seconds >= IDLE_TO_NUDGE and fails == 0:
        mins = idle_seconds // 60
        return Nudge(nudge=True, reason="idle", task_id=st.task,
                     line=f"You have been on \"{task.title}\" for {mins} minutes. Need a hand getting started?",
                     detail=f"They asked for help after {mins} minutes on the task \"{task.title}\" without pressing Check yet.")
    return Nudge(nudge=False)


# ---------- welcome on sign-up and on return (step 3) ----------

AWAY_TO_WELCOME = timedelta(hours=6)  # away this long: "welcome back"


class Welcome(BaseModel):
    show: bool
    kind: str = ""  # "new" (nothing started yet) or "back"
    line: str = ""  # what the orb says
    continue_url: str | None = None  # where they left off
    continue_label: str = ""
    detail: str = ""  # for Jarvis, when they tap Talk: why the conversation started


def welcome(session: Session, user: User, now: datetime | None = None, force: bool = False) -> Welcome:
    """A new learner (no lab opened yet) or one back after AWAY_TO_WELCOME. The dashboard asks once per browser
    session. Text for everyone; the voice greeting is one tap away for Pro and trial learners."""
    now = now or utcnow()
    if user.jarvis_mode == "off" and not force:
        return Welcome(show=False)
    profile = engagement.get_profile(session, user.id)
    first = (profile.display_name or user.username).split()[0]
    last = session.exec(select(ChapterProgress).where(ChapterProgress.user_id == user.id).order_by(col(ChapterProgress.updated_at).desc()).limit(1)).first()
    if last is None:
        goal = f" Your goal: {goal_title(profile.goal)}." if profile.goal else ""
        return Welcome(show=True, kind="new", line=f"Welcome to LabBox, {first}.{goal} Shall I help you pick your first lab?",
                       detail=("WELCOME: they are new to LabBox and have not opened a lab yet. Welcome them warmly by name in one "
                               "or two sentences, then ask one question about what they want to learn, and suggest one lab "
                               "that fits. Use get_progress to see the labs on offer."))
    if not force and now - last.updated_at < AWAY_TO_WELCOME:
        return Welcome(show=False)
    lab = _safe_lab(last.lab_id)
    if not lab:
        return Welcome(show=False)
    ch = next((c for c in lab.chapters if c.id == last.chapter_id), None)
    num = _chapter_number(lab, last.chapter_id)
    days = (now - last.updated_at).days
    when = "today" if days == 0 else "yesterday" if days == 1 else f"{days} days ago"
    where = f"chapter {num}, \"{ch.title}\"" if ch else "your last chapter"
    return Welcome(show=True, kind="back",
                   line=f"Welcome back, {first}. You were in {lab.title}, {where}, {when}. Shall we pick up there?",
                   continue_url=f"/labs/{lab.id}?chapter={last.chapter_id}", continue_label=f"Continue {lab.title}",
                   detail=(f"WELCOME: they are back after {when if days else 'a few hours'}; they were last in {lab.title}, {where}. "
                           "Welcome them back by name in one or two sentences, remind them where they stopped (and what you "
                           "remember, if anything), and ask whether they want to pick up there."))


# ---------- celebrations (step 4) ----------

CHEER_WINDOW = timedelta(minutes=3)  # a chapter or first task done this recently is news
CERT_WINDOW = timedelta(minutes=10)  # a certificate may wait for the learner to type their name first
CHEER_TALK_WINDOW = timedelta(minutes=30)  # tapping Talk on a cheer a little later still works


class Cheer(BaseModel):
    show: bool
    kind: str = ""  # "lab" (certificate), "chapter" or "first" (the learner's first task ever)
    key: str = ""  # the page shows each cheer once
    line: str = ""
    link_url: str | None = None
    link_label: str = ""
    detail: str = ""  # for Jarvis, when they tap Talk


def cheer(session: Session, user: User, lab_id: str | None, chapter_id: str | None, now: datetime | None = None,
          window: timedelta | None = None) -> Cheer:
    """Something worth celebrating just happened in this lab: the lab finished (its certificate), the chapter finished,
    or the learner's first task ever passed. Rules, no model; the lab page asks after every check."""
    now = now or utcnow()
    lab = _safe_lab(lab_id)
    if user.jarvis_mode == "off" or not lab or not any(c.id == chapter_id for c in lab.chapters):
        return Cheer(show=False)
    first = (engagement.get_profile(session, user.id).display_name or user.username).split()[0]
    cert = session.exec(select(Certificate).where(Certificate.user_id == user.id, Certificate.lab_id == lab.id)).first()
    if cert and now - cert.issued_at < (window or CERT_WINDOW):
        return Cheer(show=True, kind="lab", key=f"lab:{lab.id}",
                     line=f"{first}, you finished {lab.title}: {cert.tasks_passed} of {cert.tasks_total} tasks. Your certificate is ready.",
                     link_url=f"/c/{cert.id}", link_label="See your certificate",
                     detail=(f"CHEER: they just finished the lab {lab.title} ({cert.tasks_passed} of {cert.tasks_total} tasks) "
                             "and earned its certificate. Congratulate them warmly in two sentences, name the biggest thing "
                             "they can now do, and ask what they want to learn next."))
    chapter = next(c for c in lab.chapters if c.id == chapter_id)
    cp = session.get(ChapterProgress, (user.id, lab.id, chapter_id))
    if cp and cp.completed_at and now - cp.completed_at < (window or CHEER_WINDOW):
        num = _chapter_number(lab, chapter_id)
        i = [c.id for c in lab.chapters].index(chapter_id)
        nxt = lab.chapters[i + 1] if i + 1 < len(lab.chapters) else None
        line = f"Chapter {num} done, {first}: every task in \"{chapter.title}\" passes."
        if nxt:
            line += f" Next is chapter {num + 1}, \"{nxt.title}\"."
        return Cheer(show=True, kind="chapter", key=f"chapter:{lab.id}:{chapter_id}", line=line,
                     link_url=f"/labs/{lab.id}?chapter={nxt.id}" if nxt else None,
                     link_label=f"Start chapter {num + 1}" if nxt else "",
                     detail=(f"CHEER: they just passed every task in chapter {num} of {lab.title}, \"{chapter.title}\". "
                             "Congratulate them in one or two sentences, say in plain words what they can now do, then ask "
                             "whether they want a quick look at what comes next"
                             + (f" (chapter {num + 1}, \"{nxt.title}\")." if nxt else ".")))
    passed = session.exec(select(TaskProgress).where(TaskProgress.user_id == user.id, TaskProgress.passed == True)  # noqa: E712
                          .limit(2)).all()
    if len(passed) == 1 and passed[0].lab_id == lab.id and passed[0].first_passed_at \
            and now - passed[0].first_passed_at < (window or CHEER_WINDOW):
        task = lab.task(passed[0].chapter_id, passed[0].task_id)
        return Cheer(show=True, kind="first", key="first",
                     line=f"Your first task passes, {first}: \"{task.title}\". Code you wrote, checked by a real test.",
                     detail=(f"CHEER: their very first task on LabBox just passed (\"{task.title}\" in {lab.title}). "
                             "Congratulate them in one or two sentences and tell them that every task works this way: "
                             "write the code, press Check, a real test decides."))
    return Cheer(show=False)


MODES = ("tap", "first", "off")


def set_learner_settings(session: Session, user: User, mode: str | None = None, note_seen: bool | None = None) -> None:
    if mode is not None:
        user.jarvis_mode = mode
    if note_seen is not None:
        user.jarvis_note_seen = note_seen
    session.add(user)
    session.commit()
    session.refresh(user)


def forget(session: Session, user: User) -> int:
    """The learner asked Jarvis to forget: every note he kept from their conversations goes (the conversations' length
    and cost stay, for the budgets)."""
    rows = session.exec(select(JarvisSession).where(JarvisSession.user_id == user.id, col(JarvisSession.summary).is_not(None))).all()
    for js in rows:
        js.summary = None
        session.add(js)
    session.commit()
    log.info("Jarvis forgot %s notes for %s", len(rows), user.username)
    return len(rows)


# ---------- sessions ----------

class SessionOut(BaseModel):
    session_id: int
    client_secret: str
    expires_at: int
    model: str
    kind: str
    max_seconds: int


async def mint_secret(instructions_text: str) -> tuple[str, int]:
    """A short-lived pass for one WebRTC call, with Jarvis's instructions, voice and tools baked in."""
    s = get_settings()
    if s.JARVIS_PROVIDER == "fake":
        return "ek_fake_for_tests", int(datetime.now(timezone.utc).timestamp()) + 60
    body = {
        "expires_after": {"anchor": "created_at", "seconds": 120},
        "session": {
            "type": "realtime",
            "model": s.JARVIS_MODEL,
            "instructions": instructions_text,
            "audio": {
                "input": {"turn_detection": {"type": "semantic_vad", "eagerness": "medium"}},
                "output": {"voice": s.JARVIS_VOICE},
            },
            "tools": TOOLS,
            "tool_choice": "auto",
            "max_output_tokens": 1200,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(CLIENT_SECRETS_URL, headers={"Authorization": f"Bearer {s.OPENAI_API_KEY}"}, json=body)
    except httpx.HTTPError as e:
        log.warning("Jarvis could not reach OpenAI: %s", e)
        raise HTTPException(503, "Jarvis could not reach his voice just now. Try again in a moment.")
    if r.status_code != 200:
        log.warning("Jarvis client secret failed: %s %s", r.status_code, r.text[:300])
        raise HTTPException(503, "Jarvis could not start a conversation just now. Try again in a moment.")
    data = r.json()
    return data["value"], int(data.get("expires_at") or 0)


async def start(session: Session, user: User, lab_id: str | None, chapter_id: str | None, step: int | None, reason: str | None = None) -> SessionOut:
    st = status(session, user)
    if st.kind == "locked":
        raise HTTPException(403, st.reason)
    lab = _safe_lab(lab_id)
    chapter = chapter_id if lab and any(c.id == chapter_id for c in lab.chapters) else None
    help_reason = ""
    if reason == "welcome":
        w = welcome(session, user, force=True)
        help_reason = w.detail
    elif reason == "cheer" and lab and chapter:
        c = cheer(session, user, lab.id, chapter, window=CHEER_TALK_WINDOW)
        help_reason = c.detail if c.show else ""
    elif reason and lab and chapter:
        n = nudge(session, user, lab.id, chapter, step, idle_seconds=IDLE_TO_NUDGE if reason == "idle" else 0)
        help_reason = n.detail if n.nudge else ""
    secret, expires = await mint_secret(instructions(session, user, lab.id if lab else None, chapter, step, help_reason))
    js = JarvisSession(user_id=user.id, kind=st.kind, lab_id=lab.id if lab else None, chapter_id=chapter, max_seconds=st.seconds_left)
    session.add(js)
    session.commit()
    session.refresh(js)
    log.info("Jarvis %s conversation %s for %s (%s s at most)", st.kind, js.id, user.username, st.seconds_left)
    return SessionOut(session_id=js.id, client_secret=secret, expires_at=expires, model=get_settings().JARVIS_MODEL,
                      kind=st.kind, max_seconds=st.seconds_left)


def own_session(session: Session, user: User, session_id: int) -> JarvisSession:
    js = session.get(JarvisSession, session_id)
    if js is None or js.user_id != user.id:
        raise HTTPException(404, "No such conversation")
    return js


class Usage(BaseModel):
    """What OpenAI reported in one response.done event (usage), as the browser received it."""
    audio_in: int = 0
    audio_cached: int = 0
    text_in: int = 0
    text_cached: int = 0
    audio_out: int = 0
    text_out: int = 0


def usage_from_event(u: dict) -> Usage:
    """OpenAI's usage object to our counts. Cached tokens are billed apart from the uncached ones."""
    inp, out = u.get("input_token_details") or {}, u.get("output_token_details") or {}
    cached = inp.get("cached_tokens_details") or {}
    audio_cached, text_cached = int(cached.get("audio_tokens") or 0), int(cached.get("text_tokens") or 0)
    return Usage(audio_in=max(0, int(inp.get("audio_tokens") or 0) - audio_cached), audio_cached=audio_cached,
                 text_in=max(0, int(inp.get("text_tokens") or 0) - text_cached), text_cached=text_cached,
                 audio_out=int(out.get("audio_tokens") or 0), text_out=int(out.get("text_tokens") or 0))


def cost(u: Usage) -> float:
    s = get_settings()
    return (u.audio_in * s.JARVIS_PRICE_AUDIO_IN + u.audio_cached * s.JARVIS_PRICE_AUDIO_CACHED + u.text_in * s.JARVIS_PRICE_TEXT_IN
            + u.text_cached * s.JARVIS_PRICE_TEXT_CACHED + u.audio_out * s.JARVIS_PRICE_AUDIO_OUT + u.text_out * s.JARVIS_PRICE_TEXT_OUT) / 1_000_000


class Heartbeat(BaseModel):
    seconds: int = 0  # how long the conversation has run, by the browser's clock
    usage: list[dict] = []  # response.done usage objects since the last heartbeat
    call_id: str | None = None
    ended: bool = False
    summary: str | None = None  # Jarvis's own note on the conversation, written at the end (step 3)


class HeartbeatOut(BaseModel):
    stop: bool
    reason: str = ""
    seconds_left: int
    cost_usd: float


async def heartbeat(session: Session, user: User, session_id: int, hb: Heartbeat) -> HeartbeatOut:
    js = own_session(session, user, session_id)
    now = utcnow()
    # The browser's clock, but never less than the wall clock since the last heartbeat allows to skip.
    js.seconds = max(js.seconds, min(hb.seconds, int((now - js.started_at).total_seconds()) + 5))
    for raw in hb.usage[:50]:
        u = usage_from_event(raw)
        js.audio_in_tokens += u.audio_in
        js.audio_cached_tokens += u.audio_cached
        js.text_in_tokens += u.text_in
        js.text_cached_tokens += u.text_cached
        js.audio_out_tokens += u.audio_out
        js.text_out_tokens += u.text_out
        js.cost_usd += cost(u)
    if hb.call_id and not js.call_id:
        js.call_id = hb.call_id[:80]
    if hb.summary and hb.summary.strip():
        js.summary = hb.summary.strip()[:SUMMARY_MAX]
    js.last_seen_at = now
    if hb.ended and js.ended_at is None:
        js.ended_at = now
    session.add(js)
    session.commit()
    left = js.max_seconds - js.seconds
    reason = ""
    if left <= 0:
        reason = "That is all the time we have for now." if js.kind == "pro" else "That was your free trial with Jarvis."
    elif spent_usd(session, _day_start(now)) >= setting(session, "jarvis_daily_usd") or \
            spent_usd(session, _month_start(now)) >= setting(session, "jarvis_monthly_usd"):
        reason = "Jarvis has reached today's budget and must go off duty."
    stop = bool(reason) and not hb.ended
    if stop and js.call_id:
        await hangup(js.call_id)
    return HeartbeatOut(stop=bool(reason), reason=reason, seconds_left=max(0, left), cost_usd=round(js.cost_usd, 4))


async def hangup(call_id: str) -> None:
    """Ends a call from the server side, so a limit holds even if the browser does not stop."""
    s = get_settings()
    if s.JARVIS_PROVIDER == "fake":
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(HANGUP_URL.format(call_id=call_id), headers={"Authorization": f"Bearer {s.OPENAI_API_KEY}"})
    except httpx.HTTPError as e:
        log.warning("Jarvis hangup of %s failed: %s", call_id, e)


# ---------- the admin view ----------

class AdminSummary(BaseModel):
    today_usd: float
    month_usd: float
    today_sessions: int
    today_minutes: float
    trials_today: int
    pro_learners: int
    cost_per_minute_usd: float | None  # measured over the month
    settings: dict[str, float]
    recent: list[dict]


def admin_summary(session: Session, now: datetime | None = None) -> AdminSummary:
    now = now or utcnow()
    day, month = _day_start(now), _month_start(now)
    today = session.exec(select(JarvisSession).where(JarvisSession.started_at >= day)).all()
    month_rows = session.exec(select(JarvisSession).where(JarvisSession.started_at >= month)).all()
    month_secs = sum(r.seconds for r in month_rows)
    month_cost = sum(r.cost_usd for r in month_rows)
    recent = session.exec(select(JarvisSession, User).join(User, User.id == JarvisSession.user_id)
                          .order_by(col(JarvisSession.id).desc()).limit(20)).all()
    return AdminSummary(
        today_usd=round(sum(r.cost_usd for r in today), 4), month_usd=round(month_cost, 4),
        today_sessions=len(today), today_minutes=round(sum(r.seconds for r in today) / 60, 1),
        trials_today=sum(1 for r in today if r.kind == "trial"),
        pro_learners=int(session.exec(select(func.count()).select_from(User).where(User.plan == "pro")).one()),
        cost_per_minute_usd=round(month_cost / (month_secs / 60), 4) if month_secs >= 30 else None,
        settings={k: setting(session, k) for k in SETTING_KEYS},
        recent=[{"id": js.id, "username": u.username, "kind": js.kind, "lab_id": js.lab_id, "started_at": js.started_at.isoformat(),
                 "seconds": js.seconds, "cost_usd": round(js.cost_usd, 4)} for js, u in recent],
    )
