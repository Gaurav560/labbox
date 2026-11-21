"""Hidden checks for the rewritten chapters of Python from zero (one folder per chapter).

Prints one @@RESULT line per task. LABBOX_CHAPTER (set by LabBox) limits the run to one chapter. The chapters
not rewritten yet are still checked by check.py, which reads files from the top of the workspace.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import traceback

W = "/check/workspace"
sys.dont_write_bytecode = True

# A pass teaches: one line on what went right and why it matters.
PASS = {
    "hello_pocket": "Pocket said its first words. Every program you ever write starts like this: a file, run "
                    "from the top, line by line.",
    "fix_first_errors": "Two errors read and fixed. You found the syntax error before anything ran, and the name "
                        "error only when its line was reached: reading Python's messages is half of programming.",
    "average": "Right: the total divided by how many, rounded to two decimals. Pocket can tell you your average "
               "spend now.",
    "format_price": "Spot on: separators and exactly two decimals, even for 5 and 999.999.",
    "greet": "Your first function works: it takes a name and returns new text. Every program is built from pieces "
             "like this.",
    "add": "Correct. Returning the result (not printing it) lets other code use it.",
    "is_even": "Right, including zero and negative numbers. n % 2 == 0 is a check you will meet everywhere.",
    "grade": "All the edges are right: 80, 79, 40, 39 and the invalid marks. Testing the boundaries is what careful "
             "developers do.",
    "leap_year": "Correct for 1900 and 2000 too. Three rules combined into one clear condition.",
    "count_above": "Well done: a counter, a loop and a condition. The limit itself is not counted, exactly as asked.",
    "first_negative": "Good: you stop at the first match and say None when there is nothing to find.",
    "fix_daily_total": "Found it: the loop started at position 1 and quietly skipped the first expense. Off-by-one "
                       "bugs are among the most common in the world, and now you know how to catch one.",
    "large_expenses": "One line, three parts: what to keep, the loop and the condition. That is a list comprehension, "
                      "and you will see them in every Python codebase.",
    "by_amount": "Biggest first, ties by name, and the original list untouched: a two-rule sort with one key.",
    "expense_class": "Your first class: __init__ sets each Expense up, and label() lets it describe itself.",
    "pocket_class": "Each Pocket has its own list, made in __init__, and methods that answer questions about it.",
    "money_module": "Refactored: the output is exactly the same, but format_price now lives in one place, ready for "
                    "any program to import.",
    "median_spend": "The standard library did the maths, and your function handles the one case it cannot: no data.",
    "first_tests": "Your tests pass on correct code and fail on both broken versions: that is what makes a test worth "
                   "having.",
    "edge_tests": "Right on the boundary: 500 of 500 is not over, 501 is. Those two tests catch bugs that dozens of "
                  "easy cases would miss.",
    "fix_over_budget": "Fixed: spending exactly the budget is fine now. Boundaries (< or <=) are where bugs love "
                       "to hide; printing the values made it visible.",
}


def report(task: str, passed: bool, message: str = "ok", expected=None, actual=None) -> None:
    if passed and message == "ok":
        message = PASS.get(task, "ok")
    result = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        result["expected"], result["actual"] = expected, actual
    print("@@RESULT " + json.dumps(result), flush=True)


def load(folder: str, module: str):
    """Import <folder>/<module>.py from the learner's workspace. Returns (module, error message)."""
    path = os.path.join(W, folder, f"{module}.py")
    if not os.path.isfile(path):
        return None, f"Could not find {folder}/{module}.py in your workspace."
    sys.path.insert(0, os.path.join(W, folder))
    try:
        spec = importlib.util.spec_from_file_location(f"{module}_{folder.replace('-', '_')}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None
    except SyntaxError as e:
        return None, f"{folder}/{module}.py has a syntax error on line {e.lineno}: {e.msg}. Run it in the terminal to see where."
    except Exception as e:
        traceback.print_exc()
        return None, f"{folder}/{module}.py crashed while loading: {type(e).__name__}: {e}"
    finally:
        sys.path.remove(os.path.join(W, folder))


def get_func(module, err, name: str):
    if module is None:
        return None, err
    fn = getattr(module, name, None)
    if not callable(fn):
        return None, f"No function named {name} was found. Check the spelling of its def line."
    return fn, None


def run_file(folder: str, name: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, name], cwd=os.path.join(W, folder), capture_output=True, text=True, timeout=10)


def lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.strip("\n").splitlines()]


# ---------- the advice for wrong answers learners really give ----------

def specific(task: str, args, got, expected) -> str:
    if task == "average" and isinstance(got, int):
        return "// drops the decimal part; / keeps it."
    if task == "average" and isinstance(got, float) and round(got, 2) == expected:
        return "The value is right but not rounded: round(..., 2) keeps two decimals."
    if task == "format_price" and isinstance(got, str) and "," not in got and abs(args[0]) >= 1000:
        return "Big amounts need thousands separators: look again at what a comma does inside an f-string format."
    if task == "format_price" and isinstance(got, str) and not got.startswith("₹"):
        return "The amount needs the rupee sign ₹ at the front."
    if task == "grade" and args[0] in (80, 60, 40):
        return "Check the boundary: 80 is an A, 60 a B, 40 a C. Use >=, not >."
    if task == "grade" and got in ("C", "B") and args[0] >= 80:
        return "Python stops at the first true condition: test the highest grade first."
    if task == "grade" and args[0] in (101, -1):
        return "Marks outside 0 to 100 are not marks at all: check for them first and return \"Invalid\"."
    if task == "leap_year" and args[0] in (1900, 2100):
        return "Years divisible by 100 are not leap years, unless they are also divisible by 400."
    if task == "count_above" and isinstance(got, int) and got > expected:
        return "Only numbers greater than the limit count; the limit itself does not."
    if task == "first_negative" and got == 0:
        return "0 is not below zero: compare with < 0."
    if task == "fix_daily_total" and isinstance(got, (int, float)) and args[0] and got == sum(args[0][1:]):
        return "The first expense is missing from the total. Print i inside the loop: which positions does it visit?"
    if task == "fix_over_budget" and got is True and sum(args[0]) == args[1]:
        return "Spending exactly the budget leaves 0 rupees: that is not over. Print left and look at the comparison."
    return ""


def advice(task, args, got, expected) -> str:
    if got is None and expected is not None and task in ("greet", "add", "is_even"):
        return ("The function gave back None. If you used print, change it to return: print shows text to a "
                "person, return gives the answer back to the code.")
    if got is None and expected is not None:
        return "The function gave back None: it needs a return statement with the answer."
    tip = specific(task, args, got, expected)
    if tip:
        return tip
    if type(got) is not type(expected) and got == expected:
        name = type(expected).__name__
        return f"The value is right but the type is not: give back a {name}, not a {type(got).__name__}."
    return ""


def run_cases(task: str, fn, err, cases) -> None:
    """cases: (args, expected) pairs. Reports the first one that goes wrong."""
    if fn is None:
        report(task, False, err)
        return
    try:
        for args, expected in cases:
            got = fn(*args)
            if got != expected or type(got) is not type(expected):
                call = f"{fn.__name__}({', '.join(repr(a) for a in args)})"
                msg = f"Not yet: {call} gave {got!r}, but it should be {expected!r}."
                tip = advice(task, args, got, expected)
                report(task, False, f"{msg} {tip}" if tip else msg, repr(expected), repr(got))
                return
        report(task, True)
    except Exception as e:
        traceback.print_exc()
        report(task, False, f"{fn.__name__} raised {type(e).__name__}: {e}. Run it in the terminal to see the line.")


# ---------- chapter 1: your first program ----------

