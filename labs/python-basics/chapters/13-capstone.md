:::step{type=story title="Putting it all together"}
This last chapter is a small real job, the kind you will meet at work: turn a month of messy
expense data into a report, and fix a bug in code somebody else wrote. Everything you need is in the
chapters before.

:::mission
Write `monthly_report(path)` in `report.py`, then find and fix the bugs in the inherited
`budget.py`.
:::
:::

:::step{type=concept title="A plan before code"}
For a task with several parts, write the steps down first:

1. Read the rows; keep a **line number** for each (the header is line 1).
2. Turn each row into a category and an amount; if that fails, note the line and skip it.
3. From the good rows, work out each number the report needs.
4. Return everything in one dictionary.

Small helper functions for each step (some you already wrote) keep the main function short and easy
to test.
:::

:::step{type=predict title="Guess first"}
:::question
Which of these rows should count as a **bad line** in the report?

```text
date,category,amount
2026-03-02,food,120
2026-03-03,,45
2026-03-03,travel,abc
2026-03-04,rent,18000
```
:::
- [ ] Only line 4 (`abc`)
- [x] Lines 3 and 4
- [ ] Lines 1, 3 and 4
- [ ] None: skip them silently
:::explain
Line 3 has no category and line 4 has no number, so neither can go in the report. The header (line 1)
is not data, so it is never a bad line. Reporting **which** lines were skipped lets someone fix the
file instead of wondering why the totals look low.
:::
:::

:::step{type=try title="Size up the data"}
```bash run
wc -l expenses.csv; cut -d, -f2 expenses.csv | sort | uniq -c | sort -rn
```

How many rows, which categories, and a hint of the messy ones (an empty category shows as a blank).
:::

:::step{type=task task=monthly_report title="The monthly report"}
In `report.py`, make `monthly_report(path)` read a CSV with the header `date,category,amount` and
return this dictionary:

| Key | Value |
|---|---|
| `"total"` | the sum of all good amounts, rounded to 2 decimals |
| `"count"` | how many good rows there were |
| `"average"` | `total / count` rounded to 2 decimals, or `0.0` when there are none |
| `"biggest"` | the single biggest expense as `{"category": ..., "amount": ...}`, or `None` |
| `"per_category"` | `{category: total}` with totals rounded to 2 decimals |
| `"bad_lines"` | line numbers of rows with no category or a missing or non-numeric amount; a blank line is skipped, not reported |

For the five lines in the "Guess first" step it returns a total of `18120.0`, a count of `2`, an
average of `9060.0`, the rent as the biggest, and `bad_lines` of `[3, 4]`.
:::

:::step{type=concept title="Reading code you did not write"}
At work you change code more often than you write it from scratch. A good routine:

1. **Read** the function and say in one sentence what it is supposed to do.
2. **Run** it on a small example, including an edge case (an empty input, a missing key).
3. Compare what it **does** with what it **should** do, and find the exact line where they part.
4. Fix that, and nothing else, then run the example again.

`budget.py` was written by a colleague who has left. Its tests are failing in production.
:::

:::step{type=task task=fix_budget title="Fix the inherited budget code"}
`over_budget(totals, budgets)` in `budget.py` should return the **sorted** list of categories whose
spending is **above** their budget. A category with a budget but no spending at all is simply not
over budget.

- `over_budget({"food": 500, "travel": 50}, {"food": 400, "travel": 100})` returns `["food"]`
- `over_budget({"food": 500}, {"food": 400, "fun": 100})` returns `["food"]` (no spending on fun)
- `over_budget({"b": 10, "a": 10}, {"b": 5, "a": 5})` returns `["a", "b"]`
- exactly on budget is not over: `over_budget({"food": 400}, {"food": 400})` returns `[]`

Run it first and find out how it fails. Keep the fix small.
:::

:::step{type=deep-dive title="What comes next"}
You can now write real Python: functions, every core data structure, errors, files and command-line
programs. The natural next steps:

- **Testing:** `pytest` lets you write checks like the hidden ones in this course, so every change
  you make is verified in seconds.
- **Classes and dataclasses:** bundle data with the functions that work on it (an `Expense` with a
  `category` and an `amount`).
- **The standard library:** `collections.Counter`, `datetime`, `json`, `pathlib` and `statistics`
  solve many everyday problems in one line.
- **Python in practice**, the next course on LabBox, covers all of these with a real project.
:::

:::step{type=recap title="Course complete"}
- Break a job into steps and small functions before you write the main one.
- Keep line numbers when reading files, and report what you skip.
- Read, run, compare, then fix the one line that is wrong.
- You have built Python from the first function to a real report: well done.
:::
