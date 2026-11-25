:::step{type=story title="A help desk for a village of farmers"}
Every morning the phone at the Pimpalgaon Farmers' Cooperative, near Nashik, rings with the same questions. "What is
the onion rate today?" "Is the office open on Saturday?" "Can I store 60 crates of tomatoes?" "Can I pick my grapes
four days after spraying?" Two people answer them, and on a harvest morning both are busy before nine.

In this course you build **Navin**, the co-op's help desk assistant. By the last chapter Navin answers members in
plain words from the co-op's real facts and rules, uses tools to look up rates and book cold storage, reads a photo of
a sick leaf, remembers each farmer, asks the manager before a big booking, and runs as a web service. You build it with
**LangChain**, one of the most widely used Python libraries for building applications on top of language models. A
**language model** is a program trained on a huge amount of text to continue text: given words, it predicts what
comes next. Chapter 2 shows exactly how.

But first: what does it mean for a program to "understand" a question at all? This chapter answers that with two tiny
programs, one written by hand and one that learns.

Onions and garlic in baskets at a market in Nashik, the district at the centre of India's onion trade, where the
members of Navin's (fictional) co-op farm.

:::photo{src="/lesson-images/langchain/onion-seller-nashik.webp" alt="Round baskets heaped with red onions and white garlic at a street market, with red plastic crates behind" credit="AnantGujratiwtn" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AOnion_seller_in_nashik.jpg"}
Onions and garlic for sale in Nashik.
:::
:::mission
Write a help desk that answers with hand-written rules, then a program that learns a rule from examples, and see
exactly where each one breaks.
:::
:::

:::step{type=concept title="Four words, one inside the other"}
People use four words as if they meant the same thing. They do not; each one sits inside the one before:

| Word | Means | A co-op example |
|---|---|---|
| **Artificial intelligence (AI)** | Any program doing something we would call intelligent | A program that answers "office hours" questions with rules |
| **Machine learning (ML)** | The program learns its rule from examples instead of being told | Learning from past mornings how much rain means "skip irrigation" |
| **Deep learning** | Machine learning with **neural networks** of many layers | Recognising a diseased grape leaf in a photo |
| **Generative AI** | Deep learning models that create new text, images or code | Writing a reply to a farmer's question in plain Marathi or English |

A **neural network** is a program made of many small calculations connected in **layers**: each layer takes numbers
in, multiplies them by learned values, and passes the result on. "Learning" means adjusting those values until the
network's answers on the examples are good. "Deep" simply means many layers.

:::diagram{name="lc-ai-circles"}
Each circle sits inside the one before. A large language model, like the one behind Navin, is in the smallest circle,
so it is all four at once.
:::

The step that matters most is the first one, from AI to machine learning: **who writes the rule**. In a rule-based
program you write `if "rate" in message`. In machine learning you give examples and the program finds the rule. The
language model behind Navin is the far end of that idea: nobody wrote a single rule about onions; it learned from
huge amounts of text, much of it from the web.
:::

:::step{type=history title="From checkers to ChatGPT"}
:::before{title="Every rule by hand"}
The name **artificial intelligence** was coined in John McCarthy's 1955 proposal for a summer workshop at Dartmouth
College, held in **1956**. For decades most AI was rules, typed by experts, and every situation nobody had a rule for
simply had no answer.
:::

In **1959** Arthur Samuel at IBM published "Some Studies in **Machine Learning** Using the Game of Checkers", about a
program that played checkers better the more games it played. That paper made the name stick. (The famous definition,
"the ability to learn without being explicitly programmed", is a later summary of his idea, not a sentence from the
paper.)

In **2012** a neural network called **AlexNet**, by Alex Krizhevsky, Ilya Sutskever and Geoffrey Hinton, won the
ImageNet image-recognition contest by a wide margin, and deep learning took over. On **30 November 2022** OpenAI
released **ChatGPT**; by an estimate from the bank UBS it had about a hundred million users two months later, faster
than any app before it.

:::solved
**Rules nobody has to write.** Learned rules cover cases no person listed, which is why Navin will understand "kanda
bhav?" without a rule for it. The price: a learned rule can be wrong in ways nobody predicted, which this course
measures again and again.
:::

:::timeline
- **1956** The Dartmouth workshop names "artificial intelligence".
- **1959** Arthur Samuel's checkers paper names "machine learning".
- **2012** AlexNet: deep learning wins ImageNet.
- **2022** ChatGPT.
:::

**Geoffrey Hinton**, one of the three authors of AlexNet, shared the 2024 Nobel Prize in Physics with John Hopfield,
"for foundational discoveries and inventions that enable machine learning with artificial neural networks".

:::photo{src="/lesson-images/langchain/geoffrey-hinton.webp" alt="Geoffrey Hinton, grey-haired, in a dark jacket, speaking at a press conference" credit="Arthur Petron" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3AGeoffrey_E._Hinton%2C_2024_Nobel_Prize_Laureate_in_Physics_%28cropped1%29.jpg"}
Geoffrey Hinton at the 2024 Nobel Prize press conference.
:::

Arthur Samuel's checkers program, the one in that 1959 paper, first ran on an **IBM 701**, IBM's first commercial
scientific computer (1952). This is its operator's console.

:::photo{src="/lesson-images/langchain/ibm-701.webp" alt="The grey operator's console of an IBM 701 computer, with rows of small lights and push buttons" credit="Dan" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File%3AIBM_701console.jpg"}
The operator's console of an IBM 701.
:::
:::

:::step{type=example title="Worked example: one rule, written by hand" file="01-ai-basics/rules.py" line="8-11"}
A rule-based reply is a chain of `if`s. Here is one for loans (only to read; it is not in your project):

```python
def loan_reply(message: str) -> str:
    text = message.lower()                  # "LOAN", "Loan" and "loan" all match
    if "loan" in text or "credit" in text:
        return "Crop loans are up to Rs 50,000 per acre, at 7% a year."
    return "Sorry, I only know about loans."
```

Line by line:

- `message.lower()` makes a lower-case copy, so the rule matches however the person typed. Nearly every word rule
  needs this.
- `"loan" in text` is True when the text contains the letters "loan" anywhere (so "loans" matches too).
- `or` means either word is enough.
- The last `return` is the answer when no rule matched: a rule-based program needs one for everything it does not know.

(The loan figures are made up for this example.)
:::

:::step{type=task task=rule_reply title="Your turn: a rule-based help desk" file="01-ai-basics/rules.py" line="8-11"}
Finish `rule_reply(message)`:

1. Lower-case the message.
2. If it mentions `office` or `open`, return `OFFICE`.
3. Else, if it mentions `price` or `rate`, return `ONION`.
4. Otherwise return `UNKNOWN`.

`OFFICE`, `ONION` and `UNKNOWN` are already defined at the top of the file.

The usual slips:

- Checking the message before lower-casing it: "What is the RATE?" then finds nothing.
- Returning the strings `"OFFICE"` (in quotes) instead of the names `OFFICE`: the farmer would get the word "OFFICE".

Press **Check**.
:::

:::step{type=concept title="Learning a rule from examples" file="01-ai-basics/learn.py" line="7-20"}
Now the other way. `EXAMPLES` holds twelve made-up mornings: millimetres of rain overnight, and whether the farmer
skipped irrigating that day. The rule we want has the shape "skip when rain >= *threshold*", where the **threshold**
is the dividing line. Nobody knows it yet.

So the program **tries every candidate** and keeps the one that explains the examples best. `accuracy(threshold,
examples)` (already written) counts the share of examples a threshold gets right; that share is its **accuracy**.
Some of the real values, from the lab's own code:

| Threshold | Gets right | Accuracy |
|---|---|---|
| 5 mm | 9 of 12 | 75% |
| 6 mm | 10 of 12 | 83% |
| 8 mm | 11 of 12 | 92% |
| 9 mm | 10 of 12 | 83% |
| 11 mm | 11 of 12 | 92% |

8 and 11 tie. Our tie-break is "keep the smaller one". That is a choice a person makes, and real machine learning is
full of such choices: which examples, which shape of rule, what counts as best.
:::

:::step{type=task task=learn_threshold title="Your turn: learn the threshold" file="01-ai-basics/learn.py" line="17-20"}
Finish `learn_threshold(examples)`:

1. Make the list of candidates: every rain value in the examples, sorted, smallest first.
2. For each candidate, compute `accuracy(candidate, examples)`.
3. Keep the candidate with the highest accuracy. On a tie, keep the one you found first, which is the smaller one
   because the list is sorted.
4. Return it.

The usual slip: replacing the best on a tie (`>=` instead of `>` when comparing), which keeps the larger threshold,
11 mm.

```bash run
cd /workspace/01-ai-basics && python main.py
```

Press **Check**.
:::

:::step{type=try title="Where each one breaks"}
```text
$ python main.py
'When is the office open?'         -> The co-op office is open Monday to Saturday, 9:00 to 17:00.
'What is the onion rate today?'    -> Today's onion rate is Rs 1,850 a quintal.
'When can I come in?'              -> Sorry, I only know the office hours and the onion rate.
'kanda bhav?'                      -> Sorry, I only know the office hours and the onion rate.

learned: skip irrigation when rain >= 8 mm (92% of the examples right)
```

The rules answered the two questions someone thought of, and failed both others: "When can I come in?" is about office
hours, and "kanda bhav?" is Marathi for "onion price?", but neither contains a word in a rule. You could add more rules
forever.

The learner found 8 mm by itself, and is right on 11 of the 12 mornings. The one it gets wrong is the 9 mm morning when
the farmer did not skip. No single threshold gets all twelve right: real data has exceptions. A threshold learned from
twelve mornings is a guess about the thirteenth.
:::

:::step{type=predict title="Guess first"}
:::question
You add twelve more mornings to `EXAMPLES` and run `learn_threshold` again. What can happen?
:::
- [ ] Nothing: 8 mm is fixed now
- [x] The threshold may change: the rule comes from the examples
- [ ] The program crashes
:::explain
That is the point of learning: change the examples and the rule follows, with no code changes.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which of these is machine learning?
:::
- [ ] `if "rate" in message: return ONION`
- [x] Finding the rain threshold from past mornings
- [ ] Lower-casing the message
:::explain
Machine learning means the rule comes from examples, not from the programmer.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Navin will understand "kanda bhav?" without anyone writing a rule for it. Why?
:::
- [ ] Someone added a Marathi rule
- [x] The language model learned from huge amounts of text, including many ways to ask about prices
- [ ] Python understands Marathi
:::explain
A language model is learning taken to the extreme: billions of examples instead of twelve.
:::
:::

:::step{type=deep-dive title="Go deeper: rules are not dead"}
**Rules and models together.** Real systems keep rules where they must be exact: the co-op's office hours, a refund
policy, a legal limit. Navin will learn to send those to plain Python (tools, chapter 12) and use the model for
language.

**Overfitting.** A rule that fits its examples perfectly may fail on new ones; that is called overfitting. Machine
learning tests a rule on examples it did not learn from; chapter 26 does the same for Navin's answers.

**Where the examples come from.** In real projects, collecting good examples is most of the work. A learned rule is
only as good as its examples.
:::

:::step{type=recap}
You can now:

- tell AI, machine learning, deep learning and generative AI apart, and say what a neural network is;
- write a rule-based reply, and say why it breaks;
- learn a rule from examples by trying candidates and measuring accuracy;
- explain why a language model needs no rule for "kanda bhav?".

Next, chapter 2: what a model actually reads. Not words, but tokens.

:::photo{src="/lesson-images/langchain/lc-01-notes.webp" alt="Handwritten notes about AI and machine learning: AI contains machine learning, which contains deep learning, which contains generative AI. With rules, a person writes the rule. With machine learning, the rule comes from examples. Our learner chose 8 mm and got 11 of 12 mornings right. No single threshold fits all twelve of our mornings. A learned rule is a guess about new cases." ai="true"}
One page of notes for this chapter.
:::
:::
