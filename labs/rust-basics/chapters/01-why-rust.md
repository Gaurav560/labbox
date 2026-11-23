:::step{type=story title="An elevator that crashed, and a language that would not let it"}
In 2006 a programmer named **Graydon Hoare** came home to his apartment building in Vancouver and found the elevator
broken, again. Its software had crashed. He lived on the 21st floor. Climbing the stairs, he thought about why
programs like that crash so often: most of them were written in C or C++, languages that let a program read memory it
no longer owns, or write past the end of a list, and nobody notices until the day it breaks.

That evening he started a small language of his own, with a strict idea: **the compiler should refuse to build a
program that could make those mistakes**. Not warn about them, refuse. He named it after the rust fungi, tough little
organisms that are hard to kill. That language is **Rust**.

In this course you will build **Windwatch**, the monitoring software of a wind farm on the Kutch coast in Gujarat:
40 turbines, each writing down its wind speed, rotor speed and power every few minutes. A monitor like that must never
crash on a bad line of data, must be fast with millions of readings, and must watch 40 turbines at once. Those are
exactly the things Rust is good at. Today, Windwatch says its first words.


Wind turbines along the Gujarat coast, where the wind off the Arabian Sea is strong and steady. Windwatch watches 40 of them.

:::photo{src="/lesson-images/rust/windfarm.webp" alt="A row of tall white wind turbines on a flat sandy shore behind rough blue sea and a rocky breakwater" credit="Priyaansh pandey" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Windmills_of_gujarat.jpg"}
Wind turbines on the coast of Gujarat.
:::
:::mission
Make Windwatch introduce itself, then fix a program that Rust refuses to build, with the compiler's help.
:::
:::

:::step{type=history title="From one programmer's evenings to the Linux kernel"}
:::before{title="Fast, or safe: pick one"}
For decades a team had to choose. C and C++ ran fast and controlled memory directly, and about **70%** of the serious
security bugs in Microsoft's and Google's software came from memory mistakes. Java, Python and Go were safe, but paid
for it with a garbage collector, a program that runs alongside yours and cleans up memory, using time and space.
:::

**Mozilla**, the makers of Firefox, began paying for Rust's development in **2009**, hoping to build a faster, safer
browser engine. Rust **1.0** came out on **15 May 2015**, with a promise that code written for 1.0 would keep
compiling. In **2021** Amazon, Google, Huawei, Microsoft and Mozilla founded the **Rust Foundation** to look after it.
In **December 2022** Linux 6.1 accepted Rust as the second language of the Linux kernel, after C, something no other
language had managed in thirty years. Android, Windows and the servers of most large cloud companies now have Rust
inside, and Rust has been the developers' most admired language in Stack Overflow's survey every year since 2016.

:::solved
**Fast and safe at once.** Rust checks memory safety when it compiles, so the program needs no garbage collector and
runs about as fast as C.
:::

:::timeline
- **2006** Graydon Hoare starts Rust after an elevator crash.
- **2009** Mozilla sponsors Rust.
- **2015** Rust 1.0.
- **2021** The Rust Foundation.
- **2022** Rust in the Linux kernel.
:::

Rust programmers call themselves Rustaceans, and their unofficial mascot is Ferris the crab, drawn by Karen Rustad Tölva in 2015 and given to everyone with no rights reserved.

:::photo{src="/lesson-images/rust/ferris.webp" alt="Ferris, a cartoon orange crab with a spiky shell, big round eyes and raised claws" credit="Karen Rustad Tölva" license="CC0" source="https://commons.wikimedia.org/wiki/File:Rustacean-orig-noshadow.svg"}
Ferris, the unofficial mascot of Rust.
:::
:::

:::step{type=concept title="Cargo: your project's builder" file="01-why-rust/Cargo.toml" line="1-6"}
Rust comes with **Cargo**, a tool that builds your code, runs it, tests it and fetches libraries. Every Rust project is
a **crate** with a `Cargo.toml` file that names it:

```toml
[package]
name = "ch01-why-rust"
version.workspace = true
edition.workspace = true
```

In this course every chapter folder is its own crate, and the `Cargo.toml` at the top of your workspace joins them all
into one **workspace**, so they share settings and one build folder. The `edition` (2024 here) is the version of the
language's rules your code uses.

| Command | What it does |
|---|---|
| `cargo build` | compiles the crate into a program |
| `cargo run` | builds it if anything changed, then runs it |
| `cargo run --bin name` | runs one of several programs in the crate |
| `cargo test` | builds and runs the tests (chapter 22) |
| `cargo check` | only checks that the code compiles; fast |
:::

:::step{type=example title="Worked example: a program in Rust" file="01-why-rust/src/bin/hello_windwatch.rs" line="2-7"}
Here is the smallest Rust program, the one every new Cargo project starts with:

```rust
fn main() {
    println!("Hello, world!");
}
```

- `fn main()` is a **function** named `main`. Every Rust program starts running there.
- `println!` prints one line. The `!` means it is a **macro**, a piece of code that writes more code for you when the
  program is compiled; for now, think of it as "a function with an exclamation mark".
- Every statement ends with a **semicolon** `;`.
:::

:::step{type=task task=hello_windwatch title="Your turn: Windwatch says hello" file="01-why-rust/src/bin/hello_windwatch.rs" line="2-7"}
Make the program print exactly these two lines, with two `println!` calls:

```text
Windwatch 0.1
Kutch Coast Wind Farm: 40 turbines, 100 MW
```

```bash run
cd /workspace/01-why-rust && cargo run --bin hello_windwatch
```

Press **Check**.
:::

:::step{type=try title="What cargo run did"}
```text
$ cargo run -q --bin hello_windwatch
Windwatch 0.1
Kutch Coast Wind Farm: 40 turbines, 100 MW
```

(`-q`, quiet, hides Cargo's own progress lines.) Cargo asked the Rust compiler, `rustc`, to turn your text into a real
machine-code program, saved it in the build folder, and ran it. Nothing interprets your code while it runs: what runs is
the program the compiler made, which is a big part of why Rust is fast.

:::diagram{name="rs-cargo-run"}
From the text you wrote to a running program: Cargo, the compiler, and the program it made.
:::
:::

:::step{type=concept title="A compiler that explains itself" file="01-why-rust/src/bin/fix_first_errors.rs" line="6-11"}
Rust's compiler is strict, and it is also the most helpful one you will meet. When it refuses your code, it says what
is wrong, where, and very often exactly how to fix it. Here is what it says about the second program in this chapter:

```text
error: expected `;`, found `println`
 --> 01-why-rust/src/bin/broken.rs:8:23
  |
8 |     let rated_mw = 2.5
  |                       ^ help: add `;` here
9 |     println("Turbines: {turbines}");
  |     ------- unexpected token

error[E0423]: cannot find function `println` in this scope
 --> 01-why-rust/src/bin/broken.rs:9:5
  |
9 |     println("Turbines: {turbines}");
  |     ^^^^^^^ not found in this scope
  |
  = note: a macro named `println` exists in another namespace
help: use `!` to invoke the macro
  |
9 |     println!("Turbines: {turbines}");
  |            +

error[E0277]: cannot multiply `{integer}` by `{float}`
  --> 01-why-rust/src/bin/broken.rs:10:42
   |
10 |     println!("Capacity: {} MW", turbines * rated_mw);
   |                                          ^ no implementation for `{integer} * {float}`
   ...
```

(The last error is shortened with "...". This is a copy of the file, named `broken.rs`.) Read each one in three parts:
the **error** line says what is wrong; the `-->` line says which file, line and column; the picture underneath points at
the exact spot, and `help:` suggests a fix. The third error is a rule you will meet in chapter 3: Rust never mixes a
whole number (`40`) and a decimal number (`2.5`) in arithmetic on its own. Write `turbines as f64` to turn 40 into a
decimal number first.
:::

:::step{type=task task=fix_first_errors title="Your turn: three mistakes, fixed" file="01-why-rust/src/bin/fix_first_errors.rs" line="2-11"}
Fix the three mistakes: add the missing semicolon, add the `!` to `println`, and multiply `turbines as f64` by
`rated_mw`. Run it after each fix and read what changes.

```bash run
cd /workspace/01-why-rust && cargo run --bin fix_first_errors
```

It should print:

```text
Turbines: 40
Capacity: 100 MW
```

Press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
A Rust program compiles without errors. Can it still read memory it no longer owns, the bug behind so many crashes?
:::
- [ ] Yes, as in C
- [x] No: the compiler refuses programs that could, unless you write the word `unsafe` and take that job yourself
- [ ] Only in release builds
:::explain
That promise is Rust's whole point. Chapter 6 shows how the compiler keeps it.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does the `!` in `println!` mean?
:::
- [ ] It prints loudly
- [x] `println!` is a macro: it writes code for you when the program is compiled
- [ ] It is required on every function
:::explain
You will use a few macros (`println!`, `format!`, `vec!`) long before you write one.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the fastest way to find out whether your code compiles, without running it?
:::
- [x] `cargo check`
- [ ] `cargo run --release`
- [ ] Reading it carefully
:::explain
`cargo check` skips making the program, so it answers in a moment. Editors run it for you as you type.
:::
:::

:::step{type=deep-dive title="Go deeper: Rust's tools"}
**rustup** installs and updates Rust itself (here, Rust 1.100.0). A new Rust comes out every six weeks, and code keeps
compiling.

**rustfmt** formats your code the standard way: `cargo fmt`. **Clippy** reads your code and suggests better ways to
write it: `cargo clippy`. Both are installed in this lab.

**crates.io** is the registry of Rust libraries (crates). This lab has no internet, so the crates the course uses are
already downloaded for you.

**Error codes.** `rustc --explain E0277` prints a full explanation, with examples, of any error code.
:::

:::step{type=recap}
You can now:

- explain why Rust exists: fast like C, without C's memory crashes;
- build and run a crate with Cargo;
- read a compiler error: what, where, and the suggested fix;
- write a `main` function that prints with `println!`.

Next, chapter 2: variables, and why they cannot change unless you say so.

:::photo{src="/lesson-images/rust/rs-01-notes.webp" alt="Handwritten notes about why Rust: Rust = fast AND memory safe; cargo run = build + run; fn main() starts the program; println! is a macro (the !); Read the error: what, where, help" ai="true"}
One page of notes for this chapter.
:::
:::
