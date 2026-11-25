:::step{type=story title="Why Marathi costs more"}
Sahyadri Rail's passengers write in English, in Marathi, in Hindi, and very often in a mix ("Pune to Lonavala train
kitne baje hai?"). When the railway's finance team saw the first quote for an AI help desk, priced "per token", they
asked a fair question: what is a token, and why would a question in Marathi cost more than the same question in
English?

Language models do not read letters, and they do not read words. They read **tokens**, and everything about a model,
what it costs, how fast it answers and how much it can remember, is measured in them. This chapter makes tokens
visible, with the very tokenizer gpt-4o-mini uses, running offline in your lab.

:::mission
Count tokens the way the model does, see why the same question costs more in some languages, and fit a long chat
into a model's context window.
:::
:::

:::step{type=concept title="Tokens: the pieces a model reads"}
In chapter 3 you cut text into words. Models cut it into **tokens**: common words become one token, rare words are
split into pieces, and anything (an emoji, a typo, a new place name) can always be spelled out from smaller pieces.
Each token is then a number, an index in the model's vocabulary.

Here is gpt-4o-mini's real tokenizer at work on some Setu text (we ran o200k_base again on 26 November: exactly these
pieces and ids):

```text
3 tokens: [L][onav][ala]  ids [43, 16531, 2528]
9 tokens: [When][ does][ the][ G][hat][ Express][ leave][ Pune][?]  ids [5958, 2226, 290, 499, 13274, 19911, 7668, 102208, 30]
3 tokens: [un][bel][ievably]  ids [373, 9880, 153516]
3 tokens: [प][ुण][े]  ids [2033, 52912, 628]
```

Read it slowly:

1. " Pune" is **one** token, space included: it is common enough to have its own entry. At the very start of a
   text, with no space before it, "Pune" is two, `[P][une]`: a token is a piece of text, spaces and all. "Lonavala"
   is three: `[L][onav][ala]`.
2. "unbelievably" is split into pieces that appear in many words (`un`, `bel`). That is how a model can handle a word
   it has never seen: from pieces it has.
3. The Marathi word पुणे (Pune) is three tokens for four characters: scripts that were rarer in the training text get
   shorter pieces, so the same sentence needs more tokens.

A rough rule for English: **one token is about three quarters of a word**, or four characters. For other languages
and for code, the rule changes, which is why you count instead of guessing.

**Check yourself:** why can a model read a word that did not exist when it was trained, such as a new station name?
(The tokenizer spells it out from smaller pieces it does know.)
:::

:::step{type=history title="A compression trick that became the alphabet of AI"}
In **1994** the programmer Philip Gage published a small data compression method, **byte pair encoding** (BPE): find
the pair of bytes that appears most often, replace it with a new symbol, and repeat. Twenty years later, in **2016**,
Rico Sennrich and colleagues at the University of Edinburgh used the same idea to split words for machine translation:
start from single characters, and keep merging the most frequent pairs until the vocabulary is the size you want.

:::before{title="Whole words only"}
Earlier systems gave every word its own number. Their vocabularies were huge and still incomplete: every name,
misspelling and new word became `UNKNOWN`, and languages that join words together (German, Finnish, Marathi) never
fitted.
:::

OpenAI's GPT-2 (**2019**) applied BPE to raw bytes, so any text in any script can be encoded. The tokenizer of
gpt-4o and gpt-4o-mini, called **o200k_base**, has about 200,000 tokens, roughly twice its predecessor's, with many more
pieces for non-English languages. That change made Indian languages noticeably cheaper on newer models.

:::solved
**Any text, a fixed vocabulary.** Subword tokens let a model with a fixed list of about 200,000 pieces read every word in
every language, plus code and emoji, and that list is what models are priced in.
:::

:::timeline
- **1994** Philip Gage: byte pair encoding, for compression.
- **2016** Sennrich, Haddow and Birch: subword units for translation.
- **2019** GPT-2: byte-level BPE, any text at all.
- **2024** o200k_base, the tokenizer of gpt-4o and gpt-4o-mini.
:::
:::

