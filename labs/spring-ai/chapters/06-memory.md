:::step{type=story title="What was my name again?"}
Ria, nine years old, is talking to the lobby screen. "Hi! My name is Ria and I am nine." Atlas greets her warmly.
Then she asks, "What would you show someone my age first?", and Atlas has no idea how old she is. It has forgotten
her completely, between one sentence and the next.

That is not a bug in Atlas: it is how every language model works. **A model remembers nothing between calls.** Each
request is read from scratch. What feels like memory in ChatGPT is the application sending the earlier messages again,
every time. This chapter gives Atlas that memory, keeps each visitor's conversation separate, and stops long
conversations from growing without limit.

People have always kept memory outside their heads. In 1817 an eleven-year-old called Samuel Parris began a journal
"wherein I intend to record every thing material that happens near me ... that by looking on this I may remember
them". A session is Atlas's journal: one per visitor, read again before every answer.

:::photo{src="/lesson-images/spring-ai/diary.webp" alt="The first page of a handwritten journal from 1817, in brown ink, headed Journal B. First Volume, by Samuel B. Parris, aged 11" credit="Samuel Bartlett Parris" license="Public domain" source="https://commons.wikimedia.org/wiki/File:The_first_page_of_Samuel_Bartlett_Parris’s_1817_diary_(Volume_I).jpg"}
The first page of Samuel Parris's journal, 1817.
:::

:::mission
Give every visitor their own conversation with Atlas, and keep only its most recent messages.
:::
:::

:::step{type=concept title="Memory is just the history, sent again"}
To hold a conversation, the application keeps the messages so far and sends them with every new question:

| Request | Messages sent |
|---|---|
| first | system, user "My name is Ria and I am 9." |
| second | system, user "My name is Ria and I am 9.", assistant "Hi Ria! ...", user "What would you show someone my age?" |
| third | all of that, plus the second answer, plus the new question |

The model reads the whole history each time, so it "remembers". Three things follow:

1. **Someone has to store the history.** In Spring AI 2.1 that is **session memory**: each conversation is a
   **session**, kept as a log of **events** (every message, in order).
2. **Each visitor needs their own session**, found by a **session id**.
3. **The history grows**, and every token of it is sent and paid for again with every question (chapter 3). So a
   session is **compacted**: once it gets long, only the recent part stays in the **view** the model sees, while the
   full log is kept.

:::diagram{name="ai-memory"}
The real tenth request of this chapter's app, read in the gateway's log (trigger: more than 8 turns; window: the last 4).
:::

A **turn** is one question and everything up to the next question: the answer, and any tool calls in between. Turns
are the unit sessions count and keep, so a window never cuts an answer away from its question.

**Check yourself:** a conversation has ten long exchanges. Does the eleventh question cost the same as the first?
(No: it carries the whole history as input tokens, so it costs much more. That is why sessions are compacted.)
:::

:::step{type=example title="Worked example: the session service and the session advisors" file="06-memory/src/main/java/com/atlas/SessionConfig.java" line="13"}
Two pieces work together.

**The `SessionService`** stores sessions. Atlas keeps them in memory, configured in `SessionConfig.java`:

```java
@Bean
SessionService sessionService() {
    return DefaultSessionService.builder()
            .sessionRepository(InMemorySessionRepository.builder().build())
            .build();
}
```

**The session advisors** connect it to the `ChatClient`. An **advisor** is a piece of code that runs around every call:
it can change the request before it is sent and look at the answer afterwards. `SessionAdvisors` builds two of them:
one loads the visitor's session into the prompt and stores the new question and answer; the other creates the session
on first use and compacts it when it grows.

```java
ChatClient chat = builder
        .defaultAdvisors(SessionAdvisors.builder(sessions).build())     // every call has memory
        .build();

String answer = chat.prompt()
        .user(q)
        .advisors(SessionAdvisors.session(visitorId))                    // whose session
        .call()
        .content();
```

1. `defaultAdvisors(...)` adds the session advisors to every call this `ChatClient` makes.
2. `SessionAdvisors.session(visitorId)` names the session for this one call. It is **required**: a call without it
   throws an error, on purpose. We tried: `IllegalStateException: No session ID found in advisor context.` A shared default session would silently mix every visitor's conversation together.
3. `sessions.delete(visitorId)` forgets a session completely.

Advisors are Spring AI's main extension point: logging, guardrails and retrieval (chapters 9, 14 and 17) are advisors too.

