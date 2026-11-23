:::step{type=story title="One interface for every model"}
Sahyadri Rail's IT team has a worry. Today Setu uses OpenAI. Next year a cheaper model may appear, or the railway may
want a model it can run on its own servers, or a regulator may want passenger data kept in India. With the OpenAI SDK
woven through the code, every change of model would be a rewrite.

Java developers have solved this problem before: JDBC lets the same code talk to Postgres, MySQL or Oracle, because the
code depends on an interface and a driver does the rest. **LangChain4j** does the same for AI. Your code depends on
interfaces like `ChatModel`; a provider module (`langchain4j-open-ai`, `langchain4j-ollama` and twenty more) does the
rest. From this chapter to the end of the course, Setu is built on it.

:::mission
Build Setu's first LangChain4j model, then give it its instructions with a system message.
:::
:::

:::step{type=history title="LangChain4j: built for Java, not ported to it"}
In **October 2022**, a month before ChatGPT, Harrison Chase released **LangChain**, a Python library for "chaining"
calls to language models with prompts, memory and tools. It grew explosively, and in early 2023 Python and JavaScript
developers had a toolbox for AI applications while Java developers had raw HTTP calls.

:::before{title="Java, left out"}
Most of the world's business software runs on the JVM: banks, railways, insurers, retailers. In 2023 those teams had
to write their own glue for every model and every vector database, or move AI work to Python services beside their
Java systems.
:::

LangChain4j started in **early 2023** to fix that, led by Dmytro Liubarskyi. Despite the name, it is not a port of the
Python library: it was designed for Java from the start, with interfaces, builders, annotations, POJOs and integrations
for **Spring Boot**, **Quarkus** (built with Red Hat), **Helidon** and **Micronaut**. Its 1.0 release in **2025**
promised a stable core API; this course uses **1.24**.

:::solved
**Unified APIs and a toolbox.** One API for 20+ model providers and 30+ embedding stores, so switching is a dependency
and a builder, plus ready-made pieces for memory, tools, retrieval, guardrails and agents.
:::

:::timeline
- **2022** LangChain for Python, in October; ChatGPT in November.
- **2023** LangChain4j begins.
- **2024** Integrations for Quarkus and Spring Boot mature.
- **2025** LangChain4j 1.0: a stable core.
- **2026** LangChain4j 1.24, the version in this course.
:::

:::usedby{title="Used for"}
- Help desks and assistants inside Java apps
- Search and question answering over company documents
- Data extraction from emails and forms
- Agents that call existing Java services
:::
:::

:::step{type=concept title="Two levels: ChatModel and AI Services"}
LangChain4j works on two levels, and this course uses both:

| Level | What you use | When |
|---|---|---|
| **Low level** | `ChatModel`, `UserMessage`, `SystemMessage`, `AiMessage`, `ChatRequest`, `ChatResponse` | Full control; you write the glue |
| **High level** | **AI Services**: a Java interface you declare, which LangChain4j implements (chapter 13) | Most application code |

This part of the course stays low, so you see every piece. A `ChatModel` has a handful of `chat` methods:

```java
String chat(String userMessage);                  // the quickest way to try a model
ChatResponse chat(ChatMessage... messages);       // a system message, a user message, history...
ChatResponse chat(ChatRequest chatRequest);       // messages plus per-request parameters (chapter 10)
```

A `ChatResponse` holds an `AiMessage` (the answer: `aiMessage().text()`) and metadata: the token usage and the
finish reason (chapter 12).

`OpenAiChatModel` is one implementation of `ChatModel`. Your methods return `ChatModel`, the interface, so the rest of
Setu never mentions OpenAI.

**Check yourself:** which line of Setu would change to move from OpenAI to a local Ollama model? (Only the one that
builds the model: `OllamaChatModel.builder()...` instead of `OpenAiChatModel.builder()...`. Chapter 24 does it.)
:::

:::step{type=example title="Worked example: a model builder" file="09-first-app/src/main/java/com/setu/Models.java" line="12-16"}
The getting-started page of the LangChain4j documentation builds a model like this (only to read; it is not in your
project):

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();
String answer = model.chat("Say 'Hello World'");
```

Setu needs one more line: `.baseUrl(baseUrl)`, so the requests go to the LabBox gateway instead of
`https://api.openai.com/v1`, and its model name is the gateway's alias, `"ai-chat"`.

