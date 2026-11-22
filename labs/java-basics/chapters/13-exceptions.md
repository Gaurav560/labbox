:::step{type=story title="What happens when someone types twelve?"}
A new member fills in Shelf's sign-up form. In the age box, they type `twelve`. Not `12`: the word.

Shelf calls `Integer.parseInt("twelve")`, and the whole program stops with a stack trace. Every member in the queue
behind them is stuck, because one person typed a word.

Real input is never perfect: words where numbers should be, files that are missing, values far out of range. A
good program does not die on the first surprise. It explains what went wrong, or puts the bad value aside and
carries on. Java's tool for this is the **exception**, and Java has one idea about exceptions that almost no other
popular language has. You will meet it today.

:::mission
Make `parseAge` turn bad input into a clear error of Shelf's own, and make `safeSum` add up the good values while
collecting the bad ones.
:::
:::

:::step{type=try title="One bad value, and the rest carry on" file="13-exceptions/Catch.java" line="4-13"}
Open `Catch.java`:

```java
for (String text : typed) {
    try {
        int age = Integer.parseInt(text);
        System.out.println(text + " -> " + age);
    } catch (NumberFormatException e) {
        System.out.println(text + " -> problem: " + e.getMessage());
    }
}
System.out.println("all done");
```

```bash run
cd /workspace/13-exceptions && java Catch.java
```

```text
42 -> 42
twelve -> problem: For input string: "twelve"
7 -> 7
all done
```

`twelve` did not stop the program. The risky line sits inside `try { }`; when it **throws** an exception, Java jumps
to the `catch` block that matches, runs it, and carries on. `7` was still read, and `all done` still printed.
:::

:::step{type=concept title="Where does the exception go?"}
What happens when an exception goes all the way up with nobody to catch it? In 1996 the first **Ariane 5** rocket
found out. A number too big for its slot raised an exception in the guidance software, nothing handled it, the
guidance system shut down, and 37 seconds after launch the rocket broke apart.

