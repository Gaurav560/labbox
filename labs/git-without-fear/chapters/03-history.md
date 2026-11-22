:::step{type=story title="Rajmachi is 51 km now?"}
A reader writes in: "Your site says Rajmachi is 51 km. I nearly cancelled my trip. Is that right?" It is not:
Rajmachi is about 15 km. Somebody typed the digits the wrong way round. And while you look, you notice something
else: the useful note about drinking water at Udhewadi village is gone from the Rajmachi section.

Three friends edit this site. Asking around ("did you change Rajmachi?") wastes everyone's evening, and memories are
unreliable. But Git remembers every change, by whom, when and why. This chapter teaches you to **read history**:
list it, filter it, look inside any commit, ask who last touched a line, and find the commit where a piece of text
appeared or vanished.

Keeping a record of who held what, and when, is an old idea. In 1086 the clerks of William the Conqueror wrote the Domesday Book, a survey of the land of England and the people who held it, and historians still read it today. git log is that record for your files, kept automatically.

:::photo{src="/lesson-images/git/domesday-page.webp" alt="A page of the Domesday Book: dense columns of handwritten Latin in brown ink, with a few lines in red" credit="Domesday Book (The National Archives)" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Domesday_Book,_Cambridgeshire,_page_21.png"}
A page of the Domesday Book, 1086.
:::

:::mission
Find who changed Rajmachi's distance, and which commit removed the water point.
:::
:::

:::step{type=concept title="git log: the history, your way"}
`git log` lists commits, newest first. This chapter's repository has eight:

```text
$ cd /workspace/03-history/trails
$ git log --oneline
28c3b1d Update Rajmachi's distance
0912977 Tidy up the Rajmachi section
2d961f3 Add Lohagad
6d3d634 Fix Kalsubai's season
6b3643e Add a water point to Rajmachi
9b9b8c3 Add Harishchandragad
5e82d81 Add Rajmachi and Kalsubai
fa60e0b Add the README
```

The first column is each commit's **short hash**: the first 7 characters of its full name. You can use a short hash
anywhere Git asks for a commit.

`git log` has many options. A few you will use all the time:

| You want | Command |
|---|---|
| one line per commit | `git log --oneline` |
| who and when, compactly | `git log --format='%h %an %ad %s' --date=short` |
| only one person's commits | `git log --author=Meera` |
| only commits that touched a file | `git log -- README.md` |
| the changes themselves, too | `git log -p` |
| the last N commits | `git log -3` |

For example, who did what in the last three commits:

```text
$ git log -3 --format='%h %an %ad %s' --date=short
28c3b1d Ravi 2026-11-09 Update Rajmachi's distance
0912977 Meera 2026-11-08 Tidy up the Rajmachi section
2d961f3 Asha 2026-11-07 Add Lohagad
```

(`%h` is the short hash, `%an` the author's name, `%ad` the date, `%s` the message's first line.)

**Check yourself:** how would you list only Meera's commits? (`git log --oneline --author=Meera`; it shows two.)
:::

:::step{type=example title="Worked example: looking inside one commit"}
`git show` with a hash shows one commit in full: who, when, the message, and the exact change. Here is Ravi's
Kalsubai fix:

```text
$ git show 6d3d634
commit 6d3d634f227b36a02f52c82f174eeb1647d7e63f
Author: Ravi <ravi@trails.example>
Date:   Fri Nov 6 21:05:00 2026 +0530

    Fix Kalsubai's season

diff --git a/trails.md b/trails.md
index b3fdc92..a8b146d 100644
--- a/trails.md
+++ b/trails.md
@@ -9,7 +9,7 @@
 ## Kalsubai
 - Distance: 6 km
 - Difficulty: hard
-- Best season: October to February
+- Best season: October to March
 
 ## Harishchandragad
 - Distance: 14 km
```

1. The full hash (40 characters), the author and the date, in the author's time zone (`+0530` is India).
2. The message.
3. The diff, exactly as chapter 2 taught you to read it: one line out (`-`), one line in (`+`).

So in one command you know that Ravi changed Kalsubai's season from February to March, on 6 November in the evening.
:::

:::step{type=concept title="git blame: who touched this line last?"}
`git log` starts from commits. Often you start from a **line** instead: "this line is wrong, who wrote it?".
`git blame` answers it for every line of a file: the commit that last changed it, the author and the date. `-L`
limits it to some lines; here, the Kalsubai section:

```text
$ git blame -L 8,11 trails.md
5e82d817 (Asha 2026-11-03 10:00:00 +0530  8) ## Kalsubai
5e82d817 (Asha 2026-11-03 10:00:00 +0530  9) - Distance: 6 km
5e82d817 (Asha 2026-11-03 10:00:00 +0530 10) - Difficulty: hard
6d3d634f (Ravi 2026-11-06 21:05:00 +0530 11) - Best season: October to March
```

Lines 8 to 10 were written by Asha in her first commit; line 11 was last changed by Ravi, in commit `6d3d634f`, the
season fix you just looked at. Take any hash from `blame` to `git show`, and you see the whole story of that change.

Despite its name, `blame` is not about blaming anyone. Most of the time it answers a friendlier question: "who
knows about this line, so I can ask them?"
:::

:::step{type=predict title="Guess first"}
:::question
`git blame` shows that line 11 was last changed in commit `6d3d634f`. Does that mean line 11 was **created** in that
commit?
:::
- [ ] Yes, blame always shows who wrote the line first
- [x] Not necessarily: blame shows the last commit that changed the line
- [ ] Blame only shows lines that were never changed
:::explain
The Kalsubai season line existed from Asha's first commit; Ravi's commit changed it, so blame now shows Ravi. To see
earlier versions, run blame on an older commit, or use `git log -L 11,11:trails.md`.
:::
:::

:::step{type=task task=find_author title="Your turn: who changed Rajmachi's distance?"}
Find out who last changed the line `- Distance: 51 km` in `trails.md`.

Write just their first name in a file called `answer-author.txt`, **next to** the trails folder (in
`/workspace/03-history`, not inside the repository):

```bash
echo NAME > /workspace/03-history/answer-author.txt
```

(with the real name instead of NAME). Press **Check**.
:::

:::step{type=concept title="git log -S: when did this text come or go?"}
The water point line is the harder case: it is **gone**, so there is no line left to blame. You need the commit in
which it disappeared.

`git log -S 'text'` (S for "string") lists every commit that changed **how many times** that text appears in the
files: the commit that added it, and the commit that removed it. Here is the same search for another word:

```text
$ git log -S 'Lohagad' --oneline
2d961f3 Add Lohagad
```

One commit: Lohagad was added once and never removed. For text that was added **and later removed**, `-S` lists both
commits, newest first: the removal on top, the addition below. Add `-p` to see each diff and be sure.

This is how teams answer "when did this feature disappear?" in a history of thousands of commits, in a second.
:::

:::step{type=task task=find_commit title="Your turn: which commit removed the water point?"}
The Rajmachi section used to say `- Water: Udhewadi village`. Find the commit that **removed** that line.

Write its short hash (the first 7 characters are enough) in `answer-commit.txt`, next to the trails folder:

```bash
echo HASH > /workspace/03-history/answer-commit.txt
```

Careful: the search finds two commits. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which command shows only the commits that touched `README.md`?
:::
- [ ] `git log README.md --oneline --all`
- [x] `git log --oneline -- README.md`
- [ ] `git show README.md`
:::explain
`--` separates options from file names. It answered one commit, `fa60e0b Add the README`. (Without `--`, Git usually
guesses right too, but `--` makes it certain.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A line was deleted last month and you want to know who deleted it. Which tool fits?
:::
- [ ] `git blame`, on today's file
- [x] `git log -S` with text from that line
- [ ] `git status`
:::explain
Blame only shows lines that still exist. `-S` finds the commit where the text disappeared, and its author.
:::
:::

:::step{type=deep-dive title="Go deeper: comparing any two versions, and finding a bug by halves"}
**Compare any two commits.** `git diff 5e82d81 HEAD` shows everything that changed between them, and `--stat`
summarises it: here, `trails.md | 14 ++++++++++++--`. `HEAD` always means "the commit you are on now"; `HEAD~2`
means two commits before it.

**See a file as it was.** `git show 5e82d81:trails.md` prints the whole file as it was in that commit, without
changing anything.

**Find the commit that broke something: git bisect.** If you know "it worked in November, it is broken now", `git
bisect` checks out the commit halfway between, you test and say `git bisect good` or `bad`, and it halves the range
again. In a history of 1,000 commits, it finds the culprit in about 10 steps.

**The history of one line.** `git log -L 4,4:trails.md` shows every commit that ever changed line 4 of `trails.md`,
with the diffs.
:::

:::step{type=recap}
You can now:

- read and filter history with `git log`: one line each, by author, by file, with the changes;
- look inside any commit with `git show`;
- find who last changed a line with `git blame`, and look at that commit;
- find when text appeared or disappeared with `git log -S`.

Next, chapter 4: branches, for working on something new without disturbing anyone.

:::photo{src="/lesson-images/git/git-03-notes.webp" alt="Handwritten notes about reading history: git log --oneline; git show HASH; git blame: who changed a line; git log -S: when text came or went; HEAD = where I am now" ai="true"}
One page of notes for this chapter.
:::
:::
