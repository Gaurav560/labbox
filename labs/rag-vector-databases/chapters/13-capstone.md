:::step{type=story title="Fieldbook goes on the radio network"}
Everything Fieldbook can do lives in `fieldbook.py`: load and chunk the documents, embed them, search by meaning and by
words, fuse, rerank, gate and answer with sources. Rangers do not run Python scripts, though. The control room wants
Fieldbook on the sanctuary's network, where the rangers' phones app, the control room's dashboard and any future tool
can ask it questions.

That means a **web service** with two endpoints:

| Endpoint | For | Returns |
|---|---|---|
| `GET /search?q=...&kind=...&zone=...` | the dashboard: "show me the documents" | the best chunks with their scores |
| `POST /ask` with a question | the phones: "just tell me" | an answer with its sources, or an honest "not found" |

You will build it with **FastAPI**, the Python web framework that turns type hints into an API, and then use it the way
its users will: with HTTP requests.


The kind of forest Fieldbook serves: evergreen forest in the Western Ghats.

:::photo{src="/lesson-images/rag/western-ghats.webp" alt="Tall trees in an evergreen forest with sunlight streaming through the canopy" credit="Rohitjahnavi" license="CC0" source="https://commons.wikimedia.org/wiki/File%3AEvergreen_forest%2C_rainforest%2C_Makutta_Range%2C_Western_Ghats%2C_Karnataka%2C_India.jpg"}
Evergreen forest in the Makutta Range, Western Ghats, Karnataka.
:::
:::mission
Write the two endpoints on top of the pipeline you built, run Fieldbook as a service, and ask it questions over HTTP.
:::
:::

:::step{type=concept title="The service around the pipeline" file="13-capstone/app.py" line="11-34"}
`app.py` has everything except the two endpoints:

| Piece | Does |
|---|---|
| `app = FastAPI(title="Fieldbook")` | the web application |
| `index()` | builds the `Index` once, on the first request (`@lru_cache`): all 55 chunks embedded and tokenized, a few seconds |
| `client()` | one OpenAI client for the model, reused |
| `find(q, kind, zone, k)` | the two-stage search from chapter 10, keeping only chunks that match the filters |
| `Question` | the shape of a POST body: `{"question": "..."}`; FastAPI checks it and answers 422 if it is wrong |

Building the index once matters: embedding every chunk on every request would add seconds to each one. A real service
pays that cost at start-up (or loads saved vectors from a vector database, chapter 8) and then answers from memory.
:::

:::step{type=concept title="Endpoints from functions" file="13-capstone/app.py" line="37-46"}
In FastAPI an endpoint is a function with a decorator. The function's parameters become the request's inputs:

```python
@app.get("/search")
def search(q: str, kind: str | None = None, zone: str | None = None, k: int = 5):
    ...
```

`GET /search?q=leopard&kind=report&k=3` calls `search(q="leopard", kind="report", zone=None, k=3)`. FastAPI converts
`k` from the text "3" to the integer 3 and answers 422 if `q` is missing. Whatever the function returns (a dict, a list)
is sent back as JSON.

The search endpoint's answer should be useful to a dashboard and small: for each chunk its id, its title and its score,
rounded, not the whole text.
:::

:::step{type=task task=search_endpoint title="Your turn: GET /search with filters" file="13-capstone/app.py" line="42-46"}
Write `search(...)`: call `find(q, kind, zone, k)` and return

```text
{"query": q, "results": [{"id": ..., "title": ..., "score": ...}, ...]}
```

with one result per chunk, the score being the chunk's `"rerank"` value rounded to 2 places.

Press **Check**.
:::

:::step{type=task task=ask_endpoint title="Your turn: POST /ask with sources" file="13-capstone/app.py" line="49-53"}
Write `ask(body: Question)`: find the best chunks for `body.question` with no filters, and return
`answer(body.question, chunks, client())`, chapter 11's function, which gates, prompts, and returns the answer with its
sources.

Press **Check**, then start the service:

```bash run
cd /workspace/13-capstone && uvicorn app:app --host 0.0.0.0 --port 8000
```

And in a second terminal:

```bash run
curl -s "localhost:8000/search?q=leopard+in+a+village&kind=report&k=3"
```
:::

