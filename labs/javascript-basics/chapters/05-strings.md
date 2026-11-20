:::step{type=story title="Why strings"}
Names, messages, addresses, product codes: most data people type is text, and people type it messily.
Extra spaces, odd capitals, the wrong separator. Cleaning text so a program can trust it is one of the
most common jobs in real code.

:::mission
In `words/words.js`, count the words in a sentence, then tidy a name typed in a hurry.
:::

:::picture{name="messy-form" concept="Capital first, the rest small"}
The cleaned name keeps the same words with one space and a capital at the start of each.
:::
:::

:::step{type=concept title="A string is a row of characters"}
Each character in a string has a numbered position, starting at **0**:

```javascript
const word = "tea cup";
word.length     // 7: the space counts too
word[0]         // "t"
word[4]         // "c"
word.slice(0, 3)  // "tea": from 0 up to (not including) 3
```

Strings never change in place. Methods like `toUpperCase()` give back a **new** string and leave the
original alone.

:::picture{name="beads-on-string" concept="A string is a row of characters"}
Every character has a numbered place, starting at 0.
:::
:::

:::step{type=concept title="Cleaning tools"}
The everyday tools for messy text:

```javascript
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

:::step{type=example title="Worked example: tidy a product code"}
Cleaning text is usually three moves: **split**, **change** each piece, **join**.

```javascript
function code(raw) {
  const parts = raw.trim().split(/\s+/);           // 1
  const upper = parts.map((p) => p.toUpperCase());  // 2
  return upper.join("-");                           // 3
}
```

1. Trim the ends, then split on runs of spaces.
2. Change each piece, here to upper case (`map` is in chapter 9; read it as "do this to each").
3. Glue the pieces back with a dash.

:::trace{title='code("  ab-12   cd ")'}
| step | value | note |
|---|---|---|
| raw | "  ab-12   cd " | The text as it arrives. |
| raw.trim() | "ab-12   cd" | trim removes the spaces at both ends only. |
| .split(/\s+/) | ["ab-12", "cd"] | Split on any run of spaces. |
| toUpperCase each | ["AB-12", "CD"] | Each piece is changed on its own. |
| .join("-") | "AB-12-CD" | The pieces are glued back with a dash. |
:::

:::picture{name="cut-and-glue" concept="Cleaning tools"}
Split the product code into words, change each word, then join the pieces with one dash.
:::
:::

:::step{type=predict title="Guess first"}
:::question
What does `"".trim().split(/\s+/)` give?
:::
- [ ] `[]`
- [x] `[""]`
- [ ] `0`
- [ ] An error
:::explain
Splitting empty text gives an array with one empty string, so its length is 1, not 0. That is the
case `countWords` must catch: text with nothing in it has no words.
:::
:::

:::step{type=try title="Split and join"}
```bash run
node -e 'const s = "  lots   of   spaces  "; console.log(s.split(" "), s.trim().split(/\s+/), "".trim().split(/\s+/))'
```
:::

:::step{type=task task=count_words title="Warm-up: count the words"}
In `words/words.js`, make `countWords(text)` return how many words the text has, however many spaces
are between them:

- `countWords("JavaScript is fun")` returns `3`
- `countWords("  lots   of   spaces  ")` returns `3`
- `countWords("")` and `countWords("   ")` return `0`

:::picture{name="word-islands" concept="Cleaning tools"}
Count the islands of letters. A wider gap still separates just two words.
:::
:::

:::step{type=concept title="Capital first, the rest small"}
To make a word look like a name, change its first letter and the rest separately:

```javascript
const w = "sHARMA";
w[0].toUpperCase()          // "S"
w.slice(1).toLowerCase()    // "harma"
w[0].toUpperCase() + w.slice(1).toLowerCase()   // "Sharma"
```

Do that to every word, then join them with one space.

:::picture{name="initial-and-tail" concept="Capital first, the rest small"}
The first letter and the tail take different paths before they rejoin.
:::
:::

:::step{type=task task=clean_name title="Tidy up a name"}
Make `cleanName(raw)` turn a name typed in a hurry into a tidy one:

- `cleanName("  riya   SHARMA ")` returns `"Riya Sharma"`
- `cleanName("ARJUN")` returns `"Arjun"`
- `cleanName("   ")` returns `""`

:::picture{name="name-register" concept="Capital first, the rest small"}
Give every word in the name its own initial before writing the whole name on the register.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `"masala".slice(0, 3)`?
:::
- [x] `"mas"`
- [ ] `"masa"`
- [ ] `"ala"`
- [ ] `"m"`
:::explain
`slice(0, 3)` takes positions 0, 1 and 2: it stops **before** 3.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
After `let s = "tea"; s.toUpperCase();` what is `s`?
:::
- [x] `"tea"`
- [ ] `"TEA"`
- [ ] `undefined`
- [ ] An error
:::explain
Strings never change in place: `toUpperCase()` returns a new string, which was thrown away here. Write
`s = s.toUpperCase()` to keep it.
:::
:::

:::step{type=deep-dive title="Unicode and emoji"}
JavaScript strings are stored as **UTF-16**: most characters take one slot, but emoji and some
scripts take two, so `"😀".length` is `2`. `for...of` and `[..."😀"]` walk real characters, which is
why they are safer than counting positions by hand.

For comparing text in human order (with accents and different languages), use `a.localeCompare(b)`
instead of `<`; you will meet it again when sorting in chapter 9.

:::picture{name="utf-slots" concept="A string is a row of characters"}
One smiling face takes two UTF-16 code units, even though it is one Unicode code point.
:::
:::

:::step{type=recap title="Chapter done"}
- Characters are numbered from 0; `length` counts them all, spaces included.
- `trim`, `split(/\s+/)`, `join` and `toUpperCase` clean text.
- Strings never change in place: methods return new strings.
- Empty text needs its own care: `"".split(...)` is not empty.

:::picture{name="unchanged-string" concept="A string is a row of characters"}
Changing the case makes a new string. The original letters remain in their own row.
:::
:::
