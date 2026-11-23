:::step{type=story title="What happens when the array needs one more slot?"}
Chapter 8's arrays have one hard rule: the size is fixed when the array is made. Shelf's queue at the desk has
three people in it. A fourth walks in. The array has nowhere to put her.

You could make a bigger array and copy everyone across, every single time someone arrives. Java's own library
already did that work for you, carefully, in a family of classes called **collections**: lists that grow and
shrink, maps that find a value by its name in an instant, and sets that never hold the same thing twice.

:::mission
Write `topN`, which picks the n biggest numbers without disturbing the list it was given, and `count`, which
counts how often each word appears.
:::
:::

:::step{type=concept title="ArrayList: an array that grows" file="11-collections/Desk.java" line="11-16"}
Open `Desk.java`:

```java
List<String> queue = new ArrayList<>();
queue.add("Asha");
queue.add("Kabir");
queue.add("Riya");
queue.remove("Kabir");
System.out.println(queue + " " + queue.size() + " " + queue.get(0));
```

- `List<String>` reads "a list of strings". The type inside the **angle brackets** says what the list holds, and
  Java checks it: `queue.add(42)` will not compile.
- `new ArrayList<>()` makes an empty list. The empty `<>` (the "diamond") means "the same type as on the left".
- `add` puts a value at the end, `remove` takes one out, `size()` counts, `get(i)` reads position i (from 0,
  as always).

And unlike an array, a list prints its values: no `[I@` mystery here.
:::

:::step{type=try title="Run the desk" file="11-collections/Desk.java" line="11-26"}
```bash run
cd /workspace/11-collections && java Desk.java
```

```text
[Asha, Riya] 2 Asha
4 null false
2 true
```

The first line is the queue after Kabir left. The other two lines come from a map and a set, which you will meet in
a moment. First, a strange rule about numbers in lists.
:::

:::step{type=concept title="List<Integer>, not List<int>" file="11-collections/RemoveTrap.java" line="7-11"}
Collections hold **objects** only, and `int` is not an object. So for numbers you write `List<Integer>`: `Integer`
is the object version of `int`. Java converts between the two by itself (that is called **boxing**), so
`fines.add(5)` just works.

Nearly always, you will not notice. Once, you will. Open `RemoveTrap.java`:

```java
List<Integer> fines = new ArrayList<>(List.of(5, 9, 1));
fines.remove(1);
System.out.println(fines);
```

Before you run it: the list holds a 1, so surely the 1 disappears?

```bash run
cd /workspace/11-collections && java RemoveTrap.java
```

```text
[5, 1]
[1]
```

The 9 vanished. `remove(1)` took out the value at **position** 1, not the value 1. A list has two `remove` methods, one taking a
position (`int`) and one taking an object, and a plain `1` is an `int`. To remove the **value**, pass an object:
`fines.remove(Integer.valueOf(5))`, which made the second line.
:::

:::step{type=example title="Worked example: sort a copy, not the original"}
Sorting a list changes that list in place. A method that sorts the list it was given wrecks the caller's data
(the same lesson as arrays in chapter 8). So copy first:

```java
List<Integer> numbers = new ArrayList<>(List.of(3, 1, 2));
List<Integer> copy = new ArrayList<>(numbers);
copy.sort(Comparator.reverseOrder());
System.out.println(numbers + " " + copy + " " + copy.subList(0, 2));
```

```text
[3, 1, 2] [3, 2, 1] [3, 2]
```

1. `new ArrayList<>(numbers)` builds a **new** list with the same values. The original stays as it was.
2. `sort(Comparator.reverseOrder())` sorts biggest first; `sort(null)` or `Collections.sort(copy)` sorts smallest
   first.
3. `subList(0, 2)` is a view of positions 0 and 1. Asking for more than the list has throws an exception, so check
   the size first: `Math.min(n, copy.size())`.
:::

:::step{type=task task=top_n title="Your turn: the n biggest numbers"}
Open `ListTools.java` and make `topN(numbers, n)` give back the n biggest numbers, **biggest first**, without
changing the list it was given.

`topN([72, 45, 90, 66], 2)` gives `[90, 72]`. Asking for more numbers than there are gives them all, and `n = 0`
gives an empty list.

```bash run
cd /workspace/11-collections && java ListTools.java
```

Then press **Check**.
:::

:::step{type=concept title="HashMap and HashSet: find it by name" file="11-collections/Desk.java" line="18-25"}
Back in `Desk.java`, a **map** remembers which shelf each book is on:

```java
Map<String, Integer> shelfOf = new HashMap<>();
shelfOf.put("Dune", 3);
shelfOf.put("The Hobbit", 1);
shelfOf.put("Dune", 4);
System.out.println(shelfOf.get("Dune") + " " + shelfOf.get("Emma") + " " + shelfOf.containsKey("Emma"));
```

