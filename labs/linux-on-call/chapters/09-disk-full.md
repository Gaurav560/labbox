:::step{type=story title="No space left on device"}
Three in the morning, and the alert is short: **disk 100% full**. The dishes keep listening, but the program that saves
their recordings cannot write a single byte. Every minute of sky that is not saved is lost for good: tonight's Crab
Nebula will not come back until next year.

Someone switched on **debug logging** last week, to chase a bug, and forgot to switch it off. Debug logs write a line
for every tiny step, and one log file has quietly grown until it filled the disk. And while you are in there, Anjali
adds: "The deploy scripts stopped running after the last copy, and I think the secrets file is open to everyone again."

When a disk fills up, Linux programs all fail in the same way, with the same words. You can see them without filling a
real disk: `/dev/full` is a special file that always answers "full":

```text
$ echo "capture 1" > /dev/full
bash: echo: write error: No space left on device
```

The first hard disk ever sold, IBM's 350 in 1956, was the size of two refrigerators and held 3.75 megabytes. The debug
log in this chapter would have filled a sixth of it. Disks have grown a million times bigger since; logs grew with them.

:::photo{src="/lesson-images/linux/ibm-350.webp" alt="The disk mechanism of the IBM 350: a tall stack of metal platters inside its frame, in a museum case" credit="ArnoldReinhold" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:IBM_350_RAMAC_disk_mechanism.agr.jpg"}
Inside the IBM 350, the first hard disk, 1956: a stack of fifty metal platters.
:::

:::mission
Get the disk space back without stopping the program that holds the log, then fix the server's permissions for good.
:::
:::

:::step{type=concept title="Finding what fills the disk"}
Two commands answer the two questions of every full disk.

**How full is each disk?** `df` (disk free), with `-h` for human sizes:

```text
$ df -h /workspace | head -2
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           7.5G  779M  6.7G  11% /workspace
```

On a real server, `df -h` alone lists every disk; you look for the one near `100%`.

**What is using it?** `du` (disk usage), going down one level at a time, biggest last with `sort -h` (which understands
`K`, `M` and `G`):

```text
$ cd /workspace/09-disk-full
$ du -sh server/* | sort -h
8.0K    server/bin
8.0K    server/config
632K    server/var
$ du -sh server/var/log/app/*
8.0K    server/var/log/app/access.log
4.0K    server/var/log/app/app.log
620K    server/var/log/app/debug.log
```

Three steps from "the disk is full" to "it is `debug.log`". On a real server it is the same walk from `/`, just longer:
`du -sh /* | sort -h`, then into the biggest, and again. The tool `ncdu` does the walk interactively.

```text
$ head -2 server/var/log/app/debug.log
2026-11-19T00:00:00 DEBUG cache probe key=frame:16631 hit=yes took=6us
2026-11-19T00:00:01 DEBUG cache probe key=frame:76229 hit=no took=9us
```

A line for every cache lookup, every second, all night: that is debug logging.
:::

:::step{type=concept title="The trap: deleting a file that is still open"}
The obvious fix is `rm debug.log`. On a running server it is the wrong one, and the reason is worth understanding.

A file's **name** and its **data** are separate. The name is just an entry in a folder pointing at the data. When a
program opens a file, it holds on to the data directly. `rm` removes the **name**; the kernel frees the data only when
**no name and no open program** points at it any more.

Here is that happening, with a 48 MB file held open by a small program in the background:

```text
$ head -c 50000000 /dev/zero > /tmp/big.log; (exec 3>>/tmp/big.log; sleep 30) & sleep 0.5; du -h /tmp/big.log; rm /tmp/big.log; ls /tmp/big.log; lsof +L1 2>/dev/null; kill %1
[1] 22
48M     /tmp/big.log
ls: cannot access '/tmp/big.log': No such file or directory
COMMAND PID    USER   FD   TYPE DEVICE SIZE/OFF NLINK    NODE NAME
sleep    22 learner    3w   REG  0,101 50000000     0 7878551 /tmp/big.log (deleted)
```

1. The file is 48 MB, and a program (PID 22) has it open for writing.
2. `rm` removed the name: `ls` cannot find it.
3. But `lsof +L1` (list open files with no name left) shows the data is still there, all 50,000,000 bytes,
   `(deleted)`, held by PID 22. The disk space is **not** back, and the program keeps writing into a file nobody can
   see.

:::diagram{name="linux-open-file"}
rm removes the name. The data stays on disk while a program still holds the file open.
:::

The right fix keeps the same file and empties it: **`truncate -s 0 file`** (set its size to zero). The program keeps
writing into the same file, now from the start, and the space is free at once:

```text
$ head -c 1000 /dev/zero > /tmp/t.log; (exec 3>>/tmp/t.log; sleep 30) & sleep 0.3; truncate -s 0 /tmp/t.log; ls -l /tmp/t.log; kill %1
[1] 2619
-rw-r--r-- 1 learner learner 0 Nov 22 18:23 /tmp/t.log
```

(`> file`, a redirection with no command, empties a file the same way.)

**Check yourself:** after `rm` on an open 10 GB log, `df` still says the disk is full. What frees the space? (Ending
or restarting the program that holds it open; or, better next time, emptying the file instead of deleting it.)
:::

:::step{type=predict title="Guess first"}
:::question
`debug.log` is still open in the running app. Which command frees its space **and** keeps the app writing happily?
:::
- [ ] `rm server/var/log/app/debug.log`
- [x] `truncate -s 0 server/var/log/app/debug.log`
- [ ] `mv server/var/log/app/debug.log /tmp/`
:::explain
`rm` removes only the name, and `mv` within a disk only renames it: the app holds the same data either way. `truncate`
empties the file itself.
:::
:::

:::step{type=task task=free_disk title="Your turn: free the disk"}
In `/workspace/09-disk-full/server/var/log/app`, one log is far bigger than the others. **Empty it** (zero bytes)
**without deleting it**, and leave the other logs exactly as they are.

`ls -l server/var/log/app` should show `debug.log` at 0 bytes. Press **Check**.
:::

:::step{type=example title="Worked example: from symptom to root cause"}
Emptying the log buys time. A good engineer also stops it happening again tomorrow. The root cause is in the settings:

```text
$ cat server/config/app.env
LOG_LEVEL=debug
PORT=8080
```

`LOG_LEVEL=debug` is the switch someone forgot. Setting it back to `info` (and restarting the app) ends the flood.

Then the long-term fix: **log rotation**. A tool called `logrotate` runs every night and, for each log, renames it
(`app.log` becomes `app.log.1`), compresses old ones (`app.log.2.gz`), deletes the oldest, and tells the program to start
a new file. Its rule for a log looks like this:

```text
/var/log/tara/*.log {
    daily
    rotate 14
    compress
    missingok
    copytruncate
}
```

Daily, keep 14, compress the old ones. `copytruncate` copies the log and then empties it in place, exactly what you
just did by hand, for programs that cannot be told to reopen their file.

**What it costs.** Disk space itself is cheap: cloud disks cost around 8 US cents per GB a month, so even 60 GB of
debug logs costs a few dollars. The real cost is the outage when the disk fills: lost data, failed orders, a lost night
of observations. That is why teams alert at 80 percent full, long before 100.
:::

:::step{type=concept title="The other half: permissions after a careless copy"}
Now Anjali's second problem. Files copied carelessly (an archive unpacked by hand, a sync from another machine) often
lose their permissions:

```text
$ ls -l server/bin server/config
server/bin:
total 8
-rw-r--r-- 1 learner learner 136 Nov 22 18:15 deploy.sh
-rw-r--r-- 1 learner learner 121 Nov 22 18:15 rotate-logs.sh

server/config:
total 8
-rw-r--r-- 1 learner learner  26 Nov 22 18:15 app.env
-rw-r--r-- 1 learner learner 105 Nov 22 18:15 secrets.env
```

Two problems from chapter 7: the scripts in `bin` have no `x`, so they cannot run, and `secrets.env` can be read by
everyone. This happens after every careless copy, so the fix belongs in a **script** that anyone can run on any server
folder:

```text
$ cat fix_perms.sh
#!/usr/bin/env bash
# fix_perms.sh DIR: fix the permissions of a server folder.
#   - every .sh file in DIR/bin must be executable
#   - DIR/config/secrets.env must be readable and writable by its owner only
# TODO (task fix_perms): your commands here. The server folder is "$1".
```

Use `"$1"` for the folder (so `"$1"/bin/*.sh` is every script in its `bin`, whatever their names), and `chmod` with the
modes from chapter 7.
:::

:::step{type=task task=fix_perms title="Your turn: fix_perms.sh"}
Finish `fix_perms.sh` in `/workspace/09-disk-full`, so that `bash fix_perms.sh server` makes every `.sh` file in
`server/bin` executable and `server/config/secrets.env` readable and writable by its owner only.

The check runs it on a fresh copy of the folder, with a script name you have not seen, so use a pattern, not names.
Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`df -h` says the disk is 100% full, but `du -sh /` adds up to much less. What is the likely reason?
:::
- [ ] du cannot count big files
- [x] Deleted files are still held open by running programs; du only sees files that have names
- [ ] df is wrong
:::explain
df asks the disk how much is used; du adds up the files it can find by name. The difference is very often deleted but
still open files. `lsof +L1` lists them, and restarting the program that holds them frees the space.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What stops tomorrow's disk from filling up the same way?
:::
- [ ] Emptying the log again every night by hand
- [x] Turning debug logging off, and rotating logs automatically with logrotate
- [ ] A bigger disk
:::explain
A bigger disk only delays the same outage. Fix the cause (the log level), and let rotation keep every log to a known
size.
:::
:::

:::step{type=deep-dive title="Go deeper: inodes, journald, and space reserved for root"}
**Inodes.** The data of a file is described by an **inode** (index node), and a folder entry is a name pointing at an
inode. A disk has a fixed number of inodes, so a disk can also be "full" with millions of tiny files while bytes are
still free: `df -i` shows inodes.

**Hard links.** Two names can point at the same inode (`ln file other`). The data is freed only when the last name and
the last open program let go, which is the same rule that made the deleted log stay.

**Space for root.** Ext4 disks keep about 5 percent for root by default, so the system and its administrator can still
work when users have filled the disk. That is why a normal user can hit "No space left" while `df` shows a little free.

**systemd's journal.** Services managed by systemd log to the journal (`journalctl`, chapter 14), which has a size limit
of its own (`SystemMaxUse` in `/etc/systemd/journald.conf`), so it rotates itself.
:::

:::step{type=recap}
You can now:

- find what fills a disk: `df -h` for each disk, then `du -sh * | sort -h` down the tree;
- explain why deleting an open file does not free its space, and find such files with `lsof +L1`;
- empty a live log safely with `truncate -s 0` (or `> file`);
- fix the cause (the log level) and prevent it with logrotate, and fix permissions with a reusable script.

Next, chapter 10: shell scripts that check their inputs and stop when something fails.

:::photo{src="/lesson-images/linux/linux-09-notes.webp" alt="Handwritten notes about disk full: df -h, then du -sh * | sort -h; rm on an open file frees nothing; truncate -s 0 file; lsof +L1 finds deleted files; fix the cause: log level, logrotate" ai="true"}
One page of notes for this chapter.
:::
:::
