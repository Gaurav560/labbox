:::step{type=story title="How does your music app know what plays next?"}
Your music app has a queue. Your chat app has a list of messages. A shop has a cart. A cricket scoreboard has
the batting order. Different apps, the same idea underneath: **many things, kept in order, in one place**.

In Python that idea is a **list**, and you have already met small ones: `[120, 80, 100]`. Today you see how
lists really behave: how to add and remove things, how to sort them, and one famous surprise that catches
almost every beginner (and plenty of professionals).


Before music apps, there was the **jukebox**: a cabinet of records kept in order, waiting in a queue for the next
coin. The queue of songs you chose was a list.

:::photo{src="/lesson-images/python/jukebox.webp" alt="An old wooden jukebox cabinet with a glass window and chrome bars, standing in a wood-panelled room" credit="Ɱ" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Wurlitzer_jukebox.jpg"}
A Wurlitzer jukebox: a list of songs, played in order.
:::
:::mission
Write `remove_duplicates`, which keeps each item once, and `top_n`, which finds the biggest amounts without
spoiling the original list.
:::
:::

:::step{type=concept title="A list keeps many values in order"}
A list is written with square brackets, items separated by commas:

```python
cart = ["rice", "milk", "bread"]
amounts = [120, 45, 900]
mixed = ["rice", 15, True]      # allowed, but rarely a good idea
empty = []
```

Everything you learned about strings in chapter 7 works on lists too, because both are **sequences**:

```python
len(cart)        # 3
cart[0]          # "rice": positions start at 0
cart[-1]         # "bread": the last one
cart[1:3]        # ["milk", "bread"]: a slice is a new list
"rice" in cart   # True
```

But there is one big difference. Strings never change. Lists **can**: you can add, remove and replace items in
the same list. Programmers say lists are **mutable**.

:::picture{name="egg-box"}
A list is like an egg box: numbered slots in a row, and you can take out or put in an egg at any slot.
:::
:::

:::step{type=try title="Fill a cart" file="08-lists/cart.py" line="2-12"}
Open `cart.py` and run it:

```bash run
cd /workspace/08-lists && python3 cart.py
```

```text
['rice', 'milk', 'bread'] 3
['rice', 'milk', 'bread', 'eggs']
['rice', 'bread', 'eggs']
rice eggs ['bread', 'eggs']
True False
```

Follow the cart as it changes: `append("eggs")` added at the end, `remove("milk")` took the milk out, and the
whole time it was the **same list**, changing in place. Now add a line of your own, like
`cart.insert(0, "salt")`, and guess what it prints before you run it.
:::

:::step{type=concept title="The list toolbox"}
Here are the tools you will use every day. All of them change the list in place:

| Code | Does | `cart` afterwards (from `["rice", "milk"]`) |
|---|---|---|
| `cart.append("eggs")` | adds at the end | `["rice", "milk", "eggs"]` |
| `cart.insert(0, "salt")` | adds at a position | `["salt", "rice", "milk"]` |
| `cart.remove("rice")` | removes the first match | `["milk"]` |
| `cart.pop()` | removes the last and gives it back | `["rice"]`, and gives back `"milk"` |
| `cart[0] = "coffee"` | replaces one item | `["coffee", "milk"]` |
| `cart.extend(["jam", "salt"])` | adds several | `["rice", "milk", "jam", "salt"]` |

Two things to know:

- `remove` and `cart[5]` on an item or a position that does not exist both stop with an error (`ValueError`,
  `IndexError`). Check with `in` or `len` first when you are not sure.
- These methods change the list and give back `None` (except `pop`, which gives back what it took). So
  `cart = cart.append("x")` is a classic bug: it stores `None` in `cart`.
:::

:::step{type=example title="Worked example: build a new list as you go"}
Very often you do not change a list: you **build a new one** from it, with a loop and `append`. Here is a
function that keeps only the big expenses:

```python
def big_ones(amounts):
    result = []
    for amount in amounts:
        if amount > 500:
            result.append(amount)
    return result

big_ones([120, 900, 45, 600])    # gives back [900, 600]
```

It is chapter 5's before / inside / after pattern, with a list as the answer:

1. **Before:** an empty list, `result = []`.
2. **Inside:** for each amount, `append` it when it passes the test.
3. **After:** return the finished list. The original list is untouched.

The order is kept, because the loop visits the items in order and `append` always adds at the end.
:::

:::step{type=predict title="Guess first"}
:::question
In the loop above, the test is `if amount > 500`. Which test would keep each item **only once**, building the
`result` list as you go?
:::
- [ ] `if amount in amounts`
- [x] `if amount not in result`
- [ ] `if result.count(amount) > 1`
:::explain
`result` holds what you have kept so far. Append an item only when it is **not in** `result` yet, and every
item lands there once, in the order it first appeared.
:::
:::

:::step{type=task task=remove_duplicates title="Your turn: each item once"}
Open `lists.py` and make `remove_duplicates(items)` give back a new list with each item once, in the order
they first appeared.

`remove_duplicates([3, 1, 3, 2, 1])` gives `[3, 1, 2]`, and `remove_duplicates(["rice", "coffee", "rice"])` gives
`["rice", "coffee"]`.

```bash run
cd /workspace/08-lists && python3 -c "from lists import remove_duplicates; print(remove_duplicates([3, 1, 3, 2, 1]))"
```

Then press **Check**.
:::

:::step{type=concept title="Sorting, and a list with two names" file="08-lists/same_list.py" line="2-5"}
Python can sort a list in two ways, and the difference matters:

```python
amounts = [300, 45, 900]
sorted(amounts)          # gives back a NEW list: [45, 300, 900]; amounts is unchanged
amounts.sort()           # sorts amounts ITSELF, and gives back None
```

Add `reverse=True` to either one for biggest first. And remember the classic bug from the toolbox:
`result = amounts.sort()` stores `None`.

Now the famous surprise. Open `same_list.py`:

```python
mine = ["rice", "milk"]
yours = mine
yours.append("cake")
print(mine)
```

Did you expect `["rice", "milk"]`? It prints `['rice', 'milk', 'cake']`. The line `yours = mine` does **not**
copy the list. It gives the **same** list a second name. Both names point at one list in memory, so a change
through one name shows through the other.

:::diagram{name="shared-list"}
Two names, one list: = shares it; a.copy() makes a second, separate list.
:::

When you really want a separate list, ask for a copy: `yours = mine.copy()` (or `sorted(mine)`, which also
makes a new list). This matters most inside functions: a function that sorts the list it was given changes the
caller's list too, which is rude and causes very confusing bugs.
:::

:::step{type=try title="See two names, one list" file="08-lists/same_list.py" line="2-5"}
Run it and see for yourself:

```bash run
cd /workspace/08-lists && python3 same_list.py
```

```text
['rice', 'milk', 'cake']
```

Now change `yours = mine` to `yours = mine.copy()` and run it again: `mine` stays `['rice', 'milk']`. One method
call, two completely different programs.
:::

:::step{type=task task=top_n title="Your turn: the biggest amounts"}
In `lists.py`, make `top_n(numbers, n)` give back the `n` biggest numbers, biggest first, **without changing**
the list it was given.

`top_n([72, 45, 90, 66], 2)` gives `[90, 72]`. Asking for more than there are gives them all:
`top_n([5, 1], 5)` gives `[5, 1]`. And `n = 0` gives `[]`.

You need two tools from this chapter: a sort that makes a **new** list, biggest first, and a slice that keeps
the first `n` items.

```bash run
cd /workspace/08-lists && python3 -c "from lists import top_n; m = [72, 45, 90, 66]; print(top_n(m, 2), m)"
```

The second thing printed must still be `[72, 45, 90, 66]`. Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `nums = [3, 1, 2]; result = nums.sort(); print(result)` print?
:::
- [ ] `[1, 2, 3]`
- [x] `None`
- [ ] `[3, 1, 2]`
:::explain
`.sort()` sorts the list itself and gives back `None`. Use `sorted(nums)` when you want the sorted list as a
value.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
After `a = [1, 2]`, `b = a`, `b.append(3)`, what is `a`?
:::
- [ ] `[1, 2]`
- [x] `[1, 2, 3]`
:::explain
`b = a` gives the same list a second name. Appending through `b` changes the one list both names share.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `[10, 20, 30, 40][1:3]`?
:::
- [ ] `[10, 20, 30]`
- [x] `[20, 30]`
- [ ] `[20, 30, 40]`
:::explain
The slice starts at position 1 (`20`) and stops before position 3: `[20, 30]`.
:::
:::

:::step{type=deep-dive title="Go deeper: why in gets slow, and lists inside lists"}
**How `in` works on a list.** To answer `"x" in my_list`, Python checks the items one by one from the start.
For three items, that is instant. For a million items checked a million times, it adds up. In chapter 10 you
will meet **sets**, which answer `in` almost instantly however big they are, and see real timings.

**Lists inside lists.** An item of a list can itself be a list. That is how you store a small table:

```python
week = [["Mon", 120], ["Tue", 450]]
week[1]        # ["Tue", 450]
week[1][0]     # "Tue"
```

Read `week[1][0]` left to right: the item at 1, then *its* item at 0. In chapter 9 you will see a clearer way
to store records like these, with names instead of positions.

**Copies of copies.** `.copy()` makes a **shallow** copy: a new outer list, but the inner lists are still
shared. For lists of lists, `copy.deepcopy(...)` copies everything. You will rarely need it; when a change
seems to appear in two places at once, remember this page.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Make lists, read them by position and slice, and ask `in`.
- Change a list in place with `append`, `insert`, `remove`, `pop` and `[i] = ...`.
- Build a new list with a loop and `append`, keeping the order.
- Sort with `sorted(...)` (new list) or `.sort()` (in place, gives back `None`), and copy before you change a
  list someone gave you, because `b = a` is one list with two names.

:::photo{src="/lesson-images/python/py-08-notes.webp" alt="Handwritten notes about Python lists: append, sorted versus sort, and two names for one list" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 9: dictionaries, where you find things by name instead of by position.
:::
