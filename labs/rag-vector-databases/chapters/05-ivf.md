:::step{type=story title="Do not read every shelf"}
Brute force reads every vector for every question. In chapter 3 that took about 5 ms for 100,000 vectors on the lab
machine, and at 10 million it would take about half a second and 15 GB of memory. Every vector database exists to avoid
that, and they all start from the same idea: **don't look everywhere; look where the answer probably is.**

The sanctuary's control room already works this way with its camera trap photos: they are filed in one folder per beat,
not in one heap, so to find photos of one stream you open that beat's folder and perhaps its neighbours. The price is the
same as in search: a photo filed in a folder you did not open is missed.

Giving up a little accuracy for a lot of speed has a name: **approximate nearest neighbour search**, or **ANN**. "Approximate"
means the result can miss a few of the true nearest vectors. This chapter builds the oldest and simplest ANN index, the
**inverted file**, or **IVF**. FAISS, Milvus and pgvector all offer it.

:::mission
File 100,000 vectors under 316 cluster centres, search only the closest few lists, and measure how much of the true
answer you keep at each speed.
:::
:::

:::step{type=concept title="Step 1: cluster centres with k-means" file="05-ivf/fieldbook.py" line="156-168"}
IVF works in three steps. The first is to find a few hundred points that each sit in the middle of a group of similar
vectors. Each such point is called a **centroid** (a "centre point"), and a group of vectors around it is a **cluster**.

The classic way to find them is **k-means**. It is already written for you in `train_centroids`, and it repeats two
simple moves:

1. **Start:** pick `n_lists` vectors at random to be the first centroids.
2. **Assign:** give every vector to its nearest centroid, the one with the highest dot product.
3. **Move:** move each centroid to the average of the vectors assigned to it, then normalize it to length 1 again.
4. **Repeat** steps 2 and 3 a few times (8 times here). Each round, the centroids move closer to the true middles of
   their groups, and after a few rounds they barely move.

When it finishes, every centroid owns a region of the space: all the points closer to it than to any other centroid.
These regions are called **Voronoi cells**, after the mathematician who studied them (you will meet him in the history
step).

**How many lists?** There is no single right number; rules of thumb differ. A common starting point is the square root
of the number of vectors: for 100,000 vectors, √100,000 ≈ 316 lists, with about 316 vectors each on average. (pgvector's
documentation suggests the number of rows divided by 1,000 up to a million rows; FAISS's guide suggests several times
the square root for large collections.) This chapter uses 316.
:::

:::step{type=concept title="Step 2: the inverted lists" file="05-ivf/fieldbook.py" line="171-176"}
The second step files every vector under its nearest centroid. The result is one list per centroid, holding the row
numbers of the vectors in that centroid's cell:

```text
list 0   -> rows [12, 907, 4410, ...]     every vector whose nearest centroid is centroid 0
list 1   -> rows [3, 88, 1290, ...]
...
list 315 -> rows [...]
```

These are the **inverted lists**. The name comes from text search engines, where an inverted list maps each word to the
documents that contain it: the index is "inverted" because it goes from the content to where it is.

With NumPy, all the filing is two lines:

```python
nearest = np.argmax(vectors @ centroids.T, axis=1)
lists = [np.flatnonzero(nearest == c) for c in range(len(centroids))]
```

- `centroids.T` is the centroid matrix turned on its side (**transposed**), so that `vectors @ centroids.T` gives a table
  with one row per vector and one column per centroid: 100,000 rows by 316 columns, every vector's score against every
  centroid.
- `np.argmax(..., axis=1)` picks, in each row, the **column** with the highest score: the number of that vector's
  nearest centroid. `nearest` is one number per vector.
- `nearest == c` is True for the vectors whose nearest centroid is `c`, and `np.flatnonzero(...)` turns those True
  positions into row numbers: list `c`.

A library card catalogue is the same structure in wood: each drawer holds the cards for one part of the alphabet, so to
find a book you open one drawer instead of reading every card. An IVF list is one drawer.

:::photo{src="/lesson-images/rag/catalogue-drawers.webp" alt="A wooden chest of many small card catalogue drawers, each with a brass handle and a label holder" credit="MarkBuckawicki" license="CC0" source="https://commons.wikimedia.org/wiki/File%3AWooden_Card_Catalog_Furniture.jpg"}
A card catalogue at a public library in Nashua, New Hampshire.
:::
:::

:::step{type=task task=build_lists title="Your turn: the inverted lists" file="05-ivf/fieldbook.py" line="171-176"}
Write `build_lists(vectors, centroids)` in `05-ivf/fieldbook.py`:

1. compute every vector's nearest centroid with one matrix product, `vectors @ centroids.T`, and `np.argmax` along each
   row (`axis=1`);
2. for each centroid number `c`, from 0 to `len(centroids) - 1`, collect the rows whose nearest centroid is `c` with
   `np.flatnonzero(nearest == c)`;
