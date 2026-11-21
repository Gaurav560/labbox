"""Chapter markdown v2: splitting into steps, v1 chapters as one step, predict parsing."""
import shutil
from pathlib import Path

import pytest

from app.labs import LabError, load_lab, load_labs
from app.lessons import LessonError, parse_attrs, parse_steps

FIXTURES = Path(__file__).parent / "fixtures" / "v1_chapters"
LABS_DIR = Path(__file__).resolve().parents[2] / "labs"


@pytest.mark.parametrize("name", ["python-01-functions.md", "java-01-methods.md"])
def test_v1_chapter_is_one_step(name: str):
    md = (FIXTURES / name).read_text()
    steps = parse_steps(md)
    assert len(steps) == 1
    assert steps[0].type == "concept"
    assert steps[0].markdown == md.strip()


def test_attrs():
    assert parse_attrs('{type=story title="Why queries get slow" task=add_index}') == {
        "type": "story",
        "title": "Why queries get slow",
        "task": "add_index",
    }
    assert parse_attrs("{minutes=15}") == {"minutes": "15"}
    assert parse_attrs(None) == {}


SPEC_EXAMPLE = '''\
:::step{type=story}
:::character{name="Meera" role="CTO"}
Lunch rush starts in 15 minutes.
:::
:::mission
Make `/checkout` fast.
:::
:::

:::step{type=concept title="Why queries get slow"}
A database finds rows in one of two ways.

:::tip
`EXPLAIN ANALYZE` shows the plan.
:::
:::

:::step{type=predict}
:::question
What does Postgres do?
:::
- [ ] Jumps straight to the row
- [x] Reads every row and filters
- [ ] Uses the primary key index
:::explain
Without an index, a sequential scan.
:::
:::

:::step{type=try}
Run this:
```bash run
psql -c "SELECT 1"
```
:::

:::step{type=task task=add_index}
Fix it.
:::

:::step{type=incident task=add_index minutes=15}
Pager: checkout is down.
:::

:::step{type=recap}
- Slow endpoints hide slow queries.
:::
'''


def test_spec_example():
    steps = parse_steps(SPEC_EXAMPLE)
    assert [s.type for s in steps] == ["story", "concept", "predict", "try", "task", "incident", "recap"]
    story = steps[0]
    assert ':::character{name="Meera" role="CTO"}' in story.markdown and ":::mission" in story.markdown
    assert steps[1].title == "Why queries get slow" and ":::tip" in steps[1].markdown
    p = steps[2].predict
    assert p is not None
    assert [o.text for o in p.options] == ["Jumps straight to the row", "Reads every row and filters", "Uses the primary key index"]
    assert p.answer == 1
    assert p.question == "What does Postgres do?"
    assert p.explain == "Without an index, a sequential scan."
    assert "[x]" not in steps[2].markdown and "explain" not in steps[2].markdown
    assert "```bash run" in steps[3].markdown
    assert steps[4].task == "add_index"
    assert steps[5].minutes == 15


def test_directive_markers_inside_code_are_ignored():
    md = ":::step{type=example}\n```text\n:::\n:::step\n```\nafter\n:::\n"
    steps = parse_steps(md)
    assert len(steps) == 1
    assert steps[0].markdown == "```text\n:::\n:::step\n```\nafter"


def test_loose_text_between_steps_is_kept():
    steps = parse_steps("intro\n\n:::step{type=concept}\nA\n:::\n")
    assert [s.markdown for s in steps] == ["intro", "A"]


@pytest.mark.parametrize(
    "md, match",
    [
        (":::step{type=banana}\nx\n:::\n", "unknown step type"),
        (":::step{type=task}\nx\n:::\n", "needs a task"),
        (":::step{type=predict}\n- [x] a\n- [ ] b\n:::\n", "no :::question"),
        (":::step{type=predict}\n:::question\nq\n:::\n- [ ] a\n- [ ] b\n:::\n", "exactly one correct"),
        (":::step{type=predict}\n:::question\nq\n:::\n- [x] a\n:::\n", "at least 2 options"),
    ],
)
def test_bad_steps(md: str, match: str):
    with pytest.raises(LessonError, match=match):
        parse_steps(md)


def test_real_chapters_are_v2():
    for lab in load_labs(LABS_DIR).values():
        for ch in lab.chapters:
            types = [s.type for s in lab.chapter_steps(ch.id)]
            # Spec section 9: story, concept or example steps, a predict, a try, 1 to 4 tasks (or an
            # incident), a recap; deep-dive and design steps come on top. CONTENT_STANDARD section 3
            # ("explain, do not just state") allows more, smaller concept steps; the owner's "talk to the
            # learner, small steps" voice (21 November) needs room for up to 14 of them.
            assert 6 <= len(types) <= 30, (lab.id, types)
            assert 1 <= sum(t in ("concept", "example") for t in types) <= 14, (lab.id, ch.id, "1 to 14 concept or example steps")
            assert sum(t in ("task", "incident") for t in types) <= 4, (lab.id, ch.id, "at most 4 tasks")
            for needed in ("story", "predict", "recap"):
                assert needed in types, (lab.id, needed)
            assert "task" in types or "incident" in types, (lab.id, "task or incident")  # content standard, section 9
            assert {s.task for s in lab.chapter_steps(ch.id) if s.task} == {t.id for t in ch.tasks}
            assert all(len(t.hints) == 3 for t in ch.tasks)


def test_step_with_unknown_task_fails_lab_load(tmp_path: Path):
    dst = tmp_path / "python-basics"
    shutil.copytree(LABS_DIR / "python-basics", dst)
    chapter = dst / "chapters" / "02-functions.md"
    chapter.write_text(chapter.read_text().replace("task=add ", "task=nope "))
    with pytest.raises(LabError, match="'nope'"):
        load_lab(dst)


def test_bad_step_fails_lab_load(tmp_path: Path):
    dst = tmp_path / "python-basics"
    shutil.copytree(LABS_DIR / "python-basics", dst)
    (dst / "chapters" / "02-functions.md").write_text(":::step{type=banana}\nx\n:::\n")
    with pytest.raises(LabError, match="unknown step type"):
        load_lab(dst)


def test_v1_lab_still_loads(tmp_path: Path):
    """A v1 lab (old chapter, no hints or xp in lab.yaml) loads with defaults."""
    dst = tmp_path / "python-basics"
    shutil.copytree(LABS_DIR / "python-basics", dst)
    shutil.copy(FIXTURES / "python-01-functions.md", dst / "chapters" / "02-functions.md")
    yaml_path = dst / "lab.yaml"
    yaml_path.write_text("\n".join(l for l in yaml_path.read_text().splitlines() if not l.startswith("          - ") and "hints:" not in l))
    lab = load_lab(dst)
    assert [s.type for s in lab.chapter_steps("01-functions")] == ["concept"]
    assert all(t.xp == 20 and t.hints == [] for t in lab.chapters[0].tasks)
