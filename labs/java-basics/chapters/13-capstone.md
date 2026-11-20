:::step{type=story title="Putting it all together"}
This last chapter is a small real job, the kind you will meet at work: fix a bug in a class somebody
else wrote, then turn a month of messy expense data into a report. Everything you need is in the
chapters before.

:::mission
First fix the inherited `capstone/Book.java` (a warm-up), then write `Report.monthly(path)` in
`capstone/Report.java`.
:::
:::

:::step{type=concept title="Reading code you did not write"}
At work you change code far more often than you write it from scratch. A calm routine helps:

1. **Read** it and say in one sentence what it is supposed to do.
2. **Run** it on a tiny example, including an edge case.
3. Compare what it **does** with what it **should** do, and find the exact line where they part.
4. Fix that line, and nothing else, then run the example again.
:::

:::step{type=concept title="How a HashSet finds things"}
Picture a library with numbered shelves. To find a book fast, the librarian first computes **which
shelf** it belongs on, then looks only on that shelf.

A `HashSet` (and a `HashMap`) works the same way: it first asks the object for its `hashCode()` (the
shelf number), then uses `equals` to compare only with the items on that shelf. So the rule is simple:
**objects that are equal must have the same hash code**. If two equal books report different shelf
numbers, the set looks on the wrong shelf and never finds the twin.

:::picture{name="library-shelves"}
First the shelf (hashCode), then the book (equals).
:::
:::

:::step{type=task task=fix_book title="Warm-up: fix the inherited Book class"}
`Book` in `capstone/Book.java` says two books are equal when their ISBNs match. Yet putting two copies of
the same book into a `HashSet` gives a set of **two**, and a `HashMap` cannot find a book by an equal key.

Find what is missing and add it. Keep the fix small: it is one method.
:::

:::step{type=concept title="A plan before code"}
For a task with several parts, write the steps down first:

1. Read the lines; the header is line 1, so data starts at line 2.
2. For each line: skip it if blank; split it; if the category is empty or the amount is not a number,
   note the line number and skip it.
3. From the good rows, add up the total, count them, and total per category.
4. Return everything in one `MonthlyReport` record.
:::

:::step{type=example title="Worked example: rows with their line numbers"}
Knowing **which line** a row came from is the one new trick:

```java
List<String> lines = Files.readAllLines(path);
for (int i = 1; i < lines.size(); i++) {
    int lineNumber = i + 1;          // list index 1 is line 2
    String line = lines.get(i);
    if (line.isBlank()) {
        continue;                    // blank: skip, do not report
    }
    System.out.println(lineNumber + ": " + line);
}
```

`readAllLines` keeps blank lines in the list, so `i + 1` always matches what someone sees in an editor,
even after a blank line.
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
data, so it is never a bad line. Reporting **which** lines were skipped lets someone fix the file
instead of wondering why the totals look low.
:::
:::

:::step{type=try title="Size up the data"}
```bash run
wc -l expenses.csv; cut -d, -f2 expenses.csv | sort | uniq -c | sort -rn
```

How many lines, which categories, and a hint of the messy ones (an empty category shows as a blank).
:::

:::step{type=task task=monthly_report title="The monthly report"}
In `capstone/Report.java`, make `monthly(path)` return a `MonthlyReport` with:

| Field | Value |
|---|---|
| `total` | the sum of the good amounts, rounded to 2 decimals |
| `count` | how many good rows |
| `average` | total divided by count, rounded to 2 decimals, or `0` when there are none |
| `perCategory` | total per category, rounded to 2 decimals |
| `badLines` | line numbers of rows with an empty category or a bad amount; blank lines are skipped, not reported |

For the five lines in "Guess first" it gives a total of `18120.0`, a count of `2`, an average of
`9060.0` and bad lines `[3, 4]`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two objects are `equals`. What must be true of their `hashCode()`?
:::
- [ ] Nothing
- [x] They must be the same
- [ ] They must be different
- [ ] They must both be zero
:::explain
Equal objects must report the same hash code, or hash-based collections look on the wrong "shelf".
Records, and IDEs that generate both methods together, get this right for you.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the safest first step when fixing someone else's class?
:::
- [ ] Rewrite it from scratch
- [x] Run it on a tiny example and see exactly how it fails
- [ ] Delete the parts you do not understand
- [ ] Add more comments
:::explain
Seeing the exact failure points you to the one line to change, and keeps the fix small and safe.
:::
:::

:::step{type=deep-dive title="What comes next"}
You can now write real Java: types, decisions, loops, strings, arrays, classes, interfaces,
collections, exceptions, streams, files and command-line programs. The natural next steps:

- **Testing with JUnit**: write checks like the hidden ones in this course, so every change is verified
  in seconds.
- **Build tools**: Maven or Gradle compile, test and package real projects.
- **Spring Boot**: Java's most popular framework for web back ends, where everything you learned here
  is used every day.
- **Java in practice**, the next course on LabBox, takes these ideas further with a real project.
:::

:::step{type=recap title="Course complete"}
- Read, run, compare, then fix the one line that is wrong.
- Equal objects must have equal hash codes.
- Plan a multi-part task in steps before writing it.
- You have built Java from the first method to a real report: well done.
:::
