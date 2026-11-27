:::step{type=story title="Never trust the request"}
Right now, the Shop API accepts anything. A product with an empty name? Saved. A price of minus five rupees?
Saved. A customer whose email is "hello" and whose phone is "12"? Saved. Every one of those will cause
trouble later: an empty line on the menu, a negative bill, an email that bounces, an SMS that never arrives.

Clients make mistakes, and some clients are not friendly at all. The rule every backend lives by is: **check
everything that comes in, before using it.** Spring makes this almost effortless with **Bean Validation**:
you write the rules as annotations on your input classes, and Spring checks every request against them
before your method ever runs.

:::mission
Reject bad products and bad customers with a clear 400, using validation annotations.
:::
:::

:::step{type=concept title="See the problem first" file="16-validation/src/main/java/com/shop/product/NewProduct.java" line="3-5"}
`NewProduct` is on the right: a name and a price, no rules at all. Start the app and send it nonsense:

```bash run
cd 16-validation && mvn -q -o package -DskipTests && java -jar target/validation.jar
```

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "", "pricePaise": -5}'
```

```text
HTTP/1.1 201
Location: /products/4

{"id":4,"name":"","pricePaise":-5,"costPaise":0}
```

That is what our lab machine answered: `201 Created`. The shop now sells a nameless product for minus five paise. Every client of the API can do
this. Let's close the door.
:::

:::step{type=concept title="Rules as annotations: Bean Validation"}
**Bean Validation** (the `jakarta.validation` standard, provided by a library called Hibernate Validator) lets
you write rules directly on the fields of a class. The validation starter, `spring-boot-starter-validation`,
is already in this project's pom.

Here is a customer address with rules:

```java
public record NewAddress(
        @NotBlank @Size(max = 100) String line1,
        @NotBlank String city,
        @Pattern(regexp = "[0-9]{6}") String pin,
        @Min(1) @Max(5) int floor) {
}
```

Read each annotation as a sentence about its field:

- `line1` must **not be blank** (not null, not empty, not only spaces), and at most **100 characters**.
- `city` must not be blank.
- `pin` must **match the pattern** "exactly six digits".
- `floor` must be **between 1 and 5**.

The rules sit right next to the data they protect, so anyone reading the class sees exactly what a valid
address is. That is documentation and enforcement in one place.
:::

:::step{type=concept title="The annotations you will use most"}
A reference you can come back to. All come from `jakarta.validation.constraints`:

- **`@NotNull`**: must be present (not null). Empty text is allowed.
- **`@NotBlank`**: text must have at least one non-space character. The usual choice for names.
- **`@NotEmpty`**: a text, list or map must not be null or empty. Good for "at least one item".
- **`@Size(min = .., max = ..)`**: length of a text, or size of a list.
- **`@Min(..)`, `@Max(..)`**: number range (inclusive).
- **`@Positive`**, **`@PositiveOrZero`**: greater than 0, or 0 and up.
- **`@Email`**: looks like an email address.
- **`@Pattern(regexp = "...")`**: matches a regular expression.
- **`@Past`**, **`@Future`**: a date before or after now.

One subtle point that catches everyone: **most rules accept `null`**. `@Size`, `@Email`, `@Pattern`, `@Min`
all say "if there is a value, it must...". A missing email passes `@Email`. To make a field required *and*
checked, combine them: `@NotBlank @Email String email`.
:::

:::step{type=concept title="Switching it on: @Valid"}
Annotations on the record only *describe* the rules. Nothing checks them until you ask. You ask with
**`@Valid`** on the controller parameter:

```java
@PostMapping("/addresses")
public ResponseEntity<Address> create(@Valid @RequestBody NewAddress body) { ... }
```

Now, for every request, Spring:

1. reads the JSON into a `NewAddress` (chapter 12),
2. **validates** it against every annotation,
3. if anything fails, **stops**: your method is never called, and the client gets **400 Bad Request**,
4. if everything passes, calls your method with a body you can trust.

Forgetting `@Valid` is the most common validation bug: the annotations are there, everything looks right,
and nothing is checked. If your rules "do not work", look for `@Valid` first.
:::

:::step{type=task task=validate_product title="Your turn: validate new products"}
Two changes:

1. In `NewProduct.java`: the `name` must not be blank and at most **40** characters; `pricePaise` must be
   **positive**. (Imports from `jakarta.validation.constraints`.)
2. In `ProductController.java`, switch validation on for the `create` method's body (import
   `jakarta.validation.Valid`).

Rebuild, run, and send the same nonsense again:

```bash run
curl -i -X POST localhost:8080/products -H "Content-Type: application/json" -d '{"name": "", "pricePaise": -5}'
```

This time: `400 Bad Request`, and nothing is saved. A valid product still gets `201`. Press **Check**.

Usual slips: the rules written but `@Valid` forgotten (everything is still accepted), `@Positive` from the wrong
package (it must be `jakarta.validation.constraints.Positive`), or `@Size(40)` instead of `@Size(max = 40)` (that
does not compile: `@Size` has no single value).
:::

:::step{type=example title="What the server knows, and the client does not (yet)"}
Look at the 400 the client received:

```text
HTTP/1.1 400
Content-Type: application/json

