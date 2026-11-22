:::step{type=story title="Somewhere on this server"}
Two worries from Anjali this morning. The server's disk is filling up faster than it should, and she would like to
know which files are big. And an auditor from the university asked a sharp question: "Is any password written in plain
text anywhere on your server?" Anjali thinks not. The previous engineer, who left in 2024, may have thought differently.

The server has thousands of folders. Opening them one by one is not a plan. Linux has two search tools that every
engineer uses daily: **find**, which searches for **files** by their name, size, age or type, and **grep -r**, which
searches **inside** files for a piece of text.

Before computers, libraries kept a card for every book in drawers like these, sorted so that any book could be found in
a minute among millions. `find` and `grep` are those drawers for a server, except that you never have to fill them in.

:::photo{src="/lesson-images/linux/card-catalogue.webp" alt="Rows of small wooden drawers of a library card catalogue, each with a brass handle and a label holder" credit="Mark Buckawicki" license="CC0" source="https://commons.wikimedia.org/wiki/File:Wooden_Card_Catalog_Furniture.jpg"}
A library card catalogue.
:::

:::mission
List every file bigger than 1 MB, and find the forgotten password before the auditor does.
:::
:::

:::step{type=concept title="find: search by name, type, size and age"}
`find` walks a folder and everything under it, and prints every path that passes your tests:

```text
find WHERE TESTS...
```

```text
$ cd /workspace/06-finding
$ find server -name "*.py"
server/app/main.py
server/app/handlers/alerts.py
server/app/handlers/captures.py
server/app/handlers/dishes.py
server/app/handlers/targets.py
```

Five Python files, in three different folders, found without opening any of them. Put quotes around the pattern:
here `find` needs the `*` itself, so the shell must not expand it first.

| Test | Keeps | Example |
|---|---|---|
| `-name "*.log"` | names matching a pattern | `find server -name "*.log"` |
| `-iname "*.env"` | the same, ignoring case | `find server -iname "*.ENV"` |
| `-type f` / `-type d` | only files / only folders | `find server -type d` |
| `-size +1M` | bigger than 1 MB (`k` for KB, `G` for GB) | `find / -size +1G` |
| `-mtime -7` | changed in the last 7 days (`+30`: more than 30 days ago) | `find logs -mtime +30` |

Tests add up: every test must pass. `find server -type f -name "*.log"` means "files, and named *.log":

```text
$ find server -name "*.log" | sort
server/logs/app-2026-11-19.log
server/logs/app-2026-11-20.log
server/logs/app-2026-11-21.log
server/logs/app-2026-11-22.log
server/logs/app-2026-11-23.log
server/logs/archive/app-2026-10.log
$ find server -type f | wc -l
20
```

**Check yourself:** how would you list every folder under `server`? (`find server -type d`.)
:::

:::step{type=try title="How is the space used?"}
Before hunting single files, see which folders are heavy. `du` (disk usage) with `-s` (one total per folder) and `-h`
(human sizes):

```text
$ du -sh server/*
24K     server/app
3.0M    server/backups
8.0K    server/config
904K    server/data
2.1M    server/logs
1.6M    server/static
```

`backups`, `logs` and `static` hold almost everything. On a real server you would run `du -sh /*` first, then go down
into the biggest folder, then the biggest one inside that, and so on: a few steps from "the disk is full" to the exact
file. Chapter 9 does exactly that, on a disk that really is full.
:::

:::step{type=task task=find_big title="Your turn: the big files"}
In `/workspace/06-finding`, use `find` to list every **file** under `server` that is **bigger than 1 MB**, and save the
list into `big-files.txt`, one path per line.

Careful: one file is a little under 1 MB, and does not belong in the list. Press **Check**.
:::

:::step{type=concept title="grep -r: search inside every file"}
`find` looks at files from the outside. To look **inside** them, give `grep` the option `-r` (recursive) and a folder
instead of a file:

```text
$ grep -r PORT server
server/config/app.env:PORT=8080
$ grep -rn "INFO" server/logs | head -3
server/logs/app-2026-11-23.log:1:2026-11-23 INFO night started
server/logs/app-2026-11-22.log:1:2026-11-22 INFO night started
server/logs/app-2026-11-21.log:1:2026-11-21 INFO night started
```

Each answer starts with the file's path, then a colon, then the matching line. With `-n` the line number sits between
them. And with `-l`, grep prints only the **names** of the files that match, once each:

```text
$ grep -rl tara server
server/config/database.env
server/app/legacy/settings.old.conf
```

The options from chapter 5 still work: `-i` ignores case, `-v` inverts, `-c` counts per file. And quote the text you
search for when it has spaces or symbols in it.
:::

:::step{type=example title="Worked example: find, then act on what you found"}
Finding is half the job. `find` can also run a command on everything it finds, with `-exec`. Here, the big files with
their sizes:

