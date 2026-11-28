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
import warnings  # noqa: E402

warnings.filterwarnings("ignore", message="This declarative base already contains")  # each task re-imports its chapter


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
    try:  # SQLModel keeps every table in one shared registry; a fresh import of a chapter must start from an empty one
        from sqlmodel import SQLModel
        SQLModel.metadata.clear()
    except ImportError:
        pass
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
    client = TestClient(mod.app)
    client.__enter__()  # runs the app's lifespan (chapter 12 on: the database tables are created there)
    return client


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



# ---------------------------------------------------------------- Part 2: models and responses

GOOD_ITEM = {"title": "red scarf", "category": "clothing", "location": {"line": "blue", "station": "University"},
             "found_on": "2026-11-27", "tags": ["wool", "long"]}


def ch6_nested_location():
    mod = load("06-models")
    c = client_for(mod)
    if not hasattr(mod, "Location"):
        raise Fail("there is no model called Location yet. Write it as a class with line and station.")
    flat = {k: v for k, v in GOOD_ITEM.items() if k != "location"} | {"line": "blue", "station": "University"}
    r = c.post("/items", json=GOOD_ITEM)
    if r.status_code == 422 and "location" not in r.text and ("line" in r.text or "station" in r.text):
        raise Fail("POST /items with a nested location was refused: FoundItemIn still wants line and station at the top. "
                   "Replace them with location: Location.", "200", f"422 {show(body(r))}"[:300])
    expect(r, (200, 201), "POST /items with a nested location")
    got = body(r)
    if got.get("location") != {"line": "blue", "station": "University"}:
        raise Fail("the stored item should keep the location as a nested object.", show(GOOD_ITEM["location"]), show(got.get("location")))
    r = c.post("/items", json=flat)
    if r.status_code != 422:
        raise Fail("POST /items with line and station at the top level should now be refused with 422: they belong "
                   "inside location.", "422", f"{r.status_code} {show(body(r))}"[:300])
    bad = GOOD_ITEM | {"location": {"line": "blue", "station": "U"}}
    if c.post("/items", json=bad).status_code != 422:
        raise Fail("a station of one letter should be refused: Location's station is 2 to 40 characters (Field).")
    return "A model inside a model: the JSON nests, the checks nest, and /docs shows the shape."


def ch6_item_fields():
    mod = load("06-models")
    c = client_for(mod)
    good = GOOD_ITEM
    fields = getattr(getattr(mod, "FoundItemIn", None), "model_fields", {})
    if "location" not in fields:  # this task can be done before nested_location: send line and station flat
        good = {k: v for k, v in GOOD_ITEM.items() if k != "location"} | {"line": "blue", "station": "University"}
    r = c.post("/items", json=good)
    if r.status_code == 422:
        raise Fail("a good item was refused: " f"{show(body(r).get('detail'))}"[:300], "200", "422")
    expect(r, (200, 201), "POST /items with a good item")
    got = body(r)
    if "found_on" not in got and "tags" not in got:
        raise Fail("the stored item has no found_on and no tags: FoundItemIn does not have those fields yet, and "
                   "Pydantic quietly drops fields a model does not know.", '"found_on" and "tags"', show(got))
    if got.get("found_on") != "2026-11-27" or got.get("tags") != ["wool", "long"]:
        raise Fail("the stored item should keep found_on (a date) and tags (a list).", '"2026-11-27" and ["wool", "long"]',
                   f"{show(got.get('found_on'))} and {show(got.get('tags'))}")
    no_tags = {k: v for k, v in good.items() if k != "tags"}
    r = c.post("/items", json=no_tags)
    expect(r, (200, 201), "POST /items without tags")
    if body(r).get("tags") != []:
        raise Fail("tags should be an empty list when they are not sent: give the field a default.", "[]", show(body(r).get("tags")))
    for bad, why in ((good | {"title": "ab"}, "a title of 2 characters"), (good | {"title": "x" * 61}, "a title of 61 characters"),
                     (good | {"found_on": "yesterday"}, "found_on that is not a date"),
                     (good | {"tags": ["a", "b", "c", "d", "e", "f"]}, "six tags"), ({k: v for k, v in good.items() if k != "found_on"}, "no found_on")):
        r = c.post("/items", json=bad)
        if r.status_code != 422:
            raise Fail(f"POST /items with {why} should be refused with 422. Field(min_length=..., max_length=...) sets the "
                       "rules; found_on: date makes it required and checks it.", "422", f"{r.status_code} {show(body(r))}"[:300])
    return "Field rules, a real date and a list with a limit: the model now refuses what a person would refuse."


def ch7_public_report():
    mod = load("07-responses")
    c = client_for(mod)
    r = c.get("/reports/1")
    expect(r, 200, "GET /reports/1")
    got = body(r)
    if isinstance(got, dict) and "contact" in got:
        raise Fail("GET /reports/1 shows the passenger's phone number to anyone. Declare the return type ReportPublic "
                   "(-> ReportPublic) and FastAPI filters it out.", "no contact", show(got))
    want = {k: v for k, v in mod.REPORTS[1].items() if k != "contact"}
    if got != want:
        raise Fail("GET /reports/1 should give back the report's public fields.", show(want), show(got))
    r = c.get("/reports/99")
    expect(r, 404, "GET /reports/99")
    return "A response model as a filter: the contact stays in your data and never reaches the public."


