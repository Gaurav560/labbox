:::step{type=story title="What did I just tell you?"}
Ravi writes: "Hello, I am Ravi. I grow onions and have 40 crates to store." Then: "How much will storing them cost for
15 days?" Any person at the co-op's counter would answer. Navin, as built so far, cannot: every `invoke` starts from
nothing. "Them" refers to a message Navin no longer has.

A model has no memory of its own. Each request is complete in itself (chapter 5): whatever the model should know about
the conversation must be sent again, every time. **Short-term memory** means the application keeps the conversation and
sends it along. In LangChain a **checkpointer** saves the agent's state after every step, and a **thread id** says which
conversation a message belongs to.

:::mission
Give Navin a checkpointer so it remembers a conversation, then give every member their own thread so conversations
never mix.
:::
:::

:::step{type=history title="The web learns to remember"}
:::before{title="Every request a stranger"}
HTTP, the protocol of chapter 5, was designed in **1991** to be **stateless**: each request stands alone, and the server
forgets you as soon as it has answered. Fine for documents; useless for a shopping basket.
:::

In **1994** Lou Montulli at Netscape invented the **cookie**: a small id the server gives the browser, which sends it
back with every request, so the server can find "this visitor's" data again. A chat model has the same problem and the
same solution: the model is stateless, the application keeps the conversation, and an id (a session, a **thread**)
says whose conversation it is. When ChatGPT added a memory feature in **2024**, it was built the same way: memory lives
in the application, not in the model.

:::solved
**State outside the model.** The model stays simple and stateless; the app decides what to remember, for whom, and
for how long.
:::

:::timeline
- **1991** HTTP: stateless by design.
- **1994** The cookie.
- **2024** Memory features in chat apps, kept outside the model.
:::
:::

:::step{type=concept title="Checkpointers and threads" file="15-memory/memory.py" line="10-13"}
```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(..., checkpointer=InMemorySaver())
agent.invoke({"messages": [{"role": "user", "content": "I am Ravi"}]},
             {"configurable": {"thread_id": "M-104"}})
```

After every step of a run (each model call, each tool round) the **checkpointer** saves the agent's state, its list of
messages, under the thread id. The next `invoke` with the same thread id starts from that saved state and adds the new
message to it, so the model receives the whole conversation.

| Checkpointer | Keeps state in | Use for |
|---|---|---|
| `InMemorySaver` | the Python process's memory | learning, tests; gone on restart |
| `SqliteSaver` | a SQLite file | one small server |
| `PostgresSaver` | PostgreSQL | production: many servers, survives restarts |

Each thread grows with every message, and every message is paid for again on every call (chapter 9). Chapter 22 adds
summarising, so long conversations stay affordable.
:::

:::step{type=task task=memory_agent title="Your turn: an agent that remembers" file="15-memory/memory.py" line="10-13"}
Finish `memory_agent()`: chapter 11's agent (model, both tools, `system_prompt=SYSTEM`) with
`checkpointer=InMemorySaver()`.

Press **Check**.
:::

:::step{type=concept title="One thread per member" file="15-memory/memory.py" line="16-20"}
The thread id decides **whose** conversation continues. Using the member's id keeps each member's conversation
separate:

:::trace{title="Four messages, two threads"}
| Message | thread_id | What the model receives |
|---|---|---|
| I am Ravi, 40 crates of onions | M-104 | that message |
| How much for 15 days? | M-104 | Ravi's first message, Navin's reply, this question |
| How much for 15 days? | M-221 | only this question: Asha's thread is new |
| What is my name? | M-104 | all of Ravi's conversation so far |
:::

A real app might use one thread per conversation instead (a member can start a new chat), and keep the member id in
the context (chapter 12). Either way: a thread must never be shared by two people.

:::diagram{name="lc-memory-threads"}
Each message joins its own thread's saved conversation; a new thread starts empty.
:::
:::

:::step{type=task task=thread_per_member title="Your turn: one thread per member" file="15-memory/memory.py" line="16-20"}
Finish `ask(agent, member_id, text)`: invoke the agent with the message and
`{"configurable": {"thread_id": member_id}}`, and return the last message's content.

```bash run
cd /workspace/15-memory && python main.py
```

Press **Check**.
:::

:::step{type=try title="Ravi is remembered; Asha starts fresh"}
```text
$ python main.py
[M-104] > Hello, I am Ravi. I grow onions and have 40 crates to store.
Hi Ravi! How many days do you want to store the 40 crates of onions?

[M-104] > How much will storing them cost for 15 days?
Storing 40 crates of onions for 15 days will cost you ₹1200.

[M-221] > How much will storing them cost for 15 days?
How many crates do you want to store?

[M-104] > What is my name?
Your name is Ravi.
```

Ravi's second message says "them": Navin knew it meant 40 crates, called `storage_cost(40, 15)`, and got ₹1,200 (40 ×
15 × 2). Asha asked **exactly the same words**, and Navin asked her how many crates: her thread has no Ravi in it. And
two questions later Ravi's thread still knew his name.

The same question gave two different, correct answers, because the memory, not the model, was different.
:::

:::step{type=predict title="Guess first"}
:::question
The server restarts between Ravi's first and second message. With `InMemorySaver`, what happens?
:::
- [ ] Nothing changes
- [x] Ravi's conversation is gone: the saver kept it in the process's memory
- [ ] The model remembers him
:::explain
`InMemorySaver` is for learning and tests. A real app uses a database checkpointer (SQLite, Postgres).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does Navin's memory of Ravi live?
:::
- [ ] In the model
- [x] In the checkpointer, under Ravi's thread id
- [ ] In the system prompt
:::explain
The model is stateless. The application saves the conversation and sends it again each time.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does a long conversation get more expensive with every message?
:::
- [x] The whole conversation is sent, and paid for, on every call
- [ ] Old messages are charged twice
- [ ] Threads cost money
:::explain
Input tokens grow with the conversation. Windows (chapter 2) and summaries (chapter 22) keep it in check.
:::
:::

:::step{type=deep-dive title="Go deeper: memory in production"}
**Durable checkpointers.** `PostgresSaver` (package `langgraph-checkpoint-postgres`) survives restarts and works across
many servers; the code changes in one line.

**More than messages.** The checkpointer saves the agent's whole state after every step, which is what makes pausing for
a person's approval (chapter 25) and resuming later possible.

**Long-term memory.** A thread is one conversation. Facts that should outlive it ("Ravi grows onions on 3 acres") go
into a **store** shared across threads (chapter 27).
:::

:::step{type=recap}
You can now:

- explain why a model is stateless and where conversation memory lives;
- add a checkpointer to an agent;
- keep one thread per member, so conversations never mix;
- choose a checkpointer for learning and for production.

Next, chapter 16: streaming an agent, its steps and its answer, as they happen.

:::photo{src="/lesson-images/langchain/lc-15-notes.webp" alt="Handwritten notes about short-term memory: The model has no memory; Checkpointer saves each step; One thread per member; Same question, two answers; Every message is paid again" ai="true"}
One page of notes for this chapter.
:::
:::
