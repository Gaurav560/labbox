:::step{type=story title="The rule book, in every answer"}
Sahyadri Rail's rules live in documents: refunds, luggage, pets, monsoon procedures, accessibility. They are long,
they change every season, and the important details hide in them ("musical instruments up to 1.5 metres travel free").
Chapter 11 pasted a timetable into the prompt; that works for one page, not for a rule book, and it would pay for
every page on every question.

**Retrieval-augmented generation** (RAG) does it properly: split the documents into pieces, store them in an embedding
store (chapter 22), and for each question **retrieve** the few pieces that matter and send only those with the
question. The model **generates** the answer from them. It is the most widely used pattern in AI applications today,
and LangChain4j does almost all of it for you.

:::mission
Load Sahyadri Rail's rule documents into an embedding store, then give Setu a content retriever so every answer is
grounded in the rules.
:::
:::

:::step{type=concept title="Two halves: indexing and retrieval"}
RAG has two halves, run at different times:

| Half | When | Steps | LangChain4j |
|---|---|---|---|
| **Indexing** | Once, and again when documents change | Load, split, embed, store | `FileSystemDocumentLoader`, `DocumentSplitters`, `EmbeddingStoreIngestor` |
| **Retrieval** | On every question | Embed the question, find the closest pieces, add them to the prompt | `EmbeddingStoreContentRetriever`, `.contentRetriever(...)` on an AI Service |

:::diagram{name="l4j-rag"}
This chapter's real run (26 November): the numbers come from the gateway's log and the store.
:::

**Why split?** A whole document is one vector that blurs all its topics together, and sending a whole document
wastes tokens. Small pieces (here at most 300 characters, overlapping by 30 so no sentence is cut without context)
each mean one thing, so the right one can be found and sent alone. `DocumentSplitters.recursive(300, 30)` splits by
paragraphs first, then lines, then sentences, then words, only as far as needed (we checked the chain in the 1.24
jar).

Here the five rule files (1,772 characters) became **12 pieces**. Some are only a heading, such as "Luggage" or
"Monsoon travel", and one starts mid-sentence ("Delays are / announced on platforms..."), because the splitter cuts at
300 characters. That is normal, and it matters later in this chapter.

**Check yourself:** which half runs when a passenger asks a question? (Retrieval. Indexing already happened when Setu
started.)
:::

:::step{type=history title="Retrieval-augmented generation, 2020"}
:::before{title="Knowledge frozen in the weights"}
A model knows only what it was trained on, frozen at a date. To teach it new or private facts you had to train it
again, which was slow and expensive, and it still hallucinated when unsure (chapter 11).
:::

In **2020** Patrick Lewis and colleagues at Facebook AI Research published **"Retrieval-Augmented Generation for
Knowledge-Intensive NLP Tasks"**. Their model looked up passages from Wikipedia with a retriever, then generated the
answer from them, and beat larger models that had to remember everything. The paper gave the pattern its name. After
ChatGPT arrived (November 2022), RAG with an embedding store became the standard way to make them answer from a
company's own documents.

:::solved
**Fresh, private, checkable knowledge.** Update a document and the next answer uses it; keep private documents in your
own store; and every answer can name the pieces it came from.
:::

:::timeline
- **2020** The RAG paper, from Facebook AI Research.
- **2022** Vector databases spread with embedding APIs.
- **2023** RAG becomes the standard pattern for company chatbots.
- **2024** Advanced RAG: query rewriting, re-ranking, hybrid search.
:::

Retrieval is older than computers. A library's **card catalogue** finds the right book from a few words, and only then do you read it. RAG works the same way: find the right pieces first, then let the model read them.

:::photo{src="/lesson-images/langchain4j/card-catalog.webp" alt="Close-up of wooden card catalogue drawers, each with a brass label holder and pull handle" credit="MarkBuckawicki" license="CC0" source="https://commons.wikimedia.org/wiki/File%3AWooden_Card_Catalog_Furniture.jpg"}
A wooden card catalogue at a public library in Nashua, New Hampshire.
:::
:::

:::step{type=example title="Worked example: the ingestor" file="23-rag/src/main/java/com/setu/Rag.java" line="26-32"}
LangChain4j's `EmbeddingStoreIngestor` runs the whole indexing half: split, embed, store. For a folder of support
articles it reads like this (only to read; it is not in your project):

