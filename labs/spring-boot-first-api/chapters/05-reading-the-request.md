:::step{type=story title="Why this chapter"}
So far every endpoint returns the same answer every time. Real endpoints depend on the request: which
product, which page, which filter. This chapter shows how Spring passes parts of the URL to your
method as ordinary Java parameters.

:::mission
In the `05-reading-the-request` folder: return one product by its id, and add a search with optional filters.
:::
:::

:::step{type=concept title="Path variables"}
A **path variable** is a part of the path that changes, written in braces in the mapping:

```java
@GetMapping("/products/{id}")
public Product byId(@PathVariable long id) {
    ...
}
```

For `GET /products/3`, Spring takes `3` from the path, converts it to the parameter's type (`long`), and
calls `byId(3)`. If the text cannot be converted, as in `/products/abc`, Spring answers 400 Bad
Request without calling the method.

Use path variables to **identify** a resource: one product, one order.
:::

:::step{type=concept title="Query parameters"}
**Query parameters** come after `?` in the URL, as `name=value` pairs joined by `&`:

```java
@GetMapping("/products/search")
public List<Product> search(@RequestParam(required = false) Integer maxPrice,
                            @RequestParam(defaultValue = "name") String sort) {
    ...
}
```

- By default a `@RequestParam` is **required**: missing it gives 400.
- `required = false` makes it optional; it is then `null` when missing, so use `Integer`, not `int`.
- `defaultValue` supplies a value when the parameter is missing.

Use query parameters to **filter, sort or page** a list.

:::diagram{name="request-mapping"}
Spring splits the URL and passes each part to the matching parameter.
:::
:::

:::step{type=example title="Worked example: orders by status"}
```java
@GetMapping("/customers/{customerId}/orders")
public List<Order> orders(@PathVariable long customerId,
                          @RequestParam(defaultValue = "all") String status) {
    return service.ordersFor(customerId, status);
}
```

| request | customerId | status |
|---|---|---|
| `GET /customers/7/orders` | 7 | `"all"` (the default) |
| `GET /customers/7/orders?status=paid` | 7 | `"paid"` |
| `GET /customers/x/orders` | not called: 400 | |

1. The path identifies the customer.
2. The query parameter filters the list, with a default.
3. A wrong type is rejected by Spring before your code runs.
:::

:::step{type=predict title="Guess first"}
:::question
`@RequestParam int page` (no default, required). What does `GET /products` answer?
:::
- [ ] Page 0
- [x] 400 Bad Request: the required parameter is missing
- [ ] 500 Internal Server Error
:::explain
Required parameters must be present. Add `defaultValue = "0"` or `required = false` with an `Integer`.
:::
:::

:::step{type=try title="Call it with different URLs"}
```bash run
cd 05-reading-the-request && mvn -q -o package -DskipTests && java -jar target/reading-the-request.jar
```

In a second tab, after you finish the tasks:

```bash run
curl -s localhost:8080/products/3; echo; curl -s "localhost:8080/products/search?maxPrice=2000&sort=price"; echo
```

Quote URLs that contain `&`, or the shell treats it as "run in the background".
:::

:::step{type=task task=product_by_id title="Warm-up: one product by id"}
In `05-reading-the-request`, add `GET /products/{id}` returning that product as JSON. For an unknown id,
throw `new ResponseStatusException(HttpStatus.NOT_FOUND, "...")`, which Spring turns into a 404.

`GET /products/3` returns the Samosa; `GET /products/99` answers 404.
:::

:::step{type=task task=search_products title="Search with optional filters"}
Add `GET /products/search` with two optional query parameters:

- `maxPrice` (paise): keep products whose price is less than or equal to it; no limit when missing;
- `sort`: `name` (the default) or `price` (cheapest first).

`GET /products/search?maxPrice=2000` returns Masala tea and Samosa, sorted by name.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which fits better for "the order with id 42"?
:::
- [x] `GET /orders/42`, a path variable
- [ ] `GET /orders?id=42`, a query parameter
:::explain
Path variables identify one resource; query parameters filter or sort a collection. Both work, but this
convention makes APIs predictable.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is an optional `maxPrice` declared as `Integer` and not `int`?
:::
- [ ] `int` cannot hold prices
- [x] A missing parameter is `null`, and an `int` cannot be `null`
- [ ] Spring only converts to wrapper types
:::explain
With `required = false`, Spring passes `null` when the parameter is absent. A primitive `int` cannot
hold `null`, so the request would fail.
:::
:::

:::step{type=deep-dive title="Headers, and binding to an object"}
`@RequestHeader("X-Request-Id") String id` reads an HTTP header the same way. When a search has many
parameters, you can bind them to one object instead: a method parameter of type
`ProductFilter(Integer maxPrice, String sort)` (a record) is filled from the query parameters with the
same names, without any annotation. Combined with validation (chapter 8), this keeps search endpoints
short.
:::

:::step{type=recap title="Chapter done"}
- `@PathVariable` takes a part of the path, such as `{id}`, and converts it to the parameter's type.
- `@RequestParam` reads query parameters; use `required = false` or `defaultValue` for optional ones.
- Path variables identify a resource; query parameters filter, sort and page.
- `ResponseStatusException(HttpStatus.NOT_FOUND)` answers 404 for a missing resource.
:::
