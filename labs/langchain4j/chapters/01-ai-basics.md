:::step{type=story title="Four hundred calls a day"}
**Sahyadri Rail** runs three little trains through the Western Ghats: the **Ghat Express** from Pune up to Lonavala and
down to Karjat, the **Konkan Breeze** to Ratnagiri on the coast, and the **Monsoon Mail**, which stops everywhere. In
the rainy season, when the hills turn green and the waterfalls come back, half of Pune wants a ticket.

And half of Pune calls the help desk. Is the 7:15 on time? Can I bring my dog? How much luggage is free? I booked for
the wrong day, do I get my money back? Two people answer about four hundred calls a day, mostly the same twenty
questions, and the interesting problems (a family stuck at Karjat after a landslide) wait in the queue behind them.

Sahyadri Rail wants a help desk assistant that answers in plain language, at any hour, in English or in Marathi, and
knows the railway: its timetables, its fares, its rules. You are going to build it, in Java, with **LangChain4j**. Its
name is **Setu**, the Marathi and Hindi word for a bridge: between passengers and the railway.

Sahyadri Rail is imaginary; the ghats are not. This is the railway climbing the Bhor Ghat, between Karjat and
Lonavala, as an engraver drew it in the nineteenth century: one of the steepest main-line climbs in India.

