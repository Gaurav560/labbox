:::step{type=story title="What does Java print when you print a whole array?"}
Make an array of four numbers and print it with `println`. You would expect the numbers. Java prints something
like this:

```text
[I@4e50df2e
```

A bracket, an `I`, an `@` and a code that changes every time you run it. What is Java telling you? By the end of
this chapter you will read that line like a sentence, and you will know the one-word fix.

Shelf's library has rows of shelves, and a row of numbered slots is exactly what an **array** is.

:::mission
Write `max`, which finds the biggest number in an array (and refuses an empty one), and `reversed`, which gives
back a new array in reverse order without touching the original.
:::
:::

:::step{type=concept title="An array: a fixed row of numbered slots" file="08-arrays/Shelves.java" line="6-10"}
Open `Shelves.java`:

```java
int[] books = {12, 30, 7, 25};
System.out.println(books.length);
System.out.println(books[0] + " " + books[3]);
books[2] = 9;
System.out.println(Arrays.toString(books));
```

- `int[]` is the type "array of int". `{12, 30, 7, 25}` creates one with four slots.
- `books.length` is the number of slots: 4. (No brackets: on an array, `length` is a field, not a method.)
- `books[0]` is the first slot, `books[3]` the last: positions run from 0 to `length - 1`.
- `books[2] = 9;` replaces the value in one slot.

