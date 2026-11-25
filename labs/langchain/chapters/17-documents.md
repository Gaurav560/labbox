:::step{type=story title="A rule book that does not fit"}
Chapter 9 gave Navin the co-op's facts by pasting a card into the system message. The co-op has more than a card: a
rule book with pages on cold storage, crop loans, spraying, membership and selling. It will grow every season. Pasting
all of it into every question would be slow, expensive (chapter 9's bill again), and soon too long for the context
window.

The way out, used by almost every AI application that answers from documents, is **retrieval**: keep the documents
outside the model, find only the pieces that matter for each question, and send just those. This Part builds it in
four steps: load the documents and cut them into pieces (this chapter), embed and store the pieces (18), search them
from an agent (19), and measure how well the search works (20).

:::mission
Load the rule book's five files as LangChain `Document`s, then cut them into pieces of at most 300 characters that
remember where they came from.
:::
:::

:::step{type=concept title="A Document: text plus metadata" file="17-documents/loader.py" line="8-12"}
LangChain represents any text from anywhere as a `Document`:

```python
Document(page_content="Cold storage\n\nThe co-op's cold store ...", metadata={"source": "storage.txt"})
```

`page_content` is the text; `metadata` is a dictionary of anything you want to keep with it: the file, a page number,
a date, who may see it. Metadata travels with the text through splitting, embedding and search, so an answer can say
**where** it came from ("[storage.txt]").

A **loader** is anything that turns files (PDFs, web pages, databases) into Documents. Many ready-made loaders live in `langchain-community` (the lab has 0.4.2) or in separate integration packages; for
plain text files, a few lines of Python are the clearest loader of all.
:::

:::step{type=task task=load_rules title="Your turn: load the rule book" file="17-documents/loader.py" line="8-12"}
Finish `load_rules(folder)`:

1. Go through `sorted(folder.glob("*.txt"))`: every `.txt` file, in name order.
2. For each `path`, make `Document(page_content=path.read_text(), metadata={"source": path.name})`.
3. Return the list.

The usual slip: `metadata={"source": str(path)}`, the whole path. Use `path.name`, the file name alone, so answers
cite "storage.txt", not a folder on your machine.

Press **Check**.
:::

:::step{type=history title="Why pieces of about a hundred words"}
:::before{title="Whole documents"}
Early search engines matched whole documents. For a question whose answer is one sentence in a long page, the page
might be found, but the sentence was still buried in it.
:::

Research on **passage retrieval** in the 1990s found that searching smaller passages often works better than whole
documents. In **2020** Facebook's **Dense Passage Retrieval** (Vladimir Karpukhin and colleagues) split Wikipedia into
about 21 million passages of 100 words each, embedded every passage, and found a passage containing the answer far more often than a strong keyword search
(BM25): 9 to 19 percentage points more often among the top 20 results, depending on the dataset.
Retrieval-augmented generation (chapter 19) was built on top of it. Splitting documents into **chunks** has been the
first step of retrieval ever since.

:::solved
**Small pieces, each about one thing.** A chunk's embedding stands for one idea, so the right one can be found and sent
alone, saving tokens.
:::

:::timeline
- **1990s** Passage retrieval in search research.
- **2020** Dense Passage Retrieval: 21 million 100-word passages.
- **2020** RAG builds on it.
:::
:::

:::step{type=concept title="Splitting text: the recursive splitter" file="17-documents/loader.py" line="15-19"}
`RecursiveCharacterTextSplitter` cuts text into chunks of at most `chunk_size` characters. It tries separators in
order, keeping text together as long as it can:

| It first tries | Then | Then | Last |
|---|---|---|---|
| `"\n\n"` (paragraphs) | `"\n"` (lines) | `" "` (words) | single characters |

`chunk_overlap=30` repeats a little text between neighbouring chunks, so a sentence cut at the border still has some
context. `add_start_index=True` records where each chunk starts in its file, in the metadata.

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30, add_start_index=True)
chunks = splitter.split_documents(docs)     # each keeps its document's metadata, plus start_index
```
:::

:::step{type=task task=split_rules title="Your turn: split the rules" file="17-documents/loader.py" line="15-19"}
Finish `split(docs, size, overlap)`:

1. `splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap, add_start_index=True)`.
2. Return `splitter.split_documents(docs)`.

The usual slip: `splitter.split_text(...)`, which returns plain strings and loses the `source` metadata.

```bash run
cd /workspace/17-documents && python main.py
```

Press **Check**.
:::

:::step{type=try title="Five documents, twelve pieces, and a rule cut in half"}
A real run (the splitter has no randomness: we got exactly this again on 25 November):

```text
$ python main.py
5 documents: loans.txt (488 chars), market.txt (436 chars), membership.txt (407 chars), spraying.txt (490 chars), storage.txt (565 chars)
12 chunks

