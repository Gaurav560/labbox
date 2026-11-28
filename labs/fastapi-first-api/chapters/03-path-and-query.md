:::step{type=story title="One route, many questions"}
Lostdesk now holds six found items, and passengers ask about them in many ways. "Any umbrellas?" "Anything from the
red line?" "Just show me the first two." Writing a separate route for every question would never end: there are
endless words a passenger might type.

The web has had an answer since its early days: put the question **in the address**. `/items?q=umbrella` asks for
items matching "umbrella"; `/lines/red/items` asks for the red line's items. Today Lostdesk learns to read both
kinds of address, and FastAPI does the converting and the checking for you.

:::mission
Teach `GET /items` to search by words, category and a limit, and add `GET /lines/{line}/items`, which accepts only
the metro's three real lines.
:::
:::

:::step{type=concept title="Two places a value can travel"}
A URL can carry values in two places. Take this one apart:

```text
/lines/red/items?q=umbrella&limit=2
```

| Part | Example | Called | In FastAPI |
|---|---|---|---|
| a piece of the path | `red` in `/lines/red/items` | **path parameter** | written `{line}` in the decorator's path |
| after the `?`, as `name=value` pairs joined by `&` | `q=umbrella`, `limit=2` | **query parameters** (the "query string") | any function parameter **not** in the path |

The rule of thumb that most APIs follow: the **path names a thing** (`/items/3`, `/lines/red`), and the **query
string narrows, sorts or pages** a list of things (`?q=`, `?limit=`). A path parameter is required, because without
it the address points elsewhere; query parameters are usually optional.
:::

:::step{type=try title="A question the route ignores" file="03-path-and-query/main.py" line="27-31"}
Start this chapter's Lostdesk, and ask the starter's `/items` to search:

```bash run
cd /workspace/03-path-and-query && fastapi dev main.py --host 0.0.0.0 --port 8000 --root-path /preview/fastapi-first-api/8000
```

In a second terminal:

```bash run
curl -s "localhost:8000/items?q=umbrella"
```

All **6** items come back (we counted), umbrellas and phones and keys alike. No error, no warning: FastAPI quietly
ignores query parameters your function does not declare. Asking is not enough; the route must say which parameters
it takes. (The quotes around the URL matter: without them, the terminal would treat `&` as "run in the background".)
:::

:::step{type=concept title="Declaring query parameters" file="03-path-and-query/main.py" line="27-31"}
Any function parameter that is not in the path is a query parameter. Its type hint and default decide everything:

```python
@app.get("/items")
def list_items(q: str | None = None, limit: int = 10):
    ...
```

- `q: str | None = None`: "text, or nothing". `str | None` means either a string or `None`, and the default `None`
  makes it **optional**: `/items` with no `q` calls the function with `q=None`.
- `limit: int = 10`: optional too, with the default 10. A query string is text, so FastAPI converts `"2"` into the
  number `2`. Something that is not a number is refused:

```text
{"detail":[{"type":"int_parsing","loc":["query","limit"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"abc"}]}
```

That was `/items?limit=abc`. Note `"loc":["query","limit"]`: the same error as chapter 1's, but this time FastAPI
says the bad value was in the **query**.

- A parameter **without** a default, like `q: str`, would be **required**: leaving it out gives a 422 saying
  `"Field required"`.
:::

:::step{type=example title="Worked example: filters, one after another"}
This is not in your project. Suppose Lostdesk let passengers filter by station:

```python
@app.get("/finds")
def finds(station: str | None = None, limit: int = 10):
    items = list(FOUND.values())
    if station:
        items = [item for item in items if item["station"] == station]
    return {"items": items[:limit]}
```

1. Start with every item.
2. Each filter that was **given** narrows the list; `if station:` skips the filter when `station` is `None`.
3. The limit comes last: `items[:limit]` keeps at most `limit` items, and a shorter list is simply kept whole.

`/finds?station=Riverside` gives the umbrella and the keys; `/finds?station=Riverside&limit=1` only the umbrella.
:::

:::step{type=predict title="Guess first"}
:::question
After your search task, what does `/items?q=UMBRELLA` give, if you compare with `q in item["title"]`?
:::
- [ ] Both umbrellas
- [x] No items at all
- [ ] A 422 error
:::explain
`"UMBRELLA" in "black umbrella"` is `False`: capitals and small letters are different characters. We tried it: the
answer was `{"items":[]}`. Lower-case both sides before comparing, `q.lower() in item["title"].lower()`, and capitals
stop mattering.
:::
:::

:::step{type=task task=search title="Your turn: search the found items" file="03-path-and-query/main.py" line="29-30"}
Give `GET /items` three optional query parameters:

- `q`: a part of the title, in any capitals: `/items?q=UMBRELLA` gives items 1 and 6;
- `category`: `/items?category=bag` gives item 2;
- `limit`: at most this many items, 10 when not given: `/items?limit=2` gives items 1 and 2.

They combine: `/items?q=umbrella&category=umbrella&limit=1` gives only item 1.

```bash run
curl -s "localhost:8000/items?q=UMBRELLA&limit=1"
```

Then press **Check**, and look at `/docs`: the three parameters are listed, each with its type.
:::

:::step{type=concept title="Only real lines: an Enum" file="03-path-and-query/main.py" line="9-14"}
The metro has three lines, red, blue and green. A path like `/lines/purple/items` should not give an empty list, as
if purple were a line with nothing found; it should say "there is no such line".

`main.py` already has the tool, an **Enum** (enumeration): a class that lists the only allowed values.

```python
class Line(str, Enum):
    red = "red"
    blue = "blue"
    green = "green"
```

Use it as a parameter's type, `line: Line`, and FastAPI accepts only those three. We tried purple:

```text
{"detail":[{"type":"enum","loc":["path","line"],"msg":"Input should be 'red', 'blue' or 'green'","input":"purple","ctx":{"expected":"'red', 'blue' or 'green'"}}]}
```

The `str` in `class Line(str, Enum)` makes each member a string too, so `Line.red == "red"` is `True` (tried). One
trap: in Python 3.12 an f-string shows the member, not the text, so `f"{line}"` gives `Line.red`. When you need the
plain text, use `line.value`, which is `"red"`. In `/docs`, an Enum parameter becomes a drop-down of the three lines.
:::

:::step{type=task task=by_line title="Your turn: one line's items" file="03-path-and-query/main.py" line="41-42"}
Add `GET /lines/{line}/items`, with the parameter typed as `Line`. It gives back the line and its items:

```json
{"line": "red", "items": [item 1, item 3]}
```

`/lines/purple/items` must give 422, which the type does for you.

```bash run
curl -s localhost:8000/lines/red/items
```

Then press **Check**.

The usual slip, tried: `line: str`. Everything seems to work, but `/lines/purple/items` gives
`{"line":"purple","items":[]}` with status 200, and a phone app would show "no items on the purple line" for a line
that does not exist. The check tries purple.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In `/stations/Riverside/items?limit=3`, which values are query parameters?
:::
- [ ] `Riverside`
- [x] `limit`
- [ ] Both
:::explain
`Riverside` is a piece of the path; only what comes after `?` is the query string.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A function has `limit: int = 10`. A request has no `limit` at all. What happens?
:::
- [ ] 422, because limit is missing
- [x] The function runs with limit set to 10
- [ ] The function runs with limit set to None
:::explain
A default makes a parameter optional. Without a default it would be required, and missing it would give 422.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why type a path parameter as an Enum instead of `str`?
:::
- [ ] It makes the route faster
- [x] Values outside the list are refused with 422, and /docs shows the allowed values
- [ ] Python requires it for paths
:::explain
The type is a rule FastAPI enforces before your code runs, and it is published in `/docs` for whoever calls the API.
:::
:::

:::step{type=deep-dive title="Go deeper: the order of routes, lists in the query, and StrEnum"}
**Order matters.** FastAPI tries routes in the order they were written. We added `/items/today` **after**
`/items/{item_id}`, and asked for `/items/today`: the first route matched, tried to turn `today` into an `int`, and
answered `422`. Write fixed paths before paths with parameters, and both work.

**Several values for one name.** `/items?category=bag&category=wallet` can arrive as a list with
`category: Annotated[list[str] | None, Query()] = None` (next chapter introduces `Annotated` and `Query`).

**StrEnum.** Python 3.11 added `enum.StrEnum`, whose members turn into their plain text in f-strings (`f"{line}"` is
`red`). FastAPI accepts it in exactly the same way; the docs' examples still use `str, Enum`, so this course does too.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Tell path parameters (a piece of the path, `{line}`) from query parameters (after `?`, any parameter not in the
  path).
- Make query parameters optional with a default, `str | None = None` or `int = 10`, and know that no default means
  required.
- Combine filters one after another, and apply a limit last.
- Restrict a value to a fixed list with an Enum, use `.value` for its text, and get the 422 for free.

:::photo{src="/lesson-images/fastapi/fa-03-sketch.webp" alt="Sketchnote: Path and query parameters. The path names a thing. The query string, after the ?, narrows, sorts or pages a list of things. Flow: the URL, path values from  , other parameters from the query, FastAPI converts each type, your function filters. Remember: A default makes a parameter optional; no default, required; Query parameters you did not declare are ignored; An Enum type allows only its values; others get 422; Write fixed paths before paths with parameters." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 4: rules for values, so a search of two letters or a limit of 5,000 is refused.
:::
