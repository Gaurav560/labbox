:::step{type=story title="Rules the control room can change"}
The control room keeps changing its alarm rules. Today "low power" means under 200 kW; for the older turbines it should
be 150. Tomorrow someone adds "idle in good wind". If every rule is a hand-written function, every change is a new
release of Windwatch.

What the control room needs is rules as **values**: built from settings, kept in a list, passed to the code that checks
the readings. In Rust a function you can keep in a variable is a **closure**, written in place as `|r| r.power_kw < 200.0`.
You have used a few already (`sort_by(|a, b| ...)`, `with_context(|| ...)`); this chapter shows what they are, and the
one keyword, `move`, that makes a closure safe to keep.

:::mission
Write a function that returns a rule (a closure that remembers its limit), then run a list of named rules over the
readings and collect the alerts.
:::
:::

:::step{type=concept title="A closure, and what it captures" file="20-closures/src/lib.rs" line="17-22"}
```rust
let limit_kw = 200.0;
let low = |r: &Reading| r.power_kw < limit_kw;   // a closure: parameters between | |, then the body
low(&reading)                                      // called like a function
```

Unlike a function, a closure can use variables from where it was written (`limit_kw`): it **captures** them. By
default it borrows them. A closure returned from a function would then borrow a variable that is gone, and the compiler
says so, with the fix:

```text
error[E0373]: closure may outlive the current function, but it borrows `limit_kw`, which is owned by the current function
 --> 20-closures/src/bin/no_move.rs:2:14
  |
2 |     Box::new(|kw: f64| kw < limit_kw)
  |              ^^^^^^^^^      -------- `limit_kw` is borrowed here
  |              |
  |              may outlive borrowed value `limit_kw`
...
help: to force the closure to take ownership of `limit_kw` (and any other referenced variables), use the `move` keyword
  |
2 |     Box::new(move |kw: f64| kw < limit_kw)
  |              ++++
```

(Shortened with "...".) `move` makes the closure own its own copy of what it uses, so it can live anywhere.
`-> impl Fn(&Reading) -> bool` says "this function returns some closure that takes a reading and gives a bool".
:::

:::step{type=task task=below title="Your turn: a rule that remembers its limit" file="20-closures/src/lib.rs" line="17-22"}
Finish `below(limit_kw)`: return `move |r: &Reading| r.wind_ms >= 6.0 && r.power_kw < limit_kw`.

Press **Check**.
:::

:::step{type=concept title="Fn, FnMut, FnOnce, and boxes" file="20-closures/src/lib.rs" line="24-30"}
Every closure implements one or more of three traits, depending on what it does with its captures:

| Trait | The closure... | Can be called |
|---|---|---|
| `Fn` | only reads what it captured | any number of times, even at once |
| `FnMut` | changes what it captured (a counter) | many times, one at a time |
| `FnOnce` | gives away what it captured | once |

Each closure has its own unnamed type, so a list of different closures needs a common type: `Box<dyn Fn(&Reading) ->
bool>`, a trait object as in chapter 18. That is how `alerts` takes `&[(&str, Box<dyn Fn(&Reading) -> bool>)]`:
a list of named rules, each any closure at all.

:::diagram{name="rs-closure"}
Each rule is a closure in a box; alerts calls every rule on every reading and collects the names that match.
:::
:::

:::step{type=history title="From lambda calculus to sort_by"}
:::before{title="Functions only at the top"}
In early languages a function was written once, by name, at the top of a program. You could not make a new one while
the program ran, or hand one to another function.
:::

In **1936** Alonzo Church's **lambda calculus** described computation with nothing but functions, written in place.
**Lisp** (**1958**) brought those "lambdas" into a language, and **Scheme** (**1975**, Sussman and Steele) made them
**closures** that capture their surroundings correctly. They reached the mainstream in JavaScript (**1995**), C#, and
Java 8's lambdas (**2014**). Rust's closures compile like ordinary functions: when the type is known (as in `impl Fn`
or a generic), calling one costs the same as calling a function, and is usually inlined away entirely.

:::solved
**Behaviour as a value.** Rules, sort orders and callbacks are passed around like numbers, at no run-time cost.
:::

