:::step{type=story title="Two accidents before lunch"}
Welcome to Part 2: undo without fear. This is the part that turns nervous Git users into calm ones.

Asha has had a bad morning. First, she committed the README change together with `secrets.env`, a file holding the
maps service's API key. It is only on her laptop so far, but if she pushes, the key will be in the history forever,
visible to anyone with a copy. Second, while editing, she accidentally deleted most of `trails.md`, and she has also
made a good edit to `notes.md` that she wants to keep.

Both mistakes are completely fixable, because neither has left her machine. The rule of this chapter: **while a
mistake is only on your machine, you may change history; once others have it, you add a new commit instead**
(chapter 7). Today you learn the first half: restoring files, unstaging, and rewriting your last commit.

:::mission
Take the secret out of the last commit without losing the README change, and throw away the accidental deletion
while keeping the good edit.
:::
:::

:::step{type=try title="Look at the damage first"}
Before undoing anything, look. Calm diagnosis is half of every rescue:

```text
$ cd /workspace/06-undo-local/trails
$ git log --oneline
d21492f Add the maps settings
c38489a Add the README, trails and notes
$ git show --stat HEAD
commit d21492fac0b4ff3f5f92b7b9ed3ae97b595efd04
Author: Asha <asha@trails.example>
Date:   Fri Nov 13 10:00:00 2026 +0530

    Add the maps settings

 README.md   | 2 ++
 secrets.env | 1 +
 2 files changed, 3 insertions(+)
```

The last commit contains two things: a good README change and the secrets file. Now the working folder:

```text
$ git status --short
 M notes.md
 M trails.md
$ git diff --stat
 notes.md  | 1 +
 trails.md | 7 -------
 2 files changed, 1 insertion(+), 7 deletions(-)
```

`trails.md` lost seven lines (the accident); `notes.md` gained one (the good edit). Neither is committed. Run `git
diff trails.md` to see exactly what was lost. Now you know precisely what to fix, and what to protect.
:::

:::step{type=concept title="Undo tools for work that is only yours"}
Each place a change can be (chapter 2) has its own undo:

| The change is | To undo it | Command |
|---|---|---|
| in the working folder only | throw the edit away, back to the last commit | `git restore file` |
| staged | unstage it, keep the edit | `git restore --staged file` |
| in the last commit | change the last commit | `git commit --amend` |
| in the last few commits | move the branch back, keep the changes | `git reset --soft HEAD~1` |

`HEAD~1` means "the commit before HEAD"; `HEAD~2`, two before.

One command on that list deserves a warning label: **`git restore file` throws your edits away, and they were never
committed, so Git cannot bring them back.** Use it on exactly the files you mean, by name, and look with `git diff`
first. Never run it on a whole folder in a hurry.

`git commit --amend` does not edit a commit (commits never change). It makes a **new** commit that replaces the last
one: whatever is staged now, plus the last commit's changes, with a new message if you give one. The old commit is
dropped from the branch. That is safe only if nobody else has the old commit yet.

:::diagram{name="git-undo-map"}
Each undo command works on one place: the working folder, the staging area, or the last commit.
:::

**Check yourself:** which command throws away an uncommitted edit to `trails.md` for good? (`git restore
trails.md`.)
:::

:::step{type=example title="Worked example: amend, then reset"}
Here are both tools in a scratch repository (only to read). A commit with a typo in its message, and a file
forgotten:

```text
$ git add tips.md
$ git commit -m 'Add a tip abuot water'
[main f5ffbcc] Add a tip abuot water
 1 file changed, 1 insertion(+)
```

"abuot", and `photo-credits.md` should have been in it too. Stage the forgotten file and amend, with a fixed
message:

```text
$ git add photo-credits.md
$ git commit --amend -m 'Add a tip about water, and photo credits'
[main db883ad] Add a tip about water, and photo credits
 Date: Fri Nov 13 15:00:00 2026 +0530
 2 files changed, 2 insertions(+)
 create mode 100644 photo-credits.md
$ git log --oneline
db883ad Add a tip about water, and photo credits
1b19441 Add tips
```

One commit, with both files and the right message; the typo commit `f5ffbcc` is gone from the branch. Note the new
hash: it is a new commit.

Now undo that commit altogether, but keep its changes, with `reset --soft`:

```text
$ git reset --soft HEAD~1
$ git status --short
A  photo-credits.md
M  tips.md
```

