:::step{type=story title="A tool that changes things"}
The planetarium team loves the new tools, and asks for one more: "Can Atlas book seats too? Visitors ask it all the
time." It can. But this tool is different from the others. `openingHours` only **reads**; a booking **changes** the
world: seats disappear, a visitor expects a ticket, someone else is turned away.

Now think about what could go wrong. A model misreads "Could I book two seats, or is it too late?" as a request to
book. A visitor types "Book 6 seats for Sam, Ravi and everyone". A child presses the button six times. The model
should be able to **propose** a booking, but a person should **decide** it. And the model must never decide **whose**
booking it is.

Spring AI 2.1 has a feature for exactly this: **tool call confirmation**. This chapter uses it, together with the
**tool context**, which gives a tool facts the model never sees and cannot change.

Banks have worked this way for centuries: nothing moves until the account holder signs. This cheque for 150 pounds was
signed by the novelist Charles Dickens in 1865; the bank paid only because his signature was on it.

:::photo{src="/lesson-images/spring-ai/cheque.webp" alt="An old handwritten cheque on Coutts and Company, London, dated September 1865, for 150 pounds, signed by Charles Dickens" credit="Wellcome Collection" license="CC BY 4.0" source="https://commons.wikimedia.org/wiki/File:Dickens;Signed_cheque_for_£150,_payable_to_Frederick_Ouvry._Wellcome_L0008370.jpg"}
A cheque signed by Charles Dickens, 1865.
:::

:::mission
Make Atlas's booking tool wait for the visitor's yes, and book for the right visitor, whoever the model names.
:::
:::

:::step{type=concept title="Propose, then decide"}
With tool call confirmation, the tool-calling loop changes for the tools you mark:

1. The model replies with a tool call, as in chapter 7: "run `bookSeats` with 16:00, 2 seats".
2. Before **anything** of that reply runs, Spring AI checks whether the tool needs confirmation. It does, so the loop
   **pauses**: nothing is booked, and the reply comes back to your application with the calls that wait for a decision.
3. Your application shows the calls to a person and collects their decision: **allow** or **deny**.
4. Your application runs the calls with those decisions (a denied call answers the model with your message instead of
   running), and sends the results back to the model, which writes the final answer.

:::diagram{name="ai-tool-confirmation"}
The model proposes a booking; the loop pauses; the visitor says yes or no; only then does the tool run (or not), and the model answers.
:::

Marking a tool takes one attribute:

```java
@Tool(description = "Book seats for a planetarium show.", requiresConfirmation = true)
public String bookSeats(...) { ... }
```

Spring AI keeps nothing while it waits: the pause is an ordinary response, and the resumption is an ordinary request.
Your application keeps the conversation in the meantime, which also means a pause survives a restart if you store it
somewhere durable.

