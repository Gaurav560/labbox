:::step{type=story title="What happens in that one second"}
Every time you have started the Shop API, about one second passed between `java -jar` and
`Started ShopApiApplication`. In that second, Spring did a surprising amount of work: it found your
controller (without you ever mentioning it anywhere), set up a web server, prepared JSON, and wired
everything together.

Most beginners treat that second as a black box. That is why, when something goes wrong at start-up (and
it will), the error messages feel impossible. This chapter opens the box. We will follow the start-up step
by step, read the real log line by line, and learn the two rules behind most "my controller is not
found" and "my setting is not read" problems.

:::mission
Understand Spring Boot's start-up, make Spring find a controller it cannot see, and read a setting from
application.properties.
:::
:::

:::step{type=concept title="It all starts in main" file="04-app-startup/src/main/java/com/shop/ShopApiApplication.java" line="10"}
Every Java program begins at a `main` method, and the JVM (the Java virtual machine) runs it. Ours has
one line, highlighted on the right:

```java
SpringApplication.run(ShopApiApplication.class, args);
```

Two arguments go in:

- `ShopApiApplication.class`: the class to start from. Spring reads its annotations to learn how to
  start, and uses its **package** (`com.shop`) as the place to look for your code.
- `args`: whatever was typed after `java -jar app.jar` on the command line. Spring can read settings from
  there too (for example `--server.port=9090`).

`run` does not return until the application shuts down. The program sits inside it, serving requests.
So everything Spring does at start-up happens *inside this one call*. Let's look inside.
:::

:::step{type=concept title="What SpringApplication.run does" file="04-app-startup/src/main/java/com/shop/ShopApiApplication.java" line="10"}
Press **▶ Play** to watch the start-up one step at a time (or use **Next** to go at your own pace). Read
the line under the picture at each step.

:::diagram{name="startup-sequence"}
Everything happens once, at start-up. After that, the application only answers requests.
:::

The important thing to take away: start-up is where Spring *prepares everything*. It reads settings,
finds your classes, creates objects, connects them, and opens the server. Once it says `Started`, the
preparation is over, and from then on it only does one thing: receive requests and call your methods.
That is why most configuration mistakes show up immediately, at start-up, and not later.
:::

:::step{type=example title="Reading the start-up log"}
The log you see when the app starts tells this same story. Here is a real one from this chapter's
project, with the timestamps shortened:

```text
 :: Spring Boot ::                (v3.4.1)

INFO [shop-api] [main] com.shop.ShopApiApplication : Starting ShopApiApplication v1.0 using Java 21.0.13 with PID 74
INFO [shop-api] [main] com.shop.ShopApiApplication : No active profile set, falling back to 1 default profile: "default"
INFO [shop-api] [main] o.s.b.w.embedded.tomcat.TomcatWebServer : Tomcat initialized with port 8080 (http)
INFO [shop-api] [main] o.apache.catalina.core.StandardService : Starting service [Tomcat]
INFO [shop-api] [main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 482 ms
INFO [shop-api] [main] o.s.b.w.embedded.tomcat.TomcatWebServer : Tomcat started on port 8080 (http) with context path '/'
INFO [shop-api] [main] com.shop.ShopApiApplication : Started ShopApiApplication in 0.933 seconds
```

Every line has the same parts: the **level** (`INFO`), the **app name** in brackets (that is the
`spring.application.name` you set in chapter 0!), the **thread** (`main`, the start-up thread), the
**class** that wrote it (shortened), and the **message**. Now the messages, in order:

1. **Starting...**: which app, which Java version, the process id (PID).
2. **No active profile set**: Spring uses the default settings. (Profiles let you have different settings
   for development and production; chapter 7.)
3. **Tomcat initialized with port 8080**: auto-configuration saw the web starter and set up Tomcat.
4. **initialization completed in 482 ms**: the **application context** (Spring's container, full of your
   objects) is ready. Your controllers were found and created in this phase.
5. **Tomcat started on port 8080**: the server is listening.
6. **Started ShopApiApplication**: done. Ready for requests.

When something fails, the log stops at the step that broke, followed by an error. So reading where it
stopped already tells you a lot.
:::

