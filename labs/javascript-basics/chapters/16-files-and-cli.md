:::step{type=story title="Can JavaScript live outside the browser?"}
For most of its first fourteen years, JavaScript lived inside web browsers. (Netscape did sell a web server that ran
JavaScript from 1996, but few people used it.) Inside a browser it could not open a file on your computer or run as a
tool in a terminal: browsers forbid that, for good reason, or any website could read your files.

Then, in 2009, a programmer called **Ryan Dahl** took Chrome's JavaScript engine, V8 (released with Chrome a year
earlier), out of the browser and wrapped it in
a program that could read files, talk to networks and run on servers. He called it **Node.js**, and it is the `node`
you have typed in every chapter of this course.

:::photo{src="/lesson-images/javascript/ryan-dahl.webp" alt="Ryan Dahl, the creator of Node.js, standing at a lectern and speaking at a conference" credit="David Calhoun" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:Ryan_Dahl.jpg"}
Ryan Dahl, who created Node.js in 2009, speaking in 2010.
:::

Today Mixtape uses that power: it reads a real playlist file from disk, and becomes a **command-line tool** people can
run with their own file, like `git` or `node` itself.

:::mission
Write `readPlaylist`, which reads songs from a messy CSV file, and `cli.js`, a tool that prints a playlist's summary,
with friendly messages when something is missing.
:::
:::

:::step{type=try title="Read a whole file" file="16-files-and-cli/readme-demo.js" line="2-7"}
Open `playlist.csv` first: a header line, then one song per line. Then open `readme-demo.js`:

```js
const fs = require("node:fs");

const text = fs.readFileSync("playlist.csv", "utf8");
const lines = text.split("\n");
console.log(lines.length, "lines");
console.log(lines.slice(0, 3));
```

```bash run
cd /workspace/16-files-and-cli && node readme-demo.js
```

```text
9 lines
[ 'title,seconds', 'Monsoon Drive,245', 'Neon Lanes,198' ]
```

- `node:fs` is Node's built-in **file system** module (chapter 12 told you about the `node:` modules).
- `readFileSync(path, "utf8")` reads the whole file as text. "Sync" means it waits for the file before going on;
  `fs.promises.readFile` is the `await` version from chapter 15.
- `split("\n")` cuts it into lines (`\n` is the invisible "new line" character at the end of each line). A bare file
  name means "in the folder I am running in".

Why 9 lines, when the file has 8? The last line of the file ends with a new line too, so `split` finds one more,
empty, piece after it. Every text file that ends properly has this, and your reader will need to skip it.

A missing file throws: `Error: ENOENT: no such file or directory, open 'nope.csv'`. ENOENT is the operating system's
old code for "Error, NO ENTry". You will catch it in a moment.
:::

:::step{type=concept title="CSV: one record per line"}
`playlist.csv` is real, which means it is messy. Scroll through it, and you will find a blank line, a song whose
seconds say `abc`, and a row with no title at all:

```text
title,seconds
Monsoon Drive,245
Paper Boats,abc
,180
```

The header is not a song. A blank line is not a song. `abc` is not a number of seconds. A good reader skips them all,
quietly, and keeps the good rows.

`const [title, seconds] = line.split(",");` cuts a row into its two values in one line: array destructuring, the
array version of chapter 9's `{ title, seconds }`.

:::picture{name="file-lines" concept="CSV: one record per line"}
A file is a ribbon of lines: the header first, then one record on each line.
:::
:::

:::step{type=example title="Worked example: count the good rows"}
Not the songs themselves (that is your task), but the same skeleton:

```js
function countGoodRows(path) {
  const lines = fs.readFileSync(path, "utf8").split("\n");
  let count = 0;
  for (const line of lines.slice(1)) {
    const [title, seconds] = line.split(",");
    if (!title || !/^\d+$/.test((seconds ?? "").trim())) {
      continue;
    }
    count = count + 1;
  }
  return count;
}
```

1. `lines.slice(1)` skips the header.
2. A blank line splits into `[""]`: `title` is empty, so `!title` skips it, and so does a row with no title.
   `continue` (chapter 5's deep dive) jumps straight to the next lap of the loop.
3. `/^\d+$/` is a tiny regular expression meaning "only digits, from start to end", so `abc` and `-5` are refused.
   `?? ""` covers a line with no comma at all, where `seconds` is `undefined`.
:::

:::step{type=task task=read_playlist title="Your turn: read the playlist"}
Open `library.js` and make `readPlaylist(path)` give back an array of `{ title, seconds }` objects, with `seconds` as
a **number**. Skip the header, blank lines, rows with no title, and seconds that are not a whole number. A missing
file throws, and `readFileSync` already does that for you.

On `playlist.csv`, it gives four songs: Monsoon Drive (245), Neon Lanes (198), Slow Sunday (312) and Night Train
(301).

```bash run
cd /workspace/16-files-and-cli && node library.js
```

Then press **Check**. The check uses a file of its own, with a row whose seconds are `-5`.

The usual slip, tried against the real check: testing the seconds with `Number.isNaN(Number(seconds))`. That refuses
`abc`, but lets `-5` through as a song of minus five seconds, and the check says to skip seconds that are not a whole
number. The "only digits" pattern from the worked example refuses both.
:::

:::step{type=concept title="A program people can run" file="16-files-and-cli/args.js" line="2-7"}
The words typed after `node file.js` arrive in **`process.argv`**. Open `args.js` and try it:

```bash run
cd /workspace/16-files-and-cli && node args.js playlist.csv --longest
```

```text
4 items
[ 'playlist.csv', '--longest' ]
```

`process.argv` has 4 items: the path of `node`, the path of your file, and then the words you typed. So the user's
first word is always `process.argv[2]`. Now run it with no words, and ask the terminal how it ended:

```bash run
cd /workspace/16-files-and-cli && node args.js; echo "exit $?"
```

```text
2 items
[]
Usage: node args.js <words>
exit 2
```

Two habits of every real command-line tool:

- **Problems go to `console.error`**, which writes to "standard error". Both show in the terminal, but when someone
  saves the normal output to a file (`> out.txt`), errors still reach their screen. (We tried it: the error stayed on
  screen and the saved file was empty.)
- **The exit code** says how it went: 0 means success, anything else means failure. `process.exitCode = 2` (or
  `process.exit(2)`, which stops at once) sets it, and `$?` in the terminal shows it. Scripts read it.
:::

:::step{type=predict title="Guess first"}
:::question
You run `node cli.js june.csv --top 3`. What is `process.argv[3]`?
:::
- [ ] `"june.csv"`
- [x] `"--top"`
- [ ] the number 3
:::explain
Items 0 and 1 are node and the file; `argv[2]` is `june.csv`, `argv[3]` is `--top`. Every item is text.
:::
:::

:::step{type=task task=playlist_cli title="Your turn: the playlist tool"}
Open `cli.js` and make it a real tool:

- `node cli.js playlist.csv` prints two lines: how many songs and their total length, then the longest song;
- with no file name, it prints a usage line with `console.error` and exits with code **2**;
- with a missing file, it prints `File not found: <the path>` with `console.error` (no stack trace) and exits with
  code **1**.

```bash run
cd /workspace/16-files-and-cli && node cli.js playlist.csv; echo "exit $?"
```

```text
4 songs, 17:36 in all
Longest: Slow Sunday
exit 0
```

`readPlaylist` throws an error whose `error.code` is `"ENOENT"` when the file is missing: catch that one, and let any
other error go on (`throw error;`), as chapter 13 advised. Then try the other two cases:

```bash run
cd /workspace/16-files-and-cli && node cli.js missing.csv; echo "exit $?"; node cli.js; echo "exit $?"
```

A finished tool prints (we ran one):

```text
File not found: missing.csv
exit 1
Usage: node cli.js <playlist.csv>
exit 2
```

Your usage line may say it in your own words; it only has to go to `console.error`. Then press **Check**.

The usual slip, tried against the real check: printing `File not found` with `console.log`. On screen it looks
identical, but it went to standard output, and the check reads standard error: it reports `got exit code 1 and ""`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why do error messages go to `console.error`?
:::
- [ ] They print in red
- [x] They still reach the screen when the normal output is saved to a file
- [ ] Node requires it
:::explain
`>` redirects only the normal output, so errors written to standard error stay visible.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does exit code 0 mean?
:::
- [x] Success
- [ ] The program printed nothing
- [ ] An error
:::explain
0 is success; any other number tells a script that something went wrong.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `error.code === "ENOENT"` tell you?
:::
- [ ] The file is empty
- [x] The file does not exist
- [ ] The file is not CSV
:::explain
ENOENT is the operating system's code for "no such file or directory".
:::
:::

:::step{type=deep-dive title="Go deeper: big files, writing files and npx"}
**Big files.** `readFileSync` loads the whole file into memory. For huge files, `fs.createReadStream` with `readline`
reads one line at a time, and `for await` (chapter 15) walks through them.

**Writing.** `fs.writeFileSync("summary.txt", text)` writes a file in one line; `fs.appendFileSync` adds to the end.

**A real command.** Add `#!/usr/bin/env node` as the first line and a `bin` entry in `package.json`, and your tool
installs as a command: `mixtape playlist.csv`. `npx` runs such tools without installing them first.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read a text file with `fs.readFileSync`, split it into lines, and handle a missing file (`ENOENT`).
- Parse a messy CSV: skip the header and bad rows, destructure each row, check numbers with a pattern.
- Read the user's words from `process.argv`, starting at index 2.
- Write a command-line tool: errors to `console.error`, and a meaningful exit code.

:::photo{src="/lesson-images/javascript/js-16-sketch.webp" alt="Sketchnote: Files and the command line. Node can read files and run as a tool in the terminal; a good tool keeps the good rows, explains problems and reports how it ended. Flow: read the file's text, split into lines, skip header and bad rows, build the records, print the summary. Remember: the user's words start at process.argv index 2; ENOENT means no such file or directory; problems go to console.error, not console.log; exit code 0 means success, any other means failure." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 17: tests with `node:test`, so Mixtape can prove it works every time anything changes.
:::
