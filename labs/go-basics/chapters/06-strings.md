:::step{type=story title="Why strings"}
Names typed in capitals, extra spaces, text pasted from somewhere else: input is messy. Go keeps the
tools for cleaning it in the `strings` package, and they are worth knowing by heart.

:::mission
In `words/words.go`, count the words in a sentence (a warm-up), then tidy up a person's name.
:::
:::

:::step{type=concept title="The strings package"}
```go
strings.TrimSpace("  hi  ")           // "hi"
strings.ToUpper("riya")               // "RIYA"
strings.Fields("  a   b  c ")         // []string{"a", "b", "c"}
strings.Join([]string{"a", "b"}, "-") // "a-b"
strings.Contains("golang", "lang")    // true
strings.Split("a,b,,c", ",")          // []string{"a", "b", "", "c"}
```

Strings cannot change: every function returns a **new** string.

:::picture{name="beads-on-string"}
Every byte of text has a numbered place, starting at 0.
:::
:::

:::step{type=example title="Worked example: tidy a product code"}
Clean text in three moves: split, change each piece, join.

```go
func Code(raw string) string {
	parts := strings.Fields(raw)
	for i, p := range parts {
		parts[i] = strings.ToUpper(p)
	}
	return strings.Join(parts, "-")
}

// Code("  ab-12   cd ") is "AB-12-CD"
```

1. `strings.Fields` drops all the extra spaces.
2. The loop changes each piece in place (`parts[i] = ...`).
3. `strings.Join` glues them back with a separator.

Both tasks here use parts of this.

:::trace{title='Code("  ab-12   cd ")'}
| step | value | note |
|---|---|---|
| raw | "  ab-12   cd " | The text as it arrives. |
| strings.Fields(raw) | [ab-12 cd] | Fields splits on any run of spaces and drops them. |
| ToUpper each | [AB-12 CD] | The loop changes each slot of the slice. |
| strings.Join(parts, "-") | "AB-12-CD" | The pieces are glued back with a dash. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
How many items does `strings.Split("a  b", " ")` return? (There are two spaces.)
:::
- [ ] 2
- [x] 3
- [ ] 4
- [ ] 1
:::explain
`Split` cuts at **every** separator, so two spaces in a row leave an empty string between them:
`["a", "", "b"]`. `strings.Fields` splits on any run of spaces and never returns empty pieces, which is
usually what you want for words.
:::
:::

:::step{type=try title="Fields and slicing"}
```bash run
cat > /tmp/str.go <<'GO'
package main

import (
	"fmt"
	"strings"
)

func main() {
	parts := strings.Fields("   riya     SHARMA  ")
	fmt.Printf("%q\n", parts)
	w := parts[1]
	fmt.Println(w[:1], strings.ToLower(w[1:]))
}
GO
go run /tmp/str.go
```

`w[:1]` is the first byte and `w[1:]` the rest: slicing works on strings too.
:::

:::step{type=task task=count_words title="Warm-up: count the words"}
In `words/words.go`, make `CountWords(text string) int` count the words separated by spaces, tabs or
new lines.

- `CountWords("Go is fun")` returns `3`
- `CountWords("  lots   of   spaces  ")` returns `3`
- `CountWords("")` returns `0`
:::

:::step{type=concept title="Building strings efficiently"}
Joining many pieces with `+` makes a new string each time. For a loop, use `strings.Builder`:

```go
var b strings.Builder
for i := 0; i < 3; i++ {
	b.WriteString("go ")
}
s := b.String()   // "go go go "
```

For a fixed list, `strings.Join` is simpler.
:::

:::step{type=task task=clean_name title="Tidy up a name"}
In `words/words.go`, make `CleanName(raw string) string` return the name with no spaces at either end,
one space between words, and each word starting with a capital letter followed by small letters.

- `CleanName("  riya   SHARMA ")` returns `"Riya Sharma"`
- `CleanName("ARJUN")` returns `"Arjun"`
- `CleanName("   ")` returns `""`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `len(strings.Fields("  go  is fun "))`?
:::
- [x] `3`
- [ ] `5`
- [ ] `7`
- [ ] `1`
:::explain
`Fields` splits on runs of spaces and never returns empty pieces: `go`, `is`, `fun`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Can you change a Go string in place, like `s[0] = 'G'`?
:::
- [ ] Yes
- [x] No: strings are immutable
- [ ] Only for ASCII text
- [ ] Only with a pointer
:::explain
Strings cannot change; every function returns a new string. Build new text with `+`, `Join` or a `strings.Builder`.
:::
:::

:::step{type=deep-dive title="Bytes, runes and capital letters"}
`w[:1]` takes the first **byte**. For names in English that is the first letter, but `"émile"` starts
with a two-byte letter, and slicing one byte would cut it in half. Unicode-safe code converts to runes
first: `r := []rune(w); string(unicode.ToUpper(r[0])) + string(r[1:])`.

`strings.Title` used to capitalise words but was deprecated because "title case" differs between
languages; `golang.org/x/text/cases` does it properly per language. Real apps usually keep the name
exactly as the person typed it and only tidy the spaces.
:::

:::step{type=recap}
- `strings.Fields` splits into words; `strings.Join` puts them back.
- `TrimSpace`, `ToUpper`, `ToLower`, `Contains`, `Split` cover most cleaning.
- Strings are immutable; use `strings.Builder` to build one in a loop.
- Slicing a string slices bytes: think in runes for non-English text.
:::