:::photo{src="/lesson-images/java/ariane-5.webp" alt="The white nose of an Ariane 5 rocket with its two side boosters, against a deep blue sky" credit="DiscoA340" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Ariane_5_on_Display_at_Le_Bourget.jpg"}
An Ariane 5 at the Paris Air and Space Museum.
:::

Press Play and follow the exception:

:::diagram{name="java-try-catch"}
A line inside try throws; the rest of try is skipped; the matching catch runs; the program carries on.
:::

An exception is a real **object**, made with `new` like any other, and `e` is the variable holding it.
`e.getMessage()` is its message. Its **class** says what kind of problem it is, and the name usually says it all:

| Exception | When |
|---|---|
| `NumberFormatException` | `parseInt` was given text that is not a number |
| `ArrayIndexOutOfBoundsException` | `a[5]` on an array of length 2 |
| `NullPointerException` | calling a method on `null` (chapter 9) |
| `ArithmeticException` | dividing an `int` by zero (chapter 6) |
| `IllegalArgumentException` | a method refused its input (chapters 8 to 12) |

:::

:::step{type=example title="Worked example: an error in your own words, with its cause"}
`For input string: "twelve"` is Java's message, not Shelf's. Good code turns a low-level error into one that
makes sense to the caller, and keeps the original inside it as the **cause**:

```java
static int parseQuantity(String text) {
    int q;
    try {
        q = Integer.parseInt(text.strip());
    } catch (NumberFormatException e) {
        throw new IllegalArgumentException("not a quantity: \"" + text + "\"", e);
    }
    if (q < 1) {
        throw new IllegalArgumentException("quantity must be at least 1: " + q);
    }
    return q;
}
```

:::trace{title="parseQuantity with three inputs"}
| text | parseInt gives | q < 1? | result |
|---|---|---|---|
| " 3 " | 3 | no | returns 3 |
| "2.5" | NumberFormatException |  | throws: not a quantity: "2.5" |
| "0" | 0 | yes | throws: quantity must be at least 1: 0 |
:::

1. Only the risky line goes inside `try`.
2. The `catch` throws a **new** exception with a clear message, and passes `e` as the second argument: the cause.
3. A number that parsed but makes no sense gets its own message.

If nobody catches it, the stack trace shows **both**, the cause under the words `Caused by:`:

```text
Exception in thread "main" java.lang.IllegalArgumentException: not a quantity: "2.5"
	at Cause.parseQuantity(Cause.java:7)
	at Cause.main(Cause.java:20)
Caused by: java.lang.NumberFormatException: For input string: "2.5"
```

Nothing is lost: the caller reads your words, and whoever debugs it later still sees exactly what went wrong
underneath.
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```java
try {
    int n = Integer.parseInt("12a");
    System.out.println("got " + n);
} catch (NumberFormatException e) {
    System.out.println("not a number");
}
System.out.println("done");
```
:::
- [ ] `got 12` then `done`
- [x] `not a number` then `done`
- [ ] Only `not a number`
:::explain
Parsing `"12a"` throws, so Java skips the rest of `try`, runs the `catch` block, and then carries on normally:
`done` is printed too.
:::
:::

:::step{type=task task=parse_age title="Your turn: read an age, or refuse it clearly"}
Open `Ages.java` and finish `parseAge(text)`:

- spaces around the number are fine: `parseAge(" 42 ")` gives `42`;
- text that is not a whole number throws an `InvalidAgeException`, with the `NumberFormatException` as its
  **cause**;
- a number outside 0 to 150 also throws an `InvalidAgeException`.

`InvalidAgeException.java` is Shelf's own exception, already written for you: it has a constructor that takes a
message and one that takes a message and a cause.

```bash run
cd /workspace/13-exceptions && javac -d out *.java && java -cp out Ages
```

Then press **Check**.
:::

:::step{type=concept title="Java's unusual idea: checked exceptions"}
Look at the first line of `parseAge`:

```java
public static int parseAge(String text) throws InvalidAgeException {
```

`throws InvalidAgeException` is a warning label: "calling me may throw this". And Java **enforces** the label.
Here is a program that opens a file and ignores what could go wrong:

```java
FileReader in = new FileReader("members.txt");
```

```text
Unreported.java:5: error: unreported exception FileNotFoundException; must be caught or declared to be thrown
        FileReader in = new FileReader("members.txt");
                        ^
```

It does not even compile. A missing file is not a bug in your code; it **will** happen one day, so Java makes you
decide now: catch it, or put `throws` on your own method and pass the decision to your caller.

Those are **checked** exceptions: classes that extend `Exception`, like `InvalidAgeException` and the file errors.
The others, which extend `RuntimeException` (`NumberFormatException`, `IllegalArgumentException`,
`NullPointerException`), are **unchecked**: they usually mean a bug, and the compiler does not force you to handle
them. Java is nearly alone in this: Python, JavaScript, Go and even Kotlin have no checked exceptions at all.
:::

:::step{type=task task=safe_sum title="Your turn: add the good, report the bad"}
In `Ages.java`, make `safeSum(values)` add up every value that is a number (with `Double.parseDouble`, so `2.5`
counts too), and collect the ones that are not. Give back both at once, in the `SumResult` record.

`safeSum(["10", "x", "2.5", ""])` gives a total of `12.5` and the bad values `["x", ""]`. An empty list gives a
total of 0 and no bad values.

The loop from `Catch.java` is the shape: try each value, and in the `catch`, remember it and carry on.

```bash run
cd /workspace/13-exceptions && javac -d out *.java && java -cp out Ages
```

Then press **Check**.
:::

:::step{type=concept title="finally: the clean-up that always runs" file="13-exceptions/Finally.java" line="5-26"}
Sometimes code must run whatever happens: close a file, close the desk. That is `finally`. Open `Finally.java`:

```java
try {
    if (title.isBlank()) {
        throw new IllegalArgumentException("no title");
    }
    System.out.println("lent " + title);
} finally {
    open--;
    System.out.println("desk closed");
}
```

```bash run
cd /workspace/13-exceptions && java Finally.java
```

```text
desk open for Dune
lent Dune
desk closed
desk open for  
desk closed
refused: no title
desks still open: 0
```

Look at the order for the blank title: `desk closed` comes **before** `refused`. The exception was on its way out of
`lend`, and Java stopped to run `finally` first. Whether the work succeeded or threw, the desk was closed, and the
count is back to 0.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why pass `e` when you write `throw new InvalidAgeException("not a whole number", e)`?
:::
- [ ] Java requires it
- [x] So the original exception is kept as the cause, and shows under `Caused by:`
- [ ] To catch it a second time
:::explain
The cause keeps the full story: your clear message on top, Java's detailed one underneath.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which exception must be caught or declared with `throws`, or the code does not compile?
:::
- [ ] `NumberFormatException`
- [ ] `NullPointerException`
- [x] `FileNotFoundException`
:::explain
`FileNotFoundException` is checked: it extends `Exception` but not `RuntimeException`. The other two are unchecked.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A `try` block throws and nothing catches it in this method. Does its `finally` block run?
:::
- [x] Yes, before the exception leaves the method
- [ ] No, the program stops at once
:::explain
`finally` always runs, whether `try` finished normally, returned, or threw.
:::
:::

:::step{type=deep-dive title="Go deeper: try-with-resources, catching too much, and the great debate"}
**try-with-resources.** Since Java 7, things that must be closed (files, network connections) go in brackets after
`try`, and Java closes them for you, even when an exception flies: `try (var in = new FileReader("a.txt")) { ... }`.
Chapter 15 uses it to read files.

**Do not catch everything.** `catch (Exception e) { }` with an empty block swallows every problem, including real
bugs, silently. Catch the exact exception you expect, and do something useful with it.

**Several kinds at once.** `catch (NumberFormatException | NullPointerException e)` handles two kinds in one block.

**The great debate.** Checked exceptions arrived with Java 1.0 in 1996. Many developers love that the compiler
reminds them about missing files; others find the `throws` labels tiring, and every language designed since has
left them out. Spring Boot mostly uses unchecked exceptions. Now you know both sides.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Catch an exception with `try` and `catch`, and let the program carry on.
- Throw your own exception with a clear message, and keep the original as the cause.
- Tell checked exceptions (must be caught or declared with `throws`) from unchecked ones.
- Use `finally` for clean-up that must always run.

:::photo{src="/lesson-images/java/java-13-notes.webp" alt="Handwritten notes about Java exceptions: try and catch, carry on, throw new with a cause, checked must be caught or declared, unchecked usually a bug, finally always runs" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 14: lambdas and streams, small functions you can pass around, and pipelines that read like sentences.
:::
