:::step{type=story title="250 faults, plus 10, makes 4"}
At the end of chapter 2 Windwatch said one turbine was 2 MW, not 2.5, because it divided whole numbers. That was a
small lie. Here is a bigger one. A counter of faults that can hold numbers up to 255 is at 250, and ten more faults
arrive. In a debug build, Rust stops the program. In a release build, the counter quietly becomes **4**.

Every value in Rust has a **type** that says what it is and how much space it takes: a whole number of 8 bits, a
decimal number of 64 bits, a single character, true or false. The compiler knows every type before the program runs,
which is how it can refuse `40 * 2.5`, and why choosing the type is part of writing the program.

:::mission
Turn power and minutes into energy with the right number types, and build one reading's text from a tuple.
:::
:::

:::step{type=concept title="Numbers come in sizes" file="03-types/src/main.rs" line="12-13"}
| Type | Holds | Use it for |
|---|---|---|
| `u8` | 0 to 255 | small counts, bytes |
| `u16` | 0 to 65,535 | turbine numbers, port numbers |
| `u32` | 0 to about 4.3 billion | most counts: kW, minutes |
| `u64` | 0 to about 18 quintillion | very large counts, timestamps |
| `i32`, `i64` | negative and positive | temperatures, differences |
| `usize` | the machine's size | positions in a list |
| `f64` | decimal numbers, about 15 digits | wind speed, energy |
| `bool` | `true` or `false` | is it running? |
| `char` | one character, like `'K'` or `'₹'` | single letters |

`u` is unsigned (never negative), `i` is signed, the number is the bits. Without a type, a whole number is `i32` and a
decimal number is `f64`.

Rust never converts between number types on its own. To mix them, convert with `as`: `power_kw as f64` turns a
`u32` into an `f64`.
:::

:::step{type=task task=energy_kwh title="Your turn: energy from power and time" file="03-types/src/lib.rs" line="3-6"}
Finish `energy_kwh(power_kw, minutes)`: `power_kw as f64 * minutes as f64 / 60.0`.

Press **Check**.
:::

:::step{type=history title="Bits, bytes and an exploding rocket"}
:::before{title="Numbers that do not fit"}
Every number type has a largest value. Put a bigger number in, and most languages either wrap around silently or keep
going with a wrong value.
:::

