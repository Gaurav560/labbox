"""Live checks for git-without-fear: read the learner's real repos (read-only) and inspect their history."""
import json
import subprocess
from pathlib import Path

WS = Path("/check/workspace")
# The kitchen setup uses fixed authors and dates, so these hashes are the same for every learner.
PUSHED = "5ac0465ba0c60b2d5aef04c1dc6d52cbee1a919d"  # "Add the prep list", already on origin
BAD = "6af4e0e867f35fde240a7cccb0833df0eb5cce9b"     # "Raise filter coffee to 300"
HOURS = "Mon to Sat: 7:00 to 22:00\nSun: 8:00 to 20:00\n"
COMBO = "filter coffee + vada pav = 50"


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


def git(repo, *args):
    """(ok, stdout) of a read-only git command in a repo."""
    p = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(WS / repo), *args], capture_output=True, text=True, timeout=10)
    return p.returncode == 0, p.stdout


def show(repo, ref, path):
    ok, out = git(repo, "show", f"{ref}:{path}")
    return out if ok else None


def is_ancestor(repo, a, b):
    return git(repo, "merge-base", "--is-ancestor", a, b)[0]


def repo_ready(repo, tasks, chapter):
    if (WS / repo / ".git").is_dir():
        return True
    for t in tasks:
        report(t, False, f"The {repo} repo is missing. Open chapter {chapter} again, or press Reset lab.")
    return False


# ---------- chapter 1: shop ----------

def commit_hours():
    content = show("shop", "main", "hours.txt")
    if content is None:
        return report("commit_hours", False, "hours.txt is not in any commit on main yet. Did you git add it, then git commit?")
    if content != HOURS:
        return report("commit_hours", False, "hours.txt on main is different from the file you were given.", HOURS, content)
    _, subjects = git("shop", "log", "main", "--format=%s", "--", "hours.txt")
    if "hour" not in subjects.lower():
        return report("commit_hours", False, "Say what the commit does: its message should mention the hours.", "a message with 'hours'", subjects.strip())
    report("commit_hours", True, "Committed, with a message that says why.")


def combo_branch():
    if not git("shop", "rev-parse", "--verify", "-q", "refs/heads/feature/combo")[0]:
        return report("combo_branch", False, "There is no branch called feature/combo.", "feature/combo", "missing")
    content = show("shop", "feature/combo", "combo.txt")
    if content is None:
        return report("combo_branch", False, "combo.txt is not committed on feature/combo.")
    if COMBO not in content:
        return report("combo_branch", False, "combo.txt needs the combo line.", COMBO, content.strip())
    report("combo_branch", True, "The combo lives on its own branch.")


def merge_combo():
    if not git("shop", "rev-parse", "--verify", "-q", "refs/heads/feature/combo")[0]:
        return report("merge_combo", False, "Make the feature/combo branch first.")
    if not is_ancestor("shop", "feature/combo", "main"):
        return report("merge_combo", False, "main does not have the feature/combo commits yet. Switch to main, then merge.")
    if show("shop", "main", "hours.txt") is None:
        return report("merge_combo", False, "main lost hours.txt. Merge should add the combo, not drop other work.")
    report("merge_combo", True, "feature/combo is merged into main.")


# ---------- chapter 2: kitchen ----------

def undo_secret():
    _, touched = git("kitchen", "log", "main", "--format=%h %s", "--", "secrets.env")
    if touched.strip():
        return report("undo_secret", False, "A commit on main still has secrets.env in it. Deleting it in a new commit is not "
                      "enough: the old commit still holds it. Change the last commit instead.", "no commit with secrets.env", touched.strip())
    if not (WS / "kitchen/secrets.env").is_file():
        return report("undo_secret", False, "secrets.env is gone from your folder. Keep the file, just not in git.")
    if "secrets.env" not in (show("kitchen", "main", ".gitignore") or "").split():
        return report("undo_secret", False, "Add secrets.env to a committed .gitignore, so it cannot be added again by accident.")
    if "SMS settings" not in (show("kitchen", "main", "README.md") or ""):
        return report("undo_secret", False, "The README from that commit is gone. Remove only the secret, keep the rest.")
    report("undo_secret", True, "The secret never happened, and .gitignore keeps it out.")


def revert_bad():
    if not is_ancestor("kitchen", PUSHED, "main"):
        return report("revert_bad", False, "main no longer has the commits that were already pushed. Pushed history must not "
                      "be rewritten: other people have it. Reset lab, then fix it with a new commit.")
    menu = show("kitchen", "main", "menu.txt") or ""
    if "filter coffee 30\n" not in menu:
        return report("revert_bad", False, "filter coffee is still not 30 on main.", "filter coffee 30", menu.strip())
    _, subjects = git("kitchen", "log", "--format=%s", f"{PUSHED}..main")
    if not any(s.startswith("Revert") and "300" in s for s in subjects.splitlines()):
        return report("revert_bad", False, "Undo the bad commit with git revert, so the history shows what happened and why.",
                      "a Revert commit", subjects.strip() or "no new commits")
    report("revert_bad", True, "Pushed history kept, mistake undone in the open.")


if repo_ready("shop", ("commit_hours", "combo_branch", "merge_combo"), 1):
    commit_hours()
    combo_branch()
    merge_combo()
if repo_ready("kitchen", ("undo_secret", "revert_bad"), 2):
    undo_secret()
    revert_bad()
