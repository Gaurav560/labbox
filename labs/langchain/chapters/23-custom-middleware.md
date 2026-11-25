:::step{type=story title="Middleware the co-op writes itself"}
The built-in middleware covered the common problems. Two of the co-op's needs are its own:

- Ravi prefers Marathi, Asha English. Navin should know who it is talking to and answer in their language, without a
  separate agent for each member.
- The co-op's auditor wants a record of every tool Navin runs, for whom, with which arguments. Rates and bookings
  touch money; "the AI did it" is not an answer an auditor accepts.

Both are a few lines of **your own middleware**, written as decorated functions. A **decorator** is the `@name` line
above a function: it hands the function to `name`, which returns a wrapped version. Here `@dynamic_prompt` builds the
system prompt before each model call, and `@wrap_tool_call` wraps every tool call.

:::mission
Write a dynamic prompt made for each member, and an audit hook that records every tool call before it runs.
:::
:::

:::step{type=history title="Cross-cutting concerns"}
:::before{title="The same lines in every function"}
Logging, permission checks and timing were once copied into every function that needed them, and forgotten in some.
:::

In **1997** Gregor Kiczales and colleagues at Xerox PARC described needs like these, which "cross-cut" a whole program
(today they are called **cross-cutting concerns**), and proposed **aspect-oriented programming** to write each one once
and apply it around many functions. Python's **decorators** (Python 2.4, 2004) gave a light version of the idea: `@something` above a function
wraps it with extra behaviour. LangChain's middleware decorators are the same idea for an agent: you write a function,
the decorator places it at the right point of every run.

:::solved
**Written once, applied everywhere.** The audit cannot be forgotten in one tool, because it is not in any tool.
:::

:::timeline
- **1997** Aspect-oriented programming at Xerox PARC.
- **2004** Decorators in Python 2.4.
- **2025** Middleware decorators for LangChain agents.
:::

The entrance of **Xerox PARC** in Palo Alto, where aspect-oriented programming was proposed in 1997, one of many ideas from the lab that shaped how software is built.

:::photo{src="/lesson-images/langchain/xerox-parc.webp" alt="The entrance of the Xerox PARC research centre: a low modern building among trees, with a sign at the front" credit="Coolcaesar at English Wikipedia" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File%3AParcentrance.jpg"}
The entrance to Xerox PARC in Palo Alto, California.
:::
:::

:::step{type=concept title="A prompt made for each call" file="23-custom-middleware/agent.py" line="13-26"}
`@dynamic_prompt` turns a function into middleware that runs **before every model call** and returns the system prompt
for that call. It receives the **request** (a `ModelRequest`: what is about to be sent to the model), and through
`request.runtime.context` the context the app passed in with `context=...` (chapter 12):

```python
@dynamic_prompt
def member_prompt(request: ModelRequest) -> str:
    member = request.runtime.context          # Member("M-104", "Ravi", "Marathi")
    return f"{SYSTEM} You are talking to {member.name}. Answer in {member.language}."
```

One agent now serves every member, each with their own instructions. The same hook can add today's date (chapter 13's
"next Monday"), the member's facts (chapter 27) or a shorter prompt for a cheaper model.
:::

:::step{type=task task=member_prompt title="Your turn: a prompt for each member" file="23-custom-middleware/agent.py" line="20-26"}
Finish `member_prompt(request)`. `member` is already read from the context; return `SYSTEM` followed by
`f" You are talking to {member.name}. Answer in {member.language}."`

The usual slips:

- Losing the space between the two sentences: the model then reads "...guess them yourself.You are talking to Ravi."
- Writing `Answer in Marathi.` by hand: Asha then gets Marathi too. Use `{member.language}`.

Press **Check**.
:::

:::step{type=concept title="Wrapping every tool call" file="23-custom-middleware/agent.py" line="29-35"}
`@wrap_tool_call` turns a function into middleware that runs **around** each tool call. It gets the request (a
`ToolCallRequest`; `request.tool_call` is a dict with the tool's `name`, `args` and `id`) and a `handler`. Calling
`handler(request)` runs the tool (and any middleware listed after this one), and you return its result:

```python
@wrap_tool_call
def audit_tools(request, handler):
    AUDIT.append(...)            # before: who, which tool, which arguments
    return handler(request)      # run it, and pass the result on
```

:::diagram{name="lc-wrap-tool"}
One real tool call from this chapter's run, with `audit_tools` around it.
:::

Because you control the call, the same shape can time a tool, retry it, change its result, or block it. To block, do
not call `handler`; return your own message instead:

```python
from langchain.messages import ToolMessage
...
return ToolMessage(content="Bookings are closed for this member.", tool_call_id=request.tool_call["id"])
```

We tried it: the tool did not run, and the model told the member "bookings are closed for you". What you must not do
is return nothing. In the lab's LangChain a wrapper that returns `None` (no `handler` call, or a `handler` call without
`return`) stops the whole run with `NotImplementedError: Unsupported message type: <class 'NoneType'>`. The wrapper is
the gate, and it must always hand something back.
:::

