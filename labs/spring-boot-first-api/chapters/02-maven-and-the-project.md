:::step{type=story title="Where your code comes from"}
You have run a Spring Boot app twice now. Each time, you typed `mvn ... package` and then `java -jar`
on a file in `target/`. But where did Spring itself come from? Your project has a handful of files, yet
the running app used Tomcat, Jackson, Spring and dozens of other libraries. Who downloaded them, chose
their versions, and packed them together?

That is the job of **Maven**, the build tool. Every Spring Boot project is described by one file,
`pom.xml`, and once you can read it, you are in control of your project: which libraries it uses, which
Java version, what the final file is called. This chapter goes through it slowly, piece by piece, and
then you will change it yourself: add a library and watch a new feature appear.

:::mission
Understand the pom.xml and the project folders, add the Actuator starter, and give the project its real name.
:::
:::

:::step{type=concept title="Why a build tool at all?"}
Imagine building a Java web app by hand. You would need to:

1. Find and download Spring, Tomcat, Jackson and their own dependencies (Spring alone needs several other
   libraries, and *those* need others). For our tiny app, that is **30 separate jar files** (we counted them in the
   built app on our lab machine).
2. Make sure all their **versions fit together**. A Jackson version that is too new for your Spring
   version can fail in strange ways at run time.
3. Compile your `.java` files with all those jars on the **classpath**: the list of folders and jar files where
   Java looks for classes. If a library is not on the classpath, your code cannot use it.
4. Run your tests.
5. Pack everything into something you can ship and run on a server.

And repeat it, identically, on every developer's laptop and on the build server. Doing this by hand is
slow and fragile.

A **build tool** does all of it from one description of your project. In the Java world the two common ones are
**Maven** (version 1.0 came out in 2004; it uses the `pom.xml` file) and **Gradle** (2012; it uses
`build.gradle`). Both are fine, and Spring supports both. This course uses Maven, which many companies use.
:::

:::step{type=concept title="The pom.xml: who this project is" file="02-maven-and-the-project/pom.xml" line="12-18"}
`pom.xml` has opened on the right. POM stands for **Project Object Model**: a description of the
project, written in XML. XML is a format of nested tags, like `<name>value</name>`; you do not need to
know more about it than that.

The highlighted lines say **who this project is**. Every Maven project in the world is identified by
three values, its **coordinates**:

- `groupId`: the organisation or area it belongs to. Ours is `com.shop`. By convention it is a reversed
  domain name, like a Java package.
- `artifactId`: the project's own name. Right now it says `demo`. That is wrong, and you will fix it.
- `version`: which release. Ours is `1.0`.

Together, `com.shop:demo:1.0` names this project uniquely. Every library you use is named the same way:
Spring's web module, for example, is `org.springframework:spring-web:6.2.1`.

Below them, `<properties>` holds settings for the build. `java.version` 21 means "compile this project
for Java 21".
:::

:::step{type=concept title="The parent: versions chosen for you" file="02-maven-and-the-project/pom.xml" line="6-11"}
Now the `<parent>` block at the top. This is the most useful line in a Spring Boot project, and the
easiest to overlook.

A parent is another pom that this one **inherits from**. Ours inherits from
`spring-boot-starter-parent`, version `3.4.1`. That parent contains a long, carefully tested list of
**versions** for hundreds of libraries: which Tomcat, which Jackson, which database driver, which test
library. They have all been tested together by the Spring team for Spring Boot 3.4.1.

That is why, further down, our dependencies have **no `<version>` line**. We do not have to choose; the
parent already did. When you upgrade Spring Boot one day, you change this single `3.4.1`, and every
library moves to versions that fit the new release. Without the parent, you would be choosing and
checking dozens of versions by hand.
:::

:::step{type=concept title="Dependencies and starters" file="02-maven-and-the-project/pom.xml" line="19-30"}
Now the `<dependencies>` section: the libraries this project needs. Each `<dependency>` gives the
coordinates of one library (minus the version, thanks to the parent).

There are two here, and both are **starters**:

- `spring-boot-starter-web`: everything for a web API.
- `spring-boot-starter-test`: everything for writing tests. Its `<scope>test</scope>` means "only while
  compiling and running tests". It is left out of the final app.

