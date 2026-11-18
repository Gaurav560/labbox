"""labbox: authoring tools for lab writers.

    scripts/labbox new-lab <id> --track languages --template python
    scripts/labbox validate [lab_id] [--no-docker]
    scripts/labbox test-lab <lab_id> [--no-build]
    scripts/labbox preview <lab_id>
    scripts/labbox cover <lab_id> --logo redis[,python]   (real logos on brand colours)
    scripts/labbox cover <lab_id> --generate              (AI art, then --pick N)
    scripts/labbox cover <lab_id> --query "chai stall"   (stock photo, then --pick N)

Runs with the backend's virtualenv and reuses the backend's own lab loader and checker,
so a lab that passes here behaves the same in the app.
"""
import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
TEMPLATES = Path(__file__).resolve().parent / "templates"
sys.path.insert(0, str(BACKEND))
if not (BACKEND / ".env").exists():
    # validate and test-lab never sign tokens; a dummy secret lets the settings load in CI.
    os.environ.setdefault("JWT_SECRET", "labbox-cli-without-env-file")

from app.labs import ID_RE, LabConfig, LabError, Track, load_lab  # noqa: E402

EM_DASH = "\u2014"
TRACKS: tuple[str, ...] = Track.__args__  # type: ignore[attr-defined]
# python, java, node, go: code exercises with fresh checks.
# service-incident: a Postgres service, an injected failure and a live check.
# preview-app: a FastAPI app shown in the Preview tab.
TEMPLATES_READY = ["python", "java", "node", "go", "service-incident", "preview-app"]
TEMPLATE_LATER = {
    "ai": "Phase E (LLM gateway)",
    "system-design": "Phase G (k6 load tests)",
}
HINTS_PER_TASK = 3


@dataclass
class Report:
    lab: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


AUTHOR_TODO = "TODO(author)"
CONCEPT_MAX_WORDS = 120
_CODE_BLOCK_RE = re.compile(r"```.*?```", re.S)
_DIRECTIVE_LINE_RE = re.compile(r"^\s*:::.*$", re.M)


def _words(markdown: str) -> int:
    text = _DIRECTIVE_LINE_RE.sub(" ", _CODE_BLOCK_RE.sub(" ", markdown))
    return len(re.findall(r"[A-Za-z0-9`'_-]+", text))


def _solution_lines(folder: Path) -> set[str]:
    """Meaningful lines of the solution that differ from the starter (what a hint must not give away)."""
    sol, starter = folder / "solution", folder / "starter"
    lines: set[str] = set()
    for f in sol.rglob("*") if sol.is_dir() else []:
        if not f.is_file() or f.suffix in {".xml", ".mod", ".md", ".json"}:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        old = (starter / f.relative_to(sol))
        before = set(old.read_text(encoding="utf-8").splitlines()) if old.is_file() else set()
        for ln in text.splitlines():
            s = ln.strip()
            if len(s) >= 10 and ln not in before and not s.startswith(("#", "//", "--", "import ", "package ", "from ")):
                lines.add(s)
    return lines


def content_lint(lab: LabConfig, folder: Path) -> tuple[list[str], list[str]]:
    """The content standard (v2 spec section 9), as far as a machine can check it. (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []
    answers = _solution_lines(folder)
    for ch in lab.chapters:
        for t in ch.tasks:
            for h in t.hints:
                leaked = [a for a in answers if a in h]
                if leaked:
                    errors.append(f"chapter {ch.id}: a hint for {t.id!r} contains a solution line: {leaked[0]!r}")
        steps = lab.chapter_steps(ch.id)
        if len(steps) == 1:
            continue
        types = [s.type for s in steps]
        if types[0] != "story":
            warnings.append(f"{ch.file}: the first step should be a story (it is {types[0]})")
        for needed in ("predict", "recap"):
            if needed not in types:
                warnings.append(f"{ch.file}: no {needed} step")
        for i, s in enumerate(steps, 1):
            if s.type in ("concept", "example") and _words(s.markdown) > CONCEPT_MAX_WORDS:
                warnings.append(f"{ch.file}: step {i} ({s.type}) has {_words(s.markdown)} words of text, keep it under {CONCEPT_MAX_WORDS}")
        if ch.minutes is None or not 8 <= ch.minutes <= 25:
            warnings.append(f"chapter {ch.id}: minutes should be 10 to 20 (is {ch.minutes})")
    for f in [folder / "lab.yaml", *sorted((folder / "chapters").rglob("*.md"))]:
        if f.is_file() and AUTHOR_TODO in f.read_text(encoding="utf-8"):
            warnings.append(f"{f.relative_to(folder)}: still has {AUTHOR_TODO} markers")
    if not lab.cover:
        warnings.append("no cover image yet (scripts/labbox cover <lab> --logo <tech>)")
    if (folder / "AUTHORING.md").exists():
        warnings.append("AUTHORING.md is still there (delete it when the lab is finished)")
    return errors, warnings


def _em_dashes(folder: Path) -> list[str]:
    """file:line for every em dash in the lab's text content (not starter, solution or tests code)."""
    found = []
    files = [folder / "lab.yaml", *sorted((folder / "chapters").rglob("*.md"))]
    for f in files:
        if not f.is_file():
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if EM_DASH in line:
                found.append(f"{f.relative_to(folder)}:{n}")
    return found


