:::step{type=story title="An answer you can check"}
Retrieval is done: for any question, Fieldbook can now find the five chunks most likely to answer it, hybrid search
for candidates and the reranker for the order. Now the "generation" part of RAG: turning chunks into an answer a ranger can act on at
2 a.m.

Two things make that answer trustworthy, and both are your design, not the model's:

1. **It shows its sources.** Every fact carries a number pointing to the chunk it came from, so anyone can check it.
2. **It says when it does not know.** If the manual and reports do not cover a question, Fieldbook says so instead of
   inventing something plausible. Sometimes it does not even need to ask the model.

:::mission
Number the sources in the prompt so the model can cite them, then add a gate: when the best chunk is clearly unrelated,
answer "not found" without calling the model at all.
:::
:::

:::step{type=concept title="Numbered sources, and rules for using them" file="11-grounded-answers/fieldbook.py" line="358-370"}
Chapter 1's prompt listed sections by their ids. This prompt numbers them, because short numbers are easy for a model to
cite and easy for a program to check:

```text
Sources:

[1] FM-5.3: Fighting a ground fire
Ground fires are fought by a crew of at least four, ... Never fight a crown fire, one that has reached the tops of the
trees: move everyone to a fire line or a burnt area and wait for the fire to reach it.

[2] R-0409: Patrol report R-0409, 2026-04-25, beat B-05
Crown fire on the southern slope of B-05 during strong wind. The crew withdrew to the fire line ...

Question: What should the crew do when the treetops are burning?
```

The system message, `GROUNDED`, sets the rules:

| Rule | Why |
|---|---|
| answer only from the numbered sources | the model's general knowledge about fires is not the sanctuary's procedure |
| cite each fact with its number, like [2] | every claim can be traced and checked |
| if the sources do not contain the answer, reply exactly NOT_FOUND | an exact sentence a program can recognise |
| at most four sentences | a ranger on a radio needs the instruction, not an essay |

The answer also returns the sources' ids, so the app can show "from FM-5.3 and R-0409" with links.
:::

:::step{type=task task=grounded_prompt title="Your turn: numbered sources" file="11-grounded-answers/fieldbook.py" line="365-370"}
Write `grounded_messages(question, sources)`: the system message `GROUNDED`, then a user message made of `"Sources:"`, a
blank line, every source as `[1] FM-5.3: Fighting a ground fire` on one line and its text on the next (numbered from 1
with `enumerate(sources, start=1)`, separated by blank lines), a blank line, and `"Question: "` with the question.

Press **Check**.
:::

:::step{type=concept title="Do not ask when there is nothing to find" file="11-grounded-answers/fieldbook.py" line="362-379"}
Some questions are simply not covered: the entry fee for foreign tourists, the capital of France. Retrieval still returns
five chunks (it always returns the nearest ones, chapter 8 showed that), but they are about something else. You could
send them to the model and trust it to say "not found". It usually does, and you pay for the call each time.

The reranker's score gives a cheaper first line of defence. These are the best scores for the 26 test questions and for
eight questions the documents do not answer:

| Questions | Best reranker score, lowest to highest |
|---|---|
| answered by the documents | -8.0, -7.6, -6.6, 0.1, 1.2, 1.9, ... up to 9.9 |
| not in the documents | -11.0, -10.7, -9.6, -8.7, -6.9, 0.6, 1.0, 3.3 |

