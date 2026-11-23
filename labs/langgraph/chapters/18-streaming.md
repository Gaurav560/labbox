:::step{type=story title="Four seconds of nothing"}
A citizen asks Harsh for an update in the board's chat app. Harsh looks up the tickets (the ticket system is slow: about
a second), then a model writes the reply (two or three seconds more). For almost four seconds the screen shows nothing.
People tap again, close the app, or call the helpline, which is exactly what the chat was meant to prevent.

Nothing about the work can be made much faster. What can change is what the citizen **sees** while it happens:
"finding your tickets...", "checking the crew schedule...", and then the reply appearing word by word, starting long
before it is finished. LangGraph streams all of that from a running graph: progress events written by your nodes, and
the model's tokens as they arrive.

:::mission
Send progress events from the slow lookup node, then stream progress and the reply's tokens together, the way a chat
screen needs them.
:::
:::

:::step{type=history title="Response times people can bear"}
:::before{title="Waiting without a sign"}
A program that works silently looks exactly like a program that has stopped. People cannot tell the difference, and
assume the worst.
:::

In **1968** Robert B. Miller measured how people experience waiting at a computer, and Jakob Nielsen restated the limits in
**1993**: about **0.1 seconds** feels instant, about **1 second** keeps the user's train of thought, and after about
**10 seconds** attention is lost unless the system shows progress. Teleprinters had always shown text as it came, one
character at a time. The web got a standard way to push events to a page with **Server-Sent Events** (**2006**), and in
**November 2022** ChatGPT made the word-by-word answer the normal face of a language model.

:::solved
**The first sign of life in well under a second**, and the answer readable while it is still being written.
:::

:::timeline
- **1968** Miller: response time and attention.
- **1993** Nielsen's limits: 0.1 s, 1 s, 10 s.
- **2006** Server-Sent Events.
- **2022** Answers that appear word by word.
:::

A Teletype Model 33, the terminal of countless early computers. It printed every answer one character at a time, as it arrived: streaming, at ten characters a second.

