:::step{type=story title="One file is getting crowded"}
Windwatch now has readings, statuses, parsing, power curves and summaries. Put all of that in one `lib.rs` and it
becomes a long scroll where everything can touch everything. A team at the wind farm needs borders: the parsing code
in one place, the reports in another, and only a few chosen functions open to the rest of the program.

Rust's borders are **modules**. A module groups related code, usually in its own file, and everything in it is
**private** unless marked `pub`. A whole library is a **crate**: this chapter's crate is `ch12_modules`, and its
modules are `reading` and `report`. The compiler checks every border, and its error when you cross one is the subject
of this chapter's first task.

:::mission
Open the farm summary to code outside its module with `pub`, then give it a short public path with `pub use`.
:::
:::

:::step{type=concept title="mod, files and paths" file="12-modules/src/lib.rs" line="1-12"}
```text
12-modules/
  Cargo.toml          the crate: name "ch12-modules", so the library is ch12_modules
  src/
    lib.rs            the crate's root:  pub mod reading;  pub mod report;
    reading.rs        the module reading
    report.rs         the module report
    main.rs           a program that uses the library
```

- `pub mod report;` in `lib.rs` tells the compiler "the module `report` is in `src/report.rs`". A file that no `mod`
  line names is simply not part of the crate.
- Inside the crate, a path starts at `crate`: `crate::reading::parse_line`. `use` brings a name in so you can write
  just `parse_line` (`report.rs` does this).
- From outside (`main.rs`, tests, other crates), the path starts with the crate's name: `ch12_modules::reading::Reading`.
:::

:::step{type=concept title="Private until pub" file="12-modules/src/report.rs" line="13-16"}
Every function, struct, field and module is **private** by default: visible only inside its own module (and the
modules inside it). `pub` opens it. The unfinished `report.rs` forgot to:

```text
error[E0603]: function `farm_summary` is private
  --> 12-modules/src/lib.rs:10:21
   |
10 |     let s = report::farm_summary(lines);
   |                     ^^^^^^^^^^^^ private function
   |
note: the function `farm_summary` is defined here
  --> 12-modules/src/report.rs:16:1
   |
16 | fn farm_summary(lines: &[&str]) -> Summary {
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

Even `lib.rs`, the parent, cannot call a private function of its child module. Private is the default because it is
the safe one: you can change a private function freely, knowing nothing outside depends on it. Every `pub` is a
promise to the code that uses it.
:::

:::step{type=task task=make_public title="Your turn: open the summary" file="12-modules/src/report.rs" line="13-16"}
In `report.rs`, add `pub` in front of `fn farm_summary`.

Press **Check**.
:::

:::step{type=history title="Information hiding"}
:::before{title="Everything visible to everything"}
In early large programs any part could read and change any other part's data. Changing one detail anywhere could
break code anywhere else.
:::

In **1972** David Parnas's paper **"On the Criteria To Be Used in Decomposing Systems into Modules"** argued that a
module should **hide** its design decisions behind a small interface. Niklaus Wirth's **Modula-2** (**1978**) made
modules with explicit exports part of the language. Rust's modules follow that line: private by default, `pub` for
the interface, and the compiler enforcing the border on every build.

:::solved
**Small public surfaces.** Each module decides what the rest of the program may touch, and can change everything else
freely.
:::

:::timeline
- **1972** Parnas: hide design decisions in modules.
- **1978** Modula-2: modules in the language.
- **2015** Rust: private by default, crates and modules.
:::
:::

:::step{type=concept title="pub use: a short public path" file="12-modules/src/lib.rs" line="4-7"}
Users of the library should not need to know which file a function lives in. `pub use` **re-exports** a name: it makes
`ch12_modules::farm_summary` another path to `ch12_modules::report::farm_summary`.

```rust
pub use report::farm_summary;
```

Libraries use this all the time: you write `std::collections::HashMap`, while the type is defined deep inside the
standard library's own modules. The re-export is the library's front door; the module layout behind it can change.

:::diagram{name="rs-modules"}
The crate root names its modules; pub opens items at the border, and pub use gives them a short path from outside.
:::
:::

:::step{type=task task=re_export title="Your turn: a short path" file="12-modules/src/lib.rs" line="4-7"}
In `lib.rs`, replace the TODO with `pub use report::farm_summary;`.

```bash run
cd /workspace/12-modules && cargo run
```

Press **Check**.
:::

:::step{type=try title="A summary from three files"}
```text
$ cargo run -q
3 turbines, 4 readings (1 skipped), 0.72 MWh
first line: Some(Reading { turbine: "T07", time: "2026-11-24 10:10", wind_ms: 12.4, power_kw: 2100.0 })
```

`main.rs` called `summary_text` in `lib.rs`, which called `farm_summary` in `report.rs`, which called `parse_line` in
`reading.rs`: four files, each with one job, and the borders checked by the compiler. Five lines gave four readings
and one skip (`windy` again), from three turbines.

The energy is worth checking by hand once: the four readings are 2,100 + 2,180 + 60 + 0 = 4,340 kW, each held for ten
minutes, so 4,340 × 10 / 60 = 723 kWh, or **0.72 MWh**.
:::

:::step{type=predict title="Guess first"}
:::question
`pub struct Summary { turbines: usize }` (the field without `pub`). Can `main.rs` read `s.turbines`?
:::
- [ ] Yes, the struct is pub
- [x] No: fields are private too, unless each one is marked pub
- [ ] Only with `use`
:::explain
That is how a type can hide its inside and offer methods instead: `s.turbines()`.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You add `src/alarms.rs` but no `mod alarms;` line. What does the compiler do with the file?
:::
- [ ] Compiles it as a module
- [x] Ignores it: only files named by a `mod` line are part of the crate
- [ ] Reports an error
:::explain
The module tree starts at `lib.rs` (or `main.rs`) and follows `mod` lines.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `pub use report::farm_summary;` add?
:::
- [ ] A copy of the function
- [x] A second public path to the same function
- [ ] Nothing outside the crate
:::explain
Re-exports shape a library's public face without moving code.
:::
:::

:::step{type=deep-dive title="Go deeper: modules and crates"}
**`pub(crate)`.** Visible everywhere inside this crate, but not to other crates: the common middle ground.

**Modules in folders.** `src/report/mod.rs` or `src/report.rs` plus `src/report/charts.rs` make nested modules.

**Crates.** A package can have a library (`lib.rs`) and several programs (`main.rs`, `src/bin/*.rs`), like chapter 1.
Other packages depend on it in their `Cargo.toml`; the next chapters use crates from crates.io that way.
:::

:::step{type=recap}
You can now:

- split a crate into modules and files with `mod`;
- use paths with `crate::` inside and the crate's name outside;
- open items with `pub`, and read E0603;
- give a library a clean public face with `pub use`.

That ends Part 3. Next, chapter 13: vectors and strings in depth.

:::photo{src="/lesson-images/rust/rs-12-notes.webp" alt="Handwritten notes about modules: mod name; = src/name.rs; Private unless pub; crate::path inside; pub use = a short path; Small public surface" ai="true"}
One page of notes for this chapter.
:::
:::
