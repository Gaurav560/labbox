"""Engagement: levels, timezone-correct streaks with fixed clocks, the XP ledger, daily drill,
skill map, onboarding and content validation. No Docker needed."""
import random
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import drills, engagement, labs
from app.config import get_settings
from app.content import get_content, init_content, load_content
from app.db import engine, init_db
from app.engagement import compute_streak, level_for, local_day, xp_for_level
from app.labs import LabError
from app.main import app
from app.models import ChapterProgress, PredictAnswer, TaskProgress, User, UserProfile, XpEvent

ROOT = Path(__file__).resolve().parents[2]
D = date(2026, 11, 18)  # a Wednesday



def _ch1_steps():
    """Python from zero, chapter 1, parsed from its file: tests find steps by type, not by number, so the
    lesson can grow (a history step, more examples) without breaking them."""
    from pathlib import Path

    from app.lessons import parse_steps

    return parse_steps((Path(__file__).resolve().parents[2] / "labs/python-basics/chapters/01-functions.md").read_text())


def days(*offsets: int, xp: int = 20) -> dict[date, int]:
    return {D + timedelta(days=o): xp for o in offsets}


# ---------- levels ----------


def test_level_thresholds():
    assert [xp_for_level(n) for n in (1, 2, 3, 4, 5)] == [0, 100, 283, 520, 800]
    assert [level_for(x) for x in (0, 99, 100, 282, 283, 519, 520, 10_000)] == [1, 1, 2, 2, 3, 3, 4, 22]


# ---------- local days (timezones) ----------


def test_local_day_crosses_midnight():
    # 18:45 UTC is 00:15 the next day in India (UTC+5:30), still the same day in London.
    at = datetime(2026, 11, 18, 18, 45)
    assert local_day(at, "Asia/Kolkata") == date(2026, 11, 19)
    assert local_day(at, "Europe/London") == date(2026, 11, 18)
    assert local_day(datetime(2026, 11, 18, 18, 15), "Asia/Kolkata") == date(2026, 11, 18)  # 23:45 IST
    assert local_day(at, "America/Los_Angeles") == date(2026, 11, 18)
    assert local_day(at, None) == date(2026, 11, 18)  # not set yet: UTC
    assert local_day(at, "Mars/Olympus") == date(2026, 11, 18)  # broken value: UTC, never a crash


# ---------- streaks ----------


def test_streak_basics():
    assert compute_streak({}, D).current == 0
    assert compute_streak(days(-2, -1, 0), D).current == 3
    # Today is not over: yesterday's streak still stands.
    assert compute_streak(days(-3, -2, -1), D).current == 3
    # 19 XP is not enough for a day to count.
    assert compute_streak({**days(-2, -1), D: 19}, D).current == 2
    assert compute_streak(days(-1, xp=19), D).current == 0


def test_streak_freeze_covers_one_missed_day():
    # Sun 15 played, Mon 16 missed (frozen), Tue 17 and Wed 18 played.
    s = compute_streak(days(-3, -1, 0), D)
    assert s.current == 3 and s.frozen_days == [D - timedelta(days=2)]
    assert s.freeze_available is False  # this week's freeze is used


def test_two_missed_days_in_a_row_break_the_streak():
    s = compute_streak(days(-5, -4, -1, 0), D)
    assert s.current == 2 and s.best == 2


def test_one_freeze_per_week():
    # Mon 16 and Wed 18 played, Tue 17 missed (freeze), Thu 19 missed: no second freeze that week.
    thu = D + timedelta(days=1)
    s = compute_streak({D - timedelta(days=2): 20, D: 20, thu + timedelta(days=1): 20}, thu + timedelta(days=1))
    assert s.current == 1 and s.best == 2


def test_freezes_in_different_weeks():
    # Missed Tue 10 Nov (week 46) and Tue 17 Nov (week 47): each week has its own freeze.
    played = {D - timedelta(days=d) for d in range(0, 10)} - {D - timedelta(days=1), D - timedelta(days=8)}
    s = compute_streak({d: 30 for d in played}, D)
    assert s.current == 8 and len(s.frozen_days) == 2


def test_freeze_not_spent_without_a_streak():
    s = compute_streak({}, D)
    assert s.freeze_available and s.frozen_days == []


# ---------- ledger and API ----------


@pytest.fixture(scope="module")
def client() -> TestClient:
    labs.init_labs(get_settings().LABS_DIR)
    init_content(ROOT)
    init_db()
    return TestClient(app)


