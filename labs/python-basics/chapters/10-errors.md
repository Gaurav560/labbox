:::step{type=story title="Why errors"}
Real input is never perfect: someone types "abc" where a number belongs, a file is missing, a line
is half empty. A good program does not crash on the first bad value. It explains what went wrong,
or skips it and carries on.

:::mission
Write two functions in `errors.py`: one turns text into a number and gives a clear error when it
cannot, and one adds up a list of values while collecting the bad ones.
:::
:::

:::step{type=concept title="Exceptions"}
When Python cannot do something, it **raises an exception** and stops:

```python
int("abc")      # ValueError: invalid literal for int() with base 10: 'abc'
10 / 0          # ZeroDivisionError: division by zero
[1, 2][5]       # IndexError: list index out of range
{}["x"]         # KeyError: 'x'
```

The last line of the error, the **traceback**, names the exception and says why. Reading it calmly is
half of debugging.
:::

:::step{type=example title="Worked example: a safe percentage"}
A function that explains bad input instead of crashing:

```python
def percent(part, whole):
    try:
        return round(part / whole * 100, 1)
    except ZeroDivisionError:
        raise ValueError("whole must not be 0") from None

percent(3, 4)     # 75.0
percent(3, 0)     # ValueError: whole must not be 0
```

1. Put the risky line inside `try`.
2. Catch only the exception you expect (`ZeroDivisionError`), never everything.
3. Raise a clear error in your own words; `from None` hides the less helpful original.

`to_number` follows this exact shape with `float()` and `ValueError`.
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```python
try:
    n = int("12a")
    print("got", n)
except ValueError:
    print("not a number")
print("done")
```
:::
- [ ] `got 12` then `done`
- [x] `not a number` then `done`
- [ ] Only `not a number`
- [ ] A ValueError and nothing else
:::explain
`int("12a")` raises a `ValueError`, so Python jumps straight to the matching `except` block and
skips the rest of the `try`. After the `except` block, the program **carries on** normally, so
`done` is printed too.
:::
:::

:::step{type=try title="Catch an error"}
```bash run
python3 -c "
for text in ['42', 'abc', '3.5']:
    try:
        print(text, '->', float(text))
    except ValueError as e:
        print(text, '-> problem:', e)
"
```

`except ValueError as e` gives you the exception itself, so you can show its message.
:::

:::step{type=task task=to_number title="Text to a number, or a clear error"}
In `errors.py`, make `to_number(text)` return the text as a **float**. Spaces around it are fine.
When it is not a number, raise a `ValueError` whose message contains the bad text.

- `to_number("12.5")` returns `12.5`
- `to_number(" 7 ")` returns `7.0`
- `to_number("abc")` raises `ValueError("'abc' is not a number")`
- `to_number("")` raises a `ValueError` too

:::why
"could not convert string to float" does not say *which* value was wrong in a file of 10,000 lines.
Your message does.
:::
:::

:::step{type=concept title="raise, else and finally"}
You can raise exceptions yourself, and a `try` can have two more parts:

```python
def percent(part, whole):
    if whole == 0:
        raise ValueError("whole cannot be zero")
    return part / whole * 100

try:
    p = percent(3, 4)
except ValueError as e:
    print("bad input:", e)
else:
    print("worked:", p)        # runs only when nothing was raised
finally:
    print("always runs")       # cleanup: closing files, connections
```

Catch only the exceptions you expect. A bare `except:` hides real bugs, even typos.
:::

:::step{type=task task=safe_sum title="Add the good, report the bad"}
In `errors.py`, make `safe_sum(values)` add up a list of texts using `to_number`, **skipping** the
ones that are not numbers. Return a tuple: the total as a float, and the list of bad values in the
order they appeared.

- `safe_sum(["10", "x", "2.5", ""])` returns `(12.5, ["x", ""])`
- `safe_sum(["1", "2"])` returns `(3.0, [])`
- `safe_sum([])` returns `(0.0, [])`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `int("12.5")` do?
:::
- [ ] Gives `12`
- [ ] Gives `12.5`
- [x] Raises a ValueError
- [ ] Gives `13`
:::explain
`int()` only reads whole numbers from text, so `"12.5"` raises a ValueError. `float("12.5")` would work.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
When does an `else` block after `try`/`except` run?
:::
- [ ] Always
- [ ] Only when an exception happened
- [x] Only when no exception happened
- [ ] Never
:::explain
`else` runs when the `try` block finished **without** an exception; `finally` is the one that always runs.
:::
:::

:::step{type=deep-dive title="Asking forgiveness, and exceptions as a family"}
Python style is often **EAFP**, "easier to ask forgiveness than permission": try the thing and catch
the failure, instead of checking every condition first. Checking `text.isdigit()` before `int(text)`
misses `"-5"` and `"3.5"`; trying `float(text)` and catching `ValueError` handles every case Python
itself understands.

Exceptions form a **family tree**: `ZeroDivisionError` is a kind of `ArithmeticError`, which is a
kind of `Exception`. `except Exception` catches almost everything, which is why it should be used
rarely and only at the outer edge of a program, to log the problem and keep a server running.

You can define your own: `class BudgetError(ValueError): pass`. Callers can then catch your specific
problem, or the general `ValueError`, whichever they need.
:::

:::step{type=recap}
- Errors raise exceptions; the last line of the traceback says which and why.
- `try` / `except SomeError` handles the cases you expect, then the program carries on.
- `raise ValueError("clear message")` reports a problem in your own words.
- `else` runs when nothing failed, `finally` always runs; never use a bare `except:`.
:::
