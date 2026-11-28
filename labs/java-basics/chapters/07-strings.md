:::step{type=story title="When are two equal names not equal?"}
Here is a puzzle that has confused Java developers for thirty years. Two strings, both containing exactly `riya`.
Java compares them with `==` and says:

```text
false
```

Not a bug in Java. It is asking a different question from the one you think, and by the end of this chapter you
will know which one, and the one-word fix every Java programmer uses.

Shelf deals with text all day: titles typed in a hurry, member names in every possible capitalisation. Today
Shelf learns to take text apart, tidy it and compare it properly.

:::mission
Write `countWords`, which counts the words in messy text, and `cleanName`, which tidies a badly typed member name.
:::
:::

:::step{type=concept title="A String is a row of characters"}
A `String` is a sequence of `char` values, each with a position starting at **0**. You have already used
`length()` and `charAt`. Here is the everyday toolbox:

| Code | Gives | For `"Hobbit"` |
|---|---|---|
| `s.length()` | the number of characters | `6` |
| `s.charAt(i)` | the character at position i | `charAt(0)` is `'H'` |
| `s.substring(a, b)` | a new string from a up to, not including, b | `substring(0, 3)` is `"Hob"` |
| `s.indexOf(c)` | the first position of c, or -1 | `indexOf('b')` is `2` |
| `s.contains(t)` | does t appear inside? | `contains("bit")` is `true` |
| `s.toUpperCase()` | all capitals | `"HOBBIT"` |

Notice that `length()` needs brackets (it is a method), while an array's `length` in chapter 8 does not (it is a
**field**: a value stored on the object, not a method). Everyone mixes them up once; the compiler will tell you.

:::picture{name="beads-on-string"}
A string is beads on a thread: each bead a character, each with its place in the row, starting at 0.
:::
:::

:::step{type=try title="Tidy a line typed at the desk" file="07-strings/Receipt.java" line="4-8"}
Open `Receipt.java` and run it:

```bash run
cd /workspace/07-strings && java Receipt.java
```

```text
[   THE hobbit   ]
[THE hobbit]
the hobbit
16 10
```

The square brackets make the invisible spaces visible. `strip()` removes the spaces at both ends,
`toLowerCase()` makes every letter small, and `length()` says the line was 16 characters, only 10 without the
spaces around it. Six invisible spaces: exactly what makes a search for "the hobbit" fail.
:::

:::step{type=concept title="Strings never change"}
Try to change a string in place:

```java
String s = "pen";
s.toUpperCase();
System.out.println(s);
```

```text
pen
```

Still `pen`. Strings in Java are **immutable**: no method ever changes a string. `toUpperCase()` built a new
string, `"PEN"`, and gave it back, and nobody stored it. To keep the result, store it: `s = s.toUpperCase();`.

Because every method gives back a new string, you can **chain** them, left to right:

```java
"   THE hobbit   ".strip().toLowerCase()    // "the hobbit"
```
:::

:::step{type=example title="Worked example: split, and its trap"}
`split` cuts a string into an array of pieces. It takes a **regular expression** (regex for short): a small
pattern language for describing text, where some characters have special meanings. (The lists below are printed
with `Arrays.toString`, which shows an array in square brackets.)

```java
"a b  c".split(" ")                       // [a, b, , c]
"  a b  c ".strip().split("\\s+")         // [a, b, c]
```

1. `split(" ")` cuts at **every single** space, so two spaces in a row leave an empty piece.
2. `"\\s+"` means "one or more whitespace characters" (spaces, tabs, new lines): any run of them is one cut. In
   Java code the backslash itself must be written twice, which is why it looks like `\\s+`.
3. `strip()` first, so there is no empty piece at the start.

And now the trap. What does an **empty** string give?

```java
"".split("\\s+")           // [], which is really one empty piece
"".split("\\s+").length    // 1
```

One piece, containing nothing. If you count words by counting pieces, an empty text has 1 word. Real code checks
for empty text first, with `s.isEmpty()`.
:::

:::step{type=predict title="Guess first"}
:::question
What is `"   ".strip().split("\\s+").length`?
:::
- [ ] `0`
- [x] `1`
- [ ] `3`
:::explain
`strip()` leaves an empty string, and splitting an empty string gives one empty piece, so the length is 1. Check
`isEmpty()` before counting.
:::
:::

:::step{type=task task=count_words title="Your turn: count the words"}
Open `Words.java` and make `countWords(text)` give back how many words the text has. Words are separated by
spaces, tabs or new lines, sometimes several in a row; an empty or blank text has 0 words.

`countWords("Java is fun")` gives `3`, `countWords("  lots   of   spaces  ")` gives `3`, and `countWords("")` gives
`0`.

```bash run
cd /workspace/07-strings && java Words.java
```

Then press **Check**. The usual slips: `split(" ")` instead of `split("\\s+")`: on `"  lots   of   spaces  "`, even
after `strip()`, it gives 7 pieces (we tried it), empty ones included; or forgetting the empty-text check, so `""`
counts as 1 word.
:::