A starter is a library that contains almost no code itself. It is a **bundle**: depending on it pulls in a
whole set of other libraries. Those come in automatically, and so do *their* dependencies. These are
called **transitive dependencies**: you asked for one, and you got everything it needs.

Between the two, you can see the TODO for your first task. Hold on to it; first let's see what the web
starter actually brought in.
:::

:::step{type=example title="What one starter really pulls in"}
Maven can draw the full tree of dependencies. Run this in the terminal (it reads the project, it does not
change anything):

```bash run
cd 02-maven-and-the-project && mvn -o -q dependency:tree -Dscope=compile -DoutputFile=/dev/stdout
```

The parts: `dependency:tree` asks Maven's dependency plugin to draw the tree; `-Dscope=compile` keeps only the
libraries the app itself uses (it leaves out the test tools); `-DoutputFile=/dev/stdout` prints the tree in the
terminal instead of into a file.

Here is part of what it printed on our lab machine (the full tree is 31 lines; we left some out):

```text
com.shop:demo:jar:1.0
+- org.springframework.boot:spring-boot-starter-web:jar:3.4.1:compile
|  +- org.springframework.boot:spring-boot-starter:jar:3.4.1:compile
|  |  +- org.springframework.boot:spring-boot:jar:3.4.1:compile
|  |  +- org.springframework.boot:spring-boot-autoconfigure:jar:3.4.1:compile
|  |  +- org.springframework.boot:spring-boot-starter-logging:jar:3.4.1:compile
|  |  |  +- ch.qos.logback:logback-classic:jar:1.5.12:compile
|  |  |  ...
|  +- org.springframework.boot:spring-boot-starter-json:jar:3.4.1:compile
|  |  +- com.fasterxml.jackson.core:jackson-databind:jar:2.18.2:compile
|  |  ...
|  +- org.springframework.boot:spring-boot-starter-tomcat:jar:3.4.1:compile
|  |  +- org.apache.tomcat.embed:tomcat-embed-core:jar:10.1.34:compile
|  |  ...
|  +- org.springframework:spring-web:jar:6.2.1:compile
|  |  ...
|  \- org.springframework:spring-webmvc:jar:6.2.1:compile
|     ...
```

Each line is `group:artifact:jar:version:scope`. The `+-` and `\-` marks are branches: a line indented under
another is a library that the one above needed.

Read it like a family tree. The web starter brought:
- **spring-boot** and **spring-boot-autoconfigure**: Spring Boot itself.
- **logback**: the library that writes the log lines you saw at start-up.
- **jackson-databind**: the JSON library that turns Java objects into JSON and back.
- **tomcat-embed-core**: the web server that runs inside your app.
- **spring-web** and **spring-webmvc**: Spring's web layer, which you will use from the next chapter.

One entry in your pom; a whole web stack in your project. (The `-o` option means **offline**: your lab machine
already has every library downloaded, so Maven does not need the internet. On your own computer, the first build
downloads them from **Maven Central**, the public online store of Java libraries, and keeps them in a folder
called `~/.m2` (`~` means your home folder), so later builds do not download them again.)
:::

:::step{type=concept title="The folders of a Maven project"}
Maven expects files in fixed places. Once you know them, you can find your way around any Java project in
the world, because they all look the same:

```text
02-maven-and-the-project/
  pom.xml                         the project description
  src/main/java/                  your Java code (in package folders: com/shop/...)
  src/main/resources/             non-Java files the app needs: application.properties, static files
  src/test/java/                  your tests
  target/                         everything Maven produces (created by the build; never edit it)
```

Two rules worth remembering:

- **The folder must match the package.** A class in `package com.shop;` lives in
  `src/main/java/com/shop/`. Java insists on this.
- **Never edit or commit `target/`.** It is output. Delete it any time; the next build recreates it.
  (`mvn clean` does exactly that.)

Look at the file tree on the left of the editor: you can see this exact layout in every chapter folder.
:::

:::step{type=concept title="Building: phases and the jar"}
When you type `mvn package`, Maven runs a sequence of **phases**, in order, each building on the last. Maven's
standard build has more than twenty phases; these four are the ones you meet every day:

1. **validate**: is the pom correct?
2. **compile**: turn `src/main/java` into `.class` files (compiled Java) in `target/classes`. Files from
   `src/main/resources` are copied there too, just before.
