:::step{type=story title="A confident wrong answer"}
During testing, a member of Sahyadri Rail's staff asked Setu a simple question: "What time does the Ghat Express leave
Pune?" Setu answered at once, politely, with a time. The time was wrong. Setu had never seen the timetable; it produced
the kind of answer a help desk gives to that kind of question, because predicting likely text is what a language
model does (chapter 3).

This is called a **hallucination**, and it is the single most important thing to design around in any AI
application. A help desk that sends passengers to the platform at the wrong time is worse than no help desk.


The real Lonavla station, on the line from Pune up through the Western Ghats (the railway spells it Lonavla). Setu's fictional Ghat Express stops here at 08:40; a model that has never seen Sahyadri Rail's timetable can only guess a time like that.

:::photo{src="/lesson-images/langchain4j/lonavla-station.webp" alt="The entrance of Lonavla railway station: a curved concrete arch with the station name in Marathi, Hindi and English, an auto-rickshaw in front" credit="Superfast1111" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File%3ALonavla_railway_station_-_Entrance.jpg"}
Lonavla station, on the ghat line from Pune.
:::
:::mission
See Setu hallucinate with the real model, then fix it the two cheapest ways: permission to say "I don't know", and the
real facts in the prompt.
:::
:::

:::step{type=concept title="Open and closed models"}
Before fixing it, one choice every AI project makes: **which model**. They come in two kinds:

| | Closed models | Open-weight models |
|---|---|---|
| Examples | OpenAI's GPT family, Anthropic's Claude, Google's Gemini | Meta's Llama, Mistral, Alibaba's Qwen, DeepSeek, Google's Gemma |
| How you use them | Only through the company's API | Download the weights; run on your own servers, or rent them from a host |
| Strengths | Usually the most capable; nothing to operate | Data stays with you; no per-token bill on your own hardware; can be fine-tuned |
| Costs | Pay per token | Pay for hardware (GPUs) and the people to run it |

"Open" usually means **open weights**: you get the trained parameters, under a licence, but rarely the training data
or code. Some licences allow any use (Apache 2.0, MIT), others restrict it.

Both kinds hallucinate. A bigger or newer model hallucinates less often, not never. So the defences in this chapter
apply whichever model Setu uses, and LangChain4j's `ChatModel` interface means switching between them is a builder
change (chapter 24 runs an open model locally).
:::

:::step{type=history title="Fake cases and a refund that never existed"}
:::before{title="Trusting fluent text"}
Because a language model writes fluently, people assume it knows. In **2023** two lawyers in New York filed a court
brief that cited six earlier cases. ChatGPT had produced all six, with names, quotes and page numbers; none existed.
The judge fined them 5,000 dollars, and courts around the world began requiring lawyers to check AI-written filings.
:::

In **February 2024** a Canadian tribunal ruled against **Air Canada**. Its website chatbot had told a grieving
passenger he could apply for a bereavement discount after travelling; the airline's real policy said the opposite. Air
Canada argued the chatbot was responsible for its own words. The tribunal disagreed: the company is responsible for
everything on its website, chatbot included, and had to pay. For Sahyadri Rail, the lesson is direct: **what Setu
promises, the railway owes**.

:::solved
**Ground the answer, allow "I don't know".** Models invent less when the facts are in front of them and when they are
told, clearly, that not knowing is acceptable. Retrieval (chapter 23) automates the first; guardrails (chapter 25) and
evaluation (chapter 26) catch what slips through.
:::

:::timeline
- **2022** ChatGPT: fluent answers to anything, right or wrong.
- **2023** The New York case of the invented court citations.
- **2024** Air Canada must honour its chatbot's invented policy.
:::
:::

:::step{type=concept title="Why models make things up"}
Three facts you already know explain hallucinations:

1. **A model predicts likely text** (chapters 3 and 6). "The Ghat Express leaves Pune at" is very likely to be
   followed by a time, so a time comes out. Nothing in the model checks it against a timetable it has never seen.
2. **Training rewarded answering.** Chat models are trained further with human feedback to be helpful, and an answer
   usually looks more helpful than "I don't know", unless you say otherwise.
3. **The model knows only what it was trained on, plus what you send.** Sahyadri Rail is not in its training data. The
   only way it can know the timetable is if the timetable is in the messages.

So the two cheapest defences follow directly: **tell it** that not knowing is fine (and what to do then), and **give
it** the facts in the prompt. That second idea has a name you will use for the rest of the course: **grounding**.
:::

:::step{type=example title="Worked example: an instruction that allows not knowing" file="11-hallucinations/src/main/java/com/setu/Honest.java" line="19-24"}
A good "I don't know" instruction says three things: when to use it, exactly what to say, and what never to do.
For a different assistant, only to read (it is not in your project):

```java
static final String LIBRARY = "You answer questions about the city library. "
        + "If the answer is not in the opening hours you were given, say \"I don't know\" "
        + "and suggest calling the front desk. Never guess dates or fees.";
```

Notice it gives the model somewhere to send the person ("calling the front desk"): an assistant told only "do not
guess" tends to give vague non-answers instead.
:::

:::step{type=task task=honest_prompt title="Your turn: permission to say I don't know" file="11-hallucinations/src/main/java/com/setu/Honest.java" line="19-24"}
Finish `Honest.honestSystem()`: return `SYSTEM` plus an instruction that, when the answer is not in the facts it was
given, Setu says "I don't know" and suggests the station office, and never invents times, fares or rules. The text must
contain the words `I don't know`.

Press **Check**.
:::

:::step{type=task task=grounded_answer title="Your turn: ground the answer in facts" file="11-hallucinations/src/main/java/com/setu/Honest.java" line="31-35"}
Finish `Honest.ask(model, question)`: build the system message from `honestSystem()`, a blank line, `"Facts:"` and
`facts()` (the timetable in `timetable.txt`); send it with the question as the user message; return the answer's text.

```bash run
cd /workspace/11-hallucinations && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Invented, then grounded"}
```text
$ mvn -q compile exec:java
Q: What time does the Ghat Express leave Pune?
  no facts:   The Ghat Express typically departs from Pune at 6:00 AM. Please check the latest schedule for any updates or changes.
  with facts: The Ghat Express leaves Pune at 07:15.
Q: How much is a ticket from Pune to Karjat?
  no facts:   Ticket prices from Pune to Karjat vary based on class and availability. Please check the official Sahyadri Rail website or app for the most accurate and up-to-date fare information.
  with facts: A ticket from Pune to Karjat costs Rs 140.
Q: Does the Konkan Breeze run on Tuesdays?
  no facts:   Yes, the Konkan Breeze operates on Tuesdays. Please check the schedule for specific timings. Let me know if you need more information!
  with facts: No, the Konkan Breeze does not run on Tuesdays.
Q: Is there wifi on the Monsoon Mail?
  with facts: I don't know. Please check with the station office for more information.
```

Read the "no facts" answers carefully, because this is real output from gpt-4o-mini at temperature 0. Two of the three are confidently wrong. The Ghat Express "typically departs from Pune at
6:00 AM": the timetable says 07:15, so a passenger who trusted Setu would wait more than an hour on the platform. The
Konkan Breeze "operates on Tuesdays": it does not run on Tuesdays at all, and a family would arrive at the station for
a train that is not coming. Only the fare question got a vague non-answer instead of a made-up number. Temperature 0
did not help: it makes the model consistent, and a consistent guess is still a guess.

With the timetable in the system message, every answer is right and checkable against `timetable.txt`. And the last
question, about wifi, is not in the facts: instead of inventing "yes, free wifi on board", Setu says it does not know
and points to the station office. That is the behaviour the railway can stand behind.
:::

:::step{type=predict title="Guess first"}
:::question
The timetable changes on 1 November. What must change in Setu?
:::
- [ ] Nothing: the model will learn the new times
- [x] The facts sent in the prompt: update timetable.txt (or wherever the facts come from)
- [ ] Retrain the model
:::explain
The model learns nothing from your calls. Facts in the prompt are read fresh on every call, so updating the source
updates Setu at once. That is the big practical advantage of grounding over hoping the model knows.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does "open-weight model" mean?
:::
- [ ] A model that is free to call through any API
- [x] A model whose trained parameters you can download and run yourself, under its licence
- [ ] A model that never hallucinates
:::explain
You get the weights, not necessarily the training data or code, and the licence may restrict use. Running it is on you.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does a model invent a departure time it was never told?
:::
- [x] It predicts the most likely continuation, and a time is the likely continuation of that question
- [ ] It looked up an old timetable on the internet
- [ ] It is broken
:::explain
Fluent and likely is what the model optimises. Truth has to come from you: grounding, permission to not know, and
checks.
:::
:::

:::step{type=deep-dive title="Go deeper: hallucinations in production"}
**Measure it.** Keep a set of real questions with known answers, and run them after every change of prompt or model
(chapter 26). "It seemed fine when I tried" is not a measurement.

**Ask for sources.** When answers come from documents, ask the model to name the document it used; a missing source
is a warning sign (chapter 23).

**Lower the stakes.** Let Setu explain rules but never confirm a refund amount by itself: a tool that calculates it in
Java (chapter 19) cannot hallucinate arithmetic.

**Say it is an AI.** Telling passengers they are talking to an AI assistant, and that it can make mistakes, is good
practice, and in some places a legal requirement.
:::

:::step{type=recap}
You can now:

- compare open-weight and closed models, and what each costs to run;
- explain why language models hallucinate, from how they are trained;
- reduce hallucinations by allowing "I don't know" and by grounding answers in facts;
- explain why the company, not the chatbot, is responsible for what it says.

Next, chapter 12: what every answer costs. Token usage, finish reasons, and the help desk's real bill.

:::photo{src="/lesson-images/langchain4j/l4j-11-notes.webp" alt="Handwritten notes about hallucinations: open weights or a closed API; models predict likely text; likely is not true; allow I don't know; ground answers in facts" ai="true"}
One page of notes for this chapter.
:::
:::
