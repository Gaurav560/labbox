:::step{type=story title="I'm sorry, I don't know"}
Atlas has good manners now. Ask it the price of a ticket, whether the museum is open on Monday, or whether there are
seats left for the planetarium, and it says honestly: "I'm sorry, but I don't know." That is far better than inventing
an answer. It is also useless: those are exactly the questions visitors ask most.

The answers exist. The opening hours are a rule anyone can write in Java, and the planetarium's free seats are in the
museum's booking system. What Atlas needs is a way to **ask your code** in the middle of answering. That is **tool
calling**: you describe a few Java methods to the model, the model decides when it needs one, Spring AI runs it, and
the result goes back to the model, which then answers with real facts.

A library desk works the same way: when a question needs a fact the librarian does not carry in their head, they
reach for the right book or catalogue drawer, look it up, and answer from it.

:::photo{src="/lesson-images/spring-ai/reference-desk.webp" alt="A black and white photo of a busy library reading room desk, with readers in hats and coats being helped by staff among catalogue drawers and books" credit="Pix Magazine photographer" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Library_desk,_Reading_Room,_Mitchell_Building.jpg"}
A library reading room desk.
:::

:::mission
Give Atlas two tools, the opening hours and the planetarium's shows, so it answers those questions from your code
instead of saying "I don't know".
:::
:::

:::step{type=concept title="How tool calling works"}
The model never runs your code, and never sees it. What it sees is a short **description** of each tool: its name,
what it does, and its parameters. Here is the real description Spring AI sent for Atlas's opening-hours tool:

```json
{
  "function": {
    "name": "openingHours",
    "description": "The museum's opening hours on one date. The museum is closed on Mondays.",
    "parameters": {
      "type": "object",
      "properties": {
        "date": { "type": "string", "description": "the date, as YYYY-MM-DD" }
      },
      "required": [ "date" ]
    }
  },
  "type": "function"
}
```

Then a conversation in several steps happens, all inside one call to your endpoint:

1. Your app sends the question **and** the tool descriptions.
2. The model decides it needs a fact. Instead of answering, it replies with a **tool call**: "please run
   `openingHours` with `date = 2026-11-30`".
3. Spring AI runs your Java method with that argument, and sends the result back as a **tool message**.
4. The model reads the result and either asks for another tool, or writes the final answer.

:::diagram{name="ai-tool-calling"}
The model asks for a tool; Spring AI runs your method; the result goes back; the model answers with the real fact.
:::

Your code decides **what is possible** (only the tools you offer, only what they return); the model decides **when** to
use them. That split is what makes tools safe enough for real systems.

**Check yourself:** who executes `openingHours`, the model or your application? (Your application. The model only asks
for it by name, with arguments.)
:::

:::step{type=example title="Worked example: a tool is a method with @Tool" file="07-tools/src/main/java/com/atlas/MuseumTools.java" line="25"}
Open `MuseumTools.java`. It is a normal Spring component, with one tool already written:

```java
@Tool(description = "Today's date, as YYYY-MM-DD, and its day of the week.")
public String today() {
    LocalDate now = LocalDate.now();
    return now + " (" + now.getDayOfWeek() + ")";
}
```

1. **`@Tool`** marks the method as a tool. Its **description** is what the model reads to decide when to use it: write
   it for the model, as clearly as for a colleague.
2. The method's name becomes the tool's name; its parameters become the tool's parameters. **`@ToolParam(description =
   "...")`** on a parameter tells the model what to put there.
3. The return value goes back to the model, as text (Spring AI writes records and lists as JSON).

To offer tools, pass the object to the prompt:

```java
chat.prompt()
    .user(q)
    .tools(museumTools)      // every @Tool method on this object
    .call()
    .content();
```

Why does Atlas need a `today()` tool at all? Because a model does not know today's date: it only knows the text it was
trained on and what you send it.
:::

:::step{type=task task=opening_hours_tool title="Your turn: the opening hours" file="07-tools/src/main/java/com/atlas/MuseumTools.java" line="38"}
In `07-tools`:

1. In `MuseumTools.java`, write a tool **`openingHours(String date)`**: the museum is **closed on Mondays**, and open
   from **10:00 to 18:00** on every other day. Describe the tool, and its `date` parameter (as `YYYY-MM-DD`).
2. In `AskController.java`, offer the model the museum's tools.

```bash run
cd 07-tools && mvn -q -o spring-boot:run
```

```bash run
curl -s -G localhost:8080/ask --data-urlencode "q=Is the museum open next Monday?"; echo
```

(`LocalDate.parse(date)` reads a `YYYY-MM-DD` string; `getDayOfWeek() == DayOfWeek.MONDAY` tests the day.) Press
**Check**.
:::

:::step{type=task task=show_times_tool title="Your turn: planetarium shows" file="07-tools/src/main/java/com/atlas/MuseumTools.java" line="40"}
Add a second tool, **`planetariumShows(String date)`**, that returns `schedule.showsOn(...)` for that date: a list of
`Show` records, each with a time, a title and the number of free seats. The `ShowSchedule` service already exists.

```bash run
curl -s -G localhost:8080/ask --data-urlencode "q=Are there free seats for the planetarium shows this Saturday?"; echo
```

Press **Check**.
:::

:::step{type=example title="A real mistake: the model and the calendar"}
Here is what happened the first time this chapter's code ran, when `today()` returned only the date ("2026-11-22", a
Sunday) and there was no other date tool. Asked about seats "this Saturday", Atlas answered confidently:

```text
This Saturday, we have three planetarium shows with free seats: 

