:::step{type=story title="A seat lost between two statements"}
Passenger 398 calls the helpline: "I booked trip 42, but I need to travel two days later instead. Same seat if
possible." Moving a booking is two changes: cancel the old booking, create the new one.

Now imagine the server crashes, or the new seat turns out to be taken, **between** those two statements. The old
booking is cancelled; the new one never happened. The passenger has paid and has no seat. Or do it the other way
round, and a failure leaves them holding **two** seats.

Some changes only make sense **together**. A database guarantees that with a **transaction**: a group of statements
that either all happen, or none do. Banks move money with them, shops take orders with them, and Safar moves
bookings with them. This chapter shows how they work, what they protect you from, and what other users see while
yours is still open.

:::mission
Move a passenger's booking to another trip as one transaction, and cancel a whole trip's bookings in one go.
:::
:::

:::step{type=concept title="BEGIN, COMMIT, ROLLBACK"}
A transaction starts with `BEGIN` and ends with one of two words:

- `COMMIT`: make every change permanent, all at once.
- `ROLLBACK`: throw every change away, as if none had happened.

```sql
BEGIN;
UPDATE bookings SET status = 'cancelled' WHERE id = 936;
INSERT INTO bookings (...) VALUES (...);
COMMIT;
```

Between `BEGIN` and `COMMIT`, the changes exist only for your session. If anything goes wrong in the middle (an
error, a crash, a lost connection), the database rolls the whole transaction back by itself. There is no state
where the first change happened and the second did not.

These promises have a famous name, **ACID**:

| Letter | Promise | In Safar |
|---|---|---|
| **A**tomic | all or nothing | a booking move is never half done |
| **C**onsistent | every rule (chapter 9) holds at the end | no seat is ever sold twice |
| **I**solated | others do not see your half-finished work | a seat map never shows a move halfway |
| **D**urable | once committed, it survives a crash | a confirmed booking is never lost |

In fact, every single statement you have run so far was a small transaction on its own: an `UPDATE` of 480 rows
either changes all 480 or none. `BEGIN` lets you put **several** statements into one.

The idea that a transfer must be written on both sides or not at all is older than computers. In 1494 Luca Pacioli, the friar in this painting, published the first printed description of double-entry bookkeeping: every movement of money is written twice, once where it leaves and once where it arrives, so the books always balance.

