:::step{type=story title="Where did order o2 go?"}
When a customer places an order, several things must happen: the store packs it, a rider is assigned, the
customer gets a text. Basket's first design used chapter 4's list as a queue: the app pushes the order, a packing
worker pops it.

It worked for months. Then one day a packing worker crashed, right after popping order o2 and before packing it.
The order had already left the list. Nobody else could see it. The customer waited, and waited.

That is the weakness of a list queue: once a worker takes a job, the job exists **only** in that worker. If the
worker dies, the job dies with it. For orders and payments, that is not acceptable.

Redis has a type built for exactly this: the **stream**. It keeps every entry, remembers which worker is busy with
which one, and lets another worker take over when one disappears.

:::mission
Put orders on a stream, share them out to a packing team that acknowledges its work, and rescue payments a
crashed worker left behind.
:::
:::

:::step{type=concept title="A stream is a log that remembers"}
A **stream** is an **append-only log**: entries are only ever added at the end, and each one gets an **ID** from
Redis. An entry holds a few field and value pairs, like a small hash. Stream commands start with **X**.

Stock exchanges had streams long before computers. A stock ticker like this one, built by Thomas Edison around 1870, printed every trade onto a paper tape as it happened: an append-only record, in order, that any broker could read without taking anything away.

:::photo{src="/lesson-images/redis/edison-ticker.webp" alt="A brass and black stock ticker machine under glass, with a roll of paper tape beside its printing wheel" credit="H. Zimmer" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Edison_Stock_Telegraph_Ticker.jpg"}
Edison's stock telegraph ticker.
:::

```text
> XADD deliveries:stream '*' rider r7 parcel p1
"1795356002481-0"
> XADD deliveries:stream '*' rider r9 parcel p2
"1795356002536-0"
```

`XADD` takes the stream's key, the ID, and the fields. `'*'` means "Redis, choose the ID". The ID it chose is two
numbers: the time in **milliseconds since 1970** when the entry was added (1795356002481 is in November 2026),
and a sequence number for entries added in the same millisecond. IDs only ever grow, so they also give you the
order.

Unlike `RPOP` on a list, **reading a stream does not remove anything**:

```text
> XRANGE deliveries:stream - +
1) 1) "1795356002481-0"
   2) 1) "rider"
      2) "r7"
      3) "parcel"
      4) "p1"
2) 1) "1795356002536-0"
   2) 1) "rider"
      2) "r9"
      3) "parcel"
      4) "p2"
```

`XRANGE key - +` reads from the very first ID (`-`) to the last (`+`). Each entry shows its ID, then its fields.
`XLEN deliveries:stream` answers `(integer) 2`, and it will still say 2 after any number of reads.

So the log is a permanent record: what happened, in what order. That is the difference from **pub/sub**, Redis's
older messaging feature (`PUBLISH` and `SUBSCRIBE`). A published message goes only to whoever is listening at
that moment: `PUBLISH news hello` answered `(integer) 0` in this lab, meaning nobody received it, and it is gone
for good. A stream entry waits until someone reads it.

**Check yourself:** you read a stream with `XRANGE` ten times. How many entries are left? (All of them.)
:::

:::step{type=example title="Worked example: deliveries on a stream"}
Here is the full life of the two deliveries above, read the simple way. `XREAD` reads entries **after** a given ID;
`0` means "from the beginning":

```text
> XREAD COUNT 10 STREAMS deliveries:stream 0
```

It answered the stream's name, then both entries (the same fields as `XRANGE` showed). A tracking screen would
remember the last ID it saw (`1795356002536-0`) and next time ask only for what came after it. With `BLOCK 5000`
added, `XREAD` waits up to five seconds for new entries instead of answering empty, just like `BRPOP` in chapter 4.

1. `XADD` appends; Redis picks an ID that tells time and order.
2. `XRANGE` and `XREAD` read without removing; any number of readers can read the same entries.
3. A reader keeps track of its own position by remembering the last ID it has seen.

That is enough for a screen that shows deliveries. For a **team of workers sharing the work**, where each order
must be packed by exactly one of them and nothing may be lost, you need one more idea.
:::

:::step{type=predict title="Guess first"}
:::question
A list queue and a stream both hold order o2. A worker takes o2 and crashes before finishing it. Where is o2 now?
:::
- [ ] In both cases, back at the front of the queue
- [x] With a list (`RPOP`), it is gone; with a stream, it is still in the log, and a consumer group knows nobody finished it
- [ ] In both cases, gone
:::explain
`RPOP` removes the entry, so only the dead worker ever had it. A stream keeps every entry, and a consumer group
(next) records that o2 was handed out but never acknowledged.
:::
:::

:::step{type=task task=orders_stream title="Your turn: orders on a stream"}
Put Basket's first three orders of the day on a stream called `orders:stream`, in this order, each with two
fields, `order` and `item`:

| order | item |
|---|---|
| `o1` | `rice` |
| `o2` | `dal` |
| `o3` | `mangoes` |

Let Redis choose the IDs. `XRANGE orders:stream - +` should show all three, oldest first. Press **Check**.
:::

:::step{type=concept title="Consumer groups: share the work, track it"}
A **consumer group** is a team of readers that **share** a stream: each entry is handed to exactly one member of
the team, and the group remembers who has which. Members are called **consumers**, and each has a name.

Create a group on the deliveries stream, starting from the beginning (`0`):

```text
> XGROUP CREATE deliveries:stream tracking 0
OK
```

Now two consumers, `app1` and `app2`, each ask the group for one new entry. `>` means "entries never handed to
anyone in this group yet":

```text
> XREADGROUP GROUP tracking app1 COUNT 1 STREAMS deliveries:stream '>'
```

`app1` received the first delivery (r7, p1). Then `app2` asked and received the **second** (r9, p2), not the first
again. When `app2` asked once more, it got `(nil)`: nothing left to hand out.

Here is the important part. Handing an entry out does not mean it is done. The group keeps a **pending entries
list**: everything handed out but not yet **acknowledged**:

```text
> XPENDING deliveries:stream tracking
1) (integer) 2
2) "1795356002481-0"
3) "1795356002536-0"
4) 1) 1) "app1"
      2) "1"
   2) 1) "app2"
      2) "1"
```

Two pending entries, from the first ID to the last, one held by `app1` and one by `app2`. When a consumer
finishes an entry, it says so with `XACK`:

```text
> XACK deliveries:stream tracking 1795356002481-0
(integer) 1
```

Now `XPENDING` shows only one pending entry, held by `app2`. If `app2` crashes, its entry does not vanish: it stays
pending, with `app2`'s name on it, until someone deals with it.

:::diagram{name="consumer-group"}
The group hands each entry to one consumer; it stays pending until that consumer acknowledges it.
:::
:::

:::step{type=task task=kitchen_group title="Your turn: a packing team that shares the work"}
Set up Basket's packing team on `orders:stream`:

1. Create a consumer group called `packing`, starting from the beginning of the stream.
2. As consumer `packer1`, read **all three** orders from the group (`COUNT 3`, with `>`).
3. `packer1` has packed the first order. Acknowledge **only** that one, using its ID.

`XPENDING orders:stream packing` should now show two pending orders, both held by `packer1`. Press **Check**.
:::

:::step{type=try title="Look at a crashed worker's work"}
The lab has a second stream, `payments:stream`, with a group called `billing`. A worker named `worker-crashed` read
two payments from it, then died before acknowledging either. Look:

```text
> XPENDING payments:stream billing
1) (integer) 2
2) "1795356009588-0"
3) "1795356009600-0"
4) 1) 1) "worker-crashed"
      2) "2"
```

For details, ask for the pending entries themselves, from `-` to `+`, up to 10:

```text
> XPENDING payments:stream billing - + 10
1) 1) "1795356009588-0"
   2) "worker-crashed"
   3) (integer) 600269
   4) (integer) 2
2) 1) "1795356009600-0"
   2) "worker-crashed"
   3) (integer) 600266
   4) (integer) 2
```

Each line: the entry's ID, who holds it, how long it has been **idle** in milliseconds (600,269 ms is ten minutes),
and how many times it has been handed out. Ten minutes without an acknowledgement means the holder is not coming
back. (Your IDs and times will be different.)

Rescuing them takes one command, `XAUTOCLAIM`: "hand to this consumer every pending entry of this group that has
been idle at least this long". Here it was run for `worker-2`, with a minimum idle time of 60,000 ms (one
minute), starting from ID `0`:

