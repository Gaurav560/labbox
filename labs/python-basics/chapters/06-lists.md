:::step{type=story title="Why lists"}
A class has 40 marks, a shop has a menu, your phone has a contact list. Whenever you have many values
of the same kind, you keep them in a **list**. Most programs spend their time building, sorting and
picking from lists, so this chapter pays off in everything you write next.

:::mission
Write two functions in `lists.py`: one removes duplicates while keeping the order (a warm-up), and one
picks the n biggest numbers without disturbing the list it was given.
:::
:::

:::step{type=concept title="Making and changing lists"}
A list keeps items **in order**, inside square brackets:

```python
marks = [72, 45, 90]
marks.append(66)     # add to the end   -> [72, 45, 90, 66]
marks[0]             # the first item   -> 72
marks[-1]            # the last item    -> 66
len(marks)           # how many         -> 4
90 in marks          # is it there?     -> True
```

Positions start at **0**, and negative positions count from the end. That is all you need for the
first task.
:::

:::step{type=example title="Worked example: keep only the passing marks"}
Here is the pattern you will use again and again: **start an empty list, loop, and append what you
want to keep.**

```python
def passing(marks):
    result = []          # 1. empty list
    for m in marks:      # 2. each mark
        if m >= 40:      # 3. keep it?
            result.append(m)  # 4. keep
    return result        # 5. give back

passing([72, 30, 90, 12])
# [72, 90]
```

1. Start with an empty list to fill.
2. Look at each mark, in order.
3. Decide whether to keep it: this is the only line that changes from task to task.
4. Keep it by appending it.
5. Give back the new list.

The original list is never changed: we built a **new** one. Your first task uses exactly this shape,
with a different rule in step 3.
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```python
seen = ["tea"]
seen.append("coffee")
print(len(seen), "milk" in seen)
```
:::
- [ ] `1 False`
- [x] `2 False`
- [ ] `2 True`
- [ ] `["tea", "coffee"]`
:::explain
After `append` the list holds two items, so `len` is `2`. `"milk" in seen` asks whether milk is in the
list, and it is not, so it is `False`. You will use `in` exactly like this in a moment.
:::
:::

:::step{type=task task=remove_duplicates title="Warm-up: each item once"}
In `lists.py`, make `remove_duplicates(items)` return a new list with each item only once, in the order
it **first** appeared.

- `remove_duplicates([3, 1, 3, 2, 1])` returns `[3, 1, 2]`
- `remove_duplicates(["tea", "coffee", "tea"])` returns `["tea", "coffee"]`
- `remove_duplicates([])` returns `[]`

Use the worked example's shape. The rule in step 3 is "keep it if it is **not in the new list yet**".
:::

:::step{type=concept title="Sorting, and a list with two names"}
Python sorts in two ways, and the difference matters:

```python
marks = [72, 45, 90]

sorted(marks)
# a NEW list: [45, 72, 90]

sorted(marks, reverse=True)
# biggest first: [90, 72, 45]

marks.sort()
# sorts marks ITSELF, gives back None
```

One more thing to know: `b = a` does **not** copy a list. It gives the same list a second name.

:::diagram{name="shared-list"}
`a` and `b` are two names for one list. A copy, made with `a.copy()`, is a separate list.
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```python
a = [3, 1, 2]
b = a
b.append(4)
print(a)
```
:::
- [ ] `[3, 1, 2]`
- [x] `[3, 1, 2, 4]`
- [ ] `[4]`
- [ ] An error
:::explain
`a` and `b` are two names for the same list (look at the picture above), so adding through `b` changes
what `a` sees too. To get a separate list, write `b = a.copy()`. Almost every Python developer has been
surprised by this once, so if you guessed `[3, 1, 2]`, you are in good company.
:::
:::

:::step{type=try title="See both sorts"}
Run this and compare the two printed lines:

```bash run
python3 -c "
marks = [72, 45, 90]
print(sorted(marks, reverse=True), marks)   # a new list; marks is untouched
marks.sort()
print(marks)                                # marks itself changed
"
```
:::

:::step{type=task task=top_n title="The n biggest numbers"}
In `lists.py`, make `top_n(numbers, n)` return the `n` biggest numbers, **biggest first**, without
changing the list it was given.

- `top_n([72, 45, 90, 66], 2)` returns `[90, 72]`
- `top_n([5, 1], 5)` returns `[5, 1]` (asking for more than there are is fine)
- `top_n([3, 1, 2], 0)` returns `[]`
- after `top_n(marks, 2)`, `marks` is still in its original order

:::why
A function that quietly changes its input causes some of the hardest bugs: the caller's list changes
"by itself" somewhere else in the program. Good functions leave their inputs alone.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `sorted([5, 2, 9])[:2]` give?
:::
- [ ] `[5, 2]`
- [x] `[2, 5]`
- [ ] `[9, 5]`
- [ ] `None`
:::explain
`sorted` gives `[2, 5, 9]`, smallest first, and `[:2]` keeps the first two items: `[2, 5]`. Add
`reverse=True` when you want the biggest first.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
After `marks = [3, 1, 2]` and `copy = marks.copy()` and `copy.sort()`, what is `marks`?
:::
- [x] `[3, 1, 2]`
- [ ] `[1, 2, 3]`
- [ ] `None`
- [ ] An error
:::explain
`copy()` made a separate list, so sorting the copy leaves `marks` alone. That is exactly the habit
`top_n` needed. You have got it.
:::
:::

:::step{type=deep-dive title="How a Python list works inside"}
A list is an array of references that grows by **over-allocating**: when it fills up, Python reserves
room for several more items at once. That is why `append` is fast on average, and why inserting at the
front with `insert(0, x)` is slow: every item has to move one place.

`x in my_list` checks the items one by one, so it slows down as the list grows. For 100,000 items,
`remove_duplicates` would be better with a **set** of the items seen so far next to the result list,
because a set answers `in` almost instantly (chapter 8).

Building a list from another is so common that Python has a one-line form, the **list
comprehension**: `[m for m in marks if m >= 40]` does exactly what the worked example's function does.

Sorting uses **Timsort**, invented for Python by Tim Peters in 2002 and now also used by Java and
Android. It is very fast on data that is already partly in order, and **stable**: equal items keep
their original order.
:::

:::step{type=recap}
- A list keeps items in order: `append`, `[0]`, `[-1]`, `len`, `in`.
- The pattern: an empty list, a loop, and `append` what you keep.
- `sorted()` returns a new list; `.sort()` changes the list and returns `None`.
- `b = a` is two names for one list; `a.copy()` makes a separate one.
:::
