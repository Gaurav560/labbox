:::step{type=story title="Less glue, more Setu"}
Look back at Part 2. Every feature took the same glue code: build a `SystemMessage`, build a `UserMessage`, call
`model.chat(...)`, dig the text out of `response.aiMessage().text()`. Real applications have dozens of AI features
(answer a question, extract a booking, classify a complaint, write an announcement), and repeating that glue for
each one is how bugs creep in.

LangChain4j's answer is its most loved feature: **AI Services**. You describe what you want as a plain Java
**interface**, a method with a question in and an answer out, and LangChain4j writes the implementation. From this
chapter on, Setu is built mostly from interfaces.

:::mission
Turn Setu into an AI Service: an interface LangChain4j implements, with its instructions loaded from a file by an
annotation.
:::
:::

:::step{type=concept title="An interface, and a proxy that implements it"}
Here is all of Setu, as an AI Service:

```java
public interface Assistant {
    @SystemMessage(fromResource = "setu-system.txt")
    String chat(String question);
}

Assistant setu = AiServices.create(Assistant.class, model);
String answer = setu.chat("Hello!");
```

There is no class that implements `Assistant` in your project. At run time, `AiServices.create` builds a **proxy**: an
object Java generates on the fly, which implements the interface by sending every method call to a handler. For
`chat("Hello!")`, LangChain4j's handler:

1. reads the annotations on the method (`@SystemMessage`, and later `@UserMessage`);
2. builds the messages: the system message from `setu-system.txt`, the argument as the user message;
3. calls the `ChatModel`;
4. converts the answer to the method's return type (a `String` here; a record or an enum in chapter 15).

:::diagram{name="l4j-ai-service"}
A call to setu.chat goes to a proxy; the proxy reads the annotations, builds the messages, calls the ChatModel and converts the answer to the return type.
:::

The documentation compares it to **Spring Data JPA** and **Retrofit**: declare an interface, let the library implement
it. If you have written a Spring Data repository (`interface ProductRepository extends JpaRepository<...>`), this is
the same idea for language models.

**Check yourself:** where is the code that sends Setu's system message? (In LangChain4j's proxy: your code only
declares it with an annotation.)
:::

:::step{type=example title="Worked example: an AI Service for one job" file="13-ai-services/src/main/java/com/setu/Desk.java" line="12-16"}
An AI Service is usually one interface per job. Here is one that writes a polite reply to a complaint (only to read;
it is not in your project):

```java
interface ComplaintWriter {
    @SystemMessage("You write short, warm replies to railway complaints. Never promise compensation.")
    String reply(String complaint);
}

ComplaintWriter writer = AiServices.create(ComplaintWriter.class, model);
String text = writer.reply("The 7:15 was late again!");
```

`AiServices.create(theInterface, model)` is the short form. When you need more (a memory in chapter 17, tools in
chapter 19, retrieval in chapter 23) you use the builder: `AiServices.builder(ComplaintWriter.class).chatModel(model)
...build()`.
:::

:::step{type=task task=ai_service title="Your turn: let LangChain4j implement Setu" file="13-ai-services/src/main/java/com/setu/Desk.java" line="12-16"}
Finish `Desk.assistant(model)`: return `AiServices.create(Assistant.class, model)`.

Press **Check**.
:::

:::step{type=concept title="Instructions as annotations" file="13-ai-services/src/main/java/com/setu/Assistant.java" line="4-9"}
Open `Assistant.java`. The method has no instructions yet, so Setu would answer as a generic assistant. LangChain4j
reads two annotations from AI Service methods:

| Annotation | What it becomes | Example |
|---|---|---|
| `@SystemMessage("...")` | The system message | `@SystemMessage("You are Setu...")` |
| `@SystemMessage(fromResource = "file.txt")` | The system message, read from a file on the classpath | `@SystemMessage(fromResource = "setu-system.txt")` |
| `@UserMessage("... {{it}}")` | The user message, as a template (chapter 14) | `@UserMessage("Translate to Marathi: {{it}}")` |

