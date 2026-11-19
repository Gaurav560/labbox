:::step{type=story title="Two mistakes before lunch"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Bad morning in the kitchen repo. Someone pushed filter coffee at 300 rupees instead of 30, and the
newest commit, not pushed yet, has our SMS key in it. Fix both. And remember the one rule.
:::

:::mission
Remove a secret from a commit that is only on your machine, and undo a pushed commit without rewriting history.
:::
:::

:::step{type=concept title="The one rule"}
**Never rewrite history that other people already have.**

- A commit that is **only on your machine** can be changed freely. `git commit --amend` replaces
  the last commit with a fixed one.
- A commit that is **already pushed** must stay. `git revert <commit>` adds a *new* commit that
  undoes it, so everyone's history still lines up.

`git log origin/main..main` lists the commits you have that the server does not.

Removing a file in a new commit does not erase it: the old commit still holds it, and anyone can
read it from there. A leaked secret must never get into history at all, or be changed (rotated).
:::

:::step{type=predict title="Guess first"}
:::question
The last commit added `secrets.env`. You run `git rm secrets.env` and commit again. Is the secret out of git?
:::
- [ ] Yes, the file is deleted
- [x] No, the earlier commit still contains it
- [ ] Only after a push
:::explain
Every commit is a full snapshot. The commit that added `secrets.env` still has it, and
`git show <that commit>:secrets.env` prints it. To remove it you have to change that commit.
:::
:::

:::step{type=try title="See what is pushed"}
```bash run
cd /workspace/kitchen && git log --oneline --graph --all
```

```bash run
git log --oneline origin/main..main
```

The newest commit is only local. The 300 typo is already on `origin`.
:::

:::step{type=task task=undo_secret title="Take the secret out"}
Change the last commit so that **no commit on main contains `secrets.env`**:

- keep `secrets.env` in your folder (the kitchen still needs it);
- add it to `.gitignore`, committed, so nobody adds it again;
- keep the README from that commit.
:::

:::step{type=task task=revert_bad title="Undo the pushed typo"}
Filter coffee must be **30** again on `main`, but the pushed history must stay exactly as it is.
Undo the "Raise filter coffee to 300" commit with a new commit.
:::

:::step{type=deep-dive title="When it was already pushed"}
If a secret reaches a shared server, treat it as public: **rotate it** (make a new key and disable
the old one) first. Cleaning history after that needs tools like `git filter-repo` and a
force-push that every teammate has to deal with. It is a last resort, not an undo button.

And if you ever think you lost commits, `git reflog` lists everywhere your branch has pointed
recently. Almost nothing in git is truly gone.
:::

:::step{type=recap}
- Only rewrite what is not pushed: `git commit --amend` fixes the last local commit.
- Pushed mistakes get a `git revert`, a new commit that undoes them.
- `git rm --cached` plus `.gitignore` keeps a file on disk but out of git.
- `git reflog` finds "lost" commits.
:::
