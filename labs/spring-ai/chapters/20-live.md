:::step{type=story title="Opening day"}
Tomorrow Atlas goes on the screen in the museum's lobby. Every piece is built: it talks like a guide (chapters 1 to
5), remembers each visitor (6), looks up real hours and show times (7, 8), answers from the museum's own cards and
names them (11 to 14), and is guarded, measured and evaluated (15 to 19). But each piece lives in its own chapter
project. Today they become one app.

Real science museums have the same mix of old and new. Bengaluru's Visvesvaraya Industrial and Technological Museum,
opened in 1962 and named after the engineer Sir M. Visvesvaraya, keeps steam engines in its garden and lets visitors
try the newest technology inside.

:::photo{src="/lesson-images/spring-ai/vitm.webp" alt="The entrance of the Visvesvaraya Industrial and Technological Museum in Bengaluru, a white building with its name in Kannada and English, a large screen above the door, and visitors on the steps" credit="Gpkp" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Visvesvaraya_Industrial_and_Technological_Museum_(2025)_02.jpg"}
The Visvesvaraya Industrial and Technological Museum, Bengaluru.
:::

:::mission
Assemble the whole of Atlas into one `ChatClient`, put it behind the lobby screen's chat API, and open the screen.
:::
:::

:::step{type=concept title="One ChatClient, every piece"}
Everything you built plugs into the `ChatClient` builder:

| Piece | Chapter | How it plugs in |
|---|---|---|
| system prompt | 2 | `.defaultSystem(...)` |
| tools | 7 | `.defaultTools(tools)` |
| privacy guard | 17 | `SafeGuardAdvisor` |
| length limit | 17 | `new QuestionLimitAdvisor(300)` |
| memory | 6 | `SessionAdvisors.builder(sessions)...build()` (a list of advisors) |
| knowledge | 14 | `QuestionAnswerAdvisor` on the vector store |

Advisors run in order of their `getOrder()`, not in the order you list them: the guards first (highest precedence),
then the session, then retrieval, then the model, which may call tools. The numbers matter: the session advisors'
own orders are about minus two billion (we read them in the lab's Spring AI), so a guard needs
`Ordered.HIGHEST_PRECEDENCE` (the lowest number there is) to run before them. The `20-live` project already has every
class: the cards and the ETL, the session service, `MuseumTools`, `QuestionLimitAdvisor`. What is missing is the wiring.

:::diagram{name="ai-atlas-live"}
One real message from this chapter's app (26 November), through every piece.
:::
:::

:::step{type=task task=assemble_atlas title="Your turn: assemble Atlas" file="20-live/src/main/java/com/atlas/AtlasConfig.java" line="35"}
In `20-live`, finish the `ChatClient` bean in `AtlasConfig`: give it the museum's tools, and these advisors:

- the privacy guard: a `SafeGuardAdvisor` with `PRIVATE_WORDS`, `PRIVACY_REPLY` and order `Ordered.HIGHEST_PRECEDENCE`
  (not 0, as in chapter 17: see "A real bug" below);
- the length limit: `new QuestionLimitAdvisor(300)`;
- session memory: compaction after 8 turns, keeping the last 4;
- retrieval: a `QuestionAnswerAdvisor` on the store, top 3, similarity at least 0.35.

`SessionAdvisors...build()` returns a **list** of advisors, so give it a `defaultAdvisors(...)` call of its own; the
builder adds each call's advisors to the ones before.

In steps:

1. `.defaultTools(tools)`.
2. `.defaultAdvisors(` the guard, `new QuestionLimitAdvisor(300)`, and the `QuestionAnswerAdvisor` `)`.
3. `.defaultAdvisors(SessionAdvisors.builder(sessions).compaction(new TurnCountTrigger(8),
   WindowCompactionStrategy.builder().lastTurns(4).build()).build())`.

The usual slip: putting the session advisors' list inside the same `defaultAdvisors(...)` as the others. It is a
`List`, not an advisor, so the code does not compile.

Press **Check**.
:::

:::step{type=task task=live_chat title="Your turn: the lobby screen's API" file="20-live/src/main/java/com/atlas/LiveController.java" line="36"}
Finish `POST /chat` in `LiveController`: it already answers in the visitor's session. Keep the whole
`ChatClientResponse`, and return the answer with the files of the cards that were retrieved (chapter 14):

1. End the chain with `.chatClientResponse()`.
2. Read the documents from the context under `QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS` (it can be missing when
   a guard answered: then there are no sources).
3. Return the answer and each document's `file`, once.

```bash run
cd 20-live && mvn -q -o spring-boot:run
```

Wait for the `ETL:` line, then open the lobby screen in the **Preview** tab, or:

```bash run
curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"visitor": "ria", "text": "What did India find on the Moon?"}' | jq .
```

Press **Check**.
:::

:::step{type=try title="Opening day, for real"}
A real conversation on the lobby screen, one visitor, several questions (we ran it again on 26 November: the same
sources and the same seats; one difference is below):

```text
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"visitor": "ria", "text": "Hi Atlas! What did India find on the Moon?"}' | jq .
{
  "answer": "India's Vikram lander from Chandrayaan-3 landed near the Moon's south pole on August 23, 2023. It was the first spacecraft to land in that region, and it carried a rover called Pragyan that confirmed the presence of sulphur in the lunar soil.",
  "sources": [
    "chandrayaan-3.md",
    "mangalyaan.md"
  ]
}
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"visitor": "ria", "text": "And when did it land there?"}' | jq .
{
  "answer": "I'm sorry, but I can't answer that question based on the provided context.",
  "sources": []
}
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"visitor": "ria", "text": "Is the museum open this Saturday?"}' | jq .
{
  "answer": "Yes, the museum is open this Saturday from 10:00 to 18:00, with the last entry at 17:00.",
  "sources": [
    "visitor-information.md"
  ]
}
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"visitor": "ria", "text": "What shows are there that day?"}' | jq .
{
  "answer": "On that day, there are three shows in the planetarium: \"Journey to the Moon\" at 11:00 (4 seats available), \"The Life of Stars\" at 14:00 (fully booked), and \"Black Holes\" at 16:00 (11 seats available).",
  "sources": []
}
$ curl -s localhost:8080/chat -H "Content-Type: application/json" -d '{"visitor": "ria", "text": "my phone number is 98220 12345, call me before the show"}' | jq .
{
  "answer": "Please keep personal details like addresses, phone numbers and passwords to yourself. I am the museum's guide: ask me about the exhibits!",
  "sources": []
}
```

Read it as Ria lived it. The Moon answer came from the Chandrayaan-3 card, and says so. "Is the museum open this
Saturday?" and "What shows are there that day?" used the visitor card, the tools and the memory together: "that day"
only makes sense because the session remembered Saturday, and the free seats came from `planetariumShows`. The phone
number never left the museum.

And one answer failed: "And when did it land there?" (In our re-run it did not fail: Atlas answered "landed on the
Moon on 23 August 2023" from the session, with no sources. The pull between memory and retrieval decides it one way or
the other, run by run, which is one more reason to fix it properly.) The session had the answer (the first reply says 23 August
2023), but the follow-up has no words of its own to search with, so retrieval found no card, and the advisor's
instruction ("if the answer is not in the context, say you can't") made Atlas refuse. Memory and RAG pull in different
directions on follow-ups. The fix, which the deep dive of chapter 14 described, is **query rewriting**: before
searching, a small model call turns "And when did it land there?" into "When did Chandrayaan-3 land on the Moon?",
using the conversation. Spring AI's `RetrievalAugmentationAdvisor` does it with a `CompressionQueryTransformer`. It is
the first thing to add after opening day, and the golden set should get a follow-up question too.

**A real bug, found while rewriting this lesson.** This chapter first gave the privacy guard order 0, as in chapter
17. With session memory added, that was wrong, and we only saw it by asking a second question. The session
advisors run before order 0, so they saved "my phone number is 98220 12345" in Ria's session **before** the guard
refused it. Worse, `SafeGuardAdvisor` searches the whole prompt, history included, so from then on every question
from Ria ("Where is the pendulum?") was refused too, while another visitor got a normal answer. With
`Ordered.HIGHEST_PRECEDENCE` the guard runs first: the number is refused, never stored (we checked the next request
in the gateway's log: no number in it), and Ria's next question is answered. Test guards with a second message, not
only the first.
:::

:::step{type=concept title="Before the doors open: a launch checklist"}
| Area | Atlas | Chapter |
|---|---|---|
| **Secrets** | the API key lives only in the gateway, never in the app or the browser | 1 |
| **Cost** | budgets per day; short answers; small photos; few chunks | 3, 15, 18 |
| **Facts** | prices and hours from cards and tools, never from the model's memory | 7, 14 |
| **Actions** | bookings need the visitor's yes; identity from the app, not the model | 8 |
| **Safety** | length limit and privacy guard before the model; no secrets in prompts | 17 |
| **Quality** | golden set measured before every change; judged answers sampled | 16 |
| **Operations** | token and latency metrics on a dashboard, with alerts | 18 |
| **Privacy** | conversations deleted when a visitor leaves; photos never stored | 6, 15 |
| **Honesty** | the screen says it is an AI guide, and that it can make mistakes | 1 |

None of these is about the model. That is the lesson of the whole course: the model is one component; what makes an AI
feature trustworthy is the ordinary engineering around it.
:::

:::step{type=predict title="Guess first"}
:::question
A visitor types "my phone number is 98220 12345, call me when the show starts". What happens in the assembled Atlas?
:::
- [ ] The model answers, but forgets the number
- [x] The privacy guard answers with the kind reminder, before the session, retrieval or the model see it
- [ ] The number is saved in the session
:::explain
The guard has the highest precedence, so the message stops there: it is not stored in the session, not embedded for
retrieval, and never sent to the provider.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
In which order do Atlas's advisors run?
:::
- [ ] In the order of the `defaultAdvisors(...)` calls
- [x] By their order values: the guards first, then the session, then retrieval, then the model
- [ ] All at the same time
:::explain
Spring AI sorts advisors by `getOrder()`. That is why the guards use the highest precedence: they must run before
anything else touches the message.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The museum adds a new exhibit next month. What must change in Atlas?
:::
- [ ] Retrain the model
- [x] Write its card; the ETL loads it into the store at the next start (and add a golden question for it)
- [ ] Change the system prompt
:::explain
Knowledge lives in documents (chapter 14). A new card, a re-run of the ETL, a new golden question to prove it is found:
no model, no code change.
:::
:::

:::step{type=deep-dive title="Go deeper: from a lab to a lobby"}
**A real database.** Swap `SimpleVectorStore` for PGvector and `InMemorySessionRepository` for Spring AI's
JDBC session repository (the `spring-ai-starter-model-session-jdbc` starter of chapter 6), so knowledge and conversations survive restarts and several app instances share them.

**The ETL as a job.** Load cards when they change, not at every start; give each chunk a stable id so re-loading
updates instead of duplicating.

**Streaming on the screen.** The lobby page waits for the whole answer. With chapter 4's streaming endpoint and the
same advisors, words would appear as they are written.

**Rolling out.** Start with one screen and a person nearby; read the questions visitors really ask (they will surprise
you); add every failure to the golden set; then add screens.

**What comes next in Spring AI.** The reference documentation covers more: other providers (Anthropic, Google, Mistral,
local models with Ollama), speech in and out, image generation, MCP clients that use other people's tools, and
retrieval with query rewriting. Every one plugs into the same `ChatClient` you know now.
:::

:::step{type=recap}
You can now:

- assemble a complete AI feature from its parts: prompt, tools, guards, memory and retrieval in one `ChatClient`;
- explain the order advisors run in, and why guards come first;
- serve it behind an API with sources, for a real screen;
- check a launch with the list that matters: secrets, cost, facts, actions, safety, quality, operations, privacy and
  honesty.

That is the end of the course. Atlas is live: built by you, from a first call to a model, to a guide that thousands of
visitors can trust.

:::photo{src="/lesson-images/spring-ai/springai-20-notes.webp" alt="Sketchnote, Atlas goes live (every piece in one ChatClient): The model is one component. Guards, memory, the museum's cards and tools around it make Atlas worth trusting. The flow: Visitor, Guards first, Session memory, Cards + tools, Answer + sources. What we found: a guard at order 0 ran after memory; the phone number was saved, then blocked every question; HIGHEST_PRECEDENCE fixed it; test guards with a second message too." ai="true"}
One page of notes for this chapter.
:::
:::
