:::step{type=story title="Konkan Lines changes its name"}
A letter arrives at Safar: Konkan Lines has merged with another company and will be called "Konkan Coastal Lines"
from Monday. A simple change, surely. But the name is not stored once. It is typed out on every one of the
operator's buses, in the `buses` table:

```text
safar=# SELECT id, operator, kind FROM buses WHERE operator = 'Konkan Lines';
 id |   operator   |     kind
----+--------------+---------------
  5 | Konkan Lines | AC seater
  6 | Konkan Lines | AC sleeper
 13 | Konkan Lines | non-AC seater
(3 rows)
```

Three rows to change today. In a bigger company, three thousand, and the day someone updates most of them but not
all, Safar has two operators that are really one, and every total per operator is quietly wrong.

This is a **design** problem, not a query problem, and it has a well-known cure: store each fact in **one place**,
and point at it from everywhere else. This chapter teaches that idea, called **normalisation**, and you will apply it
to Safar's real tables.

:::mission
Give bus operators their own table, and make every bus point at its operator by id.
:::
:::

:::step{type=concept title="One fact, one place"}
Look at why `cities` was designed the way it was in chapter 1. A route does not say "Pune"; it says
`from_city_id = 1`, and the name lives once, in `cities`. Rename Pune in one row, and every route, every report and
every screen sees the change.

The operator's name breaks that rule: it is a fact about the **operator**, stored on every **bus**. That repetition
causes three classic problems, called **anomalies**:

| Anomaly | What goes wrong in Safar |
|---|---|
| Update anomaly | renaming Konkan Lines means changing every one of its buses, and missing one splits it in two |
| Insert anomaly | a new operator signed this week, with no buses yet, has nowhere to be stored |
| Delete anomaly | removing an operator's last bus erases the operator itself, and its contact details with it |

The fix is always the same shape: a table for the thing (`operators`), with an id, and an **id column** wherever
the thing is used (`buses.operator_id`), protected by a foreign key.

Here is the rule of thumb behind normalisation, which database people put in formal steps ("normal forms"): **every
column in a table should describe that table's thing, the whole thing, and nothing but that thing.** `kind` and
`seats` describe a bus. The operator's name describes an operator, so it belongs in the operator's table.

**Check yourself:** a `trips` table with a `route_distance_km` column on every trip: is that one fact in one place?
(No: the distance is a fact about the route, so it belongs in `routes`, where it already is.)
:::

:::step{type=example title="Worked example: bus kinds get their own table"}
`kind` is repeated on every bus too, so here is the full move on that column (an example only: you will undo it
at the end). It takes four steps.

**1. Make the new table**, with an id and a unique name:

```text
safar=# CREATE TABLE bus_kinds (id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY, name text NOT NULL UNIQUE);
CREATE TABLE
```

**2. Fill it** from the values that exist today, each once, straight from a query:

```text
safar=# INSERT INTO bus_kinds (name) SELECT DISTINCT kind FROM buses ORDER BY kind RETURNING *;
 id |     name
----+---------------
  1 | AC seater
  2 | AC sleeper
  3 | non-AC seater
(3 rows)

INSERT 0 3
```

`INSERT ... SELECT` inserts the rows a query returns, instead of typed values.

**3. Point at it.** Add the id column with its foreign key, then fill it in by matching names, with an `UPDATE`
that reads from a second table (`FROM bus_kinds k`):

```text
safar=# ALTER TABLE buses ADD COLUMN kind_id integer REFERENCES bus_kinds(id);
ALTER TABLE
safar=# UPDATE buses b SET kind_id = k.id FROM bus_kinds k WHERE k.name = b.kind;
UPDATE 16
```

Sixteen buses, sixteen rows updated.

**4. Check, then lock it in.** No bus may be left without a kind:

```text
safar=# SELECT COUNT(*) FROM buses WHERE kind_id IS NULL;
 count
-------
     0
(1 row)

safar=# ALTER TABLE buses ALTER COLUMN kind_id SET NOT NULL;
ALTER TABLE
```

Now renaming a kind is one row: `UPDATE bus_kinds SET name = 'AC sleeper (2+1)' WHERE name = 'AC sleeper'`
answered `UPDATE 1`, and all seven AC sleepers saw it. In a real migration, the old text column would be dropped
once every program reads the new one. To undo this example: `ALTER TABLE buses DROP COLUMN kind_id; DROP TABLE
bus_kinds;`.
:::

