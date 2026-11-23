:::step{type=story title="A request nobody planned for"}
Chapter 28's workflows handle the messages the railway expected: refunds, timetables, complaints. Then a family
writes: "We are 2 adults going from Pune to Ratnagiri next Sunday. What is the date, and the total fare?" That needs
a date, a fare and some arithmetic, in an order no workflow was written for.

You could write one more workflow. Or you could let a model **plan**: give it a set of agents with clear
descriptions, and let it decide which to call, with which arguments, until the request is done. LangChain4j calls
that model a **supervisor**, and this is what its documentation calls **pure agentic AI**.

:::mission
Give a fare agent its tool, then build a supervisor that plans over the fare agent and a date agent and answers with
a summary.
:::
:::

:::step{type=history title="A model that chooses the tools"}
:::before{title="Every step written by hand"}
In a workflow, a programmer decides every step. That is predictable, and it means every new kind of request needs
new code.
:::

In **March 2023** Microsoft researchers published **HuggingGPT**: a language model that read a request, chose which
specialist models from the Hugging Face hub to run, in which order, and combined their results. A model as a
**controller** of other models. The same year, plan-and-execute agents split the work into a **planner** that writes
the next step and **workers** that do it. Through 2024 and 2025, frameworks made the idea a standard building block:
a supervisor agent over a team of sub-agents, as in LangGraph's supervisor and LangChain4j's `supervisorBuilder()`.

:::solved
**Requests nobody planned for.** A supervisor can combine its agents in new ways for new requests. The price is
predictability: you no longer know in advance how many calls a request will take, or that the plan will be right.
:::

:::timeline
- **2022** ReAct: a model chooses its next action (chapter 27).
- **2023** HuggingGPT: a model as controller of other models; planner and worker agents.
- **2024 to 2025** Supervisor agents in agent frameworks, including LangChain4j.
:::
:::

:::step{type=concept title="Agents with tools" file="29-supervisor/src/main/java/com/setu/Specialists.java" line="13-24"}
The sub-agents are small and honest about what they do:

```java
public interface FareAgent {
    @UserMessage("Use the fare tool to find the fare from Pune to {{destination}} for one adult. Return only the number.")
    @Agent("Finds the fare in rupees from Pune to a station, for one adult")
    int fare(@V("destination") String destination);
}
```

An agent can have tools, exactly like an AI Service in chapter 19: `.tools(new RailTools())` on its builder. So the
fare agent never guesses a fare, and the date agent never guesses a date: each asks Java.

The `@Agent` description matters more here than anywhere else in the course. The supervisor model reads only the
agents' names, descriptions and arguments to decide what to call. A vague description is a wrong plan.
:::

:::step{type=task task=tool_agent title="Your turn: the fare agent" file="29-supervisor/src/main/java/com/setu/Supervisor.java" line="18-23"}
Finish `Supervisor.fareAgent(model)`: `AgenticServices.agentBuilder(Specialists.FareAgent.class)` with the model,
`.tools(new RailTools())` and the output key `"fare"`. `dateAgent(model)` below it is the same pattern, already done.

Press **Check**.
:::

:::step{type=concept title="How a supervisor plans" file="29-supervisor/src/main/java/com/setu/Supervisor.java" line="32-38"}
`AgenticServices.supervisorBuilder()` builds a `SupervisorAgent`. Calling `invoke(request)` runs a loop:

1. The **planner** model gets the request, the list of agents (`{'name', 'description', [arguments]}`) and the last
   result, and answers with the next step as JSON: `{"agentName": "fare", "arguments": {"destination": "Ratnagiri"}}`.
2. LangChain4j runs that agent and stores its result.
3. Back to the planner with the new result, until it answers `{"agentName": "done", "arguments": {"response": "..."}}`.

LangChain4j's own planner instructions say: *"Decide which agent to invoke next, doing things in small steps and
never taking any shortcuts or relying on your own knowledge."*

Two settings shape the answer:

| Setting | What it does |
|---|---|
| `responseStrategy(...)` | `LAST`: the last agent's raw result; `SUMMARY`: the planner's final recap; `SCORED`: a model picks the better of the two |
| `supervisorContext("...")` | House rules added to the planner's instructions, for things the agent descriptions cannot say |

Setu wants `SUMMARY`: the family asked for a date and a fare, and the last agent alone knows only one of them.
:::

:::step{type=task task=supervisor_agent title="Your turn: the supervisor" file="29-supervisor/src/main/java/com/setu/Supervisor.java" line="32-38"}
Finish `Supervisor.supervisor(model)`: `AgenticServices.supervisorBuilder()` with the model, the fare and date agents as
sub-agents, `.supervisorContext(CONTEXT)` and `.responseStrategy(SupervisorResponseStrategy.SUMMARY)`.

`CONTEXT` is written above it. Read it before you run, and the next step shows why it is there.

