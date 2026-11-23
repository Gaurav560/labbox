:::step{type=story title="A confident wrong answer"}
In chapter 6 Navin told a member, with complete confidence, that the co-op does not store tomatoes. It does. In chapter
5 it stated office hours nobody had given it, and happened to be right. A help desk that sometimes invents the co-op's
rules is worse than no help desk: a farmer who believes it may sell a harvest in a hurry, or pick grapes too early
after spraying.

This is called **hallucination**, and it is the most important thing to design around in any AI application. The
model is not lying; it produces likely text, and a likely-sounding answer is not the same as a true one. Two defences
work together: **give the model the facts**, and **give it permission to say "I don't know"**.

And since every answer has a price, this chapter also reads the bill: tokens in, tokens out, dollars.


Grapes ripening in a vineyard near Nashik. An invented answer about when they may be picked after spraying is not a small mistake: the co-op's rule is 10 days.

:::photo{src="/lesson-images/langchain/grapes-nashik.webp" alt="A bunch of dark grapes hanging among green vine leaves, with the low sun shining through" credit="Savitr1915" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AGrapes._Nasik.jpg"}
Grapes at a vineyard in Nashik.
:::
:::mission
Write an honest system prompt with the co-op's facts and an "I don't know" rule, then compute the cost of each answer
from its token usage.
:::
:::

:::step{type=history title="Fake cases and a chatbot's refund"}
:::before{title="Trusting fluent text"}
Fluent writing used to be a sign that someone knew what they were talking about. Language models broke that link.
:::

In **2023**, in the case **Mata v. Avianca** in New York, two lawyers filed a brief citing court decisions that did not
exist: ChatGPT had invented them, with names, dates and quotes. The judge fined them in June 2023. In **February 2024** a
Canadian tribunal ordered Air Canada to honour a bereavement refund policy its website chatbot had invented
(**Moffatt v. Air Canada**): the airline argued the chatbot was responsible for its own words, and lost. The lesson for
every company: **your assistant's words are your words**.

:::solved
**Ground and permit.** Answer from facts that are given, and allow "I don't know". It does not make a model infallible,
but it turns most invented answers into honest ones.
:::

:::timeline
- **2023** Mata v. Avianca: invented court cases.
- **2024** Moffatt v. Air Canada: a chatbot's invented refund policy.
:::
:::

:::step{type=concept title="Facts in the prompt, and permission not to know" file="09-hallucinations/honest.py" line="5-22"}
The co-op's facts (`FACTS`) are a short card: office hours, today's mandi rates, cold storage prices, loans, and the
spraying rule. The honest prompt is three parts:

```text
<who Navin is: SYSTEM>
If the answer is not in the facts below, say "I don't know" and suggest calling the co-op office.
Never invent prices, dates or rules.

Facts:
<the facts card>
```

Why both? Facts alone are not enough: asked about garlic, a model with an onion and tomato rate list may still guess a
garlic rate. Permission alone is not enough: without facts, it has nothing to answer from. Together, the model answers
what it was given and declines the rest.

Pasting facts into the prompt works for one card. A whole rule book does not fit, and would be paid for on every
question; Part 4 (retrieval) sends only the parts that matter.
:::

:::step{type=task task=honest_prompt title="Your turn: the honest prompt" file="09-hallucinations/honest.py" line="19-23"}
Finish `honest_prompt()`: return `SYSTEM`, then the "I don't know" instruction (exactly those words), then a blank line,
`Facts:` and `FACTS`.

Press **Check**.
:::

:::step{type=concept title="Reading the bill" file="09-hallucinations/honest.py" line="14-16"}
Every `AIMessage` has `usage_metadata`:

```python
reply.usage_metadata   # {'input_tokens': 224, 'output_tokens': 13, 'total_tokens': 237, ...}
```

gpt-4o-mini costs **$0.15 per million input tokens** and **$0.60 per million output tokens**: output is four times
dearer, because each output token is one full pass through the model (chapter 4).

| | Tokens | Price per million | Cost |
|---|---|---|---|
| Input | 224 | $0.15 | $0.0000336 |
| Output | 13 | $0.60 | $0.0000078 |
| **Answer** | | | **$0.0000414** |

Notice where the money goes: 224 tokens in, mostly the facts card sent with every question, and only 13 out. The facts
made Navin honest, and they are also most of its bill.
:::

:::step{type=task task=answer_cost title="Your turn: the cost of an answer" file="09-hallucinations/honest.py" line="31-35"}
Finish `answer_cost(reply)`: input tokens times `INPUT_PER_MILLION`, plus output tokens times `OUTPUT_PER_MILLION`,
divided by one million.

```bash run
cd /workspace/09-hallucinations && python main.py
```

Press **Check**.
:::

:::step{type=try title="Right, honest, and careful"}
```text
$ python main.py
> What is today's onion rate?
Today's onion rate is Rs 1,850 per quintal.
  (224 in, 13 out, $0.000041)

> What is today's garlic rate?
I don't know. Please call the co-op office for that information.
  (224 in, 14 out, $0.000042)

> Can I harvest grapes 4 days after spraying?
No, you cannot harvest grapes 4 days after spraying. You must wait for 10 days.
  (228 in, 20 out, $0.000046)
```

Three questions, three behaviours you want. The onion rate came from the facts. Garlic is not on the card, so Navin
said "I don't know" and pointed to the office instead of inventing a rate. And the spraying question got the co-op's
rule, applied to the member's situation: 4 days is not 10.

The cost: about **$0.00004** an answer. If every member asked ten questions a day, 1,000 members would cost about
$0.43 a day. Cheap, but notice that it scales with the facts card: double the card, nearly double the bill. That is
the cost argument for retrieval in Part 4.
:::

:::step{type=predict title="Guess first"}
:::question
The co-op changes the onion rate every morning. What must change for Navin to answer with today's rate?
:::
- [ ] Retrain the model
- [x] Update the facts it is given; the next answer uses them
- [ ] Nothing: the model reads the news
:::explain
The model knows only what it was trained on, plus what you send. Facts in the prompt (or retrieved, Part 4) can change
any time.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why add "say I don't know" when the facts are already in the prompt?
:::
- [ ] It makes answers shorter
- [x] Without permission, the model tends to answer anyway, guessing what is not in the facts
- [ ] The API requires it
:::explain
Facts give it something to answer from; permission makes declining an acceptable answer.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Most of each answer's cost here comes from...
:::
- [x] the input: the facts card sent with every question
- [ ] the output: Navin's long answers
- [ ] the HTTP request itself
:::explain
224 tokens in against 13 out. Input is cheaper per token, but there is much more of it.
:::
:::

:::step{type=deep-dive title="Go deeper: hallucinations in practice"}
**It still happens.** Grounding and permission reduce invented answers; they do not remove them. Chapter 26 measures
how often Navin gets a set of known questions right.

**Citations.** Asking the model to say which fact it used makes answers checkable; Part 4 returns the source document
with each answer.

**Prompt caching.** Providers discount input tokens that repeat at the start of every request (like a long facts card),
which lowers exactly the cost this chapter found.
:::

:::step{type=recap}
You can now:

- explain hallucination, and why fluent answers are not evidence;
- ground answers in facts and permit "I don't know";
- read `usage_metadata` and turn tokens into dollars;
- see that the facts that make Navin honest are also most of its cost.

That ends Part 2. Next, chapter 10: an agent built by hand, a model that can ask your Python code for help.

:::photo{src="/lesson-images/langchain/lc-09-notes.webp" alt="Handwritten notes about hallucinations and cost: Hallucination: likely, not true; Give facts, allow I don't know; Garlic: I don't know; 224 in, 13 out; About $0.00004 an answer" ai="true"}
One page of notes for this chapter.
:::
:::
