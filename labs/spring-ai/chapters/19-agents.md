:::step{type=story title="One question, several steps"}
So far every feature of Atlas was one call to the model, sometimes with a tool or two. Some jobs do not fit in one
call. The museum's front desk, the planetarium desk and the science explainers each answer differently, from
different facts: one prompt for all of them grows long, slow and confused. And the education team wants Atlas to
write labels for children, which must follow strict rules; the first draft rarely does.

People solve such jobs in steps: one person decides who should answer, another writes, a third checks. With language
models you can build the same thing: several calls, each with one clear job, joined by your Java code. These are
**workflows**, and when the model itself decides the steps, **agents**.

In 1907, every telephone call went first to an operator at a switchboard, who asked who you wanted and plugged you
through to the right line.

:::photo{src="/lesson-images/spring-ai/switchboard.webp" alt="A long row of telephone operators in white blouses seated at a switchboard that runs the length of a large hall" credit="The Salt Lake Herald" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Telephone_switchboard_6_Oct_1907_Salt_Lake_City.jpg"}
Telephone operators at a newly installed switchboard in Salt Lake City, 6 October 1907.
:::

:::mission
Build two workflows: a router that sends each question to the right desk, and a writer and reviewer that improve an
exhibit label until it follows the rules.
:::
:::

:::step{type=history title="From chains to agents"}
As soon as language models became useful, people started joining calls together. In **2022**, Harrison Chase released
LangChain, a Python library for chains of model calls, and researchers published ReAct, a pattern where the model
reasons, calls a tool, reads the result, and decides the next step in a loop: the first **agents**.

:::before{title="Agents everywhere"}
By 2023, agent frameworks promised systems that plan and act on their own. Many were hard to predict, hard to debug,
and expensive: an agent that decides its own steps can take twenty calls where three would do, or loop.
:::

In **December 2024**, Anthropic published "Building Effective Agents", drawn from its work with many teams. Its
advice: start with the simplest thing that works; prefer **workflows** (steps fixed in your code) for tasks you
understand, and use **agents** (the model chooses the steps) only where flexibility is worth the cost. It described a
handful of patterns. Spring AI's documentation shows each one in a few lines of Java.

:::solved
**Patterns, not frameworks.** A chain, a router, parallel calls, an orchestrator with workers, an evaluator and an
optimizer: each is a few calls to a `ChatClient` and ordinary Java (loops, maps, records). You already know everything
needed to build them.
:::
:::

:::step{type=concept title="The patterns"}
| Pattern | What happens | Use it when |
|---|---|---|
| **Chain** | the output of one call is the input of the next | a task has clear steps (outline, then write, then shorten) |
| **Routing** | one call classifies the input; a specialised prompt handles it | inputs fall into kinds that need different handling |
| **Parallelisation** | several calls run at once; code combines the results | independent parts, or several opinions to compare |
| **Orchestrator and workers** | one call plans subtasks; worker calls do them | the subtasks are not known in advance |
| **Evaluator and optimizer** | one call writes, another reviews; repeat with the feedback | clear rules to check, and rewriting helps |
| **Agent** | the model calls tools in a loop until it decides it is done | open-ended tasks; you accept less predictability |

Atlas's tool calling in chapter 7 was already a small agent: the model decided to call `nextDay`, then `openingHours`,
then answer. This chapter builds the two most useful workflows.

:::diagram{name="ai-workflows"}
A router picks the desk; a writer and a reviewer take turns until the label passes.
:::
:::

:::step{type=example title="Worked example: classify, then answer" file="19-agents/src/main/java/com/atlas/AgentController.java" line="70"}
Routing is two calls. The first only classifies, into a closed set your code understands; the second answers with the
prompt for that class:

```java
Desk desk = chat.prompt()
        .system(ROUTER)                 // "sort visitor questions into one desk: EXHIBITS, VISIT, BOOKING"
        .user(q)
        .call()
        .entity(Routing.class)          // record Routing(Desk desk), Desk an enum
        .desk();
String answer = chat.prompt()
        .system(DESKS.get(desk))        // the chosen desk's own prompt and facts
        .user(q)
        .call()
        .content();
```

1. The enum is the closed set: structured output (chapter 5) makes the model pick one of its values.
2. Each desk's prompt is short and focused: the front desk knows hours and prices, the explainer knows how to talk to
   a ten-year-old. Short focused prompts follow their rules better than one long prompt with every rule.
3. Your code sees the route, so it can log it, count it, or send BOOKING somewhere else entirely.
:::

:::step{type=task task=route_question title="Your turn: route to the right desk" file="19-agents/src/main/java/com/atlas/AgentController.java" line="71"}
In `19-agents`, finish `GET /agent/route?q=...`: ask the model which `Desk` fits (the `ROUTER` prompt, as a `Routing`),
then answer with `DESKS.get(desk)`, and return both.

```bash run
cd 19-agents && mvn -q -o spring-boot:run
```

```bash run
curl -s -G localhost:8080/agent/route --data-urlencode "q=Are you open on Sunday?" | jq .
```

Press **Check**.
:::

:::step{type=try title="Three desks"}
```text
$ curl -s -G localhost:8080/agent/route --data-urlencode "q=Are you open on Sunday?" | jq .
{
  "desk": "VISIT",
  "answer": "Yes, we are open on Sunday from 10:00 to 18:00."
}
$ curl -s -G localhost:8080/agent/route --data-urlencode "q=Why does the pendulum turn?" | jq .
{
  "desk": "EXHIBITS",
  "answer": "A pendulum swings back and forth because of gravity! When you pull it to one side and let go, gravity pulls it down, and it moves to the other side due to its energy. It will keep swinging until friction and air slow it down."
}
$ curl -s -G localhost:8080/agent/route --data-urlencode "q=Can I get two seats for the 4 o clock show?" | jq .
{
  "desk": "BOOKING",
  "answer": "You can book your seats at atlas.deccanscience.example/book or at the ticket counter."
}
```

Three questions, three right desks, and each desk answered in its own voice: the front desk with the real hours, the
booking desk with where to book. But look at the pendulum answer. The router was right; the explainer was not: it
explained why an ordinary pendulum swings, not why Foucault's pendulum **turns**. The explainer desk has no exhibit
cards, so it answered from general knowledge. Routing decides **who** answers; it does not give them knowledge. In
chapter 20, retrieval (chapter 14) is added to every answer.
:::

:::step{type=concept title="Write, review, rewrite"}
The education team's rules for a children's label: at most 40 words, only words a nine-year-old knows, and end with a
question that makes the reader look closer at the exhibit. A model writing a text often misses one rule or another; a
second call whose only job is to check the text against the rules catches many of those misses. (Many, not all: you
will see a reviewer get one badly wrong.)

So split the job. A **writer** call drafts the label. A **reviewer** call checks it against the rules and returns a
`Review(boolean approved, String feedback)`. If it is not approved, the writer gets its draft back with the feedback
and tries again. And because a loop that calls a paid model must always end, it stops after at most **three drafts**,
approved or not.
:::

:::step{type=task task=improve_loop title="Your turn: review and rewrite" file="19-agents/src/main/java/com/atlas/AgentController.java" line="83"}
Finish `GET /agent/label?exhibit=...`: the first draft is written. In a loop, ask the reviewer (`REVIEWER` and `RULES`,
as a `Review`); stop when it is approved or after 3 drafts; otherwise ask the `WRITER` to rewrite, giving it the draft
and the feedback. Return the last draft and how many drafts it took.

```bash run
curl -s -G localhost:8080/agent/label --data-urlencode "exhibit=the prism room" | jq .
```

Press **Check**.
:::

:::step{type=try title="A label, improved"}
```text
$ curl -s -G localhost:8080/agent/label --data-urlencode "exhibit=the prism room" | jq .
{
  "text": "**The Prism Room**  \nWelcome to the amazing Prism Room! Here, light bends and makes bright rainbows. Discover how prisms turn light into colors. Can you find all the colors shining around you?",
  "drafts": 3
}
```

Three drafts, and the label was never approved: the loop stopped at its limit, as it should. Why? The last review,
from the gateway's log:

```text
$ lab requests --last
2026-11-23 00:02:59 UTC  ai-chat -> openai/gpt-4o-mini  270 in, 31 out
...
--- response ---
... "content": "{\n  \"approved\": false,\n  \"feedback\": \"The label has 46 words, so reduce the word count ...
```

Count the words of the final label yourself: 32, under the limit of 40. The reviewer was wrong. Models are poor at
counting words, whether they write the text or check it, so the reviewer kept rejecting good drafts, and every round
cost two calls. The fix is the lesson of chapter 7 again: **do not let the model calculate**. Count the words in Java
(`text.split("\\s+").length`) and ask the reviewer only about what needs judgement: hard words, and the question at
the end. (The writer also added Markdown, `**The Prism Room**`; a rule "plain text only" would fix that.)
:::

:::step{type=predict title="Guess first"}
:::question
Why does the label loop stop after 3 drafts even when the reviewer never approves?
:::
- [ ] The model can only write 3 drafts
- [x] Every round is two paid model calls; a loop without a limit could run, and cost, forever
- [ ] Spring AI stops loops after 3 calls
:::explain
Any loop around a model needs a hard limit, in steps and in money. Return the best draft you have, and log that it
was not approved so a person can look at it.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What is the difference between a workflow and an agent, in "Building Effective Agents"?
:::
- [x] In a workflow your code fixes the steps; in an agent the model decides the steps, using tools in a loop
- [ ] Agents use bigger models
- [ ] Workflows cannot call tools
:::explain
Workflows are predictable, testable and cheaper; agents are flexible. Start with a workflow, and give the model control
only where you need it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The router answers with a desk that is not in your enum, like "TICKETS". What happens?
:::
- [ ] The route is created
- [x] Turning the answer into the enum fails, so your code must handle it (for example, fall back to EXHIBITS)
- [ ] The second call answers anyway
:::explain
Structured output makes such mistakes rare, not impossible. A closed set lets your code notice and recover, which an
open text answer would not.
:::
:::

:::step{type=deep-dive title="Go deeper: when to build an agent"}
**Real agents in Spring AI.** Give a `ChatClient` tools and a goal, and the tool-calling loop you used in chapter 7 is
an agent: the model keeps calling tools until it can answer. Keep its tools few and safe, check permissions in them
(chapter 8's `ToolContext`), and let tool call confirmation put a person in the loop where it matters.

**Parallel calls.** Independent steps (for example, the same question to three desks, to compare) can run at once with
Java's virtual threads or `CompletableFuture`; the total time is the slowest call, not the sum.

**Orchestrator and workers.** For "plan a school visit for 40 children who like space and dinosaurs", one call can
plan the parts (the route, the show times, the lunch break), worker calls handle each part (with tools), and a last
call writes the plan.

**Cost and time.** Every step is a model call: routing doubles the calls for each question, and a review loop can
make six. Use a small model for routing and reviewing, measure with chapter 18's meter, and check quality with chapter
16's golden set.
:::

:::step{type=recap}
You can now:

- tell workflows from agents, and choose the simpler one first;
- name the patterns from "Building Effective Agents": chain, routing, parallelisation, orchestrator and workers,
  evaluator and optimizer;
- build a router with an enum and specialised prompts;
- build a write, review and rewrite loop that always ends.

Next, chapter 20: everything together. Atlas goes live.

:::photo{src="/lesson-images/spring-ai/springai-19-notes.webp" alt="Handwritten notes about workflows and agents: start with a workflow; route: classify, then answer; write, review, rewrite; always a limit: 3 drafts; every step is a paid call" ai="true"}
One page of notes for this chapter.
:::
:::
