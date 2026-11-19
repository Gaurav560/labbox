"""Hidden checks for linux-on-call. The log tools run against fresh logs the learner has never seen,
so only a real pipeline passes. Prints one @@RESULT line per task; never prints the solution."""
import json
import os
import random
import shutil
import stat
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

WS = Path("/check/workspace")
TMP = Path(tempfile.mkdtemp())
SIZES = {"access.log": 6254, "app.log": 2870}  # the logs that must survive the clean-up


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


def make_log(seed):
    """A log where the top IPs and the slowest requests are never tied."""
    rnd = random.Random(seed)
    ips = [f"192.168.{rnd.randint(0, 9)}.{n}" for n in rnd.sample(range(2, 250), 7)]
    counts = [rnd.randint(1, 4) for _ in ips]
    counts[:4] = [60, 41, 27, 13]  # clear winners
    rows, used_ms = [], set()
    for ip, n in zip(ips, counts):
        for _ in range(n):
            status = rnd.choice([200, 200, 200, 201, 404, 500, 501, 502, 503, 599])
            ms = rnd.randint(5, 5000)
            while ms in used_ms:
                ms = rnd.randint(5, 5000)
            used_ms.add(ms)
            path = rnd.choice(["/menu", "/order", "/pay", "/otp", "/login"])
            rows.append((ip, status, ms, path))
    rnd.shuffle(rows)
    lines = [f"2026-12-0{seed % 9 + 1}T10:{i // 60 % 60:02d}:{i % 60:02d} {ip} GET {p} {s} {ms}ms" for i, (ip, s, ms, p) in enumerate(rows)]
    path = TMP / f"hidden-{seed}.log"
    path.write_text("\n".join(lines) + "\n")
    want = {
        "count_5xx": str(sum(1 for _, s, _, _ in rows if 500 <= s <= 599)),
        "top_ips": "\n".join(ip for ip, _ in Counter(ip for ip, _, _, _ in rows).most_common(3)),
        "slowest": "\n".join(sorted(lines, key=lambda l: -int(l.split()[5][:-2]))[:3]),
    }
    return path, want


def run_script(name, *args):
    p = subprocess.run(["bash", str(WS / name), *map(str, args)], capture_output=True, text=True, timeout=10, cwd=WS)
    return p.stdout.strip(), p.stderr.strip()


def log_tool(task):
    script = f"{task}.sh"
    if not (WS / script).is_file():
        return report(task, False, f"{script} is missing.")
    for seed in (3, 11):
        log, want = make_log(seed)
        try:
            got, err = run_script(script, log)
        except subprocess.TimeoutExpired:
            return report(task, False, f"{script} did not finish in 10 seconds. Does it read the file given as $1?")
        got = "\n".join(l.strip() for l in got.splitlines()) if task == "top_ips" else got
        if got != want[task]:
            msg = f"On a log you have not seen, {script} printed something else."
            if not got:
                msg = f"{script} printed nothing." + (f" Error: {err.splitlines()[-1]}" if err else "")
            return report(task, False, msg, want[task], got)
    report(task, True, "Right on two logs it had never seen.")


def free_disk():
    logs = WS / "server/var/log/app"
    debug = logs / "debug.log"
    if not debug.exists():
        return report("free_disk", False, "debug.log is gone. The app still has it open, so deleting it does not free the "
                      "space until a restart; empty it instead. Make an empty one with: touch server/var/log/app/debug.log")
    size = debug.stat().st_size
    if size > 0:
        return report("free_disk", False, "The biggest log is still full.", "debug.log: 0 bytes", f"debug.log: {size} bytes")
    for name, want in SIZES.items():
        f = logs / name
        if not f.is_file() or f.stat().st_size != want:
            return report("free_disk", False, f"{name} was changed. Only the runaway log should be emptied (Reset lab restores it).")
    report("free_disk", True, "Disk space is back, and the app can keep writing to the same file.")


def fix_perms():
    if not (WS / "fix_perms.sh").is_file():
        return report("fix_perms", False, "fix_perms.sh is missing.")
    # A fresh server folder with the wrong permissions, plus a script name the learner has not seen.
    target = TMP / "srv"
    shutil.copytree(WS / "server", target, ignore=shutil.ignore_patterns("*.log"))
    (target / "bin/backup.sh").write_text("#!/usr/bin/env bash\necho backup\n")
    for f in target.rglob("*"):
        if f.is_file():
            f.chmod(0o644)
    try:
        _, err = run_script("fix_perms.sh", target)
    except subprocess.TimeoutExpired:
        return report("fix_perms", False, "fix_perms.sh did not finish in 10 seconds.")
    for sh in sorted((target / "bin").glob("*.sh")):
        if not sh.stat().st_mode & stat.S_IXUSR:
            return report("fix_perms", False, f"bin/{sh.name} is still not executable." + (f" Error: {err.splitlines()[-1]}" if err else ""),
                          "-rwx", stat.filemode(sh.stat().st_mode))
    secrets = target / "config/secrets.env"
    mode = secrets.stat().st_mode
    if mode & 0o077:
        return report("fix_perms", False, "Other users can still read config/secrets.env.", "-rw-------", stat.filemode(mode))
    if not mode & stat.S_IRUSR:
        return report("fix_perms", False, "Now even the owner cannot read config/secrets.env.", "-rw-------", stat.filemode(mode))
    report("fix_perms", True, "Scripts run, and secrets stay with their owner. Works on any server folder.")


try:
    for t in ("count_5xx", "top_ips", "slowest"):
        log_tool(t)
    free_disk()
    fix_perms()
finally:
    shutil.rmtree(TMP, ignore_errors=True)
    os.chdir("/")
