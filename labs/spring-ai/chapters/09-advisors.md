:::step{type=story title="The same change, everywhere at once"}
Two requests arrive on the same morning. Mr. Kulkarni from finance wants a meter: how many model calls Atlas makes each
day, and how many tokens they use, for every endpoint. And the education team wants Atlas to answer in Marathi or Hindi
when a visitor picks a language on the screen.

You could add a few lines to every controller method. Atlas already has `/ask`, `/explain`, `/tour`, `/suggest` and
`/chat`, and it will have more. Copying the same lines into each one is how bugs are born: one endpoint is forgotten, one
counts twice.

You have already used the better way three times without writing one: session memory, and later retrieval and
guardrails, all work as **advisors**, code that wraps **every** call a `ChatClient` makes. This chapter writes two of
your own.

Canal locks work like a chain of advisors: a boat passes through each one in order, and each lock does one job to it
on the way up, and again on the way down. This flight of five locks lifts boats from Loch Ness at Fort Augustus, in
Scotland.

:::photo{src="/lesson-images/spring-ai/canal-locks.webp" alt="A flight of canal locks climbing between grassy banks and white railings, with stone houses and green hills behind" credit="Jim Osley" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Fort_Augustus_,_flight_of_locks,_Caledonian_Canal_-_geograph.org.uk_-_7480800.jpg"}
The flight of locks at Fort Augustus, Caledonian Canal.
:::

:::mission
Write an advisor that meters every model call and its tokens, and one that makes Atlas answer in the visitor's
language.
:::
:::

:::step{type=concept title="A chain around every call"}
When you call `chat.prompt()...call()`, the request does not go straight to the model. It passes through a **chain of
advisors**, in order, and the answer comes back through the same chain, in reverse:

:::diagram{name="ai-advisor-chain"}
The request passes through each advisor on the way to the model; the response passes back through them in reverse order.
:::

Each advisor can:

- **look at or change the request** before passing it on (add a system line, add retrieved documents, add history);
- **look at or change the response** on the way back (count tokens, log, check the answer);
- or **stop the chain** and answer by itself (a guardrail that refuses, a cache that already knows the answer).

The order is decided by `getOrder()`: lower numbers run first on the way in (and last on the way out). Spring AI's own
tool-calling loop and session memory are advisors in the same chain, at fixed orders.

The name comes from Spring itself: since 2004, Spring's aspect-oriented programming has used "advice" for code that runs
around a method call, the same idea used for transactions and security in every Spring app. Spring AI applies it to
model calls.

**Check yourself:** which kind of advisor could stop the chain and answer without calling the model? (A guardrail
refusing a question, or a cache returning a saved answer.)
:::

:::step{type=example title="Worked example: a CallAdvisor" file="09-advisors/src/main/java/com/atlas/UsageAdvisor.java" line="30"}
An advisor that wraps the whole call implements **`CallAdvisor`**. Its one important method receives the request and
the rest of the chain:

```java
@Override
public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
    long start = System.nanoTime();                       // before: on the way in
    ChatClientResponse response = chain.nextCall(request); // the rest of the chain, and the model
    long ms = (System.nanoTime() - start) / 1_000_000;    // after: on the way back
    log.info("model call took {} ms", ms);
    return response;
}
```

1. Everything before `chain.nextCall(request)` happens on the way in.
2. `chain.nextCall(request)` passes the request on, and returns the response once everything after this advisor
   (other advisors, then the model) has finished. **Forget it, and the model is never called.**
3. Everything after it happens on the way back, with the response in hand:
   `response.chatResponse().getMetadata().getUsage()` holds the tokens, as in chapter 3.

`getName()` gives the advisor a name for logs; `getOrder()` its place in the chain. Register it on the `ChatClient`
with `defaultAdvisors(...)`, and every call has it: the controller in `09-advisors` already does that.
:::

:::step{type=task task=usage_advisor title="Your turn: a token meter" file="09-advisors/src/main/java/com/atlas/UsageAdvisor.java" line="31"}
In `09-advisors`, finish `UsageAdvisor.adviseCall`: pass the request down the chain, then count the call and add the
response's **total tokens** to the meter.

```bash run
cd 09-advisors && mvn -q -o spring-boot:run
```

```bash run
curl -s -G localhost:8080/ask --data-urlencode "q=Why does the Foucault pendulum turn?"; echo
curl -s localhost:8080/meter; echo
```

Press **Check**.
:::

:::step{type=concept title="BaseAdvisor: before and after"}
Many advisors only need to change the request on the way in, or the response on the way out. **`BaseAdvisor`** splits
`adviseCall` into two simpler methods, and calls the chain for you:

```java
public class ReReadingAdvisor implements BaseAdvisor {
    @Override
    public ChatClientRequest before(ChatClientRequest request, AdvisorChain chain) {
        String q = request.prompt().getUserMessage().getText();
        return request.mutate()
                .prompt(request.prompt().augmentUserMessage(q + "\nRead the question again: " + q))
                .build();
    }

    @Override
    public ChatClientResponse after(ChatClientResponse response, AdvisorChain chain) {
        return response;
    }

    @Override
    public int getOrder() { return 0; }
}
```

(This one comes from Spring AI's own documentation: asking the model to read the question twice measurably improves its
reasoning on some tasks.) Two things to know:

- Requests and prompts are **immutable**: you never change them in place. `request.mutate()` gives a builder for a
  changed copy, and `prompt.augmentUserMessage(...)` or `prompt.augmentSystemMessage(...)` returns a new prompt with one
  message changed.
- An advisor gets per-request information through the **advisor context**: the controller sets it with
  `.advisors(a -> a.param("language", "Marathi"))`, and the advisor reads `request.context().get("language")`.
:::

:::step{type=task task=language_advisor title="Your turn: answer in the visitor's language" file="09-advisors/src/main/java/com/atlas/LanguageAdvisor.java" line="16"}
Finish `LanguageAdvisor.before`: when the request's context has a `language`, add the line `Answer in LANGUAGE.` to the
**end** of the system message (keep Atlas's own rules); without a language, change nothing.

`prompt.augmentSystemMessage(system -> ...)` takes a function from the current system message to a new one; a message's
`mutate().text(...).build()` makes the changed copy.

```bash run
curl -s -G localhost:8080/ask --data-urlencode "q=Why does the Foucault pendulum turn?" --data-urlencode lang=Marathi; echo
```

Press **Check**.
:::

:::step{type=try title="One question, three languages"}
With both advisors in place, the same question three times:

```text
$ curl -s -G localhost:8080/ask --data-urlencode "q=Why does the Foucault pendulum turn?"; echo
The Foucault pendulum turns because of the Earth’s rotation. As the pendulum swings back and forth, the ground beneath it moves, making it appear to change direction. This shows how the Earth spins on its axis.
$ curl -s -G localhost:8080/ask --data-urlencode "q=Why does the Foucault pendulum turn?" --data-urlencode lang=Marathi; echo
फोको पेंडुलम फिरण्याचे कारण म्हणजे पृथ्वीची फिरती. पेंडुलमचे दोर फिरत नाही, पण पृथ्वी चालू राहते आणि त्यामुळे पेंडुलमच्या हालचालीत बदल होतो. यामुळे तो फिरताना दिसतो.
$ curl -s -G localhost:8080/ask --data-urlencode "q=Why does the Foucault pendulum turn?" --data-urlencode lang=Hindi; echo
फौकोल्ट पेंडुलम इसलिए घूमता है क्योंकि यह पृथ्वी की घूर्णन के खिलाफ झूलता है। जैसे-जैसे पृथ्वी घूमती है, पेंडुलम का झूला पृथ्वी के सापेक्ष बदलता है। यह एक अद्भुत तरीका है पृथ्वी की गति को दिखाने का।
$ curl -s localhost:8080/meter; echo
{"tokens":486,"calls":3}
```

One line in the system prompt, added by one advisor, turned Atlas trilingual, and the meter counted all three calls
(486 tokens). A Marathi or Hindi speaker will spot that the wording is not perfect in places: smaller models are weaker
in Indian languages than in English, so test with native speakers before trusting a model in a language.
:::

:::step{type=predict title="Guess first"}
:::question
Your `UsageAdvisor` forgets to call `chain.nextCall(request)` and returns `null`. What happens to `/ask`?
:::
- [ ] Nothing changes: Spring AI calls the model anyway
- [x] The model is never called, and the call fails
- [ ] Only the meter stops working
:::explain
An advisor is part of the path to the model. Each one must pass the request on, unless it means to stop the chain and
answer itself (then it must return a real response).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two advisors have orders 0 and 100. Which sees the request first, and which sees the response first?
:::
- [x] Order 0 sees the request first; order 100 sees the response first
- [ ] Order 100 sees both first
- [ ] Order 0 sees both first
:::explain
The chain is like nested boxes: the outer advisor (lower order) is entered first and left last.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why use an advisor for the language line instead of adding it in each controller method?
:::
- [ ] Advisors are faster
- [x] One advisor applies to every call of the ChatClient, so no endpoint can be forgotten
- [ ] Controllers cannot change prompts
:::explain
Cross-cutting concerns (metering, logging, language, safety) belong in one place. The same reasoning made Spring's
`@Transactional` and security filters what they are.
:::
:::

:::step{type=deep-dive title="Go deeper: streaming advisors and recursive advisors"}
**Streaming.** `CallAdvisor` wraps `.call()`. For `.stream()`, implement `StreamAdvisor` too: `adviseStream` receives
and returns a `Flux<ChatClientResponse>`. To look at the whole streamed answer (for logging or metering),
`ChatClientMessageAggregator` collects the pieces without delaying them.

**Recursive advisors.** An advisor may call the rest of the chain more than once: Spring AI's tool-calling loop does
this (model, tool, model again), and so does the structured-output validation advisor of chapter 5 (ask, validate,
ask again with the error). Spring AI calls these **recursive advisors**; they need care, because every round costs a
model call.

**Built-in advisors you have met or will meet:** the session advisors (chapter 6), `SimpleLoggerAdvisor` (chapter
19), `QuestionAnswerAdvisor` and `RetrievalAugmentationAdvisor` (chapter 14), `SafeGuardAdvisor` (chapter 17), and
the tool-calling advisor that runs every chapter 7 tool.
:::

:::step{type=recap}
You can now:

- explain the advisor chain: requests go in through each advisor by order, responses come back in reverse;
- write a `CallAdvisor` that wraps every call, and pass the request on with `chain.nextCall(request)`;
- write a `BaseAdvisor` that changes the request with `mutate()` and `augmentSystemMessage(...)`;
- pass per-request data to advisors through the advisor context.

Next, chapter 10: the Model Context Protocol, so other AI applications can use Atlas's tools.

:::photo{src="/lesson-images/spring-ai/springai-09-notes.webp" alt="Handwritten notes about advisors: a chain around every call; chain.nextCall(request); BaseAdvisor: before + after; request.mutate(); lower order = outer" ai="true"}
One page of notes for this chapter.
:::
:::
