:::step{type=story title="1.5 seconds per price"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Our app asks the old billing system for a price on every screen, and every call takes 1.5 seconds.
Prices change maybe once a day. And yesterday a bot pressed "Send OTP" four thousand times on one
number, and we paid for every SMS.
:::

:::mission
Put a Redis cache in front of the slow price lookup, and limit OTPs to 3 a minute per phone.
:::
:::

:::step{type=concept title="Cache-aside and counters"}
**Cache-aside** is the most common way to use a cache:

1. Look for the answer in Redis.
2. Found it (a **hit**)? Return it.
3. Not there (a **miss**)? Do the slow work, store the answer in Redis with a TTL, return it.

The TTL decides how stale an answer can get.

A **rate limiter** needs a counter per caller that resets on its own. `INCR` adds one to a key
(and creates it at 0 first if it is missing), and `EXPIRE` makes the counter go away after a window.

In Python, the `redis` package has a method for every command: `r.get`, `r.set`, `r.incr`, `r.expire`.
:::

:::step{type=predict title="Guess first"}
:::question
Redis holds `price:samosa` = `20`. In Python, what does `r.get("price:samosa")` return?
:::
- [ ] The number `20`
- [x] The string `"20"`
- [ ] `None`, because it is a number
:::explain
Redis stores strings. You get `"20"` back (as text, because the app uses `decode_responses=True`),
so turn it into a number yourself with `int()`.
:::
:::

:::step{type=try title="Feel the slowness"}
Start the app in this terminal:

```bash run
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open a **second terminal tab** and time a price:

```bash run
time curl -s localhost:8000/price/samosa
```

About 1.5 seconds, every single time. Leave the app running: `--reload` restarts it when you save.
:::

:::step{type=task task=price_cache title="Cache the prices"}
In `app.py`, make `GET /price/{item}` use cache-aside:

- the key is `price:<item>`, for example `price:samosa`;
- on a miss, call `slow_price_lookup(item)` and keep the answer for **60 seconds**;
- on a hit, answer from Redis without calling the slow lookup.

The answer stays the same JSON: `{"item": "samosa", "price": 20}`. Time two calls in a row to see it work.
:::

:::step{type=task task=otp_limit title="Stop the OTP spam"}
Make `POST /otp/{phone}` allow at most **3 calls per phone number per minute**.
The 4th call within the minute must get status **429** (Too Many Requests).

Keep the count in Redis under `otp:count:<phone>`, and let it reset after 60 seconds.

```bash
for i in 1 2 3 4; do curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/otp/9876543210; done
```
:::

:::step{type=deep-dive title="What the simple limiter gets wrong"}
This is a **fixed window**: the minute starts at the first request. A caller can send 3 requests at
the end of one window and 3 more at the start of the next, so 6 in two seconds. Real APIs often use
a **sliding window** (a sorted set of timestamps per caller) or a **token bucket**.

There is also a small race: if the app crashes between `INCR` and `EXPIRE`, the counter never
expires. Redis can run both in one step with a `MULTI` transaction or a short Lua script.
:::

:::step{type=recap}
- Cache-aside: read Redis, on a miss do the slow work and store it with a TTL.
- The TTL is how stale you allow the answer to get.
- `INCR` plus `EXPIRE` gives a per-caller counter that resets itself: a simple rate limiter.
:::
