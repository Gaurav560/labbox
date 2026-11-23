:::step{type=story title="Is the search any good?"}
Chapter 19 ended with a wrong answer from the right rule book, and the cause was retrieval: the search found half a rule.
Before changing anything (chunk size, threshold, prompts) the co-op needs a way to tell whether a change made retrieval
**better or worse**, on its own questions. Otherwise every fix is a guess, and a fix for one question can quietly break
three others.

The tool is old and simple: a **golden set** of real questions, each with the document that should answer it, and a
number, the **hit rate**: how often the right document is among the first k results.

:::mission
Measure retrieval with a golden set and a hit rate, then improve it by giving every chunk its document's title, and see
what splitting at sentences and query rewriting do to the problems of chapters 17 and 19.
:::
:::

:::step{type=history title="Testing search with known answers"}
:::before{title="Search judged by impression"}
In the 1950s library and documentation systems were judged by how they felt to the people using them. Nobody could say
whether a new indexing method was really better.
:::

In the **1960s** at the Cranfield College of Aeronautics, **Cyril Cleverdon** ran the **Cranfield experiments**: a fixed
collection of papers, a fixed set of questions, and for each question a list of the papers that answer it, judged by
people. Any indexing method could then be scored by how many right papers it found. In **1992** the US National
Institute of Standards and Technology started **TREC**, yearly search competitions on the same principle, which shaped
web search. A golden set for Navin is a tiny Cranfield collection.

:::solved
**Change, measure, keep or revert.** A number on fixed questions turns opinions about search into evidence.
:::

:::timeline
- **1960s** The Cranfield experiments.
- **1992** TREC.
- **2020s** Golden sets for RAG applications.
:::

The library of Cranfield University, the college where Cyril Cleverdon ran his experiments in testing search with known answers.

:::photo{src="/lesson-images/langchain/cranfield-library.webp" alt="The modern library building of Cranfield University, with large windows, seen from outside" credit="Cj1340" license="CC0" source="https://commons.wikimedia.org/wiki/File%3ACranfield_University_Library.jpg"}
Cranfield University Library.
:::
:::

:::step{type=concept title="A golden set and a hit rate" file="20-retrieval-quality/quality.py" line="4-21"}
`GOLDEN` has eight real-looking questions, each with the file that answers it. Some are easy ("How much loan can I get
for 4 acres?"), some share no words with their rule ("Who can tell me what is wrong with my vines?"), one is Marathi in
English letters.

**hit@k** is the share of questions whose expected file appears in the first k results:

| | Expected | First 3 results | hit@1 | hit@3 |
|---|---|---|---|---|
| What papers do I need to join? | membership.txt | loans, membership, spraying | no | yes |
| How much loan for 4 acres? | loans.txt | loans, loans, membership | yes | yes |

`hit_rate(sources_for, golden, k)` takes a function that returns the sources for a question, so the same measurement
works for any store, any splitter and any setting you want to compare.
:::

:::step{type=task task=hit_rate title="Your turn: the hit rate" file="20-retrieval-quality/quality.py" line="16-20"}
Finish `hit_rate(sources_for, golden, k)`: count the questions whose expected file is in `sources_for(question)[:k]`,
and divide by `len(golden)`.

Press **Check**.
:::

:::step{type=concept title="Chunks that say what they are about" file="20-retrieval-quality/quality.py" line="23-28"}
A chunk cut from the middle of `membership.txt` ("A new member brings an Aadhaar card, the 7/12 land record...") never
says it is about membership in general. Putting the document's title in front of each chunk gives every piece that
context, for the embedding and for the model:

```text
Membership: A new member brings an Aadhaar card, the 7/12 land record and two photographs; ...
```

It is one of the cheapest improvements in retrieval, often called **contextual chunks**.
:::

:::step{type=task task=titled_chunks title="Your turn: titled chunks" file="20-retrieval-quality/quality.py" line="23-28"}
Finish `titled_chunks(chunks, titles)`: for each chunk, look up `titles[chunk.metadata["source"]]` and make a new
`Document` with `f"{title}: {chunk.page_content}"` (unchanged if it already starts with the title) and a copy of the
metadata.

```bash run
cd /workspace/20-retrieval-quality && python main.py
```

Press **Check**.
:::

:::step{type=try title="Measured: what helped, and what did not"}
```text
$ python main.py
plain chunks : hit@1 75%, hit@3 88%
    miss@1 'What papers do I need to join?': ['loans.txt', 'membership.txt', 'spraying.txt']
    miss@1 'kanda thevaycha aahe, kiti paise lagtil?': ['membership.txt', 'market.txt', 'loans.txt']
titled chunks: hit@1 88%, hit@3 100%
    miss@1 'kanda thevaycha aahe, kiti paise lagtil?': ['membership.txt', 'market.txt', 'storage.txt']

split at line breaks: the chunks about more than 50 crates:
    "The co-op's cold store at Pimpalgaon keeps onions, tomatoes and grapes. The charge is Rs 2 per crate per day, paid\nwhen the crates are taken out. Bookings of up to 50 crates are confirmed at the counter. Bookings of more than 50"
    "crates need the manager's approval, which usually takes one working day."

split at sentences: the chunks about more than 50 crates:
    ". Bookings of more than 50\ncrates need the manager's approval, which usually takes one working day."

rewritten: 'kanda thevaycha aahe, kiti paise lagtil?' -> 'What are the costs associated with joining the cooperative?': ['membership.txt', 'market.txt', 'storage.txt']

rewritten: 'kanda thevaycha aahe, kiti paise lagtil?' -> 'How much will it cost to store onions?': ['storage.txt', 'storage.txt', 'storage.txt']
```

Three experiments, three real results:

1. **Titled chunks** raised hit@1 from 75% to 88% and hit@3 to 100%: "What papers do I need to join?" now finds
   `membership.txt` first, because its chunks now say "Membership".
2. **Splitting at sentences** (the separators `"\n\n", ". ", "\n"`, so a full stop is preferred over a line break) keeps
   chapter 17's rule whole: "Bookings of more than 50 crates need the manager's approval, which usually takes one working
   day" is now one chunk. (The leading ". " is the separator kept at the start of the chunk; the splitter's
   `keep_separator="end"` option puts it at the end of the previous chunk instead.)
