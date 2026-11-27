:::step{type=story title="When there is more than one"}
In chapter 5, every time a class asked for a bean, there was exactly one that fitted: one
`PriceCalculator`, one `VisitCounter`. Spring's job was easy.

Real shops are not that tidy. Our Shop API accepts payments by **card** and by **UPI** (Unified Payments
Interface, India's system for paying straight from a bank account with a phone), and next year maybe by wallet
too. Each is its own class, and they all do the same kind of job. So when a class says "I need
something that can take a payment", there are two (or three) beans that fit. Which one should Spring
pass in?

This chapter is about exactly that situation. It is also where dependency injection shows its real power:
your code depends on *what* a thing can do, not on *which* class does it. That is how big codebases stay
changeable.

:::mission
Make the Shop API start again by choosing a main payment gateway, then list every gateway the shop accepts.
:::
:::

:::step{type=concept title="Depend on what it does, not who does it" file="06-dependency-injection/src/main/java/com/shop/payments/PaymentGateway.java" line="3-11"}
Open the project on the right: `PaymentGateway.java` is an **interface**. An interface in Java is a list of methods
with no code inside, a promise: "anything that is a `PaymentGateway` can do *these* things". (A payment
**gateway** is the service that actually moves the money for a shop.)

```java
public interface PaymentGateway {
    String name();
    String pay(int paise);
}
```

Then two classes keep that promise, each in its own way: `CardGateway` and `UpiGateway`. Both say
`implements PaymentGateway`, and both write the code for `name()` and `pay()`. Both are `@Component`, so
both are beans.

Now look at who uses them. `CheckoutService` asks for a `PaymentGateway`, the interface, not for
`CardGateway` or `UpiGateway`:

```java
public CheckoutService(PaymentGateway gateway) { ... }
```

This is a deliberate design choice, and a very common one. `CheckoutService` only needs *something that
can pay*. It does not want to know whether that is a card machine or UPI. If the shop switches payment
provider next year, `CheckoutService` does not change at all: you add a new class that implements the
interface, and Spring injects it. That is what people mean by **loose coupling**: classes connected
through promises (interfaces), not through specific classes.
:::

:::step{type=concept title="How Spring chooses a bean"}
When Spring creates `CheckoutService`, it looks at the constructor parameter's **type**,
`PaymentGateway`, and searches the application context for beans of that type. A bean "is of that type"
if its class is that type, or **implements** it (or extends it).

Three things can happen:

- **Exactly one bean fits.** Spring injects it. This is what you saw in chapter 5.
- **No bean fits.** Spring cannot create the class, so the app stops at start-up:
  `required a bean of type '...PaymentGateway' that could not be found`. Usually a missing `@Component`,
  or a class outside the scanned packages (chapter 4).
- **More than one bean fits.** Spring will not guess. It stops at start-up with
  `required a single bean, but 2 were found`. Guessing could mean charging customers through the wrong
  provider, so refusing to start is the safe choice.

Our project is in the third case right now. You will see the real message in a minute.
:::

:::step{type=try title="See Spring refuse to guess"}
Build and run this chapter's project:

```bash run
cd 06-dependency-injection && mvn -q -o package -DskipTests && java -jar target/dependency-injection.jar
```

The app does not start. Scroll up a little in the output and find this block (it is the most readable part of
any start-up failure). This is what it said on our lab machine, with the long file locations shortened to `...`:

```text
***************************
APPLICATION FAILED TO START
***************************

Description:

Parameter 0 of constructor in com.shop.payments.CheckoutService required a single bean, but 2 were found:
	- cardGateway: defined in URL [...CardGateway.class]
	- upiGateway: defined in URL [...UpiGateway.class]

This may be due to missing parameter name information

Action:

Consider marking one of the beans as @Primary, updating the consumer to accept multiple beans, or using
@Qualifier to identify the bean that should be consumed
```

Read it slowly. It is a very good error message:

- **Which class** could not be created: `CheckoutService`, its constructor's first parameter
  ("Parameter 0"; counting starts at 0).
- **What went wrong:** it needs one bean, and found two.
- **Which two:** `cardGateway` and `upiGateway`. Those are the **bean names**: by default, the class name
  with a small first letter.
- **What you can do:** three options. We will go through all three, and you will use two of them.

And the line "This may be due to missing parameter name information"? Spring has one more way to choose: if the
constructor parameter's *name* matches a bean's name, it uses that bean. Our parameter is called `gateway`, which
matches neither, so this line is only a general hint (we tried renaming the parameter to `upiGateway` on our lab
machine, and the app started with UPI). The deep dive at the end comes back to it.

Whenever a Spring app fails to start, look for this `APPLICATION FAILED TO START` block first.
:::

:::step{type=concept title="Option 1: a default with @Primary"}
The first option is to say "when there is a choice, use **this** one". You put `@Primary` on the bean
that should win:

```java
@Component
@Primary
public class UpiGateway implements PaymentGateway { ... }
```

Now, whenever someone asks for a single `PaymentGateway`, Spring picks `UpiGateway`. The other bean,
`CardGateway`, still exists, and you can still get it when you ask for it specifically (as you will in
a moment).

`@Primary` is the right tool when one bean is the **normal choice** and the others are special cases.
That is our situation: UPI is the shop's main way to pay.
:::

:::step{type=task task=primary_gateway title="Your turn: make UPI the main gateway"}
`UpiGateway.java` has opened at its TODO. Mark this bean as the one Spring should use when there is a
choice. You will also need the import for the annotation: `org.springframework.context.annotation.Primary`.
(In VS Code, the light-bulb quick fix can add the import for you.)

Rebuild and run. The app starts again. Then:

```bash run
curl localhost:8080/pay/5000
```

It should answer `Paid Rs 50 by UPI` (5000 paise is Rs 50). Press **Check**.

Usual slips: `@Primary` on `CardGateway` instead (then the answer says card), or on both gateways. We tried both
on our lab machine: the second fails again, this time without the tidy "APPLICATION FAILED TO START" block, as a
long error whose last `Caused by` line says `more than one 'primary' bean found among candidates: [cardGateway,
upiGateway]`. With a long error, read the last `Caused by` line first.
:::

:::step{type=concept title="Option 2: name the one you want with @Qualifier"}
The second option is for when *one particular class* needs *one particular bean*, whatever the default is.
For example, refunds for card payments must go back through the card gateway:

```java
@Service
public class CardRefundService {

    private final PaymentGateway gateway;

    public CardRefundService(@Qualifier("cardGateway") PaymentGateway gateway) {
        this.gateway = gateway;
    }
}
```

`@Qualifier("cardGateway")` on the parameter says: "not the default, the bean **named** `cardGateway`".
Remember from the error message that bean names are the class name with a small first letter.

So you can use both together: `@Primary` sets the default for everyone, and `@Qualifier` lets a specific
class ask for a specific bean. A qualifier always wins over primary.

A small warning: the qualifier is a string, so a typo (`"cardGatway"`) is only discovered at start-up,
with a "could not be found" error. That is one reason to prefer `@Primary` when it is enough.
:::

:::step{type=concept title="Option 3: take all of them" file="06-dependency-injection/src/main/java/com/shop/payments/GatewayController.java" line="11-17"}
The third option from the error message was "updating the consumer to accept multiple beans". Sometimes
you do not want *one* gateway, you want *all* of them. For example, the checkout page needs to show every
payment method the shop accepts.

You can ask Spring for a **list**:

```java
public GatewayController(List<PaymentGateway> all) {
    this.all = all;
}
```

When a constructor asks for `List<PaymentGateway>`, Spring gathers **every bean of that type** into the
list and passes it in. Two gateways today, so the list has two items. Add a `WalletGateway` class
tomorrow (with `@Component` and `implements PaymentGateway`), and it appears in the list automatically.
`GatewayController` never changes.

This pattern is everywhere in real Spring code: a list of validators that all check an order, a list of
notifiers that all send a message (email, SMS, push)... Each one is its own small class, and the code
that uses them just loops over the list.

`GatewayController` has opened on the right. Right now, `GET /gateways` returns an empty list, with a
TODO.
:::

:::step{type=example title="Worked example: turning the list into names"}
You already know the tool for this from chapter 3: a stream. Here is the same idea with a list of
notifiers, each having a `channel()` method:

```java
private final List<Notifier> notifiers;

public NotificationController(List<Notifier> notifiers) {
    this.notifiers = notifiers;
}

@GetMapping("/channels")
public List<String> channels() {
    return notifiers.stream()               // each notifier, one by one
            .map(Notifier::channel)          // replace each one by its channel name
            .sorted()                        // A to Z
            .toList();
}
```

The new piece is **`.map(...)`**: it transforms each item into something else. `Notifier::channel` is
short for "call `channel()` on each item" (a **method reference**). You could also write it as
`n -> n.channel()`, which means exactly the same.

So a list of notifier *objects* becomes a list of *names*, sorted.
:::

:::step{type=task task=all_gateways title="Your turn: list every gateway"}
In `GatewayController.java`:

1. Add a field for a `List<PaymentGateway>`, and a constructor that takes the list and stores it.
2. Make `GET /gateways` return the **names** of all gateways, sorted A to Z.

Rebuild, run, and try:

```bash run
curl localhost:8080/gateways
```

You should see `["card","upi"]`. Notice that `@Primary` did not change anything here: when you ask for a list, you
get all of them. Press **Check**.

Usual slips: returning `List.of()` still (the TODO's placeholder), returning the gateway objects instead of their
names, or forgetting `.sorted()`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Three beans implement `Notifier`, and none is `@Primary`. A class asks for `List<Notifier>`. What happens?
:::
- [ ] Start-up fails: three beans fit
- [x] It works: the list holds all three
- [ ] The list holds only the first one found
:::explain
"Required a single bean" only applies when you ask for one. A `List` asks for all of them, so any number
is fine, including zero (an empty list).
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`UpiGateway` is `@Primary`. A class asks for `@Qualifier("cardGateway") PaymentGateway gateway`. Which bean does it get?
:::
- [ ] UpiGateway, because it is primary
- [x] CardGateway, because the qualifier names it
- [ ] Start-up fails: the two annotations conflict
:::explain
`@Primary` is only the default. A `@Qualifier` asks for a specific bean by name, and that always wins.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why does `CheckoutService` ask for `PaymentGateway` (the interface) and not `UpiGateway` (the class)?
:::
- [ ] Spring cannot inject classes, only interfaces
- [x] So it works with any gateway, and switching providers does not change it
- [ ] It is faster at run time
:::explain
Spring can inject classes too. Depending on the interface keeps `CheckoutService` independent of any one
provider: loose coupling. It also makes testing easy (chapter 25): a test can pass in a fake gateway.
:::
:::

:::step{type=deep-dive title="Go deeper: injecting by name, Map injection, and @Order"}
**Map injection.** Besides `List<PaymentGateway>`, you can ask for `Map<String, PaymentGateway>`: the keys
are the bean names (`"cardGateway"`, `"upiGateway"`) and the values the beans. Handy to choose a gateway
from a request parameter.

**Order.** The order of beans in an injected `List` is not guaranteed unless you say so. Put `@Order(1)`,
`@Order(2)`... on the classes (lower first) when the order matters, for example for a chain of checks.

**Bean names.** You can give a bean an explicit name: `@Component("upi")`. Then `@Qualifier("upi")`
refers to it. Explicit names survive renaming the class, which is nice for qualifiers.

**Matching by parameter name.** As the error message hinted, when several beans fit and none is primary, Spring
also tries the bean whose name equals the constructor parameter's name: `PaymentGateway upiGateway` gets the
`upiGateway` bean. It works (we tried it), but renaming a parameter then silently changes which bean you get, so
`@Primary` or `@Qualifier` say it more clearly.

**Field injection.** You will see `@Autowired` on fields in older code (`@Autowired private PaymentGateway
gateway;`). It works, but as chapter 5 explained, constructors are better: the dependencies are visible,
the field can be `final`, and tests can pass in fakes without tricks.
:::

:::step{type=recap title="What you can do now"}
You can now handle the most common dependency injection situations:

- Depend on an **interface**, so any implementation can be injected: **loose coupling**.
- Spring injects by **type**: one fitting bean is injected; none stops the start-up; more than one stops it too,
  unless you say which one. Look for **APPLICATION FAILED TO START**, or the last `Caused by` line.
- **`@Primary`** marks the default bean when several fit.
- **`@Qualifier("beanName")`** asks for one specific bean; it wins over `@Primary`. Bean names are the
  class name with a small first letter.
- **`List<Type>`** in a constructor gets **all** the beans of that type; add a class, and it joins the list.
- `.map(...)` in a stream turns each item into something else.

:::photo{src="/lesson-images/spring/spring-06-notes.webp" alt="Sketchnote: Dependency injection with several beans. Spring injects by type; no fitting bean fails the start-up, and with two you must choose. Flow: ask for an interface, Spring finds the beans of that type, one wins or a list gets all. Remember: @Primary sets the default; @Qualifier names one and wins over @Primary; List gets every bean; read APPLICATION FAILED TO START first." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 7 is about configuration: settings files, YAML, typed settings classes, and different
settings for development and production with profiles.
:::
