:::step{type=story title="A better prompt, or is it?"}
Chapter 9 ended with a puzzle: the model wrote some dates in **2023**, because emails like "6 Oct" have no year and the
model does not know today's date. Its notes said: tell the model today's date.

So you wrote version 2 of the prompt. It adds three things to chapter 9's prompt:

- "Today is 2026-10-31": for a day and month without a year, use the most recent such date that is not after today, and
  never guess a date the email does not give;
- "Write policy numbers exactly as DS-POL- and five digits";
- "photos_attached is true only when photos or pictures of the vehicle are attached, not other documents".

You tried it on three emails. It looked better. Is it?

Both versions were run on all 30 golden emails through the gateway, with the real model, and their answers saved in
`data/run_v1.json` and `data/run_v2.json`. In this chapter you score them and decide with numbers, not with three
emails and a feeling.

:::mission
Score a run against the golden set, field by field, and build a gate that refuses any version in which a field got
worse.
:::
:::

:::step{type=concept title="An eval report" file="15-evals/evals.py" line="35-41"}
An **eval** (short for evaluation) runs a system on cases with known answers and reports how often it was right. Ours
reports two kinds of number.

**Per field.** For each of the six fields, the percentage of emails where `field_match` says it is right. Per field,
because the fields fail for different reasons and matter differently: a wrong amount is caught by the pilot limit
(chapter 13), a wrong date can wrongly put a claim outside its policy period.

**All fields.** The percentage of emails where **every** field is right. This is the number an adjuster feels: an email
with even one wrong field needs a person to fix it.

These two kinds can tell very different stories:

```text
policy_no 95%, vehicle_reg 95%, incident_date 95%, ...  (each field looks fine)
all_fields: could be as low as 70%                       (the errors are in different emails)
```

Two rules for the report:

- An email the run **could not read** (its `fields` is `null`, chapter 9's `safe_extract` set it aside) counts as wrong
  on every field. Leaving it out would make a version that fails on hard emails look better.
- Percent is right divided by the **number of cases**, rounded to one decimal place. With 30 cases, one email is 3.3
  points.
:::

:::step{type=example title="Worked example: scoring a scanner"}
This is only to read; it is not in your project. Scoring the library scanner from chapter 14 on two fields:

```python
FIELDS = ["book_id", "on_loan"]

def report(golden, run):
    right = {f: 0 for f in FIELDS}
    whole = 0
    for case in golden:
        got = run.get(case["id"])
        oks = [got is not None and reading_matches(got[f], case["truth"][f])
               for f in FIELDS]
        for f, ok in zip(FIELDS, oks):
            right[f] += ok
        whole += all(oks)
    n = len(golden)
    out = {f: round(right[f] / n * 100, 1) for f in FIELDS}
    out["all_fields"] = round(whole / n * 100, 1)
    return out
```

- `oks` holds one True/False per field for this case. `got is not None and ...` makes an unread case False everywhere.
- `right[f] += ok` works because True counts as 1 and False as 0 when added.
- `all(oks)` is True only when every field is right: that is the "all fields" count.
:::

:::step{type=predict title="Guess first"}
:::question
Version 2 told the model today's date, the policy format and a photos rule. Which is most likely on the full 30 emails?
:::
- [ ] Every field improves or stays the same
- [x] Some fields improve and at least one gets worse
- [ ] Nothing changes, prompts do not matter
:::explain
A prompt is read for every email, so a change aimed at three emails can change answers on all thirty. That is why you
measure every field, every time. The real numbers are below.
:::
:::

:::step{type=try title="Nothing to compare yet"}
```text
$ python evals.py
field                v1     v2
Traceback (most recent call last):
  File "/workspace/15-evals/evals.py", line 57, in <module>
    print(f"{field:<16}{v1[field]:>7}{v2[field]:>7}")
                        ~~^^^^^^^
KeyError: 'policy_no'
```

`eval_report` returns an empty dict, so there is no `policy_no` to print.
:::

:::step{type=task task=eval_report title="Your turn: the eval report"}
In `eval_report` in `evals.py`:

1. Count right answers per field, and the emails with every field right.
2. For each case, `got = run.get(case["email_id"])`; a field is right when `got` is not `None` and `field_match` says so.
3. Return each field's percent (right / number of cases * 100, rounded to 1 place) and `"all_fields"` the same way.

Press **Check**.
:::

:::step{type=concept title="The gate: no field may get worse" file="15-evals/evals.py" line="43-48"}
Suppose version 2 has a higher "all fields" score. Ship it?

Not yet. Look at **each** field. If one field got worse, then some emails that were right are now wrong. For a field like
the incident date, that is serious: chapter 13 checks the date against the policy period, so a wrong date can refer a
covered customer, or pass a claim that should have been looked at.

A **regression** is something that used to work and no longer does. A **regression gate** compares the new report with
the old one and refuses the change when any field fell:

```text
(ok, drops) = regression_gate(before, after)
drops: [(field, before, after), ...]   every field that fell
ok:    True only when drops is empty
```

It works like a go/no-go gauge in a workshop: a part passes only if the "go" end fits and the "no go" end does not. No
opinions, no "it is nearly fine", and the same answer for whoever checks.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-gauge.webp" alt="Two steel plug gauges lying on a table. Each has a GO end and a NOT GO end; the lower one has a green handle at the go end and a red one at the no-go end, marked 12.60 mm and 12.90 mm." credit="Glenn McKechnie" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:GaugePlugThreadGoNoGo.jpg"}
Go and no-go plug gauges: a hole passes only if the go end fits and the no-go end does not.
:::

