:::step{type=story title="How does your phone find one contact among five hundred, instantly?"}
Scroll through five hundred contacts looking for "Ravi" and it takes a while. Type "Ravi" into the search and
he appears at once. The phone did not read every contact from the top: it looked him up **by name**.

Lists find things by position: item 0, item 1, item 2. But real life is full of things you find by a name or a
label: the price of juice, the phone number of Ravi, how much you spent on food. For those, Python has the
**dictionary**, and it is so useful that big Python programs are mostly made of them.

:::mission
Write `count_letters`, which counts every letter in a piece of text, and `total_by_category`, which tells
Pocket how much you spent on food, travel and everything else.
:::
:::

:::step{type=concept title="A dictionary: keys and values"}
A dictionary (a **dict**) stores pairs: a **key**, and the **value** that belongs to it. You write it with curly
braces, a colon between each key and its value:

```python
prices = {"juice": 15, "samosa": 20, "coffee": 30}
```

Now you look things up by key, in square brackets:

```python
prices["juice"]          # 15
prices["vada"] = 25    # adds a new pair
prices["juice"] = 18     # the key exists, so its value is replaced
len(prices)            # 4 pairs
```

Three rules make dictionaries work:

- **Keys are unique.** Each key appears once. Storing a value under an existing key replaces the old value.
- **Lookups are by key, not position.** `prices[0]` does not mean "the first pair"; it looks for a key `0`.
- **Keys must be values that never change**, like strings and numbers. A list cannot be a key: Python says
  `TypeError: unhashable type: 'list'`.

:::picture{name="phone-book"}
A dictionary is a phone book: you look up a name (the key) and find the number (the value) straight away.
:::
:::

:::step{type=try title="A price list" file="09-dictionaries/prices.py" line="2-13"}
Open `prices.py` and run it:

```bash run
cd /workspace/09-dictionaries && python3 prices.py
```

```text
15
{'juice': 18, 'samosa': 20, 'coffee': 30, 'vada': 25}
juice    ₹18
samosa   ₹20
coffee   ₹30
vada     ₹25
0
Traceback (most recent call last):
  File "/workspace/09-dictionaries/prices.py", line 13, in <module>
    print(prices["cake"])
          ~~~~~~^^^^^^^^
KeyError: 'cake'
```

Read it top to bottom. Juice cost 15, then the price list grew a `vada` and juice went up to 18. The loop printed a
neat menu (the `<8` from chapter 7 lines up the names). `prices.get("cake", 0)` gave `0`. And the last line
crashed: asking for a key that does not exist with square brackets raises a **KeyError**, which names the
missing key. Which brings us to the most useful method of all.
:::

:::step{type=concept title="get, in, and looping over pairs"}
When a key might be missing, you have two polite ways to ask:

```python
prices.get("cake")        # None: no crash
prices.get("cake", 0)     # 0: you choose what "missing" means
"cake" in prices          # False: in checks the KEYS
```

Careful: `in` looks at **keys** only. `15 in {"juice": 15}` is `False`, because 15 is a value, not a key.

To go through a dictionary, loop over its pairs with `.items()`. Each lap gives you a key and its value, and
you can name them both at once:

```python
for item, price in prices.items():
    print(item, price)
```

There are also `.keys()` and `.values()` when you only need one side. And since Python 3.7, a dictionary
remembers the **order** you added things in, so your loops come out in a predictable order.
:::

:::step{type=example title="Worked example: counting with a dictionary"}
Here is the most famous dictionary pattern in Python: **counting**. How many of each drink did the shop sell?

```python
orders = ["juice", "coffee", "juice", "vada", "juice"]
counts = {}
for o in orders:
    counts[o] = counts.get(o, 0) + 1
print(counts)    # {'juice': 3, 'coffee': 1, 'vada': 1}
```

The middle line does all the work: "look up the count so far, or 0 if this is the first time; add 1; store it
back". Press Play and watch the dictionary fill up:

:::trace{title="counting the orders"}
| o | counts.get(o, 0) | counts | note |
|---|---|---|---|
|  |  | {} | Before the loop: an empty dictionary. |
| juice | 0 | {'juice': 1} | First juice: not there yet, so 0 + 1. |
| coffee | 0 | {'juice': 1, 'coffee': 1} | A new key appears. |
| juice | 1 | {'juice': 2, 'coffee': 1} | juice was 1, now 2. |
| vada | 0 | {'juice': 2, 'coffee': 1, 'vada': 1} | Another new key. |
| juice | 2 | {'juice': 3, 'coffee': 1, 'vada': 1} | juice reaches 3. |
:::

One line, any number of different things to count. Your first task counts letters the same way.
:::

