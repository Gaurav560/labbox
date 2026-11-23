:::step{type=story title="How is Setu doing?"}
A week after launch, two questions arrive on the same morning. Finance asks: "How many model calls did Setu make
yesterday, and what did they cost?" And a developer asks: "I shortened the system message. Is Setu still as good?"

Nobody can answer either. The first needs **observability**: seeing what the application does while it runs. The
second needs **evaluation**: a repeatable measure of answer quality, so a change can be compared with the version
before it. Ordinary unit tests cannot do this on their own, because a model's answers are not fixed.

LangChain4j gives you the hook for the first, a **chat model listener**, and the second is a small amount of plain
Java that you will write: a **golden set** of questions with answers you know are right.

:::mission
Count every call and token with a `ChatModelListener`, and score Setu against six golden questions.
:::
:::

:::step{type=history title="From logs to traces to evals"}
:::before{title="Reading log files"}
For decades, knowing what a server did meant searching its log files. When one request passed through ten services,
nobody could follow it from start to end.
:::

"Observability" is a word from control theory (Rudolf Kálmán, **1960**): how well you can tell a system's inner state
from its outputs. Software borrowed it in the 2010s. Google's **Site Reliability Engineering** book (**2016**) made
monitoring a discipline, and **OpenTelemetry** (**2019**), formed by merging OpenTracing and OpenCensus, became the
standard way to record metrics and traces. In **2024** OpenTelemetry added conventions for generative AI: model
name, input tokens and output tokens for every call.

Quality needed something new. When OpenAI released GPT-4 in **March 2023** it also open-sourced **OpenAI Evals**, a
framework for scoring models on sets of questions with known answers. Teams building on models adopted the same
idea for their own apps, under the name **evals**.

:::solved
**Numbers instead of impressions.** Listeners give cost and traffic; a golden set gives a quality score. Together
they turn "I think it is fine" into "94% of the golden set, $0.45 a day".
:::

:::timeline
- **1960** Kálmán defines observability for control systems.
- **2016** Google's SRE book.
- **2019** OpenTelemetry.
- **2023** OpenAI Evals; evals become a practice.
- **2024** OpenTelemetry conventions for generative AI.
:::

**Rudolf Kálmán**, who defined observability for control systems in 1960, photographed in 2008 when he received the Charles Stark Draper Prize for his work.

