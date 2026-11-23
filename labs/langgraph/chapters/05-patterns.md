:::step{type=story title="Two jobs that should not wait for each other"}
Before a crew is sent, Harsh needs two facts about the street: its **zone** (which crew) and its **history** (how many
complaints this year: six on Station Road means the old main may be failing). The two lookups do not depend on each
other, so waiting for one before starting the other wastes time. They should run **in parallel**, and the assignment
should wait for both.

The board also writes public notices for planned shutdowns, and they must be complete: which area, the date, the hours,
why, and "store water the day before". A model writes a draft; a second model checks it against that list; if
something is missing, the writer tries again with the feedback.

Both are standard **workflow patterns**, and naming them makes graphs easier to design and to talk about.

:::mission
Run two lookups in parallel and join them, then build a writer and a grader in a loop that ends when the notice is good,
or after three drafts.
:::
:::

:::step{type=history title="Five patterns, named in 2024"}
:::before{title="Everything called an agent"}
In 2023 almost any program that called a model more than once was called an "agent", whatever its shape, which made
designs hard to compare.
:::

In **December 2024** Anthropic's essay **"Building effective agents"** separated **workflows** (code decides the path)
from **agents** (a model decides), and named five workflow patterns that kept appearing in real systems. LangGraph's
documentation teaches the same five, each a small graph:

| Pattern | Shape | In Harsh |
|---|---|---|
| Prompt chaining | step after step | triage, then reply (chapter 4) |
| Routing | a branch picks one path | dirty water to the health team (chapter 3) |
| Parallelization | several nodes at once, then a join | zone and history lookups (this chapter) |
| Orchestrator-workers | one node splits work, workers do the parts | one triage per complaint (chapter 6) |
| Evaluator-optimizer | write, grade, rewrite | public notices (this chapter) |

:::solved
**Shapes with names.** "This is an evaluator loop with three rounds" says more than a page of description, and each
shape has known costs and limits.
:::

:::timeline
- **2023** Many "agents" of many shapes.
- **2024** Workflows and agents separated; five patterns named.
:::
:::

:::step{type=concept title="Fan out, then join" file="05-patterns/graph.py" line="37-47"}
Two edges from START mean both nodes run in the **same step**:

```python
graph.add_edge(START, "zone_lookup")
graph.add_edge(START, "history_lookup")
graph.add_edge(["zone_lookup", "history_lookup"], "assign")   # a list: assign waits for all of them
```

The list in the last edge is a **join**: `assign` runs once, after both have finished. Here both branches are one node
long, so two separate edges would happen to work too. When one branch has more steps than the other, separate edges run
`assign` as soon as the shorter branch is done (and again later); the list always waits for every node in it.

The two branches write different keys (`zone`, `past`), so there is no conflict. If parallel nodes update the **same**
key, that key needs a reducer (chapter 2), or LangGraph refuses the update.

:::diagram{name="lg-join"}
Both lookups share step 1; assign waits for both and runs once in step 2.
:::
:::

:::step{type=task task=parallel_branches title="Your turn: two lookups at once" file="05-patterns/graph.py" line="37-47"}
In `build_parallel()`, add the edges START -> zone_lookup, START -> history_lookup, and the join
`graph.add_edge(["zone_lookup", "history_lookup"], "assign")`.

Press **Check**.
:::

:::step{type=concept title="Write, grade, write again" file="05-patterns/graph.py" line="74-91"}
The notice loop has two model nodes and one decision:

