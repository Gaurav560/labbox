:::step{type=story title="Permission denied"}
Anjali wrote a tiny script to greet new operators, `hello.sh`, and asked you to try it. You type `./hello.sh`, and the
server answers with two words every Linux user meets in their first week: **Permission denied**.

While you are there, you notice something worse. The **deploy key**, the private key that opens the archive server where
every night of sky data is stored, can be read by **every user on the machine**. Students log in to this server during
workshops. Any one of them could copy the key.

Linux was built from the start for many people sharing one computer, so every file carries a small set of rules: **who**
may **read** it, **write** it, and **run** it. Today you learn to read those rules and change them.

A bank's locker room works the same way: every box has an owner, and only the right key opens it. The bank's staff can
reach every room, but not the inside of your box.

:::photo{src="/lesson-images/linux/safe-deposit-boxes.webp" alt="A bank vault lined from floor to ceiling with numbered metal safe deposit boxes" credit="Asanagi" license="CC0" source="https://commons.wikimedia.org/wiki/File:Safe_deposit_boxes_in_Japan_2024-12-19.jpg"}
Safe deposit boxes: each one has its owner and its own key.
:::

:::mission
Make hello.sh a program you can run, and lock the deploy key so only you can read it.
:::
:::

:::step{type=concept title="Users, groups, and root"}
Every person (and every service) on Linux is a **user**, with a number, the **uid**. Users belong to **groups**, so
that a team can share files. `id` shows who you are:

```text
$ cd /workspace/07-permissions
$ whoami
learner
$ id
uid=1000(learner) gid=1000(learner) groups=1000(learner)
```

The list of users lives in `/etc/passwd` (it holds no passwords any more; the name stayed from the 1970s):

```text
$ grep learner /etc/passwd
learner:x:1000:1000:Ubuntu:/home/learner:/bin/bash
```

Name, `x` (the password is elsewhere), uid, group id, a description, the home folder, and the shell.

