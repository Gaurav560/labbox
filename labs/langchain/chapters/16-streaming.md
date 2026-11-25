:::step{type=story title="Four seconds of silence"}
An agent takes longer than a single model call: chapter 10's question needed two model calls and two tools. In the
co-op's test app that meant four seconds of an empty screen, and members pressed the button again, starting a second
run, paying twice.

Chapter 8 streamed a model's words. An agent can stream more: **what it is doing** ("looking up the tomato rate...")
the moment each step finishes, and then its **answer**, word by word. LangChain agents stream in several **modes**, and
you choose what to show.

:::mission
Report each step of an agent's run as it finishes, then stream only the answer's words, leaving tool calls and results
out of the text.
:::
:::

:::step{type=history title="Progress you can see"}
:::before{title="Waiting blind"}
Early programs simply went quiet while they worked. Nobody could tell a slow program from a stuck one.
:::

In **1985** Brad Myers, a computer scientist, published a study of **percent-done progress indicators** (bars that show
how much of a job is done): people strongly preferred programs that showed their progress. Progress bars, spinners
and "typing..." indicators followed everywhere. Agents brought the idea back with a twist: their progress is a list of
**steps** ("searching", "calling a tool", "writing"), which is exactly what LangGraph's streaming reports.

:::solved
**A wait that explains itself.** Members see that something is happening, and what, so they do not press again.
:::

:::timeline
- **1985** Myers: people prefer programs that show their progress.
- **2024** Agent frameworks stream their steps.
:::
:::

:::step{type=concept title="Stream modes" file="16-streaming/streaming.py" line="13-20"}
`agent.stream(input, stream_mode=...)` yields pieces of the run as they happen:

| Mode | Yields | Use it to |
|---|---|---|
| `"updates"` | after each step: `{step name: {"messages": [new messages]}}` | show progress: "asks for storage_cost" |
| `"messages"` | each token of each model call: `(message_chunk, metadata)` | show the answer as it is written |
| `"values"` | after each step: the whole state | debugging |
| `"custom"` | whatever a tool sends with `runtime.stream_writer` | a tool's own progress |

The step names of a `create_agent` agent are `model` and `tools`, the two nodes of its graph (chapter 11). You can ask
for several modes at once, `stream_mode=["updates", "messages"]`, and then each item is a `(mode, data)` pair.
:::

:::step{type=task task=stream_steps title="Your turn: report each step" file="16-streaming/streaming.py" line="13-20"}
Finish `steps(agent, question, on_line)`:

1. Loop over `agent.stream({"messages": [...]}, stream_mode="updates")`. Each item is a dict `{step: update}`.
2. For each new message in `update["messages"]`: if it has tool calls, make one line `f"{step}: asks for {name}"` per
   call; otherwise one line `f"{step}: {type(message).__name__}"`.
3. For every line: add it to `lines` **and** call `on_line(line)` straight away.
4. Return `lines`.

The usual slip: calling `on_line` only at the end, after the loop. The lines are right, but they all appear at once:
no progress to show (it happened to us, below).

Press **Check**.
:::

:::step{type=concept title="Only the answer's words" file="16-streaming/streaming.py" line="23-29"}
With `stream_mode="messages"` you get every token of every model call. In an agent that includes the model's tool-call
turns (chunks with no text, only tool-call pieces) and, with some models, other model calls inside tools. For the
member's screen you want only the text of the `model` step:

```python
for chunk, metadata in agent.stream(..., stream_mode="messages"):
    if metadata["langgraph_node"] == "model" and chunk.content:
        print(chunk.content, end="")
```

`metadata` tells you where each chunk came from: the node (`langgraph_node`), the step number, and more.
:::

:::step{type=task task=stream_answer_text title="Your turn: stream the answer" file="16-streaming/streaming.py" line="23-29"}
Finish `answer_text(agent, question, on_piece)`:

