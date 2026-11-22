:::step{type=story title="Can a passenger give a trip 11 stars?"}
Welcome to Part 3. Until now you have only read Safar's data. From here on you change it, starting with the most
important change of all: making a new table, and deciding what may go into it.

Safar wants passengers to review their trips: one to five stars and an optional comment. You could make a table
that accepts anything. Then one day a bug in the app sends 11 stars, another sends a review for booking 99999999,
which does not exist, and a third sends a review with no stars at all. Every report built on that table quietly
becomes wrong.

A database can refuse bad data at the door, every time, whatever program sends it. The rules are called
**constraints**, and you write them once, when you create the table. This chapter teaches you to design a table
the way experienced engineers do: with the rules built in.

:::mission
Create the reviews table with every rule a review needs, and make it impossible to sell the same seat twice.
:::
:::

:::step{type=concept title="CREATE TABLE: columns and types"}
A table is created with `CREATE TABLE`, a name, and a list of columns. Each column has a name and a **type**,
which decides what kind of value it can hold:

| Type | Holds | Example |
|---|---|---|
| `integer` | whole numbers (up to about 2 billion) | `14`, `33000` |
| `bigint` | bigger whole numbers | ids of a huge table |
| `text` | text of any length | `'Suresh Pawar'` |
| `numeric(10, 2)` | exact decimals | `796.28` |
| `boolean` | true or false | `true` |
| `date` | a day | `'2026-11-22'` |
| `timestamp` | a day and a time | `'2026-11-22 21:30'` |

The type is already a first rule: `integer` refuses `'fourteen'`, `date` refuses `'2026-13-45'`. Choose the most
precise type that fits: a number stored as text cannot be added up or sorted properly.

The smallest useful table:

```sql
CREATE TABLE notes (
  id   integer,
  body text
);
```

It works, but it accepts anything: no id, the same id twice, an empty body. The rest of this chapter adds the
rules.
:::

:::step{type=example title="Worked example: a table of drivers, with every rule"}
Here is a table for Safar's bus drivers, with one rule of each kind. It is only an example (you will drop it at
the end):

```sql
CREATE TABLE drivers (
  id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name       text NOT NULL,
  licence_no text NOT NULL UNIQUE,
  bus_id     integer REFERENCES buses(id),
  years      integer CHECK (years >= 0),
  joined_on  date NOT NULL DEFAULT current_date
);
```

Read it rule by rule:

1. `GENERATED ALWAYS AS IDENTITY`: the database fills in the id itself, 1, 2, 3, and so on, so no two programs
   can ever pick the same one. `PRIMARY KEY`: unique and never empty.
2. `NOT NULL`: a driver must have a name.
3. `UNIQUE`: no two drivers can share a licence number.
4. `REFERENCES buses(id)`: a **foreign key**. `bus_id` must be a real bus (or empty, since it allows NULL here).
5. `CHECK (years >= 0)`: any condition you like; a row where it is false is refused.
6. `DEFAULT current_date`: when no value is given, use today's date.

Now a good row. `RETURNING *` makes the `INSERT` show the row it stored, defaults filled in:

```text
safar=# INSERT INTO drivers (name, licence_no, bus_id, years)
safar-# VALUES ('Suresh Pawar', 'MH12-2011-0042', 1, 14) RETURNING *;
 id |     name     |   licence_no   | bus_id | years | joined_on
----+--------------+----------------+--------+-------+------------
  1 | Suresh Pawar | MH12-2011-0042 |      1 |    14 | 2026-11-22
(1 row)
```

The id (1) and the date (today) were filled in by the database.
:::

:::step{type=try title="Break every rule, on purpose"}
Now try four bad drivers and watch each rule say no. Every refused `INSERT` changes nothing. A missing name:

```text
safar=# INSERT INTO drivers (licence_no, bus_id, years) VALUES ('MH14-2019-0007', 2, 6);
ERROR:  null value in column "name" of relation "drivers" violates not-null constraint
DETAIL:  Failing row contains (2, null, MH14-2019-0007, 2, 6, 2026-11-22).
```

A licence number that is already taken:

```text
safar=# INSERT INTO drivers (name, licence_no, bus_id, years) VALUES ('Imran Shaikh', 'MH12-2011-0042', 3, 9);
ERROR:  duplicate key value violates unique constraint "drivers_licence_no_key"
DETAIL:  Key (licence_no)=(MH12-2011-0042) already exists.
```

A bus that does not exist:

```text
safar=# INSERT INTO drivers (name, licence_no, bus_id, years) VALUES ('Lata Jadhav', 'GA07-2015-0110', 99, 8);
ERROR:  insert or update on table "drivers" violates foreign key constraint "drivers_bus_id_fkey"
DETAIL:  Key (bus_id)=(99) is not present in table "buses".
```

A negative number of years:

```text
safar=# INSERT INTO drivers (name, licence_no, bus_id, years) VALUES ('Lata Jadhav', 'GA07-2015-0110', 5, -2);
ERROR:  new row for relation "drivers" violates check constraint "drivers_years_check"
DETAIL:  Failing row contains (5, Lata Jadhav, GA07-2015-0110, 5, -2, 2026-11-22).
```

Each error names the rule that refused, and `DETAIL` shows the row that was refused. Notice one curious thing in the
last `DETAIL`: the id is 5. Every attempt took the next id, even the refused ones, so the next good driver will be
number 6, not 2. Gaps in identity ids are normal and harmless: an id is a name, not a count.

`\d drivers` lists every rule in one place. When you are done, remove the example with `DROP TABLE drivers;`.
`DROP` deletes a table and all its rows, with no undo, so read it twice before you press Enter.
:::

