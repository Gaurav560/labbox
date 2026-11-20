:::step{type=story title="Why lists"}
A class has 40 marks, a shop has a menu, your phone has a contact list. Whenever you have many
values of the same kind, you keep them in a **list**, and most programs spend their time sorting,
filtering and picking from lists.

:::mission
Write two functions in `lists.py`: one picks the n biggest numbers, and one removes duplicates while
keeping the original order.
:::
:::

:::step{type=concept title="Making and changing lists"}
A list keeps items in order, and you can change it:

```python
marks = [72, 45, 90]
marks.append(66)        # [72, 45, 90, 66]
marks.remove(45)        # [72, 90, 66]   (the first 45)
marks[0] = 75           # [75, 90, 66]
len(marks)              # 3
marks[-1]               # 66, the last item
marks[:2]               # [75, 90], a slice is a new list
```

`in` asks whether an item is there: `90 in marks` is `True`.
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
`b = a` does not copy the list: both names point to the **same** list, so changing it through `b`
changes what `a` sees too. To get a separate copy, write `b = a.copy()` or `b = a[:]`.
:::
:::

:::step{type=try title="sort() and sorted()"}
Two ways to sort, with one big difference:

```bash run
python3 -c "
marks = [72, 45, 90]
print(sorted(marks, reverse=True), marks)   # a new list; marks is untouched
marks.sort()
print(marks)                                # marks itself is now sorted
"
```

`sorted(list)` gives back a **new** sorted list. `list.sort()` sorts the list **in place** and
gives back `None`.
:::

:::step{type=task task=top_n title="The n biggest numbers"}
In `lists.py`, make `top_n(numbers, n)` return the `n` biggest numbers, **biggest first**, without
changing the list it was given.

- `top_n([72, 45, 90, 66], 2)` returns `[90, 72]`
- `top_n([5, 1], 5)` returns `[5, 1]` (asking for more than there are is fine)
- `top_n([3, 1, 2], 0)` returns `[]`
- after `top_n(marks, 2)`, `marks` must still be in its original order

:::why
Functions that quietly change their inputs cause some of the hardest bugs: the caller's list
changes "by itself" somewhere else in the program.
:::
:::

:::step{type=concept title="List comprehensions"}
Building a list from another list is so common that Python has a short form for it:

```python
marks = [72, 45, 90, 30]
passed = [m for m in marks if m >= 40]    # [72, 45, 90]
doubled = [m * 2 for m in marks]          # [144, 90, 180, 60]
```

Read it as "m, for each m in marks, if m >= 40". It does exactly what a loop with `append` does,
in one line.
:::

:::step{type=task task=remove_duplicates title="Remove duplicates, keep the order"}
In `lists.py`, make `remove_duplicates(items)` return a new list with each item only once, in the
order it **first** appeared.

- `remove_duplicates([3, 1, 3, 2, 1])` returns `[3, 1, 2]`
- `remove_duplicates(["tea", "coffee", "tea"])` returns `["tea", "coffee"]`
- `remove_duplicates([])` returns `[]`
:::

:::step{type=deep-dive title="How a Python list works inside"}
A list is an array of references that grows by **over-allocating**: when it fills up, Python makes
room for several more items at once. That is why `append` is fast on average, and why adding at the
front with `insert(0, x)` is slow: every item has to move one place.

`x in my_list` checks the items one by one, so it gets slower as the list grows. In
`remove_duplicates`, checking `in` a list of 100,000 items for each new item adds up. For big data
you would keep a **set** of the items seen so far (next chapters) alongside the result list: a set
answers `in` almost instantly.

Sorting uses **Timsort**, which is very fast on data that is already partly in order, and it is
**stable**: items that compare equal keep their original order.
:::

:::step{type=recap}
- Lists keep items in order: `append`, `remove`, indexing, slicing, `len`, `in`.
- `b = a` shares one list; `a.copy()` makes a separate one.
- `sorted()` returns a new list; `.sort()` changes the list and returns `None`.
- A comprehension `[x for x in items if ...]` builds a list in one line.
:::
