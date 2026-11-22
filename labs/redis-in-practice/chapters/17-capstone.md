:::step{type=story title="Production is slow, and it is your shift"}
It is 11 pm. Basket's dashboard shows response times jumping: most requests are quick, but every few seconds a
burst of them takes ten or twenty times longer than usual. Customers are noticing. The team chat has already
started guessing: "Is it the network?" "Is Redis overloaded?" "Should we restart it?"

The first people to do this for a living were NASA's flight controllers, here in Mission Control during Apollo 9 in 1969: watch the numbers, find the cause, fix it calmly. Production incidents are still run the same way.

:::photo{src="/lesson-images/redis/apollo-mission-control.webp" alt="Rows of flight controllers at consoles with small screens, facing a wall of large displays, in NASA's Mission Control room" credit="NASA" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Mission_Operations_Control_Room_during_Apollo_9.jpg"}
Mission Control during Apollo 9, 1969.
:::

You have everything you need to answer properly, from this whole course. Redis runs one command at a time (chapter
2). Some commands are slow by nature, and the slow log remembers them (chapter 13). Big keys are dangerous to read
and dangerous to delete (chapters 13 and 14). This capstone puts them together, the way a real incident does:
gather the facts, find the cause, fix it without making things worse, and say what should change.

Three things are waiting in this Redis: 30,000 customer sessions, a huge analytics key, and an ops dashboard that
calls `GET /sessions/active` every few seconds.

:::mission
Make the dashboard count sessions without blocking Redis, and remove the slow key the safe way.
:::
:::

:::step{type=try title="Gather the facts: the slow log" file="17-capstone/app.py" line="16-21"}
Start the dashboard's app and ask it a few times, the way the dashboard does:

```bash run
cd /workspace/17-capstone && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

```bash run
curl -s -w "  %{time_total} s\n" localhost:8000/sessions/active
```

```text
{"active":30000}  0.031811 s
```

It answers, and not even slowly. But "it is fast for me" is not the question; the question is what it does to
**everybody else**. The slow log knows. This Redis logs every command slower than 2 ms:

```bash run
redis-cli SLOWLOG GET 5
```

In this lab it showed (shortened to the important fields: the id, the duration in microseconds, and the command):

```text
1) 1) (integer) 6
   3) (integer) 2591
   4) 1) "KEYS"
      2) "session:*"
2) 1) (integer) 5
   3) (integer) 2399
   4) 1) "KEYS"
      2) "session:*"
3) 1) (integer) 4
   3) (integer) 8708
   4) 1) "ZRANGE"
      2) "analytics:raw"
      3) "0"
      4) "-1"
      5) "WITHSCORES"
4) 1) (integer) 3
   3) (integer) 13316
   4) 1) "ZRANGE"
      2) "analytics:raw"
      3) "0"
      4) "-1"