:::step{type=predict title="Guess first"}
:::question
`reviews` will have `stars integer NOT NULL CHECK (stars BETWEEN 1 AND 5)`. An app tries to save a review with
stars = 0. What happens?
:::
- [ ] It is saved, and a report shows a 0-star review
- [x] The `INSERT` is refused with a check constraint error, and nothing is saved
- [ ] It is saved with stars = 1
:::explain
The database never changes your data to make it fit; it refuses. The app gets an error and can tell the user.
:::
:::

:::step{type=task task=reviews_table title="Your turn: the reviews table"}
Write the `CREATE TABLE` for `reviews` in `09-tables-and-constraints/reviews.sql`, with these columns and rules:

| Column | Rules |
|---|---|
| `id` | a whole number the database fills in itself; the primary key |
| `booking_id` | a whole number; always there; must be a real booking |
| `stars` | a whole number; always there; from 1 to 5 |
| `comment` | text; optional |
| `created_at` | a timestamp; always there; the current time when not given (`now()`) |

Run it with `psql -f reviews.sql`. If you need to start again, `DROP TABLE reviews;` and run it again. Press
**Check**: it tries a good review and three bad ones, inside a transaction it throws away, so your table stays
empty.
:::

:::step{type=concept title="Rules for a table that already exists"}
Tables change as an app grows, so rules can be added later with `ALTER TABLE`:

```sql
ALTER TABLE drivers ADD COLUMN phone text;
ALTER TABLE drivers ADD CONSTRAINT phone_digits CHECK (phone ~ '^[0-9]{10}$');
```

The first adds a column (empty in every existing row). The second adds a named rule: `~` is a text pattern match,
here "exactly ten digits".

When you add a rule to a table that already has data, Postgres first checks **every existing row**. If any row
breaks the new rule, the whole `ALTER TABLE` is refused, and you must fix the data first. So before adding a rule,
look for the rows that would break it.

That matters for Safar's biggest risk: two passengers holding **the same seat on the same trip**. Today the app
avoids it by checking first ("is seat 1 free?"), but two requests that check at the same instant can both be told
yes, and both book.
The database can make it impossible, with a `UNIQUE` constraint on the **pair** of columns: a trip can have many
seats, a seat number appears on many trips, but each (trip, seat) pair may appear only once:

```sql
UNIQUE (trip_id, seat_no)
```

Before adding it, check that no pair is taken twice today:

```text
safar=# SELECT 1 FROM bookings GROUP BY trip_id, seat_no HAVING COUNT(*) > 1;
 ?column?
----------
(0 rows)
```

Zero rows: the data is clean, so the rule can be added.
:::

:::step{type=task task=one_seat_one_booking title="Your turn: one seat, one booking"}
In `09-tables-and-constraints/one_seat.sql`, add a constraint to the existing `bookings` table so that **no two
bookings can have the same `trip_id` and `seat_no`**. Give it a name you would understand in an error message, like
`one_booking_per_seat`.

Run it with `psql -f one_seat.sql`, then try to book seat 1 of trip 42 again yourself and read the error. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why let the database fill in ids (`GENERATED ALWAYS AS IDENTITY`) instead of the app choosing the next number?
:::
- [ ] Database ids are shorter
- [x] Two apps choosing "the highest id plus one" at the same moment can pick the same id; the database never does
- [ ] Apps cannot count
:::explain
"Read the highest, add one" is check-then-act again. An identity hands out each number once, even to many
programs at the same instant.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You add `CHECK (fare_paise > 0)` to `trips`, but one old trip has a fare of 0. What happens?
:::
- [ ] The rule is added and the old trip is deleted
- [x] The `ALTER TABLE` is refused until the bad row is fixed
- [ ] The rule is added but only applies to new rows
:::explain
Postgres checks every existing row when a rule is added, so the table can never hold data that breaks its own
rules. Fix the row, then add the rule.
:::
:::

:::step{type=deep-dive title="Go deeper: why rules belong in the database"}
**Apps change; the database stays.** Today one app writes bookings. Next year a second app, an admin tool, a data
import and a teammate's one-off script do too. A rule in one app's code protects only that app. A rule in the
database protects every path in.

**Constraints are documentation.** `\d reviews` tells a new teammate what a review is allowed to be, precisely, and
it can never go out of date.

**Partial unique rules.** Sometimes a rule should apply only to some rows: "a seat may be taken by at most one
**confirmed** booking" (cancelled ones do not count). Postgres does that with a unique index with a condition:
`CREATE UNIQUE INDEX ON bookings (trip_id, seat_no) WHERE status = 'confirmed'`.

**Deleting with foreign keys.** If a booking has reviews, Postgres refuses to delete the booking (the reviews would
point at nothing). `REFERENCES bookings(id) ON DELETE CASCADE` deletes the reviews with it; `ON DELETE SET NULL`
empties the column. The default, refusing, is the safest.
:::

:::step{type=recap}
You can now:

- create a table with fitting types, and let the database fill in ids and defaults;
- protect data with `NOT NULL`, `UNIQUE`, `PRIMARY KEY`, `REFERENCES` and `CHECK`, and read the errors they raise;
- add columns and rules to an existing table with `ALTER TABLE`, after checking the data first;
- make a pair of columns unique, so the database itself prevents double-selling a seat.

Next, chapter 10: adding, changing and deleting rows, safely.

:::photo{src="/lesson-images/sql/sql-09-notes.webp" alt="Handwritten notes about tables and constraints: NOT NULL, UNIQUE, CHECK; REFERENCES = a foreign key; IDENTITY fills in the id; DEFAULT now(); UNIQUE (trip_id, seat_no)" ai="true"}
One page of notes for this chapter.
:::
:::
