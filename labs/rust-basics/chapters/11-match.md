:::step{type=story title="Line 5 says 22O0"}
Real logs are messy. A radio link drops the last field of a line. A sensor writes `windy` where a number should be. A
technician types a capital letter **O** where a zero should be: `22O0` kW. Chapter 9's `from_line` calls `.unwrap()`,
which stops the whole program at the first bad line. A monitor that stops on line 5 of a million is no monitor.

Rust's tool for "it could be this, or this, or this" is **pattern matching**. `match` checks a value against patterns
one by one, and the compiler makes sure no case is forgotten. Patterns can take values apart, test ranges, and add
extra conditions. And `let else` says, in one line: "this must fit the pattern; if it does not, leave now".

:::mission
Describe every turbine status in words, with a guard and a range of urgent fault codes, then parse a log line into
`Some(reading)` or `None`, so broken lines are skipped instead of crashing Windwatch.
:::
:::

:::step{type=concept title="Patterns, guards and ranges" file="11-match/src/lib.rs" line="21-33"}
```rust
match status {
    Status::Calm => "waiting for wind".to_string(),
    Status::Generating { kw } if *kw >= 2_500.0 => "full power".to_string(),   // a guard: an extra condition
    Status::Generating { kw } => format!("generating {kw:.0} kW"),              // kw is taken out of the variant
    Status::StormStop => "stopped for the storm".to_string(),
    Status::Fault(code @ 500..=599) => format!("fault {code}: send the crew now"),   // a range, bound to code
    Status::Fault(code) => format!("fault {code}: check at the next visit"),
}
```

| Pattern | Matches |
|---|---|
| `Status::Calm` | exactly that variant |
| `Status::Generating { kw }` | that variant, and names its field `kw` |
| `... if *kw >= 2_500.0` | only when the guard is also true |
| `Status::Fault(500..=599)` | a fault whose code is 500 to 599 |
| `code @ 500..=599` | the same, and names the code |
| `_` | anything (a wildcard) |

Arms are tried **in order**: the guarded `Generating` must come before the plain one, or it would never be reached.
And every possible value must be covered, or the program does not compile:

```text
error[E0004]: non-exhaustive patterns: `Status::Fault(_)` not covered
  --> 11-match/src/bin/missing_arm.rs:4:11
   |
 4 |     match status {
   |           ^^^^^^ pattern `Status::Fault(_)` not covered
...
help: ensure that all possible cases are being handled by adding a match arm with a wildcard pattern or an explicit pattern as shown
   |
 7 ~         Status::StormStop => "storm",
 8 ~         Status::Fault(_) => todo!(),
```

(Shortened with "...".) Add a variant to `Status` next year, and every `match` in the program that forgot it stops
compiling, with the exact line. That is a large part of why Rust code stays correct as it grows.
:::

:::step{type=task task=describe_status title="Your turn: a status in words" file="11-match/src/lib.rs" line="21-33"}
Replace `_ => todo!()` in `describe` with the four arms from the TODO, in that order: full power (with the guard),
generating, urgent fault (`code @ 500..=599`), other fault.

Press **Check**.
:::

:::step{type=history title="Patterns from proofs to production"}
:::before{title="Chains of ifs"}
Taking a value apart and testing it was a chain of `if`s and type checks; forgetting a case was silent.
:::

