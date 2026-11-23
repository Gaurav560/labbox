:::step{type=story title="A number that refuses to change"}
Windwatch needs to remember things: how many turbines are online, how much each one can make, the wind speed the last
reading said. In most languages a variable is a box you can put a new value into whenever you like. In Rust, a
variable **cannot change** unless you say, when you create it, that it may.

That sounds like a nuisance until you have chased a bug where some far-away line of code changed a value you were
relying on. In Rust, when you read `let online = 40;`, you know `online` is 40 for the rest of that block, everywhere.
And when something does need to change, the word `mut` warns every reader.

:::mission
Use a constant to compute the farm's capacity, then turn the wind speed text an anemometer writes into a number,
reusing one name with shadowing.
:::
:::

:::step{type=concept title="let, mut and const" file="02-variables/src/main.rs" line="4-14"}
```rust
let online = 40;          // fixed: online is 40 from here on
let mut online = 40;      // may change: mut says so
online -= 3;              // three turbines stopped for maintenance
const RATED_POWER_KW: u32 = 2_500;   // a constant: fixed forever, known when compiling
```

| | `let` | `let mut` | `const` |
|---|---|---|---|
| can change? | no | yes | never |
| type written? | optional | optional | required |
| where? | inside functions | inside functions | anywhere, even outside functions |
| naming | `snake_case` | `snake_case` | `SCREAMING_SNAKE_CASE` |

Underscores in numbers are only for reading: `2_500` is 2500, `1_000_000` is a million.

Try to change a plain `let` and the compiler stops you, and tells you the fix:

```text
error[E0384]: cannot assign twice to immutable variable `online`
 --> 02-variables/src/bin/immutable.rs:3:5
  |
2 |     let online = 40;
  |         ------ first assignment to `online`
3 |     online -= 3;
  |     ^^^^^^^^^^^ cannot assign twice to immutable variable
  |
help: consider making this binding mutable
  |
2 |     let mut online = 40;
  |         +++
```
:::

:::step{type=task task=capacity_mw title="Your turn: the farm's capacity" file="02-variables/src/lib.rs" line="6-10"}
Finish `capacity_mw(turbines)`: return `turbines * RATED_POWER_KW / 1_000`.

The functions you finish in this course live in `src/lib.rs`, the crate's **library**; `src/main.rs` is a small
program that uses them, so you can see them work.

Press **Check**.
:::

:::step{type=history title="Immutable by default"}
:::before{title="Everything can change, anywhere"}
In C, Java and Python a variable can be changed by any line that can see it. In big programs that makes bugs where a
value changes "by itself" (really, somewhere far away) some of the hardest to find.
:::

Languages from the **functional programming** family made values unchangeable by default: **ML** (**1973**) and
**Haskell** (**1990**). Rust's first compiler was written in **OCaml**, an ML language, and Rust took the idea from
there, but kept `mut` for the places where changing a value in place is simply the fastest thing to do.

:::solved
**Changes you can see.** Every value that can change is marked `mut` where it is born, so readers, and the compiler,
know exactly what may move.
:::

:::timeline
- **1973** ML: values do not change.
- **1990** Haskell.
- **2010** Rust: immutable by default, `mut` when needed.
:::
:::

:::step{type=concept title="Shadowing: the same name, a new value" file="02-variables/src/lib.rs" line="12-19"}
A new `let` with a name already in use **shadows** the old one: from that line on, the name means the new value.
Unlike `mut`, the new value may even have a different **type**:

```rust
let speed = "  12.5 m/s";                     // text
let speed = speed.trim();                     // text, without the spaces
let speed = speed.trim_end_matches("m/s").trim();   // "12.5"
let speed: f64 = speed.parse().unwrap();      // now a number: 12.5
```

This is how Rust code tidies a value step by step without inventing names like `speed_text`, `speed_clean`,
`speed_number`. `parse()` turns text into a number of the type you ask for (`: f64`, a decimal number), and `unwrap()`
says "I am sure this worked; stop the program if it did not". Chapter 15 replaces that promise with proper error
handling.

:::diagram{name="rs-shadowing"}
One name, four values, each made from the one before; the old ones are simply no longer reachable.
:::
:::

:::step{type=task task=wind_speed title="Your turn: a wind speed from text" file="02-variables/src/lib.rs" line="12-19"}
Finish `wind_speed(text)`: after the first `let speed = text.trim();`, shadow `speed` with
`speed.trim_end_matches("m/s").trim()`, then with `let speed: f64 = speed.parse().unwrap();`, and return `speed`.

```bash run
cd /workspace/02-variables && cargo run --bin ch02-variables
```

Press **Check**.
:::

:::step{type=try title="A capacity that lost half a megawatt"}
```text
$ cargo run -q --bin ch02-variables
One turbine: 2500 kW
1 turbines: 2 MW
10 turbines: 25 MW
40 turbines: 100 MW
Online now: 37, 92 MW
"12.5 m/s" -> 12.5
"  3.2m/s " -> 3.2
"25 m/s" -> 25
```

The constant, the `mut` counter and the three shadows all did their jobs. `{text:?}` (with `:?`) prints the text in
quotes, so you can see the spaces.

Now read the second line. One turbine of 2,500 kW is **2.5** MW, and Windwatch says **2**. So is 37 turbines: 92.5 MW
became 92. Nothing crashed and nothing warned: `turbines * RATED_POWER_KW / 1_000` works on **whole numbers**, and
whole-number division throws the remainder away. For 40 turbines it happens to come out even. The next chapter is
about exactly this: Rust's number types, and choosing the right one.
:::

:::step{type=predict title="Guess first"}
:::question
`let total = 10; let total = total * 2;` Does this compile, and what is `total`?
:::
- [ ] It does not compile: `total` is not `mut`
- [x] It compiles, and `total` is 20: the second `let` makes a new variable that shadows the first
- [ ] It compiles, and `total` is 10
:::explain
Shadowing makes a new value; nothing is changed in place, so no `mut` is needed.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When should a variable be `mut`?
:::
- [ ] Always, to be safe
- [x] Only when its value really has to change after it is created
- [ ] Never
:::explain
Fewer `mut`s means fewer places a value can change, which is less to think about.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `unwrap()` do if `parse()` fails, for example on `"windy"`?
:::
- [ ] Returns 0
- [x] Stops the program with a message (a panic)
- [ ] Skips the line
:::explain
`unwrap` is a promise that nothing went wrong. Chapter 15 shows how to handle bad input without stopping.
:::
:::

:::step{type=deep-dive title="Go deeper: variables in practice"}
**Unused variables.** Rust warns about a variable you never use. Start its name with `_` (`_spare`) to say "on purpose".

**Blocks.** A variable lives until the end of the `{ }` block it was made in. Shadowing inside a block ends with the
block, and the outer value is visible again.

**Constants versus statics.** `const` values are copied into every place they are used; `static` makes one fixed place
in memory. Use `const` unless you know you need `static`.
:::

:::step{type=recap}
You can now:

- create variables with `let`, and make them changeable with `mut` only when needed;
- name a fixed value with `const`;
- shadow a name to tidy a value step by step, even into another type;
- spot whole-number division quietly losing a fraction.

Next, chapter 3: Rust's types, so 2.5 MW stays 2.5.

:::photo{src="/lesson-images/rust/rs-02-notes.webp" alt="Handwritten notes about variables: let = cannot change; let mut = may change; const NAME: u32 = 2_500;; Shadowing: same name, new value; Whole numbers: 2500 / 1000 = 2" ai="true"}
One page of notes for this chapter.
:::
:::
