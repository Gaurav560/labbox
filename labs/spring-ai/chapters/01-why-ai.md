:::step{type=story title="The same twenty questions, every day"}
The **Deccan Science Museum** in Pune has five galleries, a planetarium dome, a Foucault pendulum that proves the
Earth turns, and about forty thousand visitors a month. Most of them, at some point, walk up to the front desk and
ask a question. When does the planetarium show start? Where is the pendulum? Is it open on Monday? Can you explain
this to my seven-year-old?

The two people at the desk are brilliant, and exhausted: they answer the same twenty questions all day, and the
interesting ones ("why does the pendulum turn?") get the least time. The museum wants a guide on its website and on
a screen in the lobby, one that never gets tired, explains science at any level, and knows the museum.

You are going to build it. Its name is **Atlas**, and it is a Spring Boot application that talks to a **large
language model**, the kind of AI behind ChatGPT. By the end of this course Atlas will answer from the museum's own
exhibit cards, call your Java code to check opening hours and show times, remember a visitor's conversation, refuse
to be tricked, stream its answers, and tell you what every answer cost.

The Deccan Science Museum is imaginary, but places like it are real: this is the garden of the Nehru Science Centre in
Mumbai, where a bust of Yuri Gagarin stands among banners about space travel. Places like this are exactly where a
patient, knowledgeable guide turns a visit into an adventure.

