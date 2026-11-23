:::step{type=story title="What must never reach the model"}
Members trust the co-op with personal details, and some type them straight into the chat: "My Aadhaar is 4821 3390
1176, is my membership active?" That number should not leave the co-op's server. Sent to a model provider, it is
stored in request logs the co-op does not control, and it may come back in an answer to someone else's screen.

Other messages should not reach the model at all. A member pastes a whole season's diary, or a script sends the same
long message a thousand times: each one costs tokens and gives nothing.

Both are **guardrails**: checks that run before the model sees anything. In LangChain they are middleware: the
built-in `PIIMiddleware` with your own detector for Aadhaar numbers, and a `before_agent` hook that refuses a message
before the agent even starts.

:::mission
Detect Aadhaar numbers so they are masked before the model sees them, and refuse over-long messages without a single
model call.
:::
:::

:::step{type=history title="A number for every resident, and a law to protect it"}
:::before{title="Data with no rules"}
For years, personal details typed into websites were stored and shared with few rules, and leaks of identity numbers
were common.
:::

India began issuing **Aadhaar** numbers in **2010**: a 12-digit identity number for every resident, now held by more
than a billion people and used for bank accounts, subsidies and land records. The **Aadhaar Act** of **2016** limited who
may collect and store the number, and the **Digital Personal Data Protection Act** of **2023** set rules for all personal
data: collect only what you need, and protect what you hold. For an AI help desk the practical rule is simple: personal
identifiers do not go to a third-party model unless they must.

:::solved
**Mask at the door.** The number is recognised and hidden before it is stored in the conversation or sent anywhere.
:::

:::timeline
- **2010** The first Aadhaar numbers.
- **2016** The Aadhaar Act.
- **2023** The Digital Personal Data Protection Act.
:::
:::

:::step{type=concept title="PII middleware with your own detector" file="24-guardrails/agent.py" line="13-21"}
`PIIMiddleware` finds personal data in messages and handles it with a strategy:

| Strategy | `4821 3390 1176` becomes |
|---|---|
| `"redact"` | `[REDACTED_AADHAAR]` |
| `"mask"` | `****1176` (only the last digits stay) |
| `"hash"` | `<aadhaar_hash:81c288af>`: the same number always gives the same code |
| `"block"` | nothing: the run stops with a `PIIDetectionError` your code must catch |

It knows emails, card numbers, IP addresses and URLs by itself. For anything else you give it a **detector**: a function
that returns the matches, each as `{"type", "value", "start", "end"}`. An Aadhaar number is 12 digits, the first from 2
to 9, often written in groups of four:

```python
AADHAAR = re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b")
PIIMiddleware("aadhaar", detector=find_aadhaar, strategy="mask", apply_to_input=True)
```

With `apply_to_input=True` the member's message is masked before it is saved in the thread and before the model call.
:::

:::step{type=task task=aadhaar_detector title="Your turn: find Aadhaar numbers" file="24-guardrails/agent.py" line="18-22"}
Finish `find_aadhaar(text)`: for every match `m` in `AADHAAR.finditer(text)`, return
`{"type": "aadhaar", "value": m.group(), "start": m.start(), "end": m.end()}`.

Press **Check**.
:::

:::step{type=concept title="Refusing before the agent starts" file="24-guardrails/agent.py" line="25-31"}
`@before_agent` runs once, when a run starts, before any model call. Returning `None` lets the run continue. Returning a
state update with `"jump_to": "end"` adds your message and ends the run at once:

```python
@before_agent(can_jump_to=["end"])
def length_guard(state, runtime):
    if len(state["messages"][-1].content) > MAX_CHARS:
        return {"messages": [AIMessage(TOO_LONG)], "jump_to": "end"}
    return None
```

`can_jump_to=["end"]` declares the jump in advance, so the agent's graph knows this path exists. Order matters too: the
guard comes first in the middleware list, so a refused message never reaches the PII check, the logs or the model.
:::

:::step{type=task task=length_guard title="Your turn: the length guard" file="24-guardrails/agent.py" line="25-31"}
Finish `length_guard(state, runtime)`: if the last message's content is longer than `MAX_CHARS`, return
`{"messages": [AIMessage(TOO_LONG)], "jump_to": "end"}`; otherwise return `None`.

```bash run
cd /workspace/24-guardrails && python main.py
```

Press **Check**.
:::

:::step{type=try title="A masked number, and a refusal that cost nothing"}
```text
$ python main.py
> My Aadhaar is 4821 3390 1176. Is my membership active?
  saved as: 'My Aadhaar is ****1176. Is my membership active?'
  I'm sorry, but I can't check membership status. Please contact the cooperative office directly for assistance.

> Please read my whole story. Please read my whole story. Plea... (717 characters)
  saved as: 'Please read my whole story. Please read my whole story. Please read my'
  That message is too long for me. Please ask in a few sentences, or call the co-op office.
```

The Aadhaar number was masked to `****1176` **in the saved conversation**, so neither the model nor the thread ever held
it. Navin then answered honestly: it has no tool to check membership, and said so.

The 717-character message got the refusal straight from the guard. The model was never called: no tokens, no cost, and
nothing from that message went anywhere.
:::

:::step{type=predict title="Guess first"}
:::question
A member writes their Aadhaar as "4821-3390-1176", with dashes. Does the detector catch it?
:::
- [ ] Yes: it looks for 12 digits
- [x] No: the pattern allows spaces between the groups, not dashes
- [ ] Only the last four digits
:::explain
A detector catches exactly what its pattern describes. Test it on the real ways people write the number, and widen the
pattern (`[\s-]?`) when you find one it misses.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the length guard run before the PII middleware?
:::
- [x] A refused message should not reach anything else: checks, logs or the model
- [ ] PII middleware cannot read long messages
- [ ] The order does not matter
:::explain
Middleware runs in list order. Cheap refusals go first.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `"jump_to": "end"` do?
:::
- [ ] Skips to the last tool
- [x] Ends the run immediately, with the messages you returned
- [ ] Restarts the agent
:::explain
The member gets your message; the model is never called.
:::
:::

:::step{type=deep-dive title="Go deeper: guardrails in production"}
**Checksums.** Real Aadhaar numbers end with a Verhoeff check digit. A detector that verifies it catches fewer false
matches, like a 12-digit phone number written in groups.

**Output too.** `apply_to_output=True` checks what the model writes, and `apply_to_tool_results=True` what tools return
(a database row with someone's number in it).

**A model as a guard.** For "is this message abusive?" a small model can be the check, in a `before_agent` hook. It
costs a call, so put the cheap rule-based guards first.
:::

:::step{type=recap}
You can now:

- mask personal data with `PIIMiddleware` and a detector of your own;
- refuse a message before the agent starts, with `before_agent` and `jump_to`;
- order guards so refusals cost nothing;
- test a detector on the real ways people write their numbers.

Next, chapter 25: a person in the loop. The manager approves every booking before Navin makes it.

:::photo{src="/lesson-images/langchain/lc-24-notes.webp" alt="Handwritten notes about guardrails: Mask at the door; Aadhaar: ****1176; Your detector, your pattern; before_agent: refuse early; 717 characters: no model call" ai="true"}
One page of notes for this chapter.
:::
:::
