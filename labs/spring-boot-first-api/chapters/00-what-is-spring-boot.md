:::step{type=story title="Welcome"}
Hi, and welcome to Spring Boot.

By the end of this course you will have built a real backend for an online shop, the **Shop API**, piece
by piece: products, prices, orders, a database, validation, error messages, tests, logins and a full
checkout. And more importantly, you will understand every line of it. Not "copy this annotation and it
works", but *why* it works, what Spring is doing behind your back, and what to do when it breaks.

You do not need to know anything about Spring yet. You need two things:

- **Basic Java**: classes, methods, `if`, loops, lists. If those feel shaky, the *Java from zero* course
  in LabBox covers all of it, and you can come back here after.
- **Patience with yourself.** Spring has a lot of new words. We will meet them one at a time, and every
  one of them will be explained the first time it appears. Nothing is assumed.

This first chapter has very little code. It answers the questions most courses skip: what is a
framework, why does Spring exist at all, and what is it actually doing when your app starts? Then you
will run your first Spring Boot application and give it its first setting.

:::mission
Understand what Spring Boot is and why it exists, run the Shop API for the first time, and name it.
:::
:::

:::step{type=concept title="How this lab works"}
Before we start, a quick tour of the screen, so you always know where to look.

**On the left** is the lesson you are reading. It is split into small steps. Use **Continue** (or the
right arrow key) to move on and **Back** to go back. The dots at the top show where you are; you can
click any dot to jump.

**On the right** is your own small Linux computer, running just for you. It has Java, Maven and
everything Spring needs already installed. At the top is the code editor, at the bottom a **terminal**
where you type commands.

When a lesson talks about a file, **that file opens on the right by itself**, and the lines it talks
about are highlighted. You never have to hunt for anything.

Commands in the lesson have a **▶ Run in terminal** button. It types the command into your terminal for
you. You still press Enter yourself, so you always see what runs. You can open a second terminal with the
**+** next to the Terminal tab: handy when one terminal is busy running your server.

At the bottom left is the **Check** button. When a step gives you a task, you write the code, press
Check, and LabBox runs hidden tests on your work. If something is not right yet, it tells you what it
expected and what it got. Getting "not yet" is normal and expected. It is how you learn.

Stuck? The 💡 button gives a hint, one at a time, from a gentle nudge to almost the answer.
:::

:::step{type=concept title="What is a server, really?"}
Let's start with the thing we are going to build: a **backend**, also called a **server**.

When you open a shopping app on your phone and see a list of products, your phone did not invent that
list. It sent a message over the internet to a computer somewhere, asking "please give me the products".
That computer ran some code, looked the products up in a database, and sent the list back. The phone
then drew it nicely on the screen.

That computer, and the program running on it, is the **backend**. The phone app is the **frontend**.

The message the phone sends is called a **request**, and the answer is a **response**. They are written
in a format called **HTTP**, which every browser, phone and server in the world understands. A request
looks roughly like this:

```text
GET /products HTTP/1.1
Host: api.myshop.in
```

It says: *get* me the thing at the address `/products`. The server answers with a status (did it work?)
and the data, usually written as **JSON**:

```json
[{"id": 1, "name": "Masala tea", "price": 20}, {"id": 2, "name": "Samosa", "price": 18}]
```

Chapter 1 goes through HTTP and JSON properly, with a real server you can poke at. For now, keep just
this picture in your head: **a backend is a program that waits for requests and sends back responses.**
:::

:::step{type=concept title="What a backend has to do before your code even runs"}
"Waits for requests and sends back responses" sounds simple. Here is what it actually involves. Before
the first line of *your* shop logic can run, a backend program has to:

- **Open a network port** (a numbered door, like 8080) and listen for connections.
- **Read the raw bytes** that arrive and understand them as HTTP: which method, which address, which
  headers, what body.
- **Handle many people at once.** A hundred phones may ask at the same moment; each needs its own
  thread of work, without mixing up their answers.
- **Decide which piece of your code** should handle `/products`, and which should handle `/orders`.
- **Convert JSON into Java objects**, and Java objects back into JSON.
- Often also: talk to a **database**, check who is **logged in**, write **logs** when something fails,
  and report whether the app is **healthy**.

