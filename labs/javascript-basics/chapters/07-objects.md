:::step{type=story title="Why objects"}
A product has a name, a price and a quantity. A student has a name, a roll number and marks. Keeping
those in separate variables quickly gets confusing. An **object** groups related values under one
name, each with its own label.

:::mission
In `objects/cart.js`, add up a shopping cart, and make a discounted copy of an item without changing
the original.
:::
:::

:::step{type=concept title="An object is a record with labels"}
An object is written with curly braces: **keys** (labels) and their **values**:

```javascript
const item = { name: "veg sandwich", price: 20, qty: 2 };
item.name          // "veg sandwich"
item.price * item.qty   // 40
item.qty = 3;      // change a value
item.inStock = true;    // add a new key
```

Read and write with a dot: `item.price`. Think of a filled-in form: each field has a label and an
answer.

:::picture{name="form-card" concept="An object is a record with labels"}
Each label leads to one field, so the price and quantity keep their own meaning.
:::
:::

:::step{type=concept title="Arrays of objects"}
Real data is usually a **list of records**: an array where each item is an object.

```javascript
const cart = [
  { name: "juice", price: 20, qty: 2 },
  { name: "bun", price: 15, qty: 1 },
];

for (const line of cart) {
  console.log(line.name, line.price * line.qty);
}
// juice 40
// bun 15
```

`for...of` gives each object in turn, and the dot reads its fields.

:::picture{name="cart-shelves" concept="Arrays of objects"}
Choose a row first, then follow a field within that row.
:::
:::

:::step{type=example title="Worked example: how many items in the cart"}
A running total over an array of objects:

```javascript
function itemCount(cart) {
  let count = 0;                 // 1. start at zero
  for (const line of cart) {     // 2. each line
    count += line.qty;           // 3. add its quantity
  }
  return count;
}

itemCount(cart)   // 3
```

`cartTotal` is the same loop, adding each line's price times its quantity instead.

:::trace{title="itemCount(cart)"}
| line | line.qty | count | note |
|---|---|---|---|
|  |  | 0 | Before the loop: count starts at zero. |
| juice | 2 | 2 | The first line is an object; line.qty reads its quantity. |
| bun | 1 | 3 | 2 + 1 = 3. No lines left: the answer is 3. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What is `item.colour` for `const item = { name: "juice", price: 20 }`?
:::
- [ ] An error
- [x] `undefined`
- [ ] `null`
- [ ] `""`
:::explain
Reading a key that does not exist gives `undefined`, not an error. It is easy to miss, so a typo in
a key name (`item.prcie`) quietly gives `undefined` too.
:::
:::

:::step{type=try title="Explore an object"}
```bash run
node -e 'const item = { name: "juice", price: 20 }; console.log(item.name, item.colour, Object.keys(item), { ...item, price: 18 }, item)'
```
:::

:::step{type=task task=cart_total title="Warm-up: the cart total"}
In `objects/cart.js`, make `cartTotal(cart)` add up `price * qty` for every line:

- `cartTotal([{ name: "juice", price: 20, qty: 2 }, { name: "bun", price: 15, qty: 1 }])` returns `55`
- `cartTotal([])` returns `0`
:::

:::step{type=concept title="Copy, then change"}
Objects behave like arrays: a variable holds the object's **address**, so `const b = a` shares one
object, and changing `b` changes `a` too.

To change a value **without** touching the original, copy first with the spread syntax:

```javascript
const item = { name: "juice", price: 20 };
const cheaper = { ...item, price: 18 };   // copy every key, then set price
item.price      // 20: the original is untouched
cheaper.price   // 18
```

Keys written after `...item` replace the copied ones.

:::picture{name="photocopy" concept="Copy, then change"}
Changing the price on a photocopy leaves the original tag at 20.
:::
:::

:::step{type=task task=with_discount title="A discounted copy"}
Make `withDiscount(item, percent)` return a **new** item with the price lowered by `percent`, rounded
to two decimals, keeping every other field, and leaving `item` exactly as it was:

- `withDiscount({ name: "juice", price: 20 }, 10)` returns `{ name: "juice", price: 18 }`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`const a = { n: 1 }; const b = a; b.n = 5;` What is `a.n`?
:::
- [ ] `1`
- [x] `5`
- [ ] `undefined`
- [ ] An error
:::explain
`a` and `b` are two names for one object. `{ ...a }` would have made a separate copy.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `{ ...{ a: 1, b: 2 }, b: 3 }`?
:::
- [ ] `{ a: 1, b: 2 }`
- [x] `{ a: 1, b: 3 }`
- [ ] `{ b: 3 }`
- [ ] `{ a: 1, b: 2, b: 3 }`
:::explain
The spread copies `a` and `b`, then `b: 3` replaces the copied `b`. A key can appear only once.
:::
:::

:::step{type=deep-dive title="JSON: objects as text"}
**JSON** (JavaScript Object Notation) writes objects as text, so they can be saved to files and sent
between programs. `JSON.stringify(obj)` turns an object into text and `JSON.parse(text)` turns it back.

Almost every web API in the world sends and receives JSON, even ones written in Python, Go or Java.
It came from JavaScript's object syntax, with stricter rules: keys in double quotes, no functions.
:::

:::step{type=recap title="Chapter done"}
- An object groups labelled values: `{ name: "juice", price: 20 }`, read with a dot.
- Real data is often an array of objects; loop over it with `for...of`.
- `b = a` shares an object; `{ ...a, key: value }` makes a changed copy.
- A missing key gives `undefined`, not an error.
:::
