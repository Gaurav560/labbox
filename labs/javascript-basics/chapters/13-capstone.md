:::step{type=story title="Putting it all together"}
This last chapter is a small real job: turn a month of messy expense data into a report. You will read
a real file, clean it, and work out the numbers, using what you learned in every chapter before.

:::mission
In `capstone/report.js`, first read the totals per category (a warm-up), then build the full monthly
report.
:::
:::

:::step{type=concept title="Reading a file"}
Node's `fs` module reads files. `readFileSync` gives the whole file as one string:

```javascript
const fs = require("node:fs");

const text = fs.readFileSync("expenses.csv", "utf8");
const lines = text.split("\n");
lines[0]        // "date,category,amount": the header
```

`"utf8"` says the file is text. Split on `"\n"` (the new-line character) to get the lines. A file that
does not exist throws an error with the code `"ENOENT"` ("no such file").
:::

:::step{type=concept title="CSV: one row per line"}
A **CSV** file stores a table as text: one row per line, the columns separated by commas.

```javascript
const [date, category, amountText] = "2026-03-02,food,120".split(",");
category              // "food"
Number(amountText)    // 120
```

The square brackets on the left **unpack** the array into three names at once.

:::picture{name="file-lines"}
Each line of a CSV file is one row, cut at the commas.
:::
:::

:::step{type=example title="Worked example: rows with their line numbers"}
Knowing **which line** a row came from is the one new trick:

```javascript
const lines = fs.readFileSync("expenses.csv", "utf8").split("\n");
lines.forEach((line, i) => {
  if (i === 0 || line.trim() === "") {
    return;                          // the header, or blank: skip
  }
  console.log(i + 1, line);          // index 1 is line 2
});
```

`forEach` gives each line with its index. The index counts blank lines too, so `i + 1` always matches
the line number someone sees in an editor.
:::

:::step{type=predict title="Guess first"}
:::question
Which of these rows are **bad lines** for the report?

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
Line 3 has no category and line 4 has no number, so neither can go in the report. The header is not
data, so it is never a bad line. Reporting **which** lines were skipped lets someone fix the file.
:::
:::

:::step{type=try title="Size up the data"}
```bash run
wc -l expenses.csv; cut -d, -f2 expenses.csv | sort | uniq -c | sort -rn
```

How many lines, which categories, and a hint of the messy ones (an empty category shows as a blank).
:::

:::step{type=task task=read_totals title="Warm-up: totals from a CSV"}
Make `readTotals(path)` return the total per category, **rounded to 2 decimals**. Skip the header,
blank lines, rows without a category, and amounts that are missing or not numbers.

- `readTotals("expenses.csv").rent` is `18000`, and `.shopping` is `4095`
:::

:::step{type=concept title="reduce, and a plan before code"}
`reduce` folds an array into one value, like a running total in one line:

```javascript
[120, 80, 45].reduce((sum, x) => sum + x, 0)   // 245
```

For the report, write the plan down first:

1. Read the rows once, each with its line number.
2. Split them into good rows and bad rows (blank lines are neither).
3. From the good rows: the total, the count, the average, the total per category.
4. From the bad rows: their line numbers.
:::

:::step{type=task task=monthly_report title="The monthly report"}
Make `monthlyReport(path)` return an object with:

| Key | Value |
|---|---|
| `total` | the sum of the good amounts, rounded to 2 decimals |
| `count` | how many good rows |
| `average` | total divided by count, rounded to 2 decimals, or `0` when there are none |
| `perCategory` | total per category, rounded to 2 decimals |
| `badLines` | line numbers of rows with no category or a bad amount; blank lines are skipped, not reported |

For the five lines in "Guess first" it gives a total of `18120`, a count of `2`, an average of `9060`
and bad lines `[3, 4]`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A file has a header, a blank line, then a bad row. Which line number is the bad row?
:::
- [ ] `1`
- [ ] `2`
- [x] `3`
- [ ] `4`
:::explain
The header is line 1 and the blank line is line 2, so the bad row is line 3. Its index is 2, plus one.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `[].reduce((sum, x) => sum + x, 0)` give?
:::
- [x] `0`
- [ ] `undefined`
- [ ] `NaN`
- [ ] An error
:::explain
The starting value `0` is returned when there is nothing to fold. Without it, `reduce` on an empty
array throws an error, so always give the start.
:::
:::

:::step{type=deep-dive title="What comes next"}
You can now write real JavaScript: values and types, decisions, loops, strings, arrays, objects, sets,
array methods, errors, classes, promises and files. The natural next steps:

- **JavaScript inside out**, the next course on LabBox: the equality traps, closures and promises
  behind every Node app, told as a story.
- **The browser**: the DOM, events and `fetch`, to make pages that react.
- **Express**: web servers and APIs in Node, the LabBox course on building a real API.
- **TypeScript**: JavaScript with types checked before the code runs, used by most large teams.
:::

:::step{type=recap title="Course complete"}
- `fs.readFileSync(path, "utf8")` reads a file; `split("\n")` gives the lines.
- Keep line numbers (index + 1), and report the rows you skip.
- Plan a multi-part task in steps; `reduce` folds an array into one value.
- You have built JavaScript from the first function to a real report: well done.
:::
