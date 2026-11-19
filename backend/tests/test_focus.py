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
    assert focus("go-basics", 0)[0] == "till.go"  # // TODO (task total)
    assert focus("sql-from-zero", 0) == ("q1.sql", 1)  # -- q1 (task q_paid_coffee)
    assert focus("python-basics", 0)[0] == "greet.py"  # no task ids, no README: the first TODO


def test_the_learners_own_copy_wins(tmp_path):
    # Lines move as the learner writes code; their copy is searched first.
    (tmp_path / "app.py").write_text("\n" * 40 + "# ---------- chapter 6: caching ----------\n# TODO(price_cache): go\n")
    assert focus("redis-in-practice", 5, tmp_path) == ("app.py", 41)
