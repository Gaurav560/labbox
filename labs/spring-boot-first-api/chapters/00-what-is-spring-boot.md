:::step{type=story title="Welcome"}
Hi, and welcome to Spring Boot.

In this course you build a real backend for an online shop, the **Shop API**, one piece at a time: products,
prices, orders, a database, checks on the data people send, clear error messages, tests, logins and a full
checkout. More importantly, you will understand every line of it. Not "copy this annotation and it works", but
*why* it works, what Spring is doing for you, and what to do when it breaks.

You do not need to know anything about Spring yet. You need two things:

- **Basic Java**: classes, methods, `if`, loops and lists. If those feel shaky, the *Java from zero* course in
  LabBox covers all of them, and you can come back here after.
- **Patience with yourself.** Spring has many new words. We meet them one at a time, and each one is explained
  the first time it appears.

This first chapter has very little code. It answers the questions most courses skip: what is a framework, why
does Spring exist, and what is it doing when your app starts? Then you run your first Spring Boot application
and give it its first setting.

:::mission
Understand what Spring Boot is and why it exists, run the Shop API for the first time, and give it a name.
:::
:::

:::step{type=concept title="How this lab works"}
Before we start, a short tour of the screen, so you always know where to look.

**On the left** is the lesson you are reading. It is split into small steps. **Continue** (or the right arrow
key) moves on, **Back** goes back. The dots at the top show where you are; click any dot to jump to it.

**On the right** is your own small Linux computer, running just for you. It already has Java, Maven (the build
tool, chapter 2) and everything Spring needs. At the top is the code editor; at the bottom is a **terminal**, a
window where you type commands and see what they print.

When a lesson talks about a file, **that file opens on the right by itself**, with the lines it talks about
highlighted. You never have to hunt for anything.

Commands in the lesson have a **▶ Run in terminal** button. It types the command into your terminal; you still
press Enter yourself, so you always see what runs. The **+** next to the Terminal tab opens a second terminal,
which is handy when the first one is busy running your server.

At the bottom left is the **Check** button. When a step gives you a task, you write the code and press Check,
and LabBox runs hidden tests on your work. If something is not right yet, it tells you what it expected and what
it got. "Not yet" is normal. It is how you learn.

Stuck? The 💡 button gives a hint, one at a time, from a small nudge to almost the answer.
:::

:::step{type=concept title="What is a server, really?"}
Let's start with the thing we are going to build: a **backend**, also called a **server**.

The first web server was written in 1990 at CERN, the physics laboratory in Geneva, by **Tim Berners-Lee**. He
also invented the web itself: web addresses (URLs), the HTTP language below, and HTML pages. Chapter 1 shows the
computer that first server ran on.

