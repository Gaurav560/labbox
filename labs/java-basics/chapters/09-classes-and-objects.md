:::step{type=story title="What if Java had a type called Book?"}
Java comes with types: `int`, `String`, arrays. It has never heard of a book. Yet Shelf is all about books: each
one has a title, a number of copies on the shelf, and things you can do with it, like borrow it.

Architects solved this problem long before programmers: draw the plan **once**, and build as many houses from it
as you like. A class is that plan; every `new` builds one more house.

:::photo{src="/lesson-images/java/blueprint.webp" alt="A blue architectural blueprint drawing of a tall building, with white lines and a title block in the corner" credit="Warner, Burns, Toan and Lunde" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Original_Blueprint_of_United_States_National_Agricultural_Library.jpg"}
A blueprint of the US National Agricultural Library: one plan, one building.
:::

So you make your own type. In Java that is a **class**, and you have been writing one in every chapter without
using its real power: until now, every class was just a box for static methods. Today you create **objects**:
real books, each with its own data, that protect themselves from bad changes.

:::mission
Finish `Point`, a record that knows the distance to another point, and `BankAccount`, an object that refuses
bad deposits and withdrawals.
:::
:::

:::step{type=concept title="A class is a blueprint; objects are what you build" file="09-classes-and-objects/Book.java" line="2-21"}
Open `Book.java`:

```java
public class Book {
    private final String title;
    private int copies;

    public Book(String title, int copies) {
        this.title = title;
        this.copies = copies;
    }

    public boolean borrow() {
        if (copies == 0) {
            return false;
        }
        copies = copies - 1;
        return true;
    }
}
```

- **Fields** (`title`, `copies`) are the data every book carries. `private` means only code inside `Book` can touch
  them; `final` means the title can never change after the book is made.
- The **constructor** (`public Book(...)`, same name as the class, no return type) sets up a new book. `this.title`
  means "this object's title field", as opposed to the parameter `title`.
- `borrow()` is a method **without** `static`: it works on one particular book, using that book's own `copies`.

Notice what is missing: the word `static`. Static methods belong to the class; these methods belong to each
object.

:::picture{name="blueprint-houses"}
A class is a blueprint and objects are the houses built from it: one plan, each house with its own furniture.
:::
:::

:::step{type=try title="Two books, two shelves" file="09-classes-and-objects/Book.java" line="24-29"}
The `main` at the bottom creates two books with `new`:

```java
Book hobbit = new Book("The Hobbit", 2);
Book dune = new Book("Dune", 1);
hobbit.borrow();
```

Run it:

```bash run
cd /workspace/09-classes-and-objects && java Book.java
```

```text
The Hobbit (1 on the shelf)
Dune (1 on the shelf)
true false
```

Borrowing *The Hobbit* changed only the Hobbit: each object keeps its own `copies`. And Dune's second `borrow()`
said `false`: the book protected itself, because the only way to change `copies` is through `borrow()`, and
`borrow()` refuses to go below zero. Try to reach the field from outside, and `javac` stops you:

```text
P.java:1: error: copies has private access in Book
```

That idea, objects guarding their own data behind methods, is called **encapsulation**. It is why a `Book` can never
end up with -3 copies, however badly the rest of the program behaves.
:::

:::step{type=concept title="What new really does"}
Creating an object is a little journey. Press Play:

:::diagram{name="java-object-creation"}
new makes an empty object, the constructor fills its fields, and the variable gets a reference to it.
:::

The variable `hobbit` does not contain the book; it holds a **reference** to it, just like strings (chapter 7) and
arrays (chapter 8). That is why the same rules apply: `Book other = hobbit;` gives the same book a second name.
:::

:::step{type=example title="Worked example: an object that protects itself"}
A wallet that never goes negative:

```java
public class Wallet {
    private int balance;

    public int getBalance() {
        return balance;
    }

    public void spend(int amount) {
        if (amount <= 0 || amount > balance) {
            throw new IllegalArgumentException("cannot spend " + amount);
        }
        balance = balance - amount;
    }
}
```

1. `balance` is `private`, so the outside world can only **read** it through `getBalance()`, a getter.
2. `spend` checks first and **throws** when the amount is bad (chapter 8 showed `throw`). Checking before changing
   anything means a refused call leaves the balance exactly as it was.
3. Only then does it change the field.

Your `BankAccount` task has the same shape, with both `deposit` and `withdraw`.
:::

:::step{type=predict title="Guess first"}
:::question
`a` and `b` are two `new BankAccount("Asha")` objects. After `a.deposit(500)`, what is `b.getBalance()`?
:::
- [ ] `500`
- [x] `0`
- [ ] An error
:::explain
Two `new` calls made two separate objects, each with its own `balance` field.
:::
:::

:::step{type=task task=bank_account title="Your turn: an account that refuses bad amounts"}
Open `BankAccount.java` and finish `deposit` and `withdraw`:

- `deposit(amount)` adds the amount; zero or a negative amount throws an `IllegalArgumentException`.
- `withdraw(amount)` takes the amount out; a zero or negative amount, or more than the balance, throws an
  `IllegalArgumentException` and leaves the balance as it was.

After `deposit(500)` and `withdraw(200)`, `getBalance()` is `300`; `withdraw(1000)` then throws, and the balance stays
`300`.

```bash run
cd /workspace/09-classes-and-objects && java BankAccount.java
```

Then press **Check**.
:::

:::step{type=concept title="Records: classes for plain data" file="09-classes-and-objects/Point.java" line="3"}
Many classes just carry a few values: a point, a date, a shelf location. Writing fields, a constructor and getters
for each is tedious, so modern Java has **records**:

```java
public record Where(String title, int shelf) { }
```

That one line gives you private final fields, a constructor, getters named like the fields (`title()`,
`shelf()`), a readable `toString`, and an `equals` that compares the values:

```text
Where[title=Dune, shelf=3]
Dune 3
true
```

(That is `System.out.println(w)`, `w.title() + " " + w.shelf()`, and
`w.equals(new Where("Dune", 3))`.) A record's values can never change after it is made, which makes records safe to
share. You can still add methods to a record, and that is your next task: open `Point.java`.
:::

:::step{type=task task=point_distance title="Your turn: the distance between two points"}
In `Point.java`, `Point` is a record with `x` and `y`. Make `distanceTo(other)` give back the straight-line distance
to another point, rounded to two decimals.

The distance is the square root of (dx squared + dy squared), where dx and dy are the differences in x and y:
`Math.sqrt(...)` and `Math.pow(d, 2)` (or just `d * d`) do the maths, and chapter 3's `Math.round(x * 100) / 100.0`
rounds.

`new Point(0, 0).distanceTo(new Point(3, 4))` gives `5.0`, and `new Point(1, 1).distanceTo(new Point(2, 2))` gives
`1.41`.

```bash run
cd /workspace/09-classes-and-objects && java Point.java
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What makes a method belong to each object rather than to the class?
:::
- [ ] The word `public`
- [x] It is written without `static`
- [ ] It returns a value
:::explain
A `static` method belongs to the class itself. Without `static`, a method runs on one object and can use its fields.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why make `balance` private?
:::
- [ ] To make the program faster
- [x] So it can only change through methods that check the amount
- [ ] So nobody can ever read it
:::explain
Private fields can still be read through getters; what they block is uncontrolled changes from outside.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `record Where(String title, int shelf)` give you for free?
:::
- [ ] Only a constructor
- [x] Fields, a constructor, getters, toString and equals
- [ ] Setters to change the values
:::explain
Records hold values that never change, so there are no setters: everything else comes for free.
:::
:::

:::step{type=deep-dive title="Go deeper: toString, equals and the null reference"}
**toString.** A plain class prints like `Book@1b6d3586`, just as arrays did. Override `toString()` to give it a
readable form, and `println(book)` uses it automatically. Records do this for you.

**equals and hashCode.** For a class, `a.equals(b)` is the same as `a == b` unless you write your own. If you do,
you must also write `hashCode`, or `HashMap` and `HashSet` break in strange ways: the capstone (chapter 18) has a bug
exactly like this for you to fix.

**null.** A reference variable can hold `null`: no object at all. Calling a method on it throws a
`NullPointerException`, the most famous exception in Java. Its inventor, Tony Hoare, later called the null reference
his "billion-dollar mistake".
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write a class with private fields, a constructor and instance methods, and create objects with `new`.
- Explain `this`, `static` versus instance methods, and references to objects.
- Protect an object's data with encapsulation: check, throw, and only then change.
- Use records for plain values, with their free constructor, getters, toString and equals.

:::photo{src="/lesson-images/java/java-09-notes.webp" alt="Handwritten notes about Java classes: a class is a blueprint, new makes an object, private fields, no static means each object, record for plain data" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 10: interfaces and inheritance, so different kinds of objects can be used the same way.
:::
