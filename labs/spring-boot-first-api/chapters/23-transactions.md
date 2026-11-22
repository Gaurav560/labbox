:::step{type=story title="All or nothing"}
Placing an order changes several rows: the stock of each item, then maybe a payment record, then the order
itself. Now imagine the third item turns out to be sold out, after the first two have already been taken off
the shelf. Or the card is declined after the stock has gone down. If the changes made so far stay in the
database, the shop's stock is now wrong: it says items are gone that were never sold.

Databases have a precise answer to this, built in for decades: the **transaction**. A group of changes that are
saved **together, or not at all**. Spring makes using one a single annotation, but with two rules that surprise
almost everyone. You will hit both in this chapter's project, on purpose.

:::mission
Make placing an order all-or-nothing, and make a declined card undo the stock changes too.
:::
:::

:::step{type=concept title="What a transaction guarantees"}
A **transaction** is a group of database changes that the database treats as one unit. It guarantees four
things, usually remembered as **ACID**:

- **Atomic**: either every change is saved (**commit**), or none is (**rollback**). Never half.
- **Consistent**: the database's rules (like the unique SKU from chapter 19) hold before and after.
- **Isolated**: other requests do not see your half-finished changes while the transaction runs.
- **Durable**: once committed, the changes survive even a crash a second later.

Atomic is the one this chapter is about. Without a transaction, **each statement is saved on its own**, the
moment it runs. So if a method runs three updates and the third fails, the first two are already permanent.
:::

:::step{type=try title="See the half-done order" file="23-transactions/src/main/java/com/shop/stock/OrderService.java" line="17-25"}
`OrderService.placeOrder`, on the right, loops over the ordered items. For each one it loads the stock, takes
the quantity (which throws `OutOfStockException` if there is not enough), and saves. The stock starts at: lassi
10, samosa **1**, coffee 5.

Start the app:

```bash run
cd 23-transactions && mvn -q -o package -DskipTests && java -jar target/transactions.jar
```

Now order 2 lassis and 5 samosas, then look at the lassi:

```bash run
curl -i -X POST localhost:8080/orders -H "Content-Type: application/json" -d '{"LAS-1": 2, "SAM-1": 5}'; echo; curl localhost:8080/stock/LAS-1
```

```text
HTTP/1.1 409
Not enough stock for SAM-1
{"quantity":8,"sku":"LAS-1"}
```

The order failed with 409, correctly. But the lassi stock is **8**. Two lassis left the shelf for an order that
never happened. Follow it step by step:

:::trace{title="placeOrder(lassi x2, samosa x5) without a transaction"}
| step | lassi in the database | samosa in the database | note |
|---|---|---|---|
| start | 10 | 1 | |
| take 2 lassi, save | 8 | 1 | saved immediately: a statement on its own is committed at once |
| take 5 samosa | 8 | 1 | only 1 left: OutOfStockException |
| the request fails | 8 | 1 | the lassi change is already permanent |
:::
:::

:::step{type=concept title="@Transactional"}
In Spring, you put a method in a transaction with one annotation:

```java
@Transactional
public void transfer(long from, long to, int points) {
    Wallet a = wallets.findById(from).orElseThrow();
    Wallet b = wallets.findById(to).orElseThrow();
    a.withdraw(points);      // throws if there are not enough points
    b.deposit(points);
}
```

When `transfer` is called, Spring:

1. **starts** a transaction, before the method's first line;
2. runs the method; every database change inside it belongs to the transaction;
3. if the method **returns normally**, **commits**: all the changes become permanent together;
4. if the method **throws a `RuntimeException`**, **rolls back**: the database undoes every change since the
   start, as if none had happened. The exception then continues on to the caller as usual.

Notice that `transfer` does not even call `save`. Inside a transaction, JPA **tracks the entities it loaded**,
and at commit it writes whatever changed. (That tracking is the persistence context from chapter 21.)

:::diagram{name="transaction-flow"}
One failure anywhere inside the method undoes every change made before it.
:::
:::

:::step{type=task task=place_order_atomic title="Your turn: all or nothing"}
In `OrderService`, make `placeOrder` run in **one transaction**. (`org.springframework.transaction.annotation.Transactional`.)

`OutOfStockException` extends `RuntimeException`, so it already triggers a rollback.

Rebuild, run (the stock resets at every start), and repeat the order:

```bash run
curl -i -X POST localhost:8080/orders -H "Content-Type: application/json" -d '{"LAS-1": 2, "SAM-1": 5}'; echo; curl localhost:8080/stock/LAS-1
```

Still `409`, and now the lassi stays at **10**. The lassi change was made, inside the transaction, then undone when
the samosas ran out. Press **Check**.
:::

:::step{type=concept title="The surprise: checked exceptions commit"}
Here is the first rule that surprises nearly everyone. Spring rolls back **only for unchecked exceptions**
(`RuntimeException` and its subclasses, and `Error`). For a **checked exception** (one that `extends Exception`
and must be declared with `throws`), Spring **commits** the transaction anyway.

Why? Historically, checked exceptions were meant for "expected business outcomes" that the caller handles, so
the work done so far was considered valid. In practice, it means a method can look transactional, throw, and
still keep its changes.

