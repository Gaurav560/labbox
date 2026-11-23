:::step{type=story title="Four loose values, or one reading"}
So far Windwatch has passed a reading around as loose pieces: a turbine id here, a wind speed there, a power number in
a tuple whose fields are `.0`, `.1` and `.2`. That works until someone swaps two numbers and a wind speed of 2,100 m/s
goes through unnoticed.

A **struct** gives a group of values one name and names for each field: a `Reading` has a `turbine`, a `time`, a
`wind_ms` and a `power_kw`, and the compiler knows which is which. Functions that belong to a reading become its
**methods**: `reading.underperforming()` reads like a question you would ask an engineer.

That question is the reason Windwatch exists. A turbine at 7.5 m/s should make about 312 kW, according to its **power
curve**. If it makes 140, a blade may be iced, dirty or damaged, and someone should go and look.

:::mission
Build a Reading from a log line, then give it a method that says whether the turbine makes much less than its power
curve promises.
:::
:::

:::step{type=concept title="A struct, and a value of it" file="09-structs/src/lib.rs" line="6-13"}
```rust
#[derive(Debug, Clone, PartialEq)]
pub struct Reading {
    pub turbine: String,
    pub time: String,
    pub wind_ms: f64,
    pub power_kw: f64,
}

let r = Reading { turbine: "T07".to_string(), time: "10:10".to_string(), wind_ms: 12.4, power_kw: 2100.0 };
println!("{} makes {} kW", r.turbine, r.power_kw);
```

- Each field has a name and a type; `pub` lets code outside this file read it.
- A value is made by naming **every** field: Rust has no half-made structs.
- `#[derive(Debug, Clone, PartialEq)]` asks the compiler to write three abilities for you: print it with `{:?}`
  (`{:#?}` prints it across lines), `.clone()` it, and compare two with `==`.
- The struct owns its fields: its two `String`s are dropped when the reading is.
:::

:::step{type=concept title="impl: methods and associated functions" file="09-structs/src/lib.rs" line="15-41"}
Functions that belong to a type go in an `impl` block:

```rust
impl Reading {
    pub fn from_line(line: &str) -> Reading { ... }   // no self: called as Reading::from_line(...)
    pub fn expected_kw(&self) -> f64 { ... }           // &self: called as r.expected_kw()
}
```

A function with no `self` is an **associated function**, usually a constructor: `Reading::from_line(line)`, like
`String::from` and `Vec::new`. A function whose first parameter is `&self` is a **method**: it borrows the value it is
called on, and reads its fields as `self.wind_ms`. (`&mut self` borrows it to change it; plain `self` takes it.)
:::

:::step{type=task task=from_line title="Your turn: a Reading from a log line" file="09-structs/src/lib.rs" line="16-23"}
Finish `from_line`: after `parts` is made, return `Reading { turbine: parts[0].to_string(), time: parts[1].to_string(),
wind_ms: parts[2].trim().parse().unwrap(), power_kw: parts[3].trim().parse().unwrap() }`.

`.to_string()` turns a borrowed `&str` part into an owned `String`, because the Reading must own its text (the line may
be gone long before the reading is). `parse()` knows to make an `f64` because that is the field's type.

Press **Check**.
:::

:::step{type=history title="Records, and data with its own functions"}
:::before{title="Parallel lists"}
Early programs kept related values in separate lists, one for names, one for amounts, and matched them up by
position. Insert one value in the wrong place and every later record was wrong.
:::

**COBOL** (**1959**), designed by a committee that built on Grace Hopper's FLOW-MATIC, grouped fields into **records**,
the way a business form groups them. C's `struct` (**1972**) did the same for systems code. **Simula 67** attached
functions to records, which became the classes of object-oriented languages. Rust keeps the data (`struct`) and the
behaviour (`impl`) side by side, without class inheritance: shared behaviour comes from traits (chapter 18).

:::solved
**One value, named parts.** The compiler checks every field's name and type, and methods sit next to the data they
work on.
:::

:::timeline
- **1959** COBOL records.
- **1967** Simula 67: records with functions.
- **1972** C structs.
- **2015** Rust: struct plus impl, no inheritance.
:::

Grace Hopper, whose FLOW-MATIC language of the 1950s showed that programs could describe business data in plain words. COBOL's records, the ancestors of structs, grew from it.

