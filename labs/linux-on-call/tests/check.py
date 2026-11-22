"""Live checks for linux-on-call (the Tara Observatory's server). The workspace is mounted read-only at /check/workspace.
Answer files and permissions are read in place; scripts run in a scratch copy, on fresh inputs the learner has never
seen, so only a real solution passes. Only the tasks in LABBOX_TASKS run. Prints one @@RESULT line per task and
never prints a solution."""
import configparser
import json
import os
import re
import random
import shutil
import signal
import socket
import stat
import subprocess
import tempfile
import threading
import time
import urllib.request
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WS = Path("/check/workspace")
TMP = Path(tempfile.mkdtemp())
WANTED = {t for t in os.environ.get("LABBOX_TASKS", "").split(",") if t}
SIZES = {"access.log": 6327, "app.log": 2510}  # chapter 9: the logs that must survive the clean-up
STARTED: list[subprocess.Popen] = []  # processes a check started; all stopped at the end


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


def answer(folder, name):
    """The stripped text of an answer file, or None when it does not exist."""
    p = WS / folder / name
    return p.read_text(errors="replace").strip() if p.is_file() else None


def run(cmd, cwd, env=None, timeout=10, stdin=None):
    """(exit code, stdout, stderr) of a command; exit code None when it timed out."""
    full = {**os.environ, **(env or {})}
    try:
        p = subprocess.run(cmd, cwd=cwd, env=full, capture_output=True, text=True, timeout=timeout, stdin=stdin or subprocess.DEVNULL)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return None, "", ""


def last_line(err):
    lines = [l for l in err.strip().splitlines() if l.strip()]
    return f" The error was: {lines[-1][:200]}" if lines else ""


def scratch(folder, name=None):
    """A scratch copy of a chapter folder (modes kept), where scripts may write."""
    dst = TMP / (name or folder)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(WS / folder, dst, symlinks=True)
    return dst


def norm(path, base):
    """A path the learner wrote (absolute, ./relative or relative) as a path relative to the chapter folder."""
    path = path.strip().strip("'\"")
    for prefix in (f"/workspace/{base}/", f"/check/workspace/{base}/", "./"):
        if path.startswith(prefix):
            path = path[len(prefix):]
    return path.rstrip("/")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_port(port, seconds):
    end = time.time() + seconds
    while time.time() < end:
        with socket.socket() as s:
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.1)
    return False


