:::step{type=story title="Calling the model for the first time"}
Part 1 showed you what a language model is. Now Setu calls a real one, gpt-4o-mini, running in OpenAI's data
centres. Before any library hides the details, you will do it the way every library does it underneath: one HTTP
request, with a JSON body, and one JSON response.

It is worth doing once by hand. When something goes wrong in a real AI application (a timeout, a wrong model name, a
key that does not work, a strange answer), the cause is almost always visible in this one request and response. Once
you have seen them raw, you can read them in any log.

:::mission
Send Setu's first question to a real language model with Java's own `HttpClient`, and read the answer out of the JSON
that comes back.
:::
:::

:::step{type=concept title="A chat completion is an HTTP POST"}
Most language model services speak the same protocol, the one OpenAI introduced: the **Chat Completions API**. A call
is one `POST` to an address ending in `/chat/completions`:

1. **headers**: `Authorization: Bearer <your key>` (who is paying) and `Content-Type: application/json`;
2. **body**: a JSON object with the `model` to use and a list of `messages`, each with a `role` and its `content`;
3. **response**: a JSON object whose `choices[0].message.content` is the answer, plus `usage`, the tokens it cost.

The three roles you will use all course:

| Role | Who writes it | What it is for |
|---|---|---|
| `system` | You, the developer | Instructions: who the assistant is, how to answer, what not to do |
| `user` | The passenger (through your app) | The question |
| `assistant` | The model | Its previous answers, when you send a conversation back (chapter 17) |

:::diagram{name="l4j-http-call"}
Setu builds a JSON body, POSTs it with a key to the gateway, the gateway forwards it to OpenAI, and the JSON answer comes back.
:::

In LabBox, the request goes to the **LabBox gateway** instead of straight to OpenAI. The gateway holds the real
OpenAI key, checks your daily budget, logs the call, and forwards it. Your lab machine has two environment variables:
`OPENAI_BASE_URL` (the gateway's address) and `OPENAI_API_KEY` (a key that only works at the gateway, for you, in this
course). In a company the shape is the same: **a real API key never goes into your code**; it lives in an environment
variable or a secret store.
:::

:::step{type=history title="From completions to chat, and an API that became a standard"}
:::before{title="Each model, its own interface"}
Before 2023, every AI service had its own API: different addresses, different JSON, different ideas of what a
"prompt" was. Even OpenAI's own first API, **Completions**, took one long string of text and returned its
continuation, exactly like your bigram model in chapter 3, which made conversations awkward to build.
:::

On **1 March 2023**, three months after ChatGPT, OpenAI opened the model behind it, gpt-3.5-turbo, as the **Chat
Completions API**: a list of messages with roles in, one message out. It was simple, it matched how people used chat
models, and it spread. Today many providers and local model servers offer an "OpenAI-compatible" endpoint with this
exact shape, including Ollama, which you will meet in chapter 24.

:::solved
**One shape for many models.** Because so many services speak this protocol, code that can send this one request can
talk to a large part of the model world, by changing a base URL and a model name.
:::

:::timeline
- **2020** OpenAI's API opens with Completions: text in, text out.
- **2022** ChatGPT, on 30 November.
- **2023** The Chat Completions API, on 1 March: messages with roles.
- **2024** OpenAI-compatible endpoints are everywhere.
:::
:::

:::step{type=example title="Worked example: the request body" file="07-raw-http/src/main/java/com/setu/Http.java" line="26-33"}
`Http.body(question)` is already written. It builds the JSON with Jackson instead of gluing strings, so a question
containing quotes or line breaks is escaped correctly:

```java
ObjectNode body = JSON.createObjectNode();
body.put("model", "ai-chat");
var messages = body.putArray("messages");
messages.addObject().put("role", "system").put("content", SYSTEM);
messages.addObject().put("role", "user").put("content", question);
return body.toString();
```

1. `"model": "ai-chat"` is the alias the LabBox gateway maps to gpt-4o-mini. With OpenAI directly, you would write
   `"gpt-4o-mini"`.
2. The system message comes first: Setu's instructions (`SYSTEM`, at the top of the class).
3. The passenger's question is the user message.

