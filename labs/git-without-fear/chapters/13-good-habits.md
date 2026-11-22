:::step{type=story title="Things that must never be committed"}
Welcome to Part 4. Trails now has a small build step: a tool downloads its libraries into `node_modules/`, writes a
`build.log` every time it runs, and reads the maps API key from a file called `.env`. All three sit in the project
folder, untracked, one careless `git add .` away from being committed.

Each would be a different kind of trouble. `node_modules/` holds thousands of downloaded files that bloat every clone
and can be re-downloaded anytime. `build.log` changes on every build, cluttering every diff. And `.env` holds a
secret, which in a public repository can be found by bots within minutes.

Professional repositories protect themselves with a `.gitignore` file, set up on day one. And when a version is
finished and published, they mark it with a **tag**, so "the version we released on Friday" has a name forever. This
chapter is about those two habits.

:::mission
Make Git ignore dependencies, logs and secrets for good, and tag Trails' first release.
:::
:::

:::step{type=concept title=".gitignore: patterns Git pretends not to see"}
A `.gitignore` file lists **patterns**, one per line. Untracked files that match are left out of `git status`, and
`git add .` will not stage them. In this chapter's repository, three things are waiting to be ignored:

```text
$ cd /workspace/13-good-habits/trails
$ git status --short
?? .env
?? build.log
?? node_modules/
```

The patterns work like this:

| Pattern | Ignores |
|---|---|
| `build.log` | a file with exactly that name, in any folder |
| `*.log` | every file ending in `.log` |
| `node_modules/` | a folder with that name, and everything inside it |
| `!keep.log` | an exception: do **not** ignore this one, even though `*.log` matched it |
| `/todo.txt` | only `todo.txt` at the top of the repository |

The `.gitignore` file itself **is** committed, so the whole team, and every future clone, shares the same rules.

One important limit: **ignoring does not untrack.** A file that is already committed stays tracked even if it
matches a pattern; Git keeps recording its changes. To stop tracking it, remove it from Git and keep it on disk with
`git rm --cached` (chapter 6), then commit.

**Check yourself:** you add `*.log` to `.gitignore`, but `old.log` was committed last week. Does Git ignore it? (No: it
is tracked. `git rm --cached old.log` first.)
:::

:::step{type=example title="Worked example: ignoring a build folder and temporary files"}
Here is a scratch repository (only to read) with a build folder and two temporary files, one of which must be kept:

```text
$ git status --short
?? dist/
?? keep.tmp
?? notes.tmp
$ printf 'dist/\n*.tmp\n!keep.tmp\n' > .gitignore && cat .gitignore
dist/
*.tmp
!keep.tmp
$ git status --short
?? .gitignore
?? keep.tmp
```

1. `dist/` ignores the whole build folder.
2. `*.tmp` ignores every temporary file...
3. ...except `keep.tmp`, rescued by `!`.

`git status` now shows only what matters: the new `.gitignore` itself and `keep.tmp`. When you wonder **why** a file
is ignored, ask:

```text
$ git check-ignore -v notes.tmp dist/site.html
.gitignore:2:*.tmp	notes.tmp
.gitignore:1:dist/	dist/site.html
```

`-v` names the file, line and pattern responsible: line 2 (`*.tmp`) ignores `notes.tmp`; line 1 (`dist/`) ignores
the site. Finally the `.gitignore` is committed, so the rules are shared.
:::

:::step{type=predict title="Guess first"}
:::question
You add `.env` to `.gitignore` **after** `.env` was already committed and pushed with a real key in it. Is the key
safe now?
:::
- [ ] Yes, Git ignores it from now on
- [x] No: it is still tracked, and it is in the pushed history; untrack it, and change the key itself
- [ ] Only if you also delete the file
:::explain
Ignoring affects untracked files only, and history keeps every committed version. A secret that was ever pushed must be
revoked and replaced. That is why `.gitignore` belongs in the very first commit.
:::
:::

:::step{type=task task=gitignore_files title="Your turn: ignore what must never be committed"}
In this chapter's repository, write a `.gitignore` that ignores:

- the `node_modules/` folder,
- every `.log` file,
- the `.env` file,

then commit the `.gitignore`. Afterwards `git status --short` should show nothing at all to commit. Press **Check**.
:::

:::step{type=concept title="Tags: names for releases"}
A **tag** is a name for one commit, like a branch that never moves. Teams tag the commit they release: `v1.0`,
`v1.1`, `v2.0`. Months later, "what exactly was in 1.0?" is one command away, and fixing a bug in an old release
starts from its tag.

