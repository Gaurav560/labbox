:::step{type=story title="Suitcase, baggage, samaan"}
In chapter 1, Setu's rules missed "How heavy can my suitcase be?" because nobody had written the word "suitcase". The
railway's FAQ page has the answer, under "How much baggage can I carry?". A person sees at once that the two questions
mean the same thing. Keyword matching never will: they share no important word.

What Setu needs is a way to compare **meanings**. Modern AI does it by turning every text into a list of numbers, so
that texts with similar meanings get similar lists. Those lists are called **embeddings**, and they are behind every
semantic search, every "related articles" box, and the retrieval step that lets a model answer from your own
documents (chapter 23).

:::mission
Compare two embeddings with cosine similarity, then answer passengers' questions from the FAQ by meaning, with a real
embedding model running inside your Java program.
:::
:::

:::step{type=concept title="Meaning as a list of numbers"}
An **embedding** is a vector: a list of numbers, always the same length for a given model. That length is the number
of **dimensions**. The model in your project gives every text **384** numbers:

```text
'refund' is 384 numbers, starting [-0.0457914, -0.028513711, 0.037330087, -0.004741748, -0.0062468387]
```

No single number means anything you can name (there is no "money" dimension). What matters is the whole list as a
direction in a 384-dimensional space. An **embedding model** is a neural network trained so that texts with similar
meanings point in similar directions: "refund" near "money back", "dog" near "puppy", and both far from "platform".

You cannot picture 384 dimensions, but you can picture 2. Imagine every text as an arrow on a sheet of paper: arrows
for "refund" and "money back" point almost the same way; "luggage" points somewhere else. The question "how similar
are these two meanings?" becomes "how small is the angle between these two arrows?".

:::diagram{name="l4j-embedding-space"}
Texts become arrows: refund and money back point nearly the same way, luggage points elsewhere; the angle between arrows measures how different the meanings are.
:::

Two kinds of models use embeddings. **Embedding models** (like this one, or OpenAI's text-embedding-3-small with 1,536
dimensions) produce them for search. **Language models** use them inside: the first thing an LLM does with each token
is look up its embedding, and every layer after that refines those vectors.

**Check yourself:** two embeddings have 384 numbers each. Does it make sense to compare an embedding from this model
with one from OpenAI's model? (No: different models, different spaces, even different lengths. Compare only
embeddings made by the same model.)
:::

:::step{type=history title="You shall know a word by the company it keeps"}
In **1957** the British linguist **J. R. Firth** wrote a sentence that became the motto of the field: "You shall know a
word by the company it keeps." Words used in similar sentences ("I want a ___ for my cancelled ticket": refund, money
back, reimbursement) tend to mean similar things. If a program records the company each word keeps, it captures
something of its meaning, without a dictionary.

:::before{title="Words as unrelated symbols"}
Counting models (chapter 3) treated every word as a separate symbol: "refund" and "reimbursement" were as different
as "refund" and "elephant". Anything learned about one word taught the program nothing about the others, so it needed
an example of every word in every situation.
:::

In **2013** **Tomas Mikolov** and colleagues at Google released **word2vec**, a small neural network that learned a
vector for every word by predicting its neighbours in billions of words of news. The vectors had a startling
property: directions meant something. The famous example was arithmetic on meaning: the vector of "king", minus
"man", plus "woman", landed closest to "queen".

:::solved
**Similar meaning, nearby numbers.** Embeddings turned meaning into geometry, and geometry is something computers are
very fast at. Later models embed whole sentences and documents, not just words; the model in your project, BGE small
from the Beijing Academy of Artificial Intelligence (2023), is one of them, small enough to run on a laptop.
:::

:::timeline
- **1957** Firth: "You shall know a word by the company it keeps."
- **2013** word2vec: a vector for every word, learned from text.
- **2018** Sentence embeddings from transformer models.
- **2022** OpenAI's ada-002: one embedding model for all text.
- **2023** BGE: small open embedding models that run anywhere.
:::
:::

:::step{type=example title="Worked example: how similar are two arrows?" file="05-embeddings/src/main/java/com/setu/Vectors.java" line="9-13"}
The standard measure is **cosine similarity**: the cosine of the angle between two vectors. It is 1 when they point the
same way, 0 when they are at right angles (unrelated), and -1 when they point in opposite directions.

Work it out by hand for two 2-number vectors, a = [3, 4] and b = [4, 3]:

| Step | Formula | Value |
|---|---|---|
| dot product | 3 × 4 + 4 × 3 | 24 |
| length of a | √(3² + 4²) | 5 |
| length of b | √(4² + 3²) | 5 |
| cosine | 24 / (5 × 5) | **0.96** |

Nearly the same direction: very similar. Notice that the lengths are divided out, so [3, 4] and [30, 40] have cosine 1:
same direction, same meaning, however long the arrow. In Java, one loop can build the three sums at once (the dot
product, and the two sums of squares), then one line divides.
:::

:::step{type=task task=cosine title="Your turn: cosine similarity" file="05-embeddings/src/main/java/com/setu/Vectors.java" line="9-13"}
Finish `Vectors.cosine(a, b)`: the dot product of `a` and `b`, divided by the length of `a` times the length of `b`
(a length is the square root of the sum of the squares, `Math.sqrt`).

Press **Check**.
:::

