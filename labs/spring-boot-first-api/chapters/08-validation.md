:::step{type=story title="Why this chapter"}
An API must never trust its input. An empty name, a negative price or a malformed email will otherwise
reach the database and cause problems much later, far from where they entered. Spring checks input
declaratively: you write the rules as annotations, and invalid requests are rejected with 400 before
your method runs.

:::mission
In the `08-validation` folder: reject invalid products and invalid customers with 400.
:::
:::

:::step{type=concept title="Bean Validation annotations"}
**Bean Validation** (Jakarta Validation) defines constraints as annotations on fields or record
components. The common ones:

| annotation | rule |
|---|---|
| `@NotNull` | not `null` |
| `@NotBlank` | a string that is not `null`, empty or only spaces |
| `@Size(min, max)` | length of a string or size of a list |
| `@Positive`, `@Min`, `@Max` | numbers |
| `@Email` | an email address |
| `@Pattern(regexp = "...")` | the string matches a regular expression |

The `spring-boot-starter-validation` dependency provides them, with Hibernate Validator as the engine.
:::

:::step{type=concept title="@Valid triggers the check"}
Annotations on the record only describe the rules. `@Valid` on the parameter tells Spring to apply them:

```java
public record NewProduct(@NotBlank @Size(max = 40) String name,
                         @Positive int pricePaise) {}

@PostMapping("/products")
public ResponseEntity<Product> create(@Valid @RequestBody NewProduct body) { ... }
```

Spring converts the JSON, validates the object, and if any constraint fails it throws
`MethodArgumentNotValidException`, answered as **400 Bad Request**. Your method is not called.

:::mistake
Without `@Valid`, the annotations on the record do nothing and invalid data goes through.
:::
:::

:::step{type=example title="Worked example: a delivery address"}
```java
public record NewAddress(
        @NotBlank String line1,
        @NotBlank String city,
        @Pattern(regexp = "[0-9]{6}") String pincode) {}
```

| JSON sent | result |
|---|---|
| `{"line1": "12 MG Road", "city": "Pune", "pincode": "411001"}` | valid: the method runs |
| `{"line1": "", "city": "Pune", "pincode": "411001"}` | 400: `line1` is blank |
| `{"line1": "12 MG Road", "city": "Pune", "pincode": "4110"}` | 400: `pincode` does not match six digits |

`[0-9]{6}` means "exactly six digits"; `@Pattern` must match the whole string.
:::

:::step{type=predict title="Guess first"}
:::question
`@NotBlank String name` and the JSON has no `"name"` property at all. Is it valid?
:::
- [ ] Yes: there is nothing to check
- [x] No: the missing property is `null`, and `@NotBlank` rejects `null`
- [ ] The JSON cannot be read
:::explain
A missing property becomes `null` in the record. `@NotBlank` rejects `null`, empty and whitespace-only
strings, which makes it the usual choice for required text.
:::
:::

:::step{type=try title="Send an invalid product"}
```bash run
cd 08-validation && mvn -q -o package -DskipTests && java -jar target/validation.jar
```

After the first task, in a second tab:

```bash run
curl -si -X POST localhost:8080/products -H 'Content-Type: application/json' -d '{"name": "", "pricePaise": -5}' | head -1
```
:::

:::step{type=task task=validate_product title="Warm-up: validate a new product"}
In `08-validation`, add constraints to `NewProduct`: the name must not be blank and at most 40
characters, and `pricePaise` must be positive. Add `@Valid` in `ProductController`.

Invalid products answer 400; valid ones are still created (201).
:::

:::step{type=task task=validate_customer title="Validate a new customer"}
Add constraints to `NewCustomer`: `name` not blank, `email` a valid email address (and not blank), and
`phone` exactly 10 digits. Add `@Valid` in `CustomerController`.

A customer with `"phone": "98765"` answers 400.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which annotation fits "at least 1 item, at most 20" for a `List` field?
:::
- [ ] `@Positive`
- [x] `@Size(min = 1, max = 20)`
- [ ] `@Min(1) @Max(20)`
:::explain
`@Size` measures the length of strings and the size of collections. `@Min` and `@Max` compare numbers.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
When validation fails, what happens to your controller method?
:::
- [ ] It runs, with the invalid values
- [x] It is not called; Spring answers 400
- [ ] It runs, and you must check a flag
:::explain
Validation happens before the call. If any constraint fails, Spring throws `MethodArgumentNotValidException`
and the method never runs.
:::
:::

:::step{type=deep-dive title="Custom messages, groups and custom constraints"}
Each annotation accepts a message: `@Positive(message = "price must be more than 0")`. Validation also
works on path and query parameters when the controller class has `@Validated`. For rules no built-in
annotation covers (for example "end date after start date"), write a custom constraint: an annotation
plus a `ConstraintValidator` class. Validation in the API layer does not replace database constraints:
both are needed, because data can also reach the database by other paths.
:::

:::step{type=recap title="Chapter done"}
- Constraint annotations (`@NotBlank`, `@Size`, `@Positive`, `@Email`, `@Pattern`) describe valid input.
- `@Valid` on a `@RequestBody` parameter applies them; invalid requests get 400 and the method does not run.
- Validate at the edge of the API, so invalid data never reaches the rest of the application.
:::