```text
> XAUTOCLAIM payments:stream billing worker-2 60000 0
1) "0-0"
2) 1) 1) "1795356009588-0"
      2) 1) "order"
         2) "o101"
         3) "amount"
         4) "120"
   2) 1) "1795356009600-0"
      2) 1) "order"
         2) "o102"
         3) "amount"
         4) "45"
3) (empty array)
```

The first line, `"0-0"`, means "nothing more to scan". Then the two entries, now handed to `worker-2`, with their
fields so it can process them. `XPENDING` would now show both held by `worker-2`, still pending until it
acknowledges them.
:::

:::step{type=task task=reclaim_stuck title="Your turn: rescue the stuck payments"}
Finish the crashed worker's payments:

1. Claim every pending entry of `payments:stream` in the group `billing` that has been idle for at least one minute,
   for the consumer `worker-2`.
2. `worker-2` has now processed them: acknowledge **both**, by their IDs. Do not delete them from the stream.

`XPENDING payments:stream billing` should show 0 pending. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A consumer reads an entry with `XREADGROUP` and finishes the work, but forgets `XACK`. What happens to the entry?
:::
- [ ] It is deleted after an hour
- [x] It stays in the pending list, and after enough idle time another consumer may claim it and do the work again
- [ ] Nothing: reading it was enough
:::explain
Without `XACK` the group cannot know the work was done, so the entry looks stuck. Real workers acknowledge right
after finishing, and design their work so that doing it twice is harmless.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Basket needs both a live "new order" sound on the store's screen and a reliable record of every order for the
packing team. What fits?
:::
- [ ] Pub/sub for both
- [x] A stream for the orders; pub/sub (or a stream reader) for the screen's sound
- [ ] A list for both
:::explain
Pub/sub is fine for "ping whoever is listening right now", where a missed sound does no harm. Work that must
never be lost belongs in a stream with a consumer group.
:::
:::

