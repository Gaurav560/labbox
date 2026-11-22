:::step{type=story title="A program that runs is not a program that is right"}
In 1947, the team running the Harvard Mark II computer found it giving wrong answers. Inside one of its relays
they found the cause: a real moth. They taped it into the logbook with the note "First actual case of bug being
found." That page is now in the Smithsonian museum.

:::photo{src="/lesson-images/python/first-computer-bug-1947.webp" alt="A page of the Harvard Mark II logbook from 9 September 1947, with a moth taped to it and the note First actual case of bug being found" credit="U.S. Naval History and Heritage Command" license="Public domain" source="https://commons.wikimedia.org/wiki/File:First_Computer_Bug,_1947.jpg"}
The real page, 9 September 1947: the moth is still taped to it.
:::

Java catches many mistakes before your program even starts (chapter 2 showed how). But no compiler can catch
this kind: Shelf's `totalFines` compiles perfectly, runs without a crash, and says ₹50 when the fines add up to
₹60. Today you learn to hunt both kinds: the loud ones that crash, and the quiet ones that just lie.

:::mission
Read a real stack trace, then use println and jshell to find and fix two bugs that never crash.
:::
:::

:::step{type=try title="Make a program crash" file="06-finding-bugs/Report.java" line="3-18"}
Open `Report.java`. It prints the average fine for each day:

```java
static int average(int[] fines) {
    int total = 0;
    for (int fine : fines) {
        total += fine;
    }
    return total / fines.length;
}

static String summary(String day, int[] fines) {
    return day + ": average fine " + average(fines) + " rupees";
}
```

`total += fine` is short for `total = total + fine`. Run it:

```bash run
cd /workspace/06-finding-bugs && java Report.java
```

```text
Monday: average fine 20 rupees
Exception in thread "main" java.lang.ArithmeticException: / by zero
	at Report.average(Report.java:8)
	at Report.summary(Report.java:12)
	at Report.main(Report.java:17)
```

Monday worked; Tuesday, with no fines at all, crashed. This is a **stack trace**: the list of method calls that
were waiting for an answer when the exception happened. And here is a curious difference: Python prints its
traceback with the newest call at the **bottom**; Java prints it with the newest call at the **top**.
:::

:::step{type=concept title="Read a stack trace from the top"}
Press Play and read this one the way Java developers do:

:::diagram{name="java-stack-trace"}
The first line says what went wrong; the first at line says where; the lines below say how the program got there.
:::

So the story, told in the order things happened, is: `main` (line 17) called `summary("Tuesday", ...)`, which
(line 12) called `average` with an empty array, which (line 8) divided `0 / 0`. Integer division by zero has no
answer, so Java threw an `ArithmeticException`.

The fix is a **decision**: what should the average of no fines be? For Shelf, 0 makes sense. With chapter 4's
tools, that is one `if` at the top of `average`:

```java
if (fines.length == 0) {
    return 0;
}
```

Try adding it and run the file again: Tuesday now says `average fine 0 rupees`.

In big programs, a stack trace can be 50 lines long, most of them inside Java's own libraries (`java.base/...`).
Look for the **first line that names your own class**: that is where to start.
:::

:::step{type=try title="Now the quiet kind" file="06-finding-bugs/Fines.java" line="4-21"}
Open `Fines.java` and run it:

```bash run
cd /workspace/06-finding-bugs && java Fines.java
```

```text
50
true
```

No exception, no error. But the fines 10 + 20 + 30 are **60**, not 50. And `canBorrow(5, 5)` says `true`: a
member who already has 5 books, with a limit of 5, is allowed one more? That breaks the library's rule.

The compiler checked every type and found nothing wrong, because nothing *is* wrong with the types. The logic is
wrong. Time for detective work.
:::

:::step{type=example title="Worked example: make the invisible visible"}
A bug lives in values you cannot see: the variables inside a method while it runs. The simplest debugging tool
in the world is still `println`: print what you want to see, run, compare with what you expected, then remove it.

Suppose you doubt a loop that doubles every price. Add one line inside it:

```java
static int doubledTotal(int[] prices) {
    int total = 0;
    for (int i = 0; i < prices.length; i++) {
        System.out.println("i=" + i + " price=" + prices[i] + " total so far=" + total);
        total = total + prices[i] * 2;
    }
    return total;
}
```

With `{10, 20}`, it prints `i=0 price=10 total so far=0`, then `i=1 price=20 total so far=20`. Each line shows
one lap. Compare them with what you expected, lap by lap; the first lap that differs points at the bug. Label your
values (`"i=" + i`), or a screen full of bare numbers becomes a puzzle of its own.
:::

