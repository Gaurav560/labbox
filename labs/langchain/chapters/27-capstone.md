:::step{type=story title="Navin goes live"}
Twenty-six chapters ago Navin was a few `if` statements. Since then it learned to call a model, use the co-op's tools,
read photos, remember conversations, search the rule book, keep Aadhaar numbers private, refuse what it should refuse,
and wait for the manager before a booking.

Now it all becomes one service. The co-op's app sends each member's message to `POST /chat`; a booking comes back as
"waiting for the manager"; the manager's screen sends a decision to `POST /manager/decide`. And one last feature: Navin
remembers lasting facts about each member's farm across conversations, so Ravi never has to explain his three acres of
onions twice.


Onions being graded and cleaned by hand before sale: the work, the people and the crop that Navin is built to serve.

:::photo{src="/lesson-images/langchain/onion-grading.webp" alt="Workers sitting among heaps of onions, grading and cleaning them by hand" credit="Nishaexport" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File%3AOnion_grading_and_cleaning.jpg"}
Grading and cleaning onions.
:::
:::mission
Give Navin a long-term memory of each member's facts, then serve the complete agent as a FastAPI web service.
:::
:::

:::step{type=history title="Everything inside Navin"}
:::before{title="A chatbot in 2016"}
A help desk bot in 2016 was a decision tree: buttons, keywords, and "Sorry, I did not understand" for everything else
(chapter 1's rules).
:::

Every part of Navin comes from the last few years:

| Year | Idea | Chapter |
|---|---|---|
| 2017 | The transformer | 4 |
| 2020 | Retrieval-augmented generation | 19 |
| 2022 | LangChain; prompt injection named | 7, 24 |
| 2023 | Function calling; JSON mode; evals | 10, 13, 26 |
| 2024 | Structured outputs; MCP; vision in small models | 13, 21, 14 |
| 2025 | LangChain 1.0: create_agent and middleware | 11, 22 |

:::solved
**Ordinary engineering around a model.** None of it makes the model smarter. Each piece supplies facts, limits what it
can do, checks what it says, or brings a person in. That is what makes it safe to put in front of a village of farmers.
:::

:::timeline
- **2017** The transformer.
- **2020** RAG.
- **2022** LangChain.
- **2025** LangChain 1.0.
:::
:::

:::step{type=concept title="Short-term and long-term memory" file="27-capstone/navin.py" line="39-55"}
Chapter 15's checkpointer remembers **one conversation** (a thread). Facts that should outlive it ("Ravi grows onions on
3 acres in Lasalgaon") go into a **store**, shared by all of a member's threads:

| Memory | Kept in | Lasts | Holds |
|---|---|---|---|
| Short-term | checkpointer, per thread | one conversation | every message |
| Long-term | store, per member (namespace) | as long as you keep it | chosen facts |

A tool writes to the store through the runtime; the dynamic prompt (chapter 23) reads the member's facts before every
model call:

```python
runtime.store.put(("M-104", "facts"), "1", {"fact": "grows onions on 3 acres"})     # in the remember tool
request.runtime.store.search(("M-104", "facts"))                                      # in member_prompt
```

The namespace `(member id, "facts")` keeps each member's facts apart, as the thread id keeps their conversations apart.
:::

:::step{type=task task=remember_fact title="Your turn: remember a fact" file="27-capstone/navin.py" line="39-45"}
Finish the `remember` tool: save `{"fact": fact}` with `runtime.store.put(namespace, key, value)`, where the namespace is
`(runtime.context.member_id, "facts")` and the key the next number, `str(len(runtime.store.search(namespace)) + 1)`.
Return `"Saved."`.

Press **Check**.
:::

:::step{type=concept title="One agent, every lesson" file="27-capstone/navin.py" line="67-81"}
`navin_agent()` puts the course together:

| Piece | From |
|---|---|
| `search_rules` over the rule book, split at sentences, with titled chunks | 17 to 20 |
| `mandi_price`, `storage_cost`, `book_storage`, `remember` | 12, 25, this chapter |
| `PIIMiddleware` with the Aadhaar detector | 24 |
| `member_prompt`: the member's name and saved facts | 23, this chapter |
| `ToolErrorMiddleware`, `ModelCallLimitMiddleware(run_limit=8)` | 22 |
| `HumanInTheLoopMiddleware` on `book_storage` | 25 |
| checkpointer and store | 15, this chapter |

`app.py` wraps it in FastAPI: `POST /chat` runs the agent for a member (thread = member id, context = who they are), and
`reply(result)` turns the result into JSON, either an answer or a booking waiting for the manager. `POST
/manager/decide` resumes the member's thread with the manager's decision.
:::

:::step{type=task task=chat_endpoint title="Your turn: the chat endpoint" file="27-capstone/app.py" line="31-36"}
Finish `chat(body)`: invoke the agent with the member's message, the config `{"configurable": {"thread_id":
body.member_id}}` and `context=Member(body.member_id, NAMES.get(body.member_id, "a member"))`, and return
`reply(result)`.

Start the service in one terminal:

```bash run
cd /workspace/27-capstone && uvicorn app:app --port 8000
```

and talk to it from another:

```bash run
cd /workspace/27-capstone && bash try.sh
```

Press **Check**.
:::

:::step{type=try title="Navin, live"}
With the service running, `try.sh` plays one member's morning:

```text
$ bash try.sh
{"status":"answered","answer":"Hello, Ravi! It's nice to meet you. How can I assist you today?"}

