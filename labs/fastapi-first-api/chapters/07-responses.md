:::step{type=story title="Who may read a passenger's phone number?"}
A passenger who lost a laptop bag leaves a report with a phone number, so the desk can call when the bag turns up.
Staff need that number. The station screen that lists open reports does not, and neither does anyone who types
`/reports/1` into a browser. Today, in the starter, they all get it:

```json
{"id":1,"title":"grey laptop bag","line":"red","station":"Tech Park","contact":"98200 11111","details":"a tiger sticker on the front","status":"open"}
```

Showing less than you store is an old idea. Kobe's Rokko Liner runs past people's flats, so its windows frost over
on those sections: the train still passes, but the view inside the homes stays private.

:::photo{src="/lesson-images/fastapi/frost-glass-train.webp" alt="A train window with a white label in Japanese across it; outside, a blue sky with light clouds" credit="Hahifuheho" license="CC0" source="https://commons.wikimedia.org/wiki/File:Instant_frost_glass_on_Rokko_liner_20200812.jpg"}
A window on Kobe's Rokko Liner. The label says "Instant frost glass: it clouds over on some sections".
:::

:::mission
Make `GET /reports/{report_id}` and `GET /reports` show every report without its contact, using a response model.
:::
:::

:::step{type=concept title="The return type is a filter" file="07-responses/main.py" line="16-33"}
`main.py` has two models for a report:

```python
class ReportIn(BaseModel):      # what a passenger sends
    title: str = Field(min_length=3, max_length=60)
    line: Line
    station: str
    contact: str = Field(min_length=6, max_length=40)
    details: str | None = None


class ReportPublic(BaseModel):  # what anyone may see
    id: int
    title: str
    line: Line
    station: str
    details: str | None = None
    status: str
```

`ReportPublic` has no `contact`, and it has two fields the passenger never sends: `id` and `status`, which Lostdesk
decides. Now look at `POST /reports`:

```python
@app.post("/reports")
def report_lost(report: ReportIn) -> ReportPublic:
```

`-> ReportPublic` is the function's **return type**. FastAPI reads it and uses it as the **response model**: whatever
the function gives back is checked against `ReportPublic`, and only its fields are sent. Press Play:

:::diagram{name="fastapi-response-filter"}
The function gives back the whole stored report; the return type keeps only the public fields.
:::
:::

:::step{type=try title="Stored is not shown" file="07-responses/main.py" line="45-49"}
We sent a new report to the starter, contact included:

```text
POST /reports {"title": "black wallet", "line": "red", "station": "Riverside", "contact": "98200 33333"}
```

The answer had no contact:

```json
{"id":3,"title":"black wallet","line":"red","station":"Riverside","details":null,"status":"open"}
```

Yet the function returned `REPORTS[new_id]`, the stored dictionary, which **does** hold `"contact": "98200 33333"`.
The return type filtered it on the way out. The two `GET` routes have no return type yet, so they send the dictionary
as it is, phone number and all. That is your task.
:::

:::step{type=concept title="Three shapes of one report"}
Real APIs usually have several models for one thing, one for each direction. FastAPI's docs call them **extra
models**:

| Shape | Has | Who uses it |
|---|---|---|
| `ReportIn` | what the client may send: title, line, station, contact, details | the request body |
| stored report | everything: `id`, all of `ReportIn`, `status` | Lostdesk itself |
| `ReportPublic` | what anyone may see: no contact | the response |

Why not one model for everything? Because the client must not choose its own `id` or set `status` to `"returned"`,
and the public must not see the contact. Chapter 16 adds a fourth case that matters even more: a user's password
hash, stored but never, ever sent.
:::

:::step{type=concept title="When the answer does not fit"}
A response model also **checks**. If the function gives back something that lacks a required field, that is a bug in
Lostdesk, not in the request. We made a small app whose response model needs `status`, and returned a dictionary
without it. The client got `500 Internal Server Error`, and the terminal running the server said:

```text
fastapi.exceptions.ResponseValidationError: 1 validation error:
  {'type': 'missing', 'loc': ('response', 'status'), 'msg': 'Field required', 'input': {'id': 1}}
```

`'loc': ('response', 'status')`: the problem is in the **response**. A 500 is right here: the client did nothing
wrong, so there is nothing for it to fix, and Lostdesk refuses to send an answer that breaks its own published shape.
:::

