:::step{type=story title="Ask for directions"}
IVF decides which drawers to open. HNSW works differently: it moves step by step towards the answer, the way you find a
place by asking for directions.

A new guard needs to find one particular water hole. The nearest ranger does not know where it is, but knows it is
towards the river and sends the guard to River Gate. At River Gate, someone sends them on to the southern beats, and the
guard there points to the exact spot. Nobody knew the whole forest; each person knew only their neighbours, and every
step got closer.

**HNSW** (Hierarchical Navigable Small World) builds a structure where this works for vectors. Every vector is linked to
a few of its near neighbours, and a search walks from neighbour to neighbour, always towards the question. It is the main
index of Qdrant, Weaviate and Elasticsearch's vector search, one of the two index types in pgvector (next to IVF), and
one of the index types Milvus offers. In this chapter you build one with **FAISS** (Facebook's library of vector indexes,
already installed in your lab) and learn to tune it by measurement.

:::mission
Measure recall the way every ANN benchmark does, then find the smallest search effort (efSearch) that reaches a recall
target, and compare HNSW's speed and memory with brute force.
:::
:::

:::step{type=concept title="A graph you can walk" file="06-hnsw/fieldbook.py" line="191-203"}
**The graph.** In HNSW every vector is a **node** (a point in the structure), and every node is linked to a few of its
nearest neighbours. A search starts at an entry node, looks at that node's neighbours, moves to whichever one is closest
to the question, and repeats until no neighbour is closer. Each step costs only a handful of dot products, one per
neighbour, so the walk is fast. Always taking the step that looks best right now is called a **greedy** walk.

**The layers.** Crossing 100,000 nodes in small steps would still take many steps, so HNSW stacks several **layers** of
the same graph:

- the **top layer** holds only a few nodes, joined by long links that cross large parts of the space;
- each layer below holds more nodes, with shorter links;
- the **bottom layer** holds every vector.

A search starts at the top, gets close quickly using the long links, then drops down one layer at a time to refine,
until it reaches the bottom layer next to the question.

:::diagram{name="rag-hnsw"}
The search enters at the top layer, hops along long links towards the question, and drops down a layer at a time. The
result at the bottom is this chapter's real benchmark.
:::

**The settings that matter.** Three numbers control an HNSW index:

| Setting | Set when | Bigger means |
|---|---|---|
| `M` | building | more links per node: better recall, more memory, slower build |
| `efConstruction` | building | more care when choosing each node's links: a better graph, slower build |
| `efSearch` | every query | the walk keeps a longer list of candidates: better recall, slower query |

In FAISS, `M` is the number of links per node on the upper layers; the bottom layer allows twice as many. This chapter
uses `M = 32` and `efConstruction = 64`.

`efSearch` is the one you tune most, because you can change it for any query without rebuilding:
`index.hnsw.efSearch = 64`.

Two helper functions are already written for you in `fieldbook.py`:

- `exact_neighbours` uses FAISS's `IndexFlatIP` (flat search by inner product, which is chapter 3's brute force written
  in C++) to get the **true** nearest neighbours: the answer key.
- `hnsw_index` builds the HNSW graph with FAISS's `IndexHNSWFlat`.
:::

:::step{type=concept title="Recall, precisely" file="06-hnsw/fieldbook.py" line="206-211"}
Chapter 5's benchmark computed recall for you. Now you write it yourself, because every tuning decision in this
chapter depends on it.

For each question you have two lists of ids: the ids the index **found**, and the **true** k nearest ids from brute
force. Recall for that question is the share of the true ids that were found. Recall for the whole test is the average
over all questions:

:::trace{title="recall at k = 3 for two questions"}
| question | found | truth | in both | recall |
|---|---|---|---|---|
| 1 | 4, 9, 2 | 4, 2, 7 | 4, 2 | 2 / 3 = 0.667 |
| 2 | 5, 1, 8 | 5, 1, 8 | 5, 1, 8 | 3 / 3 = 1.0 |
| average | | | | (0.667 + 1.0) / 2 = 0.833 |
:::

Two rules:

1. **Order does not matter inside the top k.** If the index returns the true ids in a different order, recall is still
   100%, so compare them as sets.