```java
List<Document> articles = FileSystemDocumentLoader.loadDocuments(Path.of("articles"), new TextDocumentParser());
EmbeddingStoreIngestor.builder()
        .documentSplitter(DocumentSplitters.recursive(500, 50))
        .embeddingModel(embeddingModel)
        .embeddingStore(store)
        .build()
        .ingest(articles);
```

Each `Document` remembers where it came from: the loader adds `file_name` and `absolute_directory_path` metadata,
and every piece keeps it, so an answer can say which file it used. `TextDocumentParser` reads plain text; other
parsers read PDF, Word and more (Apache Tika handles dozens of formats).
:::

:::step{type=task task=ingest_rules title="Your turn: index the rules" file="23-rag/src/main/java/com/setu/Rag.java" line="26-32"}
Finish `Rag.ingest(model, folder)`:

1. load the documents with `FileSystemDocumentLoader.loadDocuments(folder, new TextDocumentParser())`;
2. make an `InMemoryEmbeddingStore<TextSegment>`;
3. build an `EmbeddingStoreIngestor` with `.documentSplitter(DocumentSplitters.recursive(300, 30))`, the model and the
   store, and call `.ingest(docs)`;
4. return the store.

The usual slip: leaving out `.documentSplitter(...)`. Nothing fails: each whole file becomes one piece. We tried it on
26 November. The whole `luggage.txt` scored under 0.7 for "Can I bring my guitar?", so nothing was retrieved and
Setu answered "please ensure it fits within the luggage guidelines", without the 1.5-metre rule. One vector for a
whole file blurred the one sentence that mattered.

Press **Check**.
:::

:::step{type=concept title="Retrieval in an AI Service" file="23-rag/src/main/java/com/setu/Rag.java" line="40-48"}
The retrieval half is a **content retriever**, already written in `Rag.retriever(...)`:

```java
EmbeddingStoreContentRetriever.builder()
        .embeddingStore(store)
        .embeddingModel(embeddingModel)
        .maxResults(3)
        .minScore(0.7)        // chapter 22's threshold
        .build();
```

Give it to an AI Service with `.contentRetriever(...)`, and every call does chapter 22's search with the question and
adds what it finds to the user message. (Retrieval has a cost of its own: the question is embedded first, 6 tokens
here.) Here is the real request Setu sent for "Can I bring my guitar?", from the
gateway's log:

```text
--- system
You are Setu, the help desk assistant of Sahyadri Rail, ... Answer only from the information you are given; if it is
not there, say you don't know and suggest the station office.
--- user
Can I bring my guitar?

Answer using the following information:
Musical instruments up to 1.5 metres travel free with their owner.
```

Of five documents, one sentence travelled with the question: the piece of `luggage.txt` that matters, found by
meaning (the question says "guitar", the rule says "musical instruments"). The whole request was **107 tokens** (107 again when we ran it on 26 November).
Notice the system message too: it tells Setu to answer **only** from that information. Retrieval brings the facts;
the instruction stops the model filling gaps with guesses.
:::

:::step{type=task task=rag_answer title="Your turn: answer from the rules" file="23-rag/src/main/java/com/setu/Rag.java" line="34-38"}
Finish `Rag.assistant(chatModel, store, embeddingModel)`: build the `Assistant` with `AiServices.builder(Assistant.class)`,
`.chatModel(chatModel)` and `.contentRetriever(retriever(store, embeddingModel))`, then `.build()`.

The usual slip: forgetting `.contentRetriever(...)`. It compiles and runs, but Setu has no rules to read. We tried it
on 26 November: the landslide question got "I don't have information on refund policies", and the guitar question
the same vague answer as with no splitter.

```bash run
cd /workspace/23-rag && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Answers from the rule book"}
```text
$ mvn -q compile exec:java
> My train was cancelled because of a landslide. Do I get my money back?
Yes, you will receive a full refund since your train was cancelled due to a landslide. Alternatively, you may travel on the next train with a free seat using the same ticket. For further assistance, please visit the station office.

> Can I bring my guitar?
Yes, you can bring your guitar if it is up to 1.5 metres in length, as it will travel free with you.

