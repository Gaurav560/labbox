:::step{type=story title="Why arrays"}
A class has 40 marks, a shop has 200 prices, a playlist has 50 songs. Making a variable for each one
would be madness. An **array** holds many values under one name, in order, and grows when you add more.

:::mission
In `arrays/arrays.js`, return the biggest numbers without disturbing the caller's array, and remove
repeats while keeping the order.
:::

:::picture{name="playlist" concept="Numbered slots"}
One playlist name reaches all four songs, with the first song at position zero.
:::
:::

:::step{type=concept title="Numbered slots"}
An array keeps its items in numbered slots, starting at **0**:

```javascript
const marks = [72, 45, 90];
marks[0]         // 72
marks.length     // 3
marks[marks.length - 1]   // 90: the last one
marks.push(66);  // adds to the end: [72, 45, 90, 66]
```

:::picture{name="egg-box" concept="Numbered slots"}
An array is a row of numbered slots, starting at 0.
:::
:::

:::step{type=concept title="Two names, one array"}
This surprises almost everyone once:

```javascript
const a = [3, 1, 2];
const b = a;        // b is NOT a copy
b.push(9);
a                   // [3, 1, 2, 9]: a changed too!
const c = [...a];   // a real copy, with the spread syntax
```

An array variable holds the **address** of the array. `b = a` copies the address, so both names
reach the same array. `[...a]` spreads the items into a **new** array.

:::picture{name="envelope-address" concept="Two names, one array"}
Two names, one address: both lead to the same array.
:::
:::

:::step{type=example title="Worked example: the cheapest two, safely"}
Sort a **copy** so the caller's array is never touched:

```javascript
function cheapest(prices, n) {
  const copy = [...prices];          // 1. a copy
  copy.sort((a, b) => a - b);        // 2. smallest first
  return copy.slice(0, n);           // 3. the first n
}

cheapest([40, 10, 30], 2)   // [10, 30]
```

1. The spread makes a separate array.
2. `sort` needs a **compare function** for numbers: `a - b` means smallest first.
3. `slice(0, n)` keeps the first n, and is fine when n is bigger than the array.

`topN` is this, biggest first.

:::picture{name="cheapest-tray" concept="Two names, one array"}
Sorting a second tray preserves the order on the original and makes the cheapest pair easy to lift out.
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `[10, 9, 100].sort()` give?
:::
- [ ] `[9, 10, 100]`
- [x] `[10, 100, 9]`
- [ ] `[100, 10, 9]`
- [ ] An error
:::explain
Without a compare function, `sort` compares items **as text**, and the text "100" comes before "9"
just as "apple" comes before "banana". For numbers, always pass `(a, b) => a - b` (or `b - a`).
:::
:::

:::step{type=try title="Sort numbers properly"}
```bash run
node -e 'const a = [10, 9, 100]; console.log([...a].sort(), [...a].sort((x, y) => x - y), [...a].sort((x, y) => y - x), a)'
```

The original `a` is printed last, unchanged, because every sort worked on a copy.

:::picture{name="sorting-lanes" concept="Two names, one array"}
The same three numbers can take different orders depending on the comparison rule.
:::
:::

:::step{type=task task=top_n title="Warm-up: the n biggest numbers"}
In `arrays/arrays.js`, make `topN(numbers, n)` return the n biggest numbers, **biggest first**, without
changing the array it was given:

- `topN([72, 45, 90, 66], 2)` returns `[90, 72]`
- `topN([5, 1], 5)` returns `[5, 1]`
- after the call, the caller's array is still `[72, 45, 90, 66]`

:::picture{name="podium-slots" concept="Numbered slots"}
After ranking, two result slots hold the two largest values.
:::
:::

:::step{type=concept title="Searching an array"}
Two questions you will ask arrays all the time:

```javascript
const items = ["tea", "coffee"];
items.includes("tea")      // true: is it in there?
items.indexOf("coffee")    // 1: where is it? (-1 when missing)
```

To build a new array as you go, start empty and `push` what you want to keep.

:::picture{name="search-signs" concept="Searching an array"}
A membership question gives yes or no. A position question gives a slot number.
:::
:::

:::step{type=task task=unique title="Each item once"}
Make `unique(items)` return the items with repeats removed, in the order they first appear:

- `unique(["tea", "coffee", "tea", "milk"])` returns `["tea", "coffee", "milk"]`
- `unique([3, 1, 3, 2, 1])` returns `[3, 1, 2]`

:::picture{name="first-footprints" concept="Searching an array"}
Keep the first footprint for each value while walking from left to right.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`const a = [1, 2]; const b = a; b.push(3);` What is `a`?
:::
- [ ] `[1, 2]`
- [x] `[1, 2, 3]`
- [ ] `[3]`
- [ ] An error, because `a` is const
:::explain
`b` and `a` are two names for one array. `const` only stops the **name** from pointing elsewhere; the
array itself can still change.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `["a", "b", "c"].indexOf("z")`?
:::
- [ ] `0`
- [ ] `undefined`
- [x] `-1`
- [ ] An error
:::explain
`-1` means "not found". Check for it before using the position.
:::
:::

:::step{type=deep-dive title="Methods that change, and methods that copy"}
Some array methods change the array they are called on: `push`, `pop`, `shift`, `splice`, `sort` and
`reverse`. Others return something new and leave it alone: `slice`, `concat`, `map`, `filter` and the
spread syntax.

Newer JavaScript (2023) adds copying versions of the changers: `toSorted`, `toReversed` and
`toSpliced`. When code is shared between people, preferring the copying versions prevents a whole
family of "who changed my data?" bugs.
:::

:::step{type=recap title="Chapter done"}
- Arrays hold items in numbered slots from 0; `length`, `push`, `slice`.
- `b = a` shares one array; `[...a]` makes a real copy.
- Sort numbers with a compare function: `(a, b) => a - b`.
- `includes` and `indexOf` search; build new arrays with `push`.

:::picture{name="missing-slot" concept="Searching an array"}
A missing item gets a special result outside the numbered slots.
:::
:::
