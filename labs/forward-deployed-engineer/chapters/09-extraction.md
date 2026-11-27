:::step{type=story title="From a chat answer to fields a program can use"}
In chapter 8 the model answered a question in a sentence. A sentence is fine for a person. Claimdesk is a program, and a
program cannot act on "It was a scooter hit near Swargate, I think the estimate was about twelve thousand". It needs
**fields**: a policy number it can look up, a registration it can compare, a date it can check against the policy period,
an amount it can compare with the pilot's limit.

Today an adjuster reads each email and types those fields into the claims system by hand. Look at two of the real emails
in `data/claim_emails.json`:

```text
Subject: Water in car

Hello, during the heavy rain on 6 Oct my car (MH12-EF-5678) was standing in water near Baner. Engine does not start.
Policy DS-POL-40148. No estimate yet, garage will tell. Sending 4 photos.
```

```text
Subject: claim

sir i had accident with my motorcycle on 7th october near katraj. leg injury and bike damage. number MH12 JK 3456. i
dont remember policy number. estimate 18k. photos in attachment
```

Registrations with dashes and spaces. "18k". A missing policy number. Dates without a year. This is the work a language
model is genuinely good at, and the most common first job of an AI deployment: **structured extraction**, free text in,
fields out.

:::mission
Ask the model for the six claim fields in a strict JSON shape, check its answer with pydantic, and make sure one
unreadable email never stops a batch.
:::
:::

:::step{type=concept title="A schema the model must follow" file="09-extraction/extract.py" line="19-34"}
You could ask "reply with JSON please" and parse what comes back. Sometimes it would be JSON. Sometimes it would be JSON
inside a sentence, or with a field renamed. A program cannot rely on "sometimes".

Instead, describe the exact shape with a pydantic model, as in chapter 7:

```python
class ClaimFields(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_no: str | None
    vehicle_reg: str | None
    incident_date: str | None
    incident_type: Literal["accident", "theft", "flood", "fire", "glass", "other"]
    amount_rs: int | None
    photos_attached: bool
```

- `str | None` means "text, or null when the email does not say". Letting the model say **null** is important: a field
  that must always be filled invites the model to invent a value.
- `Literal[...]` limits `incident_type` to six words, so Claimdesk never meets "Accident (minor)".
- `extra="forbid"` refuses any field not listed.

Then `ClaimFields.model_json_schema()` turns the class into a **JSON schema**, a standard description of a JSON shape,
and `RESPONSE_FORMAT` (lines 31 to 34) sends it to the model with `"strict": True`. In strict mode the provider forces
the model's answer to match the schema: every field present, the right types, nothing extra.

So the same class does two jobs: it tells the model what to produce, and it checks what came back.
:::

:::step{type=history title="JSON, and answers that must be JSON"}
:::before{title="Before: scraping text"}
Early programs that used language models searched the answer for patterns ("Amount: ...") and broke whenever the model
phrased something differently.
:::

**JSON** (JavaScript Object Notation) was described by Douglas Crockford in the early 2000s as a small, readable format
for data, and written down as RFC 4627 in 2006. It became the common language of web APIs.

Language models could write JSON, but not reliably. In November 2023 OpenAI added a "JSON mode" that guaranteed valid
JSON, though not any particular shape. In August 2024 it introduced **Structured Outputs**: give a JSON schema with
`strict: true`, and the answer is constrained to match it. Other providers added similar features.

:::solved
The model's answer is guaranteed to have the shape your program expects, so parsing it stops being the fragile part.
:::

:::timeline
- **2001** Crockford and Chip Morningstar send the first JSON message; json.org follows in 2002.
- **2006** RFC 4627 describes JSON.
- **November 2023** JSON mode.
- **August 2024** Structured Outputs with strict JSON schemas.
:::

:::funfact
JSON has no comments, on purpose. Crockford removed them because people had started putting parsing instructions in
comments, which would have made one program's JSON unreadable to another.
:::
:::

:::step{type=example title="Worked example: parse, then check"}
This is only to read; it is not in your project. Turning the model's JSON text into a checked object:

