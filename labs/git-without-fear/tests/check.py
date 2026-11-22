"""Live checks for git-without-fear (Trails, a trekking website): read the learner's real repositories (mounted
read-only) with plain, read-only git commands. Never runs learner code. Only the tasks in LABBOX_TASKS run."""
import json
import os
import re
import subprocess
from pathlib import Path

WS = Path("/check/workspace")
WANTED = {t for t in os.environ.get("LABBOX_TASKS", "").split(",") if t}

RULES = "# Safety rules\n\n1. Tell someone where you are going.\n2. Carry two litres of water.\n3. Start back before 3 pm.\n"
NOTES = "Ideas for later:\n- a map page\n"
MONSOON = "Monsoon treks: carry a raincoat and check the forecast"
MARKERS = re.compile(r"^(<<<<<<<|=======|>>>>>>>)", re.M)


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


def git(repo, *args):
    """(ok, stdout) of a read-only git command in a repository, given as a path relative to the workspace."""
    p = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(WS / repo), *args], capture_output=True, text=True, timeout=10)
    return p.returncode == 0, p.stdout


def show(repo, ref, path):
    ok, out = git(repo, "show", f"{ref}:{path}")
    return out if ok else None


def exists(repo, ref):
    return git(repo, "rev-parse", "--verify", "-q", ref + "^{commit}")[0]


def is_ancestor(repo, a, b):
    return git(repo, "merge-base", "--is-ancestor", a, b)[0]


def by_message(repo, message, ref="--all"):
    ok, out = git(repo, "log", ref, "--format=%H %s")
    for line in out.splitlines():
        h, _, s = line.partition(" ")
        if s == message:
            return h
    return None


def answer(folder, name):
    p = WS / folder / name
    return p.read_text(encoding="utf-8", errors="replace").strip() if p.is_file() else None


def repo_ok(task, repo, chapter):
    if (WS / repo / ".git").is_dir() or (WS / repo / "HEAD").is_file():
        return True
    report(task, False, f"The repository {repo} is missing. Open chapter {chapter} again, or press Reset lab.")
    return False


# ---------- chapter 1: why version control ----------

def first_repo():
    if not (WS / "01-why-version-control/trails/.git").is_dir():
        return report("first_repo", False, "01-why-version-control/trails is not a git repository yet. Go into the folder and run git init.")
    report("first_repo", True, "trails is a git repository: it can now remember every version.")


def first_commit():
    r = "01-why-version-control/trails"
    if not (WS / r / ".git").is_dir():
        return report("first_commit", False, "Make the repository first (the task before this one).")
    if not exists(r, "HEAD"):
        return report("first_commit", False, "The repository has no commits yet. Add both files, then commit them.")
    _, files = git(r, "ls-tree", "--name-only", "HEAD")
    missing = [f for f in ("README.md", "trails.md") if f not in files.split()]
    if missing:
        return report("first_commit", False, f"The last commit does not have {missing[0]}. Add both files before you commit.",
                      "README.md and trails.md", ", ".join(files.split()) or "nothing")
    report("first_commit", True, "Your first commit: both files, saved with who, when and why.")


# ---------- chapter 2: commits ----------

def commit_hours():
    r = "02-commits/trails"
    if not repo_ok("commit_hours", r, 2):
        return
    content = show(r, "main", "rules.md")
    if content is None:
        return report("commit_hours", False, "rules.md is not in any commit on main yet. git add it, then git commit.")
    if content != RULES:
        return report("commit_hours", False, "rules.md on main is different from the file you were given.", RULES, content)
    _, subjects = git(r, "log", "main", "--format=%s", "--", "rules.md")
    if "rule" not in subjects.lower():
        return report("commit_hours", False, "Say what the commit does: its message should mention the rules.",
                      "a message about the safety rules", subjects.strip())
    report("commit_hours", True, "Committed, with a message that says what and why.")


def stage_part():
    r = "02-commits/trails"
    if not repo_ok("stage_part", r, 2):
        return
    trails = show(r, "main", "trails.md") or ""
    if "## Harishchandragad" not in trails:
        return report("stage_part", False, "The new trail (Harishchandragad) is not committed on main yet.")
    if show(r, "main", "notes.txt") != NOTES:
        return report("stage_part", False, "notes.txt was committed too. Only trails.md belonged in that commit: "
                      "stage one file with git add trails.md (Reset lab to try again).", "notes.txt unchanged in git", "notes.txt committed")
    local = (WS / r / "notes.txt").read_text() if (WS / r / "notes.txt").is_file() else ""
    if "ask Ravi" not in local:
        return report("stage_part", False, "Your scratch line in notes.txt is gone from the folder. It should stay there, just not in git.")
    report("stage_part", True, "One commit, one change: the trail went in, the scratch notes stayed out.")


