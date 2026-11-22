:::step{type=story title="How do you know Mixtape still works tomorrow?"}
Every chapter so far, you pressed **Check** and LabBox told you whether your code worked. Someone wrote those checks.
Real programs have no Check button: somebody has to write it.

And it matters more than you might think. Change one line of Mixtape next month, a small tidy-up, and something three
files away may quietly break: a song length shown as `4:5` instead of `4:05`, and nobody notices until the reviews
come in. Unless there is a **test**: a small program that calls your code with known inputs and shouts the moment an
answer changes.

Node has a test runner **built in**: `node:test`. No downloads, no setup. Today you write the tests yourself.

:::mission
Make a failing test pass by fixing the Skip button, then write tests for `formatDuration` that are good enough to catch
three bugs you cannot see.
:::
:::

:::step{type=try title="Red: a test that fails" file="17-testing/skip.test.js" line="6-12"}
Open `skip.test.js`. A test is a name and a small function:

```js
test("skip moves to the next song", () => {
  assert.equal(nextIndex(0, 3), 1);
});

test("after the last song, back to the first", () => {
  assert.equal(nextIndex(2, 3), 0, "the playlist should wrap around");
});
```

Run every test in the folder:

```bash run
cd /workspace/17-testing && node --test
```

```text
✔ a whole minute (0.511414ms)
✔ skip moves to the next song (0.504916ms)
✖ after the last song, back to the first (0.540481ms)
ℹ tests 3
ℹ pass 2
ℹ fail 1

✖ failing tests:

test at skip.test.js:10:1
✖ after the last song, back to the first (0.540481ms)
  AssertionError [ERR_ASSERTION]: the playlist should wrap around

  3 !== 0
```

(Your timings will differ, and Node prints a few more lines.) `node --test` finds every file ending in `.test.js` and
runs it. A failing test is called **red**. Read the report like a sentence: the test "after the last song, back to the
first", in `skip.test.js` at line 10, failed; its message says why; it got `3` where it expected `0`.
:::

:::step{type=task task=fix_skip title="Your turn: make it green" file="17-testing/skip.js" line="3-7"}
Open `skip.js`. After the last song, Skip should go back to the first one: with 3 songs, the positions are 0, 1, 2, and
after 2 comes 0 again. Find the mistake the test points at, fix it, and run the tests again:

```bash run
cd /workspace/17-testing && node --test
```

When every line starts with `✔`, the run is **green**. Then press **Check**.
:::

:::step{type=concept title="Inside a test"}
Open `duration.test.js`. It has one example:

```js
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { formatDuration } = require("./duration.js");

test("a whole minute", () => {
  assert.equal(formatDuration(60), "1:00");
});
```

- `test(name, fn)` registers a test. Its **name** says the rule it checks.
- `assert.equal(actual, expected)` compares, and fails the test if they differ. In Node, **actual comes first**; the
  failure report then reads `actual !== expected`.
- `assert.throws(() => f(-1), RangeError)` checks that a call throws that kind of error. The arrow function (chapter
  11) lets the assertion make the call itself, and catch it.

Tests are independent: one failure does not stop the others.
:::

:::step{type=example title="Worked example: tests for canAdd"}
Chapter 6's `canAdd(count, limit)` says a playlist may take another song while it has fewer than the limit. Good tests
for it:

```js
test("room left means yes", () => {
  assert.equal(canAdd(9, 10), true);
});

test("at the limit means no", () => {
  assert.equal(canAdd(10, 10), false);
});

test("a negative limit is refused", () => {
  assert.throws(() => canAdd(0, -1), RangeError);
});
```

1. **Test the edges.** `9, 10` and `10, 10` sit on either side of the boundary, exactly where chapter 6's `>=` bug
   lived. Testing `1, 10` and `50, 10` would never have caught it.
2. **One rule per test**, named after the rule. When "at the limit means no" goes red, you know what broke without
   reading a line.
3. `assert.throws` for the refusals, so a function that quietly accepts nonsense fails its test.
:::

