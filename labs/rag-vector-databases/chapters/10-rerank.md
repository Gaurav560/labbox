:::step{type=story title="A second, careful reading"}
Look at how every search so far has worked. The chunk was turned into a vector **before** anyone asked anything; the
question was turned into a vector on its own; then two points were compared. The model that made the chunk's vector never
saw the question. It had to squeeze everything the chunk might ever be asked about into 384 numbers.

That is why the "jeep" question went wrong in chapter 9, and why "big cat" in chapter 3 scored FM-4.2 only a little above
"Finding a dead animal". The search was fast because it was shallow.

There is a slower, deeper way: give a model the question **and** a chunk **together**, and let it read both and say how
well the chunk answers the question. Doing that for all 55 chunks for every question would be too slow, but for the 20
candidates that hybrid search already found, it is affordable. This two-step pattern, a fast wide search followed by a
slow careful judge, is called **reranking**.

:::mission
Rerank hybrid search's candidates with a cross-encoder, then build the two-stage pipeline Fieldbook will use from now on,
and measure what the extra care costs in time.
:::
:::

:::step{type=concept title="Bi-encoder and cross-encoder" file="10-rerank/fieldbook.py" line="338-342"}
Two kinds of model, two ways to compare a question and a text:

| | Bi-encoder (chapters 2 to 9) | Cross-encoder (this chapter) |
|---|---|---|
| reads | the question alone, the chunk alone | the question and the chunk **together** |
| outputs | one vector each | one relevance score for the pair |
| chunk work done | once, ahead of time | again for every question |
| speed | microseconds per comparison | tens of milliseconds per pair on a CPU |
| quality | good | better: it sees which words answer which |

Fieldbook's cross-encoder is **ms-marco-MiniLM-L-6-v2**: a small transformer (6 layers) trained on hundreds of thousands
of real web search questions, each with passages people judged relevant. It is already in your lab machine.

Its scores are not cosines: they are unbounded numbers where higher means more relevant. Roughly, above 0 is a good
match and below -5 is a poor one, but, as with cosines, a score is most useful **compared with the other candidates for
the same question**.

`reranker().rerank(question, texts)` returns one score per text, in the same order as the texts.
:::

:::step{type=task task=rerank title="Your turn: score question and chunk together" file="10-rerank/fieldbook.py" line="345-350"}
Write `rerank(question, chunks, top_n=5)`:

1. `scores = list(reranker().rerank(question, [chunk_text(c) for c in chunks]))`.
2. Order the positions by score, highest first (`np.argsort(scores)[::-1]`), and keep `top_n` of them.
3. Return a **copy** of each of those chunks with its score added: `dict(chunks[i], rerank=float(scores[i]))`.

Copies matter: the index keeps using its chunks for the next question, so do not write into them. Press **Check**.
:::

:::step{type=history title="Reading the question and the passage together"}
:::before{title="One vector per passage"}
Search systems compared precomputed representations: word counts, then embeddings. Fast, but the passage was represented
without knowing the question.
:::

In **2016** Microsoft released **MS MARCO**, a dataset of real Bing search questions with passages that people marked as
answering them, big enough to train neural rankers. In **2018** Google published **BERT**, a transformer that reads two
texts side by side. Rodrigo Nogueira and Kyunghyun Cho fed it a question and a passage together in **2019** and asked for
one number: the jump in quality on MS MARCO was the largest the benchmark had seen. Smaller copies trained to imitate
large models (MiniLM, **2020**) made cross-encoders fast enough for a CPU, and hosted reranking services (**2023**) made
"retrieve, then rerank" a standard part of RAG.

:::solved
**Precision where it counts.** The fast search only has to put the right chunk somewhere in the top 20; the careful
reader puts it first.
:::

:::timeline
- **2016** MS MARCO: real questions, judged passages.
- **2018** BERT reads two texts together.
- **2019** BERT as a reranker (Nogueira and Cho).
- **2020** MiniLM: small enough for a CPU.
- **2023** Reranking becomes a standard RAG step.
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
Hybrid search narrows 55 chunks to 20 candidates in milliseconds; the cross-encoder reads each with the question and keeps 5.
:::

Stage 1 only has to get the right chunk **into** the 20 (its hit rate at 20); stage 2 has to put it **first**. Each stage
does what it is good at. `first` and `final` are the two dials: more candidates catch more, and cost more reranking time.
:::

