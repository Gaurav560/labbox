:::step{type=story title="Harsh needs a front door"}
Until now Harsh ran inside `python main.py`. The board's WhatsApp bridge, its website and the engineer's approval app
cannot import a Python file. They need a **server**: an address they can send a message to, which runs the graph, keeps
each conversation's thread, streams progress back, and survives many citizens writing at once.

You could write that server yourself with FastAPI, threads, a database and a job queue. LangGraph ships one. A file
called `langgraph.json` says where the graph is; `langgraph dev` runs it on your machine with an HTTP API for
**threads** (conversations) and **runs** (one execution of the graph on a thread); and the `langgraph_sdk` client talks
to it from any Python program. The same app can later be deployed to a production server unchanged.

:::mission
Make the graph acceptable to the server (it refuses one detail of how you built graphs so far), start it with
`langgraph dev`, then write the client function that sends a citizen's message and returns Harsh's answer.
:::
:::

:::step{type=history title="From scripts to servers"}
:::before{title="One program per request"}
Early web pages that did any work started a whole program for every request, and forgot everything when it ended.
:::

In **1993** the **Common Gateway Interface** let a web server run a script for each request. Python standardised how
servers call Python code with **WSGI** in **2003**, and with **ASGI** for long-lived, streaming connections in
**2019**. Agents needed more than a request and a response: conversations that last for days, runs that pause for a
person, streams of tokens, background work. In **2024** LangChain released a server built for exactly that, now called
the **Agent Server**, with threads, runs, streaming and a persistence layer of its own; `langgraph dev` runs it on your
laptop.

:::solved
**Any program can talk to Harsh.** Over HTTP, with threads kept and runs managed by the server, not by your code.
:::

:::timeline
- **1993** CGI: a script per request.
- **2003** WSGI; **2019** ASGI for streaming.
- **2024** A server for agents: threads and runs.
:::
:::

:::step{type=concept title="An app the server can load" file="21-server/harsh/graph.py" line="17-29"}
A LangGraph app is a folder:

```text
21-server/
  langgraph.json        which graphs to serve, and where they are
  harsh/                the app's code, as a package
    graph.py            builds the graph; ends with   graph = build_graph()
    prompts.py          the prompts, reviewed on their own
    tickets.py          the tools
  client.py             a program that talks to the server
```

`langgraph.json` names the graph `harsh` and points at the module-level variable:

```json
{
  "dependencies": ["."],
  "graphs": {"harsh": "./harsh/graph.py:graph"},
  "env": {"LANGSMITH_TRACING": "false"}
}
```

Every graph in this course so far was compiled with its own checkpointer. The server refuses that. Starting it with the
unfinished `graph.py` gives:

```text
Graph 'harsh' failed to load: ValueError: Heads up! Your graph 'graph' from './harsh/graph.py' includes a custom checkpointer (type <class 'langgraph.checkpoint.memory.InMemorySaver'>). With LangGraph API, persistence is handled automatically by the platform, ...
To simplify your setup and use the built-in persistence, please remove the custom checkpointer ...
```

(Shortened with "..."; we started the starter graph again on 26 November and got the same message, and the server did
not start.) The server keeps every thread in its own store: for `langgraph dev`, in memory, saved to files in a
`.langgraph_api` folder next to `langgraph.json`; in production, in Postgres. Your graph only describes the work.
:::

:::step{type=task task=server_graph title="Your turn: a graph the server accepts" file="21-server/harsh/graph.py" line="17-29"}
In `build_graph`, compile without a checkpointer: `return graph.compile()`, and remove the `InMemorySaver` import.

The usual slip: removing the import but keeping `checkpointer=InMemorySaver()`. Python then stops at once with
`NameError: name 'InMemorySaver' is not defined`, before the server's own message.

Start the server in the background and ask it whether it is up:

```bash run
cd /workspace/21-server && (langgraph dev --no-browser --port 2024 > server.log 2>&1 &) && sleep 8 && curl -s localhost:2024/ok
```

Press **Check**: it starts its own `langgraph dev` on your folder and sends it a message.
:::

:::step{type=concept title="Threads and runs, from a client" file="21-server/client.py" line="7-11"}
The SDK mirrors what you did by hand in Part 2:

| In Part 2 | Through the server |
|---|---|
| a `thread_id` you chose | `client.threads.create()` returns one |
| `app.invoke(input, config)` | `client.runs.wait(thread_id, "harsh", input=...)` |
| `app.stream(...)` | `client.runs.stream(thread_id, "harsh", input=..., stream_mode="updates")` |
| `app.get_state(config)` | `client.threads.get_state(thread_id)` |
| `Command(resume=...)` | `client.runs.wait(thread_id, "harsh", command={"resume": ...})` (chapter 24) |

Messages travel as JSON: `{"role": "user", "content": "..."}` going in, dicts with `"content"` coming out.
`runs.wait` returns the thread's state when the run finishes.

:::diagram{name="lg-server"}
The real run of 26 November: one thread, one run per message, and a restart.
:::
:::

