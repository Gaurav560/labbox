:::step{type=story title="What the adjusters say, and what the inbox says"}
You now know that a claim takes 12.5 days. Your next question is: **where do those days go?**

You spend Tuesday morning with the adjusters. Everyone has an answer. Sunil says the policy system is slow. Farah says
garages send estimates late. Meera says customers keep asking for status updates. All three are probably true. None of
them tells you which problem to solve first.

So you ask for something else: a sample of real work. The team lead exports 40 emails from the claims inbox, and next
to each one an adjuster writes down roughly how many minutes it took to deal with. It is in your project as
`data/inbox_sample.csv`.

This is **discovery**: finding out how the work is really done, from the work itself, before deciding what to build.
In this chapter you sort those 40 emails and find what costs the most time. The answer is not the one anyone said.

:::mission
Sort a sample of the customer's real work into kinds, then find the kind that costs the most time, not the one that
shows up the most.
:::
:::

:::step{type=concept title="Discovery: go and see the work"}
An FDE's first weeks are mostly listening and looking. **Discovery** has three sources, and you need all three:

| Source | What it gives you | Its weakness |
|---|---|---|
| Interviews | people's goals, pains and words | memory is selective; people describe the work as it should be |
| Watching the work | the real steps, the workarounds, the copy-pasting | slow, and you see only a few cases |
| The data | how often each thing happens, and how long it takes | it says what, never why |

The interviews told you three stories. The data will tell you how big each story is. Together they tell you where to
start.

Discovery is not only for the start. Every time something surprising happens later (a demo goes badly, a number moves),
you go back to the work and look again.

Check yourself: if three adjusters each name a different biggest problem, what settles it? The work itself: counting
what really happens, with the time it takes.
:::

:::step{type=history title="Go and see, and the vital few"}
:::before{title="Before: deciding from the office"}
In factories of the early twentieth century, improvements were usually designed by managers and engineers away from
the floor, from reports. Problems that were obvious to workers often never reached the people deciding what to change.
:::

Two ideas from manufacturing are the roots of good discovery.

**Go and see.** At Toyota, the engineer Taiichi Ohno built the Toyota Production System in the decades after the Second
World War. One of its rules is known as **genchi genbutsu**, roughly "the real place, the real thing": to understand a
problem, go to where the work happens and look at it yourself, instead of reading a report about it.

This is Taiichi Ohno, the Toyota engineer behind that rule. He was known for drawing a chalk circle on the factory floor
and asking a manager to stand in it for hours, just watching the work, until they saw the problem for themselves. An
FDE sitting with the adjusters is standing in Ohno's circle.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-ohno.webp" alt="A black and white portrait of a man with short dark hair and a small moustache, in a suit and tie." credit="Toyota Motor Co., company history editorial committee" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Ohno-Taiichi-1.jpg"}
Taiichi Ohno (1912 to 1990), who built the Toyota Production System.
:::

**The vital few.** In 1896 the Italian economist Vilfredo Pareto observed that a small share of the people in Italy
owned a large share of the land. Decades later, the quality engineer Joseph Juran noticed the same shape in defects: a
few causes produced most of the problems. He called them "the vital few and the trivial many", and named the idea after
Pareto. Today it is called the **Pareto principle**, often stated as "80% of the effects come from 20% of the causes"
(the exact numbers vary; the shape is what matters).

:::solved
Look at the real work, count the causes, and fix the few that matter most first.
:::

:::timeline
- **1896** Pareto describes the uneven spread of land ownership in Italy.
- **1950s** Toyota develops the production system that includes "go and see".
- **1951** Juran's Quality Control Handbook spreads "the vital few and the trivial many" in quality management.
:::

:::funfact
In 1975 Juran published an article called "The Non-Pareto Principle; Mea Culpa", admitting that Pareto had only
studied wealth, and that the general principle was Juran's own idea with Pareto's name on it. The name stuck anyway.
:::
:::

:::step{type=concept title="Sorting emails with rules" file="02-discovery/discovery.py" line="14-20"}
To count kinds of work, each email needs a **kind**. You and the team agreed five kinds after reading the sample:

| Kind | What the email is about |
|---|---|
| `photos` | a photo was asked for, sent, resent or argued about |
| `status` | "where is my claim?" |
| `new_claim` | a new accident, theft or damage |
| `documents` | the RC book, licence, invoice, estimate, PAN card |
| `complaint` | an escalation or an unhappy customer |

Anything else is `other`.

You could ask a model to sort them. Not yet. For 40 emails, a few **keyword rules** are faster to write, free to run,
and easy to explain to Meera. If simple rules give a clear answer, you have learned something cheaply. If they do not,
you have learned where the hard part is.

A rule here is a test like "does the text contain the word `photo`?". Two details decide whether rules work:

1. **Look everywhere, in one case.** Join the subject and the body, and lower-case the result once, so "PHOTO", "Photo"
   and "photo" all match.
2. **Order matters.** A photo email often also says "attached". If the documents rule ran first, it would grab the photo
   email. So the rules run in a fixed order, and the first match wins.
:::

:::step{type=example title="Worked example: first match wins"}
This is only to read; it is not in your project. A tiny classifier for a garage's messages:

```python
def kind(message):
    text = message.lower()
    if "brake" in text:
        return "brakes"
    if "tyre" in text or "puncture" in text:
        return "tyres"
    return "other"

print(kind("Brake noise and a PUNCTURE"))  # brakes
print(kind("Puncture near Swargate"))      # tyres
print(kind("Car wash please"))             # other
```

- `message.lower()` happens once, at the top; every test then compares lower-case words.
- `"brake" in text` asks whether that word appears anywhere in the text.
- The first message mentions both brakes and a puncture. Brakes come first in the code, so it is `brakes`. Put the
  most important or most specific kinds first.
- Each `return` ends the function, so later rules never run once one has matched.
:::

