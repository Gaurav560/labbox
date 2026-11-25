:::step{type=story title="The manager says yes"}
Navin can now book cold storage with a `book_storage` tool. That tool does something real: it takes space in the
co-op's cold store, which members pay for and other members then cannot use. The co-op's rule (chapter 17's rule book)
is that bookings of more than 50 crates need the manager's approval, and in the first weeks the manager wants to see **every** booking.

So the agent must **pause** before it books, show the manager what it wants to do, and wait, perhaps for hours, until
the manager approves it, changes it, or says no. Then it must carry on from exactly where it stopped. LangChain's
`HumanInTheLoopMiddleware` does the pausing ("human in the loop" means a person takes part in a decision the program
would otherwise make alone); chapter 15's **checkpointer**, which saves a thread's state after every step, does the
remembering.

:::mission
Make every booking wait for the manager, then resume the paused run with the manager's decision: approve, edit or
reject.
:::
:::

:::step{type=history title="Two people for every important decision"}
:::before{title="One person, full control"}
When the clerk who writes a payment can also approve it, a mistake or a fraud goes unnoticed until the books are
checked, perhaps weeks later.
:::

Banks answered with the **maker-checker** (or "four eyes") principle: one person prepares a transaction, a second
approves it before it takes effect. It became standard in banking and in any system that moves money or changes records.
AI agents brought the same question back: an agent can prepare a booking, a payment or an email in a second, but should
it send it alone? In **2024** LangGraph added **interrupts**, a way for a run to stop, save its whole state and wait for a
person, and LangChain 1.0's `HumanInTheLoopMiddleware` (**2025**) made it one line for tool calls.

:::solved
**The agent prepares, a person decides.** Nothing irreversible happens without a human looking at it first.
:::

:::timeline
- **Banking** Maker-checker: one prepares, another approves.
- **2024** Interrupts in LangGraph.
- **2025** Human-in-the-loop middleware in LangChain 1.0.
:::

Banks applied the same idea to their vaults: many were built for **dual control**, two keys or two combinations held
by two people, so that no one person could open them alone. A booking that waits for the manager is the same idea in
software. Below, an old vault lock and its two keys from a bank in Saint Paul, Minnesota, in use from the bank's
founding in 1856 until a new building opened in 1885.

:::photo{src="/lesson-images/langchain/vault-lock.webp" alt="An old brass bank vault lock mechanism with two large keys beside it" credit="Minnesota Historical Society" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File%3AGerman_American_Bank_vault_lock.jpg"}
The vault lock and two keys of the National German American Bank, Saint Paul (in use 1856 to 1885).
:::
:::

:::step{type=concept title="Pausing a run" file="25-human-in-the-loop/agent.py" line="13-21"}
```python
create_agent(..., checkpointer=InMemorySaver(),
             middleware=[HumanInTheLoopMiddleware(interrupt_on={
                 "book_storage": {"allowed_decisions": ["approve", "edit", "reject"]}})])
```

`interrupt_on` maps a tool's name to the decisions the manager may make about it. When the model asks for
`book_storage`, the middleware stops the run **before the tool runs**. The run's state (every message, the pending
tool call) is saved by the checkpointer under the thread id, and `invoke` returns a result with an extra key,
`__interrupt__`: a list of pauses, each with a `.value`. `main.py` reads `result["__interrupt__"][0].value`, which
was, in a real run:

```text
{'action_requests': [{'name': 'book_storage', 'args': {'crates': 80, 'days': 10, 'crop': 'onion'}, ...}],
 'review_configs': [{'action_name': 'book_storage', 'allowed_decisions': ['approve', 'edit', 'reject']}]}
```

By default all the calls the model asks for in one turn wait in one pause, as a list (`action_requests`). Tools not
listed (`mandi_price`, `storage_cost`) run as before. The checkpointer is required: without saved state there is
nothing to come back to.
:::

:::step{type=task task=approval_middleware title="Your turn: every booking waits" file="25-human-in-the-loop/agent.py" line="13-21"}
In `booking_agent()`, add one argument after `checkpointer=InMemorySaver(),`:

1. `middleware=[HumanInTheLoopMiddleware(interrupt_on={...})]`
2. In `interrupt_on`, the key `"book_storage"` and the value `{"allowed_decisions": ["approve", "edit", "reject"]}`.

The usual slip, and a dangerous one: a misspelled tool name. We tried `"book-storage"` (a dash): no error, no pause,
and the booking was made without the manager. The name must match the tool's name exactly.

Press **Check**.
:::

:::step{type=concept title="Resuming with a decision" file="25-human-in-the-loop/agent.py" line="24-28"}
To continue, invoke the **same thread** with a `Command` carrying the decision:

```python
agent.invoke(Command(resume={"decisions": [decision]}), {"configurable": {"thread_id": "M-104"}})
```

| Decision | Shape | What happens |
|---|---|---|
| approve | `{"type": "approve"}` | the tool runs as the model asked |
| edit | `{"type": "edit", "edited_action": {"name": "book_storage", "args": {...}}}` | the tool runs with the manager's arguments, and the model is told a person changed the call |
| reject | `{"type": "reject", "message": "..."}` | the tool does not run; the model receives the reason and tells the member |

What the model really receives, from our run (the tool's result, as a `ToolMessage`):

- After the edit: "Note: a human reviewer replaced this tool call before it ran. ... Do not re-issue your original
  call. Executed instead: book_storage with arguments {"crates": 50, ...}. Tool response: Booked 50 crates of onion
  for 10 days, number B-101."
- After the reject: "User rejected the tool call for `book_storage` with reason: The grape chamber is full this week."

The pause can last seconds or days: with a database checkpointer, the run survives restarts in between.

:::diagram{name="lc-human-loop"}
Ravi's real booking from this chapter's run: paused before the tool, edited by the manager, resumed on the same thread.
:::
:::

:::step{type=task task=resume_decision title="Your turn: the manager decides" file="25-human-in-the-loop/agent.py" line="24-28"}
Finish `manager_decides(agent, thread_id, decision)`:

1. Wrap the decision: `Command(resume={"decisions": [decision]})` (a list, one decision per paused call).
2. Invoke the agent with it, on the same thread: `{"configurable": {"thread_id": thread_id}}`.
3. Return what `invoke` returns.

The usual slips (both tried):

- `Command(resume=decision)`, without the `{"decisions": [...]}` wrapper: `KeyError: 'decisions'`.
- A different thread id: nothing is resumed, and the member's booking stays waiting.

```bash run
cd /workspace/25-human-in-the-loop && python main.py
```

Press **Check**.
:::

:::step{type=try title="Approve, edit, reject"}
A real run (again on 25 November: the same pauses, the same bookings, and nearly the same words):

```text
$ python main.py
[M-104] > Please book 80 crates of onions for 10 days.
  paused, waiting for the manager: book_storage {'crates': 80, 'days': 10, 'crop': 'onion'}
  the manager decides: edit
  I have booked 50 crates of onions for 10 days. Your booking number is B-101. Please let me know if you need anything else!

[M-221] > Book 20 crates of tomatoes for 5 days, please.
  paused, waiting for the manager: book_storage {'crates': 20, 'days': 5, 'crop': 'tomato'}
  the manager decides: approve
  I have booked 20 crates of tomatoes for 5 days. Your booking number is B-102.

[M-305] > Book 300 crates of grapes for 2 days.
  paused, waiting for the manager: book_storage {'crates': 300, 'days': 2, 'crop': 'grapes'}
  the manager decides: reject
  I cannot book the cold storage for grapes as the chamber is full this week. Please check back later or choose a different crop if you need storage.

bookings made: [{'crates': 50, 'days': 10, 'crop': 'onion'}, {'crates': 20, 'days': 5, 'crop': 'tomato'}]
```

Three members, three decisions, and every run paused before anything was booked.

- Ravi asked for 80 crates; the manager **edited** it to 50 (the 50-crate rule). The tool booked 50, and Navin told Ravi
  "50 crates". The model's own message still holds its call for 80; the note in the tool's result is what tells it
  the call was replaced.
- Asha's 20 crates were **approved** and booked as asked.
- The 300 crates of grapes were **rejected**. Nothing was booked, and Navin passed on the manager's reason. Read its last
  sentence, though: "choose a different crop" is not advice the co-op would give. The model filled the silence with a
  suggestion of its own; a reject message that says what the member can do leaves it less to invent. We tried "The grape chamber is full
  this week. Tell the member to call the office on Monday to book for next week." three times: all three answers were
  "Please call the office on Monday to book for next week", with nothing added. (The re-run gave the same invented
  advice as above, "You might want to try another crop", with the short reason.)

`bookings made` is the proof: two bookings, the edited one at 50.
:::

:::step{type=predict title="Guess first"}
:::question
The server restarts while a booking waits for the manager. With `InMemorySaver`, what happens to the paused run?
:::
- [ ] It resumes after the restart
- [x] It is lost: the saved state lived in the process's memory
- [ ] The booking is made automatically
:::explain
Pauses that may last hours need a database checkpointer (PostgresSaver), like any state that must survive a restart.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When exactly does the run pause?
:::
- [ ] Before the model is called
- [x] After the model asks for `book_storage`, before the tool runs
- [ ] After the booking is made
:::explain
The model has decided; nothing has happened yet. That is the moment a person can still change it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is the model told when the manager edits a call?
:::
- [x] So it does not repeat its original call, and answers about what really happened
- [ ] To make it apologise
- [ ] The API requires it
:::explain
Its own message still holds the original call (80 crates). The note says "Do not re-issue your original call" and
names the call that ran, so the model answers about 50.
:::
:::

:::step{type=deep-dive title="Go deeper: people in the loop"}
**Approve only what matters.** `interrupt_on` can list several tools; read-only tools should not wait for anyone.

**A fourth decision.** `{"type": "respond", "message": "..."}` skips the tool and gives the model the person's
answer as if it were the tool's result. Useful when the manager knows the answer already.

**A real approval screen.** The `__interrupt__` value is data: an app shows it to the manager, and sends back the
decision with the thread id (chapter 27 does this over HTTP).

**Several calls at once.** If the model asks for two bookings in one turn, the interrupt holds two action requests, and
the resume carries one decision for each, in order (decisions are matched to calls by position). Another setting,
`interrupt_mode="per_call"`, pauses once per call instead.
:::

:::step{type=recap}
You can now:

- pause an agent before chosen tools with `HumanInTheLoopMiddleware`, with the tool's exact name;
- read an interrupt and the actions waiting in it;
- resume a thread with approve, edit or reject;
- explain why a checkpointer is required, and when it must be a database.

Next, chapter 26: testing Navin, with a golden set and a second model as judge.

:::photo{src="/lesson-images/langchain/lc-25-notes.webp" alt="Handwritten notes about a person in the loop: HumanInTheLoopMiddleware pauses before a listed tool runs. The checkpointer keeps the paused thread. Resume the same thread with Command(resume=...). The manager can approve, edit or reject. A misspelled tool name means no pause at all. A reject message that says what to do left less to invent." ai="true"}
One page of notes for this chapter.
:::
:::
