:::step{type=story title="Can you build a real report from a messy month?"}
Nineteen chapters ago, Pocket said its first words. Since then it has learned to count, decide, loop, clean text,
remember things in files, survive bad data and run from the command line. Now it gets its final job, the one every
money app is really for: **the monthly report**. How much did you spend? On what? What was the biggest thing? And
which lines of the file were too broken to trust?

This chapter works like a real job. First you fix code a colleague left behind. Then you build a feature from a
written **contract**, with no step-by-step instructions, using everything you know.

:::mission
Fix the inherited `over_budget`, then write `monthly_report`, which turns a real, messy CSV file into a complete
report.
:::
:::

:::step{type=try title="Code someone else left behind" file="19-capstone/budget.py" line="1-11"}
Open `budget.py`. A colleague wrote `over_budget` before leaving the team. It should give back the **sorted** list
of categories whose spending is **above** their budget. The tests in production are failing. Try it:

```bash run
cd /workspace/19-capstone && python3 -c "from budget import over_budget; print(over_budget({'food': 500}, {'food': 400, 'travel': 100}))"
```

```text
  File "/workspace/19-capstone/budget.py", line 9, in over_budget
    if totals[category] >= budgets[category]:
       ~~~~~~^^^^^^^^^^
KeyError: 'travel'
```

A crash: there is a budget for travel, but no travel spending yet. And when every category does have spending:

```bash run
cd /workspace/19-capstone && python3 -c "from budget import over_budget; print(over_budget({'food': 500, 'travel': 50}, {'food': 400, 'travel': 100}))"
```

```text
None
```

`None` instead of `['food']`. Reading code you did not write, finding *all* its bugs (not just the first one),
and fixing them without breaking what works: that is a big part of a developer's real job. You have every tool:
tracebacks (chapter 6), dictionaries and `get` (chapter 9), boundaries (chapters 4 and 17), and `sort` versus
`sorted` (chapter 8).
:::

:::step{type=task task=fix_budget title="Your turn: fix the inherited code"}
Fix `over_budget(totals, budgets)` in `budget.py`. There are **three** bugs. When it is right:

- `over_budget({"food": 500, "travel": 50}, {"food": 400, "travel": 100})` gives `["food"]`.
- A category with a budget but no spending is simply not over: no crash.
- Spending **exactly** the budget is not over: `over_budget({"food": 400}, {"food": 400})` gives `[]`.
- The result is always a sorted list.

Then press **Check**. If it fails, the message names the bug that is still there.
:::

:::step{type=concept title="The contract for monthly_report"}
Real features start with a description of what they must do: a **contract**. Here is Pocket's. `monthly_report(path)`
reads a CSV file with the columns `date,category,amount` and gives back a dictionary with exactly these keys:

| Key | Holds | For the five-line file below |
|---|---|---|
| `total` | the sum of the good amounts, rounded to 2 | `18120.0` |
| `count` | how many good rows | `2` |
| `average` | total / count, rounded to 2; `0.0` if there are none | `9060.0` |
| `biggest` | `{"category": ..., "amount": ...}` of the largest, or `None` | `{"category": "rent", "amount": 18000.0}` |
| `per_category` | `{category: total}`, each rounded to 2 | `{"food": 120.0, "rent": 18000.0}` |
| `bad_lines` | the **file line numbers** of rows skipped | `[3, 4]` |

A row is **bad** when its category is empty, or its amount is missing or not a number. Bad rows are skipped and
their line numbers remembered, so a person can go and fix the file. Line numbers count the header as line 1, and
blank lines count too, exactly like the line numbers in your editor.

The five-line file:

```text
date,category,amount
2026-03-02,food,120
2026-03-03,,45
2026-03-03,travel,abc
2026-03-04,rent,18000
```
:::

:::step{type=predict title="Guess first"}
:::question
In that five-line file, which lines are bad?
:::
- [ ] `[2, 3]`
- [x] `[3, 4]`
- [ ] `[3]`
:::explain
Line 1 is the header. Line 3 has an empty category; line 4 has the amount `abc`. Lines 2 and 5 are good: food 120
and rent 18000, so the total is 18120.0 from 2 rows.
:::
:::

