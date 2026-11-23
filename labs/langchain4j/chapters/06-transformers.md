:::step{type=story title="What does 'it' mean?"}
A passenger writes to Setu: "The train left Lonavala on time, but it was late into Karjat because it stopped at the
ghat signal." There are two "it"s in that sentence. You knew at once that both mean the train, not Lonavala and not
the signal. To know that, you had to look back across the whole sentence and decide which earlier words mattered for
each "it".

Your bigram model from chapter 3 looks back one word. It cannot do this, and neither could any model for decades. The
idea that fixed it is called **attention**, and the architecture built on it, the **transformer**, is the "T" in GPT
and the engine inside every large language model you will call from this chapter on.

:::mission
Write the two calculations at the heart of a transformer: softmax, which turns scores into probabilities (with the
temperature knob every chat API has), and attention, which decides which words matter to each word.
:::
:::

:::step{type=concept title="Scores to probabilities: softmax and temperature"}
At the end of every step, a language model has a **score** (called a logit) for every token in its vocabulary: how
well that token would continue the text. After "The Ghat Express is running", the scores might be:

| Next word | late | early | smoothly | backwards |
|---|---|---|---|---|
| Score | 4.0 | 2.5 | 2.0 | -1.0 |

Scores are not probabilities: they can be negative and do not add up to 1. **Softmax** converts them: take `e` to the
power of each score (`Math.exp`), so every value is positive and bigger scores grow much bigger, then divide each by
the total, so they add up to 1.

Before that, every score is divided by the **temperature**:

1. temperature **1**: the model's own probabilities;
2. temperature **below 1** (say 0.2): differences grow, and the top word becomes nearly certain;
3. temperature **above 1** (say 2): differences shrink, and unlikely words get a real chance.

The model then **samples** the next token from these probabilities, like a weighted lottery. That is why the same
question can get different answers, and why chat APIs offer a `temperature` setting: low for facts and data
extraction, higher for creative writing (chapter 10).

One practical detail every real implementation has: `Math.exp(1000)` is `Infinity`, so subtract the largest score
from every score first. It changes nothing in the result (the common factor cancels in the division) and keeps the
numbers small.

**Check yourself:** at a temperature close to 0, what does sampling become? (Always picking the highest score:
greedy, and the same answer every time.)
:::

:::step{type=example title="Worked example: softmax by hand" file="06-transformers/src/main/java/com/setu/Attention.java" line="9-14"}
Softmax of the scores [2, 1, 0] at temperature 1:

| Step | late (2) | early (1) | smoothly (0) |
|---|---|---|---|
| subtract the largest (2) | 0 | -1 | -2 |
| `Math.exp` | 1.000 | 0.368 | 0.135 |
| divide by the sum (1.503) | **0.665** | **0.245** | **0.090** |

At temperature 0.5, divide first: [4, 2, 0], and the same steps give 0.867, 0.117, 0.016: sharper. In Java the three
steps are three loops over the array: find the maximum of `score / temperature`; fill a new array with
`Math.exp(score / temperature - max)` and add them up; divide each by the sum.
:::

:::step{type=task task=softmax_temperature title="Your turn: softmax with temperature" file="06-transformers/src/main/java/com/setu/Attention.java" line="9-14"}
Finish `Attention.softmax(scores, temperature)`: divide every score by the temperature, subtract the largest of
those, take `Math.exp` of each, and divide each by their sum.

Press **Check**.
:::

:::step{type=history title="Attention is all you need"}
:::before{title="Reading one word at a time"}
From the 1990s, neural language models were **recurrent** networks (RNNs, and from 1997 the improved LSTMs): they read
a sentence one word at a time, squeezing everything read so far into one vector of numbers. By the end of a long
sentence the beginning had faded, and because each word waited for the one before, training could not use the
thousands of parallel cores of a graphics card.
:::

