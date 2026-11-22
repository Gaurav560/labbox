:::step{type=story title="Saying exactly what happened"}
Every response starts with a status code, and clients rely on it. A phone app checks for `201` to show
"Product added", for `404` to show "This product no longer exists", for `5xx` to show "Something went
wrong, try again". If your API answers `200` to everything, every client has to dig through the body to
guess what happened, and many will guess wrong.

So far your methods only chose the **body**; Spring always answered `200` (or threw for errors). In this
chapter you take control of the **whole response**: the status code, the headers and the body, with one
class, `ResponseEntity`. And you fix two places where the Shop API is currently not telling the truth.

:::mission
Make `POST /products` answer `201 Created` with a `Location`, and `DELETE /products/{id}` answer `204` or `404`.
:::
:::

:::step{type=concept title="Two endpoints that say 200 for everything" file="13-status-codes/src/main/java/com/shop/product/ProductController.java" line="26-36"}
Look at the two methods with TODOs on the right.

`create` returns a `Product`, so Spring answers **200** with it. But something new was just created. HTTP
has a precise code for that, **201 Created**, plus a convention: a **`Location`** header saying where the
new thing now lives, so the client can fetch it later.

`delete` returns `void` (nothing). Spring answers **200** with an empty body. Worse, it answers 200 even when
there was **nothing to delete**: `repository.delete(id)` returns `false` in that case, and the method ignores
it. The client is told "done" for an id that never existed.

See both for yourself:

```bash run
cd 13-status-codes && mvn -q -o package -DskipTests && java -jar target/status-codes.jar
```

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "Poha", "pricePaise": 2200}'; echo; curl -i -X DELETE localhost:8080/products/99
```

`200` and `200`. Both technically "work", and both mislead. Leave the app running.
:::

:::step{type=concept title="ResponseEntity: the whole response in one object"}
**`ResponseEntity<T>`** is a Spring class that represents a complete HTTP response: a status, headers, and
a body of type `T`. When your method returns one, Spring sends exactly what it describes.

You build one with short, readable factory methods:

```java
ResponseEntity.ok(product)                        // 200 with the product as body
ResponseEntity.status(HttpStatus.ACCEPTED).body(x) // any status, with a body
ResponseEntity.notFound().build()                 // 404, no body
ResponseEntity.noContent().build()                // 204, no body
ResponseEntity.created(uri).body(product)         // 201, Location: uri, with a body
```

Two shapes to notice:

- Methods like `ok(...)` take the body directly.
- Methods like `notFound()` and `noContent()` return a **builder**: you can add headers to it, and you
  finish with **`.build()`** (no body) or **`.body(x)`** (with one). Forgetting `.build()` is a common
  compile error; the message will say something like "cannot convert HeadersBuilder to ResponseEntity".

The `<T>` is the type of the body: `ResponseEntity<Product>` for a product, and **`ResponseEntity<Void>`**
when there is never a body (note the capital V: `Void` is the "no type" type for generics).
:::

:::step{type=example title="Worked example: 201 with a Location"}
Here is a "create" done properly, for customers:

```java
@PostMapping("/customers")
public ResponseEntity<Customer> create(@RequestBody NewCustomer body) {
    Customer saved = customers.add(body.name(), body.email());
    URI location = URI.create("/customers/" + saved.id());    // where the new customer lives
    return ResponseEntity.created(location).body(saved);      // 201 + Location + body
}
```

- Save first, because the **id is only known after saving**.
- Build the address of the new thing from its id. **`URI`** (from `java.net`) is Java's type for an
  address; `URI.create("...")` makes one from text.
- `ResponseEntity.created(location)` sets status **201** *and* the `Location` header in one go.
  `.body(saved)` adds the new customer as the body.

The response:

```text
HTTP/1.1 201
Location: /customers/12
Content-Type: application/json

{"id":12,"name":"Asha","email":"asha@shop.in"}
```

You saw exactly this shape from the menu API in chapter 1. Now you know how it is made.
:::

:::step{type=task task=created_201 title="Your turn: 201 Created for new products"}
Change `create` so it returns a `ResponseEntity<Product>`: status `201`, a `Location` header of
`/products/{the new id}`, and the product as the body.

Imports: `org.springframework.http.ResponseEntity` and `java.net.URI`.

Rebuild, run, and POST again with `-i` to see the headers:

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "Poha", "pricePaise": 2200}'
```

```text
HTTP/1.1 201
Location: /products/4
Content-Type: application/json

{"id":4,"name":"Poha","pricePaise":2200,"costPaise":0}
```

Press **Check**.
:::

:::step{type=concept title="Choosing the status at run time"}
`ResponseEntity` really shines when the status **depends on what happened**. The delete endpoint is the
perfect case: the same request can succeed or find nothing.

