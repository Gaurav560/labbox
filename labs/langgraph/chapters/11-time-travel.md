:::step{type=story title="The rust that went to the wrong team"}
"The tap water tastes of rust since the storm." Harsh's keyword rules (chapter 1) look for dirty, smell, brown, muddy,
worms. Rust is not on the list, so the complaint was triaged as **other**, severity **normal**, and sent to the repair
crew with a promise of **72 hours**. Rusty water after a storm can mean a broken main letting dirt in: it is a health
complaint, and the promise should have been 4 hours.

The auditor asks two questions the next day. **What exactly happened**, step by step? And can it be **fixed from the
step that went wrong**, without asking the citizen to complain again?

Both answers are already saved. A checkpointer keeps not only the latest state of a thread, but a checkpoint after
**every** step. You can read them all, go back to any one, change what a node decided, and run the graph on from there.
LangGraph calls this **time travel**.

:::mission
Find the checkpoint between triage and routing in a thread's history, then correct triage's answer there and run the
rest of the graph again.
:::
:::

:::step{type=history title="Recorders and histories"}
:::before{title="Only the wreckage"}
In the early 1950s, when an airliner crashed, investigators had only the wreckage and witnesses. What the crew saw and
did in the last minutes was lost.
:::

After the de Havilland Comet crashes of **1953 and 1954**, the Australian scientist **David Warren** proposed a device that
records the cockpit and the instruments, and built a prototype in **1958**: the **flight recorder**, now required in
every airliner. Software took the same path: **Git** (**2005**) keeps every version of every file, and **event
sourcing** stores every change to an application's data, so its state at any past moment can be rebuilt. A LangGraph
thread's checkpoints are a flight recorder for one run: every step, in order, with the full state at that moment.

:::solved
**Answers instead of guesses.** What did triage decide, and when? Read the checkpoint. Was it wrong? Change it there and
run on.
:::

:::timeline
- **1953 to 1954** The Comet crashes.
- **1958** Warren's flight recorder prototype.
- **2005** Git: every version kept.
- **2024** LangGraph: a checkpoint after every step.
:::

A modern flight data recorder, painted orange so it can be found in wreckage. The French label reads "flight recorder, do not open". Investigators read it back step by step, the way you read a thread's history.

