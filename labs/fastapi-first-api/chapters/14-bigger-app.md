:::step{type=story title="When one file is not enough"}
Chapter 13's `main.py` is about a hundred lines, and it only knows about items. Add reports, claims, users, photos
and live updates, and it would pass a thousand. Two people changing it at once would trip over each other, and
finding the route you want would mean scrolling for a long time.

Every real FastAPI service is split up the same way: one file for the models, one for the database, and a **router**
for each subject, with a short `main.py` that puts the pieces together. FastAPI's docs call it "Bigger Applications".
Today Lostdesk becomes a package.

:::mission
Move the report routes into their own router file with the prefix `/reports` and the tag `reports`, and give the API
a name, a version and a one-line summary.
:::
:::

:::step{type=concept title="The new shape of Lostdesk"}
This chapter's folder holds a **package** called `app`, a folder of Python files with an `__init__.py` in it (an
empty file that marks the folder as a package):

```text
14-bigger-app/
  app/
    __init__.py
    main.py          the app: creates FastAPI, includes the routers
    database.py      the engine, get_session, SessionDep
    models.py        every model: Item..., Report...
    routers/
      __init__.py
      items.py       every route about found items
```

Each file has one job, and its first line says which. Files import from each other with **relative imports**: in
`routers/items.py`, `from ..database import SessionDep` means "from the `database` module one level up". The two
dots climb from `routers` to `app`.

Starting it changes slightly: tell `fastapi dev` where the app is.

```bash run
cd /workspace/14-bigger-app && fastapi dev app/main.py --host 0.0.0.0 --port 8000 --root-path /preview/fastapi-first-api/8000
```

The banner says `Using import string: app.main:app`: the module `app.main`, the variable `app`.
:::

:::step{type=concept title="A router is a small app" file="14-bigger-app/app/routers/items.py" line="1-30"}
Open `app/routers/items.py`:

```python
router = APIRouter(prefix="/items", tags=["items"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: SessionDep) -> ItemPublic:
    ...


@router.get("/{item_id}")
def read_item(item_id: int, session: SessionDep) -> ItemPublic:
    ...
```

An **`APIRouter`** works exactly like `app`: the same decorators, the same parameters, dependencies and response
models. Two arguments save repetition:

- `prefix="/items"` goes in front of every path in the file, so `"/{item_id}"` becomes `/items/{item_id}`, and `""`
  becomes `/items` itself.
- `tags=["items"]` groups the routes under an "items" heading in `/docs`.

On its own a router does nothing. `main.py` includes it:

```python
app.include_router(items.router)
```

That one line adds all of the router's routes to the app, with their prefix and tags.
:::

:::step{type=example title="Worked example: a stations router"}
This is not in your project. A third subject, stations, would get its own file, `app/routers/stations.py`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/stations", tags=["stations"])

STATIONS = ["Airport", "Old Market", "Riverside", "Tech Park", "University"]


@router.get("")
def list_stations():
    return {"stations": STATIONS}
