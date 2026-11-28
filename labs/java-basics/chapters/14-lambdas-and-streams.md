:::step{type=story title="How many lines does it take to say 'sort by length'?"}
Before 2014, telling Java "sort these titles by their length" took six lines of ceremony: a whole unnamed class,
an `@Override`, a method signature, all to say one small thing, `a.length() - b.length()`.

Then Java 8 arrived, in 2014, with **lambdas**, and the same rule shrank to one line. It is often called the
biggest change to the language since it was born, and it brought **streams** with it: a way to say "the overdue books, titles in
capitals, sorted" almost exactly as you would say it in English.

Today Shelf learns to talk like that.

:::mission
Write `passing`, which keeps the marks of 40 or more with one stream, and `sortByLength`, which sorts words by
length with a tie rule of its own.
:::
:::

:::step{type=try title="One rule, three eras of Java" file="14-lambdas-and-streams/OldAndNew.java" line="8-22"}
Open `OldAndNew.java`. It sorts the same list three times:

```java
titles.sort(new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.length() - b.length();
    }
});

titles.sort((a, b) -> b.length() - a.length());

titles.sort(Comparator.comparing(String::length));
```

```bash run
cd /workspace/14-lambdas-and-streams && java OldAndNew.java
```

```text
[It, Emma, Dune, Ulysses]
[Ulysses, Emma, Dune, It]
[It, Emma, Dune, Ulysses]
```

1. **2004 style** (Java 5 added the `<String>` part that year): an *anonymous class*, a class with no name,
   written and used in one place, that implements the `Comparator` interface (chapter 10) on the spot. A comparator's
   `compare` gives back a negative number when `a` should come first, a positive one when `b` should, and 0 for a
   tie; `a.length() - b.length()` does exactly that.
2. **A lambda**: `(a, b) -> b.length() - a.length()` is the same `compare` method with everything obvious left out.
   This one sorts longest first.
3. **A method reference**: `String::length` means "call `length()` on each one", and `Comparator.comparing` builds
   the whole comparator from it.
:::

:::step{type=concept title="A lambda is a method without a name"}
Read a lambda in two halves, around the arrow:

```java
(a, b) -> b.length() - a.length()
```

- Left of `->`: the **parameters**. Java works out their types from where the lambda is used.
- Right of `->`: the **body**. One expression is returned automatically; longer bodies use `{ }` and `return`.
- `m -> m >= 40` has one parameter, so it needs no brackets.

Where can a lambda go? Anywhere Java expects an interface with exactly **one** method to fill in, like
`Comparator` (`compare`) or `Predicate` (`test`). The lambda *is* that one method. That is the whole trick: lambdas
are built on the interfaces you met in chapter 10.
:::

:::step{type=concept title="A stream is a conveyor belt" file="14-lambdas-and-streams/Pipeline.java" line="14-20"}
Open `Pipeline.java`. Shelf has four books, some overdue:

```java
List<String> late = books.stream()
        .filter(b -> b.overdue())
        .map(b -> b.title().toUpperCase())
        .sorted()
        .toList();
```

Read it top to bottom, like a sentence: *take the books; keep the overdue ones; turn each into its title in capitals;
sort them; make a list.*

:::picture{name="conveyor-belt"}
A stream is a conveyor belt: each station does one small job, and items flow through them in order.
:::

- `stream()` puts the items on the belt.
- `filter` keeps the items for which the lambda says `true`.
- `map` turns each item into something else: here a `Book` becomes a `String`.
- `sorted` puts them in order, and `toList()` collects what reaches the end into a new list.
:::

:::step{type=try title="Run the pipeline" file="14-lambdas-and-streams/Pipeline.java" line="14-25"}
```bash run
cd /workspace/14-lambdas-and-streams && java Pipeline.java
```

```text
[DUNE, IT, ULYSSES]
3 overdue, 2954 pages in all
4
```

The second line used two more stations that end a stream with a single value: `count()`, and `mapToInt(...)`
followed by `sum()`. `Book::overdue` and `Book::pages` are method references again.

And the last line matters most: `books` still has 4 books. A stream never changes the list it came from. It
builds something **new**, which is exactly the habit chapters 8 and 11 taught by hand.
:::

:::step{type=example title="Worked example: the long titles, shortest first"}
Keep the titles longer than 3 letters, shortest first:

```java
List<String> titles = List.of("Ulysses", "It", "Emma", "Dune");
List<String> longOnes = titles.stream()
        .filter(t -> t.length() > 3)
        .sorted(Comparator.comparing(String::length))
        .toList();
// [Emma, Dune, Ulysses]
```

1. `filter` drops `It`.
2. `sorted(...)` takes a comparator: by length.
3. Look at the tie. `Emma` and `Dune` both have 4 letters, and they stay in the order they arrived. Java's sort is
   **stable**: it never swaps equal items. If you want ties in a particular order, you must say so with
   `thenComparing(...)`. Your second task needs exactly that.
:::

:::step{type=predict title="Guess first"}
:::question
What does this print?

