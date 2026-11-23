:::step{type=story title="The thing on my roof"}
Citizens ask about rules: "Do we pay for the tanker?" "The thing on my roof overflows every night, is that your problem
or mine?" The answers are in the board's **rulebook**, and Harsh must answer from it, not from what a model believes
water boards usually do.

Plain RAG (the LangChain course, chapter 19) searches once and answers from whatever came back. Two things go wrong. The
search finds the wrong section, because the citizen's words ("the thing on my roof") are not the rulebook's words
("roof tank"); and the model answers anyway, from text that does not contain the answer. **Agentic RAG** adds judgement
around the search: the model decides **whether** to search, a grader checks **what came back**, and a vague question is
**rewritten** and searched again.

:::mission
Grade what the search found, and when it does not answer the question, rewrite the question once and search again.
:::
:::

:::step{type=history title="The reference interview"}
:::before{title="Searching the words people use"}
A library catalogue finds what you type. People rarely type what the catalogue calls things.
:::

Librarians solved this long before computers. In **1968** Robert S. Taylor described the **reference interview**: a
reader's first question is rarely the real one, so the librarian asks, rephrases, searches, checks what was found and
searches again. In **2020** the paper that named **retrieval-augmented generation** (Lewis and others, at Facebook AI)
put a search in front of a model. In **2023** and **2024**, **Self-RAG** and **Corrective RAG** taught models to judge
their own search results and search again, the reference interview done by a graph.

:::solved
**Answers that come from the right page**, and an honest "I will ask a person" when no page has the answer.
:::

:::timeline
- **1968** The reference interview.
- **2020** Retrieval-augmented generation.
- **2023 to 2024** Self-RAG and Corrective RAG.
:::

A library desk in 1943. Readers brought their questions here, and the staff turned them into searches of the catalogue, and searched again when the first answer was not it.

