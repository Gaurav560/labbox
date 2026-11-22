:::step{type=story title="Can you write a whole loop in one line?"}
Here is a four-line loop you could already write: start an empty list, loop, check a condition, append. Python
programmers write that loop so often that the language has a shorter way to say it, in **one line** that reads
almost like English: "the amounts, for each amount in the week, if it is over 100".

And there is a second everyday question: sorting things that are not plain numbers. How do you sort expenses by
their amount? Words by their length? Customers by name? One small idea, the **key**, answers all of them.

:::mission
Write `large_expenses`, which picks out the big ones in one line, and `by_amount`, which sorts Pocket's expenses
biggest first.
:::
:::

:::step{type=concept title="Sorting by anything with key" file="11-sorting-and-comprehensions/spends.py" line="2-15"}
You know `sorted(amounts)` and `reverse=True` from chapter 8. Python sorts numbers by size and strings
alphabetically. But what if you want words by their **length**?

```python
words = ["samosa", "pav", "biryani"]
sorted(words, key=len)      # ['pav', 'samosa', 'biryani']
```

`key=len` means: "before comparing two items, pass each one through `len`, and compare **those** answers". Python
compares 6, 3 and 7, puts them in order, and gives back the original words in that order. The key can be any
function that takes one item and gives back something comparable.

Open `spends.py` and run it to see sorting and the rest of this chapter in action:

```bash run
cd /workspace/11-sorting-and-comprehensions && python3 spends.py
```

```text
[45, 80, 120, 300, 900]
[900, 300, 120, 80, 45]
[120, 45, 900, 300, 80]
[240, 90, 1800, 600, 160]
[120, 900, 300]
['pav', 'samosa', 'biryani']
```

Line three proves `sorted` left the original list alone. Lines four and five are comprehensions, coming next.
:::

:::step{type=concept title="lambda: a tiny function, right where you need it"}
To sort expenses by their amount, you need a key function that takes one expense and gives back its amount. You
could write one with `def`:

```python
def get_amount(expense):
    return expense["amount"]

sorted(expenses, key=get_amount)
```

For a one-line job like that, Python lets you write the function **inline**, without a name. It is called a
**lambda**:

```python
sorted(expenses, key=lambda e: e["amount"])
```

Read `lambda e: e["amount"]` as "a function that takes `e` and gives back `e["amount"]`". Everything after the
colon is what it returns; there is no `return` word. Use lambdas for tiny jobs like keys; anything longer deserves
a proper `def` with a name.

To sort by two things, give back a **tuple**: Python compares tuples item by item, so
`key=lambda e: (e["category"], e["amount"])` sorts by category, and by amount within each category. And a minus
sign flips a number's order: `key=lambda e: -e["amount"]` puts the biggest first.
:::

:::step{type=example title="Worked example: biggest first, ties by name"}
Here is a sort with two rules, on a list of shop items:

```python
items = [
    {"name": "toast", "price": 15},
    {"name": "cake", "price": 40},
    {"name": "bun", "price": 15},
]
sorted(items, key=lambda i: (-i["price"], i["name"]))
# cake (40), then bun and toast (both 15, so alphabetical)
```

1. The key gives each item a tuple: cake becomes `(-40, "cake")`, toast `(-15, "toast")`, bun `(-15, "bun")`.
2. Python compares the first parts: -40 is the smallest, so cake comes first (the minus made "biggest price"
   come first).
3. Toast and bun tie on -15, so Python looks at the second part: `"bun"` comes before `"toast"`.

Two rules in one key. Your second task uses exactly this idea with expenses.
:::

:::step{type=concept title="List comprehensions: a loop in one line"}
Here is a loop you can already write, and the same thing as a **list comprehension**:

```python
# the loop
big = []
for a in amounts:
    if a > 100:
        big.append(a)

# the comprehension
big = [a for a in amounts if a > 100]
```

Read the comprehension in this order: **for** each `a` in `amounts`, **if** `a > 100`, **keep** `a`. The part at
the front is what goes into the new list; it can be any expression: `[a * 2 for a in amounts]` doubles every
amount, `[e["name"] for e in expenses]` picks out every name. The `if` part is optional.

Press Play to watch Python work through one:

:::diagram{name="comprehension-steps"}
For each item: test the condition, work out the expression, collect the answer.
:::

Comprehensions always build a **new** list; the original is never touched.
:::

:::step{type=predict title="Guess first"}
:::question
What is `[a // 100 for a in [120, 45, 900] if a > 100]`?
:::
- [ ] `[120, 900]`
- [x] `[1, 9]`
- [ ] `[1, 0, 9]`
:::explain
The `if` keeps only 120 and 900 (45 is not over 100). Then the expression at the front, `a // 100`, turns them
into `1` and `9`.
:::
:::

:::step{type=task task=large_expenses title="Your turn: the big ones, in one line"}
Open `sorting.py` and make `large_expenses(expenses, limit)` give back the **names** of the expenses whose amount
is greater than `limit`, in their original order. Each expense looks like `{"name": "rent", "amount": 9000}`.

With the week's expenses in the file, `large_expenses(WEEK, 500)` gives `["rent", "phone"]`. Try to write it as one
list comprehension.

```bash run
cd /workspace/11-sorting-and-comprehensions && python3 -c "from sorting import large_expenses, WEEK; print(large_expenses(WEEK, 500))"
```

Then press **Check**.
:::

:::step{type=task task=by_amount title="Your turn: biggest first"}
In `sorting.py`, make `by_amount(expenses)` give back a **new** list of the expenses sorted by amount, biggest
first, and expenses with the same amount in alphabetical order of their name. The list it was given must not
change.

`[e["name"] for e in by_amount(WEEK)]` gives `["rent", "phone", "books", "lunch", "bus"]`: books and lunch both cost
120, so books comes first.

```bash run
cd /workspace/11-sorting-and-comprehensions && python3 -c "from sorting import by_amount, WEEK; print([e['name'] for e in by_amount(WEEK)])"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `sorted(["bb", "a", "ccc"], key=len, reverse=True)` give?
:::
- [x] `["ccc", "bb", "a"]`
- [ ] `["a", "bb", "ccc"]`
- [ ] `["ccc", "a", "bb"]`
:::explain
`key=len` compares lengths 2, 1 and 3; `reverse=True` puts the longest first.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is `[n * n for n in range(4)]`?
:::
- [ ] `[1, 4, 9, 16]`
- [x] `[0, 1, 4, 9]`
- [ ] `[0, 2, 4, 6]`
:::explain
`range(4)` gives 0, 1, 2 and 3, and each is squared: 0, 1, 4, 9.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `lambda e: e["amount"]` give back for `{"name": "juice", "amount": 15}`?
:::
- [x] `15`
- [ ] `"juice"`
- [ ] The whole dictionary
:::explain
A lambda returns whatever comes after its colon: here, the value under `"amount"`.
:::
:::

:::step{type=deep-dive title="Go deeper: other comprehensions, and when not to use them"}
Comprehensions come in other shapes too:

```python
{a for a in amounts}                       # a set comprehension
{e["name"]: e["amount"] for e in WEEK}     # a dict comprehension
sum(a for a in amounts if a > 100)         # a generator: no list is even built
```

The last one is worth knowing: without square brackets, Python produces the values one at a time and `sum` adds
them as they come, so no list is ever stored. For very large data, that saves memory.

**When not to.** A comprehension is lovely for one simple filter and one simple expression. Once you need several
conditions, nested loops, or a comment to explain it, go back to a plain `for` loop: code is read far more often
than it is written, and a clear loop beats a clever line.

**Stable sorting.** Python's sort is *stable*: items that compare equal keep their original order. That is why
you can sort by name first and then by amount, and the names stay alphabetical within each amount.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Sort by anything with `key=`, biggest first with `reverse=True` or a minus sign, and by two rules with a tuple.
- Write tiny functions inline with `lambda`.
- Turn a filter-and-collect loop into one line: `[expr for x in items if condition]`.
- Know when a plain loop is clearer than a clever comprehension.

:::photo{src="/lesson-images/python/py-11-notes.webp" alt="Handwritten notes about sorting and comprehensions: sorted with reverse and key, and two list comprehensions" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 12: functions in depth, with defaults, any number of arguments, and a famous trap.
:::
