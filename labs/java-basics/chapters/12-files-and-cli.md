:::step{type=story title="Why files and command-line programs"}
So far every value lived only while your program ran. Real programs read data that already exists, like
a month of expenses, and are started from a terminal by other people or by scripts. In this chapter you
build exactly that: a program someone runs with a file and gets an answer.

:::mission
In `files/Expenses.java`, read `expenses.csv` (a real, messy file in your workspace) into totals per
category, then finish `files/Summary.java`, a program that prints the biggest categories.
:::
:::

:::step{type=concept title="Paths and reading a whole file"}
A **path** is a file's address, like `expenses.csv` or `/workspace/expenses.csv`. Java's modern file
tools live in `java.nio.file`:

```java
Path path = Path.of("expenses.csv");
List<String> lines = Files.readAllLines(path);
lines.get(0)       // "date,category,amount" (the header)
lines.size()       // how many lines
```

`readAllLines` gives you the file as a list, one String per line, ready for the loops and string tools
you already know. If the file does not exist, it throws a `NoSuchFileException`.
:::

:::step{type=concept title="CSV: one record per line"}
A **CSV** file stores a table as text: one row per line, the columns separated by commas.

```text
date,category,amount
2026-03-02,food,120
2026-03-02,travel,40.50
```

To use a row, split it on commas and convert the parts you need:

```java
String[] parts = "2026-03-02,food,120".split(",", -1);
parts[1]                          // "food"
Double.parseDouble(parts[2])      // 120.0
```

The `-1` keeps empty parts at the end, so `"2026-03-04,travel,"` gives three parts, the last one empty.

:::picture{name="file-lines"}
Each line of a CSV file is one row, cut at the commas.
:::
:::

:::step{type=example title="Worked example: count the rows per category"}
Read, skip the header, split, and count per key:

```java
public static Map<String, Integer> rowsPerCategory(Path path) throws IOException {
    List<String> lines = Files.readAllLines(path);
    Map<String, Integer> out = new HashMap<>();
    for (int i = 1; i < lines.size(); i++) {      // 1. skip the header
        String[] parts = lines.get(i).split(",", -1);
        if (parts.length != 3) {                  // 2. skip broken rows
            continue;
        }
        out.merge(parts[1], 1, Integer::sum);     // 3. count
    }
    return out;
}
```

`merge(key, 1, Integer::sum)` is a compact "add 1 to this key's count". `readTotals` adds amounts
instead, and skips amounts that are not numbers.

:::trace{title="four lines of a file"}
| i | line | parts | out | note |
|---|---|---|---|---|
| 0 | date,category,amount |  | {} | The loop starts at 1, so the header is skipped. |
| 1 | 2026-03-02,food,120 | 3 parts | {food=1} | merge adds 1 to food's count (0 the first time). |
| 2 | 2026-03-02,travel | 2 parts | {food=1} | A broken row: continue skips it. |
| 3 | 2026-03-03,food,80 | 3 parts | {food=2} | food again: 1 + 1. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
`expenses.csv` has a row `2026-03-07,food,` with no amount. What does `Double.parseDouble("")` do?
:::
- [ ] Returns `0.0`
- [x] Throws a `NumberFormatException`
- [ ] Returns `null`
- [ ] Returns `NaN`
:::explain
An empty string is not a number, so `parseDouble` throws. Catch it and skip that row: one broken line
should never stop a whole report.
:::
:::

:::step{type=try title="Look at the real file"}
```bash run
head -5 expenses.csv; echo ...; grep -n -v -E '^[0-9-]+,[a-z]+,[0-9.]+$' expenses.csv
```

The second command lists the lines that do not look like `date,category,amount`: the header, a blank
line, a missing amount, a word for an amount, an empty category. Your code must survive all of them.
:::

:::step{type=task task=read_totals title="Warm-up: totals from a CSV"}
In `files/Expenses.java`, make `readTotals(path)` return the total per category, **rounded to 2
decimals**. Skip the header, blank lines, rows without three parts, and amounts that are not numbers.
A missing file throws `NoSuchFileException` (`Files.readAllLines` already does that for you).
:::

:::step{type=concept title="A program people can run"}
Every Java program starts at `main`, and the words typed after the class name arrive in `args`:

```java
public static void main(String[] args) {
    // java files.Summary expenses.csv --top 2
    // args[0] is "expenses.csv", args[1] "--top", args[2] "2"
}
```

A good program reports problems to **standard error** (`System.err.println(...)`), separate from its
normal output, and ends with an **exit code**: `0` means success, anything else failure.
`System.exit(1)` stops the program and reports failure, so scripts can tell something went wrong.
:::

:::step{type=task task=summary_cli title="The Summary program"}
In `files/Summary.java`, make the program print the biggest categories, biggest first, one per line as
`category: amount` with two decimals (`%.2f`). `--top N` says how many; the default is 3. For a missing
file it prints `File not found: <path>` to `System.err` and exits with code `1`, with no stack trace.

```bash run
javac -d /tmp/out files/*.java && java -cp /tmp/out files.Summary expenses.csv --top 2
```
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why print errors with `System.err` instead of `System.out`?
:::
- [ ] It is faster
- [x] So errors stay visible even when normal output goes to a file or another program
- [ ] `System.out` cannot print errors
- [ ] To make them red
:::explain
Normal output is often redirected (`> report.txt`); errors on stderr still reach the person.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does exit code `1` tell the shell?
:::
- [ ] Success
- [x] The program failed
- [ ] The program printed one line
- [ ] The program needs one argument
:::explain
`0` means success and anything else failure. Scripts check it to decide what to do next.
:::
:::

:::step{type=deep-dive title="Big files, encodings and jar files"}
`readAllLines` loads the whole file into memory, which is fine for a month of expenses but not for a
10 GB log. For big files, read line by line with `Files.lines(path)` (a stream) or a `BufferedReader`
in a try-with-resources block.

Text in files is stored in an **encoding**; Java 18 and later read and write UTF-8 by default, so names
in any language work. Real Java tools are packaged as a `.jar` file (a zip of compiled classes) and run
with `java -jar tool.jar`, which is exactly how Spring Boot applications start.
:::

:::step{type=recap}
- `Path.of` names a file; `Files.readAllLines` reads it as a list of lines.
- A CSV row is split on commas; skip rows you cannot read instead of crashing.
- `main(String[] args)` receives the command-line words.
- Errors go to `System.err`; `System.exit(1)` reports failure.
:::
