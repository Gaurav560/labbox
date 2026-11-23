# Book Point: wallets and orders

You are connected to the database already: `psql` needs no arguments.

- Chapter 1: tables `wallets` and `ledger`. Write the `transfer` function in `transfer.sql`, then load
  it with `psql -f transfer.sql`.
- Chapter 2: table `orders`. Checkout runs `UPDATE orders SET status = 'paid' WHERE id = ...`.
