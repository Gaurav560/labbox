:::step{type=story title="Why strings"}
Names typed in capitals, extra spaces, a sentence pasted from a chat: text from people is messy. Before
a program can use it, it usually has to clean it up and look inside it. Java's String has a large set
of tools for exactly that.

:::mission
In `words/Words.java`, count the words in a sentence (a warm-up), then tidy up a person's name.
:::
:::

:::step{type=concept title="A String is a row of characters"}
Picture a string of beads, each bead one character, numbered from **0**:

```java
String word = "Java";
word.length()        // 4
word.charAt(0)       // 'J'   (positions start at 0)
word.substring(1)    // "ava"  from position 1 to the end
word.substring(0, 2) // "Ja"   from 0 up to, not including, 2
```

Strings **never change**. Every method gives you a **new** string and leaves the original alone:
`word.toUpperCase()` returns `"JAVA"`, but `word` is still `"Java"`.

:::picture{name="beads-on-string"}
Every character has a numbered place, starting at 0.
:::
:::

:::step{type=concept title="Cleaning tools"}
The everyday cleaning tools:

```java
"  hi  ".trim()               // "hi"        spaces off both ends
"riya".toUpperCase()          // "RIYA"
"RIYA".toLowerCase()          // "riya"
"a b  c".split("\\s+")        // ["a", "b", "c"]
String.join(" ", parts)       // glue pieces with a space
```

`"\\s+"` is a small **pattern** meaning "one or more spaces, tabs or new lines". Splitting on it treats
any run of spaces as one gap, so extra spaces never make empty pieces.
:::

:::step{type=example title="Worked example: tidy a product code"}
Cleaning text is usually three moves: **split**, **change** each piece, **join**.

```java
public static String code(String raw) {
    String[] parts = raw.trim().split("\\s+");   // 1
    for (int i = 0; i < parts.length; i++) {
        parts[i] = parts[i].toUpperCase();         // 2
    }
    return String.join("-", parts);                // 3
}

// code("  ab-12   cd ") gives "AB-12-CD"
```

1. Trim the ends, then split on runs of spaces.
2. Change each piece, here to upper case.
3. Glue the pieces back with a dash.

Both tasks in this chapter use some of these moves.

:::trace{title='code("  ab-12   cd ")'}
| step | value | note |
|---|---|---|
| raw | "  ab-12   cd " | The text as it arrives. |
| raw.trim() | "ab-12   cd" | trim removes the spaces at both ends only. |
| split("\\\\s+") | {"ab-12", "cd"} | Split on any run of spaces. |
| toUpperCase each | {"AB-12", "CD"} | The loop changes each slot of the array. |
| String.join("-", parts) | "AB-12-CD" | The pieces are glued back with a dash. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
How many pieces does `"a  b".split(" ")` give? (There are two spaces.)
:::
- [ ] 2
- [x] 3
- [ ] 4
- [ ] 1
:::explain
`split(" ")` cuts at **every** single space, so two spaces in a row leave an empty piece between them:
`["a", "", "b"]`. Splitting on `"\\s+"` treats the run of spaces as one gap.
:::
:::

:::step{type=try title="Split two ways"}
```bash run
cat > /tmp/Split.java <<'JAVA'
import java.util.Arrays;

public class Split {
    public static void main(String[] args) {
        String messy = "  riya    SHARMA ";
        System.out.println(Arrays.toString(messy.split(" ")));
        System.out.println(Arrays.toString(messy.trim().split("\\s+")));
    }
}
JAVA
java /tmp/Split.java
```
:::

:::step{type=task task=count_words title="Warm-up: count the words"}
In `words/Words.java`, make `countWords(text)` return how many words the text has, separated by one or
more spaces, tabs or new lines.

- `countWords("Java is fun")` returns `3`
- `countWords("  lots   of   spaces  ")` returns `3`
- `countWords("")` and `countWords("   ")` return `0`

Careful: splitting an empty string still gives one (empty) piece, so check for empty text first.
:::

:::step{type=concept title="Comparing strings: equals, not =="}
Java's most famous beginner trap. Picture two **identical** printed letters in two envelopes. Asking
"are these the same envelope?" is different from asking "do they say the same thing?".

`==` on strings asks "same envelope?" (the same object in memory). `equals` asks "same text?":

```java
String a = "riya";
String b = new String("riya");
a == b          // false: two different objects
a.equals(b)     // true: the same text
```

:::diagram{name="string-equals"}
`a` and `b` hold the same text in two different objects: `==` compares the objects, `equals` compares the text.
:::

Always compare text with `equals` (or `equalsIgnoreCase` to ignore capitals).
:::

:::step{type=task task=clean_name title="Tidy up a name"}
In `words/Words.java`, make `cleanName(raw)` return the name with no spaces at the ends, one space
between words, and each word as a capital letter followed by small letters.

- `cleanName("  riya   SHARMA ")` returns `"Riya Sharma"`
- `cleanName("ARJUN")` returns `"Arjun"`
- `cleanName("   ")` returns `""`

For one word `w`: `w.substring(0, 1).toUpperCase()` plus `w.substring(1).toLowerCase()`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
After `String s = "java"; s.toUpperCase();` what is `s`?
:::
- [ ] `"JAVA"`
- [x] `"java"`
- [ ] `null`
- [ ] It does not compile
:::explain
Strings never change: `toUpperCase()` returns a **new** string, and here nobody kept it. Write
`s = s.toUpperCase();` to keep the result.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which is the right way to check that `name` is `"Riya"`?
:::
- [ ] `name == "Riya"`
- [x] `name.equals("Riya")`
- [ ] `name = "Riya"`
- [ ] `name.compare("Riya")`
:::explain
`equals` compares the text. `==` compares whether two variables point to the same object, which may be
false even for identical text.
:::
:::

:::step{type=deep-dive title="Why == sometimes seems to work"}
`"riya" == "riya"` is often `true`, which makes the trap sneakier. Java keeps one shared copy of every
string **literal** written in your code (the **string pool**), so two literals with the same text are
literally the same object. Strings built at run time (read from input, made with `new` or by joining)
are new objects, and `==` fails. Code that "worked in testing" then breaks in production.

Because strings never change, building one in a loop with `+=` makes a new string every round. For many
pieces, use a `StringBuilder`: `sb.append(piece)` grows one buffer, and `sb.toString()` gives the
result at the end.
:::

:::step{type=recap}
- A String is a row of characters numbered from 0: `length`, `charAt`, `substring`.
- Strings never change; methods return new strings.
- `trim`, `split("\\s+")`, `String.join` clean and rebuild text.
- Compare text with `equals`, never `==`.
:::
