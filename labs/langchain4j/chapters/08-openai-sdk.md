:::step{type=story title="Less JSON, more Java"}
Chapter 7 worked, but look at what it took: a JSON body built field by field, a path through `choices[0].message.content`
typed as strings, and nothing to stop you misspelling `"mesages"`. The compiler could not help you, because to Java
it was all just text.

OpenAI publishes an official **Java SDK** for its API: Java classes for every request and response, with builders, so
the compiler checks your request and your IDE completes it. Setu makes the same call again, the typed way.

:::mission
Create an OpenAI client pointed at the LabBox gateway, and ask Setu's question with typed request and response
classes.
:::
:::

:::step{type=concept title="A client, parameters, a completion"}
The SDK (`com.openai:openai-java`) has three pieces you will use:

| Piece | Class | What it does |
|---|---|---|
| The client | `OpenAIClient`, built with `OpenAIOkHttpClient.builder()` | Holds the base URL, the key, timeouts and retries; one per application |
| The request | `ChatCompletionCreateParams` | A typed request: `.model(...)`, `.addSystemMessage(...)`, `.addUserMessage(...)` |
| The response | `ChatCompletion` | `choices().get(0).message().content()` |

The call itself reads like the API's address: `client.chat().completions().create(params)` sends a POST to
`/chat/completions`. Underneath it is exactly chapter 7's request; you can see the same JSON in `lab requests`.

Two details make the SDK feel like modern Java:

1. **Optional.** `message().content()` returns an `Optional<String>`, because a message can have no text (when the
   model asks to call a tool instead, chapter 19). `orElse("")` gives the text or an empty string.
2. **From the environment.** `OpenAIOkHttpClient.fromEnv()` reads `OPENAI_API_KEY` and `OPENAI_BASE_URL` by itself.
   Your task passes them in explicitly, so the check can point the client at a test server.

**Check yourself:** why does a whole application usually share one client? (It holds a connection pool and settings;
creating one per request wastes connections and time.)
:::

:::step{type=history title="SDKs generated from the API"}
For years, Java developers called OpenAI through community libraries, each covering part of the API and each a little
behind the latest models. In **2024** OpenAI began publishing an official Java SDK, generated from the machine-readable
description of its API (an OpenAPI specification), so every new endpoint and field appears in Java at the same time as
in Python and JavaScript.

:::before{title="Hand-written clients"}
Hand-written clients lag the API, differ in naming, and break in different ways when the API changes. Every team
re-learned the same JSON.
:::

:::solved
**Typed and current.** A generated SDK gives typed classes for the whole API, kept up to date automatically. Its
limit is the other side of the same coin: it speaks only OpenAI's API. Switching to another provider means rewriting
the calls, which is the problem LangChain4j solves in the next chapter.
:::
:::

:::step{type=example title="Worked example: a client for another service" file="08-openai-sdk/src/main/java/com/setu/Sdk.java" line="16-19"}
Every builder in the SDK follows the same pattern: start with `builder()`, set what you need, end with `build()`.
Here is a client with a timeout and fewer retries, only to read (it is not in your project):

```java
OpenAIClient client = OpenAIOkHttpClient.builder()
        .baseUrl("https://api.openai.com/v1")
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .timeout(Duration.ofSeconds(30))
        .maxRetries(1)
        .build();
```

For Setu the base URL is the gateway's, which `Setu.java` reads from `OPENAI_BASE_URL`. A base URL is the address of
the API without the endpoint: the SDK adds `/chat/completions` itself.
:::

:::step{type=task task=sdk_client title="Your turn: the client" file="08-openai-sdk/src/main/java/com/setu/Sdk.java" line="16-19"}
Finish `Sdk.client(baseUrl, apiKey)`: build an `OpenAIClient` with `OpenAIOkHttpClient.builder()`, the base URL and the
key: `return OpenAIOkHttpClient.builder().baseUrl(baseUrl).apiKey(apiKey).build();`

The usual slip: a base URL that already ends in `/chat/completions`. The SDK adds that path itself, so the request
goes to `.../chat/completions/chat/completions`, which does not exist.

Press **Check**.
:::

:::step{type=task task=sdk_ask title="Your turn: ask the question" file="08-openai-sdk/src/main/java/com/setu/Sdk.java" line="21-26"}
Finish `Sdk.ask(client, question)`:

