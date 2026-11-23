:::step{type=story title="Which line prints first?"}
Here are four lines of JavaScript. Read them, and decide the order they print in:

```js
console.log("1. start");
setTimeout(() => console.log("2. timer, after 0 ms"), 0);
Promise.resolve().then(() => console.log("3. promise"));
console.log("4. end");
```

A timer of **zero** milliseconds should run straight away, surely? Run it in a minute and see. The real order tells
you exactly how JavaScript works underneath: one worker, a queue of jobs, and a strict rule about who goes next.

Mixtape needs this. Downloading a song takes time, and a music app that froze every time it waited for the network
would be useless. Today you learn how JavaScript waits **without stopping**.

:::mission
Make `fetchAll` ask for every price at the same time, and make `retry` try a flaky task again until it works.
:::
:::

:::step{type=try title="The real order" file="15-async/order.js" line="2-5"}
Open `order.js` and run it:

```bash run
cd /workspace/15-async && node order.js
```

```text
1. start
4. end
3. promise
2. timer, after 0 ms
```

1, 4, 3, 2. Neither of the "later" lines interrupted the normal code: both waited until line 4 was done. And the
promise went **before** the timer, even though the timer was set first, with zero milliseconds. The diagram below
shows why.
:::

:::step{type=concept title="One worker and a queue"}
JavaScript runs on **one thread**: one worker that does one thing at a time. It never stops in the middle of your
code to run something else. Press Play:

:::diagram{name="js-event-loop"}
The call stack runs your code to the end; then all promise jobs run; then one timer job; and the loop goes round.
:::

So "later" in JavaScript means: "when the current code has finished, and it is my turn in the queue". A 0 ms timer
means "as soon as possible after that", not "now". And promise jobs always jump ahead of timers. This whole system is
called the **event loop**, and it is why one thread can serve thousands of downloads at once: while it waits for the
network, it is free to do other work.
:::

:::step{type=concept title="A promise is a receipt"}
When you order at a busy food counter, you get a **receipt** straight away, and your food later. A **promise** is that
receipt: an object that stands for a value that is not ready yet.

```js
const p = download("Neon Lanes");          // a promise, at once
p.then((title) => console.log(title));     // runs later, when ready
```

A promise is **pending** at first, then either **fulfilled** (here is the value) or **rejected** (it failed, with an
error).

:::picture{name="token-receipt" concept="A promise is a receipt"}
The receipt is available immediately. Its final outcome arrives later.
:::
:::

:::step{type=concept title="async and await"}
`await` waits for a promise **without freezing everything else**, and gives you its value:

```js
async function playNext() {
  const title = await download("Neon Lanes");
  console.log("now playing", title);
}
```

- `await` only works inside a function marked `async`.
- An `async` function always gives back a promise, so whoever calls it awaits it too.
- If the promise is rejected, `await` **throws**, so chapter 13's `try`/`catch` works as usual.

:::picture{name="parallel-tickets" concept="async and await"}
One suspended function can wait while other work keeps moving.
:::
:::

:::step{type=try title="Forgetting await" file="15-async/forgot.js" line="4-8"}
Open `forgot.js`:

```js
async function main() {
  const title = download("Neon Lanes");
  console.log(title);
  console.log(await download("Neon Lanes"));
}
```

```bash run
cd /workspace/15-async && node forgot.js
```

```text
Promise { <pending> }
Neon Lanes
```

Without `await`, you get the **receipt**, not the song: `Promise { <pending> }`. This is the most common async bug in
JavaScript, and now you will recognise it on sight.
:::

:::step{type=try title="One at a time, or all at once?" file="15-async/download.js" line="4-29"}
Open `download.js`. Three downloads of 300 ms each, done two ways:

```bash run
cd /workspace/15-async && node download.js
```

```text
[ 'Monsoon Drive', 'Neon Lanes', 'Slow Sunday' ]
true true
```

`oneByOne` awaits each download before starting the next: at least 900 ms. `allAtOnce` starts all three first, then
waits once with `Promise.all`: under 450 ms, about as long as the slowest one. And `Promise.all` gives back the
values **in the order you asked**, whichever finished first.
:::

