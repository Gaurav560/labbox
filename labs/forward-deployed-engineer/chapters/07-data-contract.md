:::step{type=story title="Three sources, one shape"}
Claims now reach Claimdesk from three places: the Monday export (chapter 4), the database (chapter 5) and the old
system (chapter 6). Next week a fourth arrives: new claims from the email inbox, typed by IT into a small form.

Every source has its own small habits. One writes registrations as `mh 12 cd 5678`, another as `MH-12-AB-9876`. One
calls a scooter a "bike". One sends a claim on 31 September, a date that does not exist.

If each part of Claimdesk handled these habits itself, the same checks would be written five times, a little
differently each time. So you sit down with Deccan Shield's IT lead, Priya, and agree, field by field, what a valid
claim **is**. Then you write that agreement as code that runs on every claim before it goes any further.

That agreement is a **data contract**. In this chapter you write it, run it on the first twelve claims from the new
form, and produce the report Priya asked for: which rows failed, on which field, and why.

:::mission
Write the agreed shape of a claim as a pydantic model, and turn its errors into a report by row and field.
:::
:::

:::step{type=concept title="A contract is a rule both sides can run"}
A **data contract** says, for each field: its type, the values allowed, and the format. Priya and you agreed this:

| Field | Rule | Why |
|---|---|---|
| `claim_id` | `DS-26-` and five digits | ids from other systems are not ours |
| `policy_no` | `DS-POL-` and five digits | must match the database |
| `vehicle` | one of `two-wheeler`, `car`, `commercial` | the pilot and the prompts depend on it |
| `amount_rs` | a whole number above 0 | a claim of Rs 0 is a mistake |
| `received` | a real date | 31 September is not |
| `vehicle_reg` | like `MH12AB1234`, after tidying | the policy check compares it with the database |

A contract is more than documentation, because it **runs**. A claim that breaks it is refused at the door, with a
reason, before a model reads it, before a decision is drafted, before anyone pays. A clean refusal is cheap; a wrong
payout is not.

The rule for `vehicle_reg` has two parts: first **normalise** (make different spellings of the same value identical:
`mh-12 ab 9876` becomes `MH12AB9876`), then **validate** (check the result against the pattern). Normalise first, or
honest data gets rejected for its spacing.

Check yourself: is `"bike"` a valid vehicle? Not by this contract. It might be a two-wheeler, but guessing is the
sending system's job to fix, not Claimdesk's.
:::

:::step{type=history title="Design by contract"}
:::before{title="Before: hoping the caller was careful"}
For decades, a function simply assumed its inputs were sensible. When they were not, the failure showed up somewhere
else, later, far from its cause.
:::

In 1986 the French computer scientist **Bertrand Meyer** introduced **Design by Contract** with his programming language
Eiffel.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-meyer.webp" alt="A portrait of a smiling man with short grey hair in a light jacket and dark shirt." credit="Fuchsias" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Bertrand_Meyer_recent.jpg"}
Bertrand Meyer in 2015. His rule, "a broken contract fails at once, at the boundary", is the rule of this chapter.
:::

In Eiffel, each routine states its **preconditions** (what must be true of its inputs), its **postconditions** (what it
promises about its result), and the program checks them as it runs. A broken contract fails at once, at the boundary,
naming the rule.

Data teams later took the same idea to the boundaries between systems. In Python, **pydantic**, first released by
Samuel Colvin in 2017, became the common way to write such a contract as a class with type hints. FastAPI, which you use
in chapter 13, is built on it.

:::solved
State the rules where data enters, check them every time, and fail loudly at the boundary with the reason.
:::

:::timeline
- **1986** Meyer introduces Design by Contract with Eiffel.
- **2017** pydantic's first release.
- **2023** pydantic 2, with its core rewritten in Rust for speed.
- **Today** "Data contracts" between teams are a common practice in data engineering.
:::

:::funfact
"Design by Contract" was later registered as a trademark by Meyer's company, which is why you sometimes see it called
"contract programming" instead.
:::
:::

:::step{type=example title="Worked example: a pydantic model"}
This is only to read; it is not in your project. A contract for a library loan:

