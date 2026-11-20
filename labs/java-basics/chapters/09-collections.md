:::step{type=story title="Why collections"}
Arrays have a fixed size, but real data grows: a shopping cart gets more items, a class gets new
students. Java's **collections** are containers that grow and shrink as you need, and the two you will
use most are `ArrayList` and `HashMap`.

:::mission
In `collections/`, return the n biggest numbers without disturbing the caller's list, and count how many
times each word appears.
:::
:::

:::step{type=concept title="ArrayList: an array that grows"}
Picture a notebook where you can always add another line, compared with a form that has exactly five
boxes. An `ArrayList` is the notebook:

```java
List<Integer> marks = new ArrayList<>();
marks.add(72);          // [72]
marks.add(45);          // [72, 45]
marks.get(0)            // 72
marks.size()            // 2
marks.remove(0);        // [45]
```

`List<Integer>` means "a list of whole numbers". The `<Integer>` part tells Java what the list may hold,
so it can stop you adding text by mistake.

:::picture{name="notebook-vs-form" code='marks.add(45)'}
An array is a form with a fixed number of boxes; an ArrayList is a notebook with room for one more line.
:::
:::

:::step{type=concept title="HashMap: look things up by name"}
A list answers "what is item number 3?". Often you need "what is Riya's phone number?". A `HashMap` is
like a **phone book**: you look up a **key** to find its **value**.

```java
Map<String, String> phones = new HashMap<>();
phones.put("Riya", "98201 11111");     // key "Riya", value her number
phones.get("Riya")                     // "98201 11111"
phones.getOrDefault("Kabir", "none")   // "none": Kabir is not there
phones.containsKey("Riya")             // true
```

`getOrDefault` is the safe lookup: it gives your default instead of `null` when the key is missing.

:::picture{name="phone-book" code='phones.get("Riya")'}
Look up a key ("Riya") to find its value, without reading the whole book.
:::
:::

:::step{type=example title="Worked example: total stock per item"}
Adding up per key is the most common map pattern:

```java
public static Map<String, Integer> totals(List<String> items, List<Integer> qty) {
    Map<String, Integer> out = new HashMap<>();
    for (int i = 0; i < items.size(); i++) {
        String item = items.get(i);
        out.put(item, out.getOrDefault(item, 0) + qty.get(i));
    }
    return out;
}
```

`out.getOrDefault(item, 0)` is the total so far (0 the first time). Add the new amount and store it
back. Counting words is the same, adding 1 each time.

:::trace{title="totals([tea, milk, tea], [2, 1, 3])"}
| i | item | qty | out | note |
|---|---|---|---|---|
|  |  |  | {} | The map starts empty. |
| 0 | tea | 2 | {tea=2} | tea is not in the map yet: 0 + 2 = 2. |
| 1 | milk | 1 | {tea=2, milk=1} | milk is new too: 0 + 1 = 1. |
| 2 | tea | 3 | {tea=5, milk=1} | tea is already 2: 2 + 3 = 5, stored back under the same key. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does the last line print?

```java
List<Integer> a = new ArrayList<>(List.of(3, 1, 2));
List<Integer> b = a;
Collections.sort(b);
System.out.println(a);
```
:::
- [ ] `[3, 1, 2]`
- [x] `[1, 2, 3]`
- [ ] `[]`
- [ ] It does not compile
:::explain
`b = a` gives the same list a second name (two envelopes, one address). Sorting through `b` sorts the one
list `a` also sees. To work on a separate copy, make one: `new ArrayList<>(a)`.
:::
:::

:::step{type=try title="Copy before you sort"}
```bash run
cat > /tmp/Copy.java <<'JAVA'
import java.util.*;

public class Copy {
    public static void main(String[] args) {
        List<Integer> marks = new ArrayList<>(List.of(72, 45, 90));
        List<Integer> copy = new ArrayList<>(marks);
        copy.sort(Comparator.reverseOrder());
        System.out.println("copy " + copy + ", original " + marks);
    }
}
JAVA
java /tmp/Copy.java
```
:::

:::step{type=task task=top_n title="Warm-up: the n biggest numbers"}
In `collections/ListTools.java`, make `topN(numbers, n)` return the n biggest numbers, **biggest first**,
without changing the list it was given.

- `topN([72, 45, 90, 66], 2)` returns `[90, 72]`
- `topN([5, 1], 5)` returns `[5, 1]` (asking for more than there are is fine)
- after the call, the caller's list is still `[72, 45, 90, 66]`

`subList(0, k)` keeps the first k items; `Math.min(n, size)` stops it going past the end.
:::

:::step{type=task task=word_counts title="Count each word"}
In `collections/WordCounter.java`, make `count(words)` return how many times each word appears, with
words lower-cased so `Tea` and `tea` count together.

- `count([tea, Coffee, TEA, tea])` returns `{tea=3, coffee=1}`
- `count([])` returns an empty map
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `map.get("milk")` give for a `HashMap` without the key `"milk"`?
:::
- [ ] `0`
- [x] `null`
- [ ] An exception
- [ ] `""`
:::explain
`get` returns `null` for a missing key, which can crash later if you do arithmetic with it. That is why
`getOrDefault(key, 0)` is the safer choice for counting.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which makes a separate copy of `list`?
:::
- [ ] `List<Integer> c = list;`
- [x] `List<Integer> c = new ArrayList<>(list);`
- [ ] `List<Integer> c = list.get(0);`
- [ ] `List<Integer> c = List.of();`
:::explain
`new ArrayList<>(list)` builds a new list with the same items. Plain assignment only shares the list.
:::
:::

:::step{type=deep-dive title="The Collections Framework"}
`ArrayList` and `HashMap` are the stars of the **Java Collections Framework**. Its other members fit
other needs: `HashSet` keeps each item once, `TreeMap` keeps keys sorted, `LinkedList` and `ArrayDeque`
suit queues. Code is usually written against the **interfaces** (`List`, `Map`, `Set`) so the class
behind them can change without touching the rest.

Collections hold objects, not primitives, so `List<int>` is not allowed: Java wraps each `int` in an
`Integer` object automatically (**autoboxing**). `List.of(...)` and `Map.of(...)` make lists and maps that
cannot be changed, handy for constants and tests.
:::

:::step{type=recap}
- `ArrayList` grows as you add: `add`, `get`, `size`, `remove`.
- `HashMap` looks values up by key: `put`, `get`, `getOrDefault`, `containsKey`.
- Assignment shares a collection; `new ArrayList<>(list)` copies it.
- Count with `map.put(k, map.getOrDefault(k, 0) + 1)`.
:::
