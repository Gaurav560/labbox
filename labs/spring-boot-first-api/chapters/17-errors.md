:::step{type=story title="Why this chapter"}
If each endpoint reports errors its own way, every client needs special code for every endpoint, and an
unhandled exception leaks as a 500 with Spring's default body. This chapter puts all error handling in
one class and answers every error in one standard format.

:::mission
In the `17-errors` folder: answer "not found" and validation errors as consistent `ProblemDetail`
responses, from one `@RestControllerAdvice`.
:::
:::

:::step{type=concept title="Exceptions in the service, responses in one place"}
The service layer should not know about HTTP. When a product does not exist, it throws an exception
that says so in domain terms:

```java
public Product get(long id) {
    return repository.findById(id).orElseThrow(() -> new ProductNotFoundException(id));
}
```

Without a handler, an exception that leaves a controller becomes **500 Internal Server Error**. A class
marked `@RestControllerAdvice` can handle exceptions from **every** controller in one place, with
methods marked `@ExceptionHandler(SomeException.class)`.

:::diagram{name="error-flow"}
The exception travels up to the advice, which turns it into one consistent response.
:::
:::

:::step{type=concept title="ProblemDetail, the standard error body"}
**RFC 9457** (Problem Details for HTTP APIs) defines a standard JSON error body. Spring supports it with
`ProblemDetail`:

```json
{
  "type": "about:blank",
  "title": "Product not found",
  "status": 404,
  "detail": "No product 99",
  "instance": "/products/99"
}
```

- `title`: a short summary of the kind of problem;
- `status`: the HTTP status code;
- `detail`: what happened in this case;
- extra properties (like a list of field errors) can be added with `setProperty`.

Spring sets the response's status code from the `ProblemDetail`.
:::

:::step{type=example title="Worked example: out of stock"}
```java
@RestControllerAdvice
public class ApiErrors {

    @ExceptionHandler(OutOfStockException.class)
    public ProblemDetail outOfStock(OutOfStockException e) {
        ProblemDetail p = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, e.getMessage());
        p.setTitle("Out of stock");
        p.setProperty("productId", e.productId());
        return p;
    }
}
```

1. The method handles `OutOfStockException` thrown from any controller or service below it.
2. `forStatusAndDetail` sets the status (409) and the detail text.
3. `setTitle` and `setProperty` complete the body. The response is 409 with that JSON.
:::

:::step{type=predict title="Guess first"}
:::question
`ProductService.get(99)` throws `ProductNotFoundException`, and there is no handler for it. What does the client receive?
:::
- [ ] 404 Not Found
- [x] 500 Internal Server Error
- [ ] 200 with an empty body
:::explain
Spring cannot know that this exception means "not found". Any unhandled exception becomes 500. The
handler is what maps it to 404.
:::
:::

:::step{type=try title="See the 500 before the fix"}
```bash run
cd 17-errors && mvn -q -o package -DskipTests && java -jar target/errors.jar
```

In a second tab:

```bash run
curl -si localhost:8080/products/99 | head -1
```
:::

:::step{type=task task=not_found_problem title="Warm-up: a ProblemDetail for not found"}
In `17-errors/src/main/java/com/shop/ApiErrors.java`, add an `@ExceptionHandler` for
`ProductNotFoundException` that answers 404 with a `ProblemDetail` titled `Product not found`, whose
detail is the exception's message.

`GET /products/99` then answers 404 with `"detail": "No product 99"`.
:::

:::step{type=concept title="Field errors from validation"}
When `@Valid` fails, Spring throws `MethodArgumentNotValidException`. Its binding result lists every
failed field:

```java
e.getBindingResult().getFieldErrors().forEach(f ->
        errors.put(f.getField(), f.getDefaultMessage()));
```

`getField()` is the field name (`pricePaise`), and `getDefaultMessage()` the constraint's message (for
`@Positive`, "must be greater than 0"). A map of these, added to the `ProblemDetail`, tells the client
exactly what to fix.
:::

:::step{type=task task=validation_problem title="A ProblemDetail for validation errors"}
In `ApiErrors`, handle `MethodArgumentNotValidException`: answer 400 with a `ProblemDetail` titled
`Invalid request`, and a property `errors` holding a map from each field name to its message.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why should `ProductService` throw `ProductNotFoundException` instead of returning a 404 response?
:::
- [ ] Exceptions are faster than responses
- [x] The service stays independent of HTTP; the advice decides how errors look on the web
- [ ] Services cannot return values
:::explain
The same service can be called from a scheduled job or a message listener, where HTTP status codes mean
nothing. Mapping to HTTP belongs at the web layer.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In a `ProblemDetail`, which field holds the case-specific message, like "No product 99"?
:::
- [ ] `title`
- [x] `detail`
- [ ] `type`
:::explain
`title` describes the kind of problem and is the same every time; `detail` describes this occurrence.
:::
:::

:::step{type=deep-dive title="Never leak internals"}
A handler for `Exception` (everything else) is a good final safety net: log the full error with its stack
trace on the server, and answer a generic 500 `ProblemDetail` without internal details. Stack traces,
SQL statements and class names in responses help attackers and confuse users. Spring Boot can also
produce `ProblemDetail` for its own errors with `spring.mvc.problemdetails.enabled=true`.
:::

:::step{type=recap title="Chapter done"}
- Services throw domain exceptions; `@RestControllerAdvice` maps them to HTTP responses for every controller.
- `ProblemDetail` (RFC 9457) is the standard error body: title, status, detail, and extra properties.
- Unhandled exceptions become 500; validation errors can list each field and its message.
:::
