:::step{type=story title="Where we are"}
In the last chapter you watched your app start. Spring scanned your package, found your controllers,
and created them for you. You never wrote `new GreetingController()` anywhere, and yet it worked.

So who created that object? And if your controller needs some other object to do its job, how does it
get one?

That is what this chapter is about. It is the most important idea in Spring, and once it clicks, a lot
of Spring code that looks like magic will suddenly look obvious. We will go slowly.

:::mission
In the `05-beans` folder: give a controller the object it needs, the Spring way, and fix a bug where two
controllers each count visits on their own.
:::
:::

:::step{type=concept title="First, the problem" file="05-beans/src/main/java/com/shop/pricing/PriceCalculator.java" line="4-9"}
Let's start with plain Java, no Spring.

Your shop needs to show prices with GST added. (GST is India's Goods and Services Tax; in this course every price
gets 18%.) Here is a small class for that. It is open on the right: this is the real `PriceCalculator` from your
project. Prices are in paise, so `2000` is Rs 20, and `paise * 18 / 100` is 18% of it in whole paise.

```java
public class PriceCalculator {

    public int withGst(int paise) {
        return paise + paise * 18 / 100;
    }
}
```

And a first try at a controller that uses it (only to read; your project does it differently):

```java
@RestController
public class PriceController {

    private final PriceCalculator calculator = new PriceCalculator();

    @GetMapping("/kulfi/price")
    public int kulfiPrice() {
        return calculator.withGst(2000);
    }
}
```

Read the line with `new` again. The controller creates its own calculator. That works today.
:::

:::step{type=concept title="Why that turns into trouble"}
Look again at `new PriceCalculator()` inside the controller, and think about what happens as the app grows:

- Five controllers need prices, so there are now five separate calculators.
- Next month the calculator needs the GST rate from a settings file. Now every controller that wrote
  `new PriceCalculator()` has to change, and has to know where that settings file is.
- When you want to test the controller with a fake calculator, you cannot: the real one is created
  inside, and you have no way to swap it.

The problem is not the calculator. The problem is that **each class builds the objects it needs**. Keep
that sentence in mind; Spring's answer is the next step.
:::

:::step{type=concept title="Spring's answer: let it build the objects"}
Here is the idea: instead of every class building what it needs, **one place builds the objects, and
hands each class what it asks for.**

In Spring, that one place is called the **container**. You met it in the last chapter without its name:
it is the thing that scanned your package and created your controllers at start-up.

An object that the container creates and looks after has a name: a **bean**. Your controllers are
already beans. That is why you never had to create them.

So now you know two words:

- **container**: the part of Spring that creates objects and keeps them;
- **bean**: an object the container created.

That's it. No more magic than that.
:::

:::step{type=concept title="How a class becomes a bean" file="05-beans/src/main/java/com/shop/pricing/PriceCalculator.java" line="3-4"}
The container does not create every class in your project. It creates a class only when you mark it.
You have already used one mark: `@RestController`.

For a class that is not a controller, like our `PriceCalculator`, the general mark is `@Component`:

```java
@Component
public class PriceCalculator {
    ...
}
```

At start-up, scanning finds this class and the container creates one `PriceCalculator`. Now it is a bean.

You will also see `@Service`. It does the same as `@Component`; the name just tells the reader "this
class holds business logic". A price calculation is business logic, so here you will use `@Service`.

Check yourself: remove `@RestController` from a controller. Does Spring still create it? (No: without
the mark, scanning skips the class.)
:::

:::step{type=concept title="Asking for a bean: the constructor" file="05-beans/src/main/java/com/shop/pricing/PriceController.java" line="11-13"}
Now the second half. `PriceController` needs a `PriceCalculator`. How does it ask the container for one?

It asks by **having a constructor parameter of that type**:

```java
@RestController
public class PriceController {

    private final PriceCalculator calculator;

    public PriceController(PriceCalculator calculator) {
        this.calculator = calculator;
    }
}
```

Let's read it line by line.

`private final PriceCalculator calculator;` is a field to keep the calculator in. There is no `new` on
this line any more. `final` means it is set once and never replaced.

`public PriceController(PriceCalculator calculator)` is the constructor. Its parameter says: "to build
me, you must give me a `PriceCalculator`."

`this.calculator = calculator;` stores what we were given in the field.
:::

:::step{type=concept title="What Spring does with that constructor"}
Now, at start-up, the container wants to create `PriceController`. It looks at the constructor, sees it
needs a `PriceCalculator`, finds the `PriceCalculator` bean it already made, and passes it in.

This has a name too: **dependency injection**. The calculator is a *dependency* of the controller (the
controller depends on it), and the container *injects* it (passes it in). You do not need an annotation
on the constructor; when a class has exactly one constructor, Spring uses it.

:::diagram{name="di-container"}
The container creates each bean once, then passes it to every constructor that asks for it.
:::
:::

:::step{type=concept title="The container has a name: the application context"}
In Spring code and in error messages you will constantly see one more term for the container: the
**application context**. They mean the same thing: the object that holds all your beans.

In fact, `SpringApplication.run` *returns* it. If you ever want to look inside, you can:

