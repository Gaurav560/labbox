:::step{type=story title="Why loops"}
Adding up 5 numbers by hand is easy. Adding up 5,000 is not. A **loop** repeats the same steps for
you: for every mark, every character, every row of a file. It is where computers save the most work.

:::mission
In `loops/loops.js`, add up the numbers from 1 to n, and count the vowels in a piece of text.
:::
:::

:::step{type=concept title="Repeating with a counter"}
The classic `for` loop has three parts, separated by semicolons:

```javascript
for (let i = 1; i <= 3; i++) {
  console.log(i);
}
// 1, then 2, then 3
```

1. `let i = 1` runs once, before the loop starts.
2. `i <= 3` is checked before every round; when it is false, the loop stops.
3. `i++` runs after every round: it adds one to `i`.

:::picture{name="running-track" concept="Repeating with a counter"}
A loop runs the same steps again, lap after lap.
:::
:::

:::step{type=concept title="for...of: each item, no counter"}
When you just want **each item**, `for...of` is simpler:

```javascript
for (const mark of [45, 20, 90]) {
  console.log(mark);
}

for (const ch of "pen") {
  console.log(ch);   // "p", "e", "n"
}
```

It works on arrays and strings alike, and you cannot get the counter wrong because there is none.

:::picture{name="postman" concept="for...of: each item, no counter"}
Each house is visited once in street order, just as the loop visits each item.
:::
:::

:::step{type=example title="Worked example: count the passing marks"}
The counting pattern, one step at a time:

```javascript
function countPassed(marks) {
  let count = 0;             // 1. start at zero
  for (const m of marks) {   // 2. each mark
    if (m >= 33) {           // 3. does it count?
      count++;               // 4. add one
    }
  }
  return count;              // 5. the answer
}
```

:::trace{title="countPassed([45, 20, 90, 33])"}
| m | m >= 33? | count | note |
|---|---|---|---|
|  |  | 0 | Before the loop: count starts at zero. |
| 45 | yes | 1 | 45 passes, so count goes up by one. |
| 20 | no | 1 | 20 does not pass: count stays 1. |
| 90 | yes | 2 | 90 passes: count is 2. |
| 33 | yes | 3 | 33 is exactly 33, and >= includes it: count is 3. |
|  |  | 3 | No marks left: the answer is 3. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
How many times does this loop print?

```javascript
for (let i = 1; i < 5; i++) {
  console.log(i);
}
```
:::
- [ ] 5
- [x] 4
- [ ] 6
- [ ] Forever
:::explain
`i < 5` stops before 5, so it prints 1, 2, 3 and 4. To include 5, write `i <= 5`. This "one too
few" mistake is so common it has a name: an **off-by-one** error.
:::
:::

:::step{type=try title="Watch a loop"}
```bash run
node -e 'let total = 0; for (let i = 1; i <= 4; i++) { total += i; console.log("i", i, "total", total); }'
```
:::

:::step{type=task task=sum_to title="Warm-up: add up 1 to n"}
In `loops/loops.js`, make `sumTo(n)` return `1 + 2 + ... + n`, and `0` when `n` is `0` or less:

- `sumTo(5)` returns `15`
- `sumTo(100)` returns `5050`
:::

:::step{type=concept title="Looking at text one character at a time"}
A string is a row of characters, and `for...of` visits them in order. Two tools help with tests:

```javascript
"Hello".toLowerCase()     // "hello"
"aeiou".includes("e")     // true
"aeiou".includes("x")     // false
```

Lower-casing first means one test covers `"A"` and `"a"` alike.

:::picture{name="case-lenses" concept="Looking at text one character at a time"}
Lower-casing gives an uppercase vowel the same shape as its lowercase partner.
:::
:::

:::step{type=task task=count_vowels title="Count the vowels"}
Make `countVowels(text)` return how many of `a, e, i, o, u` the text contains, in either case:

- `countVowels("Hello World")` returns `3`
- `countVowels("AEIOU")` returns `5`, and `countVowels("rhythm")` returns `0`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
After `let n = 5; n++;`, what is `n`?
:::
- [ ] `5`
- [x] `6`
- [ ] `"51"`
- [ ] An error
:::explain
`n++` adds one to `n`. It is short for `n = n + 1`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which loop is simplest for "each item of an array"?
:::
- [ ] `for (let i = 0; i < a.length; i++)`
- [x] `for (const x of a)`
- [ ] `while (true)`
- [ ] `if (a)`
:::explain
`for...of` gives each item directly, with no counter to get wrong.
:::
:::

:::step{type=deep-dive title="while, break and infinite loops"}
`while (condition) { ... }` repeats as long as the condition is true; it suits "keep going until
something happens", like reading until the end of input. `break` leaves a loop early, and `continue`
skips to the next round.

A loop whose condition never becomes false runs forever and freezes the program (or the browser tab).
If your terminal hangs, press Ctrl+C and check that something in the loop moves it towards the end.
:::

:::step{type=recap title="Chapter done"}
- `for (let i = 1; i <= n; i++)` counts; `for (const x of items)` visits each item.
- A running total starts at 0 and adds inside the loop.
- Watch the boundary: `<` versus `<=` is the classic off-by-one.
- Lower-case text before testing characters.
:::
