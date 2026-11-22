:::step{type=story title="What happens when everyone arrives at once?"}
A cache is wonderful on an ordinary day. Now picture Basket's big sale. At exactly 6 pm a notification goes out:
"Paneer, 30% off". Thousands of phones open the paneer page in the same second.

The cached price of paneer happened to expire a moment ago. So the first request misses and asks the catalogue.
And so does the second, which arrived a millisecond later, before the first one had an answer to store. And the
third. In that one second, **every** request misses, and every one asks the slow, paid catalogue at the same time.

This has a name: a **cache stampede**, or the **thundering herd problem**. It is one of the classic ways busy
systems fall over: the cache is fine 99.99% of the time, and in the one moment it is empty, the whole crowd runs
straight past it to the system it was protecting.

Every year more than a million wildebeest cross the Mara River in East Africa, and when the first ones go, the whole herd follows at once. To the system behind a cache, a stampede of requests looks just the same.

:::photo{src="/lesson-images/redis/wildebeest-crossing.webp" alt="A dense herd of wildebeest pouring down a dusty riverbank into a brown river, splashing as they cross" credit="Naturaltracksafaris" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Wildebeests_migration_crossing.jpg"}
Wildebeest crossing the Mara River during the great migration.
:::

:::mission
Let only one request ask the catalogue when the cache is empty, and stop prices cached together from expiring
together.
:::
:::

:::step{type=try title="Watch a stampede" file="09-stampede/stampede.py" line="17-26"}
`stampede.py` in this chapter's folder recreates the sale: it empties the cache for one item, sends **30 requests
at the same moment** to your app, and counts how many reached the catalogue.

Stop the previous chapter's app and start this one (it already has the cache and the counters from chapters 7
and 8):

```bash run
cd /workspace/09-stampede && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

In a second terminal:

```bash run
cd /workspace/09-stampede && python3 stampede.py paneer
```

```text
30 requests for paneer: 30 answered in 1.9 s
catalogue calls: 30
```

Every one of the 30 requests asked the catalogue. Thirty times the fee, and thirty slow calls landing on the
catalogue in the same instant. With 30 requests that is annoying; with 30,000, the catalogue falls over, its
callers time out and retry, and the outage feeds itself.

Before reading on, think about it: the cache code is correct. Each request did exactly what cache-aside says. So
what is missing?
:::

:::step{type=concept title="Only one asks; the others wait"}
What is missing is **coordination**. Thirty requests each decided on their own "it is a miss, I will ask".
What we want is: **one** of them asks, and the other 29 wait a moment for its answer.

Redis can make that decision for us, with a tiny **lock**: a key that only one request can create.
Chapter 2's deep dive mentioned `SET ... NX`, "set only if it does **not** exist". Watch it in `redis-cli`:

```text
> SET lock:price:paneer 1 NX EX 5
OK
> SET lock:price:paneer 1 NX EX 5
(nil)
```

The first `SET` created the key and answered `OK`. The second found it already there, changed nothing, and
answered `(nil)`. Remember the rule from chapter 2, one command at a time: if thirty requests send this command at
the same instant, Redis runs them one after another, and **exactly one** gets `OK`. That one is the winner.

So on a miss, the new plan is:

1. **Try to take the lock**, `lock:price:<item>`, with `NX`.
2. **The winner** asks the catalogue, stores the price, removes the lock, and answers.
3. **Everyone else** waits a short moment (say 100 ms), then looks in the cache again, until the winner's answer
   appears there.

And the `EX 5`? It is the lock's own lifetime. If the winner crashes halfway, nobody would ever remove the lock,
and the others would wait forever. With a lifetime, the lock disappears on its own after 5 seconds at the most.

:::diagram{name="stampede"}
Without a lock all 30 miss and all 30 ask; with one, a single winner asks and the rest read its answer.
:::
:::

:::step{type=example title="Worked example: one worker builds the nightly report"}
Here is the same `NX` trick on a different problem. Basket runs three copies of its report worker, for safety, and
each one wakes at midnight to build the daily sales report. The report must be built **once**, not three times.
This code is only to read; it is not in your project.

```python
if r.set("lock:report", "1", nx=True, ex=600):
    build_report()
    r.delete("lock:report")
else:
    print("another worker is building it")
```

In redis-py, `set(..., nx=True)` gives back `True` when it created the key and `None` when the key was already
there. Running it twice in this lab:

```python
print(r.set("lock:report", "1", nx=True, ex=5))
print(r.set("lock:report", "1", nx=True, ex=5))
```

```text
True
None
```

1. `nx=True` is the `NX` option: only one caller can get `True`.
2. `ex=600` makes the lock expire after ten minutes, longer than a report takes, in case a worker crashes.
3. The winner removes the lock when it is done. The others do nothing.

The stampede is the same shape, with one difference: the losers do not give up. They **wait and read the cache
again**, because they still need the price. A loop like this does that, with a limit so nobody waits forever:

```python
for _ in range(50):
    time.sleep(0.1)
    cached = r.get(key)
    if cached is not None:
        return ...  # the winner's answer
