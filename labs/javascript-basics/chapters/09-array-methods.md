:::step{type=story title="Why array methods"}
"Keep the passing marks." "Sort the words by length." With loops, each is several lines of
bookkeeping. JavaScript arrays have **methods** that say exactly what you want in one readable line,
and you will see them in almost every modern JavaScript file.

:::mission
In `arraymethods/marks.js`, keep only the passing marks, then sort words by length.
:::
:::

:::step{type=concept title="Arrow functions: small functions, written short"}
Many array methods need a small function that says **how** to do part of the job. An **arrow
function** is a short way to write one:

```javascript
function isPass(m) { return m >= 40; }   // the long way
const isPass2 = (m) => m >= 40;           // the same, as an arrow
```

Read `(m) => m >= 40` as "given m, answer whether m is at least 40". The inputs go left of `=>` and
the result on the right; with one short expression, `return` is not needed.

:::picture{name="rule-gate" concept="Arrow functions: small functions, written short"}
The arrow function asks one small question about whichever mark arrives.
:::
:::

:::step{type=concept title="filter and map: a conveyor belt"}
Picture a conveyor belt: items ride along, stations keep some and change others, and a box at the end
collects the result.

```javascript
const marks = [72, 30, 90];
marks.filter((m) => m >= 40)    // [72, 90]: keep the ones that answer true
marks.map((m) => m + 5)         // [77, 35, 95]: change every item
marks                           // [72, 30, 90]: never changed
```

Both give back a **new** array and leave the original alone.

:::picture{name="conveyor-belt" concept="filter and map: a conveyor belt"}
Items ride the belt; stations keep, change or sort them.
:::
:::

:::step{type=example title="Worked example: long names, in capitals"}
Methods chain, one station after another:

```javascript
function longNames(names) {
  return names
    .filter((n) => n.length > 4)      // 1. keep long ones
    .map((n) => n.toUpperCase());     // 2. change each
}

longNames(["Riya", "Arjun", "Meera"])   // ["ARJUN", "MEERA"]
```

1. `filter` keeps the names longer than 4 characters.
2. `map` turns each kept name into capitals.

Each line reads like part of the sentence it implements. `passing` needs only step 1.

:::trace{title='longNames(["Riya", "Arjun", "Meera"])'}
| station | result | note |
|---|---|---|
| names | ["Riya", "Arjun", "Meera"] | The items as they arrive on the belt. |
| .filter((n) => n.length > 4) | ["Arjun", "Meera"] | Riya has exactly 4 letters, not more than 4, so it is dropped. |
| .map((n) => n.toUpperCase()) | ["ARJUN", "MEERA"] | Each kept name is changed. names itself never changed. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
After this code, what is `marks`?

```javascript
const marks = [72, 30, 90];
const kept = marks.filter((m) => m >= 40);
```
:::
- [x] `[72, 30, 90]`
- [ ] `[72, 90]`
- [ ] `[]`
- [ ] An error
:::explain
`filter` builds a new array (`kept` is `[72, 90]`) and leaves `marks` exactly as it was.
:::
:::

:::step{type=try title="A pipeline in action"}
```bash run
node -e 'const m = [72, 30, 90, 45, 12]; console.log(m.filter((x) => x >= 40), m.map((x) => x * 2), m.reduce((sum, x) => sum + x, 0), m)'
```

`reduce` folds an array into one value, here a total: you will meet it in the capstone.
:::

:::step{type=task task=passing title="Warm-up: the passing marks"}
In `arraymethods/marks.js`, make `passing(marks)` return the marks of **40 or more**, in their order:

- `passing([72, 30, 90, 40, 39])` returns `[72, 90, 40]`
:::

:::step{type=concept title="Sorting by your own rule"}
`sort` takes a **compare function** `(a, b) => ...` that says which of two items comes first:

- a **negative** result puts `a` first,
- a **positive** result puts `b` first,
- `0` means "equal, keep them as they are".

```javascript
words.sort((a, b) => a.length - b.length)   // shorter first
words.sort((a, b) => a.localeCompare(b))    // alphabetical
```

For ties, combine two rules with `||`: when the first gives `0`, the second decides.

:::mistake
`sort` changes the array it is called on. Sort a copy (`[...words]`) when the array is not yours.
:::

:::picture{name="line-up" concept="Sorting by your own rule"}
The shortest words stand first. Equal-length words line up alphabetically.
:::
:::

:::step{type=task task=sort_by_length title="Sort words by length"}
Make `sortByLength(words)` return the words **shortest first**, with words of the same length in
alphabetical order, without changing the array it was given:

- `sortByLength(["banana", "fig", "apple", "kiwi", "date"])` returns
  `["fig", "date", "kiwi", "apple", "banana"]`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `[1, 2, 3].map((n) => n * 10)` give?
:::
- [ ] `[1, 2, 3]`
- [x] `[10, 20, 30]`
- [ ] `60`
- [ ] `[11, 12, 13]`
:::explain
`map` changes every item with the function: each number times ten.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A compare function returns `-1` for `(a, b)`. Which comes first?
:::
- [x] `a`
- [ ] `b`
- [ ] They stay where they are
- [ ] It depends on their length
:::explain
Negative means `a` first, positive means `b` first, zero means equal.
:::
:::

:::step{type=deep-dive title="Callbacks everywhere"}
A function passed to another function is called a **callback**. Array methods were many people's first
callbacks, but the idea is everywhere in JavaScript: `setTimeout(callback, 1000)` runs one later, a web
page runs one when a button is clicked, and Node runs one when a file has been read.

Other useful methods: `find` (the first match), `some` and `every` (does any or every item pass?),
`reduce` (fold into one value) and `flatMap`.
:::

:::step{type=recap title="Chapter done"}
- `(x) => ...` is an arrow function: a small function written short.
- `filter` keeps, `map` changes, and both return new arrays.
- `sort((a, b) => ...)` sorts by your rule; combine rules with `||` for ties.
- `sort` changes the array: sort a copy when it is not yours.
:::
