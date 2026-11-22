:::step{type=story title="Which are Safar's longest routes?"}
The marketing team is planning a "long journeys" campaign and asks: "What are our three longest routes?" You know
how to get rows out of a table. But the question is about **order** ("longest") and **how many** ("three"), and
you will soon want results shaped in other ways too: each value only once, a fare in rupees instead of paise, a
label like "long" or "short".

This chapter covers the clauses that shape a result: `ORDER BY` to sort, `LIMIT` to keep the top few,
`DISTINCT` to remove repeats, and expressions and `CASE` to compute new columns on the fly. Together with
`WHERE`, they answer most of the questions people ask a database every day.

:::mission
Find the three longest routes, ties included properly, and list every bus operator once.
:::
:::

:::step{type=concept title="ORDER BY: sorting, and breaking ties"}
`ORDER BY` sorts the result by one or more columns. Smallest first is the default (`ASC`, ascending); add `DESC`
for largest first. Here are the five longest routes:

```text
safar=# SELECT id, distance_km FROM routes ORDER BY distance_km DESC LIMIT 5;
 id | distance_km
----+-------------
 15 |         840
 16 |         840
 10 |         710
  9 |         710
  8 |         590
(5 rows)
```

Look closely at routes 10 and 9: both are 710 km, and they came back as 10, then 9. Run it again tomorrow and it
could be 9, then 10. When rows are **equal** on the sort column, their order is not defined. Worse, look at the
fifth row: route 8 (590 km) made it in, but route 7 is also 590 km and was cut off. Which one you get is luck.

The fix is a **tie-breaker**: a second sort column, used only when the first is equal:

```text
safar=# SELECT id, distance_km FROM routes ORDER BY distance_km DESC, id LIMIT 5;
 id | distance_km
----+-------------
 15 |         840
 16 |         840
  9 |         710
 10 |         710
  7 |         590
(5 rows)
```

Now the order is fully decided: longest first, and among equal distances, the lowest id first. The same query gives
the same answer every time. Each column in `ORDER BY` can have its own direction: `ORDER BY operator, seats DESC`
sorts operators A to Z, and within each operator the biggest buses first.

**Check yourself:** why does a tie-breaker matter most together with `LIMIT`? (Because `LIMIT` cuts the list, and
an undefined order decides **which** of the equal rows make the cut.)
:::

:::step{type=example title="Worked example: pages of results"}
Apps rarely show all results at once. They show a page, say passengers 11 to 15. `LIMIT` takes a number of rows;
`OFFSET` skips some first:

```sql
SELECT id, name
FROM passengers
ORDER BY id
LIMIT 5 OFFSET 10;
```

```text
 id |      name
----+----------------
 11 | Neel Patil
 12 | Priya Shaikh
 13 | Rohan Kulkarni
 14 | Pooja Reddy
 15 | Dev Sharma
(5 rows)
```

1. `ORDER BY id`: a fixed order first. Pages without a fixed order can repeat or skip rows.
2. `OFFSET 10`: skip the first ten rows (page 1 and page 2, at 5 a page).
3. `LIMIT 5`: then keep five: page 3.

For page `p` with `n` rows a page, the offset is `(p - 1) * n`. (On huge tables, big offsets get slow, because the
database still walks through every skipped row; the deep dive shows what teams do instead.)
:::

:::step{type=predict title="Guess first"}
:::question
`SELECT status FROM bookings` returns 12,005 rows. What does `SELECT DISTINCT status FROM bookings` return?
:::
- [ ] 12,005 rows, sorted
- [x] One row for each different status: two rows
- [ ] The number of different statuses
:::explain
`DISTINCT` removes repeated rows from the result, so each different value appears once: `confirmed` and
`cancelled`. To **count** them you would write `COUNT(DISTINCT status)`.
:::
:::

:::step{type=try title="See it: DISTINCT"}
Look at a few raw statuses, then at the distinct ones:

```text
safar=# SELECT status FROM bookings LIMIT 5;
  status
-----------
 cancelled
 cancelled
 confirmed
 confirmed
 confirmed
(5 rows)

safar=# SELECT DISTINCT status FROM bookings;
  status
-----------
 confirmed
 cancelled
(2 rows)
```

Exactly two values exist, in small letters. This is the habit that would have saved you from chapter 2's
`'Confirmed'` trap: before filtering on a text column, look at its distinct values.

`DISTINCT` works on whole rows: `SELECT DISTINCT kind FROM buses ORDER BY kind` gives the three kinds, `AC seater`,
`AC sleeper` and `non-AC seater`. With two columns, it removes rows where **both** columns repeat.
:::

:::step{type=task task=longest_routes title="Your turn: the three longest routes"}
Answer the marketing team. In `03-sorting-and-shaping/q1.sql`, return the **three longest routes**: their `id` and
`distance_km`, longest first. When two routes are equally long, the lower id comes first.

