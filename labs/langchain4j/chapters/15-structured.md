:::step{type=story title="From a message to a booking"}
Passengers write to Setu the way people write: "Hi, I need 3 tickets from Pune to Karjat this coming Saturday morning
please". The booking system cannot read that. It needs a departure station, an arrival station, a date and a number of
passengers, as fields. And the complaints team wants every message sorted into one of six queues, not described in a
paragraph.

So far Setu has returned `String`s, written for people. This chapter makes it return **Java objects**: a record your
code can read field by field, and an enum your code can `switch` on. LangChain4j and the model do this together, with
a **JSON schema**.

:::mission
Extract a `TripRequest` record from a passenger's message, and classify messages into a `Topic` enum.
:::
:::

:::step{type=concept title="A record as the return type" file="15-structured/src/main/java/com/setu/TripRequest.java" line="6-11"}
Here is the shape the booking system needs:

```java
public record TripRequest(
        @Description("departure station") String from,
        @Description("arrival station") String to,
        @Description("travel date as YYYY-MM-DD") String date,
        @Description("number of passengers") int passengers) {
}
```

When an AI Service method returns a record, LangChain4j:

1. turns the record into a **JSON schema**, a machine-readable description of the fields and their types (the
   `@Description`s become descriptions the model reads);
2. sends the schema with the request, asking the model to answer with JSON that fits it;
3. parses the JSON answer into a `TripRequest` with a JSON library.

Here is the real request Setu sent, from the gateway's log (shortened):

```json
"response_format": {"type": "json_schema", "json_schema": {"name": "TripRequest", "strict": true,
  "schema": {"type": "object", "properties": {
    "from": {"type": ["string", "null"], "description": "departure station"},
    "to": {"type": ["string", "null"], "description": "arrival station"},
    "date": {"type": ["string", "null"], "description": "travel date as YYYY-MM-DD"},
    "passengers": {"type": ["integer", "null"], "description": "number of passengers"}},
  "required": ["from", "to", "date", "passengers"], "additionalProperties": false}}}
```

and the model's real answer, which LangChain4j turned into the record:

```json
{"from":"Pune","to":"Karjat","date":"2026-11-26","passengers":3}
```

**Check yourself:** what does `"additionalProperties": false` stop? (The model adding fields the record does not
have.)
:::

:::step{type=history title="From asking nicely to a contract"}
:::before{title="Please reply in JSON"}
In 2023 developers asked models for JSON in the prompt ("Reply only with JSON like this...") and hoped. Usually it
worked. Sometimes the model added a friendly sentence before the JSON, forgot a comma, or invented a field, and the
parser threw an exception in production.
:::

In **June 2023** OpenAI added function calling, which made models produce arguments as JSON (chapter 19). In
**November 2023** came **JSON mode**: the answer was guaranteed to be valid JSON, but not guaranteed to have your
fields. In **August 2024** OpenAI released **Structured Outputs**: with `"strict": true`, the model's output is
constrained, token by token, to match the schema exactly. Other providers followed.

:::solved
**A contract, not a request.** With strict JSON schemas the shape is guaranteed by the server. The content is not:
the model can still put a wrong value in a correct field, as you are about to see.
:::

:::timeline
- **2023** Function calling (June) and JSON mode (November).
- **2024** Structured Outputs with strict JSON schemas, in August.
- **2025** LangChain4j turns records, enums and lists into schemas automatically.
:::
:::

:::step{type=concept title="Telling LangChain4j the model can follow a schema" file="15-structured/src/main/java/com/setu/Models.java" line="14-23"}
Not every model supports strict schemas, so LangChain4j asks you to say so. `Models.structuredModel` (already written)
adds two lines to the builder:

```java
.supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)
.strictJsonSchema(true)
```