```

and two changes in `main.py`: `from .routers import items, reports, stations`, then
`app.include_router(stations.router)`. Nothing else in the app has to change.
:::

:::step{type=predict title="Guess first"}
:::question
A router has `prefix="/reports"`, and a route `@router.get("/{report_id}")`. Which path does it answer?
:::
- [ ] `/{report_id}`
- [x] `/reports/{report_id}`
- [ ] `/reports`
:::explain
The prefix goes in front of every path in the router.
:::
:::

:::step{type=task task=reports_router title="Your turn: a reports router" file="14-bigger-app/app/main.py" line="29-30"}
The three report routes still live in `app/main.py`. Move them:

1. create `app/routers/reports.py` with `router = APIRouter(prefix=..., tags=[...])`, prefix `/reports` and tag
   `reports`, and the three routes on `router` (paths `""` and `"/{report_id}"`);
2. in `main.py`, import it next to `items` and include it;
3. delete the old report routes and their imports from `main.py`.

`items.py` is the model to copy. Afterwards `/docs` shows a **reports** section, and `POST /reports` still answers
201 without the contact. Then press **Check**.

The usual slip, tried: steps 1 and 2 without step 3. Both copies of each route exist (the app held two routes for
`/reports`), the old ones without a tag win in `/docs`, and the server prints `UserWarning: Duplicate Operation ID
read_report_reports__report_id__get` when the docs are built. The check looks at the tags and asks you to remove the
old routes.
:::

:::step{type=concept title="The API's name tag" file="14-bigger-app/app/main.py" line="18-19"}
The top of `/docs` still says **FastAPI** and **0.1.0**: the defaults. The `FastAPI(...)` call takes the API's own
details:

```python
app = FastAPI(
    title="Lostdesk",
    version="1.0.0",
    summary="The lost-property API of a city metro.",
    lifespan=lifespan,
)
```

They go into `/openapi.json`, where tools and people read them. From the solution:

```text
{'title': 'Lostdesk', 'summary': 'The lost-property API of a city metro.', 'version': '1.0.0'}
```

The `version` is **your** API's version, not FastAPI's. Teams raise it when the API changes, so the people who call it
know what to expect.
:::

:::step{type=task task=app_metadata title="Your turn: a name and a version" file="14-bigger-app/app/main.py" line="18-19"}
Give the app the title `Lostdesk`, the version `1.0.0` and a one-line `summary`. Keep `lifespan=lifespan`. Reload
`/docs`, then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `from ..database import SessionDep` mean inside `app/routers/items.py`?
:::
- [ ] Import from a module called `..database`
- [x] Import from the `database` module one package up, in `app`
- [ ] Import from the folder above `14-bigger-app`
:::explain
One dot is the current package (`routers`); two dots go one level up (`app`).
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
You create a router file but forget `app.include_router(...)`. What happens to its routes?
:::
- [ ] They work anyway
- [x] They do not exist: every path gives 404
- [ ] The server refuses to start
:::explain
A router is only a collection of routes until the app includes it.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `tags=["reports"]` change?
:::
- [ ] The paths
- [x] How /docs groups the routes
- [ ] Who may call them
:::explain
Tags are for documentation: they group routes under headings in `/docs` and in `/openapi.json`.
:::
:::

:::step{type=deep-dive title="Go deeper: router dependencies, and circular imports"}
**Dependencies for a whole router.** `APIRouter(prefix="/admin", dependencies=[Depends(require_desk)])` guards every
route in the file with one line: chapter 11's guard, applied to a group.

**Circular imports.** If `models.py` imported from `routers/items.py` while `items.py` imported from `models.py`,
Python would stop with an `ImportError` about a partially initialised module. The layout of this chapter avoids it by
pointing every arrow one way: routers import models and the database; `main.py` imports routers; nothing imports
`main.py`.

**Where to stop.** A package like this comfortably holds dozens of routers. Beyond that, teams split by service
rather than by file, and that is an architecture question, not a FastAPI one.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Lay out a FastAPI service as a package: `main.py`, `database.py`, `models.py` and a `routers` folder.
- Write an `APIRouter` with a `prefix` and `tags`, and include it with `app.include_router(...)`.
- Use relative imports like `from ..database import SessionDep`, and start the app with `fastapi dev app/main.py`.
- Give the API a title, version and summary for `/docs` and `/openapi.json`.

:::photo{src="/lesson-images/fastapi/fa-14-sketch.webp" alt="Sketchnote: Bigger applications. A bigger service is a package: models, database and one router per subject, joined together in a short main.py. Flow: APIRouter(prefix, tags), routes on the router, main.py imports it, app.include_router(...), /docs groups by tag. Remember: The prefix goes in front of every path in the router; Two dots in an import climb one package up; A router does nothing until the app includes it; title and version describe your API, not FastAPI." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 15: tests that prove Lostdesk works, run against a throwaway database.
:::
