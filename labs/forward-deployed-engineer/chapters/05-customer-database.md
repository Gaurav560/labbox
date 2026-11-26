:::step{type=story title="Read access, and a warning"}
The export tells you about claims. To decide a claim, Claimdesk also needs the **policy**: who is insured, which vehicle,
from when to when, for how much, and the **deductible** (the part of every claim the customer pays themselves, Rs 1,000
for a two-wheeler at Deccan Shield).

Policies live in Deccan Shield's database. After a week of forms, their IT team gives you a read-only copy to build
against, in your project as `data/policies.db`, with a warning from the database administrator, Rahul: "Read-only.
Parameterised queries only. The last vendor's code let a customer's name break a report."

In this chapter you ask the database two questions Claimdesk needs every day: "which policy is behind this claim?" and
"which claims arrived after their policy had ended?". You will also see, for real, what Rahul was warning about.

:::mission
Join claims to policies in SQL, safely, with the claim id passed as a parameter, and find the claims on lapsed policies
in one query.
:::
:::

:::step{type=concept title="Two tables, joined by a key" file="05-customer-database/db.py" line="6-10"}
The database has two **tables** (a table is a grid of rows and named columns):

| Table | One row is | Columns |
|---|---|---|
| `policies` | an insurance policy | `policy_no`, `holder`, `vehicle_reg`, `vehicle`, `start_date`, `end_date`, `sum_insured`, `deductible` |
| `claims` | a claim | `claim_id`, `policy_no`, `received_at`, `amount_rs`, `status` |

The claim does not repeat the policy's details. It stores only `policy_no`, a **key** that points to one row in
`policies`. To see a claim with its policy, you **join** the tables on that key:

```sql
SELECT p.*
FROM claims c
JOIN policies p ON p.policy_no = c.policy_no
WHERE c.claim_id = 'DS-26-10038';
```

- `claims c` and `policies p` give each table a short name (an **alias**).
- `JOIN ... ON` matches each claim to the policy whose `policy_no` equals the claim's.
- `p.*` means every column of the policy.
- `WHERE` keeps only the claim you asked for.

The `connect` function (lines 6 to 10) opens the file with `mode=ro`, **read-only**. Claimdesk reads the customer's
records; it never changes them. We tried a write to be sure:

```text
OperationalError: attempt to write a readonly database
```

That is the database itself refusing, not just a promise in your code.
:::

:::step{type=history title="SQL, and the night it learned to lie"}
:::before{title="Before: programs that walked the files"}
Before relational databases, programs read data by following the physical structure of files and pointers, written
for each question. A new question meant new code.
:::

In 1970, Edgar F. Codd, a mathematician at IBM, described the **relational model**: data as tables, and questions asked
by describing the result you want. Libraries had worked with the same idea for a century: a drawer of index cards,
each card pointing to where the real thing lives. A card is a row; the call number on it is a key; walking from the
card to the shelf is a join.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-card-catalog.webp" alt="Long rows of wooden cabinets with many small drawers of index cards in a library room, one drawer pulled out." credit="Michael Holley (Swtpc6800)" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Copyright_Card_Catalog_Files.jpg"}
The copyright card catalogue at the Library of Congress, Washington DC: millions of records, each pointing elsewhere.
:::

Codd's tables made that idea mathematical. IBM researchers Donald Chamberlin and Raymond Boyce then designed a language for
those questions, first called SEQUEL, later **SQL**. It is still how most of the world's business data is queried.

The danger arrived with the web. On 25 December 1998, a security researcher writing as "rain.forest.puppy" (Jeff
Forristal) described in the magazine *Phrack* how text typed into a web form could change the SQL a program built from
it. This became known as **SQL injection**. It is still in the OWASP Top Ten list of the most critical web application
security risks.

:::solved
Send values to the database separately from the SQL text (parameters), so a value can never become a command.
:::

:::timeline
- **1970** Codd publishes the relational model.
- **1974** Chamberlin and Boyce describe SEQUEL, which becomes SQL.
- **1998** SQL injection is described publicly in Phrack.
- **2007** The comic xkcd 327 makes "Bobby Tables" the most famous example.
:::