Sending it is three calls on Java's `HttpClient` (part of the JDK since Java 11): build an `HttpRequest` for the
address, with headers and `POST(BodyPublishers.ofString(...))`; `CLIENT.send(request, BodyHandlers.ofString())`; and
`.body()` on the response. Here is a different POST, only to read (it is not in your project):

```java
HttpRequest request = HttpRequest.newBuilder(URI.create("https://example.com/feedback"))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString("{\"stars\": 5}"))
        .build();
String reply = CLIENT.send(request, HttpResponse.BodyHandlers.ofString()).body();
```
:::

:::step{type=task task=send_request title="Your turn: send the request" file="07-raw-http/src/main/java/com/setu/Http.java" line="35-39"}
Finish `Http.send(baseUrl, apiKey, question)`: POST `body(question)` to `baseUrl + "/chat/completions"`, with the
headers `Content-Type: application/json` and `Authorization: Bearer ` followed by the key, and return the response
body as a `String`.

Press **Check**.
:::

:::step{type=try title="Careful: the HTTP/2 surprise" file="07-raw-http/src/main/java/com/setu/Http.java" line="18-20"}
When we first wrote this chapter, `CLIENT` was simply `HttpClient.newHttpClient()`. The very first run failed:

```text
== Response body
Invalid HTTP request received.
[ERROR] Failed to execute goal org.codehaus.mojo:exec-maven-plugin:3.7.0:java (default-cli) on project setu: An exception occurred while executing the Java class. Unrecognized token 'Invalid': was expecting (JSON String, Number, Array, Object or token 'null', 'true' or 'false')
```

Two lessons in one error. First, the server did not answer with JSON at all, and `answer` tried to parse the error
text: always check the status code before reading the body. Second, the cause: by default Java's `HttpClient` asks to
upgrade a plain `http://` connection to HTTP/2, and the gateway's web server answers that with "Invalid HTTP request
received". That is why `CLIENT` asks for HTTP/1.1:

```java
static final HttpClient CLIENT = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
```

This is the kind of detail a library handles for you, and the kind you can only debug if you have seen the raw call.
:::

:::step{type=concept title="Reading the answer out of the response"}
Here is the shape of what comes back (trimmed):

```json
{
  "id": "chatcmpl-...",
  "model": "ai-chat",
  "choices": [
    {
      "index": 0,
      "message": { "role": "assistant", "content": "Hello! We run three trains..." },
      "finish_reason": "stop"
    }
  ],
  "usage": { "prompt_tokens": 47, "completion_tokens": 30, "total_tokens": 77 }
}
```

(The gateway answers with the alias you asked for, `ai-chat`; OpenAI itself would answer with the exact model version.)
`choices` is a list because you can ask for several alternative answers in one call; normally there is one. The
answer is `choices[0].message.content`. With Jackson, `JSON.readTree(text)` turns the JSON into a tree you can walk with
`path(...)`: `path("choices").path(0).path("message").path("content")`, then `asString()`. `path` never throws: a
missing field gives a "missing node", which is safer than `get` when a server sends something unexpected.
:::

:::step{type=task task=read_answer title="Your turn: read the answer" file="07-raw-http/src/main/java/com/setu/Http.java" line="41-44"}
Finish `Http.answer(responseJson)`: return the text at `choices[0].message.content`.

```bash run
cd /workspace/07-raw-http && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="A real model answers"}
```text
$ mvn -q compile exec:java
== Request body
{"model":"ai-chat","messages":[{"role":"system","content":"You are Setu, the help desk assistant of Sahyadri Rail, a small hill railway between Pune, Lonavala, Karjat and Ratnagiri. Answer passengers in at most three short sentences."},{"role":"user","content":"Hello! Which trains do you run?"}]}

