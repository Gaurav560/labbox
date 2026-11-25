:::step{type=story title="An answer you can check"}
Retrieval is done. For any question, Fieldbook can now find the five chunks most likely to answer it: hybrid search finds
the candidates, and the reranker puts them in order. Now comes the "generation" part of RAG: turning those chunks into an
answer a ranger can act on at 2 a.m.

Two things make that answer trustworthy, and both are your design, not the model's:

1. **It shows its sources.** Every fact carries a number pointing to the chunk it came from, so anyone can check it.
2. **It says when it does not know.** If the manual and the reports do not cover a question, Fieldbook says so instead
   of inventing something that sounds right. Sometimes it does not even need to ask the model.

An answer built only from the documents you supply, and traceable back to them, is called a **grounded** answer.

:::mission
Number the sources in the prompt so the model can cite them, then add a gate: when the best chunk is clearly unrelated,
answer "not found" without calling the model at all.
:::
:::

:::step{type=concept title="Numbered sources, and rules for using them" file="11-grounded-answers/fieldbook.py" line="358-370"}
Chapter 1's prompt listed sections by their ids. This prompt numbers them, because short numbers are easy for a model to
cite and easy for a program to check. Here is the start of a real prompt for one question:

```text
Sources:

[1] FM-5.3: Fighting a ground fire
Ground fires are fought by a crew of at least four, ... Never fight a crown fire, one that has reached the tops of the
trees: move everyone to a fire line or a burnt area and wait for the fire to reach it.

[2] R-0409: Patrol report R-0409, 2026-04-25, beat B-05
Crown fire on the southern slope of B-05 during strong wind. The crew withdrew to the fire line ...

Question: What should the crew do when the treetops are burning?
```

The **system message** is the first message of a chat: the model treats it as standing instructions, and the user
message after it holds the sources and the question. Fieldbook's system message, `GROUNDED`, sets four rules:

| Rule | Why |
|---|---|
| answer only from the numbered sources | the model's general knowledge about fires is not the sanctuary's procedure |
| after each fact, cite its source number, like [2] | every claim can be traced and checked |
| if the sources do not contain the answer, reply exactly "I could not find this in the Fieldbook." | one exact sentence that a program can recognise (it is stored as `NOT_FOUND`) |
| at most four sentences | a ranger on a radio needs the instruction, not an essay |

The answer also returns the sources' ids, so the app can show "from FM-5.3 and R-0409" with links.
:::

:::step{type=task task=grounded_prompt title="Your turn: numbered sources" file="11-grounded-answers/fieldbook.py" line="365-370"}
Write `grounded_messages(question, sources)`. It returns a list of two messages:

1. `{"role": "system", "content": GROUNDED}`.
2. `{"role": "user", "content": ...}`, where the content is, in order:
   - `"Sources:"`, then a blank line;
   - every source as two lines: `[1] FM-5.3: Fighting a ground fire` and then its text. Number them from 1 with
     `enumerate(sources, start=1)`, and put a blank line between sources (`"\n\n".join(...)`);
   - a blank line, then `"Question: "` followed by the question.

The usual slips:

- Numbering from 0: the model then cites [0], and [1] points at the second source.
- Using `s["text"]` without the id and title line: the app can no longer show which section a number means.

Press **Check**.
:::

:::step{type=concept title="Do not ask when there is nothing to find" file="11-grounded-answers/fieldbook.py" line="362-379"}
Some questions are simply not covered: the entry fee for foreign tourists, the capital of France. Retrieval still returns
five chunks (it always returns the nearest ones; chapter 8 showed that), but they are about something else. You could
send them to the model and trust it to say "not found". It usually does, but you pay for every call.

The reranker's score gives a cheaper first line of defence. We ran the real two-stage search on all 26 test questions
and on eight questions the documents do not answer, and noted the best reranker score of each:

| Questions | Best reranker score, lowest to highest |
|---|---|
| the 26 answered by the documents | -8.0, -7.6, -6.6, 0.1, 1.2, 1.9, 2.2, ... up to 9.9 |
| 8 not in the documents | -11.0, -10.7, -9.6, -8.1, -6.9, -2.1, 0.6, 3.3 |

The eight unanswerable questions, with their scores:

| Question | Best chunk | Score |
|---|---|---|
| What is the capital of France? | FM-1.1 | -11.0 |
| How do I renew my driving licence? | FM-6.3 | -10.7 |
| What is the entry fee for a foreign tourist? | FM-1.1 | -9.6 |
| When was the sanctuary founded? | FM-5.1 | -8.1 |
| Which mobile network works best in the sanctuary? | FM-9.2 | -6.9 |
| What is the salary of a beat guard? | FM-8.2 | -2.1 |
| How many tigers live in Vanrai? | FM-4.3 | 0.6 |
| Who is the Range Forest Officer? | FM-8.2 | 3.3 |

The two groups overlap. "Who is the Range Forest Officer?" (3.3) finds a chunk that **sounds** relevant, because FM-8.2
mentions the officer, and three real questions in everyday words score as low as -8.0 (cooking at the gate, a big cat on
the trail, the jeep). No single number separates the groups perfectly.

:::diagram{name="rag-gate"}
Every dot is one question's best reranker score, from the real two-stage search. The groups overlap from -8.0 to 3.3,
so no single number separates them. The gate at -9.0 blocks no real question and keeps a margin below the lowest real
one (-8.0).
:::

So the gate is set where it is safe: `MIN_RERANK = -9.0`. On these questions it stops the three clearly unrelated ones
(the capital of France, the driving licence, the entry fee) and never blocks a real one. Everything above it goes to the
model, whose instructions handle the rest. This -9.0 belongs to this reranker and these documents: with another model or
other data, measure again.

That is a general pattern: a cheap rule for the obvious cases, the expensive model for the subtle ones.
:::

:::step{type=task task=refuse_unsure title="Your turn: no answer without a source" file="11-grounded-answers/fieldbook.py" line="373-379"}
Write `answer(question, sources, client)`. `sources` are the reranked chunks from `two_stage`, best first, each with its
`"rerank"` score. `client` is an OpenAI client; in the lab it is already pointed at the lab's model gateway, which gives
its chat model the name `lab-chat`.

1. If there are no sources, or `sources[0]["rerank"] < MIN_RERANK`, return `{"answer": NOT_FOUND, "sources": []}`
   **without** calling the model.
2. Otherwise call `client.chat.completions.create(model="lab-chat", messages=grounded_messages(question, sources),
   temperature=0)`.
3. Return `{"answer": reply.choices[0].message.content, "sources": [s["id"] for s in sources]}`.

**temperature** controls how freely the model chooses its words. At 0 it takes its most likely word each time, so the same
question gives the same answer, or very nearly.

The usual slips:

- Checking `sources[0]["rerank"]` before checking that `sources` is not empty: an empty list then raises an IndexError.
- Returning the chunks themselves under `"sources"` instead of their ids.

```bash run
cd /workspace/11-grounded-answers && python ask.py
```

Press **Check**.
:::

:::step{type=try title="Four questions, four behaviours"}
The best sources and their scores below are what the search returns every time. The answers come from the language model,
so your wording may differ a little. This is a real run; we ran it again on 25 November, in a lab machine through the
lab's model gateway, and got the same answers word for word.

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

1. **The treetops.** Best source FM-5.3 (4.0): the gate opens, and the model answers from it and cites **[1]**. The
   answer repeats the manual's rule (never fight a crown fire, move to a fire line) instead of generic fire advice.