```java
ApplicationContext context = SpringApplication.run(ShopApiApplication.class, args);

System.out.println(context.getBeanDefinitionCount() + " beans");
PriceCalculator calc = context.getBean(PriceCalculator.class);   // ask the container directly
```

We tried it on our lab machine with the finished project: this chapter's small app had **158 beans**. Only six are
yours: the main class, `PriceController`, `PriceCalculator`, `HomeController`, `StatsController` and `VisitCounter`.
The rest
belong to Spring Boot: Tomcat's set-up, Jackson's `ObjectMapper` (the object that writes JSON), the part that routes
requests, and many more, all created by auto-configuration.

You will almost never call `getBean` yourself in real code (constructor injection, which you just learned, is the
proper way to get a bean). But it helps to know that the context is a real object, sitting in memory, full
of the objects your application is made of. When an error says "No qualifying bean of type ... in the
application context", it is talking about exactly this.
:::

:::step{type=example title="Worked example: is the shop open?"}
Before you try it, let's walk through one complete example together. (This one is only for reading: it
is not in your project, so you will not find it on the right.) The shop wants a URL that tells whether it
is open at 9 in the morning.

First, the class that knows the opening hours. It is marked, so it becomes a bean:

```java
@Component
public class OpeningHours {

    public boolean isOpen(int hour) {
        return hour >= 8 && hour < 22;
    }
}
```

Then the controller. It asks for `OpeningHours` in its constructor:

```java
@RestController
public class ShopStatusController {

    private final OpeningHours hours;

    public ShopStatusController(OpeningHours hours) {
        this.hours = hours;
    }

    @GetMapping("/open-at/9")
    public boolean openAtNine() {
        return hours.isOpen(9);
    }
}
```

Let's follow what Spring does at start-up, one step at a time.

:::trace{title="What the container does at start-up"}
| step | what Spring does | beans so far |
|---|---|---|
| 1 | scans the package, finds OpeningHours (@Component) and ShopStatusController (@RestController) | none |
| 2 | OpeningHours has no constructor parameters: creates it | OpeningHours |
| 3 | ShopStatusController's constructor needs an OpeningHours | OpeningHours |
| 4 | passes the OpeningHours bean in, creates the controller | OpeningHours, ShopStatusController |
| 5 | a request for /open-at/9 calls openAtNine(), which uses hours | both, unchanged |
:::

Notice what is missing from `ShopStatusController`: the word `new`. The controller says what it needs.
It never says how to make it.
:::

:::step{type=predict title="Guess first"}
:::question
You write `PriceController` with the constructor that takes a `PriceCalculator`, but you forget to put
`@Service` on `PriceCalculator`. You start the app. What happens?
:::
- [ ] Spring creates a `PriceCalculator` anyway, because the constructor needs one
- [x] The app does not start: there is no `PriceCalculator` bean to pass in
- [ ] The app starts, and `calculator` is `null`
:::explain
The container only passes in beans, and without a mark `PriceCalculator` is not a bean. We tried it on our lab
machine; Spring stopped at start-up with:

```text
Parameter 0 of constructor in com.shop.pricing.PriceController required a bean of type
'com.shop.pricing.PriceCalculator' that could not be found.
```

("Parameter 0" is the first parameter; Java counts from 0.) When you see that message, the fix is almost always a
missing `@Component` or `@Service`, or a class outside the scanned packages (chapter 4). It is one of the most
common Spring errors, and now you know it.
:::
:::

:::step{type=try title="See it for yourself" file="05-beans/src/main/java/com/shop/pricing/PriceController.java" line="11"}
Open `05-beans/src/main/java/com/shop/pricing/PriceController.java`. Look at the field:

```java
private PriceCalculator calculator;
```