def http_get(url, timeout=3):
    """(status, body) or (None, error text)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:  # a zombie has finished; it only waits for its parent to collect it
        return Path(f"/proc/{pid}/stat").read_text().split(")")[-1].split()[0] != "Z"
    except OSError:
        return False


def kill_tree_by_cwd(folder):
    """Stop every process whose working folder is inside a scratch folder (servers a learner script started)."""
    for p in Path("/proc").iterdir():
        if p.name.isdigit():
            try:
                if os.readlink(p / "cwd").startswith(str(folder)):
                    os.kill(int(p.name), signal.SIGKILL)
            except OSError:
                pass


# ---------------------------------------------------------------- chapter 1: why Linux

def hidden_file():
    got = answer("01-why-linux", "answer-hidden.txt")
    if got is None:
        return report("hidden_file", False, "There is no answer-hidden.txt in 01-why-linux yet. Write the secret word into it "
                      "with echo and >.")
    if got.lower() == "pulsar":
        return report("hidden_file", True, "Right: pulsar. Hidden files only need ls -a; nothing on Linux is truly hidden.")
    if "secret word" in got.lower():
        return report("hidden_file", False, "Close: the file should hold only the word itself, not the whole sentence.", "one word", got[:80])
    report("hidden_file", False, "That is not the word in the hidden file. ls -a in the tara folder shows files that "
           "start with a dot; cat the one you find.", "the secret word", got[:80])


def deep_file():
    got = answer("01-why-linux", "answer-target.txt")
    if got is None:
        return report("deep_file", False, "There is no answer-target.txt in 01-why-linux yet.")
    if " ".join(got.lower().split()) == "crab nebula":
        return report("deep_file", True, "The Crab Nebula it is. Four cd's deep, or one cd with the whole path: both work.")
    if "crab nebula" in got.lower():
        return report("deep_file", False, "Close: the file should hold only the target's name.", "Crab Nebula", got[:80])
    report("deep_file", False, "That is not tonight's first target. The plan is in observations/2026/november/23.", "a target in the sky", got[:80])


# ---------------------------------------------------------------- chapter 2: files and folders

PDFS = {f"invoice-2026-11-{d}.pdf" for d in ("03", "07", "12", "18", "21")} | {"star chart.pdf"}
JPGS = {f"sky-{n}.jpg" for n in range(1, 5)}


def tidy_folder():
    d = WS / "02-files/downloads"
    if not d.is_dir():
        return report("tidy_folder", False, "The downloads folder is gone. Machine, then Reset, brings the chapter back.")
    tmps = sorted(p.name for p in d.rglob("*.tmp"))
    inv = {p.name for p in (d / "invoices").glob("*")} if (d / "invoices").is_dir() else None
    pho = {p.name for p in (d / "photos").glob("*")} if (d / "photos").is_dir() else None
    if inv is None or pho is None:
        return report("tidy_folder", False, "downloads needs two new folders, invoices and photos. mkdir makes them.")
    if inv != PDFS:
        missing = sorted(PDFS - inv)
        hint = " Names with spaces need quotes, or a * pattern." if "star chart.pdf" in missing else ""
        return report("tidy_folder", False, "invoices should hold every .pdf file, and nothing else." + hint, sorted(PDFS), sorted(inv))
    if pho != JPGS:
        return report("tidy_folder", False, "photos should hold every .jpg file, and nothing else.", sorted(JPGS), sorted(pho))
    if tmps:
        return report("tidy_folder", False, "The .tmp files are still there. rm *.tmp removes them all at once.", "no .tmp files", tmps)
    if not (d / "notes.txt").is_file():
        return report("tidy_folder", False, "notes.txt is gone: it should stay where it was. Reset brings it back.")
    report("tidy_folder", True, "Tidy: invoices, photos, notes.txt, and no junk. Three commands with * did twelve files.")


def tree_of(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def backup_copy():
    src, dst = WS / "02-files/targets", WS / "02-files/targets-backup"
    if not src.is_dir():
        return report("backup_copy", False, "The targets folder is gone: a backup is a copy, the original stays. Reset brings it back.")
    if not dst.is_dir():
        return report("backup_copy", False, "There is no folder called targets-backup in 02-files yet.")
    a, b = tree_of(src), tree_of(dst)
    if "targets" in {p.name for p in dst.iterdir()} and not b.keys() & a.keys():
        return report("backup_copy", False, "The copy went inside targets-backup as targets-backup/targets. Remove targets-backup and copy again "
                      "while targets-backup does not exist yet.")
    if a != b:
        missing = sorted(set(a) - set(b))
        hint = " Folders inside folders need cp -r." if any("/" in m for m in missing) else ""
        return report("backup_copy", False, "targets-backup is not an exact copy of targets." + hint, sorted(a), sorted(b))
    report("backup_copy", True, "An exact copy, folders inside folders included. That is cp -r.")


# ---------------------------------------------------------------- chapter 3: reading files

def count_observations():
    got = answer("03-reading-files", "answer-observations.txt")
    if got is None:
        return report("count_observations", False, "There is no answer-observations.txt in 03-reading-files yet.")
    if got == "1248":
        return report("count_observations", True, "1,248 observations: wc -l counts 1,249 lines, minus the header. You did not miss it.")
    if got.split()[:1] == ["1249"]:
        return report("count_observations", False, "So close: wc -l counts every line, and the first line of observations.csv is the "
                      "header, not an observation.", "the number of observations", got)
    if got.split()[-1:] == ["observations.csv"]:
        return report("count_observations", False, "The file should hold just the number, without the file name. wc -l < observations.csv "
                      "prints only the number.", "a number", got)
    report("count_observations", False, "That is not the number of observations. wc -l counts lines.", "a number", got[:80])


def last_lines():
    f = WS / "03-reading-files/recent.log"
    if not f.is_file():
        return report("last_lines", False, "There is no recent.log in 03-reading-files yet.")
    want = "".join((WS / "03-reading-files/app.log").read_text().splitlines(True)[-20:])
    got = f.read_text()
    if got == want:
        return report("last_lines", True, "The last 20 lines, exactly. tail and > together: your first saved result.")
    n = len(got.splitlines())
    if n != 20:
        return report("last_lines", False, f"recent.log has {n} lines; it should have the last 20 of app.log.", "20 lines", f"{n} lines")
    report("last_lines", False, "recent.log has 20 lines, but not the last 20 of app.log. tail takes lines from the end.")


# ---------------------------------------------------------------- chapter 4: pipes and redirection

BUILD_ERR = ("warning: photo crab-nebula.jpg is larger than 1 MB\nerror: tonight.html links to a missing chart orion.png\n"
             "error: about.html has no title\n")


def errors_only():
    f = WS / "04-pipes/errors.txt"
    if not f.is_file():
        return report("errors_only", False, "There is no errors.txt in 04-pipes yet.")
    got = f.read_text()
    if got == BUILD_ERR:
        return report("errors_only", True, "Only the problems, none of the progress lines. That is 2>.")
    if "Building" in got and "error:" in got:
        return report("errors_only", False, "errors.txt has the progress lines too. 2> sends only standard error into a file; "
                      "2>&1 joins both streams.")
    if "Building" in got:
        return report("errors_only", False, "errors.txt has the progress lines (standard output). The problems go to standard "
                      "error, stream 2.")
    report("errors_only", False, "errors.txt should hold exactly what build.sh writes to standard error.", BUILD_ERR.splitlines(), got.splitlines()[:5])


def target_list():
    f = WS / "04-pipes/tonight-targets.txt"
    if not f.is_file():
        return report("target_list", False, "There is no tonight-targets.txt in 04-pipes yet.")
    targets = (WS / "04-pipes/targets.txt").read_text().splitlines()
    want = sorted(set(targets))
    got = f.read_text().splitlines()
    if got == want:
        return report("target_list", True, f"{len(want)} targets, each once, in order. sort -u (or sort | uniq) did 64 lines.")
    if sorted(got) == sorted(targets):
        return report("target_list", False, "Every target is there, but repeats too. uniq, or sort -u, keeps one of each.")
    if set(got) == set(want) and len(got) > len(want):
        return report("target_list", False, "Some targets appear twice. uniq only merges repeats that sit next to each other, so "
                      "sort first.")
    if set(got) == set(want):
        return report("target_list", False, "The right targets, but not in alphabetical order.", want, got)
    report("target_list", False, "tonight-targets.txt should list each target from targets.txt once, sorted.", want, got[:12])


# ---------------------------------------------------------------- chapter 5: reading logs (the old chapter 1)

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
            path = rnd.choice(["/sky", "/targets", "/images", "/status", "/login"])
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


def log_tool(task):
    script = WS / "05-logs" / f"{task}.sh"
    if not script.is_file():
        return report(task, False, f"05-logs/{task}.sh is missing.")
    for seed in (3, 11):
        log, want = make_log(seed)
        code, got, err = run(["bash", str(script), str(log)], cwd=WS / "05-logs")
        if code is None:
            return report(task, False, f"{task}.sh did not finish in 10 seconds. Does it read the file given as $1?")
        got = got.strip()
        got = "\n".join(l.strip() for l in got.splitlines()) if task == "top_ips" else got
        if got != want[task]:
            msg = f"On a log you have not seen, {task}.sh printed something else."
            if not got:
                msg = f"{task}.sh printed nothing." + last_line(err)
            return report(task, False, msg, want[task], got)
    report(task, True, "Right on two logs it had never seen.")


def count_5xx():
    log_tool("count_5xx")


def top_ips():
    log_tool("top_ips")


def slowest():
    log_tool("slowest")


# ---------------------------------------------------------------- chapter 6: finding things

BIG = {"server/backups/db-2026-11-22.sql.gz", "server/logs/archive/app-2026-10.log", "server/static/images/milky-way.jpg"}


def find_big():
    f = WS / "06-finding/big-files.txt"
    if not f.is_file():
        return report("find_big", False, "There is no big-files.txt in 06-finding yet. find can write its list there with >.")
    got = {norm(l, "06-finding") for l in f.read_text().splitlines() if l.strip()}
    if got == BIG:
        return report("find_big", True, "Three big files, 6.5 MB between them, found without opening a single folder by hand.")
    if "server/data/cache.bin" in got:
        return report("find_big", False, "cache.bin is 900 KB: under 1 MB. find -size +1M means bigger than 1 MB.", sorted(BIG), sorted(got))
    report("find_big", False, "big-files.txt should list every file bigger than 1 MB under server/, one path per line.", sorted(BIG), sorted(got))


def find_secret():
    got = answer("06-finding", "answer-secret.txt")
    if got is None:
        return report("find_secret", False, "There is no answer-secret.txt in 06-finding yet.")
    got = norm(got.split(":")[0], "06-finding")
    if got == "server/app/legacy/settings.old.conf":
        return report("find_secret", True, "Found it: an old settings file with a real password in plain text. On a real server, "
                      "you would now change that password and delete the file.")
    if got.endswith("database.env"):
        return report("find_secret", False, "database.env has DB_PASSWORD_FILE, which only says where the password is kept. Search "
                      "for the exact text DB_PASSWORD= instead.")
    report("find_secret", False, "That file does not contain a line with DB_PASSWORD=. grep -r searches every file in a folder.",
           "a path under server/", got[:120])


# ---------------------------------------------------------------- chapter 7: permissions

def mode_of(p):
    return stat.S_IMODE(p.stat().st_mode)


def make_executable():
    f = WS / "07-permissions/hello.sh"
    if not f.is_file():
        return report("make_executable", False, "hello.sh is gone. Reset brings it back.")
    m = mode_of(f)
    if m & 0o002:
        return report("make_executable", False, "hello.sh can now be changed by everyone (the last w). chmod 755 hello.sh gives "
                      "exactly: you change it, everyone runs it.", "-rwxr-xr-x", stat.filemode(f.stat().st_mode))
    if not m & stat.S_IXUSR:
        return report("make_executable", False, "hello.sh is not executable yet: ./hello.sh still says Permission denied.",
                      "-rwx...", stat.filemode(f.stat().st_mode))
    report("make_executable", True, "./hello.sh runs now. One letter, x, made a text file a program.")


def private_key():
    key, d = WS / "07-permissions/keys/deploy-key.pem", WS / "07-permissions/keys"
    if not key.is_file():
        return report("private_key", False, "keys/deploy-key.pem is gone. Reset brings it back.")
    km, dm = mode_of(key), mode_of(d)
    if km != 0o600:
        hint = "Now even you cannot read it." if not km & stat.S_IRUSR else "Others can still read it." if km & 0o077 else "Close."
        return report("private_key", False, f"deploy-key.pem should be read and write for you, nothing for anyone else. {hint}",
                      "-rw------- (600)", f"{stat.filemode(key.stat().st_mode)} ({km:o})")
    if dm != 0o700:
        return report("private_key", False, "The key is right; now the keys folder: only you may list it or enter it.",
                      "drwx------ (700)", f"{stat.filemode(d.stat().st_mode)} ({dm:o})")
    report("private_key", True, "600 on the key, 700 on the folder: ssh itself refuses keys that others can read.")


# ---------------------------------------------------------------- chapter 8: processes

HOG = "#!/bin/bash\n[ \"${1:-}\" = stubborn ] && trap '' TERM\nwhile :; do sleep 0.2; done\n"


def stop_hog():
    script = WS / "08-processes/stop.sh"
    if not script.is_file():
        return report("stop_hog", False, "08-processes/stop.sh is missing.")
    d = TMP / "procs"
    d.mkdir(exist_ok=True)
    name = f"hog{random.randint(100, 999)}"
    for n in (name, "keeper"):
        (d / n).write_text(HOG)
        (d / n).chmod(0o755)
    polite = subprocess.Popen([str(d / name)])
    stubborn = subprocess.Popen([str(d / name), "stubborn"])
    other = subprocess.Popen([str(d / "keeper")])
    STARTED.extend([polite, stubborn, other])
    time.sleep(0.5)
    start = time.time()
    code, out, err = run(["bash", str(script), name], cwd=d, timeout=15)
    took = time.time() - start
    for p in (polite, stubborn):
        try:
            p.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
    alive = [p for p in (polite, stubborn) if p.poll() is None]
    if code is None:
        return report("stop_hog", False, "stop.sh did not finish in 15 seconds. Wait a few seconds, not forever.")
    if code in (143, -15, 137, -9) and alive:
        return report("stop_hog", False, "stop.sh stopped itself: its own command line contains the name too. pgrep -f and pkill -f "
                      "match whole command lines; pgrep -x matches the exact process name.")
    if other.poll() is not None:
        return report("stop_hog", False, "stop.sh also stopped a process with a different name. Match the exact name only.")
    if polite in alive and stubborn in alive:
        return report("stop_hog", False, "Both test processes are still running." + last_line(err))
    if stubborn in alive:
        return report("stop_hog", False, "The polite process stopped, but one that ignores TERM is still running. After the "
                      "waiting time, send KILL to whatever is left.")
    if polite in alive:
        return report("stop_hog", False, "A process that would have stopped politely is still running.")
    if took < 0.8:
        return report("stop_hog", False, "Both stopped, but at once: nothing got the TERM signal and a moment to clean up. "
                      "Send TERM first, wait, then KILL what is left.")
    report("stop_hog", True, f"TERM first, KILL only for the stubborn one, and the process called keeper untouched ({took:.1f} s).")


def run_background():
    script = WS / "08-processes/start-report.sh"
    if not script.is_file():
        return report("run_background", False, "08-processes/start-report.sh is missing.")
    d = scratch("08-processes", "bg")
    for f in ("report.log", "report.pid"):
        (d / f).unlink(missing_ok=True)
    start = time.time()
    code, out, err = run(["bash", "start-report.sh"], cwd=d, timeout=8)
    took = time.time() - start
    if code is None or took > 2:
        kill_tree_by_cwd(d)
        return report("run_background", False, "start-report.sh waited for the report to finish. An & at the end of a command "
                      "runs it in the background and comes back at once.")
    pidf = d / "report.pid"
    if not pidf.is_file():
        kill_tree_by_cwd(d)
        return report("run_background", False, "There is no report.pid. $! holds the process id of the last background command.")
    try:
        pid = int(pidf.read_text().strip())
    except ValueError:
        kill_tree_by_cwd(d)
        return report("run_background", False, "report.pid should hold just a number, the process id.", "a number", pidf.read_text()[:40])
    if not pid_alive(pid):
        kill_tree_by_cwd(d)
        return report("run_background", False, "The process id in report.pid is not running. Is it the id of slow-report.sh, taken "
                      "with $! right after starting it?")
    cmd, end = "", time.time() + 1.5  # right after the fork, the child still shows its parent's command line
    while time.time() < end and "slow-report" not in cmd:
        try:
            cmd = Path(f"/proc/{pid}/cmdline").read_text().replace("\0", " ")
        except OSError:
            break
        time.sleep(0.1)
    if "slow-report" not in cmd:
        kill_tree_by_cwd(d)
        return report("run_background", False, "The process in report.pid is not slow-report.sh.", "slow-report.sh", cmd[:80])
    ign = int(next((l.split()[1] for l in Path(f"/proc/{pid}/status").read_text().splitlines() if l.startswith("SigIgn:")), "0"), 16)
    if not ign & (1 << (signal.SIGHUP - 1)) and os.getsid(pid) == os.getsid(0):
        kill_tree_by_cwd(d)
        return report("run_background", False, "It runs in the background, but closing the terminal would stop it: start it with "
                      "nohup, which makes it ignore the hang-up signal.")
    end = time.time() + 6
    while time.time() < end and "Report done" not in ((d / "report.log").read_text() if (d / "report.log").is_file() else ""):
        time.sleep(0.2)
    log = (d / "report.log").read_text() if (d / "report.log").is_file() else ""
    kill_tree_by_cwd(d)
    if "Report done" not in log:
        return report("run_background", False, "report.log does not have the report's output. Send it there with > report.log 2>&1.",
                      "Report done", log[-80:])
    report("run_background", True, "Started in the background, safe from a closed terminal, output in report.log, id in report.pid.")


# ---------------------------------------------------------------- chapter 9: disk full and permissions (the old chapter 2)

def free_disk():
    logs = WS / "09-disk-full/server/var/log/app"
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
    script = WS / "09-disk-full/fix_perms.sh"
    if not script.is_file():
        return report("fix_perms", False, "09-disk-full/fix_perms.sh is missing.")
    # A fresh server folder with the wrong permissions, plus a script name the learner has not seen.
    target = TMP / "srv"
    shutil.copytree(WS / "09-disk-full/server", target, ignore=shutil.ignore_patterns("*.log"))
    (target / "bin/backup.sh").write_text("#!/usr/bin/env bash\necho backup\n")
    for f in target.rglob("*"):
        if f.is_file():
            f.chmod(0o644)
    code, _, err = run(["bash", str(script), str(target)], cwd=WS / "09-disk-full")
    if code is None:
        return report("fix_perms", False, "fix_perms.sh did not finish in 10 seconds.")
    for sh in sorted((target / "bin").glob("*.sh")):
        if not sh.stat().st_mode & stat.S_IXUSR:
            return report("fix_perms", False, f"bin/{sh.name} is still not executable." + last_line(err),
                          "-rwx", stat.filemode(sh.stat().st_mode))
    secrets = target / "config/secrets.env"
    mode = secrets.stat().st_mode
    if mode & 0o077:
        return report("fix_perms", False, "Other users can still read config/secrets.env.", "-rw-------", stat.filemode(mode))
    if not mode & stat.S_IRUSR:
        return report("fix_perms", False, "Now even the owner cannot read config/secrets.env.", "-rw-------", stat.filemode(mode))
    report("fix_perms", True, "Scripts run, and secrets stay with their owner. Works on any server folder.")


# ---------------------------------------------------------------- chapter 10: scripts

def check_file():
    script = WS / "10-scripts/check_file.sh"
    if not script.is_file():
        return report("check_file", False, "10-scripts/check_file.sh is missing.")
    d = TMP / "cf"
    d.mkdir(exist_ok=True)
    (d / "star list.txt").write_text("Vega\n")
    (d / "empty captures.csv").write_text("")
    cases = [("star list.txt", 0, "OK: star list.txt", "out"), ("no such file.txt", 1, "MISSING: no such file.txt", "err"),
             ("empty captures.csv", 2, "EMPTY: empty captures.csv", "err")]
    for name, want_code, want_text, stream in cases:
        code, out, err = run(["bash", str(script), name], cwd=d)
        if code is None:
            return report("check_file", False, "check_file.sh did not finish. Does it wait for input?")
        where, other = (out, err) if stream == "out" else (err, out)
        if want_text not in where:
            if want_text in other:
                return report("check_file", False, f"For \"{name}\" the message went to the wrong stream. Errors go to standard "
                              "error: echo ... >&2.", stream, "the other one")
            hint = " A name with spaces needs quotes: \"$1\"." if "binary operator expected" in err or "too many arguments" in err else ""
            return report("check_file", False, f"For a file called \"{name}\", check_file.sh printed something else.{hint}",
                          want_text, (out + err).strip()[:120])
        if code != want_code:
            return report("check_file", False, f"For \"{name}\" the message is right but the exit code is {code}. exit {want_code} "
                          "sets it.", want_code, code)
    report("check_file", True, "Three cases, three exit codes, errors on standard error, and names with spaces handled.")


def safe_deploy():
    script = WS / "10-scripts/deploy.sh"
    if not script.is_file():
        return report("safe_deploy", False, "10-scripts/deploy.sh is missing.")
    d = scratch("10-scripts", "deploy")
    shutil.rmtree(d / "live", ignore_errors=True)
    (d / "live").mkdir()
    code, out, err = run(["bash", "deploy.sh"], cwd=d, env={"TARGET": "live", "BUILD_FAILS": "1"})
    if code is None:
        return report("safe_deploy", False, "deploy.sh did not finish in 10 seconds.")
    if code == 0 or (d / "live/site").exists():
        return report("safe_deploy", False, "When the build fails, deploy.sh still copies the site and says Deployed. set -e stops a "
                      "script at the first command that fails.")
    env = {k: v for k, v in os.environ.items() if k != "TARGET"}
    try:
        p = subprocess.run(["bash", "deploy.sh"], cwd=d, env=env, capture_output=True, text=True, timeout=10)
        code, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        code = None
    if code == 0 or "Deployed" in out:
        return report("safe_deploy", False, "Without TARGET, deploy.sh still runs (and would run rm -rf /site). set -u makes an "
                      "unset variable an error.")
    code, out, err = run(["bash", "deploy.sh"], cwd=d, env={"TARGET": "live"})
    if code != 0 or not (d / "live/site/index.html").is_file():
        return report("safe_deploy", False, "Now a normal deploy fails too: TARGET=live bash deploy.sh should copy the site." + last_line(err))
    report("safe_deploy", True, "It stops at the first failure, refuses an unset TARGET, and still deploys when all is well.")


# ---------------------------------------------------------------- chapter 11: loops

def rename_photos():
    d = WS / "11-loops/photos"
    if not d.is_dir():
        return report("rename_photos", False, "The photos folder is gone. Reset brings it back.")
    want = {f"sky-{n:04d}.jpg": f"photo {n:04d}\n" for n in range(1, 13)}
    got = {p.name: p.read_text() for p in d.iterdir() if p.is_file()}
    if got == want:
        return report("rename_photos", True, "Twelve photos renamed by one loop. A hundred would take the same three lines.")
    left = sorted(n for n in got if n.startswith("IMG_"))
    if left and len(left) < 12:
        return report("rename_photos", False, f"{len(left)} photos still have their camera names.", "sky-0001.jpg ...", left[:4])
    if set(got) == set(want):
        return report("rename_photos", False, "The names are right, but some photos ended up with another photo's contents.")
    report("rename_photos", False, "photos should hold sky-0001.jpg to sky-0012.jpg (the number kept, lowercase .jpg).",
           sorted(want)[:3] + ["..."], sorted(got)[:4])


def daily_report():
    script = WS / "11-loops/report.sh"
    if not script.is_file():
        return report("daily_report", False, "11-loops/report.sh is missing.")
    d = TMP / "captures-hidden"
    d.mkdir(exist_ok=True)
    rnd = random.Random(7)
    want = []
    for day in (3, 5, 9, 11):
        n = rnd.randint(50, 400)
        (d / f"captures-2026-12-{day:02d}.csv").write_text("capture_id,dish,target\n" + "".join(f"{i},dish-1,Jupiter\n" for i in range(n)))
        want.append(f"2026-12-{day:02d} {n}")
    (d / "notes.txt").write_text("not a captures file\n")
    code, out, err = run(["bash", str(script), str(d)], cwd=WS / "11-loops")
    if code is None:
        return report("daily_report", False, "report.sh did not finish in 10 seconds. Does it read the folder given as $1?")
    got = [" ".join(l.split()) for l in out.strip().splitlines()]
    if got == want:
        return report("daily_report", True, "Right for a folder it had never seen: one line per day, headers not counted.")
    if [g.split()[0] for g in got if g] == [w.split()[0] for w in want] and all(
            int(g.split()[-1]) == int(w.split()[-1]) + 1 for g, w in zip(got, want) if g.split()[-1].isdigit()):
        return report("daily_report", False, "Each count is one too high: the header line is not a capture.", want, got)
    if not got:
        return report("daily_report", False, "report.sh printed nothing." + last_line(err))
    report("daily_report", False, "On a folder you have not seen, report.sh printed something else.", want, got[:6])


# ---------------------------------------------------------------- chapter 12: the environment

def env_defaults():
    script = WS / "12-environment/start.sh"
    if not script.is_file():
        return report("env_defaults", False, "12-environment/start.sh is missing.")
    base = {k: v for k, v in os.environ.items() if k not in ("PORT", "APP_ENV")}
    cases = [({}, "8080", "development"), ({"PORT": "9000"}, "9000", "development"),
             ({"PORT": "8443", "APP_ENV": "production"}, "8443", "production"), ({"APP_ENV": "staging"}, "8080", "staging")]
    for extra, port, mode in cases:
        try:
            p = subprocess.run(["bash", str(script)], env={**base, **extra}, capture_output=True, text=True, timeout=5, cwd=TMP)
        except subprocess.TimeoutExpired:
            return report("env_defaults", False, "start.sh did not finish in 5 seconds.")
        want = f"Starting Tara on port {port} in {mode} mode"
        if p.stdout.strip() != want:
            setting = " ".join(f"{k}={v}" for k, v in extra.items()) or "nothing set"
            return report("env_defaults", False, f"With {setting}, start.sh printed something else. ${{PORT:-8080}} means PORT, or "
                          "8080 when it is not set.", want, p.stdout.strip()[:120] or last_line(p.stderr))
    report("env_defaults", True, "Right with and without each variable: defaults when unset, the real value when set.")


def path_tool():
    env_sh, tool = WS / "12-environment/env.sh", WS / "12-environment/bin/tara-status"
    if not tool.is_file():
        return report("path_tool", False, "bin/tara-status is gone. Reset brings it back.")
    if not mode_of(tool) & stat.S_IXUSR:
        return report("path_tool", False, "bin/tara-status is not executable yet, so it cannot run as a command (chapter 7).")
    if not env_sh.is_file():
        return report("path_tool", False, "12-environment/env.sh is missing.")
    text = env_sh.read_text().replace("/workspace/", "/check/workspace/").replace("~/12-environment", "/check/workspace/12-environment")
    copy = TMP / "env.sh"
    copy.write_text(text)
    probe = f'source "{copy}" >/dev/null 2>&1; cd /; tara-status; ls / >/dev/null && echo LS-WORKS'
    p = subprocess.run(["bash", "--noprofile", "--norc", "-c", probe], capture_output=True, text=True, timeout=5, cwd=WS / "12-environment",
                       env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin"})
    if "LS-WORKS" not in p.stdout:
        return report("path_tool", False, "After source env.sh, ordinary commands like ls stopped working: the old PATH was replaced. "
                      "Add your folder in front of $PATH, keeping the rest.")
    if "Crab Nebula" not in p.stdout:
        return report("path_tool", False, "After source env.sh, tara-status is still not found from another folder. PATH needs the "
                      "full path of the bin folder, starting with /.")
    report("path_tool", True, "tara-status runs from any folder, and every other command still works.")


# ---------------------------------------------------------------- chapter 13: networking

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(5)
        code = 200 if self.path in ("/health", "/slow") else 500 if self.path == "/broken" else 404
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b"ok\n" if code == 200 else b"no\n")

    def log_message(self, *args):
        pass


def health_check():
    script = WS / "13-networking/health.sh"
    if not script.is_file():
        return report("health_check", False, "13-networking/health.sh is missing.")
    port = free_port()
    srv = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    closed = free_port()
    cases = [(f"http://127.0.0.1:{port}/health", 0, "UP", "a healthy service"),
             (f"http://127.0.0.1:{port}/broken", 1, "DOWN", "a service that answers 500"),
             (f"http://127.0.0.1:{closed}/health", 1, "DOWN", "a port where nothing listens"),
             (f"http://127.0.0.1:{port}/slow", 1, "DOWN", "a service that takes 5 seconds")]
    try:
        for url, want_code, want_text, what in cases:
            code, out, err = run(["bash", str(script), url], cwd=WS / "13-networking", timeout=8)
            if code is None:
                return report("health_check", False, f"For {what}, health.sh waited too long. curl --max-time 3 gives up after 3 seconds.")
            if out.strip() != want_text or code != want_code:
                hint = (" curl alone does not fail on a 500 answer; check the status code (-w '%{http_code}') or use --fail."
                        if what.endswith("500") else "")
                return report("health_check", False, f"For {what}, health.sh gave something else.{hint}",
                              f"{want_text}, exit {want_code}", f"{out.strip()[:40] or '(nothing)'}, exit {code}")
    finally:
        srv.shutdown()
    report("health_check", True, "UP for a healthy service; DOWN for an error, a closed port and a slow answer.")


def fetch_tonight():
    f = WS / "13-networking/tonight-fetched.json"
    if not f.is_file():
        return report("fetch_tonight", False, "There is no tonight-fetched.json in 13-networking yet.")
    try:
        got = json.loads(f.read_text())
    except ValueError:
        text = f.read_text()
        hint = (" It has the HTTP headers too: curl -i shows them, plain curl does not." if text.startswith("HTTP/") else
                " Is the app running? Start it first, in the background.")
        return report("fetch_tonight", False, "tonight-fetched.json is not the JSON the app sends." + hint, "JSON", text[:80])
    want = json.loads((WS / "13-networking/tonight.json").read_text())
    if got != want:
        return report("fetch_tonight", False, "tonight-fetched.json is JSON, but not the plan from /tonight.")
    report("fetch_tonight", True, "Fetched from the running app over HTTP, on port 8080, byte for byte.")


# ---------------------------------------------------------------- chapter 14: services and cron

def unit_file():
    f = WS / "14-services/tara.service"
    cp = configparser.ConfigParser(strict=False, interpolation=None, comment_prefixes=("#", ";"))
    cp.optionxform = str
    try:
        cp.read_string(f.read_text())
    except (configparser.Error, OSError) as e:
        return report("unit_file", False, f"tara.service cannot be read as a unit file: {str(e)[:120]}")
    for section in ("Unit", "Service", "Install"):
        if not cp.has_section(section):
            return report("unit_file", False, f"tara.service has no [{section}] section.")
    u, s, i = cp["Unit"], cp["Service"], cp["Install"]
    want = [
        (u.get("Description", "").strip() != "", "[Unit] needs a Description."),
        ("network.target" in u.get("After", ""), "[Unit] should start the app After=network.target."),
        (s.get("User", "").strip() == "tara", "[Service] should run as the user tara (User=tara), never as root."),
        (s.get("WorkingDirectory", "").strip() == "/srv/tara", "[Service] needs WorkingDirectory=/srv/tara."),
        ("APP_ENV=production" in s.get("Environment", ""), "[Service] needs Environment=APP_ENV=production."),
        (s.get("ExecStart", "").split()[:2] == ["/usr/bin/python3", "/srv/tara/server.py"],
         "[Service] ExecStart should be /usr/bin/python3 /srv/tara/server.py 8080: systemd needs full paths."),
        (s.get("Restart", "").strip() in ("on-failure", "always"), "[Service] needs Restart=on-failure, so a crash is not the end."),
        (i.get("WantedBy", "").strip() == "multi-user.target", "[Install] needs WantedBy=multi-user.target, so it starts at boot."),
    ]
    for ok, msg in want:
        if not ok:
            return report("unit_file", False, msg)
    report("unit_file", True, "A unit systemd would accept: who, where, how, restart on failure, and start at boot.")


NAMES = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "jan": 1, "feb": 2, "mar": 3, "apr": 4,
         "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def cron_field(text, lo, hi):
    out = set()
    for part in text.lower().split(","):
        step = 1
        if "/" in part:
            part, s = part.split("/", 1)
            step = int(s)
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            a, b = (NAMES.get(x, None) if x in NAMES else int(x) for x in part.split("-", 1))
        else:
            a = b = NAMES[part] if part in NAMES else int(part)
        out |= set(range(a, b + 1, step))
    return {0 if (hi == 7 and v == 7) else v for v in out}


def cron_lines():
    f = WS / "14-services/crontab.txt"
    if not f.is_file():
        return report("cron_lines", False, "14-services/crontab.txt is missing.")
    jobs = {}
    for line in f.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split(None, 5)
        if len(parts) < 6:
            return report("cron_lines", False, f"This line needs five time fields and a command: {line.strip()[:80]}")
        try:
            when = (cron_field(parts[0], 0, 59), cron_field(parts[1], 0, 23), cron_field(parts[2], 1, 31),
                    cron_field(parts[3], 1, 12), cron_field(parts[4], 0, 7))
        except (ValueError, KeyError, TypeError):
            return report("cron_lines", False, f"A time field in this line is not valid cron: {line.strip()[:80]}")
        jobs[parts[5].split()[0]] = when
    every = lambda lo, hi: set(range(lo, hi + 1))  # noqa: E731
    want = {
        "/srv/tara/backup.sh": (({30}, {2}, every(1, 31), every(1, 12), every(0, 6)), "every day at 02:30: 30 2 * * *"),
        "/srv/tara/report.sh": (({0}, {9}, every(1, 31), every(1, 12), {1}), "on Mondays at 09:00: the last time field is the day of the week, Monday is 1"),
        "/srv/tara/health.sh": ((set(range(0, 60, 5)), every(0, 23), every(1, 31), every(1, 12), every(0, 6)), "every 5 minutes: */5 in the minute field"),
    }
    for cmd, (when, hint) in want.items():
        if cmd not in jobs:
            return report("cron_lines", False, f"There is no line that runs {cmd} (with its full path).")
        if jobs[cmd] != when:
            return report("cron_lines", False, f"{cmd} runs at the wrong times. It should run {hint}.")
    report("cron_lines", True, "Three schedules cron will understand: daily, weekly and every five minutes.")


# ---------------------------------------------------------------- chapter 15: capstone

APP_PORT = 8090


def start_app(d):
    """Run the learner's app/start.sh in a scratch copy, as an operator would: ./start.sh. Returns an error or None."""
    code, out, err = run(["./start.sh"], cwd=d / "app", timeout=8)
    if code is None:
        return "start.sh did not come back. The app should start in the background."
    if code == 126 or "Permission denied" in err and "start.sh" in err:
        return "./start.sh says Permission denied: it is not executable yet."
    if "No such file or directory" in err:
        return "start.sh fails before the app starts: " + last_line(err).strip() + " Read the message: what is missing?"
    if not wait_port(APP_PORT, 5):
        log = d / "app/logs/app.log"
        tail = log.read_text(errors="replace").strip().splitlines()[-1:] if log.is_file() else []
        return "start.sh ran, but nothing answers on port 8090." + (f" The app's log ends with: {tail[0][:160]}" if tail else "")
    return None