**Check yourself:** with `requiresConfirmation = true`, what has happened to the seats when `/book` returns the pending
call? (Nothing. No part of the model's reply has run yet.)
:::

:::step{type=example title="Worked example: pausing and resuming" file="08-tool-safety/src/main/java/com/atlas/BookingController.java" line="69"}
`BookingController.java` already handles both halves; read it once. After the call, it asks whether anything waits:

```java
ChatResponse reply = chat.prompt()
        .messages(conversation)
        .tools(tools)
        .toolContext(context)
        .call()
        .chatResponse();
List<String> awaiting = ToolCallDecisions.awaitingDecision(reply);
```

`awaitingDecision` returns the **keys** (usually the tool call ids) of the calls waiting for a decision, or an empty
list for an ordinary answer. When something waits, the controller stores the conversation and the reply under a new id,
and returns the pending calls, with their arguments, for a screen to show:

```text
$ curl -s -G localhost:8080/book --data-urlencode visitor=ria --data-urlencode "q=Please book 2 seats for the Black Holes show at 16:00 on 2026-11-28." | jq .
{
  "answer": null,
  "pendingId": "b7c5eaae-0cf5-46e1-b8c1-29f538470a5a",
  "pending": [
    {
      "key": "call_L00rQBuE7by1OtrwNAuPfqpB",
      "tool": "bookSeats",
      "arguments": "{\"date\":\"2026-11-28\",\"time\":\"16:00\",\"seats\":2}"
    }
  ]
}
```

The second half, `POST /book/{id}/confirm?yes=...`, builds one `ToolCallDecision` per call (`allow(key)` or
`deny(key, message)`), and lets Spring AI's `ToolCallingManager` run them:

```java
ToolExecutionResult result = toolCallingManager.executeToolCalls(p.prompt(), p.reply(), new ToolCallDecisions(decisions));
String answer = chat.prompt()
        .messages(result.conversationHistory())
        .call()
        .content();
```

`conversationHistory()` is the whole conversation with the tool results added; sending it on lets the model write the
final answer:

```text
$ curl -s -X POST "localhost:8080/book/b7c5eaae-0cf5-46e1-b8c1-29f538470a5a/confirm?yes=true" | jq .
{
  "answer": "I have booked 2 seats for you for the Black Holes show at 16:00 on November 28, 2026. Enjoy the show!",
  "pendingId": null,
  "pending": []
}
```
:::

:::step{type=task task=confirm_booking title="Your turn: no booking without a yes" file="08-tool-safety/src/main/java/com/atlas/BookingTools.java" line="18"}
In `08-tool-safety`, the `bookSeats` tool runs the moment the model asks. Make it wait for the visitor's decision.

```bash run
cd 08-tool-safety && mvn -q -o spring-boot:run
```

```bash run
curl -s -G localhost:8080/book --data-urlencode visitor=ria --data-urlencode "q=Please book 2 seats for the 16:00 show on 2026-11-28." | jq .
```

You should get a `pendingId` and a pending `bookSeats` call instead of a booking; confirm it with
`curl -s -X POST "localhost:8080/book/ID/confirm?yes=true"` (with the real id). Press **Check**: it tests a no and a
yes.
:::

:::step{type=example title="A real mistake: the model invents a reason"}
The first version of this chapter denied a call with the message "The visitor said no. Nothing was booked." Here is
what the real model then told the visitor:

```text
$ curl -s -X POST "localhost:8080/book/a5181ef4-fa8e-40ee-b918-e93ce35cffab/confirm?yes=false" | jq -r .answer
I can't book seats for that date. The show is too far in the future. Please choose another date or time.
```

"Too far in the future" is invented. Nobody said that; the model filled the gap with a plausible story. A deny
message is an instruction to the model, so it should say what happened **and** what to say. The message became "The
visitor chose not to book. Nothing was booked. Say only that, kindly, and offer more help.", and the same no now gives:

```text
I couldn't book the seats for you. If you need help with anything else, feel free to ask!
```

Plain and true. The same lesson as chapter 2 again: models follow the words you give them, and invent when you leave a
gap.
:::

:::step{type=concept title="The tool context: facts the model never sees"}
Look at the starter's tool once more:

```java
public String bookSeats(String date, String time, int seats,
                        @ToolParam(description = "the visitor's name") String visitorName) { ... }
```

The **model** fills in `visitorName`. So the model decides whose booking it is: it can guess, mishear, or be talked
into "book it for Sam". Who is asking is not something the model knows; your application knows it (from the login, the
screen, the session).

The **tool context** carries such facts from your application to the tool, **without passing through the model**:

```java
chat.prompt()
    .user(q)
    .tools(tools)
    .toolContext(Map.of("visitor", visitor))    // set by the app
    .call();

@Tool(description = "...")
public String bookSeats(String date, String time, int seats, ToolContext context) {
    String visitor = (String) context.getContext().get("visitor");    // read by the tool
    ...
}
```

A `ToolContext` parameter is not shown to the model at all, so the model cannot even try to set it. Use it for every
fact of identity and permission: the user, the tenant, the account.

:::diagram{name="ai-tool-context"}
The model fills the tool's arguments; the tool context goes straight from your application to the tool, around the model.
:::
:::

:::step{type=predict title="Guess first"}
:::question
The tool reads the visitor from the tool context. The model, trying to be helpful, passes `"visitorName": "Sam"` in its
arguments. Whose booking is it?
:::
- [ ] Sam's: the model asked for Sam
- [x] Ria's, the visitor the app put in the tool context; the model's extra argument is ignored
- [ ] Nobody's: the call fails
:::explain
The tool has no `visitorName` parameter any more, so that argument has nowhere to go, and the visitor comes from the
context, set by your code.
:::
:::

:::step{type=task task=tool_context title="Your turn: the right visitor" file="08-tool-safety/src/main/java/com/atlas/BookingTools.java" line="19"}
Change `bookSeats` so that the visitor comes from the tool context (the controller already puts it there under the key
`visitor`), and the model is no longer asked for a name.

Press **Check**: its pretend model asks to book for "Sam" while Ria is the visitor.
:::

:::step{type=try title="When a request breaks the rules"}
What if a visitor asks for more seats than allowed? The parameter's description says "how many seats, 1 to 6", and the
real model respected it before calling anything:

```text
$ curl -s -G localhost:8080/book --data-urlencode visitor=ria --data-urlencode "q=Book 7 seats for the 16:00 show on 2026-11-28." | jq -c .
{"answer":"We can only book a maximum of 6 seats at a time. Would you like to book 6 seats instead?","pendingId":null,"pending":[]}
```

Descriptions guide the model, but they are not a guarantee. The real limit is in `BookingService.book`, which throws if
seats are outside 1 to 6 or not free. When a tool throws, Spring AI's default exception processor sends the exception's
message back to the model as the tool's result ("Only 4 seats are free for the 11:00 show"), so the model can tell the
visitor instead of the request failing. Always validate in code; let descriptions save a round trip.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which tools should need confirmation?
:::
- [ ] Every tool, to be safe
- [x] Tools that change something or cost money: bookings, payments, emails, deletions
- [ ] Only tools that are slow
:::explain
Reading opening hours needs no yes; booking seats does. Confirming every read would make Atlas tedious, and people
learn to click "yes" without reading, which is no safety at all.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why should the visitor's identity come from the tool context and not from a tool parameter?
:::
- [ ] Tool parameters cannot hold names
- [x] The model fills parameters, so it could guess or be talked into another name; the context comes from your app
- [ ] It is faster
:::explain
Anything the model fills, a visitor can try to influence with words. Identity and permissions must come from your
application, which knows who is really asking.
:::
:::

:::step{type=deep-dive title="Go deeper: policies, many tools, and agents that act"}
**Policies.** `requiresConfirmation` is the default policy. A `ToolCallConfirmationPolicy` can also look at the arguments
(confirm only bookings of more than 4 seats), or name tools you cannot annotate, such as tools from an MCP server
(chapter 10), with `spring.ai.tools.confirmation.tools=bookSeats,cancelBooking`.

**Every call of a reply needs a decision.** If the model asks for two tools at once and only one needs confirmation,
the whole reply pauses, and your decisions must cover both calls. Spring AI refuses to resume otherwise, so nothing can
slip through.

**Too many tools.** Each tool's description is sent with every request. Spring AI 2.1's **Tool Search Tool** lets the
model search a large set of tools and receive only the few it needs, which saves tokens and keeps the model's choice
sharp.

**Agents that act.** Assistants that book, pay and send messages for people are called **agents** (chapter 20). The rule
of this chapter scales up: let the model propose, keep identity in your code, and have a person decide anything that
cannot be undone.
:::

:::step{type=recap}
You can now:

- explain why tools that change things need a person's decision, and how confirmation pauses the tool-calling loop;
- mark a tool with `requiresConfirmation = true`, recognise a paused reply with `ToolCallDecisions.awaitingDecision`,
  and resume it with allow and deny decisions through the `ToolCallingManager`;
- write deny messages that tell the model exactly what to say;
- pass identity to tools with `ToolContext`, out of the model's reach, and validate every request in code.

Next, chapter 9: writing your own advisor, the extension point behind memory, retrieval and guardrails.

:::photo{src="/lesson-images/spring-ai/springai-08-notes.webp" alt="Handwritten notes about tools you can trust: requiresConfirmation = true; propose, pause, decide; deny messages say what to say; identity in the ToolContext; validate in code" ai="true"}
One page of notes for this chapter.
:::
:::
