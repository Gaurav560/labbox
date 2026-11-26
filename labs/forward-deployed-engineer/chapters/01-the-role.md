:::step{type=story title="Monday, 9 a.m., at someone else's office"}
It is your first Monday at **Deccan Shield Insurance**, a motor insurer with a claims office in Pune. You do not work
for Deccan Shield. You work for the company that sold them an AI platform, and for the next eight weeks your desk is
here, next to the people who will use what you build.

The head of claims, Meera Kulkarni, puts it simply: "Motor claims are too slow. Customers are angry. Can your AI fix
it?" Then she goes to her next meeting.

That sentence is not a task. Nobody can build "fix it". Before you write a line of AI code, you need to know three
things: how slow is "too slow", in numbers; what the slowness costs; and which part of it you can change in eight
weeks. This chapter does the first two, with Deccan Shield's own data.

This is the daily work of a **forward deployed engineer**: an engineer who goes to the customer, turns a vague wish
into a measured problem, builds the solution inside the customer's world, and stays until it works in production.
By the end of this course you will have done every part of that job once, on one realistic engagement.

:::mission
Measure the problem in the customer's own numbers: how many days a claim takes today, and how many hours of
adjusters' time it costs each week.
:::
:::

:::step{type=concept title="What a forward deployed engineer is"}
Most software engineers build a product once, for many customers. They rarely meet those customers. A product team
asks "what do most customers need?" and builds that.

A **forward deployed engineer** (FDE) works the other way round. They work for the company that makes a product, but
they spend their time **inside one customer's organisation**, with that customer's people, data and systems, often for
a few months. Their job is to make the product succeed **there**: connect it to the customer's data, build the missing
pieces, prove it works, and get it into real daily use.

A common way to put the difference: a product engineer builds one capability for many customers; a forward deployed
engineer builds many capabilities for one customer.

The word **deployed** is meant literally. The OpenAI job posting for an FDE in New York says the engineer will "own
discovery, technical scoping, system design, build, and production rollout" with strategic customers, and that
"travel up to 50% is required". Anthropic's postings describe FDEs who "embed directly" with customers to build
production applications with Claude, and who deliver things like MCP servers, sub-agents and agent skills (you will
build an MCP server in chapter 12).

So the job has two halves, and you need both:

| Half | What it means | In this course |
|---|---|---|
| Engineer | real code that runs in production: data, models, APIs, tests, monitoring | every chapter has two coding tasks |
| Deployed | working where the customer is: their language, their constraints, their numbers | every chapter starts from Deccan Shield's real problem |

Check yourself: if Meera asked a product engineer and an FDE the same question, which one would start by reading
Deccan Shield's claim data? The FDE: the product engineer would ask what most insurers need.
:::

:::step{type=history title="The story of the forward deployed engineer"}
:::before{title="Before: software that arrived in a box"}
For most of the history of business software, a company bought a product, and its own IT team (or an outside
consultancy) installed and adapted it. The vendor's engineers stayed at headquarters. When the product did not fit the
customer's data or way of working, the problem travelled through a chain of people: the customer told the account
manager, who told a product manager, who wrote a ticket, which an engineer read months later. Much was lost on the way.
:::

The idea of sending the vendor's own engineers to sit with the customer was made famous by **Palantir Technologies**,
a data analysis company founded in 2003, which put engineers at the sites of the government agencies and companies it
worked for and gave them this title. The phrase **forward deployed** comes from military vocabulary: forces stationed
close to where they are needed, rather than at a home base.

The US Navy, for example, keeps some ships permanently based far from home, so they are already in the region when
they are needed. This ship, the USS Blue Ridge, is arriving at what the Navy calls its "forward deployed operating base"
in Yokosuka, Japan: not visiting, but living where the work is. That is exactly the idea behind the engineer's title.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-blue-ridge.webp" alt="A large grey navy ship, number 19 on its bow, being guided by a small tug into a harbour, with cranes and coiled wire in the foreground." credit="U.S. Navy photo by Photographer's Mate 2nd Class John L. Beeman" license="Public domain" source="https://commons.wikimedia.org/wiki/File:US_Navy_060324-N-9851B-001_Amphibious_command_and_control_ship_USS_Blue_Ridge_(LCC_19)_pulls_into_her_forward_deployed_operating_base,_Commander_Fleet_Activities_Yokosuka,_Japan.jpg"}
The USS Blue Ridge pulls into its forward deployed operating base in Yokosuka, Japan, 24 March 2006.
:::

