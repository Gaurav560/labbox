:::step{type=story title="A menu that answers"}
:::character{name="Ravi" role="Owner, Ravi's Tapri"}
Every morning I send a photo of the menu board on WhatsApp. People still ask
"bhaiya, filter coffee kitne ka?" all day. My nephew built a bot, but it needs an
API to read the menu from. Can you make one?
:::

:::mission
Build a small web API with two endpoints: the whole menu, and the price of one item.
:::
:::

:::step{type=concept title="Routes are just functions"}
In FastAPI, a **route** is a normal Python function with a decorator above it.
The decorator says which URL and HTTP method it answers:

```python
@app.get("/hello")
def hello():
    return {"message": "namaste"}
```

When a request for `GET /hello` arrives, FastAPI calls `hello()` and sends back
what it returns.
:::

:::step{type=predict title="Guess first"}
:::question
`hello()` returns a Python dict. What does the caller actually receive?
:::
- [ ] A Python dict, through the network
- [x] JSON text: `{"message": "namaste"}`
- [ ] An error, because routes must return strings
:::explain
FastAPI turns the dict into JSON for you and sets the `Content-Type: application/json`
header. That is why APIs written in any language can read it.
:::
:::

:::step{type=try title="Run it and look"}
Start the server, then open the **Preview** tab next to Terminal:

```bash run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see the welcome message. `--reload` restarts the server every time you
save, so keep it running while you work.

:::tip
`--host 0.0.0.0` matters: it makes the server listen for the Preview, not only inside
the machine.
:::
:::

:::step{type=task task=menu title="List the menu"}
Add `GET /menu`, returning every item name from `MENU`, sorted A to Z:

```json
{"items": ["bun maska", "cold coffee", "filter coffee", "vada pav"]}
```

Check it in the Preview tab: change the address to `/menu`.
:::

:::step{type=example title="Values from the URL"}
Curly braces in the path become a function parameter:

```python
@app.get("/outlets/{city}")
def outlet(city: str):
    return {"city": city}
```

To say "not found", raise an exception instead of returning:

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="No outlet there yet")
```
:::

:::step{type=task task=price title="Price of one item"}
Add `GET /menu/{item}`. `/menu/filter coffee` returns `{"item": "filter coffee", "price": 20}`.
An item that is not on the menu (try `/menu/pizza`) returns **404**.

:::mistake
Returning `{"error": "not found"}` with status 200 looks fine in a browser, but every
program calling your API will think it worked. Use the right status code.
:::
:::

:::step{type=recap}
- A route is a function with a decorator such as `@app.get("/menu")`.
- Return a dict and FastAPI sends JSON.
- `{item}` in the path becomes a parameter; `HTTPException(404)` says "not found".
:::
