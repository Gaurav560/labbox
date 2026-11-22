:::step{type=story title="How does a program with ten thousand files stay tidy?"}
Shelf has grown chapter by chapter, but each folder is still a little pile of files with no names for its
neighbourhoods. Real Java programs are huge: a bank's code can have ten thousand classes, and some of them are
bound to be called `Account` or `Report`. How does Java know which `Report` you mean?

The answer has three parts, and every professional Java project uses all three:

- **packages** give every class a full name, like a postal address;
- **jar files** pack a whole program into one file you can hand to someone;
- **Maven** builds it all with one command, and fetches other people's libraries for you.

Today Shelf becomes a real project, with the exact folder layout used by Spring Boot and nearly every Java
codebase in the world.


Shipping had the same problem, and solved it with one idea: the **standard container**. Every box is the same shape,
labelled with where it goes, so any crane and any ship can handle any cargo. Packages give classes an address; a jar
is the box they travel in.

:::photo{src="/lesson-images/java/container-ship.webp" alt="A large blue container ship loaded with stacked shipping containers, beside cranes at a port" credit="Petar Milošević" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:MAERSK_HANOI_Container_Ship_(Port_Koper_SIKOP,_2023).jpg"}
A container ship at the port of Koper: standard boxes, labelled, ready for any crane.
:::
:::mission
Move `Catalog` into its own package so the project builds, then make the jar start with a plain `java -jar`.
:::
:::

:::step{type=concept title="A package is a class's address" file="16-packages-and-maven/src/main/java/shelf/App.java" line="2-8"}
Open `src/main/java/shelf/App.java`:

```java
package shelf;

import shelf.catalog.Catalog;

public class App {
    public static void main(String[] args) {
        Catalog catalog = new Catalog();
```

- `package shelf;` is the first line of code: this class lives in the package `shelf`. Its full name is
  `shelf.App`.
- `import shelf.catalog.Catalog;` says: when I write `Catalog`, I mean the one in the package `shelf.catalog`.
  You have used `import java.util.List;` since chapter 8, and that was exactly this: `List` lives in the package
  `java.util`.

And here is Java's strict rule: **the folders must spell the package**, one folder per dot.

| Full class name | File |
|---|---|
| `shelf.App` | `src/main/java/shelf/App.java` |
| `shelf.catalog.Catalog` | `src/main/java/shelf/catalog/Catalog.java` |
| `java.util.List` | inside Java itself, in `java/util/` |

Big companies start their packages with their web address backwards (`com.google...`, `org.apache...`), so two
companies can never pick the same full name.
:::

:::step{type=try title="A build that cannot find a package"}
Maven is already installed. Build the project:

```bash run
cd /workspace/16-packages-and-maven && mvn -o -q package
```

```text
[ERROR] COMPILATION ERROR : 
[ERROR] /workspace/16-packages-and-maven/src/main/java/shelf/App.java:[4,21] package shelf.catalog does not exist
[ERROR] /workspace/16-packages-and-maven/src/main/java/shelf/App.java:[8,9] cannot find symbol
  symbol:   class Catalog
  location: class shelf.App
```

Read it the way chapter 1 taught: file `App.java`, line 4, column 21, `package shelf.catalog does not exist`. `App`
imports `shelf.catalog.Catalog`, but `Catalog.java` sits loose in `src/main/java/` with no package at all.

`-o` means **offline**: LabBox machines have no internet, and everything Maven needs is already stored on this
machine. `-q` (quiet) shows only problems.
:::

:::step{type=example title="Worked example: moving a class into a package"}
Say a class `Report.java` sits loose in `src/main/java/` and should live in the package `shelf.reports`. Two
changes, and both are needed:

```bash
mkdir -p src/main/java/shelf/reports
mv src/main/java/Report.java src/main/java/shelf/reports/
```

and the first code line of `Report.java` becomes:

```java
package shelf.reports;
```

1. `mkdir -p` makes the folders, and the parents too if they are missing.
2. `mv` moves the file. The folder now spells `shelf/reports`.
3. The `package` line must say the same thing. Folder without the line, or the line without the folder, and
   `javac` complains.

A class used from another package must also be `public`, and so must the methods it calls. `Catalog` already is.
:::

:::step{type=task task=package_catalog title="Your turn: Catalog moves into shelf.catalog"}
Put `Catalog` into the package `shelf.catalog`:

- move `src/main/java/Catalog.java` into `src/main/java/shelf/catalog/`;
- give it the right `package` line at the top.

Then build again:

```bash run
cd /workspace/16-packages-and-maven && mvn -o -q package && ls target
```

No `ERROR` lines, and `target` now holds `shelf.jar` and a `classes` folder. Then press **Check**.
:::

:::step{type=concept title="Maven: one command, a standard layout"}
Before Maven (2004), every Java project had its own home-made build script, and every new developer spent their
first week learning it. Maven's idea was **convention**: put your files where everyone puts them, and one command
builds anything.

| Where | What |
|---|---|
| `pom.xml` | the project's description: its name, Java version, libraries and plugins |
| `src/main/java/` | your code, in package folders |
| `src/test/java/` | tests (chapter 17) |
| `target/` | everything Maven makes; delete it any time |

`pom.xml` stands for Project Object Model. Its `<dependencies>` section is Maven's superpower: write a library's
name and version, and Maven downloads it, and everything it needs, from **Maven Central**, a public store of
millions of Java libraries. Spring Boot projects are Maven projects exactly like this one.

`mvn package` runs a fixed series of **phases** in order: compile the code, run the tests, then package the result
into a jar. (The name Maven is Yiddish for "one who knows".)
:::

:::step{type=try title="What is inside a jar?"}
A jar (Java ARchive) is really a zip file of `.class` files. Look inside:

```bash run
cd /workspace/16-packages-and-maven && jar tf target/shelf.jar
```

```text
META-INF/
META-INF/MANIFEST.MF
shelf/
shelf/catalog/
META-INF/maven/
META-INF/maven/com.labbox/
META-INF/maven/com.labbox/shelf/
shelf/catalog/Catalog.class
shelf/App.class
META-INF/maven/com.labbox/shelf/pom.xml
META-INF/maven/com.labbox/shelf/pom.properties
```

The package folders again, now holding compiled classes. Run the program from the compiled classes by its full
name:

```bash run
cd /workspace/16-packages-and-maven && java -cp target/classes shelf.App
```

```text
Shelf 1.0: 2 books
```

Now try the way people expect to start a program they were given:

```bash run
cd /workspace/16-packages-and-maven && java -jar target/shelf.jar
```

```text
no main manifest attribute, in target/shelf.jar
```

The jar holds two classes, and `java -jar` has no idea which one has the `main` to start.
:::

:::step{type=predict title="Guess first"}
:::question
`MANIFEST.MF` is a small text file inside every jar. What line would let `java -jar` start the program?
:::
- [ ] `Start: main`
- [x] `Main-Class: shelf.App`
- [ ] `Main-Class: App.java`
:::explain
The manifest names the class with `main`, by its full name: package, a dot, and the class, with no `.java`.
:::
:::

:::step{type=task task=runnable_jar title="Your turn: a jar that starts by itself" file="16-packages-and-maven/pom.xml" line="28"}
In `pom.xml`, the `maven-jar-plugin` writes the manifest, and its `<mainClass>` is empty. Fill it in, so that

```bash run
cd /workspace/16-packages-and-maven && mvn -o -q package && java -jar target/shelf.jar
```

prints

```text
Shelf 1.0: 2 books
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A class starts with `package shelf.loans;` and is called `Renewal`. Where must its file be, under `src/main/java`?
:::
- [ ] `loans/Renewal.java`
- [x] `shelf/loans/Renewal.java`
- [ ] `shelf.loans/Renewal.java`
:::explain
One folder per dot of the package: `shelf`, then `loans`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `mvn -o -q package` mean?
:::
- [x] Build the project into a jar, offline, showing only problems
- [ ] Download every library from the internet
- [ ] Run the program
:::explain
`package` compiles, tests and makes the jar; `-o` stays offline and `-q` keeps it quiet.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Which folder can you delete without losing any work?
:::
- [ ] `src/main/java`
- [x] `target`
- [ ] the folder holding `pom.xml`
:::explain
`target` only holds what Maven made from your files. `mvn package` makes it again.
:::
:::

:::step{type=deep-dive title="Go deeper: access between packages, Gradle and the class path"}
**Package-private.** A class, method or field with no `public` or `private` is visible only inside its own
package. That is the quiet default, and a good one: make public only what other packages need.

**Gradle.** The other big Java build tool, used by Android. It describes the build in code instead of XML, but the
folders and the ideas are the same.

**The class path.** `-cp` (chapter 10) is a list of folders and jars where Java looks for classes. Maven builds the
class path for you from the dependencies in `pom.xml`, which is why real projects rarely type `-cp` by hand.

**Fat jars.** `shelf.jar` holds only Shelf's own classes. A Spring Boot jar also packs every library inside, so one
file runs the whole application anywhere Java is installed.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Give a class a package and put its file in the matching folders, and import it from another package.
- Build a project with `mvn -o -q package`, using Maven's standard layout and `pom.xml`.
- Look inside a jar with `jar tf`, and run classes by their full name.
- Make a jar runnable with `java -jar` by naming its main class.

:::photo{src="/lesson-images/java/java-16-notes.webp" alt="Handwritten notes about packages and Maven: package shelf.catalog lives in shelf/catalog, import by full name, mvn -o -q package, src/main/java, target can be deleted, mainClass for java -jar" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 17: tests with JUnit, so Shelf can prove it works, every time anything changes.
:::
