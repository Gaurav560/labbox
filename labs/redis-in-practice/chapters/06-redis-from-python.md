:::step{type=story title="From the terminal to the app"}
Welcome to Part 2. So far you have talked to Redis yourself, one command at a time, in `redis-cli`. But customers
never type Redis commands. The Basket **app** does, thousands of times a second, from Python code running on a
server.

In this part you build that app's backend, one chapter folder at a time: customer profiles, cached prices, a
report of what the cache saves, protection against stampedes, safe counters, locks and order streams. Every
chapter's code lives in its own folder, like `06-redis-from-python/`, and the check calls your running app over
HTTP exactly the way the real Basket app would.

This chapter starts with the basics: connecting from Python, what Redis answers look like there, and the one
hidden cost that surprises everyone the first time: the **round trip**.

:::mission
Serve customer profiles straight from Redis, and make a 2000 row import fast by sending it in one go.
:::
:::

:::step{type=concept title="Talking to Redis from Python" file="06-redis-from-python/hello_redis.py" line="7-18"}
Python talks to Redis through a **client library** called `redis-py` (you import it as `redis`). It is already
installed in this lab. Look at `hello_redis.py`, on the right.

**Line 10** opens the connection:

```python
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"))
```

`host` is where Redis runs. In this lab the Redis server is reachable under the name `redis`, which the
environment variable `REDIS_HOST` also holds. (In production it would be an address like
`basket-cache.internal`.) The default port, 6379, needs no mention.

You make this object **once**, at the top of your program, and use it everywhere. Behind it, redis-py keeps a
small **pool** of open connections and reuses them, because opening a new network connection for every command
would cost more than the command itself.

**Lines 12 and 13** are the `SET` and `GET` you know, as Python methods: every Redis command is a method with the
same name in lower case (`r.incr`, `r.hset`, `r.zadd`, and so on).

Now the surprise. By default, redis-py gives you **bytes**, not text, because a Redis value can be any bytes at
all. **Line 16** makes a second client with `decode_responses=True`, which turns every answer into a normal Python
`str`. The Basket apps always use that.

**Line 18** asks for a key that does not exist. In `redis-cli` that was `(nil)`; in Python it is `None`.
:::

:::step{type=try title="Run it" file="06-redis-from-python/hello_redis.py" line="13-18"}
Go into this chapter's folder and run it:

```bash run
cd /workspace/06-redis-from-python && python3 hello_redis.py
```

```text
b'Hello from Python'
Hello from Python
None
```

1. The first line is **bytes**: the little `b'...'` gives it away. Forget `decode_responses=True` in a real app,
   and you end up comparing `b'gold' == 'gold'`, which is `False`, and wondering why nothing matches.
2. The second line is the same value as a normal `str`.
3. The third is `None`: no such key.

Try changing line 12 to store your own name, and run it again.
:::

:::step{type=example title="Worked example: a hash, as Python sees it"}
Chapter 4's hash commands work the same way in Python. Here is what redis-py answered in this lab for Asha's
profile, and for a customer that does not exist (this code is only to read; it is not in your project):

```python
r = redis.Redis(host="redis", decode_responses=True)
print(r.hgetall("customer:42"))
print(r.hgetall("customer:7"))
print(type(r.hget("customer:42", "orders")))
```

```text
{'name': 'Asha', 'orders': '8', 'tier': 'gold'}
{}
<class 'str'>
```

Three lessons in three lines:

1. `hgetall` gives a real Python **dict**, not chapter 4's flat list of pairs.
2. A hash that does not exist gives an **empty dict**, `{}`, not `None` and not an error. So "is there such a
   customer?" is simply `if not profile:`.
3. Every value is a **string**, even `orders`. Redis stores text; turning `'8'` into the number `8` is your job,
   with `int(...)`.

Point 3 matters for an API: a client that receives `"orders": "8"` and adds one gets `"81"` in JavaScript. Always
give numbers their real type before they leave your app.
:::