def ch7_report_list_public():
    mod = load("07-responses")
    c = client_for(mod)
    r = c.get("/reports")
    expect(r, 200, "GET /reports")
    got = body(r)
    if not isinstance(got, list):
        raise Fail("GET /reports should give back a list of reports (-> list[ReportPublic]).", "a list", show(got)[:200])
    if any("contact" in x for x in got if isinstance(x, dict)):
        raise Fail("GET /reports still shows contacts. The return type list[ReportPublic] filters every report.",
                   "no contact", show(got)[:300])
    if len(got) != len(mod.REPORTS):
        raise Fail("GET /reports should list every report.", str(len(mod.REPORTS)), str(len(got)))
    return "A list of response models: every report filtered the same way, and /docs shows exactly what callers get."


def ch8_created_201():
    mod = load("08-errors")
    c = client_for(mod)
    r = c.post("/items", json={"title": "red scarf", "line": "blue", "station": "University"})
    if r.status_code == 200:
        raise Fail("POST /items worked, but answered 200. Something new was created: 201 Created says so. Add "
                   "status_code=status.HTTP_201_CREATED to the decorator.", "201", "200")
    expect(r, 201, "POST /items")
    if body(r).get("id") != 4:
        raise Fail("the new item should come back with its id, 4.", "4", show(body(r).get("id")))
    return "201 Created: the status code itself tells the client that something new now exists."


def ch8_claim_conflict():
    mod = load("08-errors")
    c = client_for(mod)
    r = c.post("/items/1/claim", json={"report_id": 12})
    expect(r, 200, "POST /items/1/claim (an unclaimed item)")
    r = c.post("/items/1/claim", json={"report_id": 13})
    if r.status_code == 200:
        raise Fail("item 1 was claimed twice, by report 12 and then by report 13. A second claim should be refused "
                   "with 409: raise AlreadyClaimed.", "409", f"200 {show(body(r))}")
    if r.status_code == 500:
        raise Fail("raising AlreadyClaimed gave 500: FastAPI does not know that exception yet. Register a handler "
                   "with @app.exception_handler(AlreadyClaimed) that answers 409.", "409", "500")
    expect(r, 409, "a second claim of item 1")
    want = {"detail": "Item 1 is already claimed", "claimed_by_report": 12}
    if body(r) != want:
        raise Fail("the 409 should say which item, and which report already claimed it.", show(want), show(body(r)))
    r = c.post("/items/3/claim", json={"report_id": 1})
    if r.status_code != 409 or body(r).get("claimed_by_report") != 7:
        raise Fail("item 3 was already claimed by report 7 when the app started; claiming it should give 409.",
                   '409 {"claimed_by_report": 7, ...}', f"{r.status_code} {show(body(r))}")
    expect(c.post("/items/99/claim", json={"report_id": 1}), 404, "POST /items/99/claim")
    return "Your own exception and its handler: a clear 409 Conflict that says who got there first."


def ch9_patch_item():
    mod = load("09-updates")
    c = client_for(mod)
    before = dict(mod.FOUND[2])
    r = c.patch("/items/2", json={"shelf": "B-12"})
    expect(r, 200, "PATCH /items/2")
    want = before | {"shelf": "B-12"}
    if body(r) != want:
        lost = [k for k in before if k not in ("shelf",) and body(r).get(k) != before[k]] if isinstance(body(r), dict) else []
        hint = f" These fields changed too: {', '.join(lost)}. Use model_dump(exclude_unset=True)." if lost else ""
        raise Fail("PATCH /items/2 with only a shelf should change only the shelf." + hint, show(want), show(body(r)))
    if c.get("/items/2").json() != want:
        raise Fail("after the PATCH, GET /items/2 should show the new shelf: change the stored item.")
    r = c.patch("/items/2", json={"line": "purple"})
    expect(r, 422, "PATCH /items/2 with line purple")
    expect(c.patch("/items/99", json={"shelf": "x"}), 404, "PATCH /items/99")
    return "A partial update with exclude_unset: only what was sent changes, and the rules still apply."


def ch9_delete_item():
    mod = load("09-updates")
    c = client_for(mod)
    r = c.delete("/items/1")
    if r.status_code == 405:
        raise Fail("DELETE /items/1 gave 405: there is no DELETE route yet.", "204", "405")
    expect(r, 204, "DELETE /items/1")
    if r.content:
        raise Fail("a 204 answer must have no body.", "an empty body", r.text[:100])
    expect(c.get("/items/1"), 404, "GET /items/1 after deleting it")
    expect(c.delete("/items/1"), 404, "a second DELETE /items/1")
    expect(c.get("/items/2"), 200, "GET /items/2 (another item)")
    return "DELETE with 204 No Content, and 404 the second time: the item is really gone."


def _png(size):
    head = b"\x89PNG\r\n\x1a\n"
    return head + b"0" * (size - len(head))


