:::step{type=story title="The capstone: your checkout"}
This is the last chapter, and it is different from the others. There is very little new to learn. Instead, you
build the most important endpoint of any shop, **checkout**, mostly on your own, using what you learned across the
whole course.

A customer sends their email and the items they want. Your API checks the input, takes the items from stock, works
out the total from the shop's own prices, saves the order, and answers with where to find it. If anything is wrong,
it answers with a clear problem, and **nothing in the database changes**. That one endpoint touches almost every
chapter: request bodies, validation, layers, entities, repositories, transactions, status codes and errors.

Take your time with it. When it passes, you will have built a real piece of a real backend, the way it is done in
production.

:::mission
Build `POST /checkout` and its error answers, so a failed checkout never changes anything.
:::
:::

:::step{type=concept title="The contract: what checkout must do"}
Before any code, the contract. This is how teams start: agree on the requests and responses first.

**The request:**

```json
POST /checkout
{"customerEmail": "asha@shop.in", "items": [{"sku": "TEA-1", "quantity": 2}, {"sku": "COF-1", "quantity": 1}]}
```

**The answers:**

- **201 Created**, a `Location: /orders/{id}` header, and the order as the body:
  `{"id": 1, "customerEmail": "asha@shop.in", "totalPaise": 7000}`.
- **400** with a problem titled `Invalid request` and an `errors` map, when the body breaks the rules (a bad email,
  no items, a quantity of 0).
- **409 Conflict** with a problem titled `Out of stock` and the `sku`, when there is not enough of an item, or the
  sku does not exist.

**The rules:**

- The total is calculated **on the server**, from the shop's own prices. Never from the request.
- Stock goes down by the quantities bought.
- **All or nothing**: if any item fails, no stock changes and no order is saved.

The stock starts at: Masala tea (TEA-1) 10 at Rs 20, Samosa (SAM-1) **1** at Rs 18, Filter coffee (COF-1) 5 at Rs 30.
:::

:::step{type=concept title="What is already built, and what you build"}
Open the project's file tree. It is layered, like chapter 14:

**Ready for you:**

- `CheckoutRequest`: the request body, a record with validation rules already on it (`@NotBlank @Email` email,
  `@NotEmpty` items, each line with a `@NotBlank` sku and a `@Positive` quantity, and `@Valid` on the lines so
  each line is checked too, chapter 16).
- `StockItem` (entity: sku, name, price, quantity, and a `take(n)` method that throws `OutOfStockException` when
  there is not enough), `ShopOrder` (entity: id, email, total), and their repositories.
- `OutOfStockException`, which carries the sku.
- `CheckoutController` with `GET /orders/{id}`.

**Yours to build:**

1. `CheckoutService.checkout(...)`: the business logic, in one transaction.
2. `POST /checkout` in `CheckoutController`.
3. Two handlers in `ApiErrors`: out of stock, and invalid requests.

Each piece is something you have done before, in an earlier chapter. The next steps point you to which one.
:::

:::step{type=concept title="The service: one transaction, server-side prices" file="30-capstone/src/main/java/com/shop/checkout/CheckoutService.java"}
`CheckoutService` is on the right. Its `checkout` method should:

1. run in **one transaction** (chapter 23);
2. for each line of the request: find the `StockItem` by sku (an unknown sku counts as out of stock: throw
   `OutOfStockException` with that sku), call `take(quantity)`, and add `price x quantity` to the total;
3. save a new `ShopOrder` with the email and the total, and return it.

Here is the same shape for a different business, cinema tickets, so you can see the pattern without being given the
answer:

```java
@Transactional
public Booking book(BookingRequest request) {
    int total = 0;
    for (BookingRequest.Seat seat : request.seats()) {
        Show show = shows.findById(seat.showId()).orElseThrow(() -> new SoldOutException(seat.showId()));
        show.reserve(seat.count());                    // throws SoldOutException if not enough seats
        total += show.getPricePaise() * seat.count();
    }
    return bookings.save(new Booking(request.email(), total));
}
```

Notice `show.reserve(...)` is never followed by `save(show)`. Inside a transaction, JPA tracks the entities it loaded
and writes their changes at commit (chapter 23). And if `reserve` throws on the second show, the first show's seats
are released too: that is the transaction rolling back.

:::trace{title="checkout: TEA-1 x1, then SAM-1 x5 (only 1 left)"}
| step | TEA-1 stock | SAM-1 stock | total |
|---|---|---|---|
| transaction starts | 10 | 1 | 0 |
| take 1 TEA-1 | 9 | 1 | 2000 |
| take 5 SAM-1 | 9 | 1 | OutOfStockException |
| rollback | 10 | 1 | the error handler answers 409 |
:::
:::

:::step{type=predict title="Guess first"}
:::question
Why is the total worked out from `StockItem` prices, and not taken from a price field in the request?
:::
- [ ] It is faster
- [x] The client could send any price; the server must only trust its own data
- [ ] JSON cannot hold prices
:::explain
Never trust prices, totals, roles or other users' ids from a request. Anyone can send any JSON. The server decides
from its own database.
:::
:::

:::step{type=concept title="The endpoint, and the errors"}
**`POST /checkout`** in `CheckoutController` (chapters 12, 13, 16): a `@Valid @RequestBody CheckoutRequest`
parameter, call the service, and answer **201** with `ResponseEntity.created(URI.create("/orders/" + id))` and the
order as the body. The controller stays thin: no business logic, only HTTP.

