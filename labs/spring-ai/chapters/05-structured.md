:::step{type=story title="A tour the website can draw"}
The museum's web team has a nice idea: a "Plan my visit" button. A family says how long they have, and the website
draws their route on the floor plan, stop by stop, with a timer for each gallery.

For that, a paragraph like "Start in the Space gallery, then perhaps spend some time with the dinosaurs" is useless.
The website needs **data**: a title, and a list of stops, each with a gallery name and a number of minutes, in JSON,
the same shape every time. Language models write text, but they can be asked to write text in a precise shape, and
Spring AI can turn that text straight into Java objects.

Museums have handed visitors floor plans for well over a hundred years, like this one of the British Museum from a
1915 travel guide. Atlas will hand the website the route to draw on its own plan.

:::photo{src="/lesson-images/spring-ai/museum-floor-plan.webp" alt="An orange printed floor plan of the British Museum's ground floor in 1915, with the round reading room in the middle and named galleries around it" credit="Karl Baedeker" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Map_of_Ground_Floor,_%22British_Museum,%22_London,_1915.jpg"}
The British Museum's ground floor, 1915.
:::

:::mission
Get a tour plan from the model as a Java record, and exhibit suggestions as a list the website can show as buttons.
:::
:::

:::step{type=concept title="Text in, objects out"}
**Structured output** means asking the model to answer in an exact JSON shape, then reading that JSON into your own
types. In Spring AI it is one method, **`.entity(...)`**, at the end of the chain instead of `.content()`:

```java
record Stop(String gallery, int minutes) {}
record TourPlan(String title, List<Stop> stops) {}

TourPlan plan = chat.prompt()
        .user("Plan a 60 minute tour.")
        .call()
        .entity(TourPlan.class);
```

Two things happen behind that call:

1. **Before** sending, Spring AI looks at the `TourPlan` record, writes its shape as a **JSON schema**, and adds it to
   your user message with instructions: answer only in JSON, following this schema.
2. **After** the answer arrives, it reads the JSON into a `TourPlan` with Jackson, exactly as Spring reads a request
   body.

:::diagram{name="ai-structured"}
Spring AI adds the record's JSON schema to the prompt; the model answers in JSON; Jackson turns it into a TourPlan.
:::

A **record** is perfect for this: a short, read-only data class whose fields are its components (Spring's own
chapters use records for request and response bodies too).

**Check yourself:** what does the model actually receive for `.entity(TourPlan.class)`? (Your question, plus Spring AI's
instructions and the JSON schema of `TourPlan`, in the user message.)
:::

:::step{type=example title="Worked example: the instructions Spring AI adds"}
This is the user message Spring AI really sent for `.entity(TourPlan.class)` with the question "Plan a short tour",
recorded by a pretend model while this course was being built:

````text
Plan a short tour
Your response should be in JSON format.
Do not include any explanations, only provide a RFC8259 compliant JSON response following this format without deviation.
Do not include markdown code blocks in your response.
Remove the ```json markdown from the output.
Here is the JSON Schema instance your output must adhere to:
```{
  "$schema" : "https://json-schema.org/draft/2020-12/schema",
  "type" : "object",
  "properties" : {
    "stops" : {
      "type" : "array",
      "items" : {
        "type" : "object",
        "properties" : {
          "gallery" : {
            "type" : "string"
          },
          "minutes" : {
            "type" : "integer",
            "format" : "int32"
          }
        },
        "required" : [ "gallery", "minutes" ],
        "additionalProperties" : false
      }
    },
    "title" : {
      "type" : "string"
    }
  },
  "required" : [ "stops", "title" ],
  "additionalProperties" : false
}```
````

1. Your question comes first, unchanged.
2. Then instructions: JSON only, no explanations, no markdown fences.
3. Then the schema, generated from the record: `stops` is an array of objects with a `gallery` (string) and `minutes`
   (integer), both required.

Field names in the record become field names in the JSON, so name them for the model to understand: `minutes` says more
than `m`.
:::

:::step{type=task task=tour_plan title="Your turn: plan a tour" file="05-structured/src/main/java/com/atlas/TourController.java" line="40"}
In `05-structured`, make `GET /tour?minutes=...` ask the model for a museum tour that takes that many minutes, and
return the answer as a `TourPlan`. Use a prompt template for the minutes.

```bash run
cd 05-structured && mvn -q -o spring-boot:run
```

```bash run
curl -s "localhost:8080/tour?minutes=60" | jq .
```

Press **Check**.
:::

:::step{type=try title="A real plan"}
```text
$ curl -s "localhost:8080/tour?minutes=60" | jq .
{
  "title": "60-Minute Museum Tour",
  "stops": [
    {
      "gallery": "Dinosaur Gallery",
      "minutes": 15
    },
    {
      "gallery": "Space Exploration Exhibit",
      "minutes": 15
    },
    {
      "gallery": "Robotics Zone",
      "minutes": 15
    },
    {
      "gallery": "Physics Experiments Area",
      "minutes": 15
    }
  ]
}
```

Real JSON, in the record's exact shape, adding up to 60 minutes. Your controller returned a `TourPlan`, and Spring wrote
it as JSON, as it would any object.

Look closely at the gallery names, though: "Robotics Zone", "Physics Experiments Area". **The model invented them.** It
does not know the Deccan Science Museum's real galleries, so it made up plausible ones, despite the system prompt's
"never invent exhibits". Structured output controls the **shape** of an answer, not its **truth**. Chapters 8 to 10 give
Atlas the museum's real exhibit cards to answer from.
:::

:::step{type=concept title="When the shape is a list"}
Now the second feature: three exhibit suggestions for an interest, as a list of names. The obvious code:

```java
List<String> names = chat.prompt()
        .user("Suggest three exhibits for a visitor interested in dinosaurs.")
        .call()
        .entity(new ParameterizedTypeReference<List<String>>() {});
```

(`ParameterizedTypeReference` is how Java passes a type like `List<String>`, which `List.class` cannot express.) It was
the first version written for this course, and with the real model it failed:

```text
{ "timestamp": "2026-11-22T19:27:56.487Z", "status": 500, "error": "Internal Server Error", "path": "/suggest" }
```

with this in the app's log:

```text
tools.jackson.databind.exc.MismatchedInputException: Cannot deserialize value of type `java.util.ArrayList<java.lang.String>` from Object value (token `JsonToken.START_OBJECT`)
```

`START_OBJECT`: the model answered with a JSON **object** (something like `{"exhibits": [...]}`), not a bare list.
Models are trained mostly on JSON objects, and wrap lists in one surprisingly often. The robust fix is to ask for an
object yourself: wrap the list in a record.

```java
record Suggestions(List<String> exhibits) {}

List<String> names = chat.prompt()
        .user(...)
        .call()
        .entity(Suggestions.class)
        .exhibits();
```

Now the schema asks for exactly what models like to write, an object with a named list, and your method still returns
a plain list.
:::

:::step{type=task task=exhibit_list title="Your turn: suggest three exhibits" file="05-structured/src/main/java/com/atlas/TourController.java" line="47"}
Finish `GET /suggest?interest=...`: ask for three exhibit names for that interest, read the answer as `Suggestions`,
and return its list.

```bash run
curl -s "localhost:8080/suggest?interest=dinosaurs" | jq -c .
```

Press **Check**.
:::

:::step{type=try title="Suggestions, as a list"}
```text
$ curl -s "localhost:8080/suggest?interest=dinosaurs" | jq -c .
["Dinosaur Hall","Jurassic Journey","Fossil Discovery Zone"]
$ curl -s "localhost:8080/suggest?interest=light%20and%20colour" | jq -c .
["Spectrum Show","Prism Room","Light and Shadow Play"]
```

Three names, every time, ready to become three buttons. And three more invented exhibits: the shape is perfect, the
facts are not yet.
:::

:::step{type=predict title="Guess first"}
:::question
The model answers a `.entity(TourPlan.class)` request with a polite sentence before the JSON: "Here is your tour: {...}".
What happens?
:::
- [ ] Spring AI ignores the sentence and reads the JSON
- [x] Reading the JSON fails with an exception, because the answer is not pure JSON
- [ ] The sentence becomes the title
:::explain
The converter expects JSON and nothing else. That is why the instructions insist on "no explanations", and why
production code catches the exception (or uses the provider's native JSON mode, below) instead of trusting every answer.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `.entity(TourPlan.class)` add to the request?
:::
- [ ] Nothing: it only changes how the answer is read
- [x] Instructions and a JSON schema generated from the TourPlan record
- [ ] A Java class file
:::explain
The model can only follow a shape it is told about, so Spring AI writes the schema into the prompt for you, then reads
the answer with Jackson.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Atlas's tour lists a "Robotics Zone" the museum does not have. Which statement is true?
:::
- [ ] Structured output should have prevented it
- [x] Structured output fixes the shape; the facts need the museum's real data (retrieval, chapter 10)
- [ ] A lower temperature would make it know the real galleries
:::explain
No setting gives a model knowledge it does not have. Shape comes from the schema; truth comes from data you provide.
:::
:::

:::step{type=deep-dive title="Go deeper: native JSON mode, validation and retries"}
**Provider-native structured output.** OpenAI, Anthropic, Google and Mistral can enforce a JSON schema on their own
side, so an answer that breaks the shape cannot even be produced. In Spring AI 2.1 it is one switch:

```java
.entity(TourPlan.class, spec -> spec.useProviderStructuredOutput())
```

The schema then travels as an API field instead of prompt text: stricter, and fewer tokens. It is off by default,
because older models reject it; when a model does not support it, Spring AI quietly falls back to prompt instructions.

**Self-correction.** `spec -> spec.validateSchema()` checks every answer against the schema and, when it does not match,
asks again with the exact error added ("missing required field title"), up to three attempts. Both switches combine:
`spec.useProviderStructuredOutput().validateSchema()`. Retries cost tokens, and the response reports the usage of all
attempts together.

**Validate anyway.** A valid shape can still hold nonsense: a tour of 60 minutes whose stops add up to 90, or a gallery
that does not exist. Check the values in Java (Bean Validation annotations on the record, or plain `if`s) before
showing them.


**Enums and nested records** work too: `enum Level { EASY, MEDIUM, HARD }` in a record gives the model a fixed list of
allowed values in the schema.
:::

:::step{type=recap}
You can now:

- turn a model's answer into a record with `.entity(MyRecord.class)`;
- explain what Spring AI adds to the prompt (instructions and a JSON schema) and how it reads the answer (Jackson);
- avoid the bare-list trap by wrapping lists in a record;
- tell shape from truth: structured output guarantees the first, not the second.

That ends Part 1. Next, chapter 6: conversations, so Atlas remembers what a visitor said a minute ago.

:::photo{src="/lesson-images/spring-ai/springai-05-notes.webp" alt="Handwritten notes about structured output: .entity(TourPlan.class); the schema goes in the prompt; wrap lists in a record; shape is not truth; validate the values" ai="true"}
One page of notes for this chapter.
:::
:::
