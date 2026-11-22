:::step{type=story title="Why does a shop's computer think samosa and SAMOSA are different?"}
Search for "samosa" in some shop apps and nothing comes up, because the menu says "SAMOSA". Type your name with a
space at the end into a form, and suddenly the site says it does not know you. Have you ever wondered why
computers are so fussy about text?

To a computer, text is a row of characters, and `c` and `C` are simply different characters. A space is a
character too. So the same word can hide in a hundred messy shapes, and programs that work with real people's
typing spend a surprising amount of effort **cleaning text up**.

Pocket reads lines from receipts and names that people typed. Today you teach it to tidy them.

:::mission
Write `count_words`, which counts the words in any messy text, and `clean_name`, which turns a badly typed name
into a tidy one.
:::
:::

:::step{type=concept title="A string is a row of characters"}
You have used strings since chapter 1. Now look inside one. A string is a **sequence**: characters in a fixed
order, each with a position number, its **index**. As with lists in chapter 5, positions start at **0**. And
Python lets you count from the end too, with negative numbers:

| Character | `S` | `a` | `m` | `o` | `s` | `a` |
|---|---|---|---|---|---|---|
| Index from the start | 0 | 1 | 2 | 3 | 4 | 5 |
| Index from the end | -6 | -5 | -4 | -3 | -2 | -1 |

```python
word = "Samosa"
len(word)      # 6: six characters
word[0]        # "S": the first
word[-1]       # "a": the last
word[0:3]      # "Sam": a slice, from 0 up to (not including) 3
word[2:]       # "mosa": from 2 to the end
word[::-1]     # "asomaS": the whole string, backwards
```

A **slice** `[start:stop]` gives a new string from `start` up to, but not including, `stop`, just like
`range`. Leave out a side and it goes to the edge.

:::picture{name="beads-on-string"}
A string is beads on a thread: each bead a character, each with its place in the row.
:::

:::

:::step{type=predict title="Guess first"}
:::question
`word = "Samosa"` has 6 characters. What happens with `word[6]`?
:::
- [ ] It gives `"a"`, the last character
- [ ] It gives an empty string `""`
- [x] An `IndexError`
:::explain
Six characters have the positions 0 to 5. Position 6 does not exist, so Python stops with
`IndexError: string index out of range`. To get the last character, use `word[-1]` or `word[len(word) - 1]`.
:::
:::

:::step{type=try title="Tidy a receipt line, one method at a time" file="07-strings/receipt.py" line="2-9"}
Strings come with built-in tools called **methods**. You call a method with a dot after the string:
`line.strip()`. Open `receipt.py` and run it:

```bash run
cd /workspace/07-strings && python3 receipt.py
```

```text
'   PANEER roll x2   '
'PANEER roll x2'
paneer roll x2
Paneer Roll X2
['PANEER', 'roll', 'x2']
20 14
```

`repr(...)` shows a string *with* its quotes, so you can see the invisible spaces. Then, line by line:

| Method | Does | Result |
|---|---|---|
| `.strip()` | removes spaces at both ends | `'PANEER roll x2'` |
| `.lower()` | all small letters | `paneer roll x2` |
| `.title()` | a capital at the start of each word | `Paneer Roll X2` |
| `.split()` | cuts into a list of words | `['PANEER', 'roll', 'x2']` |

And `len` says the line was 20 characters, and only 14 without the spaces around it. Six invisible spaces:
exactly the kind of thing that makes a computer say "user not found".
:::

:::step{type=concept title="Strings never change: methods make new ones"}
Try to change one letter of a string:

```python
text = "book"
text[0] = "B"
```

```text
TypeError: 'str' object does not support item assignment
```

Strings are **immutable**: once made, they never change. That is why every method *gives back a new string*
and leaves the old one alone. If you want to keep the result, store it:

```python
name = "  asha "
name.strip()          # gives back "asha", but name is still "  asha "
name = name.strip()   # now name is "asha"
```

Because each method gives back a string, you can **chain** them, left to right:

```python
"  PANEER roll  ".strip().lower()    # "paneer roll"
```

Python works it out step by step: first `.strip()`, then `.lower()` on that result.
:::

:::step{type=example title="Worked example: split with and without an argument"}
`split` is the most useful string method of all, and it has a secret. Look at the difference:

```bash run
python3 -c "print('  lots   of   spaces  '.split(' ')); print('  lots   of   spaces  '.split())"
```

```text
['', '', 'lots', '', '', 'of', '', '', 'spaces', '', '']
['lots', 'of', 'spaces']
```

1. `split(" ")` cuts at **every single space**. Two spaces in a row leave an empty string `''` between them,
   so you get eleven pieces, most of them empty.
2. `split()` with **no argument** is smarter: it treats any run of spaces, tabs or new lines as one gap, and
   ignores them at both ends. Three real words, three pieces.

When the text comes from people, `split()` with no argument is almost always what you want. You can split at
anything else, too: `"rice,milk,,bread".split(",")` gives `['rice', 'milk', '', 'bread']`.
:::

