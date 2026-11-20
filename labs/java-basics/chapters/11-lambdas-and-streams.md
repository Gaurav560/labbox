:::step{type=story title="Why lambdas and streams"}
"Give me the passing marks." "Sort these words by length." Written with loops, each takes several lines
of bookkeeping. Since Java 8 you can often say exactly what you want in one readable line, with
**lambdas** and **streams**. They are everywhere in modern Java code.

:::mission
In `streams/Streams.java`, keep only the passing marks, and sort words by length.
:::
:::

:::step{type=concept title="A lambda is a small unnamed method"}
Sometimes a method needs to be told **how** to do part of its job: which items to keep, how to compare
two things. A **lambda** is a tiny method you write right where it is needed, with no name:

```java
m -> m >= 40
```

Read it as "given `m`, answer whether `m` is at least 40". Left of the arrow are the inputs, right of it
the result. `(a, b) -> a.length() - b.length()` takes two inputs.
:::

:::step{type=concept title="A stream is a conveyor belt"}
Picture a factory **conveyor belt**: items ride along, and stations on the way filter some out,
change others, and at the end a box collects what is left.

A **stream** is that belt for a collection:

```java
List<Integer> passed = marks.stream()      // put the items on the belt
        .filter(m -> m >= 40)              // a station that keeps some
        .toList();                         // the box at the end
```

The original `marks` list is never changed: the stream builds a **new** list at the end.
:::

:::step{type=concept title="map and sorted: two more stations"}
```java
names.stream()
     .map(n -> n.toUpperCase())    // change each item
     .sorted()                     // put them in order
     .toList();
```

- `map` changes each item into something new (here, upper-case text).
- `sorted()` sorts in natural order (numbers small to large, text alphabetically).
- `sorted(comparator)` sorts by your own rule.

`String::toUpperCase` is a shorter way to write `n -> n.toUpperCase()`, called a **method reference**.
:::

:::step{type=example title="Worked example: the long names, in capitals"}
A whole pipeline, one station per line:

```java
public static List<String> longNames(List<String> names) {
    return names.stream()
            .filter(n -> n.length() > 4)    // 1. keep long ones
            .map(String::toUpperCase)       // 2. change each
            .sorted()                       // 3. alphabetical
            .toList();                      // 4. collect
}

// longNames(["Riya", "Arjun", "Meera"]) gives [ARJUN, MEERA]
```

Each line reads like a step of the sentence it implements. `passing` needs only steps 1 and 4.
:::

:::step{type=predict title="Guess first"}
:::question
After this code, what is `marks`?

```java
List<Integer> marks = List.of(72, 30, 90);
List<Integer> kept = marks.stream().filter(m -> m >= 40).toList();
```
:::
- [x] `[72, 30, 90]`
- [ ] `[72, 90]`
- [ ] `[]`
- [ ] It does not compile
:::explain
Streams never change the collection they came from: `kept` is a new list `[72, 90]`, and `marks` stays
exactly as it was.
:::
:::

:::step{type=try title="A pipeline in action"}
```bash run
cat > /tmp/Pipe.java <<'JAVA'
import java.util.List;

public class Pipe {
    public static void main(String[] args) {
        List<Integer> marks = List.of(72, 30, 90, 45, 12);
        System.out.println(marks.stream().filter(m -> m >= 40).toList());
        System.out.println(marks.stream().map(m -> m + 5).sorted().toList());
        System.out.println(marks);
    }
}
JAVA
java /tmp/Pipe.java
```
:::

:::step{type=task task=passing title="Warm-up: the passing marks"}
In `streams/Streams.java`, make `passing(marks)` return the marks of **40 or more**, in their original
order.

- `passing([72, 30, 90, 40, 39])` returns `[72, 90, 40]`
:::

:::step{type=concept title="Comparators: sorting by your own rule"}
To sort by something other than natural order, give `sorted` a **comparator**, a rule for which of two
items comes first. `Comparator` builds them for you:

```java
Comparator.comparing(String::length)              // shorter first
Comparator.comparing(String::length).reversed()   // longer first
Comparator.comparing(String::length)
          .thenComparing(Comparator.naturalOrder())  // ties: alphabetical
```

`thenComparing` decides only the ties left by the first rule, like sorting students by marks and then
by name.
:::

:::step{type=task task=sort_by_length title="Sort words by length"}
In `streams/Streams.java`, make `sortByLength(words)` return the words **shortest first**, with words
of the same length in alphabetical order, without changing the list it was given.

- `sortByLength([banana, fig, apple, kiwi, date])` returns `[fig, date, kiwi, apple, banana]`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `List.of(1, 2, 3).stream().map(n -> n * 10).toList()` give?
:::
- [ ] `[1, 2, 3]`
- [x] `[10, 20, 30]`
- [ ] `60`
- [ ] `[11, 12, 13]`
:::explain
`map` changes every item with the lambda: each number times ten.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In `Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder())`, when does the second
rule matter?
:::
- [ ] Always
- [x] Only for words of the same length
- [ ] Only for the first word
- [ ] Never
:::explain
`thenComparing` only decides ties left by the first rule.
:::
:::

:::step{type=deep-dive title="Streams under the hood"}
Streams are **lazy**: nothing happens until a final step such as `toList()`, `count()` or `forEach`.
Then each item flows through all the stations one at a time, so `filter` followed by `findFirst()` can
stop after the first match without looking at the rest.

`parallelStream()` spreads the work over several CPU cores, which can help for very large data and big
computations, but adds overhead for small lists. And a lambda can be used wherever Java expects a
**functional interface** (an interface with one method), such as `Runnable`, `Comparator` or
`Predicate`.
:::

:::step{type=recap}
- A lambda `x -> ...` is a small unnamed method passed where it is needed.
- A stream is a conveyor belt: `filter`, `map`, `sorted`, then `toList()`.
- Streams never change their source collection.
- `Comparator.comparing(...).thenComparing(...)` sorts by your own rules.
:::