def ch10_upload_photo():
    mod = load("10-files")
    c = client_for(mod)
    r = c.post("/items/1/photo", files={"photo": ("umbrella.png", _png(1000), "image/png")})
    if r.status_code == 404 and isinstance(body(r), dict) and body(r).get("detail") == "Not Found":
        raise Fail("there is no POST /items/{item_id}/photo route yet.", "200", "404")
    expect(r, (200, 201), "POST /items/1/photo with a small PNG")
    want = {"item_id": 1, "filename": "umbrella.png", "saved_as": "photos/1.png", "size": 1000}
    if body(r) != want:
        raise Fail("the answer should say which item, the uploaded name, where it was saved and its size in bytes.",
                   show(want), show(body(r)))
    if not os.path.isfile("photos/1.png") or os.path.getsize("photos/1.png") != 1000:
        raise Fail("photos/1.png was not saved with the uploaded bytes.")
    for files, status, why in (({"photo": ("notes.txt", b"hello", "text/plain")}, 415, "a text file"),
                               ({"photo": ("huge.png", _png(2 * 1024 * 1024 + 1), "image/png")}, 413, "a PNG over 2 MB")):
        r = c.post("/items/1/photo", files=files)
        if r.status_code != status:
            raise Fail(f"uploading {why} should be refused with {status}.", str(status), f"{r.status_code} {show(body(r))}"[:200])
    expect(c.post("/items/99/photo", files={"photo": ("a.png", _png(100), "image/png")}), 404, "a photo for item 99")
    r = c.post("/items/1/photo", files={"picture": ("a.png", _png(100), "image/png")})
    expect(r, 422, "an upload whose field is not called photo")
    return "An UploadFile with its checks: type, size, and a predictable name on disk. Never trust the client's name."


def ch10_desk_header():
    mod = load("10-files")
    c = client_for(mod)
    form = {"title": "red scarf", "station": "University"}
    r = c.post("/items", data=form)
    if r.status_code in (200, 201):
        raise Fail("POST /items without an X-Desk-Key header was accepted. Anyone could log items; answer 401.", "401",
                   str(r.status_code))
    expect(r, 401, "POST /items without X-Desk-Key")
    expect(c.post("/items", data=form, headers={"X-Desk-Key": "guess"}), 401, "POST /items with a wrong key")
    r = c.post("/items", data=form, headers={"X-Desk-Key": mod.DESK_KEY})
    expect(r, (200, 201), "POST /items with the right key")
    if body(r).get("title") != "red scarf":
        raise Fail("with the right key, the item should be logged from the form fields.", "red scarf", show(body(r)))
    return "A header parameter: x_desk_key in Python, X-Desk-Key on the wire. FastAPI translated the underscores."


# ---------------------------------------------------------------- Part 3: structure and data

def ch11_pagination_dep():
    mod = load("11-dependencies")
    c = client_for(mod)
    r = c.get("/reports?offset=1&limit=2")
    expect(r, 200, "GET /reports?offset=1&limit=2")
    want = {"reports": mod.REPORTS[1:3]}
    if body(r) != want:
        raise Fail("GET /reports should page like /items: from offset on, at most limit reports. Use your paginate "
                   "dependency in both routes.", show(want), show(body(r)))
    for path in ("/reports?limit=0", "/reports?limit=21", "/items?limit=0", "/reports?offset=-1"):
        expect(c.get(path), 422, f"GET {path}")
    r = c.get("/items?offset=2&limit=2")
    if body(r) != {"items": list(mod.FOUND.values())[2:4]}:
        raise Fail("GET /items?offset=2&limit=2 should still give items 3 and 4.", "items 3 and 4", show(body(r)))
    if not callable(getattr(mod, "paginate", None)):
        raise Fail("both routes page now, but there is no function called paginate: write the paging once, as a "
                   "dependency, and use it with Depends in both.")
    return "One dependency, two routes: the paging rules live in one place, and /docs lists them on both."


def ch11_desk_dep():
    mod = load("11-dependencies")
    c = client_for(mod)
    r = c.delete("/items/1")
    if r.status_code == 204:
        raise Fail("DELETE /items/1 without a desk key removed the item. Anyone could empty the shelf: add "
                   "dependencies=[Depends(require_desk)] to the DELETE route.", "401", "204")
    expect(r, 401, "DELETE /items/1 without X-Desk-Key")
    key = next(iter(mod.DESK_KEYS))
    expect(c.delete("/items/1", headers={"X-Desk-Key": key}), 204, "DELETE /items/1 with a desk key")
    expect(c.post("/items", json={"title": "red scarf"}), 401, "POST /items without X-Desk-Key")
    r = c.post("/items", json={"title": "red scarf"}, headers={"X-Desk-Key": "airport-desk-2"})
    expect(r, 201, "POST /items with the Airport desk's key")
    if body(r).get("logged_at") != "Airport":
        raise Fail("an item logged with the Airport desk's key should say logged_at Airport: use the station the "
                   "dependency gives back.", "Airport", show(body(r).get("logged_at")))
    if not callable(getattr(mod, "require_desk", None)):
        raise Fail("there is no function called require_desk: write the key check once, as a dependency.")
    return "A dependency that guards and gives back a value: one check for every route that needs a desk."


