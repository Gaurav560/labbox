:::step{type=story title="Everything, by Friday"}
On Wednesday you show Meera the inbox table: photos take 44.6% of the adjusters' email time. She likes it. Then the
requests begin.

"Can Claimdesk also handle car claims? And commercial vehicles? The branch claims are on paper, can it read those? And
the agents' WhatsApp messages?" By the end of the meeting, the project is "every claim, from every channel, for every
vehicle".

That project will not be finished in eight weeks. Worse, it will never be finished well enough to trust, because there
is no way to tell when it is done.

The most important skill an FDE has after discovery is **saying what is in, and what is out**, and turning "make it
better" into a goal that can be measured. In this chapter you choose the pilot's claims from the real data, and write
a goal that can be won or lost.

:::mission
Cut the customer's wish down to a pilot you can finish, and write a goal with a metric, a baseline, a target, a unit
and a date.
:::
:::

:::step{type=concept title="A pilot: small, real, and finishable"}
A **pilot** is a first version used on real work, but only a slice of it, with a fixed end date. It is not a demo
(which can use made-up data) and not the full product (which covers everything). It answers one question for the
customer: does this work here, on our cases, well enough to grow it?

A good pilot slice has three properties:

| Property | Why | Deccan Shield |
|---|---|---|
| Common | big enough that success matters | two-wheeler claims are the most numerous |
| Simple | the inputs are digital and alike | email, not paper or phone |
| Low risk | a mistake costs little while trust is built | Rs 50,000 or less |

Each property removes a reason to fail that has nothing to do with the model: scanning paper, reading WhatsApp, or an
expensive wrong decision in week two.

Why two-wheelers? Look at almost any road in Pune: scooters and motorcycles outnumber everything else, so they are the
largest group of claims at Deccan Shield too (135 of 240 last quarter), and each one is usually a small amount.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-pune-traffic.webp" alt="A busy road in Pune: a cement mixer truck and cars, with several people riding scooters and motorcycles alongside." credit="Ganesh Dhamodkar" license="CC BY 4.0" source="https://commons.wikimedia.org/wiki/File:Mix_of_traffic_on_Pune_roads.jpg"}
Trucks, cars, autos and two-wheelers on Shankarsheth Road, Pune.
:::

Saying no is easier when the no has a reason and a date: "Car claims are in phase two, after the pilot proves the photo
checks work on two-wheelers." People accept "not yet, because" far more easily than "no".

Check yourself: why is "email only" part of the pilot, when branch claims matter too? Branch claims arrive on paper,
which adds a whole scanning problem; email lets the pilot test the idea itself.
:::

:::step{type=example title="Worked example: several conditions on one list"}
This is only to read; it is not in your project. Filtering a list of rows where every condition must hold:

```python
orders = [
    {"city": "Pune", "paid": "yes", "total": "450"},
    {"city": "Pune", "paid": "no", "total": "300"},
    {"city": "Nashik", "paid": "yes", "total": "900"},
    {"city": "Pune", "paid": "yes", "total": "500"},
]
small_pune = [
    o for o in orders
    if o["city"] == "Pune" and o["paid"] == "yes"
    and int(o["total"]) <= 500
]
print([o["total"] for o in small_pune])  # ['450', '500']
```

- A **list comprehension** builds a new list from the rows that pass the test after `if`.
- `and` means every condition must be true. One false condition drops the row.
- CSV values are always **strings**. `"500" <= "60"` compares text, letter by letter, and is wrong for amounts, so
  `int(o["total"])` turns the text into a number first.
- `<= 500` keeps the order for 500 itself; `< 500` would drop it. "Up to 500" and "under 500" are different pilots.
- The order of the rows stays the same, which keeps results easy to compare with the source.
:::

:::step{type=predict title="Guess first"}
:::question
The pilot is "two-wheelers, by email, for Rs 50,000 or less". Of Deccan Shield's 240 claims, 135 are two-wheelers and 71
are two-wheelers sent by email. How many do you expect in the pilot?
:::
- [ ] 135
- [ ] 71
- [x] fewer than 71, because the amount limit removes some
:::explain
Every condition can only remove claims. The amount limit drops the two-wheeler email claims above Rs 50,000. Run it in
the next steps to see the exact number.
:::
:::

:::step{type=try title="An empty pilot"}
```text
$ python scope.py
all claims: 240, in the pilot: 0 (0%)
missing from the goal: nothing
missing from 'make claims faster': []
```

Two problems. The pilot has no claims (`pilot_slice` returns an empty list), and the goal checker says "make claims
faster" is missing nothing, as if a vague wish were a plan. You fix both in this chapter.
:::

:::step{type=task task=pilot_slice title="Your turn: choose the pilot's claims"}
In `pilot_slice` in `scope.py`:

1. Keep a claim only when all three hold: `vehicle` is `"two-wheeler"`, `channel` is `"email"`, and
   `int(amount_rs)` is 50000 or less.
2. Return the kept claims, in the same order.

The check includes a claim of exactly Rs 50,000 (it belongs in the pilot). Press **Check**.
:::

:::step{type=history title="SMART goals"}
:::before{title="Before: goals nobody could check"}
Companies have always set goals. Many of them sounded good and could not be checked: "improve customer service",
"increase efficiency". A year later nobody could say whether they had been met, so nothing was learned.
:::