1. "Journey to the Moon" at 11:00 - 37 seats
2. "The Life of Stars" at 14:00 - 52 seats
3. "Black Holes" at 16:00 - 60 seats
```

Those are **Thursday's** numbers: on Saturdays the 14:00 show is sold out. The gateway's log (`lab requests --last`
shows it) explains why. These were the messages of that request:

```text
user      | Are there free seats for the planetarium shows this Saturday?
assistant | tool call: today {}
tool      | "2026-11-22"
assistant | tool call: planetariumShows {"date":"2026-11-26"}
tool      | [{"time":"11:00","title":"Journey to the Moon","freeSeats":37}, ...]
```

The model knew today's date, then worked out "this Saturday" by itself, and got it wrong: 26 November 2026 is a
Thursday. Language models are poor at arithmetic, and calendar arithmetic is arithmetic. The tool was right, the
model's argument was wrong.

The fix is a rule worth remembering: **do not make the model calculate; give it a tool that calculates.** `today()`
now also says the day of the week, and a new tool does the date arithmetic in Java:

```java
@Tool(description = "The date of the next given day of the week, counting today. Use it for 'this Saturday' or 'next Monday'.")
public String nextDay(@ToolParam(description = "a day of the week in capitals, like SATURDAY") String dayOfWeek) {
    LocalDate date = LocalDate.now().with(TemporalAdjusters.nextOrSame(DayOfWeek.valueOf(dayOfWeek.trim().toUpperCase())));
    return date + " (" + date.getDayOfWeek() + ")";
}
```

The same question afterwards:

```text
user      | Are there free seats for the planetarium shows this Saturday?
assistant | tool call: nextDay {"dayOfWeek":"SATURDAY"}
tool      | "2026-11-28 (SATURDAY)"
assistant | tool call: planetariumShows {"date":"2026-11-28"}
tool      | [{"time":"11:00","title":"Journey to the Moon","freeSeats":4},{"time":"14:00","title":"The Life of Stars","freeSeats":0},{"time":"16:00","title":"Black Holes","freeSeats":11}]
```

```text
$ curl -s -G localhost:8080/ask --data-urlencode "q=Are there free seats for the planetarium shows this Saturday?"; echo
Yes, there are free seats for the planetarium shows this Saturday. "Journey to the Moon" at 11:00 has 4 free seats, and "Black Holes" at 16:00 has 11 free seats. However, "The Life of Stars" at 14:00 is fully booked.
```

Two tool calls, the right date, the right seats, and the sold-out show named. Note that one question cost three
model calls here; tools make answers right, and a little slower and dearer.
:::

:::step{type=predict title="Guess first"}
:::question
A visitor asks "How much is a ticket?". Atlas has the tools `today`, `nextDay`, `openingHours` and `planetariumShows`.
What should happen?
:::
- [ ] The model calls `openingHours`, because it is the closest tool
- [x] No tool fits, so the model answers without one, and should say it does not know the price
- [ ] Spring AI throws an error because no tool matches
:::explain
The model only calls a tool when its description fits the question. With the system prompt's "never invent prices", the
honest answer is still "I don't know", until you add a `ticketPrices` tool.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does the model use to decide which tool to call?
:::
- [ ] The Java code of each method
- [x] The tools' names, descriptions and parameter descriptions
- [ ] The order in which you wrote the methods
:::explain
The model only ever sees the descriptions. A vague description ("gets data") leads to wrong or missing calls; a precise
one ("The museum's opening hours on one date. Closed on Mondays.") leads to the right call.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
The model passes a wrong argument to a correct tool (Thursday's date for "this Saturday"). What is the best fix?
:::
- [ ] Ask the model to be more careful in the system prompt
- [x] Add a tool that does the calculation, so the model does not have to
- [ ] Raise the temperature
:::explain
Prompts can help a little, but models stay weak at arithmetic. Code is exact: move the calculation into a tool, and the
model only has to pick the right tool and copy the answer.
:::
:::

:::step{type=deep-dive title="Go deeper: what else tools can do"}
**Tools that change things.** A tool could book seats, not just read them. Then the stakes change: the model might call
it by mistake, or a visitor might trick it into doing so. Chapter 8 covers tools you can trust: confirmation before a
tool runs, limits, and handling errors.

**Returning directly.** `@Tool(returnDirect = true)` sends the tool's result straight to the caller, without a second
model call. Useful when the result is already the answer (a booking reference, say), and it saves a call.

**Tool context.** `ToolContext` passes information from your app to a tool without the model seeing it (the visitor's
id, for example), so a tool can act for the right person without the model being able to change who that is.

**Many tools.** Every tool description is sent with every request, as input tokens. With dozens of tools, Spring AI 2.1's
Tool Search Tool lets the model search for the tools it needs instead of receiving all of them every time.

**Who supports it.** Most current models from OpenAI, Anthropic, Google, Mistral and many open models (through Ollama)
support tool calling; Spring AI uses each provider's own format behind the same `@Tool` annotation.
:::

:::step{type=recap}
You can now:

- explain tool calling: the model asks for a tool by name, your app runs it, the result goes back, the model answers;
- write tools as methods with `@Tool` and `@ToolParam`, and offer them with `.tools(...)`;
- read a tool-calling conversation, and diagnose a wrong answer from it;
- move calculations out of the model and into tools.

Next, chapter 8: tools you can trust, when a tool can change things.

:::photo{src="/lesson-images/spring-ai/springai-07-notes.webp" alt="Handwritten notes about tools: @Tool + a clear description; the model asks, Java runs it; .tools(museumTools); don't let the model calculate; give it a tool that does" ai="true"}
One page of notes for this chapter.
:::
:::
