:::step{type=story title="How many kinds of loop does a language need?"}
Most languages give you a collection of loops: `for`, `while`, `do while`, `for each`, `repeat until`. Java has four.
JavaScript has five.

Go has **one**. It is called `for`, and it does every job the others do. That is Go all over: fewer features, each one
doing more, so every Go program reads the same way. Today Parcel goes through its whole van, parcel by parcel, with
that single loop in three different shapes.

:::mission
Write `SumTo`, which adds up 1 to n, and `CountVowels`, which counts the vowels in a street name.
:::
:::

:::step{type=try title="A van, stop by stop" file="05-loops/route.go" line="9-24"}
Open `route.go`. The same `for`, three ways:

```go
weights := []int{4, 12, 7}
total := 0
for i := 0; i < len(weights); i++ {
	total += weights[i]
	fmt.Printf("stop %d: %d kg so far\n", i+1, total)
}

for i, w := range weights {
	fmt.Println(i, w)
}

fuel := 10
for fuel > 0 {
	fuel -= 4
}
fmt.Println("fuel left:", fuel)
```

```bash run
cd /workspace/05-loops && go run route.go
```

```text
stop 1: 4 kg so far
stop 2: 16 kg so far
stop 3: 23 kg so far
0 4
1 12
2 7
fuel left: -2
```

`[]int{4, 12, 7}` is a **slice**: a list of whole numbers (chapter 7 is all about them). `total += weights[i]` is short
for `total = total + weights[i]`.
:::

:::step{type=concept title="Repeating with a counter"}
The first shape is the classic counting loop, with three parts separated by `;`:

```go
for i := 0; i < len(weights); i++ {
	// runs once for each i
}
```

1. `i := 0` runs once, at the start: positions begin at 0.
2. `i < len(weights)` is checked **before every lap**; when it is false, the loop ends.
3. `i++` (add 1 to `i`) runs **after every lap**.

So `i` is 0, 1, 2, and then 3 fails the check. Three laps for three parcels.

:::picture{name="running-track"}
The counter marks each lap until the runner reaches the finish line.
:::
:::

:::step{type=concept title="range, and the loop with only a condition"}
**range** hands you each item with its position:

```go
for i, w := range weights { ... }   // i is the position, w the weight
for _, w := range weights { ... }   // only the weight: _ throws the position away
```

Go's rule about unused variables applies here too: if you write `i` and never use it, Go refuses. `_` says "I do not
need it".

**A condition alone** is Go's `while`: `for fuel > 0 { ... }` repeats while it is true. And notice the last line of
the output: fuel went 10, 6, 2, then -2. The check happens **before** each lap, so the last lap ran with 2 litres and
went below zero. Loops end at the check, not in the middle.

And `for { ... }` with nothing at all loops forever, until a `break` or a `return` gets out.
:::

:::step{type=example title="Worked example: count the heavy parcels"}
```go
func CountHeavy(weights []int) int {
	count := 0
	for _, w := range weights {
		if w >= 10 {
			count++
		}
	}
	return count
}

CountHeavy([]int{4, 12, 7, 15})   // 2
```

:::trace{title="CountHeavy with 4, 12, 7, 15"}
| w | w >= 10? | count |
|---|---|---|
| 4 | no | 0 |
| 12 | yes | 1 |
| 7 | no | 1 |
| 15 | yes | 2 |
:::

1. Start the counter at 0, before the loop.
2. Inside the loop, decide (chapter 4) and add one when it fits.
3. Return the counter **after** the loop, once every item has been looked at.
:::

:::step{type=predict title="Guess first"}
:::question
`total := 0; for i := 1; i <= 3; i++ { total += i }`. What is `total` after the loop?
:::
- [ ] `3`
- [x] `6`
- [ ] `10`
:::explain
`i` is 1, 2 and 3 (`<=` includes 3), so the total is 1 + 2 + 3 = 6.
:::
:::

:::step{type=task task=sum_to title="Your turn: add up 1 to n"}
Open `loops.go` and make `SumTo(n)` give back 1 + 2 + ... + n. When `n` is 0 or less, give back `0`.

`SumTo(5)` gives `15`, `SumTo(100)` gives `5050`, and `SumTo(0)` gives `0`.

```bash run
cd /workspace/05-loops && go run run.go
```

Then press **Check**.
:::

:::step{type=concept title="Looking at text one character at a time"}
`range` over a string gives each character, as a **rune** (chapter 3's deep dive):

```go
for _, r := range "Pune" {
	fmt.Println(string(r))   // P, then u, then n, then e
}
```

`strings.ToLower("PUNE")` makes a whole string small first (`import "strings"`), and
`strings.ContainsRune("aeiou", r)` asks whether one character is a vowel.
:::

:::step{type=task task=count_vowels title="Your turn: count the vowels"}
In `loops.go`, make `CountVowels(text)` count the vowels (a, e, i, o, u) in either case.

`CountVowels("Hello World")` gives `3`, `CountVowels("AEIOU")` gives `5`, and `CountVowels("rhythm")` gives `0`.

```bash run
cd /workspace/05-loops && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
How do you write a `while` loop in Go?
:::
- [ ] `while fuel > 0 { }`
- [x] `for fuel > 0 { }`
- [ ] Go cannot do it
:::explain
`for` with only a condition is Go's `while`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`for i, w := range weights { fmt.Println(w) }`. What does Go say?
:::
- [ ] It prints every weight
- [x] A compile error: `i` is declared and not used
:::explain
Write `for _, w := range weights` when you do not need the position.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Where should `total := 0` go, to add up a list?
:::
- [x] Before the loop
- [ ] Inside the loop
:::explain
Inside the loop it would be reset on every lap, and only the last item would count.
:::
:::

:::step{type=deep-dive title="Go deeper: break, continue, labels and range over a number"}
**break and continue.** `break` leaves the loop at once; `continue` skips to the next lap.

**Labels.** `outer: for ... { for ... { break outer } }` breaks out of two loops at once.

**range over a number.** Since Go 1.22, `for i := range 3` counts 0, 1, 2: the shortest counting loop in any
language.

**Stuck?** Press **Ctrl + C** in the terminal to stop a loop that never ends.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Count with `for i := 0; i < n; i++`, and know the check runs before every lap.
- Walk through every item with `for _, w := range items`, using `_` for what you do not need.
- Repeat while a condition holds with `for condition { }`.
- Keep a running total or a count: start before the loop, add inside, return after.

:::photo{src="/lesson-images/go/go-05-notes.webp" alt="Handwritten notes about Go loops: one loop called for, for i colon equals 0, for range gives position and item, underscore when you do not need one, for with a condition is while, total before the loop" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 6: finding bugs, and how to read a Go panic.
:::
