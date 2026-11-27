"""End to end tests against real Docker. Run with: pytest -m docker

Needs the Docker daemon and the lab images (bash scripts/build_lab_images.sh).
"""
import json
import random
import subprocess
import time
from collections.abc import Iterator

import pytest

pytestmark = pytest.mark.docker

docker = pytest.importorskip("docker")


def _docker_ready() -> bool:
    try:
        c = docker.from_env()
        c.ping()
        c.images.get("labbox/python-basics:v1")
        c.images.get("labbox/java-basics:v1")
        return True
    except Exception:
        return False


if not _docker_ready():
    pytest.skip("Docker or lab images not available", allow_module_level=True)

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app import labs  # noqa: E402
from app.db import engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402

PY_SOLVED = {
    "02-functions/greet.py": 'def greet(name):\n    return f"Hello, {name}!"\n',
    "02-functions/math_utils.py": "def add(a, b):\n    return a + b\n\n\ndef is_even(n):\n    return n % 2 == 0\n",
}
JAVA_SOLVED = """public class Greeter {
    public static String greet(String name) { return "Hello, " + name + "!"; }
    public static int longestWord(String s) {
        int best = 0;
        for (String w : s.split(" ")) best = Math.max(best, w.length());
        return best;
    }
    public static void main(String[] args) { System.out.println(greet("Asha")); }
}
"""


def docker_cli(*args: str) -> str:
    return subprocess.run(["docker", *args], capture_output=True, text=True).stdout.strip()


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    init_db()
    # Start ids at a random high number so container names never clash with a dev database
    # on the same Docker host (lab-u1-python-basics may already exist).
    with Session(engine) as s:
        s.add(User(id=random.randint(10_000_000, 99_000_000), username=f"seed{random.randint(0, 10**9)}", password_hash="x"))
        s.commit()
    with TestClient(app) as c:
        yield c
    for cid in docker_cli("ps", "-aq", "--filter", "label=labbox=true", "--filter", "name=lab-u[0-9]{8}-").split():
        subprocess.run(["docker", "rm", "-f", cid], capture_output=True)


