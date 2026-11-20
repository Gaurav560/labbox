:::step{type=story title="Why arrays"}
A class has forty marks; a week has seven temperatures. Making forty separate variables would be
madness. An **array** keeps many values of the same type under one name, each in its own numbered
slot.

:::mission
In `arrays/ArrayTools.java`, find the biggest number in an array, and return a reversed copy without
touching the original.
:::
:::

:::step{type=concept title="A row of numbered slots"}
Picture an egg tray with a fixed number of cups, numbered from **0**. An array is that tray:

```java
int[] marks = {72, 45, 90};     // three slots
marks[0]           // 72: the first slot
marks[2]           // 90: the last slot
marks.length       // 3: how many slots
marks[1] = 50;     // put 50 in slot 1
```

- `int[]` means "an array of `int`".
- The size is fixed when the array is made: a tray of 3 cups always has 3.
- The last slot is `length - 1`, because counting starts at 0.

:::picture{name="egg-box"}
An array is a row of numbered slots, starting at 0.
:::
:::

:::step{type=concept title="Visiting every slot"}
Two loops fit arrays. When you only need the values, use for-each:

```java
for (int m : marks) {
    System.out.println(m);
}
```

When you need the **position** too, use the counting loop:

```java
for (int i = 0; i < marks.length; i++) {
    System.out.println("slot " + i + " holds " + marks[i]);
}
```

:::mistake
`marks[marks.length]` is one past the end. Java stops with an
`ArrayIndexOutOfBoundsException`. The last slot is `marks.length - 1`.
:::
:::

:::step{type=example title="Worked example: the smallest mark"}
"Best so far" is the pattern for finding a minimum or maximum:

```java
public static int min(int[] numbers) {
    int best = numbers[0];          // 1. start with the first
    for (int n : numbers) {         // 2. look at each
        if (n < best) {             // 3. smaller?
            best = n;               // 4. keep it
        }
    }
    return best;
}
```

1. Start with the **first** value, not 0: with all-negative numbers, 0 would win wrongly.
2. Compare each value with the best so far, and keep the winner.

`max` is the mirror image. And an empty array has no first value: decide what to do about that.

:::trace{title="min({72, 45, 90, 38})"}
| n | n < best? | best | note |
|---|---|---|---|
|  |  | 72 | Start with the first value, not 0. |
| 72 | no | 72 | The first value is compared with itself: no change. |
| 45 | yes | 45 | 45 is smaller: keep it. |
| 90 | no | 45 | 90 is not smaller: best stays 45. |
| 38 | yes | 38 | 38 is smaller: the loop ends and returns 38. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What happens here?

```java
int[] a = {1, 2, 3};
System.out.println(a[3]);
```
:::
- [ ] It prints `3`
- [ ] It prints `0`
- [x] It stops with an ArrayIndexOutOfBoundsException
- [ ] It does not compile
:::explain
The slots are 0, 1 and 2, so `a[3]` does not exist. Java checks every array access and stops with a
clear exception rather than reading random memory, one of the protections C did not have.
:::
:::

:::step{type=try title="Arrays in action"}
```bash run
cat > /tmp/Arr.java <<'JAVA'
import java.util.Arrays;

public class Arr {
    public static void main(String[] args) {
        int[] marks = {72, 45, 90};
        System.out.println(Arrays.toString(marks) + " has " + marks.length + " slots");
        marks[1] = 50;
        System.out.println(Arrays.toString(marks));
    }
}
JAVA
java /tmp/Arr.java
```

`Arrays.toString` prints an array nicely; printing the array directly would show something like
`[I@1b6d3586`.
:::

:::step{type=task task=array_max title="Warm-up: the biggest number"}
In `arrays/ArrayTools.java`, make `max(numbers)` return the biggest number.

- `max({3, 9, 2})` returns `9`
- `max({-5, -2, -9})` returns `-2`
- an empty array has no biggest number: throw an `IllegalArgumentException`:
  `throw new IllegalArgumentException("max of an empty array");`
:::

:::step{type=concept title="Making a new array"}
To build a result without touching the input, make a **new** array of the right size and fill it:

```java
int[] doubled = new int[numbers.length];   // all slots start at 0
for (int i = 0; i < numbers.length; i++) {
    doubled[i] = numbers[i] * 2;
}
```

The caller's array is untouched, which matters: other code may still be using it.
:::

:::step{type=task task=reversed title="A reversed copy"}
In `arrays/ArrayTools.java`, make `reversed(numbers)` return a **new** array with the numbers in reverse
order, leaving the original alone.

- `reversed({1, 2, 3, 4})` returns `{4, 3, 2, 1}`
- after the call, the original is still `{1, 2, 3, 4}`

Slot `i` of the result holds slot `length - 1 - i` of the input.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is the index of the last slot of `int[] a = new int[5];`?
:::
- [ ] `5`
- [x] `4`
- [ ] `6`
- [ ] `-1`
:::explain
Five slots are numbered 0 to 4. The last one is always `length - 1`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What do the slots of `new int[3]` hold before you fill them?
:::
- [ ] Random numbers
- [x] `0`
- [ ] `null`
- [ ] Nothing: reading them is an error
:::explain
Java fills new arrays with a default: `0` for numbers, `false` for booleans and `null` for objects.
No garbage values, ever.
:::
:::

:::step{type=deep-dive title="Fixed size, and what replaced it in everyday code"}
An array's size is fixed when it is made, which makes it fast and simple but inflexible. Most everyday
Java code uses an `ArrayList` instead (chapter 9), which grows as you add items and is built on an array
inside.

`int[] b = a;` does **not** copy the array: both names now point to the same slots, so changing `b[0]`
changes `a[0]` too. To copy, use `a.clone()` or `Arrays.copyOf(a, a.length)`. The `java.util.Arrays`
class also has `sort`, `fill` and `equals`.
:::

:::step{type=recap}
- An array is a fixed row of numbered slots: `a[0]` to `a[a.length - 1]`.
- for-each visits values; the counting loop gives positions too.
- "Best so far" starts from the first value, not from 0.
- Build results in a new array; leave the caller's array alone.
:::
