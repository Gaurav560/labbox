:::step{type=story title="Is Atlas right?"}
The museum's director has one question before Atlas goes on the lobby screen: "How do we know it is right?" A fair
question. In chapter 13 you changed the chunk size and the visitor card's headings, and the ticket question started
working. Did anything else stop working? You do not know. You checked three questions by hand.

Ordinary code has tests: the same input always gives the same output, and `assertEquals` says whether it is right.
AI features are harder. The model's wording changes from run to run, and there are many right answers ("60 rupees",
"Children pay 60 rupees", "It costs 60 rupees for a child"). Yet "it seems fine when I try it" is not good enough for a
screen thousands of children will use.

Silversmiths faced the same question centuries ago: is this spoon really silver? Since **1300**, English law has
required silver to be tested against a fixed standard and stamped when it passes. The testing later moved to the
Goldsmiths' Hall in London, which gave the stamp its name: a **hallmark**.

:::photo{src="/lesson-images/spring-ai/hallmarks.webp" alt="Close-up of four small marks stamped into the silver rim of a thimble" credit="Birmingham Museums Trust, Teresa Gilmore" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:WMID-89CE08,_Post_Medieval_to_Modern,_Thimble_-_hallmark_close_up_(FindID_535269).jpg"}
Hallmarks on a silver thimble from the 1800s: tested against a standard, and stamped.
:::

:::mission
Measure Atlas: a hit rate for retrieval on a set of real questions, and a second model that judges each answer.
:::
:::

:::step{type=concept title="Two things to measure"}
A RAG answer can go wrong in two places, and they are measured differently:

| What | Goes wrong when | Measured by | Costs |
|---|---|---|---|
| **Retrieval** | the right card is not found | golden questions: is the right card in the top 3? | embeddings only, almost free |
| **The answer** | the card was found, but the answer misreads it or adds things | a judge: a model that grades the answer | one more model call per answer |

Start with retrieval: it is cheap, exact and repeatable (the same question always finds the same chunks), and when it
fails, no prompt can save the answer.

A **golden set** is a list of real questions, each with what a right answer needs: here, the card that must be found.
The `16-evaluation` project has fifteen, in `Golden.java`, "collected from the lobby screen's logs". The rule for a
golden set is simple: every time Atlas gets a question wrong, it joins the set, so the same mistake is caught forever.

:::diagram{name="ai-evaluation"}
Retrieval is measured by searching golden questions; answers are graded by a judge model.
:::
:::

:::step{type=task task=retrieval_eval title="Your turn: measure retrieval" file="16-evaluation/src/main/java/com/atlas/EvalController.java" line="55"}
In `16-evaluation`, finish `GET /eval/retrieval`: search each golden question in the store (top 3, similarity at least
0.35, as Atlas does); count a **hit** when the golden file is among the files found, and list the other questions as
**misses**.

```bash run
cd 16-evaluation && mvn -q -o spring-boot:run
```

Wait for the `ETL:` line, then:

```bash run
curl -s localhost:8080/eval/retrieval | jq .
```

Press **Check**.
:::

:::step{type=try title="The real number"}
With the real embedding model:

```text
$ curl -s localhost:8080/eval/retrieval | jq .
{
  "total": 15,
  "hits": 10,
  "misses": [
    "Is there a lift for my grandmother's wheelchair?",
    "When is the black holes show?",
    "Where do the colours of a rainbow come from?",
    "Can I talk to my friend across the gallery?",
    "Does the museum make its own electricity?"
  ]
}
```

**10 of 15.** Atlas's retrieval finds the right card for two questions in three. The misses are worth reading, one
by one, because each has a reason:

- "When is the black holes show?": the planetarium card says "16:00 (Black Holes)", one short phrase inside a chunk
  about the dome and its seats.
- "Is there a lift for my grandmother's wheelchair?" and "Does the museum make its own electricity?": the visitor's
  words (grandmother, make its own) are far from the card's (lifts in every gallery, a solar tree).
- "Where do the colours of a rainbow come from?" found the prism room in chapter 11, where whole descriptions were
  compared; here, small chunks and a threshold of 0.35 let it slip.

None of this was visible from trying three questions by hand. Each miss suggests a fix to try (a separate show
timetable card, a "Questions visitors ask" section on each card, a lower threshold), and the golden set tells you
whether the fix helped, and whether it broke anything else.

This number is your baseline. Change the chunk size, the threshold, the embedding model or a card, run it again, and
you know at once whether retrieval got better or worse. It costs fifteen tiny embedding requests.
:::

:::step{type=history title="Models grading models"}
How do you grade an answer whose wording changes every time? Researchers first used word-overlap scores (BLEU in 2002,
ROUGE in 2004), which count shared words with a reference answer. They work for translation, badly for free answers:
"Children pay 60 rupees" and "The price for kids is sixty" share almost no words.

:::before{title="People grading answers"}
The reliable way was people: read each answer and mark it. That is slow and expensive, and nobody does it again after
every small change.
:::

In **2023**, a team from UC Berkeley and other universities (Lianmin Zheng and colleagues) studied **LLM-as-a-judge**:
asking a strong model to grade answers. Its grades agreed with human experts about as often as two humans agreed with
each other.

:::solved
**A grader you can run after every change.** A judge model reads the question, the context and the answer, and gives
a verdict in a second. It is not perfect (judges favour longer answers, and answers in their own style), so you check a
sample of its verdicts by hand, and you use it to find problems, not to prove there are none.
:::
:::

:::step{type=example title="Worked example: Spring AI's judges" file="16-evaluation/src/main/java/com/atlas/EvalController.java" line="68"}
Spring AI has an `Evaluator` interface with two ready-made judges:

| Evaluator | Asks the judge model |
|---|---|
| `RelevancyEvaluator` | is the answer in line with the question and the context? YES or NO |
| `FactCheckingEvaluator` | is this claim supported by this document? |

Both take an `EvaluationRequest`: the question, the documents that were retrieved, and the answer.

```java
RelevancyEvaluator judge = new RelevancyEvaluator(ChatClient.builder(model));
EvaluationRequest request = new EvaluationRequest(q, used, answer);
boolean relevant = judge.evaluate(request).isPass();
```

1. The judge gets its own `ChatClient`, from a fresh builder: it must not carry Atlas's advisors (a judge with the RAG
   advisor would retrieve cards about its own grading prompt).
