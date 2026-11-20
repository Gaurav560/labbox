:::step{type=story title="The order that vanished"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Our kitchen screens used Redis pub/sub for new orders. It is fast and simple, and last Tuesday a
screen rebooted during lunch and missed eleven orders: they were published while nobody was
listening, and pub/sub does not keep anything. Then a payments worker crashed halfway through two
payments, and nobody noticed for an hour. We need messages that wait for us, and work that cannot
be silently dropped.
:::

:::mission
Put orders on a stream, share them out with a consumer group, and rescue the work a crashed worker left behind.
:::
:::

:::step{type=concept title="Pub/sub forgets; streams remember"}
**Pub/sub** delivers a message to whoever is subscribed *right now*. Nobody listening? The message is
gone. It is perfect for "the price changed, refresh your screen", and wrong for orders.

A **stream** is an append-only log. Every entry gets an ID (a timestamp and a counter, like
`1732012345678-0`) and a few fields, and it **stays** until you trim it:

```text
> XADD orders:stream * order o1 item "filter coffee"
"1732012345678-0"
> XRANGE orders:stream - +
```

`*` asks Redis to choose the ID. `-` and `+` mean "from the oldest to the newest".
:::

:::step{type=example title="Worked example: deliveries on a stream"}
The delivery team logs every pickup on a stream, and reads the log back later:

```text
> XADD deliveries * rider r7 order o41
"1732012345678-0"
> XADD deliveries * rider r9 order o42
"1732012345690-0"
> XLEN deliveries
(integer) 2
> XRANGE deliveries - +
1) 1) "1732012345678-0"   2) 1) "rider" 2) "r7" 3) "order" 4) "o41"
2) 1) "1732012345690-0"   2) 1) "rider" 2) "r9" 3) "order" 4) "o42"
```

1. Each `XADD` returns the ID Redis chose: the time in milliseconds, then a counter.
2. `XLEN` counts entries; reading them never removes them.
3. `XRANGE - +` reads everything, oldest first, each entry with its fields in pairs.
:::

:::step{type=predict title="Guess first"}
:::question
A kitchen screen is offline while three orders are added to a stream. It comes back and reads the stream. What does it see?
:::
- [ ] Nothing: those orders were published while it was away
- [x] All three orders, in order
- [ ] Only the newest order
:::explain
A stream keeps its entries, so a reader can always catch up from where it was. That is the
difference from pub/sub, where a message exists only for the listeners of that moment.
:::
:::

:::step{type=task task=orders_stream title="Orders on a stream"}
Add three orders to the stream `orders:stream`, in this order, each with two fields, `order` and `item`:

| order | item |
|---|---|
| `o1` | `filter coffee` |
| `o2` | `vada pav` |
| `o3` | `cold coffee` |
:::

:::step{type=concept title="Consumer groups: share the work, track it"}
A **consumer group** lets several workers share one stream: each entry goes to **one** of them, and
Redis remembers who has what until they **acknowledge** it.

```text
XGROUP CREATE orders:stream kitchen 0          a group that starts at the oldest entry
XREADGROUP GROUP kitchen barista1 COUNT 3 STREAMS orders:stream >
XACK orders:stream kitchen <id>                 done with this one
XPENDING orders:stream kitchen                  delivered but not acknowledged
```

`>` means "entries nobody in the group has received yet". Until `XACK`, an entry sits in the
**pending list**, owned by the consumer that received it. If that worker dies, the work is not lost:
it is visible, and someone else can claim it.

:::diagram{name="consumer-group"}
The group hands each entry to one worker, and keeps it pending until that worker acknowledges it.
:::

:::trace{title="two riders share the deliveries group"}
| command | pending list | note |
|---|---|---|
| XREADGROUP GROUP riders r7 COUNT 1 ... > | 1-0 (r7) | r7 gets the oldest new entry. |
| XREADGROUP GROUP riders r9 COUNT 1 ... > | 1-0 (r7), 2-0 (r9) | r9 gets the next one, not the same one. |
| XACK deliveries riders 1-0 | 2-0 (r9) | r7 delivered it: acknowledged, off the pending list. |
| (r9 crashes) | 2-0 (r9) | r9's entry is still pending: nothing is lost, someone can claim it. |
:::
:::

:::step{type=task task=kitchen_group title="A kitchen that shares the work"}
Create a consumer group called `kitchen` on `orders:stream`, starting from the **oldest** entry.
Read all three orders as consumer `barista1`, then **acknowledge only the first one** (o1 is made;
o2 and o3 are still in progress).
:::

:::step{type=try title="Look at the crashed worker's work"}
The `billing` group on `payments:stream` has a problem. Look at what is pending, and for how long:

```bash run
redis-cli XPENDING payments:stream billing - + 10
```

Each line shows an entry ID, the consumer holding it, how many milliseconds since it was delivered, and how many times.
:::

:::step{type=task task=reclaim_stuck title="Rescue the stuck payments"}
`worker-crashed` took two payments ten minutes ago and never finished. As consumer `worker-2`,
**claim** every payment that has been pending for more than a minute, then **acknowledge** them.

`XAUTOCLAIM payments:stream billing worker-2 60000 0` claims entries idle for over 60 seconds.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A worker reads an entry with `XREADGROUP`, then crashes before `XACK`. Where is the entry?
:::
- [ ] Gone: it was delivered
- [x] Still in the group's pending list, owned by the crashed worker
- [ ] Back at the end of the stream
:::explain
Until it is acknowledged, an entry stays pending. `XPENDING` shows it, and `XAUTOCLAIM` hands it to a live worker.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which tool fits "tell every open screen that the menu changed, right now"?
:::
- [ ] A stream with a consumer group
- [x] Pub/sub
- [ ] A sorted set
:::explain
A screen that is offline can simply reload the menu later, so losing the notice does no harm. Pub/sub is simple and fast for that; streams are for work that must not be lost.
:::
:::

:::step{type=deep-dive title="Running streams in production"}
**Trim, or it grows forever.** `XADD orders:stream MAXLEN ~ 100000 * ...` keeps about the newest
100000 entries; `~` lets Redis trim in cheap whole blocks.

**At-least-once, so be idempotent.** A worker can finish the work, then crash before `XACK`; the
entry will be delivered again. Make handlers safe to run twice (the idempotency keys of chapter 7).

**Poison messages.** An entry that crashes every worker is redelivered forever. `XPENDING` shows a
delivery count: past a limit, move the entry to a dead-letter stream and alert someone.

**When to reach for Kafka.** Streams handle a lot, but they live in memory on one node. For long
retention, huge volumes or replay across many teams, a disk-based log like Kafka fits better.
:::

:::step{type=recap}
- Pub/sub delivers only to current listeners; a stream keeps every entry with an ID.
- `XADD`, `XRANGE` write and read; `MAXLEN ~` keeps a stream bounded.
- A consumer group shares entries between workers and tracks them until `XACK`.
- Pending entries survive crashes; `XAUTOCLAIM` hands stuck work to a live worker.
:::