:::photo{src="/lesson-images/langchain4j/rudolf-kalman.webp" alt="Rudolf Kalman in 2008, white-haired, in a dark suit and patterned tie, in front of a blue wall" credit="ETH-Bibliothek Zurich, Image Archive" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AETH-BIB-Kalman%2C_Rudolf_E._%281930-2016%29-HK_04-01925.jpg"}
Rudolf Kálmán in 2008.
:::
:::

:::step{type=concept title="A listener sees every call" file="26-observability/src/main/java/com/setu/Models.java" line="15-22"}
A `ChatModelListener` has three methods, all optional:

| Method | Called | You get (from the context) |
|---|---|---|
| `onRequest` | Before each call | `chatRequest()`: the messages, the tools, the parameters |
| `onResponse` | After each answer | `chatResponse()`: the answer and its `metadata()`, with `tokenUsage()` and the finish reason |
| `onError` | When a call fails | `error()`: the exception, for example a rate limit |

Every context also has `attributes()`, a map shared between `onRequest` and `onResponse` of the same call, useful for
timing: put the start time in on the request, read it back on the response.

You attach listeners where the model is built, so **nothing else in Setu changes**:

```java
OpenAiChatModel.builder()
        ...
        .listeners(List.of(new UsageLog()))
        .build();
```

`Models.chatModel(baseUrl, apiKey, listeners...)` already does this. The listener sees every call, including the
ones AI Services make for tools, which your own code never sees directly.
:::

:::step{type=task task=usage_listener title="Your turn: count calls and tokens" file="26-observability/src/main/java/com/setu/UsageLog.java" line="15-19"}
Finish `UsageLog.onResponse`: add 1 to `calls`, then add the response's input and output tokens
(`context.chatResponse().metadata().tokenUsage()`, with `inputTokenCount()` and `outputTokenCount()`) to
`inputTokens` and `outputTokens`.

Press **Check**.
:::

:::step{type=concept title="Testing an app whose answers change"}
How do you test code that calls a model? Two kinds of test, for two different questions:

| Test | Question | Model | Runs |
|---|---|---|---|
| **Unit test with a fake model** | Does my code do the right thing with an answer? | A fake server with fixed answers | Every build, in milliseconds, free |
| **Eval with a golden set** | Are the answers good? | The real model | Before each change of prompt or model, costs cents |

You have been using the first kind all course: every **Check** you pressed ran your code against a fake
OpenAI-compatible server that returns fixed answers and records every request. That is how the checks know you sent
the system message, or offered the right tools, without paying for a single token.

An eval is different: real questions, the real model, and a rule for "right". The simplest rule is that the answer
contains a word that must be there. `Eval.GOLDEN` has six such pairs, taken from Setu's facts:

| Question | Must contain |
|---|---|
| When does the Ghat Express leave Pune? | 07:15 |
| How much is a ticket from Pune to Ratnagiri? | 420 |
| Does the Konkan Breeze run on Tuesdays? | not |
| When does the Monsoon Mail reach Karjat? | 18:40 |
| Do small children need a ticket? | free |
| Is there wifi on the Ghat Express? | don't know |

The last row matters most: an honest "I don't know" is a right answer, and inventing one is a wrong one.
:::

:::step{type=task task=golden_eval title="Your turn: the golden set" file="26-observability/src/main/java/com/setu/Eval.java" line="23-28"}
Finish `Eval.passRate(assistant, golden)`: ask every golden question, count the answers that contain `mustContain`
(lower-case both with `toLowerCase(Locale.ROOT)` so capitals do not matter), and return `passed / golden.size()` as a
`double`.

```bash run
cd /workspace/26-observability && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="A score, a bill, and a regression caught"}
```text
$ mvn -q compile exec:java
golden set: 100% of 6 questions passed
usage: 6 calls, 1418 tokens in, 98 tokens out, $0.000272
```

Six calls for six questions, and the listener counted them without one line of Setu's code knowing. At
$0.000045 a question, 10,000 questions a day cost about $0.45. Notice the ratio as well: 1,418 tokens in and 98 out.
Most of what Setu reads is the system message and the facts, sent again with every question (chapter 12 counted
the same thing). Output tokens cost four times as much, but here there are few of them.

Now the developer's change. We removed one sentence from `setu-system.txt`, the one that says to answer "I don't
know" when the facts do not say, and ran the same eval:

```text
$ mvn -q compile exec:java
  MISSED: Is there wifi on the Ghat Express? -> no, the ghat express does not offer wi-fi services.
golden set: 83% of 6 questions passed
usage: 6 calls, 1238 tokens in, 85 tokens out, $0.000237
```

The shorter prompt saved 180 tokens and made Setu **invent a fact**. Nothing in the facts says the Ghat Express has
no wifi; the model made it up and said it with confidence. Without the golden set, that change would have shipped,
and the first person to notice would have been a passenger. With it, the change failed in a minute, for less than a
tenth of a cent.
:::

:::step{type=predict title="Guess first"}
:::question
You switch Setu to a cheaper model. Which test tells you whether the answers got worse?
:::
- [ ] The unit tests with the fake model
- [x] The golden set, run on the real new model
- [ ] Neither: answers cannot be measured
:::explain
The fake model returns fixed answers, so it tests your code, not the model. Only an eval on the real model measures
answer quality.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the listener count more calls than Setu's code makes, when tools are used?
:::
- [x] An AI Service makes extra calls for tool results, and the listener sees every call to the model
- [ ] Listeners count twice
- [ ] The gateway adds calls
:::explain
A question with one tool call is two model calls: one that asks for the tool, one that answers with its result.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The golden set passes 100%. Is Setu correct?
:::
- [ ] Yes, it has been proven
- [x] It is correct on these six questions; a bigger, more varied set gives more confidence
- [ ] No, evals are meaningless
:::explain
A golden set is a sample. Add every real question that went wrong in production, so the same mistake cannot return.
:::
:::

:::step{type=deep-dive title="Go deeper: observability for real"}
**Metrics.** The `langchain4j-micrometer-metrics` module records calls, tokens and durations as Micrometer metrics,
so they appear in Prometheus and Grafana like any other Spring Boot metric.

**AI Service events.** Besides model listeners, LangChain4j can report AI Service events: when a service starts,
calls a tool, retrieves content or applies a guardrail. Useful to see a whole conversation, not only model calls.

**LLM as a judge.** "Contains 07:15" works for facts. For tone or completeness, teams ask a second model to grade
the answer against a rubric. It costs calls and can be wrong itself; check its grades against yours on a sample.

**Logging prompts.** `.logRequests(true)` on a model builder logs every request. Useful in development; in
production remember that prompts contain what passengers typed (chapter 25's phone numbers).
:::

:::step{type=recap}
You can now:

- attach a `ChatModelListener` and read requests, responses, token usage and errors;
- tell a unit test with a fake model from an eval with the real one, and when to use each;
- score an assistant against a golden set and catch a regression before it ships;
- read cost from token counts.

Next, chapter 27: agents. AI Services that work together, each with one job.

:::photo{src="/lesson-images/langchain4j/l4j-26-notes.webp" alt="Handwritten notes about observability: a listener sees every call and every token; a fake model tests your code; a golden set tests the answers; a shorter prompt invented wifi; numbers, not impressions" ai="true"}
One page of notes for this chapter.
:::
:::
