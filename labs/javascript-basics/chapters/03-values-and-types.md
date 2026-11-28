:::step{type=story title="Is 0.1 + 0.2 equal to 0.3?"}
Ask any person, and they say yes. Ask JavaScript:

```text
0.30000000000000004
```

Does a tiny leftover like that ever matter? On 25 February 1991, at Dhahran in Saudi Arabia, a **Patriot**
air-defence system was protecting the area. It counted time in tenths of a second, and stored one tenth in a box of
24 **binary** digits (binary: only 0s and 1s, the way computers store everything). A tenth cannot be written exactly
in binary, so every tick lost a tiny sliver. After about 100 hours switched on, its clock was off by about a third of
a second (0.34 s). For a missile moving that fast, a third of a second meant looking in the wrong part of the sky. It
lost track of an incoming Scud missile, which hit an army barracks; 28 soldiers died. Small errors add up.

:::photo{src="/lesson-images/javascript/patriot.webp" alt="A Patriot missile launcher, a large angled box of missile tubes on a vehicle, in the desert during the Gulf War" credit="U.S. Army" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Patriot_missile_launcher_during_the_Gulf_War.jpg"}
A Patriot launcher, 1991: a tiny error in storing one tenth, after 100 hours, became a third of a second.
:::

The Patriot's numbers were not the same kind as JavaScript's, but the root is the same: a tenth has no exact binary
form. And `0.30000000000000004` is not a bug in JavaScript: Python and Java print exactly the same, because they all
use the same standard way of storing decimals (called IEEE 754). But JavaScript has a few more
surprises of its own, and they all come from one question: what **type** of value is this? A number? Text? Nothing at
all? By the end of this chapter, five of the strangest lines in programming will make complete sense.

:::mission
Write `percent`, a safe percentage that never divides by zero, and `formatRupees`, which shows an amount of money
exactly right.
:::
:::

:::step{type=concept title="Variables: names for values"}
A **variable** is a name for a value, so you can use it later:

```js
const title = "Monsoon Drive";   // text, called a string
const seconds = 245;             // a number
let playing = true;              // a boolean: true or false
playing = false;                 // let can change later
```

- `const` means the name always points at the same value. Use it by default.
- `let` is for values that will change, like a counter or a running total.

:::picture{name="labelled-jars" concept="Variables: names for values"}
The labels are the names. The picture sorts whole numbers and decimals into different jars; JavaScript calls both
17 and 12.50 type `number`.
:::
:::

:::step{type=try title="Five lines, five surprises" file="03-values-and-types/surprises.js" line="2-6"}
Open `surprises.js` and run it:

```js
console.log(0.1 + 0.2);
console.log("5" + 5, "5" * 2);
console.log(typeof 42, typeof "42", typeof null);
console.log(5 == "5", 5 === "5");
console.log(10 / 0, "abc" * 2);
```

```bash run
cd /workspace/03-values-and-types && node surprises.js
```

```text
0.30000000000000004
55 10
number string object
true false
Infinity NaN
```

Every line looks wrong. Every line has a reason. Let's take them one at a time.
:::

:::step{type=concept title="typeof, and the + trap"}
`typeof` tells you a value's type: `typeof 42` is `"number"`, `typeof "42"` is `"string"`.

Now line 2. `+` does two jobs: it **adds** numbers and **joins** text. When one side is text, joining wins, so
`"5" + 5` turns the 5 into text and gives `"55"`. But `*` only means multiply, so `"5" * 2` turns the text into a
number and gives `10`.

Values typed into a form or read from a file always arrive as **text**. Turn them into numbers with `Number("5")`
before doing sums: `Number("5") + 3` is `8`. Two things to know (we tried both): `Number("abc")` is `NaN`, and
`Number("")`, empty text, is `0`, not `NaN`, so an empty form field quietly becomes zero.

:::picture{name="glue-vs-add" concept="typeof, and the + trap"}
Two number blocks add up, while two text tiles fit together end to end.
:::
:::

:::step{type=concept title="The other three surprises"}
**`typeof null` is `"object"`.** `null` means "deliberately nothing". Calling it an object is a mistake from the very
first version of JavaScript, in 1995. A proposal to fix it was turned down, because existing websites depend on it,
so it stays.

**`5 == "5"` is `true`, `5 === "5"` is `false`.** The double `==` converts types before comparing, so text and a
number can be "equal". The triple `===` compares type **and** value. Always use `===`; chapter 4 shows why.

**`10 / 0` is `Infinity`, and `"abc" * 2` is `NaN`.** JavaScript does not crash on bad maths: it gives special number
values instead. `NaN` (Not a Number) is so strange that it is not even equal to itself: `NaN === NaN` is `false`.

And the first line: computers store decimals in binary, where 0.1 cannot be written exactly, just as 1/3 cannot be
written exactly in decimals (0.3333...). The tiny leftover shows up.
:::

:::step{type=example title="Worked example: an average, rounded"}
JavaScript has one number type for whole numbers and decimals. To round to one decimal:

```js
function average(a, b, c) {
  const exact = (a + b + c) / 3;
  return Math.round(exact * 10) / 10;
}

average(7, 8, 8)   // 7.7
```

1. Work out the exact value: `23 / 3` is `7.666...`.
2. Multiply by 10 (`76.66...`), round to a whole number (`77`), then divide by 10: `7.7`.
3. The same trick with 100 gives two decimals.

And a guard: what if there were no values to average at all? Dividing by zero gives `NaN` or `Infinity`, never an
error, so you must check for it yourself. Your first task needs exactly that check.
:::

:::step{type=predict title="Guess first"}
:::question
What does `0 / 0` give in JavaScript?
:::
- [ ] `0`
- [ ] An error
- [x] `NaN`
:::explain
Zero divided by zero has no answer, and JavaScript says so with `NaN` instead of stopping. (Any other number divided
by zero gives `Infinity`.)
:::
:::

:::step{type=task task=percent title="Your turn: a safe percentage"}
Open `numbers.js` and make `percent(scored, total)` give back `scored` as a percentage of `total`, rounded to one
decimal. When `total` is `0`, give back `0`.

`percent(45, 50)` gives `90`, `percent(1, 3)` gives `33.3`, and `percent(7, 0)` gives `0`.

```bash run
cd /workspace/03-values-and-types && node numbers.js
```

Before you start, it prints `-1 -1 -1` and an empty line: the placeholders. Then press **Check**.

The usual slips, each one tried on a lab machine:

- `Math.round(scored / total * 100)` rounds to a whole number: `percent(1, 3)` gives `33`, not `33.3`. Multiply by 10
  before rounding and divide by 10 after, as in the worked example.
- `(scored / total * 100).toFixed(1)` looks right, `33.3`, but `toFixed` gives back **text**, `"33.3"`, and the check
  wants a number.
- No check for `total === 0`: `percent(7, 0)` gives `Infinity`.
:::

:::step{type=concept title="Money: whole paise, shown as rupees"}
Because decimals are not exact, shops and banks keep money as **whole paise** (or cents), and only turn it into
rupees for display:

```js
const paise = 1999;
(paise / 100).toFixed(2)   // "19.99", text with exactly 2 decimals
(5 / 100).toFixed(2)       // "0.05"
```

`toFixed(2)` always shows two decimals, which is exactly what a price needs.

:::picture{name="coin-jar" concept="Money: whole paise, shown as rupees"}
Keep 1,999 whole paise in the calculation and write ₹19.99 on the price label.
:::
:::

:::step{type=task task=format_rupees title="Your turn: show an amount in rupees"}
In `numbers.js`, make `formatRupees(paise)` return the amount as text with the ₹ sign and two decimals:
`formatRupees(1250)` gives `"₹12.50"`, and `formatRupees(5)` gives `"₹0.05"`. (The ₹ sign can be typed straight into
your code, inside the quotes.)

```bash run
cd /workspace/03-values-and-types && node numbers.js
```

Then press **Check**.

The usual slip: `"₹" + paise / 100` with no `toFixed`. It gives `"₹12.5"` (we tried it): a plain number drops the
last zero. `toFixed(2)` is what keeps it.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `"5" + 3` give?
:::
- [ ] `8`
- [x] `"53"`
- [ ] An error
:::explain
With text on one side, `+` joins, so the 3 becomes text.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which comparison is `false`?
:::
- [ ] `5 == "5"`
- [x] `5 === "5"`
- [ ] `5 === 5`
:::explain
`===` checks the type too: a number is never the same as a string.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why keep money as whole paise?
:::
- [ ] Rupees are not allowed in JavaScript
- [x] Decimal maths is not exact, so totals would drift
- [ ] It is faster
:::explain
`0.1 + 0.2` is not exactly `0.3`. Whole numbers are always exact.
:::
:::

:::step{type=deep-dive title="Go deeper: seven types, undefined versus null, and BigInt"}
JavaScript has seven simple ("primitive") types: `number`, `string`, `boolean`, `undefined`, `null`, `bigint` and
`symbol`. Everything else (arrays, objects, functions) is an **object**.

**undefined versus null.** `undefined` means "nobody set this yet", which is what JavaScript gives you. `null` means
"deliberately empty", which is what people write.

**BigInt.** Whole numbers are exact only up to 9,007,199,254,740,991 (`Number.MAX_SAFE_INTEGER`). One step past it,
things slip: `console.log(9007199254740993)` prints `9007199254740992` (we tried it). Write `9007199254740993n`, with
an `n`, and you get a **BigInt**, which keeps huge whole numbers exact.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Name values with `const` and `let`, and check a type with `typeof`.
- Explain the + trap: one side text, and `+` joins instead of adding.
- Explain `0.1 + 0.2`, `typeof null`, `NaN` and `Infinity`.
- Round with `Math.round`, guard a division by zero, and show money with `toFixed(2)`.

:::photo{src="/lesson-images/javascript/js-03-sketch.webp" alt="Sketchnote: Values and types. Every value has a type: number, string, boolean, undefined, null and more; the type decides what plus and triple equals do. Flow: text arrives, Number() turns it into a number, do the maths, round it, toFixed() shows it. Remember: with text on one side, plus joins instead of adding; triple equals checks type and value, double equals converts first; decimals are not exact, keep money in whole paise; bad maths gives NaN or Infinity, not an error." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 4: decisions, so Mixtape can choose what to do.
:::
