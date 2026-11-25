:::step{type=story title="Big cat is not tiger, to a computer"}
Chapter 1 ended with a failure, and it is worth sitting with it for a moment, because this whole chapter exists to fix
it.

A ranger typed a perfectly sensible question into Fieldbook: *"Where was the big cat seen last week?"* The sanctuary
manual has the answer. It just never uses the words *big cat*. It says *tiger*. Keyword search compares letters, and
the letters of "big cat" and "tiger" have nothing in common, so Fieldbook came back empty-handed, while the answer sat
right there in the manual.

Now think about how *you* read that question. You did not compare letters. You knew at once that a tiger is a big cat,
that a trail is a kind of path, and that a ranger asking "do the trail cameras need new cells?" is asking about the
**batteries** in the camera traps. You compared **meanings**, without even noticing you were doing it.

That is what Fieldbook needs: a way to compare meanings. There is one problem. A computer cannot compare meanings. It
can only compare **numbers**. So the plan for this chapter is a clever one: we will turn every piece of text into a list
of numbers, chosen so that texts with **similar meanings** end up with **similar numbers**. Then "do these two sentences
mean the same thing?" becomes "are these two lists of numbers close?", and that is a question a computer can answer
quickly and exactly.

That list of numbers has a name, the **embedding** of the text. Every vector database you will ever use, and every
search engine that understands meaning, is built on embeddings. By the end of this chapter you will have made your own.

You will make them on your own machine's processor, with a small model that is already installed in your lab: no
internet, no account, no API key, no cost, and the same numbers every time you run it.

:::mission
Turn sentences into 384 numbers each, measure how alike two of them are with cosine similarity, and find out where
comparing meanings works beautifully and where it quietly fails.
:::
:::

:::step{type=concept title="An embedding: a text as a point in space"}
An **embedding model** is a program that reads a piece of text and gives back a fixed-length list of numbers. That list
is called a **vector**, and the vector of a text is its **embedding**.

The model in your lab always gives back **384 numbers**, whatever the length of the text: one word, one sentence or a
whole paragraph. The picture below shows it with three real sentences from the sanctuary manual. Each sentence goes into
the model, and a row of 384 numbers comes out (only the first 4 are shown).

:::diagram{name="rag-embed"}
Text in, 384 numbers out. The numbers are the model's real output, and so are the two scores at the bottom.
:::

**What are the 384 numbers?** Each one is a measurement the model makes of the text. Together, the 384 measurements
describe what the text is about. No person decided what any of them measures: the model worked them out by itself while
it was trained, and none of them lines up with a word you could name. There is no "animal" number and no "danger"
number; the meaning is spread across all 384 together. So you never read an embedding one number at a time. You only
**compare** whole embeddings with each other.

**Why exactly 384?** Because the people who built this model chose that size when they designed it. Every text it reads
comes out as exactly 384 numbers, never more and never fewer, and that cannot be changed after the model is trained.
The number of values in a vector is called its **dimension**, so you will often read that bge-small makes
"384-dimensional embeddings". Other models chose other sizes:

| Model | Numbers per text (its dimension) |
|---|---|
| bge-small (the one in your lab) | 384 |
| bge-base, and many mid-size models | 768 |
| bge-large | 1,024 |
| OpenAI's text-embedding-3-small | 1,536 |

More numbers give a model more room to tell fine differences in meaning apart, but every vector then takes more memory
and is slower to compare. 384 is a small, fast size that is good enough for a manual of a few hundred pages. Two rules
follow:

- every vector from the same model has the same length, so any two of them can be compared;
- vectors from **different** models can never be compared, even when their lengths match, because each model measures
  different things.

**Why this helps Fieldbook.** The model was trained so that **texts with similar meanings get similar vectors.** "A
tiger crossed the path." and "A big cat walked across the trail." share almost no words, yet their two rows of numbers
are close, so they score **0.69**. The sentence about batteries is about something else, so its row is further away, and
it scores only **0.42** against the tiger. You will compute these scores yourself later in this chapter.