def first_program() -> None:
    folder = "01-first-program"
    want = ["Hello! I am Pocket.", "I will help you track your money."]
    if not os.path.isfile(os.path.join(W, folder, "hello.py")):
        report("hello_pocket", False, f"Could not find {folder}/hello.py in your workspace.")
    else:
        run = run_file(folder, "hello.py")
        got = lines(run.stdout)
        if run.returncode != 0:
            last = (run.stderr.strip().splitlines() or ["an error"])[-1]
            report("hello_pocket", False, f"hello.py stopped with an error: {last}. Run python3 hello.py in the "
                   "terminal and read the message from the bottom.")
        elif not got:
            report("hello_pocket", False, "hello.py ran but printed nothing. Lines that start with # are notes for "
                   "people; Python skips them. Add print(...) lines.", "\n".join(want), "")
        elif got == want:
            report("hello_pocket", True)
        elif len(got) < 2:
            report("hello_pocket", False, "Not yet: hello.py printed one line; Pocket should say two. Each print(...) "
                   "prints one line.", "\n".join(want), "\n".join(got))
        elif [g.lower() for g in got] == [w.lower() for w in want]:
            report("hello_pocket", False, "So close: the words are right, but a capital letter differs. Python "
                   "prints exactly what is between the quotes.", "\n".join(want), "\n".join(got))
        else:
            report("hello_pocket", False, "Not yet: the lines differ from what Pocket should say. Compare them "
                   "letter by letter, including the full stops.", "\n".join(want), "\n".join(got))

    want = ["Pocket is starting...", "Ready to count your rupees.", "Today's budget is 500 rupees."]
    if not os.path.isfile(os.path.join(W, folder, "fix_me.py")):
        report("fix_first_errors", False, f"Could not find {folder}/fix_me.py in your workspace.")
        return
    run = run_file(folder, "fix_me.py")
    got = lines(run.stdout)
    if "SyntaxError" in run.stderr:
        report("fix_first_errors", False, "Python still finds a syntax error, so not one line runs. Run python3 "
               "fix_me.py: the ^ under the line points at the spot. A text needs a quote at both ends.")
    elif "NameError" in run.stderr:
        report("fix_first_errors", False, "One mistake fixed. Now Python stops at a name it does not know: read the "
               "last line of its message (it even suggests the right name).")
    elif run.returncode != 0:
        last = (run.stderr.strip().splitlines() or ["an error"])[-1]
        report("fix_first_errors", False, f"fix_me.py still stops with an error: {last}")
    elif got != want:
        report("fix_first_errors", False, "It runs now, but the lines changed. Fix only the two mistakes and keep "
               "the words as they were.", "\n".join(want), "\n".join(got))
    else:
        report("fix_first_errors", True)


# ---------- chapter 3: numbers and text ----------

def numbers_and_text() -> None:
    mod, err = load("03-numbers-and-text", "numbers_text")
    fn, e = get_func(mod, err, "average")
    run_cases("average", fn, e, [
        (([120, 80, 100],), 100.0), (([70, 71],), 70.5), (([1, 2, 2],), 1.67),
        (([100],), 100.0), (([0, 0],), 0.0), (([33, 34, 34],), 33.67),
    ])
    fn, e = get_func(mod, err, "format_price")
    run_cases("format_price", fn, e, [
        ((1250.5,), "₹1,250.50"), ((5,), "₹5.00"), ((1234567.891,), "₹1,234,567.89"), ((0,), "₹0.00"),
        ((999.999,), "₹1,000.00"), ((12.3,), "₹12.30"),
    ])


# ---------- chapter 2: your first functions ----------

