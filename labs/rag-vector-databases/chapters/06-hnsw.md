:::step{type=story title="Ask for directions"}
IVF looks in the right drawers. HNSW does something different: it asks for directions.

Picture a new guard who needs to find a particular water hole. They ask the nearest ranger, who says "go towards the
river, ask at River Gate". At River Gate someone says "the southern beats, ask the B-07 guard". The B-07 guard points to
the exact spot. Nobody knew the whole forest; each person only knew their neighbours, and every step got closer.

**HNSW** (Hierarchical Navigable Small World) is a graph of vectors built so that this works: every vector is linked to a
few of its near neighbours, and a search walks from neighbour to neighbour, always towards the query. It is the default
index in Qdrant, Weaviate, Milvus, pgvector, Elasticsearch and most other vector databases, and in this chapter you build
one with FAISS and learn to tune it by measurement.

:::mission
Measure recall the way every ANN benchmark does, then find the smallest search effort (efSearch) that reaches a recall
target, and compare HNSW's speed and memory with brute force and IVF.
:::
:::

:::step{type=concept title="A graph you can walk" file="06-hnsw/fieldbook.py" line="191-203"}
**The graph.** Every vector is a node, linked to up to `M` of its nearest neighbours (M = 32 here). To search, start at an
entry node, look at its neighbours, move to whichever is closest to the query, and repeat until no neighbour is closer.
That greedy walk is fast because each step is a handful of dot products.

**The hierarchy.** A walk across 100,000 nodes in small steps would still be long, so HNSW adds layers, like a road map:
the top layer has a few nodes with long links (highways), each lower layer has more nodes and shorter links, and the bottom
layer holds every vector. The search starts at the top, gets close quickly on the long links, then drops down a layer at a
time to refine.

:::diagram{name="rag-hnsw"}
The search enters at the top layer, takes long hops towards the query, and drops down until it reaches the bottom layer.
:::

**The two settings that matter:**

| Setting | When | Bigger means |
|---|---|---|
| `M` | building | more links per node: better recall, more memory, slower build |
| `efConstruction` | building | more care when choosing links: a better graph, slower build |
| `efSearch` | every query | the walk keeps more candidates: better recall, slower query |

`efSearch` is the one you tune most, because it can change at query time without rebuilding: `index.hnsw.efSearch = 64`.

`exact_neighbours` (FAISS's `IndexFlatIP`: chapter 3's brute force in C++) gives the true answer, and `hnsw_index`
builds the graph.
:::

:::step{type=concept title="Recall, precisely" file="06-hnsw/fieldbook.py" line="206-211"}
Chapter 5 measured recall in the benchmark script. Now you write it, because every tuning decision depends on it.

For each query you have the ids the index **found** and the **true** k nearest ids from brute force:

:::trace{title="recall at k = 3 for two queries"}
| query | found | truth | in both | recall |
|---|---|---|---|---|
| 1 | 4, 9, 2 | 4, 2, 7 | 4, 2 | 2 / 3 |
| 2 | 5, 1, 8 | 5, 1, 8 | 5, 1, 8 | 3 / 3 |
| average | | | | (0.667 + 1.0) / 2 = 0.833 |
:::

Order does not matter inside the top k (sets), and only the first k found ids count: an index that returns the right id
in 11th place has not found it in the top 10.
:::

:::step{type=task task=recall_at_k title="Your turn: measure recall" file="06-hnsw/fieldbook.py" line="206-211"}
Write `recall_at_k(found, truth)`. `k` is the length of a truth row. For each pair of rows, count how many of the first k
found ids are in the truth row (`len(set(f[:k]) & set(t))`), divide by k, and return the average over all queries as a
plain `float`.

Press **Check**.
:::

:::step{type=history title="Small worlds"}
:::before{title="Trees that stop working"}
For low-dimensional data (maps, two or three numbers per point), tree indexes like the k-d tree (**1975**) find
neighbours fast. With hundreds of dimensions they degrade to checking almost everything: the curse of dimensionality from
chapter 3.
:::

In **1967** the psychologist Stanley Milgram asked people in Nebraska and Kansas to get a letter to a stranger in Boston by
passing it only to someone they knew personally. The letters that arrived took about six steps: the **small world**
effect, "six degrees of separation". Duncan Watts and Steven Strogatz explained in **1998** how a few long links make any
network small. William Pugh's **skip list** (**1990**) had shown how layers of longer and longer jumps make a sorted list
fast to search. Yury Malkov and his colleagues built "navigable small world" graphs for vector search (**2014**), and Malkov
and Dmitry Yashunin added the layers in **2016**: **HNSW**. It won the public ANN benchmarks and became the default index
of almost every vector database.

:::solved
**A few hops instead of every vector.** Recall close to 100% at a small fraction of the cost of brute force, and a dial
(efSearch) that can be turned per query.
:::

:::timeline
- **1967** Milgram's small-world letters.
- **1990** Pugh's skip lists.
- **1998** Watts and Strogatz: small-world networks.
- **2016** HNSW (Malkov and Yashunin).
- **2023** HNSW in pgvector.
:::

Stanley Milgram, whose letters reached strangers across the United States in about six steps.

