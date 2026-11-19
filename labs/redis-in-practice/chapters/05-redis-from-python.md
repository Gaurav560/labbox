:::step{type=story title="From the terminal to the app"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
You can talk to Redis by hand. Our customers cannot: they talk to the app, and the app talks to
Redis thousands of times a minute. This week the app learns to read profiles straight from Redis,
and our nightly sales import, which takes far too long, gets fixed.
:::

:::mission
Serve customer profiles from Redis through the API, and make a 2000-row import fast.
:::
:::

:::step{type=concept title="The client, and what comes back"}
In Python, the `redis` package has one method per command: `r.set`, `r.get`, `r.hgetall`,
`r.incr`. The app creates one client and reuses it; under the hood it keeps a **pool** of open
connections, because opening a connection for every command would cost more than the command.

Redis only stores **strings**. With `decode_responses=True` you get `str` back instead of `bytes`,
but a number is still text: `r.hget("customer:42", "visits")` returns `"8"`. Turning it into an
`int` is your job, and forgetting is a classic bug.

A missing key comes back as `None` from `get`, and as an empty dict from `hgetall`.
:::

:::step{type=predict title="Guess first"}
:::question
`customer:7` does not exist. What does `r.hgetall("customer:7")` return in Python?
:::
- [ ] `None`
- [x] `{}`, an empty dict
- [ ] It raises a `KeyError`
:::explain
Redis treats a missing hash as an empty one, so `HGETALL` returns no fields and the client gives you
`{}`. Check `if not data:` to answer 404, not `if data is None`.
:::
:::

:::step{type=try title="Start the app"}
Start the app in this terminal. Leave it running: `--reload` restarts it every time you save.

```bash run
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

In a **second terminal tab**, Asha from chapter 3 is still in Redis:

```bash run
curl -s localhost:8000/customers/42
```

It answers 501, "not written yet". That is your first task.
:::

:::step{type=task task=profile_api title="Profiles from Redis"}
Make `GET /customers/{cid}` in `app.py` read the hash `customer:<cid>` and answer:

```json
{"id": 42, "name": "Asha", "visits": 8, "tier": "gold"}
```

`visits` must be a **number**. A customer that does not exist gets a **404**.
:::

:::step{type=concept title="Round trips: the hidden cost"}
Every command is a **round trip**: the app sends it, waits, and Redis answers. Redis itself needs a
few microseconds. The network needs far more: in production, Redis usually runs on another machine
about **0.5 ms** away.

So 2000 commands, one at a time, cost 2000 round trips: about **one second** of pure waiting.

A **pipeline** sends many commands in one go and reads all the answers in one go:

```python
pipe = r.pipeline(transaction=False)
for row in rows:
    pipe.hset("sales:import", row["key"], row["value"])
pipe.execute()          # one round trip for all of them
```
:::

:::step{type=task task=bulk_import title="A fast import"}
`POST /import` loads `data/sales.csv` (2000 rows) into the hash `sales:import`. It works, but it
makes one round trip per row. Make it fast **without changing what it stores**.

The check counts the round trips your import makes to Redis.

```bash
curl -s -X POST localhost:8000/import
```
:::

:::step{type=deep-dive title="Pipelines, transactions and big batches"}
`r.pipeline()` with the default `transaction=True` wraps the batch in `MULTI` and `EXEC`, so Redis
runs it as one block with nothing in between. With `transaction=False`, other clients' commands may
run in the middle; that is fine for an import, and slightly cheaper.

Pipelines are not free either: Redis must keep every answer in memory until the batch is done. For a
million rows, send batches of a few thousand, not one giant pipeline.

And a pipeline cannot use an answer *inside* the same batch (you cannot read a value, then decide).
When the next command depends on the last one, you need a script: chapter 7.
:::

:::step{type=recap}
- One client, reused: it keeps a pool of connections for you.
- Redis returns strings: convert numbers yourself; a missing hash is `{}`, a missing key is `None`.
- Each command costs a network round trip; in production that is about 0.5 ms.
- A pipeline sends many commands in one round trip: 2000 rows in milliseconds, not a second.
:::
