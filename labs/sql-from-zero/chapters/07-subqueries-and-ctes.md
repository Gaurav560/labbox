:::step{type=story title="Which trips cost more than average?"}
The pricing team asks a question that sounds simple: "Which trips cost more than the average fare?" Try to write
it with what you know. `WHERE fare_paise > AVG(fare_paise)`? Postgres refuses: an aggregate cannot be used in
`WHERE`, because `WHERE` runs before any totals exist (chapter 6's running order).

The answer needs **two steps**: first work out the average, then compare every trip with it. SQL lets you put a
whole query inside another one, as a **subquery**, and lets you give a step a name, with `WITH`, so a long
question reads like a short recipe. This chapter is about building answers in steps.

:::mission
Find the routes longer than average, and count the trips that were at least 90% full.
:::
:::

:::step{type=concept title="A query inside a query"}
First, the average on its own:

```text
safar=# SELECT AVG(fare_paise) FROM trips;
        avg
--------------------
 83656.250000000000
(1 row)
```

A query that returns exactly **one value** (one row, one column) can be used anywhere a single value can, inside
brackets. That is a **subquery**:

```text
safar=# SELECT id, fare_paise FROM trips
safar-# WHERE fare_paise > (SELECT AVG(fare_paise) FROM trips)
safar-# ORDER BY id LIMIT 4;
 id | fare_paise
----+------------
  6 |      99000
  8 |      94400
  9 |     156200
 10 |     113600
(4 rows)
```

Postgres runs the inner query first (the average, Rs 836.56), then uses its answer in the outer `WHERE`, exactly
as if you had typed `83656.25` there yourself. But unlike a typed number, it is always up to date.

The brackets matter. Without them, Postgres does not see a subquery:

```text
safar=# SELECT id FROM trips WHERE fare_paise > SELECT AVG(fare_paise) FROM trips;
ERROR:  syntax error at or near "SELECT"
```

A subquery can also return a **list** of values, for `IN`. The names of the passengers in seats 1 to 3 on trip 42:

```text
safar=# SELECT name FROM passengers
safar-# WHERE id IN (SELECT passenger_id FROM bookings WHERE trip_id = 42 AND seat_no <= 3)
safar-# ORDER BY name;
    name
-------------
 Pooja Rao
 Sana Pillai
 Zoya Rao
(3 rows)
```

**Check yourself:** could you write that last question as a join instead? (Yes: join `passengers` to `bookings`.
Many questions can be written both ways; use whichever reads more clearly.)
:::

:::step{type=example title="Worked example: a subquery as a table"}
A subquery can also stand in for a whole **table**, in `FROM`. How many confirmed bookings does a trip have, on
average? That is an average of counts, two levels of totals:

```sql
SELECT AVG(n)
FROM (
  SELECT trip_id, COUNT(*) AS n
  FROM bookings
  WHERE status = 'confirmed'
  GROUP BY trip_id
) AS per_trip;
```

```text
         avg
---------------------
 32.2962962962962963
(1 row)
```

1. The inner query makes a small table: one row per trip, with its count `n`.
2. `AS per_trip` gives that table a name; a subquery in `FROM` must have one.
3. The outer query averages the counts: about 32 confirmed bookings per trip that has any.

A subquery can even refer to the outer query's row. "Passengers for whom no booking exists":

```sql
SELECT COUNT(*)
FROM passengers p
WHERE NOT EXISTS (SELECT 1 FROM bookings b WHERE b.passenger_id = p.id);
```

That answered 3, the same three passengers chapter 5 found with a LEFT JOIN. `EXISTS` is true when the subquery
returns at least one row; `SELECT 1` is a convention, because only "is there a row?" matters.
:::

:::step{type=predict title="Guess first"}
:::question
A subquery used as `WHERE fare_paise > (SELECT ...)` accidentally returns **two** rows. What happens?
:::
- [ ] Postgres uses the first row
- [ ] Postgres compares with both and keeps rows bigger than either
- [x] An error: a subquery used as one value must return at most one row
:::explain
`>` needs one value on each side, so Postgres stops with "more than one row returned by a subquery used as an
expression". For a list of values, use `IN` (or `> ALL (...)`, `> ANY (...)`).
:::
:::

:::step{type=task task=above_average title="Your turn: longer than average"}
In `07-subqueries-and-ctes/q1.sql`, list the **routes that are longer than the average route**: their `id` and
`distance_km`, ordered by id.

Compute the average inside a subquery, in the `WHERE`. Press **Check**.
:::

:::step{type=concept title="WITH: giving each step a name"}
Subqueries inside subqueries get hard to read quickly. A **common table expression**, or **CTE**, does the same
job with a name, written first, with `WITH`. Which passengers are Safar's most loyal, with ten or more confirmed
trips?

```sql
WITH loyal AS (
  SELECT passenger_id, COUNT(*) AS trips
  FROM bookings
  WHERE status = 'confirmed'
  GROUP BY passenger_id
)
SELECT COUNT(*) AS passengers, MAX(trips) AS most
FROM loyal
WHERE trips >= 10;
```

```text
 passengers | most
------------+------
         79 |   15
(1 row)
```

Read it top to bottom like a recipe:

1. `WITH loyal AS (...)`: first, make a temporary table called `loyal`: one row per passenger with their trip
   count. It exists only while this query runs.
2. The main query uses `loyal` like any table: 79 passengers have ten or more trips; the most loyal has 15.

And because `loyal` is a table, you can join it. Their names:

```text
safar=# WITH loyal AS (...) SELECT p.name, l.trips FROM loyal l JOIN passengers p ON p.id = l.passenger_id
safar-# ORDER BY l.trips DESC, p.id LIMIT 3;
     name     | trips
--------------+-------
 Zoya Reddy   |    15
 Ishaan Joshi |    13
 Priya Shaikh |    13
(3 rows)
```

(`...` stands for the same `loyal` query as above.) A `WITH` can define several steps, separated by commas, each
one able to use the ones before it. Long reports become a list of small, named, readable steps.
:::

:::step{type=task task=almost_full title="Your turn: the almost full trips"}
Safar's planners want to know how often buses nearly sell out. In `07-subqueries-and-ctes/q2.sql`, return **how
many trips were at least 90% full**: trips whose confirmed bookings are at least 0.9 times their bus's seats.

Build it in two steps with `WITH`:

1. A step that gives, for every trip, its bus's `seats` and its number of confirmed bookings. Use a `LEFT JOIN`
   from trips to bookings, so trips with no bookings count as 0, and put the "confirmed" condition in the `ON`
   of that join, so it does not throw those trips away.
2. A main query that counts the rows of that step where confirmed bookings are at least `0.9 * seats`.

One number. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why can't you write `WHERE fare_paise > AVG(fare_paise)`?
:::
- [ ] `AVG` only works on whole numbers
- [x] `WHERE` runs on single rows before any totals exist, so an aggregate cannot be used there
- [ ] `AVG` must always be in `SELECT`
:::explain
The average needs its own step: a subquery in brackets, or a CTE. (Filtering groups by their totals is `HAVING`,
chapter 6.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In a LEFT JOIN from trips to bookings, where should `b.status = 'confirmed'` go so that trips with no confirmed
bookings still appear with a count of 0?
:::
- [x] In the join's `ON`, so it only decides which bookings match
- [ ] In `WHERE`, so it filters the result
- [ ] It does not matter
:::explain
A `WHERE` on the right table's column throws away the rows where it is NULL, quietly turning the LEFT JOIN back
into an inner join. In the `ON`, it only limits which bookings match, and every trip stays.
:::
:::

:::step{type=deep-dive title="Go deeper: CTEs in Postgres, and recursive queries"}
**CTEs are not slower.** Older Postgres versions always ran a CTE completely before the main query, which could
be slow. Since Postgres 12, a simple CTE used once is folded into the main query and optimised together with it.
`WITH x AS MATERIALIZED (...)` forces the old behaviour when you want it.

**Recursive CTEs.** `WITH RECURSIVE` lets a step refer to itself, to walk trees and graphs: an employee's whole
management chain, a category and all its subcategories, or every city reachable from Pune by changing buses.

**A puzzle in Safar's data.** Chapter 6 counted 480 trips, but the average above was only over trips that have
confirmed bookings. Count the trips that have **no** bookings at all, with what you learned in chapter 5: you
will find a surprising number of empty buses.
:::

:::step{type=recap}
You can now:

- use a subquery as one value (in brackets), as a list (with `IN`), or as a table (in `FROM`, with a name);
- test whether related rows exist with `EXISTS` and `NOT EXISTS`;
- build an answer in named steps with `WITH`, and join a CTE like any table;
- keep a LEFT JOIN a left join, by putting conditions on the right table in its `ON`.

Next, chapter 8: window functions, for ranks and running totals.

:::photo{src="/lesson-images/sql/sql-07-notes.webp" alt="Handwritten notes about subqueries and ctes: ( SELECT AVG(...) ) = one value; IN ( SELECT ... ) = a list; WITH step AS ( ... ); EXISTS / NOT EXISTS; LEFT JOIN rules go in ON" ai="true"}
One page of notes for this chapter.
:::
:::
