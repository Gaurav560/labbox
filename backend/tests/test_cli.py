"""tools/labbox_cli.py: validate, new-lab and test-lab."""
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("labbox_cli", ROOT / "tools" / "labbox_cli.py")
assert _spec and _spec.loader
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)

LABS_DIR = ROOT / "labs"


@pytest.fixture
def labs_dir(tmp_path: Path) -> Path:
    for name in ("python-basics", "java-basics", "fastapi-first-api"):
        shutil.copytree(LABS_DIR / name, tmp_path / name)
    return tmp_path


def errors(folder: Path) -> list[str]:
    return cli.validate_lab(folder, check_image=False).errors


def test_real_labs_are_valid():
    assert cli.main(["validate", "--no-docker"]) == 0
    for name in ("python-basics", "java-basics"):
        rep = cli.validate_lab(LABS_DIR / name, check_image=False)
        assert rep.errors == [] and rep.warnings == []


def test_missing_solution(labs_dir: Path):
    shutil.rmtree(labs_dir / "python-basics" / "solution")
    assert any("solution/" in e for e in errors(labs_dir / "python-basics"))


def test_too_few_hints(labs_dir: Path):
    path = labs_dir / "python-basics" / "lab.yaml"
    data = yaml.safe_load(path.read_text())
    data["chapters"][0]["tasks"][1]["hints"] = data["chapters"][0]["tasks"][1]["hints"][:2]
    path.write_text(yaml.safe_dump(data))
    assert errors(labs_dir / "python-basics") == ["chapter 01-functions: task 'add' has 2 hints, needs 3"]


def test_em_dash(labs_dir: Path):
    ch = labs_dir / "java-basics" / "chapters" / "01-methods.md"
    ch.write_text(ch.read_text() + "\nOne more thing \u2014 really.\n")
    assert any("01-methods.md:" in e and "em dash" in e for e in errors(labs_dir / "java-basics"))


def test_task_without_step(labs_dir: Path):
    ch = labs_dir / "python-basics" / "chapters" / "01-functions.md"
    ch.write_text(ch.read_text().replace(":::step{type=task task=add ", ":::step{type=concept "))
    assert any("'add' has no task step" in e for e in errors(labs_dir / "python-basics"))


def test_schema_errors_are_reported(labs_dir: Path):
    path = labs_dir / "python-basics" / "lab.yaml"
    path.write_text(path.read_text() + "runtime: sysbox\n")
    assert any("runtime: sysbox needs Phase F" in e for e in errors(labs_dir / "python-basics"))
    assert cli.main(["--labs-dir", str(labs_dir), "validate", "--no-docker"]) == 1


def test_unknown_prerequisite_warns(labs_dir: Path):
    path = labs_dir / "java-basics" / "lab.yaml"
    path.write_text(path.read_text() + "prerequisites: [core-java]\n")
    rep = cli.validate_lab(labs_dir / "java-basics", check_image=False, known_labs={"java-basics", "python-basics"})
    assert rep.errors == [] and any("core-java" in w for w in rep.warnings)


@pytest.mark.parametrize("template", ["python", "java", "ai", "system-design"])
def test_new_lab_is_valid(tmp_path: Path, template: str):
    assert cli.main(["--labs-dir", str(tmp_path), "new-lab", f"my-{template}", "--template", template, "--track", "languages"]) == 0
    rep = cli.validate_lab(tmp_path / f"my-{template}", check_image=False)
    assert rep.errors == [], rep.errors
    assert "{{" not in (tmp_path / f"my-{template}" / "lab.yaml").read_text()


def test_new_lab_refuses(tmp_path: Path):
    assert cli.main(["--labs-dir", str(tmp_path), "new-lab", "Bad_Id"]) == 2
    assert cli.main(["--labs-dir", str(tmp_path), "new-lab", "ok-lab"]) == 0
    assert cli.main(["--labs-dir", str(tmp_path), "new-lab", "ok-lab"]) == 2  # exists


@pytest.mark.docker
@pytest.mark.parametrize("lab", ["python-basics", "java-basics", "fastapi-first-api", "spring-boot-first-api", "postgres-indexing-incident", "javascript-inside-out", "go-basics", "sql-from-zero", "express-api", "redis-in-practice", "linux-on-call", "git-without-fear", "postgres-transactions-and-locks", "rate-limiter"])  # one or more per template
def test_test_lab(lab: str, capsys):
    """Starter fails every task, solution passes every task (image must be built)."""
    from tests.test_e2e_docker import _docker_ready

    if not _docker_ready():
        pytest.skip("Docker or lab images not available")
    assert cli.main(["test-lab", lab, "--no-build"]) == 0
    assert "starter fails every task, solution passes every task" in capsys.readouterr().out


