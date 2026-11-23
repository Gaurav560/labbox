:::step{type=story title="A storm night"}
After a monsoon storm, complaints arrive in a burst: a pipe burst outside the bakery, no water in Tilak Nagar, brown
water in Old Market, a leak at the Gandhi Chowk tank, a broken meter cover. Each needs the same triage, and the number of
complaints is not known until the night is over. A graph with a fixed number of nodes cannot have "one triage node per
complaint" drawn in advance.

`Send` solves that: a function looks at the state and returns **one task per item**, each running the same node with
its own small input, all at once. Their results flow back into the shared state through a reducer.

The repairs then split: anything over Rs 50,000 needs the executive engineer's approval; smaller ones go straight to
tomorrow's schedule. A node that decides **where to go next** and **what to write** at the same moment can return a
`Command`, which does both.

:::mission
Fan out one triage per complaint with `Send` and collect the results, then write a planning node that routes each repair
with a `Command`.
:::
:::

:::step{type=history title="Fork, join, and commands"}
:::before{title="One thing at a time"}
Early programs did one thing at a time, even when the work split naturally into independent pieces.
:::

In **1963** Melvin Conway described **fork and join**: split a computation into parts that run at the same time, then
wait for them all. Google's **MapReduce** (**2004**) made the same shape (map each item, then reduce the results) the way
to process the web's data. In LangGraph, `Send` is the fork, and a reducer on the results is the join. Separately, the
**Command** pattern (described in the "Design Patterns" book of **1994**) wraps an instruction and its data in one object;
LangGraph's `Command` carries "go here" and "change this" together.

:::solved
**As many parallel tasks as the data needs**, decided at run time, and nodes that can steer the graph themselves.
:::

:::timeline
- **1963** Fork and join (Conway).
- **1994** The Command pattern.
- **2004** MapReduce.
:::
:::

:::step{type=concept title="Send: one task per item" file="06-send-command/graph.py" line="14-37"}
```python
def fan_out(state: Night) -> list[Send]:
    return [Send("triage_one", {"text": text}) for text in state["complaints"]]

graph.add_conditional_edges(START, fan_out, ["triage_one"])
```

A function used as a conditional edge may return `Send` objects instead of node names. Each `Send(node, input)` starts
that node with **its own input**, here a small `OneComplaint` state with just the text, not the whole night. All the
`triage_one` runs happen in the same step.

Each run returns `{"tickets": [ticket]}`, and `tickets` has the `operator.add` reducer, so the results are collected into
one list, whatever the order they finish in. Then `summarise` runs once, with all of them.

:::diagram{name="lg-send"}
One Send per complaint out, one list of tickets back in, then a Command per repair.
:::
:::

:::step{type=task task=fan_out title="Your turn: one triage per complaint" file="06-send-command/graph.py" line="24-27"}
Finish `fan_out(state)`: return one `Send("triage_one", {"text": text})` for every text in `state["complaints"]`.

Press **Check**.
:::

:::step{type=concept title="Command: go there, and write this" file="06-send-command/graph.py" line="56-60"}
So far nodes returned updates, and edges decided where to go. A node can do both by returning a `Command`:

```python
def plan(state: Repair) -> Command[Literal["engineer_approval", "schedule"]]:
    if state["estimate"] > APPROVAL_OVER:
        return Command(goto="engineer_approval", update={"status": "waiting for the engineer"})
    ...
```

The return type lists where it may go, so the graph's diagram and `compile()` know the possible paths, and the graph
needs no edge out of `plan`. Use `Command` when the decision and the update come from the same work (here, reading the
estimate); use a conditional edge when the decision is a separate question.
:::

:::step{type=task task=command_goto title="Your turn: route the repair" file="06-send-command/graph.py" line="56-60"}
Finish `plan(state)`: over `APPROVAL_OVER`, return `Command(goto="engineer_approval", update={"status": "waiting for the
engineer"})`; otherwise `Command(goto="schedule", update={"status": "scheduled"})`.

```bash run
cd /workspace/06-send-command && python main.py
```

Press **Check**.
:::

:::step{type=try title="Five complaints at once, and a rule that forgot something"}
```text
$ python main.py
  high    leak         Rs 18,000  Pipe burst outside the bakery on Station Road
  high    no_water     Rs 65,000  No water in Tilak Nagar since the storm
  urgent  dirty_water  Rs 40,000  Brown water in Old Market
  high    leak         Rs 18,000  Leak at the Gandhi Chowk tank
  normal  billing      Rs      0  Meter cover broken, bill looks wrong
5 complaints, 1 urgent

leak, Rs 18,000: scheduled for tomorrow

no_water, Rs 65,000: waiting for the engineer (sent to the executive engineer)

dirty_water, Rs 40,000: scheduled for tomorrow

leak, Rs 18,000: scheduled for tomorrow
```

Five `Send`s, five triages in one step, one list of tickets, one summary. The `Command` sent the Rs 65,000 repair to the
engineer and scheduled the others.

Now read the third repair. The brown water in Old Market is **urgent**: chapter 1 promised a response within four
hours, because people may drink it. `plan` scheduled it "for tomorrow", because `plan` only looks at the cost. Every line
of code did what it was told; the rule was incomplete. A real plan node checks severity first (urgent goes to an
emergency crew today, whatever it costs) and cost second. Graphs make such gaps easy to fix, because the decision lives
in one small function, but only if someone reads the results.
:::

:::step{type=predict title="Guess first"}
:::question
`tickets` loses its `operator.add` reducer. What happens when five `triage_one` runs return in the same step?
:::
- [ ] Only the last ticket is kept
- [x] LangGraph refuses: five updates to one key in one step need a reducer
- [ ] They are joined anyway
:::explain
Parallel updates to the same key always need a reducer (chapter 5).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does each `Send` carry?
:::
- [x] The node to run and that run's own input
- [ ] The whole state
- [ ] A message to the user
:::explain
That is what makes it map-reduce: small inputs out, results reduced back in.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
When is `Command` a better choice than a conditional edge?
:::
- [ ] Always
- [x] When the same work produces both the decision and the update
- [ ] When there are more than two paths
:::explain
If deciding is a separate question, keep it a routing function; if it falls out of the node's work, a Command is simpler.
:::
:::

:::step{type=deep-dive title="Go deeper: Send and Command in practice"}
**Orchestrator and workers.** Replace `fan_out`'s list with a model that splits a task into parts ("plan the storm
response by area"), and you have the orchestrator-workers pattern.

**Limits.** A thousand complaints means a thousand parallel node runs, and with model nodes, a thousand calls at once.
Batch them, or cap concurrency (`max_concurrency` in the config).

**Command across graphs.** In multi-agent systems (Part 3), a `Command` can send control to a node in the parent graph:
that is how one agent hands over to another.
:::

:::step{type=recap}
You can now:

- fan out one task per item with `Send`, each with its own input;
- collect parallel results with a reducer;
- route and update in one return value with `Command`;
- read results critically, after an urgent complaint was scheduled for tomorrow.

That ends Part 1. Next, chapter 7: checkpointers and threads, so a graph remembers and can pause.

:::photo{src="/lesson-images/langgraph/lg-06-notes.webp" alt="Handwritten notes about Send and Command: Send = one task per item; results joined by a reducer; Command = goto + update; urgent before cost!; read the results" ai="true"}
One page of notes for this chapter.
:::
:::
