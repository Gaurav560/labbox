:::step{type=story title="Friday, 4 p.m., the demo"}
Meera has booked thirty minutes on Friday afternoon. In the room: herself, two senior adjusters, Priya from IT, and the
head of finance. They do not want slides. They want to see a real claim go in and something useful come out.

You have every piece: extraction (chapter 9), the policy database (chapter 5), exact checks in code (chapters 11 and
12), the pilot limit (chapter 3). The demo puts them behind one web endpoint, `POST /triage`: a claim email goes in, and
a **draft** comes out for the adjuster: `pay` when nothing needs a human, `refer` with the reasons when something does.

Two rules for a demo that builds trust instead of losing it:

1. **Real cases, including the hard ones.** Show a clean claim, and show the claims that must be referred, with the
   reason in plain words. A demo that only shows the happy path makes experienced adjusters suspicious, and they are
   right to be.
2. **Nothing decides alone yet.** It drafts; the adjuster decides. Say so in the first minute.

:::mission
Build the triage endpoint that combines extraction, the policy and the pilot's rules into a draft with reasons, and
guard it against junk input before it costs anything.
:::
:::

:::step{type=concept title="The model reads, code decides" file="13-day-five-demo/app.py" line="33-43"}
Look at how the work is divided inside `/triage`:

| Step | Who does it | Why |
|---|---|---|
| Read the six fields from the email | the model (`safe_extract`) | free text is what models are good at |
| Find the policy | code (`get_policy`, SQL) | exact lookup |
| Does the registration match? | code | exact comparison |
| Is the incident inside the policy period? | code | chapter 11 showed a model getting this wrong |
| Is there an amount, and is it within the pilot limit? | code | a rule agreed in writing (chapter 3) |
| Pay or refer | code, from the reasons | the same claim always gets the same draft |

The model touches the claim exactly once, to read it. Everything that decides is ordinary code you can test, read aloud to
an auditor, and change when the rules change.

The **reasons** list is the heart of it. Each check that fails adds a sentence an adjuster understands:

- `"no policy number"` or `"unknown policy"`;
- `"registration does not match the policy"`;
- `"incident outside the policy period"`;
- `"no amount"` or `"above the pilot limit"`.

No reasons: draft `pay`. Any reason: draft `refer`, with every reason listed, not just the first. And if the email cannot
be read at all, `refer` with `"could not read the email: ..."`.
:::

:::step{type=example title="Worked example: rules that collect reasons"}
This is only to read; it is not in your project. Checking a library loan the same way:

```python
def check_loan(member, book):
    reasons = []
    if member is None:
        reasons.append("unknown member")
    elif member["fines_rs"] > 100:
        reasons.append("unpaid fines")
    if book["on_loan"]:
        reasons.append("already on loan")
    return {"decision": "lend" if not reasons else "ask librarian",
            "reasons": reasons}

print(check_loan({"fines_rs": 250}, {"on_loan": True}))
# {'decision': 'ask librarian', 'reasons': ['unpaid fines', 'already on loan']}
```

- Each rule **appends** instead of returning early, so the librarian sees every problem at once.
- `elif` is used only where a rule depends on the one before (no member, no fines to check).
- The decision is computed from the reasons at the end, in one line, so it can never disagree with them.
:::

:::step{type=predict title="Guess first"}
:::question
E-24's email asks about policy DS-POL-40370 for car MH14HJ5656, with a new estimate of Rs 61,000. In the database,
DS-POL-40370 belongs to MH14PQ8899. Which reasons should the draft give?
:::
- [ ] None, the policy exists
- [x] "registration does not match the policy" and "above the pilot limit"
- [ ] Only "above the pilot limit"
:::explain
Two independent problems, so two reasons. The registration mismatch may be a typing mistake or something worse; either
way a person must look.
:::
:::

:::step{type=try title="A demo that always says refer"}
Start the service in one terminal:

```text
$ uvicorn app:app --port 8000
```

and in another, send the sample claim (E-01, a clean one):

```text
$ curl -s localhost:8000/triage -H 'content-type: application/json' -d @data/sample.json
{"draft":"refer","reasons":["not written yet"]}
```

Now send a one-word "email":

