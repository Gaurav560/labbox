:::step{type=story title="What happens to an umbrella left on a train?"}
Every evening, a city metro's trains come back to the depot carrying things nobody meant to leave: umbrellas, school
bags, phones, keys, a wallet under a seat. Staff collect them, label them and put them on shelves. The next morning
the owners start asking: "I left a black umbrella on the red line yesterday. Do you have it?"

Here is the shelf of one real lost-property office, in Helsinki: every umbrella tagged, every tag waiting for an owner.

:::photo{src="/lesson-images/fastapi/lost-umbrellas.webp" alt="Dozens of umbrellas standing in blue and grey bins, each with a white paper tag tied to its handle, in a lost and found office" credit="Paul Keller" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:Found_umbrellas_(1555767152).jpg"}
Found umbrellas at the lost and found office in Helsinki, each one tagged.
:::

A shelf cannot answer questions. A phone app, a station screen or a chatbot could, if they had something to ask. In
this course you build that something: **Lostdesk**, the API behind a metro's lost-property office. By the last
chapter it stores found items in a database, takes passengers' reports, lets staff sign in, checks every input and
streams new finds live. Today it answers its very first questions.

:::mission
Start Lostdesk, then add two routes: one that lists every found item, and one that gives back a single item, or a
proper "not found".
:::
:::

:::step{type=history title="The story of FastAPI"}
:::before
Python web code in the 2010s, with frameworks like Flask (2010) and Django (2005), worked well, but a lot of it was
checking by hand. Is `item_id` really a number? Is the `email` field there at all? Every route repeated those checks,
and the documentation for other developers was written separately, by hand, and was soon out of date.
:::

:::solved
In 2018 Sebastián Ramírez, a developer in Colombia, noticed that Python had gained **type hints**, small labels like
`item_id: int` that say what kind of value a name holds. His idea: let the framework read those labels and do the
checking, the converting and the documentation by itself. Write the type once; get the check, the error message and
the docs for free. He called it FastAPI.
:::

:::timeline
- **2015** Python 3.5 adds type hints (PEP 484): `def get_item(item_id: int)`.
- **2017** Samuel Colvin publishes **Pydantic**, which checks data against type hints (first release 3 May 2017).
- **2018** Tom Christie publishes **Starlette** (25 June 2018), a small, fast toolkit for Python web servers.
- **2018** Sebastián Ramírez builds FastAPI on top of both; version 0.1.0 reaches PyPI on 8 December 2018.
- **2023** Pydantic 2.0 (30 June 2023) moves its core into Rust, and FastAPI follows within days (0.100.0, 7 July).
- **2026** FastAPI 0.165.0 (18 November 2026), the version this course uses.
:::

:::usedby
FastAPI's own home page quotes teams at Microsoft (machine-learning services), Uber (a prediction server for its
Ludwig project), Netflix (Dispatch, its open-source crisis-management tool) and Cisco.
:::

:::funfact
FastAPI is still below version 1.0, after eight years and more than 160 releases. That is a choice, not a sign of
trouble: its docs ask you to pin the exact version you use (this course pins 0.165.0), because small breaking changes
can still arrive in a minor release.
:::
:::

:::step{type=concept title="What an API is"}
Look at London's lost-property office. You do not walk into the store room and search the shelves yourself. You go
to the counter, ask in a set way ("a black umbrella, red line, Tuesday"), and get an answer in a set way.

