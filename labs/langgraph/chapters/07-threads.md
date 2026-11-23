:::step{type=story title="Any update?"}
Harsh now answers on WhatsApp. A citizen writes "No water in Tilak Nagar, lane 3, since yesterday morning." An hour
later the same phone writes "Any update?". To the graph of Part 1, that second message is a brand-new run: it has no
idea which street, which problem, or that this person wrote before. Every run starts empty and forgets everything when it
ends.

People do not talk like that, and a help desk cannot work like that. Harsh needs **memory per conversation**: each phone
number gets its own thread, and every message in a thread sees the ones before it. That memory must also survive a
restart, because the server that runs Harsh is restarted every night.

LangGraph does this with a **checkpointer**: after every step, it saves the whole state of the thread.

:::mission
Give Harsh a checkpointer and one thread per phone number, then keep the threads in a SQLite file so a conversation
survives a restart.
:::
:::

:::step{type=history title="Save points and sessions"}
:::before{title="Long jobs that started over"}
On early computers a job that ran for hours and stopped near the end, because of a power cut or a card jam, had to be
run again from the beginning.
:::

IBM's **OS/360** (announced in **1964**) offered **checkpoint/restart**: a long job could save its progress at
checkpoints and, after a failure, continue from the last one instead of from the start. The web met the same problem
from the other side. HTTP (**1991**) forgets each visitor between requests; in **1994** Lou Montulli at Netscape added
**cookies**, a small id the browser sends back, so a site could find that visitor's session. A LangGraph thread is
both ideas together: the `thread_id` is the cookie, and the checkpoints are the saved progress.

:::solved
**Conversations and jobs that remember.** A thread can be continued tomorrow, after a restart, on another server, as
long as you know its id.
:::

:::timeline
- **1964** OS/360: checkpoint and restart.
- **1991** HTTP: every request forgets the last.
- **1994** Cookies: an id that finds your session.
- **2024** LangGraph checkpointers and threads.
:::

An IBM System/360 Model 30, one of the machines OS/360 ran on. A job that saved checkpoints on it could lose a power cut's worth of work instead of a night's.

:::photo{src="/lesson-images/langgraph/s360.webp" alt="A large red IBM System/360 cabinet with a grey operator panel full of switches, dials and lamps, beside a desk" credit="ArnoldReinhold" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:IBM_System_360_model_30_profile.agr.jpg"}
An IBM System/360 Model 30 at the Computer History Museum.
:::
:::

:::step{type=concept title="A checkpointer and a thread id" file="07-threads/chat.py" line="23-37"}
Two changes turn a forgetful graph into one with memory:

```python
app = graph.compile(checkpointer=InMemorySaver())       # 1. save the state after every step
config = {"configurable": {"thread_id": "98220"}}       # 2. say which thread this run belongs to
app.invoke({"messages": [HumanMessage("Any update?")]}, config)
```

With a checkpointer, `invoke` first **loads** the thread's last saved state, applies your input to it (here the
`add_messages` reducer of `MessagesState` appends the new message), runs the graph, and saves after every step. A new
`thread_id` starts empty; the same one continues.

| Checkpointer | Where it saves | Use it for |
|---|---|---|
| `InMemorySaver` | the process's memory | tests and notebooks: gone when the process ends |
| `SqliteSaver` | a SQLite file | one server, small apps, this course |
| `PostgresSaver` | a Postgres database | production, many servers sharing threads |

`app.get_state(config)` shows a thread's saved state at any time, without running anything.

:::diagram{name="lg-threads"}
Two phones, two threads: each run loads its own thread, adds to it, and saves it again.
:::
:::

:::step{type=task task=thread_memory title="Your turn: one thread per phone" file="07-threads/chat.py" line="23-37"}
In `build_graph`, pass the checkpointer to `compile`. In `ask`, make the config
`{"configurable": {"thread_id": phone}}` and pass it to `invoke` as the second argument.

Press **Check**.
:::

:::step{type=concept title="Memory on disk" file="07-threads/chat.py" line="40-43"}
`InMemorySaver` forgets everything when the process ends, which is exactly what happens every time you run
`python main.py`. A `SqliteSaver` keeps the checkpoints in a file:

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

