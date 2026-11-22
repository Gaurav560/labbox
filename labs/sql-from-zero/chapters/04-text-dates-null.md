:::step{type=story title="Find every Patil, and every night bus"}
Two requests land on your desk on the same morning. The support team: "A Mr Patil called about a refund but did
not leave his first name. How many Patils do we have?" And the operations team: "Which trips leave at night on 15
November? We need to check the drivers' rest hours."

Neither is an exact match on a whole value. The first is about **part** of a text ("ends in Patil"). The second
is about **part** of a date and time ("on this day, after 9 pm"). And while you look at the passengers, you will
meet the strangest value in SQL: **NULL**, which means "unknown", and which breaks the rules you have learned so far
in a very particular way.

:::mission
Find the trips that leave after 9 pm on 15 November, and count the passengers who never gave an email address.
:::
:::

:::step{type=concept title="Text: patterns with LIKE"}
`=` compares whole values. To match **part** of a text, use `LIKE` with a pattern. In a pattern, `%` means "any
characters, any number of them, even none", and `_` means "exactly one character":

```text
safar=# SELECT id, name FROM passengers WHERE name LIKE 'Asha%' ORDER BY id LIMIT 4;
 id |    name
----+-------------
 20 | Asha Gupta
 40 | Asha Desai
 60 | Asha Sharma
 80 | Asha Gupta
(4 rows)
```

`'Asha%'` means "starts with Asha". `'%Patil'` would mean "ends with Patil", and `'%an%'` "contains an anywhere".

Like `=`, `LIKE` cares about capital letters. `ILIKE` (a Postgres extra; the I is for "insensitive") does not:

```text
safar=# SELECT COUNT(*) FROM passengers WHERE name LIKE '%patil';
 count
-------
     0
(1 row)

safar=# SELECT COUNT(*) FROM passengers WHERE name ILIKE '%patil';
 count
-------
   133
(1 row)
```

Postgres has many text functions too. `upper(name)` gives `PUNE`, `lower(...)` the opposite, `length(name)` counts
characters (4 for Pune), and `||` joins texts: `name || ', ' || state` gives `Pune, Maharashtra`.

**Check yourself:** which names does `LIKE '_avi%'` match? (Names whose second, third and fourth letters are
"avi", like Ravi: one character, then "avi", then anything.)
:::

:::step{type=example title="Worked example: dates and times"}
`departs_at` is a **timestamp**: a date and a time together, like `2026-11-01 21:30:00`. Postgres can take one
apart, shift it, and compare it:

```text
safar=# SELECT id, departs_at, departs_at::date AS day, extract(hour FROM departs_at) AS hour
safar-# FROM trips ORDER BY id LIMIT 3;
 id |     departs_at      |    day     | hour
----+---------------------+------------+------
  1 | 2026-11-01 09:00:00 | 2026-11-01 |    9
  2 | 2026-11-01 13:15:00 | 2026-11-01 |   13
  3 | 2026-11-01 21:30:00 | 2026-11-01 |   21
(3 rows)
```

1. `departs_at::date` **casts** (converts) the timestamp to just its date. `::` is Postgres's way of saying
   "turn this into that type".
2. `extract(hour FROM departs_at)` takes out one part: the hour. `day`, `month`, `dow` (day of the week) and
   others work the same way.

An **interval** is a length of time, and you can add it to a timestamp. A trip that leaves at 21:30 and takes
about nine hours:

```text
safar=# SELECT id, departs_at, departs_at + interval '9 hours' AS arrives_about FROM trips WHERE id = 15;
 id |     departs_at      |    arrives_about
----+---------------------+---------------------
 15 | 2026-11-01 21:30:00 | 2026-11-02 06:30:00
(1 row)
```

It crosses midnight into 2 November, and Postgres handles that for you. To compare, write a timestamp as text in
`'YYYY-MM-DD HH:MM'` form; Postgres turns it into a timestamp. The cleanest way to ask for "one day" is a range:
**from** the start of the day, **up to but not including** the next day:

```sql
WHERE departs_at >= '2026-11-15' AND departs_at < '2026-11-16'
```

That catches every moment of 15 November, from midnight to 23:59:59.999, and nothing of the 16th.
:::

:::step{type=predict title="Guess first"}
:::question
Some passengers never gave an email address, so their `email` is empty. What does
`SELECT COUNT(*) FROM passengers WHERE email = NULL` return?
:::
- [ ] The number of passengers without an email
- [x] 0
- [ ] An error
:::explain
Anything compared with NULL using `=` is not true, not even NULL itself. So no row passes the condition and the
count is 0, silently. The next step shows why, and the right way: `IS NULL`.
:::
:::

:::step{type=try title="Meet NULL"}
Look at four passengers. One of them has nothing in `email`:

```text
safar=# SELECT id, name, email FROM passengers WHERE id BETWEEN 5 AND 8 ORDER BY id;
 id |     name     |     email
----+--------------+----------------
  5 | Farhan Gupta | p5@example.com
  6 | Meera Nair   | p6@example.com
  7 | Ishaan Iyer  |
  8 | Kavya Pillai | p8@example.com
(4 rows)
```

Ishaan's email is **NULL**: not an empty text, not zero, but "no value; unknown". SQL treats unknown honestly: is
an unknown email equal to an unknown email? Nobody knows. So comparisons with NULL give neither true nor false, but
**unknown**, and `WHERE` keeps only rows where the condition is **true**:

```text
safar=# SELECT NULL = NULL AS equal, NULL IS NULL AS is_null, 1 + NULL AS sum;
 equal | is_null | sum
-------+---------+-----
       | t       |
(1 row)
```

`NULL = NULL` is unknown (shown as empty), and even `1 + NULL` is NULL: one plus an unknown number is unknown.
Only `IS NULL` (and `IS NOT NULL`) give a real answer: `t`, true. Try the wrong and the right way to count:

```text
safar=# SELECT COUNT(*) FROM passengers WHERE email = NULL;
 count
-------
     0
(1 row)
```

Now with `IS NULL` instead, and see the real number.
:::

:::step{type=task task=night_trips title="Your turn: the night buses of 15 November"}
Operations needs to check the drivers' rest hours. In `04-text-dates-null/q1.sql`, list every trip that leaves
**at 21:00 or later on 15 November 2026**: its `id` and `departs_at`, earliest first.

Use a range for "on 15 November, from 21:00": from `'2026-11-15 21:00'`, up to but not including the next day. Run
it, then press **Check**.
:::

:::step{type=concept title="Living with NULL: COUNT and COALESCE"}
NULL changes how some functions behave, and you need to know two of them.

**`COUNT(*)` counts rows; `COUNT(column)` counts values that are not NULL:**

```text
safar=# SELECT COUNT(*), COUNT(email) FROM passengers;
 count | count
-------+-------
  2000 |  1715
(1 row)
```

2,000 passengers, 1,715 emails. The difference is exactly the passengers without one. (`SUM` and `AVG` also skip
NULLs, which is usually what you want.)

**`COALESCE` replaces NULL with something you choose**: it returns the first of its arguments that is not NULL.
For a report that should never show a blank:

```text
safar=# SELECT id, name, COALESCE(email, '(no email)') AS email FROM passengers WHERE id BETWEEN 6 AND 8 ORDER BY id;
 id |     name     |     email
----+--------------+----------------
  6 | Meera Nair   | p6@example.com
  7 | Ishaan Iyer  | (no email)
  8 | Kavya Pillai | p8@example.com
(3 rows)
```

The rule to remember: **NULL means unknown, so test it with `IS NULL`, count around it with `COUNT(column)`, and
fill it in with `COALESCE`.** Where NULL is not allowed at all, the table says so: `NOT NULL` in `\d passengers` is
on every column except `email`. Chapter 9 shows how to set that rule yourself.
:::

:::step{type=task task=missing_emails title="Your turn: passengers without an email"}
The marketing team wants to know how many passengers they cannot email. In `04-text-dates-null/q2.sql`, return
**how many passengers have no email address**: one number.

Press **Check**. If you get 0, look at the previous step again.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which condition finds every trip on 1 November, whatever the time?
:::
- [ ] `departs_at = '2026-11-01'`
- [x] `departs_at >= '2026-11-01' AND departs_at < '2026-11-02'`
- [ ] `departs_at BETWEEN '2026-11-01' AND '2026-11-02'`
:::explain
`= '2026-11-01'` means exactly midnight, so it misses every real trip. `BETWEEN` includes the end, so it would also
catch a trip at exactly midnight on the 2nd. The half-open range is exactly one day.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A table has 100 rows; 30 of them have NULL in `phone`. What do `COUNT(*)` and `COUNT(phone)` return?
:::
- [ ] 100 and 100
- [x] 100 and 70
- [ ] 70 and 70
:::explain
`COUNT(*)` counts rows; `COUNT(phone)` counts the values that are there.
:::
:::

:::step{type=deep-dive title="Go deeper: time zones, and NULL's three-valued logic"}
**Time zones.** Safar's `departs_at` is a `timestamp` without a time zone: a wall-clock time in India. Apps that
serve several countries use `timestamptz` (timestamp with time zone): Postgres stores the moment in UTC and shows
it in each session's zone (`SET timezone = 'Asia/Kolkata'`). A rule many teams follow: store moments as
`timestamptz`, and convert to local time only when showing them.

**Three-valued logic.** With NULL, conditions have three possible results: true, false and unknown. `NOT unknown`
is still unknown, which is why `WHERE NOT (email = 'x')` also skips the NULL emails. `true OR unknown` is true
(one side is enough), but `true AND unknown` is unknown. When a query with NULLs surprises you, work through it
with these three values.

**Faster text search.** `LIKE 'Asha%'` (starts with) can use an index; `LIKE '%Patil'` (ends with) cannot, so
it reads every row. Postgres has full-text search and trigram indexes (the `pg_trgm` extension) for searching
inside text quickly.
:::

:::step{type=recap}
You can now:

- match part of a text with `LIKE` and `ILIKE`, and use `upper`, `lower`, `length` and `||`;
- take dates and times apart with `::date` and `extract`, add an `interval`, and ask for one day with a half-open range;
- explain NULL as "unknown", and test it with `IS NULL`, never `= NULL`;
- count around NULLs with `COUNT(column)`, and fill them in with `COALESCE`.

That completes Part 1. Next, Part 2 starts with chapter 5: joining tables together.

:::photo{src="/lesson-images/sql/sql-04-notes.webp" alt="Handwritten notes about text, dates and null: LIKE 'Asha%', ILIKE ignores case; one day: >= day AND < next day; NULL = unknown; IS NULL, never = NULL; COALESCE fills in a NULL" ai="true"}
One page of notes for this chapter.
:::
:::
