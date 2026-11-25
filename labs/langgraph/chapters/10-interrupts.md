:::step{type=story title="Rs 65,000 needs a signature"}
Chapter 6 sent big repairs to a node called `engineer_approval`, which only wrote "waiting for the engineer". Nobody
actually waited. At the water board, any repair over **Rs 50,000** needs the executive engineer's approval, and she
answers when she can: in ten minutes, or tomorrow morning after a site visit.

So the graph must **stop** at the approval step, show her what she needs to decide (the work, the street, the estimate,
a short brief), save itself, and end the process. When she answers, hours later and maybe on another server, the same
run must **continue** from that step with her decision, and go to the schedule or to a refusal.

LangGraph calls this an **interrupt**: a node pauses the run and hands a question to the outside world, and the answer
comes back as the value the node was waiting for.

:::mission
Pause big repairs at the approval node with `interrupt`, then resume each paused job with the engineer's decision,
in separate runs, the way it happens at the board.
:::
:::

:::step{type=history title="Machines that stop and call a person"}
:::before{title="Machines that carried on regardless"}
Early factory machines kept running when something went wrong. A broken thread on a loom produced metres of faulty
cloth before anyone noticed.
:::

In **1924** Sakichi Toyoda built the **Type G automatic loom**, which **stopped itself** when a thread broke, so that a
person could fix the cause before it went on. Toyota made the idea a rule of its factories: any worker could pull the
**andon** cord and stop the line until someone came. Banks built the same thing into their software as **maker-checker**:
one clerk enters a big payment, and it waits until a second person approves it. LangGraph's `interrupt` is that stop:
the graph does the routine work and waits for a person exactly where judgement is needed.

:::solved
**Automation with a person in charge.** The graph prepares everything, a person decides, and the work continues on
their answer, however long they take.
:::

:::timeline
- **1924** The Type G loom stops itself when a thread breaks.
- **1950s** Toyota's production line: stop and call a person.
- **2024** LangGraph: `interrupt` and `Command(resume=...)`.
:::

The first Type G loom ever built, now in a museum. When a thread broke, it stopped and waited for a person, instead of weaving on.

