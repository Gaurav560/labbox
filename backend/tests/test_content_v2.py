"""Content format v2: lab.yaml v2 fields, unbuilt features, answer redaction, predict and outline routes,
@@METRIC parsing, and solution privacy."""
import random
import shutil
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from app import containers, labs
from app.checker import parse_metrics
from app.config import get_settings
from app.db import init_db
from app.labs import LabError, load_lab, load_labs
from app.main import app

LABS_DIR = Path(__file__).resolve().parents[2] / "labs"
LAB, CH = "python-basics", "01-functions"
PREDICT_STEP = 2  # "Guess first" in python-basics
EXPLAIN_TEXT = "Python's way of saying"


@pytest.fixture
def lab_copy(tmp_path: Path) -> Path:
    dst = tmp_path / LAB
    shutil.copytree(LABS_DIR / LAB, dst)
    return dst


def edit(folder: Path, fn) -> None:
    data = yaml.safe_load((folder / "lab.yaml").read_text())
    fn(data)
    (folder / "lab.yaml").write_text(yaml.safe_dump(data))


# ---------- lab.yaml v2 ----------


def test_v1_defaults(lab_copy: Path):
    """A lab.yaml without any v2 key still loads, with v2 defaults."""
    def to_v1(d):
        for k in ("version", "subtitle", "track", "tags", "level", "estimated_minutes", "story"):
            d.pop(k, None)  # a lab may have no story (plain beginner courses)
        for c in d["chapters"]:
            c.pop("minutes")

    edit(lab_copy, to_v1)
    lab = load_lab(lab_copy)
    assert lab.version == 1 and lab.level is None and lab.story is None
    assert (lab.track, lab.free_chapters, lab.services, lab.check.mode, lab.runtime) == ("languages", 2, [], "fresh", "default")
    assert all(t.xp == 20 for c in lab.chapters for t in c.tasks)


def test_v2_catalog_fields(lab_copy: Path):
    def v2(d):
        d.update(
            version=2,
            subtitle="Fix real bugs",
            track="frameworks",
            tags=["python", "fastapi"],
            level="intermediate",
            estimated_minutes=240,
            free_chapters=1,
            prerequisites=["java-basics"],
            story={"company": "Tapri Counter", "character": {"name": "Meera", "role": "CTO"}, "pitch": "Lunch rush."},
        )
        del d["description"], d["language"]
        d["chapters"][0]["minutes"] = 15

    edit(lab_copy, v2)
    lab = load_lab(lab_copy)
    assert lab.track == "frameworks" and lab.level == "intermediate" and lab.story and lab.story.character
    assert lab.description == "Fix real bugs" and lab.language == "python"  # filled from subtitle and tags
    assert lab.chapters[0].minutes == 15


def test_bad_track(lab_copy: Path):
    edit(lab_copy, lambda d: d.update(track="cooking"))
    with pytest.raises(LabError, match="track"):
        load_lab(lab_copy)


@pytest.mark.parametrize(
    "change, phase",
    [
        (lambda d: d.update(runtime="sysbox"), "runtime: sysbox needs Phase F"),
        (lambda d: d["resources"].update(disk_mb=1024), "disk_mb needs Phase H"),
        (lambda d: d["workspace"].update(sudo=True), "sudo needs Phase F"),
    ],
)
def test_unbuilt_features_are_refused(lab_copy: Path, change, phase: str):
    edit(lab_copy, change)
    with pytest.raises(LabError, match=phase):
        load_lab(lab_copy)


def test_phase_d_features_load(lab_copy: Path):
    def d(data):
        data["resources"] = "m"
        data["services"] = [{"name": "db", "image": "postgres:16", "ready": ["pg_isready"], "data": "/var/lib/postgresql/data"}]
        data["preview"] = [{"name": "App", "port": 8000}]
        data["workspace"].update(network="lab", env={"PGHOST": "db"})
        data["check"].update(mode="live")
        data["chapters"][0].update(setup=["bash", "/lab/setup/01.sh"])

    edit(lab_copy, d)
    lab = load_lab(lab_copy)
    assert (lab.resources.cpus, lab.resources.memory, lab.resources.pids_limit) == (2, "2g", 1024)
    assert lab.uses_lab_network and lab.services[0].user == "1000:1000"


