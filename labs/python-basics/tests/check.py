"""Hidden checks for the chapters of python-basics not rewritten yet (files at the top of the workspace).
Prints one @@RESULT line per task. The rewritten chapters, one folder each, are in checks.py."""
import importlib
import json
import sys
import traceback

sys.path.insert(0, "/check/workspace")
sys.dont_write_bytecode = True


# Content standard: a pass teaches (one line on what went right), a failure says what to try.
PASS = {
    "greet": "Your first function works: it takes a name and returns new text. Every program is built from pieces like this.",
    "add": "Correct. Returning the result (not printing it) lets other code use it.",
    "is_even": "Right, including zero and negative numbers. n % 2 == 0 is a check you will meet everywhere.",
    "average": "Nice: the empty list is handled and the result is rounded. Real data is often empty; your function copes.",
    "format_price": "Spot on: separators and exactly two decimals, even for 5 and 999.999.",
    "grade": "All the edges are right: 80, 79, 40, 39 and the invalid marks. Testing the boundaries is what careful developers do.",
    "leap_year": "Correct for 1900 and 2000 too. Three rules combined into one clear condition.",
    "count_above": "Well done: a counter, a loop and a condition. The limit itself is not counted, exactly as asked.",
    "first_negative": "Good: you stop at the first match and say None when there is nothing to find.",
    "count_words": "Correct, even with extra spaces, tabs and new lines. split() with no argument does the hard work.",
    "clean_name": "Tidy: no extra spaces and every word capitalised. You chained split, join and title like a pro.",
    "count_letters": "Nice counting: the get-with-a-default line is the classic way to count with a dictionary.",
    "total_by_category": "Correct totals per category. Lists of small dictionaries are how real data arrives.",
    "common_items": "Right: sets found the shared items, and sorting made the answer predictable.",
    "min_max": "Good: two answers at once in a tuple, and a clear answer for an empty list.",
    "add_item": "You fixed one of Python's most famous traps. Many experienced developers have shipped this bug; you will spot it now.",
    "total": "Correct, and the discount can only be given by name, so nobody passes it by mistake.",
    "to_number": "Clear errors that name the bad value: whoever reads them will know exactly what to fix.",
    "safe_sum": "Robust: good values added, bad ones reported, nothing crashes.",
    "save_lines": "The file holds exactly your lines. Opening with 'w' and a with block is the safe way to write files.",
    "read_totals": "You read a messy real file without crashing, quoted commas and all. That is a real-world skill.",
    "summary_top": "Your program runs from the command line and prints a clean answer. You built a real tool.",
    "summary_errors": "A friendly message, the right exit code, and silence on import: this is how professional tools behave.",
    "fix_budget": "Found and fixed all three bugs in someone else's code: the crash, the boundary and the missing return.",
    "monthly_report": "A complete report from messy data, with the right line numbers. You have finished Python from zero: well done.",
}


def report(task: str, passed: bool, message: str, expected=None, actual=None) -> None:
    if passed and message == "ok":
        message = PASS.get(task, "ok")
    result = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        # Optional v2 fields: the UI shows them side by side.
        result["expected"], result["actual"] = expected, actual
    print("@@RESULT " + json.dumps(result), flush=True)


def load(module_name: str):
    """Import a user module. Returns (module, error_message)."""
    try:
        return importlib.import_module(module_name), None
    except SyntaxError as e:
        return None, f"{module_name}.py has a syntax error on line {e.lineno}: {e.msg}"
    except ModuleNotFoundError as e:
        if e.name == module_name:
            return None, f"Could not find {module_name}.py in your workspace"
        traceback.print_exc()
        return None, f"{module_name}.py failed to import: {e}"
    except Exception as e:
        traceback.print_exc()
        return None, f"{module_name}.py crashed while importing: {type(e).__name__}: {e}"


def get_func(module, module_err, name: str):
    if module is None:
        return None, module_err
    fn = getattr(module, name, None)
    if not callable(fn):
        return None, f"No function named {name} was found"
    return fn, None


def advice(task: str, args, got, expected) -> str:
    """One line on the likely mistake, for the wrong answers learners really give."""
    if got is None:
        return "The function gave back None: it needs a return statement with the answer."
    tip = _specific(task, args, got, expected)
    if tip:
        return tip
    if type(got) is not type(expected) and got == expected:
        def a(t):
            return ("an " if t[0] in "aeiou" else "a ") + t
        return f"The value is right but the type is not: give back {a(type(expected).__name__)}, not {a(type(got).__name__)}."
    return ""