def _image_exists(image: str) -> bool | None:
    """True/False, or None when Docker is not reachable."""
    try:
        r = subprocess.run(["docker", "image", "inspect", image], capture_output=True)
    except FileNotFoundError:
        return None
    if r.returncode != 0 and b"Cannot connect" in r.stderr:
        return None
    return r.returncode == 0


def validate_lab(folder: Path, check_image: bool = True, known_labs: set[str] | None = None, strict: bool = False) -> Report:
    rep = Report(folder.name)
    try:
        lab = load_lab(folder)  # schema, chapter files, step parsing, task references, unbuilt features
    except LabError as e:
        rep.errors.append(str(e))
        return rep

    for ch in lab.chapters:
        steps = lab.chapter_steps(ch.id)
        if len(steps) == 1:
            rep.warnings.append(f"{ch.file}: no :::step markers (v1 chapter, shown as one long step)")
        else:
            in_steps = {s.task for s in steps if s.task}
            for t in ch.tasks:
                if t.id not in in_steps:
                    rep.errors.append(f"{ch.file}: task {t.id!r} has no task step (add :::step{{type=task task={t.id}}})")
            if not any(s.type == "recap" for s in steps):
                rep.warnings.append(f"{ch.file}: no recap step")
        for t in ch.tasks:
            if len(t.hints) != HINTS_PER_TASK:
                rep.errors.append(f"chapter {ch.id}: task {t.id!r} has {len(t.hints)} hints, needs {HINTS_PER_TASK}")
            if any(not h.strip() for h in t.hints):
                rep.errors.append(f"chapter {ch.id}: task {t.id!r} has an empty hint")

    for where in _em_dashes(folder):
        rep.errors.append(f"{where}: em dash (use a comma, colon or full stop instead)")

    solution = folder / "solution"
    if not solution.is_dir() or not any(solution.iterdir()):
        rep.errors.append("solution/ is missing or empty (test-lab and CI need it)")
    if not lab.starter_dir.is_dir():
        rep.warnings.append("starter/ is missing (new workspaces start empty)")

    tests_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in lab.tests_dir.rglob("*") if p.is_file())
    for t in (t for c in lab.chapters for t in c.tasks):
        if not re.search(rf"\b{re.escape(t.id)}\b", tests_text):
            rep.warnings.append(f"task {t.id!r} is never mentioned in tests/ (it will always fail)")

    for pre in lab.prerequisites:
        if known_labs is not None and pre not in known_labs:
            rep.warnings.append(f"prerequisite {pre!r} is not a lab in this repo")

    lint_errors, lint_warnings = content_lint(lab, folder)
    rep.errors += lint_errors
    rep.warnings += lint_warnings

    if check_image:
        exists = _image_exists(lab.image)
        if exists is None:
            rep.warnings.append("Docker is not reachable: image not checked")
        elif not exists:
            rep.errors.append(f"image {lab.image} is not built (bash scripts/build_lab_images.sh)")
    if strict:  # the CI quality gate: every warning must be fixed
        rep.errors += rep.warnings
        rep.warnings = []
    return rep


def _lab_folders(labs_dir: Path, lab_id: str | None) -> list[Path]:
    if lab_id:
        folder = labs_dir / lab_id
        if not (folder / "lab.yaml").is_file():
            sys.exit(f"No lab {lab_id!r} in {labs_dir}")
        return [folder]
    return sorted(p for p in labs_dir.iterdir() if (p / "lab.yaml").is_file())


def _print_report(rep: Report) -> None:
    mark = "✗" if rep.errors else "✓"
    print(f"{mark} {rep.lab}")
    for e in rep.errors:
        print(f"    error:   {e}")
    for w in rep.warnings:
        print(f"    warning: {w}")


# ---------- commands ----------