def functions() -> None:
    mod, err = load("02-functions", "greet")
    fn, e = get_func(mod, err, "greet")
    run_cases("greet", fn, e, [(("Asha",), "Hello, Asha!"), (("World",), "Hello, World!"), (("",), "Hello, !")])
    mod, err = load("02-functions", "math_utils")
    fn, e = get_func(mod, err, "add")
    run_cases("add", fn, e, [((2, 3), 5), ((-1, 1), 0), ((0, 0), 0), ((100, 250), 350)])
    fn, e = get_func(mod, err, "is_even")
    run_cases("is_even", fn, e, [((2,), True), ((3,), False), ((0,), True), ((-4,), True), ((-7,), False)])


# ---------- chapter 4: making decisions ----------

def decisions() -> None:
    mod, err = load("04-decisions", "decisions")
    fn, e = get_func(mod, err, "grade")
    run_cases("grade", fn, e, [
        ((95,), "A"), ((80,), "A"), ((79,), "B"), ((60,), "B"), ((59,), "C"), ((40,), "C"), ((39,), "F"),
        ((100,), "A"), ((0,), "F"), ((101,), "Invalid"), ((-1,), "Invalid"),
    ])
    fn, e = get_func(mod, err, "is_leap_year")
    run_cases("leap_year", fn, e, [
        ((2024,), True), ((2023,), False), ((1900,), False), ((2000,), True), ((2100,), False),
        ((1600,), True), ((2019,), False),
    ])


# ---------- chapter 5: loops ----------

def loops() -> None:
    mod, err = load("05-loops", "loops")
    fn, e = get_func(mod, err, "count_above")
    run_cases("count_above", fn, e, [
        (([350, 720, 400, 900], 400), 2), (([], 10), 0), (([-5, -1, 3], -2), 2), (([40, 40], 40), 0),
        (([1, 2, 3], 0), 3),
    ])
    fn, e = get_func(mod, err, "first_negative")
    run_cases("first_negative", fn, e, [
        (([120, -50, 80, -20],), -50), (([1, 2, 3],), None), (([],), None), (([0, 5],), None), (([-1],), -1),
        (([0.0, -0.5, -3],), -0.5),
    ])


# ---------- chapter 6: finding bugs ----------

def finding_bugs() -> None:
    mod, err = load("06-finding-bugs", "spending")
    fn, e = get_func(mod, err, "daily_total")
    run_cases("fix_daily_total", fn, e, [
        (([120, 80, 100],), 300), (([50],), 50), (([],), 0), (([10, 20],), 30), (([0, 0, 7],), 7),
    ])
    fn, e = get_func(mod, err, "over_budget")
    run_cases("fix_over_budget", fn, e, [
        (([300, 200], 500), False), (([300, 250], 500), True), (([100], 500), False), (([], 0), False),
        (([1], 0), True),
    ])


# ---------- chapter 11: sorting and comprehensions ----------

WEEK = [
    {"name": "chai", "amount": 120}, {"name": "rent", "amount": 9000}, {"name": "bus", "amount": 40},
    {"name": "lunch", "amount": 120}, {"name": "phone", "amount": 599},
]