1. Loop: `for chunk, metadata in agent.stream(..., stream_mode="messages"):`.
2. Keep a chunk only if `metadata["langgraph_node"] == "model"` and `chunk.content` is non-empty text.
3. Call `on_piece(chunk.content)` for it, and keep it in a list.
4. Return the pieces joined.

The usual slip: no filter on the node. Then a model with tools in its run can show pieces that are not the answer.

```bash run
cd /workspace/16-streaming && python main.py
```

Press **Check**.
:::

:::step{type=try title="Progress, then words"}
A real run (in two more runs on 25 November the tool requests came after 2.0 and 1.5 seconds and the answers at 3.6
and 3.1 seconds; the times depend on the network and the provider):

```text
$ python main.py
 2.35s  model: asks for storage_cost
 2.35s  model: asks for mandi_price
 2.35s  tools: ToolMessage
 2.35s  tools: ToolMessage
 3.95s  model: AIMessage

The storage cost for 30 crates of tomatoes for 6 days is ₹360. The current mandi rate for tomatoes is ₹1200 per quintal.

120 characters in 3.99s
```

The first run shows the shape of the agent's work. After 2.35 seconds the model asked for both tools; the tools ran
almost instantly (the same 2.35); the answer came at 3.95. A screen can say "looking up the storage charge and the
tomato rate..." for most of the wait.

The second run (the same question again) streamed only the answer's words, which appeared as they were written: no
tool calls, no `360` from the `ToolMessage` leaking into the text.

When we first wrote `steps`, it collected the lines and returned them at the end, and all five lines printed at the same
moment, after 4.01 seconds: correct, and useless for a progress display. Streaming only helps if each piece is used as
soon as it arrives; that is why `steps` takes `on_line`.
:::

:::step{type=predict title="Guess first"}
:::question
With `stream_mode="messages"` and no filter, what would the member's screen show for a run with tool calls?
:::
- [x] Possibly empty or odd pieces from the tool-calling turn mixed in, depending on the model
- [ ] Exactly the same as with the filter
- [ ] Nothing at all
:::explain
"messages" streams every model call. Filtering by node and by text keeps only the answer.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which mode tells you that the agent asked for `mandi_price`?
:::
- [x] `"updates"`
- [ ] `"custom"`
- [ ] None: tool calls are hidden
:::explain
Each update carries the new messages of a finished step, including the model's tool calls.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does streaming steps reduce double clicks?
:::
- [ ] It makes the agent faster
- [x] The member sees the run is working, so they do not start a second one
- [ ] It blocks the button
:::explain
Same speed, better wait: the lesson of progress indicators since 1985.
:::
:::

:::step{type=deep-dive title="Go deeper: event streaming"}
**Event streaming.** Agents also have `agent.stream_events(...)`: one stream of typed events (messages, tool calls,
state) that frontends can read directly. In the lab's LangGraph (1.2.24) it accepts `version="v1"`, `"v2"` (the default)
or the newer `"v3"`.

**Async.** `astream` does the same with `async for`, so a web server (chapter 27) can stream to many members at once,
sending each piece as a Server-Sent Event (chapter 8).

**Custom progress.** A slow tool can report its own progress: `runtime.stream_writer({"progress": "checking 3 markets"})`
appears in the `"custom"` mode.
:::

:::step{type=recap}
You can now:

- choose a stream mode: updates, messages, values, custom;
- report each step of an agent's run as it finishes;
- stream only the answer's words, filtered by node;
- use each piece as soon as it arrives, after seeing what happens when you do not.

That ends Part 3. Next, chapter 17: documents. The co-op's rule book, loaded and cut into pieces Navin can search.

:::photo{src="/lesson-images/langchain/lc-16-notes.webp" alt="Handwritten notes about streaming an agent: An agent run can be streamed step by step and word by word. updates reports each finished step: model or tools. messages streams the tokens of every model call. Keep only text from the model node for the member's screen. Use each piece at once, or it is no progress at all. In our runs the tools were asked for after about 1.5 to 2.4 seconds." ai="true"}
One page of notes for this chapter.
:::
:::
