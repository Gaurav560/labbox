"""Phase J: the admin area and its numbers."""
import random
import sys
from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import observability
from app.db import engine
from app.models import AnalyticsEvent, ChapterProgress, LlmRequest, TaskProgress, User, Workspace, utcnow

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def signup(api: TestClient, name: str) -> tuple[dict, int]:
    r = api.post("/api/auth/signup", json={"username": f"{name}{random.randint(0, 10**8)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user"]["id"]


@pytest.fixture(scope="module")
def admin(api) -> dict:
    h, uid = signup(api, "boss")
    with Session(engine) as s:
        u = s.get(User, uid)
        u.is_admin = True
        s.add(u)
        s.commit()
    return h


ROUTES = ["/api/admin/funnel", "/api/admin/labs", "/api/admin/labs/python-basics", "/api/admin/learners",
          "/api/admin/ai-spend", "/api/admin/errors", "/api/admin/machines"]


def test_only_admins_get_in(api, admin):
    learner, _ = signup(api, "plain")
    for route in ROUTES:
        assert api.get(route).status_code == 401
        assert api.get(route, headers=learner).status_code == 403, route
    assert api.post("/api/admin/machines/lab-u1-python-basics", json={"action": "stop"}, headers=learner).status_code == 403
    assert api.get("/api/me", headers=learner).json()["is_admin"] is False
    assert api.get("/api/me", headers=admin).json()["is_admin"] is True


def test_funnel_follows_a_learner_down(api, admin):
    _, uid = signup(api, "fun")
    before = {f["key"]: f["count"] for f in api.get("/api/admin/funnel?window=7d", headers=admin).json()}
    with Session(engine) as s:
        s.add(Workspace(user_id=uid, lab_id="python-basics", container_name=f"lab-u{uid}-python-basics", volume_path="/tmp/x"))
        s.add(TaskProgress(user_id=uid, lab_id="python-basics", task_id="hello_pocket", chapter_id="first-program", passed=True))
        s.add(ChapterProgress(user_id=uid, lab_id="python-basics", chapter_id="first-program", completed_at=utcnow()))
        s.commit()
    steps = api.get("/api/admin/funnel?window=7d", headers=admin).json()
    after = {f["key"]: f["count"] for f in steps}
    for key in ("signed_up", "opened_lab", "first_pass", "chapter_1"):
        assert after[key] == before[key] + (0 if key == "signed_up" else 1), key
    counts = [f["count"] for f in steps]
    assert counts == sorted(counts, reverse=True)  # each step is a subset of the one before
    assert steps[0]["of_previous"] is None and 0 <= steps[1]["of_previous"] <= 1


def test_step_events_give_time_per_step_and_quit_points(api, admin):
    h, uid = signup(api, "steps")
    for step in (0, 1, 2):
        assert api.put("/api/labs/python-basics/chapters/first-program/progress", json={"current_step": step}, headers=h).status_code == 200
    with Session(engine) as s:
        events = s.exec(select(AnalyticsEvent).where(AnalyticsEvent.user_id == uid).order_by(AnalyticsEvent.id)).all()
        assert [e.step_index for e in events] == [0, 1, 2]
        base = utcnow() - timedelta(minutes=10)
        for i, e in enumerate(events):  # 90 s on step 0, 30 s on step 1
            e.created_at = base + timedelta(seconds=[0, 90, 120][i])
            s.add(e)
        cp = s.exec(select(ChapterProgress).where(ChapterProgress.user_id == uid, ChapterProgress.chapter_id == "first-program")).one()
        cp.updated_at = utcnow() - timedelta(days=3)  # left on step 2 three days ago
        s.add(cp)
        s.commit()
    report = api.get("/api/admin/labs/python-basics", headers=admin).json()
    steps = report["chapters"][0]["steps"]
    assert steps[0]["avg_seconds"] is not None and steps[2]["stopped_here"] >= 1
    assert report["tasks"] == sorted(report["tasks"], key=lambda t: (-t["confusion"], -t["attempted"]))


def test_ai_spend_by_day_model_and_learner(api, admin):
    _, uid = signup(api, "spender")
    with Session(engine) as s:
        for tokens in (100, 300):
            s.add(LlmRequest(user_id=uid, lab_id="ai-lab", endpoint="chat", alias="lab-chat", model="fake/chat-small",
                             prompt_tokens=tokens, completion_tokens=0, cost_usd=0.001))
        s.commit()
    spend = api.get("/api/admin/ai-spend?days=7", headers=admin).json()
    today = utcnow().date().isoformat()
    assert any(d["day"] == today and d["tokens"] >= 400 for d in spend["days"])
    assert any(m["name"] == "fake/chat-small" for m in spend["by_model"])


def test_recent_errors_are_listed(api, admin):
    observability.remember_error("POST", "/api/labs/{lab_id}/check", 500, "req-xyz", 12, "RuntimeError: boom")
    errs = api.get("/api/admin/errors", headers=admin).json()
    assert errs[0]["request_id"] == "req-xyz" and errs[0]["error"] == "RuntimeError: boom"


def test_learner_search(api, admin):
    _, uid = signup(api, "findme")
    rows = api.get("/api/admin/learners?q=findme", headers=admin).json()
    assert any(r["id"] == uid for r in rows) and all("findme" in r["username"] for r in rows)


def test_cli_grants_and_revokes(api):
    sys.path.insert(0, str(ROOT / "tools"))
    import labbox_cli

    _, uid = signup(api, "cli")
    with Session(engine) as s:
        name = s.get(User, uid).username
    assert labbox_cli.main(["admin", "grant", name]) == 0
    with Session(engine) as s:
        assert s.get(User, uid).is_admin is True
    assert labbox_cli.main(["admin", "revoke", name]) == 0
    with Session(engine) as s:
        assert s.get(User, uid).is_admin is False
    assert labbox_cli.main(["admin", "grant", "no-such-account-anywhere"]) == 1


@pytest.mark.docker
def test_admin_sees_and_stops_and_kills_machines(api, admin):
    h, uid = signup(api, "mach")
    name = f"lab-u{uid}-python-basics"
    try:
        assert api.post("/api/labs/python-basics/workspace/start", headers=h).status_code == 200
        machines = api.get("/api/admin/machines", headers=admin).json()
        assert any(m["container"] == name and m["lab_title"] == "Python from zero" for m in machines)

        assert api.post(f"/api/admin/machines/{name}", json={"action": "stop"}, headers=admin).status_code == 200
        st = api.get("/api/labs/python-basics/workspace/status", headers=h).json()
        assert st["status"] == "stopped" and "by an admin" in st["stopped_reason"]

        assert api.post("/api/labs/python-basics/workspace/start", headers=h).status_code == 200
        assert api.post(f"/api/admin/machines/{name}", json={"action": "kill"}, headers=admin).status_code == 200
        assert api.get("/api/labs/python-basics/workspace/status", headers=h).json()["status"] == "missing"
        files = api.get("/api/labs/python-basics/files", headers=h)  # the learner's files are still there
        assert files.status_code == 200 and any(f["name"] == "01-first-program" for f in files.json())
        assert api.post("/api/admin/machines/lab-u1-no-such-lab", json={"action": "stop"}, headers=admin).status_code == 404
    finally:
        api.post("/api/labs/python-basics/workspace/stop", headers=h)