def validate_content(labs_dir: Path) -> Report:
    """Skill maps, drills and onboarding next to the labs folder (they refer to labs and chapters)."""
    from app.content import load_content
    from app.labs import init_labs

    rep = Report("tracks, drills, onboarding")
    try:
        init_labs(labs_dir)
        load_content(labs_dir.parent)
    except LabError as e:
        rep.errors.append(str(e))
    for f in [*sorted((labs_dir.parent / "tracks").glob("*.yaml")), *sorted((labs_dir.parent / "drills").glob("*.yaml")),
              *sorted((labs_dir.parent / "onboarding").glob("*.yaml"))]:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if EM_DASH in line:
                rep.errors.append(f"{f.relative_to(labs_dir.parent)}:{n}: em dash (use a comma, colon or full stop instead)")
    return rep


def cmd_validate(args: argparse.Namespace) -> int:
    folders = _lab_folders(args.labs_dir, args.lab_id)
    known = {p.name for p in _lab_folders(args.labs_dir, None)}
    reports = [validate_lab(f, check_image=not args.no_docker, known_labs=known, strict=args.strict) for f in folders]
    for r in reports:
        _print_report(r)
    bad = sum(bool(r.errors) for r in reports)
    print(f"\n{len(reports) - bad} of {len(reports)} labs valid")
    if args.lab_id is None and not bad:
        content = validate_content(args.labs_dir)
        _print_report(content)
        bad += bool(content.errors)
    return 1 if bad else 0


# ---------- lab specs ----------
# specs/<lab>.yaml is the short form of a lab: story, chapters, tasks, hints, cover scene.
# `labbox new-lab --from-spec specs/<lab>.yaml` turns it into a lab folder from its template.


def _spec_models():
    from pydantic import BaseModel, ConfigDict, Field

    from app.labs import Story, Track

    class _S(BaseModel):
        model_config = ConfigDict(extra="forbid")

    class SpecTask(_S):
        id: str
        title: str
        xp: int = 20
        hints: list[str] = Field(min_length=3, max_length=3)

    class SpecChapter(_S):
        id: str
        title: str
        minutes: int = 15
        goal: str = ""  # one line: what the learner can do after this chapter
        tasks: list[SpecTask] = Field(min_length=1)

    class LabSpec(_S):
        id: str
        template: str
        title: str
        subtitle: str
        track: Track
        tags: list[str] = Field(min_length=1)
        level: str = "beginner"
        estimated_minutes: int | None = None
        story: Story
        cover_scene: str
        chapters: list[SpecChapter] = Field(min_length=1)

    return LabSpec


def _chapter_skeleton(spec, ch) -> str:
    who = spec.story.character
    name, role = (who.name, who.role) if who else ("TODO(author)", "")
    parts = [
        f':::step{{type=story title="{ch.title}"}}',
        f':::character{{name="{name}" role="{role}"}}',
        "TODO(author): two to four lines from the character. A real problem, today.",
        ":::",
        "",
        ":::mission",
        f"{ch.goal or 'TODO(author): one line, what the learner will make work.'}",
        ":::",
        ":::",
        "",
        ':::step{type=concept title="TODO(author)"}',
        "TODO(author): one idea, under 120 words, with a short code example.",
        ":::",
        "",
        ':::step{type=predict title="Guess first"}',
        ":::question",
        "TODO(author): a question whose answer surprises a little.",
        ":::",
        "- [ ] TODO(author)",
        "- [x] TODO(author)",
        "- [ ] TODO(author)",
        ":::explain",
        "TODO(author): why.",
        ":::",
        ":::",
        "",
        ':::step{type=try title="Try it"}',
        "TODO(author): a command to run and what to look for.",
        "",
        "```bash run",
        "echo TODO",
        "```",
        ":::",
        "",
    ]
    for t in ch.tasks:
        parts += [f':::step{{type=task task={t.id} title="{t.title}"}}',
                  "TODO(author): the goal in plain words, with one example input and output.", ":::", ""]
    parts += [":::step{type=recap}", "- TODO(author)", "- TODO(author)", "- TODO(author)", ":::", ""]
    return "\n".join(parts)


