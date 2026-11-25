:::step{type=story title="The finance team's question"}
Before Sahyadri Rail approves Setu for the monsoon season, the finance team asks the question every AI project gets
eventually: **what will it cost?** "Cheap" is not an answer. They want a number per question, per day and per year, and
a way to see it every month.

You do not have to guess. Every response from a model comes with a receipt: how many tokens went in, how many came out,
which model answered and why it stopped. LangChain4j puts that receipt in the `ChatResponse`, next to the answer.

:::mission
Read the token usage of every answer, turn it into dollars, and work out Setu's bill for a season.
:::
:::

:::step{type=concept title="The receipt: ChatResponse metadata"}
A `ChatResponse` has two parts: the `aiMessage()` (the answer) and the `metadata()`, a `ChatResponseMetadata` with:

| Method | What it tells you |
|---|---|
| `tokenUsage()` | A `TokenUsage`: `inputTokenCount()`, `outputTokenCount()`, `totalTokenCount()` |
| `finishReason()` | Why the model stopped: `STOP` (it finished), `LENGTH` (it hit the limit), `TOOL_EXECUTION` (it wants a tool, chapter 19), `CONTENT_FILTER` |
| `modelName()` | The model the server says answered (OpenAI reports the exact version, such as `gpt-4o-mini-2024-07-18`; the LabBox gateway reports the alias) |
| `id()` | The provider's id for this call, useful when you report a problem |

These numbers come from the model's server, so they are what you are billed for. Input tokens are everything you sent:
the system message, any facts, the history and the question. Output tokens are the answer.

gpt-4o-mini costs **$0.15 per million input tokens** and **$0.60 per million output tokens**: output is four times
dearer, because every output token needs its own pass through the model (chapter 6).

**Check yourself:** this chapter's system message is 24 tokens (we counted it with gpt-4o-mini's tokenizer). Over 400
questions, how many tokens is that? (9,600 input tokens a day, just for the instructions: small, but it is why long
system prompts and long fact lists matter.)
:::

:::step{type=example title="Worked example: a cost formula" file="12-usage/src/main/java/com/setu/Bill.java" line="10-11"}
The prices sit at the top of `Bill.java`:

```java
static final double INPUT_PER_MILLION = 0.15;
static final double OUTPUT_PER_MILLION = 0.60;
```

One answer with 180 input tokens and 60 output tokens costs:

| Part | Tokens | Price per million | Cost |
|---|---|---|---|
| Input | 180 | $0.15 | $0.000027 |
| Output | 60 | $0.60 | $0.000036 |
| **Total** | | | **$0.000063** |

In Java, watch the arithmetic: `180 * 0.15 / 1_000_000` works because `0.15` makes it a `double` calculation. Writing
`180 / 1_000_000 * 0.15` gives 0, because `180 / 1_000_000` is integer division first.
:::

:::step{type=task task=token_usage title="Your turn: read the receipt" file="12-usage/src/main/java/com/setu/Bill.java" line="20-24"}
Finish `Bill.usage(response)`: get the `TokenUsage` from `response.metadata().tokenUsage()` and return
`new Usage(inputTokenCount, outputTokenCount)`:

1. `TokenUsage t = response.metadata().tokenUsage();`
2. `return new Usage(t.inputTokenCount(), t.outputTokenCount());`

The usual slip: `totalTokenCount()` for one of the two. The bill then prices the whole call at one rate.

Press **Check**.
:::

:::step{type=task task=answer_cost title="Your turn: tokens to dollars" file="12-usage/src/main/java/com/setu/Bill.java" line="26-30"}
Finish `Bill.dollars(usage)`: input tokens at `INPUT_PER_MILLION` per million, plus output tokens at
`OUTPUT_PER_MILLION` per million:
`return usage.inputTokens() * INPUT_PER_MILLION / 1_000_000 + usage.outputTokens() * OUTPUT_PER_MILLION / 1_000_000;`

The usual slip is the one in the worked example: dividing the token count by `1_000_000` first, which is integer
division and gives 0.

```bash run
cd /workspace/12-usage && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="A season of Setu"}
```text
$ mvn -q compile exec:java
Q: Hi!
  model ai-chat, finish STOP, 37 in, 9 out, $0.000011
