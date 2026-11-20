:::step{type=story title="Why dictionaries"}
A list answers "what is the third item?". Most real questions are different: "what is Riya's
phone number?", "how much did I spend on food?". A **dictionary** looks values up by a name, and
it is the most used data structure in Python.

:::mission
Write two functions in `dict_tools.py`: one counts each letter in a text, and one adds up spending
per category.
:::
:::

:::step{type=concept title="Keys and values"}
A dictionary maps **keys** to **values**:

```python
phone = {"Riya": "98765 43210", "Arjun": "91234 56789"}
phone["Riya"]               # '98765 43210'
phone["Meera"] = "99887 76655"   # add or change
"Arjun" in phone            # True: checks the keys
len(phone)                  # 3
```

Asking for a key that is not there with `phone["Kabir"]` raises a `KeyError`. `phone.get("Kabir")`
gives `None` instead, and `phone.get("Kabir", "unknown")` gives your own default.

:::picture{name="phone-book"}
Look up a key to find its value.
:::
:::

:::step{type=example title="Worked example: count the words"}
Counting with a dictionary always looks like this:

```python
def count_words(words):
    counts = {}                   # 1. empty dictionary
    for w in words:               # 2. each word
        counts[w] = counts.get(w, 0) + 1   # 3. one more
    return counts

count_words(["tea", "coffee", "tea"])
# {'tea': 2, 'coffee': 1}
```

1. Start with an empty dictionary.
2. Look at each item.
3. `counts.get(w, 0)` is the count so far, or `0` the first time; add one and store it back.

`count_letters` is this pattern, plus deciding which characters count.

:::trace{title='count_words(["tea", "coffee", "tea"])'}
| w | counts.get(w, 0) | counts | note |
|---|---|---|---|
|  |  | {} | Start with an empty dictionary. |
| tea | 0 | {'tea': 1} | tea is new, so get gives 0; 0 + 1 is stored. |
| coffee | 0 | {'tea': 1, 'coffee': 1} | coffee is new too. |
| tea | 1 | {'tea': 2, 'coffee': 1} | tea is already 1: 1 + 1 = 2, stored back under tea. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What is `counts` after this code?

```python
counts = {}
for word in ["tea", "coffee", "tea"]:
    counts[word] = counts.get(word, 0) + 1
```
:::
- [ ] `{"tea": 1, "coffee": 1}`
- [x] `{"tea": 2, "coffee": 1}`
- [ ] A `KeyError`
- [ ] `{"tea": 2}`
:::explain
The first time a word is seen, `counts.get(word, 0)` gives `0`, so it becomes `1`. The next time
it gives the count so far. This "get with a default, then add" line is the classic way to count
things with a dictionary.
:::
:::

:::step{type=try title="Loop over a dictionary"}
```bash run
python3 -c "
prices = {'tea': 15, 'coffee': 30, 'samosa': 20}
for name, price in prices.items():
    print(name, price)
print(list(prices.keys()), sum(prices.values()))
"
```

`.items()` gives each key with its value, `.keys()` the keys and `.values()` the values.
:::

:::step{type=task task=count_letters title="Count each letter"}
In `dict_tools.py`, make `count_letters(text)` return a dictionary with how many times each letter
appears. Count upper and lower case as the same letter (use lower case keys) and ignore everything
that is not a letter.

- `count_letters("Hello!")` returns `{"h": 1, "e": 1, "l": 2, "o": 1}`
- `count_letters("A a")` returns `{"a": 2}`
- `count_letters("123 ?!")` returns `{}`
:::

:::step{type=concept title="Lists of dictionaries"}
Real data often comes as a list of small dictionaries, one per row:

```python
expenses = [
    {"category": "food", "amount": 120},
    {"category": "travel", "amount": 40},
    {"category": "food", "amount": 80},
]
for e in expenses:
    print(e["category"], e["amount"])
```

This is the same shape as a row from a spreadsheet, or a record from a web API.
:::

:::step{type=task task=total_by_category title="Total per category"}
In `dict_tools.py`, make `total_by_category(expenses)` return a dictionary of the total amount per
category.

- for the three expenses above it returns `{"food": 200, "travel": 40}`
- `total_by_category([])` returns `{}`
- amounts can be decimals: `120.5` and `0.5` in the same category add up to `121.0`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `{"a": 1}.get("b", 0)`?
:::
- [ ] `1`
- [x] `0`
- [ ] `None`
- [ ] A KeyError
:::explain
`b` is not a key, so `get` gives the default you passed: `0`. Square brackets would raise a KeyError instead.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `len({"x": 1, "y": 2})`?
:::
- [ ] `1`
- [x] `2`
- [ ] `3`
- [ ] `4`
:::explain
`len` counts the keys of a dictionary: two.
:::
:::

:::step{type=deep-dive title="Why dictionaries are so fast"}
A dictionary is a **hash table**. Python turns each key into a number with `hash(key)` and uses it to
jump almost straight to the right slot, so looking up one key among a million takes about as long
as among ten.

That is why keys must be **immutable** (strings, numbers, tuples): if a key could change, its hash
would change and it could never be found again. A list cannot be a key; a tuple of the same values
can.

Since Python 3.7, dictionaries also **remember insertion order**, so looping over one gives keys in
the order they were added. Counting is common enough that the standard library has a ready tool for
it: `collections.Counter("hello")` does in one call what `count_letters` does by hand.
:::

:::step{type=recap}
- A dictionary maps keys to values: `d[key]`, `d[key] = value`, `key in d`.
- `d.get(key, default)` avoids a `KeyError`.
- `counts[k] = counts.get(k, 0) + 1` counts things.
- `.items()`, `.keys()`, `.values()` loop over a dictionary.
:::