:::funfact
In xkcd 327, "Exploits of a Mom", a school's database is wiped because a student is named
`Robert'); DROP TABLE Students;--`. His mother calls him "little Bobby Tables".
:::
:::

:::step{type=example title="Worked example: a parameter is always data"}
This is only to read; it is not in your project. The wrong way and the right way, with the standard library's `sqlite3`:

```python
# WRONG: the value becomes part of the SQL text
sql = f"SELECT * FROM books WHERE title = '{title}'"
con.execute(sql)

# RIGHT: a placeholder, and the value passed separately
con.execute("SELECT * FROM books WHERE title = ?", (title,))
```

- In the wrong version, Python builds one string. Whatever `title` contains, quotes included, becomes SQL.
- In the right version, `?` is a **placeholder**. The database receives the SQL and the value separately, and treats
  the value as data, never as SQL, whatever characters it has.
- The values go in a tuple: `(title,)`. The comma makes it a one-item tuple; `(title)` is just `title` in brackets.

Reading results:

```python
row = con.execute("SELECT * FROM books WHERE id = ?", (7,)).fetchone()
print(dict(row) if row else None)
```

`fetchone()` gives the first row or `None`. With `row_factory = sqlite3.Row` (set in `connect`), `dict(row)` turns it
into a dictionary of column names to values.
:::

:::step{type=predict title="Guess first"}
:::question
A query is built with an f-string: `... WHERE c.claim_id = '{claim_id}'`. Someone sends the claim id
`DS-26-99999' OR '1'='1`. Claim DS-26-99999 does not exist. What comes back?
:::
- [ ] Nothing, because the claim does not exist
- [x] A real customer's policy
- [ ] An error
:::explain
The quote in the id closes the text early, and `OR '1'='1'` is true for every row. See it for real in the next step.
:::
:::

:::step{type=try title="What the last vendor's bug looked like"}
We built the query the wrong way, in the lab image, with that claim id:

```text
SELECT p.policy_no, p.holder FROM claims c JOIN policies p ON p.policy_no = c.policy_no WHERE c.claim_id = 'DS-26-99999' OR '1'='1'
{'policy_no': 'DS-POL-40000', 'holder': 'M. Joshi'}
240 rows
```

Read the SQL that was really sent: the `WHERE` now says "this claim, **or** one equals one". One always equals one, so
every row matches: **240 rows**, and the first is M. Joshi's policy, shown to someone who asked about a claim that does
not exist. In Claimdesk, claim ids arrive inside customers' emails, so this is not theoretical.

Now run your starter:

```text
$ python db.py
None
None
claims on a lapsed policy: 0
```

Nothing yet. Write it the right way.
:::

:::step{type=task task=policy_for_claim title="Your turn: the policy behind a claim"}
In `policy_for_claim` in `db.py`:

1. Write one query: `SELECT p.* FROM claims c JOIN policies p ON p.policy_no = c.policy_no WHERE c.claim_id = ?`.
2. Run it with `con.execute(sql, (claim_id,))` and take `.fetchone()`.
3. Return `dict(row)`, or `None` when there is no row.

The check asks for a real claim, an unknown claim, and the sneaky id from the last step. Press **Check**.
:::

:::step{type=concept title="Asking the database to compare" file="05-customer-database/db.py" line="21-25"}
A claim is only covered if it happened while the policy was in force: on or before its `end_date`. A claim that
arrives after the end date is on a **lapsed** policy, and an adjuster must look at it before anything is paid.

You could load every row into Python and compare there. For 240 rows that works; for Deccan Shield's real database of
several hundred thousand policies, it means moving all of them across the network to throw most away. Let the database
do the comparison, and send you only the answer.

One detail. `received_at` holds a date **and** a time (`2026-09-20 11:15`), while `end_date` is a date (`2026-09-08`).
Compared as text, `"2026-09-08 10:00"` is always later than `"2026-09-08"`, so a claim received on the very last day
would look lapsed. Take only the date part with `substr`:

```sql
substr(c.received_at, 1, 10)
```