:::photo{src="/lesson-images/sql/luca-pacioli.webp" alt="A Renaissance painting of a friar in grey robes at a table with a book and geometry instruments, a young man standing beside him" credit="Jacopo de' Barbari" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Jacopo_de'_Barbari_(attributed_to)_Portrait_of_Luca_Pacioli_(1445_1517)_with_a_student_(Guidobaldo_da_Montefeltro)_(2).jpg"}
Luca Pacioli, painted around 1495.
:::

**Check yourself:** the server crashes after `UPDATE` but before `COMMIT`. After the restart, is booking 936
cancelled? (No: the transaction never committed, so its change was rolled back.)
:::

:::step{type=example title="Worked example: a failure in the middle"}
Here is a move that fails halfway, run as one psql script. The second statement uses a booking id that already
exists:

```text
BEGIN
UPDATE 1
ERROR:  duplicate key value violates unique constraint "bookings_pkey"
DETAIL:  Key (id)=(1) already exists.
ERROR:  current transaction is aborted, commands ignored until end of transaction block
ROLLBACK
  status
-----------
 confirmed
(1 row)
```

Line by line:

1. `BEGIN`: the transaction starts.
2. `UPDATE 1`: the old booking (940) is cancelled, but only inside this transaction.
3. The `INSERT` fails: booking id 1 is taken.
4. Postgres now marks the whole transaction as failed. The next statement, a `SELECT`, is not even run: "current
   transaction is aborted, commands ignored until end of transaction block". After an error, the only way forward
   is `ROLLBACK`.
5. `ROLLBACK`, and booking 940 is `confirmed` again. The half-move never happened.

Without the transaction, booking 940 would have stayed cancelled, with no new booking: the passenger's seat lost
between two statements.
:::

:::step{type=predict title="Guess first"}
:::question
Session A runs `BEGIN; UPDATE trips SET fare_paise = 99900 WHERE id = 5;` and has not committed yet. Session B
now reads trip 5's fare. What does B see?
:::
- [ ] 99900, the new fare
- [x] The old fare: A's change is invisible to others until A commits
- [ ] B waits until A finishes
:::explain
Isolation: uncommitted changes are private. In Postgres, a reader never waits for a writer; it sees the last
committed value. The next step shows it happening.
:::
:::

:::step{type=try title="Two sessions, one trip"}
This lab ran two sessions at once on trip 5, whose fare is 72000 paise. Session A:

```sql
BEGIN;
UPDATE trips SET fare_paise = 99900 WHERE id = 5;
SELECT pg_sleep(3);
COMMIT;
```

`pg_sleep(3)` just waits three seconds, to keep the transaction open. Session B read the fare one second after A
started, and again four seconds after:

```text
B at 1s:
72000
B at 4s:
99900
```

At one second, A had changed the fare but not committed, so B saw the old value, 72000. At four seconds, A had
committed, so B saw 99900. B never saw anything in between, and never had to wait.

Try it yourself with two terminals (the + button): open `psql` in each, run `BEGIN;` and an `UPDATE` in the first,
read the row in the second, then `COMMIT` in the first and read again. (Then put the fare back, or press Reset lab
when you are done with this chapter.)
:::

:::step{type=task task=move_booking title="Your turn: move a booking, all or nothing"}
Passenger 398 holds **booking 936** (trip 42, seat 1). Move them to **trip 74**, two days later on the same route,
**seat 1**, in `11-transactions/move_booking.sql`, as **one transaction**:

1. Cancel booking 936 (set its status to `'cancelled'`; do not delete it).
2. Insert a new booking: id `12006`, trip 74, passenger 398, seat 1, status `'confirmed'`, booked now (`now()`), and
   an amount equal to trip 74's fare. (You can look the fare up first, or take it with `INSERT ... SELECT ... FROM
   trips WHERE id = 74`.)

Wrap both in `BEGIN;` and `COMMIT;`. Run it with `psql -f move_booking.sql`, then press **Check**. If it fails
halfway, look: nothing changed. Fix the script and run it again.
:::

:::step{type=concept title="Many rows, one decision"}
A transaction does not need several tables to be useful. Sometimes it is one change across many rows that must
happen together, and a second change that depends on it.

Trip 100 has been called off by its operator: the bus broke down. Every booking on it must be cancelled (kept, for
the refunds). Picture that as one `UPDATE` on 38 rows: Postgres already makes a single statement all or nothing,
so no passenger is left half cancelled. In a real app the same transaction would also record a refund for each
booking and an announcement to send, and all of that should happen together or not at all.

Two habits make transactions safe in daily work:

- **Keep them short.** While a transaction holds changed rows, other writers that want those rows must wait. Do the
  slow work (calling a payment service, sending emails) outside it.
- **Look before COMMIT.** Inside the transaction, a `SELECT` shows your changes. If the numbers are wrong,
  `ROLLBACK` costs nothing.
:::

:::step{type=task task=refund_trip title="Your turn: the trip that was called off"}
In `11-transactions/refund_trip.sql`, cancel **every confirmed booking on trip 100**, in a transaction. Keep the rows
(status `'cancelled'`), and change nothing on any other trip.

Before you `COMMIT`, count the rows you are about to change. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Inside a transaction, the third of five statements fails. What happens to the first two?
:::
- [ ] They stay; only the failed one is undone
- [x] Nothing is kept: after an error the transaction can only be rolled back, and all its changes go
- [ ] They are committed automatically
:::explain
That is atomicity: the transaction is one unit. Postgres refuses further statements until you `ROLLBACK`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why should a transaction not call a slow payment service in the middle?
:::
- [ ] Transactions cannot run while a network call is open
- [x] Rows it changed stay locked meanwhile, so other writers wait for the whole slow call
- [ ] The payment would be rolled back too
:::explain
A transaction holds its locks until it ends. Keep transactions short: gather what you need first, then change the
data quickly and commit.
:::
:::

:::step{type=deep-dive title="Go deeper: isolation levels and locks"}
**How Postgres keeps readers and writers apart.** Postgres keeps old versions of changed rows for as long as
someone might need them (this is called MVCC, multi-version concurrency control). A reader sees a snapshot, and a
writer makes a new version. That is why session B never waited.

**Two writers, one row.** Two transactions updating the **same** row do wait: the second waits until the first
commits or rolls back, then works on the new version. `SELECT ... FOR UPDATE` takes that lock while reading, which
is how a booking app reserves a seat it is about to sell.

**Isolation levels.** The default, **Read Committed**, shows each statement the latest committed data. **Repeatable
Read** shows the whole transaction one snapshot. **Serializable** makes concurrent transactions behave as if they
ran one after another, refusing (with an error you retry) the rare ones that cannot. Stricter levels prevent
subtler anomalies, at the cost of more retries.

**Deadlocks.** If A waits for B's row while B waits for A's, Postgres notices within a second, cancels one of them
with a deadlock error, and the app retries. Touching rows in the same order everywhere prevents most deadlocks.
:::

:::step{type=recap}
You can now:

- group changes into one unit with `BEGIN` and `COMMIT`, and undo them with `ROLLBACK`;
- explain ACID: atomic, consistent, isolated, durable;
- recognise "current transaction is aborted" and recover with `ROLLBACK`;
- predict what other sessions see while your transaction is open, and keep transactions short.

That completes Part 3. Next, Part 4 starts with chapter 12: indexes, and making slow queries fast.

:::photo{src="/lesson-images/sql/sql-11-notes.webp" alt="Handwritten notes about transactions: BEGIN ... COMMIT; ROLLBACK undoes it all; ACID: all or nothing; error? ROLLBACK first; keep transactions short" ai="true"}
One page of notes for this chapter.
:::
:::
