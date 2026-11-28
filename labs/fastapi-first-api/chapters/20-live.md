:::step{type=story title="How does a screen know something new was found?"}
Every station will get a screen in its lost-property corner, showing the newest finds across the network. A
passenger glancing at it should see a phone the moment a clerk logs it, not five minutes later.

Departure boards had the same job long before screens: this split-flap board in Philadelphia rattles through its
letters whenever a train changes, and everyone looking up sees it at once. The photo caught it halfway through a
change.

:::photo{src="/lesson-images/fastapi/solari-board.webp" alt="A black split-flap departure board listing trains, their numbers and destinations in white letters; one line is caught mid-change with jumbled characters, and a yellow line of text runs across the bottom" credit="Foxtod" license="CC0" source="https://commons.wikimedia.org/wiki/File:Solari_board_at_Amtrak_30th_Street_Station_in_Philadelphia.jpg"}
A split-flap board at Amtrak's 30th Street Station, Philadelphia, caught mid-change.
:::

So far, every exchange with Lostdesk has been one request and one answer. A screen could ask `GET /items` every few
seconds ("polling"), but most of those requests would bring nothing new. Today Lostdesk **pushes** instead: the screen
opens one long-lived request, and Lostdesk writes each new find into it as it happens.

:::mission
Add `GET /items/feed`, a stream of Server-Sent Events, one per found item, with event names and ids so a screen that
reconnects carries on where it stopped.
:::
:::

:::step{type=concept title="Server-Sent Events"}
**Server-Sent Events** (SSE) are a simple, old idea built into every modern browser: the server answers one normal
HTTP request with the type `text/event-stream`, keeps the connection open, and writes **events** into it, one after
another, as plain text. Opera shipped an early version in 2006; it is now part of the HTML standard, and browsers
read it with a built-in object called `EventSource`.

| | Polling | Server-Sent Events | WebSockets |
|---|---|---|---|
| who speaks | the client asks again and again | the server pushes | both, either way |
| what it is | ordinary requests | one long HTTP response | a different protocol after an upgrade |
| reconnects by itself | not needed | yes, with `Last-Event-ID` | no, your code must |
| good for | rare changes | feeds, notifications, progress | chat, games, editing together |

A lost-property feed only flows one way, from Lostdesk to screens, which is exactly SSE's job. FastAPI added SSE to
its main tutorial recently, with `fastapi.sse`; WebSockets are in its advanced guide.
:::

:::step{type=concept title="A stream is a generator" file="20-live/main.py" line="31-33"}
In FastAPI, a stream is a function that `yield`s instead of `return`ing, with `response_class=EventSourceResponse`.
This is the solution's version:

```python
@app.get("/items/feed", response_class=EventSourceResponse)
async def feed(since: int | None = None, ...) -> AsyncIterable[ServerSentEvent]:
    ...
    for item in list(FOUND.values()):
        if item["id"] > since:
            yield ServerSentEvent(data=item, event="found", id=str(item["id"]))
```

Each `yield` sends one event at once, before the function has finished. `ServerSentEvent(data=...)` turns `data` into
JSON; you can also `yield` a dictionary or a model directly, and FastAPI wraps it as an event with only `data`. We
asked the solution with `curl -N` (`-N`: print each piece as it arrives):

```text
$ curl -s -i -N "localhost:8000/items/feed?since=1"
HTTP/1.1 200 OK
...
content-type: text/event-stream; charset=utf-8
cache-control: no-cache
x-accel-buffering: no
transfer-encoding: chunked

event: found
data: {"id": 2, "title": "blue school bag", "station": "Old Market"}
id: 2

event: found
data: {"id": 3, "title": "silver phone", "station": "Tech Park"}
id: 3
```

Each event is a few `name: value` lines and an empty line. `cache-control: no-cache` and `x-accel-buffering: no` ask
proxies not to hold the stream back; `transfer-encoding: chunked` means the length is not known in advance, because
the answer is still being written.
:::

:::step{type=task task=sse_feed title="Your turn: the feed" file="20-live/main.py" line="31-32"}
Add `GET /items/feed` with `response_class=EventSourceResponse`: an `async def` that yields one `ServerSentEvent`
(data: the item) for each item whose id is greater than the query parameter `since` (0 when not given).

Start this chapter's server from `/workspace/20-live`, then in a second terminal:

```bash run
curl -s -N "localhost:8000/items/feed?since=1"
```

Log a new item in `/docs`, and ask again with `since=3`: there it is. Then press **Check**.
:::

