:::step{type=story title="Why this chapter"}
A repository method can look right and still return the wrong rows, or the right rows in the wrong
order. A mock cannot catch that: a mock answers whatever you tell it. To test a query you need a real
database. Spring Boot's `@DataJpaTest` gives you one, in memory, for each test.

:::mission
In the `18-testing-data` folder: test `findByCategoryOrderByNameAsc` against a real database. The check
runs your test on the correct repository (it must pass) and on one that sorts the wrong way (it must fail).
:::
:::

:::step{type=concept title="@DataJpaTest"}
`@DataJpaTest` starts the database layer only:

- your `@Entity` classes and repositories;
- an **embedded database** (H2 here) in place of the configured one;
- a **transaction around each test**, rolled back at the end, so every test starts with empty tables.

No controllers and no services are created. You inject the repository with `@Autowired` and call it.

:::diagram{name="test-slices"}
The data slice starts entities, repositories and a database; nothing above them.
:::
:::

:::step{type=concept title="Arrange data, then query"}
A query test has the same three parts as any test:

1. **Arrange**: save the rows the query should find, and rows it should **not** find.
2. **Act**: call the repository method.
3. **Assert**: check exactly which rows came back, and in which order.

The rows it should not find matter as much as the others. A test that saves only snack products cannot
tell whether the query filters by category at all.
:::

:::step{type=example title="Worked example: customers by city"}
```java
@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    CustomerRepository repository;

    @Test
    void findsOneCitySortedByName() {
        repository.save(new Customer("Ravi", "Pune"));
        repository.save(new Customer("Asha", "Delhi"));
        repository.save(new Customer("Meera", "Pune"));

        List<String> names = repository.findByCityOrderByNameAsc("Pune")
                .stream().map(Customer::getName).toList();

        assertThat(names).containsExactly("Meera", "Ravi");
    }
}
```

`assertThat(...).containsExactly(...)` (from AssertJ, included in `spring-boot-starter-test`) checks the
elements **and** their order. `contains(...)` would ignore the order.

:::trace{title="findsOneCitySortedByName"}
| step | table customer | result |
|---|---|---|
| save Ravi, Pune | 1 row | |
| save Asha, Delhi | 2 rows | |
| save Meera, Pune | 3 rows | |
| findByCityOrderByNameAsc("Pune") | 3 rows | [Meera, Ravi] |
| containsExactly("Meera", "Ravi") | 3 rows | passes |
| test ends | rolled back: 0 rows | the next test starts clean |
:::
:::

:::step{type=predict title="Guess first"}
:::question
The query is broken and returns Pune customers sorted **descending**: [Ravi, Meera]. Which assertion catches it?
:::
- [ ] assertThat(names).contains("Meera", "Ravi")
- [x] assertThat(names).containsExactly("Meera", "Ravi")
- [ ] assertThat(names).hasSize(2)
:::explain
Only `containsExactly` checks the order. The other two pass on the broken query too.
:::
:::

:::step{type=try title="Run your test"}
```bash run
cd 18-testing-data && mvn -q -o test
```

Add a mistake on purpose (expect `"Samosa"` first) and run it again: read the failure message AssertJ
prints. Then put it back.
:::

:::step{type=task task=repository_test title="Test the category query"}
In `18-testing-data/src/test/java/com/shop/product/ProductRepositoryTest.java`, save a few products of
two categories, call `findByCategoryOrderByNameAsc("snacks")`, and check that the result contains only the
snacks, sorted by name.
:::

:::step{type=task task=catches_query_bug title="Catch the wrong order"}
The check swaps in a repository whose query returns the right products in the wrong order, and runs
your test again. Your test must fail there. If it does not, it is not checking the order yet.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two tests in a `@DataJpaTest` class each save three products. How many products does the second test see before it saves anything?
:::
- [x] 0
- [ ] 3
- [ ] 6
:::explain
Each test runs in a transaction that is rolled back when the test ends, so the tables are empty again.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why not test a repository with a mock?
:::
- [ ] Mocks cannot return lists
- [x] A mock returns what the test tells it; it never runs the query, so it cannot find a wrong query
- [ ] Repositories are interfaces and cannot be mocked
:::explain
The thing under test here is the query itself. Only a real database runs it.
:::
:::

:::step{type=deep-dive title="H2 in tests, Postgres in production"}
An in-memory H2 database is fast, but it is not the database you run in production. Most queries behave
the same; some do not (special SQL functions, JSON columns, locking). Teams that need certainty use
**Testcontainers**: the test starts a real Postgres in Docker for the length of the test run, and
`@DataJpaTest` with `@AutoConfigureTestDatabase(replace = NONE)` uses it. The test code stays the same.
:::

:::step{type=recap title="Chapter done"}
- `@DataJpaTest` starts entities, repositories and an in-memory database.
- Each test runs in a transaction that is rolled back, so tests do not affect each other.
- Save rows that should match and rows that should not; assert the exact result.
- `containsExactly` checks the order; `contains` does not.
:::