```

Two culprits:

1. **`KEYS session:*`**, about 2.5 ms each time, sent by the dashboard (look at line 21 on the right). Every few
   seconds, every other client waits 2.5 ms. And it grows with the number of keys.
2. **`ZRANGE analytics:raw 0 -1`**, 9 to 13 ms each time: a nightly report reading a huge sorted set in one go.

Check the second one's size:

```text
> ZCARD analytics:raw
(integer) 150000
> MEMORY USAGE analytics:raw
(integer) 18026528
```

150,000 members, 18 MB, in one key. And `INFO commandstats` confirms the first: `cmdstat_keys:calls=2,usec=4990,
usec_per_call=2495.00`.
:::

:::step{type=concept title="SCAN: walk the keys in small steps"}
`KEYS session:*` has to look at **every key in the database** to find the matching ones, and it does it as one
command. Here that is 30,002 keys in 2.5 ms. The time grows in step with the number of keys: by the same rate, a
Redis with 10 million keys would take most of a second, every few seconds, with nobody else served meanwhile. That
is why `KEYS` is banned on production servers at many companies.

**SCAN** finds the same keys in **small pieces**. Each call looks at a small batch of keys and returns two things:
the matching keys from that batch, and a **cursor**, a number that says where to continue. You call it again with
that cursor, and again, until the cursor comes back as `0`:

Here are the first three steps in this lab, starting from cursor `0`:

| Call | Cursor it returned | Keys it returned |
|---|---|---|
| `SCAN 0 MATCH session:* COUNT 1000` | 10512 | 1000 |
| `SCAN 10512 MATCH session:* COUNT 1000` | 19208 | 1000 |
| `SCAN 19208 MATCH session:* COUNT 1000` | 17816 | 1001 |

The cursors jump around (they are positions in Redis's internal table, not counts), and the walk is done when a
call returns cursor `0`.

`COUNT 1000` is a hint for how much work to do per call, not how many keys come back. Between two calls, Redis
serves everybody else, so no client ever waits long.

You do not have to handle the cursor yourself in Python: `r.scan_iter(match="session:*", count=1000)` makes all
the calls for you and gives you the keys one by one, ready for a loop or a `sum(1 for _ in ...)`.

Two honest small print points. SCAN does more work in total than KEYS (many small calls instead of one), and if
keys are added or removed while it walks, it may return a key twice or miss a brand-new one. For a dashboard
count, both are fine. For anything else, design so that a duplicate does no harm.

:::diagram{name="slow-command"}
One big command has Redis to itself; with SCAN, other clients' commands run between the small steps.
:::
:::

:::step{type=task task=scan_not_keys title="Your turn: count sessions without KEYS"}
Change `active_sessions()` in `17-capstone/app.py` to count the `session:*` keys with SCAN, in steps of about
1000, instead of `KEYS`. The answer must stay the same: `{"active": 30000}`.

Press **Check**: it watches `INFO commandstats` while your endpoint runs, and fails if `KEYS` was called.
:::

:::step{type=concept title="Removing a big key: DEL or UNLINK"}
Now the analytics key. It is a leftover: raw events that a report reads every night in one huge `ZRANGE`, and
nobody needs it any more. Deleting it is the fix. But **how** you delete it matters, because freeing 150,000
members is real work.

`DEL` frees the key **and all its members** right away, inside the command. Here is a test in this lab, on an
exact copy of the key (made with `COPY analytics:raw analytics:copy`):

```text
> DEL analytics:copy
(integer) 1
```

and the slow log caught it:

```text
1) 1) (integer) 8
   3) (integer) 13331
   4) 1) "DEL"
      2) "analytics:copy"
