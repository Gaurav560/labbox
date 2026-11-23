:::step{type=story title="The same announcement, two hundred times a day"}
Every delay at every station needs an announcement, in English and in Marathi, calm, with one apology. The
announcement team wrote the perfect prompt for it once. Then they started copying it and changing the train's name by
hand, and within a week there were five versions: one forgot the Marathi, one apologised three times, one said
"platform" where it meant "destination".

A good prompt is worth reusing exactly, with only the facts changed. That is a **prompt template**: fixed wording with
named blanks, filled in at run time. Setu needs two kinds today: a template you fill in your own code, and a template
built into an AI Service method.

:::mission
Fill the delay announcement template from Java, then give the station desk a user message template whose blanks come
from its method's parameters.
:::
:::

:::step{type=concept title="Named blanks: {{train}}, {{destination}}, {{minutes}}" file="14-templates/src/main/java/com/setu/Announcements.java" line="10-12"}
A LangChain4j `PromptTemplate` is text with variables in double curly braces:

```java
static final PromptTemplate DELAY = PromptTemplate.from(
        "Write one short, calm station announcement in English and Marathi: the {{train}} to {{destination}} "
                + "is running {{minutes}} minutes late. Apologise once.");
```

`apply(Map.of("train", ..., "destination", ..., "minutes", ...))` fills every blank and returns a `Prompt`; its
`text()` is the finished string, and `toUserMessage()` turns it straight into a `UserMessage`.

Three rules keep templates safe:

1. **Every variable needs a value.** A blank with no value in the map is an error, not an empty string, so a typo in
   a key fails loudly instead of sending "the {{trian}} to Karjat".
2. **Values are inserted as text.** Whatever a passenger typed goes in as words in the prompt. It cannot change the
   template, but the model still reads it, so it can still try to give the model instructions (prompt injection,
   chapter 25).
3. **Keep the template constant.** One tested wording, many uses: that is the point.

**Check yourself:** where does the number 25 in "running 25 minutes late" come from? (From the `minutes` value in the
map, at run time: the template only says where it goes.)
:::

:::step{type=history title="From few-shot examples to prompt engineering"}
In **May 2020** OpenAI's GPT-3 paper had a title that changed how people used models: **"Language Models are Few-Shot
Learners"**. It showed that you did not need to retrain a model for a new task: put a description and a few examples
in the prompt ("few-shot"), and the model continued the pattern.

:::before{title="A model per task"}
Before that, a new language task (classify complaints, write announcements) meant collecting thousands of labelled
examples and training or fine-tuning a model for it. Each task had its own model.
:::

Suddenly the prompt was the program, and the work of writing prompts that behave reliably got a name: **prompt
engineering**. Teams quickly learned what programmers already knew about code: copy-paste breeds bugs, so prompts
became templates, kept in files, versioned and reviewed.

:::solved
**One tested prompt, many uses.** Templates separate what stays fixed (the wording that works) from what changes (the
facts of each case).
:::
:::

:::step{type=task task=prompt_template title="Your turn: fill the template" file="14-templates/src/main/java/com/setu/Announcements.java" line="17-21"}
Finish `Announcements.delayPrompt(train, destination, minutes)`: fill `DELAY` with
`apply(Map.of("train", train, "destination", destination, "minutes", minutes))` and return the prompt's `text()`.

Press **Check**.
:::

:::step{type=concept title="Templates inside an AI Service" file="14-templates/src/main/java/com/setu/StationDesk.java" line="6-13"}
In an AI Service, the template goes in the `@UserMessage` annotation, and the method's parameters fill it:

```java
@UserMessage("A passenger at {{station}} station asks: {{question}}")
String ask(@V("station") String station, @V("question") String question);
```

`@V("station")` says "this parameter's value goes in the `{{station}}` blank". When a method has a single parameter and
no `@V`, its value is called `{{it}}`: `@UserMessage("Translate to Marathi: {{it}}") String translate(String text);`.

Why does Setu need the station at all? Because the same question means different things in different places: "How do
I get to the town centre?" has one answer at Lonavala and another at Ratnagiri. Putting the station in the prompt is
**context**, the same idea as grounding in chapter 11, on a small scale.

