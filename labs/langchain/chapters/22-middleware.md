:::step{type=story title="Ready for real members"}
Navin works. Before the whole co-op uses it, the volunteer who runs the server lists what worries them:

- A tool error (a crop the co-op does not trade) stops the whole run with a Python exception (chapter 11).
- A confused model could loop for a long time, calling tools and costing money (the recursion limit is 10,007, chapter 11).
- A member who chats all season makes every call longer and dearer, until the conversation no longer fits the context
  window (chapters 2 and 15).

Each worry could be fixed inside the agent loop, if you wrote the loop. With `create_agent` you do not change the loop:
you add **middleware**: small pieces of code that run at fixed points around every model call and every tool call
(each such point is a **hook**). LangChain
ships ready-made middleware for exactly these three problems.

:::mission
Let tool errors reach the model as messages (while internal errors stay private), stop runaway runs after five model
calls, and summarise long conversations automatically.
:::
:::

:::step{type=concept title="Where middleware runs"}
An agent run is a loop: before the agent, the model call, the tool calls, again, after the agent. Middleware hooks into
those points:

| Hook | Runs | Built-in example |
|---|---|---|
| `before_agent` | once, when a run starts | a guard that refuses a message (chapter 24) |
| `before_model` | before each model call | summarising old messages; counting model calls |
| `wrap_model_call` | around each model call | retries, a fallback model, a prompt made per member (chapter 23) |
| `wrap_tool_call` | around each tool call | turning tool errors into messages; retries; audit logs |
| `after_model`, `after_agent` | after each call, after the run | checking what the model wrote |

:::diagram{name="lc-middleware"}
The hooks of one run, and what chapter 22's middleware does at each.
:::

You pass a list, `create_agent(..., middleware=[a, b, c])`, and they run in that order. Nothing else in Navin changes.
:::

:::step{type=history title="Middleware, from web servers to agents"}
:::before{title="Every feature inside the application"}
Early web applications handled logging, sign-in checks and compression inside every page's code, copied again and again.
:::

In **2007** Ruby's **Rack** defined a simple way to stack small components around a web application, each one able to
look at a request before it reached the app and at the response after; Python's **WSGI** (2003) had allowed the same
pattern. Express, Django and almost every web framework since call these components **middleware**. When agents needed
the same thing (logging, limits, retries, safety checks around every step), LangChain 1.0 (**October 2025**) brought the
idea to `create_agent`.

:::solved
**Cross-cutting rules in one place.** A limit, a log or a check is written once and applies to every step of every run.
:::

:::timeline
- **2003** WSGI, Python's web server interface.
- **2007** Rack: stacked middleware for Ruby web apps.
- **2025** Middleware in LangChain 1.0 agents.
:::
:::

:::step{type=concept title="Tool errors: you decide what the model may see" file="22-middleware/agent.py" line="11-16"}
`ToolErrorMiddleware` catches exceptions from tool calls and turns the ones **you choose** into an error `ToolMessage`.
It takes a function, `on_error(error, request)`:

- return a string: it becomes the tool's result, and the model can explain it to the member;
- return `None`: the exception continues as before, and the run stops.

Why choose? Because exceptions can carry details nobody should see: a database address, a password in a connection
error, a stack of file paths. The co-op's `ValueError` ("no rate for garlic") is meant for people; anything else stays in
the server's logs. Handling is **opt-in**: in the lab's LangChain, without `ToolErrorMiddleware` every tool exception stops the run
(chapter 11 showed it), and with it only the errors your function turns into text reach the model.
:::

:::step{type=task task=tool_errors title="Your turn: which errors the model may see" file="22-middleware/agent.py" line="11-16"}
Finish `on_tool_error(error, request)`:

1. `if isinstance(error, ValueError):` return `f"{request.tool_call['name']} failed: {error}"`.
2. Otherwise return `None`.

The usual slip: returning `str(error)` for every exception, which sends internal details (a database address, a
file path) to the model and on to the member.

Press **Check**.
:::

:::step{type=concept title="A ceiling on calls, and summaries" file="22-middleware/agent.py" line="19-29"}
Two more built-ins finish the job:

| Middleware | Setting | Effect |
|---|---|---|
| `ModelCallLimitMiddleware` | `run_limit=5, exit_behavior="end"` | at most 5 model calls per run; then the run ends with a short message instead of an error |
| `SummarizationMiddleware` | `trigger=("messages", 8), keep=("messages", 4)` | when a thread holds more than 8 messages, a model writes a summary of the older ones, which replaces them; the newest 4 stay as they are |

The summary costs one extra model call each time it runs, and saves tokens on every call after it. It also loses
detail: whatever the summary leaves out is gone.
:::

:::step{type=task task=limits_and_summaries title="Your turn: add the middleware" file="22-middleware/agent.py" line="19-29"}
Add `middleware=[...]` to `navin_agent()`, in this order:

1. `ToolErrorMiddleware(on_tool_error)`
2. `ModelCallLimitMiddleware(run_limit=5, exit_behavior="end")`
3. `SummarizationMiddleware("openai:ai-chat", trigger=("messages", 8), keep=("messages", 4))`

