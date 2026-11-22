:::step{type=story title="Small tools, joined together"}
Two small jobs today. The observatory's website build prints a wall of text, and somewhere in it are the problems that
matter; Anjali wants **only the problems**, in a file, to send to the person who looks after the website. And
`targets.txt` lists every target the dishes looked at last night, one line per session, with repeats; she wants a clean
list, **each target once**, in order.

There is no single Linux command for either job. There does not need to be. Linux gives you **small tools that each
do one thing**, and two simple ideas for joining them: **redirection** (sending output into a file) and **pipes**
(sending one tool's output straight into the next tool). Together they are the reason one line in a Linux terminal can
replace a whole program.

Pipes came from a 1964 note by **Doug McIlroy** at Bell Labs: "We should have some ways of coupling programs like a
garden hose: screw in another segment when it becomes necessary to massage data in another way." In 1973 Ken Thompson
added them to Unix, in one night. Oil and water have travelled the same way for a century: one long line, made of
sections joined end to end.

:::photo{src="/lesson-images/linux/pipeline.webp" alt="A long silver pipeline on supports runs across green land towards distant mountains, beside a marker post numbered 562" credit="Luca Galuzzi (Lucag)" license="CC BY-SA 2.5" source="https://commons.wikimedia.org/wiki/File:Trans-Alaska_Pipeline_System_Luca_Galuzzi_2005.jpg"}
The Trans-Alaska Pipeline: sections joined end to end.
:::

:::mission
Save only the build's problems into a file, and turn last night's targets into a sorted list with each target once.
:::
:::

:::step{type=concept title="Three streams for every program"}
Every program on Linux starts with three **streams** already open, numbered:

| Number | Name | Normally connected to | Used for |
|---|---|---|---|
| 0 | standard input (**stdin**) | the keyboard | what the program reads |
| 1 | standard output (**stdout**) | the screen | the results |
| 2 | standard error (**stderr**) | the screen | problems and warnings |

Results and problems go to the screen together, so they look like one stream. But they are two, and you can send them
to different places. **Redirection** does it:

| You type | Means |
|---|---|
| `cmd > file` | stdout into `file` (replaced if it exists) |
| `cmd >> file` | stdout added to the **end** of `file` |
| `cmd 2> file` | stderr into `file` |
| `cmd > file 2>&1` | both into `file` (`2>&1`: "send 2 where 1 is going") |
| `cmd < file` | `file` becomes stdin |
| `cmd > /dev/null` | throw stdout away (`/dev/null` swallows everything) |

:::diagram{name="linux-streams"}
A program has one way in (0) and two ways out (1 for results, 2 for problems). Redirection points each one somewhere new.
:::

Careful with `>`: it **empties the file first**. `>>` adds to the end:

```text
$ echo one > /tmp/x.txt; echo two >> /tmp/x.txt; cat /tmp/x.txt
one
two
$ echo three > /tmp/x.txt; cat /tmp/x.txt
three
```

**Check yourself:** you run `ls nope > out.txt`. The file does not exist, so `ls` complains. Is the complaint in
`out.txt`? (No: complaints go to stream 2, and only stream 1 was redirected. You see the message on the screen, and
`out.txt` is empty.)
:::

:::step{type=try title="Split the build's output"}
```text
$ cd /workspace/04-pipes
$ ./build.sh
Building target pages...
warning: photo crab-nebula.jpg is larger than 1 MB
Building sky pages...
error: tonight.html links to a missing chart orion.png
Packing photos...
error: about.html has no title
Build finished with 2 errors.
```

(`./build.sh` runs the program `build.sh` from this folder; chapter 7 explains the `./`.) Now send stdout into a
file, and see what is left on the screen:

```text
$ ./build.sh > /tmp/out.txt
warning: photo crab-nebula.jpg is larger than 1 MB
error: tonight.html links to a missing chart orion.png
error: about.html has no title
$ cat /tmp/out.txt
Building target pages...
Building sky pages...
Packing photos...
Build finished with 2 errors.
```

The progress lines went into the file; the problems stayed on the screen, because they travel on stream 2. The build
was written the right way: results on 1, problems on 2.
:::

:::step{type=task task=errors_only title="Your turn: only the problems"}
In `/workspace/04-pipes`, run `./build.sh` so that **only its problems** (the warning and the two errors) are saved in
a file called `errors.txt`. The progress lines must not be in it; they can go to the screen, or to `/dev/null`.

`cat errors.txt` should show exactly three lines. Press **Check**.
:::

:::step{type=concept title="Pipes: one tool's output is the next tool's input"}
A **pipe**, written `|`, connects stdout of the command on its left to stdin of the command on its right. No file in
between; the data flows straight through, a line at a time.

```text
$ grep ERROR ../03-reading-files/app.log | wc -l
23
```

`grep ERROR` keeps the lines that contain ERROR (chapter 5 is all about it), and `wc -l` counts what arrives. Two small
tools, one new answer: 23 errors last night.

Three more tools make pipes powerful:

| Tool | Does |
|---|---|
| `sort` | puts lines in order (`-n` by number, `-r` reversed) |
| `uniq` | removes repeated lines **that sit next to each other** (`-c` counts them) |
| `cut -d, -f3` | keeps one column (`-f3`, the third) of lines split by a character (`-d,`, a comma) |

`uniq` only looks at neighbours. That is why the classic pattern is **sort first, then uniq**:

```text
$ wc -l targets.txt
64 targets.txt
$ uniq targets.txt | wc -l
58
```

Without sorting, `uniq` only removed the six repeats that happened to be next to each other.

:::diagram{name="linux-pipe"}
Each command reads the stream from the one before it and passes its result to the next. No files in between.
:::

**Check yourself:** what does `sort targets.txt | head -1` print? (The first target in alphabetical order:
`Andromeda Galaxy`.)
:::

:::step{type=example title="Worked example: the most observed targets"}
Here is a pipeline built one piece at a time, the way engineers really build them: run, look, add the next piece.

```text
$ sort targets.txt | head -5
Andromeda Galaxy
Andromeda Galaxy
Andromeda Galaxy
Andromeda Galaxy
Andromeda Galaxy
$ sort targets.txt | uniq -c
      8 Andromeda Galaxy
      7 Crab Nebula
      4 Cygnus A
     12 Jupiter
      7 Moon
      7 Orion Nebula
      2 Pleiades
     11 Saturn
      6 Vela Pulsar
$ sort targets.txt | uniq -c | sort -rn | head -3
     12 Jupiter
     11 Saturn
      8 Andromeda Galaxy
```

1. `sort` puts equal lines next to each other.
2. `uniq -c` squeezes each group into one line, with its count in front.
3. `sort -rn` sorts those lines by the number, biggest first; `head -3` keeps the top three.

**Sort, count, sort by count, take the top**: remember this shape. It answers "what happens most?" for any list:
busiest IP addresses, most common errors, most observed targets. It works the same on 64 lines or 64 million.

The same idea on the CSV from chapter 3, with `cut` taking the target column and `tail -n +2` skipping the header:

```text
$ cut -d, -f3 ../03-reading-files/observations.csv | tail -n +2 | sort | uniq -c | sort -rn | head -3
    149 Andromeda Galaxy
    147 Vela Pulsar
    146 Saturn
```
:::

:::step{type=predict title="Guess first"}
:::question
What does `sort targets.txt | uniq | wc -l` print?
:::
- [ ] 64, the number of lines in the file
- [x] 9, the number of different targets
- [ ] 58
:::explain
After sorting, every repeat is next to its twin, so `uniq` leaves one of each: 9 different targets. `sort -u` does
sort and uniq in one step.
:::
:::

:::step{type=task task=target_list title="Your turn: each target once"}
In `/workspace/04-pipes`, make `tonight-targets.txt`: every target from `targets.txt`, **each one once**, in
alphabetical order, one per line.

`cat tonight-targets.txt` should show 9 lines, starting with `Andromeda Galaxy`. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which line saves both the results and the problems of `./build.sh` into `all.txt`?
:::
- [ ] `./build.sh > all.txt`
- [ ] `./build.sh 2> all.txt`
- [x] `./build.sh > all.txt 2>&1`
:::explain
`> all.txt` points stream 1 at the file, then `2>&1` points stream 2 at the same place as stream 1. The order matters:
`2>&1 > all.txt` would point stream 2 at the screen (where 1 was at that moment), then move only 1.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does `uniq` give a wrong answer on a file that is not sorted?
:::
- [ ] It only reads the first 10 lines
- [x] It only removes repeats that sit next to each other
- [ ] It sorts the file in the wrong order
:::explain
`uniq` compares each line with the one just before it. That makes it fast and light on memory, and it is why `sort`
comes first.
:::
:::

:::step{type=deep-dive title="Go deeper: exit codes, tee, and the Unix philosophy"}
**Exit codes.** Every command also ends with a number, its **exit code**: `0` means success, anything else means
failure. The shell keeps the last one in `$?`:

```text
$ ./build.sh > /dev/null; echo "exit code: $?"
warning: photo crab-nebula.jpg is larger than 1 MB
error: tonight.html links to a missing chart orion.png
error: about.html has no title
exit code: 1
```

The build failed, and said so twice: with its messages, for people, and with its exit code, for scripts. Chapter 10
builds on this.

**tee**, a T-junction in a pipe: it writes what passes through into a file **and** passes it on:

```text
$ sort targets.txt | uniq | tee /tmp/t.txt | wc -l
9
```

The 9 targets went into `/tmp/t.txt`, and `wc` still counted them.

**The Unix philosophy**, as Doug McIlroy summed it up: write programs that do one thing and do it well; write programs
to work together; write programs to handle text streams, because that is a universal interface. Fifty years later it is
still how Linux, and much of modern software, is built.

**Speed.** In a pipeline all the commands run **at the same time**: `sort` is reading while `cut` is still cutting. On
a machine with several processor cores, a long pipeline uses several of them at once, without you doing anything.
:::

:::step{type=recap}
You can now:

- name the three streams (stdin 0, stdout 1, stderr 2), and redirect them with `>`, `>>`, `2>`, `2>&1`, `<` and
  `/dev/null`;
- join commands with pipes `|`, and use `sort`, `uniq`, `uniq -c`, `cut` and `tee` in them;
- build the "sort, count, sort by count, take the top" pipeline, one piece at a time;
- read a command's exit code with `$?`.

Next, chapter 5: reading a real web server's logs with `grep` and `awk`, and three tools for the next incident.

:::photo{src="/lesson-images/linux/linux-04-notes.webp" alt="Handwritten notes about pipes and redirection: 0 in, 1 results, 2 problems; > file, >> file, 2> errors.txt; cmd > all.txt 2>&1; sort | uniq -c | sort -rn; exit code 0 = success" ai="true"}
One page of notes for this chapter.
:::
:::