:::photo{src="/lesson-images/fastapi/baker-street-lost-property.webp" alt="The street front of Transport for London's Lost Property Office at 200 Baker Street, a pale blue shop window with the London Underground roundel sign, two men talking outside" credit="Andy F" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:TfL_lost_property_office_on_Baker_Street_-_geograph.org.uk_-_1404542.jpg"}
Transport for London's Lost Property Office, 200 Baker Street.
:::

An **API** (Application Programming Interface) is that counter, for programs. A program sends a request to an
address, like `http://localhost:8000/items/3`, and gets back an answer it can read without any guessing. For web
APIs that answer is almost always **JSON** (JavaScript Object Notation): plain text that looks like Python's
dictionaries and lists, with double quotes:

```json
{"id": 3, "title": "silver phone", "station": "Tech Park"}
```

The words you will use all course:

| Word | Means | In Lostdesk |
|---|---|---|
| **server** | the program that waits for requests and answers them | Lostdesk, running on port 8000 |
| **client** | whoever sends the request | the Preview tab, `curl`, a phone app |
| **route** (or endpoint) | one address the API answers, with one method | `GET /items` |
| **request** | what the client sends: a method, a path, maybe data | `GET /items/3` |
| **response** | what the server sends back: a status code and a body | `200` and the JSON above |
:::

:::step{type=try title="Run it and look" file="01-first-api/main.py" line="1-17"}
Open `main.py`. Then start the server in the terminal:

```bash run
cd /workspace/01-first-api && fastapi dev main.py --host 0.0.0.0 --port 8000 --root-path /preview/fastapi-first-api/8000
```

```text
 ⚡️ Starting FastAPI in development mode

 🐍 Using import string: main:app

 🌐 Server started at http://0.0.0.0:8000
    Documentation at http://0.0.0.0:8000/docs

  Logs:

 ▕  Will watch for changes in these directories: ['/workspace/01-first-api']
 ▕  Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
 ▕  Started reloader process [18] using WatchFiles
 ▕  Started server process [20]
 ▕  Waiting for application startup.
 ▕  Application startup complete.
```

Now open the **Preview** tab, next to the terminal. It shows the answer to `GET /`:

```json
{"message":"Lostdesk is open. Try /items"}
```

What happened, line by line:

- `fastapi dev main.py` is FastAPI's command for working on an app. It found `app` inside `main.py` ("import string:
  main:app") and started **Uvicorn**, the program that actually listens for requests (the "server" in the table).
- `--host 0.0.0.0` makes it listen to requests from outside the machine too, which the Preview tab needs. Without it,
  `fastapi dev` listens only inside the machine, and the Preview cannot reach it.
- `--root-path ...`: the Preview tab reaches your server through LabBox, at an address that starts with
  `/preview/fastapi-first-api/8000`. This option tells FastAPI so, and the `/docs` page below needs it to find its
  data. Real servers behind a company's gateway use the same option (FastAPI's docs call it "behind a proxy").
- "Will watch for changes": every time you save `main.py`, the server restarts by itself. Leave it running in this
  terminal while you work, and open a second terminal (the **+** button) for other commands. **Ctrl + C** stops it.

The process numbers in square brackets will differ on your machine.
:::

:::step{type=concept title="A route is a function" file="01-first-api/main.py" line="4-17"}
Here is everything `main.py` has so far, apart from the data:

```python
app = FastAPI()


@app.get("/")
def home():
    return {"message": "Lostdesk is open. Try /items"}
```

- `app = FastAPI()` creates the application. Every route is attached to it, and `fastapi dev` looks for it by name.
- `@app.get("/")` is a **decorator**: the line starting with `@` just above a function. It tells FastAPI: "when a
  `GET` request for the path `/` arrives, call the function below".
- `home()` is a normal Python function. It gives back a dictionary, and FastAPI turns it into JSON text for the
  response. You never write JSON by hand.

`FOUND` above it (lines 7 to 12) is today's data: four found items, kept in a dictionary by their id number. Later
chapters move it into a real database; for now a dictionary is enough to learn on. Each `GET` you add is one more
question Lostdesk can answer.
:::

:::step{type=concept title="One request, start to finish"}
When the Preview asks for `/`, a lot happens in a few milliseconds. Press Play and follow a request for one item:

:::diagram{name="fastapi-request"}
A request goes through Uvicorn to FastAPI, which finds the route, checks and converts the inputs, calls your function and turns its answer into JSON.
:::

Two of those steps are why FastAPI exists: **checking and converting the inputs** before your function runs, and
**turning the answer into JSON** after. You write only the middle.
:::

:::step{type=try title="/docs: the page you did not write"}
In the Preview tab, change the path to `/docs` and press Enter.

