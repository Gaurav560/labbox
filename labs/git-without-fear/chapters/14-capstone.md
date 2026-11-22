:::step{type=story title="Release day, and a mess"}
It is release day for Trails 2.0, with Meera's new maps page. Ravi was meant to prepare main, and he left a note:
"Added the trekking tips. Oops, I committed credentials.json with the maps key by accident, but I deleted it in the
next commit, so it's fine. Haven't pushed yet. Can you do the release?"

It is not fine, as you know from chapter 6: the key is still inside the first of those two commits, and pushing would
publish it forever. But because neither commit is pushed, it can still be fixed properly.

This capstone has no worked example and no step-by-step recipe. You have every tool you need from the course:
reading history (3), merging (4), undoing local work (6), the golden rule about shared history (7 and 11), remotes
(9) and tags (13). The job is to **diagnose first, plan, then act**, exactly as an engineer would on a real team.

Mountain rescue teams work this way on every call: find out exactly where things stand, make a plan, then act, never the other way round.

:::photo{src="/lesson-images/git/mountain-rescue.webp" alt="A mountain rescue team's white and orange four-wheel-drive vehicle parked beside their gazebo and kit bags" credit="Steve Houldsworth" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Mountain_Rescue_Team_-_geograph.org.uk_-_6198377.jpg"}
A mountain rescue team and its kit.
:::

:::mission
Remove the leaked credentials from history without touching what was pushed, then merge the maps feature and release
v2.0 to the server.
:::
:::

:::step{type=try title="Diagnose before you touch anything"}
Start, as always, by looking. The whole picture in one command:

```text
$ cd /workspace/14-capstone/trails
$ git log --oneline --graph --all --decorate
* f84bd85 (HEAD -> main) Remove credentials
* a0aa73b Add trekking tips
| * 0048c8d (feature/maps) Add a maps page
|/
* 72b9698 (origin/main) Add the README and two trails
```

Three lines of facts. `origin/main` is on the server; main has two commits the server does not; `feature/maps` is
Meera's finished work. Confirm which commits are only local:

```text
$ git status
On branch main
Your branch is ahead of 'origin/main' by 2 commits.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
$ git log --oneline origin/main..main
f84bd85 Remove credentials
a0aa73b Add trekking tips
```

And what exactly is in them:

```text
$ git log --stat --format='%h %an: %s' origin/main..main
f84bd85 Ravi: Remove credentials

 credentials.json | 1 -
 1 file changed, 1 deletion(-)
a0aa73b Ravi: Add trekking tips

 credentials.json | 1 +
 tips.md          | 1 +
 2 files changed, 2 insertions(+)
```

There it is: `a0aa73b` added **both** the good `tips.md` and the bad `credentials.json`; `f84bd85` removed the file
again. `git log -- credentials.json` lists both commits. The file is gone from the folder, but not from history.
:::

:::step{type=concept title="Plan the rescue"}
Write the plan down before typing. Good engineers do this even for small jobs, because the order matters:

1. **What may I rewrite?** Only `a0aa73b` and `f84bd85`: they are not pushed. `72b9698` is on the server, so it must
   stay exactly as it is (chapter 7's rule).
2. **What should main look like afterwards?** The pushed commit, then **one** commit that adds `tips.md` and never
   contained `credentials.json`.
3. **Which tool does that?** Chapter 6's `git reset --soft`: move main back to `origin/main`, keeping the changes of
   the two local commits staged. Their **net** effect is just `tips.md`, because one added the credentials file and
   the other removed it. Then commit once. (An interactive rebase, chapter 11, squashing the two commits, gives the
   same result.)
4. **Then the release:** merge `feature/maps` into the clean main, tag the result as an annotated `v2.0`, and push
   main **and** the tag (chapter 13: tags are pushed separately).
5. **Check at every step:** `git log --oneline --graph --all --decorate`, and `git log -- credentials.json`, which
   must come back empty.

And one note for real life: a key that was ever pushed must be revoked. This one never left Ravi's laptop, so cleaning
history is enough.
:::

:::step{type=predict title="Guess first"}
:::question
After `git reset --soft origin/main`, what is staged?
:::
- [ ] Nothing
- [x] The combined result of the two local commits: just tips.md
- [ ] tips.md and credentials.json
:::explain
`--soft` moves the branch and keeps the end state staged. The two commits added and then removed `credentials.json`,
so only `tips.md` remains. `git status --short` will show `A  tips.md`.
:::
:::

:::step{type=task task=capstone_clean title="Your turn: clean the history"}
Rewrite **only the unpushed commits**, so that no commit on `main` ever contained `credentials.json`, while keeping
`tips.md` and the pushed commit exactly as they are.

Check your work: `git log -- credentials.json` prints nothing, `git log --oneline origin/main..main` shows your one
clean commit, and `tips.md` is still there. Do not push yet. Press **Check**.
:::

:::step{type=task task=capstone_release title="Your turn: release Trails 2.0"}
Now ship it:

1. Merge `feature/maps` into the clean `main`.
2. Tag the result as `v2.0`, annotated, with a message.
3. Push `main`, then push the tag.

`git ls-remote --tags origin` should list `v2.0`, and `git status` should say main is up to date with
`origin/main`. Press **Check**: it inspects the server.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why was it right to rewrite these two commits, when chapter 7 said not to rewrite history?
:::
- [x] They were not pushed: nobody else had them, so rewriting harmed nobody
- [ ] Secrets are an exception to every rule
- [ ] Because it was main
:::explain
The rule is about **shared** commits. Local commits are yours to tidy. Had they been pushed, the right moves would be
to revoke the key at once, then decide with the team whether to rewrite shared history.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You pushed main but your teammates cannot see `v2.0`. What did you forget?
:::
- [ ] To make the tag annotated
- [x] To push the tag: `git push origin v2.0`
- [ ] To merge the tag
:::explain
Tags travel only when you push them. One more line, and the release is visible to everyone.
:::
:::

:::step{type=deep-dive title="Go deeper: where to go from here"}
You now know the Git that most professional engineers use every day, and the parts that frighten many of them. Some
directions for later:

**Hosting platforms.** GitHub and GitLab add pull requests, code review, issues, CI pipelines and protected branches
on top of what you learned. Everything in this course carries over unchanged.

**Workflows.** "Trunk-based development" (short branches merged into main many times a day) and "Git flow" (separate
develop and release branches) are two common ways teams organise branches. Most modern teams lean towards short-lived
branches and frequent, small pull requests.

**Big repositories.** Partial clones (`git clone --filter=blob:none`), sparse checkouts and Git LFS (for big binary
files such as videos) keep huge projects fast.

**Signing.** `git commit -S` and `git tag -s` sign commits and tags with a key, so others can verify who really made
them.

**Your own projects.** The best way to keep this knowledge is to use it: put your next project in Git from the first
minute, commit small and often, write clear messages, and push to a remote. Your future self will thank you.
:::

:::step{type=recap}
You can now:

- diagnose a repository fully before acting: graph, status, `origin/main..main`, `log --stat`, `log -- file`;
- plan a rescue: what may be rewritten, what the result should be, which tool, which order;
- remove a leaked file from unpushed history while keeping pushed history and good work;
- release: merge a feature, tag it annotated, and push both the branch and the tag.

You have finished Git without fear: from your first commit to rescuing a messy repository and shipping a release.
Well done.

:::photo{src="/lesson-images/git/git-14-notes.webp" alt="Handwritten notes about the capstone: 1. diagnose: log --graph --all; 2. what is pushed? origin/main..main; 3. plan, then act; rewrite only local commits; merge, tag, push, release!" ai="true"}
One page of notes for this chapter.
:::
:::
