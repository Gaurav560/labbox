:::step{type=story title="Only the reports, only the buffer zone"}
The range officer asks Fieldbook: *"Leopards near people: what happened in the buffer zone villages this spring?"* The
nearest chunk by meaning is FM-4.3, the manual's section on leopards near villages. Useful, but it is not what she asked.
She wants **patrol reports**, and only those from the **buffer zone**, the belt of villages around the protected core.

Your NumPy matrix knows nothing about kinds of documents or zones; it only holds numbers. Real searches nearly always come
with conditions like these: this customer's documents only, this year only, only what this user may see. A system that
keeps vectors **together with their data** and searches with conditions is a **vector database**.

You have now built the main parts of one yourself: embeddings, exact search, IVF, HNSW and quantization. Time to use a
real one. Fieldbook uses **Qdrant**, an open-source vector database written in the Rust programming language. Your
Python code talks to it through a **client**: a Python library that sends your requests to Qdrant and returns the
answers. The client also has a **local mode** that runs Qdrant's features inside your own Python program, with no
server to install. It is meant for development and small collections. In production you change one line, and the same
code talks to a Qdrant server.

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
Qdrant uses four words, and each maps to something you already have:

| Word | Means | In Fieldbook |
|---|---|---|
| **collection** | a named set of points; all its vectors have the same size and are compared the same way | `"fieldbook"`: 384 numbers (bge-small's size), cosine |
| **point** | one stored item: an id, a vector and a payload | one chunk |
| **id** | the point's name: a whole number (0 or more) or a UUID, a 36-character random identifier | the chunk's position, 0 to 54 |
| **payload** | any JSON data stored next to the vector (JSON is the common text format for keys and values, like a Python dict) | the chunk itself: id, title, text, kind and zone; reports also have beat and date |

Fieldbook's 55 chunks are 31 manual sections (`kind` "manual", `zone` "all") and 24 patrol reports (`kind` "report";
15 from the core zone, 6 from the buffer zone, 3 from the tourism zone).

Creating a collection and adding points:

```python
client = QdrantClient(":memory:")                     # local mode: inside this program, in memory
client.create_collection(
    "fieldbook",
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)
client.upsert("fieldbook", points=[
    models.PointStruct(id=0, vector=[...384 numbers...], payload={"id": "FM-1.1", "kind": "manual", ...}),
    ...
])
```

Line by line:

- `QdrantClient(":memory:")` opens local mode, keeping everything in memory; it is gone when the program ends.
- `create_collection` names the collection and fixes two things for every vector in it: its size and its **distance**,
  the way two vectors are compared. Cosine is what chapters 2 and 3 used.
- `upsert` stores points. **Upsert** means insert, or update if the id already exists: run it twice and you still have
  55 points.
- `v.tolist()` turns a NumPy row into a plain Python list. This version of the client (1.20) also accepts a NumPy
  array, but a plain list works with every version and with a remote server.

Because the payload is the chunk, a search result already carries the text to show the model: no second lookup.
:::

:::step{type=task task=make_store title="Your turn: a collection of points" file="08-qdrant/fieldbook.py" line="263-269"}
Write `make_store(chunks, vectors)`:

1. `client = QdrantClient(":memory:")`.
2. Create the collection `COLLECTION` with `models.VectorParams(size=vectors.shape[1], distance=models.Distance.COSINE)`.
   (`vectors.shape[1]` is the number of numbers per vector, 384 here; reading it from the data means the code still
   works with another model.)
3. Upsert one `models.PointStruct(id=i, vector=v.tolist(), payload=c)` for every chunk `c` and its vector `v`. A list
   comprehension over `enumerate(zip(chunks, vectors))` gives you `i`, `c` and `v` together.
4. Return the client.

The usual slips:

- Writing `size=384` by hand: it works here, but breaks the day you switch models.
- Using the chunk's text id (`"FM-1.1"`) as the point id: Qdrant accepts only whole numbers or UUIDs. Keep the text id
  in the payload.

Press **Check**.
:::

:::step{type=concept title="Search with conditions" file="08-qdrant/fieldbook.py" line="272-279"}
A Qdrant query takes the question's vector, how many results you want, and optionally a **filter**: conditions on the
payload that a point must meet.

```python
models.Filter(must=[
    models.FieldCondition(key="kind", match=models.MatchValue(value="report")),
    models.FieldCondition(key="zone", match=models.MatchValue(value="buffer")),
])
```

- A `FieldCondition` names a payload key and the value it must have.
- `must` means every condition in the list has to hold (AND). Qdrant also has `should` (at least one must hold, OR) and
  `must_not` (none may hold, NOT), and conditions for ranges (dates, numbers), lists of allowed values, words in a text
  and geographic areas.

**The filter is applied during the search, not afterwards.** That difference matters. If you took the 3 nearest chunks
first and then threw away the ones that do not match, you might be left with fewer than 3, or none, even when matching
chunks exist further down the list. Filtering during the search returns the 3 nearest chunks **among those that match**.
In local mode the search is exact, so these are exactly the 3 nearest matches. A Qdrant server with an HNSW index
checks the filter while it walks the graph, so it returns them approximately, like any HNSW search.

:::diagram{name="rag-filter"}
The real question from this chapter. Filtering after a top-3 search keeps only R-0410; filtering inside the search
returns three buffer-zone reports, the third one weaker.
:::

```python
hits = client.query_points("fieldbook", query=query_vector.tolist(), limit=3, query_filter=the_filter).points
```

Each hit has `.payload` (the chunk), `.score` (the cosine similarity) and `.id`.
:::

