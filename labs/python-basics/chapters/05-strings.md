:::step{type=story title="Why strings"}
Text from the real world is messy: names typed in capitals, extra spaces, sentences pasted from
somewhere else. Before a program can use text, it usually has to clean it up.

:::mission
Write two functions in `text_tools.py`: one counts the words in a sentence (a warm-up), and one
tidies up a name.
:::
:::

:::step{type=concept title="Pieces of text"}
A string is a sequence of characters. You can read one character or a slice:

```python
word = "Python"
word[0]      # 'P'   (positions start at 0)
word[-1]     # 'n'   (negative counts from the end)
word[1:4]    # 'yth' (from 1 up to, not including, 4)
len(word)    # 6
```

Strings never change in place: methods give you a **new** string.

```python
"  hi  ".strip()      # 'hi'
"riya".upper()        # 'RIYA'
"riya sharma".title() # 'Riya Sharma'
```
:::

:::step{type=example title="Worked example: tidy a product code"}
Cleaning text is usually three moves: **split** it into pieces, **change** each piece, **join** them back.

```python
raw = "  ab-12   cd  "
parts = raw.split()        # ['ab-12', 'cd']
parts = [p.upper() for p in parts]
code = "-".join(parts)     # 'AB-12-CD'
```

1. `split()` with no argument drops all the extra spaces.
2. Each piece is changed (here, to upper case).
3. `"-".join(parts)` glues the pieces with a dash between them.

Both tasks in this chapter use some of these three moves.
:::

:::step{type=predict title="Guess first"}
:::question
What is `"a,b,,c".split(",")`?
:::
- [ ] `['a', 'b', 'c']`
- [x] `['a', 'b', '', 'c']`
- [ ] `['a,b,,c']`
- [ ] `'abc'`
:::explain
`split(",")` cuts at **every** comma, so two commas in a row leave an empty piece between them.
`split()` with no argument behaves differently: it splits on any run of spaces and never gives
empty pieces.
:::
:::

:::step{type=try title="Split and join"}
```bash run
python3 -c "
messy = '   riya     SHARMA  '
parts = messy.split()
print(parts)
print(' '.join(parts))
print(' '.join(parts).title())
"
```

`split()` breaks text into a list of words, and `' '.join(list)` glues a list back together with a
space between the pieces.
:::

:::step{type=concept title="Searching in text"}
Some quick questions you can ask a string:

```python
s = "Python is fun"
"fun" in s             # True
s.startswith("Py")     # True
s.find("is")           # 7, the position (or -1 if not found)
s.count("n")           # 2
s.replace("fun", "great")   # 'Python is great'
```
:::

:::step{type=task task=count_words title="Warm-up: count the words"}
In `text_tools.py`, make `count_words(text)` return how many words the text has. Words are
separated by one or more spaces (or tabs and new lines).

- `count_words("Python is fun")` returns `3`
- `count_words("  lots   of   spaces  ")` returns `3`
- `count_words("")` returns `0`
- `count_words("hello, world")` returns `2`
:::

:::step{type=task task=clean_name title="Tidy up a name"}
In `text_tools.py`, make `clean_name(raw)` return the name with:

- no spaces at the start or end,
- exactly one space between words,
- each word starting with a capital letter and the rest small.

So `clean_name("  riya   SHARMA ")` returns `"Riya Sharma"`, `clean_name("ARJUN")` returns
`"Arjun"`, and `clean_name("   ")` returns `""`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is `"  hi there  ".split()`?
:::
- [x] `['hi', 'there']`
- [ ] `['', 'hi', 'there', '']`
- [ ] `'hi there'`
- [ ] `['  hi there  ']`
:::explain
With no argument, `split()` splits on any run of spaces and drops the empty pieces.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `" ".join(["a", "b", "c"])`?
:::
- [ ] `'abc'`
- [x] `'a b c'`
- [ ] `['a b c']`
- [ ] `'a, b, c'`
:::explain
`join` puts the string it is called on (a space) between every piece.
:::
:::

:::step{type=deep-dive title="Text is Unicode"}
Python strings hold **Unicode** characters, so `"नमस्ते"`, `"₹"` and emoji work like any other
text. `len()` counts characters, not bytes: `len("₹")` is 1, even though it takes 3 bytes when
saved as UTF-8.

`title()` is simple: it capitalises after any non-letter, so `"o'brien"` becomes `"O'Brien"` but
`"mcdonald"` stays `"Mcdonald"`. Real name handling has many such cases, which is why serious apps
store the name exactly as the person typed it and only tidy the spaces.

Because strings cannot change, building a long text with `+=` in a loop makes a new string each
time. Collect the pieces in a list and `"".join(pieces)` once at the end.
:::

:::step{type=recap}
- Strings are sequences: index with `[0]`, slice with `[a:b]`, measure with `len()`.
- Methods return new strings: `strip`, `upper`, `lower`, `title`, `replace`.
- `split()` breaks text into words; `" ".join(words)` puts them back.
- `in`, `startswith`, `find` and `count` search inside text.
:::