```java
@DeleteMapping("/customers/{id}")
public ResponseEntity<Void> delete(@PathVariable long id) {
    if (customers.delete(id)) {
        return ResponseEntity.noContent().build();   // deleted: 204, nothing to send back
    }
    return ResponseEntity.notFound().build();        // nothing to delete: 404
}
```

Why **204** and not 200? After a delete there is nothing left to show, and `204 No Content` says precisely
"success, and intentionally no body". Clients then do not try to read one.

The `if` can also be written on one line with Java's **conditional operator**, `condition ? valueIfTrue : valueIfFalse`:

```java
return customers.delete(id) ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
```

Both are fine; choose whichever reads more clearly to you.
:::

:::step{type=task task=delete_204 title="Your turn: DELETE answers 204 or 404"}
Change `delete` to return a `ResponseEntity<Void>`: **`204`** when `repository.delete(id)` deleted
something (it returns `true`), and **`404`** when it did not.

Rebuild, run, and delete the samosa twice:

```bash run
curl -i -X DELETE localhost:8080/products/3; echo; curl -i -X DELETE localhost:8080/products/3
```

The first answers `204` with no body; the second `404`, because it is already gone. Press **Check**.
:::

:::step{type=concept title="Which status for what: a short guide"}
Here is the guide most good APIs follow. You do not have to memorise it; come back to it whenever you write
an endpoint:

- **GET** a thing: `200` with it, or `404` if it does not exist.
- **GET** a list: `200` with the list, even when the list is **empty** (an empty search result is not an
  error, so not 404).
- **POST** to create: `201` with `Location` and the new thing. Invalid input: `400` (chapter 16). Duplicate:
  `409 Conflict` (chapter 20).
- **PUT / PATCH**: `200` with the updated thing, or `404` (chapter 15).
- **DELETE**: `204`, or `404`.
- **Not logged in**: `401`. Logged in but not allowed: `403` (chapter 28).
- **Your code crashed**: `500`, which you never return on purpose; Spring produces it for unexpected
  exceptions, and chapter 17 makes sure it never leaks internal details.

`ResponseEntity` lets you return any of these. `ResponseStatusException` (chapter 11) is the other tool:
throwing it from deep inside your code turns into that status. Use `ResponseEntity` when the method itself
decides the outcome, and the exception when "this cannot continue" is discovered somewhere deeper.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A search for products under Rs 5 finds nothing. Which answer is right?
:::
- [ ] 404 Not Found
- [x] 200 with an empty list []
- [ ] 204 No Content
:::explain
The search worked, and its result is "none". 404 would mean the address `/products/search` itself does not
exist. Clients can show "no results" from an empty list.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which code compiles and answers 404 with no body?
:::
- [ ] return ResponseEntity.notFound();
- [x] return ResponseEntity.notFound().build();
- [ ] return ResponseEntity.ok(404);
:::explain
`notFound()` gives a builder; `.build()` finishes it into a `ResponseEntity`. `ok(404)` would answer 200 with
the number 404 as the body.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does a create answer include a Location header?
:::
- [ ] Browsers need it to show the page
- [x] It tells the client the address of the new thing, built from the id the server chose
- [ ] It is required for status 200
:::explain
Only the server knows the new id. `Location` hands the client the exact URL to fetch, update or delete the
new resource.
:::
:::

:::step{type=deep-dive title="Go deeper: @ResponseStatus, and building URIs properly"}
**@ResponseStatus.** For a method that always answers the same non-200 code, you can annotate it instead:
`@ResponseStatus(HttpStatus.CREATED)` on the method makes every successful call answer 201. It cannot add a
`Location` header, though, which is why `ResponseEntity.created(...)` is usually better for creates.

**Full URIs.** We wrote `Location: /products/4`, a relative address, which HTTP allows. To build an absolute
one (`http://api.myshop.in/products/4`) from the current request, Spring has
`ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}").buildAndExpand(id).toUri()`.

**Headers.** Any builder accepts more headers: `ResponseEntity.ok().header("Cache-Control", "max-age=60").body(x)`.
:::

:::step{type=recap title="What you can do now"}
Your endpoints now tell the truth:

- **`ResponseEntity<T>`** describes the whole response: status, headers, body. `ok(body)`, `created(uri).body(x)`,
  `noContent().build()`, `notFound().build()`, `status(...).body(x)`.
- Builders end with `.build()` (no body) or `.body(x)`; `ResponseEntity<Void>` when there is never a body.
- **Create**: `201` + `Location` (built with `URI.create`) + the new thing.
- **Delete**: `204`, or `404` when there was nothing; the status can be chosen at run time.
- An empty list is `200 []`, not 404.

:::photo{src="/lesson-images/spring/spring-13-notes.webp" alt="Handwritten notes about Status codes: ResponseEntity = status + headers + body, create: 201 + Location, delete: 204 or 404, empty list is 200 [], .build() or .body(x)" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 14: the controller is getting busy. Time to split the work into layers.
:::