With those, every AI Service method that returns a record, an enum, a list or a `boolean` sends a schema. Without
them, LangChain4j falls back to the 2023 way: it adds instructions to the prompt ("You must answer strictly in the
following JSON format...") and hopes, which works most of the time with good models and fails occasionally.

An **enum** works the same way. The schema for `Topic` that Setu sent says the answer must be one of six values:

```json
"properties": {"value": {"type": "string", "enum": ["TIMETABLE", "FARES", "LUGGAGE", "REFUND", "COMPLAINT", "OTHER"]}}
```

The model answered `{"value":"TIMETABLE"}`, and LangChain4j returned `Topic.TIMETABLE`. Classification with an enum
is one of the most useful things a model does in a real system: routing messages, tagging tickets, choosing a team.
:::

:::step{type=task task=extract_trip title="Your turn: extract a TripRequest" file="15-structured/src/main/java/com/setu/Reader.java" line="8-11"}
In `Reader.java`, change the return type of `trip` from `String` to `TripRequest`. Keep the `@UserMessage`.

Press **Check**.
:::

:::step{type=task task=classify_topic title="Your turn: classify with an enum" file="15-structured/src/main/java/com/setu/Reader.java" line="13-14"}
Add a method to `Reader`: `Topic topic(String message)`, annotated with
`@UserMessage("Which team should handle this passenger message? {{it}}")`.

```bash run
cd /workspace/15-structured && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Fields, not paragraphs, and one wrong date"}
```text
$ mvn -q compile exec:java
TripRequest[from=Pune, to=Karjat, date=2026-11-26, passengers=3]
passengers + 1 = 4
COMPLAINT  <- The 7:15 was 40 minutes late again and nobody announced anything!
LUGGAGE  <- Can I carry a bicycle on the Konkan Breeze?
REFUND  <- I cancelled yesterday, where is my money?
TIMETABLE  <- Does the Monsoon Mail stop at Khandala?
```

A real `TripRequest`: `trip.passengers() + 1` is arithmetic on an `int`, no parsing in sight. Four messages, four
sensible queues: the late train is a COMPLAINT, the bicycle is LUGGAGE, the missing money is a REFUND.

Now look at the date. The message said "this coming Saturday", the prompt said today is 2026-11-23 (a Monday), and the
model answered **2026-11-26**, which is a Thursday. Saturday is 2026-11-28. The schema guaranteed a string in the date
field; nothing guaranteed the right date. Models are poor at calendar arithmetic, for the same reason they are poor at
counting (chapter 4): they predict likely text, they do not compute. The fix is to let Java compute: the model can
extract "Saturday" as a word, and `LocalDate.now().with(TemporalAdjusters.next(DayOfWeek.SATURDAY))` does the
arithmetic. Chapter 19 gives Setu tools for exactly this.
:::

:::step{type=predict title="Guess first"}
:::question
With a strict JSON schema, can the model return a `TripRequest` with the wrong destination?
:::
- [ ] No: the schema guarantees correct answers
- [x] Yes: the schema guarantees the shape, not that the values are right
- [ ] No: LangChain4j checks the values
:::explain
Strict schemas remove parsing failures, not mistakes. Validate important values in Java (is "Karjat" a real station?
is the date in the future?) before acting on them.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is an enum a good return type for classification?
:::
- [x] The model can only choose one of your values, and your code can switch on it
- [ ] Enums are cheaper in tokens
- [ ] The model understands Java enums natively
:::explain
The schema lists the allowed values, so the answer is always one your code handles. A free-text answer like "probably
a refund question" would need parsing.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What do `@Description` annotations on record fields do?
:::
- [ ] Nothing at run time
- [x] They become descriptions in the JSON schema, which the model reads
- [ ] They validate the values
:::explain
They are instructions per field. "travel date as YYYY-MM-DD" is how the model knew which date format to use.
:::
:::

:::step{type=deep-dive title="Go deeper: structured output in production"}
**Validation.** Add Bean Validation to the record, or check values in a constructor; refuse or ask again when a field
is impossible.

**Nulls.** The schema allowed `null` for each field (`["string", "null"]`). If the message has no date, a good model
returns `null` instead of inventing one, if your prompt says that is allowed.

**Lists and nested records.** A method can return `List<TripRequest>` (several trips in one message) or records inside
records; the schema grows with them.

**Low level.** Without AI Services, build a `JsonSchema` with `JsonObjectSchema.builder()` and pass a
`ResponseFormat` in a `ChatRequest`; useful when the shape is only known at run time.
:::

:::step{type=recap}
You can now:

- return records and enums from AI Service methods, and explain the JSON schema behind them;
- enable strict schemas with `supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)` and `strictJsonSchema(true)`;
- classify messages into an enum your code can switch on;
- explain why a schema guarantees shape, not truth, and where Java should compute instead.

Next, chapter 16: streaming. Answers that appear word by word, like ChatGPT's.

:::photo{src="/lesson-images/langchain4j/l4j-15-notes.webp" alt="Handwritten notes about structured output: return a record, get a record; the JSON schema goes with the request; an enum is one of your values; schema means shape, not truth; let Java do the date maths" ai="true"}
One page of notes for this chapter.
:::
:::
