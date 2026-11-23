:::step{type=story title="Answers from the rule book"}
Everything is ready: the rule book is loaded, cut into pieces, embedded and searchable. Now Navin must use it: for a
question about the co-op's rules, find the right pieces and answer **from them**, saying which file the answer came
from, and admit it when nothing was found.

This is **retrieval-augmented generation** (RAG), the most widely used pattern in AI applications. With an agent, it
takes one new tool, `search_rules`, and a system message that says when to use it. It also takes care, because this
chapter's first three attempts all went wrong, each in a different way, and each is a lesson you will meet again in
real projects.

:::mission
Turn the vector search into a `search_rules` tool that returns pieces with their sources, then build Navin as a RAG
agent with it.
:::
:::

:::step{type=history title="Retrieval-augmented generation, 2020"}
:::before{title="Knowledge frozen in the weights"}
A model knows only what it was trained on, up to a date, and nothing about a co-op in Pimpalgaon. Teaching it new facts
meant training it again.
:::

In **2020** Patrick Lewis and colleagues at Facebook AI Research published **"Retrieval-Augmented Generation for
Knowledge-Intensive NLP Tasks"**: a model that first retrieved passages (with chapter 17's Dense Passage Retrieval) and
then generated its answer from them. It beat larger models that had to remember everything, and gave the pattern its
name. When chat models arrived, RAG with a vector store became the standard way to make them answer from an
organisation's own documents.

:::solved
**Fresh, private, checkable knowledge.** Change a rule file, re-index it, and the next answer uses the new rule; every
answer can name its source.
:::

:::timeline
- **2020** The RAG paper.
- **2023** RAG becomes the standard pattern for company assistants.
- **2024** Agentic RAG: the model decides when and what to search.
:::
:::

:::step{type=concept title="Two ways to do RAG"}
| | **2-step RAG** | **Agentic RAG** (this chapter) |
|---|---|---|
| Search happens | always, before the model is called | when the model calls the `search_rules` tool |
| The search query is | the member's question | whatever the model writes as the tool's argument |
| Good at | simple, predictable, one model call | mixing rules with other tools (rates, charges), several searches |
| Risk | searches even for "hello" | the model may not search, or search badly |

Agentic RAG gives the model more freedom, and therefore more ways to be wrong. Both risks in that last row happened
while this chapter was being written.

:::diagram{name="lc-rag"}
The rule book is embedded once; for each question the model searches, and answers only from the pieces that come back, with their sources.
:::
:::

:::step{type=task task=rules_tool title="Your turn: the search_rules tool" file="19-rag/rag.py" line="21-28"}
Finish `search_rules(query)`: `search(rule_store(), query)` gives `(document, score)` pairs. If there are none, return
`"No rule found for that question."`; otherwise return the pieces joined by a blank line, each as
`f"[{doc.metadata['source']}] {doc.page_content}"`, so the model sees where each one came from.

(`rule_store()` builds the store once, on first use, and remembers it: `@cache`.)

Press **Check**.
:::

:::step{type=task task=rag_agent title="Your turn: Navin as a RAG agent" file="19-rag/rag.py" line="31-34"}
Finish `rag_agent()`: return `create_agent("openai:ai-chat", tools=[search_rules, mandi_price, storage_cost],
system_prompt=SYSTEM)`. Read `SYSTEM` at the top of the file: every sentence in it is there because of the next step.

```bash run
cd /workspace/19-rag && python main.py
```

Press **Check**.
:::

:::step{type=try title="Careful: three ways a RAG agent goes wrong"}
**Attempt 1: it never looked.** Our first system message said "use search_rules ... If it finds nothing, say you don't
know". The real answer to the first question:

```text
> Can I store 80 crates of onions? How long until I know?
I don't know the rules about storing crates. Please call the co-op office for that information.
```

The run's messages showed no tool call at all: the model went straight to the "I don't know" fallback, without
searching. In agentic RAG the model decides whether to search; the system message now says "Before answering any
question about storage, loans, spraying, membership or selling, **always call search_rules first**".

