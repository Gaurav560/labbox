:::step{type=story title="How big is a piece?"}
So far Fieldbook embedded whole sections: one vector for each of the manual's 31 numbered parts. That worked because
somebody wrote the manual in short, tidy sections of 52 to 95 words. Real documents are rarely that kind: a 40-page
research report, a 300-page procedures book, a scanned letter with no headings at all.

You cannot embed a whole book as one vector: the model reads only the first few hundred words, and one point cannot stand
for a hundred different topics. So documents are cut into pieces, called **chunks**, and each chunk gets its own vector.
How you cut decides what search can find. Cut too small and a chunk loses the context that makes it mean anything; cut
too big and its vector becomes a blurry average, and the model has to read pages to find one sentence.

This chapter writes the two most common cutters and then does what most tutorials skip: **measures** six ways of
cutting on real questions.

:::mission
Write a word-window chunker with overlap and a section chunker that follows the document's headings, then compare six
ways of cutting the manual by how often search finds the right section and how much the model would have to read.
:::
:::

:::step{type=concept title="Windows of words, with overlap" file="04-chunking/fieldbook.py" line="112-116"}
The simplest cutter ignores the document's structure: take `size` words, then the next `size` words, and so on. Its
weakness: a sentence cut in half lands in two chunks and makes sense in neither. The usual fix is **overlap**: each window
starts a little before the previous one ended, so a sentence near a border appears whole in at least one chunk.

:::trace{title="word_chunks over ten words, size 4, overlap 2"}
| window | starts at word | words | note |
|---|---|---|---|
| 1 | 0 | 1 2 3 4 | |
| 2 | 2 | 3 4 5 6 | starts size - overlap = 2 words later |
| 3 | 4 | 5 6 7 8 | |
| 4 | 6 | 7 8 9 10 | reaches the last word: stop here |
:::

The stopping rule matters. Without it, the loop would make one more window starting at word 8, "9 10", which only
repeats the end of window 4.
:::

:::step{type=task task=word_chunks title="Your turn: windows of words" file="04-chunking/fieldbook.py" line="112-116"}
Write `word_chunks(text, size=120, overlap=20)`:

1. Split the text into words with `text.split()`.
2. Start a window every `size - overlap` words: `range(0, len(words), size - overlap)`.
3. Join each window's words with single spaces and add it to the list.
4. Stop right after the window that reaches the last word (`start + size >= len(words)`).

Press **Check**.
:::

:::step{type=concept title="Cutting along the document's own lines" file="04-chunking/fieldbook.py" line="119-125"}
The manual already has structure: every section starts with a line like `## FM-4.2 Meeting a tiger`. Cutting there gives
chunks that are about **one thing** each, and every chunk carries its number and title, which a word window loses:

```text
# Vanrai Hills Wildlife Sanctuary: Field Manual        <- the document's title: not a section
...
## FM-4.2 Meeting a tiger                               <- heading: id "FM-4.2", title "Meeting a tiger"
If you meet a tiger, stand still, keep facing it       <- text, over several lines
and do not run: running can trigger a chase. ...
```

`markdown.split("\n## ")` cuts the text at every heading. The first piece is everything before the first section (the
title and introduction), so skip it with `[1:]`. In each piece, `partition("\n")` splits the heading line from the body,
and `" ".join(body.split())` squeezes line breaks and runs of spaces into single spaces.

Most real chunkers combine both ideas: follow headings and paragraphs, and fall back to word or token windows only when a
part is too long.
:::

:::step{type=task task=section_chunks title="Your turn: one chunk per section" file="04-chunking/fieldbook.py" line="119-125"}
Write `section_chunks(markdown)`. For every piece of `markdown.split("\n## ")[1:]`:

1. Split the heading line from the body with `partition("\n")`.
2. Split the heading into its first word (the id) and the rest (the title), again with `partition(" ")`.
3. Squeeze the body's whitespace, and add `{"id": ..., "title": ..., "text": ...}` to the list.

```bash run
cd /workspace/04-chunking && python compare_chunks.py
```

Press **Check**.
:::

:::step{type=history title="Chunks, from memory research to RAG"}
:::before{title="Whole documents"}
Early search engines ranked whole documents. A 200-page report that mentioned your topic once, on page 143, competed with
a one-page note about nothing else, and the reader still had to find page 143.
:::

The word **chunk** comes from psychology: in **1956** George A. Miller's famous paper on "the magical number seven"
described how people remember more by grouping information into meaningful chunks. Information retrieval took up the idea
in the **1990s** as **passage retrieval**: researchers such as James Callan (**1994**) showed that ranking documents by
their best passage beats ranking them as a whole. With RAG the passage became the unit of everything: what gets embedded,
what gets found, and what the model reads. Libraries made fixed-size windows with overlap the default (LangChain's text
splitters, **2022**), and the default is often where people stop, which is why measuring matters.