Tags are milestones. This is the Zero Mile Stone in Nagpur, which British surveyors treated as the centre of India and measured distances from: a fixed point that everyone could refer to. A tag like v1.0 is a fixed point in history in the same way.

:::photo{src="/lesson-images/git/zero-mile-stone.webp" alt="A tall sandstone pillar and four stone horse statues in a small garden in Nagpur, with trees behind" credit="Rajatchakks" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Zero_Mile_The_Geographical_Center_of_India.jpg"}
The Zero Mile Stone, Nagpur.
:::

There are two kinds:

- A **lightweight** tag is just a name pointing at a commit, like a branch file in `.git/refs/tags`.
- An **annotated** tag is a real object (chapter 12's fourth kind) with its own author, date and message. Releases
  should be annotated: they record who released what, when, and why.

In the scratch repository, one of each:

```text
$ git tag quick
$ git tag -a v0.1 -m 'Preview release'
$ git tag -l
quick
v0.1
$ git cat-file -t quick; git cat-file -t v0.1
commit
tag
```

`quick` points straight at a commit; `v0.1` is a tag object. `git show v0.1` shows the tag's own details first, then
the commit it marks:

```text
$ git show v0.1 --stat | head -12
tag v0.1
Tagger: Learner <learner@trails.example>
Date:   Sat Nov 21 12:00:00 2026 +0530

Preview release

commit 4c81e61b93204a9c0c061278cabc595afad85c6d
Author: Learner <learner@trails.example>
Date:   Sat Nov 21 12:00:00 2026 +0530

    Ignore the build folder and temporary files
```

`git tag -a NAME -m MESSAGE` tags the commit you are on; add a commit hash at the end to tag an older one. And one
surprise worth knowing now: **`git push` does not push tags.** You push a tag by name, `git push origin v1.0`, or all
of them with `git push --tags`.
:::

:::step{type=task task=tag_release title="Your turn: tag the first release"}
The commit **"Ready for the first release"** is Trails version 1.0. Find its hash with `git log --oneline`, and tag
it as `v1.0` with an **annotated** tag and a message.

`git show v1.0` should show `tag v1.0`, your message, and that commit. (There is no server in this chapter, so no push
is needed.) Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which pattern ignores every `.log` file except `keep.log`?
:::
- [ ] `*.log` alone
- [x] `*.log` and then `!keep.log`
- [ ] `!*.log`
:::explain
Rules are read top to bottom, and `!` re-includes a file a previous pattern excluded.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You tagged `v1.0` and ran `git push`. Your teammate fetches and does not see the tag. Why?
:::
- [ ] Tags are private
- [x] `git push` does not send tags; push it with `git push origin v1.0`
- [ ] Lightweight tags cannot be pushed
:::explain
Tags are pushed explicitly, by name or with `--tags`. Once pushed, everyone who fetches gets them.
:::
:::

:::step{type=deep-dive title="Go deeper: version numbers, release notes and global ignores"}
**Semantic versioning.** Many projects number releases MAJOR.MINOR.PATCH: a patch (1.0.1) fixes bugs, a minor version
(1.1.0) adds features without breaking anything, a major version (2.0.0) may break compatibility. Tags such as
`v1.4.2` let anyone check out exactly that version.

**Release notes from history.** `git log --oneline v1.0..v1.1` lists every commit between two releases: the raw
material for release notes, and one more reason for clear commit messages. Hosting platforms turn tags into release
pages with downloadable archives.

**Templates and global ignores.** GitHub keeps ready-made `.gitignore` templates for most languages. Files that only
your own machine makes (an editor's settings, `.DS_Store` on macOS) belong in a **global** ignore file
(`git config --global core.excludesFile ~/.gitignore_global`), not in every project.

**Secrets scanning.** Tools such as gitleaks, and the scanners built into hosting platforms, check commits for keys
before or after they are pushed. They are a safety net; `.gitignore` is the fence.
:::

:::step{type=recap}
You can now:

- keep dependencies, logs and secrets out of history with a committed `.gitignore`, using names, `*`, folders and `!`;
- find out why a file is ignored with `git check-ignore -v`, and remember that ignoring does not untrack;
- tag a release with an annotated tag, `git tag -a v1.0 -m ...`, on any commit;
- push tags explicitly, by name or with `--tags`.

Next, chapter 14, the capstone: rescue a messy repository and ship a release.

:::photo{src="/lesson-images/git/git-13-notes.webp" alt="Handwritten notes about good habits: .gitignore: node_modules/, *.log; ignoring does not untrack; git tag -a v1.0 -m ...; git push origin v1.0; secrets: never commit them" ai="true"}
One page of notes for this chapter.
:::
:::
