:::step{type=story title="Your first day on someone else's code"}
Here is what a first week as a Java developer really looks like. You will not start with an empty file. You will
open a project somebody else wrote, somebody who has since left, and you will be asked to fix one bug and build
one feature, without breaking anything else.

That is this chapter. Shelf's previous developer left two things behind: a `Book` class with a bug that makes the
same book appear twice, and a half-finished monthly report for the library's spending. Everything you need is in
the seventeen chapters behind you.

:::mission
Fix the inherited `Book` class, then write `Report.monthly`, which turns a month of messy spending data into one
clear report.
:::
:::

:::step{type=try title="The book that appears twice" file="18-capstone/Book.java" line="26-35"}
Open `Book.java` and run its `main`:

```java
Book a = new Book("978-0261102217", "The Hobbit");
Book b = new Book("978-0261102217", "The Hobbit");
Set<Book> shelf = new HashSet<>();
shelf.add(a);
shelf.add(b);
```

```bash run
cd /workspace/18-capstone && javac -d out *.java && java -cp out Book
```

```text
equal: true
same hash code: false
books in the set: 2
```

The two books are **equal**: same ISBN, and the `equals` the previous developer wrote compares exactly that. Yet a set, which keeps one
of each, holds **two**. The middle line is the clue. To see why it matters, you need to know how a `HashSet`
finds anything at all.
:::

:::step{type=concept title="First the shelf, then the book"}
This is the Long Room of Trinity College Library in Dublin, home to about 200,000 of its oldest books. Look at the
end of each bookcase: a column of letters runs up it, `aa`, `bb`, `cc`..., one for each shelf.

:::photo{src="/lesson-images/java/long-room-library.webp" alt="The Long Room of the Old Library at Trinity College Dublin: a long hall with a curved wooden ceiling, tall bookcases on both sides, each bay marked with letters, and marble busts along the aisle" credit="Diliff" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Long_Room_Interior,_Trinity_College_Dublin,_Ireland_-_Diliff.jpg"}
The Long Room, Trinity College Dublin. Each bookcase is an address, and the letters running up its end name every shelf in it, so a librarian goes straight to the right place.
:::

A librarian looking for a book does not walk past 200,000 spines. The catalogue says which **bookcase and shelf**,
and they only search there. Call that place a "bay". A `HashSet` (and a `HashMap`, chapter 11) works the same way:

1. It asks the object for its `hashCode()`: a number that says which bay to look in.
2. Only inside that bay does it compare with `equals`.

So the rule every Java class must keep is: **objects that are equal must have the same hash code**. `Book` broke it.
It wrote its own `equals`, but kept the hash code it inherited from `Object`, which is different for every object.
Two equal books were sent to two different bays, so the set never compared them, and kept both.
:::

:::step{type=example title="Worked example: equals and hashCode, always together"}
A member card is equal to another when the member number matches:

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Card other)) return false;
    return number == other.number;
}

