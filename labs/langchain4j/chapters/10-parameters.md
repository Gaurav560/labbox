:::step{type=story title="The same question, a different answer"}
The railway's announcement team tried Setu and loved it: ask for a monsoon slogan and you get a fresh one every time.
The ticket office tried it too and was worried: ask "When does the Ghat Express leave?" twice and the two answers
were worded differently, and once it rambled for a whole paragraph.

Both teams were seeing the same setting. In chapter 6 you built softmax with a temperature: that knob is exposed in
every chat API. The announcement team wants it high; the ticket office wants it at zero, and short answers. This
chapter sets those knobs from LangChain4j, once for a model, or just for one request.

:::mission
Build a steady model that gives the same answer every time, and cap the length of one answer with a request-level
parameter.
:::
:::

:::step{type=concept title="The knobs every chat model has"}
| Parameter | What it controls | Typical values |
|---|---|---|
| `temperature` | How random the choice of each token is (chapter 6) | 0 for facts and data; 0.7 to 1 for writing; up to 2 |
| `topP` | Sample only from the likeliest tokens that together make up this share of the probability | 1.0 (off); 0.9 trims the long tail |
| `maxOutputTokens` | The most tokens the answer may have; the model stops there | 100 to 500 for chat answers |
| `stopSequences` | Text that ends the answer as soon as the model writes it | e.g. `"\n\n"` for one paragraph |
| `frequencyPenalty`, `presencePenalty` | Discourage repeating the same words or topics | 0 to 1 |

Two things to know before you turn them:

1. **Change one at a time.** OpenAI's documentation advises changing temperature or `topP`, not both: they do similar
   jobs, and together they are hard to reason about.
2. **Temperature 0 is steady, not perfect.** It removes the randomness of sampling, so the same input usually gives the
   same output, but the servers are not guaranteed to be bit-for-bit identical, and a wrong answer stays wrong every
   time.

`maxOutputTokens` is a hard stop, not a request to be brief: the model does not plan to finish within it, so a long
answer is simply cut. To get short answers, **ask** for them in the system message; use the limit as a safety net
against runaway costs.
:::

:::step{type=example title="Worked example: defaults on the model, overrides per request" file="10-parameters/src/main/java/com/setu/Tuned.java" line="18-32"}
LangChain4j lets you set parameters in two places:

```java
// on the model: the defaults for every request (only to read)
ChatModel model = OpenAiChatModel.builder()
        .baseUrl(baseUrl).apiKey(apiKey).modelName("ai-chat")
        .temperature(0.7)
        .maxTokens(300)
        .build();

// on one request: overrides the defaults, for this call only
ChatRequest request = ChatRequest.builder()
        .messages(SystemMessage.from(SYSTEM), UserMessage.from(question))
        .temperature(0.0)
        .build();
ChatResponse response = model.chat(request);
```

The builder of `OpenAiChatModel` sets the default for everything that uses the model; a `ChatRequest` changes only one
call. The ticket office's timetable questions and the announcement team's slogans can share one model, each request
with its own settings.
:::

:::step{type=task task=steady_model title="Your turn: a steady model" file="10-parameters/src/main/java/com/setu/Tuned.java" line="18-26"}
Finish `Tuned.steadyModel(baseUrl, apiKey)`: keep the base URL, key and model name, and add `.temperature(0.0)`.

Press **Check**.
:::

:::step{type=task task=short_answer title="Your turn: a limit for one answer" file="10-parameters/src/main/java/com/setu/Tuned.java" line="28-32"}
Finish `Tuned.ask(model, question, maxTokens)`: build a `ChatRequest` with `.messages(...)` (the system message and the
question) and `.maxOutputTokens(maxTokens)`, send it with `model.chat(request)`, and return the `ChatResponse`.

```bash run
cd /workspace/10-parameters && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Hot, cold, and cut short"}
```text
$ mvn -q compile exec:java
temperature 1.5, try 1: "Embrace the Rain, Ride the Train: Sahyadri!"
temperature 1.5, try 2: "Ride the Rain, Embrace the Tracks!"
temperature 1.5, try 3: "Ride the Rails, Embrace the Monsoon Bliss!"
temperature 0.0, try 1: "Ride the Rain: Sahyadri's Monsoon Magic Awaits!"
temperature 0.0, try 2: "Ride the Rain: Sahyadri's Monsoon Magic Awaits!"
temperature 0.0, try 3: "Ride the Rain: Sahyadri's Monsoon Magic Awaits!"

max 20 tokens: The journey from Pune to Ratnagiri on Sahyadri Rail offers stunning views of the Western
finish reason: LENGTH
```

At temperature 1.5, three slogans, three styles: what the announcement team wants. At 0.0, the same slogan three
times: what the ticket office wants. Then the answer limited to 20 tokens stops mid-sentence, and the finish reason
says why: `LENGTH`, the limit, not `STOP`, the model's own decision to end. Whenever you see `LENGTH` in production,
your limit is too small for the answers you are getting, or the model is rambling and the system message should ask
for brevity.
:::

:::step{type=predict title="Guess first"}
:::question
Setu answers timetable questions. Which temperature fits best?
:::
- [x] 0, so the same question gets the same answer
- [ ] 1.5, so answers sound natural
- [ ] It does not matter for facts
:::explain
For facts, randomness only adds ways to be wrong or inconsistent. Natural wording comes from the system message, not
from temperature.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You set `maxOutputTokens(50)` and the model's answer would need 80. What happens?
:::
- [ ] The model writes a shorter, complete answer
- [x] The answer is cut after 50 tokens, with finish reason LENGTH
- [ ] The request fails
:::explain
The limit is a hard stop. Ask for short answers in the instructions, and treat LENGTH as a signal to investigate.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where do you set a parameter that should apply to every call of a model?
:::
- [x] On the model's builder
- [ ] In every ChatRequest
- [ ] In the system message
:::explain
The builder sets defaults; a ChatRequest overrides them for one call.
:::
:::

:::step{type=deep-dive title="Go deeper: more knobs"}
**Seed.** Some providers accept a `seed` to make sampling repeatable even above temperature 0 (OpenAI calls it best
effort). Useful in tests.

**Reasoning models.** Newer "reasoning" models think before answering and often ignore temperature; they have their
own setting for how hard to think. Read the provider's page before tuning.

**Provider-specific parameters.** `OpenAiChatRequestParameters` exposes OpenAI-only options while the rest of your
code stays generic.

**Logging what you sent.** With `.logRequests(true)` on the builder, you can confirm that `temperature` and
`max_tokens` really are in the request, the first thing to check when a knob seems to do nothing.
:::

:::step{type=recap}
You can now:

- choose temperature, `topP`, `maxOutputTokens` and stop sequences for a job;
- set defaults on the model builder and override them per request with `ChatRequest`;
- tell finish reason `STOP` from `LENGTH`, and know what each means;
- explain why temperature 0 is steady but not a guarantee of truth.

Next, chapter 11: open and closed models, and the problem every AI application must design around: hallucinations.

:::photo{src="/lesson-images/langchain4j/l4j-10-notes.webp" alt="Handwritten notes about parameters: temperature 0 gives the same answer; temperature 1.5 gives new ideas; maxOutputTokens is a hard stop; LENGTH means cut off; the builder sets defaults, a request overrides them" ai="true"}
One page of notes for this chapter.
:::
:::
