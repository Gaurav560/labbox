:::step{type=story title="Two passengers, one umbrella"}
A passenger files a report for a black umbrella, and the desk matches it to item 1: claimed. An hour later another
passenger describes a black umbrella too, and a busy clerk matches that report to item 1 as well. In the starter, the
second claim simply wins. We tried it:

```text
POST /items/1/claim {"report_id": 12}   ->  200 {"id":1,...,"claimed_by":12}
POST /items/1/claim {"report_id": 13}   ->  200 {"id":1,...,"claimed_by":13}
```

Report 12's owner has lost the umbrella a second time, and nothing anywhere said that something was wrong. Today
Lostdesk learns to say exactly what happened, in the status code itself: **201** when something new is created,
**409** when a request clashes with what already exists.

:::mission
Make `POST /items` answer 201 Created, and refuse a second claim on the same item with your own exception, turned
into a 409 Conflict by an exception handler.
:::
:::

:::step{type=concept title="Status codes are signals"}
Before anyone reads a word of the body, the status code has already said how things went. Railways have long worked
the same way: a semaphore signal's arm tells a driver at a glance, from far away, whether the line ahead is clear.

:::photo{src="/lesson-images/fastapi/semaphore-signal.webp" alt="A tall railway semaphore signal against a cloudy evening sky: a red and white arm sticking out from the top of a metal post with a ladder" credit="Hywel Williams" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Semaphore_Railway_Signal_-_geograph.org.uk_-_285124.jpg"}
A semaphore railway signal at Pantyffynnon station, Wales.
:::

Programs read status codes the same way, and decide what to do before they parse anything. FastAPI has every code
with a readable name in `fastapi.status`:

| Name in code | Number | Use it when |
|---|---|---|
| `status.HTTP_200_OK` | 200 | an answer, nothing created (the default) |
| `status.HTTP_201_CREATED` | 201 | a `POST` made something new |
| `status.HTTP_204_NO_CONTENT` | 204 | it worked, and there is nothing to send back (chapter 9) |
| `status.HTTP_404_NOT_FOUND` | 404 | there is no such thing |
| `status.HTTP_409_CONFLICT` | 409 | the request clashes with the current state |

The names cost nothing at run time and make the code read like a sentence.
:::

:::step{type=try title="200 or 201?" file="08-errors/main.py" line="54-59"}
Start Lostdesk from `/workspace/08-errors` and log an item in `/docs` (`POST /items`, **Try it out**). The answer
works, and its status is 200. The solution's answer to the same body:

```text
201
{"id":4,"title":"red scarf","line":"blue","station":"University","claimed_by":null}
```

One argument in the decorator makes the difference:

```python
@app.post("/items", status_code=status.HTTP_201_CREATED)
```

The status is fixed for every successful answer of that route; errors raised inside it still bring their own codes.
:::

:::step{type=task task=created_201 title="Your turn: 201 Created" file="08-errors/main.py" line="54-55"}
Make `POST /items` answer 201 when it creates an item. Then press **Check**.
:::

:::step{type=concept title="Your own exception" file="08-errors/main.py" line="29-33"}
`HTTPException` is fine for a one-off answer. But "already claimed" is a rule of Lostdesk's own that can be broken in
several places (a claim from the desk, a claim from the app, a claim by email later), and every place should answer
the same way. So `main.py` gives the problem a name, as a normal Python exception class:

```python
class AlreadyClaimed(Exception):
    def __init__(self, item_id: int, report_id: int):
        self.item_id, self.report_id = item_id, report_id
```

It knows nothing about HTTP. It just says "item 1 is already claimed by report 12". The code that finds the problem
raises it; one **exception handler** decides, in one place, how it looks on the web.

What if you raise it and nobody handles it? We tried: the client got `500 Internal Server Error`, and the server's
terminal showed the traceback ending in

```text
main.AlreadyClaimed: (1, 12)
```

FastAPI only knows how to answer its own `HTTPException` and validation errors. Anything else is, as far as it can
tell, a crash.
:::

:::step{type=concept title="The handler: one place for one answer"}
A handler is a function registered for one exception class:

```python
@app.exception_handler(AlreadyClaimed)
def already_claimed_handler(request: Request, exc: AlreadyClaimed):
    return JSONResponse(status_code=..., content={...})
```

Press Play to follow the second claim:

:::diagram{name="fastapi-exception-handler"}
The route raises, FastAPI finds the handler registered for that exception, and the handler's JSONResponse goes to the client.
:::

`JSONResponse` (from `fastapi.responses`) is a response you build by hand: a status code and the content to send as
JSON. Inside the handler you have the exception object, `exc`, with its `item_id` and `report_id`, and the request,
in case the answer depends on it.
:::

:::step{type=example title="Worked example: a closed desk"}
This is not in your project. Suppose the lost-property desk only works from 8 in the morning to 8 in the evening:

```python
class DeskClosed(Exception):
    def __init__(self, opens_at: str):
        self.opens_at = opens_at


@app.exception_handler(DeskClosed)
def desk_closed_handler(request: Request, exc: DeskClosed):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "The lost-property desk is closed", "opens_at": exc.opens_at},
    )
```

1. The exception carries the facts (`opens_at`), not the HTTP details.
2. The handler chooses the code, 503 Service Unavailable, and the body.
3. Any route can now `raise DeskClosed("08:00")`, and every client sees the same answer.
:::

:::step{type=predict title="Guess first"}
:::question
Item 3 was claimed by report 7 before Lostdesk started. With your finished task, what does a new claim on item 3 give?
:::
- [ ] 200, because this is the first claim since the start
- [x] 409, saying report 7 claimed it
- [ ] 404
:::explain
The rule looks at the item's `claimed_by`, whoever set it and whenever. Item 3's is 7, so the answer is a 409 with
`"claimed_by_report": 7`.
:::
:::

:::step{type=task task=claim_conflict title="Your turn: 409 for a second claim" file="08-errors/main.py" line="36-37"}
Two parts:

1. In `claim_item`, when the item already has a `claimed_by`, raise `AlreadyClaimed(item_id, ...)` with the report
   that has it.
2. Register a handler for `AlreadyClaimed` that answers **409** with

```json
{"detail": "Item 1 is already claimed", "claimed_by_report": 12}
```

The first claim on an item still gives 200; an unknown item still gives 404. Claim item 1 twice in `/docs`, then press
**Check**.

The usual slip: only part 1. The second claim is stopped, but as `500 Internal Server Error`, with the traceback in
the terminal. The check sees the 500 and reminds you about the handler.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which status fits "a report for this item already exists, created a minute ago"?
:::
- [ ] 404 Not Found
- [x] 409 Conflict
- [ ] 500 Internal Server Error
:::explain
The request is well formed, but clashes with the current state of the data.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A route raises an exception that has no handler. What does the client get?
:::
- [ ] 400 Bad Request
- [x] 500 Internal Server Error
- [ ] Nothing: the connection hangs
:::explain
An unhandled exception is a crash as far as FastAPI knows. The details go to the server's log, never to the client.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why keep HTTP details out of `AlreadyClaimed` itself?
:::
- [ ] Exceptions cannot hold numbers
- [x] So the same rule can be raised from anywhere, and one handler decides how it looks on the web
- [ ] Because FastAPI forbids it
:::explain
The exception describes the problem in Lostdesk's terms; the handler translates it to HTTP once.
:::
:::

:::step{type=deep-dive title="Go deeper: headers on errors, and your own 422s"}
**Headers on errors.** `HTTPException(status_code=401, detail="...", headers={"WWW-Authenticate": "Bearer"})` sends
headers with an error. Chapter 17 needs exactly this.

**Changing the 422.** Validation errors are an exception too, `RequestValidationError`. Register a handler for it,
and every 422 in the app takes your shape, for example a shorter message for a phone app.

**A standard error shape.** RFC 9457, "Problem Details for HTTP APIs" (2023), suggests a common JSON shape for
errors: `type`, `title`, `status`, `detail`. Some companies adopt it so every API they own fails the same way;
FastAPI's `{"detail": ...}` is simpler, and also fine.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Set a route's success status with `status_code=`, using names like `status.HTTP_201_CREATED`.
- Choose between 200, 201, 204, 404 and 409 by what happened.
- Write your own exception class for a rule of your app, and raise it where the rule breaks.
- Register an exception handler that turns it into a `JSONResponse` with the right status and a clear body.

:::photo{src="/lesson-images/fastapi/fa-08-sketch.webp" alt="Sketchnote: Status codes and errors. The status code says what happened before anyone reads the body. Your own exceptions name your app's rules. Flow: the route finds a problem, it raises your exception, FastAPI finds the handler, the handler builds a JSONResponse, the client gets 409. Remember: 201 when a POST creates something; 409 when a request clashes with the data; An exception with no handler becomes a 500; Keep HTTP details in the handler." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 9: changing and removing items with PUT, PATCH and DELETE.
:::
