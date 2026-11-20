:::step{type=story title="Why loops"}
Working out one student's grade is easy. Working out forty, or adding up a month of expenses, means
doing the same steps again and again. A **loop** repeats steps for you, so ten lines of code can
handle ten thousand values.

:::mission
In `loops/Loops.java`, add up the numbers from 1 to n, and count the vowels in a piece of text.
:::
:::

:::step{type=concept title="Repeating with a counter"}
Picture counting laps on a running track: you start at lap 1, run, add one to your count, and stop
after the last lap.

Java's classic `for` loop does exactly that:

```java
for (int i = 1; i <= 5; i++) {
    System.out.println("lap " + i);
}
```

It has three parts in the brackets:

1. `int i = 1` **start**: make a counter `i` and set it to 1.
2. `i <= 5` **keep going while** this is true.
3. `i++` **after each round**, add one to `i`.

So the block runs with `i` as 1, 2, 3, 4 and 5, then stops.
:::

:::step{type=concept title="A running total"}
To add things up, keep a **running total** outside the loop and grow it inside:

```java
int total = 0;
for (int i = 1; i <= 3; i++) {
    total = total + i;      // or: total += i
}
// round 1: total 1, round 2: total 3, round 3: total 6
```

The total starts at 0 **before** the loop, so it survives from one round to the next. If you created
it inside the loop, it would start again at 0 every round.
:::

:::step{type=example title="Worked example: count the passing marks"}
Counting is a running total that adds one at a time:

```java
public static int countPassed(int[] marks) {
    int count = 0;              // 1. start at zero
    for (int m : marks) {       // 2. each mark
        if (m >= 33) {          // 3. does it count?
            count++;            // 4. add one
        }
    }
    return count;               // 5. the answer
}
```

`for (int m : marks)` is the **for-each** loop: it visits every item, calling it `m`, without a
counter. Change the condition in step 3 and the same lines count anything you like.
:::

:::step{type=predict title="Guess first"}
:::question
How many times does this print?

```java
for (int i = 1; i <= 5; i += 2) {
    System.out.println(i);
}
```
:::
- [ ] 5 times
- [x] 3 times (1, 3, 5)
- [ ] 2 times (1, 3)
- [ ] Forever
:::explain
`i` starts at 1 and grows by 2: 1, 3, 5, then 7, which fails `i <= 5`. Reading the three parts one at
a time is the surest way to see how many rounds a loop makes.
:::
:::

:::step{type=try title="Watch a running total grow"}
```bash run
cat > /tmp/Total.java <<'JAVA'
public class Total {
    public static void main(String[] args) {
        int total = 0;
        for (int i = 1; i <= 5; i++) {
            total += i;
            System.out.println("after " + i + " the total is " + total);
        }
    }
}
JAVA
java /tmp/Total.java
```
:::

:::step{type=task task=sum_to title="Warm-up: add up 1 to n"}
In `loops/Loops.java`, make `sumTo(n)` return `1 + 2 + ... + n`.

- `sumTo(5)` returns `15`
- `sumTo(100)` returns `5050`
- `sumTo(0)` and `sumTo(-3)` return `0` (the loop simply never runs)
:::

:::step{type=concept title="Looking at text one character at a time"}
A String is a row of characters. `toCharArray()` turns it into an array you can loop over, and a
`char` is a single character in single quotes:

```java
for (char c : "Hi!".toCharArray()) {
    System.out.println(c);      // H, then i, then !
}
Character.toLowerCase('E')      // 'e'
"aeiou".indexOf('o')            // 3: its position
"aeiou".indexOf('x')            // -1: not there
```

`indexOf` returning `-1` is a handy way to ask "is this character one of these?".
:::

:::step{type=task task=count_vowels title="Count the vowels"}
In `loops/Loops.java`, make `countVowels(text)` count `a`, `e`, `i`, `o` and `u`, upper or lower case.

- `countVowels("Hello World")` returns `3`
- `countVowels("AEIOU")` returns `5`
- `countVowels("rhythm")` returns `0`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `total` after this code?

```java
int total = 0;
for (int i = 1; i <= 3; i++) total += 10;
```
:::
- [ ] `10`
- [x] `30`
- [ ] `6`
- [ ] `0`
:::explain
The loop runs three times and adds 10 each time: 30.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `'A' == 'a'` give in Java?
:::
- [ ] `true`
- [x] `false`
- [ ] It does not compile
- [ ] `null`
:::explain
Upper and lower case are different characters. That is why `countVowels` lowers each character first.
:::
:::

:::step{type=deep-dive title="while loops and the loop you must not write"}
A `while` loop repeats as long as a condition holds, which suits work with no fixed count:

```java
int n = 1;
while (n < 100) {
    n = n * 2;     // 1, 2, 4 ... stops at 128
}
```

If the condition never becomes false, the loop runs **forever** and the program hangs. LabBox checks
have a time limit for exactly this reason. Inside any loop, `break` leaves it early and `continue` skips
to the next round.
:::

:::step{type=recap}
- `for (start; keep going while; after each round)` repeats with a counter.
- `for (Type x : items)` visits every item; no counter needed.
- Keep running totals and counters **outside** the loop.
- `toCharArray()` and `char` look at text one character at a time.
:::
