:::step{type=story title="Two plus two is twenty-two"}
:::character{name="Ravi" role="Owner, Ravi's Tapri"}
A customer typed "2" cold coffee and the bot billed him for 22 cups. Yesterday it said an order
was new when it was the same as the last one. My nephew says "that is just JavaScript".
:::

:::mission
Make the bot read quantities safely and compare two orders by what is in them.
:::
:::

:::step{type=concept title="Text is not a number"}
Everything a user types arrives as a **string**. JavaScript's `+` joins strings, and turns the other
side into a string if one side already is one:

```javascript
"2" + 2          // "22"
Number("2") + 2  // 4
Number("two")    // NaN
```

Convert first, then check what you got: `Number.isInteger(n)` is `true` only for whole numbers.
:::

:::step{type=predict title="Guess first"}
:::question
What is `["coffee"] === ["coffee"]`?
:::
- [ ] `true`: same contents
- [x] `false`: two different arrays
- [ ] An error: arrays cannot be compared
:::explain
`===` on objects and arrays asks "is this the very same object?". Two arrays built separately are never
the same object, even with identical contents. To compare contents you have to check the items.
:::
:::

:::step{type=try title="Poke at it"}
Run the examples in `bot.js` and see what the placeholders do:

```bash run
node bot.js
```
:::

:::step{type=task task=parse_quantity title="Read the quantity"}
Make `parseQuantity(text)` turn a message like `"2"` or `" 3 "` into a number.
Anything that is not a whole number from 1 to 20 (like `"two"`, `"2.5"` or `"0"`) gives `0`.
:::

:::step{type=task task=same_items title="Same order?"}
Make `sameItems(a, b)` return `true` when both arrays hold the same items in the same order.

`sameItems(["coffee", "bun"], ["coffee", "bun"])` is `true`; `sameItems(["coffee", "bun"], ["bun", "coffee"])` is `false`.

:::mistake
`JSON.stringify(a) === JSON.stringify(b)` looks like a shortcut, but it breaks on `undefined`,
dates and key order. Compare the items.
:::
:::

:::step{type=recap}
- User input is text: convert it, then check it.
- `+` with a string joins; `Number()` converts and gives `NaN` when it cannot.
- `===` on arrays compares identity, not contents.
:::
