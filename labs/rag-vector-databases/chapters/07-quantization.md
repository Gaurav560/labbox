:::step{type=story title="The memory bill"}
Every vector so far has been 384 numbers of 4 bytes each: 1,536 bytes. For Fieldbook's 55 chunks, nothing. But the same
arithmetic decides whether a large system fits on one server or needs a rack of them:

| Vectors | float32 memory |
|---|---|
| 100,000 | 154 MB |
| 10 million | 15.4 GB |
| 100 million | 154 GB |

HNSW (chapter 6) wants all of it in RAM, and RAM is the expensive part of a server. So vector databases do something that
sounds wrong at first: they store the numbers **less precisely**. A float32 can tell apart about 8 million values between
1 and 2. To decide which of two vectors is closer to a question, you need far less than that.

Making numbers less precise to save space is called **quantization**. This chapter tries the two kinds every vector
database offers: 8 bits per number instead of 32, and **1 bit** per number.

:::mission
Squeeze vectors into 8-bit whole numbers and measure what recall you lose, then reduce them to single bits, shortlist by
counting differing bits, and win the accuracy back by rescoring the shortlist with the full vectors.
:::
:::

:::step{type=concept title="int8: 256 levels instead of 4 billion" file="07-quantization/fieldbook.py" line="224-235"}
**Scalar quantization** maps each number onto a whole number from -127 to 127, one byte. Each column (each of the 384
dimensions) gets its own **scale**, so that its largest absolute value becomes exactly 127:

:::trace{title="One column quantized"}
| value | scale = 1.0 / 127 | value / scale | rounded int8 | back: code x scale |
|---|---|---|---|---|
| 0.50 | 0.007874 | 63.5 | 64 | 0.5039 |
| -1.00 | 0.007874 | -127.0 | -127 | -1.0000 |
| 0.25 | 0.007874 | 31.75 | 32 | 0.2520 |
:::

The largest value in the column (1.00, ignoring its sign) sets the scale. Every number is now off by at most half a
step (here 0.004), a quarter of the memory is used, and `dequantize` turns codes back into approximate floats.

Two details: round **before** converting (`np.round(...).astype(np.int8)`; converting alone cuts 63.5 to 63), and a column
that is all zeros has a largest value of 0, so give it the scale 1 instead of dividing by zero.
:::

:::step{type=task task=quantize_int8 title="Your turn: 8 bits instead of 32" file="07-quantization/fieldbook.py" line="224-230"}
Write `quantize_int8(m)`:

1. `scales = np.abs(m).max(axis=0) / 127` (one per column), and set any scale of 0 to 1.
2. `codes = np.round(m / scales).astype(np.int8)`.
3. Return `(codes, scales.astype(np.float32))`.

Press **Check**.
:::

:::step{type=concept title="Binary: one bit per number, and a shortlist" file="07-quantization/fieldbook.py" line="238-253"}
Go further: keep only the **sign** of each number. Positive becomes 1, everything else 0. 384 numbers become 384 bits,
**48 bytes**, 32 times smaller than float32. `binary_codes` packs eight bits into each byte with `np.packbits`.

Comparing two bit strings is extremely cheap: XOR them (1 wherever they differ) and count the ones. That count is the
**Hamming distance**: the smaller, the more alike.

```text
query bits   1 0 1 1 0 0 1 0
chunk bits   1 0 0 1 0 1 1 0
XOR          0 0 1 0 0 1 0 0    -> Hamming distance 2
```

One bit per number throws away a lot, so the bits alone give a rough ranking. The trick is **rescoring**: use the bits to
pick a **shortlist** of, say, 200 candidates out of 100,000, then score just those 200 exactly with the full float
vectors (which can live on disk, since only 200 are read). Fast and rough first, exact on a few at the end.

:::diagram{name="rag-binary"}
Bits pick a shortlist from the whole collection; the full vectors decide the order within it.
:::
:::

:::step{type=task task=binary_rescore title="Your turn: bits for the shortlist, floats for the answer" file="07-quantization/fieldbook.py" line="248-253"}
Write `binary_search(query, codes, vectors, k=10, candidates=100)`:

1. `distances = hamming(binary_codes(query)[0], codes)`.
2. Keep the `candidates` rows with the smallest distances: `np.argpartition(distances, candidates - 1)[:candidates]`
   (make `candidates` at most the number of rows first).
3. Score those rows exactly with `vectors[shortlist] @ query`, and return the k best as
   `(int(row), float(score))` pairs, best first.

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

In **1937** Alec Reeves invented **pulse-code modulation**: send a voice as a stream of numbers, each rounded to one of a
fixed set of levels. Rounding to levels is quantization, and it is how every phone call, CD and digital photo works. At
Bell Labs in **1957** Stuart Lloyd worked out the best levels for PCM, the same procedure you met as k-means in chapter 5.
For vectors, Moses Charikar showed in **2002** that the signs of random projections preserve cosine similarity: binary
codes for meaning. Hervé Jégou, Matthijs Douze and Cordelia Schmid's **product quantization** (**2011**) compressed vectors
for billion-scale search. Vector databases added scalar and binary quantization with rescoring around **2023** (Qdrant,
Weaviate, Elasticsearch), and embedding providers began training models whose vectors survive being cut to bits.

