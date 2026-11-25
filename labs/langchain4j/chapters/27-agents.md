:::step{type=story title="One assistant, too many jobs"}
Setu's help desk now gets complaints, refund requests and timetable questions in one stream, and the operations
team wants each message to reach the right team with a kind first reply. One prompt could try to do all of it:
"Decide the team, then write a reply, then...". Prompts like that grow, become hard to test, and fail in ways
that are hard to find.

The alternative is to split the work. One small AI Service **classifies** the message. Another **writes** the reply,
knowing the team. Each has one job and one prompt you can test alone. LangChain4j's **agentic** module calls each
of them an **agent**, and lets you join agents into **workflows**.

:::mission
Turn a classifier into an agent that stores its answer in a shared scope, then join it with a reply-writer in a
sequence.
:::
:::

:::step{type=history title="From ReAct to agent frameworks"}
:::before{title="One prompt, one answer"}
Until 2022, applications used a language model for one step: a prompt in, a text out. Anything with several steps
was ordinary code around it.
:::

In **October 2022** Shunyu Yao and colleagues published **ReAct**: a model that alternates reasoning and actions
(calling tools), observing each result before the next step. In **2023** projects like **AutoGPT** (March) and
**BabyAGI** (April) let a model plan and run its own steps towards a goal; they were exciting and unreliable, often
looping or wandering off. Frameworks for teams of agents followed, such as Microsoft's **AutoGen** (2023).

In **December 2024** Anthropic's essay *Building effective agents* drew the line most teams now use: **workflows**,
where code decides the order of the steps, and **agents**, where the model decides. Its advice was to prefer the
simplest one that works. LangChain4j's `langchain4j-agentic` module, released in **2025**, offers both. (In 1.24 it is still a beta module:
this lab uses version `1.24.0-beta34`, so names may change.)

:::solved
**Small, testable steps.** Each agent is an AI Service with one job; workflows join them with code you can read.
When something fails you know which step it was.
:::

:::timeline
- **2022** ReAct: reason, act, observe.
- **2023** AutoGPT, BabyAGI, AutoGen.
- **2024** Workflows versus agents (Anthropic).
- **2025** LangChain4j's agentic module.
:::
:::

:::step{type=concept title="An agent is an AI Service with a name and an output key" file="27-agents/src/main/java/com/setu/TopicClassifier.java" line="8-13"}
`TopicClassifier` looks like chapter 15's classifier, with one new annotation:

```java
public interface TopicClassifier {
    @UserMessage("Which team should handle this passenger message? Answer with one word. Message: {{message}}")
    @Agent("Decides which team should handle a passenger message")
    Topic classify(@V("message") String message);
}
```

`@Agent` gives the agent a **description**, which other parts of the system (and in chapter 29, another model) read
to know what it does. `@V("message")` names the argument, so the agent can read it from the scope.

Agents share an **agentic scope**: a map of named values for one run. An agent reads its arguments from the scope by
their `@V` names, and writes its result to the scope under its **output key**:

| Agent | Reads | Writes |
|---|---|---|
| `TopicClassifier` | `message` | `topic` (a `Topic`) |
| `ReplyWriter` | `message`, `topic` | `reply` (a `String`) |

That is how agents pass work to each other without knowing each other: through names in the scope.
:::

:::step{type=example title="Worked example: building the writer agent" file="27-agents/src/main/java/com/setu/Agents.java" line="18-23"}
`Agents.writer(model)` is already written. An agent is built like an AI Service, by `AgenticServices` instead of
`AiServices`:

```java
AgenticServices.agentBuilder(ReplyWriter.class)
        .chatModel(model)
        .outputKey("reply")    // its answer goes into the scope as "reply"
        .build();
```

The result is a normal Java object: `writer.write("My train was late", Topic.COMPLAINT)` works on its own, which
makes each agent easy to test.
:::

:::step{type=task task=first_agent title="Your turn: the classifier agent" file="27-agents/src/main/java/com/setu/Agents.java" line="12-16"}
Finish `Agents.classifier(model)`, the same way as `writer` above:

1. `AgenticServices.agentBuilder(TopicClassifier.class)`;
2. `.chatModel(model)`;
3. `.outputKey("topic")`, then `.build()`.

