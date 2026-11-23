:::step{type=story title="A quarter of a year, before the meeting starts"}
Each quarter the farm's owners ask for the energy each turbine produced. The log for one quarter is 40 turbines × 90
days × 144 readings a day: **518,400 lines**, 16 MB of text. The old script, written in Python, reads it and totals it.
It works, and it is not slow for one farm.

The company now runs twelve farms and wants the numbers every hour rather than every quarter, from a server it pays for
by the CPU-hour. Now "fast enough" has a price. This chapter measures Rust against the Python script on the same file,
and shows where Rust's speed comes from: not cleverness, but **not copying**.

:::mission
Parse a log line by slicing it instead of splitting it into new strings, then total the energy in a `HashMap` whose keys
borrow from the text.
:::
:::

:::step{type=concept title="Slicing, not splitting" file="27-speed/src/lib.rs" line="4-11"}
The usual way to read a line is to split it into a list of fields:

```rust
let fields: Vec<String> = line.split(',').map(|f| f.to_string()).collect();   // a Vec and 4 Strings per line
```

That is five memory allocations for every line, half a million times over, only to read two fields. The fast way
looks only for the commas it needs:

```rust
let (turbine, rest) = line.split_once(',')?;     // "T07" and "2026-11-24 10:10,12.4,2100"
let (_, power) = rest.rsplit_once(',')?;         // the last field: "2100"
Some((turbine, power.trim().parse().ok()?))
```