:::solved
**Four to thirty-two times less memory, at almost no loss in quality**, when a quick rough pass is followed by an exact
look at a shortlist.
:::

:::timeline
- **1937** Pulse-code modulation (Reeves).
- **1957** Lloyd's optimal quantizer.
- **2002** Sign bits keep cosine similarity (Charikar).
- **2011** Product quantization.
- **2023** Binary quantization with rescoring in vector databases.
:::

Every compact disc stores sound as numbers rounded to 65,536 levels: quantization you have listened to all your life.

:::photo{src="/lesson-images/rag/compact-disc.webp" alt="Two shiny compact discs reflecting rainbow colours" credit="Marius Iordache" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3ADvd_cd_disk.jpg"}
Compact discs.
:::
:::

:::step{type=try title="Smaller vectors, measured"}
100,000 vectors, 100 questions, recall against the exact float32 answer:

```text
$ python quant_bench.py
float32:  153.6 MB  recall 100% (the reference)
int8:      38.4 MB  recall 99%
binary:     4.8 MB  recall 57% (bits only)
binary,   50 rescored: recall 94%
binary,  200 rescored: recall 100%
binary, 1000 rescored: recall 100%
```

1. **int8 is nearly free**: a quarter of the memory and 99% recall. Most production systems should start here.
2. **Bits alone are rough**: 57% recall from 32 times less memory. Many near-ties in Hamming distance hide the true order.
3. **Bits plus rescoring are excellent**: rescoring just 200 candidates out of 100,000 (0.2%) brings recall back to 100%.

What this means for money, with one real price: an AWS r7g.4xlarge server has 128 GiB of RAM and costs about $0.857 an
hour on demand in us-east-1 (mid-2026), about $625 a month. For **100 million** vectors of 384 numbers:

| Stored as | Vectors in RAM | Servers of 128 GiB for the vectors alone | About, a month |
|---|---|---|---|
| float32 | 154 GB | 2 | $1,250 |
| int8 | 38 GB | 1, a third full | $625 |
| binary in RAM, float32 on disk for rescoring | 4.8 GB | a small slice of 1 | under $625, shared with other work |

The same search, at 99 to 100% recall, for half the cost or less. (Real systems add the index's own memory, HNSW links
for example, so measure your own; the ratios hold.)
:::

:::step{type=predict title="Guess first"}
:::question
Why does rescoring with 200 candidates recover 100% recall, when the bits alone give 57%?
:::
- [ ] Rescoring changes the bits
- [x] The true neighbours are almost always somewhere in the 200 closest by Hamming distance, just not in the right order; the float vectors fix the order
- [ ] 200 is half the collection
:::explain
Bits are good at "roughly near" and bad at "exactly which is nearest". A shortlist needs only the first.
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
A column whose values stay within -0.1 and 0.1 would use only about 27 of the 255 levels with a scale set by a column that
reaches 1.0.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which is cheapest to compare: two float32 vectors or two binary codes?
:::
- [ ] Two float32 vectors, because CPUs are made for floats
- [x] Two binary codes: an XOR and a count of ones over 48 bytes
- [ ] They cost the same
:::explain
Modern CPUs count the ones in 64 bits in a single instruction, so 48 bytes take a handful of instructions.
:::
:::

:::step{type=deep-dive title="Go deeper: quantization in practice"}
**Check your model first.** Binary quantization works well for some embedding models and badly for others (it depends on
how the numbers are spread around zero). Measure recall with rescoring on your own data before switching.

**Product quantization (PQ)** splits each vector into pieces and replaces every piece with the number of its nearest
centroid from a small codebook (k-means again). It compresses 1,536 bytes to 16 to 64 bytes and is the workhorse of
billion-scale indexes (FAISS's `IndexIVFPQ`).

**Where the full vectors live.** Rescoring reads only the shortlist, so the float vectors can stay on SSD or in a cheaper
store while the compact codes stay in RAM.

**Smaller at the source.** Some embedding models are trained so that the first 256 or 128 numbers still work on their own
(Matryoshka embeddings): another way to cut memory, and it combines with quantization.
:::

:::step{type=recap}
You can now:

- quantize vectors to int8 with a scale per column, and turn them back;
- make binary codes and compare them with the Hamming distance;
- shortlist with bits and rescore with full vectors to recover accuracy;
- turn memory into money with honest arithmetic, and choose between float32, int8 and binary.

Next, chapter 8: putting Fieldbook into a real vector database, Qdrant.

:::photo{src="/lesson-images/rag/rag-07-notes.webp" alt="Handwritten notes about quantization: int8: a quarter of the memory; One scale per column; Binary: 1 bit per number; Shortlist by bits, rescore by floats; Less RAM, smaller bill" ai="true"}
One page of notes for this chapter.
:::
:::