:::step{type=example title="Worked example: two prices at once"}
```js
async function priceOfTwo() {
  const jellyP = fetchPrice("jelly");
  const bunP = fetchPrice("bun");
  const [jelly, bun] = await Promise.all([jellyP, bunP]);
  return jelly + bun;
}
```

1. Calling without `await` **starts** the work and gives promises straight away.
2. `Promise.all` waits for all of them and gives the values in the same order.

With 100 ms each, this takes about 100 ms instead of 200. Like more cooks in the kitchen, the waiting happens side by
side.

:::picture{name="two-cooks" concept="async and await"}
More cooks, all at once: dinner is ready sooner.
:::
:::

:::step{type=task task=fetch_all title="Your turn: fetch every price at once"}
Open `prices.js`. `fetchAll(items, fetchPrice)` works, but waits for one price before asking for the next. Make it start
every fetch at once, and still give back the prices **in the items' order**.

`items.map(...)` makes an array of promises; `Promise.all` waits for them together.

```bash run
cd /workspace/15-async && node prices.js
```

Then press **Check**: it measures how many fetches run at the same time.
:::

:::step{type=concept title="Retrying a flaky task"}
Networks fail now and then. A common fix is to **try again** a few times before giving up:

```js
for (let i = 0; i < 3; i++) {
  try {
    return await sendMessage();
  } catch (error) {
    console.log(`try ${i + 1} failed: ${error.message}`);
  }
}
```

`return` inside the loop ends the whole function as soon as one try works. If every try fails, the loop simply ends:
decide what to do then.

:::picture{name="retry-stamps" concept="Retrying a flaky task"}
Each failure opens another attempt while tries remain. A success ends the journey.
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `console.log("a"); setTimeout(() => console.log("b"), 0); console.log("c");` print?
:::
- [ ] `a b c`
- [x] `a c b`
- [ ] `b a c`
:::explain
The timer's job waits in the queue until the current code (which prints a and c) has finished.
:::
:::

:::step{type=task task=retry title="Your turn: try again"}
In `prices.js`, make `retry(task, times)` call the async `task` up to `times` times: give back the first success, or,
when every try fails, **throw the last error**.

With a task that fails twice and then works, `retry(task, 5)` gives its value on the third try. A task that always
fails, with `times` of 2, is tried exactly twice.

```bash run
cd /workspace/15-async && node prices.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`const t = download("x");` without `await`. What is `t`?
:::
- [ ] The title
- [x] A promise
- [ ] `undefined`
:::explain
Without `await` you hold the receipt, not the value.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which runs first: a promise's `then`, or a 0 ms timer set before it?
:::
- [x] The promise's `then`
- [ ] The timer
:::explain
Promise jobs always run before the next timer job.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
In what order does `Promise.all` give back its values?
:::
- [ ] The order they finished
- [x] The order they were given
:::explain
`Promise.all` keeps your order, so each value lines up with what you asked for.
:::
:::

:::step{type=deep-dive title="Go deeper: Promise.allSettled, any, race, and top-level await"}
**allSettled.** `Promise.all` fails as soon as one promise fails. `Promise.allSettled` waits for every one and tells
you which worked and which did not.

**race and any.** `Promise.race` gives the first to finish, success or failure (handy for timeouts); `Promise.any` the
first success.

**Top-level await.** In ES modules (`.mjs`), `await` works at the top of a file, outside any function.

**Callbacks.** Before promises (2015), async code passed functions to call later: `readFile(path, (error, text) => {
... })`. Nest a few, and you get the famous "callback pyramid". Promises and `await` were invented to flatten it.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Explain the event loop: one worker, your code first, then promise jobs, then timers.
- Use promises, `async` and `await`, and spot a forgotten `await` by its `Promise { <pending> }`.
- Run many tasks at once with `Promise.all`, getting results in your order.
- Retry a flaky task with `await` inside `try`/`catch` in a loop.

:::photo{src="/lesson-images/javascript/js-15-notes.webp" alt="Handwritten notes about async JavaScript: one worker and a queue, your code first then promises then timers, a promise is a receipt, await gives the value, forgot await gives Promise pending, Promise.all keeps the order" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 16: files and a command-line program, so Mixtape can read real playlists from disk.
:::
