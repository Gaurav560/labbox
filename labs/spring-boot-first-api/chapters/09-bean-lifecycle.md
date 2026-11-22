:::step{type=story title="A bean is born, lives, and goes away"}
You know what a bean is, how Spring creates it and passes it to the classes that need it. But a bean has a
whole life around that moment. *When* exactly is it created? Can it prepare itself before the first
request arrives, like loading a price list? Is there really only one of it, and what if you need a fresh
one each time? And when you press Ctrl+C, does it get a chance to clean up?

These questions sound academic until you meet the bugs they cause. A price list that is empty because
nobody loaded it. A customer's receipt that shows the *previous* customer's items. You will meet both in
this chapter's project, and fix both.

:::mission
Load the price catalogue once at start-up, and give every customer their own fresh receipt.
:::
:::

:::step{type=concept title="The life of a singleton bean"}
Most beans you write are **singletons**: Spring creates exactly one, at start-up, and keeps it until the
app shuts down. Press **▶ Play** to follow one bean, the shop's `PriceCatalog`, through its whole life.

:::diagram{name="bean-lifecycle"}
Created once at start-up, prepared, used by every request, cleaned up at shutdown.
:::

Two moments are yours to hook into:

- **Right after creation** (step 3): a method marked **`@PostConstruct`** runs once, after the constructor
  and after the dependencies are in place. It is the place to *prepare* the bean: load data, warm a cache,
  check a setting.
- **Right before destruction** (step 5): a method marked **`@PreDestroy`** runs once, when the application
  shuts down. It is the place to *clean up*: close files, finish writing, say goodbye to other systems.

Both annotations come from `jakarta.annotation`, a standard Java package that Spring understands.
:::

:::step{type=concept title="The catalogue that is never loaded" file="09-bean-lifecycle/src/main/java/com/shop/prices/PriceCatalog.java" line="22-36"}
Look at `PriceCatalog` on the right. It holds every product's price in a `Map` (a lookup table: product
code to price). The `load()` method reads them from a file, `prices.csv`, in `src/main/resources`:

```text
sku,price_paise
LAS-1,2000
SAM-1,1800
COF-1,3000
```

Reading a file is slow compared to looking in a map, so the plan is: read the file **once**, at start-up,
and then answer every request from memory.

The code to read the file is there. But look for who calls `load()`. Nobody does. The constructor does not,
no controller does, and Spring does not know it should. So the map stays empty forever, and every price
lookup answers 404.

You *could* call `load()` from the constructor. It would work here, but it is a habit worth avoiding: a
constructor should only **build** the object (store what it is given), and preparing work belongs after
the object is fully built. With field injection or `@Value` fields, for example, those fields are still
empty inside the constructor; by the time `@PostConstruct` runs, everything has been injected.
`@PostConstruct` is the clean, standard place for "prepare yourself".
:::

:::step{type=try title="See the empty catalogue"}
Build and run, and ask for a price:

```bash run
cd 09-bean-lifecycle && mvn -q -o package -DskipTests && java -jar target/bean-lifecycle.jar
```

In a second terminal:

```bash run
curl -i localhost:8080/prices/LAS-1; echo; curl localhost:8080/prices/count
```

`404`, and a count of `0`. Look at the start-up log in Terminal 1 too: there is no `Loaded ... prices`
line, because `load()` never ran. Stop the app with Ctrl+C.
:::

:::step{type=task task=post_construct title="Your turn: load the prices at start-up"}
In `PriceCatalog.java`, mark `load()` so that Spring calls it once, right after creating the bean. The
annotation is `@PostConstruct`, and its import is `jakarta.annotation.PostConstruct`.

Rebuild and run. This time, the start-up log has a new line just before `Started`:

```text
INFO ... com.shop.prices.PriceCatalog : Loaded 3 prices
```

Then `curl localhost:8080/prices/LAS-1` answers `2000`. Press **Check**.
:::

:::step{type=concept title="Scopes: how many copies?"}
The **scope** of a bean decides how many copies Spring makes, and when.

- **singleton** (the default): **one** object for the whole application. Created at start-up, shared by
  everyone who asks. Every bean you have written so far is a singleton.
