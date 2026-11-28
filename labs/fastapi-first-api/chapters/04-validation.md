:::step{type=story title="Should Lostdesk answer a search for one letter?"}
A passenger types `a` into the station screen's search box. Lostdesk dutifully finds every item with an "a" in its
title: most of the shelf. Another program asks for `/items?limit=5000`, and Lostdesk would send everything it has,
again and again. A third sends `/items/-7`. None of these crash Lostdesk today, but none of them make sense, and on a
real shelf of thousands of items the first two would be slow and expensive.

A metro checks tickets at the gate, before anyone reaches the platform, not on the train. Problems are cheapest to
stop at the entrance.

:::photo{src="/lesson-images/fastapi/ticket-turnstile.webp" alt="A stainless steel metro ticket gate with a three-armed turnstile, a blue card reader and a white arrow on a blue panel pointing forward" credit="Leo Johannes" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Turnstile_in_Stockholm_Metro_station_in_Slussen-1.jpg"}
A ticket gate in Stockholm's metro, at Slussen: every ticket is checked before the platform.
:::

FastAPI has a gate too. You write the rules into the function's signature (a search of at least 3 characters, a
limit from 1 to 20), and FastAPI checks them before your code runs.

:::mission
Make `limit` stay between 1 and 20, add an `offset` for paging, and make `q` 3 to 40 characters long and `item_id` 1
or more.
:::
:::

:::step{type=concept title="Rules in the type: Annotated, Query and Path"}
Here is a parameter with rules:

```python
from typing import Annotated
from fastapi import Query

limit: Annotated[int, Query(ge=1, le=20)] = 10
```

Read it in three parts:

1. `Annotated[int, ...]`: Python's way (since 3.9) to attach extra information to a type. The type is still `int`;
   everything after the first comma is a note for whoever reads it. FastAPI reads it.
2. `Query(ge=1, le=20)`: the note. "This is a query parameter, greater than or equal to 1, less than or equal to 20."
3. `= 10`: the default, exactly as before.

The rules you will use most:

| Rule | Means | For |
|---|---|---|
| `ge`, `gt` | greater than or equal, greater than | numbers |
| `le`, `lt` | less than or equal, less than | numbers |
| `min_length`, `max_length` | at least, at most this many characters | text |
| `pattern` | must match this regular expression | text, like `pattern="^[A-Z]{2}[0-9]{4}$"` |

For a path parameter, use `Path(...)` instead of `Query(...)`, with the same rules. Mixing them up is caught at once:
we wrote `Query` for the path parameter `item_id`, and the app would not even start: `AssertionError: Cannot use
`Query` for path param 'item_id'`.
:::

:::step{type=concept title="What happens at the gate"}
The checking is not a vague promise; it has a fixed order. Press Play:

:::diagram{name="fastapi-validation"}
FastAPI converts every parameter, checks every rule, collects every problem, and answers 422 with all of them; only a request that passes reaches your function.
:::

The most useful detail is step 4: FastAPI collects **every** problem before answering, so a client fixes them all in
one go instead of one per request.
:::

:::step{type=try title="Three mistakes, one answer" file="04-validation/main.py" line="18-32"}
The solution of this chapter has all the rules. We sent it a request with three mistakes at once,
`/items?q=ab&limit=0&offset=-1`, and got one 422 (line breaks added to read it):

```json
{"detail":[
  {"type":"string_too_short","loc":["query","q"],"msg":"String should have at least 3 characters","input":"ab","ctx":{"min_length":3}},
  {"type":"greater_than_equal","loc":["query","limit"],"msg":"Input should be greater than or equal to 1","input":"0","ctx":{"ge":1}},
  {"type":"greater_than_equal","loc":["query","offset"],"msg":"Input should be greater than or equal to 0","input":"-1","ctx":{"ge":0}}
]}
```

Each problem names its place (`loc`), says what is wrong in plain English (`msg`), shows the bad `input`, and gives
the rule in `ctx`. A phone app can show each message next to the right field. And in `/openapi.json`, the rules are
published: `limit` is listed with `"minimum": 1`, `"maximum": 20` and `"default": 10`.
:::

:::step{type=concept title="Paging: offset and limit"}
Real shelves hold thousands of items, so APIs hand them out a page at a time. Two numbers do it:

- `limit`: how many items at most in one answer;
- `offset`: how many to skip first.

In Python, that is one slice: `items[offset : offset + limit]`. For `offset=2&limit=2` on six items:

:::trace{title="items[2 : 4]"}
| position | item | kept? |
|---|---|---|
| 0 | black umbrella | no: skipped by the offset |
| 1 | blue school bag | no: skipped by the offset |
| 2 | silver phone | yes |
| 3 | bunch of keys | yes: that is limit 2 |
| 4 | brown leather wallet | no: past the limit |
:::

Page 1 is `offset=0&limit=2`, page 2 is `offset=2&limit=2`, page 3 `offset=4&limit=2`. An offset past the end is not
an error, just an empty page: `/items?offset=10` gave `{"items":[]}`.
:::

:::step{type=example title="Worked example: a rule on a path parameter"}
This is not in your project. A route for one of the metro's ticket windows, numbered 1 to 12:

```python
@app.get("/windows/{number}")
def window(number: Annotated[int, Path(ge=1, le=12)]):
    return {"window": number}
```

1. `Path` instead of `Query`, because `number` is in the path.
2. No default: a path parameter is always required (the path does not match without it).
3. `/windows/13` and `/windows/0` give 422 with `"loc":["path","number"]`; `/windows/5` gives `{"window":5}`.
:::

:::step{type=predict title="Guess first"}
:::question
Lostdesk has 6 items. What does `/items?offset=10` give, with the rules in place?
:::
- [ ] 422, because 10 is more than the number of items
- [x] `{"items":[]}`, an empty page
- [ ] 404
:::explain
`offset` only has the rule `ge=0`, and 10 passes it. Slicing past the end of a list gives an empty list; we tried it.
:::
:::

:::step{type=task task=limits title="Your turn: limits and an offset" file="04-validation/main.py" line="23-25"}
In `list_items`:

- give `limit` the rule 1 to 20, default 10: `/items?limit=0` and `/items?limit=21` give 422;
- add `offset`, 0 or more, default 0: `/items?offset=-1` gives 422;
- give back the items from `offset` on, at most `limit` of them: `/items?offset=2&limit=2` gives items 3 and 4.

```bash run
curl -s "localhost:8000/items?offset=2&limit=2"
```

(Start this chapter's server first, as before, from `/workspace/04-validation`.) Then press **Check**.

The usual slip, tried: slicing `items[offset:limit]`. For `offset=2&limit=2` that is `items[2:2]`, an empty list,
because the end of a slice is a position, not a count. The end is `offset + limit`.
:::

:::step{type=task task=search_rules title="Your turn: rules for q and item_id" file="04-validation/main.py" line="20-21"}
Two more rules:

- `q` is 3 to 40 characters when it is given: `/items?q=ab` gives 422, `/items?q=bag` works;
- `item_id` is 1 or more: `/items/0` and `/items/-3` give 422, and `/items/99` still gives your 404.

Then press **Check**. `q` keeps its default `None`: the rule applies only when a value is sent.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`limit: Annotated[int, Query(ge=1, le=20)] = 10`. What is the type of `limit` inside the function?
:::
- [ ] `Annotated`
- [x] `int`
- [ ] `Query`
:::explain
`Annotated` only attaches the note. The value your function receives is a plain `int`, already checked.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A request breaks two rules at once. How many 422 answers does the client need to see both problems?
:::
- [x] One: the detail list holds both
- [ ] Two: one per request
:::explain
FastAPI checks every parameter and reports every problem together.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Page 3 of a list, 20 items per page. Which query string?
:::
- [ ] `?offset=3&limit=20`
- [x] `?offset=40&limit=20`
- [ ] `?offset=60&limit=20`
:::explain
Page 1 skips 0, page 2 skips 20, page 3 skips 40.
:::
:::

:::step{type=deep-dive title="Go deeper: query parameter models, and refusing unknown parameters"}
When a route has many filters, put them in one class. FastAPI calls it a **query parameter model**:

```python
class Filters(BaseModel):
    model_config = {"extra": "forbid"}
    q: str | None = Field(default=None, min_length=3)
    limit: int = Field(default=10, ge=1, le=20)


@app.get("/m")
def m(filters: Annotated[Filters, Query()]):
    return filters
```

`BaseModel` and `Field` are chapter 5's and 6's tools. The bonus is `"extra": "forbid"`: unknown query parameters are
refused instead of silently ignored. Chapter 3's surprise, `/items?colour=red` returning everything, becomes:

```text
{"detail":[{"type":"extra_forbidden","loc":["query","colour"],"msg":"Extra inputs are not permitted","input":"red"}]}
```

(We ran this small app.) Whether to forbid is a design choice: forbidding catches typos like `?catgory=bag`; allowing
lets old clients keep sending parameters you have retired.

**Paging with millions of rows.** `offset` gets slow on huge database tables, because the database still walks past
every skipped row. Large APIs often page with a "cursor" instead: "the next 20 after id 51,207".
:::

:::step{type=recap title="What you can do now"}
You can now:

- Put rules into a parameter's type with `Annotated` and `Query(...)` or `Path(...)`: `ge`, `le`, `min_length`,
  `max_length`, `pattern`.
- Read a 422 with several problems, each with its `loc`, `msg`, `input` and `ctx`.
- Page through a list with `offset` and `limit`, slicing `items[offset : offset + limit]`.
- Know that the rules are checked before your function runs, and published in `/docs` and `/openapi.json`.

:::photo{src="/lesson-images/fastapi/fa-04-sketch.webp" alt="Sketchnote: Validating input. Rules go into the parameter's type with Annotated, and FastAPI checks them before your function runs. Flow: read each parameter, convert its type, check its rules, collect every problem, 422 or call the function. Remember: Query for query parameters, Path for path parameters; ge and le for numbers, min_length and max_length for text; a page is items from offset to offset plus limit; every rule is published in /docs." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 5: requests that carry data in their body, and the Pydantic models that check it.
:::
