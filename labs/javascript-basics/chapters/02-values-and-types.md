:::step{type=story title="Why values and types"}
A shop's app stores a price, a product name, and whether the item is in stock. These are different
**kinds** of value: a number, some text, a yes or no. JavaScript keeps track of the kind, called the
**type**, and it matters: adding two numbers and joining two pieces of text both use `+`.

:::mission
In `types/numbers.js`, work out a percentage safely, and show an amount in paise as rupees.
:::

:::picture{name="price-tags" concept="Variables: names for values"}
A shop keeps the price as a number, the name as text, and stock status as a yes or no.
:::
:::

:::step{type=concept title="Variables: names for values"}
A **variable** is a name for a value, so you can use it later:

```javascript
const price = 120;        // a number
const item = "masala tea"; // text, called a string
let inStock = true;        // a boolean: true or false
inStock = false;           // let can change later
```

- `const` means the name always points at the same value. Use it by default.
- `let` is for values that will change, like a counter.

:::picture{name="labelled-jars" concept="Variables: names for values"}
The labels name the values. Both 17 and 12.50 are numbers in JavaScript.
:::
:::

:::step{type=concept title="typeof, and the + trap"}
`typeof` tells you a value's type:

```javascript
typeof 120        // "number"
typeof "120"      // "string"
typeof true       // "boolean"
```

Now the trap. `+` adds numbers, but **joins** text:

```javascript
2 + 2         // 4
"2" + "2"     // "22"
"2" + 2       // "22": a string wins, so 2 is turned into text
Number("2") + 2   // 4
```

Values from a form or a file arrive as **text**. Turn them into numbers with `Number(...)` before
doing sums.

:::picture{name="glue-vs-add" concept="typeof, and the + trap"}
Two number blocks add up, while two text tiles fit together end to end.
:::
:::

:::step{type=example title="Worked example: an average, rounded"}
JavaScript has one number type for whole numbers and decimals. To round to one decimal:

```javascript
function average(a, b, c) {
  const exact = (a + b + c) / 3;        // 1. the exact value
  return Math.round(exact * 10) / 10;   // 2. one decimal
}

average(70, 71, 71)   // 70.7
```

1. Brackets make the adding happen before the dividing.
2. `Math.round` rounds to a whole number, so multiply by 10 first, then divide by 10 again.

`percent` needs the same rounding, plus one guard you will meet in the next step.

:::picture{name="average-notebook" concept="Variables: names for values"}
Naming the exact average gives the rounding step a value to work with.
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `10 / 0` give in JavaScript?
:::
- [ ] An error
- [x] `Infinity`
- [ ] `0`
- [ ] `NaN`
:::explain
JavaScript does not stop the program: dividing by zero gives the special number `Infinity`. That
quietly flows into the rest of your sums, which is why `percent` checks for a total of `0` first.
:::
:::

:::step{type=try title="Try the trap yourself"}
```bash run
node -e 'console.log(2 + 2, "2" + "2", "2" + 2, Number("2") + 2, 10 / 0, typeof "120")'
```

`node -e` runs one line of JavaScript, handy for quick experiments.

:::picture{name="type-stamps" concept="typeof, and the + trap"}
Converting the typed digit changes which operation the plus sign performs.
:::
:::

:::step{type=task task=percent title="Warm-up: a safe percentage"}
In `types/numbers.js`, make `percent(scored, total)` return `scored` as a percentage of `total`,
rounded to one decimal, and `0` when `total` is `0`:

- `percent(45, 50)` returns `90`
- `percent(1, 3)` returns `33.3`
- `percent(7, 0)` returns `0`
:::

:::step{type=concept title="Money: whole paise, shown as rupees"}
Decimals in computers are not exact: `0.1 + 0.2` gives `0.30000000000000004`. That is why shops and
banks keep money as **whole paise** (or cents) and only turn it into rupees for display.

```javascript
const paise = 1999;
(paise / 100).toFixed(2)   // "19.99", text with exactly 2 decimals
(5 / 100).toFixed(2)       // "0.05"
```

`toFixed(2)` always shows two decimals, which is exactly what a price needs.

:::picture{name="coin-jar" concept="Money: whole paise, shown as rupees"}
Keep 1,999 whole paise in the calculation and write ₹19.99 on the price label.
:::
:::

:::step{type=task task=format_rupees title="Show an amount in rupees"}
Make `formatRupees(paise)` return the amount as text with the ₹ sign and two decimals:

- `formatRupees(1250)` returns `"₹12.50"`
- `formatRupees(5)` returns `"₹0.05"`

:::picture{name="paise-pockets" concept="Money: whole paise, shown as rupees"}
The two small places after the decimal point hold tens of paise and single paise.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `"5" + 3` give?
:::
- [ ] `8`
- [x] `"53"`
- [ ] `NaN`
- [ ] An error
:::explain
One side is a string, so `+` joins text. `Number("5") + 3` gives `8`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which keyword should you use for a value that never changes?
:::
- [x] `const`
- [ ] `let`
- [ ] `var`
- [ ] `fixed`
:::explain
`const` by default; `let` only when the value really changes. `var` is the old way, from before 2015.
:::
:::

:::step{type=deep-dive title="Seven primitive types, and NaN"}
JavaScript has seven **primitive** types: number, string, boolean, `undefined`, `null`, bigint and
symbol. Everything else (arrays, objects, functions) is an **object**.

`Number("abc")` gives `NaN`, "not a number", which is still of type number. `NaN` is the only value
not equal to itself, so check for it with `Number.isNaN(x)`. For very large whole numbers, beyond
about 9 million billion, use **bigint** (`123n`).

:::picture{name="number-sorter" concept="typeof, and the + trap"}
A failed conversion still produces a value of the number type.
:::
:::

:::step{type=recap title="Chapter done"}
- `const` and `let` give names to values; `typeof` shows the type.
- `+` adds numbers but joins strings: turn text into numbers with `Number(...)`.
- Round with `Math.round(x * 10) / 10`; show money with `toFixed(2)`.
- Guard a division by zero: JavaScript gives `Infinity`, not an error.

:::picture{name="shop-till" concept="Money: whole paise, shown as rupees"}
The till adds whole paise and formats the total once for the customer.
:::
:::