`split_once` and `rsplit_once` return **slices** of the line (chapter 8): two numbers each, a start and a length, and
nothing is copied. The function's type, `fn turbine_and_power(line: &str) -> Option<(&str, f64)>`, says so: the
turbine it returns borrows from the line (chapter 19's elision connects them).
:::

:::step{type=task task=fast_parse title="Your turn: parse by slicing" file="27-speed/src/lib.rs" line="4-11"}
Finish `turbine_and_power(line)` with the three lines above: `split_once(',')`, then `rsplit_once(',')` on the rest,
then parse the power. Each `?` turns a line without enough commas, or with a bad number, into `None`.

Press **Check**.
:::

:::step{type=history title="What speed is worth"}
:::before{title="Fast or safe, pick one"}
For decades the choice for a busy server was C or C++, fast but open to memory bugs, or a language with a garbage
collector, safe but heavier and with pauses while the collector runs.
:::

Companies started publishing what Rust changed for them. **Discord** (**2020**) moved a service from Go to Rust because
Go's garbage collector paused it every two minutes, and the latency spikes disappeared. **Cloudflare** replaced its
nginx-based proxy with **Pingora** (**2022**), written in Rust, and reported about **70% less CPU and 67% less memory**
for the same traffic, across a network that handles a large share of the web's requests. **AWS** built **Firecracker**
(**2018**), the small virtual machines under AWS Lambda, in Rust. Python is not left out: tools like **Polars** and
**Ruff** are written in Rust and called from Python, which is how a lot of Rust reaches people who never write it.

:::solved
**Speed you can bill.** On rented servers, CPU time and memory are money; a program that needs a sixth of the CPU
needs a sixth of the servers.
:::

:::timeline
- **2018** Firecracker, under AWS Lambda.
- **2020** Discord moves a service from Go to Rust.
- **2022** Cloudflare's Pingora: 70% less CPU.
:::

Where the bill comes from: rows of server racks, each drawing power and cooling around the clock.

:::photo{src="/lesson-images/rust/datacenter.webp" alt="A long, brightly lit aisle between rows of white server racks with perforated doors" credit="PiDatacenters" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ARacks_Amravati_Data_Center.jpg"}
Server racks in a data centre in Amaravati, India.
:::
:::

:::step{type=concept title="Keys that borrow" file="27-speed/src/lib.rs" line="13-20"}
```rust
pub fn energy_by_turbine(text: &str) -> HashMap<&str, f64> {
    let mut totals = HashMap::new();
    for line in text.lines() {
        if let Some((turbine, kw)) = turbine_and_power(line) {
            *totals.entry(turbine).or_insert(0.0) += kw * 10.0 / 60.0;   // ten minutes a reading: kWh
        }
    }
    totals
}
```

The map's keys are `&str`: slices of `text`. 518,400 lines, 40 turbines, and not one `String` is made for a key; the
map stores 40 slices that point into the file's text. The return type, `HashMap<&str, f64>`, tells every caller the
map may not outlive `text`, and the compiler holds them to it. In Python every line becomes a new string object, and
every field another.

:::diagram{name="rs-speed"}
One 16 MB string; every key in the map is a slice pointing into it, so totalling half a million lines copies nothing.
:::
:::

:::step{type=task task=borrowed_keys title="Your turn: total by turbine" file="27-speed/src/lib.rs" line="13-20"}
Finish `energy_by_turbine(text)` as above: make the map `mut`, and for each line that `turbine_and_power` accepts, add
`kw * 10.0 / 60.0` to `*totals.entry(turbine).or_insert(0.0)`.

```bash run
cd /workspace/27-speed && cargo run -q --release
```

```bash run
cd /workspace/27-speed && python3 compare.py
```

Press **Check**.
:::

:::step{type=try title="The race"}
The first run writes `data/quarter.log`; then each program reads the 16 MB file and totals it:

```text
$ cargo run -q --release
518400 lines, 16 MB, 40 turbines
T07: 2696858 kWh
read and totalled in 27.3 ms
$ cargo run -q --release
518400 lines, 16 MB, 40 turbines
T07: 2696858 kWh
read and totalled in 27.0 ms
$ python3 compare.py
T07: 2696858 kWh
read and totalled in 182.0 ms
$ cargo run -q
518400 lines, 16 MB, 40 turbines
T07: 2696858 kWh
read and totalled in 176.5 ms
```

| Version | Time | Against Rust release |
|---|---|---|
| Rust, `--release`, slices and borrowed keys | 27 ms | 1 × |
| Rust, `--release`, a `Vec<String>` and a `String` key per line | 62 ms | 2.3 × slower |
| Rust, debug build | 177 ms | 6.5 × slower |
| Python, the same job | 182 ms | 6.7 × slower |

The same answer every time, 2,696,858 kWh for T07. Rust in release is **6.7 times** faster than Python here, which is
typical for simple text work; arithmetic in plain Python loops often shows 20 to 100 times. The second row is the same Rust
program written the copying way (`split(',')` into `String`s), timed in a later run on the same machine (62.3 ms, while
the fast version took 25.8 ms in that run): more than twice as slow.
Half of Rust's advantage here came from not copying. And a debug build is as slow as Python: always measure with
`--release` (chapter 21).

For one file, the difference is a fraction of a second. For a server that does this work all day, it is the difference
between one machine and six or seven.
:::

:::step{type=predict title="Guess first"}
:::question
Could `energy_by_turbine` return its map after the text it was given has been dropped?
:::
- [ ] Yes, the keys were copied
- [x] No: the keys are slices of the text, so the compiler stops the map from outliving it
- [ ] Only in release builds
:::explain
`HashMap<&str, f64>` borrows from `text`. If the map must live longer, make `String` keys once per turbine, not per line.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where did the slower Rust version lose its time?
:::
- [ ] Parsing the numbers
- [x] Allocating a `Vec` and four `String`s for each of half a million lines
- [ ] Reading the file
:::explain
Allocation is cheap once and expensive half a million times. Slices avoid it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why compare in release, never in debug?
:::
- [x] Debug builds skip optimisation, and can be slower than Python, as the table shows
- [ ] Debug builds give wrong answers
- [ ] Python runs in release mode too
:::explain
Release is what users run. A debug timing measures something nobody uses.
:::
:::

:::step{type=deep-dive title="Go deeper: making Rust fast"}
**Measure first.** `cargo bench` with the `criterion` crate times a function many times and reports the spread;
`perf` and `cargo flamegraph` show which lines take the time.

**Bigger than memory.** `BufReader::new(file).lines()` reads a line at a time (each line a new `String`, but memory
stays small); `memmap2` maps a huge file into memory without reading it.

**More CPUs.** The log could be split into 16 parts, one thread each (chapter 25), and the maps merged at the end.

**Release settings.** In `Cargo.toml`, `[profile.release] lto = true` and `codegen-units = 1` let the optimiser see the
whole program at once, for a few more percent.
:::

:::step{type=recap}
You can now:

- parse text with `split_once` and `rsplit_once`, returning slices instead of new strings;
- build a `HashMap` whose keys borrow from the text, and read what its type promises;
- measure honestly: the same data, release builds, more than one run;
- explain where Rust's speed comes from, and what it is worth on a server bill.

Next, chapter 28, the last: Windwatch as a web service.

:::photo{src="/lesson-images/rust/rs-27-notes.webp" alt="Handwritten notes about speed: split_once: a slice, no copy; HashMap of &str keys borrows; 27 ms Rust, 182 ms Python; Copying cost 2x; Measure with --release" ai="true"}
One page of notes for this chapter.
:::
:::
