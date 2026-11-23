:::step{type=story title="Forty turbines in one log"}
The farm's log mixes all 40 turbines, line after line: T07, then T12, then T31, then T07 again. The control room
wants totals **per turbine**: how many kWh did each one make today? And it wants to know which turbines said
**nothing at all**, because a turbine that stops reporting may have lost power, or its radio, or worse.

A list is the wrong shape for both questions. Looking up "T07's total so far" in a list means searching it every time.
What Windwatch needs is a **map** from turbine id to total, where finding a key takes the same short time whether the
map holds 4 turbines or 4 million keys, and a **set** of the turbines it has heard from.

:::mission
Add up each turbine's energy in a HashMap, then find the farm's silent turbines with a HashSet.
:::
:::

:::step{type=concept title="HashMap: keys to values" file="14-hashmap/src/lib.rs" line="4-18"}
```rust
use std::collections::HashMap;

let mut energy: HashMap<String, f64> = HashMap::new();
energy.insert("T07".to_string(), 350.0);
energy.get("T07")          // Some(&350.0)
energy.get("T40")          // None
energy["T07"]              // 350.0, or a panic if the key is missing
```

The everyday way to add to a total is the **entry** API:

```rust
*energy.entry(turbine.to_string()).or_insert(0.0) += kwh;
```

Read it right to left: find this turbine's entry; if it is not there yet, insert 0.0; that gives a `&mut f64`; `*`
reaches the number; add to it. One line, one lookup, for the first reading and every later one.
:::

:::step{type=task task=energy_by_turbine title="Your turn: energy per turbine" file="14-hashmap/src/lib.rs" line="4-18"}
In the loop of `energy_by_turbine`, replace `let _ = (turbine, kw);` with
`*energy.entry(turbine.to_string()).or_insert(0.0) += kw * 10.0 / 60.0;`.

Press **Check**.
:::

:::step{type=history title="Finding things without searching"}
:::before{title="Searching every time"}
Finding a record by its key in a list means comparing it with every entry. A list of a million turbines' readings is
a million comparisons per lookup.
:::

In **1953** Hans Peter Luhn, at IBM, described **hashing**: turn the key into a number (its **hash**), and use that
number to pick a slot directly. Finding a key then takes about the same time however many keys there are. Hash tables
became the workhorse of compilers, databases and caches. In **2011**, researchers showed that a web server whose hash
function an attacker could predict could be slowed to a crawl by keys chosen to land in the same slot. Rust's
`HashMap` uses **SipHash** with a random key chosen when the program starts, which defends against that, and is why
its order changes from run to run.

:::solved
**Lookups in constant time**, safe against keys chosen to collide.
:::

:::timeline
- **1953** Luhn: hashing at IBM.
- **2011** Hash-flooding attacks on web servers.
- **2015** Rust's HashMap: random SipHash keys from the start.
:::
:::

:::step{type=concept title="HashSet: is it in there?" file="14-hashmap/src/lib.rs" line="20-27"}
A `HashSet` is a map with keys only: it answers "have we seen this?" in one step, and keeps each value once.

```rust
let heard: HashSet<&str> = reported.iter().copied().collect();
heard.contains("T07")      // true or false
```

`.iter().copied().collect()` turns the list into a set (chapter 21 explains these iterator methods). Duplicates
disappear: three readings from T07 make one entry.

| Want | Use |
|---|---|
| a value per key | `HashMap<K, V>` |
| "is it there?" | `HashSet<T>` |
| keys in sorted order | `BTreeMap<K, V>`, `BTreeSet<T>` |

:::diagram{name="rs-entry"}
Each line finds its turbine's slot by hash; the first reading creates it at zero, later ones add to it.
:::
:::

:::step{type=task task=silent_turbines title="Your turn: the silent turbines" file="14-hashmap/src/lib.rs" line="20-27"}
Finish `silent_turbines(farm, reported)`: for each `id` in `farm` where `!heard.contains(id)`, push `id.to_string()`
onto a `Vec`; sort it and return it.

```bash run
cd /workspace/14-hashmap && cargo run
```

Press **Check**.
:::

:::step{type=try title="The same program, two different orders"}
The same program, run twice:

```text
$ cargo run -q
HashMap, in its own order:
  T07: 1086.7 kWh
  T31: 416.7 kWh
  T12: 50.8 kWh
  T19: 50.8 kWh
BTreeMap, sorted by key: {"T07": 1086.6666666666665, "T12": 50.83333333333333, "T19": 50.833333333333336, "T31": 416.6666666666667}
T07 made 1086.7 kWh; T40 made None
36 of 40 turbines are silent; the first five: ["T01", "T02", "T03", "T04", "T05"]
$ cargo run -q
HashMap, in its own order:
  T07: 1086.7 kWh
  T19: 50.8 kWh
  T12: 50.8 kWh
  T31: 416.7 kWh
...
```

(The second run's last lines were the same, and are shortened with "...".) The totals are identical; the **order** is
not. A `HashMap` keeps no order, and Rust's picks a new random hash key each run, on purpose. Never rely on a
`HashMap`'s order: when people will read it, collect it into a `BTreeMap` (sorted by key), as the next line did.

T12 and T19 made the same energy, 50.8 kWh, in different ways: T12 sent two weak readings (140 and 165 kW), T19 one
reading of 305. `energy.get("T40")` gave `None`: T40 never reported. And the silent list says only 4 of 40 turbines are
in this small sample; on a real day, any turbine on that list is a phone call.
:::

:::step{type=predict title="Guess first"}
:::question
`let mut m = HashMap::new(); m.insert("T07", 1); m.insert("T07", 2);` What is `m.len()` and `m["T07"]`?
:::
- [ ] 2 and 1
- [x] 1 and 2: a key appears once; inserting again replaces the value
- [ ] It panics
:::explain
`insert` returns the old value (`Some(1)`) so you can tell it replaced one.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why might two runs of the same program print a HashMap in different orders?
:::
- [x] Rust's HashMap hashes with a random key chosen each run, to resist hash-flooding attacks
- [ ] It is a bug
- [ ] Because of threads
:::explain
Use `BTreeMap`, or sort the keys, whenever order matters.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `entry(k).or_insert(0.0)` give back?
:::
- [ ] A copy of the value
- [x] A `&mut` to the value in the map, created at 0.0 if the key was new
- [ ] `Some` or `None`
:::explain
That is why `*... += kwh` changes the total inside the map.
:::
:::

:::step{type=deep-dive title="Go deeper: maps and sets in practice"}
**Keys must be hashable.** Any type with `#[derive(Hash, Eq, PartialEq)]` can be a key; `f64` cannot (NaN again).

**Set operations.** `a.difference(&b)`, `a.intersection(&b)` and `a.union(&b)` work on whole sets at once:
`silent_turbines` is `farm` minus `heard`.

**Counting.** `*counts.entry(word).or_insert(0) += 1;` counts anything: faults per turbine, lines per hour.
:::

:::step{type=recap}
You can now:

- keep a value per key in a `HashMap`, and add to it with `entry().or_insert()`;
- answer "have we seen it?" with a `HashSet`;
- choose `BTreeMap` when order matters;
- explain why a `HashMap`'s order changes from run to run.

Next, chapter 15: errors you can handle, with `Result` and `?`.

:::photo{src="/lesson-images/rust/rs-14-notes.webp" alt="Handwritten notes about maps and sets: HashMap: key -> value; entry().or_insert(0.0); HashSet: is it there?; No order! Use BTreeMap; Silent turbine = call someone" ai="true"}
One page of notes for this chapter.
:::
:::