:::step{type=predict title="Guess first"}
:::question
`totalFines` loops with `for (int i = 1; i < fines.length; i++)`. For `{10, 20, 30}`, which fines does it add?
:::
- [ ] 10, 20 and 30
- [x] 20 and 30
- [ ] 10 and 20
:::explain
`i` starts at 1, so position 0, the first fine (10), is never visited: 20 + 30 = 50. Positions start at 0, as
chapter 5 said.
:::
:::

:::step{type=task task=fix_total_fines title="Your turn: the total that forgets"}
Fix `totalFines` in `Fines.java`, so `totalFines(new int[] {10, 20, 30})` gives `60`.

1. Prove it first: add `System.out.println("i=" + i + " fine=" + fines[i]);` inside the loop and run
   `java Fines.java`. Which positions are visited?
2. Find what decides where the loop starts, and fix it.
3. Remove your `println` and run it again: `60`.

An empty array must still give `0`. Then press **Check**.
:::

:::step{type=concept title="jshell: call one method by hand"}
`println` means editing the file and running the whole program. Sometimes you just want to **ask a method a
question**. Java's interactive shell, **jshell**, lets you do exactly that. Start it, load the file, and call:

```bash run
cd /workspace/06-finding-bugs && jshell
```

```text
jshell> /open Fines.java
jshell> Fines.totalFines(new int[] {10, 20, 30})
$2 ==> 50
jshell> Fines.totalFines(new int[] {10})
$3 ==> 0
jshell> Fines.canBorrow(5, 5)
$4 ==> true
jshell> /exit
```

Look at the second question: a single fine of 10 gives **0**. That is the kind of small, sharp test that makes a
bug obvious, and in jshell it takes two seconds. `$3 ==> 0` means "the answer, which jshell saved in a variable
called `$3`, is 0".

The very first time you start jshell it may print a short `INFO: Created user preferences directory.` line: Java
setting up its settings folder. It is harmless.
:::

:::step{type=task task=fix_can_borrow title="Your turn: at the limit means no more"}
Fix `canBorrow` in `Fines.java`. A member may borrow while they have **fewer** books than the limit; at the limit,
no more:

- `canBorrow(4, 5)` gives `true` (one slot of room left),
- `canBorrow(5, 5)` gives `false` (no room left),
- `canBorrow(0, 0)` gives `false`.

1. Look inside: print `room` before the `return`, or try the values in jshell.
2. What is `room` exactly at the limit? Is that enough room to borrow?
3. Fix the comparison, remove your debugging line, and run `java Fines.java`: `60`, then `false`.

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In a Java stack trace, which line usually tells you where the problem happened in **your** code?
:::
- [x] The first `at` line that names your own class
- [ ] The last line
- [ ] The line that starts with `Exception in thread`
:::explain
The first line says what went wrong; the `at` lines are listed newest first. The first one that is in your own
class is where to look.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A method compiles, runs, and returns a wrong number. Which tool helps first?
:::
- [ ] Reading the compile errors
- [x] Printing the values inside it, or calling it with a small input in jshell
- [ ] Adding more code
:::explain
There is no error to read. Make the hidden values visible, and test with tiny inputs where you know the answer.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `$3 ==> 0` mean in jshell?
:::
- [ ] Error number 3
- [x] The answer is 0, saved in a variable called `$3`
- [ ] Three zeros
:::explain
jshell shows each answer and stores it in `$1`, `$2`, ... so you can use it again.
:::
:::

:::step{type=deep-dive title="Go deeper: debuggers, assertions and logs"}
**A real debugger.** Big Java editors (IntelliJ IDEA, Eclipse, VS Code with Java support) let you click next to a
line to set a **breakpoint**, run the program, and pause there to look at every variable. It is `println` without
editing the file. Java's own command-line debugger is called `jdb`.

**Assertions.** `assert total >= 0 : "total can never be negative";` stops the program when something impossible
happens. Java ignores assertions unless you run with `java -ea`, so teams mostly use them in tests (chapter 17).

**Reproduce it small.** The jshell session above is the professional habit: find the smallest input that shows
the bug (`{10}` instead of a whole month), and the cause is usually obvious.

**Off-by-one.** Starting at 1 instead of 0, or `<=` instead of `<`: the same two mistakes, in every language, every
day. You have now fixed both.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Tell a compile error, an exception (a loud crash) and a logic bug (a quiet wrong answer) apart.
- Read a Java stack trace: what went wrong first, then the `at` lines, newest first.
- Make hidden values visible with labelled `println`s.
- Ask a method questions directly in jshell with `/open` and a call.

:::photo{src="/lesson-images/java/java-06-notes.webp" alt="Handwritten notes about finding bugs in Java: stack traces read from the top, find your own class, println with labels, jshell /open, off by one" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 1. Shelf can talk, count, decide and loop, and you can fix it when it misbehaves. Next,
Part 2: working with data, starting with strings.
:::