```text
$ curl -s -w ' (HTTP %{http_code})' localhost:8000/triage -H 'content-type: application/json' -d '{"email": "help"}'
{"draft":"refer","reasons":["not written yet"]} (HTTP 200)
```

The endpoint accepted "help" as if it were a claim. Once triage calls the model, every such request would cost a model call
for nothing.
:::

:::step{type=task task=triage_endpoint title="Your turn: the triage endpoint"}
In `triage` in `app.py`, following the TODO:

1. `fields, problem = safe_extract(body.email)`. If `problem` is not `None`, return
   `{"draft": "refer", "reasons": ["could not read the email: " + problem]}`.
2. Build `reasons` in this order: no policy number, or an unknown policy; then (when there is a policy) a registration
   that differs, and an incident date outside `start_date`..`end_date`; then no amount, or an amount above `PILOT_LIMIT_RS`.
3. Return `{"draft": "pay" if not reasons else "refer", "reasons": reasons, "fields": fields.model_dump()}`.

The check runs a clean claim, E-24's two problems, a claim after its policy ended, a claim with no policy and no amount,
an unknown policy, and an unreadable answer. Press **Check**.
:::

:::step{type=concept title="Guard the door before the model" file="13-day-five-demo/app.py" line="27-30"}
Every request that reaches `safe_extract` costs a model call. A request with an empty email, a single word, or someone
pasting a 50-page PDF as text should never get that far.

FastAPI checks request bodies with the pydantic model you declare, before your function runs. Give the field limits:

```python
class TriageIn(BaseModel):
    email: str = Field(min_length=20, max_length=8000)
```

- Shorter than 20 characters: not a claim email (even "Scooter stolen DS-POL-40000" is longer).
- Longer than 8,000 characters (about 2,000 tokens): far beyond any real claim email; probably a paste, or an attack.

When the body breaks the limits, FastAPI answers **422 Unprocessable Content** with the reason, and `triage` never runs.
This is the cheapest guard you will ever write: it costs nothing and stops waste and abuse before the first token.
:::

:::step{type=task task=input_guard title="Your turn: guard the door"}
In `class TriageIn`, give `email` the limits: `Field(min_length=20, max_length=8000)`.

The check sends an empty email, "help", and 8,001 characters (all must be refused with 422, and none may reach the
model), and exactly 8,000 characters (allowed). Press **Check**.
:::

:::step{type=history title="Demo or die"}
:::before{title="Before: papers nobody tried"}
For a long time, computing research was judged mostly by papers. An idea could sound convincing on paper and never meet
a real user.
:::

At the **MIT Media Lab**, founded in 1985 by Nicholas Negroponte and Jerome Wiesner, the working motto became **"Demo or
Die"**: an idea counted when it ran in front of people. Visitors, sponsors and students judged what they could see and
try, and the hard questions came from watching it work, or fail.

This is the lab's building in Cambridge, Massachusetts, with its newer extension under construction on the right. Most
of what was invented inside was judged by one test: does it work when someone walks up and tries it?

