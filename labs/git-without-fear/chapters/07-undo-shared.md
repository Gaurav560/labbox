:::step{type=story title="A mistake everyone already has"}
Yesterday Ravi committed "Make Kalsubai easy" and pushed it to the server. Kalsubai is the highest peak in
Maharashtra, and the climb is hard; a beginner who trusts the site could get into real trouble. And by now Asha and
Meera have pulled the server's history: the bad commit is on three machines.

Chapter 6's tools rewrite history. Here they would be a disaster: if Ravi amended or reset the pushed commit and
forced the server to accept it, everyone else's history would no longer match the server's, and the next pull would
tangle the team in confusing merges. Shared history is like a published newspaper: you do not secretly reprint
yesterday's edition; you print a **correction**.

Git's correction is `git revert`: a **new** commit that does the opposite of an old one. And this chapter has a
second gift: the **reflog**, Git's private diary, which can bring back commits you thought you had destroyed.

:::mission
Undo the pushed Kalsubai mistake with a new commit and push it, then rescue a commit that a hard reset threw away.
:::
:::

:::step{type=concept title="Rewrite or add? The one rule"}
How do you know whether a commit is shared? Compare your branch with what the server has. In this chapter's
repository, `origin/main` is your copy of the server's main (chapter 9 explains it fully):

```text
$ cd /workspace/07-undo-shared/trails
$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
$ git log --oneline origin/main
4c1184b Add trekking tips
bd200d6 Make Kalsubai easy
0c20db6 Add the README and two trails
```

All three commits are on the server. So the rule applies:

| The commit is | Undo it with | Because |
|---|---|---|
| only on your machine | `--amend`, `reset` (chapter 6) | nobody else has it, so rewriting harms nobody |
| pushed, shared | `git revert` | it adds a commit; everyone's history stays the same, plus the fix |

`git revert X` looks at what commit X changed, makes the **opposite** change, and commits it with the message
`Revert "..."` and a line saying which commit it undoes. History stays honest: the mistake, then its correction, both
visible, with reasons.

**Check yourself:** a commit you made ten minutes ago, not pushed, has a wrong message. Amend or revert? (Amend: it
is only yours.)
:::

:::step{type=example title="Worked example: reverting a pushed commit"}
Here a team decides to take the tips page back out, in a scratch clone (only to read; your task reverts a different
commit). The commit to undo is `4c1184b Add trekking tips`:

```text
$ git revert --no-edit 4c1184b
[main 5fe9a02] Revert "Add trekking tips"
 Date: Sun Nov 15 15:00:00 2026 +0530
 1 file changed, 1 deletion(-)
 delete mode 100644 tips.md
$ git log --oneline
5fe9a02 Revert "Add trekking tips"
4c1184b Add trekking tips
bd200d6 Make Kalsubai easy
0c20db6 Add the README and two trails
```

1. `git revert` takes the hash of the commit to undo; `--no-edit` keeps the default message (without it, Git opens
   the editor so you can add the reason).
2. The original commit is still there, unchanged. A new commit on top undoes it: `tips.md`, which it added, is
   deleted.
3. The full message even names the undone commit: `This reverts commit 4c1184b7451eb19b63fb7d3ec98885605e759841.`

A revert is an ordinary new commit, so you share it the ordinary way:

```text
$ git push
To /workspace/07-undo-shared/server/trails.git
   4c1184b..5fe9a02  main -> main
```

Everyone who pulls now gets the correction on top of what they already have. No surprises, no tangles.
:::

:::step{type=predict title="Guess first"}
:::question
You revert a commit that changed one line in `trails.md`. Later commits changed other lines of the same file. What
does the revert undo?
:::
- [ ] The whole file goes back to how it was before that commit
- [x] Only that commit's change; the later changes stay
- [ ] Every commit after it
:::explain
A revert undoes exactly one commit's changes, as a new change on top of today's files. Everything else stays. (If a
later commit changed the very same lines, the revert can conflict, and you resolve it as in chapter 5.)
:::
:::

:::step{type=task task=revert_bad title="Your turn: undo the Kalsubai mistake"}
Undo Ravi's pushed commit **"Make Kalsubai easy"** the shared-history way:

1. Find its short hash with `git log --oneline`.
2. Revert it, keeping the default message.
3. Check that Kalsubai is `- Difficulty: hard` again in `trails.md`.
4. Push, so everyone gets the correction.