```text
$ find server -type f -size +1M -exec ls -lh {} \;
-rw-r--r-- 1 learner learner 1.5M Nov 22 18:15 server/static/images/milky-way.jpg
-rw-r--r-- 1 learner learner 3.0M Nov 22 18:15 server/backups/db-2026-11-22.sql.gz
-rw-r--r-- 1 learner learner 2.0M Nov 22 18:15 server/logs/archive/app-2026-10.log
```

1. `-exec ls -lh {} \;` runs `ls -lh` once for every file found; `{}` is replaced by the file's path, and `\;` marks
   the end of the command.
2. With `+` instead of `\;`, find gives **all** the paths to one command, which is much faster with many files:
   `find server -name "app-*.log" -exec wc -l {} +`.

The other way to do the same is `xargs`, which turns lines of input into arguments for a command:

```text
$ find server -name '*.py' | xargs wc -l
  1 server/app/main.py
  2 server/app/handlers/alerts.py
  2 server/app/handlers/captures.py
  2 server/app/handlers/dishes.py
  2 server/app/handlers/targets.py
  9 total
```

The pattern is the same as with pipes: one tool finds, another acts. On a real server, `find /var/log -name "*.log"
-mtime +30 -delete` is a classic: delete logs older than a month. **Run it without `-delete` first** and read the list.
:::

:::step{type=predict title="Guess first"}
:::question
`grep -r DB_PASSWORD server` would also match a line like `DB_PASSWORD_FILE=/run/secrets/db`. Why?
:::
- [ ] Because -r ignores the end of the word
- [x] Because grep looks for the text anywhere in the line, and DB_PASSWORD is part of DB_PASSWORD_FILE
- [ ] It would not match it
:::explain
grep matches text, not words. Searching for `DB_PASSWORD=`, with the equals sign, finds only lines where a password
itself is set. (`-w` makes grep match whole words only.)
:::
:::

:::step{type=task task=find_secret title="Your turn: the forgotten password"}
Somewhere under `server` a file still has a real database password in it, on a line that starts with `DB_PASSWORD=`.
Find the file.

Write its path (as grep shows it, for example `server/...`) into `answer-secret.txt` in `/workspace/06-finding`.
Careful: another file has a line that looks similar but holds no password. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `find server -name "*.log"` need the quotes?
:::
- [x] Without them the shell might expand `*.log` itself, using the files in the current folder, before find runs
- [ ] find only reads text in quotes
- [ ] The quotes make the search case-insensitive
:::explain
Quotes stop the shell from globbing, so find receives the pattern and applies it at every level of the tree.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the difference between `find server -name "*.env"` and `grep -r "PORT" server`?
:::
- [ ] There is none
- [x] find matches file names and properties; grep -r matches text inside the files
- [ ] grep -r is the faster find
:::explain
find never opens a file; it checks names, sizes, types and dates. grep -r opens every file and reads it line by line.
Together they answer almost any "where is it?" question.
:::
:::

:::step{type=deep-dive title="Go deeper: secrets, sizes and speed"}
**Passwords in files are a real danger.** Forgotten credentials in old config files, backups and code are one of the most
common ways servers get broken into. Teams run scanners that grep for patterns of keys and passwords on every change.
When you find one, the fix is not only deleting the file: the password must be **changed**, because you cannot know who
already copied it.

**find's sizes round up.** `-size -1M` means "less than 1 MB", but find first rounds every size **up** to whole
megabytes, so a 900 KB file counts as 1 MB and is not "less than 1":

```text
$ find server -type f -size +500k -size -1M
$ ls -lh server/data
total 904K
-rw-r--r-- 1 learner learner 900K Nov 22 18:15 cache.bin
-rw-r--r-- 1 learner learner   45 Nov 22 18:15 dishes.csv
```

The first command found nothing, although `cache.bin` is 900 KB. Use kilobytes for precise ranges: `-size -1024k`.

**Speed.** `find /` on a big server walks millions of files and can take minutes; always start from the smallest folder
you can. `locate` answers in a blink by searching a database of names built every night (it may be a day old). For
searching code, `ripgrep` (`rg`) is a much faster grep -r that skips files you would not want anyway.

**Errors you can ignore.** Searching folders you may not read prints "Permission denied" lines. Send them away with
`2>/dev/null` (chapter 4): `find / -name "*.conf" 2>/dev/null`.
:::

:::step{type=recap}
You can now:

- find files by name, type, size and age with `find`, and combine tests;
- see which folders take the space with `du -sh`;
- search inside every file of a folder with `grep -r`, `-n` and `-l`, and search for exact text like `DB_PASSWORD=`;
- act on what you found with `-exec` and `xargs`, previewing before anything destructive.

Next, chapter 7: who may read, change and run each file, and why it matters.

:::photo{src="/lesson-images/linux/linux-06-notes.webp" alt="Handwritten notes about finding things: find server -name '*.log'; -type f -size +1M; du -sh * | sort -h; grep -rl 'DB_PASSWORD=' .; preview before -delete" ai="true"}
One page of notes for this chapter.
:::
:::
