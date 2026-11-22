:::step{type=story title="How can an error remember where it came from?"}
A van cannot be dispatched. The error message says so. But **why**? Because loading failed. And why did loading fail?
Because the van was full.

In chapter 7 an error was one plain sentence. Real programs go deeper: one function calls another, which calls
another, and an error from the bottom has to travel up to the top without losing its story, and while staying
recognisable, so the code at the top can still ask "was this the van-is-full problem?". Go solves it with one small
verb, `%w`, and one function, `errors.Is`. You will also meet `defer`, Go's way to clean up on the way out.

:::mission
Write `Withdraw`, which refuses bad amounts and wraps a known error, and `ParseAge`, which wraps the error it got from
`strconv`.
:::
:::

:::step{type=try title="An error wrapped twice" file="13-errors-in-depth/wrap.go" line="11-32"}
Open `wrap.go`:

```go
var ErrNoRoom = errors.New("van is full")

func load(van string, count int) error {
	if count >= 10 {
		return fmt.Errorf("load parcel onto %s: %w", van, ErrNoRoom)
	}
	return nil
}

func dispatch(van string, count int) error {
	if err := load(van, count); err != nil {
		return fmt.Errorf("dispatch failed: %w", err)
	}
	return nil
}
```

```bash run
cd /workspace/13-errors-in-depth && go run wrap.go
```

```text
dispatch failed: load parcel onto Van 7: van is full
true false
true
```

The message tells the whole story, outside in. And look at line two: `errors.Is(err, ErrNoRoom)` is `true`, even though
`err == ErrNoRoom` is `false`. The error at the top is not `ErrNoRoom` itself; it **wraps** it, two layers deep.
:::

:::step{type=concept title="%w wraps, errors.Is looks inside"}
`fmt.Errorf` builds an error from a format, like `Sprintf`. With the special verb `%w` (for "wrap"), the new error
also **keeps** the old one inside it.

Think of Russian **matryoshka** dolls: each one opens to reveal a smaller one inside, all the way down to the
smallest. `%w` puts an error inside a new one; `errors.Is` opens every doll until it finds the one it is looking for.