:::step{type=concept title="Search by meaning" file="05-embeddings/src/main/java/com/setu/Faq.java" line="12-32"}
Open `Faq.java`. It already has the two ingredients:

1. `MODEL`, a real embedding model, **BGE small**, quantised to about 24 MB. It runs inside your program on the CPU: no
   network, no API key, no cost. (LangChain4j ships it as a Maven dependency, `langchain4j-embeddings-bge-small-en-v15-q`.)
2. `ENTRIES`, five FAQ questions with their answers, and `embed(text)`, which returns a text's 384 numbers.

Searching by meaning is then three steps, and you will write them:

1. embed the passenger's question;
2. compare it with the embedding of every FAQ question, with your `cosine`;
3. return the answer of the FAQ question with the **highest** score.

This is called **semantic search**, and it is the same thing a vector database does for millions of documents
(chapter 22), just with a loop instead of an index. It is also the "retrieval" in retrieval-augmented generation:
find the right text first, then give it to the language model to answer from (chapter 23).
:::

:::step{type=task task=closest_question title="Your turn: answer by meaning" file="05-embeddings/src/main/java/com/setu/Faq.java" line="34-38"}
Finish `Faq.answer(question)`: embed the question, compare it with the embedding of each question in `ENTRIES` using
`Vectors.cosine`, and return the answer of the most similar one.

```bash run
cd /workspace/05-embeddings && mvn -q compile exec:java
```

The first run takes a few seconds longer: the model loads into memory.

Press **Check**.
:::

:::step{type=try title="Suitcase finds baggage"}
```text
$ mvn -q compile exec:java
'refund' is 384 numbers, starting [-0.0457914, -0.028513711, 0.037330087, -0.004741748, -0.0062468387]
refund   ~ money back 0.763
refund   ~ luggage    0.564
dog      ~ puppy      0.862
dog      ~ platform   0.612
My trip is cancelled, can I get a refund?
  -> Refunds: the full fare up to 24 hours before departure, half the fare after that.
How heavy can my suitcase be?
  -> Each passenger may carry 40 kg of luggage free of charge.
Can my puppy come along?
  -> Small pets travel in the guard's van, with a pet ticket of Rs 120.
```

Three questions, three right answers, and not one keyword in common: "suitcase" found "baggage", "puppy" found "cat or
dog", "refund" found "money back". Look at the scores too. "refund" and "money back" score 0.763, "dog" and "puppy"
0.862, while unrelated pairs still score about 0.6, not 0. With this model, every English text points roughly the same
general way, so the **absolute** number means little; what matters is **which candidate scores highest**. That is
why semantic search always ranks, and why a fixed "similar if above 0.5" rule rarely works without testing on your
own data.
:::

:::step{type=predict title="Guess first"}
:::question
A passenger asks "Is there a canteen on board?". No FAQ question contains "canteen" or "board". What will `Faq.answer`
return?
:::
- [x] The food answer: "canteen on board" is close in meaning to "food on the train"
- [ ] Nothing, because no keyword matches
- [ ] A random answer
:::explain
Embeddings compare meaning, so the food question wins (we ran it: it returns the pantry car answer). But semantic
search always returns **something**: asked "What is the capital of France?", the same code answers "Each passenger may
carry 40 kg of luggage free of charge." Real systems also check that the best score is good enough (chapter 22).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does cosine similarity measure?
:::
- [ ] How long two vectors are
- [x] How closely two vectors point in the same direction
- [ ] How many numbers two vectors share
:::explain
It ignores length and keeps direction. For embeddings, direction is meaning.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does the course run BGE small inside the program instead of calling an embedding API here?
:::
- [ ] It is more accurate than every API
- [x] It needs no network, no key and costs nothing, and 384 dimensions are plenty for short FAQ questions
- [ ] APIs cannot produce embeddings
:::explain
Small local embedding models are a real production choice for short texts and private data. Chapter 22 compares them
with OpenAI's embedding model, which has 1,536 dimensions and costs $0.02 per million tokens.
:::
:::

:::step{type=deep-dive title="Go deeper: embeddings in production"}
**Embed once, search many times.** Your `answer` embeds the five FAQ questions on every call. Real systems embed the
documents once, store the vectors, and embed only the incoming question. That store is a vector database (chapter 22).

**Normalised vectors.** Many models return vectors of length 1. Then the cosine is just the dot product, which is why
vector databases often offer "dot product" as a faster distance.

**Same model, both sides.** Documents and questions must be embedded with the same model and version. Changing the
embedding model means re-embedding everything you stored.

**Languages.** BGE small is trained on English; a Marathi question would match poorly. Multilingual embedding models
exist, and OpenAI's models handle many languages. Test with your real passengers' questions.
:::

:::step{type=recap}
You can now:

- explain embeddings as vectors whose directions encode meaning, and what dimensions are;
- compute cosine similarity, by hand and in Java;
- search by meaning with a real embedding model running inside a Java program;
- explain why semantic search ranks candidates rather than trusting an absolute score.

Next, chapter 6: the transformer. How attention lets a model use every word of the text at once, and how
temperature turns scores into the next word.

:::photo{src="/lesson-images/langchain4j/l4j-05-notes.webp" alt="Handwritten notes about embeddings: an embedding is a list of numbers; similar meaning, similar direction; cosine: 1 same, 0 unrelated; suitcase finds baggage; rank, do not trust one score" ai="true"}
One page of notes for this chapter.
:::
:::