You see an interactive page that lists every route of Lostdesk, with a **Try it out** button for each. You did not
write a line of it. FastAPI built it from your code: the paths, the methods, and (from the next routes on) the types
of every parameter. It follows a standard called **OpenAPI**, and the raw description is at `/openapi.json`.

This page is not a toy. Real teams send it to the people who build the phone app, so they never have to ask "what
does this endpoint take?". And because it is built from the code, it can never be out of date. Come back to `/docs`
after each task in this course and watch it grow.
:::

:::step{type=example title="Worked example: a second route"}
This route is not in your project; it shows the shape your first task needs. Suppose Lostdesk should list the metro's
lines:

```python
LINES = {"red": "Riverside to Airport", "blue": "Old Market to University"}


@app.get("/lines")
def list_lines():
    return {"lines": list(LINES.keys())}
```

1. `@app.get("/lines")`: a `GET` request for `/lines` calls the function below. The function's name can be anything
   you like; the path in the decorator is what clients use.
2. `LINES.keys()` gives the keys, and `list(...)` turns them into a list: `["red", "blue"]`.
3. The answer is wrapped in a dictionary, `{"lines": [...]}`. APIs usually do this instead of answering with a bare
   list, so that more keys (a total, the next page) can be added later without breaking anyone.

The answer would be `{"lines":["red","blue"]}`.
:::

:::step{type=task task=menu title="Your turn: list every found item" file="01-first-api/main.py" line="20"}
In `main.py`, add a route for `GET /items` that gives back every found item, in id order, inside a dictionary under
the key `"items"`:

```json
{"items": [{"id": 1, "title": "black umbrella", "station": "Riverside"}, ...]}
```

`FOUND.values()` gives the items in the order they were written, which is id order here. Save the file (the server
restarts by itself), then change the Preview's path to `/items`. Then press **Check**.

The usual slips, each one tried:

- Giving back the list itself, `return list(FOUND.values())`. It works in the browser, but the check asks for the
  dictionary with the `"items"` key, as in the worked example, and says so.
- Forgetting the decorator line. The function exists, but no path leads to it: `/items` stays `{"detail":"Not
  Found"}`, which is FastAPI's own answer when no route matches.
:::

:::step{type=concept title="Values from the path, and status codes" file="01-first-api/main.py" line="23"}
Your second route needs a value from the path itself: `/items/3` should give item 3. Write the changing part in curly
braces, and give the function a parameter with the same name:

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    ...
```

The `: int` is a type hint, and FastAPI takes it seriously. The path is text, `"3"`; FastAPI turns it into the
number `3` before calling your function. That matters, because `FOUND`'s keys are numbers: the text `"3"` would never
match.

Every response also carries a **status code**, a three-digit number that says how it went, before anyone reads the
body:

| Code | Name | Means |
|---|---|---|
| `200` | OK | here is what you asked for |
| `404` | Not Found | there is nothing at that address |
| `422` | Unprocessable Entity | your request was understood, but its data is wrong |
| `500` | Internal Server Error | the server crashed |

To answer "not found", **raise** an exception instead of returning (chapter 13 of the Python course explains
`raise`):

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="No item with that id")
```

FastAPI catches it and sends status 404 with the body `{"detail":"No item with that id"}`.
:::

:::step{type=predict title="Guess first"}
:::question
With `item_id: int`, what does `GET /items/umbrella` give?
:::
- [ ] 404, because there is no item called umbrella
- [x] 422, because umbrella is not a whole number
- [ ] 500, because the function crashes
:::explain
FastAPI tries to turn `"umbrella"` into an `int`, fails, and answers 422 before your function ever runs. We ran it:

```json
{"detail":[{"type":"int_parsing","loc":["path","item_id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"umbrella"}]}
```

`loc` says where the bad value was (the path, the parameter `item_id`), `msg` says what is wrong, and `input` repeats
what was sent. Your code did not have to write any of it.
:::
:::

