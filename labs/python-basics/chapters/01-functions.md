:::step{type=story title="Why start with functions"}
Every program you will write, from a marks calculator to a web server, is built from small pieces
that each do one job. In Python those pieces are **functions**. Learn them first and everything
after this builds on them.

:::mission
Write three small functions: one greets a person, one adds two numbers, and one tells whether a
number is even. Real tests check each one.
:::
:::

:::step{type=history title="The story of Python"}
Python is one of the most used programming languages in the world. It started as one person's
holiday project.

:::before{title="Before Python"}
In the late 1980s, programmers mostly chose between **C**, which is fast but needs long, careful code
where one memory mistake crashes the program, and **shell scripts**, which are quick to write but turn
messy beyond a few lines. Guido van Rossum, a programmer at the CWI research institute in Amsterdam,
kept hitting jobs that were too awkward for a shell script and too slow to write in C.
:::

:::solved
A language that is as **quick to write** as a script, **powerful enough** for real programs, and above
all **easy to read**. Python code is read far more often than it is written, so it looks almost like
plain English, and its indentation is part of the language.
:::

:::timeline
- **1989** Guido starts Python as a hobby project over the Christmas holidays.
- **1991** The first public release, version 0.9.0.
- **2000** Python 2.0 adds list comprehensions and a new garbage collector.
- **2008** Python 3.0 cleans up old design mistakes, even though old code needs changes to run.
- **2020** Python 2 reaches end of life; Python 3 is the only Python.
:::

Today Python is maintained by the **Python Software Foundation**, a non-profit, and a worldwide team of
volunteer core developers led by an elected **steering council**. Guido led the language for almost
30 years as its "Benevolent Dictator For Life" and stepped down from that role in 2018.

:::usedby{title="Industries"}
- AI and machine learning
- Data science
- Web backends
- Automation and DevOps
- Science and research
- Teaching
:::

:::usedby{title="Used at"}
- Instagram
- YouTube
- Spotify
- Netflix
- Dropbox
- NASA
:::

:::funfact
Python is named after the British comedy show *Monty Python's Flying Circus*, not the snake. Type
`import this` in Python to read "The Zen of Python", the short poem of design rules the language
follows.
:::

```bash run
python3 -c "import this" | head -9
```
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

:::picture{name="recipe-card"}
A function is a recipe card: name, inputs, steps, result.
:::
:::

:::step{type=example title="Worked example: a function that builds text"}
Here is a complete function, line by line:

```python
def welcome(city):
    return f"Welcome to {city}!"

welcome("Pune")
# 'Welcome to Pune!'
```

1. `def welcome(city):` names the function and its input, `city`.
2. The indented line is the body. `f"..."` is an **f-string**: `{city}` is replaced by the value.
3. `return` hands the finished text back to whoever called the function.

Your first task has exactly this shape, with different words.
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

:::step{type=task task=greet title="Greet someone"}
Make `greet(name)` in `greet.py` return `"Hello, <name>!"`.

For example, `greet("Asha")` returns `"Hello, Asha!"`. Mind the comma and the
exclamation mark: the tests compare the text exactly.

:::why
Returning the text (instead of printing it) lets other code reuse it: a web page, a
message, or the tests that check your work.
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

:::trace{title="17 % 5, step by step"}
| step | value | note |
|---|---|---|
| 17 // 5 | 3 | 5 fits into 17 three whole times. |
| 3 * 5 | 15 | Those three fives make 15. |
| 17 - 15 | 2 | What is left over is the remainder. |
| 17 % 5 | 2 | % gives exactly that leftover in one step. |
| 10 % 2 | 0 | Nothing left over: 10 is even, the test you will need for is_even. |
:::
:::

:::step{type=task task=add title="Add two numbers"}
In `math_utils.py`, make `add(a, b)` return the sum of `a` and `b`.

`add(2, 3)` returns `5`, and `add(-1, 1)` returns `0`.
:::

:::step{type=task task=is_even title="Even or odd"}
In `math_utils.py`, make `is_even(n)` return `True` when `n` is even and `False`
otherwise. Zero and negative numbers count too: `is_even(0)` and `is_even(-4)` are `True`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `double(5)` give, after `def double(n): return n * 2`?
:::
- [ ] `5`
- [x] `10`
- [ ] `None`
- [ ] `25`
:::explain
`n` is 5 inside the function, and `return n * 2` gives back `10`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A function has no `return` line. What does calling it give back?
:::
- [ ] `0`
- [ ] An empty string
- [x] `None`
- [ ] An error
:::explain
Without `return`, a function gives back `None`, Python's way of saying "nothing". You saw it in this chapter's try step.
:::
:::

:::step{type=recap title="Chapter done"}
- `def` defines a function; `return` sends a value back to the caller.
- A function with no `return` gives back `None`.
- `%` gives the remainder, so `n % 2 == 0` tells you if `n` is even.
:::
