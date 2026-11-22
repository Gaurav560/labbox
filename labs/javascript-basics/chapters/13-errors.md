:::step{type=story title="Why errors"}
Real input is never perfect: someone types "abc" as their age, a file has a broken line, a value is
out of range. A good program does not fall over on the first surprise. It says clearly what went
wrong, or skips the bad value and carries on.

:::mission
In `errors/ages.js`, read an age with clear errors for bad input, and add up a list of values while
collecting the ones that are not numbers.
:::
:::

:::step{type=concept title="An error is an alarm"}
Picture a fire alarm in a building. When something goes wrong in one room, the alarm rings and normal
work stops, until someone whose job it is deals with it.

When JavaScript cannot carry on, it **throws** an error: the current function stops, and JavaScript
looks for code that will **catch** it. If nobody does, the program ends with a message.

```javascript
null.length           // TypeError: Cannot read properties of null
JSON.parse("{oops")   // SyntaxError
```

:::picture{name="fire-alarm" concept="An error is an alarm"}
An error stops the work until something handles it.
:::
:::

:::step{type=concept title="try and catch"}
Code that might throw goes in `try`. If it throws, JavaScript jumps to `catch`:

```javascript
try {
  const data = JSON.parse(text);
  console.log("read", data);
} catch (e) {
  console.log("that was not valid JSON:", e.message);
}
console.log("carrying on");
```

- If nothing throws, the `catch` block is skipped.
- If something throws, the rest of `try` is skipped and `catch` runs with the error as `e`.
- Either way, the program **carries on** afterwards.

:::picture{name="safety-net" concept="try and catch"}
A thrown error drops out of the risky work and into its handler.
:::
:::

:::step{type=example title="Worked example: a safe quantity"}
Your own functions can throw, with a message in your own words:

```javascript
function parseQuantity(text) {
  const q = Number(text);
  if (!Number.isInteger(q)) {
    throw new TypeError(`not a whole number: "${text}"`);
  }
  if (q < 1) {
    throw new RangeError(`quantity must be at least 1: ${q}`);
  }
  return q;
}
```

1. Text that is not a whole number gets a `TypeError` (the wrong **kind** of value).
2. A number that makes no sense gets a `RangeError` (the right kind, out of range).
3. Each message names the bad value, so the person can fix it.

:::trace{title="parseQuantity with three inputs"}
| text | Number(text) | whole? | q < 1? | result |
|---|---|---|---|---|
| "3" | 3 | yes | no | returns 3 |
| "2.5" | 2.5 | no |  | TypeError: not a whole number: "2.5" |
| "0" | 0 | yes | yes | RangeError: quantity must be at least 1: 0 |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```javascript
try {
  throw new Error("boom");
  console.log("A");
} catch (e) {
  console.log("B");
}
console.log("C");
```
:::
- [ ] `A`, `B`, `C`
- [x] `B`, `C`
- [ ] `A`, `C`
- [ ] Only `B`
:::explain
`throw` stops the `try` block at once, so `A` never prints. `catch` prints `B`, and then the program
carries on with `C`.
:::
:::

:::step{type=try title="Catch one, carry on"}
```bash run
node -e 'for (const t of ["42", "abc", "7"]) { try { const n = Number(t); if (Number.isNaN(n)) throw new TypeError("not a number: " + t); console.log(t, "->", n); } catch (e) { console.log(t, "-> problem:", e.message); } }'
```
:::

:::step{type=task task=parse_age title="Warm-up: read an age"}
Make `parseAge(text)` return a whole number from 0 to 150, ignoring spaces at the ends:

- `parseAge("17")` returns `17`, and `parseAge(" 42 ")` returns `42`
- text that is not a whole number (`"abc"`, `"12.5"`, `""`, `"-1"`) throws a `TypeError`
- `parseAge("151")` throws a `RangeError`
- every message names the bad value
:::

:::step{type=concept title="NaN: the quiet failure"}
Not every problem throws. `Number("x")` does not crash; it gives `NaN`, "not a number", which then
quietly spoils every sum it touches. And `Number("")` gives `0`, not `NaN`, which is even sneakier.

```javascript
Number("12.5")          // 12.5
Number("x")             // NaN
Number.isNaN(Number("x"))   // true: the safe test
Number("")              // 0, careful!
```

So when you read values, test them yourself: skip or report the bad ones.

:::picture{name="spoiled-total" code='NaN' concept="NaN: the quiet failure"}
A failed conversion can carry a bad value into the next sum without ringing an alarm.
:::
:::

:::step{type=task task=safe_sum title="Add the good, report the bad"}
Make `safeSum(values)` add up the values that are numbers and collect the others, returning both:

- `safeSum(["10", "x", "2.5", ""])` returns `{ total: 12.5, bad: ["x", ""] }`
- `safeSum([])` returns `{ total: 0, bad: [] }`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When does a `finally` block run?
:::
- [ ] Only when an error happened
- [ ] Only when no error happened
- [x] Always, error or not
- [ ] Never, unless you call it
:::explain
`finally` always runs after `try` and `catch`, which makes it the place for clean-up.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `Number("12a")`?
:::
- [ ] `12`
- [x] `NaN`
- [ ] An error is thrown
- [ ] `"12a"`
:::explain
`Number` does not throw: anything it cannot read becomes `NaN`. Test with `Number.isNaN`.
:::
:::

:::step{type=deep-dive title="Error types, and catching too much"}
JavaScript's built-in errors include `TypeError`, `RangeError`, `SyntaxError` and `ReferenceError`
(using a name that does not exist). You can create your own with `class AgeError extends Error {}`.

Catch only what you expect and can handle. An empty `catch (e) {}` swallows every problem, including
real bugs, and makes failures silent: one of the most common causes of "it just stopped working" in
production systems.
:::

:::step{type=recap title="Chapter done"}
- An error is an alarm: work stops until a `catch` handles it.
- `try { } catch (e) { }` handles what you expect; then the program carries on.
- `throw new TypeError(...)` or `RangeError(...)` with a message that names the value.
- `Number` gives `NaN` (and `0` for `""`) instead of throwing: test values yourself.
:::
