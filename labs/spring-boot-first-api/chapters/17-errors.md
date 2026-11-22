:::step{type=story title="Errors are part of the API"}
When things go wrong, the client still needs an answer it can use. A phone app must be able to tell
"this product no longer exists" (show a friendly message) from "your form has two mistakes" (highlight the
fields) from "the server is broken" (try again later). That only works if errors come back **in one
predictable shape**, with enough detail, and without leaking the server's insides.

Right now the Shop API is not there yet. A missing product causes a **500** (as if the server broke), and a
validation failure says "Bad Request" without saying what was bad. This chapter fixes both, in one place,
for every controller at once, using the standard error format for HTTP APIs.

:::mission
Answer every missing product with a clear 404, and every invalid request with a 400 that lists each
field's problem, from one error-handling class.
:::
:::

:::step{type=concept title="See what the client gets today" file="17-errors/src/main/java/com/shop/product/ProductController.java" line="28-31"}
This chapter's project is layered (chapter 14): `ProductController` calls `ProductService`, and when a
product does not exist, the service **throws** a `ProductNotFoundException`. That is good design: the service
says "this product does not exist" in business terms, with no idea about HTTP.

But nobody translates that exception into HTTP. Start the app and ask for a missing product:

```bash run
cd 17-errors && mvn -q -o package -DskipTests && java -jar target/errors.jar
```

```bash run
curl -i localhost:8080/products/99
```

```text
HTTP/1.1 500
{"timestamp":"...","status":500,"error":"Internal Server Error","path":"/products/99"}
```

**500 Internal Server Error**: "the server is broken". It is not; the client asked for something that does not
exist, which is a 404. And look at Terminal 1: a long **stack trace** in the log, the kind of alarm that wakes
up the on-call engineer at night, for a perfectly normal situation.

Any exception your code does not handle becomes a 500. So: we need to handle them.
:::

:::step{type=concept title="One place for every error: @RestControllerAdvice" file="17-errors/src/main/java/com/shop/ApiErrors.java" line="5-14"}
You could catch the exception in every controller method with `try`/`catch`. Thirty endpoints, thirty
copies, thirty chances to answer differently.

Spring offers a single place instead: a class marked **`@RestControllerAdvice`**. It "advises" all the
controllers: when any controller method throws, Spring looks in the advice class for a method that handles
that exception type, and uses it to build the response.

```java
@RestControllerAdvice
public class ApiErrors {

    @ExceptionHandler(CustomerNotFoundException.class)
    public ProblemDetail customerNotFound(CustomerNotFoundException e) {
        ...   // build the error answer
    }
}
```

- **`@ExceptionHandler(X.class)`** on a method means: "call me when a controller throws an `X`".
- The method receives the exception as its parameter, so it can use its message and data.
- Whatever it returns becomes the response, exactly like a controller method.

`ApiErrors.java`, on the right, is already a `@RestControllerAdvice`, with a TODO for each handler.
:::

:::step{type=concept title="The standard error shape: ProblemDetail"}
What should an error look like? There is an official standard for HTTP APIs, **RFC 9457, "Problem Details"**,
and Spring supports it directly with the class **`ProblemDetail`**. A problem looks like this:

```json
{
  "type": "about:blank",
  "title": "Product not found",
  "status": 404,
  "detail": "No product 99",
  "instance": "/products/99"
}
```

- **`title`**: a short, fixed summary of the *kind* of problem. The same for every missing product.
- **`status`**: the HTTP status, repeated in the body for convenience.
- **`detail`**: the explanation for *this* occurrence ("No product 99").
- **`instance`**: which request it was (Spring fills in the path).
- **`type`**: a link to documentation about this kind of problem; `about:blank` when there is none.

The response also gets a special content type, `application/problem+json`, so clients can recognise an error
body without even reading it. And you can add your **own fields** (like the list of invalid fields, coming
up). Using a standard means every client developer, and every tool, already knows how to read your errors.
:::

:::step{type=example title="Worked example: a handler for a missing customer"}
```java
@ExceptionHandler(CustomerNotFoundException.class)
public ProblemDetail customerNotFound(CustomerNotFoundException e) {
    ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
    problem.setTitle("Customer not found");
    return problem;
}
```

- **`ProblemDetail.forStatusAndDetail(status, detail)`** creates a problem with a status and a detail. The
  detail comes from the exception's message (`"No customer 42"`).
- **`setTitle(...)`** sets the fixed summary.
- Returning the `ProblemDetail` is enough: Spring uses its status for the response and writes it as JSON.

Notice what the service and the controller never had to do: nothing. The service throws, the controller
does not catch, and this one method turns it into a correct 404 for **every** endpoint that can lose a
customer.
:::

:::step{type=task task=not_found_problem title="Your turn: a 404 problem for missing products"}
In `ApiErrors`, add a handler for **`ProductNotFoundException`**: a `ProblemDetail` with status **404**, the
exception's message as the detail, and the title **`Product not found`**.

Imports: `ExceptionHandler` (`org.springframework.web.bind.annotation`), `ProblemDetail` and `HttpStatus`
(`org.springframework.http`), and `com.shop.product.ProductNotFoundException`.

Rebuild, run, and ask for product 99 again:

```bash run
curl -i localhost:8080/products/99
```

```text
HTTP/1.1 404
Content-Type: application/problem+json

{"type":"about:blank","title":"Product not found","status":404,"detail":"No product 99","instance":"/products/99"}
```

And no stack trace in the log. Press **Check**.
:::

:::step{type=concept title="Validation errors, with every field"}
Chapter 16 ended with a promise: the validation failure (`MethodArgumentNotValidException`) holds every
field that failed, and the client deserves to see them. Here is how to read them:

```java
e.getBindingResult().getFieldErrors()   // a List<FieldError>, one per failed rule
```

Each `FieldError` has **`getField()`** (the field's name, like `"name"`) and **`getDefaultMessage()`** (the
rule's message, like `"must not be blank"`). Turn them into a map from field name to message, and add it to
the problem as an extra property:

```java
Map<String, String> errors = new LinkedHashMap<>();
e.getBindingResult().getFieldErrors()
        .forEach(f -> errors.put(f.getField(), f.getDefaultMessage()));

ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
problem.setTitle("Invalid request");
problem.setProperty("errors", errors);
```

- **`forStatus`** creates a problem with only a status (there is no single detail for several errors).
- **`setProperty(name, value)`** adds your own field to the JSON.
- A **`LinkedHashMap`** keeps the order you put things in (a plain `HashMap` does not promise any order).

The client then receives:

```json
{"type":"about:blank","title":"Invalid request","status":400,"instance":"/products",
 "errors":{"name":"must not be blank","pricePaise":"must be greater than 0"}}
```

A form can now put each message right next to its field.
:::

:::step{type=task task=validation_problem title="Your turn: a 400 problem that lists every field"}
In `ApiErrors`, add a handler for **`MethodArgumentNotValidException`** (from
`org.springframework.web.bind`): status **400**, title **`Invalid request`**, and a property **`errors`**: a map
from each field name to its message.

Rebuild, run, and send an invalid product:

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "", "pricePaise": -1}'
```

You should see `400`, `application/problem+json`, and both fields in `errors`. Press **Check**.
:::

:::step{type=concept title="What about bugs? The 500 that does not leak"}
Some exceptions are real bugs: a `NullPointerException` you did not expect. Those *should* be 500. But be
careful what a 500 tells the outside world. A stack trace, a database error text or a file path in a
response is a gift to an attacker: it reveals which libraries you use and how your code is structured.

Spring Boot's default 500 body is safe (`"error":"Internal Server Error"`, no stack trace). If you add a
handler for `Exception` (the catch-all), keep it that way:

```java
@ExceptionHandler(Exception.class)
public ProblemDetail unexpected(Exception e) {
    log.error("Unexpected error", e);                         // the details go to YOUR logs
    ProblemDetail p = ProblemDetail.forStatus(HttpStatus.INTERNAL_SERVER_ERROR);
    p.setTitle("Something went wrong");                       // the client gets no details
    return p;
}
```

Log everything (with the request id from chapter 18, you can find it later); tell the client nothing about
the inside. Spring picks the **most specific** handler for an exception, so this catch-all only applies to
exceptions no other handler covers.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A service throws `OrderNotFoundException`, and no handler exists for it. What does the client get?
:::
- [ ] 404 Not Found
- [x] 500 Internal Server Error
- [ ] 400 Bad Request
:::explain
Spring has no idea what your exception means. Unhandled exceptions are 500. An `@ExceptionHandler` in the
advice class is how you say "this one means 404".
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`ApiErrors` handles `ProductNotFoundException`. A new `ReviewController` also throws it. Does it get the 404 problem?
:::
- [x] Yes: the advice applies to every controller
- [ ] No: each controller needs its own handler
- [ ] Only if ReviewController extends ApiErrors
:::explain
That is the point of `@RestControllerAdvice`: one class, applied to all controllers. Every endpoint answers
errors the same way.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why should a 500 response not include the exception's stack trace?
:::
- [ ] It makes the response too slow
- [x] It reveals internal details (libraries, code structure, sometimes data) to anyone
- [ ] JSON cannot hold a stack trace
:::explain
Internal details help attackers and confuse users. Log them on the server, with a request id; send the
client a short, generic problem.
:::
:::

:::step{type=deep-dive title="Go deeper: ErrorResponseException, and spring.mvc.problemdetails"}
**Exceptions that carry their status.** Your own exception can extend Spring's `ErrorResponseException` and
build its `ProblemDetail` itself; then no handler is needed. Handlers in one advice class are often easier to
read, though, because all error answers are in one place.

**Spring's own errors as problems.** Spring itself raises many exceptions (405, 415, unreadable JSON...). With
`spring.mvc.problemdetails.enabled=true`, Spring Boot answers all of those as `ProblemDetail` too, so your API
is consistent even for errors you did not write. Or extend `ResponseEntityExceptionHandler` in your advice
class for full control.

**The type field.** Mature APIs point `type` to a documentation page per problem kind
(`https://api.myshop.in/problems/out-of-stock`), so client developers can look up what to do.
:::

:::step{type=recap title="What you can do now"}
Your API now fails clearly and consistently:

- An **unhandled exception is a 500**. Business exceptions (like "not found") need a handler.
- **`@RestControllerAdvice`** + **`@ExceptionHandler(X.class)`**: one class that turns exceptions from every
  controller into responses.
- **`ProblemDetail`** (RFC 9457): `title`, `status`, `detail`, `instance`, `type`, plus your own properties
  with `setProperty`; sent as `application/problem+json`.
- Validation failures: read `getBindingResult().getFieldErrors()` into a field-to-message map, and return a
  400 problem with it.
- Unexpected errors: log the details on the server, give the client a short, generic 500.

:::photo{src="/lesson-images/spring/spring-17-notes.webp" alt="Handwritten notes about Errors: unhandled exception = 500, @RestControllerAdvice, @ExceptionHandler(X.class), ProblemDetail: title, status, detail, log details, show a short 500" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 18: code that runs around every request, with filters and interceptors.
:::
