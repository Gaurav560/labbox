:::step{type=story title="Opening the black box"}
Since chapter 0 you have heard "auto-configuration sets that up for you" many times. Add the web starter,
and Tomcat and JSON appear. Add the Actuator, and a health endpoint appears. You never wrote a line of
code for any of it.

That can feel like magic, and magic is uncomfortable when something goes wrong. So in this chapter we
open the box. You will see that auto-configuration is not magic at all: it is ordinary Spring
configuration, written by the Spring Boot team, that switches itself on and off based on simple
**conditions**. You will read Spring Boot's own report of what it decided and why, and then you will
change a small auto-configuration yourself, written exactly the way Spring Boot writes its own.

After this chapter, "how does Spring Boot know to do that?" will always have an answer you can look up.

:::mission
Make ShopKit's default greeter step aside when the app has its own, and make the festival banner appear
only when a setting switches it on.
:::
:::

:::step{type=concept title="First: beans you define yourself, with @Bean" file="08-auto-configuration/src/main/java/com/shop/ShopConfig.java" line="8-16"}
Until now, every bean came from a class marked `@Component` (or `@Service`, `@RestController`). There is a
second way to make a bean, and auto-configuration is built on it, so let's learn it first.

`ShopConfig.java` has opened on the right:

```java
@Configuration
public class ShopConfig {

    @Bean
    public Greeter shopGreeter() {
        return new Greeter("Welcome to the Shop API");
    }
}
```

- **`@Configuration`** marks a class whose job is to *define beans*.
- **`@Bean`** on a method says: "call this method at start-up, and put what it returns into the
  application context as a bean". The method name, `shopGreeter`, becomes the bean's name.

Why not just put `@Component` on `Greeter`? Because sometimes you **cannot**: `Greeter` belongs to a
library (here, a small library called ShopKit, in the package `com.shopkit`), and you cannot edit
library code. Or you need to create the object in a special way, with a specific message, or with
settings. `@Bean` lets you create *any* object exactly how you want and hand it to Spring.

So there are two ways to make beans: `@Component` on **your own classes**, and `@Bean` methods for
**anything else**.
:::

:::step{type=concept title="Auto-configuration is just @Bean methods with conditions" file="08-auto-configuration/src/main/java/com/shopkit/greeting/GreetingAutoConfiguration.java"}
Now open ShopKit's `GreetingAutoConfiguration.java`, on the right. It looks almost the same as
`ShopConfig`:

```java
@AutoConfiguration
public class GreetingAutoConfiguration {

    @Bean
    public Greeter defaultGreeter() { return new Greeter("Hello from ShopKit"); }

    @Bean
    public FestivalBanner festivalBanner() { return new FestivalBanner("Diwali sale: 20% off sweets!"); }
}
```

It is a configuration class with `@Bean` methods. The only new thing is `@AutoConfiguration` instead of
`@Configuration`. That is all an auto-configuration is.

**Every one of Spring Boot's own auto-configurations is written like this.** Somewhere inside the
`spring-boot-autoconfigure` jar there is a `JacksonAutoConfiguration` class with a `@Bean` method that
creates the JSON `ObjectMapper`, a `DispatcherServletAutoConfiguration` that creates the part that routes
your requests, and about 150 more. They are ordinary Java code. You could read them.

Two questions remain: how does Spring find them, and how do they decide whether to apply? The next two
steps answer both.
:::

:::step{type=concept title="How Spring finds auto-configurations"}
Look at ShopKit's package: `com.shopkit.greeting`. That is **not** under `com.shop`. Component scanning
(chapter 4) would never find it. That is on purpose: a library should not depend on where *your* main
class happens to be.

Instead, a library lists its auto-configurations in a special file, inside its jar:

```text
src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

You can find this file in the project's file tree. It contains one line per auto-configuration class:

```text
com.shopkit.greeting.GreetingAutoConfiguration
```

At start-up, `@EnableAutoConfiguration` (one of the three annotations hidden in `@SpringBootApplication`)
reads **this file from every jar on the classpath**. Spring Boot's own `spring-boot-autoconfigure` jar has
the same file, with its long list. That is the whole discovery mechanism: libraries announce their
auto-configurations in a file; Spring Boot reads all those files.

And there is one more important detail: auto-configurations are processed **after** your own
configuration. Spring first registers everything from your code, *then* looks at the auto-configurations.
Remember that; it is exactly what makes the next idea work.
:::

:::step{type=concept title="Conditions: apply only when it makes sense"}
If every auto-configuration always applied, every app would contain a database connection, a message
queue, a cache and a hundred things it never asked for. So every auto-configuration is guarded by
**conditions**: annotations that say *when* a bean (or a whole configuration class) should be created.
The most important ones:

- **`@ConditionalOnClass(SomeClass.class)`**: only if that class is on the classpath. This is how *adding
  a starter* switches a feature on. `JacksonAutoConfiguration` is conditional on Jackson's `ObjectMapper`
  class: no Jackson library, no JSON setup.
- **`@ConditionalOnMissingBean`**: only if the app has **not** already defined a bean of this type. This
  is how *your* beans win over Spring Boot's defaults. The default **backs off** when you provide your own.
- **`@ConditionalOnProperty(...)`**: only if a setting has a certain value. This is how a property can
  switch a whole feature on or off.

Now the "processed after your configuration" detail pays off. Because your beans are registered first, by
the time Spring evaluates `@ConditionalOnMissingBean` on a default, it already knows whether you defined
your own. If you did, the default is simply never created.

This is Spring Boot's core design idea, and it is worth saying slowly: **sensible defaults, that step
aside the moment you define your own.** You get everything for free, and you can replace any piece.
:::

:::step{type=try title="See the problem: two greeters"}
Right now ShopKit's `defaultGreeter` has **no condition**. And the app defines its own `shopGreeter`. Build
and run:

```bash run
cd 08-auto-configuration && mvn -q -o package -DskipTests && java -jar target/auto-configuration.jar
```

The app fails to start, with an error you know from chapter 6:

```text
Parameter 0 of constructor in com.shop.GreetingController required a single bean, but 2 were found:
	- shopGreeter: defined by method 'shopGreeter' in class path resource [com/shop/ShopConfig.class]
	- defaultGreeter: defined by method 'defaultGreeter' in class path resource [com/shopkit/greeting/GreetingAutoConfiguration.class]
```

Two `Greeter` beans: the shop's and ShopKit's. In chapter 6 you would have reached for `@Primary`. But think
about whose problem this really is. The shop did nothing wrong: it just wanted its own greeter. It is the
**library's** default that should have stepped aside. A good auto-configuration never forces the app to
fight it.
:::

:::step{type=task task=backs_off title="Your turn: make the default back off"}
In `GreetingAutoConfiguration.java`, make `defaultGreeter` apply only when the application has not
defined a `Greeter` bean of its own. You need one annotation on that method, and its import:
`org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean`.

With no arguments, it uses the method's return type (`Greeter`), which is exactly what you want.

Rebuild and run. The app starts. Then:

```bash run
curl localhost:8080/greeting
```

It should answer `Welcome to the Shop API`: the shop's own greeter. The check also confirms that in an
app *without* its own greeter, ShopKit still provides `Hello from ShopKit`. Press **Check**.
:::

:::step{type=example title="Reading Spring Boot's own decisions"}
Spring Boot can tell you every decision it made. Start the app with `--debug` at the end:

```bash run
java -jar target/auto-configuration.jar --debug
```

A long **CONDITIONS EVALUATION REPORT** scrolls past, before `Started`. It has two big sections:
**Positive matches** (applied) and **Negative matches** (not applied), each with the reason. Scroll up and
find these entries (here from the finished project):

```text
Positive matches:
   DispatcherServletAutoConfiguration matched:
      - @ConditionalOnClass found required class 'org.springframework.web.servlet.DispatcherServlet'
   JacksonAutoConfiguration matched:
      - @ConditionalOnClass found required class 'com.fasterxml.jackson.databind.ObjectMapper'

Negative matches:
   GreetingAutoConfiguration#defaultGreeter:
      Did not match:
         - @ConditionalOnMissingBean (types: com.shopkit.greeting.Greeter) found beans of type
           'com.shopkit.greeting.Greeter' shopGreeter
