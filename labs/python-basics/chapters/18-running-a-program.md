:::step{type=story title="How do real tools know what you want?"}
When you type `python3 hello.py`, how does `python3` know which file to run? When you type `ls -l`, how does `ls`
know you want the long list? You give them **arguments**: words after the program's name. Every tool developers
use all day (`git`, `pip`, `pytest`) works this way, and none of them asks "which file?" with `input()`.

Today Pocket becomes a real command-line tool. You will run it as `python3 summary.py expenses.csv --top 2`, it
will print your biggest spending categories, give a polite one-line message when something is wrong, and even
write its own help page.

:::mission
Finish `summary.py`, a command-line program that prints the top spending categories from a CSV file, and make it
behave like a professional tool when things go wrong.
:::
:::

:::step{type=concept title="sys.argv: the words after the program's name" file="18-running-a-program/args_demo.py" line="2-5"}
When a program starts, Python puts the words you typed into a list called `sys.argv` (**arg**ument **v**alues).
Open `args_demo.py`, then run it with some words after its name:

```bash run
cd /workspace/18-running-a-program && python3 args_demo.py expenses.csv --top 2
```

```text
program: args_demo.py
arguments: ['expenses.csv', '--top', '2']
```

`sys.argv[0]` is the program's own name, and the rest are the arguments, always as **strings**, even the `2`.
Try it with other words, or none at all.

You could pick the arguments out of that list yourself, but checking them properly gets messy fast: which ones are
required, what is a number, what happens when one is missing. Python has a standard module for exactly that job.
:::

:::step{type=example title="Worked example: argparse does the hard work"}
`argparse` (from the standard library, chapter 16) turns a description of your arguments into a full command-line
interface. Here is a small converter, `python3 convert.py 42.195 --unit miles`:

```python
import argparse

parser = argparse.ArgumentParser(description="Convert a distance")
parser.add_argument("km", type=float)
parser.add_argument("--unit", default="miles")
args = parser.parse_args()

print(args.km, args.unit)
```

1. `ArgumentParser(description=...)` creates the parser; the description appears in the help page.
2. `add_argument("km", type=float)` adds a **positional** argument: required, and converted to a float for you.
3. `add_argument("--unit", default="miles")` adds an **option**: it starts with `--`, it is optional, and it has a
   default.
4. `parse_args()` reads `sys.argv`, checks everything, and gives back `args`, with one attribute per argument:
   `args.km` and `args.unit`.

And you get three things for free. A missing argument gives a short usage message and stops the program. A
value of the wrong type is refused too: `--top two` stops with `error: argument --top: invalid int value: 'two'`
(we tried it on the finished program). And `--help` prints a help page, written by argparse from your
description.
:::

:::step{type=try title="A tool that writes its own help page" file="18-running-a-program/summary.py" line="1-9"}
Here is what the finished `summary.py` does (yours will, soon). Its help page, which nobody wrote by hand:

```text
usage: summary.py [-h] [--top TOP] path

The biggest spending categories

positional arguments:
  path

options:
  -h, --help  show this help message and exit
  --top TOP
```

The real work:

```text
$ python3 summary.py expenses.csv --top 2
rent: 18000.00
shopping: 4095.00
$ python3 summary.py expenses.csv
rent: 18000.00
shopping: 4095.00
fun: 3250.00
```

Without `--top`, it shows the top 3. (`$` here stands for the terminal's prompt: the line after it is what was
typed.) Open `summary.py` now: it already imports what it needs, including your chapter 14 `read_totals` (a
finished copy is in this folder as `file_tools.py`). Right now it only imports, so running it prints nothing.
:::

:::step{type=task task=summary_top title="Your turn: the top categories"}
In `summary.py`, write the program:

1. Read the arguments with `argparse`: a positional `path`, and an option `--top` (a whole number, 3 by default).
2. Get the totals with `read_totals(path)`.
3. Print the top categories, biggest first, one per line as `category: amount` with two decimals.

```bash run
cd /workspace/18-running-a-program && python3 summary.py expenses.csv --top 2
```

It must print exactly `rent: 18000.00` and `shopping: 4095.00`. Chapter 11 has the tool for "biggest first", and
`totals.items()` gives you the pairs to sort: each pair is a `(category, amount)` tuple, so the key is
`lambda pair: pair[1]`. Then a slice keeps the first `args.top` of them. Then press **Check**.

The usual slips: leaving out `type=int`, so `args.top` is the text `"2"`, and the slice fails with
`TypeError: slice indices must be integers or None or have an __index__ method` (we tried it); sorting the
categories by name instead of by amount; or printing `18000.0` without `:.2f`.

Try `--top 10` too: the last line is `: 350.00`, chapter 14's row with no category, still here. The capstone
deals with it.
:::

