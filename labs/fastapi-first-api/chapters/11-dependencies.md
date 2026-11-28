:::step{type=story title="The same five lines, everywhere"}
Open this chapter's `main.py` and look for repetition. `GET /items` reads `offset` and `limit` with their rules;
`GET /reports` will need exactly the same. `POST /items` checks the desk key by hand; `DELETE /items/{item_id}` needs
the same check, and does not have it. We tried: in the starter, `DELETE /items/1` with no key at all answers `204`,
and the item is gone.

Copying code between routes fails in a familiar way: one copy gets fixed, another is forgotten. FastAPI's answer is a
**dependency**: write the shared piece once, as a function, and let every route that needs it say so.

:::mission
Write `paginate`, a dependency both lists use, and `require_desk`, a dependency that guards `POST /items` and
`DELETE /items/{item_id}` and tells `POST` which desk logged the item.
:::
:::

:::step{type=concept title="A function FastAPI calls for you"}
A dependency is an ordinary function. Its parameters are read from the request exactly like a route's parameters:

```python
def paginate(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> Page:
    return Page(offset=offset, limit=limit)
```

A route asks for its result with `Depends`:

```python
@app.get("/reports")
def list_reports(page: Annotated[Page, Depends(paginate)]):
    return {"reports": REPORTS[page.offset : page.offset + page.limit]}
```

You never call `paginate` yourself. For each request, FastAPI sees `Depends(paginate)`, reads `offset` and `limit`
from the query with all their rules, calls `paginate`, and passes what it gives back as `page`. (`Page` is a small
Pydantic model holding the two numbers together; you write it too.)

Because that `Annotated[...]` is long, it is usual to name it once:

```python
PageDep = Annotated[Page, Depends(paginate)]


@app.get("/items")
def list_items(page: PageDep): ...
```
:::

:::step{type=history title="Where the name comes from"}
The idea is older than FastAPI. Programs had long passed objects the things they need instead of letting them build
those things themselves, and in January 2004 the software writer Martin Fowler gave the pattern its name in an essay,
"Inversion of Control Containers and the Dependency Injection pattern". The thing a piece of code needs is its
**dependency**; handing it over from outside is **injecting** it.

Java's Spring framework made it everyday practice (LabBox's Spring Boot course, chapter 6, shows its version). FastAPI's
`Depends` is a light Python take on the same idea: you declare what a route needs, and the framework provides it.
:::

:::step{type=concept title="A guard that stops the request"}
A dependency can also refuse. `require_desk` reads a header and raises when the key is wrong:

```python
def require_desk(x_desk_key: Annotated[str | None, Header()] = None) -> str:
    if x_desk_key not in DESK_KEYS:
        raise HTTPException(status_code=401, detail="Only staff at a desk can do this")
    return DESK_KEYS[x_desk_key]
```

Press Play to follow a `DELETE` through it:

:::diagram{name="fastapi-dependency"}
Dependencies run before the route; one that raises stops the request, one that returns hands its value to the route.
:::

Some routes need the guard but not its value. `DELETE` only needs to know the key was good, so the dependency goes in
the decorator instead of the parameters:

```python
@app.delete("/items/{item_id}", status_code=204, dependencies=[Depends(require_desk)])
```

`POST /items` does want the value, the desk's station, to record where the item was logged: it takes
`desk: Annotated[str, Depends(require_desk)]` as a parameter.
:::

:::step{type=example title="Worked example: a language dependency"}
This is not in your project. Suppose station screens in several languages call Lostdesk:

```python
def language(accept_language: Annotated[str | None, Header()] = None) -> str:
    if accept_language and accept_language.startswith("hi"):
        return "hi"
    return "en"


LangDep = Annotated[str, Depends(language)]


@app.get("/welcome")
def welcome(lang: LangDep):
    return {"message": "स्वागत है" if lang == "hi" else "Welcome"}
```

1. The dependency reads the standard `Accept-Language` header, which browsers send by themselves.
2. Any route that takes `lang: LangDep` gets `"hi"` or `"en"`, worked out in one place.
3. Changing the rule later (adding Marathi, say) changes one function, and every route follows.
:::

