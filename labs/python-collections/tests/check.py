"""Hidden checks for python-collections. Prints one @@RESULT line per task; never prints the solution."""
import json
import sys
import traceback

sys.path.insert(0, "/check/workspace")
sys.dont_write_bytecode = True

PRICES = {"veg thali": 120, "dal rice": 90, "paneer roll": 110, "curd rice": 80}


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


def run(task, fn_name, cases):
    fn = getattr(mod, fn_name, None)
    if not callable(fn):
        report(task, False, f"No function named {fn_name} in orders.py")
        return
    try:
        for args, want in cases:
            got = fn(*args)
            if got != want:
                shown = ", ".join(repr(a) if len(repr(a)) < 60 else "[...]" for a in args)
                report(task, False, f"{fn_name}({shown}) returned {got!r}", repr(want), repr(got))
                return
        report(task, True, "ok")
    except Exception as e:
        traceback.print_exc()
        report(task, False, f"{fn_name} raised {type(e).__name__}: {e}")


try:
    import orders as mod
except Exception as e:
    traceback.print_exc()
    for t in ("total_bill", "top_dishes", "unique_areas", "route_order"):
        report(t, False, f"orders.py could not be loaded: {type(e).__name__}: {e}")
    raise SystemExit(0)

run("total_bill", "total_bill", [
    ((["veg thali", "dal rice", "veg thali"], PRICES), 330),
    (([], PRICES), 0),
    ((["curd rice"], PRICES), 80),
])
run("top_dishes", "top_dishes", [
    ((["dal rice", "veg thali", "dal rice"], 1), ["dal rice"]),
    ((["poha", "dal rice", "poha", "veg thali", "dal rice", "idli"], 2), ["dal rice", "poha"]),
    ((["b", "a", "c"], 2), ["a", "b"]),
    (([], 3), []),
])
areas = [{"dish": "x", "area": a} for a in ["Kothrud", "Baner", "Kothrud", "Aundh", "Baner"]]
run("unique_areas", "unique_areas", [
    ((areas,), ["Aundh", "Baner", "Kothrud"]),
    (([],), []),
])
run("route_order", "route_order", [
    (([("Baner", 7.5), ("Aundh", 3.0)],), ["Aundh", "Baner"]),
    (([("Wakad", 9.0), ("Hinjewadi", 9.0), ("Pashan", 4.2)],), ["Pashan", "Hinjewadi", "Wakad"]),
    (([],), []),
])
