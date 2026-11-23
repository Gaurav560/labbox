:::step{type=story title="A gust is not a trend"}
At 10:30 turbine T07 jumps to 2,490 kW, and at 10:40 it drops to 1,650. Is it failing? Probably not: a gust came and
went. Engineers look at a **moving average** instead of single readings: the average of the last three readings,
then of the next three, sliding along the log. A gust becomes a small bump; a real drop stays a drop.

Windwatch also writes alerts for people: "T07, T12 and T31 need a visit". Getting the commas and the "and" right
for one, two or many turbines is a small puzzle every program that writes sentences has to solve.

Both are jobs for Rust's two workhorse types: `Vec<T>`, a list that can grow, and `String`, text that can grow. You have
used them since chapter 6; this chapter shows what they can do.

:::mission
Smooth a turbine's log with a moving average over sliding windows, then turn a list of turbine ids into a proper
sentence.
:::
:::

:::step{type=concept title="Vec: a list that grows" file="13-vec-and-string/src/main.rs" line="4-14"}
| Want | Write |
|---|---|
| a new one | `Vec::new()`, or `vec![1.0, 2.0]` |
| add at the end | `v.push(x)` |
| how many | `v.len()`, `v.is_empty()` |
| read one | `v[2]` (panics past the end), `v.get(2)` (an `Option`) |
| sort | `v.sort()`, and for `f64`, `v.sort_by(\|a, b\| a.total_cmp(b))` |
| remove repeats next to each other | `v.dedup()` (sort first) |
| look at every run of n | `v.windows(n)` gives each slice of n in a row |
| split into groups of n | `v.chunks(n)` |

A `Vec` keeps its numbers side by side on the heap, with room to spare: when it runs out of room it moves to a block
about twice as big, which is why a `push` is fast on average.

`sort()` on a vector of `f64` does not compile:

```text
error[E0277]: the trait bound `{float}: Ord` is not satisfied
 --> 13-vec-and-string/src/bin/sort_f64.rs:3:9
  |
3 |     log.sort();
  |         ^^^^ the trait `Ord` is not implemented for `{float}`
...
```

(Shortened with "...".) Floating-point numbers include **NaN** ("not a number", from 0.0 / 0.0), which is neither
smaller nor larger than anything, so `f64` has no complete order. `total_cmp` gives one, with NaN at the end. The
`|a, b| a.total_cmp(b)` is a **closure**, a small function written in place; chapter 20 explains them.
:::

:::step{type=task task=moving_average title="Your turn: a moving average" file="13-vec-and-string/src/lib.rs" line="3-10"}
Finish `moving_average(log, window)`: `let mut averages = Vec::new();`, then `for group in log.windows(window)`, add up
the group, `averages.push(total / window as f64)`, and return `averages`.

Press **Check**.
:::

:::step{type=history title="Arrays that grow"}
:::before{title="Fixed sizes"}
In early languages a list's size was fixed when the program was written. Programs guessed a maximum, wasted memory, or
crashed when the guess was wrong.
:::

Growable arrays appeared in **Lisp** and **Smalltalk**, and became everyday tools with C++'s **std::vector** (part of
the Standard Template Library, accepted into C++ in **1994**) and Java's `ArrayList` (**1998**). The trick behind all
of them is the same: keep spare room, and when it runs out, double it. Rust's `Vec` uses it too, and adds what the
others could not: the borrow checker makes sure nobody holds a reference into the old block when the vector moves
(chapter 7).

:::solved
**Lists of any length**, fast to add to, and safe to grow while other code looks at them, because it cannot.
:::

:::timeline
- **1994** std::vector in C++.
- **1998** ArrayList in Java.
- **2015** Rust's Vec: growth checked by the borrow checker.
:::
:::

:::step{type=concept title="Building a String" file="13-vec-and-string/src/lib.rs" line="12-23"}
```rust
let mut text = String::new();
text.push_str("T07");        // add a &str
text.push_str(", ");
text += "T12";               // += works too
let line = format!("{text} and T31");
```

