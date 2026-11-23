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
    ("ownership", "06-ownership", "test", ["fix_moved_value", "add_reading"]),
    ("borrowing", "07-borrowing", "test", ["average_power", "cap_readings"]),
    ("slices-and-strings", "08-slices-and-strings", "test", ["turbine_id", "last_hour"]),
    ("structs", "09-structs", "test", ["from_line", "underperforming"]),
    ("enums", "10-enums", "test", ["classify", "peak_power"]),
    ("match", "11-match", "test", ["describe_status", "parse_line"]),
    ("modules", "12-modules", "test", ["make_public", "re_export"]),
    ("vec-and-string", "13-vec-and-string", "test", ["moving_average", "as_sentence"]),
    ("hashmap", "14-hashmap", "test", ["energy_by_turbine", "silent_turbines"]),
    ("errors", "15-errors", "test", ["number", "parse_reading"]),
    ("error-types", "16-error-types", "test", ["error_enum", "load_with_context"]),
    ("generics", "17-generics", "test", ["largest", "series_peak"]),
    ("traits", "18-traits", "test", ["impl_display", "impl_sensor"]),
    ("lifetimes", "19-lifetimes", "test", ["stronger", "zero_copy"]),
    ("closures", "20-closures", "test", ["below", "alerts"]),
    ("iterators", "21-iterators", "test", ["total_energy", "weak_turbines"]),
    ("testing", "22-testing", "own", ["test_curve", "test_parse"]),
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


# For "own" chapters: the learner's test function for each task, and the bug it must catch in the reference library.
OWN = {
    "test_curve": ("power_curve_edges", "the storm stop starts above 25 m/s instead of at 25",
                   ("wind_ms >= 25.0", "wind_ms > 25.0")),
    "test_parse": ("parse_rejects_broken_lines", "the power error names the wind field instead",
                   ('format!("bad power {:?}", parts[3])', 'format!("bad power {:?}", parts[2])')),
}


def own_mode(cid, folder, tasks, work, pkg):
    """The learner wrote the tests (tests/windwatch.rs). Each test must pass on the reference library and fail when
    the bug is planted in it."""
    reference = open(f"{T}/{cid}/lib_reference.rs").read()
    mine = open(f"{work}/{folder}/tests/windwatch.rs").read()
    for t in tasks:
        name, bug, (good, bad) = OWN[t]
        if f"fn {name}(" not in mine:
            result(t, False, f"keep the test function {name} in tests/windwatch.rs.")
            continue
        outcomes = []
        for lib in (reference, reference.replace(good, bad)):
            with open(f"{work}/{folder}/src/lib.rs", "w") as f:
                f.write(lib)
            p = subprocess.run(["cargo", "test", "-q", "-p", pkg, "--test", "windwatch", "--", "--exact", name],
                               cwd=work, capture_output=True, text=True, timeout=200)
            outcomes.append((p.returncode == 0, p.stdout + p.stderr))
        (ok, log), (caught_fail, _) = outcomes[0], outcomes[1]
        if "could not compile" in log:
            show_errors(folder, log)
            result(t, False, f"tests/windwatch.rs does not compile yet: {first_error(log)}.")
        elif not ok:
            result(t, False, f"{name} fails on the correct code. Read its assertion message in Output.")
            print(log[-1500:])
        elif caught_fail:
            result(t, False, f"{name} still passes when {bug}. Add asserts this bug would break (an empty test always "
                             "passes).", "fails with the bug", "passed")
        else:
            result(t, True, f"Your test passes on the correct code and catches the bug where {bug}.")


def test_mode(cid, folder, tasks, work, pkg):
    """One hidden test for the chapter (check.rs), or one per task (check_<task>.rs) when a task's test would not
    even compile until that task is done (like a missing `pub use`): then each task is built on its own."""
    if os.path.exists(f"{T}/{cid}/check.rs"):
        run_tests(folder, tasks, work, pkg, {"labbox_check": f"{T}/{cid}/check.rs"})
    else:
        for t in tasks:
            run_tests(folder, [t], work, pkg, {f"labbox_{t}": f"{T}/{cid}/check_{t}.rs"})


def run_tests(folder, tasks, work, pkg, targets):
    os.makedirs(f"{work}/{folder}/tests", exist_ok=True)
    for name, src in targets.items():
        with open(f"{work}/{folder}/tests/{name}.rs", "w") as f:
            f.write(open(f"{T}/common/check.rs").read() + "\n" + open(src).read())
    args = ["cargo", "test", "-q", "-p", pkg]
    for name in targets:
        args += ["--test", name]
    p = subprocess.run(args + ["--", "--nocapture", "--test-threads=1"], cwd=work, capture_output=True, text=True,
                       timeout=200)
    for name in targets:
        os.remove(f"{work}/{folder}/tests/{name}.rs")
    out = p.stdout + p.stderr
    lines = [l for l in out.splitlines() if l.startswith("@@RESULT ")]
    for l in lines:
        print(l, flush=True)
    reported = {json.loads(l[9:])["task"] for l in lines}
    missing = [t for t in tasks if t not in reported]
    if missing and "could not compile" in out:
        show_errors(folder, p.stderr)
        err = first_error(p.stderr)
        for t in missing:
            if "(tests/labbox_" in err:  # the learner's crate compiled; the check cannot reach what it needs
                result(t, False, f"your code compiles, but the check cannot use it: {err.split(' (tests/')[0]}. "
                                 "Check that the name exists, is `pub`, and is where the task says.")
            else:
                result(t, False, f"your code in {folder}/ does not compile yet: {err}. Read the compiler's message in "
                                 "Output: it says which line, and usually how to fix it.")
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
        {"run": run_mode, "test": test_mode, "own": own_mode}[mode](cid, folder, tasks, work, pkg)
    except subprocess.TimeoutExpired:
        for t in tasks:
            result(t, False, "your code ran for too long (an endless loop?). Check your loops and try again.")
