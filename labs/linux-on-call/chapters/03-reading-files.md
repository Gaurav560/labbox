:::step{type=story title="Too long to read"}
Every night Tara writes two files. `observations.csv` lists every observation: which dish, which target, for how long,
and how strong the signal was. `app.log` is the diary of the program that drives the dishes: one line for everything it
does, all night.

Anjali needs two answers before the morning meeting: how many observations are in the file, and what happened at the
very end of the night. Opening the files and scrolling would take an hour, and you would still lose count.

In 1967 a young astronomer, **Jocelyn Bell Burnell**, did read her telescope's output by eye: about 30 metres of paper
chart, every day. In it she noticed a tiny, regular "bit of scruff" that turned out to be the first **pulsar** ever
found, a spinning dead star. It was one of the great discoveries of the century, and it took months of careful reading.
On a Linux server, the same kind of question takes one command.

:::photo{src="/lesson-images/linux/jocelyn-bell-burnell.webp" alt="A young Jocelyn Bell Burnell in 1967, with curly hair and dark glasses, smiling at the camera" credit="Roger W Haworth" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Susan_Jocelyn_Bell_(Burnell),_1967.jpg"}
Jocelyn Bell Burnell in 1967, the year she found the first pulsar.
:::

:::mission
Count the night's observations without opening the file, and save the last 20 lines of the log.
:::
:::

:::step{type=concept title="Five ways to look inside a file"}
`cat` prints a whole file. That is perfect for a short file and terrible for a long one: 1,249 lines fly past and only
the last screenful stays. Linux has a tool for each way of looking:

| Command | Shows | Use it for |
|---|---|---|
| `cat file` | the whole file | short files |
| `head file` | the first 10 lines (`-n 5` for 5) | what the file looks like, its header |
| `tail file` | the last 10 lines (`-n 20` for 20) | the newest lines of a log |
| `less file` | one screen at a time, to scroll and search | reading a long file |
| `wc file` | counts: lines, words, bytes | how big is it? |

```text
$ cd /workspace/03-reading-files
$ head -5 observations.csv
obs_id,dish,target,minutes,signal
10001,dish-1,Sun,10,weak
10002,dish-3,Cygnus A,60,strong
10003,dish-3,Crab Nebula,30,weak
10004,dish-3,Saturn,10,good
$ tail -n 4 app.log
2026-11-24 05:56:32 INFO  capture=20596 dish moved to target
2026-11-24 05:57:39 INFO  capture=20597 calibration done
2026-11-24 05:58:46 INFO  capture=20598 dish moved to target
2026-11-24 05:59:53 INFO  capture=20599 capture saved
```

The first line of `observations.csv` is special: it is the **header**, the names of the columns. A `.csv` file
(comma-separated values) is a table written as text, one row per line, columns separated by commas.

**less**, the one you will use most on real servers, opens a file of any size instantly, because it only reads what
fits on the screen. Inside it: **space** for the next page, **b** to go back, **/word** then Enter to search, **n** for
the next match, **G** for the end, **g** for the start, **q** to quit. Try `less app.log` now, search for `/ERROR`, and
press `q` when you are done.

**Check yourself:** which command shows the first line of a file, and only that? (`head -n 1 file`, or `head -1 file`.)
:::

:::step{type=try title="How big is it?"}
`wc` (word count) counts lines, words and bytes:

```text
$ wc observations.csv
 1249  1951 39549 observations.csv
$ wc -l observations.csv app.log
 1249 observations.csv
  600 app.log
 1849 total
```

1,249 lines, 1,951 words, 39,549 bytes. `-l` asks for lines only. Notice the file's name is repeated in the answer.
When you want **just the number** (to save it, or to use it in a calculation), give `wc` the file through `<`, so it
never learns the name:

```text
$ wc -l < observations.csv
1249
```

`ls -lh` shows sizes in a human-friendly way (`-h` for human):

```text
$ ls -lh
total 76K
-rw-r--r-- 1 learner learner 34K Nov 22 18:15 app.log
-rw-r--r-- 1 learner learner 39K Nov 22 18:15 observations.csv
```
:::

:::step{type=predict title="Guess first"}
:::question
`wc -l observations.csv` says 1249. How many **observations** are in the file?
:::
- [ ] 1249
- [x] 1248
- [ ] 1250
:::explain
Every line is counted, including the header line with the column names. One line is not an observation.
:::
:::

:::step{type=task task=count_observations title="Your turn: count the observations"}
How many observations did Tara record? Write **just the number** into `answer-observations.txt` in
`/workspace/03-reading-files`. Careful with the header. Press **Check**.
:::

:::step{type=example title="Worked example: reading a log like an engineer"}
A log is read from the end, because the newest lines are at the bottom, and from the middle when you know what you
are looking for. Here is the start of last night's log, then a look at line numbers, then any lines you like:

```text
$ head -3 app.log
2026-11-23 20:00:00 INFO  capture=20000 data copied to archive
2026-11-23 20:01:07 INFO  capture=20001 calibration done
2026-11-23 20:02:14 INFO  capture=20002 data copied to archive
$ cat -n observations.csv | head -3
     1  obs_id,dish,target,minutes,signal
     2  10001,dish-1,Sun,10,weak
     3  10002,dish-3,Cygnus A,60,strong
$ sed -n "500,502p" observations.csv
10499,dish-3,Vela Pulsar,10,weak
10500,dish-1,Pleiades,5,good
10501,dish-1,Sun,30,weak
```

1. Every log line starts with the date and time, then a **level**: `INFO` (all is well), `WARN` (worth a look),
   `ERROR` (something failed). That shape is the same on almost every server.
2. `cat -n` numbers the lines. Handy when someone says "look at line 500".
3. `sed -n "500,502p"` prints only lines 500 to 502. (`sed` can do much more; this one use is worth remembering.)

And the most useful of all on a live server: **`tail -f app.log`** (follow) shows the last lines, then **keeps
waiting** and prints each new line the moment it is written. You watch the log live while you test something; `Ctrl+C`
stops it. Engineers keep a `tail -f` open in one terminal during almost every incident.
:::

:::step{type=task task=last_lines title="Your turn: the end of the night"}
Anjali wants the end of the night on her desk. Save the **last 20 lines** of `app.log` into a new file called
`recent.log`, in `/workspace/03-reading-files`.

`wc -l recent.log` should say 20, and `head -1 recent.log` should be a line from about 5:40 in the morning. Press
**Check**.
:::

:::step{type=concept title="Help when you need it: man pages"}
Nobody remembers every option of every command. Professionals look things up, all the time, with **man** (manual):

```text
$ man wc | sed -n "1,12p"
WC(1)                                     User Commands                                     WC(1)

NAME
       wc - print newline, word, and byte counts for each file

SYNOPSIS
       wc [OPTION]... [FILE]...
       wc [OPTION]... --files0-from=F

DESCRIPTION
       Print newline, word, and byte counts for each FILE, and a total line if more than one FILE
       is  specified.   A word is a non-zero-length sequence of printable characters delimited by
```

Every man page has the same parts: **NAME** (one line), **SYNOPSIS** (how to call it: `[...]` means optional, `...`
means "as many as you like"), **DESCRIPTION** and the options, and at the end **EXAMPLES** on many pages. A man page
opens in `less`, so `/word` searches it and `q` leaves.

Don't know the command's name? `man -k` searches the one-line descriptions:

```text
$ man -k "last part"
tail (1)             - output the last part of files
```

**Check yourself:** in a synopsis, what does `[FILE]...` tell you? (A file name is optional, and you may give
several.)
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A log file is 4 GB. Which command opens it fastest?
:::
- [ ] `cat app.log`
- [x] `less app.log`
- [ ] Opening it in a text editor
:::explain
`less` reads only the part on the screen, so it opens instantly whatever the size. `cat` would print all 4 GB, and an
editor would try to load all of it into memory first.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You want to watch new lines arrive in `app.log` while the dishes move. Which command?
:::
- [ ] `tail app.log`
- [x] `tail -f app.log`
- [ ] `head -f app.log`
:::explain
`-f` (follow) keeps the file open and prints each new line as it is written. `Ctrl+C` stops it.
:::
:::

:::step{type=deep-dive title="Go deeper: text, bytes and very big files"}
**Everything is text.** Linux's tools work on lines of text, which is why logs, settings and data like CSV are kept as
text: every tool can read every file. Binary files (photos, programs) need special tools; `cat` on one prints garbage,
and can confuse the terminal. If that happens, type `reset` and press Enter.

**Lines end with a newline.** A line is the text up to a newline character. That is what `wc -l` counts, and why a
file whose last line has no newline at the end counts one line less than you expect.

**Speed.** `head` and `tail` are fast on any size: `tail` jumps straight to the end of the file instead of reading it
all. `wc -l` reads the whole file, but at hundreds of megabytes a second. Counting the lines of a 4 GB log takes a few
seconds; scrolling it by hand would take a lifetime.

**Compressed logs.** Old logs are often kept compressed, as `app.log.1.gz`. `zcat`, `zless` and `zgrep` read them
without unpacking them first.
:::

:::step{type=recap}
You can now:

- choose the right way to look: `cat` (short), `head` and `tail` (start and end), `less` (long, with search);
- count lines, words and bytes with `wc`, and get just the number with `wc -l < file`;
- read a log from the end, number lines with `cat -n`, print a range with `sed -n`, and follow it live with `tail -f`;
- find help with `man`, `man -k` and `--help`, and read a synopsis.

Next, chapter 4: pipes, the idea that makes Linux's small tools add up to big ones.

:::photo{src="/lesson-images/linux/linux-03-notes.webp" alt="Handwritten notes about reading files: head, tail -n 20, less; wc -l < file: just the number; the header is not a row; tail -f: watch it live; man wc, then q" ai="true"}
One page of notes for this chapter.
:::
:::