**Attempt 2: it looked for one word.** Now it searched, like this:

```text
AIMessage [{'name': 'search_rules', 'args': {'query': 'storage'}, ...}]
ToolMessage "[storage.txt] Cold storage\n\n[storage.txt] Crates must be clean and labelled with the member's number. ..."
```

The query "storage" found the heading chunk (chapter 17's two-word chunk) and the crate-labelling rule, not the 50-crate
rule. The tool's description now says what a good query is: "query: the member's whole question, in full, not a single
keyword". The model reads that like any instruction.

**Attempt 3: it looked well, and the chunk lied by omission.** With the full question as the query:

```text
$ python main.py
> Can I store 80 crates of onions? How long until I know?
You can store 80 crates of onions, but bookings of more than 50 crates must be confirmed at the counter. You will know once the booking is confirmed. Make sure the crates are clean and labeled with your member number.

> I sprayed my grapes on Monday. Can I harvest on Friday?
You cannot harvest your grapes on Friday since you sprayed them on Monday. Grapes must be harvested at least 10 days after any fungicide spray. Make sure to record the spray in the co-op's spray diary.

> Do you give loans for buying a tractor?
We provide crop loans but not specifically for buying a tractor. Members can borrow up to Rs 50,000 per acre for seeds, fertiliser, and labour. To apply, you'll need the 7/12 land record, your passbook, and an estimate of costs.
```

The spraying and loan answers are right, and come from the rules (the tractor answer even lists the 7/12 land record
from `loans.txt`). The storage answer is **wrong**: more than 50 crates needs the **manager's approval**, about one
working day, not the counter. The retrieved chunk ended with "Bookings of more than 50", the rule cut in half in chapter
17, and the model filled the gap with the sentence before it.

Three fixes so far: a firmer system message, a better tool description, and the third is in the documents themselves.
Chapter 20 measures retrieval and fixes the chunking.
:::

:::step{type=predict title="Guess first"}
:::question
The answer came from the rule book, yet it was wrong. Which layer failed?
:::
- [ ] The model ignored the rules
- [x] Retrieval: the chunk sent to the model held only half of the rule
- [ ] The embedding model
:::explain
A model can only be as right as what it is given. Most RAG errors start in loading and chunking, not in the model.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `search_rules` put `[storage.txt]` in front of each piece?
:::
- [x] So the model can name its source, and a person can check the answer
- [ ] The vector store needs it
- [ ] To make the search faster
:::explain
Sources turn "trust me" into "according to storage.txt".
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In agentic RAG, who writes the search query?
:::
- [ ] The member
- [x] The model, as the tool's argument; the tool's description guides it
- [ ] The vector store
:::explain
That is its strength and its risk: attempt 2 searched for the single word "storage".
:::
:::

:::step{type=deep-dive title="Go deeper: RAG in production"}
**2-step RAG with middleware.** If every question needs the rules, search before the model is called, always, and add
the pieces to the prompt. Chapter 23's middleware can do exactly that.

**Citations you can check.** Return the sources as data (the `ToolMessage` content, or structured output with a
`sources` field), not only in the text, so an app can link to the rule.

**Freshness.** When a rule changes, re-embed that file's chunks only, and test the answers again.
:::

:::step{type=recap}
You can now:

- explain RAG, and the difference between 2-step and agentic RAG;
- build a retrieval tool that returns pieces with their sources;
- build a RAG agent that answers from the rule book and cites it;
- diagnose three real failures: no search, a weak query, a half rule.

Next, chapter 20: measuring retrieval, and fixing what this chapter found.

:::photo{src="/lesson-images/langchain/lc-19-notes.webp" alt="Handwritten notes about retrieval-augmented generation: RAG: retrieve, then answer; search_rules cites its source; 1: it never looked; 2: it searched one word; 3: half a rule, wrong answer" ai="true"}
One page of notes for this chapter.
:::
:::
