"""Lesson progress API: steps in the chapter response, step position, hint ladder. No Docker needed."""
import random

import pytest
from fastapi.testclient import TestClient

from app import labs
from app.config import get_settings
from app.db import init_db
from app.main import app

LAB, CH = "python-basics", "01-functions"


def _ch1_steps():
    """Python from zero, chapter 1, parsed from its file: tests find steps by type, not by number, so the
    lesson can grow (a history step, more examples) without breaking them."""
    from pathlib import Path

    from app.lessons import parse_steps

    return parse_steps((Path(__file__).resolve().parents[2] / "labs/python-basics/chapters/01-functions.md").read_text())


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
    n = len(_ch1_steps())
    assert first == {"current_step": 0, "step_count": n, "hints": {}, "predicts": {}, "xp_earned": 0, "designs": {}}
    assert client.put(url, json={"current_step": 4}, headers=h).json()["current_step"] == 4
    assert client.get(url, headers=h).json()["current_step"] == 4
    # Past the end is clamped to the last step; negative is rejected.
    assert client.put(url, json={"current_step": 99}, headers=h).json()["current_step"] == n - 1  # clamped to the last step
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


def test_task_card_examples_are_served(client: TestClient):
    h = auth(client)
    tasks = client.get("/api/labs/java-basics", headers=h).json()["chapters"][0]["tasks"]
    assert tasks[0]["examples"][0] == {"call": 'greet("Asha")', "gives": '"Hello, Asha!"', "note": None}
    py = client.get(f"/api/labs/{LAB}", headers=h).json()["chapters"][0]["tasks"][0]
    assert py["examples"][0]["call"] == 'greet("Asha")'
    other = client.get("/api/labs/sql-from-zero", headers=h).json()["chapters"][0]["tasks"][0]
    assert other["examples"] == []  # optional: tasks without a card still work


def test_next_starts_new_learners_and_continues_the_rest(client: TestClient):
    h = auth(client)
    # A new learner with no goal: the coding basics, chapter 1, step 1.
    first = client.get("/api/me/next", headers=h).json()
    assert (first["kind"], first["lab_id"], first["chapter_number"], first["step"]) == ("start", "python-basics", 1, 1)
    assert first["reason"]

    # After moving through a chapter: continue exactly there (steps are 1-based for people).
    url = "/api/labs/java-basics/chapters/03-decisions/progress"
    assert client.put(url, json={"current_step": 4}, headers=h).status_code == 200
    nxt = client.get("/api/me/next", headers=h).json()
    assert (nxt["kind"], nxt["lab_id"], nxt["chapter_id"], nxt["chapter_number"], nxt["step"]) == ("continue", "java-basics", "03-decisions", 3, 5)
    assert nxt["steps"] > 5 and nxt["chapters"] == 13

    # The most recently touched chapter wins.
    client.put(f"/api/labs/{LAB}/chapters/{CH}/progress", json={"current_step": 2}, headers=h)
    assert client.get("/api/me/next", headers=h).json()["lab_id"] == LAB

    # Opening a chapter counts too, even without moving a step (reading only).
    assert client.get("/api/labs/java-basics/chapters/03-decisions/progress", headers=h).status_code == 200
    back = client.get("/api/me/next", headers=h).json()
    assert (back["lab_id"], back["chapter_id"], back["step"]) == ("java-basics", "03-decisions", 5)
    assert client.get("/api/me/next").status_code == 401

    # One lab's own answer (its course page): where you were in that lab, else its first chapter.
    assert client.get("/api/me/next?lab=java-basics", headers=h).json()["chapter_id"] == "03-decisions"
    assert client.get(f"/api/me/next?lab={LAB}", headers=h).json()["chapter_id"] == CH
    fresh = client.get("/api/me/next?lab=go-basics", headers=h).json()
    assert (fresh["kind"], fresh["chapter_id"], fresh["step"]) == ("start", "01-first-program", 1)
    assert client.get("/api/me/next?lab=nope", headers=h).status_code == 404