@pytest.mark.docker
def test_test_lab_catches_a_wrong_solution(labs_dir: Path, capsys):
    from tests.test_e2e_docker import _docker_ready

    if not _docker_ready():
        pytest.skip("Docker or lab images not available")
    (labs_dir / "python-basics" / "solution" / "math_utils.py").write_text("def add(a, b):\n    return a - b\n")
    assert cli.main(["--labs-dir", str(labs_dir), "test-lab", "python-basics", "--no-build"]) == 1
    out = capsys.readouterr().out
    assert "add: should PASS on solution" in out and "is_even: should PASS on solution" in out


def test_cover_writes_lab_yaml(labs_dir: Path):
    """--pick sets cover and cover_credit in lab.yaml as text and the lab still loads."""
    folder = labs_dir / "python-basics"
    (folder / "cover.jpg").write_bytes(b"\xff\xd8\xff fake jpeg")
    credit = {"by": 'Ravi "Coffee" Kumar', "url": "https://www.pexels.com/photo/1/", "source": "Pexels"}
    cli._yaml_set_cover(folder / "lab.yaml", credit)
    cli._yaml_set_cover(folder / "lab.yaml", credit)  # again: replaces, never duplicates
    text = (folder / "lab.yaml").read_text()
    assert text.count("cover: cover.jpg") == 1 and text.count("cover_credit:") == 1
    lab = cli.load_lab(folder)
    assert lab.cover == "cover.jpg" and lab.cover_credit and lab.cover_credit.by == 'Ravi "Coffee" Kumar'


def test_cover_needs_a_key(capsys, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "PEXELS_API_KEY", "")
    assert cli.main(["cover", "python-basics", "--query", "coffee"]) == 2
    assert "PEXELS_API_KEY" in capsys.readouterr().out


