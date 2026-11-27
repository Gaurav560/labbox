:::step{type=story title="The last two weeks"}
The eight weeks planned in chapter 1 became four months, as engagements do: the pilot, then the rollout to every
office. Now your engagement at Deccan Shield ends in two weeks. Claimdesk works, people use it, and from the first Monday after you
leave, **Priya's team owns it**.

That changes what "done" means. Until now, Claimdesk only had to work. Now it has to work **without you**: started by
someone who did not write it, configured without reading the code, checked by someone who does not know the golden set
by heart, and changed by someone who was not in the shadow-week meeting.

Teams measure this with a grim little number, the **bus factor**: how many people would have to disappear before nobody
can run the system. Right now Claimdesk's bus factor is one, and it is you.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-baton.webp" alt="Runners on a red athletics track during a relay; on the left, one runner reaches out to pass the baton to the next, who is already starting to run." credit="Irish Defence Forces" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:The_Medlay_Relay_Baton_Handover_(4663978109).jpg"}
A relay handover: the next runner is already moving before the baton arrives.
:::

In a relay, the handover happens while both runners are running, in a marked zone, practised in advance. A good FDE
handover is the same: done during the engagement, not in the last afternoon.

:::mission
Make Claimdesk configurable without touching code, give it a smoke test anyone can run, and leave a runbook that answers
the questions people will ask at 9 a.m. on a Monday.
:::
:::

:::step{type=concept title="What the handover contains" file="21-handover/RUNBOOK.md"}
The project folder holds the final Claimdesk in one place: `claimdesk.py` puts together extraction (chapter 9), the fixes
(chapter 16, with the year corrected against the email's **arrival date**, as chapter 16's deep-dive suggested), the
rules (chapters 13 and 19) and the instruction guard (chapter 17).

Around it, four things make it someone else's:

| Piece | Answers | File |
|---|---|---|
| Settings from the environment | "How do I point it at another model, database or limit?" | `settings.py` |
| A smoke test | "Is it working right now?" | `smoke.py` |
| Checks in CI | "Did my change break it?" | the CI file below |
| A runbook | "What do I do when this alert fires?" | `RUNBOOK.md` |

Open `RUNBOOK.md` and read it as Priya would. It says what Claimdesk does and does not do, how to run it, what to do
before changing the prompt, who acts on each alert from chapter 20, the known limits, and the decisions with their
reasons. The **decisions** section matters more than it looks: in six months, someone will ask "why do all thefts go to
investigation?" and the answer should not depend on finding you.
:::

:::step{type=concept title="Settings come from the environment" file="21-handover/settings.py" line="5-28"}
Some values must change without changing code: the gateway address, the API key, the pilot limit (Meera may raise it to
Rs 75,000 next quarter), the prompt version, where the database is. The standard place for them is **environment
variables**, set by whoever runs the program.

Three rules make settings safe to hand over:

1. **Check everything at start-up, and report everything at once.** A service that starts with a missing key and fails
   on the first claim an hour later is worse than one that refuses to start. And a message that names one problem, then
   another on the next try, then another, wastes everyone's morning. Collect every problem into one message.
2. **Never print a secret.** Not in an error message, not in a log line, not when the settings are printed. `Settings`
   declares `api_key` with `field(repr=False)`, so printing a `Settings` shows everything except the key. Error messages
   name the variable ("OPENAI_API_KEY is not set"), never its value.
3. **Defaults for what is safe to default, nothing for secrets.** The pilot limit can default to 50,000. The key cannot
   have a default; it must come from the secrets store.

`settings_from_env(env)` takes the environment as a dict. In real use that is `os.environ`; in the check it is a plain
dict, so it can test every case without changing the real environment, the same idea as the pacer's clock in chapter 18.
:::

:::step{type=example title="Worked example: settings for a library's reminder service"}
This is only to read; it is not in your project.

```python
class ConfigError(Exception):
    pass

def reminder_settings(env):
    problems = []
    if not env.get("SMTP_HOST"):
        problems.append("SMTP_HOST is not set")
    days = env.get("REMIND_AFTER_DAYS", "14")
    if not (days.isdigit() and int(days) > 0):
        problems.append("REMIND_AFTER_DAYS must be a positive whole number")
    if problems:
        raise ConfigError("; ".join(problems))
    return {"smtp_host": env["SMTP_HOST"], "remind_after_days": int(days)}
```

- `env.get(...)` returns `None` for a missing variable; `not` catches both missing and empty (`""`).
- `days.isdigit()` is false for `"14 days"`, `"-3"` and `"1.5"`, so only whole numbers pass; `int(days) > 0` refuses 0.
- The function raises once, at the end, with every problem.
:::