:::step{type=predict title="Guess first"}
:::question
After the move, a program inserts a bus with `kind_id = 9`, and there is no kind 9. What happens?
:::
- [ ] The bus is stored with an unknown kind
- [x] It is refused by the foreign key
- [ ] Postgres creates kind 9
:::explain
The foreign key from chapter 9 does the guarding: a bus can only point at a kind that exists. With a text column,
a typo like `'AC sleepr'` would have been stored without a word.
:::
:::

:::step{type=task task=operators_table title="Your turn: an operators table"}
In `13-designing-tables/operators.sql`, create a table called `operators` with an `id` the database fills in (the
primary key) and a `name` that is required and **unique**. Fill it with every operator name that appears in `buses`,
each once.

Run it with `psql -f operators.sql` and look at the table: five operators. Press **Check**.
:::

:::step{type=task task=buses_operator_id title="Your turn: buses point at their operator"}
In `13-designing-tables/operator_id.sql`, finish the move, the way the worked example did for kinds:

1. Add an `operator_id` column to `buses` that references `operators`.
2. Fill it in for every bus, by matching the operator's name.
3. Check that no bus is left without one, then make the column `NOT NULL`.

(Keep the old `operator` text column for now; the check uses it to compare.) Press **Check**.
:::

:::step{type=concept title="Do not split too far"}
Normalisation is a tool, not a religion. Two honest warnings.

**Not every repeated value is a problem.** `status` repeats `'confirmed'` on ten thousand bookings, but
`'confirmed'` is not a thing with its own facts (no address, no contact person, no name that might change). A short
fixed set of values is fine as text, ideally with a `CHECK (status IN ('confirmed', 'cancelled'))`.

**Some copies are deliberate.** A booking stores `amount_paise`, even though the trip has a fare. That is not a
mistake: the fare can change later (you raised fares in chapter 10), but what this passenger **paid** must never
change. A value that records what was true **at a moment** belongs on the record of that moment.

Analytics systems go further and deliberately keep wide, repeated tables (called **denormalised**), because they are
read billions of times and almost never updated. Apps that take bookings, like Safar, keep their working tables
normalised, because they are updated all day and must never contradict themselves.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A `passengers` table has columns `city_name` and `city_state`. What is the better design?
:::
- [ ] Keep both, they are useful
- [x] A `city_id` pointing at `cities`, where each city's name and state live once
- [ ] Put the city and state in one text column
:::explain
The state is a fact about the city, not the passenger. Store it once in `cities`, as Safar does, and point at it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does `bookings` keep its own `amount_paise` instead of always reading the trip's current fare?
:::
- [ ] It is a design mistake
- [x] The fare can change later, but what the passenger paid must not; the booking records a moment
- [ ] Reading the fare would need a join
:::explain
Copies that record history are deliberate. Normalise facts that should be the same everywhere; keep snapshots of
facts that must not change after the event.
:::
:::

:::step{type=deep-dive title="Go deeper: normal forms, and changing a live database"}
**The normal forms.** First normal form: one value per cell (no "Pune, Mumbai, Goa" in one column; that is a separate
table of rows). Second and third: every column depends on the key, the whole key, and nothing but the key, the rule
of thumb from this chapter. Beyond third normal form there are more, but most real designs stop at the third.

**Migrations.** In a real app the four steps of the worked example ship as a **migration**: a versioned script the
deploy runs once, recorded in a table so it never runs twice (tools such as Flyway, Liquibase and Alembic do this;
LabBox's own Spring Boot course uses Flyway). Big tables are migrated in small, safe steps: add the column, fill it
in batches, switch the code, add `NOT NULL`, and only later drop the old column.

**Views.** If old reports still expect `buses.operator` as text, a **view** can keep that shape while the data is
normalised underneath: `CREATE VIEW bus_list AS SELECT b.id, o.name AS operator, ... FROM buses b JOIN operators o ON
o.id = b.operator_id`. A view is a saved query that you can select from like a table.
:::

:::step{type=recap}
You can now:

- spot repeated facts, and name the update, insert and delete anomalies they cause;
- move a repeated value into its own table: create, fill with `INSERT ... SELECT`, point with a foreign key, fill with
  `UPDATE ... FROM`, and lock in with `NOT NULL`;
- tell a harmful repeat from a harmless one (a fixed set of values) and from a deliberate snapshot (what was paid);
- explain why booking apps keep normalised tables.

Next, chapter 14, the capstone: November's report, from everything you have learned.

:::photo{src="/lesson-images/sql/sql-13-notes.webp" alt="Handwritten notes about designing tables: one fact, one place; repeated name? own table + id; INSERT ... SELECT DISTINCT; UPDATE ... FROM to fill ids; snapshots: what was paid" ai="true"}
One page of notes for this chapter.
:::
:::
