:::step{type=story title="How do you know nothing broke?"}
Lostdesk changes every week now. Each change is small, and each one could break something three routes away: a
status code, a filter, a field. Until now you checked by hand, in `/docs`. With twenty routes, checking them all after
every change would take an hour, and nobody would do it.

Car makers faced the same question long ago: you cannot wait for real accidents to learn whether a car is safe. So
they crash cars on purpose, with a dummy inside that measures what a person would feel, again and again, the same way
every time.

:::photo{src="/lesson-images/fastapi/crash-test-dummy.webp" alt="A crash test dummy with a pink head and a yellow suit sits at the wheel of a blue car, its hands on a steering wheel marked with yellow and black tape" credit="Brady Holt" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:IIHS_crash_test_dummy_in_Hyundai_Tucson.jpg"}
A crash test dummy in a car at the Insurance Institute for Highway Safety's research centre.
:::

Automated **tests** are Lostdesk's crash tests: small programs that call the API with known inputs and check the
answers, in a second, every time anything changes.

:::mission
Give the tests their own throwaway database instead of `lostdesk.db`, then write tests good enough to catch three
bugs planted in copies of Lostdesk.
:::
:::

:::step{type=history title="Where tests come from"}
Programmers have always tested by hand. Automated tests that live next to the code became a habit in the 1990s: Kent
Beck wrote a small testing framework for the Smalltalk language, and in 1997 he and Erich Gamma wrote JUnit for Java,
which spread the idea everywhere. Python's `unittest` copies JUnit's design (it began as PyUnit in 1999 and joined
the standard library in 2001).

**pytest** began in 2004, in Holger Krekel's `py` library, with a simpler idea: a test is just a function whose name
starts with `test_`, and checking is just Python's `assert`. It became the most used Python test runner, and it is
what FastAPI's docs use. LabBox's Python course teaches it in chapter 17.
:::

:::step{type=try title="Run the first test" file="15-testing/tests/test_items.py" line="1-17"}
`15-testing/main.py` is chapter 13's finished app. Open `tests/test_items.py`:

```python
@pytest.fixture
def client():
    with TestClient(app) as test_client:  # "with" runs the app's lifespan, which creates the tables
        yield test_client


def test_unknown_item_is_404(client):
    response = client.get("/items/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No item with that id"}
```

Run it (no server needed):

```bash run
cd /workspace/15-testing && python -m pytest -q
```

```text
.                                                                        [100%]
1 passed in 0.31s
```

- **`TestClient`** calls the app directly, inside the same Python process: no server, no network, no port. It has
  the methods you know from curl: `.get`, `.post`, `.patch`, `.delete`.
- A **fixture** (`@pytest.fixture`) is pytest's way of preparing something a test needs. A test asks for it by naming
  it as a parameter, `client`, a little like FastAPI's `Depends`. Code after `yield` runs once the test is over.
- Each dot is a passing test; an `F` is a failure.

Now look in the folder: `lostdesk.db` has appeared. The test used the **real** database.
:::

:::step{type=concept title="A throwaway database for tests"}
That one test only reads. The next ones will create items, and with the real database they would leave rows behind in
`lostdesk.db`, and a test that counts items would see rows from yesterday's run. Tests must start from the same empty
state every time.

FastAPI's answer is `app.dependency_overrides`: a dictionary in which you say "whenever a route asks for this
dependency, give it that one instead". Every route asks for `get_session`, so one line swaps the database for all of
them:

```python
app.dependency_overrides[get_session] = get_test_session
```

The test session uses an **in-memory** SQLite database, which lives only in memory and vanishes when the test ends:

```python
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(engine)
```

`sqlite://` with nothing after it means "in memory". `StaticPool` makes every session use one and the same
connection; without it, each new connection would see its own, empty, in-memory database. (This is the recipe of the
docs' "Testing a Database" page.) Press Play:

:::diagram{name="fastapi-test-override"}
The override sends every route's get_session to the test's in-memory database, so lostdesk.db is never opened.
:::
:::

:::step{type=example title="Worked example: overriding a guard"}
This is not in your project. Chapter 11's routes needed a desk key. A test that is about logging items, not about
keys, can switch the guard off:

```python
from main import app, require_desk


@pytest.fixture
def client():
    app.dependency_overrides[require_desk] = lambda: "Riverside"
    yield TestClient(app)
    app.dependency_overrides.clear()
```

1. The override is any function with the right result: here it always says the desk is at Riverside.
2. `yield` hands the client to the test; after the test, `clear()` removes every override, so the next test starts
   clean.
3. A separate test, without this fixture, still checks that a missing key gives 401.
:::

:::step{type=task task=override_db title="Your turn: a test database" file="15-testing/tests/test_items.py" line="20-21"}
Change the `client` fixture so that it:

1. creates an in-memory engine (`sqlite://` with `StaticPool`) and its tables;
2. overrides `get_session` with a function that yields a session on that engine;
3. yields a `TestClient(app)`, and clears the overrides afterwards.

The imports you need: `from sqlmodel import Session, SQLModel, create_engine`, `from sqlmodel.pool import StaticPool`,
and `get_session` from `main`. Delete `lostdesk.db`, run `python -m pytest -q`, and check it does not come back with
any rows. Then press **Check**: it runs your tests on a copy of Lostdesk whose real database refuses to work, so only
tests that really use your override pass.
:::

:::step{type=concept title="What a good test checks"}
A test that passes proves only what it checks. The check for your next task plants three bugs in copies of Lostdesk
and runs your tests against each: every copy must make at least one test fail. Think like someone who might write
those bugs.

Three habits make tests catch them:

- **Arrange, act, assert.** Prepare the data (`client.post(...)`), do the one thing (`client.get(...)`), then check
  the result. One rule per test, named after the rule: `test_station_filter`.
- **Check the status code, always.** A route that answers 200 instead of 201 still "works" in a browser.
- **Compare whole answers.** `assert response.json() == created` catches a wrong field that
  `assert response.json()["title"] == ...` would miss.

When a test fails, pytest shows exactly where. We changed the solution's `POST` to answer 200 and ran its tests:

```text
.F..                                                                     [100%]
...
    def test_create_gives_201_and_the_new_item(client):
        response = client.post("/items", json=UMBRELLA)
>       assert response.status_code == 201
E       assert 200 == 201
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_items.py:36: AssertionError
...
1 failed, 3 passed in 0.34s
```

The `>` marks the failing line, and `E` lines show both values: got 200, expected 201.
:::

:::step{type=task task=write_tests title="Your turn: tests that catch bugs" file="15-testing/tests/test_items.py" line="24-25"}
Add tests (each using your `client` fixture) that prove:

- `POST /items` answers **201** with the new item, including its `id` and the status `held`;
- the new item can be read back with `GET /items/{id}`, and the answer equals what `POST` gave back;
- `GET /items?station=...` gives only that station's items (create items at two stations first).

```bash run
cd /workspace/15-testing && python -m pytest -q
```

All green on the real app? Then press **Check**. If a planted bug slips through, the check says which rule it broke,
so you know which test to sharpen.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why does the test fixture need `StaticPool` with `sqlite://`?
:::
- [ ] To make the tests faster
- [x] So every session shares one connection, and so one in-memory database
- [ ] Because SQLite needs it for every database
:::explain
Each connection to `sqlite://` gets its own empty database. StaticPool keeps one connection, so the tables created
in the fixture are the ones the routes see.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why clear `app.dependency_overrides` after each test?
:::
- [ ] pytest requires it
- [x] So one test's swap does not leak into the next test
- [ ] To delete the database file
:::explain
`app` is shared by every test in the run. A leftover override would make later tests run against the wrong thing.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
All your tests pass. What does that prove?
:::
- [ ] Lostdesk has no bugs
- [x] Lostdesk does what your tests check, and nothing more
:::explain
That is why the check plants bugs: tests are only as good as the mistakes they can catch.
:::
:::

:::step{type=deep-dive title="Go deeper: what else gets tested"}
**Validation.** One line, `assert client.post("/items", json={"title": "ab", ...}).status_code == 422`, keeps a rule
from being lost in a refactor.

**Parametrize.** `@pytest.mark.parametrize("title", ["", "ab", "x" * 61])` runs one test with many inputs.

**Async tests.** For `async def` code you can test with `httpx.AsyncClient` and an async test runner; FastAPI's docs
have an "Async Tests" page. `TestClient` handles async routes by itself, so most apps never need it.

**Coverage.** `pytest --cov` (the `pytest-cov` plugin) shows which lines no test ran: a map of what is unchecked.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write and run API tests with pytest and `TestClient`, without a server.
- Use fixtures, and swap a dependency in tests with `app.dependency_overrides`.
- Give tests a throwaway in-memory database with `sqlite://` and `StaticPool`.
- Write tests that check status codes, whole answers and filters, and read a red pytest report.

:::photo{src="/lesson-images/fastapi/fa-15-sketch.webp" alt="Sketchnote: Testing your API. Tests call the app with TestClient and check the answers, every time anything changes, on a database of their own. Flow: a fixture prepares, dependency_overrides swaps the database, the test calls the app, assert checks the answer, clear the overrides. Remember: sqlite:// with StaticPool: one in-memory database; Check status codes and whole answers; One rule per test, named after the rule; Passing tests prove only what they check." ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 3. Lostdesk has a database, a package layout and tests. Next, Part 4: production, starting
with passwords and tokens.
:::