:::step{type=predict title="Guess first"}
:::question
With `counts = {"juice": 3}`, what does `counts.get("milk", 0) + 1` give?
:::
- [ ] A `KeyError`
- [x] `1`
- [ ] `None`
:::explain
`get` does not crash on a missing key: it gives back the default you chose, `0`, and `0 + 1` is `1`. That is
exactly why the counting pattern works on the first sighting of a new item.
:::
:::

:::step{type=task task=count_letters title="Your turn: count every letter"}
Open `dict_tools.py` and make `count_letters(text)` give back a dictionary of how many times each **letter**
appears.

- Count only letters: skip spaces, digits and punctuation. `"a".isalpha()` is `True`; `"!".isalpha()` is
  `False`.
- Count capital and small letters together, as small letters: `"A a"` gives `{"a": 2}`.

`count_letters("Hello!")` gives `{"h": 1, "e": 1, "l": 2, "o": 1}`, and `count_letters("123 ?!")` gives `{}`.

```bash run
cd /workspace/09-dictionaries && python3 -c "from dict_tools import count_letters; print(count_letters('Hello!'))"
```

Then press **Check**.
:::

:::step{type=concept title="Records: one dictionary per thing"}
Dictionaries are also perfect for describing **one thing** with several facts, by name:

```python
expense = {"category": "food", "amount": 120}
expense["amount"]       # 120
```

Compare that with a list like `["food", 120]`: what is position 1 again? With a dictionary, the code says what
it means. A list of such dictionaries is how real data usually arrives: from a file, a website, a database:

```python
expenses = [
    {"category": "food", "amount": 120},
    {"category": "travel", "amount": 40},
    {"category": "food", "amount": 80},
]
```

You loop over the list, and in each lap you read the record's fields by name: `e["category"]`, `e["amount"]`.
:::

:::step{type=task task=total_by_category title="Your turn: spending per category"}
In `dict_tools.py`, make `total_by_category(expenses)` give back a dictionary with the total spent per
category. Each expense looks like `{"category": "food", "amount": 120}`.

For the three expenses above, it gives `{"food": 200, "travel": 40}`, and an empty list gives `{}`.

It is the counting pattern again, with one change: instead of adding 1, add the expense's amount.

```bash run
cd /workspace/09-dictionaries && python3 -c "from dict_tools import total_by_category; print(total_by_category([{'category': 'food', 'amount': 120}, {'category': 'travel', 'amount': 40}, {'category': 'food', 'amount': 80}]))"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `{"juice": 15}["coffee"]` do?
:::
- [ ] Gives `None`
- [ ] Gives `0`
- [x] Raises a `KeyError`
:::explain
Square brackets demand the key. When it is missing, Python raises `KeyError: 'coffee'`. Use `.get("coffee")`
or `"coffee" in ...` when a key might not be there.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is `prices` after `prices = {"juice": 15}` and `prices["juice"] = 20`?
:::
- [x] `{"juice": 20}`
- [ ] `{"juice": 15, "juice": 20}`
- [ ] `{"juice": [15, 20]}`
:::explain
Keys are unique: storing under an existing key replaces its value.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `15 in {"juice": 15}` give?
:::
- [ ] `True`
- [x] `False`
:::explain
`in` checks the keys. `"juice" in {"juice": 15}` is `True`; to search the values, use `15 in d.values()`.
:::
:::

:::step{type=deep-dive title="Go deeper: why dictionaries are so fast"}
A dictionary does not search its keys one by one. When you store a key, Python works out a number from it, its
**hash**, and uses that number to decide where in memory the pair goes. Looking a key up repeats the same
calculation and goes straight there. That is why a dictionary with ten million keys answers `prices["juice"]` as
quickly as one with three. It is also why keys must never change: a key that changed would have a different
hash, and Python would look for it in the wrong place.

Dictionaries look almost exactly like **JSON**, the text format websites use to send data:
`{"category": "food", "amount": 120}` is valid in both. Python's `json` module turns one into the other with a
single call, which is why Python is so popular for working with web APIs.

There is also a tidy way to build a dictionary in one line, a **dict comprehension**:
`{item: price * 2 for item, price in prices.items()}`. You will meet its cousin, the list comprehension, in
chapter 11.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Store and look up values by key with `d[key]`, and add or replace pairs with `d[key] = value`.
- Ask safely with `d.get(key, default)` and `key in d`, and loop over pairs with `for k, v in d.items()`.
- Count anything with `counts[x] = counts.get(x, 0) + 1`, and total by group the same way.
- Describe a record with a dictionary, and work through a list of them.

:::photo{src="/lesson-images/python/py-09-notes.webp" alt="Handwritten notes about Python dictionaries: keys, values, get and items" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 10: tuples and sets, two small collections with special powers.
:::
