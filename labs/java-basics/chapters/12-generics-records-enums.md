:::step{type=story title="What if a typo could never reach the shelf?"}
Shelf stores each book's genre as text. One busy afternoon, someone types `"Fantsy"`. Nothing complains. The book
is saved, and from then on it never shows up when a member asks for fantasy books. Nobody notices for a month.

Java's whole personality is catching mistakes **before** the program runs: chapter 1 showed `javac` refusing a
missing semicolon. Today you get three tools that push that idea much further:

- **generics**, so one piece of code can work with any type and still be checked;
- **records** that refuse bad values the moment they are made;
- **enums**, a type with a fixed list of values, so `Fantsy` becomes a compile error instead of a month of silence.

:::mission
Make `Loan` refuse a blank title or a silly number of days, and make `Genre.fromText` turn typed text into a real
genre, or refuse it.
:::
:::

:::step{type=concept title="Generics: the type in angle brackets" file="12-generics-records-enums/Pair.java" line="5-17"}
You have been using generics since chapter 11: `List<String>` is a `List` with the type `String` filled in. You can
write your own. Open `Pair.java`:

```java
record Two<A, B>(A first, B second) { }
```

`A` and `B` are **type parameters**: blanks to fill in when you use it. `Two<String, Integer>` is a title and a
number; `Two<String, Boolean>` is a title and a yes or no. One record, any two types, and Java still checks each
use:

```bash run
cd /workspace/12-generics-records-enums && java Pair.java
```

```text
Two[first=Dune, second=4] Two[first=Emma, second=true]
5
Asha nobody
```

Look at line 15: `int number = shelf.second();` needs no cast. Java **knows** `second()` gives an `Integer` here,
because the type was written in the brackets. Try `String s = shelf.second();` and `javac` refuses it.

Methods can be generic too. `static <T> T firstOr(List<T> items, T fallback)` works for a list of anything, and
promises to give back the same type it was given.
:::

:::step{type=concept title="A record that checks its values" file="12-generics-records-enums/Loan.java" line="2-5"}
Chapter 9's records gave you a constructor for free. Free, but trusting: `new Loan("", -3)` would happily make a
nonsense loan. A record can add a **compact constructor**, a check that runs every time one is made:

```java
public record Loan(String title, int days) {
    public Loan {
        // checks go here
    }
}
```

No brackets after the name, no parameter list: the parameters are already `title` and `days`. Inside, you can
**replace** a value (`title = title.strip();`) or **throw** to refuse the whole thing. When the block ends, Java
stores whatever values are left in the fields.

Because records can never change after they are made, one check here protects the loan for its whole life.
:::

:::step{type=example title="Worked example: a rating from 1 to 5 stars"}
```java
public record Rating(String member, int stars) {
    public Rating {
        member = member.strip();
        if (stars < 1 || stars > 5) {
            throw new IllegalArgumentException("stars must be 1 to 5, not " + stars);
        }
    }
}
```

1. `member = member.strip();` tidies a value: the field gets the stripped name.
2. The `if` refuses impossible values with a clear message that shows the bad value.
3. `new Rating("Riya", 5)` works; `new Rating("Riya", 9)` throws before any rating exists. No half-made object
   can escape.
:::

:::step{type=task task=loan_record title="Your turn: a loan that refuses nonsense"}
Open `Loan.java` and fill in the compact constructor:

- strip the title, so `new Loan("  Dune ", 14).title()` is `"Dune"`;
- a title that is blank after stripping throws an `IllegalArgumentException`;
- days must be from 1 to 60: `0` and `61` throw, `1` and `60` are fine.

```bash run
cd /workspace/12-generics-records-enums && java Loan.java
```

When it works, it prints `Loan[title=Dune, days=14]`, then `refused:` and your message. Then press **Check**.
:::

:::step{type=concept title="Enums: a type with a fixed list of values" file="12-generics-records-enums/Days.java" line="3-22"}
Open `Days.java`:

```java
enum Genre {
    FANTASY, HISTORY, CHILDREN
}
```

An **enum** (short for enumeration) is a type whose values are listed once, forever. A `Genre` variable can only
ever hold `FANTASY`, `HISTORY` or `CHILDREN`. Write `Genre.FANTSY` and the program does not compile. The typo from
the start of the chapter cannot happen.

And `switch` works beautifully with enums:

```java
return switch (genre) {
    case CHILDREN -> 14;
    case FANTASY, HISTORY -> 21;
};
```

This is a **switch expression**: it gives back a value, and each `->` arm is one answer. Here is the best part:
remove the `HISTORY` arm, and `javac` refuses, because the switch no longer covers every genre. Add a genre next
year, and the compiler points you at every switch that needs a new arm.
:::

:::step{type=try title="Values, names and a refusal" file="12-generics-records-enums/Days.java" line="14-23"}
```bash run
cd /workspace/12-generics-records-enums && java Days.java
```

```text
CHILDREN 14 2
FANTASY HISTORY CHILDREN 
true
Exception in thread "main" java.lang.IllegalArgumentException: No enum constant Days.Genre.Fantasy
	at java.base/java.lang.Enum.valueOf(Enum.java:293)
	at Days$Genre.valueOf(Days.java:3)
	at Days.main(Days.java:22)
```

