:::step{type=story title="The morning route"}
:::character{name="Priya" role="Founder, Dabba Express"}
Our riders leave at 11. They need two lists: every area we deliver to today, once,
and the order to ride them in, nearest first. Right now they guess.
:::

:::mission
List every delivery area once, and sort a route from nearest to farthest.
:::
:::

:::step{type=concept title="Sets keep one of each"}
A **set** holds each value at most once, and has no order:

```python
areas = {"Baner", "Aundh", "Baner"}
len(areas)   # 2
```

Adding a value that is already there does nothing. That makes a set the quickest way to
remove duplicates. When you need order back, sort it: `sorted(areas)` gives a list.
:::

:::step{type=predict title="Guess first"}
:::question
What does `sorted([("Baner", 7.5), ("Aundh", 3.0)])` sort by?
:::
- [ ] The distances, because they are numbers
- [x] The area names first, then the distances
- [ ] Nothing: tuples cannot be sorted
:::explain
Tuples are compared item by item, from the left. The first item is the name, so this sorts A to Z.
To sort by distance you need `key=`.
:::
:::

:::step{type=try title="Sets in the shell"}
Try a set and a sort in the Python REPL:

```bash run
python3 -c "print(sorted({'Baner', 'Aundh', 'Baner', 'Kothrud'}))"
```
:::

:::step{type=task task=unique_areas title="Every area once"}
Make `unique_areas(orders)` return every delivery area once, sorted A to Z.
Each order is a dict like `{"dish": "veg thali", "area": "Kothrud"}`.
:::

:::step{type=task task=route_order title="Nearest first"}
Make `route_order(stops)` return the area names from nearest to farthest.
Each stop is a tuple like `("Baner", 7.5)`. Two areas at the same distance go A to Z.

`route_order([("Baner", 7.5), ("Aundh", 3.0)])` is `["Aundh", "Baner"]`.

:::mistake
`stops.sort()` sorts the list in place and returns `None`. `sorted(stops)` returns a new list.
:::
:::

:::step{type=recap}
- A set keeps each value once: the fastest way to drop duplicates.
- Tuples sort item by item from the left.
- `key=` decides what to sort by; a tuple key gives a tie-breaker for free.
:::
