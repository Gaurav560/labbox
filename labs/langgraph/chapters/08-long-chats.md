:::step{type=story title="Forty messages about one tap"}
Some complaints are long conversations. Sunita Pawar writes her name and address, asks whether the whole area is dry,
reports what the neighbours saw, asks for a tanker in the evening, mentions the dripping meter. Some citizens write
forty messages over a week about one tap.

With the checkpointer of chapter 7, every message stays in the thread, and every turn sends **all of them** to the model.
The bill grows with every message (you pay for every token sent, every time), answers get slower, and a long enough
thread no longer fits in the model's context window at all.

Two fixes are standard. **Trimming** sends the model only the last few messages: cheap and simple, but the model forgets
whatever was said before them. **Summarising** folds old messages into a short summary that travels with the thread:
one extra model call now and then, and the important facts stay.

:::mission
Trim what the model sees to the last four messages, then build the other way: a node that folds old messages into a
summary and removes them. Send the same six messages to both and compare.
:::
:::

:::step{type=history title="Windows that grew, and costs that stayed"}
:::before{title="Paying by the word"}
Telegrams were charged by the word, so people learned to write "ARRIVING TUESDAY STOP" instead of a letter. Every
message to a model is charged the same way, by the token, on every turn.
:::

Context windows grew fast: **2,048** tokens for GPT-3 (**2020**), **8,192** and **32,768** for GPT-4 (**March 2023**),
**128,000** for GPT-4 Turbo (**November 2023**), a million for Gemini 1.5 (**February 2024**). Size did not make the
problem go away. Each token is still paid for on every turn, and the paper **"Lost in the Middle"** (Liu and others,
**2023**) showed that models use facts at the start and end of a long context much better than facts in the middle.
Keeping the context short and relevant is still the job of the program around the model.

:::solved
**Bounded cost per turn.** A thread can last for weeks while each turn sends the model a small, chosen context.
:::

:::timeline
- **2020** GPT-3: 2,048 tokens.
- **2023** GPT-4: up to 32,768; then 128,000. "Lost in the Middle".
- **2024** One million tokens.
:::

In India, telegrams were sent from offices like this one and charged by the word until the service closed on 15 July 2013. Senders learned to say everything important in very few words, which is what a summary does for a model.

