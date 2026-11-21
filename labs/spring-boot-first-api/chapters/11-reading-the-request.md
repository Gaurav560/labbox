:::step{type=story title="Listening to the request"}
Your endpoints so far have ignored the request almost completely: `GET /hello` always says hello, `GET /merchants` always returns the
same list. Real endpoints depend on what the client asks: *which* product, products *cheaper than* what,
sorted *how*.

A request carries that information in a few places: **in the path** (`/products/2`), **in the query
string** (`?maxPrice=2500&sort=price`) and **in headers**. (The body is the fourth place; it gets its own
chapter, 12.) This chapter teaches you to read each one into a plain Java parameter, and what Spring does
when the client sends something that does not fit.

:::mission
Add `GET /products/{id}` (with a proper 404) and `GET /products/search` with optional filters.
:::
:::

:::step{type=concept title="The project" file="11-reading-the-request/src/main/java/com/shop/product/ProductController.java" line="8-27"}
`ProductController` is on the right, with a `ProductRepository` that holds four products:

```text
1 Masala tea      2000 paise
2 Filter coffee   3000
3 Samosa          1800
4 Paneer roll     9000
```

`GET /products` returns them all. There are two TODOs, one per task. Before we write them, let's learn the
three tools: `@PathVariable`, `@RequestParam` and `@RequestHeader`.
:::

:::step{type=concept title="Values in the path: @PathVariable"}
In REST, one specific thing gets its own address: product 2 lives at `/products/2`. You do not want to
write a method per product, so the mapping uses a **placeholder** in curly braces:

```java
@GetMapping("/customers/{id}")
public Customer one(@PathVariable long id) {
    ...
}
```

`{id}` in the mapping matches **any one segment** of the path (one piece between slashes):
`/customers/7`, `/customers/250`, even `/customers/abc`. **`@PathVariable`** then hands that piece to the
parameter with the **same name**, `id`.

Notice the parameter type is `long`, but the path is text. Spring **converts** it for you. And if the text
cannot be converted (`/customers/abc` into a `long`), Spring does not even call your method: it answers
**400 Bad Request** by itself. Your method only ever receives a valid number.

A path can have several placeholders: `@GetMapping("/customers/{customerId}/orders/{orderId}")` with two
`@PathVariable` parameters.
:::

:::step{type=concept title="When the thing does not exist: 404"}
`/products/99` is a valid number, so it reaches your method. But there is no product 99. What should the
method do?

Not return `null`: Spring would answer `200` with an empty body, which tells the client "here it is, and
it is nothing". That is a lie. The honest answer is **404 Not Found**.

One way to produce it: **throw a `ResponseStatusException`**:

```java
@GetMapping("/customers/{id}")
public Customer one(@PathVariable long id) {
    return customers.findById(id)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No customer " + id));
}
```

Read it from the inside out. `findById` returns an **`Optional`**: a box that either holds the customer or
is empty. **`orElseThrow`** says "give me what is in the box, or, if it is empty, throw this exception".
And `ResponseStatusException` is a special exception that Spring catches and turns into a response with
that status code.

So: found, return it (200 + JSON). Not found, throw (404). Your method stays one clear expression. (In
chapter 13 you will meet `ResponseEntity`, the other way to choose a status; chapter 17 shows how to give
every error a consistent JSON body.)
:::

:::step{type=example title="Worked example: finding one item in a list"}
Our repository has no `findById`; it only has `findAll()`. So the controller must look through the list
itself. Streams do this nicely:

```java
Optional<Customer> found = customers.findAll().stream()   // every customer, one by one
        .filter(c -> c.id() == id)                        // keep only the one with this id
        .findFirst();                                     // the first that is left, as an Optional
```

- **`filter`** keeps only the items for which the test is true. `c -> c.id() == id` is a **lambda**: a
  small function written inline, "given a customer `c`, is its id equal to `id`?".
- **`findFirst`** returns the first remaining item, wrapped in an `Optional`, because there might be none.

Then `.orElseThrow(...)` from the previous step finishes the job.

:::trace{title="filter(c -> c.id() == 3) on four customers"}
| customer | c.id() == 3? | kept? |
|---|---|---|
| id 1, Asha | false | no |
| id 2, Ravi | false | no |
| id 3, Meera | true | yes |
| id 4, Kabir | false | no (findFirst already has one) |
:::
:::

