:::step{type=story title="The midnight settlement"}
:::character{name="Kabir" role="Lead engineer, PaySetu"}
Every night at 12 we pay each merchant what they earned that day. Last night a spreadsheet
formula broke and three coffee stalls got nothing. I want the settlement in plain, tested Java.
:::

:::mission
Add up a day of payments, and work out one total per merchant.
:::
:::

:::step{type=concept title="List and Map"}
A **List** keeps values in order. A **Map** stores a value under a key, so you can find it again:

```java
List<Payment> today = List.of(new Payment("Brew Point", 2000));
Map<String, Long> totals = new HashMap<>();
totals.put("Brew Point", 2000L);
totals.get("Brew Point");   // 2000
```

`Payment` is a **record**: a small class whose fields you read with methods like `p.merchant()`.
Amounts are in paise, so 2000 means 20 rupees.
:::

:::step{type=predict title="Guess first"}
:::question
`totals` is an empty `HashMap<String, Long>`. What does `totals.get("Kirana King")` return?
:::
- [ ] `0`
- [x] `null`
- [ ] It throws an exception
:::explain
A missing key gives `null`. Adding `+ 100` to that `null` would throw a `NullPointerException`,
which is why `getOrDefault` and `merge` exist.
:::
:::

:::step{type=try title="Run the examples"}
`Payments.java` has four methods that return placeholders. Compile and run:

```bash run
javac *.java && java Payments
```
:::

:::step{type=task task=total_paise title="Everything paid today"}
Make `totalPaise(payments)` return the sum of every payment's `amountPaise()`.
No payments add up to `0`.
:::

:::step{type=example title="merge: add or start"}
`merge` adds to the value under a key, or puts the value there if the key is new:

```java
Map<String, Long> m = new HashMap<>();
m.merge("Brew Point", 2000L, Long::sum);  // {Brew Point=2000}
m.merge("Brew Point", 3000L, Long::sum);  // {Brew Point=5000}
```

`Long::sum` is a method reference: "add the old and the new value".
:::

:::step{type=task task=totals_by_merchant title="One total per shop"}
Make `totalsByMerchant(payments)` return a map from each merchant's name to the total
they were paid today.

:::why
This map is exactly what the bank transfer job reads at midnight. A wrong total here is real money.
:::
:::

:::step{type=recap}
- A `List` keeps order; a `Map` finds a value by key.
- `get` on a missing key returns `null`, not 0.
- `merge(key, value, Long::sum)` adds to a total or starts a new one.
:::
