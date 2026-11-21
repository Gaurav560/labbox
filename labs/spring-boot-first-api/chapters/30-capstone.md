:::step{type=story title="The capstone: a checkout API"}
Everything in this course comes together in one endpoint: **checkout**. A customer sends their email and
the items they want. The API checks the input, takes the items from stock, works out the total, saves the
order, and answers with where to find it. If anything is wrong, it answers with a clear error, and
nothing in the database changes.

:::mission
In the `30-capstone` folder: build `POST /checkout` and its error answers.
:::
:::

:::step{type=concept title="What you will use, and where you learned it"}
- A request body read into a record, with validation on it: chapters 6 and 8.
- 201 Created with a Location header: chapter 7.
- Entities and repositories: chapters 11 and 12.
- One transaction around the whole checkout: chapter 15.
- `ProblemDetail` answers from a `@RestControllerAdvice`: chapter 9.

:::diagram{name="checkout-flow"}
The request passes validation, the service works in one transaction, errors become ProblemDetails.
:::
:::

:::step{type=example title="The request and the answers"}
The request:

```json
{"customerEmail": "asha@shop.in", "items": [{"sku": "TEA-1", "quantity": 2}, {"sku": "COF-1", "quantity": 1}]}
```

The answers your API gives:

- **201 Created**, `Location: /orders/1`, body `{"id": 1, "customerEmail": "asha@shop.in", "totalPaise": 7000}`;
- **400** with a ProblemDetail titled `Invalid request` and an `errors` map, when the body breaks the rules;
- **409 Conflict** with a ProblemDetail titled `Out of stock` and the `sku`, when an item has run out.

`CheckoutRequest`, `StockItem`, `ShopOrder`, both repositories and `OutOfStockException` are ready. You
write the service, the endpoint and the error handlers.
:::

:::step{type=example title="Worked example: the service, step by step"}
The shape of a transactional service method that changes several rows:

```java
@Transactional
public Booking book(BookingRequest request) {
    int total = 0;
    for (BookingRequest.Seat seat : request.seats()) {
        Show show = shows.findById(seat.showId()).orElseThrow(() -> new SoldOutException(seat.showId()));
        show.reserve(seat.count());              // throws SoldOutException if not enough seats
        total += show.getPricePaise() * seat.count();
    }
    return bookings.save(new Booking(request.email(), total));
}
```

Changes to `show` are saved at commit without calling `save`: inside a transaction, Hibernate tracks the
entities it loaded and writes what changed. If `reserve` throws for the second show, the whole method
rolls back, and the first show's seats are back.

:::trace{title="checkout: TEA-1 x1, then SAM-1 x5 (1 left)"}
| step | TEA-1 stock | SAM-1 stock | total |
|---|---|---|---|
| transaction starts | 10 | 1 | 0 |
| take 1 TEA-1 | 9 | 1 | 2000 |
| take 5 SAM-1 | 9 | 1 | OutOfStockException |
| rollback | 10 | 1 | the advice answers 409 |
:::
:::

:::step{type=task task=checkout title="POST /checkout"}
In `30-capstone/.../checkout/CheckoutService.java`, write `checkout`: in one transaction, take each
line's quantity from its `StockItem` (an unknown sku is out of stock), add up the total, and save a
`ShopOrder`. In `CheckoutController`, add `POST /checkout`: validate the body, call the service, and
answer 201 with `Location: /orders/{id}` and the order.
:::

:::step{type=predict title="Guess first"}
:::question
The checkout loop takes the tea, then throws OutOfStockException for the samosas. Your controller does not catch it. What does the client get?
:::
- [ ] 500, always
- [x] Whatever your @RestControllerAdvice answers for OutOfStockException; without a handler, 500
- [ ] 409, because Spring knows it is a conflict
:::explain
Spring does not know what your exceptions mean. A handler in the advice turns each one into the right
status and body, for every controller at once.
:::
:::

:::step{type=try title="Place an order by hand"}
```bash run
cd 30-capstone && mvn -q -o package -DskipTests && java -jar target/capstone.jar
```

```bash run
curl -si -X POST localhost:8080/checkout -H 'Content-Type: application/json' -d '{"customerEmail": "asha@shop.in", "items": [{"sku": "TEA-1", "quantity": 2}]}'
```
:::

:::step{type=task task=checkout_errors title="Clear errors, and nothing half-done"}
In `30-capstone/.../ApiErrors.java`, answer:

- `OutOfStockException` with 409, title `Out of stock`, the message as detail, and a `sku` property;
- validation errors with 400, title `Invalid request`, and an `errors` map of field to message.

The check also makes sure a failed checkout leaves the stock exactly as it was.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is the total worked out on the server from StockItem prices, not taken from the request?
:::
- [ ] It is faster
- [x] The client could send any price; the server must trust only its own data
- [ ] JSON cannot hold numbers
:::explain
Never trust prices, totals, roles or ids of other users from a request. Read them from your own database.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Two customers check out the last samosa at the same moment. What could go wrong in this design?
:::
- [ ] Nothing: transactions prevent it
- [x] Both may read quantity 1 before either commits, and both succeed
- [ ] The database deletes the samosa
:::explain
Transactions alone do not stop two of them reading the same old value. Real shops add optimistic locking
(`@Version` on the entity) or an atomic `UPDATE ... SET quantity = quantity - ? WHERE quantity >= ?`.
That is one of the first topics in "Spring Boot in production".
:::
:::

:::step{type=deep-dive title="What a production checkout adds"}
This checkout is correct for one server and honest traffic. In production you would add: `@Version` for
concurrent buyers; an **idempotency key** header so a retried request does not create two orders; the
payment call **outside** the database transaction, with a status on the order; an event or outbox table
so emails and invoices are sent reliably after the commit; metrics on checkouts and failures. The
"Spring Boot in production" course builds each of these, one incident at a time.
:::

:::step{type=recap title="Course done"}
You have built a Spring Boot API from the first endpoint to a real checkout:

- controllers, request bodies, status codes, validation and ProblemDetail errors;
- beans, layers, configuration and profiles;
- JPA entities, repositories, relationships, paging, transactions and Flyway migrations;
- tests for the web and data layers, logs, health, security, and calls to other services.

These are the parts of nearly every Spring Boot service in production.
:::
