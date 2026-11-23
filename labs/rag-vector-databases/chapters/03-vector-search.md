:::step{type=story title="Thirty-one sections, one question"}
You can now turn any text into 384 numbers and compare two of them. Fieldbook needs one more thing: given a question,
find the closest sections **out of all of them**. With 31 sections you could call `cosine` 31 times in a loop. The
sanctuary also has patrol reports, and every year adds thousands more; other RAG systems search millions of passages.

This chapter does nearest-neighbour search the honest way, by checking every vector, which is called **brute force**
(or exact, or flat search). It is the answer every clever index is measured against, and, as you will see, it is much
faster than its name suggests, as long as you let NumPy do the work.

:::mission
Normalize vectors so that one matrix product scores a whole collection, find the k best rows without sorting them all,
then measure how the time grows from ten thousand to three hundred thousand vectors.
:::
:::

:::step{type=concept title="Length one: then the dot product is the cosine" file="03-vector-search/fieldbook.py" line="79-83"}
The cosine divides by both lengths every time. Do that division **once**, when the vector is stored: scale every vector
to length 1. After that,

```text
cosine(a, b) = dot(a, b) / (1 * 1) = dot(a, b)
```

Scaling a vector to length 1 is called **normalizing** it: divide every number by the vector's length.

```python
>>> normalize([3, 4])          # length 5
[0.6, 0.8]                     # length 1, same direction
```

For a matrix, each **row** needs its own length. `np.linalg.norm(m, axis=-1, keepdims=True)` gives one length per row,
shaped as a column, so that `m / lengths` divides row by row. The same line works for a single vector, because for a
vector the last axis is the only one.
:::

:::step{type=task task=normalize title="Your turn: vectors of length one" file="03-vector-search/fieldbook.py" line="79-83"}
Write `normalize(m)`: turn `m` into a float32 array (`np.asarray(m, dtype=np.float32)`) and divide it by
`np.linalg.norm(m, axis=-1, keepdims=True)`. Return the result.

Careful: `np.linalg.norm(m)` without `axis` gives **one** length for the whole matrix, and every row would be divided by
the same number. Press **Check**.
:::

:::step{type=concept title="Every row in one product, the best k without a full sort" file="03-vector-search/fieldbook.py" line="86-91"}
Put the 31 section vectors in a matrix, one row each. Multiply the matrix by the question's vector:

```text
matrix (31 x 384)  @  query (384)  =  scores (31)
```

Row 0 times the query is section 0's score, row 1 is section 1's, and so on: all 31 cosines in one line,
`scores = matrix @ query`. NumPy hands that to a BLAS library, which uses the CPU's vector instructions; it is hundreds of
times faster than a Python loop.

Then the k highest scores. Sorting all of them is wasteful when you want 3 out of 300,000. `np.argpartition(-scores, k - 1)`
moves the k best to the front, in no particular order, in time proportional to the number of rows; then sort just those k.

:::trace{title="top_k with k = 2 over five scores"}
| step | values | note |
|---|---|---|
| scores | [0.31, 0.77, 0.45, 0.80, 0.12] | one product, five cosines |
| argpartition(-scores, 1)[:2] | [3, 1] (any order) | the two best rows |
| sort those two by score | [3, 1] | 0.80 before 0.77 |
| result | [(3, 0.80), (1, 0.77)] | plain ints and floats |
:::
:::

:::step{type=task task=top_k title="Your turn: the k closest rows" file="03-vector-search/fieldbook.py" line="86-91"}
Write `top_k(query, matrix, k=3)`:

1. `scores = matrix @ query`.
2. Make `k` at most the number of rows.
3. Use `np.argpartition` on the negative scores to get the k best rows, then order those rows by their scores, best first.
4. Return a list of `(int(row), float(score))` pairs.

```bash run
cd /workspace/03-vector-search && python search.py
```

Press **Check**.
:::

:::step{type=try title="Big cat, found"}
```text
$ python search.py
Embedded 31 sections in 3.22 s: a 31 x 384 matrix

'What should I do if a big cat is right in front of me?' (87.8 ms, the question's embedding included)
  0.595  [FM-4.2] Meeting a tiger
  0.565  [FM-7.3] Finding a dead animal
  0.551  [FM-4.1] General rules for animal encounters
```

The question keyword search could not answer: **FM-4.2 Meeting a tiger** comes first, without a single shared word.
Notice how close the scores are (0.595, 0.565, 0.551): all three sections are about large animals, and the model is not
very sure which one is meant. Chapter 10 adds a second, more careful judge for exactly this.

A question in the manual's own words is easier:

```text
$ python search.py "Which gate sells safari permits?"
Embedded 31 sections in 3.17 s: a 31 x 384 matrix

'Which gate sells safari permits?' (4.1 ms, the question's embedding included)
  0.771  [FM-1.2] Gates and checkposts
  0.714  [FM-6.1] Safari timings and vehicles
  0.672  [FM-6.5] The monsoon closure
```

