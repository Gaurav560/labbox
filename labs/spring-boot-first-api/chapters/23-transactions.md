:::step{type=story title="Why this chapter"}
Placing an order changes several rows: stock for each item, the order itself, perhaps a payment record.
If the application fails halfway, some of those changes must not stay. A **transaction** groups changes
so that they are saved together or not at all. This chapter shows how Spring manages transactions, and
one rule that surprises almost everyone.

:::mission
In the `23-transactions` folder: make placing an order all-or-nothing, and make a declined payment
undo the stock changes too.
:::
:::

:::step{type=concept title="What a transaction guarantees"}
A database **transaction** is a group of changes with these guarantees (often called ACID):

- **Atomic**: either every change is saved (commit) or none is (rollback).
- **Consistent**: constraints hold before and after.
- **Isolated**: other transactions do not see half-done changes.
- **Durable**: once committed, the changes survive a crash.

Without a transaction around them, each repository call commits on its own: a failure after the first
call leaves the first change in place.
:::

:::step{type=concept title="@Transactional"}
In Spring, a method marked `@Transactional` runs in one transaction:

```java
@Transactional
public void placeOrder(Map<String, Integer> items) { ... }
```

Spring starts a transaction before the method, **commits** when it returns normally, and **rolls back**
when it throws a `RuntimeException` (unchecked). It works through a proxy around the bean, so the method
must be `public` and called from another bean, not from inside the same class.

:::diagram{name="transaction-flow"}
One failure anywhere inside the method undoes every change made before it.
:::
:::

:::step{type=example title="Worked example: moving points between wallets"}
```java
@Transactional
public void transfer(long from, long to, int points) {
    Wallet a = wallets.findById(from).orElseThrow();
    Wallet b = wallets.findById(to).orElseThrow();
    a.withdraw(points);     // throws if not enough points
    b.deposit(points);
}
```

:::trace{title="transfer(1, 2, 500) when wallet 1 has 300"}
| step | wallet 1 | wallet 2 | note |
|---|---|---|---|
| transaction starts | 300 | 100 | Spring opens a transaction. |
| a.withdraw(500) | 300 | 100 | Not enough points: an exception is thrown. |
| rollback | 300 | 100 | Nothing was saved; both wallets are unchanged. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
`placeOrder` has no `@Transactional`. It saves the tea's new stock, then fails on the samosas. What is in the database?
:::
- [ ] Nothing changed
- [x] The tea stock is reduced; the samosas are not
- [ ] Both are reduced
:::explain
Each `save` commits by itself without a surrounding transaction. The tea change is already permanent
when the samosa check fails.
:::
:::

:::step{type=try title="Watch the stock"}
```bash run
cd 23-transactions && mvn -q -o package -DskipTests && java -jar target/transactions.jar
```

In a second tab:

```bash run
curl -s localhost:8080/stock/TEA-1; echo; curl -s localhost:8080/stock/SAM-1; echo
```
:::

:::step{type=task task=place_order_atomic title="Warm-up: all or nothing"}
In `23-transactions/.../OrderService.java`, make `placeOrder` run in one transaction, so that when an
item is out of stock, no stock changes at all.
:::

:::step{type=concept title="Checked exceptions do not roll back"}
By default, Spring rolls back only for **unchecked** exceptions (`RuntimeException`) and errors. A
**checked** exception (one declared with `throws`, such as `PaymentDeclinedException extends Exception`)
**commits** the transaction: Spring treats it as an expected outcome.

To roll back for a checked exception, say so:

```java
@Transactional(rollbackFor = PaymentDeclinedException.class)
```

This is one of the most common transaction bugs in Spring code: the method looks transactional, but a
declined payment still keeps the stock changes.
:::

:::step{type=task task=rollback_checked title="A declined card undoes the order"}
`placePaidOrder` is `@Transactional`, but `PaymentDeclinedException` is a checked exception, so a declined
card keeps the stock changes. Make it roll back for `PaymentDeclinedException` too.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A `@Transactional` method throws `IllegalStateException` (unchecked). What happens?
:::
- [x] Rollback
- [ ] Commit
- [ ] It depends on the database
:::explain
Unchecked exceptions roll back by default. Checked ones commit unless listed in `rollbackFor`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`OrderService.place()` calls `this.saveAll()`, which is `@Transactional` and in the same class. Is `saveAll` transactional?
:::
- [ ] Yes, always
- [x] No: a call inside the same object skips Spring's proxy, so the annotation has no effect
- [ ] Only if it is `private`
:::explain
Spring applies `@Transactional` through a proxy around the bean. Calls from outside go through it; a call
on `this` does not. Put the annotation on the method other beans call.
:::
:::

:::step{type=deep-dive title="Read-only transactions and propagation"}
`@Transactional(readOnly = true)` on query methods lets Hibernate skip change tracking, and some databases
route such work to replicas. **Propagation** decides what happens when one transactional method calls
another: the default `REQUIRED` joins the existing transaction, `REQUIRES_NEW` suspends it and starts a
separate one (useful for an audit log that must be saved even if the main work rolls back). Keep
transactions short: they hold database locks until they end, so never wait for a slow network call inside one.
:::

:::step{type=recap title="Chapter done"}
- A transaction saves all its changes together, or none of them.
- `@Transactional` commits on return and rolls back on unchecked exceptions.
- Checked exceptions commit by default: use `rollbackFor` when they must undo the work.
- It works through a proxy: public methods, called from another bean.
:::
