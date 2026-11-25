:::step{type=story title="Harsh, complete"}
Harsh started in chapter 1 as two nodes and a keyword list. Now it can be the board's real desk. One server answers
every citizen. A message is read once by an **intake** model, then handled by the right part of the desk:

- questions about complaints go to the **status agent**, which looks up tickets with tools (chapter 13);
- questions about charges and rules go to the **rules agent**, which searches the rulebook (chapter 15);
- reports of broken things go to **repairs**, where anything over Rs 50,000 waits for the executive engineer
  (chapter 10), whose answer arrives over HTTP;
- anything else gets a polite hand-over to a person.

Each agent is a `create_agent` graph used as a node (chapter 16), the server keeps every thread (chapter 21), and a
shared rate limiter keeps the whole desk under the gateway's limit.

:::mission
Route each intent to its part of the desk, then let the engineer approve a paused repair through the server, and read
the whole conversation as the board would.
:::
:::

:::step{type=history title="From a keyword list to a desk"}
:::before{title="Chapter 1"}
Two nodes, a keyword list, and a promise of hours: everything Harsh knew fitted on one screen.
:::

Each part of this course added one idea that production systems need: state and reducers, branches and loops (Part 1);
memory, durability, people in the loop and history (Part 2); agents, checks, retrieval, teams and streaming (Part 3);
tests, a server and longer tasks (Part 4). None of them is specific to water boards. A bank's dispute desk, a
hospital's appointment line or a railway's help desk is built from the same parts, in a different order.

:::solved
**A desk that is explainable at every step**: the graph says where each message can go, the checkpoints say where it
went, and every decision with money or safety in it is in code or with a person.
:::

:::timeline
- **Part 1** Thinking in graphs.
- **Part 2** Persistence and people.
- **Part 3** Agents in graphs.
- **Part 4** Production.
:::
:::

:::step{type=concept title="The desk graph" file="24-capstone/harsh/graph.py" line="22-72"}
```python
graph.add_edge(START, "intake")
graph.add_conditional_edges("intake", route_intent, ["status", "rules", "repair", "other"])
```

| Node | What it is | From chapter |
|---|---|---|
| `intake` | one model call with structured output: `Intent(kind, problem, street)` | 4 |
| `status` | `create_agent` with the ticket tools, added as a node | 13, 16 |
| `rules` | `create_agent` with the rulebook search tool | 15, 16 |
| `repair` | Python: the cost table, `interrupt` over Rs 50,000, then a booking | 6, 10 |
| `other` | a fixed message: a person will read it | 14 |

`Desk` extends `MessagesState` with `intent` and `approved`. The two agents share `messages` with the desk, so they see
the conversation and add their answer to it. The cost of a repair comes from a table in Python, never from the model.
:::

:::step{type=task task=route_intent title="Your turn: every message to its place" file="24-capstone/harsh/graph.py" line="35-38"}
Finish `route_intent(state)`:

1. read `state["intent"]["kind"]`;
2. return `"status"`, `"rules"` or `"repair"` when it is that word, and `"other"` for anything else.

The usual slip: `state["intent"].kind`. The intent is stored as a dictionary (`intake` saves `intent.model_dump()`),
so it needs `["kind"]`; we tried the attribute: `AttributeError: 'dict' object has no attribute 'kind'`.

Press **Check**.
:::

:::step{type=concept title="The engineer's answer, over HTTP" file="24-capstone/client.py" line="10-14"}
A paused run on the server is resumed the way chapter 10 resumed one in Python, with the command sent as JSON:

```python
client.runs.wait(thread_id, "harsh", command={"resume": {"approve": True, "note": "before the evening rush"}})
```

The engineer's app needs only the thread id and her answer. The server finds the run waiting at `repair`, runs that node
again from its first line, and this time `interrupt` returns her decision.

:::diagram{name="lg-capstone"}
The real conversation of 26 November, message by message, on one server thread.
:::
:::

:::step{type=task task=approve_over_api title="Your turn: the engineer's answer over HTTP" file="24-capstone/client.py" line="10-14"}
Finish `decide(client, thread_id, approve, note)`: return `client.runs.wait(thread_id, "harsh", command={"resume":
{"approve": approve, "note": note}})`.

The usual slip: `input={"resume": ...}` instead of `command=`. We tried it on the server: no error, and the thread was
still waiting at `repair` afterwards. An answer to an interrupt must travel as a command.

```bash run
cd /workspace/24-capstone && (langgraph dev --no-browser --port 2024 > server.log 2>&1 &) && sleep 10 && python client.py
```

Press **Check**. (If a server from chapter 21 is still running on port 2024, stop it first: `pkill -f "langgraph dev"`.)
:::

