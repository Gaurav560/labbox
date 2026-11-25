:::step{type=story title="Please reply in Marathi, from now on"}
Some facts belong to a conversation: "no water in lane 3 since Monday". Others belong to the **person**, and should be
known in every conversation they ever start: "please reply in Marathi from now on". A thread (chapter 7) forgets the
first kind when the complaint is closed, which is right. It also forgets the second kind, which is wrong: the next
complaint from the same phone gets English again, and the citizen has to ask again, every time.

The crews have the same need for the **board**: notes like "the Gandhi Chowk tank's inlet valve sticks after heavy
rain" should be found whenever a complaint is about that tank, whatever words it uses.

LangGraph keeps such facts in a **store**: a place outside any thread, shared by all of them, organised in namespaces
like folders. Nodes read and write it through the runtime.

:::mission
Save a citizen's reply language in the store when they ask for one, then read it in every new thread from the same
phone. Then search crew notes by meaning.
:::
:::

:::step{type=history title="Remembering the customer"}
:::before{title="Memory in one person's head"}
A corner shopkeeper remembers that you take the newspaper in Marathi and pay on Sundays. When the shop grew, or the
shopkeeper changed, that memory was gone.
:::

Businesses wrote such facts down: card files, and from **1956** the **Rolodex**, a wheel of cards with a customer on each,
on desks all over the world. In the **1990s** customer databases (CRM) put them in shared software, so every clerk saw
the same facts about you. Chat assistants needed the same thing: in **February 2024** ChatGPT got a "memory" of facts
about each user across chats, and LangGraph's **store** gives your own graphs that layer: facts per person (or per
street, or per team), kept apart from any one conversation.

:::solved
**Facts that follow the person.** Asked once, used in every thread, on every server that shares the store.
:::

:::timeline
- **1956** The Rolodex.
- **1990s** Customer databases.
- **2024** Memory across chats; LangGraph stores.
:::

A Rolodex: one card per person or business, kept on the desk, so whoever sat there could find what the office knew about them.

:::photo{src="/lesson-images/langgraph/rolodex.webp" alt="A rotary card file seen from the front, with cream cards on a wheel and blue letter tabs B, C and D, the front card typed with a name and phone numbers" credit="ArnoldReinhold" license="CC BY 2.5" source="https://commons.wikimedia.org/wiki/File:Rolodex.agr.jpg"}
A Rolodex card file from the 1970s.
:::
:::

:::step{type=concept title="A store, a namespace, a key" file="12-stores/chat.py" line="32-36"}
A store holds JSON values under a **namespace** (a tuple, like a folder path) and a **key**:

```python
store.put(("citizens", "98220"), "profile", {"language": "Marathi"})
store.get(("citizens", "98220"), "profile").value      # {'language': 'Marathi'}
```

Compile the graph with it (`compile(checkpointer=..., store=store)`), and every node can reach it through the
**runtime**. The graph also gets a **context schema**: per-run data that is not part of the state, here the citizen's
phone number, passed as `invoke(..., context=Citizen("98220"))`:

```python
def note_preferences(state: MessagesState, runtime: Runtime[Citizen]) -> dict:
    ...runtime.store...  runtime.context.phone ...
```

| | Checkpointer (thread) | Store |
|---|---|---|
| Holds | one conversation's state, every step | facts you choose to keep |
| Shared by | one thread | every thread |
| Ends | when you stop using the thread | when you delete it |
| Example | "no water since Monday" | "reply in Marathi" |
:::

:::step{type=task task=save_preference title="Your turn: remember the language" file="12-stores/chat.py" line="32-36"}
In `note_preferences`, when `prefs.language` is set, save it:
`runtime.store.put(("citizens", runtime.context.phone), "profile", {"language": prefs.language})`.

The usual slip: saving a bare string, `put(..., "profile", prefs.language)`. A store value must be a dictionary. We
tried it: `ValueError: dictionary update sequence element #0 has length 1; 2 is required`, an unclear message for a
simple cause.

Press **Check**.
:::

:::step{type=concept title="Reading it in every thread" file="12-stores/chat.py" line="39-43"}
`respond` looks the citizen up before writing:

```python
item = runtime.store.get(("citizens", runtime.context.phone), "profile")
language = item.value["language"] if item else "English"
```

`get` returns an `Item` (with `.value`, `.key`, `.namespace` and timestamps) or `None`. The language then goes into the
system message. The thread id does not matter here: a brand-new thread from the same phone finds the same profile.

:::diagram{name="lg-store"}
The three real complaints of this chapter (26 November) and the one fact the store kept.
:::
:::

:::step{type=task task=use_preference title="Your turn: use it in every thread" file="12-stores/chat.py" line="39-43"}
In `respond`:

1. `item = runtime.store.get(("citizens", runtime.context.phone), "profile")`;
2. `language = item.value["language"] if item else "English"`.

The usual slips, both tried: `item["language"]` (`TypeError: 'Item' object is not subscriptable`: the dictionary is
`item.value`), and forgetting the `if item` check, which fails for every phone with no profile yet:
`AttributeError: 'NoneType' object has no attribute 'value'`.

```bash run
cd /workspace/12-stores && python main.py
```

Press **Check**.
:::

