:::step{type=story title="final_v2_REAL_fixed.docx"}
You have probably seen a folder like this, or made one:

```text
trails.md
trails_old.md
trails_v2.md
trails_v2_asha_edits.md
trails_FINAL.md
trails_FINAL_really.md
```

Which one is the latest? What changed between v2 and FINAL? Who deleted the Kalsubai section, and when? If you
email a copy to a friend and both of you edit it, how do you put the two versions back together?

Every team that writes anything together runs into these questions. Programmers met them first, at enormous scale:
the Linux kernel has had tens of thousands of contributors. The tool they built to answer them is called **Git**,
and today almost every piece of software in the world is made with it.

In this course you will look after **Trails**, a small website about treks in the Sahyadri hills near Pune and
Mumbai, written by three friends: Asha, Ravi and Meera. You will save its versions, read its history, work on
branches, settle arguments between versions, undo mistakes without panic, and work together through a server, the
way real teams do.

Rajmachi, the first trail on the site, is a pair of old hill forts above Lonavala, a favourite trek for people from Pune and Mumbai. Every trail on Trails is a place like this one.

:::photo{src="/lesson-images/git/rajmachi-fort.webp" alt="The stone ruins of a hill fort on a rocky ridge above deep green valleys, with misty hills behind" credit="Rohit Nair" license="CC0" source="https://commons.wikimedia.org/wiki/File:Rajmachi_Fort_(153460031).jpeg"}
Rajmachi fort, in the Sahyadri hills.
:::

:::mission
Turn the Trails folder into a Git repository, and save its first version with your first commit.
:::
:::

:::step{type=concept title="What version control does"}
**Version control** is a system that remembers every version of a set of files, with **who** changed **what**,
**when**, and **why**. **Git** is the version control system almost everyone uses today.

Three ideas carry the whole course, so meet them now in plain words:

1. A **repository** (or **repo**) is a folder that Git is looking after. Git keeps its memory in a hidden folder
   inside it, called `.git`.
2. A **commit** is a saved version of the whole folder, like a photo of every file at one moment, with a message
   saying why. Commits are never changed; new ones are added after them.
3. The **history** is the chain of commits, each pointing at the one before it. You can look at any of them,
   compare any two, and go back to any one.

The difference from the folder of `_FINAL_really` files: there is **one** `trails.md`, always the current one, and
Git holds every earlier version behind it, labelled and in order. Nothing is lost, and nothing is confusing.

:::diagram{name="git-three-areas"}
Files move from your working folder, to the staging area with git add, into history with git commit.
:::

**Check yourself:** if a commit is a photo of the whole folder, what does the history look like? (A line of photos,
oldest to newest, each with a caption saying what changed and why.)
:::

:::step{type=history title="The story of Git"}
Git was written in about ten days, by the person who had written Linux, because he had suddenly lost the tool
he depended on.

:::before{title="Before Git"}
Early tools kept versions of single files (RCS, 1982). CVS (late 1980s) and then Subversion (2000) kept a whole
project on a **central server**: you had to be connected to it to see history or save a version, and if the server
broke, everybody stopped. Merging two people's work was so painful that many teams avoided branches entirely. The
Linux kernel used none of these: from 2002 it used **BitKeeper**, a commercial tool whose company let open-source
projects use it for free.
:::

In April 2005 that free licence was withdrawn. **Linus Torvalds**, Linux's creator, decided to write his own tool,
with three goals: fast, impossible to corrupt silently, and good at merging many people's work. He started on 3
April 2005, and within a few days Git was managing its own source code. In July 2005 he handed it over to **Junio
Hamano**, who has maintained it ever since.

This is Linus Torvalds in January 2003, two years before he wrote Git, at a Linux conference in Perth, Australia.

