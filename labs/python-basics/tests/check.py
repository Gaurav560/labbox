"""Hidden checks for python-basics. Prints one @@RESULT line per task."""
import importlib
import json
import sys
import traceback

sys.path.insert(0, "/check/workspace")
sys.dont_write_bytecode = True


def report(task: str, passed: bool, message: str) -> None:
    print("@@RESULT " + json.dumps({"task": task, "passed": passed, "message": message}), flush=True)


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
                report(task, False, f"{call} returned {got!r}, expected {expected!r}")
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