:::step{type=try title="Start the app" file="06-redis-from-python/app.py" line="18-22"}
Now the real app. `app.py` is a small web API built with **FastAPI**: each function with `@app.get(...)` or
`@app.post(...)` above it answers one URL. Start it in the terminal, from this chapter's folder:

```bash run
cd /workspace/06-redis-from-python && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

`uvicorn` is the web server that runs FastAPI apps; `app:app` means "the `app` object in `app.py`"; `--reload`
restarts it whenever you save the file. It prints:

```text
INFO:     Started server process [975]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Leave it running, and open a **second terminal** (the + button) to call it. First give Asha a profile, then ask
the API for it:

```bash run
redis-cli HSET customer:42 name Asha orders 8 tier gold
```

```bash run
curl -i localhost:8000/customers/42
```

```text
HTTP/1.1 501 Not Implemented
...
{"detail":"Not written yet"}
```

**501** means "not implemented": look at lines 18 to 22 on the right, the function only raises an error. That is
your first task. (You can also open the API's own page, **Basket API** in the preview, to try every endpoint in
the browser.)
:::

:::step{type=predict title="Guess first"}
:::question
`r.hgetall("customer:7")` runs for a customer who does not exist. What does it give?
:::
- [ ] `None`
- [x] `{}`, an empty dict
- [ ] It raises an exception
:::explain
For a missing hash, `hgetall` answers an empty dict. Test it with `if not profile:` and answer 404.
:::
:::

:::step{type=task task=profile_api title="Your turn: profiles from Redis"}
Write `GET /customers/{cid}` in `app.py`:

1. Read the whole hash `customer:<cid>` (for example `customer:42`) with one command.
2. If it is empty, raise `HTTPException(status_code=404, detail=...)`.
3. Otherwise return `{"id": cid, "name": ..., "orders": ..., "tier": ...}`, with `orders` as an **int**.

Save the file (uvicorn reloads it), and try `curl localhost:8000/customers/42` and `/customers/7`. Asha should come
back with `"orders": 8`, a number, and customer 7 should get a 404. Press **Check**: it creates a customer of its own
with a random id, and asks your API.
:::

:::step{type=concept title="Round trips: the hidden cost" file="06-redis-from-python/app.py" line="25-33"}
Look at `import_sales()` on the right. It reads `data/sales.csv`, 2000 rows of "store, item, units", and stores
each row in the hash `sales:import` with `r.hset(...)`, one call per row.

Each call is a **round trip**: Python sends one command over the network, then **waits** for Redis to answer,
then sends the next. Remember chapter 1: Redis needs a microsecond or two to do the work, and the rest of the
round trip is the network. So this loop spends almost all its time waiting.

Here is what it cost in this lab, measured three times, next to what Redis itself counted:

| Run | Time for POST /import | Network reads Redis made |
|---|---|---|
| 1 | 67 ms | 2003 |
| 2 | 75 ms | 2001 |
| 3 | 54 ms | 2001 |

