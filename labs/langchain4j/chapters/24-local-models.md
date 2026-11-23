:::step{type=story title="A model in the station office"}
Two requests reach Setu's team in the same week. Legal asks whether passenger messages could stay on Sahyadri Rail's
own servers instead of going to a provider abroad. Finance asks why a "Hi!" costs the same model as a two-paragraph
complaint about a missed connection.

Both have answers in LangChain4j. **Open-weight models** (chapter 11) can run on your own machine with **Ollama**,
behind the same `ChatModel` interface. And a **routing model** can send each request to the model that fits it: a
small, cheap one for greetings, a capable one for the hard questions. Both are just more `ChatModel`s, so nothing else
in Setu changes.

:::mission
Build a chat model for a local Ollama server, then a routing model that sends short messages to a small model and long
ones to a large one.
:::
:::

:::step{type=history title="Large language models on a laptop"}
:::before{title="Data-centre only"}
In early 2023 running a large language model meant renting graphics cards with tens of gigabytes of memory. The
weights of Meta's LLaMA, released to researchers in **February 2023**, needed more memory than any laptop had.
:::

In **March 2023** Georgi Gerganov released **llama.cpp**, which ran LLaMA on an ordinary computer's CPU by
**quantising** the weights: storing each parameter in 4 bits instead of 16, at a small cost in quality. Within months
people ran capable models on laptops and phones. **Ollama**, launched in **2023**, wrapped the same idea in a simple
tool: `ollama pull`, `ollama run`, and a local API on port 11434. Open-weight model families followed fast, from Meta
(Llama), Mistral, Alibaba (Qwen), Google (Gemma) and DeepSeek, many in sizes from half a billion parameters to hundreds
of billions.

:::solved
**Your machine, your data.** A local model sends nothing outside your network and has no per-token bill. The costs
move elsewhere: hardware, memory, and answers that are noticeably weaker for small models.
:::

:::timeline
- **2023** LLaMA (February), llama.cpp (March), Ollama.
- **2024** Llama 3, Qwen 2.5, Gemma 2: strong small open models.
- **2025** Reasoning models with open weights.
:::
:::

:::step{type=concept title="Same interface, different engine" file="24-local-models/src/main/java/com/setu/Local.java" line="14-18"}
`OllamaChatModel` lives in its own module, `langchain4j-ollama`, and is built like every other model:

```java
ChatModel local = OllamaChatModel.builder()
        .baseUrl("http://localhost:11434")   // where Ollama listens
        .modelName("qwen2.5:0.5b")            // a model pulled with: ollama pull qwen2.5:0.5b
        .temperature(0.0)
        .build();
```

There is no API key: the server is yours. It speaks Ollama's own API (`/api/chat`), not OpenAI's, which is why it has
its own LangChain4j module; your code sees only `ChatModel`, so AI Services, memory, tools and RAG all work the same.

Choosing a local model is a trade-off you measure, not guess:

| Model size | Memory needed (4-bit) | Typical use |
|---|---|---|
| 0.5 to 3 billion parameters | 0.5 to 2.5 GB | Classification, routing, short extraction; weak at explanations |
| 7 to 14 billion | 5 to 10 GB | Decent chat and RAG on one good machine |
| 70 billion and more | 40 GB and more | Close to hosted models, on serious hardware |

Your lab machine has no Ollama server (models need gigabytes of memory per learner), so `Setu.java` skips the local
part unless `OLLAMA_URL` is set; the check uses a stand-in for Ollama's API. The output below was captured on a machine
running Ollama with Qwen 2.5 0.5B.
:::

:::step{type=task task=ollama_model title="Your turn: a local model" file="24-local-models/src/main/java/com/setu/Local.java" line="14-18"}
Finish `Local.ollama(baseUrl, modelName)`: build an `OllamaChatModel` with `baseUrl(baseUrl)`, `modelName(modelName)`
and `temperature(0.0)`.

Press **Check**.
:::

:::step{type=concept title="Routing: the right model for each request" file="24-local-models/src/main/java/com/setu/Local.java" line="20-27"}
A `RoutingChatModel` (experimental in 1.24) is a `ChatModel` that forwards each request to one of several **routes**,
as decided by a **router**:

```java
RoutingChatModel.builder()
        .route("simple", "greetings and short questions", small)
        .route("complex", "long questions and complaints", large)
        .router(request -> ChatModelRoutingResult.route(lastLength(request.chatRequest()) > 120 ? "complex" : "simple"))
        .defaultRoute("complex")
        .build();
```

1. Each route has a name, a description and a model.
2. The router looks at the request and returns a route. This one is a plain rule on the length of the passenger's last
   message (`lastLength` is already written).
3. The default route is used whenever the router cannot decide: choose the safe one, the capable model.

A rule is free and predictable. LangChain4j also has `DecisionModelChatModelRouter`, which asks a small, cheap
**decision model** to choose the route from the descriptions, useful when "hard" cannot be judged by length. Because a
`RoutingChatModel` is itself a `ChatModel`, you can pass it to `AiServices` and nothing else in Setu knows routing
exists.
:::