3. **Query rewriting** is not automatically good. Asked to "rewrite this farmer's question as a search query", the model
   turned "kanda thevaycha aahe, kiti paise lagtil?" (I want to store onions, how much will it cost?) into **"What are
   the costs associated with joining the cooperative?"**: a confident mistranslation that searched the wrong rules. With
   a prompt that says the farmer writes Marathi in English letters and gives two words, it became "How much will it cost
   to store onions?", and all three results came from `storage.txt`.

None of these was obvious in advance. Each one was decided by a number.
:::

:::step{type=predict title="Guess first"}
:::question
A change raises hit@3 from 88% to 100% but lowers hit@1 from 88% to 75%. Navin's tool sends the top 3 chunks. Is it
better?
:::
- [x] Probably yes: the right chunk now always reaches the model, which reads all three
- [ ] No: hit@1 is the only number that matters
- [ ] It makes no difference
:::explain
Measure the k you actually use. If the model only ever saw one chunk, hit@1 would be the number to watch.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does a golden set need the expected document for each question?
:::
- [ ] To train the model
- [x] So a search result can be scored right or wrong automatically, every time something changes
- [ ] To make the questions harder
:::explain
Known answers make retrieval measurable, as in the Cranfield experiments.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What did the first query rewrite teach?
:::
- [ ] Rewriting always helps
- [x] A rewrite is another model output that can be wrong; measure it like everything else
- [ ] Marathi cannot be searched
:::explain
Adding a model step adds a place for mistakes. The better prompt fixed it, and the golden set showed both.
:::
:::

:::step{type=deep-dive title="Go deeper: better retrieval"}
**Grow the golden set from real questions.** Every question a member asked that went wrong becomes a golden question,
so the same mistake cannot return unnoticed.

**Answer quality, not only retrieval.** Hit rate checks that the right rule was found; chapter 26 checks that the answer
built from it is right.

**More techniques.** Hybrid search (keywords plus vectors), re-ranking the top results with a second model, and
searching smaller chunks but sending their larger parent section. Add each one only when the numbers say it helps.
:::

:::step{type=recap}
You can now:

- build a golden set and measure retrieval with hit@k;
- improve chunks by giving each its document's title;
- keep rules whole by splitting at sentences;
- treat query rewriting as a model output to be measured, after a real mistranslation.

Next, chapter 21: MCP. The co-op's tools as a server any AI application can use.

:::photo{src="/lesson-images/langchain/lc-20-notes.webp" alt="Handwritten notes about measuring retrieval: Golden set + hit@k; Titled chunks: 75% to 88%; Split at sentences; A rewrite can mistranslate; Decide by the number" ai="true"}
One page of notes for this chapter.
:::
:::
