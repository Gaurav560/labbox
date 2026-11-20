:::step{type=story title="Why loops"}
Doing something once is easy. Doing it for every mark in a class or every word in a file means
repeating, and Go keeps that simple: it has exactly **one** loop keyword, `for`, used in a few shapes.

:::mission
In `loops/loops.go`, add up the numbers from 1 to n, and count the vowels in a piece of text.
:::
:::

:::step{type=concept title="The shapes of for"}
```go
for i := 0; i < 5; i++ {   // classic: start; condition; step
	fmt.Println(i)
}

n := 1
for n < 100 {              // like "while" in other languages
	n *= 2
}

for {                      // forever, until break or return
	break
}
```

`i++` adds one to `i`. `break` leaves the loop, `continue` skips to the next round.

:::picture{name="running-track"}
A loop runs the same steps again, lap after lap.
:::
:::

:::step{type=example title="Worked example: count the passing marks"}
The counting loop in Go:

```go
func CountPassed(marks []int) int {
	count := 0
	for _, m := range marks {
		if m >= 33 {
			count++
		}
	}
	return count
}
```

1. Start a counter at zero.
2. `range` gives each mark (the `_` ignores its position).
3. `count++` adds one when the mark passes.

`SumTo` is the classic three-part `for` instead, adding instead of counting.

:::trace{title="CountPassed([]int{45, 20, 90, 33})"}
| m | m >= 33? | count | note |
|---|---|---|---|
|  |  | 0 | Before the loop: count starts at zero. |
| 45 | yes | 1 | 45 passes, so count goes up by one. |
| 20 | no | 1 | 20 does not pass: count stays 1. |
| 90 | yes | 2 | 90 passes: count is 2. |
| 33 | yes | 3 | 33 is exactly 33, and >= includes it: count is 3. |
|  |  | 3 | No marks left: the answer is 3. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
How many times does this print?

```go
for i := 1; i <= 5; i += 2 {
	fmt.Println(i)
}
```
:::
- [ ] 5 times
- [x] 3 times (1, 3, 5)
- [ ] 2 times (1, 3)
- [ ] Forever
:::explain
`i` starts at 1 and grows by 2: 1, 3, 5, then 7, which fails `i <= 5`. Reading the three parts of a
`for` one at a time is the quickest way to see how many rounds it makes.
:::
:::

:::step{type=try title="range over text"}
```bash run
cat > /tmp/rng.go <<'GO'
package main

import "fmt"

func main() {
	for i, r := range "Go₹" {
		fmt.Println(i, string(r))
	}
}
GO
go run /tmp/rng.go
```

`range` over a string gives each character (a **rune**) and the byte position where it starts: `₹` is
three bytes, so positions go 0, 1, 2.
:::

:::step{type=task task=sum_to title="Add up 1 to n"}
In `loops/loops.go`, make `SumTo(n int) int` return `1 + 2 + ... + n`.

- `SumTo(5)` returns `15`
- `SumTo(100)` returns `5050`
- `SumTo(0)` and `SumTo(-3)` return `0`
:::

:::step{type=concept title="Runes and characters"}
A rune is a character's number in Unicode. Single quotes make a rune, double quotes a string:

```go
r := 'a'                       // a rune
unicode.ToLower('E')           // 'e'
unicode.IsLetter('7')          // false
```

A `switch` can list several values in one case: `case 'a', 'e', 'i', 'o', 'u':`.
:::

:::step{type=task task=count_vowels title="Count the vowels"}
In `loops/loops.go`, make `CountVowels(text string) int` count `a`, `e`, `i`, `o` and `u`, upper or
lower case.

- `CountVowels("Hello World")` returns `3`
- `CountVowels("AEIOU")` returns `5`
- `CountVowels("rhythm")` returns `0`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
How many times does `for i := 0; i < 3; i++ { }` run?
:::
- [ ] 2
- [x] 3
- [ ] 4
- [ ] Forever
:::explain
`i` is 0, 1 and 2, then `i < 3` is false: three rounds.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `for i, r := range "hi"` give as `r`?
:::
- [ ] Bytes
- [x] Runes (characters)
- [ ] Strings of length 1
- [ ] Nothing: strings cannot be ranged
:::explain
Ranging over a string gives each **rune**; `i` is the byte position where it starts.
:::
:::

:::step{type=deep-dive title="Loop variables and the 1.22 change"}
Until Go 1.22, a `for` loop had **one** variable shared by every round. Goroutines or closures that
captured it all saw its last value, a famous bug. Since Go 1.22, each round gets its own copy, so
`for i := range 3 { go func() { fmt.Println(i) }() }` prints 0, 1 and 2 as you would expect.

Go 1.22 also lets you `range` over an integer: `for i := range 5` counts 0 to 4. And since 1.23 you
can `range` over functions (iterators), which is how many new standard library helpers hand out
values one at a time.
:::

:::step{type=recap}
- `for` is Go's only loop: classic, condition-only, or forever.
- `range` over a string gives runes; over a slice, index and value.
- `break` leaves, `continue` skips a round.
- A loop that never runs leaves its starting value: plan for empty input.
:::