Q: Explain in detail how a train climbs a steep ghat section.
  model ai-chat, finish STOP, 48 in, 66 out, $0.000047

400 questions a day, about 180 tokens in and 60 out each: $0.0252 a day, $9.20 a year
```

(We ran it again on 26 November: 37 in and 9 out for the greeting again; 48 in and 81 out for the long question,
$0.000056.)

A greeting cost 37 tokens in and 9 out: most of the 37 are Setu's instructions (24 tokens), which travel with every
question; "Hi!" is 2, and the rest is the format that marks where each message starts and ends. The
detailed question cost four times as much, almost all of it in output tokens. `modelName()` says `ai-chat` because
the gateway answers with the alias; called directly, OpenAI reports the exact version, such as
`gpt-4o-mini-2024-07-18`.

For 400 questions a day the model costs a few cents a day and a few dollars a year: far less than the electricity of
the station's lights. That is the honest headline for most help desk assistants. What makes AI bills big is not the
price per token, it is **volume and length**: long documents pasted into every prompt, long conversations sent back in
full each time (chapter 17), and long answers. Those are the things to measure, and now Setu can.
:::

:::step{type=predict title="Guess first"}
:::question
Setu starts sending the whole 20-page rules book with every question (about 10,000 tokens). What happens to the cost per
question?
:::
- [ ] Nothing: the answer is the same length
- [x] It rises about twenty-five-fold, because the rules book is input tokens on every call
- [ ] It falls, because the answers get shorter
:::explain
Everything sent is billed, every time. With the chapter's typical question (180 in, 60 out), the cost goes from
$0.000063 to $0.001563: the input part alone grows 56 times, the whole question about 25 times. Chapter 23 sends only the few paragraphs that matter, which is why retrieval is
as much about cost as about quality.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which is cheaper with gpt-4o-mini: 1,000 input tokens or 1,000 output tokens?
:::
- [x] Input tokens: output tokens cost four times as much
- [ ] Output tokens
- [ ] They cost the same
:::explain
$0.15 against $0.60 per million. Short answers save more than short questions.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
`finishReason()` is `LENGTH`. What happened?
:::
- [ ] The answer was complete
- [x] The answer hit the maxOutputTokens limit and was cut off
- [ ] The question was too long
:::explain
LENGTH means cut off. Log it: frequent LENGTH answers mean a limit that is too low or answers that are too long.
:::
:::

:::step{type=deep-dive title="Go deeper: cost in production"}
**Log usage with every answer.** Store the input and output tokens and the model name for each call; monthly bills
become a database query instead of a surprise. Chapter 26 sends the same numbers to metrics.

**Budgets.** The LabBox gateway enforces a daily token budget per learner: the same idea protects a company from a
runaway loop or an attack. Set one in your own gateway or provider dashboard.

**Prompt caching.** Providers discount input tokens that repeat at the start of a prompt (a long system message sent
with every call). OpenAI does it automatically for long prompts; LangChain4j exposes cache options for it.

**Choose the model per job.** A small model for routing and classifying, a stronger one only where needed (chapter 24,
model routing).
:::

:::step{type=recap}
You can now:

- read a `ChatResponse`'s metadata: token usage, finish reason, model name;
- turn token usage into dollars, with separate input and output prices;
- estimate an assistant's daily and yearly cost;
- explain what really drives AI bills: volume and length.

That is the end of Part 2. Next, chapter 13: AI Services, LangChain4j's high-level API, where you describe Setu as a
Java interface and LangChain4j writes the implementation.

:::photo{src="/lesson-images/langchain4j/l4j-12-notes.webp" alt="Sketchnote, What Setu costs (every answer comes with a receipt): Every ChatResponse carries its token usage and finish reason. Input and output tokens have different prices. The flow: ChatResponse, tokenUsage(), Tokens x price, Dollars. What we measured: Hi! cost 37 tokens in, 24 of them the instructions; output costs 4 times as much as input; 400 questions a day: about 9 dollars a year; a 10,000-token rule book: 25 times dearer." ai="true"}
One page of notes for this chapter.
:::
:::