In **2014** Dzmitry Bahdanau, Kyunghyun Cho and Yoshua Bengio added **attention** to translation networks: at each
output word, the network could look back at every input word and weigh how much each one mattered. In **June 2017**
eight researchers at Google, Ashish Vaswani and seven colleagues, asked what happens if attention is the only thing a
network uses. Their paper, **"Attention Is All You Need"**, described the **transformer**: every word looks at every
other word at once, in parallel, in many layers.

:::photo{src="/lesson-images/langchain4j/transformer-diagram.webp" alt="The transformer architecture drawn as two stacks of coloured blocks on a black background, labelled multi-headed self-attention, feed-forward network and norm, with embeddings at the bottom" credit="dvgodoy" license="CC BY 4.0" source="https://commons.wikimedia.org/wiki/File%3ATransformer%2C_full_architecture.png"}
The transformer, as drawn after the 2017 paper: layers of attention and feed-forward blocks.
:::

Transformers trained far faster than recurrent networks on graphics cards, and they kept getting better as they got
bigger. In **2018** OpenAI trained one to predict the next word over thousands of books and called it a **Generative
Pre-trained Transformer**: GPT. Google's BERT, the same year, used transformers to understand search queries.

:::solved
**Every word sees every word.** Attention removed the bottleneck of reading in order. A transformer with 128,000 tokens
of context relates the last word of a long document directly to the first.
:::

:::timeline
- **1997** LSTM: recurrent networks that remember a little longer.
- **2014** Attention for translation (Bahdanau, Cho and Bengio).
- **2017** "Attention Is All You Need": the transformer.
- **2018** GPT and BERT, both transformers.
- **2020** GPT-3: a transformer with 96 layers.
:::

:::funfact
The paper's title is a nod to the Beatles song "All You Need Is Love". It is one of the most cited computer science
papers ever written.
:::
:::

:::step{type=concept title="Attention: which words matter to this word?"}
Inside a transformer, every token carries three vectors, all computed from its embedding (chapter 5) by learned
weights (chapter 2):

1. a **query**: what this token is looking for ("it" looks for the thing that moves on a schedule);
2. a **key**: what this token offers ("train" offers "I am a vehicle that moves");
3. a **value**: the information this token passes on if chosen.

For one token, attention does three things:

1. **score** every token: the dot product of this token's query with that token's key, divided by `√d` (d is the
   vector length; the division keeps scores from growing with the vector size);
