"""Jarvis, the learner's realtime voice assistant (owner, 28 November). The fake provider is on (conftest): no test
ever calls OpenAI. Budgets and trial counts are site-wide, so a fixture lifts them for this module and puts the site's
settings back afterwards."""
import random
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import jarvis
from app.db import engine
from app.models import CheckRun, JarvisSession, SiteSetting, User

LAB = "python-basics"


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        with Session(engine) as s:
            before = {k: s.get(SiteSetting, k).value if s.get(SiteSetting, k) else None for k in jarvis.SETTING_KEYS}
            jarvis.set_settings(s, {"jarvis_daily_usd": 1e6, "jarvis_monthly_usd": 1e6, "jarvis_trials_per_day": 1e6}, None)
        yield c
        with Session(engine) as s:
            for k, v in before.items():
                row = s.get(SiteSetting, k)
                if v is None and row is not None:
                    s.delete(row)
                elif v is not None:
                    row.value = v
                    s.add(row)
            s.commit()


def signup(api: TestClient, plan: str = "free", admin: bool = False) -> tuple[dict, int]:
    r = api.post("/api/auth/signup", json={"username": f"jv{random.randint(0, 10**9)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    uid = r.json()["user"]["id"]
    with Session(engine) as s:
        u = s.get(User, uid)
        u.plan, u.is_admin = plan, admin
        s.add(u)
        s.commit()
    return {"Authorization": f"Bearer {r.json()['token']}"}, uid


def start(api, h, **body):
    return api.post("/api/jarvis/session", json={"lab_id": LAB, "chapter_id": "first-program", "step": 0, **body}, headers=h)


def test_a_free_learner_gets_one_trial_then_the_pro_lock(api):
    h, uid = signup(api)
    st = api.get("/api/jarvis/status", headers=h).json()
    assert st["plan"] == "free" and st["kind"] == "trial" and st["seconds_left"] == 180
    r = start(api, h)
    assert r.status_code == 200, r.text
    assert r.json()["kind"] == "trial" and r.json()["client_secret"].startswith("ek_") and r.json()["max_seconds"] == 180
    st = api.get("/api/jarvis/status", headers=h).json()
    assert st["kind"] == "locked" and st["trial_used"] and "Pro" in st["reason"]
    assert start(api, h).status_code == 403


def test_pro_and_admins_talk_up_to_the_daily_minutes(api):
    h, uid = signup(api, plan="pro")
    st = api.get("/api/jarvis/status", headers=h).json()
    assert st["kind"] == "pro" and st["seconds_left"] == 20 * 60
    sid = start(api, h).json()["session_id"]
    out = api.post(f"/api/jarvis/session/{sid}/heartbeat", json={"seconds": 3600}, headers=h).json()
    assert not out["stop"] and out["seconds_left"] > 20 * 60 - 10
    # The browser cannot claim more time than has passed (plus a few seconds).
    with Session(engine) as s:
        js = s.get(JarvisSession, sid)
        js.seconds = 20 * 60
        s.add(js)
        s.commit()
    assert api.get("/api/jarvis/status", headers=h).json()["kind"] == "locked"
    ha, _ = signup(api, admin=True)
    assert api.get("/api/jarvis/status", headers=ha).json()["kind"] == "pro"


def test_the_heartbeat_counts_cost_and_stops_at_the_limit(api):
    h, uid = signup(api, plan="pro")
    sid = start(api, h).json()["session_id"]
    usage = {"input_token_details": {"audio_tokens": 1000, "text_tokens": 2000, "cached_tokens_details": {"text_tokens": 1500, "audio_tokens": 0}},
             "output_token_details": {"audio_tokens": 500, "text_tokens": 50}}
    out = api.post(f"/api/jarvis/session/{sid}/heartbeat", json={"seconds": 3, "usage": [usage]}, headers=h).json()
    # 1000 audio in at $10/M, 500 text in at $0.60/M, 1500 cached text at $0.06/M, 500 audio out at $20/M, 50 text out at $2.40/M
    expected = (1000 * 10 + 500 * 0.6 + 1500 * 0.06 + 500 * 20 + 50 * 2.4) / 1e6
    assert abs(out["cost_usd"] - round(expected, 4)) < 1e-6 and not out["stop"]
    with Session(engine) as s:
        js = s.get(JarvisSession, sid)
        assert (js.audio_in_tokens, js.text_in_tokens, js.text_cached_tokens, js.audio_out_tokens) == (1000, 500, 1500, 500)
        js.max_seconds = 2
        s.add(js)
        s.commit()
    out = api.post(f"/api/jarvis/session/{sid}/heartbeat", json={"seconds": 3}, headers=h).json()
    assert out["stop"] and out["seconds_left"] == 0


def test_the_daily_budget_locks_everyone(api):
    h, uid = signup(api, plan="pro")
    with Session(engine) as s:
        spent = jarvis.spent_usd(s, jarvis._day_start(jarvis.utcnow()))
        jarvis.set_settings(s, {"jarvis_daily_usd": spent}, None)  # already used up
    try:
        st = api.get("/api/jarvis/status", headers=h).json()
        assert st["kind"] == "locked" and "off duty" in st["reason"]
        assert start(api, h).status_code == 403
    finally:
        with Session(engine) as s:
            jarvis.set_settings(s, {"jarvis_daily_usd": 1e6}, None)


def test_jarvis_knows_the_learner_and_where_they_are(api):
    h, uid = signup(api, plan="pro")
    with Session(engine) as s:
        user = s.get(User, uid)
        s.add(CheckRun(user_id=uid, lab_id=LAB, chapter_id="first-program", passed_count=0, total_count=2, output_tail="",
                       duration_ms=10, results_json='[{"task": "print_hello", "passed": false, "message": "x"}]'))
        s.add(CheckRun(user_id=uid, lab_id=LAB, chapter_id="first-program", passed_count=0, total_count=2, output_tail="",
                       duration_ms=10, results_json='[{"task": "print_hello", "passed": false, "message": "x"}]'))
        s.commit()
        text = jarvis.instructions(s, user, LAB, "first-program", 0)
    assert "You are Jarvis" in text and user.username in text
    assert "Python from zero" in text or "python" in text.lower()
    assert "step 1" in text and "Right now they are in the lab" in text


def test_tools_answer_from_the_lesson_and_the_learners_own_work(api):
    h, uid = signup(api, plan="pro")
    sid = start(api, h).json()["session_id"]
    step = api.post(f"/api/jarvis/session/{sid}/tool", json={"name": "get_current_step", "step": 0}, headers=h).json()["output"]
    assert step.startswith("Step ")
    prog = api.post(f"/api/jarvis/session/{sid}/tool", json={"name": "get_progress"}, headers=h).json()["output"]
    assert "Labs on LabBox" in prog
    # Someone else's conversation is not yours.
    h2, _ = signup(api, plan="pro")
    assert api.post(f"/api/jarvis/session/{sid}/tool", json={"name": "get_task"}, headers=h2).status_code == 404


def test_no_tool_ever_returns_a_solution_line(api):
    from app import tutor
    from app.labs import get_lab

    h, uid = signup(api, plan="pro")
    lab = get_lab(LAB)
    secrets = tutor.solution_lines(lab)
    for chapter in lab.chapters[:4]:
        sid = start(api, h, chapter_id=chapter.id).json()["session_id"]
        for i, st in enumerate(lab.chapter_steps(chapter.id)):
            if not st.task:
                continue
            for name in ("get_task", "get_current_step", "get_my_code", "get_last_check"):
                out = api.post(f"/api/jarvis/session/{sid}/tool", json={"name": name, "step": i}, headers=h).json()["output"]
                assert not any(line in tutor._code(out) for line in secrets), (chapter.id, name)


def test_admins_set_plans_and_see_the_spend(api):
    ha, _ = signup(api, admin=True)
    h, uid = signup(api)
    assert api.put(f"/api/admin/learners/{uid}/plan", json={"plan": "pro"}, headers=ha).json() == {"plan": "pro"}
    assert api.get("/api/jarvis/status", headers=h).json()["plan"] == "pro"
    assert api.put(f"/api/admin/learners/{uid}/plan", json={"plan": "gold"}, headers=ha).status_code == 422
    assert api.put(f"/api/admin/learners/{uid}/plan", json={"plan": "pro"}, headers=h).status_code == 403
    summary = api.get("/api/admin/jarvis", headers=ha).json()
    assert {"today_usd", "month_usd", "settings", "recent"} <= set(summary)
    assert api.get("/api/admin/jarvis", headers=h).status_code == 403
    me = api.get("/api/me", headers=h).json()
    assert me["plan"] == "pro"


def test_usage_from_event_bills_cached_tokens_apart():
    u = jarvis.usage_from_event({"input_token_details": {"audio_tokens": 100, "text_tokens": 50,
                                                         "cached_tokens_details": {"audio_tokens": 40, "text_tokens": 20}},
                                 "output_token_details": {"audio_tokens": 70, "text_tokens": 5}})
    assert (u.audio_in, u.audio_cached, u.text_in, u.text_cached, u.audio_out, u.text_out) == (60, 40, 30, 20, 70, 5)


# ---------- step 2: noticing when a learner is stuck ----------

TASK_STEP = 7  # python-basics, chapter first-program: the "Pocket says hello" task (hello_pocket)


def _fail(uid: int, task: str = "hello_pocket", passed: bool = False) -> None:
    with Session(engine) as s:
        s.add(CheckRun(user_id=uid, lab_id=LAB, chapter_id="first-program", passed_count=int(passed), total_count=2, output_tail="",
                       duration_ms=10, results_json=f'[{{"task": "{task}", "passed": {str(passed).lower()}, "message": "Expected two lines"}}]'))
        s.commit()


def nudge(api, h, step=TASK_STEP, idle=0):
    return api.get("/api/jarvis/nudge", params={"lab_id": LAB, "chapter_id": "first-program", "step": step, "idle": idle}, headers=h).json()


def test_three_failed_checks_in_a_row_bring_an_offer_of_help(api):
    h, uid = signup(api)
    _fail(uid); _fail(uid)
    assert nudge(api, h)["nudge"] is False  # two is not yet stuck
    _fail(uid)
    n = nudge(api, h)
    assert n["nudge"] and n["reason"] == "fails" and n["task_id"] == "hello_pocket" and "3 checks" in n["line"]
    # A pass ends the streak: no more offers on that task.
    _fail(uid, passed=True)
    assert nudge(api, h)["nudge"] is False


def test_every_hint_used_or_a_long_pause_bring_an_offer(api):
    from app.models import TaskProgress

    h, uid = signup(api)
    assert nudge(api, h, idle=60)["nudge"] is False
    n = nudge(api, h, idle=9 * 60)
    assert n["nudge"] and n["reason"] == "idle" and "9 minutes" in n["line"]
    with Session(engine) as s:
        from app.labs import get_lab
        hints = len(get_lab(LAB).task("first-program", "hello_pocket").hints)
        s.add(TaskProgress(user_id=uid, lab_id=LAB, task_id="hello_pocket", chapter_id="first-program", hints_used=hints))
        s.commit()
    assert nudge(api, h)["reason"] == "hints"


def test_no_offer_off_a_task_step_or_for_a_passed_task(api):
    h, uid = signup(api)
    _fail(uid); _fail(uid); _fail(uid)
    assert nudge(api, h, step=0)["nudge"] is False  # the story step has no task
    with Session(engine) as s:
        from app.models import TaskProgress
        s.add(TaskProgress(user_id=uid, lab_id=LAB, task_id="hello_pocket", chapter_id="first-program", passed=True))
        s.commit()
    assert nudge(api, h)["nudge"] is False


def test_accepting_the_offer_tells_jarvis_why(api):
    h, uid = signup(api, plan="pro")
    _fail(uid); _fail(uid); _fail(uid)
    with Session(engine) as s:
        user = s.get(User, uid)
        n = jarvis.nudge(s, user, LAB, "first-program", TASK_STEP)
        text = jarvis.instructions(s, user, LAB, "first-program", TASK_STEP, n.detail)
    assert "Why this conversation started" in text and "failed 3 checks" in text and "Expected two lines" in text
    r = api.post("/api/jarvis/session", json={"lab_id": LAB, "chapter_id": "first-program", "step": TASK_STEP, "reason": "fails"}, headers=h)
    assert r.status_code == 200, r.text