:::step{type=concept title="Exit codes, and errors that do not scare people"}
Every program, when it ends, hands back a number to whoever started it: its **exit code**. `0` means success;
anything else means something went wrong. You can see it in the terminal with `echo $?` right after a command.
Scripts and other tools rely on it: a test run that exits with 1 tells the build system to stop.

Now think about the person using Pocket. They mistype the file name. Should they see a 10-line traceback? No. A
professional tool:

- prints **one clear line** saying what is wrong, to the error channel (`print(..., file=sys.stderr)`), not to
  normal output;
- exits with a non-zero code, with `sys.exit(1)`.

```text
$ python3 summary.py missing.csv
File not found: missing.csv
$ echo $?
1
```

That is chapter 13's `try` / `except FileNotFoundError`, plus a friendly message and the right exit code.
(argparse already does this for missing arguments: it exits with code 2 and a usage line.)
:::

:::step{type=concept title="Quiet on import: the __main__ check"}
Remember chapter 16: `import` **runs** a module's file. So if `summary.py` does its work at the top level, then
`import summary` from another program (or from a test!) would start reading arguments and printing totals. That
is a nasty surprise.

The fix is one of the most recognisable lines in Python:

```python
def main():
    ...  # read the arguments, do the work

if __name__ == "__main__":
    main()
```

Python sets the variable `__name__` for every module. When you **run** a file (`python3 summary.py`), its
`__name__` is the special string `"__main__"`. When it is **imported**, `__name__` is the module's name,
`"summary"`. So that `if` means: "do the work only when I was run, not when I was imported". Put the program in a
`main()` function, and call it from under that line.
:::

:::step{type=task task=summary_errors title="Your turn: friendly errors, quiet imports"}
Make `summary.py` behave like a professional tool:

- For a file that does not exist, print `File not found: <path>` to `sys.stderr` and exit with code 1, with no
  traceback.
- `import summary` prints nothing at all: the work runs only under `if __name__ == "__main__":`.

```bash run
cd /workspace/18-running-a-program && python3 summary.py missing.csv; echo "exit code $?"; python3 -c "import summary"
```

The first line should say `File not found: missing.csv`, the exit code should be 1, and the import should print
nothing. Then press **Check**.

The usual slips: printing the message but forgetting `sys.exit(1)`, so the exit code is still 0 and other tools
think it worked; putting the `try` around the whole program, so the error message hides other bugs too (catch
only `FileNotFoundError`, around the `read_totals` call); or leaving the work at the top level, so the import
prints the usage message.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
For `python3 tool.py data.csv --top 5`, what is `sys.argv[2]`?
:::
- [ ] `"data.csv"`
- [x] `"--top"`
- [ ] `5`
:::explain
`sys.argv` is `["tool.py", "data.csv", "--top", "5"]`: index 2 is `"--top"`, and every item is a string.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What exit code means a program succeeded?
:::
- [x] `0`
- [ ] `1`
- [ ] `200`
:::explain
`0` means success. Any other number means something went wrong; tools often use 1 for general errors and 2 for
wrong usage.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
In `summary.py`, what is `__name__` when another file does `import summary`?
:::
- [ ] `"__main__"`
- [x] `"summary"`
:::explain
`__name__` is `"__main__"` only for the file you run directly. An imported module's `__name__` is its own name.
:::
:::

:::step{type=deep-dive title="Go deeper: stdin, pipes and making a real command"}
**Pipes.** Command-line tools are built to be chained. `python3 summary.py expenses.csv | head -1` sends Pocket's
output into another program that keeps only the first line. That is why error messages go to `stderr`: they still
reach your screen, but they do not pollute the data flowing through a pipe.

**Reading input.** `sys.stdin` lets a program read text piped into it, so tools can read files *or* the output of
other tools.

**A real command.** Packaging tools (with a `pyproject.toml`, chapter 16's Go deeper) can install your program as
a command, so people type `pocket expenses.csv` instead of `python3 summary.py expenses.csv`. That is exactly how
`pytest` and `pip` are installed.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read command-line arguments with `sys.argv`, and properly with `argparse` (positional arguments, options,
  defaults, types, and a free `--help`).
- Report errors like a professional tool: one line to `sys.stderr`, and `sys.exit(1)`.
- Explain exit codes, and check one with `echo $?`.
- Keep a module quiet on import with `if __name__ == "__main__":`.

:::photo{src="/lesson-images/python/py-18-sketch.webp" alt="Sketchnote: Running a program. Arguments are the words typed after the program's name; argparse reads them, checks them and writes --help. Flow: python3 summary.py expenses.csv --top 2, parse_args(), read_totals(path), sort and keep the top 2, two lines, rent and shopping. Remember: exit code 0 means success, any other number means trouble; errors go to sys.stderr, in one clear line; sys.exit(1) stops with a failure code; do the work in main(), called only when the file is run." ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 3. Pocket is a real program now. One chapter left: the capstone, where you put it all
together.
:::