:::photo{src="/lesson-images/forward-deployed-engineer/fde-media-lab.webp" alt="A long white building with bands of windows on a street corner, and a newer glass and yellow building being built beside it." credit="Madcoverboy" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:MIT_Media_Lab.jpg"}
The MIT Media Lab, with its expansion under construction.
:::

FDE teams live by a version of the same rule: early, honest, working demos on the customer's own data, every week or two,
instead of a big reveal at the end. The web framework you are using for it, **FastAPI**, was created by Sebastián Ramírez
and first released in December 2018. It builds on pydantic (chapter 7), which is why the request limits in this chapter
are one line.

:::solved
Show working software on real cases early, so the customer's questions shape what is built next.
:::

:::timeline
- **1985** The MIT Media Lab opens; "Demo or Die" becomes its motto.
- **December 2018** FastAPI's first release.
- **Today** FDE teams demo on customer data every week or two.
:::

:::funfact
Joi Ito, the lab's director from 2011, proposed changing the motto to "Deploy or Die": building it so people use it every
day is the real test. That is what the rest of this course is about.
:::
:::

:::step{type=try title="The demo, for real"}
Through the gateway, with the real model, the claims from the meeting:

```text
$ curl -s localhost:8000/health
{"ok":true}
$ curl -s localhost:8000/triage -H 'content-type: application/json' -d @data/sample.json
{"draft":"pay","reasons":[],"fields":{"policy_no":"DS-POL-40000","vehicle_reg":"MH12AB1234","incident_date":"2026-10-03","incident_type":"accident","amount_rs":12500,"photos_attached":true}}
$ curl -s localhost:8000/triage -H 'content-type: application/json' -d @data/e24.json
{"draft":"refer","reasons":["registration does not match the policy","above the pilot limit"],"fields":{"policy_no":"DS-POL-40370","vehicle_reg":"MH14HJ5656","incident_date":null,"incident_type":"other","amount_rs":61000,"photos_attached":false}}
$ curl -s localhost:8000/triage -H 'content-type: application/json' -d @data/e26.json
{"draft":"refer","reasons":["incident outside the policy period"],"fields":{"policy_no":"DS-POL-40925","vehicle_reg":"MH12LL6767","incident_date":"2026-10-26","incident_type":"accident","amount_rs":6800,"photos_attached":false}}
$ curl -s -w ' (HTTP %{http_code})' localhost:8000/triage -H 'content-type: application/json' -d @data/short.json
{"detail":[{"type":"string_too_short","loc":["body","email"],"msg":"String should have at least 20 characters","input":"help","ctx":{"min_length":20}}]} (HTTP 422)
```

This is what the room sees:

- **E-01**, a scooter hit near Swargate: `pay`, no reasons, every field correct. The adjuster checks it in seconds.
- **E-24**: `refer`, with both problems named. Sunil nods: the registration mismatch is exactly what he would have caught.
- **E-26**: the accident was on 26 October, the policy ended on 20 October. `refer`, "incident outside the policy period".
- **"help"**: refused at the door, 422, no model call.

Then the questions start, and they are the right ones. Finance: "How often is it right?" Priya: "What happens when the
model is down?" Meera: "Can we trust it on the claims you did not show?". Those are the next two parts of this course:
proving it works (Part 4), and running it safely every day (Part 5).
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `/triage` collect every reason instead of returning at the first problem?
:::
- [x] The adjuster sees all the problems at once and can resolve the claim in one pass
- [ ] Python requires it
- [ ] The model needs the list
:::explain
One reason at a time means the claim bounces back and forth. All reasons at once respects the adjuster's time.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where is the cheapest place to stop a junk request (an empty email or a 50-page paste)?
:::
- [ ] In the prompt: tell the model to ignore it
- [x] In the request model, before any code or model call runs
- [ ] After extraction, by checking the fields
:::explain
A field limit costs nothing and runs before everything else. Anything later has already spent time or tokens.
:::
:::

:::step{type=deep-dive title="Go deeper: demos that win"}
**Rehearse on fresh data.** The day before, run the demo on claims from that week, not the ones you built with. If it
breaks, better then than in the room.

**Show the failure modes.** A refer with a good reason builds more trust than ten clean approvals. Prepare one claim the
system cannot read, and show that it says so.

**Record the questions.** The questions in the room are the real requirements for the next phase. Write them down with
who asked, and answer each one in writing within a week.

**Do not promise numbers yet.** "Right on most claims we tried" is honest; "98% accurate" is not, until Part 4 measures
it on a golden set.
:::

:::step{type=recap}
You can now:

- combine a model and code so that the model only reads and code makes every exact decision;
- build an endpoint that drafts pay or refer, with every reason in words an adjuster understands;
- guard an endpoint with request limits, so junk never costs a model call;
- run a demo that shows hard cases and builds trust.

That closes Part 3. Claimdesk reads emails, answers from the wording with citations, uses tools, offers them over MCP, and
triages claims behind an API. Next, chapter 14: "how often is it right?", answered with a golden set.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-13-notes.webp" alt="Handwritten notes about the day-five demo: The model reads, code decides. Collect every reason, not just the first. No reasons means pay, any reason means refer. Guard the door before the model runs. Show the hard cases in a demo. It drafts; the adjuster decides." ai="true"}
One page of notes for this chapter.
:::
:::
