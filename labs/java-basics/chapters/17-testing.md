:::step{type=story title="How do you know Shelf still works tomorrow?"}
Every chapter so far, you pressed **Check** and LabBox told you whether your code worked. Someone wrote those
checks. Real programs have no Check button: someone has to write it.

And it matters more than you might think. Change one line of Shelf next month, a small tidy-up, and something
three files away may quietly break. Nobody would know until a member is charged the wrong fine. Unless there is a
**test**: a small program that calls your code with known inputs and shouts the moment an answer changes.

Java's testing library is **JUnit**. It is so central that Kent Beck and Erich Gamma wrote its first version on a
plane, in 1997, and today almost every Java project on Earth, Spring Boot included, uses it. Today you write the
tests yourself.

:::mission
Make a failing test pass by fixing `Renewals`, then write tests for `lateFee` that are good enough to catch three
bugs you cannot see.
:::
:::

:::step{type=try title="Red: a test that fails" file="17-testing/src/test/java/shelf/RenewalsTest.java" line="20-23"}
Open `src/test/java/shelf/RenewalsTest.java`. A test is a method with `@Test` on top:

```java
@Test
void noThirdRenewal() {
    assertFalse(Renewals.canRenew(2, false), "two renewals already: a third is not allowed");
}
```

Run every test in the project:

```bash run
cd /workspace/17-testing && mvn -o -q test
```

```text
[ERROR] Tests run: 3, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.114 s <<< FAILURE! -- in shelf.RenewalsTest
[ERROR] shelf.RenewalsTest.noThirdRenewal -- Time elapsed: 0.099 s <<< FAILURE!
org.opentest4j.AssertionFailedError: two renewals already: a third is not allowed ==> expected: <false> but was: <true>
```

Testers call a failing test **red**. Read the report like a sentence: in `RenewalsTest`, the test `noThirdRenewal`
failed; its message says why; it **expected** `false`, but `canRenew(2, false)` **was** `true`. A good test does not
just say "wrong": it says what it wanted and what it got.
:::

:::step{type=task task=fix_renewal title="Your turn: make it green" file="17-testing/src/main/java/shelf/Renewals.java" line="5-9"}
Open `src/main/java/shelf/Renewals.java`. A loan may be renewed at most twice, and never while another member has
reserved the book. Find the mistake the test points at, fix it, and run the tests again:

```bash run
cd /workspace/17-testing && mvn -o -q test
```

With `-q`, success is silence: no `ERROR` lines at all. That is a **green** run. Then press **Check**.
:::

:::step{type=concept title="Inside a test"}
Open `src/test/java/shelf/FinesTest.java`. It has one example:

```java
class FinesTest {
    @Test
    void onTimeIsFree() {
        assertEquals(0, Fines.lateFee(0));
    }
}
```

- The test class lives in `src/test/java`, in the **same package** as the code it tests, `shelf`. Maven runs
  every class there whose name ends in `Test`, and never puts them in the jar.
- `@Test` marks a method JUnit should run. Its name says the rule it checks: `onTimeIsFree`.
- `assertEquals(expected, actual)` compares, and fails the test if they differ. **Expected first**: get the order
  wrong and the report reads backwards.
- `assertTrue`, `assertFalse` and `assertThrows` complete the everyday toolbox. They are imported with
  `import static`, so you can write them without `Assertions.` in front.

Each test is independent: JUnit runs them in any order, and one failure does not stop the others.
:::

:::step{type=example title="Worked example: tests for canBorrow"}
Take a version of chapter 6's `canBorrow(have, limit)` that also refuses a negative limit: a member may borrow
while they have fewer books than the limit. Good tests for it:

```java
class LimitsTest {
    @Test
    void roomLeftMeansYes() {
        assertTrue(Limits.canBorrow(4, 5));
    }

    @Test
    void atTheLimitMeansNo() {
        assertFalse(Limits.canBorrow(5, 5));
    }

    @Test
    void aNegativeLimitIsRefused() {
        assertThrows(IllegalArgumentException.class, () -> Limits.canBorrow(0, -1));
    }
}
```

1. **Test the edges.** `4, 5` and `5, 5` sit on either side of the rule's boundary, exactly where chapter 6's
   `>=` bug lived. Testing `1, 5` and `9, 5` would never have caught it.
2. **One rule per test**, named after the rule. When `atTheLimitMeansNo` goes red, you know what broke without
   reading a line.
3. `assertThrows` takes a lambda (chapter 14): JUnit calls it and checks that it throws that kind of exception.
:::

:::step{type=concept title="Who tests the tests?"}
Here is a curious question. Your tests pass. Does that prove anything?

This happened to a telescope. The **Hubble Space Telescope**'s main mirror was polished to the wrong shape, by about
one fiftieth of a hair's width, because the instrument used to test it had one lens 1.3 mm out of place. The test
said "perfect", and Hubble's first pictures came back blurred. Astronauts had to fit corrective optics in 1993.

