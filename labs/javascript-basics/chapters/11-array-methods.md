:::step{type=story title="Why does parseInt give 10, NaN, 2?"}
`parseInt` turns text into a whole number: `parseInt("10")` is `10`. And `map` does something to every item of an
array. So what could be simpler than this?

```js
["10", "10", "10"].map(parseInt)
```

```text
[ 10, NaN, 2 ]
```

Ten, not-a-number, two. From three identical strings. This is the most famous puzzle in JavaScript, and it has fooled
experienced developers for years. By the end of this chapter you will solve it yourself.

On the way you meet the tools that make JavaScript code short and readable: **arrow functions**, and the array
methods `filter`, `map`, `reduce`, `find` and `sort`.

:::mission
Write `passing`, which keeps the marks of 40 or more in one line, and `sortByLength`, which sorts words with a tie rule
of its own.
:::
:::

:::step{type=concept title="Arrow functions: small functions, written short"}
An **arrow function** is a function without the word `function`:

```js
function double(n) { return n * 2; }   // the long way
const double = (n) => n * 2;           // the same function, as an arrow
```

Read it as "n goes to n times 2". With one parameter, the brackets are optional: `n => n * 2`. With a single
expression after the arrow, it is returned automatically: no `return`, no braces.

:::picture{name="rule-gate" concept="Arrow functions: small functions, written short"}
A small rule at a gate: each value walks in, an answer walks out.
:::
:::

:::step{type=try title="A playlist, filtered, mapped and added up" file="11-array-methods/songs.js" line="8-12"}
Open `songs.js`:

```js
const long = songs.filter((s) => s.seconds > 200);
console.log(long.map((s) => s.title));
console.log(songs.map((s) => s.seconds).reduce((sum, n) => sum + n, 0));
console.log(songs.find((s) => s.title.startsWith("N")));
console.log(songs.length);
```

```bash run
cd /workspace/11-array-methods && node songs.js
```

```text
[ 'Monsoon Drive', 'Slow Sunday' ]
755
{ title: 'Neon Lanes', seconds: 198 }
3
```

Each method takes a small arrow function and calls it **for every item**. And the last line matters most: `songs`
still has 3 songs. These methods never change the array they are called on; they build something **new**.
:::

:::step{type=concept title="filter and map: a conveyor belt"}
Each method answers a different question:

| Method | The arrow function answers | You get back |
|---|---|---|
| `filter` | keep this one? (true or false) | a new array of the kept items |
| `map` | what does this item become? | a new array, the same length |
| `find` | is this the one? | the first match, or `undefined` |
| `reduce` | how does this item change the running total? | one single value |

`reduce((sum, n) => sum + n, 0)` is chapter 5's running total in one line: start at 0, and for each item, the new
total is the old total plus the item.

:::picture{name="conveyor-belt" concept="filter and map: a conveyor belt"}
Items ride the belt: one station keeps or drops them, the next turns each into something new.
:::
:::

:::step{type=example title="Worked example: titles of the short songs"}
```js
const titles = songs
  .filter((s) => s.seconds < 240)
  .map((s) => s.title.toUpperCase());
// ["NEON LANES"]
```

1. `filter` keeps the songs under 240 seconds: only Neon Lanes.
2. `map` turns each kept song into its title in capitals.
3. Chaining reads top to bottom like a sentence: take the songs, keep the short ones, turn each into a loud title.

Chaining methods works like Henry Ford's **assembly line** of 1913: each station does one small job and passes the
work on, and the finished result comes out at the end. Nobody at a station needs to know the whole car.