:::photo{src="/lesson-images/langchain4j/bhor-ghat.webp" alt="An old engraving of the Bhor Ghat railway: the line cut into steep cliffs above a valley, with a bullock cart on the road below" credit="British Library" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3ABhore_Ghat_Railway.jpg"}
The Bhore Ghat railway, from a nineteenth-century book about India.
:::

Before Setu calls any AI model, this first part of the course answers the question every developer should be able to
answer: **what is the thing we are calling?** You will build each idea yourself, in plain Java, from a hand-written
rule to a neuron, a tiny language model, tokens, embeddings and attention. No AI library does the thinking for you
in Part 1; when you reach LangChain4j in chapter 9, you will know what happens on the other side of the call.

:::mission
Build Setu's first help desk the oldest way, with rules written by hand. Then let Java find a rule by itself, from
examples: your first machine learning.
:::
:::

:::step{type=concept title="Four words, one inside the other"}
You will hear four words used as if they meant the same thing. They do not; each is a smaller circle inside the one
before:

| Word | What it means | A Setu example |
|---|---|---|
| **Artificial intelligence** (AI) | Any program that does something we would call intelligent if a person did it | Answering a passenger's question |
| **Machine learning** (ML) | AI whose rules are **learned from examples**, not written by a programmer | Learning, from last month's data, how late a train can be before passengers complain |
| **Deep learning** (DL) | Machine learning with **neural networks** of many layers | Reading a photo of a ticket |
| **Generative AI** (GenAI) | Deep learning models that **create** new content: text, images, sound, code | Writing a polite answer to a question nobody has asked before |

:::diagram{name="l4j-ai-circles"}
AI is the biggest circle; machine learning sits inside it, deep learning inside that, and generative AI at the centre.
:::

The difference that matters most is the first step, from AI to machine learning: **who writes the rule**. In a
rule-based program you write `if (question.contains("refund"))`. In machine learning you give the program examples
(questions and the right answers, or delays and whether passengers complained) and it finds the rule.

A large language model, the kind of AI behind ChatGPT, sits in the smallest circle: it is a deep learning model,
trained with machine learning, that generates text. Everything in this course builds towards it.

**Check yourself:** a spam filter that learned from a million emails marked "spam" or "not spam": which circles is it
in? (AI and machine learning; deep learning only if it uses a neural network; not generative, because it labels mail
instead of writing new mail.)
:::

:::step{type=history title="Seventy years of thinking machines"}
In **1950** the mathematician **Alan Turing** published a paper that opened with a question: "Can machines think?"
Instead of arguing about the word "think", he proposed a test: if a person chatting in writing cannot tell a machine
from a human, call the machine intelligent. He called it the imitation game; we call it the **Turing test**.

:::photo{src="/lesson-images/langchain4j/alan-turing.webp" alt="A black and white portrait of Alan Turing in 1951, in a tweed jacket and tie" credit="Elliott and Fry" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AAlan_Turing_%281951%29.jpg"}
Alan Turing in 1951, a year after he asked "Can machines think?"
:::

:::before{title="Rules, written by hand"}
The name **artificial intelligence** was coined for a summer workshop at Dartmouth College in **1956**. For the next
thirty years most AI was rules. **Expert systems** of the 1970s and 1980s, such as MYCIN for infections or XCON for
configuring computers at Digital Equipment Corporation, held thousands of hand-written "if this, then that" rules.
They worked inside their small worlds, and broke at the edges: every situation nobody wrote a rule for got no answer,
and every new rule could break an old one.
:::

In **1959** Arthur Samuel at IBM coined **machine learning** for his program that learned to play draughts (checkers)
better than he did, by playing thousands of games against itself. Learning from data stayed a side road for decades,
because computers were slow and data was scarce. Then both changed: in **2012** a deep neural network called AlexNet
won the ImageNet image recognition contest by a huge margin, and **deep learning** took over. In **2017** Google
researchers published the **transformer**, and from it came the large language models: GPT-3 in **2020**, and on
**30 November 2022**, ChatGPT.

:::solved
**Rules from examples.** Machine learning replaced "write every rule" with "show enough examples". Generative AI went
one step further: a model that has learned from a huge part of everything people have written can produce answers
to questions nobody wrote a rule, or an example, for.
:::

:::timeline
- **1950** Alan Turing asks "Can machines think?"
- **1956** The Dartmouth workshop names the field: artificial intelligence.
- **1959** Arthur Samuel coins "machine learning".
- **1980s** Expert systems: thousands of hand-written rules.
- **2012** AlexNet: deep learning wins at seeing.
- **2017** The transformer paper, "Attention Is All You Need".
- **2022** ChatGPT opens to the public on 30 November.
:::

:::funfact
Samuel's draughts program, written on an IBM 701, beat a strong human player in 1962. IBM's shares reportedly rose
the morning after Samuel first demonstrated it on television in 1956.
:::
:::

:::step{type=example title="Worked example: a rule-based help desk" file="01-ai-basics/src/main/java/com/setu/Rules.java" line="8-11"}
Open `Rules.java`. Its four answers are already written, as constants:

```java
static final String REFUND = "Refunds: the full fare up to 24 hours before departure, half the fare after that.";
static final String LUGGAGE = "Each passenger may carry 40 kg of luggage free of charge.";
static final String PETS = "Small pets travel in the guard's van, with a pet ticket of Rs 120.";
static final String UNKNOWN = "Sorry, I don't know that yet. Please ask at the station office.";
```

A rule-based program picks one of them by looking for **keywords**. Here is the same idea for a different job, a
greeting bot (only to read; it is not in your project):

```java
static String greet(String message) {
    String m = message.toLowerCase(Locale.ROOT);   // "HELLO" and "hello" become the same
    if (m.contains("hello") || m.contains("namaste")) {
        return "Hello! How can I help?";
    }
    if (m.contains("bye")) {
        return "Have a good journey!";
    }
    return "Sorry, I did not understand.";
}
```

1. Lower-case the message first, once, so capitals never matter.
2. Check the rules in order: the first rule that matches wins.
3. End with a fallback, for everything no rule covers.

`Locale.ROOT` makes `toLowerCase` behave the same on every computer (in a Turkish locale, `"I".toLowerCase()` is a
dotless "ı", and keywords stop matching).
:::

:::step{type=task task=rule_reply title="Your turn: Setu's first rules" file="01-ai-basics/src/main/java/com/setu/Rules.java" line="16-21"}
Finish `Rules.reply(question)`:

1. a question that contains `refund` gets `REFUND`;
2. one that contains `luggage` or `bag` gets `LUGGAGE`;
3. one that contains `pet` or `dog` gets `PETS`;
4. anything else gets `UNKNOWN`.

Capitals must not matter: "REFUND please" is a refund question.

```bash run
cd /workspace/01-ai-basics && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Where rules break"}
With the rules written, `Setu.java` asks them four questions:

```text
$ mvn -q compile exec:java
== Rules, written by hand
How do I get a refund?
  -> Refunds: the full fare up to 24 hours before departure, half the fare after that.
Can my dog travel with me?
  -> Small pets travel in the guard's van, with a pet ticket of Rs 120.
Can I bring two bags?
  -> Each passenger may carry 40 kg of luggage free of charge.
How heavy can my suitcase be?
  -> Sorry, I don't know that yet. Please ask at the station office.
```

Three right answers, and one miss: "How heavy can my suitcase be?" is a luggage question, but it says neither
"luggage" nor "bag". You could add `suitcase`. Then `trolley`, `backpack`, `samaan` (Hindi for luggage), "my stuff",
the spelling mistakes, the questions in Marathi... A rule-based help desk grows forever and still misses the next
question. Worse, "Is the dog-friendly coach on the Konkan Breeze?" is matched by the `dog` rule, and gets the pet
ticket price instead of a coach number.

That is the wall expert systems hit in the 1980s. The way over it was to stop writing the rule, and let the program
**learn** it.
:::

:::step{type=concept title="Learning a rule from examples"}
Here is a question Sahyadri Rail really cares about: **how late can a train be before passengers start complaining?**
Nobody knows the answer as a rule. But the railway has data: for every train last week, how many minutes late it was,
and whether anyone complained.

| Minutes late | 0 | 2 | 5 | 8 | 12 | 15 | 18 | 25 | 30 | 45 |
|---|---|---|---|---|---|---|---|---|---|---|
| Complaint? | no | no | no | no | yes | no | yes | yes | yes | yes |

The rule we want looks like "late by at least **T** minutes means a complaint". Machine learning, in its simplest form,
is a search: try every possible **T**, count how many examples each one gets wrong, keep the best.

`Learn.mistakes(threshold, minutesLate, complained)` already counts the mistakes of one threshold. For **T = 12** the
rule says yes for 12, 15, 18, 25, 30 and 45, and the data disagrees only once (15 minutes, no complaint): 1 mistake.
For **T = 20** it misses the complaints at 12 and 18: 2 mistakes.

Notice what just happened. You did not decide that 12 is the answer; **the data did**. If next month passengers
become more patient, you run the same code on new data and get a new rule, without changing a line. That is the
whole promise of machine learning: real systems use millions of examples and millions of adjustable numbers instead
of one threshold, but the idea is this one.

**Check yourself:** what does "training" mean in this example? (Searching for the threshold that makes the fewest
mistakes on the examples.)
:::

:::step{type=task task=learn_threshold title="Your turn: learn the threshold" file="01-ai-basics/src/main/java/com/setu/Learn.java" line="21-25"}
Finish `Learn.bestThreshold(minutesLate, complained)`:

1. try every value in `minutesLate` as the threshold;
2. count its mistakes with `mistakes(...)`;
3. return the threshold with the fewest mistakes; if two tie, return the smaller one.

```bash run
cd /workspace/01-ai-basics && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="A rule nobody wrote"}
```text
== A rule, learned from examples
Learned: late by 12 minutes or more means a complaint (1 of 10 examples wrong)
```

Twelve minutes. Sahyadri Rail can now say, from evidence, that a delay of 12 minutes or more is when passengers start
calling, and plan its announcements around it. One of the ten examples is still wrong (a train 15 minutes late and
nobody complained): learned rules are about **most** cases, not all of them. Remember that: every model you meet in
this course, however large, is right most of the time, not every time.
:::

:::step{type=predict title="Guess first"}
:::question
A rule-based Setu and a machine-learning Setu both answer "Is my bag too heavy?" correctly. A new question arrives:
"Can I carry my harmonium?" Which one is more likely to cope?
:::
- [ ] The rule-based one: rules are exact
- [x] The learned one, if it learned from enough examples of similar questions
- [ ] Neither: computers cannot understand new questions
:::explain
A rule only covers the words someone thought of. A model that learned from many examples of luggage questions can
match a new one that is similar in meaning. That is also its weakness: it will answer confidently even when its
examples did not really cover the question.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
ChatGPT is in which of the four circles?
:::
- [ ] Only AI
- [ ] AI and machine learning, but not deep learning
- [x] All four: AI, machine learning, deep learning and generative AI
:::explain
It is a deep neural network (deep learning), trained from data (machine learning), that writes new text (generative),
and all of that is a kind of AI.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In machine learning, what does the programmer write?
:::
- [ ] Every rule, by hand
- [x] The learning procedure and the data it learns from; the rule comes out of training
- [ ] Nothing: the model writes itself
:::explain
You wrote `bestThreshold`, the search; the threshold, 12, came from the data. Real machine learning works the same
way, with far bigger searches over far more numbers.
:::
:::

:::step{type=deep-dive title="Go deeper: training, testing, and why 12 might be wrong"}
**Training and testing.** You chose 12 using all ten examples, then measured its mistakes on the same ten. That flatters
it. Real machine learning keeps some examples aside (a **test set**) and measures the rule only on those, because
what matters is how the rule does on trains it has not seen.

**Overfitting.** With enough freedom a model can memorise its examples (every one right) and still be useless on new
ones. A rule like "complaint when late by 12, 18, 25, 30 or 45 minutes, but not 15" has zero mistakes on last week and
makes no sense. Large language models fight the same problem with enormous amounts of training text.

**Features.** Lateness is one input. A better model would also use the time of day, the weather, whether it is a
holiday. Chapter 2 builds a model with several inputs: a neuron.

**Rules still matter.** Production AI systems mix both. A model writes the friendly answer; hand-written rules check
that a refund amount is right, or that nobody's phone number leaks. You will build those checks, called guardrails,
in chapter 25.
:::

:::step{type=recap}
You can now:

- tell AI, machine learning, deep learning and generative AI apart, and place a language model inside all four;
- build a rule-based answerer, and explain why rules break on questions nobody planned for;
- explain machine learning as finding a rule from examples, and do it in Java;
- say why a learned rule is right most of the time, not every time.

Next, chapter 2: the building block of deep learning, an artificial neuron, built and trained in Java.

:::photo{src="/lesson-images/langchain4j/l4j-01-notes.webp" alt="Handwritten notes about AI basics: AI, ML, deep learning, GenAI; rules are written by hand; ML: the rule comes from examples; learned rules are right most of the time; an LLM is in all four circles" ai="true"}
One page of notes for this chapter.
:::
:::
