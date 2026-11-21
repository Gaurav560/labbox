:::step{type=story title="Why this chapter"}
So far a hidden check has tested your code. In a real team, **you** write the tests, and they run on
every change, so a bug is caught before it reaches users. Spring Boot gives you tools to test one layer
at a time, fast. This chapter tests the web layer: does each URL answer with the right status and JSON?

:::mission
In the `17-testing-controllers` folder: write tests for `ProductController`. The check runs your tests
twice: on the correct controller (they must pass) and on a broken one (they must fail).
:::
:::

:::step{type=concept title="What a good test proves"}
A test is code that runs your code and checks the result. A good test:

- **passes** when the code is right;
- **fails** when the code is wrong, and says what went wrong;
- runs **fast** and gives the same answer every time.

The second point is the one people forget. A test that always passes proves nothing. That is why the
check in this chapter also runs your tests against a broken controller: your tests must notice.
:::

:::step{type=concept title="Test slices: start only what you need"}
`@SpringBootTest` starts the whole application: every bean, the database, everything. That is the most
realistic test, and the slowest. Spring Boot also has **test slices**, which start only one layer:

- **`@WebMvcTest`** starts controllers, JSON, validation and error handling: test URLs, status codes and JSON.
- **`@DataJpaTest`** starts entities, repositories and an in-memory database: test queries.
- **`@SpringBootTest`** starts everything: test the whole flow, end to end.

With `@WebMvcTest(ProductController.class)` there is no `ProductService` bean: you replace it with a
**mock**, a fake object whose answers you choose in the test.

:::diagram{name="test-slices"}
A slice starts one layer; the layer below it is replaced by a mock.
:::
:::

:::step{type=concept title="MockMvc and @MockitoBean"}
Two tools do the work:

- **`MockMvc`** sends a request to your controllers without a real network or server, and lets you check
  the answer: `mvc.perform(get("/products/1")).andExpect(status().isOk())`.
- **`@MockitoBean`** on a field puts a Mockito mock in the application context, in place of the real bean.
  `when(service.find(1)).thenReturn(...)` decides what the mock answers.

```java
@WebMvcTest(GreetingController.class)
class GreetingControllerTest {

    @Autowired
    MockMvc mvc;

    @MockitoBean
    GreetingService service;
}
```
:::

:::step{type=example title="Worked example: testing a greeting endpoint"}
The controller answers `GET /greet/{name}` with `{"text": "..."}` from `GreetingService.greet(name)`.

```java
@Test
void greetsByName() throws Exception {
    when(service.greet("Asha")).thenReturn("Hello, Asha");

    mvc.perform(get("/greet/Asha"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.text").value("Hello, Asha"));
}
```

Three parts, in every test: **arrange** (tell the mock what to answer), **act** (send the request),
**assert** (check the status and the JSON). `jsonPath("$.text")` reads the `text` field of the answer.

:::trace{title="What happens when greetsByName runs"}
| step | what runs | result |
|---|---|---|
| arrange | when(service.greet("Asha")) | the mock will answer "Hello, Asha" |
| act | mvc.perform(get("/greet/Asha")) | the controller runs, the mock answers |
| assert | status().isOk() | 200: passes |
| assert | jsonPath("$.text") | "Hello, Asha": passes |
:::
:::

:::step{type=predict title="Guess first"}
:::question
In a `@WebMvcTest`, you forget the `@MockitoBean ProductService` field. What happens?
:::
- [ ] The real ProductService is used
- [x] The test cannot start: the controller needs a ProductService bean, and the slice does not create one
- [ ] The controller gets null and every request answers 500
:::explain
A web slice starts only the web layer. Services are not scanned, so the controller's constructor has
nothing to receive. A mock fills the gap.
:::
:::

:::step{type=try title="Run the tests yourself"}
Maven runs every test in `src/test/java`:

```bash run
cd 17-testing-controllers && mvn -q -o test
```

With no tests yet, it prints nothing and succeeds. Once you have written them, a failing test prints
its name and what it expected.
:::

:::step{type=task task=controller_test title="Test ProductController"}
In `17-testing-controllers/src/test/java/com/shop/product/ProductControllerTest.java`, write at least
two tests with MockMvc and a mocked `ProductService`:

- `GET /products/1` answers 200 with the product's name, when the service finds it;
- `GET /products/99` answers 404, when the service finds nothing (`Optional.empty()`).
:::

:::step{type=task task=catches_bug title="Catch the planted bug"}
The check replaces `ProductController` with a broken version and runs your tests again. If your tests
cover both cases above, at least one of them fails there, and this task passes. If it does not, read the
failure message: it tells you which behaviour your tests do not check yet.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which annotation starts only controllers, JSON handling and MockMvc?
:::
- [x] @WebMvcTest
- [ ] @SpringBootTest
- [ ] @DataJpaTest
:::explain
`@WebMvcTest` is the web slice. `@SpringBootTest` starts everything; `@DataJpaTest` starts the database layer.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A test checks only `status().isOk()` for `GET /products/1`. The controller starts returning the wrong product. Does the test fail?
:::
- [ ] Yes
- [x] No: it never looks at the body
- [ ] Only if the product does not exist
:::explain
A test proves only what it asserts. Check the parts of the answer that matter: the status and the fields.
:::
:::

:::step{type=deep-dive title="How much to test, and where"}
Most teams follow a **test pyramid**: many fast slice and unit tests at the bottom, fewer
`@SpringBootTest` tests that run the whole flow, and very few tests through a real browser or a real
deployed server. Slice tests give quick, precise failures; full tests catch wiring mistakes the slices
cannot see. `@MockitoBean` replaced the older `@MockBean` in Spring Boot 3.4; you will see `@MockBean` in
older code, and it works the same way.
:::

:::step{type=recap title="Chapter done"}
- You write tests that pass on correct code and fail on broken code.
- `@WebMvcTest` starts only the web layer; `@MockitoBean` replaces the service with a mock.
- `MockMvc` sends requests; `status()` and `jsonPath()` check the answer.
- Every test has three parts: arrange, act, assert.
:::
