:::step{type=story title="Every office has its own way"}
The water board is not one desk. The **billing office** checks meter readings: a bill more than three times the
average is held until an inspector looks at the meter. The **repair office** books crews and orders parts, and has its
own words: it speaks of **jobs**, not tickets. Each office maintains its own process, and changes it without asking
the front desk.

Harsh's desk graph should **use** those processes, not copy them. LangGraph lets a compiled graph be used inside
another graph, as a node: a **subgraph**. There are two ways to connect one, depending on whether the two graphs speak
the same language.

:::mission
Add the billing office's graph as a node that shares the desk's keys, then call the repair office's graph from a node
that translates a ticket into a job and the job's log back into the ticket.
:::
:::

:::step{type=history title="Subroutines and modules"}
:::before{title="One long program"}
Early programs were written top to bottom. The same steps were copied wherever they were needed, and a fix had to be
made in every copy.
:::

In **1951**, on Cambridge's EDSAC, David Wheeler wrote **subroutines** that any program could jump into and return from
(the "Wheeler jump"); with Maurice Wilkes and Stanley Gill he published the first book of them the same year. In
**1972** David Parnas's paper **"On the Criteria To Be Used in Decomposing Systems into Modules"** argued that each
module should hide its own decisions behind a small interface, so it can change without breaking the rest. A subgraph is
both: a process you call by name, and an office that keeps its details to itself.

:::solved
**Graphs built from graphs.** Each office owns its graph; the desk composes them, and a change inside one office stays
inside it.
:::

:::timeline
- **1951** Subroutines on EDSAC.
- **1972** Parnas: modules that hide their decisions.
- **2024** LangGraph subgraphs.
:::

EDSAC at the University of Cambridge, where the first library of subroutines was written: racks of valves, and programs that could call each other's parts.

:::photo{src="/lesson-images/langgraph/edsac.webp" alt="Two men standing among tall racks of vacuum tubes and wiring in a plain room, a black and white photo" credit="Computer Laboratory, University of Cambridge" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:EDSAC_(12).jpg"}
EDSAC, Cambridge, around 1949.
:::
:::

:::step{type=concept title="Shared keys: the graph is the node" file="16-subgraphs/desk.py" line="36-47"}
The billing graph's state is `Bill` (`phone`, `readings`, `verdict`); the desk's `Ticket` also has `phone` and
`verdict`. When the keys are shared, the compiled graph itself is the node:

```python
graph.add_node("billing", build_billing())
```

LangGraph passes the parent's state in (the subgraph reads `phone`), runs the subgraph, and merges the keys they share
back (`verdict`). `readings` stays inside the billing graph: the desk never sees it, and does not need to.
:::

:::step{type=task task=add_subgraph title="Your turn: a graph as a node" file="16-subgraphs/desk.py" line="39-41"}
In `build_graph`, replace the empty function with the billing office's graph: `graph.add_node("billing",
build_billing())`.

Press **Check**.
:::

:::step{type=concept title="Different languages: translate in and out" file="16-subgraphs/desk.py" line="30-33"}
The repair graph's state is `Job` (`job`, `log`); the desk has `ticket` and `repair_log`. No keys are shared, so a node
function translates:

```python
def repairs(state: Ticket) -> dict:
    result = REPAIRS.invoke({"job": state["ticket"]})     # ticket -> job
    return {"repair_log": result["log"]}                  # log -> repair_log