:::photo{src="/lesson-images/langgraph/fdr.webp" alt="A bright orange box with a cylinder on its side labelled in French: flight recorder, do not open" credit="NTSB" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Fdr_sidefront.jpg"}
A flight data recorder, photographed by the US National Transportation Safety Board.
:::
:::

:::step{type=concept title="A thread's history" file="11-time-travel/ticket.py" line="44-48"}
`app.get_state_history(config)` yields the thread's checkpoints, **newest first**. Each one is a `StateSnapshot`:

| Field | Here | Meaning |
|---|---|---|
| `values` | `{"text": ..., "kind": "other", ...}` | the state at that moment |
| `next` | `("route",)` | the nodes about to run (empty at the end) |
| `config` | `{"configurable": {"thread_id": ..., "checkpoint_id": ...}}` | the address of this exact checkpoint |
| `metadata` | `{"step": 1, "source": "loop"}` | the step number, and what made it: `input`, `loop` (a node ran) or `update` |

The checkpoint "just before route" is the one whose `next` is `("route",)`. Its `values` show what triage decided.
:::

:::step{type=task task=find_checkpoint title="Your turn: find the moment" file="11-time-travel/ticket.py" line="44-48"}
Finish `snapshot_before(app, thread, node)`:

1. loop over `app.get_state_history({"configurable": {"thread_id": thread}})` (newest first);
2. return the first snapshot whose `.next == (node,)`, a **tuple** with one name;
3. after the loop, return `None`.

The usual slip: `snapshot.next == node`, comparing the tuple `('route',)` with the string `"route"`. They are never
equal. We tried it: no snapshot was found, and the function returned `None`.

Press **Check**.
:::

:::step{type=concept title="Change the past, run on" file="11-time-travel/ticket.py" line="51-56"}
Two calls fix the complaint:

```python
config = app.update_state(snapshot.config, {"kind": "dirty_water", "severity": "urgent"}, as_node="triage")
app.invoke(None, config)
```

`update_state` writes the values into the state **at that checkpoint**, through the reducers, as if the node named by
`as_node` had returned them, and saves the result as a **new** checkpoint. Because it acts as `triage`, the graph's edges
say what comes next: `route`. (Here `as_node` could even be left out: we tried, and LangGraph took the update as
triage's, the last node that wrote at that checkpoint. Writing it says what you mean.) It returns the new checkpoint's config, and `invoke(None, config)` runs on from it.

Nothing is overwritten. The old run stays in the history, and the corrected run becomes a new branch from the same point,
like a branch in Git. The thread's current state is the newest checkpoint: the corrected one.

:::diagram{name="lg-fork"}
The real history of thread C-311 (26 November): the first run, and the branch the correction made.
:::
:::

:::step{type=task task=correct_and_rerun title="Your turn: correct a step and run on" file="11-time-travel/ticket.py" line="51-56"}
Finish `correct(app, thread, fields)`:

1. `config = app.update_state(snapshot.config, fields, as_node="triage")`;
2. `return app.invoke(None, config)`.

The usual slip: skipping `update_state` and calling `app.invoke(fields, snapshot.config)`. That is a new input, so the
run starts from START, triage runs again, and puts "other" back. We tried it: "repair crew ... 72 hours" again.

```bash run
cd /workspace/11-time-travel && python main.py
```

Press **Check**.
:::

:::step{type=try title="A wrong answer, its history, and a branch"}
```text
$ python main.py
first run: other, normal -> Your complaint is with the repair crew. We will respond within 72 hours.

history (newest first):
  step  3  loop   next=()             kind=other
  step  2  loop   next=('reply',)     kind=other
  step  1  loop   next=('route',)     kind=other
  step  0  loop   next=('triage',)    kind=-
  step -1  input  next=('__start__',) kind=-

corrected: dirty_water, urgent -> Your complaint is with the health team. We will respond within 4 hours.

history after the correction (newest first):
  step  4  loop   next=()             kind=dirty_water
  step  3  loop   next=('reply',)     kind=dirty_water
  step  2  update next=('route',)     kind=dirty_water
  step  3  loop   next=()             kind=other
  step  2  loop   next=('reply',)     kind=other
  step  1  loop   next=('route',)     kind=other
  step  0  loop   next=('triage',)    kind=-
  step -1  input  next=('__start__',) kind=-
```

(We ran it again on 26 November: the same output, line for line.)

Read the first history from the bottom up: the input arrived (step -1), triage was about to run (0), triage had
decided "other" and route was next (1), then reply (2), then the end (3). The auditor's first question is answered by
the step 1 line: the mistake was triage's, not route's.

After the correction there are eight checkpoints. The `update` at step 2 is your correction, made from the step 1
checkpoint; route and reply then ran again on it (steps 3 and 4). The old steps 2 and 3, with "other", are still there:
nothing was deleted, and the audit trail shows both what happened and how it was fixed. The citizen gets the health team
and 4 hours.

The real fix is upstream: add "rust" (and "taste") to the dirty-water words, or use the model triage of chapter 4. Time
travel repairs one thread; only a change to the graph repairs the next thousand.
:::

:::step{type=predict title="Guess first"}
:::question
You call `update_state(snapshot.config, {...}, as_node="route")` instead of `as_node="triage"`. What runs next?
:::
- [ ] route
- [x] reply: the update counts as route's output, so the graph continues after route
- [ ] Nothing
:::explain
`as_node` says which node the update pretends to come from; the edges from that node decide what runs next. Tried
for real, reply runs and stops with `KeyError: 'team'`: route never ran on this branch, so no team was ever set.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What happens to the old checkpoints when you correct a step?
:::
- [ ] They are replaced
- [x] They stay; the correction starts a new branch from that point
- [ ] They are deleted after the rerun
:::explain
Checkpoints are append-only, which is what makes them an audit trail.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `invoke(None, config)` do with a config that names a past checkpoint?
:::
- [x] Runs the graph on from that checkpoint
- [ ] Runs from START
- [ ] Shows the checkpoint
:::explain
Input `None` means "continue"; the config says from where. Called on an untouched past checkpoint, it replays from there.
:::
:::

:::step{type=deep-dive title="Go deeper: time travel in practice"}
**Debugging agents.** When an agent run goes wrong, find the checkpoint just before the bad model call, change the
messages (or the prompt in the state), and run on from there, instead of reproducing the whole conversation.

**Replays cost money.** Running on from a checkpoint calls the later model nodes again; their answers may differ from
the first time.

**Cleaning up.** History grows with every step of every thread. Production checkpointers are cleaned by age; keep what
your audits need (`saver.delete_thread(thread_id)` removes one thread).
:::

:::step{type=recap}
You can now:

- read a thread's history, step by step, with `get_state_history`;
- find the checkpoint just before a node;
- correct a node's answer with `update_state(..., as_node=...)` and run on from there;
- explain why the old branch stays, and why the graph itself still needs fixing.

Next, chapter 12: stores, for facts that outlive one thread.

:::photo{src="/lesson-images/langgraph/lg-11-notes.webp" alt="Handwritten notes titled Time travel, read the history, fix a step, run on: a checkpointer keeps a checkpoint after every step, get_state_history lists them newest first, and update_state changes one and starts a new branch from it; find the checkpoint before route, update_state as triage, a new branch with dirty_water, invoke None with the config, health team and 4 hours; rust was not a dirty-water word so the promise was 72 hours; next equal to the string route never matches, use the tuple; invoke with fields and a config starts over and gives other again; 8 checkpoints after the fix, nothing lost" ai="true"}
One page of notes for this chapter.
:::
:::