None of this is about *your shop*. Every backend in the world needs exactly the same machinery. Writing it
yourself would take thousands of lines and months of fixing subtle bugs, before you could even say hello.

That is the problem a framework solves.

:::diagram{name="backend-stack"}
You write the top layer, your shop's logic. Spring Boot and its built-in web server provide everything under it.
:::
:::

:::step{type=concept title="Library or framework: who is in charge?"}
You have probably used **libraries** before. A library is a box of ready-made code that **you call**
when you need it. For example, to turn text into a date:

```java
LocalDate day = LocalDate.parse("2026-11-21");   // you decide when this runs
```

Your program is in charge. It runs from top to bottom, and calls the library whenever it wants.

A **framework** flips this around. The framework is the program. It starts first, it runs the main loop,
it waits for things to happen, and **it calls your code** at the right moments. You write small pieces
that say "when someone asks for `/products`, run this method", and the framework decides *when* that
happens.

```java
@GetMapping("/products")          // "framework, when someone asks for /products..."
public List<Product> products() { // "...call this method, and send back what it returns"
    return shop.allProducts();
}
```

You never call `products()` yourself. You never will. Spring calls it, every time a request for
`/products` arrives.

This flip has a name that you will hear often: **inversion of control**. "Control" (who decides what runs
when) has been "inverted" (moved from your code to the framework). It sounds fancy; it just means *the
framework is in charge and calls you*.

:::diagram{name="library-vs-framework"}
A library waits for your code to call it. A framework runs the show and calls your code when something happens.
:::
:::

:::step{type=predict title="Guess first"}
:::question
In the `@GetMapping("/products")` example above, who calls the `products()` method?
:::
- [ ] Your `main` method, once, at start-up
- [x] Spring, every time a request for `/products` arrives
- [ ] Nobody: the annotation replaces the method
:::explain
That is inversion of control in one sentence: you write the method and mark it, and the framework calls
it whenever the matching request comes in. A hundred requests, a hundred calls, and you never wrote
one of them.
:::
:::

:::step{type=history title="The story of Spring"}
Spring is now more than twenty years old, and knowing where it came from explains a lot about how it
looks today.

:::before{title="Before Spring"}
Around the year 2000, the official way to build serious Java servers was called **J2EE**, with a part
named **EJB** (Enterprise JavaBeans). It was powerful, and painful. A simple service that adds two numbers
needed several Java interfaces, a long XML file describing them, and a big, expensive **application
server** program (with names like WebLogic and WebSphere) to deploy into. Every change meant packaging
and redeploying, which could take minutes. And because your code only ran *inside* that server, testing
it on its own was very hard. Developers spent more time feeding the machinery than writing business logic.
:::

:::solved
**Plain Java objects, wired together by a small container.** Spring's idea was: write ordinary Java
classes, with no special interfaces, and let a lightweight **container** create them and connect them to
each other. Your classes stay simple, readable and easy to test. Ten years later, **Spring Boot** (2014)
removed the remaining pain: sensible defaults instead of long configuration, a web server *inside* your
application, and one command to run it.
:::

The story starts with one developer, **Rod Johnson**. In 2002 he published a book, *Expert One-on-One
J2EE Design and Development*, that argued enterprise Java could be much simpler, and he shipped about
30,000 lines of example code with it. Readers loved the code more than the book. It grew into an
open-source project, and **Spring 1.0** was released in **March 2004**.

