:::step{type=story title="A program that runs is not a program that is right"}
On 9 September 1947, the team running the Harvard Mark II, a room-sized computer built from thousands of **relays**
(small switches that click open and shut), traced a problem to relay number 70. Inside it they found a real moth.
They taped it into the logbook with the note "First actual case of bug being found." Engineers had already called
faults "bugs" for decades (Thomas Edison wrote about them in the 1870s), which is exactly why a real one was funny
enough to keep.

:::photo{src="/lesson-images/python/first-computer-bug-1947.webp" alt="A page of the Harvard Mark II logbook from 9 September 1947, with a moth taped to it and the note First actual case of bug being found" credit="U.S. Naval History and Heritage Command" license="Public domain" source="https://commons.wikimedia.org/wiki/File:First_Computer_Bug,_1947.jpg"}
The real page, 9 September 1947: the moth is still taped to it.
:::

JavaScript makes bug hunting extra important. You saw it already: a missing argument gives `NaN`, not an error;
dividing by zero gives `Infinity`, not a crash. JavaScript keeps going whenever it can, so many bugs never announce
themselves. Mixtape's `totalLength` runs perfectly and says a playlist is 420 seconds long when it is 620. Today you
learn to hunt both kinds: the loud ones that crash, and the quiet ones that just lie.

:::mission
Read a real stack trace, then use labelled console.log lines and the Node REPL to find and fix two quiet bugs.
:::
:::

:::step{type=try title="A crash two functions deep" file="06-finding-bugs/report.js" line="2-17"}
Open `report.js`. It shouts the longest song title of each playlist:

```js
function longestTitle(titles) {
  let best = titles[0];
  for (const title of titles) {
    if (title.length > best.length) {
      best = title;
    }
  }
  return best;
}

function headline(name, titles) {
  return name + ": " + longestTitle(titles).toUpperCase();
}
```

```bash run
cd /workspace/06-finding-bugs && node report.js
```

```text
Morning: MONSOON DRIVE
/workspace/06-finding-bugs/report.js:13
  return name + ": " + longestTitle(titles).toUpperCase();
                                           ^

TypeError: Cannot read properties of undefined (reading 'toUpperCase')
    at headline (/workspace/06-finding-bugs/report.js:13:44)
    at Object.<anonymous> (/workspace/06-finding-bugs/report.js:17:13)
    at Module._compile (node:internal/modules/cjs/loader:1781:14)
```

The morning playlist worked. The evening one, with no songs at all, crashed. This is a **stack trace**: the list of
function calls that were waiting for an answer when things went wrong. (Your terminal shows five more `node:internal`
lines and the Node version after these; as in chapter 1, we cut them.)
:::

:::step{type=concept title="Read a stack trace from the top"}
Press Play and read this one the way JavaScript developers do:

:::diagram{name="js-stack-trace"}
The error line says what went wrong; the first at line says where; the lines below say how the program got there.
:::

Told in the order things happened: the top of the file (line 17, which Node calls `Object.<anonymous>`) called
`headline("Evening", [])`; `headline` (line 13) called `longestTitle([])`; with no titles, `best` was
`titles[0]`, which is `undefined`, and the loop never ran; so `longestTitle` gave back `undefined`, and line 13 asked
`undefined` to be upper case.

The lines starting `at Module._compile` and `node:internal` are Node's own machinery. Skip them: look for the **first
line that names your file**. That is where to start.

The fix is a decision about empty playlists. One `if` at the top of `longestTitle`:

```js
if (titles.length === 0) {
  return "nothing yet";
}
```

Try it and run the file again (we did):

```text
Morning: MONSOON DRIVE
Evening: NOTHING YET
```
:::

:::step{type=try title="Now the quiet kind" file="06-finding-bugs/playlist.js" line="3-18"}
Open `playlist.js` and run it:

```bash run
cd /workspace/06-finding-bugs && node playlist.js
```

```text
420
true
```

No error. But the songs are 200 + 180 + 240 = **620** seconds, not 420. And `canAdd(10, 10)` says `true`: a playlist
already holding 10 songs, with a limit of 10, has room for one more? That breaks Mixtape's own rule. Nothing crashed,
because nothing is wrong with the grammar or the types. The logic is wrong. Time for detective work.
:::

:::step{type=example title="Worked example: make the invisible visible"}
A bug lives in values you cannot see: the variables inside a function while it runs. The simplest debugging tool in
the world is still `console.log`: print what you want to see, run, compare with what you expected, then remove it.

Suppose you doubt a loop that doubles every price. Add one line inside it:

```js
function doubledTotal(prices) {
  let total = 0;
  for (let i = 0; i < prices.length; i++) {
    console.log("i =", i, "price =", prices[i], "total so far =", total);
    total = total + prices[i] * 2;
  }
  return total;
}
```

With `[10, 20]`, it prints `i = 0 price = 10 total so far = 0`, then `i = 1 price = 20 total so far = 20`. Each line
is one lap. Compare them with what you expected, lap by lap; the first lap that differs points at the bug. Label your
values (`"i =", i`), or a screen full of bare numbers becomes a puzzle of its own.
:::

