:::step{type=story title="When one class does everything"}
Picture the Shop API a year from now if every endpoint is written the quick way: the controller reads the
request, looks up products in the database, applies the discount rules, calculates GST, checks stock, and
builds the response, all in one method. It works. Then the same discount rule is needed by the mobile app's
endpoint, the admin endpoint and the nightly report, so it gets copied three times. Then the rule changes,
and one copy is forgotten.

Every serious Spring codebase avoids this the same way: by splitting the work into **layers**, each with
one job. It is not a Spring feature you switch on; it is a way of organising your classes, and Spring's
annotations are designed around it. Once you see it, you will recognise it in every Spring project you
ever open.

:::mission
Move a calculation out of the controller into the service, and give the repository a proper query method.
:::
:::

:::step{type=concept title="Three layers, three jobs"}
A typical Spring application has three layers. A request travels down through them, and the answer travels
back up:

:::diagram{name="layers"}
Each layer only talks to the one below it.
:::

- **The web layer: controllers** (`@RestController`). They speak **HTTP**: read the path, the query and the
  body; call the service; turn the result into a response with the right status. They contain no business
  rules.
- **The service layer: services** (`@Service`). They hold the **business rules**: what a "budget product"
  is, how a discount is calculated, what must be true before an order can be placed. They know nothing about
  HTTP: no `ResponseEntity`, no status codes, no request objects.
- **The data layer: repositories** (`@Repository`). They **store and fetch** data: from memory today, from a
  database in Part 3. They know nothing about business rules.

The rule that makes it work: **each layer only calls the layer directly below it.** Controllers call
services, services call repositories. A controller never reaches into a repository, and a repository never
calls a service.
:::

:::step{type=concept title="Why it is worth the extra classes"}
Three classes instead of one looks like more work. Here is what you get back:

- **One place for each rule.** "Budget means under Rs 50" lives in the service, once. The mobile endpoint,
  the admin endpoint and the report all call the same method. Change it once, it changes everywhere.
- **Changes stay contained.** When the products move from memory to a database (chapter 19), only the
  repository changes. The service and the controller do not notice. When the JSON format of a response
  changes, only the controller changes.
- **Easy to test.** A service can be tested with plain Java calls, no HTTP involved (chapter 25). A controller
  can be tested with a fake service.
- **Easy to read.** A new team member opens `ProductService` and finds every product rule, without reading
  HTTP code.

`@Service` and `@Repository` are, technically, just `@Component` with a different name (chapter 5). The
names document the role. `@Repository` also adds one real feature: it translates low-level database errors
into Spring's own, consistent exception types, which matters in Part 3.
:::

:::step{type=example title="Worked example: a fat controller, made thin"}
Here is an endpoint for a customer's loyalty points, written the quick way:

```java
@GetMapping("/customers/{id}/points")
public int points(@PathVariable long id) {
    List<Order> orders = orderRepository.findByCustomer(id);       // data access
    int total = 0;
    for (Order o : orders) {
        total += o.totalPaise() / 10000;                           // business rule: 1 point per Rs 100
    }
    return total;
}
```

The controller does three jobs: HTTP, data access and a business rule. The same, layered:

```java
// LoyaltyService: the rule lives here, once.
public int points(long customerId) {
    return orderRepository.findByCustomer(customerId).stream()
            .mapToInt(o -> o.totalPaise() / 10000)
            .sum();
}

// The controller: HTTP only.
@GetMapping("/customers/{id}/points")
public int points(@PathVariable long id) {
    return loyalty.points(id);
}
```

The controller is now one line: "get the id from the path, ask the service". That is what a healthy
controller looks like.

The stream shows one new tool, **`mapToInt(...).sum()`**: turn each order into a number, then add them all
up. It does the same as the `for` loop with `total +=`, in one expression.
:::

:::step{type=try title="Find the controller doing the service's job" file="14-layers/src/main/java/com/shop/product/ProductController.java" line="25-35"}
Look at `averagePrice()` in `ProductController`, on the right. It works, but it breaks the rule twice:

- it calls the **repository** directly (the controller holds a `ProductRepository` it should not need);
- it **calculates** the average itself, which is a business rule.

Meanwhile `ProductService.averagePrice()` exists, and returns `0` with a TODO. Run the app to see both:

```bash run
cd 14-layers && mvn -q -o package -DskipTests && java -jar target/layers.jar
```

```bash run
curl localhost:8080/products/average-price
```

It answers `3950`: the average of 2000, 3000, 1800 and 9000 (15800 / 4). The right number, from the wrong place.
(On our lab machine, `curl localhost:8080/products/budget` answered `[]` at this point: that is the second task.)
:::

:::step{type=task task=thin_controller title="Your turn: a thin controller"}
Move the calculation where it belongs:

1. In `ProductService.averagePrice()`, calculate the average price from the repository's products (0 when
   there are none). You can move the loop from the controller, or use `mapToInt(...)` with `average()` or
   `sum()`.
2. In `ProductController.averagePrice()`, just return what the service gives.
3. The controller no longer needs the `ProductRepository`: remove that field and constructor parameter.

`GET /products/average-price` still answers `3950`; the check also makes sure the service does the work.
Press **Check**.

