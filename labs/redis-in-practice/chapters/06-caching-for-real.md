:::step{type=story title="1.5 seconds per price"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Our app asks the old billing system for a price on every screen, and every call takes 1.5 seconds.
Prices change maybe once a day. A cache is the obvious fix. But the last team that added one shipped
two bugs with it: customers saw yesterday's prices, and one morning the cache emptied at 9 o'clock and
took billing down with it. Let us get all three right.
:::

:::mission
Put a cache in front of the slow price lookup, keep it correct when prices change, and survive the moment it is empty.
:::
:::

:::step{type=concept title="Cache-aside"}
**Cache-aside** is the most common way to use a cache, and it is three lines of logic:

1. Look for the answer in Redis.
2. Found it (a **hit**)? Return it.
3. Not there (a **miss**)? Do the slow work, store the answer with a **TTL**, return it.

The TTL is a promise about staleness: with 60 seconds, a wrong answer can live for at most a minute.
It is also a safety net: even if every other part of your invalidation fails, the cache heals itself.
:::

:::step{type=predict title="Guess first"}
:::question
The cache is empty, and 30 customers open the menu in the same second. With plain cache-aside, how many times is the slow billing system called?
:::
- [ ] Once: the first request fills the cache for the others
- [x] About 30 times: they all miss before the first one finishes
- [ ] Never: the cache handles it
:::explain
Each request checks Redis, finds nothing, and starts the 1.5 second lookup. The first one only fills
the cache after 1.5 seconds; by then all 30 have already gone to billing. This is a **cache
stampede**, and it hits exactly when you are busiest.
:::
:::

:::step{type=try title="Feel the slowness"}
With the app running, time a price twice:

```bash run
time curl -s localhost:8000/price/samosa
```

About 1.5 seconds, every single time. Every call is also counted:

```bash run
redis-cli GET billing:calls
```
:::

:::step{type=task task=price_cache title="Cache the prices"}
In `app.py`, make `GET /price/{item}` use cache-aside:

- the key is `price:<item>`, for example `price:samosa`;
- on a miss, call `slow_price_lookup(item)` and keep the answer for **60 seconds**;
- on a hit, answer from Redis without calling the slow lookup.

The answer stays the same JSON: `{"item": "samosa", "price": 20}`.
:::

:::step{type=task task=price_invalidate title="When a price changes"}
`PUT /price/{item}` updates the billing system, but the cache keeps serving the old price for up to a
minute. Make the **very next read** after a change return the new price.

```bash
curl -s -X PUT localhost:8000/price/samosa -H 'Content-Type: application/json' -d '{"price": 22}'
```
:::

:::step{type=concept title="Taming the stampede"}
The fix for a stampede: let **one** request rebuild the cache, and make the others wait for it.

Redis gives you the "only one" for free. `SET key value NX` sets the key only if it does **not**
exist, and tells you whether it did. The first request to set `lock:price:samosa` wins; everyone
else gets `None`.

The winner calls billing, fills the cache and deletes the lock. The others poll the cache every
50 ms until the answer appears. Give the lock a short TTL (`ex=5`), so a crashed winner cannot block
everyone forever.
:::

:::step{type=task task=stampede_lock title="Survive the stampede"}
Make sure that when the cache for an item is empty and many requests arrive at once, **only one** of
them calls `slow_price_lookup`; the others wait and return the same price.

The check sends 30 requests for the same item at the same moment and counts the calls to billing.
:::

:::step{type=deep-dive title="What senior engineers add"}
**Write paths: delete, do not update.** Deleting `price:samosa` after a change is safer than writing
the new price into the cache: two updates racing to write could leave the older value cached forever.

**Jitter.** Thousands of keys cached at 9:00 with the same TTL all expire at 9:01. Add a few random
seconds to each TTL so they expire spread out.

**Refresh early.** Hot keys can be refreshed in the background shortly *before* they expire
(probabilistic early expiration), so readers never see a miss at all.

**Negative caching.** "No such item" is an answer too: cache it briefly, or a bot asking for
missing items goes straight to your database every time.
:::

:::step{type=recap}
- Cache-aside: read Redis; on a miss, do the work and store it with a TTL.
- On a change, delete the cached value; the next read rebuilds it.
- A stampede is many misses at once; `SET ... NX` with a TTL lets exactly one request rebuild.
- Jitter, early refresh and negative caching are the habits of production caches.
:::
