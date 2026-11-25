:::step{type=story title="The first bill"}
Atlas has been on the lobby screen for a week, in a trial. Then the museum's accountant forwards the first invoice from
the AI provider and asks two questions: "What does one answer cost? And what will it cost in May, when the schools
come?" The director adds a third: "Some children said it was slow. Is it?"

Nobody could answer. Atlas worked, but nobody was measuring it. Every service in production needs three numbers you
can see at any time: **how much** it costs, **how fast** it is, and **how often** it fails. For AI features the first
one matters more than usual, because every answer has a price.

Electricity has the same problem, and the answer has turned in every house for over a century: a meter, counting
every unit as it is used.

:::photo{src="/lesson-images/spring-ai/kwh-meter.webp" alt="The opened mechanism of an old electricity meter: coils, an aluminium disc and a row of small dials counting kilowatt-hours, with numbered labels" credit="Ali@gwc.org.uk" license="CC BY-SA 2.5" source="https://commons.wikimedia.org/wiki/File:ElectricityMeterMechanism.jpg"}
Inside an electricity meter: a spinning disc turns the dials that count every kilowatt-hour.
:::

:::mission
Put a meter on Atlas: the tokens and price of every answer, and the AI metrics Spring AI records, on a web endpoint.
:::
:::

:::step{type=concept title="Where the money goes"}
You have seen the pieces of an answer's cost in chapters 3, 14 and 15. Together:

| Part of the request | Tokens (measured in this course) | Grows with |
|---|---|---|
| system prompt | about 90 | your instructions |
| retrieved chunks (RAG) | about 100 per chunk | `topK` and chunk size |
| conversation history | everything kept by the session | the window (chapter 6) |
| tool descriptions | about 40 to 50 per tool (chapter 7: 4 tools added about 170) | how many tools you offer |
| a photo | about 8,500 at 512 pixels | its size (chapter 15) |
| the question | 5 to 30 | the visitor |
| **the answer** (output) | 30 to 80 | `maxTokens`, and how chatty the prompt allows |

