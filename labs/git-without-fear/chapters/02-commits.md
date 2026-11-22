:::step{type=story title="One commit, one idea"}
Imagine opening Trails' history a year from now to find out when the safety rules changed. You find one commit
called "updates", which changed nine files: the rules, three trails, the README, a typo, and someone's private
notes. Which line was the rules change? Why was it made? Can you undo just that, without undoing the rest?

You can't, easily. Good history is made of **small commits that each do one thing**, with a message that says
what and why. Then history reads like a diary, `git revert` can undo exactly one idea (chapter 7), and a reviewer can
understand each step.

This chapter teaches the daily routine that makes that possible: look at what changed, choose what goes into the
next commit, and commit it with a message worth reading.

:::mission
Commit the new safety rules on their own, then commit one changed file while leaving another out.
:::
:::

:::step{type=concept title="Three places a change can be"}
At any moment, a change in your repository is in one of three places:

| Place | What it is | How a change gets there |
|---|---|---|
| **Working folder** | the files as they are on disk now | you edit, create or delete a file |
| **Staging area** (also called the index) | what will go into the next commit | `git add file` |
| **History** | the commits | `git commit` |

`git status` shows all three at once. Open the Trails repository for this chapter and run it:

```text
$ cd /workspace/02-commits/trails
$ git status
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   notes.txt
	modified:   trails.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	rules.md

no changes added to commit (use "git add" and/or "git commit -a")
```

Three kinds of change: two files Git knows are **modified** but not staged, and one file it has never seen,
**untracked**. Nothing is staged, so a commit now would save nothing. Notice how `git status` even tells you the
command for each next step: it is a helpful command, read it often.

:::diagram{name="git-three-areas"}
git add moves a change from the working folder to the staging area; git commit moves everything staged into history.
:::
:::

:::step{type=try title="See exactly what changed"}
`git status` says **which** files changed. `git diff` says **how**, line by line:

```text
$ git diff
diff --git a/notes.txt b/notes.txt
index 0b5d883..bf9dd3f 100644
--- a/notes.txt
+++ b/notes.txt
@@ -1,2 +1,3 @@
 Ideas for later:
 - a map page
+- ask Ravi about the night trek
diff --git a/trails.md b/trails.md
index 1adbb97..cc0d4d1 100644
--- a/trails.md
+++ b/trails.md
@@ -9,3 +9,8 @@
 - Distance: 6 km
 - Difficulty: hard
 - Best season: October to February
+
+## Harishchandragad
+- Distance: 14 km
+- Difficulty: hard
+- Best season: September to February
```

How to read a diff:

- `--- a/` is the version in Git, `+++ b/` the version in your folder.
- `@@ -9,3 +9,8 @@` says where: from line 9, three lines became eight.
- Lines starting with `+` were added, `-` removed, and a space means unchanged context around them.

So `trails.md` gained a whole new trail, Harishchandragad, and `notes.txt` gained one private scratch line. Those
are two very different changes. They do not belong in the same commit; the scratch line probably belongs in no
commit at all.

`git diff` with no options shows **unstaged** changes. Once you stage something, `git diff --staged` shows what the
next commit will contain. Run both before every commit and you will never commit a surprise.
:::

:::step{type=example title="Worked example: two changes, two commits"}
Here are two unrelated changes made in a scratch copy of this repository (only to read): a new contact page, and a
reworded line in the README. Each gets its own commit:

```text
$ git add contact.md
$ git commit -m 'Add a contact page'
[main bf6b927] Add a contact page
 1 file changed, 1 insertion(+)
 create mode 100644 contact.md
$ git add README.md
$ git commit -m 'Say who writes Trails'
[main 204005f] Say who writes Trails
 1 file changed, 1 insertion(+), 1 deletion(-)
$ git log --oneline
204005f Say who writes Trails
bf6b927 Add a contact page
0819462 Add Rajmachi and Kalsubai
cab50c3 Add the README and a notes file
```

1. `git add contact.md` stages only that file, by name.
2. The first commit contains only the contact page.
3. Then the README, staged and committed on its own.
4. `git log --oneline` shows one line per commit, newest first: the history now reads like a list of ideas.

Everything not added (here, the other changed files) stayed out of both commits. That is the whole point of the
staging area.

**Messages that help.** Write the message as a short instruction, in the present tense, saying what the commit does:
"Add a contact page", "Fix Kalsubai's season", "Remove the old map". If it needs a reason, add it: "Fix
Kalsubai's season: the forest department changed it". Avoid "update", "changes" and "stuff".
:::

