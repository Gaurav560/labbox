:::step{type=story title="Why does matching an item take a second and a half?"}
When a clerk matches a found item to a passenger's report, Lostdesk sends the passenger a text message: "your laptop
bag has been found". The text-message gateway, like many outside services, is slow to answer. We timed the starter's
match route with curl:

```text
starter match: 1.508769s
```

A second and a half, every time, for the clerk to see "done", and all of it spent waiting for someone else's server.
Waiting is what web servers do most: for databases, for other APIs, for files. Today you learn the two tools FastAPI
gives you for it: **background tasks**, for work the client need not wait for, and **async**, for doing several
waits at once.

:::mission
Send the text message after the answer has gone, as a background task, and make `GET /search` run its two slow
searches at the same time with `asyncio.gather`.
:::
:::

:::step{type=concept title="Answer first, then do the rest" file="18-background/main.py" line="35-44"}
The clerk does not need the text message to have arrived; they need to know the match was recorded. So the message
can wait until **after** the answer:

```python
@app.post("/items/{item_id}/match/{report_id}")
def match(item_id: int, report_id: int, background_tasks: BackgroundTasks):
    ...
    background_tasks.add_task(send_text_message, report["contact"], message)
    return {"item_id": item_id, "report_id": report_id, "notice": "queued"}
```

- A parameter of type `BackgroundTasks` is filled in by FastAPI, like a dependency.
- `add_task(function, arguments...)` does not call the function; it adds it to a list.
- FastAPI sends the response, **then** runs the list.

We timed the solution the same way:

```text
solution match: 0.011568s
```

1.5 seconds became 11 milliseconds. Right after the answer, `outbox.log` did not exist yet; two seconds later it held
the message:

```text
to 98200 11111: Lostdesk: a grey laptop bag has been found. Bring ID to the Tech Park desk.
```
:::

:::step{type=task task=notify_background title="Your turn: a background task" file="18-background/main.py" line="35-38"}
Make `match` take `background_tasks: BackgroundTasks` and add `send_text_message` to it instead of calling it. Time
it with curl, before and after (start this chapter's server from `/workspace/18-background` first):

```bash run
curl -s -o /dev/null -w "%{time_total}s\n" -X POST localhost:8000/items/1/match/1
```

Then look at `outbox.log` a couple of seconds later, and press **Check**.
:::

:::step{type=history title="How Python learned to wait"}
For most of its life, Python ran one thing at a time per thread: while a function waited for the network, its
thread sat idle. Running many threads helps, but each costs memory, and a server with thousands of slow connections
runs out.

- **2009**: Node.js showed that one thread can serve thousands of connections if nothing ever blocks it: an **event
  loop** switches to other work whenever a task is waiting.
- **2014**: Python 3.4 adds `asyncio`, an event loop for Python.
- **2015**: Python 3.5 adds the keywords `async` and `await` (PEP 492), which make such code read like normal code.
- **2018**: FastAPI is built on Starlette and ASGI, so `async def` routes run on an event loop from the start.
:::

:::step{type=concept title="One loop, and what blocks it"}
An `async def` function can `await` something slow. At each `await`, it pauses and hands the event loop back, so the
loop can serve other requests meanwhile. Press Play:

:::diagram{name="fastapi-event-loop"}
await gives the loop back while waiting; time.sleep inside async def holds it, and every other request waits too.
:::

We measured it in the course image: a small app with three routes that each wait one second, and five requests sent
to each route at the same moment:

| Route | How it waits | 5 requests at once |
|---|---|---|
| `async def` | `await asyncio.sleep(1)` | 1.01 s |
| `async def` | `time.sleep(1)` | **5.01 s** |
| plain `def` | `time.sleep(1)` | 1.01 s |

The middle row is the classic mistake. `time.sleep` does not know about the event loop, so the loop is stuck for a
whole second, and the five requests are served one after another. The last row surprises people: FastAPI runs plain
`def` routes in a pool of threads, so blocking there only blocks that one thread.

The rule of thumb from FastAPI's docs: use `async def` when everything slow inside it is `await`ed (libraries made
for async, like `httpx.AsyncClient` or `asyncio.sleep`); otherwise use plain `def`, and FastAPI keeps the loop free
for you.
:::

