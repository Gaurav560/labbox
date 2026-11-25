:::step{type=story title="The memory bill"}
A computer stores each number of a vector as a **float32**: a number with a decimal point, kept in 32 bits. A **bit** is
a single 0 or 1, and 8 bits make a **byte**, so a float32 takes 4 bytes. Our model, bge-small, gives 384 numbers per
vector, so every vector so far has taken 384 x 4 = **1,536 bytes**. (Other models give other sizes; the arithmetic is
the same.)

For Fieldbook's 55 chunks that is nothing. But the same multiplication decides whether a large system fits on one server
or needs several:

| Vectors (384 numbers each) | Memory as float32 |
|---|---|
| 100,000 | 154 MB |
| 10 million | 15.4 GB |
| 100 million | 154 GB |

HNSW (chapter 6) is fastest when all of these vectors sit in **RAM**, the computer's working memory, and RAM is the
expensive part of a server. So vector databases do something that sounds wrong at first: they store the numbers **less
precisely**.

Why is that safe? A float32 can tell apart about 8 million different values between 1 and 2 (it has 23 bits for the
digits, and 2 to the power 23 is 8,388,608). To decide which of two vectors is closer to a question, you need far less
precision than that.

Storing numbers less precisely to save space is called **quantization**: every value is rounded to one of a small,
fixed set of levels. This chapter tries the two kinds that Qdrant, Weaviate, Elasticsearch and other vector databases
offer: **8 bits** per number instead of 32, and **1 bit** per number.

:::mission
Squeeze vectors into 8-bit whole numbers and measure what recall you lose, then reduce them to single bits, shortlist by
counting differing bits, and win the accuracy back by rescoring the shortlist with the full vectors.
:::
:::

:::step{type=concept title="int8: 255 levels instead of billions" file="07-quantization/fieldbook.py" line="224-235"}
**int8** is a whole number stored in one byte (8 bits). It can hold -128 to 127; we use -127 to 127, which is 255
levels. **Scalar quantization** turns every float into one of those levels. "Scalar" means each number is handled on its
own.

How a float becomes a level:

1. Look at one **column**: the same position (say, number 17) in every vector. A matrix of 100,000 vectors with 384
   numbers each has 384 columns.
2. Find the column's largest value, ignoring the sign. Divide it by 127. That is the column's **scale**: the size of one
   step between levels.
3. Divide every value in the column by the scale and round to the nearest whole number. That whole number is the
   **code** stored in one byte.
4. To get an approximate float back, multiply the code by the scale. That is `dequantize`.

A small column of three numbers, worked by hand:

:::trace{title="One column quantized (a toy column of three numbers)"}
| value | scale = 1.00 / 127 | value / scale | rounded int8 code | back: code x scale |
|---|---|---|---|---|
| 0.50 | 0.007874 | 63.5 | 64 | 0.5039 |
| -1.00 | 0.007874 | -127.0 | -127 | -1.0000 |
| 0.25 | 0.007874 | 31.75 | 32 | 0.2520 |
:::

The largest value in this column, ignoring its sign, is 1.00, so the scale is 1.00 / 127 = 0.007874. Rounding moves a
number by at most half a step, so every value comes back within 0.0039 of where it started. Each number now takes 1
byte instead of 4: a quarter of the memory. The scales add only one float per column (384 of them), which is nothing.

On real data the steps are much smaller. In this chapter's benchmark the largest value of a column is between 0.12 and
0.27, so one step is between 0.0009 and 0.0021, and we measured that every number comes back within 0.0011 of the
original.

The code, line by line:

```python
scales = np.abs(m).max(axis=0) / 127              # largest absolute value of each column, over 127
scales[scales == 0] = 1                           # a column of zeros would divide by 0: use scale 1
codes = np.round(m / scales).astype(np.int8)      # divide, round, store as one byte each
return codes, scales.astype(np.float32)
```

- `axis=0` means "down the rows", so the result has one value per column.
- Round **before** converting. `astype(np.int8)` on its own cuts off the fraction, so 63.5 would become 63 instead of
  64. (`np.round` sends an exact half to the nearest even number, so 62.5 becomes 62; either way the error stays within
  half a step.)
- A column that is all zeros has a largest value of 0. Dividing by 0 gives NaN ("not a number"), so give such a column
  the scale 1.

Qdrant's version stores the codes as 0 to 255 instead of -127 to 127. The idea is the same: one byte per number, a
quarter of the memory.
:::