The fix is to say which checked exceptions should roll back:

```java
@Transactional(rollbackFor = InsufficientFundsException.class)
public void pay(...) throws InsufficientFundsException { ... }
```

`rollbackFor` lists exception classes that roll back too. (Some teams simply use `rollbackFor = Exception.class`
everywhere, to make every exception roll back.)
:::

:::step{type=example title="The declined card that keeps the stock"}
`placePaidOrder` in the project takes the stock, then charges the card. It is already `@Transactional`. But
`PaymentDeclinedException` is a **checked** exception (`extends Exception`). Watch:

```bash run
curl -i -X POST "localhost:8080/paid-orders?card=DECLINE-4242" -H "Content-Type: application/json" -d '{"COF-1": 1}'; echo; curl localhost:8080/stock/COF-1
```

```text
HTTP/1.1 402
Card DECLINE-4242 was declined
{"quantity":4,"sku":"COF-1"}
```

(`402 Payment Required` is the HTTP status for exactly this.) The card was declined, the customer pays nothing,
and yet the coffee stock went from 5 to 4. The transaction **committed**, because the exception was checked.
That is a real, common bug: in production it shows up as stock that slowly drifts away from reality.
:::

:::step{type=task task=rollback_checked title="Your turn: a declined card undoes the order"}
In `OrderService`, change the `@Transactional` on `placePaidOrder` so that **`PaymentDeclinedException` rolls the
transaction back** too.

Rebuild, run, and decline the card again: the coffee now stays at **5**. Press **Check**.
:::

:::step{type=concept title="The other surprise: calls inside the same class"}
The second rule. `@Transactional` works through a **proxy**: when Spring creates your `OrderService` bean, it
actually hands out a wrapper around it. When another bean calls `orders.placeOrder(...)`, the call goes through
the wrapper, which starts the transaction, calls your real method, then commits or rolls back.

But a call **from inside the same object** (`this.placeOrder(...)`, or just `placeOrder(...)` from another
method of `OrderService`) goes straight to the real method, **skipping the wrapper**. No wrapper, no
transaction, even though the annotation is right there.

```java
public void checkout(Map<String, Integer> items) {
    placeOrder(items);          // same class: @Transactional on placeOrder is IGNORED here
}
```

The fix: put `@Transactional` on the method that is called **from outside** (here, `checkout`), or move the
transactional method to another bean. And because of the proxy, `@Transactional` only works on **public**
methods called by other beans.

This is the same proxy mechanism behind other Spring annotations too (caching, security on methods). Once you
know it, the behaviour makes sense.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A `@Transactional` method throws `IllegalStateException`. What happens to its database changes?
:::
- [x] Rolled back
- [ ] Committed
- [ ] It depends on the database
:::explain
`IllegalStateException` is a `RuntimeException`: unchecked, so Spring rolls back by default.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A `@Transactional` method throws `IOException` (a checked exception). With no `rollbackFor`, what happens?
:::
- [ ] Rolled back
- [x] Committed: checked exceptions do not roll back by default
- [ ] The exception is swallowed
:::explain
Spring commits for checked exceptions unless they are listed in `rollbackFor`. The exception still reaches the
caller.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`OrderService.checkout()` (no annotation) calls `this.placeOrder()`, which is `@Transactional`. Is placeOrder transactional here?
:::
- [ ] Yes, always
- [x] No: a call inside the same object skips Spring's proxy
- [ ] Only if placeOrder is private
:::explain
The transaction is added by the proxy around the bean. Calls from other beans go through it; calls on `this`
do not. Annotate the method that outsiders call.
:::
:::

:::step{type=deep-dive title="Go deeper: read-only, propagation, isolation, and keeping them short"}
**readOnly.** `@Transactional(readOnly = true)` on methods that only read (you saw it in chapter 21) lets
Hibernate skip change tracking, and some setups send such work to read replicas.

**Propagation.** What happens when a transactional method calls another? By default (`REQUIRED`), the inner one
**joins** the outer transaction: one unit. `REQUIRES_NEW` suspends the outer one and starts a separate
transaction, useful for an audit log entry that must be saved even if the main work rolls back.

**Isolation.** How much concurrent transactions see of each other. The database's default is usually right; two
customers buying the last samosa at the same moment is a concurrency problem solved with locking (`@Version`,
optimistic locking), covered in the production course.

**Keep them short.** A transaction holds database locks until it ends. Never call a slow external service
(payment provider, email) *inside* one; do the database work, commit, then call out.
:::

:::step{type=recap title="What you can do now"}
Your multi-step changes are now safe:

- A **transaction** saves changes together or not at all (**ACID**: atomic, consistent, isolated, durable).
  Without one, each statement commits on its own.
- **`@Transactional`**: Spring starts a transaction, **commits** on normal return, **rolls back** on a
  `RuntimeException`. Changes to loaded entities are saved at commit, even without `save`.
- **Checked exceptions commit** by default: add `rollbackFor = SomeException.class`.
- It works through a **proxy**: public methods, called from **another bean**; calls on `this` skip it.

Next, chapter 24: so far Hibernate creates the tables on start-up. In real life the database outlives every
version of your app. Migrations with Flyway.
:::