def signup(client: TestClient) -> tuple[dict, int]:
    r = client.post("/api/auth/signup", json={"username": f"eng{random.randint(0, 10**9)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user"]["id"]


def test_new_user_stats_and_onboarding_flag(client: TestClient):
    h, _ = signup(client)
    s = client.get("/api/me/stats", headers=h).json()
    assert (s["xp_total"], s["level"], s["streak_current"], s["needs_onboarding"]) == (0, 1, 0, True)
    assert s["next_level_xp"] == 100
    assert client.post("/api/onboarding/skip", headers=h).json()["needs_onboarding"] is False


def test_check_awards_task_chapter_and_lab_once(client: TestClient):
    h, uid = signup(client)
    lab = labs.get_lab("python-basics")
    with Session(engine) as s:
        s.add(TaskProgress(user_id=uid, lab_id=lab.id, task_id="greet", chapter_id="01-functions", hints_used=1))
        s.commit()
        part = engagement.award_for_check(s, uid, lab, "01-functions", {"greet": True, "add": False, "is_even": False})
        assert [(a.kind, a.amount) for a in part] == [("task", 16)]  # one hint: 80% of 20
        full = engagement.award_for_check(s, uid, lab, "01-functions", {"greet": True, "add": True, "is_even": True})
        assert [(a.kind, a.amount) for a in full] == [("task", 20), ("task", 20), ("chapter", 50)]
        assert engagement.award_for_check(s, uid, lab, "01-functions", {"greet": True, "add": True, "is_even": True}) == []
        assert len(s.exec(select(XpEvent).where(XpEvent.user_id == uid)).all()) == 4
    st = client.get("/api/me/stats", headers=h).json()
    assert st["xp_total"] == 106 and st["level"] == 2 and st["today_xp"] == 106 and st["streak_current"] == 1
    prog = client.get("/api/labs/python-basics/chapters/01-functions/progress", headers=h).json()
    assert prog["xp_earned"] == 106  # this chapter's tasks and completion

    # The lab bonus comes once, with the last chapter finished (whatever the course's length).
    with Session(engine) as s:
        rest = lab.chapters[1:]
        for i, ch in enumerate(rest):
            got = engagement.award_for_check(s, uid, lab, ch.id, {t.id: True for t in ch.tasks})
            kinds = [a.kind for a in got]
            assert ("lab" in kinds) == (i == len(rest) - 1), (ch.id, kinds)
            if "lab" in kinds:
                assert next(a.amount for a in got if a.kind == "lab") == 200
        assert engagement.award_for_check(s, uid, lab, rest[-1].id, {t.id: True for t in rest[-1].tasks}) == []


def test_predict_first_try_bonus(client: TestClient):
    url = "/api/labs/python-basics/chapters/01-functions/predict"
    h, _ = signup(client)
    step = next(i for i, s in enumerate(_ch1_steps()) if s.type == "predict")
    right = client.post(url, json={"step": step, "choice": 2}, headers=h).json()
    assert right["xp_awarded"] == [{"kind": "predict", "amount": 10, "label": "Right first time"}]
    h2, _ = signup(client)
    client.post(url, json={"step": step, "choice": 0}, headers=h2)
    assert client.post(url, json={"step": step, "choice": 2}, headers=h2).json()["xp_awarded"] == []
    assert client.get("/api/me/stats", headers=h2).json()["xp_total"] == 0


def test_xp_uses_the_timezone_at_the_time(client: TestClient):
    h, uid = signup(client)
    assert client.put("/api/me/profile", json={"timezone": "Asia/Kolkata"}, headers=h).status_code == 200
    with Session(engine) as s:
        engagement.award(s, uid, "drill", 20, "t1", at=datetime(2026, 11, 18, 18, 45))  # 00:15 IST on the 19th
    client.put("/api/me/profile", json={"timezone": "America/New_York"}, headers=h)
    with Session(engine) as s:
        day = s.exec(select(XpEvent.day).where(XpEvent.user_id == uid, XpEvent.ref == "t1")).one()
        assert day == date(2026, 11, 19)  # changing timezone later does not rewrite history
        st = engagement.stats(s, uid, now=datetime(2026, 11, 20, 12, 0))  # 07:00 on the 20th in New York
        assert st.streak_current == 1 and st.today_xp == 0
        assert engagement.stats(s, uid, now=datetime(2026, 11, 22, 12, 0)).streak_current == 0


def test_profile_validation(client: TestClient):
    h, _ = signup(client)
    assert client.put("/api/me/profile", json={"timezone": "Not/AZone"}, headers=h).status_code == 422
    assert client.put("/api/me/profile", json={"goal": "become-a-wizard"}, headers=h).status_code == 422
    r = client.put("/api/me/profile", json={"goal": "devops", "display_name": "  Asha  "}, headers=h).json()
    assert r["goal"] == "devops" and r["display_name"] == "Asha"


def test_existing_user_is_backfilled_and_skips_onboarding():
    labs.init_labs(get_settings().LABS_DIR)  # backfill reads the real labs; do not rely on an earlier test
    with Session(engine) as s:
        u = User(username=f"old{random.randint(0, 10**9)}", password_hash="x")
        s.add(u)
        s.commit()
        uid = u.id
        assert uid is not None
        # What migration 0004 does for users that existed before XP.
        s.add(UserProfile(user_id=uid, onboarded_at=datetime(2026, 11, 1)))
        passed_at = datetime(2026, 10, 1, 9, 0)
        for t in ("greet", "longest_word"):
            s.add(TaskProgress(user_id=uid, lab_id="java-basics", task_id=t, chapter_id="01-methods", passed=True, first_passed_at=passed_at))
        s.add(PredictAnswer(user_id=uid, lab_id="java-basics", chapter_id="01-methods", step_index=2, choice=2, correct=True, created_at=passed_at))
        s.commit()
        st = engagement.stats(s, uid)
        assert st.needs_onboarding is False
        assert st.xp_total == 20 + 20 + 50 + 10  # two tasks, chapter 1, a predict (Java from zero has 13 chapters: no lab bonus yet)
        assert {e.day for e in s.exec(select(XpEvent).where(XpEvent.user_id == uid)).all()} == {date(2026, 10, 1)}
        engagement.backfill(s, uid)  # running again changes nothing
        assert engagement.stats(s, uid).xp_total == 100


def test_daily_drill(client: TestClient):
    h, uid = signup(client)
    d = client.get("/api/drill/today", headers=h).json()
    assert d["drill"] and "answer" not in d["drill"] and d["answer"] is None and d["explain"] is None
    assert client.get("/api/drill/today", headers=h).json()["drill"]["id"] == d["drill"]["id"]  # stable for the day
    drill = next(x for _, x in get_content().drills if x.id == d["drill"]["id"])
    wrong = (drill.answer + 1) % len(drill.options)
    r = client.post("/api/drill/today/answer", json={"choice": wrong}, headers=h).json()
    assert r["solved"] is False and r["wrong"] == [wrong] and r["xp_awarded"] == []
    assert client.post("/api/drill/today/answer", json={"choice": 99}, headers=h).status_code == 422
    r = client.post("/api/drill/today/answer", json={"choice": drill.answer}, headers=h).json()
    assert r["solved"] and r["answer"] == drill.answer and r["xp_awarded"][0]["amount"] == 20
    again = client.post("/api/drill/today/answer", json={"choice": drill.answer}, headers=h).json()
    assert again["xp_awarded"] == []
    st = client.get("/api/me/stats", headers=h).json()
    assert st["xp_total"] == 20 and st["streak_current"] == 1  # a drill alone keeps the streak


def test_drill_follows_the_goal_track(client: TestClient):
    h, uid = signup(client)
    client.put("/api/me/profile", json={"goal": "devops"}, headers=h)
    with Session(engine) as s:
        assert drills.studying_tracks(s, uid) == {"devops"}
        for offset in range(5):
            out = drills.today(s, uid, now=datetime(2026, 11, 18) + timedelta(days=offset))
            assert out.drill and out.drill.track == "devops"


def test_skill_map_lights_up(client: TestClient):
    h, uid = signup(client)
    nodes = {n["id"]: n for n in client.get("/api/tracks/languages/skills", headers=h).json()["nodes"]}
    assert nodes["py-functions"]["state"] == "available"
    assert nodes["py-collections"]["state"] == "locked"  # needs py-functions first
    assert nodes["py-traps"]["state"] == "coming_soon"
    assert nodes["py-functions"]["chapters"][0]["title"] == "Your first functions"
    # The 3D roadmap's panel names each chapter's lab and its number as the lab's menu shows it.
    first = nodes["py-functions"]["chapters"][0]
    assert (first["lab_title"], first["number"]) == ("Python from zero", 1)
    spring = {n["id"]: n for n in client.get("/api/tracks/frameworks/skills", headers=h).json()["nodes"]}
    rel = spring["spring-data-deep"]["chapters"][0]
    assert (rel["lab_title"], rel["number"], rel["chapter_id"]) == ("Spring Boot", 21, "21-relationships")  # numbered from 0
    with Session(engine) as s:
        s.add(ChapterProgress(user_id=uid, lab_id="python-basics", chapter_id="01-functions"))
        s.commit()
        engagement.award_for_check(s, uid, labs.get_lab("python-basics"), "01-functions", {"greet": True, "add": True, "is_even": True})
        assert s.get(ChapterProgress, {"user_id": uid, "lab_id": "python-basics", "chapter_id": "01-functions"}).completed_at
    nodes = {n["id"]: n for n in client.get("/api/tracks/languages/skills", headers=h).json()["nodes"]}
    assert nodes["py-functions"]["state"] == "done" and nodes["java-methods"]["state"] == "available"
    assert nodes["py-collections"]["state"] == "available"  # unlocked by finishing Python functions
    languages = next(t for t in client.get("/api/tracks", headers=h).json() if t["track"] == "languages")
    assert languages["done"] == 1 and languages["nodes"] >= 11  # more skills appear as courses grow
    assert client.get("/api/tracks/cooking/skills", headers=h).status_code == 404


def test_onboarding(client: TestClient):
    h, _ = signup(client)
    ob = client.get("/api/onboarding", headers=h).json()
    assert len(ob["goals"]) == 5 and len(ob["placement"]) == 3
    assert all(set(q) == {"question", "options"} for q in ob["placement"])  # answers stay on the server
    r = client.post("/api/onboarding", json={"goal": "new-language", "answers": [1, 1, 0]}, headers=h).json()
    assert (r["score"], r["level"], r["start"]["lab_id"], r["note"]) == (2, "intermediate", "python-basics", None)
    assert [x["correct"] for x in r["results"]] == [True, True, False]
    assert client.get("/api/me/stats", headers=h).json()["needs_onboarding"] is False
    r = client.post("/api/onboarding", json={"goal": "devops", "answers": [0, 0, 0]}, headers=h).json()
    assert r["level"] == "beginner" and r["start"]["lab_id"] == "linux-on-call" and r["note"] is None  # DevOps now has its own first lab
    r = client.post("/api/onboarding", json={"goal": "ai", "answers": [0, 0, 0]}, headers=h).json()
    assert r["start"]["lab_id"] == "python-basics" and "on the way" in r["note"]  # a track with no labs yet
    assert client.post("/api/onboarding", json={"goal": "devops", "answers": [0]}, headers=h).status_code == 422
    assert client.post("/api/onboarding", json={"goal": "nope", "answers": [0, 0, 0]}, headers=h).status_code == 422


def test_engagement_routes_need_login(client: TestClient):
    for path in ("/api/me/stats", "/api/drill/today", "/api/tracks", "/api/onboarding"):
        assert client.get(path).status_code == 401


# ---------- content validation ----------


@pytest.fixture
def content_root(tmp_path: Path) -> Path:
    labs.init_labs(get_settings().LABS_DIR)
    for d in ("tracks", "drills", "onboarding"):
        shutil.copytree(ROOT / d, tmp_path / d)
    return tmp_path


@pytest.mark.parametrize(
    "file, old, new, match",
    [
        ("tracks/languages.yaml", "requires: [py-collections]", "requires: [nope]", "unknown node 'nope'"),
        ("tracks/languages.yaml", "chapters: [java-basics/01-methods]", "chapters: [java-basics/99]", "unknown chapter"),
        ("tracks/languages.yaml", "    chapters: [python-basics/01-functions]",
         "    chapters: [python-basics/01-functions]\n    requires: [py-traps]", "loop"),
        ("drills/devops.yaml", "    answer: 2\n", "    answer: 7\n", "answer 7"),
        ("drills/devops.yaml", "id: sh-grep-r", "id: sh-ls-la", "duplicate drill id"),
        ("onboarding/onboarding.yaml", "track: ai\n    start: [python-basics]", "track: ai\n    start: [no-such-lab]", "none of the existing labs"),
    ],
)
def test_broken_content_fails_loudly(content_root: Path, file: str, old: str, new: str, match: str):
    p = content_root / file
    assert old in p.read_text()
    p.write_text(p.read_text().replace(old, new, 1))
    with pytest.raises(LabError, match=match):
        load_content(content_root)


def test_real_content_loads():
    labs.init_labs(get_settings().LABS_DIR)
    c = load_content(ROOT)
    assert "languages" in c.tracks and len(c.drills) >= 14 and c.onboarding is not None