The dependency is one module, in `pom.xml`, with its version from the LangChain4j BOM (bill of materials), so every
LangChain4j module you add later has a matching version:

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-open-ai</artifactId>
</dependency>
```
:::

:::step{type=task task=chat_model title="Your turn: Setu's first ChatModel" file="09-first-app/src/main/java/com/setu/Models.java" line="12-16"}
Finish `Models.chatModel(baseUrl, apiKey)`: build an `OpenAiChatModel` with `.baseUrl(baseUrl)`, `.apiKey(apiKey)` and
`.modelName("ai-chat")`, and return it.

Press **Check**.
:::

:::step{type=concept title="Messages, in LangChain4j"}
LangChain4j has a class for each role of chapter 7:

| Role | Class | Made with |
|---|---|---|
| system | `SystemMessage` | `SystemMessage.from("You are Setu...")` |
| user | `UserMessage` | `UserMessage.from(question)` |
| assistant | `AiMessage` | returned by the model: `response.aiMessage()` |

Pass them to `model.chat(...)` in order, system first. Models are trained to give the system message more weight than
the user's text, which is why instructions belong there. The documentation adds a warning worth remembering: never
let a user write into the system message, because then the user controls the instructions.

A language model has no memory between calls (chapter 4), so these messages are everything it knows about this
conversation. To continue a conversation, you would pass the earlier messages again:
`model.chat(system, firstQuestion, firstAnswer, secondQuestion)`. Chapter 17 lets a chat memory do that for you.
:::

:::step{type=task task=system_message title="Your turn: give Setu its instructions" file="09-first-app/src/main/java/com/setu/Desk.java" line="16-20"}
Finish `Desk.ask(model, question)`: call `model.chat(...)` with `SystemMessage.from(SYSTEM)` and
`UserMessage.from(question)`, and return the text of the answer's `AiMessage`.

```bash run
cd /workspace/09-first-app && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="With and without instructions"}
```text
$ mvn -q compile exec:java
Without instructions: Hello! I'm an AI language model created by OpenAI. I'm here to help answer your questions, provide information, and assist with various topics. What can I help you with today?
As Setu:              Hello! I am Setu, the help desk assistant for Sahyadri Rail. I'm here to assist you with any questions or information you may need about our railway services.
```

The same question, the same model, two different assistants. Without instructions the model introduces itself as a
general AI assistant; with the system message it is Setu, polite and short, as told. Nothing about the model changed:
only the messages. That is the first lesson of AI engineering: **most of the behaviour you want comes from what you
send**, and LangChain4j's job is to make sending the right things easy.
:::

:::step{type=predict title="Guess first"}
:::question
`Models.chatModel` returns `ChatModel`, not `OpenAiChatModel`. What does that buy Setu?
:::
- [ ] Nothing, it is the same object
- [x] The rest of the code depends only on the interface, so the provider can change in one place
- [ ] Faster answers
:::explain
It is the same object at run time, but the code that uses it cannot depend on anything OpenAI-specific. Swapping
providers becomes a one-method change, and tests can pass in a fake model.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where should Setu's instructions ("You are Setu... answer in three sentences") go?
:::
- [x] In a SystemMessage, first
- [ ] Appended to every user question
- [ ] In the model name
:::explain
The system message is where models expect instructions, and it keeps them separate from the passenger's text.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does the LangChain4j BOM in `pom.xml` do?
:::
- [ ] It downloads models
- [x] It fixes the versions of all LangChain4j modules, so they always match
- [ ] It replaces the Spring Boot parent
:::explain
With the BOM imported, you add modules without versions and they all come from the same release. Mixing module
versions is a classic source of strange errors.
:::
:::

:::step{type=deep-dive title="Go deeper: what else ChatModel gives you"}
**Retries and timeouts.** `OpenAiChatModel.builder().timeout(Duration.ofSeconds(30)).maxRetries(2)` handles the
production concerns of chapter 7.

**Logging.** `.logRequests(true).logResponses(true)` prints every request and response, the fastest way to see what
LangChain4j actually sent (chapter 26 adds proper observability).

**Async.** `model.chatAsync(request)` returns a `CompletableFuture<ChatResponse>` (experimental in 1.24).

**Other model types.** `EmbeddingModel` (chapter 22), `ImageModel`, `ModerationModel` and `ScoringModel` follow the
same pattern: an interface, and a provider module per company.
:::

:::step{type=recap}
You can now:

- explain why LangChain4j exists and its two levels, `ChatModel` and AI Services;
- build an `OpenAiChatModel` for any base URL and model name, behind the `ChatModel` interface;
- send a system message and a user message and read the `AiMessage`;
- explain why behaviour comes mostly from the messages you send.

Next, chapter 10: the knobs. Temperature, answer length, and parameters per request.

:::photo{src="/lesson-images/langchain4j/l4j-09-notes.webp" alt="Handwritten notes about the first LangChain4j app: one API, many models; ChatModel is an interface; SystemMessage first, then UserMessage; the answer is aiMessage().text(); behaviour comes from the messages" ai="true"}
One page of notes for this chapter.
:::
:::