2. **Only the first k found ids count.** An index that returns the right id in 11th place has not found it in the top
   10, so cut the found list to its first k before comparing.
:::

:::step{type=task task=recall_at_k title="Your turn: measure recall" file="06-hnsw/fieldbook.py" line="206-211"}
Write `recall_at_k(found, truth)` in `06-hnsw/fieldbook.py`:

1. `k` is the length of one truth row: `k = len(truth[0])`.
2. For each pair of rows (`zip(found, truth)`), count the shared ids among the first k found:
   `len(set(f[:k]) & set(t))`, and divide by `k`.
3. Return the average over all questions as a plain Python `float` (`float(np.mean(...))`).

The usual slip: forgetting `f[:k]`, which lets ids found beyond the top k count as hits.

Press **Check**.
:::

:::step{type=history title="Small worlds"}
:::before{title="Trees that stop working"}
For data with few dimensions (a map has two numbers per point), tree indexes such as the k-d tree (**1975**) find
neighbours quickly. With hundreds of dimensions they end up checking almost everything: the curse of dimensionality
from chapter 3.
:::

In **1967** the psychologist **Stanley Milgram** ran a famous experiment. He asked people in Nebraska and Kansas to get
a letter to a stranger in Boston, passing it only to someone they knew personally. The letters that arrived had taken
about six steps on average. This is the **small world** effect, the origin of the phrase "six degrees of separation":
even in a huge network, a few hops connect almost anyone, because some people know others far away.

Duncan Watts and Steven Strogatz explained in **1998** how a few long links make any network "small" in this way.
Separately, William Pugh's **skip list** (**1990**) had shown how layers of longer and longer jumps make a sorted list fast
to search. Yury Malkov and his colleagues built "navigable small world" graphs for vector search in **2014**, and Malkov
and Dmitry Yashunin added the layers in **2016**: **HNSW**. It became one of the top performers on public ANN benchmarks
and the most widely used index in vector databases.

:::solved
**A few hops instead of every vector.** Recall close to 100% at a small fraction of the cost of brute force, and a dial
(efSearch) that can be turned for each query.
:::

:::timeline
- **1967** Milgram's small-world letters.
- **1990** Pugh's skip lists.
- **1998** Watts and Strogatz: small-world networks.
- **2016** HNSW (Malkov and Yashunin).
- **2023** HNSW in pgvector.
:::

This is the psychologist whose letters showed that a few hops connect strangers. HNSW's search works on the same idea:
a few long links on the upper layers mean any vector is only a few hops away.

