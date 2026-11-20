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
