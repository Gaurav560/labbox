:::step{type=story title="Who to call, and who shares the crew"}
When T12's blade sensor trips at night, Windwatch calls the **shift engineer**. If nobody answers, the **site manager**.
If nobody answers there, the **turbine maker's hotline**. An escalation chain: each step is a person, plus the rest
of the chain. That is a value that contains a smaller copy of its own kind, and Rust's first answer is "that type has
infinite size".

Then the repair crews. The North crew looks after T12 and T19. Both turbines report faults to **the same** crew, so
both need to hold it, and both need to add jobs to its list. One owner per value (chapter 6) and "shared or mutable,
not both" (chapter 7) seem to forbid exactly that.

Both problems have the same kind of answer: **smart pointers**, small types from the standard library that own
data in a particular way. This chapter uses three: `Box`, `Rc` and `RefCell`.

A real repair crew at work: two technicians on ropes at a turbine's blade.

:::photo{src="/lesson-images/rust/turbine-crew.webp" alt="Two technicians hanging on ropes beside the blade of a large white wind turbine, seen from below against a pale sky" credit="U.S. Department of Energy" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AWind_turbine_maintenance_%2851689968067%29.jpg"}
Rope-access technicians checking a turbine blade.
:::

:::mission
Build an escalation chain with `Box`, then let two turbines share one crew with `Rc<RefCell<Crew>>` and add jobs
to it.
:::
:::

:::step{type=concept title="Box: a value on the heap" file="24-smart-pointers/src/lib.rs" line="6-25"}
Rust must know every type's size when compiling. An `Escalation` that holds another `Escalation` directly would hold
another, which holds another, with no end:

```text
error[E0072]: recursive type `Escalation` has infinite size
```

`Box<T>` puts a `T` on the heap and holds only a pointer to it, which is always the same size (8 bytes). So:

```rust
pub enum Escalation {
    Call(String),                          // the last person
    CallThen(String, Box<Escalation>),     // a person, then the rest of the chain, on the heap
}
```

A `Box` is the simplest smart pointer: one owner, like any value, and when the box is dropped, so is what it points
to. `people()` walks the chain by calling itself on `rest`; a `Box` is used just like the value inside it.
:::

:::step{type=task task=build_chain title="Your turn: build the chain" file="24-smart-pointers/src/lib.rs" line="27-34"}
Finish `chain(contacts)` with a `match` on the slice:

- `[]` gives `None`;
- `[last]` gives `Some(Escalation::Call(last.to_string()))`;
- `[first, rest @ ..]` gives `Some(Escalation::CallThen(first.to_string(), Box::new(chain(rest)?)))`.

The last arm builds the rest of the chain the same way, and puts it in a box.

Press **Check**.
:::

:::step{type=concept title="Rc and RefCell: shared, and changeable" file="24-smart-pointers/src/lib.rs" line="36-57"}
`Rc<T>` (**reference counted**) lets several owners hold one value. `Rc::clone(&north)` does not copy the crew: it
adds one to a counter and gives back another pointer to the same crew. Each owner dropped takes one off; at zero, the
crew is dropped.

An `Rc` only gives shared access (`&T`), so the crew cannot be changed through it. `RefCell<T>` moves the borrow rules
from compile time to **run time**: `.borrow()` gives a shared borrow, `.borrow_mut()` a mutable one, and the
`RefCell` counts them as the program runs.

| Type | Owners | Change it? | Rules checked |
|---|---|---|---|
| `T` | one | if `mut` | when compiling |
| `Box<T>` | one, data on the heap | if `mut` | when compiling |
| `Rc<T>` | many | no | when compiling |
| `Rc<RefCell<T>>` | many | yes, with `.borrow_mut()` | **while running** |

Break the rule (two `borrow_mut` at once) and it is not undefined behaviour: the program stops with a clear panic.

:::diagram{name="rs-rc-refcell"}
Two turbines hold Rc pointers to one RefCell; each borrow_mut is counted, and the count drops when a turbine goes.
:::
:::

:::step{type=history title="Who frees shared memory?"}
:::before{title="Count by hand, or collect garbage"}
In C, memory shared by several parts of a program is freed by whoever is "last", and working out who is last is the
programmer's job. Get it wrong and the memory is freed twice, or never.
:::

**Reference counting** goes back to George Collins (**1960**): keep a count of the pointers to each object, and free
it when the count reaches zero. Python, Swift and Objective-C use it for every object. C++ put it in a library type,
`shared_ptr` (Boost around **2000**, the C++ standard in **2011**), next to `unique_ptr`, the equivalent of `Box`.
Early Rust had a garbage-collected pointer built into the language, written `@T`; it was removed before Rust 1.0
(**2014**), and `Rc` and `RefCell` in the standard library took its place. You pay for counting only where you choose
`Rc`; everything else has one owner and no counter at all.

:::solved
**Sharing when you ask for it.** One owner by default, many owners with `Rc`, changes to shared data with `RefCell`,
each visible in the type.
:::

:::timeline
- **1960** Reference counting (Collins).
- **2011** shared_ptr and unique_ptr in C++.
- **2014** Rust removes @T; Rc and RefCell instead.
:::
:::

:::step{type=task task=shared_crew title="Your turn: report a fault to the shared crew" file="24-smart-pointers/src/lib.rs" line="49-57"}
Finish `report_fault(fault)`: borrow the crew mutably for one line and push the job:
`self.crew.borrow_mut().jobs.push(format!("{}: {}", self.id, fault));`

```bash run
cd /workspace/24-smart-pointers && cargo run -q
```

Press **Check**.
:::

:::step{type=try title="One chain, one crew, three owners"}
```text
$ cargo run -q
CallThen("shift engineer", CallThen("site manager", Call("turbine maker's hotline")))
call in order: ["shift engineer", "site manager", "turbine maker's hotline"]
owners of the North crew: 3
North crew: ["T12: blade inspection", "T19: yaw motor noise"]
owners after T19 is removed: 2
```

The chain prints as nested boxes, three people deep. The North crew has **3** owners: the variable `north` in `main`,
T12 and T19. Each turbine added a job through its own `Rc`, and both jobs are in the one list. When T19 is dropped
(taken out for repairs), the count falls to 2; the crew lives on while anyone still holds it.

Now the rule broken on purpose. A small program keeps a shared `borrow()` alive while asking for a mutable one:

```rust
let jobs = RefCell::new(vec!["T12: blade inspection".to_string()]);
let reading = jobs.borrow();                                 // a shared borrow, still in use below
jobs.borrow_mut().push("T19: yaw motor noise".to_string());  // line 6
println!("{reading:?}");
```

```text
thread 'main' (366) panicked at 24-smart-pointers/src/bin/double_borrow.rs:6:10:
RefCell already borrowed
```

The same rule as chapter 7, "shared or mutable, not both", checked a moment later: while running, with the exact
line. Keep borrows short, as your task does: its `borrow_mut()` lasts one statement, so it is over before anyone else asks.
:::

:::step{type=predict title="Guess first"}
:::question
`let t20 = Turbine { id: "T20".into(), crew: Rc::clone(&north) };` How many crews exist now?
:::
- [ ] Two: T20 got a copy
- [x] One: `Rc::clone` copies the pointer and adds one to the count
- [ ] None until T20 reports a fault
:::explain
Cloning an `Rc` is cheap (one addition) precisely because the data is not copied.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `CallThen` hold a `Box<Escalation>` and not an `Escalation`?
:::
- [ ] Boxes are faster
- [x] An Escalation inside an Escalation would have no fixed size; a Box is always one pointer
- [ ] Enums cannot hold enums
:::explain
E0072 says exactly this, and its help suggests the `Box`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `RefCell` do that `&mut` cannot?
:::
- [ ] It turns off the borrow rules
- [x] It checks the same borrow rules while the program runs, so shared data can still be changed
- [ ] It makes the value thread-safe
:::explain
The rules are the same; only the time of checking moves. `RefCell` is for one thread; chapter 25 has `Mutex` for many.
:::
:::

:::step{type=deep-dive title="Go deeper: smart pointers in practice"}
**Cycles.** Two `Rc`s pointing at each other never reach zero, so they are never freed. `Weak<T>` (from
`Rc::downgrade`) points without owning; a crew can hold `Weak` pointers back to its turbines.

**Reach for them last.** Most Rust code needs none of these: one owner and borrows cover it. `Rc<RefCell<T>>`
everywhere is usually a sign that the data wants a different shape, such as a `HashMap` of crews looked up by name.

**Deref.** A smart pointer implements the `Deref` trait, which is why `rest.people()` works on a `Box` directly.
:::

:::step{type=recap}
You can now:

- put a value on the heap with `Box`, and build a type that contains itself;
- share one value between several owners with `Rc`, and read `Rc::strong_count`;
- change shared data with `RefCell` and `borrow_mut`, and read the panic when the rule is broken;
- choose the simplest owner that works.

Next, chapter 25: threads, and many turbines at once.

:::photo{src="/lesson-images/rust/rs-24-notes.webp" alt="Handwritten notes about smart pointers: Box = one owner, on the heap; Box makes recursive types work; Rc = many owners, counted; RefCell = borrow rules at run time; Rc of RefCell: shared and changeable" ai="true"}
One page of notes for this chapter.
:::
:::
