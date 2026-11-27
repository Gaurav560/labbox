:::step{type=story title="Is that in the policy?"}
Adjusters spend part of every day answering one kind of question: "is this covered?". A cracked windscreen: does the
deductible apply? A stolen scooter: what must the customer send? The answers are in Deccan Shield's **policy wording**,
the legal text of the policy, in your project as `data/policy_wording.md`, fourteen numbered clauses:

```text
C1 | Own damage | We pay for loss of or damage to the insured vehicle caused by accident, fire, explosion, lightning, flood, storm, hailstorm, earthquake or landslide.
C2 | Theft | We pay for theft of the insured vehicle. A police complaint (FIR) must be filed within 48 hours of discovering the theft, and a copy sent with the claim.
C3 | Deductible | Every own damage claim bears a compulsory deductible: Rs 1,000 for two-wheelers and Rs 2,000 for private cars. We pay the assessed loss minus the deductible.
...
```

Meera's legal team has one rule for anything that answers these questions: **every answer must point to the clause it
came from**, so a person can check it in seconds. A confident answer without a source is worse than no answer, because it
will be believed.

In this chapter Claimdesk finds the clauses a question is about, gives only those to the model, and checks that the
answer cites them, and only them.

:::mission
Find the clauses that match a question, give only those to the model, and check that every citation in its answer is
real.
:::
:::

:::step{type=concept title="Find first, then answer from what you found" file="10-policy-lookup/lookup.py" line="37-42"}
A model on its own answers from what it learned in training: general motor insurance, from many countries and many
insurers. That is exactly the wrong source here. Deccan Shield's deductible is Rs 1,000 for two-wheelers; another
insurer's may be Rs 500.

So the answer is built in two steps:

1. **Retrieve**: find the few clauses that are about the question.
2. **Generate**: give the model the question and only those clauses, and ask it to answer from them, citing each one.

This pattern is called **retrieval-augmented generation**, usually shortened to **RAG**. Sending three clauses instead of
all fourteen also makes every call cheaper (input tokens, chapter 8) and the answer easier to check.

How do you find the right clauses? The simplest method that can work: count the **meaningful words** a clause shares with
the question. `words()` (already written) lower-cases a text, keeps words of 4 letters or more, and drops very common
ones like "what" and "which" (the `STOP` set), so only words that say something are left.

Here is the real trace for one question. Its meaningful words are `cracked`, `windscreen`, `paid`, `without`, `deductible`:

:::trace{title='Scoring clauses for: Is a cracked windscreen paid without the deductible?'}
| clause | shared words | score | note |
|---|---|---|---|
| C4 Glass | windscreen, paid, without, deductible | 4 | the best match |
| C3 Deductible | deductible | 1 | one word in common |
| C9 Valid licence | without | 1 | ties with C3; C3 comes first in the wording |
| C1, C2 and the rest | none | 0 | left out |
:::

So `find_clauses` returns `['C4', 'C3', 'C9']`: the right clause first, and two weaker ones that do no harm because
the model is told to use only what answers the question.
:::

:::step{type=history title="Finding the right page"}
:::before{title="Before: reading everything"}
Before search engines, finding the passage that answered a question meant knowing the document, or reading it.
:::

In 1972 the British computer scientist **Karen Spärck Jones** published "A statistical interpretation of term specificity
and its application in retrieval". Her idea: a word that appears in few documents tells you more than a word that appears
in all of them. Weighting words this way, later called **inverse document frequency**, became part of almost every search
engine. Our `STOP` set is the crude version of her idea: words in nearly every sentence say nothing.

This is Karen Spärck Jones, photographed in 2002 outside the University of Cambridge Computer Laboratory, where she
worked for most of her career. Every time a search engine ranks a page because it shares your rare words, it is using
her idea, and so does `find_clauses` in this chapter.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-sparck-jones.webp" alt="A woman with short white hair and glasses, in a red jacket, smiling, outdoors." credit="Markus Kuhn" license="CC BY 2.5" source="https://commons.wikimedia.org/wiki/File:Karen_Sp%C3%A4rck.jpg"}
Karen Spärck Jones (1935 to 2007), in summer 2002.
:::

In 2020 Patrick Lewis and colleagues at Facebook AI Research, University College London and New York University published
"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", combining a retriever with a language model and
naming the pattern **RAG**. It became the standard way to make a model answer from a company's own documents.

