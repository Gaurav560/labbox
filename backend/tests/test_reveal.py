"""Plan A (owner, 27 November): a learner sees a chapter's starter folder only once they reach that chapter.

A new learner's machine opens with chapter 1's folder (and files every chapter shares, like go.mod); opening a later
chapter brings its folder and every earlier one in; files a learner already has are never touched; labs without
chapter folders, and workspaces from before, keep every file.
"""
import random
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app import containers, labs
from app.config import get_settings
from app.db import init_db
from app.labs import get_lab, init_labs
from app.main import app

FDE = "forward-deployed-engineer"


def _ws(folder: Path, name: str = "lab-u12345678-fde"):
    return SimpleNamespace(volume_path=str(folder), container_name=name)


def _tops(folder: Path) -> set[str]:
    return {p.name for p in folder.iterdir()}


def test_which_labs_reveal_their_chapter_folders():
    init_labs(get_settings().LABS_DIR)
    fde = get_lab(FDE)
    assert len(fde.chapter_folders()) == len(fde.chapters) == 22
    assert fde.chapter_folders()["01-the-role"] == 0
    assert get_lab("express-api").chapter_folders() == {}  # one chapter, one file: nothing to reveal
    # The shared module file of the Go course comes at once, with chapter 1.
    go = get_lab("go-basics")
    assert "go.mod" in containers.visible_files(go, 0)
    assert containers.visible_files(go, None) == containers.starter_files(go)


def test_a_new_workspace_starts_with_chapter_one_and_grows(tmp_path):
    init_labs(get_settings().LABS_DIR)
    lab = get_lab(FDE)
    folder = tmp_path / "u12345678" / FDE
    folder.mkdir(parents=True)
    containers.seed(lab, folder, 0)
    assert _tops(folder) == {"01-the-role"}
    # The learner opens chapter 3: chapters 2 and 3 arrive, nothing later.
    added = containers.top_up(lab, _ws(folder), 2)
    assert {Path(a).parts[0] for a in added} == {"02-discovery", "03-scoping"}
    assert _tops(folder) == {"01-the-role", "02-discovery", "03-scoping"}
    assert containers.top_up(lab, _ws(folder), 2) == []  # once is enough
    # A folder brought in by opening a chapter stays, even when a later request counts only saved progress.
    containers.top_up(lab, _ws(folder), 0)
    assert "03-scoping" in _tops(folder)
    # Their own work in chapter 1 is never replaced when more folders arrive.
    mine = next(p for p in (folder / "01-the-role").glob("*.py"))
    mine.write_text("# my own version\n")
    containers.top_up(lab, _ws(folder), 5)
    assert mine.read_text() == "# my own version\n"
    assert "06-legacy-system" in _tops(folder) and "07-data-contract" not in _tops(folder)


def test_an_old_workspace_puts_away_untouched_later_folders(tmp_path):
    # Learners who started before plan A received every folder (owner, 27 November: "why are you still showing me all
    # the folders in chapter 1?"). Folders of chapters not reached that are still the starter copy go away and come
    # back the same later; a folder with the learner's own work stays.
    init_labs(get_settings().LABS_DIR)
    lab = get_lab(FDE)
    folder = tmp_path / "u12345678" / FDE
    folder.mkdir(parents=True)
    containers.seed(lab, folder)  # the old way: everything
    containers._tidied_path(folder).unlink()  # workspaces from before plan A have no mark
    assert len(_tops(folder)) == 22
    mine = next((folder / "09-extraction").glob("*.py"))
    mine.write_text("# I started this one early\n")
    (folder / "12-mcp-server" / "notes.txt").write_text("mine\n")
    assert containers.top_up(lab, _ws(folder), 1) == []
    assert _tops(folder) == {"01-the-role", "02-discovery", "09-extraction", "12-mcp-server"}
    assert mine.read_text() == "# I started this one early\n"
    assert containers.top_up(lab, _ws(folder), 1) == []  # once only: kept folders are not compared again
    # Reaching chapter 3 brings its folder back, byte for byte the starter.
    assert {Path(a).parts[0] for a in containers.top_up(lab, _ws(folder), 2)} == {"03-scoping"}
    for f in (lab.starter_dir / "03-scoping").rglob("*"):
        if f.is_file():
            assert (folder / f.relative_to(lab.starter_dir)).read_bytes() == f.read_bytes()


def test_the_lab_page_learns_each_chapters_folder():
    # The Files panel hides the folders of chapters after the one open; the lab API names each chapter's folder.
    init_labs(get_settings().LABS_DIR)
    fde = get_lab(FDE)
    assert fde.chapter_folder(fde.chapters[0]) == "01-the-role"
    git = get_lab("git-without-fear")  # folders made by each chapter's setup
    assert git.chapter_folder(git.chapters[0]) == "01-why-version-control"
    express = get_lab("express-api")
    assert express.chapter_folder(express.chapters[0]) is None and express.folders_after(-1) == []
    # VS Code: in chapter 3 the Explorer hides folders 4 to 22.
    import json
    from app import ide
    hidden = json.loads(ide.workspace_config(fde, 2))["settings"]["files.exclude"]
    assert "03-scoping" not in hidden and "04-messy-data" in hidden and len(hidden) == 19
    assert json.loads(ide.workspace_config(fde, -1))["settings"] == {}


@pytest.fixture(scope="module")
def client() -> TestClient:
    labs.init_labs(get_settings().LABS_DIR)
    init_db()
    return TestClient(app)


def test_opening_a_chapter_brings_its_folder(client: TestClient):
    r = client.post("/api/auth/signup", json={"username": f"reveal{random.randint(0, 10**9)}", "password": "secret123"})
    body = r.json()
    h = {"Authorization": f"Bearer {body['token']}"}
    folder = Path(get_settings().VOLUMES_DIR) / f"u{body['user']['id']}" / FDE
    # The lab page opens chapter 1: the workspace is made with chapter 1 only.
    first = client.post(f"/api/labs/{FDE}/chapters/the-role/focus", json={}, headers=h)
    assert first.status_code == 200, first.text
    assert _tops(folder) == {"01-the-role"}
    # The lab page opens chapter 4 (chapter focus): chapters 2 to 4 arrive.
    assert client.post(f"/api/labs/{FDE}/chapters/messy-data/focus", json={}, headers=h).status_code == 200
    assert _tops(folder) == {"01-the-role", "02-discovery", "03-scoping", "04-messy-data"}
    # A chapter the learner has been in counts later too (progress saved): opening chapter 1 again keeps them.
    client.put(f"/api/labs/{FDE}/chapters/messy-data/progress", json={"current_step": 1}, headers=h)
    client.post(f"/api/labs/{FDE}/chapters/the-role/focus", json={}, headers=h)
    assert "04-messy-data" in _tops(folder) and "05-customer-database" not in _tops(folder)
