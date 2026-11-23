:::step{type=story title="How can a const change?"}
In chapter 3 you learned that `const` means "this name never changes". So what do you think happens here?

```js
const song = { title: "Monsoon Drive", liked: false };
song.liked = true;
```

No error. The song is now liked. A `const` that changed? By the end of this chapter you will see that nothing broke
the rule, and you will understand the single most important idea in JavaScript data: names point at things.

A song is more than a title. It has a length, a like, a count of plays. An **object** keeps all of that together,
each value with a label.

:::mission
Write `cartTotal`, which adds up a shopping cart of objects, and `withDiscount`, which makes a new, cheaper item
without touching the original.
:::
:::

:::step{type=concept title="An object is a record with labels"}
An **object** holds named values, called **properties**:

```js
const song = { title: "Monsoon Drive", seconds: 245, liked: false };
song.title          // "Monsoon Drive"
song["seconds"]     // 245: the same thing, with the name as text
song.liked = true;  // change a property
song.plays = 1;     // add a new one
```

Use the dot when you know the name while writing the code; use `["..."]` when the name is in a variable.

:::picture{name="form-card" concept="An object is a record with labels"}
An object is a filled-in form: every value sits next to its label.
:::
:::

:::step{type=try title="One song, as an object" file="09-objects/song.js" line="2-8"}
Open `song.js` and run it:

```bash run
cd /workspace/09-objects && node song.js
```

```text
Monsoon Drive 245
{ title: 'Monsoon Drive', seconds: 245, liked: true, plays: 1 }
undefined
99
99 0
```

Line two shows the song after the changes: `liked` is now `true`, and `plays` appeared out of nowhere. Line three
asked for `song.artist`, which was never set: `undefined`, not an error. Typos in property names fail just as
quietly: `song.tilte` is `undefined` too.
:::

:::step{type=concept title="Copy, then change" file="09-objects/song.js" line="10-15"}
Now the last two lines of the output, and the answer to the puzzle:

```js
const same = song;
same.plays = 99;
console.log(song.plays);       // 99

const copy = { ...song, plays: 0 };
console.log(song.plays, copy.plays);   // 99 0
```

A variable does not **contain** an object; it **points at** it, like the address of a house. `const` fixes the
address: `song` will always point at this one object. But you can still move the furniture around inside. That is why
`song.liked = true` is allowed, and `song = {}` is not.

And it explains `same`: `const same = song` copied the address, not the house, so `same.plays = 99` changed the one
and only song (the same idea as arrays in chapter 8). To get a real copy, spread it: `{ ...song, plays: 0 }` builds
a **new** object with every property of `song`, then sets `plays` to 0 on the new one only.

:::picture{name="photocopy" concept="Copy, then change"}
Change the photocopy, and the original page stays as it was.
:::
:::

:::step{type=concept title="Arrays of objects"}
Most real data is a list of records: an array of objects.

```js
const cart = [
  { name: "earphones", price: 799, qty: 1 },
  { name: "cable", price: 150, qty: 2 },
];
for (const line of cart) {
  console.log(line.name, line.price * line.qty);
}
```

Every shopping cart, playlist and invoice you will ever build looks like this.

:::picture{name="cart-shelves" concept="Arrays of objects"}
Each shelf in the cart holds one record with the same labels.
:::
:::

:::step{type=example title="Worked example: total length of a playlist"}
```js
function totalSeconds(songs) {
  let total = 0;
  for (const song of songs) {
    total = total + song.seconds;
  }
  return total;
}

totalSeconds([{ title: "Monsoon Drive", seconds: 245 }, { title: "Neon Lanes", seconds: 198 }])   // 443
```

1. A running total, exactly like chapter 5.
2. Each item is an object, so read the property you need: `song.seconds`.
3. An empty playlist gives `0`, because the loop never runs.

Your `cartTotal` task has this shape, with a multiplication inside.
:::

:::step{type=task task=cart_total title="Your turn: the cart total"}
Open `cart.js` and make `cartTotal(cart)` add up `price * qty` for every line of the cart.

`cartTotal([{ price: 20, qty: 2 }, { price: 15, qty: 1 }])` gives `55`, and `cartTotal([])` gives `0`.

```bash run
cd /workspace/09-objects && node cart.js
```

Then press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
`const a = { n: 1 }; const b = a; b.n = 2;` What is `a.n`?
:::
- [ ] `1`
- [x] `2`
- [ ] An error, because `a` is const
:::explain
`a` and `b` point at the same object. `const` stops `a` pointing elsewhere; it does not freeze the object.
:::
:::

:::step{type=task task=with_discount title="Your turn: a cheaper copy"}
In `cart.js`, make `withDiscount(item, percent)` give back a **new** item with the price lowered by `percent`, rounded
to two decimals. The item it was given must not change.

`withDiscount({ name: "jelly", price: 20 }, 10)` gives `{ name: "jelly", price: 18 }`, and the original still costs 20.

```bash run
cd /workspace/09-objects && node cart.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `song.artist` give when the object has no `artist`?
:::
- [ ] An error
- [x] `undefined`
- [ ] `""`
:::explain
A missing property is `undefined`. That is also why typos in property names are hard to spot.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which line makes a real copy of `song`?
:::
- [ ] `const c = song;`
- [x] `const c = { ...song };`
:::explain
The spread builds a new object. Plain `=` copies only the address.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`const p = { x: 1 };` Which line is an error?
:::
- [ ] `p.x = 2;`
- [x] `p = { x: 2 };`
- [ ] `p.y = 3;`
:::explain
`const` stops the name pointing at a different object. Changing the object's own properties is allowed.
:::
:::

:::step{type=deep-dive title="Go deeper: shallow copies, Object.freeze and destructuring"}
**Shallow copies.** `{ ...song }` copies one level. If a property is itself an object (say `song.album`), the copy
and the original still share that inner object. `structuredClone(song)` copies everything, all the way down.

**Object.freeze.** `Object.freeze(song)` really does stop changes: assignments are silently ignored (or an error, in
strict mode).

**Destructuring.** `const { title, seconds } = song;` makes two variables from two properties in one line. You saw the
array version, `[...]`, in chapter 8.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Build objects with labelled properties, and read, change and add them with `.` or `["..."]`.
- Loop over an array of objects, the shape of almost all real data.
- Explain that variables point at objects, so `const` does not freeze an object.
- Copy with `{ ...item }` before changing something that belongs to someone else.

:::photo{src="/lesson-images/javascript/js-09-notes.webp" alt="Handwritten notes about JavaScript objects: properties with labels, dot or brackets, a missing property is undefined, variables point at objects, const fixes the address not the furniture, spread to copy" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 10: counting with objects, sets and maps, and why the number 1 and the text "1" are the same key.
:::
