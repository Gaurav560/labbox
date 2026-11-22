:::step{type=story title="Which seats on trip 42 are taken?"}
A customer calls Safar's helpline: "I want to sit near my friend on trip 42. Which seats are already taken?"
The answer is somewhere among 12,005 bookings. Listing all of them and scrolling would take all day.

What you need is a way to say **which rows** you want: only bookings, only on trip 42, only the confirmed ones.
That is the `WHERE` clause, and it is the part of SQL you will write more than any other. By the end of this
chapter you can pick any rows you like out of a table, and you will know the three small traps that catch nearly
everyone in their first week.

Indian Railways has answered this question on paper for decades. A few hours before a train leaves, a reservation chart lists every booked berth, coach by coach, and passengers crowd around boards like this one to find their names. A WHERE clause prints exactly the part of the chart you need.

:::photo{src="/lesson-images/sql/reservation-chart.webp" alt="Passengers reading long printed reservation charts pinned to a board at a New Delhi railway station" credit="Bahnfrend" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Reservation_chart_board,_New_Delhi,_2008.JPG"}
A reservation chart board at a New Delhi station.
:::

:::mission
List the taken seats on trip 42, and count how many bookings were cancelled.
:::
:::

:::step{type=concept title="WHERE: keep only the rows you want"}
`WHERE` comes after `FROM` and holds a **condition**. The database checks the condition for every row, and keeps
only the rows where it is **true**:

```text
safar=# SELECT id, name FROM passengers WHERE id = 42;
 id |     name
----+---------------
 42 | Anjali Shaikh
(1 row)
```

Out of 2,000 passengers, one row: the one whose `id` equals 42. Conditions compare a column with a value:

| Operator | Means | Example |
|---|---|---|
| `=` | equal | `seats = 40` |
| `<>` | not equal (`!=` works too) | `kind <> 'AC sleeper'` |
| `<`, `>` | less, greater | `distance_km > 500` |
| `<=`, `>=` | less or equal, greater or equal | `seats >= 40` |

**Text goes in single quotes.** `'AC sleeper'` is a piece of text; without quotes, Postgres would think you meant
a column called that:

```text
safar=# SELECT id, operator, kind FROM buses WHERE kind = 'AC sleeper';
 id |     operator     |    kind
----+------------------+------------
  1 | Sahyadri Travels | AC sleeper
  3 | Deccan Rides     | AC sleeper
  6 | Konkan Lines     | AC sleeper
  9 | Kaveri Travels   | AC sleeper
 12 | Deccan Rides     | AC sleeper
 14 | Godavari Coaches | AC sleeper
 16 | Sahyadri Travels | AC sleeper
(7 rows)
```

Numbers need no quotes: `WHERE distance_km > 500`.

**Check yourself:** which rows does `WHERE seats >= 40` keep from a bus with 40 seats? (It keeps it: 40 is
greater than **or equal** to 40.)
:::

:::step{type=example title="Worked example: two conditions at once"}
Real questions have several conditions. `AND` keeps a row only if **both** sides are true; `OR` keeps it if
**either** is. Here are the cancelled seats on trip 7:

```sql
SELECT id, seat_no
FROM bookings
WHERE trip_id = 7 AND status = 'cancelled';
```

```text
 id  | seat_no
-----+---------
 159 |       4
 160 |       5
 166 |      11
 183 |      28
 184 |      29
 188 |      33
 189 |      34
 192 |      37
 194 |      39
 198 |      43
(10 rows)
```

1. `FROM bookings`: start with all 12,005 bookings.
2. `trip_id = 7`: keep those on trip 7.
3. `AND status = 'cancelled'`: of those, keep the cancelled ones.
4. `SELECT id, seat_no`: show just these two columns.

Notice the order the database "thinks" in: first **FROM** (which table), then **WHERE** (which rows), and only then
**SELECT** (which columns). You write `SELECT` first, but it happens last.

Two shortcuts for common shapes:

- `state IN ('Goa', 'Karnataka', 'Telangana')` means "equal to any of these", instead of three `OR`s. In Safar it
  gives Panaji, Bengaluru and Hyderabad.
- `distance_km BETWEEN 300 AND 500` means `distance_km >= 300 AND distance_km <= 500`, both ends included. It gives
  routes 5, 6, 13 and 14 (450 km and 350 km).
:::

:::step{type=predict title="Guess first"}
:::question
Every booking's status is stored in small letters: `'confirmed'` or `'cancelled'`. What does
`SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'` return?
:::
- [ ] 10,464, the number of confirmed bookings
- [x] 0
- [ ] An error
:::explain
Text comparison with `=` is exact, capital letters included. No row equals `'Confirmed'`, so the count is 0, with
no error at all. That is the most dangerous kind of mistake: a quiet wrong answer. When a count looks surprising,
look at the real values first (`SELECT DISTINCT status FROM bookings`, chapter 3).
:::
:::

:::step{type=try title="Two classic mistakes, on purpose"}
Make both mistakes yourself, now, so you recognise them forever. First, capital letters:

```text
safar=# SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed';
 count
-------
     0
(1 row)
```

Zero, and no warning. Second, forgetting the quotes:

```text
safar=# SELECT COUNT(*) FROM bookings WHERE status = confirmed;
ERROR:  column "confirmed" does not exist
LINE 1: SELECT COUNT(*) FROM bookings WHERE status = confirmed;
                                                     ^
```

Without quotes, `confirmed` looks like a column name, and there is no such column. At least this one shouts.
Now run it correctly, with `'confirmed'`, and see the real number.
:::

:::step{type=task task=q_paid_coffee title="Your turn: the taken seats on trip 42"}
Help the customer on the helpline. In `02-asking-for-rows/q1.sql`, list the `seat_no` and `passenger_id` of every
**confirmed** booking on **trip 42**, sorted by `seat_no`.

Run it with `psql -f q1.sql` from the chapter's folder, then press **Check**.
:::

:::step{type=concept title="AND before OR: the trap with brackets"}
Mixing `AND` and `OR` hides a trap. Suppose you want the short routes (under 300 km) that start **or** end in Pune
(city 1). Here is the obvious way to write it, and what it returned:

```text
safar=# SELECT id, from_city_id, to_city_id FROM routes
safar-#   WHERE from_city_id = 1 OR to_city_id = 1 AND distance_km < 300 ORDER BY id;
 id | from_city_id | to_city_id
----+--------------+------------
  1 |            1 |          2
  2 |            2 |          1
  3 |            1 |          4
  4 |            4 |          1
  5 |            1 |          5
  9 |            1 |          3
 11 |            1 |          7
 15 |            1 |          6
(8 rows)
```

Eight routes, including route 15, which is 840 km long. What happened? Like multiplication before addition in
arithmetic, **`AND` is worked out before `OR`**. Postgres read the condition as:

```text
from_city_id = 1  OR  (to_city_id = 1 AND distance_km < 300)
```

so every route **from** Pune came back, whatever its length. Brackets say what you mean:

```text
safar=# SELECT id, from_city_id, to_city_id FROM routes
safar-#   WHERE (from_city_id = 1 OR to_city_id = 1) AND distance_km < 300 ORDER BY id;
 id | from_city_id | to_city_id
----+--------------+------------
  1 |            1 |          2
  2 |            2 |          1
  3 |            1 |          4
  4 |            4 |          1
(4 rows)
```

The rule worth keeping: **whenever a condition mixes AND and OR, add brackets**, even when you think you do not
need them. The next person to read it will thank you.

(The `safar-#` prompt means psql is waiting for the rest of the query: a query can span several lines, and it
ends at the `;`.)
:::

:::step{type=task task=q_count_refunds title="Your turn: how many cancellations?"}
The operations team wants one number for their weekly report. In `02-asking-for-rows/q2.sql`, return **how many
bookings were cancelled**, as one column named `cancelled`.

To name a result column, write `AS` and the name after it: `SELECT COUNT(*) AS cancelled ...`. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which condition keeps the routes between 300 and 500 km, both included?
:::
- [ ] `distance_km > 300 AND distance_km < 500`
- [x] `distance_km BETWEEN 300 AND 500`
- [ ] `distance_km BETWEEN 300 OR 500`
:::explain
`BETWEEN` includes both ends. The first option would leave out a route of exactly 300 or 500 km.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `WHERE status = 'cancelled' OR status = 'confirmed' AND trip_id = 7` keep?
:::
- [ ] Cancelled and confirmed bookings on trip 7 only
- [x] Every cancelled booking on any trip, plus the confirmed ones on trip 7
- [ ] Nothing, because a status cannot be both
:::explain
`AND` binds first, so it reads `cancelled OR (confirmed AND trip 7)`. Brackets around the two statuses, or
`status IN ('cancelled', 'confirmed')`, say what was meant.
:::
:::

:::step{type=deep-dive title="Go deeper: how the database finds the rows"}
For a `WHERE` like `trip_id = 42`, Postgres has two main ways to find the rows.

**Read everything.** A **sequential scan** reads every row of the table and keeps the matching ones. For Safar's
12,005 bookings that takes about a millisecond. For a billion rows, it takes minutes.

**Look it up.** With an **index** on `trip_id`, Postgres jumps straight to the bookings of trip 42, like using the
index at the back of a book instead of reading every page. Chapter 12 builds one and measures the difference.

You never choose between them in your query: you say **what** you want, and Postgres's **planner** picks the
fastest way, using statistics it keeps about every table. That is Codd's idea from chapter 1, working every time
you press Enter. `EXPLAIN` in front of any query shows the plan it chose; try `EXPLAIN SELECT * FROM bookings
WHERE trip_id = 42;` now and look for "Seq Scan".
:::

:::step{type=recap}
You can now:

- keep only the rows you need with `WHERE`, using `=`, `<>`, `<`, `>`, `<=` and `>=`;
- quote text with single quotes, and remember that text comparison is exact;
- combine conditions with `AND`, `OR`, `IN` and `BETWEEN`, with brackets whenever AND and OR meet;
- name a result column with `AS`.

Next, chapter 3: putting results in order, keeping the top few, and shaping what comes back.

:::photo{src="/lesson-images/sql/sql-02-notes.webp" alt="Handwritten notes about asking for rows: SELECT columns FROM table; WHERE keeps matching rows; text in 'single quotes'; 'Confirmed' is not 'confirmed'; AND before OR: add brackets!" ai="true"}
One page of notes for this chapter.
:::
:::
