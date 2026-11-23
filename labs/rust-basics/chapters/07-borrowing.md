:::step{type=story title="Lend it, don't give it away"}
To work out a turbine's average power, a function only needs to **read** the log. To clean up a meter glitch, a
function needs to **change** some readings. Neither should take the log away from its owner, as chapter 6's moves did.

In daily life you lend things: a book to a friend who reads it and gives it back; a pen to someone who writes with it.
Rust's word for lending is **borrowing**, and its symbol is `&`. A borrowed value has rules, and the compiler enforces
them so strictly that one of Rust's most famous error messages comes from here. Those rules are also why a Rust program
cannot read a list while another part of it is changing that list.

:::mission
Average a log by borrowing it to read, then cap glitched readings by borrowing it to change it, in place.
:::
:::

:::step{type=concept title="References: & and &mut" file="07-borrowing/src/lib.rs" line="3-11"}
```rust
pub fn average_power(log: &Vec<f64>) -> f64 { ... }   // borrows the log, to read it
average_power(&log)                                     // lend it; the caller still owns log

pub fn cap_readings(log: &mut Vec<f64>, max_kw: f64)   // borrows the log, to change it
cap_readings(&mut log, 2500.0)                          // lend it for changing (log must be mut)
```

A **reference** (`&log`) points at a value without owning it. When the function ends, the reference is gone and the
owner still has its value. To change the value through a reference, use `*` to reach the value itself:
`*kw = max_kw;` (read it as "the value kw points at").
:::

:::step{type=task task=average_power title="Your turn: an average, on loan" file="07-borrowing/src/lib.rs" line="3-11"}
Finish `average_power(log)`: add the readings with `for kw in log { total += kw; }` (start with `let mut total = 0.0;`)
and return `total / log.len() as f64`.

Press **Check**.
:::

:::step{type=concept title="The borrowing rules" file="07-borrowing/src/main.rs" line="4-12"}
At any moment, a value can have **either**:

- any number of **shared** references (`&`), all only reading, **or**
- exactly **one** **mutable** reference (`&mut`), and nothing else.

And no reference may live longer than the value it points at. Break either rule, and the program does not compile.
Here, `first` reads the vector while `push` tries to change it:

```text
error[E0502]: cannot borrow `log` as mutable because it is also borrowed as immutable
 --> 07-borrowing/src/bin/conflict.rs:4:5
  |
3 |     let first = &log[0];
  |                  --- immutable borrow occurs here
4 |     log.push(1980.0);
  |     ^^^^^^^^^^^^^^^^ mutable borrow occurs here
5 |     println!("first reading: {first}");
  |                               ----- immutable borrow later used here
```

This is not pickiness. `push` may need more room, and then the whole vector **moves** to a new block of memory. `first`
would point at the old block, already given back: in C this is a real, common crash. Rust refuses to build it.

A function cannot return a reference to something it owns, either, because the owner is dropped when the function
ends:

```text
error[E0106]: missing lifetime specifier
 --> 07-borrowing/src/bin/dangling.rs:1:16
  |
1 | fn latest() -> &Vec<f64> {
  |                ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but there is no value for it to be borrowed from
...
help: instead, you are more likely to want to return an owned value
  |
1 - fn latest() -> &Vec<f64> {
1 + fn latest() -> Vec<f64> {
```

(Shortened with "...".) "There is no value for it to be borrowed from": return the vector itself, not a reference to
it. Chapter 19 explains lifetimes, the compiler's word for "how long a reference is valid".

:::diagram{name="rs-borrow"}
Many readers, or one writer: why push is refused while a reference into the vector is still in use.
:::
:::

:::step{type=history title="Readers, writers and a rule from 1971"}
:::before{title="Two hands on one list"}
When one part of a program changes data that another part is reading, the reader sees half-changed data, or memory
that has moved away. In programs with threads this is a data race, among the hardest bugs to find.
:::

