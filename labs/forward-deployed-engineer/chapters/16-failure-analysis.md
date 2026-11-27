:::step{type=story title="Do not guess the next prompt"}
The gate said no. Version 2 improved photos and policy numbers, and made dates worse.

The tempting next move is version 3: add another sentence about dates, run it, hope. Teams can spend weeks like that,
each new prompt fixing two emails and breaking one, because they never looked at **what** went wrong.

This chapter does the slower, faster thing. Take every wrong field in both runs, look at it, and sort it into a **kind**
of failure. Then fix kinds, not emails, and fix each kind in the place it belongs: some in the prompt, most in code.

:::mission
Sort every wrong field into a kind of failure, then fix the kinds that code can fix, and measure the result.
:::
:::

:::step{type=concept title="Four kinds of wrong" file="16-failure-analysis/failures.py" line="14-20"}
For one field, Claimdesk's value `got` and the adjusters' `truth` can disagree in four ways:

| Kind | Meaning | Example from the real runs |
|---|---|---|
| missing | the email said it, Claimdesk read nothing | (none in these runs) |
| invented | the email did not say it, Claimdesk filled it in | E-12, "scratched my car ... yesterday": the date was set to 2026-10-30 |
| format | the right value, written differently | E-16: `ds-pol-40592` for `DS-POL-40592` |
| wrong | a different value | E-03: 2023-10-06 for 2026-10-06 |

The order of the tests matters:

1. `got is None`: **missing** (we know the field is wrong, so the truth has a value).
2. `truth is None`: **invented**. This includes the text `"null"`: the model wrote a word where it should have left the
   field empty.
3. Same once spaces, dashes and capitals are ignored: **format**. `squash` (already written, line 9) does that:
   `"ds pol-40999"` becomes `"DSPOL40999"`.
4. Anything else: **wrong**.

Why kinds? Because each kind has a different cure. Format problems are fixed in code, reliably. Invented values come from
a model trying too hard to fill a form, and need a different fix. A table of kinds tells you where to work; a list of 9
emails only tells you what to patch.
:::

:::step{type=history title="Sorting deaths by cause"}
:::before{title="Before: deaths counted, causes not"}
In the winter of 1854, during the Crimean War, British soldiers were dying in great numbers in army hospitals. Everyone
could see the deaths. The common belief was that they died of their wounds.
:::

Florence Nightingale led the nurses at the army hospital at Scutari. After the war, she and the statistician William
Farr sorted the deaths by **cause**, month by month. Most soldiers had not died of wounds. They had died of diseases spread by dirty water and
crowded wards, which could be prevented. After a sanitary commission cleaned the hospitals in the spring of 1855, the
death rate fell sharply.

In 1858 she published the figures as a diagram: each month a wedge, its area showing deaths, coloured by cause. Blue,
preventable disease, filled most of it.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-nightingale.webp" alt="Florence Nightingale's diagram of the causes of mortality in the army in the East: two rose-shaped charts made of monthly wedges, mostly pale blue for preventable disease, with smaller pink wedges for wounds and dark grey for other causes." credit="Florence Nightingale" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Nightingale-mortality.jpg"}
Nightingale's 1858 diagram: the blue wedges are deaths from preventable disease.
:::

The lesson for Claimdesk is the same. A total ("9 wrong fields") tells you there is a problem. Sorting by cause tells you
what to do about it.

:::solved
Count failures by cause, and the biggest cause becomes obvious, and fixable.
:::

:::timeline
- **1854** Nightingale arrives at Scutari.
- **1855** A sanitary commission cleans the hospitals; deaths fall.
- **1858** Her diagram of the causes of mortality is published.
- **Today** "Error analysis", sorting a model's failures by kind, is the first step teams take when evals disappoint.
:::

:::funfact
Florence Nightingale was the first woman elected a member of the Royal Statistical Society.
:::
:::

:::step{type=example title="Worked example: sorting scanner errors"}
This is only to read; it is not in your project. The library scanner's wrong readings, sorted:

```python
def kind_of_error(got, truth):
    if got is None:
        return "missed"
    if truth is None:
        return "phantom"           # it read a book that is not there
    if squash(got) == squash(truth):
        return "format"            # bk 0042 for BK-0042
    return "wrong"

from collections import Counter
table = Counter(kind_of_error(g, t) for g, t in wrong_readings)
print(table.most_common())
# [('format', 31), ('wrong', 4), ('phantom', 2)]
```

