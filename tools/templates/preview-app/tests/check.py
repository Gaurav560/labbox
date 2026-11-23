"""Hidden checks: call the learner's app in-process with FastAPI's TestClient (no server, no network)."""
import json
import sys
import traceback

sys.path.insert(0, "/check/workspace")
sys.dont_write_bytecode = True

EXPECTED_MENU = {"corn cutlet": 15, "fried idli": 20, "bun maska": 30, "vada pav": 25}


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


try:
    from fastapi.testclient import TestClient

    import main

    client = TestClient(main.app)
except Exception as e:
    traceback.print_exc()
    for t in ("menu", "price"):
        report(t, False, f"main.py could not be loaded: {type(e).__name__}: {e}")
    raise SystemExit(0)


def body(r):
    try:
        return r.json()
    except ValueError:
        return r.text


try:
    r = client.get("/menu")
    want = {"items": sorted(EXPECTED_MENU)}
    if r.status_code == 404:
        report("menu", False, "GET /menu returned 404: there is no /menu route yet.", "200", "404")
    elif r.status_code != 200 or body(r) != want:
        report("menu", False, "GET /menu does not return the items A to Z.", json.dumps(want), f"{r.status_code} {json.dumps(body(r))}")
    else:
        report("menu", True, "ok")
except Exception as e:
    traceback.print_exc()
    report("menu", False, f"GET /menu crashed: {type(e).__name__}: {e}")

try:
    ok = True
    for item, price in [("fried idli", 20), ("vada pav", 25)]:
        r = client.get(f"/menu/{item}")
        want = {"item": item, "price": price}
        if r.status_code != 200 or body(r) != want:
            report("price", False, f"GET /menu/{item} is not right.", json.dumps(want), f"{r.status_code} {json.dumps(body(r))}")
            ok = False
            break
    if ok:
        r = client.get("/menu/pizza")
        if r.status_code != 404:
            report("price", False, "An item that is not on the menu should return 404.", "404", str(r.status_code))
        else:
            report("price", True, "ok")
except Exception as e:
    traceback.print_exc()
    report("price", False, f"GET /menu/<item> crashed: {type(e).__name__}: {e}")
