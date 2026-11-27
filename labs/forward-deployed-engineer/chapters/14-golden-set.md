:::step{type=story title="\"How often is it right?\""}
Monday of week six. The demo went well, and Meera, head of claims at Deccan Shield, has one question before she lets
Claimdesk near real claims:

"How often is it right?"

You could say "most of the time, it looked good on Friday". She would be right not to accept that. Friday's demo showed
five emails you picked. Nobody, including you, knows how Claimdesk does on the next hundred.

To answer with a number, you need three things:

1. a fixed set of **real** claim emails;
2. for each one, the **right answer**, written by someone who knows (not by the model);
3. a strict rule for when Claimdesk's answer **counts** as right.

That set is called a **golden set**. Last week Sunil and another senior adjuster went through the 30 emails you have used
since chapter 9 and wrote down, for each, the six fields as an adjuster would fill them. This chapter turns their work
into something code can measure against, every day, for every version.

:::mission
Write the rule that decides when a field is right, strictly, and pick a small sample that still covers every kind of
claim.
:::
:::

:::step{type=concept title="What is in the golden set" file="14-golden-set/data/golden.json"}
Open `data/golden.json`. Each case has the email exactly as it arrived, and the **truth**, the adjusters' answer:

```json
{
 "email_id": "E-03",
 "text": "Subject: Water in car\n\nHello, during the heavy rain on 6 Oct my car (MH12-EF-5678) was standing in water near Baner. Engine does not start. Policy DS-POL-40148. No estimate yet, garage will tell. Sending 4 photos.",
 "truth": {
  "policy_no": "DS-POL-40148",
  "vehicle_reg": "MH12EF5678",
  "incident_date": "2026-10-06",
  "incident_type": "flood",
  "amount_rs": null,
  "photos_attached": true
 }
}
```

Look at two details. The email says "6 Oct" with no year, and the adjusters wrote 2026, because they know when it
arrived. And there is **no estimate yet**, so `amount_rs` is `null`. An empty field is a real answer: "the email does not
say". If Claimdesk writes a number there, it has made one up.

What makes a golden set useful:

| Property | In ours | Why it matters |
|---|---|---|
| Real inputs | 30 emails as customers wrote them, typos and all | invented test emails are always too tidy |
| Truth from experts | two senior adjusters, not the model | if the model wrote the truth, you would measure it against itself |
| Every kind of case | accidents, thefts, floods, glass, fires, "other" | a rare kind can fail completely and an average would hide it |
| Empty fields | 6 fields left empty on purpose | tests that the model says "not given" instead of guessing |
| Hard cases | E-24 (a follow-up with a mismatched registration), E-30 (an email that tries to give the model orders) | the cases that hurt in production |
| Frozen | the file only changes on purpose, with a note | otherwise last week's number and this week's mean different things |
:::

:::step{type=history title="Something everyone measures against"}
:::before{title="Before: every town its own kilogram"}
Before the 1790s, a pound in one French town was not a pound in the next. Merchants argued, and there was no way to
settle the argument, because there was nothing to compare with.
:::

In 1889 an international conference approved a single metal cylinder kept near Paris, the **International Prototype of
the Kilogram**, as *the* kilogram. Countries received numbered copies; the United States received K20 and K4 in 1890.
Every scale in a country was checked against its national copy, and the copies were brought back to Paris from time to
time to be compared with the original. A measurement meant something because everyone measured against the same thing,
kept unchanged.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-kilograms.webp" alt="Four polished metal cylinders, the United States' national prototype kilograms, standing in a steel holder inside a round vacuum chamber." credit="J. Lee, NIST" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Kilograms-pml0013_K20_and_Friends_Four_of_the_five_U.S._national_prototype_kilogram_artifacts,_including_K20_(front)_and_K4_(back).png"}
Four of the United States' national kilograms, with K20 in front, at NIST.
:::

Machine learning learned the same lesson. Shared test sets, like MNIST for handwritten digits (1998) and ImageNet for
photos (2009), let researchers compare methods honestly: same questions, same answers, different systems.

In 2019 the kilogram was redefined from a constant of nature, so the metal cylinder is no longer needed. Your golden
set will never be that perfect; it is a small, honest sample that you keep improving.

:::solved
A fixed reference, kept unchanged, turns "it seems fine" into a number that means the same thing every time.
:::

:::timeline
- **1889** The International Prototype of the Kilogram is approved.
- **1890** The United States receives K20 and K4.
- **1998** MNIST becomes a shared test set for digit recognition.
- **2009** ImageNet is published.
- **2019** The kilogram is redefined; the cylinder retires.
:::