:::photo{src="/lesson-images/go/matryoshka.webp" alt="Shelves in a glass cabinet filled with many brightly painted matryoshka nesting dolls of different sizes" credit="LR0725" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Many_matryoshka_dolls.jpg"}
Matryoshka dolls: each one holds a smaller one inside.
:::

- `errors.Is(err, ErrNoRoom)` opens every doll, looking for `ErrNoRoom`. That is how the top of a program asks
  "is this the van-is-full problem?" without caring how many layers there are.
- `errors.Unwrap(err)` opens one doll, which is why the third line, unwrapping twice, found `ErrNoRoom`.
- `%v` instead of `%w` would copy the **text** only: the message would look the same, but `errors.Is` would say
  `false`.

A known error stored in a variable, like `ErrNoRoom`, is called a **sentinel error**. By convention its name starts with
`Err`. The `os` package has `os.ErrNotExist`, which chapter 15 uses.

:::

:::step{type=example title="Worked example: a load that refuses"}
```go
var ErrTooHeavy = errors.New("too heavy")

func Load(capacity, kg int) (int, error) {
	if kg <= 0 {
		return capacity, fmt.Errorf("invalid weight %d", kg)
	}
	if kg > capacity {
		return capacity, fmt.Errorf("load %d kg into %d kg of room: %w", kg, capacity, ErrTooHeavy)
	}
	return capacity - kg, nil
}
```

1. A nonsense value gets its own error, made with `fmt.Errorf` so the message names the bad value.
2. The known problem wraps the sentinel with `%w`, so callers can check `errors.Is(err, ErrTooHeavy)`.
3. On every error, the room is returned **unchanged**: a refused load must never half-happen.

Your `Withdraw` has exactly this shape.
:::

:::step{type=task task=withdraw title="Your turn: a withdrawal that refuses"}
Open `bank.go` (the depot's petty cash) and finish `Withdraw(balance, amount)`:

- give back the new balance;
- an amount of 0 or less returns an error;
- an amount bigger than the balance returns an error that **wraps** `ErrInsufficientFunds`, so `errors.Is` finds it;
- on any error, return the balance unchanged.

```bash run
cd /workspace/13-errors-in-depth && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
`err := fmt.Errorf("oops: %v", ErrNoRoom)`. What is `errors.Is(err, ErrNoRoom)`?
:::
- [ ] `true`
- [x] `false`
:::explain
`%v` only copies the text. Only `%w` keeps the original error inside, where `errors.Is` can find it.
:::
:::

:::step{type=task task=parse_age title="Your turn: wrap what strconv tells you"}
In `bank.go`, make `ParseAge(text)` read a whole number from 0 to 150:

- text that is not a number returns an error that **wraps** `strconv`'s error with `%w`, so the caller can still find
  `strconv.ErrSyntax` inside;
- a number outside 0 to 150 returns an error.

```bash run
cd /workspace/13-errors-in-depth && go run run.go
```

Then press **Check**.
:::

:::step{type=try title="defer: clean up on the way out" file="13-errors-in-depth/defer.go" line="8-17"}
Open `defer.go`:

```go
func deliver(stop string) {
	fmt.Println("open the van doors")
	defer fmt.Println("close the van doors")
	defer fmt.Println("lock the van")
	fmt.Println("hand over the parcel at", stop)
}
```

```bash run
cd /workspace/13-errors-in-depth && go run defer.go
```

```text
open the van doors
hand over the parcel at MG Road
lock the van
close the van doors
```

`defer` postpones a call until the function **returns**, however it returns: normally, through an early `return`, or
in a panic. And several defers run **last in, first out**, like a stack of plates. Go programs write
`defer f.Close()` right after opening a file, so it can never be forgotten (chapter 15).
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which verb in `fmt.Errorf` keeps the original error inside the new one?
:::
- [ ] `%v`
- [ ] `%s`
- [x] `%w`
:::explain
`%w` wraps. `%v` and `%s` copy the text only.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A function has `defer fmt.Println("A")` then `defer fmt.Println("B")`. What prints when it returns?
:::
- [ ] A then B
- [x] B then A
:::explain
Deferred calls run last in, first out.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why compare with `errors.Is(err, ErrNoRoom)` instead of `err == ErrNoRoom`?
:::
- [x] Because the error may be wrapped in other errors
- [ ] Because `==` does not work on errors
:::explain
`==` only matches the exact same error. `errors.Is` looks through every layer of wrapping.
:::
:::

:::step{type=deep-dive title="Go deeper: errors.As, custom error types and errors.Join"}
**Custom error types.** Any type with an `Error() string` method is an error (chapter 12's interfaces again):
`type LoadError struct { Van string; Kg int }` can carry details, not just a sentence.

**errors.As.** `var le *LoadError; if errors.As(err, &le) { fmt.Println(le.Van) }` finds an error of a **type** inside
the wrapping, and hands it to you.

**errors.Join.** `errors.Join(err1, err2)` combines several errors into one, for "three of the ten parcels failed".
:::

:::step{type=recap title="What you can do now"}
You can now:

- Wrap an error with `fmt.Errorf("...: %w", err)`, keeping its story and its identity.
- Check for a known error anywhere inside with `errors.Is`, and define sentinel errors named `Err...`.
- Return the value unchanged on every error, so a refused operation never half-happens.
- Use `defer` for clean-up that always runs, last in, first out.

:::photo{src="/lesson-images/go/go-13-notes.webp" alt="Handwritten notes about Go errors in depth: wrap with percent w, errors.Is looks inside every layer, percent v only copies text, sentinel errors start with Err, defer runs on the way out, last in first out" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 14: packages, modules and JSON, so Parcel can save a van's manifest and send it anywhere.
:::
