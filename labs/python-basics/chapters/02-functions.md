:::step{type=story title="Why does every program have functions?"}
Count how many times a shop's billing app says "Hello, ..." to a customer, or works out a total. Thousands of
times a day. Do you think someone wrote those instructions out thousands of times?

The idea is older than electric computers. In 1843 **Ada Lovelace** wrote out, step by step, how Charles Babbage's
Analytical Engine could calculate a series of numbers called Bernoulli numbers: a recipe written down once, which the
machine could follow again for every number in the series. It is now called the first published computer program.

:::photo{src="/lesson-images/python/ada-lovelace.webp" alt="A watercolour portrait of Ada Lovelace in a purple and white dress with a dark lace shawl, holding a fan" credit="Alfred Edward Chalon" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Ada_Lovelace_portrait.jpg"}
Ada Lovelace, around 1840.
:::

No. They wrote them **once**, gave them a name, and then used that name over and over. That named, reusable
piece of a program is a **function**. Everything big in programming is made of small functions, the way a
long book is made of sentences.

Today Pocket gets its first three functions: one to greet you, and two little helpers for its sums.

:::mission
Write `greet`, which builds a greeting for any name, then `add` and `is_even`, two helpers Pocket will need.
:::
:::

:::step{type=concept title="A function: a name for some instructions" file="02-functions/greet.py" line="4-6"}
You have already used a function: `print`. You never saw how `print` works inside; you just wrote its name,
put something in the brackets, and it did its job. Now you will write your own.

Here is a small function that doubles a number:

```python
def double(x):
    return x * 2
```

Every part has a job:

- `def` means "I am **def**ining a function". It is a keyword: a word Python reserves for itself.
- `double` is the function's **name**. You choose it, and you use it later to run the function.
- `(x)` lists the **parameters**: the inputs the function expects. Here there is one, called `x`.
- The `:` at the end says "the body comes next".
- The **body** is every line below that is **indented** (pushed right by 4 spaces). Python knows which lines
  belong to the function only by that indentation.
- `return x * 2` works out `x * 2` and **hands the answer back**. It is the function's result.

Writing a `def` does not run anything. It only teaches Python a new word. The function runs when you **call**
it, by writing its name with brackets:

```python
double(4)     # gives back 8
double(10)    # gives back 20
```

The value you put in the brackets, like `4`, is called an **argument**. When the function runs, the parameter
`x` holds that argument.

:::picture{name="recipe-card"}
A function is like a recipe card: a name, the inputs, the steps, and what you get at the end.
:::
:::

:::step{type=example title="Worked example: follow one call"}
Let's watch a function that builds text, call by call:

```python
def welcome(city):
    return f"Welcome to {city}!"

message = welcome("Pune")
print(message)
```

Run it in your head first, then press Play to see what Python really does. The diagram uses `greet`, which is
exactly the same shape:

:::diagram{name="function-call"}
The call jumps into the function, the parameter gets the argument, and return carries the answer back.
:::

Line by line:

1. `def welcome(city):` teaches Python the function. Nothing is printed yet.
2. `welcome("Pune")` calls it. Inside, `city` now holds `"Pune"`.
3. `f"Welcome to {city}!"` is an **f-string**: a string with an `f` in front, where anything inside curly
   braces `{ }` is replaced by its value. So it becomes `"Welcome to Pune!"`.
4. `return` hands that text back. It lands in `message`.
5. `print(message)` shows `Welcome to Pune!`.

Your first task has exactly this shape, with different words.
:::

:::step{type=predict title="Guess first"}
:::question
Open `greet.py`. The body of `greet` is just `pass`, a word that means "do nothing". What does `greet("Asha")`
give back right now?
:::
- [ ] `"Hello, Asha!"`
- [ ] An empty string `""`
- [x] `None`
- [ ] An error
:::explain
A function that ends without a `return` gives back `None`, Python's special value for "nothing". `pass` only
fills the space so the function is not empty; it returns nothing, so you get `None`.
:::
:::

:::step{type=try title="Ask the function yourself" file="02-functions/greet.py" line="4-6"}
You can call a function straight from the terminal, without writing a new file:

```bash run
cd /workspace/02-functions && python3 -c "from greet import greet; print(greet('Asha'))"
```

It prints `None`, as you guessed. Here is how that long command works:

- `python3 -c "..."` runs the Python code inside the quotes, instead of a file.
- `from greet import greet` means "from the file `greet.py`, bring in the function `greet`".
- `print(greet('Asha'))` calls it and prints what comes back.

Keep this command handy: run it again after each change to see your function's answer.
:::

:::step{type=task task=greet title="Your turn: greet someone"}
Make `greet(name)` in `greet.py` give back `"Hello, <name>!"`.

1. Replace `pass` with a `return` line.
2. Build the text with an f-string, putting `name` inside curly braces.
3. Mind the comma after Hello and the exclamation mark: the check compares the text exactly.

So `greet("Asha")` gives `"Hello, Asha!"`, and `greet("Kabir")` gives `"Hello, Kabir!"`. Run the command from
the last step to see it, then press **Check**.

:::why
Returning the text (instead of printing it) lets other code use it: a web page, a message, or the checks that
test your work.
:::
:::

:::step{type=concept title="print shows, return gives back" file="02-functions/shout.py" line="2-13"}
Here is the most common beginner confusion in all of Python, and you are about to understand it better than
most people. Open `shout.py`:

```python
def shout_print(word):
    print(word.upper() + "!")


def shout_return(word):
    return word.upper() + "!"


a = shout_print("hello")
b = shout_return("hello")
print("a is", a)
print("b is", b)
```

Two functions that *look* like they do the same thing. (`word.upper()` makes the text capital letters, and `+`
joins two strings.) One **prints** the result. The other **returns** it. What ends up in `a` and `b`?

Run it and find out:

```bash run
cd /workspace/02-functions && python3 shout.py
```

```text
HELLO!
a is None
b is HELLO!
```

Surprised? Here is what happened:

- `shout_print("hello")` showed `HELLO!` on the screen right away. But it has no `return`, so it gave back
  `None`, and `a` is `None`.
- `shout_return("hello")` showed nothing. It handed `"HELLO!"` back, and that went into `b`.

`print` talks to **the person** at the screen. `return` talks to **the code** that called the function. The
screen cannot do sums or store answers; only returned values can be used again. That is why almost every
function you write will `return` its answer.
:::

:::step{type=example title="Worked example: numbers in, a number out"}
Functions can take more than one parameter. Separate them with commas:

```python
def area(width, height):
    return width * height

area(3, 4)     # gives back 12
```

The first argument goes to the first parameter, the second to the second: `width` is `3` and `height` is `4`.

Functions can also answer yes-or-no questions. Python has two special values for that, `True` and `False`, and
a comparison gives back one of them. `==` means "is equal to" (two equal signs: one `=` means "store",
you will meet it in chapter 3):

```python
def is_ten(n):
    return n == 10

is_ten(10)     # gives back True
is_ten(7)      # gives back False
```

And one new operator for your next task. `%` gives the **remainder** after dividing:

```python
7 % 2     # 1, because 7 = 2 * 3 + 1
8 % 2     # 0, because 8 divides by 2 exactly
9 % 3     # 0
```

A remainder of `0` means "divides exactly". Can you see how that helps with even numbers?
:::

:::step{type=task task=add title="Your turn: add two amounts"}
Open `math_utils.py` and make `add(a, b)` give back the two numbers added together.

For example, `add(2, 3)` gives `5`, and `add(-1, 1)` gives `0`. Check it in the terminal:

```bash run
cd /workspace/02-functions && python3 -c "from math_utils import add; print(add(2, 3))"
```

Then press **Check**.
:::

:::step{type=task task=is_even title="Your turn: is it even?"}
Still in `math_utils.py`, make `is_even(n)` give back `True` when `n` is even and `False` when it is not.

A number is even when dividing it by 2 leaves nothing over. You have two tools from the worked example: `%`
for the remainder, and `==` to compare.

`is_even(4)` gives `True`, `is_even(7)` gives `False`. And what about `0` and negative numbers like `-4`? Try
them in the terminal before you press **Check**: the check tries them too.
:::

:::step{type=try title="When the call does not match" file="02-functions/greet.py" line="4"}
What happens if you call a function but forget its argument? Try it:

```bash run
cd /workspace/02-functions && python3 -c "from greet import greet; print(greet())"
```

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
TypeError: greet() missing 1 required positional argument: 'name'
```

Read it from the bottom, as you learned in chapter 1. `TypeError` is the kind of mistake; the message names
the function, `greet()`, and says exactly what is missing: the argument for the parameter `name`. Python
does not guess. If a function asks for one input, you must give it one.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does this program print?

```python
def triple(n):
    return n * 3

print(triple(5))
```
:::
- [ ] `n * 3`
- [x] `15`
- [ ] Nothing: the function was only defined
- [ ] `None`
:::explain
`triple(5)` runs the body with `n` set to `5`, returns `15`, and `print` shows it.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A function has a `print(...)` line but no `return`. What does calling it give back?
:::
- [ ] What it printed
- [x] `None`
- [ ] An error
:::explain
Printing only shows something on the screen. A function without `return` gives back `None`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `10 % 3`?
:::
- [ ] `3`
- [x] `1`
- [ ] `3.33`
:::explain
`%` gives the remainder: 10 is 3 times 3, with 1 left over.
:::
:::

:::step{type=deep-dive title="Go deeper: hints, docstrings and why small functions win"}
**Type hints.** In other Python code you will see functions written like this:

```python
def welcome(city: str) -> str:
    return f"Welcome to {city}!"
```

`city: str` says "city should be a string", and `-> str` says "this gives back a string". These are **type
hints**: notes for people and for tools that check your code. Python itself ignores them when it runs. You
will use them more in Part 3.

**Docstrings.** A string right under the `def` line describes the function. Tools show it as help:

```python
def double(x):
    """Give back x times two."""
    return x * 2
```

**Why small functions?** A function that does one job is easy to name, easy to test and easy to reuse. When
you cannot find a short name for a function, it is usually doing too much: split it in two. Professional
developers follow this rule every day.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Define a function with `def`, a name, parameters and an indented body.
- Call it with arguments, and give an answer back with `return`.
- Tell `print` (shows it to a person) from `return` (gives it to the code), and know a function without
  `return` gives back `None`.
- Build text with f-strings, compare with `==`, and find a remainder with `%`.

:::photo{src="/lesson-images/python/py-02-notes.webp" alt="Handwritten notes: def, return gives the answer back, print only shows it, no return gives None" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 3: numbers and text in depth, with variables, maths that surprises, and money that looks right.
:::