:::step{type=concept title="Searching by meaning" file="12-stores/main.py" line="18-25"}
A store can also **index** what you put in it with an embedding model (the LangChain course, chapter 3), and then
`search` by meaning:

```python
notes = InMemoryStore(index={"embed": init_embeddings("openai:ai-embed"), "dims": 1536})
notes.put(("crew_notes",), "n1", {"text": "Gandhi Chowk tank: the inlet valve sticks after heavy rain, ..."})
notes.search(("crew_notes",), query="the tank valve jams in the monsoon", limit=2)
```

Each result has a `score` (similarity, higher is closer). By default the store embeds the **whole value as JSON**,
braces and key included. We checked: the cosine of the question with the JSON text `{"text": "Gandhi Chowk tank..."}` is
0.59, the score you will see; with the note's text alone it is 0.63. Add `"fields": ["text"]` to the index to embed
only the text: the scores then became 0.63 and 0.30. This is how an agent finds "what do we know about this?" in a
store full of notes, without exact words.
:::

:::step{type=try title="Two threads, one memory, and a note found by meaning"}
```text
$ python main.py
98220 / complaint-1
> Please reply in Marathi from now on. No water in Shivaji Nagar since morning.
  शिवाजी नगरमध्ये पाण्याचा अभाव आहे, याबद्दल खेद आहे. एक क्रू तिथे पाठवला जाईल.

98220 / complaint-2
> The pipe near my gate is leaking.
  आपल्या गेटजवळील पाईप लीक होत असल्याबद्दल खेद आहे. एक क्रू तिथे पाठवला जाईल.

70300 / complaint-3
> The pipe near my gate is leaking.
  Thank you for reporting the leak. A crew will be assigned to address the issue.

stored: [(('citizens', '98220'), {'language': 'Marathi'})]
0.59  Gandhi Chowk tank: the inlet valve sticks after heavy rain, open it by hand.
0.27  Station Road: the main is 40 years old, cast iron, expect bursts in summer.
```

(We ran it again on 26 November: the same behaviour and the same two scores; the Marathi replies were worded a little
differently.)

Complaint 1 asked for Marathi: `note_preferences` saved it, and the reply came in Marathi ("we regret the lack of water
in Shivaji Nagar; a crew will be sent there"). Complaint 2 is a **new thread**, with nothing about language in it, and
still came in Marathi: the profile was in the store. Complaint 3, the same words from another phone, got English. The
store holds exactly one fact.

The search found the right note with none of its words: "jams" for "sticks", "monsoon" for "heavy rain". The scores are
cosine similarities (of the JSON text, as above); 0.59 against 0.27 is a clear winner.

One thing to check before shipping: nobody confirmed that 98220 really wants Marathi **forever**. A fact saved from one
message is a guess about the person. Real systems show what they remember ("I'll reply in Marathi from now on, write
ENGLISH to change it") and let people correct it.
:::

:::step{type=predict title="Guess first"}
:::question
The server restarts. A new complaint arrives from 98220. With `InMemoryStore`, in which language is the reply?
:::
- [ ] Marathi
- [x] English: an in-memory store is gone with the process
- [ ] It fails
:::explain
Like `InMemorySaver`, `InMemoryStore` is for tests. Production uses `PostgresStore` (or another persistent store).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does a fact belong that every future conversation with a citizen should know?
:::
- [ ] In the thread's state
- [x] In the store, under a namespace for that citizen
- [ ] In the system prompt of the code
:::explain
State belongs to one thread; the store is shared by all threads.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
How do the nodes know whose phone number the run is for?
:::
- [x] From the runtime context, passed as `invoke(..., context=Citizen(phone))`
- [ ] From the thread id
- [ ] From the last message
:::explain
Context is per-run data that is not part of the state: user ids, phone numbers, settings.
:::
:::

:::step{type=deep-dive title="Go deeper: memory that lasts"}
**Kinds of memory.** Facts about a person (semantic memory), what happened before (episodic memory, often whole past
threads summarised) and rules learned for the job (procedural memory, like a prompt improved over time) can all live in
a store, in different namespaces.

**Writing memories in the background.** Extracting facts costs a model call per message. Many systems do it after the
reply is sent, or once per conversation, so the citizen does not wait.

**Privacy.** A store keeps personal data across conversations. Save only what you need, let people see and delete it,
and keep phone numbers and addresses out of logs.
:::

:::step{type=recap}
You can now:

- tell a thread's state apart from facts that outlive it;
- give a graph a store and a context schema, and reach both through `runtime`;
- save and read a person's facts by namespace and key;
- search a store by meaning with an embedding index;
- treat a saved preference as something the person can see and change.

That ends Part 2. Next, chapter 13: an agent graph, built by hand.

:::photo{src="/lesson-images/langgraph/lg-12-notes.webp" alt="Handwritten notes titled Stores, facts that outlive a thread: a store keeps JSON values under a namespace and a key, shared by every thread, and nodes reach it through runtime.store while runtime.context says whose run it is; ask for Marathi, put under citizens 98220 profile, a new thread from the same phone, get Marathi, reply in Marathi; a bare string value gives ValueError; use item.value, not item with brackets; with no profile yet, check for None; search embeds the JSON and scored 0.59, with fields text 0.63" ai="true"}
One page of notes for this chapter.
:::
:::