{"status":"answered","answer":"You can store 80 crates of onions, but you'll need the manager's approval since it's more than 50 crates. This usually takes one working day to get. Remember, the crates must be clean and labeled with your member number."}

{"status":"waiting_for_manager","action":"book_storage","args":{"crates":80,"days":10,"crop":"onion"}}

{"status":"answered","answer":"I have booked 80 crates of onions for 10 days. Your booking number is B-101."}

{"status":"answered","answer":"I'm sorry, but I can't store sensitive information like Aadhaar numbers. Is there anything else I can help you with?"}

{"status":"answered","answer":"You can get a loan of up to Rs 50,000 per acre for your farm. Since you have 3 acres, that would be Rs 150,000. To apply, bring your 7/12 land record, member's passbook, and an estimate of your costs to the office."}
```

Six requests, the whole course at work:

1. Ravi introduces himself. A plain answer.
2. **80 crates**: "you'll need the manager's approval since it's more than 50 crates. This usually takes one working
   day". The question chapters 19 and 26 got wrong is now right, because this rule book is split at sentences and its
   chunks carry their titles (chapter 20).
3. The booking comes back as `waiting_for_manager` with its arguments; nothing is booked yet (chapter 25).
4. The manager approves through `/manager/decide`, and the same thread finishes: booking B-101.
5. The Aadhaar number was masked before the model saw it (chapter 24), and Navin declined to store it.
6. The loan: Rs 50,000 per acre for his 3 acres. Navin knew the acres from earlier in the conversation.

The last answer also shows what is still missing: the model multiplied 3 × 50,000 itself, because this agent has no loan
tool. It is right, but chapter 12's `crop_loan_limit` belongs in the tool list.

Long-term memory is clearest across two **different** threads. Ravi mentions his farm on Monday; on Friday, in a new
conversation, he asks about a loan:

```text
[monday] > I farm 3 acres of onions in Lasalgaon.
    Got it! You farm 3 acres of onions in Lasalgaon. How can I help you today?
[friday] > How much crop loan can I get for my whole farm?
    You can borrow up to Rs 50,000 per acre for your 3 acres of onions, which totals Rs 1,50,000. The loan is for seeds, fertiliser, and labour at a 7% interest rate, to be repaid after harvest. To apply, bring your land record, passbook, and cost estimate to the office.
store: [{'fact': 'Ravi Patil farms 3 acres of onions in Lasalgaon.'}]
```

The Friday thread had never seen Monday's message. The `remember` tool had saved "Ravi Patil farms 3 acres of onions in
Lasalgaon" in the store, and `member_prompt` put it in Friday's system prompt, so the answer used his 3 acres
(Rs 1,50,000) without asking.
:::

:::step{type=predict title="Guess first"}
:::question
The co-op runs two copies of the service behind a load balancer, each with its own `InMemorySaver` and `InMemoryStore`.
What goes wrong?
:::
- [ ] Nothing
- [x] A member's next message may reach the other copy, which has none of their conversation, facts or paused booking
- [ ] Answers get slower
:::explain
Shared state needs a shared place: `PostgresSaver` for threads and a database store for facts, used by every copy.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does Navin keep "Ravi grows onions on 3 acres" so a new conversation knows it?
:::
- [ ] In the thread
- [x] In the store, under Ravi's namespace
- [ ] In the model
:::explain
Threads are conversations; the store holds what should outlive them.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `POST /chat` return for a booking request?
:::
- [ ] The booking number
- [x] `waiting_for_manager`, with the tool and its arguments, until the manager decides
- [ ] An error
:::explain
The run is paused and saved; `/manager/decide` resumes it.
:::
:::

:::step{type=deep-dive title="Go deeper: before real members"}
**Durable state.** `PostgresSaver` and a Postgres-backed store, so conversations, facts and paused bookings survive
restarts and work across several servers.

**Streaming.** Return the answer as Server-Sent Events (chapters 8 and 16) so members see it as it is written.

**Sign-in.** The member id must come from a signed-in session, never from the request body as in this exercise, or
anyone could send `M-104` and read Ravi's facts (chapter 12's least privilege, for the whole service).

**The checklist.** A golden set and judge before every change (26), budgets and rate limits per member, logs without
personal data (24), and the rule from chapter 10: numbers come from tools, never from the model.
:::

:::step{type=recap}
You can now:

- keep long-term facts per member in a store, and use them in the prompt;
- combine tools, retrieval, guardrails, approvals and memory in one agent;
- serve an agent over HTTP, including pauses for a person;
- list what must change before real members use it.

That is the end of the course. You started with a rule that answered two questions; Navin now answers a village of
farmers from the co-op's own rules, in their own language, and asks the manager before it books. Well done.

:::photo{src="/lesson-images/langchain/lc-27-notes.webp" alt="Handwritten notes about the capstone: Thread: one conversation; Store: facts per member; Every lesson, one agent; POST /chat, /manager/decide; 80 crates: now right" ai="true"}
One page of notes for this chapter.
:::
:::