- The same four questions, in the same order, as Claimdesk's.
- `Counter` counts each kind; `most_common()` puts the biggest first.
- 31 of 37 errors are formats: one normalising line in code fixes most of the problem. Without the table, someone would
  have bought a new scanner.
:::

:::step{type=predict title="Guess first"}
:::question
Version 2 returned `"null"` as E-05's policy number (the customer wrote "i dont remember policy number"). The truth is
`None`. Which kind is it?
:::
- [ ] missing
- [x] invented
- [ ] format
:::explain
The truth is empty and Claimdesk filled the field with something: the word "null". The intent was right; the output
was not, and code reading it would look up a policy called "null".
:::
:::

:::step{type=try title="Everything looks the same"}
With the starter, every failure is "wrong":

```text
$ python failures.py
run v1: 9 wrong fields
   5 x incident_date   wrong     e.g. E-03: got '2023-10-06', truth '2026-10-06'
   2 x policy_no       wrong     e.g. E-16: got 'ds-pol-40592', truth 'DS-POL-40592'
   1 x photos_attached wrong     e.g. E-02: got True, truth False
   1 x incident_type   wrong     e.g. E-12: got 'accident', truth 'other'
...
```

Nine fields, one label. You cannot tell a typing difference from a made-up date.
:::

:::step{type=task task=classify_failure title="Your turn: name the kind"}
In `classify_failure` in `failures.py`, in this order: `got is None` gives `"missing"`; `truth is None` gives `"invented"`;
`squash(got) == squash(truth)` gives `"format"`; anything else is `"wrong"`.

Press **Check**.
:::

:::step{type=try title="What really went wrong"}
```text
$ python failures.py
run v1: 9 wrong fields
   4 x incident_date   wrong     e.g. E-03: got '2023-10-06', truth '2026-10-06'
   2 x policy_no       format    e.g. E-16: got 'ds-pol-40592', truth 'DS-POL-40592'
   1 x photos_attached wrong     e.g. E-02: got True, truth False
   1 x incident_date   invented  e.g. E-12: got '2023-10-02', truth None
   1 x incident_type   wrong     e.g. E-12: got 'accident', truth 'other'
run v2: 8 wrong fields
   4 x incident_date   wrong     e.g. E-03: got '2023-10-06', truth '2026-10-06'
   2 x incident_date   invented  e.g. E-12: got '2026-10-30', truth None
   1 x policy_no       invented  e.g. E-05: got 'null', truth None
   1 x incident_type   wrong     e.g. E-12: got 'accident', truth 'other'
...
```

Now each line is a story you can act on:

- **The year.** In both versions, four dates are the right day and month in the wrong year: "6 Oct" became 2023. Version 2
  told the model today's date and it **still** wrote 2023 for the same four emails.
- **The made-up dates.** E-12 says "yesterday", and E-24 says "last week". The email text does not say when it was sent,
  so the adjusters left the date empty. Version 2, told that today is 31 October, worked out 30 October and 24 October.
  Those dates are guesses about when the email was written, and that is why dates went down in chapter 15.
- **Formats.** Version 1 wrote two policy numbers in small letters. Version 2's format sentence fixed them, but turned
  E-05's missing policy into the word `"null"`.
- **Photos.** E-02 says "FIR filed, copy attached": a police report, not photos. Version 2's photos sentence fixed it.
- **E-12's type.** A scratch in a car park: "accident" or "other"? The adjusters say "other" (it is vandalism). That is a
  question about the rules, not the model; write the rule down with the adjusters.
:::

:::step{type=concept title="Fix each kind where it belongs" file="16-failure-analysis/failures.py" line="22-30"}
Now decide, kind by kind:

| Kind | Where to fix it | Why |
|---|---|---|
| policy number format | **code**: rebuild `DS-POL-` and five digits | exact, testable, never forgets |
| the word "null" | **code**: any `"null"` text becomes `None` | the same |
| a day and month in the wrong year | **code**: use this year, or last year if that would be after today | the prompt already failed to fix it, twice |
| photos vs other attachments | **prompt**: keep version 2's photos sentence | it is about reading meaning, which is the model's job |
| dates guessed from "yesterday" | **prompt**: drop the "today is" line | it caused them; and code cannot tell a guess from a real date |
| scratch: accident or other | **the adjusters**: write the rule | the task itself was unclear |

The rule from chapter 11 again: the model reads, code does anything exact. Fixing a year is arithmetic on dates, so it
belongs in code, where you can test it with any date you like.

The year rule, with today as 31 October 2026:

```text
2023-10-06  -> 2026-10-06   (6 October 2026 is not after today)
2023-12-20  -> 2026-12-20 would be after today -> 2025-12-20
2026-10-06  -> unchanged    (already this year)
```

Its limit, stated honestly: it assumes claims are about recent incidents. A real incident from an earlier year would be
moved into this year, and could then look covered. Deccan Shield's wording asks for claims within 7 days (clause C5,
chapter 10), so that is rare, and in the pilot an adjuster still reviews every draft. At another customer, check the
assumption first.
:::

:::step{type=task task=fix_fields title="Your turn: fix the kinds that code can fix"}
In `fix_fields`, on a copy of the dict (`dict(fields)`):

1. Every str value equal to `"null"`, in any case, becomes `None`.
2. If `policy_no` squashes to `DSPOL` and five digits (`re.fullmatch(r"DSPOL\d{5}", ...)`), write it as
   `"DS-POL-"` and the five digits.
3. If `incident_date` is in a year before today's, use today's year; if that date is after today, use the year before.

Leave right values as they are, and return the copy. The check runs your fixes on the real version 1 output. Press
**Check**.
:::

:::step{type=try title="73.3% to 93.3%"}
```text
$ python failures.py
...
v1 before and after the code fixes:
   policy_no          93.3  100.0
   vehicle_reg       100.0  100.0
   incident_date      83.3   96.7
   incident_type      96.7   96.7
   amount_rs         100.0  100.0
   photos_attached    96.7   96.7
   all_fields         73.3   93.3
```

Emails with every field right went from 22 of 30 to 28 of 30, without touching the prompt, and nothing got worse (the
gate from chapter 15 would pass). Version 2's prompt reached 80.0% and failed the gate.

Two emails are left. E-02 is the photos case, which version 2's photos sentence fixes. E-12 is the invented date and the
unclear type. So the next version is small and clear: version 1's prompt, plus the photos sentence, plus these code
fixes, and the gate decides.

That is the whole method of this part: a golden set to measure on, evals and a gate to decide, and failure analysis to
know what to change next.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Four dates came back as 2023 instead of 2026, even after the prompt said "Today is 2026-10-31". What is the better fix?
:::
- [ ] Repeat the sentence three times in the prompt
- [x] Correct the year in code, with a rule you can test
- [ ] Ask customers to always write the year
:::explain
The prompt failed twice. The fix is date arithmetic, which code does exactly and the tests can prove.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
E-12 says "someone scratched my car ... yesterday". Version 2 wrote 2026-10-30. Why is that counted as invented?
:::
- [ ] 30 October is a Friday
- [x] The email's text does not say when it was sent, so "yesterday" has no date; the model guessed one
- [ ] Dates must be in 2023
:::explain
The adjusters left it empty. To fill it truly, Claimdesk would need the email's received time from the mailbox, which is
data, not a guess.
:::
:::

:::step{type=deep-dive title="Go deeper: error analysis as a habit"}
**Look at the outputs.** Before writing any eval code, read 20 to 50 real outputs yourself and write a note on each
wrong one. The kinds come from those notes. Teams that skip this build careful dashboards that measure the wrong things.

**Use the data you already have.** "Yesterday" is relative to the email's arrival time, which the mailbox records. Pass
that time with each email ("This email arrived on 2026-10-31") instead of today's date, and "yesterday" becomes a real
date. Many model problems are missing-context problems.

**Every fix gets a test.** `fix_fields` has a test for each rule. When a new failure kind appears in production, add the
email to the golden set and the rule to the tests.

**Watch the remaining kinds.** The table of kinds is worth running every week on real traffic (chapter 20): a new kind
appearing is often the first sign that the emails have changed.
:::

:::step{type=recap}
You can now:

- sort every wrong field into missing, invented, format or wrong, in an order that makes the kinds unambiguous;
- read a failure table and see causes, not just counts;
- decide where each fix belongs: code for exact rules, the prompt for reading meaning, the customer for unclear rules;
- show the effect of a fix on the golden set: 73.3% to 93.3% of emails fully right, with no field worse.

Next, chapter 17 starts the last stretch before real claims: the emails hold names, phone numbers and one attempt to
give Claimdesk orders. Keep personal data out of logs, and treat the email as data.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-16-notes.webp" alt="Handwritten notes about failure analysis: Sort failures into kinds, fix the kinds. Missing, invented, format, wrong. The year was wrong in both prompts. Fix exact things in code, with tests. Fix meaning in the prompt. 73.3 to 93.3, nothing worse." ai="true"}
One page of notes for this chapter.
:::
:::