:::step{type=concept title="@SpringBootApplication: three annotations in one" file="04-app-startup/src/main/java/com/shop/ShopApiApplication.java" line="6-7"}
Now look at the annotation on the class: `@SpringBootApplication`. It is a shortcut for **three**
annotations, and each one switches on one part of the start-up you just watched:

- **`@Configuration`**: this class may define objects for Spring to manage (chapter 5 shows how).
- **`@EnableAutoConfiguration`**: switch on Spring Boot's auto-configuration (step 3 of the animation:
  look at the libraries present and set them up). Chapter 8 opens this box completely.
- **`@ComponentScan`**: **scan for components** (step 2). Search this class's package, and every package
  inside it, for classes marked `@RestController`, `@Component`, `@Service` and similar, and create them.

That last one is the answer to the mystery from chapter 3: nobody ever told Spring about
`MerchantController`. Component scanning found it, because it was marked `@RestController` and it lived
in the right place.

"The right place" is the key phrase. Let's be precise about it.
:::

:::step{type=concept title="The scanning rule: same package, or below"}
Component scanning starts at the package of the class marked `@SpringBootApplication`, and searches **that
package and every package below it**. Nothing else.

Our main class is in `com.shop`. So:

```text
com.shop.MerchantController            found      (same package)
com.shop.orders.OrderController        found      (com.shop.orders is below com.shop)
com.shop.orders.web.CartController     found      (any depth below)
com.shopping.ProductController         NOT found  (com.shopping is a different package, not below com.shop)
status.StatusController                NOT found  (status is not below com.shop)
```

A **package** in Java is like a folder name for classes, written with dots. `com.shop.orders` is "inside"
`com.shop` in the same way the folder `com/shop/orders` is inside `com/shop`. (In chapter 2 you saw that
the folders under `src/main/java` must match the package names exactly.)

This is why every Spring Boot project puts its main class in the **top-level package**, and all other
classes in packages below it. If you ever see a controller that "should work" but always returns 404, the
first thing to check is: is it below the main class's package?
:::

:::step{type=predict title="Guess first"}
:::question
The main class is `com.shop.ShopApiApplication`. A colleague adds `com.payments.PaymentController` with `@RestController` and `@GetMapping("/pay")`. What does GET /pay return?
:::
- [ ] 200, Spring finds every @RestController in the project
- [x] 404: com.payments is not inside com.shop, so scanning never finds it
- [ ] The app fails to start
:::explain
Scanning only looks at `com.shop` and the packages below it. The class compiles and sits in the jar, but
Spring never creates it, so no route for `/pay` exists. No error, just a quiet 404, which is exactly why
this mistake is so confusing the first time.
:::
:::

:::step{type=try title="Find the missing controller" file="04-app-startup/src/main/java/status/StatusController.java" line="1-8"}
This chapter's project has a controller with exactly this problem. It has opened on the right:
`StatusController`. Look at its first lines: `package status;`. And look at the file tree: it is in
`src/main/java/status/`, not under `com/shop/`.

Start the app and see the result:

```bash run
cd 04-app-startup && mvn -q -o package -DskipTests && java -jar target/app-startup.jar
```

In a second terminal:

```bash run
curl -i localhost:8080/status
```

404. The class is perfectly fine, it is just in a place Spring never looks. Stop the app with Ctrl+C.
:::

:::step{type=task task=component_scan title="Your turn: let Spring find StatusController"}
Move `StatusController` into a package **below `com.shop`**: make it `com.shop.status`. That takes two
changes, and both are needed:

1. **The file's location:** it must be in `src/main/java/com/shop/status/StatusController.java`. In the
   editor, you can create the new file there and paste the code, then delete the old one. Or in the
   terminal:

   ```bash run
   mkdir -p src/main/java/com/shop/status && mv src/main/java/status/StatusController.java src/main/java/com/shop/status/
   ```

2. **The package line** at the top of the file: change `package status;` to match the new folder.

Rebuild, run, and `curl localhost:8080/status` should answer `ok`. Press **Check**.
:::

:::step{type=concept title="Settings, read into your code: @Value" file="04-app-startup/src/main/java/com/shop/GreetingController.java" line="10-12"}
The second thing Spring does at start-up, before creating your objects, is read your settings. In chapter 0
you set `spring.application.name`, a setting Spring itself uses. Your own code can read settings too.

