:::step{type=story title="Thirty-one sections, one question"}
In chapter 2 you turned text into vectors (lists of 384 numbers, with this course's model) and compared two of them with
cosine similarity. Fieldbook needs one more thing: given a ranger's question, find the closest sections **out of all of
them**.

With 31 sections you could simply call `cosine` 31 times in a loop and keep the best. But the sanctuary also has patrol
reports, and every year adds thousands more; other RAG systems search millions of passages. So this chapter does the
search properly, and measures how far it goes.

Finding the vectors closest to a query vector is called **nearest-neighbour search**. This chapter does it the
straightforward way: score **every** vector and keep the best ones. That is called **brute force** (also **exact** or
**flat** search). It is never wrong, which is why every faster method in later chapters is measured against it. And, as
you will see, it is much faster than its name suggests, as long as NumPy does the work.

:::mission
Normalize vectors so that one matrix product scores a whole collection, find the k best rows without sorting them all,
then measure how the time grows from ten thousand to three hundred thousand vectors.
:::
:::

:::step{type=concept title="Length one: then the dot product is the cosine" file="03-vector-search/fieldbook.py" line="79-83"}
Remember the cosine from chapter 2:

```text
cosine(a, b) = dot(a, b) / (length(a) * length(b))
```

To compare one question with 300,000 sections, you would compute 300,000 dot products **and** divide by 600,000
lengths. The divisions are wasted work, because a section's length never changes. So do that division **once**, when
the vector is stored: scale every vector so that its length is exactly 1. After that, every length is 1 and the formula
shrinks to:

```text
cosine(a, b) = dot(a, b) / (1 * 1) = dot(a, b)
```

Scaling a vector to length 1 is called **normalizing** it. You do it by dividing every number by the vector's length.
The direction stays the same, and only the direction carries the meaning:

```python
>>> normalize([3, 4])          # length 5 (the square root of 3*3 + 4*4)
[0.6, 0.8]                     # each number divided by 5: now length 1, same direction
```

Here is the function in `03-vector-search/fieldbook.py`, line by line:

```python
def normalize(m):
    m = np.asarray(m, dtype=np.float32)
    return m / np.linalg.norm(m, axis=-1, keepdims=True)
```

- `np.asarray(m, dtype=np.float32)` makes sure `m` is a NumPy array of `float32` numbers, whether you pass a list, one
  vector or a whole matrix.
- `np.linalg.norm(m, axis=-1, ...)` computes lengths. `axis=-1` means "along the last direction of the array": for a
  matrix, along each **row**, so you get one length per row (one per section). For a single vector, the last direction
  is the only one, so you get its one length.
- `keepdims=True` keeps those lengths shaped as a column (31 rows, 1 column) instead of a flat list. That shape is what
  lets `m / lengths` divide **each row by its own length**: NumPy lines the column up against the rows.

A fact you can check later in this chapter: the model in this course, bge-small, already returns vectors of length 1.
Other models do not always, so Fieldbook normalizes anyway; it costs almost nothing and protects you when you change
models.
:::

:::step{type=task task=normalize title="Your turn: vectors of length one" file="03-vector-search/fieldbook.py" line="79-83"}
Write `normalize(m)` in `03-vector-search/fieldbook.py`:

1. turn `m` into a `float32` array with `np.asarray(m, dtype=np.float32)`;
2. compute one length per row with `np.linalg.norm(m, axis=-1, keepdims=True)`;
3. return `m` divided by those lengths.

The usual slip: `np.linalg.norm(m)` **without** `axis` gives **one** length for the whole matrix, so every row would be
divided by the same number and almost none of them would end up with length 1. If the check says your rows do not have
length 1, look for the missing `axis=-1`.

Press **Check**.
:::

:::step{type=concept title="Every row in one product, the best k without a full sort" file="03-vector-search/fieldbook.py" line="86-91"}
Now the search itself. Put all 31 normalized section vectors in one **matrix**: a table with one row per section and 384
columns. Then multiply the matrix by the normalized question vector:

```text
matrix (31 rows x 384 columns)  @  question (384 numbers)  =  scores (31 numbers)
```

`@` is Python's operator for this **matrix product**. It takes each row, computes its dot product with the question,
and puts the result in the same position: score 0 belongs to section 0, score 1 to section 1, and so on. Because all the
vectors have length 1, each of those dot products **is** the cosine. So one line, `scores = matrix @ question`, gives
the cosine of the question with every section.

The picture shows it for the question "What should I do if a big cat is right in front of me?" with five of the 31 rows
and their real scores:

:::diagram{name="rag-matrix"}
One matrix product gives every section's score; `top_k` keeps the three highest. Real scores from this chapter's run.
:::

Why is this fast? NumPy does not loop in Python. It hands the whole product to a **BLAS** library (Basic Linear Algebra
Subprograms), compiled code that uses the processor's instructions for doing many multiplications at once. That is far
faster than calling `cosine` in a Python loop.

**Then the k highest scores.** The obvious way is to sort all the scores and take the first k. But sorting 300,000
scores to keep 3 is wasted work. NumPy has a cheaper tool, `np.argpartition`:

- `np.argpartition(-scores, k - 1)` returns the row numbers rearranged so that the k best come first, in no particular
  order among themselves. It does not sort the rest. (The minus sign turns "highest score" into "lowest number", which is
  what `argpartition` puts first.)
- Then you sort only those k rows by their scores. Sorting 3 numbers costs nothing.

Here it is with five real scores from the big cat question and k = 2:

:::trace{title="top_k with k = 2 over five real scores"}
| step | values | note |
|---|---|---|
| scores (rows 0 to 4) | [0.411, 0.436, 0.551, 0.595, 0.565] | FM-1.1, FM-2.2, FM-4.1, FM-4.2, FM-7.3 |
| argpartition(-scores, 1)[:2] | rows 3 and 4, in any order | the two best, not sorted |
| sort those two by score | [3, 4] | 0.595 before 0.565 |
| result | [(3, 0.595), (4, 0.565)] | plain Python ints and floats |
:::
:::

:::step{type=task task=top_k title="Your turn: the k closest rows" file="03-vector-search/fieldbook.py" line="86-91"}
Write `top_k(query, matrix, k=3)` in `03-vector-search/fieldbook.py`:

1. `scores = matrix @ query`: one score per row.
2. Make `k` at most the number of rows (`min(k, len(scores))`), so asking for 3 from a 2-row matrix does not fail.
3. Find the k best rows with `np.argpartition(-scores, k - 1)[:k]`.
4. Put those rows in order, best first: `np.argsort(-scores[best])` gives the order, so `best[...]` with it.
5. Return a list of `(row, score)` pairs as plain Python values: `(int(row), float(scores[row]))`.

The usual slips: forgetting the minus sign (you get the k **worst** rows), or returning NumPy numbers instead of
`int` and `float`.

Then run the search:

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

This is the question keyword search could not answer in chapter 1. Now **FM-4.2 Meeting a tiger** comes first, without
a single shared word.

Look at how close the three scores are: 0.595, 0.565, 0.551. All three sections are about large animals, so the model
places them near the question and only slightly apart. Search by meaning found the right neighbourhood, but it is not
very sure which section is meant. Chapter 10 adds a second, more careful judge for exactly this.

A question in the manual's own words is easier:

```text
$ python search.py "Which gate sells safari permits?"
Embedded 31 sections in 3.17 s: a 31 x 384 matrix

'Which gate sells safari permits?' (4.1 ms, the question's embedding included)
  0.771  [FM-1.2] Gates and checkposts
  0.714  [FM-6.1] Safari timings and vehicles
  0.672  [FM-6.5] The monsoon closure
```

Now the time, measured on the lab machine this lesson was written on (yours will differ a little):

- **Embedding the 31 sections took about 3 seconds**, loading the model included. You do that once, not per question.
- **A question then took 4.1 ms**, and almost all of it is embedding the question. The search itself, one matrix
  product over 31 rows, is a tiny fraction of a millisecond.
- **The first question took 87.8 ms** because the model's first call does extra start-up work. Later questions are
  fast.

The tiger in this photo is the animal FM-4.2 is about. A ranger who says "big cat" means this animal, and now Fieldbook
finds the right section anyway, because the model places "big cat" close to "tiger".

:::photo{src="/lesson-images/rag/tiger-resting.webp" alt="A Bengal tiger lying on the ground at the edge of a forest clearing" credit="Tisha Mukherjee" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ABengal_tiger_in_Sanjay_Dubri_Tiger_Reserve_December_2024_by_Tisha_Mukherjee_02.jpg"}
A Bengal tiger resting in Sanjay Dubri Tiger Reserve.
:::
:::

:::step{type=history title="Nearest neighbours and the curse of dimensionality"}
:::before{title="Rules written by hand"}
Early pattern recognition meant writing rules by hand: if the petal is longer than this and wider than that, it is this
flower. Every new kind of data needed new rules.
:::

In **1951** Evelyn Fix and Joseph Hodges proposed something simpler: to decide what a new example is, look at the known
examples **closest** to it. In **1967** Thomas Cover and Peter Hart proved how good this **nearest-neighbour rule** is.
It needs only one thing: a way to measure how close two examples are, like the cosine you use.

The catch was named by Richard Bellman in **1957**: the **curse of dimensionality**. When every point has many numbers
(you have 384), the space is so large that clever shortcuts for finding near points stop working well. For random
data it is even worse: almost every point ends up nearly the same distance from every other. (Real embeddings are
friendlier than random data, which is why the shortcuts in chapters 5 and 6 work at all.) So for decades, checking every
point was the only reliable method. Fast libraries for linear algebra, starting with BLAS in **1979**, made checking
every point quick, and NumPy still uses one today.

:::solved
**Exact search in one line.** With normalized vectors and one matrix product, brute force over hundreds of thousands
of vectors takes milliseconds, and it is never wrong.
:::

:::timeline
- **1951** Fix and Hodges: decide by the nearest examples.
- **1957** Bellman: the curse of dimensionality.
- **1967** Cover and Hart: the nearest-neighbour rule.
- **1979** BLAS: fast linear algebra, used by NumPy today.
:::
:::

:::step{type=example title="How far does brute force go?" file="03-vector-search/bench.py" line="1-17"}
The sanctuary will never have 300,000 documents, but plenty of RAG systems do. So how far does brute force go?
`bench.py` measures it. It makes random vectors shaped like real embeddings (the `fake_embeddings` function: 384 numbers
each, grouped around 500 topics, length 1), then asks 20 random questions at each of three sizes and prints the average
time of `top_k` (k = 10) per question:

```bash run
cd /workspace/03-vector-search && python bench.py
```

```text
$ python bench.py
   10,000 vectors     15.4 MB     0.15 ms a query
  100,000 vectors    153.6 MB     4.87 ms a query
  300,000 vectors    460.8 MB    15.02 ms a query
```

These numbers were measured on the lab machine this lesson was written on, with two processor cores. Yours will differ,
but the pattern will be the same. Three things to read here:

1. **Memory is easy to predict**: rows times 384 numbers times 4 bytes each. 300,000 x 384 x 4 = 460.8 million bytes,
   about 460.8 MB, all of it in memory (RAM).
2. **Time grows with the number of vectors.** From 100,000 to 300,000 vectors the time triples (4.87 ms to 15.02 ms),
   because every question reads every vector once. On this machine that is about 5 ms per 100,000 vectors.
3. **10,000 vectors were 30 times faster than 100,000, not 10 times.** The likely reason: 15 MB of vectors fit in the
   processor's own fast memory (its **cache**), while 154 MB do not, so at that size every question has to fetch the
   whole matrix from the slower main memory. Past that point, memory speed, not arithmetic, sets the time.

Now the arithmetic for a bigger system, using this machine's rate: 10 million vectors would need 15.4 GB of RAM (10
million x 384 x 4 bytes) and about half a second per question, so about two questions a second. That is where indexes
(chapters 5 and 6) and smaller vectors (chapter 7) come in.
:::

:::step{type=predict title="Guess first"}
:::question
You forget to normalize the section vectors but keep using `matrix @ query`. What changes?
:::
- [ ] Nothing: the dot product is the cosine anyway
- [x] Longer vectors get higher scores whatever their direction, so the ranking can be wrong
- [ ] It raises an error
:::explain
The dot product equals the cosine only for vectors of length 1. With this course's model the bug would stay hidden,
because bge-small happens to return vectors of length 1 already; switch to a model that does not, and the ranking quietly
goes wrong.
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
`argsort` would give the same answer, but it sorts every row. `argpartition` only moves the k best to the front
(unsorted), and you sort just those k afterwards.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
On the machine above, brute force over 100,000 vectors took 4.87 ms a question. Roughly how long would 1,000,000 take
on the same machine?
:::
- [ ] Still about 5 ms
- [x] About 50 ms: every question reads every vector, so the time grows with the count
- [ ] About 5 seconds
:::explain
The time grows in proportion to the number of vectors once they no longer fit in the processor's cache: ten times the
vectors, about ten times the time.
:::
:::

:::step{type=deep-dive title="Go deeper: when brute force is the right answer"}
**Up to about 100,000 vectors, brute force is often the best choice.** It is exact, has no index to build or tune, and
answers in a few milliseconds on an ordinary machine. Many production systems that search one customer's documents at a
time never need more.

**Batching.** Ten questions at once can be one matrix-by-matrix product (`matrix @ queries.T`), which keeps the
processor much busier than ten separate products.

**FAISS's `IndexFlatIP`** does this chapter's search (the name means: flat, by inner product, which is the dot product),
written in C++ and tuned for the processor. Chapter 6 uses it as the "true answer" when measuring how accurate faster
indexes are.

**GPUs** can run brute force over millions of vectors in a few milliseconds; for very large collections, a GPU with
brute force can beat a processor with an index.
:::

:::step{type=recap}
You can now:

- normalize vectors (scale them to length 1) so that a dot product is the cosine;
- score a whole collection with one matrix product, and take the top k with `argpartition`;
- search the manual by meaning, and see "big cat" find the tiger section;
- predict brute force's memory from the number of vectors, and read how its time grows on a real machine.

Next, chapter 4: how to cut documents into the pieces you embed.

:::photo{src="/lesson-images/rag/rag-03-notes.webp" alt="Handwritten notes about brute-force search: Normalize once: then the dot product is the cosine. One matrix product scores every section. argpartition finds the best k without a full sort. Brute force checks every vector, so it is never wrong. Its time grows with the number of vectors. Memory: rows x dimension x 4 bytes." ai="true"}
One page of notes for this chapter.
:::
:::