The usual slip: `ToolErrorMiddleware(on_tool_error())` with brackets: pass the function, not its result.

```bash run
cd /workspace/22-middleware && python main.py
```

Press **Check**.
:::

:::step{type=try title="An error explained, and a conversation summarised"}
First, a question that makes the model call a tool with a crop the co-op does not trade. We asked "Call mandi_price
for onion and for garlic, both, and tell me both rates." (and got the same four messages again on 25 November):

```text
AIMessage [{'name': 'mandi_price', 'args': {'crop': 'onion'}, ...}, {'name': 'mandi_price', 'args': {'crop': 'garlic'}, ...}]
ToolMessage '1850'
ToolMessage 'mandi_price failed: The co-op has no rate for garlic: it trades onion, tomato and grapes.'
AIMessage 'The mandi rate for onion is ₹1850 per quintal. We do not have a rate for garlic as we only trade in onion, tomato, and grapes.'
```

The model asked for both rates at once. The garlic call raised `ValueError`; your `on_tool_error` turned it into a
message; the model explained it in plain words. In chapter 11 the same error stopped the whole run.

Then `main.py`, a six-turn conversation with Ravi (a real run; on 25 November we got the same message counts, 2, 4,
8, 8, 8 and 6, in different words):

```text
$ python main.py
> Please look up today's garlic rate with your tool.
I'm sorry, but I can only provide rates for onions, tomatoes, and grapes. Would you like to know the rate for one of those crops instead?
  (2 messages kept in the thread)

> Hello, I am Ravi. I grow onions in Lasalgaon.
Hello Ravi! How can I assist you with your onion farming today? Do you want to know the mandi rate or something else?
  (4 messages kept in the thread)

> What is the onion rate today?
Today's onion rate is Rs 1850 per quintal. Let me know if you need any more information!
  (8 messages kept in the thread)

> And what does storing 40 crates for 10 days cost?
Storing 40 crates for 10 days will cost you Rs 800. If you have any more questions, feel free to ask!
  (8 messages kept in the thread)

> And for 20 days?
Storing 40 crates for 20 days will cost you Rs 1600. Let me know if you need more information!
  (8 messages kept in the thread)

> Thank you. What did I say I grow?
You mentioned that you grow onions.
  (6 messages kept in the thread)

the thread now starts with: HumanMessage "Here is a summary of the conversation to date:\n\n## SESSION INTENT\nThe user's primary goal is to obtain today's onion rate for their farming activities.\n\n## SUMM"
```

(This time the model declined garlic without calling the tool at all, as in chapter 11: the tool's description was
enough.) Watch the message count: 2, 4, then 8, 8, 8, then 6. Each time the thread would pass 8 messages, the older ones are
replaced by one summary message, the newest 4 stay, and the new turn's messages are added; so the count stays at 8 or
below. The last answer proves the summary kept what mattered: Ravi grows onions,
although his introduction is no longer in the thread. The thread now starts with that summary, written by the model.
:::

:::step{type=predict title="Guess first"}
:::question
A database connection fails inside a tool with a `ConnectionError` that includes the server's address. With your
`on_tool_error`, what does the member see?
:::
- [ ] The address, explained by the model
- [x] Nothing of it: `None` lets the exception stop the run, and the details stay in the server's logs
- [ ] A summary
:::explain
Only the errors you choose become messages. That is why the handler is opt-in.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `exit_behavior="end"` do when the limit is reached?
:::
- [x] Ends the run with a short message instead of raising an error
- [ ] Waits and tries again
- [ ] Removes the limit
:::explain
The member gets an answer; your logs show the limit was hit.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the cost of summarising?
:::
- [ ] None
- [x] One extra model call per summary, and whatever detail the summary leaves out
- [ ] All later calls become slower
:::explain
Later calls get cheaper; the summary itself is a call, and a summary is a choice about what to forget.
:::
:::

:::step{type=deep-dive title="Go deeper: more built-in middleware"}
**Retries and fallbacks.** `ModelRetryMiddleware` and `ToolRetryMiddleware` retry with growing waits;
`ModelFallbackMiddleware("openai:...", "anthropic:...")` switches to another model when the first fails.

**Per-tool limits.** `ToolCallLimitMiddleware(tool_name="book_storage", run_limit=1)` allows one booking per run.

**Context editing.** `ContextEditingMiddleware` clears old tool results from the conversation, a lighter alternative to
summaries when tool results are long.
:::

:::step{type=recap}
You can now:

- explain where middleware runs in the agent loop;
- turn chosen tool errors into messages and keep the rest private;
- cap a run's model calls and summarise long threads;
- read the cost and the loss of a summary.

Next, chapter 23: writing your own middleware.

:::photo{src="/lesson-images/langchain/lc-22-notes.webp" alt="Handwritten notes about middleware: Middleware runs at fixed hooks around every model call and tool call. ToolErrorMiddleware turns the errors you choose into messages. Other errors stop the run and stay out of the model's sight. ModelCallLimitMiddleware ends a run after 5 model calls. SummarizationMiddleware replaced older messages with a summary. Our thread stayed at 8 messages or fewer." ai="true"}
One page of notes for this chapter.
:::
:::
