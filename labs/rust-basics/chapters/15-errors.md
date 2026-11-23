:::step{type=story title="Skipped is not enough"}
Chapter 11 turned broken log lines into `None`, and Windwatch kept going. But `None` says nothing about **why**. The
technician who has to fix the sensor needs to know: was the line cut short? Was the wind field `windy`? Was the power
`22O0`, with a letter O? Each answer means a different fix.

There are two kinds of failure in a program. Some are **bugs**: a case that "cannot happen" did happen; stopping the
program (a **panic**) is right. Most are **expected trouble**: a missing file, a bad line, a network that is down.
For those, Rust has no exceptions. A function that can fail returns a **`Result`**: either `Ok(value)` or
`Err(error)`, and the caller must look at it before using the value. The `?` operator makes passing an error along a
single character.

:::mission
Turn one field into a number or a clear error message, then parse a whole line with `?`, so each broken line says
exactly what is wrong.
:::
:::

:::step{type=concept title="Result: Ok or Err" file="15-errors/src/lib.rs" line="10-16"}
`Result` is an enum, like `Option`, with a value on both sides:

```rust
enum Result<T, E> {
    Ok(T),     // it worked: here is the value
    Err(E),    // it failed: here is why
}

pub fn number(field: &str, what: &str) -> Result<f64, String> {
    match field.trim().parse::<f64>() {
        Ok(value) => Ok(value),
        Err(_) => Err(format!("{what} is not a number: {field:?}")),
    }
}
```

`parse` itself returns a `Result`: `Ok(12.4)` or `Err(ParseFloatError)`. `number` translates that error into a message
a person can act on. A `String` is the simplest kind of error; chapter 16 makes better ones.
:::

:::step{type=task task=number title="Your turn: a number, or why not" file="15-errors/src/lib.rs" line="10-16"}
Finish `number(field, what)`: match `field.trim().parse::<f64>()`; `Ok(value)` gives `Ok(value)`, `Err(_)` gives
`Err(format!("{what} is not a number: {field:?}"))`.

Press **Check**.
:::

:::step{type=concept title="The ? operator" file="15-errors/src/lib.rs" line="17-27"}
In a function that returns `Result`, `?` after a `Result` means: if it is `Ok`, take the value out and go on; if it is
`Err`, **return that error from this function, now**.

```rust
let wind_ms = number(parts[2], "wind speed")?;   // windy?  the function returns Err("wind speed is not ...")
let power_kw = number(parts[3], "power")?;       // 22O0?   the function returns Err("power is not ...")
Ok(Reading { turbine: parts[0].to_string(), wind_ms, power_kw })
```

Without `?` each of those lines would be a five-line `match`. With it, the happy path reads straight down, and every
error still reaches the caller. `?` works for `Option` too, in functions that return `Option`.

`main` can return a `Result` as well (`fn main() -> Result<(), Box<dyn Error>>`), so `?` works there: a missing file
ends the program with the error printed, instead of a panic.

:::diagram{name="rs-question-mark"}
Each ? is an exit: an Err leaves the function at once, carrying its message; only Ok values continue.
:::
:::

:::step{type=history title="Exceptions, error codes, and values"}
:::before{title="Errors you can ignore"}
C functions return error codes that are easy to ignore. Java, C++ and Python throw **exceptions**, which jump out of
the function invisibly: reading the code, you cannot tell which line might throw.
:::

**Exceptions** spread from Lisp and CLU in the **1970s** to C++ (**1990**) and Java (**1995**), which tried "checked
exceptions" that a function must declare. Languages of the ML family returned errors as **values** instead, and
**Haskell**'s `Either` did it with a type. Go (**2009**) returns an `error` value next to the result (`val, err :=`),
plain but easy to forget. Rust's `Result` is a value the compiler will not let you ignore (an unused `Result` is a
warning), and `?` (**2016**, Rust 1.13) made handling it short.

:::solved
**Errors that are visible in the code.** Every function that can fail says so in its type, and every `?` marks a line
where it might return early.
:::

:::timeline
- **1970s** Exceptions in CLU and Lisp.
- **1995** Java's checked exceptions.
- **2009** Go's error values.
- **2016** Rust's ? operator.
:::
:::

:::step{type=task task=parse_reading title="Your turn: a line, or what is wrong with it" file="15-errors/src/lib.rs" line="17-27"}
Finish `parse_reading(line)`: `let wind_ms = number(parts[2], "wind speed")?;`, `let power_kw = number(parts[3],
"power")?;`, then return `Ok(Reading { turbine: parts[0].to_string(), wind_ms, power_kw })`.

```bash run
cd /workspace/15-errors && cargo run
```

Press **Check**.
:::

:::step{type=try title="Every broken line, explained"}
`main` reads the real file `data/t07.log` (six lines) and parses each one:

```text
$ cargo run -q
line 1: T07 2100 kW
line 2: expected 4 fields, found 3
line 3: wind speed is not a number: "windy"
line 4: T07 2210 kW
line 5: power is not a number: "22O0"
line 6: T07 2190 kW
3 good readings
t99: Err(Os { code: 2, kind: NotFound, message: "No such file or directory" })
```

The same six lines as chapter 11, but now each broken one says what is wrong, in words a technician can act on:
line 2 was cut short, line 3's anemometer sent text, line 5 has a letter O in the power. The good lines went straight
through `?`.

The last line asked for a file that does not exist. `read_to_string` did not crash: it returned an `Err` with the
operating system's reason (error 2, "No such file or directory"), and the program decided to print it.
:::

:::step{type=predict title="Guess first"}
:::question
In a function returning `Result<Reading, String>`, `number(parts[2], "wind speed")?` meets `"windy"`. What happens to the
next line, `number(parts[3], "power")?`?
:::
- [ ] It runs, and both errors are returned
- [x] It never runs: `?` returned the first error from the function
- [ ] It runs, and the error is ignored
:::explain
`?` returns at the first error. To collect all problems in a line, check each field without `?` and gather the errors.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When is a panic the right choice instead of a `Result`?
:::
- [x] For bugs: a state that should be impossible, where carrying on would be wrong
- [ ] For a missing file
- [ ] For bad user input
:::explain
Expected trouble is a `Result`; broken assumptions are a panic.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where can you use `?`?
:::
- [ ] Anywhere
- [x] In a function that returns `Result` (or `Option`, for `Option` values)
- [ ] Only in `main`
:::explain
`?` returns from the function, so the function's return type must be able to carry the error.
:::
:::

:::step{type=deep-dive title="Go deeper: Result in practice"}
**map_err.** `text.parse().map_err(|e| format!("bad number: {e}"))?` converts an error in place, without a `match`.

**unwrap and expect.** `.expect("the config file is checked at start-up")` panics with a message; use it where an error
really is a bug.

**Collecting.** `lines.map(parse_reading).collect::<Result<Vec<_>, _>>()` gives `Ok(all readings)` or the first error.
:::

:::step{type=recap}
You can now:

- tell bugs (panic) from expected trouble (`Result`);
- return `Ok` or `Err` with a message a person can act on;
- pass errors up with `?`, and let `main` return a `Result`;
- read a file without crashing when it is missing.

Next, chapter 16: error types of your own, with thiserror and anyhow.

:::photo{src="/lesson-images/rust/rs-15-notes.webp" alt="Handwritten notes about Result and the ? operator: Result: Ok(v) or Err(e); Panic = bug, Result = trouble; ? returns the error early; main can return Result; Say what is wrong, in words" ai="true"}
One page of notes for this chapter.
:::
:::