def ch12_create_found():
    mod = load("12-database")
    c = client_for(mod)
    r = c.post("/items", json={"title": "red scarf", "station": "University"})
    if r.status_code == 405:
        raise Fail("there is no POST /items route yet.", "201", "405")
    expect(r, 201, "POST /items")
    got = body(r)
    if not isinstance(got, dict) or not isinstance(got.get("id"), int):
        raise Fail("POST /items should give back the saved item with the id the database gave it. Call "
                   "session.refresh(db_item) after commit.", '{"id": 1, ...}', show(got))
    want = {"id": got["id"], "title": "red scarf", "station": "University", "status": "held"}
    if got != want:
        raise Fail("POST /items should give back the saved row.", show(want), show(got))
    expect(c.post("/items", json={"title": "ab", "station": "University"}), 422, "POST /items with a title of 2 characters")
    import sqlite3
    if not os.path.exists("lostdesk.db"):
        raise Fail("there is no lostdesk.db file after a POST: the item was not saved to the database.")
    rows = sqlite3.connect("lostdesk.db").execute("select title, station from item").fetchall()
    if ("red scarf", "University") not in rows:
        raise Fail("the item table in lostdesk.db does not have the scarf: add it to the session and commit.",
                   "red scarf", show(rows))
    return "A row in a real database file: it survives a restart, and SQLite chose the id."


def ch12_read_found():
    mod = load("12-database")
    c = client_for(mod)
    with mod.Session(mod.engine) as session:
        row = mod.Item(title="black umbrella", station="Riverside")
        session.add(row)
        session.commit()
        session.refresh(row)
        rid = row.id
    r = c.get(f"/items/{rid}")
    if r.status_code == 404 and isinstance(body(r), dict) and body(r).get("detail") == "Not Found":
        raise Fail("there is no GET /items/{item_id} route yet.", "200", "404")
    expect(r, 200, f"GET /items/{rid}")
    want = {"id": rid, "title": "black umbrella", "station": "Riverside", "status": "held"}
    if body(r) != want:
        raise Fail("GET /items/{id} should give back the row from the database.", show(want), show(body(r)))
    expect(c.get("/items/999999"), 404, "GET /items/999999")
    return "session.get by primary key, and a 404 when the row is not there: the database is now the shelf."


def _seed(mod, items):
    with mod.Session(mod.engine) as session:
        for title, category, station in items:
            session.add(mod.Item(title=title, category=category, station=station))
        session.commit()


SEED = [("black umbrella", "umbrella", "Riverside"), ("silver phone", "phone", "Tech Park"),
        ("green umbrella", "umbrella", "Airport"), ("bunch of keys", "keys", "Riverside")]


def ch13_filter_db():
    mod = load("13-crud")
    c = client_for(mod)
    _seed(mod, SEED)
    for path, want in (("/items?station=Riverside", ["black umbrella", "bunch of keys"]),
                       ("/items?q=umbrella", ["black umbrella", "green umbrella"]),
                       ("/items?q=umbrella&station=Airport", ["green umbrella"]),
                       ("/items", [t for t, _, _ in SEED])):
        r = c.get(path)
        expect(r, 200, f"GET {path}")
        got = [i.get("title") for i in body(r)] if isinstance(body(r), list) else body(r)
        if got != want:
            raise Fail(f"GET {path} should give back {', '.join(want)}. Add .where(...) to the query for each filter "
                       "that was given.", show(want), show(got))
    return "Filters in SQL: the database does the searching, with its indexes, however many rows there are."


def ch13_update_db():
    mod = load("13-crud")
    c = client_for(mod)
    _seed(mod, SEED)
    r = c.patch("/items/2", json={"status": "returned"})
    if r.status_code == 405:
        raise Fail("there is no PATCH /items/{item_id} route yet.", "200", "405")
    expect(r, 200, "PATCH /items/2")
    want = {"id": 2, "title": "silver phone", "category": "phone", "station": "Tech Park", "status": "returned"}
    if body(r) != want:
        raise Fail("PATCH /items/2 with only a status should change only the status.", show(want), show(body(r)))
    r = c.get("/items/2")
    if body(r).get("status") != "returned":
        raise Fail("after the PATCH, GET /items/2 still shows the old status: commit the change.", "returned", show(body(r)))
    expect(c.patch("/items/2", json={"title": "ab"}), 422, "PATCH /items/2 with a title of 2 characters")
    expect(c.patch("/items/999", json={"status": "returned"}), 404, "PATCH /items/999")
    return "sqlmodel_update with exclude_unset, then commit: a partial update that the database keeps."


def ch14_reports_router():
    mod = load("14-bigger-app", "app.main")
    c = client_for(mod)
    try:
        reports = importlib.import_module("app.routers.reports")
    except ModuleNotFoundError:
        raise Fail("there is no app/routers/reports.py yet. Move the report routes there, on an APIRouter.")
    if not hasattr(reports, "router"):
        raise Fail("app/routers/reports.py has no router. Create it with APIRouter(prefix=\"/reports\", tags=[\"reports\"]).")
    paths = {getattr(r, "path", "") for r in reports.router.routes}
    if not any(p.startswith("/reports") for p in paths):
        raise Fail("the reports router has no routes under /reports. Give it the prefix /reports.", "/reports...", show(sorted(paths)))
    spec = c.get("/openapi.json").json()["paths"]
    tags = spec.get("/reports", {}).get("get", {}).get("tags")
    if tags != ["reports"]:
        raise Fail("GET /reports should be tagged reports in /docs, and only once: include the router in main.py and "
                   "remove the old routes there.", '["reports"]', show(tags))
    r = c.post("/reports", json={"title": "grey laptop bag", "station": "Tech Park", "contact": "98200 11111"})
    expect(r, 201, "POST /reports")
    if "contact" in body(r):
        raise Fail("POST /reports shows the contact: keep the return type ReportPublic.")
    expect(c.get(f"/reports/{body(r)['id']}"), 200, "GET /reports/{id}")
    return "A router per subject, included with a prefix and a tag: main.py stays short however much Lostdesk grows."