:::step{type=example title="Worked example: counting tokens in Java" file="04-tokens/src/main/java/com/setu/Tokens.java" line="8"}
LangChain4j can count tokens exactly as an OpenAI model will, offline, with `OpenAiTokenCountEstimator`:

```java
static final OpenAiTokenCountEstimator ESTIMATOR = new OpenAiTokenCountEstimator("gpt-4o-mini");
```

It picks the right tokenizer for the model name (o200k_base for gpt-4o-mini). It does not call OpenAI; it runs the
tokenizer inside your program. To count the tokens of a whole message list instead of one text, it also has
`estimateTokenCountInMessages(...)` (only to read; you need only the text version today):

```java
int n = ESTIMATOR.estimateTokenCountInText("Pune to Lonavala");   // 6
```

Counting matters before you call a model, too: to check a question is not too long, to estimate a bill, or to decide
what fits in the context window.
:::

:::step{type=task task=count_tokens title="Your turn: count like the model" file="04-tokens/src/main/java/com/setu/Tokens.java" line="13-16"}
Finish `Tokens.count(text)`: return how many tokens gpt-4o-mini sees, by asking `ESTIMATOR`: one line,
`return ESTIMATOR.estimateTokenCountInText(text);`.

The usual slip: `text.length()`, which counts Java characters. It happens to give 6 for the three emojis, and 8
instead of 3 for "Lonavala".

```bash run
cd /workspace/04-tokens && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="The same question, three languages"}
```text
$ mvn -q compile exec:java
3 tokens, 8 characters: Lonavala
9 tokens, 38 characters: When does the Ghat Express leave Pune?
18 tokens, 36 characters: पुणे ते लोणावळा गाडी किती वाजता आहे?
13 tokens, 38 characters: Pune to Lonavala train kitne baje hai?
6 tokens, 6 characters: 🚆🚆🚆
```

The same question about the morning train: 9 tokens in English, 13 in Hinglish, and 18 in Marathi, twice the English.
At the course model's prices ($0.15 per million input tokens) that is still a tiny fraction of a paisa per question,
but across four hundred calls a day for a year, and with long answers in Marathi too, the language of your users is a
real line in the budget.

Two more surprises. Three train emojis are 6 tokens, and Java says they are 6 characters long: each emoji is stored as
two `char` values (a surrogate pair), and the tokenizer splits each emoji into byte pieces. And "Lonavala" (8 letters)
is 3 tokens while the 38-letter English question is 9: the more common the words, the more letters per token.
:::

:::step{type=concept title="The context window"}
A model reads its whole input at once, and that input has a hard size limit, counted in tokens: the **context window**.
For gpt-4o-mini it is **128,000 tokens** (about 300 pages of English), and an answer can be up to 16,384 tokens long.
GPT-3 in 2020 had 2,048.

Everything you send counts against it: the instructions (the "system message"), the conversation so far, any documents
you paste in, and the question. Three facts follow, and you will meet each one again:

| Fact | Consequence |
|---|---|
| A model has no memory between calls | To continue a chat, you send the history again, every time (chapter 17) |
| History grows with every message | Long chats eventually do not fit; you must drop or summarise old messages |
| You pay for every token you send | Sending the whole history each time makes long chats expensive |

The simplest policy, and the one LangChain4j's `TokenWindowChatMemory` uses, is a **sliding window**: keep the newest
messages that fit in a budget, and drop the oldest. The newest messages matter most ("Can she get a lower berth?"
only makes sense next to the messages just before it). The rule has one subtlety: once a message does not fit, stop,
even if an older, shorter message would fit, because a conversation with a hole in the middle confuses the model.

:::diagram{name="l4j-context-window"}
This chapter's real five-message chat, counted with o200k_base and fitted into 40 tokens.
:::
:::

:::step{type=task task=fit_window title="Your turn: fit the chat in the window" file="04-tokens/src/main/java/com/setu/Context.java" line="12-17"}
Finish `Context.fit(messages, budget)`:

1. walk from the **newest** message (the last) backwards, adding up `Tokens.count` of each;
2. stop at the first message that would take the total over `budget`;
3. return the kept messages **oldest first**, in their original order.

The usual slips:

- Skipping a message that does not fit and carrying on with older ones: that makes the hole in the middle the
  concept warned about.
- Returning the kept messages newest first, in the order you walked.

Press **Check**.
:::

:::step{type=try title="What the model sees"}
```text
With a budget of 40 tokens, the model sees:
  Setu: The Ghat Express leaves Pune at 7:15 and reaches Lonavala at 8:40.
  Passenger: Can she get a lower berth?
