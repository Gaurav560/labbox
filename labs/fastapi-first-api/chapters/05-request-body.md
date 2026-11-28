:::step{type=story title="How does a found umbrella get onto the shelf?"}
So far Lostdesk only answers questions. But the shelf changes all day: a cleaner finds a red scarf at University
station and has to log it; a passenger who lost a laptop bag wants to leave a report with a phone number. Both need
to **send** data to Lostdesk, not just ask.

A lost-property office has always worked this way. This is Berlin's, in January 1973: every bag, pram and bicycle on
those shelves was handed in at a counter and written down before it got a place.

:::photo{src="/lesson-images/fastapi/fundbuero-berlin.webp" alt="A black and white photo of a large room with tall wooden shelves packed with handbags, suitcases and briefcases; a man in a white coat pushes an old pram past a row of bicycles" credit="Klaus Franke, Bundesarchiv, Bild 183-M0125-421" license="CC BY-SA 3.0 de" source="https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_183-M0125-421,_Fundb%C3%BCro_in_Berlin.jpg"}
The lost-property office in Berlin, 25 January 1973: shelves of handed-in bags, a pram and bicycles.
:::

On the web, sending data means a `POST` request with a **body**. Today Lostdesk accepts two kinds: a found item from
staff, and a lost report from a passenger. You describe each one as a small class, and FastAPI checks every field
before your code sees it.

:::mission
Add `POST /items`, which logs a found item, and `POST /reports`, which stores a passenger's report.
:::
:::

:::step{type=concept title="A body, described by a model" file="05-request-body/main.py" line="16-32"}
Query parameters are fine for a few short values. A report has six fields, one of them a sentence, so it travels in
the request's **body** as JSON:

```json
{"title": "grey laptop bag", "line": "red", "station": "Tech Park", "contact": "98200 11111"}
```

You describe its shape with a **Pydantic model**, a class that inherits from `BaseModel`. `main.py` already has two:

```python
class LostReport(BaseModel):
    title: str
    line: Line
    station: str
    contact: str
    details: str | None = None
```

Each line is a field: a name and a type, exactly like a function parameter. `details` has a default, so it is
optional; every other field is required. And `line: Line` reuses chapter 3's Enum, so only red, blue and green get
in.

Then a route takes the model as a parameter:

```python
@app.post("/reports")
def report_lost(report: LostReport):
    ...
```

The rule FastAPI follows: a parameter in the path is a path parameter; a parameter of a simple type (`int`, `str`)
is a query parameter; a parameter whose type is a Pydantic model is read from the **body**.
:::

:::step{type=history title="Where Pydantic came from"}
Pydantic is older than FastAPI. Samuel Colvin, a British developer, published its first version on 3 May 2017,
with one idea: use Python's type hints to check and convert data at runtime. FastAPI's author built on it a year and a
half later, and the two grew together.

:::timeline
- **2017** Pydantic 0.0.1 (3 May): models from type hints.
- **2018** FastAPI 0.1.0 (8 December) uses Pydantic for every body, query and response.
- **2023** Pydantic 2.0 (30 June): the checking core is rewritten in Rust, a fast compiled language. Pydantic's own
  docs show an example where it checks JSON about 3.5 times faster than the same checks hand-written in Python.
- **2023** FastAPI 0.100.0 (7 July) supports Pydantic 2.
:::

Pydantic is now used far beyond FastAPI: for settings files (chapter 19), for data pipelines, and by many AI
libraries to describe the structured answers they ask a model for.
:::

:::step{type=concept title="The body's journey"}
Press Play to follow one report:

:::diagram{name="fastapi-body"}
JSON text arrives, is parsed, is checked field by field against the model, missing optional fields get their defaults, and your function receives a ready object.
:::

Inside your function, `report` is a real object: `report.title` is a `str`, `report.line` is a `Line`. To store it
or send it back, turn it into a dictionary with `report.model_dump()`. Add `mode="json"` and every value becomes plain
JSON-ready data, so `line` is stored as the text `"blue"`, not as the Enum member.
:::

:::step{type=try title="Send a POST with curl" file="05-request-body/main.py" line="55-56"}
The solution of this chapter can log a found item. We started it and sent one with curl (`-X POST` for the method,
`-H` for a header, `-d` for the body):

```bash
curl -s -i -X POST localhost:8000/items -H "content-type: application/json" -d '{"title": "red scarf", "category": "clothing", "line": "blue", "station": "University"}'
```

```text
HTTP/1.1 200 OK
date: Sat, 28 Nov 2026 05:57:59 GMT
server: uvicorn
content-length: 87
content-type: application/json

{"id":4,"title":"red scarf","category":"clothing","line":"blue","station":"University"}
```

The header `content-type: application/json` tells Lostdesk the body is JSON. There is an easier way to try it: open
`/docs` in the Preview, click `POST /items`, then **Try it out**. The page shows an example body built from your
model, sends it for you, and shows the answer. (Status 200 is FastAPI's default; chapter 8 changes it to the more
precise 201 Created.)
:::

:::step{type=concept title="Bad bodies, exact answers"}
Every one of these was refused with a 422 before the function ran. We sent them to the solution:

| We sent | FastAPI answered |
|---|---|
| a report with no `contact` | `"type":"missing","loc":["body","contact"],"msg":"Field required"` |
| `"line": "Blue"` with a capital B | `"type":"enum","loc":["body","line"],"msg":"Input should be 'red', 'blue' or 'green'"` |
| `"title": 42`, a number | `"type":"string_type","loc":["body","title"],"msg":"Input should be a valid string"` |
| broken JSON, a comma before `}` | `"type":"json_invalid","msg":"JSON decode error"`, with `"Expecting property name enclosed in double quotes"` |

