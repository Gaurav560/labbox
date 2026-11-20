:::step{type=story title="Why types matter"}
Every program stores values: a price, a name, a mark. Java asks you to say what **kind** of value each
one is, its **type**, before you use it. That sounds strict, but it is a gift: Java catches many
mistakes before your program ever runs.

:::mission
In `types/Numbers.java`, write `percent`, which needs a careful division, and `formatRupees`, which
turns paise into a price like `₹12.50`.
:::
:::

:::step{type=concept title="Variables are labelled boxes"}
Picture a row of boxes, each with a **label** and a **kind of thing** it may hold. A box for whole
numbers cannot hold text, just as an egg tray cannot hold milk.

In Java, a **variable** is such a box. You give it a type, a name, and usually a first value:

```java
int marks = 45;          // a whole number
double price = 49.5;     // a number with a decimal point
String name = "Riya";    // text
boolean passed = true;   // true or false
```

Read the first line as: "make a box for an `int`, call it `marks`, and put 45 in it".

:::picture{name="labelled-jars"}
A variable is a labelled jar; its shape is its type.
:::
:::

:::step{type=concept title="Changing what is in the box"}
Once a box exists, you can put a new value in it with `=`, without saying the type again:

```java
int marks = 45;
marks = 60;              // the box now holds 60
marks = marks + 5;       // read 60, add 5, store 65
```

The last line looks odd at first, but read it right to left: "take what is in `marks`, add 5, and put
the result back into `marks`".

:::mistake
`marks = "sixty";` does not compile: the box is for `int`, and `"sixty"` is text. Java stops you
before the program runs, which is exactly the point of types.
:::
:::

:::step{type=concept title="Two kinds of division"}
Java treats whole numbers and decimals differently when dividing:

```java
7 / 2        // 3     both are int: the fraction is thrown away
7.0 / 2      // 3.5   one is a double: the fraction is kept
7 % 2        // 1     % gives the remainder
```

Think of sharing 7 sweets between 2 children with `int`: each gets 3, and 1 is left over (that is
`7 % 2`). With `double` you are allowed to cut a sweet in half, so each gets 3.5.
:::

:::step{type=example title="Worked example: an average that keeps the fraction"}
To divide two `int`s without losing the fraction, **cast** one of them to `double` first:

```java
public static double average(int total, int count) {
    if (count == 0) {
        return 0;
    }
    return (double) total / count;
}

// average(7, 2) gives 3.5, not 3
```

1. `count == 0` is answered first: dividing by zero makes no sense.
2. `(double) total` turns the whole number into a decimal **before** the division.
3. A `double` divided by an `int` is a `double`, so the fraction survives.

`percent` uses this same idea, plus rounding.

:::trace{title="average(7, 2)"}
| step | value | note |
|---|---|---|
| count == 0? | false | 2 is not 0, so it is safe to divide. |
| 7 / 2 (ints) | 3 | Dividing two ints drops the fraction: this is the trap. |
| (double) 7 / 2 | 3.5 | Make one side a double first, and the fraction stays. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `System.out.println(45 / 50 * 100);` print?
:::
- [ ] `90`
- [x] `0`
- [ ] `90.0`
- [ ] It does not compile
:::explain
`45 / 50` uses two `int`s, so the answer is `0` (0.9 with the fraction thrown away), and `0 * 100` is
still `0`. Almost everyone falls into this once. Cast first: `(double) 45 / 50 * 100` is `90.0`.
:::
:::

:::step{type=try title="See both divisions"}
Java can run a single file directly. Write a tiny program and run it:

```bash run
cat > /tmp/Div.java <<'JAVA'
public class Div {
    public static void main(String[] args) {
        System.out.println(45 / 50 * 100);
        System.out.println((double) 45 / 50 * 100);
        System.out.println(7 / 2 + " " + 7 % 2 + " " + 7.0 / 2);
    }
}
JAVA
java /tmp/Div.java
```
:::

:::step{type=task task=percent title="Warm-up: a percentage"}
In `types/Numbers.java`, make `percent(scored, total)` return the percentage **rounded to one
decimal**, and `0` when `total` is `0`.

- `percent(45, 50)` returns `90.0`
- `percent(1, 3)` returns `33.3`
- `percent(7, 0)` returns `0.0`

To round to one decimal: `Math.round(x * 10) / 10.0`.
:::

:::step{type=concept title="Building text with String.format"}
Joining text with `+` works, but for numbers in a fixed shape, `String.format` is clearer. It takes a
**pattern** with placeholders, then the values to put in them:

```java
String.format("%s scored %d", "Riya", 92)   // "Riya scored 92"
String.format("%.1f%%", 33.333)             // "33.3%"
String.format("%02d", 5)                    // "05"
```

- `%s` is replaced by text, `%d` by a whole number, `%.1f` by a decimal with one digit.
- `%02d` means "at least two digits, padded with a zero", so 5 becomes `05`.
:::

:::step{type=task task=format_rupees title="Paise as a price"}
In `types/Numbers.java`, make `formatRupees(paise)` show the amount in rupees with two digits of paise.

- `formatRupees(1250)` returns `"₹12.50"`
- `formatRupees(5)` returns `"₹0.05"`
- `formatRupees(120000)` returns `"₹1200.00"`

1250 paise is 12 rupees (`1250 / 100`) and 50 paise (`1250 % 100`).
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `7 / 2` in Java, when both are `int`?
:::
- [ ] `3.5`
- [x] `3`
- [ ] `4`
- [ ] It does not compile
:::explain
Dividing two `int`s keeps only the whole part: `3`. Make one of them a `double` to keep the `.5`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `String.format("%02d", 7)` give?
:::
- [ ] `"7"`
- [x] `"07"`
- [ ] `"70"`
- [ ] `"007"`
:::explain
`%02d` pads the number to two digits with a leading zero. That is how 5 paise shows as `.05`.
:::
:::

:::step{type=deep-dive title="Primitive types and why money avoids double"}
`int`, `double`, `boolean` and `char` are **primitive** types: plain values, stored directly. `String`
is different: it is an **object** (chapter 7). Java has more primitives too: `long` for very big whole
numbers, `float` for smaller decimals, `byte` and `short` for tiny ones.

A `double` cannot store most decimals exactly: `0.1 + 0.2` is `0.30000000000000004`. Banks never keep
money in `double`. They use whole numbers of the smallest unit (paise, as you did here) or
`java.math.BigDecimal`, which does exact decimal arithmetic.
:::

:::step{type=recap}
- A variable is a labelled box with a type: `int`, `double`, `String`, `boolean`.
- `int / int` throws the fraction away; cast with `(double)` first to keep it.
- `%` gives the remainder; `Math.round(x * 10) / 10.0` rounds to one decimal.
- `String.format` builds text from a pattern: `%d`, `%s`, `%.2f`, `%02d`.
:::
