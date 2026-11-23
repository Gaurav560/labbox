:::step{type=story title="Calm, generating, stopped, or broken"}
A turbine is always in exactly one of a few states. It is **calm** (waiting for wind), **generating** (and then it
matters how many kW), **stopped** for a storm, or in **fault**, and then it matters which fault code it reported. A
number or a piece of text cannot say that safely: someone will write `"generatng"`, or forget the fault code.

Rust's **enum** lists the possible states, and each one can carry its own data. The compiler then insists that every
piece of code handling a status handles **every** state.

The same idea answers a much older question. What is the peak power of a log with no readings in it? Most languages
answer with **null**, a value that means "nothing" and crashes the program when someone forgets to check for it. Rust
has no null. It has an enum instead: `Option`.

:::mission
Classify a turbine into one of four statuses, carrying its power or its fault code, then return the peak of a log as
an Option that can say "there is none".
:::
:::

:::step{type=concept title="An enum whose variants carry data" file="10-enums/src/lib.rs" line="3-10"}
```rust
pub enum Status {
    Calm,                       // no data
    Generating { kw: f64 },     // named data, like a small struct
    StormStop,
    Fault(u16),                 // unnamed data: the fault code
}

let s = Status::Generating { kw: 2100.0 };
let f = Status::Fault(512);
```

A `Status` value is exactly one of the four, never two, never none. To look inside, you **match** on it:

```rust
match fault {
    Some(code) => Status::Fault(code),
    None => Status::Calm,
}
```

Each arm is a **pattern** and what to do when it fits. Chapter 11 goes deep into patterns; this is all you need now.
:::

:::step{type=task task=classify title="Your turn: classify a turbine" file="10-enums/src/lib.rs" line="12-17"}
Finish `classify(wind_ms, power_kw, fault)`: `match fault`. With `Some(code)`, return `Status::Fault(code)`. With
`None`: below 3.0 m/s `Status::Calm`, from 25.0 `Status::StormStop`, otherwise `Status::Generating { kw: power_kw }`.

Press **Check**.
:::

:::step{type=history title="The billion-dollar mistake"}
:::before{title="Null everywhere"}
In C, Java, C#, Python and JavaScript any reference can be null. Forget to check once, and the program crashes:
`NullPointerException`, `NoneType has no attribute`, `undefined is not a function`.
:::

In **1965** Tony Hoare added the null reference to **ALGOL W** "because it was so easy to implement". In a talk in
**2009** he called it "my **billion-dollar mistake**", counting the crashes, bugs and security holes it caused over forty
years. Languages of the ML family had already shown another way: a type that is either "some value" or "none", which
the compiler forces you to check (ML's `option`, Haskell's `Maybe`, **1990**). Rust's `Option<T>` is that type, and
Rust references can never be null.

:::solved
**"Maybe nothing" in the type.** A function that might have no answer says so (`Option<f64>`), and the caller cannot
use the value without deciding what to do about `None`.
:::

:::timeline
- **1965** Null in ALGOL W.
- **1990** Haskell's Maybe.
- **2009** "My billion-dollar mistake".
- **2015** Rust: Option, and no null at all.
:::

Tony Hoare, who added null references to ALGOL W in 1965, and in 2009 called them his billion-dollar mistake. He also invented Quicksort.

:::photo{src="/lesson-images/rust/hoare.webp" alt="Tony Hoare, an older man with white hair, a white beard and glasses, smiling, in a beige jacket" credit="Rama" license="CC BY-SA 2.0 FR" source="https://commons.wikimedia.org/wiki/File:Sir_Tony_Hoare_IMG_5125.jpg"}
Sir Tony Hoare at EPFL, Lausanne, 2011.
:::
:::

:::step{type=concept title="Option: Some(value) or None" file="10-enums/src/lib.rs" line="19-24"}
`Option` is an ordinary enum from the standard library:

```rust
enum Option<T> {
    Some(T),
    None,
}
```

`T` stands for any type (chapter 17 explains generics): `Option<f64>` is "an f64, or nothing". An `Option<f64>` is
**not** an `f64`: you cannot add one to a number until you have said what happens with `None`:

