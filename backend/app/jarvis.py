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


def status(session: Session, user: User, now: datetime | None = None) -> Status:
    now = now or utcnow()
    s = get_settings()
    plan = "pro" if is_pro(user) else "free"
    used_trial = trial_used(session, user.id)
    base = {"enabled": s.JARVIS_ENABLED, "plan": plan, "trial_used": used_trial}
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
        lines.append(f"Their goal, from sign-up: {profile.goal}.")
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


def instructions(session: Session, user: User, lab_id: str | None, chapter_id: str | None, step: int | None) -> str:
    return PERSONA + "\n\nWhat you know about this learner right now:\n" + learner_context(session, user, lab_id, chapter_id, step)


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


async def start(session: Session, user: User, lab_id: str | None, chapter_id: str | None, step: int | None) -> SessionOut:
    st = status(session, user)
    if st.kind == "locked":
        raise HTTPException(403, st.reason)
    lab = _safe_lab(lab_id)
    chapter = chapter_id if lab and any(c.id == chapter_id for c in lab.chapters) else None
    secret, expires = await mint_secret(instructions(session, user, lab.id if lab else None, chapter, step))
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
