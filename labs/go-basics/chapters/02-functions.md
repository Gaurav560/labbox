:::step{type=story title="Can one function give back two answers?"}
Ask most languages how long a 245-second journey is, and a function can hand you one answer: 245 seconds, or 4.08
minutes. Ask Go, and it can hand you **two at once**: 4 minutes **and** 5 seconds.

That is one of Go's small, practical ideas, and the next chapters lean on it constantly. Today you write your first
Go functions, see the two-answer trick, and find out what Go does when you forget an argument. (Spoiler: it refuses,
politely, before the program ever runs.)

:::mission
Write `Greeting`, which builds a welcome message, and `TotalMinutes`, which turns hours and minutes into minutes.
:::
:::

:::step{type=concept title="Why functions exist"}
Imagine Parcel greeting every customer with the same three steps, copied into twenty places. Then the greeting
changes. You would hunt down twenty copies, and miss one.

A **function** fixes that. Write the steps **once**, give them a name, and call the name wherever you need them.
Change the function, and every place that uses it changes too.

:::picture{name="recipe-card"}
A function is a recipe card: name, inputs, steps, result.
:::
:::

:::step{type=concept title="A function, part by part" file="02-functions/split.go" line="8-10"}
Open `split.go`. Its first function:

```go
func minutesAndSeconds(total int) (int, int) {
	return total / 60, total % 60
}
```

- `func` says "here comes a function", and `minutesAndSeconds` is its name.
- `(total int)` is its parameter: a value called `total`, of type `int` (a whole number). In Go, every parameter has
  a type, written **after** its name.
- `(int, int)` after the brackets says what it gives back: **two** whole numbers.
- `return total / 60, total % 60` gives back both: the minutes, and the remainder.
:::

:::step{type=try title="Two answers, and a blank" file="02-functions/split.go" line="12-22"}
The rest of the file uses it:

```go
func describe(name string, seconds int) string {
	m, s := minutesAndSeconds(seconds)
	return fmt.Sprintf("%s: %d min %d s", name, m, s)
}

func main() {
	fmt.Println(minutesAndSeconds(245))
	fmt.Println(describe("Pune to Mumbai", 9015))
	m, _ := minutesAndSeconds(130)
	fmt.Println(m)
}
```

```bash run
cd /workspace/02-functions && go run split.go
```

```text
4 5
Pune to Mumbai: 150 min 15 s
2
```

`m, s := minutesAndSeconds(seconds)` catches both answers in two new variables at once. And look at the last call:
`m, _ :=` keeps only the minutes. The underscore `_` means "I do not need this one", and it is how you tell Go you are
throwing something away **on purpose** (remember: Go refuses unused variables).

`fmt.Sprintf` builds text without printing it: `%s` is replaced by a string, `%d` by a whole number.
:::

:::step{type=try title="Forgetting an argument" file="02-functions/missing.go" line="8-14"}
Open `missing.go`. It calls `describe` with only the name:

```bash run
cd /workspace/02-functions && go run missing.go
```

```text
# command-line-arguments
./missing.go:13:23: not enough arguments in call to describe
	have (string)
	want (string, int)
```

Go refused to build it. And the message is wonderfully exact: you **have** one string, it **wants** a string and an int.
In JavaScript, a missing argument quietly becomes `undefined` and the program carries on with a wrong answer. Go
catches it before anything runs.
:::

:::step{type=example title="Worked example: a function that builds text"}
```go
func Welcome(city string) string {
	return "Welcome to " + city + "!"
}

Welcome("Pune")   // "Welcome to Pune!"
```

1. One parameter, `city`, of type `string`; one result, also a `string`.
2. `+` joins strings in Go. (`fmt.Sprintf("Welcome to %s!", city)` does the same.)
3. A capital first letter, `Welcome`, means other packages may use this function. A small letter, like
   `minutesAndSeconds`, keeps it private to its own package. That is Go's whole rule for public and private.

Your first task has this shape, with different words.
:::

:::step{type=task task=greeting title="Your turn: a greeting"}
Open `hello.go` and make `Greeting(name)` return `"Hello, <name>!"`: `Greeting("Asha")` gives `"Hello, Asha!"`. Mind the
comma, the space and the exclamation mark: the check compares the text exactly.

```bash run
cd /workspace/02-functions && go run run.go
```

Then press **Check**.
:::

:::step{type=concept title="Numbers and arithmetic"}
Go does arithmetic like school maths, with one twist you will meet in the next chapter:

```go
2 + 3*4     // 14: * before +
(2 + 3) * 4 // 20: brackets first
7 % 3       // 1: the remainder
7 / 2       // 3, not 3.5: whole numbers stay whole
```

A function can take two parameters of the same type written together: `func add(a, b int) int`.
:::

:::step{type=predict title="Guess first"}
:::question
`func twice(n int) int { return n * 2 }`. What happens with `twice("7")`?
:::
- [ ] It gives `14`
- [ ] It gives `"77"`
- [x] It does not compile: a string is not an int
:::explain
Go checks every argument's type before running. JavaScript would quietly turn `"7"` into 7; Go refuses.
:::
:::

:::step{type=task task=total_minutes title="Your turn: hours and minutes"}
In `hello.go`, make `TotalMinutes(hours, minutes)` return the total number of minutes: `TotalMinutes(2, 15)` gives
`135`, and `TotalMinutes(0, 45)` gives `45`.

```bash run
cd /workspace/02-functions && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `m, _ := minutesAndSeconds(130)` do with the seconds?
:::
- [ ] Stores them in `_`
- [x] Throws them away, on purpose
- [ ] A compile error
:::explain
The blank identifier `_` accepts a value and discards it, so Go does not complain about an unused variable.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which function can another package call?
:::
- [x] `Greeting`
- [ ] `greeting`
:::explain
In Go, a name starting with a capital letter is exported (public). Small letter means private to the package.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
In `func describe(name string, seconds int) string`, what is the last `string`?
:::
- [ ] A third parameter
- [x] The type of the value it gives back
- [ ] The function's name
:::explain
After the parameters comes the result type: `describe` gives back a string.
:::
:::

:::step{type=deep-dive title="Go deeper: named results, variadic functions and functions as values"}
**Named results.** `func split(total int) (minutes, seconds int)` names the results, which then start at 0 and can be
returned with a bare `return`. Handy for documenting what each answer means.

**Variadic functions.** `func sum(numbers ...int) int` accepts any number of ints: `sum(1, 2, 3)`. `fmt.Println` works
this way.

**Functions are values.** `add := func(a, b int) int { return a + b }` stores a function in a variable, ready to be
passed to another function. Chapter 16 passes functions to goroutines.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write Go functions with typed parameters and a result type, and call them.
- Give back two results at once, catch them with `a, b :=`, and skip one with `_`.
- Build text with `+` and `fmt.Sprintf`, and explain capital (public) versus small (private) names.
- Trust Go to catch a missing or wrong argument before anything runs.

:::photo{src="/lesson-images/go/go-02-notes.webp" alt="Handwritten notes about Go functions: func name, parameter then its type, the result type after the brackets, two results at once, the blank underscore throws one away, capital letter means public" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 3: numbers and text, and whether Go gets 0.1 + 0.2 right.
:::