```java
List<Integer> marks = new ArrayList<>(List.of(72, 30, 90));
List<Integer> high = marks.stream().filter(m -> m > 50).toList();
System.out.println(marks.size() + " " + high.size());
```
:::
- [ ] `2 2`
- [x] `3 2`
- [ ] `3 3`
:::explain
`filter` builds a new list with 72 and 90; the original list still has all 3 marks.
:::
:::

:::step{type=task task=passing title="Your turn: the passing marks"}
Open `Streams.java` and make `passing(marks)` give back the marks of **40 or more**, in their original order, with
one stream.

`passing([72, 30, 90, 40, 39])` gives `[72, 90, 40]`.

```bash run
cd /workspace/14-lambdas-and-streams && java Streams.java
```

Right now it prints `[]` and the words in their original order. Then press **Check**. The usual slip: `m > 40`,
which drops the 40 (the task says 40 **or more**).
:::

:::step{type=concept title="Lazy: nothing happens until you ask" file="14-lambdas-and-streams/Lazy.java" line="7-13"}
Here is something curious. Open `Lazy.java`: its `filter` prints every title it checks.

```java
Stream<String> s = List.of("Dune", "Emma", "It").stream()
        .filter(t -> {
            System.out.println("  checking " + t);
            return t.length() > 2;
        });
System.out.println("pipeline built");
System.out.println(s.findFirst().get());
```

```bash run
cd /workspace/14-lambdas-and-streams && java Lazy.java
```

```text
pipeline built
  checking Dune
Dune
```

`pipeline built` came **first**: building the pipeline checked nothing at all. Streams are **lazy**. The work only
starts when a final step (`toList`, `count`, `findFirst`) asks for a result. And `Emma` and `It` were never checked,
because `findFirst` had its answer after one item. With a million books, that laziness is a gift.
:::

:::step{type=task task=sort_by_length title="Your turn: shortest first, ties alphabetical"}
In `Streams.java`, make `sortByLength(words)` give back the words **shortest first**, and words of the same length in
**alphabetical** order. The list it was given must not change.

`sortByLength([banana, fig, apple, kiwi, date])` gives `[fig, date, kiwi, apple, banana]`: `date` comes before
`kiwi` because d comes before k.

`Comparator.comparing(String::length)` sorts by length; `.thenComparing(Comparator.naturalOrder())` adds the
alphabetical tie rule. ("Natural order" for strings means alphabetical.)

```bash run
cd /workspace/14-lambdas-and-streams && java Streams.java
```

Then press **Check**.

The usual slips (we tried them): the two rules the other way round, alphabetical first, which gives
`[apple, banana, date, fig, kiwi]`: the length rule never gets a say, because no two words tie alphabetically. And
`words.sort(...)` on the list itself: `main` passes a `List.of(...)`, which refuses changes, so it throws
`UnsupportedOperationException`. Sort a stream, or a copy.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `map` do in a stream?
:::
- [ ] Keeps some items and drops others
- [x] Turns each item into a new value
- [ ] Builds a HashMap
:::explain
`filter` keeps or drops; `map` transforms each item, like a `Book` into its title.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Where can a lambda be used?
:::
- [ ] Anywhere a value is expected
- [x] Where Java expects an interface with exactly one method to fill in
- [ ] Only inside streams
:::explain
A lambda fills in that single method: `compare` for a `Comparator`, `test` for a `Predicate`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A stream pipeline has `filter` and `map`, but no final step like `toList()`. How many items does it process?
:::
- [ ] All of them
- [x] None
- [ ] Only the first
:::explain
Streams are lazy: without a final step that asks for a result, nothing runs at all.
:::
:::

:::step{type=deep-dive title="Go deeper: collectors, Optional and parallel streams"}
**Collectors.** `collect(Collectors.groupingBy(Book::overdue))` splits books into a map of `true` and `false` lists;
`Collectors.joining(", ")` glues strings together. Chapter 11's word counter is one line with
`groupingBy(w -> w, Collectors.counting())`.

**Optional.** `findFirst()` gives an `Optional<String>`: a box that may be empty, because a stream can have no items.
`.get()` on an empty one throws; `.orElse("none")` is safer. It is Java's answer to the `null` problem from chapter 9.

**Parallel streams.** `parallelStream()` splits the work across processor cores. It only pays off for big, slow work,
and only when the lambdas do not change shared variables.

**Where lambdas came from.** The idea is from mathematics: Alonzo Church's lambda calculus, in the 1930s. The Greek
letter λ is why they are called lambdas, in Java, Python and nearly every language today.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write lambdas (`m -> m >= 40`, `(a, b) -> ...`) and method references (`String::length`).
- Build stream pipelines with `filter`, `map`, `sorted`, `toList`, `count` and `mapToInt(...).sum()`.
- Sort with `Comparator.comparing` and give ties a rule with `thenComparing`.
- Explain why streams never change their source, and why they are lazy.

:::photo{src="/lesson-images/java/java-14-sketch.webp" alt="Sketchnote: Lambdas and streams. A lambda is a method with no name; a stream passes items through steps and builds something new. Flow: books.stream(), filter by overdue, map to the title, sorted(), toList(). Remember: filter keeps items, map turns each item into a new value; a stream never changes the list it came from; streams are lazy, nothing runs until a final step; thenComparing gives ties a rule." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 15: files and a command-line program, so Shelf can read real data from disk.
:::
