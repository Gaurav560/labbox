:::step{type=story title="Money that vanishes"}
:::character{name="Kabir" role="Backend lead, Book Point"}
Customers can send loyalty money to friends. This week Sana's wallet went to minus 25 rupees, and
one transfer took money from Asha and gave it to nobody: the app crashed halfway. Money must never
appear, vanish, or go below zero. The database can promise that; the app cannot.
:::

:::mission
Make negative balances impossible, and write a transfer that either fully happens or not at all.
:::
:::

:::step{type=concept title="Transactions and constraints"}
A **transaction** groups statements so they succeed or fail together:

```sql
BEGIN;
UPDATE wallets SET balance_paise = balance_paise - 500 WHERE customer_id = 1;
UPDATE wallets SET balance_paise = balance_paise + 500 WHERE customer_id = 2;
COMMIT;   -- or ROLLBACK to undo both
```

If anything fails before `COMMIT`, nothing is saved. A **function** always runs inside one
transaction, so an error anywhere in it undoes all its changes.

A **CHECK constraint** is a rule the database enforces on every write, whatever the app does:
a statement that breaks it fails with an error.
:::

:::step{type=predict title="Guess first"}
:::question
`UPDATE wallets SET balance_paise = 0 WHERE customer_id = 999` and there is no customer 999. What happens?
:::
- [ ] An error: customer 999 does not exist
- [x] Nothing: `UPDATE 0`, and no error
- [ ] Postgres creates customer 999
:::explain
An UPDATE that matches no rows is not an error; it just changes zero rows. In a function you
must check `FOUND` yourself, or a transfer to a typo customer makes money disappear.
:::
:::

:::step{type=try title="Look at the wallets"}
```bash run
psql -c "SELECT * FROM wallets ORDER BY customer_id"
```

```bash run
psql -c "BEGIN; UPDATE wallets SET balance_paise = 0 WHERE customer_id = 1; SELECT * FROM wallets WHERE customer_id = 1; ROLLBACK;" -c "SELECT * FROM wallets WHERE customer_id = 1"
```

Inside the transaction Asha has 0; after `ROLLBACK` her money is back.
:::

:::step{type=task task=no_negative title="No wallet below zero"}
Fix the wallet that is already negative by setting it to **0**, then make the database **refuse any
negative balance** from now on. Do not delete wallets.
:::

:::step{type=task task=atomic_transfer title="An all-or-nothing transfer"}
Write `transfer(from, to, amount)` in `transfer.sql` and load it with `psql -f transfer.sql`:

- take `amount` from `from`'s wallet and add it to `to`'s wallet;
- add one row to `ledger` (`from_customer`, `to_customer`, `amount_paise`);
- if the sender has too little money, or either wallet does not exist, **raise an error and change nothing**.

```bash
psql -c "SELECT transfer(3, 2, 1500)" -c "SELECT * FROM ledger"
```
:::

:::step{type=recap}
- A transaction is all or nothing: `BEGIN`, then `COMMIT` or `ROLLBACK`.
- A function runs in one transaction; raising an error undoes everything it did.
- `CHECK` constraints make the database enforce rules, even against buggy apps.
- An UPDATE that matches nothing is not an error: check `FOUND`.
:::
