:::step{type=story title="How big is a piece?"}
So far Fieldbook embedded whole sections: one vector for each of the manual's 31 numbered parts. That worked because
somebody wrote the manual in short, tidy sections of 52 to 95 words each. Real documents are rarely like that: a 40-page
research report, a 300-page procedures book, a scanned letter with no headings at all.

You cannot embed a whole book as one vector, for two reasons:

1. **The model reads only so much.** An embedding model has a limit on how much text it reads; bge-small, this course's
   model, reads at most 512 **tokens** (the pieces a model cuts text into, about three quarters of an English word
   each), so about 380 words. Everything after that is cut off and never seen.
2. **One vector cannot stand for many topics.** A vector describes what a text is about. A text about a hundred things
   gets one vector that is a little about everything and clearly about nothing.

So documents are cut into pieces, called **chunks**, and each chunk gets its own vector. How you cut decides what search
can find:

- **Too small**, and a chunk loses the context that makes it mean anything ("Change them every 21 days": change what?).
- **Too big**, and its vector becomes a blurry average of several topics, and the model has to read pages to find one
  sentence.

This chapter writes the two most common cutters and then does what most tutorials skip: it **measures** six ways of
cutting the manual on real questions.

:::mission
Write a word-window chunker with overlap and a section chunker that follows the document's headings, then compare six
ways of cutting the manual by how often search finds the right section and how much the model would have to read.
:::
:::

:::step{type=concept title="Windows of words, with overlap" file="04-chunking/fieldbook.py" line="112-116"}
The simplest cutter ignores the document's structure entirely. It takes the first `size` words, then the next `size`
words, and so on, like sliding a window along the text. Each position of the window is one chunk.

Its weakness: a window ends wherever the word count says, often in the middle of a sentence. A sentence cut in half lands
in two chunks and makes full sense in neither.

The usual fix is **overlap**: each window starts a little **before** the previous one ended, so the last few words of
one chunk are repeated at the start of the next. A sentence that crosses a border then appears whole in at least one of
the two chunks. The cost is a few extra chunks and some repeated words.

Here is the rule with small numbers, so you can follow every step. Ten words, windows of 4 words (`size=4`), each
repeating 2 words of the one before (`overlap=2`). Each new window starts `size - overlap = 2` words after the last one:

:::trace{title="word_chunks over ten words, size 4, overlap 2"}
| window | starts at word | words | note |
|---|---|---|---|
| 1 | 0 | 1 2 3 4 | |
| 2 | 2 | 3 4 5 6 | starts size - overlap = 2 words later; repeats 3 and 4 |
| 3 | 4 | 5 6 7 8 | |
| 4 | 6 | 7 8 9 10 | reaches the last word: stop here |
:::

The stopping rule matters. Without it, the loop would go on to make a window starting at word 8, "9 10", which only
repeats the end of window 4 and adds nothing.
:::

:::step{type=task task=word_chunks title="Your turn: windows of words" file="04-chunking/fieldbook.py" line="112-116"}
Write `word_chunks(text, size=120, overlap=20)` in `04-chunking/fieldbook.py`:

1. Split the text into words with `text.split()`.
2. Start a window every `size - overlap` words: `range(0, len(words), size - overlap)`.
3. For each start, join that window's words, `words[start:start + size]`, with single spaces, and add it to the list.
4. Stop right after the window that reaches the last word: when `start + size >= len(words)`, `break`.

The usual slip is the stopping rule: without the `break`, you get extra windows that only repeat the end. The check
uses short texts where an extra window is easy to spot.

Press **Check**.
:::

:::step{type=concept title="Cutting along the document's own lines" file="04-chunking/fieldbook.py" line="119-125"}
The manual already has structure. It is a **Markdown** file (plain text where a line starting with `##` is a heading),
and every section starts with a heading line like `## FM-4.2 Meeting a tiger`. Cutting at those lines gives chunks that
are each about **one thing**, and every chunk keeps its section number and title, which a word window loses:

```text
# Vanrai Hills Wildlife Sanctuary: Field Manual        <- the document's title: not a section
...
## FM-4.2 Meeting a tiger                               <- heading: id "FM-4.2", title "Meeting a tiger"
If you meet a tiger, stand still, keep facing it       <- the section's text, over several lines
and do not run: running can trigger a chase. ...
```

Three string methods do all the work:

1. `markdown.split("\n## ")` cuts the whole file at every heading (a line break followed by `## `). The first piece is
   everything before the first section (the document's title and introduction), so you skip it with `[1:]`.
2. In each piece, `piece.partition("\n")` splits at the **first** line break only. It gives three parts: the heading
   line, the line break itself, and the body. So `heading, _, body = piece.partition("\n")`.
3. `heading.partition(" ")` splits the heading at its first space: `"FM-4.2"` (the id) and `"Meeting a tiger"` (the
   title).

Finally, `" ".join(body.split())` cleans the body: `split()` with no argument splits on any run of spaces and line
breaks, and joining with single spaces puts it back together on one line.

Most real chunkers combine both ideas: follow headings and paragraphs first, and fall back to word windows only when a
part is too long.
:::

:::step{type=task task=section_chunks title="Your turn: one chunk per section" file="04-chunking/fieldbook.py" line="119-125"}
Write `section_chunks(markdown)` in `04-chunking/fieldbook.py`. For every piece of `markdown.split("\n## ")[1:]`:

1. split the heading line from the body with `partition("\n")`;
2. split the heading into the id and the title with `partition(" ")`;
3. clean the body with `" ".join(body.split())`;
4. add `{"id": ..., "title": ..., "text": ...}` to the list.

Return the list. With the manual, you get 31 chunks, the first with id `FM-1.1`. A usual slip: forgetting `[1:]`, which
adds the document's introduction as a fake first section.

Then compare six ways of cutting:

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
`compare_chunks.py` tests six ways of cutting the manual. It uses the 22 test questions in `data/questions.json` whose
answers are in the manual; each question lists the section that answers it. For each way of cutting, the script embeds
the chunks, runs every question through `top_k`, and counts three things:

| Column | Means |
|---|---|
| hit@1 | how often the **best** chunk contains the right section |
| hit@3 | how often one of the **three** best chunks does |
| words read | how many words the three best chunks hold on average: what the model would have to read |

A word window can cross a section border, so a window gets credit for **every** section it touches. That is fair to
the big windows: they are not punished just for crossing borders.

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

The picture shows what the main methods do to three real sections, FM-4.1 to FM-4.3, drawn to scale, with each
method's hit@1 from the table:

:::diagram{name="rag-chunks"}
The same three sections cut four ways (the window rules applied to these three, to scale). Only one chunk per section
keeps every chunk about one thing.
:::

What the numbers say, for this manual and these 22 questions:

1. **Tiny windows (15 words)** are cheap to read (45 words per question) but lose context: only 73% are right at the
   first try. A 15-word piece often does not say what it is about.
2. **Huge windows (300 words)** each cover several sections, so you might expect them to contain every answer. Yet hit@1
   is only 77%, and the model would read **864 words** per question, 19 times more than with tiny windows. Their vectors
   are averages of several topics, so they match many questions a little and none of them well.
3. **Following the sections wins.** Small windows that stay inside one section, and whole sections with their title,
   both reach **91%** at the first try. Adding the title to a whole section raised it from 86% to 91%: a title like
   "Meeting a tiger" uses exactly the kind of words a question uses.

With only 22 questions, one question is about 4.5 percentage points, so treat small differences (86% against 91%) as a
hint, not a proof. The big ones (tiny and huge windows against sections) are clear.

From now on, Fieldbook uses one chunk per section with its title first (the `chunk_text` function in `fieldbook.py`),
plus one chunk per patrol report. For long documents without sections, windows of 40 to 60 words with some overlap are
a sound place to start, and measuring on your own questions, as you just did, is how you decide.
:::

:::step{type=predict title="Guess first"}
:::question
A 300-word window contains the answer to a question. Why might search still not rank it first?
:::
- [x] Its vector averages several topics, so it is only partly similar to any one question
- [ ] Long chunks are cut off before embedding
- [ ] Search always prefers short chunks
:::explain
One vector per chunk means one summary of the chunk's meaning. A chunk about one thing has a sharp vector; a chunk about
five things has a blurry one. (300 words also stay under bge-small's limit of 512 tokens, so nothing was cut off.)
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
Overlap costs a few extra chunks and repeated words, and saves the sentences that would otherwise be cut in half.
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
Information stored with a chunk, like its id and title, is called **metadata**. Later chapters add more: the zone, the
date and the kind of document (chapter 8 filters searches on them).
:::
:::

:::step{type=deep-dive title="Go deeper: chunking real documents"}
**Tokens, not words.** Models count tokens, not words (in English a token is about three quarters of a word).
Production chunkers measure chunks in tokens and keep them safely under the embedding model's limit: 512 tokens for
bge-small; other models allow more.

**Structure first.** Split on headings, then paragraphs, then sentences, and fall back to windows only for long blocks.
Tables, code and lists need their own rules: half a table is useless.

**Context for small chunks.** A chunk that says "Change them every 21 days" means little alone. Put the document and
section title in front of each chunk (as `chunk_text` does), or search small chunks and give the model the whole section
they came from ("small to big" retrieval).

**Re-chunking costs.** Changing how you chunk means embedding everything again. Keep the original documents, not only the
chunks.
:::

:::step{type=recap}
You can now:

- cut text into windows of words with overlap, and stop at the right place;
- cut a document along its own headings, keeping an id and a title with every chunk;
- measure a way of cutting by how often search finds the right section and how much the model must read;
- explain why chunks about one thing beat both tiny and huge ones.

That ends Part 1. Next, chapter 5: the first of the indexes inside every vector database.

:::photo{src="/lesson-images/rag/rag-04-notes.webp" alt="Handwritten notes about chunking: Documents are cut into chunks; each chunk gets a vector. Too small: a chunk loses its context. Too big: its vector blurs several topics. Overlap keeps border sentences whole. Cut along headings and put the title first. Measure on your own questions." ai="true"}
One page of notes for this chapter.
:::
:::
