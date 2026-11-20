:::step{type=story title="Why interfaces"}
A delivery app handles bikes, scooters and vans. Each moves in its own way, but the app only needs to
know one thing about all of them: "how long will you take?". Java's **interfaces** let you write code
for "anything that can do this", without caring what exactly it is.

:::mission
In `shapes/`, give rectangles and circles an `area()` method, then add up the area of any mix of shapes.
:::
:::

:::step{type=concept title="A promise, written down"}
Picture a power socket. Any device with the right plug can use it: a lamp, a phone charger, a kettle.
The socket does not care what the device is, only that it fits the plug.

An **interface** is that socket: a list of methods a class **promises** to have.

```java
public interface Shape {
    double area();
}
```

This says: "anything that is a `Shape` can tell you its area". It does not say how; each shape decides
that for itself.

:::picture{name="plug-socket"}
Anything with the right plug fits the socket.
:::
:::

:::step{type=concept title="Keeping the promise: implements"}
A class signs the promise with `implements`, and must then provide every method in the list:

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

`@Override` tells Java "this method fills in a promise", so a typo in the name becomes a compile error
instead of a silent bug.
:::

:::step{type=concept title="One list, many kinds of shapes"}
Because every shape keeps the same promise, you can put different shapes in one list and treat them
alike:

```java
List<Shape> shapes = List.of(new Square(2), new Circle(1));
for (Shape s : shapes) {
    System.out.println(s.area());   // each answers in its own way
}
```

The loop calls `area()` without knowing which kind each shape is; Java runs the right version for each.
This is called **polymorphism** ("many forms").
:::

:::step{type=example title="Worked example: total perimeter"}
A method that works for every shape that has a perimeter:

```java
public interface HasPerimeter {
    double perimeter();
}

public static double totalPerimeter(List<HasPerimeter> items) {
    double total = 0;
    for (HasPerimeter p : items) {
        total += p.perimeter();
    }
    return total;
}
```

The method never mentions squares or circles. Next month someone adds triangles, and this method works
for them with no changes. `totalArea` is the same idea with `area()`.
:::

:::step{type=predict title="Guess first"}
:::question
A class says `implements Shape` but has no `area()` method. What happens?
:::
- [ ] It runs, and `area()` returns 0
- [x] It does not compile
- [ ] It runs until something calls `area()`
- [ ] Java writes `area()` for you
:::explain
An interface is a promise the compiler checks. A class that `implements Shape` without `area()` breaks
the promise, so it does not compile. You find out at once, not when a customer clicks a button.
:::
:::

:::step{type=try title="Many shapes, one loop"}
```bash run
cat > /tmp/Shapes.java <<'JAVA'
import java.util.List;

public class Shapes {
    interface Shape { double area(); }
    record Square(double side) implements Shape { public double area() { return side * side; } }
    record Strip(double w, double h) implements Shape { public double area() { return w * h; } }

    public static void main(String[] args) {
        for (Shape s : List.of(new Square(2), new Strip(1, 5))) {
            System.out.println(s + " has area " + s.area());
        }
    }
}
JAVA
java /tmp/Shapes.java
```
:::

:::step{type=task task=areas title="Warm-up: each shape's area"}
In `shapes/Rect.java` and `shapes/Circle.java`, make `area()` return the right value:

- `new Rect(3, 4).area()` returns `12.0` (width times height)
- `new Circle(2).area()` returns about `12.566` (`Math.PI` times the radius squared)
:::

:::step{type=task task=total_area title="The total area"}
In `shapes/Shapes.java`, make `totalArea(shapes)` add up the areas of any list of shapes, **rounded to 2
decimals**.

- `totalArea(List.of(new Rect(3, 4), new Circle(1)))` returns `15.14`
- `totalArea(List.of())` returns `0.0`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does an interface contain?
:::
- [ ] Fields with values
- [x] A list of methods a class promises to have
- [ ] Objects
- [ ] A main method
:::explain
An interface lists methods (the promise); classes that `implement` it provide the code.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`List<Shape> shapes` holds a `Rect` and a `Circle`. Which `area()` runs for each?
:::
- [ ] Always Rect's
- [ ] The interface's
- [x] Each object's own: Rect's for the rectangle, Circle's for the circle
- [ ] None: it does not compile
:::explain
Java looks at the actual object and runs its own method. That is polymorphism.
:::
:::

:::step{type=deep-dive title="Inheritance, and why interfaces are usually preferred"}
A class can also **extend** another class and inherit its fields and methods: `class Savings extends
BankAccount`. It is powerful but couples the classes tightly: change the parent, and every child may
break. Experienced Java developers prefer interfaces plus small classes that use each other
("composition over inheritance").

Java allows extending only one class, but implementing many interfaces. Since Java 8, interfaces may
also carry `default` methods with code, which is how `List` gained methods like `forEach` without
breaking every list ever written.
:::

:::step{type=recap}
- An interface is a written promise: a list of methods.
- A class `implements` it and provides each method; `@Override` catches typos.
- Code written for the interface works for every class that keeps the promise (polymorphism).
- Prefer small interfaces over deep inheritance.
:::