:::photo{src="/lesson-images/rust/hopper.webp" alt="Grace Hopper in her US Navy uniform and cap, wearing glasses, in front of a United States flag" credit="James S. Davis, US Navy" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Commodore_Grace_M._Hopper,_USN_(covered).jpg"}
Commodore Grace M. Hopper, 1984.
:::
:::

:::step{type=concept title="The power curve" file="09-structs/src/lib.rs" line="25-35"}
`expected_kw` is already written. It is the turbine's **power curve**, simplified: nothing below 3 m/s or from 25 m/s,
full power (2,500 kW) from 12 m/s, and in between it grows with the **cube** of the wind:

| Wind | Expected power |
|---|---|
| 3 m/s | 0 kW |
| 7.5 m/s | 2,500 × (4.5 / 9)³ = 312.5 kW |
| 12 m/s and up | 2,500 kW |

The cube is real physics: the energy in moving air grows with the cube of its speed, so twice the wind carries eight
times the power. `.powi(3)` raises a number to the power 3.
:::

:::step{type=task task=underperforming title="Your turn: is this turbine underperforming?" file="09-structs/src/lib.rs" line="36-41"}
Finish `underperforming(&self)`: `let expected = self.expected_kw();` and return
`expected > 0.0 && self.power_kw < 0.8 * expected`.

```bash run
cd /workspace/09-structs && cargo run
```

Press **Check**.
:::

:::step{type=try title="Two turbines, the same wind, half the power"}
```text
$ cargo run -q
Reading {
    turbine: "T07",
    time: "2026-11-24 10:10",
    wind_ms: 12.4,
    power_kw: 2100.0,
}
T07 at 12.4 m/s:   2100 kW of   2500 expected
T12 at  7.5 m/s:    140 kW of    312 expected  <- check this turbine
T19 at  7.5 m/s:    305 kW of    312 expected
T31 at 25.6 m/s:      0 kW of      0 expected
```

`{:#?}` printed the whole Reading, field by field, thanks to `derive(Debug)`.

T12 and T19 feel the same wind, 7.5 m/s. T19 makes 305 kW, close to its curve. T12 makes **140**, less than half of
what it should: Windwatch flags it. T07 at 2,100 of 2,500 is fine (84%, above the 80% line). T31 makes nothing, but
nothing is expected in a storm, which is why the method checks `expected > 0.0` first.
:::

:::step{type=predict title="Guess first"}
:::question
`let r = Reading { turbine: "T07".into(), wind_ms: 12.4, power_kw: 2100.0 };` (no `time`). What happens?
:::
- [ ] `time` is an empty string
- [x] It does not compile: every field must be given
- [ ] `time` is null
:::explain
Rust has no half-built values and no null. Every field always has a real value.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is the difference between `Reading::from_line(...)` and `r.expected_kw()`?
:::
- [x] The first is an associated function (no self); the second is a method that borrows `r`
- [ ] None
- [ ] The first is private
:::explain
Constructors are usually associated functions; questions about a value are methods.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why do the struct's text fields use `String`, not `&str`?
:::
- [ ] `&str` is slower
- [x] The reading must own its text: the line it came from may be gone long before it
- [ ] Structs cannot hold references
:::explain
Structs can hold references, but then they need lifetimes (chapter 19). Owning is simpler.
:::
:::

:::step{type=deep-dive title="Go deeper: structs in practice"}
**Tuple structs.** `struct Kw(f64);` gives a plain number its own type, so a `Kw` can never be passed where an `Ms` (wind
speed) is expected: a cheap guard against swapped arguments.

**Shorthand.** `Reading { wind_ms, power_kw, .. }` uses variables named like the fields; `..other` copies the rest
from another value.

**Default.** `#[derive(Default)]` gives a value with every field zero or empty: `Reading::default()`.
:::

:::step{type=recap}
You can now:

- define a struct with named, typed fields, and make values of it;
- add associated functions and methods in an `impl` block, with `&self`;
- derive `Debug`, `Clone` and `PartialEq`;
- spot a turbine making far less than its power curve promises.

Next, chapter 10: enums, for values that can be one of several things, and Option, Rust's answer to null.

:::photo{src="/lesson-images/rust/rs-09-notes.webp" alt="Handwritten notes about structs and methods: struct = named fields; Every field, every time; impl Type with fn inside; &self = a method; Type::new() = no self" ai="true"}
One page of notes for this chapter.
:::
:::
