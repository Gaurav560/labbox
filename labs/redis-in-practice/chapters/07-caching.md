:::step{type=story title="1.5 seconds for every price"}
Here is the problem chapter 1 promised to solve. Every product page in Basket shows a price, and every price
comes from the catalogue service: always right, always slow, and billed per call.

The catalogue does not change its prices every second. Rice cost Rs 60 a moment ago, and it almost certainly
costs Rs 60 now. Asking again is pure waste. What if the app **remembered** the answer for a little while?

That is a **cache**: a fast place to keep copies of answers that are slow or expensive to get. Redis is the most
common cache in the world, and this chapter builds the most common way of using it. You will see a price go from
1.5 seconds to under a millisecond, measured on your own app.

The word comes from the French cacher, to hide. Trappers and explorers in the far north left caches of food along their routes, often raised on posts out of reach of animals, so they did not have to carry everything from home every time. A Redis cache does the same for answers.

:::photo{src="/lesson-images/redis/alaska-cache.webp" alt="A small log storehouse raised high on wooden posts with a ladder, next to a log cabin in a forest in Alaska" credit="NPS Photo" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Gidding's_Cabin_at_Onion_Portage_(c54f6f71-1dd8-b71c-074c-75eb35032212).jpg"}
A log cache on posts beside a cabin at Onion Portage, Alaska.
:::

:::mission
Cache prices in Redis for 60 seconds, and make sure a price change shows up on the very next read.
:::
:::

:::step{type=try title="Feel the slowness" file="07-caching/app.py" line="19-26"}
Look at `price()` in `07-caching/app.py`, on the right. On every request it calls `lookup_price(item)`, the slow
catalogue (it lives in `catalogue.py` next to it: a 1.5 second wait, counted in the Redis key `catalogue:calls`).

Stop the chapter 6 app if it is still running (**Ctrl+C**), and start this chapter's app:

```bash run
cd /workspace/07-caching && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

In a second terminal, ask for the price of rice three times. The `-w` option makes curl print how long each
request took:

```bash run
for i in 1 2 3; do curl -s -w "  %{time_total} s\n" localhost:8000/price/rice; done
```

```text
{"item":"rice","price":60}  1.509738 s
{"item":"rice","price":60}  1.501050 s
{"item":"rice","price":60}  1.509181 s
```

The same answer, the same 1.5 second wait, three times. Now count the bill:

```bash run
redis-cli GET catalogue:calls
```

Every request was a paid call. Ten customers opening the rice page means ten calls, fifteen seconds of waiting and
Rs 1. A million means Rs 100,000 (chapter 1's table).
:::

:::step{type=concept title="Cache-aside: look in Redis first"}
The pattern you will write is called **cache-aside** (also "lazy loading"), and it is three rules:

1. **Look in the cache first.** Ask Redis for `price:rice`.
2. **On a hit**, answer with what Redis gave you. The slow system is not asked at all.
3. **On a miss**, ask the slow system, **store its answer in Redis with a lifetime**, then answer.

A **hit** means the cache had the answer; a **miss** means it did not. The cache sits "aside" the real source:
the app talks to both, and Redis only ever holds copies.

:::diagram{name="cache-aside-flow"}
The first request misses and pays for the catalogue once; every request after it, until the copy expires, is a hit.
:::

Why the **lifetime** in rule 3? Because a copy can go out of date. If the pricing team changes the price of rice
and nobody tells the cache, customers would see the old price forever. With `EX 60`, the worst case is a minute
of the old price, and then Redis drops the copy and the next read asks the catalogue again. The lifetime is a
promise about how stale a copy can ever be.

Choosing it is a business question, not a technical one:

| Data | A sensible lifetime | Why |
|---|---|---|
| A product price | 1 minute | price changes must show up quickly |
| The list of categories | 1 hour | it changes a few times a year |
| A customer's delivery estimate | 5 minutes | traffic changes slowly |
| A login code | 5 minutes | for safety, not speed (chapter 3) |

**Check yourself:** with `EX 60`, a price changes at 10:00:00. What is the latest moment a customer could still
see the old price? (About 10:01:00, when the copy expires.)
:::

:::step{type=example title="Worked example: caching a delivery estimate"}
Here is cache-aside on a different problem: Basket asks a slow maps service how many minutes a delivery to a
pincode takes. This code is only to read; it is not in your project.

```python
def delivery_minutes(pincode):
    key = f"eta:{pincode}"
    cached = r.get(key)
    if cached is not None:
        return int(cached)
    minutes = slow_eta(pincode)
    r.set(key, minutes, ex=300)
    return minutes
```

Read it line by line:

1. `key = f"eta:{pincode}"`: one cache key per pincode, named with the colon convention.
2. `cached = r.get(key)`: rule 1, look in Redis first.
3. `if cached is not None`: a hit. Compare with `None`, not with "truthiness": a cached `0` or `""` is still a
   hit. `int(cached)` because Redis gives back text.
4. `minutes = slow_eta(pincode)`: a miss, so rule 3, ask the slow service.
5. `r.set(key, minutes, ex=300)`: keep the answer for five minutes.
6. `return minutes`: answer the caller.

Calling it three times in a row in this lab printed:

```text
14 minutes, answered in 1008.86 ms
14 minutes, answered in 0.17 ms
14 minutes, answered in 0.08 ms
```

The first call paid for the maps service; the next two were hits, thousands of times faster.
:::

:::step{type=predict title="Guess first"}
:::question
An item's cached value is an empty string, `""`. Your code checks `if cached:` instead of
`if cached is not None:`. What happens on every request for that item?
:::
- [ ] A hit, as it should be
- [x] A miss every time: `""` is falsy, so the slow system is asked on every request
- [ ] It crashes
:::explain
In Python an empty string counts as false, so `if cached:` treats a real cached value as a miss, forever.
`is not None` says exactly what you mean: "Redis had a value".
:::
:::

:::step{type=task task=price_cache title="Your turn: cache the prices"}
Make `price()` in `07-caching/app.py` use cache-aside, following the worked example:

1. Look in Redis first, under `price:<item>` (for example `price:rice`).
2. On a hit, return `{"item": item, "price": ...}` with the price as an **int**.
3. On a miss, ask `lookup_price(item)` as now (keep the 404 for unknown items), store the price under
   `price:<item>` with a lifetime of **60 seconds**, and return it.

Run the three-curl loop again: the first request should take 1.5 s, the next two a millisecond or so. Press
**Check**: it empties the cache, times a cold and a warm request, and looks at the lifetime you set.
:::

:::step{type=concept title="When the truth changes: invalidation" file="07-caching/app.py" line="33-40"}
Now look at `set_price()` on the right. The pricing team calls `PUT /price/<item>` to change a price, and line 38
updates the catalogue. But the cached copy in Redis does not know that.

Here is what this lab's app did with cache-aside working but nothing else changed. Bread was cached at Rs 45, then
its price was changed to Rs 50:

```text
$ curl localhost:8000/price/bread
{"item":"bread","price":45}
$ curl -X PUT localhost:8000/price/bread -H "content-type: application/json" -d '{"price": 50}'
{"item":"bread","price":50}
$ curl localhost:8000/price/bread
{"item":"bread","price":45}
```

The catalogue says 50; customers still see 45, for up to a minute (`TTL price:bread` answered 60). For a price,
that is a real problem: a customer sees one price on the product page and another at checkout.

The fix is called **invalidation**: when the source of truth changes, **delete the cached copy**. The next read
misses, asks the catalogue, and caches the new price. You could also write the new price straight into Redis,
but deleting is safer: the copy is always rebuilt from the source of truth, so a bug in your update code can never
leave a wrong value cached.

There is a famous line in programming, often credited to Phil Karlton: "There are only two hard things in
computer science: cache invalidation and naming things." Now you know why the first one is on the list.
:::

:::step{type=task task=price_invalidate title="Your turn: when a price changes"}
In `set_price()`, after the catalogue is updated, make sure the next read of that item sees the new price.

Try the bread sequence above: GET, PUT 50, GET. The second GET should answer 50 (after a 1.5 second miss), and the
GET after that should be fast again. Press **Check**.
:::

:::step{type=try title="Measure what you built"}
With both tasks done, run the measurement once more on your own app. In this lab it printed:

```text
{"item":"rice","price":60}  1.530646 s
{"item":"rice","price":60}  0.000999 s
{"item":"rice","price":60}  0.000678 s
```

Under one millisecond, from 1.5 seconds: about **two thousand times faster** for every request after the first,
and the catalogue was asked **once** instead of three times (`GET catalogue:calls`). Then change a price and watch:

```text
$ curl -X PUT localhost:8000/price/rice -H "content-type: application/json" -d '{"price": 62}'
{"item":"rice","price":62}
$ redis-cli GET price:rice
(nil)
```

The copy is gone, so the next read pays once more and caches the new price:

```text
{"item":"rice","price":62}  1.509527 s
{"item":"rice","price":62}  0.000823 s
```

Correct and fast. Chapter 8 measures how much this saves over a whole day.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the cached price get a lifetime, even though `set_price()` already deletes it on every change?
:::
- [ ] Redis requires every key to have a TTL
- [x] As a safety net: if a change ever bypasses `set_price()` (another system, a bug, a manual fix), the stale copy still dies within a minute
- [ ] To save memory only
:::explain
Invalidation handles the changes you know about; the lifetime limits the damage from the ones you do not. Real
systems use both. (It also lets Redis drop copies nobody reads any more, which chapter 14 uses.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A price changes. Which is the safest way to update the cache?
:::
- [x] Delete `price:<item>`; the next read rebuilds it from the catalogue
- [ ] Write the new price into `price:<item>` with a plain `SET`
- [ ] Do nothing; the lifetime will handle it
:::explain
Deleting means the cache is always rebuilt from the source of truth. A plain `SET` would also drop the lifetime
(chapter 3), and doing nothing shows the old price for up to a minute.
:::
:::

:::step{type=deep-dive title="Go deeper: other caching patterns, and what real teams add"}
**Write-through.** Every write goes to the database **and** the cache at the same time, so the cache is always
warm. It costs a cache write for data that may never be read, and it still needs care when two writes race.

**Write-behind.** Writes go to the cache first, and a background worker copies them to the database later. Very
fast, but a crash can lose writes the database never saw. Used for counters and analytics, rarely for money.

**Read-through.** The cache library itself calls the slow system on a miss; your code only ever talks to the
cache. Cache-aside is the same idea, written in your own code, which is why it is the most common.

**Negative caching.** `GET /price/caviar` misses, asks the catalogue for 1.5 seconds, and gets "no such item".
Nothing is cached, so the next request for caviar pays again. An attacker who sends random item names can make
every request slow. Teams cache the "not found" too, for a short time (`SET price:caviar none EX 30`).

**Keep cached values small, and versioned.** Cache what the page needs, not a whole database row. And put a
version in the key (`price:v2:rice`): when the format changes, new code reads new keys and the old ones simply
expire.

**A cache is not the source of truth.** If Redis is restarted or empty, a cache-aside app must still work, just
slower. Never store something only in a cache that you cannot rebuild.
:::

:::step{type=recap}
You can now:

- explain hits, misses and cache-aside: look in Redis, answer on a hit, ask and store with a lifetime on a miss;
- choose a lifetime from how stale the data may be, and explain the trade-off;
- invalidate a cached copy when the source of truth changes, by deleting it;
- measure what a cache does to response time, with `curl -w` and the catalogue's call counter.

Next, chapter 8: count every hit and miss, and turn them into seconds and rupees saved.

:::photo{src="/lesson-images/redis/redis-07-notes.webp" alt="Handwritten notes about caching: 1. look in Redis first; 2. hit: answer at once; 3. miss: ask, then SET ... EX 60; price changed? delete the copy; 1.5 s became 1 ms" ai="true"}
One page of notes for this chapter.
:::
:::
