:::step{type=story title="A second pair of eyes"}
Trails has grown. Readers rely on it, and one wrong distance could send someone up a hill at the wrong time of
day. So the three friends agree on a rule that almost every software team follows: **nothing goes into main without
someone else looking at it first**.

The way teams do that is the **pull request** (GitLab calls it a merge request): you push your work on its own
branch, ask a teammate to review it, fix what they spot, and only then merge it into main. On GitHub it is a web
page with the diff, comments and a big green Merge button. Underneath, it is exactly the Git you already know:
branches, push, diff, commits and a merge.

Writers have always had their work checked before it went out. These are printer's proofs of a novel by Marcel Proust, covered in his own corrections and additions before printing. A pull request is a proof for code: read, marked up, corrected, then published.

:::photo{src="/lesson-images/git/proust-proofs.webp" alt="Old printed pages pasted together and covered with dense handwritten corrections and added slips of paper" credit="Marcel Proust (scan from Wikipedia)" license="Public domain" source="https://commons.wikimedia.org/wiki/File:MS_A_la_recherche_du_temps_perdu.jpg"}
Marcel Proust's corrected proofs.
:::

In this lab you play both roles yourself, with plain Git commands, so you understand what every button on such a
page really does. You will add a new trail, Torna, through a full review cycle.

:::mission
Push a branch with the Torna trail for review, fix what the reviewer asks, and merge it into main on the server.
:::
:::

:::step{type=concept title="The pull request flow"}
Every pull request, on any platform, follows the same five steps:

1. **Branch.** Make a branch from an up-to-date main, and commit your work on it.
2. **Push the branch.** The server now has your branch; on GitHub you would click "Compare and pull request".
3. **Review.** A teammate reads the diff between main and your branch, and comments.
4. **Fix.** You commit the requested changes on the same branch and push again. The pull request updates itself,
   because it simply shows the branch.
5. **Merge.** When approved, the branch is merged into main (on the website, or locally and pushed), and the branch
   is deleted.

Pushing a new branch for the first time needs one extra word, `-u` (set upstream), so that later plain `git push` and
`git pull` on that branch know where to go:

```bash
git push -u origin feature/torna
```

The review itself is built on a diff you already know, with one twist: **three dots**. `git diff main...feature`
shows what the branch changed **since it left main**, ignoring anything that happened on main in the meantime.
That is exactly what a reviewer needs to see.

:::diagram{name="git-pull-request"}
Branch, push, review, fix, merge: the same five steps on every platform.
:::

**Check yourself:** the reviewer asks for a change. Do you open a new pull request? (No: commit on the same branch
and push; the existing pull request shows the new commit.)
:::

:::step{type=example title="Worked example: a tips page, reviewed"}
Here is the whole cycle for a different change, a tips page, in a scratch clone (only to read). Steps 1 and 2:

```text
$ git switch -c feature/tips
Switched to a new branch 'feature/tips'
$ git push -u origin feature/tips
To /workspace/10-pull-request/server/trails.git
 * [new branch]      feature/tips -> feature/tips
branch 'feature/tips' set up to track 'origin/feature/tips'.
$ git branch -vv
* feature/tips 8d2cfb8 [origin/feature/tips] Add trekking tips
  main         a90c4c7 [origin/main] Add the README and two trails
```

(The commit `Add trekking tips` was made before the push.) `[new branch]`: the server has it now. `git branch -vv`
shows each branch with its upstream in square brackets.

Step 3, the review. The reviewer looks at the commits and the diff since main:

```text
$ git log --oneline main..feature/tips
8d2cfb8 Add trekking tips
$ git diff main...feature/tips
diff --git a/tips.md b/tips.md
new file mode 100644
index 0000000..6547801
--- /dev/null
+++ b/tips.md
@@ -0,0 +1,2 @@
+Start early.
+Carry water.
```

They comment: "Please add the most important tip: tell someone where you are going." Step 4, the fix, on the same
branch:

```text
$ git push
To /workspace/10-pull-request/server/trails.git
   8d2cfb8..6221627  feature/tips -> feature/tips
```

(after committing "Add the safety tip, from the review"). Step 5, merge into main and push, then delete the branch on
the server:

```text
$ git switch main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
$ git merge --no-ff --no-edit feature/tips
Merge made by the 'ort' strategy.
 tips.md | 3 +++
 1 file changed, 3 insertions(+)
 create mode 100644 tips.md
$ git push
To /workspace/10-pull-request/server/trails.git
   a90c4c7..6e9591d  main -> main
$ git push origin --delete feature/tips
To /workspace/10-pull-request/server/trails.git
 - [deleted]         feature/tips
$ git log --oneline --graph -4
*   6e9591d Merge branch 'feature/tips'
|\
| * 6221627 Add the safety tip, from the review
| * 8d2cfb8 Add trekking tips
|/
* a90c4c7 Add the README and two trails
```

