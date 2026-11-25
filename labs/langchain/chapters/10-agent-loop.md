:::step{type=story title="A model that can ask for help"}
Chapter 9 made Navin honest by pasting facts into the prompt. But some answers are not facts to paste: "what does it
cost to store 60 crates for 10 days?" needs **arithmetic**, and a model can get arithmetic wrong: it predicts likely digits instead of calculating
(chapter 4). For sums the co-op charges money for, the answer must come from code. "What is the onion rate?" needs today's **live** number from the co-op's system, which changes every morning.

The fix is to let the model **ask your code**. You describe a few Python functions to the model; described this way they are called **tools**. When it
needs one, instead of answering, it replies "please call `storage_cost` with crates=60 and days=10". Your code runs the
function and sends back the result; the model then writes the answer. A model plus that loop is an **agent**.

In this chapter you build the loop by hand, with no agent library, so that nothing about agents is magic afterwards.


Engineers did not multiply in their heads for centuries: they reached for a tool, such as this slide rule. Tools give Navin the same habit: exact numbers from code, not likely-looking digits.

:::photo{src="/lesson-images/langchain/slide-rule.webp" alt="An old wooden slide rule with printed scales, lying on a flat surface" credit="Encik Tekateki" license="CC0" source="https://commons.wikimedia.org/wiki/File%3ASlide_Rule_Found_in_Perak%2C_Malaysia.jpg"}
A slide rule found in Perak, Malaysia.
:::
:::mission
Run one tool call and wrap its result for the model, then write the agent loop: call, run tools, send results, repeat
until the model answers.
:::
:::

:::step{type=concept title="Tools are descriptions the model can ask for" file="10-agent-loop/coop_tools.py" line="1-19"}
`coop_tools.py` has the co-op's two tools, plain Python functions with `@tool`:

```python
@tool
def storage_cost(crates: int, days: int) -> int:
    """The cold storage charge in rupees for some crates kept some days (Rs 2 per crate per day)."""
    return crates * days * 2
```

The model never sees the code. It sees a **description**, built from the function's name, its **docstring** (the text
in triple quotes under the `def`) and its **type hints** (`int`, `str`), written as a **JSON schema** (a standard
way to describe what shape some JSON must have). This is the real description of `storage_cost`:

```json
{"name": "storage_cost",
 "description": "The cold storage charge in rupees for some crates kept some days (Rs 2 per crate per day).",
 "parameters": {"properties": {"crates": {"type": "integer"}, "days": {"type": "integer"}}, "required": ["crates", "days"]}}
```

`model.bind_tools(tools)` sends those descriptions with every request. If the model decides it needs one, its reply
has no text but a list of **tool calls**: `[{"name": "storage_cost", "args": {"crates": 60, "days": 10}, "id": "call_..."}]`.
:::

:::step{type=history title="From Toolformer to function calling"}
:::before{title="Models that could only talk"}
Until 2023 a model could only produce text. To make it "use a calculator", applications asked it to write a special
phrase and searched the answer for it, which broke whenever the model phrased it differently.
:::

In **October 2022** the **ReAct** paper (Shunyu Yao and colleagues) showed models alternating reasoning and actions, and in
**February 2023** Meta's **Toolformer** taught a model to insert calls to calculators and search engines into its own
text. In **June 2023** OpenAI added **function calling** to its API: tools described as JSON schemas, and replies that
are structured tool calls instead of text to parse. The other major providers added the same idea, and LangChain's
`bind_tools` and `tool_calls` hide the small differences between them.

:::solved
**Facts and arithmetic in code, language in the model.** The model decides what it needs; Python computes it exactly.
:::

:::timeline
- **2022** ReAct: reason, act, observe.
- **2023** Toolformer (February), function calling in the OpenAI API (June).
- **2024** Tool calling in every major model API.
:::
:::

:::step{type=example title="Worked example: running a tool by hand" file="10-agent-loop/loop.py" line="5-10"}
A tool made with `@tool` is an object with `.invoke(args)`. Running one of the model's calls (only to read; your task
wraps it):

```python
call = {"name": "mandi_price", "args": {"crop": "onion"}, "id": "call_k0Ua..."}
tool = {"mandi_price": mandi_price}[call["name"]]
result = tool.invoke(call["args"])                       # 1850
ToolMessage(content=str(result), tool_call_id=call["id"])  # the reply to that call
```

The `tool_call_id` matters: the model may ask for several tools at once, and the id says which request each result
answers.
:::

:::step{type=task task=run_tool_call title="Your turn: run one tool call" file="10-agent-loop/loop.py" line="5-10"}
Finish `run_tool_call(call, tools_by_name)`:

1. Find the tool: `tools_by_name[call["name"]]`.
2. Run it inside `try`: `result = tool.invoke(call["args"])`.
3. Return `ToolMessage(content=str(result), tool_call_id=call["id"])`.
4. If the tool raises an exception, return a `ToolMessage` whose content is `"Error: "` plus the exception's text
   (`str(e)`), with the same `tool_call_id`: the model can read it and tell the member.

The usual slips:

- Forgetting `tool_call_id`: the model cannot tell which request the result answers, and the API rejects the next call.
- `content=result` without `str(...)`: a number is not text.

Press **Check**.
:::

:::step{type=concept title="The loop" file="10-agent-loop/loop.py" line="13-20"}
An agent run is a loop over one growing list of messages:

:::trace{title="What is the onion rate, and what does storing 60 crates for 10 days cost?"}
| Step | Who | Message added |
|---|---|---|
| 1 | you | SystemMessage, HumanMessage (the question) |
| 2 | model | AIMessage with two tool calls: mandi_price(onion), storage_cost(60, 10) |
| 3 | your code | ToolMessage "1850", ToolMessage "1200" |
| 4 | model | AIMessage with text and no tool calls: the answer. Stop. |
:::

:::diagram{name="lc-agent-loop"}
Chapter 10's real run as the growing list of messages: two model calls, and your code in between.
:::

Two rules keep it safe. The model may ask for several tools in one reply: run them all. And a model can keep asking
forever (a confused model, a tool that keeps failing): cap the loop with `max_steps`, because every turn is a paid
model call.
:::

:::step{type=task task=agent_loop title="Your turn: the agent loop" file="10-agent-loop/loop.py" line="13-20"}
Finish `agent_loop(model, messages, tools, max_steps)`. `model_with_tools` (already made for you) is the model with the
tool descriptions bound to it.

1. Repeat at most `max_steps` times: `reply = model_with_tools.invoke(messages)`, then `messages.append(reply)`.
2. If `reply.tool_calls` is empty, the model has answered: return `reply`.
3. Otherwise, for each call in `reply.tool_calls`, append `run_tool_call(call, tools_by_name)`.
4. If the loop ends without an answer, `raise RuntimeError("the agent did not finish in max_steps")`.

The usual slips:

- Not appending the model's reply before the tool results: the API needs the reply with the tool calls first, then
  one ToolMessage per call.
- Running only the first tool call when the model asked for two.

```bash run
cd /workspace/10-agent-loop && python main.py
```

Press **Check**.
:::

:::step{type=try title="Two tools in one turn"}
A real run (we ran it again on 25 November and got the same messages; only the call ids change every time):

```text
$ python main.py
SystemMessage  "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onion
HumanMessage   "What is today's onion rate, and what does it cost to store 60 crates for 10 days?"
AIMessage      [{'name': 'mandi_price', 'args': {'crop': 'onion'}, 'id': 'call_k0UaNrWIPa32piH7avq3Dxdw', 'type': 'tool_call'}, {'name': 'storage_cost', 'args': {'crates': 60, 'days': 10}, 'id': 'call_hf4jJj6wPdTxiqzNOypvOcdX', 'type': 'tool_call'}]
ToolMessage    '1850'
ToolMessage    '1200'
AIMessage      "Today's onion rate is ₹1850 per quintal. The cost to store 60 crates for 10 days is ₹1200."
```

The whole run, message by message. The model read the question, saw that it needed two numbers it must not guess, and
asked for **both tools at once**, with the right arguments pulled out of the English. Your code ran them: 1850 from the
co-op's rate table, 1200 from Python's arithmetic (60 × 10 × 2). One more model call turned two numbers into a sentence.

Two model calls for one answer. That is the price of an agent: more calls, but numbers that are right.
:::

:::step{type=predict title="Guess first"}
:::question
A member asks "What is the garlic rate?" and the model calls `mandi_price("garlic")`, which raises an error. With your
`run_tool_call`, what happens next?
:::
- [ ] The program crashes
- [x] The model receives "Error: The co-op has no rate for garlic..." and can tell the member
- [ ] The model receives 0
:::explain
An error message is just another tool result. The model reads it and explains, instead of the program crashing.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does the model see of `storage_cost`?
:::
- [ ] Its Python code
- [x] Its name, its docstring and its parameter types, as a JSON schema
- [ ] Nothing until it is called
:::explain
The description is all the model has to decide when to call a tool. Chapter 12 is about writing good ones.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why cap the loop with `max_steps`?
:::
- [x] A model that keeps asking for tools would otherwise loop, and every turn is a paid model call
- [ ] The API allows only five calls
- [ ] Tools can only run five times
:::explain
A ceiling on steps is a ceiling on cost and time.
:::
:::

:::step{type=deep-dive title="Go deeper: tools in practice"}
**Parallel calls.** Asking for two tools in one reply saves a round trip. Your loop runs them one after the other;
agents in production can run them at the same time.

**Errors as messages.** Turning exceptions into tool results is a deliberate choice: the model can retry with better
arguments, or explain. LangChain's `create_agent` does not do this by default (chapter 11 shows what happens instead);
middleware in chapter 22 adds it.

**Never trust arguments.** The model chooses the arguments. A tool that changes data (a booking, a payment) must
check them like any user input.
:::

:::step{type=recap}
You can now:

- describe a tool as the model sees it: name, description, parameter schema;
- run a tool call and answer it with a `ToolMessage` and the call's id;
- write the agent loop, with a step limit;
- read a run as a list of messages.

Next, chapter 11: `create_agent`, the same loop built by LangChain.

:::photo{src="/lesson-images/langchain/lc-10-notes.webp" alt="Handwritten notes about the agent loop: A tool is a Python function the model can ask you to run. The model sees only its name, docstring and parameter types. A reply with tool calls has no answer yet: run the tools. Each ToolMessage carries the id of the call it answers. Repeat until a reply has no tool calls, at most max_steps times. Our question needed two model calls and two tools." ai="true"}
One page of notes for this chapter.
:::
:::