:::photo{src="/lesson-images/spring-ai/science-centre.webp" alt="A bust of Yuri Gagarin on a black plinth in a garden, between tall banners about space travel, at the Nehru Science Centre in Mumbai" credit="Viraj" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Nehru_Science_Centre16.JPG"}
At the Nehru Science Centre, Mumbai.
:::

:::mission
Connect Atlas to a language model: one Spring endpoint that sends a visitor's question to the model and returns its
answer.
:::
:::

:::step{type=concept title="What a language model is, in plain words"}
A **large language model** (LLM) is a program that has read an enormous amount of text and learned one skill
extremely well: **given some text, predict what comes next**. Ask "The capital of France is" and it continues
"Paris". Ask a whole question, and it continues with an answer, one small piece at a time.

Those small pieces are called **tokens**. A token is a word or a part of a word: "planetarium" might be two or three
tokens, "the" is one. On average a token is about three quarters of an English word. Tokens matter because they are
how models are **measured and priced**: you pay for the tokens you send and the tokens you get back.

Four facts about LLMs shape everything in this course:

| Fact | What it means for Atlas |
|---|---|
| It predicts likely text, it does not look things up | It can sound sure and be wrong. It does not know your museum unless you tell it. |
| It has no memory between calls | Every call starts from nothing. To hold a conversation, you send the history again (chapter 6). |
| Its answers vary | The same question can get a different answer each time (chapter 3 controls this). |
| It costs money and time per token | Long questions and long answers are slower and dearer (chapters 3 and 13). |

The model does not run on your lab machine: it runs on big servers at a company like **OpenAI**, and you use it the
way you use any web service, by sending an HTTP request and reading the JSON that comes back. Atlas will be a normal
Spring Boot app that, inside some of its endpoints, calls that service.

**Check yourself:** why can Atlas not answer "When does the planetarium show start?" correctly yet? (The model has
never seen the museum's timetable. It predicts text; it cannot know facts nobody gave it.)
:::

:::step{type=history title="From ELIZA to Spring AI"}
People have wanted to talk to computers in plain language for as long as there have been computers.

:::before{title="Before language models"}
In **1966** Joseph Weizenbaum at MIT wrote **ELIZA**, a program that imitated a therapist by turning your sentences
back into questions ("I feel tired." "Why do you feel tired?"). It understood nothing, yet people confided in it, which
alarmed its own author. For fifty years, chatbots worked the same way underneath: hand-written rules, keywords and
decision trees. Every question nobody had planned for got "Sorry, I did not understand that."
:::

This is Joseph Weizenbaum, ELIZA's creator, who spent the rest of his life asking what computers should and should not
be trusted to do.

:::photo{src="/lesson-images/spring-ai/weizenbaum.webp" alt="Joseph Weizenbaum in 1982, with grey hair, glasses and a moustache, in a dark jacket" credit="Rochester Institute of Technology" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Weizenbaum_1982.jpg"}
Joseph Weizenbaum, who wrote ELIZA in 1966.
:::

Here is ELIZA at work, in a modern re-creation of the program. Notice how every answer is built from the visitor's own
words: "my boyfriend made me come here" becomes "your boyfriend made you come here".

:::photo{src="/lesson-images/spring-ai/eliza.webp" alt="A black terminal screen showing a conversation with ELIZA, which answers each sentence with a question built from the user's words" credit="Unknown author (re-creation by Norbert Landsteiner)" license="Public domain" source="https://commons.wikimedia.org/wiki/File:ELIZA_conversation.png"}
A conversation with ELIZA, re-created.
:::

In **2017** eight researchers at Google published a paper with a confident title, **"Attention Is All You Need"**. It
described the **transformer**, a way for a neural network to look at every word of a text at once and weigh how
much each one matters to the others. Transformers trained on huge amounts of text turned out to be astonishingly good
at continuing it. OpenAI's **GPT-3** (2020) wrote whole essays; on **30 November 2022** OpenAI opened **ChatGPT** to the
public, and it reached a hundred million users in about two months, faster than any app before it.

:::solved
**Language as an API.** Today a model that can explain, summarise, translate and plan is one HTTP call away. Every
company suddenly wanted it inside its own applications, and most of those applications are written in Java. In 2023
Mark Pollack and Christian Tzolov at the Spring team started **Spring AI**: the same idea Spring applied to databases
(JDBC, Spring Data) applied to AI. One Java API, `ChatClient`, works with OpenAI, Anthropic, Google, Mistral, local
models and more, so your code does not depend on one company.
:::

:::timeline
- **1966** ELIZA, the first famous chatbot, built from hand-written rules.
- **2017** Google's transformer paper, "Attention Is All You Need".
- **2020** GPT-3 shows that a big enough transformer can write almost anything.
- **2022** ChatGPT opens to the public on 30 November.
- **2023** Spring AI begins, as an experiment in the Spring team.
- **2025** Spring AI 1.0, the first stable release, in May.
- **2026** Spring AI 2.0 on Spring Boot 4; in November, Spring AI 2.1, the version this course uses.
:::

:::usedby{title="Used for"}
- Customer and visitor help desks
- Search that understands questions
- Summaries of long documents
- Assistants inside existing apps
- Turning text into structured data
:::

:::usedby{title="Used by"}
- Banks and insurers on the JVM
- Retail and travel booking sites
- Internal tools at large companies
- Startups building AI features
:::

:::funfact
ELIZA's most famous script, DOCTOR, was so convincing that Weizenbaum's own secretary asked him to leave the room
while she "talked" to it, although she had watched him write the program.
:::
:::

:::step{type=concept title="How Atlas reaches the model"}
Here is the journey of one question, which you will build in this chapter:

:::diagram{name="ai-request-flow"}
The visitor asks Atlas; Atlas builds a prompt with ChatClient; the LabBox gateway passes it to the model; the answer comes back the same way.
:::

1. A visitor's browser calls Atlas: `GET /ask?q=When is the show?`.
2. Atlas's controller uses Spring AI's **`ChatClient`** to build a **prompt** (the text sent to the model).
3. Spring AI turns it into an HTTP request in OpenAI's format and sends it.
4. In LabBox, it goes to the **LabBox gateway**, which holds the real OpenAI key, checks your daily budget and logs
   the call, then forwards it to OpenAI. (In a company, the same job is done by an "AI gateway" or by putting the key
   in a secret store. The rule is the same: **an API key never goes into your code.**)
5. The answer comes back as JSON; Spring AI reads it; your controller returns the text.

Open `01-why-ai/src/main/resources/application.properties`. Three lines connect Spring AI to the gateway:

```properties
spring.ai.openai.base-url=${OPENAI_BASE_URL}
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.openai.chat.options.model=gpt-4o
```

`${OPENAI_BASE_URL}` means "the value of the environment variable OPENAI_BASE_URL". Your lab machine already has
both variables set: the gateway's address, and a key that works only at the gateway, only for you, only in this
course. The third line names the **model**. Hold that thought: it is not right yet.
:::

:::step{type=example title="Worked example: one call, line by line" file="01-why-ai/src/main/java/com/atlas/AskController.java" line="14"}
Open `AskController.java`. Spring Boot has already created a `ChatClient.Builder` for you (the starter
`spring-ai-starter-model-openai` in the `pom.xml` did that), and the constructor builds a `ChatClient` from it:

```java
public AskController(ChatClient.Builder builder) {
    this.chat = builder.build();
}
```

Asking the model something is one fluent chain. Read it aloud, as a sentence:

```java
String answer = chat.prompt()        // start a new prompt
        .user("What is a comet?")    // the visitor's message
        .call()                      // send it, and wait for the whole answer
        .content();                  // just the answer's text
```

1. `prompt()` starts building a request.
2. `.user(...)` adds a **user message**: what the person asked. (Chapter 2 adds a second kind, the system message.)
3. `.call()` sends it and **blocks** until the model has finished. (Chapter 4 streams instead.)
4. `.content()` returns the text of the answer as a `String`. (Chapter 3 shows what else comes back.)

Nothing here mentions OpenAI. Switch the starter in the `pom.xml` to another provider, and this code stays exactly the
same.
:::

:::step{type=task task=first_call title="Your turn: connect /ask to the model" file="01-why-ai/src/main/java/com/atlas/AskController.java" line="20"}
In `AskController.java`, make `GET /ask?q=...` send `q` to the model as the visitor's message, and return the model's
answer instead of the placeholder text.

Then start the app, in Terminal 1:

```bash run
cd 01-why-ai && mvn -q -o spring-boot:run
```

and ask it something, in a second terminal (click **+**):

```bash run
curl -s "localhost:8080/ask?q=Hello%2C%20who%20are%20you%3F"; echo
```

(`%20` is a space and `%3F` a question mark: spaces cannot travel in a web address as they are.) You will see a
500 error for now: read the app's log in Terminal 1, and the next step explains it. Press **Check**: it tests your
code with a pretend model, so it does not need the next step.
:::

:::step{type=try title="The model's name"}
When you run `/ask` with the starter's settings, the app's log shows why it failed:

```text
Request processing failed: com.openai.errors.BadRequestException: 400: Unknown model 'gpt-4o'.
Labs use model aliases: ai-chat, ai-embed, lab-chat, lab-chat-smart, lab-code, lab-embed.
```

(The log prints it on one long line.) The gateway refused the request: `gpt-4o` is a real OpenAI model, but LabBox
gives each course a short list of **aliases**, names that the gateway maps to a real model. This course's chat model is
**`ai-chat`** (behind it is OpenAI's `gpt-4o-mini`: fast, cheap and capable), and its embedding model, which you will
meet in chapter 8, is `ai-embed`.

Aliases are a good habit in real companies too: the code says what it needs ("the chat model"), and one setting
decides which real model that is today. Changing model later then means changing one line, not hunting through code.
:::

:::step{type=task task=model_alias title="Your turn: the right model" file="01-why-ai/src/main/resources/application.properties" line="8"}
In `application.properties`, set `spring.ai.openai.chat.options.model` to this course's chat model alias.

Stop the app (Ctrl+C), start it again, and ask:

```bash run
curl -s "localhost:8080/ask?q=Hello%2C%20who%20are%20you%3F"; echo
```

This time a real model answers. Press **Check**.
:::

:::step{type=try title="Atlas's first words"}
Here is what Atlas said when this lesson was written:

```text
$ curl -s "localhost:8080/ask?q=Hello%2C%20who%20are%20you%3F"; echo
Hello! I’m an AI language model created by OpenAI. I’m here to answer your questions, provide information, and assist you with a variety of topics. How can I help you today?
```

It works, and it is not Atlas yet: it introduces itself as OpenAI's assistant, because nobody told it otherwise. Ask
it a science question, and the answer is long: the first lines of a real answer about black holes looked like this,
and it went on for five numbered sections and about four hundred tokens:

```text
A black hole is a region in space where the gravitational pull is so strong that nothing, not even light, can escape from it. This occurs when a massive star exhausts its nuclear fuel and collapses under its own gravity. 

There are several key characteristics of black holes:
```

Asked the same question a second time, it gave a **different** long answer, with a fifth section the first one did not
have. Too long for a lobby screen, not about the museum, and never quite the same: chapters 2 and 3 fix all three.
Your own answers will differ from these: that is the nature of the model.
:::

:::step{type=predict title="Guess first"}
:::question
You ask Atlas "What is a comet?" twice in a row. What do you get?
:::
- [ ] Exactly the same answer: computers are deterministic
- [x] Two answers that say similar things in different words
- [ ] An error the second time: the model remembers it already answered
:::explain
The model picks each next token with a little randomness, so wording changes from call to call. And it remembers
nothing between calls: the second call is as new to it as the first.
:::
:::

:::step{type=concept title="What it costs, and how long it takes"}
Every answer costs money and time, so engineers estimate both before they ship. The gateway's price list for this
course's model (`gpt-4o-mini`) is **$0.15 per million input tokens** and **$0.60 per million output tokens**.

| Example | Tokens | Cost |
|---|---|---|
| One short question and a three-sentence answer | about 100 in, 60 out | $0.00005 |
| The long black hole answer above | about 15 in, 400 out | $0.00024 |
| 40,000 visitors a month, 3 short answers each | 12 million in, 7 million out | about $6 a month |
| The same, with long answers like the black hole one | 2 million in, 48 million out | about $29 a month |

Cheap, and yet the length of the answers alone changes the bill five times over. Bigger models cost ten to a hundred
times more per token, so the same choices matter far more there.

**Time** matters even more to a person waiting at a screen: a model writes perhaps fifty to a hundred tokens a second,
so a 400-token answer takes several seconds to finish. Short answers (chapter 2), a cap on length (chapter 3) and
streaming (chapter 4) are how Atlas stays quick.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does Atlas read the API key from the environment variable `OPENAI_API_KEY` instead of having it written in
`application.properties`?
:::
- [ ] Spring AI cannot read keys from files
- [x] A key in code or config ends up in Git, in logs and in other people's hands; the environment keeps it out of the code
- [ ] Environment variables make the calls faster
:::explain
Leaked API keys are found by bots within minutes of being pushed to a public repository, and someone else's usage
lands on your bill. Keep keys in the environment or a secret store, never in the code.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In `chat.prompt().user(q).call().content()`, what does `.call()` do?
:::
- [ ] It returns the first token of the answer at once
- [x] It sends the prompt to the model and waits until the whole answer has arrived
- [ ] It saves the question for later
:::explain
`.call()` is the blocking way: one request, one complete answer. Chapter 4's `.stream()` gets the answer as it is
written.
:::
:::

:::step{type=deep-dive title="Go deeper: what really travels over the wire"}
Spring AI hides the HTTP, but it is worth seeing once. For `/ask?q=Hello`, the request Spring AI sends looks like
this (OpenAI's "chat completions" format, which most providers and gateways now accept):

```json
{"messages":[{"content":"Hello","role":"user"}],"model":"ai-chat"}
```

and the answer comes back as JSON with the text in `choices[0].message.content`, plus a `usage` block counting the
tokens. Spring AI 2 uses OpenAI's own Java library underneath to send it.

**Why a framework at all?** You could send that JSON yourself with `RestClient`. Spring AI earns its place when you
need more than one call: switching providers, conversation memory, tools, retrieval, structured output, retries,
metrics. Each is a few lines with Spring AI and a small project without it.

**Running a model yourself.** Open models (Llama, Qwen, Mistral, Gemma) can run on your own servers, for example with
Ollama, which Spring AI also supports. They cost hardware instead of tokens, keep data in-house, and are usually less
capable than the largest hosted models. LabBox's own tutor runs on such a model.
:::

:::step{type=recap}
You can now:

- explain what a large language model is (it predicts the next token), and its four big limits: no knowledge of
  your data, no memory, varying answers, cost per token;
- tell the story from ELIZA (1966) and the transformer (2017) to ChatGPT (2022) and Spring AI;
- configure Spring AI with a base URL, a key from the environment, and a model alias;
- call a model with `chat.prompt().user(q).call().content()`, and estimate what answers cost.

Next, chapter 2: a system prompt that turns a general model into Atlas, the museum's guide.

:::photo{src="/lesson-images/spring-ai/springai-01-notes.webp" alt="Handwritten notes about why AI in your app: an LLM predicts the next token; no memory, no facts of yours; chat.prompt().user(q).call().content(); keys live in the environment; model alias: ai-chat" ai="true"}
One page of notes for this chapter.
:::
:::
