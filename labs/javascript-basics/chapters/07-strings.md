:::step{type=story title="How long is one emoji?"}
Count the characters in `hello`: five. Now count the characters in 🎵, a single music note. One, surely. Ask
JavaScript:

```text
2
```

Two. For one picture. By the end of this chapter you will know why, and the one-line trick that counts it properly.

Mixtape deals with text all day: song titles typed in a hurry, artists' names in every possible capitalisation. Today
Mixtape learns to take text apart, tidy it and put it back together.

:::mission
Write `countWords`, which counts the words in messy text, and `cleanName`, which tidies a badly typed name.
:::
:::

:::step{type=concept title="A string is a row of characters"}
A **string** is a sequence of characters, each with a numbered place starting at **0**:

| Code | Gives | For `"Neon Lanes"` |
|---|---|---|
| `s.length` | how many characters | `10` |
| `s[0]` | the character at position 0 | `"N"` |
| `s.at(-1)` | the last character | `"s"` |
| `s.slice(0, 4)` | from 0 up to, not including, 4 | `"Neon"` |
| `s.indexOf("L")` | the first position of `"L"`, or -1 | `5` |
| `s.includes("Lane")` | does it appear inside? | `true` |

Strings never change in place. Methods like `toUpperCase()` give back a **new** string and leave the original alone.

:::picture{name="beads-on-string" concept="A string is a row of characters"}
Every character has a numbered place, starting at 0.
:::
:::

:::step{type=try title="Tidy a title typed in a hurry" file="07-strings/titles.js" line="2-11"}
Open `titles.js` and run it:

```bash run
cd /workspace/07-strings && node titles.js
```

```text
[   monsoon DRIVE  ]
[monsoon DRIVE]
monsoon drive
18 13
N s Neon 5 true
Neon Lanes
```

The square brackets make the invisible spaces visible. `trim()` removed the spaces at both ends, `toLowerCase()`
made every letter small, and the lengths say 18 characters before and 13 after: five invisible spaces, exactly what
makes a search for "monsoon drive" fail.

The last line is the proof that strings never change: `title.toUpperCase()` built `"NEON LANES"`, nobody stored it,
and `title` is still `Neon Lanes`. To keep a result, store it: `const loud = title.toUpperCase();`.
:::

:::step{type=concept title="Cleaning tools"}
The everyday tools for messy text:

```js
"  hi  ".trim()                 // "hi": spaces at both ends removed
"a b  c".split(" ")             // ["a", "b", "", "c"]: every single space cuts
"a b  c".split(/\s+/)           // ["a", "b", "c"]: any run of spaces cuts once
["a", "b"].join("-")            // "a-b"
"RIYA".toLowerCase()            // "riya"
```

`/\s+/` is a small **regular expression**: "one or more spaces". You will see it often.

:::picture{name="trim-edges" concept="Cleaning tools"}
Trimming removes the spaces at both edges and keeps the gap between the words.
:::
:::

:::step{type=example title="Worked example: tidy a song code"}
Cleaning text is usually three moves: **split**, **change** each piece, **join**:

```js
function code(raw) {
  const parts = raw.trim().split(/\s+/);
  const upper = parts.map((p) => p.toUpperCase());
  return upper.join("-");
}

code("  neon   lanes 2 ")   // "NEON-LANES-2"
```

1. Trim the ends, then split on runs of spaces: `["neon", "lanes", "2"]`.
2. Change each piece, here to upper case (`map` means "do this to each"; chapter 11 explains it).
3. Join the pieces with `-`.

And a trap: what does an **empty** text give? `"".split(/\s+/)` is `[""]`: one empty piece. If you count words by
counting pieces, empty text has 1 word. Check for it first.
:::

:::step{type=predict title="Guess first"}
:::question
What is `"   ".trim().split(/\s+/).length`?
:::
- [ ] `0`
- [x] `1`
- [ ] `3`
:::explain
`trim()` leaves an empty string, and splitting an empty string gives one empty piece, so the length is 1.
:::
:::

:::step{type=task task=count_words title="Your turn: count the words"}
Open `words.js` and make `countWords(text)` give back how many words the text has. Words are separated by spaces, tabs
or new lines, sometimes several in a row; an empty or blank text has 0 words.