:::photo{src="/lesson-images/langgraph/teletype.webp" alt="A beige teleprinter with a round-key keyboard, a paper tape punch on its left and a paper roll holder above, on its own stand" credit="Dennis van Zuijlekom" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Teletype_Model_33_ASR_(1968)_(14689737122).png"}
A Teletype Model 33 ASR from 1968.
:::
:::

:::step{type=concept title="Progress from inside a node" file="18-streaming/stream.py" line="27-34"}
Any node can send its own events to the stream with a **stream writer**:

```python
from langgraph.config import get_stream_writer

def lookup(state):
    write = get_stream_writer()
    write({"progress": "finding your tickets"})
    ...
```

Whatever you pass to `write` comes out of `app.stream(..., stream_mode="custom")`, at the moment it is written, while the
node is still running. It is ignored when nobody streams `custom` (a plain `invoke`), so the node works the same either
way.
:::

:::step{type=task task=progress_events title="Your turn: progress from a node" file="18-streaming/stream.py" line="27-34"}
In `lookup`, add `write = get_stream_writer()`, then `write({"progress": "finding your tickets"})` at the start and
`write({"progress": f"found {len(found)}, checking the crew schedule"})` after the tickets are found.

Press **Check**.
:::

:::step{type=concept title="Several stream modes at once" file="18-streaming/stream.py" line="51-56"}
`stream_mode` can be a list; then each item is a `(mode, chunk)` pair:

| Mode | Each chunk | Use it for |
|---|---|---|
| `"values"` | the whole state after each step | debugging, simple screens |
| `"updates"` | `{node: its update}` after each step | following the steps (as in most chapters) |
| `"custom"` | whatever a node passed to its stream writer | progress, partial results |
| `"messages"` | `(message chunk, metadata)` for every token a model produces, in any node | showing the reply as it is written |

`"messages"` works even though the node calls `model().invoke(...)`: LangGraph asks the model to stream underneath. The
metadata says which node the tokens came from (`meta["langgraph_node"]`), so the screen shows only the reply node's words,
not those of a classifier or a checker running elsewhere in the graph.

:::diagram{name="lg-stream"}
Progress events arrive during the lookup; tokens start arriving as soon as the model starts writing.
:::
:::

:::step{type=task task=stream_tokens title="Your turn: the reply token by token" file="18-streaming/stream.py" line="51-56"}
Finish `events(app, phone)`: loop over `app.stream({"phone": phone}, stream_mode=["custom", "messages"])`. For
`"custom"`, `yield "progress", chunk["progress"]`; for `"messages"`, `message, meta = chunk`, and
`yield "token", message.content` when `meta["langgraph_node"] == "reply"` and the content is not empty.

```bash run
cd /workspace/18-streaming && python main.py
```

Press **Check**.
:::

:::step{type=try title="What the citizen's screen would show"}
```text
$ python main.py
[0.00s] ... finding your tickets
[0.50s] ... found 2, checking the crew schedule
[2.22s] first token
For| ticket| T|-|447|1|,| the| East| Zone| Crew| |2| has| been| assigned| to| address| the| no| water| issue| and| will| be| working| on| it| Wednesday| from| |8|:|00| to| |11|:|00|.| Regarding| ticket| T|-|447|5|,| a| water| sample| has| been| taken| by| the| health| team|,| and| the| lab| results| are| expected| by| Wednesday| at| |18|:|00|.|
[3.73s] done, 72 chunks
```

Each `|` marks where one chunk ended. The tokens are the model's own pieces: "T", "-", "447", "1" for a ticket number,
a space glued to the front of most words.

Read the times. The first sign of life came at **0.00 s**, and the second at 0.50 s. The model call started at about
1.0 s; its first token arrived at **2.22 s**, and the last at **3.73 s**. Without streaming the citizen would see nothing
for 3.73 seconds; with it, the longest silence is the 1.7 seconds between the second progress event and the first
token (a third event, "writing your reply", would cut that too), and the reply can be read while it is written. The work
took exactly as long as before.
:::

:::step{type=predict title="Guess first"}
:::question
You call `app.invoke({"phone": "98220"})` on this graph, with the stream writer still in `lookup`. What happens to the
progress events?
:::
- [ ] invoke fails
- [x] Nothing: with no one streaming "custom", the writer's events are dropped, and the result is the same
- [ ] They are added to the state
:::explain
Stream writers only matter to a caller that asks for the custom stream.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why filter tokens by `meta["langgraph_node"] == "reply"`?
:::
- [x] Other nodes may call models too (a classifier, a checker), and their tokens are not for the citizen
- [ ] The messages mode needs a filter
- [ ] To make it faster
:::explain
In chapter 14's graph, a checker's labels would otherwise appear on the citizen's screen.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What did streaming change about the run's total time?
:::
- [ ] It halved it
- [x] Nothing: it changed what the citizen sees while waiting
- [ ] It made it longer
:::explain
Streaming is about perceived waiting: the first visible sign of progress, and reading while the model writes.
:::
:::

:::step{type=deep-dive title="Go deeper: streaming to a real screen"}
**To the browser.** A web server turns these events into Server-Sent Events or websocket messages; chapter 21's server
does it for you, and its client library streams the same modes.

**Async.** `async for mode, chunk in app.astream(...)` does the same inside an async web framework, without blocking
other requests.

**Subgraphs.** Add `subgraphs=True` to see events from inside subgraphs too, each with its namespace (chapter 16).

**Tokens are not words.** Never split or count on tokens in the screen code; show them as they come.
:::

:::step{type=recap}
You can now:

- send progress events from inside a node with `get_stream_writer`;
- stream several modes at once and tell them apart;
- show a model's reply token by token, only from the node that talks to the citizen;
- measure what streaming changes: time to the first sign of life, not total time.

Next, chapter 19: the Functional API, the same durable machinery in plain Python functions.

:::photo{src="/lesson-images/langgraph/lg-18-notes.webp" alt="Handwritten notes about streaming: get_stream_writer() = progress; custom + messages together; only the reply node's tokens; same total time; first sign of life: 0.00 s" ai="true"}
One page of notes for this chapter.
:::
:::
