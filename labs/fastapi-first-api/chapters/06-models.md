:::step{type=story title="Where exactly was it found, and when?"}
Chapter 5's models accepted almost anything with the right field names. A title of one letter, `"x"`, went straight
onto the shelf. Nobody recorded **when** an item was found, so nobody could tell a scarf found this morning from one
that has waited three months. And a line and a station are really one fact, "red line, Riverside", stored as two
loose fields.

Today the found-item model grows up: rules on each field, a real date, a short list of tags, and a location that is
a small model of its own, inside the item.

:::mission
Give `FoundItemIn` a title of 3 to 60 characters, a `found_on` date and up to five `tags`, and move `line` and
`station` into a nested `Location` model.
:::
:::

:::step{type=concept title="Field: rules for one field" file="06-models/main.py" line="30-38"}
In chapter 4, `Query(...)` put rules on a query parameter. Inside a model, the same job is done by `Field(...)`:

```python
from pydantic import BaseModel, Field


class FoundItemIn(BaseModel):
    title: str = Field(min_length=3, max_length=60, examples=["black umbrella"])
```

`Field` takes the same rules you already know (`min_length`, `max_length`, `ge`, `le`, `pattern`), plus a few for
documentation, like `examples`, which `/docs` shows as the sample value. A default goes inside it too:
`Field(default=[], max_length=5)` means "an empty list when not sent, at most five items". For a list, `max_length`
counts items, not characters.

| Field type | JSON sends | Python gets |
|---|---|---|
| `str` | `"black umbrella"` | a string |
| `date` | `"2026-11-27"` | a `datetime.date` |
| `list[str]` | `["wool", "long"]` | a list of strings |
| `Category` (an Enum) | `"clothing"` | `Category.clothing` |
| `Location` (a model) | `{"line": "blue", "station": "University"}` | a `Location` object |
:::

:::step{type=history title="Why dates travel as 2026-11-27"}
JSON has no date type, only text and numbers. So a date has to travel as text, and the question is which text.
`11/12/2026` is 12 November in the United States and 11 December almost everywhere else.

In 1988 the International Organization for Standardization published **ISO 8601**: year, month, day, biggest unit
first, always with dashes, `2026-11-27`. It cannot be misread, and it even sorts correctly as plain text. Almost every
API uses it, and Pydantic reads and writes it by default.

We sent the solution a date written the other way, `"27/11/2026"`, and Pydantic refused it:

```text
{"type":"date_from_datetime_parsing","loc":["body","found_on"],"msg":"Input should be a valid date or datetime, invalid character in year","input":"27/11/2026",...}
```

It read `27/1` as the start of a year, met the `/`, and gave up. A date and a time, `"2026-11-27T10:30:00"`, is refused
too, with "Datetimes provided to dates should have zero time".
:::

:::step{type=concept title="A model inside a model"}
A location is two facts that always travel together. Give them their own model, and use it as a field's type:

```python
class Location(BaseModel):
    line: Line
    station: str = Field(min_length=2, max_length=40)


class FoundItemIn(BaseModel):
    title: str
    location: Location
```

The JSON nests the same way:

```json
{"title": "red scarf", "location": {"line": "blue", "station": "University"}}
```

And so do the error messages. We sent a location with the line `"pink"` and the station `"U"`; both problems came back
together, each with its full path:

```text
{"detail":[
  {"type":"enum","loc":["body","location","line"],"msg":"Input should be 'red', 'blue' or 'green'",...},
  {"type":"string_too_short","loc":["body","location","station"],"msg":"String should have at least 2 characters",...}
]}
```

`["body","location","line"]` reads like an address: in the body, inside location, the field line. A phone app can
point at exactly the right box on its form. The same `Location` can now be reused in every model that needs a place:
reports, sightings, claims.
:::

:::step{type=try title="The model in /docs" file="06-models/main.py" line="30-38"}
Start this chapter's Lostdesk from `/workspace/06-models` (the same `fastapi dev` command as before) and open `/docs`
in the Preview. Under **Schemas** at the bottom, `FoundItemIn` lists every field with its rules. We read the
solution's schema from `/openapi.json`; part of it:

```json
{"title": {"type": "string", "maxLength": 60, "minLength": 3, "title": "Title", "examples": ["black umbrella"]},
 "found_on": {"type": "string", "format": "date", "title": "Found On"},
 "tags": {"items": {"type": "string"}, "type": "array", "maxItems": 5, "title": "Tags", "default": []}}
```

with `"required": ["title", "category", "location", "found_on"]`. `tags` is not required, because it has a default.
Every rule you write in Python is published for the people who call Lostdesk.
:::

:::step{type=example title="Worked example: a nested contact"}
This is not in your project. A sighting reported by a passenger, with a nested contact:

```python
class Contact(BaseModel):
    name: str = Field(min_length=2)
    phone: str = Field(pattern=r"^[0-9 ]{8,15}$")


class Sighting(BaseModel):
    seen_on: date
    contact: Contact
    notes: list[str] = Field(default=[], max_length=3)
```

