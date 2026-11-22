:::step{type=story title="Where are Go's exceptions?"}
Python has `try` and `except`. Java and JavaScript have `try` and `catch`. When something goes wrong, they **throw**,
and the problem flies up through your program until someone catches it.

Go has none of that. No `try`, no `catch`, no throwing. So what happens when Parcel reads a weight typed as `twelve`?
The answer is so simple it surprises people: the function **hands the error back to you**, like any other value, and
you decide what to do with it, right there, on the next line. Go programmers love it and joke about it in equal
measure, and by the end of this chapter you will see why.

Errors come with their best friend: the **slice**, Go's list that grows.

:::mission
Write `Total`, which adds up a slice of prices, and `ParseAmount`, which reads an amount like "12.50" or hands back an
error.
:::
:::

:::step{type=try title="A slice that grows" file="07-slices-and-errors/slices.go" line="9-14"}
Open `slices.go`:

```go
var weights []int
fmt.Println(weights, len(weights), weights == nil)
weights = append(weights, 4)
weights = append(weights, 12, 7)
fmt.Println(weights, len(weights), weights[0], weights[len(weights)-1])
fmt.Println(weights[1:3])
```

```bash run
cd /workspace/07-slices-and-errors && go run slices.go
```

```text
[] 0 true
[4 12 7] 3 4 7
[12 7]
```

- `var weights []int` makes an empty slice of ints. Its zero value is `nil`, and a nil slice works fine: length 0.
- `append` gives back a **new** slice with the values added, so you always write `weights = append(weights, ...)`.
- `weights[1:3]` is a **slice of the slice**: positions 1 up to, not including, 3.
:::

:::step{type=example title="Worked example: the heaviest parcel"}
```go
func Heaviest(weights []int) int {
	best := 0
	for _, w := range weights {
		if w > best {
			best = w
		}
	}
	return best
}
```

1. `range` over the slice gives each weight (chapter 5).
2. Keep the best so far, starting at 0, which is also the answer for an empty slice.
3. `Total` is the same shape, with `+=` instead of a comparison.
:::

:::step{type=task task=total title="Your turn: add up prices"}
Open `till.go` (the depot's little counter, which sells boxes and snacks) and make `Total(prices)` return the sum of a
slice of prices in paise. An empty slice gives `0`.

`Total([]int{1500, 2000})` gives `3500`.

```bash run
cd /workspace/07-slices-and-errors && go run run.go
```

Then press **Check**.
:::

:::step{type=concept title="An error is just a value" file="07-slices-and-errors/errors.go" line="12-19"}
Open `errors.go`. `strconv.Atoi` turns text into an int, and gives back **two** things:

```go
for _, text := range []string{"42", "twelve", "7"} {
	n, err := strconv.Atoi(text)
	if err != nil {
		fmt.Println("problem:", err)
		continue
	}
	fmt.Println("parcel weighs", n, "kg")
}
```

```bash run
cd /workspace/07-slices-and-errors && go run errors.go
```

```text
parcel weighs 42 kg
problem: strconv.Atoi: parsing "twelve": invalid syntax
parcel weighs 7 kg
```

No crash, no exception. `Atoi` returned a number **and** an `error`: `nil` when all went well, a description when it
did not. `if err != nil` is the most written line in all of Go. You check it, deal with it, and carry on.

:::picture{name="result-and-note"}
Every call hands back two things: the result, and a note saying whether anything went wrong.
:::
:::

:::step{type=example title="Worked example: your own error"}
```go
var errWeight = errors.New("weight must be 1 to 50 kg")

func ParseWeight(text string) (int, error) {
	kg, err := strconv.Atoi(strings.TrimSpace(text))
	if err != nil || kg < 1 || kg > 50 {
		return 0, errWeight
	}
	return kg, nil
}
```

1. `errors.New` makes an error value with your own message (`import "errors"`).
2. On failure, return the **zero value** (0) together with the error. On success, the value with `nil`.
3. The caller checks `err` first, every time. Bad input never panics; it comes back as an error.

`strings.Cut(text, ".")` splits text at the first dot: `"12.50"` gives `"12"`, `"50"` and `true`. Handy for the next task.
:::

:::step{type=predict title="Guess first"}
:::question
`n, err := strconv.Atoi("12a")`. What are `n` and `err`?
:::
- [ ] `12` and `nil`
- [x] `0` and an error
- [ ] The program panics
:::explain
Bad input comes back as an error, with the zero value for the number. Go functions panic only for real bugs.
:::
:::

:::step{type=task task=parse_amount title="Your turn: read an amount"}
In `till.go`, make `ParseAmount(text)` turn `"12.50"` into `1250` and `"7"` into `700` (paise). Anything else, like `""`,
`"abc"`, `"1.5"`, `"-3"` or `"12.505"`, returns `0` and a non-nil error.

```bash run
cd /workspace/07-slices-and-errors && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why write `weights = append(weights, 4)` and not just `append(weights, 4)`?
:::
- [ ] It is only a style rule
- [x] `append` gives back the new slice; without storing it, the 4 is lost
:::explain
`append` may need a bigger array, so it returns the slice to use from now on. Go refuses an unused result here too.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does a Go function usually do with bad input?
:::
- [ ] Throws an exception
- [x] Returns an error value alongside its result
- [ ] Prints a message and stops
:::explain
Errors are ordinary values in Go. The caller checks `err != nil`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `[]int{4, 12, 7}[1:3]`?
:::
- [ ] `[4 12]`
- [x] `[12 7]`
- [ ] `[12 7 0]`
:::explain
From position 1 up to, but not including, position 3.
:::
:::

:::step{type=deep-dive title="Go deeper: arrays, panics and the great error debate"}
**Arrays.** `[3]int` is an **array**: fixed size, part of its type. Slices are views onto arrays, and you will use
slices 99% of the time. Chapter 9 shows what that "view" means.

**panic.** `panic("...")` exists, for impossible situations (bugs), not for bad input. A panic you do not recover
from stops the program, as you saw in chapter 6.

**The debate.** Some people find `if err != nil` repetitive; Go's designers chose it because every error is visible in
the code, right where it happens. Nothing flies past three functions without anyone noticing.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Make slices, grow them with `x = append(x, ...)`, and take slices of slices.
- Read Go's error style: two results, the value and an `error`, checked with `if err != nil`.
- Return your own errors with `errors.New`, and the zero value on failure.
- Turn text into numbers with `strconv.Atoi` and split text with `strings.Cut`.

:::photo{src="/lesson-images/go/go-07-notes.webp" alt="Handwritten notes about Go slices and errors: append gives back the slice, a nil slice has length 0, no exceptions in Go, value and err, if err not equal nil, errors.New, return 0 and the error" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 8: strings, and why the word café has 5 bytes but 4 letters.
:::