Do not use `reset` or `--amend` here: the commit is already on the server. Press **Check**.
:::

:::step{type=concept title="The reflog: nothing is ever really lost"}
Asha had a scary moment yesterday. She committed a new trail, Visapur, then mistyped a command and ran `git reset
--hard HEAD~1`. The branch jumped back one commit, the Visapur commit vanished from `git log`, and so did the
section from `trails.md`. Is it gone?

No. A reset only moves a branch label; the commit itself is still in the repository. Git also keeps a diary of
**every place HEAD has been**, called the **reflog** (reference log). Here is the same accident in a scratch repo:

```text
$ git reflog | head -4
5fe9a02 HEAD@{0}: reset: moving to HEAD~1
50d7b19 HEAD@{1}: commit: Add a draft page
5fe9a02 HEAD@{2}: revert: Revert "Add trekking tips"
4c1184b HEAD@{3}: clone: from /workspace/07-undo-shared/server/trails.git
```

Read it from the top: the newest entry is the reset; just before it, HEAD was on `50d7b19`, the commit "Add a draft
page", the one that disappeared. `HEAD@{1}` means "where HEAD was one move ago". Give it a branch, and it is back:

```text
$ git branch saved HEAD@{1}
$ git log --oneline saved -1
50d7b19 Add a draft page
```

`git branch NAME COMMIT` makes a branch pointing at any commit you name: a hash, or a reflog position. The "lost"
commit is safe again, on its own branch, ready to merge.

The reflog is private to your repository (it is not pushed), and Git keeps its entries for about 90 days. It cannot
save edits that were never committed: one more reason to commit small and often.

:::diagram{name="git-reflog"}
A reset moves the branch label back; the commit is still there, and the reflog remembers where HEAD has been.
:::
:::

:::step{type=task task=rescue_commit title="Your turn: rescue Visapur"}
In this chapter's repository, find Asha's lost **"Add Visapur"** commit in the reflog, and make a branch called
`rescued` that points at it.

`git log --oneline rescued -1` should show `Add Visapur`, and `git show rescued:trails.md` should include the Visapur
section. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A bad commit was pushed an hour ago and two teammates have pulled it. What is the safe way to undo it?
:::
- [ ] `git reset --hard HEAD~1`, then force push
- [x] `git revert` the commit, then push
- [ ] Ask the teammates to delete their repositories
:::explain
Revert adds a correction that fits on top of everyone's history. Rewriting and force-pushing shared history makes
everyone else's copy disagree with the server.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
After `git reset --hard HEAD~1`, where can you find the commit you moved away from?
:::
- [ ] Nowhere, it is deleted
- [x] In `git reflog`, as one of the recent positions of HEAD
- [ ] On the server
:::explain
A reset moves a label; the commit stays in the repository, and the reflog records where HEAD was. Make a branch at it
to keep it.
:::
:::

:::step{type=deep-dive title="Go deeper: reverting merges, force pushes, and garbage collection"}
**Reverting a merge commit.** A merge has two parents, so Git asks which side to keep: `git revert -m 1 MERGE` undoes
what the merge brought in, keeping parent 1 (the branch you merged into). Re-merging that branch later needs care,
because Git thinks its commits are already merged.

**Force pushing.** `git push --force` makes the server accept rewritten history, throwing away commits others may
depend on. Teams protect main against it. If you ever truly must (for example to remove a leaked secret), use `git
push --force-with-lease`, which refuses if someone else pushed in the meantime, and tell the team first.

**When "lost" commits really go.** Commits that no branch, tag or reflog entry points at are eventually removed by
Git's housekeeping (`git gc`), after the reflog entries expire, typically 30 to 90 days later. Until then, they can
always be found.
:::

:::step{type=recap}
You can now:

- tell shared commits from your own, with `git status` and `origin/main`;
- undo a pushed commit with `git revert`, keep history honest, and push the correction;
- find commits that resets and amends left behind with `git reflog`;
- bring a lost commit back with `git branch NAME HEAD@{n}`.

Next, chapter 8: putting unfinished work aside for an urgent fix, and cleaning up junk files.

:::photo{src="/lesson-images/git/git-07-notes.webp" alt="Handwritten notes about undoing shared history: pushed? git revert, then push; never rewrite shared commits; git reflog: where HEAD has been; git branch rescued HEAD@ 1 in braces; almost nothing is lost" ai="true"}
One page of notes for this chapter.
:::
:::
