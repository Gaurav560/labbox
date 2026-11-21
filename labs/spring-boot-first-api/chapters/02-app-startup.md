:::step{type=story title="Why this chapter"}
When something does not work in Spring Boot, the cause is usually in how the application starts: a
class Spring did not find, or a setting it did not read. This chapter explains what happens between
`main` and "Started", so those problems become easy to diagnose.

:::mission
In the `02-app-startup` folder: make Spring find a controller it is missing, and move a greeting out of
the code into `application.properties`.
:::
:::

:::step{type=concept title="What SpringApplication.run does" file="02-app-startup/src/main/java/com/shop/ShopApiApplication.java" line="10"}
`main` calls one method:

```java
SpringApplication.run(ShopApiApplication.class, args);
```

That call does six things, in this order:

1. reads `application.properties` (and command-line arguments);
2. **scans** for your classes marked `@Component`, `@RestController`, `@Service` and similar;
3. applies **auto-configuration** for the libraries on the classpath;
4. creates the objects it manages (**beans**) and connects them;
5. starts the embedded **Tomcat** server on port 8080;
6. logs `Started ShopApiApplication` and waits for requests.

:::diagram{name="startup-sequence"}
Everything happens once, at start-up. After that, the application only answers requests.
:::
:::

:::step{type=concept title="@SpringBootApplication and component scanning" file="02-app-startup/src/main/java/com/shop/ShopApiApplication.java" line="1-7"}
`@SpringBootApplication` on the main class combines three annotations:

- `@Configuration`: this class may define beans;
- `@EnableAutoConfiguration`: turn on auto-configuration;
- `@ComponentScan`: search **this class's package and every package below it** for components.

The main class is in `com.shop`, so Spring scans `com.shop`, `com.shop.product`, `com.shop.status` and
so on. A class in a package outside that tree, such as `status` or `org.example`, is never found: its
endpoints simply answer 404, with no error at start-up.
:::

:::step{type=example title="Worked example: a class Spring cannot see"}
Two classes with the same code, in different packages:

```text
src/main/java/com/shop/ShopApiApplication.java      package com.shop          the main class
src/main/java/com/shop/menu/MenuController.java     package com.shop.menu     found
src/main/java/menu/MenuController.java              package menu              not found
```

1. `com.shop.menu` is below `com.shop`, so component scanning finds it and maps its URLs.
2. `menu` is a separate top-level package. Spring never looks there; its URLs answer 404.
3. The fix is to move the file and change its `package` line to match the new folder.

In Java, the `package` line and the folder must always agree.
:::

:::step{type=predict title="Guess first"}
:::question
`OrderController` is in `org.shop.orders`; the main class is in `com.shop`. What happens when the app starts?
:::
- [ ] Start-up fails with an error naming `OrderController`
- [x] The app starts normally, and the order URLs answer 404
- [ ] Spring finds it, because both packages contain "shop"
:::explain
Component scanning only looks under the main class's package. Classes elsewhere are silently ignored,
which is why a 404 is the typical symptom.
:::
:::

:::step{type=try title="Find the missing controller" file="02-app-startup/src/main/java/status/StatusController.java" line="3"}
Start the app from the chapter folder and call both URLs:

```bash run
cd 02-app-startup && mvn -q -o package -DskipTests && java -jar target/app-startup.jar
```

In a second terminal tab:

```bash run
curl -s localhost:8080/status; echo; curl -s localhost:8080/greeting; echo
```

`/status` answers 404 and `/greeting` answers `not set`. Look at where `StatusController.java` is.
:::

:::step{type=task task=component_scan title="Warm-up: make Spring find StatusController"}
`StatusController` is in `src/main/java/status/`, outside `com.shop`. Move it to
`src/main/java/com/shop/status/` and change its `package` line to `package com.shop.status;`.

`GET /status` should then answer `ok`.
:::

:::step{type=concept title="Reading a setting with @Value" file="02-app-startup/src/main/java/com/shop/GreetingController.java" line="10-12"}
Values that may change between environments (a greeting, a URL, a limit) belong in
`application.properties`, not in code. `@Value` injects a property into a field when Spring creates the bean:

```java
@Value("${shop.greeting:not set}")
private String greeting;
```

- `${shop.greeting}` is the property name.
- The part after `:` is a **default**, used when the property is missing.
- Without a default, a missing property stops the application at start-up with an error.

Chapter 10 shows `@ConfigurationProperties`, a structured way to read many settings at once.
:::

:::step{type=task task=greeting_property title="Move the greeting into settings"}
`GreetingController` reads `shop.greeting`, which is not set yet. In
`02-app-startup/src/main/resources/application.properties`, add:

`shop.greeting` with the value `Welcome to the Shop API`

`GET /greeting` should then answer `Welcome to the Shop API`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which annotation tells Spring which packages to search for components?
:::
- [ ] `@RestController`
- [x] `@ComponentScan`, included in `@SpringBootApplication`
- [ ] `@Value`
:::explain
`@SpringBootApplication` includes `@ComponentScan`, which starts from the main class's package.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`@Value("${shop.limit}")` has no default, and `shop.limit` is not set. What happens?
:::
- [ ] The field is `null`
- [ ] The field is `0`
- [x] The application fails to start, with an error naming `shop.limit`
:::explain
Without a default after `:`, Spring cannot fill the field and refuses to start. That is often what you
want: a missing setting is found at start-up, not later by a user.
:::
:::

:::step{type=deep-dive title="The conditions report"}
Auto-configuration is a set of rules like "if the web library is present and no web server is
configured, configure Tomcat". Start the app with `--debug` and Spring prints the **conditions
evaluation report**: every auto-configuration, and why it was or was not applied. It is the first
place to look when Spring configures something you did not expect, or does not configure something
you did.
:::

:::step{type=recap title="Chapter done"}
- `SpringApplication.run` reads settings, scans for components, auto-configures, creates beans and starts Tomcat.
- Component scanning searches the main class's package and everything below it; classes elsewhere are ignored.
- `@Value("${name:default}")` injects a property from `application.properties`.
:::