```

13 ms of freezing to delete one key. `UNLINK` does the same job in two halves: it removes the **key** from the
database at once (so nobody can see it any more), and hands the freeing of its memory to a background thread.

```text
> UNLINK analytics:raw
(integer) 1
```

That one did not appear in the slow log at all. Same result for every client, none of the waiting. (Redis can
also be told to make `DEL` behave like `UNLINK` with `lazyfree-lazy-user-del yes`, but typing `UNLINK` says what
you mean.)

**Check yourself:** right after `UNLINK analytics:raw`, what does `EXISTS analytics:raw` answer? (`0`: the key is
gone at once; only the memory is freed later.)
:::

:::step{type=task task=unlink_culprit title="Your turn: remove the slow key"}
Remove the key behind the slow `ZRANGE` entries, **without blocking Redis** while its memory is freed. Leave the
30,000 sessions alone.

Press **Check**: it looks in the slow log for a `DEL` of that key, so a blocking delete fails the task (Reset lab
lets you try again).
:::

:::step{type=try title="After the fix"}
With both tasks done, this lab's dashboard endpoint answered the same number:

```text
{"active":30000}  0.032775 s
```

and `INFO commandstats` showed how it got there:

```text
cmdstat_scan:calls=30,usec=4658,usec_per_call=155.27,rejected_calls=0,failed_calls=0
```

Thirty small `SCAN` calls of about 0.16 ms each instead of one `KEYS` of 2.5 ms: a little more work in total, but
no client ever waited more than a fraction of a millisecond for the dashboard. And `KEYS` does not appear at all.

`EXISTS analytics:raw` answered `(integer) 0`, `DBSIZE` showed the 30,000 sessions still there, and the slow log
stayed quiet. Incident over.
:::

:::step{type=concept title="Writing it up"}
A real incident ends with a short write-up, so the same thing never happens again. It is called a **post-mortem**,
and good teams write it without blame: the question is what in the **system** let this happen, not who typed
what. Here is this one, as you would write it:

| | |
|---|---|
| **What happened** | Every few seconds, requests to Redis took several milliseconds longer than usual. |
| **Cause** | Two O(N) commands on the single Redis thread: the dashboard's `KEYS session:*` every few seconds, and a nightly report's `ZRANGE` over a 150,000 member key. |
| **How it was found** | `SLOWLOG GET`, confirmed with `INFO commandstats`, `ZCARD` and `MEMORY USAGE`. |
| **Fix** | The dashboard counts with `SCAN`; the unused key was removed with `UNLINK`. |
| **So it does not happen again** | Ban `KEYS` in code review (or rename it with `rename-command` on servers); keep collections bounded (trim, TTLs, one key per day); keep the slow log on (chapter 13) and alert on it. |

Notice what the fix did **not** need: a bigger server, a restart, or a guess. Measure, find, fix, prevent.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Your dashboard must count keys matching `session:*` every minute. What should it use?
:::
- [ ] `KEYS session:*`
- [x] `SCAN` with `MATCH session:*`, in small steps
- [ ] `DBSIZE`
:::explain
`SCAN` walks the keyspace a little at a time, so other clients are served in between. `DBSIZE` counts every key,
not only sessions. (Better still: keep a counter or a set of active sessions, so nothing has to be counted at
all.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A key holds 5 million list items and must go. Which is safest?
:::
- [ ] `DEL` it during quiet hours
- [x] `UNLINK` it: removed at once, memory freed in the background
- [ ] `FLUSHALL`
:::explain
`DEL` would freeze Redis while it frees 5 million items, quiet hours or not. `FLUSHALL` would delete everything
else too.
:::
:::

:::step{type=design title="Final design review"}
You have run Redis from your first `SET` to a production incident. Show how you would run it.

:::ask{id=monitoring}
Redis is your cache, your session store and your queue. Which numbers would you watch and alert on, and why?
:::

:::ask{id=big_keys}
A product team wants one sorted set holding every event of every customer, forever. What would you tell them, and how would you design it instead?
:::

:::ask{id=not_redis}
Name a kind of data you would not keep only in Redis, and explain why.
:::
:::

:::step{type=deep-dive title="Go deeper: where to go from here"}
You have covered what most teams use Redis for every day. Some directions for later:

**Redis Stack and modules.** Extra data types and features: JSON documents you can update field by field, full-text
search and secondary indexes, time series, and probabilistic structures such as Bloom filters. Since Redis 8 many
of them ship with Redis itself.

**Vector search.** Redis can store embeddings (lists of numbers that describe text or images) and find the most
similar ones fast, which is how many AI apps add "search by meaning" and caching of model answers. LabBox's AI
track uses ideas you now know: a cache in front of a slow, paid model is chapter 7 and 8 all over again, with
bigger savings.

**Client-side caching.** Redis 6 added a protocol (RESP3 with tracking) that lets apps keep a copy of hot keys in
their own memory, and Redis tells them when a key changes, removing even the round trip.

**Running it yourself versus managed.** Self-hosting means owning upgrades, failover, backups and security
(passwords and ACLs, TLS, never exposing port 6379 to the internet). Managed services do most of that for a fee.
Either way, the questions in this course are the ones you will be asked: what does it save, what does it cost,
what happens when it is full, and what happens when it dies.
:::

:::step{type=recap}
You can now:

- investigate a slow Redis from facts: `SLOWLOG GET`, `INFO commandstats`, `ZCARD`, `MEMORY USAGE`;
- replace `KEYS` with `SCAN` (`scan_iter` in Python), and explain the trade-off;
- remove a big key without freezing Redis, with `UNLINK`;
- write a blameless post-mortem: what happened, cause, how it was found, fix, and prevention.

You have finished Redis in practice: from why a millisecond matters, through caching that pays for itself, to
running Redis in production. Well done.

:::photo{src="/lesson-images/redis/redis-17-notes.webp" alt="Handwritten notes about production is slow: 1. SLOWLOG GET; 2. INFO commandstats; SCAN, never KEYS; UNLINK big keys; measure, find, fix, prevent" ai="true"}
One page of notes for this chapter.
:::
:::
