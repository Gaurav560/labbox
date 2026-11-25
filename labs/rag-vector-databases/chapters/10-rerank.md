:::step{type=story title="A second, careful reading"}
Look at how every search so far has worked. Each chunk was turned into a vector **before** anyone asked anything. The
question was turned into a vector on its own. Then the two vectors were compared. The model that made the chunk's vector
never saw the question: it had to squeeze everything the chunk might ever be asked about into one fixed list of numbers
(384 of them with bge-small).

That is why the "jeep" question went wrong in chapter 9, and why in chapter 3 the big-cat question scored FM-4.2, the
right section, only a little above "Finding a dead animal" (0.595 against 0.565). The search was fast because each side
was read alone.

There is a slower, more careful way: give a model the question **and** a chunk **together**, let it read both, and ask
for one number: how well does this chunk answer this question? Doing that for every chunk would be slow. Here it would
take about 4 seconds for Fieldbook's 55 chunks, and it is impossible for millions. But for the 20 candidates that hybrid
search already found, it is affordable. This two-step pattern, a fast wide search followed by a slow careful judge, is
called **reranking**.

:::mission
Rerank hybrid search's candidates with a cross-encoder, then build the two-stage pipeline Fieldbook will use from now on,
and measure what the extra care costs in time.
:::
:::

:::step{type=concept title="Bi-encoder and cross-encoder" file="10-rerank/fieldbook.py" line="338-342"}
Two kinds of model, two ways to compare a question with a text:

| | Bi-encoder (chapters 2 to 9) | Cross-encoder (this chapter) |
|---|---|---|
| reads | the question alone, the chunk alone | the question and the chunk **together** |
| outputs | one vector for each | one relevance score for the pair |
| work on the chunks | done once, ahead of time | done again for every question |
| time to compare | about a microsecond, once the vectors exist | about 70 ms per pair, measured on this lab's 2 CPUs |
| quality | good | usually better: it sees which words of the chunk answer which words of the question |

"Bi" means two: the two texts are encoded separately. "Cross" means the two texts are read across each other, in one
pass.

Fieldbook's cross-encoder is **ms-marco-MiniLM-L-6-v2**. Its name says what it is:

- **MiniLM** is a small **transformer**, the kind of neural network behind today's language models. A transformer is
  built from **layers**, steps that each refine the model's reading of the text; **L-6** means this one has 6 of them
  (large models have dozens).
- **ms-marco** is what it learned from: MS MARCO, a collection of about half a million real web search questions, each
  with passages that people marked as answering it.

It is already in your lab machine, so it runs offline.

**Its scores are not cosines.** They are plain numbers with no fixed range, where higher means more relevant. On
Fieldbook's 26 test questions we measured: right chunks scored about 4 in the middle (9 in 10 above -1.9), wrong chunks
about -11 (9 in 10 below -7). But a score is most useful **compared with the other candidates for the same question**:
in the jeep question below, the right chunk scores only -6.6, and it is still the best of the 20.

`reranker().rerank(question, texts)` returns one score per text, in the same order as the texts. `reranker()` loads the
model once and keeps it (`@lru_cache`); loading takes about 0.8 seconds.
:::

:::step{type=task task=rerank title="Your turn: score question and chunk together" file="10-rerank/fieldbook.py" line="345-350"}
Write `rerank(question, chunks, top_n=5)`:

1. `scores = list(reranker().rerank(question, [chunk_text(c) for c in chunks]))`: one score per chunk.
2. Order the positions by score, highest first: `np.argsort(scores)[::-1]` (`argsort` sorts lowest first, and `[::-1]`
   reverses it). Keep the first `top_n`.
3. Return a **copy** of each of those chunks with its score added: `dict(chunks[i], rerank=float(scores[i]))`.

The usual slips:

- Writing the score into the chunk itself (`chunks[i]["rerank"] = ...`). The index keeps its chunks for the next question,
  so they would carry this question's scores. `dict(...)` makes a copy.
- Forgetting `[::-1]`: you then keep the five **worst** chunks.

Press **Check**.
:::

:::step{type=history title="Reading the question and the passage together"}
:::before{title="One vector per passage"}
Search systems compared representations made ahead of time: word counts, then embeddings. Fast, but each passage was
represented without knowing the question.
:::

