:::step{type=story title="Garbage in, garbage out"}
Chapter 12 ended with a miss: "How much is a ticket for a child?" found nothing, though the answer was in the
visitor-information card. The search was not broken. The **documents** were badly cut: one card about three topics
became one vector that matched none of them well.

Retrieval is only as good as what you put into the store. Engineers who build search over documents spend most of
their time not on the model but on the **pipeline that prepares the documents**: reading them from files, cutting
them into good pieces, labelling each piece, and loading them. That pipeline has an old name from the world of data
warehouses: **ETL**, extract, transform, load. Spring AI has one built in.

A printing press works the same way, in stages: the text is set in pieces of type, arranged into pages, then printed;
a mistake at any stage shows on every copy.

:::photo{src="/lesson-images/spring-ai/printing-press.webp" alt="Two old wooden hand printing presses side by side in a museum room, with a wooden statue on the wall between them" credit="Riopelle" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Museum_Plantin-Moretus_Printing_Press.jpg"}
The two oldest surviving printing presses, from the 1500s, in the Plantin-Moretus Museum, Antwerp.
:::

:::mission
Build Atlas's ETL pipeline: read the cards as Markdown, split them into chunks of about 100 tokens, and load the chunks
into the vector store.
:::
:::

:::step{type=concept title="Extract, transform, load"}
Spring AI's ETL pipeline has three kinds of parts, each a plain Java interface:

| Stage | Interface | Atlas uses |
|---|---|---|
| **Extract** | `DocumentReader`: a source becomes `Document`s | `MarkdownDocumentReader` for the `.md` cards |
| **Transform** | `DocumentTransformer`: documents become better documents | `TokenTextSplitter`, to cut them into chunks |
| **Load** | `DocumentWriter`: documents go somewhere | the `VectorStore` itself |

They fit together like functions: the official documentation writes a whole pipeline in one line,

```java
vectorStore.accept(tokenTextSplitter.apply(reader.get()));
```

Readers exist for many sources: plain text, JSON, Markdown, PDF (by page or by paragraph), HTML (with jsoup), and
almost any office format (with Apache Tika). Transformers include splitters, a keyword enricher and a summary enricher
that ask a model to label each chunk.

:::diagram{name="ai-etl"}
This chapter's real pipeline (26 November): the counts it printed, and the ticket question afterwards.
:::
:::

:::step{type=example title="Worked example: the Markdown reader" file="13-etl/src/main/java/com/atlas/ExhibitEtl.java" line="42"}
The Markdown reader understands the structure of a Markdown file: it starts a new document at each heading. Extra
metadata is added through its configuration:

```java
MarkdownDocumentReaderConfig config = MarkdownDocumentReaderConfig.builder()
        .withAdditionalMetadata("file", "planetarium.md")
        .build();
List<Document> docs = new MarkdownDocumentReader(resource, config).get();
```

1. `withAdditionalMetadata` adds a fixed key and value to every document this reader produces.
2. `get()` reads the resource and returns the documents.

Structure is information. When this course started, the visitor-information card was three paragraphs under one
heading, and it became one document. It now has three headings (Opening hours, Tickets and prices, Getting here), so the
reader makes three documents, each about one thing. That is the first half of the fix for the ticket question.
:::

:::step{type=task task=read_cards title="Your turn: read the cards" file="13-etl/src/main/java/com/atlas/ExhibitEtl.java" line="43"}
In `13-etl`, finish `read(...)`: read every card with a `MarkdownDocumentReader`, giving each document the metadata
`file` = the card's file name (`card.getFilename()`), and return all the documents together:

1. For each card: a config with `.withAdditionalMetadata("file", card.getFilename())`.
2. `new MarkdownDocumentReader(card, config).get()`, and add those documents to one list.
3. Return the list.

The usual slip: one config made before the loop, with no file. The chunks then have no `file`, and chapter 14 cannot
say where an answer came from.

Press **Check**.
:::

:::step{type=concept title="Chunks: the right size of a piece"}
Even one section can be too long, or mix too much. **Chunking** cuts documents into pieces of a chosen size. How big?

| Chunks that are... | Give... |
|---|---|
| too big (whole cards, whole pages) | vectors that average many topics; costly to send to the model |
| too small (single sentences) | pieces without enough context to be understood alone |
| about 100 to 500 tokens, along natural boundaries | focused vectors that still make sense on their own |

`TokenTextSplitter` cuts by **tokens** (the same units the model counts), and tries to end chunks at the end of a
sentence. Its chunks keep the metadata of the document they came from, so every chunk still knows its file:

```java
List<Document> chunks = TokenTextSplitter.builder()
        .withChunkSize(100)
        .build()
        .apply(documents);
```

Atlas's cards are short, so a small size of 100 tokens shows the effect clearly. Real documents (manuals, policies,
catalogues) usually use 300 to 800, often with a small **overlap** between neighbouring chunks, so a sentence on a
boundary is not lost.
:::

:::step{type=predict title="Guess first"}
:::question
The splitter cuts a document from `planetarium.md` into three chunks. What metadata do the chunks have?
:::
- [ ] None: chunks are new documents
- [x] The same `file` as the document they came from
- [ ] Only the first chunk keeps it
:::explain
Splitters copy the metadata to every chunk. That is why you add metadata before splitting: it then follows every piece,
all the way to the answer's list of sources.
:::
:::

:::step{type=task task=split_and_load title="Your turn: split and load" file="13-etl/src/main/java/com/atlas/ExhibitEtl.java" line="49"}
Finish `splitAndLoad(...)`: split the documents into chunks of at most **100 tokens** with a `TokenTextSplitter`, add
the chunks to the vector store, and return them:

1. `List<Document> chunks = TokenTextSplitter.builder().withChunkSize(100).build().apply(documents);`
2. `store.add(chunks);`
3. `return chunks;`

The usual slip: adding `documents` instead of `chunks` to the store. The counts look right, but the store holds the
big documents, and the ticket question misses again.

```bash run
cd 13-etl && mvn -q -o spring-boot:run
```

Wait for the line starting `ETL:`, then:

```bash run
curl -s localhost:8080/etl; echo
curl -s -G localhost:8080/search --data-urlencode "q=How much is a ticket for a child?" | jq -c ".[] | {file, score, text: .text[0:80]}"
```

Press **Check**.
:::

:::step{type=try title="The ticket question, again"}
With headings in the card and chunks of 100 tokens, the real pipeline reported (our re-run on 26 November: the same
12, 14 and 23, and scores within 0.003 of these, 0.407 for the ticket chunk):

```text
$ curl -s localhost:8080/etl; echo
{"chunks":23,"files":12,"documents":14}
$ curl -s -G localhost:8080/search --data-urlencode "q=How much is a ticket for a child?" | jq -c ".[] | {file, score, text: .text[0:80]}"
{"file":"visitor-information.md","score":0.4045389258301116,"text":"A museum ticket costs 120 rupees for adults, and 60 rupees for children aged 5 t"}
{"file":"planetarium.md","score":0.24197345787805954,"text":"35 minutes. Planetarium tickets are sold separately from museum tickets, and wee"}
{"file":"planetarium.md","score":0.13213933935953984,"text":"Gallery: Space Gallery (Gallery 1)The planetarium is a 15 metre dome with 120 re"}
```

12 cards, 14 documents (the visitor card's three sections), 23 chunks. The ticket chunk is now **first**, with 0.40.
In chapter 12, the whole visitor card scored 0.219 for the same question, mixed in with the opening hours.

Look closely at the third result's text: "Gallery: Space Gallery (Gallery 1)The planetarium". The reader joined the
card's gallery line and its first paragraph without a space. The embedding barely minds, but if you show chunks to
people, check how your reader joins lines. And the pendulum question
still finds both of its chunks first:

```text
$ curl -s -G localhost:8080/search --data-urlencode "q=Where is the pendulum?" | jq -c ".[] | {file, score, text: .text[0:80]}"
{"file":"foucault-pendulum.md","score":0.5868879066707143,"text":"How fast the swing turns depends on where you are: at the North Pole it turns a "}
{"file":"foucault-pendulum.md","score":0.5650926488550371,"text":"Gallery: Motion Gallery (Gallery 2)A brass ball of 25 kilograms hangs from a 15 "}
{"file":"whispering-dishes.md","score":0.2728442842633302,"text":"Gallery: Motion Gallery (Gallery 2)Two large curved dishes face each other from "}
```

Notice that a question about **prices** scores lower (0.40) than one about a named exhibit (0.59): short questions about
facts are hard for embeddings. In chapter 14, Atlas will therefore retrieve with a threshold of 0.35, set from these
real numbers rather than guessed.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why did adding headings to the visitor card help the ticket question?
:::
- [ ] Headings are weighted more by the embedding model
- [x] The reader started a new document at each heading, so the ticket text got a vector of its own
- [ ] The model reads headings first
:::explain
Each piece now has one topic, so its vector points clearly in that topic's direction. Good structure in the source makes
good chunks.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You change the chunk size from 100 to 400 tokens. What must you do with the vector store?
:::
- [x] Build it again: the stored chunks (and their vectors) were made with the old size
- [ ] Nothing
- [ ] Only restart the model
:::explain
Changing any stage of the pipeline (reader, splitter, embedding model) means re-running it. In production, ETL jobs are
versioned and re-runnable for exactly this reason.
:::
:::

:::step{type=deep-dive title="Go deeper: ETL in production"}
**Run it as a job, not at start-up.** Real pipelines run on a schedule or when documents change, not every time the app
starts, and write to a database store. Each chunk gets a stable id (for example the file name and position), so
re-running updates chunks instead of duplicating them.

**Enrichers.** `KeywordMetadataEnricher` and `SummaryMetadataEnricher` ask a chat model to add keywords or a summary to
each chunk's metadata, which improves search and filtering, at the cost of a model call per chunk.

**PDFs and office files.** `PagePdfDocumentReader` reads a PDF page by page; `TikaDocumentReader` reads Word, PowerPoint,
HTML and many more. Scanned documents need text recognition (OCR) first.

**Measure.** Keep a list of real questions with the chunk that should answer each, and check after every change that
the right chunk comes first. Chapter 16 turns this into automated tests.
:::

:::step{type=recap}
You can now:

- describe Spring AI's ETL pipeline: readers, transformers and writers;
- read Markdown with `MarkdownDocumentReader`, adding metadata to every document;
- split documents into token-sized chunks with `TokenTextSplitter`, keeping their metadata;
- load chunks into a vector store, and improve retrieval by improving the documents' structure.

Next, chapter 14: retrieval-augmented generation, so Atlas answers from these chunks, and says which cards it used.

:::photo{src="/lesson-images/spring-ai/springai-13-notes.webp" alt="Sketchnote, The ETL pipeline (extract, transform, load): Good answers need good pieces. Read the cards, cut them into small chunks about one thing, and load the chunks. The flow: 12 cards, Reader: 14 documents, Splitter: 23 chunks, Vector store. What we measured: the ticket question: 0.219 before, 0.407 after; headings made the reader split the card; every chunk keeps its file name; change a stage: build the store again." ai="true"}
One page of notes for this chapter.
:::
:::
