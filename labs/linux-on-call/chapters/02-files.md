:::step{type=story title="The downloads folder"}
Anjali has a confession: "The downloads folder on the server is a mess. Electricity bills for the dishes, photos of
the sky, a star chart, half-finished uploads. Could you tidy it? And before you change anything else, please make a
backup of the targets folder. If we lose that, we lose the plan for the whole month."

On a laptop you would drag files around with a mouse. On a server there is no mouse, and that turns out to be a
**strength**: one typed command can move a hundred files as easily as one, and the same command works on a folder of a
million files, where dragging would take a week.

Every letter this postwoman carried in London in 1941 had an address: a city, a street, a house. Follow it step by
step, and you reach exactly one door. A file on Linux has an address too, its **path**: folder, folder, file.

:::photo{src="/lesson-images/linux/postwoman.webp" alt="A smiling postwoman in uniform and hat holds out a letter, with a bundle of letters in her hand, in a London street in 1941" credit="Ministry of Information Photo Division" license="Public domain" source="https://commons.wikimedia.org/wiki/File:The_work_of_the_General_Post_Office,_London,_October_1941_D5279.jpg"}
A postwoman in London, 1941: every letter has an address.
:::

:::mission
Tidy the downloads folder with a few commands, and make an exact backup of the targets folder.
:::
:::

:::step{type=concept title="Make, copy, move, delete"}
Six commands do almost all the work with files and folders:

| Command | Does | Example |
|---|---|---|
| `mkdir` | makes a folder | `mkdir photos` |
| `touch` | makes an empty file (or updates its time) | `touch notes.txt` |
| `cp` | copies | `cp tonight.txt tonight-old.txt` |
| `mv` | moves, or renames (the same thing on Linux) | `mv draft.txt final.txt` |
| `rm` | removes a file | `rm upload.tmp` |
| `rmdir` | removes an **empty** folder | `rmdir old` |

`cp` and `mv` take the source first and the destination last. When the destination is a folder, the files go **into**
it, keeping their names: `mv a.txt b.txt photos/` moves both files into `photos`.

There is no recycle bin. **`rm` deletes for good**, at once, without asking. This is the single most important thing to
remember on a Linux server, and the reason experienced people pause for a second before pressing Enter on an `rm`.

Folders need one more word. These are real answers from Tara's server:

```text
$ mkdir scratch/a/b
mkdir: cannot create directory ‘scratch/a/b’: No such file or directory
$ mkdir -p scratch/a/b && tree scratch
scratch
└── a
    └── b

3 directories, 0 files
$ cp scratch scratch2
cp: -r not specified; omitting directory 'scratch'
$ rmdir scratch
rmdir: failed to remove 'scratch': Directory not empty
$ rm -r scratch && ls
downloads  targets
```

`mkdir -p` makes every missing folder on the way (p for parents). `cp -r` and `rm -r` work **recursively**: the folder,
everything in it, everything in those, all the way down. `rm -r` on the wrong folder is how people lose a day's work,
so read the line twice before you press Enter.

**Check yourself:** what does `mv old.txt new.txt` do when `new.txt` does not exist? (It renames `old.txt` to
`new.txt`. Moving and renaming are the same operation.)
:::

:::step{type=try title="Look at the mess"}
```text
$ cd /workspace/02-files
$ ls downloads
 cache-1.tmp              invoice-2026-11-12.pdf   sky-1.jpg  'star chart.pdf'
 cache-2.tmp              invoice-2026-11-18.pdf   sky-2.jpg   upload.tmp
 invoice-2026-11-03.pdf   invoice-2026-11-21.pdf   sky-3.jpg
 invoice-2026-11-07.pdf   notes.txt                sky-4.jpg
```

Fourteen files. Notice `'star chart.pdf'`: `ls` puts quotes around a name that contains a space, to show you where the
name starts and ends. Spaces in names are allowed, but every command needs to be told that the space is part of the
name, or it sees two names:

```text
$ ls downloads/star chart.pdf
ls: cannot access 'downloads/star': No such file or directory
ls: cannot access 'chart.pdf': No such file or directory
$ ls "downloads/star chart.pdf"
'downloads/star chart.pdf'
```

Quotes (or a backslash before the space: `star\ chart.pdf`) keep the name in one piece.
:::

:::step{type=concept title="Patterns: one command for many files"}
The shell has a small superpower called **globbing**: before running a command, it replaces a **pattern** with every
file name that matches it.

| Pattern | Matches |
|---|---|
| `*` | any characters, any number of them (even none) |
| `?` | exactly one character |
| `[abc]` | one of those characters |

```text
$ ls downloads/*.pdf
 downloads/invoice-2026-11-03.pdf   downloads/invoice-2026-11-18.pdf
 downloads/invoice-2026-11-07.pdf   downloads/invoice-2026-11-21.pdf
 downloads/invoice-2026-11-12.pdf  'downloads/star chart.pdf'
$ ls downloads/sky-?.jpg
downloads/sky-1.jpg  downloads/sky-2.jpg  downloads/sky-3.jpg  downloads/sky-4.jpg
```

The important part: `ls` never sees the `*`. The **shell** expands it first, then runs `ls` with six names. You can see
the expansion with `echo`, which just prints its arguments:

```text
$ echo downloads/*.tmp
downloads/cache-1.tmp downloads/cache-2.tmp downloads/upload.tmp
```

So `rm downloads/*.tmp` is really `rm` with three names. That is also why globbing is worth checking with `echo` or
`ls` first: what you see is exactly what the command will get. A glob handles names with spaces safely, too: each
matching name arrives in one piece.

