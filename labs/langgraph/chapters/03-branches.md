:::step{type=story title="The right team, and a street spelt three ways"}
Not every complaint goes to a repair crew. Brown or smelly water goes to the **health team**, who take a water sample
within four hours. A wrong bill goes to the **billing office**. Everything else goes to the **repair crew** of the
street's zone.

And the street is often spelt in a way the board's map does not know: "Gandi Chowk", "stn road", "tilaknagar". Harsh
should try the street as written, then try a corrected spelling, and only then ask the citizen to confirm it. That is a
**loop**, and it needs a limit, or a street nobody can find would be looked up forever.

In a graph, both are **conditional edges**: after a node, a function reads the state and returns the name of the next
node.

:::mission
Route each complaint to its team with a conditional edge, then loop back to try a corrected street spelling, at most
twice, before asking the citizen.
:::
:::

:::step{type=history title="Branches, loops and a famous letter"}
:::before{title="Processes in people's heads"}
Factories and offices once ran on habit: who did what next, and what happened when something went wrong, was known only
to the people doing it.
:::

In **1921** Frank and Lillian Gilbreth presented **process charts** to the American Society of Mechanical Engineers:
steps drawn as symbols joined by arrows, with decisions where the path splits. Flowcharts became how programmers
planned programs too, until code with jumps everywhere became unreadable. In **1968** Edsger Dijkstra's letter **"Go To
Statement Considered Harmful"** argued that programs should use only clear structures: sequence, choice and loop. A
LangGraph graph is a flowchart again, but with the same discipline: each branch is a named function, and each loop has a
condition you can read.

:::solved
**Paths you can see.** Every possible route through Harsh is in the graph's diagram, and each decision is one small
function you can test.
:::

:::timeline
- **1921** The Gilbreths' process charts.
- **1968** "Go To Statement Considered Harmful".
- **2024** Conditional edges in LangGraph.
:::

Lillian Gilbreth, an engineer and psychologist, worked with her husband Frank on the process charts of 1921, and went on to study how people work for decades after his death in 1924.

