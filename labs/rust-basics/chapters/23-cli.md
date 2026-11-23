:::step{type=story title="A tool the night shift can run"}
Until now Windwatch has been code in chapters: functions, tests, a `main` that prints. The night shift at the Kutch
Coast Wind Farm needs a **program**: something they can type in a terminal, point at last night's log, and read.

```text
windwatch data/farm.csv --turbine T12 --low-kw 300
```

That one line holds a lot: a file name, two options with values, a default when an option is missing, a `--help`
page, and kind errors when someone types `--turbin` or names a file that does not exist. Writing all of that by hand is
a week of fiddly code. In Rust it is a struct with a few attributes, and two crates from the Rust ecosystem: **clap**
for the arguments and **csv** with **serde** for the log.

:::mission
Turn `Args` into a real command line with `--turbine` and `--low-kw` options, then read the CSV log into typed
`Reading`s with errors that name the file and the row.
:::
:::

:::step{type=concept title="Arguments as a struct" file="23-cli/src/lib.rs" line="8-24"}
clap's **derive** reads a struct and writes the whole argument parser for you:

```rust
#[derive(Parser)]
#[command(name = "windwatch", version, about)]
pub struct Args {
    /// The log file              <- a doc comment becomes the help text
    pub file: PathBuf,            // no attribute: a positional argument, required

    #[arg(long)]                  // --turbine T07
    pub turbine: Option<String>,  // Option: may be left out

    #[arg(long, default_value_t = 200.0)]
    pub low_kw: f64,              // --low-kw 150, or 200 when left out
}
```

| You write | clap gives you |
|---|---|
| a field with no attribute | a positional argument, in order |
| `#[arg(long)]` | an option named after the field: `low_kw` becomes `--low-kw` |
| `Option<T>` | an argument that may be missing (`None`) |
| `default_value_t = ...` | the value when it is missing, shown in `--help` |
| a typed field (`f64`, `PathBuf`) | the text checked and converted, with an error if it does not fit |

`Args::parse()` in `main.rs` reads the real command line, and on `--help` or a mistake prints a message and exits.

:::diagram{name="rs-cli"}
The command line becomes an Args struct: clap matches names, fills defaults, converts types, or explains the mistake.
:::
:::

:::step{type=task task=cli_args title="Your turn: options, not positions" file="23-cli/src/lib.rs" line="15-23"}
Right now `turbine` and `low_kw` have no `long`, so clap expects them as more positions (`windwatch farm.csv T07 150`).
Add `#[arg(long)]` above `turbine`, and change the line above `low_kw` to `#[arg(long, default_value_t = 200.0)]`.
Remove the TODO.

```bash run
cd /workspace/23-cli && cargo run -q -- --help
```

Press **Check**.
:::

:::step{type=history title="From getopt to clap"}
:::before{title="Every program parsed by hand"}
Early Unix programs read their arguments one character at a time, each in its own way: some took `-f file`, some
`-ffile`, some neither. Help pages, if any, were written separately and drifted out of date.
:::

**getopt** (Unix, early **1980s**) gave C programs one shared way to read short options like `-v`. The GNU project
added **long options** such as `--verbose` (**1990s**), the style almost every tool uses today. Comma-separated values
are older than both: spreadsheets and databases swapped CSV files for decades before **RFC 4180** (**2005**) wrote the
format down. In Rust, Kevin Knapp's **clap** (**2015**) and David Tolnay's work on **serde** (1.0 in **2017**) turned
both jobs into attributes on a struct. Command-line tools became one of the things Rust is best known for:
Andrew Gallant's **ripgrep** (**2016**), a search tool now built into VS Code, is the best-known example, and Gallant
also wrote the **csv** crate this chapter uses.

:::solved
**A full command line in a struct.** Options, defaults, types, help text and error messages all come from one
definition, so they cannot disagree.
:::

:::timeline
- **1980s** getopt: short options for C.
- **1990s** GNU long options: --verbose.
- **2005** RFC 4180 writes down CSV.
- **2015** clap for Rust.
- **2017** serde 1.0.
:::
:::

:::step{type=concept title="A CSV log, read into structs" file="23-cli/src/lib.rs" line="26-43"}
The log's first line names the columns: `turbine,time,wind_ms,power_kw`. With `#[derive(Deserialize)]` on `Reading`,
serde matches each column to the field of the same name and converts the text: `"12.4"` becomes the `f64` 12.4.

```rust
let mut reader = csv::Reader::from_path(path)          // opens the file, reads the header
    .with_context(|| format!("cannot open {}", path.display()))?;
for row in reader.deserialize() {                      // one Result<Reading, csv::Error> per row
    let reading: Reading = row.with_context(|| format!("bad row in {}", path.display()))?;
    readings.push(reading);
}
```

`reader.deserialize()` needs to know what to make, and `let reading: Reading` tells it. `with_context` is anyhow's
(chapter 16): it wraps the error with a line a person can act on, and keeps the original underneath, so the night shift
reads both "which file" and "what was wrong".
:::