On **4 June 1996** the first **Ariane 5** rocket veered off course 37 seconds after launch and was destroyed. Its
guidance software converted a 64-bit decimal number (the rocket's sideways speed, far larger than on Ariane 4) into a
16-bit whole number that could not hold it, and the conversion failed. In **2014** the video of "Gangnam Style" passed
2,147,483,647 views on YouTube, the largest number a 32-bit signed counter can hold, and YouTube moved its counters to
64 bits. Rust makes the problem loud: in debug builds an overflowing sum **stops the program**, and the standard
library offers `checked_add` (returns `None` if it does not fit), `saturating_add` (stops at the top) and
`wrapping_add` (wraps, on purpose).

:::solved
**Overflow you can see.** Tests in debug builds catch it, and the code can say what should happen when a number does
not fit.
:::

:::timeline
- **1996** Ariane 5: a number that did not fit.
- **2014** A view counter outgrows 32 bits.
- **2015** Rust 1.0: overflow stops debug builds.
:::

An Ariane 5 on its launch pad in French Guiana. The type flew more than a hundred times after its first flight ended 37 seconds after launch, because of one number that did not fit.

:::photo{src="/lesson-images/rust/ariane.webp" alt="A tall white rocket with two side boosters standing on a launch pad, seen through mist above green trees" credit="Bill Ingalls, NASA" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Ariane_5_on_Launch_Pad_with_James_Webb_Space_Telescope_(December_23,_2021).jpg"}
An Ariane 5 with the James Webb Space Telescope, December 2021.
:::
:::

:::step{type=concept title="Tuples and arrays" file="03-types/src/lib.rs" line="8-14"}
A **tuple** groups a few values of different types; an **array** holds a fixed number of values of one type:

```rust
let reading: (u8, f64, u32) = (7, 12.43, 2100);   // turbine, wind m/s, power kW
let (turbine, wind, power) = reading;              // take it apart into three names
let first = reading.0;                             // or reach in by position

let hours: [f64; 3] = [12.4, 13.0, 11.8];          // three f64 values
let second = hours[1];                             // 13.0
```

`format!` builds text the way `println!` prints it. Inside the braces, a format can follow a colon: `{turbine:02}`
pads to two digits (`07`), `{wind:.1}` rounds to one decimal.
:::

:::step{type=task task=describe title="Your turn: a reading as text" file="03-types/src/lib.rs" line="8-15"}
Finish `describe(reading)`: take the tuple apart with `let (turbine, wind, power) = reading;` and return
`format!("T{turbine:02}: {wind:.1} m/s, {power} kW")`.

```bash run
cd /workspace/03-types && cargo run --bin ch03-types
```

Press **Check**.
:::

:::step{type=try title="Three readings, and a counter that overflows"}
```text
$ cargo run -q --bin ch03-types
T07: 12.4 m/s, 2100 kW
T12: 3.0 m/s, 40 kW
T31: 25.0 m/s, 2500 kW
2100 kW for 10 minutes: 350.0 kWh
2500 kW for a day: 60000 kWh
u8 holds 0 to 255, so 250 + 10 does not fit: None
is 25 m/s a storm? true
the farm's code letter: K
```

The energy is a decimal number now: 350.0 kWh. Look at the second reading: the turbine sent **3.05** m/s, and `.1`
rounded it to **3.0**, not 3.1. 3.05 cannot be stored exactly in binary; the nearest `f64` is 3.04999..., which rounds
down. Decimal numbers are approximations, so never compare two `f64` values with `==` after arithmetic, and never use
them for money.

Here is the faults counter from the story, with 250 read from a file at run time, then 10 added:

```text
$ cargo run -q --bin overflow

thread 'main' (222) panicked at 03-types/src/bin/overflow.rs:3:17:
attempt to add with overflow
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
$ cargo run -q --release --bin overflow
faults: 4
```

A **debug** build (the normal `cargo run`) checks every sum and stops at the overflow, with the file and line. A
**release** build (`--release`, optimised, what you ship) skips the check for speed and wraps around: 250 + 10 = 260,
minus 256, is 4. Test in debug, and use `checked_add` where a number might not fit.

:::diagram{name="rs-overflow"}
A u8 has eight bits: 250 + 10 needs a ninth, so a debug build stops and a release build keeps the low eight bits.
:::
:::

:::step{type=predict title="Guess first"}
:::question
`let total: u32 = 7 / 2;` What is `total`?
:::
- [ ] 3.5
- [x] 3: whole-number division drops the remainder
- [ ] It does not compile
:::explain
`7.0 / 2.0` is 3.5. `7 % 2` gives the remainder, 1.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which type fits a wind speed of 12.43 m/s?
:::
- [ ] `u32`
- [x] `f64`
- [ ] `char`
:::explain
Whole-number types cannot hold fractions; `f64` holds about 15 significant digits.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did 3.05 become 3.0 with `{:.1}`?
:::
- [ ] Rust rounds down always
- [x] 3.05 is stored as the nearest binary value, 3.0499999..., which rounds to 3.0
- [ ] `.1` cuts off digits
:::explain
Most decimal fractions have no exact binary form. That is true in every language that uses `f64`.
:::
:::

:::step{type=deep-dive title="Go deeper: types in practice"}
**Type inference.** Rust works out most types itself (`let x = 2.5;` is `f64`); you write types where they matter,
like function signatures.

**Money.** Store money in the smallest unit as a whole number (paise in a `u64`), or use a decimal crate, never `f64`.

**Characters.** A `char` is four bytes and holds any Unicode character, `'₹'` included. Text (`String`) is chapter 8.
:::

:::step{type=recap}
You can now:

- choose an integer or float type, and convert between them with `as`;
- group values with tuples and arrays, and take a tuple apart;
- format numbers with padding and rounding;
- explain overflow in debug and release builds, and why decimal numbers are approximate.

Next, chapter 4: functions, and the semicolon that changes what a function returns.

:::photo{src="/lesson-images/rust/rs-03-notes.webp" alt="Handwritten notes about types: u8 u32 u64 / i32 / f64; Mix types? Convert with as; Tuple (a, b, c), array [x; n]; Debug: overflow stops; 3.05 is not exact in f64" ai="true"}
One page of notes for this chapter.
:::
:::