def _specific(task: str, args, got, expected) -> str:
    """The mistakes a task is known for, checked before the general advice."""
    if task == "average" and isinstance(got, int):
        return "// drops the decimal part; / keeps it."
    if task == "format_price" and isinstance(got, str) and "," not in got and abs(args[0]) >= 1000:
        return "Big amounts need thousands separators: look again at what a comma does inside an f-string format."
    if task == "grade" and args[0] in (80, 60, 40):
        return "Check the boundary: 80 is an A, 60 a B, 40 a C. Use >=, not >."
    if task == "grade" and got in ("C", "B") and args[0] >= 80:
        return "Python stops at the first true condition: test the highest grade first."
    if task == "leap_year" and args[0] in (1900, 2100):
        return "Years divisible by 100 are not leap years, unless they are also divisible by 400."
    if task == "count_above" and isinstance(got, int) and got > expected:
        return "Only numbers greater than the limit count; the limit itself does not."
    if task == "clean_name" and isinstance(got, str) and "  " in got:
        return "There are still double spaces inside: split() with no argument, then join with one space."
    if task == "count_words" and isinstance(got, int) and got > expected:
        return "split(\" \") makes an empty piece for every extra space; split() with no argument does not."
    if task == "count_letters" and isinstance(got, dict) and any(not k.isalpha() or k.isupper() for k in got):
        return "Count only letters (isalpha), and lower() the text first so A and a count together."
    if task == "common_items" and isinstance(got, list) and len(got) != len(set(got)):
        return "Some items appear twice: turn the lists into sets first."
    if task == "common_items" and isinstance(got, list) and sorted(got) == expected:
        return "The right items, in another order: give back sorted(...)."
    return ""


def run_cases(task: str, fn, err, cases) -> None:
    """cases: list of (args, expected). Reports first failure."""
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
        report(task, True, "ok")
    except Exception as e:
        traceback.print_exc()
        report(task, False, f"{fn.__name__} raised {type(e).__name__}: {e}")


# Chapters 1 to 6 (first program, numbers and text, functions, decisions, loops, finding bugs) live in
# their own folders now and are checked by checks.py.

# ---------- chapter 5: strings ----------
txt_mod, txt_err = load("text_tools")

fn, err = get_func(txt_mod, txt_err, "clean_name")
run_cases("clean_name", fn, err, [
    (("  riya   SHARMA ",), "Riya Sharma"), (("ARJUN",), "Arjun"), (("   ",), ""), (("meera\tnair",), "Meera Nair"),
    (("a b",), "A B"), (("priya",), "Priya"),
])

fn, err = get_func(txt_mod, txt_err, "count_words")
run_cases("count_words", fn, err, [
    (("Python is fun",), 3), (("  lots   of   spaces  ",), 3), (("",), 0), (("hello, world",), 2), (("one",), 1),
    (("tab\tand\nnew line",), 4),
])

# ---------- chapter 6: lists ----------
# Content standard: a failure says what happened, why, and what to try; a pass says what went right.
lst_mod, lst_err = load("lists")

fn, err = get_func(lst_mod, lst_err, "remove_duplicates")
if fn is None:
    report("remove_duplicates", False, err)
else:
    try:
        for items, expected in [([3, 1, 3, 2, 1], [3, 1, 2]), (["tea", "coffee", "tea"], ["tea", "coffee"]), ([], []),
                                ([5, 5, 5], [5]), ([2, 1], [2, 1])]:
            got = fn(list(items))
            if got == expected:
                continue
            call = f"remove_duplicates({items!r})"
            if got is None:
                msg = f"{call} gave None. Nearly there: the function needs to return the new list at the end."
            elif sorted(map(str, got)) == sorted(map(str, expected)) and got != expected:
                msg = (f"{call} gave {got!r}: the right items, but in a different order. A set loses the order; "
                       "build the result with a loop and append, as in the worked example.")
            elif len(got) > len(expected):
                msg = f"{call} gave {got!r}: some items appear twice. Append an item only when it is not in the result yet."
            else:
                msg = f"{call} gave {got!r}, but it should be {expected!r}."
            report("remove_duplicates", False, msg, repr(expected), repr(got))
            break
        else:
            report("remove_duplicates", True, "Nice: each item once, and the original order kept. That loop-and-append "
                   "pattern is one you will use in almost every program.")
    except Exception as e:
        traceback.print_exc()
        report("remove_duplicates", False, f"remove_duplicates raised {type(e).__name__}: {e}. See Output for the line.")

