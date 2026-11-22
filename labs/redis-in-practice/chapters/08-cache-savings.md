:::step{type=story title="Is the cache paying for itself?"}
Your price cache works. Requests are fast. Then, in a planning meeting, someone asks the question every engineer
eventually hears: "We pay for a Redis server now. **What does it actually save us?**"

"It is faster" is not an answer anyone can put in a budget. "Yesterday it answered 96% of price reads, which
saved 400 hours of waiting and Rs 96,000 in catalogue fees, and it costs us 124 MB of memory" is.

To say that, you need numbers, and the cheapest place to keep them is Redis itself. In this chapter Basket's app
starts measuring its own cache: every hit, every miss, and what they add up to in seconds and rupees.

:::mission
Count every hit and miss in Redis, and report what the cache saved in time and money.
:::
:::

:::step{type=concept title="Hits, misses and the hit rate"}
Every read through a cache ends one of two ways: a **hit** (Redis had it) or a **miss** (it did not, so the slow
system was asked). Count both, and one number tells you how well the cache works:

```text
hit rate = hits / (hits + misses)
```

Nine hits and one miss give 9 / 10 = **0.9**, a 90% hit rate. Chapter 1 showed why that number matters so much:
only the misses reach the slow system, so going from 90% to 99% cuts its load **ten times**.

Each hit also has a value you can calculate, because you know what a miss costs. For Basket's catalogue
(`catalogue.py` holds both prices):

| Every hit saves | Because a miss costs |
|---|---|
| 1.5 seconds of waiting | `SECONDS_PER_CALL = 1.5` |
| Rs 0.10 | `RUPEES_PER_CALL = 0.10` |

So the savings are simply **hits multiplied by the cost of one call**. Nine hits saved 13.5 seconds and Rs 0.90.

**Check yourself:** 99 hits and 1 miss. What is the hit rate, and how much money was saved? (0.99, and
99 x Rs 0.10 = Rs 9.90.)
:::

:::step{type=try title="What does Redis count by itself?"}
Redis already keeps some statistics of its own. With this chapter's app running (stop the chapter 7 app first),
ask for the price of onions ten times:

```bash run
cd /workspace/08-cache-savings && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

```bash run
for i in $(seq 10); do curl -s localhost:8000/price/onions > /dev/null; done
```

Now look at Redis's own counters:

```bash run
redis-cli INFO stats | grep keyspace
```

In this lab, after a fresh start, it showed:

```text
keyspace_hits:9
keyspace_misses:2
```

Nine hits: the nine reads after the first. But **two** misses, not one. Why? The second miss was a `GET` this lab
ran on a key that did not exist yet, nothing to do with prices. Redis counts **every** lookup of **every** key:
prices, sessions, counters, your own typing in `redis-cli`. On a real server shared by many features, the global
numbers mix everything together.

That is why apps count their own hits and misses, per feature, with names like `stats:price:hits`. Then the
price cache's hit rate is the price cache's, and nothing else's.
:::

:::step{type=example title="Worked example: counting on-time deliveries"}
Here is the same idea on a different problem: Basket wants to know how many deliveries arrive within its
10-minute promise. This code is only to read; it is not in your project.

```python
def record_delivery(minutes):
    if minutes <= 10:
        r.incr("stats:delivery:on_time")
    else:
        r.incr("stats:delivery:late")


def on_time_report():
    on_time = int(r.get("stats:delivery:on_time") or 0)
    late = int(r.get("stats:delivery:late") or 0)
    total = on_time + late
    rate = round(on_time / total, 3) if total else 0
    return {"on_time": on_time, "late": late, "on_time_rate": rate}
