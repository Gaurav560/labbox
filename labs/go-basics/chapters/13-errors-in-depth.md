:::step{type=story title="Why errors in depth"}
"insufficient funds" alone does not say which account or how much. Real Go code adds context to an
error as it travels up, while keeping the original inside so callers can still recognise it. Go 1.13
added exactly the tools for that.

:::mission
In `bank/bank.go`, write `Withdraw`, which wraps a known error with context, and `ParseAge`, which
wraps `strconv`'s error so callers can still inspect it.
:::
:::

:::step{type=concept title="Sentinel errors and wrapping"}
A **sentinel** error is a named value callers can compare against:

```go
var ErrNotFound = errors.New("not found")
```

`fmt.Errorf` with the `%w` verb adds context **and** keeps the original error inside:

```go
return fmt.Errorf("load user %d: %w", id, ErrNotFound)
// "load user 7: not found"
```

`errors.Is(err, ErrNotFound)` looks through every layer of wrapping and says whether it is in there.
:::

:::step{type=example title="Worked example: wrap a sentinel with context"}
A function that adds context and keeps the original error recognisable:

```go
var ErrNotFound = errors.New("not found")

func FindUser(id int) (string, error) {
	if id != 7 {
		return "", fmt.Errorf("find user %d: %w", id, ErrNotFound)
	}
	return "Riya", nil
}

_, err := FindUser(3)
// err: "find user 3: not found"
// errors.Is(err, ErrNotFound) is true
```

`%w` is the one detail that matters: it wraps, so callers can still recognise `ErrNotFound`. `Withdraw`
does the same with `ErrInsufficientFunds`.

:::trace{title="FindUser(3), then FindUser(7)"}
| call | id != 7? | returns | note |
|---|---|---|---|
| FindUser(3) | true | "", find user 3: not found | %w wraps ErrNotFound inside a message with the id. |
| errors.Is(err, ErrNotFound) | | true | The original error is still inside, so callers can test for it. |
| FindUser(7) | false | "Riya", nil | Found: no error. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
`err := fmt.Errorf("withdraw: %v", ErrInsufficientFunds)`. What is
`errors.Is(err, ErrInsufficientFunds)`?
:::
- [ ] `true`: the message contains it
- [x] `false`: `%v` only copies the text
- [ ] It does not compile
- [ ] It panics
:::explain
`%v` turns the error into text and the original is gone; `errors.Is` compares errors, not messages, so
it returns `false`. Only `%w` **wraps**: then `errors.Is` finds `ErrInsufficientFunds` inside. One
letter decides whether callers can react to the error.
:::
:::

:::step{type=try title="Wrap and unwrap"}
```bash run
cat > /tmp/wrap.go <<'GO'
package main

import (
	"errors"
	"fmt"
)

var ErrLow = errors.New("too low")

func main() {
	a := fmt.Errorf("step 1: %v", ErrLow)
	b := fmt.Errorf("step 1: %w", ErrLow)
	fmt.Println(a, errors.Is(a, ErrLow))
	fmt.Println(b, errors.Is(b, ErrLow))
}
GO
go run /tmp/wrap.go
```
:::

:::step{type=task task=withdraw title="Withdraw money"}
In `bank/bank.go`, make `Withdraw(balance, amount int) (int, error)` return the new balance, or an
error with the **balance unchanged**:

- `Withdraw(500, 200)` returns `300, nil`, and `Withdraw(500, 500)` returns `0, nil`
- an amount of `0` or less is an error of its own (not insufficient funds)
- `Withdraw(100, 250)` returns `100` and an error for which `errors.Is(err, ErrInsufficientFunds)` is
  `true`, with a message that says how much and from what, like
  `withdraw 250 from 100: insufficient funds`
:::

:::step{type=concept title="Errors with details: errors.As"}
:::diagram{name="error-chain"}
Each `%w` adds a layer of context around the error inside; `errors.Is` and `errors.As` look through every layer.
:::

Some errors are types with fields. `strconv.Atoi` returns a `*strconv.NumError` that holds the text it
could not read. `errors.As` finds such an error inside the wrapping and gives you its fields:

```go
var numErr *strconv.NumError
if errors.As(err, &numErr) {
	fmt.Println("could not read", numErr.Num)
}
```

Wrap with `%w` and both `errors.Is` and `errors.As` keep working for your callers.
:::

:::step{type=task task=parse_age title="Read an age"}
In `bank/bank.go`, make `ParseAge(text string) (int, error)` return a whole number from 0 to 150:

- `ParseAge("17")` returns `17, nil`
- `ParseAge("abc")` returns an error that **wraps** strconv's error, so
  `errors.Is(err, strconv.ErrSyntax)` is `true`
- `ParseAge("-1")`, `ParseAge("151")`, `ParseAge("")` and `ParseAge("12.5")` return errors
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which verb wraps an error so `errors.Is` can find it?
:::
- [ ] `%v`
- [ ] `%s`
- [x] `%w`
- [ ] `%e`
:::explain
Only `%w` wraps; `%v` and `%s` just copy the text.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the best way to check for a specific error?
:::
- [ ] `err.Error() == "not found"`
- [x] `errors.Is(err, ErrNotFound)`
- [ ] `strings.Contains(err.Error(), "not")`
- [ ] `err != nil`
:::explain
Compare errors, not their text: messages can change, sentinels do not.
:::
:::

:::step{type=deep-dive title="Handle each error once"}
A common mistake is to log an error **and** return it: then every layer logs it again and one failure
fills the log ten times. Handle each error once: either deal with it (retry, use a default, log and
stop), or add context with `%w` and return it.

Messages read best as a chain of lower-case phrases, no full stops: `load config: open settings.json:
no such file or directory`. Each layer adds only what it knows. And never compare error **text**
(`err.Error() == "..."`): use `errors.Is` and `errors.As`, so a reworded message breaks nothing.
:::

:::step{type=recap}
- A sentinel error (`var ErrX = errors.New(...)`) is a value callers can check.
- `fmt.Errorf("context: %w", err)` adds context and keeps the original; `%v` does not.
- `errors.Is` finds a sentinel inside the wrapping; `errors.As` finds an error type.
- Handle each error once; add context as it travels up.
:::
