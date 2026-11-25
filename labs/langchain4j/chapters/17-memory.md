:::step{type=story title="What did I just tell you?"}
A passenger writes: "My name is Meera and I am travelling to Karjat with my grandmother." Setu answers warmly. Then
she asks: "Can she get a lower berth?" and Setu replies: "Who would you like a lower berth for?"

Every call to a model starts from nothing (chapter 4): the model has no memory of the call before. ChatGPT seems to
remember because the app sends the whole conversation again with every new message. Setu needs the same: a **chat
memory**, kept by your application, sent with each request. And because Setu talks to hundreds of passengers at once,
it needs one memory **per passenger**, never mixed up.

:::mission
Give Setu a memory of the conversation, then give every passenger their own.
:::
:::

:::step{type=concept title="ChatMemory: the conversation, kept for you"}
A `ChatMemory` holds the messages of one conversation. When an AI Service has one, every call:

1. adds the new user message to the memory;
2. sends **all** the messages in the memory to the model (system message first);
3. adds the model's answer to the memory.

So the model sees the history every time, exactly as in chapter 9's manual
`model.chat(system, firstQuestion, firstAnswer, secondQuestion)`, but nobody writes that list by hand.

A memory cannot grow forever: the context window has a limit, and every remembered token is paid for on every call
(chapter 12). LangChain4j has two policies, the same sliding window you built in chapter 4:

| Memory | Keeps | Use when |
|---|---|---|
| `MessageWindowChatMemory` | The last N messages | Prototypes and short chats |
| `TokenWindowChatMemory` | The newest messages that fit in N tokens (with a `TokenCountEstimator`) | Production: it controls cost directly |

The system message is special: it is kept even when old messages are evicted, so Setu never forgets who it is. It
does count as one of the N, though (we checked, below).

:::diagram{name="l4j-memory-window"}
A real `MessageWindowChatMemory` with a limit of 10, filled on 26 November with a system message and six questions
and answers.
:::

**Check yourself:** with a window of 10 messages and a system message, what happens to the passenger's first message
after 6 questions and 6 answers? (It has been evicted. We tried it: 13 messages do not fit in 10, the system message
stays, so the oldest three go: the first question, its answer, and the second question. The kept history then starts
with an answer whose question is gone, which can confuse the model; a token window or a summary handles the edge more
gently.)
:::

:::step{type=example title="Worked example: a memory on the builder" file="17-memory/src/main/java/com/setu/Memories.java" line="13-17"}
A memory goes on the AI Service builder (only to read; it is not in your project):

```java
ComplaintWriter writer = AiServices.builder(ComplaintWriter.class)
        .chatModel(model)
        .chatMemory(MessageWindowChatMemory.withMaxMessages(20))
        .build();
```

`AiServices.create(...)` from chapter 13 is the short form with no memory. The builder takes the same model plus any
extras: a memory today, tools in chapter 19, a content retriever in chapter 23.

One memory like this is **shared by every call** of that AI Service: fine for a command-line chat with one user,
wrong for a help desk with many.
:::

:::step{type=task task=window_memory title="Your turn: a memory for Setu" file="17-memory/src/main/java/com/setu/Memories.java" line="13-17"}
Finish `Memories.assistant(model)`: build the `Assistant` with `AiServices.builder(Assistant.class)`, `.chatModel(model)`
and `.chatMemory(MessageWindowChatMemory.withMaxMessages(10))`, then `.build()`.

The usual slip: building a new memory inside each call. Every call then starts empty, and Setu forgets Meera between
her two questions.

Press **Check**.
:::

:::step{type=concept title="One memory per passenger: @MemoryId" file="17-memory/src/main/java/com/setu/PassengerDesk.java" line="8-12"}
For many users, each conversation needs its own memory, chosen by an id. In the interface, mark the parameter that
says whose conversation it is with `@MemoryId`:

```java
String chat(@MemoryId String passenger, @UserMessage String message);
```

and give the builder a **`ChatMemoryProvider`** instead of one memory: a function from an id to that id's memory.
LangChain4j calls it the first time it sees an id, and reuses the memory for every later call with the same id:

```java
.chatMemoryProvider(id -> MessageWindowChatMemory.builder().id(id).maxMessages(10).build())
```

Ravi's messages go to Ravi's memory, Asha's to Asha's, and a request for Ravi never contains a word Asha said. The id
can be anything that identifies a conversation: a user id, a session id, a phone number's hash.

By default these memories live in the JVM's memory and vanish on restart. A `ChatMemoryStore` (for example backed by
a database or Redis) makes them persistent: `MessageWindowChatMemory.builder()...chatMemoryStore(store)`.
:::

