:::step{type=story title="Lunch orders at Dabba Express"}
:::character{name="Priya" role="Founder, Dabba Express"}
Every morning we deliver 300 tiffins across Pune. Right now I write every order
slip by hand and add up the bills on my phone. I need a few small helpers in Python.
Can you build them for me before the lunch rush?
:::

:::mission
Write three small Python functions: one greets a customer, one adds up a bill,
and one decides which van an order goes in.
:::
:::

:::step{type=concept title="What a function is"}
## Your first functions

A **function** is a named block of code that does one job. You define it with `def`,
give it a name, and list its inputs in brackets:

```python
def square(x):
    return x * x
```

The `return` keyword sends a value back to whoever called the function.
`square(4)` gives back `16`.

:::tip
Python knows which lines belong to the function from the **indentation**. Use 4 spaces.
:::
:::

:::step{type=predict title="Guess first"}
:::question
Open `greet.py`. The function body is just `pass`. What does `greet("Asha")` give back right now?
:::
- [ ] `"Hello, Asha!"`
- [ ] An empty string `""`
- [x] `None`
- [ ] An error
:::explain
A function without a `return` statement gives back `None`, Python's way of saying
"nothing". That is why the starter code does not pass yet: it only says `pass`.
:::
:::

:::step{type=try title="See it for yourself"}
The terminal at the bottom is a real Linux machine with your files in `/workspace`.
Ask Python to call `greet` and print what comes back:

```bash run
python3 -c "from greet import greet; print(greet('Asha'))"
```

You should see `None`. Keep this command handy: run it again after each change.
:::

:::step{type=task task=greet title="Greet a customer"}
Make `greet(name)` in `greet.py` return `"Hello, <name>!"`.

For example, `greet("Asha")` returns `"Hello, Asha!"`. Mind the comma and the
exclamation mark: the order slips are printed exactly as you return them.

:::why
Returning the text (instead of printing it) lets other code reuse it: the slip
printer, the SMS sender, and the tests that check your work.
:::
:::

:::step{type=example title="Two tools for the next tasks"}
Python does arithmetic with the usual operators. One less familiar one is `%`,
which gives the **remainder** after a division:

```python
17 + 5    # 22
17 % 5    # 2, because 17 = 3 * 5 + 2
10 % 2    # 0
```

A comparison like `x == 0` is itself a value: it is either `True` or `False`.

:::mistake
`=` stores a value in a variable. `==` compares two values. Mixing them up is the
most common bug on day one.
:::
:::

:::step{type=task task=add title="Add up a bill"}
In `math_utils.py`, make `add(a, b)` return the sum of `a` and `b`.

`add(2, 3)` returns `5`, and `add(-1, 1)` returns `0`.
:::

:::step{type=task task=is_even title="Pick the right van"}
Orders with an even number go in the blue van, odd ones in the red van.

In `math_utils.py`, make `is_even(n)` return `True` when `n` is even and `False`
otherwise. Zero and negative numbers count too: `is_even(0)` and `is_even(-4)` are `True`.
:::

:::step{type=recap title="Chapter done"}
- `def` defines a function; `return` sends a value back to the caller.
- A function with no `return` gives back `None`.
- `%` gives the remainder, so `n % 2 == 0` tells you if `n` is even.
:::