For years the title belonged mostly to Palantir. Then large language models arrived, and every company that wanted to
use them hit the same wall: a model is general, and a business is specific. Someone has to connect the general model
to the specific claims, contracts, tickets and databases, and prove that the result is right often enough to trust.

:::solved
FDEs close the distance between the product and the customer: the person who understands the customer's problem is the
same person who can change the code, so a fix takes days, not a quarter.
:::

:::timeline
- **2000s** Palantir puts engineers at customer sites and makes the title "forward deployed engineer" well known.
- **4 June 2025** Joe Schmidt of the venture firm a16z publishes "Trading Margin for Moat: Why the Forward Deployed Engineer Is the Hottest Job in Startups".
- **13 October 2025** The Wall Street Journal: "AI Startups Have a New (Old) Secret Weapon: Forward Deployed Engineers".
- **2026** OpenAI, Anthropic, AWS, Microsoft and Google Cloud announce teams built around forward deployed engineering.
:::

:::usedby{title="Who hires FDEs"}
- AI model companies (OpenAI, Anthropic), to put their models into production at large customers
- AI application startups, whose products need deep connection to each customer's data
- Data and analytics companies (Palantir, where the title began)
- Cloud providers, for their biggest AI customers
:::

:::funfact
The a16z article explains why startups accept the cost. FDE work lowers a company's profit margin at first (people are
expensive, software copies are not), but a product wired deep into a customer's daily work is very hard to replace.
The title says it: trading margin for a moat.
:::
:::

:::step{type=concept title="A typical engagement, start to finish"}
Every FDE engagement is different in its details and alike in its shape. This course follows that shape, in six
parts, at Deccan Shield:

| Part | The FDE's question | What you build |
|---|---|---|
| 1. The role | What is the real problem, and how big is it? | a baseline, a discovery count, a pilot scope |
| 2. The customer's data | What does their data really look like? | readers for messy exports, SQL, an old system, a data contract |
| 3. Building with models | Can a model do the work, on their data? | extraction, cited answers, tools, an MCP server, a demo |
| 4. Proving it works | Is it right often enough to trust? | a golden set, evals, a failure analysis |
| 5. Production | Can it run every day, safely? | privacy, fallbacks, shadow mode, monitoring |
| 6. Leaving it better | Can they run it without you? | a handover with a CI gate, and the next customer |

The product you build is **Claimdesk**: an assistant that reads a claim email, pulls the customer's policy from Deccan
Shield's systems, and drafts a decision for a human adjuster to approve. An **adjuster** is the person at an insurer who
checks a claim and decides whether, and how much, to pay.

Notice the order. Models arrive in Part 3, not in chapter 1. An FDE who opens a chat with the model on day one usually
builds an impressive demo of the wrong thing.
:::

:::step{type=concept title="A baseline: the number before you change anything" file="01-the-role/baseline.py" line="15-25"}
A **baseline** is the measurement of how things are today, before you change anything. Without it, nobody can say
whether your work helped. "Claims feel faster now" is an opinion; "claims went from 12.5 days to 5 days" is a result.

Deccan Shield's IT team sent you an export of every motor claim from July to September 2026. It is in your project as
`data/claims_2026_q3.csv`. The first lines look like this:

```text
claim_id,received_at,decided_at,vehicle,amount_rs,channel,status
DS-26-10038,2026-07-02 12:45,2026-07-10 07:32,two-wheeler,34500,email,approved
DS-26-10011,2026-07-02 17:00,2026-07-18 17:47,commercial,337500,email,approved
DS-26-10097,2026-07-04 17:00,2026-07-19 14:37,two-wheeler,21500,email,rejected
```

