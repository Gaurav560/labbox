:::step{type=story title="CT-112 means nothing to a vector"}
The control room asks Fieldbook a two-word question, the way people type into search boxes: **CT-112**. Camera trap 112.
One patrol report mentions it: R-0301, the big male tiger by the Kolhi stream.

**Dense search**, the embedding search of chapters 3 to 8 (it is called dense because nearly all of a vector's
numbers are non-zero), ranks R-0301 only **11th**. Its first five results all mention *other* camera traps: CT-113 to CT-120,
CT-117, CT-104. To the embedding model, "CT-112" is a few pieces of a code with no meaning. It can tell the text is about
camera traps, so it finds camera trap reports, but it cannot tell 112 from 117.

The old keyword search from chapter 1 would have found it at once: the report contains exactly that string.

Codes, names, part numbers, form numbers and error codes are everywhere in real questions, and meaning-based search
handles exact strings badly. The usual fix in modern search systems is **hybrid search**: run a word search and a meaning
search, and merge the two rankings. This chapter builds it, and then measures where it helps and where it hurts.

A real camera trap at night: the animal walks past the sensor, the camera takes the picture, and the trap's number goes
into the record, just like CT-112 in the report.

:::photo{src="/lesson-images/rag/camera-trap-leopard.webp" alt="A night-time camera trap photograph of a leopard walking past, lit by the infrared flash" credit="MSGNP" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File%3ACamera_trap_4.jpg"}
A male leopard photographed by a camera trap in Sanjay Gandhi National Park, Mumbai.
:::
:::mission
Write BM25, the ranking formula behind most search engines, then merge its ranking with dense search using reciprocal
rank fusion, and see where hybrid search helps, and where it hurts.
:::
:::

:::step{type=concept title="BM25: rare words count most" file="09-hybrid/fieldbook.py" line="285-295"}
Chapter 1 counted how many words a chunk shares with the question. **BM25** ("best matching", formula number 25) is a
better way to score shared words. It uses three ideas:

| Idea | Why | Name in the formula |
|---|---|---|
| **Rare words matter more** | "ct-112" is in 1 chunk of 55; "the" is in 50 | **idf**, inverse document frequency |
| **Repeats help, but less and less** | the 5th "tiger" in a chunk adds less than the 1st | **tf**, term frequency, with **k1** controlling how fast it levels off |
| **Long chunks are held back** | a long chunk contains many words by chance | the chunk's length against the average, with **b** controlling how much |

Some words first:

- A **term** is one word of the question. **df** (document frequency) is how many chunks contain it. **tf** is how many
  times it appears in one chunk.
- `tokens(text)`, written for you, splits a text into lower-case words and keeps codes like `ct-112` whole. Unlike
  chapter 1's `words`, it keeps every word, even "the".

**idf**, how rare a term is, with `n` the number of chunks (55):

```text
idf = log((n - df + 0.5) / (df + 0.5) + 1)
```

:::trace{title="idf for three words over the 55 chunks (computed with the lab's code)"}
| word | chunks containing it (df) | idf |
|---|---|---|
| ct-112 | 1 | log(54.5 / 1.5 + 1) = 3.62 |
| tiger | 3 | log(52.5 / 3.5 + 1) = 2.77 |
| the | 50 | log(5.5 / 50.5 + 1) = 0.10 |
:::

"the" is in 50 of the 55 chunks, so it adds almost nothing; "ct-112" is in one, so it decides the ranking. No list of
words to ignore is needed: rarity does the work.

**The gain.** For each distinct term of the question, every chunk that contains it gains:

```text
idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(chunk) / average_length))
```

- With `tf` = 1 in a chunk of average length, the fraction is exactly 1, so the gain is just `idf`.
- As `tf` grows, the fraction grows towards `k1 + 1` (2.5 here) but never reaches it: repeats help, less and less.
- A chunk longer than average makes the bottom bigger, so its gain is smaller. `b` = 0 would switch this off; `b` = 1
  would apply it fully.

This lab uses `k1` = 1.5 and `b` = 0.75. Lucene, the search library inside Elasticsearch and OpenSearch, uses `k1` = 1.2
and the same `b`. Fieldbook's chunks are 53 tokens long on average.

Add the gains over the question's terms, and you have the chunk's BM25 score.
:::

:::step{type=task task=bm25_scores title="Your turn: BM25 by hand" file="09-hybrid/fieldbook.py" line="290-295"}
Write `bm25_scores(query, docs, k1=1.5, b=0.75)`. `query` is a list of tokens, and `docs` is a list of token lists (one
per chunk).

1. `n = len(docs)`, `average = sum(len(d) for d in docs) / n`, and `scores = np.zeros(n)`.
2. For each **distinct** term in the query (`for term in set(query)`): count `df`, the number of docs that contain the
   term. Skip the term if `df` is 0. Otherwise compute `idf` with `math.log`.
3. For each document `i`, `tf = d.count(term)`; if it is above 0, add the gain from the formula above to `scores[i]`.
4. Return `scores`.

The usual slips:

- Looping over `query` instead of `set(query)`: a word typed twice is then counted twice.
- Using `len(docs)` where the chunk's own length `len(d)` belongs.
- Forgetting the `+ 1` inside the `log`: very common words then get a negative idf.

Press **Check**.
:::

:::step{type=history title="Okapi BM25 and rank fusion"}
:::before{title="Counting words"}
The first ranked search systems scored a document by how often the query's words appeared in it. Long documents and
common words won.
:::

Karen Spärck Jones introduced **inverse document frequency** in **1972**: weight a word by how rare it is. With Stephen
Robertson she worked out a probabilistic theory of relevance (**1976**), and Robertson's team at City University London
tested formula after formula in their **Okapi** search system. Formula number 25 of their "best match" series, **BM25**,
was introduced at the TREC-3 evaluation in **1994**, where it was among the best, and it has been the standard ranking
formula ever since. In **2016** it became the default in Lucene (version 6) and so in Elasticsearch (version 5).

For merging rankings, Gordon Cormack, Charles Clarke and Stefan Büttcher showed in **2009** that a very simple rule,
**reciprocal rank fusion**, beat more complicated methods in their tests.

:::solved
**Exact words, weighted by rarity, plus a way to merge any rankings.** Together they give hybrid search: exact strings
from BM25, meaning from embeddings.
:::

:::timeline
- **1972** Inverse document frequency (Spärck Jones).
- **1976** The probabilistic relevance model (Robertson and Spärck Jones).
- **1994** BM25 at TREC-3.
- **2009** Reciprocal rank fusion (Cormack, Clarke, Büttcher).
- **2016** BM25 becomes the default in Lucene and Elasticsearch.
:::
:::

:::step{type=concept title="Merging two rankings: reciprocal rank fusion" file="09-hybrid/fieldbook.py" line="298-322"}
Now every question gets two rankings: dense (by cosine; the best chunk scored between 0.63 and 0.86 for this lab's
questions) and BM25 (the best chunk scored between 3.9 and 14.9). The scores are on different scales, so you cannot just
add them: BM25 would win every time.

**Reciprocal rank fusion** (RRF) ignores the scores and uses only the positions:

```text
each ranking gives each of its chunks   1 / (k + rank)      rank 1 is first place; k = 60
a chunk's fused score = the sum over the rankings it appears in
```

- A chunk ranked first in both lists gets 1/61 + 1/61 = 0.0328.
- A chunk ranked first in one list and missing from the other gets only 1/61 = 0.0164.
- The constant 60 makes the drop from one place to the next small, so no single list's first place can dominate. The
  original paper picked 60 by experiment, and most systems keep it.

:::diagram{name="rag-rrf"}
The real CT-112 rankings. Dense search puts R-0301 11th; BM25 finds only R-0301. Its fused score adds both lists, so it
beats R-0503, which is first in one list only.
:::

`Index` (written for you) puts it together: `dense()` gives the 20 best chunk ids by meaning, `keyword()` up to 20 by
BM25 (only chunks with a score above 0), and `hybrid()` fuses the two lists with your `rrf` and returns the top chunks.
:::

:::step{type=task task=rrf_fuse title="Your turn: reciprocal rank fusion" file="09-hybrid/fieldbook.py" line="298-302"}
Write `rrf(rankings, k=60)`. `rankings` is a list of lists of ids, each best first.

1. Start an empty dict for the totals.
2. For every ranking, and for every id with its rank (`for rank, item in enumerate(ranking, start=1)`), add
   `1 / (k + rank)` to that id's total (`fused.get(item, 0.0) + ...`).
3. Return the ids sorted by their totals, highest first: `sorted(fused, key=lambda item: -fused[item])`.

The usual slips:

- `enumerate(ranking)` without `start=1`: the first place then counts as rank 0.
- Returning the totals or `(id, total)` pairs instead of the ids alone.

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

**CT-112: hybrid wins.** Dense search ranks R-0301 11th. BM25 finds only R-0301, the only chunk with that token, and
fusion puts it first (the picture above).

**The snakebite: both agree.** The fused list keeps FM-4.6 (snakebite first aid) and R-0309 (the villager bitten near
Rajur) at the top.

**The jeep: hybrid loses the answer.** Dense search had it right: FM-6.2 Visitor rules. But FM-6.2 says *visitors* and
*vehicle*, and the question says *tourists*, *jeep* and *photos*. The only words they share are "the" and "to", so BM25
ranks FM-6.2 41st, far outside its top 20. Here is the arithmetic:

:::trace{title="Why FM-6.2 dropped out (real ranks)"}
| chunk | dense rank | BM25 rank | fused score |
|---|---|---|---|
| FM-6.2 Visitor rules | 1 | 41 (not in the top 20) | 1/61 = 0.0164 |
| FM-1.2 Gates and checkposts | 6 | 9 | 1/66 + 1/69 = 0.0296 |
| R-0305 (a visitor vehicle off the road) | 3 | 13 | 1/63 + 1/73 = 0.0296 |
| FM-2.2 Night patrols | 11 | 8 | 1/71 + 1/68 = 0.0288 |
:::

FM-6.2 ends up 8th in the fused list. Being fairly good in both lists beats being the best in one: that is RRF's known
weakness.

**On all 26 test questions** (the same file chapter 12 uses), we measured how often the right chunk comes **first**:

| Search | Right chunk first | Right chunk in the top 5 |
|---|---|---|
| dense | 20 of 26 | 24 of 26 |
| BM25 | 12 of 26 | 21 of 26 |
| hybrid (RRF) | 15 of 26 | 24 of 26 |

What happened inside those numbers:

- **The code questions improved.** Three of the 26 ask about camera trap codes. For "What did CT-112 record?" the answer
  moved from 14th (dense) to 2nd (hybrid); for "Which report mentions CT-104?" from 7th to 2nd. Both entered the top 5,
  though neither reached first place. (For CT-117 both searches already had a right report first.)
- **Questions in other words got worse.** At first place, fusion fixed one question (which radio channel is kept for
  emergencies) and pushed six right answers down, the jeep question among them.
- In the top 5 the two even out: hybrid gains the two code questions and loses two others, so both find 24 of 26.

So on these questions hybrid search is worse than dense search at first place, and equal in the top 5. A set with many
more code questions would favour it. That is why chapter 12 measures instead of assuming, and chapter 10 adds the step
that repairs both cases.
:::

:::step{type=predict title="Guess first"}
:::question
The question is "Form P-7". Which search do you expect to rank FM-6.3 (drones and photography permits) first?
:::
- [ ] Only dense: it understands forms
- [x] Both: "p-7" is a rare token (only FM-6.3 and one report contain it), and dense search also ranks FM-6.3 first
- [ ] Neither
:::explain
We ran it: dense, BM25 and hybrid all put FM-6.3 first and R-0310 (the drone flown without a P-7 permit) second. When the
code is rare and the topic is clear, both searches agree, and fusion keeps them agreeing.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does RRF use ranks instead of adding the dense and BM25 scores?
:::
- [x] The scores are on different scales (best cosines here 0.63 to 0.86, best BM25 scores 3.9 to 14.9), so adding them lets BM25 dominate
- [ ] Ranks are faster to compute
- [ ] Scores are not available
:::explain
You could rescale the scores first, but the right way to rescale depends on the data; positions need no tuning.
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
"the" is in 50 of the 55 chunks: idf 0.10, against 3.62 for "ct-112". No stopword list is needed: rarity does the work.
(Chapter 1's keyword search used a stopword list instead.)
:::
:::

:::step{type=deep-dive title="Go deeper: hybrid search in real systems"}
**Weights.** Many systems weight the fusion (for example, dense counts double), or fuse only the top 10 of each list.
Tune it on your own questions, never by feel.

**Sparse vectors.** A BM25-style score can be stored as a **sparse vector**: one number per word of the vocabulary, almost
all zero, so only the non-zero ones are kept. Then one database runs both searches and fuses them. Qdrant's Query API
does RRF over a dense and a sparse search in one call; Weaviate, Elasticsearch and OpenSearch have hybrid modes too.

**Stemming does not fix the jeep.** Search engines often cut words to a stem: "visitors" becomes "visitor", "photos"
becomes "photo". That joins forms of the same word, but never different words: "tourists" and "visitors", or "jeep" and
"vehicle", stay apart. Linking those needs a list of synonyms, or a **learned sparse model** (SPLADE, for example), which
adds related words to the sparse vector, so "jeep" can also count as "vehicle".
:::

:::step{type=recap}
You can now:

- compute BM25 scores by hand: idf for rarity, term frequency that levels off, and a correction for long chunks;
- fuse rankings with reciprocal rank fusion, without comparing scores;
- show where hybrid search wins (codes and exact names) and where it loses (questions in different words), with the
  arithmetic;
- explain why hybrid search must be measured, not assumed: on Fieldbook's 26 questions it is worse than dense at first
  place.

Next, chapter 10: a second, careful judge that reads every candidate together with the question.

:::photo{src="/lesson-images/rag/rag-09-notes.webp" alt="Handwritten notes about hybrid search: BM25 scores shared words, and rare words count most. Embeddings often miss exact codes; word search finds them. Reciprocal rank fusion adds 1 / (60 + rank) from each list. Good in both lists beats best in one. Hybrid can lose answers that use other words. Measure on your own questions before choosing." ai="true"}
One page of notes for this chapter.
:::
:::