`GreetingController` has opened. Look at the highlighted field:

```java
@Value("${shop.greeting:not set}")
private String greeting;
```

`@Value` tells Spring: "when you create this object, fill this field from the settings". The text inside
is a small expression:

- `${shop.greeting}` means "the value of the property named `shop.greeting`". You choose property names
  for your own settings; using your app's name as the first part (`shop.`) keeps them apart from Spring's.
- `:not set` is a **default**: if the property does not exist, use the text `not set` instead.

The method `greeting()` simply returns that field. Right now, `application.properties` has no
`shop.greeting`, so `GET /greeting` answers `not set`.

Why not just write the greeting in the Java code? Because settings can change **without rebuilding**: on
the real server, someone can change the file (or an environment variable, chapter 7) and restart. Code is
for logic; settings are for values that depend on where and how the app runs.
:::

:::step{type=example title="When a setting is missing"}
The default after the colon is not decoration. Look at what happens without it:

```java
@Value("${shop.support-email}")     // no default
private String supportEmail;
```

If `shop.support-email` is not in the settings, **the application refuses to start**. The log stops before
`Started`, and you get an error like:

```text
Error creating bean with name 'supportController'
Could not resolve placeholder 'shop.support-email' in value "${shop.support-email}"
```

That is actually helpful: a required setting is missing, and Spring tells you at start-up, with the exact
property name, instead of letting the app run with a broken value. So the choice is yours:

- **With a default** (`${name:value}`): the setting is optional.
- **Without a default** (`${name}`): the setting is required, and the app will not start without it.
:::

:::step{type=task task=greeting_property title="Your turn: set the greeting"}
In `04-app-startup/src/main/resources/application.properties`, add a property `shop.greeting` with the
value `Welcome to the Shop API`.

Rebuild, run, and try:

```bash run
curl localhost:8080/greeting
```

It should answer `Welcome to the Shop API`. You did not touch any Java code: the controller read the new
value from the settings when Spring created it. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which annotation, hidden inside @SpringBootApplication, makes Spring find your controllers?
:::
- [ ] @EnableAutoConfiguration
- [x] @ComponentScan
- [ ] @Configuration
:::explain
`@ComponentScan` searches the main class's package and everything below it for annotated classes.
Auto-configuration sets up libraries (Tomcat, Jackson); it does not look for your classes.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A field has `@Value("${shop.max-cart-items}")`, and the property is not set anywhere. What happens?
:::
- [ ] The field is null
- [ ] The field is 0
- [x] The app fails at start-up: Could not resolve placeholder 'shop.max-cart-items'
:::explain
Without a default after a colon, the property is required. Spring stops at start-up and names the missing
property. Add `:20` (or any default) to make it optional.
:::
:::

:::step{type=deep-dive title="Go deeper: the banner, and the conditions report"}
**The banner.** The big ASCII-art "Spring" at the top of the log is the **banner**. You can replace it with
your own text in a `banner.txt` file in `src/main/resources`, or switch it off with
`spring.main.banner-mode=off`.

**The conditions report.** Run the app with `--debug` at the end of the command
(`java -jar target/app-startup.jar --debug`). Spring then prints a long **conditions evaluation report**:
every auto-configuration it considered, and whether it was used and why. "DispatcherServletAutoConfiguration
matched: found class DispatcherServlet". It looks overwhelming at first, but it is the best tool for
answering "why did Spring set up X?" or "why not?". Chapter 8 uses it.
:::

:::step{type=recap title="What you can do now"}
The start-up second is no longer a black box. You know:

- `SpringApplication.run` reads settings, scans for your classes, applies auto-configuration, creates and
  connects the objects, starts Tomcat, and logs `Started`. All once, at start-up.
- How to read the start-up log, line by line, and that a failing start-up stops at the step that broke.
- `@SpringBootApplication` = `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`.
- **The scanning rule:** only the main class's package and the packages below it. A class elsewhere is
  silently ignored, so its endpoints answer 404.
- `@Value("${name:default}")` reads a setting into a field; without a default, a missing setting stops the app.

Next, chapter 5: what exactly are those "objects Spring creates and connects"? Beans, and the application context.
:::
