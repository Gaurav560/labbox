"""Lesson progress API: steps in the chapter response, step position, hint ladder. No Docker needed."""
import random

import pytest
from fastapi.testclient import TestClient

from app import labs
from app.config import get_settings
from app.db import init_db
from app.main import app

LAB, CH = "python-basics", "01-functions"


@pytest.fixture(scope="module")
def client() -> TestClient:
    # No lifespan (it would start the Docker reaper): load labs and the schema directly.
    labs.init_labs(get_settings().LABS_DIR)
    init_db()
    return TestClient(app)


def auth(client: TestClient) -> dict:
    r = client.post("/api/auth/signup", json={"username": f"prog{random.randint(0, 10**9)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_needs_login(client: TestClient):
    assert client.get(f"/api/labs/{LAB}/chapters/{CH}/progress").status_code == 401
    assert client.post(f"/api/labs/{LAB}/chapters/{CH}/tasks/greet/hint").status_code == 401


def test_chapter_has_steps_and_markdown(client: TestClient):
    h = auth(client)
    body = client.get(f"/api/labs/{LAB}/chapters/{CH}", headers=h).json()
    assert body["markdown"].startswith(":::step")  # raw markdown still served (old clients)
    types = [s["type"] for s in body["steps"]]
    assert types[0] == "story" and types[-1] == "recap" and "predict" in types
    # Hint text is never part of the chapter or lab payloads.
    hints = [hint for t in labs.get_lab(LAB).chapters[0].tasks for hint in t.hints]
    lab_body = client.get(f"/api/labs/{LAB}", headers=h).text
    for text in hints:
        assert text not in body["markdown"] and text not in lab_body


def test_step_position(client: TestClient):
    h = auth(client)
    url = f"/api/labs/{LAB}/chapters/{CH}/progress"
    first = client.get(url, headers=h).json()
    assert first == {"current_step": 0, "step_count": 9, "hints": {}}
    assert client.put(url, json={"current_step": 4}, headers=h).json()["current_step"] == 4
    assert client.get(url, headers=h).json()["current_step"] == 4
    # Past the end is clamped to the last step; negative is rejected.
    assert client.put(url, json={"current_step": 99}, headers=h).json()["current_step"] == 8
    assert client.put(url, json={"current_step": -1}, headers=h).status_code == 422
    # Another user starts at 0.
    assert client.get(url, headers=auth(client)).json()["current_step"] == 0


def test_unknown_lab_or_chapter(client: TestClient):
    h = auth(client)
    assert client.get(f"/api/labs/nope/chapters/{CH}/progress", headers=h).status_code == 404
    assert client.put(f"/api/labs/{LAB}/chapters/nope/progress", json={"current_step": 1}, headers=h).status_code == 404


def test_hint_ladder(client: TestClient):
    h = auth(client)
    url = f"/api/labs/{LAB}/chapters/{CH}/tasks/greet/hint"
    hints = labs.get_lab(LAB).chapters[0].tasks[0].hints
    xp = []
    for i in range(1, 4):
        r = client.post(url, headers=h).json()
        assert r["hints"] == hints[:i] and r["hints_left"] == 3 - i
        xp.append(r["xp"])
    assert xp == [16, 12, 8]  # 80%, 60%, 40% of 20
    again = client.post(url, headers=h).json()  # nothing left: stays at 3
    assert again["hints_left"] == 0 and len(again["hints"]) == 3

    progress = client.get(f"/api/labs/{LAB}/chapters/{CH}/progress", headers=h).json()
    assert progress["hints"] == {"greet": hints}
    task = client.get(f"/api/labs/{LAB}", headers=h).json()["chapters"][0]["tasks"][0]
    assert (task["id"], task["hint_count"], task["hints_used"], task["xp"]) == ("greet", 3, 3, 8)


def test_hint_for_task_of_other_chapter_or_lab(client: TestClient):
    h = auth(client)
    assert client.post(f"/api/labs/{LAB}/chapters/{CH}/tasks/longest_word/hint", headers=h).status_code == 404
    assert client.post(f"/api/labs/java-basics/chapters/{CH}/tasks/greet/hint", headers=h).status_code == 404
