:::step{type=story title="One line of the log, and the part you need"}
Every ten minutes each turbine writes one line to Windwatch's log:

```text
T07,2026-11-24 10:10,12.4,2100
```

Turbine, time, wind speed in m/s, power in kW. Often Windwatch needs only a **part** of something: the turbine id at
the start of the line, or the last hour of a day's readings. Copying that part into a new string or a new vector every
time would be slow with millions of lines. What Windwatch needs is a way to **point at part** of a value it does not own
and does not copy. That is a **slice**: a borrowed view of a piece of a list or a text.

Text in Rust also comes in two types, `String` and `&str`, which confuses almost every newcomer. By the end of this
chapter the difference will be obvious.

:::mission
Return the turbine id as a slice of the line, without copying it, then return the last hour of readings as a slice of
the day.
:::
:::

:::step{type=concept title="String and &str" file="08-slices-and-strings/src/main.rs" line="17-23"}
| | `String` | `&str` |
|---|---|---|
| what | owns its text, on the heap | borrows some text that lives somewhere else |
| can grow? | yes: `push_str`, `+` | no |
| made by | `String::from("..")`, `format!`, `.to_string()` | `"literal"`, or slicing a `String`: `&site[..11]` |
| use for | text you build or keep | parameters that only read text |

A text literal like `"T07"` is a `&str` that points into the program itself (that is the `&'static str` of chapter 5).
A function that only reads text should take `&str`: it then accepts both a literal and a borrowed `String`
(`turbine_id(&line)` works when `line` is a `String`).
:::

:::step{type=concept title="Slicing with ranges" file="08-slices-and-strings/src/lib.rs" line="3-10"}
`&value[start..end]` borrows the part from `start` up to, not including, `end`; either side may be left out:

```rust
let line = "T07,2026-11-24 10:10,12.4,2100";
let comma = line.find(',').unwrap();   // 3: the position of the first comma
let id = &line[..comma];               // "T07": positions 0, 1 and 2
let rest = &line[comma + 1..];         // everything after the comma
```

`id` is a view into `line`, not a copy. The compiler makes sure it cannot outlive `line`.

`line.find(',')` returns `Some(position)` or `None` when there is no comma, so the real function uses `match` to handle
both (chapter 11 is all about `match`).
:::

:::step{type=task task=turbine_id title="Your turn: the turbine id, without copying" file="08-slices-and-strings/src/lib.rs" line="3-10"}
Finish `turbine_id(line)`: `match line.find(',') { Some(comma) => &line[..comma], None => line }`.

Press **Check**. (The check also makes sure you return a slice of the line, not a new `String`.)
:::

:::step{type=concept title="Slices of lists, and bytes of text" file="08-slices-and-strings/src/lib.rs" line="12-22"}
Lists slice the same way. `&[f64]` is a slice of `f64` values: it accepts a borrowed `Vec<f64>`, an array, or part of
either, which is why functions that read a list take `&[f64]`, not `&Vec<f64>`.

Asking for a position past the end does not read some other memory, as C would: it stops the program. For text there
is one more rule. Rust strings are **UTF-8**: an English letter is one byte, `₹` is three bytes, a Hindi letter is three.
Positions in a slice are **byte** positions, and a slice must not cut a character in half:

```text
$ cargo run -q --bin boundary

thread 'main' (335) panicked at 08-slices-and-strings/src/bin/boundary.rs:3:26:
end byte index 1 is not a char boundary; it is inside '₹' (bytes 0..3 of string)
```

Find positions with `find`, `split` or `char_indices`, never by counting letters yourself.

:::diagram{name="rs-slice"}
A slice is a pointer and a length into data someone else owns: no copy, and checked against the end.
:::
:::

:::step{type=history title="Reading past the end, and a code for every alphabet"}
:::before{title="Lengths nobody checked"}
In C a list is just a place in memory; nothing stops a program from reading past its end into whatever lies there.
:::

In **April 2014** the **Heartbleed** bug was found in OpenSSL, the code that encrypted a large part of the web. A
server trusted a length sent by the other side and copied that many bytes back, up to 64 KB of whatever was in memory
next: passwords, private keys. A Rust slice always carries its length and checks every position against it.

