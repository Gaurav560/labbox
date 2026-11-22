:::step{type=story title="How can print take one thing, or five, or none?"}
`print("hi")` takes one value. `print("a", 1, True, 2.5)` takes four. `print()` takes none, and prints an empty
line. And `print("a", "b", sep="-")` takes a setting by **name**. Your functions from chapter 2 could only do one
of those things: a fixed number of inputs, in a fixed order.

Today you learn the tricks `print` uses: **defaults**, **named arguments**, and **any number of arguments**. You
also meet one of the most famous traps in Python, one that has fooled experienced developers in real products,
and you will fix it yourself.

:::mission
Fix `add_item`, a function with a famous hidden bug, and write `total`, which adds any number of prices and takes
an optional discount by name.
:::
:::

:::step{type=concept title="Defaults and named arguments"}
A parameter can have a **default value**, used when the caller leaves it out:

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Asha")                       # 'Hello, Asha!'
greet("Asha", "Namaste")            # 'Namaste, Asha!'
greet(greeting="Hi", name="Ravi")   # 'Hi, Ravi!'
```

The last call uses **named arguments** (also called keyword arguments): you say which parameter gets which value,
so the order no longer matters. Named arguments make calls easier to read, especially for settings:
`total(100, 50, discount=10)` says what 10 means; `total(100, 50, 10)` does not.

Two rules: parameters with defaults come **after** those without, and in a call, named arguments come **after**
the plain ones.
:::

:::step{type=example title="Worked example: any number of arguments"}
Put a `*` before a parameter, and it collects **all** the plain arguments into one tuple:

```python
def average_of(*numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

average_of(10, 20)          # 15.0
average_of(1, 2, 3, 4)      # 2.5
average_of()                # 0
```

1. `*numbers` collects whatever was passed: `(10, 20)`, then `(1, 2, 3, 4)`, then `()`.
2. Inside, `numbers` is an ordinary tuple, so `sum`, `len` and loops all work.

Now the clever part. Any parameter written **after** the `*` parameter can only be given **by name**, because all
the plain arguments were already swallowed by the star:

```python
def show(*args, sep=" "):
    ...
```

That is exactly how `print(..., sep="-")` works. It also protects callers from mistakes: in the next task,
`total(100, 50, 10)` adds 10 as a third price, and only `discount=10` means a discount.
:::

:::step{type=task task=total title="Your turn: any number of prices"}
Open `functions.py` and write `total(*prices, discount=0)`: the sum of all the prices, minus `discount` percent,
rounded to 2 decimals, always a float.

- `total(100, 50)` gives `150.0`.
- `total(100, 50, discount=10)` gives `135.0` (10% off 150).
- `total(100, 50, 10)` gives `160.0`: 10 is a third price here, because the discount can only be given by name.
- `total()` gives `0.0`.

```bash run
cd /workspace/12-functions-in-depth && python3 -c "from functions import total; print(total(100, 50, discount=10))"
```

Then press **Check**.
:::

:::step{type=concept title="Where do names live?" file="12-functions-in-depth/scope.py" line="2-12"}
Open `scope.py`. There is a `total` outside the function, and another `total` inside it:

```python
total = 100


def add_tip(amount):
    total = amount + 10
    print("inside:", total)
    return total


add_tip(50)
print("outside:", total)
```

Before you run it: does `add_tip(50)` change the outside `total` to 60?

```bash run
cd /workspace/12-functions-in-depth && python3 scope.py
```

```text
inside: 60
outside: 100
```

No. A variable created inside a function is **local**: it lives only while the function runs, and it is a
different variable from any outside one with the same name. The function's `total` is born when `add_tip` starts
and disappears when it returns. That separation is a gift: you can name things inside a function freely without
breaking the rest of your program.

The clean way for a function to affect the outside world is the one you already know: **return** a value, and
let the caller store it.
:::

:::step{type=concept title="The famous trap: a default list" file="12-functions-in-depth/functions.py" line="4-7"}
Now the trap. Open `functions.py` and look at `add_item`:

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket
```

It looks harmless: "add the item to the basket, or to a new empty basket if none was given". Call it twice:

```python
add_item("milk")     # ['milk']
add_item("bread")    # ['milk', 'bread']   ... wait, what?
```

The second customer got the first customer's milk! Here is why. A default value is created **once**, when Python
reads the `def` line, not each time the function is called. So every call without a basket shares the **same**
list, and it keeps growing. It is chapter 8's "two names, one list", hidden inside a function.

:::diagram{name="default-list"}
The default list is made once, when def runs, and every call without a basket shares it.
:::

The standard fix is a pattern every Python developer knows: use `None` as the default, and make a fresh list
**inside** the function when nothing was given:

```python
def log(message, history=None):
    if history is None:
        history = []
    history.append(message)
    return history
```

`is None` is the right way to ask "was nothing given?". A new list is now made on every call that needs one.
:::

:::step{type=predict title="Guess first"}
:::question
With the buggy `add_item`, what does a **third** call, `add_item("eggs")`, give back?
:::
- [ ] `['eggs']`
- [x] `['milk', 'bread', 'eggs']`
- [ ] An error
:::explain
All three calls share the one default list made when `def` ran, so it keeps everything ever added to it.
:::
:::

:::step{type=task task=add_item title="Your turn: fix the basket that never empties"}
Fix `add_item` in `functions.py`, so every call without a basket starts with its own, new, empty basket.

- `add_item("milk")` gives `["milk"]`, and then `add_item("bread")` gives `["bread"]`.
- With a basket given, it still adds to that basket: `add_item("juice", ["milk"])` gives `["milk", "juice"]`.

Use the pattern from the trap step.

```bash run
cd /workspace/12-functions-in-depth && python3 -c "from functions import add_item; print(add_item('milk')); print(add_item('bread'))"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
With `def greet(name, greeting="Hello")`, what does `greet("Asha", greeting="Hi")` give?
:::
- [ ] `'Hello, Asha!'`
- [x] `'Hi, Asha!'`
- [ ] An error
:::explain
A named argument replaces the default for that call.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Inside `def f(*nums)`, what is `nums` when you call `f(4, 5)`?
:::
- [ ] `[4, 5]`
- [x] `(4, 5)`
- [ ] `4`
:::explain
A starred parameter collects the arguments into a tuple.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`x = 5`, then a function does `x = 99` inside it and is called. What is `x` outside afterwards?
:::
- [x] `5`
- [ ] `99`
:::explain
The `x` inside the function is a separate, local variable. The outside `x` is untouched.
:::
:::

:::step{type=deep-dive title="Go deeper: **kwargs, global, and functions as values"}
**Named arguments of any kind.** Two stars collect any **named** arguments into a dictionary:

```python
def show(*args, **kwargs):
    print(args, kwargs)

show(1, 2, city="Pune")     # (1, 2) {'city': 'Pune'}
```

You will see `*args, **kwargs` in libraries that pass arguments along to other functions.

**global.** A function *can* change an outside variable if it declares `global total` first. Professional code
almost never does: functions that quietly change things outside themselves are hard to understand and test.
Return a value instead.

**Functions are values.** A function is an object like any other: you can store it in a variable, put it in a
list, or pass it to another function. You already did this in chapter 11: `key=len` passed the function `len`
itself, without calling it.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Give parameters defaults, and call functions with named arguments.
- Accept any number of arguments with `*args`, and make settings name-only by putting them after it.
- Explain local variables: names inside a function live and die with the call.
- Avoid the mutable default trap with `None` and a fresh list inside the function.

:::photo{src="/lesson-images/python/py-12-notes.webp" alt="Handwritten notes about functions in depth: star arguments, never a list as a default, and local names" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 2. Pocket can hold, find, count, sort and reshape data. Next, Part 3: real programs,
starting with errors you can catch and handle.
:::
