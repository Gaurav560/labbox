:::step{type=story title="wip, wip again, done"}
Meera finished the Sinhagad trail on her branch. Her commits tell the story of her afternoon: "wip", "wip again",
"done Sinhagad". Meanwhile two commits landed on main. If she merges now, main's history gains three meaningless
messages and a merge commit, for what is really one small idea: "Add Sinhagad".

Many teams want history that reads like a clean list of ideas, not a diary of someone's afternoon. Git's tool for
that is **rebase**: it takes your commits and **replays** them on top of another commit, so your branch starts from
the latest main, and it can combine or reword commits on the way.

Rebase is powerful, and it comes with one rule you must never break, because it **rewrites** commits. This chapter
teaches both: how to make history clean, and when you must not.

:::mission
Move Meera's branch onto the latest main, and turn her three commits into one clear commit.
:::
:::

:::step{type=concept title="Rebase: replay your commits somewhere else"}
Here is this chapter's repository. The branch started from the first commit; main has moved on twice since:

```text
$ cd /workspace/11-rebase/trails
$ git log --oneline --graph --all --decorate
* 181b8a1 (main) Say where the Sahyadri are
* 5afa288 Add trekking tips
| * 42a80bb (HEAD -> feature/sinhagad) done Sinhagad
| * d9bacb6 wip again
| * 166e142 wip
|/
* dd0d29b Add the README and two trails
```

There are two ways to bring these lines together:

- **Merge** (chapter 4) keeps both lines exactly as they happened, and joins them with a merge commit.
- **Rebase** takes the branch's commits, sets them aside, moves the branch to the tip of main, and **replays** each
  commit on top, one by one, as **new** commits. The result looks as if Meera had started her work after main's two
  commits. History becomes one straight line.

The commits after a rebase have the same changes and messages, but **new hashes**: they have new parents, so they are
different commits. The old ones are left behind (and remembered by the reflog, chapter 7).

:::diagram{name="git-rebase"}
Rebase replays the branch's commits, as new commits, on top of the latest main: one straight line.
:::

That leads to **the golden rule of rebase: never rebase commits that others already have.** On your own unpushed
branch, rebase freely. On shared commits, it causes the same trouble as any rewrite of shared history (chapter 7).

**Check yourself:** after a rebase, are the replayed commits the same commits as before? (No: same changes, new
hashes, because their parent changed.)
:::

:::step{type=example title="Worked example: rebase, then squash"}
Here is a different branch, `feature/torna`, with two commits, rebased in a scratch copy (only to read):

```text
$ git log --oneline --graph --all --decorate
* 2bf1fc1 (HEAD -> feature/torna) fix
* 01203e8 Add Torna heading
| * 181b8a1 (main) Say where the Sahyadri are
| * 5afa288 Add trekking tips
|/
* dd0d29b Add the README and two trails
$ git rebase main
Successfully rebased and updated refs/heads/feature/torna.
$ git log --oneline --graph --all --decorate
* 2b9beba (HEAD -> feature/torna) fix
* 0be0617 Add Torna heading
* 181b8a1 (main) Say where the Sahyadri are
* 5afa288 Add trekking tips
* dd0d29b Add the README and two trails
```

(While it works, `git rebase` also prints "Rebasing (1/2)" and "Rebasing (2/2)" as it replays each commit.) One
straight line: the two commits now sit on top of main, with new hashes (`01203e8` became `0be0617`).

Now the messages. "fix" means nothing to a reader; the two commits are one idea. **Squashing** combines commits into
one. The simplest way: move the branch back to main with `reset --soft` (chapter 6), which keeps all the changes
staged, and commit them once:

```text
$ git reset --soft main
$ git status --short
M  trails.md
$ git commit -qm 'Add Torna' && git log --oneline --graph --all --decorate
* daa6bb2 (HEAD -> feature/torna) Add Torna
* 181b8a1 (main) Say where the Sahyadri are
* 5afa288 Add trekking tips
* dd0d29b Add the README and two trails
```

One commit, one idea, one clear message, on top of the latest main. Merged into main, it will be a fast-forward with
no merge commit at all.
:::

:::step{type=predict title="Guess first"}
:::question
You rebased your branch and had already pushed it once before. What happens when you `git push` now?
:::
- [ ] It pushes normally
- [x] It is rejected: the server's branch has the old commits, which your rebased branch no longer contains
- [ ] Git merges the two automatically
:::explain
Rebased commits are new commits, so your branch and the server's have diverged. Only if the branch is yours alone may
you replace it, with `git push --force-with-lease`. On shared branches, do not rebase.
:::
:::

