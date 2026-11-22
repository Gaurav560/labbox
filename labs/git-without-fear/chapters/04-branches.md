:::step{type=story title="Work on something new without breaking the site"}
Meera wants to add a page about monsoon treks. It will take her a week: some days the page will be half written,
with broken sentences and missing links. Meanwhile Asha keeps fixing typos on the live site, and Ravi adds trails.

If Meera works directly on the version everyone uses, the site shows her half-written page all week. If she works
in a private copy of the folder, putting her work back together with everyone else's at the end is painful.

Git's answer is the **branch**: a separate line of work inside the same repository. Meera's page grows on its own
branch, invisible to everyone else, while the main line carries on. When the page is ready, one command brings it
in. Branches are the heart of how every software team works, and in Git they cost almost nothing.

In 1837 Charles Darwin drew this little tree in his notebook, under the words "I think": one line splitting into branches that each go their own way. A Git history drawn with --graph looks surprisingly like it.

:::photo{src="/lesson-images/git/darwin-tree.webp" alt="A small ink sketch of a branching tree with lettered branch tips, and the words I think written above it" credit="Charles Darwin" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Darwins_first_tree.jpg"}
Darwin's first tree sketch, 1837.
:::

:::mission
Build the monsoon page on its own branch, then merge it into main.
:::
:::

:::step{type=concept title="A branch is just a name for a commit"}
Here is the surprising truth that makes branches easy: **a branch is only a label pointing at a commit**. It does
not copy any files. You can see it for yourself: in this chapter's repository, `main` is a tiny file in `.git`
holding one commit hash.

```text
$ cd /workspace/04-branches/trails
$ git branch
* main
```

`git branch` lists the branches; the `*` marks the one you are on. Making a new one and moving onto it is one
command:

```text
$ git switch -c feature/lohagad
Switched to a new branch 'feature/lohagad'
```

`git switch` moves you to a branch; `-c` creates it first. (Older tutorials use `git checkout -b`, which does the
same thing.) The name `feature/...` is just a habit many teams follow; the slash has no special meaning.

When you commit on a branch, **that branch's label moves forward** to the new commit. The other branches stay where
they were. One more name to know: **HEAD** means "where I am now": it normally points at the branch you are on.

:::diagram{name="git-branch-pointer"}
A branch is a label on a commit; committing moves the label of the branch you are on, and HEAD follows you.
:::

**Check yourself:** you make a branch and then make no commits on it. How many copies of your files exist? (Still
one. The new branch is just a second label on the same commit.)
:::

:::step{type=example title="Worked example: a branch, a commit, a merge"}
Here is the whole life of a small branch, Lohagad, in a scratch copy (only to read; your task uses another name).
After `git switch -c feature/lohagad`, one commit is made on the branch, and the history shows two labels:

```text
$ git log --oneline --graph --all --decorate
* a45b8d4 (HEAD -> feature/lohagad) Add Lohagad
* ad08525 (main) Add Rajmachi and Kalsubai
* 46beb8c Add the README
```

`HEAD -> feature/lohagad`: you are on the branch, which points at the new commit. `main` still points one commit
behind. Now switch back to main, and look for Lohagad in the file:

```text
$ git switch main
Switched to branch 'main'
$ grep -c Lohagad trails.md
0
```

Zero: on main, the file is exactly as main left it. Switching branches rewrites your working folder to match the
branch. Your work is not lost; it is on the other branch. To bring it in, **merge** it into the branch you are on:

```text
$ git merge feature/lohagad
Updating ad08525..a45b8d4
Fast-forward
 trails.md | 3 +++
 1 file changed, 3 insertions(+)
$ git log --oneline --graph --all --decorate
* a45b8d4 (HEAD -> main, feature/lohagad) Add Lohagad
* ad08525 Add Rajmachi and Kalsubai
* 46beb8c Add the README
```

**Fast-forward** means main had not moved since the branch started, so Git simply slid the `main` label forward to
the branch's commit. No new commit was needed; both labels now point at `a45b8d4`.

The rule to remember: **you merge another branch INTO the branch you are on.** Always switch to the receiving
branch first.
:::

:::step{type=predict title="Guess first"}
:::question
You are on `feature/monsoon` and run `git merge main`. What happens?
:::
- [ ] main receives the monsoon work
- [x] feature/monsoon receives whatever is new on main; main does not change
- [ ] Git refuses: you can only merge into main
:::explain
A merge always changes the branch you are on. Merging main into your feature branch is a common way to catch up with
others' work, but to publish your work you switch to main and merge the feature into it.
:::
:::

:::step{type=task task=combo_branch title="Your turn: a branch for the monsoon page"}
In `/workspace/04-branches/trails`:

1. Make a branch called `feature/monsoon` and move onto it.
2. Create `monsoon.md` containing exactly this line:
   `Monsoon treks: carry a raincoat and check the forecast`
3. Add and commit it **on the branch**.

`git log --oneline --graph --all --decorate` should show your branch one commit ahead of main. Press **Check**.
:::

:::step{type=concept title="When both sides moved: a merge commit"}
A fast-forward only works when the receiving branch has not moved. Usually it has: while Meera worked on her branch,
Asha committed to main. Then history has **forked**, and Git makes a **merge commit**: a commit with **two
parents**, joining both lines.

Here it is in the scratch copy: a `feature/tips` branch with one commit, while main got a commit of its own:

```text
$ git log --oneline --graph --all --decorate
* c704507 (feature/tips) Add tips
| * 05b838c (HEAD -> main) Reword the README
|/
* a45b8d4 (feature/lohagad) Add Lohagad
* ad08525 Add Rajmachi and Kalsubai
* 46beb8c Add the README
```

Two lines, starting from the same commit. Merge tips into main:

```text
$ git merge --no-edit feature/tips
Merge made by the 'ort' strategy.
 tips.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 tips.md
$ git log --oneline --graph --all --decorate
*   44ffb0a (HEAD -> main) Merge branch 'feature/tips'
|\
| * c704507 (feature/tips) Add tips
* | 05b838c Reword the README
|/
* a45b8d4 (feature/lohagad) Add Lohagad
* ad08525 Add Rajmachi and Kalsubai
* 46beb8c Add the README
```

The new commit `44ffb0a` joins both lines. Git combined the two sides by itself, because they changed different
files ("ort" is the name of Git's merge method). `--no-edit` accepted the default message; without it, Git opens
the editor so you can write one.

A merged branch can be deleted; its commits stay in history: `git branch -d feature/tips` answered
`Deleted branch feature/tips (was c704507).` `-d` refuses to delete a branch whose work is not merged yet, which
protects you.

:::diagram{name="git-merge"}
A fast-forward slides the label; when both sides moved, a merge commit with two parents joins them.
:::
:::

:::step{type=task task=merge_combo title="Your turn: merge the monsoon page"}
Bring the monsoon page into `main`: switch to main, and merge `feature/monsoon` into it.

Afterwards, `ls` on main should show `monsoon.md`, and `git log --oneline --graph --all --decorate` should show main
at the monsoon commit. Was your merge a fast-forward? Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does a branch contain?
:::
- [ ] A full copy of every file
- [x] Just the hash of one commit; the files come from that commit and its history
- [ ] The list of changes since main
:::explain
`cat .git/refs/heads/main` prints one hash, here `44ffb0a7a2...`. That is all a branch is, which is why making one
is instant, even in a huge repository.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
When does `git merge` make a fast-forward instead of a merge commit?
:::
- [x] When the branch you are on has not moved since the other branch started
- [ ] When the branches changed different files
- [ ] Always, on main
:::explain
If nothing new happened on the receiving branch, there is nothing to join: Git just moves its label forward. When
both sides have new commits, it needs a merge commit.
:::
:::

:::step{type=deep-dive title="Go deeper: HEAD, detached HEAD, and branch habits"}
**HEAD is a file too.** `cat .git/HEAD` answers `ref: refs/heads/main`: HEAD points at a branch, which points at a
commit. When you commit, Git moves the branch HEAD points at.

**Detached HEAD.** `git switch --detach a45b8d4` (or `git checkout a45b8d4`) puts HEAD on a commit directly, not on a
branch. You can look around and even commit, but those commits belong to no branch, and switching away leaves them
behind (chapter 7 shows how to find them again). To keep work from there, make a branch: `git switch -c name`.

**Habits that keep teams calm.** Keep branches short-lived (days, not months), so merges stay small. Name them for
what they do (`feature/monsoon`, `fix/kalsubai-season`). Merge main into a long branch now and then, so the final
merge holds no surprises. Many teams never commit straight to main at all: every change arrives through a reviewed
branch (chapter 10).
:::

:::step{type=recap}
You can now:

- explain that a branch is a label on a commit, and HEAD is where you are;
- make a branch and move onto it with `git switch -c`, and move between branches with `git switch`;
- merge a branch into the one you are on, and tell a fast-forward from a merge commit;
- read `git log --oneline --graph --all --decorate`, and delete a merged branch with `git branch -d`.

Next, chapter 5: what happens when two branches change the same line.

:::photo{src="/lesson-images/git/git-04-notes.webp" alt="Handwritten notes about branches: a branch = a label on a commit; git switch -c feature/x; merge INTO the branch you are on; fast-forward or merge commit; git branch -d when merged" ai="true"}
One page of notes for this chapter.
:::
:::
