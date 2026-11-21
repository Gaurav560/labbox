:::step{type=story title="When the client sends data"}
Reading data is half of an API. The other half is accepting it: a shop owner adds a new product, a
customer places an order, someone updates their address. That data arrives as **JSON in the request
body**, and your code needs it as a Java object.

This chapter covers that, and something just as important: **what you send back**. Right now the Shop API
has a quiet data leak. Every product it returns includes `costPaise`, what the shop *paid* for it, which
customers (and competitors) should never see. The fix is a habit every professional API follows: separate
classes for what comes in, what is stored, and what goes out. They are called **DTOs**, and you will
understand exactly why they exist.

:::mission
Accept new products with `POST /products`, and stop leaking the shop's costs with a `ProductView`.
:::
:::

:::step{type=concept title="The project, and the leak" file="12-request-bodies/src/main/java/com/shop/product/Product.java" line="3-4"}
`Product.java` is on the right:

```java
public record Product(long id, String name, int pricePaise, int costPaise) { }
```

`costPaise` is what the shop paid the supplier. It is needed inside the shop (to calculate profit), but it
is **internal**. Now start the app and look at what `GET /products` sends to anyone who asks:

```bash run
cd 12-request-bodies && mvn -q -o package -DskipTests && java -jar target/request-bodies.jar
```

```bash run
curl localhost:8080/products
```

```text
[{"id":1,"name":"Masala tea","pricePaise":2000,"costPaise":900}, ...]
```

There it is: tea costs the shop Rs 9 and sells for Rs 20. Jackson writes **every field** of the object you
return. It has no idea which ones are secret. Keep that in mind; we will fix it in the second task. Leave
the app running.
:::

:::step{type=concept title="Reading the body: @RequestBody"}
To read the request body, you add a parameter marked **`@RequestBody`**:

```java
public record NewCustomer(String name, String email) { }

@PostMapping("/customers")
public Customer create(@RequestBody NewCustomer body) {
    return customers.add(body.name(), body.email());
}
```

When a request arrives with this body:

```json
{"name": "Asha", "email": "asha@shop.in"}
```

Spring hands the body to Jackson (the same message converter that writes your responses, now working in
reverse). Jackson creates a `NewCustomer`, matching each JSON field to the record component **with the same
name**: `"name"` to `name`, `"email"` to `email`. Your method receives a ready Java object; you never touch
the raw JSON text.

Three details worth knowing:

- **A missing field** gets the type's default: `null` for objects like `String`, `0` for `int`, `false` for
  `boolean`. (Chapter 16 adds validation to refuse bodies with missing or wrong values.)
- **An extra field** the record does not have is **ignored** (Spring Boot sets Jackson up that way).
- The client must say the body is JSON, with the header `Content-Type: application/json`.
:::

:::step{type=example title="Worked example: one body, three outcomes"}
Let's see what happens with a good body, a forgotten header, and broken JSON, using the solved version of
this chapter's endpoint:

```text
POST /products   Content-Type: application/json   {"name": "Vada pav", "pricePaise": 2500}
-> 200   {"id":4,"name":"Vada pav","pricePaise":2500,"costPaise":0}

POST /products   (no Content-Type header)          {"name": "Vada pav", "pricePaise": 2500}
-> 415 Unsupported Media Type

POST /products   Content-Type: application/json   {"name": "Vada pav", pricePaise: 2500
-> 400 Bad Request
```

- **415** happens because curl, without `-H "Content-Type: application/json"`, labels the body as a web
  form. Spring has no converter that turns a form into a `NewProduct`, so it refuses. The server log even
  says why: `Content-Type 'application/x-www-form-urlencoded' is not supported`.
- **400** happens because the JSON is broken (a name without quotes, a missing `}`). Jackson cannot read
  it, and the log says `JSON parse error: Unexpected character ('p')... was expecting double-quote`.

In both error cases, your method never runs. When a POST "does nothing", check these two things first:
the Content-Type header, and the JSON itself.
:::

:::step{type=task task=create_product title="Your turn: POST /products"}
At the first TODO in `ProductController`, add **`POST /products`**:

- its parameter is a `NewProduct` read from the body;
- it stores it with `repository.add(name, pricePaise, NEW_PRODUCT_COST_PAISE)` (the cost is filled in later
  by the back office, so new products start at 0);
- it returns the stored `Product`.

Rebuild, run, and add a product:

```bash run
curl -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "Vada pav", "pricePaise": 2500}'
```

You get it back with its new id, 4. Then `curl localhost:8080/products` shows four products. Press **Check**.
:::

:::step{type=concept title="Why one class is not enough: DTOs"}
Look at the two classes the body went through. The client sent a **`NewProduct`** (name and price), and
the shop stored a **`Product`** (id, name, price *and cost*). Why not just use `Product` for both?

Try to imagine `@RequestBody Product body`. The client could then send:

```json
{"id": 1, "name": "Masala tea", "pricePaise": 1, "costPaise": 999999}
```

and choose the id (overwrite someone else's product?) and the cost (corrupt the shop's accounts). Fields
that the *server* should control would be in the client's hands. This is a real class of security bug,
called **mass assignment**.