fn, err = get_func(lst_mod, lst_err, "top_n")
if fn is None:
    report("top_n", False, err)
else:
    try:
        marks = [72, 45, 90, 66]
        got = fn(marks, 2)
        if marks != [72, 45, 90, 66]:
            report("top_n", False, f"top_n gave the right kind of answer, but it changed the list it was given: the caller's "
                   f"list is now {marks}. .sort() sorts the list itself; sorted() makes a new one. Try sorted().",
                   "[72, 45, 90, 66]", repr(marks))
        else:
            for args, expected in [(([72, 45, 90, 66], 2), [90, 72]), (([5, 1], 5), [5, 1]), (([3, 1, 2], 0), []),
                                   (([], 3), []), (([4, 4, 1], 2), [4, 4])]:
                got = fn(*args)
                if got != expected:
                    call = f"top_n({args[0]!r}, {args[1]!r})"
                    if got is None:
                        msg = f"{call} gave None. .sort() returns None: return the sorted list itself (or use sorted())."
                    elif isinstance(got, list) and got and got == sorted(args[0])[: args[1]]:
                        msg = f"{call} gave {got!r}: smallest first. Ask sorted() for the biggest first with reverse=True."
                    elif isinstance(got, list) and len(got) != len(expected):
                        msg = f"{call} gave {len(got)} numbers but should give {len(expected)}. A slice like [:n] keeps the first n."
                    else:
                        msg = f"{call} gave {got!r}, but it should be {expected!r}."
                    report("top_n", False, msg, repr(expected), repr(got))
                    break
            else:
                report("top_n", True, "Well done: the biggest first, and the caller's list left exactly as it was. "
                       "Leaving inputs alone is a habit good developers are known for.")
    except Exception as e:
        traceback.print_exc()
        report("top_n", False, f"top_n raised {type(e).__name__}: {e}. See Output for the line.")

# ---------- chapter 7: dictionaries ----------
dct_mod, dct_err = load("dict_tools")

fn, err = get_func(dct_mod, dct_err, "count_letters")
run_cases("count_letters", fn, err, [
    (("Hello!",), {"h": 1, "e": 1, "l": 2, "o": 1}), (("A a",), {"a": 2}), (("123 ?!",), {}), (("",), {}),
    (("Mississippi",), {"m": 1, "i": 4, "s": 4, "p": 2}),
])


def same_values(task, fn, err, cases):
    """Like run_cases, but 200 and 200.0 count as the same answer."""
    if fn is None:
        report(task, False, err)
        return
    try:
        for args, expected in cases:
            got = fn(*args)
            if got != expected:
                call = f"{fn.__name__}({', '.join(repr(a) for a in args)})"
                report(task, False, f"{call} returned {got!r}, expected {expected!r}", repr(expected), repr(got))
                return
        report(task, True, "ok")
    except Exception as e:
        traceback.print_exc()
        report(task, False, f"{fn.__name__} raised {type(e).__name__}: {e}")


EXPENSES = [{"category": "food", "amount": 120}, {"category": "travel", "amount": 40}, {"category": "food", "amount": 80}]
fn, err = get_func(dct_mod, dct_err, "total_by_category")
same_values("total_by_category", fn, err, [
    ((EXPENSES,), {"food": 200, "travel": 40}), (([],), {}),
    (([{"category": "fun", "amount": 120.5}, {"category": "fun", "amount": 0.5}],), {"fun": 121.0}),
    (([{"category": "rent", "amount": 9000}],), {"rent": 9000}),
])

# ---------- chapter 8: tuples and sets ----------
st_mod, st_err = load("sets_tuples")

fn, err = get_func(st_mod, st_err, "common_items")
run_cases("common_items", fn, err, [
    ((["tea", "coffee", "milk"], ["milk", "tea", "juice"]), ["milk", "tea"]), (([1, 2, 2, 3], [2, 2, 4]), [2]),
    (([1, 2], [3, 4]), []), (([], [1]), []), (([3, 2, 1], [1, 2, 3]), [1, 2, 3]),
])

