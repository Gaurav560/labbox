:::step{type=story title="Where is my order?"}
:::character{name="Priya" role="Founder, Thali House"}
Every day at 12:45 the phone does not stop: "Where is our lunch?" Our riders already update the
status on their phones. If offices could ask an API, my team could finally eat their own lunch.
:::

:::mission
Build two endpoints: look up one order, and place a new one, with the right status codes.
:::
:::

:::step{type=concept title="Routes in Express"}
An Express **route** is a method, a path and a function that gets the request and the response:

```javascript
app.get("/outlets/:city", (req, res) => {
  res.json({ city: req.params.city });
});
```

`:city` captures that part of the URL into `req.params`. `res.status(404).json(...)` sets the status
code first. `express.json()` reads JSON bodies into `req.body`.
:::

:::step{type=predict title="Guess first"}
:::question
`ORDERS` has a key `1`. In `GET /orders/1`, is `req.params.id` the number `1`?
:::
- [ ] Yes, Express converts numbers
- [x] No, it is the string `"1"`
- [ ] It is undefined until you parse it
:::explain
Everything in a URL is text, so `req.params.id` is `"1"`. Plain object keys are strings too, so
`ORDERS["1"]` finds it, but `=== 1` would not.
:::
:::

:::step{type=try title="Run it and look"}
Start the server, then open the **Preview** tab (it opens on `/orders/1`):

```bash run
node server.js
```

You will see an error page for now: there is no `/orders/:id` route yet. Stop the server with Ctrl+C
before changing the code, and start it again after.
:::

:::step{type=task task=get_order title="Look up an order"}
Add `GET /orders/:id`. It answers the order as JSON, or **404** with `{"error": "..."}` when there is no
such order. Try `/orders/1` and `/orders/999` in the Preview.
:::

:::step{type=example title="Testing a POST"}
Browsers send GET requests from the address bar. For POST, use `curl` in the terminal:

```bash
curl -s -X POST localhost:3000/orders -H 'content-type: application/json' \
  -d '{"items": ["poha"], "area": "Kothrud"}'
```

`-i` instead of `-s` also shows the status line, like `HTTP/1.1 201 Created`.
:::

:::step{type=task task=create_order title="Place an order"}
Add `POST /orders`. A valid body has `items` (a non-empty list of dish names) and `area` (text).
Answer **201** with the new order `{id, items, area, status: "preparing"}`, or **400** with an error.

:::mistake
Answering 200 with `{"error": ...}` looks fine to a person, but every program calling you will think the
order was placed. The status code is the answer; the body explains it.
:::
:::

:::step{type=recap}
- A route is a method, a path and a handler; `:id` lands in `req.params` as text.
- `res.status(code).json(body)`: 200 found, 201 created, 400 bad input, 404 not found.
- Validate input before you store it.
:::