1. `Contact` is a model of its own, with its own rules: `pattern` allows only digits and spaces, 8 to 15 of them.
2. `contact: Contact` nests it; the JSON is `{"seen_on": "2026-11-27", "contact": {"name": ..., "phone": ...}}`.
3. `notes` is optional (an empty list) and holds at most 3 texts.
:::

:::step{type=predict title="Guess first"}
:::question
The starter's `FoundItemIn` has no `found_on`. A client sends `"found_on": "2026-11-27"` and `"colour": "red"` anyway.
What happens?
:::
- [ ] 422, because of the unknown fields
- [x] 200, and both fields are silently dropped
- [ ] 200, and both fields are stored
:::explain
We tried it on the starter: the stored item came back as `{"id":2,"title":"x","category":"clothing","line":"blue",
"station":"U"}`. By default a model ignores fields it does not know. That is why a field must be in the model before
Lostdesk can keep it (and why `title: "x"` got in: there is no rule yet).
:::
:::

:::step{type=task task=item_fields title="Your turn: a title rule, a date and tags" file="06-models/main.py" line="31-34"}
In `FoundItemIn`:

- `title`: 3 to 60 characters;
- add `found_on`, a `date`, required;
- add `tags`, a list of texts, at most 5, an empty list when not sent.

Then `POST /items` keeps `"found_on": "2026-11-27"` and `"tags": ["wool", "long"]`, and refuses a two-letter title, a
date like `"yesterday"`, six tags, or no `found_on` at all. Try them in `/docs`, then press **Check**.

You can do this task before or after the next one: the check sends the location flat or nested, whichever your model
expects. (`date` is already imported at the top of the file.)
:::

:::step{type=task task=nested_location title="Your turn: a nested Location" file="06-models/main.py" line="27-36"}
Write a model `Location` with `line` (a `Line`) and `station` (2 to 40 characters), and in `FoundItemIn` replace
`line` and `station` with `location: Location`.

Then this body is accepted, and stored with the location nested:

```json
{"title": "red scarf", "category": "clothing", "location": {"line": "blue", "station": "University"}, "found_on": "2026-11-27"}
```

while `"line"` and `"station"` at the top level are refused with 422. Then press **Check**.

The usual slip: defining `Location` **below** `FoundItemIn`. Python reads the file top to bottom, so
`location: Location` would name a class that does not exist yet, and the file stops with `NameError: name 'Location'
is not defined`. Write the smaller model first.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`tags: list[str] = Field(default=[], max_length=5)`. What does `max_length` count?
:::
- [ ] Characters in each tag
- [x] Items in the list
- [ ] Characters in the whole list
:::explain
On a list, `max_length` limits how many items it holds. To limit each tag's length you would need a rule on the
item type itself.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which date text does Pydantic accept for a `date` field?
:::
- [x] `"2026-11-27"`
- [ ] `"27/11/2026"`
- [ ] `"27 November 2026"`
:::explain
ISO 8601: year-month-day with dashes. We saw `"27/11/2026"` refused.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A nested field fails. What does its `loc` look like?
:::
- [ ] `["body", "station"]`
- [x] `["body", "location", "station"]`
- [ ] `["station"]`
:::explain
`loc` is the full path into the body, one step per level of nesting.
:::
:::

:::step{type=deep-dive title="Go deeper: your own checks with field_validator"}
Some rules are not about length or range. "A found item cannot be found in the future" needs a little code.
Pydantic's `field_validator` runs a method of yours on one field:

```python
from pydantic import field_validator


class FoundItemIn(BaseModel):
    title: str
    found_on: date

    @field_validator("found_on")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("found_on cannot be in the future")
        return value
```

We ran it (with today fixed at 28 November 2026) and sent `"2027-01-01"`. The `ValueError` became a normal 422:

```text
{"type":"value_error","loc":["body","found_on"],"msg":"Value error, found_on cannot be in the future","input":"2027-01-01",...}
```

The method must give back the value (possibly changed, for example `value.strip()` on a text). For rules that
involve two fields at once ("returned_on must be after found_on"), Pydantic has `model_validator`.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Put rules on model fields with `Field(...)`: lengths, ranges, patterns, defaults and examples.
- Use `date` fields, and explain why dates travel as ISO 8601 text, `2026-11-27`.
- Use lists with a limit, `list[str]` with `Field(default=[], max_length=5)`.
- Nest one model in another, read errors with paths like `["body","location","line"]`, and see it all in `/docs`.

:::photo{src="/lesson-images/fastapi/fa-06-sketch.webp" alt="Sketchnote: Fields and nested models. Field puts rules on one field of a model. A model can be the type of a field, so the JSON nests. Flow: JSON body, outer model checks its fields, nested model checks its own, any problem: 422 with a path, a ready object. Remember: Field(min_length, max_length, ge, le, pattern); Dates travel as year-month-day text; By default, a model ignores fields it does not know; Write the smaller model first." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 7: response models, so that what Lostdesk stores and what it shows can differ.
:::
