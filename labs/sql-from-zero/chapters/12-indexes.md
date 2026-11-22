:::step{type=story title="Two million searches, and a slow app"}
Welcome to Part 4: fast and safe. Safar's app records every search people make, "Pune to Mumbai on 20 November",
to learn what people want. After a few months, the `searches` table holds **two million rows**. (Opening this
chapter just created it for you.)

Two screens read it all day. "My recent searches" shows one passenger's searches. The "how busy is this route"
badge counts searches for one route and one date. Both were instant when the table was small. Now each takes most of
a tenth of a second, the database's CPU is busy all the time, and the team is talking about a bigger, more
expensive server.

They do not need one. They need an **index**, and in this chapter you will measure, with the database's own
numbers, how a few megabytes turn a hundred-millisecond query into a sub-millisecond one.

:::mission
Make a passenger's searches fast, and make the app's trip search fast, each with the right index.
:::
:::

:::step{type=try title="How slow is it, exactly?"}
Never guess about speed; measure. In psql, `\timing on` makes every query report how long it took:

```text
safar=# \timing on
Timing is on.
safar=# SELECT COUNT(*) FROM searches WHERE passenger_id = 42;
 count
-------
  1000
(1 row)

Time: 46.242 ms
```

46 milliseconds to find 1,000 rows. To see **why**, put `EXPLAIN ANALYZE` in front of a query: Postgres runs it and
reports the plan it used, with real timings:

```text
safar=# EXPLAIN ANALYZE SELECT * FROM searches WHERE passenger_id = 42;
                                                        QUERY PLAN
---------------------------------------------------------------------------------------------------------------------------
 Gather  (cost=1000.00..30511.38 rows=995 width=32) (actual time=0.218..83.631 rows=1000 loops=1)
   Workers Planned: 1
   Workers Launched: 1
   ->  Parallel Seq Scan on searches  (cost=0.00..29411.88 rows=585 width=32) (actual time=0.169..80.163 rows=500 loops=2)
         Filter: (passenger_id = 42)
         Rows Removed by Filter: 999500
 Planning Time: 0.022 ms
 Execution Time: 83.671 ms
(8 rows)
```

Read it from the inside out:

1. **Seq Scan on searches**: a sequential scan, reading **every row** of the table. "Parallel" means two
   processes shared the work.
2. **Rows Removed by Filter: 999500**: each process read about a million rows and threw away all but 500.
3. **Execution Time: 83.671 ms**: the real time (fetching every column took longer than just counting).

To find 1,000 rows, Postgres read 2,000,000. That is the whole problem.
:::

:::step{type=concept title="What an index is"}
An **index** is a separate, sorted structure that points into the table, like the index at the back of a book:
instead of reading every page to find "passengers", you look it up in the index and go straight to pages 112 and
340.

Books have had indexes like this one, from a world atlas printed in 1655, for centuries: sorted words, each with the pages where it appears.

