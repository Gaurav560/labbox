:::step{type=story title="The same call, with less to get wrong"}
Chapter 5 built the request by hand: the URL, the header, the JSON keys, the path to the answer. Each was a chance for a
typo that only fails at run time. And it had no retries: if the gateway is busy for a second, the call just fails.

Most providers ship an official **SDK** (software development kit: a library made by the provider for its own API)
that does this for you. OpenAI's Python SDK knows every field, gives you typed
objects with autocomplete, retries busy calls, and applies timeouts. It also reads the token usage for you, which Navin
needs to know what each answer costs.

:::mission
Build an OpenAI client with a timeout and retries, then ask Navin's question and read both the answer and its token
usage.
:::
:::

:::step{type=concept title="A client, then a call" file="06-openai-sdk/sdk.py" line="9-19"}
Two objects:

| Object | Made | Holds |
|---|---|---|
| `OpenAI(...)` client | once, at start-up | base URL, key, timeout, retries, a pool of HTTP connections |
| `client.chat.completions.create(...)` | once per question | the same `model` and `messages` as chapter 5 |

```python
completion = client.chat.completions.create(model="ai-chat", messages=[...])
completion.choices[0].message.content    # the answer: attributes instead of ["keys"]
completion.usage.prompt_tokens           # 61
```

If you build `OpenAI()` with no arguments it reads `OPENAI_BASE_URL` and `OPENAI_API_KEY` from the environment by
itself. Passing them explicitly, as you will, makes it obvious where the client points.

`max_retries=2` makes the SDK try a failed call up to two more times, waiting a little longer each time. (2 is also the
SDK's default; writing it out makes the choice visible.) The SDK in your lab (version 3.57.0) retries only errors that
may pass by themselves: lost connections and timeouts, and the HTTP codes 408 (request timeout), 409 (conflict), 429
(too many requests) and 500 and above (server errors). A bad key (401) is never retried: trying again cannot fix it.
:::

:::step{type=history title="SDKs generated from the API"}
:::before{title="Hand-written clients"}
OpenAI's first Python library (2020) was written by hand, so every new API feature had to be added to it by hand too,
and responses came back as plain dictionaries with no types.
:::

In **November 2023** OpenAI released version 1.0 of `openai-python`, rewritten so that most of it is **generated** from
the API's own specification by a tool (from the company Stainless). A new API field appears in the SDK automatically,
with types. The SDK runs on `httpx`, the library you used in chapter 5, and has had frequent releases since; your lab
has version 3.57.0. In **March 2025** OpenAI added a second, newer endpoint, the **Responses API**; Chat Completions
remains the format most other providers and gateways speak, so this course uses it.

:::solved
**Typed, current, resilient.** Fewer typos, autocomplete in the editor, and retries and timeouts without writing them.
:::

:::timeline
- **2020** The first openai Python library.
- **2023** v1.0: generated from the API specification.
- **2025** The Responses API added.
:::
:::

:::step{type=task task=sdk_client title="Your turn: the client" file="06-openai-sdk/sdk.py" line="9-12"}
Finish `client()`: return `OpenAI(base_url=..., api_key=..., timeout=60, max_retries=2)`, with the base URL and key
read from the environment: `os.environ["OPENAI_BASE_URL"]` and `os.environ["OPENAI_API_KEY"]`.

The usual slip: `timeout="60"` (a string). The SDK wants a number of seconds.

Press **Check**.
:::

:::step{type=task task=sdk_ask title="Your turn: ask, and read the usage" file="06-openai-sdk/sdk.py" line="15-19"}
Finish `ask(openai, question)`:

1. `completion = openai.chat.completions.create(model="ai-chat", messages=[...])`, with the same two messages as
   chapter 5 (system first, then the question).
2. Return two things: `completion.choices[0].message.content` and `completion.usage`.

The usual slip: `completion["choices"]`. The SDK returns objects, so it is `completion.choices` with a dot.

```bash run
cd /workspace/06-openai-sdk && python main.py
```

Press **Check**.
:::

:::step{type=try title="A confident no"}
One real run (the wording changes from run to run; when we ran it again on 25 November it said "No, we do not store
tomatoes in cold storage. Tomatoes are better kept at room temperature.", 61 tokens in and 28 out):

```text
$ python main.py
No, we do not store tomatoes in cold storage. Tomatoes prefer a cool, dry place, but too much cold can ruin their taste. We keep them in a well-ventilated area instead.

61 tokens in, 41 tokens out
```

The SDK works: the answer, and the usage as attributes. Now read the answer as a co-op member would. The co-op **does**
store tomatoes in cold storage, at Rs 2 a crate a day (it is in the co-op's handbook, which Navin reads in chapter 9). Navin has never been told that, so it did what language models
do: it wrote a likely-sounding answer about tomatoes in general (it is true that cold can affect tomato flavour) and
presented it as the co-op's policy, "We keep them in a well-ventilated area instead", with complete confidence.

A member reading that might sell their tomatoes in a hurry instead of storing them. This is the **hallucination**
problem in one sentence, and it is the reason chapter 9 exists.
:::

:::step{type=predict title="Guess first"}
:::question
The gateway answers 429 (too many requests) on the first try and works on the second. With `max_retries=2`, what does
your code see?
:::
- [ ] An exception
- [x] The answer: the SDK retried by itself, a little later
- [ ] Two answers
:::explain
Retries with a growing wait turn short-lived errors into a small delay.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `completion.usage.prompt_tokens` count?
:::
- [x] The tokens the model read: system message, question and their formatting
- [ ] The words of the question
- [ ] The tokens of the answer
:::explain
Input (prompt) and output (completion) tokens are counted and priced separately.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why was Navin's answer about tomatoes wrong?
:::
- [ ] The SDK changed the question
- [x] The model was never given the co-op's facts, so it answered from general knowledge as if it knew
- [ ] Temperature was too high
:::explain
A model knows the world in general, not your co-op. Facts must be given to it (chapter 9, and RAG in Part 4).
:::
:::

:::step{type=deep-dive title="Go deeper: the SDK in production"}
**One client per program.** A client holds a pool of connections; make it once and reuse it, not once per question.

**Async.** `AsyncOpenAI` has the same methods, used with `await`, so one program can wait for many answers at once:
useful for a web server answering many members together.

**Errors.** The SDK raises typed exceptions (`openai.RateLimitError`, `openai.APITimeoutError`,
`openai.AuthenticationError`), so you can handle each case on purpose.
:::

:::step{type=recap}
You can now:

- build an OpenAI client with a base URL, key, timeout and retries;
- call `chat.completions.create` and read typed results and token usage;
- explain which errors are retried and why;
- recognise a confident hallucination about your own business.

Next, chapter 7: LangChain. One interface for every model, and messages as objects.

:::photo{src="/lesson-images/langchain/lc-06-notes.webp" alt="Handwritten notes about the OpenAI SDK: An SDK is the provider's own library for its API. Make one client and reuse it for every call. The SDK retries errors that may pass, like 429 and 500. A bad key, 401, is never retried. Usage reports tokens in and tokens out. Navin said no about tomatoes: wrong, and sure of itself." ai="true"}
One page of notes for this chapter.
:::
:::