1. `write_notice` drafts the notice (with the grader's feedback, from the second draft on) and counts the drafts.
2. `grade_notice` asks a model for a `Grade`: is every required item there, and if not, what is missing.
3. `next_step` decides: done if the notice is good **or** three drafts have been written; otherwise write again.

The ceiling matters as much as the grade: a grader that is never satisfied would otherwise loop until the budget runs
out.
:::

:::step{type=task task=evaluator_loop title="Your turn: when to stop" file="05-patterns/graph.py" line="86-90"}
Finish `next_step(state)`: return `END` when `state["good"]` is true or `state["drafts"]` has reached `MAX_DRAFTS`;
otherwise return `"write_notice"`.

```bash run
cd /workspace/05-patterns && python main.py
```

Press **Check**.
:::

:::step{type=try title="A join, a rewrite, and a grader that missed something"}
```text
$ python main.py
Station Road: {'street': 'Station Road', 'zone': 'South', 'past': 6, 'plan': 'South zone crew and a survey of the old main (repeated complaints)'}
  steps: [['history_lookup'], ['zone_lookup'], ['assign']]
Tilak Nagar: {'street': 'Tilak Nagar', 'zone': 'East', 'past': 1, 'plan': 'East zone crew'}
  steps: [['history_lookup'], ['zone_lookup'], ['assign']]

--- draft 1:
**Public Notice**  
Residents of Ujjwal Nagar are informed of a planned water shutdown on Thursday, 28 November, from 10:00 to 16:00. This is due to valve replacement at the Tilak Nagar tank. We apologize for any inconvenience and appreciate your understanding. Thank you for your cooperation.
--- grade: good=False The notice does not specify that residents should store water the day before.
--- draft 2:
**Public Notice**  
Residents of Ujjwal Nagar are informed of a planned water shutdown on Thursday, 28 November, from 10:00 to 16:00, due to valve replacement at the Tilak Nagar tank. Please store sufficient water the day before to avoid inconvenience. Thank you for your understanding.
--- grade: good=True 
```

The parallel graph: both lookups ran in the first step (the stream reports them one by one, but neither waited for the
other), and `assign` ran once, with both facts. Station Road's six past complaints added a survey of the old main.

The notice loop: the grader rejected draft 1 for exactly the right reason, the writer added "store sufficient water the
day before", and draft 2 passed. The pattern works.

But read draft 2 against the facts: the shutdown is for **Old Market and Tilak Nagar**, and both drafts say only
"residents of Ujjwal Nagar". The first item on the grader's own list, which area, is missing, and the grader passed it.
A model grader is a second model with the same kind of blind spots, and it is lenient with fluent text. Two fixes are
worth knowing: check what can be checked in Python (does the notice contain each area's name?), and give the grader one
question per item instead of one question for all five.
:::

:::step{type=predict title="Guess first"}
:::question
Both parallel lookups return `{"note": ...}` for the same key, which has no reducer. What happens?
:::
- [ ] The last one wins
- [x] LangGraph raises an error: two updates to one key in the same step need a reducer to combine them
- [ ] Both are kept in a list
:::explain
In a sequence the last update wins; in the same step there is no "last". A reducer says how to combine them.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `add_edge(["a", "b"], "c")` mean?
:::
- [x] c runs once, after both a and b have finished
- [ ] c runs twice
- [ ] c runs after either a or b
:::explain
A list of start nodes is a join.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What did the missed area name teach about model graders?
:::
- [ ] Graders are useless
- [x] A grader can miss things; check what you can in Python, and ask it narrow questions
- [ ] Use a bigger notice
:::explain
Graders help, as draft 1 showed. They are evidence, not proof.
:::
:::

:::step{type=deep-dive title="Go deeper: patterns in practice"}
**Parallel model calls.** Two model nodes in the same step run at the same time: the step takes as long as the slower one,
not the sum.

**Python checks first.** In an evaluator loop, put cheap exact checks (required words, length, dates) before the model
grader; only text that passes them costs a grading call.

**Patterns combine.** Harsh in Part 4 is a chain whose steps include a router, a parallel join and an approval loop.
:::

:::step{type=recap}
You can now:

- name the five workflow patterns and recognise them in a graph;
- run nodes in parallel and join them with a list edge;
- build an evaluator-optimizer loop with a ceiling;
- treat a model grader's verdict as evidence, after watching one miss the area.

Next, chapter 6: `Send` for one task per item, and `Command` for nodes that choose where to go.

:::photo{src="/lesson-images/langgraph/lg-05-notes.webp" alt="Handwritten notes about workflow patterns: five workflow patterns; parallel: same step, then join; add_edge([a, b], c) waits for both; write, grade, write again; max 3 drafts. Graders can miss" ai="true"}
One page of notes for this chapter.
:::
:::