Comparing meanings is now comparing lists of numbers, which a computer does quickly and exactly. To search the manual by
meaning, you will:

1. turn every section of the manual into a vector, once;
2. turn the ranger's question into a vector, the same way;
3. find the sections whose vectors are closest to the question's vector.

Because a vector is a list of 384 numbers, you can also think of it as a **point**: two numbers mark a point on a sheet of
graph paper, and 384 numbers mark a point in a space with 384 directions. "Closest vectors" and "nearest points" mean
the same thing, and later chapters use both.

**How did the model learn which texts are similar?** During training, it was shown millions of pairs of texts that
belong together (a question and its answer, a title and its article, two ways of saying the same thing) and millions of
pairs that do not. Each time, it adjusted its internal settings slightly, so that related texts got closer vectors and
unrelated texts got vectors further apart. Those internal settings are called **weights**; this model has about 33
million of them. After that training, it gives sensible vectors even for sentences it has never seen before.

Check yourself: what does it mean that this model is "384-dimensional"? (Every text it reads becomes a vector of exactly
384 numbers.) And if two sentences have very similar embeddings, what does that tell you? (That they mean something
similar, as far as the model can tell, even if they use different words.)
:::

:::step{type=concept title="Reading the code: the model and embed()" file="02-embeddings/fieldbook.py" line="60-71"}
Open `02-embeddings/fieldbook.py`. Two functions do all of this chapter's embedding work. Let's read them line by line.

```python
@lru_cache(maxsize=1)
def model():
    """The embedding model, BAAI/bge-small-en-v1.5: 33 million weights, on your own CPU. Loaded once."""
    from fastembed import TextEmbedding
    return TextEmbedding("BAAI/bge-small-en-v1.5")
```

- `TextEmbedding("BAAI/bge-small-en-v1.5")` loads the model. **BAAI/bge-small-en-v1.5** is its name: published in 2023
  by the Beijing Academy of Artificial Intelligence, small ("small"), for English ("en"). It is free to use, and its
  files are already inside your lab machine.
- `fastembed` is the library that runs it. It is built to run models fast on an ordinary processor, without a graphics
  card.
- Loading the model takes almost a second. You do not want to pay that every time you embed a sentence. That is what
  `@lru_cache(maxsize=1)` is for: it is a Python decorator that **remembers** the function's answer. The first call to
  `model()` loads the model and keeps it; every later call gets the same loaded model back instantly.

Now the function you will write:

```python
def embed(texts):
    """One row of 384 numbers for each text, as a float32 matrix (len(texts) rows, 384 columns)."""
```

`embed` takes a list of texts and must give back a **matrix**: a table of numbers with one **row** per text and **384
columns**. Three sentences in, a table of 3 rows by 384 columns out. This shape matters, because every later chapter
expects it: row 0 is the vector of the first text, row 1 of the second, and so on.

Two small details will matter when you write it:

1. **The model hands you vectors one at a time.** `model().embed(texts)` does not return a finished list. It returns a
   **generator**: something that produces the vectors only when you ask for them, one by one. Wrapping it in
   `list(...)` asks for all of them and collects them into a list.
2. **The numbers should be `float32`.** That is the standard size for embedding numbers: 4 bytes each, so one text costs
   384 times 4 = 1,536 bytes. NumPy's `np.array(..., dtype=np.float32)` turns the list of vectors into exactly the
   matrix we want, with that number type.

Here is what one row looks like (only its first 8 numbers):

```python
>>> embed(["A tiger crossed the path."])[0][:8]
[-0.019, -0.013, 0.011, 0.056, -0.038, -0.004, 0.043, 0.017]   # and 376 more
```

Small numbers, some positive, some negative, none of them meaningful alone. Together, all 384 are the sentence's
embedding.

