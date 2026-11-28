:::step{type=story title="How can one loop lend a book and a DVD?"}
Shelf's library now lends DVDs too. A book goes home for 21 days, a DVD for 7. The desk has a pile of both, and
one loop must print how long each may stay out.

Here is the puzzle: a `Book` is not a `Dvd`, and a loop over a list can only have one type for its variable. Do
you write two loops? Ten loops, when the library adds magazines, games and maps?

No. You write down **what they have in common**, give it a name, and write the loop once for that name. In Java,
that written-down promise is an **interface**, and it is the idea every big Java program is built on.

:::mission
Give rectangles and circles an `area()` so Shelf can work out how much carpet the library floor needs, then add up
the area of any mix of shapes.
:::
:::

:::step{type=concept title="A promise, written down" file="10-interfaces/Loans.java" line="5-8"}
Open `Loans.java`. Near the top (inside the class `Loans`, so the whole example fits in one file):

```java
interface Lendable {
    String name();
    int loanDays();
}
```

An interface is a list of methods with **no bodies**. It says: "anything that is `Lendable` can tell you its name
and its loan days". It does not say how; each kind of thing decides that for itself.

:::picture{name="plug-socket"}
An interface is a socket: any device with the right plug fits, whatever the device is.
:::
:::

:::step{type=try title="Two kinds of things, one loop" file="10-interfaces/Loans.java" line="10-27"}
Below the interface, two records **implement** it, each with its own answer:

```java
record Book(String name) implements Lendable {
    public int loanDays() {
        return 21;
    }
}

record Dvd(String name) implements Lendable {
    public int loanDays() {
        return 7;
    }
}
```

