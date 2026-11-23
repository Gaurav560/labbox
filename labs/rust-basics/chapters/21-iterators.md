:::step{type=story title="A year of readings, in four milliseconds"}
A year of Windwatch data is 40 turbines × 6 readings an hour × 24 hours × 365 days: **2,102,400 readings**. The board
asks questions of it all the time: total energy, the turbines that are weak in strong wind, the worst hour of the month.

Each question can be a `for` loop with counters and `if`s, or a chain of small steps: take the readings, keep the
strong-wind ones, keep the weak ones, take their ids, collect. The chain reads like the question. The worry, in many
languages, is that each step costs: function calls, temporary lists. This chapter measures it.

:::mission
Total a log's energy with one iterator chain, list the turbines that are weak in strong wind with filter and map, then
time an iterator against a hand-written loop over a year of readings.
:::
:::

:::step{type=concept title="Iterators: lazy steps, one consumer" file="21-iterators/src/lib.rs" line="16-29"}
```rust
readings.iter()                                   // each &Reading in turn
    .filter(|r| r.wind_ms >= 12.0)               // keep some
    .map(|r| r.turbine.as_str())                 // turn each into something else
    .collect::<Vec<&str>>()                      // run it all, and gather the results
```

| Kind | Examples | What it does |
|---|---|---|
| start | `.iter()`, `.iter_mut()`, `.into_iter()`, `0..24`, `.lines()`, `.chars()` | gives items one at a time |
| adapter | `.map()`, `.filter()`, `.enumerate()`, `.zip()`, `.take(n)`, `.skip(n)` | makes a new step; does **nothing yet** |
| consumer | `.sum()`, `.count()`, `.max_by()`, `.collect()`, `.any()`, `.for_each()` | runs the chain |

Adapters are **lazy**: until a consumer asks for items, no work happens. Then each item flows through all the steps
before the next item starts, so no temporary lists are made. `sum::<f64>()` names the type to add up into.

:::diagram{name="rs-iterator-chain"}
Items flow one at a time through every step; nothing happens until collect asks, and no list is made in between.
:::
:::

:::step{type=task task=total_energy title="Your turn: total energy in one chain" file="21-iterators/src/lib.rs" line="16-21"}
Finish `total_energy_mwh(readings)`: `readings.iter().map(|r| r.power_kw * 10.0 / 60.0).sum::<f64>() / 1_000.0`.

Press **Check**.
:::

:::step{type=history title="Zero-cost abstractions"}
:::before{title="Convenience, or speed"}
High-level code used to mean slower code: each layer of abstraction added calls and temporary data that a hand-written
loop avoided.
:::

Barbara Liskov's **CLU** (**1975**) introduced iterators as a language feature. Bjarne Stroustrup stated the goal C++
aimed for as the **zero-overhead principle**: "what you don't use, you don't pay for, and what you do use, you couldn't
hand-code any better". Rust's iterators are built for that: each adapter is a small struct, the compiler knows the whole
chain's types (generics, chapter 17), and in an optimised build it merges the steps into one loop, the same machine
code you would have written by hand. Whether that is true here is what the try step measures.

:::solved
**Code that reads like the question, running like a hand-written loop.**
:::

:::timeline
- **1975** Iterators in CLU.
- **1990s** C++'s zero-overhead principle.
- **2015** Rust iterators: lazy, generic, inlined.
:::

Barbara Liskov, whose language CLU had iterators in 1975, decades before most languages did.

:::photo{src="/lesson-images/rust/liskov.webp" alt="Barbara Liskov, a woman with short curly hair in a light blue shirt with a flower pattern" credit="Kenneth C. Zirkel" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Barbara_Liskov_MIT_computer_scientist_2010.jpg"}
Barbara Liskov at MIT, 2010.
:::
:::

:::step{type=task task=weak_turbines title="Your turn: weak in strong wind" file="21-iterators/src/lib.rs" line="23-29"}
Finish `weak_in_strong_wind(readings)`: `readings.iter()`, `.filter(|r| r.wind_ms >= 12.0 && r.wind_ms < 25.0)`,
`.filter(|r| r.power_kw < 2_000.0)`, `.map(|r| r.turbine.as_str())`, `.collect()`.

```bash run
cd /workspace/21-iterators && cargo run --release
```

```bash run
cd /workspace/21-iterators && cargo run
```

Press **Check**.
:::

:::step{type=try title="Iterator against loop, release against debug"}
`main.rs` builds a year of made-up readings (2,102,400 of them) and totals them 20 times with each version:

```text
$ cargo run -q --release
energy: 1.008 MWh
weak in strong wind: ["T12"]
iterator: 595648.6 MWh, 4.05 ms a pass
    loop: 595648.6 MWh, 4.21 ms a pass
$ cargo run -q
energy: 1.008 MWh
weak in strong wind: ["T12"]
iterator: 595648.6 MWh, 12.99 ms a pass
    loop: 595648.6 MWh, 9.59 ms a pass
```

In the **release** build (optimised), the iterator and the loop take the same time, about 4 ms to total two million
readings: about half a billion readings a second. The small difference is noise between runs; neither is faster.

In the **debug** build (`cargo run` without `--release`), the iterator is slower than the loop (13.0 against 9.6 ms), and
both are about three times slower than release. Debug builds keep every step as a real function call so a debugger
can stop in it. "Zero cost" is a promise about optimised code. Measure in release, always.
:::

:::step{type=predict title="Guess first"}
:::question
`readings.iter().map(|r| { println!("seen"); r.power_kw });` with no consumer. How many times is "seen" printed?
:::
- [ ] Once per reading
- [x] Never: adapters are lazy, and nothing consumed the chain
- [ ] Once
:::explain
The compiler even warns: "iterators are lazy and do nothing unless consumed".
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why was the iterator as fast as the loop in release?
:::
- [x] The optimiser merged the chain into one loop, like the hand-written one
- [ ] Iterators run on several threads
- [ ] The loop was slow
:::explain
Generics and inlining let the compiler see the whole chain at once.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where should you measure Rust's speed?
:::
- [ ] In debug builds
- [x] In release builds (`--release`)
- [ ] It does not matter
:::explain
Debug builds trade speed for debuggability; they can be several times slower.
:::
:::

:::step{type=deep-dive title="Go deeper: iterators in practice"}
**Ownership.** `.iter()` borrows items, `.iter_mut()` borrows them mutably, `.into_iter()` takes them (the `Vec` is used
up).

**Your own iterator.** Implement the `Iterator` trait (one method, `next`) and every adapter works on your type.

**Parallel.** The `rayon` crate turns `.iter()` into `.par_iter()` and runs the same chain on all cores; chapter 25
does the threads by hand.
:::

:::step{type=recap}
You can now:

- build iterator chains from a start, adapters and a consumer;
- explain laziness, and why no temporary lists are made;
- total, filter, map and collect without counters;
- measure in release, and show that the chain costs what the loop costs.

Next, chapter 22: tests you write yourself.

:::photo{src="/lesson-images/rust/rs-21-notes.webp" alt="Handwritten notes about iterators: iter() -> map / filter -> collect; Adapters are lazy; No lists in between; Release: as fast as a loop; Always measure with --release" ai="true"}
One page of notes for this chapter.
:::
:::