```
:::

:::step{type=predict title="Guess first"}
:::question
The winner takes the lock, asks the catalogue, and crashes before storing the price or removing the lock. The lock
was set with `EX 5`. What happens to the 29 waiting requests?
:::
- [ ] They wait forever
- [x] The lock expires within 5 seconds; a waiter that runs out of patience asks the catalogue itself
- [ ] They all get an error at once
:::explain
That is what the lock's lifetime is for: a crashed winner cannot block everyone. Combined with a limited wait
loop (50 tries of 100 ms), every request gets an answer, at worst a few seconds late.
:::
:::

:::step{type=task task=stampede_lock title="Your turn: survive the stampede"}
Change `price()` in `09-stampede/app.py` so that on a miss, only one request asks the catalogue:

1. On a miss, try to take a lock `lock:price:<item>` with `SET ... NX` and a short lifetime (5 seconds).
2. If you got it: ask the catalogue, store the price and count the miss as now, then **delete the lock** (a
   `try`/`finally` makes sure it is deleted even if something fails).
3. If you did not: wait 0.1 s and look in Redis again, up to 50 times. When the price appears, count a hit and
   return it. If it never appears, ask the catalogue yourself.

Run `python3 stampede.py paneer` again: it should say `catalogue calls: 1`. Press **Check**.
:::

:::step{type=concept title="A herd of expiries: why lifetimes need jitter"}
There is a quieter version of the same problem. Look at what this lab's app did when six prices were cached at
the same moment (for example right after a deploy, or when the home page loads six items at once), each with
`EX 60`:

```text
rice 60
dal 60
mangoes 60
eggs 60
atta 60
onions 60
```

Six prices, six identical lifetimes. Sixty seconds from now they all expire **in the same second**, so the next
visitor misses six times at once, and the catalogue gets a burst. Then they are all cached again together, with
identical lifetimes again, and a minute later the burst repeats. On a real shop with thousands of items cached
in the first second after a deploy, these bursts can last for hours.

The fix is beautifully simple: give each key a slightly **random** lifetime, called **jitter**. Instead of exactly
60 seconds, pick anything between 45 and 60:

```python
import random

random.randint(45, 60)
```

`randint(45, 60)` gives a whole number from 45 to 60, both included. Six calls in this lab gave
`[57, 50, 58, 48, 57, 51]`. The expiries spread out over fifteen seconds, the catalogue sees a gentle trickle
instead of a burst, and the worst case for a stale price is still one minute.
:::

:::step{type=task task=jitter_ttl title="Your turn: spread out the expiries"}
In the same `price()`, store each price with a **random** lifetime between **45 and 60** seconds instead of the
fixed 60. (Python's `random` module needs an `import random` at the top of the file.)

Cache a few prices at once (open several in parallel, or run the stampede script for different items) and look at
their TTLs: they should differ. Press **Check**: it caches six prices at the same moment and compares their
lifetimes.
:::

:::step{type=try title="The stampede, tamed"}
With both tasks done, here is what this lab's app did. The stampede first:

```text
30 requests for paneer: 30 answered in 1.8 s
catalogue calls: 1
```

The same 30 requests, the same total time (everyone still waits for one catalogue answer), but **one** call
instead of thirty: one fee instead of thirty, and no burst on the catalogue. Then six prices cached together:

```text
rice 55
dal 48
mangoes 60
eggs 45
atta 54
onions 60
```

The expiries are now spread over fifteen seconds instead of landing in one (two of them happen to share 60,
which is fine: what matters is that they no longer all arrive together). And the counters agree with the story: `MGET stats:price:hits stats:price:misses`
answered 29 hits and 7 misses: the stampede's 29 waiters were served from the cache (hits), and the 7 misses were
the stampede's single winner plus the six new prices.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `SET lock NX` pick exactly one winner, even when 30 requests send it at the same instant?
:::
- [ ] redis-py retries the losers
- [x] Redis runs commands one at a time: the first `SET NX` creates the key, and every later one finds it there
- [ ] Each request locks for a different number of seconds
:::explain
There is no gap between "is the key there?" and "create it" inside one command, so two requests can never both
see "not there". The same one-at-a-time rule made `INCR` safe in chapter 2.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Prices are cached with `EX 60`. What does adding jitter (a random lifetime from 45 to 60 seconds) change about the
worst case for a stale price?
:::
- [ ] It makes stale prices last longer
- [x] Nothing: a copy still lives 60 seconds at most, it just expires at a less predictable moment
- [ ] It removes stale prices completely
:::explain
The upper limit stays at 60 seconds, so the promise to the pricing team is unchanged. Jitter only spreads the
expiries out, so they do not all arrive together.
:::
:::

:::step{type=deep-dive title="Go deeper: other ways to stop a herd"}
**Serve stale while refreshing.** Some caches keep the old value a little past its lifetime, and while one
request refreshes it in the background, everyone else gets the slightly old value at once instead of waiting.
You store two times with the value: a "soft" expiry when a refresh should start, and a "hard" one for the key.

**Refresh before expiry.** A popular key can be refreshed early by a background job, so it never expires during
traffic at all. Some systems refresh with a probability that rises as the expiry approaches (a technique known as
"probabilistic early expiration" or XFetch), so that in a crowd usually exactly one request does it.

**Request coalescing inside one server.** If one app server receives 30 requests for the same missing key, it can
make one call and share the answer among its own threads, without Redis. A Redis lock is still needed across
many app servers.

**The lock here is a hint, not a guarantee.** This lock only saves work: if it ever fails (say Redis restarts
and loses it), two requests ask the catalogue, which costs a little money and nothing worse. When a lock must
**guarantee** correctness, as with a delivery slot that only one customer may book, it needs more care. That is
chapter 11.
:::

:::step{type=recap}
You can now:

- explain a cache stampede, and see one happen on your own app;
- pick exactly one winner with `SET key value NX EX seconds`, and let the others wait and re-read the cache;
- give a lock a lifetime, so a crashed winner can never block everyone;
- add jitter to lifetimes, so keys cached together do not expire together.

Next, chapter 10: counters and checks that must never be fooled by requests that arrive together.

:::photo{src="/lesson-images/redis/redis-09-notes.webp" alt="Handwritten notes about the stampede: empty cache + a crowd = stampede; SET lock NX EX 5: one winner; the rest wait and read again; jitter: EX 45 to 60, random; 30 requests, 1 call" ai="true"}
One page of notes for this chapter.
:::
:::
