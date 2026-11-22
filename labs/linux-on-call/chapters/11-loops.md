:::step{type=story title="Twelve photos, then twelve thousand"}
Tara's all-sky camera takes a photo of the whole sky every night, to record the clouds. It names them the way cameras
do: `IMG_0001.JPG`, `IMG_0002.JPG`... Anjali wants them named for what they are, `sky-0001.jpg`, before they go on the
website. Twelve photos you could rename by hand in a few minutes. But the camera has been running for three years. That
is about a thousand photos, and next year's will make two thousand.

She also wants a small daily report: for each night, how many captures the dishes made. The data is there, one file per
night.

Both jobs are the **same small action, repeated**. That is what loops are for: write the action once, and let the shell
repeat it for every file, whether there are twelve or twelve thousand.

The idea is older than computers. In 1804 Joseph Marie Jacquard built a loom that wove patterns from a chain of punched
cards: one card per row of the fabric, read again and again in a loop. Engineers who later built the first computers
borrowed his punched cards.

:::photo{src="/lesson-images/linux/jacquard-loom.webp" alt="A wooden Jacquard loom with its long chain of punched cards hanging beside the threads" credit="Stephencdickson" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:A_Jacquard_loom_showing_information_punchcards,_National_Museum_of_Scotland.jpg"}
A Jacquard loom and its chain of punched cards.
:::

:::mission
Rename every sky photo with one loop, and write a report script that counts the captures of every night.
:::
:::

:::step{type=concept title="for: once for each item"}
A `for` loop runs the same commands once for each item in a list, with the item in a variable:

```text
$ cd /workspace/11-loops
$ for t in Jupiter Saturn "Crab Nebula"; do echo "Pointing at $t"; done
Pointing at Jupiter
Pointing at Saturn
Pointing at Crab Nebula
```

Read it as: **for** each `t` **in** this list, **do** these commands, **done**. Written over several lines in a
script, it looks like this:

```bash
for t in Jupiter Saturn "Crab Nebula"; do
  echo "Pointing at $t"
done
```

The list is usually a **glob** from chapter 2, so the loop runs once per matching file, in alphabetical order:

```text
$ for f in captures/*.csv; do echo "$f has $(wc -l < "$f") lines"; done
captures/captures-2026-11-17.csv has 213 lines
captures/captures-2026-11-18.csv has 199 lines
captures/captures-2026-11-19.csv has 241 lines
captures/captures-2026-11-20.csv has 252 lines
captures/captures-2026-11-21.csv has 306 lines
captures/captures-2026-11-22.csv has 188 lines
```

Six nights, one line of code. Notice the quotes around `"$f"` inside the loop: if a file name ever has a space in it,
the loop still works.

:::diagram{name="linux-for-loop"}
The glob makes the list; the body runs once for each name, with the name in the variable.
:::

For a range of numbers, `seq` or braces make the list: `for i in $(seq 1 3)`, or `for i in {1..3}`.

**Check yourself:** what does `for f in *.log; do echo "$f"; done` print in a folder with `a.log` and `b.log`? (Two
lines: `a.log`, then `b.log`.)
:::

:::step{type=concept title="Cutting names apart"}
To rename, you need pieces of a name: the number from `IMG_0007.JPG`, the date from `captures-2026-11-17.csv`. The
shell can cut text from the front and the back of a variable:

| Write | Means | `f=photos/IMG_0007.JPG` gives |
|---|---|---|
| `${f#text}` | remove `text` from the **front** | `${f#photos/}` is `IMG_0007.JPG` |
| `${f%text}` | remove `text` from the **end** | `${f%.JPG}` is `photos/IMG_0007` |

```text
$ f=photos/IMG_0007.JPG; echo "${f#photos/}"; echo "${f%.JPG}"; n=${f#photos/IMG_}; echo "$n"; echo "${n%.JPG}"
IMG_0007.JPG
photos/IMG_0007
0007.JPG
0007
```

Two cuts, one from each end, leave just `0007`. (Remember `#` is on the left of `$` on a keyboard and `%` on the
right: `#` cuts the left, `%` the right.)

`basename` and `dirname` do the folder part for you, and `basename` can drop an ending too:

```text
$ basename captures/captures-2026-11-17.csv .csv; dirname captures/captures-2026-11-17.csv
captures-2026-11-17
captures
```
:::

:::step{type=example title="Worked example: rename safely, with a dry run first"}
Renaming many files with a loop is powerful, and one typo can scramble all of them. So professionals do a **dry run**
first: the same loop, with `echo` in front of the dangerous command, so it prints what it **would** do. Here, renaming
the capture files to `night-DATE.csv`:

```text
$ for f in captures/*.csv; do echo mv "$f" "captures/night-${f#captures/captures-}"; done | head -3
mv captures/captures-2026-11-17.csv captures/night-2026-11-17.csv
mv captures/captures-2026-11-18.csv captures/night-2026-11-18.csv
mv captures/captures-2026-11-19.csv captures/night-2026-11-19.csv
```

1. The glob gives each file in turn.
2. `${f#captures/captures-}` cuts the folder and the old prefix, leaving `2026-11-17.csv`.
3. `echo mv ...` only **prints** the command. Nothing was renamed.

Read the output. Every line right? Then remove the `echo`, run it again, and it happens for real. (Do not run it for
real here: the report task needs these names.) The same habit works for `rm`, `cp` and `chmod` in loops.
:::

:::step{type=task task=rename_photos title="Your turn: rename the sky photos"}
In `/workspace/11-loops/photos`, rename every photo from `IMG_0001.JPG` to `sky-0001.jpg`: same number, a `sky-`
prefix, and a lowercase `.jpg`.

Use one loop (a dry run with `echo` first is a good idea). `ls photos` should end up showing `sky-0001.jpg` to
`sky-0012.jpg`. Press **Check**.
:::

:::step{type=concept title="while, read and functions"}
A `while` loop repeats **as long as** a command succeeds:

```text
$ count=0; while [ $count -lt 3 ]; do count=$((count + 1)); echo "try $count"; done
try 1
try 2
try 3
```

Its most common use is reading a file **line by line**, with `read`:

```text
$ while read -r line; do echo "-> $line"; done < ../01-why-linux/tara/observations/2026/november/23/plan.txt
-> First target tonight: Crab Nebula
-> Then: Orion Nebula, Jupiter
```

(`-r` keeps backslashes as they are; always use it.) Unlike `for line in $(cat file)`, which splits on every space,
`while read` gives you whole lines.

A **function** names a few lines so you can use them again, with arguments like a script:

```text
$ greet() { echo "Hello, $1"; }; greet Anjali; greet operator
Hello, Anjali
Hello, operator
```

And `case` picks one branch by matching a value against patterns, tidier than many `elif`s:

```text
$ case "dish-2" in dish-1) echo one;; dish-2) echo two;; *) echo other;; esac
two
```
:::

:::step{type=predict title="Guess first"}
:::question
A night file has 213 lines, and its first line is the header `capture_id,dish,target`. What should the report print
for that night?
:::
- [ ] 213
- [x] 212
- [ ] 214
:::explain
The header is not a capture, so one less than the line count: `$((lines - 1))`. Same lesson as chapter 3, now inside a
loop.
:::
:::

:::step{type=task task=daily_report title="Your turn: report.sh"}
Finish `report.sh` in `/workspace/11-loops`. Given a folder as `"$1"`, it prints one line for every file
`captures-YYYY-MM-DD.csv` in it, oldest first:

```text
2026-11-17 212
```

the date, a space, and the number of captures (lines minus the header). Ignore any other files in the folder.

`bash report.sh captures` should print six lines. The check runs it on a folder it makes itself. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why run a renaming loop with `echo` in front of `mv` first?
:::
- [ ] echo makes mv faster
- [x] It prints every command the loop would run, so you can check them before anything changes
- [ ] mv needs echo to work inside a loop
:::explain
A dry run costs one second and catches the typo that would otherwise rename a thousand files wrongly.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`n=IMG_0042.JPG`. What is `${n#IMG_}`?
:::
- [x] `0042.JPG`
- [ ] `IMG_0042`
- [ ] `0042`
:::explain
`#` removes the text from the front. To also drop `.JPG`, cut from the end with `%`: `${n%.JPG}`.
:::
:::

:::step{type=deep-dive title="Go deeper: empty globs, find with loops, and doing it in parallel"}
**When nothing matches.** If no file matches a glob, bash leaves the pattern as it is, and the loop runs once with the
pattern itself as the name:

```text
$ for f in photos/*.PNG; do echo "found $f"; done
found photos/*.PNG
```

`shopt -s nullglob` makes a glob with no matches expand to nothing, so the loop simply does not run:

```text
$ shopt -s nullglob; for f in photos/*.PNG; do echo "found $f"; done; echo "done"
done
```

Or check inside the loop: `[ -e "$f" ] || continue` skips names that do not exist.

**Whole trees.** A glob only looks in one folder. For every file in a tree, feed `find` into `while read`:
`find photos -name "*.JPG" | while read -r f; do ...; done`.

**Faster with many cores.** A loop does one file at a time. For slow work (compressing images, say),
`xargs -P 4` or GNU `parallel` runs four at once, on four cores.

**Ready-made tools.** Ubuntu's `rename` command can rename by pattern in one line, and `mmv` too. Knowing the loop
means you never depend on them.
:::

:::step{type=recap}
You can now:

- repeat commands for every item, file or number with `for`, and for every line of a file with `while read -r`;
- cut names apart with `${f#front}`, `${f%end}`, `basename` and `dirname`;
- rename many files safely: a dry run with `echo` first, then for real;
- write small functions, use `case`, and handle globs that match nothing.

Next, chapter 12: the environment, PATH, and how programs find their settings.

:::photo{src="/lesson-images/linux/linux-11-notes.webp" alt="Handwritten notes about loops: for f in *.csv; do ...; done; while read -r line; $(f#front)  $(f%end); dry run: echo mv first; one loop, any number of files" ai="true"}
One page of notes for this chapter.
:::
:::
