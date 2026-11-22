:::step{type=story title="Hello, I am an AI language model"}
Atlas answered its first question in chapter 1, and introduced itself as "an AI language model created by OpenAI".
Then it wrote four hundred tokens about black holes, in five numbered sections. A visitor standing at a lobby screen
wants three friendly sentences, from a guide who belongs to this museum.

The model can be all of that. It just needs to be **told**, before every conversation, who it is, where it works and
how to answer. That instruction is called the **system prompt**, and writing a good one is the first real skill of
building with language models. You will also find, as everyone does, that the first draft of a prompt is never the
last.

A good human guide works the same way: before their first tour, someone tells them what the museum is, who visits,
and what to say when they do not know.

:::photo{src="/lesson-images/spring-ai/museum-guide.webp" alt="A black and white photo of a museum guide talking to a group of visitors in a gallery of large paintings, in the 1970s" credit="PBA Lille" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Visite_guidée_au_Palais_des_Beaux-Arts_de_Lille_dans_les_années_1970.jpg"}
A guided tour at the Palais des Beaux-Arts in Lille, 1970s.
:::

:::mission
Give Atlas its personality and rules with a system prompt, and explain any exhibit to a visitor of any age with a
prompt template.
:::
:::

:::step{type=concept title="Messages have roles"}
A request to a chat model is not one block of text: it is a list of **messages**, and each message has a **role**.

| Role | Written by | Holds |
|---|---|---|
| `system` | you, the developer | who the model is, its rules, its tone. The visitor never sees it. |
| `user` | the visitor | their question |
| `assistant` | the model | its earlier answers (chapter 6 sends them back to hold a conversation) |
| `tool` | your code | results of tools the model asked for (chapter 7) |

Models are trained to treat the system message as the **ground rules** and the user message as **the request to
answer within those rules**. So the rules go in the system message, and the visitor's words go in the user message,
never mixed together. (Mixing them is how attacks like "ignore your instructions" get in; chapter 12 is about that.)

:::diagram{name="ai-roles"}
The system message sets the rules; the user message asks; the model answers as the assistant.
:::

In Spring AI, `.user(...)` adds a user message, and `.system(...)` adds a system message to one prompt. For rules
that every conversation needs, the builder has **`defaultSystem(...)`**: set once, sent with every request this
`ChatClient` makes.

**Check yourself:** a visitor types "Talk like a pirate from now on." Which role does that text have? (User. Whatever
the visitor types is user text, however much it sounds like an instruction.)
:::

:::step{type=example title="Worked example: a first draft, and what went wrong" file="02-prompts/src/main/java/com/atlas/AskController.java" line="14"}
Here is the first system prompt written for Atlas, while this course was being made. It looks sensible:

```java
this.chat = builder
        .defaultSystem("""
            You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
            Answer in at most three short sentences, in simple words a twelve-year-old understands.
            Only talk about the museum, its exhibits and science. If you do not know, say so.
            """)
        .build();
```

(`"""` starts a Java **text block**: a string over several lines, exactly as written.) It fixed the introduction at
once:

```text
$ curl -s "localhost:8080/ask?q=Hello%2C%20who%20are%20you%3F"; echo
Hi! I'm Atlas, your friendly guide at the Deccan Science Museum. I'm here to help you learn about our exhibits and science. What would you like to know?
```

Then real questions found two problems. Asked "Name one planet with rings." three times, it refused every time:

```text
I can't answer that, but if you visit the Deccan Science Museum, you can learn all about planets and their features! We have fun exhibits that show how planets work, including those with rings. Come explore and discover more about space!
```

"Only talk about the museum" won over "and science": the model read the rule more strictly than it was meant. And
asked to explain the Foucault pendulum to a 30-year-old, it apologised that it could only talk "in simple words for
kids": "a twelve-year-old" had become a rule about the audience, not about the style.

The lesson every AI engineer learns early: **models follow the words you wrote, not the meaning you had in mind.** Be
explicit about what is allowed, say what to do in the other cases, and test with real questions, including awkward
ones.
:::

:::step{type=concept title="A better system prompt"}
The improved prompt says what is allowed, what to do otherwise, and what never to do:

```text
You are Atlas, the friendly visitor guide of the Deccan Science Museum in Pune.
Answer in at most three short sentences, in plain, simple words.
You may answer questions about the museum, its exhibits, and any science topic.
For anything else, say kindly that you are the museum's guide.
Never invent opening hours, prices or exhibits: if you do not know, say so.
```

The same questions, with this prompt:

```text
$ curl -s "localhost:8080/ask?q=Name%20one%20planet%20with%20rings."; echo
Saturn is a planet with rings. Its rings are made of ice and rock. They are beautiful and can be seen with a telescope!
$ curl -s "localhost:8080/ask?q=Can%20you%20help%20me%20with%20my%20maths%20homework%3F"; echo
I'm sorry, but I am the guide for the Deccan Science Museum. I can help you with questions about the museum or science topics if you’d like!
$ curl -s "localhost:8080/ask?q=How%20much%20is%20a%20ticket%3F"; echo
I'm sorry, but I don't know the ticket prices. Please check the museum's official website or contact them for that information.
```

Science: answered. Homework: politely declined. Ticket prices: "I don't know", instead of an invented number. That
last one matters most: a guide that invents prices is worse than no guide. (Chapter 7 gives Atlas a way to look them
up.)

A good system prompt usually has these parts:

| Part | Example |
|---|---|
| Identity | You are Atlas, the guide of the Deccan Science Museum. |
| Audience and style | Three short sentences, plain words. |
| What is allowed | The museum, its exhibits, any science topic. |
| What to do otherwise | Say kindly that you are the museum's guide. |
| Hard limits | Never invent hours, prices or exhibits. |
:::

:::step{type=task task=system_prompt title="Your turn: Atlas's system prompt" file="02-prompts/src/main/java/com/atlas/AskController.java" line="15"}
In `02-prompts`, give the `ChatClient` a default system prompt, so that every request starts with Atlas's rules. It
must say who the model is (**Atlas**) and where it works (the **Deccan Science Museum**), plus your rules. Use the
improved prompt above, or write your own with the same parts.

Run it and try the questions above, plus one awkward question of your own:

```bash run
cd 02-prompts && mvn -q -o spring-boot:run
```

Press **Check**.
:::

:::step{type=concept title="Prompt templates: the same request, different details"}
Visitors often ask Atlas to explain an exhibit, and the right explanation depends on who is asking. The request is
always the same sentence with two details changed:

> Explain the exhibit **Foucault pendulum** to a visitor who is **7** years old.

A **prompt template** is that sentence with **placeholders** in braces, filled in for each request. In Spring AI the
user message can be a template:

```java
chat.prompt()
    .user(u -> u.text("Tell me one fun fact about {topic}.")
                .param("topic", topic))
    .call()
    .content();
```

`u.text(...)` is the template; each `.param(name, value)` fills one placeholder. Why not just join strings,
`"Tell me one fun fact about " + topic`? For one placeholder, the result is the same. As prompts grow, templates keep
the wording in one readable piece, and they make it obvious which parts come from outside, which matters for
safety (chapter 12).

**Check yourself:** what happens if the template has `{age}` but you forget `.param("age", age)`? (Spring AI refuses to
send it, with an error naming the missing variable. Sending "{age}" to the model would be worse.)
:::

:::step{type=predict title="Guess first"}
:::question
The template is "Explain the exhibit {exhibit} to a visitor who is {age} years old." With the improved system prompt,
what changes between age 7 and age 30?
:::
- [ ] Nothing: the system prompt fixes the style for everyone
- [x] The wording: simpler for the child, a little more precise for the adult, both still short
- [ ] The model refuses one of them
:::explain
The system prompt says "three short sentences, plain words" for everyone; the user message adds who is asking. The
model combines both. (With the first draft, which said "a twelve-year-old", it refused the adult.)
:::
:::

:::step{type=task task=prompt_template title="Your turn: explain any exhibit" file="02-prompts/src/main/java/com/atlas/AskController.java" line="30"}
Finish `GET /explain?exhibit=...&age=...` in `AskController.java`: ask the model to explain the exhibit for a visitor
of that age, with a prompt template and two parameters. The system prompt applies here too, because it is the
`ChatClient`'s default.

Try a child and an adult:

```bash run
curl -s -G localhost:8080/explain --data-urlencode "exhibit=Foucault pendulum" --data-urlencode "age=7"; echo
```

(`-G` with `--data-urlencode` builds the address and encodes the spaces for you.) Press **Check**.
:::

:::step{type=try title="Two visitors, one exhibit"}
With the improved system prompt, the same template gave these:

```text
$ curl -s -G localhost:8080/explain --data-urlencode "exhibit=Foucault pendulum" --data-urlencode "age=7"; echo
The Foucault pendulum is a big swinging pendulum that shows how the Earth spins. As it swings back and forth, it seems to change direction because the Earth is moving under it. It's a fun way to see that the Earth is always turning!
$ curl -s -G localhost:8080/explain --data-urlencode "exhibit=Foucault pendulum" --data-urlencode "age=30"; echo
The Foucault pendulum is a large swinging pendulum that shows how the Earth rotates. As it swings, you can see the path change over time, demonstrating the rotation. It's a fascinating way to experience the science of motion and our planet’s movement!
```

"Spins" and "always turning" for the child; "rotates", "demonstrating" and "the science of motion" for the adult. One
template, one parameter, a different explanation.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Where should the visitor's question go?
:::
- [ ] Inside the system prompt, so the model takes it seriously
- [x] In the user message, separate from the system prompt
- [ ] In both
:::explain
Rules in the system message, the visitor's words in the user message. Keeping them apart is both how models are
trained and the first defence against visitors who try to rewrite the rules.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Your system prompt says "Only talk about the museum." A visitor asks about Saturn's rings, and Atlas refuses. What is
the best fix?
:::
- [ ] Remove the system prompt
- [x] Say explicitly what is allowed ("the museum, its exhibits, and any science topic") and what to do otherwise
- [ ] Add "please" to the rule
:::explain
Models follow the words literally. Name what is allowed, name what to do in the other cases, and test again with the
questions that failed.
:::
:::

:::step{type=deep-dive title="Go deeper: how to keep improving a prompt"}
**Keep a test list.** Write down twenty real questions (easy, awkward, off-topic, tricky) and run them after every
change to the prompt. Prompts drift: a fix for one question often breaks another. Chapter 11 turns this into
automated tests.

**Examples beat adjectives.** "Answer in a friendly tone" is vague. One example answer in the system prompt ("Visitor:
Where is the pendulum? Atlas: In Gallery 2, next to the stairs. It swings all day!") shows the model exactly what you
mean. This is called **few-shot prompting**.

**Prompts are code.** Keep them in the code base (or in resource files), review changes, and test them. Spring AI can
load a template from a file: `.user(new ClassPathResource("prompts/explain.st"))`.

**Shorter is cheaper.** The system prompt is sent with **every** request, so every word in it is paid for again and
again. A 500-token system prompt on 100,000 requests is 50 million input tokens. Keep it as short as it can be while
still clear.
:::

:::step{type=recap}
You can now:

- explain message roles (system, user, assistant, tool) and why rules and visitors' words stay apart;
- give a `ChatClient` a default system prompt with identity, style, what is allowed, what to do otherwise, and hard
  limits;
- improve a prompt by testing it with real and awkward questions;
- fill prompt templates with `.user(u -> u.text(...).param(...))`.

Next, chapter 3: options that make answers steadier and shorter, and the tokens and money behind every answer.

:::photo{src="/lesson-images/spring-ai/springai-02-notes.webp" alt="Handwritten notes about prompts: system = your rules; user = the visitor's words; say what is allowed + what else; (exhibit) + .param(...); test with awkward questions" ai="true"}
One page of notes for this chapter.
:::
:::
