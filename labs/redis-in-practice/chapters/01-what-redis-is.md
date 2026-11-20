:::step{type=story title="The database is tired"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Brew Point has forty coffee outlets, and every one of them asks our Postgres database the same
questions all day: how many cups did we sell, what is on the menu, who is logged in. Postgres
answers every time, but it is tired, and lunch rush is getting slow.

Most of those questions do not need a full database. They need something closer to a notebook
on the counter: tiny, instant, always at hand. That notebook is called Redis, and this week it is yours.
:::

:::mission
Talk to Redis for the first time: store a few values, count cups without losing a single one, and tidy up after an old script.
:::
:::

:::step{type=history title="The story of Redis"}
Redis began as one developer's fix for his own slow website, and became the fast memory behind much
of the internet.

:::before{title="Before Redis"}
In 2009 a web app kept almost everything in a relational database on disk. Busy sites put
**memcached** in front of it: fast, but it stored only plain strings, forgot everything on a restart,
and could not count, queue or rank. Anything smarter meant another trip to the database.
:::

:::solved
**A data structure server.** Redis keeps strings, hashes, lists, sets, sorted sets and counters in
memory, with commands that change them in one step, and can save them to disk. A counter, a queue, a
leaderboard or a session became one command each.
:::

Redis was created by **Salvatore Sanfilippo** (known as antirez) in Sicily, to make his real-time web
analytics product fast. The name is short for **REmote DIctionary Server**. Today it is developed by
**Redis Ltd** with a large open-source community; after a licence change in 2024, the Linux Foundation
started an open fork called **Valkey**, and Redis 8 added an open-source licence again in 2025.

:::timeline
- **2009** Salvatore Sanfilippo releases Redis.
- **2015** Redis 3.0 adds Redis Cluster: one dataset spread over many servers.
- **2018** Redis 5 adds streams, the log-shaped type you will use in chapter 9.
- **2024** A licence change; the Linux Foundation starts the Valkey fork.
- **2025** Redis 8 is released with an open-source licence option again.
:::

:::usedby{title="Used for"}
- Caching
- Sessions and logins
- Rate limiting
- Leaderboards
- Queues and jobs
- Real-time analytics
:::

:::usedby{title="Used at"}
- Twitter
- GitHub
- Stack Overflow
- Instagram
- Craigslist
:::

:::funfact
The very first prototype of Redis was written in **Tcl**, a scripting language, before Salvatore
rewrote it in C. The single-threaded design from those first days is still why Redis is so predictable.
:::
:::

:::step{type=concept title="A dictionary that lives on a server"}
If you have used a Python `dict` or a JavaScript object, you already understand Redis. It stores
**keys** and their **values**, and you ask for a value by its key:

```text
shop:name   ->  "Brew Point"
cups:sold   ->  "128"
```

The difference is where it lives. A dict lives inside one program and vanishes when it stops.
Redis is a **server**: every app, every outlet and every worker can share the same dictionary,
over the network. And it keeps everything **in memory**, so a read or a write usually takes well
under a millisecond.

That is why Redis sits in front of almost every busy website: caching, sessions, counters, queues,
leaderboards.

:::diagram{name="redis-shared"}
Every outlet and worker talks to one Redis, in memory; Postgres keeps the full records on disk.
:::
:::

:::step{type=example title="Worked example: one key, from start to finish"}
Here is the whole life of a key, the way you will see it in `redis-cli`:

```text
> SET shop:phone "020 4455 6677"
OK
> GET shop:phone
"020 4455 6677"
> EXISTS shop:phone
(integer) 1
> DEL shop:phone
(integer) 1
> GET shop:phone
(nil)
```

1. `SET` stores the value and answers `OK`.
2. `GET` reads it back. The quotes were only needed because of the spaces.
3. `EXISTS` answers `1` for "there", `0` for "not there".
4. `DEL` answers how many keys it deleted, and after that the key is gone: `(nil)`.
:::

:::step{type=try title="Your first conversation"}
`redis-cli` is a terminal for talking to Redis, already pointed at it. You type a command; Redis
answers in one line. `PING` is the "are you there?" of Redis:

```bash run
redis-cli PING
```

`SET` stores a value and `GET` reads it back:

```bash run
redis-cli SET greeting "Hello from Brew Point"
```

```bash run
redis-cli GET greeting
```

Now ask for a key that does not exist: `redis-cli GET shop:phone` answers `(nil)`, Redis for "no such
key". Commands are not case sensitive, but keys are: `Shop:Name` is a different key from `shop:name`.
Quotes matter only when a value has spaces.

Type `redis-cli` on its own to open an interactive prompt, handier for several commands in a row.
`exit` leaves it.
:::

:::step{type=task task=first_keys title="Introduce the shop"}
Store two facts about the shop, as plain text values:

| key | value |
|---|---|
| `shop:name` | `Brew Point` |
| `shop:city` | `Pune` |
:::

:::step{type=concept title="Counting without losing a count"}
Forty outlets sell coffee at the same moment. Picture two of them updating the cup counter the
obvious way: each **reads** 128, adds one, and **writes** 129. Two cups were sold; the counter
moved by one. This is a **race condition**, and it quietly loses money.

Redis has a command that does the read, the add and the write as **one step**:

```text
> INCR cups:sold
(integer) 129
```

Nothing can sneak in between, because Redis runs one command at a time, start to finish. There is
`INCRBY key 5` to add more than one, and `DECR` and `DECRBY` to subtract.

:::trace{title="two outlets sell a cup at the same moment"}
| moment | outlet A | outlet B | counter | note |
|---|---|---|---|---|
| start |  |  | 128 | Two cups are about to be sold, one in each outlet. |
| A reads | GET: 128 |  | 128 | The obvious way: read the number first. |
| B reads |  | GET: 128 | 128 | B reads before A has written: it also sees 128. |
| A writes | SET 129 |  | 129 | A adds one and writes 129. |
| B writes |  | SET 129 | 129 | B also writes 129. Two cups sold, the counter moved by one. |
| with INCR | INCR: 129 | INCR: 130 | 130 | Each INCR reads, adds and writes as one step: nothing gets in between. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
The key `visits` does not exist yet. What does `INCR visits` do?
:::
- [ ] It fails with an error: there is nothing to add to
- [x] It creates `visits` with the value 1
- [ ] It returns `(nil)` and changes nothing
:::explain
A missing key counts as 0, so `INCR` creates it and returns 1. That is why counters in Redis need
no setup step: the first `INCR` makes them.
:::
:::

:::step{type=task task=cups_counter title="Count the cups"}
Two jobs for the morning shift:

1. Three cups were just sold. Record them in a counter called `cups:sold`, one `INCR` per cup.
2. The bean stock `beans:grams` is already in Redis. A 250 gram batch went into the grinder:
   take 250 off the stock, without retyping the whole number.

Use `GET` to look before and after.
:::

:::step{type=concept title="Naming keys, and cleaning up"}
Redis has no tables. Teams keep thousands of keys tidy with a **naming convention**: parts joined
by colons, from general to specific.

```text
user:42:name     cups:2026-11-19     session:7f3a
```

To remove keys, `DEL` takes one or more names and says how many it deleted. `EXISTS` says whether
a key is there.

To find keys by pattern, `KEYS tmp:*` works on your laptop, but never on a busy server: it walks
every key while everyone else waits. In production you use `SCAN`, which walks in small pieces.
More on that in the last chapter.
:::

:::step{type=task task=clean_up title="Tidy up after the import script"}
An old import script left temporary keys behind, all starting with `tmp:import:`. Find them and
delete every one of them. Leave everything else alone.

```bash
redis-cli --scan --pattern 'tmp:*'
```
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`EXISTS shop:email` answers `0`. What does `GET shop:email` answer?
:::
- [ ] An error
- [x] `(nil)`
- [ ] `""`, an empty string
:::explain
A missing key reads as `(nil)`, not an error and not an empty string. Code that reads Redis must
always be ready for "not there".
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does `INCR` never lose a count, even when 40 outlets use it at once?
:::
- [ ] It locks the key for a second
- [x] Redis runs one command at a time, and `INCR` reads, adds and writes in that one command
- [ ] It retries when two outlets clash
:::explain
There is no gap between the read and the write for another outlet to slip into. That one-at-a-time
design is also why one slow command delays everyone.
:::
:::

:::step{type=deep-dive title="Why is Redis so fast?"}
Three reasons, and they explain most of how Redis behaves.

**Memory, not disk.** Reading RAM takes about 100 nanoseconds; a random read from an SSD takes
about 100 microseconds, a thousand times longer.

**One command at a time.** Redis runs commands on a single thread, one after another. No locks, no
waiting for other threads. This is also why `INCR` is safe: nothing runs in the middle of it. The
catch: one slow command delays *everyone*, which is why `KEYS *` on a big server is dangerous.

**Simple, well-chosen data structures.** Most commands touch one key and take the same time no
matter how big your data is (O(1)). Redis also keeps small values in compact encodings, so it
stays fast while using little memory.
:::

:::step{type=recap}
- Redis is a shared dictionary on a server, kept in memory: reads and writes in well under a millisecond.
- `SET`, `GET`, `DEL` and `EXISTS` are the basics; `(nil)` means no such key.
- `INCR`, `INCRBY`, `DECRBY` change a number in one step, so concurrent updates never get lost.
- Name keys like `shop:city` and find them with `SCAN`, never `KEYS`, on a busy server.
:::
