:::step{type=story title="How do you know your code still works tomorrow?"}
Every time you pressed **Check** in this course, a program you could not see ran your functions with dozens of
inputs and compared the answers. That program is a set of **tests**. Professional developers write them for
their own code, every day, for one reason: code changes. Someone fixes a bug in one place and quietly breaks
another. Clicking through everything by hand after each change is slow, boring and easy to get wrong. Tests run in
a second, every time.

Today you switch sides. You write the tests, and LabBox checks whether **your** tests are good enough to catch real
bugs.


**Margaret Hamilton** led the MIT team that wrote the software flying the Apollo missions. Testing and error checking
were central to her team's work, and during the Apollo 11 landing in 1969, that software handled a flood of alarms
without falling over. Next to her: the program, printed out.

:::photo{src="/lesson-images/python/margaret-hamilton.webp" alt="Margaret Hamilton in 1969, smiling and standing next to a stack of printed program listings as tall as she is" credit="Adam Cuerden (restoration)" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Margaret_Hamilton_-_restoration.jpg"}
Margaret Hamilton with the Apollo guidance software, 1969.
:::
:::mission
Write tests for Pocket's `format_price` and `over_budget`, good enough to catch the bugs LabBox plants in them.
:::
:::

:::step{type=concept title="A test is a function that checks one thing"}
Python has a keyword made for checking: `assert`. It does nothing when its condition is true, and stops with an
`AssertionError` when it is false:

```python
assert 2 + 2 == 4     # fine, nothing happens
assert 2 + 2 == 5     # AssertionError
```

A **test** is a small function that calls your code and asserts what the answer must be:

```python
from money import to_paise


def test_whole_rupees():
    assert to_paise(120) == 12000
```

The tool that runs tests is **pytest** (already installed in your lab). It follows simple rules:

- it looks for files whose names start with `test_`,
- inside them, it runs every function whose name starts with `test_`,
- a test **passes** if it finishes, and **fails** if an assert (or anything else) goes wrong.

Name each test after what it proves, like `test_whole_rupees`: when one fails, the name tells you what broke.
:::

:::step{type=try title="Run your first tests" file="17-testing/test_example.py" line="2-10"}
Open `test_example.py`: two finished tests for `to_paise`. Run them:

```bash run
cd /workspace/17-testing && python3 -m pytest -v test_example.py
```

```text
collecting ... collected 2 items

test_example.py::test_whole_rupees PASSED                                [ 50%]
test_example.py::test_rupees_and_paise PASSED                            [100%]

============================== 2 passed in 0.01s ===============================
```

(Your time may differ.) Now break a test on purpose: change `4550` to `455` in the second test, and run it again:

```text
test_example.py .F                                                       [100%]

=================================== FAILURES ===================================
____________________________ test_rupees_and_paise _____________________________

    def test_rupees_and_paise():
>       assert to_paise(45.5) == 455
E       assert 4550 == 455
E        +  where 4550 = to_paise(45.5)

test_example.py:10: AssertionError
```

Look how much pytest tells you: the failing test, the exact line (marked `>`), and both sides of the comparison,
`4550 == 455`, including where `4550` came from. Put `4550` back when you are done.
:::

:::step{type=example title="Worked example: tests that would catch a mistake"}
Here are tests for chapter 16's `km_to_miles(km)`, which rounds to two decimals:

```python
from units import km_to_miles


def test_a_marathon():
    assert km_to_miles(42.195) == 26.22


def test_zero_is_zero():
    assert km_to_miles(0) == 0


def test_rounds_to_two_decimals():
    assert km_to_miles(1) == 0.62
```

Each test has a job:

1. A **normal** case, with an answer you worked out by hand (not by running the code!).
2. An **edge** case: zero, empty, the smallest possible input.
3. A **rule** the function promises: here, rounding. If someone removed the `round`, `km_to_miles(1)` would give
   `0.621371` and this test would fail.

That last idea is the heart of testing: for each promise your function makes, ask "what test would fail if this
promise were broken?"
:::

:::step{type=predict title="Guess first"}
:::question
A teammate writes only one test for `format_price`: `assert format_price(5) == "₹5.00"`. Someone then breaks the
thousands separator. Does the test catch it?
:::
- [ ] Yes, it tests format_price
- [x] No: 5 has no thousands, so the broken code still gives "₹5.00"
:::explain
A test only checks what it tests. With no amount of 1,000 or more, a missing comma goes unnoticed. Good tests cover
every promise: here, a big amount too.
:::
:::

:::step{type=task task=first_tests title="Your turn: test format_price"}
Open `test_money.py` and write **at least two** test functions for `format_price` (from `money.py`, which works).

Your tests must **pass** on the correct `money.py`. Then LabBox runs them against two broken versions of
`format_price`, and your tests must **fail** on both:

- one that forgets the thousands separator,
- one that rounds to one decimal instead of two.

So think: which amounts would show those two mistakes? Run your tests:

```bash run
cd /workspace/17-testing && python3 -m pytest -v test_money.py
```

When they pass, press **Check**: it tells you if a planted bug slipped through.
:::

:::step{type=concept title="Edges: where the bugs live"}
Remember chapter 6's `over_budget` bug, `<=` instead of `<`? And chapter 4's grade boundaries, 80 is an A but 79
is not? Bugs love **boundaries**: the exact point where the answer changes. So good tests sit right on them:

| Kind of input | For over_budget(spent, budget=500) | Expected |
|---|---|---|
| clearly under | `over_budget(120, 500)` | `False` |
| exactly on the boundary | `over_budget(500, 500)` | `False` |
| just past the boundary | `over_budget(501, 500)` | `True` |
| clearly over | `over_budget(900, 500)` | `True` |

The middle two rows matter most. A test with only 120 and 900 passes on almost any version of the function,
including broken ones. The boundary tests are the ones that catch `>=` instead of `>`, or an off-by-one.

Also, compare booleans with `is`: `assert over_budget(500, 500) is False` checks for exactly `False`, not just
something false-ish like `0` or `None`.
:::

:::step{type=task task=edge_tests title="Your turn: pin down the boundary"}
Open `budget.py`: `over_budget(spent, budget)` is correct. In `test_budget.py`, write tests that pin down its
boundary.

Your tests must pass on the correct `budget.py`, and fail on both broken versions LabBox plants:

- one that says spending exactly the budget is over,
- one that only notices when you are **more than one rupee** over.

```bash run
cd /workspace/17-testing && python3 -m pytest -v test_budget.py
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which function does pytest run as a test?
:::
- [ ] `def check_total():`
- [x] `def test_total():`
- [ ] `def total_test():`
:::explain
pytest runs functions whose names **start** with `test_`, in files whose names start with `test_`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
When is a test useful?
:::
- [ ] When it always passes
- [x] When it passes on correct code and fails on broken code
- [ ] When it is long
:::explain
A test that passes whatever the code does proves nothing. Its value is that it fails when something breaks.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
For `is_adult(age)`, true from 18, which pair of tests guards the boundary best?
:::
- [ ] `is_adult(5)` and `is_adult(60)`
- [x] `is_adult(17)` and `is_adult(18)`
- [ ] `is_adult(30)` and `is_adult(40)`
:::explain
17 and 18 sit on either side of the exact point where the answer changes, where boundary bugs hide.
:::
:::

:::step{type=deep-dive title="Go deeper: testing errors, many cases at once, and writing tests first"}
**Testing that an error is raised.** For chapter 13's `to_number`:

```python
import pytest
from errors import to_number

def test_rejects_text():
    with pytest.raises(ValueError):
        to_number("abc")
```

The test passes only if the code inside raises a `ValueError`.

**Many cases, one test.** `@pytest.mark.parametrize` runs one test with a table of inputs and answers:

```python
@pytest.mark.parametrize("spent, expected", [(499, False), (500, False), (501, True)])
def test_over_budget(spent, expected):
    assert over_budget(spent, 500) is expected
```

**Tests first.** Many teams write the test *before* the code (test-driven development): write a failing test for
the next small behaviour, make it pass, tidy up, repeat. It forces you to decide what "correct" means before you
start typing.

**LabBox's own Check button** works exactly like this chapter: hidden tests, each with a message for when it
fails. You have been on the receiving end of good tests all course long.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write tests as `test_` functions with `assert`, and run them with `python3 -m pytest -v`.
- Read a pytest failure: the test, the line, and both sides of the comparison.
- Choose test cases that matter: normal, edge, and every promise the function makes.
- Put tests right on the boundaries, where bugs like `>=` instead of `>` hide.

:::photo{src="/lesson-images/python/py-17-notes.webp" alt="Handwritten notes about testing: def test_add, assert add(2, 3) == 5, python3 -m pytest, a good test fails on a bug" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 18: running a program, so Pocket becomes a real command-line tool.
:::
