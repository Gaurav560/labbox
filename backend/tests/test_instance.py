"""Two LabBoxes on one Docker (owner, 27 November: the live site runs on the laptop beside development).
INSTANCE names one of them: its machines, checks and networks get their own names and label, and each instance's
cleanup and limits see only their own. Unnamed: the names of before."""
import uuid

import pytest
from fastapi.testclient import TestClient

from app import containers, services
from app.config import get_settings
from app.models import Workspace


@pytest.fixture
def instance(monkeypatch):
    def use(name: str) -> None:
        monkeypatch.setenv("INSTANCE", name)
        get_settings.cache_clear()

    yield use
    monkeypatch.setenv("INSTANCE", "")
    get_settings.cache_clear()


class Fake:
    def __init__(self, labels: dict[str, str], network: bool = False):
        self.attrs = {"Labels": labels} if network else {"Config": {"Labels": labels}}


def test_unnamed_instance_keeps_the_old_names(instance):
    instance("")
    assert containers.container_name(7, "redis-in-practice") == "lab-u7-redis-in-practice"
    assert services.lab_network_name(7, "redis-in-practice") == "labnet-u7-redis-in-practice"
    assert "labbox.instance" not in containers.labels("workspace", 7, "x")
    assert containers.label_filter("labbox.kind=workspace") == ["labbox=true", "labbox.kind=workspace"]


def test_named_instance_names_and_labels_its_own(instance):
    instance("prod")
    assert containers.container_name(1, "langgraph") == "lab-prod-u1-langgraph"
    ws = Workspace(user_id=1, lab_id="langgraph", container_name="lab-prod-u1-langgraph", volume_path="/tmp/x")
    assert services.network_name(ws) == "labnet-prod-u1-langgraph"
    assert containers.labels("check", 1, "langgraph")["labbox.instance"] == "prod"
    assert services._labels("service", ws)["labbox.instance"] == "prod"
    assert containers.label_filter("labbox.kind=check") == ["labbox=true", "labbox.kind=check", "labbox.instance=prod"]


def test_each_instance_sees_only_its_own(instance):
    dev, live = Fake({"labbox": "true"}), Fake({"labbox": "true", "labbox.instance": "prod"})
    net_dev, net_live = Fake({"labbox": "true"}, network=True), Fake({"labbox.instance": "prod"}, network=True)
    instance("")
    assert containers.mine([dev, live, net_dev, net_live]) == [dev, net_dev]
    instance("prod")
    assert containers.mine([dev, live, net_dev, net_live]) == [live, net_live]


def test_instance_name_is_checked(instance):
    for bad in ("Prod", "1prod", "pro-d", "a" * 13):
        instance(bad)
        with pytest.raises(Exception):
            get_settings()
    instance("prod2")
    assert get_settings().INSTANCE == "prod2"


def test_health_reports_the_release(monkeypatch):
    from app.main import app

    monkeypatch.setenv("RELEASE", "abc1234")
    get_settings.cache_clear()
    try:
        body = TestClient(app).get("/api/health").json()
        assert body["ok"] is True and body["release"] == "abc1234"
    finally:
        monkeypatch.setenv("RELEASE", "")
        get_settings.cache_clear()


@pytest.mark.docker
def test_cleanup_never_crosses_instances(instance):
    """A real container of another instance: invisible to this one's machine list, visible to its own."""
    client = containers.client()
    name = f"labbox-instance-test-{uuid.uuid4().hex[:8]}"
    c = client.containers.run("alpine/socat:1.8.0.3", entrypoint="sleep", command="60", name=name, detach=True,
                              labels={"labbox": "true", "labbox.kind": "workspace", "labbox.user": "99999999",
                                      "labbox.lab": "x", "labbox.instance": "zzother"})
    try:
        instance("")
        assert name not in containers.running_workspace_containers()
        instance("zzother")
        assert name in containers.running_workspace_containers()
    finally:
        c.remove(force=True)


def test_auth_options_say_whether_signup_is_open(monkeypatch):
    """The login page asks; an invite-only site (the live site on the laptop) shows a note instead of Sign up."""
    from app.main import app

    client = TestClient(app)
    assert client.get("/api/auth/options").json() == {"signup": True}
    monkeypatch.setenv("ALLOW_SIGNUP", "false")
    get_settings.cache_clear()
    try:
        assert client.get("/api/auth/options").json() == {"signup": False}
        r = client.post("/api/auth/signup", json={"username": "invitedonly", "password": "secret123"})
        assert r.status_code == 403
    finally:
        monkeypatch.setenv("ALLOW_SIGNUP", "true")
        get_settings.cache_clear()