def signup(client: TestClient, name: str) -> tuple[dict, int]:
    r = client.post("/api/auth/signup", json={"username": f"{name}{random.randint(0, 10**6)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    body = r.json()
    return {"Authorization": f"Bearer {body['token']}"}, body["user"]["id"]


@pytest.fixture(scope="module")
def user(client: TestClient) -> tuple[dict, int]:
    return signup(client, "alice")


def write(client: TestClient, h: dict, lab: str, path: str, content: str) -> None:
    r = client.put(f"/api/labs/{lab}/files/content", headers=h, json={"path": path, "content": content})
    assert r.status_code == 200, r.text


def check(client: TestClient, h: dict, lab: str, chapter: str) -> dict:
    r = client.post(f"/api/labs/{lab}/check", headers=h, json={"chapter_id": chapter})
    assert r.status_code == 200, r.text
    return r.json()


def test_health_and_auth(client: TestClient, user):
    health = client.get("/api/health").json()
    assert {"ok": True, "docker": True}.items() <= health.items()  # the original fields, unchanged
    assert health["database"] is True and health["shared_state"] is True  # added in Phase H6
    assert client.get("/api/labs").status_code == 401
    h, uid = user
    assert client.get("/api/me", headers=h).json()["id"] == uid
    assert {"python-basics", "java-basics"} <= {lab["id"] for lab in client.get("/api/labs", headers=h).json()}


def test_start_workspace(client: TestClient, user):
    h, uid = user
    r = client.post("/api/labs/python-basics/workspace/start", headers=h)
    assert r.json() == {"status": "running", "container": f"lab-u{uid}-python-basics"}
    name = f"lab-u{uid}-python-basics"
    info = json.loads(docker_cli("inspect", name))[0]
    host = info["HostConfig"]
    assert info["State"]["Running"]
    assert info["Config"]["User"] == "1000:1000"
    assert host["CapDrop"] == ["ALL"] and host["SecurityOpt"] == ["no-new-privileges:true"]
    assert host["PidsLimit"] == 256 and host["Memory"] == 512 * 1024 * 1024 and not host["Privileged"]
    assert not any("docker.sock" in b for b in host["Binds"])
    tree = client.get("/api/labs/python-basics/files", headers=h).json()
    # One folder per chapter, shown one chapter at a time (plan A, 27 November): a new learner sees chapter 1's only,
    # and opening chapter 2 (the lab page's chapter focus) brings its folder in.
    assert {n["name"] for n in tree} == {"01-first-program"}
    assert client.post("/api/labs/python-basics/chapters/01-functions/focus", json={}, headers=h).status_code == 200
    assert {"01-first-program", "02-functions"} <= {n["name"] for n in client.get("/api/labs/python-basics/files", headers=h).json()}
    assert client.get("/api/labs/python-basics/workspace/status", headers=h).json()["status"] == "running"


def test_write_file_visible_in_container(client: TestClient, user):
    h, uid = user
    write(client, h, "python-basics", "02-functions/greet.py", "# edited from the API\n")
    assert docker_cli("exec", f"lab-u{uid}-python-basics", "cat", "/workspace/02-functions/greet.py") == "# edited from the API"
    r = client.get("/api/labs/python-basics/files/content", headers=h, params={"path": "02-functions/greet.py"})
    assert r.json()["content"] == "# edited from the API\n"


def test_check_fail_then_pass(client: TestClient, user):
    h, _ = user
    assert client.post("/api/labs/python-basics/workspace/reset", headers=h).status_code == 200
    res = check(client, h, "python-basics", "01-functions")
    assert (res["passed_count"], res["total_count"]) == (0, 3)
    assert all(not t["passed"] and t["message"] for t in res["results"])

    for path, content in PY_SOLVED.items():
        write(client, h, "python-basics", path, content)
    res = check(client, h, "python-basics", "01-functions")
    assert (res["passed_count"], res["total_count"]) == (3, 3), res
    assert res["duration_ms"] < 5000

    progress = {lab["id"]: lab["progress"] for lab in client.get("/api/labs", headers=h).json()}
    total = sum(len(c.tasks) for c in labs.get_lab("python-basics").chapters)
    assert progress["python-basics"] == {"passed_tasks": 3, "total_tasks": total}
    assert len(client.get("/api/labs/python-basics/checks?limit=10", headers=h).json()) == 2
    assert docker_cli("ps", "-aq", "--filter", "label=labbox.kind=check", "--filter", "label=labbox.user=" + str(user[1])) == ""


def test_check_timeout_cleans_up(client: TestClient, user, monkeypatch):
    h, uid = user
    monkeypatch.setattr(labs.get_lab("python-basics").check, "timeout_seconds", 3)
    write(client, h, "python-basics", "02-functions/greet.py", "while True:\n    pass\n")
    res = check(client, h, "python-basics", "01-functions")
    assert res["passed_count"] == 0
    assert all("Timed out after 3 seconds" in t["message"] for t in res["results"])
    assert docker_cli("ps", "-aq", "--filter", "label=labbox.kind=check", "--filter", f"label=labbox.user={uid}") == ""


def test_java_check(client: TestClient, user):
    h, _ = user
    assert check(client, h, "java-basics", "01-methods")["passed_count"] == 0
    write(client, h, "java-basics", "02-methods/Greeter.java", JAVA_SOLVED)
    res = check(client, h, "java-basics", "01-methods")
    assert (res["passed_count"], res["total_count"]) == (2, 2), res


@pytest.mark.parametrize("path", ["../x", "a/../../x", "/etc/passwd", "../../u1/python-basics/greet.py"])
def test_traversal_is_403(client: TestClient, user, path):
    h, _ = user
    assert client.get("/api/labs/python-basics/files/content", headers=h, params={"path": path}).status_code == 403
    r = client.put("/api/labs/python-basics/files/content", headers=h, json={"path": path, "content": "x"})
    assert r.status_code == 403
    assert client.delete("/api/labs/python-basics/files", headers=h, params={"path": path}).status_code == 403


def test_users_are_isolated(client: TestClient, user):
    h, _ = user
    h2, uid2 = signup(client, "bob")
    write(client, h, "python-basics", "secret.py", "alice only\n")
    r = client.get("/api/labs/python-basics/files/content", headers=h2, params={"path": "secret.py"})
    assert r.status_code == 404
    names = {n["name"] for n in client.get("/api/labs/python-basics/files", headers=h2).json()}
    assert "secret.py" not in names and "01-first-program" in names


def test_terminal_echo(client: TestClient, user):
    h, uid = user
    token = h["Authorization"].split()[1]
    with client.websocket_connect(f"/ws/terminal/python-basics?token={token}") as ws:
        assert ws.receive_json() == {"type": "status", "message": "connected"}
        ws.send_text(json.dumps({"type": "resize", "cols": 100, "rows": 30}))
        ws.send_text(json.dumps({"type": "input", "data": "echo hel''lo; id -u\r"}))
        out = b""
        deadline = time.time() + 10
        while b"\rhello\r\n1000" not in out and time.time() < deadline:
            msg = ws.receive()
            out += msg.get("bytes") or b""
        assert b"\rhello\r\n1000" in out, out[-500:]
        ws.send_text(json.dumps({"type": "input", "data": "exit\r"}))
        while True:
            msg = ws.receive()
            if msg.get("text"):
                assert json.loads(msg["text"]) == {"type": "exit"}
                break
    # Closing the terminal does not stop the machine.
    assert docker_cli("inspect", "-f", "{{.State.Running}}", f"lab-u{uid}-python-basics") == "true"


def test_terminal_requires_token(client: TestClient):
    with client.websocket_connect("/ws/terminal/python-basics?token=nope") as ws:
        assert ws.receive_json()["type"] == "error"
        msg = ws.receive()
        assert msg["type"] == "websocket.close" and msg["code"] == 4401


def test_stop_and_restart_keeps_files(client: TestClient, user):
    h, uid = user
    write(client, h, "python-basics", "keep.txt", "still here\n")
    assert client.post("/api/labs/python-basics/workspace/stop", headers=h).json()["status"] == "stopped"
    assert client.get("/api/labs/python-basics/workspace/status", headers=h).json()["status"] == "stopped"
    client.post("/api/labs/python-basics/workspace/start", headers=h)
    assert docker_cli("exec", f"lab-u{uid}-python-basics", "cat", "/workspace/keep.txt") == "still here"


def test_check_v2_fields_and_task_progress(client: TestClient):
    """Failed tasks carry expected/actual; a pass is recorded in task_progress once."""
    from app.models import TaskProgress

    h, uid = signup(client, "v2check")
    client.post("/api/labs/java-basics/workspace/start", headers=h)
    res = check(client, h, "java-basics", "01-methods")
    greet = next(r for r in res["results"] if r["task"] == "greet")
    assert greet["passed"] is False
    assert (greet["expected"], greet["actual"]) == ('"Hello, Asha!"', "null")

    write(client, h, "java-basics", "02-methods/Greeter.java", JAVA_SOLVED)
    assert check(client, h, "java-basics", "01-methods")["passed_count"] == 2
    with Session(engine) as s:
        row = s.get(TaskProgress, {"user_id": uid, "lab_id": "java-basics", "task_id": "greet"})
        assert row is not None and row.passed and row.first_passed_at is not None
        first = row.first_passed_at
    check(client, h, "java-basics", "01-methods")
    with Session(engine) as s:
        assert s.get(TaskProgress, {"user_id": uid, "lab_id": "java-basics", "task_id": "greet"}).first_passed_at == first


def test_real_check_awards_xp_once(client: TestClient):
    h, uid = signup(client, "xp")
    client.post("/api/labs/python-basics/workspace/start", headers=h)
    client.post("/api/labs/python-basics/chapters/01-functions/focus", json={}, headers=h)  # the learner opens chapter 2
    for path, content in PY_SOLVED.items():
        write(client, h, "python-basics", path, content)
    first = check(client, h, "python-basics", "01-functions")
    # Chapter 1 of a multi-chapter course: its tasks and the chapter bonus (the lab bonus comes at the end).
    assert sorted(a["kind"] for a in first["xp_awarded"]) == ["chapter", "task", "task", "task"]
    assert check(client, h, "python-basics", "01-functions")["xp_awarded"] == []
    assert client.get("/api/me/stats", headers=h).json()["xp_total"] == 3 * 20 + 50
