:::step{type=story title="What does a computer actually read?"}
Here is something most people never find out: a computer cannot read Java. Not one word of it. Its processor
only understands long lists of tiny numbered instructions, and those instructions are different on a laptop, a
phone and a bank's server.

So how can one Java program run on all of them, unchanged? There is a clever trick in the middle, and by the end
of this chapter you will have seen it with your own eyes, down to the four secret bytes at the start of every
Java file.

In this course you will build **Shelf**, a small library app: books, members, loans and late fees. Today Shelf
learns to talk.

:::photo{src="/lesson-images/java/duke.webp" alt="Duke, the Java mascot: a black and white figure with a red nose, waving" credit="Sun Microsystems, converted by sbmehta" license="BSD" source="https://commons.wikimedia.org/wiki/File:Duke_(Java_mascot)_waving.svg"}
Meet Duke, Java's mascot since the 1990s. He waves at you from Java conferences, stickers and T-shirts all over the world.
:::

:::mission
Make Shelf say its first two sentences, then find and fix two mistakes in a program that refuses to run.
:::
:::

:::step{type=history title="The story of Java"}
Java is one of the most used programming languages in the world. It started with a small team, a big idea and
a tree.

:::before{title="Before Java"}
In the early 1990s, most serious programs were written in **C** and **C++**. They were fast, but a program had to
be rebuilt separately for every kind of computer (each kind of processor understands different instructions), and
the programmer managed memory by hand, so one memory mistake could crash it. At Sun Microsystems in
California, a small team led by **James Gosling** (the "Green Project", started in 1991) wanted to program all
kinds of devices, from TV set-top boxes to handheld gadgets, and C++ made that painful.
:::

:::solved
A language that is **compiled** (translated, before running) once into a **neutral, portable form** called
**bytecode**, and then run by a program called the **Java Virtual Machine** (JVM), which exists for every kind of
computer. The bytecode is the same everywhere; only the JVM differs. Sun's slogan was **"Write once, run anywhere"**.
Java also manages memory for you, so a whole family of crashes simply disappears.
:::