```

With 40 tokens to spend, only the last two messages fit: 9 tokens, then 25 (34 in all); the next one, 14 tokens,
would make 48. (Re-run on 26 November: the same output.) The model would know about the 7:15 Ghat Express and the lower
berth, but not that the passenger is travelling with her grandmother, or that the trip is next Sunday. If the next
question is "Which day did I say?", it cannot know. That is the trade-off of every chat memory: what to keep, and what
it costs to keep it.
:::

:::step{type=predict title="Guess first"}
:::question
A passenger's chat is 100 messages long, and each message is sent again with every new question. What grows fastest?
:::
- [ ] The answer length
- [x] The input tokens per call, and so the cost and the wait
- [ ] Nothing: the model remembers the chat for free
:::explain
The model has no memory, so the history is input every time. A long chat means long inputs, which cost more and make
the model slower to start answering. Chapter 17 shows LangChain4j's chat memories, which keep it bounded.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does the same question usually need more tokens in Marathi than in English?
:::
- [ ] Marathi words are longer
- [x] The tokenizer learned its pieces mostly from English text, so other scripts get smaller pieces
- [ ] The model translates it to English first
:::explain
Tokenizers learn their vocabulary from their training text. Pieces for frequent English words are whole words; for
less frequent scripts they are smaller, so the same meaning takes more of them.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What counts against the context window?
:::
- [x] Everything sent in the request, plus the answer: instructions, history, documents and the question
- [ ] Only the user's question
- [ ] Only the model's answer
:::explain
The window covers input and output together. Pasting a long document into a prompt leaves less room for the
conversation and the answer.
:::
:::

:::step{type=deep-dive title="Go deeper: tokens in practice"}
**Count before you send.** A help desk can refuse a 5,000-token question before calling the model, at no cost. You
will build exactly that as a guardrail in chapter 25.

**Every model has its own tokenizer.** Claude, Gemini and Llama each split text differently, so the same text is a
different number of tokens. LangChain4j's `TokenCountEstimator` interface has an implementation per provider.

**Output tokens cost more.** For gpt-4o-mini, output tokens cost four times as much as input tokens, and they are
generated one at a time, so a long answer is both dearer and slower than a long question. Asking for short answers is
the cheapest optimisation there is (chapter 10).

**Long context is not free attention.** A model with a 128,000-token window can read 300 pages, but it uses the
beginning and end of a long input more reliably than the middle. Retrieval (chapter 23) sends only the relevant pages
instead.
:::

:::step{type=recap}
You can now:

- explain tokens, subword pieces and why rare words and scripts take more of them;
- count tokens exactly as gpt-4o-mini does, offline, with `OpenAiTokenCountEstimator`;
- explain the context window and what counts against it;
- keep the newest part of a conversation that fits a token budget.

Next, chapter 5: how a model represents meaning, as long lists of numbers called embeddings, computed by a real model
running inside your program.

:::photo{src="/lesson-images/langchain4j/l4j-04-notes.webp" alt="Sketchnote, Tokens (the pieces a model reads, and pays for): Models read tokens: common words are one piece, rare words are several. Cost and the context window are counted in tokens. The flow: Text, Tokenizer: o200k_base, Token ids, Count against the window. What we measured: Lonavala = 3 tokens: L + onav + ala; the same question: 9 in English, 18 in Marathi; budget 40: only the last 2 messages fit; stop at the first message that does not fit." ai="true"}
One page of notes for this chapter.
:::
:::
