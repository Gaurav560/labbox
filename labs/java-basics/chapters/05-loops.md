:::step{type=story title="How would you count ten thousand books?"}
Shelf's library has 10,000 books. To total up today's returns, would you write one line per book? Ten thousand
lines? Nobody does. You write the instruction **once** and tell Java: "do this for every item". That is a
**loop**, and it is why computers are so good at boring, repetitive work: they never get tired and never skip one.

Today you meet Java's three loops, and one famous crash that every Java developer has seen at least once.

:::mission
Write `sumTo`, which adds up 1 + 2 + ... + n, and `countVowels`, which counts the vowels in any text.
:::
:::

:::step{type=concept title="for-each: once for every item" file="05-loops/Week.java" line="4-10"}
Open `Week.java`:

```java
int[] returned = {12, 9, 15, 4, 20};

for (int count : returned) {
    System.out.println("Returned: " + count);
}

System.out.println("Done: that was the whole week.");
```

`int[] returned = {12, 9, 15, 4, 20};` is an **array**: several `int` values in one variable (chapter 8 is all
about arrays). The loop reads: "for each `int count` in `returned`, run the body".

1. Java takes the first value, `12`, puts it in `count`, and runs the body.
2. It takes the next one, `9`, and runs the body again.
3. It repeats until there are no values left, then carries on after the loop.

Each pass is an **iteration** (from the Latin word for "again"). The loop variable needs a type too (`int count`), because every value in the array
is an `int`.

:::picture{name="running-track"}
A loop is a lap around a track: the same route each time, with a new item on every lap.
:::
:::

:::step{type=try title="Watch it go round" file="05-loops/Week.java" line="6-8"}
Run it:

```bash run
cd /workspace/05-loops && java Week.java
```

```text
Returned: 12
Returned: 9
Returned: 15
Returned: 4
Returned: 20
Done: that was the whole week.
```

Two lines of loop, five lines of output. Add a sixth number to the array and run it again: the loop does one
more lap without you touching it.
:::

:::step{type=example title="Worked example: a running total"}
The most useful loop in the world keeps a **running total**:

```java
static int weekTotal(int[] counts) {
    int total = 0;
    for (int count : counts) {
        total = total + count;
    }
    return total;
}

weekTotal(new int[] {12, 9, 15})    // 36
```

Step through it and watch `total` grow:

:::trace{title="weekTotal(new int[] {12, 9, 15})"}
| count | total | note |
|---|---|---|
|  | 0 | Before the loop: total starts at zero. |
| 12 | 12 | First lap: 0 + 12. |
| 9 | 21 | 12 + 9. |
| 15 | 36 | 21 + 15. |
|  | 36 | No values left: return 36. |
:::

Three parts, always in this order: **before** the loop, set up the answer; **inside**, update it with one item;
**after**, return it. Counting works the same way: add 1 instead of the item, and only when a condition is true.
:::

:::step{type=concept title="The counting for loop"}
Sometimes you do not have a list: you want to count. Java's classic `for` loop has three parts in its brackets:

```java
for (int i = 0; i < 3; i++) {
    System.out.println("Lap " + i);
}
```

```text
Lap 0
Lap 1
Lap 2
```

- `int i = 0` runs once, before the loop: start the counter at 0.
- `i < 3` is checked **before** every lap: keep going while it is `true`.
- `i++` runs **after** every lap: add 1 to `i` (`i++` is short for `i = i + 1`).

Positions in Java arrays start at **0**, which is why counters usually start at 0 and stop **before** the length:
`for (int i = 0; i < returned.length; i++)` visits positions 0, 1, 2 of a 3-item array. Get it wrong by one, with
`<=` instead of `<`, and Java crashes on the last lap:

```text
12
9
15
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 3 out of bounds for length 3
	at Oops.main(Oops.java:5)
```