:::step{type=task task=quantize_int8 title="Your turn: 8 bits instead of 32" file="07-quantization/fieldbook.py" line="224-230"}
Write `quantize_int8(m)`. `m` is a matrix with one vector per row.

1. `scales = np.abs(m).max(axis=0) / 127`: one scale per column. Then set any scale of 0 to 1.
2. `codes = np.round(m / scales).astype(np.int8)`.
3. Return `(codes, scales.astype(np.float32))`.

The usual slips:

- `max(axis=1)` gives one value per **row**, not per column.
- Forgetting `np.round`: the codes are then cut down, not rounded (63.5 becomes 63).
- Forgetting the all-zeros column: the check sends one, and dividing by 0 fills it with NaN.

Press **Check**.
:::

:::step{type=concept title="Binary: one bit per number, and a shortlist" file="07-quantization/fieldbook.py" line="238-253"}
Now go much further: keep only the **sign** of each number. A number above zero becomes 1, anything else becomes 0. So
384 numbers become 384 bits, which is **48 bytes**: 32 times smaller than the 1,536 bytes of float32.

`binary_codes` does this with `m > 0` (True or False for every number), and `np.packbits` packs every 8 of those into
one byte.

**Comparing two bit strings.** Line them up and count the positions where they differ. That count is the **Hamming
distance** (named after Richard Hamming, who used it for error-correcting codes in 1950). The smaller it is, the more
alike the two vectors. A computer finds it with **XOR**, an operation that gives 1 where two bits differ and 0 where
they match, then counts the ones:

```text
question bits   1 0 1 1 0 0 1 0
chunk bits      1 0 0 1 0 1 1 0
XOR             0 0 1 0 0 1 0 0    -> 2 bits differ: Hamming distance 2
```

`hamming` does exactly this for every row at once: `np.bitwise_xor` gives the differing bits, `np.unpackbits` turns the
bytes back into single bits, and `.sum(axis=1)` counts the ones in each row.

**Why bits alone are not enough.** One bit per number throws away almost everything except the direction of each
number. The bits give a **rough** order: true neighbours tend to have few differing bits, but other rows mix in between
them. The picture below shows one real question from this chapter's benchmark.

**Rescoring** fixes the order:

1. Use the bits to pick a **shortlist**: the rows with the fewest differing bits, say 200 out of 100,000.
2. Score just those 200 exactly, with their full float vectors.
3. Return the best 10 of the 200.

Only 200 full vectors are read per question, so the full vectors can stay on disk while the small bits stay in RAM.
Qdrant's documentation recommends exactly this setup.

:::diagram{name="rag-binary"}
One real question from the benchmark (100,000 synthetic vectors). Left: the 16 rows with the fewest differing bits; green
rows are among the true 10 nearest. Right: the true 10 nearest in exact order. Row 95241, the third best by exact score,
has 78 differing bits, and 14 other rows differ in fewer. A shortlist of 10 by bits misses it; a shortlist of 200 catches
it, and rescoring puts it back in third place.
:::
:::

:::step{type=task task=binary_rescore title="Your turn: bits for the shortlist, floats for the answer" file="07-quantization/fieldbook.py" line="248-253"}
Write `binary_search(query, codes, vectors, k=10, candidates=100)`. `codes` holds the bits of every row and `vectors`
the full float vectors.

1. `distances = hamming(binary_codes(query)[0], codes)`. (`binary_codes` returns a matrix; `[0]` takes its one row.)
2. Make `candidates` at most the number of rows: `candidates = min(candidates, len(distances))`.
3. Keep the `candidates` rows with the smallest distances:
   `shortlist = np.argpartition(distances, candidates - 1)[:candidates]`. `argpartition` puts the smallest values first
   without sorting the whole array, which is faster than `argsort` for 100,000 rows.
4. Score those rows exactly: `scores = vectors[shortlist] @ query`.
5. Sort the scores, best first, and return the k best as `(int(row), float(score))` pairs. Use the **row numbers from
   the shortlist**, not the positions inside it.

The usual slips:

- Returning `i` (the position inside the shortlist) instead of `shortlist[i]` (the row in the whole collection).
- Sorting by Hamming distance at the end instead of by the exact score.
- `np.argpartition(distances, candidates)` when `candidates` equals the number of rows: the index is then one past the
  end. That is why step 3 uses `candidates - 1`.

```bash run
cd /workspace/07-quantization && python quant_bench.py
```

Press **Check**.
:::

:::step{type=history title="From telephone lines to vector databases"}
:::before{title="Every value exact"}
Sound, pictures and measurements were stored and sent as exactly as the equipment allowed, and storage and bandwidth were
always too small.
:::

