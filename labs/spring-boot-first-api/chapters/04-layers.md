:::step{type=story title="Why this chapter"}
A small app can put everything in one controller. As it grows, that controller becomes impossible to
read, reuse or test. Almost every Spring codebase therefore uses the same three layers. Knowing them
tells you where to put new code, and where to find existing code.

:::mission
In the `04-layers` folder: move a calculation out of a controller into its service, and add a
repository method for the service to use.
:::
:::

:::step{type=concept title="Controller, service, repository"}
| layer | annotation | its job |
|---|---|---|
| controller | `@RestController` | HTTP: paths, parameters, status codes, JSON |
| service | `@Service` | the application's rules and calculations |
| repository | `@Repository` | reading and writing data |

Each layer calls only the one below it: the controller calls the service, the service calls the
repository. A controller method is usually one or two lines: read the request, call the service,
return the result.

:::diagram{name="layers"}
Requests come in at the top; data is reached only through the repository.
:::
:::

:::step{type=concept title="Why separate them"}
- **Reuse:** a rule in a service can be called from a controller, a scheduled job or another service.
  A rule inside a controller can only be reached through HTTP.
- **Testing:** a service can be tested with a plain method call, without HTTP.
- **Change:** when the data moves from a list in memory to a database (chapter 11), only the
  repository changes. Services and controllers stay the same.

The rule of thumb: if a line is about HTTP, it belongs in the controller; if it is about the shop, it
belongs in the service.
:::

:::step{type=example title="Worked example: the most expensive product"}
The same feature, split into layers:

```java
// ProductService: the rule
public Product mostExpensive() {
    return repository.findAll().stream()
            .max(Comparator.comparingInt(Product::pricePaise))
            .orElseThrow();
}

// ProductController: only HTTP
@GetMapping("/products/most-expensive")
public Product mostExpensive() {
    return service.mostExpensive();
}
```

1. The service gets the data from the repository and applies the rule.
2. The controller maps the URL and delegates in one line.
3. The controller does not know where products are stored.
:::

:::step{type=predict title="Guess first"}
:::question
Where should "orders over Rs 500 get free delivery" be written?
:::
- [ ] In the controller that receives the order
- [x] In a service
- [ ] In the repository
:::explain
It is a business rule. In a service, it applies however the order arrives (web, mobile, a batch job),
and it can be tested without HTTP.
:::
:::

:::step{type=try title="See the layers"}
```bash run
cd 04-layers && ls src/main/java/com/shop/product/
```

Open `ProductController.java`: `averagePrice()` reads the repository and does the calculation itself.
:::

:::step{type=task task=thin_controller title="Warm-up: move the average into the service"}
In `04-layers`, `GET /products/average-price` works, but the controller calculates the average
itself. Move the calculation into `ProductService.averagePrice()`, and make the controller call it.

The answer stays the same (`3950`).
:::

:::step{type=concept title="Repository methods"}
A repository offers methods named after the data they return: `findAll()`, `findById(id)`,
`findByCategory(...)`. The service decides **which** data it needs and calls the matching method:

```java
// ProductRepository
public List<Product> findCheaperThan(int paise) {
    return PRODUCTS.stream().filter(p -> p.pricePaise() < paise).toList();
}
```

Keeping the filtering in the repository matters later: with a database, `findCheaperThan` becomes a
`WHERE` query that runs in the database, instead of loading every product into memory.
:::

:::step{type=task task=budget_products title="A repository method for budget products"}
In `04-layers`, add `findCheaperThan(int paise)` to `ProductRepository`, and make
`ProductService.budgetProducts()` use it with `BUDGET_PAISE`.

`GET /products/budget` should list the three products under Rs 50.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which layer should know that the data is in a `List` in memory?
:::
- [ ] The controller
- [ ] The service
- [x] Only the repository
:::explain
Only the repository knows how data is stored. When storage changes, the other layers are unaffected.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A controller method is 40 lines long. What does that usually mean?
:::
- [ ] Nothing: controllers are allowed to be long
- [x] Business logic is in the controller and should move to a service
- [ ] The controller needs more annotations
:::explain
Controllers translate between HTTP and the service. Long controller methods usually contain rules that
belong in a service.
:::
:::

:::step{type=deep-dive title="DTOs and where they live"}
In bigger codebases the layers also use different object types: the repository works with **entities**
(mapped to database tables, chapter 11), and the controller returns **DTOs** (data transfer objects,
chapter 6) shaped for the API. The service converts between them. This lets the database structure
and the public API change independently. For small services, using one type everywhere is fine.
:::

:::step{type=recap title="Chapter done"}
- Controller: HTTP. Service: rules. Repository: data. Each calls only the layer below.
- Business rules belong in services, where they can be reused and tested without HTTP.
- Repository methods are named after the data they return, such as `findCheaperThan`.
:::
