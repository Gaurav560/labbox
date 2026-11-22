:::step{type=story title="Three laptops, one website"}
Welcome to Part 3: working with others. Until now, every repository lived on one machine. But Trails is written by
three people, on three laptops. How does Ravi's new trail reach Asha? How does Meera's fix reach the website?

The answer is a shared copy that everyone can reach: a **remote**, usually on a server such as GitHub, GitLab or a
company's own Git server. Everyone **pushes** their new commits to it and **pulls** everyone else's from it.
Remember chapter 1: every copy is a full copy. The server is not special to Git; it is simply the copy the team
agreed to share through.

Keeping full copies in more than one place is the oldest way to keep something safe. The Svalbard Global Seed Vault, dug into an Arctic mountain, keeps copies of seeds from gene banks around the world. In 2020 GitHub stored a copy of public open-source code in the Arctic World Archive, in another mountain nearby.

:::photo{src="/lesson-images/git/seed-vault.webp" alt="The narrow concrete entrance of the Svalbard Global Seed Vault sticking out of a snowy mountainside, with people in orange suits" credit="Dag Endresen" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Svalbard_Global_Seed_Vault_is_well_guarded.jpg"}
The Svalbard Global Seed Vault.
:::

In this lab, the "server" is a folder, `09-remotes/server/trails.git`, standing in for GitHub. Everything works
exactly as with a real server, only faster. Since you cloned it, Ravi has pushed a commit.

:::mission
Bring Ravi's new commit into your copy, then push a trail of your own on top of it.
:::
:::

:::step{type=concept title="Remotes, origin, and remote-tracking branches"}
Your copy was made with `git clone`, which copies a whole repository and remembers where it came from, under the name
**origin**:

```text
$ cd /workspace/09-remotes/trails
$ git remote -v
origin	/workspace/09-remotes/server/trails.git (fetch)
origin	/workspace/09-remotes/server/trails.git (push)
```

On GitHub the address would be like `https://github.com/trails-team/trails.git`; here it is a folder. Now list
every branch, including the remote ones:

```text
$ git branch -a
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
```

`main` is your branch. `origin/main` is a **remote-tracking branch**: your copy's memory of where the server's main
was, the last time you talked to the server. It does not update by itself; you never commit on it. Three commands
move commits between the copies:

| Command | What it does |
|---|---|
| `git fetch` | download new commits from the server, and update `origin/main`; your `main` does not change |
| `git pull` | fetch, then merge `origin/main` into your branch |
| `git push` | upload your new commits and move the server's main to your commit |

:::diagram{name="git-push-pull"}
fetch downloads into origin/main, pull also merges into main, push uploads your commits to the server.
:::

**Check yourself:** after `git fetch`, has your `main` changed? (No: only `origin/main` moved. Your files are
untouched until you merge or pull.)
:::

:::step{type=try title="Is the server ahead of you?"}
`git status` compares your branch with `origin/main`, but only with what your copy **last saw**. So right now it
looks fine:

```text
$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

"Up to date" with an old memory. Fetch, and ask again:

```text
$ git fetch
From /workspace/09-remotes/server/trails
   4a973c2..312f52a  main       -> origin/main
$ git status
On branch main
Your branch is behind 'origin/main' by 1 commit, and can be fast-forwarded.
  (use "git pull" to update your local branch)

nothing to commit, working tree clean
```

The fetch moved `origin/main` from `4a973c2` to `312f52a`. You are one commit behind. To see what that commit is,
compare the two branches: "what is on origin/main that is not on main?"

```text
$ git log --oneline main..origin/main
312f52a Add Harishchandragad
```

That is Ravi's commit. Fetching is always safe: it never changes your work. A good habit is to fetch first and look,
before you pull.
:::

:::step{type=task task=pull_changes title="Your turn: bring in Ravi's commit"}
Bring Ravi's commit into your `main` with `git pull`. Afterwards `git log --oneline -1` should show `Add
Harishchandragad`, and `git status` should say your branch is up to date. Press **Check**.
:::

:::step{type=example title="Worked example: a push the server refuses"}
Pushing is how your commits reach everyone. But the server refuses a push that would **throw away** commits it has
and you do not. Here is the classic case in two scratch clones (only to read): a teammate pushed "Add tips" while you
were committing "Add a water page".

```text
$ git push
To /workspace/09-remotes/server/trails.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '/workspace/09-remotes/server/trails.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

**Rejected** is protection, not failure. If the server accepted, the teammate's "Add tips" would vanish from main.
The hint says exactly what to do: pull first.

```text
$ git pull --no-edit
From /workspace/09-remotes/server/trails
   312f52a..570798f  main       -> origin/main
Merge made by the 'ort' strategy.
 tips.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 tips.md
$ git log --oneline --graph -4
*   2f746bb Merge branch 'main' of /workspace/09-remotes/server/trails
|\
| * 570798f Add tips
* | 43fe0be Add a water page
|/
* 312f52a Add Harishchandragad
$ git push
To /workspace/09-remotes/server/trails.git
   570798f..2f746bb  main -> main
```

1. The pull fetched "Add tips" and merged it with your "Add a water page" (a merge commit, as in chapter 4).
2. Now your main contains everything the server has, plus your work.
3. The push is accepted: `570798f..2f746bb` means the server's main moved forward from the teammate's commit to your
   merge.

If both had changed the same lines, the pull would have stopped with a conflict, and you would resolve it exactly as
in chapter 5, then push.
:::

:::step{type=predict title="Guess first"}
:::question
Your push is rejected with "Updates were rejected because the remote contains work that you do not have locally".
What is the right next step?
:::
- [ ] `git push --force`
- [x] `git pull`, resolve anything that conflicts, then `git push` again
- [ ] Clone the repository again
:::explain
The server has commits you do not. Pull them in, then your push adds to them instead of replacing them. Force would
delete your teammate's work from the server.
:::
:::

:::step{type=task task=push_work title="Your turn: push a trail"}
Add this section to the end of `trails.md`, commit it on `main` with a clear message, and push it to the server:

```text
## Visapur
- Distance: 9 km
- Difficulty: moderate
```

`git status` should then say `Your branch is up to date with 'origin/main'`, and `git log --oneline origin/main -1`
should show your commit. Press **Check**: it looks at the server's copy.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `origin/main`?
:::
- [ ] The server's main, live
- [x] Your copy's memory of where the server's main was the last time you fetched, pulled or pushed
- [ ] A branch you commit to before pushing
:::explain
It updates only when you talk to the server. `git fetch` refreshes it without touching your own branches.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the difference between `git fetch` and `git pull`?
:::
- [x] fetch only downloads; pull downloads and then merges into your current branch
- [ ] They are the same
- [ ] fetch uploads, pull downloads
:::explain
pull is fetch plus merge. Fetch first when you want to look before anything changes.
:::
:::

:::step{type=deep-dive title="Go deeper: upstreams, pull with rebase, and real servers"}
**Upstream branches.** When you clone, your `main` is linked to `origin/main`, its **upstream**, which is why plain
`git pull` and `git push` know where to go. A new branch has no upstream until you push it with `-u` (chapter 10).

**pull --rebase.** Instead of a merge commit, `git pull --rebase` replays your local commits on top of the server's,
giving a straight history (chapter 11 explains rebase). Many teams set it as the default. This lab uses merges, so
you see what happens.

**Real servers.** On GitHub or GitLab you clone with an HTTPS address and a token, or with SSH and a key you add to
your account (`ssh-keygen`, then upload the public key). Everything else in this chapter is the same.

**Several remotes.** A repository can have more than one remote: `git remote add upstream URL` is common when you
contribute to someone else's project from your own fork.
:::

:::step{type=recap}
You can now:

- explain remotes, `origin`, and remote-tracking branches like `origin/main`;
- see whether the server is ahead with `git fetch`, `git status` and `git log main..origin/main`;
- bring others' work in with `git pull`, and share yours with `git push`;
- handle a rejected push the right way: pull, resolve, push.

Next, chapter 10: a pull request, end to end.

:::photo{src="/lesson-images/git/git-09-notes.webp" alt="Handwritten notes about remotes: origin = where you cloned from; fetch: download only; pull = fetch + merge; push: upload your commits; rejected? pull, then push" ai="true"}
One page of notes for this chapter.
:::
:::