In **1937** Alec Reeves, an engineer working for ITT in France, invented **pulse-code modulation (PCM)**: send a voice
as a stream of numbers, each rounded to one of a fixed set of levels. Rounding to levels is quantization, and it is part
of every digital phone call, audio CD and digital photo. At Bell Labs in **1957** Stuart Lloyd worked out how to choose
the best levels for PCM. His procedure is the k-means you met in chapter 5 (it was published only in 1982).

For vectors, Moses Charikar showed in **2002** that the signs of **random projections** keep cosine similarity: if you
multiply vectors by random directions and keep only the signs, vectors with similar directions get similar bits. (Our
`binary_codes` keeps the signs of the numbers themselves, which is simpler and works when the numbers are spread evenly
around zero, as they are in our benchmark: almost exactly half of them are positive.)

Hervé Jégou, Matthijs Douze and Cordelia Schmid published **product quantization** in **2011**, the method that made
search over a billion vectors fit in memory. Qdrant added 8-bit quantization in **2023** (version 1.1) and binary
quantization the same year (version 1.5); Weaviate and Elasticsearch added their own between 2023 and 2024. In **2024**
some embedding providers, Cohere for example, began returning int8 and binary embeddings directly.

:::solved
**Four to thirty-two times less memory, at a small loss in quality**, when a quick rough pass is followed by an exact
look at a shortlist.
:::

:::timeline
- **1937** Pulse-code modulation (Reeves).
- **1957** Lloyd's quantizer, the k-means procedure (published 1982).
- **2002** Signs of random projections keep cosine similarity (Charikar).
- **2011** Product quantization (Jégou, Douze, Schmid).
- **2023** Scalar and binary quantization with rescoring in Qdrant; others follow.
:::

An audio CD stores sound as numbers rounded to one of 65,536 levels (16 bits per number, 44,100 numbers a second for
each ear): quantization you have listened to all your life.

