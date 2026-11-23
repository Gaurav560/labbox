:::step{type=story title="A question the model cannot answer"}
Deep in the Western Ghats lies the Vanrai Hills Wildlife Sanctuary: 212 square kilometres of evergreen forest, grassland
and river valley, with tigers, leopards, gaur, sloth bears and a small herd of wild elephants. Forty rangers and guards
look after it. Everything they need to know is written in two places: the **field manual** (31 numbered sections, from
"FM-1.1 The three zones" to "FM-9.2 Radios and phones") and a pile of **patrol reports**.

A new guard on night patrol has a question: *how often do we change the batteries in the camera traps?* The answer is in
section FM-3.2. But it is 2 a.m., the manual is back at the office, and the guard has a phone.

In this course you build **Fieldbook**, the assistant that answers the rangers' questions from their own documents. You
will build every part of it yourself, by hand first, so that nothing stays magic: finding the right pages, turning text
into numbers, the indexes inside a vector database, and answers that say where they came from.

Let's start with the obvious idea: just ask a language model.


A Bengal tiger in a tiger reserve in central India: the animal behind some of the most important sections of the manual.

:::photo{src="/lesson-images/rag/tiger.webp" alt="A Bengal tiger walking through dry grass at the edge of a forest, looking towards the camera" credit="Tisha Mukherjee" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ABengal_tiger_in_Sanjay_Dubri_Tiger_Reserve_December_2024_by_Tisha_Mukherjee_11.jpg"}
A Bengal tiger in Sanjay Dubri Tiger Reserve, Madhya Pradesh.
:::
:::mission
See a model answer a question about the sanctuary wrongly, then give it a way to look things up: a keyword search over
the manual, and a prompt that hands it the sections it found.
:::
:::

:::step{type=concept title="What a model knows, and what it does not"}
A language model learned from a huge amount of public text, up to a cut-off date. Two kinds of knowledge are missing from
it, and Fieldbook needs both:

| Missing | Example | Why the model cannot know |
|---|---|---|
| **Private** | the sanctuary's own field manual | it was never on the public internet |
| **New** | last night's patrol report | it was written after the model was trained |

When you ask about something it does not know, a model rarely says "I don't know". It writes the most likely-sounding
answer: fluent, confident, and made up. People call this a **hallucination**. For a ranger, a confident wrong answer about
a tiger or a snakebite is worse than no answer at all.

There are two ways to give a model knowledge:

| Way | How | Good for | Problem |
|---|---|---|---|
| Train it again (fine-tuning) | days of computing on your documents | style, format, a skill | slow and costly, out of date the next day, no sources |
| **Look it up (RAG)** | find the right passages for each question, put them in the prompt | facts that change, private documents | the search has to be good |

The second way is called **retrieval-augmented generation**, RAG for short: *retrieve* the right passages, *augment* the
prompt with them, let the model *generate* the answer. This whole course is about doing that well.

:::diagram{name="rag-flow"}
A question goes to the search first; only the sections it finds, and the question, reach the model.
:::
:::

:::step{type=example title="See it: the model on its own" file="01-why-rag/ask.py" line="9-14"}
`ask.py` asks the question twice. First, the question alone. `OpenAI()` needs no address or key in the code: LabBox sets
both for your lab, so the call goes to the model through the lab's AI gateway.

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

Read the first answer carefully. It sounds sure of itself. The manual says something quite different (FM-3.2: **every 21
days**, with the memory card swapped at the same visit), not "every 1-3 months". The model did not lie on purpose: it has never seen this manual, so it
wrote what camera trap batteries *usually* need.

Then the program stopped: `keyword_search` is not written yet. That is your first task.
:::

:::step{type=concept title="Finding sections by their words" file="01-why-rag/fieldbook.py" line="23-34"}
The simplest search there is: a section is a good match when it shares many words with the question.

`words(text)` turns a text into its meaningful words: lower case, punctuation gone, short and common words (`the`, `how`,
`do`, `we`) dropped, because they appear everywhere and say nothing about the topic:

```python
>>> words("How often do we change the batteries in the camera traps?")
{'often', 'change', 'batteries', 'camera', 'traps'}
```

Codes like `CT-117` stay whole (the pattern keeps hyphens inside a word). Then for every section, count the question's
words that also appear in the section's title and text:

:::trace{title="Three sections scored for the battery question"}
| section | shared words | score |
|---|---|---|
| FM-3.1 Camera traps | camera, traps | 2 |
| FM-3.2 Batteries and memory cards | change, batteries, camera | 3 |
| FM-4.2 Meeting a tiger | (none) | 0 |
:::

Highest score first, zeros left out. Two sections with the same score keep the manual's order, so the result is always the
same for the same question.
:::

:::step{type=task task=keyword_search title="Your turn: find sections by their words" file="01-why-rag/fieldbook.py" line="28-34"}
Write `keyword_search(question, sections, k=3)`:

1. Get the question's words once with `words(question)`.
2. For each section, count how many of them appear in `words(section["title"] + " " + section["text"])`. A set
   intersection, `a & b`, gives the shared ones.
3. Leave out sections with a score of 0, sort the rest best first (equal scores in the manual's order), and return the
   first `k` sections (the dicts themselves).

Remember `enumerate` gives you each section's position, which settles ties. Press **Check**.
:::

:::step{type=history title="Finding the right page, from card catalogues to RAG"}
:::before{title="Libraries of cards"}
For most of history, finding information meant a librarian, a card catalogue and a subject heading somebody had chosen
by hand. If your words were not the cataloguer's words, you did not find the book.
:::

In the **1950s** Hans Peter Luhn at IBM had computers read the text itself: count the words, and let the important ones
index the document. In the **1960s** Gerard Salton at Cornell built **SMART**, a retrieval system that treated every
document and every question as a list of word counts, a **vector**, and ranked documents by how closely the vectors
pointed the same way. Karen Spärck Jones showed in **1972** that rare words deserve more weight than common ones, an idea
every search engine still uses (chapter 9). Web search grew from these ideas in the **1990s**.

Then language models arrived, fluent but unaware of anything outside their training. In **2020** Patrick Lewis and his
colleagues at Facebook AI Research, University College London and New York University joined the two worlds in a paper
called *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*: a retriever finds passages, a generator writes
the answer from them. After ChatGPT (**November 2022**), RAG became the standard way to make a model answer from a
company's own documents.

:::solved
**Answers from your documents, not from memory.** Change a document and the next answer changes with it: no training,
and every answer can point to its source.
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
- Assistants for doctors and lawyers over their literature
- Code assistants that read your repository
:::

:::funfact
Patrick Lewis has said that he and his co-authors would have put more thought into the name if they had known how widely
"RAG" would be used.
:::

A subject catalogue: every card filed under a heading that a librarian chose. If your words were not the librarian's, you looked in the wrong drawer.

:::photo{src="/lesson-images/rag/card-catalogue.webp" alt="Rows of wooden drawers with labels, one pulled out to show packed index cards" credit="Dr. Marcus Gossler" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File%3ASchlagwortkatalog.jpg"}
The subject catalogue of the University Library of Graz.
:::
:::

:::step{type=concept title="Augmented: the sections go into the prompt" file="01-why-rag/fieldbook.py" line="37-47"}
Finding the sections is half of RAG. The other half is giving them to the model, and that is nothing more mysterious than
text in a prompt. A chat request is a list of **messages**, each with a role:

| Role | Holds | Here |
|---|---|---|
| `system` | the rules for the assistant | `SYSTEM`: answer only from the sections, name the section used, admit when the manual does not cover it |
| `user` | what the person asks | the sections found, then the question |

The user message `build_prompt` makes looks like this (shortened):

```text
Manual sections:

[FM-3.2] Batteries and memory cards
Change the batteries of every camera trap every 21 days, and swap the memory card at the same visit. ...

[FM-3.1] Camera traps
The sanctuary runs 60 camera traps, numbered CT-101 to CT-160, ...

Question: How often should we change the batteries in the camera traps?
```

Each section starts with its number in square brackets, so the model can say which one it used, and you can check it.
:::

:::step{type=task task=context_prompt title="Your turn: put the sections in the prompt" file="01-why-rag/fieldbook.py" line="42-47"}
Write `build_prompt(question, sections)`. Return a list of two message dicts:

1. `{"role": "system", "content": SYSTEM}`
2. a `user` message whose content is `"Manual sections:"`, a blank line, then every section as
   `[FM-3.2] Batteries and memory cards` on one line and its text on the next, sections separated by a blank line, and
   finally `"Question: "` and the question.

`"\n\n".join(...)` puts a blank line between pieces. Press **Check**, then run `ask.py` again:

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
every 1-3 months". Notice it was not word for word the same as last time: a model's answers vary from run to run.)

Same model, same question. The only difference is the text you added to the prompt, and now the answer is right and
names its section. That is the whole idea of RAG.

Now try a question in your own words:

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

(Shortened with "...".) Two lessons in one run. **Without the manual**, the model gives general advice written for
mountain lions in North America: look bigger, prepare to fight. The sanctuary's tiger procedure (FM-4.2) is different:
stand still, keep facing it, back away slowly, leave it a way out. A plausible answer can still be the wrong one for
your situation.

**With the manual**, keyword search looked for "big", "cat", "now" and "watching". The manual says *tiger* and
*leopard*: no shared word, nothing found, and the model, following its instructions, said the manual does not cover it.
Honest, but useless. Phrase it slightly differently ("What should I do about a big cat right ahead of me?") and keyword
search finds FM-4.7, FM-5.3 and FM-8.2 (elephants, fire fighting and compensation claims) through the words "ahead",
"right" and "about"; the model again says the manual does not cover it.

A ranger does not talk the way the manual is written. Chapter 2 fixes this with search by **meaning**.
:::

:::step{type=predict title="Guess first"}
:::question
A ranger asks "When does the monsoon closure end?" Which section will keyword search put first?
:::
- [x] FM-6.5 The monsoon closure: it shares "monsoon" and "closure" in its title and text
- [ ] FM-5.1 The fire season, because both are about seasons
- [ ] None: questions about dates cannot be searched
:::explain
"When", "does" and "the" are dropped as common words; "monsoon", "closure" and "end" remain, and FM-6.5 has the first two.
Keyword search works well when the question uses the document's own words.
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
Fine-tuning teaches style and skills; for facts that change, looking them up at question time is cheaper and stays current.
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
That is why most of this course is about retrieval: the generation step is only as good as what it is given.
:::
:::

:::step{type=deep-dive title="Go deeper: RAG in the real world"}
**Context windows are big now, so why search?** Today's models accept hundreds of pages in one prompt. Sending the whole
manual every time works for a 31-section manual, but you pay for every token on every question, answers get slower, and
models attend less carefully to the middle of very long prompts. For a library of thousands of documents it is not
possible at all. Retrieval sends the few passages that matter.

**Where RAG goes wrong.** Most failures are retrieval failures: the right passage was not found, was cut in half, or was
outranked by a similar wrong one. The rest are generation failures: the model ignored the passage or mixed it with what it
remembered. Chapters 2 to 10 work on the first kind, chapter 11 on the second, chapter 12 measures both.

**Privacy.** The model sees only what you put in the prompt. The search runs on your own machine (from chapter 2, even the
embeddings do), so a document the question does not need never leaves it.
:::

:::step{type=recap}
You can now:

- explain why a model cannot answer from private or new documents, and what a hallucination is;
- say what retrieval-augmented generation is: retrieve, augment, generate;
- search sections by the words they share with a question, and see where that fails;
- build a prompt that hands the model numbered sections to answer from.

Next, chapter 2: turning text into numbers that capture meaning.

:::photo{src="/lesson-images/rag/rag-01-notes.webp" alt="Handwritten notes about why RAG: Models do not know your documents; Retrieve, augment, generate; Keyword search: shared words; Sections go in the prompt; big cat is not tiger" ai="true"}
One page of notes for this chapter.
:::
:::
