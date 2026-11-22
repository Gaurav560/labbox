:::step{type=story title="Is 2100 a leap year?"}
Quick, without looking it up: is the year 2100 a leap year? It is divisible by 4, so... yes?

Most people say yes. The answer is **no**. And the year 2000, which was also divisible by 100, *was* a leap
year. The calendar has rules inside rules, and a computer gets them right every time, but only if someone
writes the rules down exactly.

:::photo{src="/lesson-images/python/pope-gregory-xiii.webp" alt="A portrait of Pope Gregory XIII in red robes" credit="Unknown artist" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Pope_Gregory_XIII_portrait.jpg"}
Pope Gregory XIII. His calendar reform of 1582 added the rule about years divisible by 100 and 400, and most of the world still uses it.
:::

Rules like these are everywhere in programs: *if* you spent more than your budget, warn me; *if* the password
is wrong, say so; *otherwise*, carry on. Today Pocket learns to make decisions.

:::mission
Write `grade`, which turns marks into a grade, and `is_leap_year`, which gets the calendar's tricky rules
exactly right.
:::
:::

:::step{type=concept title="Questions with yes-or-no answers"}
Every decision starts with a question whose answer is yes or no. In Python, the answer is a **boolean**: one of
the two values `True` or `False` (with capital letters, no quotes). You met one in chapter 2: `n == 10`.

**Comparisons** ask those questions:

| Operator | Asks | Example | Answer |
|---|---|---|---|
| `==` | equal? | `5 == 5` | `True` |
| `!=` | not equal? | `5 != 5` | `False` |
| `<` | less than? | `3 < 7` | `True` |
| `>` | greater than? | `3 > 7` | `False` |
| `<=` | less than or equal? | `7 <= 7` | `True` |
| `>=` | greater than or equal? | `8 >= 7` | `True` |

You can compare text too: Python compares strings letter by letter, like a dictionary does, so `"apple" <
"banana"` is `True`. But here is a curious one:

```bash run
python3 -c 'print("Zebra" < "apple", "2" < "10")'
```

```text
True False
```

`"Zebra"` comes before `"apple"`, because every capital letter is "smaller" than every lowercase letter in the
computer's alphabet. And `"2" < "10"` is `False`, because as text Python compares the first characters, `"2"`
and `"1"`, and `"1"` comes first. Numbers compare as numbers; text compares as text. Keep that in mind when
data arrives as text.
:::

:::step{type=concept title="if and else: two paths" file="04-decisions/budget.py" line="2-10"}
Open `budget.py`:

```python
spent = 650
budget = 500

if spent > budget:
    print("Over budget by", spent - budget, "rupees.")
else:
    print("Within budget. Well done!")

print("Pocket checked today's spending.")
```

Here is how Python reads the `if`:

1. It works out the **condition**, `spent > budget`: is 650 greater than 500? `True`.
2. When the condition is `True`, it runs the indented block under `if`, and skips the `else` block.
3. When the condition is `False`, it skips the `if` block and runs the block under `else`.
4. Either way, it continues with the first line that is not indented: `print("Pocket checked...")`.

The `:` at the end of the `if` and `else` lines and the 4-space indentation work exactly as they do for
functions. Forget the indentation and Python says so before running anything:

```text
IndentationError: expected an indented block after 'if' statement on line 5
```

:::picture{name="fork-in-road"}
An if is a fork in the road: the condition decides which path the program takes, then both paths meet again.
:::
:::

:::step{type=try title="Change the facts, change the path" file="04-decisions/budget.py" line="2"}
Run it:

```bash run
cd /workspace/04-decisions && python3 budget.py
```

```text
Over budget by 150 rupees.
Pocket checked today's spending.
```

Now change `spent = 650` to `spent = 400`, save, and run it again:

```text
Within budget. Well done!
Pocket checked today's spending.
```

Same program, different path, because the facts changed. The last line prints both times: it is outside the
`if`. What do you think happens with `spent = 500`, exactly the budget? Try it and see if you were right.
:::

:::step{type=example title="Worked example: more than two paths"}
Sometimes there are more than two answers. `elif` (short for "else if") adds more conditions. Here is a function
that sorts a day's spending into levels:

```python
def spend_level(amount):
    if amount >= 1000:
        return "high"
    elif amount >= 500:
        return "medium"
    else:
        return "low"
```

Follow `spend_level(700)`:

1. Is `700 >= 1000`? No. Skip that block.
2. Is `700 >= 500`? Yes. Return `"medium"`. The function ends right there; the rest is never even looked at.

**Python stops at the first condition that is `True`.** That is why the order matters: test the biggest
threshold first. And `else` catches everything that matched nothing above it.
:::

:::step{type=predict title="Guess first"}
:::question
Someone wrote the levels in the other order:

```python
def spend_level(amount):
    if amount >= 500:
        return "medium"
    elif amount >= 1000:
        return "high"
    else:
        return "low"
```

What does `spend_level(1500)` give back?
:::
- [ ] `"high"`
- [x] `"medium"`
- [ ] `"low"`
:::explain
1500 is greater than or equal to 500, so the first condition is already `True` and the function returns
`"medium"`. The `"high"` line can never be reached: any amount of 1000 or more is caught by the first test.
:::
:::

:::step{type=task task=grade title="Your turn: a grade from marks"}
Open `decisions.py` and make `grade(marks)` give back a grade:

- `"A"` for 80 and above, `"B"` for 60 and above, `"C"` for 40 and above, `"F"` below 40;
- `"Invalid"` for marks below 0 or above 100, because they cannot be real marks.

1. Deal with the invalid marks first.
2. Then test from the highest grade down, with `if`, `elif` and `else`.
3. Watch the edges: 80 is an `"A"`, 79 is a `"B"`.

```bash run
cd /workspace/04-decisions && python3 -c "from decisions import grade; print(grade(80))"
```

Try 79, 40, 39, 101 and -1 too, then press **Check**.
:::

:::step{type=concept title="and, or, not: combining questions"}
Real rules often have several parts. Three words combine conditions:

- `a and b` is `True` only when **both** are `True`.
- `a or b` is `True` when **at least one** is `True`.
- `not a` flips it: `not True` is `False`.

```python
marks = 85
marks >= 0 and marks <= 100    # True: both parts are true
marks < 0 or marks > 100       # False: neither part is true
not (marks > 100)              # True
```

When you mix them, `not` is worked out first, then `and`, then `or`, just as `*` comes before `+`. When in
doubt, add brackets: they make the order obvious to the next person who reads your code.

One mistake everybody makes once: writing `=` (store) instead of `==` (compare) in a condition. Python catches
it before running, and even suggests the fix:

```text
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```
:::

:::step{type=example title="Worked example: rules with exceptions"}
Here is a rule with an exception, on a different problem. A shop gives free delivery on orders of ₹500 or more,
except for heavy items, unless the customer is a member:

```python
def free_delivery(total, heavy, member):
    return total >= 500 and (not heavy or member)
```

Read it as a sentence: "the total is at least 500, **and** either it is not heavy **or** the customer is a
member". The brackets keep the exception together. Test it in your head:

- `free_delivery(600, False, False)`: 600 >= 500 is `True`, not heavy is `True`, so `True`.
- `free_delivery(600, True, False)`: heavy and not a member, so the bracket is `False`, so `False`.
- `free_delivery(600, True, True)`: heavy, but a member, so `True`.

A whole rule, in one line, returned directly as `True` or `False`. Your leap-year task has the same shape.
:::

:::step{type=task task=leap_year title="Your turn: the calendar's tricky rule"}
In `decisions.py`, make `is_leap_year(year)` give back `True` for leap years and `False` otherwise. The rule:

- a year divisible by 4 is a leap year,
- **except** years divisible by 100, which are not,
- **unless** they are also divisible by 400, which are.

So 2024 is `True`, 2023 is `False`, 1900 is `False`, 2000 is `True`, and 2100 is `False`. "Divisible by 4"
means `year % 4 == 0`.

```bash run
cd /workspace/04-decisions && python3 -c "from decisions import is_leap_year; print(is_leap_year(2100))"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `"10" < "9"` give?
:::
- [x] `True`
- [ ] `False`
- [ ] An error
:::explain
As text, Python compares character by character: `"1"` comes before `"9"`, so `"10"` is smaller. Compare
numbers as numbers: `int("10") < int("9")` is `False`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In an `if` / `elif` / `else` chain, two conditions are both `True`. Which block runs?
:::
- [x] Only the first one
- [ ] Both, in order
- [ ] Only the last one
:::explain
Python stops at the first `True` condition and skips the rest of the chain.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `True and not False`?
:::
- [x] `True`
- [ ] `False`
:::explain
`not False` is `True`, and `True and True` is `True`.
:::
:::

:::step{type=deep-dive title="Go deeper: truthiness, chained comparisons and match"}
**Truthiness.** An `if` does not need a real boolean. Python treats `0`, `0.0`, an empty string `""`, an
empty list `[]` and `None` as false, and almost everything else as true. So `if amounts:` means "if the list is
not empty". You will use this a lot.

**Chained comparisons.** Python lets you write a range check the way you would in maths:

```python
0 <= marks <= 100    # same as: 0 <= marks and marks <= 100
```

**match.** Since Python 3.10, `match` picks a branch by comparing one value against several patterns. It
shines with complicated data; for simple thresholds like grades, `if` and `elif` stay clearer.

**Why 2100 is not a leap year.** A year is really about 365.2422 days. Adding a day every 4 years gives
365.25: slightly too much. Skipping 3 leap days every 400 years (1700, 1800, 1900, but not 2000) brings the
average to 365.2425, close enough for about 3,000 years.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Ask yes-or-no questions with `== != < > <= >=`, and know text compares differently from numbers.
- Choose a path with `if`, `elif` and `else`, knowing Python stops at the first `True` condition.
- Combine conditions with `and`, `or` and `not`, with brackets to keep the meaning clear.
- Return a whole rule as `True` or `False` in one line.

:::photo{src="/lesson-images/python/py-04-notes.webp" alt="Handwritten notes: if, elif and else, the first true condition wins, = stores and == compares, 2100 is not a leap year" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 5: loops, so Pocket can go through a whole list of amounts without you writing a line for each.
:::
