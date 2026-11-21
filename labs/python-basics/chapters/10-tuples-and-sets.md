:::step{type=story title="Which customers came on both days?"}
A chai shop keeps a list of who visited on Monday and who visited on Tuesday. The owner asks a simple question:
"Who came on **both** days?" With what you know, you would write a loop inside a loop, checking every Monday name
against every Tuesday name. It works. It is also slow and fiddly.

Python has a collection that answers that question in **one line**, and answers "is this name here?" almost
instantly even for millions of names. It also has a tiny collection for small, fixed groups of values, like a
date or a receipt line. Today: **sets** and **tuples**, two small tools with special powers.

:::mission
Write `common_items`, which finds what two lists share, and `min_max`, which gives back two answers at once.
:::
:::

:::step{type=concept title="Tuples: small groups that never change" file="10-tuples-and-sets/receipt_line.py" line="2-6"}
A **tuple** is like a list in round brackets, with one difference: it can never change. Open `receipt_line.py`:

```python
line = ("Masala chai", 2, 15.0)
name, quantity, price = line
print(name, "x", quantity, "=", quantity * price)
print(line[0], len(line))
line[1] = 3
```

Tuples are for a **fixed group** of values that belong together: one receipt line (name, quantity, price), a
point `(3, 4)`, a date `(2026, 11, 22)`. You read them by position like a list, but changing one fails.

The second line shows the best trick of tuples, **unpacking**: put several names on the left of `=`, and each
gets one value, in order. It reads far better than `line[0]`, `line[1]`, `line[2]`.

Run it:

```bash run
cd /workspace/10-tuples-and-sets && python3 receipt_line.py
```

```text
Masala chai x 2 = 30.0
Masala chai 3
Traceback (most recent call last):
  File "/workspace/10-tuples-and-sets/receipt_line.py", line 6, in <module>
    line[1] = 3
    ~~~~^^^
TypeError: 'tuple' object does not support item assignment
```

Unpacking worked, reading worked, changing failed, exactly as promised. That refusal is a feature: a tuple you
pass around cannot be changed by accident somewhere else.
:::

:::step{type=example title="Worked example: returning two answers"}
Here is where tuples shine every day. A function can only `return` one value, but that value can be a tuple, so
a function can effectively give back **several answers**:

```python
def first_and_last(names):
    if not names:
        return (None, None)
    return (names[0], names[-1])

first, last = first_and_last(["Asha", "Ravi", "Meera"])
print(first, last)     # Asha Meera
```

1. The function packs two values into one tuple.
2. The caller unpacks them straight into two names.
3. For an empty list there is no first or last, so it returns `(None, None)`: still two values, so the caller's
   unpacking still works.

Python also has `min(...)` and `max(...)` built in: `min([72, 45, 90])` is `45` and `max(...)` is `90`. They raise
an error on an empty list, which is why an empty check comes first.

A neat bonus of unpacking: swapping two variables needs no temporary variable. `a, b = b, a` swaps them.
:::

:::step{type=task task=min_max title="Your turn: smallest and largest together"}
Open `sets_tuples.py` and make `min_max(numbers)` give back a tuple `(smallest, largest)`, or `(None, None)` for
an empty list.

`min_max([72, 45, 90])` gives `(45, 90)`, and `min_max([])` gives `(None, None)`.

```bash run
cd /workspace/10-tuples-and-sets && python3 -c "from sets_tuples import min_max; low, high = min_max([72, 45, 90]); print(low, high)"
```

Then press **Check**.
:::

:::step{type=concept title="Sets: each thing once, and instant questions" file="10-tuples-and-sets/visits.py" line="2-9"}
A **set** is a collection where every item appears **at most once**, and order does not exist. You write it with
curly braces, or make one from a list with `set(...)`:

```python
{1, 2, 2, 3}           # {1, 2, 3}: the extra 2 simply vanishes
set(["tea", "tea"])    # {'tea'}
```

Three things make sets special:

- **No duplicates.** Turning a list into a set removes repeats.
- **No order.** A set has no first item and no positions. Python may even print the same set in a different
  order each time the program runs, so when you want a predictable order, wrap it in `sorted(...)`.
- **Set maths.** Sets understand "both", "either" and "only":

| Code | Means | Monday and Tuesday visitors |
|---|---|---|
| `a & b` | in both | `['Meera', 'Ravi']` |
| `a \| b` | in either | `['Asha', 'Kabir', 'Meera', 'Ravi']` |
| `a - b` | in `a` but not in `b` | `['Asha']` |

:::picture{name="guest-list"}
A set is a guest list: each name is on it once, and nobody cares in which order the names were written.
:::
:::

