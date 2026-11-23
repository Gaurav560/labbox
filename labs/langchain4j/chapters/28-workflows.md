:::step{type=story title="The right desk, and a second look"}
Chapter 27's writer answered every message the same way, whatever the topic. Sahyadri Rail really has desks with
different knowledge: the refund desk knows the refund rules, the timetable desk knows the trains, and everything
else gets a polite holding reply. And the operations team has one more request: before any reply goes out,
someone should check it is short, kind, and promises nothing the railway cannot keep.

Both are workflows. **Routing** is a condition: read the topic, run one desk. **Checking** is a loop: score the
reply, improve it if needed, score again, stop when it is good or after a few tries. LangChain4j has a builder for
each, and a third for agents that can work at the same time, **in parallel**.

:::mission
Route each message to one of three desk agents with a conditional workflow, then add a review loop that improves a
reply until it scores 0.8.
:::
:::

:::step{type=history title="Workflows, then and now"}
:::before{title="Flowcharts on paper"}
Businesses have drawn workflows for a long time: "if the claim is over 10,000, send it to a manager". For decades
these lived on paper and in the heads of the people who ran them.
:::

**BPMN** (Business Process Model and Notation, **2004**) gave workflows a standard drawing that software could run,
and tools like **Apache Airflow** (created at Airbnb in **2014**) ran data workflows as code: steps, conditions,
loops and parallel branches. The patterns of this chapter are the same patterns, with model calls as the steps.

One pattern is new. In **March 2023** Aman Madaan and colleagues published **Self-Refine**: a model writes an answer,
criticises it, and rewrites it, several times. Quality improved on many tasks without any extra training. That is
the review loop you will build, with one change: a separate scorer agent, and code deciding when to stop.

:::solved
**Known shapes, model steps.** Sequence, condition, loop and parallel are well understood. Using them around model
calls keeps an AI application predictable: you know which steps can run, how often, and so what it can cost.
:::

:::timeline
- **2004** BPMN, a standard for business workflows.
- **2014** Apache Airflow at Airbnb.
- **2023** Self-Refine: generate, critique, refine.
- **2025** Agentic workflows in LangChain4j.
:::

Before workflow software, programmers drew flowcharts by hand with plastic templates like this IBM one: a diamond for a decision, a rectangle for a step, arrows for the order. The conditions and loops in this chapter are the same shapes, with agents in the boxes.