:::step{type=try title="One conversation, the whole desk, and the lesson of chapter 6 again"}
```text
$ (langgraph dev --no-browser --port 2024 > server.log 2>&1 &); for i in $(seq 1 80); do curl -s localhost:2024/ok > /dev/null && break; sleep 0.5; done; curl -s localhost:2024/ok; echo
{"ok":true,"services":{}}
$ timeout 300 python client.py
> Any update on my complaints? My number is 98220.
  Harsh: You have two open complaints: 

1. **Ticket T-4471**: Crew assigned from East zone crew 2, scheduled to visit on Wednesday between 8:00 to 11:00.
2. **Ticket T-4475**: Water sample taken by the health team, with lab results expected by Wednesday at 18:00.
> Do we have to pay for the tanker? Water has been off since Monday because of the burst.
  Harsh: If the piped water has been off for more than 24 hours due to a board fault, the tanker service is provided free of charge. You can request a tanker before 2 PM for same-day delivery. Private tankers hired by citizens are not reimbursed by the board.
> The main on Station Road has burst, water is flooding the road!
  (waiting for the engineer: main_burst at Station Road, Rs 65,000)
[engineer] approve, note: before the evening rush
  Harsh: A crew is booked for the main burst at Station Road: Thursday, 9:00 to 12:00.
```

(We ran it again on 26 November, on a fresh server: the same three paths and the same Thursday booking; the answers
were worded a little differently, for example "the board will send a tanker free of charge". The whole conversation
used 10,469 tokens.)

One thread, three kinds of message, three parts of the desk. The status answer came from the tickets, the tanker answer
from the rulebook (with its conditions, "if ... due to a board fault", not a guess), and the burst main paused for the
engineer, whose approval came in through the server.

Now read the last two lines as the people on Station Road would. Water is flooding the road, and the desk first
**waited for an approval** and then booked a crew for **Thursday**. The engineer even wrote "before the evening rush";
the booking ignored her note. This is chapter 6's lesson, returning at the end: the graph checks the **cost** and not
the **urgency**. A burst main is an emergency; the right graph sends an emergency crew at once, whatever it costs, and
asks the engineer to approve the bill afterwards. The fix is one more branch in `repair` and one more test in
chapter 20's style. Every graph in this course worked as written; the important questions were always about what it was
written to do.
:::

:::step{type=predict title="Guess first"}
:::question
The intake model returns `kind: "complaint"`, a word that is not in the `Literal`. What happens?
:::
- [ ] It goes to other
- [x] The structured output fails validation before `route_intent` runs, and the run reports the error
- [ ] It goes to status
:::explain
We tried it: `Intent(kind="complaint")` raises `ValidationError: 1 validation error for Intent, kind`. The schema
guards the router, as in chapter 4. A retry policy on intake (chapter 9) makes such failures recover.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does the Rs 65,000 come from?
:::
- [x] `REPAIR_COST`, a table in Python, chosen by the problem the intake found
- [ ] The model's estimate
- [ ] The engineer
:::explain
Money and promises stay in code; the model only says which problem it is.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What should change so a flooding main gets a crew today?
:::
- [ ] A bigger model
- [x] A branch for emergencies before the approval, and a test that proves it
- [ ] A longer prompt for intake
:::explain
Urgency is a rule of the board. Rules belong in the graph, and in its tests.
:::
:::

:::step{type=deep-dive title="Go deeper: from here to production"}
**Deploy.** The same `langgraph.json` builds a container (`langgraph build`) for a server with Postgres and Redis.

**Observe.** Tracing every run (LangSmith, or OpenTelemetry) shows each node's inputs, outputs, tokens and time; the
first thing to look at when a citizen complains about an answer.

**Evaluate.** Collect real messages, label where each should go, and measure the intake's routing every time a prompt
changes (the LangChain course, chapter 26).

**Guard.** Personal data in messages (chapter 24 of the LangChain course), rate limits per citizen, and a person on call
for everything the desk hands over.
:::

:::step{type=recap}
You can now:

- compose a production graph from agents, Python nodes and an approval step;
- route by a model's structured intent, with every route's target in code;
- resume a paused run over HTTP from another app;
- read a working system for what it was not written to do.

That is the end of the course. Harsh began as two nodes; it is now a desk that remembers, pauses for people, looks
things up, checks itself, and runs as a server. Build the emergency branch next.

:::photo{src="/lesson-images/langgraph/lg-24-notes.webp" alt="Handwritten notes titled Harsh, complete, one server, the whole desk: an intake model reads each message once and names its kind, code routes it to the status agent, the rules agent, repairs or a person, and big repairs wait for the engineer whose answer comes over HTTP; message, intake kind, route_intent, status, rules or repair, reply; status came from the tickets and the tanker answer from the rulebook; Rs 65,000 waited for the engineer; approved, then booked for Thursday; check urgency before cost" ai="true"}
One page of notes for this chapter.
:::
:::
