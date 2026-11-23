:::step{type=story title="Middleware the co-op writes itself"}
The built-in middleware covered the common problems. Two of the co-op's needs are its own:

- Ravi prefers Marathi, Asha English. Navin should know who it is talking to and answer in their language, without a
  separate agent for each member.
- The co-op's auditor wants a record of every tool Navin runs, for whom, with which arguments. Rates and bookings
  touch money; "the AI did it" is not an answer an auditor accepts.

Both are a few lines of **your own middleware**, written as decorated functions: `@dynamic_prompt` builds the system
prompt before each model call, and `@wrap_tool_call` wraps every tool call.

:::mission
Write a dynamic prompt made for each member, and an audit hook that records every tool call before it runs.
:::
:::

:::step{type=history title="Cross-cutting concerns"}
:::before{title="The same lines in every function"}
Logging, permission checks and timing were once copied into every function that needed them, and forgotten in some.
:::

In **1997** Gregor Kiczales and colleagues at Xerox PARC named the problem: **cross-cutting concerns**, needs that cut
across a whole program, and proposed **aspect-oriented programming** to write each one once and apply it around many
functions. Python's **decorators** (Python 2.4, 2004) gave a light version of the idea: `@something` above a function
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
for that call. It receives the request, and through `request.runtime.context` the context the app passed in (chapter 12):

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
Finish `member_prompt(request)`: return `SYSTEM` followed by `f" You are talking to {member.name}. Answer in
{member.language}."`

Press **Check**.
:::

:::step{type=concept title="Wrapping every tool call" file="23-custom-middleware/agent.py" line="29-35"}
`@wrap_tool_call` turns a function into middleware that runs **around** each tool call. It gets the request and a
`handler`; calling `handler(request)` runs the tool (and any inner middleware), and you return its result:

```python
@wrap_tool_call
def audit_tools(request, handler):
    AUDIT.append(...)            # before: who, which tool, which arguments
    return handler(request)      # run it, and pass the result on
```

Because you control the call, the same shape can time a tool, block it for some members, retry it, or change its
result. Forgetting `return handler(request)` means the tool never runs: the wrapper is the gate.
:::

:::step{type=task task=audit_tools title="Your turn: the audit log" file="23-custom-middleware/agent.py" line="29-35"}
Finish `audit_tools(request, handler)`: append `f"{member id} {tool name} {args}"` to `AUDIT` (the member id is
`request.runtime.context.member_id`; the name and args are in `request.tool_call`), then return `handler(request)`.

```bash run
cd /workspace/23-custom-middleware && python main.py
```

Press **Check**.
:::

:::step{type=try title="Marathi for Ravi, English for Asha, and an audit log"}
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
A wrap hook holds the call in its hands. That is what makes it useful for blocking, and dangerous when forgotten.
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

**Order matters.** Middleware runs in list order before a call and in reverse order after it. Put guards first, so a
refused message never reaches the logging or the model.
:::

:::step{type=recap}
You can now:

- build a system prompt per call with `@dynamic_prompt` and the runtime context;
- wrap every tool call with `@wrap_tool_call`, and know that `handler` is the gate;
- serve every member from one agent, in their own language;
- keep an audit of every tool call, outside the tools.

Next, chapter 24: guardrails. Aadhaar numbers that never reach the model, and messages that are refused before they cost
anything.

:::photo{src="/lesson-images/langchain/lc-23-notes.webp" alt="Handwritten notes about custom middleware: dynamic_prompt: before each call; Ravi in Marathi, Asha in English; wrap_tool_call: around each tool; handler(request) is the gate; Audit: who, what, when" ai="true"}
One page of notes for this chapter.
:::
:::
