:::step{type=story title="What if the language came with its own tester?"}
Every chapter so far, you pressed **Check** and LabBox told you whether your code worked. Someone wrote those checks,
in Go, with a tool every Go programmer has: `go test`. It is not a library you download. It ships with Go itself, and
every Go project in the world, including Go's own compiler, is tested with it.

Tests matter more than you might think. Change one line of Parcel next month, and a delivery time could quietly show
`1 h 5 min` instead of `1 h 05 min`. Nobody notices, until a test notices for you, the moment you run it. Today you
write the tests yourself.

:::mission
Make a failing test pass by fixing `NextStop`, then write a table of tests for `FormatETA` that is good enough to catch
three bugs you cannot see.
:::
:::

:::step{type=try title="Red: a test that fails" file="17-testing/stops_test.go" line="6-16"}
Open `stops_test.go`. A test is a function whose name starts with `Test`, in a file ending in `_test.go`:

```go
func TestNextStopWrapsToTheDepot(t *testing.T) {
	if got := NextStop(2, 3); got != 0 {
		t.Errorf("NextStop(2, 3) = %d, want 0: after the last stop, back to the depot", got)
	}
}
```

Run every test in the folder:

```bash run
cd /workspace/17-testing && go test
```

```text
--- FAIL: TestNextStopWrapsToTheDepot (0.00s)
    stops_test.go:14: NextStop(2, 3) = 3, want 0: after the last stop, back to the depot
FAIL
exit status 1
FAIL	labbox/lab/17-testing	0.001s
```

A failing test is called **red**. Read it like a sentence: the test `TestNextStopWrapsToTheDepot` failed at
`stops_test.go` line 14, and its message says what it got (3) and what it wanted (0). `t.Errorf` reports a failure and
lets the test carry on; `go test` runs every test and only says `ok` when all of them pass.
:::

:::step{type=task task=fix_next_stop title="Your turn: make it green" file="17-testing/stops.go" line="4-8"}
Open `stops.go`. With 3 stops, the positions are 0, 1 and 2; after the last one, the van returns to the depot, 0.
Find the mistake the test points at, fix it, and run the tests again:

```bash run
cd /workspace/17-testing && go test
```

```text
PASS
ok  	labbox/lab/17-testing	0.001s
```

That is a **green** run. Then press **Check**.
:::

:::step{type=concept title="Table-driven tests"}
Go programmers rarely write one test per input. They write a **table**: a slice of cases, and one loop. Open
`eta_test.go`:

```go
func TestFormatETA(t *testing.T) {
	cases := []struct {
		minutes int
		want    string
	}{
		{45, "45 min"},
	}
	for _, c := range cases {
		got, err := FormatETA(c.minutes)
		if err != nil || got != c.want {
			t.Errorf("FormatETA(%d) = %q, %v; want %q", c.minutes, got, err, c.want)
		}
	}
}
```

- `[]struct{ minutes int; want string }` is a slice of anonymous structs: each row is one case.
- Adding a case is one line. Ten edge cases cost ten lines, not ten functions.
- The message names the input, what came back, and what was wanted, so a red test explains itself.

Get the expected answer wrong, and the test tells you just as clearly. A case `{65, "1 h 5 min"}` gives:

```text
--- FAIL: TestFormatETA (0.00s)
    eta_test.go:18: FormatETA(65) = "1 h 05 min", <nil>; want "1 h 5 min"
```

Before blaming the code, check the rule: minutes always have two digits. Here the **test** was wrong.
:::

:::step{type=example title="Worked example: tests for CanLoad"}
Chapter 6's `CanLoad(count, limit)` says a van may take another parcel while it holds fewer than its limit. A good
table for it:

```go
func TestCanLoad(t *testing.T) {
	cases := []struct {
		count, limit int
		want         bool
	}{
		{9, 10, true},
		{10, 10, false},
		{0, 0, false},
	}
	for _, c := range cases {
		if got := CanLoad(c.count, c.limit); got != c.want {
			t.Errorf("CanLoad(%d, %d) = %v, want %v", c.count, c.limit, got, c.want)
		}
	}
}
```

1. **Test the edges.** `9, 10` and `10, 10` sit on either side of the boundary, exactly where chapter 6's `>=` bug
   lived. `1, 10` would never have caught it.