In November 1981, George T. Doran, a consultant and former director of planning at a power company in Washington, wrote
a short article in the journal *Management Review* called "There's a S.M.A.R.T. way to write management's goals and
objectives". He proposed that a good objective is **Specific, Measurable, Assignable, Realistic and Time-related**.

Over the years, people changed some of the letters (Assignable often became Achievable, Realistic became Relevant), but
the idea stayed: a goal you cannot measure and date is not a goal.

:::solved
A goal written so that, on a known date, anyone can check whether it was met.
:::

:::timeline
- **1981** Doran's "S.M.A.R.T." article appears in Management Review.
- **1990s** SMART goals spread through management training and public sector planning.
- **Today** The same idea appears in AI projects as "success criteria" agreed before a pilot starts.
:::

:::funfact
Doran's article was about one page long. It became one of the most repeated ideas in management.
:::
:::

:::step{type=concept title="A goal you can win or lose" file="03-scoping/scope.py" line="11-17"}
"Make claims faster" cannot fail, so it cannot succeed either. Turn it into five parts:

```python
GOAL = {
    "metric": "days to decide a two-wheeler email claim",
    "baseline": 12.2,
    "target": 5,
    "unit": "days",
    "by": "2026-12-31",
}
```

- **metric**: exactly what is measured, in words everyone agrees on.
- **baseline**: its value today, as a number. We measured it with chapter 1's `days_to_decide` on the 57 pilot claims:
  **12.2 days** (a little faster than the 12.5 days of all claims, as you would expect for small, simple ones).
- **target**: the number that means success.
- **unit**: days, hours, percent. "5" alone could mean anything.
- **by**: the date on which it is checked.

The baseline and target must be **numbers**, not words like "about 12" or "much less", or nobody can compare them later.
Agree this goal in writing with Meera before you build anything. It protects both of you: she knows what she is getting,
and you know when you are done.
:::

:::step{type=task task=measurable_goal title="Your turn: a goal you can win or lose"}
In `missing_parts`:

1. Go through `PARTS` in order.
2. A part is missing when its key is absent from the goal, or its value is empty (`None` or `""`).
3. For `"baseline"` and `"target"`, a value that is not an `int` or `float` also counts as missing. (A baseline of 0 is
   a real number and is **not** missing.)
4. Return the list of missing names, in `PARTS` order.

Press **Check**.
:::

:::step{type=try title="The pilot and its goal"}
```text
$ python scope.py
all claims: 240, in the pilot: 57 (24%)
missing from the goal: nothing
missing from 'make claims faster': ['baseline', 'target', 'unit', 'by']
```

**57 claims**, a quarter of Deccan Shield's volume: small enough to finish, real enough to matter. We also added up the
money: these 57 claims ask for Rs 15,49,000 of the Rs 1,86,90,500 claimed in the quarter, about **8%**. If something
goes wrong early, it goes wrong on the small amounts.

And "make claims faster" is now visibly missing four of five parts, which is exactly what you will tell Meera, kindly,
with the full goal next to it.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Meera asks to add car claims to the pilot. What is the best answer?
:::
- [ ] Yes, it is only one more condition in the code
- [x] Not in the pilot: cars go into phase two once the two-wheeler goal is met, because they add bigger amounts and more checks
- [ ] No, cars are not important
:::explain
The code change is small; the risk is not. A "not yet, because" with a date keeps the pilot finishable and the customer
on your side.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which of these is a goal you can win or lose?
:::
- [ ] Claims will be much faster with AI
- [ ] Reduce claim time as much as possible
- [x] Two-wheeler email claims decided in 5 days or less on average, from 12.2 days, by 31 December 2026
:::explain
Only the third has a metric, a baseline, a target, a unit and a date. On 31 December anyone can check it.
:::
:::

:::step{type=deep-dive title="Go deeper: scope documents in real engagements"}
**The one-page scope.** FDEs usually write a page the customer signs: the problem (with the baseline), what is in, what
is out (and when it might come in), the success criteria, the data and systems needed, and who decides. Writing "out of
scope" down is as important as writing "in scope".

**More than one criterion.** A pilot that is fast but wrong is worse than the old process. Real success criteria pair
speed with quality, for example "and no more than 2% of decisions reversed on review". You will measure quality from
Part 4 on.

**Guardrails on scope.** Agree how changes are handled: a new request is written down, sized, and either swaps with
something in scope or waits for the next phase.

**Exit criteria.** Also agree what happens if the pilot misses its target: stop, change approach, or extend. Deciding
this in advance keeps the end of the pilot calm.
:::

:::step{type=recap}
You can now:

- choose a pilot slice that is common, simple and low risk, from the customer's real data;
- filter records on several conditions, with numbers compared as numbers;
- write a SMART goal with a metric, a baseline, a target, a unit and a date;
- say "not yet, because" to scope that does not fit, and offer a later phase.

That closes Part 1. You know the problem (12.5 days), where the time goes (photos, 44.6%), and what the pilot is (57
two-wheeler email claims, 12.2 days to 5). Next, chapter 4: the customer's real data, which is never as clean as the
export you were given this week.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-03-notes.webp" alt="Handwritten notes about scoping a pilot: A pilot is a small slice of real work. Pick a slice that is common, simple, low risk. Compare amounts as numbers, not text. A goal needs metric, baseline, target, unit, date. Pilot goal: 12.2 days down to 5 days. Say 'not yet, because' to extra scope." ai="true"}
One page of notes for this chapter.
:::
:::
