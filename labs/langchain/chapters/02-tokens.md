:::step{type=story title="How long is a question?"}
Navin will pay for every question it reads and every answer it writes, and the bill is not counted in words or
characters. It is counted in **tokens**, the pieces a language model really reads.

Many members of the co-op write in Marathi, some in English, and many in Marathi typed with English letters ("kanda
bhav kay aahe?"). Which costs the most? Many people guess the Marathi script, because it looks the most complicated.
In this chapter you count for real, and the answer is not what most people expect.

Tokens also set a hard limit: a model can read only so many at once, its **context window**. A long conversation with
a farmer must fit, so you also write the code that keeps the newest messages and lets the oldest go.

:::mission
Count tokens with the same tokenizer OpenAI's gpt-4o models use, then fit a conversation into a token budget.
:::
:::

:::step{type=concept title="Tokens: pieces of text, numbered" file="02-tokens/tokens.py" line="1-14"}
A **tokenizer** cuts text into pieces from a fixed list of pieces, its **vocabulary**, and replaces each piece with its
number in that list. OpenAI's `o200k_base` vocabulary (used by gpt-4o and gpt-4o-mini, the model behind Navin) has
200,019 entries:

```python
import tiktoken
ENCODING = tiktoken.get_encoding("o200k_base")
ENCODING.encode("What is the onion rate today?")   # a list of 7 numbers
```

- `tiktoken` is OpenAI's tokenizer library; it runs on your machine, with no model call.
- `get_encoding("o200k_base")` loads that vocabulary.
- `encode(text)` returns the token numbers. Their count is what the model reads, and what you pay for.

Common words are one token each; rarer words are cut into several. `pieces(text)` (already written) turns each number
back into its text, so you can see the cuts:

:::diagram{name="lc-tokens"}
The real pieces of the same question, three ways, from this chapter's `main.py`.
:::

Why not whole words? A vocabulary of every word in every language would be enormous and would still miss new words,
names and typos. Pieces can spell anything.

Rules of thumb for English with this tokenizer (we measured 131 tokens per 100 words on chapter 1's story):

| English text | Tokens |
|---|---|
| One short word | about 1 |
| 100 words | about 130 |
| One page (about 500 words) | about 650 |

Other languages and other tokenizers give other numbers; the only reliable way is to count.

A printer once built every page from a fixed set of small metal pieces, reused for every word. A tokenizer also works
from a fixed set of pieces, about 200,000 of them here.

:::photo{src="/lesson-images/langchain/metal-type.webp" alt="Close-up of metal movable type letters for printing, set side by side in a composing stick" credit="Willi Heidelbach" license="CC BY 2.5" source="https://commons.wikimedia.org/wiki/File%3AMetal_movable_type.jpg"}
Metal movable type for letterpress printing.
:::
:::

:::step{type=history title="A compression trick that became the alphabet of AI"}
:::before{title="Words, or letters"}
Early language systems used whole words (and failed on any word they had not seen) or single letters (and needed
very long sequences for one sentence).
:::

In **1994** Philip Gage described **byte pair encoding** (BPE) as a way to compress files: repeatedly replace the most
common pair of symbols with a new symbol. In **2016** Rico Sennrich, Barry Haddow and Alexandra Birch used the same
idea to cut rare words into pieces for translation models. OpenAI's GPT-2 (**2019**) applied it to bytes, the raw
numbers a computer stores text as, so any text in any language can be encoded. OpenAI published its fast tokenizer as
the **tiktoken** library in 2022, and the `o200k_base` vocabulary arrived with **GPT-4o** in **2024**, with many more
pieces for languages other than English.

:::solved
**Any text, a fixed vocabulary.** No word is ever unknown: anything can be spelled from pieces. The price is that the
same meaning costs a different number of tokens in different languages and spellings.
:::

:::timeline
- **1994** Byte pair encoding, for compression.
- **2016** BPE for translation models.
- **2019** Byte-level BPE in GPT-2.
- **2024** o200k_base with GPT-4o.
:::
:::

:::step{type=task task=count_tokens title="Your turn: count tokens" file="02-tokens/tokens.py" line="7-9"}
Finish `count_tokens(text)`: return the number of tokens, `len(ENCODING.encode(text))`.

The usual slip: returning `len(text)` (characters) or `len(text.split())` (words). Neither is what the model counts.

Press **Check**.
:::

:::step{type=concept title="The context window" file="02-tokens/tokens.py" line="17-20"}
Everything a model reads in one call (the instructions, the facts, the whole conversation so far, the new question)
must fit in its **context window**. For gpt-4o-mini that is 128,000 tokens, and one answer can be at most 16,384
tokens long. You rarely want to fill the window: every token sent is paid for on every call.

So chat applications keep a **window** of the conversation: the newest messages that fit a **budget** (a number of
tokens you choose), oldest dropped first. The real counts for this chapter's conversation, budget 25:

:::trace{title="fit_window(chat, 25), walking backwards"}
| Message (newest first) | Tokens | Used so far | Kept? |
|---|---|---|---|
| Can I add 20 more crates next week? | 10 | 10 | yes |
| My cold storage booking is 40 crates. | 9 | 19 | yes |
| I grow onions on 3 acres. | 8 | 27 | no: over 25, stop |
| Hello, I am Ravi from Lasalgaon. | 10 | | not looked at |
:::

Notice what is lost: "I grow onions on 3 acres". Windows forget, and chapter 15 shows what that does to a conversation.
:::

:::step{type=task task=fit_window title="Your turn: fit the window" file="02-tokens/tokens.py" line="17-20"}
Finish `fit_window(messages, budget)`:

1. Walk the messages from the last one backwards (`reversed(messages)`), keeping a running total of tokens.
2. If adding the next message would go over the budget, stop.
3. Otherwise keep it and add its tokens to the total.
4. Return the kept messages in their original order (reverse the kept list back).

The usual slips:

- Skipping a message that does not fit and carrying on with older ones. That keeps a gap in the conversation, and
  the model then reads an old message as if it came just before the new one. Stop at the first one that does not fit.
- Returning the messages newest first.

```bash run
cd /workspace/02-tokens && python main.py
```

Press **Check**.
:::

:::step{type=try title="Which way of writing is cheapest?"}
```text
$ python main.py
  7 tokens  ['What', ' is', ' the', ' onion', ' rate', ' today', '?']
 11 tokens  ['a', 'aj', ' k', 'andy', 'acha', ' bh', 'av', ' kay', ' aa', 'he', '?']
  8 tokens  ['आज', ' कां', 'द्य', 'ाचा', ' भाव', ' काय', ' आहे', '?']

fits in 25 tokens: ['My cold storage booking is 40 crates.', 'Can I add 20 more crates next week?']
```

The same question three ways. English: 7 tokens, one per word. Marathi in Devanagari: only 8, because `o200k_base`
has pieces like `भाव` (price) and `काय` (what). Marathi typed with English letters: **11**, the most expensive, because
"kandyacha" is not a common English piece and gets cut into `k`, `andy`, `acha`.

The surprise is that the way many members actually type is the one that costs the most: 11 tokens against 7, about 57%
more than English. On Navin's scale that is a tiny amount per question; on millions of questions it is a line in a
budget. Measure, do not assume.
:::

:::step{type=predict title="Guess first"}
:::question
A conversation grows to 200,000 tokens and the model's window is 128,000. What must the application do?
:::
- [ ] Nothing: the model reads the first 128,000 tokens
- [x] Send less: drop or summarise old messages so the request fits
- [ ] Split the answer into two calls
:::explain
A request larger than the window is refused with an error. Windows (this chapter) and summaries (chapter 22) are the
two common fixes.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why do tokenizers use pieces instead of whole words?
:::
- [ ] Pieces are faster to type
- [x] Any word, name or typo can be spelled from pieces, with a vocabulary of fixed size
- [ ] Models cannot read whole words
:::explain
With pieces nothing is ever unknown; with whole words, every new name would be.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why count tokens yourself, before calling the model?
:::
- [x] To know the cost and to make sure the request fits the context window
- [ ] The model refuses text that was not counted
- [ ] Counting makes the answer better
:::explain
The model counts too, and bills you for it. Counting first lets you decide what to send.
:::
:::

:::step{type=deep-dive title="Go deeper: tokens in practice"}
**Different models, different tokenizers.** Claude, Gemini and Llama each have their own vocabulary, so the same text is
a different number of tokens for each. Count with the tokenizer of the model you call.

**Output tokens cost more.** The answer is tokens too. For gpt-4o-mini, OpenAI's list price is $0.15 per million input
tokens and $0.60 per million output tokens (November 2026): an output token costs four times an input token. Other
models have other prices and other ratios. Chapter 9 works out what Navin's questions cost.

**The usage the API reports.** Every model reply says how many tokens it used. Chapter 6 reads that number from the
real API, and it includes a few tokens of message formatting that `count_tokens` does not see.
:::

:::step{type=recap}
You can now:

- explain what tokens and a tokenizer's vocabulary are, and why tokenizers cut text into pieces;
- count tokens with tiktoken and `o200k_base`;
- keep the newest messages within a token budget;
- show, with real numbers, that the same question costs different amounts in different scripts.

Next, chapter 3: embeddings. Meaning as a list of numbers, so a program can find "kanda bhav" from "onion rate".

:::photo{src="/lesson-images/langchain/lc-02-notes.webp" alt="Handwritten notes about tokens: Models read tokens, not words or letters. Each tokenizer has its own fixed vocabulary of pieces. With o200k_base, our question took 7 tokens in English and 8 in Devanagari. Marathi in English letters took 11, the most. A context window limits how many tokens fit in one call. Keep the newest messages that fit the budget." ai="true"}
One page of notes for this chapter.
:::
:::
