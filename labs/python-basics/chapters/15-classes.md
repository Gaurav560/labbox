:::step{type=story title="What if Python had a type called Expense?"}
Python comes with types: `str` for text, `int` for whole numbers, `list`, `dict`. Each one is a kind of value that
knows how to do things: a string knows how to `.upper()`, a list knows how to `.append()`.

But Python has never heard of an expense. Until now, Pocket has described one with a dictionary,
`{"name": "lunch", "amount": 120}`, and kept the functions that work on it somewhere else. Wouldn't it be nicer to
make a **new type**, `Expense`, that holds its own data *and* knows how to describe itself? That is exactly what a
**class** does, and almost every large program in the world is built from classes.

:::mission
Design two classes: `Expense`, one thing you spent money on, and `Pocket`, which holds your expenses and knows
their total and the biggest one.
:::
:::

:::step{type=concept title="A class is a blueprint; objects are what you build" file="15-classes/shop.py" line="2-8"}
Open `shop.py`. Its first part defines a class:

```python
class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def with_tax(self, percent):
        return round(self.price * (100 + percent) / 100, 2)
```

A **class** is a blueprint: it describes what every item has and can do. An **object** (also called an
**instance**) is one real item built from it: `Item("pen", 15)` builds one, `Item("cake", 40)` builds another.

- `__init__` (two underscores on each side, said "dunder init") is the special method Python runs **when an object
  is created**. Its job is to set the object up.
- `self` is the object being set up. `self.name = name` stores the name **on that object**. Values stored on an
  object are called **attributes**.
- `with_tax` is a **method**: a function that belongs to the class. It also receives `self`, so it can read that
  object's own `price`.

:::picture{name="blueprint-houses"}
A class is a blueprint and objects are the houses built from it: same plan, each with its own furniture.
:::
:::

:::step{type=try title="One class, two objects" file="15-classes/shop.py" line="11-17"}
Run it:

```bash run
cd /workspace/15-classes && python3 shop.py
```

```text
pen 15
cake 42.0
45 15
<class '__main__.Item'>
```

Line by line: `pen.name` and `pen.price` read the pen's own attributes. `cake.with_tax(5)` calls the method on the
cake: `40 * (100 + 5) / 100` is 42.0, 40 plus 5%. Then `cake.price = 45` changed the cake, and the pen still costs 15: **each object keeps
its own values**. The last line shows you have truly made a new type: Python calls it `Item`. (`__main__` is the name Python
gives the file you ran directly, so `__main__.Item` means "the Item class from the file being run".)
:::

:::step{type=concept title="What happens when you create an object"}
Creating an object looks like calling a function, and a lot happens in that moment. Press Play:

:::diagram{name="object-creation"}
Python makes a new empty object, runs __init__ on it, and gives you the finished object.
:::

That also explains `self` in methods. When you write `cake.with_tax(5)`, Python turns it into
`Item.with_tax(cake, 5)` (we tried both; each gives 42.0): the object before the dot becomes `self`. So inside every method, `self` means "the
object this method was called on". You never pass `self` yourself; Python does it.
:::

:::step{type=example title="Worked example: a wallet that remembers"}
Objects shine when data and the actions on it belong together. Here is a small wallet:

```python
class Wallet:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        self.balance = self.balance + amount

    def can_afford(self, price):
        return price <= self.balance

w = Wallet()
w.deposit(500)
w.balance            # 500
w.can_afford(120)    # True
w.can_afford(900)    # False
```

1. `__init__` gives a parameter a default (chapter 12), so `Wallet()` starts at 0.
2. `deposit` **changes** the object: the wallet remembers its balance between calls.
3. `can_afford` **answers a question** about the object, using its own data.

Your first task is the same shape: an `__init__` that stores values, and one method that uses them.
:::

:::step{type=predict title="Guess first"}
:::question
`a = Wallet(100)` and `b = Wallet(100)`. Then `a.deposit(50)`. What is `b.balance`?
:::
- [ ] `150`
- [x] `100`
- [ ] `50`
:::explain
`a` and `b` are two separate objects, each with its own `balance`. Changing one never changes the other.
:::
:::

:::step{type=task task=expense_class title="Your turn: an Expense"}
Open `pocket.py` and write the class `Expense`:

- `Expense(name, amount, category="other")` keeps all three as attributes: `e.name`, `e.amount`, `e.category`.
- `label()` gives back the expense as text: `Expense("lunch", 120, "food").label()` gives
  `"lunch: ₹120.00 (food)"`, and `Expense("rent", 18000).label()` gives `"rent: ₹18,000.00 (other)"`.

The amount uses the format you learned in chapter 3.

```bash run
cd /workspace/15-classes && python3 -c "from pocket import Expense; print(Expense('lunch', 120, 'food').label())"
```

Then press **Check**. Delete the `pass` line when you write the class body; it was only holding the place.

The usual slips, with Python's real messages (we tried each):

