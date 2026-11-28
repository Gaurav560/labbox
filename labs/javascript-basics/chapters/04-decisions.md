:::step{type=story title="Is an empty list true or false?"}
Every program decides things. Is this song too long for the playlist? Is the listener old enough for this concert?
JavaScript decides with `if`, and `if` needs a yes or a no.

But here is the curious part. You can give `if` **anything**: a number, some text, an empty list. JavaScript turns it
into a yes or a no by its own rules, and some of those rules surprise even experienced developers. Is `"0"` true? Is
an empty list? You will find out by running it.

:::mission
Write `grade`, which turns marks into a grade (and refuses impossible marks), and `isLeapYear`, which follows the real
calendar rule.
:::
:::

:::step{type=concept title="if and else"}
`if` asks a yes-or-no question. When the answer is `true`, its block runs; otherwise the `else` block runs:

```js
if (seconds > 300) {
  console.log("A long one!");
} else {
  console.log("A short one.");
}
```

Comparisons give `true` or `false`, a **boolean** (the type with only those two values): `>` (more than), `>=` (more
than or equal), `<`, `<=`, `===` (equal) and `!==` (not equal). The `else` part is optional: an `if` on its own simply
does nothing when the answer is `false`.

:::picture{name="fork-in-road" concept="if and else"}
One question, and the answer picks the road.
:::
:::

:::step{type=try title="A ticket price, one question at a time" file="04-decisions/ticket.js" line="2-12"}
Open `ticket.js`. A concert ticket costs nothing under 5, ₹250 under 18, and ₹500 for adults:

```js
function ticketPrice(age) {
  if (age < 0) {
    return "Invalid";
  } else if (age < 5) {
    return 0;
  } else if (age < 18) {
    return 250;
  } else {
    return 500;
  }
}
```

```bash run
cd /workspace/04-decisions && node ticket.js
```

```text
0 250 250 500 Invalid
```

JavaScript asks the questions **from the top**, and the first `true` wins: for age 17, `age < 0` is false, `age < 5`
is false, `age < 18` is true, so it returns 250 and never looks further. Notice the edges: 5 is not under 5, so it
costs 250; 18 is not under 18, so it costs 500. Edges are where bugs live.
:::

:::step{type=concept title="Always ===, never =="}
JavaScript has two kinds of "equal":

```js
5 === 5      // true
5 === "5"    // false: a number is not a string
5 == "5"     // true: == quietly converts the types first
0 == ""      // true, surprisingly
```

`==` tries to be helpful and converts values before comparing, which gives strange results (we ran all four lines
above). **Always use `===` and `!==`**: they compare without converting.

A single `=` is not a comparison at all: it **stores** a value. `if (x = 5)` sets `x` to 5, and the `if` sees the 5,
which counts as true, so it always runs. With `if (x = 0)` it is the other way round: the `if` never runs, and `x` has
quietly become 0 (we tried it).

:::picture{name="number-vs-text" concept="Always ===, never =="}
The printed symbols match, but the coin holds a number and the tag holds text.
:::
:::

:::step{type=example title="Worked example: impossible values first"}
A star rating from 1 to 5, as words:

```js
function stars(n) {
  if (n < 1 || n > 5) {
    return "Invalid";
  } else if (n >= 4) {
    return "Loved it";
  } else if (n >= 2) {
    return "It was fine";
  } else {
    return "Not for me";
  }
}
```

1. Impossible values first, so they can never sneak into a real answer.
2. Then the ranges **from the top down**: once `n >= 4` has been ruled out, `n >= 2` only catches 2 and 3.
3. `stars(4)` is "Loved it", `stars(2)` is "It was fine", `stars(9)` is "Invalid".

Your `grade` task has this exact shape.
:::

:::step{type=task task=grade title="Your turn: a grade from marks"}
Open `decisions.js` and make `grade(marks)` give back `"A"` for 80 and up, `"B"` for 60 and up, `"C"` for 40 and up,
and `"F"` below that. Marks below 0 or above 100 give `"Invalid"`.

`grade(80)` gives `"A"`, `grade(79)` gives `"B"`, `grade(39)` gives `"F"`, and `grade(101)` gives `"Invalid"`.

```bash run
cd /workspace/04-decisions && node decisions.js
```

Before you start, it prints a line of empty answers and `false false false`: the placeholders. Then press **Check**.

The usual slips, each one tried on a lab machine:

- The ranges in the wrong order: asking `marks >= 40` first catches everything from 40 up, so `grade(80)` and
  `grade(95)` both give `"C"`. Ask from the top down.
- No impossible-values test: `grade(101)` gives `"A"` and `grade(-5)` gives `"F"`. Put the test first.
:::

:::step{type=try title="Truthy and falsy" file="04-decisions/truthy.js" line="2-9"}
Now the question from the start. Open `truthy.js`: it puts six values into an `if`. Two new things appear here, and
both get their own chapter later: `[0, "", ...]` is a **list** of values in square brackets (chapter 8), and
`for (const value of values)` runs the block once for each value in the list, calling it `value` each time (chapter 5).
`JSON.stringify(value)` shows a value with its quotes, so you can see the difference between `""` and `"0"`
(chapter 12):

