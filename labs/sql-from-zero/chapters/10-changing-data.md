:::step{type=story title="Every fare on Safar is now zero"}
It is a true story, told in many companies with different numbers. An engineer means to fix one price, types
`UPDATE trips SET fare_paise = 0`, presses Enter, and forgets the `WHERE`. Postgres answers `UPDATE 480`. Every
trip, every route, every day: free. The next twenty minutes are the longest of that engineer's year.

Changing data takes three commands, and they are not hard: `INSERT` adds rows, `UPDATE` changes them, `DELETE`
removes them. What takes care is the **habit** around them: look before you change, change exactly the rows you
looked at, and know how to see what you changed. This chapter builds that habit.

:::mission
Put a new trip on sale, and raise one operator's fares on exactly the trips the announcement covers.
:::
:::

:::step{type=concept title="INSERT: adding rows"}
`INSERT INTO` names a table and its columns, then gives the values in the same order:

```text
safar=# INSERT INTO cities (id, name, state) VALUES (9, 'Mysuru', 'Karnataka');
INSERT 0 1
```

`INSERT 0 1` means one row was inserted (the 0 is a leftover from older Postgres versions; ignore it). Several rows
can go in one statement, and `RETURNING` shows what was stored:

```text
safar=# INSERT INTO cities (id, name, state)
safar-# VALUES (10, 'Belagavi', 'Karnataka'), (11, 'Nashik', 'Maharashtra') RETURNING *;
 id |   name   |    state
----+----------+-------------
 10 | Belagavi | Karnataka
 11 | Nashik   | Maharashtra
(2 rows)

INSERT 0 2
```

Always list the columns, even when you give every one: if someone adds a column to the table next year, an
`INSERT` without a column list breaks, and one with a list keeps working. Every rule from chapter 9 applies: a
duplicate id, a missing `NOT NULL` value or an unknown city is refused, and nothing is stored.

**Check yourself:** what do you expect from inserting `(9, 'Mysuru', 'Karnataka')` a second time? (A duplicate key
error: `id` 9 is the primary key, and it is taken.)
:::

:::step{type=example title="Worked example: look, change, look again"}
`UPDATE` changes columns in the rows that match its `WHERE`. The habit that keeps you safe has three steps. Bus 4
has been refitted as a 40-seat AC seater. First, **look** at exactly the rows you mean to change, with a `SELECT`
using the same `WHERE`:

```text
safar=# SELECT id, operator, kind, seats FROM buses WHERE id = 4;
 id |   operator   |     kind      | seats
----+--------------+---------------+-------
  4 | Deccan Rides | non-AC seater |    45
(1 row)
```

One row, the right one. Second, **change**, with the very same `WHERE`:

```text
safar=# UPDATE buses SET kind = 'AC seater', seats = 40 WHERE id = 4;
UPDATE 1
```

`SET` lists each column and its new value, separated by commas. `UPDATE 1` is the number of rows changed: compare
it with what you saw. Third, **look again**:

```text
safar=# SELECT id, operator, kind, seats FROM buses WHERE id = 4;
 id |   operator   |   kind    | seats
----+--------------+-----------+-------
  4 | Deccan Rides | AC seater |    40
(1 row)
```

A new value can be computed from the old one. Route 13's fares go up by Rs 20 from 25 November; first the count
(6 trips), then the change with `RETURNING` to see every new value at once:

```text
safar=# UPDATE trips SET fare_paise = fare_paise + 2000
safar-# WHERE route_id = 13 AND departs_at >= '2026-11-25' RETURNING id, fare_paise;
 id  | fare_paise
-----+------------
 397 |      40500
 413 |      40500
 429 |      40500
 445 |      40500
 461 |      40500
 477 |      40500
(6 rows)

UPDATE 6
```

Six counted, six changed. `fare_paise = fare_paise + 2000` reads each row's current fare and adds 2,000 paise.
:::

:::step{type=predict title="Guess first"}
:::question
You run `UPDATE trips SET fare_paise = 0`, with no `WHERE`. What does Postgres do?
:::
- [ ] It refuses, because a WHERE is required
- [ ] It asks you to confirm
- [x] It sets every trip's fare to 0, at once, and says `UPDATE 480`
:::explain
No `WHERE` means every row. SQL does exactly what it is told, with no "are you sure?". The next step shows the
safety net: a transaction you can roll back.
:::
:::

:::step{type=try title="The missing WHERE, with a safety net"}
Let's make the famous mistake, safely. `BEGIN` starts a **transaction**: until you say `COMMIT`, nobody else can
see your changes, and `ROLLBACK` undoes them all. In psql:

```text
safar=# BEGIN;
BEGIN
safar=*# UPDATE trips SET fare_paise = 0;
UPDATE 480
safar=*# SELECT COUNT(*) FROM trips WHERE fare_paise = 0;
 count
-------
   480
(1 row)
```

Every trip is free (the `*` in the prompt means a transaction is open). Now undo it:

```text
safar=*# ROLLBACK;
ROLLBACK
safar=# SELECT COUNT(*) FROM trips WHERE fare_paise = 0;
 count
-------
     0
(1 row)
```

