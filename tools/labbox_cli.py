"""labbox: authoring tools for lab writers.

    scripts/labbox new-lab <id> --track languages --template python
    scripts/labbox validate [lab_id] [--no-docker]
    scripts/labbox test-lab <lab_id> [--no-build]
    scripts/labbox preview <lab_id>

Runs with the backend's virtualenv and reuses the backend's own lab loader and checker,
so a lab that passes here behaves the same in the app.
"""
import argparse
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
TEMPLATE_LATER = {
    "node": "a later phase (needs the labbox/node base image)",
    "go": "a later phase (needs the labbox/go base image)",
    "multi-service": "Phase D (services)",
    "incident": "Phase D (failure injection and live checks)",
    "ai": "Phase E (LLM gateway)",
    "system-design": "Phase G (k6 load tests)",
}
HINTS_PER_TASK = 3


@dataclass
class Report:
    lab: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


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


def validate_lab(folder: Path, check_image: bool = True, known_labs: set[str] | None = None) -> Report:
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

    if check_image:
        exists = _image_exists(lab.image)
        if exists is None:
            rep.warnings.append("Docker is not reachable: image not checked")
        elif not exists:
            rep.errors.append(f"image {lab.image} is not built (bash scripts/build_lab_images.sh)")
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
    reports = [validate_lab(f, check_image=not args.no_docker, known_labs=known) for f in folders]
    for r in reports:
        _print_report(r)
    bad = sum(bool(r.errors) for r in reports)
    print(f"\n{len(reports) - bad} of {len(reports)} labs valid")
    if args.lab_id is None and not bad:
        content = validate_content(args.labs_dir)
        _print_report(content)
        bad += bool(content.errors)
    return 1 if bad else 0


def cmd_new_lab(args: argparse.Namespace) -> int:
    if args.template in TEMPLATE_LATER:
        print(f"The {args.template!r} template arrives with {TEMPLATE_LATER[args.template]}. Use python or java for now.")
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="labbox", description="Authoring tools for LabBox labs")
    p.add_argument("--labs-dir", type=Path, default=ROOT / "labs", help="folder with the labs (default: labs/)")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new-lab", help="scaffold a new lab from a template")
    n.add_argument("lab_id")
    n.add_argument("--track", choices=TRACKS, default="languages")
    n.add_argument("--template", choices=["python", "java", *TEMPLATE_LATER], default="python")
    n.add_argument("--title")
    n.set_defaults(fn=cmd_new_lab)

    v = sub.add_parser("validate", help="check lab.yaml, chapters, hints, solution and image")
    v.add_argument("lab_id", nargs="?")
    v.add_argument("--no-docker", action="store_true", help="skip the image check")
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

    args = p.parse_args(argv)
    args.labs_dir = args.labs_dir.resolve()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
