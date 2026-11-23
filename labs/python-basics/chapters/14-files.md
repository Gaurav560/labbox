:::step{type=story title="Where does your data go when the program ends?"}
Run any program from this course, close it, and run it again. Everything it knew is gone: every variable, every
list, every total. Variables live in the computer's memory, and memory is wiped the moment a program ends.

So how does a notes app remember yesterday's notes? How does a bank remember your balance? They **write it down**
somewhere that survives: a **file** on disk (or a database, which is files underneath). Today Pocket learns to
write its records to a file and to read a whole month of real expenses back.

:::photo{src="/lesson-images/python/hard-drive.webp" alt="An opened laptop hard drive showing its shiny disk and the arm that reads it" credit="Evan-Amos" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Laptop-hard-drive-exposed.jpg"}
Inside a hard drive: the shiny disk keeps your files as tiny magnetic patterns, even with the power off. Memory forgets when a program ends; this does not.
:::

:::mission
Write `save_lines`, which saves lines of text to a file, and `read_totals`, which reads a real CSV file of
expenses, survives its messy rows, and adds up each category.
:::
:::

:::step{type=concept title="Opening, reading and writing a file"}
Working with a file always has three moments: **open** it, **read or write**, **close** it. Python's `with`
statement does the opening and, crucially, the closing for you:

```python
with open("diary.txt", "w") as f:
    f.write("jelly 15\n")
```

`open(path, mode)` gives back a file object, here named `f`. The **mode** says what you want to do:

| Mode | Means | If the file exists | If it does not |
|---|---|---|---|
| `"r"` (the default) | read | read it from the start | `FileNotFoundError` |
| `"w"` | write | **empties it first** | creates it |
| `"a"` | append | adds to the end | creates it |

When the indented block ends, `with` closes the file, even if an error happened inside. Closing matters: until a
file is closed, what you wrote may still be waiting in memory, not on disk.

One detail that catches everyone: `f.write(...)` writes **exactly** what you give it. It does not add a new line
like `print` does, so you add `"\n"` yourself.

:::picture{name="file-lines"}
A text file is a stack of lines: you can write them in, add more at the end, and read them back one by one.
:::
:::

:::step{type=try title="Pocket's diary" file="14-files/diary.py" line="2-11"}
Open `diary.py` and run it:

```bash run
cd /workspace/14-files && python3 diary.py
```

```text
['jelly', '15']
['bus', '30']
['lunch', '120']
```

A file called `diary.txt` has appeared in the folder: open it in the editor. Now the curious part: run the
program **again**. Do you get six lines now? No, the same three. The `"w"` at the start empties the file every
time; only the `"a"` part adds. Change the first `"w"` to `"a"`, run it twice, and watch the diary grow.

Reading a file line by line with `for line in f:` gives each line **with** its `"\n"` at the end, which is why the
program uses `line.strip()` before `split()`.
:::

:::step{type=example title="Worked example: write a list, one item per line"}
To save a list of strings, loop over it and write each one with its own new line:

```python
def save_names(path, names):
    with open(path, "w") as f:
        for name in names:
            f.write(f"{name}\n")
    return len(names)

save_names("guests.txt", ["Asha", "Ravi"])    # gives back 2
```

1. `"w"` because saving means "this is the whole content now": any old content is replaced.
2. One `write` per name, each ending in `"\n"`, so the file has one name per line.
3. It gives back how many it wrote, so the caller knows what happened.

An empty list gives an empty file, and `0`.
:::

:::step{type=predict title="Guess first"}
:::question
A file `notes.txt` contains three lines. You run `with open("notes.txt", "w") as f: f.write("new\n")`. What is in
the file now?
:::
- [ ] The three old lines, then `new`
- [x] Only `new`
- [ ] `new`, then the three old lines
:::explain
Opening with `"w"` empties the file first. To keep the old lines and add one, use `"a"`.
:::
:::

:::step{type=task task=save_lines title="Your turn: save some lines"}
Open `file_tools.py` and make `save_lines(path, lines)` write each string from `lines` to the file at `path`, one
per line (each followed by a new line), replacing anything that was there. It gives back how many lines it wrote.

`save_lines("report.txt", ["food: 200.00", "travel: 40.50"])` gives `2`, and the file then contains exactly
those two lines. `save_lines("empty.txt", [])` gives `0` and leaves an empty file.

```bash run
cd /workspace/14-files && python3 -c "from file_tools import save_lines; print(save_lines('report.txt', ['food: 200.00', 'travel: 40.50']))" && cat report.txt
```

Then press **Check**.
:::

:::step{type=concept title="CSV: a table in a text file" file="14-files/expenses.csv" line="1-6"}
Open `expenses.csv`. It is a whole month of Pocket's spending:

```text
date,category,amount
2026-03-01,rent,18000
2026-03-01,fun,600
2026-03-02,travel,150
2026-03-03,food,210.5
```

**CSV** means "comma-separated values": the first line names the columns, and every other line is one row, with a
comma between the values. Spreadsheets, banks and shops export data like this every day.

It looks like `line.split(",")` would be enough. It is not. A value can itself contain a comma, inside quotes:

```text
2026,"snacks, jelly",30
```

`split(",")` cuts that into `['2026', '"snacks', ' jelly"', '30']`: four pieces, quotes and all. Python's `csv`
module understands the quoting rules and gives `['2026', 'snacks, jelly', '30']`. Never split CSV by hand.

The best tool is `csv.DictReader`: it reads the header line and gives you every row as a **dictionary** (chapter
9), with the column names as keys:

```python
import csv
with open("expenses.csv", newline="") as f:
    for row in csv.DictReader(f):
        print(row["category"], row["amount"])
```

(`newline=""` lets the csv module handle line endings itself; always use it with csv.) Note that every value
arrives as **text**: `row["amount"]` is `"18000"`, not a number, so you convert it with `float(...)`.
:::

:::step{type=try title="How many expenses in a month?" file="14-files/expenses.csv" line="1"}
Count them:

```bash run
cd /workspace/14-files && python3 -c "import csv; rows = list(csv.DictReader(open('expenses.csv', newline=''))); print(len(rows)); print(rows[0])"
```

```text
44
{'date': '2026-03-01', 'category': 'rent', 'amount': '18000'}
```

44 rows, each a dictionary of text values. Now scroll through the file in the editor and look closely: real data is
never perfect. Find the row where the amount is **empty**, and the one where it says **abc**. Your next function
must survive both, exactly like `safe_sum` in chapter 13.
:::

:::step{type=task task=read_totals title="Your turn: totals from a real file"}
In `file_tools.py`, make `read_totals(path)` read a CSV file with the columns `date,category,amount` and give back
a dictionary of the total amount per category, each rounded to 2 decimals.

- Use `csv.DictReader`, so quoted values with commas work.
- Skip any row whose amount is missing or not a number (chapter 13 has the tool for that).
- With the month in `expenses.csv`: `read_totals("expenses.csv")["rent"]` is `18000.0`, and `["shopping"]` is
  `4095.0`. A file with only the header line gives `{}`.

```bash run
cd /workspace/14-files && python3 -c "from file_tools import read_totals; print(read_totals('expenses.csv'))"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `with` do for you?
:::
- [ ] It makes the file read faster
- [x] It closes the file when the block ends, even after an error
- [ ] It creates the file
:::explain
`with` guarantees the file is closed, which also makes sure everything written reaches the disk.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Reading a CSV with `csv.DictReader`, what type is `row["amount"]`?
:::
- [x] `str`
- [ ] `float`
- [ ] `int`
:::explain
Everything in a text file is text. Convert it yourself with `float(...)`, and handle the rows where that fails.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `f.write("rice")` followed by `f.write("bus")` put in the file?
:::
- [ ] Two lines: `rice` and `bus`
- [x] One line: `ricebus`
:::explain
`write` adds no new line of its own. Write `"rice\n"` and `"bus\n"` to get two lines.
:::
:::

:::step{type=deep-dive title="Go deeper: encodings, paths and JSON"}
**Encoding.** A text file is stored as bytes. To turn bytes back into characters, Python needs the file's
**encoding**, and the world's standard is UTF-8 (chapter 7's Go deeper). Professional code says it explicitly:
`open(path, encoding="utf-8")`, so the program works the same on every computer.

**Paths.** `"expenses.csv"` means "in the current folder". Python's `pathlib` module treats paths as objects:

```python
from pathlib import Path
p = Path("14-files") / "expenses.csv"
p.exists()          # True or False
p.read_text()       # the whole file as one string
```

**JSON.** For saving dictionaries and lists, CSV is clumsy. The `json` module writes them as text and reads them
back exactly: `json.dump(data, f)` and `json.load(f)`. Most web APIs speak JSON.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Open files with `with open(path, mode)`, knowing `"r"`, `"w"` (empties first) and `"a"` (adds).
- Write lines yourself with `"\n"`, and read a file line by line with `strip()`.
- Read CSV files properly with `csv.DictReader`, getting each row as a dictionary of text values.
- Survive messy real data by skipping rows that are not valid.

:::photo{src="/lesson-images/python/py-14-notes.webp" alt="Handwritten notes about files: with open, the r w and a modes, csv.DictReader, and with closes the file" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 15: classes, so you can design your own kinds of values.
:::
