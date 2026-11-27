:::step{type=story title="Week three: the model arrives"}
Two weeks in, and you have not yet called a language model. That was deliberate. You know the problem (12.5 days), where
the time goes (photos, 44.6%), what the pilot is (57 claims), and Claimdesk can read the customer's export, database and
old system, and refuse bad data at the door.

Now the model. Deccan Shield's security team has one condition, and it is a good one: **no AI provider key on any
developer laptop or customer server**. Every call goes through one **gateway** that holds the key, checks who is
calling, enforces a budget, and records every request and answer.

In LabBox, your lab machine is set up exactly like that. In this chapter you make your first call through the gateway,
read the record it keeps, and then answer the question Deccan Shield's finance team will ask before anyone else: **what
does it cost?**

:::mission
Call the model through the gateway with a system message, then turn its token counts into rupees, per call and per
month.
:::
:::

:::step{type=concept title="A gateway between your code and the model" file="08-first-call/gateway.py" line="13-15"}
A **language model** here is a service you send text to over HTTP and get text back from. **gpt-4o-mini**, the model
this lab uses, belongs to OpenAI.

Your code never talks to OpenAI directly. It talks to the **LabBox gateway**, which talks to OpenAI:

```text
gateway.py  ->  LabBox gateway (key, budget, log)  ->  OpenAI
```

LabBox puts two values in your machine's environment:

- `OPENAI_BASE_URL`: the gateway's address;
- `OPENAI_API_KEY`: a **lab token**, valid only at the gateway, only for you and this lab. It is not an OpenAI key.

`client()` (lines 13 to 15) builds an OpenAI client from those two values. The official `openai` library does not care
that it is talking to a gateway: the gateway speaks the same API. That is the point. The same code later runs at Deccan
Shield, pointed at their gateway.

`MODEL = "ai-chat"` (line 6) is a name the gateway maps to the real model. If Deccan Shield later chooses another
model, the gateway changes the mapping and your code does not change.

Why does a customer insist on this? Three reasons an FDE hears in every enterprise:

| Concern | What the gateway does |
|---|---|
| Keys leak (laptops, logs, git history) | the real key lives in one place only |
| Costs run away (a loop, a bug) | a daily budget per person, and a rate limit |
| "What did the AI see and say?" | every request and answer is logged, for audits |

A gateway works like a toll plaza on an expressway: every vehicle passes the same booths, where it is checked, charged
and counted, so the road's owner always knows who used it and how much. Here every request passes the gateway in the
same way.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-toll.webp" alt="A black and white aerial view of a wide Indian expressway with heavy traffic, and a row of toll booths across the road in the distance." credit="kevin rawlings" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:India_highway_gurgaon.jpg"}
An expressway near Gurgaon, with its toll plaza across the road in the distance (top centre).
:::
:::

:::step{type=example title="Worked example: one chat completion"}
This is only to read; it is not in your project. One call has a list of **messages**, each with a **role**:

```python
completion = openai.chat.completions.create(
    model="ai-chat",
    temperature=0,
    messages=[
        {"role": "system", "content": "You are a librarian. Be brief."},
        {"role": "user", "content": "What is an ISBN?"},
    ],
)
print(completion.choices[0].message.content)
print(completion.usage.prompt_tokens, completion.usage.completion_tokens)
```

- The **system** message sets the rules for the whole conversation: who the model is, how long to answer, what not to do.
- The **user** message is the question.
- `temperature=0` makes the model pick its most likely words, so the same question gives (almost always) the same
  answer. While building and testing, you want that.
- The answer is in `choices[0].message.content` (there can be several choices; we ask for one).
- `usage` counts **tokens**, the pieces of text the model reads and writes: a token is roughly three quarters of an
  English word. `prompt_tokens` went in, `completion_tokens` came out. You pay for both.
:::

:::step{type=predict title="Guess first"}
:::question
The starter's `ask()` returns `("", None)`. What happens when you run `python gateway.py`?
:::
- [ ] It prints an empty answer and zero tokens
- [x] It crashes when it reads the token counts from None
- [ ] It calls the model anyway
:::explain
`usage` is `None`, and `None` has no `prompt_tokens`. The next step shows the real error.
:::
:::