Spring AI 1.x and 2.0 did this with `MessageChatMemoryAdvisor` and `ChatMemory`; you will still see them in older
code and tutorials. Since 2.1 they are deprecated in favour of sessions, which keep the full log and never split a turn.
:::

:::step{type=task task=session_memory title="Your turn: one session per visitor" file="06-memory/src/main/java/com/atlas/ChatController.java" line="39"}
In `06-memory`, give Atlas memory:

1. In the constructor, add the session advisors, built on the session service, as default advisors:
   `.defaultAdvisors(SessionAdvisors.builder(sessions).build())` before `.build()`.
2. In `chat(...)`, run each call in the visitor's own session: `.advisors(SessionAdvisors.session(visitor))` before
   `.call()`.

The usual slips:

- Forgetting step 2: every call then fails with the "No session ID found" error above.
- `SessionAdvisors.session("visitor")` in quotes: every visitor shares one session called "visitor", and Sam would
  see Ria's name.

```bash run
cd 06-memory && mvn -q -o spring-boot:run
```

```bash run
curl -s -G localhost:8080/chat --data-urlencode visitor=ria --data-urlencode "q=Hi! My name is Ria and I am 9."; echo
curl -s -G localhost:8080/chat --data-urlencode visitor=ria --data-urlencode "q=What is my name, and what would you show someone my age first?"; echo
curl -s -G localhost:8080/chat --data-urlencode visitor=sam --data-urlencode "q=What is my name?"; echo
```

Press **Check**.
:::

:::step{type=try title="Ria and Sam"}
With session memory, the same three questions (our re-run on 25 November: the same results, in other words; Ria was
forgotten after the delete):

```text
$ curl -s -G localhost:8080/chat --data-urlencode visitor=ria --data-urlencode "q=Hi! My name is Ria and I am 9."; echo
Hi Ria! It's great to meet you. Welcome to the Deccan Science Museum! Do you want to know about any exhibits or fun science facts?
$ curl -s -G localhost:8080/chat --data-urlencode visitor=ria --data-urlencode "q=What is my name, and what would you show someone my age first?"; echo
Your name is Ria! For someone your age, I would show you the fun interactive exhibits. They let you explore science in a hands-on way, which is really exciting!
$ curl -s -G localhost:8080/chat --data-urlencode visitor=sam --data-urlencode "q=What is my name?"; echo
I'm sorry, but I am just the guide for the museum and don’t know your name. 
```

Ria's name and age carried over to her second question; Sam's session is empty. And when Ria leaves the screen,
`DELETE /chat/ria` deletes her session:

```text
$ curl -s -X DELETE localhost:8080/chat/ria -o /dev/null -w "%{http_code}\n"
200
$ curl -s -G localhost:8080/chat --data-urlencode visitor=ria --data-urlencode "q=Do you remember my name?"; echo
I'm sorry, but I don't know your name. I'm here to help with questions about the Deccan Science Museum. How can I assist you today?
```

Forgotten, as it should be: a public screen must not show the next visitor what the last one said.
:::

:::step{type=concept title="Compaction: keeping long sessions short"}
A visitor who chats for half an hour builds a long session, and every question then carries all of it. **Compaction**
keeps the view the model sees short. You give the session advisors two things:

- a **trigger**: when to compact. `new TurnCountTrigger(8)` fires when the view holds **more than** 8 turns;
  `TokenCountTrigger` fires on an estimated number of tokens.
- a **strategy**: what to keep. `WindowCompactionStrategy.builder().lastTurns(4).build()` keeps the last 4 turns
  in the view; a summarising strategy replaces older turns with a short summary written by the model.

```java
SessionAdvisors.builder(sessions)
        .compaction(new TurnCountTrigger(8), WindowCompactionStrategy.builder().lastTurns(4).build())
        .build()
```

Compaction never deletes anything: the older events stay in the session's log (for audits, or for search with Spring
AI's recall tool); they just leave the view that is sent to the model.
:::

:::step{type=predict title="Guess first"}
:::question
With a trigger of 8 turns and a window of the last 4, a visitor has asked nine questions. They ask a tenth. What goes
to the model, besides the system prompt?
:::
- [ ] All nine earlier turns and the new question
- [x] The last four turns (questions 6 to 9 with their answers) and the new question
- [ ] Only the new question
:::explain
After the ninth turn the view held more than 8 turns, so the session was compacted to its last 4. The tenth request
carries those 4 turns and the new question, and stays that size however long the conversation runs. We ran ten
questions through the real app and read the tenth request in the gateway's log: the system message, questions 6 to 9
with their answers, and question 10. Nothing else.
:::
:::

