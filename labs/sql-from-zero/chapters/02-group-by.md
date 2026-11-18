:::step{type=story title="Totals per outlet"}
:::character{name="Meera" role="CTO, Tapri Counter"}
The board meets on Thursday. They want two numbers: how much each outlet really earned, and what
our best seller is. Refunds do not count as earnings.
:::

:::mission
Join outlets to their orders, and add up money and plates per group.
:::
:::

:::step{type=concept title="JOIN and GROUP BY"}
Outlet names are in `outlets`, money is in `orders`. A **JOIN** puts matching rows side by side:

```sql
SELECT o.name, r.amount_paise
FROM orders r
JOIN outlets o ON o.id = r.outlet_id;
```

**GROUP BY** squashes rows with the same value into one, and functions like `SUM` and `COUNT`
work per group: `SELECT item, SUM(qty) FROM orders GROUP BY item`.
:::

:::step{type=predict title="Guess first"}
:::question
`SELECT item, qty FROM orders GROUP BY item` gives an error. Why?
:::
- [ ] `qty` is a reserved word
- [x] Each group has many qty values, and the query does not say how to combine them
- [ ] GROUP BY needs ORDER BY
:::explain
After grouping, a column must either be in the GROUP BY or be inside a function like `SUM(qty)`,
so Postgres knows which single value to show for the group.
:::
:::

:::step{type=try title="Group something"}
Count orders per status:

```bash run
psql -c "SELECT status, COUNT(*) FROM orders GROUP BY status"
```
:::

:::step{type=task task=q_revenue_by_outlet title="Paid revenue per outlet"}
In `q3.sql`, return each outlet's `name` and its paid revenue as `revenue_paise`, biggest first.
Only `'paid'` orders count.
:::

:::step{type=task task=q_top_item title="The best seller"}
In `q4.sql`, return the one item with the most `qty` sold in paid orders: one row with `item` and `qty`.

:::tip
"Most sold" means the total quantity, not the number of orders. A table of 4 samosas is one order.
:::
:::

:::step{type=recap}
- `JOIN ... ON` puts matching rows from two tables side by side.
- `GROUP BY` makes one row per group; `SUM` and `COUNT` work per group.
- Every selected column is either grouped or inside a function.
:::
