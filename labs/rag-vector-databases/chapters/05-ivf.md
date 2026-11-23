:::step{type=story title="Do not read every shelf"}
Brute force reads every vector for every question. At 100,000 vectors that took about 5 ms; at 10 million it would take
half a second and 15 GB of memory. Every vector database exists to avoid that, and they all do it the same basic way:
**don't look everywhere, look where the answer probably is**.

Think of how the sanctuary's control room files its camera trap images: not in one heap, but in a folder per beat. To find
images of the Kolhi stream, you open the folder for beat B-03 and maybe the beats next to it, not all twelve. The price:
if an image was filed in a beat you did not open, you miss it.

That trade, a little accuracy for a lot of speed, is called **approximate nearest neighbour search** (ANN). This chapter
builds the oldest and simplest ANN index, the **inverted file**, or **IVF**, the one FAISS, Milvus and pgvector all offer.

:::mission
File 100,000 vectors under 316 cluster centres, search only the closest few lists, and measure how much of the true
answer you keep at each speed.
:::
:::

:::step{type=concept title="Step 1: cluster centres with k-means" file="05-ivf/fieldbook.py" line="156-168"}
First, find a few hundred points that sit in the middle of groups of vectors. These are the **centroids**, and k-means
finds them (it is written for you in `train_centroids`):

1. Pick n_lists random vectors as the first centroids.
2. Give every vector to its nearest centroid (the highest dot product).
3. Move each centroid to the average of its vectors (and normalize it).
4. Repeat steps 2 and 3 a few times (8 here); the centroids settle into the middles of the groups.

Every centroid now owns a region of the space: the points closer to it than to any other centroid. Those regions are
called **Voronoi cells**.

How many lists? A common starting rule is about the square root of the number of vectors: for 100,000, about 316 lists of
about 316 vectors each.
:::

:::step{type=concept title="Step 2: the inverted lists" file="05-ivf/fieldbook.py" line="171-176"}
Now file every vector under its nearest centroid. The result is one list of row numbers per centroid, the **inverted
lists** (the name comes from search engines, where an inverted list maps a word to the documents that contain it):

```text
list 0   -> rows [12, 907, 4410, ...]     every vector whose nearest centroid is 0
list 1   -> rows [3, 88, 1290, ...]
...
list 315 -> rows [...]
```

All at once with NumPy:

```python
nearest = np.argmax(vectors @ centroids.T, axis=1)   # for each vector, the number of its best centroid
lists = [np.flatnonzero(nearest == c) for c in range(len(centroids))]
```

`vectors @ centroids.T` is a 100,000 x 316 table of scores; `argmax(axis=1)` picks the best column in every row;
`np.flatnonzero(nearest == c)` gives the row numbers filed under centroid c.

A card catalogue is an inverted file made of wood: every drawer holds the cards for one stretch of the alphabet, so you open one drawer, not all of them.

:::photo{src="/lesson-images/rag/catalogue-drawers.webp" alt="A wooden chest of many small card catalogue drawers, each with a brass handle and a label holder" credit="MarkBuckawicki" license="CC0" source="https://commons.wikimedia.org/wiki/File%3AWooden_Card_Catalog_Furniture.jpg"}
A card catalogue at a public library in Nashua, New Hampshire.
:::
:::

:::step{type=task task=build_lists title="Your turn: the inverted lists" file="05-ivf/fieldbook.py" line="171-176"}
Write `build_lists(vectors, centroids)`: find each vector's nearest centroid with one matrix product and `np.argmax`
along each row, then return a list with one array of row numbers per centroid, in centroid order.

Every vector must appear in exactly one list. Press **Check**.
:::

:::step{type=concept title="Step 3: search only the nearest lists" file="05-ivf/fieldbook.py" line="179-184"}
For a question:

1. Score the query against the 316 **centroids** (316 dot products instead of 100,000).
2. Take the `nprobe` best centroids.
3. Gather the rows in their lists: the **candidates**.
4. Score only the candidates exactly, and keep the k best.

:::diagram{name="rag-ivf"}
The query is compared with the centroids, then only the vectors in the closest lists are scored.
:::

`nprobe` is the dial. With `nprobe=1` you search about 0.3% of the vectors and may miss neighbours that sit just across a
border, in the next cell. With `nprobe` equal to the number of lists you search everything and get the brute-force answer.

One detail: the candidates are rows of the full matrix (like 4410), but after `scores = vectors[candidates] @ query` the
positions in `scores` are 0, 1, 2, ... So translate back: the row for position `i` is `candidates[i]`.
:::

:::step{type=task task=ivf_search title="Your turn: search only the nearest lists" file="05-ivf/fieldbook.py" line="179-184"}
Write `ivf_search(query, vectors, centroids, lists, k=10, nprobe=4)`:

1. Rank the centroids by `centroids @ query` and take the best `nprobe` of them.
2. `np.concatenate` their lists into one array of candidate rows (return `[]` if it is empty).
3. Score the candidates, take the k best, and return `(int(candidates[i]), float(scores[i]))` pairs, best first.

```bash run
cd /workspace/05-ivf && python ivf_bench.py
```

Press **Check**.
:::

:::step{type=history title="Cells, centres and inverted files"}
:::before{title="Look everywhere"}
Before indexes for vectors, finding the nearest of a million points meant computing a million distances, every time.
:::