saver = SqliteSaver(sqlite3.connect("harsh.db", check_same_thread=False))
```

`check_same_thread=False` lets LangGraph use the connection from its worker threads. The file holds every checkpoint of
every thread; the next process that opens it finds them all.
:::

:::step{type=task task=sqlite_saver title="Your turn: a chat that survives a restart" file="07-threads/chat.py" line="40-43"}
Finish `open_saver(path)`: return `SqliteSaver(sqlite3.connect(path, check_same_thread=False))`.

```bash run
cd /workspace/07-threads && python main.py 98220 "No water in Tilak Nagar, lane 3, since yesterday morning."
```

```bash run
cd /workspace/07-threads && python main.py 98220 "Any update? Also, the little water that came at night was brown."
```

Press **Check**.
:::

:::step{type=try title="Three processes, two threads, and an answer that made things up"}
Each command is a separate process, like three WhatsApp messages arriving hours apart:

```text
$ python main.py 98220 "No water in Tilak Nagar, lane 3, since yesterday morning."
Harsh: A crew will be assigned to address the water issue in Tilak Nagar, lane 3. You will receive an SMS with updates.
(2 messages saved in thread 98220)
$ python main.py 98220 "Any update? Also, the little water that came at night was brown."
Harsh: A crew is still working on the issue in Tilak Nagar, lane 3. You will receive an SMS with further updates soon.
(4 messages saved in thread 98220)
$ python main.py 70300 "Any update?"
Harsh: A crew will be assigned to address your issue, and you will receive an SMS with further details. Thank you for your patience!
(2 messages saved in thread 70300)
```

The memory works. The second process had never seen "Tilak Nagar, lane 3", yet the answer used it: the checkpointer
loaded the thread from `harsh.db`, and the state grew from 2 to 4 messages. The other phone, 70300, got its own empty
thread.

Now read the answers as the board would. The second one says "a crew is **still working**": no crew was ever assigned;
the model invented a status because the chat has no access to real tickets. It also ignored the most important words,
"the little water that came was **brown**": dirty water is urgent (chapter 1), and it should have been escalated. The
third answer pretends to know "your issue" in a thread where nothing was said. Memory gives the model the conversation;
it does not give it the facts. Parts 3 and 4 connect Harsh to the real ticket system with tools, and route dirty water
in code, as in Part 1.
:::

:::step{type=predict title="Guess first"}
:::question
You run `python main.py 98220 "..."` again, but `build_graph` now uses `InMemorySaver()` instead of the SQLite saver.
How many messages are saved in thread 98220 afterwards?
:::
- [ ] 6
- [x] 2: a new process starts with an empty memory, so the thread starts over
- [ ] 0
:::explain
`InMemorySaver` lives as long as the process. Each `python main.py` is a new process.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does LangGraph do first when you invoke a graph that has a checkpointer, with a thread id it has seen before?
:::
- [x] Loads that thread's last saved state, and applies the new input to it
- [ ] Starts from an empty state
- [ ] Replays every earlier run
:::explain
The input is merged into the saved state by the reducers, here appended to the messages.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did the second answer claim "a crew is still working"?
:::
- [ ] The checkpointer saved a wrong status
- [x] The model has only the chat, no real ticket data, and filled the gap with something likely
- [ ] The thread id was wrong
:::explain
Memory stores what was said, not what is true. Facts come from tools and code.
:::
:::

:::step{type=deep-dive title="Go deeper: threads in production"}
**Choosing thread ids.** One thread per conversation is the usual choice: per phone number for a chat, per ticket for a
job, per user and session for an app. A thread id is a lookup key; anyone who knows it can continue the thread, so treat
it like a session id.

**Postgres.** `PostgresSaver` (package `langgraph-checkpoint-postgres`) stores the same checkpoints in Postgres, so
several servers can serve the same threads. Call `saver.setup()` once to create its tables.

**Size and cost.** A checkpoint is saved after every step, and a chat thread grows with every message. The next chapter
keeps long threads small and cheap.
:::

:::step{type=recap}
You can now:

- explain why a graph without a checkpointer forgets everything between runs;
- give a graph memory with a checkpointer and a `thread_id`;
- keep threads on disk with `SqliteSaver`, so they survive a restart;
- tell memory (what was said) apart from facts (what is true).

Next, chapter 8: long chats, trimmed and summarised.

:::photo{src="/lesson-images/langgraph/lg-07-notes.webp" alt="Handwritten notes about checkpointers and threads: checkpointer = save after every step; thread_id = which conversation; same id: continue. New id: empty; SQLite file survives a restart; memory is not facts!" ai="true"}
One page of notes for this chapter.
:::
:::