def new_lab_from_spec(spec_path: Path, labs_dir: Path) -> Path:
    import yaml

    LabSpec = _spec_models()
    spec = LabSpec.model_validate(yaml.safe_load(spec_path.read_text(encoding="utf-8")))
    if spec.template not in TEMPLATES_READY:
        raise SystemExit(f"Unknown template {spec.template!r}: use one of {', '.join(TEMPLATES_READY)}")
    if not ID_RE.match(spec.id):
        raise SystemExit(f"Bad lab id {spec.id!r}")
    dst = labs_dir / spec.id
    if dst.exists():
        raise SystemExit(f"{dst} already exists")
    shutil.copytree(TEMPLATES / spec.template, dst)
    for p in dst.rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            p.write_text(text.replace("{{lab_id}}", spec.id).replace("{{title}}", spec.title).replace("{{track}}", spec.track), encoding="utf-8")

    data = yaml.safe_load((dst / "lab.yaml").read_text(encoding="utf-8"))
    template_task_ids = [t["id"] for c in data["chapters"] for t in c["tasks"]]
    for old in (dst / "chapters").glob("*.md"):
        old.unlink()
    data.update(
        version=2, title=spec.title, subtitle=spec.subtitle, description=spec.subtitle, track=spec.track,
        tags=spec.tags, language=spec.tags[0], level=spec.level,
        estimated_minutes=spec.estimated_minutes or sum(c.minutes for c in spec.chapters),
        story=spec.story.model_dump(exclude_none=True), cover_scene=spec.cover_scene,
    )
    data["chapters"] = []
    for ch in spec.chapters:
        chapter = {"id": ch.id, "title": ch.title, "file": f"chapters/{ch.id}.md", "minutes": ch.minutes,
                   "tasks": [t.model_dump() for t in ch.tasks]}
        data["chapters"].append(chapter)
        (dst / "chapters" / f"{ch.id}.md").write_text(_chapter_skeleton(spec, ch), encoding="utf-8")
    (dst / "lab.yaml").write_text(
        "# Generated from " + spec_path.name + ". Edit freely; the spec is only the starting point.\n"
        + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=110),
        encoding="utf-8",
    )
    # The template's example task (and setup) belong to the template's own story: say so loudly.
    note = dst / "AUTHORING.md"
    note.write_text(
        f"# {spec.title}: still to write\n\n"
        f"Made from the `{spec.template}` template. Before this lab is done:\n\n"
        "1. Fill every TODO(author) in `chapters/`.\n"
        f"2. Replace the template's example task ({', '.join(template_task_ids)}) in `starter/`, `solution/` and `tests/` "
        "with this lab's tasks: " + ", ".join(t.id for c in spec.chapters for t in c.tasks) + ".\n"
        "3. `scripts/labbox validate " + spec.id + " --strict` and `scripts/labbox test-lab " + spec.id + "`.\n"
        "4. `scripts/labbox cover " + spec.id + " --logo <tech>[,<tech>]` (see tools/logo_cover.py for the list).\n"
        "5. Delete this file.\n",
        encoding="utf-8",
    )
    return dst


def cmd_new_lab(args: argparse.Namespace) -> int:
    if args.from_spec:
        dst = new_lab_from_spec(Path(args.from_spec), args.labs_dir)
        print(f"Created {dst} from {args.from_spec}. Next steps are in {dst / 'AUTHORING.md'}")
        return 0
    if not args.lab_id:
        print("Give a lab id, or --from-spec specs/<lab>.yaml")
        return 2
    if args.template in TEMPLATE_LATER:
        print(f"The {args.template!r} template arrives with {TEMPLATE_LATER[args.template]}. Use one of: {', '.join(TEMPLATES_READY)}.")
        return 2
    if not ID_RE.match(args.lab_id):
        print(f"Bad lab id {args.lab_id!r}: lowercase a-z, 0-9 and dashes only")
        return 2
    dst = args.labs_dir / args.lab_id
    if dst.exists():
        print(f"{dst} already exists")
        return 2
    title = args.title or args.lab_id.replace("-", " ").capitalize()
    shutil.copytree(TEMPLATES / args.template, dst)
    for p in dst.rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            text = text.replace("{{lab_id}}", args.lab_id).replace("{{title}}", title).replace("{{track}}", args.track)
            p.write_text(text, encoding="utf-8")
    print(f"Created {dst} from the {args.template} template. Next:")
    print(f"  1. Write the story, chapter and tests (see README: How to add a new lab)")
    print(f"  2. scripts/labbox validate {args.lab_id} --no-docker")
    print(f"  3. scripts/labbox test-lab {args.lab_id}")
    return 0


def _build(lab: LabConfig) -> bool:
    print(f"==> Building {lab.image}", flush=True)
    return subprocess.run(["docker", "build", "-q", "-t", lab.image, str(lab.root)]).returncode == 0


