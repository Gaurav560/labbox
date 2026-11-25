:::step{type=story title="Twelve cards today, thousands tomorrow"}
In chapter 11 Atlas compared a question with six descriptions, embedding all six every time. That is fine for six. The
museum has twelve exhibit cards today; the archive team has three thousand catalogue entries waiting; a big museum has
a million. Embedding everything again for every question would be slow and wasteful, and comparing a question with a
million vectors one by one would be slower still.

The answer is a **vector store**: a database for embeddings. You embed each document **once**, when you add it, and
the store keeps the text, its vector and its metadata together. A search embeds only the question, and the store finds
the nearest documents for you.

The great card catalogues of old libraries solved the same problem for books: every book got its card once, filed by
subject, and finding one never meant walking past every shelf.

:::photo{src="/lesson-images/spring-ai/catalogue-drawers.webp" alt="Rows of wooden catalogue drawers with metal label holders; one drawer is pulled out, full of index cards" credit="Dr. Marcus Gossler" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Schlagwortkatalog.jpg"}
The subject catalogue of the University Library of Graz: every book filed once, found many times.
:::

:::mission
Put every exhibit card into a vector store at start-up, and search it by meaning, with a limit on how many and how weak
the matches may be.
:::
:::

:::step{type=concept title="Documents, vectors and metadata"}
Spring AI's unit of knowledge is a **`Document`**: a piece of text, plus **metadata** (a map of facts about it), plus,
once stored, its embedding.

```java
new Document("The planetarium is a 15 metre dome ...", Map.of("file", "planetarium.md"))
```

Metadata is how you remember where a text came from (a file, a page, a gallery), and later how you filter ("only
cards from the Space Gallery") and cite sources (chapter 14).

A **`VectorStore`** has two jobs:

| Method | Does |
|---|---|
| `store.add(documents)` | embeds each document with the `EmbeddingModel` and keeps it |
| `store.similaritySearch(request)` | embeds the query and returns the most similar documents, best first |

Spring AI has one `VectorStore` interface and over twenty implementations: PGvector (PostgreSQL), Redis, Elasticsearch,
MongoDB Atlas, Pinecone, Weaviate, Qdrant, Chroma and more. Atlas uses **`SimpleVectorStore`**, which keeps everything in
memory: perfect for learning and small data, and the code is the same when you move to a real database.

:::diagram{name="ai-vector-store"}
This chapter's real start-up and one real search (26 November).
:::
:::

:::step{type=task task=add_documents title="Your turn: load the cards" file="12-vector-store/src/main/java/com/atlas/CardLoader.java" line="34"}
In `12-vector-store`, `CardLoader` runs at start-up (it is an `ApplicationRunner`) and already reads every card in
`src/main/resources/exhibits/` into a `Document` with a `file` in its metadata. Add the documents to the vector store:

1. Where the TODO is: `store.add(documents);`
2. Then print what happened, so you can see when the cards are ready:
   `System.out.println("Loaded " + documents.size() + " exhibit cards into the vector store.");`

The usual slip: adding them one at a time in a loop with `store.add(List.of(doc))`. It works, but it is longer code
for the same twelve requests: `SimpleVectorStore` already sends one embedding request per document (we counted them
in the backend's log: twelve, about 0.4 seconds apart).

```bash run
cd 12-vector-store && mvn -q -o spring-boot:run
```

Wait for the line `Loaded 12 exhibit cards into the vector store.` before you search: the cards load just after the
web server starts. Press **Check**.
:::

:::step{type=example title="Worked example: a search request" file="12-vector-store/src/main/java/com/atlas/SearchController.java" line="27"}
A search is described by a `SearchRequest`:

```java
List<Document> found = store.similaritySearch(SearchRequest.builder()
        .query("Where is the pendulum?")   // embedded for you
        .topK(3)                            // at most 3 results
        .similarityThreshold(0.5)           // none weaker than 0.5
        .build());
```

1. `query` is the text to look for; the store embeds it with the same model as the documents.
2. `topK` caps how many documents come back. Each one will cost tokens when you send it to the model, so keep it small.
3. `similarityThreshold` drops weak matches. Without it, a search **always** returns `topK` documents, even for a
   question the cards know nothing about.

Each returned `Document` carries its `getScore()`: the similarity, between 0 and 1 here.
:::

:::step{type=task task=search_cards title="Your turn: search by meaning" file="12-vector-store/src/main/java/com/atlas/SearchController.java" line="28"}
Finish `GET /search?q=...&k=...`: ask the store for the `k` most similar cards, leaving out any with a similarity below
**0.5**:

1. `SearchRequest.builder().query(q).topK(k).similarityThreshold(0.5).build()`
2. Pass it to `store.similaritySearch(...)` and return the result.

The usual slip: leaving out `similarityThreshold`. Every search then returns `k` cards, the pizza question too.

```bash run
curl -s -G localhost:8080/search --data-urlencode "q=Where is the pendulum?" | jq -c ".[] | {file, score}"
```

Press **Check**.
:::

:::step{type=try title="Real searches, and one honest miss"}
With the real embedding model (our re-run on 26 November gave exactly the same scores, to the last digit: embeddings
are deterministic):

```text
$ curl -s -G localhost:8080/search --data-urlencode "q=Where is the pendulum?" | jq -c ".[] | {file, score}"
{"file":"foucault-pendulum.md","score":0.6374886702930733}
$ curl -s -G localhost:8080/search --data-urlencode "q=Has India sent anything to Mars?" | jq -c ".[] | {file, score}"
{"file":"mangalyaan.md","score":0.5420380850657599}
$ curl -s -G localhost:8080/search --data-urlencode "q=How much is a ticket for a child?" | jq -c ".[] | {file, score}"
$ curl -s -G localhost:8080/search --data-urlencode "q=What is the recipe for pizza?" | jq -c .
[]
```

The pendulum and the Mars mission were found (the question never names Mangalyaan). Pizza found nothing, as it should:
the threshold kept the store from returning random cards. And the ticket question found **nothing**, although the
visitor-information card does give the price. Why? That card is about opening hours, tickets **and** directions; its
one vector is an average of all three topics, so it is not close enough to a question about one of them.

Measuring without the threshold showed how the real scores spread: the good matches scored 0.54 and 0.64; unrelated
cards 0.02 to 0.29. The ticket question's best card was visitor-information, at only 0.219. A whole card is often too big a unit. Chapter 13 fixes the ticket question by cutting
documents into smaller, focused pieces.
:::

:::step{type=predict title="Guess first"}
:::question
You search with `topK(3)` and no threshold, for "What is the recipe for pizza?". What comes back?
:::
- [ ] Nothing: no card mentions pizza
- [x] Three cards anyway, the least unrelated ones, with low scores
- [ ] An error
:::explain
Similarity search always ranks; without a threshold it returns the top three, however poor. Sent to the model as
"context", those could lead it astray. A threshold turns "least bad" into "nothing found".
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When are documents embedded in a vector store?
:::
- [x] Once, when they are added; searches embed only the question
- [ ] Every time someone searches
- [ ] Never: vector stores compare text directly
:::explain
That is the point of a vector store: pay for embedding once, search many times. (With `SimpleVectorStore` "once" means
once per start, because it lives in memory; a database keeps them.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the metadata `file` for?
:::
- [ ] It makes the search more accurate
- [x] It records where each text came from, for filtering and for citing sources
- [ ] The vector store needs it to work
:::explain
Metadata travels with the document but is not part of the similarity. You will use it in chapter 14 to show visitors
which card an answer came from.
:::
:::

:::step{type=deep-dive title="Go deeper: real vector databases"}
**PGvector.** For most Spring teams the first real vector store is PostgreSQL with the pgvector extension: your vectors
live next to your other data, with transactions and backups you already have. Spring AI's `spring-ai-starter-vector-store-pgvector`
creates the table and an **HNSW index**, which finds near neighbours among millions of vectors in milliseconds by
checking only a small part of them.

**Filters.** `SearchRequest.builder().filterExpression("gallery == 'Space Gallery'")` searches only matching metadata,
with the same portable expression syntax on every store.

**Persistence for `SimpleVectorStore`.** `store.save(file)` and `store.load(file)` write and read the store as JSON, handy
for small apps and tests.

**Rate limits.** `SimpleVectorStore` embeds documents one request each (twelve requests for twelve cards, in our log). For thousands of documents, a store with
batching (most database stores batch for you) or a slower, steady ingestion job keeps you under your provider's limits.
:::

:::step{type=recap}
You can now:

- explain what a vector store is for: embed once, search many times, by meaning;
- create `Document`s with metadata, and load them at start-up with `store.add(...)`;
- search with `SearchRequest`: a query, `topK` and a `similarityThreshold`;
- read real similarity scores, and explain why a big mixed document can be missed.

Next, chapter 13: the ETL pipeline, to read, split and load documents properly.

:::photo{src="/lesson-images/spring-ai/springai-12-notes.webp" alt="Sketchnote, The vector store (embed once, search many times): A vector store keeps each document's text, its embedding and its metadata. A search embeds only the question. The flow: 12 cards, store.add(), Vector store, similaritySearch(), Nearest cards. What we measured: the pendulum card scored 0.637; pizza found nothing: the 0.5 threshold worked; the ticket card scored only 0.219: too mixed; 12 cards took 12 embedding requests." ai="true"}
One page of notes for this chapter.
:::
:::