```python
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class Loan(BaseModel):
    book_id: str = Field(pattern=r"^BK-\d{4}$")
    kind: Literal["book", "magazine"]
    days: int = Field(gt=0)
    due: date
    member: str

    @field_validator("member")
    @classmethod
    def tidy(cls, value):
        name = value.strip().title()
        if not name:
            raise ValueError("a member name is needed")
        return name

loan = Loan(book_id="BK-0042", kind="book", days="14",
            due="2026-12-01", member="  asha rao ")
print(loan.days, loan.due, loan.member)
# 14 2026-12-01 Asha Rao
```

- `class Loan(BaseModel)` declares the fields with **type hints**; pydantic checks and converts each value. The text
  `"14"` becomes the int 14, and `"2026-12-01"` a real `date`.
- `Field(pattern=...)` adds a **regular expression** the text must match: `^BK-\d{4}$` means "starts with BK-, then
  exactly four digits, then ends".
- `Literal["book", "magazine"]` allows only those exact values.
- `Field(gt=0)` means greater than 0.
- `@field_validator("member")` runs your own function on that field. Return the cleaned value, or raise `ValueError`
  with a message, which pydantic turns into a validation error.
:::

:::step{type=predict title="Guess first"}
:::question
`Claim(..., amount_rs="48000", received="2026-10-02", vehicle_reg="mh 12 cd 5678")`, with the contract finished. What is
`amount_rs`?
:::
- [ ] The text "48000"
- [x] The number 48000
- [ ] A validation error, because it is text
:::explain
pydantic converts text that is clearly a number into the declared type. We ran it: `Claim(claim_id='DS-26-10502',
policy_no='DS-POL-40037', vehicle='car', amount_rs=48000, received=datetime.date(2026, 10, 2), vehicle_reg='MH12CD5678')`.
The registration was normalised too.
:::
:::

:::step{type=try title="Nothing is checked yet"}
```text
$ python contract.py
accepted: 0
rejected rows: 0
```

The starter's `Claim` (lines 18 to 26 of `contract.py`) has only `claim_id`, and `contract_report` returns empty lists.
The twelve rows in `data/incoming_claims.csv` are waiting.
:::

:::step{type=task task=claim_model title="Your turn: the claim contract"}
In `class Claim` in `contract.py`:

1. Declare the six fields from the TODO: `claim_id` and `policy_no` with `Field(pattern=...)`, `vehicle` as a
   `Literal`, `amount_rs: int = Field(gt=0)`, `received: date`, and `vehicle_reg: str`.
2. Add a `@field_validator("vehicle_reg")` (with `@classmethod` under it) that upper-cases the value, removes spaces and
   dashes, and raises `ValueError("not a vehicle registration like MH12AB1234")` if the result does not match `REG`.
   Return the cleaned value.

Press **Check**.
:::

:::step{type=concept title="Turning errors into a report" file="07-data-contract/contract.py" line="29-34"}
When a value breaks the contract, pydantic raises `ValidationError`, which lists **every** problem in the row, not just
the first. A real one, from the lab image:

```text
2 validation errors for Claim
vehicle
  Input should be 'two-wheeler', 'car' or 'commercial' [type=literal_error, input_value='bike', input_type=str]
amount_rs
  Input should be greater than 0 [type=greater_than, input_value='0', input_type=str]
```

That text is for developers. Priya asked for something she can act on: row, field, reason. `e.errors()` gives each
problem as a dictionary:

```text
{'type': 'literal_error', 'loc': ('vehicle',), 'msg': "Input should be 'two-wheeler', 'car' or 'commercial'", ...}
```

- `loc` is the **location** of the problem: a tuple, here `('vehicle',)`. For a flat model like ours, its first part is
  the field name.
- `msg` is the human-readable message.

So the report goes through the rows, numbered from 1 with `enumerate(rows, start=1)` (the way Priya sees them in a
spreadsheet, without the header), tries `Claim(**row)`, and on failure adds one `(row_no, field, message)` per problem.
`Claim(**row)` unpacks the dictionary: each key becomes an argument of the same name.
:::

