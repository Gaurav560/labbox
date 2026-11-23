:::step{type=story title="Some processes are just a list of steps"}
The repair job of chapter 9 is three steps in a row: book the crew, order the parts, send the SMS. As a graph it needed
a state class with a reducer, three nodes, four edges and a `compile`. Written as plain Python it is three lines.
And chapter 10's approval would be one `if`.

LangGraph's **Functional API** keeps the plain Python and adds the parts that mattered in Part 2: every finished step
saved, a crash resumed without repeating work, `interrupt` for a person's decision. A function marked `@entrypoint` is
the workflow; functions marked `@task` are its steps, whose results are saved in the checkpoint.

Graphs are still the better picture when there are branches, loops and parallel paths to see. For a straight process,
a function is easier to read.

:::mission
Turn the three steps into tasks so a resumed job skips what was done, then add the engineer's approval to the
workflow with `interrupt`.
:::
:::

:::step{type=history title="Futures and workflows as code"}
:::before{title="Waiting for every call"}
A program that calls something slow waits, doing nothing, until the answer comes, and the answer is lost if the program
stops.
:::

In **1977** Henry Baker and Carl Hewitt described **futures**: a call returns at once with a placeholder, and the program
asks for the value when it needs it. In **1988** Barbara Liskov and Liuba Shrira's **promises** brought the idea to
distributed systems; Python added `concurrent.futures` in **2011**. Workflow engines then let developers write durable
workflows as ordinary code (Temporal's workflows are plain functions whose steps are recorded), and in **January 2025**
LangGraph added its **Functional API**: `@task` calls return futures, and their results go into the same checkpoints as
a graph's steps.

:::solved
**Durable workflows in plain functions.** Ifs, loops and variables as usual; saved steps, resumes and interrupts for free.
:::

:::timeline
- **1977** Futures (Baker and Hewitt).
- **1988** Promises (Liskov and Shrira).
- **2011** Python's concurrent.futures.
- **2025** LangGraph's Functional API.
:::

Barbara Liskov, whose promises (with Liuba Shrira) let a program start a remote call and collect its result later. She received the Turing Award in 2008.

:::photo{src="/lesson-images/langgraph/liskov.webp" alt="Barbara Liskov, a woman with short curly hair in a light blue shirt with a flower pattern" credit="Kenneth C. Zirkel" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Barbara_Liskov_MIT_computer_scientist_2010.jpg"}
Barbara Liskov at MIT, 2010.
:::
:::

:::step{type=concept title="@task and @entrypoint" file="19-functional-api/flow.py" line="14-35"}
```python
@task
def order_parts(job: str) -> str:
    return board.order_parts(job)

@entrypoint(checkpointer=saver)
def repair_job(order: dict) -> list[str]:
    log = [book_crew(job).result(), order_parts(job).result()]
    ...
```

Calling a task returns a **future**; `.result()` waits for its value. Behind it, LangGraph saves each task's result in
the thread's checkpoint. When a crashed job is resumed (`invoke(None, config)`), the entrypoint runs again **from its
first line**, but each task call that already finished returns its saved result instead of running again. Only the
tasks that did not finish do real work.

| Graph API | Functional API |
|---|---|
| a state class, nodes and edges | a function and its local variables |
| `compile(checkpointer=...)` | `@entrypoint(checkpointer=...)` |
| a node's update is saved | a `@task` result is saved |
| branches are conditional edges | branches are `if` |

Because the entrypoint replays from the top, side effects belong **inside tasks**: code outside them runs again on every
resume.
:::

:::step{type=task task=task_steps title="Your turn: steps that are saved" file="19-functional-api/flow.py" line="14-35"}
Put `@task` above `book_crew`, `order_parts` and `send_sms`, and in `repair_job` call each one with `.result()`:
`[book_crew(job).result(), order_parts(job).result()]`, then `send_sms(job).result()`. Remove the TODO.

```bash run
cd /workspace/19-functional-api && rm -f jobs.db board_record.txt && SMS_FAILS=1 python main.py start J-301 18000
```

```bash run
cd /workspace/19-functional-api && python main.py resume J-301 && cat board_record.txt
```

Press **Check**.
:::

:::step{type=concept title="interrupt inside a function" file="19-functional-api/flow.py" line="28-35"}
`interrupt` works in an entrypoint exactly as in a node (chapter 10):

```python
if order["estimate"] > APPROVAL_OVER:
    decision = interrupt({"job": job, "estimate": order["estimate"], "question": "Approve this repair?"})
    if not decision["approve"]:
        return [f"{job}: refused ({decision.get('note', '')})"]
```

The run pauses at `interrupt` and is saved. `invoke(Command(resume={...}), config)` runs the entrypoint from its first line
again, and this time `interrupt` returns the decision. An early `return` is a refusal; no task runs.

:::diagram{name="lg-functional"}
Saved task results are replayed on resume; only unfinished tasks run again.
:::
:::

:::step{type=task task=approval_in_flow title="Your turn: approval in plain Python" file="19-functional-api/flow.py" line="28-35"}
In `repair_job`, before the tasks: if `order["estimate"] > APPROVAL_OVER`, call `interrupt({...})` with the job, the
estimate and the question; if the answer's `"approve"` is false, return `[f"{job}: refused ({decision.get('note', '')})"]`.

```bash run
cd /workspace/19-functional-api && python main.py start J-302 65000
```

```bash run
cd /workspace/19-functional-api && python main.py decide J-302 yes "Go ahead"
```

Press **Check**.
:::

:::step{type=try title="A crash, a resume, and an approval, in thirty lines"}
```text
$ rm -f jobs.db board_record.txt; SMS_FAILS=1 python main.py start J-301 18000
  book_crew: J-301: crew booked (South zone, tomorrow 8:00)
  order_parts: J-301: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
  SMS attempt 1
crashed: SmsTimeout: the SMS gateway did not answer in 10 seconds
$ python main.py resume J-301
  SMS attempt 1
  send_sms: J-301: SMS sent to the citizen
  repair_job: ['J-301: crew booked (South zone, tomorrow 8:00)', 'J-301: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)', 'J-301: SMS sent to the citizen']
$ python main.py start J-302 65000
  __interrupt__: (Interrupt(value={'job': 'J-302', 'estimate': 65000, 'question': 'Approve this repair?'}, id='b2f8006eb1feb5abcb0d1f2aaa979ff7', response_schema=None),)
$ python main.py decide J-302 yes "Go ahead"
  book_crew: J-302: crew booked (South zone, tomorrow 8:00)
  SMS attempt 1
  order_parts: J-302: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
  send_sms: J-302: SMS sent to the citizen
  repair_job: ['J-302: crew booked (South zone, tomorrow 8:00)', 'J-302: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)', 'J-302: SMS sent to the citizen']
$ cat board_record.txt
J-301: crew booked (South zone, tomorrow 8:00)
J-301: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
J-301: SMS sent to the citizen
J-302: crew booked (South zone, tomorrow 8:00)
J-302: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
J-302: SMS sent to the citizen
```

J-301 crashed at the SMS (one failure, and this version has no retry policy). The resume ran `repair_job` from the top,
but `book_crew` and `order_parts` returned their saved results: the only new work was one SMS attempt, and the record
has one crew and one order. The final line is the entrypoint's return value.

J-302 is over Rs 50,000, so it stopped at `interrupt` before any task ran; the `decide` run resumed it with the approval,
and the three tasks ran. (The stream reports each task's result as it arrives, so the SMS attempt printed by
`board.py` can appear before the parts line.)

The same behaviour as chapters 9 and 10, in a function you can read top to bottom.
:::

:::step{type=predict title="Guess first"}
:::question
`repair_job` calls `board.order_parts(job)` directly, without a task. The SMS fails, and the job is resumed. What happens?
:::
- [ ] The parts are not ordered again
- [x] The parts are ordered again: code outside tasks runs again on every resume
- [ ] The resume fails
:::explain
Only task results are saved. Every side effect belongs in a task.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does a `@task` call return?
:::
- [x] A future; `.result()` gives its value, saved in the checkpoint
- [ ] The value itself
- [ ] A node
:::explain
Futures also let several tasks run at once: start them all, then take each result.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
When is a graph a better choice than an entrypoint?
:::
- [ ] Never
- [x] When branches, loops and parallel paths should be visible, tested and drawn
- [ ] When there are more than three steps
:::explain
Both run on the same runtime. Pick the one that makes the process easiest to read.
:::
:::

:::step{type=deep-dive title="Go deeper: the Functional API in practice"}
**Parallel tasks.** `futures = [check_zone(s) for s in streets]` starts every task at once; `[f.result() for f in futures]`
collects them, like `Send` in chapter 6.

**Short-term memory.** `entrypoint.final(value=..., save=...)` returns one value and saves another for the thread's next
run, which reads it through a `previous` parameter.

**Mixing.** An entrypoint can call a compiled graph, and a graph node can call an entrypoint: use each where it reads
best.
:::

:::step{type=recap}
You can now:

- write a durable workflow as a function with `@entrypoint` and `@task`;
- resume a crashed workflow without repeating finished tasks;
- pause a function for a person's decision with `interrupt`;
- keep side effects inside tasks, and choose between a graph and a function.

That ends Part 3. Next, chapter 20: testing graphs.

:::photo{src="/lesson-images/langgraph/lg-19-notes.webp" alt="Handwritten notes about the Functional API: @entrypoint = the workflow; @task = a saved step; resume replays from line 1; side effects inside tasks; interrupt works here too" ai="true"}
One page of notes for this chapter.
:::
:::