@pytest.mark.parametrize(
    "change, match",
    [
        (lambda d: d.update(resources="xxl"), "unknown tier"),
        (lambda d: d.update(services=[{"name": "workspace", "image": "redis:7"}]), "bad service name"),
        (lambda d: d.update(services=[{"name": "db", "image": "x"}, {"name": "db", "image": "y"}]), "duplicate service"),
        (lambda d: d.update(services=[{"name": "db", "image": "x", "cap_add": ["SYS_ADMIN"]}]), "cap_add may only"),
        (lambda d: d.update(services=[{"name": "db", "image": "x", "cap_add": ["CHOWN"]}]), "only allowed with user: default"),
        (lambda d: d["check"].update(mode="live"), "live needs services"),
        (lambda d: d["workspace"].update(network_egress=True), "network_egress only applies"),
        (lambda d: d["chapters"][0].update(setup=["x"], setup_target="db"), "is not a service"),
        (lambda d: d["chapters"][0].update(setup=["x"], setup_user="admin"), "setup_user"),
    ],
)
def test_bad_phase_d_config(lab_copy: Path, change, match: str):
    edit(lab_copy, change)
    with pytest.raises(LabError, match=match):
        load_lab(lab_copy)


def test_llm_labs_load_and_get_a_lab_network(lab_copy: Path):
    edit(lab_copy, lambda d: d.update(llm={"enabled": True}))
    lab = load_lab(lab_copy)
    assert lab.llm.enabled and lab.uses_lab_network  # the gateway relay lives on the lab network


def test_engine_fields_at_defaults_are_fine(lab_copy: Path):
    edit(lab_copy, lambda d: d.update(runtime="default", llm={"enabled": False}, services=[], preview=[]))
    load_lab(lab_copy)


# ---------- @@METRIC ----------


def test_parse_metrics():
    logs = "\n".join(
        [
            '@@METRIC {"name": "p95_ms", "value": 1840, "target": 200, "better": "lower"}',
            "@@METRIC not json",
            '@@METRIC {"name": "rps", "value": 90}',
            '@@METRIC {"name": "p95_ms", "value": 150, "target": 200, "better": "lower"}',
            '@@METRIC {"name": "bad", "value": "fast"}',
        ]
    )
    assert [(m.name, m.value) for m in parse_metrics(logs)] == [("p95_ms", 150), ("rps", 90)]


# ---------- routes ----------


@pytest.fixture(scope="module")
def client() -> TestClient:
    labs.init_labs(get_settings().LABS_DIR)
    init_db()
    return TestClient(app)


