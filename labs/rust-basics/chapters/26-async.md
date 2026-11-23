:::step{type=story title="Forty radios, mostly waiting"}
Every ten minutes Windwatch asks each turbine for its power over the farm's radio link. Each answer takes 100 to 150
ms to arrive, and T31, at the far end of the farm with a weak signal, takes three seconds or never answers at all.

Asking one turbine after another, 40 answers take 8.3 seconds, three of them spent waiting for T31. Almost all of that time
the program is doing **nothing**: it is waiting. Chapter 25's threads would help, but a thread is a lot of machinery
(its own stack, two megabytes by default) to spend on waiting.

**async** Rust is built for exactly this: thousands of things in progress at once, on a handful of threads, each one
put aside while it waits and picked up when its answer arrives. The library that runs it is **Tokio**.

:::mission
Ask every turbine at once and gather the answers, then give up on a turbine that takes longer than a time limit.
:::
:::

:::step{type=concept title="async, await, and a runtime" file="26-async/src/lib.rs" line="12-17"}
```rust
pub async fn poll(id: String) -> (String, f64) {
    sleep(Duration::from_millis(delay_ms(&id))).await;   // wait here, without blocking the thread
    ...
}
```

| Piece | Means |
|---|---|
| `async fn` | calling it does not run it: it returns a **future**, a task that can be run later |
| `.await` | run this future until it is done; while it waits, let the thread do other work |
| `#[tokio::main]` | starts the Tokio **runtime**, which runs futures and wakes them when their wait is over |
| `tokio::time::sleep` | a wait that gives the thread back (`std::thread::sleep` would block it) |

Futures are lazy, like iterators (chapter 21): `poll(id)` without `.await` does nothing at all, and the compiler
warns about it. `.await` one after another still means one after another, which is what the starter's `poll_all` does.
:::

:::step{type=concept title="Many at once: JoinSet" file="26-async/src/lib.rs" line="19-30"}
To have them all waiting at the same time, hand each future to the runtime as its own **task**:

```rust
let mut set = JoinSet::new();
for id in ids {
    set.spawn(poll(id.to_string()));         // starts now; does not wait
}
while let Some(answer) = set.join_next().await {
    answers.push(answer.unwrap());           // in the order they finish
}
```

All 40 requests are now in flight together, so the whole round takes about as long as the slowest one. Answers
arrive in the order they finish, not the order they were asked, so sort them afterwards. `answer` is a `Result`,
`Err` only if the task panicked.

:::diagram{name="rs-async"}
One thread starts every poll, parks each while it waits, and wakes each when its answer arrives.
:::
:::

:::step{type=task task=concurrent_poll title="Your turn: ask them all at once" file="26-async/src/lib.rs" line="19-30"}
Rewrite `poll_all(ids)`: make a `JoinSet::new()`, `set.spawn(poll(id.to_string()))` for each id, then
`while let Some(answer) = set.join_next().await` push `answer.unwrap()`, and sort the answers by id
(`answers.sort_by(|a, b| a.0.cmp(&b.0))`). Remove the line with `JoinSet::<()>::new`.

Press **Check**.
:::

:::step{type=history title="The C10K problem"}
:::before{title="A thread per connection"}
Servers in the 1990s gave every connection its own thread or process. Ten thousand slow clients meant ten thousand
threads, each with its own memory, mostly asleep, and the machine ran out long before the network did.
:::

In **1999** Dan Kegel named it **the C10K problem**: serving ten thousand connections at once. The answer was the
**event loop**: one thread, told by the operating system which connections are ready, doing a little work for each.
nginx (**2004**) served the web that way, and Node.js (**2009**) made it the way JavaScript works. Writing event-loop
code by hand meant callbacks inside callbacks, so C# added **async and await** (**2012**) to write it like ordinary
code, and JavaScript and Python followed. Rust's version arrived in Rust 1.39 (**November 2019**), with one difference:
a Rust future is a plain value that does nothing until it is run, so it needs no garbage collector and no hidden
threads. Carl Lerche's **Tokio** (**2016**) is the runtime most Rust services use.

:::solved
**Waiting is nearly free.** A Tokio task is a small value on the heap, not a thread with a stack, so a server can keep a
hundred thousand of them in progress at once.
:::

:::timeline
- **1999** The C10K problem.
- **2009** Node.js: an event loop for everyone.
- **2012** async and await in C#.
- **2016** Tokio.
- **2019** async and await in Rust 1.39.
:::

Ryan Dahl, who built Node.js in 2009 to show that one thread with an event loop could serve thousands of connections at once.