Each row is one claim: when it arrived (`received_at`), when an adjuster decided it (`decided_at`), the kind of
vehicle, the amount claimed in rupees, how it came in (by email, at a branch, or through an agent), and the outcome.

The question "how slow is too slow?" becomes a calculation: for each decided claim, the time from `received_at` to
`decided_at`; then the average of those times.

Two things to notice before you write it:

1. Some claims are **still open**: their `decided_at` is empty. An open claim has no "days to decide" yet. It must be
   left out of the average, not counted as zero days (that would make the insurer look faster than it is).
2. The times have hours and minutes. A claim decided 12 hours after it arrived took half a day, not zero days.
:::

:::step{type=example title="Worked example: time between two moments in Python"}
This is only to read; it is not in your project. Python's `datetime` turns text into a moment in time, and subtracting
two moments gives a **timedelta**, a length of time:

```python
from datetime import datetime

FMT = "%Y-%m-%d %H:%M"
start = datetime.strptime("2026-08-03 10:00", FMT)
end = datetime.strptime("2026-08-03 22:00", FMT)
gap = end - start
print(gap)                         # 12:00:00
print(gap.days)                    # 0
print(gap.total_seconds() / 86400) # 0.5
```

Line by line:

- `FMT` describes the text's shape: `%Y` a four-digit year, `%m` the month, `%d` the day, `%H:%M` hours and minutes.
- `strptime` (string, parse, time) reads the text with that shape and returns a `datetime`.
- `end - start` is a `timedelta` of 12 hours.
- `gap.days` is **0**: it counts only whole days and drops the hours. This is the most common mistake here.
- `gap.total_seconds() / 86400` is **0.5**: a day has 86,400 seconds, so this gives days with the fraction kept.

To average only some values, filter first:

```python
values = [2.0, None, 0.5]
known = [v for v in values if v is not None]
print(round(sum(known) / len(known), 1))  # 1.2
```

(The average is 1.25. Python rounds a number exactly halfway to the nearest even digit, so it prints 1.2.)
:::

:::step{type=predict title="Guess first"}
:::question
A claim arrived on 3 August at 10:00 and was decided on 5 August at 09:00. What does `(decided - received).days` give?
:::
- [ ] 2
- [x] 1
- [ ] 1.96
:::explain
The gap is 1 day and 23 hours. `.days` keeps only the whole days, so it gives 1, and the 23 hours are lost.
`total_seconds() / 86400` gives about 1.96. For a baseline, the fraction matters: it is almost two days.
:::
:::

:::step{type=try title="Run the baseline before writing it"}
Open a terminal and run the report as it is now:

```text
$ python baseline.py
claims in the export: 240
average days to decide: 0.0
adjuster hours a week: 0.0
```

240 claims, and an average of 0.0 days. That is the starter's placeholder: `baseline_days` returns 0.0 until you write
it. If you showed Meera this number, you would promise her a miracle that already happened. Wrong numbers are worse
than no numbers.
:::

:::step{type=task task=baseline_days title="Your turn: how long a claim takes today"}
In `baseline.py`:

1. In `days_to_decide`, return `None` when `claim["decided_at"]` is empty.
2. Otherwise parse `received_at` and `decided_at` with `datetime.strptime(..., FMT)` and return the difference in
   days, with the fraction: `total_seconds() / 86400`.
3. In `baseline_days`, call `days_to_decide` for every claim, keep the values that are not `None`, and return their
   average rounded to 1 decimal place.

The check tries an open claim, a two-day claim and a half-day claim before your real data. Press **Check**.
:::

:::step{type=concept title="What the slowness costs" file="01-the-role/baseline.py" line="28-32"}
Days are what the **customer's customers** feel: the person waiting for their scooter repair money. Meera also feels
something else: her team's time. Every claim needs an adjuster to read it, chase missing photos, check the policy and
decide.

In your first meeting, the adjusters estimated **35 minutes of work per claim**, spread over the days it is open. That
number came from people, not data, so you write it down as an assumption and use it as an argument with a default, so
it is easy to change when you learn better:

```python
def adjuster_hours(claims, minutes_per_claim=35, weeks=13):
```

