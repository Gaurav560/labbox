:::step{type=story title="Is the number 1 the same key as the text 1?"}
Mixtape wants to know which song was played most. That means counting: one tally per song title. JavaScript objects
make a fine tally sheet, with the title as the label and the count as the value.

But objects have a secret. Store something under the number `1`, then store something else under the text `"1"`,
and ask how many entries there are. Two, surely: a number is not text. JavaScript says one. Today you find out why,
and meet the two tools JavaScript added for exactly these jobs: **Set** and **Map**.


Counting things is one of the oldest jobs computers were built for. For the 1890 US census, Herman Hollerith's
**tabulating machine** counted 62 million people from punched cards, with a dial for each category: a tally, one per
key. His company later became part of IBM.

:::photo{src="/lesson-images/javascript/hollerith.webp" alt="A black and white photo of a man seated at a Hollerith tabulating machine, a desk with a wall of round counting dials" credit="U.S. Census Bureau" license="Public domain" source="https://commons.wikimedia.org/wiki/File:1902_Hollerith_electric_tabulating_machine.jpg"}
A Hollerith tabulating machine, 1902: a dial per category, counting.
:::
:::mission
Write `wordCounts`, which counts how often each word appears, and `commonItems`, which finds what two lists share.
:::
:::

:::step{type=concept title="An object as a dictionary"}
An object can be used as a **dictionary**: look a value up by its key. To count, read the count so far, add one,
and store it back:

```js
const counts = {};
counts[key] = (counts[key] ?? 0) + 1;
```

`counts[key] ?? 0` means "the count so far, or 0 if this key has never been seen" (chapter 4's `??`). The square
brackets are needed because the key is in a variable.

:::picture{name="phone-book" code='counts[key]' concept="An object as a dictionary"}
Look a value up by its name, like a number in a phone book.
:::
:::

:::step{type=try title="Which song was played most?" file="10-counting/plays.js" line="2-11"}
Open `plays.js` and run it:

```bash run
cd /workspace/10-counting && node plays.js
```

```text
{ 'Neon Lanes': 3, 'Monsoon Drive': 1 }
Set(2) { 'Neon Lanes', 'Monsoon Drive' } 2 false
```

The first line is the tally: Neon Lanes was played 3 times. Notice the quotes around the keys: object keys are
always **text**. Keep that in mind; it is the answer to the puzzle.

The second line is a **Set**, made from the same list of plays: `new Set(plays)`. A Set keeps **each value once**,
so four plays became two titles. `size` counts them, and `has` asks "is this one in there?" in an instant.
:::

:::step{type=example title="Worked example: count the letters"}
```js
function letterCounts(word) {
  const counts = {};
  for (const ch of word.toLowerCase()) {
    counts[ch] = (counts[ch] ?? 0) + 1;
  }
  return counts;
}

letterCounts("Noon")   // { n: 2, o: 2 }
```

:::trace{title="letterCounts with Noon"}
| ch | counts[ch] ?? 0 | counts after |
|---|---|---|
| n | 0 | { n: 1 } |
| o | 0 | { n: 1, o: 1 } |
| o | 1 | { n: 1, o: 2 } |
| n | 1 | { n: 2, o: 2 } |
:::

1. Lower-case first, so `N` and `n` count as the same letter.
2. Read, add one, store back: the same line every counting problem uses.
:::

:::step{type=task task=word_counts title="Your turn: count each word"}
Open `counting.js` and make `wordCounts(words)` give back an object of each word, in **lower case**, to how many times
it appears. Capitals should not matter.

`wordCounts(["juice", "Coffee", "JUICE", "juice"])` gives `{ juice: 3, coffee: 1 }`, and no words give `{}`.

```bash run
cd /workspace/10-counting && node counting.js
```

Then press **Check**.
:::

:::step{type=try title="A number key and a text key" file="10-counting/keys.js" line="2-10"}
Now the puzzle. Open `keys.js`:

```js
const box = {};
box[1] = "the number one";
box["1"] = "the text one";
console.log(box, Object.keys(box));

const map = new Map();
map.set(1, "the number one");
map.set("1", "the text one");
console.log(map.size, map.get(1), map.get("1"));
```

```bash run
cd /workspace/10-counting && node keys.js
```

```text
{ '1': 'the text one' } [ '1' ]
2 the number one the text one
```

An object turns **every key into text**. `box[1]` quietly became `box["1"]`, so the second line overwrote the first:
one entry. A **Map** keeps keys exactly as they are, numbers as numbers and text as text: two entries. Use a Map
when your keys are not text, or when you add and remove keys all the time.
:::

:::step{type=concept title="A Set: each value once"}
A **Set** is a collection that never holds the same value twice:

```js
const guests = new Set(["Asha", "Riya", "Asha"]);
guests.size           // 2
guests.has("Riya")    // true
guests.add("Kabir");
[...guests]           // ["Asha", "Riya", "Kabir"]: back to an array
```

`has` is fast however big the Set grows, which makes Sets perfect for "is it in there?" questions.

:::picture{name="guest-list" concept="A Set: each value once"}
Each guest is on the list once, however many times their name is written down.
:::
:::

:::step{type=predict title="Guess first"}
:::question
What is `new Set([3, 1, 3, 3, 1]).size`?
:::
- [ ] `5`
- [x] `2`
- [ ] `3`
:::explain
A Set keeps each value once: only 3 and 1 are left.
:::
:::

:::step{type=task task=common_items title="Your turn: what two lists share"}
In `counting.js`, make `commonItems(a, b)` give back the items that are in **both** arrays, each once, sorted.

`commonItems(["toast", "coffee", "milk"], ["milk", "toast", "juice"])` gives `["milk", "toast"]`.

Put one list in a Set, then keep the items of the other that the Set `has`.

```bash run
cd /workspace/10-counting && node counting.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `(counts.x ?? 0) + 1` give when `counts` has no `x`?
:::
- [ ] `NaN`
- [x] `1`
- [ ] An error
:::explain
The missing key is `undefined`, `??` replaces it with 0, and 0 + 1 is 1.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In an object, are `o[2]` and `o["2"]` the same entry?
:::
- [x] Yes: object keys are always text
- [ ] No: one is a number
:::explain
The number is turned into the text `"2"`. A Map would keep them apart.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
How do you turn a Set back into an array?
:::
- [ ] `set.toArray()`
- [x] `[...set]`
- [ ] `Array(set)`
:::explain
The spread walks the Set and puts each value into a new array.
:::
:::

:::step{type=deep-dive title="Go deeper: Object.entries, Map in loops, and WeakMap"}
**Object.entries.** `Object.entries({ a: 1, b: 2 })` gives `[["a", 1], ["b", 2]]`, perfect for a loop:
`for (const [key, value] of Object.entries(counts))`.

**Maps in loops.** `for (const [key, value] of map)` walks a Map in the order the keys were added.

**WeakMap.** A Map whose keys must be objects, and which lets those objects be cleaned out of memory when nothing
else uses them. Libraries use it to attach extra data to objects they do not own.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Count anything with an object: `counts[key] = (counts[key] ?? 0) + 1`.
- Explain that object keys are always text, so `1` and `"1"` collide.
- Use a Set to keep each value once and answer "is it in there?" quickly.
- Use a Map when keys are not text, with `set`, `get`, `has` and `size`.

:::photo{src="/lesson-images/javascript/js-10-notes.webp" alt="Handwritten notes about counting in JavaScript: counts of key equals counts of key or 0 plus 1, object keys are always text, a Set keeps each value once, has is fast, a Map keeps number keys as numbers" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 11: array methods and arrow functions, and the most famous puzzle in JavaScript.
:::