:::photo{src="/lesson-images/langchain4j/ibm-flowchart-template.webp" alt="An IBM flowcharting template, a green plastic stencil with cut-out shapes such as diamonds and rectangles, next to its paper holder listing the symbols" credit="Bubba73 (Jud McCranie)" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AIBM_flowchart_template.jpg"}
An IBM flowcharting template and its holder.
:::
:::

:::step{type=concept title="Four workflow shapes"}
| Builder | Runs | Setu uses it to |
|---|---|---|
| `sequenceBuilder()` | Sub-agents one after another (chapter 27) | classify, then answer, then review |
| `conditionalBuilder()` | Each sub-agent whose condition is true | send a message to one desk |
| `loopBuilder()` | Sub-agents again and again, until an exit condition or a maximum | improve a reply until it is good |
| `parallelBuilder()` | Sub-agents at the same time, on an executor | (example below) |

Every one of them is itself an agent, so they nest: this chapter's help desk is a sequence whose second step is a
condition and whose third step is a loop.

:::diagram{name="l4j-workflow"}
A message is classified, routed to one desk by its topic, then scored and edited in a loop until it is good enough.
:::

Conditions and exit tests are plain Java lambdas that read the scope, so **code** makes every decision about which
step runs next.
:::

:::step{type=example title="Worked example: two checks at once" file="28-workflows/src/main/java/com/setu/Flows.java" line="13-15"}
When two agents do not depend on each other, a parallel workflow runs them at the same time (only to read, it is not
in your project). Here a complaint is summarised for the duty manager while its urgency is rated:

```java
AgenticServices.parallelBuilder()
        .subAgents(summaryAgent, urgencyAgent)          // both read "message" from the scope
        .executor(Executors.newFixedThreadPool(2))      // two threads: the calls overlap
        .output(scope -> scope.readState("urgency") + ": " + scope.readState("summary"))
        .build();
```

Two calls of about a second each finish in about one second instead of two. The cost is the same: two calls are two
calls. `output(...)` combines what the sub-agents wrote into the workflow's result.
:::

:::step{type=concept title="Routing with conditions" file="28-workflows/src/main/java/com/setu/Flows.java" line="17-25"}
`conditionalBuilder()` takes pairs of a condition and an agent:

```java
.subAgents(scope -> scope.readState("topic", Topic.OTHER) == Topic.REFUND, refundDesk)
```

`readState("topic", Topic.OTHER)` reads the classifier's answer, with a default if it is missing. Every agent whose
condition is true runs, in order. So the conditions must not overlap, and together they must cover every topic:
REFUND, TIMETABLE, and "neither" for everything else. A message that matched no condition would get no reply.

The three desks are in `Experts.java`: each is an agent with its own instructions and the output key `reply`.
:::

:::step{type=task task=conditional_route title="Your turn: route to a desk" file="28-workflows/src/main/java/com/setu/Flows.java" line="17-25"}
Finish `Flows.desks(model)`: a `conditionalBuilder()` with three `subAgents(condition, agent)` pairs: REFUND to
`Experts.RefundDesk`, TIMETABLE to `Experts.TimetableDesk`, and any other topic to `Experts.GeneralDesk`. Build each
desk with the helper `agent(Experts.RefundDesk.class, model, "reply")`.

Press **Check**.
:::

:::step{type=concept title="A loop with a ceiling" file="28-workflows/src/main/java/com/setu/Review.java" line="13-25"}
The review loop has two agents from `Review.java`: `ReplyScorer` reads `reply` and writes `score` (a `double` from 0
to 1), and `ReplyEditor` reads `reply` and writes a better `reply`.

```java
AgenticServices.loopBuilder()
        .subAgents(scorer, editor)
        .maxIterations(3)
        .exitCondition(scope -> scope.readState("score", 0.0) >= 0.8)
        .build();
```

The exit condition is tested after each sub-agent, so a reply that scores 0.8 at once leaves before the editor runs:
one call. A reply that never scores 0.8 stops after three rounds: six calls. **`maxIterations` is a cost ceiling**: a
loop without one, with a strict scorer, would call the model until your budget ran out.
:::

:::step{type=task task=review_loop title="Your turn: the review loop" file="28-workflows/src/main/java/com/setu/Flows.java" line="27-33"}
Finish `Flows.reviewLoop(model)`: a `loopBuilder()` with the scorer (output key `score`) and the editor (output key
`reply`), at most 3 iterations, exiting when the score is at least 0.8.

`Flows.desk(model)` joins everything: classifier, desks, review loop. `Trace` prints the start of every prompt, so
you can see each agent work:

```bash run
cd /workspace/28-workflows && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Three paths through one workflow"}
```text
$ mvn -q compile exec:java

> I cancelled my Ratnagiri ticket 3 days before, how much do I get back?
  [model call] Which team should handle this passenger message? Answer with...
  [model call] You handle refunds. Cancelled 24 hours or more before depart...
  [model call] Score this reply to a railway passenger from 0.0 to 1.0: 1.0...
You will receive a full refund for your Ratnagiri ticket since you cancelled it 3 days before departure. Refunds typically take 5 working days to process.

> When does the Monsoon Mail reach Karjat?
  [model call] Which team should handle this passenger message? Answer with...
  [model call] You handle timetable questions, using only the facts. Answer...
  [model call] Score this reply to a railway passenger from 0.0 to 1.0: 1.0...
  [model call] Rewrite this reply to a railway passenger: at most two sente...
  [model call] Score this reply to a railway passenger from 0.0 to 1.0: 1.0...
The Monsoon Mail arrives in Karjat at 18:40 and departs from Pune at 16:05. Please check the schedule for any updates.

> the review loop alone, on a bad reply:
  [model call] Score this reply to a railway passenger from 0.0 to 1.0: 1.0...
  [model call] Rewrite this reply to a railway passenger: at most two sente...
  [model call] Score this reply to a railway passenger from 0.0 to 1.0: 1.0...
score 0.8: Dear passenger, we sincerely apologize for the inconvenience you've experienced. While we cannot guarantee specific outcomes, we are working to resolve the issue as quickly as possible.
```

Follow the trace. The refund message went to the refund desk, which applied the 24-hour rule correctly, and the
reply passed review at once. The timetable question went to the timetable desk; its reply scored below 0.8, was
rewritten and passed. The bad reply ("SO sorry!!!", a free ticket, a personal call from the manager) lost its
promises in one edit.

Two real lessons from this run:

1. **Agents multiply calls.** Three jobs took 11 model calls. On our first attempt, the run stopped half-way with
   `Too many requests: the limit is 20 a minute`: the gateway's rate limit, reached after two runs in one minute.
   Count calls per request before you go live, and set budgets.
2. **The same input can take another path.** In an earlier run, the Monsoon Mail reply ("The Monsoon Mail reaches
   Karjat at 18:40. It operates daily from Pune.") passed review at once. A score from a model is a model's
   judgement, not a measurement: the loop's ceiling keeps it safe either way.
:::

:::step{type=predict title="Guess first"}
:::question
A scorer that never gives more than 0.5 meets this loop. How many model calls does one review take?
:::
- [ ] One
- [ ] It never stops
- [x] Six: three rounds of score and edit, then `maxIterations` stops it
:::explain
The ceiling is the point. Without it, a strict scorer would loop until the budget or the rate limit stopped it.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two desks' conditions are both true for one message. What happens?
:::
- [ ] Only the first runs
- [x] Both run, in order, and the second's `reply` replaces the first's
- [ ] The workflow fails
:::explain
Every agent with a true condition runs. Make the conditions exclusive, and cover every case.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does a parallel workflow save?
:::
- [x] Time: independent calls overlap
- [ ] Money: parallel calls are cheaper
- [ ] Tokens
:::explain
Each call is billed the same. Parallel runs only reduce how long the passenger waits.
:::
:::

:::step{type=deep-dive title="Go deeper: workflows in practice"}
**Exit at the end.** `.testExitAtLoopEnd(true)` checks the exit condition only after a whole round, when every
sub-agent must run before stopping.

**Errors.** Every workflow builder has `.errorHandler(...)`, which can retry a failed step, skip it, or stop. Rate
limits (`429`) are worth retrying after a pause; a missing scope value is a bug.

**Parallel over a list.** `parallelMapperBuilder()` runs one agent for each item of a list in the scope, for example
one summary per complaint in a batch.

**Human in the loop.** `humanInTheLoopBuilder()` adds a step that waits for a person, for example a manager approving
a refund above a limit before the reply goes out.
:::

:::step{type=recap}
You can now:

- choose between sequence, condition, loop and parallel workflows;
- route a message to one agent with `conditionalBuilder()` and exclusive conditions;
- improve an answer with a scored loop, and cap its cost with `maxIterations`;
- count the model calls a workflow makes, and expect its paths to vary.

Next, chapter 29: supervisor agents. A model plans which agents to call, and in which order.

:::photo{src="/lesson-images/langchain4j/l4j-28-notes.webp" alt="Handwritten notes about workflows: sequence, condition, loop, parallel; conditions must not overlap; the loop scores, edits and scores again; maxIterations is a cost ceiling; 3 jobs took 11 model calls" ai="true"}
One page of notes for this chapter.
:::
:::