:::photo{src="/lesson-images/java/james-gosling.webp" alt="James Gosling, the creator of Java, speaking at a seminar in 2008" credit="Peter Campbell" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:James_Gosling_2008.jpg"}
James Gosling, who led the team that created Java, in 2008.
:::

:::timeline
- **1991** The Green Project starts at Sun. The language is first called **Oak**.
- **1995** Renamed **Java** and announced to the world.
- **1996** JDK 1.0, the first official release.
- **2006** Sun begins releasing Java as open source (**OpenJDK**).
- **2010** Oracle completes its purchase of Sun and becomes Java's steward (the company that leads it).
- **2014** Java 8 adds lambdas and streams (you will use both in this course).
:::

Today Java is developed in the open by the **OpenJDK** community, led by Oracle with many other companies, and a
new version comes out every six months. Every two years one becomes a **long-term support** (LTS) release, kept
up to date with fixes for years; your lab runs **Java 21** (released in 2023), one of those.

:::usedby{title="Industries"}
- Banking and payments
- Large web backends
- Android apps
- Big data
- Telecom
- Games
:::

:::usedby{title="Used at"}
- Netflix
- Amazon
- LinkedIn
- Uber
- Most big banks
- Minecraft (Java Edition)
:::

:::funfact
Java's first name, Oak, came from an oak tree that stood outside James Gosling's office. The name was already
taken by another company, so the team picked a new one in a brainstorm: Java, a name borrowed from the island of Java in Indonesia. And every compiled
Java file still starts with four bytes that spell a joke in hexadecimal: **CA FE BA BE**. You will see them
yourself in this chapter.
:::

:::photo{src="/lesson-images/java/oak-tree.webp" alt="A single oak tree on a green hill in California" credit="Daniel Lu (dllu)" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Oak_tree_Sunol_Regional_Wilderness_California_2023_dllu.jpg"}
An oak tree in California, not far from where Java was born. Java was almost called Oak.
:::
:::

:::step{type=concept title="Meet the terminal"}
Look at the bottom of your screen. That dark box is the **terminal**: a way to talk to a computer by typing
instructions instead of clicking. It is a real Linux machine, made just for you, with Java already installed.

It shows a **prompt** and waits:

```text
learner@java-basics:/workspace$
```

Read it from left to right: you are the user `learner`, on a machine called `java-basics`, in the folder
`/workspace`. A **folder** (also called a directory) is a box that holds files, like the folders on your own
computer. The `$` means "your turn".

Three commands are enough to find your way around:

- `pwd` prints the folder you are in.
- `ls` lists what is in it.
- `cd 01-first-program` moves into that folder.

Every chapter of this course has its own folder in `/workspace`, numbered like the chapter. Press **Run** on the
line below, then **Enter** in the terminal:

```bash run
cd /workspace/01-first-program && ls
```

The `&&` means "do the first command, and if it worked, the second". You should see four files: `Crash.java`,
`First.java`, `FixMe.java` and `Hello.java`. They are in the file list
next to the editor too.

:::photo{src="/lesson-images/python/vt100-terminal.webp" alt="A DEC VT100 computer terminal from 1978: a beige screen and keyboard" credit="Jason Scott" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:DEC_VT100_terminal.jpg"}
A DEC VT100 from 1978: a screen and a keyboard wired to one big shared computer. Your terminal window is named after machines like this.
:::
:::

:::step{type=concept title="A Java program: a class and a main" file="01-first-program/First.java" line="2-9"}
Open `First.java`:

```java
// Your very first Java file. Java runs what is inside main, from the top, one line at a time.
public class First {
    public static void main(String[] args) {
        System.out.println("Java is running this file, line by line.");
        System.out.println("2 + 3");
        System.out.println(2 + 3);
        System.out.println("That's the end of main. Bye!");
    }
}
```

There is more around the instructions than you might expect. Java likes structure, and every piece has a job:

1. A line starting with `//` is a **comment**: a note for people. Java skips it.
2. `public class First { ... }` is a **class**, a container for code. In Java, **all** code lives in a class,
   and the class name must match the file name: `First` lives in `First.java`.
3. `public static void main(String[] args) { ... }` is the **main method**: where your program starts. You will
   understand every word of that line by chapter 9; for now, think of it as Java's front door.
4. `System.out.println("...")` is an instruction: show this on the screen, then start a new line.
5. Every instruction ends with a **semicolon** `;`. It is how Java knows where one instruction stops.
6. Curly braces `{ }` mark where a class or a method begins and ends.

The text between double quotes is a **string**: a piece of text. Now look at lines 5 and 6 of the file. They
look almost the same. Do you think they print the same thing?
:::

:::step{type=predict title="Guess first"}
:::question
`First.java` has `System.out.println("2 + 3");` and then `System.out.println(2 + 3);`. What do those two lines
show?
:::
- [ ] `5` and `5`
- [ ] `2 + 3` and `2 + 3`
- [x] `2 + 3`, then `5`
- [ ] An error, because you cannot print a sum
:::explain
Quotes make a string, and a string is shown exactly as written: `2 + 3`. Without quotes, `2 + 3` is a calculation,
so Java works it out first and prints `5`. The quotes decide whether Java shows something or works it out.
:::
:::

:::step{type=try title="Run your first program" file="01-first-program/First.java" line="3-8"}
Run it:

```bash run
cd /workspace/01-first-program && java First.java
```

```text
Java is running this file, line by line.
2 + 3
5
That's the end of main. Bye!
```

Four lines, one for each `println`, in order. So what happened in that second after you pressed Enter? More than
you think. Press Play:

:::diagram{name="java-runs-a-file"}
Java checks and compiles the whole file to bytecode, then the JVM runs main, one line at a time.
:::

Now try something brave: change `System.out.println(2 + 3);` to `System.out.println(20 * 3);`, save, and run it
again. `*` means multiply. You just changed what a program does.
:::

:::step{type=example title="Worked example: a program that introduces itself"}
Here is a program with the same shape as your first task. A weather program that should say two lines:

```text
Hi, I am Sunny.
I will tell you if you need an umbrella.
```

```java
public class Sunny {
    public static void main(String[] args) {
        System.out.println("Hi, I am Sunny.");
        System.out.println("I will tell you if you need an umbrella.");
    }
}
```

1. The class is called `Sunny`, so the file must be `Sunny.java`.
2. One `println` for each line you want to see, inside `main`, each ending in `;`.
3. Each sentence goes in double quotes, so Java shows it exactly as written, capitals and full stops included.
:::

:::step{type=task task=hello_shelf title="Your turn: Shelf says hello"}
Open `Hello.java`. Its `main` has only comments, so it prints nothing. Make it print these two lines, exactly:

```text
Hello! I am Shelf.
I will look after your books.
```

1. Inside `main`, below the comments, write one `System.out.println(...);` for each line.
2. Copy each sentence exactly, with its capitals and punctuation.
3. Run it to see Shelf talk:

```bash run
cd /workspace/01-first-program && java Hello.java
```

When the two lines look right, press **Check**.

The usual slips, with what Java says (we tried each):

- `System.out.Println` with a capital P: `error: cannot find symbol`, then `symbol: method Println(String)`.
  Java cares about every capital letter.
- A missing `;`: `error: ';' expected`, with the `^` right after the line.
- Curly quotes `“…”` pasted from a document: `error: illegal character: '\u201c'`. Type plain quotes `"`.
- The `println` lines written below main's closing `}`: `error: <identifier> expected`. Instructions belong
  inside main's braces.
:::

:::step{type=concept title="When Java does not understand you" file="01-first-program/FixMe.java" line="4-6"}
Every programmer's code has mistakes, every day. Good programmers are simply good at reading what the computer
tells them, and Java tells you a lot. Open `FixMe.java`:

```java
System.out.println("Shelf is starting...")
system.out.println("Ready to look after your books.");
System.out.println("Books on the shelf: " + 12);
```

There are two mistakes. Can you spot them? Look closely at the end of the first line, and at the first letter of
the second.

The last line shows a handy trick: `+` between a string and a number **joins** them into one string, so it prints
`Books on the shelf: 12`.
:::

:::step{type=try title="Read Java's first message" file="01-first-program/FixMe.java" line="4"}
Run the broken program and let Java explain:

```bash run
cd /workspace/01-first-program && java FixMe.java
```

```text
FixMe.java:4: error: ';' expected
        System.out.println("Shelf is starting...")
                                                  ^
1 error
error: compilation failed
```

Read it piece by piece:

- `FixMe.java:4` is the file and the **line number**: line 4.
- `error: ';' expected` is the problem: Java expected a semicolon and did not find one.
- The code is shown again, and the `^` points at the exact spot where the `;` is missing.
- `compilation failed` means Java never even started running your program.

Here is the curious part: Java said **1 error**, but there are two mistakes. Java reads the grammar of the whole
file first; a grammar mistake like a missing `;` stops it before it even looks at the names you used. Fix the
semicolon, run it again, and Java will find the second one.
:::

:::step{type=example title="Worked example: two kinds of mistakes"}
After you add the `;`, Java finds the second mistake:

```text
FixMe.java:5: error: package system does not exist
        system.out.println("Ready to look after your books.");
              ^
1 error
error: compilation failed
```

Java is **case-sensitive**: `System` and `system` are two different names, and only `System` exists. (The message
talks about a "package" because Java guesses that a lowercase name followed by a dot might be a package, a group of
classes; you will meet packages in chapter 16. The real cause is the small `s`.) Again, nothing
ran: this is still a **compile error**, found before the program starts.

But some mistakes can only show up **while** the program runs. Open `Crash.java` and run it:

```bash run
cd /workspace/01-first-program && java Crash.java
```

```text
Books: 12
Exception in thread "main" java.lang.ArithmeticException: / by zero
	at Crash.main(Crash.java:7)
```

It compiled perfectly and printed the first line. Then it tried `books / shelves` with `shelves` being 0, and
dividing by zero has no answer, so Java threw an **exception** and stopped. The last line says exactly where:
`Crash.java`, line 7, in `main`.

| When | Kind | What you see |
|---|---|---|
| Before anything runs | compile error | `error: ...`, the line, a `^`, nothing printed |
| While it runs | exception | the lines before it print, then `Exception in thread "main"` |

Java catches far more mistakes before running than most languages. That is one reason big companies like it.
:::

:::step{type=task task=fix_first_errors title="Your turn: fix the two mistakes"}
Make `FixMe.java` compile and print exactly:

```text
Shelf is starting...
Ready to look after your books.
Books on the shelf: 12
```

1. Run it and read the first line of Java's message.
2. Fix that one mistake, save, and run it again.
3. Repeat until all three lines appear. Change only the mistakes, not the words.

```bash run
cd /workspace/01-first-program && java FixMe.java
```

Then press **Check**.
:::

:::step{type=try title="Look inside a class file: CA FE BA BE" file="01-first-program/First.java" line="2"}
`java First.java` hides a step. Let's do it by hand, the way Java worked for its first 22 years. First
**compile** with `javac` (the Java compiler), then **run** the result with `java`:

```bash run
cd /workspace/01-first-program && javac First.java && ls && java First
```

```text
Crash.java
First.class
First.java
FixMe.java
Hello.java
Java is running this file, line by line.
2 + 3
5
That's the end of main. Bye!
```

A new file appeared: `First.class`. That is the **bytecode**, the neutral form the JVM runs on any computer. Note
that `java First` takes the class name, without `.java`. Now peek at its first bytes:

```bash run
cd /workspace/01-first-program && od -A x -t x1 First.class | head -1
```

```text
000000 ca fe ba be 00 00 00 41 00 24 0a 00 02 00 03 07
```

There it is: **ca fe ba be**, the start of every class file ever compiled. The JVM checks those four bytes to make
sure it is looking at a real Java file. (The `41` a few bytes later is hexadecimal for 65, the class-file version
for Java 21.)
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A Java file is missing a semicolon on its very last line. What happens when you run it?
:::
- [ ] Every line runs, then Java stops at the last one
- [x] Nothing runs: Java reports a compile error first
- [ ] Java skips the broken line and runs the rest
:::explain
Java compiles the whole file before running any of it. A grammar mistake anywhere stops everything.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
In which file must the class `public class Shelf` be written?
:::
- [ ] Any file ending in `.java`
- [x] `Shelf.java`
- [ ] `Main.java`
:::explain
A public class must live in a file with exactly the same name, capitals included, plus `.java`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `System.out.println("Books: " + 12);` show?
:::
- [ ] `"Books: " + 12`
- [x] `Books: 12`
- [ ] `Books: 1`, then `2`
:::explain
`+` between a string and a number joins them into one string, and the quotes are not part of the text.
:::
:::

:::step{type=deep-dive title="Go deeper: JDK, JVM and the JIT"}
**Three names you will hear.** The **JVM** (Java Virtual Machine) runs bytecode. The **JDK** (Java Development
Kit) is the JVM plus the tools for developers: `javac`, `java`, `jshell` and more. Your lab has JDK 21.

**Why is Java fast, if it is not machine code?** The JVM watches your program run, finds the methods that run most
often, and compiles those into real machine code for this exact processor, while the program is running. This is
the **JIT** (just-in-time compiler). Long-running Java servers often end up very fast.

**jshell.** Type `jshell` in the terminal and you get Java's interactive mode: type `2 + 3` and it answers
`$1 ==> 5` right away, no class or `main` needed. Type `/exit` to leave. (The very first time, it may print a
line ending in `Created user preferences directory`: that is a harmless note, not an error.) You will use it for quick experiments in
chapter 6.

**`java File.java` versus `javac` + `java`.** Since Java 11, `java File.java` compiles in memory and runs in one go,
leaving no `.class` file: perfect for learning. Real projects compile everything with a build tool (chapter 16).
:::

:::step{type=recap title="What you can do now"}
You can now:

- Find your way in the terminal, and run a Java file with `java File.java`, or `javac` then `java`.
- Write a class with a `main` method, and print with `System.out.println`, ending each instruction with `;`.
- Tell a string (in quotes) from a calculation, and join text and numbers with `+`.
- Read a compile error (line number, message, `^`) and an exception at run time, and fix both.

:::photo{src="/lesson-images/java/java-01-sketch.webp" alt="Sketchnote: Your first Java program. All Java code lives in a class; the program starts in main and runs its lines from the top, one at a time. Flow: Hello.java, javac checks and compiles, Hello.class bytecode, the JVM runs main, println shows a line. Remember: every instruction ends with a semicolon; the class Hello lives in the file Hello.java; a compile error means nothing runs at all; an exception means the lines before it already ran." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 2: your first methods, small named pieces that each do one job.
:::