:::step{type=task task=price title="Your turn: one item, or a real 404" file="01-first-api/main.py" line="23"}
Add `GET /items/{item_id}`:

- `/items/3` gives back item 3: `{"id":3,"title":"silver phone","station":"Tech Park"}`;
- an id that is not in `FOUND`, like `/items/99`, gives status **404** with a `detail` message;
- `/items/umbrella` gives 422 by itself, once the parameter has the type `int`.

Try all three in the Preview, then press **Check**.

The usual slips, each one tried on the lab machine:

- No type: `def get_item(item_id):`. Then `item_id` is the text `"3"`, it is never found in `FOUND`, and even item 3
  gives your 404. The check spots it and tells you to add `: int`.
- Answering `{"error": "not found"}` with a plain `return`. The browser shows it, but the status is **200 OK**, and
  every program calling Lostdesk will believe it found something.
- No check at all, just `return FOUND[item_id]`. For 99 the dictionary raises `KeyError`, and the client gets
  `500 Internal Server Error`: a crash, not an answer.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A route function gives back `{"items": []}`. What does the client receive?
:::
- [ ] A Python dictionary
- [x] The JSON text `{"items":[]}`
- [ ] Nothing, because the list is empty
:::explain
FastAPI turns the dictionary into JSON text. Clients in any language can read it; an empty list is still a valid
answer.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which status code tells a client "there is nothing at that address"?
:::
- [ ] 200
- [x] 404
- [ ] 422
:::explain
404 Not Found. 422 means the request's data was wrong, like a word where a number belongs.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does `fastapi dev` need `--host 0.0.0.0` in LabBox?
:::
- [ ] Without it the server does not start
- [x] Without it the server only listens inside the machine, so the Preview tab cannot reach it
- [ ] It makes the server faster
:::explain
By default `fastapi dev` listens on `127.0.0.1`, the machine talking to itself. `0.0.0.0` means "every network
address this machine has", which includes the one the Preview uses.
:::
:::

:::step{type=deep-dive title="Go deeper: Uvicorn, Starlette, Pydantic and ASGI"}
FastAPI is a thin, clever layer over other projects, and knowing them helps when you read error messages:

| Piece | Its job | You see it in |
|---|---|---|
| **Uvicorn** | the server: opens port 8000, reads the raw request, writes the raw response | the logs, `Uvicorn running on ...` |
| **Starlette** | the web toolkit: routing, requests, responses, middleware | error messages and imports like `starlette.responses` |
| **Pydantic** | checks and converts data against type hints | 422 bodies (`int_parsing`), and models from chapter 5 |
| **FastAPI** | joins them: reads your type hints, builds `/docs` | your code |

Between Uvicorn and Starlette sits **ASGI** (Asynchronous Server Gateway Interface), a standard way for a Python server
to hand a request to a Python app. Because it is a standard, you could swap Uvicorn for another ASGI server without
changing a line of Lostdesk. Chapter 18 shows what "asynchronous" buys you.

`fastapi run main.py` is the production twin of `fastapi dev`: no reloading, and listening on `0.0.0.0` by default.
The last chapter uses it.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Start a FastAPI app with `fastapi dev`, see it in the Preview tab, and read its automatic docs at `/docs`.
- Write a route: a function with a decorator like `@app.get("/items")` that gives back a dictionary, sent as JSON.
- Take a value from the path with `{item_id}` and a type hint, and let FastAPI convert it or answer 422.
- Answer "not found" properly with `HTTPException(status_code=404)`, and tell 200, 404, 422 and 500 apart.

:::photo{src="/lesson-images/fastapi/fa-01-sketch.webp" alt="Sketchnote: Your first API. An API answers requests from programs. FastAPI turns a Python function into a route and its answer into JSON. Flow: a request arrives, FastAPI finds the route, it checks the inputs, your function runs, a JSON response goes back. Remember: @app.get(/items) attaches a function to a path; A type hint makes FastAPI convert the value, or answer 422; raise HTTPException(status_code=404) for not found; /docs is built from your code." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 2: how a request really travels, and what the status codes and headers in it mean.
:::
