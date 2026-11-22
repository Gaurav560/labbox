:::step{type=story title="What if you could teach JavaScript a new word?"}
JavaScript knows `console.log`. It does not know how long a playlist is, or how to greet a Mixtape listener. But you
can teach it: give a few steps a **name**, and from then on that name does all of them, every time you say it.

That is a **function**, and every program you will ever read is built out of them. Today you write your first two,
and you discover something JavaScript does that most languages would never allow.

:::mission
Write `greet`, which builds a welcome message, and `totalMinutes`, which turns hours and minutes into minutes.
:::
:::

:::step{type=concept title="Why functions exist"}
Imagine Mixtape greeting every listener with the same three steps, copied into twenty places. Then the greeting
changes. You would hunt down twenty copies, and miss one.

A **function** fixes that. Write the steps **once**, give them a name, and call the name wherever you need them.
Change the function, and every place that uses it changes too.

:::picture{name="recipe-card" concept="Why functions exist"}
A function is a recipe card: name, inputs, steps, result.
:::
:::

:::step{type=concept title="A function, part by part" file="02-functions/duration.js" line="2-4"}
Open `duration.js`. Its first function:

```js
function minutesOf(seconds) {
  return Math.floor(seconds / 60);
}
```

- `function` says "here comes a function", and `minutesOf` is its **name**.
- `(seconds)` is its **parameter**: inside the function, the value it was given is called `seconds`.
- `return` sends the answer back to whoever **called** it. `Math.floor` rounds down to a whole number.

Calling `minutesOf(245)` runs the steps with `seconds` set to `245`, and gives back `4`.

:::picture{name="square-tiles" concept="A function, part by part"}
Four rows of four tiles make the value that comes back to the caller.
:::
:::

:::step{type=try title="Run it, and forget an argument" file="02-functions/duration.js" line="6-12"}
The second function uses the first one:

```js
function describe(title, seconds) {
  return `${title} (${minutesOf(seconds)} min)`;
}

console.log(describe("Monsoon Drive", 245));
console.log(minutesOf(59));
console.log(describe("Neon Lanes"));
```

```bash run
cd /workspace/02-functions && node duration.js
```

```text
Monsoon Drive (4 min)
0
Neon Lanes (NaN min)
```

Look at the last line. `describe` wants two values and got only one. Java would refuse to even start; JavaScript just
shrugs, sets the missing `seconds` to `undefined`, and carries on. `undefined / 60` is `NaN`: **Not a Number**. No
error, just a strange answer. That is JavaScript's personality: it tries hard to keep going, so **you** have to watch
what goes in.
:::

:::step{type=example title="Worked example: a function that builds text"}
A function that gives back text, with a **template literal**:

```js
function welcome(city) {
  return `Welcome to ${city}!`;
}

welcome("Pune")   // "Welcome to Pune!"
```

1. Template literals use **backticks** (the key above Tab), not quotes.
2. `${city}` puts the value of `city` into the text, right there.
3. `return` hands the finished text back to the caller.

Your first task has exactly this shape, with different words.
:::

:::step{type=task task=greet title="Your turn: greet someone"}
Open `hello.js` and make `greet(name)` return `"Hello, <name>!"`: `greet("Asha")` gives `"Hello, Asha!"`. Mind the comma,
the space and the exclamation mark: the check compares the text exactly.

```bash run
cd /workspace/02-functions && node hello.js
```

Then press **Check**.
:::

:::step{type=try title="The function that forgot to answer" file="02-functions/noreturn.js" line="2-6"}
Open `noreturn.js`:

```js
function double(n) {
  n * 2;
}

console.log(double(21));
```

Before you run it: surely `42`?

```bash run
cd /workspace/02-functions && node noreturn.js
```

```text
undefined
```

The function **worked out** `42`, and then threw it away, because nothing said `return`. A function without
`return` gives back `undefined`. This is the most common function bug in JavaScript, and now you will spot it on sight.
:::

:::step{type=concept title="Numbers and arithmetic"}
Functions often calculate. JavaScript does arithmetic like school maths:

```js
2 + 3 * 4     // 14: * before +
(2 + 3) * 4   // 20: brackets first
10 / 4        // 2.5
7 % 3         // 1: the remainder
```

A function can take **two** parameters, separated by a comma: `function add(a, b) { return a + b; }`.

:::picture{name="remainder-bowls" concept="Numbers and arithmetic"}
Seven counters fill two groups of three, with one counter left over.
:::
:::

:::step{type=predict title="Guess first"}
:::question
`function twice(n) { return n * 2; }` What does `twice("7")` give back?
:::
- [ ] `"77"`
- [x] `14`
- [ ] An error
:::explain
`*` only works on numbers, so JavaScript quietly turns the text `"7"` into the number 7. (`+` would have joined text
instead: chapter 3 shows that trap.)
:::
:::

:::step{type=task task=total_minutes title="Your turn: hours and minutes"}
In `hello.js`, make `totalMinutes(hours, minutes)` return the total number of minutes: `totalMinutes(2, 15)` gives `135`,
and `totalMinutes(0, 45)` gives `45`.

```bash run
cd /workspace/02-functions && node hello.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does a function without `return` give back?
:::
- [ ] `0`
- [x] `undefined`
- [ ] An error
:::explain
Without `return`, the caller gets `undefined`, whatever the function worked out inside.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `` `Hi, ${"Riya"}!` `` give?
:::
- [ ] `"Hi, ${Riya}!"`
- [x] `"Hi, Riya!"`
- [ ] An error
:::explain
Inside backticks, `${...}` is replaced by its value.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A function `f(a, b)` is called as `f(1)`. What is `b` inside it?
:::
- [ ] `0`
- [x] `undefined`
- [ ] It does not run
:::explain
JavaScript runs it anyway, and a parameter with no value is `undefined`.
:::
:::

:::step{type=deep-dive title="Go deeper: default values, arrow functions and scope"}
**Default values.** `function describe(title, seconds = 0)` gives `seconds` a value when the caller leaves it out, so
`describe("Neon Lanes")` would say `0 min` instead of `NaN min`.

**Arrow functions.** A shorter way to write a function: `const double = (n) => n * 2;`. Chapter 11 uses them all the
time.

**Scope.** A variable made inside a function exists only inside it. Two functions can each have their own `total`
without disturbing each other.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write a function with parameters, and give back a value with `return`.
- Call one function from another, and build text with template literals.
- Explain why a missing argument gives `undefined` (and `NaN` in maths), not an error.
- Spot the missing-`return` bug: the function works, and gives back `undefined`.

:::photo{src="/lesson-images/javascript/js-02-notes.webp" alt="Handwritten notes about JavaScript functions: function name, parameters, return sends the answer back, backticks with dollar braces, missing argument is undefined, no return gives undefined" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 3: values and types, and the five strangest lines in JavaScript.
:::