{"timestamp":"2026-11-21T11:54:01.646+00:00","status":400,"error":"Bad Request","path":"/products"}
```

It says *something* was wrong, but not what. Now look at the server's log in Terminal 1. Spring logged the full
story; on our lab machine it was one very long line, shortened here:

```text
Resolved [MethodArgumentNotValidException: Validation failed for argument [0] ... with 2 errors:
  [Field error in object 'newProduct' on field 'name': rejected value []; ... default message [must not be blank]]
  [Field error in object 'newProduct' on field 'pricePaise': rejected value [-5]; ... default message [must be greater than 0]]
```

Everything is there: **which field**, **what value was sent**, and **a message** for each rule that failed.
`MethodArgumentNotValidException` is the exception Spring throws when `@Valid` fails, and it carries all of
those errors.

The client deserves that information too: a phone app could highlight the name field and show "must not
be blank". Turning this exception into a clear JSON answer is exactly what chapter 17 does. For now, the
important part works: bad data never reaches your code.
:::

:::step{type=concept title="Regular expressions, just enough" file="16-validation/src/main/java/com/shop/customer/NewCustomer.java" line="3-6"}
The second task validates customers, and an Indian mobile number needs `@Pattern`, which uses a **regular
expression** (a "regex"): a small language for describing text. You only need a few pieces:

- `[0-9]` matches **one digit** (any character from 0 to 9).
- `{10}` after something means **exactly 10 times**.
- So **`[0-9]{10}`** means "exactly ten digits, nothing else".

`@Pattern` checks the **whole** value against the expression, so `98765` (too short), `98765432101` (too
long) and `98765-43210` (a dash) all fail, and `9876543210` passes.

A few more you will meet: `[A-Z]` one capital letter, `[a-z]+` one or more small letters, `\\d` (written
with two backslashes in Java) is another way to say a digit. Regexes can get complicated; keep yours short
and add a comment saying what it means.
:::

:::step{type=task task=validate_customer title="Your turn: validate new customers"}
In `NewCustomer.java`: `name` must not be blank; `email` must not be blank and must be an email address;
`phone` must be exactly 10 digits. Then switch validation on in `CustomerController`.

Rebuild, run, and try a bad phone, then a good customer:

```bash run
curl -i -X POST localhost:8080/customers -H "Content-Type: application/json" -d '{"name": "Asha", "email": "asha@shop.in", "phone": "98765"}'
```

```bash run
curl -i -X POST localhost:8080/customers -H "Content-Type: application/json" -d '{"name": "Asha", "email": "asha@shop.in", "phone": "9876543210"}'
```

`400`, then `201` (that is what our lab machine answered). Press **Check**.

Usual slips: only `@Email` on the email (a missing email then passes; add `@NotBlank`), or `@Pattern(regexp =
"[0-9]{10}")` on a number type (a pattern needs a `String`; keep `phone` as text).
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`NewProduct` has `@NotBlank String name`, but the controller parameter is `@RequestBody NewProduct body` (no `@Valid`). A blank name arrives. What happens?
:::
- [ ] 400 Bad Request
- [x] The product is saved with a blank name: nothing triggered the validation
- [ ] 500 Internal Server Error
:::explain
The annotations describe rules; `@Valid` makes Spring check them. Without it, the body goes straight to
your method.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`email` has only `@Email`. A request leaves out the email entirely. Is it valid?
:::
- [x] Yes: like most rules, @Email accepts null
- [ ] No: @Email requires a value
- [ ] It depends on the JSON library
:::explain
"If there is a value, it must look like an email." To require it, add `@NotBlank` (or `@NotNull`) as well.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Which value matches `@Pattern(regexp = "[0-9]{6}")`?
:::
- [ ] 56001
- [x] 560001
- [ ] 560 001
:::explain
Exactly six digits, nothing else: five is too few, and a space is not a digit.
:::
:::

:::step{type=deep-dive title="Go deeper: messages, nested objects, and your own rules"}
**Your own messages.** Every annotation takes a `message`: `@Positive(message = "price must be more than 0")`.
That text is what the client will see in chapter 17.

**Nested objects and lists.** For a body that contains other objects (an order with a list of lines), put
`@Valid` on the nested field too, or on the list's type: `List<@Valid OrderLine> lines`. Otherwise the inner
objects are not checked. The capstone (chapter 30) uses exactly this.

**Path and query parameters.** Put `@Validated` on the controller class, and then rules like
`@RequestParam @Min(0) int maxPrice` work too.

**Your own rule.** For a rule no annotation covers ("delivery date must be on a working day"), you can write
a custom constraint annotation with a small validator class. Simple checks that need the database (is this
email already registered?) usually belong in the service instead.
:::

:::step{type=recap title="What you can do now"}
You can now keep bad data out of your API:

- **Bean Validation** rules are annotations on input classes: `@NotBlank`, `@NotNull`, `@NotEmpty`, `@Size`,
  `@Min`/`@Max`, `@Positive`, `@Email`, `@Pattern`, `@Past`/`@Future`.
- Most rules accept `null`; combine with `@NotBlank` or `@NotNull` to make a field required.
- **`@Valid`** on the `@RequestBody` parameter switches checking on. A failure means **400**, and your
  method never runs.
- The failure is a **`MethodArgumentNotValidException`** carrying every field, value and message, visible in
  the server log.
- `[0-9]{10}`: exactly ten digits.

:::photo{src="/lesson-images/spring/spring-16-notes.webp" alt="Sketchnote: Validation. Write the rules as annotations and switch them on with @Valid. Flow: JSON body, read into a record, @Valid checks each rule, 400 or your method runs. Remember: no @Valid, no checking; most rules accept null, so add @NotNull or @NotBlank to require a field; the pattern [0-9] ten times means exactly ten digits; the log names every failed field." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 17: turning that exception, and every other error, into clear and consistent JSON answers.
:::
