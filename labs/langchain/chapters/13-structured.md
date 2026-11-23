:::step{type=story title="From a sentence to a booking"}
Members ask for cold storage in every possible way: "Please keep 60 crates of kanda for two weeks", "tomatoes, 25
kreats, till next monday". The co-op's booking system cannot read sentences. It needs three fields: a crop, a number of
crates, a number of days.

Asking the model to "answer in JSON" and hoping is fragile: a missing quote, a word instead of a number, and the
booking code crashes. **Structured output** asks for a schema instead: you describe the result as a Pydantic class,
the model is constrained to fill it, and LangChain hands you a checked Python object.

:::mission
Turn free text into a `Booking` object with `with_structured_output`, then build an agent whose run ends with a
`Booking`.
:::
:::

:::step{type=concept title="A schema as a Pydantic class" file="13-structured/booking.py" line="9-13"}
```python
class Booking(BaseModel):
    """A cold storage booking request."""
    crop: Literal["onion", "tomato", "grapes"]
    crates: int = Field(description="number of crates, 1 or more")
    days: int = Field(description="how many days to store them")
```

Everything here reaches the model: the class docstring, the field names, the types (an `int` must be a number; a
`Literal` must be one of the listed words) and each `Field` description. Pydantic then **validates** the reply: a
`Booking` you receive always has a crop from the list and whole numbers.
:::

:::step{type=history title="From asking nicely to a contract"}
:::before{title="Parsing hopeful text"}
In 2023 applications asked "reply only with JSON" and wrote code to fix the replies that were not: stray sentences,
missing brackets, numbers as words.
:::

In **June 2023** function calling (chapter 10) gave a first reliable way: describe the output as a tool's parameters.
In **November 2023** OpenAI added **JSON mode**, which guaranteed valid JSON but not the right fields. In **August 2024**
**Structured Outputs** went further: given a JSON Schema with `strict` set, the model's sampling is constrained so the
output always matches it. LangChain's `with_structured_output` picks the best method each model supports, and turns the
result into your Pydantic class.

:::solved
**A contract, not a request.** The reply has the fields and types you asked for, every time. Whether the **values** are
right is another matter, as this chapter shows.
:::

:::timeline
- **2023** Function calling (June); JSON mode (November).
- **2024** Structured Outputs with strict schemas.
:::
:::

:::step{type=task task=extract_booking title="Your turn: free text to a Booking" file="13-structured/booking.py" line="16-20"}
Finish `extract_booking(message)`: return `model.with_structured_output(Booking).invoke(message)`.

Press **Check**.
:::

:::step{type=concept title="Structured output from an agent: two strategies" file="13-structured/booking.py" line="23-26"}
`create_agent(..., response_format=Booking)` makes an agent's run end with `result["structured_response"]`, a
`Booking`. LangChain has two ways to get it:

| Strategy | How | When LangChain uses it |
|---|---|---|
| `ProviderStrategy` | the provider's own structured outputs (`response_format` with a JSON schema) | models it knows support it |
| `ToolStrategy` | a tool named `Booking` whose parameters are the schema; the model "answers" by calling it | every other model |

Our gateway calls the model `ai-chat`, a name LangChain cannot look up, so it uses `ToolStrategy`: the run ends with an
`AIMessage` calling the `Booking` tool, and a `ToolMessage` confirming it. You can choose explicitly with
`response_format=ProviderStrategy(Booking)`.
:::

:::step{type=task task=booking_agent title="Your turn: an agent that answers with a Booking" file="13-structured/booking.py" line="23-26"}
Finish `booking_agent()`: return `create_agent("openai:ai-chat", tools=[], response_format=Booking)`.

```bash run
cd /workspace/13-structured && python main.py
```

Press **Check**.
:::

:::step{type=try title="Valid, and wrong"}
```text
$ python main.py
'Please keep 60 crates of kanda for two weeks'          -> Booking(crop='onion', crates=60, days=14)
'tomatoes, 25 kreats, till next monday'                 -> Booking(crop='tomato', crates=25, days=7)
'Store my garlic, 10 crates, 5 days'                    -> Booking(crop='onion', crates=10, days=5)

agent: Booking(crop='grapes', crates=40, days=3) ['HumanMessage', 'AIMessage', 'ToolMessage']
```

The first is impressive: "kanda" became `onion`, "two weeks" became 14. The agent ended its run with a `Booking`, and the
three messages show the `ToolStrategy` at work.

Now the other two. Every one is a **valid** `Booking`, and two are **wrong**:

1. "till next monday" became `days=7`. The model does not know today's date, so it could not count the days; the
   schema demanded a number, so it wrote a plausible one. The fix: put today's date in the prompt, or ask for the
   weekday and let Python count the days.
2. "Store my garlic" became `crop='onion'`. The schema allowed only onion, tomato or grapes, and garlic is none of
   them. Constrained to the list, the model picked the nearest word, and a garlic farmer would have got an onion booking.

The fix for the second is to give the schema an honest way out. With `"other"` added to the `Literal` and described as
"other when the crop is not onion, tomato or grapes", the same message gave:

```text
Booking(crop='other', crates=10, days=5)
```

A strict schema guarantees the **shape**. Only your design guarantees the shape can say "this does not fit".
:::

:::step{type=predict title="Guess first"}
:::question
A member writes "keep my onions for a while". The schema requires `days: int`. What is the risk?
:::
- [ ] The call fails
- [x] The model invents a number of days, and the booking looks valid
- [ ] Pydantic asks the member
:::explain
A required field must be filled. Make it optional (`int | None`) when the text may not say, and ask the member.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does Pydantic guarantee about the `Booking` you receive?
:::
- [x] The fields exist and have the right types and allowed values
- [ ] The values match what the member meant
- [ ] The crates are available
:::explain
Validation checks the form. Meaning, and business rules, are still yours to check.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did the agent use a `Booking` tool instead of the provider's structured outputs?
:::
- [ ] Tools are always better
- [x] LangChain does not recognise the gateway's model name, so it uses the strategy every model supports
- [ ] Structured outputs cost more
:::explain
`ToolStrategy` works with any tool-calling model; `ProviderStrategy` can be chosen explicitly when you know the model
supports it.
:::
:::

:::step{type=deep-dive title="Go deeper: schemas that tell the truth"}
**Optional fields.** `days: int | None = None` lets the model say "not given". Your code then asks a follow-up
question instead of booking a guess.

**Validators.** Pydantic's `Field(ge=1, le=500)` rejects 0 or 10,000 crates; `ToolStrategy` can send the validation
error back to the model so it tries again (its `handle_errors` option).

**Dates.** Never ask a model "what date is next Monday". Give it today's date, or have it return the words and compute
the date in Python.
:::

:::step{type=recap}
You can now:

- describe a result as a Pydantic class with types, `Literal`s and descriptions;
- get a checked object from a model with `with_structured_output`;
- end an agent's run with `response_format`, and tell `ToolStrategy` from `ProviderStrategy`;
- design schemas with an honest way out, after seeing a valid but wrong garlic booking.

Next, chapter 14: a member sends a photo.

:::photo{src="/lesson-images/langchain/lc-13-notes.webp" alt="Handwritten notes about structured output: A schema as a Pydantic class; with_structured_output; Agent: response_format; Garlic became onion; Give the schema a way out" ai="true"}
One page of notes for this chapter.
:::
:::