:::photo{src="/lesson-images/sql/atlas-index.webp" alt="A page of an old printed book titled INDEX, with columns of names in alphabetical order and page numbers" credit="Martino Martini (atlas), edited by Waldyrious" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Novus_Atlas_Sinensis_-_First_page_of_the_index.jpg"}
The index of the Novus Atlas Sinensis, 1655.
:::

Postgres's standard index is a **B-tree**: the values of a column, kept sorted in a shallow tree of pages, each
entry pointing at the rows that hold it. Finding a value means walking from the top of the tree to a leaf: three or
four page reads, whether the table has a thousand rows or a billion.

You create one with `CREATE INDEX`, naming the table and the column:

```sql
CREATE INDEX searches_passenger_idx ON searches (passenger_id);
```

Here is the same query after that index was built (building it took 0.86 seconds):

```text
safar=# EXPLAIN ANALYZE SELECT * FROM searches WHERE passenger_id = 42;
                                                             QUERY PLAN
-------------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on searches  (cost=12.14..3137.29 rows=995 width=32) (actual time=0.146..0.648 rows=1000 loops=1)
   Recheck Cond: (passenger_id = 42)
   Heap Blocks: exact=1000
   ->  Bitmap Index Scan on searches_passenger_idx  (cost=0.00..11.89 rows=995 width=0) (actual time=0.068..0.069 rows=1000 loops=1)
         Index Cond: (passenger_id = 42)
 Planning Time: 0.087 ms
 Execution Time: 0.676 ms
(7 rows)
```

**Bitmap Index Scan on searches_passenger_idx**: Postgres looked up passenger 42 in the index, found where the
1,000 rows live, and read only those. **0.676 ms instead of 83.671 ms: about 120 times faster.** The index takes 14 MB
of disk. Nothing in the query changed; Postgres's planner noticed the index and chose it by itself.

**Check yourself:** does a query need to mention the index by name to use it? (No: you only create it; the planner
decides when to use it.)
:::

:::step{type=example title="Worked example: what 120 times faster is worth"}
Speed is only half of it. Think about what the database's CPU spends.

A query that takes about 84 ms of work means one CPU core can serve about **12 of them a second** (1000 / 84). At
0.7 ms, the same core serves about **1,400 a second**. Suppose the "recent searches" screen is opened 300 times a
second at the evening peak:

| | Time per query | Queries per core per second | Cores busy at 300 a second |
|---|---|---|---|
| No index | 84 ms | about 12 | about **25** |
| With the index | 0.7 ms | about 1,400 | well under **1** |

(Rough arithmetic from this lab's measurements; a real server has caches and overheads. The shape is what
matters.)

Without the index, that one screen needs a large, expensive database server on its own. With it, the screen costs
almost nothing, for 14 MB of disk. This is why the first question about any slow database is "which index is
missing?", long before "which bigger server should we buy?".

There is a price on the other side, and you should know it: every index must be updated on every `INSERT`,
`UPDATE` and `DELETE` of the table, which makes writes a little slower, and it takes disk space. So you index the
columns your important queries **filter, join and sort on**, not every column.
:::

:::step{type=predict title="Guess first"}
:::question
After creating an index on `passenger_id`, you run `SELECT COUNT(*) FROM searches` (no `WHERE`). Is it faster?
:::
- [ ] Yes, about 120 times
- [x] No: it needs every row anyway, so the index does not help
- [ ] It fails, because the index does not cover COUNT
:::explain
An index helps you find **some** rows quickly. A question about all rows still reads them all. The planner knows
this and keeps the sequential scan.
:::
:::

:::step{type=task task=index_passenger title="Your turn: fast recent searches"}
Make "all searches of one passenger" fast. In `12-indexes/passenger_index.sql`, create an index on the `searches`
table that the query `SELECT * FROM searches WHERE passenger_id = 42` can use.

Run it with `psql -f passenger_index.sql`, then run the `EXPLAIN ANALYZE` above yourself and compare the
execution time with before. Press **Check**: it looks at the indexes and at the plan.
:::

:::step{type=concept title="One index, several columns"}
The "how busy is this route" badge asks a three-part question:

```sql
SELECT * FROM searches
WHERE from_city_id = 1 AND to_city_id = 2 AND travel_date = '2026-11-20';
```

Today it scans everything: `Execution Time: 42.223 ms`, with `Rows Removed by Filter: 999604` per worker.

An index can hold **several columns**, sorted by the first, then by the second within each first, and so on, like a
phone book sorted by surname, then by first name. An index on `(from_city_id, to_city_id, travel_date)` keeps all
searches from Pune together, within them all Pune to Mumbai together, and within those, each date together. One
lookup finds exactly the 793 rows the badge needs. With that index, this lab measured:

```text
 Bitmap Index Scan on searches_trip_idx  (cost=0.00..14.19 rows=781 width=0) (actual time=0.043..0.043 rows=793 loops=1)
       Index Cond: ((from_city_id = 1) AND (to_city_id = 2) AND (travel_date = '2026-11-20'::date))
 Execution Time: 2.362 ms
```

**2.4 ms instead of 42 ms.**

The order of columns matters, because of how the index is sorted. A multi-column index helps queries that use its
**first** column (and then the next ones, in order). A phone book cannot find "everyone called Asha" without a
surname. The same index, for a query that skips `from_city_id`:

```text
safar=# EXPLAIN ANALYZE SELECT * FROM searches WHERE to_city_id = 2 AND travel_date = '2026-11-20';
 ...
   ->  Parallel Seq Scan on searches  (cost=0.00..32353.06 rows=3558 width=32) (actual time=0.025..38.796 rows=2778 loops=2)
 ...
 Execution Time: 42.604 ms
```

Back to a full scan. And three separate indexes, one per column, are not the same as one index on all three: the
planner can combine them, but far less efficiently than one index built for the question.
:::

:::step{type=task task=index_trip_search title="Your turn: fast trip search"}
In `12-indexes/trip_search_index.sql`, create **one** index that makes the badge's query fast: searches
`WHERE from_city_id = ... AND to_city_id = ... AND travel_date = ...`.

Run it, then `EXPLAIN ANALYZE` the query above and find your index's name in the plan. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
An index exists on `(from_city_id, to_city_id, travel_date)`. Which query can use it best?
:::
- [x] `WHERE from_city_id = 1 AND to_city_id = 2`
- [ ] `WHERE travel_date = '2026-11-20'`
- [ ] `WHERE to_city_id = 2`
:::explain
A multi-column index serves queries that use its leading columns. The first query uses the first two; the others
skip the first column, like looking up a first name in a phone book sorted by surname.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why not simply create an index on every column of every table?
:::
- [ ] Postgres allows only one index per table
- [x] Every index slows down writes and takes disk space; only indexes that real queries use are worth it
- [ ] Indexes make reads slower
:::explain
Each `INSERT` and `UPDATE` must update every index on the table. Index what your important queries filter, join and
sort on, and check with `EXPLAIN` that they are used.
:::
:::

:::step{type=deep-dive title="Go deeper: reading plans, and indexes in production"}
**Index Scan, Bitmap Scan, Index Only Scan.** An Index Scan walks the index and fetches each row as it goes. A
Bitmap Scan first collects every matching location from the index, then reads the table pages in order, good for
hundreds or thousands of rows. An Index Only Scan answers from the index alone, without touching the table, when
the index holds every column the query needs (`INCLUDE (...)` can add columns for that).

**When the planner ignores your index.** If a query matches a large share of the table, reading it all is cheaper
than jumping around, so the planner keeps the sequential scan, correctly. It decides using statistics about each
column, which `ANALYZE` refreshes (Postgres also does it automatically, in the background).

**Building indexes on a live table.** A plain `CREATE INDEX` blocks writes to the table while it builds. On a busy
production table, teams use `CREATE INDEX CONCURRENTLY`, which takes longer but lets the app keep writing.

**Other kinds of index.** Besides B-trees, Postgres has GIN (for searching inside arrays, JSON and full text), GiST
(for ranges and geography), BRIN (tiny indexes for huge tables in time order) and hash indexes.

**Finding what to index.** The `pg_stat_statements` extension records every query's total time; sort by it, and
the top few are where an index pays off most. LabBox's "Postgres: the slow checkout" lab is a full incident about
exactly this.
:::

:::step{type=recap}
You can now:

- measure a query with `\timing` and `EXPLAIN ANALYZE`, and read Seq Scan, Index Scan and Rows Removed by Filter;
- create an index with `CREATE INDEX`, and see the planner choose it by itself;
- design a multi-column index for a query, and explain why the column order matters;
- weigh an index's cost (slower writes, disk) against what it saves (CPU, servers, waiting customers).

Next, chapter 13: designing tables so that every fact lives in one place.

:::photo{src="/lesson-images/sql/sql-12-notes.webp" alt="Handwritten notes about indexes: EXPLAIN ANALYZE: measure!; Seq Scan reads every row; CREATE INDEX ON t (col); 84 ms became 0.7 ms; many columns: order matters" ai="true"}
One page of notes for this chapter.
:::
:::
