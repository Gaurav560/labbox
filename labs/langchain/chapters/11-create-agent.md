:::step{type=story title="The same loop, without writing it"}
Your `agent_loop` from chapter 10 works. In a real application it would also need streaming, memory between messages,
a way to pause for a person's approval, retries when the model is busy, and limits on how many times each tool can
run. Writing all that well is a lot of work, and every team would write it differently.

LangChain's `create_agent` is that loop, finished: one function that takes a model, tools and instructions, and
returns an agent you `invoke`. Underneath it is a small **LangGraph** graph with two steps, `model` and `tools`, and
everything later in this course (memory, streaming, middleware, human approval) plugs into it.

:::mission
Build Navin as an agent with `create_agent`, then read a finished run to list the tools it used.
:::
:::

:::step{type=concept title="create_agent" file="11-create-agent/agent.py" line="9-12"}
```python
from langchain.agents import create_agent

agent = create_agent("openai:ai-chat",                     # a model, by name or as an object
                     tools=[mandi_price, storage_cost],     # the tools it may call
                     system_prompt=SYSTEM)                  # Navin's instructions
result = agent.invoke({"messages": [{"role": "user", "content": "What does 25 crates for a week cost?"}]})
result["messages"][-1].content                               # the answer
```

The input and the output are the same shape, a **state** with a list of `messages`. The result holds every message of
the run, exactly like the list your `agent_loop` grew: the question, the model's tool calls, the tool results, the
answer.

| Chapter 10 (by hand) | Chapter 11 (`create_agent`) |
|---|---|
| `model.bind_tools(tools)` | done for you |
| your loop, `max_steps` | the graph loops between `model` and `tools`, up to a recursion limit you should set |
| exceptions turned into error messages | **not** by default: a tool's exception stops the run (chapter 22 fixes that) |
| no streaming, no memory | `stream`, `checkpointer` and middleware, one argument each |
:::

:::step{type=history title="Agents, from experiments to a library function"}
:::before{title="Every framework its own agent"}
In 2023 "agent" frameworks multiplied: AutoGPT, BabyAGI, LangChain's own `AgentExecutor` with a dozen agent types.
Each parsed the model's text in its own way, and many broke when models changed.
:::

When models gained reliable **tool calling** (chapter 10's history), the loop became simple and standard: call the
model, run the tools it asks for, repeat. In **2024** LangChain built **LangGraph** to run such loops as graphs with
saved state, and in **October 2025** LangChain 1.0 made `create_agent` the one way to build an agent, replacing the
old agent types. You will build the same kind of graph yourself in the LangGraph course.

:::solved
**One agent, many add-ons.** A standard loop that memory, streaming, approvals and guardrails can attach to.
:::

:::timeline
- **2023** Many agent frameworks; LangChain's AgentExecutor.
- **2024** LangGraph: agents as graphs with state.
- **2025** LangChain 1.0: `create_agent`.
:::
:::

:::step{type=task task=first_agent title="Your turn: Navin as an agent" file="11-create-agent/agent.py" line="9-12"}
Finish `navin_agent()`: return `create_agent("openai:ai-chat", tools=[mandi_price, storage_cost], system_prompt=SYSTEM)`.

Press **Check**.
:::

:::step{type=concept title="Reading a run" file="11-create-agent/agent.py" line="15-19"}
A finished run is a list of messages, and each kind says something:

| Message | Means |
|---|---|
| `HumanMessage` | the member's question |
| `AIMessage` with `tool_calls` | the model asked for tools (no text) |
| `ToolMessage` | one tool's result, with the `tool_call_id` it answers |
| `AIMessage` without `tool_calls` | the answer |

Listing the tools a run used is useful far beyond this chapter: for logs, for tests ("did it look up the rate, or
guess?"), and for cost (every tool round is another model call).
:::

:::step{type=task task=tools_used title="Your turn: which tools did it use?" file="11-create-agent/agent.py" line="15-19"}
Finish `tools_used(result)`: go through `result["messages"]` and collect the `name` of every call in each message's
`tool_calls` (only AI messages have them; use `getattr(m, "tool_calls", None) or []`), in order.

```bash run
cd /workspace/11-create-agent && python main.py
```

Press **Check**.
:::

:::step{type=try title="One tool, and none"}
```text
$ python main.py
> What does it cost to keep 25 crates of tomatoes for a week?
It costs ₹350 to keep 25 crates of tomatoes for a week.
  tools: ['storage_cost'], 4 messages

> What is the garlic rate today?
I'm sorry, but I can only provide rates for onions, tomatoes, and grapes. Would you like to know the rate for one of those crops?
  tools: [], 2 messages
```

The first question: four messages (question, tool call, tool result, answer), one tool, and ₹350, which is 25 × 7 × 2.
The model turned "a week" into `days=7` by itself.

The second is more interesting: **no tool at all**. The model read `mandi_price`'s description, "crop is onion, tomato
or grapes", and concluded garlic is not covered, without calling it. A good tool description shapes the model's
decisions even when the tool is never run. (Had it called the tool, your chapter 10 error message would have told it
the same thing.)

Careful, though. Had the model called `mandi_price("garlic")`, the tool would have raised `ValueError: The co-op has no
rate for garlic` and, unlike your chapter 10 loop, `create_agent` does **not** turn that into a message by default: we
tried it, and the whole run stopped with that exception. Your chapter 10 loop was kinder. Chapter 22 adds middleware that
turns tool errors into messages the model can read.
:::

:::step{type=predict title="Guess first"}
:::question
A member asks "Hello!". How many messages will the result hold?
:::
- [x] Two: the question and the answer, no tools
- [ ] Four
- [ ] One
:::explain
An agent only calls tools when the model decides it needs them. A greeting needs none.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `agent.invoke` return?
:::
- [ ] The answer text
- [x] The final state: a dict whose `messages` list holds the whole run
- [ ] Only the tool results
:::explain
The last message is the answer; the ones before it are the story of how the agent got there.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did the garlic question need no tool call?
:::
- [ ] Garlic is a tool error
- [x] The tool's description said which crops it covers, and the model decided from that
- [ ] The model knows garlic prices
:::explain
Descriptions are instructions too. Chapter 12 is about writing them well.
:::
:::

:::step{type=deep-dive title="Go deeper: what create_agent builds"}
**A graph.** `agent.get_graph().draw_mermaid()` prints the graph: a `model` node, a `tools` node, and edges that loop
until the model answers without tool calls.

**Recursion limit.** Instead of `max_steps`, LangGraph counts steps (each model call and each tool round) and stops at
`recursion_limit`. In this version the default is **10,007**, effectively no limit, so pass your own:
`agent.invoke(state, {"recursion_limit": 10})`. Chapter 22 adds limits per model call and per tool, too.

**Models as objects.** Instead of a string you can pass a configured model, `create_agent(init_chat_model(...,
temperature=0), ...)`, to set its parameters.
:::

:::step{type=recap}
You can now:

- build an agent with `create_agent`: model, tools, system prompt;
- invoke it with a state of messages and read the answer;
- read a run's messages and list the tools it used;
- see how a tool's description steers the model even without a call.

Next, chapter 12: writing tools well, and tools that know which member is asking.

:::photo{src="/lesson-images/langchain/lc-11-notes.webp" alt="Handwritten notes about create_agent: create_agent: model, tools, prompt; The run is a list of messages; Garlic: no tool needed; Tool errors stop the run; Set your own recursion limit" ai="true"}
One page of notes for this chapter.
:::
:::
