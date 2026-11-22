:::step{type=story title="How much did each operator earn in November?"}
At the end of every month Safar pays its bus operators, and the finance team asks the same questions: how much
did each operator earn? Which route is the busiest? Who are our most loyal passengers?

Each answer is a **total**: not a list of rows, but a number per group. One total for Kaveri Travels, one for
Konkan Lines, and so on. That is what `GROUP BY` does, and with it SQL turns from a way of finding rows into a way
of **summarising** them. Reports, dashboards, invoices and monthly reviews are all built from this one idea.

Businesses printed totals per group long before SQL. An accounting machine like this IBM 407 read punched cards sorted by customer, added up each customer's amounts, and printed a subtotal every time the customer changed. GROUP BY does the same, without the cards.

:::photo{src="/lesson-images/sql/ibm-407.webp" alt="A woman operating a large grey IBM 407 accounting machine in an office, with card cabinets along the wall" credit="Pauli Lehtioksa" license="Public domain" source="https://commons.wikimedia.org/wiki/File:IBM-407-at-Nokia.jpg"}
An IBM 407 accounting machine at Nokia.
:::

:::mission
Total November's confirmed revenue per bus operator, and find Safar's busiest route.
:::
:::

:::step{type=concept title="Aggregates: many rows in, one value out"}
An **aggregate function** takes many rows and returns one value. You have met `COUNT(*)` already; here are its
four companions, on every confirmed booking:

```text
safar=# SELECT COUNT(*), SUM(amount_paise), AVG(amount_paise), MIN(amount_paise), MAX(amount_paise)
safar-# FROM bookings WHERE status = 'confirmed';
 count |    sum    |        avg         |  min  |  max
-------+-----------+--------------------+-------+--------
 10464 | 833231200 | 79628.363914373089 | 24000 | 184800
(1 row)
```

10,464 confirmed bookings brought in 833,231,200 paise: **Rs 83.3 lakh** in November. The average fare was about
Rs 796, the cheapest Rs 240 and the dearest Rs 1,848.

`AVG` gives many decimals; tidy it with `round(...)`, and convert to rupees on the way:
`round(AVG(amount_paise) / 100.0, 2)` gives `796.28`.

A handy Postgres extra: `FILTER` counts only some rows inside an aggregate, so one query can give several counts:

```text
safar=# SELECT COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled, COUNT(*) AS total FROM bookings;
 cancelled | total
-----------+-------
      1541 | 12005
(1 row)
```

**Check yourself:** what does `MAX(distance_km)` on `routes` return, one row or sixteen? (One row: the longest
distance, 840.)
:::

:::step{type=example title="Worked example: one total per group"}
`GROUP BY` splits the rows into groups that share a value, and runs the aggregates once **per group**. How many
buses, and how many seats, of each kind?

```sql
SELECT kind, COUNT(*) AS buses, SUM(seats) AS seats
FROM buses
GROUP BY kind
ORDER BY kind;
```

```text
     kind      | buses | seats
---------------+-------+-------
 AC seater     |     5 |   200
 AC sleeper    |     7 |   210
 non-AC seater |     4 |   180
(3 rows)
```

Picture what happened:

1. `FROM buses`: 16 rows.
2. `GROUP BY kind`: put them in three piles, one per kind.
3. `SELECT kind, COUNT(*), SUM(seats)`: for each pile, one result row: the kind, how many buses, how many seats.
4. `ORDER BY kind`: sort the three result rows.

:::trace{title='GROUP BY kind, seven of the buses'}
| bus | kind | AC seater pile | AC sleeper pile | non-AC seater pile | note |
|---|---|---|---|---|---|
| 1 | AC sleeper |  | 1 bus, 30 seats |  | The first bus starts the AC sleeper pile. |
| 2 | AC seater | 1 bus, 40 seats | 1 bus, 30 seats |  | A new kind starts a new pile. |
| 3 | AC sleeper | 1 bus, 40 seats | 2 buses, 60 seats |  | Same kind as bus 1: same pile. |
| 4 | non-AC seater | 1 bus, 40 seats | 2 buses, 60 seats | 1 bus, 45 seats | A third pile. |
| 5 | AC seater | 2 buses, 80 seats | 2 buses, 60 seats | 1 bus, 45 seats | Each pile keeps its own count and sum. |
| 6 | AC sleeper | 2 buses, 80 seats | 3 buses, 90 seats | 1 bus, 45 seats | And so on, for all 16 buses. |
| 7 | non-AC seater | 2 buses, 80 seats | 3 buses, 90 seats | 2 buses, 90 seats | At the end, each pile becomes one result row. |
:::

The rule that follows from the piles: **every column in `SELECT` must either be in `GROUP BY` or be inside an
aggregate**. A pile of AC sleepers has many operators; which one should Postgres show? It refuses to guess:

```text
safar=# SELECT kind, operator, COUNT(*) FROM buses GROUP BY kind;
ERROR:  column "buses.operator" must appear in the GROUP BY clause or be used in an aggregate function
```

