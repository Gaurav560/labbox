:::step{type=story title="Why real programs"}
Functions are building blocks. A **program** is something a person runs: they type a command,
give it a file and a few options, and get an answer, or a clear message when they made a mistake.
This chapter turns your file tools into a command-line program.

:::mission
Write `summary.py`: `python summary.py expenses.csv --top 3` prints the three biggest spending
categories, a missing file gets a friendly message, and importing the file runs nothing.
:::
:::

:::step{type=concept title="Modules and import"}
Every `.py` file is a **module**. Another file can use what it defines:

```python
from file_tools import read_totals     # your chapter 11 function
import math                            # a module from the standard library

totals = read_totals("expenses.csv")
math.sqrt(16)                          # 4.0
```

Python looks for modules in the folder of the program you run, then in the standard library and
installed packages. Thousands more come from the internet with `pip install`.
:::

:::step{type=predict title="Guess first"}
:::question
`tools.py` contains:

```python
def double(x):
    return x * 2

print("hello from tools")
```

Another file runs `from tools import double`. What happens?
:::
- [ ] Nothing is printed: only `double` is imported
- [x] `hello from tools` is printed, then `double` can be used
- [ ] An error: you cannot import a file that prints
- [ ] `double` runs once
:::explain
Importing a module **runs the whole file** once, top to bottom. Definitions are made, and any loose
code, like that `print`, runs too. That is why programs put their "do the work" code behind
`if __name__ == "__main__":`, which is true only when the file is run directly.
:::
:::

:::step{type=try title="See __name__ for yourself"}
```bash run
echo 'print("my name is", __name__)' > whoami.py
python3 whoami.py
python3 -c "import whoami"
rm whoami.py
```

Run directly, the file's `__name__` is `"__main__"`. Imported, it is the module's name.
:::

:::step{type=concept title="Command-line arguments"}
`sys.argv` is the list of words typed after `python`. The `argparse` module turns them into named
options, with `--help` for free:

```python
import argparse

parser = argparse.ArgumentParser(description="Sum up expenses")
parser.add_argument("path")                          # required
parser.add_argument("--top", type=int, default=3)    # optional, a number
args = parser.parse_args()
print(args.path, args.top)
```

A program reports problems on **stderr** (`print(..., file=sys.stderr)`) and ends with an **exit
code**: `0` means success, anything else means failure, and scripts check it.
:::

:::step{type=task task=summary_top title="Print the top categories"}
In `summary.py`, make the program read a CSV (with `read_totals` from chapter 11) and print the
biggest categories, biggest first, one per line as `category: amount` with two decimals. `--top N`
says how many; the default is 3.

```text
$ python summary.py expenses.csv --top 2
rent: 18000.00
shopping: 4095.00
```

Try it on `expenses.csv` once `read_totals` works.
:::

:::step{type=task task=summary_errors title="Friendly errors, quiet on import"}
Make `summary.py` behave like a good program:

- `python summary.py missing.csv` prints `File not found: missing.csv` to **stderr**, prints no
  traceback, and exits with code `1`
- `import summary` (from Python or another file) prints **nothing**

:::why
A traceback is for the programmer; a person running your tool needs one clear sentence. Scripts that
call your program rely on the exit code to know whether it worked.
:::
:::

:::step{type=deep-dive title="Packages, pip and virtual environments"}
A **package** is a folder of modules. `pip install requests` downloads one from PyPI, the public
package index with hundreds of thousands of them.

Different projects need different versions of the same package, so each project gets its own
**virtual environment**: `python3 -m venv .venv` makes a private folder of packages, and
`.venv/bin/pip install ...` installs into it without touching anything else. A `requirements.txt`
lists exact versions so another machine can build the same environment.

Tools that are meant to be run like `summary` instead of `python summary.py` declare an entry point in
`pyproject.toml`; that is how commands such as `pytest` and `black` get installed.
:::

:::step{type=recap}
- Every `.py` file is a module; `import` runs it once and gives you its names.
- `if __name__ == "__main__":` keeps "run the program" code from running on import.
- `argparse` reads arguments and options and gives `--help` for free.
- Errors for people go to `sys.stderr`; `sys.exit(1)` reports failure to the caller.
:::