def ch14_app_metadata():
    mod = load("14-bigger-app", "app.main")
    c = client_for(mod)
    info = c.get("/openapi.json").json()["info"]
    if info.get("title") != "Lostdesk" or info.get("version") != "1.0.0":
        raise Fail("the API's title and version in /docs should be Lostdesk and 1.0.0: pass title= and version= to "
                   "FastAPI(...).", "Lostdesk 1.0.0", f"{info.get('title')} {info.get('version')}")
    if not info.get("summary") and not info.get("description"):
        raise Fail("give the app a one-line summary (summary=...) for the top of /docs.")
    return "Metadata for the people who read /docs: a name, a version, and one line on what Lostdesk is."


def _run_tests(variant):
    """Runs the learner's tests in a copy of 15-testing whose main.py is the planted variant."""
    import subprocess
    src = os.path.join(W, "15-testing")
    dst = os.path.join(tempfile.mkdtemp(prefix=f"lostdesk-tests-{variant}-"), "15-testing")
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.db", ".pytest_cache"))
    shutil.copy(os.path.join(HERE, "testing", variant, "main.py"), os.path.join(dst, "main.py"))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], cwd=dst,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr, dst


def ch15_override_db():
    if not os.path.isdir(os.path.join(W, "15-testing", "tests")):
        raise Fail("15-testing/tests/ is missing from your workspace.")
    code, out, dst = _run_tests("good")
    if code != 0:
        print(out[-3000:])
        last = [l for l in out.splitlines() if l.strip()][-1:] or ["see Output"]
        raise Fail(f"your tests fail on the correct app ({last[0]}). Run python -m pytest -q in 15-testing and read the first failure.")
    code, out, _ = _run_tests("nodb")  # the same app, but its real get_session refuses to work
    if code != 0:
        print(out[-3000:])
        raise Fail("your tests still use the real database, lostdesk.db: we ran them on a copy of the app whose real "
                   "database refuses to work, and they failed. Give the app an in-memory database in a fixture, with "
                   "app.dependency_overrides[get_session], and use that fixture in every test.")
    return "Tests on a throwaway database: fast, repeatable, and the real lostdesk.db never sees a test row."


def ch15_write_tests():
    if not os.path.isdir(os.path.join(W, "15-testing", "tests")):
        raise Fail("15-testing/tests/ is missing from your workspace.")
    code, out, _ = _run_tests("good")
    if code != 0:
        print(out[-3000:])
        raise Fail("your tests fail on the correct app, so one of them expects the wrong answer. Run python -m pytest -q in 15-testing.")
    for variant, what in (("bug201", "POST /items answers 200 instead of 201"),
                          ("bugread", "GET /items/{id} gives back a different status from the one that was created"),
                          ("bugfilter", "GET /items ignores station=")):
        code, out, _ = _run_tests(variant)
        if code == 0:
            raise Fail(f"your tests all pass even when {what}. Add a test that would catch it.")
    return "Your tests caught three planted bugs: a wrong status, a wrong read-back and a filter that does nothing."


# ---------------------------------------------------------------- Part 4: production

def ch16_hash_passwords():
    mod = load("16-security")
    h = mod.hash_password("riverside-umbrella-42")
    if h == "riverside-umbrella-42":
        raise Fail("hash_password gives back the password itself. Anyone who reads STAFF would know every password: "
                   "use password_hash.hash(password).", "a hash starting $argon2", h)
    if not h.startswith("$argon2"):
        raise Fail("hash_password should use password_hash (pwdlib with argon2).", "$argon2...", h[:30])
    if mod.hash_password("riverside-umbrella-42") == h:
        raise Fail("two hashes of the same password are the same: a good hash adds a random salt each time.")
    if not mod.verify_password("riverside-umbrella-42", h) or mod.verify_password("riverside-umbrella-43", h):
        raise Fail("verify_password should be True for the right password and False for any other: use password_hash.verify.")
    if any(u["hashed_password"].startswith("$argon2") is False for u in mod.STAFF.values()):
        raise Fail("STAFF still stores a password that is not a hash.")
    if mod.authenticate("meera", "riverside-umbrella-42") is None:
        raise Fail("authenticate(\"meera\", her right password) gave None; it should give back her staff record.")
    if mod.authenticate("meera", "wrong") is not None or mod.authenticate("nobody", "x") is not None:
        raise Fail("authenticate should give None for a wrong password and for an unknown username.")
    return "Argon2 hashes with a fresh salt each time: even you cannot read the passwords you store."