:::step{type=task task=routing_model title="Your turn: route by length" file="24-local-models/src/main/java/com/setu/Local.java" line="20-27"}
Finish `Local.routing(small, large)`: build the `RoutingChatModel` above, with the routes `simple` and `complex`, the
length rule (over 120 characters is `complex`) and `complex` as the default route.

```bash run
cd /workspace/24-local-models && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="A small local model, and two routes"}
Captured with Ollama running locally and `OLLAMA_URL` set:

```text
$ OLLAMA_URL=http://localhost:11434 mvn -q compile exec:java
Local model: A hill railway is a type of railway that runs along hills or mountains, connecting different parts of the country.

> Hi!
(simple route) Hello! How can I assist you today?

> Last Sunday the Konkan Breeze stopped for two hours near Karjat in heavy rain, nobody told us why, and we missed our connection to Ratnagiri. What should we have done, and can we get anything back?
(complex route) I'm sorry to hear about your experience with the Konkan Breeze. Here are a few steps you could have taken, as well as potential options for seeking compensation:

1. **Immediate Actions**:
   - **Contact Train Staff**: If you experience delays, it’s best to immediately contact the train staff or a helpline for information regarding delays and next steps.
   - **Check Station Announcements**: Often, information about train delays is announced over the intercom.

2. **Alternative Travel**: If you missed your connection to Ratnagiri, you could have checked for the next available train or other modes of transportation such as buses or taxis to reach your destination.

3. **Documentation**: Keep all relevant documentation, such as your train tickets, any communications you attempt (emails, texts, etc.), and notes on the circumstances of the delay.

4. **Feedback and Compensation**:
   - **File a Complaint**: You can file a complaint with the railway authorities or the customer care service of the train you were on. Explain your situation and ask for any potential compensation.
   - **Compensation Policies**: Check the railway’s policy on delays and cancellations. Depending on the circumstances and their policies, you may be eligible for a refund or compensation.

5. **Follow Up**: If you don’t receive a response in a reasonable time, follow up on your complaint.

6. **Travel Insurance**: If you had travel insurance, check if it covers delays and missed connections.

Be sure to act promptly and keep records of all communications. Good luck!
```

The local model answered on a laptop's CPU, sending nothing to anyone. Read its answer, though: "a
type of railway that runs along hills or mountains, connecting different parts of the country" is vague, and the last
part is not true of hill railways in general. A 0.5-billion-parameter model is fine for classifying a message or
picking a route; for explaining rules to passengers it is too weak, and a 7B or larger model would be needed.

The routing model sent "Hi!" down the simple route (a model limited to 60 tokens) and the long complaint down the
complex route (400 tokens), which wrote a full, structured reply. In a real deployment the simple route would be a
cheaper model, or a local one, and most greetings and short questions would never touch the expensive model. (Notice
also that the long answer gives generic advice: Setu had no refund rules in this chapter. Routing chooses a model; it
does not give it knowledge.)
:::

:::step{type=predict title="Guess first"}
:::question
You switch Setu from OpenAI to a local Ollama model. Which code changes?
:::
- [ ] Every AI Service and tool
- [x] Only where the ChatModel is built
- [ ] The prompts must be rewritten in Ollama's format
:::explain
Everything depends on the ChatModel interface. Test the quality again, though: prompts that work well with one model
may need adjusting for a smaller one.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does quantisation do?
:::
- [x] Stores each weight with fewer bits, so a model needs less memory, at a small cost in quality
- [ ] Removes layers from the model
- [ ] Makes the model answer in fewer tokens
:::explain
4-bit weights need a quarter of the memory of 16-bit ones; that is what put LLMs on laptops.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is the default route the complex one?
:::
- [ ] It is cheaper
- [x] When the router cannot decide, the capable model is the safer choice
- [ ] RoutingChatModel requires it
:::explain
A wrong answer to a hard question costs more than a few extra tokens on an easy one.
:::
:::

:::step{type=deep-dive title="Go deeper: running models yourself"}
**OpenAI-compatible servers.** Ollama, vLLM and others also offer an OpenAI-compatible endpoint, so `OpenAiChatModel`
with a different base URL works too; the dedicated `OllamaChatModel` exposes Ollama-specific options.

**Serving many users.** Ollama suits one machine. For many concurrent users, servers like vLLM batch requests on GPUs
far more efficiently.

**Decision models.** `TypeSafeDecisionModel` and the decision router choose among options with probabilities, and a
`minProbability` sends unsure cases to the default route.

**Measure before you route.** Log which route each request took and compare quality and cost per route with a golden
set of questions (chapter 26); a router that sends hard questions to a weak model saves money and loses passengers.
:::

:::step{type=recap}
You can now:

- explain open-weight models, quantisation and Ollama, and their trade-offs;
- build an `OllamaChatModel` behind the same `ChatModel` interface;
- route requests between models with `RoutingChatModel`, a router and a default route;
- judge a model's quality from its real answers, not its name.

That is the end of Part 4. Next, chapter 25: guardrails. Checks before and after the model that keep Setu safe.

:::photo{src="/lesson-images/langchain4j/l4j-24-notes.webp" alt="Handwritten notes about local models: open weights run on your machine; Ollama gives the same ChatModel; small models are fast but weak; route simple or complex; the default route is the safe model" ai="true"}
One page of notes for this chapter.
:::
:::