def sorting_and_comprehensions() -> None:
    import copy
    mod, err = load("11-sorting-and-comprehensions", "sorting")
    fn, e = get_func(mod, err, "large_expenses")
    run_cases("large_expenses", fn, e, [
        ((copy.deepcopy(WEEK), 500), ["rent", "phone"]), ((copy.deepcopy(WEEK), 100), ["chai", "rent", "lunch", "phone"]),
        ((copy.deepcopy(WEEK), 120), ["rent", "phone"]), (([], 10), []), ((copy.deepcopy(WEEK), 9000), []),
    ])
    fn, e = get_func(mod, err, "by_amount")
    if fn is None:
        report("by_amount", False, e)
        return
    try:
        week = copy.deepcopy(WEEK)
        got = fn(week)
        names = [x["name"] for x in got] if isinstance(got, list) else got
        want = ["rent", "phone", "chai", "lunch", "bus"]
        if week != WEEK:
            report("by_amount", False, "The order is one thing, but the list you were given changed: its order is now "
                   f"{[x['name'] for x in week]}. .sort() sorts the list itself; sorted() makes a new one.")
        elif got is None:
            report("by_amount", False, "by_amount gave back None. .sort() returns None: return sorted(...) instead.")
        elif names == ["bus", "chai", "lunch", "phone", "rent"]:
            report("by_amount", False, "Smallest first. Biggest first needs reverse=True, or a minus sign in the key.",
                   repr(want), repr(names))
        elif names == ["rent", "phone", "lunch", "chai", "bus"]:
            report("by_amount", False, "Biggest first, well done, but chai and lunch both cost 120: the same amount should "
                   "come in alphabetical order of name. A key can give back a tuple: (first rule, second rule).",
                   repr(want), repr(names))
        elif names != want:
            report("by_amount", False, f"Not yet: the names come out as {names}, but they should be {want}.", repr(want), repr(names))
        elif [x["name"] for x in fn([{"name": "tea", "amount": 15}, {"name": "bun", "amount": 15},
                                     {"name": "cake", "amount": 40}])] != ["cake", "bun", "tea"]:
            report("by_amount", False, "Biggest first works, but tea and bun both cost 15 and came out as tea, bun: the "
                   "same amount should come in alphabetical order of name. A key can give back a tuple: (first rule, "
                   "second rule).", repr(["cake", "bun", "tea"]))
        elif fn([]) != []:
            report("by_amount", False, "by_amount([]) should give back an empty list.")
        else:
            report("by_amount", True)
    except Exception as ex:
        traceback.print_exc()
        report("by_amount", False, f"by_amount raised {type(ex).__name__}: {ex}. Run it in the terminal to see the line.")


# ---------- chapter 15: classes ----------

def classes() -> None:
    mod, err = load("15-classes", "pocket")
    Expense = getattr(mod, "Expense", None) if mod else None
    Pocket = getattr(mod, "Pocket", None) if mod else None
    if Expense is None:
        report("expense_class", False, err or "No class named Expense was found in pocket.py.")
    else:
        try:
            e = Expense("lunch", 120, "food")
            plain = Expense("rent", 18000)
            missing = [a for a in ("name", "amount", "category") if not hasattr(e, a)]
            if missing:
                report("expense_class", False, f"An Expense needs the attributes name, amount and category; missing: "
                       f"{', '.join(missing)}. Store each one on self in __init__.")
            elif (e.name, e.amount, e.category) != ("lunch", 120, "food"):
                report("expense_class", False, f"Expense('lunch', 120, 'food') stored name={e.name!r}, amount={e.amount!r}, "
                       f"category={e.category!r}.")
            elif getattr(plain, "category", None) != "other":
                report("expense_class", False, "Without a category, an Expense's category should be \"other\": give the "
                       "parameter a default in __init__.")
            elif not callable(getattr(e, "label", None)):
                report("expense_class", False, "An Expense needs a method label(self).")
            elif e.label() != "lunch: ₹120.00 (food)":
                report("expense_class", False, "Not yet: Expense('lunch', 120, 'food').label() gave "
                       f"{e.label()!r}.", repr("lunch: ₹120.00 (food)"), repr(e.label()))
            elif plain.label() != "rent: ₹18,000.00 (other)":
                report("expense_class", False, "Big amounts need the thousands separator, as in chapter 3.",
                       repr("rent: ₹18,000.00 (other)"), repr(plain.label()))
            else:
                report("expense_class", True)
        except TypeError as ex:
            traceback.print_exc()
            report("expense_class", False, f"Creating an Expense failed: {ex}. __init__ takes self, name, amount and "
                   "category=\"other\".")
        except Exception as ex:
            traceback.print_exc()
            report("expense_class", False, f"Expense raised {type(ex).__name__}: {ex}")

    if Pocket is None or Expense is None:
        report("pocket_class", False, err or "No class named Pocket was found in pocket.py.")
        return
    try:
        a, b = Pocket(), Pocket()
        if not all(callable(getattr(a, m, None)) for m in ("add", "total", "biggest")):
            report("pocket_class", False, "A Pocket needs three methods: add(expense), total() and biggest().")
            return
        if a.biggest() is not None or a.total() != 0:
            report("pocket_class", False, f"An empty Pocket should have total() 0 and biggest() None; it gave "
                   f"{a.total()!r} and {a.biggest()!r}.")
            return
        lunch, bus = Expense("lunch", 120, "food"), Expense("bus", 30, "travel")
        a.add(lunch)
        a.add(bus)
        if b.total() != 0:
            report("pocket_class", False, "Two pockets share their expenses: adding to one changed the other. Make the "
                   "list in __init__ (self.expenses = []), not in the class body.")
        elif a.total() != 150:
            report("pocket_class", False, f"With lunch (120) and bus (30), total() gave {a.total()!r}.", "150", repr(a.total()))
        elif a.biggest() is not lunch:
            got = a.biggest()
            report("pocket_class", False, "biggest() should give back the Expense object with the largest amount (here, "
                   f"lunch); it gave {getattr(got, 'name', got)!r}.")
        else:
            report("pocket_class", True)
    except Exception as ex:
        traceback.print_exc()
        report("pocket_class", False, f"Pocket raised {type(ex).__name__}: {ex}")