def _test_live(lab: LabConfig, folder: Path) -> bool:
    """live labs: a throwaway group (workspace + services) for a test user, then
    setup -> check must FAIL -> apply the solution -> check must PASS -> remove everything."""
    import tempfile
    import uuid

    from app import checker, containers, lab_setup, services, workspace_files
    from app.models import Workspace

    short = uuid.uuid4().hex[:6]
    tmp = Path(tempfile.mkdtemp(prefix=f"labbox-test-{lab.id}-"))
    vol = tmp / "workspace"
    vol.mkdir()
    workspace_files.chown(vol)
    ws = Workspace(user_id=0, lab_id=f"{lab.id}", container_name=f"labtest-{short}-{lab.id}", volume_path=str(vol))
    ok = True
    try:
        containers.seed(lab, vol)
        services.ensure_services(lab, ws)
        containers._create(lab, ws)
        for ch in lab.chapters:
            if ch.setup:
                lab_setup.exec_setup(lab, ws, ch)
        for label in ("starter", "solution"):
            if label == "solution":
                shutil.copytree(folder / "solution", vol, dirs_exist_ok=True)
                workspace_files.chown_tree(vol)
                if (vol / "apply.sh").is_file():
                    r = containers.client().containers.get(ws.container_name).exec_run(
                        ["bash", f"{lab.workspace.mount_path}/apply.sh"], user=containers.LEARNER_USER)
                    if r.exit_code != 0:
                        print(f"    ✗ solution/apply.sh failed: {r.output.decode(errors='replace')[-500:]}")
                        return False
            want = label == "solution"
            for ch in lab.chapters:
                res = checker.check_live(lab, ch.id, ws)
                print(f"  {ch.id} {label:8} {res.passed_count}/{res.total_count} passed ({res.duration_ms} ms, live)")
                for r in res.results:
                    if r.passed != want:
                        ok = False
                        print(f"    ✗ {r.task}: should {'PASS' if want else 'FAIL'} on {label}: {r.message}")
        return ok
    finally:
        for c in containers.client().containers.list(all=True, filters={"name": ws.container_name}):
            c.remove(force=True)
        services.remove_services(lab, ws, wipe_data=True)
        try:
            containers.client().networks.get(services.network_name(ws)).remove()
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(f"{vol}.services", ignore_errors=True)


def cmd_test_lab(args: argparse.Namespace) -> int:
    from app import checker
    from app.config import get_settings

    folder = _lab_folders(args.labs_dir, args.lab_id)[0]
    rep = validate_lab(folder, check_image=False)
    if rep.errors:
        _print_report(rep)
        return 1
    lab = load_lab(folder)
    if not args.no_build and not _build(lab):
        print("Image build failed")
        return 1
    get_settings().CHECKS_DIR.mkdir(parents=True, exist_ok=True)

    if lab.check.mode == "live":
        ok = _test_live(lab, folder)
        print(f"✓ {lab.id}: starter fails every task, solution passes every task" if ok else f"✗ {lab.id}")
        return 0 if ok else 1

    ok = True
    for ch in lab.chapters:
        for label, src, want in (("starter", lab.starter_dir, False), ("solution", folder / "solution", True)):
            res = checker.check_folder(lab, ch.id, src, user_id=0)
            print(f"  {ch.id} {label:8} {res.passed_count}/{res.total_count} passed ({res.duration_ms} ms)")
            for r in res.results:
                good = r.passed == want
                ok &= good
                if not good:
                    expect = "PASS" if want else "FAIL"
                    print(f"    ✗ {r.task}: should {expect} on {label}, got {'PASS' if r.passed else 'FAIL'}: {r.message}")
            if res.timed_out:
                ok = False
                print(f"    ✗ timed out on {label}")
    print(f"{'✓' if ok else '✗'} {lab.id}: starter fails every task, solution passes every task" if ok else f"✗ {lab.id}")
    return 0 if ok else 1


def cmd_preview(args: argparse.Namespace) -> int:
    from sqlmodel import Session, select

    from app.auth import hash_password
    from app.db import engine, init_db
    from app.models import User

    _lab_folders(args.labs_dir, args.lab_id)  # exits if unknown
    init_db()
    password = secrets.token_urlsafe(9)
    with Session(engine) as s:
        user = s.exec(select(User).where(User.username == args.user)).first()
        if user is None:
            user = User(username=args.user, password_hash=hash_password(password))
        else:
            user.password_hash = hash_password(password)  # a fresh password each run: this account is for previews only
        s.add(user)
        s.commit()
    url = f"{args.url.rstrip('/')}/labs/{args.lab_id}"
    print(f"Log in as {args.user} / {password}, then open {url}")
    print("(needs the backend and Vite running, see README)")
    if not args.no_browser:
        webbrowser.open(f"{args.url.rstrip('/')}/login")
    return 0