# ---------- chapter 3: history ----------

def find_author():
    r = "03-history/trails"
    if not repo_ok("find_author", r, 3):
        return
    got = answer("03-history", "answer-author.txt")
    if got is None:
        return report("find_author", False, "Write the name in 03-history/answer-author.txt (next to the trails folder).")
    if got.lower() == "ravi":
        return report("find_author", True, "Ravi changed it, in \"Update Rajmachi's distance\": blame shows who touched a line last.")
    report("find_author", False, "That is not who changed the distance line last. Run git blame on trails.md and read that line.",
           "a name", got)


def find_commit():
    r = "03-history/trails"
    if not repo_ok("find_commit", r, 3):
        return
    removed = by_message(r, "Tidy up the Rajmachi section")
    added = by_message(r, "Add a water point to Rajmachi")
    got = (answer("03-history", "answer-commit.txt") or "").lower()
    if not got:
        return report("find_commit", False, "Write the commit's hash (the first 7 characters are enough) in 03-history/answer-commit.txt.")
    if len(got) < 7 or not re.fullmatch(r"[0-9a-f]+", got):
        return report("find_commit", False, "Write just the hash: at least 7 of its characters, like 1a2b3c4.", "a hash", got)
    if added and added.startswith(got):
        return report("find_commit", False, "That is the commit that added the water point. You need the one that removed it: "
                      "git log -S shows both, newest first.")
    if removed and removed.startswith(got):
        return report("find_commit", True, "Found it: Meera's \"tidy up\" removed the water point. git log -S finds when text came or went.")
    report("find_commit", False, "That hash is not the commit that removed the water point line.", "a hash from git log -S", got)


# ---------- chapter 4: branches ----------

def combo_branch():
    r = "04-branches/trails"
    if not repo_ok("combo_branch", r, 4):
        return
    if not exists(r, "refs/heads/feature/monsoon"):
        return report("combo_branch", False, "There is no branch called feature/monsoon.", "feature/monsoon", "missing")
    content = show(r, "feature/monsoon", "monsoon.md")
    if content is None:
        return report("combo_branch", False, "monsoon.md is not committed on feature/monsoon.")
    if MONSOON not in content:
        return report("combo_branch", False, "monsoon.md needs the line from the task.", MONSOON, content.strip())
    report("combo_branch", True, "The monsoon page lives on its own branch, and main is untouched.")


def merge_combo():
    r = "04-branches/trails"
    if not repo_ok("merge_combo", r, 4):
        return
    if not exists(r, "refs/heads/feature/monsoon"):
        return report("merge_combo", False, "Make the feature/monsoon branch first.")
    if not is_ancestor(r, "feature/monsoon", "main"):
        return report("merge_combo", False, "main does not have the feature/monsoon commits yet. Switch to main, then merge.")
    if show(r, "main", "trails.md") is None:
        return report("merge_combo", False, "main lost trails.md. A merge should add the monsoon page, not drop other work.")
    report("merge_combo", True, "feature/monsoon is merged into main.")


# ---------- chapter 5: merge conflicts ----------

def resolve_conflict():
    r = "05-merge-conflicts/trails"
    if not repo_ok("resolve_conflict", r, 5):
        return
    if not is_ancestor(r, "ravi/rajmachi", "main"):
        return report("resolve_conflict", False, "ravi/rajmachi is not merged into main yet. On main: git merge ravi/rajmachi.")
    trails = show(r, "main", "trails.md") or ""
    if MARKERS.search(trails):
        return report("resolve_conflict", False, "trails.md on main still has conflict markers (<<<<<<<, =======, >>>>>>>). "
                      "Edit them out, then add and commit.")
    if "- Distance: 16 km" not in trails:
        line = next((l for l in trails.splitlines() if l.startswith("- Distance: 1")), "missing")
        return report("resolve_conflict", False, "Rajmachi's distance should be Ravi's GPS number.", "- Distance: 16 km", line)
    if "## Kalsubai" not in trails:
        return report("resolve_conflict", False, "Kalsubai disappeared from trails.md while resolving. Keep everything else.")
    report("resolve_conflict", True, "Conflict resolved: the right distance, nothing else lost, and a merge commit that says so.")


