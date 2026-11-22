:::step{type=story title="Is 2100 a leap year?"}
Quick, without looking it up: is 2100 a leap year? It is divisible by 4, so... yes?

Most people say yes. The answer is **no**. And 2000, which was also divisible by 100, *was* a leap year. The
calendar has rules inside rules, and a program gets them right every time, but only if someone writes the rules
down exactly.

:::photo{src="/lesson-images/python/pope-gregory-xiii.webp" alt="A portrait of Pope Gregory XIII in red robes" credit="Unknown artist" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Pope_Gregory_XIII_portrait.jpg"}
Pope Gregory XIII. His calendar reform of 1582 added the rule about years divisible by 100 and 400, and most of the world still uses it.
:::

Programs are full of rules like this: *if* a book is late, charge a fine; *if* the member has too many books, say
no; *otherwise*, carry on. Today Shelf learns to decide.

:::mission
Write `grade`, which turns marks into a grade, and `isLeapYear`, which gets the calendar's tricky rule exactly
right.
:::
:::

:::step{type=concept title="Questions with true or false answers"}
Every decision starts with a question whose answer is a `boolean`: `true` or `false`. **Comparisons** ask those
questions:

| Operator | Asks | Example | Answer |
|---|---|---|---|
| `==` | equal? | `5 == 5` | `true` |
| `!=` | not equal? | `5 != 5` | `false` |
| `<` `>` | less, greater? | `3 < 7` | `true` |
| `<=` `>=` | or equal? | `7 >= 7` | `true` |

Three words combine them, written as symbols in Java:

- `a && b` ("and"): `true` only when both are.
- `a || b` ("or"): `true` when at least one is.
- `!a` ("not"): flips it.

```java
5 > 3 && 2 > 1        // true
!(5 > 3) || 2 > 1     // true: the left part is false, the right part is true
```

One warning for later: never compare **strings** with `==`. It compiles, but it asks a different question.
Chapter 7 shows why, and the right way.
:::

:::step{type=concept title="if and else: two paths" file="04-decisions/Loan.java" line="4-12"}
Open `Loan.java`:

```java
int daysLate = 3;

if (daysLate > 0) {
    System.out.println("Late by " + daysLate + " days: fine of " + daysLate * 2 + " rupees.");
} else {
    System.out.println("Returned on time. Thank you!");
}

System.out.println("Shelf checked the loan.");
```

1. Java works out the **condition** in the round brackets, `daysLate > 0`: `true`.
2. When it is `true`, the block in `{ }` after `if` runs, and the `else` block is skipped.
3. When it is `false`, the `if` block is skipped and the `else` block runs.
4. Either way, the program carries on after the closing brace.

The condition **must** be a `boolean`. Type `=` instead of `==` by mistake, and Java stops you before anything
runs:

```text
Eq.java:4: error: incompatible types: int cannot be converted to boolean
        if (daysLate = 3) {
                     ^
```

In some languages that mistake silently compiles and causes bugs for years. In Java it cannot.

:::picture{name="fork-in-road"}
An if is a fork in the road: the condition decides the path, then both paths meet again.
:::
:::

:::step{type=try title="Change the facts, change the path" file="04-decisions/Loan.java" line="4"}
Run it:

```bash run
cd /workspace/04-decisions && java Loan.java
```

```text
Late by 3 days: fine of 6 rupees.
Shelf checked the loan.
```

Now change `daysLate` to 0, save, and run it again:

```text
Returned on time. Thank you!
Shelf checked the loan.
```

Same program, different path. What would a negative `daysLate` print? Predict, then try it.
:::

:::step{type=example title="Worked example: more than two paths"}
`else if` adds more conditions, checked from the top:

```java
static String fineLevel(int rupees) {
    if (rupees >= 100) {
        return "high";
    } else if (rupees >= 20) {
        return "medium";
    } else {
        return "low";
    }
}
```

Follow `fineLevel(50)`: is 50 >= 100? No. Is 50 >= 20? Yes: return `"medium"`, and the method ends right there.

**Java stops at the first condition that is `true`**, so test the biggest threshold first, and let `else` catch
everything else.
:::

:::step{type=predict title="Guess first"}
:::question
Someone swapped the first two conditions: `if (rupees >= 20) return "medium"; else if (rupees >= 100) return "high";`.
What does `fineLevel(150)` give back?
:::
- [ ] `"high"`
- [x] `"medium"`
- [ ] `"low"`
:::explain
150 is >= 20, so the first condition is already `true`: `"medium"`. The `"high"` branch can never be reached.
:::
:::

:::step{type=task task=grade title="Your turn: a grade from marks"}
Open `Decisions.java` and make `grade(marks)` give back:

- `"A"` for 80 and above, `"B"` for 60 and above, `"C"` for 40 and above, `"F"` below 40;
- `"Invalid"` for marks below 0 or above 100.

Deal with the invalid marks first, then test from the highest grade down. Watch the edges: 80 is an A, 79 a B.

```bash run
cd /workspace/04-decisions && java Decisions.java
```

The first line it prints is `grade(80)`. Then press **Check**.
:::

:::step{type=example title="Worked example: a whole rule in one line"}
A rule with an exception: free delivery for orders of ₹500 or more, except heavy items, unless the customer is a
member.

```java
static boolean freeDelivery(int total, boolean heavy, boolean member) {
    return total >= 500 && (!heavy || member);
}
```

Read it as a sentence: "at least 500, **and** either not heavy **or** a member". The brackets keep the exception
together, and the whole rule is one `boolean` value, returned directly. No `if` needed.

`freeDelivery(600, false, false)` is `true`, `freeDelivery(600, true, false)` is `false`, and
`freeDelivery(600, true, true)` is `true`.
:::

:::step{type=task task=leap_year title="Your turn: the calendar's tricky rule"}
In `Decisions.java`, make `isLeapYear(year)` give back `true` for leap years:

- divisible by 4 is a leap year,
- **except** divisible by 100, which is not,
- **unless** also divisible by 400, which is.

2024 is `true`, 2023 `false`, 1900 `false`, 2000 `true`, 2100 `false`. "Divisible by 4" is `year % 4 == 0`.

```bash run
cd /workspace/04-decisions && java Decisions.java
```

The second line is `isLeapYear(2100)`. Then press **Check**.
:::

:::step{type=concept title="switch: choosing by value"}
When you compare one value against several fixed options, Java has a neat tool, the **switch expression**:

```java
static String shelfFor(String genre) {
    return switch (genre) {
        case "fantasy", "science fiction" -> "Shelf A";
        case "history" -> "Shelf B";
        default -> "Shelf C";
    };
}
```

`shelfFor("fantasy")` is `"Shelf A"`, `shelfFor("history")` is `"Shelf B"`, and anything else lands on
`default`: `"Shelf C"`. Each `case` can list several values, and the whole `switch` is one value you can return.

For a tiny either-or there is also the **ternary** operator: `books == 1 ? "book" : "books"` reads "if books is 1,
then "book", else "books"". With 4 books it gives `"books"`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `if (count = 1)` do in Java, where `count` is an `int`?
:::
- [ ] Sets count to 1, then runs the block
- [x] Does not compile: an int is not a boolean
- [ ] Compares count with 1
:::explain
An `if` needs a `boolean`. `count = 1` is an assignment whose value is an `int`, so `javac` refuses it.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In an `if` / `else if` chain, two conditions are both `true`. Which block runs?
:::
- [x] Only the first one
- [ ] Both, in order
- [ ] Only the last one
:::explain
Java stops at the first `true` condition and skips the rest.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `true && !false`?
:::
- [x] `true`
- [ ] `false`
:::explain
`!false` is `true`, and `true && true` is `true`.
:::
:::

:::step{type=deep-dive title="Go deeper: short-circuits and why 2100 is not a leap year"}
**Short-circuit.** `&&` and `||` stop as soon as they know the answer. In `member != null && member.isActive()`,
if `member` is `null`, the right side never runs, which avoids a crash. Professional Java code relies on this all
the time.

**Braces.** Java lets you leave out `{ }` when an `if` has a single line, but then adding a second line later
silently puts it outside the `if`. Most teams always write the braces.

**The calendar.** A year is about 365.2422 days. A leap day every 4 years gives 365.25, slightly too much. Skipping
3 leap days every 400 years (1700, 1800, 1900, but not 2000) brings the average to 365.2425: right for about 3,000
years.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Ask true-or-false questions with `== != < > <= >=`, and combine them with `&&`, `||` and `!`.
- Choose a path with `if`, `else if` and `else`, testing the biggest threshold first.
- Return a whole rule as one `boolean`, and pick by value with a `switch` expression.
- Trust Java to reject `=` where a condition belongs.

:::photo{src="/lesson-images/java/java-04-notes.webp" alt="Handwritten notes about Java decisions: if, else if, else; the first true wins; && || and !; switch with arrows; 2100 is not a leap year" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 5: loops, so Shelf can go through every book without a line of code for each.
:::
