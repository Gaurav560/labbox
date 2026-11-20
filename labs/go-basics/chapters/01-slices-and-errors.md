:::step{type=story title="Why slices and errors"}
Most programs work on many values at once (a day of prices, a class of marks), and most input can be
wrong. Go handles both in its own simple way: **slices** for lists, and **errors** as ordinary values
that a function returns, instead of exceptions.

:::mission
In `till.go`, add up a slice of prices, and read money amounts typed by a person without ever
crashing.
:::
:::

:::step{type=concept title="Slices and errors"}
A **slice** is Go's list: `[]int{1500, 2000}`. Loop over it with `range`:

```go
for i, p := range prices {
    fmt.Println(i, p)
}
```

Go has no exceptions for normal failures. A function that can fail returns an **error** as its
last value, and the caller checks it:

```go
n, err := strconv.Atoi("12")
if err != nil {
    return 0, err
}
```

:::picture{name="result-and-note"}
Go hands back a result and an error note.
:::
:::

:::step{type=example title="Worked example: parse a whole number safely"}
The Go way to handle input that may be wrong:

```go
func ParseCount(text string) (int, error) {
	n, err := strconv.Atoi(text)
	if err != nil {
		return 0, fmt.Errorf("not a count: %q", text)
	}
	if n < 0 {
		return 0, errors.New("a count cannot be negative")
	}
	return n, nil
}
```

1. A function that can fail returns `(value, error)`.
2. Check `err` right after the call, and return early with a clear message.
3. On success, return the value and `nil`.

`ParseAmount` follows this shape, with a dot between rupees and paise.

:::trace{title="ParseCount with three inputs"}
| text | strconv.Atoi | n < 0? | returns | note |
|---|---|---|---|---|
| "12" | 12, nil |  no | 12, nil | A good count: no error. |
| "abc" | 0, an error |  | 0, not a count: "abc" | Atoi failed: return our own, clearer error. |
| "-3" | -3, nil | yes | 0, a count cannot be negative | It parsed, but it makes no sense as a count. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `strconv.Atoi("12.50")` return?
:::
- [ ] `12, nil`
- [ ] `1250, nil`
- [x] `0` and an error
:::explain
`Atoi` only reads whole numbers. Anything else gives `0` and an error, so you split rupees and paise
first and convert each part on its own.
:::
:::

:::step{type=try title="Run it"}
`cmd/main.go` calls your functions. Run it from the workspace:

```bash run
go run ./cmd
```
:::

:::step{type=task task=total title="Add up prices"}
Make `Total(prices)` return the sum of a slice of prices in paise. An empty slice gives `0`.
:::

:::step{type=task task=parse_amount title="Read an amount"}
Make `ParseAmount(text)` turn `"12.50"` into `1250` and `"7"` into `700` (paise).
Anything else, like `""`, `"abc"`, `"1.5"` or `"-3"`, returns `0` and a non-nil error.

:::why
Returning an error lets a program show "please type an amount like 12.50" instead of crashing.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `strconv.Atoi("12.50")` return?
:::
- [ ] `12, nil`
- [ ] `1250, nil`
- [x] `0` and an error
- [ ] It panics
:::explain
`Atoi` reads only whole numbers, so anything else gives `0` and an error.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `len(nil)` for a nil `[]int`?
:::
- [ ] It panics
- [x] `0`
- [ ] `-1`
- [ ] It does not compile
:::explain
A nil slice behaves like an empty one for `len` and `range`: `0`. That is why `Total(nil)` can simply be `0`.
:::
:::

:::step{type=deep-dive title="Why Go returns errors instead of throwing them"}
In many languages an error jumps out of the function as an exception and may be caught far away, or
not at all. Go makes failure part of the function's signature: `(int, error)` tells every caller that
this can fail, and the `if err != nil` right after the call shows exactly where it is handled.

It is more typing, but control flow stays visible: nothing leaves a function except through a
`return`. Go does have `panic`, but only for programmer mistakes (an index out of range, a nil map
write), never for bad input. Chapter 10 shows how to add context to errors and check them precisely.
:::

:::step{type=recap}
- A slice is Go's list; `range` gives the index and the value.
- Functions that can fail return `(value, error)`; always check `err`.
- Split, convert each part, and turn every bad case into an error.
:::