:::timeline
- **1936** Lambda calculus.
- **1975** Scheme's closures.
- **2014** Lambdas in Java 8.
- **2015** Rust closures: Fn, FnMut, FnOnce.
:::

Guy Steele, who with Gerald Sussman created Scheme, the language that made closures work correctly.

:::photo{src="/lesson-images/rust/steele.webp" alt="Guy Steele, a smiling man with grey hair in a striped shirt with pens in the pocket" credit="George Ruban" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AGuy_Steele.jpg"}
Guy Steele speaking at Google Boston.
:::
:::

:::step{type=task task=alerts title="Your turn: run the rules" file="20-closures/src/lib.rs" line="24-30"}
Finish `alerts(readings, rules)`: for each `r` in `readings`, for each `(name, rule)` in `rules`, when `rule(r)` is true,
push `format!("{}: {}", r.turbine, name)`. Return the lines.

```bash run
cd /workspace/20-closures && cargo run --bin ch20-closures
```

Press **Check**.
:::

:::step{type=try title="Four alerts, and one that is wrong"}
```text
$ cargo run -q --bin ch20-closures
T12: low power
T19: low power
T19: storm stop
T19: idle in good wind
by power: ["T07", "T12", "T19", "T31"]
2 running, 4 checks
```

Three rules: one made by `below(200.0)`, one capturing `storm_limit` with `move`, one capturing nothing. T12, making
140 kW in 7.5 m/s, is a real "low power" alert.

Now read T19's three alerts. T19 is at 26 m/s: it **stopped for the storm**, exactly as it should. "Low power" and
"idle in good wind" are both false alarms: each rule checked its own condition and knew nothing about storms. Rules that
are values are easy to add, and just as easy to get wrong together. The fix is in the rules (`wind_ms < 25.0` in both),
and a test with a storm reading (chapter 22) would have caught it.

The last line used an `FnMut` closure that counts every check it is asked to make: 4 checks, 2 turbines running.
:::

:::step{type=predict title="Guess first"}
:::question
`let rule = below(200.0);` and then the function's `limit_kw` is long gone. Does `rule(&r)` still work?
:::
- [ ] No, the limit was dropped
- [x] Yes: with `move`, the closure owns its own copy of `limit_kw`
- [ ] Only once
:::explain
Without `move` the compiler would refuse to build it (E0373), so it can never fail at run time.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does a list of rules need `Box<dyn Fn(...)>`?
:::
- [x] Every closure has its own type; the box gives them one common type
- [ ] Closures cannot be in a Vec otherwise
- [ ] For speed
:::explain
One closure type in a `Vec` needs no box; different ones do.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A closure adds to a counter it captured. Which trait does it implement?
:::
- [ ] Fn
- [x] FnMut
- [ ] FnOnce only
:::explain
Changing a capture needs `FnMut`; reading only is `Fn`.
:::
:::

:::step{type=deep-dive title="Go deeper: closures in practice"}
**Taking closures.** `fn apply(f: impl Fn(f64) -> f64)` is the simple way; a generic `F: Fn(f64) -> f64` is the same;
`&dyn Fn(f64) -> f64` avoids a copy of the function per closure type.

**Closures in the standard library.** `sort_by_key`, `retain`, `map`, `filter`, `unwrap_or_else` all take closures;
chapter 21 chains them.

**Capturing less.** In Rust 2021 and later, a closure captures only the fields it uses (`r.power_kw`), not the whole
variable.
:::

:::step{type=recap}
You can now:

- write closures, and know what they capture;
- return a closure with `move` and `impl Fn`, and read E0373;
- tell `Fn`, `FnMut` and `FnOnce` apart;
- keep different closures together with `Box<dyn Fn>`, and see how rules interact.

Next, chapter 21: iterators, and whether they cost anything.

:::photo{src="/lesson-images/rust/rs-20-notes.webp" alt="Handwritten notes about closures: |x| x + 1 is a closure; It can capture variables; move = own the captures; Fn, FnMut, FnOnce; Rules can clash: test them" ai="true"}
One page of notes for this chapter.
:::
:::
