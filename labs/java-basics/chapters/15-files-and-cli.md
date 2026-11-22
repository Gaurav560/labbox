:::step{type=story title="What happens to Shelf's data when you close it?"}
Everything Shelf has learned so far vanishes the moment the program ends. Every list, every map, every `Book`
object lives in memory, and memory is wiped when `main` returns. Run it again, and Shelf remembers nothing.

Real programs keep their data in **files**, and the most popular kind of data file in the world is the humble
CSV: plain text, one record per line, values separated by commas. Every bank, spreadsheet and shop till can export
one.

Today Shelf reads a real CSV, a month of the library's spending, and becomes a **command-line program**: a tool
people run from the terminal with their own file and options, like `javac` and `git`.


Before disks were cheap, data lived on punched cards, one record per card. This is how the US government kept its
records in 1959: a warehouse of boxes, a few hundred thousand cards per aisle. A CSV file is the same idea, one
record per line, on a disk the size of a fingernail.

:::photo{src="/lesson-images/java/punched-cards.webp" alt="A black and white photo of a huge warehouse filled with rows of stacked boxes of IBM punched cards" credit="U.S. National Archives and Records Administration" license="Public domain" source="https://commons.wikimedia.org/wiki/File:IBM_card_storage.NARA.jpg"}
IBM punched cards in storage at a US federal records centre, 1959.
:::
:::mission
Write `readTotals`, which adds up a messy CSV per category, and the `Summary` program, which prints the top
categories, with a friendly message when the file is missing.
:::
:::

:::step{type=try title="Read a whole file" file="15-files-and-cli/Members.java" line="9-18"}
Open `Members.java`, and look at `members.txt` next to it: a name and a number of books on each line, and one
blank line.

```java
Path path = Path.of("members.txt");
List<String> lines = Files.readAllLines(path);
System.out.println(lines.size() + " lines");
for (String line : lines) {
    if (line.isBlank()) {
        continue;
    }
    String[] parts = line.split(",");
    System.out.println(parts[0] + " has " + parts[1] + " books");
}
```

```bash run
cd /workspace/15-files-and-cli && java Members.java
```

```text
4 lines
Asha has 2 books
Kabir has 0 books
Riya has 5 books
```

- `Path.of("members.txt")` names a file. A bare name means "in the folder I am running in".
- `Files.readAllLines(path)` reads the whole file into a `List<String>`, one string per line.
- `continue` skips the rest of this lap of the loop: the blank line is counted in the 4, but never printed.
:::

:::step{type=concept title="When the file is not there"}
`main` says `throws IOException`. Chapter 13 explained why: reading a file can fail for reasons that are not
bugs, so Java makes you decide what to do. Here, `main` passes the problem on, and when nobody handles it:

```text
Exception in thread "main" java.nio.file.NoSuchFileException: nobody.txt
	at java.base/sun.nio.fs.UnixException.translateToIOException(UnixException.java:92)
```

A stack trace is fine for you. For someone who just ran your tool with a typo in the file name, it is frightening.
A good command-line program catches `NoSuchFileException` and says one clear sentence instead. That is half of
your second task.
:::

:::step{type=concept title="CSV: one record per line"}
Open `expenses.csv`. It starts like this:

```text
date,category,amount
2026-03-01,rent,18000
2026-03-01,fun,600
```

The first line is the **header**: the names of the columns, not data. Every other line is one record, and
`split(",")` cuts it into its three values.

But this file is real, which means it is messy. Scroll down, and you will find a blank line, an amount that says
`abc`, a row with no amount, and a row with no category. And here is a trap in `split`:

```java
"2026-03-07,food,".split(",")        // [2026-03-07, food]
"2026-03-07,food,".split(",", -1)    // [2026-03-07, food, ]
```

By default, `split` silently **drops empty pieces at the end**, so the missing amount makes the row look like it
has only two columns. Passing `-1` keeps them, so every row has three pieces and you can check each one.

:::picture{name="file-lines"}
A file is a ribbon of lines: the header first, then one record on each line.
:::
:::

:::step{type=example title="Worked example: count the rows per category"}
Not the totals (that is your task), but the same skeleton: how many good rows does each category have?

```java
static Map<String, Integer> rowsPerCategory(Path path) throws IOException {
    List<String> lines = Files.readAllLines(path);
    Map<String, Integer> counts = new HashMap<>();
    for (int i = 1; i < lines.size(); i++) {
        String[] parts = lines.get(i).split(",", -1);
        if (parts.length != 3 || parts[1].isBlank()) {
            continue;
        }
        counts.merge(parts[1], 1, Integer::sum);
    }
    return counts;
}
```

1. The loop starts at 1: line 0 is the header.
2. Rows without exactly three pieces (like the blank line) and rows with no category are skipped.
3. `merge(key, 1, Integer::sum)` is the modern way to count: put 1 if the key is new, otherwise add 1 to the old
   value with `Integer::sum`. It does the work of chapter 11's `getOrDefault` in one call.
:::

