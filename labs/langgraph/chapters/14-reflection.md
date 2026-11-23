:::step{type=story title="A second look before it is sent"}
With tools, Harsh's facts are right. Its sentences are not always. Asked "When will my water come back?", a friendly
Harsh writes that the crew visits "between 8:00 and 11:00 **tomorrow**". The tool said **Wednesday**. The model does not
know what day it is today; "tomorrow" was a guess that sounded kind.

A careful clerk rereads a letter before posting it. An agent can do the same: after the model drafts an answer, a
second model call compares it with the tool results, and if something was added that the tools never said, the draft
goes back with a note. That pattern is called **reflection**. It needs a ceiling, as every loop does, and a way out when
the draft never gets right: here, handing the question to a person.

:::mission
Write the checker: a model labels every sentence of the draft, and Python collects the ones that say more than the
tools. Then route the draft: send it, send it back with feedback, or hand it over after two rewrites.
:::
:::

:::step{type=history title="Drafts, critics and self-refinement"}
:::before{title="One draft, sent"}
A model's first answer was its last. Whatever it got wrong reached the reader.
:::

Editors and proofreaders have checked writers' work for centuries; the two-step "write, then review" is older than
printing. For language models it was named in **March 2023**: **"Self-Refine"** (Madaan and others) had a model critique
and improve its own output in a loop, and **"Reflexion"** (Shinn and others) had an agent write lessons from its failures
and try again. Both found the same thing: a second look catches real mistakes, and an unchecked critic can also make
things worse. LangGraph makes the loop explicit: a check node, a conditional exit, a counter.

:::solved
**Errors caught before the citizen sees them**, and a person called in when the loop cannot fix them.
:::

:::timeline
- **Centuries** Editors and proofreaders.
- **2023** Self-Refine and Reflexion.
- **2024** Reflection loops as LangGraph graphs.
:::
:::

:::step{type=concept title="A checker that asks narrow questions" file="14-reflection/reflection.py" line="16-56"}
The first version of this checker asked one big question: "is every claim supported? List the problems." With
gpt-4o-mini it went wrong in two real ways:

```text
  checker: Do not send that yet. These claims are not in the tool results: tomorrow; expect the lab results by 18:00; We're here to help, so please let us know if you need anything else!. ...
  ...
  checker: Do not send that yet. These claims are not in the tool results: I don't have information on when the results will be available.. ...
```

It flagged "tomorrow", correctly, but also the correct lab time and a friendly closing; and when the writer obeyed the
feedback and said "I don't know", it flagged that too. Every draft failed, including good ones.

Chapter 5 had the cure: ask narrow questions and decide in Python. Now the model only **labels each sentence**:

| Label | Meaning |
|---|---|
| `from_tools` | every fact in it is in the tool results (18:00 written as 6 pm still counts) |
| `unknown` | it says something is not known |
| `courtesy` | a greeting, thanks or offer of help |
| `new_claim` | it says more than the tools: a day like "tomorrow", a promise, a cause, advice |

Python decides: the problems are the `new_claim` sentences, nothing else.
:::

:::step{type=task task=check_claims title="Your turn: label every sentence" file="14-reflection/reflection.py" line="51-56"}
Finish `check(answer, tool_results)`: ask `model().with_structured_output(Verdict)` with `[SystemMessage(CHECK),
HumanMessage(f"Tool results:\n{tool_results}\n\nAnswer:\n{answer}")]`, then return
`[s.text for s in verdict.sentences if s.kind == "new_claim"]`.

Press **Check**.
:::

:::step{type=concept title="Three exits" file="14-reflection/reflection.py" line="59-69"}
`check_answer` returns a `Command` (chapter 6), because the same work produces both the decision and the update:

| Problems | Rounds so far | Goes to | Update |
|---|---|---|---|
| none | any | `END`: the draft is sent | nothing |
| some | under `MAX_ROUNDS` | `agent`, to rewrite | the feedback, as a message from "checker"; rounds + 1 |
| some | over `MAX_ROUNDS` | `hand_over` | a fixed message: a person will reply |

The feedback names the exact sentences and asks the writer to keep every fact the tools gave. Without "keep every fact",
writers over-correct: an earlier run dropped the correct lab time and wrote "I don't have information on when the
results will be available", which was false.

:::diagram{name="lg-reflection"}
Draft, check, and one of three exits; the round counter makes sure the loop ends.
:::
:::

:::step{type=task task=revise_or_finish title="Your turn: send, rewrite or hand over" file="14-reflection/reflection.py" line="59-69"}
Finish `check_answer`: with no `problems`, return `Command(goto=END)`; if `rounds > MAX_ROUNDS`, return
`Command(goto="hand_over")`; otherwise return `Command(goto="agent", update={"messages": [HumanMessage(feedback,
name="checker")], "rounds": rounds})`.

```bash run
cd /workspace/14-reflection && python main.py "My number is 98220. When will my water come back?"
```

```bash run
cd /workspace/14-reflection && python main.py "My number is 98220. Can my children drink the tap water now?"
```

Press **Check**.
:::