:::photo{src="/lesson-images/langgraph/refdesk.webp" alt="A black and white photo from above of a long library desk, with men in hats standing at it and women librarians behind it among books and papers" credit="Pix Magazine Photographer" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Library_desk,_Reading_Room,_Mitchell_Building.jpg"}
The reading room desk of the State Library of New South Wales, 1943.
:::
:::

:::step{type=concept title="Search as a tool, then a grade" file="15-agentic-rag/rag.py" line="38-69"}
The rulebook is eight short sections in an `InMemoryVectorStore`, embedded with `ai-embed`. `search_rules` is a tool,
so the model decides whether a message needs it ("thank you" does not). After the search, a routing function grades the
result:

```python
def grade_documents(state) -> Literal["answer", "rewrite_question"]:
    grade = model().with_structured_output(Grade).invoke([SystemMessage(GRADE), HumanMessage(question + found)])
    if grade.relevant or state.get("rewrites", 0) >= 1:
        return "answer"
    return "rewrite_question"
```

A routing function may call a model: it still only decides, and changes nothing. The `rewrites` counter allows one
rewrite; after that, `answer` runs, and its prompt says to send the question to a person if the rulebook text does not
answer it.
:::

:::step{type=task task=grade_documents title="Your turn: check what the search found" file="15-agentic-rag/rag.py" line="62-68"}
Finish `grade_documents(state)`: ask `model().with_structured_output(Grade)` with `[SystemMessage(GRADE),
HumanMessage(f"Question: {question(state)}\n\nText:\n{found}")]`; return `"answer"` if it is relevant or
`state.get("rewrites", 0) >= 1`, else `"rewrite_question"`.

Press **Check**.
:::

:::step{type=concept title="Rewrite in the rulebook's words" file="15-agentic-rag/rag.py" line="71-74"}
`rewrite_question` asks the model to turn the citizen's words into the words a rulebook would use, and adds the result as
a new human message, so `search_or_answer` searches again with it:

```python
better = model().invoke([SystemMessage(REWRITE), HumanMessage(question(state))]).content
return {"messages": [HumanMessage(better)], "rewrites": state.get("rewrites", 0) + 1}
```

The `answer` node always answers the citizen's **original** question (the first human message), with the last search's
text as its only source.

:::diagram{name="lg-agentic-rag"}
Search, grade, and either answer or rewrite once; a greeting skips the search entirely.
:::
:::

:::step{type=task task=rewrite_question title="Your turn: a better search" file="15-agentic-rag/rag.py" line="71-74"}
Finish `rewrite_question(state)`: ask `model()` with `[SystemMessage(REWRITE), HumanMessage(question(state))]`, and return
`{"messages": [HumanMessage(<its content>)], "rewrites": state.get("rewrites", 0) + 1}`.

```bash run
cd /workspace/15-agentic-rag && python main.py "I bought bottled water for three days during the cut. Will the board give that money back?"
```

Press **Check**.
:::

:::step{type=try title="Four questions, four paths"}
```text
$ python main.py "Our water has been off since Monday because of the burst main. Do we have to pay for a tanker?"
> Our water has been off since Monday because of the burst main. Do we have to pay for a tanker?
  [search_or_answer] search: tanker charges burst main
  [retrieve] found: Private tankers: the board does not repay the cost of a tanker a citizen hires privately. || Tankers: when piped water has been off for more than 24 h...
  [answer] No, you do not have to pay for a tanker since the water has been off for more than 24 hours due to a board fault. Please ask the desk before 2 pm for a tanker the same evening.
$ python main.py "The thing on my roof overflows every night. Is that your problem or mine?"
> The thing on my roof overflows every night. Is that your problem or mine?
  [search_or_answer] search: overflow responsibility
  [retrieve] found: Roof tanks: the tank on a building's roof, its float valve and its overflow pipe belong to the owner. The board is responsible only up to and includin...
  [answer] The overflow issue is your responsibility, as the tank and its components belong to the owner. It usually indicates a stuck float valve. If you need further assistance, I will ask a person at the desk.
$ python main.py "I bought bottled water for three days during the cut. Will the board give that money back?"
> I bought bottled water for three days during the cut. Will the board give that money back?
  [search_or_answer] search: refund bottled water during cut
  [retrieve] found: Tankers: when piped water has been off for more than 24 hours because of a board fault, the board sends a tanker free of charge. Ask the desk before 2...
  [rewrite_question] Water board rulebook refund policy for bottled water purchases during service interruptions.
  [search_or_answer] search: refund policy service interruptions
  [retrieve] found: Reconnection after a cut for unpaid bills: Rs 500, done within 2 working days of payment. || Meters: a meter that leaks, stops or is cracked is replac...
  [answer] The rulebook does not mention reimbursement for bottled water during a cut. I will ask a person at the desk for clarification.
$ python main.py "Hello, thank you for the help yesterday!"
> Hello, thank you for the help yesterday!
  [search_or_answer] You're welcome! If you have any more questions or need assistance today, feel free to ask.
```

- **The tanker:** one search found both tanker rules, the grade passed, and the answer quotes the rule, including "ask
  before 2 pm". One assumption slipped in: the answer treats a burst main as a "board fault", which the rulebook does not
  say.
- **The roof:** "the thing on my roof" became the search "overflow responsibility", and the embeddings found the roof
  tank rule anyway. No rewrite was needed: a good search on the first try is the common case.
- **Bottled water:** the first search found tanker rules, the grader said they do not answer the question, the question
  was rewritten and searched again, and the second search found nothing either. With one rewrite used, `answer` ran,
  and said honestly that the rulebook does not cover it. A plain RAG chain would have answered from the tanker rule.
- **Thank you:** no search at all; the model decided this needed none.
:::

:::step{type=predict title="Guess first"}
:::question
Without the `rewrites` limit, the bottled-water question would…
:::
- [ ] be answered after the second search
- [x] rewrite and search again and again, because no rule ever matches, until the recursion limit stops it
- [ ] skip the grader
:::explain
When the answer is not in the documents, no rewrite will find it. One retry, then an honest answer.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is `search_rules` a tool instead of a fixed first step?
:::
- [x] So the model can skip it when a message needs no rules, like a thank-you
- [ ] Tools are faster
- [ ] Vector stores require tools
:::explain
A fixed search on every message costs an embedding call and adds irrelevant text to simple replies.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which question does `answer` reply to after a rewrite?
:::
- [ ] The rewritten search
- [x] The citizen's original question, using the last search's text
- [ ] Both
:::explain
The rewrite is for the search engine; the citizen should get an answer to what they asked.
:::
:::

:::step{type=deep-dive title="Go deeper: agentic RAG in practice"}
**Grade each document.** Here the grader judges the two sections together. Grading each one and keeping only the relevant
ones gives the answer less noise.

**Fall back to the web, or to a person.** Corrective RAG searches the web when the documents fail; for a water board,
a person at the desk is the right fallback.

**Measure it.** A golden set of questions with the right rulebook section (the LangChain course, chapter 20) tells you
whether a change to chunking, the grader or the rewrite prompt helps.
:::

:::step{type=recap}
You can now:

- let a model decide when to search, with retrieval as a tool;
- grade search results before answering from them;
- rewrite a vague question in the documents' words, once, and search again;
- answer honestly when the documents do not have the answer.

Next, chapter 16: subgraphs, so each office can own its own graph.

:::photo{src="/lesson-images/langgraph/lg-15-notes.webp" alt="Handwritten notes about agentic RAG: search is a tool; grade what came back; rewrite once, search again; answer the original question; not found? Ask a person" ai="true"}
One page of notes for this chapter.
:::
:::