:::step{type=try title="Fieldbook over HTTP"}
The service's terminal, after the first request:

```text
INFO:     Started server process [117]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:41334 - "GET /health HTTP/1.1" 200 OK
```

The dashboard's search, reports only, then reports from the buffer zone only:

```text
$ time curl -s "localhost:8000/search?q=leopard+in+a+village&kind=report&k=3"; echo
{"query":"leopard in a village","results":[{"id":"R-0302","title":"Patrol report R-0302, 2026-03-05, beat B-11","score":5.03},{"id":"R-0410","title":"Patrol report R-0410, 2026-04-28, beat B-10","score":4.04},{"id":"R-0407","title":"Patrol report R-0407, 2026-04-19, beat B-12","score":-6.28}]}
real	0m6.218s
...
$ curl -s "localhost:8000/search?q=leopard+in+a+village&kind=report&zone=buffer&k=3"; echo
{"query":"leopard in a village","results":[{"id":"R-0302","title":"Patrol report R-0302, 2026-03-05, beat B-11","score":5.03},{"id":"R-0410","title":"Patrol report R-0410, 2026-04-28, beat B-10","score":4.04},{"id":"R-0309","title":"Patrol report R-0309, 2026-03-24, beat B-10","score":-8.54}]}
```

The two leopard-in-a-village reports come first with high scores (5.03 and 4.04). The third result is weak in both
cases (-6.28 for the leopard on the safari viewpoint; -8.54 for the snakebite near Rajur once the filter removes the
tourism zone): as chapter 8 showed, a filter makes the pool smaller and the last places go to whatever is left. The
scores let the dashboard grey out such results.

The first request took **6.2 seconds**: building the index (embedding all 55 chunks) and loading the reranker happened
then. The same request again:

```text
$ time curl -s "localhost:8000/search?q=leopard+in+a+village&kind=report&k=3" > /dev/null

real	0m0.612s
```

0.6 seconds, almost all of it reranking. The phones' question, then one the documents cannot answer, then a mistake in
the request:

```text
$ curl -s -X POST localhost:8000/ask -H "content-type: application/json" -d "{\"question\": \"Which animal injures the most people?\"}"; echo
{"answer":"The sloth bear injures more people in India than any other wild animal, primarily because it attacks when surprised at close range [1].","sources":["FM-4.5","FM-4.1","FM-4.6","FM-8.1","FM-7.3"]}
$ curl -s -X POST localhost:8000/ask -H "content-type: application/json" -d "{\"question\": \"What is the entry fee for a foreign tourist?\"}"; echo
{"answer":"I could not find this in the Fieldbook.","sources":[]}
$ curl -s -i -X POST localhost:8000/ask -H "content-type: application/json" -d "{\"q\": \"Which gate sells safari permits?\"}"; echo
HTTP/1.1 422 Unprocessable Entity
...
{"detail":[{"type":"missing","loc":["body","question"],"msg":"Field required","input":{"q":"Which gate sells safari permits?"}}]}
```

(Shortened with "...".) An answer with its citation and sources; an honest "not found" that never reached the model;
and a request with `q` instead of `question`, refused by FastAPI before your code ran, with an error that names the
missing field. Fieldbook is a service.
:::

:::step{type=history title="From scripts to services"}
:::before{title="Programs for one user"}
A program on one computer served the person sitting at it. Sharing it meant copying it to every machine.
:::

Tim Berners-Lee's **HTTP** (**1991**) let any program ask another for a document by its address. Roy Fielding described
the style of **REST** in **2000**: resources at paths, read with GET, changed with POST and PUT. **JSON**, popularised by
Douglas Crockford in the early **2000s**, became the common language of these services. In Python, Flask (**2010**) made
small web services easy, and Sebastián Ramírez's **FastAPI** (**2018**) used type hints to check requests and write
interactive documentation automatically. Today a RAG system is almost always a service like this one: an index in memory,
a model behind it, and two or three endpoints in front.

:::solved
**One Fieldbook for every client.** Phones, dashboards and other services ask the same endpoint and get the same,
cited answers.
:::

