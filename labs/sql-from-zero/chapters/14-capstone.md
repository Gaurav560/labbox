:::step{type=story title="The November report"}
It is the first of December. Safar's founders meet the investors on Friday, and they need two answers from November,
on one page each:

1. **How did every route do?** Trips run, seats sold, money earned, best route first.
2. **Who are our best customers?** The top five by money spent, with a rank, for a thank-you gift.

Nobody will tell you which tables to use or in what order. That is the capstone: you plan the query from the
question, build it in steps, check every step against the data, and finish with a result someone else can trust.
Everything you need is in this course: joins (5), totals (6), steps with `WITH` (7), ranks (8).

Reports built from thousands of facts are not new. From 1839 travellers planned their journeys with Bradshaw's railway guides, which gathered every timetable into one book that answered a question at a glance. That is the job of your report too.

:::photo{src="/lesson-images/sql/bradshaw-1840.webp" alt="The worn brown cloth cover of a small book with a pale label reading Bradshaw's Railway Companion" credit="Unknown author" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Bradshaw's_Railway_Comanion_-_1840_-_cover.webp"}
Bradshaw's Railway Companion, 1840.
:::

:::mission
Build November's route report and the top five customers, each as one query.
:::
:::

:::step{type=concept title="Plan the query before you write it"}
Experienced engineers do not start typing `SELECT`. They start with the **shape of the answer** and work backwards.

**1. One row per what?** The route report has one row per **route**. So, somewhere, a `GROUP BY` route, or a join to
`routes` that keeps one row each.

**2. Which columns, and where does each live?**

| Column | Lives in | How |
|---|---|---|
| route id | `routes` | as is |
| from city, to city | `cities`, twice | join on `from_city_id` and `to_city_id` |
| trips run in November | `trips` | count per route |
| confirmed bookings | `bookings` | count per route, through `trips` |
| revenue | `bookings.amount_paise` | sum per route, through `trips` |

**3. Where are the traps?** Two of them, both from earlier chapters:

- **Joins multiply rows** (chapter 5). Counting trips **after** joining to bookings would count each trip once per
  booking. So trips and bookings must be totalled **separately**, each in its own step, then joined to routes.
- **Missing matches become NULL** (chapters 5 and 4). A route with no confirmed bookings would vanish in an inner
  join, or show NULL revenue. A `LEFT JOIN` and `COALESCE(..., 0)` keep it, with 0.

**4. Which rows count?** November only: trips leaving before `'2026-12-01'` (trip 481 from chapter 10 is in
December). Confirmed bookings only.

**5. In what order?** Highest revenue first; equal revenues by route id, so the order is always the same.

Writing those five answers down takes two minutes, and it turns a scary query into three small ones.
:::

:::step{type=example title="Worked example: one row per bus kind"}
Here is the same method on a smaller question (only to read): **for each kind of bus, how many buses, and how many
confirmed bookings in November?**

```sql
WITH kind_buses AS (
  SELECT kind, COUNT(*) AS buses
  FROM buses
  GROUP BY kind
),
kind_sales AS (
  SELECT bu.kind, COUNT(*) AS bookings
  FROM bookings b
  JOIN trips t ON t.id = b.trip_id
  JOIN buses bu ON bu.id = t.bus_id
  WHERE b.status = 'confirmed' AND t.departs_at < '2026-12-01'
  GROUP BY bu.kind
)
SELECT k.kind, k.buses, COALESCE(s.bookings, 0) AS bookings
FROM kind_buses k
LEFT JOIN kind_sales s ON s.kind = k.kind
ORDER BY bookings DESC, k.kind;
```

Each step answers one small question and can be run on its own while you build it (select from it, look, then
add the next step):

1. `kind_buses`: one row per kind, counting buses. No bookings involved, so nothing multiplies.
2. `kind_sales`: one row per kind, counting confirmed November bookings, through trips to buses.
3. The main query joins the two steps on `kind`, one row each, with `LEFT JOIN` and `COALESCE` so a kind with no
   sales still appears with 0.

The route report has exactly this shape, with routes instead of kinds, plus the two city names.
:::

:::step{type=predict title="Guess first"}
:::question
You count trips per route with `COUNT(*)` **after** joining trips to bookings. Route 8 ran 30 trips and sold 910
seats. What count do you get for its trips?
:::
- [ ] 30
- [x] Close to 910: one row per booking, not per trip
- [ ] 16
:::explain
After the join, each trip appears once per booking, so `COUNT(*)` counts bookings. That is why the report counts
trips in their own step. (`COUNT(DISTINCT t.id)` would also work, at a price on big tables.)
:::
:::

:::step{type=task task=monthly_report title="Your turn: the route report"}
In `14-capstone/q1.sql`, build **November's route report**: one row per route that ran in November, with

| Column | Meaning |
|---|---|
| `id` | the route's id |
| `from_city`, `to_city` | the two city names |
| `trips` | trips the route ran in November |
| `bookings` | confirmed bookings on those trips (0 if none) |
| `revenue_paise` | the confirmed revenue (0 if none) |

highest revenue first, then by route id. Build it in steps with `WITH`; run each step on its own before you join
them. Press **Check**: it compares your sixteen rows with the expected report.
:::

:::step{type=concept title="Ranks with ties, honestly"}
The second page wants the top five customers with a rank. Chapter 8 gave you three ways to number rows, and here the
choice matters, because Safar's data has a real tie. In this lab the top five by confirmed spend came out as:

```text
     name     | trips | spent_paise | rank
--------------+-------+-------------+------
 Vikram Bose  |    13 |     1460500 |    1
 Zoya Reddy   |    15 |     1343700 |    2
 Priya Shaikh |    13 |     1223600 |    3
 Vikram Reddy |    12 |     1121300 |    4
 Rohan Khan   |     9 |     1121300 |    4
(5 rows)
```

Vikram Reddy and Rohan Khan spent exactly the same, Rs 11,213. `RANK()` gives them both 4th place, which is the
honest answer: neither is ahead. `ROW_NUMBER()` would have called one of them 5th by a coin toss.

Notice too: Zoya Reddy took the most trips (15), but Vikram Bose spent the most. "Best customer" depends on what you
measure, and a good report says which.

One more decision hides in "top five": the sixth customer may also have spent Rs 11,213. `LIMIT 5` cuts after five
rows, so the order of equal rows must be fixed (by passenger id) to make the cut the same every time.
:::

:::step{type=task task=top_passengers title="Your turn: the five best customers"}
In `14-capstone/q2.sql`, return **Safar's five best customers by confirmed spend**:

| Column | Meaning |
|---|---|
| `name` | the passenger's name |
| `trips` | their confirmed bookings |
| `spent_paise` | the total of their confirmed `amount_paise` |
| `rank` | `RANK()` by spend, 1 = spent the most |

most first, equal spends by passenger id, five rows. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Your report shows 15 routes, but Safar has 16, and every route ran trips in November. What is the most likely bug?
:::
- [ ] A missing `ORDER BY`
- [x] An inner join to the sales step dropped a route with no confirmed bookings; use a LEFT JOIN with COALESCE
- [ ] `COUNT(*)` instead of `SUM`
:::explain
Rows that silently disappear are almost always an inner join where a left join was needed. Count your rows against
what you know (16 routes) before you trust a report.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Two customers spent the same amount and are 4th and 5th by spend. Which ranking is fair to both?
:::
- [x] `RANK()`: both are 4th
- [ ] `ROW_NUMBER()`: 4th and 5th
- [ ] Neither; remove one of them
:::explain
`RANK()` gives equal values the same rank. `ROW_NUMBER()` must pick an order, which says one is ahead when neither is.
:::
:::

:::step{type=deep-dive title="Go deeper: where to go from here"}
You can now read, change, protect, design and speed up a real relational database. A few directions for later:

**Postgres features worth knowing.** JSON columns (`jsonb`) for flexible data with indexes; full-text search; arrays;
`generate_series` for calendars (Safar's data script uses it); extensions such as PostGIS for maps.

**Running a database.** Backups and point-in-time recovery, replication to a standby, connection pooling (PgBouncer),
`VACUUM` and why Postgres needs it, monitoring slow queries with `pg_stat_statements`. LabBox's "Postgres: the slow
checkout" and "Postgres: transactions and locks" labs are real incidents about these.

**SQL from code.** Every language talks to databases through a driver (psycopg in Python, JDBC in Java, pg in Node).
Always pass values as **parameters**, never by gluing text into the query, or you open the door to SQL injection.
Frameworks such as Spring Data or Django build queries for you, but the SQL they run is exactly what you now
understand, and when they are slow, `EXPLAIN` still tells you why.

**Analytics.** The same SQL powers data warehouses (BigQuery, Snowflake, Redshift, DuckDB), where window functions
and CTEs are everyday tools. Chapter 8's running total is a line in a thousand dashboards.
:::

:::step{type=recap}
You can now:

- plan a query from the shape of its answer: one row per what, which columns from where, which traps, which rows,
  which order;
- build a report in steps with `WITH`, totalling each side separately to avoid multiplied rows;
- keep rows without matches with `LEFT JOIN` and `COALESCE`, and check row counts against what you know;
- rank fairly with `RANK()`, and make `LIMIT` cuts the same every time.

You have finished SQL from zero: from your first `SELECT` to normalised tables, transactions and indexes you measured
yourself. Well done.

:::photo{src="/lesson-images/sql/sql-14-notes.webp" alt="Handwritten notes about the report: 1. one row per what?; 2. which columns, from where?; 3. traps: multiplied rows, NULLs; build it step by step: WITH; RANK is fair to ties" ai="true"}
One page of notes for this chapter.
:::
:::