@Override
public int hashCode() {
    return Integer.hashCode(number);
}
```

1. `equals` decides what "the same card" means: the same `number`.
2. `hashCode` is built from **exactly the same field**. Equal cards then always land in the same bay.
3. `Objects.hash(a, b, ...)` builds a hash code from any number of fields, objects included.

Write one, write both: it is the oldest rule in Java. (Records, chapter 9, write both for you.)
:::

:::step{type=task task=fix_book title="Your turn: fix the inherited Book"}
`Book` says two books are equal when their ISBNs match, but a `HashSet` keeps both copies, and a `HashMap` cannot find
a book by an equal key. Add what is missing. Keep the fix small: it is one method.

```bash run
cd /workspace/18-capstone && javac -d out *.java && java -cp out Book
```

When it is right, `same hash code: true` and `books in the set: 1`. Then press **Check**.

The usual slips: building the hash code from the title as well as the ISBN (two copies with slightly different
titles would then be equal but land in different bays: use exactly the field `equals` uses); or forgetting
`@Override` and misspelling the name, `hashcode` with a small c, which quietly adds a new method that nobody calls.
:::

:::step{type=concept title="A plan before code"}
The report is the biggest method you have written, and that is exactly when to stop and plan, in plain words,
before any code. Open `MonthlyReport.java`: it is a record (chapter 9) of five values. Then the plan:

1. Read every line (chapter 15). The header is line 1, so the data starts at line 2.
2. For each line: skip it if blank. Split it with `split(",", -1)`. If the category is empty or the amount is not a
   number (chapter 13's try and catch), remember the **line number** and skip it.
3. From the good rows: add the total, count them, and total per category with `merge`.
4. Round to two decimals, work out the average (0 when there are no good rows), and return one `MonthlyReport`.

Every step is a chapter you have done. The only new trick is the line numbers.
:::

:::step{type=example title="Worked example: rows with their line numbers"}
```java
List<String> lines = Files.readAllLines(path);
for (int i = 1; i < lines.size(); i++) {
    int lineNumber = i + 1;
    String line = lines.get(i);
    if (line.isBlank()) {
        continue;
    }
    System.out.println(lineNumber + ": " + line);
}
```

`readAllLines` keeps blank lines in the list, so `i + 1` always matches the line number someone sees in an editor,
even after a blank line.

:::trace{title="four lines of a file"}
| i | lineNumber | line | prints | note |
|---|---|---|---|---|
| 1 | 2 | 2026-03-02,food,120 | 2: 2026-03-02,food,120 | Index 1 is line 2: the header was line 1. |
| 2 | 3 | (blank) | (nothing) | Blank: skipped, but it still uses a number. |
| 3 | 4 | 2026-03-03,,45 | 4: 2026-03-03,,45 | So this row is line 4, as an editor shows it. |
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
never a bad line. Reporting **which** lines were skipped lets someone fix the file instead of wondering why the
totals look low.
:::
:::

:::step{type=try title="Size up the data"}
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

46 lines. `cut -d, -f2` takes the second column, and `uniq -c` counts each value. The two blank categories are one
blank line and one row with no category; `category` is the header. Your report should find 41 good rows.
:::

:::step{type=task task=monthly_report title="Your turn: the monthly report"}
In `Report.java`, make `monthly(path)` give back a `MonthlyReport` with:

| Field | Value |
|---|---|
| `total` | the sum of the good amounts, rounded to 2 decimals |
| `count` | how many good rows |
| `average` | total divided by count, rounded to 2 decimals, or `0` when there are none |
| `perCategory` | the total per category, rounded to 2 decimals |
| `badLines` | the line numbers of rows with an empty category or a bad amount; blank lines are skipped, not reported |

For the five lines in "Guess first", it gives a total of `18120.0`, a count of `2`, an average of `9060.0` and bad
lines `[3, 4]`. Right now the starter prints zeros, `null` and `[]`. On the real file:

```bash run
cd /workspace/18-capstone && javac -d out *.java && java -cp out Report
```

```text
total 30086.0, 41 rows, average 733.8
rent 18000.0, food 2262.5
bad lines [16, 24, 32]
```

Then press **Check**. The usual slip: counting line numbers yourself and forgetting the blank line 9. Every bad
line after it then comes out one too small, `[15, 23, 31]`. The worked example's `i + 1` over `readAllLines`
avoids it, because the blank line stays in the list.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Two objects are `equals`. What must be true of their `hashCode()`?
:::
- [ ] Nothing
- [x] They must be the same
- [ ] They must be different
:::explain
Equal objects must report the same hash code, or hash-based collections look in the wrong bay.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is the safest first step when fixing someone else's class?
:::
- [ ] Rewrite it from scratch
- [x] Run it on a tiny example and see exactly how it fails
- [ ] Delete the parts you do not understand
:::explain
Seeing the exact failure (chapter 6) points you to the one thing to change, and keeps the fix small and safe.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Two different books happen to have the same hash code. Is that a bug?
:::
- [x] No: they share a bay, and `equals` tells them apart
- [ ] Yes: hash codes must be unique
:::explain
Hash codes only pick the bay. Different objects may share one (that is called a collision); equal objects must.
:::
:::

:::step{type=deep-dive title="Go deeper: where Java goes from here"}
You now know the Java that professional code is made of. The natural next steps:

- **Spring Boot**, LabBox's next Java course: Java's most popular framework for web back ends. Its controllers are
  classes, its services are interfaces, its data are records, its errors are exceptions, its builds are Maven and its
  tests are JUnit. You have met every one.
- **Concurrency**: threads, and Java 21's virtual threads, which let one program serve thousands of people at once.
- **The JVM itself**: memory, garbage collection, and why a Java program gets faster the longer it runs.

And Duke, the waving mascot from chapter 1, has been on every one of those journeys since Java was first released, in 1995.
:::

:::step{type=recap title="Course complete"}
You can now:

- Read code you did not write: run it small, compare what it does with what it should do, and fix one line.
- Keep `equals` and `hashCode` together, and explain how a `HashSet` finds things.
- Plan a multi-part method in plain words first, then build it from parts you know.
- Write Java from your first `println` to packages, Maven, tests and a real report.

:::photo{src="/lesson-images/java/java-18-sketch.webp" alt="Sketchnote: The capstone. Equal objects must have the same hash code; hashCode picks the bay, equals picks the book. Flow: read every line, line number = i + 1, bad row note the line, good row add it up, one MonthlyReport. Remember: write equals, write hashCode, always together; run someone else's code small before changing it; plan in plain words, then write the code; report bad data, never drop it silently." ai="true"}
One page of notes for this chapter.
:::

That is Java from zero, all eighteen chapters. Shelf started as two lines of `println`; it ends as a tested Maven
project that reads real data. Well done.
:::
