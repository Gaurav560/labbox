:::step{type=story title="Steady, short, and paid for"}
The museum's finance officer, Mr. Kulkarni, has one question about Atlas, and it is a fair one: "What will this cost
us?" The lobby team has another: "Why does it answer the same question differently every time?" A school teacher
asked Atlas the same thing on two days and got two different explanations, and wondered which one was right.

Both questions have the same answer: **options**. Every request to a model can carry settings that control how
random the answer is, how long it may be, and which model writes it. And every answer comes back with a receipt: the
number of tokens it used. This chapter is about both.

An electricity meter counts every unit you use, and the bill follows the count. Tokens are a model's units: every
answer turns the dial, and every answer tells you by how much, if you know where to look.

:::photo{src="/lesson-images/spring-ai/electricity-meter.webp" alt="An old mechanical electricity meter from 1965, with five small dials counting kilowatt hours" credit="Mike1024" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Mechanical_electricity_meter_1965_(1).jpg"}
An electricity meter: every unit counted.
:::

:::mission
Make Atlas's answers steady and capped in length, and report the tokens every answer used.
:::
:::

:::step{type=concept title="Temperature: how adventurous the model is"}
For every next token, a model has a list of candidates with probabilities: after "The sky is", maybe "blue" 70%,
"clear" 10%, "full" 5%, and so on. **Temperature** decides how it picks:

| Temperature | Behaviour | Good for |
|---|---|---|
| 0 | almost always the most likely token | facts, data extraction, the same answer each time |
| 0.2 to 0.5 | mostly the likely tokens, a little variety | help desks like Atlas |
| 0.7 to 1 | balanced (usually the default) | general chat |
| above 1 | surprising, sometimes odd | brainstorming names and ideas |

Here is the same request, "Invent a name for a robot that guides museum visitors", three times at temperature 0 and
three times at 1.5, sent straight to the gateway:

```text
MuseBot|MuseBot|MuseBot| (temperature 0)
MuseBotsky.|ArtiGuide|ArtisanBot| (temperature 1.5)
```

At 0, the same name three times; at 1.5, three different ones (and a stray full stop). For a museum guide that should
say the same true thing every day, low is right.

:::diagram{name="ai-temperature"}
At a low temperature the model nearly always takes the most likely next word; at a high one it often takes a less likely one.
:::

**Check yourself:** you want Atlas to suggest five fun names for a new gallery. Low or high temperature? (Higher, about
0.9: you want variety.)
:::

:::step{type=concept title="maxTokens: a ceiling on length and cost"}
**maxTokens** caps how many tokens the answer may have. It is a ceiling, not a target: the model does not try to fill
it. If the answer reaches the ceiling, it simply stops, mid-sentence if need be. Here is a request with a ceiling of
12 tokens:

```text
{"content":"A black hole is a region in space where the gravitational pull","finish_reason":"length","usage":{"prompt_tokens":13,"completion_tokens":12}}
```

Cut off after "pull", and the answer says why: `finish_reason` is `length`, where a complete answer says `stop`. So the
system prompt asks for short answers ("three short sentences"), and maxTokens is the safety net: generous enough never
to cut a normal answer, low enough that no single answer can run away with the budget or the visitor's patience.

In Spring AI, options go on the prompt with the provider's options builder:

```java
chat.prompt()
    .user(q)
    .options(OpenAiChatOptions.builder()
            .temperature(0.2)
            .maxTokens(300))
    .call()
    .content();
```

(Note: you pass the **builder**, without `.build()`: Spring AI 2.0 merges it with the defaults for you.) Options can also
be set for the whole app in `application.properties`, such as `spring.ai.openai.chat.options.temperature=0.2`; options on a
prompt override those for that one request.
:::

:::step{type=task task=chat_options title="Your turn: steady and short" file="03-options/src/main/java/com/atlas/AskController.java" line="34"}
In `03-options`, make `GET /ask` send its requests with a **temperature of 0.2** and **at most 300 tokens**.

Run it, and ask the same question three times:

```bash run
cd 03-options && mvn -q -o spring-boot:run
```

```bash run
for i in 1 2 3; do curl -s "localhost:8080/ask?q=Give%20a%20one-line%20fun%20fact%20about%20Saturn."; echo; done
```

Press **Check**.
:::

:::step{type=try title="Three times the same question"}
With temperature 0.2 and the system prompt from chapter 2, the three answers were nearly identical:

```text
$ for i in 1 2 3; do curl -s "localhost:8080/ask?q=Give%20a%20one-line%20fun%20fact%20about%20Saturn."; echo; done
Saturn is famous for its beautiful rings, which are made mostly of ice and rock particles!
Saturn is famous for its beautiful rings, which are made of ice and rock particles!
Saturn is famous for its beautiful rings, which are made mostly of ice and rock particles!
```

One word ("mostly") came and went. Low temperature makes answers steady, not identical: if you need exactly the same
answer every time, you cache it (chapter 13).
:::

:::step{type=example title="Worked example: reading the receipt" file="03-options/src/main/java/com/atlas/AskController.java" line="41"}
`.content()` gives you only the text. `.chatResponse()` gives you the whole answer, receipt included:

```java
ChatResponse response = chat.prompt()
        .user("What is a comet?")
        .call()
        .chatResponse();

String text = response.getResult().getOutput().getText();   // the answer
Usage usage = response.getMetadata().getUsage();             // the receipt
usage.getPromptTokens();       // tokens you sent: system prompt + question
usage.getCompletionTokens();   // tokens the model wrote
usage.getTotalTokens();        // both
```

1. `getResult()` is the generated answer; `getOutput()` is the assistant's message; `getText()` its text.
2. `getMetadata()` holds facts about the call, and `getUsage()` the token counts.

Prompt tokens include **everything** you sent, not just the visitor's words: the whole system prompt travels with
every request.
:::

:::step{type=task task=token_usage title="Your turn: what did that answer cost?" file="03-options/src/main/java/com/atlas/AskController.java" line="44"}
Finish `GET /ask/costed?q=...`. It returns a `CostedAnswer`: the answer's text, and its prompt, completion and total
tokens, read from the `ChatResponse`.

```bash run
curl -s "localhost:8080/ask/costed?q=What%20is%20a%20black%20hole%3F" | jq .
```

(`jq .` prints JSON neatly.) Press **Check**.
:::

:::step{type=try title="One answer's receipt"}
```text
$ curl -s "localhost:8080/ask/costed?q=What%20is%20a%20black%20hole%3F" | jq .
{
  "answer": "A black hole is a place in space where gravity is so strong that nothing can escape from it, not even light. It forms when a large star collapses at the end of its life. They are mysterious and can be found in many parts of the universe.",
  "promptTokens": 96,
  "completionTokens": 53,
  "totalTokens": 149
}
```

96 tokens in, although the question is only six words: about 85 of them are the system prompt. 53 out: three short
sentences. At the course model's prices ($0.15 per million in, $0.60 per million out) this answer cost
$0.0000144 + $0.0000318 = **$0.000046**, about four thousandths of a rupee. Chapter 1's unlimited answer used about 400
output tokens: eight times more for the same question.
:::

:::step{type=predict title="Guess first"}
:::question
The system prompt grows from 85 tokens to 850 tokens (you added long rules and examples). Visitors ask 100,000 short
questions a month. Roughly what happens to the monthly input tokens?
:::
- [ ] Nothing changes: the system prompt is only sent once
- [x] They grow by about 76 million, because the system prompt is sent with every request
- [ ] They grow by 765 tokens in total
:::explain
Every request carries the whole system prompt: 765 extra tokens times 100,000 requests is 76.5 million tokens, about
$11 more a month on this model, and ten to a hundred times that on a big model. Short prompts are not just tidy; they
are cheaper.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
An answer ends in the middle of a sentence, and its finish reason is `length`. What happened?
:::
- [ ] The model ran out of things to say
- [x] It reached the maxTokens ceiling and was stopped
- [ ] The network dropped the end of the answer
:::explain
`length` means the ceiling cut it. Raise maxTokens, or ask for shorter answers in the prompt. `stop` means the model
finished by itself.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which tokens does `getPromptTokens()` count?
:::
- [ ] Only the visitor's question
- [x] Everything sent: system prompt, earlier messages, and the question
- [ ] The tokens of the answer
:::explain
The model reads the whole request every time, so all of it is counted and paid for. That is why conversation
history (chapter 6) and retrieved documents (chapter 10) make requests more expensive, and why they are trimmed.
:::
:::

:::step{type=deep-dive title="Go deeper: choosing a model"}
**Bigger is not always better.** Providers sell several sizes. Small models (like `gpt-4o-mini`) are fast and cheap
and handle help-desk questions well. Large models reason better on hard problems and cost ten to fifty times more per
token. Many teams start with the smallest model that passes their test questions, and route only the hard requests to
a big one.

**Speed has three parts.** Time to the **first token** (how soon anything appears), tokens per second (how fast the
rest arrives), and the answer's length. Streaming (chapter 4) hides the second; short answers cut the third.

**Other options.** `topP` is another way to limit randomness (use temperature or topP, not both). `stop` sequences end
the answer at a chosen text. `presencePenalty` and `frequencyPenalty` discourage repeating words. Each provider has its
own options class (`OpenAiChatOptions`, `AnthropicChatOptions`, ...); the common ones also exist on the portable
`ChatOptions`.

**Budgets in production.** Limit tokens per user per day (LabBox's gateway does exactly this to your requests), alert
on unusual spending, and log the usage of every call. Chapter 13 builds a small cost meter into Atlas.
:::

:::step{type=recap}
You can now:

- explain temperature, and choose it for facts (low) or ideas (high);
- cap answers with maxTokens, and recognise a cut answer by `finish_reason` = `length`;
- set options per request with `.options(OpenAiChatOptions.builder()...)` or for the whole app in properties;
- read the answer and its token usage from a `ChatResponse`, and turn tokens into money.

Next, chapter 4: streaming, so visitors see the answer as it is written instead of waiting for all of it.

:::photo{src="/lesson-images/spring-ai/springai-03-notes.webp" alt="Handwritten notes about options and cost: temperature 0.2 = steady; maxTokens = a ceiling; finish_reason: length = cut off; getUsage(): tokens in, out; the system prompt is paid every time" ai="true"}
One page of notes for this chapter.
:::
:::
