:::step{type=story title="Can you turn a messy month into one clear answer?"}
Mixtape is a small company now, and small companies spend money: rent, food, travel, subscriptions. Every purchase
ends up as a line in `expenses.csv`. At the end of each month, someone has to answer simple questions: how much did we
spend, on what, and which lines in the file are broken?

The developer who started the report left before finishing it. You have the file, a half-written `report.js`, and
everything from the last seventeen chapters: files, loops, objects, array methods, errors and a plan. This is the
kind of job a junior developer is given in their first week.

:::mission
Write `readTotals`, the spending per category, then `monthlyReport`: the total, count, average, the spending per
category and the line numbers of every broken row.
:::
:::

:::step{type=try title="Size up the data first"}
Before writing code against a file, look at it. Two classic terminal tools help:

```bash run
cd /workspace/18-capstone && wc -l expenses.csv && cut -d, -f2 expenses.csv | sort | uniq -c | sort -rn
```

```text
46 expenses.csv
     18 food
     10 travel
      7 fun
      5 shopping
      2 bills
      2 
      1 rent
      1 category
```

46 lines. `cut -d, -f2` takes the second column, the category, and `uniq -c` counts each one. The two blank
categories are one blank line and one row with no category; `category` is the header. Your report should find 41 good
rows.
:::

:::step{type=concept title="A plan before code"}
This is the biggest function in the course, and that is exactly when to stop and plan, in plain words, before any
code:

1. Read every line of the file (chapter 16), keeping each line's **number**.
2. Skip the header and blank lines. Split each other line into date, category and amount.
3. A row is **bad** when its category is empty or its amount is not a number (chapter 13). Note its line number.
4. From the good rows: the total (chapter 11's `reduce`), the count, the average (0 when there are none), and the
   total per category (chapter 10's counting pattern). Round money to two decimals.

Every step is a chapter you have done. The only new trick is the line numbers.

:::picture{name="funnel" concept="A plan before code"}
Three amounts enter the fold and one running total comes out.
:::
:::

:::step{type=example title="Worked example: rows with their line numbers"}
```js
const lines = fs.readFileSync("expenses.csv", "utf8").split("\n");
lines.forEach((line, i) => {
  if (i === 0 || line.trim() === "") {
    return;
  }
  console.log(i + 1, line);
});
```

`forEach` gives each line **with its index**. The index counts blank lines too, so `i + 1` always matches the line
number someone sees in an editor, even after a blank line. (`return` inside `forEach` skips to the next line, like
`continue` in a loop.)

:::trace{title="four lines of a file"}
| i | line | prints | note |
|---|---|---|---|
| 0 | date,category,amount | (nothing) | The header is line 1, not data. |
| 1 | 2026-03-02,food,120 | 2 2026-03-02,food,120 | Index 1 is line 2. |
| 2 | (blank) | (nothing) | Blank: skipped, but it still uses a number. |
| 3 | 2026-03-03,,45 | 4 2026-03-03,,45 | So this row is line 4, as an editor shows it. |
:::
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
:::explain
Line 3 has no category and line 4 has no number, so neither can go in the report. The header is not data, so it is
never a bad line. Reporting **which** lines were skipped lets someone fix the file instead of wondering why the totals
look low.
:::
:::

:::step{type=task task=read_totals title="Your turn: spending per category"}
Open `report.js` and make `readTotals(path)` give back an object of each category to its total, rounded to two
decimals. Skip the header, blank lines, rows with no category, and amounts that are not numbers.

On `expenses.csv`, `readTotals("expenses.csv").rent` is `18000`. Then press **Check**.
:::

:::step{type=task task=monthly_report title="Your turn: the monthly report"}
In `report.js`, make `monthlyReport(path)` give back:

| Property | Value |
|---|---|
| `total` | the sum of the good amounts, rounded to 2 decimals |
| `count` | how many good rows |
| `average` | total divided by count, rounded to 2 decimals, or `0` when there are none |
| `perCategory` | the total per category, rounded to 2 decimals |
| `badLines` | the line numbers of rows with an empty category or a bad amount; blank lines are skipped, not reported |

For the five lines in "Guess first", it gives a total of `18120`, a count of `2`, an average of `9060` and bad lines
`[3, 4]`. On the real file:

```bash run
cd /workspace/18-capstone && node report.js
```

```text
total 30086, 41 rows, average 733.8
rent 18000, food 2262.5
bad lines [16,24,32]
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`lines.forEach((line, i) => ...)`: a blank line sits at index 2. What line number is the row at index 3?
:::
- [ ] 3
- [x] 4
- [ ] 2
:::explain
The line number is always the index plus 1, and blank lines still take a place in the list.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
There are no good rows at all. What should the average be?
:::
- [ ] `NaN`
- [x] `0`
- [ ] It should throw
:::explain
`0 / 0` is `NaN`, which would spoil anything it touches (chapter 13). Check for an empty list first.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is the safest first step with a file you have never seen?
:::
- [ ] Write the whole report, then run it
- [x] Look at it: count the lines and the kinds of values
- [ ] Delete the broken lines by hand
:::explain
A minute with `wc` and `uniq -c` shows the shape and the mess, so the code handles both from the start.
:::
:::

:::step{type=deep-dive title="Go deeper: where JavaScript goes from here"}
You now know the JavaScript that real code is made of. The natural next steps:

- **Servers.** LabBox's **Express** course builds a real web API with Node: routes, JSON, errors and tests, all
  things you have met here.
- **The browser.** The DOM lets JavaScript change a web page: `document.querySelector("button").addEventListener(...)`.
  Frameworks like React build on exactly the functions, objects and arrays you know.
- **TypeScript.** JavaScript with types checked before it runs, catching chapter 2's `NaN min` before it ever happens.
  Most large JavaScript projects use it today.

And it all started with ten days of work at Netscape in 1995.
:::

:::step{type=recap title="Course complete"}
You can now:

- Size up a data file before coding, and plan a big function in plain words first.
- Keep line numbers while reading a file, and report broken rows instead of hiding them.
- Combine files, loops, objects, array methods and error handling into one real program.
- Write JavaScript from your first `console.log` to modules, async code, command-line tools and tests.

:::photo{src="/lesson-images/javascript/js-18-notes.webp" alt="Handwritten notes for the JavaScript capstone: look at the data first, a plan in words, line number is index plus 1, blank lines still count, report the bad lines, average 0 when there are no rows, course complete" ai="true"}
One page of notes for this chapter.
:::

That is JavaScript from zero, all eighteen chapters. Mixtape started as two `console.log` lines; it ends as a tested
command-line program that reads real files. Well done.
:::