== Response body
{"id":"chatcmpl-EnKHqboCQqrkTle9hDzk0oMk3ZidN","object":"chat.completion","created":1795424762,"model":"ai-chat","choices":[{"index":0,"message":{"role":"assistant","content":"Sahyadri Rail operates between Pune, Lonavala, Karjat, and Ratnagiri. We provide scenic hill train experiences on this picturesque route. For specific train schedules and timings, please check our official website.","refusal":null,"annotations":[]},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":62,"completion_tokens":45,"total_tokens":107,...},"service_tier":"default","system_fingerprint":"fp_758480d42c"}

== The answer
Sahyadri Rail operates between Pune, Lonavala, Karjat, and Ratnagiri. We provide scenic hill train experiences on this picturesque route. For specific train schedules and timings, please check our official website.
```

That is a complete conversation with gpt-4o-mini, nothing hidden. Read the response from top to bottom: the answer
(`content`), why it stopped (`finish_reason: stop`: it finished its answer), and what it cost (`usage`: 62 tokens in,
45 out). The system message made it speak for Sahyadri Rail, and in three short sentences, as told. But look at what it
did with the question: it never names a train, and sends the passenger to "our official website", which does not
exist. It has never seen Sahyadri Rail's timetable, so it avoided the question with something vague. Chapter 11 is
about what models do when they do not know, and how to stop them inventing.

Inside your lab, `lab requests --last` shows the same call from the gateway's side. Two differences are worth
noticing: the gateway answered your program with the alias, `"model": "ai-chat"`, but its log shows the real model,
`gpt-4o-mini-2024-07-18`; and it added `"max_tokens": 1024`, a safety limit on the answer's length that every
LabBox call gets:

```text
$ lab requests --last
2026-11-23 09:06:03 UTC  ai-chat -> openai/gpt-4o-mini  62 in, 45 out

--- request ---
{"model": "ai-chat", "messages": [{"role": "system", "content": "You are Setu, ..."}, {"role": "user", "content": "Hello! Which trains do you run?"}], "max_tokens": 1024}

--- response ---
{"id": "chatcmpl-EnKHqboCQqrkTle9hDzk0oMk3ZidN", "object": "chat.completion", "created": 1795424762, "model": "gpt-4o-mini-2024-07-18", ...}
```
:::

:::step{type=predict title="Guess first"}
:::question
You change `"model": "ai-chat"` to `"model": "gpt-99"`. What happens?
:::
- [ ] OpenAI picks the closest model
- [x] The server answers with an error (an HTTP status that is not 200) instead of choices
- [ ] The answer is empty but the call succeeds
:::explain
The server cannot guess. Your code must check the status code before reading `choices`: a real client turns a 4xx
into a clear exception. LangChain4j does this for you from chapter 9.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where does the API key belong?
:::
- [ ] In the source code, so the app works anywhere
- [x] In an environment variable or a secret store, read at run time
- [ ] In the system message
:::explain
Code is copied, committed and shared; a key in it leaks. LabBox goes one step further: your key only works at the
gateway, so even printing it exposes nothing valuable.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why build the body with Jackson instead of `"{\"content\": \"" + question + "\"}"`?
:::
- [ ] It is faster
- [x] A question with a quote or a line break would break hand-glued JSON
- [ ] The server requires Jackson
:::explain
A passenger typing `my "big" bag` would end the string early, and the server would reject the request. A JSON library
escapes everything correctly. This is also the first defence against prompt injection through malformed input.
:::
:::

:::step{type=deep-dive title="Go deeper: what a production client adds"}
**Timeouts.** A model can take many seconds for a long answer. Set a connect timeout and a request timeout, and decide
what Setu says when they expire.

**Retries.** Servers answer `429 Too Many Requests` or `5xx` now and then. A good client retries a few times with a
growing wait (exponential backoff), and never retries a request that changed something.

**Status codes.** `401` means a bad key, `404` usually a wrong model name, `400` a malformed body, `429` too many
requests or no budget left. Turning these into clear messages saves hours of debugging.

Every one of these is built into LangChain4j's `OpenAiChatModel` (chapter 9): `timeout(...)`, `maxRetries(...)`, and
exceptions with the server's message.
:::

:::step{type=recap}
You can now:

- explain a chat completion: a POST with a key, a JSON body of messages with roles, and a JSON answer;
- call a real language model with Java's `HttpClient` and read the answer with Jackson;
- say why API keys live outside the code, and what the gateway does;
- read a raw response: model, content, finish reason and usage.

Next, chapter 8: the same call with OpenAI's official Java SDK, which gives you typed classes instead of JSON.

:::photo{src="/lesson-images/langchain4j/l4j-07-notes.webp" alt="Handwritten notes about calling a model over HTTP: a model call is one HTTP POST; the key goes in the Authorization header; the body holds the model and messages; the answer is choices[0].message.content; keys never go in code" ai="true"}
One page of notes for this chapter.
:::
:::
