:::step{type=story title="Why does a page take two seconds?"}
Open almost any shopping app and count. Before the first screen appears, the app has asked its servers dozens of
questions: what is in stock, what does it cost, who is this customer, what is in their cart, which offers apply.
Every question is a little wait. Add the waits up, and that is how long the screen stays blank.

In this course you will build the backend of **Basket**, a 10-minute grocery delivery app in Pune with two dark
stores (small warehouses that only pack orders), one in Kothrud and one in Baner. Basket has a problem you can
measure today: every price comes from a **catalogue service** that is always right but takes 1.5 seconds to
answer, and the partner who runs it bills Basket Rs 0.10 for every question.

A home page that shows ten prices waits fifteen seconds. Nobody waits fifteen seconds for groceries.

This chapter is about **why** a tool called **Redis** exists at all: where the time goes inside a computer, what
people did before Redis, and what a millisecond is worth in money. By the end you will have measured your own
Redis server with the same tools the people who run Redis at big companies use.

:::mission
Measure one round trip to Redis, and how many requests a second it can serve.
:::
:::

:::step{type=try title="Ask the same question two ways" file="01-why-redis/compare.py" line="12-23"}
Let's start with something you can see. Look at `compare.py`, on the right. It asks for the price of rice in two
ways:

1. Three times from the slow catalogue service (lines 12 to 15), timing each answer.
2. A thousand times from **Redis** (lines 18 to 21), after storing the price there once.

You do not need to read every line yet. Open a terminal, go into the chapter's folder, and run it:

```bash run
cd 01-why-redis && python3 compare.py
```

It takes about five seconds, almost all of it spent waiting for the catalogue. Here is what it printed in this lab
when we ran it:

```text
catalogue service:   1506.3 ms per answer
redis:                0.017 ms per answer
Redis answered about 89,156 times faster.
```

Your numbers will be a little different, and that is fine. The shape is the point: one way takes a second and a
half; the other takes **seventeen millionths of a second**. Same question, same answer, a difference of about a
hundred thousand times.

How can two answers to the same question be so far apart? The catalogue in this lab is slow on purpose, a
stand-in for a real slow system. But real systems are slow for real reasons, and the next step shows where the
time goes.
:::

:::step{type=concept title="Where the time goes: the latency ladder"}
**Latency** is the time between asking and getting an answer. A computer can fetch data from many places, and
each place is much slower than the one before it, like rungs on a ladder.

Here are the classic numbers, from a list Google engineer **Jeff Dean** shared in 2009 and programmers have
passed around ever since (rounded; today's hardware is a little faster, but the gaps between the rungs are what
matter). The last column makes them human: pretend that reading memory took one second, and scale everything
else by the same amount.

| Where the data is | Real time | If a memory read took 1 second |
|---|---|---|
| The CPU's own cache | 0.5 ns | a blink: 5 milliseconds |
| Main memory (RAM) | 100 ns | 1 second |
| A random read from an SSD | 150 µs | 25 minutes |
| A round trip to another server in the same data centre | 500 µs | 1 hour and 23 minutes |
| A seek on a spinning hard disk | 10 ms | 28 hours |
| A packet from California to the Netherlands and back | 150 ms | 17 days |

(1 ms, a millisecond, is a thousandth of a second. 1 µs, a microsecond, is a millionth. 1 ns, a nanosecond, is a
billionth.)

How long is a nanosecond? Grace Hopper, one of the pioneers of programming, used to hand out pieces of wire about 30 cm long: the distance light travels in one nanosecond, so people could hold one in their hands. These two wires were hers.

