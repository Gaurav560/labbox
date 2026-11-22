:::step{type=story title="Two friends, one line"}
Ravi walked Rajmachi with a GPS watch and changed the distance to 16 km, on his branch. The same evening, Asha
measured the route on a map and changed the same line on main to 15.5 km. Both were trying to help. Now Ravi's
branch must be merged into main, and Git faces a question it cannot answer by itself: **which number is right?**

When two branches change **different** places, Git combines them on its own, as you saw in chapter 4. When they
change **the same lines**, Git stops and asks you. That is a **merge conflict**.

Roads have the same problem where two lanes become one. Most of the time traffic merges smoothly by itself; only when two cars aim for the same spot does someone have to decide who goes first.

:::photo{src="/lesson-images/git/merge-sign.webp" alt="A red-bordered triangular road sign showing a side road merging into a main road, beside a dual carriageway" credit="Albert Bridge" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:%22Traffic_merging_from_left%22_sign,_Belfast_-_geograph.org.uk_-_2673443.jpg"}
A merging traffic sign in Belfast.
:::

Conflicts frighten beginners, because the terminal says "CONFLICT" and "failed". They are nothing of the sort: they
are Git being careful, showing you both versions, and waiting for a person to decide. Resolving one takes a minute
once you have seen how. This chapter makes conflicts boring, which is exactly what they should be.

:::mission
Merge Ravi's branch and keep his GPS distance, then merge Meera's branch and keep both credits.
:::
:::

:::step{type=try title="See a conflict happen"}
Look at this chapter's repository first. Main and two branches have all moved since they split:

```text
$ cd /workspace/05-merge-conflicts/trails
$ git log --oneline --graph --all --decorate
* 635f60d (HEAD -> main) Credit the maps
* a80ceee Rajmachi is 15.5 km from the map
| * 9bb5bf0 (meera/readme) Credit the photos
|/
| * 55e4a84 (ravi/rajmachi) Rajmachi is 16 km by GPS
|/
* df53390 Add the README and two trails
```

Now merge Ravi's branch into main, and read what Git says:

```text
$ git merge ravi/rajmachi
Auto-merging trails.md
CONFLICT (content): Merge conflict in trails.md
Automatic merge failed; fix conflicts and then commit the result.
$ git status
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   trails.md

no changes added to commit (use "git add" and/or "git commit -a")
```

Nothing is broken. The merge is simply **paused**: everything that could be combined automatically has been, and
`trails.md` is waiting for you. `git status` even lists your two ways forward: fix and commit, or `git merge
--abort` to go back to exactly how things were before the merge. Try the abort now, to see that it is safe:

```text
$ git merge --abort
$ git status --short
```

Empty: as if you had never started. Now merge again; this time you will finish it.
:::

:::step{type=concept title="Reading conflict markers"}
During a conflict, Git writes **both versions** into the file, between three marker lines. Here is the Rajmachi
section of `trails.md` while the merge is paused:

```text
## Rajmachi
<<<<<<< HEAD
- Distance: 15.5 km
=======
- Distance: 16 km
>>>>>>> ravi/rajmachi
- Difficulty: easy
- Best season: June to September
```

Read it in three parts:

1. From `<<<<<<< HEAD` to `=======`: **your** version, the branch you are on (main, so Asha's 15.5 km).
2. From `=======` to `>>>>>>> ravi/rajmachi`: **their** version, the branch you are merging in.
3. Everything outside the markers merged fine and needs nothing from you.

**Resolving** means editing the file until it says what it should, and removing the three marker lines. You can
keep one side, the other, both, or write something new. Git does not care which; it only needs you to decide.
Then `git add` the file (that tells Git "this one is resolved"), and `git commit` to finish the merge.

:::diagram{name="git-conflict"}
Both sides changed the same line; Git pauses, writes both versions between markers, and waits for your decision.
:::

**Check yourself:** in a conflict block, which part is the branch you are on? (The top part, after `<<<<<<< HEAD`.)
:::

:::step{type=example title="Worked example: one conflict, start to finish"}
Here is a different conflict, in a scratch copy (only to read). Main says Kalsubai's season starts in November; a
branch called `season` says it ends in March. Both changed the same line:

```text
$ git merge season
Auto-merging trails.md
CONFLICT (content): Merge conflict in trails.md
Automatic merge failed; fix conflicts and then commit the result.
```

The Kalsubai section now reads:

```text
## Kalsubai
- Distance: 6 km
- Difficulty: hard
<<<<<<< HEAD
- Best season: November to February
=======
- Best season: October to March
>>>>>>> season
```

Both people were partly right: November is the true start (main), March the true end (the branch). So the
resolution is a **new** line that combines them. In the editor, the section becomes:

```text
## Kalsubai
- Distance: 6 km
- Difficulty: hard
- Best season: November to March
```

The markers are gone and the line says what is true. Mark it resolved and finish:

```text
$ git add trails.md
$ git status
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
	modified:   trails.md

$ git commit --no-edit
[main 9eb56ec] Merge branch 'season'
```

(The scratch copy was a clone, which is why `status` also mentions `origin/main`; ignore that line here.)

1. Read both versions, and decide what is **true**, not which side "wins".
2. Edit the file; delete all three marker lines.
3. `git add` the file; `git commit` concludes the merge, with a merge commit.

Before you `git add`, search the file for `<<<<<<<` once more. A forgotten marker committed into a file is the most
common conflict mistake, and it is embarrassing on a live website.
:::

:::step{type=predict title="Guess first"}
:::question
In the middle of resolving, you feel lost and want to start the merge again from scratch. What is safe?
:::
- [ ] Delete the repository and clone it again
- [x] `git merge --abort`: everything goes back to how it was before the merge started
- [ ] `git commit` whatever is there
:::explain
`--abort` is always available while a merge is paused, and it throws away only the half-finished merge. Committing
a half-resolved file is the one thing to avoid.
:::
:::

:::step{type=task task=resolve_conflict title="Your turn: Ravi's GPS against Asha's map"}
Asha agrees: a GPS track beats a measurement on a map. On `main`, merge `ravi/rajmachi` and resolve the conflict so
that Rajmachi's distance is Ravi's:

```text
- Distance: 16 km
```

Remove all the marker lines and leave the rest of the file as it is, then `git add trails.md` and `git commit` to
finish the merge. (In VS Code, the editor shows the conflict with buttons such as "Accept Incoming Change", which
does the same edit for you.) Press **Check**.
:::

:::step{type=concept title="When both sides are right"}
Not every conflict is an argument. Often both sides **added** something at the same spot, and the right resolution
keeps both.

Meera's branch adds a line at the end of the README crediting her photos. Asha, on main, added a line at the very
same place crediting her maps. Git sees two different additions at one position, and cannot know the order you
want, so it asks.

A good habit for any conflict: ask "what should this file say now?", not "whose side do I take?". For two credits,
the answer is obviously both, one after the other.

Two more tools, for when one side should win completely (whole files, like a generated file): `git checkout --ours
file` keeps your version, `git checkout --theirs file` keeps the incoming one. Then `git add` as usual. Use them only
when you are sure; reading the markers is safer.
:::

:::step{type=task task=combine_both title="Your turn: two credits, both right"}
On `main`, merge `meera/readme`. Resolve the conflict in `README.md` so that **both** lines stay:

```text
Maps by Asha.
Photos by Meera.
```

Delete only the marker lines, then add and commit. `tail -4 README.md` should show both credits and no markers.
Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You edited the conflicted file and deleted the markers. Why does Git still say "you are still merging"?
:::
- [ ] It did not notice the edit
- [x] You have not run `git add` on the file and `git commit` yet; Git only knows a file is resolved when you stage it
- [ ] You must run `git merge` again
:::explain
Staging a conflicted file is how you tell Git "resolved". Then `git commit` creates the merge commit.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Two branches changed **different** lines of the same file. What happens when you merge them?
:::
- [x] Git combines both changes by itself, with no conflict
- [ ] A conflict, because it is the same file
- [ ] Git keeps only the branch you are on
:::explain
Conflicts are about the same lines (or lines right next to each other), not the same file. Most merges have no
conflict at all.
:::
:::

:::step{type=deep-dive title="Go deeper: fewer conflicts, and better tools"}
**Why conflicts happen less than you fear.** Git merges by comparing both sides with their common ancestor, the
commit where they split. A line changed on only one side is taken from that side automatically. Only lines changed
on **both** sides, differently, become conflicts.

**Making them rarer.** Merge often, keep branches short, and keep commits focused. Two people reformatting the same
whole file at once is the classic recipe for a huge conflict.

**Seeing three versions.** `git config --global merge.conflictstyle zdiff3` adds the ancestor's version between the
markers, so you see what both sides started from. Many people find conflicts much easier to read this way.

**Merge tools.** Editors such as VS Code show conflicts side by side with buttons, and `git mergetool` opens a
three-way merge program. They change how it looks, not what you decide.
:::

:::step{type=recap}
You can now:

- explain when Git can merge by itself and when it must ask: the same lines changed on both sides;
- read conflict markers: your side, their side, and the separator;
- resolve a conflict by editing, `git add`, then `git commit`, or abandon it safely with `git merge --abort`;
- choose a resolution by what is true: one side, the other, a combination, or both.

That completes Part 1. Next, Part 2 starts with chapter 6: undoing mistakes before anyone else sees them.

:::photo{src="/lesson-images/git/git-05-notes.webp" alt="Handwritten notes about merge conflicts: same line changed on both sides; <<<<<<< yours, >>>>>>> theirs; edit to the truth, delete markers; git add, then git commit; git merge --abort is safe" ai="true"}
One page of notes for this chapter.
:::
:::
