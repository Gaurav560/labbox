:::step{type=story title="Forty turbines, one CPU busy"}
Every night Windwatch checks a year of wind for each of the 40 turbines: what power the curve expected, reading by
reading. It does them one after another, on one CPU, while the other CPUs of the server sit idle.

The work for T07 has nothing to do with the work for T12. They could run at the same time, on separate **threads**.
In most languages that is where the trouble starts: two threads touch the same data, and once in a few thousand runs
the answer is wrong. These **data races** are among the hardest bugs to find, because they rarely happen twice the
same way.

Rust makes a strong promise here: if a program has a data race, it **does not compile**. This chapter shows the
promise at work.

:::mission
Total each turbine's log on its own thread and join the results in order, then have each thread send its alerts back
over a channel.
:::
:::

:::step{type=concept title="Scoped threads" file="25-threads/src/lib.rs" line="5-14"}
```rust
thread::scope(|s| {
    let handles: Vec<_> = logs.iter()
        .map(|log| s.spawn(move || log.iter().sum::<f64>()))   // one thread per log, started now
        .collect();                                            // collect first: every thread is running
    handles.into_iter().map(|h| h.join().unwrap()).collect()   // then wait for each, in order
})
```

| Piece | Does |
|---|---|
| `thread::scope(\|s\| ...)` | opens a scope; every thread started in it has finished when the scope ends |
| `s.spawn(move \|\| ...)` | starts a thread running the closure, and returns a handle |
| `h.join()` | waits for that thread and gives its result (an `Err` if it panicked) |

Because the scope waits for its threads, they may **borrow** `logs`: the compiler knows `logs` outlives every
thread. The `collect()` in the middle matters. Without it, the iterator would start one thread and join it before
starting the next, one at a time again.

:::diagram{name="rs-threads"}
Forty threads start at once on the logs they borrow, run on every CPU, and are joined in order before the scope ends.
:::
:::

:::step{type=task task=scoped_threads title="Your turn: a thread per log" file="25-threads/src/lib.rs" line="5-14"}
Finish `parallel_totals(logs)`: inside `thread::scope(|s| { ... })`, start one thread per log with
`s.spawn(move || log.iter().sum::<f64>())`, keep the handles in a `Vec`, then join each one in order and collect the
sums.

Press **Check**.
:::

:::step{type=history title="From semaphores to fearless concurrency"}
:::before{title="Locks, and hoping"}
Threads that share memory need rules about who may touch it when. For decades the rules lived in comments and in
programmers' heads; the compiler could not check them, so one missed lock meant a rare, random wrong answer.
:::

Edsger Dijkstra described **semaphores** in **1965**, the first standard tool for taking turns. Tony Hoare's
**monitors** (**1974**) bundled data with its lock, and his **Communicating Sequential Processes** (**1978**)
proposed something different: threads that share nothing and **send messages** to each other over channels. Go
built its concurrency on that idea (**2009**). Rust's contribution (**2015**) is to check the rules when compiling,
with two marker traits: `Send` (this value may move to another thread) and `Sync` (it may be shared between threads).
The Rust team called it **fearless concurrency**. Scoped threads were in Rust before 1.0, were taken out in **2015**
when a soundness hole was found in their design, and came back, done safely, in Rust 1.63 (**2022**).

:::solved
**Data races caught when compiling.** Sharing something that is not safe to share is a type error, not a bug report.
:::

:::timeline
- **1965** Semaphores (Dijkstra).
- **1978** CSP: processes and channels (Hoare).
- **2015** Rust: Send, Sync, fearless concurrency.
- **2022** Scoped threads in the standard library.
:::
:::

:::step{type=concept title="Channels: threads send, one place receives" file="25-threads/src/lib.rs" line="16-33"}
A **channel** has two ends. `mpsc::channel()` gives `(tx, rx)`: many senders, one receiver (**m**ulti-**p**roducer,
**s**ingle-**c**onsumer). Each thread gets its own clone of `tx` and sends what it found; `rx` receives everything,
in whatever order it arrives.

```rust
let tx = tx.clone();                                      // this thread's own sender
s.spawn(move || {                                         // move: the thread owns tx, id and log references
    let low = log.iter().filter(|&&kw| kw < low_kw).count();
    if low > 0 {
        tx.send(format!("{id}: {low} low readings")).unwrap();
    }
});
```

`rx.iter()` gives messages until every sender has been dropped. That is why the function drops the original `tx`
after the scope: if one sender stayed alive, `rx.iter()` would wait for it forever. Threads that only send messages
share nothing, so there is nothing to lock.
:::