:::step{type=try title="A start that should have failed"}
With the starter, start Claimdesk with an empty key and a pilot limit of "50k":

```text
$ OPENAI_API_KEY= PILOT_LIMIT_RS=50k python smoke.py; echo "exit code $?"
settings: Settings(base_url='http://172.17.0.1:9000/llm/v1', pilot_limit_rs=50000, prompt_version='v1', db_path='data/claimdesk.db')
smoke: 3 of 3 passed []
exit code 0
```

Read it twice. The key is empty and "50k" was quietly ignored, yet the settings look fine. And the smoke test says
**3 of 3 passed**, because the starter's `smoke_test` runs nothing. A check that cannot fail is the most dangerous kind:
everyone believes it.
:::

:::step{type=task task=settings_from_env title="Your turn: settings from the environment"}
In `settings_from_env` in `settings.py`:

1. For each name in `REQUIRED`, in order, add `f"{name} is not set"` when it is missing or empty.
2. Read `PILOT_LIMIT_RS` (default `"50000"`); unless it is all digits and above 0, add
   `"PILOT_LIMIT_RS must be a positive whole number of rupees"`.
3. If there are problems, `raise ConfigError("; ".join(problems))`.
4. Otherwise return a `Settings` with the values, `int(...)` for the limit, and the defaults for `PROMPT_VERSION` and
   `CLAIMDESK_DB`.

Press **Check**.
:::