```

The repair office can rename anything inside its graph; only this function needs to know both languages.

| | Shared keys | Different schemas |
|---|---|---|
| Add as | `add_node("billing", subgraph)` | a function that calls `subgraph.invoke(...)` |
| State in | the parent's keys, as they are | whatever the function passes |
| State out | the shared keys are merged back | whatever the function returns |

:::diagram{name="lg-subgraph"}
Billing shares keys and runs as the node itself; repairs is called through a function that translates both ways.
:::
:::

:::step{type=task task=map_state title="Your turn: translate in and out" file="16-subgraphs/desk.py" line="30-33"}
Finish `repairs(state)`: `result = REPAIRS.invoke({"job": state["ticket"]})`, then return
`{"repair_log": result["log"]}`.

```bash run
cd /workspace/16-subgraphs && python main.py
```

Press **Check**.
:::

:::step{type=try title="Three tickets, two offices, every inner step"}
```text
$ python main.py
> T-4490: My bill is Rs 2,400, usually Rs 600.
  {'triage': {'kind': 'billing'}}
  billing / {'load_readings': {'readings': [610, 590, 640, 600, 620, 605, 2410]}}
  billing / {'check_jump': {'verdict': 'held: 2410 litres a day against an average of 611; a meter inspector will visit'}}
  {'billing': {'phone': '98220', 'verdict': 'held: 2410 litres a day against an average of 611; a meter inspector will visit'}}

> T-4491: The meter bill looks high this month.
  {'triage': {'kind': 'billing'}}
  billing / {'load_readings': {'readings': [380, 410, 395, 400, 420, 390, 405]}}
  billing / {'check_jump': {'verdict': 'correct: 405 litres a day, close to the average of 399'}}
  {'billing': {'phone': '70300', 'verdict': 'correct: 405 litres a day, close to the average of 399'}}

> T-4492: Pipe burst outside the school gate.
  {'triage': {'kind': 'leak'}}
  repairs / {'book_crew': {'log': ['T-4492: crew booked']}}
  repairs / {'order_parts': {'log': ['T-4492: parts ordered']}}
  {'repairs': {'repair_log': ['T-4492: crew booked', 'T-4492: parts ordered']}}
```

`stream(..., subgraphs=True)` shows every step at every level: lines starting `billing /` come from inside the billing
graph, and the line after them is the subgraph's result as the desk sees it. Its update is `phone` and `verdict`, the
shared keys; `readings` stayed inside.

The first bill was held: 2,410 litres a day against an average of 611 is four times normal. The second was fine. The
third ticket went to repairs, and even though `repairs` is a plain function that calls `REPAIRS.invoke`, its inner steps
still appear under `repairs /`: LangGraph links a subgraph called inside a node to its parent run.
:::

:::step{type=predict title="Guess first"}
:::question
The billing office renames `verdict` to `decision` in its own graph. What happens to the desk?
:::
- [ ] Nothing
- [x] The desk's `verdict` stays empty: shared keys are matched by name
- [ ] LangGraph renames it automatically
:::explain
Sharing keys couples the graphs by their names. If an office's names may change, call it through a translating function.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When can a compiled graph be added directly with `add_node`?
:::
- [x] When it shares state keys with the parent graph
- [ ] Always
- [ ] Only without a checkpointer
:::explain
Otherwise, call it from a function that maps the parent's state to its input and its output back.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did `readings` not appear in the desk's state?
:::
- [ ] It was deleted
- [x] It is not one of the desk's keys, so it stays inside the billing graph
- [ ] Subgraphs cannot return lists
:::explain
That is the module boundary of 1972: an office's details stay inside it.
:::
:::

:::step{type=deep-dive title="Go deeper: subgraphs in practice"}
**Persistence.** Compile only the parent with a checkpointer; subgraphs share it. An interrupt inside a subgraph pauses
the whole run, and resuming continues inside the subgraph.

**Teams.** Different teams can own different subgraphs, test them on their own (chapter 20), and release them
separately, as long as the shared keys or the translating function stay the same.

**Agents as subgraphs.** An agent from `create_agent` is a compiled graph too; chapter 17 uses two of them as
specialists.
:::

:::step{type=recap}
You can now:

- use a compiled graph as a node when it shares keys with the parent;
- call a graph with its own schema from a node that translates in and out;
- stream every inner step with `subgraphs=True`;
- choose between the two by how closely the graphs should be tied.

Next, chapter 17: several agents, and a supervisor that hands work between them.

:::photo{src="/lesson-images/langgraph/lg-16-notes.webp" alt="Handwritten notes about subgraphs: a graph can be a node; shared keys: add it directly; other keys: translate in/out; subgraphs=True shows inside; details stay in the office" ai="true"}
One page of notes for this chapter.
:::
:::
