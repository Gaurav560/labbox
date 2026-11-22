:::step{type=story title="How many people visited today?"}
Basket's dashboard wants a simple number: how many **different** people opened the app today. Not how many visits:
Asha opening the app five times is still one person.

With a counter from chapter 2 you would count visits, not people. With a list you would store Asha five times,
and then have to remove the repeats yourself. What you want is a collection that **refuses duplicates** on its own.

And the dashboard has a second wish: today's best-selling items, always in order, updated with every sale. Sorting
thousands of items again for every page view would be slow. What you want is a collection that **stays sorted**
by itself.

Redis has both, and they are this chapter.

:::mission
Count each visitor once, find the customers who order from both stores, and keep a best-seller list that sorts
itself.
:::
:::

:::step{type=concept title="Sets: each member once"}
A **set** is an unordered collection of unique strings, called **members**, like a Python `set`. Add the same
member twice and it is still there once. Set commands start with **S**.

```text
> SADD tasted:mangoes asha ravi
(integer) 2
> SADD tasted:mangoes ravi meera
(integer) 1
```

The second `SADD` sent two members but answered `1`: Ravi was already in the set, so only Meera was new. `SADD`
always tells you how many members it actually added.

```text
> SMEMBERS tasted:mangoes
1) "asha"
2) "ravi"
3) "meera"
> SCARD tasted:mangoes
(integer) 3
> SISMEMBER tasted:mangoes ravi
(integer) 1
```

- `SMEMBERS` lists every member. The order is not meaningful: a set has no order, and you should never rely on
  the one you see.
