:::step{type=story title="Where does an app keep 12,000 bookings?"}
Open a bus booking app and search for Pune to Mumbai tomorrow. In less than a second it shows you every trip, the
seats left on each, the fare, and maybe the seat you picked last time. Somewhere, a program found those answers
among millions of facts: cities, routes, buses, trips, passengers, bookings.

Where are those facts kept, so that thousands of people can search and book **at the same time** without two of
them getting the same seat, and so that nothing is lost when a server restarts? The answer, for almost every app
you have ever used, is a **database**, and the language you use to talk to it is **SQL**.

In this course you will look after the data of **Safar**, a bus ticket booking app that runs buses between Pune,
Mumbai, Goa, Bengaluru and four more cities. Its database is real, running next to you, with 480 trips and
12,005 bookings from November 2026. You will learn to ask it any question, change it safely, and make it fast.

Safar's trips run on long-distance coaches like this one, a Shivneri of the Maharashtra state bus company on the Pune to Mumbai road. Every seat on it is a row in a table somewhere.

:::photo{src="/lesson-images/sql/shivneri-bus.webp" alt="A light blue long-distance Volvo coach with large tinted windows, parked on a concrete bus stand" credit="Rsrikanth05" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:MSRTC-Shivneri-Volvo-B7R.jpg"}
An MSRTC Shivneri coach, which runs between Pune and Mumbai.
:::

:::mission
Meet the database, look around its tables, and ask your first two questions in SQL.
:::
:::

:::step{type=concept title="Tables, rows and columns"}
A **relational database** keeps data in **tables**. A table is like a sheet in a spreadsheet, with one strict
difference: every row has exactly the same columns, and every column holds one kind of value. Here is Safar's
`cities` table, all of it:

```text
 id |   name    |    state
----+-----------+-------------
  1 | Pune      | Maharashtra
  2 | Mumbai    | Maharashtra
  3 | Nagpur    | Maharashtra
  4 | Kolhapur  | Maharashtra
  5 | Panaji    | Goa
  6 | Bengaluru | Karnataka
  7 | Hyderabad | Telangana
  8 | Chennai   | Tamil Nadu
```

- A **row** is one thing: one city.
- A **column** is one fact about every row: its `id`, its `name`, its `state`. Each column has a **type**:
  `id` holds whole numbers, `name` holds text.
- The **primary key**, here `id`, is a value that is different for every row, so each row can be found and
  pointed at without confusion. Two cities could share a name; they can never share an id.

Tables point at each other through those ids. A route does not repeat "Pune" and "Mumbai"; it stores
`from_city_id = 1` and `to_city_id = 2`. That is why it is called **relational**: the tables are related by
their keys, and you combine them when you ask a question (chapter 5).

Safar has six tables: `cities`, `routes` (from one city to another, with a distance), `buses` (each with an
operator, a kind and a number of seats), `trips` (one bus on one route at one time, with a fare), `passengers`,
and `bookings` (one passenger, one seat, on one trip).

**Check yourself:** why does `routes` store city ids instead of city names? (So each city's name lives in one
place: rename it once in `cities`, and every route sees the change.)
:::

:::step{type=history title="The story of SQL and Postgres"}
SQL is more than fifty years old, and it is still the most widely used language for data in the world.

:::before{title="Before relational databases"}
In the 1960s every program kept its data in its own files, in its own format. To find "all bookings for
Tuesday", a programmer wrote a program that walked the file record by record, following pointers from one record
to the next. Early database systems, such as IBM's IMS (built in the late 1960s for the parts lists of the Apollo
moon programme), worked the same way: you had to know **how** the data was stored to get anything out. Change the
storage, and every program that read it broke.
:::

In June 1970 **Edgar F. Codd**, a mathematician at IBM's research lab in San Jose, published a paper called "A
Relational Model of Data for Large Shared Data Banks". His idea: keep data in simple tables, and let people ask
for **what** they want, not **how** to find it. The database itself works out the how.

:::solved
**Ask for what, not how.** With a relational database you describe the answer you want, in one language, and
the database decides how to find it, using indexes and plans it chooses itself. Programs keep working when the
storage changes, and one database can be shared safely by many programs at once.
:::

At IBM, **Donald Chamberlin** and **Raymond Boyce** turned Codd's idea into a language you could type, called
**SEQUEL** (1974). Its name was later shortened to **SQL**, because "SEQUEL" was already a trademark. Meanwhile,
at the University of California, Berkeley, **Michael Stonebraker** built Ingres, and in 1986 started its
successor, **Postgres** ("post-Ingres"). It gained SQL in 1994 and was renamed **PostgreSQL** in 1996.

