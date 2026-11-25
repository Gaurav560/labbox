:::step{type=story title="Complaints the rules cannot read"}
Harsh's keyword rules work for "brown water" and "no water". Real complaints are messier: "Tap water in Tilak Nagar
smells like sewage, my children drank it." "pani nahi aaya aaj gandhi chowk mein." "Why is my bill Rs 2,400 this month?"
No list of keywords covers every way people write, in every language they mix.

This is where a model earns its place in a graph: one **node** that reads the complaint and returns its kind, severity
and street as a checked object, and another that writes the first reply. Everything else, the promised hours, the
routing, the zones, stays in Python. A node that calls a model is still just a function: state in, update out.

:::mission
Write a triage node that turns a complaint into a structured `Triage` with a model, and a reply node that writes a
first reply promising only the time Python computed.
:::
:::

:::step{type=history title="From spam filters to models that read anything"}
:::before{title="Classifiers trained for one job"}
Text classification used to mean training a model for each task, on thousands of labelled examples: one for spam, one
for sentiment, one for each kind of complaint.
:::

In **2002** Paul Graham's essay **"A Plan for Spam"** popularised Bayesian spam filters: count which words appear in
spam and in normal mail, and score each new message. They worked well, for spam only. In **2020** the GPT-3 paper,
"Language Models are Few-Shot Learners", showed one large model doing new classification tasks from a description and a
few examples, with no training. Since **2024** structured outputs (chapter 13 of the LangChain course) make such a
model return exactly the fields a program needs.

:::solved
**One model, any wording, a fixed shape.** Classification without training data, returned as an object the graph can
route on.
:::

:::timeline
- **2002** "A Plan for Spam": Bayesian filters.
- **2020** GPT-3: tasks from a description.
- **2024** Structured outputs.
:::

Before any program classified text, people did: clerks read every address and dropped each letter into the right bag, a routing decision made thousands of times a day.