Keeping instructions in a resource file has real advantages: the prompt is a text file anyone can review in a pull
request, it can be long without cluttering Java, and you can change wording without touching code. Setu's
instructions are in `src/main/resources/setu-system.txt`, the same text as Part 2.

Careful with the import: `dev.langchain4j.service.SystemMessage` is the **annotation**;
`dev.langchain4j.data.message.SystemMessage` is the message class from chapter 9. Same name, different packages.
:::

:::step{type=task task=system_annotation title="Your turn: give the interface its instructions" file="13-ai-services/src/main/java/com/setu/Assistant.java" line="6-8"}
Annotate `chat` in `Assistant.java` with `@SystemMessage(fromResource = "setu-system.txt")`, importing
`dev.langchain4j.service.SystemMessage`.

```bash run
cd /workspace/13-ai-services && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="A class nobody wrote"}
```text
$ mvn -q compile exec:java
jdk.proxy3.$Proxy28
Hello! I'm Setu, the help desk assistant for Sahyadri Rail. I can assist you with information about train schedules, ticket bookings, and general inquiries related to our services. How can I help you today?
```

The first line is the class of `setu`: `jdk.proxy3.$Proxy28`, generated by the JDK at run time. Nobody wrote it, and
yet it answers as Setu, in the voice of `setu-system.txt`. Everything you did by hand in chapters 7 to 9 (messages,
the call, reading the answer) now happens inside that proxy.
:::

:::step{type=predict title="Guess first"}
:::question
You add a second method to `Assistant`: `String translate(String text);`, with no annotations. What does calling it do?
:::
- [ ] It fails to compile: AI Services allow one method
- [x] It works: the text goes to the model as the user message, with no system message
- [ ] It translates automatically because of its name
:::explain
An AI Service can have many methods; each is its own prompt. The method name means nothing to the model: without a
`@SystemMessage` or a `@UserMessage` template saying what to do, the model just sees the text.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `AiServices.create(Assistant.class, model)` return?
:::
- [x] A proxy object that implements Assistant by calling the model
- [ ] A new Java source file
- [ ] The ChatModel itself
:::explain
A dynamic proxy, created at run time. It is a normal object: you can pass it around, inject it, or replace it with a
fake in tests (chapter 26).
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why keep the system prompt in a resource file?
:::
- [ ] The model reads files faster
- [x] Long prompts stay readable and reviewable, and wording changes do not touch Java code
- [ ] Annotations cannot hold text
:::explain
Prompts are part of your application's behaviour. Treat them like code: versioned, reviewed, tested.
:::
:::

:::step{type=deep-dive title="Go deeper: what else an AI Service method can take and return"}
**Return types.** `String`, `AiMessage`, `Result<T>` (the answer plus token usage and sources), records, enums,
`boolean`, lists, and `TokenStream` for streaming (chapter 16).

**Parameters.** The user message, template variables with `@V` (chapter 14), a `@MemoryId` (chapter 17), images and
other content with `@UserMessage ImageContent`, and `ChatRequestParameters` to override temperature per call.

**System message providers.** `AiServices.builder(...).systemMessageProvider(memoryId -> ...)` chooses the
instructions at run time, for example per language or per customer type.

**Chains are legacy.** LangChain4j started with "chains" like the Python library; the documentation now marks them
legacy because they were too rigid. AI Services replaced them.
:::

:::step{type=recap}
You can now:

- describe an AI feature as a Java interface and let `AiServices` implement it;
- explain the proxy: annotations in, messages built, model called, answer converted;
- attach instructions with `@SystemMessage`, inline or from a resource file;
- tell the `SystemMessage` annotation from the `SystemMessage` class.

Next, chapter 14: prompt templates. The same instructions, with blanks filled in for each passenger and station.

:::photo{src="/lesson-images/langchain4j/l4j-13-notes.webp" alt="Handwritten notes about AI Services: an AI Service is an interface; AiServices.create writes the class; a proxy builds the messages; @SystemMessage(fromResource = ...); prompts in files, not in code" ai="true"}
One page of notes for this chapter.
:::
:::