:::step{type=concept title="equals, not ==" file="07-strings/SameText.java" line="4-7"}
Now the puzzle from the start. Open `SameText.java` and run it:

```java
String a = "riya";
String b = new String("riya");
System.out.println(a == b);
System.out.println(a.equals(b));
```

```bash run
cd /workspace/07-strings && java SameText.java
```

```text
false
true
```

A `String` is an **object**, and a variable like `a` holds a **reference**: an arrow pointing at the object
somewhere in memory. `==` asks "do these two arrows point at the **same object**?" `new String("riya")` made a
second object, so the answer is `false`, even though both say `riya`. `equals` asks the question you meant: "do
they contain the **same text**?"

:::diagram{name="string-equals"}
a and b point to two different String objects with the same text: == compares the objects, equals compares the text.
:::

The rule: **compare strings with `equals`**, always. (`"Riya".equalsIgnoreCase("RIYA")` is `true` when capitals
should not matter.) The `==` sometimes *seems* to work, because Java reuses identical text written directly in
your code, which makes the bug appear only now and then. That is exactly what makes it dangerous.
:::

:::step{type=example title="Worked example: building text"}
Two ways to put strings together. For a few pieces, `String.join`:

```java
String.join("-", "2026", "11", "22")    // "2026-11-22"
```

To build a string bit by bit in a loop, use a `StringBuilder`, which **can** grow in place:

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 3; i++) {
    sb.append(i).append(",");
}
System.out.println(sb);    // 0,1,2,
```

And capitalising one word, a small recipe you will need next:

```java
String w = "riya";
String nice = w.substring(0, 1).toUpperCase() + w.substring(1).toLowerCase();   // "Riya"
```

The first letter, made a capital, plus the rest, made small.
:::

:::step{type=task task=clean_name title="Your turn: a tidy member name"}
In `Words.java`, make `cleanName(raw)` give back the name tidied: no spaces at the ends, one space between words,
and each word with a capital first letter and small letters after.

`cleanName("  riya   SHARMA ")` gives `"Riya Sharma"`, `cleanName("ARJUN")` gives `"Arjun"`, and a name that is only
spaces gives `""`.

Strip, check for empty, split on runs of spaces, capitalise each word, and join with single spaces.

```bash run
cd /workspace/07-strings && java Words.java
```

Then press **Check**.

The usual slip: skipping the empty check. A name of only spaces strips to `""`, splits into one empty piece, and
`substring(0, 1)` on that empty piece crashes: `StringIndexOutOfBoundsException: Range [0, 1) out of bounds for
length 0` (we tried it). `[0, 1)` is maths notation for "from 0, up to but not including 1".
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is `"Shelf".substring(1, 4)`?
:::
- [ ] `"She"`
- [x] `"hel"`
- [ ] `"helf"`
:::explain
From position 1 (`h`) up to, but not including, position 4: `hel`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
How should you check whether `name` contains exactly the text `"Riya"`?
:::
- [ ] `name == "Riya"`
- [x] `name.equals("Riya")`
- [ ] `name = "Riya"`
:::explain
`equals` compares the text. `==` compares which object it is, and `=` stores a value.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
After `String t = "abc"; t.toUpperCase();`, what is `t`?
:::
- [x] `"abc"`
- [ ] `"ABC"`
:::explain
Strings never change; the new `"ABC"` was thrown away. Write `t = t.toUpperCase();` to keep it.
:::
:::

:::step{type=deep-dive title="Go deeper: the string pool, text blocks and char"}
**The string pool.** Java keeps one shared copy of every string literal (text written directly in your code). That
is why `"riya" == "riya"` happens to be `true`, while `new String("riya")` makes a separate object. The pool saves
memory; it also hides `==` bugs until a string arrives from a file or a user. Always `equals`.

**Text blocks.** Since Java 15, three double quotes start a multi-line string, perfect for long messages or JSON:

```java
String json = """
    {"title": "The Hobbit", "copies": 3}
    """;
```

**char is a number.** A `char` is really a 16-bit number: `'A' + 1` is `66`, and `(char) ('A' + 1)` is `'B'`. That
is how `Character.toUpperCase` and friends work underneath.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read characters and pieces of a string with `charAt`, `substring`, `indexOf`, `contains` and `length()`.
- Tidy text with `strip`, `toLowerCase` and `toUpperCase`, remembering strings never change.
- Split with `"\\s+"` and avoid the empty-string trap; join with `String.join` and `StringBuilder`.
- Compare strings with `equals`, never `==`, and explain why.

:::photo{src="/lesson-images/java/java-07-sketch.webp" alt="Sketchnote: Strings. A String is a row of characters, positions from 0; strings never change, every method gives back a new one. Flow: messy riya SHARMA, strip() and check empty, split on spaces, capitalise each word, join to Riya Sharma. Remember: compare text with equals, never with ==; s.toUpperCase() alone changes nothing, store it; an empty string splits into one empty piece; length() for a String, length for an array." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 8: arrays, a fixed row of values with numbered slots.
:::
