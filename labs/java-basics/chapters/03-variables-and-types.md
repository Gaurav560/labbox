:::step{type=story title="Can adding 1 make a number negative?"}
Take the biggest whole number Java's `int` can hold, 2147483647, and add 1. What do you get? 2147483648, surely.
Java says:

```text
-2147483648
```

A huge **negative** number. Is Java broken? No: every `int` lives in a fixed-size box of 32 bits, and when the box
is full it wraps around, like a car's odometer rolling over. By the end of this chapter you will know exactly why,
and why programs that handle money care so much about types.

Shelf counts books and adds up late fees, so today you learn how Java stores numbers and text.

:::mission
Write `percent`, which tells Shelf what share of books came back on time, and `formatRupees`, which shows a late
fee stored in paise as rupees.
:::
:::

:::step{type=concept title="Variables: a name, a type and a value" file="03-variables-and-types/Today.java" line="4-10"}
Open `Today.java`:

```java
int borrowed = 7;
int returned = 4;
double fineRupees = 12.5;

int stillOut = borrowed - returned;
System.out.println("Books still out: " + stillOut);
```

`int borrowed = 7;` creates a **variable**: a name (`borrowed`) for a value (`7`), with a **type** (`int`). In Java
the type comes first, and it never changes: `borrowed` will always hold a whole number. Assign it text, and `javac`
refuses before anything runs:

```text
E.java:1: error: incompatible types: String cannot be converted to int
```

The everyday types:

| Type | Holds | Example |
|---|---|---|
| `int` | whole numbers, up to about 2.1 billion | `int books = 7;` |
| `long` | much bigger whole numbers | `long views = 9000000000L;` |
| `double` | numbers with a decimal point | `double fine = 12.5;` |
| `boolean` | `true` or `false` | `boolean late = true;` |
| `char` | one character, in single quotes | `char grade = 'A';` |
| `String` | text, in double quotes | `String title = "The Hobbit";` |

`String` has a capital S: it is a class (chapter 9 explains why), while the others are built-in **primitive**
types. And as in maths class, `=` here means "store", not "equals": `stillOut = stillOut - 1;` is perfectly fine.

:::picture{name="labelled-jars"}
A variable is a labelled jar: the label is the name, the jar's shape is the type, and only values of that shape fit.
:::
:::

:::step{type=try title="One day at the library" file="03-variables-and-types/Today.java" line="4-12"}
Run it:

```bash run
cd /workspace/03-variables-and-types && java Today.java
```

```text
Books still out: 3
Fines today: 12.5 rupees
7 / 2 = 3, but 7 / 2.0 = 3.5
```

Look at the last line. `7 / 2` is **3**? And `7 / 2.0` is 3.5? Hold that thought: it is the most important rule of
this chapter. Change `borrowed` to 10 first, save, and run it again: every line worked out from it changes.
:::

:::step{type=concept title="Dividing whole numbers throws the fraction away"}
When **both** sides of `/` are whole numbers (`int`), Java does **integer division**: it gives back a whole number
and throws the fraction away. Not rounding: just cutting.

| Code | Answer | Why |
|---|---|---|
| `7 / 2` | `3` | both `int`: the .5 is cut off |
| `7 / 2.0` | `3.5` | one side is a `double`, so the answer is too |
| `7 % 2` | `1` | `%` is the remainder: 7 = 2 * 3 + 1 |
| `(double) 7 / 2` | `3.5` | `(double)` turns 7 into 7.0 first |
| `(int) 3.99` | `3` | `(int)` cuts a double down; it does not round |

Writing a type in brackets before a value is a **cast**: "treat this as a double". Cast **before** dividing:
`(double) (7 / 2)` is 3.0, because the division already happened between two ints and the .5 was already gone.
:::

:::step{type=predict title="Guess first"}
:::question
`int onTime = 45; int total = 60;` What is `onTime / total * 100`?
:::
- [ ] `75`
- [ ] `75.0`
- [x] `0`
:::explain
`45 / 60` is integer division: 0.75 is cut down to 0, and `0 * 100` is 0. To get 75.0, make it a double before
dividing: `(double) onTime / total * 100`.
:::
:::

:::step{type=example title="Worked example: an average with one decimal"}
The average of two marks, rounded to one decimal place:

```java
static double average(int a, int b) {
    double avg = (double) (a + b) / 2;
    return Math.round(avg * 10) / 10.0;
}

average(70, 75)    // 72.5
average(70, 71)    // 70.5
average(1, 2)      // 1.5
```

1. `(double) (a + b)` turns the sum into a double **before** dividing, so nothing is cut off.
2. `Math.round(x)` rounds to the nearest whole number. To keep one decimal, multiply by 10, round, then divide by
   `10.0` (a double, so the division keeps the decimal).

Your first task has this shape, with a percentage instead of an average.
:::

:::step{type=task task=percent title="Your turn: books returned on time"}
Open `Numbers.java` and make `percent(scored, total)` give back `scored` out of `total` as a percentage, rounded to
one decimal. When `total` is 0, give back 0 (dividing by zero makes no sense).

`percent(45, 60)` gives `75.0`, `percent(1, 3)` gives `33.3`, and `percent(7, 0)` gives `0.0`.

```bash run
cd /workspace/03-variables-and-types && java Numbers.java
```