The two groups overlap: "How many tigers live in Vanrai?" (0.6) and "Who is the Range Forest Officer?" (3.3) find chunks
that **sound** relevant, and three real questions in everyday words score as low as -8.0. No threshold separates them
perfectly. So the gate is set where it is safe: `MIN_RERANK = -9.0` stops the three clearly unrelated questions (the
capital of France, renewing a driving licence, a foreign tourist's entry fee) and never blocks a real one. Everything
above it goes to the model, whose instructions handle the rest.

That is a general pattern: a cheap rule for the obvious cases, the expensive model for the subtle ones.
:::

:::step{type=task task=refuse_unsure title="Your turn: no answer without a source" file="11-grounded-answers/fieldbook.py" line="373-379"}
Write `answer(question, sources, client)`:

1. If there are no sources, or `sources[0]["rerank"] < MIN_RERANK`, return
   `{"answer": NOT_FOUND, "sources": []}` without calling the model.
2. Otherwise call `client.chat.completions.create(model="lab-chat", messages=grounded_messages(question, sources),
   temperature=0)`.
3. Return `{"answer": <the reply's text>, "sources": [each source's "id"]}`.

`temperature=0` makes the model pick its most likely words, so the same question gives (nearly) the same answer.

```bash run
cd /workspace/11-grounded-answers && python ask.py
```

Press **Check**.
:::

:::step{type=try title="Four questions, four behaviours"}
```text
$ python ask.py
What should the crew do when the treetops are burning?
  best source: FM-5.3 (4.0)
  When the treetops are burning, the crew should never fight a crown fire. Instead, they should move everyone to a fire line or a burnt area and wait for the fire to reach it [1].
  sources: ['FM-5.3', 'R-0409', 'FM-3.3', 'R-0306', 'FM-5.1'] 

Which animal injures the most people?
  best source: FM-4.5 (6.8)
  The sloth bear injures more people in India than any other wild animal, primarily because it attacks when surprised at close range [1].
  sources: ['FM-4.5', 'FM-4.1', 'FM-4.6', 'FM-8.1', 'FM-7.3'] 

How many tigers live in Vanrai?
  best source: FM-4.3 (0.6)
  I could not find this in the Fieldbook.
  sources: ['FM-4.3', 'FM-7.3', 'FM-4.2', 'R-0410', 'FM-4.6'] 

What is the entry fee for a foreign tourist?
  best source: FM-1.1 (-9.6)
  I could not find this in the Fieldbook.
  sources: []
```

Four questions, four different paths through `answer`:

1. **The treetops.** Best source FM-5.3 (4.0): the gate opens, the model answers from it and cites **[1]**. The answer
   repeats the manual's rule (never fight a crown fire, move to a fire line) instead of generic fire advice.
2. **The most injuries.** FM-4.5 scores 6.8; the answer names the sloth bear and cites [1]. You can open FM-4.5 and
   check every word.
3. **How many tigers.** The best source, FM-4.3 about leopards near villages, scores 0.6: above the gate, so the model is
   asked. The sources never give a number, and the model follows its rule: "I could not find this in the Fieldbook."
   The second line of defence worked. (Notice that `sources` still lists five chunks: the app should hide them when the
   answer is NOT_FOUND; the deep dive comes back to this.)
4. **The entry fee.** Best source -9.6, below `MIN_RERANK`: Fieldbook answers at once, **without calling the model**,
   and lists no sources. That question cost nothing.

One more, from the "Guess first" step below:

```text
$ python ask.py "Who is the Range Forest Officer?"
Who is the Range Forest Officer?
  best source: FM-8.2 (3.3)
  I could not find this in the Fieldbook.
  sources: ['FM-8.2', 'FM-7.3', 'FM-1.3', 'FM-4.7', 'FM-8.1']
```

FM-8.2 mentions the Range Forest Officer, so the reranker scores it well, but it never gives a name. A model without
the "only from the sources" rule might well have invented one.

The answer to the second question: a sloth bear, here with her cubs riding on her back.

:::photo{src="/lesson-images/rag/sloth-bear.webp" alt="A black sloth bear walking on a forest track with two cubs on her back" credit="Rohit Sharma" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ASloth_Bear_with_Cubs_at_Bor_tiger_reserve%2C_Maharashtra%2C_India.jpg"}
A sloth bear with cubs in Bor Tiger Reserve, Maharashtra.
:::
:::

:::step{type=history title="Footnotes, citations and grounding"}
:::before{title="Trust me"}
An answer without sources asks you to trust whoever wrote it. For a fluent language model, that is exactly the problem:
it sounds equally sure when it is right and when it is inventing.
:::

Scholars have cited their sources for centuries; the footnote became standard in printed books in the **17th and 18th
centuries** so that readers could check claims for themselves. Wikipedia made "citation needed" famous (**2000s**). For
language models, the RAG paper (**2020**) grounded answers in retrieved passages, and in **2021** OpenAI's WebGPT trained
a model to browse and quote its sources while answering. Since **2023** assistants that cite their sources have become
the expected form for answering from documents, and "answer only from the sources, and say when they are silent" is the
first rule of nearly every RAG prompt.

:::solved
**Answers that can be checked, and silence when there is nothing to say.** Trust comes from being able to verify, not
from sounding sure.
:::

:::timeline
- **1700s** Footnotes become standard in print.
- **2000s** Wikipedia's "citation needed".
- **2020** RAG grounds answers in passages.
- **2021** WebGPT quotes its sources.
- **2023** Cited answers become the norm for document assistants.
:::
:::

:::step{type=predict title="Guess first"}
:::question
"Who is the Range Forest Officer?" passes the gate (its best chunk scores 3.3). The sources mention the officer's duties
but never a name. What should a good answer be?
:::
- [ ] The most likely name for an Indian forest officer
- [x] "I could not find this in the Fieldbook.", because the sources do not contain a name
- [ ] A description of the officer's duties, presented as the answer
:::explain
The gate passes it; the instructions must catch it. Try it with `python ask.py "Who is the Range Forest Officer?"`.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why number the sources [1], [2] instead of only using their ids?
:::
- [x] Short numbers are easy for the model to cite and for a program to map back to the chunks
- [ ] Ids cannot be put in a prompt
- [ ] The model reads numbers faster
:::explain
Either works; numbers keep citations short and uniform. The app maps [2] back to R-0409 using the sources list.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why not set MIN_RERANK higher, say 0, to block more unanswerable questions?
:::
- [ ] It would make answers slower
- [x] It would also block real questions in everyday words (three scored between -8 and -6.6), and refusing a real question is a failure too
- [ ] The reranker cannot score above 0
:::explain
A threshold trades one error for another. Measure both kinds before choosing, as the table above does.
:::
:::

:::step{type=deep-dive title="Go deeper: grounded answers in production"}
**Hide sources for "not found".** When the answer is NOT_FOUND, show no sources: listing five unrelated
chunks under "I could not find this" confuses people.

**Check the citations in code.** Parse the [n] markers, make sure every number exists, and flag answers with no citation
at all. Some teams go further and check that each cited source actually contains the claim (another model call).

**Show the sources.** Under the answer, list the cited chunks with their titles; one tap opens the section. Rangers trust
an assistant more when they can see where an answer came from.

**Long sources.** Put the best source first and last-but-not-least: models read the start and end of a prompt most
carefully. Five chunks of 60 to 90 words are well within a small model's comfort.

**Never let sources give orders.** A document can contain text like "ignore your instructions". Keep the rules in the
system message, the documents in the user message as quoted data, and treat what comes back as untrusted.
:::

:::step{type=recap}
You can now:

- give the model numbered sources and rules for citing them;
- make "not found" an exact, recognisable answer;
- gate the model with a reranker score, and choose the threshold from measured scores;
- explain why a cheap rule handles the obvious cases and the model the subtle ones.

Next, chapter 12: measuring all of Fieldbook's ways of retrieving on the same questions.

:::photo{src="/lesson-images/rag/rag-11-notes.webp" alt="Handwritten notes about grounded answers: Number the sources; Cite every fact like [2]; Not found is an answer; Gate: weak source, no model call; Cheap rule first, model second" ai="true"}
One page of notes for this chapter.
:::
:::
