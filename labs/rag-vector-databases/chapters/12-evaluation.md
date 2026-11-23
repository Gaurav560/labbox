:::step{type=story title="Is it actually better?"}
You have built four ways for Fieldbook to find chunks: keyword counting (chapter 1), dense search (chapter 3), hybrid
search (chapter 9) and hybrid search with reranking (chapter 10). Each chapter showed a few questions where the new way
looked better. A few hand-picked questions prove nothing: chapter 9 showed hybrid search fixing CT-112 and breaking the
jeep question in the same run.

Teams that skip measurement end up changing chunk sizes, models and settings by feel, and never know whether yesterday's
change helped. The cure is old and simple: a fixed set of test questions with known right answers, and a number that says
how well each pipeline does on all of them.

:::mission
Write two standard retrieval measures, hit rate and mean reciprocal rank, then run all four of Fieldbook's pipelines on
the same 26 questions and decide, with numbers, which one Fieldbook should use.
:::
:::

:::step{type=concept title="A golden set" file="12-evaluation/evaluate.py" line="1-12"}
`data/questions.json` holds 26 questions a ranger might ask, each with the ids of the chunks that answer it:

```json
{"question": "What should I do if a big cat is right in front of me on the trail?", "answers": ["FM-4.2"]},
{"question": "What did CT-112 record?", "answers": ["R-0301"]},
{"question": "Who is allowed into the core zone?", "answers": ["FM-1.1", "FM-6.4"]},
```

This is a **golden set**. A good one:

| Rule | Why |
|---|---|
| uses the users' words, not the documents' | "big cat", "jeep" and "cook dinner" are how people ask |
| includes the hard kinds | codes (CT-112), paraphrases, questions with two right answers |
| is written before tuning | otherwise you tune to the test |
| never changes casually | so that this month's number compares with last month's |

26 questions is small; real teams use 100 to 1,000. But even 26 show differences that a demo hides.
:::

:::step{type=concept title="Hit rate at k" file="12-evaluation/fieldbook.py" line="384-389"}
The first question to ask of a retriever: **did the right chunk make it into what the model will read?** If Fieldbook
sends the top 5 to the model, a question is a **hit** when any of the 5 is a right id.

```text
hit rate at k = (questions with a right id in their first k results) / (all questions)
```

`hit@1` asks for the right chunk in first place; `hit@5` anywhere in the first five. A question with two right answers
(the core zone) is a hit if either appears.
:::

:::step{type=task task=hit_rate title="Your turn: hit rate at k" file="12-evaluation/fieldbook.py" line="384-389"}
Write `hit_rate(results, expected, k=5)`. `results` has one list of ids per question (best first), `expected` one list of
right ids per question. Count the questions where `set(got[:k]) & set(good)` is not empty, and divide by the number of
questions.

Press **Check**.
:::

:::step{type=concept title="Mean reciprocal rank" file="12-evaluation/fieldbook.py" line="392-396"}
Hit rate at 5 does not care whether the right chunk is first or fifth, but the model does: it reads the first source most
carefully, and chapter 11's refusal rule looks only at the first. **Mean reciprocal rank** rewards putting it first:

:::trace{title="MRR over four questions"}
| question | first right id at position | reciprocal rank |
|---|---|---|
| 1 | 1 | 1/1 = 1.00 |
| 2 | 3 | 1/3 = 0.33 |
| 3 | 2 | 1/2 = 0.50 |
| 4 | not found | 0 |
| MRR | | (1.00 + 0.33 + 0.50 + 0) / 4 = 0.46 |
:::

Only the **first** right id counts: a question with right ids at positions 2 and 3 scores 1/2, not 1/2 + 1/3. An MRR of
1.0 means the right chunk was always first.
:::

:::step{type=task task=mrr title="Your turn: mean reciprocal rank" file="12-evaluation/fieldbook.py" line="392-396"}
Write `mrr(results, expected)`: for each question, walk its results with `enumerate(got, start=1)`; at the first id in
the right answers add `1 / rank` to a total and `break`. Return the total divided by the number of questions.

```bash run
cd /workspace/12-evaluation && python evaluate.py
```

Press **Check**. (The script runs the reranker on all 26 questions: give it about a minute.)
:::

:::step{type=history title="Measuring search, from Cranfield to RAG"}
:::before{title="Opinions"}
Early retrieval systems were judged by demonstrations and by their builders' confidence. Two systems could not be
compared, because nobody had tested them on the same questions.
:::

In the **1960s** Cyril Cleverdon at the College of Aeronautics in Cranfield, England, ran the **Cranfield experiments**:
1,400 documents, a set of questions, and people's judgements of which documents answered which question. For the first
time, indexing methods were compared on the same test collection with numbers, and some cherished methods lost. In
**1992** the US National Institute of Standards and Technology started **TREC**, a yearly evaluation that gave
researchers shared collections and measures; mean reciprocal rank was used there to score question answering (**1999**).
RAG brought the same practice to new teams, along with tools that use a language model to judge answers (RAGAS, **2023**).

:::solved
**Decisions by numbers.** A golden set turns "it feels better" into "hit@1 went from 77% to 88%", and catches the change
that quietly made things worse.
:::