- **prototype**: a **new** object **every time** someone asks Spring for one.
- **request** (web apps only): one object per HTTP request.
- **session** (web apps only): one object per user session.

Singletons are right for almost everything: controllers, services, repositories, catalogues. Those are
objects that *do* things, and they do not need to remember anything about one particular customer. That
is also why sharing one copy is safe.

But a singleton is **shared by every request at the same time**. Many customers may be using the same
object at the same moment, on different threads. So if a singleton **keeps state** (fields that change
while handling a request), customers start seeing each other's data. That is the classic singleton bug,
and this chapter's project has it.
:::

:::step{type=example title="The receipt bug" file="09-bean-lifecycle/src/main/java/com/shop/receipts/ReceiptPrinter.java" line="9-20"}
`ReceiptPrinter`, on the right, collects the lines of one customer's receipt in a list. It **keeps
state**: the `lines` list grows as items are added.

`ReceiptController` asks Spring for a `ReceiptPrinter` for each customer:

```java
ReceiptPrinter receipt = receipts.getObject();   // "Spring, give me a ReceiptPrinter"
receipt.add("1 x " + item);
return receipt.lines();
```

(`receipts` is an `ObjectProvider<ReceiptPrinter>`, which you met in chapter 8: a way to ask Spring for a
bean *at the moment you need it*, instead of once in the constructor.)

But `ReceiptPrinter` is a singleton. So `getObject()` returns **the same object** every time. Follow two
customers:

:::trace{title="Two customers, one shared ReceiptPrinter"}
| request | what getObject() returns | lines in the receipt | answer |
|---|---|---|---|
| Asha buys lassi | the one ReceiptPrinter | [1 x lassi] | [1 x lassi] |
| Ravi buys a samosa | the same ReceiptPrinter | [1 x lassi, 1 x samosa] | [1 x lassi, 1 x samosa] |
| Meera buys coffee | the same ReceiptPrinter | [1 x lassi, 1 x samosa, 1 x coffee] | all three |
:::

Ravi's receipt shows Asha's lassi. Meera's shows everything. In a real shop, that is a privacy problem
and a billing problem at once.
:::

:::step{type=try title="See the bug for yourself"}
Run the app and play two customers:

```bash run
mvn -q -o package -DskipTests && java -jar target/bean-lifecycle.jar
```

```bash run
curl localhost:8080/receipt/lassi; echo; curl localhost:8080/receipt/samosa; echo
```

The second answer contains the lassi. Stop the app.
:::

:::step{type=task task=prototype_scope title="Your turn: a fresh receipt for every customer"}
In `ReceiptPrinter.java`, change the bean's scope so Spring creates a **new** `ReceiptPrinter` every time
one is asked for. The annotation is `@Scope("prototype")`, from `org.springframework.context.annotation.Scope`.

Rebuild, run, and play the two customers again: the second receipt now holds only the samosa. Press **Check**.
:::

:::step{type=concept title="A trap: a prototype inside a singleton"}
Here is a subtle point that catches experienced developers too. Why did `ReceiptController` use an
`ObjectProvider` instead of simply asking for a `ReceiptPrinter` in its constructor?

```java
public ReceiptController(ReceiptPrinter receipt) { this.receipt = receipt; }   // looks fine...
```

`ReceiptController` is a singleton: Spring creates it **once**. So its constructor runs **once**, and asks
for a `ReceiptPrinter` **once**. Even with prototype scope, it gets exactly one new receipt, at start-up,
and then reuses it for every request. Back to the bug.

Prototype scope means "new object *each time someone asks*". A constructor only asks one time. To get a
fresh one per customer, you have to **ask again for each customer**, and that is what
`ObjectProvider.getObject()` does.

In real projects, though, the more common fix is simpler still: do not keep per-customer state in a bean at
all. Create a plain object with `new` inside the method (`var receipt = new Receipt();`), use it, return
it. Beans are for the shared machinery; data that belongs to one request lives in local variables.
:::