```bash run
cd /workspace/29-supervisor && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Careful: a confident plan with a wrong total"}
When we first wrote this chapter the supervisor had no `supervisorContext`. Here is that real run:

```text
$ mvn -q compile exec:java
> We are 2 adults going from Pune to Ratnagiri next Sunday. What is the date, and the total fare?
  [model call] The user request is: 'We are 2 adults going from Pune to Rat...
  [model call] Use the date tool to find the date of the next Sunday. Retur...
  [model call] The user request is: 'We are 2 adults going from Pune to Rat...
  [model call] Use the fare tool to find the fare from Pune to Ratnagiri fo...
  [model call] The user request is: 'We are 2 adults going from Pune to Rat...
The date for next Sunday is 2026-11-29, and the total fare for 2 adults going from Pune to Ratnagiri is 420 rupees.
```

The plan was good: the date agent, then the fare agent, then done. Both tools gave correct facts: 29 November, and
Rs 420 **for one adult**. Then the planner wrote the summary and called 420 the **total for two**. Nothing failed,
nothing was logged as an error, and the answer was wrong by half.

The cause is that the planner knew the fare agent's description but not what its number meant for this request.
`CONTEXT` tells it: "The fare agent returns the fare for ONE adult. When several adults travel, multiply that fare by
the number of adults, and show the sum in the answer." With it, the same request:

```text
$ mvn -q compile exec:java
> We are 2 adults going from Pune to Ratnagiri next Sunday. What is the date, and the total fare?
  [model call] The user request is: 'We are 2 adults going from Pune to Rat...
  [model call] Use the date tool to find the date of the next Sunday. Retur...
  [model call] The user request is: 'We are 2 adults going from Pune to Rat...
  [model call] Use the fare tool to find the fare from Pune to Ratnagiri fo...
  [model call] The user request is: 'We are 2 adults going from Pune to Rat...
The date for next Sunday is 2026-11-29, and the total fare for 2 adults going from Pune to Ratnagiri is 840 rupees.
```

Right this time. But notice what fixed it: a sentence, not code. The multiplication still happened inside a model,
and chapter 19 said facts and arithmetic belong in Java. For money, the sturdier fix is a tool that does the sum
(`fare(destination, adults)`), and a golden question with two adults in chapter 26's eval, so this mistake cannot
come back unnoticed.

The trace (from the `Trace` listener) also shows the price of planning. It prints five prompts, and three of them
only decide what to do next. Each agent also makes a second call with its tool's result, which the trace does not
print (that request ends with a tool message, not a user message): **seven model calls** in all. A fixed workflow
running the same two agents would take four.
:::

:::step{type=predict title="Guess first"}
:::question
When should Setu use a supervisor instead of a workflow?
:::
- [ ] Always: it is more intelligent
- [x] For varied requests no workflow covers, accepting more calls and less predictability
- [ ] Never: supervisors cannot use tools
:::explain
Prefer the simplest thing that works. Workflows for the requests you know; a supervisor, with budgets and evals, for
the long tail.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does the supervisor's planner know about each sub-agent?
:::
- [ ] Its Java code
- [x] Its name, its `@Agent` description and its arguments
- [ ] The tools inside it
:::explain
That is all it plans with, so descriptions are part of your program's logic. Write them as carefully as code.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
With `responseStrategy(LAST)`, what would the family have received?
:::
- [ ] The full summary
- [x] Only the last agent's result: 420
- [ ] Nothing
:::explain
`LAST` returns the last sub-agent's raw output. `SUMMARY` returns the planner's recap of everything that was done.
:::
:::

:::step{type=deep-dive title="Go deeper: supervisors safely"}
**A ceiling.** `.maxAgentsInvocations(n)` caps how many agents one request may call, like `maxIterations` for loops.

**Typed supervisors.** `supervisorBuilder(MySupervisor.class)` gives the supervisor your own interface instead of
`SupervisorAgent`, and `@SupervisorAgent` declares one with annotations.

**Context strategy.** `.contextGenerationStrategy(...)` chooses what the planner remembers between steps: its own
chat memory, a summary of what the agents did, or both.

**Agents across services.** The agentic module can also call agents served elsewhere over the **Agent2Agent (A2A)**
protocol (`a2aBuilder(url)`), the agent-to-agent counterpart of chapter 20's MCP.
:::

:::step{type=recap}
You can now:

- explain a supervisor: a planner model choosing agents and arguments step by step;
- give agents tools, and write descriptions a planner can plan with;
- choose a response strategy, and add house rules with `supervisorContext`;
- spot a confidently wrong plan, and fix it with context, a tool and an eval.

Next, chapter 30: the capstone. Setu goes live as one Spring Boot app with everything from this course.

:::photo{src="/lesson-images/langchain4j/l4j-29-notes.webp" alt="Handwritten notes about supervisors: a model plans; it reads names and descriptions; SUMMARY returns the planner's recap; right plan, wrong total of 420; context fixed it to 840" ai="true"}
One page of notes for this chapter.
:::
:::
