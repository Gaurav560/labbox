"""At most a few labs at a time (owner, 26 November): unlocking, the full lock, finishing (80%), the Monday swap,
and the admin's limits. Most tests give one learner their own limit, so the site's setting stays "every lab" for
the other tests; the one test that changes the site's setting puts it back."""
import random
from collections.abc import Iterator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import slots
from app.db import engine
from app.labs import get_lab
from sqlmodel import select

from app.models import TaskProgress, User, Workspace, utcnow

A, B, C = "python-basics", "python-collections", "fastapi-first-api"


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def signup(api: TestClient, name: str = "slot") -> tuple[dict, int]:
    r = api.post("/api/auth/signup", json={"username": f"{name}{random.randint(0, 10**8)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user"]["id"]


def set_user(uid: int, **fields) -> None:
    with Session(engine) as s:
        u = s.get(User, uid)
        for k, v in fields.items():
            setattr(u, k, v)
        s.add(u)
        s.commit()


def learner(api: TestClient, limit: int) -> tuple[dict, int]:
    h, uid = signup(api)
    set_user(uid, lab_limit=limit)
    return h, uid


def pass_tasks(uid: int, lab_id: str, n: int) -> None:
    lab = get_lab(lab_id)
    tasks = [(c.id, t.id) for c in lab.chapters for t in c.tasks][:n]
    with Session(engine) as s:
        # A real learner opened the lab before passing anything (the admin funnel counts on it).
        if s.exec(select(Workspace).where(Workspace.user_id == uid, Workspace.lab_id == lab_id)).first() is None:
            s.add(Workspace(user_id=uid, lab_id=lab_id, container_name=f"lab-u{uid}-{lab_id}", volume_path="/tmp/x"))
        for chapter_id, task_id in tasks:
            s.add(TaskProgress(user_id=uid, lab_id=lab_id, task_id=task_id, chapter_id=chapter_id, passed=True,
                               first_passed_at=utcnow()))
        s.commit()


def lab_routes(lab_id: str) -> list[tuple[str, str, dict | None]]:
    lab = get_lab(lab_id)
    ch = lab.chapters[0]
    task = ch.tasks[0].id
    return [
        ("get", f"/api/labs/{lab_id}/chapters/{ch.id}", None),
        ("get", f"/api/labs/{lab_id}/chapters/{ch.id}/outline", None),
        ("get", f"/api/labs/{lab_id}/chapters/{ch.id}/steps/0/code", None),
        ("post", f"/api/labs/{lab_id}/chapters/{ch.id}/focus", {}),
        ("get", f"/api/labs/{lab_id}/chapters/{ch.id}/progress", None),
        ("post", f"/api/labs/{lab_id}/chapters/{ch.id}/tasks/{task}/hint", None),
        ("post", f"/api/labs/{lab_id}/chapters/{ch.id}/tasks/{task}/tutor", {"question": "why?"}),
        ("post", f"/api/labs/{lab_id}/chapters/{ch.id}/setup", None),
        ("post", f"/api/labs/{lab_id}/check", {"chapter_id": ch.id}),
        ("get", f"/api/labs/{lab_id}/checks", None),
        ("get", f"/api/labs/{lab_id}/files", None),
        ("get", f"/api/labs/{lab_id}/files/content?path=README.md", None),
        ("post", f"/api/labs/{lab_id}/workspace/start", None),
        ("post", f"/api/labs/{lab_id}/workspace/reset", None),
        ("post", f"/api/labs/{lab_id}/preview/ticket", None),
        ("post", f"/api/labs/{lab_id}/ide", None),
        ("post", f"/api/labs/{lab_id}/complete", {"prefix": "x", "suffix": "", "path": "a.py"}),
    ]


def call(api, h, method, url, body):
    return getattr(api, method)(url, headers=h, **({"json": body} if body is not None else {}))


def test_every_lab_is_open_by_default(api):
    h, _ = signup(api)
    s = api.get("/api/slots", headers=h).json()
    assert s["limit"] is None and s["free"] is None
    assert set(s["labs"].values()) == {"open"}
    assert {lab["access"] for lab in api.get("/api/labs", headers=h).json()} == {"open"}
    ch = get_lab(A).chapters[0].id
    assert api.get(f"/api/labs/{A}/chapters/{ch}", headers=h).status_code == 200


def test_a_locked_lab_shows_only_its_course_page(api):
    h, _ = learner(api, 2)
    detail = api.get(f"/api/labs/{A}", headers=h)
    assert detail.status_code == 200 and detail.json()["access"] == "locked"  # the course page still opens
    assert detail.json()["chapters"]  # with its skill map
    for method, url, body in lab_routes(A):
        r = call(api, h, method, url, body)
        assert r.status_code == 403, (url, r.status_code, r.text)
        assert "locked" in r.json()["detail"]


def test_the_terminal_refuses_a_locked_lab(api):
    h, _ = learner(api, 1)
    token = h["Authorization"].split()[1]
    with api.websocket_connect(f"/ws/terminal/{A}?token={token}") as ws:
        msg = ws.receive_json()
    assert msg["type"] == "error" and "locked" in msg["message"]


def test_unlock_up_to_the_limit(api):
    h, _ = learner(api, 2)
    r = api.post(f"/api/labs/{A}/unlock", headers=h)
    assert r.status_code == 200 and r.json()["labs"][A] == "unlocked" and r.json()["free"] == 1
    assert api.post(f"/api/labs/{A}/unlock", headers=h).json()["used"] == 1  # unlocking twice costs nothing
    assert api.post(f"/api/labs/{B}/unlock", headers=h).json()["free"] == 0
    r = api.post(f"/api/labs/{C}/unlock", headers=h)
    assert r.status_code == 409 and "All 2 of your lab slots" in r.json()["detail"]
    ch = get_lab(A).chapters[0].id
    assert api.get(f"/api/labs/{A}/chapters/{ch}", headers=h).status_code == 200
    assert api.get(f"/api/labs/{A}/chapters/{ch}/progress", headers=h).status_code == 200
    assert api.get(f"/api/labs/{C}/chapters/{get_lab(C).chapters[0].id}", headers=h).status_code == 403
    access = {lab["id"]: lab["access"] for lab in api.get("/api/labs", headers=h).json()}
    assert access[A] == access[B] == "unlocked" and access[C] == "locked"


def test_finishing_80_percent_frees_the_slot(api):
    h, uid = learner(api, 1)
    api.post(f"/api/labs/{A}/unlock", headers=h)
    total = get_lab(A).task_count
    need = -(-total * 4 // 5)  # 80%, rounded up
    pass_tasks(uid, A, need - 1)
    assert api.get("/api/slots", headers=h).json()["labs"][A] == "unlocked"
    assert api.post(f"/api/labs/{C}/unlock", headers=h).status_code == 409
    lab_tasks = [(c.id, t.id) for c in get_lab(A).chapters for t in c.tasks]
    with Session(engine) as s:
        chapter_id, task_id = lab_tasks[need - 1]
        s.add(TaskProgress(user_id=uid, lab_id=A, task_id=task_id, chapter_id=chapter_id, passed=True, first_passed_at=utcnow()))
        s.commit()
    s = api.get("/api/slots", headers=h).json()
    assert s["labs"][A] == "finished" and s["used"] == 0 and s["free"] == 1
    assert api.post(f"/api/labs/{C}/unlock", headers=h).status_code == 200
    ch = get_lab(A).chapters[0].id
    assert api.get(f"/api/labs/{A}/chapters/{ch}", headers=h).status_code == 200  # a finished lab stays open


def test_a_finished_lab_is_open_without_a_slot(api):
    h, uid = learner(api, 1)
    pass_tasks(uid, B, get_lab(B).task_count)
    assert api.get(f"/api/labs/{B}", headers=h).json()["access"] == "finished"
    assert api.get("/api/slots", headers=h).json()["free"] == 1


def _at(monkeypatch, iso: str) -> None:
    monkeypatch.setattr(slots, "now", lambda: datetime.fromisoformat(iso))


def test_the_swap_day_is_monday_in_india(monkeypatch):
    # Sunday 18:30 UTC is Monday 00:00 in India; Monday 18:30 UTC is Tuesday 00:00 there.
    assert not slots.swap_open(datetime(2026, 11, 29, 18, 29, tzinfo=timezone.utc))
    assert slots.swap_open(datetime(2026, 11, 29, 18, 30, tzinfo=timezone.utc))
    assert slots.swap_open(datetime(2026, 11, 30, 18, 29, tzinfo=timezone.utc))
    assert not slots.swap_open(datetime(2026, 11, 30, 18, 30, tzinfo=timezone.utc))
    nxt = slots.next_swap(datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc))  # a Thursday
    assert nxt.isoformat() == "2026-11-30T00:00:00+05:30"
    assert slots.next_swap(datetime(2026, 11, 30, 3, 0, tzinfo=timezone.utc)).isoformat() == "2026-11-30T00:00:00+05:30"


def test_swap_only_on_monday(api, monkeypatch):
    h, uid = learner(api, 1)
    api.post(f"/api/labs/{A}/unlock", headers=h)
    _at(monkeypatch, "2026-12-01T10:00:00+00:00")  # a Tuesday
    r = api.post(f"/api/labs/{A}/swap", headers=h)
    assert r.status_code == 409 and "Monday" in r.json()["detail"]
    assert api.get("/api/slots", headers=h).json()["swap_open"] is False
    _at(monkeypatch, "2026-11-30T10:00:00+00:00")  # a Monday
    assert api.post(f"/api/labs/{B}/swap", headers=h).status_code == 409  # never unlocked
    r = api.post(f"/api/labs/{A}/swap", headers=h)
    assert r.status_code == 200 and r.json()["labs"][A] == "locked" and r.json()["free"] == 1
    ch = get_lab(A).chapters[0].id
    assert api.get(f"/api/labs/{A}/chapters/{ch}", headers=h).status_code == 403
    assert api.post(f"/api/labs/{C}/unlock", headers=h).status_code == 200
    # Progress is kept: unlocking the first lab again (after swapping the second out) finds it as it was.
    pass_tasks(uid, A, 1)
    api.post(f"/api/labs/{C}/swap", headers=h)
    assert api.post(f"/api/labs/{A}/unlock", headers=h).json()["labs"][A] == "unlocked"
    with Session(engine) as s:
        assert s.get(TaskProgress, (uid, A, get_lab(A).chapters[0].tasks[0].id)) is not None


def test_admins_are_never_limited(api):
    h, uid = learner(api, 1)
    set_user(uid, is_admin=True)
    try:
        assert set(api.get("/api/slots", headers=h).json()["labs"].values()) == {"open"}
        assert api.get(f"/api/labs/{A}/chapters/{get_lab(A).chapters[0].id}", headers=h).status_code == 200
    finally:
        set_user(uid, is_admin=False)


def test_lowering_the_limit_keeps_unlocked_labs(api):
    h, uid = learner(api, 2)
    api.post(f"/api/labs/{A}/unlock", headers=h)
    api.post(f"/api/labs/{B}/unlock", headers=h)
    set_user(uid, lab_limit=1)
    s = api.get("/api/slots", headers=h).json()
    assert s["labs"][A] == s["labs"][B] == "unlocked" and s["free"] == 0
    assert api.post(f"/api/labs/{C}/unlock", headers=h).status_code == 409


def test_the_dashboard_picks_up_in_an_open_lab(api):
    h, uid = learner(api, 1)
    api.post(f"/api/labs/{B}/unlock", headers=h)
    nxt = api.get("/api/me/next", headers=h).json()
    assert nxt["lab_id"] == B and nxt["reason"] == "One of the labs you unlocked"
    locked = api.get(f"/api/me/next?lab={A}", headers=h).json()
    assert locked["step_title"] is None and locked["code"] == []  # no lesson text from a locked lab


def test_admin_sets_the_limit_for_everyone_and_for_one_learner(api):
    boss, boss_id = signup(api, "boss")
    set_user(boss_id, is_admin=True)
    plain, plain_id = signup(api)
    try:
        assert api.put("/api/admin/lab-access", json={"limit": 3}, headers=plain).status_code == 403
        assert api.get("/api/admin/lab-access", headers=boss).json()["limit"] is None
        assert api.put("/api/admin/lab-access", json={"limit": 3}, headers=boss).json()["limit"] == 3
        s = api.get("/api/slots", headers=plain).json()
        assert s["limit"] == 3 and s["labs"][A] == "locked"
        # One learner gets 10, then every lab, then the site's setting again.
        r = api.put(f"/api/admin/learners/{plain_id}/lab-limit", json={"lab_limit": 10}, headers=boss)
        assert r.json() == {"lab_limit": 10}
        assert api.get("/api/slots", headers=plain).json()["limit"] == 10
        api.put(f"/api/admin/learners/{plain_id}/lab-limit", json={"lab_limit": 0}, headers=boss)
        assert api.get("/api/slots", headers=plain).json()["labs"][A] == "open"
        with Session(engine) as db:
            name = db.get(User, plain_id).username
        rows = api.get(f"/api/admin/learners?q={name}", headers=boss).json()
        assert rows[0]["lab_limit"] == 0
        exceptions = api.get("/api/admin/lab-access", headers=boss).json()["exceptions"]
        assert {"id": plain_id, "username": name, "lab_limit": 0} in exceptions
        api.put(f"/api/admin/learners/{plain_id}/lab-limit", json={"lab_limit": None}, headers=boss)
        assert api.get("/api/slots", headers=plain).json()["limit"] == 3
        assert api.put("/api/admin/lab-access", json={"limit": -1}, headers=boss).status_code == 422
    finally:
        api.put("/api/admin/lab-access", json={"limit": None}, headers=boss)
        set_user(boss_id, is_admin=False)
    assert api.get("/api/slots", headers=plain).json()["limit"] is None
