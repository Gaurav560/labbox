:::step{type=story title="Look it up, do not make it up"}
In chapter 7 Harsh told a citizen "a crew is still working" when no crew existed: the model had the conversation and
nothing else. The board's ticket system knows the truth: which tickets a phone number has, who has each one, and when
they visit. Harsh should **look things up** before answering.

But which lookups, and how many, depends on the question. "Any update?" needs the citizen's tickets, then the status of
each. "Is the brown water safe?" may need none. The model should decide, call a tool, read the result, and decide again,
until it can answer. That loop, a model choosing tools until it is done, is what people call an **agent**.

In the LangChain course `create_agent` built that loop for you. Here you build it yourself, as a graph of two nodes.
After this chapter, `create_agent` holds no secrets.

:::mission
Give the model the ticket tools, then route its tool requests to a tool node and back, until it answers.
:::
:::

:::step{type=history title="Reason, act, observe"}
:::before{title="Models that only talked"}
A language model on its own can only write text. It cannot look up a ticket, and it does not know when it should.
:::

In **October 2022** the paper **"ReAct: Synergizing Reasoning and Acting in Language Models"** (Yao and others) showed a
model alternating between thinking, acting (calling a tool) and reading the result, until it could answer. In
**June 2023** OpenAI added **function calling** to its API, so a model could ask for a tool in a fixed format instead of
free text. LangGraph's `create_react_agent` (**2024**) and LangChain 1.0's `create_agent` (**October 2025**) package that
loop, and both are LangGraph graphs underneath: a model node, a tool node, and one conditional edge.

:::solved
**Answers from data.** The model decides what to look up; your tools decide what is true.
:::

:::timeline
- **2022** ReAct: reason, act, observe.
- **2023** Function calling in the API.
- **2024** `create_react_agent` in LangGraph.
- **2025** `create_agent` in LangChain 1.0.
:::

The loop is older than language models. Shakey, built at the Stanford Research Institute from 1966 to 1972, was the first mobile robot to plan its own actions: look with its camera, decide on a step, take it, and look again.

