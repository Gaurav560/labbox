:::step{type=story title="Why numbers and text"}
Marks, prices, percentages: almost every program does arithmetic and shows the result as text. Go is
stricter than many languages about mixing number types, and that strictness catches real bugs.

:::mission
In `numbers/numbers.go`, write `Percent`, which needs a careful division, and `FormatRupees`, which
turns paise into a price like `₹12.50`.
:::
:::

:::step{type=concept title="int, float64 and string"}
Go's everyday types:

```go
marks := 45          // int
price := 49.5        // float64
name := "Riya"       // string
ok := true           // bool
```

Go never mixes types silently. To combine an `int` with a `float64`, convert one yourself:

```go
avg := float64(total) / float64(count)
```
:::

:::step{type=predict title="Guess first"}
:::question
What does `fmt.Println(45 / 50 * 100)` print?
:::
- [ ] `90`
- [x] `0`
- [ ] `90.0`
- [ ] It does not compile
:::explain
`45` and `50` are both `int`, so `45 / 50` is integer division: `0`, with the fraction thrown away.
`0 * 100` is still `0`. Convert to `float64` **before** dividing: `float64(45) / float64(50) * 100`
is `90`.
:::
:::

:::step{type=try title="Divide two ways"}
```bash run
cat > /tmp/div.go <<'GO'
package main

import "fmt"

func main() {
	fmt.Println(45/50*100, float64(45)/float64(50)*100)
	fmt.Println(7/2, 7%2, 7.0/2)
}
GO
go run /tmp/div.go
```
:::

:::step{type=task task=percent title="A percentage"}
In `numbers/numbers.go`, make `Percent(scored, total int) float64` return the percentage, **rounded
to one decimal**, and `0` when `total` is `0`.

- `Percent(45, 50)` returns `90`
- `Percent(1, 3)` returns `33.3`
- `Percent(2, 3)` returns `66.7`
- `Percent(7, 0)` returns `0`

`math.Round(x*10) / 10` rounds to one decimal.
:::

:::step{type=concept title="Building text with fmt.Sprintf"}
`fmt.Sprintf` builds a string from a pattern and values:

```go
fmt.Sprintf("%s scored %d", "Riya", 92)     // "Riya scored 92"
fmt.Sprintf("%.1f%%", 33.333)               // "33.3%"
fmt.Sprintf("%02d", 5)                      // "05": two digits, padded with 0
```

`%d` is an int, `%s` a string, `%f` a float (`%.2f` two decimals) and `%v` anything.
:::

:::step{type=task task=format_rupees title="Paise as a price"}
In `numbers/numbers.go`, make `FormatRupees(paise int) string` show the amount in rupees with two
digits of paise.

- `FormatRupees(1250)` returns `"₹12.50"`
- `FormatRupees(5)` returns `"₹0.05"`
- `FormatRupees(0)` returns `"₹0.00"`
- `FormatRupees(120000)` returns `"₹1200.00"`
:::

:::step{type=deep-dive title="Sizes, overflow and runes"}
`int` is 64 bits on today's machines, but Go also has `int8` to `int64`, `uint` types and `float32`.
Fixed sizes **overflow** quietly: an `int8` holding 127 plus 1 becomes -128. Real money code keeps
amounts in an `int64` of paise, as here, and never in floats.

A Go `string` is a sequence of **bytes** holding UTF-8 text. `len("₹")` is 3, because the rupee sign
takes 3 bytes. A single character is a `rune` (a Unicode code point); `for _, r := range s` walks a
string rune by rune, which chapter 4 uses.
:::

:::step{type=recap}
- `int`, `float64`, `string` and `bool` are the everyday types; Go never mixes them silently.
- `int / int` throws the fraction away: convert with `float64(x)` first.
- `math.Round(x*10) / 10` rounds to one decimal.
- `fmt.Sprintf` builds text: `%d`, `%s`, `%.2f`, `%02d`.
:::