:::photo{src="/lesson-images/langgraph/loom.webp" alt="A black cast-iron weaving loom with orange parts, gear wheels at the side and a roll of white cloth at the front, on a red museum stand" credit="Morio" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:1924_Non-Stop_Shuttle_Change_Toyoda_Automatic_Loom,_Type_G_1.jpg"}
The first Toyoda automatic loom, Type G, 1924.
:::
:::

:::step{type=concept title="interrupt: pause here, with a question" file="10-interrupts/repair.py" line="41-46"}
Inside a node, `interrupt(value)` stops the run:

```python
def approval(state: Repair) -> dict:
    decision = interrupt({"job": state["job"], "estimate": state["estimate"], "brief": state["brief"],
                          "question": "Approve this repair?"})
    return {"approved": decision["approve"], "note": decision.get("note", "")}
```

1. The run stops at `interrupt`. The checkpointer saves the thread, with `approval` as the next step. (Without a
   checkpointer the run still stops, we found, but nothing is saved, and the later resume fails with `RuntimeError:
   Cannot use Command(resume=...) without checkpointer`.)
2. `invoke` returns the state so far, plus `"__interrupt__"`: a list holding your value, for the program to show the
   engineer.
3. Later, the run is resumed with her answer, and `interrupt(...)` **returns that answer** inside the node, which goes on
   from there.

The value can be anything JSON can hold. Give the person everything they need to decide, so they never have to look it
up.
:::

:::step{type=task task=pause_for_engineer title="Your turn: wait for the engineer" file="10-interrupts/repair.py" line="41-46"}
In `approval`:

1. `decision = interrupt({"job": state["job"], "estimate": state["estimate"], "brief": state["brief"], "question":
   "Approve this repair?"})`;
2. `return {"approved": decision["approve"], "note": decision.get("note", "")}`.

The usual slip: leaving out the brief or the estimate. The engineer then sees a question with nothing to decide on,
and must look the job up elsewhere, which is the work the graph was meant to save her.

Press **Check**.
:::

:::step{type=concept title="Command(resume=...): the answer comes back" file="10-interrupts/repair.py" line="73-77"}
A paused thread continues when you invoke it with a `Command` carrying the answer, and the same thread id:

```python
app.invoke(Command(resume={"approve": True, "note": "Before the festival"}), {"configurable": {"thread_id": "J-201"}})
```

LangGraph loads the thread, **runs the paused node again from its first line**, and this time `interrupt(...)` returns
the resume value instead of stopping. Then the graph goes on: `after_approval` reads `approved` and picks `schedule` or
`refuse`.

"From its first line" matters: everything in the node before `interrupt` runs twice, once before the pause and once on
resume. Keep that part free of side effects (no SMS, no order), or move side effects into a node after the approval.

:::diagram{name="lg-interrupt"}
The real job J-201 (26 November): two processes, and the approval node starting twice.
:::
:::

:::step{type=task task=resume_with_decision title="Your turn: resume with her decision" file="10-interrupts/repair.py" line="73-77"}
Finish `decide(app, job, approve, note)`: return `app.invoke(Command(resume={"approve": approve, "note": note}),
{"configurable": {"thread_id": job}})`.

The usual slip: invoking with a plain dictionary, `app.invoke({"approve": approve, "note": note}, config)`. A plain
dictionary is a **new input**, not an answer. We tried it: the job ran again from START (a second brief, a second
model call) and stopped at the same approval, still waiting. And a resume sent to a thread id that never paused runs
from START with an empty state: `KeyError: 'work'`.

```bash run
cd /workspace/10-interrupts && python main.py start J-201 "Replace 40 m of the cast-iron main" "Station Road" 65000
```

```bash run
cd /workspace/10-interrupts && python main.py decide J-201 yes "Before the festival, please"
```

Press **Check**.
:::

:::step{type=try title="Three repairs, two decisions, and a brief that invented its reasons"}
Every line is a separate process, as if the engineer answered the next morning:

```text
$ python main.py start J-201 "Replace 40 m of the cast-iron main" "Station Road" 65000
  (the approval node starts)
J-201 is waiting for the engineer: Rs 65,000
  brief: The work involves replacing 40 meters of the cast-iron main on Station Road due to frequent leaks and reduced water pressure affecting local residents. Immediate action is needed to prevent further disruptions and ensure reliable water supply in the area.
$ python main.py start J-202 "Replace a cracked meter cover" "Old Market" 1200
J-202: scheduled
$ python main.py start J-203 "Paint the Gandhi Chowk tank" "Gandhi Chowk" 90000
  (the approval node starts)
J-203 is waiting for the engineer: Rs 90,000
  brief: The work involves repainting the Gandhi Chowk water tank to prevent corrosion and ensure the longevity of the structure. This repair is needed now to maintain water quality and prevent potential leaks that could disrupt service to the community.
$ python main.py decide J-201 yes "Before the festival, please"
  (the approval node starts)
J-201: scheduled (Before the festival, please)
$ python main.py decide J-203 no "Not this year, the budget is for pipes"
  (the approval node starts)
J-203: refused: Not this year, the budget is for pipes
```

(We ran the five commands again on 26 November, on a new `repairs.db`: the same results. The first brief again gave
the reason "due to frequent leaks and reduced water pressure affecting local residents", which nobody had given.)

The small repair went straight to the schedule. The two big ones paused, each process ended, and each decision, in a
new process, reached the right paused job through `repairs.db`. Notice "(the approval node starts)" printed again on
every resume: the node really runs from its first line twice.

Now read the first brief as the engineer would. The facts given to the model were the work, the street and the
estimate. The brief adds "**due to frequent leaks and reduced water pressure**": nobody said that. The model invented a
reason, because the instruction asked for "why it is needed now" and no reason was given. An engineer approving Rs
65,000 on an invented reason is the worst kind of error, because it looks like information. The fix is in the graph:
pass the real reason as a fact (the street's complaint history from chapter 5: six complaints this year), and tell the
model to use only the facts given, or to say "no reason given". We tried the second half on the same facts, adding "Use
only the facts given. If no reason is given, write: No reason given." The brief became: "The work involves replacing
40 meters of the cast-iron main on Station Road. No reason given." Less fluent, and true.
:::

:::step{type=predict title="Guess first"}
:::question
`approval` sends the engineer an SMS ("A repair needs your approval") before calling `interrupt`. She approves. How many
SMS did she get?
:::
- [ ] One
- [x] Two: the node runs from its first line again on resume
- [ ] None
:::explain
The output above shows why: "(the approval node starts)" is printed again on every resume, so an SMS sent there
would be sent again. Put side effects in a node of their own before the approval (it runs once and is saved), or after it.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `interrupt` need a checkpointer?
:::
- [x] The paused run must be saved, so a later process can load it and continue
- [ ] To show the question
- [ ] It does not
:::explain
Without a checkpointer there is nothing to resume: we tried it, and the resume failed with `RuntimeError: Cannot use
Command(resume=...) without checkpointer`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What did the invented reason in the brief teach?
:::
- [ ] Engineers should not read briefs
- [x] Give the model every fact it is asked about, and tell it to use only those
- [ ] Use a longer brief
:::explain
When the prompt asks for something the facts do not contain, a model fills the gap with something that sounds likely.
:::
:::

:::step{type=deep-dive title="Go deeper: people in the loop"}
**Edit, not just approve.** The resume value can carry changes: `{"approve": True, "estimate": 58000}` lets the engineer
lower the estimate, and the node writes it into the state.

**Several questions at once.** Parallel nodes can each interrupt; the result lists all of them, each with an `id`, and
`Command(resume={id: answer, ...})` answers them together.

**Static breakpoints.** `compile(interrupt_before=["schedule"])` pauses before a node without changing its code. It is
useful for debugging; for real approvals, `interrupt` inside the node is clearer.

**Agents.** `HumanInTheLoopMiddleware` (the LangChain course) is built on this same `interrupt`.
:::

:::step{type=recap}
You can now:

- pause a run inside a node with `interrupt`, handing out a question;
- resume a paused thread with `Command(resume=...)`, from another process;
- remember that the paused node runs again from its first line, and keep side effects out of it;
- give a model only facts to summarise, after a brief invented a reason.

Next, chapter 11: time travel through a thread's checkpoints.

:::photo{src="/lesson-images/langgraph/lg-10-notes.webp" alt="Handwritten notes titled Interrupts, stop, ask a person, continue: interrupt with a value pauses a run inside a node and hands out a question, and Command with resume continues the same thread later, with interrupt returning that answer; write_brief, approval interrupt, saved and the process ends, Command resume yes, approval again then schedule; the paused node runs again from its first line; a plain dict makes the job start over and wait again; with no checkpointer the resume fails; the brief invented a reason until told not to" ai="true"}
One page of notes for this chapter.
:::
:::