- `SCARD` counts them (the name comes from "cardinality", a mathematician's word for "how many").
- `SISMEMBER` asks "is this one in?" and answers `1` or `0`, instantly, however big the set is.
- `SREM` removes a member.

**Check yourself:** what does `SADD tasted:mangoes asha` answer now? (`0`: Asha is already a member.)
:::

:::step{type=example title="Worked example: comparing two stores"}
The real power of sets is comparing them. The lab already holds this month's customers of each store. Kothrud:

```text
> SMEMBERS customers:kothrud
1) "asha"
2) "ravi"
3) "meera"
4) "kabir"
5) "priya"
6) "dev"
```

Baner holds ravi, sana, priya, arjun, dev and zoya. Three questions, three commands:

**Who orders from both stores?** The **intersection**:

```text
> SINTER customers:kothrud customers:baner
1) "ravi"
2) "priya"
3) "dev"
```

**Who orders from either store?** The **union**, everyone once:

```text
> SUNION customers:kothrud customers:baner
```

It answered nine names: asha, ravi, meera, kabir, priya, dev, sana, arjun, zoya. Ravi, Priya and Dev are in both
sets but appear once.

**Who orders only from Kothrud?** The **difference**, Kothrud's members that are not in Baner:

```text
> SDIFF customers:kothrud customers:baner
1) "asha"
2) "meera"
3) "kabir"
```

Each of these has a twin with **STORE** on the end (`SINTERSTORE`, `SUNIONSTORE`, `SDIFFSTORE`) that writes the
result into a new key instead of printing it. Its first argument is the destination key, then the sets to
compare. Doing this inside Redis means the member lists never travel to your app at all.
:::

:::step{type=predict title="Guess first"}
:::question
Five visits arrive this morning: asha, ravi, asha, meera, ravi. You add all five to the set `visitors:today` in
one `SADD`. What does `SCARD visitors:today` answer?
:::
- [ ] 5
- [x] 3
- [ ] 2
:::explain
A set keeps each member once: asha, ravi and meera. The repeats are simply ignored, which is exactly what
"unique visitors" means.
:::
:::

:::step{type=task task=unique_visitors title="Your turn: count each visitor once"}
This morning's app opens, in order, were: **asha, ravi, asha, meera, ravi**.

Add all five to a set called `visitors:today`, in **one** `SADD`. Then ask `SCARD visitors:today`: it should say
3. Press **Check**.
:::

:::step{type=task task=common_customers title="Your turn: customers of both stores"}
Basket wants to thank the customers who order from **both** stores, Kothrud and Baner, with a small gift.

Store exactly those customers in a new set called `customers:both`, with one command. Do not change
`customers:kothrud` or `customers:baner`. Check with `SMEMBERS customers:both`, then press **Check**.
:::

:::step{type=concept title="Sorted sets: a leaderboard that sorts itself"}
A **sorted set** is a set where every member also has a **score**, a number, and Redis keeps the members sorted
by score at all times. Sorted set commands start with **Z** (a "Z-set", because S was taken).

Golf tournaments have kept leaderboards like this one at Augusta National for decades: after every hole the scores change, and the order on the board must be right again at once. A sorted set is that board, kept in order by Redis itself.

:::photo{src="/lesson-images/redis/augusta-leaderboard.webp" alt="A large white golf leaderboard on a green stand under a blue sky, with the word LEADERS at the top and rows of names and scores" credit="Ryan Schreiber" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:Augusta_National_Leaderboard_(17071936729).jpg"}
The leaderboard at Augusta National Golf Club.
:::

Here are three customers and their loyalty points this month:

```text
> ZADD points 50 asha 80 ravi 65 meera
(integer) 3
> ZRANGE points 0 -1 WITHSCORES
1) "asha"
2) "50"
3) "meera"
4) "65"
5) "ravi"
6) "80"
```

`ZADD` takes **score member** pairs (score first). `ZRANGE` lists them from the lowest score up, and `WITHSCORES`
shows each score after its member. For a leaderboard you want the top first, so reverse it:

```text
> ZREVRANGE points 0 1 WITHSCORES
1) "ravi"
2) "80"
3) "meera"
4) "65"
```

`0 1` means positions 0 to 1: the top two. Now Asha earns 20 more points:

```text
> ZINCRBY points 20 asha
"70"
> ZREVRANGE points 0 -1 WITHSCORES
1) "ravi"
2) "80"
3) "asha"
4) "70"
5) "meera"
6) "65"
```

Asha moved up past Meera, and nobody sorted anything. Redis placed her when the score changed, and it does that
in a time that grows only very slowly with the size of the set (O(log N)), so a leaderboard of ten million
players is as easy as one of ten.

A few more questions a sorted set answers in one command:

| Question | Command | Answer here |
|---|---|---|
| What is Meera's score? | `ZSCORE points meera` | `"65"` |
| What place is Asha in, from the top? | `ZREVRANK points asha` | `(integer) 1` (counting from 0, so second) |
| Who has between 60 and 100 points? | `ZRANGEBYSCORE points 60 100 WITHSCORES` | meera 65, asha 70, ravi 80 |
| How many members? | `ZCARD points` | `(integer) 3` |

Careful: `ZADD` on an existing member **replaces** its score. `ZADD points 10 asha` answers `0` (no new member)
and Asha's score is now 10, not 80. To add to a score, use `ZINCRBY`.
:::

:::step{type=task task=top_sellers title="Your turn: today's best sellers"}
Keep today's sales, in units, in a sorted set called `sales:today`:

1. So far today: **mangoes 120**, **rice 80**, **dal 45**. Add all three with one `ZADD`.
2. Five more packets of dal were just sold. Add 5 to dal's score, without typing its new total.

`ZREVRANGE sales:today 0 -1 WITHSCORES` should show mangoes 120, rice 80, dal 50. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You want to know whether customer `zoya` is in `customers:kothrud`, which has a million members. What is the
right command?
:::
- [ ] `SMEMBERS customers:kothrud`, then search the answer in your app
- [x] `SISMEMBER customers:kothrud zoya`
- [ ] `SCARD customers:kothrud`
:::explain
`SISMEMBER` answers in constant time, however big the set. `SMEMBERS` would send a million names across the
network to find one, and freeze Redis while it builds that answer.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Meera has 65 points. You run `ZADD points 10 meera`. What is her score now?
:::
- [ ] 75
- [x] 10
- [ ] 65, because ZADD never changes an existing member
:::explain
`ZADD` sets the score, replacing the old one. `ZINCRBY points 10 meera` would have added 10, giving 75.
:::
:::

:::step{type=deep-dive title="Go deeper: counting a billion visitors in 12 KB"}
A set of unique visitors stores every member. For a big site that is millions of IDs, and many megabytes, just to
answer "how many?".

Redis has a structure made for exactly that question, the **HyperLogLog**. It never stores the members, only a
clever summary of them, and it estimates how many different ones it has seen with an error of about 0.81%,
using at most **12 KB**, whether it saw a hundred visitors or a billion:

```text
> PFADD hll:today asha ravi asha meera
(integer) 1
> PFCOUNT hll:today
(integer) 3
```

(PF honours Philippe Flajolet, the computer scientist who invented the algorithm.) You cannot ask a HyperLogLog
**who** visited, only **how many**, so use a set when you need the names and a HyperLogLog when you only need the
count of something huge.

**How sorted sets work inside.** A big sorted set is two structures at once: a hash table (member to score, for
`ZSCORE` in one step) and a **skip list**, a sorted linked list with "express lanes" that let Redis jump ahead,
so finding a position takes about log N steps. Small sorted sets use the compact listpack encoding instead.

**Leaderboards in the real world.** Game studios use sorted sets for leaderboards with millions of players, and
many apps use them for "trending" lists, with a score that combines likes and time. A sorted set with timestamps
as scores is also a neat way to find "everything in the last hour" with `ZRANGEBYSCORE`.
:::

:::step{type=recap}
You can now:

- keep unique members in a set with `SADD`, and count or test them with `SCARD` and `SISMEMBER`;
- compare sets inside Redis with `SINTER`, `SUNION` and `SDIFF`, and store the result with the STORE versions;
- build a leaderboard that sorts itself with `ZADD`, `ZINCRBY` and `ZREVRANGE ... WITHSCORES`;
- choose a HyperLogLog when you only need to count something enormous.

That completes Part 1. Next, chapter 6: Redis from a real Python app, and why round trips matter.

:::photo{src="/lesson-images/redis/redis-05-notes.webp" alt="Handwritten notes about sets and sorted sets: SADD: each member once; SINTER = in both; ZADD score member; ZINCRBY adds to a score; ZREVRANGE 0 9 = the top 10" ai="true"}
One page of notes for this chapter.
:::
:::