:::step{type=task task=product_by_id title="Your turn: GET /products/{id}"}
At the first TODO, add **`GET /products/{id}`**: it returns the product with that id, and answers **404**
(with a `ResponseStatusException`) when there is none.

Imports you will need: `PathVariable` (in `org.springframework.web.bind.annotation`), `HttpStatus`
(`org.springframework.http`) and `ResponseStatusException` (`org.springframework.web.server`).

Build, run, and try a found product, a missing one, and nonsense:

```bash run
cd 11-reading-the-request && mvn -q -o package -DskipTests && java -jar target/reading-the-request.jar
```

```bash run
curl -i localhost:8080/products/2; echo; curl -i localhost:8080/products/99; echo; curl -i localhost:8080/products/abc
```

You should get `200` with the filter coffee, `404`, and `400` (Spring could not turn `abc` into a number,
so your method never ran). Press **Check**.
:::

:::step{type=concept title="Values in the query string: @RequestParam"}
The query string carries **options**: filters, sorting, pages. `GET /products/search?maxPrice=2500&sort=price`
has two parameters, `maxPrice` and `sort`. **`@RequestParam`** reads them:

```java
@GetMapping("/books/search")
public List<Book> search(@RequestParam String author) { ... }
```

`GET /books/search?author=Premchand` calls the method with `author = "Premchand"`. As with path variables,
the parameter's name is the query parameter's name, and Spring converts the text to the parameter's type
(`int`, `long`, `boolean`...), answering 400 if it cannot.

But query parameters are usually **optional**. By default, `@RequestParam` is **required**: a request
without it gets **400**. Two ways to make it optional:

```java
@RequestParam(required = false) Integer maxPages      // missing -> null
@RequestParam(defaultValue = "title") String sort     // missing -> "title"
```

- `required = false` gives `null` when the parameter is missing. That only works with **object** types
  (`Integer`, not `int`, which cannot be null), the same idea you will meet again in chapter 15.
- `defaultValue` gives a value when it is missing, so the parameter is never null.

Use `null` when "missing" means "no filter at all", and a default when there is a sensible normal choice.
:::

:::step{type=example title="Worked example: optional filters and a chosen order"}
Here is a book search with an optional maximum page count and a choice of sort order:

```java
@GetMapping("/books/search")
public List<Book> search(@RequestParam(required = false) Integer maxPages,
                         @RequestParam(defaultValue = "title") String sort) {
    Comparator<Book> order = sort.equals("pages")
            ? Comparator.comparingInt(Book::pages)          // fewest pages first
            : Comparator.comparing(Book::title);            // A to Z
    return books.findAll().stream()
            .filter(b -> maxPages == null || b.pages() <= maxPages)   // no limit when missing
            .sorted(order)
            .toList();
}
```

The new pieces:

- A **`Comparator`** says how to order two items. `Comparator.comparing(Book::title)` orders by title,
  `Comparator.comparingInt(Book::pages)` by the page count, smallest first. `.sorted(order)` uses it.
- The filter `maxPages == null || b.pages() <= maxPages` reads: "keep the book if there is no limit, *or*
  if it is within the limit". Because of `||`, when `maxPages` is null, the second part is never checked
  (good: comparing with null would crash).

Every combination now works: no parameters, one, or both.
:::

:::step{type=task task=search_products title="Your turn: GET /products/search"}
At the second TODO, add **`GET /products/search`** with two optional query parameters:

- `maxPrice` (paise): only products with a price **less than or equal** to it; no limit when it is missing;
- `sort`: `name` (the default, A to Z) or `price` (lowest first).

Rebuild, run, and try a few combinations:

```bash run
curl "localhost:8080/products/search?maxPrice=2500"; echo; curl "localhost:8080/products/search?sort=price"; echo; curl -i "localhost:8080/products/search?maxPrice=cheap"
```

(The quotes around the URL matter: without them, your shell would treat `&` as a command of its own.)

You should get the masala tea and the samosa (sorted by name), then all four from cheapest to dearest,
then a `400`, because `cheap` is not a number. Press **Check**.
:::

