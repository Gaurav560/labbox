:::step{type=story title="A day of wind at turbine T12"}
A turbine does not simply spin whenever there is wind. Below about **3 m/s** there is too little wind to be worth
turning, so it waits. From **25 m/s**, a storm, it turns its blades out of the wind and stops, to protect itself.
In between, it generates.

Windwatch reads one wind speed an hour from each turbine: 24 numbers a day. From them it should say what each turbine
did, how many hours it made power, and when the first storm stop came. That is a program that **decides** (if this,
then that) and **repeats** (for every hour). Rust's `if` gives back a value, and it has three loops, each with its own
job.

:::mission
Decide a turbine's status from the wind with an if expression, then count a day's generating hours with a for loop.
:::
:::

:::step{type=concept title="if is an expression" file="05-control-flow/src/lib.rs" line="3-9"}
```rust
pub fn status(wind_ms: f64) -> &'static str {
    if wind_ms < 3.0 {
        "too calm"
    } else if wind_ms < 25.0 {
        "generating"
    } else {
        "storm stop"
    }
}
```

The whole `if` is the function's last expression, so its value is returned, the value of whichever branch ran. Each
branch must give the same type, and there are no brackets around the condition.

`&'static str` is the type of a fixed piece of text written in the program, like `"storm stop"`. Chapter 8 explains
text types properly; for now, read it as "some fixed text".

The same works in a `let`: `let state = if running { "on" } else { "off" };`.
:::

:::step{type=task task=status title="Your turn: what the turbine does" file="05-control-flow/src/lib.rs" line="3-9"}
Finish `status(wind_ms)`: below `3.0` return `"too calm"`, below `25.0` return `"generating"`, otherwise
`"storm stop"`.

Press **Check**.
:::

:::step{type=concept title="Three loops" file="05-control-flow/src/lib.rs" line="10-27"}
| Loop | Runs | Use it for |
|---|---|---|
| `for x in things { }` | once for each value | arrays, ranges like `0..24`, lists |
| `while condition { }` | while the condition is true | when you don't know how many times |
| `loop { }` | for ever, until `break` | retrying; `break value` gives the loop a value |

```rust
let mut hours = 0;
for wind in winds {                 // wind takes each of the 24 values in turn
    if status(wind) == "generating" {
        hours += 1;
    }
}
```

`0..24` is a **range**: 0, 1, ... 23 (the end is left out). `0..=24` includes the end.

:::trace{title="for wind in [2.1, 5.6, 26.1]"}
| Step | wind | status(wind) | hours |
|---|---|---|---|
| start | - | - | 0 |
| 1 | 2.1 | too calm | 0 |
| 2 | 5.6 | generating | 1 |
| 3 | 26.1 | storm stop | 1 |
:::
:::

:::step{type=task task=hours_generating title="Your turn: hours of power in a day" file="05-control-flow/src/lib.rs" line="10-16"}
Finish `hours_generating(winds)`: start with `let mut hours = 0;`, loop with `for wind in winds`, add 1 when
`status(wind) == "generating"`, and return `hours`.

```bash run
cd /workspace/05-control-flow && cargo run
```

Press **Check**.
:::

:::step{type=history title="Branches and loops, and the end of GOTO"}
:::before{title="Jumps everywhere"}
Early programs looped and branched with jumps to line numbers. Programs became tangles that nobody could follow.
:::

In **1966** Corrado Böhm and Giuseppe Jacopini proved that any program can be written with just three shapes:
**sequence**, **choice** and **loop**. In **1968** Edsger Dijkstra's letter "Go To Statement Considered Harmful" made
the case that programmers should. Rust has no `goto` at all. Its `loop` with `break value` comes from the same idea:
a loop is a block, and a block can give back a value.

:::solved
**Programs you can read from top to bottom.** Every choice and every loop has a clear start and end.
:::

:::timeline
- **1966** Böhm and Jacopini: three shapes are enough.
- **1968** "Go To Statement Considered Harmful".
- **2015** Rust 1.0: no goto, loops with values.
:::

Edsger Dijkstra, whose 1968 letter asked programmers to build programs only from sequence, choice and loop. Rust has no goto at all.

:::photo{src="/lesson-images/rust/dijkstra.webp" alt="Edsger Dijkstra, an older man with grey hair, a beard and glasses, in a checked shirt and an orange sweater vest" credit="Hamilton Richards" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Edsger_Wybe_Dijkstra.jpg"}
Edsger W. Dijkstra in 2002.
:::
:::

:::step{type=try title="Monday at T12: a calm night, a windy day, a storm"}
```text
$ cargo run -q
 1.8 m/s: too calm
   3 m/s: generating
12.4 m/s: generating
24.9 m/s: generating
  25 m/s: storm stop
31.2 m/s: storm stop
Hours generating: 18
First storm stop at 18:00
T12 answered after 3 tries
```

The edges are right: exactly 3 m/s generates, exactly 25 m/s stops (`{wind:>4}` lined the numbers up to the right).

Monday had **18** generating hours: four calm hours in the night (1.5 to 2.4 m/s) and two storm hours in the evening (26.1
and 28.4 m/s) made nothing. `first_storm_hour` used a `while` loop to find the first storm at 18:00, and the last line
came from a `loop` that broke out with a value on its third try.

`first_storm_hour` returns `Some(18)` or `None`: there may be no storm at all, and Rust has no "null" to stand for
"nothing". That type, `Option`, is chapter 10; `main.rs` already reads it with a `match`.

:::diagram{name="rs-day-loop"}
The for loop walks the 24 hours; each hour's status decides whether the counter moves.
:::
:::

:::step{type=predict title="Guess first"}
:::question
`let n = if wind > 25.0 { "stop" } else { 0 };` Does it compile?
:::
- [ ] Yes, `n` is text or a number
- [x] No: both branches of an if expression must have the same type
- [ ] Only if wind is above 25
:::explain
`n` needs one type, known when compiling. Both branches must agree.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
How many times does `for h in 0..24 { }` run?
:::
- [ ] 25
- [x] 24: 0 to 23, the end is left out
- [ ] 23
:::explain
`0..=23` says the same thing with the end included.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which loop fits "try to reach the turbine until it answers"?
:::
- [x] `loop` with `break`
- [ ] `for` over a range
- [ ] None, use recursion
:::explain
You do not know how many tries it takes; `break` leaves when it answers, and can carry a value out.
:::
:::

:::step{type=deep-dive title="Go deeper: control flow in practice"}
**Labels.** `'outer: for t in turbines { for h in hours { break 'outer; } }` leaves both loops at once.

**Iterators instead of counters.** `winds.iter().filter(|w| status(**w) == "generating").count()` does what your loop
does, in one line. Chapter 21 shows why it is just as fast.

**Floats and edges.** Comparing `wind < 3.0` is fine; comparing computed floats with `==` is not (chapter 3).
:::

:::step{type=recap}
You can now:

- choose between branches with `if`, `else if` and `else`, and use `if` as a value;
- loop with `for` over arrays and ranges, `while` with a condition, and `loop` with `break value`;
- count with a `mut` counter;
- read `Some` and `None`, which chapter 10 explains.

That ends Part 1. Next, chapter 6: ownership, Rust's big idea.

:::photo{src="/lesson-images/rust/rs-05-notes.webp" alt="Handwritten notes about control flow: if is an expression; Both branches: same type; for x in list / 0..24; while, loop + break value; Under 3 calm, from 25 stop" ai="true"}
One page of notes for this chapter.
:::
:::