fn, err = get_func(st_mod, st_err, "min_max")
run_cases("min_max", fn, err, [
    (([72, 45, 90],), (45, 90)), (([7],), (7, 7)), (([],), (None, None)), (([-3, -10, 4.5],), (-10, 4.5)),
])

# ---------- chapter 9: functions in depth ----------
fun_mod, fun_err = load("functions")

fn, err = get_func(fun_mod, fun_err, "add_item")
if fn is None:
    report("add_item", False, err)
else:
    try:
        first, second, third = fn("milk"), fn("bread"), fn("eggs")
        mine = ["milk"]
        given = fn("tea", mine)
        if second != ["bread"]:
            report("add_item", False, f'add_item("milk") then add_item("bread") gave {second!r}: the calls share one basket. '
                   "A default list is made once and reused; use None as the default.", "['bread']", repr(second))
        elif first != ["milk"] or third != ["eggs"]:
            report("add_item", False, f"Three calls without a basket gave {first!r}, {second!r}, {third!r}; each should hold one item.")
        elif given is not mine or mine != ["milk", "tea"]:
            report("add_item", False, 'add_item("tea", basket) should add to the basket it was given and return that same '
                   f"basket, but the caller's basket is still {mine!r} (a copy was changed instead).", "['milk', 'tea']", repr(mine))
        else:
            report("add_item", True, "ok")
    except Exception as e:
        traceback.print_exc()
        report("add_item", False, f"add_item raised {type(e).__name__}: {e}")

fn, err = get_func(fun_mod, fun_err, "total")
if fn is None:
    report("total", False, err)
else:
    try:
        cases = [((100, 50), {}, 150.0), ((100, 50), {"discount": 10}, 135.0), ((), {}, 0.0), ((99.99, 0.01), {}, 100.0),
                 ((100, 10), {}, 110.0), ((10,), {"discount": 33}, 6.7)]
        for args, kw, expected in cases:
            got = fn(*args, **kw)
            if got != expected or type(got) is not float:
                call = "total(" + ", ".join([*map(repr, args), *(f"{k}={v!r}" for k, v in kw.items())]) + ")"
                report("total", False, f"{call} returned {got!r}, expected {expected!r}", repr(expected), repr(got))
                break
        else:
            report("total", True, "ok")
    except TypeError as e:
        report("total", False, f"total could not be called like total(100, 50, discount=10): {e}")
    except Exception as e:
        traceback.print_exc()
        report("total", False, f"total raised {type(e).__name__}: {e}")

# ---------- chapter 10: errors ----------
import os
import subprocess
import tempfile

err_mod, err_mod_err = load("errors")

fn, err = get_func(err_mod, err_mod_err, "to_number")
if fn is None:
    report("to_number", False, err)
else:
    try:
        for args, expected in [(("12.5",), 12.5), ((" 7 ",), 7.0), (("-3",), -3.0), (("1e3",), 1000.0)]:
            got = fn(*args)
            if got != expected or type(got) is not float:
                report("to_number", False, f"to_number({args[0]!r}) returned {got!r}, expected {expected!r}", repr(expected), repr(got))
                break
        else:
            for bad in ("abc", "", "12a"):
                try:
                    got = fn(bad)
                except ValueError as e:
                    if bad and bad not in str(e):
                        report("to_number", False, f"to_number({bad!r}) raised ValueError({str(e)!r}): the message should include {bad!r}.")
                        break
                except Exception as e:
                    report("to_number", False, f"to_number({bad!r}) raised {type(e).__name__}, expected a ValueError.")
                    break
                else:
                    report("to_number", False, f"to_number({bad!r}) returned {got!r} instead of raising ValueError.")
                    break
            else:
                report("to_number", True, "ok")
    except Exception as e:
        traceback.print_exc()
        report("to_number", False, f"to_number raised {type(e).__name__}: {e}")

fn, err = get_func(err_mod, err_mod_err, "safe_sum")
if fn is not None:
    try:
        empty = fn([])
        if not (isinstance(empty, tuple) and len(empty) == 2 and type(empty[0]) is float):
            fn, err = None, f"safe_sum([]) returned {empty!r}: the total should always be a float, like (0.0, [])"
    except Exception:
        pass  # run_cases below reports the error