:::step{type=concept title="Who tests the tests?"}
Here is a curious question. Your tests pass. Does that prove anything?

Not by itself. A test that checks `formatDuration(60)` and nothing else passes on the correct code, and **also** passes
on a hundred broken versions of it. So professionals test their tests: they break the code on purpose, one small
change at a time, and check that some test goes red. That is called **mutation testing**.

When you press **Check** for your next task, LabBox does exactly that. It runs your `duration.test.js` on the real
`formatDuration` (every test must pass), and then on three copies of it, each with one small bug planted inside. Each
broken copy must make at least one of your tests fail. You will not see the bugs: you have to think like someone who
might write them.
:::

:::step{type=predict title="Guess first"}
:::question
`formatDuration` shows an hour or more as `h:mm:ss`. Which **one** input best catches a bug in where hours start?
:::
- [ ] `formatDuration(60)`
- [x] `formatDuration(3600)`
- [ ] `formatDuration(245)`
:::explain
3600 seconds is exactly one hour, the first value that must show hours: `1:00:00`. Smaller inputs never reach that
rule.
:::
:::

:::step{type=task task=test_duration title="Your turn: tests that catch a broken duration"}
Read `duration.js`. Its `formatDuration(seconds)` is correct:

- `60` gives `"1:00"`, `245` gives `"4:05"` and `5` gives `"0:05"`: seconds always have two digits;
- an hour or more shows hours, with two-digit minutes: `3600` gives `"1:00:00"`, `3725` gives `"1:02:05"`;
- `3599` gives `"59:59"`;
- negative seconds throw a **RangeError**.

In `duration.test.js`, write tests for these rules, so that **any** of three small wrong changes to `formatDuration`
would make at least one test fail. Work out each expected answer from the rules above, not by running the code.

```bash run
cd /workspace/17-testing && node --test
```

All green on the real code? Then press **Check**, and LabBox will try your tests against the broken copies.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which files does `node --test` run?
:::
- [ ] Every `.js` file
- [x] Files whose names end in `.test.js` (and a few similar patterns)
- [ ] Only `test.js`
:::explain
The runner looks for test files by name, so your app's own files are not run as tests.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In `assert.equal(formatDuration(245), "4:05")`, which value is the expected one?
:::
- [ ] `formatDuration(245)`
- [x] `"4:05"`
:::explain
In Node's `assert`, actual comes first and expected second.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Every test passes. What does that prove?
:::
- [ ] The code has no bugs
- [x] The code does what these tests check, and nothing more
:::explain
Tests only prove what they check. That is why good tests target the edges, and why mutation testing tests the tests.
:::
:::

:::step{type=deep-dive title="Go deeper: describe, watch mode, coverage and Jest"}
**describe.** `describe("formatDuration", () => { test(...); test(...); })` groups related tests under one heading.

**Watch mode.** `node --test --watch` reruns the tests every time you save a file: red and green as you type.

**Coverage.** `node --test --experimental-test-coverage` shows which lines your tests ran. A line no test runs is a
line nobody has checked.

**Other runners.** Before `node:test` arrived (Node 18, 2022), the JavaScript world used Jest, Mocha or Vitest. They
look almost the same: `test`, `expect(...).toBe(...)`. Everything you learned here carries over.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Run tests with `node --test` and read a red report: which test, where, the message, actual and expected.
- Write tests with `test`, `assert.equal` and `assert.throws`.
- Choose inputs at the edges of each rule, one rule per test.
- Explain why passing tests are not enough, and how mutation testing checks the tests themselves.

:::photo{src="/lesson-images/javascript/js-17-notes.webp" alt="Handwritten notes about testing with node:test: node --test finds .test.js files, test with a name, assert.equal actual then expected, assert.throws, red then green, test the edges, break the code to test the tests" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 3. Mixtape reads files, runs from the terminal, waits without freezing and proves itself with
tests. One chapter left: the capstone.
:::
