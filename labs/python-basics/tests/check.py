"""Hidden checks for python-basics. Prints one @@RESULT line per task."""
import importlib
import json
import sys
import traceback

sys.path.insert(0, "/check/workspace")
sys.dont_write_bytecode = True


def report(task: str, passed: bool, message: str, expected=None, actual=None) -> None:
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
                report(task, False, f"{call} returned {got!r}, expected {expected!r}", repr(expected), repr(got))
                return
        report(task, True, "ok")
    except Exception as e:
        traceback.print_exc()
        report(task, False, f"{fn.__name__} raised {type(e).__name__}: {e}")


greet_mod, greet_err = load("greet")
math_mod, math_err = load("math_utils")

fn, err = get_func(greet_mod, greet_err, "greet")
run_cases("greet", fn, err, [(("Asha",), "Hello, Asha!"), (("World",), "Hello, World!"), (("",), "Hello, !")])

fn, err = get_func(math_mod, math_err, "add")
run_cases("add", fn, err, [((2, 3), 5), ((-1, 1), 0), ((0, 0), 0), ((100, 250), 350)])

fn, err = get_func(math_mod, math_err, "is_even")
run_cases("is_even", fn, err, [((2,), True), ((3,), False), ((0,), True), ((-4,), True), ((-7,), False)])

# ---------- chapter 2: numbers and text ----------
nt_mod, nt_err = load("numbers_text")

fn, err = get_func(nt_mod, nt_err, "average")
run_cases("average", fn, err, [
    (([78, 85, 92],), 85.0), (([70, 71],), 70.5), (([1, 2, 2],), 1.67), (([],), 0.0),
    (([100],), 100.0), (([0, 0],), 0.0), (([33, 34, 34],), 33.67),
])

fn, err = get_func(nt_mod, nt_err, "format_price")
run_cases("format_price", fn, err, [
    ((1250.5,), "₹1,250.50"), ((5,), "₹5.00"), ((1234567.891,), "₹1,234,567.89"), ((0,), "₹0.00"),
    ((999.999,), "₹1,000.00"), ((12.3,), "₹12.30"),
])

# ---------- chapter 3: decisions ----------
dec_mod, dec_err = load("decisions")

fn, err = get_func(dec_mod, dec_err, "grade")
run_cases("grade", fn, err, [
    ((95,), "A"), ((80,), "A"), ((79,), "B"), ((60,), "B"), ((59,), "C"), ((40,), "C"), ((39,), "F"),
    ((100,), "A"), ((0,), "F"), ((101,), "Invalid"), ((-1,), "Invalid"),
])

fn, err = get_func(dec_mod, dec_err, "is_leap_year")
run_cases("leap_year", fn, err, [
    ((2024,), True), ((2023,), False), ((1900,), False), ((2000,), True), ((2100,), False),
    ((1600,), True), ((2019,), False),
])

# ---------- chapter 4: loops ----------
loop_mod, loop_err = load("loops")

fn, err = get_func(loop_mod, loop_err, "count_above")
run_cases("count_above", fn, err, [
    (([35, 72, 40, 90], 40), 2), (([], 10), 0), (([-5, -1, 3], -2), 2), (([40, 40], 40), 0),
    (([1, 2, 3], 0), 3),
])

fn, err = get_func(loop_mod, loop_err, "first_negative")
run_cases("first_negative", fn, err, [
    (([4, -2, 7, -9],), -2), (([1, 2, 3],), None), (([],), None), (([0, 5],), None), (([-1],), -1),
    (([0.0, -0.5, -3],), -0.5),
])

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
lst_mod, lst_err = load("lists")

fn, err = get_func(lst_mod, lst_err, "top_n")
if fn is None:
    report("top_n", False, err)
else:
    try:
        marks = [72, 45, 90, 66]
        got = fn(marks, 2)
        if marks != [72, 45, 90, 66]:
            report("top_n", False, f"top_n changed the list it was given: it is now {marks}. Use sorted(), not .sort().",
                   "[72, 45, 90, 66]", repr(marks))
        else:
            run_cases("top_n", fn, None, [
                (([72, 45, 90, 66], 2), [90, 72]), (([5, 1], 5), [5, 1]), (([3, 1, 2], 0), []), (([], 3), []),
                (([4, 4, 1], 2), [4, 4]),
            ])
    except Exception as e:
        traceback.print_exc()
        report("top_n", False, f"top_n raised {type(e).__name__}: {e}")

fn, err = get_func(lst_mod, lst_err, "remove_duplicates")
run_cases("remove_duplicates", fn, err, [
    (([3, 1, 3, 2, 1],), [3, 1, 2]), ((["tea", "coffee", "tea"],), ["tea", "coffee"]), (([],), []),
    (([5, 5, 5],), [5]), (([2, 1],), [2, 1]),
])

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