def ch16_login_token():
    mod = load("16-security")
    c = client_for(mod)
    r = c.post("/token", data={"username": "meera", "password": "riverside-umbrella-42"})
    if r.status_code in (404, 405):
        raise Fail("there is no POST /token route yet.", "200", str(r.status_code))
    if r.status_code == 401:
        raise Fail("the right password was refused. Finish hash_passwords first: authenticate must accept Meera.", "200", "401")
    expect(r, 200, "POST /token with Meera's password")
    got = body(r)
    if not isinstance(got, dict) or got.get("token_type") != "bearer" or not got.get("access_token"):
        raise Fail("the answer should be a Token: access_token and token_type \"bearer\".", '{"access_token": "...", "token_type": "bearer"}', show(got))
    import jwt
    try:
        claims = jwt.decode(got["access_token"], mod.SECRET_KEY, algorithms=[mod.ALGORITHM])
    except Exception as e:
        raise Fail(f"the access token could not be decoded with SECRET_KEY: {e}. Make it with create_access_token.")
    if claims.get("sub") != "meera" or "exp" not in claims:
        raise Fail("the token should name the user in sub and have an exp (expiry).", '{"sub": "meera", "exp": ...}', show(claims))
    for form in ({"username": "meera", "password": "wrong"}, {"username": "nobody", "password": "x"}):
        r = c.post("/token", data=form)
        if r.status_code != 401:
            raise Fail("a wrong username or password should give 401.", "401", f"{r.status_code} {show(body(r))}")
        if r.headers.get("www-authenticate") != "Bearer":
            raise Fail("the 401 should carry the header WWW-Authenticate: Bearer.", "Bearer", str(r.headers.get("www-authenticate")))
    return "A login that gives a signed, expiring token: the server never has to remember who is signed in."


def _token(mod, user, minutes=None):
    return mod.create_access_token(user) if minutes is None else mod.create_access_token(user, minutes)