```python
from pydantic import BaseModel, ValidationError

class Book(BaseModel):
    title: str
    pages: int | None

text = '{"title": "Shelf", "pages": 320}'
book = Book.model_validate_json(text)
print(book.pages + 1)  # 321

try:
    Book.model_validate_json("Sorry, I cannot help.")
except ValidationError as e:
    print("not a book:", e.error_count(), "error")
```

- `model_validate_json(text)` reads the JSON **and** checks it against the class in one step.
- Text that is not JSON, or JSON of the wrong shape, raises `ValidationError`: even with strict mode on, keep this check.
  A gateway, a proxy or a model refusal can still hand you something else.
- On success you get an object: `book.pages` is an `int`, ready for arithmetic.
:::

:::step{type=predict title="Guess first"}
:::question
E-03 says "during the heavy rain on 6 Oct", with no year. `incident_date` must be YYYY-MM-DD. What do you expect the model to
write?
:::
- [ ] null, because the year is not in the email
- [ ] 2026-10-06, because claims are about recent events
- [x] It is hard to say; it has to pick a year from somewhere
:::explain
The prompt says "use only what the email says", but the date needs a year the email does not give. Keep this question in
mind; the last try step of this chapter shows what the real model did.
:::
:::

:::step{type=try title="Nothing is read yet"}
```text
$ python extract.py
E-01 NOT READ: None
E-02 NOT READ: None
E-03 NOT READ: None
E-04 NOT READ: None
E-05 NOT READ: None
```

`extract_claim` returns `None`, so every email shows as not read, and with no reason (`None`), which is worse: a batch of
500 emails would fail silently.
:::

:::step{type=task task=extract_claim title="Your turn: read the fields from an email"}
In `extract_claim` in `extract.py`:

1. `openai = openai or client()`.
2. Call `chat.completions.create` with `model=MODEL`, `temperature=0`, `response_format=RESPONSE_FORMAT`, and two messages:
   `SYSTEM` as the system message and the email text as the user message.
3. Return `ClaimFields.model_validate_json(completion.choices[0].message.content)`.

Press **Check**.
:::

:::step{type=concept title="One bad email must not stop five hundred" file="09-extraction/extract.py" line="54-59"}
In production, Claimdesk reads emails in batches. Some calls will fail, and they fail in two different ways:

| What went wrong | Where it shows | What to do |
|---|---|---|
| the answer was not the claim JSON (a refusal, a cut-off answer) | `ValidationError` from pydantic | set the email aside: "the answer did not match the claim fields" |
| the call itself failed (network, gateway, rate limit) | an exception from the `openai` library | set it aside with the error's name, to retry later |

`safe_extract` wraps `extract_claim` so that **it never raises**. It always returns two things: the fields (or `None`) and
a reason (or `None`). The caller can then keep going and report the set-aside emails at the end.

```python
try:
    return extract_claim(email_text, openai), None
except ValidationError:
    return None, "the answer did not match the claim fields"
except Exception as e:
    return None, f"the model call failed: {type(e).__name__}"
```

`type(e).__name__` is the class name of the error, like `APIConnectionError` or `RateLimitError`: short, and enough to
decide whether a retry makes sense. Catch `ValidationError` **first**: Python uses the first matching `except`, and
`Exception` would match it too.

Careful: catching every exception is right **here**, at the boundary of a batch job, and wrong almost everywhere else.
It is deliberate, and it reports what it caught.
:::

:::step{type=task task=safe_extract title="Your turn: never stop the batch"}
In `safe_extract`:

1. Call `extract_claim` inside `try` and return `(fields, None)`.
2. On `ValidationError`, return `(None, "the answer did not match the claim fields")`.
3. On any other `Exception as e`, return `(None, f"the model call failed: {type(e).__name__}")`.

The check sends a refusal, a JSON answer with a field missing, and a gateway that cannot be reached. Press **Check**.
:::

:::step{type=try title="Five real emails, and two surprises"}
Through the gateway, with the real model:

