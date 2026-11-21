"""AI code completion in the editor (fake provider): suggestions, the solution guard, and its own
limits, separate from the tutor's budget."""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import labs, llm_gateway, shared, tutor
from app.config import get_settings
from app.db import engine
from app.main import app
from app.models import LlmRequest

URL = "/api/labs/python-basics/complete"


@pytest.fixture
def client() -> TestClient:
    shared.forget_hits()
    with TestClient(app) as c:
        yield c


def login(client: TestClient) -> tuple[dict[str, str], int]:
    body = client.post("/api/auth/signup", json={"username": f"cc{uuid.uuid4().hex[:8]}", "password": "secret123"}).json()
    return {"Authorization": f"Bearer {body['token']}"}, body["user"]["id"]


def test_suggestion_and_log(client: TestClient, monkeypatch):
    h, uid = login(client)
    seen = {}

    def model(prompt, suffix):
        seen["prompt"], seen["suffix"] = prompt, suffix
        return "total = 0\n    for x in items:\n        total += x\n\n\n"

    monkeypatch.setattr(llm_gateway, "fake_code_completion", model)
    r = client.post(URL, headers=h, json={"path": "sums.py", "prefix": "x" * 5000 + "\ndef total(items):\n    ", "suffix": "\n    return total\n"})
    assert r.status_code == 200
    assert r.json()["text"] == "total = 0\n    for x in items:\n        total += x"  # trailing blank lines trimmed
    assert len(seen["prompt"]) == 2000 and seen["suffix"].startswith("\n    return total")
    with Session(engine) as s:
        row = s.exec(select(LlmRequest).where(LlmRequest.user_id == uid)).one()
    assert (row.endpoint, row.alias) == ("completion", "lab-code")


def test_suggestion_stops_at_the_first_blank_line(client: TestClient, monkeypatch):
    h, _ = login(client)
    monkeypatch.setattr(llm_gateway, "fake_code_completion", lambda p, s: "return r.incr(page)\n\ndef extra():\n    return 1")
    assert client.post(URL, headers=h, json={"path": "a.py", "prefix": "def f(page):\n    ", "suffix": ""}).json()["text"] == "return r.incr(page)"


def test_fences_are_stripped_and_similar_code_is_allowed(client: TestClient, monkeypatch):
    h, _ = login(client)
    monkeypatch.setattr(llm_gateway, "fake_code_completion", lambda p, s: "```python\nreturn n % 2 != 0\n```")
    # is_odd is not the task (is_even is), so its line is a fine suggestion.
    r = client.post("/api/labs/python-basics/complete", headers=h, json={"path": "02-functions/math_utils.py", "prefix": "def is_odd(n):\n    ", "suffix": ""})
    assert r.json()["text"] == "return n % 2 != 0"


def test_solution_lines_are_never_suggested(client: TestClient, monkeypatch):
    h, _ = login(client)
    lab = labs.get_lab("python-basics")
    line = next(l for l in tutor.solution_lines(lab) if l.startswith("returnf"))  # the greet solution
    monkeypatch.setattr(llm_gateway, "fake_code_completion", lambda p, s: 'return f"Hello, {name}!"')
    r = client.post(URL, headers=h, json={"path": "02-functions/greet.py", "prefix": "def greet(name):\n    ", "suffix": ""})
    assert line and r.json()["text"] == ""
    # The model finishing a line the learner started is caught too.
    monkeypatch.setattr(llm_gateway, "fake_code_completion", lambda p, s: '"Hello, {name}!"')
    assert client.post(URL, headers=h, json={"path": "02-functions/greet.py", "prefix": "def greet(name):\n    return f", "suffix": ""}).json()["text"] == ""


def test_completion_has_its_own_limits(client: TestClient, monkeypatch):
    h, _ = login(client)
    monkeypatch.setattr(get_settings(), "LLM_DAILY_TOKENS", 1)  # the tutor's budget is gone...
    body = {"path": "a.py", "prefix": "def f():\n    ", "suffix": ""}
    assert client.post(URL, headers=h, json=body).json()["text"] == "pass"  # ...completion still works
    monkeypatch.setattr(get_settings(), "LLM_COMPLETION_DAILY_TOKENS", 1)
    r = client.post(URL, headers=h, json=body)
    assert r.status_code == 429 and "code completion for today is used up" in r.json()["detail"]


def test_switched_off(client: TestClient, monkeypatch):
    h, _ = login(client)
    assert client.get("/api/ai/config", headers=h).json() == {"completion": True}
    monkeypatch.setattr(get_settings(), "AI_COMPLETION", False)
    assert client.get("/api/ai/config", headers=h).json() == {"completion": False}
    assert client.post(URL, headers=h, json={"path": "a.py", "prefix": "x", "suffix": ""}).json()["text"] == ""
