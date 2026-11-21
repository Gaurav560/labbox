:::step{type=story title="Why this chapter"}
Every HTTP response has a **status code**, and clients act on it before they read the body: a mobile
app shows "saved" for 201, "not found" for 404, and retries on 503. Returning 200 for everything hides
what happened. This chapter shows how to answer with the right code.

:::mission
In the `07-status-codes` folder: answer 201 Created with a Location header when a product is created,
and 204 or 404 when one is deleted.
:::
:::

:::step{type=concept title="The status codes an API uses"}
| code | meaning | typical use |
|---|---|---|
| `200 OK` | it worked, here is the result | `GET`, most `PUT` |
| `201 Created` | a new resource was created | `POST` that creates |
| `204 No Content` | it worked, nothing to return | `DELETE` |
| `400 Bad Request` | the request is invalid | validation errors |
| `404 Not Found` | no such resource | unknown id |
| `409 Conflict` | it clashes with the current state | duplicate email |
| `500 Internal Server Error` | the server failed | an unexpected exception |

Codes in the 200s mean success, 400s mean the client must change something, 500s mean the server failed.
:::

:::step{type=concept title="ResponseEntity"}
A method that returns an object always answers 200. To choose the code and headers, return a
`ResponseEntity`:

```java
return ResponseEntity.ok(product);                                  // 200 with a body
return ResponseEntity.created(URI.create("/products/4")).body(p);   // 201, Location header, body
return ResponseEntity.noContent().build();                          // 204, no body
return ResponseEntity.notFound().build();                           // 404, no body
```

`ResponseEntity<Product>` declares the body type; use `ResponseEntity<Void>` when there is never a body.
:::

:::step{type=example title="Worked example: cancel an order"}
```java
@PostMapping("/orders/{id}/cancel")
public ResponseEntity<Order> cancel(@PathVariable long id) {
    Optional<Order> order = service.find(id);
    if (order.isEmpty()) {
        return ResponseEntity.notFound().build();          // 1. no such order
    }
    if (order.get().isShipped()) {
        return ResponseEntity.status(409).build();         // 2. too late to cancel
    }
    return ResponseEntity.ok(service.cancel(order.get())); // 3. done
}
```

1. 404: the order does not exist.
2. 409 Conflict: the request is valid, but the order's state does not allow it.
3. 200 with the updated order.
:::

:::step{type=predict title="Guess first"}
:::question
What does a `@PostMapping` method that returns a `Product` answer, with no `ResponseEntity`?
:::
- [ ] 201 Created, because it is a POST
- [x] 200 OK
- [ ] 204 No Content
:::explain
Spring does not infer the code from the HTTP method. A plain return value always means 200; use
`ResponseEntity.created(...)` for 201.
:::
:::

:::step{type=try title="See the status code and headers"}
```bash run
cd 07-status-codes && mvn -q -o package -DskipTests && java -jar target/status-codes.jar
```

In a second tab, `-i` shows the status line and headers:

```bash run
curl -si -X POST localhost:8080/products -H 'Content-Type: application/json' -d '{"name": "Poha", "pricePaise": 2200}'
```
:::

:::step{type=task task=created_201 title="Warm-up: 201 Created with a Location"}
In `07-status-codes`, make `POST /products` answer `201 Created`, with a `Location` header pointing to the
new product (`/products/4` for the first one you add) and the product as the body.
:::

:::step{type=task task=delete_204 title="Delete: 204 or 404"}
Make `DELETE /products/{id}` answer `204 No Content` when a product was deleted, and `404 Not Found` when
there was no such product. `repository.delete(id)` returns whether it deleted something.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A client sends a product with a negative price. Which code fits?
:::
- [ ] 404
- [x] 400
- [ ] 500
:::explain
The request itself is wrong, so it is a 4xx. 400 Bad Request means "fix your request"; chapter 8 makes
Spring send it automatically.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does the `Location` header of a 201 contain?
:::
- [ ] The server's address
- [x] The URL of the newly created resource
- [ ] The client's address
:::explain
`Location: /products/4` tells the client where to find what it just created.
:::
:::

:::step{type=deep-dive title="Idempotency"}
`GET`, `PUT` and `DELETE` are **idempotent**: repeating them leaves the server in the same state.
Deleting product 3 twice still leaves it deleted (the second call answers 404). `POST` is not: two
identical `POST /orders` create two orders. That is why clients may safely retry a failed `GET` or `DELETE`,
but need care with `POST`. Payment APIs solve it with an **idempotency key** header: the server remembers
the key and does not create a second order for a retried request.
:::

:::step{type=recap title="Chapter done"}
- 2xx success, 4xx the client must change something, 5xx the server failed.
- Return `ResponseEntity` to choose the status code and headers.
- `POST` that creates answers 201 with a `Location`; `DELETE` answers 204, or 404 when nothing was there.
:::
