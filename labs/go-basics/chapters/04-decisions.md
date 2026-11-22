:::step{type=story title="Is 0 true or false?"}
Every program decides things. Is this parcel too heavy for the bike? Does it go west or north? Go decides with `if`
and `switch`, and `if` needs a yes or a no.

In JavaScript, you can give `if` almost anything: `0` counts as false, `"hello"` as true. Python is the same. Try that
in Go, and something different happens. By the end of this chapter you will know what, and why Go's designers chose
it.

:::mission
Write `Grade`, which turns marks into a grade (and refuses impossible marks), and `IsLeapYear`, which follows the real
calendar rule.
:::
:::

:::step{type=concept title="if and else"}
`if` asks a yes-or-no question. When the answer is `true`, its block runs; otherwise the `else` block runs:

```go
if kg > 10 {
	fmt.Println("send it by van")
} else {
	fmt.Println("a bike will do")
}
```

No brackets around the condition, and the braces `{ }` are always required, even for one line. Comparisons give a
`bool`, `true` or `false`: `>`, `>=`, `<`, `<=`, `==` (equal) and `!=` (not equal).

:::picture{name="fork-in-road"}
One question, and the answer picks the road.
:::
:::

:::step{type=try title="A shipping price, one question at a time" file="04-decisions/shipping.go" line="8-17"}
Open `shipping.go`. Shipping costs ₹60 up to 2 kg, ₹120 up to 10 kg, and ₹250 above that:

```go
func shipping(kg int) int {
	if kg <= 0 {
		return -1
	} else if kg <= 2 {
		return 60
	} else if kg <= 10 {
		return 120
	}
	return 250
}
```

```bash run
cd /workspace/04-decisions && go run shipping.go
```

```text
60 60 120 250 -1
west north elsewhere
```

Go asks the questions **from the top**, and the first `true` wins: for 3 kg, `kg <= 0` is false, `kg <= 2` is false,
`kg <= 10` is true, so 120. Notice the edges: 2 kg is still ₹60, because `<=` includes 2. Edges are where bugs live.

The second line comes from a `switch`, coming up next.
:::

:::step{type=concept title="switch: many answers, one value"}
When one value is compared against many fixed answers, `switch` reads better than a ladder of `if`s:

```go
switch city {
case "Pune", "Mumbai":
	return "west"
case "Delhi":
	return "north"
default:
	return "elsewhere"
}
```

- A `case` can list several values: `"Pune", "Mumbai"`.
- Go stops after the matching case. There is no `break` to forget, unlike C, Java and JavaScript, where a missing
  `break` quietly runs the next case too.
- `default` runs when nothing else matches.
:::

:::step{type=try title="Can 0 be false?" file="04-decisions/truthy.go" line="8-13"}
Now the question from the start. Open `truthy.go`:

```go
parcels := 0
if parcels {
	fmt.Println("the van has parcels")
}
```

```bash run
cd /workspace/04-decisions && go run truthy.go
```

```text
# command-line-arguments
./truthy.go:10:5: non-boolean condition in if statement
```

Go refuses. An `if` must be given a real `bool`, nothing else. There are no "truthy" or "falsy" values in Go, so a
whole family of JavaScript and Python bugs simply cannot happen. Say what you mean: `if parcels > 0`.
:::

:::step{type=example title="Worked example: impossible values first"}
A star rating from 1 to 5, as words:

```go
func Stars(n int) string {
	if n < 1 || n > 5 {
		return "Invalid"
	} else if n >= 4 {
		return "Loved it"
	} else if n >= 2 {
		return "It was fine"
	}
	return "Not for me"
}
```

1. Impossible values first, so they can never sneak into a real answer.
2. Then the ranges **from the top down**: once `n >= 4` has been ruled out, `n >= 2` only catches 2 and 3.
3. `||` means "or": true when at least one side is true.

Your `Grade` task has this exact shape.
:::

:::step{type=task task=grade title="Your turn: a grade from marks"}
Open `decisions.go` and make `Grade(marks)` give back `"A"` for 80 and up, `"B"` for 60 and up, `"C"` for 40 and up, and
`"F"` below that. Marks below 0 or above 100 give `"Invalid"`.

`Grade(80)` gives `"A"`, `Grade(79)` gives `"B"`, `Grade(39)` gives `"F"`, and `Grade(101)` gives `"Invalid"`.

```bash run
cd /workspace/04-decisions && go run run.go
```

Then press **Check**.
:::

:::step{type=concept title="Combining conditions: && and ||"}
Some decisions need more than one test:

- `a && b` ("and") is true only when **both** are true.
- `a || b` ("or") is true when **at least one** is true.
- `!a` ("not") flips true and false.

The remainder operator `%` tests "divisible by": `2024%4 == 0` is `true`, because 2024 divides by 4 with nothing left
over.
:::

:::step{type=concept title="A rule from 1582"}
A year is about 365.2425 days long, not 365. The old calendar added a leap day every 4 years, slightly too many, and by
1582 it had drifted ten days away from the seasons. Pope Gregory XIII fixed it with the rule we still use: skip the leap
day in years divisible by 100, but keep it in years divisible by 400.

:::photo{src="/lesson-images/python/pope-gregory-xiii.webp" alt="A portrait of Pope Gregory XIII in red robes" credit="Unknown artist" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Pope_Gregory_XIII_portrait.jpg"}
Pope Gregory XIII, whose calendar we still use.
:::
:::

:::step{type=task task=leap_year title="Your turn: is it a leap year?"}
In `decisions.go`, make `IsLeapYear(year)` follow the rule:

1. a year divisible by 4 is a leap year,
2. **except** years divisible by 100,
3. **except** years divisible by 400, which are leap years again.

`IsLeapYear(2024)` is `true`, `IsLeapYear(1900)` is `false`, and `IsLeapYear(2000)` is `true`.

```bash run
cd /workspace/04-decisions && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does Go say to `if count { ... }` when `count` is an `int`?
:::
- [ ] Runs the block when count is not 0
- [x] A compile error: non-boolean condition
:::explain
Go has no truthy values: conditions must be real booleans, like `count > 0`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In a Go `switch`, does the next case run after a matching one?
:::
- [ ] Yes, unless you write `break`
- [x] No, Go stops after the matching case
:::explain
Go ends each case automatically. (The rare opposite wish has its own keyword, `fallthrough`.)
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `true && false || true`?
:::
- [x] `true`
- [ ] `false`
:::explain
`&&` goes first: `true && false` is `false`, then `false || true` is `true`.
:::
:::

:::step{type=deep-dive title="Go deeper: if with a short statement, and switch with no value"}
**if with a short statement.** `if err := save(); err != nil { ... }` runs `save()` and tests its result in one line,
and `err` exists only inside the `if`. You will write this hundreds of times from chapter 7 on.

**switch with no value.** `switch { case kg <= 2: ...; case kg <= 10: ... }` is a tidy ladder of conditions, often
cleaner than `else if`.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Decide with `if`, `else if` and `else`, from the top down, impossible values first.
- Use `switch` with several values per case, knowing Go never falls into the next case.
- Combine conditions with `&&`, `||` and `!`, and test "divisible by" with `%`.
- Explain why Go refuses `if 0`: conditions must be real booleans.

:::photo{src="/lesson-images/go/go-04-notes.webp" alt="Handwritten notes about decisions in Go: if needs a real bool, no brackets but braces always, the first true wins, switch stops after the matching case, and or not, impossible values first" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 5: loops, and the language that needs only one kind of loop.
:::
