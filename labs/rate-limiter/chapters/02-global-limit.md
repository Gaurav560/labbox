:::step{type=story title="Ten polite partners"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Good news: every partner now stays under 10 a second. Bad news: we have ten partners, and our quotes
database falls over above 50 requests a second in total. Each partner is polite; together they are not.
:::

:::mission
Add a global limit of 50 requests a second for all partners together, then explain your design.
:::
:::

:::step{type=concept title="Layers of limits"}
Real APIs stack limits: **per key** (fairness between clients) and **global** (protecting what
sits behind, like a database). A request goes through only if **every** layer allows it.

Each layer is another counter. To keep it fast, send all the Redis commands in **one round trip**
with a **pipeline**: the app waits for Redis once, not four times.
:::

:::step{type=predict title="Guess first"}
:::question
Ten keys each send 8 requests a second. The per-key limit is 10 and the global limit is 50. About how
many requests a second get through?
:::
- [ ] 80
- [x] 50
- [ ] 10
:::explain
No key goes over its own limit of 10, so per-key allows all 80. The global counter stops everything
above 50 a second.
:::
:::

:::step{type=task task=global_limit title="Protect the database"}
Make `allow()` also enforce `GLOBAL_LIMIT`: at most 50 requests a second for all keys together, still
across both copies of the app. Keep the per-key limit working. Run `bash run.sh` again, then Check.
:::

:::step{type=design title="Design review"}
Senior engineers explain their choices. Answer each in a few sentences, in your own words.

:::ask{id=redis_down}
Redis goes down for a minute. What does your limiter do now, and what should it do? Think about users and about the database.
:::

:::ask{id=two_servers}
Why did the first limiter, with a dict in the app, let a client through at twice its limit?
:::

:::ask{id=burst}
With a one-second window, can a client ever send more than 10 requests within one second? How would you prevent it?
:::
:::

:::step{type=deep-dive title="Token buckets"}
A **token bucket** gives each client a bucket that refills at a steady rate (10 tokens a second, up
to a maximum). Each request takes a token; an empty bucket means 429. It allows short bursts but
keeps the average, and it has no edge between windows. In Redis it is a few lines of **Lua**, run
with `EVAL`, so reading and updating the bucket happen as one atomic step on every server.
:::

:::step{type=recap}
- Stack limits: per key for fairness, global to protect what is behind.
- Pipelines send several Redis commands in one round trip.
- Fixed windows are simple but allow bursts at the edges; sliding windows and token buckets do not.
:::
