:::step{type=story title="Rank the operators, but keep the details"}
The operators' meeting is on Monday, and the finance team wants a league table: every operator, their revenue,
and their **rank**: first, second, third. They also want a chart of November's revenue, day by day, with a line
that climbs as the month goes on: the **running total**.

`GROUP BY` can total things, but it squashes rows into one per group: you lose the details. Ranks and running
totals need something different: a calculation that looks **across** rows while keeping every row. SQL calls
these **window functions**, and they are one of the most useful tools in reporting. Many people who have used
SQL for years have never learned them; after this chapter, you will have.

:::mission
Rank the operators by revenue, and build November's daily revenue with a running total.
:::
:::

:::step{type=concept title="OVER: a total that keeps the rows"}
Compare two ways of counting buses. `GROUP BY` gives one row. A **window function**, any aggregate followed by
`OVER (...)`, gives the total **on every row**:

```text
safar=# SELECT id, operator, seats,
safar-#   COUNT(*) OVER () AS all_buses, SUM(seats) OVER () AS all_seats
safar-# FROM buses ORDER BY id LIMIT 3;
 id |     operator     | seats | all_buses | all_seats
----+------------------+-------+-----------+-----------
  1 | Sahyadri Travels |    30 |        16 |       590
  2 | Sahyadri Travels |    40 |        16 |       590
  3 | Deccan Rides     |    30 |        16 |       590
(3 rows)
```

Each bus keeps its own row, and beside it sit the totals over its **window**. `OVER ()`, with nothing inside,
means "the window is all the rows". Now each row can be compared with the whole: bus 1 has 30 of the 590 seats.

`PARTITION BY` splits the window into groups, like `GROUP BY` but without squashing:

```text
safar=# SELECT id, operator, seats, SUM(seats) OVER (PARTITION BY operator) AS operator_seats
safar-# FROM buses ORDER BY operator, id LIMIT 5;
 id |     operator     | seats | operator_seats
----+------------------+-------+----------------
  3 | Deccan Rides     |    30 |            105
  4 | Deccan Rides     |    45 |            105
 12 | Deccan Rides     |    30 |            105
  7 | Godavari Coaches |    45 |            115
  8 | Godavari Coaches |    40 |            115
(5 rows)
```

Every Deccan Rides bus sees the Deccan Rides total (105 seats); every Godavari bus sees Godavari's.

**Check yourself:** how many rows does `SELECT operator, SUM(seats) OVER (PARTITION BY operator) FROM buses`
return? (16, one per bus. `GROUP BY operator` would return 5.)
:::

:::step{type=example title="Worked example: ranking routes by length"}
With `ORDER BY` inside `OVER`, the window has an order, and a whole family of functions becomes possible. Here are
three ways to number the routes from longest to shortest:

```sql
SELECT id, distance_km,
       RANK()       OVER (ORDER BY distance_km DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY distance_km DESC) AS dense,
       ROW_NUMBER() OVER (ORDER BY distance_km DESC, id) AS row_no
FROM routes
ORDER BY row_no
LIMIT 6;
```

```text
 id | distance_km | rank | dense | row_no
----+-------------+------+-------+--------
 15 |         840 |    1 |     1 |      1
 16 |         840 |    1 |     1 |      2
  9 |         710 |    3 |     2 |      3
 10 |         710 |    3 |     2 |      4
  7 |         590 |    5 |     3 |      5
  8 |         590 |    5 |     3 |      6
(6 rows)
```

Look at how they treat the ties (routes 15 and 16 are both 840 km):

1. `RANK()` gives equal rows the same rank, then **skips**: 1, 1, 3. Like a race where two people share first
   place and the next runner is third.
2. `DENSE_RANK()` gives equal rows the same rank, **without** gaps: 1, 1, 2.
3. `ROW_NUMBER()` numbers every row differently, 1 to 16, using the tie-breaker (`id`) to decide.

Which one is right depends on the question. A league table usually wants `RANK()`. "The newest booking per
passenger" wants `ROW_NUMBER()` with `PARTITION BY passenger_id`, then keeping row number 1.
:::

:::step{type=predict title="Guess first"}
:::question
Three operators have revenues of 100, 100 and 80. What `RANK()` does the third one get, ordering by revenue, highest
first?
:::
- [ ] 2
- [x] 3
- [ ] 1
:::explain
The first two share rank 1, and `RANK()` skips the rank they used up, so the next is 3. `DENSE_RANK()` would give 2.
:::
:::

:::step{type=task task=rank_operators title="Your turn: the operators' league table"}
In `08-window-functions/q1.sql`, build the league table: every **operator**, their confirmed revenue as
`revenue_paise`, and their `rank` (1 for the most revenue), ordered by rank.