:::step{type=example title="Worked example: response_model in the decorator"}
This is not in your project. Sometimes the function cannot have the return type, for example when it returns a plain
dictionary on purpose. The decorator takes the model instead:

```python
@app.get("/reports/{report_id}/summary", response_model=ReportPublic)
def report_summary(report_id: int) -> dict:
    return REPORTS[report_id]
```

1. `response_model=ReportPublic` does the filtering and checking, exactly like a return type.
2. When both are present, the decorator's `response_model` wins.
3. For a list, use `list[ReportPublic]`, in either place.

The FastAPI docs recommend the return type when it fits, because your editor then checks it too.
:::

:::step{type=predict title="Guess first"}
:::question
`get_report` returns the stored dictionary, which has a `contact`. Its return type is `ReportPublic`. Is the contact
in the answer?
:::
- [ ] Yes: the function returned it
- [x] No: the response model keeps only its own fields
- [ ] It causes a 500, because of the extra field
:::explain
Extra fields are dropped, not refused. Only a **missing** required field causes a 500.
:::
:::

:::step{type=task task=public_report title="Your turn: one report, no contact" file="07-responses/main.py" line="58-60"}
Make `GET /reports/{report_id}` give back the report as a `ReportPublic`:

```json
{"id":1,"title":"grey laptop bag","line":"red","station":"Tech Park","details":"a tiger sticker on the front","status":"open"}
```

and keep its 404 for an unknown id. Then press **Check**.
:::

:::step{type=task task=report_list_public title="Your turn: the list, no contacts" file="07-responses/main.py" line="52-55"}
Make `GET /reports` give back every report without its contact: a list of `ReportPublic`. The answer is a JSON list,
starting `[{"id":1,"title":"grey laptop bag",...`. Then press **Check**, and look at `/docs`: both routes now show
`ReportPublic` as their response, so callers can see there is no contact to expect.

The usual slip: a return type of `ReportPublic` on the list route. The function gives back a list, the model wants
one report, and every request becomes a 500 with a `ResponseValidationError` in the terminal. A list needs
`list[ReportPublic]`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does FastAPI use as the response model when a function says `-> ReportPublic`?
:::
- [x] `ReportPublic`
- [ ] The dictionary the function returns
- [ ] Nothing: return types are only for the editor
:::explain
FastAPI reads the return type and uses it to check and filter the answer.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
The answer is missing a field that the response model requires. Which status does the client get?
:::
- [ ] 422
- [x] 500
- [ ] 200, with the field as null
:::explain
422 means "your request is wrong". Here the server's own answer is wrong, so it is a 500, and the details go to the
server's log.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does `ReportIn` not have an `id` field?
:::
- [ ] Ids are not allowed in Pydantic models
- [x] Lostdesk chooses ids; a client must not be able to send one
- [ ] Because the id is in the path
:::explain
Input models hold what the client may decide. Anything the server decides (ids, statuses, timestamps) belongs only in
the stored data and the output model.
:::
:::

:::step{type=deep-dive title="Go deeper: leaving out empty fields, and inheritance"}
**Leaving out null fields.** `@app.get(..., response_model_exclude_none=True)` drops fields whose value is `None`,
so a report with no details simply has no `details` key. Handy for compact answers; but clients must then cope with a
missing key, so many teams keep the `null`.

**Sharing fields with inheritance.** Models are classes, so they can inherit:

```python
class ReportBase(BaseModel):
    title: str
    line: Line
    station: str
    details: str | None = None


class ReportIn(ReportBase):
    contact: str


class ReportPublic(ReportBase):
    id: int
    status: str
```

Each field is written once. Chapter 13 uses exactly this pattern with a database.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Use a function's return type (or `response_model=`) as a response model, for one object or a `list[...]`.
- Explain how it filters: extra fields are dropped, so stored secrets like a contact never leave the server.
- Read a `ResponseValidationError`: the server's own answer broke its model, so the client gets 500.
- Design separate input, stored and public shapes for one thing.

:::photo{src="/lesson-images/fastapi/fa-07-sketch.webp" alt="Sketchnote: Response models. What Lostdesk stores and what it shows can differ. The return type decides the shape of every answer. Flow: the function returns stored data, FastAPI reads the return type, required fields are checked, every other field is dropped, public JSON goes out. Remember: Input model: what clients may send. Output model: what they may see; Extra fields are dropped; a missing one causes 500; Use list[Model] for a list; Secrets stay stored, never sent." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 8: status codes and errors of your own, like 201 Created and 409 Conflict.
:::
