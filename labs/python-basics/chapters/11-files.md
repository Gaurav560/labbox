:::step{type=story title="Why files"}
So far every value lived only while the program ran. Real programs read data that already exists,
like a bank statement or a list of marks, and save results for later. Most of that data is plain
text, and very often **CSV**: values separated by commas, one record per line.

:::mission
In `file_tools.py`, write lines of text to a file (a warm-up), then read `expenses.csv` (a real
file in your workspace, with a few messy lines) into totals per category.
:::
:::

:::step{type=concept title="Opening, reading and writing"}
`open()` gives you a file. Use it in a `with` block, which closes the file for you even if an error
happens:

```python
with open("notes.txt") as f:          # read (the default mode)
    text = f.read()                   # the whole file as one string

with open("notes.txt") as f:
    for line in f:                    # one line at a time, "\n" included
        print(line.strip())

with open("out.txt", "w") as f:       # "w" creates or empties the file
    f.write("first line\n")           # write() adds no new line by itself
```

Mode `"a"` adds to the end instead of emptying the file.
:::

:::step{type=example title="Worked example: write a shopping list, then read it back"}
Writing and reading a file, with nothing left open:

```python
items = ["milk", "bread", "tea"]

with open("list.txt", "w") as f:   # 1. open to write
    for item in items:
        f.write(item + "\n")       # 2. one line each

with open("list.txt") as f:        # 3. open to read
    lines = [line.strip() for line in f]

lines   # ['milk', 'bread', 'tea']
```

1. `"w"` creates the file, or empties it if it exists.
2. `write` adds no new line by itself, so we add `"\n"`.
3. Reading line by line gives each line with its `"\n"`; `strip()` removes it.

The warm-up task is step 1 and 2 as a function.
:::

:::step{type=predict title="Guess first"}
:::question
`expenses.csv` starts with this line. What does `line.split(",")` give for it?

```text
2026-03-02,food,120
```
:::
- [ ] `["2026-03-02", "food", 120]`
- [x] `["2026-03-02", "food", "120"]`
- [ ] `["2026-03-02,food,120"]`
- [ ] `("2026-03-02", "food", "120")`
:::explain
Everything read from a text file is **text**, so the amount is the string `"120"`, not the number.
You convert it yourself with `float()`, which is exactly where messy files cause errors.
:::
:::

:::step{type=try title="Look at the real file"}
```bash run
head -6 expenses.csv; echo ...; grep -n -v -E '^[0-9-]+,[a-z]+,[0-9.]+$' expenses.csv
```

The second command lists the lines that do not look like `date,category,amount`: the header, a
blank line, a missing amount, a word where a number should be. Your code must survive all of them.
:::

:::step{type=task task=save_lines title="Warm-up: write lines to a file"}
In `file_tools.py`, make `save_lines(path, lines)` write each string in `lines` to the file as its
own line, replacing anything that was there, and return how many lines it wrote.

- `save_lines("report.txt", ["food: 200.00", "travel: 40.50"])` creates a file with exactly those
  two lines, each ending in a new line, and returns `2`
- `save_lines("empty.txt", [])` leaves an empty file and returns `0`
:::

:::step{type=concept title="The csv module"}
Splitting on commas breaks as soon as a value contains a comma (`"Mumbai, India"`). The `csv` module
handles that, and `DictReader` uses the header row to name the columns:

```python
import csv

with open("expenses.csv", newline="") as f:
    for row in csv.DictReader(f):
        print(row["category"], row["amount"])     # each row is a dictionary
```

A short line gives `None` for the missing columns, so expect `None` as well as bad text.

:::picture{name="file-lines"}
Each line of a CSV file is one row, cut at the commas.
:::
:::

:::step{type=task task=read_totals title="Totals from a CSV file"}
In `file_tools.py`, make `read_totals(path)` read a CSV file with the header `date,category,amount`
and return a dictionary of the total amount per category, **rounded to 2 decimals**. Skip rows that
are blank, have no amount, or have an amount that is not a number.

For a file with these rows (after the header):

```text
2026-03-02,food,120
2026-03-02,travel,40.50

2026-03-03,food,80
2026-03-04,food,abc
2026-03-04,travel,
```

it returns `{"food": 200.0, "travel": 40.5}`. Try it on `expenses.csv` in the terminal too.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which mode adds to the end of a file instead of replacing it?
:::
- [ ] `"r"`
- [ ] `"w"`
- [x] `"a"`
- [ ] `"x"`
:::explain
`"a"` appends. `"w"` replaces the whole file, which is what `save_lines` wants.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why use `csv.DictReader` instead of `line.split(",")`?
:::
- [ ] It is faster
- [x] It handles values with commas inside quotes, and names columns by the header
- [ ] It turns numbers into ints
- [ ] It skips the file's first line only
:::explain
A value like `"snacks, tea"` contains a comma; `split` would cut it in two. DictReader also gives each row as a dictionary keyed by the header.
:::
:::

:::step{type=deep-dive title="Paths, encodings and big files"}
`pathlib.Path` makes paths easy and works on every system: `Path("data") / "march.csv"` joins parts,
`.exists()` checks for a file and `.read_text()` reads it in one call.

Text in files is stored as bytes in an **encoding**. Python 3 uses UTF-8 by default on most systems,
but pass `encoding="utf-8"` explicitly when the data can contain names in other scripts, so your
program behaves the same everywhere.

Looping `for line in f` reads one line at a time, so a 10 GB log file uses almost no memory, while
`f.read()` loads it all at once. For huge data, always loop.
:::

:::step{type=recap}
- Use `with open(path) as f:`; the file closes itself.
- Modes: `"r"` read, `"w"` write (replaces), `"a"` append.
- Everything read from a file is text: convert numbers yourself, and expect bad values.
- `csv.DictReader` names the columns from the header; `write()` needs its own `"\n"`.
:::