def combine_both():
    r = "05-merge-conflicts/trails"
    if not repo_ok("combine_both", r, 5):
        return
    if not is_ancestor(r, "meera/readme", "main"):
        return report("combine_both", False, "meera/readme is not merged into main yet.")
    readme = show(r, "main", "README.md") or ""
    if MARKERS.search(readme):
        return report("combine_both", False, "README.md on main still has conflict markers.")
    have = [x for x in ("Photos by Meera.", "Maps by Asha.") if x in readme]
    if len(have) < 2:
        return report("combine_both", False, "Both credits belong in the README: neither side was wrong.", "Photos by Meera. and Maps by Asha.",
                      ", ".join(have) or "neither")
    report("combine_both", True, "Both credits kept: sometimes the right resolution is to keep both sides.")


# ---------- chapter 6: undoing local work ----------

def undo_secret():
    r = "06-undo-local/trails"
    if not repo_ok("undo_secret", r, 6):
        return
    _, touched = git(r, "log", "main", "--format=%h %s", "--", "secrets.env")
    if touched.strip():
        return report("undo_secret", False, "A commit on main still has secrets.env in it. Deleting it in a new commit is not enough: "
                      "the old commit still holds it. Change the last commit instead.", "no commit with secrets.env", touched.strip())
    if not (WS / r / "secrets.env").is_file():
        return report("undo_secret", False, "secrets.env is gone from your folder. Keep the file, just not in git.")
    if "secrets.env" not in (show(r, "main", ".gitignore") or "").split():
        return report("undo_secret", False, "Add secrets.env to a committed .gitignore, so it cannot be added again by accident.")
    if "maps API settings" not in (show(r, "main", "README.md") or ""):
        return report("undo_secret", False, "The README change from that commit is gone. Remove only the secret, keep the rest.")
    report("undo_secret", True, "The secret never happened, and .gitignore keeps it out.")


def discard_changes():
    r = "06-undo-local/trails"
    if not repo_ok("discard_changes", r, 6):
        return
    committed = show(r, "main", "trails.md") or ""
    if "## Kalsubai" not in committed:
        return report("discard_changes", False, "The half-deleted trails.md was committed. Reset lab, and throw the accident away instead of saving it.")
    local = (WS / r / "trails.md").read_text() if (WS / r / "trails.md").is_file() else ""
    if local != committed:
        return report("discard_changes", False, "trails.md in your folder is still different from the last commit.",
                      "the committed version", "a changed file")
    notes = (WS / r / "notes.md").read_text() if (WS / r / "notes.md").is_file() else ""
    if "night trek" not in notes:
        return report("discard_changes", False, "Your good edit to notes.md was thrown away too. Restore only trails.md.")
    report("discard_changes", True, "trails.md is back as it was, and your notes edit survived.")


# ---------- chapter 7: undoing shared history ----------

def revert_bad():
    r, server = "07-undo-shared/trails", "07-undo-shared/server/trails.git"
    if not repo_ok("revert_bad", r, 7):
        return
    pushed = by_message(r, "Add trekking tips")
    if not pushed or not is_ancestor(r, pushed, "main"):
        return report("revert_bad", False, "main no longer has the commits that were already pushed. Pushed history must not be "
                      "rewritten: others have it. Reset lab, then fix it with a new commit.")
    kalsubai = (show(r, "main", "trails.md") or "").split("## Kalsubai")[-1]
    if "- Difficulty: hard" not in kalsubai:
        return report("revert_bad", False, "Kalsubai is still marked easy on main.", "- Difficulty: hard", "easy")
    _, subjects = git(r, "log", "--format=%s", f"{pushed}..main")
    if not any(s.startswith("Revert") and "Kalsubai" in s for s in subjects.splitlines()):
        return report("revert_bad", False, "Undo the bad commit with git revert, so the history shows what happened.",
                      "a Revert commit", subjects.strip() or "no new commits")
    if "- Difficulty: hard" not in (show(server, "main", "trails.md") or "").split("## Kalsubai")[-1]:
        return report("revert_bad", False, "The fix is only on your machine. Push it, so everyone gets it.")
    report("revert_bad", True, "Pushed history kept, mistake undone in the open, and the fix pushed.")