Group by `kind, operator` instead, and you get one row per pair.
:::

:::step{type=predict title="Guess first"}
:::question
`SELECT status, COUNT(*) FROM bookings GROUP BY status` runs over 12,005 bookings. How many rows does it return?
:::
- [ ] 12,005
- [x] 2, one per status
- [ ] 1
:::explain
One row per group, and there are two statuses. It answered `confirmed 10464` and `cancelled 1541`.
:::
:::

:::step{type=task task=q_revenue_by_outlet title="Your turn: revenue per operator"}
Finance needs the payouts. In `06-totals/q1.sql`, return the **confirmed revenue of each bus operator** in
November: the `operator` and the total of `amount_paise` as `revenue_paise`, biggest first.

A booking knows its trip, and a trip knows its bus, and the bus knows its operator: join `bookings` to `trips` to
`buses`, keep the confirmed bookings, then group. Press **Check**.
:::

:::step{type=concept title="HAVING: filtering the groups"}
`WHERE` filters **rows**, before they are grouped. To filter **groups** by their totals, use `HAVING`, which runs
after grouping. Which cities have more than one route starting there?

```text
safar=# SELECT from_city_id, COUNT(*) AS routes FROM routes
safar-# GROUP BY from_city_id HAVING COUNT(*) > 1 ORDER BY from_city_id;
 from_city_id | routes
--------------+--------
            1 |      6
            2 |      2
            5 |      2
            6 |      2
(4 rows)
```

Pune (city 1) is Safar's hub, with six routes leaving it. `WHERE COUNT(*) > 1` would be an error: when `WHERE`
runs, there are no groups and no counts yet.

The full running order of a query, now complete:

| Step | Clause | What it does |
|---|---|---|
| 1 | `FROM`, `JOIN` | which rows to start from |
| 2 | `WHERE` | keep some rows |
| 3 | `GROUP BY` | make piles |
| 4 | `HAVING` | keep some piles |
| 5 | `SELECT` | compute the columns |
| 6 | `ORDER BY`, `LIMIT` | sort and cut |

And chapter 5's warning, measured. The sum of all trip fares is 40,155,000 paise. Join trips to their bookings
first, and the "same" sum comes out as 953,617,000, more than 23 times bigger: each trip's fare was added once for
every booking. **Total the "many" side (bookings), or total before you join.**
:::

:::step{type=task task=q_top_item title="Your turn: the busiest route"}
In `06-totals/q2.sql`, find Safar's **busiest route**: the `route_id` with the most **confirmed** bookings, and that
number of bookings. Return only the top route.

Group the confirmed bookings by their trip's route, sort by the count, and keep one row. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You want operators whose confirmed revenue is over Rs 15 lakh. Where does that condition go?
:::
- [ ] In `WHERE`
- [x] In `HAVING`, because it is about a group's total
- [ ] In `ORDER BY`
:::explain
The total exists only after grouping, so the filter belongs in `HAVING SUM(amount_paise) > 150000000`. "Confirmed
only" is about single rows, so it stays in `WHERE`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`SELECT kind, COUNT(*) FROM buses GROUP BY kind, operator` returns more rows than `GROUP BY kind`. Why?
:::
- [ ] It counts each bus twice
- [x] It makes one group per pair of kind and operator, and there are more pairs than kinds
- [ ] `GROUP BY` with two columns is an error
:::explain
Grouping by two columns makes one pile for every combination that exists, so you get finer groups.
:::
:::

:::step{type=deep-dive title="Go deeper: GROUPING SETS, and counting distinct things"}
**COUNT(DISTINCT ...).** `COUNT(DISTINCT passenger_id)` counts how many different passengers booked, not how many
bookings. On big tables it is expensive, because it has to remember every value it has seen.

**Subtotals in one query.** `GROUP BY ROLLUP (operator, kind)` returns a row per operator and kind, a subtotal row
per operator, and a grand total, with NULL marking the "all" columns. `GROUPING SETS` and `CUBE` give other
combinations. Reports that once took three queries take one.

**Grouping by expressions.** You can group by anything you can compute: `GROUP BY departs_at::date` for daily
totals, `GROUP BY extract(dow FROM departs_at)` for "which weekday is busiest". Chapter 8 builds a daily total
with a running sum on top.
:::

:::step{type=recap}
You can now:

- summarise rows with `COUNT`, `SUM`, `AVG`, `MIN` and `MAX`, and count some rows only with `FILTER`;
- make one total per group with `GROUP BY`, and keep every selected column grouped or aggregated;
- filter groups by their totals with `HAVING`, and rows before grouping with `WHERE`;
- avoid inflated totals by summing the "many" side, or totalling before you join.

Next, chapter 7: queries inside queries, and naming steps with WITH.

:::photo{src="/lesson-images/sql/sql-06-notes.webp" alt="Handwritten notes about totals: COUNT, SUM, AVG, MIN, MAX; GROUP BY: one row per group; select it, group it or total it; WHERE: rows, HAVING: groups; sum the many side" ai="true"}
One page of notes for this chapter.
:::
:::
