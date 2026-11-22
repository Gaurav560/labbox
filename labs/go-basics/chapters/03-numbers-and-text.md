:::step{type=story title="Does Go get 0.1 + 0.2 right?"}
In most languages, `0.1 + 0.2` prints `0.30000000000000004`: computers store decimals in binary, and 0.1 cannot be
written exactly. Ask Go:

```text
0.3
```

Perfect. Has Go fixed computer maths? Now store the same numbers in two variables first, and add those. You will see
the answer in a minute, and the reason is one of Go's cleverest and least known ideas. Along the way you will meet
Go's strictness about **types**: whole numbers, decimals and text are never quietly mixed.

:::mission
Write `Percent`, a safe percentage that never divides by zero, and `FormatRupees`, which shows an amount of money
exactly right.
:::
:::

:::step{type=concept title="Variables and types"}
A **variable** is a name for a value. Go has two ways to make one:

```go
var weight int = 12     // the long way: name, type, value
parcels := 3            // the short way: Go works out the type (int)
price := 249.50         // a float64: a number with a decimal point
label := "fragile"      // a string
```

Every variable has a **type**, decided once and forever. `parcels = "three"` is a compile error: `parcels` is an `int`
and will always be one.

:::picture{name="labelled-jars"}
The labels name the values, and each jar holds only one kind of thing.
:::
:::

:::step{type=try title="Five lines, five surprises" file="03-numbers-and-text/surprises.go" line="9-16"}
Open `surprises.go` and run it:

```go
fmt.Println(0.1 + 0.2)
a, b := 0.1, 0.2
fmt.Println(a + b)
fmt.Println(7/2, 7.0/2, float64(7)/2)
var small int8 = 127
small++
fmt.Println(small)
fmt.Printf("%.2f %5d| %q %T\n", 3.14159, 42, "box", 42)
```

```bash run
cd /workspace/03-numbers-and-text && go run surprises.go
```

```text
0.3
0.30000000000000004
3 3.5 3.5
-128
3.14    42| "box" int
```

The same sum, two answers. Here is why.
:::

:::step{type=concept title="Exact constants, and ordinary variables"}
**Line 1 is a constant.** `0.1 + 0.2` written directly in the code is a **constant expression**, and Go does
constant maths **exactly**, with as many digits as it needs, at compile time. Exactly 0.3 is then stored, and 0.3 is
printed.

**Line 2 uses variables.** `a` and `b` are `float64` variables: real binary decimals, with the same tiny leftover as
every other language. The surprise is not that Go gets it wrong; it is that constants get it **right**.

**Line 3:** `7/2` is two whole numbers, so the answer is whole: `3`. Make one side a decimal (`7.0`) or convert it
with `float64(7)`, and you get `3.5`. Go never converts for you.

**Line 4:** an `int8` holds -128 to 127. Add 1 to 127 and it **wraps around** to -128, silently. Go's normal `int` is
huge (up to about 9 quintillion), so this rarely bites, but now you know.

**Line 5:** `fmt.Printf` formats: `%.2f` two decimals, `%5d` a number padded to 5 wide, `%q` a quoted string, `%T`
the type of a value.

Wrapping around is not only a computer thing. A car's odometer has six digits, so after 99,999.9 miles it rolls
back to all zeros, exactly like an `int8` going from 127 to -128: the counter simply has no room for more.

