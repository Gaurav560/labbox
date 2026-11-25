:::step{type=story title="A question the model cannot answer"}
Deep in the Western Ghats lies the Vanrai Hills Wildlife Sanctuary: 212 square kilometres of evergreen forest, grassland
and river valley, with tigers, leopards, gaur, sloth bears and a small herd of wild elephants. Forty rangers and guards
look after it. Everything they need to know is written in two places: the **field manual** (31 numbered sections, from
"FM-1.1 The three zones" to "FM-9.2 Radios and phones") and a pile of **patrol reports**.

A new guard on night patrol has a question: *how often do we change the batteries in the camera traps?* The answer is in
section FM-3.2. But it is 2 a.m., the manual is back at the office, and the guard has only a phone.

In this course you build **Fieldbook**, an assistant that answers the rangers' questions from their own documents. You
will build every part of it yourself, by hand first, so that nothing stays magic: finding the right pages, turning text
into numbers, the indexes inside a vector database, and answers that say where they came from. (Vanrai Hills and its
manual are made up for this course; the animals, the forest and the engineering are real.)

Let's start with the obvious idea: just ask a language model.

Some of the manual's most important sections are about this animal: FM-4.2 "Meeting a tiger" tells a guard exactly what
to do when one is close. A wrong answer about it is dangerous, which is why Fieldbook must answer from the manual and
nothing else.