2. **softmax** the scores, at temperature 1, into weights that add up to 1;
3. mix the values with those weights (a high weight passes on most of that token's information).

:::diagram{name="l4j-attention"}
The query of "it" is compared with the key of every word; softmax turns the scores into weights; the train gets the most attention.
:::

Your task is steps 1 and 2: the **attention weights**. They are the part that decides; step 3 is a weighted sum.

A real transformer does this for every token at once, with dozens of attention **heads** per layer (each learning a
different kind of relation: grammar, meaning, who did what) and dozens of layers. The queries, keys and values are not
written by anyone; they are learned in training, the same way your neuron learned its weights.
:::

:::step{type=task task=attention_weights title="Your turn: attention weights" file="06-transformers/src/main/java/com/setu/Attention.java" line="25-29"}
Finish `Attention.weights(query, keys)`: for each key, the score is `dot(query, key) / Math.sqrt(query.length)`;
return `softmax` of those scores at temperature 1.0.

```bash run
cd /workspace/06-transformers && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="Temperature, and what 'it' attends to"}
```text
$ mvn -q compile exec:java
temperature 0.2: late 1.00  early 0.00  smoothly 0.00  backwards 0.00  
temperature 1.0: late 0.73  early 0.16  smoothly 0.10  backwards 0.00  
temperature 2.0: late 0.52  early 0.25  smoothly 0.19  backwards 0.04  
'it' attends to train    0.46
'it' attends to station  0.18
'it' attends to it       0.36
```

At temperature 0.2, "late" is practically certain (1.00). At 1.0 it is 73% likely, and at 2.0 only about half, with
"backwards" now at 4%: turn the temperature up too far and a model starts saying odd things, which is exactly what you
see from a chat model with a high temperature.

In the second part, "it" gives the train 0.46 of its attention and the station 0.18. These query and key vectors were
written by hand for the example; in a real model they are learned, there are 768 to 12,288 numbers instead of 3, and
a single sentence passes through 96 layers of this.
:::

:::step{type=concept title="Putting it all together: how an LLM answers"}
You have now built, in miniature, every part of a language model. Here is how they fit when Setu asks gpt-4o-mini a
question:

:::diagram{name="l4j-llm-pipeline"}
Text is split into tokens, tokens become embeddings, layers of attention refine them, the last layer scores every possible next token, softmax and temperature pick one, and the loop repeats.
:::

1. **Tokens** (chapter 4): the question is split into tokens, about 15 for a short question.
2. **Embeddings** (chapter 5): each token becomes a vector.
3. **Layers** (chapters 2 and 6): dozens of layers of attention and neurons refine every vector, using every other
   token in the context window.
4. **Scores**: the last layer gives a score for each of the ~200,000 possible next tokens.
5. **Softmax and temperature** (this chapter): scores become probabilities; one token is sampled.
6. **Repeat**: the new token is added to the text, and the whole model runs again for the next one, until it produces
   a special "end" token or reaches the maximum length.

Step 6 explains two things you will notice from chapter 7 on. Answers **stream** word by word, because they are
literally produced one token at a time. And **output tokens cost more** than input tokens: the input is read in one
parallel pass, but every output token needs a full run of the model.
:::

:::step{type=predict title="Guess first"}
:::question
You ask a chat model the same question twice with temperature 1.0 and get two different answers. Why?
:::
- [ ] The model learned something between the two calls
- [x] Each token is sampled from probabilities, so different choices lead to different answers
- [ ] The server is broken
:::explain
The model is the same; the sampling differs. One different early token sends the rest of the answer in another
direction. With temperature 0 the answers become (almost) the same every time.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What made transformers better than the recurrent networks before them?
:::
- [ ] They use fewer parameters
- [x] Every token attends to every other token at once, so nothing fades and training runs in parallel
- [ ] They only work in English
:::explain
Recurrent networks read one word at a time and forgot the beginning. Attention connects every pair directly, and the
parallel computation suits graphics cards, so transformers could be trained much bigger.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does a long answer take longer than a long question?
:::
- [ ] The model reads questions faster because they are shorter
- [x] The question is read in one pass, but each answer token needs its own full pass of the model
- [ ] Answers go through more servers
:::explain
Generation is a loop, one token per pass. That is also why streaming exists (chapter 16): show each token as soon as
it is made.
:::
:::

:::step{type=deep-dive title="Go deeper: what this chapter left out"}
**Values and multiple heads.** Real attention also mixes the value vectors with your weights, and runs many heads in
parallel, whose results are joined and passed on.

**Position.** Attention alone ignores order ("train left station" and "station left train" look alike), so
transformers add position information to each token's vector.

**Causal masking.** A model generating text must not peek at words that come later, so each token attends only to the
tokens before it.

**The KV cache.** Recomputing every key and value for every new token would be wasteful. Servers keep them in memory
between steps, which is one reason long contexts need a lot of memory.

**Top-p and top-k.** Besides temperature, APIs offer `top_p` (sample only from the most likely tokens that together
make up p of the probability) and `top_k`. Chapter 10 sets them from LangChain4j.
:::

:::step{type=recap}
You can now:

- turn scores into probabilities with softmax, and explain what temperature does to them;
- compute scaled dot-product attention weights, the core of a transformer;
- explain why transformers replaced recurrent networks;
- describe how an LLM answers, from tokens to sampling, and why answers stream and output tokens cost more.

That is the end of Part 1: you know what is on the other side of the call. Next, chapter 7: Setu calls a real model for
the first time, with nothing but Java's own HTTP client.

:::photo{src="/lesson-images/langchain4j/l4j-06-notes.webp" alt="Handwritten notes about transformers: softmax turns scores into probabilities; low temperature is sure; high temperature is surprising; attention: which words matter; one token at a time, then repeat" ai="true"}
One page of notes for this chapter.
:::
:::