| Piece | In this course |
|---|---|
| the model | BAAI/bge-small-en-v1.5, run by the `fastembed` library on your processor |
| one text in | anything from one word to about 400 words (longer text is cut off at the end) |
| one vector out | 384 numbers of type `float32`: 1,536 bytes per text |
:::

:::step{type=task task=embed_texts title="Your turn: 384 numbers for every text" file="02-embeddings/fieldbook.py" line="67-71"}
Write `embed(texts)` in `02-embeddings/fieldbook.py`. In words, it does three things:

1. call `model().embed(...)` with the texts (pass them as `list(texts)`, so any sequence of strings works);
2. wrap the result in `list(...)` so you collect every vector;
3. turn that list into a NumPy matrix with `np.array(..., dtype=np.float32)` and return it.

It fits on one line. When it works, a list of two texts gives a matrix of shape `(2, 384)`: 2 rows, 384 columns.

Press **Check**. If the check says the shape is wrong, look at what you returned: a plain list instead of an array, or a
matrix with the rows and columns swapped, are the usual slips.
:::

:::step{type=history title="Before embeddings: synonyms written by hand"}
For most of the history of computing, a machine had no idea that two different words could mean the same thing. To a
program, "tiger" and "big cat" were simply two different strings of letters, exactly the problem Fieldbook hit in
chapter 1.

When a system needed to know which words were related, people **wrote it down by hand**. They used the oldest tool for
the job: the **thesaurus**, a book that groups words by meaning, so that next to *tiger* you find *big cat*, *feline*,
*predator*. The most famous one is still in print after more than 170 years.

The man in this portrait is **Peter Mark Roget**, a British doctor. In **1852** he published the *Thesaurus of English
Words and Phrases*, after decades of sorting English words into groups by meaning, by hand, on paper. Search systems in
the twentieth century worked in his spirit: lists of synonyms, written by people, plugged into the search. They helped,
but they were never complete, never up to date, and someone had to write a new list for every subject and every
language. A sanctuary manual full of words like *gaur*, *camera trap* and *core zone* would have needed its own list.