:::photo{src="/lesson-images/rag/compact-disc.webp" alt="Shiny optical discs, CDs and DVDs, reflecting rainbow colours" credit="Marius Iordache" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3ADvd_cd_disk.jpg"}
Optical discs. An audio CD holds music as quantized numbers, 65,536 levels each.
:::
:::

:::step{type=try title="Smaller vectors, measured"}
The benchmark uses 100,000 **synthetic** vectors (random vectors built to be shaped like embeddings, from chapter 3's
`fake_embeddings`) and 100 questions. **Recall** is the share of the exact top 10 (found with the full float32 vectors)
that each method also returns. These are our measurements; your numbers will be the same, because the vectors are made
from fixed random seeds.

```text
$ python quant_bench.py
float32:  153.6 MB  recall 100% (the reference)
int8:      38.4 MB  recall 99.2%
binary:     4.8 MB  recall 57.2% (bits only)
binary,   50 rescored: recall 93.7%
binary,  200 rescored: recall 99.8%
binary, 1000 rescored: recall 100.0%
```

What the numbers say:

1. **int8 costs almost nothing.** A quarter of the memory and 99.2% recall. It is usually the first saving to try.
2. **Bits alone are rough.** 57.2% recall from 32 times less memory. ("Bits only" means a shortlist of just 10, so the
   bits alone decide which 10 come back.)
3. **Bits plus rescoring are excellent.** Rescoring 200 candidates out of 100,000 (0.2%) brings recall back to 99.8%:
   2 misses out of 1,000 true neighbours. 1,000 candidates gave 100% here.

**Two honest limits.**

- **Speed in this lab's code.** On this machine, the NumPy binary search took about 19 ms a question, slower than the
  exact float search (about 5 ms), because `np.unpackbits` expands every bit to a whole byte before counting. Real
  databases count the differing bits with one CPU instruction for every 64 bits (called popcount), which is where the
  speed comes from. This lab's version shows the memory and the recall, not the speed.
- **Real models differ.** Our vectors are synthetic. Qdrant's documentation says binary quantization works well only for
  vectors with many numbers; the models it lists have 1,536 or more. With a 384-number model like bge-small, measure
  recall with rescoring on your own data before relying on bits.

**What this means for money.** One real price: an AWS r7g.4xlarge server has 128 GiB of RAM and costs $0.8568 an hour
on demand (Linux, us-east-1, checked 25 November 2026), about $625 a month. For **100 million** vectors of 384 numbers:

| Stored as | Memory for the vectors | Servers of 128 GiB, for the vectors alone | About, a month |
|---|---|---|---|
| float32 | 154 GB (143 GiB) | 2 | $1,250 |
| int8 | 38 GB (36 GiB) | 1, about 30% full | $625 |
| binary in RAM, float32 on disk for rescoring | 4.8 GB in RAM | a small part of 1 | under $625, shared with other work |

(A GiB is 1,073,741,824 bytes, a little more than a GB of 1,000,000,000 bytes; AWS sells RAM in GiB.) Real systems
also need memory for the index itself, HNSW's links for example, so measure your own system; the ratios between the rows
stay the same.
:::

:::step{type=predict title="Guess first"}
:::question
In the benchmark, why does rescoring 200 candidates give 99.8% recall when the bits alone give 57.2%?
:::
- [ ] Rescoring changes the bits
- [x] The true neighbours are almost always somewhere in the 200 rows with the fewest differing bits, just not in the right order; the float vectors fix the order
- [ ] 200 is half the collection
:::explain
Bits are good at "roughly near" and bad at "exactly which is nearest". A shortlist needs only the first. In this
benchmark, the last of a question's true 10 had about 40 rows ahead of it by bits for a typical question, and 238 for
the worst of the 100, which is why 200 candidates miss a few and 1,000 miss none.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does each column get its own scale in int8 quantization?
:::
- [x] Columns have different ranges; one shared scale would squash the narrow columns into a few levels
- [ ] NumPy requires it
- [ ] To make the codes positive
:::explain
Say one column reaches 1.0 and another stays between -0.1 and 0.1. With one shared scale of 1.0 / 127, the narrow column
would use only the codes -13 to 13: 27 of the 255 levels. With its own scale it uses all 255.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Inside a database written for speed, which is cheaper to compare: two float32 vectors of 384 numbers, or their two
binary codes of 48 bytes?
:::
- [ ] Two float32 vectors, because CPUs are made for floats
- [x] Two binary codes: an XOR and a count of ones over 48 bytes
- [ ] They cost the same
:::explain
Modern CPUs count the ones in 64 bits with a single instruction (popcount), so 48 bytes take six XORs and six counts.
The floats need 384 multiplications and additions. (This lab's NumPy code does not use popcount, so there the bits are
not faster; the point of our version is the memory and the recall.)
:::
:::

:::step{type=deep-dive title="Go deeper: quantization in practice"}
**Check your model first.** Binary quantization works well for some embedding models and badly for others. It depends
on how many numbers a vector has and on how they are spread around zero. Measure recall with rescoring on your own data
before switching.

**Oversampling.** Databases let you set the shortlist size as a multiple of k: Qdrant calls it oversampling, and its
documentation suggests starting with 3 (a shortlist of 30 for k = 10). Our benchmark needed a larger multiple, 20 (200
for k = 10), to reach 99.8%: one more reason to measure.

**Product quantization (PQ)** cuts each vector into pieces, for example 48 pieces of 8 numbers, and replaces every piece
with the number of its nearest centroid from a small list made by k-means (chapter 5). With one byte per piece, a
1,536-byte vector becomes 48 bytes. It is the main compression method in FAISS for billion-scale indexes
(`IndexIVFPQ`).

**Where the full vectors live.** Rescoring reads only the shortlist, so the float vectors can stay on SSD while the
compact codes stay in RAM. Qdrant's documentation notes the cost: rescoring from disk is slower than from RAM.

**Smaller at the source.** Some embedding models are trained so that the first 256 or 128 numbers still work on their
own (Matryoshka embeddings; OpenAI's text-embedding-3 models let you ask for fewer numbers this way). That is another
way to cut memory, and it combines with quantization.
:::

:::step{type=recap}
You can now:

- quantize vectors to int8 with a scale per column, and turn them back into approximate floats;
- make binary codes (one bit per number, 48 bytes for 384 numbers) and compare them with the Hamming distance;
- shortlist with bits and rescore with the full vectors to win the accuracy back;
- turn memory into money with honest arithmetic, and choose between float32, int8 and binary, measuring recall on your
  own data first.

Next, chapter 8: putting Fieldbook into a real vector database, Qdrant.

:::photo{src="/lesson-images/rag/rag-07-notes.webp" alt="Handwritten notes about quantization: Quantization stores each number less precisely to save memory. int8 keeps one byte per number: a quarter of float32. Each column gets its own scale, its largest value over 127. Binary keeps one bit per number: 32 times smaller. Bits pick a shortlist; full vectors rescore it. Measure recall on your own data before choosing." ai="true"}
One page of notes for this chapter.
:::
:::
