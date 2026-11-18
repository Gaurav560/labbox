:::step{type=story title="Tokens and slow suppliers"}
:::character{name="Ravi" role="Owner, Ravi's Tapri"}
At rush hour I hand out tokens, T1, T2, T3, and the bot keeps restarting at T1. And when it asks
my three suppliers for today's prices, the customer waits for one, then the next, then the next.
:::

:::mission
Give each token counter its own memory, and ask every supplier at the same time.
:::
:::

:::step{type=concept title="Closures remember"}
A function created inside another function keeps access to the variables around it, even after the
outer function has returned. That is a **closure**:

```javascript
function makeGreeter(name) {
  return () => `Namaste, ${name}`;
}
const hi = makeGreeter("Ravi");
hi();  // "Namaste, Ravi"
```

Each call to `makeGreeter` creates fresh variables, so two greeters never share a name.
:::

:::step{type=predict title="Guess first"}
:::question
Three `await fetchPrice(item)` calls in a loop, each taking 1 second. How long does the loop take?
:::
- [ ] About 1 second: promises run in parallel
- [x] About 3 seconds: each await waits before the next starts
- [ ] It never finishes
:::explain
`await` pauses until that promise settles, so the next call only starts afterwards. To overlap them,
start all the calls first and then wait for all of them together with `Promise.all`.
:::
:::

:::step{type=try title="Watch the clock"}
Time three slow promises, one after another:

```bash run
node -e "const s=Date.now(); const w=()=>new Promise(r=>setTimeout(r,300)); (async()=>{await w(); await w(); await w(); console.log(Date.now()-s,'ms')})()"
```
:::

:::step{type=task task=make_counter title="Token counters"}
Make `makeTokenCounter(prefix)` return a function. Each call gives the next token: `"T1"`, `"T2"`, ...
Two counters made separately count on their own.
:::

:::step{type=task task=fetch_all title="All suppliers at once"}
Make `fetchAllPrices(items, fetchPrice)` resolve to the prices, in the same order as `items`.
`fetchPrice(item)` returns a promise. Start every fetch at once instead of one after another.
:::

:::step{type=recap}
- A closure keeps the variables of the function that made it.
- Every call to the outer function makes fresh, private state.
- `await` in a loop runs one at a time; `Promise.all` waits for many at once and keeps their order.
:::
