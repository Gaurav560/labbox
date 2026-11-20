:::step{type=story title="Why decisions"}
A program that always does the same thing is not much use. Real programs choose: a grade depends on
the marks, a discount on the total, a login on the password. In this chapter your code learns to
choose.

:::mission
In `decisions/Decisions.java`, turn marks into a grade, and decide whether a year is a leap year.
:::
:::

:::step{type=concept title="A fork in the road"}
Picture walking and reaching a fork: if it is raining, take the covered path; otherwise take the
park. You check **one condition**, then go **one way**.

Java's `if` is exactly that fork:

```java
if (marks >= 40) {
    result = "pass";
} else {
    result = "fail";
}
```

- The **condition** in brackets is a question with a `true` or `false` answer.
- When it is `true`, the first block runs; otherwise the `else` block runs.
- Exactly one of the two blocks runs, never both.

:::picture{name="fork-in-road"}
One question, and the answer picks the road.
:::
:::

:::step{type=concept title="Comparing and combining"}
Conditions are built from comparisons:

```java
marks >= 40      // at least 40
marks == 100     // exactly 100 (two equals signs!)
marks != 0       // not 0
```

and combined with `&&` (and), `||` (or) and `!` (not):

```java
age >= 13 && age <= 19     // a teenager: both must be true
day == 6 || day == 7       // a weekend: either is enough
!passed                    // the opposite of passed
```

:::mistake
`=` puts a value in a box; `==` asks whether two values are equal. `if (marks = 100)` does not
compile in Java, which saves you from a classic bug.
:::
:::

:::step{type=concept title="Many choices: else if"}
For more than two choices, chain them with `else if`. Java checks them **from the top** and stops at
the **first** true one:

```java
if (age < 5) {
    ticket = "Free";
} else if (age < 18) {
    ticket = "Child";
} else {
    ticket = "Adult";
}
```

A 3-year-old matches the first condition and stops there. A 10-year-old fails the first, matches the
second, and stops. Everyone else lands in `else`.
:::

:::step{type=example title="Worked example: a ticket price by age"}
Notice the order of the checks:

```java
public static String ticket(int age) {
    if (age < 0) {
        return "Invalid";
    } else if (age >= 60) {
        return "Senior";
    } else if (age >= 18) {
        return "Adult";
    } else {
        return "Child";
    }
}
```

1. **Impossible values first**: a negative age is answered before anything else.
2. Then the ranges **from the top down**: 60 and over, then 18 and over.
3. Each age matches exactly one branch, because the first true condition wins.

`grade` works the same way: invalid marks first, then 80, 60 and 40.

:::trace{title="ticket(45)"}
| check | true? | note |
|---|---|---|
| age < 0 | no | 45 is not below 0, so go on to the next check. |
| age >= 60 | no | 45 is not 60 or more: next check. |
| age >= 18 | yes | 45 is 18 or more: the answer is "Adult", and no later check runs. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `level(90)` return?

```java
static String level(int marks) {
    if (marks >= 40) return "pass";
    else if (marks >= 80) return "distinction";
    return "fail";
}
```
:::
- [x] `"pass"`
- [ ] `"distinction"`
- [ ] `"fail"`
- [ ] It does not compile
:::explain
`90 >= 40` is already true, so Java returns `"pass"` and never reaches the `80` check. Put the
strictest condition first. If you picked "distinction", you are in good company: this is one of the
most common ordering mistakes.
:::
:::

:::step{type=try title="Watch the order matter"}
```bash run
cat > /tmp/Order.java <<'JAVA'
public class Order {
    static String level(int m) {
        if (m >= 40) return "pass";
        else if (m >= 80) return "distinction";
        return "fail";
    }
    public static void main(String[] args) {
        System.out.println(level(90) + " " + level(50) + " " + level(10));
    }
}
JAVA
java /tmp/Order.java
```
:::

:::step{type=task task=grade title="Warm-up: grades from marks"}
In `decisions/Decisions.java`, make `grade(marks)` return:

| Marks | Grade |
|---|---|
| 80 to 100 | `"A"` |
| 60 to 79 | `"B"` |
| 40 to 59 | `"C"` |
| 0 to 39 | `"F"` |
| below 0 or above 100 | `"Invalid"` |

Edges matter: `grade(80)` is `"A"`, `grade(79)` is `"B"`, `grade(101)` is `"Invalid"`.
:::

:::step{type=concept title="Divisible by: the remainder trick"}
`%` gives the remainder of a division, so it answers "does this divide exactly?":

```java
2024 % 4    // 0: 4 divides 2024 exactly
2023 % 4    // 3: it does not
```

`year % 4 == 0` is therefore `true` exactly when the year is divisible by 4. You can combine several
such tests with `&&` and `||`, using brackets to group them, just like in maths.
:::

:::step{type=task task=leap_year title="Leap years"}
In `decisions/Decisions.java`, make `isLeapYear(year)` follow the real rule:

1. a year divisible by 4 is a leap year,
2. **except** years divisible by 100,
3. **except** years divisible by 400, which are leap years again.

`2024` is `true`, `2023` is `false`, `1900` is `false`, `2000` is `true`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `true && !false`?
:::
- [x] `true`
- [ ] `false`
- [ ] It does not compile
- [ ] `null`
:::explain
`!false` is `true`, and `true && true` is `true`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Does `if (count) { ... }` compile when `count` is an `int`?
:::
- [ ] Yes, it runs when count is not zero
- [x] No: a condition must be a `boolean`
- [ ] Yes, but with a warning
- [ ] Only inside `main`
:::explain
Java only accepts real `true` or `false` values as conditions. Write the question you mean:
`if (count > 0)`.
:::
:::

:::step{type=deep-dive title="The modern switch"}
For choosing by one value, Java 14 and later have **switch expressions**, which return a value
directly:

```java
String day = switch (n) {
    case 6, 7 -> "weekend";
    case 1, 2, 3, 4, 5 -> "weekday";
    default -> "unknown";
};
```

Each `case` lists values, the arrow gives the answer, and there is no "fall through" to the next case.
Older Java code uses `case 6: ... break;` instead, and forgetting a `break` was a classic bug the new
form removes.
:::

:::step{type=recap}
- `if (condition) { } else { }` runs exactly one block.
- Compare with `== != < <= > >=`; combine with `&&`, `||`, `!`.
- `else if` chains are checked from the top: strictest condition first.
- `x % n == 0` means "n divides x exactly".
:::