Input tokens are cheap (gpt-4o-mini: 0.15 dollars per million); output tokens cost four times more (0.60 per million).
So the levers are: fewer chunks, a shorter window, fewer tools per call, smaller photos, and short answers ("at most
three sentences" in Atlas's system prompt is a cost control too).
:::

:::step{type=example title="Worked example: the usage of one answer" file="18-production/src/main/java/com/atlas/MeterController.java" line="42"}
Every response from the model carries its **usage**: how many tokens it read and wrote. Spring AI puts it in the
response metadata. To reach it, end the chain with `chatResponse()`, which returns the whole response instead of only
its text:

```java
ChatResponse response = chat.prompt().user(q).call().chatResponse();
Usage usage = response.getMetadata().getUsage();
int in = usage.getPromptTokens();      // tokens the model read
int out = usage.getCompletionTokens(); // tokens it wrote
String text = response.getResult().getOutput().getText();
```

The counts come from the provider itself, so they are exactly what you are billed for.
:::

:::step{type=task task=answer_cost title="Your turn: the price of an answer" file="18-production/src/main/java/com/atlas/MeterController.java" line="43"}
In `18-production`, finish `GET /ask/metered?q=...`: return the answer, its prompt and completion tokens, and its cost
in US dollars, using `INPUT_PER_MILLION` and `OUTPUT_PER_MILLION`:

1. `.call().chatResponse()`, then `getMetadata().getUsage()`.
2. The cost: `in * INPUT_PER_MILLION / 1_000_000 + out * OUTPUT_PER_MILLION / 1_000_000`.
3. Return the answer's text, both counts and the cost.

The usual slip: integer division. `in / 1_000_000` with `int`s is 0 for any real answer; multiply by the price
(a `double`) first.

```bash run
cd 18-production && mvn -q -o spring-boot:run
```

```bash run
curl -s -G localhost:8080/ask/metered --data-urlencode "q=When are you open?" | jq .
```

Press **Check**.
:::

:::step{type=try title="What Atlas costs"}
Real answers, with their meter (our re-run on 26 November: 95, 96 and 105 tokens in again, 27, 39 and 65 out, and
$0.00003045 for the first):

```text
$ curl -s -G localhost:8080/ask/metered --data-urlencode "q=When are you open?" | jq .
{
  "answer": "I'm sorry, but I don’t know the specific opening hours of the museum. You might want to check our website or contact the museum for that information.",
  "promptTokens": 95,
  "completionTokens": 31,
  "costUsd": 0.00003285
}
$ curl -s -G localhost:8080/ask/metered --data-urlencode "q=Why is the sky blue?" | jq .
{
  "answer": "The sky appears blue because of a process called scattering. When sunlight enters the Earth's atmosphere, it hits small particles and scatters. Blue light is scattered more than other colors, making the sky look blue to our eyes.",
  "promptTokens": 96,
  "completionTokens": 44,
  "costUsd": 0.000040799999999999996
}
$ curl -s -G localhost:8080/ask/metered --data-urlencode "q=Tell me everything about black holes, in as much detail as you can." | jq .
{
  "answer": "I’m here to help you learn about our museum and its exhibits. For detailed information about black holes, I recommend checking out a science book or a website dedicated to space. If you want to know more about our exhibits related to space, feel free to ask!",
  "promptTokens": 105,
  "completionTokens": 53,
  "costUsd": 0.000047550000000000004
}
```

About 95 tokens in (almost all of it the system prompt: the question is five tokens) and 30 to 50 out: about
0.003 to 0.005 US cents an answer. For the accountant: 2,000 visitors in May, three questions each, is 6,000 answers,
about 25 cents a day. With RAG's three chunks (chapter 14) each answer reads about 300 tokens more, and it is still
under a dollar a day. Language models are cheap per answer; they become expensive through volume, long contexts,
photos and loops.

Look at the answers too. "When are you open?" got an honest "I don't know": this chapter's Atlas has no tools and no
cards. And "Tell me everything about black holes, in as much detail as you can" was refused, although science
questions are allowed (our re-run refused the detail, then gave one sentence anyway): the visitor asked for detail, the system prompt said three short sentences, and the model
resolved the conflict by not answering. A cost rule in the prompt changes behaviour; check it with your golden set.
:::

:::step{type=concept title="Speed"}
Visitors feel two different times:

| Time | Depends on | Levers |
|---|---|---|
| **until the first word** | the input size, the provider's load, the network | fewer input tokens, a nearby region |
| **until the last word** | mostly the output length: models write tokens one by one | shorter answers, `maxTokens`, a smaller model |

Streaming (chapter 4) does not make the answer faster, but the first words appear after a few hundred milliseconds
instead of a few seconds, and that is what people notice. Every extra step adds a full model call: a tool call is two
calls, a judge (chapter 16) is one more, and the agent workflows of chapter 19 are several.

The cheapest and fastest call is the one you do not make: if a hundred visitors a day ask "When are you open?", the
answer can be cached, or better, the screen can show the hours without asking the model at all.
:::

:::step{type=concept title="Metrics: watching Atlas all day"}
The meter on one answer is useful; the director needs the totals, all day, every day. Spring Boot's way is **metrics**,
recorded with Micrometer and shown by **Spring Boot Actuator**. Spring AI records metrics for every model call by
itself, with the names of OpenTelemetry's conventions for AI:

| Metric | Counts |
|---|---|
| `gen_ai.client.token.usage` | tokens, by model and by type (input, output) |
| `gen_ai.client.operation` | model calls: how many, and how long they took |
| `spring.ai.chat.client` | calls through `ChatClient` |
| `spring.ai.advisor` | each advisor's work, for example retrieval |

Actuator shows them on `/actuator/metrics`, once the endpoint is exposed (only `health` is, by default). In production
the same numbers go to a monitoring system such as Prometheus, with a dashboard in Grafana and an alert when tokens per
hour jump.

:::diagram{name="ai-cost-meter"}
This chapter's real meter and metrics (26 November).
:::
:::

:::step{type=task task=ai_metrics title="Your turn: expose the metrics" file="18-production/src/main/resources/application.properties" line="11"}
Actuator is already in `18-production`'s `pom.xml`. In `application.properties`, expose its `health` and `metrics`
web endpoints: one line, `management.endpoints.web.exposure.include=health,metrics`.

The usual slip: `management.endpoint.web.exposure.include`, with "endpoint" singular. Spring Boot does not know that
name, so only `health` stays exposed, and `/actuator/metrics` answers 404.

Restart the app, ask one question, then:

```bash run
curl -s localhost:8080/actuator/metrics/gen_ai.client.token.usage | jq .
```

Press **Check**.
:::

:::step{type=try title="The meter, all day"}
After a few questions:

```text
$ curl -s localhost:8080/actuator/metrics/gen_ai.client.token.usage | jq .
{
  "availableTags": [
    {
      "tag": "gen_ai.operation.name",
      "values": [
        "chat"
      ]
    },
    {
      "tag": "gen_ai.response.model",
      "values": [
        "ai-chat"
      ]
    },
    {
      "tag": "gen_ai.request.model",
      "values": [
        "ai-chat"
      ]
    },
    {
      "tag": "gen_ai.token.type",
      "values": [
        "output",
        "input",
        "total"
      ]
    },
    {
      "tag": "gen_ai.system",
      "values": [
        "openai"
      ]
    }
  ],
  "description": "Measures number of input and output tokens used",
  "measurements": [
    {
      "statistic": "COUNT",
      "value": 848.0
    }
  ],
  "name": "gen_ai.client.token.usage"
}
```

The `availableTags` say how the numbers can be split. Careful with the total: `gen_ai.token.type` has three values,
`input`, `output` and `total`, and without a tag the endpoint adds all three. The three answers above read 296 tokens
and wrote 128, a total of 424; the untagged count, 848, counts every token twice. (Our re-run: input 296, output
131, total 427, untagged 854: twice again.) Always pick a type:

```text
$ curl -s "localhost:8080/actuator/metrics/gen_ai.client.token.usage?tag=gen_ai.token.type:output" | jq -c .measurements
[{"statistic":"COUNT","value":128.0}]
$ curl -s localhost:8080/actuator/metrics | jq -c "[.names[] | select(startswith(\"gen_ai\") or startswith(\"spring.ai\"))]"
["gen_ai.client.operation","gen_ai.client.token.usage","spring.ai.advisor","spring.ai.chat.client"]
```
:::

:::step{type=predict title="Guess first"}
:::question
Atlas sends 3 RAG chunks of about 100 tokens with every question. You change `topK` from 3 to 10. What happens to the
cost of an answer?
:::
- [ ] Nothing: retrieval is free
- [x] Input tokens grow by about 700 per question, so the input cost roughly triples or more
- [ ] Only the output gets longer
:::explain
Every retrieved chunk is input. More chunks can help hard questions, but each one is paid for on every call: measure
with the golden set (chapter 16) before paying for it.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does Atlas's system prompt say "at most three short sentences"?
:::
- [ ] To hide information
- [x] Output tokens cost the most and take the longest; short answers are cheaper, faster, and better for children
- [ ] The model cannot write more
:::explain
The answer's length is the biggest lever on both cost and time, and you control it with the prompt and `maxTokens`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where do the token numbers in `getUsage()` come from?
:::
- [ ] Spring AI estimates them from the text
- [x] The provider returns them with every response: they are what you are billed for
- [ ] Actuator counts them
:::explain
OpenAI (and every major provider) reports usage in each response; Spring AI passes it on and also feeds it into the
`gen_ai.client.token.usage` metric.
:::
:::

:::step{type=deep-dive title="Go deeper: running AI in production"}
**Budgets.** Put limits in front of the provider: per user, per day, per feature. The LabBox gateway you have used all
course is exactly that: every request goes through it, it counts tokens per account, and it stops at the daily budget
(you may have met its message: "Your AI budget for today is used up").

**Tracing.** With Micrometer Tracing, every model call, advisor and tool call becomes a span, so a slow answer shows
where its time went: retrieval, the model, or a tool. Spring AI can also record prompts and answers in traces
(`spring.ai.chat.observations.log-prompt=true`); leave it off where questions may hold personal data.

**Prompt caching.** OpenAI automatically gives a discount on the repeated beginning of long prompts (a long system
prompt, a long document); keeping the fixed parts at the start of the prompt helps it work. The provider's usage
data reports how many tokens were cached.

**Choosing the model.** A smaller model for simple steps (routing, classifying, judging) and a stronger one for hard
answers is the most common big saving. Measure quality with your golden set before you switch.
:::

:::step{type=recap}
You can now:

- list where an answer's tokens come from, and the levers that reduce them;
- read an answer's usage from `chatResponse().getMetadata().getUsage()`, and price it;
- explain the two times visitors feel, and what streaming and shorter answers do for each;
- expose Spring AI's metrics with Actuator, and read `gen_ai.client.token.usage`.

Next, chapter 19: workflows and agents, where one question becomes several model calls.

:::photo{src="/lesson-images/spring-ai/springai-18-notes.webp" alt="Sketchnote, What Atlas costs (usage, price and metrics): Every answer reports how many tokens it read and wrote. Price each answer, and count them all day with metrics. The flow: Answer, Usage: 95 in, 27 out, Price: $0.00003, Metrics on /actuator. What we measured: about 95 tokens in, mostly the system prompt; output costs 4 times as much as input; 6,000 answers a day: about 25 cents; no tag on the metric: every token counted twice." ai="true"}
One page of notes for this chapter.
:::
:::