:::step{type=task task=memory_per_passenger title="Your turn: a memory per passenger" file="17-memory/src/main/java/com/setu/Memories.java" line="19-24"}
Finish `Memories.desk(model)`: build the `PassengerDesk` with `AiServices.builder(PassengerDesk.class)`,
`.chatModel(model)` and a `.chatMemoryProvider(...)` that makes, for each id, a `MessageWindowChatMemory` with that
id and 10 messages:
`.chatMemoryProvider(id -> MessageWindowChatMemory.builder().id(id).maxMessages(10).build())`.

The usual slip: `.chatMemory(...)` with one memory, plus `@MemoryId` in the interface. The ids then have nothing to
choose between, and Ravi and Asha share one history.

```bash run
cd /workspace/17-memory && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Meera, Ravi and Asha"}
```text
$ mvn -q compile exec:java
> My name is Meera and I am travelling to Karjat with my grandmother.
Hello Meera! I hope you and your grandmother have a pleasant journey to Karjat. If you need any assistance with your travel plans or schedule, feel free to ask!
> What is my name, and where am I going?
Your name is Meera, and you are traveling to Karjat. If you need any further assistance, just let me know!

> (ravi) What did I lose?
You mentioned that you lost your umbrella on the Monsoon Mail. If you need further assistance, please let me know!
> (asha) What did I lose?
I'm sorry to hear that you've lost something. Please provide more details about the item, and I can guide you on how to report it or check for lost and found services.
```

(We ran it again on 26 November: the same answers, word for word.)

Meera's second question only makes sense with the first, and Setu answered it: her name and Karjat, from the memory.
Then the part that matters for a real help desk: Ravi and Asha asked the same question, "What did I lose?". Ravi got
his umbrella back from his own history; Asha, who never lost anything, got a sensible "please tell me more". Two
conversations, one AI Service, no mixing.
:::

:::step{type=predict title="Guess first"}
:::question
Setu runs as one shared memory (not per passenger) on a website. Two passengers chat at the same time. What happens?
:::
- [ ] Nothing bad: the model knows who is who
- [x] Their messages mix in one history, so one passenger's details can appear in answers to the other
- [ ] The second passenger gets an error
:::explain
A single memory is one conversation. On a multi-user system that is a privacy bug. Use @MemoryId and a provider.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does a chat memory have a limit?
:::
- [x] The context window is finite, and every remembered token is paid for on every call
- [ ] Java lists cannot grow
- [ ] Models refuse long conversations
:::explain
Memory is resent, not stored inside the model. Longer memory means bigger, slower and dearer requests.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What happens to the memories when Setu restarts?
:::
- [ ] They are saved by the model provider
- [x] They are lost, unless the memory uses a persistent ChatMemoryStore
- [ ] They are written to setu-system.txt
:::explain
The default store is in memory. For real conversations, give the memory a store backed by a database.
:::
:::

:::step{type=deep-dive title="Go deeper: memory in production"}
**Token windows.** `TokenWindowChatMemory.withMaxTokens(2000, new OpenAiTokenCountEstimator("gpt-4o-mini"))` bounds
the cost of every call directly.

**Summaries.** Some systems replace old messages with a short summary written by the model, keeping the gist of a long
conversation for a few tokens.

**Privacy.** A memory holds what passengers typed: names, plans, sometimes phone numbers. Decide how long to keep it,
who can read it, and delete it when a conversation ends. Chapter 25 adds guardrails for personal data.

**Tools and memory.** When Setu calls tools (chapter 19), the tool requests and results go into the memory too, so the
model can refer back to them.
:::

:::step{type=recap}
You can now:

- explain why models need an application-side memory, and how it is resent each call;
- add a `MessageWindowChatMemory` to an AI Service, and choose between message and token windows;
- keep a separate conversation per user with `@MemoryId` and a `ChatMemoryProvider`;
- explain persistence with a `ChatMemoryStore`, and the privacy duties memory brings.

Next, chapter 18: Setu as a real web API, with Spring Boot and the LangChain4j starter.

:::photo{src="/lesson-images/langchain4j/l4j-17-notes.webp" alt="Sketchnote, Chat memory (the history, resent with every call): A model remembers nothing between calls. A ChatMemory keeps the conversation and sends it again each time, one memory per passenger. The flow: New message, Add to memory, Send the whole window, Save the answer. What we found: Ravi and Asha asked the same, got their own answers; the system message counts as 1 of the 10; 13 messages in, the oldest 3 were evicted; no provider: all passengers share one history." ai="true"}
One page of notes for this chapter.
:::
:::
