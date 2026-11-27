:::step{type=story title="\"Can we have it too?\""}
February. Word travels between insurers too. Konkan Mutual, a smaller motor insurer on the coast, has heard about
Claimdesk and wants it. Their head of claims sends a sample: last November's export of ten claims, `data/konkan_claims.csv`.

Open it, and the first surprise is what is **not** there: no emails. Konkan's customers file claims through a web form,
so every claim already arrives as columns:

```text
Claim No,Policy Ref,Vehicle,Loss Date,Cause,Estimate,Photos
KC-1001,KM/26/004512,MH-04-AB-1234,03-11-2026,ACC,"12,500.00",Y
KC-1002,km/26/004519,mh 04 cd 5678,04-11-2026,THF,"28,000.00",Y
```

Konkan does not need a model to read its claims at all. It needs everything **after** the reading: the policy check, the
rules, the reasons, the drafts, the monitoring, the handover. And its rules differ: a lower limit (Rs 30,000), fires
always go to a surveyor as well as thefts, and their policy numbers look like `KM/26/004512`.

This is the moment that decides whether an FDE built a **project** or the beginning of a **product**. A project is
copied and edited for each customer, and after five customers there are five Claimdesks, each with its own bugs. A
product has one core, and a small, separate piece per customer.

:::mission
Split Claimdesk into what every customer shares and what is theirs: an adapter that turns Konkan's export into
Claimdesk's fields, and rules that take their numbers from a per-customer config.
:::
:::

:::step{type=concept title="What was Deccan Shield's, and what is Claimdesk" file="22-second-customer/product.py" line="8-11"}
Go through Claimdesk part by part and ask: "would Konkan need this exactly as it is?"

| Part | Shared, configured, or theirs? | For Konkan |
|---|---|---|
| Reading claims | **theirs**: an adapter per input | Deccan: the model reads emails. Konkan: `from_konkan` reads CSV columns |
| The six fields (`ClaimFields`) | **shared**: the common shape | the same |
| The checks (policy, registration, period, amount) | **shared** | the same code |
| The limit, the always-refer kinds, the policy number format | **configured** | `KONKAN = {...}` |
| Reasons and drafts | **shared** | the same |
| Golden set, evals, smoke test, monitoring | **shared** method, their own cases | Konkan's adjusters write a golden set |
| Theft rule, instruction guard | Deccan's discoveries, now config and shared code | fire joins theft |

The key move is the **common shape**. Everything after reading works on six fields. Deccan Shield's emails reach that
shape through the model; Konkan's CSV reaches it through 10 lines of code. Neither the rules nor anything after them can
tell the difference.

This pattern has a name in software design: an **adapter** (sometimes "ports and adapters") translates an outside format
into the shape the core expects, so the core never changes for a new source.
:::

:::step{type=example title="Worked example: an adapter for a second library"}
This is only to read; it is not in your project. A reminder service built for one library gets a second one, whose
export looks different:

```python
def from_city_library(row):
    due = row["Due"].strip()                       # "21/03/2027"
    return {
        "member_id": row["Card"].strip().upper() or None,
        "due_date": f"{due[6:10]}-{due[3:5]}-{due[0:2]}" if due else None,
        "fine_rs": int(round(float(row["Fine"].replace(",", "")))) if row["Fine"].strip() else None,
        "renewed": row["Renewed"].strip().upper() == "Y",
    }
```

- `.strip().upper() or None` turns an empty column into `None`, because `""` is false.
- Slicing `DD/MM/YYYY` by position and rebuilding it as `YYYY-MM-DD` gives the ISO form the core compares as text.
- `int(round(float(...)))` turns `"1,250.40"` into 1250 after removing the comma.
- Every value ends in the core's type: text or `None`, an int or `None`, a real bool.
:::

:::step{type=predict title="Guess first"}
:::question
Konkan's row KC-1002 has `km/26/004519` and `mh 04 cd 5678`. What should the adapter do with them?
:::
- [ ] Leave them: the customer typed them
- [x] Normalise them to the core's form: `KM/26/004519` and `MH04CD5678`
- [ ] Send the row back to Konkan
:::explain
The checks compare exactly (chapter 14). Adapters normalise at the edge, so the core can stay strict.
:::
:::

:::step{type=try title="Ten claims, all paid"}
With the starter:

```text
$ python product.py
Konkan Mutual: 10 claims from last night's export
   KC-1001 pay    []
   KC-1002 pay    []
   KC-1003 pay    []
...
```

