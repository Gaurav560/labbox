:::step{type=story title="Why loops"}
Working out one student's grade is easy. Working out 40 students' grades, or a whole month of
expenses, means doing the same thing again and again. Loops repeat work for you.

:::mission
Write two functions in `loops.py`: one counts how many numbers are above a limit, and one finds the
first negative number in a list.
:::
:::

:::step{type=concept title="for loops"}
A `for` loop runs its block once for each item in a list:

```python
marks = [72, 45, 90]
for m in marks:
    print(m)
```

`range` gives you numbers to loop over: `range(5)` is 0, 1, 2, 3, 4 and `range(1, 4)` is 1, 2, 3.
A common pattern is to start a value before the loop and update it inside:

```python
total = 0
for m in marks:
    total = total + m      # or: total += m
```
:::

:::step{type=example title="Worked example: count the passing marks"}
The counting pattern, one line at a time:

```python
def count_passed(marks):
    count = 0              # 1. start at zero
    for m in marks:        # 2. each mark
        if m >= 33:        # 3. does it count?
            count += 1     # 4. add one
    return count           # 5. the answer

count_passed([45, 20, 90, 33])
# 3
```

Change only the condition in step 3 and the same five lines count anything you like. That is your
first task.
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```python
for i in range(1, 4):
    print(i * 10)
```
:::
- [ ] `0 10 20 30`
- [x] `10 20 30`
- [ ] `10 20 30 40`
- [ ] `1 2 3`
:::explain
`range(1, 4)` starts at 1 and stops **before** 4, so `i` is 1, 2 and 3. The end of a range is
never included, which is also why `range(len(items))` fits a list exactly.
:::
:::

:::step{type=try title="Loop in the terminal"}
```bash run
python3 -c "
total = 0
for m in [72, 45, 90]:
    total += m
    print('after', m, 'total is', total)
"
```
:::

:::step{type=task task=count_above title="How many are above the limit"}
In `loops.py`, make `count_above(numbers, limit)` return how many numbers are **greater than** the
limit.

- `count_above([35, 72, 40, 90], 40)` returns `2` (40 itself is not above 40)
- `count_above([], 10)` returns `0`
- `count_above([-5, -1, 3], -2)` returns `2`
:::

:::step{type=concept title="Stopping early: return, break and while"}
Sometimes you can stop as soon as you know the answer. Inside a function, `return` ends the loop
and the function at once. Outside one, `break` ends just the loop:

```python
for m in marks:
    if m < 33:
        print("someone failed")
        break
```

A `while` loop repeats as long as a condition stays true, which suits work with no fixed list:

```python
n = 1
while n < 100:
    n = n * 2      # 1, 2, 4 ... stops at 128
```
:::

:::step{type=task task=first_negative title="The first negative number"}
In `loops.py`, make `first_negative(numbers)` return the **first** negative number in the list, or
`None` if there is none.

- `first_negative([4, -2, 7, -9])` returns `-2`
- `first_negative([1, 2, 3])` returns `None`
- `first_negative([])` returns `None`
- `first_negative([0, 5])` returns `None` (zero is not negative)
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `list(range(2, 5))`?
:::
- [ ] `[2, 3, 4, 5]`
- [x] `[2, 3, 4]`
- [ ] `[3, 4, 5]`
- [ ] `[0, 1, 2, 3, 4]`
:::explain
A range starts at the first number and stops **before** the second: 2, 3 and 4.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `for x in []: print(x)` print?
:::
- [ ] `None`
- [ ] `[]`
- [x] Nothing at all
- [ ] An error
:::explain
The list is empty, so the loop body never runs and nothing is printed. That is why `count_above([], 10)` gives `0`: the starting value.
:::
:::

:::step{type=deep-dive title="What a for loop really does"}
A `for` loop works on anything **iterable**: lists, text (one letter at a time), dictionaries (one
key at a time), files (one line at a time) and `range`. Behind the scenes Python asks the object
for an iterator and calls `next()` on it until it says it is done.

`range(1_000_000)` does not build a list of a million numbers: it hands them out one by one, so it
uses almost no memory. Many Python tools work the same way, which is why loops over huge files stay
fast and light.

To loop with a position too, use `enumerate`: `for i, m in enumerate(marks):` gives 0 and the first
mark, then 1 and the second, and so on.
:::

:::step{type=recap}
- `for item in items:` runs once per item; `range(a, b)` stops before `b`.
- Start a counter or total before the loop and update it inside.
- `return` (in a function) or `break` stops a loop early; `while` repeats while a condition holds.
- A function that finds nothing should return something clear, like `None`.
:::
