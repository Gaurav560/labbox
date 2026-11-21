:::step{type=story title="What a mock cannot test"}
In chapter 25 you replaced the service with a mock, and that was right: the test was about the controller. But
look at what a mock can never tell you. If a repository's query is wrong (wrong condition, wrong sort order, a
join that loses rows), a mock will happily return whatever you told it to. The test passes; the bug ships.

A query is only tested when it **actually runs against a database**. Spring Boot makes that easy and fast with a
second test slice, `@DataJpaTest`, which gives each test a real (in-memory) database, empty and clean. This
chapter teaches it, and one assertion detail that decides whether your test really protects you.

:::mission
Test `findByCategoryOrderByNameAsc` against a real database. The check runs your test on the correct repository,
and on one whose query sorts the wrong way.
:::
:::

:::step{type=concept title="@DataJpaTest: the data slice"}
**`@DataJpaTest`** starts only the data layer:

- your `@Entity` classes and your Spring Data repositories;
- an **embedded database** (H2), used instead of whatever `spring.datasource.url` says, so your tests never
  touch a real server's data;
- **a transaction around each test, rolled back at the end**. Whatever a test inserts disappears when it
  finishes, so every test starts with empty tables, and tests never affect each other.

No controllers, no services, no web layer. You inject the repository with `@Autowired`, and call it:

```java
@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    CustomerRepository repository;
}
```

It starts in a second or two, and each test runs in milliseconds.
:::

:::step{type=concept title="Arrange data that can prove something"}
A query test has the same three parts as any test:

1. **Arrange**: save the rows the query **should** find, *and* rows it **should not** find.
2. **Act**: call the query method.
3. **Assert**: check **exactly** which rows came back, and in which order.

The rows that should *not* be found matter as much as the others. Suppose you test "customers in Pune" and save
only Pune customers. A broken query that returns **everyone** would still pass. Save a Delhi customer too, and the
test can tell the difference.

The same for order: to test "sorted by name", save rows **out of order** (Ravi before Meera). If you save them
already sorted, a query that forgot to sort would still pass.

Think of it as: "what is the bug this test could catch?" Then arrange data where that bug would show.
:::

:::step{type=example title="Worked example: customers of one city, by name"}
```java
@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    CustomerRepository repository;

    @Test
    void findsOneCitySortedByName() {
        repository.save(new Customer("Ravi", "Pune"));          // arrange: out of order...
        repository.save(new Customer("Asha", "Delhi"));         // ...and one that must NOT appear
        repository.save(new Customer("Meera", "Pune"));

        List<String> names = repository.findByCityOrderByNameAsc("Pune")     // act
                .stream().map(Customer::getName).toList();

        assertThat(names).containsExactly("Meera", "Ravi");    // assert: these two, in this order
    }
}
```

**`assertThat(...)`** comes from **AssertJ**, the assertion library included in `spring-boot-starter-test`
(import `static org.assertj.core.api.Assertions.assertThat`). It reads like a sentence, and its failure messages
are very clear.

:::trace{title="findsOneCitySortedByName"}
| step | rows in the customer table | result |
|---|---|---|
| save Ravi, Pune | 1 | |
| save Asha, Delhi | 2 | |
| save Meera, Pune | 3 | |
| findByCityOrderByNameAsc("Pune") | 3 | [Meera, Ravi] |
| containsExactly("Meera", "Ravi") | 3 | passes |
| test ends | 0: rolled back | the next test starts with an empty table |
:::
:::

:::step{type=concept title="Which assertion actually checks the order?"}
AssertJ has several ways to compare a list, and they check very different things:

```java
assertThat(names).containsExactly("Meera", "Ravi");          // these elements, in THIS order, nothing else
assertThat(names).containsExactlyInAnyOrder("Ravi", "Meera"); // these elements, any order, nothing else
assertThat(names).contains("Meera", "Ravi");                  // at least these, any order, others allowed
assertThat(names).hasSize(2);                                 // only the number
```

Now imagine the query is broken and returns Pune customers sorted **Z to A**: `[Ravi, Meera]`. Only the first line
fails. The other three all pass, and the bug ships.

When order is part of what you are testing (and `OrderBy` says it is), use **`containsExactly`**.
:::

