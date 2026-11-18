:::step{type=story title="Rupees, paise and bad input"}
:::character{name="Meera" role="CTO, Tapri Counter"}
Our old till service crashes when a cashier types "12.5" instead of "12.50". The new one is in Go,
and I want it to say "that is not an amount" instead of falling over. Start with the money code.
:::

:::mission
Add up prices, and read amounts typed at the till without ever crashing.
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
Returning an error lets the till show "please type an amount like 12.50" instead of crashing at lunch rush.
:::
:::

:::step{type=recap}
- A slice is Go's list; `range` gives the index and the value.
- Functions that can fail return `(value, error)`; always check `err`.
- Split, convert each part, and turn every bad case into an error.
:::
