:::step{type=story title="How long is a question?"}
Navin will pay for every question it reads and every answer it writes, and the bill is not counted in words or
characters. It is counted in **tokens**, the pieces a language model really reads.

Many members of the co-op write in Marathi, some in English, many in Marathi typed with English letters ("kanda bhav
kay aahe?"). Which costs more? Most people guess English is the cheapest. In this chapter you count for real, and the
answer is not what most people expect.

Tokens also set a hard limit: a model can read only so many at once, its **context window**. A long conversation with
a farmer must fit, so you also write the code that keeps the newest messages and lets the oldest go.

:::mission
Count tokens with the same tokenizer OpenAI's gpt-4o models use, then fit a conversation into a token budget.
:::
:::

:::step{type=concept title="Tokens: pieces of text, numbered" file="02-tokens/tokens.py" line="1-14"}
A **tokenizer** cuts text into pieces from a fixed vocabulary and replaces each piece with its number. OpenAI's
`o200k_base` vocabulary (used by gpt-4o and gpt-4o-mini, the model behind Navin) has about 200,000 pieces:

```python
import tiktoken
ENCODING = tiktoken.get_encoding("o200k_base")
ENCODING.encode("What is the onion rate today?")   # a list of 7 numbers
```

Common words are one token each; rare words are cut into several. `pieces(text)` (already written) decodes each number
back to its text, so you can see the cuts.

Why not whole words? A vocabulary of every word in every language would be enormous and would still miss new words,
names and typos. Pieces can spell anything.

| Rule of thumb (English) | Tokens |
|---|---|
| One short word | about 1 |
| 100 words | about 130 |
| One page of text | about 600 to 800 |

A printer once set a page from a case of small metal pieces: letters, common pairs and spaces, reused for every word. A tokenizer's vocabulary is the same idea, with about 200,000 pieces instead of a few hundred.

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
common pair of symbols with a new symbol. In **2016** Rico Sennrich and colleagues used the same idea to cut words into
pieces for translation models. OpenAI's GPT-2 (**2019**) applied it to bytes, so any text in any language can be
encoded. OpenAI published its fast tokenizer as the **tiktoken** library, and the `o200k_base` vocabulary arrived with
**GPT-4o** in **2024**, with many more pieces for languages other than English.

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
Finish `count_tokens(text)`: return the length of `ENCODING.encode(text)`.

Press **Check**.
:::

:::step{type=concept title="The context window" file="02-tokens/tokens.py" line="17-20"}
Everything a model reads in one call (the instructions, the facts, the whole conversation so far, the new question)
must fit in its **context window**, and its answer must fit too. gpt-4o-mini's window is 128,000 tokens, but you
rarely want to fill it: every token sent is paid for on every call.

So chat applications keep a **window** of the conversation: the newest messages that fit a budget, oldest dropped
first.

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
Finish `fit_window(messages, budget)`: walk from the last message backwards, add each one while the total stays within
the budget, stop at the first that does not fit, and return the kept messages in their original order.

```bash run
cd /workspace/02-tokens && python main.py
```

Press **Check**.
:::

:::step{type=try title="Which language is cheapest?"}
```text
$ python main.py
  7 tokens  ['What', ' is', ' the', ' onion', ' rate', ' today', '?']
 11 tokens  ['a', 'aj', ' k', 'andy', 'acha', ' bh', 'av', ' kay', ' aa', 'he', '?']
  8 tokens  ['आज', ' कां', 'द्य', 'ाचा', ' भाव', ' काय', ' आहे', '?']

fits in 25 tokens: ['My cold storage booking is 40 crates.', 'Can I add 20 more crates next week?']
```

The same question three ways. English: 7 tokens, one per word. Marathi in Devanagari: 8, because `o200k_base` has
pieces like `भाव` (price) and `काय` (what). Marathi typed with English letters: **11**, the most expensive, because
"kandyacha" is not a common English piece and gets cut into `k`, `andy`, `acha`.

The surprise is that the way most members actually type is the one that costs most, about 40% more than English. On
Navin's scale that is a rounding error per question; on millions of questions it is a line in a budget. Measure, do not
assume.
:::

:::step{type=predict title="Guess first"}
:::question
A conversation grows to 200,000 tokens and the model's window is 128,000. What must the application do?
:::
- [ ] Nothing: the model reads the first 128,000 tokens
- [x] Send less: drop or summarise old messages so the request fits
- [ ] Split the answer into two calls
:::explain
A request larger than the window is refused. Windows (this chapter) and summaries (chapter 22) are the two common fixes.
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

**Output tokens.** The answer is tokens too, usually priced at about four times an input token (chapter 9). A long
answer costs more than a long question.

**The usage the API reports.** Every model reply says how many tokens it used. Chapter 6 reads that number from the
real API, and it includes a few tokens of message formatting that `count_tokens` does not see.
:::

:::step{type=recap}
You can now:

- explain what tokens are and why tokenizers cut text into pieces;
- count tokens with tiktoken and `o200k_base`;
- keep the newest messages within a token budget;
- show, with real numbers, that the same question costs different amounts in different scripts.

Next, chapter 3: embeddings. Meaning as a list of numbers, so a program can find "kanda bhav" from "onion rate".

:::photo{src="/lesson-images/langchain/lc-02-notes.webp" alt="Handwritten notes about tokens: Models read tokens, not words; English 7, Devanagari 8; Marathi in English letters: 11; Window: keep the newest; Every token is paid for" ai="true"}
One page of notes for this chapter.
:::
:::
