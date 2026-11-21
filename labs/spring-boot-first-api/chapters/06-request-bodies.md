:::step{type=story title="Why this chapter"}
Reading data is half of an API; the other half is receiving it. When an app creates a product or places
an order, it sends JSON in the request body. This chapter shows how that JSON becomes a Java object, and
why the objects you send back should be designed separately from the ones you store.

:::mission
In the `06-request-bodies` folder: create products from a JSON body, and return a view that hides the
shop's internal cost.
:::
:::

:::step{type=concept title="@RequestBody"}
`POST`, `PUT` and `PATCH` requests usually carry a **body**, most often JSON with the header
`Content-Type: application/json`. `@RequestBody` tells Spring to convert it to a parameter:

```java
public record NewProduct(String name, int pricePaise) {}

@PostMapping("/products")
public Product create(@RequestBody NewProduct body) {
    return repository.add(body.name(), body.pricePaise(), 0);
}
```

Jackson matches JSON properties to the record's components **by name**: `"name"` goes to `name`,
`"pricePaise"` to `pricePaise`. Unknown properties are ignored; missing ones get the default value
(`null`, or `0` for an `int`).

:::diagram{name="json-binding"}
JSON in, a Java record for your method; a Java object out, JSON for the client.
:::
:::

:::step{type=concept title="DTOs: separate what you send from what you store"}
A **DTO** (data transfer object) is a class whose only job is to carry data in or out of the API.
`NewProduct` (input) and `ProductView` (output) are DTOs; `Product` is how the shop stores a product.

Keeping them separate matters:

- **Security:** `Product` has `costPaise`, the price the shop paid. Returning `Product` would expose it.
- **Control:** clients cannot set fields they should not, such as `id`.
- **Stability:** the stored data can change without breaking the public API.

Records are a good fit for DTOs: short, immutable, and Jackson reads and writes them directly.
:::

:::step{type=example title="Worked example: a customer summary"}
A DTO that shows only what a client needs:

```java
public record CustomerSummary(long id, String name, String memberSince) {}

@GetMapping("/customers/{id}/summary")
public CustomerSummary summary(@PathVariable long id) {
    Customer c = service.get(id);                       // the stored object
    return new CustomerSummary(c.id(), c.name(),        // only safe fields
            c.createdAt().getYear() + "");              // shaped for display
}
```

The stored `Customer` might also hold a password hash and a phone number. The summary never includes
them, because the method builds the response from chosen fields only.
:::

:::step{type=predict title="Guess first"}
:::question
A client sends `{"name": "Tea", "pricePaise": 2000, "id": 999}` to a `@RequestBody NewProduct` with only `name` and `pricePaise`. What happens to `"id"`?
:::
- [ ] The product is stored with id 999
- [x] It is ignored: `NewProduct` has no `id` field
- [ ] The request fails with 400
:::explain
Jackson fills only the record's components and ignores unknown properties (Spring Boot's default). This
is one reason input DTOs are safer than binding directly to the stored type.
:::
:::

:::step{type=try title="Send JSON with curl"}
Start the app from the chapter folder:

```bash run
cd 06-request-bodies && mvn -q -o package -DskipTests && java -jar target/request-bodies.jar
```

After the first task, in a second tab:

```bash run
curl -s -X POST localhost:8080/products -H 'Content-Type: application/json' -d '{"name": "Vada pav", "pricePaise": 2500}'; echo
```

`-X POST` sets the method, `-H` the header, and `-d` the body.
:::

:::step{type=task task=create_product title="Warm-up: create a product"}
In `06-request-bodies`, add `POST /products`: read a `NewProduct` from the body, store it with
`repository.add(name, pricePaise, NEW_PRODUCT_COST_PAISE)`, and return the stored `Product`.

The new product then appears in `GET /products`, with an id.
:::

:::step{type=concept title="Formatting in the DTO"}
An output DTO can also present data in the form clients need. Prices are stored as whole paise (exact
integers); the view shows them as text:

```java
String price = String.format("Rs %d.%02d", paise / 100, paise % 100);   // 2000 -> "Rs 20.00"
```

`%02d` pads to two digits, so 5 paise becomes `05`.
:::

:::step{type=task task=product_view title="A view without the internal cost"}
`GET /products/{id}/view` returns the whole `Product`, including `costPaise`. Change it to return a
`ProductView`: the id, the name, and the price formatted as `Rs 20.00`. An unknown id still answers 404.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which annotation reads the JSON body of a request into a parameter?
:::
- [ ] `@RequestParam`
- [ ] `@PathVariable`
- [x] `@RequestBody`
:::explain
`@RequestBody` converts the whole body. `@RequestParam` reads query parameters, and `@PathVariable` reads parts of the path.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why return a `ProductView` instead of the stored `Product`?
:::
- [ ] Records are faster to serialize
- [x] The API shows only the fields you choose, so internal data like the cost is never exposed
- [ ] Spring cannot serialize `Product`
:::explain
Returning the stored type exposes every field it has today, and every field anyone adds later. A DTO makes
the API's contents a deliberate choice.
:::
:::

:::step{type=deep-dive title="Jackson's rules, and customising them"}
Jackson maps names exactly (`pricePaise`, not `price_paise`) unless configured otherwise: set
`spring.jackson.property-naming-strategy=SNAKE_CASE` for snake_case APIs. `@JsonProperty("price")` renames
one field. For dates, Spring Boot writes `LocalDate` as `"2026-11-21"` (ISO-8601) by default. Records need
no setters or default constructor; older classes need a no-argument constructor and setters, or a
constructor marked `@JsonCreator`.
:::

:::step{type=recap title="Chapter done"}
- `@RequestBody` converts a JSON body into a parameter; Jackson matches properties by name.
- DTOs carry data in and out of the API; keep them separate from what you store.
- Output DTOs choose and format the fields, so internal data is never exposed.
:::
