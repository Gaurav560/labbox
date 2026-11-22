:::step{type=story title="Trip 42 leaves at 22:45. On which bus?"}
Welcome to Part 2. So far every question had its answer in one table. Real questions almost never do.

Ask the database about trip 42 and it says: route 10, bus 10, 3 November at 22:45. That is all a trip knows: ids
pointing at other tables. Which operator runs bus 10? What kind of bus is it? Where does route 10 go? Those facts
live in `buses`, `routes` and `cities`, each stored **once**, on purpose (chapter 1's "one fact in one place").

To answer a real question, you **join** tables back together along their keys. Joins are where SQL becomes
powerful, and also where most surprising results come from, so this chapter goes slowly: what a join really
does, the two kinds you will use every day, and the rows that can quietly appear or disappear.

Maps have joined places for a long time. This railway map of India from 1870 is mostly cities and the lines between them, which is exactly what Safar's routes table holds: a line is just two city ids, and the names live with the cities.

:::photo{src="/lesson-images/sql/india-railway-map-1870.webp" alt="An old pale map of India with thin railway lines drawn between cities" credit="Unknown author" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Railway_map_of_India_1870.jpg"}
A railway map of India, 1870.
:::

:::mission
List every route with the names of its two cities, and find the passengers who have never booked a seat.
:::
:::

:::step{type=concept title="JOIN: matching rows along a key"}
Here is trip 42 on its own:

```text
safar=# SELECT id, route_id, bus_id, departs_at FROM trips WHERE id = 42;
 id | route_id | bus_id |     departs_at
----+----------+--------+---------------------
 42 |       10 |     10 | 2026-11-03 22:45:00
(1 row)
```

To see the bus, put both tables in `FROM` with `JOIN`, and say **how rows match** with `ON`:

```text
safar=# SELECT t.id, t.departs_at, b.operator, b.kind
safar-# FROM trips t JOIN buses b ON b.id = t.bus_id
safar-# WHERE t.id = 42;
 id |     departs_at      |    operator    |   kind
----+---------------------+----------------+-----------
 42 | 2026-11-03 22:45:00 | Kaveri Travels | AC seater
(1 row)
```

Read it carefully:

1. `FROM trips t JOIN buses b`: two tables. `t` and `b` are **aliases**, short names for the tables in this
   query, so you can write `t.id` instead of `trips.id`.
2. `ON b.id = t.bus_id`: a trip row and a bus row belong together when the bus's id equals the trip's `bus_id`.
   This is exactly the foreign key you saw in `\d trips`.
3. The result rows have the columns of **both** tables, so `SELECT` can take `departs_at` from the trip and
   `operator` from the bus.

Think of it as: for every trip, find the bus whose id matches, and glue the two rows side by side. Trip 42 runs
on an AC seater from Kaveri Travels.

When both tables have a column with the same name, you must say which one you mean, or Postgres refuses:

```text
safar=# SELECT id, name FROM routes JOIN cities ON cities.id = routes.from_city_id LIMIT 1;
ERROR:  column reference "id" is ambiguous
```

`routes` and `cities` both have an `id`. Write `routes.id` (or `r.id` with an alias) and the error is gone.

**Check yourself:** in `ON b.id = t.bus_id`, which side is the primary key and which the foreign key? (`b.id` is
the bus's primary key; `t.bus_id` is the trip's foreign key pointing at it.)
:::

:::step{type=example title="Worked example: who sits where on trip 42"}
A booking knows its passenger only by `passenger_id`. To show names on a seat map, join `bookings` to
`passengers`:

```sql
SELECT b.id, b.seat_no, p.name
FROM bookings b
JOIN passengers p ON p.id = b.passenger_id
WHERE b.trip_id = 42 AND b.status = 'confirmed'
ORDER BY b.seat_no
LIMIT 4;
```

```text
 id  | seat_no |    name
-----+---------+-------------
 936 |       1 | Sana Pillai
 937 |       2 | Pooja Rao
 938 |       3 | Zoya Rao
 939 |       4 | Vikram Rao
(4 rows)
```

1. `FROM bookings b JOIN passengers p ON p.id = b.passenger_id`: each booking finds its passenger.
2. `WHERE` filters the **joined** rows: only trip 42, only confirmed. Conditions can use columns from either
   table.
3. `ORDER BY` and `LIMIT` work exactly as before.

A query can join as many tables as it needs, one `JOIN ... ON ...` after another. A route needs **two** joins to
`cities`, one for each end, so the `cities` table appears twice with two different aliases:

```sql
SELECT r.id, c.name AS from_city
FROM routes r
JOIN cities c ON c.id = r.from_city_id
ORDER BY r.id;
```

That gives the start city (route 1 from Pune, route 2 from Mumbai, route 4 from Kolhapur, and so on). For the end
city you join `cities` a second time, under another alias, on `to_city_id`.
:::

:::step{type=predict title="Guess first"}
:::question
Safar has 2,000 passengers and 12,005 bookings, and every booking has a passenger. How many rows does
`SELECT COUNT(*) FROM passengers p JOIN bookings b ON b.passenger_id = p.id` count?
:::
- [ ] 2,000, one per passenger
- [x] 12,005, one per matching pair
- [ ] 24,010
:::explain
A join makes one row for every **pair** that matches. A passenger with six bookings appears six times. So the count
is the number of bookings: 12,005. Joins multiply rows; keep that in mind whenever a total looks too big.
:::
:::

:::step{type=task task=route_names title="Your turn: routes with city names"}
In `05-joins/q1.sql`, list **every route** with both city names: the route's `id`, the name of the city it starts
from as `from_city`, and the name of the city it goes to as `to_city`, ordered by route id.

You need `cities` twice, under two aliases. Run it (16 rows), then press **Check**.
:::

:::step{type=concept title="LEFT JOIN: keep the rows that have no match"}
The join you have used is an **inner join**: it keeps only pairs that match. A row with no partner simply
disappears. Usually that is what you want. Sometimes, the rows **without** a partner are the whole point.

Here is the difference on a tiny example: three passengers, and bookings for two of them (only to read; built
inline with `VALUES`, not Safar's tables):

```text
safar=# SELECT p.name, b.seat FROM (VALUES (1, 'Asha'), (2, 'Ravi'), (3, 'Meera')) AS p(id, name)
safar-#   JOIN (VALUES (1, 12), (1, 13), (3, 7)) AS b(passenger_id, seat) ON b.passenger_id = p.id;
 name  | seat
-------+------
 Asha  |   13
 Asha  |   12
 Meera |    7
(3 rows)
```

Ravi has no booking, so the inner join dropped him. Change `JOIN` to `LEFT JOIN`:

```text
 name  | seat
-------+------
 Asha  |   13
 Asha  |   12
 Ravi  |
 Meera |    7
(4 rows)
```

`LEFT JOIN` keeps **every row of the left table** (the one before `JOIN`). When a row has no match on the right,
it still appears once, with **NULL** in every column from the right table. Ravi's seat is NULL.

That gives you a classic pattern: **find what has no match** with `LEFT JOIN` and `WHERE right_side.id IS NULL`.
Try it on Safar's real data:

```text
safar=# SELECT COUNT(*) FROM passengers p JOIN bookings b ON b.passenger_id = p.id;
 count
-------
 12005
(1 row)

safar=# SELECT COUNT(*) FROM passengers p LEFT JOIN bookings b ON b.passenger_id = p.id;
 count
-------
 12008
(1 row)
```

Three more rows with the `LEFT JOIN`. Each one is a passenger with no booking at all, kept with NULLs on the
booking side. Who are they? That is your next task.

:::diagram{name="left-join"}
An inner join keeps only matching pairs; a left join keeps every left row, with NULLs where nothing matches.
:::
:::

:::step{type=task task=never_booked title="Your turn: passengers who never booked"}
Safar wants to send a welcome offer to people who signed up but never booked. In `05-joins/q2.sql`, list **the
passengers who have never booked anything**: their `id` and `name`, ordered by id.

Use a `LEFT JOIN` from `passengers` to `bookings`, and keep only the rows where the booking side is NULL. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`SELECT ... FROM cities c LEFT JOIN routes r ON r.from_city_id = c.id`. A new city with no routes yet is in
`cities`. Is it in the result?
:::
- [ ] No, it has no routes to match
- [x] Yes, once, with NULL in the route columns
- [ ] Yes, once for every route in the table
:::explain
A left join keeps every row of the left table. The new city appears once, with NULLs on the right side, which is
exactly how you would find "cities without routes".
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A query joins `trips` (480 rows) and `bookings` (12,005 rows) on `b.trip_id = t.id`, then sums `t.fare_paise`.
Why is the total far bigger than the sum of all fares?
:::
- [ ] Postgres adds the fares twice
- [x] Each trip appears once per booking, so its fare is added once for every booking
- [ ] Bookings have their own fares
:::explain
Joins multiply rows: a trip with 30 bookings appears 30 times. Sum a value from the "one" side after joining to the
"many" side and you count it many times. Chapter 6 shows how to total properly.
:::
:::

:::step{type=deep-dive title="Go deeper: other joins, and how Postgres runs them"}
**RIGHT and FULL joins.** `RIGHT JOIN` keeps every row of the right table instead; it is a left join written the
other way round, and most people just swap the tables. `FULL JOIN` keeps unmatched rows from both sides.

**The forgotten ON.** `SELECT COUNT(*) FROM trips, buses` (two tables with a comma and no condition) is a **cross
join**: every trip paired with every bus, 480 x 16 = 7,680 rows. Occasionally useful (Safar's data script uses one
to make a trip for every day and every route), usually a bug.

**How Postgres joins.** For each join, the planner picks a method: a **nested loop** (for each row on one side, look
up its partners, great with an index), a **hash join** (build a hash table of one side in memory, then stream the
other side through it), or a **merge join** (sort both sides by the key and walk them together). `EXPLAIN` shows
which one it chose. You still just say what you want.

**USING.** When both key columns have the same name, `JOIN cities USING (city_id)` is a shorter `ON`.
:::

:::step{type=recap}
You can now:

- join tables along their keys with `JOIN ... ON ...`, using aliases and naming columns that exist in both;
- join one table twice under two aliases, as for a route's two cities;
- explain why a join multiplies rows, one per matching pair;
- keep unmatched rows with `LEFT JOIN`, and find "what has no match" with `IS NULL` on the right side.

Next, chapter 6: totals per group, with GROUP BY.

:::photo{src="/lesson-images/sql/sql-05-notes.webp" alt="Handwritten notes about joins: JOIN ... ON a.id = b.a_id; one row per matching pair; joins multiply rows!; LEFT JOIN keeps every left row; no match? WHERE b.id IS NULL" ai="true"}
One page of notes for this chapter.
:::
:::
