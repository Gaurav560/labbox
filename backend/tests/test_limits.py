"""Phase H5: safety limits (app/limits.py)."""
import random
import time
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import limits, shared
from app.config import get_settings


@pytest.fixture
def setting(monkeypatch):
    """Change settings for one test: setting(DISK_QUOTA_MB=1)."""
    def change(**values):
        for k, v in values.items():
            monkeypatch.setenv(k, str(v))
        get_settings.cache_clear()

    yield change
    get_settings.cache_clear()


# ---------- no Docker ----------


def test_values_expire():
    shared.put("test:v", "hello", 0.2)
    assert shared.get("test:v") == "hello"
    time.sleep(0.3)
    assert shared.get("test:v") is None
    shared.put("test:v", "again", 5)
    shared.delete("test:v")
    assert shared.get("test:v") is None


def test_disk_counts_own_files_not_lab_databases(tmp_path, setting):
    setting(VOLUMES_DIR=tmp_path, DISK_QUOTA_MB=1)
    uid = random.randint(10_000_000, 89_000_000)
    home = tmp_path / f"u{uid}"
    (home / "go-basics").mkdir(parents=True)
    (home / "go-basics" / "small.go").write_bytes(b"x" * 100_000)
    (home / "sql-from-zero.services" / "db").mkdir(parents=True)
    (home / "sql-from-zero.services" / "db" / "base").write_bytes(b"x" * 3_000_000)  # seeded data: not counted
    assert limits.learner_files_mb(uid, fresh=True) < 0.2
    limits.check_disk(uid, fresh=True)  # under 1 MB: fine
    (home / "go-basics" / "big.bin").write_bytes(b"x" * 2_000_000)
    with pytest.raises(HTTPException) as e:
        limits.check_disk(uid, fresh=True)
    assert e.value.status_code == 507 and "of your 1 MB" in e.value.detail


def test_cpu_stuck_needs_the_whole_window(monkeypatch, setting):
    setting(CPU_STUCK_MINUTES=10)
    c = SimpleNamespace(id="abc", name=f"lab-u{random.randint(10**7, 9 * 10**7)}-go-basics", attrs={"HostConfig": {"NanoCpus": 1_000_000_000}})
    usage = {"u": 0}
    monkeypatch.setattr(limits, "cpu_usage_usec", lambda _id: usage["u"])
    t = 1_000_000.0
    assert not limits.cpu_stuck(c, t)
    for minute in range(1, 10):  # busy (one full CPU) for 9 minutes: not yet
        usage["u"] += 60 * 1_000_000
        assert not limits.cpu_stuck(c, t + 60 * minute)
    usage["u"] += 60 * 1_000_000
    assert limits.cpu_stuck(c, t + 600)  # the tenth busy minute
    usage["u"] += 1_000_000  # one quiet minute starts the count again
    assert not limits.cpu_stuck(c, t + 660)


@pytest.fixture
def api(setting) -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def _signup(api: TestClient, name: str) -> dict:
    r = api.post("/api/auth/signup", json={"username": f"{name}{random.randint(0, 10**8)}", "password": "secret123"})
    return r


def test_signups_per_address(api, setting):
    setting(SIGNUPS_PER_IP_HOUR=2)
    shared.forget_hits()
    assert _signup(api, "a").status_code == 200
    assert _signup(api, "b").status_code == 200
    r = _signup(api, "c")
    assert r.status_code == 429 and "an hour" in r.json()["detail"] and r.headers["Retry-After"] == "3600"


def test_only_failed_logins_count(api, setting):
    setting(LOGIN_FAILS_PER_USER_MINUTE=3)
    shared.forget_hits()
    name = f"lf{random.randint(0, 10**8)}"
    assert api.post("/api/auth/signup", json={"username": name, "password": "secret123"}).status_code == 200
    for _ in range(5):  # logging in often is fine
        assert api.post("/api/auth/login", json={"username": name, "password": "secret123"}).status_code == 200
    for _ in range(3):
        assert api.post("/api/auth/login", json={"username": name, "password": "wrong-one"}).status_code == 401
    r = api.post("/api/auth/login", json={"username": name, "password": "secret123"})
    assert r.status_code == 429  # even the right password waits a minute after 3 wrong ones


def test_checks_per_address(api, setting):
    setting(CHECKS_PER_IP_MINUTE=1)
    shared.forget_hits()
    token = _signup(api, "ck").json()["token"]
    h = {"Authorization": f"Bearer {token}"}
    api.post("/api/labs/python-basics/check", json={"chapter_id": "no-such-chapter"}, headers=h)  # counts, then 404
    r = api.post("/api/labs/python-basics/check", json={"chapter_id": "no-such-chapter"}, headers=h)
    assert r.status_code == 429


# ---------- with Docker: real machines ----------


@pytest.mark.docker
def test_a_third_lab_stops_the_least_recently_used(api, setting):
    setting(MAX_RUNNING_LABS=2)
    h = {"Authorization": f"Bearer {_signup(api, 'room').json()['token']}"}
    try:
        for lab in ("python-basics", "go-basics"):
            assert api.post(f"/api/labs/{lab}/workspace/start", headers=h).status_code == 200
            time.sleep(1.1)  # distinct "last used" times
        assert api.post("/api/labs/java-basics/workspace/start", headers=h).status_code == 200
        first = api.get("/api/labs/python-basics/workspace/status", headers=h).json()
        assert first["status"] == "stopped"
        assert "make room for Java" in first["stopped_reason"]
        assert api.get("/api/labs/go-basics/workspace/status", headers=h).json()["status"] == "running"
        # Starting it again clears the note (and stops the next least recently used one).
        assert api.post("/api/labs/python-basics/workspace/start", headers=h).status_code == 200
        again = api.get("/api/labs/python-basics/workspace/status", headers=h).json()
        assert again["status"] == "running" and "stopped_reason" not in again
        assert api.get("/api/labs/go-basics/workspace/status", headers=h).json()["status"] == "stopped"
    finally:
        for lab in ("python-basics", "go-basics", "java-basics"):
            api.post(f"/api/labs/{lab}/workspace/stop", headers=h)


@pytest.mark.docker
def test_session_and_disk_limits_stop_a_machine_and_say_why(api, setting):
    from sqlmodel import Session

    from app.db import engine

    h = {"Authorization": f"Bearer {_signup(api, 'sess').json()['token']}"}
    uid = api.get("/api/me", headers=h).json()["id"]
    try:
        assert api.post("/api/labs/python-basics/workspace/start", headers=h).status_code == 200
        setting(SESSION_HOURS=0.0002)  # under a second
        time.sleep(1.2)
        with Session(engine) as s:
            stopped = limits.enforce(s)
        assert any(name == f"lab-u{uid}-python-basics" for name, _ in stopped)
        st = api.get("/api/labs/python-basics/workspace/status", headers=h).json()
        assert st["status"] == "stopped" and "hours of running" in st["stopped_reason"]

        # Disk: over the quota, starting and saving are refused; deleting brings it back.
        setting(SESSION_HOURS=4, DISK_QUOTA_MB=1)
        folder = Path(get_settings().VOLUMES_DIR) / f"u{uid}" / "python-basics"
        (folder / "big.bin").write_bytes(b"x" * 2_000_000)
        r = api.post("/api/labs/python-basics/workspace/start", headers=h)
        assert r.status_code == 507 and "of your 1 MB" in r.json()["detail"]
        (folder / "big.bin").unlink()
        assert api.post("/api/labs/python-basics/workspace/start", headers=h).status_code == 200
    finally:
        api.post("/api/labs/python-basics/workspace/stop", headers=h)