:::step{type=deep-dive title="Go deeper: running streams in production"}
**Streams grow forever unless you trim them.** Every entry stays until you remove it. `XADD orders:stream MAXLEN
~ 100000 * ...` keeps roughly the last 100,000 entries (the `~` lets Redis trim in efficient chunks), and
`XTRIM ... MINID` removes entries older than an ID, so older than a time.

**At least once, not exactly once.** A worker might finish the work and crash just before `XACK`. Then the entry is
claimed and done again. So stream workers are written to be **idempotent**: doing an entry twice has the same
effect as doing it once (check "was payment o101 already charged?" before charging).

**Poison messages.** An entry that always crashes its worker would be claimed again and again. The delivery count
(the last number in `XPENDING`'s detail) shows how often it was handed out; after, say, five tries, move it to a
"dead letter" stream for a person to look at.

**Many groups, one stream.** Several groups can read the same stream independently: `packing` hands each order to
one packer, while a separate `notifications` group sends each order's text message. Each group has its own
position and its own pending list.

**When to use something else.** Redis streams live in memory, on one server or one cluster slot per stream. For
years of event history, huge volumes or replaying data into many systems, teams reach for Kafka or a cloud queue,
and keep Redis streams for fast, short-lived work queues.
:::

:::step{type=recap}
You can now:

- append to a stream with `XADD`, and read it without removing anything with `XRANGE` and `XREAD`;
- explain why pub/sub forgets and streams remember;
- share a stream's work in a consumer group with `XREADGROUP`, and confirm finished work with `XACK`;
- find a crashed worker's work with `XPENDING`, and hand it to another consumer with `XAUTOCLAIM`.

That completes Part 2. Next, Part 3 starts with chapter 13: measuring Redis like the people who run it.

:::photo{src="/lesson-images/redis/redis-12-notes.webp" alt="Handwritten notes about streams: XADD: append, Redis picks the ID; reading never removes; a group shares the work; XACK when done; XAUTOCLAIM rescues stuck work" ai="true"}
One page of notes for this chapter.
:::
:::
