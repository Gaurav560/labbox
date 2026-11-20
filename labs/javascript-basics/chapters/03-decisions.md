:::step{type=story title="Why decisions"}
A cinema charges children, adults and seniors differently. A school turns marks into grades. A form
refuses a date that is impossible. Every useful program **decides** what to do based on its data, and
the tool for that is `if`.

:::mission
In `decisions/decisions.js`, turn marks into a grade, and decide whether a year is a leap year.
:::

:::picture{name="cinema-booth" concept="if and else"}
The age at the ticket window decides which ticket the clerk hands back.
:::
:::

:::step{type=concept title="if and else"}
`if` asks a yes-or-no question. When the answer is `true`, its block runs; otherwise the `else` block
runs:

```javascript
if (age >= 18) {
  return "Adult";
} else {
  return "Child";
}
```

Comparisons give `true` or `false`: `>`, `>=`, `<`, `<=`, `===` (equal) and `!==` (not equal).

:::picture{name="fork-in-road" concept="if and else"}
One question, and the answer picks the road.
:::
:::

:::step{type=concept title="Always ===, never =="}
JavaScript has two kinds of "equal":

```javascript
5 === 5      // true
5 === "5"    // false: a number is not a string
5 == "5"     // true: == quietly converts the types first
0 == ""      // true, surprisingly
```

`==` tries to be helpful and converts values before comparing, which leads to strange results.
**Always use `===` and `!==`**: they compare without converting.

:::mistake
A single `=` is not a comparison at all: it **stores** a value. `if (x = 5)` sets `x` to 5.
:::

:::picture{name="number-vs-text" concept="Always ===, never =="}
The printed symbols match, but the coin holds a number and the tag holds text.
:::
:::

:::step{type=example title="Worked example: a ticket price by age"}
Notice the order of the checks:

```javascript
function ticket(age) {
  if (age < 0) {
    return "Invalid";
  } else if (age >= 60) {
    return "Senior";
  } else if (age >= 18) {
    return "Adult";
  } else {
    return "Child";
  }
}
```

1. **Impossible values first**: a negative age is answered before anything else.
2. Then the ranges **from the top down**: 60 and over, then 18 and over.
3. The first true condition wins, so each age gets exactly one answer.

:::trace{title="ticket(45)"}
| check | true? | note |
|---|---|---|
| age < 0 | no | 45 is not below 0, so go on to the next check. |
| age >= 60 | no | 45 is not 60 or more: next check. |
| age >= 18 | yes | 45 is 18 or more: the answer is "Adult", and no later check runs. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
Using `ticket` above, what does `ticket(60)` return?
:::
- [ ] `"Adult"`
- [x] `"Senior"`
- [ ] `"Invalid"`
- [ ] `"Child"`
:::explain
`60 >= 60` is true, so the Senior branch answers first. Boundaries are where most decision bugs live:
always try the exact boundary value.
:::
:::

:::step{type=try title="Try the boundaries"}
```bash run
node -e 'const t = (a) => a < 0 ? "Invalid" : a >= 60 ? "Senior" : a >= 18 ? "Adult" : "Child"; console.log(t(17), t(18), t(59), t(60), t(-1))'
```

:::picture{name="adult-interval" concept="Combining conditions: && and ||"}
The adult band starts at 18 and ends just before the senior band. Both edges matter.
:::
:::

:::step{type=task task=grade title="Warm-up: a grade from marks"}
In `decisions/decisions.js`, make `grade(marks)` return `"A"` for 80 and up, `"B"` for 60 and up, `"C"`
for 40 and up, and `"F"` below 40. Marks below 0 or above 100 give `"Invalid"`.

- `grade(80)` returns `"A"`, and `grade(79)` returns `"B"`
- `grade(101)` returns `"Invalid"`

:::picture{name="grade-boundary" concept="if and else"}
A single mark can move a score across the edge of a grade band.
:::
:::

:::step{type=concept title="Combining conditions: && and ||"}
Some decisions need more than one test:

- `a && b` ("and") is true only when **both** are true.
- `a || b` ("or") is true when **at least one** is true.
- `!a` ("not") flips true and false.

The remainder operator `%` tests "divisible by": `2024 % 4 === 0` is `true` because 2024 divides by 4
with nothing left over.

```javascript
const weekend = day === "Sat" || day === "Sun";
const canVote = age >= 18 && isCitizen;
```

:::picture{name="two-switches" concept="Combining conditions: && and ||"}
A circuit in series needs both switches closed. Parallel paths can light the bulb through either switch.
:::
:::

:::step{type=task task=leap_year title="Is it a leap year?"}
Make `isLeapYear(year)` follow the real rule:

1. a year divisible by 4 is a leap year,
2. **except** years divisible by 100,
3. **except** years divisible by 400, which are leap years again.

`2024` is `true`, `2023` is `false`, `1900` is `false`, `2000` is `true`.

:::picture{name="century-calendar" concept="Combining conditions: && and ||"}
Century years reach the extra check. That is where 1900 and 2000 part ways.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `7 === "7"`?
:::
- [ ] `true`
- [x] `false`
- [ ] An error
- [ ] `undefined`
:::explain
A number and a string are different types, so `===` says false. (`==` would say true, which is why we
avoid it.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `true || false && false`?
:::
- [x] `true`
- [ ] `false`
- [ ] An error
- [ ] `undefined`
:::explain
`&&` is worked out before `||`, like `*` before `+`: `false && false` is false, then `true || false` is
true. Brackets make it clearer to read.
:::
:::

:::step{type=deep-dive title="Truthy and falsy"}
`if` accepts any value, not only booleans. Six values count as false: `false`, `0`, `""`, `null`,
`undefined` and `NaN`. Everything else counts as true, even `"0"` and `[]`.

That is handy (`if (name)` checks for a non-empty name) but can surprise you: `if (count)` is false
when the count is `0`. When in doubt, compare explicitly: `if (count > 0)`.

The **ternary** `cond ? a : b` is an `if` that gives a value, like the one-line ticket in the try step.

:::picture{name="empty-labels" concept="Always ===, never =="}
An empty label and a label bearing the digit zero behave differently in a condition.
:::
:::

:::step{type=recap title="Chapter done"}
- `if`, `else if`, `else` choose a path; the first true condition wins.
- Check impossible values first, then ranges from the top down.
- Use `===` and `!==`, never `==`.
- Combine tests with `&&`, `||` and `!`; `%` tests "divisible by".

:::picture{name="matching-badges" concept="Always ===, never =="}
Strict equality needs both the same type and the same value.
:::
:::