:::step{type=try title="Who came when?" file="10-tuples-and-sets/visits.py" line="2-9"}
Run the shop's question:

```bash run
cd /workspace/10-tuples-and-sets && python3 visits.py
```

```text
4 3
['Asha', 'Meera', 'Ravi']
both days: ['Meera', 'Ravi']
either day: ['Asha', 'Kabir', 'Meera', 'Ravi']
only Monday: ['Asha']
```

The first line says it all: four visits on Monday, but only three different people, because Asha came twice.
Every question after that is one line. Try adding a Wednesday list and asking who came on all three days.
:::

:::step{type=predict title="Guess first"}
:::question
What does `sorted(set([3, 1, 3, 2, 1]))` give?
:::
- [ ] `[3, 1, 2]`
- [x] `[1, 2, 3]`
- [ ] `[1, 1, 2, 3, 3]`
:::explain
The set keeps each number once (`{1, 2, 3}`), and `sorted` turns it into a list in order. Note that the original
order, 3 then 1, is lost: sets do not keep order. When you need "each once, in the original order", use the loop
from chapter 8 instead.
:::
:::

:::step{type=task task=common_items title="Your turn: what both lists share"}
In `sets_tuples.py`, make `common_items(a, b)` give back a **sorted list** of the items that appear in both
lists, each once.

`common_items(["tea", "coffee", "milk"], ["milk", "tea", "juice"])` gives `["milk", "tea"]`, and
`common_items([1, 2, 2, 3], [2, 2, 4])` gives `[2]`.

Three moves: turn both into sets, keep what is in both, and give back a sorted list.

```bash run
cd /workspace/10-tuples-and-sets && python3 -c "from sets_tuples import common_items; print(common_items(['tea', 'coffee', 'milk'], ['milk', 'tea', 'juice']))"
```

Then press **Check**.
:::

:::step{type=concept title="Why sets are so fast"}
Remember chapter 8's warning, that `in` on a list checks the items one by one? A set does not search: like a
dictionary's keys (chapter 9), it uses each item's **hash** to jump straight to where the item would be. Here is
the difference, measured on the lab machine: looking up one number a thousand times, in a collection of 100,000
numbers:

| Collection | Time for 1,000 lookups |
|---|---|
| a set | about 0.015 milliseconds |
| a list | about 421 milliseconds |

That is roughly **28,000 times faster**. For three items you will never notice. For a list of every customer, every
order, every word in a book, it is the difference between instant and painfully slow.

So the rule of thumb: when the main question is "is this thing in my collection?", use a set.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which line fails?
:::
- [ ] `t = (1, 2, 3); print(t[0])`
- [x] `t = (1, 2, 3); t[0] = 9`
- [ ] `a, b, c = (1, 2, 3)`
:::explain
Tuples cannot change, so assigning to `t[0]` raises a `TypeError`. Reading and unpacking are fine.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is `len({"tea", "tea", "milk"})`?
:::
- [x] `2`
- [ ] `3`
:::explain
A set keeps each item once, so the second `"tea"` disappears: two items.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`a = {1, 2, 3}` and `b = {2, 3, 4}`. What is `sorted(a - b)`?
:::
- [x] `[1]`
- [ ] `[4]`
- [ ] `[1, 4]`
:::explain
`a - b` is "in `a` but not in `b`": only `1`. The items in either but not both would be `a ^ b`, which is `{1, 4}`.
:::
:::

:::step{type=deep-dive title="Go deeper: the comma makes the tuple"}
A surprise: the brackets do not make a tuple, the **comma** does.

```python
type((45, 90))    # <class 'tuple'>
type((45))        # <class 'int'>: just a number in brackets
type((45,))       # <class 'tuple'>: one item needs a trailing comma
```

That is also why `a, b = 1, 2` works without any brackets: `1, 2` is already a tuple.

Two more things worth knowing:

- An empty set is written `set()`, not `{}`: empty curly braces make an empty **dictionary**.
- Sets can only hold values that never change (like dictionary keys): numbers, strings, tuples. A set of lists
  is not allowed. That is the price of being fast.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Group fixed values in a tuple, read them by position, and unpack them into names.
- Return several answers from one function as a tuple, and swap values with `a, b = b, a`.
- Remove duplicates and ask "both / either / only" with sets and `& | -`.
- Choose a set when the main question is "is it in there?", because it is thousands of times faster than a list.

:::photo{src="/lesson-images/python/py-10-notes.webp" alt="Handwritten notes about tuples and sets: a fixed tuple, unpacking, a set removing duplicates, and items in both" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 11: sorting and comprehensions, the shortest way to reshape a whole list.
:::
