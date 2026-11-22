:::step{type=story title="Welcome to Java"}
Java runs banks, airline bookings, Android's foundations and the back ends of huge websites. It has a
reputation for being "big", but every large Java program is built from one small idea you will learn
right now: the **method**, a named piece of code that does one job.

:::mission
Write two small methods in `Greeter.java`: one builds a greeting, and one finds the longest word in a
sentence. Real tests check each one.
:::
:::

:::step{type=history title="The story of Java"}
Java began as a language for television set-top boxes and ended up running much of the world's
business software.

:::before{title="Before Java"}
In the early 1990s, most programs were written in **C** and **C++**. A program had to be compiled
separately for every kind of computer and operating system, so shipping software to many devices meant
many builds. And C and C++ let programs work with raw memory directly: one wrong pointer could crash
the program, or worse, quietly corrupt its data.
:::

:::solved
**"Write once, run anywhere."** Java programs compile to **bytecode**, which runs on the **Java Virtual
Machine (JVM)**, so the same program runs on Windows, Linux or a phone without being rebuilt. Java also
manages memory for you with a **garbage collector**, removing a whole family of crashes.
:::

Java was created by **James Gosling** and a small team at **Sun Microsystems**. Since Sun was bought in
2010, **Oracle** has led its development, together with a large community in the open-source
**OpenJDK** project.

:::timeline
- **1991** James Gosling's "Green" team starts a language for smart devices, first called Oak.
- **1996** Java 1.0 is released, renamed after the coffee because "Oak" was taken.
- **2007** Sun releases Java as open source (OpenJDK).
- **2014** Java 8 adds lambdas and streams, the biggest change in its history.
- **2017** Java moves to a new release every six months.
:::

:::usedby{title="Industries"}
- Banking and finance
- Enterprise back ends
- Android's foundations
- Big data
- E-commerce
- Government systems
:::

:::usedby{title="Used at"}
- Netflix
- LinkedIn
- Amazon
- Uber
- Minecraft (Java Edition)
- Apache Kafka
:::

:::funfact
Java's mascot is **Duke**, a little black-and-white figure with a red nose, drawn by Joe Palrang at Sun.
And the source of Java's name really is coffee: Java is an island in Indonesia famous for it.
:::
:::

:::step{type=concept title="Why methods exist"}
Imagine writing the same five lines every time you want to greet a customer. If the greeting ever
changes, you would have to find and fix every copy.

A **method** solves this. You write the steps **once**, give them a name, and then use that name
whenever you need them. Change the method, and every place that uses it changes too.

Think of a method like a **recipe card**: it has a name ("Lemon rice"), a list of things it needs
(rice, lemon), and a result (a plate of lemon rice). You do not rewrite the recipe each morning; you
follow the card.

:::picture{name="recipe-card"}
The same four parts, on a card and in a method.
:::
:::

:::step{type=concept title="A method, part by part"}
Here is a complete Java method:

```java
public static int square(int x) {
    return x * x;
}
```

Read it from left to right:

- `public` means other code may use it.
- `static` means you can call it without creating an object first (more on objects in chapter 7).
- `int` before the name is the **return type**: this method hands back a whole number.
- `square` is the **name**.
- `(int x)` is the **input**: one whole number, called `x` inside the method.
- `return x * x;` sends the answer back to whoever called it.

`square(4)` gives back `16`.
:::

:::step{type=concept title="Methods live in classes"}
In Java, every method lives inside a **class**, a named container for related code. `Greeter.java`
holds a class called `Greeter`, so its methods are used as `Greeter.greet(...)`.

The file name and the class name must match exactly, capital letters included: class `Greeter` lives
in `Greeter.java`. If they differ, Java refuses to compile.

:::mistake
Java is **case-sensitive**: `greet`, `Greet` and `GREET` are three different names. Keep method names
starting with a small letter and class names with a capital, like the code you see here.
:::
:::

:::step{type=example title="Worked example: a method that builds text"}
A complete method that returns text, line by line:

```java
public static String welcome(String city) {
    return "Welcome to " + city + "!";
}

// welcome("Pune") gives "Welcome to Pune!"
```

1. `String` before the name says the method hands back **text** (Java calls text a String).
2. `(String city)` is the input: a piece of text called `city`.
3. `+` joins pieces of text together: `"Welcome to "` then the city then `"!"`.
4. `return` hands the finished text back.

Your first task has exactly this shape, with different words.
:::