```js
const values = [0, "", "0", [], null, "hello"];
for (const value of values) {
  if (value) {
    console.log(JSON.stringify(value), "is truthy");
  } else {
    console.log(JSON.stringify(value), "is falsy");
  }
}
```

```bash run
cd /workspace/04-decisions && node truthy.js
```

```text
0 is falsy
"" is falsy
"0" is truthy
[] is truthy
null is falsy
"hello" is truthy
```

JavaScript has a short list of **falsy** values: `false`, `0`, `""` (empty text), `null`, `undefined` and `NaN`.
**Everything else is truthy**, including the text `"0"` and an empty list `[]`. So `if (playlist)` does not check
whether the playlist has songs: an empty one is still truthy. Check `playlist.length > 0` instead.
:::

:::step{type=concept title="Combining conditions: && and ||"}
Some decisions need more than one test:

- `a && b` ("and") is true only when **both** are true.
- `a || b` ("or") is true when **at least one** is true.
- `!a` ("not") flips true and false.

The remainder operator `%` tests "divisible by": `2024 % 4 === 0` is `true`, because 2024 divides by 4 with nothing
left over.

```js
const weekend = day === "Sat" || day === "Sun";
const canSing = age >= 18 && hasTicket;
```

:::picture{name="two-switches" concept="Combining conditions: && and ||"}
A circuit in series needs both switches closed. Parallel paths can light the bulb through either switch.
:::
:::

:::step{type=concept title="A rule from 1582"}
The Earth goes round the Sun in about 365.2422 days, not 365. The old Julian calendar, from Julius Caesar's time,
added a leap day every 4 years, which makes 365.25: slightly too long. The extra 11 minutes a year added up, and by
1582 the spring equinox (the day of equal day and night) came about ten days earlier on the calendar than it had
centuries before. Pope Gregory XIII fixed it with the rule we
still use: skip the leap day in years divisible by 100, but keep it in years divisible by 400. That averages 365.2425
days a year, close enough to drift only about one day in 3,000 years.

:::photo{src="/lesson-images/python/pope-gregory-xiii.webp" alt="A portrait of Pope Gregory XIII in red robes" credit="Unknown artist" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Pope_Gregory_XIII_portrait.jpg"}
Pope Gregory XIII, whose calendar we still use.
:::
:::

:::step{type=task task=leap_year title="Your turn: is it a leap year?"}
In `decisions.js`, make `isLeapYear(year)` follow it:

1. a year divisible by 4 is a leap year,
2. **except** years divisible by 100,
3. **except** years divisible by 400, which are leap years again.

`isLeapYear(2024)` is `true`, `isLeapYear(1900)` is `false`, and `isLeapYear(2000)` is `true`.

```bash run
cd /workspace/04-decisions && node decisions.js
```

Then press **Check**.

The usual slip: writing only the first two rules, `year % 4 === 0 && year % 100 !== 0`. That gives `true false false`
(we tried it): right for 2024 and 1900, wrong for 2000, because the 400 rule is missing. The year 2000 is exactly the
case people forget.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Is `"0"` (the text with a zero in it) truthy or falsy?
:::
- [x] Truthy
- [ ] Falsy
:::explain
Only empty text is falsy. `"0"` has a character in it, so it is truthy.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`if (x = 5)` is written by mistake. What happens?
:::
- [ ] It compares x with 5
- [x] It stores 5 in x, and the if is always true
- [ ] A SyntaxError
:::explain
One `=` stores a value. Comparisons are `===`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `true && false || true`?
:::
- [x] `true`
- [ ] `false`
:::explain
`&&` goes first: `true && false` is `false`, then `false || true` is `true`.
:::
:::

:::step{type=deep-dive title="Go deeper: switch, the ternary, and ??"}
**switch.** Comparing one value against many fixed answers: `switch (day) { case "Sat": case "Sun": return "weekend";
default: return "weekday"; }`. Remember `break` (or `return`) in each case, or the next case runs too.

**The ternary.** A one-line if: `const label = seconds > 300 ? "long" : "short";`.

**Nullish `??`.** `name ?? "Guest"` gives `"Guest"` only when `name` is `null` or `undefined`, while `name || "Guest"`
would also replace an empty name or `0`. The difference matters when 0 is a real answer.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Decide with `if`, `else if` and `else`, asking from the top down, impossible values first.
- Compare with `===` and `!==`, never `==`, and never confuse `=` with a comparison.
- Combine conditions with `&&`, `||` and `!`, and test "divisible by" with `%`.
- List the falsy values, and know that `"0"` and `[]` are truthy.

:::photo{src="/lesson-images/javascript/js-04-sketch.webp" alt="Sketchnote: Decisions. if runs its block when the condition is true; with else if, JavaScript asks from the top and the first true answer wins. Flow: impossible values first, then the biggest range, then the next one down, else catches the rest. Remember: compare with triple equals and not-equals, never double equals; one equals sign stores a value, it does not compare; and needs both, or needs at least one, not flips; falsy values are false, 0, empty text, null, undefined and NaN, all else is truthy." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 5: loops, so Mixtape can go through a whole playlist.
:::