:::timeline
- **1991** HTTP.
- **2000** REST.
- **2010** Flask.
- **2018** FastAPI.
:::

Tim Berners-Lee, who invented the web and HTTP at CERN, the protocol every request in this chapter uses.

:::photo{src="/lesson-images/rag/berners-lee.webp" alt="Tim Berners-Lee, an older man with thinning grey hair and a headset microphone, in a dark jacket, on a stage with a pink screen behind him" credit="Amy Martin Photography" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ASir_Tim_Berners-_Lee.jpg"}
Tim Berners-Lee at SXSW London, 2026.
:::
:::

:::step{type=predict title="Guess first"}
:::question
The service has just started. The first request took 6.2 seconds, the same request again 0.6 seconds. Why?
:::
- [ ] The model is slow to wake up
- [x] index() builds the index on the first request (embedding every chunk) and the reranker loads; later requests reuse both
- [ ] FastAPI compiles the endpoint
:::explain
`@lru_cache` keeps the built index. A real service builds or loads it at start-up so that no user waits.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A client sends `POST /ask` with `{"q": "Which gate sells safari permits?"}`. What happens?
:::
- [ ] Fieldbook answers the question
- [x] FastAPI answers 422: the body does not match Question, which needs a "question" field
- [ ] The service crashes
:::explain
The request is checked against the model class before your function runs, and the error names the missing field.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does /search return only ids, titles and scores, not the chunks' text?
:::
- [x] The dashboard lists results; smaller responses are faster, and the full text can be fetched for the one the user opens
- [ ] JSON cannot hold long text
- [ ] The text is secret
:::explain
Design an endpoint's response for what its client shows, not for everything you have.
:::
:::

:::step{type=deep-dive title="Go deeper: Fieldbook in production"}
**Persist the index.** Rebuilding embeddings at every start does not scale. Store the vectors in Qdrant (chapter 8) or
pgvector, embed only new or changed documents, and record which embedding model made them.

**New documents.** Patrol reports arrive daily. Add an endpoint or a job that chunks, embeds and upserts new reports; with
stable ids, re-sending one replaces it.

**Filters in the database.** `find` filters after the hybrid search, which works for 55 chunks. At scale, push the
filters into the vector database's query (chapter 8) so they apply during the search.

**Cost and safety.** Log every question, the sources found and the answer (for chapter 12's golden set and for audits),
rate-limit the endpoint, and cache answers to repeated questions. Only `/ask` costs money (one model call), and only
when the gate lets it through.
:::

:::step{type=deep-dive title="You built Fieldbook from nothing"}
Thirteen chapters ago, a model answered a ranger's question with a confident guess. Since then you have built every part
of a RAG system yourself:

| Part | You built | And measured |
|---|---|---|
| Retrieval from scratch | keyword search, embeddings, brute-force search, chunking | "big cat" found by meaning; 91% first-time hits by chunking along sections |
| Inside a vector database | IVF, HNSW, int8 and binary quantization, Qdrant with filters | 35 times faster than brute force at 98.9% recall; 32 times less memory with full recall after rescoring |
| RAG that works | BM25, rank fusion, reranking, grounded answers, evaluation, a service | where hybrid helps and hurts; 88% right first time with reranking |

Where to go next: read the documentation of the vector database you will use in production (Qdrant, pgvector, Weaviate
or Milvus), now that you know what is inside it; build a golden set for your own documents before anything else; and
read the original papers behind this course (the RAG paper, HNSW, product quantization, BM25, reciprocal rank fusion):
every one of them is readable now.
:::

:::step{type=recap}
You can now:

- wrap a retrieval pipeline in a FastAPI service with filtered search and cited answers;
- design endpoint responses for their clients;
- explain what changes for production: a persistent index, updates, filters in the database, logging and caching;
- build, measure and explain a RAG system from the first embedding to the last citation.

That is the end of the course. Fieldbook is on the sanctuary's network, and every answer can say where it came from.

:::photo{src="/lesson-images/rag/rag-13-notes.webp" alt="Handwritten notes about the capstone: GET /search: ids, titles, scores; POST /ask: answer with sources; Build the index once; Filters, gate, citations; Measure before you change" ai="true"}
One page of notes for this chapter.
:::
:::
