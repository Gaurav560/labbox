:::step{type=story title="Who cleans up the log?"}
Windwatch keeps a log of power readings for each turbine: thousands of numbers that grow every ten minutes. A list
like that lives in the computer's memory, and at some point it must be given back, or the program slowly eats all the
memory there is. But it must not be given back too early, while some other part of the program still reads it.

Languages have answered "who cleans up?" in two ways. In C, **you** do, by hand, and the mistakes (cleaning up twice,
too early, or never) are the crashes and security holes of chapter 1. In Java, Python and Go a **garbage collector**
does, a helper that runs alongside your program and costs time and memory. Rust has a third answer, checked entirely
when the program is compiled: **every value has exactly one owner**, and when the owner goes away, so does the value.

:::mission
Fix a function that uses a value after giving it away, then write one that takes a log, adds a reading, and gives the
log back.
:::
:::

:::step{type=concept title="The stack and the heap" file="06-ownership/src/main.rs" line="4-19"}
A running program keeps its data in two places:

| | Stack | Heap |
|---|---|---|
| holds | values of a fixed, known size: numbers, `bool`, tuples of them | data that can grow: a `Vec`, a `String` |
| speed | very fast: push on, pop off | slower: the program asks for a block of memory |
| cleaned up | automatically, when the function ends | by whoever owns it |

A `Vec<f64>` (a growable list of `f64`, chapter 13 covers it fully; `vec![...]` makes one) is two things: a small part
on the stack (where the numbers are, how many, how much room) and the numbers themselves on the heap.

:::diagram{name="rs-move"}
A move copies the small stack part and makes the old name unusable; the heap data is never copied and never freed twice.
:::
:::

:::step{type=concept title="Three rules, and the move" file="06-ownership/src/lib.rs" line="3-9"}
Rust's ownership rules are short:

1. Every value has one **owner** (a variable).
2. There is only ever **one** owner at a time.
3. When the owner goes out of scope (its `{ }` block ends), the value is **dropped**: its memory is given back.

So what does `let backup = log;` do with a vector? It cannot make two owners. It **moves** the vector: `backup` now
owns it, and `log` can no longer be used. Try, and the compiler explains:

```text
error[E0382]: borrow of moved value: `log`
 --> 06-ownership/src/bin/moved.rs:4:16
  |
2 |     let log = vec![2100.0, 2250.0];
  |         --- move occurs because `log` has type `Vec<f64>`, which does not implement the `Copy` trait
3 |     let backup = log;
  |                  --- value moved here
4 |     println!("{log:?} {backup:?}");
  |                ^^^ value borrowed here after move
  |
help: consider cloning the value if the performance cost is acceptable
  |
3 |     let backup = log.clone();
  |                     ++++++++
```

Without that rule both names would point at one heap block, and at the end both would free it: a "double free", one of
C's classic crashes. `.clone()` makes a real second copy of the heap data, when you really want two.

Small fixed-size values (numbers, `bool`, `char`) are **Copy**: assigning them copies them, and nothing moves. That is
why `let also_rated = rated;` leaves `rated` usable.
:::

:::step{type=task task=fix_moved_value title="Your turn: a backup that is really a copy" file="06-ownership/src/lib.rs" line="3-9"}
`with_backup` does not compile: it uses `log` after moving it into `backup`. Change `let backup = log;` to
`let backup = log.clone();`.

Press **Check**. (This crate does not compile until this is fixed, so do this task first.)
:::

:::step{type=history title="malloc, garbage collectors, and a third way"}
:::before{title="Two answers, each with a price"}
Manual memory management was fast and dangerous; garbage collection was safe and cost time, memory, and pauses at
unpredictable moments.
:::

C's `malloc` and `free` (**1972**) left cleaning up to the programmer. **John McCarthy** invented garbage collection for
**Lisp** in **1959**, and Java (1995), Python, C# and Go followed. C++ gave a middle way in the **1980s**: an object
cleans up its resources when its scope ends (Bjarne Stroustrup called it RAII), but nothing stopped a program from
keeping a pointer to an object that was gone. Research languages like **Cyclone** (**2002**) showed that a compiler
could track who owns memory and for how long. Rust made that tracking part of every program, and the compiler's
**borrow checker** became its most famous feature.

:::solved
**No garbage collector and no use-after-free.** Memory is given back at a point the compiler knows, and nothing can use
it afterwards.
:::