:::step{type=task task=memory_window title="Your turn: compact long sessions" file="06-memory/src/main/java/com/atlas/ChatController.java" line="32"}
Give the session advisors a compaction: once a session holds **more than 8 turns**, keep only its **last 4**:

1. On `SessionAdvisors.builder(sessions)`, before `.build()`, add `.compaction(trigger, strategy)`.
2. The trigger: `new TurnCountTrigger(8)`. The strategy: `WindowCompactionStrategy.builder().lastTurns(4).build()`.

The usual slip: swapping the numbers (a trigger of 4 and a window of 8). The view then stays near 8 turns instead of
4, twice the tokens, and the Check counts the difference.

Press **Check**: it holds a ten-question conversation and counts what the tenth request carries.
:::

:::step{type=concept title="Where sessions live"}
`InMemorySessionRepository` keeps sessions in the application's own memory, which suits tests and demos: a restart
forgets every conversation, and two copies of the app behind a load balancer do not
share them. For production there is a JDBC repository:

| Repository | Keeps sessions | Use when |
|---|---|---|
| in memory | in this app's RAM, until restart | one server, demos, tests |
| JDBC (`spring-ai-starter-model-session-jdbc`) | in PostgreSQL, MySQL, MariaDB or H2 (the databases the Spring AI 2.1 reference lists) | several servers, history that must survive restarts |

With the JDBC starter on the class path, Spring Boot creates the `SessionService` for you on the application's
database, and your advisor code stays the same.

**Privacy.** Conversations can contain names, ages, worries. Sessions have an expiry time (60 days by default: we found the 60 in the lab's
Spring AI; set `timeToLive` when you create one), and should be deleted when they are no longer needed. Never log them
carelessly (chapter 18).
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You add the session advisors but forget `SessionAdvisors.session(visitor)` on the call. What happens?
:::
- [ ] Every visitor shares one default conversation
- [x] The call fails with an error: a session id is required on every call
- [ ] Nothing is remembered, silently
:::explain
Spring AI 2.1 refuses to guess, because a shared default session would be a privacy bug: one visitor reading another's
conversation. The error points you to the missing id.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does the model "remember" Ria's name in her second question?
:::
- [ ] The model stored it after the first call
- [x] The session advisor sent her first question and its answer again, inside the second request
- [ ] OpenAI keeps a profile of every user
:::explain
The model itself is stateless. Your application keeps the history and sends it back; the model reads it like any other
part of the prompt.
:::
:::

:::step{type=deep-dive title="Go deeper: summaries, token windows and long memory"}
**Summarise instead of dropping.** A summarising compaction strategy asks the model for a short summary of the older
turns ("Ria, 9, likes space, has seen the pendulum") and keeps it in the view, with the last few turns in full. It costs
one extra model call now and then (`asyncCompaction(true)` makes it happen after the answer is sent), and keeps the
important facts.

**Count tokens, not turns.** Ten one-word turns and ten long ones cost very different amounts.
`TokenCountTrigger` and a window with `tokenBudget(4000)` keep the view within a token budget instead.

**Memory across sessions.** Some assistants remember facts about a person for weeks ("you visited the dinosaur gallery
last month"). That is usually stored as separate facts, retrieved when relevant (the technique of chapter 14), with
the user's clear consent.

**Stateless servers.** Keeping conversations in a shared store means any server can answer any request: the
application itself stays stateless, which is what makes it easy to run many copies of it.
:::

:::step{type=recap}
You can now:

- explain why a model remembers nothing, and how memory works: the history, sent again with every request;
- add session memory with a `SessionService` and `SessionAdvisors`, one session per visitor;
- compact long sessions with a trigger and a window, and delete a session when its visitor leaves;
- choose where sessions live: in memory for demos, JDBC for production.

Next, chapter 7: tools, so Atlas can look up real opening hours and show times instead of saying "I do not know".

:::photo{src="/lesson-images/spring-ai/springai-06-notes.webp" alt="Sketchnote, Conversations that remember (sessions and compaction): The model remembers nothing. The app keeps each visitor's session and sends the recent part again with every question. The flow: Visitor's question, Session advisor adds the history, Model, Answer saved to the session. What we found: every call needs a session id, or it fails; the 10th request sent only turns 6 to 9; old turns stay in the log, out of the view; delete a session when the visitor leaves." ai="true"}
One page of notes for this chapter.
:::
:::
