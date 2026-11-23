:::step{type=story title="Setu goes live"}
Twenty-nine chapters ago, Setu was an idea: a help desk for Sahyadri Rail that answers passengers kindly and never
invents a train. Since then you have given it every piece: a model behind a gateway, a system message, memory,
tools for fares and dates, the railway's rule book, guardrails on the way in and out, and a listener that counts
every token.

Now they become one application. The railway's website will call one endpoint, `POST /chat`, and every answer will
say which rule-book files it came from, so the staff can check it. This is the app the operations team will run.

:::mission
Index the rule book when the app starts, and return every answer with its sources, in a Spring Boot app that wires
everything else by itself.
:::
:::

:::step{type=history title="The ideas inside Setu"}
:::before{title="A chatbot in 2016"}
A help-desk bot in 2016 was a decision tree: buttons, keywords, and "Sorry, I did not understand" for everything
else.
:::

Every part of Setu comes from the last few years, and you have met each one:

| Year | Idea | Where Setu uses it |
|---|---|---|
| 2017 | The transformer | The model itself (chapter 6) |
| 2020 | Retrieval-augmented generation | The rule book (chapter 23) |
| 2022 | Prompt injection named; ReAct | Guardrails (25), agents (27) |
| 2023 | Function calling in OpenAI's API (June); LangChain4j begins | Tools (19), the whole course |
| 2024 | The Model Context Protocol (November) | MCP clients and servers (20, 21) |
| 2025 | LangChain4j 1.0; its agentic module | AI Services, workflows, supervisors |

:::solved
**Ordinary engineering around a model.** None of these ideas makes the model smarter. Each one puts the model inside
Java code that supplies facts, limits what it can do, and checks what it says. That is what makes it safe to run.
:::

:::timeline
- **2017** Attention Is All You Need.
- **2020** RAG.
- **2023** Function calling; LangChain4j.
- **2024** MCP.
- **2025** LangChain4j 1.0 and agents.
:::
:::

:::step{type=concept title="What the starter wires for you" file="30-capstone/src/main/java/com/setu/SetuAssistant.java" line="15-23"}
`SetuAssistant` is an `@AiService` (chapter 18). With automatic wiring, the Spring Boot starter looks through the
application's beans and connects each one it finds:

| Bean | Made by | Becomes |
|---|---|---|
| `ChatModel` | the OpenAI starter, from `application.properties` | the model, with every `ChatModelListener` bean attached |
| `UsageLog` | `@Component` | the listener behind `GET /usage` (chapter 26) |
| `ChatMemoryProvider` | `MemoryConfig` | one memory per passenger (chapter 17) |
| `RailTools` | `@Component` | the `fare` and `nextDate` tools (chapter 19) |
| `ContentRetriever` | `KnowledgeConfig` | the rule book, searched on every question (chapter 23) |
| `EmbeddingModel` | the OpenAI starter, `ai-embed` | embeddings for indexing and search (chapter 22) |

The guardrails are named on the interface with `@InputGuardrails(QuestionLimit.class)` and
`@OutputGuardrails(NoPhoneNumbers.class)` (chapter 25). And the method returns `Result<String>`: the answer together
with the `sources()` that retrieval used.

Nothing in the controller knows about tools, memory or retrieval. It calls one method.
:::

:::step{type=task task=rules_store title="Your turn: index the rule book at start-up" file="30-capstone/src/main/java/com/setu/KnowledgeConfig.java" line="24-32"}
Finish the `rulesStore` bean: load the documents with `ClassPathDocumentLoader.loadDocuments("rules", new
TextDocumentParser())` (they are in `src/main/resources/rules`, so they travel inside the app), and ingest them into
a new `InMemoryEmbeddingStore` with an `EmbeddingStoreIngestor`: `DocumentSplitters.recursive(300, 30)`, the
embedding model, the store. Return the store.

This is chapter 23's ingestion, moved into a bean: it runs once, when the app starts.

Press **Check**.
:::