def rescue_commit():
    r = "07-undo-shared/trails"
    if not repo_ok("rescue_commit", r, 7):
        return
    if not exists(r, "refs/heads/rescued"):
        return report("rescue_commit", False, "There is no branch called rescued yet. Find the lost commit with git reflog.")
    if by_message(r, "Add Visapur", "rescued") is None:
        return report("rescue_commit", False, "rescued does not contain the \"Add Visapur\" commit.", "Add Visapur", "missing")
    if "## Visapur" not in (show(r, "rescued", "trails.md") or ""):
        return report("rescue_commit", False, "rescued has the commit, but trails.md there has no Visapur section.")
    report("rescue_commit", True, "The \"lost\" commit is back on a branch. Almost nothing in git is ever really gone.")


# ---------- chapter 8: stash and clean ----------

def stash_work():
    r = "08-stash/trails"
    if not repo_ok("stash_work", r, 8):
        return
    readme = show(r, "main", "README.md") or ""
    if "Sahyadry" in readme or "Sahyadri" not in readme:
        return report("stash_work", False, "The README typo (Sahyadry) is not fixed in a commit on main yet.")
    if "## Lohagad" in readme or "## Lohagad" in (show(r, "main", "trails.md") or ""):
        return report("stash_work", False, "The half-written Lohagad section ended up on main. Stash it before you switch.")
    ok, head = git(r, "symbolic-ref", "--short", "HEAD")
    if head.strip() != "feature/lohagad":
        return report("stash_work", False, "Go back to feature/lohagad when the fix is done.", "feature/lohagad", head.strip() or "a detached HEAD")
    local = (WS / r / "trails.md").read_text() if (WS / r / "trails.md").is_file() else ""
    if "## Lohagad" not in local:
        _, stashes = git(r, "stash", "list")
        hint = " It is still in the stash: git stash pop." if stashes.strip() else ""
        return report("stash_work", False, "Your half-written Lohagad section is not back in trails.md." + hint)
    report("stash_work", True, "Fix shipped on main, and your unfinished work is back exactly where you left it.")


def clean_untracked():
    r = "08-stash/trails"
    if not repo_ok("clean_untracked", r, 8):
        return
    if not (WS / r / "ideas.md").is_file():
        return report("clean_untracked", False, "ideas.md was deleted too: it was a keeper. Preview with git clean -n first (Reset lab restores it).")
    left = [p for p in ("preview", "draft.tmp") if (WS / r / p).exists()]
    if left:
        return report("clean_untracked", False, f"{left[0]} is still there.", "preview/ and draft.tmp gone", ", ".join(left))
    report("clean_untracked", True, "Junk gone, ideas.md kept. A dry run first is the habit that saves you.")


# ---------- chapter 9: remotes ----------

def pull_changes():
    r, server = "09-remotes/trails", "09-remotes/server/trails.git"
    if not repo_ok("pull_changes", r, 9):
        return
    ravi = by_message(server, "Add Harishchandragad")
    if not ravi:
        return report("pull_changes", False, "Ravi's commit is missing from the server. Press Reset lab.")
    if not exists(r, ravi) or not is_ancestor(r, ravi, "main"):
        return report("pull_changes", False, "Your main does not have Ravi's commit yet. git pull brings it in.")
    report("pull_changes", True, "Ravi's Harishchandragad commit is in your main.")


def push_work():
    r, server = "09-remotes/trails", "09-remotes/server/trails.git"
    if not repo_ok("push_work", r, 9):
        return
    trails = show(server, "main", "trails.md") or ""
    if "## Visapur" not in trails:
        local = "## Visapur" in (show(r, "main", "trails.md") or "")
        return report("push_work", False, "Visapur is committed but not pushed yet." if local else "There is no Visapur section on the server yet.")
    ravi = by_message(server, "Add Harishchandragad")
    if ravi and not is_ancestor(server, ravi, "main"):
        return report("push_work", False, "Ravi's commit is gone from the server. Never force-push over others' work (Reset lab).")
    report("push_work", True, "Your Visapur commit is on the server, on top of Ravi's.")


# ---------- chapter 10: a pull request ----------

def torna(text):
    return text.split("## Torna", 1)[1] if "## Torna" in text else None


def push_branch():
    server = "10-pull-request/server/trails.git"
    if not repo_ok("push_branch", "10-pull-request/trails", 10):
        return
    if not exists(server, "refs/heads/feature/torna"):
        return report("push_branch", False, "The server has no feature/torna branch yet. Push it with git push -u origin feature/torna.")
    section = torna(show(server, "feature/torna", "trails.md") or "")
    if section is None or "- Distance: 7 km" not in section:
        return report("push_branch", False, "feature/torna on the server needs the Torna section from the task.")
    report("push_branch", True, "The branch is on the server, ready for review.")


