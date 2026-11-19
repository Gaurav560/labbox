"""Phase E end to end against real Docker: an llm.enabled lab calls lab-chat with the OpenAI SDK using
only the injected env vars, through the relay on its private network, to a gateway served in this
test process (fake provider). Also: `lab requests`, a budget 429 inside the lab, and no provider key
anywhere in the container.

Needs the images: bash scripts/build_lab_images.sh
"""
import asyncio
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

pytestmark = pytest.mark.docker

docker = pytest.importorskip("docker")
IMAGES = ("labbox/ai-python:v1", "alpine/socat:1.8.0.3")


def _ready() -> bool:
    try:
        c = docker.from_env()
        for image in IMAGES:
            c.images.get(image)
        return True
    except Exception:
        return False


if not _ready():
    pytest.skip("Docker or the Phase E images are not available", allow_module_level=True)

import uvicorn  # noqa: E402

from app import containers, llm_gateway, services, workspace_files  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db import init_db  # noqa: E402
from app.labs import load_lab  # noqa: E402
from app.models import Workspace  # noqa: E402

FAKE_PROVIDER_KEY = "sk-provider-secret-never-in-a-lab-7f3a"
TEST_PORT = 19000  # not 9000, so a running dev backend's gateway does not get in the way

LAB_YAML = """\
id: ai-test-lab
title: AI test lab
image: labbox/ai-python:v1
resources: xs
llm: {enabled: true}
check: {command: ["true"]}
chapters:
  - {id: 01-x, title: X, file: chapters/01-x.md, tasks: [{id: t, title: T}]}
"""

SDK_CALL = """
from openai import OpenAI, RateLimitError
client = OpenAI()  # only the injected OPENAI_BASE_URL and OPENAI_API_KEY
try:
    r = client.chat.completions.create(model="lab-chat", messages=[{"role": "user", "content": "hello from the lab"}])
    print("REPLY:", r.choices[0].message.content)
except RateLimitError as e:
    print("LIMIT:", e.body["message"] if isinstance(e.body, dict) else e)
"""


@pytest.fixture
def gateway(monkeypatch) -> Iterator[None]:
    settings = get_settings()
    monkeypatch.setattr(settings, "LLM_GATEWAY_PORT", TEST_PORT)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", FAKE_PROVIDER_KEY)
    init_db()
    llm_gateway._recent.clear()
    server = uvicorn.Server(uvicorn.Config(llm_gateway.gateway_app, host=llm_gateway.bind_host(), port=TEST_PORT, log_level="warning", lifespan="off"))
    thread = threading.Thread(target=lambda: asyncio.run(server.serve()), daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)
    assert server.started, "the test gateway did not start"
    yield
    server.should_exit = True
    thread.join(5)


@pytest.fixture
def lab_group(gateway) -> Iterator[tuple[str, Workspace]]:
    tmp = Path(tempfile.mkdtemp(prefix="labbox-ai-"))
    folder = tmp / "ai-test-lab"
    (folder / "chapters").mkdir(parents=True)
    (folder / "lab.yaml").write_text(LAB_YAML)
    (folder / "chapters/01-x.md").write_text(":::step{type=task task=t title=T}\nDo it.\n:::\n")
    (folder / "starter").mkdir()
    (folder / "tests").mkdir()
    lab = load_lab(folder)
    vol = tmp / "ws"
    vol.mkdir()
    workspace_files.chown(vol)
    from sqlmodel import Session

    from app.db import engine
    from app.models import User

    with Session(engine) as s:
        u = User(username=f"ai{uuid.uuid4().hex[:8]}", password_hash="x")
        s.add(u)
        s.commit()
        s.refresh(u)
    ws = Workspace(user_id=u.id, lab_id=lab.id, container_name=f"labtest-ai-{uuid.uuid4().hex[:6]}", volume_path=str(vol))
    try:
        services.ensure_services(lab, ws)
        containers._create(lab, ws)
        yield ws.container_name, ws
    finally:
        for c in containers.client().containers.list(all=True, filters={"name": ws.container_name}):
            c.remove(force=True)
        services.remove_services(lab, ws, wipe_data=True)
        try:
            containers.client().networks.get(services.network_name(ws)).remove()
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


def run_in(container: str, *cmd: str) -> str:
    r = subprocess.run(["docker", "exec", "-u", "1000", container, *cmd], capture_output=True, text=True, timeout=60)
    return r.stdout + r.stderr


def test_lab_calls_lab_chat_with_only_env_vars(lab_group, monkeypatch):
    name, ws = lab_group
    out = run_in(name, "python", "-c", SDK_CALL)
    assert "REPLY: Fake reply to: hello from the lab" in out, out

    table = run_in(name, "lab", "requests")
    assert "lab-chat" in table and "Tokens used today" in table, table
    assert "hello from the lab" in run_in(name, "lab", "requests", "--last")

    # Budget used up: the SDK gets a 429 with a message a learner understands.
    monkeypatch.setattr(get_settings(), "LLM_DAILY_TOKENS", 1)
    out = run_in(name, "python", "-c", SDK_CALL)
    assert "LIMIT:" in out and "budget for today is used up" in out, out


def test_provider_keys_never_reach_the_container(lab_group):
    name, _ = lab_group
    env = run_in(name, "env")
    assert "OPENAI_BASE_URL=http://gateway:" in env and "OPENAI_API_KEY=" in env
    assert FAKE_PROVIDER_KEY not in env
    for cmd in (["ps", "auxe"], ["sh", "-c", "grep -rs sk-provider / --exclude-dir=proc --exclude-dir=sys 2>/dev/null | head -3"]):
        assert FAKE_PROVIDER_KEY not in run_in(name, *cmd)
    # The lab key is not a login: the main API refuses it.
    token = next(line.split("=", 1)[1] for line in env.splitlines() if line.startswith("OPENAI_API_KEY="))
    from fastapi.testclient import TestClient

    from app.main import app

    assert TestClient(app).get("/api/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_relay_is_locked_down(lab_group):
    _, ws = lab_group
    relay = containers.client().containers.get(services.relay_name(ws))
    hc = relay.attrs["HostConfig"]
    assert hc["CapDrop"] == ["ALL"] and hc["ReadonlyRootfs"] and relay.attrs["Config"]["User"] == "65534:65534"
    assert set(relay.attrs["NetworkSettings"]["Networks"]) == {services.network_name(ws), "bridge"}
