:::step{type=story title="Why async"}
Asking a server for a price takes time: 100 milliseconds, maybe a second. If JavaScript stood still
while waiting, a web page would freeze and a server could only help one person at a time. Instead,
JavaScript **asks, and carries on**, and deals with the answer when it arrives. This chapter is the
heart of how JavaScript works.

:::mission
In `async/prices.js`, fetch many prices at once instead of one after another, and retry a task that
sometimes fails.
:::

:::picture{name="food-counter" concept="A promise is a receipt"}
The customer can do something else while the kitchen prepares the order.
:::
:::

:::step{type=concept title="A promise is a receipt"}
When you order at a busy food counter, you get a **receipt** straight away, and your food later. A
**promise** is that receipt: an object that stands for a value that is not ready yet.

```javascript
const p = fetchPrice("tea");   // a promise, at once
p.then((price) => console.log(price));   // runs later, when ready
```

A promise is **pending** at first, then either **fulfilled** (here is the value) or **rejected** (it
failed, with an error).

:::picture{name="token-receipt" concept="A promise is a receipt"}
The receipt is available immediately. Its final outcome arrives later.
:::
:::

:::step{type=concept title="async and await"}
`await` waits for a promise **without freezing everything else**, and gives you its value:

```javascript
async function priceOfTwo() {
  const tea = await fetchPrice("tea");      // wait here
  const bun = await fetchPrice("bun");      // then wait here
  return tea + bun;
}
```

- `await` only works inside a function marked `async`.
- An `async` function always returns a promise, so its caller awaits it too.
- If the promise is rejected, `await` throws, so `try`/`catch` works as usual.

:::picture{name="parallel-tickets" concept="async and await"}
One suspended function can wait while other work keeps moving.
:::
:::

:::step{type=example title="Worked example: two at once"}
The code above waits for tea, **then** asks for the bun. Both can be asked at the same time:

```javascript
async function priceOfTwo() {
  const teaP = fetchPrice("tea");     // 1. ask for both
  const bunP = fetchPrice("bun");
  const [tea, bun] = await Promise.all([teaP, bunP]);  // 2. wait once
  return tea + bun;
}
```

1. Calling without `await` starts the work and gives promises straight away.
2. `Promise.all` waits for all of them and gives the values **in the same order**.

With 100 ms each, this takes about 100 ms instead of 200 ms. Like more cooks in the kitchen, the
waiting happens side by side.

:::picture{name="two-cooks" concept="async and await"}
More cooks, all at once: dinner is ready sooner.
:::
:::

:::step{type=predict title="Guess first"}
:::question
In what order do the lines print?

```javascript
setTimeout(() => console.log("later"), 0);
console.log("now");
```
:::
- [ ] `later`, then `now`
- [x] `now`, then `later`
- [ ] Only `now`
- [ ] It depends on the computer
:::explain
Even with 0 ms, `setTimeout` runs its callback **after** the current code has finished. JavaScript
finishes what it is doing, then handles what is waiting: this is the **event loop**.
:::
:::

:::step{type=try title="One after another, or all at once"}
```bash run
node -e 'const wait = (ms) => new Promise((ok) => setTimeout(ok, ms)); (async () => { let t = Date.now(); await wait(200); await wait(200); console.log("one by one", Date.now() - t, "ms"); t = Date.now(); await Promise.all([wait(200), wait(200)]); console.log("together", Date.now() - t, "ms"); })()'
```
:::

:::step{type=task task=fetch_all title="Warm-up: fetch every price at once"}
`fetchAll(items, fetchPrice)` in `async/prices.js` works, but waits for each price before asking for
the next. Make it ask for **every** price at once and still return the prices in the items' order:

- `fetchAll(["coffee", "bun"], fetchPrice)` gives `[30, 15]` (in the order of the items)
- four fetches of about 100 ms each take about 100 ms in all, not 400

:::picture{name="price-tickets" concept="async and await"}
Prices go back into request order even if the bun price is ready first.
:::
:::

:::step{type=concept title="Retrying a flaky task"}
Networks fail now and then. A common fix is to **try again** a few times before giving up:

```javascript
for (let i = 0; i < 3; i++) {
  try {
    return await sendMessage();   // worked: stop here
  } catch (e) {
    console.log(`try ${i + 1} failed: ${e.message}`);
  }
}
```

`return` inside the loop ends the whole function as soon as one try works. If every try fails, the
loop simply ends: decide what to do then.

:::picture{name="retry-stamps" concept="Retrying a flaky task"}
Each failure opens another attempt while tries remain. A success ends the journey.
:::
:::

:::step{type=task task=retry title="Try again"}
Make `retry(task, times)` call the async function `task` up to `times` times. Return the first
successful result; if every try fails, throw the **last** error:

- a task that fails twice then gives `"ok"`: `retry(task, 5)` gives `"ok"` on the third try
- a task that always fails: `retry(task, 2)` tries exactly twice, then throws the second error

:::picture{name="last-error-slip" concept="Retrying a flaky task"}
When all attempts fail, the caller needs the reason from the last attempt.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does an `async` function return?
:::
- [ ] Its value, straight away
- [x] A promise of its value
- [ ] Nothing
- [ ] A callback
:::explain
Always a promise, even when it returns a plain value. Callers use `await` (or `.then`) to get it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`Promise.all([a, b, c])` with `b` finishing first. In what order are the values?
:::
- [ ] The order they finish
- [x] `a`, `b`, `c`: the order you gave
- [ ] Random
- [ ] Only `b`
:::explain
`Promise.all` keeps your order, whatever order the work finishes in. If any promise is rejected, the
whole `Promise.all` is rejected.
:::
:::

:::step{type=deep-dive title="The event loop"}
JavaScript runs your code on **one thread**. Slow work (timers, network, files) is handed to the
browser or to Node, and when it finishes, its callback joins a **queue**. The event loop takes the next
callback from the queue whenever the current code has finished.

That is why one Node server can serve thousands of people at once: nobody's request blocks anyone
else's while it waits. It is also why a long calculation in a loop freezes a web page: while it runs,
nothing else in the queue gets a turn.

:::picture{name="ready-queue" concept="A promise is a receipt"}
A completed job waits for the current code to finish before its callback takes a turn.
:::
:::

:::step{type=recap title="Chapter done"}
- A promise is a receipt for a value that will arrive later.
- `await` waits without freezing; it only works inside `async` functions.
- Start several promises, then `await Promise.all([...])`: faster, and in your order.
- Retry flaky work with `await` inside `try` in a loop.

:::picture{name="retry-exits" concept="Retrying a flaky task"}
The two ways out of a retry loop carry different things back to its caller.
:::
:::
