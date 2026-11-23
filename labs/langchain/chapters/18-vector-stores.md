:::step{type=story title="Embed once, search many times"}
Chapter 3 compared a question with five FAQ vectors, made in advance. The rule book has twelve chunks today and will have
hundreds next year. Each chunk must be embedded once (that is a model call, and costs a little), stored with its text
and metadata, and then searched in milliseconds for every question a member asks.

That is what a **vector store** does. LangChain has one interface for dozens of them, from `InMemoryVectorStore` (in
your Python process, perfect for learning) to PostgreSQL with pgvector, Elasticsearch, Redis or Pinecone in production.

:::mission
Embed the rule book's chunks into a vector store, then search it with a threshold that keeps unrelated chunks out.
:::
:::

:::step{type=concept title="Embeddings and a store" file="18-vector-stores/store.py" line="9-12"}
Two LangChain pieces work together:

| Piece | Here | Does |
|---|---|---|
| Embeddings | `OpenAIEmbeddings(model="ai-embed")` | text to vector, through the gateway (text-embedding-3-small, 1,536 numbers) |
| Vector store | `InMemoryVectorStore` | keeps vector, text and metadata; finds the closest vectors to a query |

```python
store = InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings(model="ai-embed"))
```

`from_documents` embeds all the chunks (in one batch request) and adds them. Searching embeds the question with the
same model and compares it with every stored vector; that is why the same embedding model must be used for both (chapter
3).
:::

:::step{type=task task=store_chunks title="Your turn: embed and store the chunks" file="18-vector-stores/store.py" line="9-12"}
Finish `build_store(chunks)`: return `InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings(model="ai-embed"))`.

Press **Check**.
:::

:::step{type=history title="Searching a billion vectors"}
:::before{title="Comparing with everything"}
Comparing a question with every stored vector is instant for twelve chunks and hopeless for a billion, the scale of
image and product search at large companies.
:::

In **2016** Yury Malkov and Dmitry Yashunin published **HNSW**, layered graphs of vectors that let a search hop towards
the right neighbourhood instead of visiting everything. In **2017** Facebook released **FAISS**, a library that searches
billions of vectors. Vector databases built around such indexes followed, and in **2021** **pgvector** brought vector
search into PostgreSQL, so most teams can keep vectors next to their ordinary tables.

:::solved
**Nearest neighbours in milliseconds.** At the price of being approximate: a fast index can occasionally miss a match an
exhaustive search would find.
:::

:::timeline
- **2016** HNSW graphs.
- **2017** FAISS.
- **2021** pgvector in PostgreSQL.
:::
:::

:::step{type=concept title="Scores, and a threshold" file="18-vector-stores/store.py" line="15-19"}
`similarity_search_with_score(question, k=3)` returns the three closest chunks with their scores. For
`InMemoryVectorStore` the score is the plain **cosine similarity** of chapter 3. (Other stores use other scales: some
rescale to 0 to 1, some return distances where smaller is better. Always check.)

The store always returns k results, however unrelated. Here are real scores for this rule book, with no threshold:

| Question | Best three |
|---|---|
| Can I store 80 crates of onions? | 0.609, 0.531, 0.346 (all storage.txt) |
| What is the capital of France? | 0.089, 0.064, 0.063 |

Real matches score about 0.4 to 0.7 here; the France question, which no rule answers, scores under 0.1. A
**minimum score** turns "the least bad match" into "no match". This chapter uses 0.3, chosen from those numbers, and
the next step shows what that choice costs.
:::

:::step{type=task task=search_threshold title="Your turn: search with a threshold" file="18-vector-stores/store.py" line="15-19"}
Finish `search(store, question, k, min_score)`: call `store.similarity_search_with_score(question, k=k)` and return only
the `(document, score)` pairs whose score is at least `min_score`.

```bash run
cd /workspace/18-vector-stores && python main.py
```

Press **Check**.
:::

:::step{type=try title="The threshold keeps France out, and one good answer too"}
```text
$ python main.py
Can I store 80 crates of onions?
   all three: 0.609 storage.txt, 0.531 storage.txt, 0.346 storage.txt
   kept     : 0.609 storage.txt, 0.531 storage.txt, 0.346 storage.txt
How much loan can I get for 4 acres?
   all three: 0.469 loans.txt, 0.382 loans.txt, 0.264 membership.txt
   kept     : 0.469 loans.txt, 0.382 loans.txt
Who can tell me what is wrong with my vines?
   all three: 0.298 spraying.txt, 0.289 storage.txt, 0.268 spraying.txt
   kept     : nothing
What is the capital of France?
   all three: 0.089 membership.txt, 0.064 loans.txt, 0.063 loans.txt
   kept     : nothing
```

The threshold did its job three times: it kept the storage chunks, dropped the unrelated membership chunk from the loan
question, and returned nothing for France.

And once it cost us. "Who can tell me what is wrong with my vines?" has a real answer in `spraying.txt` (show a sample to
Mrs. Kulkarni), and its chunk was the best match, at **0.298**, just under 0.3. The question never says "spray",
"agronomist" or "disease", so its score is low. Lower the threshold to 0.25 and this question works, but weaker,
unrelated chunks start getting in for others. There is no perfect number: a threshold trades misses against noise, and
chapter 20 shows how to measure the trade instead of guessing.
:::

:::step{type=predict title="Guess first"}
:::question
You switch the store to PostgreSQL with pgvector, which reports a distance where 0 means identical. What happens to
`min_score=0.3` if you change nothing else?
:::
- [ ] It works the same
- [x] It means something different: check what the new store's score is, and choose the threshold again
- [ ] It is converted automatically
:::explain
Scores are not comparable between stores, or between embedding models. A threshold is tied to both.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why must the question be embedded with the same model as the chunks?
:::
- [x] Vectors from different models live in different spaces; comparing them is meaningless
- [ ] To save money
- [ ] The store refuses other models
:::explain
Same model, same space. Changing the model means embedding everything again.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A threshold of 0.3 dropped the vines question's correct chunk (0.298). What does that show?
:::
- [ ] The embedding model is broken
- [x] A threshold trades missed answers against noise; there is no perfect number
- [ ] Cosine similarity is wrong
:::explain
Measure on real questions (chapter 20) and choose the trade you can live with.
:::
:::

:::step{type=deep-dive title="Go deeper: stores in production"}
**Persistent stores.** `InMemoryVectorStore` is rebuilt (and re-embedded) on every start. A real deployment embeds once
into a database such as PostgreSQL with pgvector and keeps the vectors.

**Metadata filters.** Most stores can search only within a filter (only `spraying.txt`, only rules a member may see),
which is also how one store serves many co-ops safely.

**Updating.** Keep the ids `add_documents` returns, so a changed rule can be deleted and re-added instead of
duplicated.
:::

:::step{type=recap}
You can now:

- embed chunks into a vector store with `OpenAIEmbeddings` and `InMemoryVectorStore`;
- search with scores, and know what this store's score means;
- keep unrelated chunks out with a threshold chosen from real scores;
- explain what a threshold costs, after watching it drop a good answer at 0.298.

Next, chapter 19: retrieval-augmented generation. Navin searches the rule book, then answers from what it found.

:::photo{src="/lesson-images/langchain/lc-18-notes.webp" alt="Handwritten notes about vector stores: Embed once, search many times; Score here = cosine; Matches 0.4 to 0.7, France 0.09; Threshold 0.3 dropped vines; No perfect number" ai="true"}
One page of notes for this chapter.
:::
:::