:::step{type=example title="Cleaning up with @PreDestroy" file="09-bean-lifecycle/src/main/java/com/shop/ShutdownNotice.java" line="9-18"}
The last moment in a bean's life is shutdown. `ShutdownNotice`, on the right, has a method marked
`@PreDestroy`:

```java
@PreDestroy
public void goodbye() {
    log.info("Shop API is shutting down: closing the till for today");
}
```

Run the app, then stop it with **Ctrl+C**, and read the last lines of the log:

```text
INFO ... o.s.b.w.e.tomcat.GracefulShutdown : Commencing graceful shutdown. Waiting for active requests to complete
INFO ... o.s.b.w.e.tomcat.GracefulShutdown : Graceful shutdown complete
INFO ... com.shop.ShutdownNotice           : Shop API is shutting down: closing the till for today
```

First, Spring Boot stops accepting new requests and lets the ones in progress finish (**graceful
shutdown**). Then it closes the application context, calling every `@PreDestroy` method. Here we only log
a message, but in real apps this is where you flush data to disk or close connections to other systems.

(Ctrl+C asks the app to stop politely. If a process is killed brutally, for example by a power cut,
`@PreDestroy` never runs. So never rely on it for anything that *must* happen.)
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In what order does Spring prepare a singleton bean?
:::
- [ ] @PostConstruct, then the constructor
- [x] The constructor (with its dependencies), then @PostConstruct
- [ ] @PostConstruct runs before every request
:::explain
The object must exist first: the constructor runs with the injected dependencies, then `@PostConstruct`
runs once on the finished object. It never runs again for that bean.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A singleton `CartService` has a field `List<String> items` that each request adds to. What happens under load?
:::
- [ ] Each request gets its own list
- [x] All requests share one list: customers see each other's items, and it can even break with many threads
- [ ] Spring makes a copy of the field for each thread
:::explain
One object, shared by every request, at the same time. Per-request data belongs in local variables, in the
request itself, or in a database; never in a singleton's fields.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`ReceiptPrinter` is a prototype, and a singleton controller takes it in its constructor. How many receipts are created while the app serves 100 customers?
:::
- [ ] 100
- [x] 1, created when the controller was created
- [ ] 0
:::explain
The constructor asks once, so Spring creates one prototype, once. To get a new one per customer, ask each
time with `ObjectProvider.getObject()`, or simply create a plain object with `new` in the method.
:::
:::

:::step{type=deep-dive title="Go deeper: lazy beans, startup order, and ApplicationRunner"}
**Lazy beans.** `@Lazy` on a bean delays creating it until the first time someone uses it, instead of at
start-up. It makes start-up faster, but hides problems until later, so use it sparingly.

**Order.** Spring creates beans in dependency order (a bean's dependencies first). If one bean must be
created after another *without* depending on it, `@DependsOn("otherBean")` forces the order. Needing it is
often a sign the design could be simpler.

**Running code after start-up.** `@PostConstruct` prepares *one bean*. To run something once the *whole*
app is ready (for example, print a summary, or load demo data that needs several beans), implement
`ApplicationRunner` (or `CommandLineRunner`) in a bean: its `run` method is called right before
`Started ShopApiApplication`.
:::

:::step{type=recap title="What you can do now"}
You now know a bean's whole life:

- A singleton bean is created once at start-up (dependencies first), used by every request, and destroyed
  when the app shuts down.
- **`@PostConstruct`**: runs once, after the constructor and injection. Prepare the bean there.
- **`@PreDestroy`**: runs once, at shutdown, after graceful shutdown. Clean up there (but never rely on it
  for anything critical).
- **Scopes**: `singleton` (default, one shared object), `prototype` (a new one each time it is asked for),
  `request` and `session` for web apps.
- A singleton is **shared by every request at once**: never keep per-request state in its fields.
- A prototype injected through a singleton's constructor is created **once**; ask each time with
  `ObjectProvider`, or use plain objects for per-request data.

That completes Part 1, the foundations. You now understand what Spring is doing under every API you will
write. Part 2 begins with chapter 10: exactly what happens to one HTTP request inside Spring, from the
moment it arrives to the moment the JSON goes back.
:::
