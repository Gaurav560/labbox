:::step{type=story title="The storm reading nobody tested"}
In chapter 20 a rule called a turbine "low power" while it was stopped for a storm, and nobody noticed until the
output was read by eye. A one-character change, `>=` to `>` in the power curve, would make Windwatch expect full
power at exactly 25 m/s, the wind speed where a real turbine has just shut itself down. Nothing would crash. The
numbers would simply be wrong, every stormy night.

**Tests** are small programs that run your code on known inputs and check the answers, every time anything changes.
Rust builds them in: `cargo test` finds every function marked `#[test]`, runs them all in parallel, and reports which
failed and why. In this chapter you write the tests, and the checks judge them by doing what the story describes:
they plant exactly that kind of bug and see whether your tests notice.

:::mission
Write a test for the power curve's edges, and a test for the parser's broken lines, both strong enough to fail when a
bug is planted.
:::
:::

:::step{type=concept title="Tests in Rust" file="22-testing/src/lib.rs" line="25-33"}
Two places for tests:

| Where | Looks like | Tests |
|---|---|---|
| inside `src/lib.rs` | `#[cfg(test)] mod tests { use super::*; #[test] fn ...() }` | private functions too: **unit tests** |
| in `tests/*.rs` | each file a separate crate, using the library like any user | the public API: **integration tests** |

```rust
#[test]
fn full_power_from_12_ms() {
    assert_eq!(power_curve(12.0), 2_500.0);
}
```

| Macro | Checks |
|---|---|
| `assert!(cond)` | the condition is true |
| `assert_eq!(left, right)` | they are equal, and prints both if not |
| `assert_ne!(a, b)` | they differ |

A failing assert **panics**, and the test runner reports that test as failed. `#[cfg(test)]` means "compile this only
for `cargo test`", so tests add nothing to the real program.
:::

:::step{type=task task=test_curve title="Your turn: the edges of the power curve" file="22-testing/tests/windwatch.rs" line="4-8"}
In `tests/windwatch.rs`, fill `power_curve_edges`: `assert_eq!(power_curve(2.99), 0.0);`, the same for 3.0 (0.0), 24.9
(2_500.0) and 25.0 (0.0), and `assert!((power_curve(7.5) - 312.5).abs() < 0.01);`.

```bash run
cd /workspace/22-testing && cargo test
```

Press **Check**: your test runs on the correct code (it must pass), then on code where the storm stop starts above
25 m/s (it must fail).
:::

:::step{type=history title="Testing built into the language"}
:::before{title="Testing as an extra"}
For a long time testing meant a separate framework to install, configure and learn, so many projects had none.
:::

Kent Beck's **SUnit** (**1994**) and **JUnit** (**1997**) made automated tests ordinary in Smalltalk and Java. Python
put `unittest` in its standard library (**2001**) and Go shipped `go test` with the language (**2012**). Rust went
further: `#[test]` is part of the language, `cargo test` comes with every installation, and examples in documentation
comments (`///`) are compiled and run as **doc tests**, so documentation cannot quietly go out of date. In **1971**
Richard Lipton proposed **mutation testing**: change the program slightly, and a good test suite must notice. This
chapter's checks do exactly that to your tests.

:::solved
**Tests from the first day.** No setup, no framework choice: every Rust crate can be tested with one command.
:::

:::timeline
- **1971** Mutation testing proposed.
- **1997** JUnit.
- **2015** Rust: #[test] and cargo test built in.
:::

Kent Beck, who wrote SUnit and, with Erich Gamma, JUnit, and made tests that run in a second an everyday habit.