:::photo{src="/lesson-images/go/odometer.webp" alt="Three close-ups of a car odometer: reading 99999.9, rolling over, then showing all zeros" credit="Hellbus" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Odometer_rollover.jpg"}
An odometer rolling over from 99999.9 to zero.
:::
:::

:::step{type=try title="A number and some text" file="03-numbers-and-text/mismatch.go" line="8-12"}
JavaScript happily computes `5 + "kg"` and gives `"5kg"`. Open `mismatch.go`, which tries the same in Go:

```bash run
cd /workspace/03-numbers-and-text && go run mismatch.go
```

```text
# command-line-arguments
./mismatch.go:11:14: invalid operation: weight + label (mismatched types int and string)
```

Refused. To join them, convert on purpose: `fmt.Sprint(weight) + label`, or `fmt.Sprintf("%d%s", weight, label)`. Go
makes you say exactly what you mean, every time.
:::

:::step{type=example title="Worked example: an average, rounded"}
```go
func Average(a, b, c int) float64 {
	exact := float64(a+b+c) / 3
	return math.Round(exact*10) / 10
}

Average(7, 8, 8)   // 7.7
```

1. Add the whole numbers, then convert to `float64` **before** dividing, or `23 / 3` would be `7`.
2. `math.Round(7.666... * 10)` is `77`; divided by 10 that is `7.7`. (`import "math"` at the top.)
3. And a guard: dividing a `float64` by zero gives `+Inf`, and dividing an `int` by zero **panics**. Check first. Your
   first task needs exactly that check.
:::

:::step{type=predict title="Guess first"}
:::question
What is `9 / 4` in Go?
:::
- [ ] `2.25`
- [x] `2`
- [ ] `3`
:::explain
Two whole numbers give a whole number: the decimal part is cut off, not rounded. `9.0 / 4` gives 2.25.
:::
:::

:::step{type=task task=percent title="Your turn: a safe percentage"}
Open `numbers.go` and make `Percent(scored, total)` give back `scored` as a percentage of `total`, rounded to one
decimal. When `total` is `0`, give back `0`.

`Percent(45, 50)` gives `90`, `Percent(1, 3)` gives `33.3`, and `Percent(7, 0)` gives `0`.

```bash run
cd /workspace/03-numbers-and-text && go run run.go
```

Then press **Check**.
:::

:::step{type=concept title="Money: whole paise, shown as rupees"}
Because decimals are not exact, shops and banks keep money as **whole paise** (an `int`), and only turn it into
rupees for display. Integer division and the remainder do the work:

```go
paise := 1999
paise / 100   // 19: the rupees
paise % 100   // 99: the paise left over
fmt.Sprintf("%02d", 5)   // "05": at least 2 digits, padded with 0
```
:::

:::step{type=task task=format_rupees title="Your turn: show an amount in rupees"}
In `numbers.go`, make `FormatRupees(paise)` return the amount as text with the ₹ sign and two decimals:
`FormatRupees(1250)` gives `"₹12.50"`, and `FormatRupees(5)` gives `"₹0.05"`.

```bash run
cd /workspace/03-numbers-and-text && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`a, b := 0.1, 0.2` then `a + b`. What prints?
:::
- [ ] `0.3`
- [x] `0.30000000000000004`
:::explain
Variables are ordinary binary floats. Only constant expressions written straight in the code are exact.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
How do you get 3.5 from the ints 7 and 2?
:::
- [ ] `7 / 2`
- [x] `float64(7) / 2`
- [ ] `int(7 / 2)`
:::explain
Convert to `float64` before dividing; Go never converts types for you.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `%02d` do to the number 5?
:::
- [x] Shows it as `05`
- [ ] Shows it as `5.00`
- [ ] Shows it as `52`
:::explain
At least 2 digits wide, padded with zeros: exactly what the paise part of a price needs.
:::
:::

:::step{type=deep-dive title="Go deeper: sizes of int, runes and math/big"}
**Sizes.** Go has `int8`, `int16`, `int32`, `int64` and plain `int` (64 bits on modern machines), plus unsigned
`uint` versions. Use plain `int` unless you have a reason.

**Runes.** A single character in single quotes, `'A'`, is a **rune**: a number (65) that stands for a character.
Chapter 8 shows why that matters for text like "café".

**math/big.** For money that must never overflow, or numbers with hundreds of digits, the `math/big` package gives
exact big integers and decimals.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Make variables with `var` and `:=`, and know that a variable's type never changes.
- Explain why `0.1 + 0.2` is exact as a constant and not as variables.
- Convert between types on purpose (`float64(n)`), knowing `7 / 2` is 3.
- Format numbers with `fmt.Sprintf` and `%d`, `%02d`, `%.2f`, and keep money in whole paise.

:::photo{src="/lesson-images/go/go-03-notes.webp" alt="Handwritten notes about numbers in Go: colon equals makes a variable, a type never changes, constants are exact so 0.1 plus 0.2 is 0.3, variables are not, 7 divided by 2 is 3, float64 to convert, money in whole paise" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 4: decisions, and why Go will not let you write `if 0`.
:::