:::step{type=task task=filtered_search title="Your turn: search with payload filters" file="08-qdrant/fieldbook.py" line="272-279"}
Write `filtered_search(client, query_vector, k=5, kind=None, zone=None)`:

1. Build a list of conditions: a `FieldCondition` for `kind` if it is not `None`, and one for `zone` if it is not `None`.
2. Call `client.query_points(COLLECTION, query=query_vector.tolist(), limit=k, query_filter=...)`, passing
   `models.Filter(must=conditions)` when the list has conditions and `None` when it is empty.
3. Return `[dict(hit.payload, score=hit.score) for hit in ...points]`: each chunk with its score added.

The usual slips:

- Forgetting `.points` at the end of `query_points(...)`: the call returns a response object, and the hits are inside.
- Adding a condition for every argument, even when it is `None`: the client refuses `MatchValue(value=None)` with a
  `ValidationError`. Skip the arguments that are `None`.

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

Vector search **libraries** came first: code you call from your own program. Spotify's **Annoy** (**2013**), Facebook's
**FAISS** (**2017**), and hnswlib, the HNSW library from the method's first author, Yury Malkov.

Then came **databases** built around such search, with storage, payloads, filters and network access:

- **Weaviate**, an open-source project since **2016** (version 1.0 in **2021**);
- **Milvus**, open-sourced in **2019**;
- **Pinecone**, a managed service, launched publicly in **2021**;
- **Qdrant**, first released in **2021**, written in Rust, from Berlin;
- **Chroma**, first released in **2022**.

Existing databases added vectors too: Andrew Kane's **pgvector** for Postgres (**2021**), and HNSW in Lucene 9 (**2021**),
the search library inside Elasticsearch and OpenSearch. When RAG took off in **2023**, vector databases went from a niche
to one of the busiest corners of the database world.

:::solved
**Vectors and data together.** One system stores, filters, searches, updates and backs up both, so the application only
asks questions.
:::

:::timeline
- **2013** Annoy (Spotify).
- **2016** Weaviate starts as an open-source project.
- **2017** FAISS.
- **2019** Milvus open-sourced.
- **2021** Qdrant, pgvector, Pinecone launched; HNSW in Lucene.
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

What changed each time:

1. **No filter:** the manual's leopard section wins, then two reports.
2. **Reports only:** the manual drops out, and a third report comes in: R-0302, the leopard that took a goat in Pimpri
   village.
3. **Reports from the buffer zone:** R-0407 (a leopard resting at a safari viewpoint, in the tourism zone) drops out.
   The two buffer-zone leopard reports remain (R-0410 in Rajur village, R-0302 in Pimpri), and third place goes to
   R-0307, which is about a herd of **gaur**, not leopards.

That last line is worth a second look. A filter makes the pool smaller; the search still returns up to `k` results, the
nearest ones that are left, however weak. Only two of the six buffer-zone reports mention leopards, so the third result
is the next closest thing, and its score (0.554) is clearly lower. Chapter 11 decides what to do with weak results.

The animal in the third result: a gaur, the Indian bison, the subject of report R-0307.

:::photo{src="/lesson-images/rag/gaur.webp" alt="A large dark gaur with curved horns walking along a forest edge" credit="PJeganathan" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AIndian_Gaur_from_anaimalai_hills_JEG5290.jpg"}
A gaur in the Anaimalai hills.
:::
:::

:::step{type=predict title="Guess first"}
:::question
You search for 5 results with zone="tourism" and kind="report". Fieldbook has exactly three reports from the tourism zone. How many results come back?
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
Dropping afterwards is called post-filtering. In this chapter it would leave one result (R-0410) where three exist.
Vector databases work hard to check filters during the search itself, even inside an HNSW graph.
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
**From local mode to a server.** `QdrantClient(path="qdrant_data")` keeps the collection on disk between runs. A server
is one Docker command (`docker run -p 6333:6333 qdrant/qdrant`) and one changed line:
`QdrantClient(url="http://localhost:6333")`. Local mode compares the question with every point (exact search, fine for
small collections). The server builds a real HNSW index, supports quantization with rescoring (chapter 7), and adds
snapshots (backups) and replication (copies on several machines).

**Payload indexes.** For fast filters on large collections, tell the server which payload fields you filter on:
`client.create_payload_index("fieldbook", "zone", "keyword")`.

**Which one?** A rough guide, not a rule:

| Option | Good when |
|---|---|
| NumPy or FAISS inside your program | one program, the vectors fit in memory, loaded or rebuilt at start |
| pgvector | you already run Postgres and want vectors next to your tables, in SQL |
| Qdrant, Weaviate, Milvus | vectors are the main workload: filters, quantization, scale, hybrid search |
| A managed service (Pinecone and others) | you do not want to run servers |

They are all built on the ideas of chapters 3 to 7. Compare them on your own data with chapter 12's measurements.
:::

:::step{type=recap}
You can now:

- explain collections, points, ids and payloads;
- create a Qdrant collection and upsert chunks with their metadata;
- search with payload filters (must, should, must_not), and explain why filtering happens inside the search;
- read a filtered result honestly: a smaller pool can return weaker matches.

That ends Part 2. Next, chapter 9: when exact words beat meaning, and how to get both.

:::photo{src="/lesson-images/rag/rag-08-notes.webp" alt="Handwritten notes about Qdrant: A collection holds points of one vector size and one distance. A point is an id, a vector and a payload. Upsert inserts, or replaces a point with the same id. Filters are checked during the search, not after. A filter shrinks the pool, so results can get weaker. Local mode is for development; production uses a server." ai="true"}
One page of notes for this chapter.
:::
:::
