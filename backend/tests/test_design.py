"""Design steps (Phase G): parsing, rubric checks, grading with a scripted fake model (clamping, retry,
"could not grade"), storage of every attempt, and XP once at half the points. No Docker."""
import asyncio
import json
import shutil
import uuid
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app import design, llm_gateway
from app.db import engine, init_db
from app.labs import load_lab
from app.lessons import LessonError, parse_steps
from app.models import DesignAnswer, User, XpEvent

ROOT = Path(__file__).resolve().parents[2]

DESIGN_STEP = """
:::step{type=design title="Design review"}
Answer in a few sentences.

:::ask{id=redis_down}
What happens to your limiter if Redis goes down?
:::

:::ask{id=many_servers}
Why does an in-memory counter break with two servers?
:::
:::
"""

RUBRIC = """01-functions:
  redis_down:
    - id: behaviour
      points: 2
      look_for: Says whether requests are allowed or blocked when Redis is down.
    - id: tradeoff
      points: 2
      look_for: Explains the trade-off (availability versus protection).
  many_servers:
    - id: shared_state
      points: 3
      look_for: Each server counts separately, so the real limit is multiplied.
"""


@pytest.fixture
def lab(tmp_path: Path):
    folder = tmp_path / "python-basics"
    shutil.copytree(ROOT / "labs" / "python-basics", folder)
    ch = folder / "chapters" / "01-functions.md"
    ch.write_text(ch.read_text() + DESIGN_STEP)
    (folder / "tests" / "rubric.yaml").write_text(RUBRIC)
    return load_lab(folder)


@pytest.fixture
def user_id() -> int:
    init_db()
    with Session(engine) as s:
        u = User(username=f"des{uuid.uuid4().hex[:8]}", password_hash="x")
        s.add(u)
        s.commit()
        s.refresh(u)
    llm_gateway._recent.clear()
    return u.id


def design_index(lab) -> int:
    return next(i for i, s in enumerate(lab.chapter_steps("01-functions")) if s.type == "design")


def grade(lab, uid, answers):
    with Session(engine) as s:
        return asyncio.run(design.grade(s, uid, lab, "01-functions", design_index(lab), answers))


GOOD = {"redis_down": "If Redis is down I let requests through (fail open) so users are not blocked, but log it.",
        "many_servers": "Each server keeps its own counter, so two servers allow twice the limit."}


def test_parse_design_step(lab):
    step = lab.chapter_steps("01-functions")[design_index(lab)]
    assert [q.id for q in step.questions] == ["redis_down", "many_servers"]
    assert "Redis goes down" in step.questions[0].text and ":::ask" not in step.markdown
    with pytest.raises(LessonError, match="1 to 5"):
        parse_steps(':::step{type=design title="x"}\nno questions\n:::\n')
    with pytest.raises(LessonError, match="used twice"):
        parse_steps(':::step{type=design}\n:::ask{id=a}\nx\n:::\n:::ask{id=a}\ny\n:::\n:::\n')
    assert design.check_rubric(lab) == []
    (lab.tests_dir / "rubric.yaml").write_text("01-functions:\n  redis_down:\n    - {id: b, points: 1, look_for: x}\n")
    design._load.cache_clear()
    assert any("many_servers" in e for e in design.check_rubric(lab))


def test_grading_is_clamped_stored_and_gives_xp_once(lab, user_id, monkeypatch):
    replies = {
        "Redis goes down": {"criteria": [{"id": "behaviour", "score": 2, "feedback": "Clear."}, {"id": "tradeoff", "score": 9, "feedback": "Good."}]},
        "two servers": {"criteria": [{"id": "shared_state", "score": 3, "feedback": "Exactly."}, {"id": "invented", "score": 5}]},
    }
    seen = []

    def model(messages):
        seen.append(messages)
        q = messages[1]["content"]
        return "```json\n" + json.dumps(next(v for k, v in replies.items() if k in q)) + "\n```"

    monkeypatch.setattr(llm_gateway, "fake_chat_reply", model)
    r = grade(lab, user_id, GOOD)
    assert (r.score, r.max) == (7, 7)  # tradeoff 9 clamped to 2; the invented criterion ignored
    assert [c.score for c in r.questions[0].criteria] == [2, 2]
    assert [x.amount for x in r.xp_awarded] == [design.XP_DESIGN]
    assert "rubric" in seen[0][1]["content"].lower() and "JSON" in seen[0][0]["content"]
    # A second attempt is stored too, but the XP is only given once.
    assert grade(lab, user_id, GOOD).xp_awarded == []
    with Session(engine) as s:
        rows = s.exec(select(DesignAnswer).where(DesignAnswer.user_id == user_id)).all()
        assert len(rows) == 2 and json.loads(rows[0].answers_json)["redis_down"].startswith("If Redis")
        assert len(s.exec(select(XpEvent).where(XpEvent.user_id == user_id, XpEvent.kind == "design")).all()) == 1
        latest = design.latest(s, user_id, lab, "01-functions")
    assert latest[design_index(lab)].result.score == 7


def test_short_answers_and_low_scores(lab, user_id, monkeypatch):
    monkeypatch.setattr(llm_gateway, "fake_chat_reply", lambda m: json.dumps({"criteria": [{"id": "shared_state", "score": 1, "feedback": "Partly."}]}))
    r = grade(lab, user_id, {"redis_down": "no idea", "many_servers": "They count on their own, so the limit grows with servers."})
    assert r.questions[0].score == 0 and "few sentences" in r.questions[0].criteria[0].feedback  # no model call for it
    assert r.score == 1 and r.xp_awarded == []  # under half the points: no XP, but still recorded


def test_bad_json_is_retried_then_refused(lab, user_id, monkeypatch):
    calls = []

    def flaky(messages):
        calls.append(1)
        return "I think it is pretty good!" if len(calls) == 1 else json.dumps({"criteria": [{"id": "behaviour", "score": 1, "feedback": "Ok."}]})

    monkeypatch.setattr(llm_gateway, "fake_chat_reply", flaky)
    r = grade(lab, user_id, {"redis_down": GOOD["redis_down"], "many_servers": "x"})
    assert len(calls) == 2 and r.questions[0].criteria[0].score == 1  # retried once, then fine

    monkeypatch.setattr(llm_gateway, "fake_chat_reply", lambda m: "not json at all")
    with pytest.raises(HTTPException) as e:
        grade(lab, user_id, GOOD)
    assert e.value.status_code == 503 and "not lost" in e.value.detail
