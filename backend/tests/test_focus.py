"""Switching chapters opens that chapter's code: which file and line (app/focus.py)."""

from pathlib import Path

from app.focus import chapter_focus
from app.labs import load_labs

LABS = load_labs(Path(__file__).resolve().parents[2] / "labs")


def focus(lab_id: str, chapter_index: int, folder: Path | None = None):
    lab = LABS[lab_id]
    return chapter_focus(lab, lab.chapters[chapter_index], folder)


def test_a_task_todo_opens_at_its_section_header():
    path, line = focus("redis-in-practice", 5)  # chapter 6, caching for real
    assert path == "app.py"
    text = (LABS["redis-in-practice"].starter_dir / "app.py").read_text().splitlines()[line - 1]
    assert "chapter 6" in text


def test_terminal_only_chapters_open_the_readme():
    assert focus("redis-in-practice", 0) == ("README.md", 1)


def test_other_comment_styles():
    go = LABS["go-basics"]
    slices_ch = next(i for i, c in enumerate(go.chapters) if c.id == "01-slices-and-errors")
    assert focus("go-basics", slices_ch)[0] == "till.go"  # // TODO (task total)
    assert focus("go-basics", 0)[0] == "hello/hello.go"  # a chapter in its own package folder
    assert focus("sql-from-zero", 0) == ("q1.sql", 1)  # -- q1 (task q_paid_coffee)
    assert focus("python-basics", 0)[0] == "greet.py"  # no task ids, no README: the first TODO


def test_the_learners_own_copy_wins(tmp_path):
    # Lines move as the learner writes code; their copy is searched first.
    (tmp_path / "app.py").write_text("\n" * 40 + "# ---------- chapter 6: caching ----------\n# TODO(price_cache): go\n")
    assert focus("redis-in-practice", 5, tmp_path) == ("app.py", 41)


# ---------- each lesson step opens the file it talks about ----------

import random  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import labs  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db import init_db  # noqa: E402
from app.focus import task_focus  # noqa: E402
from app.lessons import LessonError, parse_steps  # noqa: E402
from app.main import app  # noqa: E402

SPRING = "spring-boot-first-api"


def test_a_step_names_its_file_and_lines():
    [s] = parse_steps(':::step{type=concept title="Run" file="app/Main.java" line="8-12"}\nText\n:::')
    assert (s.file, s.line, s.end_line) == ("app/Main.java", 8, 12)
    [s] = parse_steps(':::step{type=concept title="Run" file="app/Main.java" line="8"}\nText\n:::')
    assert (s.line, s.end_line) == (8, None)
    for bad in ('file="/etc/passwd"', 'file="../x.py"', 'file="a/./b.py"', 'file="a.py" line="0"',
                'file="a.py" line="9-3"', 'file="a.py" line="eight"', 'line="3"'):
        with pytest.raises(LessonError):
            parse_steps(f":::step{{type=concept {bad}}}\nText\n:::")


def test_a_task_step_opens_its_own_tasks_todo():
    lab = LABS[SPRING]
    ch = next(c for c in lab.chapters if c.id == "05-beans")
    assert task_focus(lab, ch, "price_service", None)[0] == "05-beans/src/main/java/com/shop/pricing/PriceCalculator.java"
    assert task_focus(lab, ch, "one_counter", None)[0] == "05-beans/src/main/java/com/shop/visits/HomeController.java"


@pytest.fixture(scope="module")
def client() -> TestClient:
    labs.init_labs(get_settings().LABS_DIR)
    init_db()
    return TestClient(app)


def test_the_focus_route_follows_the_step(client: TestClient):
    r = client.post("/api/auth/signup", json={"username": f"focus{random.randint(0, 10**9)}", "password": "secret123"})
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    url = f"/api/labs/{SPRING}/chapters/04-app-startup/focus"
    steps = client.get(f"/api/labs/{SPRING}/chapters/04-app-startup", headers=h).json()["steps"]
    run = next(i for i, s in enumerate(steps) if s["title"] == "What SpringApplication.run does")
    assert steps[run]["file"].endswith("ShopApiApplication.java")  # the page knows the step has a file
    f = client.post(url, json={"step": run}, headers=h).json()
    assert f == {"path": "04-app-startup/src/main/java/com/shop/ShopApiApplication.java", "line": 10, "end_line": 10}
    task = next(i for i, s in enumerate(steps) if s["task"] == "greeting_property")
    assert client.post(url, json={"step": task}, headers=h).json()["path"] == "04-app-startup/src/main/resources/application.properties"
    story = 0  # a step about no file: nothing to open
    assert client.post(url, json={"step": story}, headers=h).json()["path"] is None
    assert client.post(url, json={"step": 999}, headers=h).status_code == 404
    # Without a step, the chapter's own file, as before.
    assert client.post(url, json={}, headers=h).json()["path"].startswith("04-app-startup/")


def test_a_course_with_a_chapter_0_numbers_chapters_by_their_ids(client: TestClient):
    # The Spring course starts at chapter 0, so "Continue" shows the number in the chapter's id (the folder's
    # number), not its position: the dashboard, the chapter menu and the folders agree.
    r = client.post("/api/auth/signup", json={"username": f"num{random.randint(0, 10**9)}", "password": "secret123"})
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    client.put(f"/api/labs/{SPRING}/chapters/11-reading-the-request/progress", json={"current_step": 2}, headers=h)
    nxt = client.get("/api/me/next", headers=h).json()
    assert (nxt["chapter_id"], nxt["chapter_number"], nxt["chapters"]) == ("11-reading-the-request", 11, 30)


def test_chapters_carry_their_course_part(client: TestClient):
    # Skill maps draw each course part as a metro line: a chapter that starts a part names it; the rest are null.
    r = client.post("/api/auth/signup", json={"username": f"part{random.randint(0, 10**9)}", "password": "secret123"})
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    chapters = client.get(f"/api/labs/{SPRING}", headers=h).json()["chapters"]
    parts = [(c["id"][:2], c["part"]) for c in chapters if c["part"]]
    assert parts == [("00", "Foundations"), ("10", "REST APIs"), ("19", "Data"), ("25", "Production basics")]
    assert all("part" in c for c in chapters)
    beans = next(c for c in chapters if c["id"] == "05-beans")
    assert "How a class becomes a bean" in beans["topics"]  # concept steps are the chapter's subtopics
    assert "What you can do now" not in beans["topics"]