3. return the list of those arrays, in centroid order.

Every vector must appear in exactly one list, so the list lengths add up to the number of vectors. The usual slip:
`axis=0` instead of `axis=1`, which picks the best vector for each centroid instead of the best centroid for each
vector.

Press **Check**.
:::

:::step{type=concept title="Step 3: search only the nearest lists" file="05-ivf/fieldbook.py" line="179-184"}
The third step is the search. For one question:

1. Score the question's vector against the 316 **centroids** only: 316 dot products instead of 100,000.
2. Keep the `nprobe` best centroids. `nprobe` ("number of probes") is how many lists you will open.
3. Gather the row numbers from those lists. These vectors are the **candidates**.
4. Score only the candidates, exactly, against the question, and keep the k best.

The picture shows it as a sketch in two dimensions (real vectors have 384, so this is only to see the idea), and below
it the real recall you will measure:

:::diagram{name="rag-ivf"}
Each cell holds the vectors nearest to its centroid. With nprobe 1, only the question's cell is searched, so a true
neighbour just across the border is missed. The numbers are this chapter's real benchmark.
:::

`nprobe` is the dial between speed and accuracy:

- With `nprobe=1` you open 1 of 316 lists, about 0.3% of them, so you score only a few hundred vectors. Fast, but any
  true neighbour that sits just across a border, in the next cell, is missed.
- Each extra probe opens one more nearby cell, so fewer neighbours are missed and more vectors are scored.
- With `nprobe` equal to the number of lists, you open every list and score every vector: the brute-force answer.

One detail to get right in code: the candidates are rows of the full matrix (like row 4410), but after
`scores = vectors[candidates] @ query`, the positions in `scores` are simply 0, 1, 2 and so on. So translate back: the
score at position `i` belongs to row `candidates[i]`.
:::

:::step{type=task task=ivf_search title="Your turn: search only the nearest lists" file="05-ivf/fieldbook.py" line="179-184"}
Write `ivf_search(query, vectors, centroids, lists, k=10, nprobe=4)` in `05-ivf/fieldbook.py`:

1. Score the centroids with `centroids @ query`, and take the numbers of the best `nprobe` of them
   (`np.argsort(-scores)[:nprobe]`).
2. Join their lists into one array of candidate rows with `np.concatenate`. If it is empty, return `[]`.
3. Score the candidates with `vectors[candidates] @ query`.
4. Take the k best positions, best first, and return `(int(candidates[i]), float(scores[i]))` pairs.

The usual slip is step 4: returning the position `i` instead of the row `candidates[i]`. The check catches it, because
the positions and the rows are different numbers.

Then measure it:

```bash run
cd /workspace/05-ivf && python ivf_bench.py
```

Press **Check**.
:::

:::step{type=history title="Cells, centres and inverted files"}
:::before{title="Look everywhere"}
Before indexes for vectors, finding the nearest of a million points meant computing a million distances, every time.
:::

The geometry is more than a century old. In **1908** the Ukrainian mathematician **Georgy Voronoy** published his study
of how space divides into cells around a set of points, each cell holding the places closer to its point than to any
other. Those are exactly the cells your k-means centroids make: every IVF list is the contents of one Voronoi cell.

Stuart Lloyd at Bell Labs described the k-means procedure in **1957**, though it was published only in **1982**, and
James MacQueen gave it its name in **1967**. The **inverted file** is the classic data structure of text search engines,
mapping each word to the documents that contain it. In **2003** Josef Sivic and Andrew Zisserman used clusters of image
features as "visual words" in an inverted file to search the frames of films ("Video Google"). In **2011** Hervé Jégou,
Matthijs Douze and Cordelia Schmid combined the inverted file with compressed vectors to search billions of vectors, and
their work grew into **FAISS**, which Facebook released in **2017**.

:::solved
**Search a fraction, keep most of the answer.** A few hundred centroid comparisons decide where to look; most of the
collection is never touched.
:::

:::timeline
- **1908** Voronoy's cells.
- **1957** Lloyd's k-means (published 1982).
- **2003** Inverted files for images ("Video Google").
- **2011** IVF with compressed vectors, for billions of vectors.
- **2017** FAISS released.
:::

This is the mathematician whose cells your index is built from. Every list you filed in the last task holds the vectors
of one of his cells.

