:::step{type=story title="Setu goes on the website"}
So far Setu has lived in `main` methods. Sahyadri Rail's website and its mobile app need something they can call over
the network: a web API that takes a passenger's message and returns Setu's answer, as JSON, with each passenger's
conversation kept apart.

Most Java services are Spring Boot applications, and LangChain4j ships **Spring Boot starters** for exactly this: they
build the `ChatModel` from `application.properties`, and turn an annotated interface into a Spring bean you can inject
anywhere. Everything you learned in chapters 13 to 17 carries over unchanged.

:::mission
Turn `SetuAssistant` into a Spring bean with `@AiService`, and expose it as `POST /chat`.
:::
:::

:::step{type=concept title="Two starters and four properties" file="18-rest-api/src/main/resources/application.properties" line="5-10"}
`pom.xml` has two LangChain4j starters, for Spring Boot 4:

| Starter | What it does |
|---|---|
| `langchain4j-open-ai-spring-boot4-starter` | Builds an `OpenAiChatModel` bean from `langchain4j.open-ai.chat-model.*` properties |
| `langchain4j-spring-boot4-starter` | Finds interfaces annotated `@AiService` and implements them as beans |

(The `-spring-boot4-starter` names are for Spring Boot 4; the same starters without the `4` are for Spring Boot 3.)

The model is configured, not built in code:

```properties
langchain4j.open-ai.chat-model.base-url=${OPENAI_BASE_URL}
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.chat-model.model-name=ai-chat
langchain4j.open-ai.chat-model.temperature=0.0
```

`${OPENAI_BASE_URL}` is read from the environment when the app starts, so the key still never appears in a file.
Every builder option from chapters 9 and 10 has a property: `timeout`, `max-retries`, `log-requests`, `max-tokens`.
:::

:::step{type=concept title="@AiService: an interface becomes a bean" file="18-rest-api/src/main/java/com/setu/MemoryConfig.java" line="10-17"}
With the starter, you annotate the interface and inject it; `AiServices.builder(...)` disappears:

```java
@AiService
public interface SetuAssistant {
    @SystemMessage(fromResource = "setu-system.txt")
    String chat(@MemoryId String passenger, @UserMessage String message);
}
```

At start-up the starter finds `@AiService` interfaces and builds each one with the beans it finds in the application:
the `ChatModel` (from the properties), a `ChatMemoryProvider` if there is one (here, `MemoryConfig` defines one per
passenger, the same lambda as chapter 17), and later tools and content retrievers. This is called **automatic wiring**.
When an application has several models, `@AiService(wiringMode = EXPLICIT, chatModel = "...")` names the beans to use.

Then any Spring component gets Setu through its constructor, like any other bean:

```java
public SetuController(SetuAssistant setu) {
    this.setu = setu;
}
```

If the annotation is missing, Spring has no `SetuAssistant` bean to give the controller and the application refuses
to start. The check tells you exactly that.
:::

:::step{type=task task=ai_service_bean title="Your turn: make Setu a bean" file="18-rest-api/src/main/java/com/setu/SetuAssistant.java" line="7-13"}
Annotate the `SetuAssistant` interface with `@AiService` (`dev.langchain4j.service.spring.AiService`).

Press **Check**.
:::

:::step{type=example title="Worked example: a JSON endpoint" file="18-rest-api/src/main/java/com/setu/SetuController.java" line="11-17"}
`SetuController` already has the request and reply shapes as records:

```java
public record ChatRequest(String passenger, String message) {
}

public record ChatReply(String passenger, String answer) {
}
```

A Spring endpoint that takes JSON and returns JSON is a method with two annotations. Here is a different one, only to
read (it is not in your project):

```java
@PostMapping("/feedback")
public Thanks feedback(@RequestBody Feedback feedback) {
    return new Thanks("Thank you, " + feedback.name());
}
```

`@RequestBody` turns the JSON body into the record; the record you return is turned back into JSON. The endpoint
itself is ordinary Java: the AI is just a method call on the injected bean.
:::

:::step{type=task task=chat_endpoint title="Your turn: POST /chat" file="18-rest-api/src/main/java/com/setu/SetuController.java" line="25-27"}
In `SetuController`, add `POST /chat`: take a `ChatRequest` from the request body, call
`setu.chat(request.passenger(), request.message())`, and return a `ChatReply` with the passenger and the answer.