The geometry is old: in **1908** the mathematician Georgy Voronoi studied how space divides into cells around a set of
points, each cell holding the places closer to its point than to any other. Stuart Lloyd at Bell Labs described the
k-means procedure in **1957** (published only in **1982**), and James MacQueen gave it its name in **1967**. The
**inverted file** is the classic data structure of text search engines, mapping each word to the documents that contain
it. In **2003** Josef Sivic and Andrew Zisserman used clusters of image features as "visual words" in an inverted file to
search video frames; Hervé Jégou, Matthijs Douze and Cordelia Schmid made the inverted file with compressed vectors the
standard for billion-scale search in **2011**, and their work became **FAISS** at Facebook in **2017**.

:::solved
**Search a fraction, keep most of the answer.** A few hundred centroid comparisons decide where to look; the rest of the
collection is never touched.
:::

:::timeline
- **1908** Voronoi cells.
- **1957** Lloyd's k-means (published 1982).
- **2003** Inverted files for images ("Video Google").
- **2011** IVF with compressed vectors for billions of vectors.
- **2017** FAISS released.
:::
:::

:::step{type=try title="Recall against speed"}
`ivf_bench.py` builds IVF over 100,000 vectors and asks 50 questions. To judge an approximate index, you compare it with
the exact answer from brute force. The measure is **recall**: of the true 10 nearest neighbours, how many did the index
return? 9 of 10 is a recall of 90%.

```text
$ python ivf_bench.py
brute force: recall 100%, 4.93 ms a query

trained 316 lists in 2.6 s; sizes from 155 to 483

nprobe   1: recall   52%,   0.09 ms a query, searches  0.3% of the lists
nprobe   4: recall   74%,   0.25 ms a query, searches  1.3% of the lists
nprobe  16: recall   92%,   1.10 ms a query, searches  5.1% of the lists
nprobe  64: recall  100%,   5.93 ms a query, searches 20.3% of the lists
```

Read it as a trade:

| nprobe | Recall | Time | Compared with brute force |
|---|---|---|---|
| 1 | 52% | 0.09 ms | 55 times faster, but half the true neighbours missed |
| 4 | 74% | 0.25 ms | 20 times faster |
| 16 | **92%** | **1.10 ms** | 4.5 times faster, 9 of 10 true neighbours |
| 64 | 100% | 5.93 ms | **slower** than brute force |

Two surprises worth remembering:

1. **Searching 0.3% of the data still finds half the right answers.** Nearest neighbours mostly live in the same cell.
2. **At nprobe 64, IVF is slower than brute force** while reading only a fifth of the vectors. Gathering 20,000 scattered
   rows from 64 lists costs more than streaming one contiguous matrix. In Python with NumPy, this index only pays off at
   small nprobe; FAISS's C++ version avoids the copying.

The training took 2.6 seconds, and it is not free in another way either: when many new vectors arrive that look different
from the old ones, the centroids no longer fit, the lists become unequal, and the index has to be trained again.
:::

:::step{type=predict title="Guess first"}
:::question
You double the number of lists to 632 and keep nprobe at 16. What happens to recall and speed?
:::
- [x] Faster (each list is half as long) but lower recall (16 lists now cover half as much of the space)
- [ ] Slower and higher recall
- [ ] No change: nprobe decides everything
:::explain
More, smaller cells make each probe cheaper and each border closer. Recall depends on the share of the space you search,
so with more lists you need a larger nprobe for the same recall. Measured on the same data: 632 lists at nprobe 16 took
0.51 ms (from 1.10) for a recall of 90% (from 92%).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does IVF miss some true neighbours at small nprobe?
:::
- [ ] k-means is random
- [x] A neighbour can sit just across a cell border, in a list that was not probed
- [ ] The candidates are scored approximately
:::explain
Candidates are scored exactly; what is approximate is which candidates you look at.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does a recall of 92% at k = 10 mean?
:::
- [ ] 92% of the questions were answered correctly
- [x] On average, 9.2 of the 10 true nearest neighbours were returned
- [ ] The search is 92% as fast as brute force
:::explain
Recall measures the index against brute force, not whether the answer helps the user (chapter 12 measures that).
:::
:::

:::step{type=deep-dive title="Go deeper: IVF in real systems"}
**pgvector's `ivfflat`** is this chapter's index inside Postgres: `lists` at creation time, `ivfflat.probes` per query.
Its documentation suggests building the index **after** loading data, because the centroids are trained on what is there.

**FAISS** offers `IndexIVFFlat` and, for billions of vectors, `IndexIVFPQ`, which also compresses the vectors in each list
(chapter 7's idea).

**When to prefer IVF.** It uses little extra memory (just the centroids and the lists) and builds fast. HNSW (chapter 6) is
usually faster for the same recall but needs much more memory and longer builds. Many systems with very large
collections still use IVF for that reason.
:::

:::step{type=recap}
You can now:

- explain approximate nearest neighbour search: a little recall for a lot of speed;
- find centroids with k-means and file every vector in an inverted list;
- search only the nprobe nearest lists and translate candidate positions back to rows;
- measure recall against brute force and read the speed and recall trade.

Next, chapter 6: HNSW, the graph index most vector databases use by default.

:::photo{src="/lesson-images/rag/rag-05-notes.webp" alt="Handwritten notes about IVF: k-means finds the centres; Every vector in its nearest list; Search only nprobe lists; Recall: share of the true neighbours; nprobe trades recall for speed" ai="true"}
One page of notes for this chapter.
:::
:::