COVERS_DIR = Path(__file__).resolve().parent / ".covers"  # candidates for review, not committed
PEXELS_SEARCH = "https://api.pexels.com/v1/search"


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_API_REVISION = "2026-05-20"
COVER_WIDTH = 1200

# One house style for every cover, so 100+ labs look like one product.
HOUSE_STYLE = (
    "A tiny isometric 3D diorama on a floating square base, seen from a three-quarter top view, at night. "
    "Lit by glowing neon accents in {palette} and soft screen glow, gentle volumetric haze, tiny detailed "
    "props, miniature tilt-shift look, rich cinematic lighting, high detail 3D render. Deep navy background "
    "with a subtle gradient and a few floating glowing particles. The diorama sits slightly right of centre "
    "with calm empty space on the left. Absolutely no text, letters, numbers, logos or watermarks anywhere. "
    "Scene: {scene}"
)
TRACK_PALETTES = {
    "languages": "electric violet and indigo",
    "frameworks": "teal and cyan",
    "databases": "amber and hot magenta",
    "devops": "electric blue and white",
    "system-design": "indigo and ice blue",
    "ai": "magenta and pink",
    "interview": "emerald and lime",
}


def cover_prompt(lab: LabConfig) -> str:
    scene = lab.cover_scene
    if not scene:
        story = lab.story.pitch if lab.story else ""
        scene = f"{lab.title}. {lab.subtitle or lab.description} {story}".strip()
    return HOUSE_STYLE.format(palette=TRACK_PALETTES.get(lab.track, TRACK_PALETTES["languages"]), scene=scene)


def _find_image(obj) -> tuple[str, str] | None:
    """The first base64 image anywhere in an API response: (base64 data, mime type)."""
    if isinstance(obj, dict):
        data = obj.get("data") or (obj.get("inlineData") or obj.get("inline_data") or {}).get("data")
        mime = obj.get("mime_type") or obj.get("mimeType") or (obj.get("inlineData") or obj.get("inline_data") or {}).get("mimeType", "")
        if isinstance(data, str) and len(data) > 1000 and (obj.get("type") == "image" or str(mime).startswith("image/")):
            return data, str(mime or "image/png")
        for v in obj.values():
            found = _find_image(v)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_image(v)
            if found:
                return found
    return None


OPENAI_URL = "https://api.openai.com/v1/images/generations"


def image_provider(settings) -> tuple[str, str, str] | None:
    """(provider, key, model) for cover art: OpenAI when its key is set, else Gemini, else None."""
    if settings.OPENAI_API_KEY:
        return "openai", settings.OPENAI_API_KEY, settings.OPENAI_IMAGE_MODEL
    if settings.GEMINI_API_KEY:
        return "gemini", settings.GEMINI_API_KEY, settings.GEMINI_IMAGE_MODEL
    return None


def generate_image(prompt: str, provider: str, key: str, model: str, quality: str = "medium") -> bytes:
    import base64

    import httpx

    if provider == "openai":
        # gpt-image-2, 1536 x 1024: about $0.041 (medium) or $0.165 (high) per image.
        r = httpx.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "prompt": prompt, "size": "1536x1024", "quality": quality, "output_format": "webp", "n": 1},
            timeout=240,
        )
        if r.status_code != 200:
            raise RuntimeError(f"OpenAI answered {r.status_code}: {r.text[:400]}")
        data = (r.json().get("data") or [{}])[0].get("b64_json")
        if not data:
            raise RuntimeError(f"No image in the OpenAI response: {r.text[:400]}")
        return base64.b64decode(data)

    r = httpx.post(
        GEMINI_URL,
        headers={"x-goog-api-key": key, "Content-Type": "application/json", "Api-Revision": GEMINI_API_REVISION},
        json={
            "model": model,
            "input": [{"type": "text", "text": prompt}],
            "response_format": {"type": "image", "aspect_ratio": "16:9", "image_size": "1K"},
        },
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Gemini answered {r.status_code}: {r.text[:400]}")
    found = _find_image(r.json())
    if not found:
        raise RuntimeError(f"No image in the Gemini response: {r.text[:400]}")
    return base64.b64decode(found[0])


def to_cover(raw: bytes) -> bytes:
    """Resize to 1200 px wide and save as WebP, well under the 512 KB cover limit."""
    import io

    from PIL import Image

    img = Image.open(io.BytesIO(raw)).convert("RGB")
    if img.width > COVER_WIDTH:
        img = img.resize((COVER_WIDTH, round(img.height * COVER_WIDTH / img.width)), Image.LANCZOS)
    for quality in (86, 78, 70, 60):
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=quality, method=6)
        if buf.tell() <= 480 * 1024:
            return buf.getvalue()
    return buf.getvalue()