:::step{type=concept title="Two routes that look alike"}
You now have both `/products/{id}` and `/products/search`. But `{id}` matches *any* segment, including the
word `search`. So why does `GET /products/search` not go to the id method (and fail with 400, since
`search` is not a number)?

Because the handler mapping picks the **most specific** match. A route with a fixed word (`/products/search`)
beats a route with a placeholder (`/products/{id}`) for the same path. So `/products/search` goes to
`search()`, and `/products/2` goes to the id method.

This also tells you something about designing APIs: keep the fixed words and the placeholders easy to tell
apart, so both humans and Spring read your routes the same way.
:::

:::step{type=concept title="Values in headers: @RequestHeader"}
The last place a request carries information is its **headers**. You will rarely need them in business
code, but some APIs read things like the client's app version or language:

```java
@GetMapping("/welcome")
public String welcome(@RequestHeader(value = "Accept-Language", defaultValue = "en") String language) {
    return language.startsWith("hi") ? "Swagat hai!" : "Welcome!";
}
```

**`@RequestHeader`** works just like `@RequestParam`: name, `required`, `defaultValue`. Header names are not
case-sensitive (`accept-language` is the same header).

Try `curl -H "Accept-Language: hi" ...` against an endpoint like that, and you would get the Hindi
greeting. Things like logins (chapter 28) also arrive in a header, `Authorization`, but Spring Security
reads that one for you.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A method has `@RequestParam int page` (no options). What happens for `GET /orders` with no `?page=`?
:::
- [ ] page is 0
- [ ] page is null
- [x] 400 Bad Request: the parameter is required by default
:::explain
`@RequestParam` is required unless you add `required = false` or a `defaultValue`. And an `int` could not
hold null anyway; use `Integer` with `required = false`, or `defaultValue = "0"`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`GET /products/abc` reaches a method with `@PathVariable long id`. What happens?
:::
- [ ] The method runs with id = 0
- [x] Spring answers 400 itself; the method never runs
- [ ] 404 Not Found
:::explain
Spring converts the path text to the parameter type first. `abc` is not a `long`, so the request is
rejected as bad input before your code is involved.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Your method finds no product and returns `null`. What does the client receive?
:::
- [ ] 404 Not Found
- [x] 200 with an empty body: Spring does not treat null as "not found"
- [ ] 500 Internal Server Error
:::explain
Returning null means "here is the answer, and it is empty". To say "not found", throw a
`ResponseStatusException(HttpStatus.NOT_FOUND, ...)` or return a `ResponseEntity` with 404 (chapter 13).
:::
:::

:::step{type=deep-dive title="Go deeper: lists of values, and many options at once"}
**Many values.** `GET /products?tag=veg&tag=snack` can be read with `@RequestParam List<String> tag`.

**Many parameters at once.** When a search has many options, put them in a record and drop the annotation:
`public List<Product> search(ProductFilter filter)`, where `ProductFilter(Integer maxPrice, String sort,
String category)`. Spring fills the record's fields from the query parameters with the same names.

**Optional instead of null.** `@RequestParam Optional<Integer> maxPrice` also works, if you prefer
`Optional` to null checks.

**Validation.** Values like `maxPrice=-5` pass conversion but make no sense. Chapter 16 adds rules such as
`@Min(0)` so Spring rejects them with a clear 400.
:::

:::step{type=recap title="What you can do now"}
You can now read everything a request carries outside its body:

- **`@PathVariable`** reads a `{placeholder}` from the path; **`@RequestParam`** reads a query parameter;
  **`@RequestHeader`** reads a header. The parameter name matches the name in the request.
- Spring **converts** text to your parameter's type, and answers **400** itself when it cannot.
- `@RequestParam` is **required** unless you add `required = false` (gives `null`, use object types) or
  `defaultValue`.
- Not found? Throw **`ResponseStatusException(HttpStatus.NOT_FOUND, ...)`**, never return null.
- Streams: `filter` with a lambda, `findFirst` to an `Optional`, `orElseThrow`, and a `Comparator` for
  `sorted`.
- A fixed route (`/products/search`) beats a placeholder route (`/products/{id}`).

Next, chapter 12: the fourth place, the request body, where clients send whole JSON objects.
:::
