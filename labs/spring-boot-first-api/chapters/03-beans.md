:::step{type=story title="Why this chapter"}
Every Spring application is a set of objects that Spring creates and connects for you. Understanding
how that works, beans and dependency injection, explains most of what you will see in Spring code:
the annotations, the constructors, and why you almost never write `new` for these classes.

:::mission
In the `03-beans` folder: turn a class into a bean and inject it, and make two controllers share one object.
:::
:::

:::step{type=concept title="Beans and the container"}
A **bean** is an object that Spring creates and manages. The part of Spring that holds them is the
**container** (in code, the `ApplicationContext`).

A class becomes a bean when it has a component annotation and is found by component scanning:

| annotation | used for |
|---|---|
| `@Component` | any bean |
| `@Service` | business logic |
| `@Repository` | data access |
| `@RestController` | web endpoints |

All four make a bean; the specific ones also document the class's role. By default, Spring creates
**one** instance of each bean (singleton scope) and reuses it everywhere.
:::

:::step{type=concept title="Dependency injection through the constructor"}
A class often needs another one to do its work: a controller needs a service. Instead of creating it
with `new`, the class **declares it in its constructor**, and Spring passes the bean in:

```java
@RestController
public class PriceController {

    private final PriceCalculator calculator;

    public PriceController(PriceCalculator calculator) {
        this.calculator = calculator;
    }
}
```

When Spring creates `PriceController`, it sees the constructor parameter, finds the
`PriceCalculator` bean, and passes it. This is **dependency injection**. With one constructor, no
annotation is needed.

:::diagram{name="di-container"}
The container creates each bean once and passes it to every constructor that asks for it.
:::
:::

:::step{type=example title="Worked example: opening hours, injected"}
A service that needs the current time, and a controller that uses the service:

```java
@Component
public class OpeningHours {
    public boolean isOpen(int hour) {
        return hour >= 8 && hour < 22;
    }
}

@RestController
public class ShopStatusController {
    private final OpeningHours hours;

    public ShopStatusController(OpeningHours hours) {   // 1
        this.hours = hours;                              // 2
    }

    @GetMapping("/open-at/9")
    public boolean openAtNine() {
        return hours.isOpen(9);                          // 3
    }
}
```

1. The constructor declares the dependency.
2. The field is `final`: it is set once and never changes.
3. The method uses the injected bean. Nothing in this class creates an `OpeningHours`.
:::

:::step{type=predict title="Guess first"}
:::question
`PriceController`'s constructor takes a `PriceCalculator`, but `PriceCalculator` has no annotation. What happens at start-up?
:::
- [ ] Spring creates a `PriceCalculator` anyway
- [x] Start-up fails: no bean of type `PriceCalculator` exists
- [ ] The parameter is `null`
:::explain
Spring only injects beans. Without `@Component` or `@Service`, there is no `PriceCalculator` bean, and
the application refuses to start with "required a bean of type ... that could not be found".
:::
:::

:::step{type=task task=price_service title="Warm-up: inject the price calculator"}
In `03-beans`: make `PriceCalculator` a bean (it is a service), and give `PriceController` a
constructor that takes a `PriceCalculator` and stores it in the field.

`GET /tea/price` should then answer `2360` (2000 paise plus 18% GST).
:::

:::step{type=concept title="One bean, shared"}
Because a bean is a single instance, every class that injects it gets **the same object**. That is how
data is shared between parts of an application: two controllers that inject the same `VisitCounter` see
the same count.

Creating it yourself breaks this:

```java
private final VisitCounter counter = new VisitCounter();   // a second, private object
```

That object is not a bean. Spring does not know about it, and no other class will ever see what it
counts.
:::

:::step{type=task task=one_counter title="Share one counter"}
In `03-beans`, `StatsController` injects the `VisitCounter` bean, but `HomeController` creates its own
with `new`, so visits to `/` never show up in `/stats`.

Change `HomeController` to receive the `VisitCounter` in its constructor. After two visits to `/`,
`GET /stats` should show 2 more.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two controllers inject `PriceCalculator`. How many `PriceCalculator` objects exist?
:::
- [x] One, shared by both
- [ ] Two, one per controller
- [ ] One per request
:::explain
Beans are singletons by default: Spring creates one and passes the same object to everyone.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is constructor injection preferred to creating dependencies with `new`?
:::
- [ ] It is faster at run time
- [x] Spring provides the shared, configured bean, and tests can pass in a replacement
- [ ] Java does not allow `new` inside a controller
:::explain
With constructor injection, the class does not decide which object it gets. Spring passes the real bean;
a test can pass a simple fake. That is what makes Spring code easy to test.
:::
:::

:::step{type=deep-dive title="Other scopes, and field injection"}
**Scopes:** besides the default singleton, a bean can be `@Scope("prototype")` (a new instance every
time it is injected) or, in web apps, `@RequestScope` (one per HTTP request). Singletons must therefore
be **thread-safe**: many requests use the same object at once, which is why `VisitCounter` uses an
`AtomicInteger`.

**Field injection:** you will see `@Autowired` on fields in older code. It works, but the dependency is
hidden, the field cannot be `final`, and tests need reflection to set it. Prefer constructors.
:::

:::step{type=recap title="Chapter done"}
- A bean is an object Spring creates and manages; `@Component`, `@Service`, `@Repository` and `@RestController` make one.
- Declare dependencies as constructor parameters; Spring injects the beans.
- A bean is a single, shared instance: objects made with `new` are not beans and are not shared.
:::