:::step{type=task task=rebase_branch title="Your turn: Sinhagad on top of the latest main"}
On `feature/sinhagad`, rebase the branch onto `main`. Then look at `git log --oneline --graph --all --decorate`: one
straight line, with the three Sinhagad commits on top of main's two new commits. Press **Check**.
:::

:::step{type=concept title="Interactive rebase: edit history like a list"}
`git rebase -i main` (interactive) does not replay at once. It first opens a **todo list** of your commits in the
editor, and you tell it what to do with each. For the Torna branch, it looked like this:

```text
pick 0be0617 Add Torna heading
pick 2b9beba fix

# Rebase 181b8a1..2b9beba onto 181b8a1 (2 commands)
#
# Commands:
# p, pick <commit> = use commit
# r, reword <commit> = use commit, but edit the commit message
# e, edit <commit> = use commit, but stop for amending
# s, squash <commit> = use commit, but meld into previous commit
# f, fixup [-C | -c] <commit> = like "squash" but keep only the previous
#                    commit's log message, unless -C is used, in which case
```

Each line is a commit, oldest first. Change the word at the start, save, and close the editor:

- `pick` keeps the commit as it is.
- `reword` keeps it but lets you change its message.
- `squash` (or `s`) melds it into the commit above and lets you write the combined message.
- `fixup` (or `f`) melds it into the commit above and keeps only that commit's message.
- Deleting a line drops that commit entirely.

To turn three commits into one, keep `pick` on the first, change the other two to `squash`, save, then write the
final message when the editor opens again. In this lab the editor is nano: save with **Ctrl+O** and Enter, quit with
**Ctrl+X**. If anything goes wrong mid-way, `git rebase --abort` puts everything back.

`git reset --soft main` then one commit, as in the worked example, gives the same result when you want **all** the
branch's commits combined. Interactive rebase is for finer work: keep some, combine others, reword one.
:::

:::step{type=task task=squash_commits title="Your turn: three wip commits become one"}
Turn Meera's three commits on `feature/sinhagad` into **one** commit with a clear message, such as `Add Sinhagad`.
Use either way: `git rebase -i main` with `squash`, or `git reset --soft main` followed by one commit.

`git log --oneline main..feature/sinhagad` should show exactly one commit, and `trails.md` should still have the
whole Sinhagad section. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which branch is safe to rebase?
:::
- [x] Your own feature branch that nobody else has pulled
- [ ] main, after it was pushed
- [ ] A branch two teammates are working on
:::explain
The golden rule: rebase only commits that are yours alone. Shared history gets merges and reverts.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In an interactive rebase todo list, what does changing `pick` to `fixup` do?
:::
- [ ] Deletes the commit
- [x] Melds the commit into the one above it, keeping only the message of the one above
- [ ] Opens the commit for editing
:::explain
`fixup` is squash without asking for a message: perfect for "fix typo" commits that belong to the previous one.
:::
:::

:::step{type=deep-dive title="Go deeper: merge or rebase, and conflicts during a rebase"}
**Which should a team use?** Merging keeps the true history, with every branch and merge visible; it never rewrites
anything, so it is always safe. Rebasing gives a clean, linear history that is easier to read and to search with
`git bisect`, at the cost of rewriting your own commits. A common compromise: rebase your own branch onto main while
you work (and squash wip commits), then merge it into main through a pull request.

**Conflicts while rebasing.** Each replayed commit can conflict, like a small merge. Rebase stops, you resolve the
file as in chapter 5, `git add` it, and run `git rebase --continue`. `git rebase --skip` drops that commit;
`git rebase --abort` gives up and restores the branch.

**Autosquash.** Commit a fix with `git commit --fixup=HASH`, and later `git rebase -i --autosquash main` puts each
fixup next to its target already marked `fixup`. Reviewers love it.

**pull --rebase.** `git pull --rebase` replays your unpushed commits on top of what you just fetched, instead of
making a merge commit, which avoids the "Merge branch 'main' of ..." commits you saw in chapter 9.
:::

:::step{type=recap}
You can now:

- explain rebase: your commits replayed as new commits on top of another branch;
- follow the golden rule: never rebase commits that others already have;
- rebase a branch onto main, and squash several commits into one with `reset --soft` or `rebase -i`;
- read an interactive rebase todo list: pick, reword, squash, fixup, drop.

Next, chapter 12: what is really inside `.git`.

:::photo{src="/lesson-images/git/git-11-notes.webp" alt="Handwritten notes about rebase: replay commits on the new main; new commits, new hashes; never rebase shared commits!; git rebase -i: squash, reword; git reset --soft main + commit" ai="true"}
One page of notes for this chapter.
:::
:::
