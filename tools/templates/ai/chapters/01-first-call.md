:::step{type=story title="A bookshop bot"}
:::character{name="Kabir" role="Backend lead, Book Point"}
Customers keep asking the counter staff the same questions. Let's put a small assistant on the
shop's screen. First step: talk to a language model from code.
:::

:::mission
Send a question to a model with a system message, and return its answer.
:::
:::

:::step{type=concept title="Messages in, a message out"}
A chat model takes a list of **messages**, each with a `role` and `content`:

- `system`: the rules ("you are a bookshop assistant, answer briefly");
- `user`: what the person asked.

It answers with one new `assistant` message. In this lab the model is called by its alias,
`lab-chat`, and your machine already has the address and key it needs.
:::

:::step{type=predict title="Guess first"}
:::question
You send the same question twice to a chat model. What comes back?
:::
- [ ] Exactly the same answer, always
- [x] Often a slightly different answer
- [ ] An error the second time
:::explain
Models sample their words, so answers vary a little. That is why the checks here look at what your
code sends, not at what the model says.
:::
:::

:::step{type=try title="Ask it something"}
```bash run
python -c "from openai import OpenAI; r = OpenAI().chat.completions.create(model='lab-chat', messages=[{'role': 'user', 'content': 'Say hi in five words'}]); print(r.choices[0].message.content)"
```

Then see exactly what was sent, with tokens and time:

```bash run
lab requests
```
:::

:::step{type=task task=ask title="Your first call"}
Make `ask(client, question)` in `bot.py` send `SYSTEM` and the question to `lab-chat`, and return
the reply text. Try it for real with `python bot.py "What is a cortado?"`.
:::

:::step{type=recap}
- A chat call is a list of messages in, one assistant message out.
- The system message sets the rules; the user message is the question.
- `lab requests` shows every call you made, with its tokens and cost.
:::