run_cases("safe_sum", fn, err, [
    ((["10", "x", "2.5", ""],), (12.5, ["x", ""])), ((["1", "2"],), (3.0, [])), (([],), (0.0, [])),
    ((["abc"],), (0.0, ["abc"])), (([" 4 ", "1e1"],), (14.0, [])),
])

# ---------- chapter 11: files ----------
TMP = tempfile.mkdtemp(prefix="labbox-check-")
SAMPLE = "date,category,amount\n2026-03-02,food,120\n2026-03-02,travel,40.50\n\n2026-03-03,food,80\n2026-03-04,food,abc\n2026-03-04,travel,\n"


def tmp_file(name: str, text: str) -> str:
    path = os.path.join(TMP, name)
    with open(path, "w") as f:
        f.write(text)
    return path


ft_mod, ft_err = load("file_tools")

fn, err = get_func(ft_mod, ft_err, "read_totals")
if fn is None:
    report("read_totals", False, err)
else:
    try:
        cases = [
            ("sample.csv", SAMPLE, {"food": 200.0, "travel": 40.5}),
            ("header_only.csv", "date,category,amount\n", {}),
            ("quoted.csv", 'date,category,amount\n2026-03-05,"snacks, tea",30\n2026-03-06,"snacks, tea",12.25\n', {"snacks, tea": 42.25}),
        ]
        for name, text, expected in cases:
            got = fn(tmp_file(name, text))
            if got != expected:
                why = " (a value with a comma inside quotes: use the csv module, not split)" if "quoted" in name else ""
                report("read_totals", False, f"read_totals on a file like\n{text.strip()}\nreturned {got!r}, expected {expected!r}{why}",
                       repr(expected), repr(got))
                break
        else:
            report("read_totals", True, "ok")
    except Exception as e:
        traceback.print_exc()
        report("read_totals", False, f"read_totals raised {type(e).__name__}: {e} (skip rows with a missing or bad amount)")

fn, err = get_func(ft_mod, ft_err, "save_lines")
if fn is None:
    report("save_lines", False, err)
else:
    try:
        path = tmp_file("out.txt", "old content that must go\n")
        n = fn(path, ["food: 200.00", "travel: 40.50"])
        text = open(path).read()
        n0 = fn(tmp_file("empty.txt", "x"), [])
        text0 = open(os.path.join(TMP, "empty.txt")).read()
        if text != "food: 200.00\ntravel: 40.50\n":
            report("save_lines", False, f"The file should contain each line followed by a new line, and nothing else; it contains {text!r}.",
                   repr("food: 200.00\ntravel: 40.50\n"), repr(text))
        elif n != 2 or n0 != 0:
            report("save_lines", False, f"save_lines should return how many lines it wrote: got {n!r} for 2 lines and {n0!r} for none.")
        elif text0 != "":
            report("save_lines", False, f"save_lines with no lines should leave an empty file; it contains {text0!r}.")
        else:
            report("save_lines", True, "ok")
    except Exception as e:
        traceback.print_exc()
        report("save_lines", False, f"save_lines raised {type(e).__name__}: {e}")

# ---------- chapter 12: a command-line program ----------
BIG = ("date,category,amount\n2026-03-01,rent,18000\n2026-03-02,food,120\n2026-03-03,shopping,799\n"
       "2026-03-03,food,abc\n2026-03-04,travel,60\n2026-03-05,food,80.5\n2026-03-06,fun,350\n")


def run_py(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd="/check/workspace", capture_output=True, text=True, timeout=20)


if not os.path.exists("/check/workspace/summary.py"):
    report("summary_top", False, "Could not find summary.py in your workspace")
    report("summary_errors", False, "Could not find summary.py in your workspace")
