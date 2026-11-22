:::step{type=story title="Is Redis slow, or is something else?"}
Welcome to Part 3, where you look after Redis the way the people who run it in production do.

It is Monday morning. A message arrives in Basket's team chat: "The app was slow last night around 11 pm. Redis
again?" Someone suggests a bigger server. Someone else suggests switching Redis off and on again.

Neither is engineering. The first question is always the same: **what do the measurements say?** Was every
request slow, or a few? Was Redis slow to answer, or was the network slow, or the app? Was it one command that
froze everything for a moment?

Redis comes with excellent tools to answer exactly these questions, and you have already used two of them in
chapter 1. In this chapter you learn the rest: how throughput changes with the way you use Redis, why some
commands are slow by nature, and how to find the culprit afterwards in the **slow log**, which somebody has
switched off.

:::mission
Find the slowest command behind last night's trouble in the slow log, and switch the slow log back on properly.
:::
:::

:::step{type=concept title="Three things to measure"}
Performance questions about Redis come down to three measurements, and each has its own tool.

| What | The question it answers | Tool |
|---|---|---|
| **Latency** | how long does one request take, there and back? | `redis-cli --latency` (chapter 1) |
| **Throughput** | how many requests a second can Redis serve? | `redis-benchmark` (chapter 1) |
| **Slow commands** | which commands took long, and on which keys? | the **slow log**, `INFO commandstats` |

They are connected by the most important fact of the course: Redis runs **one command at a time**. If one command
takes 5 ms, every client waiting behind it gets an extra 5 ms of latency, and throughput drops while it runs. So a
single slow command shows up in all three measurements at once, which is why finding it matters so much.

Latency also has two parts you must keep apart:

- **Server time**: how long Redis spends on the command itself, usually a microsecond or two.
- **Round trip**: the server time plus the trip over the network both ways (chapter 6).

When "Redis is slow", it is very often the round trips (too many of them, or a slow network), not Redis. The slow
log only measures server time, so it tells you which of the two you are looking at.
:::

:::step{type=try title="Throughput, four ways"}
`redis-benchmark` has options that show how much the **way** you use Redis changes what it can do. Here are four
runs from this lab, all of `GET` and `SET` on one Redis with one CPU core:

```bash run
redis-benchmark -t get -n 100000 -q
```

```text
GET: 207900.20 requests per second, p50=0.127 msec
```

That is the default: 50 clients at once, tiny values. Now **one** client (`-c 1`), sending one command and waiting
for each answer:

```text
GET: 93023.26 requests per second, p50=0.015 msec
```

Fewer than half the requests per second, even though each one is answered faster: a single client spends most of
its time waiting for the network. Now 50 clients, each **pipelining** 16 commands at a time (`-P 16`, chapter 6):

```text
GET: 2222222.25 requests per second, p50=0.295 msec
```

**Over two million a second**, ten times the default, from the same Redis. Pipelining lets Redis read and answer
many commands per network trip. Finally, values of 100 KB each instead of 3 bytes
(`-t set,get -n 20000 -q -d 100000`):

```text
SET: 7358.35 requests per second, p50=2.663 msec
GET: 41841.00 requests per second, p50=0.263 msec
```

The same Redis now manages only about **7,000** writes a second, and the median write takes 2.7 ms instead of
0.13 ms: every request moves a hundred thousand bytes. Put together:

| How Redis is used | GETs per second, this lab |
|---|---|
| one client, one command at a time | 93,023 |
| 50 clients | 207,900 |
| 50 clients, pipelines of 16 | 2,222,222 |
| 50 clients, 100 KB values (SET) | 7,358 |

The lesson: **how you use Redis matters more than Redis itself.** Many small round trips, or big values, cost far
more than any setting on the server.
:::

:::step{type=concept title="Big O: why some commands are slow by nature"}
Most Redis commands are **O(1)**, said "order one": they take the same short time whether the database holds ten
keys or ten million. `GET`, `SET`, `INCR`, `HGET`, `SADD`, `LPUSH` are all O(1).

Some commands are **O(N)**: their time grows with N, the number of elements they touch. Reading a whole
collection is O(N), and on a big collection that adds up fast. The lab's report key is big:

```text
> ZCARD report:2025
(integer) 100000
> MEMORY USAGE report:2025
(integer) 9689376
```

A sorted set of 100,000 members, almost 10 MB. Asking for all of it at once (`ZRANGE report:2025 0 -1`) makes
Redis walk all 100,000 members and build one huge answer, while every other client waits.