:::step{type=predict title="Guess first"}
:::question
`totalLength` loops with `for (let i = 1; i < seconds.length; i++)`. For `[200, 180, 240]`, which values does it add?
:::
- [ ] 200, 180 and 240
- [x] 180 and 240
- [ ] 200 and 180
:::explain
`i` starts at 1, so position 0, the first song (200), is never visited: 180 + 240 = 420. Positions start at 0.
:::
:::

:::step{type=task task=fix_total_length title="Your turn: the total that forgets a song"}
Fix `totalLength` in `playlist.js`, so that `totalLength([200, 180, 240])` gives `620`.

1. Prove it first: add `console.log("i =", i, "seconds =", seconds[i]);` inside the loop and run `node playlist.js`.
   Which positions are visited?
2. Find what decides where the loop starts, and fix it.
3. Remove your `console.log` and run it again: `620`.

An empty list must still give `0`. Then press **Check**.

The usual slip: fixing the start and also changing `<` to `<=`. Then the loop visits position 3, which does not
exist, adds `undefined`, and the whole total becomes `NaN` (we tried it: even `[]` gives `NaN`). Start at 0, stop
**before** the length.
:::

:::step{type=concept title="The REPL: ask a function a question"}
Editing the file and running everything takes time. Sometimes you just want to **ask one function one question**.
Type `node` with no file name, and you get the **REPL** (Read, Evaluate, Print, Loop): type a line, see its value.

```bash run
cd /workspace/06-finding-bugs && node
```

```text
Welcome to Node.js v22.23.5.
Type ".help" for more information.
> const p = require("./playlist.js")
undefined
> p.totalLength([200, 180, 240])
420
> p.totalLength([200])
0
> p.canAdd(10, 10)
true
> .exit
```

Look at the third question: a single song of 200 seconds gives **0**. That kind of small, sharp test makes a bug
obvious, and in the REPL it takes two seconds. (The `undefined` after the first line is just the REPL saying "that
line gave back nothing"; `require` loads a file, and chapter 12 explains it.)
:::

:::step{type=task task=fix_can_add title="Your turn: at the limit means no more"}
Fix `canAdd` in `playlist.js`. A playlist may take another song while it has **fewer** songs than the limit; at the
limit, no more:

- `canAdd(9, 10)` gives `true` (room for one more),
- `canAdd(10, 10)` gives `false` (full),
- `canAdd(0, 0)` gives `false`.

1. Look inside: print `room` before the `return`, or try the values in the REPL.
2. What is `room` exactly at the limit? Is that enough room for another song?
3. Fix the comparison, remove your debugging line, and run `node playlist.js`: `620`, then `false`.

Then press **Check**.

There is more than one right answer here: `room > 0`, `room >= 1` and `count < limit` all say the same thing for
whole numbers (we tried them). Pick the one that reads most clearly to you. The one that does not work is
`count <= limit`: it is the same bug written the other way round, and `canAdd(10, 10)` stays `true`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In a Node stack trace, which line usually tells you where the problem is in **your** code?
:::
- [x] The first `at` line that names your own file
- [ ] The last line
- [ ] The line `at Module._compile`
:::explain
The `at` lines are listed newest first. The first one in your own file is where to look; `node:internal` lines are
Node's own machinery.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A function runs without any error and returns a wrong number. What helps first?
:::
- [ ] Reading the error message
- [x] Printing the values inside it, or asking it small questions in the REPL
- [ ] Adding more code
:::explain
There is no error to read. Make the hidden values visible, and test with tiny inputs where you know the answer.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
How do you leave the Node REPL?
:::
- [ ] Type `exit()`
- [x] Type `.exit`, or press Ctrl + D
- [ ] Close the browser
:::explain
`.exit` (with the dot) or Ctrl + D ends the REPL and gives you the terminal back.
:::
:::

:::step{type=deep-dive title="Go deeper: debuggers, the debugger statement, and console.table"}
**A real debugger.** `node inspect playlist.js` starts Node's built-in debugger, and VS Code can pause on any line you
click: every variable, visible, without editing the file.

**The debugger statement.** Write `debugger;` on a line, and when a debugger is attached (or the browser's developer
tools are open), the program pauses right there.

**console.table.** `console.table([{ title: "Neon Lanes", seconds: 198 }])` prints a neat table, with a column for
the position, `(index)`, and one for each field: perfect for lists of songs.

**Off-by-one.** Starting at 1 instead of 0, or `>=` instead of `>`: the same two mistakes, in every language, every
day. You have now fixed both.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Tell a loud bug (an error and a stack trace) from a quiet one (a wrong answer).
- Read a Node stack trace: what went wrong first, then the `at` lines, newest first; skip Node's own lines.
- Make hidden values visible with labelled `console.log` lines.
- Ask a function questions directly in the Node REPL, and leave with `.exit`.

:::photo{src="/lesson-images/javascript/js-06-sketch.webp" alt="Sketchnote: Finding bugs. A loud bug stops the program with an error and a stack trace; a quiet bug runs and gives a wrong answer. Flow: see the wrong result, make values visible, find the first difference, fix one thing, run it again. Remember: read the error line, then the first at line in your file; skip the node:internal lines, Node's own machinery; label every console.log, then remove it; node with no file opens the REPL, .exit leaves." ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 1. Mixtape can talk, work things out, decide and loop, and you can fix it when it misbehaves.
Next, Part 2: working with data, starting with strings.
:::
