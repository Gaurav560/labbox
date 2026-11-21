"""Labs that grow: learners who started before get the new starter files, and nothing of theirs is touched."""
from pathlib import Path
from types import SimpleNamespace

from app import containers
from app.config import get_settings
from app.labs import get_lab, init_labs


def _ws(folder: Path, name: str = "lab-u12345678-python-basics"):
    return SimpleNamespace(volume_path=str(folder), container_name=name)


def test_an_old_workspace_gets_the_new_files_and_keeps_its_own(tmp_path):
    init_labs(get_settings().LABS_DIR)
    lab = get_lab("python-basics")
    folder = tmp_path / "u12345678" / "python-basics"
    folder.mkdir(parents=True)
    # Opened before chapters 2 to 5 existed: only chapter 1's files, one already edited by the learner.
    (folder / "greet.py").write_text("def greet(name):\n    return f'Hello, {name}!'\n")
    (folder / "math_utils.py").write_text("# my own version\n")
    (folder / "notes.txt").write_text("mine")

    added = containers.top_up(lab, _ws(folder))
    assert {"03-numbers-and-text/numbers_text.py", "04-decisions/decisions.py", "05-loops/loops.py", "07-strings/text_tools.py"} <= set(added)
    assert "greet.py" not in added and "math_utils.py" not in added
    assert "Hello, {name}!" in (folder / "greet.py").read_text()  # their work, untouched
    assert (folder / "math_utils.py").read_text() == "# my own version\n"
    assert (folder / "03-numbers-and-text/numbers_text.py").read_text() == (lab.starter_dir / "03-numbers-and-text/numbers_text.py").read_text()
    assert (folder / "notes.txt").read_text() == "mine"

    assert containers.top_up(lab, _ws(folder)) == []  # once is enough
    (folder / "05-loops/loops.py").unlink()  # deleted on purpose
    assert containers.top_up(lab, _ws(folder)) == []
    assert not (folder / "05-loops/loops.py").exists()


def test_a_learner_file_with_the_same_name_wins(tmp_path):
    init_labs(get_settings().LABS_DIR)
    lab = get_lab("python-basics")
    folder = tmp_path / "ws"
    folder.mkdir()
    (folder / "04-decisions").mkdir()
    (folder / "04-decisions/decisions.py").write_text("# I wrote this before the chapter existed\n")
    containers.top_up(lab, _ws(folder))
    assert (folder / "04-decisions/decisions.py").read_text() == "# I wrote this before the chapter existed\n"


def test_a_fresh_seed_records_its_files(tmp_path):
    init_labs(get_settings().LABS_DIR)
    lab = get_lab("python-basics")
    folder = tmp_path / "fresh"
    folder.mkdir()
    containers.seed(lab, folder)
    assert containers.top_up(lab, _ws(folder)) == []  # nothing new to add
    assert set(containers.starter_files(lab)) <= {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}


def test_never_writes_through_a_link_out_of_the_workspace(tmp_path):
    starter = tmp_path / "starter"
    (starter / "pkg").mkdir(parents=True)
    (starter / "pkg" / "new.py").write_text("x = 1\n")
    lab = SimpleNamespace(id="demo", starter_dir=starter)
    outside = tmp_path / "outside"
    outside.mkdir()
    folder = tmp_path / "ws"
    folder.mkdir()
    (folder / "pkg").symlink_to(outside)  # the learner points pkg/ somewhere else
    assert containers.top_up(lab, _ws(folder, "lab-u12345678-demo")) == []
    assert not (outside / "new.py").exists()