:::step{type=predict title="Guess first"}
:::question
What is `"a,b,".split(",").length`?
:::
- [ ] `3`
- [x] `2`
- [ ] `1`
:::explain
Empty pieces at the end are dropped, so you get `[a, b]`. `"a,b,".split(",", -1)` keeps the empty piece and has
length 3.
:::
:::

:::step{type=task task=read_totals title="Your turn: totals from a messy CSV"}
Open `Expenses.java` and make `readTotals(path)` give back a map of each category to its total amount, rounded to two
decimals:

- skip the header, blank lines, rows without three pieces, rows with no category, and amounts that
  `Double.parseDouble` cannot read (chapter 13's try and catch);
- a file with only the header gives an empty map;
- a missing file throws `NoSuchFileException`, which `Files.readAllLines` already does for you.

On `expenses.csv`, `rent` is `18000.0`.

```bash run
cd /workspace/15-files-and-cli && javac -d out *.java && java -cp out Expenses
```

Then press **Check**.
:::

:::step{type=concept title="A program people can run" file="15-files-and-cli/Args.java" line="3-12"}
`main` has had a parameter all along: `String[] args`. It holds the **words typed after the program's name**. Open
`Args.java`:

```bash run
cd /workspace/15-files-and-cli && java Args.java expenses.csv --top 2
```

```text
3 words
args[0] = expenses.csv
args[1] = --top
args[2] = 2
```

Every word arrives as a `String`, even `2`: turn it into a number with `Integer.parseInt`. Now run it with no
words at all, and then ask the terminal how it ended:

```bash run
cd /workspace/15-files-and-cli && java Args.java; echo "exit $?"
```

```text
0 words
Usage: java Args.java <words>
exit 2
```

Two more habits of real command-line tools:

- **Problems go to `System.err`**, not `System.out`. Both show in the terminal, but when someone saves the output
  to a file (`> out.txt`), errors still appear on their screen instead of hiding in the file.
- **The exit code** says how it went: `System.exit(0)` (or just ending) means success; any other number means
  failure. `$?` in the terminal shows the last one. Scripts, and LabBox's own checks, read it.
:::

:::step{type=task task=summary_cli title="Your turn: the Summary program"}
Open `Summary.java` and make it a real tool:

- `args[0]` is the CSV file; `--top N` after it chooses how many categories to print, and the default is 3;
- print the categories with the biggest totals first, one per line, as `category: amount` with two decimals
  (`%.2f`);
- for a missing file, print `File not found: <the path>` to `System.err` (no stack trace) and end with exit code 1.

```bash run
cd /workspace/15-files-and-cli && javac -d out *.java && java -cp out Summary expenses.csv --top 2
```

```text
rent: 18000.00
shopping: 4095.00
```

Then try `java -cp out Summary missing.csv; echo "exit $?"`, and press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
You run `java Report.java june.csv 5`. What is `args[1]`?
:::
- [ ] `june.csv`
- [x] `"5"`, a String
- [ ] the number 5
:::explain
`args[0]` is the first word after the file name of the program. Every word is a String; parse it to get a number.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why do error messages go to `System.err`?
:::
- [ ] They print in red
- [x] They stay on screen even when the normal output is saved to a file
- [ ] Java requires it
:::explain
`>` redirects only the normal output, so errors written to `System.err` still reach the person.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A program ends with `System.exit(1)`. What does that tell a script that ran it?
:::
- [ ] It printed one line
- [x] Something went wrong
- [ ] It succeeded
:::explain
0 means success; any other exit code means failure.
:::
:::

:::step{type=deep-dive title="Go deeper: big files, writing files and text encodings"}
**Big files.** `readAllLines` loads the whole file into memory. For a file of 10 GB, read it a line at a time with
`Files.lines(path)`, which gives a lazy stream (chapter 14), inside try-with-resources so the file is closed.

**Writing.** `Files.writeString(Path.of("report.txt"), text)` writes a file in one line; `Files.write(path, lines)`
writes a list of lines.

**Encodings.** A file is bytes, not letters. Java 18 and later read and write **UTF-8** by default, the encoding
that can hold every script in the world: Hindi, Tamil and emoji included. Older programs sometimes guessed the
encoding from the computer and garbled anything that was not English.

**Real CSV is harder.** A value can contain a comma inside quotes (`"Mumbai, India"`), which a plain `split` cuts
in half. Production code uses a CSV library for that.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read a text file with `Path.of` and `Files.readAllLines`, and handle a missing file.
- Parse a messy CSV: skip the header and bad rows, and use `split(",", -1)` to keep empty values.
- Count and add per key with `merge`.
- Write a command-line program: read `args`, send errors to `System.err`, and end with a meaningful exit code.

:::photo{src="/lesson-images/java/java-15-notes.webp" alt="Handwritten notes about files and command-line programs: Files.readAllLines, skip the header, split with -1 keeps empty values, merge to add per key, args holds the words, errors to System.err, exit code 0 means OK" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 16: packages, jar files and Maven, so Shelf can grow from a folder of files into a real project.
:::