def _yaml_set_cover(lab_yaml: Path, credit: dict, filename: str = "cover.jpg") -> None:
    """Set cover and cover_credit in lab.yaml as text, so comments and layout stay as they are."""
    lines = lab_yaml.read_text(encoding="utf-8").splitlines()
    keep = [ln for ln in lines if not re.match(r"^cover(_credit)?:", ln)]
    flow = ", ".join(f"{k}: {json.dumps(v)}" for k, v in credit.items())
    new = [f"cover: {filename}", f"cover_credit: {{ {flow} }}"]
    at = next((i for i, ln in enumerate(keep) if ln.startswith("image:")), len(keep))
    lab_yaml.write_text("\n".join(keep[:at] + new + keep[at:]) + "\n", encoding="utf-8")


def _logo_cover(folder: Path, lab_id: str, logos: str) -> int:
    """The real technology logos on their brand colours (free, no API). Replaces any other cover."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import logo_cover

    try:
        svg = logo_cover.build_cover([n.strip() for n in logos.split(",") if n.strip()], lab_id)
    except ValueError as e:
        print(e)
        return 2
    for old in ("cover.jpg", "cover.webp", "cover.png"):
        (folder / old).unlink(missing_ok=True)
    (folder / "cover.svg").write_text(svg, encoding="utf-8")
    source = "devicon (MIT), Duke (BSD)" if "duke" in logos else "devicon (MIT)"
    _yaml_set_cover(folder / "lab.yaml", {"by": f"Logos: {logos}", "source": source}, "cover.svg")
    load_lab(folder)
    print(f"✓ {folder / 'cover.svg'} ({len(svg) // 1024} KB)")
    return 0


def cmd_cover(args: argparse.Namespace) -> int:
    """Stock photo covers from Pexels (free for commercial use). Search, look, then pick."""
    import httpx

    from app.config import get_settings

    folder = _lab_folders(args.labs_dir, args.lab_id)[0]
    if args.logo:
        return _logo_cover(folder, args.lab_id, args.logo)
    out = COVERS_DIR / args.lab_id
    settings = get_settings()
    if args.generate:
        chosen = image_provider(settings)
        if chosen is None:
            print("Set OPENAI_API_KEY (or GEMINI_API_KEY) in backend/.env to generate cover art")
            return 2
        provider, key, model = chosen
        lab = load_lab(folder)
        prompt = cover_prompt(lab)
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)
        made = []
        for i in range(1, args.count + 1):
            try:
                img = to_cover(generate_image(prompt, provider, key, model, args.quality))
            except Exception as e:
                print(f"  {i}. failed: {e}")
                continue
            (out / f"{i}.webp").write_bytes(img)
            made.append({"file": f"{i}.webp"})
            print(f"  {i}. {out / f'{i}.webp'} ({len(img) // 1024} KB)")
        (out / "generated.json").write_text(
            json.dumps({"provider": provider, "model": model, "quality": args.quality, "prompt": prompt, "images": made}, indent=1)
        )
        if not made:
            return 1
        print(f"Look at them, then: scripts/labbox cover {args.lab_id} --pick N")
        return 0
    if args.pick is not None and (out / "generated.json").is_file():
        info = json.loads((out / "generated.json").read_text())
        names = [m["file"] for m in info["images"]]
        if f"{args.pick}.webp" not in names:
            print(f"Pick one of: {', '.join(n.split('.')[0] for n in names)}")
            return 2
        old = folder / "cover.jpg"
        if old.exists():
            old.unlink()
        shutil.copyfile(out / f"{args.pick}.webp", folder / "cover.webp")
        who = "OpenAI" if info.get("provider") == "openai" else "Gemini"
        _yaml_set_cover(folder / "lab.yaml", {"by": f"Generated with {who}", "source": info["model"]}, "cover.webp")
        load_lab(folder)
        print(f"✓ {folder / 'cover.webp'} ({(folder / 'cover.webp').stat().st_size // 1024} KB)")
        return 0
    if args.pick is None:
        key = settings.PEXELS_API_KEY
        if not key:
            print("Set PEXELS_API_KEY in backend/.env (free key: https://www.pexels.com/api/)")
            return 2
        if not args.query:
            print("Say what the photo should show, for example --query \"chai stall street india\"")
            return 2
        r = httpx.get(PEXELS_SEARCH, params={"query": args.query, "orientation": "landscape", "per_page": args.count},
                      headers={"Authorization": key}, timeout=20)
        if r.status_code != 200:
            print(f"Pexels answered {r.status_code}: {r.text[:200]}")
            return 1
        photos = r.json().get("photos", [])
        if not photos:
            print("No photos found; try other words.")
            return 1
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)
        (out / "search.json").write_text(json.dumps({"query": args.query, "photos": photos}, indent=1), encoding="utf-8")
        for i, p in enumerate(photos, 1):
            (out / f"{i}.jpg").write_bytes(httpx.get(p["src"]["medium"], timeout=30, follow_redirects=True).content)
            print(f"  {i}. {out / f'{i}.jpg'}  by {p['photographer']}: {p.get('alt') or ''}")
        print(f"Look at them, then: scripts/labbox cover {args.lab_id} --pick N")
        return 0

    found = out / "search.json"
    if not found.is_file():
        print(f"Search first: scripts/labbox cover {args.lab_id} --query \"...\"")
        return 2
    photos = json.loads(found.read_text(encoding="utf-8"))["photos"]
    if not 1 <= args.pick <= len(photos):
        print(f"Pick a number from 1 to {len(photos)}")
        return 2
    p = photos[args.pick - 1]
    data = httpx.get(p["src"]["landscape"], timeout=30, follow_redirects=True).content  # 1200 x 627 crop
    if len(data) > 512 * 1024:
        data = httpx.get(p["src"]["large"], timeout=30, follow_redirects=True).content
    (folder / "cover.jpg").write_bytes(data)
    _yaml_set_cover(folder / "lab.yaml", {"by": p["photographer"], "url": p["url"], "source": "Pexels"})
    load_lab(folder)  # fails loudly if anything is off
    print(f"✓ {folder / 'cover.jpg'} ({len(data) // 1024} KB), photo by {p['photographer']} on Pexels")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="labbox", description="Authoring tools for LabBox (by Telusko) labs")
    p.add_argument("--labs-dir", type=Path, default=ROOT / "labs", help="folder with the labs (default: labs/)")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new-lab", help="scaffold a new lab from a template or a spec")
    n.add_argument("lab_id", nargs="?")
    n.add_argument("--from-spec", help="specs/<lab>.yaml: story, chapters, tasks and hints")
    n.add_argument("--track", choices=TRACKS, default="languages")
    n.add_argument("--template", choices=[*TEMPLATES_READY, *TEMPLATE_LATER], default="python")
    n.add_argument("--title")
    n.set_defaults(fn=cmd_new_lab)

    v = sub.add_parser("validate", help="check lab.yaml, chapters, hints, solution and image")
    v.add_argument("lab_id", nargs="?")
    v.add_argument("--no-docker", action="store_true", help="skip the image check")
    v.add_argument("--strict", action="store_true", help="treat every warning as an error (CI)")
    v.set_defaults(fn=cmd_validate)

    t = sub.add_parser("test-lab", help="build the image; starter must fail every task, solution must pass")
    t.add_argument("lab_id")
    t.add_argument("--no-build", action="store_true", help="use the image that is already built")
    t.set_defaults(fn=cmd_test_lab)

    pv = sub.add_parser("preview", help="open a lab locally as a dev user")
    pv.add_argument("lab_id")
    pv.add_argument("--user", default="labbox-dev")
    pv.add_argument("--url", default="http://localhost:5173")
    pv.add_argument("--no-browser", action="store_true")
    pv.set_defaults(fn=cmd_preview)

    c = sub.add_parser("cover", help="lab card cover: real logos (--logo), AI art (--generate) or a stock photo")
    c.add_argument("lab_id")
    c.add_argument("--logo", help="real technology logos on brand colours, main first: redis or fastapi,python")
    c.add_argument("--query", help="what the photo should show")
    c.add_argument("--generate", action="store_true", help="AI cover art in the house style (OpenAI or Gemini, paid per image)")
    c.add_argument("--quality", choices=["low", "medium", "high"], default="medium", help="OpenAI image quality (cost goes up)")
    c.add_argument("--pick", type=int, help="save candidate N as the cover")
    c.add_argument("--count", type=int, default=None, help="how many candidates (default: 3 generated, 6 photos)")
    c.set_defaults(fn=cmd_cover)

    args = p.parse_args(argv)
    if getattr(args, "cmd", None) == "cover" and args.count is None:
        args.count = 3 if args.generate else 6
    args.labs_dir = args.labs_dir.resolve()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