```

1. `record_delivery` adds one to one of two counters with `INCR`: one step, safe when many workers record
   deliveries at once (chapter 2), and the first `INCR` creates the counter.
2. In the report, `r.get(...)` gives `None` for a counter that was never created. `None or 0` turns that into 0,
   and `int(...)` turns the text `"5"` into the number 5.
3. `if total else 0` guards against dividing by zero before the first delivery.

Before and after seven deliveries (8, 9, 12, 7, 10, 15 and 6 minutes), it printed:

```text
{'on_time': 0, 'late': 0, 'on_time_rate': 0}
{'on_time': 5, 'late': 2, 'on_time_rate': 0.714}
```
:::

:::step{type=predict title="Guess first"}
:::question
The counter `stats:price:hits` has never been created. What does `int(r.get("stats:price:hits") or 0)` give?
:::
- [ ] It raises an error, because `r.get` returns `None`
- [x] `0`
- [ ] `None`
:::explain
`r.get` returns `None`, `None or 0` is `0`, and `int(0)` is `0`. Without the `or 0`, `int(None)` would raise a
`TypeError`, a classic first-day bug in a fresh environment.
:::
:::

:::step{type=task task=hit_counter title="Your turn: count every hit and miss"}
In `price()` in `08-cache-savings/app.py` (the cache-aside you wrote in chapter 7 is already there):

1. On a **hit**, add one to `stats:price:hits` before returning.
2. On a **miss**, after storing the price, add one to `stats:price:misses`.

Unknown items (the 404) are neither: do not count them. Run the ten-onions loop again and `GET` both counters.
Press **Check**: it resets the counters and makes exactly one miss and nine hits.
:::

:::step{type=concept title="From counts to money, and what Redis costs"}
Counting is half the answer. The other half is turning counts into the numbers a planning meeting cares about,
and being honest about the cost on the other side.

**What the cache saves**, for any period, is hits times the cost of one slow call. Basket's app answered about
a million price reads a day in our story. At a 96% hit rate:

| Per day | Without the cache | With the cache (96% hits) | Saved |
|---|---|---|---|
| Catalogue calls | 1,000,000 | 40,000 | 960,000 calls |
| Catalogue fees | Rs 100,000 | Rs 4,000 | Rs 96,000 |
| Customer waiting | 417 hours | 17 hours | 400 hours |

**What the cache costs** is mostly **memory**. You can measure that too. This lab stored 100,000 cached prices,
each with a lifetime, and `INFO memory` went from about 1.2 MB to about 13.6 MB: roughly **124 bytes per cached
price**, key, value, lifetime and Redis's own bookkeeping included. A million cached prices would need about
124 MB of RAM, a small slice of a single server.

```bash run
redis-cli MEMORY USAGE price:onions
```

(`MEMORY USAGE` answered `56` bytes for one price key in this lab: the key and its value. The rest of the 124 is
the shared tables Redis keeps to find keys and their lifetimes.)

That is the honest comparison: a few hundred megabytes of memory against hundreds of hours and tens of thousands
of rupees a day. It is why almost every busy app has a cache. But the comparison only holds if you **measure**:
a cache with a 20% hit rate costs the same memory and saves very little.
:::

:::step{type=task task=savings_report title="Your turn: the savings report"}
Write `GET /savings` in the same file. Read the two counters (a missing one counts as 0) and return:

| field | value |
|---|---|
| `hits` | the hits counter, as an int |
| `misses` | the misses counter, as an int |
| `hit_rate` | hits / (hits + misses), rounded to 3 places; **0** when there were no reads yet |
| `seconds_saved` | hits x `SECONDS_PER_CALL`, rounded to 2 places |
| `rupees_saved` | hits x `RUPEES_PER_CALL`, rounded to 2 places |

`SECONDS_PER_CALL` and `RUPEES_PER_CALL` are already imported from `catalogue.py`. Try `curl
localhost:8000/savings` before and after some reads, then press **Check**.
:::

:::step{type=try title="Watch the savings grow"}
With both tasks done, this lab's app answered, starting from empty counters:

```text
{"hits":0,"misses":0,"hit_rate":0,"seconds_saved":0.0,"rupees_saved":0.0}
```

After ten reads of onions (one miss, then nine hits):

```text
{"hits":9,"misses":1,"hit_rate":0.9,"seconds_saved":13.5,"rupees_saved":0.9}
```

After thirty more reads each of rice, dal and eggs (three more misses, 87 more hits):

```bash run
for it in rice dal eggs; do for i in $(seq 30); do curl -s localhost:8000/price/$it > /dev/null; done; done
```

```text
{"hits":96,"misses":4,"hit_rate":0.96,"seconds_saved":144.0,"rupees_saved":9.6}
```

The more popular an item, the closer its hit rate gets to 100%: each item misses once per minute at most, then
every other read is free. That is why caches work so well for shops, where a few hundred popular items get most of
the views.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`INFO stats` shows `keyspace_hits:5000` and `keyspace_misses:5000`, a 50% hit rate. Does that mean the price cache
is doing badly?
:::
- [ ] Yes, half the prices miss
- [x] Not necessarily: Redis counts every lookup of every key, so other features mix into the number
- [ ] No, 50% is always good
:::explain
The global counters include sessions, counters, rate limits and anything else that reads keys. Count per feature,
like `stats:price:hits`, to know how one cache is doing.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A cache for a cheap, fast lookup has a 99% hit rate. A cache for the slow, paid catalogue has an 80% hit rate.
Which one saves more?
:::
- [ ] The 99% one, because its hit rate is higher
- [x] Probably the 80% one: savings are hits times the cost of a miss, and the catalogue's misses are expensive
- [ ] They save the same
:::explain
A hit rate on its own says how often the cache helps, not how much. Multiply by what a miss costs. Caches in
front of slow, paid or overloaded systems are where the money is.
:::
:::

:::step{type=deep-dive title="Go deeper: what real teams watch"}
**Latency percentiles, not averages.** A page that is fast on average can still be slow for 1 customer in 100.
Teams watch **p50** (the median), **p95** and **p99** of response time. A cache mostly improves p50; the misses
are what keep p99 high, which is one reason to raise the hit rate further.

**Evictions.** `INFO stats` also shows `evicted_keys`: keys Redis threw away because memory was full (chapter
14). If it climbs, the cache is too small and the hit rate will fall.

**Hit rate per kind of key.** One counter pair per feature (`stats:price:*`, `stats:eta:*`), graphed over time.
A sudden drop usually means a deploy changed the key names, or expired everything at once (chapter 9).

**Count cheaply.** Two `INCR` commands per read is one extra round trip each. At high volume, teams send the
counter `INCR` in the same pipeline as other commands, or count in the app's memory and add the totals to Redis
every few seconds. Metric systems such as Prometheus do this for you.

**Cache warming.** After a deploy or a restart the cache is empty, so the hit rate starts at 0 and the slow
system takes the full load. Some teams fill the most popular keys before sending traffic, called warming the
cache.
:::

:::step{type=recap}
You can now:

- calculate a hit rate, and explain why the misses decide the load on the slow system;
- count hits and misses per feature with `INCR`, and read counters safely with `or 0`;
- turn counts into time and money saved, and measure what the cache costs in memory;
- read Redis's own `keyspace_hits` and `keyspace_misses`, and know why they mix features together.

Next, chapter 9: what happens when the cache is empty and everyone arrives at once.

:::photo{src="/lesson-images/redis/redis-08-notes.webp" alt="Handwritten notes about what the cache saves: hit rate = hits / (hits + misses); INCR stats:price:hits; saved = hits x cost of a call; a cached price: about 124 bytes; measure before you promise" ai="true"}
One page of notes for this chapter.
:::
:::