:::photo{src="/lesson-images/langgraph/sorting.webp" alt="A long post office sorting room with clerks standing at wooden pigeonhole racks and rows of open canvas mail bags hanging in frames" credit="Archives New Zealand" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:General_Post_Office_mail_sorting_room,_Wellington_c.1900s.jpg"}
The mail sorting room of the General Post Office in Wellington, around 1900.
:::
:::

:::step{type=concept title="A model call inside a node" file="04-model-nodes/graph.py" line="16-38"}
The triage node is three lines of LangChain you already know, inside a LangGraph node:

```python
def triage(state: Ticket) -> dict:
    result = model().with_structured_output(Triage).invoke([SystemMessage(TRIAGE), HumanMessage(state["text"])])
    return result.model_dump()        # {"kind": ..., "severity": ..., "street": ...}
```

`Triage` is a Pydantic model (a class whose fields are checked when an object is made). It limits `kind` and
`severity` to the board's values with `Literal` (from `typing`: "only these exact values"), so the router of chapter 3 always gets a name
it knows. The rules for severity ("dirty water is always urgent") are written in the `TRIAGE` system message, where the
model reads them.

`model()` builds the chat model when the node runs, not when the file is imported, so the checks can point it at their
fake server, and a long-running graph always uses the current settings.

:::diagram{name="lg-model-node"}
One real run (26 November): two model calls, and the promise between them made by Python.
:::
:::

:::step{type=task task=triage_node title="Your turn: the triage node" file="04-model-nodes/graph.py" line="35-38"}
Finish `triage(state)`:

1. `result = model().with_structured_output(Triage).invoke([SystemMessage(TRIAGE), HumanMessage(state["text"])])`;
2. `return result.model_dump()`.

The usual slip: forgetting `.with_structured_output(Triage)`. The model then returns an ordinary message, whose
fields (`content` and so on) are not keys of the state. We tried it on 26 November: LangGraph quietly ignored them,
and the next node stopped with `KeyError: 'kind'`. (Leaving out `.model_dump()` is fine in LangGraph 1.2.24, we
found: a node may return a Pydantic object as its update. The dict keeps the update easy to read.)

Press **Check**.
:::

:::step{type=concept title="What the model may promise" file="04-model-nodes/graph.py" line="41-46"}
The reply node gives the model **facts** (the complaint, its kind, the street, and the response time Python looked up
from the severity) and the `REPLY` instruction: "Promise only the response time you are given, nothing else."

The model writes the sentence; Python decides the promise. A model asked to "reply to this complaint" with no facts
would happily promise "a crew within the hour", and the board would have to keep it.
:::

:::step{type=task task=reply_node title="Your turn: the reply node" file="04-model-nodes/graph.py" line="41-46"}
Finish `draft_reply(state)`:

1. `answer = model().invoke([SystemMessage(REPLY), HumanMessage(facts)])` (`facts` is already built above);
2. `return {"reply": answer.content}`.

The usual slip: `{"reply": answer}` without `.content`. Nothing fails, but the state then holds a whole `AIMessage`,
and we saw it print as `content='Dear Citizen, thank you...'` instead of the text.

```bash run
cd /workspace/04-model-nodes && python main.py
```

Press **Check**.
:::

:::step{type=try title="Four messy complaints"}
```text
$ python main.py
> Tap water in Tilak Nagar smells like sewage, my children drank it.
  dirty_water, urgent, street 'Tilak Nagar'
  Thank you for bringing this to our attention. We will investigate the issue and respond within 4 hours.

> Since 3 days no water in the upper floors of Station Road society.
  no_water, high, street 'Station Road'
  Dear Citizen, thank you for bringing this to our attention. We will address your complaint regarding the water issue on Station Road within the next 24 hours.

> Why is my bill Rs 2,400 this month? Usually it is Rs 600.
  billing, normal, street ''
  Thank you for reaching out regarding your bill. We will investigate your concern and get back to you within 72 hours.

> pani nahi aaya aaj gandhi chowk mein
  no_water, high, street 'Gandhi Chowk'
  Dear Citizen, thank you for bringing this to our attention. We will address the water issue at Gandhi Chowk within the next 24 hours.
```

(We ran it again on 26 November: the same four triages, and the same replies except the first, which now also
named Tilak Nagar: "We will investigate the issue in Tilak Nagar and respond within the next 4 hours." Each triage call
was about 180 tokens in, each reply about 90.)

All four triaged correctly, including "pani nahi aaya aaj gandhi chowk mein" (Hindi in English letters: "the water did
not come today in Gandhi Chowk"), with the street written the way the map spells it. The billing complaint has no
street, and the model returned an empty string instead of inventing one. Each reply promised exactly the hours Python
gave it.

Now read the first reply as the parent who wrote it: "my children drank it", and the answer is only "we will
investigate within 4 hours". It says nothing about not drinking the water or seeing a doctor. The model followed its
instructions perfectly; the instructions were incomplete. For urgent health complaints the board needs fixed advice in
the reply, written by people and added by Python, not left to the model. That is a graph change (a separate node for
health replies), and exactly the kind of decision this course keeps in code.
:::

:::step{type=predict title="Guess first"}
:::question
The model returns `severity: "critical"`, a word not in the `Literal`. What happens?
:::
- [ ] The router sends it to repair_crew
- [x] Validation fails before the update reaches the state, so the graph never routes on a value it does not know
- [ ] It is stored as it is
:::explain
We tried it: `Triage(kind="leak", severity="critical", street="")` raises `ValidationError: 1 validation error for
Triage, severity`. The schema is a gate between the model and the graph. Chapter 9 adds retries for such failures.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does Python compute the response time instead of the model?
:::
- [x] It is a promise the board must keep; it comes from the rules, not from likely-sounding text
- [ ] Models cannot count hours
- [ ] It is faster
:::explain
Facts and promises in code, wording in the model.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What makes a model node different from a Python node, for the graph?
:::
- [ ] It must be async
- [x] Nothing: it is a function from state to update
- [ ] It needs its own edge type
:::explain
That is why you can swap a rule for a model (or back) without touching the rest of the graph.
:::
:::

:::step{type=deep-dive title="Go deeper: models in graphs"}
**Cost per node.** Every model node is a paid call on every run. Rules for the easy cases and a model for the rest (a
conditional edge) cuts the bill.

**Retries.** Nodes can be given a retry policy (`graph.add_node(..., retry_policy=RetryPolicy(max_attempts=3))`) for
rate limits and timeouts. (In 1.2.24 `add_node` also takes `timeout`, `cache_policy` and `error_handler`.)

**Fixed wording for safety.** Advice that must be exact (health warnings, legal text) belongs in templates filled by
Python, as the try step showed.
:::

:::step{type=recap}
You can now:

- put a model call inside a node and return its result as an update;
- turn free text into a structured, checked object for routing;
- give a model facts and limit what it may promise;
- spot a perfectly obeyed but incomplete instruction, and move that decision into the graph.

Next, chapter 5: the five workflow patterns, with parallel branches and an evaluator loop.

:::photo{src="/lesson-images/langgraph/lg-04-notes.webp" alt="Handwritten notes titled Model nodes, the model writes words and Python makes promises: a node that calls a model is still a function, state in and update out, and structured output turns free text into a checked object the graph can route on; complaint text, triage where the model returns Triage, Python looks up the hours, draft_reply where the model writes, a reply with the right promise; Hindi in English letters was triaged right; with no structured output, KeyError kind; with no .content, a whole message in the state; critical fails the Literal check" ai="true"}
One page of notes for this chapter.
:::
:::
