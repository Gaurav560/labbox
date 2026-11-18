:::step{type=story title="The analyst just quit"}
:::character{name="Meera" role="CTO, Tapri Counter"}
Our analyst left on Friday, and every Monday the outlet managers ask me the same questions.
The answers are all in the order database. You do not need a dashboard, you need SQL.
:::

:::mission
Ask the database for exactly the rows you need, and count them.
:::
:::

:::step{type=concept title="SELECT, FROM, WHERE"}
A query names the columns you want, the table they live in, and which rows to keep:

```sql
SELECT id, item
FROM orders
WHERE outlet_id = 1 AND status = 'paid'
ORDER BY id;
```

Text goes in single quotes. `ORDER BY` sorts the result; without it, the order is not guaranteed.
`COUNT(*)` counts rows instead of listing them.
:::

:::step{type=predict title="Guess first"}
:::question
What does `SELECT COUNT(*) FROM orders WHERE item = 'Masala Chai'` return, when the data says `'masala chai'`?
:::
- [ ] The number of masala chai orders
- [x] `0`
- [ ] An error
:::explain
Text comparison with `=` is exact, including capital letters. No row equals `'Masala Chai'`, so the
count is 0. That is a quiet wrong answer, the worst kind.
:::
:::

:::step{type=try title="Look at the data"}
Your terminal is connected to the database. Peek at a few orders:

```bash run
psql -c "SELECT * FROM orders ORDER BY id LIMIT 5"
```

`\d orders` inside `psql` shows every column and its type.
:::

:::step{type=task task=q_paid_chai title="Paid masala chai at outlet 3"}
In `q1.sql`, list the `id` and `qty` of every **paid** `'masala chai'` order at **outlet 3**, sorted by `id`.
Run your file with `psql -f q1.sql` to see what it returns.
:::

:::step{type=task task=q_count_refunds title="How many refunds"}
In `q2.sql`, return how many orders have the status `'refunded'`, as one column named `refunds`.
:::

:::step{type=recap}
- `SELECT` picks columns, `FROM` the table, `WHERE` the rows.
- Text comparisons are exact; quote text with single quotes.
- `ORDER BY` makes the order certain; `COUNT(*)` counts the rows that are left.
:::