The big difference from a Python list: an array's **size is fixed** when it is created. You can change what is in
a slot, but you can never add a fifth slot to this array. (Chapter 11's `ArrayList` can grow.)

`new int[3]` makes an array of three slots without values, and Java fills them with a default: `0` for numbers,
`false` for booleans, `null` for objects such as strings.

:::picture{name="egg-box"}
An array is an egg box: a fixed number of numbered slots, decided when the box is made.
:::
:::

:::step{type=try title="Fill the shelves" file="08-arrays/Shelves.java" line="6-13"}
Run it:

```bash run
cd /workspace/08-arrays && java Shelves.java
```

```text
4
12 25
[12, 30, 9, 25]
[0, 0, 0] [null, null]
```

Now the mystery from the start: printing `books` directly gives `[I@` and a code, because an array does not know
how to describe itself. `[I` is Java's internal name for "array of int", and the code after `@` identifies this
particular object. `Arrays.toString(books)` is the fix: it prints the values. Remember `import java.util.Arrays;`
at the top of the file, which is how you use a class from Java's library (chapter 16 explains imports).
:::

:::step{type=example title="Worked example: the smallest number"}
Your first task finds the biggest number. Here is the smallest, with the same shape, and one new idea:

```java
static int min(int[] numbers) {
    if (numbers.length == 0) {
        throw new IllegalArgumentException("min of an empty array");
    }
    int best = numbers[0];
    for (int n : numbers) {
        if (n < best) {
            best = n;
        }
    }
    return best;
}
```

1. An empty array has no smallest number, and returning 0 would be a lie. So the method **throws an exception**:
   `throw` stops the method at once, and the caller sees
   `IllegalArgumentException: min of an empty array`. Chapter 13 covers exceptions properly; for now,
   `throw new IllegalArgumentException("message")` means "this input is not allowed".
2. Start `best` with the first real value, not 0: with negative numbers, 0 would be wrong.
3. Keep any value that beats the best so far.
:::

:::step{type=task task=array_max title="Your turn: the biggest number"}
Open `ArrayTools.java` and make `max(numbers)` give back the biggest number. An empty array throws an
`IllegalArgumentException`.

`max(new int[] {3, 9, 2})` gives `9`, `max(new int[] {-5, -2, -9})` gives `-2`, and `max(new int[] {})` throws.

```bash run
cd /workspace/08-arrays && java ArrayTools.java
```

Then press **Check**.
:::

:::step{type=concept title="Two names, one array" file="08-arrays/SameArray.java" line="6-9"}
Open `SameArray.java`:

```java
int[] mine = {1, 2, 3};
int[] yours = mine;
yours[0] = 99;
System.out.println(Arrays.toString(mine));
```

Before you run it: what does it print? `[1, 2, 3]`?

```bash run
cd /workspace/08-arrays && java SameArray.java
```

```text
[99, 2, 3]
```

`int[] yours = mine;` does not copy the array. An array is an object, and the variable holds a **reference** to it
(the same idea as strings in chapter 7). Now two names refer to **one** array, so changing it through `yours` shows
through `mine`. That `[I@...` code you saw is, in a way, the identity of that one object.

To get a real, separate copy, ask for one: `int[] copy = Arrays.copyOf(mine, mine.length);`, or build a new array
and fill it yourself. That matters a lot in methods: a method that changes the array it was given changes the
caller's array too.
:::

:::step{type=predict title="Guess first"}
:::question
A method does `Arrays.sort(numbers); return numbers;`. After calling it, what has happened to the caller's array?
:::
- [ ] Nothing: the method had its own copy
- [x] It is now sorted: there was only ever one array
- [ ] It is empty
:::explain
The method received a reference to the caller's array and sorted that very array in place. To leave the caller's
data alone, make a new array first.
:::
:::

:::step{type=task task=reversed title="Your turn: a reversed copy"}
In `ArrayTools.java`, make `reversed(numbers)` give back a **new** array with the numbers in reverse order. The
array it was given must not change.

`reversed(new int[] {1, 2, 3})` gives `[3, 2, 1]`, and an empty array gives an empty array.

1. Create a new array of the same length: `new int[numbers.length]`.
2. Loop over the positions and fill it from the other end: the last value goes into position 0.

```bash run
cd /workspace/08-arrays && java ArrayTools.java
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `new int[4]` contain?
:::
- [ ] Nothing: it has 0 slots
- [x] Four slots, each 0
- [ ] Four slots, each `null`
:::explain
Number arrays start filled with 0. Arrays of objects, like `String[]`, start with `null`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
How do you print the values of an `int[] a`?
:::
- [ ] `System.out.println(a)`
- [x] `System.out.println(Arrays.toString(a))`
- [ ] `System.out.println(a.length)`
:::explain
Printing the array itself shows its type and identity (`[I@...`). `Arrays.toString` shows the values.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
After `int[] b = a;` and `b[0] = 5;`, what is `a[0]`?
:::
- [x] `5`
- [ ] whatever it was before
:::explain
`b = a` gives the same array a second name. There is only one array.
:::
:::

:::step{type=deep-dive title="Go deeper: 2D arrays, Arrays helpers and varargs"}
**Arrays of arrays.** `int[][] grid = {{1, 2}, {3, 4}};` is a table: `grid[1][0]` is `3` (row 1, then column 0).
Shelf could store books per shelf per floor this way.

**The Arrays helpers.** `Arrays.sort(a)` sorts in place, `Arrays.copyOf(a, n)` copies, `Arrays.equals(a, b)`
compares values (because `a == b` compares identity, as with strings), and `Arrays.fill(a, 7)` sets every slot.

**Varargs.** A parameter written `int... numbers` lets callers pass any number of values, `sum(1, 2, 3)`, and
inside the method `numbers` is a plain `int[]`. `String.join("-", "a", "b", "c")` from chapter 7 works this way.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Create arrays with values or with `new int[n]`, and read or replace slots by position.
- Remember an array's size is fixed, and that `length` has no brackets.
- Print values with `Arrays.toString`, and explain what `[I@...` means.
- Avoid changing a caller's array: two names can share one array, so copy when you need your own.

:::photo{src="/lesson-images/java/java-08-notes.webp" alt="Handwritten notes about Java arrays: int array with numbered slots from 0, fixed size, Arrays.toString to print, two names one array, copy before you change" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 9: classes and objects, so Shelf can describe its own things, like a Book.
:::