:::step{type=task task=channel_alerts title="Your turn: alerts over a channel" file="25-threads/src/lib.rs" line="18-28"}
In `collect_alerts`, replace the `let _ = ...` line with a thread: `s.spawn(move || { ... })` that counts the log's
readings below `low_kw` and, when there are any, sends `format!("{id}: {low} low readings")` with
`tx.send(...).unwrap()`.

```bash run
cd /workspace/25-threads && cargo run -q --release
```

Press **Check**.
:::

:::step{type=try title="One thread against forty"}
On a 16-thread laptop:

```text
$ cargo run -q --release
this machine has 16 CPU threads
one thread:  2852760917 kW expected in total, 15.9 ms
40 threads:  2852760917 kW expected in total, 3.6 ms
totals: [4280.0, 305.0, 305.0]
alerts: ["T12: 3 low readings", "T19: 1 low readings"]
```

The same total both ways, 4.4 times faster with threads. Not 16 times: starting 40 threads costs time, and 16 ms of work
is very little. Your lab machine has **2** CPUs, so expect about twice as fast there; the first line tells you what
your machine has. More threads than CPUs never makes work faster, it only takes turns.

The channel's alerts came back from three threads in an unknown order and were sorted at the end; T07 sent nothing.

Now the promise. A thread given an `Rc` (chapter 24, whose counter is not safe to change from two threads at once):

```text
error[E0277]: `Rc<Vec<f64>>` cannot be sent between threads safely
 --> 25-threads/src/bin/rc_thread.rs:6:32
  |
6 |     let handle = thread::spawn(move || log.iter().sum::<f64>());
  |                  ------------- -------^^^^^^^^^^^^^^^^^^^^^^^^
  |                  |             |
  |                  |             `Rc<Vec<f64>>` cannot be sent between threads safely
...
  = help: within `{closure@25-threads/src/bin/rc_thread.rs:6:32: 6:39}`, the trait `Send` is not implemented for `Rc<Vec<f64>>`
```

(Shortened with "...".) `Rc` is not `Send`, so this program never runs. The thread-safe version is `Arc` (**a**tomic
reference count), used in chapter 28.
:::

:::step{type=predict title="Guess first"}
:::question
`logs.iter().map(|log| s.spawn(...).join().unwrap()).collect()`: spawn and join in one `map`. How fast is it?
:::
- [ ] As fast as the version with two steps
- [x] No faster than one thread: each thread is joined before the next one starts
- [ ] It does not compile
:::explain
Iterators are lazy (chapter 21): each item goes through spawn and join before the next. Collect the handles first.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why may a scoped thread borrow `logs`, when `thread::spawn` would need it moved or copied?
:::
- [x] The scope waits for all its threads, so `logs` is guaranteed to outlive them
- [ ] Scoped threads copy their data
- [ ] Borrowing is always allowed in threads
:::explain
A plain `thread::spawn` thread may outlive the function, so it may only hold data it owns.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`rx.iter()` never ends. What was forgotten?
:::
- [ ] A `join`
- [x] A sender is still alive (the original `tx` was not dropped), so the receiver keeps waiting for it
- [ ] The channel is full
:::explain
The receiver ends when every sender is gone. `drop(tx)` after the scope is what lets it finish.
:::
:::

:::step{type=deep-dive title="Go deeper: threads in practice"}
**Shared state.** When threads must change one value, `Arc<Mutex<T>>`: `Arc` for shared ownership across threads,
`Mutex` so one thread at a time can `.lock()` it. Chapter 28's web service keeps its readings that way.

**rayon.** For "do this to every item, on every CPU", the `rayon` crate's `.par_iter()` replaces `.iter()`, splits
the work and joins it for you.

**How many.** A thread per CPU is usually right for computing. Waiting is different: a thread per turbine just to
wait on a slow radio link wastes memory. That is chapter 26.
:::

:::step{type=recap}
You can now:

- start threads in a scope, let them borrow, and join them in order;
- send results from many threads to one receiver over a channel, and end it by dropping senders;
- measure the speed-up, and know why it is less than the number of CPUs;
- read E0277 for `Rc`, and know that data races do not compile.

Next, chapter 26: waiting for 40 radios at once, with async.

:::photo{src="/lesson-images/rust/rs-25-notes.webp" alt="Handwritten notes about threads: thread::scope + spawn; Collect handles, then join; Channel: tx sends, rx receives; Rc is not Send: use Arc; Data races do not compile" ai="true"}
One page of notes for this chapter.
:::
:::