Every claim "pay", including a theft, a fire and one with no policy number. The adapter passes raw text through, and the
rules return no reasons. This is what copying a project to a new customer without thinking looks like.
:::

:::step{type=task task=from_konkan title="Your turn: Konkan's adapter"}
In `from_konkan` in `product.py`, build the six fields from one CSV row:

1. `policy_no`: `Policy Ref` stripped and in capitals, `None` when empty.
2. `vehicle_reg`: `Vehicle` with everything but letters and digits removed (`re.sub(r"[^A-Za-z0-9]", "", ...)`), in
   capitals, `None` when empty.
3. `incident_date`: `Loss Date` from `DD-MM-YYYY` to `YYYY-MM-DD`, `None` when empty.
4. `incident_type`: the `Cause` code looked up in `CODES`, `"other"` when it is not there.
5. `amount_rs`: `Estimate` without commas, rounded to whole rupees as an `int`, `None` when empty.
6. `photos_attached`: `True` only for `"Y"`.

Press **Check**.
:::

:::step{type=concept title="Rules that read their numbers from config" file="22-second-customer/product.py" line="24-30"}
Chapter 13's rules had Deccan Shield inside them: `PILOT_LIMIT_RS = 50000`, and chapter 19 added "theft" by hand. For
two customers, the rules stay the same code and the differences move into a **config**:

```python
DECCAN = {"pilot_limit_rs": 50000, "always_refer": ["theft"],         "policy_pattern": r"DS-POL-\d{5}"}
KONKAN = {"pilot_limit_rs": 30000, "always_refer": ["theft", "fire"], "policy_pattern": r"KM/\d{2}/\d{6}"}
```

`rules(fields, policy, config)` checks, in order:

1. policy number: missing (`"no policy number"`), or not matching `config["policy_pattern"]` with `re.fullmatch`
   (`"policy number not in the expected format"`), or not found (`"unknown policy"`);
2. with a policy: registration and policy period, as in chapter 13;
3. amount: missing, or above `config["pilot_limit_rs"]`;
4. kind: in `config["always_refer"]` gives `f"{kind}: always referred"`.

The format check is new, and it comes from Konkan's data: `KM/26/04577` has five digits where six belong. Looking it up
would find nothing and say "unknown policy", which sends an adjuster looking for a policy that may exist. "Not in the
expected format" tells them it is a typing mistake.

A config is not code. It can be shown to Konkan's head of claims and confirmed line by line: "your limit is 30,000; fire
and theft always go to a person; is that right?" That conversation is much harder to have about an `if` statement.
:::

:::step{type=task task=customer_rules title="Your turn: one set of rules for every customer"}
In `rules`, write the four steps above, taking the limit, the always-refer kinds and the policy pattern from `config`,
and return the reasons in that order.

Press **Check**.
:::

:::step{type=try title="Two customers, one core"}
```text
$ python product.py
Konkan Mutual: 10 claims from last night's export
   KC-1001 pay    []
   KC-1002 refer  ['theft: always referred']
   KC-1003 refer  ['no amount']
   KC-1004 pay    []
   KC-1005 refer  ['fire: always referred']
   KC-1006 refer  ['above the pilot limit']
   KC-1007 refer  ['no policy number']
   KC-1008 refer  ['policy number not in the expected format']
   KC-1009 refer  ['registration does not match the policy']
   KC-1010 refer  ['incident outside the policy period']
Deccan Shield: the golden set's 30 claims, same rules code: {'pay': 17, 'refer': 13}
```

Ten Konkan claims, each with the right reason, and on the last line Deccan Shield's 30 golden claims going through the
**same function** with Deccan's config. Lower-case `km/26/004519` and spaced `mh 04 cd 5678` were normalised by the
adapter before the rules ever saw them.

Konkan's onboarding is now: an adapter, a config, a golden set from their adjusters, a shadow week. Weeks, not months.
:::

:::step{type=history title="A box everyone agreed on"}
:::before{title="Before: every cargo handled its own way"}
Until the 1950s, ships were loaded by hand. Sacks, barrels, crates and loose goods were carried, stacked and tied down
one by one by dock workers. Each kind of cargo needed its own handling, and a ship could spend days in port.
:::

On 26 April 1956 the trucking businessman Malcom McLean sent a converted tanker, the **Ideal X**, from Newark to
Houston with 58 metal trailer boxes on its deck. The boxes went from truck to ship to truck without being opened. By
McLean's own estimate, loading cost fell from about $5.86 a ton by hand to about 16 cents a ton.

