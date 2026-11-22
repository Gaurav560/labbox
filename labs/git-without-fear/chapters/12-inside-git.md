:::step{type=story title="How can Git be so sure?"}
You have used Git for eleven chapters, and it has done some remarkable things. It knew instantly that a file was
unchanged across a hundred commits. It found a "lost" commit weeks later. It guaranteed that the history on your
laptop and on the server are the same, down to the last character. How?

There is no magic, and the explanation is beautiful. Inside the `.git` folder, everything is made of just **three
kinds of object**, each named by a fingerprint of its own content. Once you see them, Git stops being a list of
commands to memorise and becomes a small, simple machine you understand.

This chapter opens `.git` and looks at real objects with Git's own low-level commands. Nothing here can break
anything: these commands only read.

:::mission
Find the tree of the last commit, and the blob that holds `trails.md`, by following the objects yourself.
:::
:::

:::step{type=concept title="Three kinds of object, named by their content"}
Everything Git stores is an **object**, and there are three kinds that matter:

| Object | Holds | Like |
|---|---|---|
| **blob** | the content of one file, nothing else (not even its name) | the text on a page |
| **tree** | a list of names, each pointing at a blob (a file) or another tree (a folder) | a folder's table of contents |
| **commit** | one tree (the whole folder at that moment), the parent commit(s), the author, the date and the message | the photo, with its caption |

And every object's name is its **hash**: a 40-character fingerprint computed from its content with an algorithm
called SHA-1. The same content always gives the same hash; change one character, and the hash is completely
different. That one idea explains a great deal:

- **Unchanged files cost nothing.** A file that did not change has the same content, so the same blob; a new commit
  just points at the existing blob again.
- **Corruption cannot hide.** If a single bit of an object changed on disk, its content would no longer match its
  name, and Git would notice.
- **A commit's hash covers its whole history.** A commit contains its tree's hash and its parent's hash, which
  contains its parent's, and so on. Change anything anywhere in the past, and every hash after it changes. This
  chain of hashes is called a **Merkle tree**, after the computer scientist Ralph Merkle.

A hash works like a fingerprint: tiny compared with the thing it identifies, different for every one, and easy to check at any time.

