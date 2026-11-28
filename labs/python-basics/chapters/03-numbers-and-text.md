:::step{type=story title="Can a computer get a sum wrong?"}
Computers are famous for maths. They can add a billion numbers in a second. So here is a puzzle for you: ask
Python for `0.1 + 0.2`, and it says...

```text
0.30000000000000004
```

Not `0.3`. Is Python broken? No, and by the end of this chapter you will know exactly why, and how real money
apps avoid the trap.

Pocket is all about money: it adds up what you spend, works out averages and shows amounts like `₹1,250.50`.
So today you learn how Python stores numbers and text, and how to make them look right.

:::mission
Write `average`, which gives Pocket the average of a list of amounts, and `format_price`, which shows any
amount the way a shop receipt would.
:::
:::

:::step{type=concept title="Variables: names for values" file="03-numbers-and-text/today.py" line="2-8"}
Open `today.py`. It keeps track of one day of spending:

```python
lunch = 120
bus = 30
jelly = 15.5

total = lunch + bus + jelly
print("Spent today:", total)
print(f"That is {total / 3:.2f} rupees per thing on average.")
```

`lunch = 120` creates a **variable**: a name (`lunch`) that refers to a value (`120`). From now on, wherever
you write `lunch`, Python uses `120`. A **value** is any single piece of data: a number, a piece of text, a list.

Here is the one thing to get right from day one: **`=` does not mean "equals"**. It means "store the value on
the right under the name on the left". Python always works out the right side first, then stores it. That is
why this line, which looks impossible in a maths class, is perfectly normal in Python:

```python
total = total + 10    # work out total + 10, then store it back in total
```

Names can use letters, digits and `_`, but cannot start with a digit, and capital letters matter (`Total` and
`total` are two different names). Python programmers write longer names in lowercase with underscores, like
`daily_budget`. This style is called **snake_case**.

:::picture{name="labelled-jars"}
A variable is a label on a jar: the name stays, and you can put a new value inside.
:::
:::

:::step{type=try title="Run a day of spending" file="03-numbers-and-text/today.py" line="2-8"}
Run it:

```bash run
cd /workspace/03-numbers-and-text && python3 today.py
```

```text
Spent today: 165.5
That is 55.17 rupees per thing on average.
```

`total` is `120 + 30 + 15.5`, which is `165.5`. The second line divides it by 3 (three things bought):
`165.5 / 3` is `55.1666...`, and the `:.2f` inside the braces shows it with two decimals, rounded: `55.17`. You will
understand that `:.2f` fully later in this chapter.

Now be curious: change `jelly = 15.5` to `jelly = 20` in the editor, save, and run it again. Only one number
changed, yet both lines changed, because everything after it was worked out from the variables. That is the
power of names.
:::

:::step{type=concept title="Two kinds of numbers, and five ways to divide"}
Look closely at the numbers in `today.py`. `120` has no decimal point; `15.5` has one. To Python these are two
different **types** of number:

- `int` (integer): whole numbers like `120`, `0`, `-7`.
- `float` (floating-point): numbers with a decimal point like `15.5`, `2.0`, `0.1`. The name comes from how they
  are stored: a set of digits plus a note of where the decimal point goes, so the point can "float" to any place.
  That is how one type can hold both `0.000015` and `15000000.0`.

You can always ask Python what type something is with `type(...)`. It answers `<class 'int'>`,
`<class 'float'>`, or for text, `<class 'str'>`.

Here are the maths operators:

| Operator | Means | Example | Answer |
|---|---|---|---|
| `+` | add | `7 + 2` | `9` |
| `-` | subtract | `7 - 2` | `5` |
| `*` | multiply | `7 * 2` | `14` |
| `/` | divide | `7 / 2` | `3.5` |
| `//` | divide, keep the whole part | `7 // 2` | `3` |
| `%` | remainder | `7 % 2` | `1` |
| `**` | power | `2 ** 10` | `1024` |

Two rules surprise people:

- `/` **always** gives a float, even when the answer is whole: `10 / 5` is `2.0`, not `2`.
- `//` rounds **down**, to the next smaller whole number. `10 // 4` is `2` (2.5 rounded down), and `-7 // 2` is
  `-4`, not `-3`: -3.5 rounded *down* is -4, because -4 is smaller than -3.

Like in school maths, `*` and `/` happen before `+` and `-`: `2 + 3 * 4` is `14`. Use brackets when you want a
different order: `(2 + 3) * 4` is `20`.
:::

