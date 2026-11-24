"""The Library (owner, 24 November): books, research papers and tech blogs. Learners read; admins change."""
import random
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlmodel import Session

from app.db import engine, init_db
from app.models import User

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def signup(api: TestClient, name: str) -> tuple[dict, int]:
    r = api.post("/api/auth/signup", json={"username": f"{name}{random.randint(0, 10**8)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user"]["id"]


@pytest.fixture(scope="module")
def admin(api) -> Iterator[dict]:
    h, uid = signup(api, "librarian")
    with Session(engine) as s:
        u = s.get(User, uid)
        u.is_admin = True
        s.add(u)
        s.commit()
    try:
        yield h
    finally:  # never leave a test account as admin
        with Session(engine) as s:
            u = s.get(User, uid)
            u.is_admin = False
            s.add(u)
            s.commit()


def test_seed_fills_a_fresh_database_once(tmp_path: Path):
    seed = yaml.safe_load((ROOT / "library" / "seed.yaml").read_text())
    db = create_engine(f"sqlite:///{tmp_path / 'lib.db'}")
    init_db(db)
    with db.connect() as c:
        counts = dict(c.execute(text("SELECT kind, COUNT(*) FROM library_item GROUP BY kind")).all())
    assert counts == {"book": len(seed["books"]), "paper": len(seed["papers"]), "blog": len(seed["blogs"])}
    with db.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM library_item WHERE image = ''")).scalar_one() == 0
    init_db(db)  # running the migrations again adds nothing
    with db.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM library_item")).scalar_one() == sum(counts.values())


def test_seed_file_is_sound():
    seed = yaml.safe_load((ROOT / "library" / "seed.yaml").read_text())
    for group in ("books", "papers", "blogs"):
        assert seed[group], group
        for item in seed[group]:
            assert item["title"] and item["note"] and item["topic"], item
            assert item["url"].startswith("https://"), item["url"]
            assert "\u2014" not in str(item), item["title"]  # no em dashes anywhere
            if item.get("lab"):
                assert (ROOT / "labs" / item["lab"] / "lab.yaml").exists(), item["lab"]
                assert item.get("practice"), item["title"]
            assert item.get("level", "") in ("", "beginner", "intermediate", "advanced")
            assert (ROOT / "library" / "images" / item["image"]).is_file(), item["title"]
        assert sum(1 for i in seed[group] if i.get("featured")) == 1, group  # one "Start here" pick each


def test_anyone_reads_the_library_in_order(api):
    items = api.get("/api/library").json()  # public: the page is shared for marketing
    kinds = {i["kind"] for i in items}
    assert {"book", "paper", "blog"} <= kinds
    for kind in kinds:
        positions = [i["position"] for i in items if i["kind"] == kind]
        assert positions == sorted(positions)
    assert any(i["title"] == "Attention Is All You Need" for i in items)
    rag = next(i for i in items if i["title"].startswith("Retrieval-Augmented Generation"))
    assert (rag["lab"], rag["free"]) == ("rag-vector-databases", True)
    papers = [i for i in items if i["kind"] == "paper"]
    assert papers[0]["title"] == "Attention Is All You Need" and papers[0]["featured"]  # the first paper (owner)
    # then the history of language models (owner, 25 November)
    assert [p["title"].split(":")[0] for p in papers[1:8]] == [
        "Efficient Estimation of Word Representations in Vector Space",
        "Improving Language Understanding by Generative Pre-Training", "BERT", "Scaling Laws for Neural Language Models",
        "Language Models are Few-Shot Learners", "Training language models to follow instructions with human feedback",
        "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"]


def test_only_admins_change_it(api):
    learner, _ = signup(api, "plain")
    body = {"kind": "book", "title": "Not allowed"}
    assert api.post("/api/admin/library", json=body, headers=learner).status_code == 403
    assert api.put("/api/admin/library/1", json=body, headers=learner).status_code == 403
    assert api.delete("/api/admin/library/1", headers=learner).status_code == 403
    assert api.post("/api/admin/library/1/move", json={"direction": "up"}, headers=learner).status_code == 403


def test_admin_adds_changes_moves_and_removes(api, admin):
    body = {"kind": "blog", "title": "  A test   blog ", "authors": "Tester", "url": "https://example.org/",
            "note": "Only for the test.", "topic": "Testing"}
    r = api.post("/api/admin/library", json=body, headers=admin)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["title"] == "A test blog"  # spaces squeezed
    blogs = [i for i in api.get("/api/library", headers=admin).json() if i["kind"] == "blog"]
    assert blogs[-1]["id"] == item["id"]  # a new item goes to the end of its list

    moved = api.post(f"/api/admin/library/{item['id']}/move", json={"direction": "up"}, headers=admin).json()
    assert [i["id"] for i in moved][-2] == item["id"]
    top = api.post(f"/api/admin/library/{moved[0]['id']}/move", json={"direction": "up"}, headers=admin).json()
    assert top[0]["id"] == moved[0]["id"]  # the first cannot move further up

    changed = api.put(f"/api/admin/library/{item['id']}", headers=admin,
                      json={**body, "kind": "paper", "title": "A test paper", "year": 2026}).json()
    assert (changed["kind"], changed["title"], changed["year"]) == ("paper", "A test paper", 2026)
    papers = [i for i in api.get("/api/library", headers=admin).json() if i["kind"] == "paper"]
    assert papers[-1]["id"] == item["id"]  # moved to the end of the papers

    assert api.delete(f"/api/admin/library/{item['id']}", headers=admin).json() == {"ok": True}
    assert item["id"] not in [i["id"] for i in api.get("/api/library", headers=admin).json()]
    assert api.delete(f"/api/admin/library/{item['id']}", headers=admin).status_code == 404


def test_bad_input_is_refused(api, admin):
    for bad in ({"kind": "video", "title": "x"}, {"kind": "book", "title": ""},
                {"kind": "book", "title": "x", "url": "javascript:alert(1)"}, {"kind": "book", "title": "x", "year": 99999},
                {"kind": "book", "title": "x" * 201}):
        assert api.post("/api/admin/library", json=bad, headers=admin).status_code == 422, bad


def test_one_start_here_per_section_and_known_labs_only(api, admin):
    body = {"kind": "book", "title": "A featured test book", "featured": True, "lab": "python-basics", "practice": "chapter 1"}
    item = api.post("/api/admin/library", json=body, headers=admin).json()
    books = [i for i in api.get("/api/library").json() if i["kind"] == "book"]
    assert [i["id"] for i in books if i["featured"]] == [item["id"]]  # the old pick lost its badge
    assert api.post("/api/admin/library", json={**body, "lab": "no-such-lab"}, headers=admin).status_code == 422
    assert api.delete(f"/api/admin/library/{item['id']}", headers=admin).status_code == 200
    old = next(i for i in books if i["title"] == "AI Engineering")
    api.put(f"/api/admin/library/{old['id']}", headers=admin, json={k: old[k] for k in (
        "kind", "title", "authors", "year", "url", "note", "topic", "lab", "practice", "level", "free")} | {"featured": True})
    books = [i for i in api.get("/api/library").json() if i["kind"] == "book"]
    assert [i["title"] for i in books if i["featured"]] == ["AI Engineering"]  # put back as it was


def test_pictures_are_served_from_labbox(api):
    items = api.get("/api/library").json()
    assert all(i["image"] for i in items), [i["title"] for i in items if not i["image"]]
    r = api.get(f"/api/library/images/{items[0]['image']}")
    assert r.status_code == 200 and r.headers["content-type"] == "image/webp" and r.content[:4] == b"RIFF"
    assert api.get("/api/library/images/..%2Fseed.yaml").status_code == 404
    assert api.get("/api/library/images/nothing-here.webp").status_code == 404


def test_admin_uploads_a_picture(api, admin):
    import base64
    import io

    from PIL import Image

    item = api.post("/api/admin/library", json={"kind": "blog", "title": "A blog with a picture"}, headers=admin).json()
    png = io.BytesIO()
    Image.new("RGB", (1600, 900), (40, 120, 200)).save(png, "PNG")
    data = "data:image/png;base64," + base64.b64encode(png.getvalue()).decode()
    learner, _ = signup(api, "nopic")
    assert api.put(f"/api/admin/library/{item['id']}/image", json={"data": data}, headers=learner).status_code == 403
    done = api.put(f"/api/admin/library/{item['id']}/image", json={"data": data}, headers=admin).json()
    assert done["image"].startswith(f"upload-{item['id']}-") and done["image"].endswith(".webp")
    got = api.get(f"/api/library/images/{done['image']}")
    assert got.status_code == 200
    assert Image.open(io.BytesIO(got.content)).size == (800, 450)  # resized, stored as WebP
    bad = base64.b64encode(b"not a picture at all").decode()
    assert api.put(f"/api/admin/library/{item['id']}/image", json={"data": bad}, headers=admin).status_code == 422
    assert api.delete(f"/api/admin/library/{item['id']}/image", headers=admin).json()["image"] == ""
    api.delete(f"/api/admin/library/{item['id']}", headers=admin)