1. build `ChatCompletionCreateParams` with `.model("ai-chat")`, `.addSystemMessage(SYSTEM)` and
   `.addUserMessage(question)`;
2. send it with `client.chat().completions().create(params)`;
3. return the first choice's message content, `orElse("")`.

The usual slip: `.content().get()`. It works for ordinary answers, and throws `NoSuchElementException` the first
time a message has no text (chapter 19's tool calls).

```bash run
cd /workspace/08-openai-sdk && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="The same answer, typed"}
```text
$ mvn -q compile exec:java
We operate several trains on the Sahyadri Rail route between Pune, Lonavala, Karjat, and Ratnagiri. Popular trains include the Sahyadri Express and the Hill-View Special. Please check our schedule for specific times and services.
$ mvn -q compile exec:java
Sahyadri Rail operates scenic trains between Pune, Lonavala, Karjat, and Ratnagiri. We offer various services including passenger trains for leisure travel. For specific train schedules and routes, please check our official website or contact our help desk.
```

The same question as chapter 7, with not a line of JSON in your code. We ran it twice, and the two answers differ,
because each token is sampled (chapter 6). (Two more runs on 26 November named no trains at all, and both sent the
passenger to "our website": the invention below comes and goes, which makes it easy to miss in a quick test.) Now read the first answer again: "Popular trains include the **Sahyadri
Express** and the **Hill-View Special**." Sahyadri Rail has no such trains. The model invented two plausible names,
politely and with confidence. Keep that in mind; chapter 11 fixes it.

Notice also what is still missing. The answer is a plain `String`, the call is OpenAI's own, and to switch Setu to
another provider tomorrow, every line using the SDK would change.
:::

:::step{type=predict title="Guess first"}
:::question
Sahyadri Rail decides to try a model from another company. How much of `Sdk.java` survives?
:::
- [ ] All of it: every model speaks the same API
- [x] Little: the SDK's classes are OpenAI's; another provider means another SDK, or an OpenAI-compatible endpoint
- [ ] None of the system message
:::explain
Provider SDKs tie your code to the provider. An OpenAI-compatible endpoint helps for simple calls, but features differ.
LangChain4j's `ChatModel` interface (chapter 9) keeps your code the same across 20+ providers.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `message().content()` return an `Optional`?
:::
- [ ] To make the code longer
- [x] A message may have no text, for example when the model asks to call a tool instead
- [ ] Because the network might fail
:::explain
A missing value is part of the API, not an error, so the type says so. Network failures are exceptions.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `OpenAIOkHttpClient.fromEnv()` read?
:::
- [x] The key and base URL from environment variables such as OPENAI_API_KEY and OPENAI_BASE_URL
- [ ] A file in your home folder
- [ ] Nothing: it connects without a key
:::explain
Configuration from the environment keeps keys out of code and lets the same program talk to OpenAI, a gateway, or a
test server.
:::
:::

:::step{type=deep-dive title="Go deeper: what the SDK offers beyond chat"}
**Every endpoint.** Embeddings, images, audio, files, moderation and the newer Responses API all have typed classes.

**Async and streaming.** `client.async()` returns futures; streaming methods give you chunks as the model writes
them (chapter 16 does this with LangChain4j).

**Raw responses.** `client.chat().completions().withRawResponse()` gives the HTTP headers too, including rate-limit
headers, useful for monitoring.

**When to use it.** If you only ever call OpenAI and want every newest feature on day one, the official SDK is a fine
choice. LangChain4j even has an integration built on it, `langchain4j-open-ai-official`. For an application that may
change providers or needs memory, tools, retrieval and agents, a framework saves you writing all of that yourself.
:::

:::step{type=recap}
You can now:

- create an OpenAI client with the official Java SDK, pointed at any compatible base URL;
- send a typed chat completion request and read the answer;
- explain why provider SDKs tie your code to one provider.

Next, chapter 9: LangChain4j. One `ChatModel` interface for every provider, and Setu's first LangChain4j app.

:::photo{src="/lesson-images/langchain4j/l4j-08-notes.webp" alt="Sketchnote, The OpenAI Java SDK (the same call, with typed classes): Java classes for every request and answer, so the compiler checks your call. The request sent is the one from chapter 7. The flow: OpenAIClient, ChatCompletionCreateParams, create(params), content(): Optional. What we found: two runs, two different answers; once it invented two train names; content() is empty when a tool is called; it ties your code to one provider." ai="true"}
One page of notes for this chapter.
:::
:::