Position 3 does not exist in an array of length 3. That message, `Index ... out of bounds`, is one of the most
common in Java. Now you know what it means. (`returned.length` is the number of items in the array; for arrays
it is written **without** brackets, unlike a string's `length()`.)
:::

:::step{type=predict title="Guess first"}
:::question
What does `sumTo(5)` need to add up?
:::
- [ ] 0 + 1 + 2 + 3 + 4
- [x] 1 + 2 + 3 + 4 + 5
- [ ] 5 + 5 + 5 + 5 + 5
:::explain
"1 up to n" starts at 1 and includes n: a counter starting at 1, with `<=` this time, because n itself belongs in
the sum. The answer is 15.
:::
:::

:::step{type=task task=sum_to title="Your turn: 1 + 2 + ... + n"}
Open `Loops.java` and make `sumTo(n)` give back 1 + 2 + ... + n. For 0 or a negative `n`, give back 0.

`sumTo(5)` gives `15`, `sumTo(1)` gives `1`, and `sumTo(0)` gives `0`. A counting `for` loop and a running total
do it; a loop whose condition is false from the start simply never runs, which handles 0 and negatives for free.

```bash run
cd /workspace/05-loops && java Loops.java
```

The first line it prints is `sumTo(5)`. Then press **Check**.

The usual slip: `i < n` instead of `i <= n`. It leaves `n` itself out: we tried it, and `sumTo(5)` gave `10`, not
15. "Up to and including n" is `<=`.
:::

:::step{type=concept title="Looping over the characters of a string"}
A `String` is a sequence of characters, type `char`. You can look at one with `charAt(i)`, or loop over all of
them with `toCharArray()`:

```java
"Hobbit".charAt(0)     // 'H'
"Hobbit".length()      // 6

for (char c : "pen".toCharArray()) {
    System.out.println(c);
}
```

```text
p
e
n
```

Two helpers for characters: `Character.toLowerCase(c)` gives the small letter, and `"aeiou".indexOf(c)` gives
the position of `c` in `"aeiou"`, or `-1` when it is not there. So `"aeiou".indexOf(c) >= 0` asks "is `c` a
vowel?".
:::

:::step{type=task task=count_vowels title="Your turn: count the vowels"}
In `Loops.java`, make `countVowels(text)` give back how many vowels (a, e, i, o, u) the text has, in either case.

`countVowels("Hello World")` gives `3`, and `countVowels("The Hobbit")` gives `3`. Uppercase vowels count too:
`countVowels("AEIOU")` gives `5`.

Loop over the characters, lower each one, and count the vowels: a counter, a loop and an `if`.

```bash run
cd /workspace/05-loops && java Loops.java
```

Then press **Check**.

The usual slips: comparing a `char` with a string in double quotes, `c == "a"`, which `javac` refuses with
`error: bad operand types for binary operator '=='` (we tried it; a `char` is written `'a'`); or forgetting
`Character.toLowerCase`, so `AEIOU` counts as 0.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which positions does `for (int i = 0; i < 4; i++)` visit?
:::
- [ ] 1, 2, 3, 4
- [x] 0, 1, 2, 3
- [ ] 0, 1, 2, 3, 4
:::explain
It starts at 0 and keeps going while `i < 4`, so 4 itself is never reached.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `ArrayIndexOutOfBoundsException: Index 3 out of bounds for length 3` mean?
:::
- [ ] The array is empty
- [x] The code asked for position 3, but positions only go 0 to 2
- [ ] The array has 4 items
:::explain
An array of length 3 has positions 0, 1 and 2. Asking for 3 is one too far: usually a `<=` that should be `<`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Where should `int total = 0;` go in a running-total loop?
:::
- [x] Before the loop
- [ ] Inside the loop
- [ ] After the loop
:::explain
Inside the loop it would reset to 0 on every lap. Set up the answer once, before the loop.
:::
:::

:::step{type=deep-dive title="Go deeper: while, break and continue"}
**while.** A `while` loop repeats as long as a condition is true, which suits "I do not know how many laps". How
many months of saving ₹300 to reach ₹1,000?

```java
int saved = 0;
int months = 0;
while (saved < 1000) {
    saved = saved + 300;
    months++;
}
System.out.println(months + " " + saved);    // 4 1200
```

**break and continue.** `break` jumps out of a loop at once; `continue` skips to the next lap.

**The loop that never ends.** If a `while` condition never becomes false, the program runs forever. Press
**Ctrl+C** in the terminal to stop it.

**Streams.** In chapter 14 you will write many loops in a shorter style: `IntStream.rangeClosed(1, n).sum()` adds 1
to n in one line (`rangeClosed` includes n; we checked `IntStream.rangeClosed(1, 5).sum()` is 15). Knowing the loop first means you will understand what that line does.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Loop over every item with `for (int x : array)`, and count with `for (int i = 0; i < n; i++)`.
- Build an answer with the before / inside / after pattern: running totals and counters.
- Explain `ArrayIndexOutOfBoundsException` and the off-by-one mistake that causes it.
- Loop over a string's characters with `toCharArray()`, and repeat with `while`.

:::photo{src="/lesson-images/java/java-05-sketch.webp" alt="Sketchnote: Loops. A loop runs its body again and again, once for each item, or while a condition stays true. Flow: int total = 0, for i from 1 while i <= n, total = total + i, i++ and check again, return total. Remember: array positions start at 0; i < length stops in time, i <= length crashes; set up the answer before the loop; a char is written with single quotes, a String with double quotes." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 6: finding bugs. Two of Shelf's methods compile and run, and give wrong answers anyway.
:::