:::photo{src="/lesson-images/git/fingerprint-card.webp" alt="A fingerprint record card with rows of black inked fingerprints, lying on a laptop keyboard" credit="cogdogblog" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:2013-365-17_Printed_(8390841733).jpg"}
A fingerprint card.
:::

:::diagram{name="git-objects"}
A commit points at a tree and its parent; a tree points at blobs and other trees; every name is a hash of the content.
:::

**Check yourself:** two different files in your project have exactly the same content. How many blobs does Git
store? (One: same content, same hash, same blob.)
:::

:::step{type=example title="Worked example: from a commit down to a file"}
Here is a tiny scratch repository (only to read): one commit with `tips.md` and a folder `maps/`. Git's low-level
command `git cat-file` shows objects: `-t` gives an object's type, `-p` prints it.

Start at the commit:

```text
$ git rev-parse HEAD
746dd3138e1a84f05248caa661923fecebfd75ea
$ git cat-file -t HEAD
commit
$ git cat-file -p HEAD
tree a3666ce84827a4149ba47b4e21d868825dd816c1
author Asha <asha@trails.example> 1795149000 +0530
committer Asha <asha@trails.example> 1795149000 +0530

Add tips and a map
```

That is the **entire** commit: a tree hash, the author and committer with the time in seconds since 1970 and the
time zone, and the message. (This is the first commit, so it has no `parent` line; later commits have one, and
merges have two.) Follow the tree:

```text
$ git cat-file -p HEAD^{tree}
040000 tree acb9c3aabc74cb378feafe167408bee1e7613f90	maps
100644 blob 6f8a202ee7bdc27279aee35b1621e59a7bc2097c	tips.md
```

The tree lists the folder: `maps` is another **tree** (a subfolder), `tips.md` is a **blob** (a file), each with its
hash. `HEAD^{tree}` means "the tree of the commit HEAD"; you could also paste the tree's hash. Now the blob:

```text
$ git cat-file -p $(git rev-parse HEAD:tips.md)
Start early.
```

Just the file's content. `HEAD:tips.md` means "the file tips.md in the commit HEAD", and `git rev-parse` turns it into
its hash.

Commit, tree, blob: three objects, three hashes, and you have walked from a commit to a file's content by hand.
:::

:::step{type=predict title="Guess first"}
:::question
A blob holds a file's content. Where is the file's **name** stored?
:::
- [ ] In the blob
- [x] In the tree that points at the blob
- [ ] In the commit message
:::explain
Names live in trees. That is why renaming a file without changing it reuses the same blob: only the tree changes.
:::
:::

:::step{type=task task=tree_hash title="Your turn: the tree of the last commit"}
In `/workspace/12-inside-git/trails`, look at the last commit with `git cat-file -p HEAD`, and find the hash of its
**tree**.

Write it (at least the first 7 characters) into `answer-tree.txt`, **next to** the trails folder:

```bash
echo HASH > /workspace/12-inside-git/answer-tree.txt
```

Careful: the commit's own hash is a different one. Press **Check**.
:::

:::step{type=try title="Compute a hash yourself"}
The best proof that the name **is** the content: compute a blob's hash with an ordinary tool. Git hashes the word
`blob`, a space, the content's length in bytes, a zero byte, then the content. In the scratch repository:

```text
$ git hash-object tips.md
6f8a202ee7bdc27279aee35b1621e59a7bc2097c
$ printf 'blob 13\0Start early.\n' | sha1sum
6f8a202ee7bdc27279aee35b1621e59a7bc2097c  -
```

`git hash-object` computes the hash a file would have as a blob. `sha1sum`, a standard Linux tool that knows nothing
about Git, gives exactly the same 40 characters from `blob 13`, the zero byte (`\0`), and the 13 bytes of
`Start early.` plus its newline. Anyone, anywhere, with the same content gets the same name.

And here are all the objects of that tiny repository, as files on disk:

```text
$ find .git/objects -type f | sort
.git/objects/6f/8a202ee7bdc27279aee35b1621e59a7bc2097c
.git/objects/74/6dd3138e1a84f05248caa661923fecebfd75ea
.git/objects/a3/666ce84827a4149ba47b4e21d868825dd816c1
.git/objects/ac/b9c3aabc74cb378feafe167408bee1e7613f90
.git/objects/c9/084086dfa9b7f70428d471d2b8572149e55e69
```

Five objects: the commit (`74...`), two trees (`a3...` and `ac...`), and two blobs (`6f...` for tips.md, and `c9...`
for the map). Each is stored under its hash, split into a two-character folder and the rest. A branch, by the way, is
just a file holding a commit's hash: `cat .git/refs/heads/main` prints `746dd3138e...`. Now you know everything a
branch is.
:::

:::step{type=task task=blob_hash title="Your turn: the blob of trails.md"}
In the same repository, list the last commit's tree with `git cat-file -p` and the tree's hash (or `HEAD^{tree}`),
and find the hash on the `trails.md` line.

Write it into `answer-blob.txt`, next to the trails folder. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does every commit after a change to an old commit get a new hash?
:::
- [ ] Git renames them on purpose
- [x] Each commit contains its parent's hash, so a change anywhere changes every hash after it
- [ ] Hashes are random
:::explain
The chain of hashes is what makes history tamper-evident, and it is also why rewriting history (amend, rebase) always
produces new commits.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You rename `tips.md` to `advice.md` without changing its content, and commit. Which new objects does Git create?
:::
- [ ] A new blob, a new tree and a new commit
- [x] A new tree and a new commit; the blob is the same
- [ ] Only a new commit
:::explain
The content did not change, so the blob (named by its content) is reused. The name changed, so the tree is new, and
so is the commit pointing at it.
:::
:::

:::step{type=deep-dive title="Go deeper: packs, SHA-256, and the index"}
**Packfiles.** Storing every version of every file whole would waste space. Now and then (and when you push or
fetch), Git compresses objects into **packfiles**, storing similar objects as small differences from each other.
`git count-objects -v` shows how much is loose and how much is packed. The objects are still blobs, trees and
commits; only their storage is clever.

**SHA-1 and SHA-256.** In 2017 researchers showed a practical way to make two different files with the same SHA-1
hash. Git added protection against that attack, and newer versions can create repositories with SHA-256 names
(`git init --object-format=sha256`), while most of the world still uses SHA-1 repositories.

**The index.** The staging area from chapter 2 is a real file, `.git/index`: a list of paths, each with the blob hash
it will have in the next commit. `git ls-files --stage` prints it. `git add` writes blobs and updates the index; `git
commit` turns the index into trees and a commit.

**Tags as objects.** An annotated tag (chapter 13) is a fourth kind of object: a name, a tagger, a message and a
pointer to a commit.
:::

:::step{type=recap}
You can now:

- explain Git's three objects: blobs (content), trees (names and folders), commits (a tree, parents and a message);
- explain why naming objects by their hash makes Git fast, compact and tamper-evident;
- walk from a commit to a file with `git cat-file -t` and `-p`, `HEAD^{tree}` and `HEAD:path`;
- compute a blob's hash with `git hash-object`, and see that a branch is a file holding one hash.

That completes Part 3. Next, Part 4: good habits, then the capstone.

:::photo{src="/lesson-images/git/git-12-notes.webp" alt="Handwritten notes about inside .git: blob = content; tree = names and folders; commit = tree + parent + message; name = hash of the content; git cat-file -p HEAD" ai="true"}
One page of notes for this chapter.
:::
:::