You can put a window function on top of a `GROUP BY`: rank by `SUM(amount_paise)` inside the `OVER`, in the same
query that groups by operator (the grouping happens first, then the window). Press **Check**.
:::

:::step{type=concept title="Running totals"}
An aggregate with `ORDER BY` inside its `OVER` becomes a **running** aggregate: for each row, it covers every row
up to this one. A tiny example (only to read; built inline):

```text
safar=# SELECT d, n, SUM(n) OVER (ORDER BY d) AS running
safar-# FROM (VALUES (1, 10), (2, 5), (3, 20)) AS t(d, n);
 d | n  | running
---+----+---------
 1 | 10 |      10
 2 |  5 |      15
 3 | 20 |      35
(3 rows)
```

:::trace{title='SUM(n) OVER (ORDER BY d)'}
| d | n | running | note |
|---|---|---|---|
| 1 | 10 | 10 | Only row 1 so far: 10. |
| 2 | 5 | 15 | Rows 1 and 2: 10 + 5. |
| 3 | 20 | 35 | Rows 1 to 3: 10 + 5 + 20. |
:::

That is the climbing line the finance team wants for November. Each day needs its own total first (a
`GROUP BY` on the day), and then a running sum **of those totals**. A window function over an aggregate looks
odd the first time, but it reads exactly as it sounds:

```sql
SUM(SUM(b.amount_paise)) OVER (ORDER BY day)
```

The inner `SUM` is the `GROUP BY` total of one day; the outer `SUM ... OVER` adds up those daily totals, in date
order. The same trick gives a running count, a running average, or a seven-day moving average
(`AVG(...) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`).
:::

:::step{type=task task=running_total title="Your turn: November, day by day"}
In `08-window-functions/q2.sql`, return one row for **each day of November** (by the trip's departure date): the
`day`, that day's confirmed revenue as `revenue_paise`, and the `running_total` of revenue so far that month,
ordered by day.

`departs_at::date` gives a trip's day. Thirty rows; the last running total is the month's revenue. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is the difference between `GROUP BY operator` and `OVER (PARTITION BY operator)`?
:::
- [ ] None
- [x] `GROUP BY` returns one row per operator; `PARTITION BY` keeps every row and adds the group's value to each
- [ ] `PARTITION BY` is faster
:::explain
Both split rows by operator. `GROUP BY` squashes each group into one row; a window keeps the rows and shows the
group's total, rank or running value beside each one.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You want each passenger's **first** booking. Which window function fits?
:::
- [ ] `RANK() OVER (ORDER BY booked_at)`
- [x] `ROW_NUMBER() OVER (PARTITION BY passenger_id ORDER BY booked_at)`, then keep row number 1
- [ ] `SUM(1) OVER ()`
:::explain
Partition by passenger, number each passenger's bookings from the earliest, and keep number 1 (in a CTE, since a
window function cannot go in `WHERE`).
:::
:::

:::step{type=deep-dive title="Go deeper: LAG, LEAD and frames"}
**Looking at neighbours.** `LAG(value) OVER (ORDER BY ...)` gives the value from the previous row, and
`LEAD(value)` from the next. "How much did revenue change from yesterday?" is
`revenue - LAG(revenue) OVER (ORDER BY day)`. The first row has no previous row, so `LAG` gives NULL there.

**Frames.** Inside `OVER`, `ROWS BETWEEN ... AND ...` says exactly which rows the window covers: `UNBOUNDED
PRECEDING` (from the start), `6 PRECEDING` (the six rows before), `CURRENT ROW`, `1 FOLLOWING`. That is how moving
averages are built.

**Where windows run.** Window functions run after `WHERE`, `GROUP BY` and `HAVING`, just before `ORDER BY`. So you
cannot filter on a window's result in the same query: wrap it in a CTE (chapter 7) and filter in the main query,
for example `WHERE rank <= 3` for a top three.
:::

:::step{type=recap}
You can now:

- add a total beside every row with `OVER ()`, and per group with `PARTITION BY`;
- rank rows with `RANK`, `DENSE_RANK` and `ROW_NUMBER`, and choose the right one for ties;
- build running totals with `SUM(...) OVER (ORDER BY ...)`, including over `GROUP BY` totals;
- filter on a window's result by wrapping the query in a CTE.

That completes Part 2. Next, Part 3 starts with chapter 9: creating your own tables, with rules the database
enforces.

:::photo{src="/lesson-images/sql/sql-08-notes.webp" alt="Handwritten notes about window functions: SUM(x) OVER () keeps every row; PARTITION BY = groups, no squash; RANK: 1, 1, 3; ROW_NUMBER: 1, 2, 3; running total: ORDER BY in OVER" ai="true"}
One page of notes for this chapter.
:::
:::