Pattern matching grew up in languages for proving things: **ML** (**1973**, for Robin Milner's theorem prover LCF) and
**Hope** (**1980**), where taking data apart by its shape was natural. ML's compilers learned to warn when a match
missed a case, and Haskell, OCaml and Scala followed. Mainstream languages are catching up: Python 3.10 added `match`
in **2021**, Java 21 pattern matching for `switch` in **2023**. In Rust, a missing case is not a warning but an error.

:::solved
**Every case handled, checked by the compiler**, with values taken apart in the same step.
:::

:::timeline
- **1973** ML: patterns, for a theorem prover.
- **2015** Rust: exhaustive match.
- **2021** Python's match; **2023** Java's.
:::
:::

:::step{type=concept title="if let and let else" file="11-match/src/lib.rs" line="35-45"}
When you care about **one** pattern, a full `match` is long. Two shorter forms:

```rust
if let Some(r) = parse_line(line) {        // run this block only when it fits
    println!("{} m/s", r.wind_ms);
}

let Ok(wind_ms) = wind.trim().parse::<f64>() else {   // it must fit; otherwise leave now
    return None;
};
// from here on, wind_ms is a plain f64
```

`parse` returns a `Result`: `Ok(number)` or `Err(why)`, chapter 15's type. `let else` keeps the happy path flat:
each check is one line, and the `else` block must leave (with `return`, `break` or `continue`).

`let [turbine, time, wind, power] = parts[..] else { return None; };` is a **slice pattern**: it fits only a list of
exactly four parts, and names them in one go.

:::diagram{name="rs-let-else"}
Each let else is a gate: a line that does not fit any gate leaves with None, and only good lines reach Some(Reading).
:::
:::

:::step{type=task task=parse_line title="Your turn: broken lines become None" file="11-match/src/lib.rs" line="35-45"}
Finish `parse_line`: `let Ok(wind_ms) = wind.trim().parse::<f64>() else { return None; };`, the same for `power_kw`,
then `Some(Reading { turbine: turbine.to_string(), time: time.to_string(), wind_ms, power_kw })`.

```bash run
cd /workspace/11-match && cargo run --bin ch11-match
```

Press **Check**.
:::

:::step{type=try title="Six lines, three broken"}
```text
$ cargo run -q --bin ch11-match
Calm -> waiting for wind
Generating { kw: 2500.0 } -> full power
Generating { kw: 1312.4 } -> generating 1312 kW
StormStop -> stopped for the storm
Fault(512) -> fault 512: send the crew now
Fault(204) -> fault 204: check at the next visit
line 1: 2100 kW at 2026-11-24 10:10
line 2: skipped: "T07,2026-11-24 10:20,12.9"
line 3: skipped: "T07,2026-11-24 10:30,windy,2180"
line 4: 2210 kW at 2026-11-24 10:40
line 5: skipped: "T07,2026-11-24 10:50,13.4,22O0"
line 6: 2190 kW at 2026-11-24 11:00
3 of 6 lines kept
T12 is at 3.1 m/s
```

The guard sent exactly 2,500 kW to "full power"; the range sent 512 to the crew today and 204 to the next visit.

The log: line 2 has three fields (the slice pattern did not fit), line 3 has `windy` (the first `let else`), line 5
has `22O0` with a letter O (the second). Each became `None`, and Windwatch went on to the next line. Look closely at
line 5 in the output: `22O0` and `2200` are hard to tell apart for a person, and trivial for the parser.

Skipping is right for a monitor, and it is also how data quietly goes missing. Half of this log was skipped: a real
Windwatch would count skipped lines per turbine and raise an alarm when the count grows (chapter 12's summary does).
:::

:::step{type=predict title="Guess first"}
:::question
In `describe`, the plain `Status::Generating { kw }` arm is moved above the guarded one. What happens at 2,500 kW?
:::
- [ ] "full power"
- [x] "generating 2500 kW": arms are tried in order, and the first one that fits wins
- [ ] It does not compile
:::explain
The compiler warns that the guarded arm can never be reached; it is still valid code.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What must the `else` block of a `let else` do?
:::
- [ ] Return a default value
- [x] Leave: `return`, `break`, `continue` or panic
- [ ] Nothing
:::explain
After the `let else`, the names are guaranteed to exist, so the else path cannot carry on.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is a non-exhaustive `match` an error, not a warning?
:::
- [x] A forgotten case is a bug waiting for that value; refusing to compile finds it now
- [ ] For speed
- [ ] Rust has no warnings
:::explain
Adding a new variant then shows you every place in the program that must decide what to do with it.
:::
:::

:::step{type=deep-dive title="Go deeper: patterns in practice"}
**`matches!`.** `matches!(status, Status::Fault(500..=599))` is `true` or `false`, handy in conditions.

**Destructuring anywhere.** `let Reading { turbine, wind_ms, .. } = r;` and `fn show(&(id, kw): &(u8, f64))` take values
apart in `let`s and parameters too.

**`while let`.** `while let Some(x) = stack.pop() { ... }` loops while the pattern fits.
:::

:::step{type=recap}
You can now:

- match on enums with patterns, guards, ranges and `@` bindings;
- rely on the compiler to catch a forgotten case;
- use `if let` for one pattern and `let else` for "it must fit, or leave";
- turn broken input into `None` instead of a panic.

Next, chapter 12: modules, so Windwatch's code is split into files with clear borders.

:::photo{src="/lesson-images/rust/rs-11-notes.webp" alt="Handwritten notes about pattern matching: match must cover every case; Arms run in order; Guards: if ... after a pattern; if let = one pattern; let else = fit, or leave" ai="true"}
One page of notes for this chapter.
:::
:::