**Tolerance.** At temperature 0 a model usually gives the same answer twice, but not always. With 30 cases, one email
changing is 3.3 points. A `tolerance` lets you accept a fall of up to that many points, as noise. It starts at 0: allow
noise only when you have seen it, and say how much.

:::diagram{name="fde-eval-gate"}
The real numbers from the two runs you score in this chapter.
:::
:::

:::step{type=task task=regression_gate title="Your turn: the regression gate"}
In `regression_gate`:

1. For each field in `FIELDS + ["all_fields"]`, in that order, add `(field, before[field], after[field])` to `drops` when
   `after[field] < before[field] - tolerance`.
2. Return `(not drops, drops)`.

Press **Check**.
:::

:::step{type=try title="The real verdict"}
```text
$ python evals.py
field                v1     v2
policy_no          93.3   96.7
vehicle_reg       100.0  100.0
incident_date      83.3   80.0
incident_type      96.7   96.7
amount_rs         100.0  100.0
photos_attached    96.7  100.0
all_fields         73.3   80.0
gate: FAIL [('incident_date', 83.3, 80.0)]
```

Read it slowly.

- Version 2 looks better where you would look first: **all fields** went from 73.3% to 80.0%, two more emails fully
  right. The policy format rule and the photos rule both worked.
- But **incident date** went **down**, from 83.3% to 80.0%. The very field version 2 was written to fix got worse.
- The gate refuses it, and names the field.

Telling the model today's date did not stop it writing 2023 for "6 Oct". And it caused something new, which you will
see in the next chapter. If you had shipped on "all fields went up", the field that decides coverage would have got
worse in production, and nobody would have known why.

Also notice what is **not** a problem: registration and amount are 100% in both. Measuring every field shows you where
not to spend effort.
:::

:::step{type=history title="Tests that run on every change"}
:::before{title="Before: testing at the end"}
For a long time, software was tested in a big phase at the end of a project. Changes piled up for months, and when
something broke, nobody could tell which change did it.
:::

In 1991 Grady Booch used the term **continuous integration** in a book on software design: put everyone's changes
together often. In 1999 Kent Beck's *Extreme Programming Explained* made it a habit with tests: every change runs the
whole test suite, and a change that breaks a test does not go in. That is a regression gate.

Language models brought a new problem. Their outputs are not simply right or wrong like a function's, and a small
prompt change can move many answers. In March 2023 OpenAI open-sourced **Evals**, a framework for running a model on
sets of cases and scoring the results. Today "write the evals first" is common advice for teams building with models.

:::solved
Every change is measured on the same cases before it ships, and a change that makes anything worse is stopped
automatically.
:::

:::timeline
- **1991** Grady Booch names continuous integration.
- **1999** *Extreme Programming Explained* makes tests on every change a habit.
- **March 2023** OpenAI open-sources Evals.
- **Today** Teams run evals on every prompt or model change, like unit tests.
:::

:::funfact
"Regression" means "going back". In 1886 Francis Galton used it in a paper on the heights of parents and children
("regression towards mediocrity"), which is where statistics' "linear regression" gets its name. Programmers use it for
a thing that worked and went back to not working.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Version 2 raised "all fields" from 73.3% to 80.0% but lowered the incident date from 83.3% to 80.0%. What should happen?
:::
- [ ] Ship it, the overall number is higher
- [x] Do not ship it yet: find out why dates got worse first
- [ ] Delete the golden set
:::explain
The gate exists for exactly this. Chapter 16 finds out why, and fixes it without losing the improvements.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is an email the run could not read counted as wrong on every field?
:::
- [x] Leaving it out would make a version that fails on hard emails look better
- [ ] It saves time
- [ ] Python requires it
:::explain
If unread emails were skipped, a version could raise its score by failing on difficult emails. Every case counts.
:::
:::

:::step{type=deep-dive title="Go deeper: evals in practice"}
**Free-text answers.** Fields can be compared exactly. Answers like chapter 10's cannot. Teams check what they can
exactly (does it cite a clause that was sent?) and, for the rest, use a rubric that a person or a second model grades,
checking that grader against people too.

**Per kind.** Also report by incident type. A version can be fine on accidents and fail every flood, and with only 3
floods the overall number barely moves.

**Run it twice.** Before trusting a small difference, run the same version twice. If the numbers move, that is your
noise level, and your tolerance.

**Cost.** One full run here is 30 model calls. Cheap, but a gate on every change in a team runs often; the stratified
sample from chapter 14 is for quick checks while working, the full set for the gate.

**In CI.** In chapter 21 this gate runs automatically before every deploy, so the customer's team keeps it after you
leave.
:::

:::step{type=recap}
You can now:

- run an eval: score a version on the golden set, per field and for all fields;
- count unread emails as wrong, and know why;
- build a regression gate that refuses a change when any field falls, with an explicit tolerance;
- read a real report and see that a higher average can hide a worse field.

Next, chapter 16: look at every wrong field in both runs, sort them into kinds, and fix the causes.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-15-notes.webp" alt="Handwritten notes about evals and the regression gate: An eval scores every field on the golden set. An unread email is wrong on every field. One email out of 30 is 3.3 points. All fields went up: 73.3 to 80.0. Dates went down: 83.3 to 80.0. The gate stops it if any field falls." ai="true"}
One page of notes for this chapter.
:::
:::
