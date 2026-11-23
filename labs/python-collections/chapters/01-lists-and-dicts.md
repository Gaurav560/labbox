:::step{type=story title="900 meals a day"}
:::character{name="Priya" role="Founder, Thali House"}
We went from 300 to 900 meals a day, and my order sheet is a mess of copy and paste.
I need two answers every morning: how much each office owes, and which dishes to cook more of.
:::

:::mission
Add up a bill with a price list, and find the best-selling dishes.
:::
:::

:::step{type=concept title="Lists and dicts"}
A **list** keeps things in order, and can repeat them:

```python
order = ["veg thali", "dal rice", "veg thali"]
```

A **dict** maps a key to a value, so you can look something up by name:

```python
prices = {"veg thali": 120, "dal rice": 90}
prices["dal rice"]   # 90
```

Lists answer "what, in which order". Dicts answer "how much is this one".
:::

:::step{type=predict title="Guess first"}
:::question
`prices = {"veg thali": 120}`. What happens with `prices["poha"]`?
:::
- [ ] It gives `0`
- [ ] It gives `None`
- [x] It raises a `KeyError`
:::explain
Asking a dict for a key it does not have raises `KeyError`. Use `prices.get("poha", 0)` when a missing
key should mean a default value instead.
:::
:::

:::step{type=try title="Look around"}
`orders.py` has the price list and four empty functions. Run it to see the examples:

```bash run
python3 orders.py
```

Every line prints `None` for now. You will fill them in one by one.
:::

:::step{type=task task=total_bill title="Add up a bill"}
Make `total_bill(items, prices)` return the total price of a list of items.

`total_bill(["veg thali", "dal rice", "veg thali"], PRICES)` is `330`, and an empty order costs `0`.
:::

:::step{type=example title="Counting things"}
`collections.Counter` counts how often each value appears:

```python
from collections import Counter
Counter(["dal rice", "poha", "dal rice"])
# Counter({'dal rice': 2, 'poha': 1})
```

`sorted()` can sort pairs by anything you like with `key=`. A minus sign sorts numbers from high to low:

```python
sorted([("a", 1), ("b", 3)], key=lambda p: -p[1])   # [('b', 3), ('a', 1)]
```
:::

:::step{type=task task=top_dishes title="Best sellers"}
Make `top_dishes(orders, n)` return the `n` most ordered dishes, most ordered first.
When two dishes are tied, put them A to Z.

`top_dishes(["dal rice", "veg thali", "dal rice"], 1)` is `["dal rice"]`.
:::

:::step{type=recap}
- Lists keep order and repeats; dicts look values up by key.
- A missing dict key raises `KeyError`; `.get(key, default)` avoids it.
- `Counter` counts, and `sorted(..., key=...)` ranks by any rule you choose.
:::
