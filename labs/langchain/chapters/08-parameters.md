:::step{type=story title="Steady answers, and no staring at an empty box"}
Two complaints came back from the first members who tried Navin. One asked the same question twice and got two
differently worded answers, and wondered which was right. Another waited for an answer with nothing on the screen,
decided the app was broken, and closed it a second before the answer appeared.

Both have simple fixes. **Model parameters** make answers steady and short: `temperature` (chapter 4's softmax knob)
and `max_tokens` (a ceiling on the answer's length, and so its cost). **Streaming** shows the answer as it is written,
one piece at a time, the way chat apps do: the model is no faster, but the wait feels much shorter.

:::mission
Build a model with a temperature of 0 and a 120-token ceiling, then stream an answer piece by piece and time the first
piece.
:::
:::

:::step{type=concept title="The parameters that matter" file="08-parameters/params.py" line="8-11"}
`init_chat_model` passes parameters to the model class, and they travel in the request:

| Parameter | What it does | Navin uses |
|---|---|---|
| `temperature` | How adventurous the next-token choice is (chapter 4) | 0: the same question gets (nearly) the same answer |
| `max_tokens` | The longest answer allowed; the model stops there | 120: a help desk answer, not an essay |
| `timeout`, `max_retries` | As in chapter 6 | defaults |
| `stop` | Text that ends the answer when produced | not needed |

```python
init_chat_model("openai:ai-chat", temperature=0, max_tokens=120)
```

Two honest caveats. Temperature 0 makes answers **steady, not guaranteed identical**: providers do not promise it,
and tiny differences between runs still happen. And a `max_tokens` ceiling cuts an answer mid-sentence if it is too
low; the reply then says why (`finish_reason: length`).
:::

:::step{type=task task=steady_model title="Your turn: a steady model" file="08-parameters/params.py" line="8-11"}
Finish `steady_model()`: return `init_chat_model("openai:ai-chat", temperature=0, max_tokens=120)`.

Press **Check**.
:::

:::step{type=history title="Pushing text to the browser"}
:::before{title="Ask, wait, then everything at once"}
On the early web a page asked the server for data and waited for the whole reply. A long answer meant a long blank
wait.
:::

**Server-Sent Events** (SSE), first drafted in **2004** for HTML5 and a W3C Recommendation since **2015**, let a server keep one HTTP
response open and send small messages through it as they become ready: lines of `data: ...`, one after another. Every
major model API streams answers this way. Each event carries the next few characters of the answer, and the last one
says `data: [DONE]`.

:::solved
**Time to first word.** The member starts reading as soon as the first token exists, instead of after the last.
:::

:::timeline
- **2004** Server-Sent Events drafted for HTML5.
- **2015** A W3C Recommendation.
- **2023** Streaming chat answers become the norm.
:::
:::

:::step{type=concept title="stream instead of invoke" file="08-parameters/params.py" line="14-17"}
Every LangChain chat model has `stream`, with the same input as `invoke`. Instead of one `AIMessage`, it yields
`AIMessageChunk`s as they arrive:

```python
for chunk in model.stream(messages):
    print(chunk.content, end="", flush=True)   # a few characters at a time
```

Chunks can be added together (`chunk1 + chunk2`) into one message, and the last chunk carries the token usage. Your
`stream_answer` takes an `on_piece` function, so the caller decides what to do with each piece: print it, send it to a
web page, or test it.
:::

:::step{type=task task=stream_tokens title="Your turn: stream the answer" file="08-parameters/params.py" line="14-17"}
Finish `stream_answer(model, question, on_piece)`: loop over `model.stream([...])` with the system message and the
question; call `on_piece(chunk.content)` for every chunk, and return all the pieces joined.

```bash run
cd /workspace/08-parameters && python main.py
```

Press **Check**.
:::

:::step{type=try title="Watching Navin write"}
```text
$ python main.py
[][On][ion][ prices][ rise][ in][ the][ mon][soon][ because][ heavy][ rains][ can][ damage][ the][ crops][.][ This][ leads][ to][ less][ supply][ in][ the][ market][.][ When][ supply][ is][ low][,][ prices][ go][ up][.][][][]

first piece after 769 ms, all 149 characters after 1157 ms
```

Each pair of brackets is one chunk, exactly as it arrived: mostly one token each (`[mon][soon]` is one word in two
tokens, as in chapter 2). The **first piece of text arrived after 769 ms**, the whole answer after 1157 ms: the member
starts reading in under a second instead of waiting for all of it.

Look at the edges too: an empty chunk `[]` first (the one that only says "the assistant is speaking") and three empty
ones at the end, which carry the finish reason and the token usage instead of text. Code that shows pieces must cope with empty
ones; `main.py` starts its timer only at the first piece that has text.
:::

:::step{type=predict title="Guess first"}
:::question
Does streaming make the whole answer arrive sooner?
:::
- [ ] Yes, it makes the model faster
- [x] No: the total time is about the same; the first words appear much sooner
- [ ] No, it makes everything slower
:::explain
The model writes at the same speed. Streaming changes when you see the words: time to first token is what people feel.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
An answer stops mid-sentence. What is the likely cause?
:::
- [ ] Temperature 0
- [x] `max_tokens` was reached (`finish_reason` is `length`)
- [ ] Streaming
:::explain
The ceiling cuts the answer. Raise it, or ask for shorter answers in the system message.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does Navin use temperature 0?
:::
- [ ] It is cheaper
- [x] Facts and rules should be answered the same way every time
- [ ] Streaming needs it
:::explain
Low temperature favours the most likely tokens: steady answers. Creativity is for other jobs.
:::
:::

:::step{type=deep-dive title="Go deeper: streaming in an app"}
**To a browser.** A web server (chapter 27) forwards each piece as its own Server-Sent Event, so the member's screen
fills in as Navin writes.

**Async streaming.** `astream` is the same with `async for`, so one server can stream to many members at once.

**Cost of a ceiling.** `max_tokens` is also a budget guard: one runaway answer cannot cost more than 120 output tokens.
:::

:::step{type=recap}
You can now:

- set temperature and `max_tokens`, and explain what each does to answers and cost;
- stream an answer with `model.stream` and handle every piece;
- measure time to first piece, from a real run;
- handle empty chunks at the start and end of a stream.

Next, chapter 9: the confident wrong answers from chapters 5 and 6, and what every answer costs.

:::photo{src="/lesson-images/langchain/lc-08-notes.webp" alt="Handwritten notes about parameters and streaming: temperature 0: steady answers; max_tokens: a ceiling; stream: piece by piece; First piece 769 ms; Empty chunks at the edges" ai="true"}
One page of notes for this chapter.
:::
:::