def merge_reviewed():
    server = "10-pull-request/server/trails.git"
    if not repo_ok("merge_reviewed", "10-pull-request/trails", 10):
        return
    if not exists(server, "refs/heads/feature/torna"):
        return report("merge_reviewed", False, "Push the feature/torna branch first (the task before this one).")
    branch = torna(show(server, "feature/torna", "trails.md") or "") or ""
    if "- Best season: October to February" not in branch:
        return report("merge_reviewed", False, "The review asked for Torna's best season. Add it on feature/torna, commit, and push the branch.")
    if not is_ancestor(server, "feature/torna", "main"):
        return report("merge_reviewed", False, "The reviewed branch is not merged into main on the server yet.")
    report("merge_reviewed", True, "Reviewed, fixed, merged and pushed: a pull request, end to end.")


# ---------- chapter 11: rebase ----------

def rebase_branch():
    r = "11-rebase/trails"
    if not repo_ok("rebase_branch", r, 11):
        return
    if not exists(r, "refs/heads/feature/sinhagad"):
        return report("rebase_branch", False, "The feature/sinhagad branch is missing. Press Reset lab.")
    if not is_ancestor(r, "main", "feature/sinhagad"):
        return report("rebase_branch", False, "feature/sinhagad does not start from the latest main yet. On the branch: git rebase main.")
    _, merges = git(r, "log", "--merges", "--format=%h", "main..feature/sinhagad")
    if merges.strip():
        return report("rebase_branch", False, "The branch has a merge commit. Rebase replays your commits instead of merging (Reset lab to retry).")
    if "- Best season: all year" not in (show(r, "feature/sinhagad", "trails.md") or ""):
        return report("rebase_branch", False, "The Sinhagad section is incomplete on the branch.")
    report("rebase_branch", True, "feature/sinhagad now sits on top of the latest main: a straight line of history.")


def squash_commits():
    r = "11-rebase/trails"
    if not repo_ok("squash_commits", r, 11):
        return
    _, ahead = git(r, "log", "--format=%s", "main..feature/sinhagad")
    subjects = ahead.splitlines()
    if len(subjects) != 1:
        return report("squash_commits", False, f"feature/sinhagad has {len(subjects)} commits ahead of main. Make them one.", "1", str(len(subjects)))
    if subjects[0].lower().startswith("wip") or subjects[0].lower().startswith("done"):
        return report("squash_commits", False, "Give the single commit a real message, like \"Add Sinhagad\".", "a clear message", subjects[0])
    if "- Best season: all year" not in (show(r, "feature/sinhagad", "trails.md") or ""):
        return report("squash_commits", False, "The squashed commit lost some of the Sinhagad lines.")
    report("squash_commits", True, f"One clear commit, \"{subjects[0]}\", instead of three wip ones.")


# ---------- chapter 12: inside git ----------

def hash_answer(task, file, ref, what):
    r = "12-inside-git/trails"
    if not repo_ok(task, r, 12):
        return
    _, truth = git(r, "rev-parse", ref)
    truth = truth.strip()
    got = (answer("12-inside-git", file) or "").lower()
    if not got:
        return report(task, False, f"Write the {what}'s hash in 12-inside-git/{file}.")
    if len(got) < 7 or not re.fullmatch(r"[0-9a-f]+", got):
        return report(task, False, "Write just the hash, at least 7 characters.", "a hash", got)
    if truth.startswith(got):
        return report(task, True, f"Right: {truth[:12]}..., the {what}'s own name, computed from its content.")
    _, head = git(r, "rev-parse", "HEAD")
    if head.strip().startswith(got):
        return report(task, False, f"That is the commit's hash. You need the {what}'s hash: git cat-file -p HEAD shows it.")
    report(task, False, f"That is not the {what}'s hash.", "the hash git shows", got)


def tree_hash():
    hash_answer("tree_hash", "answer-tree.txt", "HEAD^{tree}", "tree")


def blob_hash():
    hash_answer("blob_hash", "answer-blob.txt", "HEAD:trails.md", "trails.md blob")


# ---------- chapter 13: good habits ----------

