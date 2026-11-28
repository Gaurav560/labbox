"""Phase D end to end against real Docker: services on a private network, chapter setup, live
checks, incident bonus, the reaper stopping the whole group, reset, and the preview proxy.

Needs the images: bash scripts/build_lab_images.sh
"""
import json
import random
import subprocess
import time
from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path

import pytest

pytestmark = pytest.mark.docker

docker = pytest.importorskip("docker")

PG_LAB, PG_CH = "postgres-indexing-incident", "01-slow-checkout"
API_LAB = "fastapi-first-api"


def _ready() -> bool:
    try:
        c = docker.from_env()
        for image in ("labbox/postgres-indexing-incident:v1", "labbox/fastapi-first-api:v2", "labbox/checker:v1", "postgres:16"):
            c.images.get(image)
        return True
    except Exception:
        return False


if not _ready():
    pytest.skip("Docker or the Phase D images are not available", allow_module_level=True)

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app import containers  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db import engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User, utcnow  # noqa: E402


def sh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), capture_output=True, text=True)


def inspect(kind: str, name: str) -> dict:
    return json.loads(sh("docker", kind, "inspect", name).stdout)[0]


def psql(container: str, sql: str) -> str:
    r = sh("docker", "exec", "-u", "1000", container, "psql", "-tAc", sql)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    init_db()
    with Session(engine) as s:  # high ids: never clash with containers of a dev database
        s.add(User(id=random.randint(10_000_000, 99_000_000), username=f"seedd{random.randint(0, 10**9)}", password_hash="x"))
        s.commit()
    with TestClient(app) as c:
        yield c
    for cid in sh("docker", "ps", "-aq", "--filter", "label=labbox=true", "--filter", "name=lab-u[0-9]{8}-").stdout.split():
        sh("docker", "rm", "-f", cid)
    for net in sh("docker", "network", "ls", "-q", "--filter", "label=labbox=true", "--filter", "name=labnet-u[0-9]{8}-").stdout.split():
        sh("docker", "network", "rm", net)