```text
$ python extract.py
E-01 {'policy_no': 'DS-POL-40000', 'vehicle_reg': 'MH12AB1234', 'incident_date': '2026-10-03', 'incident_type': 'accident', 'amount_rs': 12500, 'photos_attached': True}
E-02 {'policy_no': 'DS-POL-40111', 'vehicle_reg': 'MH14CD4321', 'incident_date': '2026-10-05', 'incident_type': 'theft', 'amount_rs': 45000, 'photos_attached': True}
E-03 {'policy_no': 'DS-POL-40148', 'vehicle_reg': 'MH12EF5678', 'incident_date': '2023-10-06', 'incident_type': 'flood', 'amount_rs': None, 'photos_attached': True}
E-04 {'policy_no': 'DS-POL-40185', 'vehicle_reg': 'MH12GH9012', 'incident_date': '2026-10-04', 'incident_type': 'glass', 'amount_rs': 8900, 'photos_attached': False}
E-05 {'policy_no': None, 'vehicle_reg': 'MH12JK3456', 'incident_date': '2023-10-07', 'incident_type': 'accident', 'amount_rs': 18000, 'photos_attached': True}
```

Most of it is impressive. `MH12-EF-5678` became `MH12EF5678`, "18k" became 18000, the missing policy number became `None`
instead of an invented one, and "No estimate yet" became `None`.

Now the surprises, which are exactly why an FDE never trusts a first run:

1. **E-03 and E-05: `2023`.** "6 Oct" and "7th october" have no year, and the model chose **2023**, not 2026. It cannot
   know today's date unless you tell it. A claim dated 2023 would be outside every policy period and wrongly referred.
2. **E-02: `photos_attached: True`.** The email attached an FIR copy, not photos. "Attached" made the model think
   "photos".

We ran all 30 emails. Policy numbers were right in 28 (two came back as `ds-pol-40592` and `DS POL 40999`), dates in 25.
You now have the facts to fix things properly, and Part 4 is about exactly that: measuring every field on every email,
and improving the prompt with evidence instead of hope.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why do the fields allow `None` (null) instead of requiring a value?
:::
- [ ] So pydantic runs faster
- [x] So the model can say "the email does not say", instead of being pushed to invent a value
- [ ] Because JSON cannot hold empty strings
:::explain
E-05 has no policy number; with a required field, the model would have to write something. A wrong policy number is far
worse than an honest null.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
With strict mode on, why still call `model_validate_json` and catch `ValidationError`?
:::
- [x] A refusal, a cut-off answer or something between you and the model can still return text that is not the claim JSON
- [ ] Strict mode only works with pydantic
- [ ] It converts the JSON to a string
:::explain
Strict mode makes a correct shape very likely, not certain. The check is cheap; trusting blindly is not.
:::
:::

:::step{type=deep-dive title="Go deeper: extraction in production"}
**Tell the model today's date.** The 2023 dates are fixed by one line in the prompt: "Today is 2026-10-31." (Part 4
measures the improvement.) More generally, give the model the context a human clerk would have.

**Normalise after extraction.** Policy numbers came back in lower case and with spaces. Do not ask the model to be perfect;
normalise in code (upper-case, fix the separator), exactly as the data contract did in chapter 7.

**Confidence and evidence.** Some teams ask for the exact words each field came from ("evidence") and check that the words
are in the email. A field without evidence goes to a human.

**Batches and limits.** A real batch of 30 hit the gateway's limit of 20 requests a minute: 15 calls came back as
`RateLimitError`, and `safe_extract` set them aside instead of crashing. Chapter 18 paces and retries them.
:::

:::step{type=recap}
You can now:

- describe an exact answer shape with pydantic and send it as a strict JSON schema;
- parse and check the model's answer in one step, and get typed fields back;
- make a batch step that never raises, and always says why an item was set aside;
- read a first run critically, and find the mistakes that matter (a missing year, a misread attachment).

Next, chapter 10: adjusters also ask questions about the policy wording. The model must answer from the real clauses, and
show which ones.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-09-notes.webp" alt="Handwritten notes about structured extraction: Describe the answer's shape with pydantic. Send it as a strict JSON schema. Let fields be null when the email says nothing. Check every answer, even in strict mode. One bad email must not stop the batch. Tell the model today's date: it guessed 2023." ai="true"}
One page of notes for this chapter.
:::
:::
