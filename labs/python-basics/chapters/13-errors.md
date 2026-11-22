:::step{type=story title="What should Pocket do when someone types abc as an amount?"}
Real people type real things. Somebody enters `abc` as the price of lunch. A file arrives with an empty line. A
friend sends `1,200` with a comma. Your program has two choices: **crash** with a traceback, or **notice, say
something useful, and carry on**.

You already know how to read errors (chapter 6). Today you learn to **raise** your own, with messages that help,
and to **catch** the ones you expect, so one bad value never brings Pocket down. This is the difference between a
script that works on your laptop and a program other people can use.

:::mission
Write `to_number`, which turns text into a number or explains clearly why it cannot, and `safe_sum`, which adds up
the good values and reports the bad ones.
:::
:::

:::step{type=concept title="Exceptions: Python's way of saying stop"}
When Python cannot carry on, it **raises an exception**: an object that describes what went wrong. If nobody
handles it, the program stops and prints the traceback. You have met a whole family of them in this course:

| Exception | Means | You met it in |
|---|---|---|
| `SyntaxError` | the code is not valid Python | chapter 1 |
| `NameError` | a name that does not exist | chapter 1 |
| `TypeError` | the wrong kind of value, like `"5" + 5` | chapters 2 and 3 |
| `ValueError` | the right kind, but a bad value, like `int("12.5")` | chapter 3 |
| `ZeroDivisionError` | dividing by zero | chapter 6 |
| `IndexError` | a position that does not exist | chapter 7 |
| `KeyError` | a dictionary key that does not exist | chapter 9 |
| `FileNotFoundError` | a file that is not there | chapter 14 |

Each has a **name** (the kind of problem) and a **message** (the details). The name is what your code uses to
decide what to do; the message is for the person reading it.

:::picture{name="fire-alarm"}
An exception is a fire alarm: something raises it, and it rings all the way up until someone handles it.
:::
:::

:::step{type=try title="Text that is a number, and text that is not"}
`float(...)` turns text into a number when it can. Try three kinds of text:

```bash run
python3 -c "print(float(' 7 '), float('2.5')); float('abc')"
```

```text
7.0 2.5
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ValueError: could not convert string to float: 'abc'
```

Two surprises worth noticing. `float(" 7 ")` happily ignores the spaces around a number. And `float("abc")`
raises a `ValueError` whose message even quotes the bad text. Python's own messages are good; your job today is
to make yours just as helpful.
:::

:::step{type=concept title="raise: say exactly what is wrong"}
Your functions can raise exceptions too, with `raise`, the kind of exception, and a message:

```python
def parse_age(text):
    age = int(text)
    if age < 0:
        raise ValueError(f"age cannot be negative: {age}")
    return age
```

`parse_age("30")` gives `30`. `parse_age("-4")` stops with:

```text
ValueError: age cannot be negative: -4
```

Why raise instead of returning something like `-1` or `None`? Because a wrong answer that *looks* fine travels
far through a program before anyone notices (a quiet bug, chapter 6). An exception stops right at the cause, with
a message that names the bad value. A good error message answers three questions: **what** was wrong, **which**
value, and ideally **what to do**.
:::

:::step{type=example title="Worked example: catch one error, raise a better one"}
Sometimes Python's own error is accurate but unhelpful for *your* users. You can catch it and raise a clearer one
in its place. Here is a function that reads a quantity:

```python
def to_quantity(text):
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"'{text}' is not a whole number of items") from None
```

1. `try:` runs the indented code and watches for exceptions.
2. If `int(text)` raises a `ValueError`, Python jumps straight to the matching `except ValueError:` block.
3. That block raises a new `ValueError` with a message in Pocket's words. `from None` hides the original error,
   so the user sees one clean message instead of two tracebacks.
4. If nothing goes wrong, the `except` block never runs, and the number is returned.

Your first task has exactly this shape.
:::

:::step{type=task task=to_number title="Your turn: a number, or a clear reason"}
Open `errors.py` and make `to_number(text)` give back the text as a `float`, or raise a `ValueError` with the
message `'<text>' is not a number` (the bad text in single quotes).

- `to_number(" 7 ")` gives `7.0`, and `to_number("2.5")` gives `2.5`.
- `to_number("abc")` raises `ValueError: 'abc' is not a number`.

