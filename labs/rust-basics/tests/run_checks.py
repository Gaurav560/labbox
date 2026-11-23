"""Hidden checks for Rust from zero. Every chapter is its own crate. A check copies the workspace's Cargo.toml and
that one chapter into a scratch folder (so another chapter's unfinished code never matters), then either runs the
chapter's programs and compares their output ("run"), or adds a hidden integration test and runs it ("test").
Every task always gets one @@RESULT line. The compiler's own messages are shown in Output when the code does not
compile: they are the best help Rust gives."""
import json
import os
import re
import shutil
import subprocess

W, T = "/check/workspace", "/check/tests"

# chapter id, folder, mode, tasks
CHAPTERS = [
    ("why-rust", "01-why-rust", "run", ["hello_windwatch", "fix_first_errors"]),
    ("variables", "02-variables", "test", ["capacity_mw", "wind_speed"]),
    ("types", "03-types", "test", ["energy_kwh", "describe"]),
    ("functions", "04-functions", "test", ["tip_speed", "capacity_factor"]),
    ("control-flow", "05-control-flow", "test", ["status", "hours_generating"]),
]


def result(task, passed, message, expected=None, actual=None):
    line = {"task": task, "passed": passed, "message": message if passed else f"Not yet: {message}"}
    if expected is not None:
        line["expected"], line["actual"] = str(expected), str(actual)
    print("@@RESULT " + json.dumps(line), flush=True)


def first_error(log: str) -> str:
    """The compiler's first error, with where it is: 'expected `;`, found `println` (src/bin/x.rs:4)'."""
    m = re.search(r"^error(\[E\d+\])?: (.+)$\n\s*--> ([^\n]+)", log, re.M)
    if m:
        where = m.group(3).split("/", 1)[-1] if "/" in m.group(3) else m.group(3)
        return f"{m.group(2)} ({where})"
    m = re.search(r"^error(\[E\d+\])?: (.+)$", log, re.M)
    return m.group(2) if m else "see Output"


def show_errors(folder: str, log: str) -> None:
    errors = [b for b in re.split(r"\n(?=error|warning)", log) if b.startswith("error")]
    print(f"---- {folder}: the compiler says ----")
    print("\n\n".join(errors[:3])[:3000])


def scratch(folder: str) -> str:
    work = "/tmp/check/ws"
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    shutil.copy(f"{W}/Cargo.toml", work)
    shutil.copytree(f"{W}/{folder}", f"{work}/{folder}", ignore=shutil.ignore_patterns("target"))
    return work


def package(folder: str) -> str:
    return re.search(r'^name\s*=\s*"([^"]+)"', open(f"{W}/{folder}/Cargo.toml").read(), re.M).group(1)


def run_mode(cid, folder, tasks, work, pkg):
    messages = json.load(open(f"{T}/{cid}/messages.json"))
    for task in tasks:
        want = open(f"{T}/{cid}/{task}.out").read()
        p = subprocess.run(["cargo", "run", "-q", "-p", pkg, "--bin", task], cwd=work, capture_output=True, text=True,
                           timeout=120)
        if p.returncode != 0 and "error" in p.stderr and "could not compile" in p.stderr:
            show_errors(folder, p.stderr)
            result(task, False, f"src/bin/{task}.rs does not compile yet: {first_error(p.stderr)}. Read the compiler's "
                                "message in Output, fix that line, and check again.")
        elif p.stdout != want:
            result(task, False, messages["wrong"], want.strip(), p.stdout.strip())
        else:
            result(task, True, messages["passed"])


def test_mode(cid, folder, tasks, work, pkg):
    os.makedirs(f"{work}/{folder}/tests", exist_ok=True)
    with open(f"{work}/{folder}/tests/labbox_check.rs", "w") as f:
        f.write(open(f"{T}/common/check.rs").read() + "\n" + open(f"{T}/{cid}/check.rs").read())
    p = subprocess.run(["cargo", "test", "-q", "-p", pkg, "--test", "labbox_check", "--", "--nocapture",
                        "--test-threads=1"], cwd=work, capture_output=True, text=True, timeout=200)
    out = p.stdout + p.stderr
    lines = [l for l in out.splitlines() if l.startswith("@@RESULT ")]
    for l in lines:
        print(l, flush=True)
    reported = {json.loads(l[9:])["task"] for l in lines}
    missing = [t for t in tasks if t not in reported]
    if missing and "could not compile" in out:
        show_errors(folder, p.stderr)
        for t in missing:
            result(t, False, f"your code in {folder}/ does not compile yet: {first_error(p.stderr)}. Read the compiler's "
                             "message in Output: it says which line, and usually how to fix it.")
    elif missing:
        print(out[-2000:])
        for t in missing:
            result(t, False, "the checks could not finish; see Output.")


for cid, folder, mode, tasks in CHAPTERS:
    if os.environ.get("LABBOX_CHAPTER") and os.environ["LABBOX_CHAPTER"] != cid:
        continue
    if not os.path.isfile(f"{W}/{folder}/Cargo.toml"):
        for t in tasks:
            result(t, False, f"could not find the folder {folder}/ in your workspace.")
        continue
    work, pkg = scratch(folder), package(folder)
    try:
        (run_mode if mode == "run" else test_mode)(cid, folder, tasks, work, pkg)
    except subprocess.TimeoutExpired:
        for t in tasks:
            result(t, False, "your code ran for too long (an endless loop?). Check your loops and try again.")