:::diagram{name="linux-glob"}
The shell turns the pattern into the list of matching names, then runs the command with that list.
:::

One more: braces make several words from one pattern, whether or not the files exist:

```text
$ echo {tonight,this-week}.txt
tonight.txt this-week.txt
```

**Check yourself:** does `*.jpg` match a file called `.jpg-notes`? (No: a `*` never matches a leading dot, so
hidden files are left out, like with `ls`.)
:::

:::step{type=task task=tidy_folder title="Your turn: tidy the downloads"}
In `/workspace/02-files/downloads`:

1. Make two folders: `invoices` and `photos`.
2. Move every `.pdf` file into `invoices`, and every `.jpg` file into `photos`.
3. Delete every `.tmp` file.
4. Leave `notes.txt` where it is.

Three or four commands are enough; you do not need to type a single full file name. Check with `ls downloads` and
`ls downloads/*`. Press **Check**.
:::

:::step{type=example title="Worked example: copying a folder the right way"}
A backup is a copy, so `cp -r`. But copying folders has one surprise worth seeing once. Here the `targets` folder is
copied to `/tmp/t1` twice in a row:

```text
$ cp -r targets /tmp/t1 && ls /tmp/t1 && cp -r targets /tmp/t1 && ls /tmp/t1
special  this-week.txt  tonight.txt
special  targets  this-week.txt  tonight.txt
```

1. The first time, `/tmp/t1` did not exist, so `cp` **created** it as the copy: it holds `special`, `this-week.txt`
   and `tonight.txt`.
2. The second time, `/tmp/t1` already existed, so `cp` put the copy **inside** it, as `/tmp/t1/targets`.

Same command, two different results, depending on whether the destination exists. When you make a backup, make sure
the backup folder does not exist yet, then check the result with `tree` or `ls -R`:

```text
$ tree targets
targets
├── special
│   └── eclipse.txt
├── this-week.txt
└── tonight.txt

2 directories, 3 files
```

To compare a copy with its original, `diff -r targets COPY` prints nothing at all when they are the same.
:::

:::step{type=predict title="Guess first"}
:::question
You run `cp tonight.txt special/`. What happens?
:::
- [ ] `special` is replaced by a file called `special`
- [x] A copy of `tonight.txt` is placed inside the `special` folder
- [ ] An error: `cp` needs a file name as the destination
:::explain
When the destination is an existing folder, files go into it and keep their names. A trailing `/` makes your
intention clear, and gives an error if `special` is not a folder.
:::
:::

:::step{type=task task=backup_copy title="Your turn: back up the targets"}
In `/workspace/02-files`, make an exact copy of the `targets` folder, with everything inside it, called
`targets-backup`. The original `targets` must stay where it is.

`tree targets-backup` should look exactly like `tree targets`. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `rm downloads/*.tmp` delete three files, when `rm` was given only one argument?
:::
- [ ] `rm` understands `*`
- [x] The shell expanded `*.tmp` into three names before `rm` ran
- [ ] `rm` deletes everything similar to the name it gets
:::explain
Globbing is done by the shell. Every command gets the finished list of names. That is why `echo downloads/*.tmp` is a
safe way to preview what an `rm` will delete.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You deleted `notes.txt` with `rm` by mistake. How do you get it back?
:::
- [ ] From the recycle bin
- [ ] With `rm --undo`
- [x] You cannot, unless there is a copy somewhere (a backup, or version control)
:::explain
`rm` has no undo. That is why backups exist, and why the next habit is worth forming: `rm -i` asks before each file.
:::
:::

:::step{type=deep-dive title="Go deeper: safer habits, and what a file really is"}
**Ask first.** `-i` (interactive) makes `cp`, `mv` and `rm` ask before they overwrite or delete:

```text
$ rm -i downloads/upload.tmp
rm: remove regular file 'downloads/upload.tmp'?
```

Answer `y` or `n`. Many people make it a habit for `rm` on servers they care about.

**Extensions are only names.** On Linux, `.jpg` at the end of a name is a hint for people, not a rule. The `file`
command looks at what is really inside:

```text
$ file downloads/sky-1.jpg downloads/notes.txt
downloads/sky-1.jpg: ASCII text
downloads/notes.txt: ASCII text
```

These practice "photos" are really small text files. A real photo would say `JPEG image data`.

**Moving is instant, copying is not.** Within one disk, `mv` only changes the name in the folder's list, so moving a
10 GB file takes a millisecond. `cp` reads and writes every byte, so it takes as long as the disk needs.

**The dangerous one.** `rm -rf` means recursive and force (never ask, ignore missing files). It is useful and
dangerous. Never run it with a variable or a pattern you have not checked first; chapter 10 shows a famous accident.
:::

:::step{type=recap}
You can now:

- make folders (`mkdir -p`) and files (`touch`), copy (`cp`, `cp -r`), move and rename (`mv`), and delete (`rm`,
  `rm -r`, `rmdir`), remembering that `rm` has no undo;
- handle names with spaces using quotes;
- use patterns (`*`, `?`, `[...]`, `{a,b}`) to work on many files at once, and preview them with `echo`;
- copy a folder without the "copy inside the copy" surprise, and check it with `tree`.

Next, chapter 3: reading files that are far too long to read with your eyes.

:::photo{src="/lesson-images/linux/linux-02-notes.webp" alt="Handwritten notes about files and folders: mkdir -p, cp -r, mv, rm -r; rm has no undo!; *.pdf = every name ending .pdf; the shell expands * first; 'names with spaces' need quotes" ai="true"}
One page of notes for this chapter.
:::
:::