3. **test**: compile and run the tests in `src/test/java`. If a test fails, the build stops here.
4. **package**: pack everything into a **jar** file in `target/`.

Asking for a phase runs all the phases before it. So `mvn package` validates, compiles, tests and
packages. That is why you have been typing `-DskipTests`: it skips running tests, to start faster while
learning. And `-q` (quiet) hides Maven's own chatter, so you see only problems.

The plugin in `<build>` matters here: **spring-boot-maven-plugin** makes the jar special. A normal jar
contains only your classes. Spring Boot's plugin builds a **fat jar** (also called an "uber jar"): your
classes *plus all 30 libraries inside it*. That is why `java -jar` on that one file is enough to run a
complete web server, anywhere Java is installed. The `<finalName>` decides the jar's file name.
:::

:::step{type=try title="Look inside the jar"}
Let's prove the fat-jar claim. Build the project, then list what is inside the jar (a jar is just a zip
file):

```bash run
mvn -q -o package -DskipTests && ls -l target/*.jar && jar tf target/demo.jar | grep "BOOT-INF/lib/" | head -12
```

On our lab machine this printed a jar of 20,671,846 bytes (about 20 MB) called `demo.jar` (because the
finalName says `demo`). Inside it, the `BOOT-INF/lib/` folder held 30 libraries, starting with
`spring-boot-3.4.1.jar`, `spring-boot-autoconfigure-3.4.1.jar` and `logback-classic-1.5.12.jar`. Your own classes
are in `BOOT-INF/classes/`. Everything the app needs, in one file.

The command in parts: `ls -l target/*.jar` lists the jar with its size in bytes; `jar tf` lists the files inside
a jar; `grep "BOOT-INF/lib/"` keeps only the library lines; `head -12` shows the first twelve.

:::diagram{name="fat-jar"}
What our lab machine found inside demo.jar: your code, 30 libraries, Spring Boot's launcher, and the manifest.
:::
:::

:::step{type=example title="Adding a dependency: the Actuator"}
Now you will change the project. The library to add is **Spring Boot Actuator**, which gives a running
app some built-in **operational endpoints**. The most famous is `/actuator/health`: it answers `UP` when
the app is healthy. Real servers use it all the time, for example so a load balancer knows whether to
send traffic to this copy of the app. (Chapter 27 covers it in depth.)

To add a library, you add a `<dependency>` block with its coordinates. For a Spring Boot starter, the
group is always `org.springframework.boot`, and the artifact is the starter's name. Here is what adding
a different starter, the validation one, would look like:

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

No version, because the parent picks it. Save the pom, build again, and the new library (and everything it brings)
is in your project. And here is the Spring Boot part: you do not write any code to use the Actuator. Its jar is
on the classpath, so auto-configuration notices it at start-up and switches it on. (On our lab machine, adding it
grew the jar from 30 libraries to 36, and from about 20 MB to about 23 MB.)
:::

:::step{type=task task=add_actuator title="Your turn: add the Actuator starter"}
In `02-maven-and-the-project/pom.xml`, at the TODO, add the dependency for the Actuator starter. Its
artifactId is `spring-boot-starter-actuator`.

Then try it: build and run, and in a second terminal ask for the health:

```bash run
mvn -q -o package -DskipTests && java -jar target/demo.jar
```

```bash run
curl -i localhost:8080/actuator/health
```

On our lab machine the answer was:

```text
HTTP/1.1 200
Content-Type: application/vnd.spring-boot.actuator.v3+json
...
{"status":"UP"}
```

`200` and `{"status":"UP"}`: the app is healthy. The odd-looking Content-Type is still JSON; it is the Actuator's
own name for its version 3 format. At start-up the log also said `Exposing 1 endpoint beneath base path
'/actuator'`: by default only the health endpoint is open over the web (chapter 27 opens more). You did not write
a single line of Java for any of it.

Stop the app with Ctrl+C in Terminal 1, then press **Check**.

Usual slips: the dependency written outside `<dependencies>`, or with a `<version>` that does not match the
parent (leave the version out). And if an app from an earlier chapter is still running in another terminal, the
new one stops at start-up with `Web server failed to start. Port 8080 was already in use.`, and your curl reaches
the *old* app instead (which answers 404 for `/actuator/health`). Stop the old one with Ctrl+C first.
:::