:::step{type=predict title="Guess first"}
:::question
What does `print(0.1 + 0.2)` show?
:::
- [ ] `0.3`
- [x] `0.30000000000000004`
- [ ] `0.3000`
- [ ] An error
:::explain
Floats are stored in binary (ones and zeros), and most decimal fractions, like 0.1, cannot be written exactly
in binary, just as 1/3 cannot be written exactly in decimal (0.3333...). So Python stores the nearest binary
number it can, which is a tiny bit off, and the tiny leftovers show up when you add. It happens in almost every
programming language, not just Python, because they all store floats the same standard way (a standard called
IEEE 754).
:::
:::

:::step{type=try title="See the surprise, then tame it"}
See it for real:

```bash run
python3 -c "print(0.1 + 0.2); print(round(0.1 + 0.2, 2))"
```

The first line shows `0.30000000000000004`. The second shows `0.3`: `round(value, 2)` rounds to two digits
after the point, which is exactly what you want for money on a screen.

Now try the division family yourself:

```bash run
python3 -c "print(7 / 2, 7 // 2, 7 % 2, 2 ** 10)"
```

```text
3.5 3 1 1024
```

Change the numbers and predict each answer before you press Enter. Being right in your head first is how you
learn fastest.
:::

:::step{type=example title="Worked example: the average temperature"}
Your next task is an average, so here is one on a different problem: the average of some temperatures, rounded
to one decimal.

```python
def average_temperature(temps):
    return round(sum(temps) / len(temps), 1)

average_temperature([31, 29, 33])    # gives back 31.0
```

There are three new things here:

1. `[31, 29, 33]` is a **list**: several values in square brackets, separated by commas. Chapter 8 is all
   about lists; for now, it is "a bunch of numbers".
2. `sum(temps)` adds up everything in the list: `93`. `len(temps)` counts the items: `3`.
3. `93 / 3` is `31.0`, and `round(..., 1)` keeps one digit after the point.

Read the `return` line from the inside out, the way Python works it out: first `sum` and `len`, then the
division, then `round`. Why `31.0` and not `31`? Because `/` always gives a float, and `round(..., 1)` keeps it a
float.
:::

:::step{type=task task=average title="Your turn: Pocket's average spend"}
Open `numbers_text.py` and make `average(amounts)` give back the average of the amounts, rounded to **2**
decimals.

`average([120, 80, 100])` gives `100.0`, and `average([1, 2, 2])` gives `1.67`.

```bash run
cd /workspace/03-numbers-and-text && python3 -c "from numbers_text import average; print(average([1, 2, 2]))"
```

Then press **Check**. The check also tries a list with one amount, `[100]` (answer `100.0`), and `[0, 0]`
(answer `0.0`).

The usual slips (we tried them on `[1, 2, 2]`):

- Forgetting to round: you get `1.6666666666666667`. The check says the value is right but not rounded.
- `//` instead of `/`: you get `1`, a whole number. `//` throws the decimals away.
- Rounding too early, `round(sum(amounts)) / len(amounts)`: you get `1.6666666666666667` again, because the
  rounding happened before the division. Round last, around the whole sum.
:::

:::step{type=concept title="Text is different from numbers"}
Text in Python is a **string** (type `str`), and strings have their own rules. Try to predict each answer:

```python
"5" + "5"      # "55"   + joins two strings
"5" * 3        # "555"  * repeats a string
len("book")    # 4      len counts the characters
```

`"5"` in quotes is not the number five; it is the *character* 5, like a letter. So `"5" + "5"` glues two
characters together.

And text plus a number? Python refuses:

```text
TypeError: can only concatenate str (not "int") to str
```

**Concatenate** means "join together". Python will not guess whether you meant `"55"` or `10`, so it asks you
to decide by **converting** one of them:

```python
int("5") + 5     # 10    int() turns text into a whole number
str(5) + "5"     # "55"  str() turns a number into text
float("15.5")    # 15.5  float() turns text into a float
```

Conversions only work when the text really is a number. `int("12.5")` fails with
`ValueError: invalid literal for int() with base 10: '12.5'`, because `12.5` is not a whole number. ("Literal"
means the value as it is written; "base 10" means ordinary decimal digits.) `int(float("12.5"))` works: it gives
`12`, cutting the decimals off.

:::picture{name="number-vs-text"}
5 and "5" look the same on screen, but one is a number and the other is text.
:::
:::

:::step{type=example title="Worked example: numbers that look right"}
f-strings can do more than drop a value in. After the value, inside the braces, a `:` starts a **format**:

```python
distance = 12345.678
f"{distance:.2f} km"      # "12345.68 km"   .2f: exactly 2 decimals
f"{distance:,} km"        # "12,345.678 km" ,: a comma between thousands
f"{distance:,.2f} km"     # "12,345.68 km"  both
```

Read `,.2f` from left to right: `,` adds thousands separators, `.2` means two digits after the point, and `f`
means "show it as a float". Formatting also rounds: `f"{5:.2f}"` gives `"5.00"`, and big numbers like
`1234567.891` become `1,234,567.89`.

Text outside the braces stays exactly as you write it, so a unit, a symbol or a word can go before or after.
:::

:::step{type=task task=format_price title="Your turn: amounts like a receipt"}
In `numbers_text.py`, make `format_price(amount)` give back the amount as a price: the rupee sign `₹`, commas
between thousands, and exactly two decimals.

`format_price(1250.5)` gives `"₹1,250.50"`, `format_price(5)` gives `"₹5.00"`, and `format_price(999.999)`
gives `"₹1,000.00"`.

```bash run
cd /workspace/03-numbers-and-text && python3 -c "from numbers_text import format_price; print(format_price(1250.5))"
```

Then press **Check**.

How to type `₹`: copy it from this page or from the comment in `numbers_text.py`, and paste it inside your
f-string. Python strings can hold any character, ₹ included.

The usual slips: the format in the wrong order, `:.2f,`, which Python refuses with `ValueError: Invalid format
specifier '.2f,' for object of type 'float'` (the comma comes first: `:,.2f`); forgetting the comma, so
`1234567.891` shows as `1234567.89`; or writing `Rs` instead of `₹`. The check names each one.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is `10 / 5`?
:::
- [ ] `2`
- [x] `2.0`
- [ ] `"2"`
:::explain
`/` always gives a float, even when the answer is a whole number.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
After `x = 5` and then `x = x + 1`, what is in `x`?
:::
- [ ] `5`
- [x] `6`
- [ ] An error: x cannot equal x + 1
:::explain
`=` stores: Python works out `x + 1` (6) first, then stores it back in `x`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `f"{3.14159:.2f}"` give?
:::
- [x] `"3.14"`
- [ ] `"3.15"`
- [ ] `"3.14159"`
:::explain
`.2f` keeps two digits after the point, rounding the rest: 3.14159 becomes 3.14.
:::
:::

:::step{type=deep-dive title="Go deeper: why real money apps avoid floats"}
**Rounding has surprises too.** Try these:

```bash run
python3 -c "print(round(2.675, 2), round(2.5), round(3.5))"
```

```text
2.67 2 4
```

`2.675` is really stored as something like `2.67499999...`, so it rounds down. And `round(2.5)` is `2` while
`round(3.5)` is `4`: Python rounds exact halves to the nearest **even** number ("banker's rounding"), so
rounding errors do not all pile up in one direction.

**What real money apps do.** Banks and payment apps never store money as floats. Two common ways:

- Store **whole paise** as an `int`: ₹1,250.50 is `125050` paise (100 paise make a rupee). Python's integers are
  always exact, however big they get. (The Spring Boot course on LabBox stores prices exactly this way.)
- Use Python's `decimal` module, which does decimal maths the way you do on paper: `Decimal("0.1") +
  Decimal("0.2")` is exactly `Decimal("0.3")`.

Pocket uses floats to keep things simple while you learn, and rounds when it shows amounts. You now know why
that is fine for a personal tracker and not for a bank.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Store values in variables with `=`, and update them (`total = total + 10`).
- Tell `int` from `float`, use `+ - * / // % **`, and explain why `0.1 + 0.2` is not exactly `0.3`.
- Join and repeat strings, and convert with `int()`, `float()` and `str()`.
- Make numbers look right with f-string formats like `:.2f` and `:,.2f`.

:::photo{src="/lesson-images/python/py-03-sketch.webp" alt="Sketchnote: Numbers and text. A variable is a name for a value; = stores, and Python works out the right side first. Flow: total = 120 + 45.5, 165.5 is a float, 165.5 / 3, 55.1666, an f-string with .2f shows 55.17. Remember: / always gives a float, 10 / 5 is 2.0; 0.1 + 0.2 is 0.30000000000000004 in Python; text plus a number is a TypeError, convert with int() or str(); in an f-string, :,.2f shows 1,250.50." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 4: making decisions, so Pocket can tell when you are over budget.
:::
