"""Hidden checks. Prints one @@RESULT line per task; never prints the solution."""
import json
import sys
import traceback

sys.path.insert(0, "/check/workspace")
sys.dont_write_bytecode = True


def report(task, passed, message, expected=None, actual=None):
    result = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        result["expected"], result["actual"] = expected, actual
    print("@@RESULT " + json.dumps(result), flush=True)


try:
    from solution import double

    for n, want in [(21, 42), (0, 0), (-3, -6)]:
        got = double(n)
        if got != want:
            report("double", False, f"double({n}) returned {got!r}", repr(want), repr(got))
            break
    else:
        report("double", True, "ok")
except Exception as e:
    traceback.print_exc()
    report("double", False, f"solution.py failed: {type(e).__name__}: {e}")