:::step{type=predict title="Guess first"}
:::question
`require_desk` raises `HTTPException(401)`. What happens to `delete_item`?
:::
- [ ] It runs, and the 401 is sent afterwards
- [x] It never runs: the 401 is the answer
- [ ] It runs with `desk` set to None
:::explain
Dependencies run first. A dependency that raises ends the request right there, exactly as if the route had raised.
:::
:::

:::step{type=task task=pagination_dep title="Your turn: paginate" file="11-dependencies/main.py" line="12-13"}
Write `paginate` (and a small model for its result, like `Page`), and use it in both `GET /items` and `GET /reports`:

```text
GET /reports?offset=1&limit=2   ->  {"reports":[{"id":2,"title":"child's water bottle"},{"id":3,"title":"red scarf"}]}
GET /reports?limit=50           ->  422, "Input should be less than or equal to 20"
```

(both captured from the solution). Then open `/docs`: `GET /reports` now lists `offset` and `limit`, with their
minimum, maximum and defaults, though the route itself never mentions them. Press **Check**.
:::

:::step{type=task task=desk_dep title="Your turn: require_desk" file="11-dependencies/main.py" line="16-17"}
Write `require_desk` and use it twice:

- on `DELETE /items/{item_id}`, as a guard: no key or a wrong key gives 401, and the item stays;
- on `POST /items`, as a parameter, so `logged_at` records the desk's station; then remove the hand-written check
  there.

With the Airport desk's key, the solution answered `POST /items` with `201 {"id":7,"title":"red scarf",
"logged_at":"Airport"}`, and without a key, `DELETE /items/1` with `401 {"detail":"Only staff at a desk can do
this"}`. Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Where does a dependency's own parameter, like `limit`, come from?
:::
- [ ] It must be passed by the route
- [x] From the request, read exactly like a route's parameters
- [ ] From a global variable
:::explain
FastAPI treats a dependency's parameters like a route's: query, path, header, body, or even another dependency.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
When does a dependency go in `dependencies=[...]` instead of the parameters?
:::
- [x] When the route needs it to run, but not its value
- [ ] When it raises exceptions
- [ ] When it reads headers
:::explain
A guard whose answer the route does not use goes in the decorator; a dependency whose value the route uses is a
parameter.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Three routes use `PageDep`. You change `le=20` to `le=50` in `paginate`. How many routes change?
:::
- [ ] One
- [x] All three
:::explain
That is the point of a dependency: one definition, used everywhere.
:::
:::

:::step{type=deep-dive title="Go deeper: dependencies of dependencies, classes, and caching"}
**Sub-dependencies.** A dependency can itself use `Depends`. Chapter 17's `get_current_user` depends on the token,
which depends on the `Authorization` header; FastAPI works out the order.

**Classes as dependencies.** `Depends(Paging)` with a class works too: FastAPI calls the class, so its `__init__`
parameters are read from the request, and the route gets the object.

**Once per request.** If two dependencies of one route both depend on `paginate`, FastAPI calls `paginate` only once
for that request and reuses the result. (`Depends(paginate, use_cache=False)` turns that off.)

**For every route.** `FastAPI(dependencies=[Depends(require_api_key)])` applies a guard to the whole app, and
`APIRouter(dependencies=[...])` (chapter 14) to one group of routes.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write a dependency: a plain function whose parameters FastAPI reads from the request.
- Use it with `Annotated[..., Depends(...)]`, and give that a short name like `PageDep`.
- Write a guard that raises before the route runs, and attach it with `dependencies=[...]`.
- Explain dependency injection: the route declares what it needs, and FastAPI provides it.

:::photo{src="/lesson-images/fastapi/fa-11-sketch.webp" alt="Sketchnote: Dependencies. A dependency is a function FastAPI calls for you before the route. It can give the route a value, or stop the request. Flow: the request arrives, FastAPI sees Depends, it reads the dependency's own parameters, the dependency runs, its value reaches the route. Remember: Annotated[T, Depends(f)], often named like PageDep; A dependency that raises stops the route from running; A guard with no value goes in dependencies=[...]; Change the dependency once; every route follows." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 12: a real database, with a dependency that opens and closes a session for every request.
:::