:::timeline
- **1960s** The Cranfield experiments.
- **1992** TREC begins.
- **1999** MRR scores question answering at TREC.
- **2023** RAG evaluation tools.
:::

The entrance of the US National Institute of Standards and Technology, which has run TREC, the yearly test of search systems, since 1992.

:::photo{src="/lesson-images/rag/nist.webp" alt="A blue sign for the National Institute of Standards and Technology at a gate, with trees behind" credit="G. Edward Johnson" license="CC BY 4.0" source="https://commons.wikimedia.org/wiki/File%3ANIST_sign_Gaithersburg_MD_2026-10-21_10-03-45.jpg"}
Gate A of NIST in Gaithersburg, Maryland.
:::
:::

:::step{type=try title="Four pipelines, 26 questions"}
```text
$ python evaluate.py
26 questions

pipeline                        hit@1  hit@5    MRR   ms/q
keywords (chapter 1)              50%    77%   0.62      1
    missed: What should I do if a big cat is right in front of me on the trail?
    missed: What did CT-112 record?
    missed: When is the park shut because of the rains?
    missed: Is it all right to cook dinner at the gate in March?
    missed: Can tourists get out of the jeep to take photos?
    missed: What time does the morning safari start?
dense (chapter 3)                 77%    92%   0.85     23
    missed: What did CT-112 record?
    missed: Which report mentions CT-104?
hybrid (chapter 9)                58%    92%   0.74     27
    missed: Is it all right to cook dinner at the gate in March?
    missed: Can tourists get out of the jeep to take photos?
hybrid + rerank (chapter 10)      88%   100%   0.94   1723
```

The misses (outside the top 5) tell the story of the whole course:

1. **Keywords** miss every paraphrase ("big cat", "shut because of the rains", "cook dinner") and, surprisingly,
   CT-112: counting words gives "record" the same weight as "CT-112", and manual sections that say "record" come first.
   BM25's rarity weighting exists for exactly this.
2. **Dense** search misses only the two **code** questions.
3. **Hybrid** fixes both codes, but loses two paraphrases, the RRF effect from chapter 9, and its hit@1 **drops** from
   77% to 58%: BM25 pushes chunks that share common words up into first place.
4. **Hybrid + rerank** misses nothing in the top 5 and is right first time for 88% of the questions, with the best MRR
   (0.94). It is also **75 times slower** (1.7 seconds against 23 ms).

So, with numbers:

| If Fieldbook needs | Choose | Because |
|---|---|---|
| the best answers, a ranger can wait 2 s | hybrid + rerank | 100% at 5, 88% first time |
| instant results (search as you type) | dense | 92% at 5 in 23 ms, but codes need a fallback |
| never hybrid alone | | on these questions it is worse than dense at first place |

Fieldbook uses hybrid + rerank. Notice the third row: without this table, hybrid search "obviously" looked like an
improvement.
:::

:::step{type=predict title="Guess first"}
:::question
You add 10 more questions, all about camera trap codes. What happens to the gap between dense and hybrid?
:::
- [x] Hybrid gains on dense: codes are where BM25 helps
- [ ] Nothing: the measures are averages
- [ ] Dense gains: codes are about meaning
:::explain
Which pipeline wins depends on the questions you test with, which is why the golden set must look like real use.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A pipeline has hit@5 of 100% and MRR of 0.4. What does that tell you?
:::
- [x] The right chunk is always in the top 5 but often not first: a reranker could help
- [ ] It is perfect
- [ ] It misses 60% of the questions
:::explain
An MRR of 0.4 means the first right chunk is typically around position 2 or 3.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why must the golden set use the users' own words?
:::
- [ ] The embedding model needs it
- [x] Questions copied from the documents' wording are easy for every pipeline and hide the paraphrase failures real users hit
- [ ] To make the questions shorter
:::explain
"How often do camera trap batteries need replacing?" is easy; "how often do the trail cameras need new cells?" is the real test.
:::
:::

:::step{type=deep-dive title="Go deeper: evaluating a RAG system"}
**Retrieval and answers are measured separately.** This chapter measured retrieval. Answer quality needs its own checks:
is the answer **faithful** (supported by the sources), does it **answer** the question, are the **citations** right? A
language model can grade these against a rubric ("LLM as a judge"), checked against human grades on a sample.

**Build the golden set from real questions.** Log what users ask (with permission), pick a few hundred, and have someone
who knows the documents mark the right chunks.

**Run it on every change.** Chunking, model, prompt, index settings: put the evaluation in your tests, and refuse changes
that lower the numbers, as you would refuse a change that makes a test fail.

**Watch the misses, not just the averages.** The list of missed questions above taught more than the four numbers.
:::

:::step{type=recap}
You can now:

- build a golden set of questions with known right chunks;
- compute hit rate at k and mean reciprocal rank;
- compare retrieval pipelines on the same questions and read their misses;
- choose a pipeline with numbers, including its cost in time.

Next, chapter 13: Fieldbook as a web service.

:::photo{src="/lesson-images/rag/rag-12-notes.webp" alt="Handwritten notes about evaluation: A golden set in the users' words; Hit rate: in the top k?; MRR: how near the top?; Read the misses; Choose with numbers" ai="true"}
One page of notes for this chapter.
:::
:::
