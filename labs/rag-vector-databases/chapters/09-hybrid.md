:::step{type=story title="CT-112 means nothing to a vector"}
The control room asks Fieldbook a two-word question, the way people type into search boxes: **CT-112**. Camera trap 112.
One patrol report mentions it: R-0301, the big male tiger by the Kolhi stream.

Dense search, the embedding search of chapters 3 to 8, returns five reports about camera traps; R-0301 comes 11th. To the
embedding model, "CT-112" is a few meaningless pieces of a code; it knows the text is about camera traps, so it finds
camera trap reports, but it cannot tell 112 from 117. The old keyword search from chapter 1 would have found it at once:
the report contains exactly that string.

Codes, names, part numbers, form numbers, error codes: real questions are full of exact strings that meaning-based
search handles badly. The fix used by nearly every serious search system is **hybrid search**: run a word search and a
meaning search, and merge the two rankings.


A real camera trap at night: the animal triggers the sensor, the camera takes the picture, and the trap's number goes into the record.

:::photo{src="/lesson-images/rag/camera-trap-leopard.webp" alt="A night-time camera trap photograph of a leopard walking past, lit by the infrared flash" credit="MSGNP" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File%3ACamera_trap_4.jpg"}
A male leopard photographed by a camera trap in Sanjay Gandhi National Park, Mumbai.
:::
:::mission
Write BM25, the ranking formula behind most search engines, then merge its ranking with dense search using reciprocal
rank fusion, and see where hybrid search helps, and where it hurts.
:::
:::

:::step{type=concept title="BM25: rare words count most" file="09-hybrid/fieldbook.py" line="285-295"}
Chapter 1 counted shared words. BM25 counts them better, with three ideas:

| Idea | Why | In the formula |
|---|---|---|
| **Rare words matter more** | "ct-112" is in 1 chunk of 55; "the" is in nearly all | `idf = log((n - df + 0.5) / (df + 0.5) + 1)`, df = chunks containing the word |
| **Repeats help, less and less** | the 5th "tiger" adds less than the 1st | `tf * (k1 + 1) / (tf + k1 * ...)`, tf = times in this chunk; k1 = 1.5 |
| **Long chunks are held back** | a long chunk contains many words by chance | `... (1 - b + b * len(doc) / average_length)`; b = 0.75 |

For each distinct word of the query, every chunk containing it gains:

```text
idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / average_length))
```

Add the gains over the query's words and you have the chunk's BM25 score. `tokens(text)` splits a text into lower-case
words and keeps codes like `ct-112` whole, which is exactly what this search needs.

:::trace{title="idf for three words over the 55 chunks"}
| word | chunks containing it (df) | idf |
|---|---|---|
| ct-112 | 1 | log(54.5 / 1.5 + 1) = 3.62 |
| tiger | 3 | log(52.5 / 3.5 + 1) = 2.77 |
| the | 50 | log(5.5 / 50.5 + 1) = 0.10 |
:::

"the" is in 50 of the 55 chunks, so it adds almost nothing; "ct-112" is in one, so it decides the ranking.
:::

:::step{type=task task=bm25_scores title="Your turn: BM25 by hand" file="09-hybrid/fieldbook.py" line="290-295"}
Write `bm25_scores(query, docs, k1=1.5, b=0.75)`. `query` is a list of tokens, `docs` a list of token lists.

1. `n = len(docs)`, the average document length, and `scores = np.zeros(n)`.
2. For each **distinct** term in the query (`set(query)`): count `df`, skip the term if it is 0, compute `idf`.
3. For each document, `tf = doc.count(term)`; if it is above 0, add the gain from the formula above to that document's
   score.
4. Return `scores`.

Press **Check**.
:::

:::step{type=history title="Okapi BM25 and rank fusion"}
:::before{title="Counting words"}
The first ranked search engines scored a document by how often the query's words appeared in it. Long documents and
common words won.
:::

Karen Spärck Jones introduced **inverse document frequency** in **1972**: weight a word by how rare it is. With Stephen
Robertson she built a probabilistic theory of relevance (**1976**), and Robertson's team at City University London tested
formula after formula in their **Okapi** search system. The 25th "best match" formula, **BM25**, did best at the TREC
evaluation in **1994** and has been the standard ever since: it became the default ranking in Lucene and therefore
Elasticsearch in **2016**. For merging rankings from different systems, Gordon Cormack, Charles Clarke and Stefan
Büttcher showed in **2009** that a very simple rule, **reciprocal rank fusion**, beat cleverer methods.

:::solved
**Exact words, weighted by rarity, plus a way to merge any rankings.** Together they give hybrid search: exact strings
from BM25, meaning from embeddings.
:::

:::timeline
- **1972** Inverse document frequency (Spärck Jones).
- **1976** The probabilistic relevance model (Robertson and Spärck Jones).
- **1994** BM25 at TREC.
- **2009** Reciprocal rank fusion.
- **2016** BM25 becomes Lucene's and Elasticsearch's default.
:::
:::

:::step{type=concept title="Merging two rankings: reciprocal rank fusion" file="09-hybrid/fieldbook.py" line="298-322"}
Now you have two rankings for every question: dense (by cosine, scores around 0.4 to 0.8) and BM25 (scores from 0 to
about 15). Those scores are on different scales, so you cannot just add them. **Reciprocal rank fusion** (RRF) ignores
the scores and uses only positions:

```text
each ranking gives an id  1 / (k + rank)      rank 1 is the first place, k = 60
an id's fused score = the sum over the rankings it appears in
```

An id ranked first by both gets 1/61 + 1/61. An id ranked first by one and missing from the other gets 1/61 only. The
constant 60 keeps the first few places from dominating; it was chosen by experiment in the original paper and almost
everyone keeps it.

`Index` (written for you) puts it together: `dense()` gives the 20 best ids by meaning, `keyword()` the 20 best by BM25,
and `hybrid()` fuses the two lists with your `rrf` and returns the top chunks.
:::

:::step{type=task task=rrf_fuse title="Your turn: reciprocal rank fusion" file="09-hybrid/fieldbook.py" line="298-302"}
Write `rrf(rankings, k=60)`: for every ranking, for every id with its rank (`enumerate(ranking, start=1)`), add
`1 / (k + rank)` to that id's total in a dict. Return the ids sorted by their totals, highest first.

```bash run
cd /workspace/09-hybrid && python hybrid_demo.py
```

Press **Check**.
:::

:::step{type=try title="Where hybrid helps, and where it hurts"}
```text
$ python hybrid_demo.py
CT-112
  dense (meaning): ['R-0503', 'R-0402', 'R-0304', 'R-0303', 'R-0405']
  BM25 (words):    ['R-0301']
  hybrid (RRF):    ['R-0301', 'R-0503', 'R-0402', 'R-0304', 'R-0303']

Where do we take someone a snake has bitten?
  dense (meaning): ['FM-4.6', 'R-0309', 'FM-9.1', 'FM-7.3', 'FM-7.1']
  BM25 (words):    ['R-0309', 'FM-4.6', 'FM-4.5', 'FM-7.1', 'FM-1.2']
  hybrid (RRF):    ['FM-4.6', 'R-0309', 'FM-7.1', 'R-0304', 'FM-4.5']

Can tourists get out of the jeep to take photos?
  dense (meaning): ['FM-6.2', 'FM-6.3', 'R-0305', 'R-0310', 'FM-6.5']
  BM25 (words):    ['FM-8.1', 'R-0306', 'FM-5.3', 'FM-4.2', 'FM-4.6']
  hybrid (RRF):    ['FM-1.2', 'R-0305', 'FM-2.2', 'FM-3.3', 'FM-6.4']
```

**CT-112: hybrid wins.** Dense search ranks R-0301 only 11th, below ten other camera trap reports. BM25 finds only
R-0301 (the only chunk with that token), and fusion puts it first.

**The snakebite: both agree**, and the fused list keeps FM-4.6 (snakebite first aid) and R-0309 (the villager bitten
near Rajur) at the top.

**The jeep: hybrid loses the answer.** Dense search had it right: FM-6.2 Visitor rules. BM25 has never heard of it: the
section says *visitors*, *vehicle* and *photograph*, the question says *tourists*, *jeep* and *photos*, so FM-6.2 is not
in BM25's top 20 at all. Here is the arithmetic:

:::trace{title="Why FM-6.2 dropped out"}
| chunk | dense rank | BM25 rank | fused score |
|---|---|---|---|
| FM-6.2 Visitor rules | 1 | not in the top 20 | 1/61 = 0.0164 |
| FM-1.2 Gates and checkposts | 6 | 9 | 1/66 + 1/69 = 0.0296 |
| R-0305 Vehicle off the road | 3 | 13 | 1/63 + 1/73 = 0.0296 |
| FM-2.2 Night patrols | 11 | 8 | 1/71 + 1/68 = 0.0288 |
:::

Being fairly good in both lists beats being the best in one. That is RRF's known weakness, and the reason chapter 12
measures instead of assuming: on Fieldbook's 26 test questions, hybrid search fixes the code questions and breaks some
paraphrased ones. Chapter 10 adds the step that repairs both.
:::

:::step{type=predict title="Guess first"}
:::question
A question asks "Form P-7". Which search do you expect to rank FM-6.3 (drones and photography permits) first?
:::
- [ ] Only dense: it understands forms
- [x] Both: "p-7" is a rare token only in FM-6.3 and one report, and the embedding also links "form" and "permit"
- [ ] Neither
:::explain
When the code is rare and the topic is clear, both searches agree, and fusion keeps them agreeing.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does RRF use ranks instead of adding the dense and BM25 scores?
:::
- [x] The scores are on different scales (cosines near 0.6, BM25 up to about 15), so adding them lets BM25 dominate
- [ ] Ranks are faster to compute
- [ ] Scores are not available
:::explain
You could rescale scores first, but how to rescale depends on the data; positions need no tuning.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In BM25, why does "the" add almost nothing to a score?
:::
- [ ] It is removed as a stopword
- [x] It appears in almost every chunk, so its idf is close to zero
- [ ] BM25 ignores words shorter than four letters
:::explain
No stopword list is needed: rarity does the work. (Chapter 1's keyword search used a stopword list instead.)
:::
:::

:::step{type=deep-dive title="Go deeper: hybrid search in real systems"}
**Weights.** Many systems weight the fusion (for example, dense counts double), or fuse only the top 10 of each list.
Tune it on your own questions, never by feel.

**Sparse vectors.** Vector databases store BM25-style scores as **sparse vectors** (only the non-zero words), so one
database runs both searches and fuses them: Qdrant's Query API does RRF over a dense and a sparse search in one call;
Weaviate, Elasticsearch and OpenSearch have hybrid modes. Learned sparse models (SPLADE) add related words to the sparse
vector, so "jeep" can match "vehicle".

**Stemming.** "photos" and "photograph" are different tokens here. Search engines usually reduce words to a stem
("photograph" and "photos" become "photo"), which would have rescued FM-6.2 partly.
:::

:::step{type=recap}
You can now:

- compute BM25 scores by hand: idf for rarity, term frequency with saturation, length normalization;
- fuse rankings with reciprocal rank fusion, without comparing scores;
- show where hybrid search wins (codes and exact names) and where it loses (paraphrases), with the arithmetic;
- explain why hybrid search should be measured, not assumed.

Next, chapter 10: a second, careful judge that reads every candidate with the question.

:::photo{src="/lesson-images/rag/rag-09-notes.webp" alt="Handwritten notes about hybrid search: BM25: exact words, rare ones count; Codes need word search; RRF: 1 / (60 + rank); Good in both beats best in one; Measure, do not assume" ai="true"}
One page of notes for this chapter.
:::
:::