This is Don Chamberlin, standing beside an exhibit about SQL, the language he designed with Raymond Boyce.

:::photo{src="/lesson-images/sql/don-chamberlin.webp" alt="Don Chamberlin in a dark suit with a flower in his lapel, standing next to a museum panel with his own picture on it" credit="Dicklyon" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Don_Chamberlin.jpg"}
Don Chamberlin, co-designer of SQL.
:::

:::timeline
- **1970** Edgar F. Codd publishes the relational model at IBM.
- **1974** Chamberlin and Boyce describe SEQUEL, later SQL.
- **1979** Oracle ships the first commercial SQL database.
- **1986** SQL becomes an ANSI standard; Stonebraker starts Postgres at Berkeley.
- **1996** PostgreSQL gets its name and its open-source community.
:::

Today PostgreSQL is developed by the **PostgreSQL Global Development Group**, a worldwide community of volunteers
and companies, under a free open-source licence. Codd received the Turing Award, computing's highest prize, in
1981; Stonebraker received it in 2014.

And this is Michael Stonebraker, whose Ingres and Postgres projects at Berkeley led to the database you are using in this course.

:::photo{src="/lesson-images/sql/michael-stonebraker.webp" alt="Michael Stonebraker, smiling, with glasses and grey hair, in a red shirt" credit="Dcoetzee" license="CC0" source="https://commons.wikimedia.org/wiki/File:Michael_Stonebraker_2.jpg"}
Michael Stonebraker, creator of Ingres and Postgres.
:::

:::usedby{title="Used for"}
- Bookings and orders
- Banking and payments
- Online shops
- Maps and location data
- Analytics and reports
- Almost every web app
:::

:::usedby{title="Postgres is used at"}
- Instagram
- Reddit
- Twitch
- Skype
:::

:::funfact
People still argue about how to say it: "S-Q-L" or "sequel". Both are fine. The "sequel" pronunciation is a
leftover from the language's first name.
:::
:::

:::step{type=try title="Meet psql"}
Your terminal is already connected to Safar's database. `psql` is the terminal program for talking to Postgres.
Type `psql` on its own to open it; the prompt shows the database's name:

```text
safar=#
```

Inside psql, commands that start with a backslash are psql's own helpers, not SQL. `\dt` lists the tables:

```text
safar=# \dt
           List of relations
 Schema |    Name    | Type  |  Owner
--------+------------+-------+----------
 public | bookings   | table | postgres
 public | buses      | table | postgres
 public | cities     | table | postgres
 public | passengers | table | postgres
 public | routes     | table | postgres
 public | trips      | table | postgres
(6 rows)
```

`\d trips` describes one table: its columns, their types, its keys and how it points at other tables:

```text
safar=# \d trips
                           Table "public.trips"
   Column   |            Type             | Collation | Nullable | Default
------------+-----------------------------+-----------+----------+---------
 id         | integer                     |           | not null |
 route_id   | integer                     |           | not null |
 bus_id     | integer                     |           | not null |
 departs_at | timestamp without time zone |           | not null |
 fare_paise | integer                     |           | not null |
Indexes:
    "trips_pkey" PRIMARY KEY, btree (id)
Foreign-key constraints:
    "trips_bus_id_fkey" FOREIGN KEY (bus_id) REFERENCES buses(id)
    "trips_route_id_fkey" FOREIGN KEY (route_id) REFERENCES routes(id)
```

Read it: five columns; `departs_at` is a date and time; `fare_paise` is a whole number of paise (Rs 330 is
33000 paise, so no rounding trouble ever). The **foreign keys** say that `bus_id` must be the id of a real bus,
and `route_id` of a real route: the database refuses anything else.

`\q` leaves psql. Try `\d bookings` and `\d passengers` yourself.
:::

:::step{type=example title="Worked example: your first questions"}
A question in SQL is a **query**, and the simplest one asks for rows from a table. Here are the first three
trips (only to read; your task files come next):

```sql
SELECT * FROM trips ORDER BY id LIMIT 3;
```

```text
 id | route_id | bus_id |     departs_at      | fare_paise
----+----------+--------+---------------------+------------
  1 |        1 |      1 | 2026-11-01 09:00:00 |      33000
  2 |        2 |      2 | 2026-11-01 13:15:00 |      24000
  3 |        3 |      3 | 2026-11-01 21:30:00 |      50600
(3 rows)
```

Read it word by word:

1. `SELECT *`: give me columns. `*` means all of them.
2. `FROM trips`: from the `trips` table.
3. `ORDER BY id`: sorted by id. Without it, a database may return rows in any order it finds convenient.
4. `LIMIT 3`: only the first three.
5. `;` ends the statement. In psql, a query without it waits for more input.

A second question: how many bookings are there?

```sql
SELECT COUNT(*) FROM bookings;
```

```text
 count
-------
 12005
(1 row)
```

`COUNT(*)` counts rows instead of listing them. The answer is a tiny table: one column, one row. SQL keywords
are not case sensitive (`select count(*) from cities` works too), but writing them in capitals makes queries easier
to read.
:::

:::step{type=predict title="Guess first"}
:::question
`SELECT * FROM cities` returns 8 rows. What does `SELECT COUNT(*) FROM cities` return?
:::
- [ ] 8 rows, each with a count
- [x] One row with one column: 8
- [ ] The number of columns, 3
:::explain
`COUNT(*)` turns all the rows into one number. You get a result with one row and one column named `count`.
:::
:::

:::step{type=task task=count_cities title="Your turn: how many cities?"}
Open `01-why-databases/q1.sql`. Below the comment, write one query that returns **how many cities** Safar serves:
one number.

Run it from the chapter's folder to see what it returns:

```bash
cd /workspace/01-why-databases && psql -f q1.sql
```

Press **Check**: it runs your query and compares the answer.
:::

:::step{type=concept title="When the database says no"}
Sooner or later every query has a typo. Postgres does not just fail; it tells you where, and often what you
meant. Here is a misspelt column name:

```text
safar=# SELECT nmae FROM cities;
ERROR:  column "nmae" does not exist
LINE 1: SELECT nmae FROM cities
               ^
HINT:  Perhaps you meant to reference the column "cities.name".
```

Read an error in three parts:

1. **ERROR**: what went wrong. There is no column called `nmae`.
2. **LINE 1** and the `^`: where Postgres stopped understanding.
3. **HINT**: Postgres's guess at what you meant. Often exactly right.

An error changes nothing and costs nothing: fix the query and run it again. Every engineer who writes SQL sees
these every day.
:::

:::step{type=task task=first_trips title="Your turn: the first five trips"}
In `01-why-databases/q2.sql`, write one query that returns the **first five trips by id**: only the columns `id`
and `departs_at`, lowest id first.

Run it with `psql -f q2.sql`, then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does Safar store `fare_paise` as a whole number of paise instead of rupees with decimals?
:::
- [ ] Postgres cannot store decimals
- [x] Whole numbers add up exactly; money with decimal fractions can pick up tiny rounding errors
- [ ] Paise use less memory
:::explain
Postgres can store exact decimals too (`numeric`), but counting money in its smallest unit is a simple habit that
avoids rounding trouble everywhere: in the database, in Python, in JavaScript.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A query without `ORDER BY` returns trips in id order today. Can you rely on that order tomorrow?
:::
- [ ] Yes, rows always come back in the order they were added
- [x] No: without `ORDER BY`, the database may return rows in any order
- [ ] Only if the table is small
:::explain
The order of rows is not part of the answer unless you ask for it. After updates, or with a different plan, it
can change. If the order matters, say `ORDER BY`.
:::
:::

:::step{type=deep-dive title="Go deeper: why not just a spreadsheet?"}
A spreadsheet is a table too, so why does every app use a database?

**Many people at once.** A database lets thousands of programs read and write the same data at the same moment,
and makes sure two bookings never take the same seat (chapter 11).

**Rules it enforces.** A spreadsheet cell can hold anything. A database refuses a trip for a bus that does not
exist, a missing fare, or a duplicate id (chapter 9). Bad data is stopped at the door.

**It survives crashes.** Postgres writes every change to a log on disk before saying "done", so a crash or a power
cut never leaves half a booking behind.

**Size and speed.** A spreadsheet slows down at a few hundred thousand rows. A database handles billions, and with
indexes (chapter 12) finds one row among them in a fraction of a millisecond.

**One language.** SQL works, with small differences, on Postgres, MySQL, SQLite, SQL Server, Oracle and many
analytics tools. What you learn here works almost everywhere.
:::

:::step{type=recap}
You can now:

- explain tables, rows, columns, primary keys and foreign keys;
- tell the story of SQL: Codd's relational model, SEQUEL at IBM, and Stonebraker's Postgres;
- explore a database in psql with `\dt` and `\d`;
- write your first queries with `SELECT`, `FROM`, `ORDER BY`, `LIMIT` and `COUNT(*)`, and read an error.

Next, chapter 2: asking for exactly the rows you need, with `WHERE`.

:::photo{src="/lesson-images/sql/sql-01-notes.webp" alt="Handwritten notes about why databases?: a table = rows and columns; primary key: each row's own id; foreign key: points at another table; SQL: say what, not how; Codd 1970, Postgres 1986" ai="true"}
One page of notes for this chapter.
:::
:::