:::timeline
- **1959** Garbage collection in Lisp.
- **1972** malloc and free in C.
- **1980s** C++ cleans up at the end of a scope.
- **2002** Cyclone: the compiler tracks memory regions.
- **2015** Rust 1.0: ownership for everyone.
:::

John McCarthy, who invented Lisp and, for it, the garbage collector in 1959: a helper that finds memory nobody uses any more and gives it back.

:::photo{src="/lesson-images/rust/mccarthy.webp" alt="John McCarthy, an older man with white hair, a white beard and black glasses, in a checked shirt, outdoors" credit="null0" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:John_McCarthy_Stanford.jpg"}
John McCarthy at Stanford.
:::
:::

:::step{type=concept title="Ownership into and out of functions" file="06-ownership/src/lib.rs" line="11-15"}
Passing a value to a function moves it into the function, exactly like `let`. Returning a value moves it out again:

```rust
pub fn add_reading(mut log: Vec<f64>, kw: f64) -> Vec<f64> {
    log.push(kw);   // the function owns log now, and may change it (mut)
    log             // ...and gives it back to the caller
}

let log = add_reading(log, 2400.0);   // log moves in, a log comes back, shadowing the old name
```

This works, but moving everything in and out is clumsy. Chapter 7 shows the everyday way: lend the value instead.
:::

:::step{type=task task=add_reading title="Your turn: take, change, give back" file="06-ownership/src/lib.rs" line="11-15"}
Finish `add_reading`: `log.push(kw);` then return `log` as the last expression.

```bash run
cd /workspace/06-ownership && cargo run --bin ch06-ownership
```

Press **Check**.
:::

:::step{type=try title="Moves, a clone, and a copy"}
```text
$ cargo run -q --bin ch06-ownership
T07 log: [2100.0, 2250.0, 1980.0, 2400.0]
working: [], backup: [2100.0, 2250.0, 1980.0, 2400.0]
rated 2500, also 2500
site: Kutch Coast
```

- The log moved into `add_reading` and came back with 2400 added.
- `with_backup` cloned it: emptying the working copy left the backup untouched, so they really are two vectors.
- `rated` is a number, so `also_rated = rated` copied it, and both are still usable.
- `site` is a `String`, which lives on the heap like a `Vec`, so `name = site` moved it; `site` cannot be printed
  after that line.

None of this costs anything when the program runs. Every check happened when it was compiled.
:::

:::step{type=predict title="Guess first"}
:::question
`let a = String::from("T07"); let b = a; println!("{a}");` What happens?
:::
- [ ] It prints T07
- [x] It does not compile: `a` was moved into `b`
- [ ] It prints an empty line
:::explain
A `String` owns heap memory, so assigning it moves it. `let b = a.clone();` keeps both.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When is a `Vec`'s memory given back?
:::
- [ ] When a garbage collector notices
- [x] When its owner goes out of scope
- [ ] When the program ends
:::explain
Rust inserts the clean-up at the end of the owner's block, when compiling.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why can `let y = x;` with `x: u32` leave `x` usable?
:::
- [x] `u32` is Copy: small, fixed-size values are copied, not moved
- [ ] Numbers cannot be moved by accident
- [ ] Because of `mut`
:::explain
Copying four bytes is cheap and safe; copying a heap block silently would be neither, so `Vec` and `String` move.
:::
:::

:::step{type=deep-dive title="Go deeper: ownership in practice"}
**Clone with care.** `.clone()` copies all the heap data. It is the right fix when you need two copies; when you only
need to read, borrow instead (chapter 7).

**Drop.** You can give a value back early with `drop(log)`. Types can run their own code when dropped (closing a file,
releasing a lock), which is how Rust closes files without `finally` blocks.

**Moves are cheap.** A move copies the small stack part (three numbers for a `Vec`), never the heap data.
:::

:::step{type=recap}
You can now:

- explain the stack and the heap, and why heap data needs an owner;
- state the three ownership rules, and recognise a move;
- fix "use of moved value" with `.clone()` when two copies are really needed;
- move values into and out of functions, and tell Copy types from moved ones.

Next, chapter 7: borrowing, so functions can use a value without taking it.

:::photo{src="/lesson-images/rust/rs-06-notes.webp" alt="Handwritten notes about ownership: One owner per value; Owner gone = value dropped; let b = a; moves a Vec; clone() = a real copy; Numbers are Copy" ai="true"}
One page of notes for this chapter.
:::
:::