:::step{type=concept title="Answers with sources" file="30-capstone/src/main/java/com/setu/SetuController.java" line="36-39"}
`Result<String>` carries more than the text:

```java
Result<String> result = setu.chat(passenger, message);
result.content();          // the answer
result.sources();          // List<Content>: the rule-book pieces sent with the question
result.tokenUsage();       // the tokens of this call, tools included
result.toolExecutions();   // which tools ran, with their arguments and results
```

Each `Content` has a `textSegment()`, and its metadata has the `file_name` the loader recorded. Several pieces can
come from one file, so keep each file once:

```java
result.sources().stream()
        .map(Content::textSegment)
        .map(segment -> segment.metadata().getString("file_name"))
        .distinct()
        .toList();
```

A source list turns "trust me" into "according to `luggage.txt`". Staff can check an answer in seconds, and an empty
list says the answer came from the facts or the tools, not the rule book.
:::

:::step{type=task task=answer_with_sources title="Your turn: POST /chat with sources" file="30-capstone/src/main/java/com/setu/SetuController.java" line="36-39"}
Add `POST /chat` to `SetuController`: take a `ChatRequest` from the body, call `setu.chat(passenger, message)`, and
return a `ChatReply` with the passenger, `result.content()`, and the distinct file names of the sources.

Start the app in one terminal:

```bash run
cd /workspace/30-capstone && mvn -q spring-boot:run
```

and ask it in another:

```bash run
curl -s localhost:8080/chat -H 'Content-Type: application/json' -d '{"passenger": "meera", "message": "Can I bring my guitar to Karjat, and how much is my ticket?"}'
```

Press **Check**.
:::

:::step{type=try title="Careful: the guardrail that refused short questions"}
When we first ran this app, with chapter 25's `QuestionLimit` unchanged, a 59-character question got this:

```text
$ curl -s localhost:8080/chat -H 'Content-Type: application/json' -d '{"passenger": "meera", "message": "Can I take my bicycle to Karjat, and how much is my ticket?"}'
{"error":"That question is too long for me. Please ask it in at most 300 characters."}
```

Meanwhile "And for my son, he is 4?" went through. To find out why, we printed what the guardrail received when we
asked "Can I bring my guitar?" (22 characters):

```text
Can I bring my guitar?

Answer using the following information:
Musical instruments up to 1.5 metres travel free with their owner.
```

**Input guardrails run after retrieval.** The message they check is the augmented one: the question plus the
rule-book pieces found for it. Questions that matched the rule book grew past 300 characters; questions that matched
nothing stayed short and passed. A guard that worked perfectly in chapter 25 broke silently when RAG was added.

The capstone's `QuestionLimit` (already in your project) measures `request.requestParams().userMessageTemplate()`
instead: the message as the method received it, before anything was added. The lesson is bigger than this one
guardrail: **when you combine features, test them together**. Each one passing alone proves little about the whole.
:::

:::step{type=try title="Setu, live"}
```text
$ curl -s localhost:8080/chat -H 'Content-Type: application/json' -d '{"passenger": "meera", "message": "Can I bring my guitar to Karjat, and how much is my ticket?"}'
{"passenger":"meera","answer":"You can bring your guitar to Karjat for free, as it is under 1.5 metres. Your ticket from Pune to Karjat costs Rs 140.","sources":["luggage.txt"]} (HTTP 200)

$ curl -s localhost:8080/chat -H 'Content-Type: application/json' -d '{"passenger": "meera", "message": "And for my son, he is 4?"}'
{"passenger":"meera","answer":"Children under 5 travel free, so your son can travel without a ticket.","sources":[]} (HTTP 200)

$ curl -s localhost:8080/chat -H 'Content-Type: application/json' -d '{"passenger": "ravi", "message": "Please note my mobile, 98220 12345, for the wheelchair booking at Karjat."}'
{"passenger":"ravi","answer":"I can't note down your mobile number. However, you can book a wheelchair space for free at any ticket counter or on the website. Please remember to ask a platform attendant or call the station office 30 minutes before departure for assistance.","sources":["accessibility.txt"]} (HTTP 200)

$ curl -s localhost:8080/chat -H 'Content-Type: application/json' -d '{"passenger": "x", "message": "Tell me everything. Tell me everything. ... (20 times)"}'
{"error":"That question is too long for me. Please ask it in at most 300 characters."} (HTTP 400)

$ curl -s localhost:8080/usage
{"calls":4,"inputTokens":1968,"outputTokens":145}
```

