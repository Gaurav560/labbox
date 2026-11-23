:::step{type=story title="Two seconds of nothing"}
Sahyadri Rail put Setu on a test page and watched real passengers use it. They typed a question, pressed Enter, and
stared at an empty box for two or three seconds. Some pressed Enter again. Some left. The answer was good; the wait
felt broken.

ChatGPT never feels like that, because its answers appear word by word while the model is still writing. Chapter 6
explained why that is possible: a model produces one token at a time. **Streaming** sends each piece to you as soon as
it exists, so the first words appear in under a second, and the passenger reads while the rest arrives.


Text that arrives a piece at a time is older than chat. Teleprinters such as the **Teletype Model 33** (1963) printed each character the moment it came down the line, about ten a second, and early computer users read every answer that way.

:::photo{src="/lesson-images/langchain4j/teletype-model-33.webp" alt="A 1975 Altair 8800 computer with a row of switches and lights, next to a beige Teletype Model 33 with a keyboard and a roll of paper" credit="Tim Colegrove" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AAltair_8800_and_Model_33_ASR_Teletype.jpg"}
An Altair 8800 and a Teletype Model 33, which printed output one character at a time.
:::
:::mission
Stream an answer piece by piece with a `StreamingChatModel`, then make a streaming AI Service that returns a
`TokenStream`.
:::
:::

:::step{type=concept title="A streaming model and its three callbacks"}
For streaming, LangChain4j has a separate interface, `StreamingChatModel`, built like the chat model:

```java
StreamingChatModel model = OpenAiStreamingChatModel.builder()
        .baseUrl(baseUrl).apiKey(apiKey).modelName("ai-chat").build();
```

Its `chat` method returns nothing; instead you give it a **handler** with callbacks, and LangChain4j calls them as
pieces arrive, on another thread:

| Callback | When | Typical job |
|---|---|---|
| `onPartialResponse(String)` | Each new piece of text (often one token) | Show it on screen |
| `onCompleteResponse(ChatResponse)` | Once, when the answer is complete | Save it; read the token usage |
| `onError(Throwable)` | If anything fails | Tell the user, log it |

Because the callbacks happen later, on another thread, your method cannot simply `return` the answer. The standard
Java tool for "a result that arrives later" is `CompletableFuture`: create one, complete it in `onCompleteResponse`
(or `completeExceptionally` in `onError`), and return it. The caller can then wait with `get()`, or attach more work.

Underneath, the server keeps the HTTP response open and sends lines of **Server-Sent Events**: `data: {...one
piece...}`, again and again, ending with `data: [DONE]`.

:::diagram{name="l4j-streaming"}
The first piece arrives after 905 ms and the passenger starts reading; the whole answer is complete after 2103 ms.
:::
:::

:::step{type=example title="Worked example: a handler for printing" file="16-streaming/src/main/java/com/setu/Streams.java" line="26-31"}
For quick experiments, LangChain4j has a one-line handler (only to read; it is not in your project):

```java
import static dev.langchain4j.model.LambdaStreamingResponseHandler.onPartialResponse;

model.chat("Tell me about the Bhor Ghat", onPartialResponse(System.out::print));
```

It prints each piece as it arrives and ignores the end and errors, which is exactly why it is only for experiments.
Your task writes the full handler, an anonymous class implementing `StreamingChatResponseHandler`:

```java
model.chat(question, new StreamingChatResponseHandler() {
    @Override
    public void onPartialResponse(String partialResponse) { ... }
    @Override
    public void onCompleteResponse(ChatResponse completeResponse) { ... }
    @Override
    public void onError(Throwable error) { ... }
});
```
:::

:::step{type=task task=stream_tokens title="Your turn: stream with a handler" file="16-streaming/src/main/java/com/setu/Streams.java" line="26-31"}
Finish `Streams.stream(model, question, onToken)`: create a `CompletableFuture<ChatResponse>`, call
`model.chat(question, handler)` with a handler that passes each partial response to `onToken`, completes the future in
`onCompleteResponse`, and completes it exceptionally in `onError`. Return the future.

Press **Check**.
:::

:::step{type=concept title="Streaming AI Services: TokenStream" file="16-streaming/src/main/java/com/setu/StreamingAssistant.java" line="7-11"}
An AI Service streams when its method returns `TokenStream`:

```java
public interface StreamingAssistant {
    @SystemMessage(fromResource = "setu-system.txt")
    TokenStream chat(String question);
}
```

Create it with a `StreamingChatModel`: `AiServices.create(StreamingAssistant.class, streamingModel)`. Calling `chat`
does **not** call the model yet; it returns a `TokenStream`, a description of the stream you can attach callbacks to,
in a fluent style:

```java
setu.chat(question)
        .onPartialResponse(...)
        .onCompleteResponse(...)
        .onError(...)
        .start();      // nothing happens until start()
```

Forgetting `start()` is the classic mistake: everything compiles, and nothing ever arrives.
:::

:::step{type=task task=token_stream title="Your turn: a streaming AI Service" file="16-streaming/src/main/java/com/setu/Streams.java" line="33-37"}
Finish `Streams.ask(setu, question, onToken)`: call `setu.chat(question)`, pass partial responses to `onToken`,
complete a `CompletableFuture<String>` with the answer's text when complete (or exceptionally on an error), call
`start()`, and return the future.

```bash run
cd /workspace/16-streaming && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Watching the model write"}
```text
$ mvn -q compile exec:java
[Tr][ains][ slow][ down][ on][ a][ g][hat][ due][ to][ the][ steep][ gradient][,][ which][ increases][ the][ risk][ of][ derail][ment][ and][ requires][ more][ controlled][ braking][ to][ maintain][ safety][.][ Additionally][,][ the][ reduction][ in][ speed][ helps][ manage][ the][ train]['s][ momentum][ and][ ensures][ the][ safety][ of][ passengers][ and][ cargo][ while][ navigating][ the][ challenging][ terrain][.]
56 pieces; first after 905 ms, all after 2103 ms
Sahyadri Rail operates scenic trains connecting Pune, Lonavala, Karjat, and Ratnagiri. We offer a range of services including express and local trains. For specific schedules and routes, please check our official website.
(221 characters)
```

The brackets show each piece exactly as it arrived: mostly one token each (`[ g][hat]` is the word "ghat" split by the
tokenizer, as in chapter 4). The numbers are the point of this chapter: the **first piece arrived after 905 ms**, the
whole answer after 2103 ms. Without streaming, the passenger would have stared at an empty box for over two seconds;
with it, they start reading in under one. The total time is the same; the wait you **feel** is less than half.
:::

:::step{type=predict title="Guess first"}
:::question
Does streaming make the whole answer arrive sooner?
:::
- [ ] Yes, streaming makes the model faster
- [x] No: the total time is about the same, but the first words appear much sooner
- [ ] No, it makes everything slower
:::explain
The model writes at the same speed either way. Streaming changes when you see the words: time to first token is what
users feel, total time is what the model needs.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Your streaming AI Service compiles and runs, but nothing ever prints. What did you forget?
:::
- [x] start() on the TokenStream
- [ ] The system message
- [ ] A bigger maxTokens
:::explain
A TokenStream is only a description until start() is called.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where do you read the token usage of a streamed answer?
:::
- [ ] In each partial response
- [x] In the ChatResponse given to onCompleteResponse
- [ ] It is not available when streaming
:::explain
The complete response carries the metadata of chapter 12, so streaming costs nothing in observability.
:::
:::

:::step{type=deep-dive title="Go deeper: streaming in a web app"}
**To the browser.** A Spring controller can return the tokens as Server-Sent Events (`SseEmitter`, or a `Flux<String>`
from an AI Service method with the reactive module), and the page appends each piece as it arrives.

**Threads.** Callbacks run on LangChain4j's HTTP threads. Do quick work there (print, send to a socket); hand anything
slow to your own executor.

**Cancelling.** If the passenger closes the page, stop paying for tokens nobody will read: LangChain4j 1.24 lets a
handler cancel the stream (`StreamingHandle.cancel()`).

**Errors mid-stream.** A connection can drop after half an answer. Decide what the user sees: the half answer with a
note, or a retry.
:::

:::step{type=recap}
You can now:

- stream an answer with a `StreamingChatModel` and a `StreamingChatResponseHandler`;
- return a result that arrives later with `CompletableFuture`;
- build a streaming AI Service that returns a `TokenStream`, and remember `start()`;
- explain time to first token, and why streaming feels faster without being faster.

Next, chapter 17: memory. Setu remembers what each passenger said earlier in the conversation.

:::photo{src="/lesson-images/langchain4j/l4j-16-notes.webp" alt="Handwritten notes about streaming: answers arrive token by token; first words in under a second; a handler has partial, complete and error; TokenStream needs start(); same total time, less waiting" ai="true"}
One page of notes for this chapter.
:::
:::