:::step{type=task task=two_stage title="Your turn: wide, then careful" file="10-rerank/fieldbook.py" line="353-357"}
Write `two_stage(question, index, first=20, final=5)`: get `index.hybrid(question, k=first)` and return
`rerank(question, those, top_n=final)`. One line.

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
  reranking 20 candidates took 2393 ms

Who is allowed into the core zone?
  hybrid top 5:   ['FM-1.1', 'FM-6.4', 'FM-2.1', 'FM-6.2', 'FM-9.2']
  reranked top 5: ['FM-6.4 (7.0)', 'FM-1.1 (4.0)', 'FM-9.2 (-1.2)', 'FM-2.1 (-2.2)', 'FM-6.2 (-8.9)']
  reranking 20 candidates took 1698 ms

Can tourists get out of the jeep to take photos?
  hybrid top 5:   ['FM-1.2', 'R-0305', 'FM-2.2', 'FM-3.3', 'FM-6.4']
  reranked top 5: ['FM-6.2 (-6.6)', 'R-0305 (-6.8)', 'FM-6.3 (-10.5)', 'R-0310 (-10.6)', 'FM-6.5 (-10.6)']
  reranking 20 candidates took 1901 ms
```

1. **The night patrol.** Hybrid search put FM-9.2 (radios and phones) first. The reranker prefers **FM-2.2 Night
   patrols**, which says exactly what happens when a night patrol misses two check-ins, then R-0403, the night the pair
   on beat B-08 lost radio contact. Both are better answers to this question.
2. **The core zone.** FM-6.4 (research permits allow entry into the core zone) moves above FM-1.1 (the zone
   definitions). Either can answer; notice how far apart the scores are (7.0 and 4.0 against -1.2 and below): the
   reranker is sure about two chunks and not the rest.
3. **The jeep, repaired.** FM-6.2 Visitor rules, lost by fusion in chapter 9, was still among the 20 candidates, and the
   reranker puts it back on top. Its score is low (-6.6): this small model is guided a lot by shared words, and the
   question shares few with the section. But it is the highest of the 20, which is what ranking needs.

**The price: about 2 seconds a question** on your two CPUs, for 20 chunks (about 100 ms a chunk). Hybrid search took
about 20 ms. For a ranger asking a question on a phone, 2 seconds is acceptable; for a search box that updates as you
type, it is not. Chapter 12 measures the gain on all 26 questions, so you can decide whether it is worth it.
:::

:::step{type=predict title="Guess first"}
:::question
You raise `first` from 20 to 55 (every chunk). What happens?
:::
- [x] Reranking takes about 2.75 times as long, and catches chunks stage 1 had ranked below 20
- [ ] Nothing changes, because the reranker only looks at the top 5
- [ ] It gets faster, because hybrid search is skipped
:::explain
Reranking time grows with the number of candidates. Reranking everything is only possible because Fieldbook is tiny.
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
That is the whole trade: precomputed means fast, joint reading means accurate.
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
Stage 1 is judged by hit rate at `first`, stage 2 by what comes first. Chapter 12 measures both.
:::
:::

:::step{type=deep-dive title="Go deeper: reranking in production"}
**Hardware.** On a GPU, a MiniLM cross-encoder scores hundreds of pairs in tens of milliseconds. On CPUs, keep `first`
small (10 to 30) or use a smaller model.

**Bigger rerankers.** BAAI's bge-reranker models, and hosted reranking APIs, are slower and better, and handle more
languages. Language models themselves can rerank ("which of these passages answers the question?"), at a much higher
price per question.

**Late interaction.** ColBERT (2020) keeps one vector per word of every chunk and compares word by word at query time: a
middle ground between bi-encoders and cross-encoders, supported by several vector databases.

**Caching.** Rangers ask the same questions again and again. Caching the final answer for a normalized question saves
both the reranking and the model call.
:::

:::step{type=recap}
You can now:

- explain the difference between a bi-encoder and a cross-encoder;
- rerank candidates by scoring the question and each chunk together;
- build a two-stage retriever: hybrid search for candidates, reranking for the order;
- weigh reranking's gain in quality against its cost in time.

Next, chapter 11: turning the best chunks into an answer that cites its sources, or honestly says it found nothing.

:::photo{src="/lesson-images/rag/rag-10-notes.webp" alt="Handwritten notes about reranking: Bi-encoder: one vector each; Cross-encoder: reads both together; Fast and wide, then slow and careful; Top 20 in, best 5 out; About 2 s on two CPUs" ai="true"}
One page of notes for this chapter.
:::
:::