:::step{type=concept title="A smoke test anyone can run" file="21-handover/smoke.py" line="10-22"}
A **smoke test** is the smallest test that tells you whether the whole system is alive: a few known inputs, end to
end, through the real model, the real database and the real rules. Not thorough (that is the golden set's job), but
fast, cheap and runnable by anyone.

Claimdesk's has three claims, chosen to cover the three paths:

| Case | Arrived | Must be | Why this one |
|---|---|---|---|
| E-01 | 2026-10-04 | pay | a clean claim: extraction, lookup and every rule pass |
| E-24 | 2026-10-27 | refer | registration mismatch and above the limit: the rules fire |
| E-30 | 2026-10-31 | refer | instructions in the email: the guard fires |

`smoke_test(run)` takes the function to test as an argument, so the check can pass fake ones and the real run passes
`triage`. For each case it records **at most one failure**, with the email id:

- `run` raises: `"E-24: crashed (TimeoutError)"`, and it moves on to the next case. A smoke test reports everything; it
  does not stop at the first problem.
- the answer has no `reasons` list: `"E-01: no reasons list"`. An adjuster must always be told why.
- the draft is wrong: `"E-01: expected pay, got refer"`.

`python smoke.py` exits with **0** when all pass and **1** when any fails (and 2 for bad settings). Exit codes are how
other programs, like CI or a deploy script, read the answer.
:::

:::step{type=task task=smoke_test title="Your turn: the smoke test"}
In `smoke_test`:

1. For each `(email_id, email, received_on, want)` in `cases`, call `run(email, received_on)` inside
   `try` / `except Exception as e`. On an exception, add `f"{email_id}: crashed ({type(e).__name__})"` and continue.
2. If the result has no list under `"reasons"`, add `f"{email_id}: no reasons list"`.
3. Otherwise, if the draft is not `want`, add `f"{email_id}: expected {want}, got {draft}"`.

Return the list. Press **Check**.
:::

:::step{type=try title="Is it working? Ask it."}
Through the gateway, with the real model:

```text
$ python smoke.py; echo "exit code $?"
settings: Settings(base_url='http://172.17.0.1:9000/llm/v1', pilot_limit_rs=50000, prompt_version='v1', db_path='data/claimdesk.db')
smoke: 3 of 3 passed []
exit code 0
$ OPENAI_API_KEY= PILOT_LIMIT_RS=50k python smoke.py; echo "exit code $?"
config: OPENAI_API_KEY is not set; PILOT_LIMIT_RS must be a positive whole number of rupees
exit code 2
```

Notice what the first line does not show: the key. And the bad start now stops before any model call, with both
problems in one line.

Now a realistic mistake: someone means to lower the limit to Rs 10,000 for a cautious week, and does not think about the
claims already in the smoke test:

```text
$ PILOT_LIMIT_RS=10000 python smoke.py; echo "exit code $?"
settings: Settings(base_url='http://172.17.0.1:9000/llm/v1', pilot_limit_rs=10000, prompt_version='v1', db_path='data/claimdesk.db')
smoke: 2 of 3 passed ['E-01: expected pay, got refer']
exit code 1
```

E-01 is Rs 12,500, so it is now referred. Maybe that is intended, maybe not; either way, the person changing the setting
finds out in ten seconds, before the adjusters do, and the smoke test's expectations get updated on purpose.
:::

:::step{type=concept title="Checks on every change"}
The last piece runs the checks automatically. A CI (continuous integration, chapter 15) file for GitHub Actions might
look like this:

```yaml
name: claimdesk
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -r requirements.txt
      - run: python -m pytest -q          # unit tests: rules, fixes, redaction (no model)
      - run: python smoke.py              # three known claims, end to end
        env:
          OPENAI_BASE_URL: ${{ secrets.OPENAI_BASE_URL }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

- The unit tests need no model and run on every push.
- The smoke test uses the real model, so its key comes from the CI system's **secrets**, never from the file.
- Add the eval gate from chapter 15 (a fresh run on the golden set, compared with the last accepted one) before any
  change to the prompt or the model. It takes 30 calls and about two minutes, paced.

A red cross on a change is the handover working: the next engineer learns the rule from the check, not from you.
:::

:::step{type=history title="Where smoke tests got their name"}
:::before{title="Before: switch it on and hope"}
When a new circuit board was built, the first test was simply to switch it on. If something was wired wrong, a part
overheated and, quite literally, smoked. Plumbers had their own version: blow smoke into new drain pipes, and wherever
smoke appears, there is a leak.
:::

Software borrowed the name for the first, quickest check after a build or a deploy: does it start, does a basic case
work, before anyone spends time on deeper tests. A failed smoke test means "stop here".

Handing over configuration got its own classic in 2011, when Adam Wiggins, a co-founder of the hosting company Heroku,
published **The Twelve-Factor App**, a short list of practices for software that others can deploy and run. Factor three:
store configuration in the environment, strictly separate from code, so the same code can run anywhere and no secret is
ever committed.

:::solved
A quick end-to-end check anyone can run, and settings that live outside the code: a system the next team can start,
change and trust.
:::

:::timeline
- **Long before software** Plumbers' smoke tests find leaks; electronics engineers switch on new boards and watch.
- **2011** The Twelve-Factor App: configuration in the environment.
- **Today** Every deploy pipeline runs a smoke test before sending real traffic.
:::

:::funfact
Many teams keep their smoke tests deliberately tiny, a handful of cases, so that they run in seconds and nobody is ever
tempted to skip them.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `settings_from_env` collect every problem before raising, instead of raising at the first?
:::
- [ ] Python requires it
- [x] So the person starting Claimdesk fixes everything in one go, not one problem per attempt
- [ ] To hide the problems
:::explain
One message, every problem. It respects the time of whoever is on call.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The starter's smoke test said "3 of 3 passed" with an empty API key. What was wrong?
:::
- [ ] The model was very fast
- [x] It never ran anything, so it could not fail; a check that cannot fail tells you nothing
- [ ] The key is not needed
:::explain
Always see a check fail once, on purpose, before you trust it. That is why every task in this course starts red.
:::
:::

:::step{type=deep-dive title="Go deeper: handing over well"}
**Pair, then watch, then leave.** In your last weeks, let Priya's team make a change while you watch, then let them run a
week while you are only on call. Gaps show up while you can still fill them.

**Write for the reader who missed everything.** The runbook is read in a hurry, by someone stressed. Short sentences,
commands they can copy, and the first step for each alert.

**Hand over the relationships too.** Who at the provider to contact, who decides on the limit, who owns the golden set.
Software fails less often than the knowledge of who to call.

**Leave the evidence.** The golden set, the eval history, the shadow-week report, the failure tables. They are how the
next team will justify changes, and how Deccan Shield will justify the pilot to its board.
:::

:::step{type=recap}
You can now:

- explain what a handover needs: settings outside the code, a smoke test, checks in CI, and a runbook with decisions;
- read settings from the environment, report every problem at once, and never show a secret;
- write a smoke test that covers each path once, survives crashes and reports with exit codes;
- see why a check that cannot fail is worse than none.

Next, the last chapter: a second insurer wants Claimdesk. Find out which parts were Deccan Shield's and which are a
product.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-21-notes.webp" alt="Handwritten notes about the handover: Hand over while you are still there. Settings live in the environment. Report every problem at once. Never print the key. Smoke test: three claims, end to end. A check that cannot fail tells you nothing." ai="true"}
One page of notes for this chapter.
:::
:::