:::step{type=predict title="Guess first"}
:::question
The broken query returns `[Ravi, Meera]` instead of `[Meera, Ravi]`. Which assertion catches it?
:::
- [ ] assertThat(names).contains("Meera", "Ravi")
- [x] assertThat(names).containsExactly("Meera", "Ravi")
- [ ] assertThat(names).hasSize(2)
:::explain
Only `containsExactly` checks the order. The others pass on the broken query too.
:::
:::

:::step{type=try title="Your test file" file="26-testing-data/src/test/java/com/shop/product/ProductRepositoryTest.java"}
`ProductRepositoryTest` is on the right: a `@DataJpaTest` with no tests yet. The repository under test has:

```java
List<Product> findByCategoryOrderByNameAsc(String category);
```

and `Product` has a constructor `new Product(name, category)`. Run the (empty) tests:

```bash run
cd 26-testing-data && mvn -q -o test
```

Nothing to fail yet. Your test comes next.
:::

:::step{type=task task=repository_test title="Your turn: test the category query"}
Write a test in `ProductRepositoryTest` that:

1. **saves** a few products of **two categories**, with the snacks **out of alphabetical order**
   (for example Samosa, then a drink, then Bhel puri, then Kachori);
2. calls **`findByCategoryOrderByNameAsc("snacks")`** and maps the result to names;
3. asserts the **exact** names, in order.

Run `mvn -q -o test` until it passes. Then break it on purpose (expect "Samosa" first), read AssertJ's message,
and put it back. Press **Check**.
:::

:::step{type=task task=catches_query_bug title="Your turn: catch the wrong order"}
The check swaps in a repository whose query returns the **right products in the wrong order**, and runs your test
again. Your test must fail there.

If this task does not pass, your test is not checking the order yet: look at your data (are the snacks saved
out of order?) and your assertion (does it check the order?).
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Two tests in a `@DataJpaTest` class each save three products. How many products does the second test see before it saves anything?
:::
- [x] 0
- [ ] 3
- [ ] 6
:::explain
Each test runs in a transaction that is rolled back at the end, so the tables are empty again.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why not test a repository with a mock?
:::
- [ ] Mocks cannot return lists
- [x] A mock returns what the test tells it; the query never runs, so a wrong query cannot be caught
- [ ] Repositories are interfaces and cannot be mocked
:::explain
The thing under test is the query itself. Only a real database runs it.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Your test for "customers in Pune" only saves Pune customers. Which bug can it NOT catch?
:::
- [ ] A query that returns nothing
- [x] A query that ignores the city and returns every customer
- [ ] A query with the wrong sort order
:::explain
With only Pune rows in the table, "every customer" and "Pune customers" are the same list. Save a row that must
not be found.
:::
:::

:::step{type=deep-dive title="Go deeper: Testcontainers, and the whole app in a test"}
**H2 is not production.** Most queries behave the same in H2 and PostgreSQL. Some do not (special functions, JSON
columns, locking). Teams that need certainty use **Testcontainers**: the test starts a real PostgreSQL in Docker
for the length of the run, and with `@AutoConfigureTestDatabase(replace = NONE)` the slice uses it. Spring Boot
3.1+ makes it a few lines with `@ServiceConnection`.

**The whole flow.** `@SpringBootTest` with `@AutoConfigureMockMvc` starts everything (web, services, database) and
lets you test a request from HTTP to the database and back. Fewer of those, but they catch wiring mistakes no slice
can. The hidden checks in this course are written exactly like that.
:::

:::step{type=recap title="What you can do now"}
You can now test queries properly:

- **`@DataJpaTest`** starts entities, repositories and an embedded database; each test runs in a **rolled-back
  transaction**, so tests never see each other's data.
- Arrange data that can **prove** something: rows that should be found, rows that should not, and rows **out of
  order** when order matters.
- **AssertJ**: `assertThat(list).containsExactly(...)` checks elements *and* order; `contains` and `hasSize` do not.
- A test's value is the bug it can catch. Ask "if someone breaks this, will my test notice?"

Next, chapter 27: when the app is running on a server, how do you know what it is doing? Logs and health checks.
:::
