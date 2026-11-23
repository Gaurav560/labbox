:::step{type=story title="Things change"}
So far the Shop API can list products, show one, create new ones and delete them. But shops change their
products all the time: the custard gets a bigger bowl and a new price, the samosa price goes up by two
rupees, a delivery arrives and the stock goes up.

HTTP has two methods for changing something that already exists, **PUT** and **PATCH**, and the
difference between them matters more than it looks. Using the wrong one, or implementing it wrongly, is how
APIs quietly wipe out data. This chapter builds both, carefully.

:::mission
Add `PUT /products/{id}` to replace a product, and `PATCH /products/{id}` to change only some of its fields.
:::
:::

:::step{type=concept title="The project: products, with a repository" file="15-updating-and-deleting/src/main/java/com/shop/product/ProductController.java" line="15-38"}
`ProductController` has opened on the right. It already has what you built in earlier chapters:

- `@RequestMapping("/products")` on the class (chapter 10), so every path below starts with `/products`.
- `GET /products` and `GET /products/{id}`.
- `DELETE /products/{id}`: `204 No Content` when it deleted something, `404` when there was nothing to
  delete (chapter 13).

One small new thing in `one()`: **`ResponseEntity.of(optional)`**. `findById` returns an `Optional`, a box
that either holds a product or is empty. `ResponseEntity.of` turns a full box into `200` with the product,
and an empty box into `404`. It is a one-line shortcut for the `map(...).orElse(...)` you wrote in
chapter 13.

The products live in `ProductRepository`, in memory, keyed by id. (To keep this chapter about HTTP, the
controller talks to the repository directly; in chapter 14 you saw where a service would sit in between.)
:::

:::step{type=concept title="PUT: replace the whole thing"}
**PUT** means: "here is the **complete** new version of this thing; replace whatever is there with it".

```text
PUT /products/2
Content-Type: application/json

{"name": "Fruit custard (large)", "pricePaise": 3500, "stock": 20}
```

The client sends **every field**. The server throws away the old version and stores this one, under the
id from the path. Afterwards, `GET /products/2` returns exactly what was PUT.

Three rules for a correct PUT:

