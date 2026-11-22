:::step{type=story title="Why does a map change its order every time?"}
Put five cities into a Go map, then walk through it three times, printing the keys. You would expect the same order
three times. Go gives you this:

```text
round 1: Kochi Agra Pune Delhi Goa
round 2: Goa Kochi Agra Pune Delhi
round 3: Delhi Goa Kochi Agra Pune
```

Different every round, and different again every time you run it. That is not a bug: Go's designers **made it random
on purpose**. By the end of this chapter you will know why, and how the counter at Parcel's depot finds its best
seller fairly, every single time.

Maps come with their partner: the **struct**, Go's way of bundling the fields of one thing, like a parcel's ID, weight
and city.


Some machines are built to be unpredictable on purpose. A lottery machine mixes the balls so nobody can guess the
order they come out. Go's maps do the same with their keys, for a very practical reason you will meet below.

:::photo{src="/lesson-images/go/lottery.webp" alt="A lottery ball machine: a clear drum with a mixing paddle, below a rack of coloured numbered balls" credit="Graphoscanada" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:TheBiLLeLottoBallMachine2012.jpg"}
A lottery ball machine: the order is random by design.
:::
:::mission
Write `CountByItem`, which adds up the quantity of each item sold, and `Busiest`, which finds the best seller with a
fair tie rule.
:::
:::

:::step{type=concept title="A map: look things up by key"}
A **map** stores values by key:

```go
waiting := map[string]int{"Pune": 3, "Delhi": 7}
waiting["Pune"]++          // 4
waiting["Goa"]             // 0: a missing key gives the zero value
n, ok := waiting["Goa"]    // 0 false: ok says whether it was really there
delete(waiting, "Delhi")
```

`map[string]int` reads "a map from strings to ints". Reading a missing key never panics: it gives the zero value, so
counting with `counts[key]++` just works, even the first time.

:::picture{name="phone-book"}
Look a value up by its name, like a number in a phone book.
:::
:::

:::step{type=try title="A parcel as a struct, and a map of depots" file="10-maps-and-structs/depots.go" line="8-27"}
Open `depots.go`:

```go
type Parcel struct {
	ID     string
	Weight int
	City   string
}
```

A **struct** groups named fields into one type. Run the file:

```bash run
cd /workspace/10-maps-and-structs && go run depots.go
```

```text
{P-101 4 Pune}
{ID:P-101 Weight:4 City:Pune}
5
4 0
0 false
2
```

`fmt.Println` shows a struct's values; `%+v` (chapter 6) adds the field names. `p.Weight = 5` changes one field. And
the map lines: Pune went from 3 to 4, Goa is missing so it reads as 0, and the `ok` form says `false`, really missing.
:::

:::step{type=try title="The random order" file="10-maps-and-structs/order.go" line="9-16"}
Now the puzzle. Open `order.go` and run it a few times:

```bash run
cd /workspace/10-maps-and-structs && go run order.go
```

Your order will differ from the one above, and from your own last run. Go deliberately starts each walk through a
map at a random place. Early Go programmers kept writing code that accidentally depended on the order, which then
broke when the map grew or when Go's map design improved. Randomising it means such bugs show up on day one, not in
production a year later.

The lesson for your code: **never rely on map order**. When you need an order (a sorted report, a fair tie rule), make
it yourself: collect the keys into a slice and sort it, or compare explicitly.
:::

:::step{type=example title="Worked example: the heaviest city"}
```go
func HeaviestCity(parcels []Parcel) string {
	totals := map[string]int{}
	for _, p := range parcels {
		totals[p.City] += p.Weight
	}
	best, bestKg := "", 0
	for city, kg := range totals {
		if kg > bestKg || (kg == bestKg && city < best) {
			best, bestKg = city, kg
		}
	}
	return best
}
```

1. Count into a map: `totals[p.City] += p.Weight`, starting from the zero value.
2. Walk the map, keeping the best so far.
3. The tie rule `city < best` (the name that sorts first) makes the answer the same **whatever order** the map hands
   out the keys. Without it, a tie could give a different winner on every run.
:::

:::step{type=task task=count_by_item title="Your turn: count per item"}
Open `orders.go` (the depot counter's sales) and make `CountByItem(orders)` return a map from each item to its total
quantity. No orders give an empty map, not `nil`.

```bash run
cd /workspace/10-maps-and-structs && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
Two items both sold 3. Without a tie rule, which one does a loop over the map pick?
:::
- [ ] Always the first one added
- [x] Either, and it can change from run to run
:::explain
Map order is random, so whichever comes first in this walk wins. A tie rule makes it fair and repeatable.
:::
:::

:::step{type=task task=busiest title="Your turn: the best seller"}
In `orders.go`, make `Busiest(orders)` return the item with the biggest total quantity. On a tie, the name that sorts
first wins. No orders give `""`.

The check calls it 20 times per case, so a tie rule that depends on map order will be caught.

```bash run
cd /workspace/10-maps-and-structs && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `counts["nobody"]` give for a `map[string]int` without that key?
:::
- [ ] A panic
- [x] `0`
- [ ] `nil`
:::explain
A missing key gives the value type's zero value. Use `v, ok := m[k]` to tell "missing" from "really 0".
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
How do you print a struct with its field names?
:::
- [ ] `fmt.Println(p)`
- [x] `fmt.Printf("%+v\n", p)`
:::explain
`%+v` adds the names: `{ID:P-101 Weight:4 City:Pune}`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why is map order random in Go?
:::
- [ ] Because maps are slow
- [x] So code that wrongly depends on the order breaks early, where you can see it
:::explain
The randomness is deliberate: order is not part of what a map promises.
:::
:::

:::step{type=deep-dive title="Go deeper: sorted keys, struct literals and maps of structs"}
**Sorted keys.** `keys := slices.Sorted(maps.Keys(totals))` gives the keys in order, for reports that must be stable.

**Struct literals.** `Parcel{ID: "P-1", Weight: 4}` names its fields, so adding a field later breaks nothing; missing
fields get zero values.

**Maps of structs.** `byID := map[string]Parcel{}` looks parcels up by ID. To change one, take it out, change it and
put it back (or store pointers, chapter 11).
:::

:::step{type=recap title="What you can do now"}
You can now:

- Make maps, read missing keys safely, and tell "missing" from zero with `v, ok :=`.
- Count with `counts[key] += n`, starting from the zero value.
- Define structs, read and change fields, and print them with `%+v`.
- Explain why map order is random, and write tie rules that make answers stable.

:::photo{src="/lesson-images/go/go-10-notes.webp" alt="Handwritten notes about Go maps and structs: a map looks things up by key, a missing key gives the zero value, v comma ok, counts of key plus equals n, map order is random on purpose, a tie rule makes it fair, struct groups fields" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 11: pointers, and why a function cannot make your parcel heavier.
:::