2. **Name what each row proves**, in your head or in a comment: "one short of full", "exactly full", "no room at all".
3. Errors are tested too: `if _, err := F(-1); err == nil { t.Error("want an error") }`.
:::

:::step{type=concept title="Who tests the tests?"}
Here is a curious question. Your tests pass. Does that prove anything?

Not by itself. A table with only `{45, "45 min"}` passes on the correct code, and **also** on a hundred broken versions
of it. So professionals test their tests: they break the code on purpose, one small change at a time, and check that
some test goes red. That is called **mutation testing**.

When you press **Check** for your next task, LabBox does exactly that. It runs your `eta_test.go` against the real
`FormatETA` (every case must pass), and then against three copies of it, each with one small bug planted inside. Each
broken copy must make your test fail.
:::

:::step{type=predict title="Guess first"}
:::question
`FormatETA` shows hours from 60 minutes up. Which **one** case best catches a bug in where hours start?
:::
- [ ] `{45, "45 min"}`
- [x] `{60, "1 h 00 min"}`
- [ ] `{200, "3 h 20 min"}`
:::explain
60 is exactly the first value that must show hours. A bug that starts hours at 120 would still pass the other two.
:::
:::

:::step{type=task task=test_eta title="Your turn: a table that catches a broken ETA"}
Read `eta.go`. Its `FormatETA(minutes)` is correct:

- under an hour: `45` gives `"45 min"`, `0` gives `"0 min"`, `59` gives `"59 min"`;
- an hour or more shows hours, with **two-digit** minutes: `60` gives `"1 h 00 min"`, `65` gives `"1 h 05 min"`, `125`
  gives `"2 h 05 min"`;
- negative minutes return an **error**.

Add cases to the table in `eta_test.go` (and a small test for the error), so that **any** of three small wrong changes
to `FormatETA` would make your tests fail. Work out each expected answer from the rules, not by running the code.

```bash run
cd /workspace/17-testing && go test -v
```

All green on the real code? Then press **Check**, and LabBox will try your tests against the broken copies.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which files does `go test` run tests from?
:::
- [ ] Every `.go` file
- [x] Files ending in `_test.go`, functions starting with `Test`
:::explain
Test files are compiled only by `go test`, never into your program.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is the difference between `t.Errorf` and `t.Fatalf`?
:::
- [x] `Errorf` reports and carries on; `Fatalf` reports and stops this test
- [ ] There is none
:::explain
Use `Fatalf` when the rest of the test cannot make sense, like after a failed setup.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Every test passes. What does that prove?
:::
- [ ] The code has no bugs
- [x] The code does what these tests check, and nothing more
:::explain
Tests only prove what they check: that is why good tables cover the edges, and why mutation testing tests the tests.
:::
:::

:::step{type=deep-dive title="Go deeper: subtests, coverage, benchmarks and fuzzing"}
**Subtests.** `t.Run(name, func(t *testing.T) { ... })` inside the loop gives every row its own name in the report,
and `go test -run TestFormatETA/one_hour` runs just that one.

**Coverage.** `go test -cover` prints the share of lines your tests ran; `go test -coverprofile` shows which.

**Benchmarks.** `func BenchmarkFormatETA(b *testing.B)` and `go test -bench .` measure speed.

**Fuzzing.** `func FuzzFormatETA(f *testing.F)` lets Go invent thousands of inputs looking for a crash. All built in,
no downloads.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Run tests with `go test`, and read a red report: test name, file and line, got and want.
- Write tests: `func TestX(t *testing.T)` in a `_test.go` file, reporting with `t.Errorf`.
- Write table-driven tests: a slice of cases and one loop, with the edges in the table.
- Explain why passing tests are not enough, and how mutation testing checks the tests themselves.

:::photo{src="/lesson-images/go/go-17-notes.webp" alt="Handwritten notes about go test: files end in _test.go, func TestX with t testing.T, t.Errorf reports and carries on, a table of cases and one loop, test the edges, red then green, break the code to test the tests" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 3. Parcel handles errors, speaks JSON, reads files, runs from the terminal, does many things at
once and proves itself with tests. One chapter left: the capstone.
:::