`countWords("JavaScript is fun")` gives `3`, `countWords("  lots   of   spaces  ")` gives `3`, and `countWords("")`
gives `0`.

```bash run
cd /workspace/07-strings && node words.js
```

Then press **Check**.
:::

:::step{type=try title="Why one emoji is two characters long" file="07-strings/emoji.js" line="2-5"}
Back to the puzzle. Open `emoji.js`:

```bash run
cd /workspace/07-strings && node emoji.js
```

```text
5
2
1
[ 'N', 'e', 'o', 'n', ' ', '\ud83c', '\udfb5' ]
```

Inside, JavaScript stores text in pieces of 16 bits, a choice made in 1995 when 65,536 characters seemed like
plenty. Emoji came later and did not fit, so each one is stored as **two** pieces, and `length` counts pieces, not
pictures. The last line shows the two halves of 🎵, which mean nothing on their own.

The fix is the spread `[...text]`, which walks the text by real characters: `[..."🎵"].length` is `1`. Use it whenever
emoji, or many scripts of the world, might appear.
:::

:::step{type=concept title="Capital first, the rest small"}
A small recipe you will need next:

```js
const w = "rIYA";
const nice = w[0].toUpperCase() + w.slice(1).toLowerCase();   // "Riya"
```

The first letter, made a capital, joined to the rest, made small.

:::picture{name="initial-and-tail" concept="Capital first, the rest small"}
The first letter becomes a capital; the tail becomes small letters.
:::
:::

:::step{type=task task=clean_name title="Your turn: a tidy name"}
In `words.js`, make `cleanName(raw)` give back the name tidied: no spaces at the ends, one space between words, and
each word with a capital first letter and small letters after.

`cleanName("  riya   SHARMA ")` gives `"Riya Sharma"`, `cleanName("ARJUN")` gives `"Arjun"`, and a name that is only
spaces gives `""`.

```bash run
cd /workspace/07-strings && node words.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is `"Mixtape".slice(1, 4)`?
:::
- [ ] `"Mix"`
- [x] `"ixt"`
- [ ] `"ixta"`
:::explain
From position 1 (`i`) up to, but not including, position 4: `ixt`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
After `let t = "abc"; t.toUpperCase();`, what is `t`?
:::
- [x] `"abc"`
- [ ] `"ABC"`
:::explain
Strings never change; the new `"ABC"` was thrown away. Write `t = t.toUpperCase();` to keep it.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `[..."hi🎵"].length`?
:::
- [ ] `4`
- [x] `3`
- [ ] `2`
:::explain
The spread walks real characters: `h`, `i` and the note. (`"hi🎵".length` would be 4.)
:::
:::

:::step{type=deep-dive title="Go deeper: replaceAll, padStart and template tricks"}
**replaceAll.** `"a-b-c".replaceAll("-", " ")` gives `"a b c"`. Plain `replace` changes only the first one.

**padStart.** `String(5).padStart(2, "0")` gives `"05"`: perfect for showing `3:05` as a song length. Chapter 12 uses
it.

**Multi-line text.** Backtick strings can span several lines, and `${...}` can hold any expression:
`` `Total: ${minutes * 60} seconds` ``.

**localeCompare.** `"é".localeCompare("f")` compares text the way a dictionary in that language would, not by code
numbers. Chapter 8 shows why plain sorting gets this wrong.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read characters and pieces of text with `[i]`, `at`, `slice`, `indexOf`, `includes` and `length`.
- Tidy text with `trim`, `toLowerCase` and `toUpperCase`, remembering strings never change.
- Split with `/\s+/`, avoid the empty-text trap, and join pieces back together.
- Explain why `"🎵".length` is 2, and count real characters with `[...text]`.

:::photo{src="/lesson-images/javascript/js-07-notes.webp" alt="Handwritten notes about JavaScript strings: positions start at 0, strings never change, trim then split on runs of spaces, empty text gives one piece, one emoji has length 2, spread counts real characters" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 8: arrays, and why JavaScript sorts 10 before 9.
:::