:::photo{src="/lesson-images/redis/hopper-nanoseconds.webp" alt="Two thin wires lying on a white cloth, one with a small label, used by Grace Hopper to show the length of a nanosecond" credit="Naval History and Heritage Command" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:90-115-AG,_AH,_Wire_Nanosecond_(15864510468).jpg"}
Grace Hopper's nanosecond wires, now in the US Navy's collection.
:::

Read the middle of the table again. Data in **memory** comes back in 1 "second". The same data on a **disk** takes
anything from 25 minutes to more than a day. That is why a database, which keeps its data safe on disk, can never
be as quick as something that keeps its data in memory.

:::diagram{name="latency-ladder"}
Each rung down the ladder is roughly a thousand times slower than the one above it.
:::

A real request also climbs this ladder more than once. Basket's home page asks a database, which reads from disk,
then asks the catalogue service, which asks its own database. The waits add up.

**Check yourself:** a program reads one value from RAM, and another reads it from an SSD. Roughly how many times
longer does the second one wait? (About 1,500 times: 100 ns against 150 µs.)
:::

:::step{type=history title="The story of Redis"}
Redis was built by one programmer to rescue his own slow website, and became the fast memory behind a large part
of the internet.

:::before{title="Before Redis"}
In the 2000s a web app kept almost everything in a **relational database** such as MySQL, on disk. Every page view
meant queries, and busy sites drowned their databases. The common fix was **memcached**, written by Brad
Fitzpatrick in 2003 for his website LiveJournal: a big shared dictionary in memory, placed in front of the
database. It was fast, but it stored only plain text values, forgot everything when it restarted, and could not
count, queue, rank or sort anything for you. Anything smarter meant another trip to the database.
:::

This is Brad Fitzpatrick, who wrote memcached for LiveJournal. It went on to run in front of the databases of Facebook, Wikipedia and many other big sites, and it is still widely used today.

:::photo{src="/lesson-images/redis/brad-fitzpatrick.webp" alt="Brad Fitzpatrick smiling, in a dark leather jacket, against a black background" credit="Anton Nosik" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Brad_Fitzpatrick_by_Anton_Nossik_cropped.jpg"}
Brad Fitzpatrick, the creator of memcached.
:::

In 2009 **Salvatore Sanfilippo**, an Italian programmer known online as **antirez**, was building **LLOOGG**, a
real-time web log analyser for his startup in Sicily. It had to record every page view of every website it
watched, and show the latest ones instantly. MySQL could not keep up with that many small writes. So he wrote his
own server that kept the data in memory, first as a small prototype in the Tcl language, then in C. He called it
**Redis**, short for **RE**mote **DI**ctionary **S**erver, and released it as open source on 26 February 2009.

:::photo{src="/lesson-images/redis/salvatore-sanfilippo.webp" alt="Salvatore Sanfilippo, with curly hair, glasses and a checked shirt, speaking on a stage" credit="dotconferences" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Salvatore_Sanfilippo.png"}
Salvatore Sanfilippo, known as antirez, the creator of Redis.
:::

:::solved
**A data structure server.** Redis keeps not just text but **lists, hashes, sets, sorted sets, counters and
streams** in memory, with commands that change them in a single step: add to a list, count up, rank by score.
It answers in well under a millisecond, and it can also save everything to disk. A counter, a queue, a
leaderboard or a login session became one command each, with no database trip at all.
:::

:::timeline
- **2009** Salvatore Sanfilippo releases Redis as open source. In 2010 VMware hires him to work on it full time.
- **2015** Redis 3.0 adds Redis Cluster: one dataset spread across many servers. Redis Labs (now Redis Ltd) becomes its sponsor.
- **2018** Redis 5 adds streams, the log-shaped type you will use in chapter 12.
- **2020** Sanfilippo steps down as maintainer. **2024**: a licence change, the Linux Foundation forks the last open version as **Valkey**, and in December Sanfilippo returns.
- **2025** Redis 8 adds an open-source licence option again (the AGPL).
:::

Today Redis is developed by **Redis Ltd** together with a large open-source community. Valkey, the Linux
Foundation's fork, speaks exactly the same commands, so everything in this course works on both.

:::usedby{title="Used for"}
- Caching
- Logins and sessions
- Rate limiting
- Leaderboards
- Queues and background jobs
- Real-time analytics
:::

:::usedby{title="Used at"}
- Twitter
- GitHub
- Stack Overflow
- Instagram
- Pinterest
- Craigslist
:::

:::funfact
The very first version of Redis was a few hundred lines of **Tcl**, a scripting language, written to prove the
idea before Sanfilippo rewrote it in C. Its single-threaded design, one command at a time, comes from those first
days and is still why Redis behaves so predictably. You will see exactly what that means in chapter 2.
:::
:::

:::step{type=concept title="What a millisecond is worth"}
Is it worth all this effort to save a second here and a millisecond there? The companies that measured it say
yes, loudly.

**Google, 2006.** Google tried showing 30 search results instead of 10. The bigger page took 0.9 seconds to build
instead of 0.4. In the group that saw it, searches dropped by **20%**. Marissa Mayer, then a Google vice president,
summed it up: half a second of delay caused a 20% drop. People did not decide to search less; they just did,
because waiting is unpleasant.

**Amazon.** Greg Linden, who built Amazon's early recommendation system, wrote that Amazon tested slowing pages
down in steps of 100 milliseconds and found that "even very small delays would result in substantial and costly
drops in revenue."

**Stack Overflow, 2016.** Stack Overflow publishes its architecture. On one day in February 2016 it reported:

| | How many that day | Total time spent |
|---|---|---|
| Redis hits | 5,831,683,114 | 2.8 hours |
| SQL database queries | 504,816,843 | 168 hours |

Read that slowly. Redis answered **eleven times more questions** than the database, in **sixty times less time**.
The whole site ran on **two** Redis servers (one main, one copy), and each used **under 2% of its CPU**. Every one
of those 5.8 billion answers was a question the database did not have to answer.

Now Basket. Suppose the app shows **a million prices a day**. Without Redis, every one is a catalogue call:
1.5 seconds of waiting and Rs 0.10 each. With Redis in front, only the **misses** (the first time a price is asked,
or after it expires) reach the catalogue. The share of reads that Redis answers is called the **hit rate**:

| Hit rate | Catalogue calls a day | Cost a day | Waiting a day |
|---|---|---|---|
| 0% (no cache) | 1,000,000 | Rs 100,000 | 417 hours |
| 90% | 100,000 | Rs 10,000 | 42 hours |
| 99% | 10,000 | Rs 1,000 | 4 hours |

Over a month, that is the difference between **Rs 30 lakh** (3 million) and **Rs 30,000**. Basket's catalogue
price is made up for this course, but the shape is real everywhere: a database or a paid API costs money for every
question, servers cost money for every extra question per second they must handle, and a cache turns most
questions into almost free ones. In chapter 8 your own app will count its hits and report what it saved.

:::diagram{name="hit-rate-savings"}
Every hit is a slow, paid call that never happens.
:::
:::

:::step{type=predict title="Guess first"}
:::question
Basket's cache answers 90% of price reads. A teammate tunes it until it answers 99%. How many catalogue calls
does that save, compared with before?
:::
- [ ] About 9% fewer: 99 is only 9 more than 90
- [x] About ten times fewer: misses drop from 10 in 100 to 1 in 100
- [ ] None: both are "almost all"
:::explain
What reaches the catalogue are the **misses**. At 90%, 10 reads in 100 miss; at 99%, only 1 does. The hit rate
moved by 9 points, but the load on the slow system fell by **ten times**. That is why teams fight for the last
few percent of hit rate.
:::
:::

:::step{type=try title="Measure one round trip yourself"}
Enough of other people's numbers. Let's measure yours.

`redis-cli` is the terminal program for talking to Redis; in this lab it is already pointed at the Redis server
next to you. With `--latency` it sends a tiny `PING` over and over, measures how long each answer takes, and
keeps a running summary:

```bash run
redis-cli --latency
```

The line updates as it counts. After a few seconds, press **Ctrl+C** to stop it. Here is the last line it showed
in this lab:

```text
min: 0, max: 1, avg: 0.08 (493 samples)
```

- **samples**: how many pings it sent, 493 here.
- **min** and **max**: the fastest and slowest answers, in **whole milliseconds** (so 0 means under one).
- **avg**: the average, in milliseconds with decimals: **0.08 ms**, eighty microseconds.

That avg is a full **round trip**: the question travels from your terminal to the Redis server over the lab's
network, Redis answers, and the answer travels back. Most of those 80 microseconds are the trip, not the work:
Redis spends only a microsecond or two on a `PING`.

Compare it with the catalogue's 1,506 ms. Your round trip to Redis is roughly **twenty thousand** times shorter.
:::

:::step{type=task task=measure_latency title="Your turn: record your round trip"}
Record your own measurement in Redis, so you can compare it later in the course:

1. Run `redis-cli --latency` for a few seconds and stop it with **Ctrl+C**.
2. Store the **avg** it printed under the key `bench:latency_ms`, as just the number:

```text
redis-cli SET bench:latency_ms 0.08
```

(Use your own number, not ours.) `SET` stores a value under a name; chapter 2 explains it properly. Press
**Check**.
:::

:::step{type=example title="Worked example: reading redis-benchmark"}
A round trip tells you how **quick** one answer is. The other big question is how **many** answers a second one
Redis can give. For that, Redis comes with a load generator called `redis-benchmark`. It opens 50 connections at
once and fires a flood of commands, then reports the rate.

Here is a run that sends 100,000 `SET` commands and 100,000 `GET` commands (`-t` picks the tests, `-n` the number
of requests, `-q` asks for one quiet line per test):

```bash run
redis-benchmark -t get,set -n 100000 -q
```

```text
SET: 195312.48 requests per second, p50=0.135 msec
GET: 203665.98 requests per second, p50=0.127 msec
```

Read it piece by piece:

1. **SET: 195312.48 requests per second**: about **195,000 writes a second**, from one Redis using one CPU core.
2. **GET: 203665.98**: about **204,000 reads a second**.
3. **p50=0.127 msec**: the **median** latency. Half of the requests were answered within 0.127 ms, half took
   longer. (p50 means "50th percentile". Teams also watch p99, the time that 99% of requests beat, because the
   slow few are what customers complain about.)

So one Redis served about 200,000 requests a second, each in about a tenth of a millisecond, on a single CPU
core. A database answering the same small lookups has far more work to do for each one: parse the SQL, plan the
query, take locks, and read pages that may be on disk. That is why it serves far fewer of them per core, and why
teams put Redis in front of it for the questions that are asked again and again.

One warning that every benchmark deserves: these numbers are for tiny values on a quiet lab machine. They show
what Redis **can** do, not what your app will see with big values, slow networks and busy neighbours. Measure
your own system before you promise anything.
:::

:::step{type=task task=measure_redis title="Your turn: measure your Redis"}
Run the benchmark yourself and keep the result:

1. Run `redis-benchmark -t get,set -n 100000 -q` (it takes a few seconds).
2. Store the two numbers it printed, as whole numbers, under `bench:get_per_sec` and `bench:set_per_sec`. For our
   run that would be `redis-cli SET bench:get_per_sec 203665`, then the same for SET.

Press **Check**. The check tells you how many requests a day your number adds up to.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A database keeps its data on disk; Redis keeps its data in memory. Using the latency ladder, why does that make
such a big difference?
:::
- [ ] Memory is cheaper than disk
- [x] Reading memory takes around 100 ns; a disk read takes from about 150 µs (SSD) to 10 ms (spinning disk)
- [ ] Disks can only be read by one program at a time
:::explain
Each rung of the ladder is roughly a thousand times slower than the one above. Data in memory skips the slow
rungs entirely. (Memory is actually **more** expensive than disk per gigabyte, which is why chapter 14 is about
fitting Redis into a memory budget.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`redis-cli --latency` shows `avg: 0.08`. What does that number measure?
:::
- [ ] How long Redis spends working on one command
- [x] One full round trip in milliseconds: the question there, the answer back, network included
- [ ] How many commands Redis runs per millisecond
:::explain
The average is for the whole trip. Redis itself needs only a microsecond or two for a `PING`; most of the 80
microseconds are the network. That is why chapter 6 is about sending many commands in **one** trip.
:::
:::

:::step{type=deep-dive title="Go deeper: why Redis is so fast, and when it is the wrong tool"}
Four design choices explain most of Redis's speed, and you will meet each of them again in this course.

**Memory, not disk.** Every read and write works on RAM. The disk is used only in the background, for saving
copies (chapter 15).

Inside a spinning hard disk, a head on an arm swings across the platters to find the data: that movement is where a seek's 10 milliseconds go. Memory has no moving parts at all.

:::photo{src="/lesson-images/redis/open-hard-drive.webp" alt="An opened hard disk drive showing the shiny round platter and the read and write arm resting over it" credit="Zzubnik" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Open_hard-drive.jpg"}
An open hard disk: the platter, and the arm that must move to every read.
:::

**One command at a time.** Redis runs commands on a single main thread, one after another. There are no locks to
take and no threads to coordinate, so each command is short and predictable. The flip side: one slow command
delays everyone behind it, which is the whole story of chapter 17.

**Efficient waiting.** One thread can serve thousands of connections because Redis asks the operating system
"which connections have something to read?" (`epoll` on Linux) instead of keeping a thread per client. Since
Redis 6, extra threads can help with reading and writing network data, while the commands still run one at a time.

**Simple data structures with known costs.** Most commands touch one key and take the same time however big the
database is (written O(1)). Small values are stored in compact encodings, so memory goes further.

**When Redis is the wrong tool.** Redis is not a replacement for your main database. Memory is expensive, so huge
datasets cost a lot to keep in Redis. It has no SQL, no joins and no ad-hoc queries over your data. And although it
can save to disk, its default settings can lose the last second or so of writes in a crash (chapter 15 shows the
trade-off). The usual design: the database is the **source of truth**, and Redis sits in front of it for
everything that must be fast, temporary or counted.
:::

:::step{type=recap}
You can now:

- explain the latency ladder, and why memory answers about a thousand times faster than an SSD;
- tell the story of Redis: memcached before it, antirez and LLOOGG, a data structure server;
- work out what a cache saves from its hit rate, in calls, time and money;
- measure a round trip with `redis-cli --latency`, and throughput with `redis-benchmark`.

Next, chapter 2: your first keys, and what "one command at a time" really means.

:::photo{src="/lesson-images/redis/redis-01-notes.webp" alt="Handwritten notes about why redis?: memory: 100 ns, disk seek: 10 ms; memcached (2003) came first; Redis = a data structure server; hit rate 90% to 99% = 10x less load; measure: --latency, redis-benchmark" ai="true"}
One page of notes for this chapter.
:::
:::
