:::step{type=story title="Why go deeper into functions"}
You have written many small functions. Real programs need a bit more from them: optional
settings, any number of inputs, and arguments that are hard to get wrong. Python also has one
famous trap here that catches beginners and experienced developers alike.

:::mission
In `functions.py`, fix a shopping basket function that mixes up different people's baskets, then
write a `total` that accepts any number of prices and an optional discount.
:::
:::

:::step{type=concept title="Default values and keyword arguments"}
A parameter can have a **default**, used when the caller leaves it out. Callers can also name the
arguments they pass:

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Riya")                        # 'Hello, Riya!'
greet("Riya", "Welcome")             # 'Welcome, Riya!'
greet(greeting="Hi", name="Riya")    # 'Hi, Riya!'  any order, by name
```

Parameters with defaults come after the ones without.
:::

:::step{type=example title="Worked example: a safe default"}
When a parameter needs a fresh list (or dictionary) on every call, use `None` as the default and
make the list inside:

```python
def add_tag(tag, tags=None):
    if tags is None:      # 1. no list given?
        tags = []         # 2. a new one, every call
    tags.append(tag)      # 3. add to it
    return tags

add_tag("python")         # ['python']
add_tag("go")             # ['go']   (not ['python', 'go'])
```

`None` never changes, so it is a safe default. Keep this pattern in mind when you look at
`add_item`.

:::trace{title="two calls without a list"}
| call | tags is None? | tags after | note |
|---|---|---|---|
| add_tag("python") | yes | ['python'] | No list given, so a new empty list is made, then "python" added. |
| add_tag("go") | yes | ['go'] | Again a brand new list: the first call's list is not reused. |
| add_tag("sql", ["py"]) | no | ['py', 'sql'] | A list was passed in, so it is used as it is. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
`add_item` in `functions.py` looks harmless. What does the second line print?

```python
print(add_item("milk"))     # ['milk']
print(add_item("bread"))    # ?
```
:::
- [ ] `['bread']`
- [x] `['milk', 'bread']`
- [ ] `['bread', 'milk']`
- [ ] An error
:::explain
The default `basket=[]` is created **once**, when Python first reads the `def` line, not on every
call. Every call that leaves out `basket` gets that same list, so items pile up across calls: one
customer's milk ends up in the next customer's basket.
:::
:::

:::step{type=try title="Watch the trap happen"}
```bash run
python3 -c "
from functions import add_item
print(add_item('milk'))
print(add_item('bread'))
print(add_item('eggs'))
"
```

Each call should start with an empty basket, but the list keeps growing.

:::diagram{name="default-list"}
Every call without a basket gets the same one list, made once when Python read the `def` line.
:::
:::

:::step{type=task task=add_item title="Fix the basket"}
Fix `add_item(item, basket)` in `functions.py` so that:

- without a basket, every call starts a **new** empty basket: `add_item("milk")` returns
  `["milk"]` and then `add_item("bread")` returns `["bread"]`
- with a basket, it adds to that basket and returns it: `add_item("tea", ["milk"])` returns
  `["milk", "tea"]`

:::why
This bug passes a quick test (the first call works) and then shows up later, far from its cause.
Linters flag `def f(x=[])` for exactly this reason.
:::
:::

:::step{type=concept title="Any number of arguments"}
A parameter with a `*` collects any number of positional arguments into a tuple. Parameters written
after it can only be given **by name**:

```python
def average(*marks, round_to=1):
    return round(sum(marks) / len(marks), round_to)

average(70, 80, 90)            # 80.0
average(70, 85, round_to=0)    # 78.0
```

Keyword-only parameters make calls readable and safe: `average(70, 85, 0)` would treat `0` as a
mark, never as the rounding.
:::

:::step{type=task task=total title="A total with a discount"}
In `functions.py`, write `total(*prices, discount=0)`: the sum of all the prices, minus `discount`
**percent**, rounded to 2 decimals and always a float.

- `total(100, 50)` returns `150.0`
- `total(100, 50, discount=10)` returns `135.0`
- `total()` returns `0.0`
- `total(99.99, 0.01)` returns `100.0`
- `total(100, 10)` returns `110.0` (10 is a price here, not a discount)
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
In `def f(x, *args, sep=" ")`, how must `sep` be passed?
:::
- [ ] By position, third
- [x] Only by name, like `sep="-"`
- [ ] It cannot be changed
- [ ] Before `x`
:::explain
Everything after `*args` is keyword-only: it can only be given by name, which keeps calls clear.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `total(10, 20)` see in `prices`, for `def total(*prices)`?
:::
- [ ] `[10, 20]`
- [x] `(10, 20)`
- [ ] `10`
- [ ] `{10, 20}`
:::explain
`*prices` collects the positional arguments into a **tuple**: `(10, 20)`.
:::
:::

:::step{type=deep-dive title="Scope, and functions as values"}
Variables made inside a function are **local**: they disappear when it returns and never clash with
names outside. A function can read an outer variable, but assigning to that name inside makes a new
local one (unless you declare it `global`, which is rarely a good idea).

Functions are values too: you can pass them around. `sorted(words, key=len)` passes the function
`len` so Python sorts by length, and `max(people, key=lambda p: p["age"])` passes a tiny unnamed
function. Many powerful Python tools are built on this idea.

Python also has `**kwargs`, which collects extra **named** arguments into a dictionary:
`def tag(text, **attrs)` called as `tag("Hi", color="red")` gets `attrs == {"color": "red"}`.
:::

:::step{type=recap}
- Defaults make parameters optional; arguments can be passed by name in any order.
- A mutable default (`[]`, `{}`) is shared by every call: use `None` and make a new one inside.
- `*args` collects any number of positional arguments into a tuple.
- Parameters after `*args` are keyword-only, which makes calls clearer and safer.
:::