:::photo{src="/lesson-images/rust/ryan-dahl.webp" alt="Ryan Dahl, a young man with glasses and a beard in a dark T-shirt, speaking at a lectern" credit="David Calhoun (cropped)" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File%3ARyan_Dahl.jpg"}
Ryan Dahl at YUIConf, 2010.
:::
:::

:::step{type=concept title="Giving up in time" file="26-async/src/lib.rs" line="32-38"}
`tokio::time::timeout(limit, future)` runs the future, but for at most `limit`:

```rust
match timeout(limit, poll(id.to_string())).await {
    Ok(answer) => Ok(answer),              // finished in time
    Err(_) => Err(format!("{id} did not answer in {} ms", limit.as_millis())),
}
```

When the time is up, the future is simply **dropped**: it stops where it was waiting, and nothing of it keeps running.
That is the advantage of lazy futures. A thread cannot be stopped from outside like that.
:::

:::step{type=task task=with_timeout title="Your turn: a time limit for T31" file="26-async/src/lib.rs" line="32-38"}
Rewrite `poll_with_timeout(id, limit)` with the `match` above: `Ok(answer)` gives `Ok(answer)`, `Err(_)` gives
`Err(format!("{id} did not answer in {} ms", limit.as_millis()))`. Remove the two old lines.

```bash run
cd /workspace/26-async && cargo run -q
```

Press **Check**.
:::

:::step{type=try title="Five seconds become a seventh of one"}
```text
$ cargo run -q
10 turbines one after another: 1.36 s
39 turbines at once: 0.14 s, first ("T01", 2300.0)
T07: Ok(("T07", 2200.0)) after 0.14 s
T31: Err("T31 did not answer in 500 ms") after 0.50 s
```

Ten turbines one after another took 1.36 s, the sum of their waits. **Thirty-nine** at once took 0.14 s: the longest
single wait (142 ms), and no more. Polled one by one, those 39 would take 5.3 s. All of it ran on the
runtime's threads, with no thread per turbine.

T07 answered in 0.14 s, well inside its 500 ms. T31 would have taken 3 s; after 0.50 s the timeout dropped the request
and returned the error, so one weak radio can no longer hold up the round. (`main` leaves T31 out of the big round for
the same reason.)
:::

:::step{type=predict title="Guess first"}
:::question
Inside an `async fn`, someone writes `std::thread::sleep(Duration::from_secs(1))` instead of Tokio's `sleep(...).await`.
What happens to the other turbines' polls?
:::
- [ ] Nothing changes
- [x] They stall: the thread is blocked for a second and cannot run other tasks while it sleeps
- [ ] It does not compile
:::explain
It compiles, which is why it is a classic mistake. Inside async code, wait only with things you can `.await`.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`let f = poll("T07".to_string());` and nothing else. Has T07 been asked?
:::
- [ ] Yes
- [x] No: a future does nothing until it is awaited or spawned
- [ ] Only half
:::explain
The compiler warns: "futures do nothing unless you `.await` or poll them".
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
When should you pick async over threads?
:::
- [x] When most of the time is spent waiting (network, disk, timers), for many things at once
- [ ] For heavy computing on every CPU
- [ ] Always: it is faster
:::explain
Computing needs CPUs (threads, chapter 25). Waiting needs only a way to be woken (async).
:::
:::

:::step{type=deep-dive title="Go deeper: async in practice"}
**Both together.** Tokio runs its tasks on a few threads, one per CPU, so async code uses every CPU too. Heavy
computing inside async code goes in `tokio::task::spawn_blocking`, so it does not stall the waiting tasks.

**select!** `tokio::select!` waits for whichever of several futures finishes first: an answer, a shutdown signal or a
timer.

**Real networks.** The same code shape works with `reqwest` for HTTP clients and `tokio::net` for sockets; chapter 28's
web server is built on it.
:::

:::step{type=recap}
You can now:

- write `async fn`s and `.await` them inside a Tokio runtime;
- start many tasks at once with a `JoinSet` and gather their answers;
- put a time limit on any future with `timeout`, and know that it is dropped;
- choose async for waiting and threads for computing.

Next, chapter 27: how fast Rust really is, against Python.

:::photo{src="/lesson-images/rust/rs-26-notes.webp" alt="Handwritten notes about async: async fn gives a future; Nothing runs until .await; JoinSet: many at once; timeout drops the slow one; Async for waiting, threads for work" ai="true"}
One page of notes for this chapter.
:::
:::
