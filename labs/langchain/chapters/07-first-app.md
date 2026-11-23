:::step{type=story title="One interface for every model"}
Chapters 5 and 6 talked to one provider's API. The co-op's IT volunteer asks a fair question: "What if next year a
cheaper model comes out from another company, or we want to run one on our own computer?" With the OpenAI SDK, every
call would have to be rewritten.

**LangChain** answers that. Every chat model, from OpenAI, Anthropic, Google, Mistral, or one running locally, sits
behind the same interface: `model.invoke(messages)` in, an `AIMessage` out. Messages are objects, not dictionaries.
And everything the rest of this course builds, agents, tools, memory, retrieval, works with any of those models.

:::mission
Create Navin's chat model with `init_chat_model`, then ask a question with a system message and a human message as
objects.
:::
:::

:::step{type=history title="LangChain: from a side project to 1.0"}
:::before{title="Glue code, again and again"}
In 2022 every team building on GPT-3 wrote the same glue: prompt templates, calling the API, parsing the answer,
remembering the conversation, calling tools. Each team's version was a little different, and none could switch models.
:::

In **October 2022**, a month before ChatGPT, Harrison Chase released **LangChain** as an open-source Python project: a
toolbox of building blocks for applications on language models. It grew faster than almost any open-source project of
its time, and LangChain became a company in **2023**. The library was split into a small core (`langchain-core`),
one package per provider (`langchain-openai`, ...), and the main package. **LangChain 1.0**, released in **October
2025**, focused it on agents built on LangGraph, with `init_chat_model` and `create_agent` at the centre. This course
uses **1.5**.

:::solved
**Swap the model, keep the program.** One interface for dozens of providers, and the same building blocks on top.
:::

:::timeline
- **2022** LangChain released (Python).
- **2023** LangChain the company; the JavaScript version.
- **2025** LangChain 1.0: agents first.
:::
:::

:::step{type=concept title="init_chat_model: provider, colon, model" file="07-first-app/app.py" line="8-11"}
`init_chat_model` builds the right class from a string:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:ai-chat", temperature=0)   # a ChatOpenAI
# init_chat_model("anthropic:claude-...")  would give a ChatAnthropic, with the same methods
```

The part before the colon picks the integration package (`langchain-openai` here), the part after is the model name the
API expects (our gateway's `ai-chat`). Like the SDK, it reads `OPENAI_BASE_URL` and `OPENAI_API_KEY` from the
environment.

| Part 2 so far | Chapter 5 (HTTP) | Chapter 6 (SDK) | Chapter 7 (LangChain) |
|---|---|---|---|
| Who builds the JSON | you | the SDK | LangChain, then the SDK |
| Messages | dictionaries | dictionaries | objects |
| Switch provider | rewrite | rewrite | change one string |
:::

:::step{type=task task=chat_model title="Your turn: Navin's chat model" file="07-first-app/app.py" line="8-11"}
Finish `chat_model()`: return `init_chat_model("openai:ai-chat", temperature=0)`.

Press **Check**.
:::

:::step{type=concept title="Messages as objects" file="07-first-app/app.py" line="14-17"}
LangChain's message classes match chapter 5's roles:

| Class | Role in the request | Who writes it |
|---|---|---|
| `SystemMessage` | `system` | you: Navin's instructions |
| `HumanMessage` | `user` | the member |
| `AIMessage` | `assistant` | the model (what `invoke` returns) |
| `ToolMessage` | `tool` | your code, with a tool's result (chapter 10) |

`model.invoke([SystemMessage(SYSTEM), HumanMessage(question)])` returns an `AIMessage`; its `.content` is the text, and
it also carries `.usage_metadata` (tokens) and `.response_metadata` (the raw details). You can also pass a plain string,
`model.invoke("Hello")`, which becomes one `HumanMessage`.
:::

:::step{type=task task=system_message title="Your turn: ask with a system message" file="07-first-app/app.py" line="14-17"}
Finish `ask(model, question)`: call `model.invoke([...])` with a `SystemMessage(SYSTEM)` and a `HumanMessage(question)`,
and return the reply's `.content`.

```bash run
cd /workspace/07-first-app && python main.py
```

Press **Check**.
:::

:::step{type=try title="Navin introduces itself"}
```text
$ python main.py
ChatOpenAI
Welcome to the cooperative! I can help you with information about growing onions, grapes, and tomatoes, as well as tips on farming practices and market prices. If you have any specific questions, feel free to ask!
```

`init_chat_model` built a `ChatOpenAI`, and the reply is friendly and short, as the system message asked.

But Navin just promised "tips on farming practices", something nobody asked it to do and the co-op cannot stand behind.
A system message says who Navin is; it does not say what Navin must **not** do. Later chapters narrow that down: facts to
answer from (chapter 9), tools that do the real work (chapter 12), guardrails (chapter 24).
:::

:::step{type=predict title="Guess first"}
:::question
The co-op switches to a model from another provider. Which line changes?
:::
- [x] The `init_chat_model("...")` string (and installing that provider's package)
- [ ] Every `invoke` call
- [ ] The message classes
:::explain
The rest of the program only knows the chat model interface. That is the whole point of LangChain's model layer.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `model.invoke(...)` return?
:::
- [ ] A string
- [x] An `AIMessage`, with `.content`, `.usage_metadata` and more
- [ ] The raw JSON reply
:::explain
The message object keeps the text together with the tokens and metadata.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where do you tell the model how to behave?
:::
- [x] In a `SystemMessage` at the start of the messages
- [ ] In the `HumanMessage`
- [ ] In `init_chat_model`
:::explain
The system message carries the instructions; the human message carries what the member typed.
:::
:::

:::step{type=deep-dive title="Go deeper: the model layer"}
**Batch and async.** Every chat model also has `batch([...])` (many questions in parallel) and `ainvoke` (for async
web servers), with no extra code.

**Configurable models.** `init_chat_model(configurable_fields=("model", "temperature"))` lets you choose the model per
call, useful for routing easy questions to a cheaper model.

**Packages.** `langchain-core` holds the interfaces (messages, chat models); each provider has its own small package. You
install only the providers you use.
:::

:::step{type=recap}
You can now:

- explain what LangChain adds on top of a provider's SDK;
- create a chat model with `init_chat_model("provider:model")`;
- send `SystemMessage` and `HumanMessage` objects and read the `AIMessage`;
- notice when a model promises more than your system message asked for.

Next, chapter 8: model parameters, and answers that stream in piece by piece.

:::photo{src="/lesson-images/langchain/lc-07-notes.webp" alt="Handwritten notes about a first LangChain app: init_chat_model(provider:model); SystemMessage, HumanMessage; invoke returns an AIMessage; Swap a model: one string; It promised farming tips" ai="true"}
One page of notes for this chapter.
:::
:::