:::photo{src="/lesson-images/spring/berners-lee.webp" alt="Sir Tim Berners-Lee, inventor of the World Wide Web, in a dark suit and blue tie" credit="Paul Clarke" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Sir_Tim_Berners-Lee_(cropped).jpg"}
Tim Berners-Lee. He wrote the first web server and the first web browser, so every backend you build descends from his.
:::

When you open a shopping app on your phone and see a list of products, the phone did not make that list up. It
sent a message over the internet to a computer somewhere: "please give me the products". That computer ran some
code, looked the products up, and sent the list back. The phone then drew it on the screen.

That computer, and the program running on it, is the **backend**. The app on the phone is the **frontend**.

The message the phone sends is a **request**, and the answer is a **response**. Both are written in **HTTP**
(HyperText Transfer Protocol), a set of rules for these messages that every browser, phone and server
understands. A request looks roughly like this:

```text
GET /products HTTP/1.1
Host: api.myshop.in
```

The first line says: *get* me the thing at the address `/products`, using HTTP version 1.1. The second line names
the server it is meant for. The server answers with a status (did it work?) and the data, usually written as
**JSON** (JavaScript Object Notation). JSON is plain text with a few simple rules: `{ }` holds named values,
`[ ]` holds a list, text goes in double quotes. For example, two products:

```json
[{"id": 1, "name": "Mango kulfi", "price": 20}, {"id": 2, "name": "Samosa", "price": 18}]
```

Chapter 1 covers HTTP and JSON properly, with a real server you can try. For now, keep one sentence in mind:
**a backend is a program that waits for requests and sends back responses.**
:::

:::step{type=concept title="What a backend has to do before your code even runs"}
"Waits for requests and sends back responses" sounds simple. Here is what it involves. Before the first line of
*your* shop's code can run, a backend program has to:

- **Open a network port and listen.** A port is a number from 0 to 65535 that tells the computer which program a
  network message is for. Web servers in development often use 8080.
- **Read the raw bytes** that arrive and make sense of them as HTTP: which method, which address, which
  headers (extra lines of information), what body.
- **Serve many people at once.** A hundred phones may ask at the same moment. The server handles them side by
  side on separate **threads** (lines of work that run at the same time inside one program), without mixing up
  their answers.
- **Pick the right piece of your code**: one method for `/products`, another for `/orders`.
- **Turn JSON into Java objects**, and Java objects back into JSON.
- Often also: talk to a **database**, check who is **logged in**, write **logs** (a running record of what
  happened) when something fails, and report whether the app is **healthy**.

None of this is about *your shop*. Every backend needs the same machinery. Writing it yourself would take
thousands of lines and months of fixing tricky bugs before you could even say hello.

That is the problem a framework solves.

:::diagram{name="backend-stack"}
You write the top layer, your shop's logic. Spring Boot and its built-in web server provide everything under it.
:::
:::

:::step{type=concept title="Library or framework: who is in charge?"}
You have probably used **libraries** before. A library is a box of ready-made code that **you call** when you
need it. For example, to turn text into a date:

```java
LocalDate day = LocalDate.parse("2026-11-21");   // you decide when this runs
```

Your program is in charge. It runs from top to bottom and calls the library whenever it wants.

A **framework** flips this around. The framework is the program. It starts first, it keeps running, it waits for
things to happen, and **it calls your code** at the right moments. You write small pieces that say "when someone
asks for `/products`, run this method", and the framework decides *when* that happens.

```java
@GetMapping("/products")          // "Spring, when someone asks for /products..."
public List<Product> products() { // "...call this method and send back what it returns"
    return shop.allProducts();
}
```

Read it line by line. `@GetMapping("/products")` is a label (an **annotation**, chapter 3 explains them) that
says which request this method answers. `public List<Product> products()` is an ordinary Java method that returns
a list of products. `return shop.allProducts();` gets the list from somewhere else in the app.

You never call `products()` yourself, anywhere. Spring calls it, every time a request for `/products` arrives.

This flip has a name you will hear often: **inversion of control**. "Control" means who decides what runs and
when. It has been "inverted": moved from your code to the framework. It sounds fancy; it just means *the
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
That is inversion of control in one sentence: you write the method and label it, and the framework calls it
whenever a matching request comes in. A hundred requests mean a hundred calls, and you wrote none of them.
:::
:::

:::step{type=history title="The story of Spring"}
Spring is more than twenty years old, and where it came from explains a lot about how it looks today.

:::before{title="Before Spring"}
Around the year 2000, the official way to build large Java servers was **J2EE** (Java 2 Enterprise Edition),
with a part called **EJB** (Enterprise JavaBeans). It was powerful and painful. Even a small service needed
several Java interfaces plus a long XML file (a text file of tags, like `<bean>...</bean>`) describing them, and a
big **application server** product (WebLogic and WebSphere were well-known ones) to run inside. Every change meant
packaging and redeploying, which could take minutes. Because your code only ran *inside* that server, testing it
on its own was hard. Developers spent more time feeding the machinery than writing the business's logic.
:::

:::solved
**Plain Java objects, connected by a small container.** Spring's idea was: write ordinary Java classes, with no
special interfaces, and let a light **container** (a part of Spring that creates your objects and hands each one
the other objects it needs) do the wiring. Your classes stay simple, readable and easy to test. Ten years later,
**Spring Boot** (2014) removed most of the remaining set-up: sensible defaults instead of long configuration, a
web server *inside* your application, and one command to run it.
:::

The story starts with one developer, **Rod Johnson**. In 2002 he published a book, *Expert One-on-One J2EE Design
and Development*, arguing that enterprise Java could be much simpler, with about 30,000 lines of example code.
Readers liked the code even more than the book. It grew into an open-source project, and **Spring 1.0** came out
in **March 2004**.

**Spring Boot 1.0** came out in **April 2014**, built by the Spring team at **Pivotal**. Pivotal became part of
VMware in 2019, and Broadcom bought VMware in 2023, so today the Spring team works at **Broadcom**, together with a
large open-source community. This course uses **Spring Boot 3.4** (3.4.1 exactly) with **Java 21**.

:::diagram{name="spring-timeline"}
From one book in 2002 to the most used Java framework today.
:::

:::funfact
The name is usually explained as a fresh start: spring after the long "winter" of heavyweight J2EE.
:::
:::

:::step{type=concept title="Where Spring Boot is used"}
Why learn Spring Boot rather than something else? Because it is everywhere Java is.

Developer surveys, such as JetBrains' yearly survey of developers, list Spring Boot as the most used Java
framework year after year, and most Java backend job listings, in India and elsewhere, ask for it. It runs the
backends of **banks and payment companies**, **online shops and food delivery**, **insurance**, **telecom**,
**logistics**, **airlines** and **government services**. Netflix, for example, has written publicly about running
its Java services on Spring Boot.

Teams choose it for practical reasons:

- **It covers the whole job.** Web APIs, databases, security, testing, monitoring and messaging come from the same
  family and are built to work together.
- **It is looked after.** Each Spring Boot version gets about a year of free fixes (paid support goes longer),
  and every upgrade to a new version comes with written step-by-step notes.
- **It is well documented**, and almost any error message you will see has been asked about and answered before.
- **It is easy to hire for.** Most Java developers know it, so teams can grow.

So the skill you build here is not a toy skill. It is the daily work of a very large number of professional
developers.
:::

:::step{type=concept title="Spring, and Spring Boot: what is the difference?"}
You will hear both names. They are related, but not the same thing.

**Spring** (officially *the Spring Framework*) is the core. Its heart is the **container**: the part that creates
your objects and connects them. Around it are modules for web requests, databases, transactions and more.

**Spring Boot** sits on top of Spring and makes it quick to start. It adds three things:

1. **Starters.** One entry in your project, like `spring-boot-starter-web`, brings every library needed for a job,
   in versions tested to work together. In this lab, the web starter brings 30 libraries, among them the web
   server (Tomcat 10.1.34), the JSON library (Jackson 2.18.2) and Spring's web module (Spring Web MVC 6.2.1).
2. **Auto-configuration.** When your app starts, Spring Boot looks at which libraries are present and sets them up
   with sensible defaults. The web starter is there? Then it starts a web server on port 8080 and sets up JSON. You
   write configuration only when you want something *different* from the default. (Chapter 8 opens this box and
   shows how it decides.)
3. **An embedded server.** The web server, **Tomcat**, runs *inside* your application. There is no separate server
   program to install. You run one file, and that file *is* the whole server.

So Spring is the engine, and Spring Boot is the engine already assembled, fuelled and ready to drive.
:::

:::step{type=predict title="Guess first"}
:::question
You add `spring-boot-starter-web` to a project. What else must you install separately to answer HTTP requests?
:::
- [ ] Tomcat, the web server
- [ ] A JSON library
- [x] Nothing: the starter brings an embedded Tomcat and a JSON library
:::explain
That is the point of a starter. The web starter brings Tomcat (embedded, inside your app), Jackson (for JSON) and
Spring's web module, in versions that work together.
:::
:::

:::step{type=concept title="Your first project: the pom.xml" file="00-what-is-spring-boot/pom.xml" line="6-27"}
Let's look at a real Spring Boot project. On the right, the file `pom.xml` has opened. It is the project's
description file for **Maven**, the build tool that downloads libraries and turns your code into a runnable
program (chapter 2 covers it; for now we only read the important parts).

The highlighted lines make this a Spring Boot project:

- The `<parent>` block says "this project is built on **spring-boot-starter-parent**, version 3.4.1". The parent
  fixes the versions of hundreds of libraries for you, so they always fit together.
- `<java.version>21</java.version>` says the code is Java 21.
- Inside `<dependencies>` (the libraries this project needs), **spring-boot-starter-web** is the web starter we
  just talked about: Tomcat, JSON and Spring's web module, in one entry.
- **spring-boot-starter-test** brings the tools for writing tests. The line `<scope>test</scope>` means "only
  needed while testing, not in the finished app".

That is all it takes: one parent, two starters, and Maven fetches and connects everything else.
:::

:::step{type=concept title="The main class" file="00-what-is-spring-boot/src/main/java/com/shop/ShopApiApplication.java" line="7-12"}
Now `ShopApiApplication.java` is open. Every Java program starts at a `main` method, and a Spring Boot app is no
different. This one does just one thing:

```java
SpringApplication.run(ShopApiApplication.class, args);
```

That single call starts *everything*: Spring's container, the auto-configuration and the embedded Tomcat web
server. Then the program waits for requests until you stop it.

Above the class sits `@SpringBootApplication`. An **annotation** (a word starting with `@`) is a label you put on
a class, method or field. It does nothing by itself; it is information that Spring reads while the app starts.
This one tells Spring: "this is the main class of a Spring Boot application; look for my other classes starting
from this package".

Chapter 4 follows this `run` call step by step. For now: one line starts a whole server.
:::

:::step{type=try title="Run your first Spring Boot app"}
Let's run it. First Maven builds the project into one runnable file (a **jar**, a Java archive: a zip file of
compiled code and its libraries), then Java starts it:

```bash run
cd 00-what-is-spring-boot && mvn -q -o package -DskipTests && java -jar target/shop-api.jar
```

The command in parts: `mvn ... package` builds the jar (`-q` prints less, `-o` works offline from the libraries
already on this machine, `-DskipTests` skips the tests for now); `&&` means "only if that worked, then"; `java
-jar target/shop-api.jar` starts the app from the jar. On our lab machine the build took about 2 seconds and the
jar was about 20 MB, because it holds the app *and* its 30 libraries.

Watch the output scroll past. You can ignore most of it. Look for these three lines (your times will differ):

```text
Tomcat initialized with port 8080 (http)
Tomcat started on port 8080 (http) with context path '/'
Started ShopApiApplication in 1.122 seconds (process running for 1.395)
```

Read them in order. Tomcat (the web server) was set up on port 8080, then started. "Context path '/'" means the
app's addresses start right at the root, so `/products` is just `/products`. Then the whole application said it
was ready: on our machine after 1.122 seconds of Spring's own start-up work, 1.395 seconds after Java itself
started.

The terminal does not come back to the `$` prompt. That is correct: a server **keeps running**, waiting for
requests. Leave it running for the next step.
:::

:::step{type=try title="Knock on the door"}
Your server is running in the first terminal. Open a **second terminal** with the **+** next to the Terminal tab,
and send the server a request with `curl`, a program that sends HTTP requests from the command line and prints
the answer:

```bash run
curl -i localhost:8080/products
```

`localhost` means "this same computer", and `8080` is the port the server listens on. `-i` asks curl to print the
response's status and headers too, not just the body. On our lab machine the answer was:

```text
HTTP/1.1 404
Vary: Origin
Vary: Access-Control-Request-Method
Vary: Access-Control-Request-Headers
Content-Type: application/json
Transfer-Encoding: chunked
Date: Fri, 27 Nov 2026 20:24:25 GMT

{"timestamp":"2026-11-27T20:24:25.210+00:00","status":404,"error":"Not Found","path":"/products"}
```

**404** means "not found". And that is exactly right. The server is running and answering, but no code handles
`/products` yet. Spring received your request, looked for a method that handles `/products`, found none, and
answered politely with a 404 and a small JSON body that explains it. (The other header lines are details for
browsers; chapter 1 explains headers.)

You write your first endpoints in chapter 3. For now, click **Terminal 1** and stop the server with **Ctrl+C**.
The `$` prompt comes back.
:::

:::step{type=example title="Settings live in application.properties" file="00-what-is-spring-boot/src/main/resources/application.properties"}
Spring Boot apps read their settings from a small text file: `src/main/resources/application.properties`. It
has opened on the right. It is almost empty for now: a comment, and a TODO for you.