def signup(client: TestClient, name: str) -> tuple[dict, int]:
    r = client.post("/api/auth/signup", json={"username": f"{name}{random.randint(0, 10**6)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user"]["id"]


@pytest.fixture(scope="module")
def pg_user(client: TestClient) -> tuple[dict, int]:
    h, uid = signup(client, "pg")
    r = client.post(f"/api/labs/{PG_LAB}/workspace/start", headers=h)
    assert r.status_code == 200, r.text
    return h, uid


def names(uid: int) -> tuple[str, str, str]:
    ws = f"lab-u{uid}-{PG_LAB}"
    return ws, f"{ws}-db", f"labnet-u{uid}-{PG_LAB}"


# ---------- services ----------


def test_services_private_network_and_security(client: TestClient, pg_user):
    h, uid = pg_user
    ws, db, net = names(uid)
    assert inspect("network", net)["Internal"] is True  # no internet

    info = inspect("container", db)
    host = info["HostConfig"]
    assert info["Config"]["User"] == "1000:1000"
    assert host["CapDrop"] == ["ALL"] and not host["CapAdd"] and host["SecurityOpt"] == ["no-new-privileges:true"]
    assert host["Memory"] == 768 * 1024 * 1024 and host["PidsLimit"] == 256 and not host["Privileged"]
    assert list(info["NetworkSettings"]["Networks"]) == [net]
    assert "db" in info["NetworkSettings"]["Networks"][net]["Aliases"]

    assert list(inspect("container", ws)["NetworkSettings"]["Networks"]) == [net]  # network: lab only
    assert sh("docker", "exec", ws, "pg_isready", "-h", "db").returncode == 0
    assert sh("docker", "exec", ws, "curl", "-sS", "-m", "3", "https://example.com").returncode != 0

    status = client.get(f"/api/labs/{PG_LAB}/workspace/status", headers=h).json()
    assert status["status"] == "running" and status["services"] == [{"name": "db", "status": "running"}]

    # Database files live next to the workspace, never inside /workspace or the file tree.
    data = get_settings().VOLUMES_DIR / f"u{uid}" / f"{PG_LAB}.services" / "db"
    assert (data / "PG_VERSION").is_file()
    tree = client.get(f"/api/labs/{PG_LAB}/files", headers=h).json()
    assert sorted(n["name"] for n in tree) == ["README.md", "checkout.sql"]


def test_setup_runs_once(client: TestClient, pg_user):
    h, uid = pg_user
    ws, _, _ = names(uid)
    first = client.post(f"/api/labs/{PG_LAB}/chapters/{PG_CH}/setup", headers=h).json()
    assert first["ran"] is True and first["setup_done"] is True and first["started_at"]
    again = client.post(f"/api/labs/{PG_LAB}/chapters/{PG_CH}/setup", headers=h).json()
    assert again["ran"] is False and again["started_at"] == first["started_at"]
    assert psql(ws, "SELECT count(*) FROM orders") == "1000000"
    assert psql(ws, "SELECT count(*) FROM pg_indexes WHERE tablename = 'orders' AND indexdef LIKE '%customer_id%'") == "0"
    # The setup script itself is not readable by the learner.
    assert sh("docker", "exec", ws, "cat", "/lab/setup/01.sh").returncode != 0


def test_live_check_fake_result_then_fix_with_incident_bonus(client: TestClient, pg_user):
    h, uid = pg_user
    ws, _, _ = names(uid)
    # Learner code printing a fake result has no effect: the live checker never runs it.
    fake = 'print(\'@@RESULT {"task": "add_index", "passed": true, "message": "trust me"}\')\n'
    client.put(f"/api/labs/{PG_LAB}/files/content", headers=h, json={"path": "run_checks.sh", "content": "python3 -c \"" + fake + "\"\n"})
    client.put(f"/api/labs/{PG_LAB}/files/content", headers=h, json={"path": "check.py", "content": fake})
    res = client.post(f"/api/labs/{PG_LAB}/check", headers=h, json={"chapter_id": PG_CH}).json()
    assert res["passed_count"] == 0 and "Seq Scan" in res["results"][0]["message"]
    assert res["results"][0]["expected"] == "an index scan"
    assert res["metrics"][0]["name"] == "lookup_ms"

    psql(ws, "CREATE INDEX ON orders (customer_id)")
    res = client.post(f"/api/labs/{PG_LAB}/check", headers=h, json={"chapter_id": PG_CH}).json()
    assert res["passed_count"] == 1, res["results"]
    kinds = {a["kind"]: a["amount"] for a in res["xp_awarded"]}
    assert kinds == {"task": 50, "incident": 25, "chapter": 50, "lab": 200}


def test_incident_bonus_needs_the_timer(client: TestClient):
    """Fixed after the timer: no bonus (the clock is moved instead of waiting 20 minutes)."""
    from app import engagement, labs
    from app.models import ChapterProgress

    h, uid = signup(client, "late")
    lab = labs.get_lab(PG_LAB)
    with Session(engine) as s:
        s.add(ChapterProgress(user_id=uid, lab_id=PG_LAB, chapter_id=PG_CH, started_at=utcnow() - timedelta(minutes=16)))
        s.commit()
        got = engagement.award_for_check(s, uid, lab, PG_CH, {"add_index": True})
    assert "incident" not in {a.kind for a in got}


def test_reaper_stops_the_group_and_data_survives(client: TestClient, pg_user):
    h, uid = pg_user
    ws, db, _ = names(uid)
    with Session(engine) as s:
        stopped = containers.stop_idle(s, older_than=utcnow() + timedelta(minutes=1))
    assert ws in stopped
    assert inspect("container", ws)["State"]["Running"] is False
    assert inspect("container", db)["State"]["Running"] is False

    assert client.post(f"/api/labs/{PG_LAB}/workspace/start", headers=h).status_code == 200
    assert inspect("container", db)["State"]["Running"] is True
    assert psql(ws, "SELECT count(*) FROM orders") == "1000000"
    assert psql(ws, "SELECT count(*) FROM pg_indexes WHERE tablename = 'orders' AND indexdef LIKE '%customer_id%'") == "1"


def test_stop_route_stops_services_too(client: TestClient, pg_user):
    h, uid = pg_user
    _, db, _ = names(uid)
    client.post(f"/api/labs/{PG_LAB}/workspace/stop", headers=h)
    assert inspect("container", db)["State"]["Running"] is False
    client.post(f"/api/labs/{PG_LAB}/workspace/start", headers=h)
    assert inspect("container", db)["State"]["Running"] is True


def test_reset_wipes_service_data_and_setup_runs_again(client: TestClient, pg_user):
    h, uid = pg_user
    ws, _, _ = names(uid)
    assert client.post(f"/api/labs/{PG_LAB}/workspace/reset", headers=h).status_code == 200
    assert psql(ws, "SELECT to_regclass('public.orders') IS NULL") == "t"
    assert client.post(f"/api/labs/{PG_LAB}/chapters/{PG_CH}/setup", headers=h).json()["ran"] is True
    assert psql(ws, "SELECT count(*) FROM orders") == "1000000"


# ---------- preview ----------

ECHO_SERVER = """
import asyncio, websockets
async def echo(ws):
    async for m in ws:
        await ws.send(m)
async def main():
    async with websockets.serve(echo, "0.0.0.0", 8000):
        await asyncio.Future()
asyncio.run(main())
"""


def ticket(client: TestClient, h: dict) -> str:
    r = client.post(f"/api/labs/{API_LAB}/preview/ticket", headers=h)
    assert r.status_code == 200 and r.json()["ports"][0]["port"] == 8000
    set_cookie = r.headers["set-cookie"]
    assert "HttpOnly" in set_cookie and "SameSite=strict" in set_cookie and "Path=/preview" in set_cookie
    token = r.cookies["labbox_preview"]
    client.cookies.clear()  # each request below says explicitly whose cookie it carries
    return token


def wait_http(client: TestClient, cookie: str, path: str = "/") -> int:
    code = 0
    for _ in range(40):
        code = client.get(f"/preview/{API_LAB}/8000{path}", headers={"cookie": f"labbox_preview={cookie}"}).status_code
        if code != 502:
            return code
        time.sleep(0.25)
    return code


def test_preview_proxy(client: TestClient):
    ha, uid_a = signup(client, "prevA")
    hb, _ = signup(client, "prevB")
    client.post(f"/api/labs/{API_LAB}/workspace/start", headers=ha)
    ws_a = f"lab-u{uid_a}-{API_LAB}"
    # The FastAPI course keeps each chapter in its own folder (28 November); chapter 1's appears first.
    sh("docker", "exec", "-d", "-u", "1000", "-w", "/workspace/01-first-api", ws_a, "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000")
    ca, cb = ticket(client, ha), ticket(client, hb)

    assert wait_http(client, ca) == 200
    r = client.get(f"/preview/{API_LAB}/8000/", headers={"cookie": f"labbox_preview={ca}"})
    assert r.json() == {"message": "Lostdesk is open. Try /items"}
    assert client.get(f"/preview/{API_LAB}/8000/items", headers={"cookie": f"labbox_preview={ca}"}).status_code == 404

    # No cookie, a broken cookie, a login token instead of a preview ticket: all refused.
    assert client.get(f"/preview/{API_LAB}/8000/").status_code == 403
    assert client.get(f"/preview/{API_LAB}/8000/", headers={"cookie": "labbox_preview=nope"}).status_code == 403
    login = ha["Authorization"].split()[1]
    assert client.get(f"/preview/{API_LAB}/8000/", headers={"cookie": f"labbox_preview={login}"}).status_code == 403
    # ...and the preview ticket is not a login either.
    assert client.get("/api/me", headers={"Authorization": f"Bearer {ca}"}).status_code == 401
    # Only ports listed in the lab's preview.
    assert client.get(f"/preview/{API_LAB}/5432/", headers={"cookie": f"labbox_preview={ca}"}).status_code == 403

    # B only ever reaches B's own machine: not running yet (503), then running with no app (502).
    assert client.get(f"/preview/{API_LAB}/8000/", headers={"cookie": f"labbox_preview={cb}"}).status_code == 503
    client.post(f"/api/labs/{API_LAB}/workspace/start", headers=hb)
    assert client.get(f"/preview/{API_LAB}/8000/", headers={"cookie": f"labbox_preview={cb}"}).status_code == 502

    # WebSocket pass-through (A swaps the app for a tiny echo server on the same port).
    sh("docker", "exec", ws_a, "pkill", "-f", "uvicorn")
    sh("docker", "exec", "-d", "-u", "1000", ws_a, "python3", "-c", ECHO_SERVER)
    time.sleep(1.5)
    with client.websocket_connect(f"/preview/{API_LAB}/8000/echo", headers={"cookie": f"labbox_preview={ca}"}) as wsock:
        wsock.send_text("ek vada pav")
        assert wsock.receive_text() == "ek vada pav"


def test_service_data_dir_is_outside_workspace(pg_user):
    _, uid = pg_user
    root = Path(get_settings().VOLUMES_DIR) / f"u{uid}"
    assert not (root / PG_LAB / ".services").exists() and (root / f"{PG_LAB}.services").is_dir()
