:::step{type=story title="Big cat is not tiger, to a computer"}
Chapter 1 ended with a failure. The ranger asked about a *big cat*; the manual says *tiger*. To keyword search those are
different strings, so it found nothing. A person would never make that mistake: we know a tiger is a big cat, that a
trail is a path, that "trail cameras need new cells" is a question about camera trap batteries.

What Fieldbook needs is a way to compare **meanings**, and computers only compare numbers. So the plan is to turn every
piece of text into a list of numbers such that texts with similar meanings get similar numbers. That list is called an
**embedding**, and it is the foundation of every vector database.

You will make embeddings on your own CPU, with a small open model that is already inside your lab machine: no internet,
no API key, no cost, the same numbers every time.

:::mission
Turn sentences into 384 numbers each, then measure how alike two of them are with cosine similarity, and find out where
meaning-based comparison surprises you.
:::
:::

:::step{type=concept title="An embedding: a text as a point in space" file="02-embeddings/fieldbook.py" line="60-71"}
An embedding model reads a text and outputs a fixed-length list of numbers, a **vector**. Fieldbook uses
**BAAI/bge-small-en-v1.5**, published in 2023 by the Beijing Academy of Artificial Intelligence: about 33 million learned
weights, and every text, from one word to a paragraph, comes out as exactly **384 numbers**.

```python
>>> embed(["A tiger crossed the path."])[0][:8]
[-0.019, -0.013, 0.011, 0.056, -0.038, -0.004, 0.043, 0.017]   # and 376 more
```

No single number means "animal" or "danger". Meaning is spread over all 384 together. What matters is where the point
lands compared with other points: the model was trained on millions of pairs of related texts (a question and its
answer, a title and its article) to put related texts close together and unrelated ones far apart.

Think of two dimensions instead of 384 to picture it: "tiger", "leopard" and "big cat" land in one neighbourhood,
"battery" and "memory card" in another. Searching by meaning becomes finding the nearest points.

| Piece | In this course |
|---|---|
| the model | BAAI/bge-small-en-v1.5, through the `fastembed` library, on your CPU |
| one text in | any length up to about 400 words (longer text is cut off) |
| one vector out | 384 numbers, stored as `float32` (4 bytes each: 1,536 bytes a text) |

`model()` loads it once (`@lru_cache` remembers it), and `model().embed(texts)` gives the vectors one by one, as a
**generator**: they are made only as you take them.
:::

:::step{type=task task=embed_texts title="Your turn: 384 numbers for every text" file="02-embeddings/fieldbook.py" line="67-71"}
Write `embed(texts)`: take every vector from `model().embed(list(texts))` (wrap it in `list(...)`), and return them as a
NumPy array with `dtype=np.float32`, one row per text.

A list of two texts gives a matrix with 2 rows and 384 columns. Press **Check**.
:::

:::step{type=history title="You shall know a word by the company it keeps"}
:::before{title="Words as labels"}
To a computer, "tiger" and "big cat" were just different strings. Systems that needed meaning used hand-made thesauri,
lists of synonyms written by people, which never covered everything and never kept up.
:::

In **1957** the linguist J. R. Firth wrote: "You shall know a word by the company it keeps." Words used in the same
contexts have related meanings. **Latent semantic analysis** (**1990**) turned that into mathematics: count which words
appear together across many documents and compress the counts into a few hundred numbers per word. In **2013** Tomas
Mikolov's team at Google released **word2vec**, which learned a vector per word from billions of words of text, fast
enough for anyone to use; the famous result was that *king* minus *man* plus *woman* lands near *queen*. Vectors for
whole **sentences** followed: Sentence-BERT (**2019**) trained a transformer to put sentences with the same meaning
close together, and a stream of small, strong open models followed, BGE among them (**2023**).

:::solved
**Meaning you can compute with.** Similar texts get similar vectors, so "find texts like this one" becomes "find the
nearest points".
:::

:::timeline
- **1957** Firth: the company a word keeps.
- **1990** Latent semantic analysis.
- **2013** word2vec.
- **2019** Sentence-BERT: vectors for sentences.
- **2023** BGE and other small open embedding models.
:::

Tomas Mikolov, who led the team at Google that released word2vec in 2013.

