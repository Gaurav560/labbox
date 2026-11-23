:::step{type=story title="Who wrote print, and do you have to write everything yourself?"}
You never wrote `print`, `len`, `sorted` or `csv.DictReader`. Somebody else did, years ago, and you just used
them. That is the secret of how programmers build big things quickly: **they reuse code**. Their own code, split
into tidy files. Python's own huge collection of tools. And more than half a million free packages that other
people share online.

Pocket's code is growing too. Today you split it into files that import each other, use Python's built-in
**standard library**, and install a package from the internet into a safe, private space.

:::mission
Move Pocket's money helpers into a module of their own, `money.py`, and let the standard library work out the
median of your spending.
:::
:::

:::step{type=concept title="Every Python file is a module" file="16-modules/tracker.py" line="6-12"}
A **module** is simply a Python file. Any `.py` file can use the functions of another one with `import`. Say
`money.py` contains a function `format_price`. There are two ways to use it from `tracker.py`, in the same folder:

```python
import money
money.format_price(120)          # name the module, then the function

from money import format_price
format_price(120)                # bring the name in directly
```

The first keeps it obvious where each name comes from; the second is shorter. Both are everywhere in real code.
You have used the first style since chapter 14: `import csv`, then `csv.DictReader`.

Open `tracker.py`. Right now `format_price` is defined inside it. That works, but every other program that wants
to show money would have to copy it. Copies drift apart: someone fixes a bug in one copy and the others stay
broken. A module is the cure: one definition, imported wherever it is needed.

Run it to see what it prints today:

```bash run
cd /workspace/16-modules && python3 tracker.py
```

```text
₹120.00 = 12000 paise
₹45.50 = 4550 paise
₹1,250.00 = 125000 paise
```

After your task, the output must be exactly the same. Only *where* the code lives changes. Programmers call this
**refactoring**.
:::

:::step{type=concept title="How does Python find a module?"}
When Python meets `import money`, it goes looking. Press Play to follow the search:

:::diagram{name="import-search"}
Python checks the modules it already loaded, then your script's folder, then the standard library, then installed packages.
:::

So right now, in the chapter 16 folder:

```bash run
cd /workspace/16-modules && python3 -c "import money"
```

```text
ModuleNotFoundError: No module named 'money'
```

That is the last step of the search: no `money.py` anywhere. Once you create it next to `tracker.py`, step 2 finds
it.

One more thing worth knowing: `import` **runs the module's file**, from the top, the first time it is imported.
That is how the functions get defined. It also means any `print` at the top level of a module runs on import:
chapter 18 shows how to keep modules quiet.
:::

:::step{type=example title="Worked example: one module, two programs"}
Here is the shape of your task, with distances instead of money. A file `units.py`:

```python
def km_to_miles(km):
    return round(km * 0.621371, 2)
```

And two programs that both use it, `trip.py` and `run.py`:

```python
from units import km_to_miles
print(km_to_miles(42.195))    # a marathon: 26.22
```

1. The conversion is written **once**, in `units.py`.
2. Each program imports what it needs.
3. Fix or improve `km_to_miles`, and every program that imports it gets the fix.

Notice that `units.py` itself prints nothing: a module offers functions; the programs decide what to do with
them.
:::

:::step{type=task task=money_module title="Your turn: a money module"}
Give Pocket a module of its own for money:

1. Create a new file `money.py` in the `16-modules` folder (the **New file** button above the file list, or
   `touch money.py` in the terminal).
2. Move `format_price(amount)` into it, and add `to_paise(amount)`, which gives back the amount in whole paise
   as an `int`: `to_paise(45.5)` gives `4550`. (Rounding matters: `to_paise(0.1 + 0.2)` must give `30`.)
3. In `tracker.py`, delete its own `format_price` and import both functions from `money` instead, and use
   `to_paise` for the paise.

`python3 tracker.py` must print exactly the three lines above. Then press **Check**.
:::

:::step{type=concept title="The standard library: batteries included"}
Python ships with hundreds of modules ready to import, no installing needed. People call this "batteries
included". A few you will use again and again:

| Module | Gives you | Example | Answer |
|---|---|---|---|
| `statistics` | averages and spread | `statistics.median([120, 45, 900])` | `120` |
| `math` | maths functions | `math.sqrt(16)` | `4.0` |
| `datetime` | dates and times | `date(2026, 11, 22).strftime("%A")` | `'Sunday'` |
| `random` | random choices | `random.choice(["jelly", "cookie"])` | either one |
| `csv`, `json` | data files | chapter 14 | |
| `pathlib` | file paths | chapter 14 | |