:::photo{src="/lesson-images/langgraph/shakey.webp" alt="A tall boxy robot with a camera head on a wheeled metal base, in a museum glass case, with a black and white photo of its builder behind it" credit="The wub" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:SRI_Shakey_robot,_1969,_Computer_History_Museum.jpg"}
Shakey the robot (SRI, 1969) at the Computer History Museum.
:::
:::

:::step{type=concept title="The model node" file="13-agent-graph/agent.py" line="20-25"}
Tools are plain functions with the `@tool` decorator (`tickets.py`): their names, arguments and docstrings tell the model
what they do. `bind_tools` hands those descriptions to the model on every call:

```python
def agent(state: MessagesState) -> dict:
    response = model().bind_tools(TOOLS).invoke([SystemMessage(SYSTEM)] + state["messages"])
    return {"messages": [response]}
```

The model's answer is an `AIMessage`. Either it has text (an answer for the citizen), or it has `tool_calls`: a list of
requests like `{"name": "find_tickets", "args": {"phone": "98220"}, "id": "call_1"}`. The model never runs anything
itself.
:::

:::step{type=task task=agent_node title="Your turn: give the model its tools" file="13-agent-graph/agent.py" line="20-25"}
In `agent`, call `model().bind_tools(TOOLS).invoke(...)` instead of `model().invoke(...)`.

Press **Check**.
:::

:::step{type=concept title="The loop: two nodes and one edge" file="13-agent-graph/agent.py" line="28-42"}
`ToolNode(TOOLS)` is a prebuilt node: it reads the tool calls in the last message, runs each tool, and returns one
`ToolMessage` per call (several calls run in parallel). The rest is the graph:

```python
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, ["tools", END])   # tools asked for? run them : stop
graph.add_edge("tools", "agent")                                         # results go back to the model
```

`should_continue` is the only decision: if the last message has `tool_calls`, go to `"tools"`; otherwise the model has
answered, and the run ends. LangGraph also ships this function as `tools_condition`.

:::diagram{name="lg-agent-loop"}
The model and the tools take turns; the loop ends when the model answers without asking for a tool.
:::
:::

:::step{type=task task=tool_loop title="Your turn: loop through the tools" file="13-agent-graph/agent.py" line="28-32"}
Finish `should_continue(state)`: return `"tools"` if `state["messages"][-1].tool_calls` is not empty; otherwise `END`.

```bash run
cd /workspace/13-agent-graph && python main.py
```

Press **Check**.
:::

:::step{type=try title="Three messages, two tool calls in one step, and advice from nowhere"}
```text
$ python main.py
> Any update on my complaints?
  [agent] Please provide your phone number so I can check the status of your complaints.
> 98220
  [agent] asks for find_tickets({'phone': '98220'})
  [tools] find_tickets -> T-4471: no_water at Tilak Nagar, lane 3, opened Monday 9:10 | T-4475: dirty_water at Tilak Nagar, lane 3, opened Tuesday 21:40
  [agent] asks for ticket_status({'ticket_id': 'T-4471'}), ticket_status({'ticket_id': 'T-4475'})
  [tools] ticket_status -> T-4471: crew assigned; East zone crew 2; Wednesday 8:00 to 11:00
  [tools] ticket_status -> T-4475: water sample taken; health team; lab result by Wednesday 18:00
  [agent] You have two open complaints: 

1. **No Water** (T-4471) at Tilak Nagar, lane 3 - Crew assigned, expected visit on Wednesday between 8:00 to 11:00.
2. **Dirty Water** (T-4475) at the same location - Water sample taken, lab results expected by Wednesday at 18:00.
> Is the brown water safe to drink until the result comes?
  [agent] I recommend not drinking the brown water until the lab results are available. It's best to wait for confirmation from the health team regarding its safety.
```

Follow the loop. With no phone number, the model asked for one instead of guessing (the system prompt allows that). With
it, the model called `find_tickets`, read two ticket ids, then asked for **both** statuses in one message; `ToolNode`
ran them together, and the model answered with every fact from the tools. Compare chapter 7: "a crew is still working"
has become "East zone crew 2, Wednesday 8:00 to 11:00".

The last answer is sensible advice, and it came from nowhere: no tool says anything about safety. The model filled the
gap with what it thought was right. Here it happens to be right; the board's rule says the same. Chapter 15 gives Harsh
the rulebook, so advice comes from the board, not from the model's guess.
:::

:::step{type=predict title="Guess first"}
:::question
You forget the edge from `tools` back to `agent`. What happens after the first tool call?
:::
- [ ] The model answers anyway
- [x] The tool runs, and the run ends with a tool result as the last message: the citizen gets no answer
- [ ] LangGraph refuses to compile
:::explain
A node with no outgoing edge ends the run. The edge back is what makes it a loop.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Who runs `find_tickets`?
:::
- [ ] The model
- [x] `ToolNode`, in your process, after the model asked for it
- [ ] OpenAI's servers
:::explain
The model only writes a request. Your code decides whether and how to run it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is `create_agent` from the LangChain course, underneath?
:::
- [x] A LangGraph graph like this one: a model node, a tool node, a conditional edge
- [ ] A different kind of program
- [ ] One model call with all tools
:::explain
It adds middleware, structured output and more, around the same loop.
:::
:::

:::step{type=deep-dive title="Go deeper: agents by hand"}
**Why build it yourself?** Your own loop can add nodes anywhere: a check before the answer is sent (chapter 14), a
retrieval grader (chapter 15), an approval before a tool with side effects (chapter 10).

**Limits.** An agent can loop for ever if the model keeps asking for tools. LangGraph's recursion limit stops it
(`invoke(..., {"recursion_limit": 10})`); a counter in the state can stop it more gently.

**Tool errors.** `ToolNode` turns a tool's exception into a `ToolMessage` with the error text by default, so the model can
read it and try again.
:::

:::step{type=recap}
You can now:

- give a model tools with `bind_tools` and read its `tool_calls`;
- run tool calls with `ToolNode`;
- build the agent loop: a model node, a tool node, a conditional edge and an edge back;
- see that tools fix facts, and that advice still needs a source.

Next, chapter 14: reflection, a second look before the answer is sent.

:::photo{src="/lesson-images/langgraph/lg-13-notes.webp" alt="Handwritten notes about the agent loop: bind_tools: the model can ask; ToolNode runs the calls; tool_calls? -> tools : END; tools -> agent = the loop; facts from tools, not guesses" ai="true"}
One page of notes for this chapter.
:::
:::