Time: embedding the 31 sections took about 3 seconds (loading the model included), done once. A question then takes
4.1 ms, almost all of it to embed the question; the search itself is a fraction of a millisecond. (The first question
took 87.8 ms because the model's first call warms up.)

No shared word, and still the right section: a big cat, to the model, is close to a tiger.

:::photo{src="/lesson-images/rag/tiger-resting.webp" alt="A Bengal tiger lying on the ground at the edge of a forest clearing" credit="Tisha Mukherjee" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ABengal_tiger_in_Sanjay_Dubri_Tiger_Reserve_December_2024_by_Tisha_Mukherjee_02.jpg"}
A Bengal tiger resting in Sanjay Dubri Tiger Reserve.
:::
:::

:::step{type=history title="Nearest neighbours and the curse of dimensionality"}
:::before{title="Rules written by hand"}
Early pattern recognition meant writing rules: if the petal is longer than this and wider than that, it is this flower.
Each new kind of data needed new rules.
:::

In **1951** Evelyn Fix and Joseph Hodges proposed simply looking at the closest known examples, and in **1967** Thomas
Cover and Peter Hart proved how good that **nearest-neighbour rule** is. It needs only a way to measure distance. The
catch was named by Richard Bellman in **1957**: the **curse of dimensionality**. In many dimensions, space is so vast that
clever shortcuts stop working, and points become almost equally far from each other; for decades, checking every point
was the only reliable way. Libraries for fast linear algebra (BLAS, from **1979**) made checking every point quick, and
chapters 5 and 6 show the shortcuts that finally beat it.

:::solved
**Exact search in one line.** With normalized vectors and a matrix product, brute force over hundreds of thousands of
vectors takes milliseconds, and it is never wrong.
:::

:::timeline
- **1951** Fix and Hodges: decide by the nearest examples.
- **1957** Bellman: the curse of dimensionality.
- **1967** Cover and Hart: the nearest-neighbour rule.
- **1979** BLAS: fast linear algebra, used by NumPy today.
:::
:::

:::step{type=example title="How far does brute force go?" file="03-vector-search/bench.py" line="1-17"}
The sanctuary will never have 300,000 documents, but plenty of RAG systems do. `bench.py` makes random vectors shaped
like real embeddings (`fake_embeddings`, grouped around topics, length 1) and times `top_k` on your two CPUs (your
numbers will differ a little; these are from the machine this lesson was written on):

```bash run
cd /workspace/03-vector-search && python bench.py
```

```text
$ python bench.py
   10,000 vectors     15.4 MB     0.15 ms a query
  100,000 vectors    153.6 MB     4.87 ms a query
  300,000 vectors    460.8 MB    15.02 ms a query
```

Three things to read here:

1. **Memory is easy to predict**: rows x 384 numbers x 4 bytes. 300,000 vectors are 460.8 MB, all of it in RAM.
2. **Time grows with the size**, about 5 ms per 100,000 vectors here. From 100,000 to 300,000 the time triples, as
   expected: every vector is read once per question.
3. **10,000 vectors are 30 times faster than 100,000, not 10.** 15 MB fit in the CPU's cache; 154 MB do not, so every
   question streams the whole matrix from main memory. Memory speed, not arithmetic, is the limit.

The arithmetic for a bigger system: 10 million vectors would need 15.4 GB of RAM and about half a second per question
on these two CPUs, about two questions a second. That is where indexes (chapters 5 and 6) and smaller vectors
(chapter 7) come in.
:::

:::step{type=predict title="Guess first"}
:::question
You forget to normalize the section vectors but keep using `matrix @ query`. What changes?
:::
- [ ] Nothing: the dot product is the cosine anyway
- [x] Longer vectors get higher scores whatever their direction, so the ranking can be wrong
- [ ] It raises an error
:::explain
The dot product is the cosine only for length-1 vectors. (BGE's vectors happen to come out with length 1 already, which
hides the bug until you switch models.)
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why use `argpartition` and not `argsort` for the top k?
:::
- [x] It finds the k best without fully sorting all rows, which matters with hundreds of thousands of rows
- [ ] argsort gives wrong answers
- [ ] argpartition returns the rows already sorted
:::explain
argpartition leaves the k best unsorted; you sort only those k afterwards.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Brute force over 100,000 vectors took 4.87 ms. Roughly how long for 1,000,000?
:::
- [ ] Still about 5 ms
- [x] About 50 ms: every question reads every vector, so the time grows with the count
- [ ] About 5 seconds
:::explain
Linear growth: ten times the vectors, about ten times the time (once the data no longer fits in the CPU's cache).
:::
:::

:::step{type=deep-dive title="Go deeper: when brute force is the right answer"}
**Up to about 100,000 vectors, brute force is often the best choice.** It is exact, has no index to build or tune, and
answers in a few milliseconds. Many production systems that search one customer's documents at a time never need more.

**Batching.** Ten questions at once are one matrix-matrix product (`matrix @ queries.T`), which uses the CPU far better
than ten separate products.

**FAISS's `IndexFlatIP`** is this chapter's search, written in C++ with careful use of the CPU: chapter 6 uses it as the
"true answer" for measuring recall.

**GPUs** do brute force over millions of vectors in milliseconds; for very large collections, a GPU and brute force can
beat a CPU and an index.
:::

:::step{type=recap}
You can now:

- normalize vectors so that a dot product is the cosine;
- score a whole collection with one matrix product and take the top k with argpartition;
- search the manual by meaning, and see "big cat" find the tiger section;
- predict brute force's memory and time from the number of vectors, and explain the cache effect.

Next, chapter 4: how to cut documents into the pieces you embed.

:::photo{src="/lesson-images/rag/rag-03-notes.webp" alt="Handwritten notes about brute-force search: Normalize once, then dot = cosine; One matrix product scores all; argpartition for the top k; Time grows with the count; Exact: the answer key" ai="true"}
One page of notes for this chapter.
:::
:::