2. **The most injuries.** FM-4.5 scores 6.8. The answer names the sloth bear, as FM-4.5 does ("The sloth bear injures
   more people in India than any other wild animal"), and cites [1]. You can open FM-4.5 and check every word.
3. **How many tigers.** The best source, FM-4.3 about leopards near villages, scores 0.6: above the gate, so the model is
   asked. The sources never give a number, and the model follows its rule and replies NOT_FOUND. The second line of
   defence worked. (Notice that `sources` still lists five chunks: the app should hide them when the answer is NOT_FOUND;
   the deep dive comes back to this.)
4. **The entry fee.** Best source -9.6, below `MIN_RERANK`: Fieldbook answers at once, **without calling the model**, and
   lists no sources. That question cost nothing.

One more, the question from the "Guess first" step below:

```text
$ python ask.py "Who is the Range Forest Officer?"
Who is the Range Forest Officer?
  best source: FM-8.2 (3.3)
  I could not find this in the Fieldbook.
  sources: ['FM-8.2', 'FM-7.3', 'FM-1.3', 'FM-4.7', 'FM-8.1']
```

FM-8.2 says that "the Range Forest Officer decides" the compensation, so the reranker scores it well, but it never gives
a name. A model without the "only from the sources" rule might well have invented one.

The answer to the second question: a sloth bear, here carrying her cubs on her back.

:::photo{src="/lesson-images/rag/sloth-bear.webp" alt="A black sloth bear walking on a forest track with two cubs on her back" credit="Rohit Sharma" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ASloth_Bear_with_Cubs_at_Bor_tiger_reserve%2C_Maharashtra%2C_India.jpg"}
A sloth bear with cubs in Bor Tiger Reserve, Maharashtra.
:::
:::

:::step{type=history title="Footnotes, citations and grounding"}
:::before{title="Trust me"}
An answer without sources asks you to trust whoever wrote it. For a fluent language model, that is exactly the problem:
it sounds equally sure when it is right and when it is inventing.
:::

Scholars have cited their sources for centuries. Printed footnotes appeared in the **1500s** and became common in
scholarly books by the **1700s**, so that readers could check claims for themselves. Wikipedia made "citation needed"
famous in the **2000s**. For language models, the RAG paper (**2020**) grounded answers in retrieved passages, and in
**2021** OpenAI's WebGPT trained a model to search the web and collect references for its answers. Since **2023**,
assistants that cite their sources have become the expected form for answering from documents, and "answer only from the
sources, and say when they are silent" is a first rule of most RAG prompts.

:::solved
**Answers that can be checked, and silence when there is nothing to say.** Trust comes from being able to verify, not
from sounding sure.
:::

:::timeline
- **1500s** Printed footnotes appear.
- **1700s** Footnotes are common in scholarly books.
- **2000s** Wikipedia's "citation needed".
- **2020** RAG grounds answers in passages.
- **2021** WebGPT answers with references.
- **2023** Cited answers become the norm for document assistants.
:::
:::

:::step{type=predict title="Guess first"}
:::question
"Who is the Range Forest Officer?" passes the gate (its best chunk scores 3.3). The sources mention the officer's role
but never a name. What should a good answer be?
:::
- [ ] The most likely name for an Indian forest officer
- [x] "I could not find this in the Fieldbook.", because the sources do not contain a name
- [ ] A description of the officer's duties, presented as the answer
:::explain
The gate lets it through; the instructions must catch it. Try it with `python ask.py "Who is the Range Forest Officer?"`.
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
- [x] It would also block real questions in everyday words (three scored between -8.0 and -6.6), and refusing a real question is a failure too
- [ ] The reranker cannot score above 0
:::explain
A threshold trades one error for another. At 0 it would block 6 of the 8 unanswerable questions, but also 3 of the 26
real ones. Measure both kinds before choosing, as the tables above do.
:::
:::

:::step{type=deep-dive title="Go deeper: grounded answers in production"}
**Hide sources for "not found".** When the answer is NOT_FOUND, show no sources: five unrelated chunks under "I could not
find this" confuse people.

**Check the citations in code.** Find the [n] markers, make sure every number exists, and flag answers with no citation
at all. Some teams go further and check that each cited source really contains the claim (another model call).

**Show the sources.** Under the answer, list the cited chunks with their titles; one tap opens the section. People trust
an assistant more when they can see where an answer came from.

**Where to put the best source.** Studies of long prompts (for example "Lost in the Middle", 2023) found that models use
information at the start and the end of a long prompt better than in the middle. Putting the best source first is a
safe habit. Fieldbook's prompt is short anyway: five chunks of 19 to 95 words.

**Never let sources give orders.** A document can contain text like "ignore your instructions". Keep the rules in the
system message and the documents in the user message as quoted data, and treat what comes back as untrusted.
:::

:::step{type=recap}
You can now:

- give the model numbered sources and rules for citing them;
- make "not found" an exact, recognisable answer;
- gate the model with a reranker score, and choose the threshold from measured scores (here -9.0, for this reranker and
  these documents);
- explain why a cheap rule handles the obvious cases and the model the subtle ones.

Next, chapter 12: measuring all of Fieldbook's ways of retrieving on the same questions.

:::photo{src="/lesson-images/rag/rag-11-notes.webp" alt="Handwritten notes about grounded answers: Number the sources, and cite each fact like [2]. Not found is an exact answer a program can check. A weak best source means no model call. Our gate, -9.0, was measured on our own questions. Cheap rules catch the obvious cases; the model the subtle ones. Hide the sources when the answer is not found." ai="true"}
One page of notes for this chapter.
:::
:::