:::step{type=task task=read_csv title="Your turn: read the log" file="23-cli/src/lib.rs" line="35-43"}
Finish `read_readings(path)`: open the file with `csv::Reader::from_path(path)` and the context
`"cannot open {}"`; then for each `row` in `reader.deserialize()`, make a `Reading` with the context `"bad row in {}"`
and push it. Return `Ok(readings)`.

```bash run
cd /workspace/23-cli && cargo run -q -- data/farm.csv
```

```bash run
cd /workspace/23-cli && cargo run -q -- data/broken.csv
```

Press **Check**.
:::

:::step{type=try title="The night shift's program"}
The help page, written entirely by clap from the struct and its doc comments:

```text
$ cargo run -q -- --help
Summarise a wind farm's turbine log

Usage: windwatch [OPTIONS] <FILE>

Arguments:
  <FILE>  The log file: CSV with the header turbine,time,wind_ms,power_kw

Options:
      --turbine <TURBINE>  Only this turbine, like T07
      --low-kw <LOW_KW>    Flag readings below this power (kW) while the wind is 6 m/s or more [default: 200]
  -h, --help               Print help
  -V, --version            Print version
```

Last night's log, then one turbine with a higher limit:

```text
$ cargo run -q -- data/farm.csv
8 readings
low: T12 at 2026-11-24 10:10: 140 kW in 7.5 m/s
low: T12 at 2026-11-24 10:20: 165 kW in 7.9 m/s
$ cargo run -q -- data/farm.csv --turbine T12 --low-kw 300
2 readings
low: T12 at 2026-11-24 10:10: 140 kW in 7.5 m/s
low: T12 at 2026-11-24 10:20: 165 kW in 7.9 m/s
```

Three kinds of mistake, three clear answers:

```text
$ cargo run -q -- data/broken.csv
Error: bad row in data/broken.csv

Caused by:
    CSV deserialize error: record 2 (line: 3, byte: 61): field 3: invalid float literal
$ cargo run -q -- data/nothing.csv
Error: cannot open data/nothing.csv

Caused by:
    No such file or directory (os error 2)
$ cargo run -q -- data/farm.csv --turbin T12
error: unexpected argument '--turbin' found

  tip: a similar argument exists: '--turbine'
```

In `broken.csv`, line 3 has `22O0` (a letter O) where the power should be: serde names the record, the line, the byte
and the field. The second error comes from the operating system, wrapped by your context. The third is clap's own,
with a suggestion. None of them is a panic or a stack trace: `main` returns `anyhow::Result`, and anyhow prints the
chain.
:::

:::step{type=predict title="Guess first"}
:::question
Someone runs `windwatch data/farm.csv --low-kw lots`. What happens?
:::
- [ ] low_kw becomes 0.0
- [x] clap refuses it before your code runs: "invalid value 'lots' for '--low-kw <LOW_KW>': invalid float literal"
- [ ] The program panics
:::explain
The field is an `f64`, so clap converts the text and reports a value that does not fit, with the option's name.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does the text of `--help` come from?
:::
- [ ] A separate help file
- [x] The struct: field names, types, defaults and the `///` doc comments
- [ ] clap guesses it
:::explain
Change a doc comment and the help changes with it. Help and code cannot drift apart.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
How does serde know which CSV column goes into `wind_ms`?
:::
- [ ] By position only
- [x] By the header: the column named `wind_ms` fills the field named `wind_ms`
- [ ] It does not; you match them by hand
:::explain
Reorder the columns in the file and it still works. Rename one and serde reports the missing field.
:::
:::

:::step{type=deep-dive title="Go deeper: tools people rely on"}
**Exit codes.** Returning `Err` from `main` exits with code 1, so scripts can tell success from failure
(`windwatch log.csv && send-report`).

**Subcommands.** `#[derive(Subcommand)]` on an enum gives `windwatch summary ...` and `windwatch check ...`, like
`cargo build` and `cargo test`.

**Shipping it.** `cargo build --release` makes one file, `target/release/windwatch`, with everything inside: copy it to
another Linux machine and it runs, with no Rust installed there. `cargo install --path .` puts it on your own `PATH`.

**Big files.** `csv` reads row by row, so a 10 GB log never sits in memory at once if you process rows as they arrive
instead of collecting them.
:::

:::step{type=recap}
You can now:

- describe a command line as a struct and let clap parse it;
- choose between positional arguments, `--long` options, `Option` and defaults;
- read a CSV file into typed structs with csv and serde;
- give every error a context that names the file, and let anyhow print the chain.

Next, chapter 24: smart pointers, for data that does not fit in one owner.

:::photo{src="/lesson-images/rust/rs-23-notes.webp" alt="Handwritten notes about a command-line tool: #[derive(Parser)] struct Args; #[arg(long)] = --name; Option = may be missing; serde: header -> fields; with_context: say which file" ai="true"}
One page of notes for this chapter.
:::
:::