:::photo{src="/lesson-images/git/linus-torvalds.webp" alt="A young Linus Torvalds, smiling broadly, in a white polo shirt under a gum tree" credit="Alex Dawson (photo), Bff (crop)" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Linus_Torvalds,_2002,_Australian_Linux_conference2.jpg"}
Linus Torvalds in 2003, aged 33.
:::

:::solved
**Every copy is a full copy.** With Git, every developer has the **whole** history on their own machine. Saving,
browsing history and branching are instant and work offline; a server is just one more copy, used for sharing.
Branches and merges became cheap and everyday, and every version is identified by a fingerprint of its content, so
corruption can never go unnoticed.
:::

:::timeline
- **2005** Linus Torvalds writes Git in April; Junio Hamano takes over in July; Git 1.0 in December.
- **2008** GitHub opens: hosting Git repositories with pull requests and a friendly website.
- **2011** GitLab starts as an open-source alternative.
- **2017** Microsoft moves the whole Windows source code to Git.
:::

Git is free software, developed by a community of volunteers and companies, led by Junio Hamano.

:::usedby{title="Used for"}
- All kinds of software
- Websites and documentation
- Configuration of servers
- Data science notebooks
- Books and research papers
:::

:::usedby{title="Used by"}
- The Linux kernel
- Windows
- Android
- Almost every software team
:::

:::funfact
Why "git"? In British slang a git is an unpleasant person. Linus joked that he names all his projects after
himself, first Linux, then git. The very first README called it "the information manager from hell".
:::
:::

:::step{type=try title="Make a folder a repository"}
Open a terminal and look at the Trails folder. It has two files, and Git does not know about it yet:

```text
$ cd /workspace/01-why-version-control/trails
$ ls -a
.
..
README.md
trails.md
$ git status
fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).
```

`git status` is the command you will type more than any other: "what is the state of things?". Here it answers that
this is not a repository at all. `git init` makes it one:

```text
$ git init
Initialized empty Git repository in /workspace/01-why-version-control/trails/.git/
$ ls -a
.
..
.git
README.md
trails.md
```

A new hidden folder, `.git`, appeared. That folder **is** the repository: Git's whole memory lives there. Your
files did not change at all. (Delete `.git`, and the folder is an ordinary folder again, with its history gone. You
will look inside it in chapter 12.)
:::

:::step{type=task task=first_repo title="Your turn: make Trails a repository"}
In `/workspace/01-why-version-control/trails`, turn the folder into a Git repository. Then run `git status` and read
what it says now. Press **Check**.
:::

:::step{type=example title="Worked example: the first commit, step by step"}
Saving a version is two steps, and the reason is worth knowing. Right after `git init`, `git status` says:

```text
$ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	README.md
	trails.md

nothing added to commit but untracked files present (use "git add" to track)
```

**Untracked** means Git sees the files but has never been told to look after them. Step one, `git add`, puts files
in the **staging area**: the list of what will go into the next commit.

```text
$ git add README.md trails.md
$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   README.md
	new file:   trails.md
```

Step two, `git commit`, saves everything staged as one commit. `-m` gives the message, which says why:

```text
$ git commit -m 'Add the README and the first two trails'
[main (root-commit) 0f2529f] Add the README and the first two trails
 2 files changed, 14 insertions(+)
 create mode 100644 README.md
 create mode 100644 trails.md
```

Read that answer:

1. `main` is the branch you are on (chapter 4); `root-commit` means the very first one.
2. `0f2529f` is the start of the commit's **hash**, its unique name (yours will be different).
3. Two files, 14 lines added.

Why two steps? Because you often change several files but want to save them as separate, meaningful commits.
The staging area lets you choose exactly what goes into each one (chapter 2).
:::

:::step{type=predict title="Guess first"}
:::question
You edit `trails.md` and run `git commit -m "Fix a typo"` without `git add`. What happens?
:::
- [ ] The change is committed
- [x] Nothing is committed: the change was never staged
- [ ] Git stages it for you and commits
:::explain
A commit saves what is **staged**. An unstaged change stays only in your folder, and Git says "no changes added to
commit". `git status` would have told you.
:::
:::

:::step{type=task task=first_commit title="Your turn: the first commit"}
Save the first version of Trails: stage **both** files, then commit them with a message that says what they are.
Then look at your history:

```bash
git log
```

You will see your commit with its full hash, the author (you are set up as `Learner`), the date and the message.
Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does Git keep all the history of a repository?
:::
- [ ] On a server on the internet
- [x] In the hidden `.git` folder inside the repository
- [ ] In each file
:::explain
Everything is in `.git`. A server, when you use one, is just another full copy (chapter 9).
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `git add` do?
:::
- [ ] It saves a new version
- [x] It puts changes in the staging area, ready for the next commit
- [ ] It adds a file to the server
:::explain
`add` chooses; `commit` saves. Nothing is in the history until you commit.
:::
:::

:::step{type=deep-dive title="Go deeper: who you are, and what a commit really holds"}
**Your identity.** Every commit records an author name and email. On a new machine you set them once:
`git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`. This lab has
done it for you (`git config user.name` shows `Learner`). On a shared server, the email is how your commits are
linked to your account.

**A commit holds the whole folder, not a diff.** It looks as if Git stores changes, because `git show` displays
them. Internally each commit points at a complete snapshot, and Git stores every file version only once, by its
content, so an unchanged file costs nothing in the next commit. Chapter 12 shows the real objects.

**`git init` versus `git clone`.** `init` makes a new, empty repository; `clone` copies an existing one, history
and all, usually from a server (chapter 9).
:::

:::step{type=recap}
You can now:

- explain what version control is: every version, with who, what, when and why;
- tell the story of Git: BitKeeper, Linus Torvalds in 2005, Junio Hamano, and every copy a full copy;
- turn a folder into a repository with `git init`, and read `git status`;
- make a commit in two steps, `git add` then `git commit -m`, and look at it with `git log`.

Next, chapter 2: commits in depth, and choosing exactly what goes into each one.

:::photo{src="/lesson-images/git/git-01-notes.webp" alt="Handwritten notes about why Git?: every version: who, what, when, why; Linus Torvalds, April 2005; every copy is a full copy; git init makes a repository; git add, then git commit -m" ai="true"}
One page of notes for this chapter.
:::
:::