:::solved
Answer from the right source, and show it: search narrows the text, the model writes the answer, citations make it
checkable.
:::

:::timeline
- **1972** Spärck Jones describes term specificity (inverse document frequency).
- **1990s** Weighted keyword search powers early web search engines.
- **2020** Lewis and colleagues name retrieval-augmented generation.
- **Today** Most enterprise AI assistants answer from retrieved documents, with citations.
:::

:::funfact
Spärck Jones is often quoted as saying "computing is too important to be left to men". She spent much of her career
encouraging women into the field.
:::
:::

:::step{type=example title="Worked example: score, filter, sort"}
This is only to read; it is not in your project. Ranking notes by shared words with a question:

```python
def words(text):
    return {w for w in text.lower().split() if len(w) >= 4}

notes = {"N1": "monsoon parking rules", "N2": "flood claims need photos",
         "N3": "office timings"}
q = words("do flood claims need photos")
scored = [(len(q & words(t)), nid) for nid, t in notes.items()]
ranked = sorted((s for s in scored if s[0] > 0), key=lambda s: -s[0])
print([nid for _, nid in ranked[:2]])  # ['N2']
```

- `q & words(t)` is the **intersection** of two sets: the words in both. `len(...)` counts them.
- `(score, id)` pairs keep the id with its score.
- `s[0] > 0` drops notes that share nothing: returning an unrelated note is worse than returning none.
- `key=lambda s: -s[0]` sorts by score, highest first. Python's `sorted` is **stable**: equal scores stay in their original
  order, so ties are decided by the wording's order, every time.
- `ranked[:2]` keeps at most k.
:::

:::step{type=predict title="Guess first"}
:::question
The question "Do we pay for a puncture?" shares no meaningful word with any clause. What should `find_clauses` return?
:::
- [ ] The three clauses with the most words in general
- [x] An empty list
- [ ] Every clause
:::explain
Returning unrelated clauses invites the model to stretch them into an answer. An empty list lets Claimdesk say plainly that
nothing was found. (Clause C12 is actually about tyres; the next try step shows why keywords missed it.)
:::
:::

:::step{type=try title="Nothing found yet"}
```text
$ python lookup.py
Q: Is a cracked windscreen paid without the deductible?
   clauses: []
   answer: 
   cited: [] ok: False
Q: My scooter was stolen. What must I send?
...
```

No clauses, no answer. Write the search first.
:::

:::step{type=task task=find_clauses title="Your turn: find the clauses a question is about"}
In `find_clauses` in `lookup.py`:

1. For each clause, score = `len(words(question) & words(title + " " + text))`.
2. Keep the clauses with a score above 0.
3. Sort by score, highest first (ties keep the wording's order), and return at most `k` ids.

The check uses the trace above, the stolen scooter, the puncture, and `k=1`. Press **Check**.
:::

:::step{type=concept title="Answers you can check" file="10-policy-lookup/lookup.py" line="45-53"}
Now the answer. The system message (lines 11 to 14) gives the model three rules: use only the clauses given, cite each one
as `[C4]`, and if they do not answer the question, say exactly `Not in the policy wording.`

The user message carries the question and the found clauses, one per line with its id:

```text
Question: Is a cracked windscreen paid without the deductible?

Clauses:
[C4] Glass: Breakage of windscreen or windows is covered under own damage. Glass-only claims are paid without the deductible.
[C3] Deductible: Every own damage claim bears a compulsory deductible: ...
[C9] Valid licence: We do not pay for loss or damage while the vehicle was driven by a person without a valid driving licence.
```

Then **Claimdesk checks the model**, instead of trusting it:

```python
cited = []
for cid in re.findall(r"\[(C\d+)\]", answer):
    if cid not in cited:
        cited.append(cid)
ok = bool(cited) and all(c in ids for c in cited)
```

- `re.findall(r"\[(C\d+)\]", answer)` finds every `[C` + digits + `]` in the answer and returns what is inside the
  brackets. (In the pattern, `\[` means a real bracket, `\d+` one or more digits.)
- Repeats are dropped, keeping the order.
- `ok` is true only when the answer cites **something**, and every citation is a clause it was **given**. An answer
  citing `[C12]` when C12 was not sent cannot be checked: the model made the citation up, or remembered it from elsewhere.

`ok` is what the screen will use: a green "checked against the wording" mark, or "verify this answer".
:::

:::step{type=task task=cited_answer title="Your turn: an answer that cites its clauses"}
In `cited_answer`:

1. Build the context: one line per found clause, `f"[{cid}] {title}: {text}"`, joined with newlines.
2. Ask the model (`MODEL`, `temperature=0`, `SYSTEM` as the system message) with the question and the clauses as the user
   message.
3. Find the cited ids with `re.findall`, without repeats, in order.
4. Return `{"answer": ..., "cited": ..., "ok": ...}` as described.

Press **Check**.
:::

:::step{type=try title="Four questions, four honest results"}
Through the gateway, with the real model:

```text
$ python lookup.py
Q: Is a cracked windscreen paid without the deductible?
   clauses: ['C4', 'C3', 'C9']
   answer: Yes, a cracked windscreen is paid without the deductible as glass-only claims are covered under own damage and are paid without the deductible [C4].
   cited: ['C4'] ok: True
Q: My scooter was stolen. What must I send?
   clauses: ['C2', 'C5']
   answer: You must send a copy of the police complaint (FIR) that was filed within 48 hours of discovering the theft, along with your claim [C2].
   cited: ['C2'] ok: True
Q: Do we pay for a puncture?
   clauses: []
   answer: Not in the policy wording.
   cited: [] ok: False
Q: Does the policy cover a medical check-up for the driver?
   clauses: ['C11', 'C6', 'C8']
   answer: Not in the policy wording.
   cited: [] ok: False
```

The first two are what Meera's legal team wanted: correct, short, with the clause.

The last one is good behaviour too: the clauses shared only general words ("policy", "driver") with the question, and the
model refused to stretch them.

The puncture is the instructive failure. Clause **C12** says Deccan Shield does not pay for "tyres damaged without other
damage", which answers the question. But the question says "puncture" and the clause says "tyres": no shared word, so
nothing was retrieved, and Claimdesk honestly said "not in the policy wording". Honest, and wrong. Keyword search cannot
know that a puncture is about a tyre. That is the limit of this method, and the reason for the next step up.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
The model answers "Glass is always covered [C12]", but C12 was not among the clauses sent. What should Claimdesk do?
:::
- [ ] Show it: the model is usually right
- [x] Mark it as not ok: the citation points to a clause the model was never shown
- [ ] Look up C12 and trust the answer if C12 exists
:::explain
A citation is only useful if it can be checked against what was actually given. Here it cannot, so a person must verify.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why send only the best few clauses instead of the whole wording?
:::
- [x] It is cheaper, and the model has less unrelated text to be misled by, so answers are easier to check
- [ ] Models cannot read fourteen clauses
- [ ] The gateway limits messages to three lines
:::explain
A real policy wording is dozens of pages. Retrieval keeps the input small and on topic; citations keep the answer
honest.
:::
:::

:::step{type=deep-dive title="Go deeper: retrieval in production"}
**Embeddings.** The puncture problem is solved by searching by **meaning**: an embedding model turns text into numbers so
that "puncture" lands near "tyres". The LabBox course "RAG and vector databases" teaches it in depth. Many teams combine
both (keyword and meaning), called **hybrid search**.

**BM25.** The standard keyword ranking in search engines (Elasticsearch, OpenSearch) builds on Spärck Jones's weighting,
and also accounts for how long each document is.

**Chunking.** Real wordings are long documents. They are split into passages (often by clause or section) before search;
the split decides what can be found.

**Measure retrieval separately.** If the right clause is not retrieved, no prompt can fix the answer. Chapter 14's golden
set can include questions with their correct clauses, so you measure search and answers apart.
:::

:::step{type=recap}
You can now:

- explain retrieval-augmented generation, and why answers must come from the customer's own documents;
- rank passages by shared meaningful words, leave out the ones that share nothing, and break ties the same way every time;
- give the model only the found clauses, and check that every citation in its answer is one it was given;
- recognise the limit of keyword search (a puncture is about tyres) and know what comes next.

Next, chapter 11: questions that need live data. "Is this policy in force today?" cannot be answered from the wording, so
the model gets a tool.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-10-notes.webp" alt="Handwritten notes about answering from the policy wording: Find the clauses first, then answer from them. Score clauses by the words they share. Leave out clauses that share nothing. Every answer must cite its clause. A citation to an unsent clause is not ok. Keywords miss synonyms: puncture is about tyres." ai="true"}
One page of notes for this chapter.
:::
:::