In **2016** Microsoft released **MS MARCO**, a dataset of real Bing search questions with passages that people marked as
answering them, big enough to train neural rankers. In **2018** Google published **BERT**, a transformer that can read two
texts side by side. In **2019** Rodrigo Nogueira and Kyunghyun Cho fed BERT a question and a passage together and asked
for one number; on MS MARCO it beat the previous best result by 27% (relative, on the leaderboard's main measure).

In **2020** Microsoft's **MiniLM** showed how to train a small transformer to copy a large one, and small cross-encoders
trained this way became fast enough for an ordinary CPU. From **2023**, hosted reranking services (Cohere's, for example)
made "retrieve, then rerank" a standard part of RAG.

:::solved
**Precision where it counts.** The fast search only has to put the right chunk somewhere in the top 20; the careful
reader puts it first.
:::

:::timeline
- **2016** MS MARCO: real questions, judged passages.
- **2018** BERT reads two texts together.
- **2019** BERT as a reranker (Nogueira and Cho).
- **2020** MiniLM: small transformers that copy big ones.
- **2023** Hosted reranking becomes a standard RAG step.
:::
:::

:::step{type=concept title="Two stages" file="10-rerank/fieldbook.py" line="353-357"}
Put the two together:

```text
question
   |
   v
stage 1: hybrid search over every chunk      fast, wide:    20 candidates
   |
   v
stage 2: cross-encoder over 20 candidates    slow, careful: the best 5
```

:::diagram{name="rag-two-stage"}
The real jeep question. Hybrid search, which lost FM-6.2 in chapter 9, still has it 8th among its 20 candidates; the
cross-encoder reads all 20 with the question and puts FM-6.2 first.
:::

Stage 1 only has to get the right chunk **into** the 20 (its hit rate at 20); stage 2 has to put it **first**. Each stage
does what it is good at.

`first` and `final` are the two dials. More candidates catch more, and cost more reranking time: about 70 ms each here.
One limit of this lab's `hybrid()`: it fuses dense search's top 20 with BM25's top 20, so it can never return more than
40 candidates (for the 26 test questions, at most 35).
:::

:::step{type=task task=two_stage title="Your turn: wide, then careful" file="10-rerank/fieldbook.py" line="353-357"}
Write `two_stage(question, index, first=20, final=5)`:

1. Get the candidates: `index.hybrid(question, k=first)`.
2. Return `rerank(question, candidates, top_n=final)`.

It fits in one line. The usual slip: passing `final` to `hybrid` and `first` to `rerank`, the wrong way round, so only
5 candidates are ever read.

```bash run
cd /workspace/10-rerank && python rerank_demo.py
```

Press **Check**.
:::

:::step{type=try title="The careful reader at work"}
```text
$ python rerank_demo.py
A night patrol cannot reach base on the radio. What happens?
  hybrid top 5:   ['FM-9.2', 'R-0403', 'FM-2.2', 'FM-1.3', 'R-0408']
  reranked top 5: ['FM-2.2 (3.7)', 'R-0403 (3.1)', 'FM-9.2 (2.1)', 'FM-1.3 (-0.9)', 'FM-3.3 (-3.5)']
  reranking 20 candidates took 2490 ms

Who is allowed into the core zone?
  hybrid top 5:   ['FM-1.1', 'FM-6.4', 'FM-2.1', 'FM-6.2', 'FM-9.2']
  reranked top 5: ['FM-6.4 (7.0)', 'FM-1.1 (4.0)', 'FM-9.2 (-1.2)', 'FM-2.1 (-2.2)', 'FM-6.2 (-8.9)']
  reranking 20 candidates took 1694 ms

Can tourists get out of the jeep to take photos?
  hybrid top 5:   ['FM-1.2', 'R-0305', 'FM-2.2', 'FM-3.3', 'FM-6.4']
  reranked top 5: ['FM-6.2 (-6.6)', 'R-0305 (-6.8)', 'FM-6.3 (-10.5)', 'R-0310 (-10.6)', 'FM-6.5 (-10.6)']
  reranking 20 candidates took 1798 ms
```

The ids and scores will be the same on your machine; the times will differ a little.

1. **The night patrol.** Hybrid search put FM-9.2 (radios and phones) first. The reranker prefers **FM-2.2 Night
   patrols**, which says exactly what happens when a night patrol misses two check-ins, then R-0403, the night a patrol
   pair missed two check-ins because its radio battery failed. Both answer this question better.
2. **The core zone.** FM-6.4 (research permits allow entry into the core zone) moves above FM-1.1 (the zone
   definitions). Either can answer. Notice the gap in the scores: 7.0 and 4.0, then -1.2 and below. The reranker is sure
   about two chunks and not the rest.
3. **The jeep, repaired.** FM-6.2 Visitor rules, lost by fusion in chapter 9, was still among the 20 candidates (8th),
   and the reranker puts it back on top. Its score is low (-6.6): the question and the section share almost no words, and
   this small model leans on shared words. But -6.6 is the highest of the 20, and ranking only needs the order.

**The price.** Reranking 20 chunks took 1.7 to 2.5 seconds a question in this run, on the lab machine's 2 CPUs. The
first question also paid about 0.8 seconds to load the model; once loaded, we measured about 1.4 seconds, roughly 70 ms a
chunk. Hybrid search took under 0.1 seconds. For a ranger asking a question on a phone, 1.5 seconds is acceptable; for
a search box that updates as you type, it is not. Chapter 12 measures the gain on all 26 questions, so you can decide
whether it is worth it.
:::

:::step{type=predict title="Guess first"}
:::question
You raise `first` from 20 to 30. What happens?
:::
- [x] Reranking takes about 1.5 times as long, and can catch a right chunk that the fused list ranked 21st to 30th
- [ ] Nothing changes, because the reranker only returns the top 5
- [ ] It gets faster, because fewer chunks are left for stage 2
:::explain
Reranking time grows with the number of candidates: 30 instead of 20 is about 1.5 times the work. Raising `first` much
further does nothing in this lab: `hybrid()` never returns more than 40 candidates (dense top 20 plus BM25 top 20).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why can the chunks' vectors be computed ahead of time, but not the cross-encoder's scores?
:::
- [ ] The cross-encoder is too large to store
- [x] A cross-encoder score depends on the question and the chunk together, and the question is only known when it is asked
- [ ] Scores change every day
:::explain
That is the whole trade: computed ahead means fast, reading both together means more accurate.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In a two-stage search, what must stage 1 be good at?
:::
- [ ] Putting the right chunk first
- [x] Getting the right chunk anywhere into its candidates
- [ ] Being exact
:::explain
Stage 1 is judged by its hit rate at `first`, stage 2 by what comes first. Chapter 12 measures both.
:::
:::

:::step{type=deep-dive title="Go deeper: reranking in production"}
**Hardware.** A GPU (graphics processor) runs these models much faster. The model's documentation (from the
sentence-transformers project) lists about 1,800 passages a second for this model on one data-centre GPU, an Nvidia
V100. On CPUs, keep `first` small (10 to 30) or use a smaller model.

**Bigger rerankers.** BAAI's bge-reranker models and hosted reranking APIs are slower and often better, and some handle
many languages. Language models themselves can rerank ("which of these passages answers the question?"), at a much
higher price per question.

**Late interaction.** ColBERT (2020) keeps one vector per word piece of every chunk and compares them piece by piece when
the question arrives: a middle way between bi-encoders and cross-encoders. Qdrant, Vespa and Weaviate can store such
multi-vectors.

**Caching.** Rangers ask the same questions again and again. Storing the final answer for a question (after lower-casing
it and trimming spaces) saves both the reranking and the model call the next time.
:::

:::step{type=recap}
You can now:

- explain the difference between a bi-encoder and a cross-encoder;
- rerank candidates by scoring the question and each chunk together;
- build a two-stage retriever: hybrid search for candidates, reranking for the order;
- weigh reranking's gain in quality against its cost in time (about 70 ms a candidate on this lab's 2 CPUs).

Next, chapter 11: turning the best chunks into an answer that cites its sources, or honestly says it found nothing.

:::photo{src="/lesson-images/rag/rag-10-notes.webp" alt="Handwritten notes about reranking: A bi-encoder turns each text into its own vector. A cross-encoder reads the question and a chunk together. Stage one is fast and wide; stage two is slow and careful. Stage one only has to get the answer into the candidates. Compare rerank scores within one question, not across. Here, each candidate cost about 70 ms on two CPUs." ai="true"}
One page of notes for this chapter.
:::
:::
