:::step{type=story title="Questions the wording cannot answer"}
Sunil, the senior adjuster, tries Claimdesk's lookup on Thursday and asks: "Is policy DS-POL-40185 in force on 4 October,
and what is its deductible?"

The wording cannot answer that. Each policy has its own dates and its own deductible, and they live in Deccan Shield's
database, which changes every day. The model has never seen that database, and must not guess it.

What the model **can** do is decide that it needs to look the policy up, and say which policy. Your code then does the
looking up, and gives the result back. This is a **tool**: a function your program offers to the model, described in
words, which the model may ask you to run.

In this chapter Claimdesk gets its first tool, `get_policy`, and the loop that runs it. At the end you will see the real
model make a mistake that teaches the most important rule about tools.

:::mission
Describe a tool the model can ask for, run it safely when asked, and write the loop that goes back and forth until the
model answers, with a limit.
:::
:::

:::step{type=concept title="How a tool call works" file="11-tools/agent.py" line="29-32"}
The model never runs anything. The conversation goes like this:

1. Your code sends the question **and a description of the tools** (`tools=TOOLS`).
2. The model answers, not with text, but with a **tool call**: "call `get_policy` with `{"policy_no": "DS-POL-40185"}`".
3. Your code runs `get_policy` itself, in your process, with your database access.
4. Your code sends the conversation back, now with a **tool message** holding the result.
5. The model writes the answer, using the result.

So you stay in control: the model can only **ask** for what you described, and you decide what actually happens.

:::diagram{name="fde-tool-loop"}
The loop with this chapter's real question and the real model's answer, including its mistake.
:::

A tool description has three parts, all read by the model:

| Part | Example | Good practice |
|---|---|---|
| `name` | `get_policy` | a clear verb and noun |
| `description` | "Looks up one Deccan Shield motor policy by its number (like DS-POL-40185). Returns ..." | what it returns, in which units, and the input's format |
| `parameters` | a JSON schema: one string, `policy_no`, required | as narrow as possible |

The description is a **prompt** for the model: a vague one ("gets data") makes the model call the tool at the wrong
time, or with the wrong argument.
:::

:::step{type=example title="Worked example: one tool, by hand"}
This is only to read; it is not in your project. A tool for a library:

```python
TOOLS = [{
    "type": "function",
    "function": {
        "name": "find_book",
        "description": "Finds a book by its id (like BK-0042). "
                       "Returns title, shelf and whether it is on loan.",
        "parameters": {
            "type": "object",
            "properties": {"book_id": {"type": "string"}},
            "required": ["book_id"],
        },
    },
}]

def run_tool(name, arguments):
    if name != "find_book":
        return json.dumps({"error": f"unknown tool {name}"})
    args = json.loads(arguments)
    book = BOOKS.get(args["book_id"])
    return json.dumps(book or {"error": "no such book"})
```

- `"type": "function"` and the `function` object are the shape the chat API expects.
- `parameters` is a JSON schema, like chapter 9's: here one required string.
- The model sends the arguments as **JSON text**, so `json.loads(arguments)` turns them into a dict.
- The result goes back as JSON text too. For a missing book it returns `{"error": ...}`, never `null`: the model must be
  told clearly that the thing does not exist, or it may invent it.
- An unknown tool name returns an error and runs **nothing**. Never let a name the model sends pick arbitrary code.
:::

:::step{type=predict title="Guess first"}
:::question
The model is offered `get_policy` and asked "Who holds policy DS-POL-99999?". The policy does not exist. What should
`run_tool` send back?
:::
- [ ] Nothing, so the model stays quiet
- [x] {"error": "no policy DS-POL-99999"}, so the model can tell the adjuster it does not exist
- [ ] null
:::explain
Silence or null leaves the model guessing. A clear error lets it answer correctly: "there is no such policy, please check
the number".
:::
:::

:::step{type=try title="No tools yet"}
```text
$ python agent.py
Q: Is policy DS-POL-40185 in force on 4 October 2026, and what is its deductible?
   tool calls: []
   answer: 
Q: Who holds policy DS-POL-99999?
   tool calls: []
   answer: 
```

No tool, no loop, no answer.
:::

:::step{type=task task=policy_tool title="Your turn: the get_policy tool"}
In `agent.py`:

1. Fill `TOOLS` with one tool: `"name": "get_policy"`, a description that says what it returns (holder, registration, vehicle,
   start and end dates, sum insured and deductible in rupees) and the format of a policy number (`DS-POL-12345`), and
   `parameters` with one required string property `policy_no`.
2. In `run_tool`: for `"get_policy"`, `json.loads` the arguments, call `get_policy(args["policy_no"])`, and return the
   policy as JSON, or `{"error": "no policy ..."}` when it is `None`. For any other name, return an `{"error": ...}`.

Press **Check**.
:::

:::step{type=history title="From reasoning to acting"}
:::before{title="Before: models that could only talk"}
Early chat models could only produce text. To use a calculator or a database, developers parsed the text for commands,
which broke as soon as the model phrased things differently.
:::

In October 2022, Shunyu Yao and colleagues published **ReAct**, short for "reasoning and acting": a model alternates
between thinking and calling tools, reading each result before the next step. In June 2023 OpenAI added **function
calling** to its API: tools described as JSON schemas, and tool calls returned as structured data, not text to parse.

The safety principle behind giving a program only the tools it needs is much older. In 1975 Jerome Saltzer and Michael
Schroeder listed the **principle of least privilege**: every program should have only the access it needs for its job.
`get_policy` reads one policy; it cannot pay a claim or change an address.

:::solved
Models ask for actions in a structured form; programs decide what actually runs, with as little power as the job needs.
:::