:::step{type=try title="No call yet"}
```text
$ python gateway.py

Traceback (most recent call last):
  File "/workspace/08-first-call/gateway.py", line 42, in <module>
    print(f"tokens: {usage.prompt_tokens} in, {usage.completion_tokens} out")
                     ^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'prompt_tokens'
```

The empty line is the empty answer; then the program fails reading the token counts. Write `ask()`.
:::

:::step{type=task task=ask_model title="Your turn: the first call through the gateway"}
In `ask` in `gateway.py`:

1. `openai = openai or client()` (the check passes its own client; normally you get the gateway's).
2. Call `openai.chat.completions.create(model=MODEL, temperature=0, messages=[...])` with two messages:
   `{"role": "system", "content": SYSTEM}` and `{"role": "user", "content": question}`.
3. Return `completion.choices[0].message.content` and `completion.usage`.

Press **Check**.
:::

:::step{type=try title="A real answer, and its record"}
We ran it in the lab, through the gateway, on 27 November:

```text
$ python gateway.py
A deductible is the amount you must pay out of pocket before your insurance coverage kicks in for a claim. It helps lower the premium costs by sharing some of the financial risk with the policyholder.
tokens: 41 in, 39 out
...
```

(Your answer may differ by a word or two; the token counts will be close. The cost lines below it are the next task.)

Now look at what the gateway recorded. `lab requests --last` shows the last request exactly as it went out, and the
answer exactly as it came back:

```text
$ lab requests --last
2026-11-27 00:06:27 UTC  ai-chat -> openai/gpt-4o-mini  41 in, 39 out

--- request ---
{"messages": [{"role": "system", "content": "You help motor insurance adjusters at Deccan Shield Insurance in Pune. Answer in at most two short sentences."}, {"role": "user", "content": "What is a deductible in motor insurance?"}], "model": "ai-chat", "temperature": 0, "max_tokens": 1024}

--- response ---
{"id": "chatcmpl-...", "object": "chat.completion", "model": "gpt-4o-mini-2024-07-18", ... "usage": {"prompt_tokens": 41, "completion_tokens": 39, "total_tokens": 80, ...}}
```

Three things to notice:

- `ai-chat -> openai/gpt-4o-mini`: the gateway mapped the name, and the response says which exact model version answered
  (`gpt-4o-mini-2024-07-18`, released in July 2024).
- `"max_tokens": 1024`: the gateway added a cap on the answer's length, which you did not send. Gateways enforce policy.
- 41 tokens in for two short sentences: the system message counts too, on **every** call.

When an adjuster asks "why did Claimdesk say that?", this record is your answer.
:::

:::step{type=history title="From research demo to rupees per call"}
:::before{title="Before: models you could not rent"}
Until 2020, a large language model was something a research lab trained and wrote papers about. Using one meant hiring
researchers and buying computers to run it.
:::

In June 2020 OpenAI opened an API for GPT-3: any program could send text and get text back, paying per token. On
30 November 2022 ChatGPT made the same models famous with the public. In July 2024 OpenAI released **gpt-4o-mini**, a
small, cheap model that is good enough for many business tasks, and the one this lab uses.

Paying per token changed how software is built and sold. A feature now has a **running cost** per use, like electricity,
and an FDE is often the first person asked to estimate it.

:::solved
Rent a model per token through an API, instead of building one.
:::

:::timeline
- **June 2020** The OpenAI API opens with GPT-3.
- **30 November 2022** ChatGPT launches.
- **18 July 2024** gpt-4o-mini is released.
- **2025 to 2026** Enterprises route model calls through gateways for keys, budgets and audit logs.
:::

:::funfact
"Token" prices are quoted per million tokens because single calls are so cheap: one call in this chapter costs a
quarter of a paisa.
:::
:::

:::step{type=concept title="Tokens into rupees" file="08-first-call/gateway.py" line="26-36"}
The gateway's price list for gpt-4o-mini (lines 7 and 8):

- **$0.15 per million input tokens** (`prompt_tokens`);
- **$0.60 per million output tokens** (`completion_tokens`): writing costs four times as much as reading.

Deccan Shield thinks in rupees, so line 9 holds the rate from their finance sheet, `RS_PER_USD = 88.0` (an assumption:
write down where it came from, and update it).

For one call:

```text
dollars = (prompt_tokens x 0.15 + completion_tokens x 0.60) / 1,000,000
rupees  = dollars x 88
```

For our call, 41 tokens in and 39 out: (41 x 0.15 + 39 x 0.60) / 1,000,000 = $0.00002955, which is about Rs 0.0026.

One call is nothing. The question finance asks is **per month**: the pilot handles about 80 claims a day across all its
steps, so `monthly_rs(usage, 80)` multiplies the cost of one call by 80 calls a day and 30 days.

Do not round inside `cost_rs`: rounding Rs 0.0026 to two places gives Rs 0.00, and multiplying zero by 2,400 calls still
gives zero. Round once, at the end, in `monthly_rs`.
:::

:::step{type=task task=call_cost title="Your turn: what each call costs"}
1. In `cost_rs`, compute the dollars from `usage.prompt_tokens` and `usage.completion_tokens` with the two prices, divide by
   1,000,000, multiply by `RS_PER_USD`, and return it unrounded.
2. In `monthly_rs`, return `cost_rs(usage) * calls_per_day * days`, rounded to 2 places.

Press **Check**.
:::

:::step{type=try title="The first cost estimate"}
```text
$ python gateway.py
...
tokens: 41 in, 39 out
this call: Rs 0.0026
80 such calls a day for 30 days: Rs 6.24
```

**Rs 6.24 a month** for 80 short questions a day. Real Claimdesk calls will be bigger (a whole claim email and policy
clauses go in, a structured answer comes out), so you will measure again in chapter 9 and in Part 5. But the shape of
the answer is already clear, and worth saying to Meera early: the model costs rupees a month; the adjusters' 10.8 hours a
week cost far more.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does Deccan Shield want every model call to go through a gateway?
:::
- [ ] Gateways make the model smarter
- [x] One place holds the real key, enforces budgets and records every request and answer
- [ ] The OpenAI library only works with gateways
:::explain
The gateway is about control: secrets, spend and audit. The model and your code are the same with or without it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A call has 2,000 tokens in and 100 out. Which part costs more?
:::
- [x] The input: 2,000 x $0.15 is $0.0003, more than 100 x $0.60 which is $0.00006
- [ ] The output, because output tokens cost four times as much
- [ ] They cost the same
:::explain
Output is dearer per token, but long inputs (emails, clauses, history) usually dominate the bill. That is why chapter 10
sends only three clauses, not the whole policy.
:::
:::

:::step{type=deep-dive title="Go deeper: gateways in production"}
**Products.** Teams use LiteLLM, Portkey, Kong AI Gateway, Azure API Management or a cloud provider's own gateway. They
add the same things as LabBox's: keys, budgets, rate limits, logs, and routing between models.

**Logs contain customer data.** Every request holds a claim email. Agree with the customer's security team how long logs
are kept and who can read them; chapter 17 removes personal data before it is logged.

**Measure, do not estimate.** Use the real token counts from a day of traffic, per step, for the monthly figure. Estimates
from one test call are usually low.

**Caching.** Repeated identical prompts (the same system message on every call) can be cheaper with provider prompt
caching; chapter 18 caches whole answers where that is safe.
:::

:::step{type=recap}
You can now:

- call a language model through a gateway that holds the key, with system and user messages;
- read the gateway's record of a request, and explain why enterprises insist on one;
- turn token counts into rupees per call and per month, rounding only at the end;
- give the customer a first cost estimate, and say what it does not include yet.

Next, chapter 9: from questions to work. Read a claim email and get the six fields an adjuster needs, in a shape code can
check.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-08-notes.webp" alt="Handwritten notes about the first model call and its cost: Every model call goes through the gateway. The gateway keeps the key, the budget and a log. Your code gets a lab token, never the real key. Output tokens cost four times input tokens. Round only the final monthly total. 80 calls a day cost about Rs 6 a month." ai="true"}
One page of notes for this chapter.
:::
:::