def test_generate_and_pick_cover(labs_dir: Path, tmp_path: Path, monkeypatch, capsys):
    """--generate calls the image API with the house style prompt, --pick saves a small WebP."""
    import base64
    import io

    from PIL import Image

    from app.config import get_settings

    buf = io.BytesIO()
    Image.new("RGB", (1376, 768), (20, 30, 90)).save(buf, "PNG")
    fake_png = base64.b64encode(buf.getvalue()).decode()
    seen = {}

    class Resp:
        status_code = 200
        text = "{}"

        def json(self):
            return {"steps": [{"type": "model_output", "content": [{"type": "image", "mime_type": "image/png", "data": fake_png}]}]}

    def fake_post(url, headers, json, timeout):
        seen.update(url=url, headers=headers, body=json)
        return Resp()

    import httpx

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(get_settings(), "OPENAI_API_KEY", "")
    monkeypatch.setattr(get_settings(), "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(cli, "COVERS_DIR", tmp_path / "covers")

    assert cli.main(["--labs-dir", str(labs_dir), "cover", "fastapi-first-api", "--generate", "--count", "2"]) == 0
    prompt = seen["body"]["input"][0]["text"]
    assert "isometric 3D diorama" in prompt and "teal and cyan" in prompt and "coffee stall" in prompt
    assert seen["headers"]["x-goog-api-key"] == "test-key" and seen["body"]["response_format"]["aspect_ratio"] == "16:9"

    assert cli.main(["--labs-dir", str(labs_dir), "cover", "fastapi-first-api", "--pick", "2"]) == 0
    folder = labs_dir / "fastapi-first-api"
    cover = folder / "cover.webp"
    assert cover.is_file() and cover.stat().st_size < 512 * 1024
    assert Image.open(cover).size == (1200, round(768 * 1200 / 1376))
    lab = cli.load_lab(folder)
    assert lab.cover == "cover.webp" and lab.cover_credit and lab.cover_credit.url == ""


def test_generate_with_openai(labs_dir: Path, tmp_path: Path, monkeypatch):
    import base64
    import io

    import httpx
    from PIL import Image

    from app.config import get_settings

    buf = io.BytesIO()
    Image.new("RGB", (1536, 1024), (90, 20, 60)).save(buf, "WEBP")
    seen = {}

    class Resp:
        status_code = 200
        text = "{}"

        def json(self):
            return {"data": [{"b64_json": base64.b64encode(buf.getvalue()).decode()}]}

    def fake_post(url, headers, json, timeout):
        seen.update(url=url, headers=headers, body=json)
        return Resp()

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(get_settings(), "OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(cli, "COVERS_DIR", tmp_path / "covers")
    assert cli.main(["--labs-dir", str(labs_dir), "cover", "python-basics", "--generate", "--count", "1", "--quality", "high"]) == 0
    assert seen["url"] == cli.OPENAI_URL and seen["headers"]["Authorization"] == "Bearer sk-test"
    assert seen["body"]["model"] == "gpt-image-2" and seen["body"]["size"] == "1536x1024" and seen["body"]["quality"] == "high"
    scene = cli.load_lab(labs_dir / "python-basics").cover_scene
    assert scene and scene in seen["body"]["prompt"] and "electric violet" in seen["body"]["prompt"]
    assert cli.main(["--labs-dir", str(labs_dir), "cover", "python-basics", "--pick", "1"]) == 0
    lab = cli.load_lab(labs_dir / "python-basics")
    assert lab.cover == "cover.webp" and lab.cover_credit.by == "Generated with OpenAI"


def test_logo_cover(labs_dir: Path, capsys):
    import xml.etree.ElementTree as ET

    folder = labs_dir / "fastapi-first-api"
    assert cli.main(["--labs-dir", str(labs_dir), "cover", "fastapi-first-api", "--logo", "fastapi,python"]) == 0
    svg = (folder / "cover.svg").read_text()
    ET.fromstring(svg)  # valid XML, or the browser shows a broken image
    assert "#009688" in svg and "<script" not in svg  # FastAPI's brand teal, no scripts
    assert not any((folder / f"cover.{x}").exists() for x in ("webp", "jpg", "png"))
    lab = cli.load_lab(folder)
    assert lab.cover == "cover.svg" and lab.cover_credit.source == "devicon (MIT)"
    assert cli.main(["--labs-dir", str(labs_dir), "cover", "fastapi-first-api", "--logo", "cobol"]) == 2
    assert "Use one or two of" in capsys.readouterr().out


def test_every_logo_makes_a_valid_cover():
    sys.path.insert(0, str(ROOT / "tools"))
    import logo_cover

    for name in logo_cover.known_logos():
        logo_cover.build_cover([name, "python"], name)


def test_generate_needs_a_key(capsys, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "OPENAI_API_KEY", "")
    monkeypatch.setattr(get_settings(), "GEMINI_API_KEY", "")
    assert cli.main(["cover", "python-basics", "--generate"]) == 2
    assert "OPENAI_API_KEY" in capsys.readouterr().out


SPEC = """
id: demo-spec-lab
template: node
title: "Demo spec lab"
subtitle: A lab made from a spec.
track: languages
tags: [javascript]
story:
  company: Dabba Express
  character: { name: Priya, role: Founder }
  pitch: Priya needs help.
cover_scene: "A tiny tiffin bicycle at night."
chapters:
  - id: 01-first
    title: First chapter
    minutes: 15
    goal: Make the first function work.
    tasks:
      - id: sum_bill
        title: "bill.js: add up a bill"
        hints: ["Look at the function.", "Loop over the items.", "Keep a running total."]
  - id: 02-second
    title: Second chapter
    tasks:
      - id: split_bill
        title: "bill.js: split it"
        hints: ["One.", "Two.", "Three."]
"""


def test_new_lab_from_spec(tmp_path: Path):
    spec = tmp_path / "demo.yaml"
    spec.write_text(SPEC)
    labs = tmp_path / "labs"
    labs.mkdir()
    assert cli.main(["--labs-dir", str(labs), "new-lab", "--from-spec", str(spec)]) == 0
    folder = labs / "demo-spec-lab"
    lab = cli.load_lab(folder)  # loads: schema, chapters and task steps all line up
    assert [c.id for c in lab.chapters] == ["01-first", "02-second"]
    assert lab.track == "languages" and lab.image == "labbox/demo-spec-lab:v1" and lab.cover_scene
    assert [s.type for s in lab.chapter_steps("01-first")] == ["story", "concept", "predict", "try", "task", "recap"]
    rep = cli.validate_lab(folder, check_image=False)
    assert any("TODO(author)" in w for w in rep.warnings) and any("AUTHORING.md" in w for w in rep.warnings)
    strict = cli.validate_lab(folder, check_image=False, strict=True)
    assert strict.errors  # not finished, so the CI gate refuses it
    assert "sum_bill" in (folder / "AUTHORING.md").read_text()


def test_hint_that_gives_away_the_answer_is_an_error(labs_dir: Path):
    path = labs_dir / "python-basics" / "lab.yaml"
    path.write_text(path.read_text().replace("Python adds numbers with the + operator.", "Write: return a + b"))
    errors = cli.validate_lab(labs_dir / "python-basics", check_image=False).errors
    assert any("contains a solution line" in e and "return a + b" in e for e in errors)


def test_real_labs_pass_the_strict_gate():
    for folder in sorted(p for p in LABS_DIR.iterdir() if (p / "lab.yaml").is_file()):
        assert cli.validate_lab(folder, check_image=False, strict=True).errors == [], folder.name