:::picture{name="phone-book" code='shelfOf.get("Dune")'}
A map is a phone book: you look a value up by its key, without reading every page.
:::

A map holds **key-value pairs**: the key is the title, the value the shelf. Each key appears only once, so the second
`put("Dune", 4)` **replaced** the 3. That is why line two said `4 null false`: Dune is on shelf 4; `get` of a key
that is not there gives `null`, not an error; and `containsKey` asks politely first.

A **set** is a bag that keeps one of each. `new HashSet<>(List.of("Asha", "Riya", "Asha", "Asha"))` holds just two
names, which is line three: `2 true`.

Why "Hash"? A `HashMap` does not search through every key. It turns the key into a number (its **hash code**) that
says where to look, so `get` takes about the same time with 10 books or 10 million.
:::

:::step{type=example title="Worked example: copies per title"}
Donations arrive as pairs, and the same title can come twice. Add up the copies of each title:

```java
Map<String, Integer> stock = new HashMap<>();
String[] titles = {"Dune", "Emma", "Dune"};
int[] copies = {2, 1, 3};
for (int i = 0; i < titles.length; i++) {
    stock.put(titles[i], stock.getOrDefault(titles[i], 0) + copies[i]);
}
System.out.println(stock);
```

```text
{Dune=5, Emma=1}
```

1. `getOrDefault(key, 0)` reads the total so far, or 0 the first time a title shows up.
2. Add this donation, and `put` the new total back, replacing the old one.

Counting is the same idea, adding 1 each time instead of the copies.
:::

:::step{type=predict title="Guess first"}
:::question
`m` is an empty `HashMap<String, Integer>`. After `m.put("Emma", 1); m.put("Emma", 2);`, what is `m.size()`?
:::
- [x] `1`
- [ ] `2`
- [ ] `3`
:::explain
A key can only appear once. The second `put` replaced the value 1 with 2, so there is still just one pair.
:::
:::

:::step{type=task task=word_counts title="Your turn: count each word"}
Open `WordCounter.java` and make `count(words)` give back a map of each word, in **lower case**, to how many times it
appears. Capitals should not matter: `Jelly` and `JELLY` are the same word.

`count([jelly, Cookie, JELLY, jelly])` gives `{cookie=1, jelly=3}` (a `HashMap` may print the pairs in any order),
and no words give an empty map.

```bash run
cd /workspace/11-collections && java WordCounter.java
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which collection fits "every member's id, each one only once, and I only need to ask whether an id is there"?
:::
- [ ] `ArrayList`
- [x] `HashSet`
- [ ] `HashMap`
:::explain
A set keeps one of each and answers `contains` fast. A map would fit if each id also needed a value.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
On a `List<Integer>` holding `[7, 3, 1]`, what does `remove(1)` remove?
:::
- [ ] The value 1
- [x] The 3, the value at position 1
- [ ] Nothing
:::explain
With an `int` argument, `remove` means a position. `remove(Integer.valueOf(1))` removes the value 1.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `shelfOf.get("Emma")` give when the map has no key `"Emma"`?
:::
- [ ] `0`
- [x] `null`
- [ ] It throws an exception
:::explain
A missing key gives `null`. Use `getOrDefault` or `containsKey` when that matters.
:::
:::

:::step{type=deep-dive title="Go deeper: unchangeable lists, order, and the big three"}
**List.of cannot change.** `List.of(1, 2)` makes a list that refuses changes: `add(3)` throws
`UnsupportedOperationException`. That is a feature: share it, and nobody can break it. Wrap it in
`new ArrayList<>(...)` when you need to change it.

**Order.** A `HashMap` or `HashSet` keeps no particular order. `LinkedHashMap` keeps the order you added things in;
`TreeMap` keeps keys sorted.

**Changing while looping.** Removing from a list inside a `for (x : list)` loop throws a
`ConcurrentModificationException`. Use `list.removeIf(x -> x < 0)` instead (chapter 14 explains the arrow).

**The interfaces.** `List`, `Set` and `Map` are interfaces (chapter 10), and `ArrayList`, `HashSet` and `HashMap` are
classes that implement them. That is why you write `List<String> queue = new ArrayList<>()`: the rest of the
program only depends on the promise, so swapping in a `LinkedList` later changes one line.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Use `ArrayList` for a growing list: `add`, `get`, `remove`, `size`.
- Write `List<Integer>`, not `List<int>`, and avoid the `remove(1)` trap.
- Sort a copy, never the caller's list, and take a safe `subList`.
- Look things up with `HashMap` (`put`, `get`, `getOrDefault`) and keep one of each with `HashSet`.

:::photo{src="/lesson-images/java/java-11-notes.webp" alt="Handwritten notes about Java collections: ArrayList grows, List of Integer not int, remove(1) means position 1, sort a copy, HashMap put and get, HashSet keeps one of each" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 12: generics, records and enums, the types that make Shelf's data safe.
:::