:::step{type=task task=sdk_client title="Your turn: talk to the server" file="21-server/client.py" line="7-11"}
Finish `ask(client, thread_id, text)`:

1. `state = client.runs.wait(thread_id, "harsh", input={"messages": [{"role": "user", "content": text}]})`;
2. `return state["messages"][-1]["content"]`.

The usual slip: `state["messages"][-1].content`, as in the earlier chapters. Over HTTP the messages arrive as plain
dictionaries, not message objects, so it is `["content"]`; `.content` raises `AttributeError: 'dict' object has no
attribute 'content'`.

```bash run
cd /workspace/21-server && python client.py "Any update on my complaints?" "98220"
```

Press **Check**.
:::

:::step{type=try title="Two messages, one thread, kept by the server"}
```text
$ (langgraph dev --no-browser --port 2024 > server.log 2>&1 &); for i in $(seq 1 60); do curl -s localhost:2024/ok > /dev/null && break; sleep 0.5; done; curl -s localhost:2024/ok; echo
{"ok":true,"services":{}}
$ python client.py "Any update on my complaints?" "98220"
> Any update on my complaints?
  Please provide your phone number so I can check the status of your complaints.
> 98220
  You have two open complaints: 

1. **Ticket T-4471**: Crew assigned from East zone crew 2, scheduled to visit on Wednesday between 8:00 to 11:00.
2. **Ticket T-4475**: Water sample taken by the health team, with lab results expected by Wednesday at 18:00.
(thread 01a2098c: 9 messages saved by the server)
```

We ran it again on 26 November. The server answered the same way, except that this time the agent listed the two
tickets and asked "Would you like to know the status of either ticket?" instead of fetching both statuses: chapter
13's two paths again, and 6 messages saved instead of 9.

The same agent as chapter 13, now behind HTTP. The client never touched a checkpointer, yet the second message knew the
first: the server loaded thread `01a2098c`, ran the graph, and saved it. Nine messages: two from the citizen, the
first answer, two tool requests, three tool results and the final answer.

To stop the server: `pkill -f "langgraph dev"`. In production the same `langgraph.json` is built into a container and
run with Postgres and Redis behind it; the client code does not change.
:::

:::step{type=predict title="Guess first"}
:::question
You restart `langgraph dev` and send another message on thread `01a2098c`. What happens?
:::
- [x] The thread is still there: `langgraph dev` saves its threads to the `.langgraph_api` folder
- [ ] The thread is gone: a development server keeps nothing
- [ ] The server refuses to start
:::explain
We tried it on 26 November: after a restart, `threads.search()` found thread `01a214d7` with all 6 messages, loaded
from `.langgraph_api/store.pckl`. Delete that folder for a clean start. It is still a development server: one
machine, one folder. A deployed server keeps threads in Postgres.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the server refuse a graph with its own checkpointer?
:::
- [x] It provides persistence itself, for every thread, and one store must own them
- [ ] Checkpointers are slow
- [ ] Servers cannot use SQLite
:::explain
Two places saving the same thread would disagree. The server's store is the one source of truth.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is a run?
:::
- [ ] A thread
- [x] One execution of the graph on a thread, with its own id and status
- [ ] A server process
:::explain
A thread holds the conversation; each message starts a run on it. Runs can be waited on, streamed, or queued.
:::
:::

:::step{type=deep-dive title="Go deeper: serving graphs"}
**LangGraph Studio.** `langgraph dev` also serves the API that LangGraph Studio (a visual debugger) connects to: the
graph drawn live, each step's state, and time travel by clicking.

**Background runs.** `client.runs.create(...)` starts a run and returns at once; poll it, or join its stream later.
Long research runs (chapter 23) work this way.

**Double texting.** A citizen sends a second message while the first run is still working. The server's
`multitask_strategy` decides: queue it, interrupt the first run, or reject it.

**Your own server.** A FastAPI app that calls `graph.invoke` with a Postgres checkpointer works too; you then build the
threads API, queues and streaming yourself.
:::

:::step{type=recap}
You can now:

- lay out a LangGraph app with `langgraph.json` and a package;
- run it with `langgraph dev`, and know why the graph must not bring its own checkpointer;
- talk to it with the SDK: threads, runs and state;
- tell development (`langgraph dev`) from production (a deployed server with Postgres).

Next, chapter 22: Deep Agents, for long tasks with files and helpers.

:::photo{src="/lesson-images/langgraph/lg-21-notes.webp" alt="Handwritten notes titled A local server, langgraph dev, threads and runs: langgraph.json says where the graph is, and langgraph dev serves it over HTTP and keeps the threads itself, so the graph must not bring its own checkpointer; langgraph.json, langgraph dev, threads.create, runs.wait, the answer as JSON; with its own checkpointer the server refused the graph; after a restart the thread was still there; it is kept in .langgraph_api; messages come back as dicts, so use the content key" ai="true"}
One page of notes for this chapter.
:::
:::
