:::step{type=story title="A complaint desk that must not get lost"}
The Ujjwal Nagar Water Board gets about two hundred complaints a day: brown water from the tap, no water since
morning, a pipe burst outside the school, a bill three times too high. Each one goes through the same journey:
understand it, decide how serious it is, find the street's zone, send it to the right team, get approval for big
repairs, tell the citizen, check later that it was fixed.

In this course you build **Harsh**, the board's complaint-to-repair desk. Harsh is not one clever prompt: it is a
**workflow** with steps, decisions, loops, pauses for a person's approval, and memory that survives a restart. Some
steps call a model; many are plain Python. **LangGraph** is the library for exactly that: you draw the workflow as a
**graph**, and LangGraph runs it, step by step, with its state saved along the way.

You already know agents from the LangChain course; here you build what is underneath them.


Most towns in India keep their water in tanks like this one, raised on columns so the water reaches every tap by gravity. Every leak, dry tap and brown glass of water in such a town ends up as a complaint at a desk like Harsh.

:::photo{src="/lesson-images/langgraph/watertank.webp" alt="A round concrete water tank on tall columns, with a spiral staircase winding up one side, against a cloudy sky" credit="Vraj Acharya, WELL Labs" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Overhead_water_tank_rural_Raichur_Karnataka_India_water_tower.jpg"}
An overhead water tank in a village in Raichur district, Karnataka.
:::
:::mission
Build Harsh's first graph: a complaint goes in, is classified, and gets a first reply. Then watch it run, step by step.
:::
:::

:::step{type=concept title="Three words: state, nodes, edges" file="01-why-graphs/graph.py" line="9-21"}
A LangGraph graph has three parts:

| Part | Here | What it is |
|---|---|---|
| **State** | `Ticket`: text, kind, reply | a dictionary that travels through the graph |
| **Nodes** | `classify`, `write_reply` | plain Python functions: they read the state and return an **update** (only the keys they change) |
| **Edges** | START -> classify -> write_reply -> END | which node runs next |

```python
def classify(state: Ticket) -> dict:
    return {"kind": kind_of(state["text"])}     # an update: LangGraph merges it into the state
```

A node never changes the state directly; it returns what should change. That one rule is what lets LangGraph save the
state after every step, show you each step, pause, and resume: the rest of this course depends on it.

Nodes and edges are older than computers. In 1736 Leonhard Euler solved a puzzle about a city's bridges by drawing each piece of land as a dot and each bridge as a line, and graph theory began.

:::photo{src="/lesson-images/langgraph/euler.webp" alt="A painted portrait of Leonhard Euler in a dark coat and a cloth cap, looking slightly to one side" credit="Jakob Emanuel Handmann" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Leonhard_Euler_-_Jakob_Emanuel_Handmann_(Kunstmuseum_Basel).jpg"}
Leonhard Euler, painted by Jakob Emanuel Handmann in 1753.
:::
:::

:::step{type=history title="From state machines to Pregel"}
:::before{title="Logic hidden in nested ifs"}
A process with many steps and decisions, written as nested `if`s and loops, works until someone has to change it: no
picture shows what happens when, and no step can be paused or replayed.
:::

Engineers have drawn processes as states and transitions for a long time: George Mealy (**1955**) and Edward Moore
(**1956**) described **finite state machines**, still used in everything from vending machines to network protocols. In
**2010** Google published **Pregel**, a system that ran computations on huge graphs in rounds called **super-steps**:
every active node runs, sends messages, and waits for the next round. LangGraph, released by LangChain in **January
2024**, takes its execution model from Pregel (its runtime is even called `pregel`), and LangGraph **1.0** arrived in
**October 2025**.

:::solved
**A workflow you can see, run, pause and replay.** The graph is the picture, and the picture is the program.
:::

:::timeline
- **1955 to 1956** Mealy and Moore: finite state machines.
- **2010** Pregel at Google.
- **2024** LangGraph.
- **2025** LangGraph 1.0.
:::

The city of Euler's puzzle was Konigsberg, built on both banks of the river Pregel and on two islands joined by seven bridges. Google named its graph system after that river, and LangGraph's runtime carries the name on.

:::photo{src="/lesson-images/langgraph/konigsberg.webp" alt="An old engraved bird's-eye map of Konigsberg, with the river winding through the city around two islands and bridges crossing it" credit="Merian-Erben" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Image-Koenigsberg,_Map_by_Merian-Erben_1652.jpg"}
Konigsberg and the river Pregel, engraved by the Merian heirs, 1652.
:::
:::

:::step{type=example title="Worked example: a one-node graph" file="01-why-graphs/graph.py" line="24-28"}
The smallest useful graph (only to read):

```python
graph = StateGraph(Ticket)             # the state's shape
graph.add_node("classify", classify)   # a name, and the function that runs
graph.add_edge(START, "classify")      # where it begins
graph.add_edge("classify", END)        # where it ends
app = graph.compile()                  # checks the graph and makes it runnable
app.invoke({"text": "No water since morning"})   # {'text': ..., 'kind': 'no_water'}
```

`compile()` checks the graph (for example, an edge to a node that does not exist) and returns something you can
`invoke` and `stream`, like a LangChain model or agent.
:::

:::step{type=task task=first_graph title="Your turn: Harsh's first graph" file="01-why-graphs/graph.py" line="24-28"}
Finish `build_graph()`: add the nodes `"classify"` and `"write_reply"`, the edges START -> classify -> write_reply ->
END, and return `graph.compile()`.

Press **Check**.
:::

:::step{type=concept title="Watching a graph run" file="01-why-graphs/graph.py" line="31-35"}
`invoke` returns the final state. `stream` returns the run **step by step**. With `stream_mode="updates"`, each item is
a dictionary from the node that just ran to the update it returned:

```python
for update in app.stream({"text": "Pipe burst near the school"}, stream_mode="updates"):
    print(update)          # {'classify': {'kind': 'leak'}}, then {'write_reply': {'reply': '...'}}
```

You will use streams to show progress, to debug a graph, and (later) to see exactly where a run paused.
:::diagram{name="lg-run"}
Watch the state grow: each node returns only its own keys, and LangGraph merges them in.
:::
:::

:::step{type=task task=trace_steps title="Your turn: the steps of a run" file="01-why-graphs/graph.py" line="31-35"}
Finish `steps(text)`: stream the graph with `stream_mode="updates"` and return the node names, in the order they ran.

```bash run
cd /workspace/01-why-graphs && python main.py
```

Press **Check**.
:::

:::step{type=try title="Three complaints, and the graph's own picture"}
```text
$ python main.py
> The water from our tap is brown and smells bad.
  {'text': 'The water from our tap is brown and smells bad.', 'kind': 'dirty_water', 'reply': 'Complaint received (dirty water). We will respond within 4 hours.'}
> There is no water in Gandhi Chowk since morning.
  {'text': 'There is no water in Gandhi Chowk since morning.', 'kind': 'no_water', 'reply': 'Complaint received (no water). We will respond within 24 hours.'}
> My bill shows 900 litres a day, we are two people.
  {'text': 'My bill shows 900 litres a day, we are two people.', 'kind': 'billing', 'reply': 'Complaint received (billing). We will respond within 72 hours.'}

steps: ['classify', 'write_reply']

---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	classify(classify)
	write_reply(write_reply)
	__end__([<p>__end__</p>]):::last
	__start__ --> classify;
	classify --> write_reply;
	write_reply --> __end__;
...
```

(The diagram text is shortened with "...".) Each final state holds everything the run learned: the text it started
with, the kind `classify` added, the reply `write_reply` added. The promised hours come from the board's rules in
`rules.py`: 4 for dirty water, which can make people ill; 72 for a bill.

The last part is the graph describing itself: `get_graph().draw_mermaid()` prints a Mermaid diagram, the same format
GitHub and many documentation tools draw. As the graphs in this course grow, this picture is how you check that the
graph you built is the graph you meant.
:::

:::step{type=predict title="Guess first"}
:::question
`classify` returns `{"kind": "leak"}`. What happens to `text`, which it did not return?
:::
- [ ] It is deleted
- [x] It stays: an update only changes the keys it contains
- [ ] It becomes None
:::explain
Nodes return updates, and LangGraph merges them into the state. Chapter 2 shows how to control that merge.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `compile()` do?
:::
- [x] Checks the graph and returns a runnable object with invoke and stream
- [ ] Turns Python into machine code
- [ ] Calls the model
:::explain
A graph is a description until it is compiled; compiling also catches mistakes such as an edge to a node that does
not exist.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why do nodes return updates instead of changing the state themselves?
:::
- [ ] It is faster
- [x] So LangGraph can merge, save and show every step, which makes pausing and replaying possible
- [ ] Python dictionaries cannot be changed
:::explain
Every later feature (checkpoints, time travel, human approval) rests on steps being clean updates.
:::
:::

:::step{type=deep-dive title="Go deeper: graphs and agents"}
**create_agent is a graph.** LangChain's `create_agent` builds a LangGraph graph with two nodes, `model` and `tools`, and a
loop between them. In Part 3 you build that graph yourself.

**Workflows and agents.** In a **workflow** the graph's edges decide what happens next; in an **agent** a model
decides. LangGraph does both, and most real systems mix them: fixed steps where the rules are known, a model where they
are not.

**When not to use a graph.** Two steps in a fixed order need no graph: a function calling a function is clearer. Graphs
pay off with branches, loops, pauses, parallel work, or state that must survive a restart.
:::

:::step{type=recap}
You can now:

- describe a graph as state, nodes and edges;
- build and compile a `StateGraph`, and run it with `invoke`;
- watch a run step by step with `stream(stream_mode="updates")`;
- print a graph's own diagram with `draw_mermaid()`.

Next, chapter 2: state that grows. Reducers decide how each update joins the state.

:::photo{src="/lesson-images/langgraph/lg-01-notes.webp" alt="Handwritten notes about graphs: a graph = nodes + edges; state flows through every node; node: state in, update out; START -> ... -> END; compile() before invoke()" ai="true"}
One page of notes for this chapter.
:::
:::