1. **The id comes from the path**, never from the body. That is why `ProductInput` (the body's type) has no
   `id` field at all: a client cannot accidentally (or deliberately) change a product's id.
2. **A missing field is not "unchanged".** PUT means "this is the whole product". If the client leaves
   out `stock`, the new product has no stock value, which for an `int` means 0. That is correct PUT
   behaviour, and exactly why PATCH exists.
3. **Unknown id: 404.** Some APIs let PUT create a new thing at that id, but for products with
   server-chosen ids, PUT on an id that does not exist should answer 404. Creating is POST's job.

PUT is also **idempotent** (chapter 1): sending the same PUT twice leaves the product in the same state as
sending it once. That makes it safe for a client to retry after a network error.
:::

:::step{type=example title="Worked example: PUT for a customer's address"}
Here is a PUT on a different resource, step by step:

```java
public record AddressInput(String line1, String city, String pin) { }

@PutMapping("/customers/{id}/address")
public ResponseEntity<Address> replaceAddress(@PathVariable long id, @RequestBody AddressInput in) {
    if (customers.findById(id).isEmpty()) {
        return ResponseEntity.notFound().build();                  // 1. unknown customer: 404
    }
    Address saved = addresses.save(new Address(id, in.line1(), in.city(), in.pin()));   // 2. replace it all
    return ResponseEntity.ok(saved);                               // 3. 200 with the new version
}
```

1. **`@PutMapping`** with a path variable for the id, and **`@RequestBody`** for the new version (both
   from chapters 11 and 12).
2. If the customer does not exist, stop with 404.
3. Build the new object **from the path's id and the body's fields**, save it (replacing the old one),
   and answer 200 with what was saved.

Answering with the saved object is a courtesy to the client: it sees the final state without a second GET.
:::

:::step{type=task task=put_product title="Your turn: PUT /products/{id}"}
At the first TODO in `ProductController`, add **`PUT /products/{id}`**:

- the body is a `ProductInput`;
- if there is no product with that id, answer `404`;
- otherwise save `new Product(id, ...)` with the id from the path and every field from the body, and
  answer `200` with it.

Build, run and try it:

```bash run
cd 15-updating-and-deleting && mvn -q -o package -DskipTests && java -jar target/updating.jar
```

```bash run
curl -i -X PUT localhost:8080/products/2 -H "Content-Type: application/json" -d '{"name": "Fruit custard (large)", "pricePaise": 3500, "stock": 20}'
```

Now see rule 2 for yourself: PUT again **without** `stock`:

```bash run
curl -X PUT localhost:8080/products/2 -H "Content-Type: application/json" -d '{"name": "Fruit custard (large)", "pricePaise": 3500}'
```

```text
{"id":2,"name":"Fruit custard (large)","pricePaise":3500,"stock":0}
```

The stock is now 0. Not a bug in your code: that is what "replace the whole thing" means. Press **Check**.
:::

:::step{type=concept title="PATCH: change only what is sent"}
Usually a client wants to change **one thing**: just the price. With PUT it would have to fetch the
product first, change the price, and send everything back. And if two staff members do that at the same
time, one silently undoes the other's change.

**PATCH** means: "change **only these fields**; leave everything else alone".

```text
PATCH /products/1
Content-Type: application/json

{"pricePaise": 2200}
```

After this, product 1 has the new price, and its name and stock are untouched.

The challenge is on the server: how does Java know which fields were **sent** and which were **not**? Look
at `ProductPatch.java` in the project:

```java
public record ProductPatch(String name, Integer pricePaise, Integer stock) { }
```

The numbers are **`Integer`**, not `int`. An `int` can never be empty: a field missing from the JSON
becomes `0`, and you cannot tell "the client wants stock 0" from "the client did not mention stock". An
`Integer` is an object, and a missing field leaves it **`null`**. So the rule in your code becomes simple:
**null means "keep the old value"**.

(`String` is already an object, so a missing `name` is `null` too.)
:::

:::step{type=example title="Worked example: PATCH for a customer"}
Here is PATCH on a customer, who has a name and a phone number:

```java
public record CustomerPatch(String name, String phone) { }

@PatchMapping("/customers/{id}")
public ResponseEntity<Customer> patch(@PathVariable long id, @RequestBody CustomerPatch patch) {
    return customers.findById(id).map(old -> {
        Customer updated = new Customer(id,
                patch.name() != null ? patch.name() : old.name(),      // sent? use it. Not sent? keep it.
                patch.phone() != null ? patch.phone() : old.phone());
        return ResponseEntity.ok(customers.save(updated));
    }).orElse(ResponseEntity.notFound().build());
}
```

Read the pattern `patch.name() != null ? patch.name() : old.name()`. It is Java's **conditional
operator**: `condition ? valueIfTrue : valueIfFalse`. For each field: if the patch has a value, take it;
otherwise keep the old one.

And the `findById(id).map(old -> ...).orElse(...)` shape you know from chapter 13: if the customer exists,
build and save the updated one and answer 200; if not, 404.

:::trace{title="PATCH /customers/7 with {\"phone\": \"9876500000\"}"}
| field | old value | in the patch | new value |
|---|---|---|---|
| id | 7 | (from the path) | 7 |
| name | Asha | null: not sent | Asha |
| phone | 9123400000 | 9876500000 | 9876500000 |
:::
:::

:::step{type=task task=patch_price title="Your turn: PATCH /products/{id}"}
At the second TODO, add **`PATCH /products/{id}`** with a `ProductPatch` body: each field that is not
`null` replaces the old value, each `null` keeps it. Answer `200` with the updated product, or `404` if
there is no such product.

Rebuild, run, and change just the price of the mango kulfi:

```bash run
curl -X PATCH localhost:8080/products/1 -H "Content-Type: application/json" -d '{"pricePaise": 2200}'
```

```text
{"id":1,"name":"Mango kulfi","pricePaise":2200,"stock":40}
```

The price changed; the name and the stock (40) did not. Press **Check**.
:::

:::step{type=concept title="DELETE, once more, and what to answer"}
You already have `DELETE /products/{id}`. A few points to round off the picture of changing data:

- **204 No Content** is the usual answer to a successful DELETE: there is nothing left to show.
- **DELETE is idempotent**: deleting product 3 twice leaves it deleted. The *second* DELETE answers 404
  (it is not there), and that is fine; the state of the server is the same either way.
- In real shops, products are often not truly deleted but **marked** inactive, because old orders still
  refer to them. That is called a **soft delete**. The API still says `DELETE`; the database keeps a
  record. You will see why that matters once orders and products are linked, in chapter 21.

Here is the full picture of a REST resource, which the Shop API's products now have:

```text
GET    /products        list them
GET    /products/{id}   read one                      200 or 404
POST   /products        create one                    201 + Location
PUT    /products/{id}   replace one (every field)     200 or 404
PATCH  /products/{id}   change some fields            200 or 404
DELETE /products/{id}   remove one                    204 or 404
```
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A product has name "Samosa", price 1800 and stock 60. A client sends `PUT /products/3` with `{"name": "Samosa", "pricePaise": 2000}`. What is the stock afterwards?
:::
- [ ] 60: PUT keeps fields that were not sent
- [x] 0: PUT replaces the whole product, and the missing stock becomes 0
- [ ] The request is rejected
:::explain
PUT means "this is the complete new version". A missing field is part of the new version too, as its
default. To change only the price, use PATCH. (Chapter 16's validation can also reject PUT bodies with
missing fields.)
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why does `ProductPatch` use `Integer pricePaise` instead of `int pricePaise`?
:::
- [ ] Integer is faster
- [x] A missing field becomes null with Integer, but 0 with int, so you could not tell "not sent" from zero
- [ ] Jackson cannot read int
:::explain
Objects can be null; primitives like `int` cannot. For a PATCH, null is exactly the signal you need: "the
client did not send this field".
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Which of these requests are idempotent (sending it twice has the same effect as once)?
:::
- [ ] POST /products and PUT /products/2
- [x] PUT /products/2 and DELETE /products/2
- [ ] Only GET requests
:::explain
PUT stores the same complete version again; DELETE leaves the product deleted. POST creates a second
product. (PATCH can go either way: "set price to 2200" is idempotent, "add 5 to stock" is not.)
:::
:::

:::step{type=deep-dive title="Go deeper: concurrent changes, and JSON Merge Patch"}
**Two people, one product.** Two staff members load product 1, both change it, both PUT. The second PUT
silently overwrites the first change: a **lost update**. The standard fix is **optimistic locking**: the
product carries a version number, the client sends it back, and the server refuses (409 Conflict) if the
version has changed meanwhile. HTTP has headers for exactly this (`ETag` and `If-Match`), and JPA has
`@Version` (Part 3 and the production course).

**Standards for PATCH bodies.** What we built is close to **JSON Merge Patch** (RFC 7396): send the fields to
change. There is also **JSON Patch** (RFC 6902), a list of operations like
`[{"op": "replace", "path": "/pricePaise", "value": 2200}]`, which can also express things like "remove
this field" or "add to this list". Most APIs use the simpler merge style.
:::

:::step{type=recap title="What you can do now"}
Products in the Shop API now have the full set of operations:

- **PUT** replaces the **whole** resource: id from the path, every field from the body, a missing field
  becomes its default, unknown id is 404. It is idempotent.
- **PATCH** changes **only the fields sent**: use object types (`Integer`, `String`) so a missing field is
  `null`, and keep the old value for each `null`.
- `condition ? a : b` picks a value; `ResponseEntity.of(optional)` answers 200 or 404 from an Optional.
- **DELETE** answers 204, is idempotent, and real systems often soft-delete instead.

:::photo{src="/lesson-images/spring/spring-15-notes.webp" alt="Handwritten notes about Updating and deleting: PUT replaces the whole thing, PATCH changes only what is sent, Integer, not int: null = not sent, DELETE: 204, idempotent, soft delete in real systems" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 16: never trust a request body. Validation, done properly.
:::