| Command | Cost | Careful with |
|---|---|---|
| `GET`, `SET`, `INCR`, `HGET`, `SADD`, `SISMEMBER` | O(1) | big values (this chapter's 100 KB test) |
| `ZADD`, `ZINCRBY`, `ZRANK` | O(log N) | nothing, really |
| `HGETALL`, `SMEMBERS`, `LRANGE 0 -1`, `ZRANGE 0 -1` | O(N) | big collections |
| `KEYS *`, `FLUSHALL` | O(all keys) | any production server |
| `DEL` of a big key | O(N) | freeing millions of elements (chapter 17) |

The fix is almost never a bigger server. It is asking for less at a time: `ZRANGE report:2025 0 99` for the top
100, `HSCAN` / `SSCAN` / `ZSCAN` to walk a big collection in pieces, or splitting one giant key into many smaller
ones (one per day, one per customer).

**Check yourself:** which is slower on a set of a million members, `SISMEMBER` or `SMEMBERS`? (`SMEMBERS`: it
returns all million; `SISMEMBER` checks one.)
:::

:::step{type=example title="Worked example: what INFO commandstats says"}
Redis keeps statistics per command: how many times each ran, and how long it took **inside the server**. Here, 200
`GET`s and two `ZRANGE`s on the report key (one for everything, one for the top ten) ran, and then:

```bash run
redis-cli INFO commandstats | grep -E "cmdstat_(get|zrange):"
```

```text
cmdstat_get:calls=200,usec=190,usec_per_call=0.95,rejected_calls=0,failed_calls=0
cmdstat_zrange:calls=2,usec=3409,usec_per_call=1704.50,rejected_calls=0,failed_calls=0
```

Read each line:

1. `calls=200`: `GET` ran 200 times.
2. `usec=190`: in total, Redis spent 190 **microseconds** on them.
3. `usec_per_call=0.95`: under one microsecond per `GET`. That is pure server time; everything else your app
   waited for was the network.
4. For `ZRANGE`: 2 calls, 3,409 microseconds, **1,704.5 per call** on average. The full read of 100,000 members
   took almost all of that; the top-ten read was nearly free.

So a single `ZRANGE` of the whole report cost Redis as much time as about **1,800 `GET`s**. During those
milliseconds, nobody else was served. `CONFIG RESETSTAT` sets these counters back to zero, so you can measure a
quiet period and a busy one separately.
:::

:::step{type=predict title="Guess first"}
:::question
`INFO commandstats` shows `cmdstat_get: ... usec_per_call=0.95`, but your app measures 0.6 ms for every `GET`. Where
do the other 599 microseconds go?
:::
- [ ] Redis is lying about its own time
- [x] The round trip: the network between the app and Redis, and the client library
- [ ] Other commands that ran at the same time
:::explain
`usec_per_call` is only the server's own work. A big gap between it and what the app sees points at the network or
the app, which is exactly the kind of answer that stops people from buying a bigger Redis server for nothing.
:::
:::

:::step{type=try title="Read the slow log"}
The **slow log** is a list Redis keeps of every command that took longer than a threshold, with its key, its
arguments and its duration. Last night's report jobs ran some heavy commands, and the slow log caught them before
someone switched it off. It still holds what it caught:

```bash run
redis-cli SLOWLOG GET
```

Here is what it showed in this lab (your ids, times and addresses will differ):

```text
1) 1) (integer) 36
   2) (integer) 1795356130
   3) (integer) 1338
   4) 1) "LRANGE"
      2) "report:pages"
      3) "0"
      4) "-1"
   5) "10.77.3.4:33476"
   6) ""
2) 1) (integer) 35
   2) (integer) 1795356130
   3) (integer) 2301
   4) 1) "SMEMBERS"
      2) "report:visitors"
   5) "10.77.3.4:33462"
   6) ""
3) 1) (integer) 34
   2) (integer) 1795356130
   3) (integer) 3527
   4) 1) "ZRANGE"
      2) "report:2025"
      3) "0"
      4) "-1"
      5) "WITHSCORES"
   5) "10.77.3.4:33450"
   6) ""
```

Each entry has six parts:

1. a unique **id**, counting up;
2. **when** it ran, in seconds since 1970;
3. how long it took, in **microseconds**: the number you care about most;
4. the **command and its arguments**: the key is right there;
5. the **client's address**, so you can find which app sent it;
6. the client's **name**, if the app set one (`CLIENT SETNAME`), here empty.

Careful: the list is **newest first**, not slowest first. The top entry is the most recent, not necessarily the
worst. Compare the durations.

:::diagram{name="slow-command"}
One big command has Redis to itself; every quick command behind it waits, and the slow log remembers.
:::
:::

:::step{type=task task=slow_key_found title="Your turn: find the slowest command"}
Using `SLOWLOG GET`, find the entry with the **longest duration** (the third field).

Store what you found in two keys:

- `answer:slow_key`: the key that command worked on;
- `answer:slow_command`: the command's name, for example `GET`.

Press **Check**. If it says your key is in the slow log but not the slowest, compare the durations once more:
newest is not slowest.
:::

:::step{type=concept title="Keep the slow log on"}
Why was the slow log switched off? Someone thought it costs performance. It costs almost nothing: Redis only adds
an entry when a command is **already** slow, and keeps a fixed number of them in memory. Two settings control it:

```text
> CONFIG GET slowlog*
1) "slowlog-log-slower-than"
2) "-1"
3) "slowlog-max-len"
4) "128"
```

- `slowlog-log-slower-than` is the threshold, in **microseconds**. Any command slower than this is logged. The
  default is 10000 (10 ms). A **negative** number switches logging off, which is what happened here. `0` logs
  **every** command, which floods the log and hides the slow ones.
- `slowlog-max-len` is how many entries to keep. The default, 128, is small: one bad minute with many slow
  commands pushes out the evidence before anyone looks. Production teams keep 1,000 or more.

You change them while Redis runs with `CONFIG SET`, for example `CONFIG SET slowlog-max-len 1000`. (This lab's
changes live until Redis restarts; on a real server you would also put them in `redis.conf`, or run `CONFIG
REWRITE`, so they survive restarts.)

Two more commands complete the toolkit: `SLOWLOG LEN` counts the entries, and `SLOWLOG RESET` empties the log, for
example after you have dealt with an incident and want a clean start.
:::

:::step{type=task task=slowlog_config title="Your turn: switch the slow log back on"}
Turn the slow log back on, the way a production team would:

1. Log every command slower than **10 ms** (careful with the unit).
2. Keep at least the last **1000** entries.

Check both with `CONFIG GET slowlog*`, then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`slowlog-log-slower-than` is set to `10000`. Which command gets logged?
:::
- [ ] One that took 10,000 nanoseconds
- [ ] One that took 5 ms
- [x] One that took 12 ms
:::explain
The threshold is in microseconds: 10,000 µs is 10 ms. Only commands slower than that are logged, so 12 ms is in
and 5 ms is not.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A dashboard calls `HGETALL stats:all` every second, on a hash that has grown to 500,000 fields. What is the best fix?
:::
- [ ] Buy a server with a faster CPU
- [x] Ask for less: read only the fields the dashboard needs (`HMGET`), or split the hash into smaller ones
- [ ] Run it inside a Lua script
:::explain
`HGETALL` is O(N), so its cost grows with the hash. A faster CPU buys a little; reading 10 fields instead of
500,000 buys a factor of 50,000. A script would still be one long command, freezing everyone just the same.
:::
:::

:::step{type=deep-dive title="Go deeper: the latency monitor, and measuring from the outside"}
**The latency monitor.** Besides the slow log, Redis can record **latency events**: moments when something inside
it (a slow command, a fork for a snapshot, an expiry cycle) took longer than a threshold. Turn it on with
`CONFIG SET latency-monitor-threshold 100` (milliseconds), then `LATENCY LATEST` lists recent spikes, and
`LATENCY DOCTOR` writes a plain-English report with advice.

**Latency over time.** `redis-cli --latency-history -i 15` prints one latency summary every 15 seconds, so you can
watch it change during a deploy or a traffic peak. `redis-cli --intrinsic-latency 30`, run on the Redis machine
itself, measures how much the machine (not Redis) delays programs, which reveals noisy neighbours on shared cloud
servers.

**Measure from the app, too.** The slow log sees server time only. Client libraries and metrics systems measure
what your app really waits for, per command, as p50, p95 and p99. A spike there with nothing in the slow log means
the network, the app, or too many round trips.

**Big keys and hot keys.** `redis-cli --bigkeys` scans the database (with `SCAN`, safely) and reports the biggest
key of each type; `--memkeys` reports the keys using the most memory, and `--hotkeys` the most used ones (it needs
an LFU eviction policy, chapter 14). One giant key or one key used by everyone is behind many production
incidents.

**Threads.** Since Redis 6, `io-threads` lets extra threads read and write network data, which helps a busy
server with many connections. Commands still run one at a time on the main thread, so a slow command still
blocks everyone.
:::

:::step{type=recap}
You can now:

- tell latency, throughput and slow commands apart, and server time from round trips;
- show with `redis-benchmark` how clients, pipelines and value sizes change throughput;
- explain O(1) and O(N), and read `INFO commandstats` to see what each command costs inside Redis;
- read the slow log correctly (newest first, durations in microseconds), and configure it for production.

Next, chapter 14: what happens when Redis runs out of memory, live.

:::photo{src="/lesson-images/redis/redis-13-notes.webp" alt="Handwritten notes about measuring redis: latency, throughput, slow commands; pipelines: 10x the throughput; O(1) fast, O(N) careful; SLOWLOG GET: newest first; threshold in microseconds" ai="true"}
One page of notes for this chapter.
:::
:::
