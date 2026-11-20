:::step{type=story title="Why tuples and sets"}
Two more containers finish the set. A **tuple** is a small fixed group of values, like a point
`(x, y)` or a function returning two answers at once. A **set** keeps each item only once and is
perfect for questions like "who was in both classes?".

:::mission
Write two functions in `sets_tuples.py`: one finds the items two lists share, and one returns the
smallest and largest number together.
:::
:::

:::step{type=concept title="Tuples"}
A tuple is like a list that cannot change, written with round brackets:

```python
point = (3, 4)
point[0]          # 3
name, age = ("Riya", 17)     # unpacking: name is 'Riya', age is 17
```

Functions return a tuple to give back more than one value:

```python
def split_marks(marks):
    return min(marks), max(marks)      # the brackets are optional

low, high = split_marks([72, 45, 90])  # low is 45, high is 90
```
:::

:::step{type=predict title="Guess first"}
:::question
What is `len({3, 1, 3, 2, 1})`?
:::
- [ ] `5`
- [x] `3`
- [ ] `2`
- [ ] An error
:::explain
A set keeps each value once, so `{3, 1, 3, 2, 1}` is just `{1, 2, 3}`, which has 3 items. That is
why `len(set(items))` is a quick way to count how many **different** values a list has.
:::
:::

:::step{type=try title="Set operations"}
```bash run
python3 -c "
mon = {'Riya', 'Arjun', 'Meera'}
tue = {'Arjun', 'Kabir', 'Meera'}
print('both days :', sorted(mon & tue))
print('either day:', sorted(mon | tue))
print('only mon  :', sorted(mon - tue))
"
```

`&` is "in both", `|` is "in either", `-` is "in the first but not the second". Sets have **no
order**, so we `sorted()` them to print them the same way every time.
:::

:::step{type=task task=common_items title="What two lists share"}
In `sets_tuples.py`, make `common_items(a, b)` return a **sorted list** of the items that appear in
both lists, each only once.

- `common_items(["tea", "coffee", "milk"], ["milk", "tea", "juice"])` returns `["milk", "tea"]`
- `common_items([1, 2, 2, 3], [2, 2, 4])` returns `[2]`
- `common_items([1, 2], [3, 4])` returns `[]`
:::

:::step{type=concept title="Empty cases and None"}
`min([])` and `max([])` raise a `ValueError`, because an empty list has no smallest value. A
friendly function decides what "no answer" looks like and checks for it first:

```python
def first_or_none(items):
    if not items:          # an empty list is falsy
        return None
    return items[0]
```

For a function that returns two values, "no answer" can be `(None, None)`.
:::

:::step{type=task task=min_max title="Smallest and largest, together"}
In `sets_tuples.py`, make `min_max(numbers)` return a **tuple** `(smallest, largest)`.

- `min_max([72, 45, 90])` returns `(45, 90)`
- `min_max([7])` returns `(7, 7)`
- `min_max([])` returns `(None, None)`
- `min_max([-3, -10, 4.5])` returns `(-10, 4.5)`
:::

:::step{type=deep-dive title="When to use which container"}
| Need | Use |
|---|---|
| items in order, may repeat, will change | `list` |
| a small fixed group, or a dictionary key | `tuple` |
| each item once, fast "is it in there?" | `set` |
| look values up by a key | `dict` |

Sets and dictionary keys work the same way inside (hash tables), so `x in some_set` is fast even
with a million items, while `x in some_list` checks them one by one.

A `frozenset` is a set that cannot change, so it can itself be a dictionary key or live inside
another set. And `{}` makes an empty **dictionary**, not a set: an empty set is `set()`.
:::

:::step{type=recap}
- Tuples are fixed groups: `(a, b)`, unpacked with `x, y = pair`.
- Returning `a, b` from a function returns a tuple.
- Sets keep items once: `&` both, `|` either, `-` difference; they have no order.
- Decide what "no answer" means (`None`, `(None, None)`) and check the empty case first.
:::