else:
    data = tmp_file("big.csv", BIG)
    try:
        r2, r3 = run_py("summary.py", data, "--top", "2"), run_py("summary.py", data)
        want2, want3 = "rent: 18000.00\nshopping: 799.00\n", "rent: 18000.00\nshopping: 799.00\nfun: 350.00\n"
        if r2.returncode != 0:
            report("summary_top", False, f"python summary.py big.csv --top 2 failed:\n{(r2.stderr or r2.stdout)[-600:]}")
        elif r2.stdout != want2:
            report("summary_top", False, f"python summary.py big.csv --top 2 printed\n{r2.stdout}expected\n{want2}", want2, r2.stdout)
        elif r3.stdout != want3:
            report("summary_top", False, f"Without --top it should print the top 3; it printed\n{r3.stdout}", want3, r3.stdout)
        else:
            report("summary_top", True, "ok")
    except subprocess.TimeoutExpired:
        report("summary_top", False, "summary.py did not finish within 20 seconds (is it waiting for input?)")

    try:
        missing = os.path.join(TMP, "missing.csv")
        r = run_py("summary.py", missing)
        imp = run_py("-c", "import summary")
        if "Traceback" in r.stderr:
            report("summary_errors", False, "A missing file should give one friendly line, not a traceback:\n" + r.stderr[-400:])
        elif f"File not found: {missing}" not in r.stderr:
            report("summary_errors", False, f"For a missing file, stderr should say 'File not found: {missing}'; it said {r.stderr.strip()!r}"
                   + (f" and stdout said {r.stdout.strip()!r}" if r.stdout.strip() else ""))
        elif r.returncode != 1:
            report("summary_errors", False, f"For a missing file the exit code should be 1; it was {r.returncode}.")
        elif imp.returncode != 0 or imp.stdout or imp.stderr:
            report("summary_errors", False, "import summary should print nothing (put the work under if __name__ == \"__main__\"); it printed "
                   + repr((imp.stdout + imp.stderr)[-300:]))
        else:
            report("summary_errors", True, "ok")
    except subprocess.TimeoutExpired:
        report("summary_errors", False, "summary.py did not finish within 20 seconds")

# ---------- chapter 13: the capstone ----------
rep_mod, rep_err = load("report")

fn, err = get_func(rep_mod, rep_err, "monthly_report")
if fn is None:
    report("monthly_report", False, err)
else:
    try:
        small = tmp_file("guess.csv", "date,category,amount\n2026-03-02,food,120\n2026-03-03,,45\n2026-03-03,travel,abc\n2026-03-04,rent,18000\n")
        want = {"total": 18120.0, "count": 2, "average": 9060.0, "biggest": {"category": "rent", "amount": 18000.0},
                "per_category": {"food": 120.0, "rent": 18000.0}, "bad_lines": [3, 4]}
        blanky = tmp_file("blank.csv", "date,category,amount\n2026-03-01,food,10\n\n2026-03-02,food,x\n2026-03-03,fun,20.5\n")
        want_b = {"total": 30.5, "count": 2, "average": 15.25, "biggest": {"category": "fun", "amount": 20.5},
                  "per_category": {"food": 10.0, "fun": 20.5}, "bad_lines": [4]}
        empty = tmp_file("none.csv", "date,category,amount\n")
        want_e = {"total": 0.0, "count": 0, "average": 0.0, "biggest": None, "per_category": {}, "bad_lines": []}
        for label, path, expected in [("the five lines from the chapter", small, want),
                                      ("a file with a blank line (line numbers must count it)", blanky, want_b),
                                      ("a file with only the header", empty, want_e)]:
            got = fn(path)
            if not isinstance(got, dict):
                report("monthly_report", False, f"monthly_report should return a dictionary; it returned {got!r}")
                break
            wrong = [k for k in expected if got.get(k) != expected[k]]
            if wrong:
                k = wrong[0]
                report("monthly_report", False, f"For {label}, {k!r} is {got.get(k)!r}, expected {expected[k]!r}", repr(expected[k]), repr(got.get(k)))
                break
        else:
            report("monthly_report", True, "ok")
    except Exception as e:
        traceback.print_exc()
        report("monthly_report", False, f"monthly_report raised {type(e).__name__}: {e}")

bud_mod, bud_err = load("budget")
fn, err = get_func(bud_mod, bud_err, "over_budget")
run_cases("fix_budget", fn, err, [
    (({"food": 500, "travel": 50}, {"food": 400, "travel": 100}), ["food"]),
    (({"food": 500}, {"food": 400, "fun": 100}), ["food"]),
    (({"b": 10, "a": 10}, {"b": 5, "a": 5}), ["a", "b"]),
    (({"food": 400}, {"food": 400}), []),
    (({}, {}), []),
])