:::step{type=task task=count_words title="Your turn: count the words"}
Open `text_tools.py` and make `count_words(text)` give back how many words the text has. Words are separated
by spaces, sometimes several in a row, and sometimes tabs or new lines.

`count_words("Python is fun")` gives `3`, `count_words("  lots   of   spaces  ")` gives `3`, and an empty
string gives `0`.

```bash run
cd /workspace/07-strings && python3 -c "from text_tools import count_words; print(count_words('  lots   of   spaces  '))"
```

Then press **Check**.
:::

:::step{type=concept title="split and join: taking text apart and putting it back"}
`split` turns a string into a list of pieces. Its partner, `join`, does the opposite: it glues a list of
strings together, with a string of your choice in between. Notice who does the joining: the **glue** comes
first.

```python
" ".join(["Riya", "Sharma"])        # "Riya Sharma"
"-".join(["2026", "11", "22"])      # "2026-11-22"
", ".join(["rice", "milk"])         # "rice, milk"
```

So a classic way to fix messy spacing is to take the text apart with `split()` (which throws the extra spaces
away), then put it back with `" ".join(...)`, one space between each word.

Two more tools you will reach for:

- `"Roll" in "Paneer Roll"` is `True`: `in` asks whether one string appears inside another. It is
  case-sensitive, so `"roll" in "Paneer Roll"` is `False`. Compare lowered text when case should not matter:
  `"roll" == "Roll".lower()` is `True`.
- f-strings can line text up in columns: `f"{'rice':<8}|{15:>5}|"` gives `rice    |   15|`. `<8` pads to 8
  characters on the left side, `>5` to 5 on the right. Receipts love this.
:::

:::step{type=task task=clean_name title="Your turn: a tidy name"}
People type names in every possible way. In `text_tools.py`, make `clean_name(raw)` give back the name tidied
up: no spaces at the ends, exactly one space between words, and each word starting with a capital.

`clean_name("  riya   SHARMA ")` gives `"Riya Sharma"`, `clean_name("ARJUN")` gives `"Arjun"`, and a name
that is only spaces gives `""`.

Think of it as three moves: take the words apart, glue them back with single spaces, then fix the capitals.

```bash run
cd /workspace/07-strings && python3 -c "from text_tools import clean_name; print(repr(clean_name('  riya   SHARMA ')))"
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is `"Pocket"[1:4]`?
:::
- [ ] `"Poc"`
- [x] `"ock"`
- [ ] `"ocke"`
:::explain
The slice starts at index 1 (`o`) and stops before index 4, so it takes positions 1, 2 and 3: `ock`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
After `name = "  Asha  "` and then `name.strip()`, what is in `name`?
:::
- [ ] `"Asha"`
- [x] `"  Asha  "`
- [ ] An error
:::explain
Strings never change. `strip()` gave back a new string, but nobody stored it, so `name` is untouched. Write
`name = name.strip()` to keep the result.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `"-".join(["a", "b", "c"])` give?
:::
- [x] `"a-b-c"`
- [ ] `"-a-b-c-"`
- [ ] `["a-", "b-", "c"]`
:::explain
`join` puts the glue only *between* the pieces, never at the ends.
:::
:::

:::step{type=deep-dive title="Go deeper: characters from every language"}
Python strings are **Unicode**: they hold characters from every writing system in the world, not just English
letters. The **Rosetta Stone** carries one decree in three scripts (Egyptian hieroglyphs, Demotic and Greek), and
that is how hieroglyphs were finally read. A single Python string could hold all three.

:::photo{src="/lesson-images/python/rosetta-stone.webp" alt="The Rosetta Stone, a dark grey stone slab covered in three bands of carved writing, in the British Museum" credit="Hans Hillewaert" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Rosetta_Stone.JPG"}
The Rosetta Stone, British Museum: one text, three scripts.
:::

Try it with a Hindi word:

```bash run
python3 -c "print(len('दाल'), 'दाल'[0])"
```

```text
3 द
```

The Hindi word for lentils, दाल (dal), is 3 characters to Python: द, the vowel sign ा, and ल. On screen the vowel sign
joins its letter, so it *looks* like two letters, but Python counts what is stored. Emojis, Tamil, Chinese,
Arabic: they are all just characters to Python.

On disk and on the network, text has to become bytes, and the usual way is **UTF-8**, which uses one byte for
English letters and two to four for others. You will see `encoding="utf-8"` when you open files in chapter 14:
that is the reason.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Reach any character by its index (from 0, or from the end with -1) and cut slices like `text[0:3]`.
- Tidy text with `strip`, `lower`, `upper`, `title` and `replace`, remembering methods give back *new* strings.
- Take text apart with `split()` and put it together with `"glue".join(...)`.
- Ask `in` questions, compare text without caring about capitals, and line up columns with f-strings.

:::photo{src="/lesson-images/python/py-07-notes.webp" alt="Handwritten notes about Python strings: indexing, slicing and methods" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 8: lists, Pocket's favourite way to keep many things in one place.
:::