2. `used` is the list of documents the `QuestionAnswerAdvisor` retrieved, read from the response context as in
   chapter 14.
3. `isPass()` is the verdict. The prompt Spring AI sends the judge says: "Your task is to evaluate if the response for
   the query is in line with the context information provided. You have two options to answer. Either YES or NO."
:::

:::step{type=task task=judge_answer title="Your turn: a judge for every answer" file="16-evaluation/src/main/java/com/atlas/EvalController.java" line="69"}
Finish `GET /ask/judged?q=...`: Atlas's answer is ready in `answer`, the retrieved documents in `used`. Ask a
`RelevancyEvaluator`, built on `ChatClient.builder(model)`, whether the answer is relevant, and return its verdict.

```bash run
curl -s -G localhost:8080/ask/judged --data-urlencode "q=How much is a ticket for a child?" | jq .
```

Press **Check**.
:::

:::step{type=try title="Real verdicts"}
```text
$ curl -s -G localhost:8080/ask/judged --data-urlencode "q=How much is a ticket for a child?" | jq .
{
  "answer": "A ticket for a child aged 5 to 15 costs 60 rupees. Children under 5 enter free. Enjoy your visit to the museum!",
  "relevant": true
}
$ curl -s -G localhost:8080/ask/judged --data-urlencode "q=Do you have a T-rex?" | jq .
{
  "answer": "I’m sorry, but we do not have a T-rex in the museum. We do have a cast of the skull of Rajasaurus narmadensis, which is a fascinating dinosaur from India!",
  "relevant": true
}
$ curl -s -G localhost:8080/ask/judged --data-urlencode "q=Which exhibits do you have?" | jq .
{
  "answer": "I'm sorry, but I can't answer questions about the exhibits at the museum. However, I can help with other topics or information related to science!",
  "relevant": false
}
```

