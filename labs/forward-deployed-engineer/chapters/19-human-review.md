:::step{type=story title="A week in the shadows"}
Meera agrees to the next step, with a condition: "For one week, it runs, and nobody sees it."

This is **shadow mode**. Every claim email goes to the adjusters exactly as before, and they decide as they always
have. Claimdesk also reads every email and writes its draft, but the drafts go into a file, not onto anyone's screen. At
the end of the week you compare, claim by claim: what Claimdesk drafted, and what the adjuster actually did.

Why hidden? Because once people see a suggestion, it changes what they do. If the adjusters saw the drafts, you would be
measuring how often they agree with Claimdesk, not how often Claimdesk agrees with good judgement.

The week's file is `data/shadow_week1.json`: 30 claims. Claimdesk's drafts are what chapter 13's rules give on the
real model's version 1 output with chapter 16's fixes. The adjusters' decisions and notes are theirs.

:::mission
Compare a week of hidden drafts with the adjusters' real decisions, separate the safe disagreements from the
dangerous ones, and decide with agreed numbers whether Claimdesk may go live.
:::
:::

:::step{type=concept title="Two kinds of disagreement" file="19-human-review/review.py" line="13-19"}
Each claim has a Claimdesk draft (`pay` or `refer`) and an adjuster decision (`pay` or `refer`). Four combinations:

| Claimdesk | Adjuster | Name | What it would cost if Claimdesk were trusted |
|---|---|---|---|
| pay | pay | agree | nothing: time saved |
| refer | refer | agree | nothing: the right claim reached a person |
| refer | pay | **extra work** | an adjuster spends a few minutes on a claim that was fine |
| pay | refer | **unsafe** | money paid on a claim a person would have stopped |

These two disagreements are not equally bad. Extra work costs minutes. An unsafe draft costs rupees, possibly to a
fraudster, and trust, which is harder to win back. So the report keeps them apart and lists the claims by id, so you
can read each one.

The same idea appears wherever errors have different costs. A medical screening test is tuned to miss as few sick
patients as possible, accepting more false alarms. Claimdesk is tuned the same way: when in doubt, refer.
:::

:::step{type=example title="Worked example: a spam filter in shadow mode"}
This is only to read; it is not in your project. A new spam filter runs silently beside people sorting their mail:

```python
def compare(rows):
    lost, nuisance = [], []
    for r in rows:
        if r["filter"] == "spam" and r["person"] == "keep":
            lost.append(r["id"])        # a real email would vanish: unsafe
        elif r["filter"] == "keep" and r["person"] == "spam":
            nuisance.append(r["id"])    # one spam gets through: annoying
    agree = len(rows) - len(lost) - len(nuisance)
    return {"agree": agree, "lost": lost, "nuisance": nuisance,
            "agreement": round(agree / len(rows) * 100, 1)}
```

- One pass over the rows; every row lands in exactly one bucket.
- `agree` is computed as what is left, so the three numbers always add up to the total.
- Which mistake is "unsafe" depends on the job. For spam, losing a real email is the expensive one.
:::

:::step{type=try title="A report that sees nothing"}
```text
$ python review.py
week1: 0 of 30 agree (0.0%)
   go live? (True, [])
week1_replayed: 0 of 30 agree (0.0%)
   go live? (True, [])
```

Two problems. The report sees no agreement and no disagreement. And the go-live check says **yes** to all of it. A gate
that always says yes is worse than no gate, because people believe it.
:::

:::step{type=task task=shadow_report title="Your turn: the shadow report"}
In `shadow_report` in `review.py`:

1. Go through the rows once. Claimdesk `pay` and adjuster `refer`: add the id to `unsafe`. Claimdesk `refer` and adjuster
   `pay`: add it to `extra_work`.
2. `agree` is the number of rows minus both lists.
3. Return `cases`, `agree`, `agreement` (agree / cases * 100, rounded to 1 place), `unsafe` and `extra_work`.

Press **Check**.
:::

:::step{type=concept title="Go live by numbers agreed in advance" file="19-human-review/review.py" line="21-26"}
When is Claimdesk ready? If you decide after seeing the week's results, you will find a reason to say yes; everyone
wants the project to succeed. So the criteria are agreed with Meera **before** the week starts, written down like
chapter 3's measurable goal:

1. **Enough cases**: at least 30. Fewer, and one claim is more than 3 points of agreement.
2. **No unsafe drafts.** Not "few": none. Each one is read, understood and fixed before going live.
3. **Agreement of at least 90%.** Below that, adjusters would spend more time correcting drafts than the drafts save.

`go_live_check` returns `(ok, reasons)` with a reason for every rule that fails, in that order. Not just the first:
Meera needs the whole list to plan the next week.

"Go live" here does not mean "decides alone". It means the drafts appear on the adjusters' screens, and an adjuster
accepts or changes each one. Deciding alone, for some kinds of claim, would be a later step with its own evidence.
:::

:::step{type=task task=go_live_check title="Your turn: the go-live check"}
In `go_live_check`, build `reasons` in this order, each only when it applies:

1. fewer than `min_cases` cases: `f"only {cases} cases, need {min_cases}"`;
2. any unsafe ids: `"unsafe drafts: "` and the ids joined with `", "`;
3. agreement below `min_agreement`: `f"agreement {agreement}% is below {min_agreement}%"`.

Return `(not reasons, reasons)`. Press **Check**.
:::