(The long message is shortened here with "..."; the real one was 400 characters.)

Every part of the course in four requests:

1. **Tools and RAG together.** The guitar rule came from `luggage.txt`; the Rs 140 came from the `fare` tool. That
   one answer took two model calls, which is why `/usage` counts 4 calls for 3 answers.
2. **Memory.** "And for my son?" meant nothing alone; Meera's memory supplied the trip. No rule-book piece was
   needed, and the sources say so.
3. **Grounding.** Ravi's answer used the accessibility rules: free wheelchair spaces, the 30-minute call. The model
   declined to "note down" a number on its own; had it repeated it, `NoPhoneNumbers` would have removed it.
4. **Guardrails.** The 400-character message was refused with HTTP 400 and never reached the model.

And the bill: 1,968 input and 145 output tokens for three answers is about $0.00038, or $0.00013 an answer. At 10,000
questions a day, Setu costs about $1.30 a day in model calls.
:::

:::step{type=predict title="Guess first"}
:::question
The refund rules change next month. What has to change in Setu?
:::
- [ ] The Java code and the prompts
- [x] `rules/refunds.txt`, then a restart (the store is indexed at start-up)
- [ ] The model must be retrained
:::explain
Knowledge lives in documents, behaviour in code. With a persistent store (PGvector), you would re-index the one
file instead of restarting.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the controller never mention tools, memory or retrieval?
:::
- [ ] They are not used
- [x] The starter wires those beans into the AI Service, so the controller calls one method
- [ ] Spring Boot forbids it
:::explain
Each concern lives in one bean, tested on its own; the AI Service brings them together.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What did the guardrail bug teach?
:::
- [ ] Guardrails do not work with RAG
- [x] A guardrail sees the augmented message, so features must be tested together
- [ ] Questions must be under 60 characters
:::explain
Each feature worked alone. Only the combination failed, which only a test of the whole app could show.
:::
:::

:::step{type=deep-dive title="Go deeper: before real passengers"}
**A real store.** Replace `InMemoryEmbeddingStore` with `PgVectorEmbeddingStore` so the index survives restarts and
can be updated one file at a time.

**Memory that survives.** `MessageWindowChatMemory` keeps conversations in memory; a `ChatMemoryStore` backed by
Redis or a database keeps them across restarts and across several app instances.

**Streaming.** Return `TokenStream` or `Flux<String>` (chapter 16) so passengers see the answer as it is written.

**The checklist.** An eval of real questions before every deploy (26); rate limits and a daily budget per user;
guardrails tested together with RAG (this chapter); logs that leave out what passengers typed; and chapter 29's lesson:
never trust a number the model wrote that a tool could have computed.
:::

:::step{type=recap}
You can now:

- build a complete LangChain4j application in Spring Boot: model, memory, tools, RAG, guardrails and a listener;
- let `@AiService` wire beans automatically, and know which bean becomes which feature;
- return answers with their sources using `Result<String>`;
- test features together, and read the cost of a whole conversation.

That is the end of the course. You started with a single neuron in chapter 2; Setu now answers passengers from the
railway's own rules, with tools, memory and guardrails, and can tell you what every answer cost. Well done.

:::photo{src="/lesson-images/langchain4j/l4j-30-notes.webp" alt="Handwritten notes about the capstone: one app with tools, RAG and memory; guardrails and a listener; the starter wires the beans; Result gives the answer plus sources; test features together" ai="true"}
One page of notes for this chapter.
:::
:::
