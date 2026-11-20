:::step{type=story title="Why more about slices"}
Chapter 5 summed a slice. Real code also sorts, filters, copies and removes duplicates, and Go slices
have one surprise that bites almost everyone once: two slices can share the same memory.

:::mission
In `slicetools/slicetools.go`, return the n biggest numbers without disturbing the caller's slice,
and remove duplicates while keeping the order.
:::
:::

:::step{type=concept title="append, slicing and sorting"}
```go
nums := []int{72, 45, 90}
nums = append(nums, 66)      // [72 45 90 66]: append returns the slice
first := nums[:2]            // [72 45]
slices.Sort(nums)            // [45 66 72 90], sorts in place
slices.Reverse(nums)         // [90 72 66 45]
slices.Contains(nums, 66)    // true
```

The `slices` package (Go 1.21+) holds the everyday helpers.
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```go
a := []int{3, 1, 2}
b := a
slices.Sort(b)
fmt.Println(a)
```
:::
- [ ] `[3 1 2]`
- [x] `[1 2 3]`
- [ ] `[]`
- [ ] It does not compile
:::explain
A slice is a small view onto an array. `b := a` copies the **view**, not the numbers, so `a` and `b`
share one array and sorting `b` sorts what `a` sees too. `slices.Clone(a)` makes a real copy.
:::
:::

:::step{type=try title="Shared memory, then a copy"}
```bash run
cat > /tmp/sl.go <<'GO'
package main

import (
	"fmt"
	"slices"
)

func main() {
	a := []int{3, 1, 2}
	b := a
	c := slices.Clone(a)
	slices.Sort(b)
	fmt.Println(a, b, c)
}
GO
go run /tmp/sl.go
```
:::

:::step{type=task task=top_n title="The n biggest numbers"}
In `slicetools/slicetools.go`, make `TopN(numbers []int, n int) []int` return the n biggest numbers,
biggest first, **without changing the slice it was given**.

- `TopN([]int{72, 45, 90, 66}, 2)` returns `[90 72]`
- `TopN([]int{5, 1}, 5)` returns `[5 1]`
- `TopN([]int{3, 1, 2}, 0)` returns an empty slice
- after the call, the caller's slice is still `[72 45 90 66]`
:::

:::step{type=concept title="Sets with a map"}
Go has no set type; a `map[string]bool` does the job:

```go
seen := map[string]bool{}
seen["tea"] = true
if seen["coffee"] {        // a missing key reads as false
	fmt.Println("had coffee")
}
```

`make([]string, 0)` or `[]string{}` is an empty slice; a plain `var s []string` is `nil`, which also
has length 0 but prints as `[]` and encodes to JSON as `null`.
:::

:::step{type=task task=unique title="Each item once"}
In `slicetools/slicetools.go`, make `Unique(items []string) []string` return each item once, in the
order it **first** appeared, and an empty (not nil) slice for no items.

- `Unique([]string{"tea", "coffee", "tea", "milk"})` returns `[tea coffee milk]`
- `Unique(nil)` returns `[]`
:::

:::step{type=deep-dive title="Length, capacity and append"}
A slice has a **length** (items in use) and a **capacity** (room in the array behind it). `append`
writes into spare capacity when there is some, so two slices made from the same array can overwrite
each other's items. When capacity runs out, `append` allocates a bigger array (roughly double) and
copies: that is why you must always use its return value, `s = append(s, x)`.

If you know the final size, `make([]int, 0, n)` reserves the room once. And `copy(dst, src)` copies
items between slices that do not share memory.
:::

:::step{type=recap}
- `append` returns the slice: always assign it back.
- Slices share memory: `b := a` is not a copy; `slices.Clone` is.
- `slices.Sort`, `slices.Reverse`, `slices.Contains` cover everyday needs.
- `map[string]bool` works as a set; prefer an empty slice over `nil` for "no items".
:::