def auth(client: TestClient) -> dict:
    r = client.post("/api/auth/signup", json={"username": f"v2u{random.randint(0, 10**9)}", "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_lab_list_has_catalog_fields(client: TestClient):
    lab = next(x for x in client.get("/api/labs", headers=auth(client)).json() if x["id"] == LAB)
    assert lab["track"] == "languages" and lab["level"] == "beginner" and lab["estimated_minutes"] >= 15


def test_predict_answer_is_not_in_the_chapter(client: TestClient):
    body = client.get(f"/api/labs/{LAB}/chapters/{CH}", headers=auth(client)).json()
    predict = body["steps"][PREDICT_STEP]["predict"]
    assert set(predict) == {"question", "options"}
    assert "[x]" not in body["markdown"] and "[X]" not in body["markdown"]
    assert EXPLAIN_TEXT not in body["markdown"] and EXPLAIN_TEXT not in str(body["steps"])
    assert "- [ ] `None`" in body["markdown"]  # the option itself is still there, unticked


def test_outline(client: TestClient):
    out = client.get(f"/api/labs/{LAB}/chapters/{CH}/outline", headers=auth(client)).json()
    assert out["steps"][0] == {"type": "story", "title": "Why start with functions", "task": None}
    assert [s["task"] for s in out["steps"] if s["type"] == "task"] == ["greet", "add", "is_even"]
    assert len(out["steps"]) == 9
    assert client.get(f"/api/labs/{LAB}/chapters/{CH}/outline").status_code == 401


def test_predict_flow(client: TestClient):
    h = auth(client)
    url = f"/api/labs/{LAB}/chapters/{CH}/predict"
    wrong = client.post(url, json={"step": PREDICT_STEP, "choice": 3}, headers=h).json()
    assert wrong == {"wrong": [3], "solved": False, "answer": None, "explain": None, "xp_awarded": []}
    right = client.post(url, json={"step": PREDICT_STEP, "choice": 2}, headers=h).json()
    assert right["solved"] and right["answer"] == 2 and EXPLAIN_TEXT in right["explain"] and right["wrong"] == [3]
    # Remembered for a reload, and only for this user.
    progress = client.get(f"/api/labs/{LAB}/chapters/{CH}/progress", headers=h).json()
    assert progress["predicts"][str(PREDICT_STEP)]["solved"] is True
    assert client.get(f"/api/labs/{LAB}/chapters/{CH}/progress", headers=auth(client)).json()["predicts"] == {}


def test_predict_bad_input(client: TestClient):
    h = auth(client)
    url = f"/api/labs/{LAB}/chapters/{CH}/predict"
    assert client.post(url, json={"step": 0, "choice": 0}, headers=h).status_code == 404  # a story step
    assert client.post(url, json={"step": 99, "choice": 0}, headers=h).status_code == 404
    assert client.post(url, json={"step": PREDICT_STEP, "choice": 9}, headers=h).status_code == 422
    assert client.post(url, json={"step": PREDICT_STEP, "choice": -1}, headers=h).status_code == 422
    assert client.post(f"/api/labs/{LAB}/chapters/nope/predict", json={"step": 2, "choice": 0}, headers=h).status_code == 404
    assert client.post(url, json={"step": PREDICT_STEP, "choice": 2}).status_code == 401


# ---------- solution privacy ----------


def test_solution_is_never_seeded(tmp_path: Path):
    for lab in load_labs(LABS_DIR).values():
        folder = tmp_path / lab.id
        folder.mkdir()
        containers.seed(lab, folder)
        seeded = {p.relative_to(folder) for p in folder.rglob("*")}
        assert seeded == {p.relative_to(lab.starter_dir) for p in lab.starter_dir.rglob("*")}
        # Solution files that differ from the starter (the actual answers) never reach a workspace.
        for f in (lab.root / "solution").rglob("*"):
            rel = f.relative_to(lab.root / "solution")
            starter = lab.starter_dir / rel
            if not f.is_file() or (starter.is_file() and starter.read_bytes() == f.read_bytes()):
                continue
            seeded_file = folder / rel
            assert not seeded_file.is_file() or seeded_file.read_bytes() != f.read_bytes(), f"{lab.id}: solution {rel} seeded"


def test_solution_and_tests_stay_out_of_images():
    for lab in load_labs(LABS_DIR).values():
        ignored = (lab.root / ".dockerignore").read_text().split()
        assert "solution/" in ignored and "tests/" in ignored, lab.id


def test_no_route_serves_solution_files(client: TestClient):
    h = auth(client)
    lab = labs.get_lab(LAB)
    solution_text = (lab.root / "solution" / "greet.py").read_text().strip().splitlines()[-1].strip()
    for path in ["", "/chapters/01-functions", "/chapters/01-functions/outline", "/chapters/01-functions/progress"]:
        assert solution_text not in client.get(f"/api/labs/{LAB}{path}", headers=h).text


def test_public_catalog_needs_no_login_and_leaks_nothing(client: TestClient):
    r = client.get("/api/catalog")
    assert r.status_code == 200
    by_id = {lab["id"]: lab for lab in r.json()}
    assert {"python-basics", "java-basics", "postgres-indexing-incident"} <= set(by_id)
    assert set(by_id["python-basics"]) == {"id", "title", "subtitle", "track", "tags", "level", "estimated_minutes", "chapter_count", "cover_url", "cover_credit"}
    lab = labs.get_lab("python-basics")
    hidden = [h for c in lab.chapters for t in c.tasks for h in t.hints]
    hidden += [(lab.root / "solution" / "greet.py").read_text().strip().splitlines()[-1].strip(), "chapters/", "@@RESULT"]
    for text in hidden:
        assert text not in r.text


# ---------- cover images ----------


def test_cover_validation(lab_copy: Path):
    (lab_copy / "cover.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    edit(lab_copy, lambda d: d.update(cover="cover.svg"))
    assert load_lab(lab_copy).cover == "cover.svg"
    for bad, match in [("nope.png", "cover image missing"), ("../../etc/passwd", "cover image missing"), ("lab.yaml", "cover must be")]:
        edit(lab_copy, lambda d: d.update(cover=bad))
        with pytest.raises(LabError, match=match):
            load_lab(lab_copy)
    (lab_copy / "big.png").write_bytes(b"x" * (600 * 1024))
    edit(lab_copy, lambda d: d.update(cover="big.png"))
    with pytest.raises(LabError, match="larger than"):
        load_lab(lab_copy)


def test_cover_route(client: TestClient):
    lab = labs.get_lab("python-basics")
    assert lab.cover  # the lab ships its own cover
    r = client.get("/api/labs/python-basics/cover")  # public, no login
    assert r.status_code == 200 and r.headers["content-type"].startswith("image/svg+xml")
    assert "sandbox" in r.headers["content-security-policy"] and r.headers["x-content-type-options"] == "nosniff"
    by_id = {x["id"]: x for x in client.get("/api/catalog").json()}
    url = by_id["python-basics"]["cover_url"]
    assert url.startswith("/api/labs/python-basics/cover?v=")  # versioned: a new cover skips the browser cache
    assert client.get(url).status_code == 200
    saved = lab.cover
    try:
        lab.cover = None  # a lab without its own image: no route, the UI draws a cover
        assert client.get("/api/labs/python-basics/cover").status_code == 404
    finally:
        lab.cover = saved
