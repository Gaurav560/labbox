:::step{type=story title="Why this chapter"}
Most Java backend jobs today are Spring Boot jobs. Before writing any code, this chapter explains what
a framework is, what problem Spring solves, where it came from and where it is used. You will finish by
running a real Spring Boot application and giving it its first setting.

:::mission
Understand what Spring Boot does for you, run the Shop API, and name it in `application.properties`.
:::
:::

:::step{type=concept title="What a framework is"}
A **framework** is code that runs your application and calls *your* code at defined points.

Compare it with a **library**. A library is code you call: your program decides when to parse JSON, and
calls Jackson to do it. With a framework, the framework is in charge: it starts the program, waits for
events (here, HTTP requests), and calls the methods you wrote for them.

This reversal is called **inversion of control**. You write the parts that are specific to your
application; the framework provides everything that every application needs.

:::diagram{name="library-vs-framework"}
A library waits for your code to call it. A framework calls your code when something happens.
:::
:::

:::step{type=concept title="What a backend has to do"}
A backend (the server side of an app) answers HTTP requests. Before your code runs even once, a
backend must:

- open a network **port** and accept connections;
- read and parse **HTTP** requests;
- handle many requests **at the same time** (threads);
- decide which method handles which **URL**;
- convert **JSON** to Java objects and back;
- often also: connect to a **database**, check **logins**, log errors.

Written by hand, that is thousands of lines before the first useful endpoint. Spring Boot provides all of
it, so a working endpoint is a few lines.

:::diagram{name="backend-stack"}
You write the top layer. Spring Boot and its built-in web server provide the rest.
:::
:::

:::step{type=history title="The story of Spring"}
Spring changed how Java servers are written, and Spring Boot made starting one take minutes.

:::before{title="Before Spring"}
In the early 2000s, enterprise Java meant **J2EE** and **EJB** (Enterprise JavaBeans). A simple service
needed several interfaces, long XML configuration files and a heavy **application server** (WebLogic,
WebSphere) to deploy into. Restarting took minutes, and code was hard to test outside the server.
:::

:::solved
**Plain Java objects, wired together by a container.** Spring let developers write ordinary classes and
let a lightweight container create them and connect them (dependency injection). Code became simple
to read and to test. **Spring Boot** (2014) then removed most configuration: sensible defaults, a web
server built into the application, and one command to run it.
:::

**Rod Johnson** described the approach in his 2002 book *Expert One-on-One J2EE Design and
Development*, and its code became the Spring Framework, released as **Spring 1.0 in 2004**. Spring Boot
was created by the Spring team at **Pivotal**. Today Spring is maintained by the Spring team at
**Broadcom** (which acquired VMware, Pivotal's successor, in 2023), with a large open-source community.

:::diagram{name="spring-timeline"}
From one book in 2002 to the most used Java framework today.
:::

:::usedby{title="Industries"}
- Banking and payments
- E-commerce
- Insurance
- Telecom
- Government systems
- Logistics
:::

:::funfact
The name "Spring" was chosen to mark a fresh start after the "winter" of heavyweight J2EE.
:::
:::

:::step{type=concept title="Where Spring Boot is used, and why"}
Spring Boot is the most widely used Java framework in developer surveys, and it runs backends at
companies of every size, from startups to banks. Netflix, for example, builds its Java services on it.

Teams choose it for practical reasons:

- **It covers the whole backend:** web, data, security, testing and monitoring, all designed to work together.
- **Stable and well documented:** long support for each version, and answers for almost every problem.
- **Easy to hire for:** most Java developers know it.

That is also why it appears in most Java backend job descriptions.
:::

:::step{type=concept title="Spring and Spring Boot"}
**Spring** (the Spring Framework) is the core: the container that creates objects and injects them,
plus modules for web, data access, transactions and more.

**Spring Boot** is built on top of it and adds three things:

1. **Starters**: one dependency, such as `spring-boot-starter-web`, brings every library needed for a
   job, in versions known to work together.
2. **Auto-configuration**: Spring Boot looks at the libraries on the classpath and configures them with
   sensible defaults. Web library present? It sets up a web server.
3. **An embedded server**: Tomcat runs inside your application. You run one `jar`; there is no server
   to install.
:::

:::step{type=predict title="Guess first"}
:::question
Which of these does a Spring Boot web application need you to install separately?
:::
- [ ] Tomcat, the web server
- [ ] The JSON library
- [x] Neither: both come with `spring-boot-starter-web`
:::explain
The web starter brings an embedded Tomcat and Jackson (for JSON). The application is one `jar` that
contains its own server.
:::
:::

:::step{type=try title="Look at the project, then run it"}
Two files make this project a Spring Boot application. `pom.xml` lists the starter:

```bash run
grep -A1 "<artifactId>spring-boot-starter" pom.xml
```

`ShopApiApplication.java` holds `main`, which calls `SpringApplication.run(...)`. Build and start it:

```bash run
mvn -q -o package -DskipTests && java -jar target/shop-api.jar
```

Look for `Tomcat started on port 8080` and `Started ShopApiApplication` in the output. Stop it with Ctrl+C.
:::

:::step{type=example title="Worked example: a setting in application.properties"}
`src/main/resources/application.properties` holds settings that Spring Boot reads at start-up. One
setting per line, `name=value`:

```properties
# The port the embedded Tomcat listens on (8080 is the default).
server.port=8080
# How much detail to log for Spring's web layer.
logging.level.org.springframework.web=INFO
```

1. Lines starting with `#` are comments.
2. Changing a value changes the behaviour without changing Java code.
3. Spring Boot documents hundreds of these properties; you only set the ones you want to change.
:::

:::step{type=task task=app_name title="Warm-up: name the application"}
In `src/main/resources/application.properties`, set the property `spring.application.name` to `shop-api`.

Run the app again: the name appears in every log line.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does "inversion of control" mean?
:::
- [ ] Your code controls when the framework runs
- [x] The framework runs the program and calls your code when needed
- [ ] The framework rewrites your code at build time
:::explain
The framework owns the main loop: it receives requests and calls your methods. You supply the parts
that are specific to your application.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does Spring Boot's auto-configuration do?
:::
- [ ] Writes your controllers for you
- [x] Configures libraries found on the classpath with sensible defaults
- [ ] Downloads missing libraries at run time
:::explain
It inspects what is on the classpath (for example, the web starter) and sets those parts up. You can
override any default in `application.properties`.
:::
:::

:::step{type=recap title="Chapter done"}
- A framework runs the application and calls your code (inversion of control).
- Spring provides the container and modules; Spring Boot adds starters, auto-configuration and an embedded server.
- Spring started in 2004 as a simpler alternative to J2EE; Spring Boot (2014) made it quick to start.
- `application.properties` holds settings that Spring Boot reads at start-up.
:::
