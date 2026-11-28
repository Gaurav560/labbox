:::step{type=story title="Why does every big program start small?"}
A library app checks out books, greets members, works out late fees and prints receipts, thousands of times a
day. Do you think someone wrote "greet the member" out a thousand times?

No. They wrote it **once**, gave it a name, and used the name everywhere. In Java, a named piece of code that
does one job is a **method**. You have already used one: `println`. Today you write your own, and you will see
something Python and JavaScript never make you do: Java wants to know the **type** of everything that goes in and
comes out.

:::mission
Write `greet`, which builds a greeting for any member, and `longestWord`, which finds the longest word in a book
title.
:::
:::

:::step{type=concept title="A method, part by part" file="02-methods/Greeter.java" line="3-6"}
Here is a small method that doubles a number:

```java
static int twice(int n) {
    return n * 2;
}
```

Read the first line from left to right:

- `static` means the method belongs to the class itself, so you can call it without creating anything first.
  (Chapter 9 shows the other kind.)
- `int` is the **return type**: this method gives back a whole number (`int` is short for integer).
- `twice` is the method's **name**.
- `(int n)` lists the **parameters**: one input called `n`, which must be an `int`.
- The **body** between `{ }` does the work, and `return n * 2;` hands the answer back.

You **call** a method by its name with brackets: `twice(4)` gives back `8`. The value in the brackets, `4`, is an
**argument**; inside the method, `n` holds it.

Open `Greeter.java`. Its `greet` method has exactly this shape, with `String` (text) instead of `int`:
`static String greet(String name)`. Right now it says `return null;`, and `null` is Java's way of saying "no
object at all".

:::picture{name="recipe-card"}
A method is like a recipe card: a name, the inputs it needs, the steps, and what you get at the end.
:::
:::

:::step{type=example title="Worked example: follow one call"}
A method that builds text, and a `main` that calls it:

```java
public class Welcome {
    static String welcome(String city) {
        return "Welcome to " + city + "!";
    }

    public static void main(String[] args) {
        String message = welcome("Pune");
        System.out.println(message);
    }
}
```

Press Play to follow the call, step by step:

:::diagram{name="java-method-call"}
The call jumps into the method, the parameter gets the argument, and return carries the answer back.
:::

1. `main` runs first. It reaches `welcome("Pune")` and jumps into the method, with `city` holding `"Pune"`.
2. `"Welcome to " + city + "!"` joins three strings into `"Welcome to Pune!"`.
3. `return` hands that back. It is stored in `message`, a variable of type `String`.
4. `println` shows `Welcome to Pune!`.

Your first task has exactly this shape.
:::

:::step{type=predict title="Guess first"}
:::question
`Greeter.java`'s `main` calls `System.out.println(greet("Asha"));`, and `greet` says `return null;`. What does
running it print first?
:::
- [ ] `Hello, Asha!`
- [x] `null`
- [ ] Nothing at all
- [ ] An error
:::explain
`greet` gives back `null`, and `println` shows `null` as the word `null`. The method runs fine; it just does not do
its job yet.
:::
:::

:::step{type=try title="Run it and see" file="02-methods/Greeter.java" line="13-16"}
Run the file:

```bash run
cd /workspace/02-methods && java Greeter.java
```

```text
null
0
```

The first line is `greet("Asha")`, the second `longestWord("The Hobbit returns")`, both still unfinished. Run it
again after each change: these two lines are your quickest way to see your methods work.
:::

:::step{type=task task=greet title="Your turn: greet someone"}
Make `greet(name)` in `Greeter.java` give back `"Hello, <name>!"`.

1. Replace `return null;` with a `return` that joins strings with `+`.
2. Mind the comma after Hello, the space, and the `!`: the check compares the text exactly.

`greet("Asha")` gives `"Hello, Asha!"`, and `greet("Kabir")` gives `"Hello, Kabir!"`. Run `java Greeter.java` to
see it, then press **Check**.

The usual slips: forgetting the spaces inside the quotes (`"Hello," + name` gives `Hello,Asha`); or single
quotes, `'Hello, '`. In Java single quotes are only for one character, so `javac` stops with
`error: unclosed character literal` (we tried it). Text always goes in double quotes.
:::

:::step{type=concept title="Java checks the types before running"}
Here is where Java is different from Python. Every parameter, every variable and every return value has a type,
and `javac` checks them **all** before your program runs. Try returning a number from a method that promises text:

```java
static String greet(String name) {
    return 42;
}
```

```text
Bad1.java:3: error: incompatible types: int cannot be converted to String
        return 42;
               ^
```

Forget the `return` entirely, and Java notices that too:

```text
Bad2.java:4: error: missing return statement
    }
    ^
```

And call `greet()` without its argument:

```text
Bad3.java:4: error: method greet in class Bad3 cannot be applied to given types;
        System.out.println(greet());
                           ^
  required: String
  found:    no arguments
  reason: actual and formal argument lists differ in length
```