Text had its own past: each country's old encoding could not show another's letters. In **September 1992** Ken Thompson
and Rob Pike designed **UTF-8** one evening in a New Jersey diner, sketching it on a placemat: every character in the
world, with English text unchanged. Today almost the whole web uses it, and every Rust string is UTF-8.

:::solved
**Views that cannot run off the end**, and text that holds any language, checked so that no character is ever cut in
half.
:::

:::timeline
- **1992** UTF-8, on a placemat.
- **2014** Heartbleed: a read past the end.
- **2015** Rust: slices carry their length.
:::

The Heartbleed bug was the first security bug with its own name and logo. It came from one missing length check.

:::photo{src="/lesson-images/rust/heartbleed.webp" alt="A white heart with a thick red outline, red drops dripping from its bottom, on a black background" credit="Leena Kurjenniska / Codenomicon" license="CC0" source="https://commons.wikimedia.org/wiki/File:Heartbleed.svg"}
The Heartbleed logo, 2014.
:::
:::

:::step{type=task task=last_hour title="Your turn: the last hour of readings" file="08-slices-and-strings/src/lib.rs" line="12-17"}
Finish `last_hour(readings)`: `let start = readings.len().saturating_sub(6);` (which stops at 0 instead of going below
it), then return `&readings[start..]`.

```bash run
cd /workspace/08-slices-and-strings && cargo run --bin ch08-slices-and-strings
```

Press **Check**.
:::

:::step{type=try title="Ids, the last hour, and a rupee of three bytes"}
```text
$ cargo run -q --bin ch08-slices-and-strings
T07 at 12.4 m/s
T12 at 3.1 m/s
T31 at 25.6 m/s
last hour: [2050.0, 2100.0, 2150.0, 2200.0, 2250.0, 2300.0]
last hour of 3: [1850.0, 1900.0, 1950.0]
Kutch Coast (11 bytes of 21)
14 characters, 16 bytes
```

The ids and wind speeds came straight out of the lines: `turbine_id` copied nothing. `last_hour` returned the last six
of ten readings, and with only three it returned all three instead of panicking, thanks to `saturating_sub`.

The last line is worth a second look: `"₹4.20 per unit"` has **14** characters but takes **16** bytes, because `₹` is
three bytes. `.len()` counts bytes; `.chars().count()` counts characters. For Windwatch's log (plain letters and
digits) they agree; for a citizen's name in Gujarati, they would not.
:::

:::step{type=predict title="Guess first"}
:::question
`let v = vec![1.0, 2.0]; let s = &v[5..];` What happens?
:::
- [ ] `s` is empty
- [x] The program panics: 5 is past the end
- [ ] It reads whatever is in memory after the vector
:::explain
Rust checks the range. Use `v.get(5..)` to get `None` instead of a panic.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which parameter type should a function that only reads text take?
:::
- [ ] `String`
- [x] `&str`
- [ ] `&String`
:::explain
`&str` accepts literals and borrowed `String`s alike, and takes nothing away from the caller.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `"₹5".len()` return?
:::
- [ ] 2
- [x] 4: `₹` is three bytes in UTF-8, `5` is one
- [ ] 1
:::explain
`len` counts bytes. `"₹5".chars().count()` is 2.
:::
:::

:::step{type=deep-dive title="Go deeper: text in practice"}
**Splitting.** `line.split(',')` gives each field as a `&str` slice of the line, without copying; `wind_of` uses
`.split(',').nth(2)`.

**Building text.** `let mut s = String::new(); s.push_str("T07"); s += ",12.4";` or simply `format!`.

**Bytes.** `line.as_bytes()` gives a `&[u8]`, the fastest way to scan plain ASCII logs, and how fast parsers work.
:::

:::step{type=recap}
You can now:

- tell `String` (owns, can grow) from `&str` (borrows), and choose `&str` for parameters;
- slice text and lists with ranges, without copying;
- return a slice of a parameter, safely;
- explain bytes versus characters in UTF-8, and avoid cutting a character in half.

That ends Part 2. Next, chapter 9: structs, so a reading becomes one value with named fields.

:::photo{src="/lesson-images/rust/rs-08-notes.webp" alt="Handwritten notes about slices and strings: String owns, &str borrows; &text[..3] = a slice, no copy; Read-only params: &str, &[T]; Out of range = panic; len() counts bytes, not chars" ai="true"}
One page of notes for this chapter.
:::
:::
