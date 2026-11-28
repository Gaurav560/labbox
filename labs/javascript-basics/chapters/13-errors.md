:::step{type=story title="What happens when a saved playlist is broken?"}
Mixtape saves playlists as JSON (chapter 12). One day, one of the files gets damaged: half a line missing. Mixtape
calls `JSON.parse` on it, the program stops, and every other playlist, all perfectly fine, never loads.

One broken file should not take everything down with it. A good program notices the problem, says what went wrong,
puts the bad one aside and carries on. That is what **errors** and `try`/`catch` are for.

And JavaScript adds a twist: many of its problems never throw at all. They just quietly hand you `NaN` or
`undefined` and keep going. Today you learn to handle both: the loud failures and the quiet ones.

:::mission
Make `parseAge` refuse bad input with the right kind of error, and make `safeSum` add up the good values while
collecting the bad ones.
:::
:::

:::step{type=concept title="An error is an alarm"}
Picture a fire alarm in a building. When something goes wrong in one room, the alarm rings and normal work stops,
until someone whose job it is deals with it.

When JavaScript cannot carry on, it **throws** an error: the current function stops, and JavaScript looks for code
that will **catch** it. If nobody does, the program ends with a stack trace (chapter 6).

```js
null.length           // TypeError: Cannot read properties of null (reading 'length')
JSON.parse("{oops")   // SyntaxError
```

:::picture{name="fire-alarm" concept="An error is an alarm"}
An error stops the work until something handles it.
:::
:::

:::step{type=try title="One broken playlist, and the rest carry on" file="13-errors/catch.js" line="2-12"}
Open `catch.js`:

```js
for (const text of saved) {
  try {
    const playlist = JSON.parse(text);
    console.log("loaded", playlist.name);
  } catch (error) {
    console.log("skipped:", error.name, "-", error.message);
  }
}
console.log("all done");
```

```bash run
cd /workspace/13-errors && node catch.js
```

```text
loaded Rainy day
skipped: SyntaxError - Expected property name or '}' in JSON at position 1 (line 1 column 2)
loaded Road trip
all done
```

The broken one was skipped; the other two loaded, and `all done` still printed. The second saved text,
`{name: oops}`, is the same mistake as chapter 12's: a key without double quotes.
:::

:::step{type=concept title="try and catch"}
Code that might throw goes in `try`. If it throws, JavaScript jumps to `catch`:

- If nothing throws, the `catch` block is skipped.
- If something throws, the **rest of `try` is skipped** and `catch` runs, with the error object as `error`.
- Either way, the program **carries on** afterwards.

An error is a real object: `error.name` is its kind (`SyntaxError`, `TypeError`, `RangeError`...) and
`error.message` says what happened.

:::picture{name="safety-net" concept="try and catch"}
A thrown error drops out of the risky work and into its handler.
:::
:::

:::step{type=example title="Worked example: a safe quantity"}
Your own functions can throw, with a message in your own words, and the **right kind** of error:

```js
function parseQuantity(text) {
  const q = Number(text.trim());
  if (!Number.isInteger(q) || text.trim() === "") {
    throw new TypeError(`not a whole number: "${text}"`);
  }
  if (q < 1) {
    throw new RangeError(`quantity must be at least 1: ${q}`);
  }
  return q;
}
```

1. `TypeError` for "this is not even the right kind of value"; `RangeError` for "a number, but out of bounds".
2. The message names the bad value, so whoever reads it knows exactly which input was wrong.
3. `Number.isInteger` refuses `NaN`, decimals and Infinity in one test. And watch out: `Number("")` is `0`, so empty
   text needs its own check.

We ran it on six inputs: `"3"` gives 3 and `" 7 "` gives 7; `"2.5"`, `""` and `"abc"` throw `TypeError: not a whole
number: "..."` with the text inside the quotes; `"0"` throws `RangeError: quantity must be at least 1: 0`.
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```js
try {
  const data = JSON.parse("{bad}");
  console.log("parsed");
} catch (error) {
  console.log("caught");
}
console.log("done");
```
:::
- [ ] `parsed` then `done`
- [x] `caught` then `done`
- [ ] Only `caught`
:::explain
`JSON.parse` throws, so the rest of `try` is skipped, `catch` runs, and the program carries on with `done`.
:::
:::

:::step{type=task task=parse_age title="Your turn: read an age, or refuse it"}
Open `ages.js` and finish `parseAge(text)`:

- spaces around the number are fine: `parseAge(" 42 ")` gives `42`, and 0 to 150 are all allowed;
- text that is not a whole number (`"abc"`, `"12.5"`, `""`) throws a **TypeError**;
- a number above 150 throws a **RangeError**;
- `"-1"` must be refused too. You can see it two ways: "a minus sign, so not written with digits only" (a TypeError)
  or "a number, but below 0" (a RangeError, like the worked example's quantity). The check accepts either;
- the messages name the bad value.

```bash run
cd /workspace/13-errors && node ages.js
```

Before you start it prints `42` and the empty `{ total: 0, bad: [] }`: the starter's `parseAge` is plain `Number(text)`,
which never throws, so the `try` block in the file has nothing to catch. Then press **Check**.

The usual slip, tried on a lab machine: testing only `Number.isInteger(Number(text.trim()))`. That lets `""` through
as `0` and `"-1"` through as `-1`, and the check reports `parseAge("") returned 0; it should throw a TypeError.`
Check for empty text, and for numbers below 0.
:::

:::step{type=try title="The quiet failures" file="13-errors/quiet.js" line="2-6"}
Now the twist. Open `quiet.js`: four lines that look like bugs, and not one of them throws:

```bash run
cd /workspace/13-errors && node quiet.js
```

```text
NaN
NaN
undefined
undefined
```

A missing property times 2 is `NaN`. Text that is not a number becomes `NaN`. A slot past the end of an array is
`undefined`. And `song.artist?.name` uses **optional chaining**: `?.` means "if this is null or undefined, stop and give
`undefined`", which is how you read deep into data that may be missing without a crash.
:::

:::step{type=concept title="NaN: the quiet failure"}
`NaN` is the sneakiest of them all. It never throws; it just spreads:

```js
Number("12.5")              // 12.5
Number("x")                 // NaN
NaN + 5                     // NaN: one NaN spoils the whole total
Number.isNaN(Number("x"))   // true: the safe test
Number("")                  // 0, careful!
```

So when you read values from outside (a file, a form, a person), test them yourself: skip or report the bad ones,
before they reach a total.

:::picture{name="spoiled-total" code='NaN' concept="NaN: the quiet failure"}
A failed conversion can carry a bad value into the next sum without ringing an alarm.
:::
:::

:::step{type=task task=safe_sum title="Your turn: add the good, report the bad"}
In `ages.js`, make `safeSum(values)` add up every value that is a number (decimals too) and collect the ones that are
not, giving back `{ total, bad }`.

`safeSum(["10", "x", "2.5", ""])` gives `{ total: 12.5, bad: ["x", ""] }`: the empty text is bad too, even though
`Number("")` is 0. An empty list gives `{ total: 0, bad: [] }`.

```bash run
cd /workspace/13-errors && node ages.js
```

Then press **Check**.

The usual slip: testing only `Number.isNaN`. It gives `{ total: 12.5, bad: [ 'x' ] }` (we tried it): the total is even
right, because the empty text added 0, but `""` is missing from `bad`. The check spots exactly that.
:::

:::step{type=concept title="finally: the clean-up that always runs" file="13-errors/finally.js" line="2-19"}
Sometimes code must run whatever happens: turn the speaker off, close a file. That is `finally`. Open `finally.js`
and run it:

```bash run
cd /workspace/13-errors && node finally.js
```

```text
speaker on for Neon Lanes
playing Neon Lanes
speaker off
speaker on for 
speaker off
refused: no title to play
```

Look at the order for the empty title: `speaker off` comes **before** `refused`. The error was on its way out of
`play`, and JavaScript stopped to run `finally` first. Success or failure, the speaker was turned off.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which kind of error fits "age 200 is too big"?
:::
- [ ] `TypeError`
- [x] `RangeError`
- [ ] `SyntaxError`
:::explain
It is a number (the right type), just outside the allowed range.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is `undefined?.name`?
:::
- [ ] A TypeError
- [x] `undefined`
- [ ] `""`
:::explain
Optional chaining stops at `undefined` and gives `undefined` instead of throwing.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`try` throws and nothing catches the error in this function. Does `finally` still run?
:::
- [x] Yes, before the error leaves the function
- [ ] No
:::explain
`finally` always runs, whether `try` finished, returned or threw.
:::
:::

:::step{type=deep-dive title="Go deeper: error.cause, your own error classes, and catching too much"}
**error.cause.** When you catch one error and throw a clearer one, keep the original:
`throw new Error("could not load the playlist", { cause: error })`. Node then prints both, the cause under
`[cause]:`, each with its own stack trace, so nothing is lost (we tried it).

**Your own error classes.** `class PlaylistError extends Error {}` (classes are next chapter) lets callers catch
exactly your errors: `if (error instanceof PlaylistError)`.

**Do not catch everything.** An empty `catch (error) {}` swallows every problem, including real bugs, silently. Catch
what you expect, do something useful, and let the rest go.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Catch errors with `try` and `catch`, read `error.name` and `error.message`, and carry on.
- Throw the right kind of error (`TypeError`, `RangeError`) with a message that names the bad value.
- Spot the quiet failures (`NaN`, `undefined`), test with `Number.isNaN`, and read safely with `?.`.
- Use `finally` for clean-up that must always run.

:::photo{src="/lesson-images/javascript/js-13-sketch.webp" alt="Sketchnote: Errors. throw stops the function and looks for a catch; try and catch handle the problem, and the program carries on. Flow: risky code in try, something throws, the rest of try is skipped, catch runs, finally always runs. Remember: TypeError is the wrong kind of value, RangeError is out of bounds; a good message names the bad value; getting NaN or undefined is silent, test for them yourself; Number of empty text is 0, empty text needs its own check." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 14: classes, so Mixtape can make many songs from one blueprint.
:::
