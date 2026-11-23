:::step{type=story title="How fast is the tip of a blade?"}
A turbine's blades are 50 metres long. At 12 turns a minute the rotor looks slow and calm, but the tip of each blade
is travelling around a circle 314 metres long, twelve times a minute. Engineers watch that **tip speed**: too fast, and
the blade edges wear out and the turbine gets loud.

Windwatch needs many small calculations like this, and each one should have a name, take what it needs, and give back
one answer: a **function**. Rust functions hide one surprise that every beginner meets once: a semicolon at the end of
the last line changes what the function returns.

:::mission
Write a function for a blade's tip speed, then a capacity factor that calls another function.
:::
:::

:::step{type=concept title="A function, from top to bottom" file="04-functions/src/lib.rs" line="4-7"}
```rust
pub fn tip_speed(rotor_rpm: f64, blade_m: f64) -> f64 {
    2.0 * PI * blade_m * rotor_rpm / 60.0
}
```

| Part | Meaning |
|---|---|
| `pub` | public: other crates (and `main.rs`) may call it |
| `fn tip_speed` | a function named `tip_speed` |
| `(rotor_rpm: f64, blade_m: f64)` | two parameters; every parameter's type must be written |
| `-> f64` | it returns an `f64` |
| last line, **no semicolon** | the value the function returns |

`use std::f64::consts::PI;` at the top of the file brings the constant π in from Rust's **standard library**.
:::

:::step{type=task task=tip_speed title="Your turn: how fast a blade tip moves" file="04-functions/src/lib.rs" line="4-9"}
Finish `tip_speed`: return `2.0 * PI * blade_m * rotor_rpm / 60.0` as the last expression, with no semicolon.

Press **Check**.
:::

:::step{type=concept title="Expressions and statements" file="04-functions/src/lib.rs" line="4-9"}
Rust is an **expression** language: almost everything gives back a value, even a block:

```rust
let tip = {
    let circle = 2.0 * PI * 50.0;   // a statement: ends with ;
    circle * 12.0 / 60.0            // an expression: no ; so it is the block's value
};
```

A **statement** does something and gives back nothing; in Rust "nothing" is a real value called the **unit**, written
`()`. Put a semicolon after the last line of a function, and that line becomes a statement, so the function returns
`()` instead of your number. The compiler catches it, and points at the semicolon:

```text
error[E0308]: mismatched types
 --> 04-functions/src/bin/semicolon.rs:3:47
  |
3 | fn tip_speed(rotor_rpm: f64, blade_m: f64) -> f64 {
  |    ---------                                  ^^^ expected `f64`, found `()`
  |    |
  |    implicitly returns `()` as its body has no tail or `return` expression
4 |     2.0 * PI * blade_m * rotor_rpm / 60.0;
  |                                          - help: remove this semicolon to return this value
```

`return value;` also works, and is used to leave a function early. At the end of a function, Rust style is the
expression without `return`.

:::diagram{name="rs-expression"}
The last expression of a block is its value; a semicolon turns it into a statement whose value is ().
:::
:::

:::step{type=history title="Functions that give back values"}
:::before{title="Jumping around"}
Early programs jumped from line to line with `GOTO`. A calculation used in three places was written three times, or
reached by jumps that were hard to follow.
:::

**FORTRAN** (**1957**) let programmers write formulas almost as in maths, and **FORTRAN II** (**1958**) added
`FUNCTION` and `SUBROUTINE`: name a calculation once, call it anywhere, get a value back. **ALGOL 60** gave blocks and
local variables. Languages from the **ML** family (Rust's ancestors, chapter 2) went further: everything is an
expression, so a block or an `if` gives back a value too. Rust kept that, which is why its last line needs no `return`.

:::solved
**Small named calculations.** Each one is easy to test on its own, and a formula is written once.
:::

:::timeline
- **1957** FORTRAN: formulas.
- **1958** FORTRAN II: functions.
- **1960** ALGOL 60: blocks.
- **1973** ML: everything is an expression.
:::
:::

:::step{type=task task=capacity_factor title="Your turn: the capacity factor" file="04-functions/src/lib.rs" line="16-20"}
A turbine never makes its full rated power all the time: the wind varies. The **capacity factor** is the energy it made,
as a percentage of what it would have made at full power the whole time.

Finish `capacity_factor(energy_mwh, rated_kw, hours)`: divide `energy_mwh` by `max_energy_mwh(rated_kw, hours)` and
multiply by `100.0`.

```bash run
cd /workspace/04-functions && cargo run --bin ch04-functions
```

Press **Check**.
:::

:::step{type=try title="Tips at highway speed"}
```text
$ cargo run -q --bin ch04-functions
8 rpm with 50 m blades: tip at 41.9 m/s (151 km/h)
12 rpm with 50 m blades: tip at 62.8 m/s (226 km/h)
15.5 rpm with 50 m blades: tip at 81.2 m/s (292 km/h)
Most one turbine can make in 30 days: 1800 MWh
612 MWh in 30 days: capacity factor 34.0%
1080 MWh in 30 days: capacity factor 60.0%
1800 MWh in 30 days: capacity factor 100.0%
```

At a calm-looking 12 turns a minute the tip moves at **226 km/h**, faster than a car on an expressway; at 15.5 rpm, 292
km/h. That is why turbines limit their rotor speed in strong wind.

`capacity_factor` called `max_energy_mwh`, which did one job (2,500 kW for 720 hours is 1,800 MWh). 34% is a typical
month for a wind turbine; 100% never happens in real life, and a reading that says so is a reason to check the meter.
:::

:::step{type=predict title="Guess first"}
:::question
A function `fn double(x: u32) -> u32 { x * 2; }` is compiled. What happens?
:::
- [ ] It returns `x * 2`
- [x] It does not compile: with the semicolon the body returns `()`, not a `u32`
- [ ] It returns 0
:::explain
Remove the semicolon, and `x * 2` is the function's value.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why must every parameter's type be written, when `let` can often leave it out?
:::
- [x] A function's signature is a contract: callers and the compiler rely on it without reading the body
- [ ] Rust cannot infer types
- [ ] Only for public functions
:::explain
Inside a function the compiler infers; at its edges, you state the types.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does a block `{ let a = 2; a * 3 }` evaluate to?
:::
- [ ] Nothing
- [ ] 2
- [x] 6
:::explain
The last expression, without a semicolon, is the block's value.
:::
:::

:::step{type=deep-dive title="Go deeper: functions in practice"}
**No default or named arguments.** Rust functions take exactly the parameters they list. Chapter 9's structs and
builders are how Rust code passes many options.

**Several values back.** Return a tuple: `fn min_max(...) -> (f64, f64)`, then `let (low, high) = min_max(...);`.

**Documentation.** `///` comments above a function become its documentation; `cargo doc --open` turns them into a
website, as for every crate on crates.io.
:::

:::step{type=recap}
You can now:

- write functions with typed parameters and a return type;
- return the last expression, and recognise the semicolon mistake from its error;
- use blocks as expressions;
- call one function from another, each doing one job.

Next, chapter 5: if, loops, and a day of wind.

:::photo{src="/lesson-images/rust/rs-04-notes.webp" alt="Handwritten notes about functions: fn name(x: f64) -> f64; Last line, no ; = the value; With ; it returns (); Blocks have values too; One job per function" ai="true"}
One page of notes for this chapter.
:::
:::