- `_init_` with one underscore on each side: Python does not know that name, so it never runs, and
  `Expense("lunch", 120)` fails with `TypeError: Expense() takes no arguments`.
- A method without `self`, like `def label():`, fails when called: `TypeError: Expense.label() takes 0
  positional arguments but 1 was given`. The "1" is the object Python passed in as `self`.
- `name = name` instead of `self.name = name` in `__init__`: it stores nothing on the object, and `e.name`
  later fails with `AttributeError: 'Expense' object has no attribute 'name'`.
:::

:::step{type=concept title="Objects that hold objects, and one trap to avoid"}
A `Pocket` holds many expenses, so each pocket needs its own **list**. Make it in `__init__`, so every new pocket
gets a new, empty one:

```python
class Pocket:
    def __init__(self):
        self.expenses = []
```

Then methods work on that list: `add` appends to `self.expenses`, `total` adds up the amounts, `biggest` finds
the largest. Inside them you use everything from Part 2: loops, `sum`, `max` with a `key` (chapter 11).

Now the trap, chapter 12's shared list in a new disguise. Writing the list **in the class body**, outside
`__init__`, looks almost the same:

```python
class Bag:
    items = []          # made ONCE, shared by every bag
    def add(self, x):
        self.items.append(x)
```

Make two bags, add a pen to the first, and look in the second: `['pen']`. A list in the class body belongs to the
class itself, so all its objects share it. Anything that should be separate for each object goes in `__init__`,
on `self`.
:::

:::step{type=task task=pocket_class title="Your turn: a Pocket full of expenses"}
In `pocket.py`, write the class `Pocket`:

- `Pocket()` starts with no expenses, and every pocket has its own.
- `add(expense)` adds an `Expense`.
- `total()` gives back the sum of the amounts (0 for an empty pocket).
- `biggest()` gives back the `Expense` with the largest amount, or `None` when the pocket is empty.

With lunch (120) and a bus ride (30) added, `total()` gives `150` and `biggest().name` gives `"lunch"`.

```bash run
cd /workspace/15-classes && python3 -c "from pocket import Expense, Pocket; p = Pocket(); p.add(Expense('lunch', 120, 'food')); p.add(Expense('bus', 30)); print(p.total(), p.biggest().name)"
```

Then press **Check**.

The usual slips: `max(self.expenses)` without a key fails, because Python does not know how to compare two
expenses: `TypeError: '>' not supported between instances of 'Expense' and 'Expense'` (give `max` a key, chapter
11); calling `max` on an empty pocket raises `ValueError` (check first, return `None`); and the list in the class
body, from the trap step.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
When does `__init__` run?
:::
- [ ] When Python reads the `class` line
- [x] Every time a new object is created
- [ ] Every time a method is called
:::explain
`__init__` sets up each new object, so it runs once per object, at the moment it is made.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In `cake.with_tax(5)`, what is `self` inside `with_tax`?
:::
- [x] The `cake` object
- [ ] The class `Item`
- [ ] `5`
:::explain
The object before the dot is passed in as `self`, and `5` arrives as `percent`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Where should a list that each object needs for itself be created?
:::
- [ ] In the class body, under the `class` line
- [x] In `__init__`, as `self.something = []`
:::explain
The class body runs once, so a list there is shared by all objects. `__init__` runs for each object.
:::
:::

:::step{type=deep-dive title="Go deeper: printing objects, dataclasses and inheritance"}
**Printing an object.** `print(pen)` shows something like `<__main__.Item object at 0x7f...>` (the number changes
every run: it is where the object lives in memory). Teach your class to describe itself with a special method:

```python
def __repr__(self):
    return f"Item({self.name!r}, {self.price})"
```

Now `print(pen)` shows `Item('pen', 15)`. Methods with double underscores are how your classes plug into Python's
own features: `__len__` makes `len(...)` work, `__eq__` makes `==` work.

**dataclasses.** For classes that mostly hold data, Python can write `__init__` and `__repr__` for you:

```python
from dataclasses import dataclass

@dataclass
class Expense:
    name: str
    amount: float
    category: str = "other"
```

**Inheritance.** One class can build on another: `class Refund(Expense):` starts with everything an `Expense`
has, and adds or changes what is different. The Java course on LabBox teaches it in its chapter 10 (Java uses
the word `extends`). Python programs tend to use it more sparingly.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Define a class with `__init__`, attributes on `self`, and methods.
- Create objects from it, each keeping its own values.
- Explain `self`: the object a method was called on.
- Give each object its own list in `__init__`, never in the class body.

:::photo{src="/lesson-images/python/py-15-sketch.webp" alt="Sketchnote: Classes and objects. A class is a blueprint; each object built from it keeps its own values, called attributes. Flow: Expense of lunch and 120, a new empty object, dunder init runs, self.name = name, the finished object. Remember: self is the object the method was called on; your methods take self first and Python passes it in; each object keeps its own values; make each object's own list in dunder init." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 16: modules and packages, so Pocket's code can live in several files, and use code other people
wrote.
:::