The branch moved back one commit; the changes are still there, **staged**, ready to commit differently. `git reset
HEAD` then unstages them (leaving the edits in the files), and `git restore tips.md` finally throws the tips edit away:

```text
$ git reset HEAD
Unstaged changes after reset:
M	tips.md
$ git status --short
 M tips.md
?? photo-credits.md
$ git restore tips.md
$ git status --short
?? photo-credits.md
```

Step by step, from "committed" all the way back to "never happened". Each step was deliberate and visible.
:::

:::step{type=predict title="Guess first"}
:::question
Asha's last commit added `secrets.env`. She runs `git rm secrets.env` and makes a **new** commit "Remove secrets".
Is the key safe now?
:::
- [ ] Yes, the file is deleted
- [x] No: the earlier commit still contains the file, and anyone with the history can read it
- [ ] Only if she pushes
:::explain
Every commit is a complete snapshot. Deleting a file in a later commit leaves it in the earlier one, forever, for
everyone who gets that history. While the commit is unpushed, change it instead with `--amend`. (A key that was ever
pushed must be treated as leaked: change the key itself.)
:::
:::

:::step{type=task task=undo_secret title="Your turn: take the secret out of the last commit"}
Fix the last commit so that it **never contained `secrets.env`**, but still has the README change:

1. Remove the file from Git but keep it on disk: `git rm --cached secrets.env`.
2. Add a `.gitignore` file containing the line `secrets.env`, so it can never be added by accident again, and stage
   it.
3. Replace the last commit with `git commit --amend` (keeping its message is fine).

Then `git show --stat HEAD` should list `README.md` and `.gitignore`, and `ls` should still show `secrets.env` on
disk. Press **Check**.
:::

:::step{type=task task=discard_changes title="Your turn: throw away the accident, keep the good edit"}
`trails.md` was half deleted by accident. Put it back exactly as it is in the last commit, **without** touching
`notes.md`, whose edit is good.

Restore that one file by name. Afterwards `git status --short` should show only ` M notes.md`. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `git reset --soft HEAD~1` do?
:::
- [ ] Deletes the last commit and its changes
- [x] Moves the branch back one commit and keeps that commit's changes staged
- [ ] Unstages every file
:::explain
`--soft` only moves the branch. `--mixed` (the default) also unstages; `--hard` also throws away the changes in your
files, which is the one to be careful with.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
When is it safe to use `git commit --amend`?
:::
- [x] When the last commit has not been pushed or shared
- [ ] Always
- [ ] Only on main
:::explain
Amending replaces a commit with a new one. If others already have the old one, their history and yours now
disagree. Shared mistakes are undone with `git revert` (chapter 7).
:::
:::

:::step{type=deep-dive title="Go deeper: reset in full, and the safety net"}
**The three resets.** `git reset --soft X` moves the branch to commit X and keeps everything staged. `--mixed` (the
default) moves it and unstages, keeping your files. `--hard` moves it and makes your files match X, **throwing
away** uncommitted work. Only `--hard` can lose work that was never committed.

**The safety net for commits.** Commits you moved away from with `reset` or replaced with `--amend` are not deleted
at once. `git reflog` lists every commit HEAD has been on, so you can get them back for weeks (chapter 7 does
exactly that). Uncommitted edits have no such net, which is why committing often is itself a safety habit.

**Leaked secrets in real life.** If a key was ever pushed to a shared server, assume it is stolen: revoke it and make
a new one, then clean the history. Tools such as `git filter-repo` rewrite a whole repository's history, and hosting
services scan pushes for keys. The best fix is prevention: `.gitignore` for secret files from day one (chapter 13).
:::

:::step{type=recap}
You can now:

- diagnose before you act, with `git log`, `git show --stat`, `git status` and `git diff`;
- throw away an uncommitted edit with `git restore file`, and unstage with `git restore --staged`;
- replace the last unpushed commit with `git commit --amend`, and step back commits with `git reset --soft`;
- remove a file from Git but keep it on disk with `git rm --cached`, and keep it out with `.gitignore`.

Next, chapter 7: undoing mistakes that others already have, and finding "lost" commits.

:::photo{src="/lesson-images/git/git-06-notes.webp" alt="Handwritten notes about undoing local work: git restore file: edit gone; git restore --staged: unstage; git commit --amend; git reset --soft HEAD~1; only if not pushed!" ai="true"}
One page of notes for this chapter.
:::
:::