[storage.txt @0] 'Cold storage'

[storage.txt @14] "The co-op's cold store at Pimpalgaon keeps onions, tomatoes and grapes. The charge is Rs 2 per crate per day, paid\nwhen the crates are taken out. Bookings of up to 50 crates are confirmed at the counter. Bookings of more than 50"

[storage.txt @243] "crates need the manager's approval, which usually takes one working day."

[storage.txt @317] "Crates must be clean and labelled with the member's number. Onions are stored at 2 degrees, tomatoes at 10 degrees and\ngrapes at 0 degrees, each in its own chamber. Crates left more than 120 days are moved to the overflow store and\ncharged double."
```

Look closely at `storage.txt`, because the splitter did two things a person never would:

1. The heading **"Cold storage"** became a chunk on its own: two words with no rule in them.
2. The most important rule was **cut in half**: "Bookings of more than 50" ends one chunk, and "crates need the
   manager's approval, which usually takes one working day" starts the next. The rule files wrap their lines every
   hundred-odd characters (as many real documents do), and the splitter prefers to cut at a line break.

Neither chunk alone says what happens to a booking of 80 crates. Keep these two problems in mind: chapter 19 shows
what they do to a real answer, and chapter 20 measures and fixes them.
:::

:::step{type=predict title="Guess first"}
:::question
You raise `chunk_size` to 2,000 characters. What happens to the rule book?
:::
- [x] Each file becomes one chunk (we tried it: 5 chunks): no rule is cut, but every search returns a whole file
- [ ] The chunks overlap more
- [ ] Embedding fails
:::explain
Bigger chunks keep rules whole but blur many topics into one vector, and send more tokens with every question.
Chunk size is a trade-off you measure (chapter 20).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why keep `source` in each chunk's metadata?
:::
- [ ] The splitter needs it
- [x] So an answer can say which file it came from, and so searches can be filtered by file
- [ ] To make chunks smaller
:::explain
Metadata is how a piece of text stays traceable after splitting and searching.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `chunk_overlap` do?
:::
- [ ] Removes repeated text
- [x] Repeats a little text across the border of neighbouring chunks
- [ ] Merges small chunks
:::explain
Overlap gives a chunk some of its neighbour's text. Here it did not save the cut rule, because the cut fell between two
lines.
:::
:::

:::step{type=deep-dive title="Go deeper: loading real documents"}
**PDFs and more.** Loaders for PDFs, Word files, web pages and databases now come in separate integration packages
(see the "Document loader integrations" pages of the LangChain docs). A PDF loader usually gives one Document per page,
with the page number in the metadata.

**Clean before you split.** Unwrapping hard line breaks, removing headers and footers, and keeping headings with their
paragraphs often matter more than the splitter's settings.

**Splitting by structure.** Markdown and HTML splitters cut at headings, and code splitters at functions, so each chunk
is a meaningful unit.
:::

:::step{type=recap}
You can now:

- represent text as `Document`s with metadata;
- write a simple loader in Python;
- split documents with `RecursiveCharacterTextSplitter`, with overlap and start positions;
- read chunks critically, after seeing a heading alone and a rule cut in half.

Next, chapter 18: embedding the chunks and searching them by meaning.

:::photo{src="/lesson-images/langchain/lc-17-notes.webp" alt="Handwritten notes about documents and chunks: A Document is text plus metadata, like its source file. Retrieval sends only the pieces a question needs. The recursive splitter cuts at paragraphs, then lines, then words. Overlap repeats a little text across each border. In our rule book, a heading became a chunk of its own. A key rule was cut in half at a line break." ai="true"}
One page of notes for this chapter.
:::
:::