# ---------- chapter 16: modules ----------

def modules() -> None:
    folder = "16-modules"
    want = ["₹120.00 = 12000 paise", "₹45.50 = 4550 paise", "₹1,250.00 = 125000 paise"]
    mod, err = load(folder, "money")
    tracker = os.path.join(W, folder, "tracker.py")
    if mod is None:
        report("money_module", False, err.replace("Could not find", "Create") if err else "money.py could not be loaded.")
    elif not callable(getattr(mod, "format_price", None)) or not callable(getattr(mod, "to_paise", None)):
        report("money_module", False, "money.py needs two functions: format_price(amount) and to_paise(amount).")
    elif mod.format_price(1250) != "₹1,250.00":
        report("money_module", False, f"money.format_price(1250) gave {mod.format_price(1250)!r}.", repr("₹1,250.00"),
               repr(mod.format_price(1250)))
    elif mod.to_paise(45.5) != 4550 or type(mod.to_paise(45.5)) is not int or mod.to_paise(0.1 + 0.2) != 30 \
            or mod.to_paise(0.29) != 29:
        got = (mod.to_paise(45.5), mod.to_paise(0.1 + 0.2))
        report("money_module", False, f"to_paise(45.5) should be the whole number 4550, to_paise(0.1 + 0.2) 30 and "
               f"to_paise(0.29) 29; they gave {got[0]!r}, {got[1]!r} and {mod.to_paise(0.29)!r}. Multiply by 100, then "
               "round to a whole number: int() cuts 28.999... down to 28.")
    else:
        source = open(tracker, encoding="utf-8").read() if os.path.isfile(tracker) else ""
        run = run_file(folder, "tracker.py")
        if "def format_price" in source:
            report("money_module", False, "tracker.py still defines its own format_price. Delete it and import the one "
                   "from money instead.")
        elif "money" not in source:
            report("money_module", False, "tracker.py does not import from money yet.")
        elif run.returncode != 0:
            report("money_module", False, "python3 tracker.py stopped with an error: "
                   + (run.stderr.strip().splitlines() or ["?"])[-1])
        elif lines(run.stdout) != want:
            report("money_module", False, "tracker.py runs, but its output changed. Refactoring keeps the output the same.",
                   "\n".join(want), run.stdout.strip())
        else:
            report("money_module", True)

    mod, err = load(folder, "stats_tools")
    fn, e = get_func(mod, err, "median_spend")
    if fn is not None:
        src = open(os.path.join(W, folder, "stats_tools.py"), encoding="utf-8").read()
        if "statistics" not in src:
            report("median_spend", False, "Use the statistics module from the standard library: import statistics.")
            return
    run_cases("median_spend", fn, e, [
        (([120, 45, 900],), 120), (([1, 2, 3, 4],), 2.5), (([],), None), (([5],), 5), (([300, 100],), 200.0),
    ])


