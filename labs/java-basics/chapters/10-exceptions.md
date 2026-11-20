:::step{type=story title="Why exceptions"}
Real input is never perfect. Someone types "abc" as their age, a file is missing, a value is out of
range. A good program does not crash on the first surprise: it explains what went wrong, or skips the
bad value and carries on. Java's tool for this is the **exception**.

:::mission
In `errors/Ages.java`, read an age with clear errors for bad input, and add up a list of values while
collecting the ones that are not numbers.
:::
:::

:::step{type=concept title="An exception is an alarm"}
Picture a fire alarm in a building. When something goes wrong in one room, the alarm goes off and
everyone stops what they are doing, until someone whose job it is deals with it.

When Java cannot continue, it **throws** an exception: normal work stops, and Java looks for code that
will **catch** it. If nobody does, the program ends with a stack trace.

```java
Integer.parseInt("abc");   // throws NumberFormatException
int[] a = new int[2];
a[5] = 1;                  // throws ArrayIndexOutOfBoundsException
```

The exception's name already tells you a lot about what went wrong.

:::picture{name="fire-alarm"}
An exception stops the work until something handles it.
:::
:::

:::step{type=concept title="Catching: try and catch"}
Code that might throw goes in a `try` block. If it throws, Java jumps to the matching `catch`:

```java
try {
    int age = Integer.parseInt(text);
    System.out.println("age " + age);
} catch (NumberFormatException e) {
    System.out.println("please type a whole number");
}
System.out.println("carrying on");
```

- If parsing works, the `catch` block is skipped.
- If it fails, the rest of `try` is skipped and the `catch` block runs.
- Either way, the program **carries on** after the `catch`.
:::

:::step{type=concept title="Throwing your own"}
Your methods can throw exceptions too, with a message in your own words:

```java
if (amount <= 0) {
    throw new IllegalArgumentException("amount must be positive: " + amount);
}
```

You can also define your own exception class, like the `InvalidAgeException` in your workspace. When
you catch one exception and throw another, pass the first as the **cause** so nothing is lost:

```java
throw new InvalidAgeException("not a whole number: " + text, e);
```
:::

:::step{type=example title="Worked example: a safe quantity"}
A method that turns bad input into a clear exception:

```java
public static int parseQuantity(String text) {
    int q;
    try {
        q = Integer.parseInt(text.trim());
    } catch (NumberFormatException e) {
        throw new IllegalArgumentException("not a quantity: \"" + text + "\"", e);
    }
    if (q < 1) {
        throw new IllegalArgumentException("quantity must be at least 1: " + q);
    }
    return q;
}
```

1. The risky line goes inside `try`.
2. The low-level error becomes one in our own words, with the original kept as the cause.
3. A value that parsed but makes no sense gets its own clear message.

`parseAge` follows this exact shape with `InvalidAgeException`.

:::trace{title="parseQuantity with three inputs"}
| text | parseInt | q < 1? | result |
|---|---|---|---|
| " 3 " | 3 | no | returns 3 (trim removed the spaces) |
| "2.5" | NumberFormatException |  | IllegalArgumentException: not a quantity: "2.5" |
| "0" | 0 | yes | IllegalArgumentException: quantity must be at least 1: 0 |
:::
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
- [ ] A stack trace and nothing else
:::explain
Parsing `"12a"` throws, so Java skips the rest of `try`, runs the `catch` block, and then carries on
normally: `done` is printed too.
:::
:::

:::step{type=try title="Catch one, carry on"}
```bash run
cat > /tmp/Catch.java <<'JAVA'
public class Catch {
    public static void main(String[] args) {
        for (String text : new String[] {"42", "abc", "7"}) {
            try {
                System.out.println(text + " -> " + Integer.parseInt(text));
            } catch (NumberFormatException e) {
                System.out.println(text + " -> problem: " + e.getMessage());
            }
        }
    }
}
JAVA
java /tmp/Catch.java
```
:::

:::step{type=task task=parse_age title="Warm-up: read an age"}
In `errors/Ages.java`, make `parseAge(text)` return a whole number from 0 to 150, ignoring spaces at the
ends:

- `parseAge("17")` returns `17`, and `parseAge(" 42 ")` returns `42`
- `parseAge("abc")` throws `InvalidAgeException` with the `NumberFormatException` as its cause
- `parseAge("-1")`, `parseAge("151")` and `parseAge("12.5")` throw `InvalidAgeException`
:::

:::step{type=concept title="Checked exceptions and throws"}
Look at `parseAge`'s first line: `throws InvalidAgeException`. Our exception is **checked**: Java forces
every caller to either catch it or declare it too. It is Java's way of making sure nobody forgets that
reading an age can fail.

`IllegalArgumentException` and `NumberFormatException` are **unchecked**: Java does not force you to
handle them. They usually mean a programming mistake rather than bad outside input.
:::

:::step{type=task task=safe_sum title="Add the good, report the bad"}
In `errors/Ages.java`, make `safeSum(values)` add up the values that are numbers and collect the ones
that are not, returning both in a `SumResult`:

- `safeSum(["10", "x", "2.5", ""])` returns a total of `12.5` with bad values `["x", ""]`
- `safeSum([])` returns a total of `0` with no bad values

`Double.parseDouble` reads decimals and throws `NumberFormatException` for anything else.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When does a `finally` block run?
:::
- [ ] Only when an exception happened
- [ ] Only when no exception happened
- [x] Always, whether or not an exception happened
- [ ] Never, unless you call it
:::explain
`finally` always runs, which makes it the place for clean-up like closing files.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why pass the original exception as the **cause** when you throw your own?
:::
- [ ] It makes the program faster
- [x] So the full story (and the original stack trace) is kept for whoever investigates
- [ ] Java requires it
- [ ] To hide the original error
:::explain
The cause chain shows both what your code decided and what really went wrong underneath.
:::
:::

:::step{type=deep-dive title="try-with-resources and catching too much"}
Files, network connections and database connections must be closed even when something fails.
**try-with-resources** does it for you: `try (var reader = Files.newBufferedReader(path)) { ... }` closes
the reader automatically at the end, however the block ends.

Catch only the exceptions you expect and can handle. `catch (Exception e) { }` with an empty body
swallows every problem, including real bugs, and makes failures silent: one of the most common causes
of "it just stopped working" in production systems.
:::

:::step{type=recap}
- An exception is an alarm: work stops until some code catches it.
- `try { } catch (SomeException e) { }` handles the cases you expect, then the program carries on.
- `throw new ...Exception("clear message", cause)` reports a problem in your own words.
- Checked exceptions must be caught or declared with `throws`.
:::
