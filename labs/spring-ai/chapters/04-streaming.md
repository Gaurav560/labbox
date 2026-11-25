:::step{type=story title="Two seconds of nothing"}
The lobby screen is live, and the museum's team watched visitors use it. A boy typed "How does a rainbow form?" and
then stared at an empty box. Two seconds passed. He pressed the button again. Then he walked away, a moment before the
answer appeared.

The model is not slow at thinking: it writes the answer **one token at a time**, and the first words exist after less
than a second. But `.call()` waits until the **last** token before handing anything over. Streaming hands over each
piece the moment it exists, so text starts to appear almost at once and grows as the visitor reads, exactly as in
ChatGPT.

Old news tickers printed the news onto paper tape as it arrived over the wire, letter by letter, long before the
whole story was in: the reader started reading at once.

:::photo{src="/lesson-images/spring-ai/ticker-tape.webp" alt="A brass and black stock ticker machine under glass, with a roll of paper tape beside its printing wheel" credit="H. Zimmer" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Edison_Stock_Telegraph_Ticker.jpg"}
A stock ticker: the news, printed as it arrives.
:::

:::mission
Stream Atlas's answers to the screen as they are written, and mark clearly when an answer is complete.
:::
:::

:::step{type=concept title="Waiting for all of it, or showing it as it comes"}
Here is what the boy's question costs in time, measured on this course's model, asking for about 120 words:

```text
$ curl -s -o /dev/null -w 'first byte %{time_starttransfer}s, all %{time_total}s\n' "localhost:8080/stream?q=Explain%20in%20about%20120%20words%20how%20a%20rainbow%20forms."
first byte 1.104249s, all 2.534571s
$ curl -s -o /dev/null -w 'first byte %{time_starttransfer}s, all %{time_total}s\n' "localhost:8080/stream?q=Explain%20in%20about%20120%20words%20how%20a%20rainbow%20forms."
first byte 0.634093s, all 1.968043s
```

With streaming, the first words arrived after 0.6 to 1.1 seconds; the whole answer took 2 to 2.5 seconds. (We ran it
three more times on 25 November: first byte 0.96 to 1.5 seconds, all 1.9 to 3.2 seconds. The numbers move with the
provider's load; the gap between them is what matters.) With
`.call()`, the visitor sees **nothing** for those full 2 to 2.5 seconds. The total is about the same; what changes is
how long the screen stays empty, and that is what people feel. A well-known rule of thumb in usability (Jakob Nielsen, 1993) says about one second is the limit for a person's flow
of thought to stay uninterrupted, and about ten seconds the limit for keeping their attention.

:::diagram{name="ai-streaming"}
One measured run (first byte 0.96 s, all 1.94 s). With call(), the same answer would appear all at once at the end.
:::

**Check yourself:** does streaming make the model write faster? (No. The same tokens take the same time. Streaming only
lets the visitor read the first ones while the rest are written.)
:::

:::step{type=concept title="Server-sent events and Flux"}
To send an answer in pieces over HTTP, the server keeps the response open and writes each piece when it is ready. The
simplest standard for that is **server-sent events** (SSE): a response of type `text/event-stream`, made of small
blocks of text, each ending with an empty line. Each block starts with `data:` and a space, then the piece:

```text
data: The

data:  sky

data:  is

```

(Two spaces before "sky": one belongs to the format, one is the token's own space before the word.)

Every browser understands it (with JavaScript's `EventSource`), and so does curl.

On the Java side, a stream of values that arrive over time is a **`Flux`**, from the Reactor library that Spring uses:
think of a `List` whose elements turn up one by one. Spring AI gives you the answer as a `Flux<String>`:

```java
Flux<String> pieces = chat.prompt()
        .user(q)
        .stream()       // instead of .call()
        .content();     // a Flux of text pieces
```

And Spring MVC knows what to do with a `Flux` returned from a controller: with `produces = text/event-stream`, it
writes each piece to the client as an SSE `data:` block the moment it arrives, and closes the response when the `Flux`
completes.
:::

:::step{type=task task=stream_answer title="Your turn: stream the answer" file="04-streaming/src/main/java/com/atlas/StreamController.java" line="32"}
In `04-streaming`, make `GET /stream?q=...` stream the model's answer instead of returning the placeholder:

1. `chat.prompt().user(q)` as before.
2. `.stream()` instead of `.call()`, then `.content()`.
3. Return that `Flux<String>`. The `produces = TEXT_EVENT_STREAM_VALUE` on the method is already there.

The usual slip: calling `.call().content()` and wrapping it in `Flux.just(...)`. It compiles, but the whole answer
arrives as one event after the full wait.

Run the app, then watch the answer arrive:

```bash run
cd 04-streaming && mvn -q -o spring-boot:run
```

```bash run
curl -sN "localhost:8080/stream?q=Why%20is%20the%20sky%20blue%3F"
```

(`-N` tells curl not to wait and collect the response: it prints every piece as it comes.) Press **Check**.
:::

:::step{type=try title="What the pieces look like"}
These are the first pieces of a real streamed answer (25 November):

```text
$ curl -sN "localhost:8080/stream?q=Why%20is%20the%20sky%20blue%3F" | head -12
data: The

data:  sky

data:  is

data:  blue

data:  because

data:  of

```

Each piece is about one token: a word, with its space in front. A web page joins them as they come; the visitor sees a
sentence grow. (Your own answer will be worded differently.)
:::

:::step{type=example title="Worked example: naming the events"}
A page that shows a streamed answer has one more question: **when is it finished?** When the stream closes, sure, but
a closed connection can also mean a network problem. Clear streams say it explicitly with a last event. SSE events can
have a **name**, given on an `event:` line:

```text
event:token
data:  blue

event:done
data: 

```

Spring builds such events with `ServerSentEvent`:

```java
ServerSentEvent.builder("Hello").event("greeting").build()
```

And a `Flux` can be turned into another `Flux` piece by piece with **`map`**, and extended with **`concatWith`**:

```java
Flux<String> words = Flux.just("Hello", " world");
Flux<String> shouted = words.map(w -> w.toUpperCase());           // "HELLO", " WORLD"
Flux<String> finished = shouted.concatWith(Flux.just("!"));       // "HELLO", " WORLD", "!"
```

`map` changes each element as it passes; `concatWith` adds more elements after the last one. Both work while the
elements are still arriving: nothing waits for the whole stream.
:::

:::step{type=task task=stream_events title="Your turn: token events and a done event" file="04-streaming/src/main/java/com/atlas/StreamController.java" line="39"}
Finish `GET /stream/events?q=...`: stream the answer as events named **`token`** (one per piece), and after the
last piece, send one event named **`done`**:

1. Stream the content as in the first task.
2. `.map(piece -> ServerSentEvent.builder(piece).event("token").build())`.
3. `.concatWith(Flux.just(ServerSentEvent.builder("").event("done").build()))` and return it.

The usual slips:

- Leaving out `.event("token")`: the events have no name, and a page listening for `token` events hears nothing.
- Building the `done` event inside `map`: the page then gets a `done` after every piece.

```bash run
curl -sN "localhost:8080/stream/events?q=Why%20is%20the%20sky%20blue%3F" | tail -9
```

Press **Check**.
:::

:::step{type=try title="The end of a stream"}
The last lines of a real stream (25 November):

```text
$ curl -sN "localhost:8080/stream/events?q=Why%20is%20the%20sky%20blue%3F" | tail -9
event:token
data:  time

event:token
data: !

event:done
data: 

```

A page listening with `EventSource` can now handle the two kinds separately: append each `token` to the answer box, and
on `done`, hide the "Atlas is typing" dots.
:::

:::step{type=predict title="Guess first"}
:::question
In `.stream().content().map(...)`, when does `map` run for the first piece?
:::
- [ ] After the whole answer has arrived
- [x] As soon as the first piece arrives
- [ ] Never: map only works on lists
:::explain
`Flux` operators work on each element as it flows past. That is what lets the first words reach the visitor while the
model is still writing the rest.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `curl` need `-N` to show a stream piece by piece?
:::
- [ ] Without it, curl refuses event streams
- [x] Without it, curl collects output in a buffer and prints it in larger chunks
- [ ] `-N` makes the server stream
:::explain
The server streams either way; `-N` turns off curl's own buffering so you see each piece arrive.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Streaming and `.call()` both take about 2.5 seconds for a long answer. What does streaming improve?
:::
- [x] How soon the visitor sees the first words
- [ ] The total time
- [ ] The cost in tokens
:::explain
Same tokens, same price, similar total time. Streaming shortens the empty wait, from the whole answer to the first
token, and that is what makes an assistant feel quick.
:::
:::

:::step{type=deep-dive title="Go deeper: what streaming changes in your code"}
**Usage arrives at the end.** When streaming, the token counts come with the last chunk, if the request asks for them
(`stream_options.include_usage` in OpenAI's format). The LabBox gateway always asks, so its log showed 96 tokens in
and 41 out for a streamed answer. Use `.stream().chatResponse()` instead of `.content()` to see every chunk's metadata.

**Errors arrive late too.** With `.call()`, a failure is an exception before anything is sent. With streaming, the
response may already have started when something fails; a `done` or `error` event lets the page tell "complete" from
"broken". `Flux` has `onErrorResume` for sending a friendly error event.

**Threads.** Spring MVC hands a returned `Flux` to an asynchronous response, so a waiting stream does not hold a
request thread. Applications that stream to thousands of people at once often use Spring WebFlux, built entirely on
`Flux` and `Mono`. With Java 21's virtual threads (`spring.threads.virtual.enabled=true`), plain blocking code scales
well too.

**WebSockets?** SSE sends in one direction, server to browser, over plain HTTP, through proxies and with automatic
reconnection. WebSockets are two-way, for chats where both sides send all the time. For streaming answers, SSE is the
usual choice; ChatGPT's API itself streams with SSE.
:::

:::step{type=recap}
You can now:

- explain why streaming makes an assistant feel fast: the first token instead of the last;
- stream an answer with `.stream().content()` and return the `Flux<String>` as `text/event-stream`;
- read server-sent events (`data:`, `event:`) and build named ones with `ServerSentEvent`;
- transform and extend a stream with `map` and `concatWith`, and mark the end with a `done` event.

Next, chapter 5: answers as data, so Atlas can plan a tour that the website shows as a real list of stops.

:::photo{src="/lesson-images/spring-ai/springai-04-notes.webp" alt="Sketchnote, Streaming answers (stream(), Flux and server-sent events): The model writes one token at a time. Streaming sends each piece as soon as it exists, so the screen is not empty while the rest is written. The flow: Question, .stream().content(), Flux of pieces, data: blocks, Words appear. What we measured: first words after about 1 second; the whole answer after about 2 seconds; same tokens, same price: only the wait changes; a done event says the answer is complete." ai="true"}
One page of notes for this chapter.
:::
:::