The ticket answer and the T-rex answer passed: both fit the question and the cards. The third did not, and the judge
was right: "Which exhibits do you have?" got the useless refusal you met in chapter 14, and the judge flagged it. That
is the point of a judge: it reads every answer, so a pattern of bad answers shows up in a count, not in a complaint
from the director.

Note what the judge cannot tell you: why. Was the card missing, the retrieval wrong, or the model's reading poor? The
retrieval report answers the first two; for the third, you read the answer yourself.
:::

:::step{type=predict title="Guess first"}
:::question
You run `/eval/retrieval` twice in a row, without changing anything. Will the numbers be the same?
:::
- [x] Yes: embeddings and similarity search have no randomness
- [ ] No: models are random
- [ ] Only if the temperature is 0
:::explain
Embedding models do not sample (chapter 11), and the search is plain arithmetic, so retrieval evaluation is
repeatable. Judged answers are not: the answer and the judge are both generated. Run judges over many questions and
read the rate, not a single verdict.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the judge get a fresh `ChatClient.builder(model)` instead of Atlas's ChatClient?
:::
- [ ] Atlas's ChatClient is too slow
- [x] Atlas's carries its own system prompt and RAG advisor, which would change the judge's question
- [ ] Evaluators cannot use a ChatClient
:::explain
A judge should see exactly the grading prompt. Atlas's advisors would add a system prompt about the museum and
retrieved cards about the grading text itself. Many teams even use a different, stronger model as the judge.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Atlas answers a question wrongly in the lobby. What should happen to that question?
:::
- [ ] Nothing: models make mistakes
- [x] Add it to the golden set, fix the cause, and keep it there so the mistake is caught if it ever comes back
- [ ] Remove the card it used
:::explain
That is how a golden set grows into a safety net: every real failure becomes a test. The same habit as writing a test
for every bug in ordinary code.
:::
:::

:::step{type=deep-dive title="Go deeper: evaluation in practice"}
**In the build.** Run the retrieval evaluation as a JUnit test with a minimum hit rate (today's baseline, 10 of
15), so a change that makes retrieval worse fails the build. Judged answers cost tokens: run them nightly, or before a
release, on a bigger set.

**More metrics.** Retrieval teams also measure where the right chunk ranks (first is better than third), and whether
irrelevant chunks come along. For answers: faithfulness (every claim is in the context), completeness, tone, length.

**Custom judges.** `RelevancyEvaluator.builder().promptTemplate(...)` takes your own grading prompt; a judge for
Atlas could check "suitable for a ten-year-old" as well.

**Fact checking with small models.** `FactCheckingEvaluator` was designed for small, cheap judge models trained only
to say whether a document supports a claim, like Bespoke-MiniCheck, which runs locally with Ollama.
:::

:::step{type=recap}
You can now:

- explain why AI features need evaluation, and the two places a RAG answer can fail;
- build a golden set, and measure retrieval with a hit rate that is exact and almost free;
- use a model as a judge with Spring AI's `RelevancyEvaluator`, on its own ChatClient;
- treat every real failure as a new golden question.

Next, chapter 17: guardrails, for the questions Atlas should never answer, and the ones that try to trick it.

:::photo{src="/lesson-images/spring-ai/springai-16-notes.webp" alt="Handwritten notes about evaluation: golden questions; retrieval: hits in the top 3; a judge: YES or NO; a fresh ChatClient for the judge; every failure joins the set" ai="true"}
One page of notes for this chapter.
:::
:::