`as_sentence` uses a slice pattern from chapter 11 to handle each case: `[]` (none), `[only]` (one), and
`[rest @ .., last]`: everything but the last in `rest`, and the last one by itself. `for (i, id) in
rest.iter().enumerate()` gives each item with its position, so the comma goes before every item but the first.

:::diagram{name="rs-windows"}
windows(3) slides along the log one reading at a time; each window becomes one average.
:::
:::

:::step{type=task task=as_sentence title="Your turn: ids as a sentence" file="13-vec-and-string/src/lib.rs" line="12-23"}
In the `[rest @ .., last]` arm, build the text: push each id of `rest` with `", "` before every one but the first,
then push `" and "` and `last`, and return the text.

```bash run
cd /workspace/13-vec-and-string && cargo run --bin ch13-vec-and-string
```

Press **Check**.
:::

:::step{type=try title="A gust, smoothed"}
```text
$ cargo run -q --bin ch13-vec-and-string
readings: [2100.0, 2180.0, 2490.0, 1650.0, 2210.0, 2240.0]
average of 3: [2256.6666666666665, 2106.6666666666665, 2116.6666666666665, 2033.3333333333333]
lowest 1650, highest 2490
underperforming: T07, T12 and T31
faulty: no turbines
Windwatch: T07 needs a visit (28 bytes, room for 44)
```

The raw readings swing by 840 kW between 10:30 and 10:40. The moving averages stay between 2,033 and 2,257: the gust
and the drop cancel out, and nobody gets called out. Six readings with a window of three give **four** averages.

The averages print with every digit: `{:.0}` would round them for people. The ids were sorted and deduplicated
(`T07` appeared twice), then joined into a sentence; an empty list said "no turbines". The last line shows a `String`
keeping spare room: 28 bytes used, room for 44, so the next few pushes need no new memory.
:::

:::step{type=predict title="Guess first"}
:::question
How many windows does `[1.0, 2.0, 3.0, 4.0, 5.0].windows(2)` give?
:::
- [ ] 5
- [x] 4: [1,2], [2,3], [3,4], [4,5]
- [ ] 2
:::explain
A list of n items has n - w + 1 windows of size w (and none if it is shorter than w).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `vec_of_f64.sort()` not compile?
:::
- [x] `f64` has no complete order, because of NaN; use `sort_by` with `total_cmp`
- [ ] Vectors cannot be sorted
- [ ] It must be `mut`
:::explain
Rust makes you choose how NaN is ordered instead of guessing.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `v.get(10)` return on a vector of 3 items?
:::
- [ ] It panics
- [x] `None`
- [ ] 0
:::explain
`v[10]` panics; `v.get(10)` lets you handle the missing item.
:::
:::

:::step{type=deep-dive title="Go deeper: vectors and strings in practice"}
**Capacity.** `Vec::with_capacity(4320)` (a month of ten-minute readings) allocates once instead of growing.

**Removing.** `v.retain(|kw| *kw >= 0.0)` keeps only what passes a test; `v.swap_remove(i)` removes fast when order does
not matter.

**Joining.** `ids.join(", ")` joins with one separator; `as_sentence` needed two.
:::

:::step{type=recap}
You can now:

- create, grow, sort and search a `Vec`, and sort `f64` with `total_cmp`;
- slide over a list with `windows` and average each window;
- build a `String` with `push_str`, `+=` and `format!`;
- turn a list into a sentence with slice patterns.

Next, chapter 14: maps and sets, to group readings by turbine.

:::photo{src="/lesson-images/rust/rs-13-notes.webp" alt="Handwritten notes about vectors and strings: Vec: push, len, get, sort; f64 sort: sort_by + total_cmp; windows(3) = runs of three; String: push_str, +=, format!; get(i) gives an Option" ai="true"}
One page of notes for this chapter.
:::
:::
