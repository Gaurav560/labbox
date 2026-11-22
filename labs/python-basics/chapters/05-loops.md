:::step{type=story title="How would you add up a thousand amounts?"}
Pocket has a month of your spending: maybe 90 amounts. Next year, a thousand. How would you add them up?

You could write `total = a1 + a2 + a3 + ...` with a thousand names. Nobody does that, because nobody needs to.
You write the instruction **once**, and tell Python: "do this for every amount in the list". That is a
**loop**, and it is the reason computers are so good at boring, repetitive work. They never get tired, and they
never skip a line.


Machines have repeated instructions for over two hundred years. A **Jacquard loom** (1804) reads a chain of punched
cards, one card per row of cloth, and weaves the same pattern again and again: a loop, made of wood and string.

:::photo{src="/lesson-images/python/jacquard-loom.webp" alt="A Jacquard loom in a museum, with a long chain of punched cards hanging beside the threads" credit="Stephencdickson" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:A_Jacquard_loom_showing_information_punchcards,_National_Museum_of_Scotland.jpg"}
A Jacquard loom and its punched cards, National Museum of Scotland.
:::
:::mission
Write `count_above`, which counts the big expenses in a list, and `first_negative`, which finds the first
refund.
:::
:::

:::step{type=concept title="for: do it once for every item" file="05-loops/week.py" line="2-7"}
Open `week.py`:

```python
week = [120, 450, 80, 900, 300]

for amount in week:
    print("Spent", amount)

print("Done: that was the whole week.")
```

`week` is a list of five amounts. The loop reads almost like English: "for each amount in week, print it".
Here is exactly what Python does:

1. It takes the first item of the list, `120`, and stores it in the variable `amount`.
2. It runs the indented body with that value: `Spent 120`.
3. It goes back to the top, takes the next item, `450`, stores it in `amount`, and runs the body again.
4. It repeats until there are no items left, then continues after the loop.

Each pass through the body is called an **iteration**. You choose the name of the loop variable; `amount` reads
well here, because each item *is* an amount. The `:` and the indented body work exactly as they do for `if`
and functions.

:::picture{name="running-track"}
A loop is a lap around a track: the same route each time, with a new item on every lap, until the list runs out.
:::
:::

:::step{type=try title="Watch it go round" file="05-loops/week.py" line="4-5"}
Run it:

```bash run
cd /workspace/05-loops && python3 week.py
```

```text
Spent 120
Spent 450
Spent 80
Spent 900
Spent 300
Done: that was the whole week.
```

Two lines of loop, five lines of output. The last line prints once, because it is not indented: it is after
the loop, not inside it.

Now add a sixth amount to the list, say `75`, and run it again. You did not touch the loop, yet it did one more
lap. A loop does not care whether the list has five items or five million.
:::

:::step{type=example title="Worked example: a running total"}
The most useful loop in the world keeps a **running total**. Start with a variable at `0`, then add each item
to it:

```python
def week_total(amounts):
    total = 0
    for amount in amounts:
        total = total + amount
    return total

week_total([120, 450, 80, 900, 300])    # gives back 1850
```

Press Play and watch `total` grow, lap by lap:

:::trace{title="week_total([120, 450, 80, 900, 300])"}
| amount | total | note |
|---|---|---|
|  | 0 | Before the loop: total starts at zero. |
| 120 | 120 | First lap: 0 + 120. |
| 450 | 570 | 120 + 450. |
| 80 | 650 | 570 + 80. |
| 900 | 1550 | 650 + 900. |
| 300 | 1850 | 1550 + 300. |
|  | 1850 | No amounts left: return 1850. |
:::

Three parts, always in this order:

1. **Before** the loop: set up the answer (`total = 0`).
2. **Inside** the loop: update it with one item (`total = total + amount`).
3. **After** the loop: use the finished answer (`return total`).

Counting works the same way, except you add `1` instead of the amount, and only when a condition is true.
:::

:::step{type=predict title="Guess first"}
:::question
Someone moved `total = 0` *inside* the loop by mistake:

```python
total = 0
for amount in [120, 450, 80]:
    total = 0
    total = total + amount
print(total)
```

What does it print?
:::
- [ ] `650`
- [x] `80`
- [ ] `0`
:::explain
On every lap, `total` is reset to 0 and then gets just that one amount. After the last lap it holds only the
last amount, `80`. Setting up the answer belongs **before** the loop, so it happens once.
:::
:::

:::step{type=task task=count_above title="Your turn: count the big expenses"}
Open `loops.py` and make `count_above(amounts, limit)` give back **how many** amounts are greater than the
limit. The limit itself does not count.

`count_above([350, 720, 400, 900], 400)` gives `2` (720 and 900; 400 is not *greater* than 400), and an empty
list gives `0`.

1. Before the loop, start a counter at `0`.
2. Inside, add 1 when an amount is greater than the limit (an `if` inside the loop).
3. After the loop, return the counter.

```bash run
cd /workspace/05-loops && python3 -c "from loops import count_above; print(count_above([350, 720, 400, 900], 400))"
```

Then press **Check**.
:::

:::step{type=concept title="range: counting without a list"}
Sometimes you just want to repeat something a number of times. `range` makes the numbers for you:

```python
for i in range(3):
    print("Hip hip hooray!")
```

That prints the line three times. `range(3)` gives `0, 1, 2`: it starts at **0** and stops **before** 3. That
"stops before" is deliberate, and you will see why in a second.

`range` can also start somewhere else or jump: `range(1, 6)` gives `1, 2, 3, 4, 5`, and `range(0, 10, 3)`
gives `0, 3, 6, 9`.

Here is why it starts at 0. Every item in a list has a **position**, called its **index**, and Python counts
positions from **0**: in `week = [120, 450, 80]`, `week[0]` is `120`, `week[1]` is `450` and `week[2]` is
`80`. So `range(len(week))` gives exactly the right positions, `0, 1, 2`:

```bash run
python3 -c "week = [120, 450, 80]
for i in range(len(week)):
    print(i, week[i])"
```

```text
0 120
1 450
2 80
```

Remember "positions start at 0". It is the cause of one of the most famous bugs in programming, and in
chapter 6 you will hunt one down.
:::

:::step{type=example title="Worked example: stop at the first match"}
Sometimes you do not need every item: you are **searching**, and you can stop as soon as you find what you
want. Here is a function that finds the first expense over ₹1,000:

```python
def first_big(amounts):
    for amount in amounts:
        if amount > 1000:
            return amount
    return None

first_big([120, 1500, 80, 2000])    # gives back 1500
first_big([120, 80])                # gives back None
```

1. The loop looks at each amount in order.
2. The moment one is over 1000, `return amount` ends the **whole function** right there: the loop stops and
   the answer goes back. `2000` is never even looked at.
3. If the loop finishes without finding one, Python reaches the line after the loop: `return None`, Python's
   way of saying "there was nothing to find".

The `return None` is indented to line up with `for`, not with `if`. That position says "after the whole loop",
which is exactly when you know there was no match.
:::

:::step{type=task task=first_negative title="Your turn: find the first refund"}
In Pocket, a refund is a negative amount: money coming back to you. In `loops.py`, make
`first_negative(amounts)` give back the **first** amount below zero, or `None` when there is none.

`first_negative([120, -50, 80, -20])` gives `-50`, and `first_negative([1, 2, 3])` gives `None`. Is `0` a
refund? It is not below zero, so no.

```bash run
cd /workspace/05-loops && python3 -c "from loops import first_negative; print(first_negative([120, -50, 80, -20]))"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What numbers does `range(4)` give?
:::
- [ ] 1, 2, 3, 4
- [x] 0, 1, 2, 3
- [ ] 0, 1, 2, 3, 4
:::explain
`range(4)` starts at 0 and stops before 4: four numbers, 0 to 3.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In `week = [120, 450, 80]`, what is `week[1]`?
:::
- [ ] `120`
- [x] `450`
- [ ] `80`
:::explain
Positions start at 0, so `week[0]` is 120 and `week[1]` is the second item, 450.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A `return` runs inside a `for` loop, on its second lap. What happens?
:::
- [ ] The loop finishes all its laps, then the function returns
- [x] The function ends immediately, loop and all
- [ ] Only that lap ends; the loop goes on
:::explain
`return` ends the whole function at once. Nothing after it runs, not even the rest of the loop.
:::
:::

:::step{type=deep-dive title="Go deeper: while, break, and the loop that never ends"}
**while.** A `for` loop goes through items. A `while` loop repeats **as long as a condition is true**, which
is handy when you do not know in advance how many laps you need. How many months of saving ₹300 to reach
₹1,000?

```python
savings = 0
months = 0
while savings < 1000:
    savings = savings + 300
    months = months + 1
print(months, savings)
```

It prints `4 1200`: after three months there is only ₹900, so a fourth lap is needed.

**break and continue.** Inside any loop, `break` jumps out of the loop at once, and `continue` skips the rest
of this lap and goes straight to the next one.

**The loop that never ends.** If a `while` condition never becomes false (say you forgot
`savings = savings + 300`), the loop runs forever. Press **Ctrl+C** in the terminal to stop it. Python stops
the program and reports `KeyboardInterrupt`: nothing is broken, you simply interrupted it.

**Python already has some loops built in.** `sum(amounts)` adds a list, `max(amounts)` finds the biggest and
`min(amounts)` the smallest. They are loops too, written once by the Python team. Knowing how to write them
yourself means you understand what they do.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Repeat work for every item with `for item in items:`, however long the list.
- Build an answer with the before / inside / after pattern: running totals and counters.
- Count with `range`, knowing positions start at 0 and `range(n)` stops before `n`.
- Stop a search early with `return`, and return `None` when there is nothing to find.

:::photo{src="/lesson-images/python/py-05-notes.webp" alt="Handwritten notes: a for loop with a running total, before, inside and after, and range(3)" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 6: finding bugs. Two of Pocket's functions run without crashing, and give wrong answers anyway.
:::
