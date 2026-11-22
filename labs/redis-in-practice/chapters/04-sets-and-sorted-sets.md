:::step{type=story title="Who, and how many"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Marketing has two questions every morning. Who visited us yesterday, counting each person once?
And which items sell best, right now, not last month? Postgres can answer both, slowly, with a
query that scans every order. Redis can keep the answers ready all day.
:::

:::mission
Count unique visitors with a set, find customers two outlets share, and keep a live best-seller board.
:::
:::

:::step{type=concept title="Sets: each member once"}
A **set** holds unique strings, with no order. Adding a member that is already there does nothing,
which makes "count each person once" free:

```text
> SADD visitors:today asha ravi asha
(integer) 2                 asha was only added once
> SCARD visitors:today
(integer) 2
> SISMEMBER visitors:today ravi
(integer) 1
```

Sets can also be combined: `SINTER` (in both), `SUNION` (in either) and `SDIFF` (in the first but
not the second). Each has a `...STORE` version that saves the result under a new key.
:::

:::step{type=example title="Worked example: who tasted the new blend"}
A tasting event: count each person once, however many cups they try.

```text
> SADD tasted:blend asha ravi
(integer) 2
> SADD tasted:blend ravi
(integer) 0
> SCARD tasted:blend
(integer) 2
> SISMEMBER tasted:blend meera
(integer) 0
```

1. Two new members: `SADD` answers `2`.
2. Ravi comes back for a second cup: he is already in the set, so `SADD` answers `0` and nothing changes.
3. `SCARD` counts the members: still `2`.
4. `SISMEMBER` asks about one person: Meera has not tasted it yet.
:::

:::step{type=predict title="Guess first"}
:::question
`SADD tags coffee juice coffee coffee` on an empty key. What does `SCARD tags` return?
:::
- [ ] 4
- [x] 2
- [ ] 1
:::explain
A set keeps each member once, so the three `coffee` become one: `coffee` and `juice`, 2 members.
`SADD` itself returns how many members were new, which is also 2.
:::
:::

:::step{type=task task=unique_visitors title="Count each visitor once"}
This morning's visits at the Andheri outlet, in order: `asha`, `ravi`, `asha`, `meera`, `ravi`.
Record them in the set `visitors:today`, so it holds each visitor once.
:::

:::step{type=task task=common_customers title="Customers of both outlets"}
The sets `customers:andheri` and `customers:bandra` hold this month's customers of each outlet.
Marketing wants to thank the people who visit **both**. Save exactly those customers in a new set,
`customers:both`, with one command.
:::

:::step{type=concept title="Sorted sets: a leaderboard that sorts itself"}
A **sorted set** is a set where every member has a **score**, and Redis keeps the members ordered by
it at all times:

```text
> ZADD sales:today 120 "filter coffee" 80 "vada pav"
> ZINCRBY sales:today 5 "vada pav"
"85"
> ZREVRANGE sales:today 0 2 WITHSCORES      the top 3, highest first
```

Adding, updating a score and reading the top N all stay fast even with millions of members, which
is why sorted sets power leaderboards, "trending now" lists and priority queues.

:::trace{title="votes for today's snack"}
| command | highest first | note |
|---|---|---|
| ZADD votes 12 poha 10 samosa | poha 12, samosa 10 | Each member has a score; Redis keeps them in order. |
| ZINCRBY votes 5 samosa | samosa 15, poha 12 | Five more votes: samosa moves to the top by itself. |
| ZADD votes 7 dosa | samosa 15, poha 12, dosa 7 | A new member slots into its place. |
| ZREVRANGE votes 0 0 | samosa | The top one, read without sorting anything. |
:::
:::

:::step{type=task task=top_sellers title="Today's best sellers"}
Keep today's sales in a **sorted set** called `sales:today`: filter coffee sold `120`, vada pav `80`,
cold coffee `45`.

Then the evening rush sells **5 more** cold coffees. Add them to its score without retyping the others.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which command answers "customers of Andheri who never visit Bandra"?
:::
- [ ] `SINTER customers:andheri customers:bandra`
- [ ] `SUNION customers:andheri customers:bandra`
- [x] `SDIFF customers:andheri customers:bandra`
:::explain
`SDIFF` keeps what is in the first set but not in the second. `SINTER` is "in both", `SUNION` is
"in either".
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You need the top 10 players out of a million, many times a second. Which type fits?
:::
- [ ] A list, sorted by the app each time
- [x] A sorted set
- [ ] A set
:::explain
A sorted set keeps members ordered by score at all times, so the top 10 is a quick read, even with
millions of members. Sorting a big list on every request would be far too slow.
:::
:::

:::step{type=deep-dive title="Counting a billion visitors in 12 KB"}
A set that remembers every visitor grows with every visitor: a hundred million IDs cost gigabytes.
Often you only need **how many**, not **who**.

A **HyperLogLog** answers "how many distinct?" in about **12 KB, whatever the count**, within about
0.8% of the truth:

```text
PFADD uniques:today asha ravi asha
PFCOUNT uniques:today
```

Seniors pick structures by the question asked: a set when you need the members, a HyperLogLog when
an estimate of the count is enough, and a sorted set when order matters.
:::

:::step{type=recap}
- A set keeps unique members: `SADD`, `SCARD`, `SISMEMBER`, and `SINTER`, `SUNION`, `SDIFF` to combine.
- `SINTERSTORE dest a b` saves an intersection under a new key.
- A sorted set keeps members ordered by score: `ZADD`, `ZINCRBY`, `ZREVRANGE ... WITHSCORES`.
- For "how many distinct" at huge scale, a HyperLogLog trades exactness for a fixed 12 KB.
:::
