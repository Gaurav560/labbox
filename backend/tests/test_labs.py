import shutil
from pathlib import Path

import pytest
import yaml

from app.labs import LabError, load_lab, load_labs

LABS_DIR = Path(__file__).resolve().parents[2] / "labs"


def test_real_labs_load():
    labs = load_labs(LABS_DIR)
    assert {"python-basics", "java-basics"} <= set(labs)  # more labs are added all the time
    py = labs["python-basics"]
    assert py.image == "labbox/python-basics:v1"
    assert [t.id for t in py.chapters[0].tasks] == ["hello_pocket", "fix_first_errors"]
    assert [t.id for t in py.chapter("01-functions").tasks] == ["greet", "add", "is_even"]  # ids kept when chapters moved
    assert py.check.network == "none"
    assert "def double(x):" in py.chapter_markdown("01-functions")
    assert [t.id for t in labs["java-basics"].chapters[0].tasks] == ["greet", "longest_word"]


@pytest.fixture
def lab_copy(tmp_path: Path) -> Path:
    dst = tmp_path / "python-basics"
    shutil.copytree(LABS_DIR / "python-basics", dst)
    return dst


def edit(folder: Path, fn) -> None:
    data = yaml.safe_load((folder / "lab.yaml").read_text())
    fn(data)
    (folder / "lab.yaml").write_text(yaml.safe_dump(data))


def expect_error(folder: Path, match: str) -> None:
    with pytest.raises(LabError, match=match):
        load_lab(folder)


def test_missing_image(lab_copy: Path):
    edit(lab_copy, lambda d: d.pop("image"))
    expect_error(lab_copy, "image")


def test_bad_id(lab_copy: Path):
    edit(lab_copy, lambda d: d.update(id="Python_Basics"))
    expect_error(lab_copy, "bad lab id")


def test_id_must_match_folder(lab_copy: Path):
    edit(lab_copy, lambda d: d.update(id="other-lab"))
    expect_error(lab_copy, "must equal folder name")


def test_duplicate_task_ids(lab_copy: Path):
    edit(lab_copy, lambda d: d["chapters"][0]["tasks"].append({"id": "greet", "title": "again"}))
    expect_error(lab_copy, "duplicate task ids: greet")


def test_chapter_file_missing(lab_copy: Path):
    (lab_copy / "chapters" / "02-functions.md").unlink()
    expect_error(lab_copy, "chapter file missing")


def test_chapter_file_cannot_escape(lab_copy: Path):
    edit(lab_copy, lambda d: d["chapters"][0].update(file="../../../etc/passwd"))
    expect_error(lab_copy, "chapter file missing")


def test_check_network_must_be_none(lab_copy: Path):
    edit(lab_copy, lambda d: d["check"].update(network="bridge"))
    expect_error(lab_copy, "invalid")


def test_unknown_key_rejected(lab_copy: Path):
    edit(lab_copy, lambda d: d.update(privileged=True))
    expect_error(lab_copy, "invalid")


def test_bad_memory(lab_copy: Path):
    edit(lab_copy, lambda d: d["resources"].update(memory="lots"))
    expect_error(lab_copy, "memory")


def test_load_labs_fails_loudly(tmp_path: Path, lab_copy: Path):
    edit(lab_copy, lambda d: d.pop("chapters"))
    with pytest.raises(LabError):
        load_labs(lab_copy.parent)


def test_task_examples_are_limited(lab_copy: Path):
    ex = {"call": "greet('Asha')", "gives": "'Hello, Asha!'"}
    edit(lab_copy, lambda d: d["chapters"][0]["tasks"][0].update(examples=[ex] * 3))
    assert load_lab(lab_copy).chapters[0].tasks[0].examples[0].gives == "'Hello, Asha!'"
    edit(lab_copy, lambda d: d["chapters"][0]["tasks"][0].update(examples=[ex] * 4))
    with pytest.raises(LabError):
        load_lab(lab_copy)
    edit(lab_copy, lambda d: d["chapters"][0]["tasks"][0].update(examples=[{"call": "x", "gives": ""}]))
    with pytest.raises(LabError):
        load_lab(lab_copy)