```

Read them like sentences:

- "The web routing was set up, because the `DispatcherServlet` class is on the classpath": that is the
  web starter switching on the web layer.
- "JSON was set up, because Jackson's `ObjectMapper` class is on the classpath."
- "ShopKit's default greeter was *not* created, because a `Greeter` bean named `shopGreeter` already
  exists": your fix, in Spring Boot's own words.

Whenever you wonder "why did Spring Boot set up X?" or "why didn't it?", this report has the answer. Stop
the app with Ctrl+C.
:::

:::step{type=concept title="Switching a feature with a setting" file="08-auto-configuration/src/main/java/com/shopkit/greeting/GreetingAutoConfiguration.java"}
The second ShopKit bean is a `FestivalBanner`. A banner like "Diwali sale" should only exist **during a
festival**. So the shop wants to switch it on and off with a setting, without changing code:

```properties
shop.festival.enabled=true
```

That is exactly what `@ConditionalOnProperty` does. Here it is on a different bean, a night-time discount
that only exists when `shop.night-discount.enabled` is `true`:

```java
@Bean
@ConditionalOnProperty(prefix = "shop.night-discount", name = "enabled", havingValue = "true")
public NightDiscount nightDiscount() {
    return new NightDiscount(10);
}
```

The three parts together name the setting and the value: the **prefix** plus the **name** gives the
property (`shop.night-discount.enabled`), and **havingValue** is the value it must have. If the property is
missing, or has any other value, the bean is simply not created.

How does the rest of the app cope with a bean that may not exist? Look at `GreetingController`: it asks for
an `ObjectProvider<FestivalBanner>` instead of a `FestivalBanner`. An **ObjectProvider** means "maybe a
bean": `getIfAvailable()` returns the bean, or `null` if there is none. So `/banner` answers either the
banner text or `No festival today`.

Spring Boot uses this constantly. For example, `management.endpoints.web.exposure.include` (chapter 27)
decides which Actuator endpoints exist, through conditions just like this one.
:::

:::step{type=task task=on_property title="Your turn: a festival switch"}
Two changes:

1. In `GreetingAutoConfiguration.java`, make `festivalBanner` apply only when the property
   `shop.festival.enabled` has the value `true`. (Import:
   `org.springframework.boot.autoconfigure.condition.ConditionalOnProperty`.)
2. In this project's `src/main/resources/application.properties`, switch the festival on for the shop.

Rebuild, run, and try:

```bash run
curl localhost:8080/banner
```

It shows the Diwali banner. Now stop the app and start it with the festival switched off from the
command line (remember chapter 7: the command line beats the file):

```bash run
java -jar target/auto-configuration.jar --shop.festival.enabled=false
```

`curl localhost:8080/banner` now answers `No festival today`. One setting, and a bean exists or does not.
Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
You add `spring-boot-starter-data-jpa` to the pom, and suddenly the app wants a database at start-up. Which kind of condition switched that on?
:::
- [ ] @ConditionalOnProperty
- [x] @ConditionalOnClass: the JPA classes are now on the classpath
- [ ] @ConditionalOnMissingBean
:::explain
Adding a starter puts new classes on the classpath, and auto-configurations conditional on those classes
apply. That is how "add a dependency, get a feature" works.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Spring Boot auto-configures an `ObjectMapper` (for JSON), and you define your own `@Bean ObjectMapper` in a `@Configuration` class. What happens?
:::
- [ ] Start-up fails: two ObjectMapper beans
- [x] Yours is used: Spring Boot's default backs off
- [ ] Spring Boot's is used: auto-configuration always wins
:::explain
Spring Boot's `ObjectMapper` bean is `@ConditionalOnMissingBean`. Your configuration is processed first, so
by the time the condition is checked, your bean exists, and the default is never created.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
How does Spring Boot find auto-configuration classes that are not under your main class's package?
:::
- [ ] Component scanning searches every package
- [x] Each jar lists them in META-INF/spring/...AutoConfiguration.imports, and Spring Boot reads those files
- [ ] They must be registered with @Import in your main class
:::explain
Component scanning only covers your own packages. Libraries announce their auto-configurations in that
file, and `@EnableAutoConfiguration` reads it from every jar on the classpath.
:::
:::

:::step{type=deep-dive title="Go deeper: writing your own starter, and excluding auto-configurations"}
**Your own starter.** Companies often write internal starters: a jar with an auto-configuration (for the
company's logging, security or messaging setup) and its `.imports` file. Every team adds one dependency and
gets the company's standard setup, with conditions so each team can still override pieces. ShopKit in this
chapter is a tiny example of exactly that.

**Excluding an auto-configuration.** Very occasionally you want Spring Boot to *not* apply one at all:
`@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)`, or the property
`spring.autoconfigure.exclude`. Usually, defining your own bean (so the default backs off) is the better
fix.

**More conditions.** `@ConditionalOnBean` (only if some other bean exists), `@ConditionalOnWebApplication`,
`@ConditionalOnResource`, `@ConditionalOnExpression`... They all follow the same idea: a bean is created
only when it makes sense.
:::

:::step{type=recap title="What you can do now"}
Auto-configuration is no longer magic. You know:

- **`@Bean`** methods in a **`@Configuration`** class create beans for objects you cannot (or do not want
  to) mark with `@Component`. The method name is the bean name.
- An **auto-configuration** is a configuration class (`@AutoConfiguration`) with `@Bean` methods, listed in
  `META-INF/spring/...AutoConfiguration.imports` in its jar. Spring Boot's own work exactly like that.
- Auto-configurations run **after** your configuration, and are guarded by **conditions**:
  `@ConditionalOnClass` (a library is present), `@ConditionalOnMissingBean` (you did not define your own:
  the default **backs off**), `@ConditionalOnProperty` (a setting switches it).
- **`ObjectProvider<T>`** injects a bean that may not exist.
- `--debug` prints the **conditions evaluation report**: every decision, with its reason.

:::photo{src="/lesson-images/spring/spring-08-notes.webp" alt="Handwritten notes about Auto-configuration: @Bean in a @Configuration class, yours first, auto-config after, @ConditionalOnMissingBean, ObjectProvider: maybe a bean, --debug shows every decision" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 9 follows a bean through its whole life: when it is created, how it can prepare itself, how
many copies exist, and what happens when the app shuts down.
:::