def ch17_current_user():
    mod = load("17-current-user")
    c = client_for(mod)
    r = c.get("/me", headers={"Authorization": f"Bearer {_token(mod, 'arjun')}"})
    expect(r, 200, "GET /me with Arjun's token")
    want = {"username": "arjun", "full_name": "Arjun Rao", "desk": "Airport", "role": "supervisor"}
    if body(r) != want:
        raise Fail("GET /me should give back the user the token names, without the password hash.", show(want), show(body(r)))
    import jwt
    forged = jwt.encode({"sub": "arjun"}, "someone-elses-secret", algorithm="HS256")
    for token, why in ((forged, "a token signed with another secret"), (_token(mod, "arjun", -5), "a token that expired"),
                       (_token(mod, "ghost"), "a token for a user who does not exist"), ("not-a-token", "a broken token")):
        r = c.get("/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 401:
            raise Fail(f"GET /me with {why} gave {r.status_code}; it should be 401. Decode the token with jwt.decode and "
                       "refuse it when that fails.", "401", f"{r.status_code} {show(body(r))}")
        if r.headers.get("www-authenticate") != "Bearer":
            raise Fail("the 401 should carry the header WWW-Authenticate: Bearer.")
    expect(c.get("/me"), 401, "GET /me with no token")
    return "The token checked on every request: a forged, expired or broken token gets nowhere."


def ch17_supervisor_only():
    mod = load("17-current-user")
    c = client_for(mod)
    r = c.delete("/items/1", headers={"Authorization": f"Bearer {_token(mod, 'meera')}"})
    if r.status_code == 204:
        raise Fail("Meera, a clerk, deleted item 1. Only a supervisor may: answer 403.", "403", "204")
    expect(r, 403, "DELETE /items/1 by a clerk")
    expect(c.delete("/items/1"), 401, "DELETE /items/1 with no token")
    expect(c.delete("/items/1", headers={"Authorization": f"Bearer {_token(mod, 'arjun')}"}), 204, "DELETE /items/1 by a supervisor")
    return "401 for who are you, 403 for you may not: authentication and authorisation, kept apart."


def ch18_notify_background():
    mod = load("18-background")
    c = client_for(mod)
    route = next((r for r in mod.app.routes if getattr(r, "path", "") == "/items/{item_id}/match/{report_id}"), None)
    if route is None:
        raise Fail("the route POST /items/{item_id}/match/{report_id} is missing.")
    if not getattr(route.dependant, "background_tasks_param_name", None):
        raise Fail("match still sends the text message before answering: the passenger waits 1.5 seconds. Take a "
                   "BackgroundTasks parameter and add send_text_message to it.")
    r = c.post("/items/1/match/1")
    expect(r, 200, "POST /items/1/match/1")
    if not os.path.exists("outbox.log") or "98200 11111" not in open("outbox.log").read():
        raise Fail("after the answer, outbox.log should hold the message to the passenger: add_task(send_text_message, "
                   "contact, message).")
    expect(c.post("/items/1/match/9"), 404, "POST /items/1/match/9")
    return "The answer goes out at once; the slow text message follows in the background."


def ch18_parallel_search():
    import time as _t
    mod = load("18-background")
    c = client_for(mod)
    start = _t.perf_counter()
    r = c.get("/search", params={"q": "laptop"})
    took = _t.perf_counter() - start
    expect(r, 200, "GET /search?q=laptop")
    want = {"reports": ["grey laptop bag"], "logs": ["grey laptop bag seen at Tech Park"]}
    if body(r) != want:
        raise Fail("GET /search should give back both searches' results.", show(want), show(body(r)))
    if took > 0.65:
        raise Fail(f"GET /search took {took:.2f} s: the two searches still run one after the other. "
                   "asyncio.gather runs them at the same time.", "about 0.4 s", f"{took:.2f} s")
    return f"Two waits at once with asyncio.gather: {took:.2f} s instead of about 0.8."


def ch19_timing_header():
    mod = load("19-settings")
    c = client_for(mod)
    for path in ("/items", "/info", "/no-such-page"):
        r = c.get(path)
        v = r.headers.get("x-process-time")
        if not v:
            raise Fail(f"GET {path} has no X-Process-Time header. A middleware (@app.middleware(\"http\")) can add it to "
                       "every response, even a 404.", "X-Process-Time: ... ms", "none")
        if "ms" not in v or not any(ch.isdigit() for ch in v):
            raise Fail("X-Process-Time should be a number of milliseconds, like 0.42 ms.", "0.42 ms", v)
    return "One middleware, every response timed: the first thing to look at when an API feels slow."


def ch19_settings_env():
    os.environ["LOSTDESK_APP_NAME"] = "Lostdesk Airport"
    os.environ["LOSTDESK_MAX_PHOTO_MB"] = "5"
    try:
        mod = load("19-settings")
        c = client_for(mod)
        r = c.get("/info")
        want = {"app_name": "Lostdesk Airport", "max_photo_mb": 5}
        if body(r) != want:
            raise Fail("with LOSTDESK_APP_NAME and LOSTDESK_MAX_PHOTO_MB set, /info should show those values. Read them "
                       "with a BaseSettings class whose env_prefix is LOSTDESK_.", show(want), show(body(r)))
        if not hasattr(mod, "settings"):
            raise Fail("there is no settings object: create it with settings = Settings().")
        if c.get("/openapi.json").json()["info"]["title"] != "Lostdesk Airport":
            raise Fail("the app's title should come from settings.app_name too.")
    finally:
        del os.environ["LOSTDESK_APP_NAME"], os.environ["LOSTDESK_MAX_PHOTO_MB"]
    mod = load("19-settings")
    if body(client_for(mod).get("/info")) != {"app_name": "Lostdesk", "max_photo_mb": 2}:
        raise Fail("without the environment variables, the defaults should apply: Lostdesk and 2.")
    return "Settings from the environment, checked by Pydantic: the same code runs on a laptop and in production."


def _events(c, path, headers=None):
    with c.stream("GET", path, headers=headers or {}) as r:
        if r.status_code == 404:
            raise Fail("there is no GET /items/feed route yet: that is the task sse_feed.", "200", "404")
        if r.status_code != 200:
            raise Fail(f"GET {path} gave {r.status_code}.", "200", str(r.status_code))
        ctype = r.headers.get("content-type", "")
        text = "".join(r.iter_text())
    if not ctype.startswith("text/event-stream"):
        raise Fail(f"GET {path} should be a Server-Sent Events stream (content-type text/event-stream); it is {ctype}. "
                   "Use response_class=EventSourceResponse and yield the items.", "text/event-stream", ctype)
    events = []
    for block in text.strip().split("\n\n"):
        ev = {}
        for line in block.splitlines():
            if ":" in line and not line.startswith(":"):
                k, v = line.split(":", 1)
                ev[k.strip()] = v.strip()
        if "data" in ev:
            events.append(ev)
    return events


def ch20_sse_feed():
    mod = load("20-live")
    c = client_for(mod)
    if not any(getattr(r, "path", "") == "/items/feed" for r in mod.app.routes):
        raise Fail("there is no GET /items/feed route yet.")
    evs = _events(c, "/items/feed")
    got = [json.loads(e["data"]).get("id") for e in evs]
    if got != [1, 2, 3]:
        raise Fail("GET /items/feed should send one event per item, its data the item as JSON.", "[1, 2, 3]", show(got))
    evs = _events(c, "/items/feed?since=2")
    if [json.loads(e["data"]).get("id") for e in evs] != [3]:
        raise Fail("GET /items/feed?since=2 should send only the items after id 2.", "[3]", show([e["data"] for e in evs]))
    c.post("/items", json={"title": "red scarf", "station": "University"})
    if [json.loads(e["data"]).get("title") for e in _events(c, "/items/feed?since=3")] != ["red scarf"]:
        raise Fail("a newly logged item should appear in the feed.")
    return "A Server-Sent Events stream: text/event-stream, one data line per item, readable by any browser."


def ch20_sse_resume():
    mod = load("20-live")
    c = client_for(mod)
    evs = _events(c, "/items/feed")
    if not evs or evs[0].get("event") != "found" or evs[0].get("id") != "1":
        raise Fail("each event should be named found and carry the item's id: ServerSentEvent(data=..., event=\"found\", id=...).",
                   "event: found, id: 1", show(evs[:1]))
    evs = _events(c, "/items/feed", headers={"Last-Event-ID": "2"})
    if [e.get("id") for e in evs] != ["3"]:
        raise Fail("with the header Last-Event-ID: 2 and no since, the feed should start after item 2, as a browser "
                   "expects when it reconnects.", '["3"]', show([e.get("id") for e in evs]))
    return "Named events with ids: a screen that loses its connection picks up exactly where it left off."


DESK = {"X-Desk-Key": "riverside-desk-7"}


def _capstone():
    mod = load("21-capstone")
    c = client_for(mod)
    item = body(c.post("/items", json={"title": "grey laptop bag", "station": "Tech Park"}, headers=DESK))
    report = body(c.post("/reports", json={"title": "grey laptop bag", "contact": "98200 11111"}, headers=DESK))
    return mod, c, item, report


def ch21_claim_flow():
    mod, c, item, report = _capstone()
    r = c.post("/claims", json={"item_id": item["id"], "report_id": report["id"]}, headers=DESK)
    if r.status_code in (404, 405) and isinstance(body(r), dict) and body(r).get("detail") in ("Not Found", "Method Not Allowed"):
        raise Fail("there is no POST /claims route yet.", "201", str(r.status_code))
    expect(r, 201, "POST /claims")
    claim = body(r)
    if claim.get("item_id") != item["id"] or claim.get("report_id") != report["id"] or not isinstance(claim.get("id"), int):
        raise Fail("POST /claims should give back the saved claim with its id.", "a claim with id, item_id, report_id", show(claim))
    with mod.Session(mod.engine) as s:
        it, rp = s.get(mod.Item, item["id"]), s.get(mod.Report, report["id"])
        if (it.status, rp.status) != ("claimed", "matched"):
            raise Fail("after a claim the item should be claimed and the report matched, saved in the database.",
                       "claimed, matched", f"{it.status}, {rp.status}")
    r = c.post("/claims", json={"item_id": item["id"], "report_id": report["id"]}, headers=DESK)
    expect(r, 409, "a second claim on the same item")
    expect(c.post("/claims", json={"item_id": 999, "report_id": report["id"]}, headers=DESK), 404, "a claim on item 999")
    expect(c.post("/claims", json={"item_id": item["id"], "report_id": report["id"]}), 401, "a claim without the desk key")
    return "A claim that changes three rows in one commit, and refuses double claims with 409."


def ch21_collect_item():
    mod, c, item, report = _capstone()
    r = c.post("/claims", json={"item_id": item["id"], "report_id": report["id"]}, headers=DESK)
    if r.status_code != 201:
        raise Fail("POST /claims does not work yet: finish claim_flow first.")
    cid = body(r)["id"]
    r = c.post(f"/claims/{cid}/collect", headers=DESK)
    if r.status_code in (404, 405) and body(r).get("detail") in ("Not Found", "Method Not Allowed"):
        raise Fail("there is no POST /claims/{claim_id}/collect route yet.", "200", str(r.status_code))
    expect(r, 200, f"POST /claims/{cid}/collect")
    from datetime import date as _d
    if body(r).get("collected_on") != _d.today().isoformat():
        raise Fail("collected_on should be today's date.", _d.today().isoformat(), show(body(r).get("collected_on")))
    with mod.Session(mod.engine) as s:
        if s.get(mod.Item, item["id"]).status != "returned":
            raise Fail("after collecting, the item's status should be returned, saved in the database.")
    expect(c.post(f"/claims/{cid}/collect", headers=DESK), 409, "collecting the same claim twice")
    expect(c.post("/claims/999/collect", headers=DESK), 404, "collecting claim 999")
    return "The umbrella went home: Lostdesk followed it from the shelf to its owner. Course complete."

# ---------------------------------------------------------------- the table

CHAPTERS = {
    "01-menu-api": [("menu", ch1_menu), ("price", ch1_price)],
    "http-basics": [("health", ch2_health), ("stations", ch2_stations)],
    "path-and-query": [("search", ch3_search), ("by_line", ch3_by_line)],
    "validation": [("limits", ch4_limits), ("search_rules", ch4_search_rules)],
    "request-body": [("found_item", ch5_found_item), ("report_lost", ch5_report_lost)],
    "fields-and-nested": [("item_fields", ch6_item_fields), ("nested_location", ch6_nested_location)],
    "response-models": [("public_report", ch7_public_report), ("report_list_public", ch7_report_list_public)],
    "status-and-errors": [("created_201", ch8_created_201), ("claim_conflict", ch8_claim_conflict)],
    "updates": [("patch_item", ch9_patch_item), ("delete_item", ch9_delete_item)],
    "forms-and-files": [("desk_header", ch10_desk_header), ("upload_photo", ch10_upload_photo)],
    "dependencies": [("pagination_dep", ch11_pagination_dep), ("desk_dep", ch11_desk_dep)],
    "databases": [("create_found", ch12_create_found), ("read_found", ch12_read_found)],
    "crud": [("filter_db", ch13_filter_db), ("update_db", ch13_update_db)],
    "bigger-apps": [("reports_router", ch14_reports_router), ("app_metadata", ch14_app_metadata)],
    "testing": [("override_db", ch15_override_db), ("write_tests", ch15_write_tests)],
    "security": [("hash_passwords", ch16_hash_passwords), ("login_token", ch16_login_token)],
    "current-user": [("current_user", ch17_current_user), ("supervisor_only", ch17_supervisor_only)],
    "async-and-background": [("notify_background", ch18_notify_background), ("parallel_search", ch18_parallel_search)],
    "middleware-and-settings": [("timing_header", ch19_timing_header), ("settings_env", ch19_settings_env)],
    "live-updates": [("sse_feed", ch20_sse_feed), ("sse_resume", ch20_sse_resume)],
    "capstone": [("claim_flow", ch21_claim_flow), ("collect_item", ch21_collect_item)],
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
