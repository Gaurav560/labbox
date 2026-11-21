"""The AI tutor and code review (Phase E) with the fake provider. The main acceptance check: across 20
tasks, a model that tries to paste the solution never gets a solution line through to the learner."""
import random
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import labs, llm_gateway, progress, shared, tutor
from app.config import get_settings
from app.db import engine
from app.main import app
from app.models import LlmRequest

LAB, CH, TASK = "python-basics", "01-functions", "add"


@pytest.fixture
def client() -> TestClient:
    shared.forget_hits()
    with TestClient(app) as c:
        yield c


def login(client: TestClient) -> tuple[dict[str, str], int]:
    r = client.post("/api/auth/signup", json={"username": f"tut{uuid.uuid4().hex[:8]}", "password": "secret123"})
    assert r.status_code in (200, 201), r.text
    body = r.json()
    return {"Authorization": f"Bearer {body['token']}"}, body["user"]["id"]


def url(lab: str, ch: str, task: str, what: str = "tutor") -> str:
    return f"/api/labs/{lab}/chapters/{ch}/tasks/{task}/{what}"


def test_tutor_answers_with_context_and_is_logged(client: TestClient, monkeypatch):
    h, uid = login(client)
    seen = {}

    def model(messages):
        seen["system"], seen["user"] = messages[0]["content"], messages[1]["content"]
        return "Look at what your function returns. What does it give back for add(2, 3) right now?"

    monkeypatch.setattr(llm_gateway, "fake_chat_reply", model)
    client.post(f"/api/labs/{LAB}/chapters/{CH}/tasks/{TASK}/hint", headers=h)  # reveal one hint
    r = client.post(url(LAB, CH, TASK), headers=h, json={"question": "why does it fail?"})
    assert r.status_code == 200, r.text
    assert r.json()["blocked"] is False and "What does it give back" in r.json()["reply"]
    assert "Socratic" in seen["system"] and "Never write the solution" in seen["system"]
    task = labs.get_lab(LAB).task(CH, TASK)
    assert task.hints[0] in seen["user"] and task.hints[1] not in seen["user"]  # only revealed hints
    assert "why does it fail?" in seen["user"] and "--- " in seen["user"]  # the question and their files
    with Session(engine) as s:
        row = s.exec(select(LlmRequest).where(LlmRequest.user_id == uid)).one()
    assert (row.endpoint, row.alias, row.lab_id) == ("tutor", "lab-chat-smart", LAB)


def _tasks_with_solutions(n: int) -> list[tuple[str, str, str]]:
    out = []
    for lab in sorted(labs.all_labs(), key=lambda l: l.id):
        if not tutor.solution_lines(lab):
            continue
        for ch in lab.chapters:
            for t in ch.tasks:
                out.append((lab.id, ch.id, t.id))
    random.Random(42).shuffle(out)
    return out[:n]


def test_tutor_never_leaks_the_solution_across_20_tasks(client: TestClient, monkeypatch):
    h, _ = login(client)
    cases = _tasks_with_solutions(20)
    assert len(cases) == 20
    for lab_id, ch, task in cases:
        lines = sorted(tutor.solution_lines(labs.get_lab(lab_id)))
        leaked = random.Random(task).choice(lines)
        monkeypatch.setattr(llm_gateway, "fake_chat_reply", lambda m, leaked=leaked: f"Easy! Just write this:\n    {leaked}\nand you are done.")
        r = client.post(url(lab_id, ch, task), headers=h, json={"question": "just tell me the answer"})
        assert r.status_code == 200, (lab_id, task, r.text)
        reply = r.json()["reply"]
        assert r.json()["blocked"] is True, (lab_id, task)
        assert not any(line in tutor._code(reply) for line in lines), (lab_id, task, reply)


def test_tutor_reply_with_whitespace_changes_still_blocked(client: TestClient, monkeypatch):
    h, _ = login(client)
    line = sorted(tutor.solution_lines(labs.get_lab(LAB)))[0]
    monkeypatch.setattr(llm_gateway, "fake_chat_reply", lambda m: "Try:   " + line.replace(" ", "    "))
    assert client.post(url(LAB, CH, TASK), headers=h, json={}).json()["blocked"] is True


