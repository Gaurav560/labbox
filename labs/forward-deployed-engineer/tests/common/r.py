"""Prints one @@RESULT line per task. Checks never fail the run: every task always gets a result."""
import json
import traceback


def passed(task: str, message: str) -> None:
    print("@@RESULT " + json.dumps({"task": task, "passed": True, "message": message}), flush=True)


def failed(task: str, message: str, expected=None, actual=None) -> None:
    result = {"task": task, "passed": False, "message": "Not yet: " + message}
    if expected is not None:
        result["expected"] = str(expected)
        result["actual"] = str(actual)
    print("@@RESULT " + json.dumps(result), flush=True)


def task(name: str, check) -> None:
    """Runs one task's check; anything unexpected becomes a clear failure for that task only."""
    try:
        check()
    except Exception as e:  # noqa: BLE001
        last = traceback.extract_tb(e.__traceback__)[-1]
        where = f" ({last.filename.rsplit('/', 1)[-1]}, line {last.lineno})" if "/_checks/" not in last.filename else ""
        failed(name, f"the check stopped with {type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}{where}")