`--no-ff` (no fast-forward) makes a merge commit even when a fast-forward was possible, as GitHub's Merge button does.
History now shows the feature as one group: the original commit, the review fix, and the merge that accepted them.
:::

:::step{type=predict title="Guess first"}
:::question
You push a branch for the first time with plain `git push` (no `-u`). What happens?
:::
- [ ] It pushes to main
- [x] Git refuses and tells you the branch has no upstream, suggesting the `--set-upstream` command
- [ ] It pushes silently and forgets the link
:::explain
A new branch does not know where it belongs on the server yet. `git push -u origin NAME` creates it there and sets
the link, once. After that, plain `git push` works.
:::
:::

:::step{type=task task=push_branch title="Your turn: push Torna for review"}
In `/workspace/10-pull-request/trails`:

1. Make a branch called `feature/torna` from main.
2. Add this section at the end of `trails.md`, and commit it:

```text
## Torna
- Distance: 7 km
- Difficulty: moderate
```

3. Push the branch to the server, with `-u`.

`git branch -vv` should show `[origin/feature/torna]` next to your branch. Press **Check**.
:::

:::step{type=concept title="Being a good reviewer, and a good author"}
Before the second task, the review itself. Meera reviewed your Torna branch with `git diff main...feature/torna`,
and left one comment: **"Please add the best season, like every other trail: October to February."**

A few habits make reviews fast and friendly, on both sides:

- **Small pull requests.** A 20-line change gets a careful review in minutes. A 2,000-line change gets "looks good
  to me" and hidden bugs.
- **The author explains.** The description says what changed and why, and how to check it.
- **The reviewer asks about the work, not the person.** "This distance differs from the map, which is right?" beats
  "wrong".
- **Fixes are new commits on the branch**, so the reviewer can see exactly what changed since they last looked.

Merging is the author's last step once the review is approved. On a platform you would click Merge; here you merge
locally and push main, which is exactly what the button does on the server.
:::

:::step{type=task task=merge_reviewed title="Your turn: fix it, then merge"}
Do what the review asked, then merge:

1. On `feature/torna`, add the line `- Best season: October to February` to the Torna section, commit it, and push
   the branch.
2. Switch to `main`, merge `feature/torna` into it, and push main.

`git log --oneline --graph -5` should show your two Torna commits joined into main. Press **Check**: it looks at the
server's main and the server's branch.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does a reviewer use `git diff main...feature` (three dots) instead of two?
:::
- [x] It shows only what the branch changed since it left main, not what main changed meanwhile
- [ ] It is faster
- [ ] Two dots only works on main
:::explain
With two dots, newer commits on main would show up as "removed" lines in the diff, confusing the review. Three dots
compares the branch with the point where it started.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The reviewer asked for a change after you pushed. What do you do?
:::
- [ ] Open a new branch and a new pull request
- [x] Commit the change on the same branch and push it
- [ ] Amend the pushed commit and force push
:::explain
The pull request follows the branch, so a new commit there shows up for the reviewer at once. Rewriting pushed
commits during a review makes it harder for the reviewer to see what changed.
:::
:::

:::step{type=deep-dive title="Go deeper: merge styles, protected branches and CI"}
**Three merge buttons.** Platforms usually offer: a merge commit (what you did), **squash and merge** (all the
branch's commits become one commit on main), and **rebase and merge** (the commits are replayed onto main, no merge
commit). Teams pick one style and stick to it; chapter 11 explains the trade-offs.

**Protected branches.** Teams lock main so that nobody pushes to it directly: every change needs a pull request,
an approval and passing checks. Force pushes are blocked.

**Continuous integration.** When a branch is pushed, a CI service (GitHub Actions, GitLab CI) runs the tests
automatically, and the pull request shows a green tick or a red cross before anyone merges. LabBox's own Check button
is a small cousin of that idea.

**Forks.** In open-source projects you cannot push to the original repository. You fork it (your own copy on the
server), push your branch there, and open the pull request from your fork to the original.
:::

:::step{type=recap}
You can now:

- describe the pull request flow: branch, push, review, fix, merge;
- push a new branch with `git push -u origin NAME`, and see upstreams with `git branch -vv`;
- review a branch with `git log main..branch` and `git diff main...branch`;
- add review fixes as new commits, merge the reviewed branch into main and push it.

Next, chapter 11: rebase, and when to use it instead of merge.

:::photo{src="/lesson-images/git/git-10-notes.webp" alt="Handwritten notes about a pull request: branch, push, review, fix, merge; git push -u origin branch; git diff main...branch; review fixes = new commits; small PRs, kind reviews" ai="true"}
One page of notes for this chapter.
:::
:::