:::photo{src="/lesson-images/java/hubble.webp" alt="The Hubble Space Telescope, wrapped in shiny silver foil, raised above the Space Shuttle with the Earth below" credit="NASA" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Hubble_Space_Telescope_(HST)_above_OV-103%27s_PLB_during_STS-31_deployment.jpg"}
Hubble being released from the Space Shuttle Discovery, 1990.
:::

Not by itself. A test that checks `lateFee(0)` and nothing else passes on the correct code, and **also** passes on
a hundred broken versions of it. So professionals test their tests: they break the code on purpose, one small
change at a time, and check that some test goes red. This is called **mutation testing**.

When you press **Check** for your next task, LabBox does exactly that. It runs your `FinesTest` on the real
`lateFee` (every test must pass), and then on three copies of `lateFee`, each with one small bug planted inside.
Each broken copy must make at least one of your tests fail. You will not see the bugs: you have to think like
someone who might write them.

Try it yourself in one second: change `assertEquals(0, ...)` to `assertEquals(1, ...)`, run `mvn -o -q test`, watch
it go red, and change it back.

:::

:::step{type=predict title="Guess first"}
:::question
The fee is 2 rupees a day for the first 7 days, then 5 a day. Which **one** test is most likely to catch a bug in
where the second rate starts?
:::
- [ ] `lateFee(3)`
- [x] `lateFee(8)`
- [ ] `lateFee(0)`
:::explain
Day 8 is the first day of the second rate. A bug that starts it a day early or late changes `lateFee(8)` (or
`lateFee(7)`), while `lateFee(3)` is the same either way.
:::
:::

:::step{type=task task=test_late_fee title="Your turn: tests that catch a broken late fee"}
Read `src/main/java/shelf/Fines.java`. Its `lateFee(daysLate)` is correct:

- 0 days late costs nothing;
- 2 rupees a day for the first 7 days, so 7 days late costs 14;
- 5 rupees a day after that, so 8 days late costs 19 and 10 days late costs 29;
- never more than 100;
- a negative number of days throws an `IllegalArgumentException`.

In `FinesTest.java`, write tests for these rules, so that **any** of three small wrong changes to `lateFee` would
make at least one of your tests fail. Work out each expected number by hand from the rules, not by running the code.

```bash run
cd /workspace/17-testing && mvn -o -q test
```

All green on the real code? Then press **Check**, and LabBox will try your tests against the broken copies.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In `assertEquals(19, Fines.lateFee(8))`, which value is the expected one?
:::
- [x] `19`
- [ ] `Fines.lateFee(8)`
:::explain
Expected first, actual second. The report then reads `expected: <19> but was: <...>`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A test file `FinesTest.java` lives in `src/test/java/shelf/`. Does its class go into `target/shelf.jar`?
:::
- [ ] Yes, with everything else
- [x] No: tests are compiled and run, but never packed into the jar
:::explain
Maven keeps tests out of the jar. They are for the people building the program, not for its users.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Every test passes. What does that prove?
:::
- [ ] The code has no bugs
- [x] The code does what these tests check, and nothing more
- [ ] The tests are good
:::explain
Tests only prove what they check. That is why good tests target the edges, and why mutation testing tests the tests.
:::
:::

:::step{type=deep-dive title="Go deeper: test first, parameterized tests and coverage"}
**Test-driven development.** Kent Beck's famous habit: write a failing test first (red), write just enough code to
pass it (green), then tidy the code while the tests protect you (refactor). Red, green, refactor.

**Parameterized tests.** One test, many inputs:
`@ParameterizedTest @CsvSource({"7, 14", "8, 19", "25, 100"})` with a method that takes `(int days, int fee)`. JUnit
runs it once per row.

**Coverage.** Tools like JaCoCo show which lines your tests ran. A line no test runs is a line nobody has checked;
but running a line is not the same as checking its answer, which is what mutation testing (the PIT tool for Java)
measures.

**Spring Boot tests.** The Spring Boot course uses this same JUnit, plus tools that start the web app or the
database inside a test.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Run a project's tests with `mvn -o -q test`, and read a red report: which test, expected, and actual.
- Write JUnit tests with `@Test`, `assertEquals`, `assertTrue`, `assertFalse` and `assertThrows`.
- Choose test inputs at the edges of each rule, one rule per test.
- Explain why passing tests are not enough, and how mutation testing checks the tests themselves.

:::photo{src="/lesson-images/java/java-17-notes.webp" alt="Handwritten notes about JUnit: @Test, assertEquals expected first, red then green, test the edges, one rule per test, assertThrows with a lambda, break the code to test the tests" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 3. Shelf reads files, runs from the terminal, builds into a jar and proves itself with
tests. One chapter left: the capstone.
:::
