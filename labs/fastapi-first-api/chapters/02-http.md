:::step{type=story title="What does the Preview tab actually send?"}
In chapter 1 you changed the Preview's path to `/items/3`, and a silver phone appeared. It felt like opening a page.
Underneath, the Preview and Lostdesk had a short, exact conversation in a language called **HTTP**, and every API you
will ever build or call speaks it.

Today you listen in on that conversation, line by line: what the request says, what the answer says, and what the
three-digit number at the top of every answer means. Then you add two routes that real APIs always have.

:::mission
Read real HTTP requests and responses with `curl`, then add `GET /health`, which says Lostdesk is alive, and
`GET /stations`, which lists each station with a found item.
:::
:::

:::step{type=history title="The story of HTTP"}
This black cube is the computer where the web began. In 1990, at CERN, the physics laboratory near Geneva, Tim
Berners-Lee wrote the first web server and the first browser on this NeXT computer, and the language they spoke to
each other: HTTP, the HyperText Transfer Protocol.

:::photo{src="/lesson-images/fastapi/first-web-server.webp" alt="A black NeXTcube computer and its monitor on a desk, with a keyboard, an open book and a sheet of paper; a handwritten red and white label is stuck on the cube" credit="Coolcaesar" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:First_Web_Server.jpg"}
The NeXTcube that Tim Berners-Lee used as the first web server, shown at CERN's Microcosm exhibition in 2005.
:::

:::timeline
- **1989** Tim Berners-Lee proposes a new information system at CERN; in 1990 he names it the WorldWideWeb.
- **1991** The first HTTP has one method, `GET`, and no status codes: the server sends the page or nothing.
- **1996** HTTP/1.0 (RFC 1945) adds status codes, headers and `POST`.
- **1997** HTTP/1.1 (RFC 2068) keeps connections open for many requests; it is what `curl` shows you today.
- **2015** HTTP/2: the same requests and answers, packed more efficiently.
- **2022** HTTP/3 (RFC 9114) runs over a new transport, QUIC; the meaning of methods and status codes stays the same.
:::

:::funfact
The label on the cube is handwritten: "This machine is a server. DO NOT POWER IT DOWN!!" For a while it was the
whole web, and switching it off would have switched the web off.
:::
:::

:::step{type=try title="Listen to a request with curl" file="02-http/main.py" line="24-28"}
Start this chapter's Lostdesk (stop chapter 1's first with **Ctrl + C**, or use a new terminal):

```bash run
cd /workspace/02-http && fastapi dev main.py --host 0.0.0.0 --port 8000 --root-path /preview/fastapi-first-api/8000
```

Then open a **second terminal** (the **+** button) and ask with **curl**, a command-line program that sends one
HTTP request and prints the answer. `-v` ("verbose") prints the conversation as well:

```bash run
curl -sv localhost:8000/items/3
```