The first line it prints is `percent(45, 60)`. Then press **Check**.
:::

:::step{type=concept title="Boxes of a fixed size, and money"}
Back to the mystery from the start. An `int` is stored in exactly 32 bits, so it has a largest value:

```text
2147483647
-2147483648
```

That is `Integer.MAX_VALUE`, and `Integer.MAX_VALUE + 1`. With no room left, the number wraps around to the most
negative `int`. Java does not warn you; it is your job to pick a type big enough (`long` goes up to about 9
quintillion).

Decimals have their own surprise: `0.1 + 0.2` is `0.30000000000000004` in Java, exactly as in Python, because a
`double` stores numbers in binary, where 0.1 has no exact form.

So how should a library store money? **As whole paise in an `int`** (or a `long`). ₹12.50 is `1250` paise: integer
maths is always exact, and you only turn it into rupees when you show it. That is what Shelf does, and your next
task is the "show it" part.
:::

:::step{type=concept title="Text and numbers together"}
`+` joins strings, and it works **left to right**. That gives a puzzle worth knowing:

```java
"5" + "5"        // "55"
"5" + 5 + 5      // "555": text first, so every + joins
5 + 5 + "5"      // "105": 5 + 5 is 10 first, then joined with "5"
```

To turn text into a number, ask the number's class: `Integer.parseInt("42") + 1` is `43`. Text that is not a whole
number throws an exception while the program runs:

```text
Exception in thread "main" java.lang.NumberFormatException: For input string: "12.5"
```

To **format** numbers into text, use `String.format`, with a pattern:

```java
String.format("%.2f", 3.14159)       // "3.14"   two decimals
String.format("%d.%02d", 12, 5)      // "12.05"  %02d pads to two digits with a zero
```

`%d` is a whole number, `%f` a decimal, and `%02d` "at least two digits, padded with 0".
:::

:::step{type=example title="Worked example: minutes as hours and minutes"}
A loan timer stores minutes and shows them as `2h 05m`:

```java
static String duration(int minutes) {
    return String.format("%dh %02dm", minutes / 60, minutes % 60);
}

duration(125)    // "2h 05m"
duration(60)     // "1h 00m"
duration(9)      // "0h 09m"
```

1. `minutes / 60` is integer division: whole hours, fraction thrown away. Here that is exactly what you want.
2. `minutes % 60` is what is left over: the minutes.
3. `%02d` keeps the minutes at two digits, so 5 shows as `05`.

Paise to rupees is the same idea with 100 instead of 60.
:::

:::step{type=task task=format_rupees title="Your turn: late fees in rupees"}
In `Numbers.java`, make `formatRupees(paise)` give back the amount as rupees: the sign `₹`, the rupees, a dot, and
exactly two digits of paise.

`formatRupees(1250)` gives `"₹12.50"`, `formatRupees(5)` gives `"₹0.05"`, and `formatRupees(120000)` gives
`"₹1200.00"`.

```bash run
cd /workspace/03-variables-and-types && java Numbers.java
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is `10 / 4` in Java?
:::
- [x] `2`
- [ ] `2.5`
- [ ] `3`
:::explain
Both are `int`, so the fraction is cut off (not rounded): 2.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `5 + 5 + "5"` give?
:::
- [ ] `"555"`
- [x] `"105"`
- [ ] `15`
:::explain
`+` works left to right: `5 + 5` is the number 10, then `10 + "5"` joins into `"105"`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does Shelf store ₹12.50 as the `int` 1250?
:::
- [ ] `int` is faster to type
- [x] Whole numbers are exact; decimals like 0.1 are not
- [ ] Java has no decimals
:::explain
A `double` cannot store most decimal fractions exactly. Whole paise in an `int` are always exact.
:::
:::

:::step{type=deep-dive title="Go deeper: var, BigDecimal and the eight primitives"}
**var.** Since Java 10 you can let Java work out a local variable's type: `var count = 3;` is an `int`. The type is
still fixed; you just do not write it. Use it when the type is obvious from the right-hand side.

**BigDecimal.** For money with decimals, banks use `java.math.BigDecimal`: `new BigDecimal("0.1").add(new
BigDecimal("0.2"))` is exactly `0.3`. It is slower and wordier, which is why whole paise in a `long` is also popular.

**Eight primitives.** Java has exactly eight primitive types: `byte`, `short`, `int`, `long` (whole numbers of 8,
16, 32 and 64 bits), `float`, `double` (decimals), `char` and `boolean`. Everything else, including `String`, is an
object, built from classes.

**Overflow on purpose.** `Math.addExact(Integer.MAX_VALUE, 1)` throws an `ArithmeticException` instead of
wrapping around, for code that must never get it silently wrong.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Declare variables with a type: `int`, `long`, `double`, `boolean`, `char`, `String`.
- Avoid integer division surprises with a cast, and round with `Math.round`.
- Explain overflow and why money is stored as whole paise.
- Join text and numbers with `+`, parse text with `Integer.parseInt`, and format with `String.format`.

:::photo{src="/lesson-images/java/java-03-notes.webp" alt="Handwritten notes about Java types: 7 / 2 is 3, 7 / 2.0 is 3.5, cast before dividing, MAX_VALUE + 1 is negative, money in paise" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 4: making decisions, so Shelf knows when a book is late.
:::
