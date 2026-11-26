:::step{type=story title="The system nobody wants to touch"}
The database copy is from last night. For a live claim, Claimdesk must ask the **current** policy: renewed this morning?
cancelled yesterday? Only Deccan Shield's policy system knows, and it is fourteen years old.

It has no SQL access for outsiders and no modern API. It answers **XML over HTTP**, the way many systems built in the
2000s do. Its names are its own (`<number>`, `<start>`, `<end>`), and at month end, when every branch is busy, it
answers some requests with **503 Service Unavailable**, which means "too busy, try later".

Nobody at Deccan Shield will change it. The team that built it left years ago, and it works. This is a **legacy
system**: old, important, and fixed in place. Meeting one is a normal part of an FDE's week. You build around it,
politely.

A stand-in for it is in your project, `policy_service.py`, behaving the same way: XML, and busy on every third request.

:::mission
Read a policy from the old system's XML into Claimdesk's own names, and retry politely when it is busy, without
hiding real errors.
:::
:::

:::step{type=concept title="What the old system really sends"}
Start the system in a second terminal:

```text
$ python policy_service.py
policy system on http://127.0.0.1:8081 (busy on every 3rd request)
```

and ask it for a policy with `curl -i` (`-i` shows the status line and headers too):

```text
$ curl -i localhost:8081/policy/DS-POL-40000
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.12.3
Content-Type: application/xml
Content-Length: 310

<?xml version="1.0" encoding="UTF-8"?>
<policy>
  <number>DS-POL-40000</number>
  <holder>M. Joshi</holder>
  <vehicle_reg>MH12EB4010</vehicle_reg>
  <vehicle>two-wheeler</vehicle>
  <start>2026-04-27</start>
  <end>2027-04-26</end>
  <sum_insured>90000</sum_insured>
  <deductible>1000</deductible>
</policy>
```

**XML** (Extensible Markup Language) wraps each value in a named **element**: `<holder>M. Joshi</holder>` is an
element called `holder` with the text `M. Joshi`. `<policy>` contains the others, its **children**.

Ask twice more:

```text
HTTP/1.0 200 OK
HTTP/1.0 503 Service Unavailable
```

The third request got a 503. Nothing is broken; the system is busy, exactly as at month end.

Two problems to solve, then. The names (`number`, `start`, `end`) are not Claimdesk's names (`policy_no`,
`start_date`, `end_date`, the same as the database in chapter 5). And every value in XML is **text**: `90000` arrives as
the string `"90000"`.
:::

:::step{type=example title="Worked example: XML into a dictionary"}
This is only to read; it is not in your project. Python's standard library reads XML with `xml.etree.ElementTree`:

```python
import xml.etree.ElementTree as ET

text = "<book><name>Shelf</name><pages>320</pages></book>"
NAMES = {"name": "title"}
book = {}
for child in ET.fromstring(text):
    key = NAMES.get(child.tag, child.tag)
    book[key] = int(child.text) if key == "pages" else child.text
print(book)  # {'title': 'Shelf', 'pages': 320}
```

- `ET.fromstring(text)` reads the whole text and returns the outer element, `<book>`.
- `for child in ...` goes through its children in order: `<name>`, then `<pages>`.
- `child.tag` is the element's name, `child.text` its text.
- `NAMES.get(child.tag, child.tag)` renames where a new name exists and keeps the tag otherwise. `get` with a second
  argument means "this, or else that".
- Numbers are turned into `int` by name; everything else stays text.

This kind of function is called an **adapter**: it sits at the edge, speaks the old system's language on one side and
yours on the other. Everything after it uses Claimdesk's names only, so when the old system is finally replaced, only
the adapter changes.
:::

:::step{type=predict title="Guess first"}
:::question
Run the starter (with `policy_service.py` running in the other terminal). It asks for four policies, one request each,
with no retrying yet. What happens to the third?
:::
- [ ] It works, like the others
- [x] It fails with 503, because the system is busy on every third request
- [ ] The program waits until the system is free
:::explain
The next step shows it. Without a retry, one busy moment becomes a failed claim for a customer.
:::
:::

:::step{type=try title="One busy moment, one failed claim"}
```text
$ python legacy.py
{}
{}
DS-POL-40074 failed: 503 <error>System busy, try again</error>
{}
```