:::photo{src="/lesson-images/rust/kent-beck.webp" alt="Kent Beck speaking at a conference in 2005, gesturing with one hand" credit="Barry Mulling" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File%3AKent_Beck_tells_it_like_it_is%2C_2005.jpg"}
Kent Beck in 2005.
:::
:::

:::step{type=concept title="Testing errors" file="22-testing/tests/windwatch.rs" line="10-14"}
`parse` returns a `Result`, so tests compare it with `Ok(...)` or `Err(...)` values directly:

```rust
assert_eq!(parse("T07,10:10,12.4,2100"), Ok(("T07".to_string(), 12.4, 2100.0)));
assert!(parse("T07,10:20,12.9").is_err());
assert_eq!(parse("T07,10:50,13.4,22O0"), Err("bad power \"22O0\"".to_string()));
```

The last assert checks the **message**, not just that it failed: a parser that blames the wrong field would still
return an error, and only this assert notices.

:::diagram{name="rs-test-mutation"}
Your test runs twice: on the correct code it must pass, and with one planted mistake it must fail.
:::
:::

:::step{type=task task=test_parse title="Your turn: broken lines, tested" file="22-testing/tests/windwatch.rs" line="10-14"}
Fill `parse_rejects_broken_lines` with the three asserts above.

```bash run
cd /workspace/22-testing && cargo test
```

Press **Check**: this time the planted bug makes the power error name the wind field.
:::

:::step{type=try title="Three green tests, then one red"}
With both tests written:

```text
$ cargo test -q 2>&1 | tail -12
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


running 2 tests
..
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Three groups ran: the unit test inside `lib.rs` (1 passed), your integration tests (2 passed), and the doc tests (none
yet). Now the one-character bug from the story, `wind_ms >= 25.0` changed to `wind_ms > 25.0`:

```text
running 2 tests
. 1/2
power_curve_edges --- FAILED

failures:

---- power_curve_edges stdout ----

thread 'power_curve_edges' (961) panicked at 22-testing/tests/windwatch.rs:10:5:
assertion `left == right` failed
  left: 2500.0
 right: 0.0
...
test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

(Shortened with "...".) The edge test caught it at once, naming the line and both values: at exactly 25 m/s the code
said 2,500 kW where it should say 0. The unit test inside `lib.rs` (12 m/s) and the parser test still passed: they test
other things. That is why edges get their own asserts.
:::

:::step{type=predict title="Guess first"}
:::question
Your curve test only checks 7.5 m/s and 12 m/s. The bug moves the storm stop from 25 to above 25. Does your test fail?
:::
- [ ] Yes
- [x] No: neither 7.5 nor 12 is near the edge the bug moved
- [ ] It does not compile
:::explain
Bugs live at edges: 3.0, 12.0, 25.0. Test them, and one value just either side.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is the difference between a test in `src/lib.rs` and one in `tests/`?
:::
- [x] Unit tests inside the crate can test private functions; files in `tests/` use only the public API
- [ ] None
- [ ] Only `tests/` runs with `cargo test`
:::explain
Both run with `cargo test`; integration tests see the crate exactly as a user would.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does assert_eq! print `left` and `right`?
:::
- [ ] For decoration
- [x] So a failing test shows both values, and you see the mistake without a debugger
- [ ] Because tests run in parallel
:::explain
A failure message is the first thing you read; make it informative.
:::
:::

:::step{type=deep-dive title="Go deeper: testing in practice"}
**Doc tests.** A code block in a `///` comment is compiled and run by `cargo test`: examples that are always true.

**Expected panics.** `#[should_panic(expected = "overflow")]` tests that something panics with a message.

**Property tests.** The `proptest` crate generates hundreds of inputs ("any wind between 12 and 25 gives 2,500") and
shrinks a failure to the smallest example.
:::

:::step{type=recap}
You can now:

- write unit tests in `#[cfg(test)]` modules and integration tests in `tests/`;
- use `assert!`, `assert_eq!` and `assert_ne!`, and read a failure;
- test edges and error messages, not just happy paths;
- judge a test by whether it catches a planted bug.

That ends Part 5. Next, chapter 23: a real command-line tool.

:::photo{src="/lesson-images/rust/rs-22-notes.webp" alt="Handwritten notes about writing tests: #[test] + cargo test; assert_eq!(left, right); Unit tests and tests/ files; Test the edges: 3, 12, 25; Plant a bug: does it fail?" ai="true"}
One page of notes for this chapter.
:::
:::