:::photo{src="/lesson-images/rag/milgram.webp" alt="A black and white portrait of Stanley Milgram, a man with a beard, speaking" credit="Unknown author" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AStanley_Milgram_1974.jpg"}
Stanley Milgram, around 1974.
:::
:::

:::step{type=concept title="Tuning by measurement" file="06-hnsw/fieldbook.py" line="214-219"}
"Which efSearch should I use?" has one honest answer: **the smallest value that reaches the recall your application
needs, measured on questions like yours.** A smaller efSearch is faster, so you try values from small to large and stop
at the first one that is good enough.

Here is that search with this chapter's real numbers and a target of 95% recall:

```text
target 0.95:   efSearch 16 -> 0.877 (no)   32 -> 0.949 (no)   64 -> 0.989 (yes: the answer is 64)
```

Notice 32 misses by a hair (94.9%). A target is a target: 64 is the answer.

In code, `index.search(queries, k)` searches all the questions at once and returns two arrays, one row per question:
the scores, and the ids found. Recall needs only the ids, so you can write `_, found = index.search(queries, k)` (the
`_` is Python's usual name for a value you do not need).
:::

:::step{type=task task=tune_ef title="Your turn: the smallest efSearch that is good enough" file="06-hnsw/fieldbook.py" line="214-219"}
Write `smallest_ef(index, queries, truth, k=10, target=0.95, choices=(...))` in `06-hnsw/fieldbook.py`. For each value
in `choices`, in order:

1. set `index.hnsw.efSearch` to it;
2. search: `_, found = index.search(queries, k)`;
3. measure `recall_at_k(found, truth)`;
4. if the recall is at least the target, return this value.

If no value reaches the target, return `None`. The usual slip: returning the value with the best recall instead of the
first one that is good enough. Larger values cost more time, so "good enough and smallest" is the goal.

Then run the benchmark:

```bash run
cd /workspace/06-hnsw && python hnsw_bench.py
```

Press **Check**.
:::

:::step{type=try title="HNSW against brute force"}
`hnsw_bench.py` builds an HNSW graph over 100,000 vectors and asks 200 questions. As in chapter 5, these are
**synthetic** vectors from `fake_embeddings`, so read the results as the shape of the trade, not as fixed values. Both
searches use FAISS on **one** processor thread, so the comparison is fair. The timings were measured on the lab machine
this lesson was written on:

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

| | Recall | Time a query | Extra memory | Build time |
|---|---|---|---|---|
| brute force (FAISS) | 100% | 6.57 ms | none | none |
| **HNSW, efSearch 64** | **98.9%** | **0.188 ms** | 27 MB of links | 18.2 s |

At efSearch 64, HNSW finds 98.9% of the true neighbours **35 times faster** than brute force (6.57 / 0.188). That is
why it is so widely used. The prices are in the other two columns:

1. **Memory.** The links take 27 MB on top of the 154 MB of vectors (181 minus 154). With `M = 32`, each node on the
   bottom layer has up to 64 links of 4 bytes each, and the whole graph must stay in memory to be fast.
2. **Build time.** 18 seconds for 100,000 vectors on one thread. Every new vector has to find its neighbours in the
   graph, so loading millions of vectors takes a while.

(Chapter 5's IVF took 2.6 s to train and 1.10 ms a query at 92% recall, but that was the Python version, so its time is
not directly comparable with FAISS's C++ here.)

And the dial: from efSearch 16 to 256, recall goes from 87.7% to 100% while the time grows about tenfold. With a target
of 95%, `smallest_ef` picks 64.
:::

:::step{type=predict title="Guess first"}
:::question
After building the index, you raise efSearch from 64 to 128. Do you need to rebuild?
:::
- [ ] Yes, the graph depends on efSearch
- [x] No: efSearch only changes how many candidates a query keeps; M and efConstruction are the build settings
- [ ] Only if recall gets worse
:::explain
That is what makes efSearch the everyday dial: one query can use 32, another 256, on the same graph.
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
Each hop costs a handful of dot products, and the layers keep the number of hops small.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Your application needs a recall of at least 99%. From the table above, which efSearch would you start with?
:::
- [ ] 64
- [x] 128: the smallest that reaches 99% (99.8%)
- [ ] 256, to be safe
:::explain
64 gives 98.9%, just short. 256 also passes, but costs almost twice as much time as 128 for 0.2% more recall. (On your
own data, measure again: these numbers are for this chapter's synthetic vectors.)
:::
:::

:::step{type=deep-dive title="Go deeper: HNSW in production"}
**Memory is the limit.** HNSW wants everything in memory. For 100 million vectors of 384 numbers, that is about 154 GB
of vectors plus the links. Chapter 7's smaller vectors are how real systems fit.

**Deletes and updates** are hard in a graph: most databases mark deleted nodes and clean them up later, and heavy
changes slowly lower recall until the index is rebuilt.

**Filters** (chapter 8) interact badly with graphs: if most nodes are filtered out, the walk runs out of allowed
neighbours. Databases handle it in their own ways: Qdrant adds extra links for filtered fields, and pgvector 0.8 added
iterative index scans.

**Benchmarks.** ann-benchmarks.com compares HNSW, IVF and dozens of other indexes on public datasets, using this
chapter's two measures: recall, and queries per second.
:::

:::step{type=recap}
You can now:

- explain how HNSW searches: greedy walks on a layered graph of neighbours;
- measure recall at k against brute force;
- tune efSearch by measurement, choosing the smallest value that meets a target;
- weigh HNSW's speed against its memory and build time.

Next, chapter 7: shrinking the vectors themselves.

:::photo{src="/lesson-images/rag/rag-06-notes.webp" alt="Handwritten notes about HNSW: HNSW links every vector to its near neighbours. A search walks the links towards the question. Upper layers take long hops, the bottom layer short ones. efSearch trades recall for speed, per query. Pick the smallest efSearch that meets your target. The graph needs extra memory and build time." ai="true"}
One page of notes for this chapter.
:::
:::
