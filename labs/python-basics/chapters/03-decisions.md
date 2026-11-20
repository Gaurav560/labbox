:::step{type=story title="Why decisions"}
A program that always does the same thing is not much use. Grades depend on marks, a discount
depends on the total, a login depends on the password. `if` is how a program chooses.

:::mission
Write two functions in `decisions.py`: one turns marks into a grade, and one tells whether a year
is a leap year.
:::
:::

:::step{type=concept title="if, elif and else"}
`if` runs a block only when a condition is `True`. `elif` (else if) tries another condition, and
`else` catches everything left:

```python
def size(n):
    if n >= 100:
        return "big"
    elif n >= 10:
        return "medium"
    else:
        return "small"
```

Python checks the conditions **from the top** and stops at the **first** one that is `True`.
Conditions use `==`, `!=`, `<`, `<=`, `>`, `>=`, and can be combined with `and`, `or` and `not`.

:::picture{name="fork-in-road"}
One question, and the answer picks the road.
:::
:::

:::step{type=example title="Worked example: a ticket price by age"}
A cinema charges by age. Notice the order of the checks:

```python
def ticket(age):
    if age < 0:
        return "Invalid"
    if age >= 60:
        return "Senior"
    elif age >= 18:
        return "Adult"
    elif age >= 5:
        return "Child"
    else:
        return "Free"
```

1. **Impossible values first**: a negative age is answered before anything else.
2. Then the ranges **from the top down**: 60 and over, then 18 and over, then 5 and over.
3. Each age matches exactly one branch, because Python stops at the first true condition.

`grade` works the same way: invalid marks first, then 80, 60 and 40.

:::trace{title="ticket(45)"}
| check | true? | note |
|---|---|---|
| age < 0 | no | 45 is not below 0, so go on to the next check. |
| age >= 60 | no | 45 is not 60 or more: next check. |
| age >= 18 | yes | 45 is 18 or more: the answer is "Adult", and no later check runs. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `level(90)` return?

```python
def level(marks):
    if marks >= 40:
        return "pass"
    elif marks >= 80:
        return "distinction"
    return "fail"
```
:::
- [x] `"pass"`
- [ ] `"distinction"`
- [ ] `"fail"`
- [ ] `None`
:::explain
`90 >= 40` is already `True`, so Python returns `"pass"` and never looks at the `elif`. With
`if` and `elif`, put the **strictest** condition first: test 80 before 40.
:::
:::

:::step{type=try title="Try a condition"}
Conditions are values too. Try a few in the terminal:

```bash run
python3 -c "m = 75; print(m >= 60, m >= 80, m >= 60 and m < 80, not m == 75)"
```
:::

:::step{type=task task=grade title="Grades from marks"}
In `decisions.py`, make `grade(marks)` return a grade:

| Marks | Grade |
|---|---|
| 80 to 100 | `"A"` |
| 60 to 79 | `"B"` |
| 40 to 59 | `"C"` |
| 0 to 39 | `"F"` |
| below 0 or above 100 | `"Invalid"` |

Edges matter: `grade(80)` is `"A"`, `grade(79)` is `"B"`, `grade(40)` is `"C"`, `grade(100)` is
`"A"`, and `grade(101)` is `"Invalid"`.
:::

:::step{type=concept title="Combining conditions"}
`and` needs both sides true, `or` needs at least one, `not` flips a value:

```python
age = 16
has_permission = True
age >= 18 or has_permission      # True
age >= 13 and age <= 19          # True: a teenager
13 <= age <= 19                  # the same, written the Python way
```

The `%` operator from chapter 1 helps with "divisible by": `year % 4 == 0` is `True` when 4
divides the year exactly.
:::

:::step{type=task task=leap_year title="Leap years"}
In `decisions.py`, make `is_leap_year(year)` return `True` or `False`. The real rule has three
parts:

1. A year divisible by 4 is a leap year,
2. **except** years divisible by 100, which are not,
3. **except** years divisible by 400, which are.

So `2024` is `True`, `2023` is `False`, `1900` is `False` and `2000` is `True`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `True and not False`?
:::
- [x] `True`
- [ ] `False`
- [ ] `None`
- [ ] An error
:::explain
`not False` is `True`, and `True and True` is `True`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `5 <= 5 < 9`?
:::
- [x] `True`
- [ ] `False`
- [ ] An error
- [ ] `5`
:::explain
Python reads it as `5 <= 5 and 5 < 9`, and both are true. Chained comparisons are a tidy way to check a range.
:::
:::

:::step{type=deep-dive title="Truthy and falsy values"}
`if` does not need a real `True` or `False`. Python treats some values as false: `0`, `0.0`, `""`
(empty text), `[]` (an empty list), `{}` and `None`. Everything else counts as true. So
`if name:` means "if the name is not empty", and `if not marks:` means "if the list is empty".

This makes code short, but be careful with numbers: `if score:` is false for a real score of `0`.
When zero is a valid value, write `if score is not None:` instead.
:::

:::step{type=recap}
- `if`, `elif`, `else` choose one path; Python stops at the first true condition.
- Put the strictest condition first.
- `and`, `or`, `not` combine conditions; `13 <= age <= 19` checks a range.
- Edges are where bugs hide: test the exact boundary values.
:::