:::photo{src="/lesson-images/rag/roget.webp" alt="Portrait engraving of Peter Mark Roget, a man in a dark coat and white cravat, seated in an armchair" credit="Thomas Pettigrew" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3ARoget_P_M.jpg"}
Peter Mark Roget, who grouped English words by meaning by hand for his Thesaurus (1852). Embeddings do the same job, but
the machine learns the groups by itself.
:::
:::

:::step{type=history title="You shall know a word by the company it keeps"}
:::before{title="Words as labels"}
To a computer, "tiger" and "big cat" were just different strings. Systems that needed meaning used hand-made thesauri,
lists of synonyms written by people, which never covered everything and never kept up.
:::

The way out came from a simple observation about language. In **1957** the British linguist J. R. Firth wrote: *"You
shall know a word by the company it keeps."* Think about what that means: words that keep turning up in the same
company, with the same neighbours, tend to mean related things. "Tiger" and "leopard" both appear next to *prowl*,
*prey*, *stripes or spots*, *forest*. So instead of writing synonyms down by hand, a machine could **count** which words
appear together, and work out the relations by itself.

**Latent semantic analysis** (**1990**) turned that idea into mathematics: count which words appear together across
many documents, then squeeze those counts into a few hundred numbers per word. For the first time, a word had a
vector that no person had written by hand.

In **2013** a team at Google led by **Tomas Mikolov** released **word2vec**. It learned a vector for every word from
billions of words of ordinary text, and it was fast enough for anyone to run. It also produced the most famous result in
the field: take the vector for *king*, subtract *man*, add *woman*, and the nearest word is *queen*. The vectors had learned
that the step from *man* to *woman* is the same step as from *king* to *queen*, with no one ever telling it. That result
convinced a generation of engineers that meaning could be computed.

Word vectors still had a gap: they gave one vector per **word**, and a question is a whole sentence. **Sentence-BERT**
(**2019**) closed it by training a model to give one vector per **sentence**, placing sentences with the same meaning
close together. A stream of small, strong, free models followed, and the one in your lab, BGE (**2023**), is one of
them. Every vector you made in the last task is a direct descendant of word2vec.

:::solved
**Meaning you can compute with.** Similar texts get similar vectors, so "find texts that mean something like this"
becomes "find the nearest points", with no hand-written synonym list anywhere.
:::

:::timeline
- **1852** Roget's Thesaurus: synonyms grouped by hand.
- **1957** Firth: the company a word keeps.
- **1990** Latent semantic analysis.
- **2013** word2vec.
- **2019** Sentence-BERT: vectors for sentences.
- **2023** BGE and other small open embedding models.
:::

This is the man behind word2vec, the 2013 tool that made word vectors fast and free for everyone, and the reason
embeddings went from a research idea to something in every search engine. The model you just used descends from his
work.

:::photo{src="/lesson-images/rag/mikolov.webp" alt="Tomas Mikolov, a young man with long hair tied back, smiling slightly, in front of a building" credit="Jindřich Nosek (NoJin)" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File%3ATom%C3%A1%C5%A1_Mikolov_%282020%29.jpg"}
Tomas Mikolov in 2020. His team at Google released word2vec in 2013.
:::
:::

:::step{type=concept title="Cosine similarity: how alike two directions are" file="02-embeddings/fieldbook.py" line="74-78"}
You can now turn any text into a vector. The next question is the one search depends on: **how close are two vectors?**
We need a single number that says "these two are very alike" or "these two have nothing in common".

Picture each vector as an **arrow** that starts at zero and points to the text's position. Two texts
about the same thing have arrows that point in nearly the **same direction**. Two unrelated texts point in quite
different directions. So we measure the **angle** between the two arrows, and to turn the angle into a friendly score,
we take its **cosine**:

| Angle between the arrows | Cosine | What it means |
|---|---|---|
| 0 degrees | 1.0 | same direction: same meaning |
| 90 degrees | 0.0 | at right angles: unrelated |
| 180 degrees | -1.0 | opposite directions |

You do not need trigonometry to compute it. The formula uses only multiplication, addition and a square root:

```text
cosine(a, b) = dot(a, b) / (length(a) * length(b))

dot(a, b)  = a[0]*b[0] + a[1]*b[1] + ... (multiply each pair of numbers, add them all up)
length(a)  = the square root of dot(a, a)
```

**Let's do one by hand**, with tiny 2-number vectors, so you can see every step. Take `a = [3, 4]` and `b = [4, 3]`:

1. **Dot product:** `3*4 + 4*3 = 12 + 12 = 24`.
2. **Length of a:** the square root of `3*3 + 4*4 = 25`, which is `5`. **Length of b:** also `5`.
3. **Cosine:** `24 / (5 * 5) = 24 / 25 = 0.96`. The two arrows point almost the same way, so the score is close to 1.

Now try `a = [3, 4]` with `c = [-4, 3]`: the dot product is `-12 + 12 = 0`, so the cosine is `0`. These two arrows are
at right angles: unrelated.

**Why divide by the lengths?** Compare `a = [3, 4]` with `[6, 8]`. The second arrow is twice as long but points the
same way. The dot product is `18 + 32 = 50`, the lengths are `5` and `10`, and the cosine is `50 / 50 = 1.0`: a
perfect match. Dividing by the lengths removes the "how long" and keeps only the "which way". That is exactly what we
want, because the direction carries the meaning.

In code, NumPy does each part in one call, and it works the same for 2 numbers or 384:

```python
np.dot(a, b)          # the dot product
np.linalg.norm(a)     # the length of a
```

Check yourself before the task: what cosine do `[1, 0]` and `[0, 1]` get? (The dot product is 0, so the cosine is 0:
unrelated.)
:::

:::step{type=task task=cosine title="Your turn: how alike two vectors are" file="02-embeddings/fieldbook.py" line="74-78"}
Write `cosine(a, b)` in `02-embeddings/fieldbook.py`:

1. compute the dot product of `a` and `b` with `np.dot`;
2. divide it by the length of `a` times the length of `b` (`np.linalg.norm` for each);
3. return the result as a plain Python number with `float(...)`.

The last step matters: NumPy gives back its own number type, and wrapping it in `float()` makes it an ordinary Python
float that prints and compares cleanly.

Then run the comparison script and read the scores the model gives:

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

1. **Tiger and big cat: 0.690.** Not one word in common (apart from "the"), and still clearly related. This is exactly
   what keyword search could not do in chapter 1.
2. **Tiger and leopard: 0.802**, even higher. Both sentences describe the same kind of event, an animal crossing a path,
   so the model places them very close. It sees the shape of the whole sentence, not only the animal.
3. **Tiger and batteries: 0.420.** Unrelated, and yet the score is not 0. With this model, unrelated texts usually
   score somewhere around 0.3 to 0.5. So a score means something only **compared with other scores** for the same
   question: 0.69 is good next to 0.42, not because 0.69 is a big number.
4. **Batteries and "trail cameras need new cells": 0.728.** Different words, the same question. This is the pair that
   will make Fieldbook genuinely useful to rangers.
5. **The trap: "closed" against "open": 0.834.** This is higher than the true paraphrase on the line above it (0.796),
   even though the two sentences say **opposite** things. They share almost every word and talk about the same topic;
   one small word flips the meaning, and the vectors barely notice. Embeddings capture what a text is **about**, not
   whether it says yes or no. Remember this the day a search returns a passage that says the opposite of what was asked.

And the cost: 12 sentences in 100 milliseconds on two processor cores, after under a second to load the model. The whole
manual (31 sections) takes about three seconds, and you only do it once.
:::

:::step{type=predict title="Guess first"}
:::question
"The road is safe after dark." and "The road is not safe after dark." What cosine will they get?
:::
- [ ] About 0.0: they mean opposite things
- [ ] About -1.0: opposite meanings point opposite ways
- [x] High, above 0.9: they are about the same thing, and "not" changes few numbers
:::explain
A cosine of -1.0 almost never happens for real texts. Negation is a known blind spot of embeddings; chapter 10's
reranker, which reads both texts together, handles it better.
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
Without the division you get the plain dot product, which grows with the lengths of the vectors: `[3, 4]` and `[6, 8]`
would look less alike than they are.
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
Each model learns its own way of placing texts. A vector from one model means nothing to another, even if both use
384 numbers. That is
why changing the embedding model means embedding every document again, and why the model's name belongs next to the
vectors.
:::
:::

:::step{type=deep-dive title="Go deeper: choosing an embedding model"}
**Local or API.** bge-small runs on a laptop processor and costs nothing per text. Hosted models (OpenAI's
text-embedding-3 family, Cohere, Voyage, Google) are larger and usually somewhat better, cost a small amount per million
tokens, and send your text to another company. For a sanctuary's internal manual, local is the natural choice; many
companies decide the same for privacy alone.

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

- explain what an embedding is: a fixed list of 384 numbers for a text, where similar meanings give similar vectors;
- make embeddings on your own processor, as a `float32` matrix with one row of 384 numbers per text;
- compute cosine similarity by hand and in code, and say why it divides by the lengths;
- read scores the right way: compare them with each other, because unrelated texts do not score 0;
- spot the blind spot: a small word like "not" or "open" barely moves a vector.

Next, chapter 3: searching a whole collection of vectors for the ones closest to a question.

:::photo{src="/lesson-images/rag/rag-02-notes.webp" alt="Handwritten notes about embeddings: An embedding turns any text into 384 numbers. Similar meanings land close together. Cosine compares directions: 1.0 means the same. Compare scores with each other, not with 0. Unrelated texts still score about 0.4. Embeddings barely notice the word not." ai="true"}
One page of notes for this chapter.
:::
:::