The lines that matter (we cut curl's own notes about connecting):

```text
> GET /items/3 HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 200 OK
< date: Sat, 28 Nov 2026 05:53:46 GMT
< server: uvicorn
< content-length: 53
< content-type: application/json
<
{"id":3,"title":"silver phone","station":"Tech Park"}
```

Lines starting with `>` are what curl **sent**; lines starting with `<` are what Lostdesk **answered**. Read them in
the next step.
:::

:::step{type=concept title="A request and a response, line by line"}
**The request** is plain text:

1. The **request line**: a **method** (`GET`), a **path** (`/items/3`) and the version (`HTTP/1.1`).
2. **Headers**, one per line, `Name: value`: `Host` says which server is meant, `User-Agent` says who is asking,
   `Accept: */*` says "any kind of answer is fine".
3. An empty line, then a **body** if there is one. A `GET` has none; a `POST` carries its data here (chapter 5).

**The response** has the same shape:

1. The **status line**: `200 OK`, the code and its name.
2. Headers: `content-type: application/json` tells the client "the body is JSON", and `content-length: 53` says the
   body is 53 bytes long, so the client knows where it ends. Uvicorn and FastAPI wrote these for you.
3. An empty line, then the body: the JSON your function gave back.

The **method** says what the client wants to do. Lostdesk will use all five by chapter 9:

| Method | Means | Lostdesk example |
|---|---|---|
| `GET` | read, change nothing | `GET /items/3` |
| `POST` | create something new | `POST /reports` (chapter 5) |
| `PUT` | replace something whole | `PUT /items/3` (chapter 9) |
| `PATCH` | change part of something | `PATCH /items/3` (chapter 9) |
| `DELETE` | remove something | `DELETE /items/3` (chapter 9) |

:::diagram{name="fastapi-http"}
The client sends a request line, headers and maybe a body; the server answers with a status line, headers and a body.
:::
:::

:::step{type=try title="The wrong method" file="02-http/main.py" line="19-21"}
`/items` exists, but only for `GET`. What happens if you `POST` to it? `-i` makes curl print the response's status
line and headers above the body:

```bash run
curl -s -i -X POST localhost:8000/items
```

```text
HTTP/1.1 405 Method Not Allowed
date: Sat, 28 Nov 2026 05:53:46 GMT
server: uvicorn
allow: GET
content-length: 31
content-type: application/json

{"detail":"Method Not Allowed"}
```

Not 404: the path is real. **405 Method Not Allowed**, and a helpful header, `allow: GET`, listing the methods that
path does accept. FastAPI worked all of that out from your decorators. (`-X POST` sets the method; `-s` hides curl's
progress meter.)
:::

:::step{type=concept title="Status codes come in families"}
You never need to learn all the codes. The first digit tells you the family:

| First digit | Family | The ones you will meet |
|---|---|---|
| `2xx` | it worked | `200 OK`, `201 Created` (chapter 8), `204 No Content` (chapter 9) |
| `3xx` | look elsewhere | `307 Temporary Redirect` |
| `4xx` | the **client** made a mistake | `401` and `403` (chapter 17), `404`, `405`, `409` (chapter 8), `422` |
| `5xx` | the **server** failed | `500 Internal Server Error` |

That split matters in real work. A 4xx means "fix your request"; retrying the same request will fail again. A 5xx
means "our fault": the client may retry later, and someone at Lostdesk should be woken up. That is why chapter 1
insisted on a real 404 instead of `{"error": "not found"}` with status 200.

Our captures also show the names exactly as Uvicorn prints them: `200 OK`, `405 Method Not Allowed`, and for 422,
`HTTP/1.1 422 Unprocessable Entity`. (The newest HTTP standard, RFC 9110, renamed 422 to "Unprocessable Content"; the
number is what programs read.)
:::

:::step{type=example title="Worked example: worked out, not written down"}
This route is not in your project. It gives back every title, A to Z:

```python
@app.get("/titles")
def titles():
    return {"titles": sorted(item["title"] for item in FOUND.values())}
```

1. `FOUND.values()` gives every item; `item["title"] for item in ...` picks each title.
2. `sorted(...)` gives a new list, A to Z: `["black umbrella", "blue school bag", "bunch of keys", "silver phone"]`.
3. The list is **worked out on every request** from `FOUND`. Add an item, and the next answer includes it. Writing
   the list by hand would be wrong the moment the shelf changes.

Your first task uses the same idea for a count.
:::

:::step{type=task task=health title="Your turn: is Lostdesk alive?" file="02-http/main.py" line="31"}
Add `GET /health`. It gives back `{"status": "ok", "items": 4}`, where `4` is how many items `FOUND` holds right now.

Real APIs almost always have such a route. A **load balancer** (the program that spreads requests over several copies
of a server) or a monitoring tool calls it every few seconds: a quick 200 means "send me traffic"; no answer means
"take me out".

```bash run
curl -s localhost:8000/health
```

Then press **Check**. The usual slip: writing the number, `"items": 4`. It is right today, wrong tomorrow; the check
adds an item to `FOUND` and asks again. `len(FOUND)` counts the items every time.
:::

:::step{type=concept title="Each station once"}
Riverside has two items: an umbrella and a bunch of keys. A list of stations must still say Riverside **once**.

A **set** keeps each value once. A **set comprehension**, with curly braces, builds one in a single line:

```python
{item["station"] for item in FOUND.values()}    # {'Riverside', 'Old Market', 'Tech Park'}
```

But JSON has no sets, only lists. We tried giving back the set itself: FastAPI turned it into a list, in whatever
order the set happened to hold, `["Tech Park","Riverside"]` for one small example. An API that changes its order from
one run to the next is hard to use. `sorted(...)` turns the set into a list, A to Z, every time.
:::

:::step{type=task task=stations title="Your turn: the stations" file="02-http/main.py" line="34-35"}
Add `GET /stations`. It gives back each station that has a found item, once, A to Z:

```json
{"stations": ["Old Market", "Riverside", "Tech Park"]}
```

```bash run
curl -s localhost:8000/stations
```

Then press **Check**.

The usual slip, tried: `sorted([item["station"] for item in FOUND.values()])`, with square brackets. That is a list
comprehension, which keeps every value, and the answer says `["Riverside","Riverside","Tech Park"]` for two Riverside
items. Curly braces make a set.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A client sends `DELETE /items/3`, but Lostdesk only has `GET /items/{item_id}`. What status comes back?
:::
- [ ] 404 Not Found
- [x] 405 Method Not Allowed
- [ ] 500 Internal Server Error
:::explain
The path exists, so it is not 404. The method is wrong for that path: 405, with an `allow` header listing `GET`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which header tells the client how to read the body?
:::
- [ ] `server`
- [x] `content-type`
- [ ] `date`
:::explain
`content-type: application/json` says the body is JSON. A web page would say `text/html`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A request gets `503 Service Unavailable`. Whose problem is it, and is retrying sensible?
:::
- [ ] The client's; retrying will never help
- [x] The server's; retrying a little later may work
:::explain
Every 5xx means the server failed. A 4xx means the request itself is wrong, and sending it again unchanged fails
again.
:::
:::

:::step{type=deep-dive title="Go deeper: HTTPS, keep-alive and /openapi.json"}
**HTTPS** is HTTP inside an encrypted tunnel (TLS). The requests and responses are exactly what you saw today; the
tunnel stops anyone in between from reading or changing them. In production, a proxy in front of Uvicorn usually
handles it.

**Keep-alive.** HTTP/1.1 keeps the connection open after an answer, so the next request skips the setup. That is why
curl ends with "Connection #0 to host localhost left intact".

**/openapi.json** is the machine-readable description behind `/docs`. Ours lists five paths, and says the parameter
`item_id` is `"in": "path"`, `"required": true`, with `"type": "integer"`: your type hint, published. Tools read it
to generate client code for phone apps in other languages.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read an HTTP request (method, path, headers, body) and a response (status line, headers, body) with `curl -v` and
  `curl -i`.
- Pick the right method: `GET` to read, `POST` to create, `PUT` and `PATCH` to change, `DELETE` to remove.
- Tell the status families apart: 2xx worked, 4xx the client's mistake, 5xx the server's.
- Write routes whose answers are worked out from the data on every request, like `/health` and `/stations`.

:::photo{src="/lesson-images/fastapi/fa-02-sketch.webp" alt="Sketchnote: How a request travels. HTTP is plain text: a request has a method, a path, headers and maybe a body; a response has a status code, headers and a body. Flow: method and path, request headers, the server runs the route, status line, headers and JSON body. Remember: GET reads, POST creates, PUT and PATCH change, DELETE removes; 2xx worked, 4xx the client's mistake, 5xx the server's; 405 means the path exists but not for that method; work answers out from the data, never write them down." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 3: path and query parameters, so one route can answer many questions.
:::