:::solved
**The right unit for search.** A chunk about one thing gets a clear vector, is found for the right questions, and gives
the model just what it needs to read.
:::

:::timeline
- **1956** Miller: people remember in chunks.
- **1994** Passage retrieval beats whole documents.
- **2022** Fixed-size chunks with overlap become the library default.
:::
:::

:::step{type=try title="Six ways to cut the manual, measured" file="04-chunking/compare_chunks.py" line="11-45"}
`compare_chunks.py` asks the 22 test questions whose answers are in the manual (from `data/questions.json`; each lists the
section that answers it). For each way of cutting it embeds the chunks, searches, and counts:

| Column | Means |
|---|---|
| hit@1 | how often the **best** chunk contains the right section |
| hit@3 | how often one of the **three** best does |
| words read | how many words the three best chunks hold: what the model would have to read |

A window gets credit for every section it overlaps, so big windows are not punished for crossing borders.

```text
$ python compare_chunks.py
22 questions, 31 sections, 2008 words

 hit@1  hit@3 words read  chunks  way of cutting
   73%    91%         45     134  windows of 15 words
   77%   100%        180      41  windows of 60 words, 10 overlapping
   77%    95%        864       9  windows of 300 words, 50 overlapping
   91%   100%        112      68  windows of 40 words inside each section
   86%   100%        194      31  one chunk per section
   91%   100%        204      31  one chunk per section, title first
```

What the numbers say:

1. **Tiny windows (15 words)** are cheap to read (45 words) but lose context: only 73% right at the first try.
2. **Huge windows (300 words)** cover several sections each, so you would expect them to contain the answer; yet hit@1 is
   only 77%, and the model would read **864 words** per question, 19 times more than the tiny windows. Their vectors are
   averages of several topics, so they match many questions a little and none well.
3. **Following the sections wins.** Small windows that never cross a section border and whole sections with their title
   both reach **91%** at the first try. Adding the title helps a whole section (86% to 91%): "Meeting a tiger" is exactly
   the kind of words a question uses.

From now on Fieldbook uses one chunk per section, title first (`chunk_text` in `fieldbook.py`), plus one chunk per
patrol report. For long documents without sections, 40 to 60 word windows with some overlap are a sound start, and
measuring on your own questions is how you decide.
:::

:::step{type=predict title="Guess first"}
:::question
A 300-word window contains the answer to a question. Why might search still not rank it first?
:::
- [x] Its vector averages several topics, so it is only partly similar to any one question
- [ ] Long chunks are cut off before embedding
- [ ] Search always prefers short chunks
:::explain
One vector per chunk means one "average meaning". A chunk about one thing has a sharp meaning; a chunk about five things
has a blurry one.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is overlap for?
:::
- [ ] Making more chunks so search is slower
- [x] Keeping a sentence that crosses a window border whole in at least one chunk
- [ ] Removing duplicate words
:::explain
Overlap costs a few extra chunks and saves the sentences that would otherwise be cut in half.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does every chunk keep its section id (FM-4.2)?
:::
- [ ] The embedding model needs it
- [x] So that the answer can cite its source, and so a search result can be traced back to the document
- [ ] To make the chunk longer
:::explain
Metadata travels with the chunk: the id, the title, and later the zone, the date and the kind of document (chapter 8
filters on them).
:::
:::

:::step{type=deep-dive title="Go deeper: chunking real documents"}
**Tokens, not words.** Models count tokens (about three quarters of a word in English). Production chunkers measure in
tokens and keep chunks safely under the embedding model's limit (512 tokens for bge-small).

**Structure first.** Split on headings, then paragraphs, then sentences, and fall back to windows only for long blocks.
Tables, code and lists need their own rules: half a table is useless.

**Context for small chunks.** A chunk saying "Change them every 21 days" means little alone. Prefix each chunk with its
document and section title (as `chunk_text` does), or retrieve small chunks and give the model the whole section they
came from ("small to big" retrieval).

**Re-chunking costs.** Changing how you chunk means re-embedding everything. Store the original documents, not only the
chunks.
:::

:::step{type=recap}
You can now:

- cut text into windows of words with overlap, and stop at the right place;
- cut a document along its own headings, keeping an id and a title with every chunk;
- measure chunking by hit rate and by how much the model must read;
- explain why chunks about one thing beat both tiny and huge ones.

That ends Part 1. Next, chapter 5: the first of the indexes inside every vector database.

:::photo{src="/lesson-images/rag/rag-04-notes.webp" alt="Handwritten notes about chunking: Too small: no context; Too big: a blurry average; Follow the headings; Title first helps; Measure hit rate and words read" ai="true"}
One page of notes for this chapter.
:::
:::
