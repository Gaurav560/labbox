:::step{type=story title="Why counting and sets"}
"Which word appears most?" "How many orders per item?" "Which customers came on both days?" These
questions come up in every kind of data, and JavaScript answers them with two tools: an object used as
a **dictionary** for counting, and a **Set** for "is it in there?".

:::mission
In `counting/counting.js`, count how often each word appears, and find the items two lists share.
:::
:::

:::step{type=concept title="An object as a dictionary"}
An object can also be a lookup table, like a **phone book**: you look up a key to find its value. When
the key is in a variable, use square brackets:

```javascript
const phones = { Riya: "98201 11111" };
const who = "Riya";
phones[who]             // "98201 11111"
phones["Kabir"]         // undefined: not there
phones["Kabir"] ?? "none"   // "none"
```

`??` gives the value on its right when the left is `undefined` or `null`, which is perfect for
"or this default".

:::picture{name="phone-book" code='phones[who]' concept="An object as a dictionary"}
Look up a key to find its value.
:::
:::

:::step{type=example title="Worked example: count the items sold"}
Counting always looks like this:

```javascript
function countItems(items) {
  const counts = {};                              // 1. empty
  for (const item of items) {                     // 2. each item
    counts[item] = (counts[item] ?? 0) + 1;       // 3. one more
  }
  return counts;
}

countItems(["tea", "coffee", "tea"])   // { tea: 2, coffee: 1 }
```

:::trace{title='countItems(["tea", "coffee", "tea"])'}
| item | counts[item] ?? 0 | counts | note |
|---|---|---|---|
|  |  | {} | Start with an empty object. |
| tea | 0 | { tea: 1 } | tea is new: undefined ?? 0 is 0, plus 1. |
| coffee | 0 | { tea: 1, coffee: 1 } | coffee is new too. |
| tea | 1 | { tea: 2, coffee: 1 } | tea is already 1: 1 + 1 = 2, stored back under tea. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What is `undefined + 1`?
:::
- [ ] `1`
- [x] `NaN`
- [ ] `"undefined1"`
- [ ] An error
:::explain
`undefined` is not a number, so the sum is `NaN`. That is exactly what happens the first time you count
a key without `?? 0`, and every count after it stays `NaN`.
:::
:::

:::step{type=try title="Count with and without ??"}
```bash run
node -e 'const c = {}; c.tea = c.tea + 1; const d = {}; d.tea = (d.tea ?? 0) + 1; console.log(c, d)'
```
:::

:::step{type=task task=word_counts title="Warm-up: count each word"}
Make `wordCounts(words)` return how many times each word appears, with words lower-cased so `Tea` and
`tea` count together:

- `wordCounts(["tea", "Coffee", "TEA", "tea"])` returns `{ tea: 3, coffee: 1 }`
- `wordCounts([])` returns `{}`
:::

:::step{type=concept title="A Set: each value once"}
A **Set** is like a guest list at a door: each name is on it once, and checking a name is instant.

```javascript
const guests = new Set(["Riya", "Arjun", "Riya"]);
guests.size          // 2: Riya only once
guests.has("Arjun")  // true
guests.add("Meera");
[...guests]          // ["Riya", "Arjun", "Meera"]: back to an array
```

`has` stays fast even with a million items, while `includes` on an array checks one item at a time.

:::picture{name="guest-list" concept="A Set: each value once"}
A set keeps each item once, like a guest list.
:::
:::

:::step{type=task task=common_items title="The items two lists share"}
Make `commonItems(a, b)` return the items that are in **both** arrays, each once, **sorted**:

- `commonItems(["tea", "coffee", "milk"], ["milk", "tea", "juice"])` returns `["milk", "tea"]`
- `commonItems(["b", "a", "b"], ["b", "b", "a"])` returns `["a", "b"]`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `new Set([1, 1, 2, 2, 2]).size`?
:::
- [ ] `5`
- [x] `2`
- [ ] `3`
- [ ] `1`
:::explain
A Set keeps each value once: just 1 and 2.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `0 ?? 5`?
:::
- [x] `0`
- [ ] `5`
- [ ] `undefined`
- [ ] `NaN`
:::explain
`??` only steps in for `undefined` and `null`. `0` is a real value, so it stays. (The older `||` would
have given 5, which is a classic counting bug.)
:::
:::

:::step{type=deep-dive title="Map, and object keys"}
Object keys are always strings: `counts[1]` and `counts["1"]` are the same key. JavaScript also has
**Map**, a dictionary whose keys can be anything (numbers, objects) and which remembers insertion
order: `new Map()`, `m.set(k, v)`, `m.get(k)`, `m.has(k)`.

Use a plain object for simple string keys and JSON data; use a Map when keys are not strings or when
items are added and removed constantly.
:::

:::step{type=recap title="Chapter done"}
- An object is a dictionary: `obj[key]` reads and writes by a key held in a variable.
- Count with `counts[k] = (counts[k] ?? 0) + 1`.
- A Set keeps each value once and answers `has` instantly; `[...set]` gives an array back.
- `??` gives a default only for `undefined` and `null`.
:::