| Way | What it does with `None` |
|---|---|
| `match` | you write both arms |
| `.unwrap_or(0.0)` | uses 0.0 instead |
| `.unwrap()` | panics: only when you are certain it is `Some` |
| `if let Some(kw) = peak { ... }` | does something only for `Some` (chapter 11) |
| `?` | passes `None` up to the caller (chapter 15) |

:::diagram{name="rs-option"}
A function that might have no answer returns Option; the caller must open it before using the number.
:::
:::

:::step{type=task task=peak_power title="Your turn: the peak, if there is one" file="10-enums/src/lib.rs" line="19-24"}
Finish `peak_power(log)`: return `None` when `log.is_empty()`; otherwise `let mut peak = log[0];`, keep the largest in
`for &kw in log { if kw > peak { peak = kw; } }`, and return `Some(peak)`.

`for &kw in log` takes each `&f64` from the slice and copies the number out (the `&` in the pattern).

```bash run
cd /workspace/10-enums && cargo run
```

Press **Check**.
:::

:::step{type=try title="Four statuses and a day with no readings"}
```text
$ cargo run -q
T07: Generating { kw: 2100.0 }
T12: Calm
T19: Fault(512)
T31: StormStop
Monday peak: Some(2400.0)
Tuesday peak: None
Tuesday peak, or 0: 0
is Generating { kw: 1800.0 } a fault? false
```

Each turbine got exactly one status. T19's fault came first, even though its wind (14 m/s) was fine: a turbine in fault
is in fault, whatever the wind. The generating one carries its power; the faulty one, its code 512.

Tuesday's log was empty, and `peak_power` said so: `None`, not a made-up 0. Printing "0" was a decision made at the
call, with `unwrap_or(0.0)`, where it is visible. A dashboard might prefer to print "no data".
:::

:::step{type=predict title="Guess first"}
:::question
`let total = peak_power(&log) + 100.0;` Does it compile?
:::
- [ ] Yes
- [x] No: `Option<f64>` is not an `f64`; you must handle `None` first
- [ ] Only if the log is not empty
:::explain
`peak_power(&log).unwrap_or(0.0) + 100.0` compiles, and makes the choice visible.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
How is `Status::Fault(512)` different from a struct with a `kind: String` field?
:::
- [x] It can only ever be one of the listed variants, and the compiler checks every match handles all of them
- [ ] It uses less memory
- [ ] It cannot hold data
:::explain
A string could be any text, typos included. An enum is a closed list.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Can a Rust `&Reading` ever be null?
:::
- [ ] Yes, if the reading was dropped
- [x] No: references always point at a valid value; "maybe nothing" is `Option<&Reading>`
- [ ] Only in release builds
:::explain
That is how Rust removed the billion-dollar mistake.
:::
:::

:::step{type=deep-dive title="Go deeper: enums in practice"}
**Methods on enums.** `impl Status { fn is_running(&self) -> bool { ... } }` works exactly as for structs.

**Size.** An enum is as big as its biggest variant plus a small tag; `Option<&T>` is the size of a plain reference,
because Rust uses the impossible "null" address to mean `None`.

**Option methods.** `.map(|kw| kw / 1000.0)` converts the value inside, `.is_some()` and `.is_none()` ask, `.ok_or(..)`
turns it into a `Result` (chapter 15).
:::

:::step{type=recap}
You can now:

- define an enum whose variants carry different data;
- build values of each variant, and look inside with `match`;
- return `Option` when a function may have no answer, and handle `None` at the call;
- explain why Rust has no null.

Next, chapter 11: pattern matching in depth, and turning broken log lines into `None` instead of crashes.

:::photo{src="/lesson-images/rust/rs-10-notes.webp" alt="Handwritten notes about enums and Option: enum = one of a list; Variants can carry data; Option<T>: Some(x) or None; No null in Rust!; Open it: match / unwrap_or" ai="true"}
One page of notes for this chapter.
:::
:::
