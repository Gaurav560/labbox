"""VS Code in the lab against real Docker: it starts in the learner's machine as the learner, answers
only through the signed-in /ide proxy (with our default settings on the start page), refuses requests
without its token, and a lab without a network gets a private one (still no internet) so the proxy
can reach it.

Needs: bash scripts/openvscode.sh and the lab images.
"""
import ipaddress
import json
import random
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

pytestmark = pytest.mark.docker

docker = pytest.importorskip("docker")
IDE_DIR = Path("/srv/labbox/openvscode")


def _ready() -> bool:
    try:
        c = docker.from_env()
        c.images.get("labbox/python-basics:v1")
        c.images.get("labbox/linux-on-call:v1")
        return (IDE_DIR / "current" / "bin" / "openvscode-server").exists()
    except Exception:
        return False


if not _ready():
    pytest.skip("Docker, the lab images or openvscode-server (scripts/openvscode.sh) are not available", allow_module_level=True)

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app import ide, services  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db import engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402


def sh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), capture_output=True, text=True)


def inspect(kind: str, name: str) -> dict:
    return json.loads(sh("docker", kind, "inspect", name).stdout)[0]


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    settings = get_settings()
    before = (settings.IDE_ENABLED, settings.IDE_DIR)
    settings.IDE_ENABLED, settings.IDE_DIR = True, IDE_DIR
    init_db()
    with Session(engine) as s:  # high ids: never clash with containers of a dev database
        s.add(User(id=random.randint(10_000_000, 99_000_000), username=f"seedi{random.randint(0, 10**9)}", password_hash="x"))
        s.commit()
    with TestClient(app) as c:
        yield c
    settings.IDE_ENABLED, settings.IDE_DIR = before
    for cid in sh("docker", "ps", "-aq", "--filter", "label=labbox=true", "--filter", "name=lab-u[0-9]{8}-").stdout.split():
        sh("docker", "rm", "-f", cid)
    for net in sh("docker", "network", "ls", "-q", "--filter", "label=labbox=true", "--filter", "name=labnet-u[0-9]{8}-").stdout.split():
        sh("docker", "network", "rm", net)


def signup(client: TestClient, name: str) -> tuple[dict, int]:
    r = client.post("/api/auth/signup", json={"username": f"{name}{random.randint(0, 10**6)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user"]["id"]


def test_vscode_through_the_proxy(client: TestClient):
    h, uid = signup(client, "vs")
    r = client.post("/api/labs/python-basics/ide", headers=h)
    info = r.json()
    assert info["available"] and info["ready"], info
    assert info["url"].startswith("/ide/python-basics/?tkn=")

    # The token URL sets VS Code's own cookie, then the start page carries our defaults.
    page = client.get(info["url"], follow_redirects=True)
    assert page.status_code == 200 and "vscode-workbench-web-configuration" in page.text
    assert "security.workspace.trust.enabled" in page.text and "chat.disableAIFeatures" in page.text

    name = f"lab-u{uid}-python-basics"
    # VS Code runs inside the machine as the learner; the machine keeps every lockdown.
    procs = sh("docker", "exec", name, "ps", "-o", "user:12,args", "-u", "1000").stdout
    assert "server-main.js" in procs
    assert "server-main.js" not in sh("docker", "exec", name, "ps", "-o", "args", "-u", "0").stdout
    host = inspect("container", name)["HostConfig"]
    assert host["CapDrop"] == ["ALL"] and not host["Privileged"] and host["SecurityOpt"] == ["no-new-privileges:true"]
    assert host["Memory"] == (512 + get_settings().IDE_EXTRA_MEMORY_MB) * 1024 * 1024  # room for VS Code
    mounts = {m["Destination"]: m for m in inspect("container", name)["Mounts"]}
    assert mounts[ide.MOUNT]["RW"] is False  # the VS Code files are read-only

    # Straight to the machine without the token: refused.
    ip = services.container_ip(name)
    assert httpx.get(f"http://{ip}:{ide.PORT}{ide.base_path('python-basics')}/", timeout=5).status_code == 403


def test_a_learner_only_ever_reaches_their_own_vscode(client: TestClient):
    h1, _ = signup(client, "own")
    assert client.post("/api/labs/python-basics/ide", headers=h1).json()["ready"]
    # A second learner who never started this lab: the proxy resolves to their (missing) machine.
    client.cookies.clear()
    h2, _ = signup(client, "other")
    client.post("/api/labs/python-basics/preview/ticket", headers=h2)  # their own proxy cookie
    client.cookies.set("labbox_preview", client.cookies.get("labbox_preview") or "", path="/ide")
    r = client.get("/ide/python-basics/")
    assert r.status_code == 503 and "not running" in r.text
    client.cookies.clear()
    assert client.get("/ide/python-basics/").status_code == 403  # and no cookie at all: refused


def test_labs_without_network_get_a_private_one(client: TestClient):
    h, uid = signup(client, "net")
    assert client.post("/api/labs/linux-on-call/ide", headers=h).json()["ready"]
    net = f"labnet-u{uid}-linux-on-call"
    info = inspect("network", net)
    assert info["Internal"] is True  # still no internet
    # A small subnet from LabBox's own range, not a /16 from Docker's pool (which runs out at ~30 networks).
    subnet = ipaddress.ip_network(info["IPAM"]["Config"][0]["Subnet"])
    assert subnet.prefixlen == 28 and subnet.subnet_of(ipaddress.ip_network(get_settings().LAB_SUBNET_POOL))
    assert list(inspect("container", f"lab-u{uid}-linux-on-call")["NetworkSettings"]["Networks"]) == [net]
