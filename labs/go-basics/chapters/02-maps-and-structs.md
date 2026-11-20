:::step{type=story title="Why maps and structs"}
Real data has shape: an order has an item and a quantity, a student has a name and marks. Go groups
such fields in a **struct**, and looks things up by key in a **map**, the tool for counting and
grouping.

:::mission
In `till.go`, count how many of each item were ordered, and pick the best seller fairly.
:::
:::

:::step{type=concept title="Structs and maps"}
A **struct** groups fields: `Order{Item: "coffee", Qty: 2}`. A **map** finds a value by key:

```go
counts := make(map[string]int)
counts["coffee"] += 2
counts["coffee"]      // 2
counts["poha"]      // 0: a missing key reads as the zero value
```

Use `make` before writing: writing to a nil map panics.
:::

:::step{type=predict title="Guess first"}
:::question
You loop over the same map twice with `range`. Do you get the keys in the same order?
:::
- [ ] Yes, insertion order
- [ ] Yes, sorted order
- [x] Not necessarily: Go randomises map order
:::explain
Go deliberately randomises map iteration, so code that depends on the order breaks early instead of
in production. When order matters (like ties), add an explicit rule.
:::
:::

:::step{type=try title="See it random"}
Print the same map a few times:

```bash run
cat > /tmp/m.go <<'G'
package main
import "fmt"
func main() { m := map[string]int{"a": 1, "b": 2, "c": 3, "d": 4}; for i := 0; i < 3; i++ { for k := range m { fmt.Print(k) }; fmt.Println() } }
G
go run /tmp/m.go
```
:::

:::step{type=task task=count_by_item title="Count per item"}
Make `CountByItem(orders)` return a map from each item to its total quantity.
No orders give an empty map, not `nil`.
:::

:::step{type=task task=busiest title="The best seller"}
Make `Busiest(orders)` return the item with the biggest total quantity. On a tie, the name that sorts
first wins. No orders give `""`.
:::

:::step{type=deep-dive title="Why Go shuffles map order on purpose"}
A Go map is a hash table. Its iteration order depends on how keys land in its buckets, which changes
as the map grows. Early Go programs came to rely on whatever order they happened to see, then broke
when the implementation changed. So Go **randomises** the starting point of every `range` over a map:
code that depends on map order fails right away in testing instead of months later.

When you need an order, collect the keys in a slice and sort it (`slices.Sort(keys)`), or, as in
`Busiest`, write an explicit rule for ties. Maps are not safe for writes from several goroutines at
once; chapter 13 shows how to share one safely.
:::

:::step{type=recap}
- Structs group fields; maps find values by key and read missing keys as zero.
- `make` a map before writing to it.
- Map order is random on purpose: write tie-breaking rules explicitly.
:::