:::step{type=concept title="Several waits at once" file="18-background/main.py" line="47-52"}
`GET /search` asks two slow services, each about 0.4 seconds. The starter awaits one, then the other:

```python
reports = await search_reports(q)
logs = await search_station_logs(q)
```

```text
starter search: 0.800590s
```

They do not depend on each other, so there is no reason to wait for the first before starting the second.
`asyncio.gather` starts several and waits for all of them together:

```python
reports, logs = await asyncio.gather(search_reports(q), search_station_logs(q))
```

It gives back their results **in the order you passed them**, whichever finished first. The solution's time:

```text
solution search: 0.401722s
```

As long as the slower of the two, not their sum.
:::

:::step{type=predict title="Guess first"}
:::question
Three independent lookups of 0.3, 0.5 and 0.2 seconds are run with `asyncio.gather`. About how long does it take?
:::
- [ ] 1.0 s
- [x] 0.5 s
- [ ] 0.2 s
:::explain
They wait at the same time, so the total is about the slowest one.
:::
:::

:::step{type=task task=parallel_search title="Your turn: asyncio.gather" file="18-background/main.py" line="49-52"}
Make `search` run both searches at the same time with `asyncio.gather`, keeping the answer the same:

```json
{"reports":["grey laptop bag"],"logs":["grey laptop bag seen at Tech Park"]}
```

```bash run
curl -s -w "\n%{time_total}s\n" "localhost:8000/search?q=laptop"
```

Then press **Check**: it times the route and wants well under 0.8 seconds.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
When does a task added with `background_tasks.add_task` run?
:::
- [ ] Before the route's code
- [ ] At the same time as the response
- [x] After the response has been sent
:::explain
That is the whole point: the client gets its answer without waiting for the task.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
An `async def` route calls `requests.get(...)`, a library that does not support await. What happens to other requests
while it waits?
:::
- [x] They wait too: the event loop is blocked
- [ ] Nothing: async makes it non-blocking
:::explain
Only `await`ing an async library gives the loop back. A blocking call inside `async def` behaves like the 5.01 s row.
Use a plain `def` route, or an async library.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
In which order does `asyncio.gather(a(), b())` give back its results?
:::
- [x] a's result, then b's, whichever finished first
- [ ] In the order they finished
:::explain
Like JavaScript's `Promise.all`: the order you asked in, so results line up with what you passed.
:::
:::

:::step{type=deep-dive title="Go deeper: when background tasks are not enough"}
Background tasks run inside the same server process, after the response. That is perfect for small, quick jobs.
They are the wrong tool when:

- **the work must not be lost**: if the server restarts, queued background tasks are gone. Important jobs go into a
  real queue (a Redis list, a database table) read by a separate worker, with tools like Celery or ARQ;
- **the work is long or heavy**: a report that takes minutes, or image processing that keeps the CPU busy, competes
  with requests for the same process.

**CPU-bound work and async.** `await` only helps while waiting. A loop that calculates for two seconds holds the event
loop just like `time.sleep`; such work belongs in a plain `def` route, a process pool, or a worker.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Move slow follow-up work after the response with `BackgroundTasks` and `add_task`.
- Explain the event loop: `await` gives it back; a blocking call in `async def` stops every request.
- Choose between `async def` (everything slow is awaited) and plain `def` (blocking libraries).
- Run independent waits at the same time with `asyncio.gather`, getting results in the order you asked.

:::photo{src="/lesson-images/fastapi/fa-18-sketch.webp" alt="Sketchnote: Async and background tasks. await gives the event loop back while waiting. Background tasks run after the answer has gone. Flow: the request arrives, the route answers, the response is sent, background tasks run, the client never waited. Remember: time.sleep inside async def blocks every request; Blocking libraries belong in plain def routes; asyncio.gather waits for several things at once; Important jobs need a real queue, not a background task." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 19: middleware that wraps every request, CORS, and settings from the environment.
:::
