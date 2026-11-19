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