The usual slip: leaving out `.outputKey("topic")`. The agent still works alone (we tried it on 26 November: "classifier
alone: REFUND"), but in the workflow the writer finds no `topic` and the run stops with `Missing argument: topic`.

Press **Check**.
:::

:::step{type=concept title="A sequence: one agent after another" file="27-agents/src/main/java/com/setu/Agents.java" line="25-30"}
The simplest workflow runs agents in order:

```java
AgenticServices.sequenceBuilder(DeskWorkflow.class)
        .subAgents(classifier(model), writer(model))
        .outputKey("reply")    // the workflow's answer: "reply" from the scope at the end
        .build();
```

`DeskWorkflow` is a typed interface with one method, `handle(@V("message") String message)`. Calling it puts
`message` in a new scope, runs the classifier (which adds `topic`), runs the writer (which reads `message` and
`topic` and adds `reply`), and returns `reply`.

:::diagram{name="l4j-sequence"}
The refund message on 26 November: what the scope holds after each step, and what each step cost.
:::

The order is **code**, not a model's decision: the classifier always runs first. That is what makes this a workflow.
:::

:::step{type=task task=sequence_workflow title="Your turn: the help desk workflow" file="27-agents/src/main/java/com/setu/Agents.java" line="25-30"}
Finish `Agents.desk(model)`:

1. `AgenticServices.sequenceBuilder(DeskWorkflow.class)`;
2. `.subAgents(classifier(model), writer(model))`, in that order;
3. `.outputKey("reply")`, then `.build()`.

The usual slip: the sub-agents in the wrong order, writer first. We tried it on 26 November: the writer runs before
anyone has written `topic`, and the run stops with the same `Missing argument: topic`.

```bash run
cd /workspace/27-agents && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Two agents at the help desk"}
```text
$ mvn -q compile exec:java
classifier alone: REFUND

> I cancelled yesterday, where is my money?
Your cancellation request has been forwarded to the REFUND team. They will process your refund as soon as possible.

> The 7:15 was 40 minutes late again and nobody announced anything!
Thank you for your feedback regarding the delay of the 7:15 train. Our Complaint team will handle your concern and get back to you shortly.
```

We ran it again on 26 November. The classifier said `REFUND` again; the replies were worded a little differently
("Your refund request has been sent to the REFUND team. They will process it and you should receive your money
soon."), and the capitals leaked again. The gateway's log shows the cost of splitting: the classifier calls were
56 and 63 tokens in with 2 and 3 tokens out (one word), the writer calls 270 and 278 in (they carry Setu's system
message).

The classifier alone answered `REFUND`, already a Java enum (chapter 15's structured output). In the workflow, each
message took two model calls: the writer received the topic from the scope and named the right team.

Read the replies like a passenger, though. "The REFUND team", in capitals, is the enum's name leaking into the
text, because the prompt passes `{{topic}}` as it is. That is the kind of detail splitting makes easy to fix: change
one line of the writer's prompt (for example "say the team's name in lower case"), and run the writer alone to test
it, without touching the classifier.
:::

:::step{type=predict title="Guess first"}
:::question
You remove `.outputKey("topic")` from the classifier. What happens when the workflow runs?
:::
- [ ] The writer guesses the topic
- [x] The writer cannot find `topic` in the scope, and the workflow fails
- [ ] Nothing changes
:::explain
Agents only meet through the scope. A value nobody writes is a value nobody can read. We tried it: `Missing argument:
topic`.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
In this chapter's workflow, who decides that the classifier runs before the writer?
:::
- [x] Your code: the order of `subAgents(...)`
- [ ] The model
- [ ] The classifier
:::explain
In a workflow the steps are fixed by code. Chapter 29 shows the other kind, where a model decides.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does the `@Agent` description do?
:::
- [ ] It is sent as the system message
- [x] It tells other parts of the system, and planning models, what the agent does
- [ ] Nothing at run time
:::explain
In a workflow it documents the agent; in chapter 29 a supervisor model reads it to choose which agent to call.
:::
:::

:::step{type=deep-dive title="Go deeper: agents and their scope"}
**Reading the scope.** `invokeWithAgenticScope(...)` on an untyped agent (`UntypedAgent`, which takes a `Map` of
arguments) returns the result and the whole scope, so
a test can check every intermediate value (`scope.readState("topic")`).

**Non-AI agents.** A step does not have to call a model. Plain Java methods can be agents too
(`AgenticServices.agentAction(...)` or an `@Agent` method on a class), for example to look up a booking in a database
between two model steps.

**Declarative style.** The module also lets you describe whole workflows with annotations such as
`@SequenceAgent(subAgents = {...})`, if you prefer configuration to builder code.

**Memory.** An agent can have chat memory like any AI Service, with a `@MemoryId` argument, so a multi-turn
conversation keeps its context across runs.
:::

:::step{type=recap}
You can now:

- explain the difference between a workflow and an agent, and when to prefer each;
- build an agent with `AgenticServices.agentBuilder(...)`, a description and an output key;
- pass values between agents through the agentic scope;
- join agents in a sequence with `sequenceBuilder(...)`.

Next, chapter 28: more workflows. Loops that improve an answer, conditions that route a message, and agents that run
in parallel.

:::photo{src="/lesson-images/langchain4j/l4j-27-notes.webp" alt="Handwritten notes titled Agents, small AI Services joined by a shared scope: an agent is an AI Service with a description and an output key, and agents pass work through the scope, a map of named values for one run; message, classifier writes topic, writer reads message and topic, writer writes reply, workflow returns reply; classifier 56 tokens in and 2 out; writer 270 in and 24 out; no output key or writer first gives Missing argument topic; in a sequence, code decides the order" ai="true"}
One page of notes for this chapter.
:::
:::
