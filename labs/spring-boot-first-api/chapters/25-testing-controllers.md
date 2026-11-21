:::step{type=story title="Part 4: production-ready"}
Welcome to Part 4. The Shop API now has endpoints, validation, errors, a database and transactions. Part 4 is about
what makes code safe to run for real customers, and safe to change next month: **tests**, **logs and health
checks**, **security**, and **calling other services**. It ends with a capstone where you build a complete
checkout yourself.

We start with tests, because every other change you will ever make is safer with them. Until now, LabBox's hidden
checks tested your code. In a real team, **you** write the tests. They run on every change, on your laptop and on
the build server, and they catch the bug before a customer does. Spring Boot gives you excellent tools for it, and
this chapter teaches the one you will use most: testing the web layer.

:::mission
Write tests for `ProductController`. The check runs your tests twice: on the correct controller (they must
pass), and on a broken one (they must fail).
:::
:::

:::step{type=concept title="What a test is, and what makes one good"}
A **test** is a small piece of code that runs your code and checks the result automatically. In Java, tests are
written with **JUnit**: a method marked `@Test` in a class under `src/test/java`. Maven runs them all in the
`test` phase (chapter 2), and a failing test stops the build.

A good test:

- **passes when the code is right**;
- **fails when the code is wrong**, with a message that says what was expected and what happened;
- runs **fast**, and gives the **same answer every time**.

The second point is the one beginners forget. A test that passes no matter what proves nothing. It only feels
safe. That is why this chapter's check also runs your tests against a **deliberately broken controller**: your
tests must notice the bug. That is the real job of a test.

Every test has the same three parts, often written as comments:

```java
// arrange: set up what the test needs
// act:     do the thing being tested
// assert:  check the result
```
:::

:::step{type=concept title="Test slices: start only what you need"}
You could test the whole app, with `@SpringBootTest`: everything starts, every bean, the database, the web
server. That is the most realistic test, and the slowest, and when it fails, the cause could be anywhere.

Spring Boot also offers **test slices**: they start **one layer** only.

:::diagram{name="test-slices"}
A slice starts one layer; the layer below it is replaced by a mock.
:::

- **`@WebMvcTest(SomeController.class)`**: starts that controller, plus Spring MVC (routing, JSON, validation,
  error handling). No services, no repositories, no database. For testing **URLs, status codes and JSON**.
- **`@DataJpaTest`**: starts entities, repositories and an in-memory database (chapter 26).
- **`@SpringBootTest`**: everything, for testing a whole flow end to end.

A web slice starts in about a second and checks exactly the controller's job. But the controller needs a
`ProductService`, and the slice does not create one. So you give it a **fake**.
:::

:::step{type=concept title="Mocks: a fake you control"}
A **mock** is a fake object that looks like a real one (same type, same methods), but whose answers **you decide**
in the test. **Mockito** is the mocking library included in `spring-boot-starter-test`.

```java
@MockitoBean
GreetingService service;
```

**`@MockitoBean`** on a test field creates a Mockito mock of `GreetingService` and puts it into the test's
application context, in place of the real bean. The controller gets the mock through its constructor, as usual.

Then, in each test, you say what the mock should answer:

```java
when(service.greet("Asha")).thenReturn("Hello, Asha");
```

Read it literally: "**when** `greet("Asha")` is called, **then return** `"Hello, Asha"`". For any call you did not
set up, a mock returns an empty value (`null`, `0`, an empty `Optional`, an empty list).

Why a mock and not the real service? Because this test is about the **controller**: does `/greet/Asha` reach the
right method, and come back as the right JSON? With a mock, the test is fast, and it fails only when the
**controller** is wrong. The service gets its own tests.
:::

:::step{type=concept title="MockMvc: requests without a server"}
**`MockMvc`** sends requests to your controllers **without a real server or network**, through the same
DispatcherServlet, handler mapping and Jackson you learned about in chapter 10. You inject it with `@Autowired`
in a `@WebMvcTest`:

```java
mvc.perform(get("/greet/Asha"))                       // act: send GET /greet/Asha
        .andExpect(status().isOk())                    // assert: status 200
        .andExpect(jsonPath("$.text").value("Hello, Asha"));   // assert: the JSON field "text"
```

- **`perform(get(...))`** sends the request (`post`, `put`, `delete`... work the same).
- **`andExpect(status().isOk())`** checks the status; also `isNotFound()`, `isCreated()`, `isBadRequest()`...
- **`jsonPath("$.text")`** reads a value from the JSON response: `$` is the whole body, `.text` its `text` field.
  `$[0].name` would be the `name` of the first element of an array.

The static methods (`get`, `status`, `jsonPath`) come from `MockMvcRequestBuilders` and `MockMvcResultMatchers`.
Your editor can add those imports for you.
:::

:::step{type=example title="Worked example: a complete controller test"}
Here is a full test class for a greeting controller that answers `GET /greet/{name}` with `{"text": ...}`:

```java
@WebMvcTest(GreetingController.class)
class GreetingControllerTest {

    @Autowired
    MockMvc mvc;

    @MockitoBean
    GreetingService service;

    @Test
    void greetsByName() throws Exception {
        when(service.greet("Asha")).thenReturn("Hello, Asha");          // arrange

        mvc.perform(get("/greet/Asha"))                                  // act
                .andExpect(status().isOk())                              // assert
                .andExpect(jsonPath("$.text").value("Hello, Asha"));
    }

    @Test
    void unknownLanguageIs400() throws Exception {
        mvc.perform(get("/greet/Asha").param("lang", "klingon"))
                .andExpect(status().isBadRequest());
    }
}
```

Each `@Test` method is independent: JUnit runs them in any order, and each one sets up what it needs. The method
names read like sentences ("greets by name", "unknown language is 400"): when one fails, the name already tells
you what broke. `throws Exception` is there because `perform` can throw; any exception fails the test.

:::trace{title="What happens when greetsByName runs"}
| step | what runs | result |
|---|---|---|
| start | the web slice starts GreetingController with the mock | about 1 second |
| arrange | when(service.greet("Asha")).thenReturn(...) | the mock is told its answer |
| act | mvc.perform(get("/greet/Asha")) | routing, the controller, the mock, Jackson |
| assert | status().isOk() | 200: passes |
| assert | jsonPath("$.text").value("Hello, Asha") | matches: passes |
:::
:::

:::step{type=predict title="Guess first"}
:::question
In a `@WebMvcTest`, you forget the `@MockitoBean ProductService` field. What happens?
:::
- [ ] The real ProductService is used
- [x] The test cannot start: the controller needs a ProductService bean, and the slice does not create one
- [ ] The controller receives null, and every request answers 500
:::explain
A web slice only creates the web layer. Services are not scanned, so the controller's constructor has nothing to
receive, and the context fails to start. A mock fills exactly that gap.
:::
:::

:::step{type=try title="Run the tests" file="25-testing-controllers/src/test/java/com/shop/product/ProductControllerTest.java"}
Your test class, `ProductControllerTest`, is on the right: a `@WebMvcTest` with no tests yet. The controller under
test answers `GET /products/{id}` with the product, or `404` when `service.find(id)` returns an empty `Optional`.

Maven runs every test in `src/test/java`:

```bash run
cd 25-testing-controllers && mvn -q -o test
```

With no tests yet, it succeeds silently. Once you have written them, a passing run prints Spring's start-up lines
and nothing else; a failing run prints which test failed, and why.
:::

:::step{type=task task=controller_test title="Your turn: test ProductController"}
In `ProductControllerTest.java`, write at least **two** tests:

1. `GET /products/1` answers **200** with the product's **name**, when the service finds it. (Arrange with
   `when(service.find(1)).thenReturn(Optional.of(new Product(1, "Masala tea", 2000)))`.)
