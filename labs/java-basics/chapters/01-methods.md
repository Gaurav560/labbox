:::step{type=story title="600 merchants a day"}
:::character{name="Kabir" role="Lead engineer, PaySetu"}
PaySetu signs up 600 new UPI merchants every day, from coffee stalls to pharmacies.
Each one gets a welcome message, and our shop-name checker keeps breaking on long
names. I need two small Java methods I can trust.
:::

:::mission
Write `greet`, which builds the welcome message, and `longestWord`, which finds the
longest word in a shop name.
:::
:::

:::step{type=concept title="Methods return values"}
## Your first methods

In Java, a **method** is a named block of code that lives inside a class. A
`static` method belongs to the class itself, so you call it as
`Greeter.greet("Asha")` without creating an object first.

```java
public static int square(int x) {
    return x * x;
}
```

The word before the name (`int`) is the **return type**. The `return` statement
sends a value of that type back to the caller.
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
`System.out.println` prints a `null` String as the word `null`. The code compiles
fine: `null` is a valid value for any object type, including `String`.
:::
:::

:::step{type=try title="Compile and run"}
The terminal at the bottom is a real Linux machine with your files in `/workspace`.
Java needs two steps: `javac` compiles your code, then `java` runs it.

```bash run
javac Greeter.java && java Greeter
```

You should see `null`. Once `greet` works, the same command prints `Hello, Asha!`.
:::

:::step{type=task task=greet title="Welcome a merchant"}
Make `greet(name)` return `"Hello, <name>!"`.

For example, `greet("Asha")` returns `"Hello, Asha!"`. Mind the comma and the
exclamation mark.

:::tip
In Java, `+` joins Strings together: `"coffee" + "cup"` is `"coffeecup"`.
:::
:::

:::step{type=example title="Splitting text into words"}
`String.split` cuts a String into an array of pieces wherever it finds a separator:

```java
String[] parts = "filter coffee stall".split(" ");
// parts is ["masala", "coffee", "stall"]
parts.length      // 3
parts[0].length() // 6
```

You can walk through an array with a for-each loop:

```java
for (String p : parts) {
    System.out.println(p);
}
```

:::mistake
Arrays use `.length` (no brackets). Strings use `.length()` (with brackets).
:::
:::

:::step{type=task task=longest_word title="Longest word in a shop name"}
Make `longestWord(sentence)` return the length of the longest word, where words are
separated by spaces.

`longestWord("the quick brown fox")` returns `5`. An empty sentence returns `0`.
:::

:::step{type=recap title="Chapter done"}
- A method has a return type, a name, inputs, and a `return` statement.
- `static` methods are called on the class: `Greeter.greet("Asha")`.
- `split(" ")` turns a sentence into words; keep the best length in a variable as you loop.
:::
