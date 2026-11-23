:::step{type=story title="The same function, three times"}
Windwatch needs the highest power reading of a day (an `f64`), the most serious fault code of a week (a `u16`), and the
latest hour letter in a shift plan (a `char`). Written plainly, that is three functions with the same body and
different types: three copies to test and three places to fix the next bug.

**Generics** write it once. `largest<T>` works for any type `T`, and the **bounds** say what `T` must be able to do:
here, compare (`PartialOrd`) and copy (`Copy`). The compiler checks the body against the bounds once, then makes a
separate, fully optimised copy for each type you actually use. You pay nothing at run time for writing it once.

:::mission
Write one `largest` function for any comparable type, then give a generic `Series<T>` a `peak` method that reuses it.
:::
:::

:::step{type=concept title="A type parameter and its bounds" file="17-generics/src/lib.rs" line="3-9"}
```rust
pub fn largest<T: PartialOrd + Copy>(items: &[T]) -> Option<T> {
    let mut best = *items.first()?;    // ? on an Option: an empty list returns None right here
    for &item in items {
        if item > best { best = item; }
    }
    Some(best)
}
```

`<T: PartialOrd + Copy>` reads "for any type T that can be compared and copied". Inside the function, `T` can do
exactly what its bounds promise and nothing else. Leave a bound out, and the compiler says which one is missing:

```text
error[E0369]: binary operation `>` cannot be applied to type `&T`
 --> 17-generics/src/bin/no_bound.rs:4:17
  |
4 |         if item > best {
  |            ---- ^ ---- &T
  |            |
  |            &T
  |
help: consider restricting type parameter `T` with trait `PartialOrd`
  |
1 | fn largest<T: std::cmp::PartialOrd>(items: &[T]) -> &T {
  |             ++++++++++++++++++++++
```
:::

:::step{type=task task=largest title="Your turn: the largest of anything" file="17-generics/src/lib.rs" line="3-9"}
Finish `largest`: `let mut best = *items.first()?;`, keep the larger in `for &item in items { if item > best { best =
item; } }`, and return `Some(best)`.

Press **Check**.
:::

:::step{type=history title="Templates, erasure, and copies made for you"}
:::before{title="One copy per type, by hand"}
Without generics, code was either copied for each type, or written for "any object" and checked only when it ran.
:::

**Ada** (**1983**) and C++ **templates** (**1990**) made generic code a language feature; C++ compiled a copy for each
type, fast but with famously long error messages. **Java** (**2004**) added generics by **erasure**: one compiled copy
for all types, with the types checked and then thrown away. **Go** added generics in **2022**. Rust checks a generic
function against its bounds **once**, so errors point at the generic code, and then makes a specialised copy per type
(**monomorphisation**), as fast as code written for that type by hand.

:::solved
**Write once, run at full speed for every type**, with errors that name the missing ability.
:::

:::timeline
- **1983** Ada generics.
- **1990** C++ templates.
- **2004** Java generics.
- **2022** Go generics.
:::
:::

:::step{type=concept title="Generic structs and impl blocks" file="17-generics/src/lib.rs" line="11-31"}
Types can be generic too. `Series<T>` holds a name and a `Vec<T>`:

```rust
pub struct Series<T> {
    pub name: String,
    pub values: Vec<T>,
}

impl<T: PartialOrd + Copy> Series<T> {   // these methods exist for every T with these abilities
    pub fn peak(&self) -> Option<T> { ... }
}
```

`Series<f64>` and `Series<u16>` are two different types, made from one definition. `Vec<T>`, `Option<T>` and
`HashMap<K, V>` are all generic types written exactly this way.
:::

:::step{type=task task=series_peak title="Your turn: the peak of a series" file="17-generics/src/lib.rs" line="26-31"}
Finish `peak`: return `largest(&self.values)`.

```bash run
cd /workspace/17-generics && cargo run --bin ch17-generics
```

Press **Check**.
:::

:::step{type=try title="One function, three types"}
```text
$ cargo run -q --bin ch17-generics
highest power: Some(2490.0)
highest fault code: Some(512)
latest hour: Some('q')
nothing: None
T07 power, kW: peak Some(2490.0)
T19 faults: peak Some(512)
```

One `largest`, called on `f64`, `u16` and `char`. The empty list needed a hint, `largest::<f64>(&[])`, because an empty
list says nothing about its type: that `::<f64>` (the "turbofish") names `T` explicitly. The two series are
`Series<f64>` and `Series<u16>`, and `peak` worked for both.

Behind the scenes the compiler made three versions of `largest`, one per type, each as fast as a hand-written
function.

:::diagram{name="rs-monomorph"}
One generic function in the source; the compiler checks it once and makes one specialised copy per type used.
:::
:::

:::step{type=predict title="Guess first"}
:::question
Could you call `largest` on a `&[String]`?
:::
- [ ] Yes
- [x] No: `String` can be compared, but it is not `Copy`
- [ ] Only with `clone()`
:::explain
The bounds are a contract. A version returning `Option<&T>` would need only `PartialOrd`, and work for `String` too.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `T: PartialOrd + Copy` mean?
:::
- [x] T can be any type that can be compared and copied
- [ ] T is a number
- [ ] T must be both types at once
:::explain
Bounds list the abilities the function's body needs.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Is a generic Rust function slower than one written for `f64`?
:::
- [ ] Yes, it checks types when it runs
- [x] No: the compiler makes a copy for each type used, optimised like hand-written code
- [ ] Only in debug builds
:::explain
The price is compile time and a slightly bigger program, not speed.
:::
:::

:::step{type=deep-dive title="Go deeper: generics in practice"}
**where clauses.** Long bounds read better after the signature: `fn f<T>(x: T) where T: PartialOrd + Copy`.

**Const generics.** `[f64; N]` with `const N: usize` lets a function work on arrays of any fixed length.

**When not to.** A generic used with one type is just harder to read; make code generic when the second type arrives.
:::

:::step{type=recap}
You can now:

- write a generic function with a type parameter and bounds;
- read E0369 and add the bound it asks for;
- define a generic struct and an `impl` block for it;
- explain monomorphisation: one source, a fast copy per type.

Next, chapter 18: traits, the abilities that bounds name.

:::photo{src="/lesson-images/rust/rs-17-notes.webp" alt="Handwritten notes about generics: fn f<T: Bound>(x: T); Bounds = what T can do; Checked once, copied per type; Series<T> is generic too; No run-time cost" ai="true"}
One page of notes for this chapter.
:::
:::