`required: String`, `found: no arguments`: Java tells you exactly what it expected. ("Formal" arguments are the
parameters in the method's first line; "actual" arguments are the ones in the call.) In Python, the missing
argument would only show up when that line ran, maybe months later, in front of a user, and the other two
mistakes would not show up at all: the function would quietly give back the wrong thing. In Java, the program
will not even start until all three are fixed. That is the deal Java offers: a little more typing, a lot fewer
surprises.
:::

:::step{type=concept title="print shows, return gives back"}
One more distinction that confuses everyone at first. A method can **show** something, or **give it back**:

```java
static void shoutPrint(String word) {
    System.out.println(word.toUpperCase() + "!");
}

static String shoutReturn(String word) {
    return word.toUpperCase() + "!";
}
```

`void` means "gives nothing back". `shoutPrint("hello")` prints `HELLO!` and that is all: there is nothing you
could store. `shoutReturn("hello")` prints nothing, but gives back `"HELLO!"`, which you can store, join or pass
on:

```java
String b = shoutReturn("hello");
System.out.println("b is " + b);    // b is HELLO!
```

In Java you cannot even try `String a = shoutPrint("hello");`: `javac` refuses with `error: incompatible types:
void cannot be converted to String`, because a `void` method has no value.
Almost every method you write will `return` its answer and let the caller decide what to do with it.
:::

:::step{type=example title="Worked example: the shortest word"}
Your next task looks at every word of a title. Here is the same idea for the **shortest** word. Two new tools
first: `sentence.split(" ")` cuts a string into an array of words at each space, and
`for (String w : ...)` runs the body once for each word (chapter 5 is all about loops):

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

1. Start with a value no real word can beat: the biggest `int` there is, `Integer.MAX_VALUE`, which is
   2,147,483,647.
2. Compare each word's `length()` with the best so far.
3. Keep it when it wins.

Press the arrows and watch `best` change:

:::trace{title='shortestWord("big kirana store")'}
| w | w.length() | best | note |
|---|---|---|---|
|  |  | huge | Before the loop: best starts bigger than any word could be. |
| big | 3 | 3 | 3 is shorter than huge, so best becomes 3. |
| kirana | 6 | 3 | 6 is not shorter than 3: best stays 3. |
| store | 5 | 3 | 5 is not shorter than 3: best stays 3. |
|  |  | 3 | No words left: the method returns 3. |
:::
:::

:::step{type=task task=longest_word title="Your turn: the longest word"}
In `Greeter.java`, make `longestWord(sentence)` give back the length of the longest word, where words are
separated by spaces.

`longestWord("The Hobbit returns")` gives `7` ("returns"), and `longestWord("the quick brown fox")` gives `5`.

It is the worked example turned around: start with the smallest possible best (0), and keep a word's length when
it is **longer**. Run `java Greeter.java` to see it, then press **Check**.

The usual slips: `w.length` without brackets. For a string, `length()` is a method, so `javac` says
`error: cannot find symbol` and `symbol: variable length` (we tried it; arrays, in chapter 8, are the ones with a
`length` without brackets). Or `sentence.length()` instead of `w.length()`, which measures the whole title.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `static double half(int n)` promise?
:::
- [ ] It takes a double and gives back an int
- [x] It takes an int and gives back a double
- [ ] It gives back nothing
:::explain
The type before the name is what comes back (`double`); the types in the brackets are what goes in (`int n`).
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A method promises `int` but has no `return`. When do you find out?
:::
- [x] When you compile: `missing return statement`
- [ ] When the method is called
- [ ] Never: Java returns 0
:::explain
`javac` checks every path through the method before anything runs.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `void` mean in `static void log(String text)`?
:::
- [ ] The method takes no input
- [x] The method gives nothing back
- [ ] The method is empty
:::explain
`void` is the return type for "nothing". The method can still take inputs and do work, like printing.
:::
:::

:::step{type=deep-dive title="Go deeper: overloading, and why types help teams"}
**Overloading.** Java lets two methods share a name if their parameters differ:

```java
static int twice(int n) { return n * 2; }
static String twice(String s) { return s + s; }
```

`twice(4)` is `8` and `twice("ha")` is `"haha"`: Java picks the right one by the argument's type, at compile time.
`println` itself is overloaded: there are versions for text, whole numbers, decimals and more.

**Why big teams like types.** In a codebase of a million lines, a method's first line tells you exactly what it
needs and what it gives back, and the compiler checks every call. Editors use the types too: they suggest the
right methods as you type and can rename things safely across thousands of files.

**Javadoc.** A comment starting with `/**` above a method is documentation: tools turn it into the web pages you
will read when you look up Java's own classes.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write a method with a return type, a name, typed parameters and a body that `return`s an answer.
- Call methods with arguments, and store what they give back in a typed variable.
- Read Java's type errors: `incompatible types`, `missing return statement`, wrong arguments.
- Tell `void` (shows, gives nothing back) from a method that returns a value.

:::photo{src="/lesson-images/java/java-02-sketch.webp" alt="Sketchnote: Your first methods. A method is a named piece of code; its first line says what goes in and what type comes back. Flow: static String greet(String name), greet of Asha calls it, name holds Asha, return the text, Hello Asha comes back. Remember: javac checks every type before the program runs; void means the method gives nothing back; return gives the answer to the code that called it; text goes in double quotes, one character in single quotes." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 3: variables and types, with whole numbers, decimals, text, and a division that surprises everyone.
:::