As if it never happened. That is the professional habit for any change you are not completely sure of: `BEGIN`,
change, look at the result, then `COMMIT` if it is right or `ROLLBACK` if it is not. Chapter 11 is all about
transactions; for now, this one trick is a seat belt.
:::

:::step{type=task task=add_trip title="Your turn: a new trip on sale"}
Safar is extending into December. In `10-changing-data/add_trip.sql`, put **trip 481** on sale:

| id | route_id | bus_id | departs_at | fare_paise |
|---|---|---|---|---|
| 481 | 1 | 1 | 1 December 2026, 09:00 | 33000 |

Write the timestamp as `'2026-12-01 09:00'`. Run it with `psql -f add_trip.sql`, look at the row, and press
**Check**.
:::

:::step{type=concept title="DELETE, and when not to"}
`DELETE FROM` removes the rows that match its `WHERE`:

```text
safar=# DELETE FROM cities WHERE id IN (10, 11);
DELETE 2
```

Everything about `UPDATE` applies, doubled: a `DELETE` without `WHERE` empties the table. Look first, use the same
`WHERE`, count, and use a transaction when in doubt.

Foreign keys protect you here too. Deleting a city that routes still point at is refused:

```text
safar=# DELETE FROM cities WHERE id = 1;
ERROR:  update or delete on table "cities" violates foreign key constraint "routes_from_city_id_fkey" on table "routes"
DETAIL:  Key (id)=(1) is still referenced from table "routes".
```

Pune cannot vanish while routes start there.

And often, the right answer is **not to delete at all**. A cancelled booking is kept, with `status = 'cancelled'`,
so the refund, the customer's history and the monthly report still add up. This is called a **soft delete**: mark
it, do not destroy it. Real deletion is for data that should truly no longer exist, such as personal data a
customer asks you to erase.
:::

:::step{type=task task=raise_fares title="Your turn: Konkan Lines raises its fares"}
Konkan Lines announced a **10% fare rise on route 7** (Mumbai to Panaji), for trips leaving **on or after 20 November
2026**. Earlier trips keep their fares, and no other route changes.

In `10-changing-data/raise_fares.sql`, write the `UPDATE`. Follow the habit: first a `SELECT` with your `WHERE` to
see how many trips it covers, then the `UPDATE` with the same `WHERE`. To add 10% to a whole number of paise, use
`fare_paise * 110 / 100`. Press **Check**: it looks at every trip's fare, on every route.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`SELECT COUNT(*) ... WHERE x` says 6, then `UPDATE ... WHERE x` says `UPDATE 480`. What should you do?
:::
- [ ] Nothing, Postgres knows best
- [x] Stop: the WHERE clauses differ. If you used BEGIN, roll back; if not, restore the rows
- [ ] Run the UPDATE again
:::explain
The count is your check. A different number means the UPDATE did not touch the rows you looked at. Inside a
transaction, `ROLLBACK` makes it as if nothing happened.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A customer cancels a booking. Why does Safar set `status = 'cancelled'` instead of deleting the row?
:::
- [ ] Deleting is slower
- [x] The booking is still a real event: refunds, history and reports need it
- [ ] Postgres cannot delete bookings
:::explain
A soft delete keeps the record and changes its meaning. Totals that count only confirmed bookings filter on
status, as you have done since chapter 2.
:::
:::

:::step{type=deep-dive title="Go deeper: upserts, and changing many rows at once"}
**Insert or update: ON CONFLICT.** "Add this city, or if the id exists, update its name" is one statement in
Postgres: `INSERT INTO cities (id, name, state) VALUES (9, 'Mysore', 'Karnataka') ON CONFLICT (id) DO UPDATE SET
name = EXCLUDED.name`. `EXCLUDED` is the row you tried to insert. `DO NOTHING` skips duplicates quietly.

**UPDATE with a join.** To change rows based on another table: `UPDATE trips t SET fare_paise = fare_paise + 1000
FROM buses b WHERE b.id = t.bus_id AND b.kind = 'AC sleeper'`.

**Big changes in batches.** Updating ten million rows in one statement locks them all and writes a huge amount of
log at once. Teams change big tables in batches of, say, 10,000 rows, in a loop, so other work keeps flowing.

**Backups are the last safety net.** Transactions protect a change while it happens. For mistakes noticed later,
production databases keep backups and a continuous log, so they can be restored to any moment, for example one
minute before the missing `WHERE`.
:::

:::step{type=recap}
You can now:

- add rows with `INSERT INTO ... (columns) VALUES ...`, and see them with `RETURNING`;
- change rows with `UPDATE ... SET ... WHERE`, including values computed from the old ones;
- follow the habit: look with a `SELECT`, change with the same `WHERE`, compare the counts, look again;
- try a risky change inside `BEGIN` and undo it with `ROLLBACK`, and prefer a soft delete to `DELETE`.

Next, chapter 11: transactions, all or nothing.

:::photo{src="/lesson-images/sql/sql-10-notes.webp" alt="Handwritten notes about changing data: INSERT INTO t (cols) VALUES; UPDATE ... SET ... WHERE; look, change, look again; no WHERE = every row!; soft delete: mark, keep" ai="true"}
One page of notes for this chapter.
:::
:::