:::photo{src="/lesson-images/rag/milgram.webp" alt="A black and white portrait of Stanley Milgram, a man with a beard, speaking" credit="Unknown authorUnknown author" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AStanley_Milgram_1974.jpg"}
Stanley Milgram, around 1974.
:::
:::

:::step{type=concept title="Tuning by measurement" file="06-hnsw/fieldbook.py" line="214-219"}
"Which efSearch should I use?" has one honest answer: the **smallest** one that reaches the recall your application needs,
measured on queries like yours. Smaller means faster, so you try values from small to large and stop at the first that is
good enough:

```text
target 0.95:   efSearch 16 -> 0.877 (no)   32 -> 0.949 (no)   64 -> 0.989 (yes: answer 64)
```

`index.search(queries, k)` searches all queries at once and returns two arrays: the scores and the ids, one row per
query. Recall needs only the ids: `_, found = index.search(queries, k)`.
:::

:::step{type=task task=tune_ef title="Your turn: the smallest efSearch that is good enough" file="06-hnsw/fieldbook.py" line="214-219"}
Write `smallest_ef(index, queries, truth, k=10, target=0.95, choices=(...))`: for each value in `choices`, in order, set
`index.hnsw.efSearch` to it, search the queries, and measure `recall_at_k(found, truth)`. Return the first value whose
recall reaches the target, or `None` if none does.

```bash run
cd /workspace/06-hnsw && python hnsw_bench.py
```

Press **Check**.
:::

:::step{type=try title="HNSW against brute force"}
`hnsw_bench.py` uses one CPU thread for both searches, so the comparison is fair:

```text
$ python hnsw_bench.py
brute force: 6.57 ms a query
built an HNSW graph of 100,000 vectors in 18.2 s, about 181 MB (the vectors alone: 154 MB)

efSearch  16: recall  87.7%, 0.066 ms a query
efSearch  32: recall  94.9%, 0.109 ms a query
efSearch  64: recall  98.9%, 0.188 ms a query
efSearch 128: recall  99.8%, 0.341 ms a query
efSearch 256: recall 100.0%, 0.637 ms a query
```

| | Recall | Time a query | Extra memory | Build |
|---|---|---|---|---|
| brute force | 100% | 6.57 ms | none | none |
| IVF, nprobe 16 (chapter 5) | 92% | 1.10 ms | the centroids, tiny | 2.6 s |
| **HNSW, efSearch 64** | **98.9%** | **0.188 ms** | 27 MB of links | 18.2 s |

At efSearch 64, HNSW finds 98.9% of the true neighbours **35 times faster** than brute force. That is why it is the
default almost everywhere. The prices are in the other two columns:

1. **Memory.** The links take 27 MB on top of the 154 MB of vectors (M = 32 means up to 64 links per node on the bottom
   layer, 4 bytes each), and the whole graph must stay in RAM to be fast.
2. **Build time.** 18 seconds for 100,000 vectors on one thread, seven times longer than training IVF. Every insert has to
   find its neighbours, so loading millions of vectors takes a while.

And the dial: from efSearch 16 to 256, recall goes from 87.7% to 100% while time grows about tenfold. With a target of
95%, `smallest_ef` picks 64.
:::

:::step{type=predict title="Guess first"}
:::question
After building the index, you raise efSearch from 64 to 128. Do you need to rebuild?
:::
- [ ] Yes, the graph depends on efSearch
- [x] No: efSearch only changes how many candidates a query keeps; M and efConstruction are the build settings
- [ ] Only if recall gets worse
:::explain
That is what makes efSearch the everyday dial: one query can use 32, another 256.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is HNSW so much faster than brute force?
:::
- [x] A search visits a few hundred nodes along the graph instead of all 100,000 vectors
- [ ] It uses a GPU
- [ ] It compresses the vectors
:::explain
Each hop costs a handful of dot products; the layers make the number of hops small.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Your application needs recall of at least 99%. From the table above, which efSearch would you start with?
:::
- [ ] 64
- [x] 128: the smallest that reaches 99% (99.8%)
- [ ] 256, to be safe
:::explain
64 gives 98.9%, just short. 256 also passes but costs almost twice as much as 128 for 0.2% more recall.
:::
:::

:::step{type=deep-dive title="Go deeper: HNSW in production"}
**Memory is the limit.** HNSW wants everything in RAM. For 100 million vectors of 384 numbers, that is about 154 GB of
vectors plus the links. Chapter 7's quantization is how real systems fit.

**Deletes and updates** are hard in a graph: most databases mark deleted nodes and clean up later, and heavy churn slowly
degrades recall until the index is rebuilt.

**Filters** (chapter 8) interact badly with graphs: if most nodes are filtered out, the walk runs out of allowed
neighbours. Databases handle this with special strategies (Qdrant builds extra links per payload value; pgvector 0.8
added iterative index scans).

**Benchmarks.** ann-benchmarks.com compares HNSW, IVF and dozens of other indexes on public datasets with exactly this
chapter's two axes: recall and queries per second.
:::

:::step{type=recap}
You can now:

- explain how HNSW searches: greedy walks on a layered graph of neighbours;
- measure recall at k against brute force;
- tune efSearch by measurement, choosing the smallest value that meets a target;
- weigh HNSW's speed against its memory and build time, next to brute force and IVF.

Next, chapter 7: shrinking the vectors themselves.

:::photo{src="/lesson-images/rag/rag-06-notes.webp" alt="Handwritten notes about HNSW: A graph of near neighbours; Layers: long hops, then short; efSearch: the query dial; Smallest ef that is good enough; Fast, but needs RAM" ai="true"}
One page of notes for this chapter.
:::
:::
