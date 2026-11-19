:::step{type=story title="Checkout is frozen"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Pager again. Paying for order 42 just spins forever, and more orders are piling up behind it.
Postgres is up, the CPU is idle, nothing is slow. Everything is just... waiting.
:::

:::mission
Find what is holding the lock, end it, and make sure a forgotten transaction can never freeze checkout again.
:::
:::

:::step{type=concept title="Locks and waiting"}
When a transaction **updates a row**, it locks that row until it ends with `COMMIT` or `ROLLBACK`.
Any other transaction that wants to change the same row **waits**.

That is how Postgres keeps two payments from overwriting each other. But if a session runs `BEGIN`,
updates a row, and then just sits there, its state is **idle in transaction**, and everyone who
needs that row waits forever.

`pg_stat_activity` shows every session (its `pid`, `state`, last `query`, `application_name`), and
`pg_blocking_pids(pid)` tells you which sessions a waiting session is stuck behind.
:::

:::step{type=predict title="Guess first"}
:::question
A session ran `BEGIN; UPDATE orders ... WHERE id = 42;` and then its program froze. When is the lock on order 42 released?
:::
- [ ] After the UPDATE finishes
- [ ] After a few seconds, automatically
- [x] Only when that transaction commits, rolls back, or its session ends
:::explain
Row locks are held until the end of the transaction. A frozen client that never commits keeps the
lock until someone ends its session, or a timeout does.
:::
:::

:::step{type=try title="See it wait"}
This tries to pay order 42 but gives up after 3 seconds instead of hanging:

```bash run
psql -c "SET lock_timeout = '3s'" -c "UPDATE orders SET status = 'paid' WHERE id = 42"
```

Now look at who is connected:

```bash run
psql -c "SELECT pid, application_name, state, now() - xact_start AS open_for, query FROM pg_stat_activity WHERE datname = 'tapri'"
```
:::

:::step{type=incident task=kill_blocker minutes=10 title="Pager: checkout frozen"}
**Brew Point on-call.** Order 42 cannot be paid; the payment request waits forever.

Find the session that holds the lock and **end it**, from SQL. Do not delete the order.
:::

:::step{type=task task=idle_timeout title="Never again"}
Make Postgres end any session of the `tapri` database that sits **idle inside a transaction** for
more than a minute (anything from 1 second to 5 minutes passes).
:::

:::step{type=deep-dive title="Deadlocks"}
Two transactions can also wait on **each other**: A locks row 1 then wants row 2, while B locks
row 2 then wants row 1. Neither can go on. Postgres notices this within a second
(`deadlock_timeout`), kills one of them with a `deadlock detected` error, and the other continues.

The fix is in the app: always lock rows in the **same order** (for example, lowest id first), and
keep transactions short.
:::

:::step{type=recap}
- An updated row stays locked until its transaction ends.
- `idle in transaction` sessions are the classic cause of "everything is waiting".
- `pg_stat_activity` and `pg_blocking_pids` find the blocker; `pg_terminate_backend(pid)` ends it.
- `idle_in_transaction_session_timeout` and `lock_timeout` are your safety nets.
:::