:::step{type=example title="Worked example: plan before you type"}
A feature this size is easier when you plan it in plain words first, then turn each line into code. Here is the
plan, every step something you have done before:

1. Open the file with `with open(path, newline="")` and `csv.DictReader` (chapter 14).
2. For each row, find its real line number: `reader.line_num` is the line the reader just finished, blank lines
   included (save the reader in a variable to use it).
3. Clean the values: the category stripped of spaces (chapter 7), the amount through `float` inside a `try`
   (chapter 13).
4. Bad row? Remember its line number and `continue` to the next row (chapter 5's loops).
5. Good row? Keep `(category, amount)` in a list.
6. After the loop: the total with `sum`, the count with `len`, the biggest with `max` and a `key` (chapter 11),
   the per-category totals with the counting pattern (chapter 9), and rounding (chapter 3).
7. Return the dictionary, with an empty file giving zeros, `None` and empty collections (chapter 10's empty
   cases).

Split it into small helper functions if that helps you think (chapter 2's advice): one to read the good rows, one
to summarise them. The check only calls `monthly_report`.
:::

:::step{type=task task=monthly_report title="Your turn: the monthly report"}
Write `monthly_report(path)` in `report.py`, following the contract above exactly.

Try it on the five-line file first (create it in the editor as `five.csv`, or let the check do it), then on a real
month:

```bash run
cd /workspace/19-capstone && python3 -c "from report import monthly_report; r = monthly_report('expenses.csv'); print(r['count'], r['total'], r['average'], r['bad_lines'])"
```

For `expenses.csv` it should print `41 30086.0 733.8 [16, 24, 32]`. The check also tries a file with a blank line
in the middle (line numbers must still match the file) and a file with only the header.

Then press **Check**. When both tasks pass, you have finished Python from zero.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why remember the line numbers of bad rows instead of just skipping them?
:::
- [ ] Python needs them
- [x] So a person can find and fix those rows in the file
- [ ] To make the total correct
:::explain
Skipping keeps the report working; reporting the line numbers lets someone repair the data. Silently dropping data
is how real reports end up quietly wrong.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What should the average be for a file with only the header line?
:::
- [ ] An error
- [x] `0.0`
- [ ] `None`
:::explain
The contract says `0.0` when there are no good rows: dividing by a count of zero would crash (chapter 6), so the
empty case is checked first.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`over_budget` returned `None` instead of a list. Which chapter explained that bug?
:::
- [ ] Chapter 9, dictionaries
- [x] Chapter 8: `.sort()` sorts in place and gives back `None`
- [ ] Chapter 13, exceptions
:::explain
`return result.sort()` returns what `.sort()` gives back, which is `None`. `return sorted(result)` returns the
sorted list.
:::
:::

:::step{type=deep-dive title="Go deeper: where to go from here"}
You can now write real Python programs: read data, clean it, analyse it, test it and run it as a tool. Here is
where people go next:

- **Python in practice** (the next course on LabBox) takes Pocket's skills to bigger, real-world programs.
- **Data:** `pandas` turns this whole chapter into a few lines (`pd.read_csv("expenses.csv").groupby("category")`)
  and `matplotlib` draws charts of it. Everything you learned about lists, dictionaries and files is what those
  libraries are built on.
- **Web:** the FastAPI course on LabBox turns functions like yours into a web API other programs can call.
- **Automation:** small scripts that rename files, fill spreadsheets or check websites: the everyday superpower
  that makes Python so loved.

The most important habit is the one you have practised for nineteen chapters: make something small work, check it,
then make it a little better.
:::

:::step{type=recap title="What you can do now"}
You have finished **Python from zero**. You can now:

- Write programs from the very first line, run them, and read every error from the bottom up.
- Work with numbers, text, lists, dictionaries, tuples and sets, and reshape data with sorting and comprehensions.
- Handle real-world mess: exceptions, files, CSV data, and bad rows reported instead of crashing.
- Organise code into functions, classes and modules; prove it works with tests; and ship it as a command-line tool.

:::photo{src="/lesson-images/python/py-19-notes.webp" alt="Handwritten notes: Pocket is done! read, clean, count, report; test the edges; read errors bottom up; keep functions small" ai="true"}
The last page of your notebook.
:::

Well done. Pocket is yours.
:::