:::photo{src="/lesson-images/rag/mikolov.webp" alt="Tomas Mikolov, a young man with long hair tied back, smiling slightly, in front of a building" credit="Jindřich Nosek (NoJin)" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ATom%C3%A1%C5%A1_Mikolov_%282020%29.jpg"}
Tomas Mikolov in 2020.
:::
:::

:::step{type=concept title="Cosine similarity: how alike two directions are" file="02-embeddings/fieldbook.py" line="74-78"}
How do you say how close two vectors are? Picture each one as an arrow from the origin. Two texts about the same thing
point in nearly the same direction. The measure is the **cosine** of the angle between the arrows:

| Angle | Cosine | Means |
|---|---|---|
| 0 degrees | 1.0 | same direction: same meaning |
| 90 degrees | 0.0 | unrelated |
| 180 degrees | -1.0 | opposite |

The formula uses two things you can compute for any two lists of numbers:

```text
cosine(a, b) = dot(a, b) / (length(a) * length(b))

dot(a, b)  = a[0]*b[0] + a[1]*b[1] + ... (all 384 pairs)
length(a)  = square root of dot(a, a)
```

Dividing by the lengths means only the direction counts: `[1, 1]` and `[2, 2]` point the same way, so their cosine is
exactly 1. NumPy does each part in one call: `np.dot(a, b)` and `np.linalg.norm(a)`.
:::

:::step{type=task task=cosine title="Your turn: how alike two vectors are" file="02-embeddings/fieldbook.py" line="74-78"}
Write `cosine(a, b)`: the dot product of `a` and `b`, divided by the product of their lengths. Return it as a plain
Python `float`.

```bash run
cd /workspace/02-embeddings && python similar.py
```

Press **Check**.
:::

:::step{type=try title="What the model thinks is alike"}
```text
$ python similar.py
model loaded in 0.87 s
12 sentences -> 384 numbers each, in 100 ms

0.690  'A tiger crossed the path.' / 'A big cat walked across the trail.'
0.802  'A tiger crossed the path.' / 'A leopard crossed the road.'
0.420  'A tiger crossed the path.' / 'Change the camera trap batteries every 21 days.'
0.728  'Change the camera trap batteries every 21 days.' / 'How often do the trail cameras need new cells?'
0.796  'The core zone is closed to visitors.' / 'Tourists may not enter the core zone.'
0.834  'The core zone is closed to visitors.' / 'The core zone is open to visitors.'

The first 8 numbers of the first sentence: [-0.019, -0.013, 0.011, 0.056, -0.038, -0.004, 0.043, 0.017]
```

Read it line by line, because each line teaches something:

1. **Tiger and big cat: 0.690.** Not one word in common (apart from "the"), and still clearly related. This is what
   keyword search could not do.
2. **Tiger and leopard: 0.802**, even higher. Both sentences are "an animal crossed a path": the model sees the shape of
   the event, not only the animal.
3. **Tiger and batteries: 0.420.** Unrelated, but not 0. With this model, scores for unrelated texts usually sit around
   0.3 to 0.5, so a score means something only **compared with other scores** for the same question.
4. **Batteries and "trail cameras need new cells": 0.728.** Different words, same question. This is the pair that will
   make Fieldbook useful.
5. **The trap: "closed" against "open": 0.834**, higher than the true paraphrase on line 5 (0.796). The two sentences
   share almost every word and the same topic; one small word flips the meaning, and the vectors barely notice.
   Embeddings capture what a text is **about**, not whether it says yes or no. Remember this when a search returns a
   passage that says the opposite of what was asked.

And the cost: 12 sentences in 100 ms on two CPUs, after under a second to load the model. The whole manual (31 sections)
takes about three seconds, once.
:::

:::step{type=predict title="Guess first"}
:::question
"The road is safe after dark." and "The road is not safe after dark." What cosine will they get?
:::
- [ ] About 0.0: they mean opposite things
- [ ] About -1.0: opposite meanings point opposite ways
- [x] High, above 0.9: they are about the same thing, and "not" changes few numbers
:::explain
Cosine -1.0 almost never happens for real texts. Negation is a known blind spot of embeddings; chapter 10's reranker,
which reads both texts together, handles it better.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why divide by the lengths in the cosine formula?
:::
- [x] So that only the direction counts: a longer vector is not "more similar" just for being longer
- [ ] To make the result an integer
- [ ] Because NumPy needs it
:::explain
Without the division you get the plain dot product, which grows with the lengths of the vectors.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Two different embedding models give vectors for the same text. Can you compare a vector from one with a vector from the other?
:::
- [ ] Yes, if both have 384 numbers
- [x] No: each model places texts in its own space; numbers from different models mean nothing to each other
- [ ] Only with cosine
:::explain
That is why changing the embedding model means embedding every document again, and why the model's name belongs next to
the vectors.
:::
:::

:::step{type=deep-dive title="Go deeper: choosing an embedding model"}
**Local or API.** bge-small runs on a laptop CPU and costs nothing per text. Hosted models (OpenAI's text-embedding-3
family, Cohere, Voyage, Google) are larger and usually somewhat better, cost a small amount per million tokens, and send
your text to another company. For a sanctuary's internal manual, local is the natural choice; many companies decide the
same for privacy alone.

**How to compare models.** The MTEB leaderboard (Massive Text Embedding Benchmark, on Hugging Face) scores models on
dozens of retrieval and similarity tasks. Use it to shortlist, then measure on **your own** questions, as chapter 12
does: a model that wins on web search may not win on a field manual.

**Size and dimensions.** Bigger models (768 or 1,024 numbers) are slower and need more memory per vector (chapter 7
counts the cost). Some newer models let you keep only the first part of the vector ("Matryoshka" embeddings) to save
space.

**The model in your lab** is an optimized ONNX file of 64 MB, run by ONNX Runtime without PyTorch, which is why it loads
in under a second and fits in a small machine. (Measured with the two sentences above: "The road is safe after dark."
and "The road is not safe after dark." score 0.941.)
:::

:::step{type=recap}
You can now:

- explain what an embedding is: a text as a point, where nearby means similar;
- make embeddings on your own CPU, as a float32 matrix with one row per text;
- compute cosine similarity, and read scores relative to each other;
- spot the limits: unrelated texts do not score 0, and negation barely moves a vector.

Next, chapter 3: searching a whole collection of vectors for the closest ones.

:::photo{src="/lesson-images/rag/rag-02-notes.webp" alt="Handwritten notes about embeddings: Text in, 384 numbers out; Similar meaning, nearby points; Cosine: same direction = 1; Scores are relative; Not does not move much" ai="true"}
One page of notes for this chapter.
:::
:::
