:::step{type=story title="How long is the name José?"}
Count the letters: J, o, s, é. Four. Ask Go:

```text
5
```

Five. Go is not wrong; it is answering a different question. Go strings are made of **bytes**, and the é takes two of
them. It sounds like a detail until Parcel delivers to Bengaluru, Köln and São Paulo, and every address with an accent,
or in Hindi, or with an emoji, gets counted, cut and capitalised wrongly. Today you learn to handle text the way the
world writes it.

:::mission
Write `CountWords`, which counts the words in messy text, and `CleanName`, which tidies a badly typed name.
:::
:::

:::step{type=try title="Bytes and runes" file="08-strings/jose.go" line="10-16"}
Open `jose.go` and run it:

```go
word := "José"
fmt.Println(len(word), utf8.RuneCountInString(word))
fmt.Println(word[3], string(word[3]))
for i, r := range word {
	fmt.Println(i, string(r))
}
```

```bash run
cd /workspace/08-strings && go run jose.go
```

```text
5 4
195 Ã
0 J
1 o
2 s
3 é
```

- `len(word)` counts **bytes**: 5. `utf8.RuneCountInString` counts characters: 4.
- `word[3]` is one **byte**, 195, which on its own is half of an é: printed alone it becomes `Ã`, a broken character.
- `range` over a string is smart: it walks by **runes** (whole characters), and the position jumps to where each one
  starts.

Go stores text as UTF-8, the encoding Ken Thompson and Rob Pike designed in 1992, on a placemat in a New Jersey diner.
It is now used by almost every web page in the world.
:::

:::step{type=concept title="The everyday string toolbox"}
The `strings` package (`import "strings"`) has the tools for messy text:

| Code | Gives |
|---|---|
| `strings.TrimSpace(s)` | s without spaces, tabs or new lines at the ends |
| `strings.Fields(s)` | the words of s, split on any run of spaces |
| `strings.Split(s, ",")` | the pieces between commas, empty ones included |
| `strings.ToUpper(s)`, `ToLower` | capitals or small letters, for every script |
| `strings.Contains(s, "x")` | does it appear inside? |
| `strings.Join(parts, " ")` | the pieces glued back together |

Strings never change in Go: every function gives back a **new** string.
:::

:::step{type=try title="Tidy an address typed in a hurry" file="08-strings/tidy.go" line="10-15"}
```bash run
cd /workspace/08-strings && go run tidy.go
```

```text
[   12 mg ROAD,  pune  ]
[12 mg ROAD,  pune]
[12 mg ROAD, pune] 4
PUNE true [a b  c]
```

The square brackets make the spaces visible. `TrimSpace` cleaned the ends; `Fields` found the 4 words however many
spaces sat between them. And look at `Split("a,b,,c", ",")`: four pieces, one of them **empty**, because Split cuts at
every single comma. `Fields` is usually what you want for words.
:::

:::step{type=task task=count_words title="Your turn: count the words"}
Open `words.go` and make `CountWords(text)` count the words separated by spaces, tabs or new lines.

`CountWords("Go is fun")` gives `3`, `CountWords("  lots   of   spaces  ")` gives `3`, and `CountWords("")` gives `0`.

```bash run
cd /workspace/08-strings && go run run.go
```

Then press **Check**.
:::

:::step{type=example title="Worked example: capital first, by runes"}
```go
func Capitalise(word string) string {
	runes := []rune(strings.ToLower(word))
	if len(runes) == 0 {
		return ""
	}
	runes[0] = unicode.ToUpper(runes[0])
	return string(runes)
}

Capitalise("éLAN")   // "Élan"
```

1. `[]rune(...)` turns the string into a slice of whole characters, so position 0 is the whole é, not half of it.
2. `unicode.ToUpper` makes one rune a capital (`import "unicode"`).
3. `string(runes)` turns it back into a string.

Cutting by bytes, `word[:1]`, would have split the é in two. Runes keep the world's letters whole.
:::

:::step{type=predict title="Guess first"}
:::question
What is `len("naïve")`?
:::
- [ ] `5`
- [x] `6`
- [ ] `4`
:::explain
`len` counts bytes, and ï takes two. There are 5 characters but 6 bytes.
:::
:::

:::step{type=task task=clean_name title="Your turn: a tidy name"}
In `words.go`, make `CleanName(raw)` return the name with no spaces at either end, one space between words, and each word
starting with a capital letter followed by small letters.

`CleanName("  riya   SHARMA ")` gives `"Riya Sharma"`, `CleanName("ARJUN")` gives `"Arjun"`, and `CleanName("   ")`
gives `""`.

```bash run
cd /workspace/08-strings && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which counts the characters of a string, not its bytes?
:::
- [ ] `len(s)`
- [x] `utf8.RuneCountInString(s)`
:::explain
`len` is bytes. Runes are whole characters.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `strings.Fields("  a  b ")` give?
:::
- [x] `[a b]`
- [ ] `[ a  b ]`
- [ ] `[a  b]`
:::explain
`Fields` splits on any run of white space and drops the empty pieces.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `range` over a string give you?
:::
- [ ] Each byte
- [x] Each rune (whole character), with the byte position where it starts
:::explain
That is why the positions jumped in `jose.go`: the é starts at byte 3 and takes two bytes.
:::
:::

:::step{type=deep-dive title="Go deeper: strings.Builder, byte slices and normalisation"}
**strings.Builder.** Joining many pieces with `+` makes a new string each time. In a loop, use a builder:
`var b strings.Builder; b.WriteString("go "); s := b.String()`.

**[]byte.** Files and networks deliver bytes. `[]byte(s)` and `string(b)` convert, and the `bytes` package mirrors
`strings` for byte slices.

**Normalisation.** "é" can be one rune or two (an e plus an accent). The `golang.org/x/text/unicode/norm` package makes
them the same before comparing.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Explain bytes versus runes: `len("José")` is 5, but it has 4 characters.
- Walk text by characters with `range`, and convert to `[]rune` to cut or capitalise safely.
- Tidy text with `TrimSpace`, `Fields`, `ToUpper`, `ToLower` and `Join`.
- Tell `Fields` (words) from `Split` (every separator, empty pieces included).

:::photo{src="/lesson-images/go/go-08-notes.webp" alt="Handwritten notes about Go strings: len counts bytes, Jose with an accent has 5 bytes and 4 letters, range walks by rune, Fields for words, rune slice to cut safely" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 9: more slices, and the secret two slices can share.
:::