Run it with `psql -f q1.sql`, then press **Check**.
:::

:::step{type=concept title="New columns: expressions, AS and CASE"}
A `SELECT` list can hold more than column names. It can **compute**: arithmetic, functions, labels. Fares are in
paise; customers think in rupees:

```text
safar=# SELECT id, fare_paise, fare_paise / 100 AS fare_rupees FROM trips ORDER BY id LIMIT 3;
 id | fare_paise | fare_rupees
----+------------+-------------
  1 |      33000 |         330
  2 |      24000 |         240
  3 |      50600 |         506
(3 rows)
```

`AS fare_rupees` names the new column; without it, Postgres would call it `?column?`. Nothing in the table
changed: the computed column exists only in this answer.

One trap with division: dividing a whole number by a whole number **throws away the fraction**:

```text
safar=# SELECT 7 / 2 AS whole, 7 / 2.0 AS exact, round(7 / 2.0, 1) AS rounded;
 whole |       exact        | rounded
-------+--------------------+---------
     3 | 3.5000000000000000 |     3.5
(1 row)
```

`7 / 2` is 3, not 3.5. Make one side a decimal (`2.0`) to keep the fraction, and `round(value, places)` to tidy
it. (Fares divide cleanly here only because every fare is a whole number of rupees.)

**CASE** turns values into labels, like an if-else inside a query. It checks each `WHEN` in order and uses the
first that is true:

```text
safar=# SELECT id, distance_km,
safar-#   CASE WHEN distance_km < 300 THEN 'short'
safar-#        WHEN distance_km < 600 THEN 'medium'
safar-#        ELSE 'long' END AS length
safar-# FROM routes ORDER BY id LIMIT 6;
 id | distance_km | length
----+-------------+--------
  1 |         150 | short
  2 |         150 | short
  3 |         230 | short
  4 |         230 | short
  5 |         450 | medium
  6 |         450 | medium
(6 rows)
```

Route 5 is 450 km: not under 300, but under 600, so `medium`. Anything else falls to `ELSE`. Later chapters use
`CASE` to count things in groups ("how many long routes per city").
:::

:::step{type=task task=distinct_operators title="Your turn: every operator, once"}
Safar works with several bus operators, and each runs several buses. In `03-sorting-and-shaping/q2.sql`, list
**every operator's name exactly once**, from A to Z.

Press **Check** when `psql -f q2.sql` shows a short, sorted list without repeats.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You want page 4 of the passengers list, 20 per page, by id. Which clause is right?
:::
- [ ] `LIMIT 20 OFFSET 80`
- [x] `LIMIT 20 OFFSET 60`
- [ ] `LIMIT 80 OFFSET 20`
:::explain
Pages 1 to 3 hold 60 rows, so skip 60 (`(4 - 1) * 20`) and take 20.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `SELECT 450 / 60` return in Postgres?
:::
- [ ] 7.5
- [x] 7
- [ ] 8
:::explain
Whole number divided by whole number gives a whole number, rounded towards zero. `450 / 60.0` would give 7.5.
:::
:::

:::step{type=deep-dive title="Go deeper: the order SQL really runs in, and faster paging"}
**Written order and running order differ.** You write `SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT`. The
database works through it as: `FROM` (which table), `WHERE` (which rows), `SELECT` (which columns and computed
values), `DISTINCT`, `ORDER BY`, then `LIMIT` and `OFFSET`. That explains some surprises: you can `ORDER BY` a
column alias defined in `SELECT` (it already exists by then), but you cannot use that alias in `WHERE` (it does not
exist yet).

**Keyset paging.** `OFFSET 100000` makes the database produce and throw away 100,000 rows to show 20. Apps with
deep pages instead remember the last row they showed and ask for what comes after it:
`WHERE id > 120 ORDER BY id LIMIT 20`. With an index on `id`, every page is equally fast.

**NULLS FIRST and LAST.** When a sort column has missing values (chapter 4), Postgres puts them last in ascending
order and first in descending order. `ORDER BY email NULLS LAST` says where you want them.
:::

:::step{type=recap}
You can now:

- sort with `ORDER BY`, in either direction, and add a tie-breaker so the order is always the same;
- keep the top few with `LIMIT`, and page through results with `OFFSET`;
- remove repeats with `DISTINCT`, and look at a column's distinct values before filtering on it;
- compute new columns with arithmetic, `AS` and `CASE`, and avoid whole-number division.

Next, chapter 4: text, dates and the strange value called NULL.

:::photo{src="/lesson-images/sql/sql-03-notes.webp" alt="Handwritten notes about sorting and shaping: ORDER BY x DESC, id; LIMIT 5 OFFSET 10; DISTINCT: each value once; 7 / 2 = 3, but 7 / 2.0 = 3.5; CASE WHEN ... THEN ... END" ai="true"}
One page of notes for this chapter.
:::
:::