`substr(text, start, length)` takes 10 characters from the first one: `2026-09-20`. ISO dates compare correctly as text
(chapter 4), so `substr(c.received_at, 1, 10) > p.end_date` is the test.

Return each row as a tuple `(claim_id, end_date, received_day)`, sorted by claim id with `ORDER BY`, so the result is
the same every time.
:::

:::step{type=task task=lapsed_claims title="Your turn: claims on lapsed policies"}
In `lapsed_claims`:

1. Join claims to policies as before.
2. Select `c.claim_id`, `p.end_date` and `substr(c.received_at, 1, 10) AS received_day`.
3. Keep the rows where the received day is later than the end date, `ORDER BY c.claim_id`.
4. Return `[tuple(r) for r in rows]`.

Press **Check**.
:::

:::step{type=try title="Six claims a human must see first"}
```text
$ python db.py
{'policy_no': 'DS-POL-40000', 'holder': 'M. Joshi', 'vehicle_reg': 'MH12EB4010', 'vehicle': 'two-wheeler', 'start_date': '2026-04-27', 'end_date': '2027-04-26', 'sum_insured': 90000, 'deductible': 1000}
None
claims on a lapsed policy: 6
   ('DS-26-10088', '2026-09-08', '2026-09-20')
   ('DS-26-10100', '2026-06-14', '2026-08-07')
   ('DS-26-10120', '2026-08-19', '2026-09-07')
   ('DS-26-10210', '2026-06-16', '2026-07-06')
   ('DS-26-10220', '2026-06-18', '2026-07-20')
   ('DS-26-10222', '2026-07-12', '2026-08-24')
```

Six claims arrived after their policies ended. DS-26-10100 came almost two months late. Some of these may still be
honest (an accident on the last day, reported later); that is the adjuster's call, not Claimdesk's. What Claimdesk can
do is put them in front of a person every time, which you will build in chapter 19.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why pass the claim id as `(claim_id,)` with a `?` in the SQL, instead of an f-string?
:::
- [ ] It is faster to type
- [x] The database then treats the value as data only, so quotes in it can never change the query
- [ ] f-strings do not work with SQLite
:::explain
f-strings work, and that is the problem: they build SQL from whatever text arrives. Placeholders keep data and SQL
apart.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why compare `substr(c.received_at, 1, 10)` with `end_date`, instead of `c.received_at`?
:::
- [x] received_at has a time too, so as text it is always "later" than a plain date on the same day
- [ ] substr makes the query faster
- [ ] end_date is stored as a number
:::explain
`"2026-09-08 10:00" > "2026-09-08"` is true. Taking the first 10 characters compares day with day.
:::
:::

:::step{type=deep-dive title="Go deeper: databases at a customer"}
**Least privilege.** Ask for a database user that can only read the tables you need. FDEs who ask for less access get
it sooner, and cannot break what they cannot touch.

**Replicas and copies.** Never run heavy analysis on the production database that serves the customer's staff. Use a
read replica or a copy, as Deccan Shield did here.

**ORMs.** Larger apps often use SQLAlchemy or a similar library, which builds parameterised SQL for you. Know the SQL
underneath anyway: every customer database is different, and the slow query in production is always a SQL question.

**Indexes.** A `WHERE c.claim_id = ?` is fast because `claim_id` is a primary key, which the database indexes. A filter
on a column without an index reads the whole table. Ask the customer's DBA before adding one.
:::

:::step{type=recap}
You can now:

- read a customer's database read-only, and see the database refuse a write;
- join two tables on a key to answer a real question;
- explain SQL injection with a real example, and prevent it with parameters;
- push comparisons into the database, comparing dates as dates.

Next, chapter 6: not everything has a database you can query. Deccan Shield's policy system is fourteen years old, it
answers in XML, and at month end it is busy.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-05-notes.webp" alt="Handwritten notes about the customer's database: Open the customer's database read-only. A JOIN links each claim to its policy. Pass values as parameters, never in the SQL. Injection turned one fake id into 240 rows. Compare the date part with the end date. Six claims came after their policy ended." ai="true"}
One page of notes for this chapter.
:::
:::