:::photo{src="/lesson-images/langgraph/lillian-gilbreth.webp" alt="A black and white portrait of Lillian Gilbreth, a woman with short wavy hair, looking to one side" credit="Unknown photographer (uploaded by Richard Arthur Norton)" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Lillian_Moller_Gilbreth,_1921.jpg"}
Lillian Moller Gilbreth, 1921.
:::
:::

:::step{type=concept title="Conditional edges" file="03-branches/graph.py" line="49-53"}
```python
def choose_team(state: Ticket) -> str:
    ...                                         # returns "health_team", "billing_office" or "repair_crew"

graph.add_conditional_edges("route", choose_team, ["health_team", "billing_office", "repair_crew"])
```

After `route` runs, LangGraph calls `choose_team(state)` and goes to the node it names. The list of possible targets is
optional but worth giving: it puts every branch in the graph's diagram, and `compile()` checks that each target exists.
We tried both on 26 November. A misspelled target stopped the build: `ValueError: At 'route' node, 'choose_team'
branch found unknown target 'health_teem'`. And with no list at all, the diagram could not know the branches and
drew a wrong picture: `route --> __end__`, as if `route` were the last step.

A routing function only **decides**: it returns a name and changes nothing. Updates belong in nodes.

Edsger Dijkstra, whose 1968 letter asked for programs built only from sequence, choice and loop. A routing function is a choice you can name, read and test on its own.

:::photo{src="/lesson-images/langgraph/dijkstra.webp" alt="Edsger Dijkstra, an older man with grey hair, a beard and glasses, in a checked shirt and an orange sweater vest" credit="Hamilton Richards" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Edsger_Wybe_Dijkstra.jpg"}
Edsger W. Dijkstra in 2002.
:::
:::

:::step{type=task task=route_by_kind title="Your turn: route by kind" file="03-branches/graph.py" line="49-53"}
Finish `choose_team(state)`:

1. read `state["kind"]`;
2. return `"health_team"` for `dirty_water` and `"billing_office"` for `billing`;
3. return `"repair_crew"` for everything else (a dictionary with `.get(kind, "repair_crew")` does all three).

The usual slip: a name that is almost right, such as `"health team"` with a space. We tried it: the run stopped with
`KeyError: 'health team'`. The router must return a node's name exactly.

Press **Check**.
:::

:::step{type=concept title="A loop is an edge back, with a limit" file="03-branches/graph.py" line="27-39"}
`find_zone` makes one attempt and counts it in `tries`: the first try uses the street as written, later tries use the
corrected spelling from `SPELLINGS`. After it, a routing function decides:

:::trace{title="The street 'Gandi Chowk'"}
| Step | tries | zone | after_find_zone says |
|---|---|---|---|
| find_zone (as written) | 1 | not found | tries < 2: back to find_zone |
| find_zone (corrected: gandhi chowk) | 2 | North | found: go to route |
:::

The limit, `MAX_TRIES`, is what makes this a loop and not a trap. A street that is not on the map at all ("Shivaji
Path") stops after two tries and goes to `ask_citizen`, where a person takes over.

:::diagram{name="lg-route"}
The four complaints of this chapter's run (26 November): how many tries each took, and where each ended.
:::
:::

:::step{type=task task=retry_loop title="Your turn: try again, then ask" file="03-branches/graph.py" line="35-39"}
Finish `after_find_zone(state)`:

1. if `state["zone"]` is not empty, return `"route"`;
2. else, if `state["tries"] < MAX_TRIES`, return `"find_zone"` (try again);
3. otherwise return `"ask_citizen"`.

The usual slip: `<=` instead of `<`. We tried it: "Shivaji Path" took 3 tries instead of 2. With a model call inside
the loop, that is one paid call more than you planned, on every lost street.

```bash run
cd /workspace/03-branches && python main.py
```

Press **Check**.
:::

:::step{type=try title="Four complaints, four paths"}
```text
$ python main.py
> Brown water from the tap (Gandi Chowk): dirty_water, tries 2 -> health team, North zone: water sample within 4 hours
> No water since morning (Station Road): no_water, tries 1 -> repair crew, South zone
> Bill is double this month (tilaknagar): billing, tries 2 -> billing office
> Pipe leaking (Shivaji Path): leak, tries 2 -> front desk: please confirm the street name
...
	find_zone -.-> ask_citizen;
	find_zone -.-> route;
	route -.-> billing_office;
	route -.-> health_team;
	route -.-> repair_crew;
	ask_citizen --> __end__;
	billing_office --> __end__;
	health_team --> __end__;
	repair_crew --> __end__;
	find_zone -.-> find_zone;
...
```

(The diagram is shortened at both ends with "...". We ran it again on 26 November: the same four lines.) Every path
ran once:

- "Gandi Chowk" was not found as written, the loop tried "gandhi chowk", and the dirty water went to the health team in
  the North zone.
- "Station Road" was found on the first try: one attempt, no loop.
- "tilaknagar" needed the correction, then went to billing.
- "Shivaji Path" is not on the map: two tries, then the front desk asks the citizen.

In the diagram, dotted arrows (`-.->`) are conditional edges and solid ones (`-->`) always run. The last dotted arrow,
`find_zone -.-> find_zone`, is the loop.
:::

:::step{type=predict title="Guess first"}
:::question
You forget the `tries < MAX_TRIES` test and always return "find_zone" when no zone is found. What happens with
"Shivaji Path"?
:::
- [ ] It goes to ask_citizen
- [x] The loop never ends until LangGraph's recursion limit stops it with an error
- [ ] It picks the nearest street
:::explain
We tried it on 26 November. LangGraph 1.2.24 stopped the run with `GraphRecursionError: Recursion limit of 10007
reached`, after 1.5 seconds of plain Python. (The default is 10,007 steps in this version; you can set your own per
run with `invoke(..., {"recursion_limit": 25})`, which stopped the same loop in 0.01 seconds.) With a model call in
the loop, 10,007 steps would be 10,007 paid calls. A loop needs a way out. The recursion limit is a last-resort safety
net; your condition is the real one.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What should a routing function do?
:::
- [x] Read the state and return the name of the next node
- [ ] Update the state
- [ ] Call the next node itself
:::explain
Deciding and changing are kept apart: routers decide, nodes change the state.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why list the possible targets in `add_conditional_edges`?
:::
- [ ] It is required
- [x] So the diagram shows every branch and compile() can check that each target exists
- [ ] It makes routing faster
:::explain
Without the list, LangGraph cannot know where the function might send a run until it runs.
:::
:::

:::step{type=deep-dive title="Go deeper: branching in practice"}
**Routing by a model.** A router can ask a model ("which team?") instead of using rules, as chapter 4 does for
classification. Keep a rule-based fallback for when the model's answer is not one of the targets.

**Many branches at once.** A routing function can return a list of node names; they then all run, in the same step
(chapter 5's parallel pattern). Their updates must not clash: when we returned `["health_team", "repair_crew"]`,
both wrote `team` in the same step and the run stopped with `InvalidUpdateError: At key 'team': Can receive only one
value per step`. A key that several branches write needs a reducer (chapter 2).

**Testing routers.** A router is a plain function of the state: test it with small dictionaries, without running the
graph, as the hidden checks do.
:::

:::step{type=recap}
You can now:

- branch with `add_conditional_edges` and a routing function;
- build a loop as an edge back to a node, with a limit in the state;
- read conditional and normal edges in a graph's diagram;
- keep routers deciding and nodes updating.

Next, chapter 4: nodes that call a model.

:::photo{src="/lesson-images/langgraph/lg-03-notes.webp" alt="Handwritten notes titled Branches and loops, a router decides and nodes change the state: a conditional edge calls a routing function after a node, which reads the state and returns the name of the next node, and a loop is an edge back with a limit; find_zone tries the street, the router reads zone and tries, found goes to route, the router picks the team, the team node replies; with no limit the run stopped at step 10,007; a wrong name gives KeyError; no target list gives a wrong diagram; two branches writing one key give InvalidUpdateError" ai="true"}
One page of notes for this chapter.
:::
:::