:::step{type=task task=audit_tools title="Your turn: the audit log" file="23-custom-middleware/agent.py" line="29-35"}
Finish `audit_tools(request, handler)`:

1. Append one line to `AUDIT`: the member id (`request.runtime.context.member_id`), the tool's name
   (`request.tool_call['name']`) and its args (`request.tool_call['args']`), separated by spaces.
2. Keep `return handler(request)` as the last line.

The usual slips:

- `request.tool_call.name`: `tool_call` is a dict, so it is `request.tool_call['name']`.
- Appending after `handler(request)`: the line is then written only if the tool succeeds. An audit should record the
  attempt, so write it first.

```bash run
cd /workspace/23-custom-middleware && python main.py
```

Press **Check**.
:::

:::step{type=try title="Marathi for Ravi, English for Asha, and an audit log"}
A real run (we ran it again on 25 November: the same numbers and the same audit lines; the Marathi sentence came out
in other words, once with the English word "crates" in it, which models often do in Marathi):

```text
$ python main.py
[Ravi, Marathi] 25 क्रेट्स 8 दिवसांसाठी ठेवण्याचा खर्च 400 रुपये आहे.

[Asha, English] Storing 25 crates for 8 days will cost you 400 rupees.

audit log:
   M-104 storage_cost {'crates': 25, 'days': 8}
   M-221 storage_cost {'crates': 25, 'days': 8}
```

The same question, the same agent, two members. Ravi's answer came in Marathi ("the cost of keeping 25 crates for 8
days is 400 rupees"), Asha's in English, and both numbers came from the tool, Rs 400 (25 × 8 × 2). The audit log has a
line for each tool call, with who asked, and no tool's code was touched to get it.
:::

:::step{type=predict title="Guess first"}
:::question
In `audit_tools` you append to `AUDIT` but forget `return handler(request)`. What happens?
:::
- [ ] The tool runs anyway
- [x] The tool never runs: the wrapper decides whether the call goes through
- [ ] The audit log stays empty
:::explain
A wrap hook decides whether the call goes through. Here it also returns nothing, so in the lab the run stops with
`NotImplementedError: Unsupported message type: <class 'NoneType'>`. To block on purpose, return a `ToolMessage`.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When does a `@dynamic_prompt` function run?
:::
- [ ] Once, when the agent is created
- [x] Before every model call
- [ ] Only when a tool fails
:::explain
That is why it can use who is asking, the time, or the facts saved so far.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why record the member id in the audit, and not only the tool?
:::
- [x] Rates and bookings touch money; the auditor needs to know who each call was for
- [ ] The tool needs it
- [ ] It makes the call faster
:::explain
An audit answers "who, what, when". The context carries the who, set by the app.
:::
:::

:::step{type=deep-dive title="Go deeper: writing middleware"}
**Classes for bigger middleware.** Subclass `AgentMiddleware` to combine several hooks with shared settings, as the
built-in middleware does.

**State.** Middleware can add its own fields to the agent's state, for example a counter that survives across the run.

**Order matters.** `before_*` hooks run in list order, `after_*` hooks in reverse order, and wrap hooks nest, the
first in the list outermost. We checked with two middleware, A then B: `before_model` ran A, B; `after_model` ran B,
A; and A's `wrap_tool_call` was around B's. Put guards first, so a refused message never reaches the logging or the
model.
:::

:::step{type=recap}
You can now:

- build a system prompt per call with `@dynamic_prompt` and the runtime context;
- wrap every tool call with `@wrap_tool_call`, and know that `handler` is the gate (and a wrapper must always return a
  message);
- serve every member from one agent, in their own language;
- keep an audit of every tool call, outside the tools.

Next, chapter 24: guardrails. Aadhaar numbers that never reach the model, and messages that are refused before they cost
anything.

:::photo{src="/lesson-images/langchain/lc-23-notes.webp" alt="Handwritten notes about custom middleware: A decorator wraps a function with extra behaviour. dynamic_prompt builds the system prompt before every model call. One agent answered Ravi in Marathi and Asha in English. wrap_tool_call runs around each tool call; handler(request) runs the tool. A wrapper that returns nothing stops the run. To block a call, return your own ToolMessage." ai="true"}
One page of notes for this chapter.
:::
:::
