:::step{type=story title="A program that runs is not a program that is right"}
In 1947, the team running the Harvard Mark II computer found it giving wrong answers. They searched, and inside
one of its relays they found the cause: a real moth, stuck between the contacts. They taped it into the logbook
with the note "First actual case of bug being found." That page is now in the Smithsonian museum.

Engineers had called problems "bugs" long before that day, but the moth made the word famous. Today your bugs
will not have wings. They will be quieter, and in a way sneakier: Pocket's `daily_total` runs perfectly, no
error, no crash, and says you spent ₹180 when you spent ₹300.

A crash shouts at you. A wrong answer whispers. Today you learn to hear both.

:::mission
Read a real traceback from the bottom up, then use print and the debugger to find and fix two bugs that never
crash.
:::
:::

:::step{type=concept title="Two kinds of trouble"}
So far, every mistake you made was loud: Python stopped and printed an error. There are really two kinds of
trouble in a program:

- **Errors** (also called **exceptions**): Python cannot go on, so it stops and prints a **traceback**. Annoying,
  but helpful: it tells you where.
- **Bugs**: the program runs to the end and gives a **wrong answer**. Nothing tells you where. You only know
  something is wrong because you know what the right answer should be.

Professional developers spend a large part of their day on both. The good news: finding them is a skill with
clear steps, not magic, and you are going to practise both kinds in this chapter.
:::

:::step{type=try title="Make a program crash" file="06-finding-bugs/report.py" line="2-11"}
Open `report.py`. It prints a short summary of each day's spending:

```python
def average(amounts):
    return sum(amounts) / len(amounts)


def summary(day, amounts):
    return f"{day}: average {average(amounts):.2f}"


print(summary("Monday", [120, 80, 100]))
print(summary("Tuesday", []))
```

Run it:

```bash run
cd /workspace/06-finding-bugs && python3 report.py
```

```text
Monday: average 100.00
Traceback (most recent call last):
  File "/workspace/06-finding-bugs/report.py", line 11, in <module>
    print(summary("Tuesday", []))
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/06-finding-bugs/report.py", line 7, in summary
    return f"{day}: average {average(amounts):.2f}"
                             ^^^^^^^^^^^^^^^^
  File "/workspace/06-finding-bugs/report.py", line 3, in average
    return sum(amounts) / len(amounts)
           ~~~~~~~~~~~~~^~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

Monday worked. Tuesday crashed. This traceback is longer than the ones in chapter 1, because the error happened
inside a function that was called by another function. Don't panic: it has a shape, and once you see the shape,
every traceback becomes easy.
:::

:::step{type=concept title="Read a traceback from the bottom up"}
A traceback is the list of function calls that were still **waiting for an answer** when the error happened,
oldest at the top, newest at the bottom. Each call is two or three lines: the file and line number, the code on
that line, and marks (`^^^` or `~~~^~~~`) under the exact part that failed.

Experienced developers read it **from the bottom up**. Press Play and read it with them:

:::diagram{name="traceback-bottom-up"}
Bottom line first (what), then the frame above it (where), then up the calls (why).
:::

So the story, told from the top, is: the main program called `summary("Tuesday", [])`, which called
`average([])`, which tried `sum([]) / len([])`, which is `0 / 0`. Dividing by zero has no answer, so Python
stopped.

Notice step 5. The crash happens in `average`, but the real question is a **decision**: what *should* the
average of no amounts be? For Pocket, `0.0` is sensible ("you spent nothing"). With chapter 4's tools, that is
one `if` at the top of `average`:

```python
def average(amounts):
    if not amounts:
        return 0.0
    return sum(amounts) / len(amounts)
```

`not amounts` is `True` for an empty list (chapter 4's Go deeper called this truthiness). Try adding it to
`report.py` and run it again: Tuesday now says `average 0.00`.
:::

:::step{type=try title="Now the quiet kind" file="06-finding-bugs/spending.py" line="5-19"}
Open `spending.py`. Two of Pocket's functions live here, and at the bottom, two lines that call them. Run it:

```bash run
cd /workspace/06-finding-bugs && python3 spending.py
```

```text
180
True
```

No traceback. No error. Everything *looks* fine. But the first line should be `300` (120 + 80 + 100), and the
second asks "is spending ₹300 + ₹200 over a budget of ₹500?" Exactly ₹500 is **on** budget, not over, so it
should say `False`.

Two wrong answers, and Python cannot help you, because as far as Python knows, the program did exactly what you
wrote. This is where your detective work starts.
:::

:::step{type=example title="Worked example: make the invisible visible"}
The bug is in values you cannot see: the variables inside the function while it runs. So the first, simplest
and most used debugging tool in the world is... `print`. Put a `print` where you want to look, run, read, and
remove it afterwards.

Imagine you doubt a function that doubles the total of some prices. Add one `print` inside the loop:

```python
def doubled_total(prices):
    total = 0
    for price in prices:
        print("price", price, "total so far", total)
        total = total + price
    return total * 2