Each setting is one line: a **property name**, an equals sign, and a **value**. Lines starting with `#` are
comments, for people only. Here is what a few settings could look like:

```properties
# Which port the web server listens on (8080 is the default).
server.port=8080
# How much detail to log for Spring's web layer.
logging.level.org.springframework.web=INFO
```

Why keep settings in a file instead of in Java code? Because then you can change how the app behaves (a
different port, a different database address on the real server) **without changing and rebuilding the code**.
Spring Boot knows hundreds of these properties. You only write the ones where you want something other than the
default. Chapter 7 goes deep into configuration.
:::

:::step{type=task task=app_name title="Your first task: name the application"}
Every Spring Boot app can have a name. The name appears in its log lines, its health checks and its monitoring.
Ours has none yet.

What to do, in `00-what-is-spring-boot/src/main/resources/application.properties`:

1. Delete the TODO comment line.
2. Write one setting in its place: the property `spring.application.name`, an equals sign, and the value
   `shop-api`.
3. Press **Check**.

Usual slips: spaces or quotes around the value (write the value plain, no quotes), a typo in the property name
(it is all lower case, with dots), or editing the file in a different chapter's folder.

If you like, run the app again first: once the name is set, Spring Boot 3.4 shows it in square brackets near the
start of every log line, like `--- [shop-api] [main]`. Without a name, that part is simply missing.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does "inversion of control" mean?
:::
- [ ] Your code controls when the framework runs
- [x] The framework runs the program and calls your code when it is needed
- [ ] The framework rewrites your code when it builds it
:::explain
Right: the framework owns the running program. It receives the requests and calls the methods you wrote for them.
You supply only the parts that are specific to your application.
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
You covered a lot of ground without writing much code. You now know:

- A **backend** is a program that waits for HTTP **requests** and sends back **responses**, usually as **JSON**.
- A **framework** runs the program and calls your code: **inversion of control**. A library is something you call.
- **Spring** gives you a container that creates and connects your objects. **Spring Boot** adds **starters**,
  **auto-configuration** and an **embedded Tomcat** server, so one line starts everything.
- Spring began with Rod Johnson's 2002 book; **Spring 1.0** came in 2004 and **Spring Boot 1.0** in 2014. Today it
  runs backends in banking, shopping, travel and much more.
- A Spring Boot project has a `pom.xml` (what it needs), a main class (`SpringApplication.run`) and
  `application.properties` (its settings).
- You built and ran a real server, saw it answer 404, and gave it a name.

:::photo{src="/lesson-images/spring/spring-00-notes.webp" alt="Sketchnote: What is Spring Boot? A backend waits for requests and sends responses. Spring Boot gives you starters, auto-configuration and an embedded web server. Flow from pom.xml to one run call to Tomcat on port 8080 to a request answered. Remember: the framework calls your code; settings live in application.properties." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 1 takes a proper look at HTTP and JSON: the language your server speaks.
:::