If you forget a `@V`, LangChain4j stops at once with a clear error naming the parameter ("The parameter 'station' in
the method 'ask' ... must be annotated with ... V"): with two or more parameters, each one must say which blank it fills.
:::

:::step{type=task task=template_service title="Your turn: a template on the station desk" file="14-templates/src/main/java/com/setu/StationDesk.java" line="8-12"}
In `StationDesk.java`, annotate `ask` with `@UserMessage("A passenger at {{station}} station asks: {{question}}")` and
its parameters with `@V("station")` and `@V("question")` (imports from `dev.langchain4j.service`).

```bash run
cd /workspace/14-templates && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Two templates at work"}
```text
$ mvn -q -o compile exec:java
PROMPT: Write one short, calm station announcement in English and Marathi: the Konkan Breeze to Ratnagiri is running 25 minutes late. Apologise once.
**English Announcement:**

"Attention please, the Konkan Breeze train to Ratnagiri is running 25 minutes late. We apologize for the inconvenience and appreciate your understanding. Thank you."

---

**Marathi Announcement:**

"कृपया लक्ष द्या, रत्नागिरीसाठीचा कोंकण ब्रीज ट्रेन २५ मिनिटे उशीराने येत आहे. यामुळे होणाऱ्या असुविधेसाठी आम्ही क्षमा मागतो आणि तुमच्या समजुतीसाठी आभारी आहोत. धन्यवाद."

At Lonavala: You can take a local taxi or an auto-rickshaw from Lonavala station to the town centre. It's a short ride, usually taking around 10-15 minutes. Alternatively, you can also walk if you prefer, as it's not too far.

At Ratnagiri: You can take a local taxi or auto-rickshaw from Ratnagiri station to the town centre, which is about 2-3 kilometers away. Alternatively, there may be local buses available. Please check the latest schedules at the station.
```

The announcement prompt is exactly the template with the three values in place, and the model followed every part
of it: English, Marathi, one apology. The station desk answered the same question differently for Lonavala and
Ratnagiri, because the station travelled in the prompt. (Are the distances right? The model knows Indian towns in
general, not Sahyadri Rail's stations; "about 2-3 kilometers" is plausible, not checked. Facts from the railway's own
documents come in chapter 23.)
:::

:::step{type=predict title="Guess first"}
:::question
A passenger types `{{station}}` into the question box. What reaches the model?
:::
- [ ] The station name, because the template fills it in
- [x] The literal text {{station}}: values are inserted once, they are not templates themselves
- [ ] An error
:::explain
Filling happens once, on the template. What the passenger typed is just a value. (It is still text the model reads,
which is why chapter 25 guards the input.)
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A method has one parameter and no `@V`. What is its template variable called?
:::
- [x] {{it}}
- [ ] {{value}}
- [ ] {{arg0}}
:::explain
`{{it}}` is LangChain4j's name for the single parameter. With two or more, name each with `@V`.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does a missing template value fail loudly instead of leaving the blank empty?
:::
- [ ] To save tokens
- [x] So a typo is caught at once instead of sending a broken prompt to the model
- [ ] Because the model cannot read braces
:::explain
A broken prompt still gets an answer, just a worse one, and nobody notices. Failing fast is safer.
:::
:::

:::step{type=deep-dive title="Go deeper: templates in production"}
**Built-in variables.** LangChain4j fills `{{current_date}}`, `{{current_time}}` and `{{current_date_time}}` for you.
Chapter 15's model got a date wrong; giving it today's date in the template is the first fix.

**Templates from files.** `@UserMessage(fromResource = "announcement.txt")` loads a template like a system message.

**Few-shot examples.** A template can include two or three examples of perfect answers. It costs tokens on every
call, so measure whether quality really improves (chapter 26).

**Versioning prompts.** Teams keep prompts in files under version control and record which version produced each
answer, so a change in behaviour can be traced to a change in wording.
:::

:::step{type=recap}
You can now:

- write a `PromptTemplate` with named blanks and fill it from a map;
- put a template on an AI Service method with `@UserMessage`, filled by `@V` parameters or `{{it}}`;
- explain why templates beat copy-pasted prompts, and what a value can and cannot do;
- add context (like the station) so the same question gets the right answer.

Next, chapter 15: answers your code can use directly. Records, enums and JSON schemas instead of free text.

:::photo{src="/lesson-images/langchain4j/l4j-14-notes.webp" alt="Handwritten notes about prompt templates: fixed words plus named blanks in double braces; apply(Map.of(...)).text(); @UserMessage with a station blank; @V names each blank; one tested prompt, many uses" ai="true"}
One page of notes for this chapter.
:::
:::