- An enum value prints its own name, and `ordinal()` is its position in the list (CHILDREN is third, so 2).
- `Genre.values()` gives every value, in order.
- `Genre.valueOf("HISTORY")` turns text into the value. Each value exists exactly once, so `==` is safe for enums.
- And the crash, read from the top as chapter 6 taught: `valueOf("Fantasy")` is refused, because the name must
  match **exactly**, capitals included. Text typed by people is never that tidy.
:::

:::step{type=example title="Worked example: tidy text, then valueOf"}
A small enum for the library's floors:

```java
enum Floor { GROUND, FIRST, SECOND }

static Floor floorFrom(String text) {
    return Floor.valueOf(text.strip().toUpperCase());
}
```

1. `strip()` removes the spaces around the text and `toUpperCase()` matches the enum's capitals (chapter 7).
2. `valueOf` does the rest. `floorFrom(" first ")` gives `FIRST`.
3. Unknown text, such as `"roof"`, still throws an `IllegalArgumentException` from `valueOf`. That is what you want:
   a loud refusal, not a wrong floor.
:::

:::step{type=task task=genre_enum title="Your turn: from typed text to a genre"}
Open `Genre.java`. It lists `FANTASY, SCIENCE_FICTION, HISTORY, CHILDREN`. Make `fromText(text)` turn typed text into
one of them:

- capitals and the spaces around it do not matter: `fromText("Fantasy")` gives `FANTASY`;
- the spaces between words, even several, become one underscore: `fromText("  science   fiction ")` gives
  `SCIENCE_FICTION`;
- text that is not a genre (`"Fantsy"`, or an empty text) throws an `IllegalArgumentException`.

Chapter 7's `split("\\s+")` and `String.join` will help with the middle rule.

```bash run
cd /workspace/12-generics-records-enums && java Genre.java
```

Then press **Check**.
:::

:::step{type=concept title="Switch on the kind of thing" file="12-generics-records-enums/Kinds.java" line="3-17"}
One more modern trick, and it combines everything in this chapter. Open `Kinds.java`:

```java
sealed interface Item permits Book, Dvd, Atlas { }

record Book(String title, int pages) implements Item { }
record Dvd(String title, int minutes) implements Item { }
record Atlas(String place) implements Item { }
```

`sealed ... permits` says these three are the **only** kinds of `Item` there will ever be. Now a switch can ask
which kind it has, and unpack it in the same breath:

```java
return switch (item) {
    case Book b when b.pages() > 500 -> b.title() + ": a long read";
    case Book b -> b.title() + ": " + b.pages() + " pages";
    case Dvd d -> d.title() + ": " + d.minutes() + " minutes";
    case Atlas a -> "an atlas of " + a.place();
};
```

```bash run
cd /workspace/12-generics-records-enums && java Kinds.java
```

```text
Dune: a long read
Emma: 474 pages
Planet Earth: 550 minutes
an atlas of Goa
```

`case Book b` means "if it is a Book, call it `b`". `when` adds a condition, and the arms are tried from the top, so
the long-book arm must come first. As with enums, leave out `Atlas` and `javac` refuses: it knows every kind there
is. This is Java 21, and it is the newest thing in this course.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why is `Genre.FANTSY` better than the text `"Fantsy"`?
:::
- [ ] It runs faster
- [x] It does not compile, so the typo is caught before the program runs
- [ ] It is shorter
:::explain
An enum lists its values once. Any name that is not on the list is a compile error, while a typo in text is just
more text.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In a record's compact constructor, what does `title = title.strip();` do?
:::
- [x] The field gets the stripped title
- [ ] Nothing: records can never change
- [ ] It is a compile error
:::explain
Inside the compact constructor the values are not stored yet, so you may replace them. Once the record exists, its
values can never change.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `T` in `static <T> T firstOr(List<T> items, T fallback)`?
:::
- [ ] A class called T
- [x] A blank for a type, filled in each time the method is used
- [ ] The word "text"
:::explain
`T` is a type parameter. Call it with a `List<String>` and T is `String`; with a `List<Integer>`, T is `Integer`.
:::
:::

:::step{type=deep-dive title="Go deeper: enums with fields, erasure and wildcards"}
**Enums can carry data.** Each value can have its own fields and methods:
`FANTASY(21), CHILDREN(14);` with a constructor `Genre(int days) { this.days = days; }`. An enum is a full class
whose objects are made once, at start-up, and never again.

**Type erasure.** Generics exist for the compiler. After checking, `javac` removes them, so at run time a
`List<String>` and a `List<Integer>` are both just a `List`. That is why `new T()` is not allowed: by then, nobody
knows what T was.

**Wildcards.** `List<? extends Shape>` means "a list of some kind of Shape": it accepts a `List<Circle>`, which a
plain `List<Shape>` parameter does not. You will see `?` all over Java's library.

**Where these came from.** Generics arrived in Java 5 (2004), enums too; records in Java 16 (2021); pattern-matching
switch in Java 21 (2023). Java keeps every old program working while growing new tools.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read and write generic types and methods: `Two<A, B>`, `<T> T firstOr(...)`.
- Protect a record with a compact constructor that tidies values or refuses them.
- Use an enum for a fixed list of values, with `values()`, `valueOf` and a switch expression.
- Switch on the kind of a sealed family of records, with `case Book b when ...`.

:::photo{src="/lesson-images/java/java-12-notes.webp" alt="Handwritten notes about generics, records and enums: angle brackets are blanks for a type, compact constructor checks values, enum has a fixed list, switch covers every case, sealed permits" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 2. Shelf's data is now made of real types that protect themselves. Next, Part 3: when
things go wrong, starting with exceptions.
:::