:::timeline
- **1975** Saltzer and Schroeder describe least privilege.
- **October 2022** The ReAct paper.
- **June 2023** Function calling in the OpenAI API.
- **Today** Agents are mostly loops of model calls and tool calls, with limits.
:::

:::funfact
The word "agent" for a program acting on someone's behalf is decades older than language models; it was common in AI
research in the 1990s.
:::
:::

:::step{type=concept title="The loop, and why it needs a limit" file="11-tools/agent.py" line="43-51"}
One tool call is one round trip. A question may need several: look up a policy, then another. So the code runs a
**loop**:

```text
send messages -> tool calls?  yes -> run them, append results, send again
                              no  -> that is the answer
```

The messages list grows each turn. After the model asks for a tool, you append two kinds of message:

1. the model's own message (`messages.append(message)`), which holds its tool calls;
2. one **tool message** per call: `{"role": "tool", "tool_call_id": call.id, "content": ...}`. The `tool_call_id` links
   each result to the call it answers, because the model may ask for several at once.

Then call the model again with the longer list.

Why `max_turns`? A model can keep asking for tools (the same lookup again, or one after another) and never answer. Each
turn is a paid call and a few seconds. Without a limit, one confused question becomes a loop that spends money until
something times out. After `max_turns` calls without an answer, stop and say so plainly. An honest "I stopped" is a
result; an endless loop is an incident.

`calls` records every tool call as `(name, arguments)`, in order. That list is how you will debug (and later evaluate)
what the model actually did.
:::

:::step{type=task task=tool_loop title="Your turn: the agent loop"}
In `run_agent`:

1. Start `messages` with `SYSTEM` and the question; `calls = []`.
2. Loop at most `max_turns` times. Call the model with `model=MODEL`, `temperature=0`, `messages`, `tools=TOOLS`, and take
   `choices[0].message`.
3. No `tool_calls`: return `(message.content, calls)`.
4. Otherwise append the message, then for each call record `(call.function.name, call.function.arguments)` and append
   its tool message with `run_tool(...)`.
5. After the loop, return `(f"Stopped after {max_turns} model calls without an answer.", calls)`.

The check includes a model that asks for tools forever. Press **Check**.
:::

:::step{type=try title="It looked it up. Then it got it wrong."}
Through the gateway, with the real model:

```text
$ python agent.py
Q: Is policy DS-POL-40185 in force on 4 October 2026, and what is its deductible?
   tool calls: [('get_policy', '{"policy_no":"DS-POL-40185"}')]
   answer: Policy DS-POL-40185 is not in force on 4 October 2026, as it starts on 1 April 2026 and ends on 31 March 2027. The deductible for this policy is ₹2000.
Q: Who holds policy DS-POL-99999?
   tool calls: [('get_policy', '{"policy_no":"DS-POL-99999"}')]
   answer: There is no policy with the number DS-POL-99999. Please check the policy number and try again.
```

The tool part worked perfectly. The model asked for the right policy, the deductible (Rs 2,000) is correct, and the unknown
policy got an honest answer because the tool returned a clear error.

Now read the first answer again. "**Not** in force on 4 October 2026, as it starts on 1 April 2026 and ends on 31 March
2027." 4 October 2026 is **between** those dates. The model had the right data in front of it and still drew the wrong
conclusion. If Claimdesk had used this sentence to refer the claim, a covered customer would have been told they were not
covered.

This is the most important rule about tools: **let the model decide what to look up; let code decide anything exact.**
Comparing dates, adding amounts, checking limits: those are code's job, every time, because code is right every time. In
the next chapter, "is it in force?" becomes a tool of its own that computes the answer, and the model only reports it.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does each tool message carry the `tool_call_id`?
:::
- [ ] The gateway needs it for billing
- [x] The model can ask for several tools at once; the id links each result to the call it answers
- [ ] It makes the result secret
:::explain
With two lookups in one turn, ids keep the results from being mixed up.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The model is given a policy's start and end dates and asked whether a date falls between them. Who should decide?
:::
- [ ] The model, since it has the data
- [x] Code: compare the dates exactly, and let the model report the result
- [ ] The adjuster, every time
:::explain
The real run above shows a model getting it wrong with the data in front of it. Exact checks belong in code.
:::
:::

:::step{type=deep-dive title="Go deeper: tools in production"}
**Validate arguments.** The schema asks for a string; the model may still send `"40185"` without `DS-POL-`. Check and
normalise arguments in `run_tool`, and return a helpful error.

**Read and write tools.** Reading a policy is safe; paying a claim is not. Write tools need human approval (chapter 19),
idempotency keys (so a retried call does not pay twice), and their own audit log.

**Parallel calls.** Models can request several tools in one turn. Run independent ones together to save time.

**Frameworks.** LangChain, LangGraph, the OpenAI Agents SDK and others wrap this loop. Knowing the loop underneath, as you
now do, is what lets you debug them.
:::

:::step{type=recap}
You can now:

- describe a tool with a name, a precise description and a narrow schema;
- run tool calls safely: known names only, clear errors instead of null;
- write the agent loop with tool messages linked by id, and stop it after a limit;
- explain why exact decisions (dates, amounts, limits) belong in code, from a real mistake.

Next, chapter 12: Deccan Shield's own AI assistant wants Claimdesk's tools too. Offer them once, through a standard
protocol, with "in force" computed in code.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-11-notes.webp" alt="Handwritten notes about tools and the agent loop: A tool is a function the model may ask for. Your code runs it, never the model. Send a clear error, never null. Link each result to its call by id. Stop the loop after a few turns. Let code decide exact things like dates." ai="true"}
One page of notes for this chapter.
:::
:::