The deep change came when the box itself became a standard. In 1968 the International Organization for Standardization
published standard container sizes and corner fittings. From then on, any crane, ship, train or truck built to the
standard could carry any box; the goods inside could be anything.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-containers.webp" alt="Stacks of shipping containers in several colours at a port, with a yellow reach-stacker machine lifting a container onto the top of a stack." credit="Ingolfson" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Container_Stacking,_Port_Of_Onehunga.jpg"}
Standard containers at the Port of Onehunga, New Zealand: the machine does not care what is inside.
:::

Claimdesk's six fields are its container. Emails, CSV exports and, one day, scanned branch forms all get packed into the
same shape at the edge, and everything after that handles them the same way.

:::solved
Agree on one shape in the middle, adapt each source at the edge, and the core never has to change for a new customer.
:::

:::timeline
- **1956** The Ideal X carries 58 containers from Newark to Houston.
- **1968** ISO publishes standard container sizes.
- **Today** Most of the world's manufactured goods travel in standard containers.
:::

:::funfact
McLean started as a truck driver. The idea, he said later, came from waiting a whole day at a port to unload his own
truck, one bale at a time.
:::
:::

:::step{type=concept title="The field report"}
One more deliverable, and it is the one that shapes what happens after you: the **field report**. FDEs work at the edge,
where the product meets real customers, and the report carries what they learned back to the product team.

For Claimdesk it would say:

- **Result against the goal.** The goal agreed in chapter 3, its baseline, and the measured number from the live weeks,
  in the customer's units (days to decide, adjuster hours a week, chapter 1). This is the sentence the next customer
  will believe, so it must be measured, not estimated.
- **What became product.** The common fields, the rules with config, the eval method, the smoke test, the monitoring.
- **What stayed custom, and why.** Deccan Shield's email reading; Konkan's CSV adapter.
- **What the product is missing.** Reading PDF attachments (chapter 20), redacting names (chapter 17), a shared rate
  limiter for many workers (chapter 18). Each with the evidence that it matters.
- **What surprised you.** The model wrote 2023 for dates without a year; a polite injection worked where a loud one did
  not; thefts were a rule nobody said out loud. Surprises are where the product team learns most.

Then you go to the next customer, and it starts again from discovery, a little faster each time.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A third insurer wants Claimdesk, with a limit of Rs 40,000 and floods always referred. What changes?
:::
- [ ] A copy of `rules` with their numbers in it
- [x] A new config, plus an adapter if their claims arrive in a new format
- [ ] Nothing: they must use Deccan Shield's limit
:::explain
The rules are shared code. Their numbers and lists live in their config.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does Konkan not need a language model to read its claims?
:::
- [ ] Konkan cannot afford one
- [x] Its claims already arrive as structured columns; plain code reads them exactly
- [ ] Models cannot read CSV
:::explain
Use a model where the input is free text. Where the data is already structured, code is cheaper, faster and right every
time. Knowing when not to use AI is part of the job.
:::
:::

:::step{type=deep-dive title="Go deeper: from engagements to a product"}
**Config needs checks too.** A config is data from a customer: check it at start-up like chapter 21's settings (is the
limit a positive number, is the pattern a valid regular expression, are the kinds known).

**Version the config.** When Konkan raises its limit, the change is reviewed, dated and logged, like a code change.

**Per-customer golden sets.** Shared code does not mean shared quality. Each customer's adjusters write their own golden
set, and the evals run per customer, so a change that helps one cannot quietly hurt another.

**Resist the third copy.** The first customer is built by hand. The second shows what is common. By the third, anything
still copied is a bug waiting to happen in one place and be fixed in another.
:::

:::step{type=recap}
You can now:

- separate what is customer-specific from what is product, part by part;
- write an adapter that normalises a new source into the core's shape at the edge;
- move rules' numbers and lists into a per-customer config, and add checks a new customer's data reveals;
- write the field report that turns one engagement into product knowledge.

**You have finished the course.** Look at what Claimdesk became: a baseline and a scoped pilot; readers for a messy
export, a database and an old XML system; extraction with a schema, cited answers and tools over MCP; a demo; a golden
set, evals, a regression gate and failure analysis; privacy, reliability, shadow mode and monitoring; a handover; and a
second customer. Every step started from the customer's real problem, and every model output in it was real.

That is the job of a forward deployed engineer.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-22-notes.webp" alt="Handwritten notes about the second customer: One core, an adapter per customer. Six fields are the common shape. Normalise at the edge, stay strict inside. Numbers and lists go in a config. No free text, no model needed. Write the field report." ai="true"}
One page of notes for this chapter.
:::
:::
