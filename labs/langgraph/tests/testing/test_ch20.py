"""Your tests are run twice: on the correct desk (they must pass) and with a bug planted (they must fail)."""
import os
import shutil
import subprocess
import sys
import tempfile

import r

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCE = open(os.path.join(HERE, "desk_reference.py")).read()
BUGS = {
    "test_routes": ("test_dirty_water_goes_to_health", "dirty water is routed to the repair crew",
                    ('TEAMS = {"dirty_water": "health team", "billing": "billing office"}', 'TEAMS = {"billing": "billing office"}')),
    "test_interrupts": ("test_big_repair_waits_for_engineer", "repairs up to Rs 5 lakh skip the engineer",
                        ("APPROVAL_OVER = 50_000", "APPROVAL_OVER = 500_000")),
}


def run_test(desk_source: str, name: str) -> tuple[bool, str]:
    work = tempfile.mkdtemp()
    shutil.copy("rules.py", work)
    shutil.copy("test_desk.py", work)
    with open(os.path.join(work, "desk.py"), "w") as f:
        f.write(desk_source)
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"test_desk.py::{name}"],
                         cwd=work, capture_output=True, text=True, timeout=120)
    return out.returncode == 0, (out.stdout + out.stderr)[-600:]


def check_task(task: str):
    name, bug, (good, bad) = BUGS[task]

    def check():
        if f"def {name}(" not in open("test_desk.py").read():
            return r.failed(task, f"Keep the test function {name} in test_desk.py.")
        ok, log = run_test(REFERENCE, name)
        if not ok:
            return r.failed(task, f"{name} fails on the correct desk. Read its error in the Output, and check what you assert.",
                            "passes on the correct desk", log.strip().splitlines()[-1] if log.strip() else "failed")
        assert good in REFERENCE
        caught, _ = run_test(REFERENCE.replace(good, bad), name)
        if caught:
            return r.failed(task, f"{name} still passes when {bug}. It needs asserts that this bug would break "
                            "(an empty test always passes).", "fails with the bug", "passed")
        r.passed(task, f"Your test passes on the correct desk and catches the bug where {bug}.")
    r.task(task, check)


def test_routes():
    check_task("test_routes")


def test_interrupts():
    check_task("test_interrupts")