`NewProduct` simply has no `id` or `costPaise`. A client can send them, and Jackson ignores them, because
there is nowhere to put them. Try it:

```bash run
curl -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "Poha", "pricePaise": 2200, "costPaise": 5}'
```

```text
{"id":5,"name":"Poha","pricePaise":2200,"costPaise":0}
```

The cost stayed 0. That is the idea of a **DTO** (Data Transfer Object): a class shaped exactly for **one
direction of one conversation**. A typical API has:

- an **input DTO** per kind of request (`NewProduct`): only what the client may set;
- the **internal model** (`Product`): everything the shop stores;
- an **output DTO** per kind of response (`ProductView`): only what the client may see.

They look like duplication at first. They are protection: each one is a written contract about what
crosses the boundary.
:::

:::step{type=concept title="The output side: a ProductView" file="12-request-bodies/src/main/java/com/shop/product/ProductView.java" line="3-4"}
Now the leak in the other direction. `ProductView.java` is on the right:

```java
public record ProductView(long id, String name, String price) { }
```

No cost. And the price is a **formatted text**, `"Rs 20.00"`, ready to show in an app, instead of a raw
number of paise. Building it from a `Product` is your job in the second task.

Formatting money: `String.format` builds text from a pattern. `%d` puts an integer in; `%02d` puts an
integer in with at least two digits, padding with zeros. So for 2050 paise:

```java
String.format("Rs %d.%02d", 2050 / 100, 2050 % 100)   // "Rs 20.50"
String.format("Rs %d.%02d", 2000 / 100, 2000 % 100)   // "Rs 20.00"  (%02d turns 0 into "00")
String.format("Rs %d.%02d", 1805 / 100, 1805 % 100)   // "Rs 18.05"
```

`/ 100` is integer division (the rupees), `% 100` is the remainder (the paise). Because prices are kept in
paise as whole numbers, there are never rounding errors, which is exactly why shops do it this way.
:::

:::step{type=task task=product_view title="Your turn: GET /products/{id}/view, without the cost"}
The method at the second TODO already exists, but it returns the whole `Product`. Change it so it returns a
**`ProductView`**: the same id, the same name, and the price formatted as `Rs 20.00`. Unknown id stays 404.

Rebuild, run, and compare:

```bash run
curl localhost:8080/products/1/view
```

```text
{"id":1,"name":"Masala tea","price":"Rs 20.00"}
```

No `costPaise` anywhere. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A client POSTs `{"name": "Tea", "pricePaise": 2000, "discount": 50}`, and `NewProduct` has no `discount`. What happens?
:::
- [ ] 400 Bad Request: unknown field
- [x] The product is created; discount is ignored
- [ ] discount is stored anyway
:::explain
Spring Boot's Jackson ignores fields it has nowhere to put. That is part of why input DTOs protect you: a
client cannot set fields the DTO does not have.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`curl -X POST localhost:8080/products -d '{"name": "Tea", "pricePaise": 2000}'` (no -H) answers 415. Why?
:::
- [ ] The JSON is invalid
- [x] Without the Content-Type header, the body is labelled as a form, which Spring cannot turn into a NewProduct
- [ ] POST is not allowed
:::explain
415 Unsupported Media Type is about the label on the body, not the content. Add
`-H "Content-Type: application/json"`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does the shop return a `ProductView` instead of a `Product`?
:::
- [ ] Records cannot be converted to JSON twice
- [x] So internal fields (the cost) are never sent, and the client gets exactly the agreed shape
- [ ] It is faster
:::explain
Jackson writes every field of whatever you return. An output DTO decides deliberately what leaves the
server. It also lets the internal model change without breaking clients.
:::
:::

:::step{type=deep-dive title="Go deeper: @JsonIgnore, JSON names, and dates"}
**@JsonIgnore.** You could put `@JsonIgnore` on `costPaise` so Jackson never writes it. It works, but it ties
the internal class to one API's needs, and it is easy to forget on the next secret field. Separate DTOs keep
the decision visible.

**Different names in JSON.** `@JsonProperty("price_paise")` on a component renames it in JSON, when a client
expects snake_case names.

**Dates and times.** Jackson writes `LocalDate` as `"2026-11-21"` and `Instant` as an ISO timestamp, thanks to
the modules the web starter includes (you saw `jackson-datatype-jsr310` in chapter 2's dependency tree).

**Mapping helpers.** Converting between models and DTOs by hand is clear and simple, as you did here. Big
projects sometimes use a library like MapStruct to generate that code.
:::

:::step{type=recap title="What you can do now"}
You can now accept data safely and control exactly what you send:

- **`@RequestBody`** turns the JSON body into a Java object; fields match by name; missing fields get
  defaults; unknown fields are ignored.
- The client must send `Content-Type: application/json`, or gets **415**; broken JSON gets **400**; in both
  cases your method never runs.
- **DTOs**: an input DTO holds only what a client may set (no **mass assignment**); an output DTO holds only
  what a client may see (no leaks); the internal model holds everything.
- Money in paise, formatted with `String.format("Rs %d.%02d", paise / 100, paise % 100)`.

Next, chapter 13: answering with the right status code, every time, with `ResponseEntity`.
:::
