:::step{type=story title="One word at a time"}
When Navin answers "Today's onion rate is Rs 1,850 per quintal", the model behind it did not plan that sentence. It
picked "Today", then, reading "Today", picked "'s", then "onion", and so on, one token at a time, each time choosing from
about 200,000 possible next tokens. A whole answer is that loop, run a few dozen times.

Two ideas make that loop work, and both are small enough to write in plain Python. **Softmax** turns the model's raw
scores for every possible next token into probabilities, and its **temperature** decides how adventurous the choice
is. **Attention** lets each word decide which other words matter for it: what "it" refers to, which crop "the rate"
is about.

:::mission
Write softmax with a temperature and the attention weights of a transformer, and watch both change real choices.
:::
:::

:::step{type=concept title="From scores to probabilities: softmax" file="04-transformers/attention.py" line="5-8"}
At each step the model gives every token in its vocabulary a score (a "logit"). Scores can be any number, positive or
negative. Softmax turns them into probabilities that are positive and add up to 1:

```text
softmax(s)[i] = exp(s[i] / T) / (exp(s[0] / T) + exp(s[1] / T) + ...)
```

`T` is the **temperature**:

| Temperature | Effect | Used for |
|---|---|---|
| Low (0.2) | The top score takes almost everything | Facts, extraction: Navin's answers |
| 1.0 | The model's own probabilities | General chat |
| High (2.0) | Choices flatten out; unlikely tokens get a chance | Brainstorming |

One practical detail: `exp(1000)` overflows a float. Subtracting the largest score from every score first changes
nothing in the result (it cancels out in the division) and keeps the numbers small.
:::

:::step{type=task task=softmax_temperature title="Your turn: softmax with a temperature" file="04-transformers/attention.py" line="5-8"}
Finish `softmax(scores, temperature)`: subtract the largest score from each, divide by the temperature, take
`math.exp` of each, and divide each by their sum.

Press **Check**.
:::

:::step{type=history title="Attention is all you need"}
:::before{title="Reading in a line"}
Before 2017, language models read one word after another, carrying a memory forward (recurrent networks). Long
sentences faded: by the end, the beginning was half forgotten, and nothing could run in parallel.
:::

In **2014** Dzmitry Bahdanau, Kyunghyun Cho and Yoshua Bengio added **attention** to translation models: while writing
each word, the model could look back at every word of the source sentence and weigh which ones mattered. In **June
2017**, eight researchers at Google (Ashish Vaswani and colleagues) published **"Attention Is All You Need"**: a model
made of attention alone, the **transformer**, with no recurrence at all. Every word looks at every other word at once,
which made training fast on graphics cards. GPT (**2018**), GPT-3 (**2020**) and every model behind Navin are
transformers.

:::solved
**Every word sees every word.** Long-range meaning ("it" referring to something ten words back) without forgetting,
and training that runs in parallel on huge amounts of text.
:::

:::timeline
- **2014** Attention for translation.
- **2017** The transformer.
- **2018** GPT.
- **2020** GPT-3: 175 billion parameters.
:::
:::

:::step{type=concept title="Attention: which words matter to this word?" file="04-transformers/attention.py" line="11-14"}
Take "The farmer sprayed the vines because it rained". Which earlier word does "it" relate to? In a transformer, every
word gets three vectors: a **query** (what am I looking for?), a **key** (what do I offer?) and a value. The
attention of one word on the others is:

1. score each key: the dot product of the query with that key, divided by the square root of the vector length
   (so long vectors do not make the scores huge);
2. softmax the scores into weights that add up to 1.

The weights say how much of each word flows into the meaning of "it". A real model learns the query and key vectors
during training, has thousands of dimensions and runs dozens of attention "heads" in parallel; the arithmetic is the
same as yours.

:::diagram{name="lc-next-token"}
The model reads everything so far, scores every possible next token, picks one, adds it, and runs again.
:::
:::

:::step{type=task task=attention_weights title="Your turn: attention weights" file="04-transformers/attention.py" line="11-14"}
Finish `attention(query, keys)`: for each key, the dot product with the query divided by `math.sqrt(len(query))`; then
return `softmax` of those scores.

```bash run
cd /workspace/04-transformers && python main.py
```

Press **Check**.
:::

:::step{type=try title="Temperature and attention, in numbers"}
```text
$ python main.py
temperature 0.2: rate 0.88, price 0.12, spray 0.00, harvest 0.00
temperature 1.0: rate 0.49, price 0.33, spray 0.10, harvest 0.07
temperature 2.0: rate 0.38, price 0.31, spray 0.17, harvest 0.15

attention of 'it': farmer 0.27, vines 0.39, rained 0.34
```

After "What is today's onion ...", the same four scores give very different choices. At 0.2, "rate" wins 88% of the
time and "spray" never does. At 2.0, "spray" gets 17%: an answer could go somewhere odd. That is why Navin will run at
temperature 0 (chapter 8).

The attention numbers come from small made-up vectors, so read them as an illustration: with these vectors, "it" looks
most at "vines". In a trained model, the learned vectors decide; for "because it rained", a good model would attend to
the weather, not the vines. Attention is a mechanism; what it attends to is learned.
:::

:::step{type=predict title="Guess first"}
:::question
Navin must answer "What is the onion rate?" the same way every time. Which temperature?
:::
- [x] 0, or close to it
- [ ] 1.0
- [ ] 2.0
:::explain
Low temperature makes the most likely token win almost always: steady, repeatable answers.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What do softmax's outputs always do?
:::
- [ ] Sum to 0
- [x] Lie between 0 and 1 and sum to 1
- [ ] Keep the original scores
:::explain
That is what makes them probabilities the model can sample from.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What made the transformer faster to train than earlier models?
:::
- [ ] It has fewer parameters
- [x] All words attend to all words at once, so the work runs in parallel
- [ ] It skips the softmax
:::explain
Recurrent models read word by word; transformers process the whole text in one go on a graphics card.
:::
:::

:::step{type=deep-dive title="Go deeper: from attention to an answer"}
**The full loop.** A transformer stacks dozens of layers of attention and small neural networks; the last layer gives a
score to every token; softmax and sampling pick one; the token is appended and the loop runs again.

**Why answers cost output tokens.** Each output token is one pass through the whole model, which is why output tokens
cost more than input tokens (chapter 9).

**Context and cost.** Attention compares every token with every other, so its work grows with the square of the
context length. Long prompts are slower as well as dearer.
:::

:::step{type=recap}
You can now:

- turn scores into probabilities with softmax, and explain temperature;
- compute attention weights from a query and keys;
- describe how a transformer writes an answer one token at a time;
- choose a temperature for a help desk, and say why.

That ends Part 1. Next, chapter 5: Navin's first call to a real model, with nothing but an HTTP request.

:::photo{src="/lesson-images/langchain/lc-04-notes.webp" alt="Handwritten notes about transformers: One token at a time; Softmax: scores to probabilities; Low temperature: steady; Attention: who looks at whom; Transformer, 2017" ai="true"}
One page of notes for this chapter.
:::
:::
