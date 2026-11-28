"""Hidden checks for the FastAPI course (Lostdesk).

Each task loads its chapter's app from a fresh copy of the chapter folder and calls it in-process with FastAPI's
TestClient: no server, no network, and nothing a task does (a POST, a database file) leaks into the next task.
LABBOX_CHAPTER (set by LabBox) limits the run to one chapter. One @@RESULT line per task; never fails as a whole.
"""
import importlib
import json
import os
import shutil
import sys
import tempfile
import traceback

W = os.environ.get("LABBOX_WORKSPACE", "/check/workspace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = str(expected), str(actual)
    print("@@RESULT " + json.dumps(r), flush=True)


class Fail(Exception):
    def __init__(self, message, expected=None, actual=None):
        super().__init__(message)
        self.message, self.expected, self.actual = message, expected, actual


_added_path = None


def load(folder, module="main"):
    """Copies the chapter folder to a temporary place, changes into it and imports `module` from it, fresh."""
    global _added_path
    src = os.path.join(W, folder)
    if not os.path.isdir(src):
        raise Fail(f"{folder}/ is missing from your workspace.")
    dst = os.path.join(tempfile.mkdtemp(prefix="lostdesk-"), folder)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.db", ".pytest_cache"))
    os.chdir(dst)
    for name in list(sys.modules):
        if name in ("main", "app", "tests", "conftest") or name.startswith(("app.", "tests.", "test_")):
            del sys.modules[name]
    if _added_path in sys.path:
        sys.path.remove(_added_path)
    sys.path.insert(0, dst)
    _added_path = dst
    try:
        return importlib.import_module(module)
    except Exception as e:  # a syntax error, a missing import, ...
        traceback.print_exc()
        where = module.replace(".", "/") + ".py"
        raise Fail(f"{folder}/{where} could not be loaded: {type(e).__name__}: {e}. Run it in the terminal to see the line.")


def client_for(mod):
    from fastapi.testclient import TestClient

    if not hasattr(mod, "app"):
        raise Fail("there is no app in the file. Keep the line app = FastAPI().")
    return TestClient(mod.app)


def body(r):
    try:
        return r.json()
    except ValueError:
        return r.text


def show(v):
    return json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v


def expect(r, status, what):
    """Fails unless the response has this status code (or one of them)."""
    ok = status if isinstance(status, tuple) else (status,)
    if r.status_code not in ok:
        hint = ""
        b = body(r)
        if r.status_code == 404 and 404 not in ok and isinstance(b, dict) and b.get("detail") == "Not Found":
            hint = " That is FastAPI's own 404: no route matches this path and method yet."
        elif r.status_code == 405:
            hint = " 405 means the path exists, but not for this method."
        elif r.status_code == 422 and 422 not in ok:
            hint = f" 422 means FastAPI refused the input: {show(b.get('detail') if isinstance(b, dict) else b)}."
        raise Fail(f"{what} gave status {r.status_code}, but it should be {' or '.join(map(str, ok))}.{hint}",
                   " or ".join(map(str, ok)), f"{r.status_code} {show(body(r))}")


def run(task, fn):
    try:
        message = fn()
        report(task, True, message)
    except Fail as f:
        report(task, False, "Not yet: " + f.message, f.expected, f.actual)
    except Exception as e:
        traceback.print_exc()
        report(task, False, f"Not yet: your code crashed with {type(e).__name__}: {e}. The Output tab shows the line.")


# ---------------------------------------------------------------- Part 1: first steps

def ch1_menu():
    mod = load("01-first-api")
    c = client_for(mod)
    r = c.get("/items")
    expect(r, 200, "GET /items")
    want = {"items": list(mod.FOUND.values())}
    got = body(r)
    if isinstance(got, list):
        raise Fail('GET /items gave back the list itself. Wrap it in a dict under the key "items".', show(want), show(got))
    if got != want:
        raise Fail("GET /items should give back every item in FOUND, in id order, under the key \"items\".", show(want), show(got))
    return "Your first route: a function, a decorator, and FastAPI turned the dict into JSON for you."


def ch1_price():
    mod = load("01-first-api")
    c = client_for(mod)
    r = c.get("/items/3")
    if r.status_code == 404 and isinstance(body(r), dict) and body(r).get("detail") != "Not Found":
        raise Fail("GET /items/3 gave 404 although item 3 exists. Without item_id: int, the id arrives as the text \"3\", "
                   "and FOUND's keys are numbers.", "200", f"404 {show(body(r))}")
    expect(r, 200, "GET /items/3")
    if body(r) != mod.FOUND[3]:
        raise Fail("GET /items/3 should give back item 3 itself.", show(mod.FOUND[3]), show(body(r)))
    r = c.get("/items/99")
    if r.status_code == 200:
        raise Fail("GET /items/99 gave status 200, for an item that does not exist. Raise HTTPException(status_code=404).",
                   "404", f"200 {show(body(r))}")
    expect(r, 404, "GET /items/99")
    r = c.get("/items/umbrella")
    expect(r, 422, "GET /items/umbrella (not a number)")
    return "A path parameter with a type, and a real 404: every program that calls Lostdesk can now tell found from not found."


def ch2_health():
    mod = load("02-http")
    c = client_for(mod)
    r = c.get("/health")
    expect(r, 200, "GET /health")
    want = {"status": "ok", "items": len(mod.FOUND)}
    if body(r) != want:
        raise Fail("GET /health should give back the status and how many items there are.", show(want), show(body(r)))
    mod.FOUND[50] = {"id": 50, "title": "red scarf", "station": "Airport"}
    r = c.get("/health")
    if body(r).get("items") != len(mod.FOUND):
        raise Fail("after one more item was added to FOUND, /health still said the old count. Count FOUND with len(), "
                   "do not write the number.", str(len(mod.FOUND)), show(body(r).get("items")))
    return "A health route: the first thing a load balancer or a monitoring tool asks a real API."


def ch2_stations():
    mod = load("02-http")
    c = client_for(mod)
    r = c.get("/stations")
    expect(r, 200, "GET /stations")
    want = {"stations": sorted({i["station"] for i in mod.FOUND.values()})}
    got = body(r)
    if isinstance(got, dict) and isinstance(got.get("stations"), list) and len(got["stations"]) != len(set(got["stations"])):
        raise Fail("a station appears more than once. Riverside has two items, but it is one station: a set keeps each once.",
                   show(want), show(got))
    if got != want:
        raise Fail("GET /stations should give back each station once, A to Z, under the key \"stations\".", show(want), show(got))
    mod.FOUND[50] = {"id": 50, "title": "red scarf", "station": "Airport"}
    if "Airport" not in body(c.get("/stations")).get("stations", []):
        raise Fail("a new item at Airport did not add Airport to /stations. Work the list out from FOUND each time.")
    return "Stations worked out from the data on every request, each once, sorted: the answer can never go stale."


def ch3_search():
    mod = load("03-path-and-query")
    c = client_for(mod)
    allx = list(mod.FOUND.values())
    cases = [
        ("/items", allx[:10], "with no query parameters, every item"),
        ("/items?q=UMBRELLA", [i for i in allx if "umbrella" in i["title"]], "q=UMBRELLA should match titles in any capitals"),
        ("/items?category=bag", [i for i in allx if i["category"] == "bag"], "category=bag"),
        ("/items?q=umbrella&category=umbrella&limit=1", [allx[0]], "q, category and limit together"),
        ("/items?limit=2", allx[:2], "limit=2 should give at most 2 items"),
    ]
    for path, want, what in cases:
        r = c.get(path)
        expect(r, 200, f"GET {path}")
        if body(r) != {"items": want}:
            raise Fail(f"GET {path}: {what}.", show({"items": want}), show(body(r)))
    return "Query parameters with defaults: one route now answers many questions, and FastAPI converted limit to a number."


def ch3_by_line():
    mod = load("03-path-and-query")
    c = client_for(mod)
    r = c.get("/lines/red/items")
    expect(r, 200, "GET /lines/red/items")
    want = {"line": "red", "items": [i for i in mod.FOUND.values() if i["line"] == "red"]}
    if body(r) != want:
        raise Fail("GET /lines/red/items should give back the line and the items found on it.", show(want), show(body(r)))
    r = c.get("/lines/purple/items")
    if r.status_code == 200:
        raise Fail("GET /lines/purple/items gave 200, but there is no purple line. Give the parameter the type Line, "
                   "and FastAPI refuses other values with 422.", "422", f"200 {show(body(r))}")
    expect(r, 422, "GET /lines/purple/items")
    return "An Enum as a path type: only real lines get in, and the /docs page shows a drop-down of the three."


def ch4_limits():
    mod = load("04-validation")
    c = client_for(mod)
    allx = list(mod.FOUND.values())
    for path in ("/items?limit=0", "/items?limit=21", "/items?offset=-1"):
        r = c.get(path)
        if r.status_code == 200:
            raise Fail(f"GET {path} gave 200. It should be refused with 422 before your function runs: "
                       "limit 1 to 20 (ge, le), offset 0 or more.", "422", f"200 {show(body(r))}")
        expect(r, 422, f"GET {path}")
    for path, want in (("/items?limit=20", allx), ("/items", allx[:10]), ("/items?offset=2&limit=2", allx[2:4]), ("/items?offset=10", [])):
        r = c.get(path)
        expect(r, 200, f"GET {path}")
        if body(r) != {"items": want}:
            raise Fail(f"GET {path} should give back the items from offset on, at most limit of them.", show({"items": want}), show(body(r)))
    return "Limits and offsets with ge and le: the classic way an API pages through a long list, and refuses silly sizes."


def ch4_search_rules():
    mod = load("04-validation")
    c = client_for(mod)
    for path, status in (("/items?q=ab", 422), ("/items?q=" + "x" * 41, 422), ("/items?q=bag", 200), ("/items?q=" + "x" * 40, 200),
                         ("/items/0", 422), ("/items/-3", 422), ("/items/1", 200), ("/items/99", 404)):
        r = c.get(path)
        if r.status_code != status:
            short = path if len(path) < 30 else path[:24] + "..."
            raise Fail(f"GET {short} gave {r.status_code}, but it should give {status}. q is 3 to 40 characters; "
                       "item_id is 1 or more (Path(ge=1)).", str(status), f"{r.status_code} {show(body(r))}"[:200])
    return "Rules in the signature: FastAPI checks them, refuses with a clear 422, and lists them in /docs."


def ch5_found_item():
    mod = load("05-request-body")
    c = client_for(mod)
    new = {"title": "red scarf", "category": "clothing", "line": "blue", "station": "University"}
    r = c.post("/items", json=new)
    expect(r, (200, 201), "POST /items")
    want = {"id": 4, **new}
    if body(r) != want:
        raise Fail("POST /items should give back the stored item with its new id (one more than the biggest so far).",
                   show(want), show(body(r)))
    r = c.get("/items/4")
    if r.status_code != 200 or body(r) != want:
        raise Fail("after POST /items, GET /items/4 did not find the new item. Store it in FOUND under its id.",
                   show(want), f"{r.status_code} {show(body(r))}")
    for bad, why in (({**new, "line": "purple"}, "line purple"), ({k: v for k, v in new.items() if k != "station"}, "no station")):
        r = c.post("/items", json=bad)
        if r.status_code != 422:
            raise Fail(f"POST /items with {why} should be refused with 422. Use FoundItemIn as the parameter's type.",
                       "422", f"{r.status_code} {show(body(r))}")
    return "A Pydantic model as the body: FastAPI read the JSON, checked every field and handed you a ready object."


def ch5_report_lost():
    mod = load("05-request-body")
    c = client_for(mod)
    one = {"title": "grey laptop bag", "line": "red", "station": "Tech Park", "contact": "98200 11111"}
    r = c.post("/reports", json=one)
    expect(r, (200, 201), "POST /reports")
    want = {"id": 1, **one, "details": None}
    if body(r) != want:
        raise Fail("POST /reports should give back what was stored: an id, the report's fields, and details as null "
                   "when it was not sent.", show(want), show(body(r)))
    r = c.post("/reports", json={**one, "details": "has a sticker of a tiger"})
    if body(r).get("id") != 2:
        raise Fail("the second report should get id 2.", "2", show(body(r).get("id")))
    r = c.get("/reports")
    if len(body(r).get("reports", [])) != 2:
        raise Fail("after two POSTs, GET /reports should list two reports. Append each one to REPORTS.",
                   "2 reports", show(body(r)))
    r = c.post("/reports", json={k: v for k, v in one.items() if k != "contact"})
    if r.status_code != 422:
        raise Fail("a report with no contact should be refused with 422: contact is required in LostReport.", "422",
                   f"{r.status_code} {show(body(r))}")
    return "Two kinds of body, two models: required fields are enforced, optional ones get their default."


# ---------------------------------------------------------------- the table

CHAPTERS = {
    "01-menu-api": [("menu", ch1_menu), ("price", ch1_price)],
    "http-basics": [("health", ch2_health), ("stations", ch2_stations)],
    "path-and-query": [("search", ch3_search), ("by_line", ch3_by_line)],
    "validation": [("limits", ch4_limits), ("search_rules", ch4_search_rules)],
    "request-body": [("found_item", ch5_found_item), ("report_lost", ch5_report_lost)],
}


def main():
    only = os.environ.get("LABBOX_CHAPTER")
    for chapter, tasks in CHAPTERS.items():
        if only and only != chapter:
            continue
        for task, fn in tasks:
            run(task, fn)


if __name__ == "__main__":
    main()