:::photo{src="/lesson-images/rag/voronoy.webp" alt="Black and white portrait of Georgy Voronoy, a man with short hair, round glasses and a beard" credit="Unknown author" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AGeorgy_Voronoy.jpg"}
Georgy Voronoy (1868 to 1908).
:::
:::

:::step{type=try title="Recall against speed"}
`ivf_bench.py` builds IVF over 100,000 vectors and asks 50 questions. These are **synthetic** vectors from
`fake_embeddings` (the same generator as chapter 3's benchmark: grouped around topics, shaped like real embeddings),
because the sanctuary's own documents are far too few to need an index. Real data gives different numbers, so read the
results as the **shape** of the trade, not as fixed values.

To judge an approximate index, you compare it with the exact answer from brute force. The measure is **recall**: of the
true 10 nearest neighbours, what share did the index return? Returning 9 of the 10 is a recall of 90%.

```text
$ python ivf_bench.py
brute force: recall 100%, 4.93 ms a query

trained 316 lists in 2.6 s; sizes from 155 to 483

nprobe   1: recall   52%,   0.09 ms a query, searches  0.3% of the lists
nprobe   4: recall   74%,   0.25 ms a query, searches  1.3% of the lists
nprobe  16: recall   92%,   1.10 ms a query, searches  5.1% of the lists
nprobe  64: recall  100%,   5.93 ms a query, searches 20.3% of the lists
```

The script rounds recall to whole percents. Measured more precisely, nprobe 64 is **99.6%**: very close, but not
exactly the brute-force answer. The timings were measured on the lab machine this lesson was written on.

Read it as a trade:

| nprobe | Recall | Time | Compared with brute force (4.93 ms) |
|---|---|---|---|
| 1 | 52% | 0.09 ms | 55 times faster, but about half the true neighbours missed |
| 4 | 74% | 0.25 ms | 20 times faster |
| 16 | **92%** | **1.10 ms** | 4.5 times faster, about 9 of 10 true neighbours |
| 64 | 99.6% | 5.93 ms | **slower** than brute force |

Two surprises worth remembering:

1. **Opening 0.3% of the lists still finds half the right answers.** Nearest neighbours mostly live in the same cell as
   the question.
2. **At nprobe 64, IVF is slower than brute force**, while it scores only about a fifth of the vectors. Gathering
   about 20,000 scattered rows from 64 lists costs more than reading one matrix that sits in one piece of memory. In
   Python with NumPy, this index only pays off at small nprobe; FAISS's C++ version avoids the copying.

The list sizes (155 to 483 vectors) also show that k-means does not make equal groups: a list in a crowded region holds
three times as many vectors as one in a quiet region.

Training is not free either. It took 2.6 seconds here, and when many new vectors arrive that look different from the old
ones, the centroids no longer fit, the lists become uneven, and the index has to be trained again.
:::

:::step{type=predict title="Guess first"}
:::question
You double the number of lists to 632 and keep nprobe at 16. What happens to recall and speed?
:::
- [x] Faster (each list is about half as long) but lower recall (16 lists now cover about half as much of the space)
- [ ] Slower and higher recall
- [ ] No change: nprobe decides everything
:::explain
More, smaller cells make each probe cheaper, and put each question closer to a border. With more lists you need a
larger nprobe for the same recall. Measured on the same synthetic data: 632 lists at nprobe 16 took 0.5 ms (from 1.10)
for a recall of 90% (from 92%).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does IVF miss some true neighbours at small nprobe?
:::
- [ ] k-means is random
- [x] A neighbour can sit just across a cell border, in a list that was not opened
- [ ] The candidates are scored approximately
:::explain
The candidates are scored exactly. What is approximate is **which** vectors become candidates.
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
Recall measures the index against brute force, not whether the answer helps the user. Chapter 12 measures that.
:::
:::

:::step{type=deep-dive title="Go deeper: IVF in real systems"}
**pgvector's `ivfflat`** is this chapter's index inside Postgres: you choose `lists` when you create the index, and
`ivfflat.probes` (its nprobe) for each query. Its documentation suggests building the index **after** loading the data,
because the centroids are trained on whatever is in the table at that moment.

**FAISS** offers `IndexIVFFlat` and, for billions of vectors, `IndexIVFPQ`, which also compresses the vectors in each list
(chapter 7's idea).

**When to choose IVF.** It needs little extra memory (just the centroids and the lists) and builds quickly. HNSW (chapter
6) is usually faster at the same recall, but needs much more memory and takes longer to build. Many very large systems
use IVF for that reason.
:::

:::step{type=recap}
You can now:

- explain approximate nearest neighbour search: a little recall for a lot of speed;
- find centroids with k-means and file every vector in an inverted list;
- search only the nprobe nearest lists, and translate candidate positions back to rows;
- measure recall against brute force, and read the trade between speed and recall.

Next, chapter 6: HNSW, the graph index most vector databases use by default.

:::photo{src="/lesson-images/rag/rag-05-notes.webp" alt="Handwritten notes about IVF: IVF files every vector under its nearest centroid. A question searches only the nprobe closest lists. More probes: higher recall, slower search. Recall: the share of the true neighbours found. Misses happen just across a cell border. Measure recall on your own data." ai="true"}
One page of notes for this chapter.
:::
:::
