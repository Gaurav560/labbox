# Your first functions

A **function** is a named block of code that does one job. You define it with `def`,
give it a name, and list the inputs it takes in brackets:

```python
def square(x):
    return x * x
```

The `return` keyword sends a value back to whoever called the function.
`square(4)` gives back `16`. A function without `return` gives back `None`, which is
why the starter code does not pass yet: it only says `pass`.

## Try it in the terminal

The terminal at the bottom is a real Linux machine with your files in `/workspace`.
After editing `greet.py`, try:

```bash
python3 -c "from greet import greet; print(greet('Asha'))"
```

You can also start the Python REPL with `python3` and import your functions to play
with them. Type `exit()` to leave.

## Your tasks

1. **greet**: in `greet.py`, make `greet(name)` return `"Hello, <name>!"`.
   For example `greet("Asha")` returns `"Hello, Asha!"`.
2. **add**: in `math_utils.py`, make `add(a, b)` return the sum of `a` and `b`.
3. **is_even**: in `math_utils.py`, make `is_even(n)` return `True` when `n` is even
   and `False` otherwise. Hint: the `%` operator gives the remainder of a division.

Your files save automatically. When you are ready, press **Check** to run the hidden
tests on a clean machine.