# ---------- chapter 17: testing ----------

def _pytest(test_file: str, module: str, module_text: str) -> subprocess.CompletedProcess:
    """Run the learner's test file against one version of the module, in a fresh folder."""
    import tempfile
    d = tempfile.mkdtemp(prefix="t17-")
    with open(os.path.join(d, test_file), "w", encoding="utf-8") as f:
        f.write(open(os.path.join(W, "17-testing", test_file), encoding="utf-8").read())
    with open(os.path.join(d, f"{module}.py"), "w", encoding="utf-8") as f:
        f.write(module_text)
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", test_file], cwd=d,
                          capture_output=True, text=True, timeout=60)


MONEY_OK = 'def format_price(amount):\n    return f"₹{amount:,.2f}"\n\n\ndef to_paise(amount):\n    return round(amount * 100)\n'
MONEY_BUGS = {
    "the one that forgets the thousands separator": MONEY_OK.replace(":,.2f", ":.2f"),
    "the one that rounds to one decimal": MONEY_OK.replace(":,.2f", ":,.1f"),
}
BUDGET_OK = "def over_budget(spent, budget):\n    return spent > budget\n"
BUDGET_BUGS = {
    "the one that says exactly the budget is over": "def over_budget(spent, budget):\n    return spent >= budget\n",
    "the one that only notices when you are more than one rupee over":
        "def over_budget(spent, budget):\n    return spent > budget + 1\n",
}


def _own_tests(task: str, test_file: str, module: str, ok: str, bugs: dict, min_tests: int) -> None:
    path = os.path.join(W, "17-testing", test_file)
    if not os.path.isfile(path):
        report(task, False, f"Could not find 17-testing/{test_file}.")
        return
    good = _pytest(test_file, module, ok)
    out = good.stdout + good.stderr
    passed = re.search(r"(\d+) passed", out)
    if good.returncode == 5 or not passed:
        if good.returncode == 0 or good.returncode == 5:
            report(task, False, f"pytest found no tests in {test_file}. Each test is a function whose name starts with test_.")
        else:
            report(task, False, f"Your tests fail on the correct {module}.py, so a test expects the wrong answer:\n"
                   + out.strip()[-500:])
        return
    if good.returncode != 0:
        report(task, False, f"Your tests fail on the correct {module}.py, so a test expects the wrong answer:\n"
               + out.strip()[-500:])
        return
    if int(passed.group(1)) < min_tests:
        report(task, False, f"Write at least {min_tests} test functions; pytest found {passed.group(1)}.")
        return
    for name, text in bugs.items():
        if _pytest(test_file, module, text).returncode == 0:
            report(task, False, f"Your tests pass on the correct code, good. But they also pass on a broken version, "
                   f"{name}, so they would not catch that bug. Add a test that fails on it.")
            return
    report(task, True)


def testing() -> None:
    _own_tests("first_tests", "test_money.py", "money", MONEY_OK, MONEY_BUGS, 2)
    _own_tests("edge_tests", "test_budget.py", "budget", BUDGET_OK, BUDGET_BUGS, 2)


CHAPTERS = {
    "first-program": first_program,
    "02-numbers-and-text": numbers_and_text,
    "01-functions": functions,
    "03-decisions": decisions,
    "04-loops": loops,
    "finding-bugs": finding_bugs,
    "sorting-and-comprehensions": sorting_and_comprehensions,
    "classes": classes,
    "modules-and-packages": modules,
    "testing": testing,
}

if __name__ == "__main__":
    wanted = os.environ.get("LABBOX_CHAPTER", "")
    for chapter, check in CHAPTERS.items():
        if not wanted or wanted == chapter:
            check()
