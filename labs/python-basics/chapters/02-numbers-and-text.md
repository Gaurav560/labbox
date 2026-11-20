:::step{type=story title="Why numbers and text"}
Almost every program works with numbers (marks, prices, counts) and text (names, messages,
labels). Python has a few simple types for them, and a couple of surprises worth knowing early.

:::mission
Write two functions in `numbers_text.py`: one finds the average of a list of marks, and one shows
an amount as a price like `₹1,250.50`.
:::
:::

:::step{type=concept title="Whole numbers, decimals and text"}
Python has three everyday types:

```python
age = 17          # int: a whole number
price = 49.5      # float: a number with a decimal point
name = "Riya"     # str: text, in quotes
```

`type(x)` tells you which one you have. Arithmetic works the way you expect, with two kinds of
division:

```python
7 / 2     # 3.5   (always a float)
7 // 2    # 3     (whole part only)
7 % 2     # 1     (the remainder)
```

:::picture{name="labelled-jars"}
A variable is a labelled jar; its shape is its type.
:::
:::

:::step{type=example title="Worked example: a bill total, rounded"}
A function that adds up prices and rounds the answer, and copes with an empty list:

```python
def bill_total(prices):
    if not prices:
        return 0.0
    return round(sum(prices), 2)

bill_total([10.5, 20.25])   # 30.75
bill_total([])              # 0.0
```

1. `if not prices:` is true for an empty list, so we answer `0.0` straight away.
2. `sum(prices)` adds them all; `len(prices)` would count them.
3. `round(x, 2)` keeps two digits after the point, for showing to people.

The average task needs the same three ideas, plus one division.
:::

:::step{type=predict title="Guess first"}
:::question
What does Python print for `0.1 + 0.2 == 0.3`?
:::
- [ ] `True`
- [x] `False`
- [ ] An error
- [ ] `0.3`
:::explain
Computers store decimals in binary, and `0.1` cannot be stored exactly, just like 1/3 cannot be
written exactly in decimal. `0.1 + 0.2` is really `0.30000000000000004`. That is why we **round**
results we show to people, and never compare floats with `==`.
:::
:::

:::step{type=try title="See it for yourself"}
Run these in the terminal and look at each answer:

```bash run
python3 -c "print(0.1 + 0.2); print(round(0.1 + 0.2, 2)); print(7 / 2, 7 // 2, 7 % 2)"
```

`round(x, 2)` keeps two digits after the decimal point.
:::

:::step{type=task task=average title="The average of some marks"}
In `numbers_text.py`, make `average(marks)` return the average of a list of numbers, **rounded to
2 decimal places**.

- `average([78, 85, 92])` returns `85.0`
- `average([70, 71])` returns `70.5`
- `average([1, 2, 2])` returns `1.67`
- `average([])` returns `0.0` (an empty list has no average, and dividing by zero is an error)

:::why
Real data is often empty: a new class with no tests yet, a day with no sales. Good functions
handle that case instead of crashing.
:::
:::

:::step{type=concept title="Putting numbers inside text"}
An **f-string** starts with `f` and puts values inside `{}`:

```python
name = "Riya"
marks = 92.456
f"{name} scored {marks}"        # 'Riya scored 92.456'
f"{name} scored {marks:.1f}"    # 'Riya scored 92.5'
f"{1234567:,}"                  # '1,234,567'
```

After the colon comes a **format**: `.1f` means one digit after the point, and `,` adds thousands
separators. You can use both together.
:::

:::step{type=task task=format_price title="Show a price"}
In `numbers_text.py`, make `format_price(amount)` return the amount as a price: a rupee sign,
thousands separators and exactly two decimals.

- `format_price(1250.5)` returns `"₹1,250.50"`
- `format_price(5)` returns `"₹5.00"`
- `format_price(1234567.891)` returns `"₹1,234,567.89"`
- `format_price(0)` returns `"₹0.00"`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `7 // 2`?
:::
- [ ] `3.5`
- [x] `3`
- [ ] `4`
- [ ] `1`
:::explain
`//` keeps only the whole part of the division: `3`. `7 / 2` would be `3.5`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `f"{1234.5:,.2f}"` give?
:::
- [ ] `'1234.5'`
- [x] `'1,234.50'`
- [ ] `'1,234.5'`
- [ ] `'1234.50'`
:::explain
`,` adds the thousands separator and `.2f` keeps exactly two decimals: `'1,234.50'`. That is your `format_price` in one line.
:::
:::

:::step{type=deep-dive title="Why money is often stored as whole numbers"}
Because floats are not exact, small errors can add up: add `0.1` ten times and you get
`0.9999999999999999`, not `1.0`. Banks and shops avoid this by storing money in the **smallest
unit** as an `int` (paise instead of rupees, cents instead of dollars) and only turning it into a
decimal when they show it.

Python also has `decimal.Decimal` for exact decimal arithmetic. It is slower than float, but it is
the right tool when every paisa must add up.

India groups large numbers differently (`12,34,567`), while `,` in a format gives the Western
grouping (`1,234,567`). Both are fine for this chapter; real apps pick one per country.
:::

:::step{type=recap}
- `int` for whole numbers, `float` for decimals, `str` for text.
- `/` always gives a float, `//` the whole part, `%` the remainder.
- Floats are not exact: round what you show, and do not compare them with `==`.
- f-strings put values in text; `:,.2f` gives separators and two decimals.
:::