:::photo{src="/lesson-images/rag/tiger.webp" alt="A Bengal tiger walking through dry grass at the edge of a forest, looking towards the camera" credit="Tisha Mukherjee" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ABengal_tiger_in_Sanjay_Dubri_Tiger_Reserve_December_2024_by_Tisha_Mukherjee_11.jpg"}
A Bengal tiger in Sanjay Dubri Tiger Reserve, Madhya Pradesh.
:::
:::mission
See a model answer a question about the sanctuary wrongly, then give it a way to look things up: a keyword search over
the manual, and a prompt that hands it the sections it found.
:::
:::

:::step{type=concept title="What a model knows, and what it does not"}
A **language model** is a program trained to continue text: given some words, it writes the words most likely to come
next. That is how chat assistants like ChatGPT work. It learned by reading a huge amount of public text, up to a
**cut-off date** (the last day of the text it was trained on).

The text you send to a model is called the **prompt**. The model answers from two things only: what it learned in
training, and what is in the prompt. So two kinds of knowledge are missing from it, and Fieldbook needs both:

| Missing | Example | Why the model cannot know |
|---|---|---|
| **Private** | the sanctuary's own field manual | it was never on the public internet, so it was never in the training text |
| **New** | last night's patrol report | it was written after the model's cut-off date |

What does a model do when you ask about something it does not know? Often it does **not** say "I don't know". It writes
the answer that sounds most likely: fluent, confident, and made up. This is called a **hallucination**. For a ranger, a
confident wrong answer about a tiger or a snakebite is worse than no answer at all.

There are two ways to give a model knowledge it does not have:

| Way | How | Good for | Problem |
|---|---|---|---|
| Train it more (**fine-tuning**) | run more training on your own documents | a writing style, a format, a skill | takes time and money, is out of date as soon as a document changes, and cannot say which document an answer came from |
| **Look it up (RAG)** | for each question, find the right passages and put them in the prompt | facts, private documents, things that change | the search has to find the right passages |

The second way is called **retrieval-augmented generation**, or **RAG**. The name is the three steps:

1. **Retrieve:** search your documents for the passages that match the question.
2. **Augment:** add those passages to the prompt, next to the question.
3. **Generate:** the model writes the answer, reading the passages you gave it.

The picture shows the three steps with the question you are about to run, and what really comes out. This whole course
is about doing step 1 well, because the answer can only be as good as the passages it is given.

:::diagram{name="rag-flow"}
RAG for the battery question: the search finds three sections, they go into the prompt with the question, and the model
answers from them, naming FM-3.2. All of it is this chapter's real output.
:::
:::

:::step{type=example title="See it: the model on its own" file="01-why-rag/ask.py" line="9-14"}
Open `01-why-rag/ask.py`. It asks the model the battery question twice. Here is the first time, the question alone:

```python
client = OpenAI()   # LabBox sets OPENAI_BASE_URL and OPENAI_API_KEY: the call goes through the lab's AI gateway

alone = client.chat.completions.create(model="lab-chat", temperature=0,
                                       messages=[{"role": "user", "content": question}])
```

- `OpenAI()` creates a client from the official `openai` Python library. You see no address and no key in the code:
  LabBox puts both in your lab's environment, so every call goes to the lab's **AI gateway**, a small service that
  passes the call to a real model and counts what it costs. You never need your own API key.
- `model="lab-chat"` is a name the gateway knows. It decides which real model answers (in this course, OpenAI's
  gpt-4o-mini). If that ever changes, your code does not have to.
- `temperature=0` asks for the most likely answer each time, so runs stay close to each other. (They can still differ
  slightly; you will see that below.)
- `messages` is the conversation. Here it holds just one message: the question, from the `user`.

Run it:

```bash run
cd /workspace/01-why-rag && python ask.py
```

```text
$ python ask.py
Without the manual:
The frequency of changing batteries in camera traps can vary based on several factors, including:

1. **Type of Batteries**: Alkaline batteries may last a few weeks to a couple of months, while lithium batteries can last significantly longer, sometimes up to a year or more.
...
As a general guideline, it's a good practice to check the batteries every 1-3 months, but you should monitor the specific performance of your camera trap and adjust accordingly. Some users may find they need to change batteries more frequently, while others may go longer between changes. Regular checks will help ensure your camera is always operational.

Traceback (most recent call last):
  File "/workspace/01-why-rag/ask.py", line 16, in <module>
    found = keyword_search(question, load_sections())
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/01-why-rag/fieldbook.py", line 34, in keyword_search
    raise NotImplementedError("task keyword_search")
NotImplementedError: task keyword_search
```

(Shortened with "...": the model listed five factors.)

Read the first answer carefully. It sounds sure of itself, and it is wrong for this sanctuary. The manual says (FM-3.2):
change the batteries **every 21 days**, and swap the memory card at the same visit. The model said "every 1-3 months".
It did not lie on purpose. It has never seen this manual, so it wrote what camera trap batteries *usually* need,
somewhere in the world.

Then the program stopped with an error: `keyword_search` is not written yet. That is your first task.
:::

:::step{type=concept title="Finding sections by their words" file="01-why-rag/fieldbook.py" line="23-34"}
The simplest search there is: **a section is a good match when it shares many words with the question.** Let's build it
from two small pieces of `fieldbook.py`.

**Piece 1: `words(text)`** turns a text into its meaningful words:

```python
def words(text):
    return {w for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower()) if len(w) > 2 and w not in STOPWORDS}
```

Reading it from the inside out:

1. `text.lower()` makes everything lower case, so "Camera" and "camera" count as the same word.
2. `re.findall(...)` cuts the text into words made of letters and digits. The pattern also keeps a hyphen **inside** a
   word, so a camera code like `CT-117` stays one word, `ct-117`, instead of becoming `ct` and `117`.
3. `len(w) > 2` drops words of one or two letters ("a", "we", "do").
4. `w not in STOPWORDS` drops common words like "the", "how", "should" and "what". `STOPWORDS` is a list at the top of
   the file. These words appear in almost every sentence, so they say nothing about the topic.
5. The curly braces make a **set**: a collection where each word appears once and the order does not matter.

```python
>>> words("How often should we change the batteries in the camera traps?")
{'often', 'change', 'batteries', 'camera', 'traps'}
```

**Piece 2: the score.** For each section, count how many of the question's words also appear in the section's title
and text. Two sets have a ready-made operation for "the items in both": `a & b`, the **intersection**. Its length is the
score. Here are four real sections scored for the battery question:

:::trace{title="Four sections scored for the battery question"}
| section | words shared with the question | score |
|---|---|---|
| FM-3.2 Batteries and memory cards | change, batteries, camera | 3 |
| FM-3.1 Camera traps | camera, traps | 2 |
| FM-7.1 Snares and traps | often, traps | 2 |
| FM-4.2 Meeting a tiger | (none) | 0 |
:::

The highest score comes first, and sections with a score of 0 are left out. When two sections score the same (FM-3.1
and FM-7.1 both score 2), they stay in the manual's order, so the same question always gives the same result.

Look at FM-7.1, "Snares and traps". It is about poachers' wire snares, not cameras at all. It scores 2 because it uses
the words "often" and "traps" in another sense. That is the weakness of matching words: a word can match while the
meaning does not. Keep it in mind; you will see the opposite problem in a moment.
:::

:::step{type=task task=keyword_search title="Your turn: find sections by their words" file="01-why-rag/fieldbook.py" line="28-34"}
Write `keyword_search(question, sections, k=3)` in `01-why-rag/fieldbook.py`:

1. Get the question's words once, with `words(question)`.
2. For each section, compute its score: the number of question words that also appear in
   `words(section["title"] + " " + section["text"])`. Use the set intersection `a & b`, and `len(...)` for the count.
3. Leave out sections that score 0.
4. Sort the rest best first. To keep equal scores in the manual's order, remember each section's position with
   `enumerate`, and sort by score (highest first), then by position (lowest first).
5. Return the first `k` sections: the section dicts themselves, not their scores.

Press **Check**. If the check says the order is wrong, look at how you break ties: two sections with the same score must
keep the manual's order.
:::

:::step{type=history title="Finding the right page, from card catalogues to RAG"}
:::before{title="Libraries of cards"}
For most of history, finding information meant a librarian, a card catalogue, and a subject heading that somebody had
chosen by hand. If your words were not the cataloguer's words, you did not find the book.
:::

In the **1950s** Hans Peter Luhn at IBM had computers read the text itself: count the words in a document, and let the
important ones index it. In the **1960s** Gerard Salton, first at Harvard and then at Cornell, built **SMART**, a
retrieval system that treated every document and every question as a list of word counts, a **vector**, and ranked
documents by how closely their vector pointed the same way as the question's. In **1972** Karen Spärck Jones showed that
rare words deserve more weight than common ones, an idea every search engine still uses (you will use it in chapter 9).
Web search grew from these ideas in the **1990s**.

Then language models arrived: fluent, but unaware of anything outside their training text. In **2020** Patrick Lewis and
his colleagues at Facebook AI Research, University College London and New York University joined the two worlds in a
paper called *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*: a retriever finds passages, and a
generator writes the answer from them. After ChatGPT appeared in **November 2022**, RAG became the standard way to make
a model answer from a company's own documents.

:::solved
**Answers from your documents, not from the model's memory.** Change a document and the next answer changes with it: no
training, and every answer can point to its source.
:::

:::timeline
- **1950s** Luhn: computers index text by its words.
- **1960s** Salton's SMART: documents and questions as vectors.
- **1972** Spärck Jones: rare words weigh more.
- **2020** The RAG paper (Lewis and others).
- **2022** ChatGPT; RAG becomes everyday engineering.
:::

:::usedby{title="Used for"}
- Help desks that answer from a company's manuals
- Search over internal wikis, tickets and contracts
- Assistants for doctors and lawyers over their own literature
- Code assistants that read your repository
:::

:::funfact
Patrick Lewis has said that he and his co-authors would have put more thought into the name if they had known how widely
"RAG" would be used.
:::

This is the problem keyword search inherits. In a subject catalogue like this one, every book is filed under headings a
librarian chose. Look under "big cats" when the librarian wrote "tigers", and you open the wrong drawer. Your search
has the same weakness, as you will see in a moment.

:::photo{src="/lesson-images/rag/card-catalogue.webp" alt="Rows of wooden drawers with labels, one pulled out to show packed index cards" credit="Dr. Marcus Gossler" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File%3ASchlagwortkatalog.jpg"}
The subject catalogue of the University Library of Graz.
:::
:::

:::step{type=concept title="Augmented: the sections go into the prompt" file="01-why-rag/fieldbook.py" line="37-47"}
Finding the sections is the first half of RAG. The second half is giving them to the model, and that is nothing more
mysterious than putting text in the prompt.

A request to a chat model is a list of **messages**. Each message has a **role** that says who it comes from:

| Role | Holds | In Fieldbook |
|---|---|---|
| `system` | the rules the assistant must follow | `SYSTEM`: answer only from the sections, in at most three sentences, name the section used, and say so when the manual does not cover the question |
| `user` | what the person asks | the sections found, then the question |

Here is `SYSTEM`, from the top of `fieldbook.py`:

```python
SYSTEM = ("You are Fieldbook, the assistant for rangers of the Vanrai Hills Wildlife Sanctuary. Answer only from the "
          "manual sections you are given, in at most three sentences, and name the section you used, like [FM-4.2]. "
          "If the sections do not answer the question, say that the manual does not cover it.")
```

Each rule has a reason. "Answer only from the sections" stops the model mixing in what it remembers. "Name the section"
lets a ranger check the answer. "Say the manual does not cover it" gives the model an honest way out, instead of making
something up.

The `user` message that `build_prompt` makes looks like this (shortened):

```text
Manual sections:

[FM-3.2] Batteries and memory cards
Change the batteries of every camera trap every 21 days, and swap the memory card at the same visit. ...

[FM-3.1] Camera traps
The sanctuary runs 60 camera traps, numbered CT-101 to CT-160, ...

Question: How often should we change the batteries in the camera traps?
```

Each section starts with its number in square brackets. That is what lets the model write `[FM-3.2]` after its answer,
and what lets you, or a ranger, open that section and check.
:::

:::step{type=task task=context_prompt title="Your turn: put the sections in the prompt" file="01-why-rag/fieldbook.py" line="42-47"}
Write `build_prompt(question, sections)` in `01-why-rag/fieldbook.py`. Return a list of two message dicts:

1. `{"role": "system", "content": SYSTEM}`
2. `{"role": "user", "content": ...}`, where the content is, in this order:
   - the line `Manual sections:`
   - for every section, `[FM-3.2] Batteries and memory cards` on one line and its text on the next
   - finally, `Question: ` followed by the question

   with a blank line between each of these pieces.

`"\n\n".join(pieces)` joins a list of strings with a blank line between them, so build a list of the pieces and join it
once. Inside one section, title and text are separated by a single `"\n"`.

Press **Check**, then run `ask.py` again:

```bash run
cd /workspace/01-why-rag && python ask.py
```
:::

:::step{type=try title="The same question, with the manual"}
```text
$ python ask.py
Without the manual:
The frequency of changing batteries in camera traps can vary based on several factors, including the type of batteries used, the camera trap model, the settings (such as trigger speed and video length), and environmental conditions. Here are some general guidelines:
...
Keyword search found: ['FM-3.2', 'FM-3.1', 'FM-7.1'] 

With the manual:
You should change the batteries of every camera trap every 21 days. [FM-3.2]
```

(Shortened with "...": the first answer was a long list again, ending with "some users recommend changing batteries
every 1-3 months". It was not word for word the same as last time: even at `temperature=0`, a model's answers can vary
a little from run to run.)

Same model, same question. The only difference is the text you added to the prompt, and now the answer is right and
names its section. That is the whole idea of RAG.

Notice the search found FM-7.1, "Snares and traps", as you predicted from the trace. It did no harm: the model ignored
it, because FM-3.2 answered the question. With more documents, though, wrong sections can crowd out the right one.

Now try a question in a ranger's own words:

```bash run
cd /workspace/01-why-rag && python ask.py "A big cat is watching me. What now?"
```

```text
$ python ask.py "A big cat is watching me. What now?"
Without the manual:
If you find yourself being watched by a big cat, such as a mountain lion or a leopard, it's important to stay calm and take the following steps:

1. **Do Not Run**: Running may trigger the cat's instinct to chase. Instead, stand your ground.

2. **Make Yourself Look Bigger**: Raise your arms, open your jacket, or hold your backpack above your head to appear larger.
...
6. **Prepare to Defend Yourself**: If the cat approaches aggressively, be ready to defend yourself. Look for anything you can use as a weapon, such as a stick or rocks.
...
Keyword search found: [] 

With the manual:
The manual does not cover this.
```

(Shortened with "...".) Two lessons in one run.

**Without the manual**, the model gives general advice that is written for mountain lions in North America: look
bigger, prepare to fight. The sanctuary's tiger procedure, FM-4.2, is different: stand still, keep facing the tiger,
back away slowly, and leave it a way out. A plausible answer can still be the wrong one for your situation.

**With the manual**, keyword search looked for "big", "cat", "now" and "watching". The manual says *tiger* and
*leopard*, never "big cat", so no section shared a word, nothing was found, and the model, following its rules, said the
manual does not cover it. Honest, but useless.

Phrase it a little differently, "What should I do about a big cat right ahead of me?", and it gets worse in another way:
keyword search finds FM-4.7 (Elephants) and FM-5.3 (Fighting a ground fire) because they contain "ahead", and FM-8.2
(Helping a claim) because it contains "about". None of them is about big cats, and the model again says the manual does
not cover it.

So keyword search fails in both directions: it misses the right section when the words differ, and it finds wrong
sections when a word happens to match. A ranger does not talk the way the manual is written. Chapter 2 fixes this with
search by **meaning**.
:::

:::step{type=predict title="Guess first"}
:::question
A ranger asks "When does the monsoon closure end?" Which section will keyword search put first?
:::
- [x] FM-6.5 The monsoon closure: it shares "monsoon" and "closure" with the question
- [ ] FM-5.1 The fire season, because both are about seasons
- [ ] None: questions about dates cannot be searched
:::explain
"When", "does" and "the" are dropped as common words; "monsoon", "closure" and "end" remain. FM-6.5 shares two of them
and comes first. Two other sections, FM-1.3 and FM-2.3, follow because they contain the word "end". Keyword search
works well when the question uses the document's own words.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does RAG put the sections in the prompt instead of training the model on the manual?
:::
- [ ] Training is impossible for small documents
- [x] The manual changes and reports arrive daily; a prompt uses the current text at once, and the answer can cite it
- [ ] Models cannot learn facts
:::explain
Fine-tuning is good for style and skills. For facts that change, looking them up at question time costs less and is
always up to date.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What happens when retrieval finds the wrong sections?
:::
- [ ] The model notices and searches again
- [x] The model answers from the wrong sections, or says the manual does not cover it: the answer can only be as good as the search
- [ ] Nothing, the model knows the manual anyway
:::explain
That is why most of this course is about retrieval: the model can only use what it is given.
:::
:::

:::step{type=deep-dive title="Go deeper: RAG in the real world"}
**Models can read long prompts now, so why search?** Many current models accept hundreds of pages in one prompt.
Sending the whole manual with every question would work for 31 sections, but you pay for every word of it on every
question, answers get slower, and studies show that many models pay less attention to the middle of a very long prompt
(chapter 11 shows it). For a library of thousands of documents it is not possible at all. Retrieval sends only the few
passages that matter.

**Where RAG goes wrong.** Most failures are retrieval failures: the right passage was not found, was cut in half, or
was pushed down by a similar wrong one. The rest are generation failures: the model ignored the passage or mixed it with
what it remembered. Chapters 2 to 10 work on the first kind, chapter 11 on the second, and chapter 12 measures both.

**Privacy.** The model sees only what you put in the prompt. The search runs on your own machine (from chapter 2, so do
the embeddings), so a document the question does not need never leaves it.
:::

:::step{type=recap}
You can now:

- explain why a model cannot answer from private or new documents, and what a hallucination is;
- say what retrieval-augmented generation is: retrieve, augment, generate;
- search sections by the words they share with a question, and see it fail both ways: missing the right section, and
  finding wrong ones;
- build a prompt that hands the model numbered sections to answer from, with rules that keep it honest.

Next, chapter 2: turning text into numbers that capture meaning.

:::photo{src="/lesson-images/rag/rag-01-notes.webp" alt="Handwritten notes about why RAG: A model knows only its training text and your prompt. It cannot know private or new documents. RAG: retrieve, augment, generate. Keyword search matches words, not meaning. Big cat finds nothing: the manual says tiger. The answer is only as good as the search." ai="true"}
One page of notes for this chapter.
:::
:::
