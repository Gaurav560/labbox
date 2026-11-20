:::step{type=story title="Why decisions"}
Grades depend on marks, fees depend on age, a login depends on the password. `if` and `switch` are
how a Go program chooses, and Go keeps both short and strict.

:::mission
In `decisions/decisions.go`, turn marks into a grade, and decide whether a year is a leap year.
:::
:::

:::step{type=concept title="if and else"}
Go's `if` needs no brackets around the condition, but always needs braces:

```go
if marks >= 40 {
	return "pass"
} else if marks >= 33 {
	return "retest"
} else {
	return "fail"
}
```

Conditions use `== != < <= > >=`, combined with `&&` (and), `||` (or) and `!` (not). An `if` can
start with a short statement: `if n, err := strconv.Atoi(s); err == nil { ... }`.
:::

:::step{type=example title="Worked example: a ticket price by age"}
A `switch` with no value is a list of rules, checked from the top:

```go
func Ticket(age int) string {
	switch {
	case age < 0:
		return "Invalid"
	case age >= 60:
		return "Senior"
	case age >= 18:
		return "Adult"
	default:
		return "Child"
	}
}
```

1. Impossible values first.
2. Then the ranges from the top down: the first matching `case` wins.
3. `default` catches everything left.

`Grade` uses the same layout with marks.
:::

:::step{type=predict title="Guess first"}
:::question
What does `level(90)` return?

```go
func level(marks int) string {
	if marks >= 40 {
		return "pass"
	} else if marks >= 80 {
		return "distinction"
	}
	return "fail"
}
```
:::
- [x] `"pass"`
- [ ] `"distinction"`
- [ ] `"fail"`
- [ ] It does not compile
:::explain
Conditions are checked **from the top** and the first true one wins: `90 >= 40` already is, so the
`80` branch is never reached. Put the strictest condition first.
:::
:::

:::step{type=try title="A switch"}
```bash run
cat > /tmp/sw.go <<'GO'
package main

import "fmt"

func main() {
	for _, m := range []int{95, 70, 30} {
		switch {
		case m >= 80:
			fmt.Println(m, "high")
		case m >= 50:
			fmt.Println(m, "middle")
		default:
			fmt.Println(m, "low")
		}
	}
}
GO
go run /tmp/sw.go
```

A `switch` with no value is a tidy list of conditions. Go's cases do not fall through: no `break`
needed.
:::

:::step{type=task task=grade title="Grades from marks"}
In `decisions/decisions.go`, make `Grade(marks int) string` return:

| Marks | Grade |
|---|---|
| 80 to 100 | `"A"` |
| 60 to 79 | `"B"` |
| 40 to 59 | `"C"` |
| 0 to 39 | `"F"` |
| below 0 or above 100 | `"Invalid"` |

Edges matter: `Grade(80)` is `"A"`, `Grade(79)` is `"B"`, `Grade(101)` is `"Invalid"`.
:::

:::step{type=concept title="Combining conditions"}
```go
teen := age >= 13 && age <= 19
canEnter := age >= 18 || withParent
divisible := year%4 == 0
```

`%` gives the remainder, so `x%n == 0` means "divisible by n". Go evaluates `&&` and `||` left to
right and stops as soon as the answer is known.
:::

:::step{type=task task=leap_year title="Leap years"}
In `decisions/decisions.go`, make `IsLeapYear(year int) bool` follow the real rule:

1. a year divisible by 4 is a leap year,
2. **except** years divisible by 100,
3. **except** years divisible by 400, which are leap years again.

`2024` is `true`, `2023` is `false`, `1900` is `false`, `2000` is `true`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Does Go need `break` at the end of each `case`?
:::
- [ ] Yes, always
- [x] No: cases do not fall through
- [ ] Only in a `switch` with a value
- [ ] Only for the last case
:::explain
Go cases stop by themselves; you would write `fallthrough` on purpose if you ever wanted the next case to run.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Does `if count { ... }` compile when `count` is an `int`?
:::
- [ ] Yes
- [x] No: a condition must be a `bool`
- [ ] Only if count is not zero
- [ ] Only inside a function
:::explain
Go has no truthy values. Write the comparison you mean: `if count > 0 { ... }`.
:::
:::

:::step{type=deep-dive title="Why Go has no ternary operator"}
Many languages have `cond ? a : b`. Go left it out on purpose: nested ternaries become unreadable, and
an `if` with a `return` (or a variable set in each branch) says the same thing plainly.

Go also has no "truthy" values: `if count {` does not compile; you write `if count > 0 {`. Only a real
`bool` can be a condition, which removes a whole class of bugs where `0`, `""` or `nil` were treated as
false by accident.
:::

:::step{type=recap}
- `if cond { } else if { } else { }`: no brackets, always braces.
- The first true branch wins: strictest condition first.
- `switch { case cond: }` is a tidy list of rules, with no fall-through.
- Only real `bool` values can be conditions; `%` checks divisibility.
:::