2. `GET /products/99` answers **404**, when the service finds nothing (`Optional.empty()`).

You need the `MockMvc` field, the `@MockitoBean ProductService` field, and the imports (`Test` from
`org.junit.jupiter.api`, `MockitoBean` from `org.springframework.test.context.bean.override.mockito`, `when` from
`org.mockito.Mockito`, and the MockMvc statics).

Run `mvn -q -o test` until it passes. Then try breaking one on purpose: expect `"Samosa"` instead of
`"Masala tea"`, and run again:

```text
[ERROR] Tests run: 2, Failures: 1, Errors: 0, Skipped: 0 <<< FAILURE! -- in com.shop.product.ProductControllerTest
[ERROR]   ProductControllerTest.returnsTheProduct:30 JSON path "$.name" expected:<Samosa> but was:<Masala tea>
```

The test's name, the line, what was expected and what came back. Put it back, and press **Check**.
:::

:::step{type=task task=catches_bug title="Your turn: catch the planted bug"}
The check now replaces `ProductController` with a broken version (it makes a small, realistic mistake in one of
the two cases) and runs **your** tests again. If your tests check both cases properly, at least one fails there,
and this task passes.

If it does not pass, read the check's message: it tells you which behaviour your tests do not check yet. This is
exactly how real teams think about tests: "if someone breaks this, will a test notice?"
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A test checks only `status().isOk()` for `GET /products/1`. The controller starts returning the wrong product. Does the test fail?
:::
- [ ] Yes
- [x] No: it never looks at the body
- [ ] Only if the product does not exist
:::explain
A test proves only what it asserts. Check the parts of the answer that matter: the status *and* the important
fields.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In a test, a mock has no `when(...)` set up for `service.find(5)`. What does `find(5)` return?
:::
- [ ] It throws an exception
- [x] An empty Optional: mocks return empty values for calls nobody set up
- [ ] The real service's answer
:::explain
Mockito returns `null`, `0`, `false`, an empty `Optional` or an empty collection, depending on the return type.
That is often useful: "not found" needs no setup at all.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Which annotation starts only controllers, JSON and MockMvc?
:::
- [x] @WebMvcTest
- [ ] @SpringBootTest
- [ ] @DataJpaTest
:::explain
`@WebMvcTest` is the web slice. `@SpringBootTest` starts everything; `@DataJpaTest` starts the data layer.
:::
:::

:::step{type=deep-dive title="Go deeper: the test pyramid, verify, and @MockBean"}
**The test pyramid.** Most teams aim for many fast unit and slice tests, fewer full `@SpringBootTest` tests, and
very few tests through a real browser or a deployed server. Slices give quick, precise failures; full tests catch
wiring mistakes slices cannot see.

**Checking calls.** Mockito can also check that a method *was called*: `verify(service).find(1)`. Use it when the
call itself is the behaviour (for example, "a confirmation email was sent").

**Older code.** Before Spring Boot 3.4, the annotation was `@MockBean` (from Spring Boot). It works the same way;
you will see it in many projects. `@MockitoBean` is the newer one, from Spring Framework itself.

**Service tests.** A service often needs no Spring at all: `new ProductService(fakeRepository)` in a plain JUnit
test, no context, no annotations, milliseconds to run.
:::

:::step{type=recap title="What you can do now"}
You can now test the web layer the way professional teams do:

- **JUnit**: `@Test` methods in `src/test/java`; `mvn test` runs them; a failure stops the build.
- A good test passes on right code and **fails on wrong code**: arrange, act, assert.
- **`@WebMvcTest(Controller.class)`** starts only the web layer; **`@MockitoBean`** replaces the service with a
  **mock**; **`when(...).thenReturn(...)`** sets its answers.
- **`MockMvc`**: `perform(get(...))`, `andExpect(status()...)`, `andExpect(jsonPath("$.field").value(...))`.
- Read a failure: test name, line, expected and actual.

Next, chapter 26: testing what a mock cannot, the database queries themselves.
:::