```bash run
cd /workspace/13-errors && python3 -c "from errors import to_number; print(to_number(' 7 ')); to_number('abc')"
```

Then press **Check**.
:::

:::step{type=concept title="try and except: handle it and carry on"}
Raising stops a program. **Catching** lets it continue. Press Play to follow what Python does when an error
happens inside `try`:

:::diagram{name="try-except-flow"}
Inside try, an error jumps straight to the matching except; then the program carries on after it.
:::

Here is the pattern in a loop, skipping the values that are not numbers:

```python
for text in ["120", "abc", "80"]:
    try:
        amount = float(text)
        print("ok:", amount)
    except ValueError:
        print("skipped:", text)
print("done")
```

```text
ok: 120.0
skipped: abc
ok: 80.0
done
```

The bad value did not stop the loop: it was handled, and the next value was tried. One rule matters more than
any other: **catch only the exceptions you expect**. `except ValueError:` catches bad numbers and nothing else, so
a real bug (a `NameError` from a typo, say) still shows up loudly instead of being silently swallowed.
:::

:::step{type=predict title="Guess first"}
:::question
What happens here?

```python
try:
    x = 1 / 0
except ValueError:
    print("caught")
```
:::
- [ ] It prints `caught`
- [x] It stops with a `ZeroDivisionError`
- [ ] Nothing happens
:::explain
`except ValueError` only catches `ValueError`s. Dividing by zero raises a `ZeroDivisionError`, which this block
does not match, so it is not caught and the program stops. That is exactly what you want when the error is one
you did not expect.
:::
:::

:::step{type=task task=safe_sum title="Your turn: add the good, report the bad"}
In `errors.py`, make `safe_sum(values)` add up every value that is a number and collect the ones that are not.
It gives back a tuple: `(total, bad_values)`, where the total is a float.

- `safe_sum(["10", "x", "2.5", ""])` gives `(12.5, ["x", ""])`.
- `safe_sum([])` gives `(0.0, [])`.

Use your `to_number` inside a `try`, and catch the `ValueError` it raises.

```bash run
cd /workspace/13-errors && python3 -c "from errors import safe_sum; print(safe_sum(['10', 'x', '2.5', '']))"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which exception does `{"juice": 15}["coffee"]` raise?
:::
- [ ] `ValueError`
- [x] `KeyError`
- [ ] `IndexError`
:::explain
A missing dictionary key raises a `KeyError`. A missing list position raises an `IndexError`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why is `except Exception:` around a whole program usually a bad idea?
:::
- [ ] It is slower
- [x] It hides real bugs, like typos, along with the errors you meant to handle
- [ ] Python does not allow it
:::explain
Catching everything also catches the mistakes you did not expect, so they vanish instead of showing up. Catch only
the specific exceptions you know how to handle.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
In a `try` block, the first line raises an exception. Do the other lines of the `try` block run?
:::
- [ ] Yes, all of them
- [x] No: Python jumps straight to the matching `except`
:::explain
The moment an exception is raised, the rest of the `try` block is skipped.
:::
:::

:::step{type=deep-dive title="Go deeper: else, finally, and your own exceptions"}
A `try` statement has two more optional parts:

```python
try:
    amount = float(text)
except ValueError:
    print("not a number")
else:
    print("ok:", amount)      # runs only when nothing went wrong
finally:
    print("checked", text)    # runs always, error or not
```

`finally` is for clean-up that must happen no matter what: closing a connection, deleting a temporary file.
(For files, chapter 14's `with` does that job for you.)

**Your own exceptions.** Big programs define their own kinds, so callers can catch exactly theirs:

```python
class BudgetError(Exception):
    pass

raise BudgetError("food budget is 0")
```

You will learn what `class` means in chapter 15. **Exception hierarchy:** every exception kind belongs to a family
tree; `except Exception` catches almost everything below it, which is exactly why it is so dangerous.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Name the common exceptions and what each one means.
- Raise your own with `raise ValueError("...")` and a message that names the bad value.
- Catch the errors you expect with `try` / `except`, and keep going.
- Catch only what you expect, so real bugs still show up.

:::photo{src="/lesson-images/python/py-13-notes.webp" alt="Handwritten notes about exceptions: try, except ValueError, raise ValueError, catch only what you expect" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 14: files, so Pocket can remember things after the program ends.
:::