Usual slips: `average()` gives an `OptionalDouble` (a decimal that may be missing), not an `int`; finish it with
`.orElse(0)` and turn it into an `int` with `(int)`, or use `sum()` and divide by the count yourself (checking for
zero products first, because dividing by zero crashes).
:::

:::step{type=concept title="Repositories answer questions about data" file="14-layers/src/main/java/com/shop/product/ProductRepository.java" line="9-27"}
Now the data layer. `ProductRepository` has `findAll()` and `findById(id)`. The service wants the
**budget products**: those under Rs 50.

The service *could* call `findAll()` and filter the list itself. With four products in memory, that is fine.
But in Part 3 the products live in a database with maybe a million rows. Fetching all of them to keep a
few would be very slow. A database is excellent at filtering; it should do it.

So the clean design is: the repository offers a method that answers the **data question** ("products cheaper
than X"), and the service decides the **business question** ("what counts as budget": X is Rs 50).

```java
// repository: a data question, with no opinion about what "budget" means
public List<Product> findCheaperThan(int paise) { ... }

// service: the business rule
public List<Product> budgetProducts() {
    return repository.findCheaperThan(BUDGET_PAISE);
}
```

Method names like `findCheaperThan` (or `findByPriceLessThan`) are a strong convention for repositories, and
in chapter 20 Spring Data will even write their code for you, just from the name.
:::

:::step{type=task task=budget_products title="Your turn: budget products, layered"}
1. In `ProductRepository`, add `findCheaperThan(int paise)`: the products whose price is **below** that
   number of paise.
2. In `ProductService.budgetProducts()`, return what the repository gives for `BUDGET_PAISE`.

Rebuild, run, and try:

```bash run
curl localhost:8080/products/budget
```

You should get the mango kulfi, the fruit custard and the samosa; not the paneer roll (Rs 90). (`BUDGET_PAISE`
is 5000, Rs 50.) Press **Check**.

Usual slips: `<=` instead of `<` ("below" means strictly less), or filtering in the service instead of in the
repository (the answer is the same, but the check looks for the data question in the repository).
:::

:::step{type=concept title="Where do things go? A quick guide"}
When you are unsure where a piece of code belongs, ask what it is about:

- Is it about **HTTP**? Paths, parameters, headers, status codes, JSON shapes, DTOs for requests and
  responses: **controller**.
- Is it a **rule of the business**, something a shopkeeper could explain without computers? Prices,
  discounts, stock limits, what is allowed: **service**.
- Is it about **storing or finding** data? Queries, saving, deleting: **repository**.

Two common mistakes to avoid:

- **Services returning `ResponseEntity` or taking request objects.** Then the service can only be used from
  HTTP. Return plain data; let the controller choose the status.
- **A "service" that only passes calls through.** For a trivial read (`findAll`), a one-line service method is
  fine and keeps the rule "controllers call services" simple and consistent. Do not skip the layer only
  because today the method is short.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Where does the rule "orders over Rs 500 get free delivery" belong?
:::
- [ ] In the controller, next to the endpoint
- [x] In a service
- [ ] In the repository's query
:::explain
It is a business rule. In a service, every endpoint, report and job that needs it calls the same method.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
The products move from an in-memory list to a database. Which classes have to change, in a layered app?
:::
- [ ] Controllers, services and repositories
- [x] Only the repository
- [ ] Only the controllers
:::explain
That is the point of layers: storage is the repository's job, so storage changes stay inside it. The service
still calls `findCheaperThan(...)`, whatever happens behind it.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Should a service method return `ResponseEntity<Product>`?
:::
- [ ] Yes, so the controller has less to do
- [x] No: status codes are HTTP, so they belong in the controller
- [ ] Only for errors
:::explain
A service should be usable from anywhere: HTTP, a scheduled job, a message listener, a test. Return plain
data (or throw a business exception); the controller turns that into HTTP.
:::
:::

:::step{type=deep-dive title="Go deeper: packaging by feature, and more layers"}
**Package by feature.** This project keeps all three layers of products in one package, `com.shop.product`.
That is called **package by feature**, and it scales well: everything about orders in `com.shop.order`,
everything about customers in `com.shop.customer`. The alternative, `controller`, `service` and `repository`
packages each holding every feature's classes, is common too, but tends to spread one change across many
folders.

**More layers.** Bigger systems sometimes add more: a **domain** layer of rich business objects, **mappers**
between DTOs and models, **clients** for other services (chapter 29). The principle stays the same: each
piece has one job, and dependencies point in one direction.
:::

:::step{type=recap title="What you can do now"}
You can now organise a Spring app the way professional teams do:

- **Controllers** speak HTTP; **services** hold business rules; **repositories** store and find data.
- Each layer only calls the one below it: controller to service to repository.
- One rule, one place: easier to change, test and read; storage changes stay in the repository.
- Repositories answer data questions (`findCheaperThan(paise)`); services decide business questions (what
  "budget" means).
- Services return plain data, never `ResponseEntity`.
- `mapToInt(...).sum()` adds up values from a stream.

:::photo{src="/lesson-images/spring/spring-14-notes.webp" alt="Sketchnote: Layers. Split the work by job: HTTP, business rules, data. Flow: request, controller, service, repository, data. Remember: a controller speaks HTTP; a service holds the rules and never returns ResponseEntity; a repository answers data questions; each layer calls only the one below." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 15: changing existing products properly, with PUT and PATCH.
:::