:::step{type=task task=contract_report title="Your turn: the report by row and field"}
In `contract_report`:

1. Go through the rows with `enumerate(rows, start=1)`.
2. Try `Claim(**row)` and add it to the valid list.
3. On `ValidationError as e`, go through `e.errors()` and add `(row_no, str(err["loc"][0]), err["msg"])` for each.
4. Return `(valid, errors)`.

Press **Check**.
:::

:::step{type=try title="Five accepted, seven reasons"}
```text
$ python contract.py
accepted: 5
   DS-26-10501 MH12AB1234 12500
   DS-26-10502 MH12CD5678 48000
   DS-26-10507 MH12AB9876 15000
   DS-26-10511 MH12FG3434 18500
   DS-26-10512 MH14HJ5656 52000
rejected rows: 7
   row 3: vehicle: Input should be 'two-wheeler', 'car' or 'commercial'
   row 4: amount_rs: Input should be greater than 0
   row 5: policy_no: String should match pattern '^DS-POL-\d{5}$'
   row 6: received: Input should be a valid date or datetime, day value is outside expected range
   row 8: claim_id: String should match pattern '^DS-26-\d{5}$'
   row 9: amount_rs: Input should be a valid integer, unable to parse string as an integer
   row 10: vehicle_reg: Value error, not a vehicle registration like MH12AB1234
```

Look at the accepted ones: `mh 12 cd 5678` became `MH12CD5678` and `MH-12-AB-9876` became `MH12AB9876`. Normalising
first saved two honest claims.

And the seven rejections are the habits from the story: the "bike", the Rs 0, the missing policy number, 31 September
(`day value is outside expected range`), an id from another system, the amount typed as `abc`, a registration missing its
number. Priya can fix every one at the source. Seven of twelve sounds bad; it was the form's first day, and that is
exactly why you check.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why normalise `vehicle_reg` before checking it against the pattern?
:::
- [x] So honest values written with spaces, dashes or lower case are accepted in one standard form
- [ ] Because the pattern cannot contain dashes
- [ ] To make validation faster
:::explain
`mh-12 ab 9876` and `MH12AB9876` are the same registration. Normalise, then validate, then store one form that matches
the database.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A row has two problems: `vehicle` is "bike" and `amount_rs` is 0. How many entries does it add to the report?
:::
- [ ] One, for the first problem
- [x] Two, one per field, because pydantic reports every problem in the row
- [ ] None, the row is just skipped
:::explain
Reporting all problems at once means the sender fixes the row in one go, instead of finding the second problem a week
later.
:::
:::

:::step{type=deep-dive title="Go deeper: contracts in production"}
**Version the contract.** When a field is added or a rule changes, the contract gets a new version, and both sides agree
when it takes effect. Silent changes break pipelines on Monday mornings.

**Strict or lax.** pydantic converted `"48000"` to 48000. For some fields you may want `strict=True`, which refuses text
where a number is expected, so sloppy senders are caught early.

**The same model everywhere.** In chapter 13, FastAPI uses pydantic models to check request bodies, and the model's
`model_json_schema()` describes the contract to other teams (and to a language model, in chapter 9).

**Quarantine, do not drop.** In production, rejected rows go to a separate table with their errors, so nothing is lost
and every rejection can be fixed and replayed.
:::

:::step{type=recap}
You can now:

- agree a data contract field by field, and explain why it runs as code;
- write it as a pydantic model with types, patterns, allowed values and limits;
- normalise a value before validating it, with a field validator;
- turn validation errors into a report by row, field and reason that a customer can act on.

That closes Part 2. Claimdesk can read the customer's export, database and old system, and refuses bad claims at the
door. Next, chapter 8: the first call to a language model, through a gateway, with its cost counted.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-07-notes.webp" alt="Handwritten notes about the data contract: A data contract says what a valid claim is. It runs as code, at the door. Normalise first, then validate. pydantic reports every problem in a row. Report the row, the field and the reason. Five of twelve claims kept the contract." ai="true"}
One page of notes for this chapter.
:::
:::