One user is special: **root**, uid 0, the administrator. Root may read, change and delete **anything**, and the rules you
are about to learn do not stop it. On real servers people do not log in as root; they use `sudo` ("do as the super
user") for the few commands that need it, so every powerful action is deliberate and logged. In this lab you are a normal
user, and the system shows you what that means:

```text
$ touch /etc/test.txt
touch: cannot touch '/etc/test.txt': Permission denied
$ ls /root
ls: cannot open directory '/root': Permission denied
```

That is the system protecting itself: a normal user cannot change system settings, or look into another user's home.
:::

:::step{type=concept title="Reading rwx"}
`ls -l` shows the rules at the start of every line:

```text
$ ls -l
total 4
-rw-r--r-- 1 learner learner 78 Nov 22 18:15 hello.sh
drwxr-xr-x 2 learner learner 80 Nov 22 18:15 keys
```

Read `-rw-r--r--` as one character, then three groups of three:

```text
-    rw-     r--     r--
type owner   group   others
```

| Letter | On a file | On a folder |
|---|---|---|
| `r` read | see what is inside | list the names in it |
| `w` write | change it | create, rename or delete files in it |
| `x` execute | run it as a program | enter it (`cd`) and reach the files in it |
| `-` | that permission is missing | |

The two names after the number are the **owner** (`learner`) and the **group** (`learner`). So `hello.sh`: the owner
may read and write it, everyone else may only read it. **Nobody** may run it: there is no `x`. That is the whole reason
for "Permission denied".

:::diagram{name="linux-permissions"}
Three groups of three: owner, group, others. Each permission is a number: r is 4, w is 2, x is 1.
:::

**Numbers.** Each group adds up to one digit: `r` = 4, `w` = 2, `x` = 1. So `rw-` is 6, `r-x` is 5, `rwx` is 7, `---`
is 0. Three digits describe the whole file:

| Mode | Letters | Typical use |
|---|---|---|
| `644` | `rw-r--r--` | ordinary files: you change, others read |
| `755` | `rwxr-xr-x` | programs and folders: you change, everyone runs or enters |
| `600` | `rw-------` | private files: keys, passwords |
| `700` | `rwx------` | private folders and scripts |

`stat` prints both forms:

```text
$ stat -c "%A %a %n" hello.sh keys keys/deploy-key.pem
-rw-r--r-- 644 hello.sh
drwxr-xr-x 755 keys
-rw-r--r-- 644 keys/deploy-key.pem
```

**Check yourself:** what does `640` mean? (Owner reads and writes, the group reads, others nothing: `rw-r-----`.)
:::

:::step{type=example title="Worked example: chmod, by letters and by numbers"}
`chmod` (change mode) changes the rules. You can give it **letters**: who (`u` owner, `g` group, `o` others, `a` all),
then `+` add, `-` remove or `=` set exactly, then which permissions. Or you can give it the **number**. Here both,
on a copy of the script in `/tmp`:

```text
$ cp hello.sh /tmp/h.sh; chmod u+x /tmp/h.sh; ls -l /tmp/h.sh; chmod go-r /tmp/h.sh; ls -l /tmp/h.sh; chmod 755 /tmp/h.sh; ls -l /tmp/h.sh; chmod 777 /tmp/h.sh; ls -l /tmp/h.sh
-rwxr--r-- 1 learner learner 78 Nov 22 18:21 /tmp/h.sh
-rwx------ 1 learner learner 78 Nov 22 18:21 /tmp/h.sh
-rwxr-xr-x 1 learner learner 78 Nov 22 18:21 /tmp/h.sh
-rwxrwxrwx 1 learner learner 78 Nov 22 18:21 /tmp/h.sh
```

1. `chmod u+x`: the owner may now run it.
2. `chmod go-r`: group and others lose read.
3. `chmod 755`: set all nine at once, the normal mode for a program.
4. `chmod 777`: everyone may do everything, **including change it**. Anyone on the machine could put their own commands
   inside your script, and the next person to run it runs them. Seeing `777` on a server is a warning sign. When
   something does not work, `chmod 777` is the "fix" that creates a security hole: find the one permission that is
   missing instead.

**Why `./hello.sh`?** To run a program, the shell searches a list of system folders (chapter 12). Your current folder is
not on that list, on purpose, so `./` says "the one right here". And `bash hello.sh` works even without `x`, because
then the program being run is `bash`, which simply reads the file:

```text
$ ./hello.sh
bash: ./hello.sh: Permission denied
$ bash hello.sh
Hello from the Tara Observatory server, learner!
```
:::

:::step{type=task task=make_executable title="Your turn: make hello.sh a program"}
In `/workspace/07-permissions`, make `hello.sh` executable, so that `./hello.sh` runs it. Everyone else may run it
too, but only you may change it.

`./hello.sh` should greet you by name. Press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
A folder has mode `600` (`rw-------`): you can read it, but not enter it. What happens with `ls` and `cat` inside it?
:::
- [ ] Both work: you own it
- [x] `ls` can list the names, but `cat` on a file inside fails
- [ ] Both fail
:::explain
On a folder, `r` lets you read its list of names, and `x` lets you reach the files in it. Without `x`, you see the
names but cannot open anything. Folders almost always need `x` together with `r`.
:::
:::

:::step{type=try title="See it for yourself"}
```text
$ mkdir /tmp/locked; echo hi > /tmp/locked/f; chmod 600 /tmp/locked; ls /tmp/locked; cat /tmp/locked/f; chmod 700 /tmp/locked
f
cat: /tmp/locked/f: Permission denied
```

`ls` listed the name `f`; `cat` could not reach it. With `chmod 700`, the folder is fully yours again.
:::

:::step{type=task task=private_key title="Your turn: lock the deploy key"}
In `/workspace/07-permissions/keys`:

1. Make `deploy-key.pem` readable and writable by **you only**: nothing at all for the group or others.
2. Make the `keys` folder yours only too: you may list it, enter it and change it; nobody else may do anything.

`ls -l keys` and `ls -ld keys` should show exactly that. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A script has mode `644`. What does `./script.sh` say?
:::
- [ ] It runs: 6 includes execute
- [x] Permission denied: 644 is rw-r--r--, with no x anywhere
- [ ] It runs only for the owner
:::explain
6 is 4 + 2, read and write. Execute is 1, so the owner would need 7 (`744` or `755`).
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A web app cannot write to its upload folder. A colleague suggests `chmod -R 777 /srv/app`. What is the better fix?
:::
- [ ] Do it: it fixes the problem
- [x] Find the user the app runs as, and give that user write permission on the upload folder only
- [ ] Run the app as root
:::explain
`777` lets every user change every file of the app, and root makes every bug a disaster. Grant the one missing
permission, to the one user that needs it, on the one folder.
:::
:::

:::step{type=deep-dive title="Go deeper: chown, umask, and the files the system protects"}
**Changing the owner.** `chown user:group file` changes who owns a file. Only root may do it: otherwise anyone could
give their files to someone else, or take someone else's.

```text
$ chown root hello.sh
chown: changing ownership of 'hello.sh': Operation not permitted
```

**Default permissions.** New files get `644` and new folders `755`, because of the **umask**, a mask of permissions to
leave out:

```text
$ umask
0022
$ touch /tmp/new.txt; mkdir /tmp/newdir; ls -ld /tmp/new.txt /tmp/newdir
-rw-r--r-- 1 learner learner    0 Nov 22 18:21 /tmp/new.txt
drwxr-xr-x 2 learner learner 4096 Nov 22 18:21 /tmp/newdir
```

`022` removes write for group and others. A server holding private data might use `077`, so new files start private.

**Passwords really are protected.** The real password hashes live in `/etc/shadow`, readable only by root and its group:

```text
$ ls -l /etc/shadow /etc/passwd
-rw-r--r-- 1 root root   890 Nov 18 15:53 /etc/passwd
-rw-r----- 1 root shadow 503 Nov 18 15:53 /etc/shadow
$ cat /etc/shadow
cat: /etc/shadow: Permission denied
```

**The sticky bit.** `/tmp` has mode `drwxrwxrwt`: everyone may create files there, but the `t` at the end means you may
only delete **your own**.

**Why ssh cares.** The `ssh` program refuses to use a private key that others can read, with an error like
"UNPROTECTED PRIVATE KEY FILE!". Many leaked keys started as one careless `644`.
:::

:::step{type=recap}
You can now:

- explain users, groups, uids and root, and why people use `sudo` instead of logging in as root;
- read `rwxr-xr-x` and its number `755`, on files and on folders;
- change permissions with `chmod` by letters (`u+x`, `go-r`) and by numbers (`644`, `755`, `600`, `700`);
- avoid `777`, and know why `./script.sh` needs `x` while `bash script.sh` does not.

Next, chapter 8: processes, the programs running right now, and how to stop one politely.

:::photo{src="/lesson-images/linux/linux-07-notes.webp" alt="Handwritten notes about permissions: rwx for owner, group, others; r=4 w=2 x=1; 755 programs, 644 files; 600 keys, 700 private folders; never chmod 777" ai="true"}
One page of notes for this chapter.
:::
:::
