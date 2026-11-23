:::step{type=story title="9,999 kW from a 2,500 kW turbine"}
Turbine T12's log says it made **9,999 kW** at 10:30. A turbine rated at 2,500 kW cannot do that: it is the meter
glitch from chapter 7, and this time Windwatch should refuse the line with a clear reason, not cap it silently.

Error messages in `String`s worked in chapter 15, but a program cannot do much with a string except print it. Code
that wants to **react** (skip glitches but stop on a missing file, count each kind of problem, retry only network
errors) needs errors it can match on. Rust's answer is an **enum of errors**, one variant per kind of problem, each
with its data and its message. The **thiserror** crate writes the boilerplate for such an enum.

The program at the top (`main`) has a different need: collect any error, add **where** it happened ("data/t12.log,
line 3") and print it. The **anyhow** crate does exactly that. Library code uses thiserror; application code uses
anyhow. This is how most real Rust programs are written.

:::mission
Add a "too much power" variant to Windwatch's error enum and return it, then load a log file with anyhow, adding the
file and line to every error.
:::
:::

:::step{type=concept title="Crates from crates.io" file="16-error-types/Cargo.toml" line="6-8"}
This chapter's `Cargo.toml` uses two crates other people wrote:

```toml
[dependencies]
anyhow = "=1.0.105"
thiserror = "=2.0.21"
```

Cargo downloads a crate (and the crates it needs) from **crates.io**, compiles it once, and links it into your program.
Here they are already downloaded and compiled for you, because the lab has no internet. `=1.0.105` pins the exact
version, so every machine builds the same thing; `Cargo.lock` records the rest.
:::

:::step{type=concept title="An error enum with thiserror" file="16-error-types/src/lib.rs" line="14-24"}
```rust
#[derive(Debug, Error, PartialEq)]
pub enum ReadingError {
    #[error("expected 4 fields, found {found}")]
    FieldCount { found: usize },
    #[error("{field} is not a number: {text:?}")]
    BadNumber { field: &'static str, text: String },
}
```

`#[derive(Error)]` (from thiserror) makes `ReadingError` a real error type, and each `#[error("...")]` becomes that
variant's message, filled in from its fields. Callers can `match` on the variant to decide what to do, and print it
with `{}` for people. `&'static str` for `field` means "a fixed name written in the program", like `"power"`.
:::

:::step{type=task task=error_enum title="Your turn: a variant for glitches" file="16-error-types/src/lib.rs" line="14-41"}
Add the variant `TooMuchPower { kw: f64 }` with `#[error("power {kw} kW is more than the turbine's 2500 kW")]`, and in
`parse_reading`, when `power_kw > 2_500.0`, return `Err(ReadingError::TooMuchPower { kw: power_kw })`.

Press **Check**.
:::

:::step{type=concept title="anyhow: any error, with context" file="16-error-types/src/lib.rs" line="42-50"}
`anyhow::Result<T>` is a `Result` whose error can be **any** error type. Its `Context` trait adds a sentence of context
on top of the error, without losing it:

```rust
let text = fs::read_to_string(path).with_context(|| format!("cannot read {path}"))?;
let reading = parse_reading(line).with_context(|| format!("{path}, line {}", n + 1))?;
```

`with_context` takes a closure (chapter 20), so the message is only built when there really is an error. When
`main` returns an anyhow error, it prints the context first and the original cause underneath ("Caused by: ...").

:::diagram{name="rs-error-chain"}
The low-level cause stays at the bottom; each layer adds where it happened on top, and main prints the whole chain.
:::
:::

:::step{type=history title="Error handling, as a community decision"}
:::before{title="Every crate its own way"}
In Rust's first years every library invented its own error handling, and programs had to convert between them by
hand.
:::

The Rust community tried several helper crates (`error-chain` in **2016**, `failure` in **2017**) before settling on two
small ones by David Tolnay in **2019**: **thiserror** for libraries (precise error enums) and **anyhow** for
applications (any error, with context). They are among the most downloaded crates on crates.io, and both work with
the standard `Error` trait, so they mix freely.

:::solved
**Precise errors inside, readable errors outside.** Libraries say exactly what went wrong; programs say where.
:::

:::timeline
- **2016** error-chain.
- **2017** failure.
- **2019** thiserror and anyhow.
:::
:::

:::step{type=task task=load_with_context title="Your turn: load a file, with context" file="16-error-types/src/lib.rs" line="42-50"}
Finish `load(path)`: read the file with `fs::read_to_string(path).with_context(|| format!("cannot read {path}"))?`, then
`for (n, line) in text.lines().enumerate()`, parse each with `parse_reading(line).with_context(|| format!("{path}, line
{}", n + 1))?` and push it; return `Ok(readings)`.

```bash run
cd /workspace/16-error-types && cargo run -- data/t12.log
```

(`--` passes what follows to your program instead of to Cargo.)

Press **Check**.
:::

:::step{type=try title="A good file, a glitch, and a file that is not there"}
```text
$ cargo run -q -- data/t07.log
data/t07.log: 3 readings, average 2173 kW
$ cargo run -q -- data/t12.log
Error: data/t12.log, line 3

Caused by:
    power 9999 kW is more than the turbine's 2500 kW
$ cargo run -q -- data/t99.log
Error: cannot read data/t99.log

Caused by:
    No such file or directory (os error 2)
```

The good file loaded. The glitch file stopped at **line 3**, and the message has two layers: where (the context added
by `load`) and why (the `TooMuchPower` message from your variant). The missing file got the same treatment, with the
operating system's reason underneath. Nobody had to write a `match` in `main`: `?` and anyhow did it, and the program
exited with a failure code that scripts can see.

Whether a glitch should stop the whole load is a decision: a nightly report might skip it and count it instead. With an
enum, that code is easy to write: `Err(ReadingError::TooMuchPower { .. }) => glitches += 1`.
:::

:::step{type=predict title="Guess first"}
:::question
`load` returns `anyhow::Result`, and `parse_reading` returns `Result<Reading, ReadingError>`. Why does `?` work between
them?
:::
- [ ] It does not compile
- [x] anyhow's error can be made from any type that implements `Error`, and `?` converts it automatically
- [ ] Because both are called Result
:::explain
`?` calls `From::from` on the error. thiserror's derive makes `ReadingError` a real `Error`, so the conversion exists.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why use an enum (thiserror) in the library instead of `String` errors?
:::
- [x] Callers can match on the kind of error and react differently
- [ ] Enums print better
- [ ] Strings cannot be errors
:::explain
`String` errors can only be shown; enum errors can be handled.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `with_context` add to an error?
:::
- [ ] It replaces the error
- [x] A message about where it happened, on top of the original cause
- [ ] A retry
:::explain
The cause is kept underneath, so nothing is lost.
:::
:::

:::step{type=deep-dive title="Go deeper: errors in real programs"}
**`#[from]`.** `#[error("cannot read the log")] Io(#[from] std::io::Error)` lets `?` turn an I/O error into your
enum automatically.

**Exit codes.** When `main` returns `Err`, the process exits with code 1, so shell scripts and schedulers notice.

**Backtraces.** Set `RUST_BACKTRACE=1` to see where a panic happened, function by function.
:::

:::step{type=recap}
You can now:

- use crates from crates.io, pinned in `Cargo.toml`;
- define an error enum with thiserror, one variant and message per kind of problem;
- return any error from a program with anyhow, adding context at each layer;
- read a two-layer error message: where, and why.

That ends Part 4. Next, chapter 17: generics, code that works for many types.

:::photo{src="/lesson-images/rust/rs-16-notes.webp" alt="Handwritten notes about your own error types: Library: thiserror enum; #[error('...')] = the message; App: anyhow::Result; with_context = where; Caused by: = why" ai="true"}
One page of notes for this chapter.
:::
:::
