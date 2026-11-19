:::step{type=story title="The menu lives in git now"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
We moved the shop's menu and notes into git. Every change is now saved with who, when and why,
and nothing is ever really lost. But only if you commit it. Let me show you how we work.
:::

:::mission
Commit a new file, build a small feature on its own branch, and merge it into main.
:::
:::

:::step{type=concept title="Three places your work lives"}
Git keeps your work in three places:

1. **Working folder**: the files you edit.
2. **Staging area**: what will go into the next commit. `git add file` puts a file here.
3. **History**: commits. `git commit -m "why"` records everything staged as one snapshot.

A **branch** is just a name pointing at a commit. `main` is the shared one. A new branch lets
you work without touching `main`; when the work is ready, `git merge` brings it in.

:::tip
`git status` tells you which place each file is in. Run it all the time: it is free.
:::
:::

:::step{type=predict title="Guess first"}
:::question
You edit `menu.txt` and run `git commit -m "New prices"` without `git add`. What is committed?
:::
- [ ] The new `menu.txt`
- [x] Nothing: there is nothing staged
- [ ] The old `menu.txt` again
:::explain
A commit records only what is staged. Without `git add`, git says "no changes added to commit"
and makes no commit at all. (`git commit -a` stages changed files that git already tracks.)
:::
:::

:::step{type=try title="Look around"}
```bash run
cd shop && git status
```

```bash run
git log --oneline
```

Two commits, and `hours.txt` is **untracked**: git has never seen it.
:::

:::step{type=task task=commit_hours title="Commit the opening hours"}
Commit `hours.txt` to `main` as it is, with a message that mentions the **hours**.
:::

:::step{type=task task=combo_branch title="Work on a branch"}
Make a branch called `feature/combo`. On it, create `combo.txt` with this line and commit it:

```text
filter coffee + vada pav = 50
```

`main` should not change while you do this.
:::

:::step{type=task task=merge_combo title="Merge it"}
The combo is approved. Merge `feature/combo` into `main`.

```bash
git log --oneline --graph --all
```
:::

:::step{type=recap}
- Working folder, staging area, history: `git add` stages, `git commit` records.
- A branch is a name for a line of commits; `git switch -c name` makes one.
- `git merge other` brings another branch's commits into the branch you are on.
:::