:::photo{src="/lesson-images/langgraph/telegraph.webp" alt="A tall red brick colonial building with white columns and balconies, with a blue sign reading Central Telegraph Office at the gate" credit="Biswarup Ganguly" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Central_Telegraph_Office_-_Red_Cross_Place_-_Kolkata_2011-12-18_0166.JPG"}
The Central Telegraph Office in Kolkata, 2011.
:::
:::

:::step{type=concept title="Trimming: the model sees the end of the chat" file="08-long-chats/chat.py" line="26-35"}
`trim_messages` cuts a list of messages down to a budget:

```python
trim_messages(messages, strategy="last", token_counter=len, max_tokens=4, start_on="human")
```

- `strategy="last"` keeps the end of the conversation.
- `token_counter=len` counts **messages** instead of tokens, so `max_tokens=4` means four messages. Pass the chat model
  itself as the counter to count real tokens.
- `start_on="human"` makes the kept part begin with a citizen's message, never with a reply whose question was cut off.
  That rule wins over the count: we trimmed seven messages (human, reply, human, reply, human, reply, human), and it kept
  **three**, because the fourth from the end was a reply. Without `start_on`, it kept four, starting with that reply.

The state still holds every message (the checkpointer saves them all); only what is **sent** to the model is cut.
:::

:::step{type=task task=trim_history title="Your turn: send only recent messages" file="08-long-chats/chat.py" line="26-30"}
Finish `recent(messages)`: return `trim_messages(messages, strategy="last", token_counter=len, max_tokens=KEEP,
start_on="human")`.

The usual slip: `strategy="first"`. It keeps the **start** of the chat, so the citizen's newest message is the one cut
off. We tried it on seven messages: it kept the first four, and the last question never reached the model. (Leaving
out `token_counter` is an error at once: `TypeError: trim_messages() missing 1 required keyword-only argument:
'token_counter'`.)

Press **Check**.
:::

:::step{type=concept title="Summarising: old messages become a paragraph" file="08-long-chats/chat.py" line="44-55"}
The summarising graph has a second node and a conditional edge:

```python
graph.add_conditional_edges("respond", needs_summary, ["summarise", END])   # more than 6 messages: summarise
```

`summarise` asks the model for a summary of every message except the last two (with the summary so far, so nothing
earlier is lost), and returns two updates:

```python
return {"summary": summary, "messages": [RemoveMessage(id=m.id) for m in old]}
```

The `add_messages` reducer treats a `RemoveMessage` as "delete the message with this id", so the old messages leave the
state. `respond` puts the summary into its system message on every later turn.

:::

:::step{type=task task=summarise_old title="Your turn: fold old messages into a summary" file="08-long-chats/chat.py" line="48-55"}
Finish `summarise(state)`:

1. `summary = model().invoke([SystemMessage(prompt), HumanMessage(transcript)]).content`;
2. `return {"summary": summary, "messages": [RemoveMessage(id=m.id) for m in old]}`.

The usual slip: removing every message (`state["messages"]`) instead of `old`, all but the last two. We tried it with a
fake model: after four turns the state held **no** messages, not even the answer just written.

```bash run
cd /workspace/08-long-chats && python main.py
```

Press **Check**.
:::

:::step{type=try title="The same six messages, two memories"}
```text
$ python main.py
=== trimmed
> Hello, this is Sunita Pawar, 14 Tilak Nagar, lane 3. No water since Monday.
  Hello Sunita, I apologize for the inconvenience. I will report the issue and ensure that water supply is restored as soon as possible.  [84 tokens in, 2 kept]
> Is it the whole area or only our lane?
  I currently don't have that information. I will check and update you shortly.  [129 tokens in, 4 kept]
> The neighbours say a tanker came yesterday, but not to lane 3.
  Thank you for the update. I will look into why lane 3 was missed and get back to you.  [108 tokens in, 6 kept]
> Can the tanker come after 6 in the evening? I work during the day.
  Tanker timings are usually scheduled during the day, but I can check if evening deliveries are possible for you. Please hold on for a moment.  [122 tokens in, 8 kept]
> One more thing: the meter outside is also dripping.
  Thank you for informing us about the dripping meter. I will report this issue for immediate attention.  [125 tokens in, 10 kept]
> Please read back my address and the time I asked for.
  I currently don't have your address or the requested time. Could you please provide that information again?  [110 tokens in, 12 kept]
=== summarised
> Hello, this is Sunita Pawar, 14 Tilak Nagar, lane 3. No water since Monday.
  Hello Sunita, I apologize for the inconvenience. I will report the issue and ensure that water supply is restored as soon as possible.  [84 tokens in, 2 kept]
> Is it the whole area or only our lane?
  I currently don't have that information. I will check and get back to you shortly.  [129 tokens in, 4 kept]
> The neighbours say a tanker came yesterday, but not to lane 3.
  Thank you for the update, Sunita. I will investigate why lane 3 was missed and ensure it is addressed promptly.  [169 tokens in, 6 kept]
> Can the tanker come after 6 in the evening? I work during the day.
  Yes, I will request the tanker to come after 6 PM to accommodate your schedule. Thank you for your patience!  [219 tokens in, 2 kept]
> One more thing: the meter outside is also dripping.
  Thank you for informing me about the dripping meter. I will arrange for a technician to check it as soon as possible.  [190 tokens in, 4 kept]
> Please read back my address and the time I asked for.
  Your address is 14 Tilak Nagar, lane 3, and you requested the tanker to come after 6 PM. Is that correct?  [234 tokens in, 6 kept]
summary: Sunita Pawar, residing at 14 Tilak Nagar, lane 3, has reported no water supply since Monday. She mentioned that a tanker came to the area yesterday but did not service lane 3. Sunita is seeking information on why her lane was missed and requests prompt action to restore water supply.
```

(This is the run of 26 November. The first run, when the chapter was written, gave the same pattern: the trimmed
Harsh asked for the address again, the summarised one read it back.)

:::diagram{name="lg-summary"}
The tokens of every turn above, and how many messages each state kept.
:::

**Trimmed:** the tokens sent stay flat, between 108 and 129 a turn after the first, however long the chat gets, while the state keeps all
12 messages. But the last question fails: the address was in the first message, which the model no longer sees, so it
asks Sunita to write it again. On turn 4 it also invented a rule, "tanker timings are usually scheduled during the day".

**Summarised:** after turn 4 the chat had 8 messages, more than 6, so `summarise` folded the first six into the summary
and removed them ("2 kept"). The final answer reads back the address and the 6 pm request correctly: the address came
from the summary, the time from a message still in the state. The cost is higher per turn here (up to 234 tokens) plus
one extra model call for each summary, and it stays bounded as the chat grows. Read turn 4 too: the summarised Harsh
promised "I will request the tanker to come after 6 PM", a promise nobody can check yet. Memory made it more helpful,
not more careful.

Which one is right depends on the chat. For a complaint desk, losing the address is worse than a few tokens.
:::

:::step{type=predict title="Guess first"}
:::question
In the trimmed graph, how many messages does the **state** hold after 20 turns?
:::
- [ ] 4
- [x] 40: trimming limits what is sent to the model, not what is saved
- [ ] 20
:::explain
`recent` is called inside the node; the checkpointer still saves every message. To shrink the state itself, remove
messages, as `summarise` does.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why `start_on="human"` when trimming?
:::
- [ ] It is required
- [x] So the kept part never starts with a reply whose question was cut off
- [ ] So only citizens' messages are kept
:::explain
A reply without its question confuses the model, and some providers refuse a chat that starts with a tool result.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `RemoveMessage(id=m.id)` do inside an update?
:::
- [x] The messages reducer deletes the message with that id from the state
- [ ] It hides the message from the model only
- [ ] It sends a message to the citizen
:::explain
`add_messages` appends new messages, replaces ones with the same id, and deletes ones named by `RemoveMessage`.
:::
:::

:::step{type=deep-dive title="Go deeper: long chats in practice"}
**Real token budgets.** `trim_messages(messages, token_counter=model, max_tokens=2000, ...)` counts real tokens with the
model's own tokenizer, which is what you pay for.

**What a summary bends.** Summaries are written by a model, so they can drop or bend facts. The summary above says
Sunita "is seeking information on why her lane was missed"; she only reported it. (The first run's summary bent it
another way: "requested an investigation".) Keep facts the desk depends on
(address, phone, ticket number) in their own state fields, set by code, not only in a summary.

**Middleware.** In `create_agent` (the LangChain course), `SummarizationMiddleware` does the same job; in your own
graphs, you decide where summarising runs.
:::

:::step{type=recap}
You can now:

- explain why long threads cost more on every turn;
- trim what the model sees with `trim_messages`, while the state keeps everything;
- fold old messages into a summary and remove them with `RemoveMessage`;
- choose between the two after seeing what each one forgets.

Next, chapter 9: durable execution, so a job that crashes continues where it stopped.

:::photo{src="/lesson-images/langgraph/lg-08-notes.webp" alt="Handwritten notes titled Long chats, trim what the model sees or summarise: every turn pays for every message sent, trimming sends only the last few messages, summarising folds old messages into a short summary and removes them; 6 messages from Sunita, trimmed to the last 4, summarised with old ones folded, read back my address, only the summary knew; trimmed used 84 to 129 tokens a turn and kept 12 messages; summarised used up to 234 tokens and kept 6; start_on human can keep 3, not 4; summaries bend facts, so keep the address in its own field" ai="true"}
One page of notes for this chapter.
:::
:::
