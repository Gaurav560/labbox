:::step{type=story title="An anemometer and a power meter"}
Each turbine carries several sensors: an **anemometer** on top of the nacelle measures the wind, a **power meter** at
the base measures what the turbine makes. They are different devices with different data, but Windwatch wants to ask
every one of them the same questions: who are you, what do you read, in what unit?

Rust's answer is a **trait**: a named set of methods that many types can implement. `Sensor` says "a sensor has an id,
a value and a unit"; `Anemometer` and `PowerMeter` each say how. Code that only needs "some sensor" works with both,
and with every sensor added next year. Traits are also how the standard library gives your types abilities:
printing for people is the trait `Display`.

:::mission
Teach Reading to print itself for people with `Display`, then implement the `Sensor` trait for the power meter, so
one report can describe every kind of sensor.
:::
:::

:::step{type=concept title="Display: printing for people" file="18-traits/src/lib.rs" line="16-23"}
`{:?}` uses the `Debug` trait (derived, for programmers). `{}` uses `Display`, which you write yourself, because only
you know how a reading should read:

```rust
impl fmt::Display for Reading {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}: {:.1} m/s, {:.0} kW", self.turbine, self.wind_ms, self.power_kw)
    }
}
```

Without it, `println!("{r}")` does not compile, and the compiler suggests the other trait:

```text
error[E0277]: `Reading` doesn't implement `std::fmt::Display`
 --> 18-traits/src/bin/no_display.rs:7:15
  |
7 |     println!("{r}");
  |               ^^^ `Reading` cannot be formatted with the default formatter
...
  = note: in format strings you may be able to use `{:?}` (or `{:#?}` for pretty-print) instead
```

(Shortened with "...".) Implementing `Display` also gives you `.to_string()` for free.
:::

:::step{type=task task=impl_display title="Your turn: Reading for people" file="18-traits/src/lib.rs" line="16-23"}
Replace the TODO with the `impl fmt::Display for Reading` block shown in it.

Press **Check**.
:::

:::step{type=concept title="A trait of your own" file="18-traits/src/lib.rs" line="24-60"}
```rust
pub trait Sensor {
    fn id(&self) -> String;              // required: every sensor must say how
    fn value(&self) -> f64;
    fn unit(&self) -> &'static str;

    fn describe(&self) -> String {       // provided: a default every sensor gets
        format!("{} reads {:.1} {}", self.id(), self.value(), self.unit())
    }
}

impl Sensor for Anemometer { fn id(&self) -> String { ... } ... }
```

A type implements a trait in its own `impl Trait for Type` block. Two ways to use "any sensor":

| Write | Means | Cost |
|---|---|---|
| `fn show<S: Sensor>(s: &S)` | a generic: one copy per sensor type (chapter 17) | none at run time |
| `&dyn Sensor`, `Box<dyn Sensor>` | a **trait object**: any sensor, chosen at run time | one pointer look-up per call |

`report(&[Box<dyn Sensor>])` takes a list of **different** types together, which a generic cannot do: a `Vec` holds one
type, and `Box<dyn Sensor>` is that one type.

:::diagram{name="rs-trait-object"}
Each Box<dyn Sensor> holds the data and a pointer to its type's methods; describe() finds the right id() at run time.
:::
:::

:::step{type=history title="Interfaces and type classes"}
:::before{title="One family tree"}
In classic object-oriented languages, sharing behaviour meant inheriting from a common base class. A type could have
only one family, and everything inherited along the tree came with it.
:::

**Java** (**1995**) added **interfaces**: a list of methods any class may promise, apart from its family tree. In
**1988** Philip Wadler and Stephen Blott designed **type classes** for Haskell: abilities like "can be compared" or "can
be shown" that a type gets by an implementation, and that generic functions can require. Rust's traits come from type
classes: there is no inheritance between structs at all, and every shared ability (`Display`, `Clone`, `Iterator`,
`Sensor`) is a trait.

:::solved
**Abilities, not ancestry.** A type can have any number of traits, added where they make sense, even to types from
other crates.
:::

:::timeline
- **1988** Type classes, for Haskell.
- **1995** Java interfaces.
- **2015** Rust traits, and no inheritance.
:::
:::

:::step{type=task task=impl_sensor title="Your turn: a power meter is a sensor" file="18-traits/src/lib.rs" line="52-60"}
Replace the TODO with `impl Sensor for PowerMeter`: `id` returns `format!("{} power meter", self.turbine)`, `value`
returns `self.kw`, `unit` returns `"kW"`. Do not write `describe`: the default does it.

```bash run
cd /workspace/18-traits && cargo run --example sensors
```

(This chapter's program is an **example**, in `examples/sensors.rs`, run with `--example`.)

Press **Check**.
:::

:::step{type=try title="Three sensors, one report"}
```text
$ cargo run -q --example sensors
T07: 12.4 m/s, 2100 kW
Reading { turbine: "T07", wind_ms: 12.43, power_kw: 2100.0 }
T07 anemometer reads 12.4 m/s
T07 power meter reads 2100.0 kW
T12 anemometer reads 7.5 m/s
```

The first two lines are the same reading through two traits: `Display` for people (rounded, with units) and `Debug`
for programmers (every digit, every field name).

The report held two kinds of sensor in one `Vec<Box<dyn Sensor>>`, and called the same `describe` on each. Neither
`Anemometer` nor `PowerMeter` wrote `describe`: the trait's default built the sentence from their own `id`, `value` and
`unit`. Adding a thermometer next year is one new `impl Sensor`; `report` does not change.
:::

:::step{type=predict title="Guess first"}
:::question
`PowerMeter` implements `id` and `value` but forgets `unit`. What happens?
:::
- [ ] `unit` returns an empty string
- [x] It does not compile: every required method must be implemented
- [ ] Only `describe` fails at run time
:::explain
Required methods are a promise checked by the compiler; only methods with a default may be left out.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When do you need `Box<dyn Sensor>` rather than a generic `S: Sensor`?
:::
- [x] When one collection must hold different sensor types together
- [ ] Always
- [ ] When the sensor is large
:::explain
A generic picks one type per use; a trait object can be a different type for each item.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does implementing `Display` give you besides `{}`?
:::
- [ ] Nothing
- [x] `.to_string()`
- [ ] `Debug`
:::explain
The standard library implements `ToString` for every type that implements `Display`.
:::
:::

:::step{type=deep-dive title="Go deeper: traits in practice"}
**Derive.** `#[derive(Debug, Clone, PartialEq)]` writes trait implementations for you; `Display` is never derived, on
purpose.

**Operator traits.** `impl Add for Kw` makes `a + b` work for your own type: operators are traits too.

**The orphan rule.** You can implement your trait for any type, or any trait for your type, but not someone else's
trait for someone else's type, so two crates can never clash.
:::

:::step{type=recap}
You can now:

- implement `Display` so your types print for people;
- define a trait with required and default methods, and implement it for several types;
- choose between generics (`S: Sensor`) and trait objects (`Box<dyn Sensor>`);
- explain why Rust shares behaviour through traits instead of inheritance.

Next, chapter 19: lifetimes, for functions and structs that return or keep references.

:::photo{src="/lesson-images/rust/rs-18-notes.webp" alt="Handwritten notes about traits: trait = shared abilities; impl Trait for Type; Default methods for free; Display: braces for people; Box<dyn Trait> = mixed types" ai="true"}
One page of notes for this chapter.
:::
:::
