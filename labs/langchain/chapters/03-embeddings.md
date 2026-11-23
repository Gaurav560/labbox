:::step{type=story title="Same question, no words in common"}
The co-op has five questions it answers every day, written up as an FAQ. A member types "kanda bhav kay aahe aaj?" The
FAQ entry is "What is today's onion rate?". They share no word at all, yet they mean the same thing. Chapter 1's rules
could never connect them.

What connects them is an **embedding**: a list of numbers that stands for the meaning of a text, made by a model, so
that texts with similar meaning get similar numbers. With embeddings, "find the FAQ entry for this question" becomes
"find the closest list of numbers", which is plain arithmetic.

:::mission
Measure how close two embeddings are with cosine similarity, then find the closest FAQ question for five new questions,
using real embeddings from OpenAI.
:::
:::

:::step{type=concept title="Meaning as a point in space" file="03-embeddings/embeddings.py" line="1-7"}
An embedding model turns a text into a vector: a fixed-length list of numbers. `vectors.json` holds real ones from
OpenAI's `text-embedding-3-small`, made for this chapter with 256 numbers each (the model can give up to 1,536):

```json
"What is today's onion rate?": [-0.0303, -0.08319, 0.02585, ...256 numbers]
```

Each number on its own means nothing you could name. Together they place the text as a point in a space of 256
dimensions, where nearby points mean similar things. Picture it in two dimensions:

| Text | x | y |
|---|---|---|
| What is today's onion rate? | 0.9 | 0.2 |
| kanda bhav kay aahe aaj? | 0.8 | 0.3 |
| When is the co-op office open? | 0.1 | 0.9 |

The first two are close; the office question is far away. Real embeddings do the same with 256 numbers instead of 2.
:::

:::step{type=history title="You shall know a word by the company it keeps"}
:::before{title="Words as entries in a list"}
Early language programs treated words as unrelated symbols: "onion" and "kanda" were as different as "onion" and
"loan".
:::

In **1957** the linguist J. R. Firth wrote: "You shall know a word by the company it keeps": words that appear in
similar sentences have similar meanings. In **2013** Tomas Mikolov and colleagues at Google published **word2vec**,
which learned a vector for every word from billions of words of text, so that similar words got nearby vectors.
Sentence embeddings followed. In **January 2024** OpenAI released `text-embedding-3-small` and `-large`, trained so that
the first numbers of a vector carry the most meaning: you can ask for fewer dimensions, as this chapter does, and keep
most of the quality.

:::solved
**Similar meaning, nearby numbers.** Search by meaning in any language, and the foundation of retrieval in chapter 19.
:::

:::timeline
- **1957** Firth: meaning from context.
- **2013** word2vec.
- **2024** text-embedding-3, with shortenable vectors.
:::
:::

:::step{type=concept title="Cosine similarity" file="03-embeddings/embeddings.py" line="10-13"}
How close are two vectors? The usual measure is the **cosine** of the angle between them:

```text
cosine(a, b) = (a1*b1 + a2*b2 + ...) / (length of a * length of b)
length of a  = square root of (a1*a1 + a2*a2 + ...)
```

| Cosine | The two vectors | Meaning |
|---|---|---|
| 1 | point the same way | the same meaning |
| 0 | at right angles | unrelated |
| -1 | point opposite ways | opposite (rare in practice) |

Only the direction counts, not the length: `[3, 4]` and `[6, 8]` have cosine 1.
:::

:::step{type=task task=cosine title="Your turn: cosine similarity" file="03-embeddings/embeddings.py" line="10-13"}
Finish `cosine(a, b)`: the dot product of `a` and `b` (the sum of `x * y` for each pair), divided by the product of
their lengths.

Press **Check**.
:::

:::step{type=task task=closest_question title="Your turn: the closest FAQ question" file="03-embeddings/embeddings.py" line="16-18"}
Finish `closest_question(query, faq)`: return the key of `faq` whose vector has the highest cosine with `query`.
(`max(faq, key=...)` does it in one line.)

```bash run
cd /workspace/03-embeddings && python main.py
```

Press **Check**.
:::

:::step{type=try title="Five questions, five right answers, one weak one"}
```text
$ python main.py
'kanda bhav kay aahe aaj?'                   -> "What is today's onion rate?" (0.155)
'Can I keep my tomatoes cold for a week?'    -> 'How much does cold storage cost?' (0.425)
'Is the office open on Sunday?'              -> 'When is the co-op office open?' (0.613)
'I need money to buy seeds'                  -> 'How much crop loan can I get?' (0.354)
'My vines were sprayed on Monday, can I pick them on Friday?' -> 'When can I harvest grapes after spraying?' (0.628)
```

Every question found its FAQ entry, including "I need money to buy seeds", which shares no word with "crop loan", and
the vines question, which never says "grapes" or "harvest".

Now look at the numbers. "kanda bhav kay aahe aaj?" found the right entry with a cosine of only **0.155**: it was the
closest of five, but not close. The model understands Marathi in English letters far less well than English, as the
tokens of chapter 2 already hinted. With a sixth FAQ entry that was a little more similar by accident, it would have
picked the wrong one. Closest is not the same as close; chapter 18 adds a threshold so a weak match can say "no
answer" instead.
:::

:::step{type=predict title="Guess first"}
:::question
You make a vector for the same question with a different embedding model, and compare it with the vectors in
`vectors.json`. What happens?
:::
- [ ] It works: vectors are vectors
- [x] The cosines are meaningless: each model has its own space
- [ ] Python refuses to compare them
:::explain
Vectors are only comparable when they come from the same model (and, here, the same number of dimensions).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Two texts have a cosine of 0.95. What does that tell you?
:::
- [x] Their meanings are very similar
- [ ] They share 95% of their words
- [ ] One is 95% as long as the other
:::explain
Cosine measures the direction of the meaning vectors, not words or length.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is a closest match with cosine 0.155 risky?
:::
- [ ] Cosines below 0.5 are errors
- [x] It was only the best of a few weak candidates; it might not be related at all
- [ ] The vector is too short
:::explain
"Closest" always returns something. A threshold decides whether that something is good enough.
:::
:::

:::step{type=deep-dive title="Go deeper: embeddings in practice"}
**Cost.** `text-embedding-3-small` costs $0.02 per million tokens: embedding all ten texts here cost 85 tokens, a tiny
fraction of a cent.

**Dimensions.** More dimensions keep more detail but use more memory and slower search. 256 to 1,536 is usual for
small models; measure on your own data.

**Where vectors live.** Comparing a question with five vectors is instant. With a million documents you need a
**vector store** with a fast index (chapter 18).
:::

:::step{type=recap}
You can now:

- explain an embedding as a point in a space of meaning;
- compute cosine similarity, and read 1, 0 and -1;
- find the closest text by meaning, with no words in common;
- tell "closest" from "close", from real scores.

Next, chapter 4: inside a transformer, attention and how a model picks its next word.

:::photo{src="/lesson-images/langchain/lc-03-notes.webp" alt="Handwritten notes about embeddings: Embedding = meaning as numbers; Cosine: 1 same, 0 unrelated; No words in common, same meaning; kanda bhav: closest, 0.155; Closest is not close" ai="true"}
One page of notes for this chapter.
:::
:::