:::step{type=try title="What the shadow week found"}
```text
$ python review.py
week1: 25 of 30 agree (83.3%)
   unsafe     E-02 theft    Claimdesk pay, adjuster: theft: sent to the investigation team; paid after the police's final report
   unsafe     E-25 theft    Claimdesk pay, adjuster: theft: investigation team
   unsafe     E-30 accident Claimdesk pay, adjuster: the email tells us to approve Rs 1,00,000: called the customer
   extra_work E-15 accident Claimdesk refer, adjuster: estimate checked with the garage, paid
   extra_work E-19 flood    Claimdesk refer, adjuster: surveyor's photos fine, paid
   go live? (False, ['unsafe drafts: E-02, E-25, E-30', 'agreement 83.3% is below 90.0%'])
...
```

Read the unsafe ones. Claimdesk read every field of E-02 and E-25 correctly; the model was not the problem.

**Thefts.** Every theft at Deccan Shield goes to the investigation team, and is paid only after the police's final
report. Nobody mentioned it in discovery (chapter 2), because to an adjuster it is too obvious to say. Claimdesk's rules
never heard of it. Shadow mode is how you find the rules that live only in people's heads.

**E-30** is chapter 17's email that tries to give orders. In this week's run the instruction guard was not yet in
Claimdesk.

The extra-work pair, E-15 and E-19, are above the pilot limit, so Claimdesk referred them, as agreed in chapter 3.
The adjusters checked and paid. That is the limit doing its job, not a mistake.

So two changes: a theft rule (`theft: investigation team`, always refer) and chapter 17's guard. Then the same week is
**replayed**: the same 30 emails, through the changed Claimdesk:

```text
week1_replayed: 28 of 30 agree (93.3%)
   extra_work E-15 accident Claimdesk refer, adjuster: estimate checked with the garage, paid
   extra_work E-19 flood    Claimdesk refer, adjuster: surveyor's photos fine, paid
   go live? (True, [])
```

No unsafe drafts, 93.3% agreement, every criterion met. The replay is how you show a fix works on real cases before
the next live week, which then has to confirm it on claims nobody has seen yet.
:::

:::step{type=history title="Too much airplane for one person"}
:::before{title="Before: experts relied on memory"}
In the 1930s, aircraft became much more complex: more engines, retractable landing gear, adjustable propellers, flaps,
control locks. Pilots were expected to remember every step. They were experts, and experts do not forget. Until they do.
:::

On 30 October 1935, Boeing's Model 299, the most advanced bomber of its day, took off for an evaluation flight at Wright
Field in Ohio, climbed steeply, stalled and crashed. Two of the five people on board died. The cause: the control lock,
which holds the control surfaces still on the ground, had not been released. The pilot was one of the Army's most
experienced test pilots.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-model299.webp" alt="A black-and-white photo of a large four-engine silver airplane with a glazed nose, parked on a concrete apron under a cloudy sky." credit="U.S. Air Force" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Boeing_XB-17_(Model_299).jpg"}
Boeing's Model 299, which became the B-17.
:::

The answer was not more training. Test pilots wrote a short **checklist** for takeoff, landing and the steps between, and
read it every time. The aircraft went into service as the B-17. Checklists spread through aviation, and later into
operating theatres.

A go-live check is the same idea for software: a short list of conditions, agreed when everyone is calm, read when
everyone is in a hurry.

:::solved
Do not rely on judgement in the moment for things that can be decided in advance. Write them down and check them every
time.
:::

:::timeline
- **30 October 1935** The Model 299 crashes at Wright Field.
- **1930s** Pilots' checklists are introduced; the aircraft enters service as the B-17.
- **2008** The World Health Organization introduces a surgical safety checklist.
- **Today** Launches, deploys and go-lives run on checklists.
:::

:::funfact
A newspaper report after the crash said the Model 299 was "too much airplane for one man to fly". The checklist proved it
was not.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why are the drafts hidden from the adjusters during the shadow week?
:::
- [ ] To save screen space
- [x] Seeing a suggestion changes people's decisions, and you want to compare Claimdesk with their own judgement
- [ ] Because the drafts are secret
:::explain
Shown drafts pull decisions toward them. Hidden drafts give an honest comparison.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The week has 97% agreement but one unsafe draft. Go live?
:::
- [ ] Yes, 97% is excellent
- [x] No: read the unsafe case, fix its cause, and show the fix on a replay first
- [ ] Yes, but only on Mondays
:::explain
Unsafe drafts are not averaged away. Each one points at a rule Claimdesk does not know yet.
:::
:::

:::step{type=deep-dive title="Go deeper: humans in the loop"}
**Automation bias.** Once drafts are on screen, people accept them more often than they should, especially when busy.
Keep measuring after go-live: how often do adjusters change a draft? A rate near zero may mean the drafts are excellent,
or that nobody is reading them. Review a random sample of accepted drafts every week.

**Make disagreeing easy.** One click to change a draft, with a short list of reasons. Those reasons are your next
failure analysis (chapter 16).

**Earn autonomy in steps.** Draft only; then auto-pay one narrow kind (small glass claims, say) with a sample audited;
then widen. Each step has its own criteria and its own shadow period.

**Write down who decides.** For every kind of claim: does Claimdesk draft, decide, or stay out? This table belongs in
the handover (chapter 21).
:::

:::step{type=recap}
You can now:

- run a system in shadow mode, hidden from the people it will later help, and compare;
- separate unsafe disagreements from extra work, because their costs differ;
- check go-live criteria agreed in advance, and list every reason that fails;
- use a replay of the same cases to show a fix works before the next live week.

Next, chapter 20: Claimdesk is live. Watch it: daily numbers from its log, and alerts when they drift.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-19-notes.webp" alt="Handwritten notes about shadow mode: Shadow mode: drafts hidden for a week. Pay where a person refers is unsafe. Refer where a person pays is extra work. Agree the go-live rules in advance. Thefts were a rule nobody said. Replay the week to prove the fix." ai="true"}
One page of notes for this chapter.
:::
:::
