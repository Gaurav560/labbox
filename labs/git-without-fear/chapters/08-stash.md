:::step{type=story title="Drop everything, but don't lose it"}
Meera is halfway through the Lohagad section on her branch: two lines written, the rest still in her head. Then a
message from Asha: "The README on the live site spells it Sahyadry! Can you fix it right now?"

The fix belongs on main and takes one minute. But Meera's half-written work is sitting uncommitted in `trails.md`.
She does not want to commit broken work ("wip, do not look"), and she must not lose it. And if she just switches to
main, something sneaky happens, which you will see in a moment.

Git has a pocket for exactly this moment: the **stash**. You put your unfinished changes in it, your folder becomes
clean, you do the urgent thing, come back, and take them out again. This chapter also tidies up after yourself with
`git clean`, the command that deletes untracked files, carefully.

:::mission
Ship the urgent spelling fix on main without losing your unfinished work, then clear out the junk files and keep the
one that matters.
:::
:::

:::step{type=try title="What happens if you just switch"}
Look at the state of things on Meera's branch:

```text
$ cd /workspace/08-stash/trails
$ git status
On branch feature/lohagad
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   trails.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	draft.tmp
	ideas.md
	preview/

no changes added to commit (use "git add" and/or "git commit -a")
```

Now try switching to main, and look again:

```text
$ git switch main
Switched to branch 'main'
M	trails.md
$ git status --short
 M trails.md
?? draft.tmp
?? ideas.md
?? preview/
```

Git switched, and **carried the uncommitted change along** to main (`M trails.md`). Uncommitted work belongs to your
folder, not to a branch. If Meera now fixed the README and ran `git commit -a`, her half-written Lohagad section
would go into main with it. (When a switch would overwrite your change, Git refuses instead; either way, it is not
what you want.) Go back with `git switch feature/lohagad` before trying the right way.
:::

:::step{type=concept title="git stash: a pocket for unfinished work"}
`git stash` takes your uncommitted changes (to tracked files, staged or not), saves them in a special place, and
makes your folder match the last commit again. `git stash pop` puts them back and removes them from the stash.

In a scratch repository, with one unfinished line in `tips.md`:

```text
$ git status --short
 M tips.md
$ git stash
Saved working directory and index state WIP on feature/gear: a00c60b Add tips
$ git status --short
$ git stash list
stash@{0}: WIP on feature/gear: a00c60b Add tips
```

After `git stash`, the folder is clean ("WIP" means work in progress), and `git stash list` shows one entry,
`stash@{0}`, remembering the branch and commit it came from. You can now switch anywhere safely. Back on the branch:

```text
$ git stash pop
On branch feature/gear
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   tips.md

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (7687ac6710326d2caba305c6f1e64c036c98d6d2)
```

The change is back, exactly as it was, and the stash entry is dropped. The stash is a stack: several stashes pile up
as `stash@{0}`, `stash@{1}` and so on, newest first. `git stash list` shows them; `git stash show -p` shows what is
in the newest.

:::diagram{name="git-stash"}
stash moves your changes into a pocket and cleans the folder; pop puts them back.
:::

Two things a plain `git stash` does **not** take: untracked files (add `-u` for those) and ignored files. Here,
`draft.tmp`, `ideas.md` and `preview/` would stay in the folder, which is fine, since they exist on every branch.
:::

:::step{type=predict title="Guess first"}
:::question
You stash, switch to main, commit a fix, switch back, and forget to pop. Where is your unfinished work?
:::
- [ ] Lost, because you switched branches
- [x] Still in the stash: `git stash list` shows it, and `git stash pop` brings it back
- [ ] It was committed with the fix
:::explain
The stash keeps it until you pop or drop it. A forgotten stash is a common surprise, so make `git stash list` part of
your routine when you come back to a branch.
:::
:::

:::step{type=task task=stash_work title="Your turn: the urgent fix"}
On `feature/lohagad`, with the Lohagad lines unfinished:

1. Stash your changes.
2. Switch to `main`, change `Sahyadry` to `Sahyadri` in `README.md`, and commit the fix.
3. Switch back to `feature/lohagad` and pop the stash.

At the end you should be on `feature/lohagad`, `git diff` should show your Lohagad lines again, `git stash list`
should be empty, and `git log --oneline main -1` should show the fix. Press **Check**.
:::

:::step{type=concept title="git clean: deleting untracked files, carefully"}
Untracked files pile up: previews, temporary files, experiments. `git clean` deletes untracked files. It is one of
the very few Git commands that destroys work **with no way back**: these files were never committed, so neither the
reflog nor anything else remembers them. So it refuses to run unless you say `-f` (force), and it has a dry run, `-n`,
that only **shows** what it would delete. Here is the dry run in this chapter's repository:

```text
$ git clean -n
Would remove draft.tmp
Would remove ideas.md
$ git clean -n -d
Would remove draft.tmp
Would remove ideas.md
Would remove preview/
```

`-d` includes untracked folders. And look: `ideas.md` is on the list. Meera's ideas file has never been committed,
so to Git it is just another untracked file. A careless `git clean -fd` would delete it along with the junk.

Two safe ways to clean only what you mean:

- Name the paths: `git clean -f -d preview draft.tmp` deletes just those.
- Use interactive mode, `git clean -i`, which shows the list and lets you choose.

The habit: **always run `git clean -n` first, and read the list.**
:::

:::step{type=task task=clean_untracked title="Your turn: remove the junk, keep the idea"}
In this chapter's repository, delete the untracked junk, `preview/` and `draft.tmp`, and **keep** `ideas.md`.

Run the dry run first and read it. Afterwards `ls` should show `ideas.md` and no `preview` or `draft.tmp`. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which of these can `git reflog` help you recover?
:::
- [x] A commit you moved away from with `git reset --hard`
- [ ] A file deleted with `git clean -f`
- [ ] An edit thrown away with `git restore`
:::explain
The reflog remembers commits. Untracked files and uncommitted edits were never in a commit, so once deleted they are
gone. That is why `clean` and `restore` deserve care, and why committing often is a safety habit.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You have changes in a tracked file **and** a new untracked file you want to stash too. What do you run?
:::
- [ ] `git stash`
- [x] `git stash -u`
- [ ] `git stash list`
:::explain
Plain `git stash` leaves untracked files in the folder. `-u` (include untracked) takes them too.
:::
:::

:::step{type=deep-dive title="Go deeper: named stashes, and a better way to multitask"}
**Name your stashes.** `git stash push -m "half of Lohagad"` gives the entry a message, which helps when there are
several. `git stash apply stash@{1}` applies one without dropping it; `git stash drop stash@{1}` deletes one.

**A stash can conflict.** If the branch changed the same lines while your work was stashed, `pop` stops with a
conflict, exactly like a merge (chapter 5). Resolve it, and drop the stash yourself afterwards.

**Worktrees: two branches at once.** `git worktree add ../trails-main main` checks main out into a second folder,
sharing the same repository. You can fix main there while your branch stays untouched here. For long interruptions,
it is cleaner than stashing.

**Or just commit.** Many experienced engineers simply commit unfinished work as "wip" on their own branch, and tidy
it into proper commits before sharing (chapter 11 shows how). A commit is safer than a stash: it is in the reflog.
:::

:::step{type=recap}
You can now:

- explain why switching branches carries uncommitted changes with you;
- put unfinished work aside with `git stash`, see it with `git stash list`, and bring it back with `git stash pop`;
- preview with `git clean -n`, and delete only the untracked files you mean;
- tell what the reflog can and cannot recover.

That completes Part 2. Next, Part 3 starts with chapter 9: working with a server, push and pull.

:::photo{src="/lesson-images/git/git-08-notes.webp" alt="Handwritten notes about stash and clean: git stash: put work aside; git stash pop: bring it back; git stash -u for new files; git clean -n first!; clean cannot be undone" ai="true"}
One page of notes for this chapter.
:::
:::