:::photo{src="/lesson-images/javascript/assembly-line.webp" alt="A black and white photo of workers standing along a moving assembly line at the Ford factory in 1913" credit="Ford Motor Company" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Ford_assembly_line_-_1913.jpg"}
Ford's assembly line, 1913: one small job per station.
:::
:::

:::step{type=task task=passing title="Your turn: the passing marks"}
Open `marks.js` and make `passing(marks)` give back the marks of **40 or more**, in their original order, using
`filter`.

`passing([72, 30, 90, 40, 39])` gives `[72, 90, 40]`.

```bash run
cd /workspace/11-array-methods && node marks.js
```

Then press **Check**.
:::

:::step{type=try title="The puzzle, solved" file="11-array-methods/puzzle.js" line="2-4"}
Here is the secret: `map` calls your function with **three** values, not one: the item, its **position**, and the
whole array. An arrow function that only names one parameter simply ignores the other two. But `parseInt` has a
second parameter of its own: the **base** of the number (10 for normal numbers, 2 for binary).

So `map(parseInt)` really calls:

- `parseInt("10", 0)`: base 0 means "work it out", so 10.
- `parseInt("10", 1)`: base 1 does not exist, so `NaN`.
- `parseInt("10", 2)`: "10" in binary is **2**.

Run the fix:

```bash run
cd /workspace/11-array-methods && node puzzle.js
```

```text
[ 10, NaN, 2 ]
[ 10, 10, 10 ]
[ 10, 10, 10 ]
```

Wrapping it in an arrow, `(s) => parseInt(s)`, passes only the item. `Number` takes just one parameter, so it is safe
too. The lesson: when you hand `map` a function written by someone else, check what its extra parameters mean.
:::

:::step{type=concept title="Sorting by your own rule"}
`sort` takes a compare function (chapter 8). To sort by more than one rule, try the first, and fall back to the second
when the first says "equal" (0):

```js
people.sort((a, b) => a.age - b.age || a.name.localeCompare(b.name));
```

`||` uses the right side only when the left side is 0, a tie. `localeCompare` compares text the way a dictionary
does. And remember: `sort` changes the array, so sort a **copy**: `[...people].sort(...)`.

:::picture{name="line-up" concept="Sorting by your own rule"}
Line up by height; when two are the same height, by name.
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `[1, 2, 3].map((n) => n * 10).filter((n) => n > 15)` give?
:::
- [ ] `[10, 20, 30]`
- [x] `[20, 30]`
- [ ] `[2, 3]`
:::explain
`map` gives `[10, 20, 30]`, then `filter` keeps the ones over 15.
:::
:::

:::step{type=task task=sort_by_length title="Your turn: shortest first, ties alphabetical"}
In `marks.js`, make `sortByLength(words)` give back the words **shortest first**, and words of the same length in
**alphabetical** order, without changing the array it was given.

`sortByLength(["banana", "fig", "apple", "kiwi", "date"])` gives `["fig", "date", "kiwi", "apple", "banana"]`.

```bash run
cd /workspace/11-array-methods && node marks.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which method gives back a single value, not an array?
:::
- [ ] `filter`
- [ ] `map`
- [x] `reduce`
:::explain
`reduce` folds the whole array into one value, like a total.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `(n) => n + 1` give back, called with 4?
:::
- [x] `5`
- [ ] `undefined`, because there is no `return`
:::explain
An arrow with a single expression after `=>` returns it automatically.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `find` give when nothing matches?
:::
- [ ] `[]`
- [x] `undefined`
- [ ] An error
:::explain
`find` gives the first match or `undefined`. `filter` would give an empty array.
:::
:::

:::step{type=deep-dive title="Go deeper: some, every, flatMap and Object.groupBy"}
**some and every.** `marks.some((m) => m < 40)` asks "is any below 40?"; `every` asks "are all?".

**flatMap.** Like `map`, but each item may become several: `albums.flatMap((a) => a.songs)` gives one long list of
songs.

**Object.groupBy.** New in recent JavaScript: `Object.groupBy(songs, (s) => (s.seconds > 240 ? "long" : "short"))`
sorts songs into named groups in one line. Chapter 10's tally, built in.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write arrow functions, and know when they return automatically.
- Use `filter`, `map`, `find` and `reduce`, and chain them so code reads like a sentence.
- Sort by your own rule with a compare function and a tie-break, on a copy.
- Explain why `map(parseInt)` gives `[10, NaN, 2]`, and fix it.

:::photo{src="/lesson-images/javascript/js-11-notes.webp" alt="Handwritten notes about JavaScript array methods: arrow functions, filter keeps, map turns, find gives the first, reduce makes one value, the array never changes, map passes item, position and array, sort a copy" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 12: modules and JSON, so Mixtape can split into files and save its playlists.
:::
