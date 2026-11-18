# Your first methods

In Java, a **method** is a named block of code that lives inside a class. A
`static` method belongs to the class itself, so you can call it as
`Greeter.greet("Asha")` without creating an object first.

```java
public static int square(int x) {
    return x * x;
}
```

The word before the name (`int`) is the **return type**. The `return` statement
sends a value of that type back to the caller.

## Try it in the terminal

The terminal at the bottom is a real Linux machine with your files in `/workspace`.
Compile and run your class with:

```bash
javac Greeter.java && java Greeter
```

`main` prints `greet("Asha")`, so once your code works you should see `Hello, Asha!`.

## Your tasks

1. **greet**: make `greet(name)` return `"Hello, <name>!"`.
2. **longest_word**: make `longestWord(sentence)` return the length of the longest
   word, where words are separated by spaces. `longestWord("the quick brown fox")`
   returns `5`. An empty sentence returns `0`. Hint: look at `String.split`.

Your files save automatically. Press **Check** to run the hidden tests on a clean
machine.
