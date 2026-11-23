:::step{type=story title="A memory for facts"}
Chapter 5 searched five FAQ questions by meaning, embedding all five again for every question. Sahyadri Rail has more:
help cards, rule books, timetables, monsoon procedures, hundreds of pages that change every season. Embedding them all
on every question would be slow and expensive, and the model's context window could never hold them all anyway.

The answer is to embed each piece of text **once**, keep the vectors in a database built for searching by meaning,
and for each question find only the few pieces that matter. That database is an **embedding store** (also called a
vector store or vector database), and it is the foundation of retrieval-augmented generation in chapter 23.

:::mission
Store Setu's help cards in an embedding store with their metadata, and search it with a threshold that keeps
irrelevant cards out.
:::
:::

:::step{type=concept title="What an embedding store keeps"}
Each entry in an embedding store has three parts:

| Part | Setu's example | Used for |
|---|---|---|
| The **embedding** | 1,536 numbers from OpenAI's text-embedding-3-small | Searching by meaning |
| The **text** (a `TextSegment`) | "Each passenger may carry 40 kg of luggage free..." | Giving to the model, or showing |
| The **metadata** | `title=Luggage`, `type=rule` | Filtering, citing sources |

LangChain4j's `EmbeddingStore` interface has two main operations, `add(embedding, segment)` and `search(request)`, and
30+ implementations: `InMemoryEmbeddingStore` for learning and tests, and real databases (PostgreSQL with pgvector,
Elasticsearch, Redis, Qdrant, Milvus, Pinecone...) for production. Your code depends on the interface, as it does on
`ChatModel`.

This chapter uses OpenAI's embedding model through the gateway (alias `ai-embed`) instead of chapter 5's local one:

```java
OpenAiEmbeddingModel.builder().baseUrl(baseUrl).apiKey(apiKey).modelName("ai-embed").build()
```

It handles many languages, has 1,536 dimensions, and costs $0.02 per million tokens: embedding all of Setu's cards
costs a small fraction of a cent.
:::

:::step{type=history title="Searching a billion vectors"}
:::before{title="Comparing with everything"}
Chapter 5's search compared the question with every stored vector. With five vectors that is instant; with a hundred
million, every question would take seconds, and recommendation systems at companies like Facebook had billions.
:::

In **2016** Yury Malkov and Dmitry Yashunin published **HNSW** (Hierarchical Navigable Small World graphs): vectors
linked in layered graphs, so a search hops quickly towards the right neighbourhood instead of visiting everything. In
**2017** Facebook released **FAISS**, a library for searching billions of vectors. Then came databases built around
it (Milvus in 2019, Pinecone, Qdrant and Weaviate soon after), and in **2021** **pgvector** added vector search to
PostgreSQL, so many teams could keep vectors next to their ordinary tables.

:::solved
**Nearest neighbours, fast.** Vector indexes find the closest vectors approximately, in milliseconds, among millions.
"Approximately" is the price: a fast index can occasionally miss a match an exhaustive search would find.
:::

:::timeline
- **2016** HNSW graphs for fast approximate search.
- **2017** FAISS from Facebook AI Research.
- **2019** Milvus, an open-source vector database.
- **2021** pgvector: vectors inside PostgreSQL.
:::
:::

:::step{type=example title="Worked example: one entry" file="22-embedding-stores/src/main/java/com/setu/Store.java" line="31-37"}
Storing one card takes three lines (only to read; your task loops over all of them):

```java
TextSegment segment = TextSegment.from("Bicycles travel in the guard's van for Rs 60.",
        Metadata.from("title", "Luggage").put("type", "rule"));
Embedding embedding = model.embed(segment).content();   // one call to the embedding model
store.add(embedding, segment);                           // vector + text + metadata
```

`model.embed(...)` returns a `Response<Embedding>` (like a chat model, an embedding model reports token usage), so
`.content()` gets the vector. For many texts, `model.embedAll(segments)` embeds them in one request, which is faster
and kinder to rate limits.
:::

:::step{type=task task=store_cards title="Your turn: store the cards" file="22-embedding-stores/src/main/java/com/setu/Store.java" line="31-37"}
Finish `Store.load(model, cards)`: create an `InMemoryEmbeddingStore<TextSegment>`; for each card, make a
`TextSegment` with the card's text and its `title` and `type` as metadata, embed it, and add both to the store.
Return the store.

Press **Check**.
:::

:::step{type=concept title="Searching, and what a score means" file="22-embedding-stores/src/main/java/com/setu/Store.java" line="39-44"}
A search is a request with the question's embedding and two limits:

```java
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(model.embed(question).content())
        .maxResults(3)       // at most this many
        .minScore(0.7)       // and only if this relevant
        .build();
List<EmbeddingMatch<TextSegment>> matches = store.search(request).matches();   // best first
```

Each `EmbeddingMatch` has the `score`, the `embedded()` segment (text and metadata) and its id.

Read the scores carefully. LangChain4j's **score** is not the cosine similarity of chapter 5: it is rescaled to run
from 0 to 1, as **(cosine + 1) / 2**. So a score of **0.5 means a cosine of 0**: unrelated, not "half relevant". Here
are the real top three scores for two questions, with no threshold:

```text
Can I take my bicycle?  0.712 Luggage  0.645 Lost property  0.612 Pets
What is the capital of France?  0.543 Accessibility  0.538 Lost property  0.526 Luggage
```

The right card scores 0.71; unrelated cards still score 0.6 or more; and a question about France, which no card
answers, scores 0.54. When we first wrote this chapter with `minScore(0.5)`, the France question returned two cards.
For this model and these cards, **0.7** separates the right answers from the noise. That number is not universal: test
your threshold on your own real questions, and test it again whenever you change the embedding model.
:::

:::step{type=task task=search_store title="Your turn: search with a threshold" file="22-embedding-stores/src/main/java/com/setu/Store.java" line="39-44"}
Finish `Store.search(store, model, question, max)`: build an `EmbeddingSearchRequest` with the question's embedding,
`maxResults(max)` and `minScore(0.7)`, search, and return the `"title"` metadata of each match, best first.

```bash run
cd /workspace/22-embedding-stores && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="The right card, or none"}
```text
$ mvn -q compile exec:java
dimensions: 1536
Can I take my bicycle? -> [Luggage]
My train is stuck because of rain -> [Monsoon]
I left my bag on the train -> [Lost property]
What is the capital of France? -> []

Can I take my bicycle?  0.712 Luggage  0.645 Lost property  0.612 Pets
What is the capital of France?  0.543 Accessibility  0.538 Lost property  0.526 Luggage
```

Each question finds exactly its card: the bicycle question finds Luggage (bicycles travel in the guard's van), the
rain finds Monsoon, the forgotten bag finds Lost property, though none of them shares the card's key words. And the
France question finds **nothing**, which is exactly what Setu needs to know: no card answers this, so it should not
pretend.
:::

:::step{type=predict title="Guess first"}
:::question
You switch from text-embedding-3-small to a different embedding model. What must you do with the store?
:::
- [ ] Nothing: vectors are vectors
- [x] Re-embed every stored text with the new model, and re-test the threshold
- [ ] Only change minScore
:::explain
Vectors from different models live in different spaces (and may have different lengths). Mixing them makes every
score meaningless.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A match has score 0.5. What does that mean in LangChain4j?
:::
- [ ] It is half relevant
- [x] Cosine similarity 0: unrelated
- [ ] It is the best possible match
:::explain
Scores are (cosine + 1) / 2, so 0.5 is the middle of the scale: no similarity at all.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why keep metadata (title, type) with each segment?
:::
- [ ] The embedding model needs it
- [x] To filter searches and to show or cite where an answer came from
- [ ] To make vectors smaller
:::explain
Metadata turns a match into something useful: which card, which file, which rule, and only rules, not service notes,
when you filter.
:::
:::

:::step{type=deep-dive title="Go deeper: embedding stores in production"}
**Metadata filters.** `EmbeddingSearchRequest.builder().filter(metadataKey("type").isEqualTo("rule"))` searches only
the rules. Filters also enforce access: a passenger's search must never return another passenger's documents.

**PGvector.** `PgVectorEmbeddingStore` keeps vectors in PostgreSQL, next to your other data, with an HNSW index. A good
first production store for most Java teams.

**Ids and updates.** `add(...)` returns an id. Keep it, so a changed card can be removed and added again instead of
duplicated.

**Cost and speed.** Embedding is cheap; the expensive part is usually re-embedding everything when you change models
or chunking. Plan for it.
:::

:::step{type=recap}
You can now:

- explain what an embedding store keeps: vectors, text and metadata;
- store segments with an embedding model and `InMemoryEmbeddingStore`;
- search with `maxResults` and `minScore`, and read scores as (cosine + 1) / 2;
- choose a threshold from real scores, and know when to re-embed.

Next, chapter 23: retrieval-augmented generation. Setu answers from the railway's own documents, found by meaning.

:::photo{src="/lesson-images/langchain4j/l4j-22-notes.webp" alt="Handwritten notes about embedding stores: vector plus text plus metadata; embed once, search many times; score equals cosine plus one, divided by two; 0.5 means unrelated; threshold from real scores: 0.7" ai="true"}
One page of notes for this chapter.
:::
:::