:::step{type=concept title="Event names, ids, and carrying on"}
A screen's connection will drop: a router restarts, a laptop sleeps. `EventSource` then reconnects by itself, and if
the events had ids, it sends the last id it saw in a header, `Last-Event-ID`. A good feed uses it to carry on after
that event, so nothing is missed and nothing is shown twice. Press Play:

:::diagram{name="fastapi-sse"}
One long response, one event per item; after a drop, the browser reconnects with Last-Event-ID and the feed carries on.
:::

On the screen's side, a few lines of JavaScript (this is browser code, not part of Lostdesk):

```js
const feed = new EventSource("/items/feed");
feed.addEventListener("found", (e) => showItem(JSON.parse(e.data)));
```

`addEventListener("found", ...)` listens for events named `found`, the `event:` line. We sent the solution
`Last-Event-ID: 2` with no `since`, and it began at item 3:

```text
event: found
data: {"id": 3, "title": "silver phone", "station": "Tech Park"}
id: 3
```
:::

:::step{type=predict title="Guess first"}
:::question
A screen received events with ids 1 to 7, then lost its connection. What does it send when it reconnects?
:::
- [ ] Nothing: it starts again from the first item
- [x] The header Last-Event-ID: 7
- [ ] A query string ?since=7
:::explain
`EventSource` does this by itself, as long as the events had ids. Your feed must read the header.
:::
:::

:::step{type=task task=sse_resume title="Your turn: names, ids, and Last-Event-ID" file="20-live/main.py" line="35-36"}
Give each event the name `found` and the item's id (as text), and when `since` is not given, start after the
`Last-Event-ID` header (a parameter `last_event_id: Annotated[str | None, Header()] = None`, chapter 10's trick).

```bash run
curl -s -N localhost:8000/items/feed -H "Last-Event-ID: 2"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What makes a FastAPI route a stream instead of one answer?
:::
- [x] It yields events, with response_class=EventSourceResponse
- [ ] It returns a very long list
- [ ] It runs in the background
:::explain
Each `yield` is sent as soon as it happens; the response ends when the function does.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A chat where both sides type at any time. SSE or WebSockets?
:::
- [ ] SSE
- [x] WebSockets
:::explain
SSE flows one way, server to client. Two-way, low-delay conversation is what WebSockets are for.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does an SSE event need an `id`?
:::
- [ ] Browsers refuse events without one
- [x] So a reconnecting client can say which event it saw last
:::explain
Without ids there is no `Last-Event-ID`, and a reconnecting screen would have to start again from the beginning.
:::
:::

:::step{type=deep-dive title="Go deeper: a feed that never ends"}
This chapter's feed sends what it has and ends, which is easy to test. A real live feed keeps going:

```python
@app.get("/items/live", response_class=EventSourceResponse)
async def live(request: Request, since: int = 0) -> AsyncIterable[ServerSentEvent]:
    while not await request.is_disconnected():
        for item in [i for i in FOUND.values() if i["id"] > since]:
            since = item["id"]
            yield ServerSentEvent(data=item, event="found", id=str(item["id"]))
        await asyncio.sleep(1)
```

The `await asyncio.sleep(1)` matters: it gives the event loop back (chapter 18), so one server can hold thousands of
open screens. Better still, instead of checking every second, wait on an `asyncio.Queue` that `POST /items` puts new
items into. Proxies and load balancers close connections that stay silent too long, so long-lived streams send a
small comment line now and then, which `EventSource` ignores. FastAPI does it for you: when a stream has been silent
for 15 seconds, it sends the line `: ping` (we read this in FastAPI 0.165's own source code). You can also send one
yourself with `ServerSentEvent(comment="ping")`.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Choose between polling, Server-Sent Events and WebSockets.
- Write an SSE route: `response_class=EventSourceResponse` and an `async def` that yields `ServerSentEvent`s.
- Read the `text/event-stream` format: `event:`, `data:`, `id:` and an empty line.
- Name events and give them ids, and carry on after `Last-Event-ID` when a client reconnects.

:::photo{src="/lesson-images/fastapi/fa-20-sketch.webp" alt="Sketchnote: Live updates with SSE. Server-Sent Events keep one HTTP response open and write events into it as they happen, server to client. Flow: the screen opens the stream, text/event-stream, one event per item, the connection drops, reconnect with Last-Event-ID. Remember: yield events with response_class=EventSourceResponse; An event: event, data, id, then an empty line; Ids let a client carry on after a drop; Two-way talk needs WebSockets instead." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 21: the capstone. Claims, a whole flow end to end, and running Lostdesk for real.
:::