> Is there wifi on the Monsoon Mail?
I don't know if there is wifi on the Monsoon Mail. Please check with the station office for more information.
```

(The same three answers, word for word, on 26 November.)

Three questions, three behaviours you want. The landslide question got the rule from `refunds.txt` (full refund when
the railway cancels, or the next train on the same ticket). Four pieces scored over 0.7 for it, the best 0.818, but
`maxResults(3)` sent only three: 253 tokens in. The guitar question got the 1.5-metre rule, from a
sentence that never mentions guitars. And wifi is in no document. The gateway's log shows what was retrieved for it:
one piece, the bare heading "Monsoon travel", which scored **0.702**, just over 0.7, only because the question says
"Monsoon Mail".
It says nothing about wifi, so Setu followed its instruction and said it does not know, instead of inventing "free
wifi on board". Compare that with chapter 18's "comfortable seating": same model, now grounded.

Two lessons hide in that wifi request. Retrieval finds what is **similar**, not what is **relevant**: a word in common
can be enough. And the instruction "answer only from the information you are given" is what kept a weak match from
becoming a wrong answer. Both layers matter.
:::

:::step{type=predict title="Guess first"}
:::question
The refund rule changes from 24 to 48 hours. What must happen before Setu gives the new answer?
:::
- [ ] Nothing: the model will notice
- [x] Update refunds.txt and index it again (remove the old pieces, ingest the new file)
- [ ] Retrain the model
:::explain
Setu's knowledge is the store. Change the document, re-index it, and the very next answer uses the new rule. This is
why RAG beats retraining for facts that change.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why split documents into small pieces?
:::
- [ ] Embedding models cannot read long texts
- [x] Each small piece means one thing, so the right one can be found and sent alone, saving tokens
- [ ] To hide the documents from the model
:::explain
A vector for a whole document blurs its topics, and sending whole documents costs tokens on every question.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
For the wifi question, the retriever sent the heading "Monsoon travel". Why did Setu still say it does not know?
:::
- [x] The heading says nothing about wifi, and the system message says to answer only from the information given
- [ ] The retriever found nothing
- [ ] The model searched the internet and found nothing
:::explain
Retrieval brought a weak, similar-sounding piece; the instruction stopped the model from filling the gap. Neither
layer is enough alone.
:::
:::

:::step{type=deep-dive title="Go deeper: better RAG"}
**Easy RAG.** `langchain4j-easy-rag` does the whole indexing half with defaults in two lines:
`EmbeddingStoreIngestor.ingest(documents, store)`, with a local embedding model (chapter 5's BGE). Good for a first
prototype.

**Sources.** Return `Result<String>` from the AI Service method, and `result.sources()` gives the pieces used, with
their `file_name` metadata, so Setu can say "according to the refund rules...".

**Advanced RAG.** LangChain4j's `RetrievalAugmentor` adds query transformers (rewrite "and for children?" into a full
question using the chat memory), query routers (search the right store), re-ranking with a scoring model, and hybrid
keyword and vector search.

**Measure it.** Keep a list of real questions with the document that should answer each, and count how often it is
retrieved. Change the chunk size or the threshold only when that number improves (chapter 26).
:::

:::step{type=recap}
You can now:

- explain RAG's two halves, indexing and retrieval, and why documents are split;
- index a folder of documents with `FileSystemDocumentLoader`, `DocumentSplitters` and `EmbeddingStoreIngestor`;
- give an AI Service a `contentRetriever`, and read the augmented prompt it sends;
- combine a threshold and an instruction so a missing answer becomes "I don't know".

Next, chapter 24: models on your own machine with Ollama, and routing each question to the right model.

:::photo{src="/lesson-images/langchain4j/l4j-23-notes.webp" alt="Handwritten notes titled RAG, retrieve the right pieces, then generate: split documents into small pieces and store their vectors once, then send only the closest pieces with each question; 5 files, 12 pieces, the question, best piece 0.711, 107 tokens in; one sentence was enough for the guitar question; with no splitter the 1.5 metre rule was lost; for wifi only a heading matched and Setu said it does not know; change a file, index it again" ai="true"}
One page of notes for this chapter.
:::
:::