Two thousand reads: one for every row. 60 milliseconds sounds harmless, but this lab's Redis sits on the same
machine as your app, a few hundredths of a millisecond away. In a real data centre a round trip is about
**0.5 ms** (chapter 1's ladder), and between cloud regions it can be 50 ms:

| Where Redis is | One round trip | 2000 rows, one by one |
|---|---|---|
| This lab (same machine) | about 0.03 ms | about 60 ms |
| Same data centre | about 0.5 ms | about **1 second** |
| Another region | about 50 ms | about **100 seconds** |

The fix is a **pipeline**: put all the commands in a queue on your side, send them **together**, and read all the
answers together. One wait instead of two thousand.

:::diagram{name="round-trips"}
One by one, every command waits for its answer; a pipeline sends them all, then reads all the answers at once.
:::
:::

:::step{type=example title="Worked example: a pipeline of reads"}
A pipeline in redis-py looks like this. Here it reads four prices at once (only to read; not in your project):

```python
pipe = r.pipeline(transaction=False)
for item in ["rice", "dal", "eggs", "paneer"]:
    pipe.get(f"price:{item}")
print(pipe.execute())
```

```text
['60', '120', '84', None]
```

1. `r.pipeline(transaction=False)` makes an empty pipeline. `transaction=False` says "just batch these"; the
   deep dive explains what a transaction would add.
2. Inside the loop, `pipe.get(...)` sends **nothing** yet. It only adds the command to the queue.
3. `pipe.execute()` sends all four commands in one go, waits once, and returns all the answers as a list, in the
   same order as the commands. `paneer` has no cached price, so its answer is `None`.

To feel the difference, this lab ran 2000 plain `SET`s both ways, from Python:

```text
72.6 ms one by one, 10.1 ms pipelined
```

Seven times faster here, on a network that is nearly free. On a real network the gap grows to hundreds of times,
because the pipeline pays the round trip once.
:::

:::step{type=task task=bulk_import title="Your turn: a fast import"}
Make `import_sales()` in `app.py` send its 2000 `hset` calls in **one** pipeline:

1. Before the loop, make a pipeline from `r` (no transaction needed).
2. Inside the loop, call `hset` on the **pipeline** instead of on `r`.
3. After the loop, execute the pipeline once.

Keep the same key and fields. Try it with `curl -X POST localhost:8000/import`, then press **Check**: it counts how
many network reads Redis makes while your import runs. It should be a handful, not 2000.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Inside a pipeline loop you write `value = pipe.get("price:rice")` and then `print(value)`. What does it print?
:::
- [ ] The price
- [x] The pipeline object itself: nothing has been sent yet
- [ ] `None`
:::explain
Commands on a pipeline are only queued. The answers arrive all together from `pipe.execute()`, as a list in the
order the commands were added.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Your app runs in one data centre and Redis in another, 40 ms away. A page makes 25 Redis calls one by one. How
long does the page spend waiting for Redis?
:::
- [ ] About 40 ms
- [x] About a second: 25 round trips of 40 ms each
- [ ] Almost nothing, because Redis is fast
:::explain
Redis being fast does not shorten the network. 25 trips of 40 ms is a full second. Pipelining them, or keeping
Redis close to the app, turns that into one trip.
:::
:::

:::step{type=deep-dive title="Go deeper: pipelines, transactions and big batches"}
**Pipeline or transaction?** `r.pipeline()` with the default `transaction=True` wraps the commands in `MULTI` and
`EXEC`. Redis then runs them as one block: no other client's command can run in the middle. That is a different
promise from a plain pipeline, which only saves round trips: other clients' commands may run between yours. Use a
transaction when the commands must happen together (move stock from one store to another), and a plain pipeline
when you only want speed.

**A Redis transaction does not roll back.** If one command inside `MULTI` fails (say, `INCR` on a name), the
others still run. Redis checks for mistakes you can see before running, like a wrong number of arguments, but
not for every runtime error. For "check, then change, all or nothing" you will use a script in chapter 10.

**Batch size.** A pipeline of a million commands makes Redis build a million answers in memory before sending
them. Teams send big imports in chunks, say 1,000 to 10,000 commands per `execute()`.

**Connections.** Each `redis.Redis` object keeps a pool of connections, by default growing as needed. In a web
app with many threads, one shared client is right; creating a client per request opens and closes a connection
every time, which costs a round trip (or several, with TLS) on its own. For asyncio apps there is
`redis.asyncio.Redis`, with the same methods behind `await`.
:::

:::step{type=recap}
You can now:

- connect from Python with `redis.Redis(..., decode_responses=True)`, and read answers as `str`, `dict` or `None`;
- serve an API endpoint from a Redis hash, with proper types and a 404 for missing data;
- explain why round trips, not Redis, usually decide how long a batch takes;
- send many commands at once with a pipeline, and know when you would want a transaction instead.

Next, chapter 7: the reason most apps use Redis in the first place, caching.

:::photo{src="/lesson-images/redis/redis-06-notes.webp" alt="Handwritten notes about redis from python: decode_responses=True; missing key = None; hgetall gives () if missing; every round trip waits; pipeline: send all, wait once" ai="true"}
One page of notes for this chapter.
:::
:::