Two problems at once. Every policy comes back as `{}`, because `parse_policy` does not read the XML yet. And the third
request, DS-POL-40074, failed only because the system was busy for a moment: a second later it would have answered.
:::

:::step{type=task task=fetch_policy title="Your turn: read a policy from the old system"}
In `parse_policy` in `legacy.py`:

1. Read the XML with `ET.fromstring(xml_text)`.
2. For each child element, the key is `TAGS.get(child.tag, child.tag)` and the value is `child.text`.
3. For the keys in `NUMBERS` (`sum_insured`, `deductible`), turn the value into an `int`.
4. Return the dictionary.

`fetch_policy` (lines 20 to 26) already sends the request, turns a 404 into a `LookupError`, and calls your function.
The check starts the system itself. Press **Check**.
:::

:::step{type=history title="Back off, and try again"}
:::before{title="Before: everyone shouting at once"}
On an early shared network cable, two computers that spoke at the same moment garbled each other's messages. If both
simply tried again at once, they collided again, forever.
:::

In 1976, Robert Metcalfe and David Boggs of Xerox PARC published the design of **Ethernet**. When two machines collided,
each waited a random time before trying again, and after each new collision it waited, on average, **twice as long**.
This is **exponential backoff**: wait, then double the wait, so a crowd of retries spreads out instead of piling up.

Metcalfe went on to found the company 3Com, which sold Ethernet hardware to offices everywhere. This early Ethernet
connector from 3Com carries his signature: the same backoff you write in this chapter was running inside boxes like it.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-ethernet-connector.webp" alt="A small black metal box with connectors at both ends and a 3Com Corporation label, signed Bob Metcalfe in green ink." credit="Daderot" license="CC0" source="https://commons.wikimedia.org/wiki/File:Early_Ethernet_connector_-_signed_by_Bob_Metcalfe.jpg"}
An early 3Com Ethernet connector, signed by Bob Metcalfe.
:::

The same idea now protects busy servers everywhere. Cloud providers recommend it for their APIs, usually with a little
randomness ("jitter") so that thousands of clients do not retry at exactly the same moment.

:::solved
Retry temporary failures after a growing wait, so the busy system gets room to recover instead of more load.
:::

:::timeline
- **1976** Metcalfe and Boggs describe Ethernet and its backoff.
- **1998** XML 1.0 becomes a W3C Recommendation; XML over HTTP spreads through business systems.
- **Today** Exponential backoff with jitter is the standard advice for calling cloud APIs.
:::

:::funfact
Metcalfe named Ethernet after the "luminiferous ether", the medium that nineteenth-century physicists wrongly believed
carried light.
:::
:::

:::step{type=concept title="Which failures deserve a retry" file="06-legacy-system/legacy.py" line="29-34"}
A retry is the right answer only when trying again can give a different result. Sort the failures:

| Answer | Meaning | Retry? |
|---|---|---|
| 503 Service Unavailable | busy right now | yes, after a wait |
| 404 Not Found | no such policy | no: it will not appear in a second |
| 500 Internal Server Error | the system failed on this request | no, here: report it, so a person looks |
| 200 OK | the policy | no need |

Retrying a 404 wastes time and hides a real problem (a wrong policy number in the claim). Retrying everything forever
can turn a busy system into a dead one at month end.

So `fetch_with_retry` makes at most `attempts` tries:

```python
for n in range(attempts):
    try:
        return fetch_policy(number, client)
    except httpx.HTTPStatusError as e:
        ...
```

- `fetch_policy` calls `response.raise_for_status()`, which raises `httpx.HTTPStatusError` for 4xx and 5xx answers.
  (A 404 is turned into a `LookupError` first, so it never reaches this `except`.)
- `e.response.status_code` tells you which status it was.
- For a 503 that is **not** the last try, sleep and loop again. For anything else, or a 503 on the last try, `raise`
  the same error so the caller sees exactly what happened.
- The wait doubles: `wait * 2 ** n` gives 0.2 seconds after the first try and 0.4 after the second (with the default
  `wait=0.2`).

Careful: a common slip is sleeping after the last try too. That makes the caller wait for nothing before the error.
:::

:::step{type=task task=retry_busy title="Your turn: retry when the system is busy"}
In `fetch_with_retry`:

1. Loop over the tries with `for n in range(attempts)`, returning `fetch_policy(number, client)` when it works.
2. Catch `httpx.HTTPStatusError`. If `e.response.status_code` is 503 and `n` is not the last try, call
   `time.sleep(wait * 2 ** n)` and continue.
3. Otherwise `raise`.

The check uses a fake system that answers busy, busy, then the policy; one that is busy three times; one with a 500; and
an unknown policy. Press **Check**.
:::

:::step{type=try title="Four policies, no failures"}
```text
$ python legacy.py
{'policy_no': 'DS-POL-40000', 'holder': 'M. Joshi', 'vehicle_reg': 'MH12EB4010', 'vehicle': 'two-wheeler', 'start_date': '2026-04-27', 'end_date': '2027-04-26', 'sum_insured': 90000, 'deductible': 1000}
{'policy_no': 'DS-POL-40037', 'holder': 'N. Gokhale', 'vehicle_reg': 'MH14HJ7313', 'vehicle': 'commercial', 'start_date': '2026-04-28', 'end_date': '2027-04-27', 'sum_insured': 1220000, 'deductible': 5000}
{'policy_no': 'DS-POL-40074', 'holder': 'V. Kale', 'vehicle_reg': 'MH12GJ1664', 'vehicle': 'two-wheeler', 'start_date': '2025-09-30', 'end_date': '2026-09-29', 'sum_insured': 110000, 'deductible': 1000}
{'policy_no': 'DS-POL-40111', 'holder': 'F. Shaikh', 'vehicle_reg': 'MH14JA8610', 'vehicle': 'two-wheeler', 'start_date': '2026-02-04', 'end_date': '2027-02-03', 'sum_insured': 80000, 'deductible': 1000}
```

All four policies, in Claimdesk's names, with `sum_insured` and `deductible` as numbers. DS-POL-40074, the one that
failed before, came through: the system was busy, Claimdesk waited 0.2 seconds, asked again, and got it. The keys are
exactly those of the database in chapter 5, so the rest of Claimdesk does not care where a policy came from.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
The old system answers 404 for a policy number. Should Claimdesk retry?
:::
- [ ] Yes, three times, to be safe
- [x] No: the policy does not exist, and a retry only delays the real problem
- [ ] Yes, but only once
:::explain
Retry what is temporary (busy), report what is not. A 404 usually means a typing mistake in the claim, which a person
should see.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why map `<number>` to `policy_no` in the adapter, instead of using the old names everywhere?
:::
- [x] So the rest of Claimdesk uses one set of names, and only the adapter changes when the old system is replaced
- [ ] XML tags cannot be used as dictionary keys
- [ ] The database requires it
:::explain
Keeping a legacy system's names at the edge stops them spreading through your code, the reports and the prompts.
:::
:::

:::step{type=deep-dive title="Go deeper: living with legacy systems"}
**Jitter.** Add a little randomness to each wait (for example, a random time between 0 and the computed wait), so many
clients that failed together do not retry together.

**Circuit breakers.** If the system fails again and again, stop calling it for a while and fall back (chapter 18), instead
of adding load to something already down.

**Timeouts.** Every call has one (`timeout=5` here). A call without a timeout can hang a whole worker for minutes when the
old system stalls.

**Talk to its owners.** Ask the team that runs the legacy system how many requests a second it can take, and when its
busy hours are. A polite FDE schedules heavy jobs at night and agrees limits in writing.
:::

:::step{type=recap}
You can now:

- read a legacy system's XML into your own names with an adapter at the edge;
- turn text values into numbers where the data needs it;
- tell temporary failures (503) from real ones (404, 500), and retry only the temporary ones;
- retry with exponential backoff, and explain where the idea came from.

Next, chapter 7: a data contract. Data now arrives from an export, a database and an old system. Before any of it reaches
a model, agree in code exactly what a valid claim looks like.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-06-notes.webp" alt="Handwritten notes about legacy systems and retries: A legacy system is old, important and fixed. Translate its names at the edge. XML values always arrive as text. Retry when busy (503), not when missing (404). Wait a little longer before each retry. Never sleep after the last try." ai="true"}
One page of notes for this chapter.
:::
:::