The export covers 13 weeks (1 July to 29 September). The arithmetic:

- claims per week = all claims / 13;
- minutes per week = claims per week x 35;
- hours per week = minutes / 60.

Why turn time into hours of work? Because that is how a business decides. "Claims take 12.5 days" is a complaint.
"Claims cost 10.8 adjuster hours every week, and a quarter of them could be halved" is a budget line. An FDE speaks
both languages: days for the customer's customers, hours (and later, rupees) for the customer.

Careful: the most common slip is forgetting the weeks and reporting the hours for the whole quarter. Always say the
unit: hours **a week**.
:::

:::step{type=task task=adjuster_hours title="Your turn: what the problem costs each week"}
In `adjuster_hours`:

1. Work out claims per week: `len(claims) / weeks`.
2. Multiply by `minutes_per_claim`, divide by 60, and round to 1 decimal place.
3. Use the arguments, not the numbers 35 and 13: the check calls it with other values too.

Then run `python baseline.py` again and read both lines aloud as a sentence you could say to Meera. Press **Check**.
:::

:::step{type=try title="The baseline, finished"}
With both tasks done:

```text
$ python baseline.py
claims in the export: 240
average days to decide: 12.5
adjuster hours a week: 10.8
```

**12.5 days** to decide a motor claim, and **10.8 hours** of adjuster time every week. These two numbers are the
yardstick for everything in this course.

We looked a little further into the same data. 11 claims are still open. Of the 229 decided ones, the fastest took
4.0 days and the slowest 24.0; the middle claim (the **median**) took 11.8 days; 89 claims took more than two weeks.
The average hides a long tail: for 89 families, "too slow" meant more than 14 days. That is worth a line in your
first report too.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the baseline leave out the 11 open claims instead of counting them as 0 days?
:::
- [ ] Open claims are not important
- [x] An open claim has no decision time yet; counting it as 0 would make the insurer look faster than it is
- [ ] Python cannot subtract an empty string
:::explain
A baseline must be honest. Zeros would pull the average down and flatter the current process. (Later, open claims get
a measure of their own: how long they have been waiting so far.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Meera says, "Make claims faster." What is the first thing a forward deployed engineer does?
:::
- [ ] Build a chatbot demo on the model
- [x] Measure how long claims take today, in Deccan Shield's own data
- [ ] Ask the product team what most insurers want
:::explain
A baseline in the customer's own numbers turns a wish into a problem with a size. Every decision that follows (what to
build, what to leave out, whether it worked) is measured against it.
:::
:::

:::step{type=deep-dive title="Go deeper: what real FDEs measure"}
**Several baselines, not one.** Real engagements measure speed (days to decide), effort (hours per claim), quality
(how often a decision is later reversed) and experience (complaints). Improving one at the cost of another is easy;
an FDE reports all of them.

**Medians and percentiles.** An average is pulled by the slowest claims. Teams usually report the median and the
**95th percentile** too (the time within which 95 of 100 claims are decided). You will compute percentiles for real
in chapter 20.

**Assumptions are part of the deliverable.** "35 minutes per claim" came from a conversation. Write such numbers down,
with who said them and when, and replace them with measurements when you can (Part 5 logs real handling times).

**Money.** Hours become rupees with a cost per hour. FDEs are often asked for the return on investment of the whole
engagement; chapter 22 writes that report.
:::

:::step{type=recap}
You can now:

- explain what a forward deployed engineer does, and how it differs from product engineering;
- tell the short history of the role, from Palantir to the AI companies of 2025 and 2026;
- compute a baseline from a customer's export, leaving open cases out honestly;
- turn a slow process into hours of people's work a week, and say the unit.

Next, chapter 2: discovery. 12.5 days is the size of the problem. Now find out what, inside those days, actually eats
the time.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-01-notes.webp" alt="Handwritten notes about the forward deployed engineer and the baseline: An FDE builds inside one customer's world. Measure the problem before building. A baseline is how things are today. Leave open claims out of the average. Claims took 12.5 days on average. Always say the unit: hours a week." ai="true"}
One page of notes for this chapter.
:::
:::
