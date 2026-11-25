:::step{type=story title="What is actually sent?"}
Part 1 explained what happens inside a model. Part 2 is about calling one, and it starts with the simplest possible
way: no AI library at all. A hosted chat model, like the one behind Navin, is a **web API**: a program on another computer that you use by
sending it requests over the internet. (Models can also run on your own machine, behind local servers like Ollama; the history below says
more.)
Navin sends an **HTTP request** (the kind of message a browser sends to load a page) carrying some **JSON** (text in
the form of keys and values, like a Python dict), and a JSON answer comes back. Everything later in this course, the OpenAI SDK, LangChain, agents, is built on that one request.

Knowing the raw request pays off for the rest of your career: when a library does something surprising, you can look
at what it really sent.

:::mission
Send Navin's first question to a real model with one HTTP POST, then read the answer out of the JSON reply.
:::
:::

:::step{type=concept title="One request, four parts" file="05-raw-http/http_call.py" line="9-17"}
Every chat call is a **POST** (the HTTP method for sending data, not just fetching a page) to
`<base URL>/chat/completions`, with:

| Part | Here | Why |
|---|---|---|
| URL | `os.environ["OPENAI_BASE_URL"] + "/chat/completions"` | Your lab machine talks to LabBox's gateway, which forwards to OpenAI |
| Header | `Authorization: Bearer <OPENAI_API_KEY>` | Who is asking (here a lab token, valid only at the gateway) |
| `model` | `"ai-chat"` | The gateway's name for the model (gpt-4o-mini) |
| `messages` | a list of `{"role", "content"}` | The conversation: a **system** message with Navin's instructions, then the **user**'s question |

The **system** message is how you tell the model who it is and how to behave; the **user** message is what the member
typed. Later, **assistant** messages hold the model's own earlier answers.

A **header** is a line of extra information sent with the request; `Authorization` says who is asking. An
**environment variable** is a named setting the machine gives every program; your lab machine has both set: run
`echo $OPENAI_BASE_URL` in the terminal. The key is a lab
token: the real OpenAI key never leaves the LabBox server.

:::diagram{name="lc-chat-request"}
Chapter 5's real request, there and back, with the numbers from the gateway's log.
:::

**Tim Berners-Lee** invented the World Wide Web and its protocol, HTTP, at CERN between 1989 and 1991. Every call to a model in this course is one of his HTTP requests.