There is no `new`, and there is no constructor. So nobody ever puts a calculator in this field. It stays `null`
(Java's "no object here"), and the method is written to answer `0` in that case, instead of crashing.

Run the app as it is, and see:

```bash run
cd 05-beans && mvn -q -o package -DskipTests && java -jar target/beans.jar
```

In a second tab, ask for the price of a kulfi:

```bash run
curl -s localhost:8080/kulfi/price; echo
```

You get `0`. The controller is waiting for someone to give it a calculator. That someone is going to be
Spring, and you are about to set it up.
:::

:::step{type=task task=price_service title="Your turn: inject the calculator"}
Two small changes, both in `05-beans/src/main/java/com/shop/pricing/`:

1. In `PriceCalculator.java`, mark the class with `@Service`, so the container creates it.
2. In `PriceController.java`, add a constructor that takes a `PriceCalculator` and stores it in the
   field. Make the field `final` while you are there.

Stop the app (Ctrl+C), build and run it again, and ask for the price. It should now answer `2360`: 2000 paise plus
360 paise of GST (18% of 2000). If the app does not start, read the error's Description: it names the class Spring
could not find.

Usual slips: `@Service` without its import (`org.springframework.stereotype.Service`; the editor offers it), a
constructor with a different name from the class (then it is a method, not a constructor), or assigning the
parameter to itself (`calculator = calculator;` instead of `this.calculator = calculator;`, which leaves the field
`null`).
:::

:::step{type=concept title="How many calculators are there now?"}
Here is a question worth stopping on. Suppose three controllers each ask for a `PriceCalculator` in
their constructors. How many `PriceCalculator` objects does the container make?

**One.** By default, the container creates **one object per bean** and passes that same object to everyone who
asks. Spring calls this the *singleton* scope; a bean's **scope** says how many objects of it exist and how long
each one lives.

This is not a small detail. It means a bean is **shared**. If a bean keeps some data, every class that
was given that bean sees the same data.

And it means `new` is not just old-fashioned, it can be a bug. An object made with `new` is not a bean.
The container does not know it exists, and no other class can ever see it.
:::

:::step{type=example title="Worked example: a bug caused by new" file="05-beans/src/main/java/com/shop/visits/HomeController.java" line="9-11"}
Let's see that bug happen. The shop counts visits with a small bean:

```java
@Component
public class VisitCounter {

    private final AtomicInteger count = new AtomicInteger();

    public int add() {
        return count.incrementAndGet();
    }

    public int count() {
        return count.get();
    }
}
```

(`AtomicInteger` is a number that is safe to change from many requests at once. Because a bean is
shared, many requests use it at the same moment.)

`StatsController` asks for the counter properly, in its constructor, and shows `count()` at `/stats`.
But `HomeController` was written like this:

```java
private final VisitCounter counter = new VisitCounter();
```

:::trace{title="Three visits to /, then /stats"}
| request | HomeController's own counter | the VisitCounter bean | /stats shows |
|---|---|---|---|
| GET / | 1 | 0 | |
| GET / | 2 | 0 | |
| GET / | 3 | 0 | |
| GET /stats | 3 | 0 | 0 |
:::

Three people visited, and the stats page says nobody did. `HomeController` has been counting on its own
private object the whole time. The fix is the same as before: ask for the bean in the constructor.
:::

:::step{type=task task=one_counter title="Your turn: one counter for everyone"}
In `05-beans/src/main/java/com/shop/visits/HomeController.java`, stop creating a `VisitCounter` with `new`.
Ask for it in the constructor instead, like `StatsController` does.

Then build, run and try it: visit `/` twice, and `GET /stats` should go up by 2.

```bash run
curl -s localhost:8080/ > /dev/null; curl -s localhost:8080/ > /dev/null; curl -s localhost:8080/stats; echo
```

(`> /dev/null` throws away the "Welcome" answers, so you only see the stats.) On our lab machine, before the fix,
three visits left `/stats` at `0`; after it, two visits took it from `0` to `2`. Press **Check**.

Usual slip: keeping `= new VisitCounter()` on the field *and* adding the constructor. A `final` field set in two
places does not compile; remove the `new`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two controllers both ask for a `PriceCalculator` in their constructors. How many `PriceCalculator` objects exist?
:::
- [x] One, shared by both
- [ ] Two, one for each controller
- [ ] A new one for every request
:::explain
Right: the container makes one and passes the same object to both. That is why sharing a bean shares its data.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is asking for a dependency in the constructor better than creating it with `new`?
:::
- [ ] It runs faster
- [x] The class gets the shared bean Spring made, and a test can pass in a fake instead
- [ ] Java does not allow `new` inside a controller
:::explain
The class only says *what* it needs, not *how* to make it. In the app, Spring passes the real bean. In a
test (chapter 25), you pass a fake. The class does not change at all.
:::
:::

:::step{type=deep-dive title="Go deeper: other scopes, and @Autowired on fields"}
**Other scopes.** One object per bean is the default, but not the only choice. `@Scope("prototype")`
makes a new object every time the bean is asked for, and `@RequestScope` makes one per HTTP request. You
will rarely need them; the default is right almost always.

**@Autowired on fields.** In older Spring code you will often see this:

```java
@Autowired
private PriceCalculator calculator;
```

It also injects the bean, straight into the field. It works, but the field cannot be `final`, the
dependency is hidden (the constructor no longer tells you what the class needs), and a test cannot pass
in a fake without tricks. That is why the Spring team recommends constructors, the way you just did it.
:::

:::step{type=recap title="What you can do now"}
Look at what you have learned in this chapter:

- You know what a **bean** is: an object the Spring **container** creates and looks after.
- You can make one, with `@Component` or `@Service`.
- You can ask for one, with a **constructor parameter**. That is dependency injection.
- You know that, by default, there is **one shared object per bean**, and why `new` can quietly break that.
- And when you see "required a bean of type ... that could not be found", you know exactly what to fix.

:::photo{src="/lesson-images/spring/spring-05-notes.webp" alt="Sketchnote: Beans. A bean is an object the Spring container creates and looks after. Flow: mark the class with @Component or @Service, scanning finds it, the container creates one, it is passed to constructors. Remember: ask for a bean with a constructor parameter; by default one shared object per bean; an object made with new is not a bean; the not-found error means a missing mark." ai="true"}
One page of notes for this chapter.
:::

Every Spring app you will ever read is built from these few ideas. Next, chapter 6 goes further with
dependency injection: what happens when there is more than one bean that fits, and how to choose.
:::
