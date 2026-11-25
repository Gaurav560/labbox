:::step{type=story title="The museum Atlas does not know"}
Atlas can now hold a conversation, look up opening hours and book seats. Yet ask it about the museum itself and it
still invents. In chapter 5 it planned a tour through a "Robotics Zone" and suggested a "Jurassic Journey"; the museum
has neither. The model has never read the museum's exhibit cards, so it fills the gaps with plausible inventions.

The museum has twelve exhibit cards, and will have hundreds. You cannot paste all of them into every prompt: too many
tokens, too slow, too expensive (chapter 3). What Atlas needs is a way to find **the two or three cards that matter
for this question**, and send only those. And it has to find them by **meaning**, not by matching words: a visitor
asking "Which exhibit shows that the Earth spins?" means the Foucault pendulum, though the question never says
"pendulum".

That ability rests on one idea, the subject of this chapter: **embeddings**, which turn a piece of text into a list of
numbers that captures what it means.

Mapmakers turn every place on Earth into two numbers, latitude and longitude, so that places near each other get
numbers near each other. Embeddings do the same for meaning, with far more than two numbers.

:::photo{src="/lesson-images/spring-ai/old-map.webp" alt="A world map drawn as a grid of eighteen sheets, with the continents covered in lines of latitude and longitude, decorated boxes of text and a compass rose" credit="Gerardus Mercator" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Mercator_1569_world_map_composite.jpg"}
Gerardus Mercator's world map of 1569: every place on Earth, given two numbers.
:::

:::mission
Measure how alike two embeddings are, and find the exhibit whose description means the most like a visitor's question.
:::
:::

:::step{type=concept title="Text as a point in space"}
An **embedding model** reads a text and returns a **vector**: a fixed-length list of numbers. This course's embedding
model, `ai-embed` (OpenAI's `text-embedding-3-small`), returns 1,536 numbers for any text, whether it is one word or a
page:

```text
$ curl -s -G localhost:8080/embed --data-urlencode "text=Where is the pendulum?" | jq -c .
{"first":[0.0029792786,0.06008911,0.05117798,0.051696777,0.013687134],"dimensions":1536}
```

No single number means anything you could name. Together they place the text at a point in a 1,536-dimensional space,
and the model was trained so that **texts with similar meanings land close together**: "Where is the pendulum?" lands
near "the Foucault pendulum hangs in Gallery 2", and far from "pedal a bicycle to make electricity".

:::diagram{name="ai-embeddings"}
Real scores from this course's embedding model (26 November): one question against the six exhibits.
:::

Embeddings are cheap: this model costs $0.02 per million tokens, so embedding all twelve exhibit cards of chapter 13
(1,152 words, about 1,500 tokens) costs about $0.00003, a few thousandths of a cent. And they are fast, because nothing is generated: the model reads, and returns its numbers.

**Check yourself:** do "the dish listens to space" and "the radio telescope hears stars" share many words? Would their
embeddings be close? (Few shared words, but very similar meaning: yes, close.)
:::

:::step{type=concept title="How close: cosine similarity"}
To compare two vectors, we look at the **angle** between them. **Cosine similarity** is the cosine of that angle:

| Cosine | Means |
|---|---|
| 1 | same direction: the same meaning |
| around 0 | at right angles: unrelated |
| -1 | opposite directions |

It is computed from three sums over the numbers:

```text
cosine(a, b) = (a1*b1 + a2*b2 + ... + an*bn) / ( sqrt(a1² + ... + an²) * sqrt(b1² + ... + bn²) )
```

The top part is the **dot product**; the bottom part multiplies the **lengths** of the two vectors. Dividing by the
lengths means only the direction counts, not how long the vectors are.

A small example by hand: a = (1, 2) and b = (2, 4) point the same way. The dot product is 1×2 + 2×4 = 10; the lengths
are √5 and √20; √5 × √20 = √100 = 10; so the cosine is 10 / 10 = **1**. And a = (1, 0), b = (0, 1): the dot product is 0,
so the cosine is **0**, unrelated.

In real embedding spaces, scores are rarely near 1. We measured this chapter's four questions against the six
exhibits with `text-embedding-3-small`: the right exhibit scored 0.37 to 0.55, the others 0.02 to 0.37. The dinosaur
question gave Rajasaurus 0.367 and the planetarium 0.323, a narrow win. What matters is the **ranking**, and the gap
between first and second tells you how sure the search is. (Other models give other ranges.)
:::

:::step{type=task task=cosine_similarity title="Your turn: cosine similarity in Java" file="11-embeddings/src/main/java/com/atlas/Similarity.java" line="14"}
In `11-embeddings`, finish `Similarity.cosine(float[] a, float[] b)`: one loop that adds up the dot product and the two
sums of squares, then the division (`Math.sqrt` for the square roots):

1. Three `double` sums, all 0: `dot`, `na`, `nb`.
2. For every `i`: `dot += a[i] * b[i]`, `na += a[i] * a[i]`, `nb += b[i] * b[i]`.
3. `return dot / (Math.sqrt(na) * Math.sqrt(nb));`

The usual slip: returning `dot` alone. It ranks texts by length as well as meaning, and the Check's ordinary case
fails.

Press **Check**: it tests vectors in the same direction, at right angles, in opposite directions, and one ordinary
case.
:::

:::step{type=example title="Worked example: the EmbeddingModel" file="11-embeddings/src/main/java/com/atlas/EmbeddingController.java" line="40"}
Spring AI gives you an `EmbeddingModel` bean, configured by the same starter as the chat model (the alias `ai-embed`
is set in `application.properties`). Two methods are all you need:

```java
float[] vector = embeddings.embed("Where is the pendulum?");          // one text, one vector
List<float[]> vectors = embeddings.embed(List.of("first", "second")); // many texts in one request
```

The second form sends all the texts in **one** request and returns the vectors in the same order: faster and kinder to
rate limits than a request per text.

To find the exhibit nearest to a question, embed the question, embed every description, and keep the one with the
highest cosine. Embedding each exhibit's name with its description (`"Rajasaurus: The skull of a horned ..."`) gives
the model more to work with than the description alone.
:::

:::step{type=task task=nearest_exhibit title="Your turn: the nearest exhibit" file="11-embeddings/src/main/java/com/atlas/EmbeddingController.java" line="46"}
Finish `GET /nearest?q=...`: embed the question and all six exhibits (name and description, in one request), and return
the **name** of the exhibit with the highest cosine similarity to the question:

1. `float[] question = embeddings.embed(q);`
2. One request for the exhibits: `embeddings.embed(...)` with the list of `name + ": " + description`.
3. Walk the names and vectors in the same order, keep the name with the highest `Similarity.cosine`, return it.

The usual slip: embedding each exhibit in its own request. It works, but makes seven requests instead of two.

```bash run
cd 11-embeddings && mvn -q -o spring-boot:run
```

```bash run
curl -s -G localhost:8080/nearest --data-urlencode "q=Which exhibit shows that the Earth spins?"; echo
```

Press **Check**.
:::

:::step{type=try title="Meaning, not words"}
With the real embedding model (our re-run on 26 November gave the same four names; the winning scores were 0.367,
0.468, 0.546 and 0.536):

```text
$ curl -s -G localhost:8080/nearest --data-urlencode "q=Where can I see a dinosaur?"; echo
Rajasaurus
$ curl -s -G localhost:8080/nearest --data-urlencode "q=Which exhibit shows that the Earth spins?"; echo
Foucault pendulum
$ curl -s -G localhost:8080/nearest --data-urlencode "q=I want to make electricity with my legs"; echo
Bicycle generator
$ curl -s -G localhost:8080/nearest --data-urlencode "q=Where do the colours of a rainbow come from?"; echo
Prism room
```

"The Earth spins" found the pendulum, whose description says "as the Earth rotates". "Electricity with my legs" found
the bicycle, which says "pedal". A keyword search would have missed both. This is **semantic search**, and it is the
"retrieval" in the retrieval-augmented generation of chapter 14.
:::

:::step{type=predict title="Guess first"}
:::question
You embed the same sentence twice with the same model. What is the cosine similarity of the two vectors?
:::
- [x] 1, or extremely close to it: the same text gives the same point
- [ ] About 0.5
- [ ] It changes every time, like chat answers
:::explain
Embedding models do not sample tokens, so there is no temperature and no randomness: the same text gives the same
vector (up to tiny rounding). We embedded the same question twice in one request: cosine 1.0. That makes embeddings
safe to store and reuse.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Can you compare a vector from `text-embedding-3-small` with one from a different embedding model?
:::
- [ ] Yes, vectors are vectors
- [x] No: each model has its own space; vectors from different models are not comparable
- [ ] Only if both have 1,536 numbers
:::explain
Each model learns its own map of meaning. Changing the embedding model means embedding every stored document again.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why divide by the vectors' lengths in cosine similarity?
:::
- [x] So that only the direction counts: long and short texts are compared fairly
- [ ] To make the result a whole number
- [ ] Because Java needs it
:::explain
Without the division you get the dot product, which grows with the vectors' lengths. Cosine keeps only the angle, which
is what carries the meaning.
:::
:::

:::step{type=deep-dive title="Go deeper: dimensions, models, and what embeddings cannot do"}
**Dimensions.** More numbers can hold finer distinctions, at the cost of storage and search time. `text-embedding-3-small`
can return fewer than 1,536 dimensions if you ask (`spring.ai.openai.embedding.options.dimensions`), keeping most of its
quality with a smaller index.

**Choosing a model.** Embedding models differ in quality per language and domain. Open models (run with Ollama or
Spring AI's ONNX Transformers support) can run on your own servers, with no per-token cost.

**What they cannot do.** Embeddings capture topic and meaning, not logic. "Tickets for children" and "tickets for
adults" land close together; numbers, negation ("not on Mondays") and exact names are weak points. That is why good
systems combine semantic search with keyword search and filters, and why the model still has to read the text it is
given.

**Where else they are used.** Recommendations ("visitors who liked this also liked"), duplicate detection, clustering
questions to see what visitors ask most, and classifying text without training a model.
:::

:::step{type=recap}
You can now:

- explain embeddings: text turned into a vector, where similar meanings land close together;
- compute cosine similarity, by hand and in Java, and read what its values mean;
- embed one text or many in one request with Spring AI's `EmbeddingModel`;
- find the nearest exhibit by meaning: semantic search, the base of retrieval.

Next, chapter 12: storing many embeddings in a vector store, and searching them in one call.

:::photo{src="/lesson-images/spring-ai/springai-11-notes.webp" alt="Sketchnote, Embeddings (meaning as a list of numbers): An embedding model turns a text into 1,536 numbers. Texts with similar meanings get numbers that point the same way. The flow: Question, embed(), 1,536 numbers, Cosine with each exhibit, Highest score wins. What we measured: the Earth spins found the pendulum: 0.468; right exhibits scored 0.37 to 0.55; the same text twice: cosine 1.0; 12 exhibit cards cost about $0.00003." ai="true"}
One page of notes for this chapter.
:::
:::