:::photo{src="/lesson-images/langchain/tim-berners-lee.webp" alt="Tim Berners-Lee in a dark suit, smiling, arriving at a formal event" credit="Paul Clarke" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ASir_Tim_Berners-Lee.jpg"}
Sir Tim Berners-Lee in London.
:::
:::

:::step{type=history title="From completions to chat"}
:::before{title="Text in, text out"}
OpenAI's API opened in **June 2020** with GPT-3 and one idea: send a piece of text, get its continuation. To build a
chat, every application glued the conversation into one long text in its own format.
:::

On **1 March 2023** OpenAI released the **Chat Completions API** with gpt-3.5-turbo: messages with roles (system, user,
assistant) instead of one blob of text. It was simple enough that many other providers and model servers, including the local servers Ollama
and vLLM, now offer an endpoint that accepts the same request, which is why one LangChain class can talk to so many of
them.

:::solved
**One shape for many models.** Learn this request once and you can read the traffic of almost any AI application.
:::

:::timeline
- **2020** The OpenAI API with GPT-3: completions.
- **2023** Chat Completions: messages with roles.
- **2024** Many servers accept the same request format.
:::
:::

:::step{type=example title="Worked example: a POST with httpx" file="05-raw-http/http_call.py" line="9-14"}
`httpx` is a modern Python HTTP client (the OpenAI SDK itself uses it). Posting JSON with a header looks like this (a
different API, only to read):

```python
response = httpx.post("https://example.org/api/orders",
                      headers={"Authorization": "Bearer abc123"},
                      json={"crop": "onion", "crates": 40},     # httpx turns the dict into JSON
                      timeout=60)
response.raise_for_status()                                       # an HTTP error becomes an exception
data = response.json()                                            # the JSON reply as a dict
```
:::

:::step{type=task task=send_request title="Your turn: send the request" file="05-raw-http/http_call.py" line="12-15"}
Finish the first part of `ask(question)`. `url` and `key` are already read from the environment variables.

1. Build the body: `{"model": "ai-chat", "messages": [...]}` with two messages, first
   `{"role": "system", "content": SYSTEM}`, then `{"role": "user", "content": question}`.
2. `httpx.post(url, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=60)`.
3. `response.raise_for_status()`, then keep `response.json()` in `reply`.

The usual slips:

- Writing `Bearer` without the space after it: the gateway then rejects the key.
- Putting the user message first: the system message must come first.

Press **Check**.
:::

:::step{type=task task=read_answer title="Your turn: read the answer" file="05-raw-http/http_call.py" line="16-17"}
The answer is inside the reply at `choices[0].message.content`. In Python: `reply["choices"][0]["message"]["content"]`.
Return it.

The usual slip: returning `reply` or `reply["choices"][0]`, which prints a whole dict instead of the answer.

```bash run
cd /workspace/05-raw-http && python main.py
```

Then look at exactly what went over the wire, as the gateway saw it:

```bash run
lab requests --last
```

Press **Check**.
:::

:::step{type=try title="The whole conversation, both ways"}
A real run (the model's wording changes from run to run; the numbers stayed the same when we ran it again on 25
November):

```text
$ python main.py
The co-op office is open from 9 AM to 5 PM, Monday to Saturday. It is closed on Sundays. If you need help, feel free to visit during these hours!
$ lab requests --last
2026-11-23 12:31:45 UTC  ai-chat -> openai/gpt-4o-mini  61 in, 38 out

--- request ---
{"model": "ai-chat", "messages": [{"role": "system", "content": "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."}, {"role": "user", "content": "When is the co-op office open?"}], "max_tokens": 1024}

--- response ---
{"id": "chatcmpl-EnNUuRVn22KaNTry8KoHX04zBH1Rg", "object": "chat.completion", "created": 1795437104, "model": "gpt-4o-mini-2024-07-18", "choices": [{"index": 0, "message": {"role": "assistant", "content": "The co-op office is open from 9 AM to 5 PM, Monday to Saturday. It is closed on Sundays. If you need help, feel free to visit during these hours!", "refusal": null, "annotations": []}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 61, "completion_tokens": 38, "total_tokens": 99, ...}, ...}
```

(The usage block is shortened with "...".) Three things to notice:

1. The gateway added `"max_tokens": 1024`: a ceiling on every answer, so no lab can run up a huge bill by accident.
2. `usage` counts **61** tokens in. Chapter 2's `count_tokens` gives 42 for the system message and 8 for the
   question: 50. The other 11 are the formatting around the two messages, and they are paid for too.
3. Read the answer. **Nobody told Navin the office hours.** The system message has none. The model wrote common office
   hours, and they happen to match the co-op's (Monday to Saturday, 9:00 to 17:00, from chapter 1). When we ran it
   again it answered "It is closed on Sundays and public holidays": the holidays are a guess too. For a question about
   something less common, the guess will be wrong and sound just as sure. Chapter 9 deals with that.
:::

:::step{type=predict title="Guess first"}
:::question
You leave out the system message and send only the question. What changes?
:::
- [ ] The API refuses the request
- [x] The model answers as a general assistant: it no longer knows it is Navin or how short to be
- [ ] Nothing at all
:::explain
The system message is the only place the model learns who it is. Without it, the answer is generic.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where is the answer text in a chat completion reply?
:::
- [ ] `reply["answer"]`
- [x] `reply["choices"][0]["message"]["content"]`
- [ ] `reply["usage"]["content"]`
:::explain
`choices` is a list because you can ask for several answers at once; usually there is one.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does the lab machine have a lab token instead of the real OpenAI key?
:::
- [x] So the real key never leaves the server, and each lab's use can be limited and counted
- [ ] Because OpenAI requires it
- [ ] To make requests faster
:::explain
The gateway checks the token, applies budgets, then calls OpenAI with the real key on the server.
:::
:::

:::step{type=deep-dive title="Go deeper: the raw API in production"}
**Errors.** A `429` means too many requests (rate limit); a `401`, a bad key; a `400`, a request the API cannot read
(often a context too long). `raise_for_status()` turns each into an exception your code must handle.

**finish_reason.** `stop` means the model ended its answer; `length` means it hit `max_tokens` mid-sentence. Check it
before showing an answer.

**Timeouts.** Answers can take many seconds. A timeout (here 60 seconds) keeps one slow call from hanging a whole web
request.
:::

:::step{type=recap}
You can now:

- describe a chat completion request: URL, key, model and messages;
- send one with httpx and read the answer out of the JSON;
- read the gateway's log of a real request and its usage;
- spot an answer the model guessed instead of knew.

Next, chapter 6: the same call with the official OpenAI Python SDK.

:::photo{src="/lesson-images/langchain/lc-05-notes.webp" alt="Handwritten notes about calling a model over HTTP: A hosted chat model is a web API: an HTTP POST, JSON in and out. The body names the model and lists the messages. The system message comes first; the user message follows. The answer is at choices[0].message.content. Usage counts every token, formatting included. Nobody told the model the office hours: it guessed." ai="true"}
One page of notes for this chapter.
:::
:::
