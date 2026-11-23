:::step{type=story title="Which reading does the answer point to?"}
Windwatch compares two readings and returns the stronger one, without copying it: a reference to whichever is
larger. Simple, until the compiler refuses to build it. The answer is a reference into `a` **or** into `b`, decided
when the program runs. The compiler must make sure the answer is not used after its reading is gone, and from the
signature alone it cannot tell which reading that is.

The fix is a **lifetime**: a name, like `'a`, for "how long a reference is valid". Writing it does not change how long
anything lives; it tells the compiler how the inputs and the output are connected, so it can check every caller.

Lifetimes also allow one of Rust's best tricks: a struct that **borrows** from a log line instead of copying it,
splitting millions of lines without making a single new `String`.

:::mission
Add the lifetime that lets `stronger` compile, then parse a log line into a `LogLine` whose fields all borrow from the
line.
:::
:::

:::step{type=concept title="Naming a lifetime" file="19-lifetimes/src/lib.rs" line="17-24"}
Without lifetimes, the function does not compile:

```text
error[E0106]: missing lifetime specifier
```

The compiler adds a helpful sketch, the same one this TODO shows:

```rust
pub fn stronger<'a>(a: &'a Reading, b: &'a Reading) -> &'a Reading {
    if b.power_kw > a.power_kw { b } else { a }
}
```

Read `'a` as "some stretch of the program". The signature says: both inputs are valid for at least `'a`, and the
result is valid for `'a` too. The compiler then checks each call: the result may be used only while **both** readings
are still alive.

Most functions need no lifetimes at all: with a single reference input (`fn turbine_id(line: &str) -> &str`, chapter
8), the compiler connects input and output on its own (the **elision** rules). Only when it cannot guess, you write
them.
:::

:::step{type=task task=stronger title="Your turn: connect the inputs and the output" file="19-lifetimes/src/lib.rs" line="17-24"}
Change the signature to `pub fn stronger<'a>(a: &'a Reading, b: &'a Reading) -> &'a Reading`, and remove the TODO.

Press **Check**. (This crate does not compile until this is done, so do this task first.)
:::

:::step{type=concept title="A struct that borrows" file="19-lifetimes/src/lib.rs" line="26-43"}
```rust
pub struct LogLine<'a> {
    pub turbine: &'a str,   // a view into the line, not a copy
    pub time: &'a str,
    pub wind: &'a str,
    pub power: &'a str,
}
```

`LogLine<'a>` says: a `LogLine` may not outlive the text its fields point into. In return, parsing costs nothing but
finding the commas. Keep the `LogLine` longer than its line, and the compiler shows exactly where:

```text
error[E0597]: `line` does not live long enough
 --> 19-lifetimes/src/bin/too_short.rs:7:32
  |
6 |         let line = String::from("T07,2026-11-24 10:10,12.4,2100");
  |             ---- binding `line` declared here
7 |         first = LogLine::parse(&line);
  |                                ^^^^^ borrowed value does not live long enough
8 |     }
  |     - `line` dropped here while still borrowed
9 |     println!("{first:?}");
  |                ----- borrow later used here
```

In C, this program would compile, and print whatever happened to be in that memory, or crash.

:::diagram{name="rs-lifetime"}
The LogLine's four fields point into the line; when the line is dropped, using the LogLine would read freed memory.
:::
:::

:::step{type=history title="Regions, from research to everyday code"}
:::before{title="Pointers with no expiry date"}
A pointer in C carries no information about how long the memory it points to stays valid. Using one too late is
a "dangling pointer", among the most common security bugs.
:::

In **1994** Mads Tofte and Jean-Pierre Talpin described **region-based memory management** for ML: the compiler works
out a region (a lifetime) for every value. **Cyclone** (**2002**), a safe dialect of C from AT&T and Cornell, gave
programmers region annotations on pointers. Rust's lifetimes descend from both, and since **2018** the compiler infers
far more of them (non-lexical lifetimes), so most code never writes one.

:::solved
**References that cannot dangle**, checked when compiling, with annotations only where the compiler needs a hint.
:::

:::timeline
- **1994** Region-based memory for ML.
- **2002** Cyclone: regions on pointers.
- **2018** Non-lexical lifetimes in Rust.
:::
:::

:::step{type=task task=zero_copy title="Your turn: parse without copying" file="19-lifetimes/src/lib.rs" line="34-43"}
Finish `LogLine::parse`: take `let turbine = fields.next()?;`, then `time`, `wind` and `power` the same way; if
`fields.next().is_some()` (a fifth field), return `None`; otherwise return `Some(LogLine { turbine, time, wind,
power })`.

```bash run
cd /workspace/19-lifetimes && cargo run --bin ch19-lifetimes
```

Press **Check**.
:::

:::step{type=try title="Views into one string"}
```text
$ cargo run -q --bin ch19-lifetimes
stronger: T07
LogLine { turbine: "T07", time: "2026-11-24 10:10", wind: "12.4", power: "2100" }
LogLine { turbine: "T12", time: "2026-11-24 10:10", wind: "7.5", power: "140" }
not a log line: "broken line"
```

`stronger` returned a reference to T07's reading (2,100 against 140 kW). The two `LogLine`s are eight views into one
`String`, `log`: no field was copied. The broken line has one field, so the first `?` after it returned `None`.

The check also confirms the "no copy" part: it compares the address of `turbine` with the address of the line, and they
are the same.
:::

:::step{type=predict title="Guess first"}
:::question
`fn first_field(line: &str) -> &str` (one reference in, one out). Does it need a lifetime annotation?
:::
- [ ] Yes, always
- [x] No: with one reference input, the compiler connects it to the output by itself
- [ ] Only if it is public
:::explain
That is the elision rule. Two reference inputs and a reference output is when you must say which.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Does `'a` make a value live longer?
:::
- [ ] Yes, as long as `'a`
- [x] No: it only describes how references are connected, so the compiler can check them
- [ ] Only for structs
:::explain
Lifetimes are checked, never enforced at run time. They cost nothing.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is `LogLine<'a>` faster than a struct with four `String` fields?
:::
- [x] It allocates nothing: its fields point into the line
- [ ] `&str` is a smaller number
- [ ] It is not faster
:::explain
For millions of lines, skipping four allocations per line is most of the work saved.
:::
:::

:::step{type=deep-dive title="Go deeper: lifetimes in practice"}
**`'static`.** Text written in the program (`"storm stop"`) lives as long as the program: `&'static str`.

**Owned versus borrowed.** When a struct must outlive its source (stored in a list for later), give it owned `String`s;
borrow when the data is used and dropped while the source exists.

**Fighting the borrow checker.** If lifetime annotations spread everywhere, a value probably wants to own its data;
`.to_string()` or `.clone()` at the edge is often the simpler design.
:::

:::step{type=recap}
You can now:

- name a lifetime and connect a function's inputs to its output;
- recognise when elision makes annotations unnecessary;
- define a struct that borrows, for parsing without copying;
- read E0106 and E0597, and know what they prevent.

Next, chapter 20: closures, functions you can keep in a variable.

:::photo{src="/lesson-images/rust/rs-19-notes.webp" alt="Handwritten notes about lifetimes: Lifetime = how long a borrow lives; Two inputs, one output: name it; One input: no need; Structs can borrow too; No dangling references" ai="true"}
One page of notes for this chapter.
:::
:::