```

Running it with `[10, 20]` prints one line per lap: `price 10 total so far 0`, then `price 20 total so far 10`.
Now compare what you *see* with what you *expected*, lap by lap. Here they match, so this loop is fine. When they
differ, the lap where they first differ points at the line with the bug.

Python has a lovely shortcut for this. Put `=` after a name inside an f-string, and it prints the name **and**
the value:

```python
left = 0
print(f"{left=}")    # shows: left=0
```

That saves typing labels, and with several variables, `print(f"{i=} {total=}")` shows them all at once.
:::

:::step{type=predict title="Guess first"}
:::question
`daily_total` loops with `for i in range(1, len(amounts)):`. For `[120, 80, 100]`, what is `i` on the
**first** lap?
:::
- [ ] `0`
- [x] `1`
- [ ] `120`
:::explain
`range(1, 3)` gives `1, 2`. It starts at 1, so position 0, the first amount, is never visited. Chapter 5 said
positions start at 0: this loop forgot.
:::
:::

:::step{type=task task=fix_daily_total title="Your turn: the total that forgets"}
Fix `daily_total` in `spending.py`, so `daily_total([120, 80, 100])` gives `300`.

1. Prove it first: add `print(i, amounts[i])` inside the loop and run `python3 spending.py`. Which amounts are
   added?
2. Find the line that decides which positions the loop visits, and fix it.
3. Remove your `print`, run it again, and see `300`.

The empty list should still give `0`. Then press **Check**.
:::

:::step{type=concept title="The debugger: pause the program and look around"}
`print` is great, but sometimes you want to **pause** the program in the middle and ask questions. That is what
a **debugger** does, and Python has one built in, called **pdb**.

Put this line where you want the program to pause:

```python
breakpoint()
```

When Python reaches it, the program stops and shows a `(Pdb)` prompt. Now you can type commands:

| Command | Does |
|---|---|
| `p name` | print the value of a variable (`p` for print) |
| `n` | run the **n**ext line, then pause again |
| `c` | **c**ontinue until the next breakpoint (or the end) |
| `q` | **q**uit the program |

Here is a real session. With `breakpoint()` placed as the first line inside the loop of the buggy
`daily_total`, and the function called like this:

```bash run
cd /workspace/06-finding-bugs && python3 -c "from spending import daily_total; print(daily_total([120, 80, 100]))"
```

```text
> /workspace/06-finding-bugs/spending.py(10)daily_total()
-> total = total + amounts[i]
(Pdb) p i
1
(Pdb) p amounts[i]
80
(Pdb) p total
0
(Pdb) c
> /workspace/06-finding-bugs/spending.py(10)daily_total()
-> total = total + amounts[i]
(Pdb) p i, total
(2, 80)
(Pdb) c
180
```

The first line tells you where it paused: `spending.py`, line 10, inside `daily_total`, and `->` shows the line
about to run. On the very first pause, `i` is already `1` and the amount is `80`: the `120` was skipped before
anything happened. The debugger let you look *inside* the moment the bug is born.

(If you quit with `q`, Python prints a few extra lines ending in `bdb.BdbQuit`. That is just the debugger
saying goodbye; nothing broke.)
:::

:::step{type=task task=fix_over_budget title="Your turn: on budget is not over budget"}
Fix `over_budget` in `spending.py`, so spending exactly the budget is **not** over:

- `over_budget([300, 200], 500)` gives `False` (₹500 of ₹500: on budget),
- `over_budget([300, 250], 500)` gives `True` (₹50 over).

1. Look inside: add `print(f"{left=}")` just before the `return`, or a `breakpoint()`, and run it.
2. What is `left` when you spend exactly the budget? Is that "over"?
3. Fix the comparison, remove your debugging line, and run `python3 spending.py`: it should print `300` and
   `False`.

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Where do you start reading a traceback?
:::
- [ ] The first line, "Traceback (most recent call last)"
- [x] The last line: the kind of error and its message
- [ ] The middle frame
:::explain
The last line says what went wrong. The frame just above says where; the frames above that say how the program
got there.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A function returns a wrong number, with no error. Which tool helps you **first**?
:::
- [ ] Reading the traceback
- [x] Printing the variables inside it, lap by lap
- [ ] Running it again and hoping
:::explain
There is no traceback for a wrong answer. Make the hidden values visible with `print` (or pause with
`breakpoint()`) and compare them with what you expected.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `print(f"{total=}")` show when `total` is `300`?
:::
- [ ] `300`
- [x] `total=300`
- [ ] `{total=}`
:::explain
The `=` inside the braces prints the variable's name, an equals sign, and its value.
:::
:::

:::step{type=deep-dive title="Go deeper: how professionals hunt bugs"}
**Reproduce it first.** A bug you can trigger on purpose is half fixed. Find the smallest input that shows it:
`daily_total([120, 80])` is easier to think about than a month of data.

**Explain it to a duck.** Many developers keep a rubber duck on the desk and explain their code to it, line by
line, out loud. Surprisingly often, the bug becomes obvious halfway through a sentence. It works with a
colleague too, but the duck never gets bored.

**Split the problem in half.** When you have no idea where the bug is, print a value in the middle of the
program. Right there? The bug is after it. Wrong already? Before it. Halve again. Ten halvings narrow a
thousand lines down to one.

**Assertions.** `assert total >= 0, "total can never be negative"` stops the program with an
`AssertionError` the moment something impossible happens, close to the cause instead of far away. In Part 3
you will write real **tests** that check your functions automatically, so the same bug can never come back
unnoticed.

**Off-by-one errors** like your `range(1, ...)` are so common they have their own name, and their own joke:
"There are two hard things in programming: naming things, cache invalidation, and off-by-one errors."
:::

:::step{type=recap title="What you can do now"}
You can now:

- Tell an error (a crash with a traceback) from a bug (a quiet wrong answer).
- Read a traceback from the bottom up: what went wrong, where, and which calls led there.
- Make hidden values visible with `print` and `print(f"{name=}")`.
- Pause a program with `breakpoint()` and inspect it with `p`, `n`, `c` and `q`.

That is the end of Part 1. Pocket can talk, count, decide and loop, and you can fix it when it misbehaves. Next,
Part 2: working with data, starting with strings.
:::