def test_commands_from_apply_sh_are_caught_without_quotes(client: TestClient, monkeypatch):
    """A real reply from a small model: the redis-cli command that solves the task, unquoted."""
    h, _ = login(client)
    reply = "Try running:\n```bash\nredis-cli HSET menu filter coffee 30 cold coffee 40 vada pav 25\n```"
    monkeypatch.setattr(llm_gateway, "fake_chat_reply", lambda m: reply)
    r = client.post(url("redis-in-practice", "03-hashes-and-lists", "menu_hash"), headers=h, json={})
    assert r.json()["blocked"] is True and "HSET menu" not in r.json()["reply"]


def test_tutor_replies_never_carry_code_blocks(client: TestClient, monkeypatch):
    h, _ = login(client)
    monkeypatch.setattr(llm_gateway, "fake_chat_reply", lambda m: "Think about hashes: one key, many fields.\n```python\nr.hset('menu', mapping=PRICES)\n```\nWhich command writes several fields at once?")
    reply = client.post(url("redis-in-practice", "03-hashes-and-lists", "menu_hash"), headers=h, json={}).json()["reply"]
    assert "```" not in reply and "hset(" not in reply and "Which command writes several fields" in reply


def test_lines_the_lesson_already_shows_are_not_secrets():
    lab = labs.get_lab("redis-in-practice")
    shown = {tutor._code(line) for line in lab.chapter_markdown("06-caching-for-real").splitlines()}
    assert not shown & tutor.solution_lines(lab)


def test_review_needs_a_passed_task(client: TestClient, monkeypatch):
    h, uid = login(client)
    monkeypatch.setattr(llm_gateway, "fake_chat_reply", lambda m: "- Good names.\\n- Think about negative numbers.")
    assert client.post(url(LAB, CH, TASK, "review"), headers=h).status_code == 409
    with Session(engine) as s:
        row = progress.task_progress(s, uid, LAB, CH, TASK)
        row.passed = True
        s.add(row)
        s.commit()
    r = client.post(url(LAB, CH, TASK, "review"), headers=h)
    assert r.status_code == 200 and "Good names" in r.json()["reply"]


def test_tutor_respects_the_budget(client: TestClient, monkeypatch):
    h, _ = login(client)
    monkeypatch.setattr(get_settings(), "LLM_DAILY_TOKENS", 1)
    assert client.post(url(LAB, CH, TASK), headers=h, json={}).status_code == 200  # the first one may use it up
    r = client.post(url(LAB, CH, TASK), headers=h, json={})
    assert r.status_code == 429 and "budget" in r.json()["detail"]


def test_unknown_task_is_404(client: TestClient):
    h, _ = login(client)
    assert client.post(url(LAB, CH, "nope"), headers=h, json={}).status_code == 404


def test_a_chapter_folder_lab_sends_only_that_chapters_files(tmp_path):
    # Spring Boot keeps each chapter in its own folder: the tutor sees that folder, not chapters 0 to 2.
    lab = labs.get_lab("spring-boot-first-api")
    ws = type("Ws", (), {"volume_path": str(tmp_path)})()
    files = tutor.learner_files(lab, ws, "20-repositories")
    assert "--- 20-repositories/" in files and "--- 00-what-is-spring-boot/" not in files
    assert "--- 00-what-is-spring-boot/" in tutor.learner_files(lab, ws)  # no chapter: the whole lab, as before


def test_a_chapter_with_its_own_folder_name_sends_that_folder(tmp_path):
    # Python from zero kept its chapter ids when chapters moved: id 01-functions lives in 02-functions/.
    lab = labs.get_lab("python-basics")
    ws = type("Ws", (), {"volume_path": str(tmp_path)})()
    files = tutor.learner_files(lab, ws, "01-functions")
    assert "--- 02-functions/greet.py" in files and "--- 01-first-program/" not in files