:::funfact
The copies drifted: over a century, weighings showed the national copies and the original differing by tens of
micrograms. That drift, about the weight of a grain of salt, is one reason the kilogram was redefined.
:::
:::

:::step{type=concept title="When does a field count as right?" file="14-golden-set/golden.py" line="19-27"}
Claimdesk read `ds-pol-40592` from E-16. The truth is `DS-POL-40592`. Right or wrong?

It is tempting to say "nearly right". But follow the value: chapter 13 looks the policy up with SQL, and
`WHERE policy_no = 'ds-pol-40592'` finds **nothing**. The claim is referred as "unknown policy". So for the business, it
was wrong. A rule that calls it right would report a number that is better than what the adjusters will experience.

So the rule is **as strict as the next step**:

| Truth | Claimdesk said | Right? | Why |
|---|---|---|---|
| `null` | `null` | yes | both say "not given" |
| `null` | `"null"` (the text) | no | the model wrote a word; code would treat it as a policy number |
| `"2026-10-06"` | `null` | no | it missed something the email said |
| `"DS-POL-40000"` | `" DS-POL-40000 "` | yes | only outer spaces differ; ignore them |
| `"DS-POL-40592"` | `"ds-pol-40592"` | no | the lookup is exact |
| `true` | `1` | no | a yes/no must be a real yes/no |
| `12500` | `"12500"` | no | the text is not the number |

In Python, `True == 1` is true, because `bool` is a kind of `int`. That is why a plain `got == truth` would call `1` right
for "photos attached", and call `True` right for an amount of 1 rupee. The check uses `is` for yes/no values, and
refuses bools where a number is expected.

Strict does not mean unfair. Later (chapter 16) you will **fix** formats in code, and then the fixed value will count.
What the rule refuses is pretending.
:::

:::step{type=example title="Worked example: a strict match for a library"}
This is only to read; it is not in your project. A library checks a scanner's readings against what is on the shelf:

```python
def reading_matches(got, truth):
    if truth is None:
        return got is None          # nothing on the shelf: the scanner must say nothing
    if got is None:
        return False                # a book is there, the scanner missed it
    if isinstance(truth, bool):
        return got is truth         # on_loan: True or False, nothing else
    if isinstance(truth, str):
        return isinstance(got, str) and got.strip() == truth
    return isinstance(got, int) and not isinstance(got, bool) and got == truth

print(reading_matches("BK-0042 ", "BK-0042"))   # True
print(reading_matches("bk-0042", "BK-0042"))    # False
print(reading_matches(1, True))                 # False
```

- The order matters: the `None` cases first, so later lines can assume both values exist.
- `isinstance(truth, bool)` comes **before** the number case, because a bool is also an `int`.
- `isinstance(got, int) and not isinstance(got, bool)` accepts `12500` and refuses `True`.
:::

:::step{type=predict title="Guess first"}
:::question
The starter's `field_match` is just `return got == truth`. What does it say for
`field_match("photos_attached", 1, True)`?
:::
- [x] True, because in Python 1 == True
- [ ] False, because 1 is not a bool
- [ ] It raises an error
:::explain
`True == 1` is true in Python. The starter would count a number as a yes/no answer. That is the kind of quiet looseness
that makes a report look better than reality.
:::
:::

:::step{type=try title="The loose version"}
```text
$ python golden.py
30 cases: {'accident': 13, 'theft': 4, 'flood': 3, 'glass': 4, 'fire': 2, 'other': 4}
fields the adjusters left empty (the email did not say): 6
two of each kind: ['E-01', 'E-02']
  field_match('policy_no', 'ds-pol-40592', 'DS-POL-40592') = False
  field_match('policy_no', 'null', None) = False
  field_match('incident_date', None, None) = True
  field_match('photos_attached', 1, True) = True
  field_match('amount_rs', 12500, 12500) = True
```

Two things to notice. `1` counts as `True`. And "two of each kind" gave two accidents and nothing else: the first two
emails, not a sample.
:::

:::step{type=task task=field_match title="Your turn: when a field is right"}
In `field_match` in `golden.py`, in this order:

1. If `truth is None`: right only when `got is None`.
2. If `got is None`: wrong.
3. If `truth` is a bool: `got is truth`.
4. If `truth` is a str: `got` is a str and `got.strip() == truth`.
5. Otherwise (numbers): `got` is an `int`, not a `bool`, and equal to `truth`.

Press **Check**.
:::

