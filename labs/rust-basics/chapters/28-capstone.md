:::step{type=story title="Windwatch goes online"}
The last step for Windwatch: the turbines stop writing log files and **send** their readings over the network as they
happen, and the control room asks for a turbine's summary whenever it wants one. Windwatch becomes a **web service**,
running all day, answering many requests at once, and refusing nonsense such as a 2.5 MW turbine claiming 9,999 kW.

Everything in this course comes together here: structs and enums for the data, `Result` and `?` for errors, closures
and iterators for the numbers, `Arc` and `Mutex` (chapter 25's deep dive) for data shared by many requests, async from
chapter 26 for waiting on the network, and serde from chapter 23 for JSON. The web framework is **axum**, built by the
Tokio team.

:::mission
Accept readings with `POST /readings`, refusing impossible power with a 422, then serve `GET /turbines/{id}/summary`
with a 404 for a turbine nobody has heard from.
:::
:::

:::step{type=concept title="Routes, handlers, extractors" file="28-capstone/src/lib.rs" line="26-40"}
```rust
pub type Store = Arc<Mutex<HashMap<String, Vec<Reading>>>>;

Router::new()
    .route("/health", get(|| async { "ok" }))
    .route("/readings", post(add_reading))
    .route("/turbines/{id}/summary", get(summary))
    .with_state(store)
```

A **route** connects a method and a path to a **handler**, an ordinary `async fn`. What the handler needs from the
request, it names in its parameters, and axum fills them in: these are **extractors**.

| Parameter | Gives the handler |
|---|---|
| `State(store): State<Store>` | the shared store passed to `with_state` |
| `Json(reading): Json<Reading>` | the request body, parsed by serde into a `Reading`; a body that does not fit gets a 422 before your code runs |
| `Path(id): Path<String>` | the `{id}` part of the path, like `T12` |

The return type becomes the response: a `StatusCode` alone, `Json(value)` as a JSON body with 200, and
`Result<Json<Summary>, StatusCode>` as either. The store is an `Arc` (shared by every request, on any thread) around a
`Mutex` (one request at a time may change it).

:::diagram{name="rs-capstone"}
A POST and a GET travel through the router to their handlers, which lock the one shared store.
:::
:::

:::step{type=task task=post_reading title="Your turn: accept a reading" file="28-capstone/src/lib.rs" line="42-49"}
Finish `add_reading`: if `reading.power_kw < 0.0 || reading.power_kw > 2_500.0`, return
`StatusCode::UNPROCESSABLE_ENTITY`. Otherwise lock the store and add the reading under its turbine:
`store.lock().unwrap().entry(reading.turbine.clone()).or_default().push(reading);` and return `StatusCode::CREATED`.

Start the service:

```bash run
cd /workspace/28-capstone && cargo run -q
```

In a second terminal:

```bash run
curl -i -X POST localhost:3000/readings -H 'content-type: application/json' -d '{"turbine":"T12","wind_ms":7.5,"power_kw":140}'
```

Press **Check**. (Stop the service with Ctrl+C after each change, and start it again.)
:::

:::step{type=history title="From one web page to a web of services"}
:::before{title="Programs that could not talk"}
Before the web, two programs on different machines talked through formats and protocols invented for each pair,
documented in binders, and understood by nothing else.
:::

Tim Berners-Lee's **HTTP** (**1991**) was meant for fetching documents, and turned out to suit programs too: a method,
a path, a status code. Roy Fielding's thesis (**2000**) described the style of "resources at paths, changed with
methods" as **REST**. Douglas Crockford popularised **JSON** (early **2000s**) as a lighter format than XML, and it
became the language web services speak. Status **422 Unprocessable Content** comes from WebDAV (**2007**) and is
part of HTTP itself since **RFC 9110** (**2022**): "I understood your request, and it makes no sense". In Rust, Sean
McArthur's **hyper** (**2014**) gave a fast HTTP implementation, and **axum** (**2021**) put a friendly layer on top,
where a handler is just a function and its parameters say what it needs.

:::solved
**A typed web service.** Requests are parsed into structs before your code sees them, and a handler that forgets a case
does not compile.
:::

:::timeline
- **1991** HTTP.
- **2000** REST.
- **2014** hyper, HTTP for Rust.
- **2021** axum.
- **2022** RFC 9110: HTTP's meaning, written down again.
:::
:::

:::step{type=concept title="A summary, or a 404" file="28-capstone/src/lib.rs" line="51-58"}
```rust
let store = store.lock().unwrap();
let readings = store.get(&id).ok_or(StatusCode::NOT_FOUND)?;     // no readings: 404, and stop here
let total: f64 = readings.iter().map(|r| r.power_kw).sum();
let weak = readings.iter()
    .filter(|r| expected_kw(r.wind_ms) > 0.0 && r.power_kw < 0.8 * expected_kw(r.wind_ms))
    .count();
Ok(Json(Summary { turbine: id, readings: readings.len(), average_kw: total / readings.len() as f64, underperforming: weak }))
```

`ok_or` turns the `Option` from `get` into a `Result`, and `?` returns the `Err(StatusCode::NOT_FOUND)` as the
response: chapter 15's `?`, now deciding HTTP status codes. A reading **underperforms** when the power curve
(chapter 9) expects something and the turbine made less than 80% of it. `Summary` derives `Serialize`, so
`Json(summary)` is the whole JSON body.
:::

:::step{type=task task=summary_route title="Your turn: the summary route" file="28-capstone/src/lib.rs" line="51-58"}
Finish `summary` with the lines above: lock the store, get the readings or a 404, count the total and the weak readings,
and return `Ok(Json(Summary { ... }))`.

Restart the service, post a reading or two, then:

```bash run
curl -s localhost:3000/turbines/T12/summary
```

Press **Check**.
:::

:::step{type=try title="Windwatch, live"}
The service, then the control room's side:

```text
$ cargo run -q
Windwatch listening on http://localhost:3000
```

```text
$ curl -s localhost:3000/health
ok
$ curl -s -i -X POST localhost:3000/readings -H 'content-type: application/json' -d '{"turbine":"T12","wind_ms":7.5,"power_kw":140}' | head -1
HTTP/1.1 201 Created
$ curl -s -i -X POST localhost:3000/readings -H 'content-type: application/json' -d '{"turbine":"T12","wind_ms":7.9,"power_kw":305}' | head -1
HTTP/1.1 201 Created
$ curl -s -i -X POST localhost:3000/readings -H 'content-type: application/json' -d '{"turbine":"T12","wind_ms":8.1,"power_kw":9999}' | head -1
HTTP/1.1 422 Unprocessable Entity
$ curl -s -i -X POST localhost:3000/readings -H 'content-type: application/json' -d '{"turbine":"T12","wind":8.1}' | sed -n '1p;$p'
HTTP/1.1 422 Unprocessable Entity
Failed to deserialize the JSON body into the target type: missing field `wind_ms` at line 1 column 28
$ curl -s localhost:3000/turbines/T12/summary
{"turbine":"T12","readings":2,"average_kw":222.5,"underperforming":2}
$ curl -s -i localhost:3000/turbines/T99/summary | head -1
HTTP/1.1 404 Not Found
```

Two readings stored, 201 each. The 9,999 kW reading was refused by **your** rule; the reading with `wind` instead of
`wind_ms` was refused by **serde**, before your handler ran, with a message that names the missing field. The summary
averages 140 and 305 kW to 222.5, and both readings underperform: at 7.5 m/s the curve expects 312.5 kW (80% is 250),
at 7.9 m/s about 403 kW (80% is about 323). T12 is the turbine to send the North crew to. T99 has never sent anything: 404.
:::

:::step{type=predict title="Guess first"}
:::question
A turbine posts `{"turbine":"T07","wind_ms":"fast","power_kw":2100}`. What does it get back?
:::
- [ ] 201: the reading is stored
- [x] 422 from axum: `wind_ms` must be a number, so the body does not fit `Reading`
- [ ] The server crashes
:::explain
The `Json<Reading>` extractor runs serde first. Your handler only ever sees well-formed readings.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is the store an `Arc<Mutex<...>>` and not an `Rc<RefCell<...>>`?
:::
- [ ] It is shorter to write
- [x] Requests run on several threads at once; `Arc` and `Mutex` are the thread-safe versions
- [ ] axum requires a HashMap
:::explain
Chapter 25 showed `Rc` is not `Send`; the compiler would refuse `Rc` here for the same reason.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `?` do in `store.get(&id).ok_or(StatusCode::NOT_FOUND)?`?
:::
- [ ] It panics when the turbine is missing
- [x] It returns `Err(StatusCode::NOT_FOUND)` from the handler, which axum sends as a 404
- [ ] It retries the lookup
:::explain
The same `?` as chapter 15: the error leaves the function, and here the error is an HTTP status.
:::
:::

:::step{type=deep-dive title="Go deeper: a service in production"}
**Testing without a network.** The checks for this chapter call `app(store).oneshot(request)` (from the `tower` crate):
the whole router, run in memory, with no port opened. Every route can be tested that way in milliseconds.

**A real database.** The `HashMap` is lost when the service stops. `sqlx` talks to PostgreSQL asynchronously and
checks your SQL against the database when compiling.

**Layers.** `tower-http` adds logging, timeouts, compression and limits to every route with one line each:
`.layer(TimeoutLayer::new(...))`.

**Shipping it.** `cargo build --release` gives one file of a few megabytes; a container image with just that file is
tiny and starts in milliseconds.
:::

:::step{type=deep-dive title="You finished Rust from zero"}
Twenty-eight chapters ago Windwatch was one `println!`. Since then you have built:

| Part | Windwatch learned to... | With |
|---|---|---|
| First steps | compute a turbine's power and a day of readings | variables, types, functions, loops |
| Ownership | pass logs around without copies or leaks | ownership, borrowing, slices |
| Shaping data | describe turbines, states and faults | structs, enums, match, modules |
| Collections and errors | keep a farm's readings and report bad ones | Vec, HashMap, Result, ?, error types |
| Abstractions without cost | work with any sensor and any rule, fast | generics, traits, lifetimes, closures, iterators, tests |
| Real programs | run as a tool, in parallel, over the network, as a service | clap, Rc, threads, async, axum |

Where to go next: **The Rust Programming Language** (the free official book, "the Book") goes deeper into every
chapter here; **Rust by Example** is the same ideas as short programs; **Rustlings** is small exercises in your own
terminal. For async services, the **Tokio tutorial**. And read other people's code: ripgrep and the crates you used
here are open source, and written in the Rust you now know.
:::

:::step{type=recap}
You can now:

- build a web service with axum: routes, handlers and extractors;
- share state between requests with `Arc<Mutex<...>>`;
- answer with the right status code: 201, 404 and 422, with `?` turning errors into responses;
- trust serde to refuse malformed JSON before your code runs.

That is the end of the course. Windwatch is a real program now, and so is everything you write next.

:::photo{src="/lesson-images/rust/rs-28-notes.webp" alt="Handwritten notes about a web service: Router: path -> handler; State, Json, Path = extractors; Arc of Mutex: shared store; 201 created, 404, 422; ? turns errors into responses" ai="true"}
One page of notes for this chapter.
:::
:::
