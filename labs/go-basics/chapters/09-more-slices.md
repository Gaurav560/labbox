:::step{type=story title="Can changing one slice change another?"}
Take Parcel's van: four parcels. Make a second slice of just the first two, and change its first parcel. Which slices
changed? Only the second one, surely: it is a different variable.

Run it, and the **van** changed too. Then append a parcel to the small slice, and the van changes again, in a place
you never touched. This is the most surprising thing about Go slices, and the one most likely to cause a real bug. By
the end of this chapter you will know exactly why it happens, and the one function that makes it safe.

:::mission
Write `TopN`, which picks the n biggest numbers without disturbing the caller's slice, and `Unique`, which keeps each
item once.
:::
:::

:::step{type=try title="Two slices, one secret" file="09-more-slices/shared.go" line="9-20"}
Open `shared.go`:

```go
van := []int{4, 12, 7, 9}
front := van[:2]
front[0] = 99
fmt.Println(van, front)

front = append(front, 50)
fmt.Println(van, front)
```

```bash run
cd /workspace/09-more-slices && go run shared.go
```

```text
[99 12 7 9] [99 12]
[99 12 50 9] [99 12 50]
99 1 3 4
```

Line one: changing `front[0]` changed `van[0]`. Line two: appending 50 to `front` **overwrote** the 7 in `van`.
:::

:::step{type=concept title="A slice is a window onto an array"}
A slice does not hold its numbers. It is a small **window** onto an array that lives somewhere else, with three
parts: where the window starts, its **length** (how many items you can see) and its **capacity** (how far the
array behind it goes).

`front := van[:2]` made a new window onto the **same** array: length 2, capacity 4. So `front[0] = 99` wrote into the
shared array, and `van` saw it.

Then `append(front, 50)`: the window had room behind it (capacity 4), so `append` simply wrote 50 into the next slot of
the shared array, which was `van[2]`. Only when there is no room left does `append` make a fresh, bigger array.

To get a truly separate slice, copy it: `make` a new slice and `copy` into it, or use `slices.Clone(van)`. That is the
last line of the output: changing `safe` left `van` alone.

:::picture{name="envelope-address"}
Two envelopes with the same address lead to the same house.
:::
:::

:::step{type=try title="Sort a copy, not the original" file="09-more-slices/sorting.go" line="12-17"}
The `slices` package (Go 1.21 and later) has the everyday tools:

```bash run
cd /workspace/09-more-slices && go run sorting.go
```

```text
[12 4 9] [4 9 12]
[12 9 4] true 2
```

`slices.Clone` made a copy, `slices.Sort` sorted the copy in place, and the original `weights` kept its order.
`slices.Reverse`, `slices.Contains` and `slices.Index` do what their names say.
:::

:::step{type=example title="Worked example: the n smallest, without damage"}
```go
func BottomN(numbers []int, n int) []int {
	sorted := slices.Clone(numbers)
	slices.Sort(sorted)
	if n > len(sorted) {
		n = len(sorted)
	}
	return sorted[:n]
}
```

1. Clone first: `slices.Sort` sorts in place, and `numbers` belongs to the caller.
2. Sort the copy, smallest first.
3. Never ask for more than there is: `sorted[:5]` on 2 items would panic.
:::

:::step{type=predict title="Guess first"}
:::question
`a := []int{1, 2, 3}; b := a; b[0] = 9`. What is `a[0]`?
:::
- [x] `9`
- [ ] `1`
:::explain
`b := a` copies the window, not the numbers. Both look at the same array.
:::
:::

:::step{type=task task=top_n title="Your turn: the n biggest numbers"}
Open `slicetools.go` and make `TopN(numbers, n)` return the n biggest numbers, biggest first, **without changing the
slice it was given**.

`TopN([]int{72, 45, 90, 66}, 2)` gives `[90 72]`, `TopN([]int{5, 1}, 5)` gives `[5 1]`, and `n = 0` gives an empty slice.
After the call, the caller's slice is still `[72 45 90 66]`.

```bash run
cd /workspace/09-more-slices && go run run.go
```

Then press **Check**.
:::

:::step{type=concept title="Sets with a map"}
Go has no set type; a `map[string]bool` does the job (chapter 10 is all about maps):

```go
seen := map[string]bool{}
seen["Pune"] = true
if seen["Goa"] {        // a missing key reads as false
	fmt.Println("been to Goa")
}
```

`[]string{}` is an empty slice; a plain `var s []string` is `nil`, which also has length 0.

:::picture{name="guest-list"}
A set keeps each item once, like a guest list.
:::
:::

:::step{type=task task=unique title="Your turn: each item once"}
In `slicetools.go`, make `Unique(items)` return each item once, in the order it first appeared.

`Unique([]string{"Pune", "Goa", "Pune"})` gives `[Pune Goa]`.

```bash run
cd /workspace/09-more-slices && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
When does `append` change the array a slice shares with another slice?
:::
- [ ] Never
- [x] When there is room (capacity) behind the slice
- [ ] Always
:::explain
With room left, `append` writes into the shared array. Without room, it moves everything to a new array.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which line makes a truly separate copy of `van`?
:::
- [ ] `c := van`
- [ ] `c := van[:]`
- [x] `c := slices.Clone(van)`
:::explain
The first two only make new windows onto the same array.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What happens with `s[:5]` when `s` has 2 items and capacity 2?
:::
- [ ] It gives the 2 items
- [x] It panics: slice bounds out of range
:::explain
A slice can only grow up to its capacity. Check the length first.
:::
:::

:::step{type=deep-dive title="Go deeper: full slice expressions, and slices of structs"}
**Full slice expressions.** `van[:2:2]` limits the capacity to 2, so a later `append` must make a new array and can
never overwrite `van`. Libraries use it to hand out safe windows.

**Sorting by a rule.** `slices.SortFunc(parcels, func(a, b Parcel) int { return a.Weight - b.Weight })` sorts structs
by any field (chapter 10 has structs).

**Growth.** When `append` needs room it roughly doubles the capacity, so appending one at a time stays fast.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Explain a slice as a window onto an array, with a length and a capacity.
- Predict when two slices share their numbers, and when `append` overwrites a neighbour.
- Copy with `slices.Clone` before changing something the caller owns.
- Use `slices.Sort`, `Reverse`, `Contains` and `Index`, and a `map[string]bool` as a set.

:::photo{src="/lesson-images/go/go-09-notes.webp" alt="Handwritten notes about Go slices: a slice is a window onto an array, length and capacity, two slices can share numbers, append may overwrite, slices.Clone to copy, sort a copy" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 10: maps and structs, and why a map never gives you its keys in the same order twice.
:::