:::step{type=concept title="A small sample that keeps every kind" file="14-golden-set/golden.py" line="29-33"}
Running all 30 emails through the model is cheap but not instant: with the gateway's limit of 20 requests a minute
(chapter 9), a paced run takes about two minutes. While you are changing a prompt and trying ideas, you want something
quicker, then the full set before anything ships.

The obvious quick sample, "the first 12", is a bad one. Our set has 13 accidents and only 2 fires. The first emails are
mostly accidents, so a quick run could miss fires entirely, and a prompt change that breaks fires would pass.

A **stratified** sample takes up to N cases **of each kind**:

```text
kinds:   accident 13   theft 4   flood 3   glass 4   fire 2   other 4
2 each:  2             2         2         2         2        2         -> 12 cases, every kind
```

The kind comes from the **truth**, not from Claimdesk's answer: you are choosing what to test, before knowing what
Claimdesk will say. Keep the set's order, so the same call always gives the same sample.
:::

:::step{type=task task=stratified title="Your turn: two of each kind"}
In `stratified`:

1. Keep a list of cases and a dict that counts how many of each `incident_type` you have kept.
2. Go through `golden` in order. Keep a case while its kind's count is below `per_kind`, and add one to the count.

Press **Check**.
:::

:::step{type=try title="The golden set, ready to measure with"}
```text
$ python golden.py
30 cases: {'accident': 13, 'theft': 4, 'flood': 3, 'glass': 4, 'fire': 2, 'other': 4}
fields the adjusters left empty (the email did not say): 6
two of each kind: ['E-01', 'E-02', 'E-03', 'E-04', 'E-05', 'E-06', 'E-08', 'E-10', 'E-12', 'E-13', 'E-14', 'E-21']
  field_match('policy_no', 'ds-pol-40592', 'DS-POL-40592') = False
  field_match('policy_no', 'null', None) = False
  field_match('incident_date', None, None) = True
  field_match('photos_attached', 1, True) = False
  field_match('amount_rs', 12500, 12500) = True
```

Twelve cases, every kind of claim in them, including both fires: E-06, and E-21, which is far down the list but still
in. And the rule now refuses `1` as a yes/no. In the next chapter this rule scores real model output for the first time.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why must the truth in a golden set be written by the adjusters, not taken from the model's best answers?
:::
- [ ] The model's answers are too long
- [x] Measuring the model against its own answers would always say it is right
- [ ] Adjusters type faster
:::explain
A golden set is only useful if it can disagree with the model. Experts who do the job write it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Claimdesk returns `"DS POL 40999"` and the truth is `"DS-POL-40999"`. Is it right?
:::
- [ ] Yes, the digits are the same
- [x] No: the exact lookup would not find it, so for the business it is wrong
- [ ] Only on weekdays
:::explain
The rule is as strict as the next step. Chapter 16 fixes formats in code, and then the fixed value counts.
:::
:::

:::step{type=deep-dive title="Go deeper: golden sets at a customer"}
**Two people, then agree.** Have two experts write the truth separately for some cases, and compare. Where they
disagree, the task itself is unclear (is a scratch in a car park "accident" or "other"?). Write the rule down and fix
the case. The agreement rate is also the ceiling: if experts agree 95% of the time, do not promise 99%.

**Size.** 30 cases is a start. One case is 3.3 points of any percentage, so small differences mean little. Grow it
toward a few hundred, adding every case that went wrong in production.

**Do not tune on all of it.** If you change prompts until all 30 pass, you have fitted these 30. Keep some cases aside
that you only run before a release.

**It holds personal data.** Real emails contain names, phone numbers and registrations. Store the set where the
customer allows, with access limited, or redact it (chapter 17).

**Version it.** When a truth is corrected, note it. Otherwise a change in the score may be a change in the answers, not
in Claimdesk.
:::

:::step{type=recap}
You can now:

- explain what a golden set is and what makes one useful: real inputs, expert truth, every kind, empty fields, hard
  cases, frozen;
- write a match rule as strict as the next step, and know why `True == 1` matters;
- take a stratified sample that keeps rare kinds;
- explain why "nearly right" is wrong when the next step is exact.

Next, chapter 15: score two real versions of Claimdesk on the golden set, field by field, and build the gate that stops
a version that gets worse.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-14-notes.webp" alt="Handwritten notes about a golden set: A golden set: real emails, expert answers. Experts write the truth, never the model. Cover every kind, keep empty fields. Be as strict as the next step. In Python 1 == True: use is for bools. Sample two of each kind, not the first few." ai="true"}
One page of notes for this chapter.
:::
:::