**Spring Boot 1.0** came out in **April 2014**, built by the Spring team at **Pivotal**. Today Spring is
maintained by the Spring team at **Broadcom** (which bought VMware, Pivotal's parent, in 2023), together
with a big open-source community. You are using **Spring Boot 3.4** with **Java 21** in this course.

:::diagram{name="spring-timeline"}
From one book in 2002 to the most widely used Java framework today.
:::

:::funfact
The name "Spring" was chosen as a fresh start: spring after the long, cold "winter" of heavyweight J2EE.
:::
:::

:::step{type=concept title="Where Spring Boot is used"}
Why learn Spring Boot rather than something else? Because it is everywhere Java is.

Spring is the most used Java framework in developer surveys year after year. If you look at Java
backend job listings in India or anywhere else, most of them say Spring Boot. It runs the backends of
**banks and payment companies**, **e-commerce and food delivery** platforms, **insurance**, **telecom**,
**logistics**, **airlines** and **government systems**. Netflix has spoken publicly about building its
Java services on Spring Boot.

Teams choose it for very practical reasons:

- **It covers the whole job.** Web APIs, databases, security, testing, monitoring and messaging all come
  from the same family and are designed to work together.
- **It is stable.** Each version gets years of fixes. Code written five years ago still runs.
- **Everything is documented**, and almost any error message you will ever see has been asked about and
  answered before.
- **It is easy to hire for.** Most Java developers know it, so teams can grow.

So the skill you build here is not a toy skill. It is the daily work of a very large number of
professional developers.
:::

:::step{type=concept title="Spring, and Spring Boot: what is the difference?"}
You will hear both names. They are related but not the same thing.

**Spring** (officially *the Spring Framework*) is the core. Its heart is the **container**: the part that
creates your objects and connects them together. Around it are modules for web requests, databases,
transactions and more.

**Spring Boot** sits on top of Spring and makes it quick to start. It adds three things:

1. **Starters.** One line in your project, like `spring-boot-starter-web`, brings every library needed
   for a job (the web server, the JSON library, Spring's web module), in versions tested to work together.
   No hunting for compatible versions.
2. **Auto-configuration.** When your app starts, Spring Boot looks at which libraries are present and
   sets them up with sensible defaults. The web starter is there? Then it starts a web server on port
   8080, sets up JSON, and so on. You only write configuration when you want something *different* from
   the default. (Chapter 8 opens this box and shows exactly how it decides.)
3. **An embedded server.** The web server, **Tomcat**, runs *inside* your application. There is no
   separate server program to install. You run one file, and that file *is* the whole server.

So: Spring is the engine; Spring Boot is the engine, already assembled, fuelled and ready to drive.
:::

:::step{type=predict title="Guess first"}
:::question
You add `spring-boot-starter-web` to a project. What else must you install separately to answer HTTP requests?
:::
- [ ] Tomcat, the web server
- [ ] A JSON library
- [x] Nothing: the starter brings an embedded Tomcat and a JSON library
:::explain
That is the point of a starter. The web starter brings Tomcat (embedded, inside your app) and Jackson
(for JSON), plus Spring's web module, in versions that work together.
:::
:::

:::step{type=concept title="Your first project: the pom.xml" file="00-what-is-spring-boot/pom.xml" line="6-27"}
Let's look at a real Spring Boot project. On the right, the file `pom.xml` has just opened. This is the
project's description file for **Maven**, the build tool (chapter 2 covers Maven in detail; for now we
only read the important parts).

The highlighted lines are the ones that make this a Spring Boot project:

- The `<parent>` block says "this project is built on **spring-boot-starter-parent**, version 3.4.1".
  The parent decides the versions of hundreds of libraries for you, so they always fit together.
- Inside `<dependencies>`, **spring-boot-starter-web** is the web starter we just talked about: Tomcat,
  JSON and Spring's web module, all in one line.
- **spring-boot-starter-test** brings the tools for writing tests. The `<scope>test</scope>` line means
  "only needed while testing, not in the final app".

That is all it takes. Two starters, one parent, and Maven downloads and wires up everything else.
:::

:::step{type=concept title="The main class" file="00-what-is-spring-boot/src/main/java/com/shop/ShopApiApplication.java" line="7-12"}
Now `ShopApiApplication.java` is open. Every Java program starts at a `main` method, and a Spring Boot
app is no different. Look at what this one does: just one line.

```java
SpringApplication.run(ShopApiApplication.class, args);
```

That single call starts *everything*: Spring's container, the auto-configuration, and the embedded Tomcat
web server. Then it waits for requests, forever, until you stop it.

Above the class sits `@SpringBootApplication`. An **annotation** (a word starting with `@`) is a label
you put on a class or method. It does nothing by itself; it is information that Spring reads. This one
tells Spring: "this is the main class of a Spring Boot application, start looking for my code from here".

Chapter 4 follows this `run` call step by step, with an animation of everything it does. For now: one
line starts a whole server.
:::

:::step{type=try title="Run your first Spring Boot app"}
Let's run it. First we build the project into a single runnable file (a **jar**), then we start it:

```bash run
cd 00-what-is-spring-boot && mvn -q -o package -DskipTests && java -jar target/shop-api.jar
```

The first build takes a little while. Then watch the output scroll past. Do not worry about most of it.
Look for these lines (yours will have different times):

```text
Tomcat initialized with port 8080 (http)
Tomcat started on port 8080 (http) with context path '/'
Started ShopApiApplication in 0.933 seconds (process running for 1.169)
```

Read them in order. Tomcat (the web server) was set up on port 8080, then started, then the whole
application reported it was ready. In about one second, you have a running web server.

Notice that the terminal does not come back to the `$` prompt. That is correct: a server **keeps
running**, waiting for requests. Leave it running for the next step.
:::

:::step{type=try title="Knock on the door"}
Your server is running in the first terminal. Open a **second terminal** with the **+** next to the
Terminal tab, and send the server a request with `curl`, a tool that sends HTTP requests from the command line:

```bash run
curl -i localhost:8080/products
```

You get back something like:

```text
HTTP/1.1 404
Content-Type: application/json
...
{"timestamp":"...","status":404,"error":"Not Found","path":"/products"}
```

**404** means "not found". And that is exactly right! The server is running and answering, but nobody
has written any code for `/products` yet. Spring received your request, looked for a method that handles
`/products`, found none, and answered politely with 404.

You will write your first endpoints in chapter 3. For now, click **Terminal 1** and stop the server with
**Ctrl+C**. The `$` prompt comes back.
:::

:::step{type=example title="Settings live in application.properties" file="00-what-is-spring-boot/src/main/resources/application.properties"}
Spring Boot apps are configured with a small text file: `src/main/resources/application.properties`.
It has opened on the right. It is almost empty for now: a comment, and a TODO for you.

Each setting is one line: a **property name**, an equals sign, and a **value**. Lines starting with `#`
are comments, for humans only. Here is what a few settings could look like in a real app:

```properties
# Which port the web server listens on (8080 is the default).
server.port=8080
# How much detail to log for Spring's web layer.
logging.level.org.springframework.web=INFO
```

Why put settings in a file instead of in Java code? Because then you can change how the app behaves
(a different port, a different database address on the real server) **without changing and rebuilding
the code**. Spring Boot knows hundreds of these properties. You only write the ones where you want
something other than the default. Chapter 7 goes deep into configuration.
:::

:::step{type=task task=app_name title="Your first task: name the application"}
Every Spring Boot app can have a name, and the name appears in its logs, its health checks and its
monitoring. Ours is currently nameless.

In `00-what-is-spring-boot/src/main/resources/application.properties`, replace the TODO comment with
this setting: the property `spring.application.name` with the value `shop-api`.

Then press **Check**. If you like, run the app again first: the name now appears in square brackets in
every log line, like `[shop-api]`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does "inversion of control" mean?
:::
- [ ] Your code controls when the framework runs
- [x] The framework runs the program and calls your code when it is needed
- [ ] The framework rewrites your code when it builds it
:::explain
Exactly: the framework owns the main loop. It receives the requests and calls the methods you wrote for
them. You supply only the parts that are specific to your application.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You run the app and request `/products`, and get a 404. What does that tell you?
:::
- [ ] The server is not running
- [ ] Tomcat is broken
- [x] The server is running fine; no code handles `/products` yet
:::explain
A 404 is an answer, and only a running server can answer. If the server were not running, curl would say
"Connection refused" instead. 404 just means "I am here, but I have nothing at that address".
:::
:::

:::step{type=recap title="What you know now"}
You have covered a lot of ground without writing much code. You now know:

- A **backend** is a program that waits for HTTP **requests** and sends back **responses**, usually as **JSON**.
- A **framework** runs the program and calls your code: **inversion of control**. A library is called by you.
- **Spring** gives you a container that creates and connects your objects; **Spring Boot** adds
  **starters**, **auto-configuration** and an **embedded Tomcat** server, so one line starts everything.
- Spring began with Rod Johnson's 2002 book and **Spring 1.0 (2004)**; **Spring Boot 1.0 (2014)** made it
  quick to start. Today it runs backends in banking, shopping, travel and much more.
- A project has a `pom.xml` (what it needs), a main class (`SpringApplication.run`), and
  `application.properties` (its settings).
- You built and ran a real server, and named it.

Next, chapter 1 takes a proper look at HTTP and JSON: the language your server will speak.
:::