def gitignore_files():
    r = "13-good-habits/trails"
    if not repo_ok("gitignore_files", r, 13):
        return
    if show(r, "HEAD", ".gitignore") is None:
        return report("gitignore_files", False, "There is no committed .gitignore yet. Write it, then add and commit it.")
    for path in ("node_modules/marked/index.js", "build.log", ".env"):
        if not git(r, "check-ignore", "-q", "--no-index", path)[0]:
            return report("gitignore_files", False, f"{path} is not ignored by your .gitignore.", "ignored", "not ignored")
    _, tracked = git(r, "ls-files")
    bad = [f for f in tracked.split() if f.startswith("node_modules/") or f in ("build.log", ".env")]
    if bad:
        return report("gitignore_files", False, f"{bad[0]} is already committed. Ignoring does not untrack: git rm --cached it.")
    report("gitignore_files", True, "Dependencies, logs and secrets can never be committed by accident now.")


def tag_release():
    r = "13-good-habits/trails"
    if not repo_ok("tag_release", r, 13):
        return
    if not git(r, "rev-parse", "-q", "--verify", "refs/tags/v1.0")[0]:
        return report("tag_release", False, "There is no tag called v1.0.")
    _, kind = git(r, "cat-file", "-t", "v1.0")
    if kind.strip() != "tag":
        return report("tag_release", False, "v1.0 is a lightweight tag. A release tag should be annotated (-a, with a message).", "annotated", "lightweight")
    want = by_message(r, "Ready for the first release")
    _, got = git(r, "rev-parse", "v1.0^{commit}")
    if got.strip() != want:
        return report("tag_release", False, "v1.0 points at the wrong commit.", "Ready for the first release", "another commit")
    report("tag_release", True, "v1.0 is tagged, annotated, on exactly the commit that was released.")


# ---------- chapter 14: capstone ----------

def capstone_clean():
    r = "14-capstone/trails"
    if not repo_ok("capstone_clean", r, 14):
        return
    pushed = by_message("14-capstone/server/trails.git", "Add the README and two trails")
    if not pushed or not is_ancestor(r, pushed, "main"):
        return report("capstone_clean", False, "The pushed commit is gone from main. Only rewrite the commits that are not pushed (Reset lab).")
    _, touched = git(r, "log", "main", "--format=%h %s", "--", "credentials.json")
    if touched.strip():
        return report("capstone_clean", False, "credentials.json is still in a commit on main. Removing it in a later commit is not enough.",
                      "no commit with credentials.json", touched.strip())
    if show(r, "main", "tips.md") is None:
        return report("capstone_clean", False, "tips.md was lost while cleaning. Keep it; only the credentials must go.")
    report("capstone_clean", True, "The leaked file is gone from every commit, and the pushed history is untouched.")


def capstone_release():
    r, server = "14-capstone/trails", "14-capstone/server/trails.git"
    if not repo_ok("capstone_release", r, 14):
        return
    if not exists(r, "refs/heads/feature/maps") or not is_ancestor(r, "feature/maps", "main"):
        return report("capstone_release", False, "feature/maps is not merged into main yet.")
    if not git(server, "rev-parse", "-q", "--verify", "refs/tags/v2.0")[0]:
        return report("capstone_release", False, "The server has no v2.0 tag yet. Tag main (annotated), then push main and the tag.")
    _, kind = git(server, "cat-file", "-t", "v2.0")
    if kind.strip() != "tag":
        return report("capstone_release", False, "v2.0 should be an annotated tag.", "annotated", "lightweight")
    _, tagged = git(server, "rev-parse", "v2.0^{commit}")
    _, main = git(server, "rev-parse", "main")
    if tagged.strip() != main.strip():
        return report("capstone_release", False, "v2.0 should point at the main that is on the server. Push main too.")
    _, touched = git(server, "log", "main", "--format=%h", "--", "credentials.json")
    if touched.strip():
        return report("capstone_release", False, "The server's main still has the credentials file in its history. Clean main first, then push.")
    if show(server, "main", "maps.md") is None:
        return report("capstone_release", False, "The server's main has no maps.md.")
    report("capstone_release", True, "Clean history, the maps feature merged, v2.0 tagged and pushed. That is a release.")


CHECKS = [first_repo, first_commit, commit_hours, stage_part, find_author, find_commit, combo_branch, merge_combo,
          resolve_conflict, combine_both, undo_secret, discard_changes, revert_bad, rescue_commit, stash_work, clean_untracked,
          pull_changes, push_work, push_branch, merge_reviewed, rebase_branch, squash_commits, tree_hash, blob_hash,
          gitignore_files, tag_release, capstone_clean, capstone_release]

for check in CHECKS:
    if not WANTED or check.__name__ in WANTED:
        check()