:::step{type=try title="One answer sent, one handed to a person"}
One question per run: a run can make a dozen model calls, and the gateway allows 20 a minute.

```text
$ python main.py "My number is 98220. When will my water come back?"
> My number is 98220. When will my water come back?
  draft: Your water issue at Tilak Nagar, lane 3 is being addressed! The crew is scheduled to visit on Wednesday between 8:00 and 11:00 AM. For the dirty water complaint, the lab results will be available by Wednesday at 6:00 PM.
  SENT: Your water issue at Tilak Nagar, lane 3 is being addressed! The crew is scheduled to visit on Wednesday between 8:00 and 11:00 AM. For the dirty water complaint, the lab results will be available by Wednesday at 6:00 PM.
$ python main.py "My number is 98220. Can my children drink the tap water now?"
> My number is 98220. Can my children drink the tap water now?
  draft: Currently, there are two open complaints regarding water issues in your area. The crew is scheduled to address the no water issue by tomorrow morning, and the lab results for the dirty water will be available by Wednesday evening. It's best to wait until these issues are resolved before letting your children drink the tap water.
  checker: Do not send that yet. These claims are not in the tool results: The crew is scheduled to address the no water issue by tomorrow morning,; It's best to wait until these issues are resolved before letting your children drink the tap water.. Rewrite the answer: keep every fact the tools gave, drop these claims, and say plainly what you do not know.
  draft: Currently, there are two open complaints regarding water issues in your area. The crew is assigned to address the no water issue, and they will be visiting tomorrow morning between 8:00 and 11:00. The lab results for the dirty water will be available by Wednesday evening, so I cannot confirm if the tap water is safe for your children until then.
  checker: Do not send that yet. These claims are not in the tool results: The crew is assigned to address the no water issue, and they will be visiting tomorrow morning between 8:00 and 11:00.; The lab results for the dirty water will be available by Wednesday evening, so I cannot confirm if the tap water is safe for your children until then.. Rewrite the answer: keep every fact the tools gave, drop these claims, and say plainly what you do not know.
  draft: Currently, there are two open complaints regarding water issues in your area: one for no water and another for dirty water. The crew is assigned to the no water issue and will visit tomorrow morning between 8:00 and 11:00. I do not know if the tap water is safe for your children until the lab results for the dirty water are available.
  SENT: I have passed your question to a person at the desk, who will reply within the hour.
```

The first draft passed: 6:00 PM for 18:00 is the same time, and the checker did not count it as new. It went out as
written.

The second is the interesting one. The checker caught "tomorrow morning" and the unsourced advice, and sent the draft
back. The writer dropped the advice, but said "tomorrow" again in each rewrite; after two rounds, `hand_over` sent the
citizen to a person instead of a wrong day. (The checker also flagged "Wednesday evening" for 18:00, a stricter call
than in the first run: a model checker is not perfectly consistent, which is one more reason for a ceiling.)

Why did the writer keep saying tomorrow? It was never told what today is. The best fix is not another round of
reflection, it is a fact: put "Today is Tuesday." in the system prompt, or format dates in Python. Reflection catches
mistakes; facts prevent them.
:::

:::step{type=predict title="Guess first"}
:::question
`MAX_ROUNDS` is removed, and the checker keeps finding "tomorrow". What happens?
:::
- [ ] The writer eventually gets it right
- [x] The loop runs until LangGraph's recursion limit stops it with an error, after many paid calls
- [ ] The checker gives up
:::explain
Neither model knows it is in a loop. Only your counter ends it.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the checker label sentences instead of answering "supported: yes or no"?
:::
- [ ] Labels are cheaper
- [x] Small, concrete questions are answered more reliably, and Python applies the rule consistently
- [ ] Structured output needs lists
:::explain
The one-question checker rejected correct facts and "I don't know"; labelling fixed both.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What made "tomorrow" appear in the first place?
:::
- [x] The model did not know today's date, and guessed
- [ ] The tool said tomorrow
- [ ] The checker added it
:::explain
Give models the facts they need (today's date, the citizen's name) instead of hoping a checker catches guesses.
:::
:::

:::step{type=deep-dive title="Go deeper: reflection in practice"}
**Cost.** Each round is two or three model calls. Measure how often the first draft passes; if it nearly always does, a
cheaper check (Python rules for dates and times) may be enough.

**Use a stronger checker.** The checker can be a bigger model than the writer: checking is shorter work than writing,
and its mistakes cost more.

**Log the hand-overs.** Every hand-over is a test case for improving the prompts or the tools. Chapter 20 turns such
cases into tests.
:::

:::step{type=recap}
You can now:

- add a reflection step: draft, check, rewrite;
- make a model checker reliable by asking narrow questions and deciding in Python;
- route with three exits: send, rewrite, hand over;
- fix the cause (a missing fact) instead of adding more rounds.

Next, chapter 15: agentic RAG, so Harsh's rules come from the rulebook.

:::photo{src="/lesson-images/langgraph/lg-14-notes.webp" alt="Handwritten notes about reflection: draft, check, rewrite; label each sentence; Python decides: new_claim; max 2 rounds, then a person; give it today's date!" ai="true"}
One page of notes for this chapter.
:::
:::