(A record's `name()` getter already keeps the first promise.) And `main` puts both kinds in **one** list of
`Lendable`:

```bash run
cd /workspace/10-interfaces && java Loans.java
```

```text
The Hobbit: 21 days
Planet Earth: 7 days
Dune: 21 days
```

The loop variable is `Lendable item`. The loop has no idea which items are books and which are DVDs, and it does
not need to: each object answers `loanDays()` in its own way. That is called **polymorphism** (Greek for "many
shapes"): one call, a different behaviour for each kind of object. Add a `Magazine` tomorrow, and this loop works
for it without a single change.
:::

:::step{type=concept title="When one file is not enough" file="10-interfaces/Shapes.java" line="1-15"}
Your task lives in four files, one type each, which is how real Java projects are laid out:

| File | What it is |
|---|---|
| `Shape.java` | the interface: `double area();` |
| `Rect.java` | a rectangle, `implements Shape` |
| `Circle.java` | a circle, `implements Shape` |
| `Shapes.java` | `totalArea`, and a `main` with the library's floor plan |

`java Shapes.java` runs one file, and that file uses three others, so in Java 21 it cannot find them. We tried it:

```text
Shapes.java:7: error: cannot find symbol
    public static double totalArea(List<Shape> shapes) {
                                        ^
  symbol:   class Shape
```

(Java 22 and later can launch a program of several source files this way; your lab runs Java 21.) The fix is the
two-step you met in chapter 1: **compile** all the files with `javac`, then **run** the class with the `main`:

```bash run
cd /workspace/10-interfaces && javac -d out *.java && java -cp out Shapes
```

- `javac -d out *.java` compiles every `.java` file here and puts the `.class` files in a folder called `out`.
- `java -cp out Shapes` runs the class `Shapes`; `-cp` (the **class path**) tells Java where the `.class` files are.

Right now it prints `Library floor: 0.0 square metres`, because every `area()` still says 0.
:::

:::step{type=example title="Worked example: a square keeps the promise"}
A class signs the promise with `implements`, and must then give every method in the interface a body:

```java
public class Square implements Shape {
    private final double side;

    public Square(double side) {
        this.side = side;
    }

    @Override
    public double area() {
        return side * side;
    }
}
```

1. `implements Shape` is the signature on the promise. Leave `area()` out, and `javac` refuses: `Square is not
   abstract and does not override abstract method area() in Shape`.
2. `@Override` tells Java "this method keeps a promise". Misspell it as `aera()`, and you get a compile error,
   `method does not override or implement a method from a supertype`, instead of a silent second method that
   nobody calls. (We tried both: misspelling the method gives both errors at once.)
3. The method must be `public`: interface methods always are.
:::

:::step{type=task task=areas title="Your turn: each shape's area"}
Open `Rect.java` and `Circle.java` and make each `area()` give the right answer:

- a rectangle: width times height, so `new Rect(3, 4).area()` gives `12.0`;
- a circle: pi times the radius squared, with `Math.PI`, so `new Circle(2).area()` gives about `12.566`
  (exactly, Java prints `12.566370614359172`).

```bash run
cd /workspace/10-interfaces && javac -d out *.java && java -cp out Shapes
```

Then press **Check**. The usual slip: `radius * 2 * Math.PI`, which is the distance around the circle, not its
area. Squaring is `radius * radius`.
:::

:::step{type=predict title="Guess first"}
:::question
`List<Shape> plan = List.of(new Rect(2, 3), new Circle(1));` In `for (Shape s : plan)`, which `area()` runs for the
second item?
:::
- [ ] `Shape`'s own `area()`
- [x] `Circle`'s `area()`
- [ ] None: the loop only knows about `Shape`
:::explain
The variable's type is `Shape`, but the object is a `Circle`, and Java always runs the method of the real object.
`Shape`'s `area()` has no body at all.
:::
:::

:::step{type=task task=total_area title="Your turn: the whole floor"}
In `Shapes.java`, make `totalArea(shapes)` add up the areas of any list of shapes, rounded to two decimals (chapter
3's `Math.round(x * 100) / 100.0`). An empty list gives `0.0`.

A list with `new Rect(3, 4)` and `new Circle(1)` gives `15.14` (12 + 3.14159...). With both tasks done, the floor
plan in `main` (a reading room of 8 by 5 metres, 40 square metres, and a round corner with radius 2, 12.566...)
prints `Library floor: 52.57 square metres`.

```bash run
cd /workspace/10-interfaces && javac -d out *.java && java -cp out Shapes
```

Then press **Check**. The usual slip: rounding each area inside the loop and not the total. Adding rounded decimals
brings back chapter 3's tiny leftovers: we tried four shapes that way and got `27.990000000000002`. Add everything
first, then round once, at the end.
:::

:::step{type=concept title="The other way to share: extends" file="10-interfaces/Members.java" line="3-28"}
An interface shares a promise. Sometimes you want to share **code**, too. Open `Members.java` (shortened here):

```java
static class Member {
    final String name;
    Member(String name) { this.name = name; }
    int maxBooks() { return 5; }
    String describe() { return name + " may borrow " + maxBooks() + " books"; }
}

static class Student extends Member {
    Student(String name) { super(name); }

    @Override
    int maxBooks() { return 2; }
}
```

```bash run
cd /workspace/10-interfaces && java Members.java
```

```text
Asha may borrow 5 books
Kabir may borrow 2 books
```

`Student extends Member` means a student **is** a member: it gets `name` and `describe()` for free and changes only
what is different, the limit. `super(name)` calls the parent's constructor. And look at Kabir's line: the parent's
`describe()` called `maxBooks()`, and Java ran the **student's** version. Polymorphism again.

A class can `extend` only **one** class, but `implement` as many interfaces as it likes. That is one reason most
Java teams reach for interfaces first and keep `extends` for real "is a" families.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does an interface contain?
:::
- [ ] Fields and their values
- [x] Methods that every implementing class must provide
- [ ] A `main` method
:::explain
An interface lists methods (normally without bodies). Each class that implements it writes the bodies.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why does `java Shapes.java` fail here, while `javac -d out *.java && java -cp out Shapes` works?
:::
- [ ] `Shapes.java` has an error
- [x] The single-file launcher compiles only that one file, and `Shapes` needs the other three
- [ ] `java` cannot run interfaces
:::explain
`java File.java` is for one-file programs. A program made of several files is compiled together with `javac`
first.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
How many classes can one class `extend`, and how many interfaces can it `implement`?
:::
- [x] One class, many interfaces
- [ ] Many classes, one interface
- [ ] One of each
:::explain
Java allows a single parent class but any number of interfaces: `class Dvd implements Lendable, Comparable<Dvd>`.
:::
:::

:::step{type=deep-dive title="Go deeper: default methods, abstract classes and sealed types"}
**Default methods.** Since Java 8, an interface can give a method a body with `default`:
`default boolean isShortLoan() { return loanDays() < 14; }`. Every `Lendable` gets it for free. That is how Java added
new methods to `List` without breaking every program that implemented it.

**Abstract classes.** Halfway between the two: an `abstract class` can have fields and finished methods, plus
`abstract` methods with no body that children must fill in. You cannot create one with `new`.

**Sealed interfaces.** `sealed interface Shape permits Rect, Circle` says these are the **only** shapes there will
ever be. Java then checks that a `switch` over a shape handles every kind (chapter 12 shows switch on types).

**Interfaces everywhere.** `List`, `Map`, `Comparable`, `Runnable`: most of the Java library you will meet next is
interfaces, and Spring Boot is built almost entirely on them.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write an interface and classes or records that `implements` it, with `@Override`.
- Put different kinds of objects in one list and let each answer in its own way (polymorphism).
- Compile a program of several files with `javac -d out *.java` and run it with `java -cp out`.
- Share code with `extends` and `super`, and say why interfaces usually come first.

:::photo{src="/lesson-images/java/java-10-sketch.webp" alt="Sketchnote: Interfaces. An interface lists methods, usually without bodies; each class that implements it writes its own version. Flow: interface Shape, Rect implements Shape, Circle implements Shape, a List of Shape called floor, s.area() for each. Remember: Java runs the method of the real object; @Override turns a misspelt method into a compile error; javac -d out *.java, then java -cp out Shapes; extends one class, implements many interfaces." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 11: collections, the lists, sets and maps that grow as you need.
:::
