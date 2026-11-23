:::step{type=story title="Only the reports, only the buffer zone"}
The range officer asks Fieldbook: *"Leopards near people: what happened in the buffer zone villages this spring?"* The
nearest chunk by meaning is FM-4.3, the manual's section on leopards near villages. Useful, but it is not what she asked.
She wants **patrol reports**, and only those from the **buffer zone**.

Your NumPy matrix knows nothing about kinds of documents or zones; it only holds numbers. Real searches nearly always come
with conditions like these: this customer's documents only, this year only, only what this user may see. Keeping vectors
**together with their data**, and searching with conditions, is the job of a **vector database**.

You have now built every part of one yourself: embeddings, exact search, IVF, HNSW, quantization. Time to use a real
one. Fieldbook uses **Qdrant**, an open-source vector database written in Rust, through its Python client. The client has
a **local mode** that runs the same API inside your Python process, with no server to install; in production you change
one line to talk to a Qdrant server.


An Indian leopard: far more often seen near villages than tigers, and the subject of the range officer's question.

:::photo{src="/lesson-images/rag/leopard.webp" alt="An Indian leopard lying on a large rock in front of bare trees" credit="Tisha Mukherjee" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AIndian_leopard_in_Jawai_Bandh_April_2025_by_Tisha_Mukherjee_02.jpg"}
An Indian leopard in Jawai, Rajasthan.
:::
:::mission
Load Fieldbook's 55 chunks into a Qdrant collection, each point carrying its chunk as a payload, then search with payload
filters: reports only, one zone only.
:::
:::

:::step{type=concept title="Collections, points, payloads" file="08-qdrant/fieldbook.py" line="260-269"}
Qdrant's vocabulary is small:

| Word | Means | In Fieldbook |
|---|---|---|
| **collection** | a named set of points with the same vector size and distance | `"fieldbook"`, 384 numbers, cosine |
| **point** | one item: an id, a vector, a payload | one chunk |
| **id** | a whole number or a UUID | the chunk's position, 0 to 54 |
| **payload** | any JSON data stored with the vector | the chunk itself: id, title, text, kind, zone, beat, date |

Creating a collection and adding points:

```python
client = QdrantClient(":memory:")                     # local mode: in this process, in memory
client.create_collection(
    "fieldbook",
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)
client.upsert("fieldbook", points=[
    models.PointStruct(id=0, vector=[...384 numbers...], payload={"id": "FM-1.1", "kind": "manual", ...}),
    ...
])
```

**Upsert** means insert, or update if the id already exists: run it twice and you still have 55 points. Vectors go in as
plain lists (`v.tolist()`), because the client sends JSON to a server.

Because the payload is the chunk, a search result already carries the text to show the model: no second lookup.
:::

:::step{type=task task=make_store title="Your turn: a collection of points" file="08-qdrant/fieldbook.py" line="263-269"}
Write `make_store(chunks, vectors)`:

1. `client = QdrantClient(":memory:")`.
2. Create the collection `COLLECTION` with `models.VectorParams(size=vectors.shape[1], distance=models.Distance.COSINE)`.
3. Upsert one `models.PointStruct(id=i, vector=v.tolist(), payload=c)` for every chunk `c` and its vector `v`
   (`enumerate(zip(chunks, vectors))`).
4. Return the client.

Press **Check**.
:::

:::step{type=concept title="Search with conditions" file="08-qdrant/fieldbook.py" line="272-279"}
A Qdrant query takes the vector, how many results you want, and optionally a **filter** on the payloads:

```python
models.Filter(must=[
    models.FieldCondition(key="kind", match=models.MatchValue(value="report")),
    models.FieldCondition(key="zone", match=models.MatchValue(value="buffer")),
])
```

`must` means every condition has to hold (AND). Qdrant also has `should` (at least one, OR) and `must_not` (NOT), and
conditions for ranges (dates, numbers), lists of values, text and geographic areas.

The filter is applied **during** the search, not afterwards. That difference matters: if you took the 3 nearest chunks
first and then threw away the ones from the wrong zone, you might be left with none. Filtering inside the search always
returns the 3 nearest chunks **among those that match**.

```python
hits = client.query_points("fieldbook", query=query_vector.tolist(), limit=3, query_filter=the_filter).points
```

Each hit has `.payload` (the chunk), `.score` (the cosine) and `.id`.
:::

:::step{type=task task=filtered_search title="Your turn: search with payload filters" file="08-qdrant/fieldbook.py" line="272-279"}
Write `filtered_search(client, query_vector, k=5, kind=None, zone=None)`:

1. Make a `FieldCondition` for `kind` if it is not `None`, and one for `zone` if it is not `None`.
2. Call `client.query_points(COLLECTION, query=query_vector.tolist(), limit=k, query_filter=...)`, passing
   `models.Filter(must=conditions)` when there are conditions and `None` when there are none.
3. Return `[dict(hit.payload, score=hit.score) for hit in ...points]`.

```bash run
cd /workspace/08-qdrant && python store.py
```

Press **Check**.
:::

:::step{type=history title="The vector database"}
:::before{title="A library and a pile of files"}
Teams kept their vectors in a FAISS index in memory and their data in a separate database, and wrote the glue themselves:
matching ids, saving and reloading the index, filtering, updates, backups.
:::

Vector search libraries came first: Spotify's **Annoy** (**2013**), **FAISS** (**2017**), hnswlib (**2018**). Then
databases built around them, with storage, payloads, filters and APIs: **Milvus** (open-sourced **2019**), **Weaviate**
(**2019**), **Pinecone** (a managed service, generally available in **2021**), **Qdrant** (first released in **2021**,
written in Rust in Berlin), **Chroma** (**2022**). Existing databases added vectors too: Andrew Kane's **pgvector** for
Postgres (**2021**), and HNSW in Lucene, so in Elasticsearch and OpenSearch. When RAG took off in **2023**, vector
databases went from a niche to one of the busiest corners of the database world.

:::solved
**Vectors and data together.** One system stores, filters, searches, updates and backs up both, so the application only
asks questions.
:::

:::timeline
- **2013** Annoy (Spotify).
- **2017** FAISS.
- **2019** Milvus and Weaviate open-sourced.
- **2021** Qdrant, pgvector, Pinecone generally available.
- **2023** RAG makes vector databases mainstream.
:::
:::

:::step{type=try title="Leopards near people, three ways"}
```text
$ python store.py
55 points in the collection 'fieldbook'

'a leopard near people', no filter:
  0.739  [FM-4.3] Leopards near villages
  0.686  [R-0410] Patrol report R-0410, 2026-04-28, beat B-10
  0.664  [R-0407] Patrol report R-0407, 2026-04-19, beat B-12

'a leopard near people', reports only:
  0.686  [R-0410] Patrol report R-0410, 2026-04-28, beat B-10
  0.664  [R-0407] Patrol report R-0407, 2026-04-19, beat B-12
  0.650  [R-0302] Patrol report R-0302, 2026-03-05, beat B-11

'a leopard near people', reports from the buffer zone:
  0.686  [R-0410] Patrol report R-0410, 2026-04-28, beat B-10
  0.650  [R-0302] Patrol report R-0302, 2026-03-05, beat B-11
  0.554  [R-0307] Patrol report R-0307, 2026-03-18, beat B-09
```

1. **No filter:** the manual's leopard section wins, then two reports.
2. **Reports only:** the manual drops out, and a third report comes in: R-0302, the leopard that took a goat in Pimpri.
3. **Reports from the buffer zone:** R-0407 (a leopard on the safari viewpoint, in the tourism zone) drops out. The two
   buffer-zone leopard reports remain, and the third place goes to R-0307, which is about **gaur**, not leopards.

That last line is worth a second look. A filter makes the pool smaller; the search still returns `k` results, the
nearest ones that are left, however weak. Only two buffer-zone reports mention leopards, so the third is the next
closest thing: its score (0.554) is clearly lower. Chapter 11 decides what to do with weak results.

The animal in the third result: a gaur, the Indian bison, the subject of report R-0307.

:::photo{src="/lesson-images/rag/gaur.webp" alt="A large dark gaur with curved horns walking along a forest edge" credit="PJeganathan" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AIndian_Gaur_from_anaimalai_hills_JEG5290.jpg"}
A gaur in the Anaimalai hills.
:::
:::

:::step{type=predict title="Guess first"}
:::question
You search for 5 results with zone="tourism" and kind="report". Only three reports are from the tourism zone. How many results come back?
:::
- [ ] 5: Qdrant fills up with other zones
- [x] 3: only points that match the filter can be returned
- [ ] 0: the filter needs at least k matches
:::explain
The filter is a hard condition. `limit` is the most you get, not a promise.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why filter inside the search rather than take the top 3 and then drop the wrong zones?
:::
- [x] Dropping afterwards can leave fewer than 3 results, or none, even when matching chunks exist further down
- [ ] Filtering afterwards is impossible in Python
- [ ] Filtering inside changes the scores
:::explain
This is called pre-filtering (inside) against post-filtering (after). Databases work hard to make pre-filtering fast with
HNSW.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `upsert` do when you load the same 55 chunks a second time?
:::
- [ ] Adds them again: 110 points
- [x] Replaces the points with the same ids: still 55
- [ ] Raises an error for duplicate ids
:::explain
Stable ids make re-loading safe. Use ids that belong to the document (or a UUID made from it), not random ones.
:::
:::

:::step{type=deep-dive title="Go deeper: Qdrant and its alternatives in production"}
**From local mode to a server.** `QdrantClient(path="qdrant_data")` keeps the collection on disk between runs. A server is
one Docker command (`docker run -p 6333:6333 qdrant/qdrant`) and one changed line:
`QdrantClient(url="http://localhost:6333")`. The server builds a real HNSW index (local mode searches by brute force,
which is fine for thousands of points), supports quantization (chapter 7) with rescoring, and adds snapshots and
replication.

**Payload indexes.** For fast filters on large collections, tell the server which payload fields you filter on:
`client.create_payload_index("fieldbook", "zone", "keyword")`.

**Which database?**

| Option | Good when |
|---|---|
| NumPy or FAISS in memory | under about 100,000 vectors, one process, rebuilt at start |
| pgvector | you already run Postgres and want vectors next to your tables, in SQL |
| Qdrant, Weaviate, Milvus | vectors are the main workload: filters, quantization, scale, hybrid search |
| A managed service (Pinecone and others) | you do not want to run servers |

They all do what you built in chapters 3 to 7. Compare them on your data with chapter 12's measurements.
:::

:::step{type=recap}
You can now:

- explain collections, points, ids and payloads;
- create a Qdrant collection and upsert chunks with their metadata;
- search with payload filters (must, should, must_not), and know why filtering happens inside the search;
- read a filtered result honestly: a smaller pool can return weaker matches.

That ends Part 2. Next, chapter 9: when exact words beat meaning, and how to get both.

:::photo{src="/lesson-images/rag/rag-08-notes.webp" alt="Handwritten notes about Qdrant: Collection: size and distance; Point: id, vector, payload; Upsert: insert or update; Filters inside the search; Fewer matches, weaker results" ai="true"}
One page of notes for this chapter.
:::
:::