:::step{type=predict title="Guess first"}
:::question
`git status` shows `rules.md` as **untracked** and `trails.md` as **modified**. You run `git commit -a -m "..."`
(the `-a` option stages every modified tracked file for you). Which files are committed?
:::
- [ ] Both
- [x] Only trails.md: -a only picks up files Git already tracks
- [ ] Only rules.md
:::explain
`-a` is a shortcut for "add every **modified tracked** file". A brand new file is untracked, so it is left out. Many
people have been surprised by a missing new file this way; `git add` by name is always clear.
:::
:::

:::step{type=task task=commit_hours title="Your turn: commit the safety rules"}
Asha wrote three safety rules in a new file, `rules.md`. Commit **only that file**, with a message that mentions the
safety rules.

Use `git status` before and after, and `git log --oneline` to see your commit on top. Press **Check**.
:::

:::step{type=concept title="Staging part of your work, and unstaging"}
Now the other two changes. The new trail in `trails.md` is ready for a commit. The scratch line in `notes.txt` is
not: it is a private reminder. The staging area lets you commit one and not the other: stage `trails.md` by name,
and leave `notes.txt` alone.

If you stage something by mistake, you can take it back out of the staging area without losing the change:

```text
$ git add trails.md
$ git status
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   trails.md

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   notes.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	rules.md

$ git restore --staged trails.md
$ git status --short
 M notes.txt
 M trails.md
?? rules.md
```

`git restore --staged file` **unstages**: the file goes back to "modified, not staged", and your edits stay in the
file. `git status --short` is the compact view: a letter in the first column means staged, in the second column
means not staged, and `??` means untracked.

Avoid `git add .` (which stages everything in the folder) until you have looked at `git status`. It is the most
common way private notes, passwords and junk end up in history.
:::

:::step{type=task task=stage_part title="Your turn: commit the trail, not the notes"}
Commit the new **Harishchandragad** trail in `trails.md`, with a message about it. **Do not** commit `notes.txt`:
its scratch line must stay in your folder, changed but uncommitted.

Afterwards, `git status --short` should still show ` M notes.txt`, and `git show --stat` should list only
`trails.md`. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You staged `notes.txt` by mistake. Which command takes it out of the staging area and keeps your edit?
:::
- [ ] `git rm notes.txt`
- [x] `git restore --staged notes.txt`
- [ ] `git restore notes.txt`
:::explain
`--staged` means "unstage". Plain `git restore notes.txt` would throw away the edit itself (chapter 6), and `git rm`
deletes the file.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which is the most useful commit message?
:::
- [ ] `update`
- [ ] `changes to trails.md`
- [x] `Add Harishchandragad`
:::explain
A good message says what the commit does, so the history reads as a list of ideas. The file name is already in the
commit; the message should add meaning.
:::
:::

:::step{type=deep-dive title="Go deeper: partial staging, and amending the last message"}
**Stage part of a file.** `git add -p trails.md` walks through each changed block ("hunk") and asks whether to stage
it: `y` yes, `n` no, `s` split it smaller. With it, two unrelated edits in the **same** file can still become two
commits.

**Fix the last message.** `git commit --amend -m "Better message"` replaces the last commit with one that has a new
message (and anything newly staged). Only do it before you share the commit: chapter 6 explains why.

**Longer messages.** `git commit` without `-m` opens an editor (nano in this lab). The first line is the summary,
under about 50 characters; then a blank line; then as much explanation as the change deserves. Many teams' tools
show only the first line, so make it count.

**Empty folders.** Git tracks files, not folders, so an empty folder never appears in a commit. Teams put a small
`.gitkeep` file in a folder they want to keep.
:::

:::step{type=recap}
You can now:

- tell the working folder, the staging area and the history apart, and read `git status` and its short form;
- see exactly what changed with `git diff`, and what you are about to commit with `git diff --staged`;
- make one commit per idea by staging files by name, and unstage with `git restore --staged`;
- write a commit message that says what the commit does.

Next, chapter 3: reading history, to find out who changed what, and when.

:::photo{src="/lesson-images/git/git-02-notes.webp" alt="Handwritten notes about commits: working folder, staging, history; git status: read it often; git diff, git diff --staged; one commit = one idea; git add file, not git add ." ai="true"}
One page of notes for this chapter.
:::
:::