:::step{type=task task=project_identity title="Your turn: give the project its real name"}
The project is still called `demo`, so its jar is `demo.jar`. In the same `pom.xml`, change two things:

- the project's own `<artifactId>` (under `<groupId>com.shop</groupId>`, not the one inside `<parent>`!)
  from `demo` to `shop-api`;
- the `<finalName>` inside `<build>` from `demo` to `shop-api`.

Build again: `target/shop-api.jar` appears. Press **Check**.

Usual slip: changing the `<artifactId>` inside `<parent>` (that one must stay `spring-boot-starter-parent`, or
Maven cannot find the parent and the build fails).
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why do the dependencies in our pom have no `<version>` line?
:::
- [ ] Maven always picks the newest version
- [x] The spring-boot-starter-parent already defines tested versions for them
- [ ] Versions are optional for all Maven dependencies
:::explain
The parent carries a list of versions tested together for Spring Boot 3.4.1. Outside a parent like this,
you would have to write the version yourself.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
You run `mvn package` and one test fails. What happens?
:::
- [ ] The jar is built anyway, with a warning
- [x] The build stops at the test phase; no new jar is made
- [ ] Maven skips the failing test and carries on
:::explain
Phases run in order, and package comes after test. A failing test stops the build, which is exactly what
you want: broken code never gets packaged. (`-DskipTests` skips running the tests altogether.)
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A class starts with `package com.shop.orders;`. Where must its file be?
:::
- [ ] src/main/resources/com/shop/orders/
- [x] src/main/java/com/shop/orders/
- [ ] src/com.shop.orders/
:::explain
Java code goes under `src/main/java`, and the folders must match the package name, one folder per dot.
:::
:::

:::step{type=deep-dive title="Go deeper: the Maven wrapper, start.spring.io and Gradle"}
**The Maven wrapper.** Many projects include files called `mvnw` and `mvnw.cmd`. They are a tiny script
that downloads the exact Maven version the project expects, so nobody needs Maven installed. You run
`./mvnw package` instead of `mvn package`. Our lab machine has Maven installed, so we use `mvn` directly.

**start.spring.io.** In real life, you rarely write a pom from scratch. The **Spring Initializr** at
start.spring.io lets you pick a build tool, a Java version and the starters you want, and downloads a
ready project with the pom, the main class and the folders. Every project in this course looks just like
what it generates.

**Gradle** does the same job as Maven with a different file (`build.gradle`, written in Groovy or Kotlin
instead of XML). The ideas are identical: coordinates, dependencies, a Spring Boot plugin that builds a
fat jar. If you can read a pom, you can read a build.gradle in an afternoon.

**Useful commands:** `mvn clean` deletes `target/`; `mvn test` runs only up to the tests;
`mvn spring-boot:run` builds and runs the app in one go.
:::

:::step{type=recap title="What you can do now"}
You can now read and change the heart of any Spring Boot project:

- A **build tool** downloads libraries, compiles, tests and packages, the same way everywhere.
- The **pom.xml** gives the project's **coordinates** (groupId, artifactId, version), its Java version,
  its **dependencies** and its build **plugins**.
- The **spring-boot-starter-parent** chooses tested versions, so your dependencies need none.
- A **starter** is a bundle; its libraries arrive as **transitive dependencies** (`mvn dependency:tree`).
- Projects follow fixed folders: `src/main/java`, `src/main/resources`, `src/test/java`, and `target/`
  for output.
- `mvn package` runs the phases up to package (validate, compile, test, package are the main ones); Spring Boot's
  plugin makes a **fat jar** that runs with `java -jar`.
- You added the Actuator, and a health endpoint appeared without any Java code.

:::photo{src="/lesson-images/spring/spring-02-notes.webp" alt="Sketchnote: Maven and the pom.xml. The pom describes the project and the libraries it needs. Flow: pom.xml, download libraries, compile and test, a fat jar. Remember: the parent picks tested versions; a starter is a bundle of libraries; code in src/main/java, tests in src/test/java; target/ is output." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 3: your first endpoints. You will write the Java side of the HTTP conversations from chapter 1.
:::
