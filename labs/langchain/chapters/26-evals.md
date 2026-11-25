:::step{type=story title="Is Navin getting better or worse?"}
Over this course Navin's prompt changed a dozen times, its rule book was re-chunked, tools were added. Each change was
checked by reading a few answers. That does not scale: the co-op wants to change the model to a cheaper one next year,
and nobody can re-read every possible answer.

Two kinds of tests answer two different questions:

- **Unit tests** check your **code** with a fake model, the way every **Check** in this course has: free, instant, the
  same result every time.
- **Evals** (short for evaluations) check the **answers**, with the real model: a **golden set** of questions with
  known right answers, scored automatically. When a phrase check is too crude, a second model reads each answer and
  judges it against the rule.

| | Unit tests | Evals |
|---|---|---|
| What they check | your code | the model's answers |
| The model | a fake one, with scripted replies | the real one |
| Cost | nothing | model calls (this chapter: 22 per run) |
| Same result every time | yes | no: answers vary from run to run |
| When to run | on every change | before changing a prompt, chunks or model, and on a schedule |

:::mission
Score Navin's real answers against a golden set, then build a judge: a model that grades an answer against the co-op's
rule and says why.
:::
:::

:::step{type=history title="From test suites to evals"}
:::before{title="Tests for code that always answers the same"}
Software testing grew up around code with one right output: `storage_cost(40, 10)` must be 800, every time. Unit testing
frameworks (SUnit for Smalltalk, published in 1994; JUnit in 1997; Python's unittest in 2001; pytest since 2004) made
those tests routine.
:::

Language models broke the assumption: the same question can get differently worded answers, all right, or one subtly
wrong. In **March 2023**, with GPT-4, OpenAI open-sourced **Evals**, a framework for scoring models on sets of questions.
In **2023** researchers studied **LLM-as-a-judge** (Lianmin Zheng and colleagues, "Judging LLM-as-a-Judge"), and found
that GPT-4's grades agreed with human graders over 80% of the time, about as often as two humans agree with each other,
with known biases: it favoured the answer shown first, longer answers, and its own style. Evals became part of building any AI application.

:::solved
**A number for answer quality.** Change the prompt, the chunks or the model, run the set, and compare.
:::

:::timeline
- **1997** JUnit.
- **2004** pytest.
- **2023** OpenAI Evals; LLM-as-a-judge studied.
:::

**Kent Beck**, who wrote SUnit and, with Erich Gamma, JUnit: the unit tests your Checks are descendants of.

:::photo{src="/lesson-images/langchain/kent-beck.webp" alt="Kent Beck speaking at a conference in 2005, gesturing with one hand" credit="Barry Mulling" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File%3AKent_Beck_tells_it_like_it_is%2C_2005.jpg"}
Kent Beck in 2005.
:::
:::

:::step{type=concept title="A golden set with phrases" file="26-evals/evals.py" line="5-19"}
`GOLDEN` holds six real questions. Each has a **phrase** the right answer must contain, and the rule file that answers
it:

| Question | Phrase | Why that phrase |
|---|---|---|
| Can I store 80 crates of onions? How long until I know? | approval | more than 50 crates needs the manager's approval |
| I sprayed my grapes on Monday. Can I harvest on Friday? | 10 days | the spraying rule |
| How much loan can I get for 4 acres? | 2,00,000 | Rs 50,000 per acre |
| Do you buy garlic? | don't know | not in any rule: the honest answer |

The **pass rate** is the share of answers containing their phrase (4 of 6 is 0.67, shown as 67%). It is cheap (no model call) and strict in the wrong ways:
"Rs 200,000" is right and fails the phrase "2,00,000"; "approval is not needed" contains "approval" and passes.
:::

:::step{type=task task=golden_eval title="Your turn: the pass rate" file="26-evals/evals.py" line="15-19"}
Finish `pass_rate(answers, golden)`:

1. Walk the answers and the golden entries side by side: `zip(answers, golden)`. Each entry is (question, phrase,
   rule file); the phrase is the second item.
2. Count an answer as passed when `phrase.lower() in answer.lower()`.
3. Return `passed / len(golden)`, a number from 0 to 1 (not a percentage).

The usual slips:

- Lower-casing only the answer: the phrase "Approval" then never matches.
- Returning `passed` (a count) or `passed * 100`: the check expects 0.75 for 3 of 4.

Press **Check**.
:::

:::step{type=concept title="A model as judge" file="26-evals/evals.py" line="22-36"}
A **judge** is a second model call that grades the first one's answer. It is chapter 13's structured output, used to
grade: the rule, the question and the answer go in; a `Grade` comes out.

```python
class Grade(BaseModel):
    correct: bool = Field(description="true only if the answer agrees with the rule in every detail")
    reason: str = Field(description="one sentence: what is right or wrong")
```

The judge sees the **rule**, which is what makes it useful: it does not need to know the co-op, only to compare. Its
`reason` makes every failure readable. Judges are models too: they can be wrong, and tend to be lenient with long,
confident answers. Check a sample of their grades yourself before trusting them.
:::

:::step{type=task task=judge_answer title="Your turn: the judge" file="26-evals/evals.py" line="32-36"}
Finish `judge(question, answer, rule)`:

1. Fill the prompt: `JUDGE.format(rule=rule, question=question, answer=answer)`.
2. Ask for a `Grade`: `model.with_structured_output(Grade)`.
3. Invoke it with the prompt and return the `Grade`.

The usual slip: `model.invoke(...)` without `with_structured_output`. That returns an `AIMessage` of free text,
and `grade.correct` in `main.py` fails with `AttributeError`.

```bash run
cd /workspace/26-evals && python main.py
```

Press **Check**.
:::

:::step{type=try title="Navin, graded"}
A real run (we ran it three more times on 25 November: 67% every time, the same two failures and the same verdicts,
in other words):

```text
$ python main.py 2>&1 | grep -v Warning
> Can I store 80 crates of onions? How long until I know?
  You can store 80 crates of onions, but you'll need to book this as your booking exceeds 50 crates. You can confirm your booking at the counter, and you will know right away. Don’t forget to label your crates with your member number.
  phrase 'approval': MISSING  judge: WRONG: The answer incorrectly states that the booking can be confirmed at the counter; it requires manager's approval which takes one working day.

> I sprayed my grapes on Monday. Can I harvest on Friday?
  No, you cannot harvest the grapes on Friday. You must wait for 10 days after spraying with a fungicide, so you can harvest the grapes the following Monday. Please remember to record every spray in the co-op's spray diary. [spraying.txt]
  phrase '10 days': found  judge: correct: The answer correctly states that harvesting cannot occur until 10 days after spraying, which aligns with the co-op's rule.

> How much loan can I get for 4 acres?
  You can borrow up to Rs 50,000 per acre, so for 4 acres, you can get Rs 2,00,000. Bring your 7/12 land record, member's passbook, and cost estimate to apply. Remember, if you have an unpaid loan, you won't be able to take a new one.
  phrase '2,00,000': found  judge: correct: The answer accurately calculates the loan amount for 4 acres and correctly states the application requirements and conditions.

> When will the money from my sale reach me?
  The money from your sale will reach your bank account within 3 working days of the sale.
  phrase '3 working days': found  judge: correct: The answer accurately reflects the rule stating that payment reaches the member's bank account within 3 working days of the sale.

> What does it cost to join the co-op?
  I don't know the cost to join the co-op. Please call the co-op office for more information.
  phrase '1,000': MISSING  judge: WRONG: The answer is incorrect because it fails to provide the specific cost to join the co-op, which is clearly stated in the rule.

> Do you buy garlic?
  I don't know if we buy garlic. Please call the co-op office for more information.
  phrase "don't know": found  

golden set: 67% of the answers contain their phrase
```

This is chapter 19's RAG agent, unchanged, graded on six questions. Two checks, two views:

- The **phrase check** says 67%: 4 of 6 answers contain their phrase.
- The **judge** read each answer against its rule and found the same two failures, with reasons a person can act on.

The failures are worth reading closely, because both are real bugs found by the eval:

1. **80 crates**, still wrong: "confirm your booking at the counter, and you will know right away". The judge named the
   problem exactly: the rule needs the manager's approval, which takes one working day. This is chapter 17's rule cut in
   half, chapter 19's wrong answer, and the reason chapter 20 split at sentences; this agent still uses the old chunks.
   (The capstone, chapter 27, uses the fixed ones.)
2. **The joining fee**: Navin said "I don't know", although `membership.txt` says Rs 1,000. An honest "I don't know"
   is better than an invented fee, but it is still a failure: retrieval did not bring the rule. The golden set turned
   "it seems fine" into two concrete bugs.

Notice also the loan answer: "Rs 2,00,000", correct, but **calculated by the model** (4 × 50,000), because this agent has
no loan tool. It was right this time; chapter 12's `crop_loan_limit` is the reliable way.
:::

:::step{type=predict title="Guess first"}
:::question
The golden set passes 100%. Is Navin correct?
:::
- [ ] Yes, proven
- [x] Correct on these questions; every real question that goes wrong should become a new golden question
- [ ] Evals prove nothing
:::explain
A golden set is a sample. It grows from real mistakes, so the same mistake cannot come back unnoticed.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why give the judge the rule, and not only the question and answer?
:::
- [x] So it compares the answer with the co-op's rule instead of its own general knowledge
- [ ] To make the call cheaper
- [ ] The judge cannot read questions
:::explain
A judge without the rule would grade plausibility, the very thing hallucinations are good at.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which test runs on every code change, for free?
:::
- [x] Unit tests with a fake model
- [ ] The golden set with the real model
- [ ] The judge
:::explain
Evals cost model calls; run them before a change of prompt, chunks or model, and on a schedule.
:::
:::

:::step{type=deep-dive title="Go deeper: evals in practice"}
**Agent trajectories.** Besides the final answer, check the path: did it call `search_rules` before answering a rule
question? Chapter 11's `tools_used` is a trajectory check.

**Tools for evals.** LangChain's docs describe agent evals with the open-source `agentevals` package and with
LangSmith (a hosted service that needs its own API key, which this course does not use).

**Cost.** One run of this chapter, from the backend's log: 16 chat calls (the 6 agent runs, most with a search, plus
5 judge calls) and 6 embedding calls, at about $0.00006 each with gpt-4o-mini's prices. A golden set of 200 questions
is about 600 chat calls, about $0.04 (prices of November 2026).

**The lab's limit.** The lab's gateway allows 20 model calls a minute. We ran `main.py` twice in a row and the second
run stopped with `429 - Too many requests: the limit is 20 a minute`. Wait a minute between runs. Real eval runs
hit the provider's limits the same way, which is why eval tools let you limit how many questions run at once.
:::

:::step{type=recap}
You can now:

- tell unit tests (your code, fake model) from evals (the answers, real model);
- score answers against a golden set, and see where phrase checks fail;
- build a judge with structured output that grades an answer against a rule;
- treat a judge's grades as evidence to check, not as truth.

Next, chapter 27: Navin goes live, everything in one web service.

:::photo{src="/lesson-images/langchain/lc-26-notes.webp" alt="Handwritten notes about tests and evals: Unit tests check your code with a fake model, for free. Evals check the real model's answers against a golden set. Our golden set scored 67% in all four runs. A phrase check reads letters; a judge reads meaning. Give the judge the rule, and check a sample of its grades. One run made 16 chat calls and 6 embedding calls." ai="true"}
One page of notes for this chapter.
:::
:::
