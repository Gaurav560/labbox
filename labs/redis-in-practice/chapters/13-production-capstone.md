:::step{type=story title="Everything is slow, nothing is down"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Last call before you graduate. Every few seconds, every app server freezes for a moment, then
recovers. CPU is fine, memory is fine, Redis is up. The ops dashboard looks innocent too: it only
counts active sessions. Find out who is freezing Redis, and fix it like a senior engineer would.
:::

:::mission
Find what blocks Redis, stop the dashboard from freezing it, and remove the culprit without a pause.
:::
:::

:::step{type=concept title="One slow command stops everyone"}
Redis runs one command at a time. A command that touches millions of elements does not just take
long for its caller: **every other client waits** behind it. Two classic offenders:

- `KEYS pattern` walks every key in one go. On millions of keys that is seconds of total silence.
- Reading a huge key whole (`ZRANGE big 0 -1`, `HGETALL big`) or deleting one with `DEL`.

**`SLOWLOG GET 10`** lists the recent commands that took longer than `slowlog-log-slower-than`
microseconds, with how long each took. It is the first place to look.
:::

:::step{type=predict title="Guess first"}
:::question
A key holds 10 million members and you run `DEL` on it. Why is that dangerous on a busy server?
:::
- [ ] It is not: `DEL` is always O(1)
- [x] Freeing 10 million members happens on the main thread, and every client waits
- [ ] `DEL` refuses keys over a million members
:::explain
`DEL` must free every member before it returns, on the one thread that serves everyone. `UNLINK`
removes the key name at once and frees the memory in a background thread.
:::
:::

:::step{type=try title="Read the slow log"}
```bash run
redis-cli SLOWLOG GET 5
```

Each entry shows an ID, a timestamp, how long it took (in microseconds), and the command itself.

```bash run
redis-cli INFO commandstats | grep -E "cmdstat_(keys|scan|zrange)"
```
:::

:::step{type=task task=scan_not_keys title="A dashboard that does not freeze Redis"}
`GET /sessions/active` counts sessions with `KEYS`. Make it count them with **`SCAN`** instead (in
Python, `r.scan_iter(match=..., count=...)` walks the keys in small steps), and keep the count exact.
:::

:::step{type=task task=unlink_culprit title="Remove the culprit, without a pause"}
The slow log points at one huge key. Remove it in a way that does **not** block Redis while its memory
is freed. Keep every session.
:::

:::step{type=design title="Final design review"}
You have run Redis from your first `SET` to production incidents. Show how you would run it.

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

:::step{type=recap}
- One slow command blocks every client: Redis has one main thread.
- `SLOWLOG` and `INFO commandstats` show who is slow and how often.
- `SCAN` instead of `KEYS`, and read big keys in pages (`ZSCAN`, `HSCAN`, ranges).
- `UNLINK` frees big keys in the background; better still, never let keys grow without bound.
:::