**`ApiErrors`** (chapter 17) needs two `@ExceptionHandler` methods returning `ProblemDetail`:

- for **`OutOfStockException`**: status **409**, title **`Out of stock`**, the exception's message as the detail,
  and a property **`sku`** with the sku (`setProperty("sku", e.sku())`);
- for **`MethodArgumentNotValidException`**: status **400**, title **`Invalid request`**, and an **`errors`**
  property mapping each field to its message, exactly as in chapter 17.

Because the service's exception travels up through the controller to the advice, and the transaction has already
rolled back by then, the client gets a clear 409 **and** the stock is untouched.
:::

:::step{type=task task=checkout title="Your turn: POST /checkout"}
Build the **service** and the **endpoint** (the first two pieces). Then run it:

```bash run
cd 30-capstone && mvn -q -o package -DskipTests && java -jar target/capstone.jar
```

```bash run
curl -i -X POST localhost:8080/checkout -H "Content-Type: application/json" -d '{"customerEmail": "asha@shop.in", "items": [{"sku": "TEA-1", "quantity": 2}, {"sku": "COF-1", "quantity": 1}]}'
```

```text
HTTP/1.1 201
Location: /orders/1

{"id":1,"customerEmail":"asha@shop.in","totalPaise":7000}
```

2 teas (Rs 40) + 1 coffee (Rs 30) = Rs 70. Then `curl localhost:8080/orders/1` returns the saved order. The check also
confirms the stock went down. Press **Check**.
:::

:::step{type=task task=checkout_errors title="Your turn: clear errors, nothing half-done"}
Add the two handlers to **`ApiErrors`**. Then try both failures:

```bash run
curl -i -X POST localhost:8080/checkout -H "Content-Type: application/json" -d '{"customerEmail": "ravi@shop.in", "items": [{"sku": "TEA-1", "quantity": 1}, {"sku": "SAM-1", "quantity": 5}]}'
```

```text
HTTP/1.1 409
{"type":"about:blank","title":"Out of stock","status":409,"detail":"Not enough stock for SAM-1","instance":"/checkout","sku":"SAM-1"}
```

```bash run
curl -i -X POST localhost:8080/checkout -H "Content-Type: application/json" -d '{"customerEmail": "not-an-email", "items": []}'
```

```text
HTTP/1.1 400
{"type":"about:blank","title":"Invalid request","status":400,"instance":"/checkout","errors":{"items":"must not be empty","customerEmail":"must be a well-formed email address"}}
```

The check also makes sure the tea taken before the samosas ran out was **put back**. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two customers check out the last samosa at exactly the same moment. Can both succeed with this design?
:::
- [ ] No: transactions prevent it
- [x] Yes: both may read quantity 1 before either one commits
- [ ] No: the database deletes the samosa
:::explain
Transactions make each checkout all-or-nothing, but two of them can still read the same old value. Real shops add
**optimistic locking** (a `@Version` field: the second commit fails and can be retried) or an atomic
`UPDATE ... SET quantity = quantity - ? WHERE sku = ? AND quantity >= ?`. That is one of the first topics of the
production course.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The phone app's network drops just after it sends the checkout, so it retries. What could go wrong?
:::
- [ ] Nothing: POST is safe to repeat
- [x] The customer may be charged and given two orders: POST is not idempotent
- [ ] The second request always gets 409
:::explain
POST creates something each time. Production checkouts accept an **idempotency key** (a unique id the client sends
with the request): a retry with the same key returns the first result instead of creating a second order.
:::
:::

:::step{type=deep-dive title="What a production checkout adds"}
What you built is correct for one server and honest traffic. A production checkout adds:

- **Concurrency**: `@Version` optimistic locking or atomic updates for the last-item race.
- **Idempotency keys**, so retries never create duplicate orders.
- **Payment outside the transaction**: never hold database locks while calling a payment provider (chapter 29). Save
  the order as `PENDING`, call the provider, then mark it `PAID` or `FAILED`.
- **An outbox**: emails and invoices are sent reliably after the commit, from a table, so a crash cannot lose them or
  send them for an order that rolled back.
- **Metrics and alerts** on checkout successes, failures and latency (chapter 27).

The **Spring Boot in production** course builds each of these, one real incident at a time.
:::

:::step{type=recap title="You have built a Spring Boot API"}
Look back at what you have learned, from "what is a framework" to a working checkout:

- **Foundations**: HTTP and JSON, Maven, how Spring Boot starts, beans and dependency injection, configuration and
  profiles, auto-configuration and its conditions, the life of a bean.
- **REST APIs**: how Spring handles a request, reading paths, parameters, headers and bodies, DTOs, status codes and
  `ResponseEntity`, layers, PUT and PATCH, validation, `ProblemDetail` errors, filters and interceptors.
- **Data**: JPA entities, Spring Data repositories and derived queries, relationships and the N+1 problem, paging and
  JPQL, transactions, Flyway migrations.
- **Production basics**: tests for controllers and queries, logs and health checks, security, calling other services
  with timeouts.

These are the building blocks of nearly every Spring Boot service running in production today. You do not just know
the annotations: you know what Spring is doing underneath each one, how to read its logs and errors, and how to check
your own work. Well done.
:::