```bash run
cd /workspace/18-rest-api && mvn -q spring-boot:run
```

```bash run
curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"passenger": "meera", "message": "Hi, I am Meera. Is the Konkan Breeze a good train for a family?"}' | jq .
```

Press **Check**.
:::

:::step{type=try title="Setu, over HTTP"}
```text
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"passenger": "meera", "message": "Hi, I am Meera. Is the Konkan Breeze a good train for a family?"}' | jq .
{
  "passenger": "meera",
  "answer": "Yes, the Konkan Breeze is a family-friendly train with comfortable seating and scenic views. It offers amenities that cater to families traveling together. Enjoy your journey!"
}
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"passenger": "meera", "message": "What did I just ask you about?"}' | jq .
{
  "passenger": "meera",
  "answer": "You asked if the Konkan Breeze is a good train for a family."
}
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"passenger": "ravi", "message": "What did I just ask you about?"}' | jq .
{
  "passenger": "ravi",
  "answer": "You haven't asked me anything yet. How can I assist you today?"
}
```

A web API with a conversation per passenger: Meera's follow-up was answered from her own memory, and Ravi, who had
asked nothing, got nothing of hers. Any website, app or other service can now use Setu with one HTTP call.

Read Meera's first answer once more, though: "comfortable seating", "amenities that cater to families". Setu has never
seen a description of the Konkan Breeze; that is a friendly guess, chapter 11's problem in a nicer voice. Part 4 gives
Setu tools to look things up, and the railway's own documents to answer from.
:::

:::step{type=predict title="Guess first"}
:::question
You restart the Spring app. Meera sends "What did I just ask you about?" again. What happens?
:::
- [ ] Setu remembers: Spring saves beans to disk
- [x] Setu has forgotten: the memories were in the JVM and the restart cleared them
- [ ] The app refuses the request
:::explain
The ChatMemoryProvider makes in-memory memories. For a real service, back them with a persistent ChatMemoryStore
(a database or Redis) so conversations survive restarts and work across several instances.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does the API key come from in the Spring app?
:::
- [ ] It is written in application.properties
- [x] application.properties refers to the OPENAI_API_KEY environment variable, read at start-up
- [ ] The starter asks OpenAI for one
:::explain
`${OPENAI_API_KEY}` is a placeholder. In production it comes from the environment or a secret manager, never from a
committed file.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which beans does @AiService wire automatically?
:::
- [x] The ChatModel, and a ChatMemoryProvider, tools or retrievers if the application defines them
- [ ] Only the ChatModel
- [ ] Every bean in the application, as tools
:::explain
Automatic wiring uses the AI components it finds. Tools are found only when you mark them (chapter 19).
:::
:::

:::step{type=deep-dive title="Go deeper: Setu as a production service"}
**Streaming over HTTP.** Return `Flux<String>` from an AI Service method (with the reactive module) or use an
`SseEmitter`, so the website shows chapter 16's word-by-word answers.

**Validation and limits.** Validate `ChatRequest` (message length, a known passenger id) before calling the model; a
length limit is also the first guardrail (chapter 25).

**Rate limits.** One user can cost real money in a loop. Limit requests per passenger, as the LabBox gateway does.

**Observability.** The starters publish Micrometer metrics for every model call (tokens, latency): chapter 26 reads
them.
:::

:::step{type=recap}
You can now:

- configure a LangChain4j model in Spring Boot with `langchain4j.open-ai.chat-model.*` properties;
- turn an interface into an injectable bean with `@AiService`, wired with a model and a memory provider;
- expose an AI Service as a JSON endpoint with `@PostMapping` and `@RequestBody`;
- explain what restarts do to in-memory conversations.

That is the end of Part 3. Next, chapter 19: tools. Setu stops guessing and starts asking your Java code for real
timetables, fares and dates.

:::photo{src="/lesson-images/langchain4j/l4j-18-notes.webp" alt="Handwritten notes about the Spring Boot API: starters build the ChatModel; properties, not code; @AiService makes a bean; POST /chat is JSON in, JSON out; keys stay in the environment" ai="true"}
One page of notes for this chapter.
:::
:::