def capstone_fix():
    plan = WS / "15-capstone/app/tonight.json"
    if plan.is_file() and not mode_of(plan) & stat.S_IRUSR:
        return report("capstone_fix", False, "The app cannot start: it cannot read one of its files. Its log says which. (ls -l shows "
                      "permissions.)")
    if not (WS / "15-capstone/app/start.sh").is_file():
        return report("capstone_fix", False, "app/start.sh is gone. Reset brings it back.")
    d = scratch("15-capstone", "cap1")
    (d / "app/logs/app.log").unlink(missing_ok=True)
    try:
        problem = start_app(d)
        if problem:
            return report("capstone_fix", False, problem)
        status, body = http_get(f"http://127.0.0.1:{APP_PORT}/tonight")
        if status != 200 or "Crab Nebula" not in body:
            return report("capstone_fix", False, "The app answers, but /tonight does not give tonight's plan.", 200, status)
    finally:
        kill_tree_by_cwd(d)
    report("capstone_fix", True, "The observatory is back on the air: ./start.sh works and /tonight answers.")


def capstone_watch():
    if not (WS / "15-capstone/watchdog.sh").is_file():
        return report("capstone_watch", False, "15-capstone/watchdog.sh is missing.")
    plan = WS / "15-capstone/app/tonight.json"
    if not plan.is_file() or not mode_of(plan) & stat.S_IRUSR:
        return report("capstone_watch", False, "Fix the app first (the task before this one): the watchdog restarts it with start.sh.")
    d = scratch("15-capstone", "cap2")
    (d / "watchdog.log").unlink(missing_ok=True)
    try:
        if start_app(d) is not None:
            kill_tree_by_cwd(d)
            return report("capstone_watch", False, "Fix the app first (the task before this one): the watchdog restarts it with start.sh.")
        kill_tree_by_cwd(d)
        time.sleep(0.3)
        text = (d / "watchdog.sh").read_text().replace("/workspace/", f"{TMP}/").replace(f"{TMP}/15-capstone", str(d))
        (d / "watchdog.sh").write_text(text)
        code, out, err = run(["bash", str(d / "watchdog.sh")], cwd="/", timeout=10)
        if code is None:
            return report("capstone_watch", False, "watchdog.sh did not finish in 10 seconds.")
        if not wait_port(APP_PORT, 5):
            return report("capstone_watch", False, "With the app down, watchdog.sh did not bring it back (it was run from another "
                          "folder, as cron would)." + last_line(err))
        log = d / "watchdog.log"
        lines = log.read_text().strip().splitlines() if log.is_file() else []
        if len(lines) != 1 or "restarted the app" not in lines[0]:
            return report("capstone_watch", False, "The app is back, but watchdog.log should have one line like "
                          "\"2026-11-23 12:31:00 restarted the app\".", 1, lines[:3])
        if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} restarted the app$", lines[0].strip()):
            return report("capstone_watch", False, "The line should start with the date and time: date '+%Y-%m-%d %H:%M:%S'.",
                          "YYYY-MM-DD HH:MM:SS restarted the app", lines[0][:80])
        run(["bash", str(d / "watchdog.sh")], cwd="/", timeout=10)
        lines = log.read_text().strip().splitlines()
        if len(lines) != 1:
            return report("capstone_watch", False, "With the app healthy, watchdog.sh should do nothing, but it wrote to watchdog.log "
                          "again (or started a second copy).", 1, len(lines))
    finally:
        kill_tree_by_cwd(d)
    report("capstone_watch", True, "Down: restarted and logged. Up: left alone. Run every minute from cron, this is how small "
           "teams sleep at night.")


CHECKS = [hidden_file, deep_file, tidy_folder, backup_copy, count_observations, last_lines, errors_only, target_list, count_5xx, top_ips,
          slowest, find_big, find_secret, make_executable, private_key, stop_hog, run_background, free_disk, fix_perms,
          check_file, safe_deploy, rename_photos, daily_report, env_defaults, path_tool, health_check, fetch_tonight, unit_file,
          cron_lines, capstone_fix, capstone_watch]

try:
    for check in CHECKS:
        if not WANTED or check.__name__ in WANTED:
            try:
                check()
            except Exception as e:  # noqa: BLE001
                report(check.__name__, False, f"The check could not finish: {type(e).__name__}: {str(e)[:160]}")
finally:
    for p in STARTED:
        if p.poll() is None:
            p.kill()
    kill_tree_by_cwd(TMP)
    shutil.rmtree(TMP, ignore_errors=True)