In **1971** Courtois, Heymans and Parnas described the **readers-writers** problem: many readers may share data at
once, but a writer needs it alone. Databases and operating systems enforce that rule at run time, with locks. Rust's
borrow checker enforces the same rule ("many readers, or one writer") when compiling, inside a single thread too.
In chapter 25 the same rule is what lets Windwatch check 40 turbines on 40 threads without a data race.

:::solved
**No reading while changing.** Whole families of crashes (iterator invalidation, use-after-free, data races) cannot be
compiled.
:::

:::timeline
- **1971** The readers-writers problem.
- **2015** Rust: the rule checked when compiling.
- **2018** Smarter borrow checking (non-lexical lifetimes).
:::
:::

:::step{type=task task=cap_readings title="Your turn: cap the glitches, in place" file="07-borrowing/src/lib.rs" line="13-18"}
A meter glitch sometimes reports 9,999 kW from a turbine that can make 2,500. Finish `cap_readings(log, max_kw)`:
`for kw in log.iter_mut()` gives a `&mut f64` for each reading; where `*kw > max_kw`, set `*kw = max_kw`.

```bash run
cd /workspace/07-borrowing && cargo run --bin ch07-borrowing
```

Press **Check**.
:::

:::step{type=try title="One glitch, and a wrong average"}
```text
$ cargo run -q --bin ch07-borrowing
T07: [2100.0, 2250.0, 9999.0, 1980.0], average 4082 kW
capped: [2100.0, 2250.0, 2500.0, 1980.0], average 2208 kW
first 2100 kW, last 1980 kW, still 4 readings
```

One impossible reading pushed T07's average to **4,082 kW**, more than the turbine's whole rating. After capping, the
average is a believable **2,208 kW**. Both functions borrowed the same vector (`&log`, then `&mut log`, then `&log`
again), one at a time, and `main` still owns it at the end: "still 4 readings".

The last line takes two shared references at once (`first` and `last`): any number of readers is fine.

Capping is a choice, not the only answer: a careful monitor might drop the glitch, or flag it for a person. Chapter 15
shows how to report bad readings as errors.
:::

:::step{type=predict title="Guess first"}
:::question
`let r1 = &mut log; let r2 = &mut log; r1.push(1.0);` Does it compile?
:::
- [ ] Yes
- [x] No: two mutable references to `log` are alive at the same time
- [ ] Only if `log` is empty
:::explain
One writer at a time. Use `r1` and stop using it before making `r2`, and it compiles.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `average_power` take `&Vec<f64>` instead of `Vec<f64>`?
:::
- [x] It only reads the log, so it borrows it and the caller keeps it
- [ ] References are faster to type
- [ ] Vectors cannot be passed by value
:::explain
Taking ownership would move the log into the function, and the caller could not use it again.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `*kw = max_kw;` change?
:::
- [ ] The reference
- [x] The reading in the caller's vector that `kw` points at
- [ ] A copy that is thrown away
:::explain
`*` reaches through the reference to the value it points at.
:::
:::

:::step{type=deep-dive title="Go deeper: borrowing in practice"}
**Non-lexical lifetimes.** Since 2018 a borrow ends at its **last use**, not at the end of the block, so code like
`let first = log[0]; log.push(x);` (a copy, not a reference) and many other patterns compile.

**Methods borrow too.** `log.len()` borrows `log` to read it; `log.push(x)` borrows it mutably. The `.` does the `&` for
you.

**When the borrow checker says no.** Usually the fix is to finish reading before you change (copy the value out, or
restructure), not to fight it.
:::

:::step{type=recap}
You can now:

- lend a value with `&` to read it, and with `&mut` to change it;
- state the rules: many readers or one writer, and no reference outlives its value;
- read E0502 and E0106 and know why they protect you;
- change values in place through `iter_mut()` and `*`.

Next, chapter 8: slices and strings, borrowed views of part of a value.

:::photo{src="/lesson-images/rust/rs-07-notes.webp" alt="Handwritten notes about borrowing: &x = borrow to read; &mut x = borrow to change; Many readers OR one writer; No reference outlives its value; *r = the value behind r" ai="true"}
One page of notes for this chapter.
:::
:::
