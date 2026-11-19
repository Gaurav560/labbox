:::step{type=story title="Lunch rush at Tapri Counter"}
:::character{name="Meera" role="CTO, Tapri Counter"}
Forty outlets, six hundred orders a minute at lunch, and checkout has started to crawl.
Customers are walking out with their coffee unpaid. The database is the only thing that
changed since yesterday. Can you find out why?
:::

:::mission
Make the checkout lookup fast again, on the real database, before the lunch rush.
:::
:::

:::step{type=concept title="How Postgres finds rows"}
Postgres has two main ways to find the rows you ask for.

A **sequential scan** reads every row in the table and keeps the ones that match.
Fine for a hundred rows. Painful for a million.

An **index** is a sorted lookup structure on one or more columns, like the index at the
back of a book. With it, Postgres jumps straight to the matching rows.

:::tip
`EXPLAIN ANALYZE` runs a query and shows the plan Postgres actually used, with timings.
:::
:::

:::step{type=predict title="Guess first"}
:::question
The `orders` table has a million rows and **no index** on `customer_id`.
What does Postgres do for `WHERE customer_id = 4242`?
:::
- [ ] Jumps straight to customer 4242's rows
- [x] Reads every row and keeps the matching ones
- [ ] Uses the primary key index on `id`
:::explain
Without an index on `customer_id`, the only option is a sequential scan over all
million rows. The primary key index helps only when you filter by `id`.
:::
:::

:::step{type=try title="Look at the plan"}
Your terminal is already connected to the database. Run the checkout query and time it:

```bash run
psql -c "EXPLAIN ANALYZE $(cat checkout.sql)"
```

Look for `Seq Scan on orders` and the `Execution Time` at the bottom.
:::

:::step{type=incident task=add_index minutes=15 title="Pager: checkout p95 is 9 seconds"}
**Tapri Counter on-call.** Checkout p95 latency 9.4 s across all outlets.
Lunch rush starts in 15 minutes.

Make the customer lookup in `checkout.sql` use an index and run in **under 5 ms**.
Your fix must live in the database, so it survives a restart. Do not delete orders:
the shop needs its history.
:::

:::step{type=deep-dive title="Index for the whole query"}
The checkout query also sorts by `created_at`. An index on `(customer_id, created_at DESC)`
gives Postgres the rows already in the right order, so it can stop after 20 rows
without sorting anything. Compare the plans of both versions with `EXPLAIN ANALYZE`.

:::warning
Every index makes inserts a little slower and takes disk space. Add the ones your
queries need, not one per column.
:::
:::

:::step{type=recap}
- A slow endpoint usually hides a slow query: start with `EXPLAIN ANALYZE`.
- A sequential scan reads every row; an index jumps straight to the right ones.
- Index the columns you filter (and sort) by, and nothing more.
:::