:::step{type=predict title="Guess first"}
:::question
Open `Greeter.java`. Right now `greet` says `return null;`. What does `main` print?
:::
- [ ] `Hello, Asha!`
- [ ] Nothing at all
- [x] `null`
- [ ] It does not compile
:::explain
`null` means "no object at all". It is a valid value for any text, so the code compiles, and
`System.out.println` prints a `null` String as the word `null`. That is why the starter does not pass
yet: it gives back nothing useful.
:::
:::

:::step{type=try title="Compile and run"}
The terminal at the bottom is a real Linux machine with your files in `/workspace`. Java runs in two
steps: `javac` **compiles** your code (checks it and turns it into bytecode), then `java` **runs** it.

```bash run
javac Greeter.java && java Greeter
```

You should see `null`. Once `greet` works, the same command prints `Hello, Asha!`.
:::

:::step{type=task task=greet title="Warm-up: greet someone"}
Make `greet(name)` return `"Hello, <name>!"`.

For example, `greet("Asha")` returns `"Hello, Asha!"`. Mind the comma, the space and the
exclamation mark: the tests compare the text exactly.

:::why
Returning the text (instead of printing it) lets other code reuse it: a web page, a message, or the
tests that check your work.
:::
:::

:::step{type=concept title="Splitting a sentence into words"}
Your second method needs to look at a sentence one word at a time. Two new tools make that possible:

```java
String[] words = "big kirana store".split(" ");
// words is ["big", "kirana", "store"]

for (String w : words) {
    System.out.println(w.length());
}
// prints 3, then 6, then 5
```

- `split(" ")` cuts the text at every space and gives back an **array** of words (a numbered list;
  chapter 6 is all about arrays).
- `for (String w : words)` repeats the block once **for each** word, calling the current one `w`.
- `w.length()` is how many characters the word has.
:::

:::step{type=example title="Worked example: the shortest word"}
Keep the "best so far" while you look at each word:

```java
public static int shortestWord(String sentence) {
    int best = Integer.MAX_VALUE;   // 1. bigger than any word
    for (String w : sentence.split(" ")) {
        if (w.length() < best) {    // 2. shorter?
            best = w.length();      // 3. keep it
        }
    }
    return best;
}
```

1. Start with a value no real word can beat.
2. Compare each word with the best so far.
3. Keep it when it wins.

:::trace{title='shortestWord("big kirana store")'}
| w | w.length() | best | note |
|---|---|---|---|
|  |  | huge | Before the loop: best starts bigger than any word could be. |
| big | 3 | 3 | 3 is shorter than huge, so best becomes 3. |
| kirana | 6 | 3 | 6 is not shorter than 3: best stays 3. |
| store | 5 | 3 | 5 is not shorter than 3: best stays 3. |
|  |  | 3 | No words left: the method returns 3. |
:::

`longestWord` is the mirror image: start small and keep the **longer** one.
:::

:::step{type=task task=longest_word title="The longest word"}
Make `longestWord(sentence)` return the **length** of the longest word, with words separated by spaces.

- `longestWord("big kirana store")` returns `6`
- `longestWord("hi")` returns `2`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`public static int twice(int n) { return n * 2; }` What does `twice(7)` give back?
:::
- [ ] `7`
- [x] `14`
- [ ] `72`
- [ ] Nothing: it does not print anything
:::explain
`n` is 7 inside the method and `return n * 2` hands back `14`. A method can give back a value without
printing anything: the caller decides what to do with it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Class `Shop` is saved in a file called `shop.java`. What happens when you compile it?
:::
- [ ] It compiles fine
- [x] An error: the file must be called `Shop.java`
- [ ] Java renames the file for you
- [ ] It compiles, with a warning
:::explain
A public class must live in a file with exactly its name, capital letters included. It is one of the
first rules every Java developer meets.
:::
:::

:::step{type=deep-dive title="What javac and the JVM really do"}
`javac` turns your `.java` file into a `.class` file of **bytecode**: instructions for an imaginary
computer, the Java Virtual Machine. When you run `java Greeter`, the JVM loads that bytecode and, as it
runs, a **just-in-time (JIT) compiler** turns the busiest parts into real machine code for your CPU.
That is how Java is portable **and** fast.

Since Java 11 you can skip the separate compile step for a single file: `java Greeter.java` compiles in
memory and runs it. Real projects still compile with build tools like **Maven** or **Gradle**, which
also download libraries and run tests.
:::

:::step{type=recap title="Chapter done"}
- A method is a named piece of code: return type, name, inputs, body.
- `return` hands a value back to whoever called the method.
- Every method lives in a class; the file name matches the class name exactly.
- `javac` compiles and `java` runs; `split` and a for-each loop look at words one by one.
:::