:::step{type=predict title="Guess first"}
:::question
The rules test `"rc"` for documents (the RC book is a vehicle's registration certificate). The email "New claim: auto
rickshaw ... Commercial policy DS-POL-90021" contains the letters "rc" inside "Commercial". What kind does it get?
:::
- [ ] documents, because "rc" matches
- [x] new_claim, because the new claim rule runs before the documents rule
- [ ] other
:::explain
`"rc" in text` matches inside "commercial", so on its own the documents rule would be wrong. The order saves it: "new
claim" is tested first and wins. Short keywords match inside other words; keep them late in the order, or match them
with spaces around them.
:::
:::

:::step{type=try title="The inbox, unsorted"}
Run the report before writing the rules:

```text
$ python discovery.py
kind        emails  minutes
photos           0        0
status           0        0
new_claim        0        0
documents        0        0
complaint        0        0
other           40      464
costliest: ('', 0.0)
```

All 40 emails are `other`, and together they took **464 minutes**: almost 8 hours of adjuster time for 40 emails. That
total is real; the sorting is what you add.
:::

:::step{type=task task=classify_email title="Your turn: sort the inbox by what each email is about"}
In `classify` in `discovery.py`:

1. Join `email["subject"]` and `email["body"]` with a space, and lower-case the result.
2. Test the kinds in the order of the TODO, returning at the first match:
   `photos`, then `status`, then `new_claim`, then `documents`, then `complaint`.
3. Return `"other"` when nothing matched.

The check tries a photo email that also says "attached", a new claim with an attachment, and a polite email that is
none of the kinds. Press **Check**.
:::

:::step{type=concept title="Count is not cost" file="02-discovery/discovery.py" line="32-36"}
With every email sorted, the obvious question is "which kind is most common?". It is the wrong question.

What Meera wants back is her team's **time**. A status email ("where is my claim?") takes an adjuster two or three
minutes: look it up, reply. A photo email can take twenty: open the attachment, compare it with what the surveyor
needed, find it is the wrong angle, write back explaining which photo, and wait. Five quick emails cost less than one
slow one.

So the question becomes: **which kind costs the most minutes?** `minutes_by_kind` (already written, lines 23 to 29)
adds up the minutes for each kind. `costliest` picks the kind with the largest total, and says what share of all the
minutes it is:

```python
minutes = minutes_by_kind(emails)
kind = max(minutes, key=minutes.get)
```

`max(..., key=minutes.get)` returns the **key** whose value is largest: the kind, not the number.

The share is that kind's minutes divided by all minutes, times 100. A share is easier to say in a meeting than a raw
count: "this one kind is almost half of the inbox work".
:::

:::step{type=task task=costliest_kind title="Your turn: find what eats the adjusters' time"}
In `costliest`:

1. Call `minutes_by_kind(emails)`.
2. Find the kind with the most minutes (not the most emails).
3. Return `(kind, share)`, where share is its minutes / the sum of all minutes x 100, rounded to 1 decimal place.

Press **Check**.
:::

:::step{type=try title="The real shape of the inbox"}
```text
$ python discovery.py
kind        emails  minutes
photos          12      207
status           9       24
new_claim        7      136
documents        5       27
complaint        4       55
other            3       15
costliest: ('photos', 44.6)
```

Read it slowly, because this table changes the project:

- **Status** emails are many (9) but cheap: **24 minutes** in total. Meera's guess was the most common kind, not the
  costliest.
- **Photos** are 12 emails and **207 minutes: 44.6%** of all the time, nearly half. Wrong photos, missing photos, photos
  that need explaining.
- **New claims** take long each (136 minutes for 7), but they are the actual work of an insurer; you will help with them
  later, not remove them.

And look at the three `other` emails: "When will I get the money?", "Which documents?", "Any news on my claim?". The
last is clearly a status question that no keyword caught. Rules handle the phrasings someone thought of; real people
write in many more. Remember this when Part 3 brings in a model.

Now you can say something useful on Wednesday: "Nearly half the inbox time goes on photos. If Claimdesk checks a claim's
photos and asks for exactly the missing one, the first time, we attack the largest pile first."
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Status emails are 9 of 40, photo emails 12 of 40, but photos take 207 minutes and status 24. Which should the pilot
attack first?
:::
- [ ] Status, because customers ask about it so often
- [x] Photos, because they cost by far the most adjuster time
- [ ] Both equally
:::explain
Rank by cost, not by count. A cheap, frequent task is worth automating later; the pile that eats nearly half the time
is where the first weeks pay back.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why sort the emails with keyword rules before trying a model?
:::
- [x] For a 40-email sample, rules are quick, free and easy to explain, and they show where the hard cases are
- [ ] Models cannot read emails
- [ ] Rules are always more accurate than models
:::explain
Rules are the cheap first instrument. Where they fail (like "Any news on my claim?") is exactly where a model may earn its
cost, and now you have examples to test it on.
:::
:::

:::step{type=deep-dive title="Go deeper: discovery in real engagements"}
**Shadowing.** Sit next to an adjuster for half a day with their permission, and write down every step and every switch
between programs. The workarounds (a personal spreadsheet, a WhatsApp group with garages) are often where the real
process lives.

**Sample size.** 40 emails is enough to see a shape, not to quote a precise percentage to a board. Before the business
case, get a larger sample (a month of the inbox) and check that the shape holds.

**Write it down the same day.** FDEs keep a short discovery log: who said what, which numbers came from data and which
from memory, and open questions. It becomes the scope document of chapter 3 and the handover of chapter 21.

**The customer's words.** Note the words people use ("survey photos", "RC copy"). Your prompts, labels and screens will
read better in their language than in yours.
:::

:::step{type=recap}
You can now:

- run discovery from interviews, observation and data, and know what each one misses;
- sort a sample of real work with ordered keyword rules, and see where rules fall short;
- rank problems by the time they cost, not by how often they appear;
- tell the customer where the time goes, as a share they can repeat in a meeting.

Next, chapter 3: scoping. Photos are the biggest pile. Now decide exactly which claims the pilot handles, and write a
goal that can be won or lost.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-02-notes.webp" alt="Handwritten notes about discovery: Discovery means looking at the real work. Interviews, watching and data each miss something. Sort the work into kinds, then count. Rank problems by time, not by count. Photo emails took 44.6% of the time. Rules miss the phrasings people really use." ai="true"}
One page of notes for this chapter.
:::
:::
