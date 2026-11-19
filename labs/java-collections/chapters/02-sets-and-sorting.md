:::step{type=story title="Who to pay first"}
:::character{name="Kabir" role="Lead engineer, PaySetu"}
The bank only lets us send a few big transfers in the first minute after midnight.
I need the list of every merchant once, and the biggest earners first.
:::

:::mission
List each merchant once, A to Z, and rank the biggest earners.
:::
:::

:::step{type=concept title="Sets and sorted sets"}
A **Set** holds each value once. A `TreeSet` also keeps its values sorted:

```java
Set<String> names = new TreeSet<>();
names.add("Kirana King");
names.add("Brew Point");
names.add("Kirana King");
// [Brew Point, Kirana King]
```

`new ArrayList<>(names)` turns any set into a list, in the set's order.
:::

:::step{type=predict title="Guess first"}
:::question
What does a `HashSet` of `"b"`, `"a"`, `"c"` print as?
:::
- [ ] Always `[a, b, c]`
- [ ] Always `[b, a, c]`
- [x] Some order you should not rely on
:::explain
A `HashSet` has no defined order. It may look sorted on a small example and then not be on
real data. Use a `TreeSet` or sort explicitly when order matters.
:::
:::

:::step{type=try title="Sort with a Comparator"}
`jshell` lets you try Java line by line. Paste this, then type `/exit`:

```bash run
printf 'var l = new java.util.ArrayList<>(java.util.List.of("b", "a", "c"));\nl.sort(java.util.Comparator.reverseOrder());\nSystem.out.println(l);\n/exit\n' | jshell -q
```
:::

:::step{type=task task=unique_merchants title="Each shop once"}
Make `uniqueMerchants(payments)` return every merchant name once, A to Z.
:::

:::step{type=task task=top_merchants title="The biggest shops"}
Make `topMerchants(payments, n)` return the `n` merchants with the biggest totals, biggest first.
Two merchants with the same total go A to Z.

:::tip
You already wrote `totalsByMerchant`. Reuse it.
:::
:::

:::step{type=recap}
- A `Set` keeps one of each; a `TreeSet` keeps them sorted too.
- Never rely on the order of a `HashSet` or `HashMap`.
- A `Comparator` can sort by one thing, reversed, then break ties with another.
:::