The **median** is the middle value once the numbers are sorted. With an even count, it is the average of the two
middle ones: the median of `[1, 2, 3, 4]` is `2.5`. Money apps like it because one huge expense (rent, say) does
not drag it around the way it drags the average.

Before writing a tool yourself, it is always worth asking: "is this already in the standard library?" Very often,
it is.
:::

:::step{type=task task=median_spend title="Your turn: the median spend"}
Open `stats_tools.py` and make `median_spend(amounts)` give back the median of the amounts, using the `statistics`
module, or `None` for an empty list (the statistics module raises an error for an empty list).

`median_spend([120, 45, 900])` gives `120`, `median_spend([1, 2, 3, 4])` gives `2.5`, and `median_spend([])` gives
`None`.

```bash run
cd /workspace/16-modules && python3 -c "from stats_tools import median_spend; print(median_spend([120, 45, 900]), median_spend([1, 2, 3, 4]), median_spend([]))"
```

Then press **Check**.
:::

:::step{type=concept title="Packages from the internet, in a private space"}
Beyond the standard library is **PyPI**, the Python Package Index: a free online library of more than half a
million packages that people share. `requests` for talking to websites, `pandas` for data tables, `django` for
web apps. You install them with **pip**, Python's package installer.

But installing everything into one shared Python soon goes wrong: project A needs version 1 of a package, project
B needs version 2. The answer is a **virtual environment**: a private folder with its own Python and its own
packages, one per project.

```bash run
cd /tmp && python3 -m venv .venv && . .venv/bin/activate && which python
```

```text
/tmp/.venv/bin/python
```

1. `python3 -m venv .venv` creates the environment in a folder called `.venv`.
2. `. .venv/bin/activate` switches your terminal into it: `python` and `pip` now mean the private ones.
3. `pip install requests` installs a package into this environment only.
4. `deactivate` switches back.

Here is the proof that it really is private. After installing `requests` inside the environment and running
`deactivate`, the normal Python cannot see it:

```text
ModuleNotFoundError: No module named 'requests'
```

Try it yourself in the terminal: your lab machine is connected to the internet, so `pip install requests` works.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
After `from money import format_price`, how do you call it?
:::
- [x] `format_price(120)`
- [ ] `money.format_price(120)`
- [ ] `import format_price(120)`
:::explain
`from ... import ...` brings the name itself in, so you use it directly. With `import money` you would write
`money.format_price(120)`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is the median of `[3, 1, 100]`?
:::
- [x] `3`
- [ ] `34.67`
- [ ] `1`
:::explain
Sorted, the numbers are 1, 3, 100: the middle one is 3. The average would be 34.67, pulled up by the 100.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why use a virtual environment for each project?
:::
- [ ] It makes Python faster
- [x] Each project gets its own packages and versions, without clashing with others
- [ ] pip only works inside one
:::explain
A virtual environment keeps a project's packages separate, so two projects can need different versions of the
same package.
:::
:::

:::step{type=deep-dive title="Go deeper: packages, requirements and the empty folder trick"}
**Packages.** A folder of modules is a **package**. Put `money.py` and `dates.py` inside a folder `pocket/`, add
a file `__init__.py` (it can be empty), and you can write `from pocket.money import format_price`. Big projects
are trees of packages.

**Recording what you installed.** `pip freeze > requirements.txt` writes every installed package and its exact
version to a file. Anyone can recreate your environment with `pip install -r requirements.txt`. Every serious
Python project has a file like this (or a `pyproject.toml`, the newer standard).

**Never commit `.venv`.** The environment folder is big and specific to one computer. You share the
requirements file instead, and everyone builds their own environment from it.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Split a program into modules and use them with `import module` or `from module import name`.
- Explain how Python searches for a module, and what `ModuleNotFoundError` means.
- Reach for the standard library first: `statistics`, `math`, `datetime`, `random`, `csv`, `json`, `pathlib`.
- Create a virtual environment, install packages into it with pip, and know why each project gets its own.

:::photo{src="/lesson-images/python/py-16-notes.webp" alt="Handwritten notes about modules: import statistics, from money import format_price, python3 -m venv .venv, pip install requests" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 17: testing, so you can prove your code works, and keep it working.
:::