Two things to notice. `loc` now starts with `"body"`, so the client knows where to look. And Pydantic does not turn
the number 42 into the text `"42"`: a string field wants a string. (It does turn the text `"3"` into the number 3 for
an `int` field, as you saw in the path; that direction is safe, the other would hide mistakes.)
:::

:::step{type=example title="Worked example: store, then answer"}
This route is not in your project. It stores a passenger's note about a station:

```python
NOTES: list[dict] = []


class Note(BaseModel):
    station: str
    text: str


@app.post("/notes")
def add_note(note: Note):
    stored = {"id": len(NOTES) + 1, **note.model_dump(mode="json")}
    NOTES.append(stored)
    return stored
```

1. `len(NOTES) + 1`: the first note gets id 1, the next id 2.
2. `{"id": ..., **note.model_dump(...)}`: a new dictionary with the id first, then every field of the note (the `**`
   unpacks one dictionary into another).
3. Append it, and give back what was stored, so the client learns the new id.

Your two tasks follow this shape; `POST /items` works out its id differently.
:::

:::step{type=predict title="Guess first"}
:::question
`FOUND` has items 1, 2 and 3. A staff member logs a red scarf. Which id should it get?
:::
- [ ] 3, because there are 3 items
- [x] 4: one more than the biggest id so far
- [ ] Any number, as long as it is new
:::explain
`max(FOUND) + 1` is 4. Counting with `len` would be wrong as soon as an item is deleted (chapter 9): with items 1 and
3 left, `len(FOUND) + 1` is 3, an id that is already taken.
:::
:::

:::step{type=task task=found_item title="Your turn: log a found item" file="05-request-body/main.py" line="55-56"}
Add `POST /items`. It takes a `FoundItemIn` as its body, stores it in `FOUND` under the next id, and gives back the
stored item, id included:

```json
{"id": 4, "title": "red scarf", "category": "clothing", "line": "blue", "station": "University"}
```

Afterwards `GET /items/4` finds it. A body with `"line": "purple"`, or without a `station`, gives 422 by itself.

Try it in `/docs`, then press **Check**.

The usual slip: `FOUND[new_id] = item`, storing the model object itself, without its id. `POST /items` still answers
something, but `GET /items/4` gives back the scarf with no `"id"` in it. Store a dictionary that has the id.
:::

:::step{type=task task=report_lost title="Your turn: a passenger's report" file="05-request-body/main.py" line="59-60"}
Add `POST /reports`. It takes a `LostReport`, adds it to `REPORTS` with an id (1 for the first, 2 for the next) and
gives back what was stored:

```json
{"id": 1, "title": "grey laptop bag", "line": "red", "station": "Tech Park", "contact": "98200 11111", "details": null}
```

`details` is `null` (JSON's word for `None`) because it was not sent. `GET /reports`, already in the file, lists them.
Then press **Check**.

The usual slips: `"id": len(REPORTS)`, which gives the first report id 0; and forgetting to `append`, so the answer
looks right but `GET /reports` stays empty. The check sends two reports and then lists them.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`def create(item: FoundItemIn, notify: bool = False)` on `POST /items`. Where does `notify` come from?
:::
- [ ] The body
- [x] The query string, like `?notify=true`
- [ ] The path
:::explain
A simple type outside the path is a query parameter. Only the parameter whose type is a model is read from the body.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A model field is `details: str | None = None`. The client leaves it out. What does your function see?
:::
- [ ] A 422 error
- [x] `report.details` is `None`
- [ ] `report.details` is `""`
:::explain
A field with a default is optional; the default fills the gap.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does Pydantic refuse `"title": 42` for a `str` field?
:::
- [ ] Numbers are not allowed in JSON
- [x] A number where text was expected is more likely a mistake than a title
- [ ] It is a bug in Pydantic
:::explain
Pydantic converts text to numbers where the meaning is clear, like `"3"` for an `int`, but refuses to guess the other
way round.
:::
:::

:::step{type=deep-dive title="Go deeper: strict mode, extra fields, and where the data really goes"}
**Extra fields.** By default a model ignores fields it does not know: a body with `"colour": "red"` is accepted and
the colour silently dropped. `model_config = {"extra": "forbid"}` refuses them, as chapter 4 did for query parameters.

**Strict mode.** `model_config = {"strict": True}` turns off even the safe conversions, so `"3"` for an `int` field is
refused. Useful when a client should send exact types.

**Memory is not storage.** `FOUND` and `REPORTS` live in the server's memory. Restart the server, and every new item
and report is gone; run two copies of the server, and each has its own shelf. Chapter 12 moves them into a real
database.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Describe a request body with a Pydantic model: required fields, optional fields with defaults, Enum fields.
- Write `POST` routes that take a model, and know how FastAPI tells body, path and query parameters apart.
- Read the 422s for bodies: `missing`, `enum`, `string_type`, `json_invalid`, with `loc` starting at `"body"`.
- Store what arrives with an id and `model_dump(mode="json")`, and give back what was stored.

:::photo{src="/lesson-images/fastapi/fa-05-sketch.webp" alt="Sketchnote: Request bodies. Data to create something travels in the body of a POST request as JSON. A Pydantic model describes it and checks it. Flow: JSON body arrives, parsed into a dictionary, checked against the model, defaults fill the gaps, your function gets an object. Remember: A parameter whose type is a model comes from the body; Fields without a default are required; model_dump() turns the object back into a dictionary; The next id is one more than the biggest so far." ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 1. Lostdesk answers questions, checks its inputs and accepts new data. Next, Part 2: models
and responses, starting with richer models.
:::
