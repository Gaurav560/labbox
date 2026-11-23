:::step{type=story title="Two nodes, one field"}
Harsh's graph is growing. A new node, `check_location`, raises the severity of complaints near a hospital or a school:
a leak outside a school is more serious than one in an empty lane. And the auditors want a **log**: a line from every
node that touched a complaint, in order.

Both bring a question chapter 1 did not answer. When `classify` sets `severity` to "urgent" and `check_location` later
returns `severity: "high"`, which one wins? And when two nodes each return `log: [...]`, does the second list replace the
first?

By default the last update wins, and here that is wrong both times: an urgent complaint must not become merely high,
and the log must keep every line. A **reducer** says how an update joins the state.

:::mission
Make the log a list that grows with every node, and give severity a reducer of your own that only ever keeps the more
serious value.
:::
:::

:::step{type=concept title="Reducers: how an update joins the state" file="02-state/graph.py" line="19-24"}
Each key of the state can have a reducer, written with `Annotated`:

```python
class Ticket(TypedDict, total=False):
    text: str                                    # no reducer: a new value replaces the old one
    log: Annotated[list[str], operator.add]      # old + new: lists are joined
    severity: Annotated[str, higher]             # your function decides
```

A reducer is a function `(current, update) -> new value`. `operator.add` joins lists; LangChain's `add_messages` (which
`create_agent` uses for its message list) adds messages and replaces one with the same id. You can write your own.

| Key | Update | No reducer | With the reducer |
|---|---|---|---|
| log | `["check_location: ..."]` | only that line | every line so far, plus this one |
| severity | `"high"` after `"urgent"` | high | urgent |

:::diagram{name="lg-reducer"}
The same two updates, joined by two different reducers.
:::
:::

:::step{type=task task=log_reducer title="Your turn: a log that grows" file="02-state/graph.py" line="19-24"}
In `Ticket`, change `log: list[str]` to `log: Annotated[list[str], operator.add]` (and remove the TODO).

Press **Check**.
:::

:::step{type=history title="Reduce, from Lisp to Redux"}
:::before{title="Loops that overwrite"}
Combining many values into one (a total, a list, the latest status) used to be a hand-written loop every time, easy to
get wrong when two parts of a program updated the same value.
:::

"Reduce" (also called fold) comes from functional programming: Lisp and APL had it in the 1960s, and Python has
`functools.reduce`. Google's **MapReduce** paper (**2004**) made "map, then reduce" the way to process the web's data
on thousands of machines. In **2015** Dan Abramov's **Redux** made reducers the way web apps manage state: every change
is an action, and a reducer turns (state, action) into the next state. LangGraph's reducers are the same idea, one per
key of the state.

:::solved
**One rule per field, applied everywhere.** Whichever node updates `severity`, and in whatever order, the result follows
the same rule. That matters most in chapter 5, when nodes run at the same time.
:::

:::timeline
- **1960s** Reduce in Lisp and APL.
- **2004** MapReduce.
- **2015** Redux reducers.
:::
:::

:::step{type=concept title="A reducer of your own" file="02-state/graph.py" line="9-16"}
Severity has an order: normal, high, urgent. The rule the board wants is "never lower it":

```python
ORDER = ["normal", "high", "urgent"]
max("urgent", "high", key=ORDER.index)    # "urgent": index 2 beats index 1
```

The reducer gets `current` (the value already in the state, empty at first) and `new` (the update). If there is no
current value, take the new one; otherwise keep whichever is more serious.
:::

:::step{type=task task=severity_reducer title="Your turn: severity only goes up" file="02-state/graph.py" line="12-16"}
Finish `higher(current, new)`: if `current` is empty, return `new`; otherwise return
`max(current, new, key=ORDER.index)`.

```bash run
cd /workspace/02-state && python main.py
```

Press **Check**.
:::

:::step{type=try title="A log of every step, and an urgent complaint that stays urgent"}
```text
$ python main.py
> Small leak in the lane behind the school.
  severity high, log ['classify: leak', 'check_location: near a hospital or school']
> Brown water near the district hospital.
  severity urgent, log ['classify: dirty_water', 'check_location: near a hospital or school']
> Meter reading looks wrong.
  severity normal, log ['classify: billing', 'check_location: nothing special']
```

Every log has a line from each node, in order: `operator.add` joined them.

The second complaint shows the custom reducer at work. `classify` set it to **urgent** (dirty water); then
`check_location` saw the hospital and returned **high**. Without a reducer the later update wins, and a complaint about
brown water near a hospital would have dropped from urgent to high. With `higher`, it stays urgent. Neither node knows
about the other; the rule lives in the state.
:::

:::step{type=predict title="Guess first"}
:::question
You remove the reducer from `log` again and run the graph. What does the final log hold?
:::
- [ ] Both lines
- [x] Only check_location's line: the last update replaced the list
- [ ] Nothing
:::explain
Without a reducer, an update replaces the value. Every list that should grow needs `operator.add` (or `add_messages`).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does a reducer receive?
:::
- [x] The current value and the update
- [ ] The whole state
- [ ] The node that sent the update
:::explain
`(current, update) -> new value`, once per key, every time a node updates that key.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why put the "never lower the severity" rule in a reducer, not in `check_location`?
:::
- [ ] Reducers are faster
- [x] Then every node that ever sets severity follows the rule, including ones written later
- [ ] Nodes cannot read the state
:::explain
A rule about a field belongs with the field. A new node cannot forget it.
:::
:::

:::step{type=deep-dive title="Go deeper: designing state"}
**Messages.** For chat-like state use `Annotated[list, add_messages]`: it appends messages, and replaces a message that has
the same id, which is how a summary can stand in for old messages (chapter 8).

**Input and output schemas.** A graph can accept a smaller input (only `text`) and return a smaller output than its
internal state, with `StateGraph(State, input_schema=..., output_schema=...)`, so callers never see working fields.

**Keep state small.** The state is saved after every step (Part 2). Store ids and short values, not whole files or
long documents.
:::

:::step{type=recap}
You can now:

- explain how updates join the state, and why the last one wins by default;
- make a list grow with `Annotated[list, operator.add]`;
- write a reducer of your own for a field with a rule;
- put a field's rule in the state, where every node follows it.

Next, chapter 3: branches and loops, so each complaint goes to the right team.

:::photo{src="/lesson-images/langgraph/lg-02-notes.webp" alt="Handwritten notes about reducers: reducer: (current, update) -> new; no reducer: last update wins; lists grow with operator.add; severity only goes up; rule lives with the field" ai="true"}
One page of notes for this chapter.
:::
:::
