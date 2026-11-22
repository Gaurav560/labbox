:::step{type=story title="Atlas reads the cards"}
Everything is ready. The exhibit cards are in the vector store, cut into good chunks, each knowing its file. Searching
by meaning works. One step is left: when a visitor asks a question, find the right chunks **and give them to the
model**, so it answers from the museum's own facts instead of its memory of the internet.

That pattern has a name you will hear in every AI team: **retrieval-augmented generation**, RAG. Retrieve, augment,
generate: find the relevant text, add it to the prompt, let the model write the answer. It is how assistants answer
from company handbooks, product manuals, legal archives and museum catalogues, without retraining the model.

A good exam to compare with is an open-book exam: nobody memorises the whole book; you learn to find the right page fast
and answer from it.

:::photo{src="/lesson-images/spring-ai/open-book.webp" alt="An open book held up in front of a blurred library shelf, its pages printed with text" credit="Shixart1985" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:An_open_book_is_placed_in_front_of_a_library_shelf.jpg"}
An open book: the answer is on the page, if you can find the page.
:::

:::mission
Make Atlas answer every question from the closest exhibit chunks, and return the cards it used as its sources.
:::
:::

:::step{type=history title="Why not just teach the model?"}
There are two ways to give a model knowledge it does not have.

:::before{title="Training it in"}
**Fine-tuning** trains the model further on your own documents. It is slow and costly, has to be repeated whenever the
documents change, and the model still cannot tell you **where** a fact came from; it may also blend your facts with
what it already believed. For a museum whose show times change weekly, it would be out of date before it finished.
:::

In **2020**, a team at Facebook AI Research led by **Patrick Lewis** published "Retrieval-Augmented Generation for
Knowledge-Intensive NLP Tasks". Their idea: keep the knowledge **outside** the model, in a searchable index, and
retrieve the relevant passages at question time.

:::solved
**Knowledge you can update, check and cite.** Change a card, re-run the ETL, and the next answer uses the new fact.
Every answer can point to the passages it came from. The model brings language and reasoning; your documents bring the
facts. RAG became the most common way companies put language models to work on their own data.
:::
:::

:::step{type=concept title="What the advisor adds to your prompt"}
Spring AI does RAG with an advisor (chapter 9): **`QuestionAnswerAdvisor`**. Before each call, it searches the vector
store with the user's question, and adds the chunks it found to the user message, with instructions. This is what it
added in a run of this course's tests, recorded by a pretend model (the chunk text shortened here):

```text
How long is the wire of the Foucault pendulum?

Context information is below, surrounded by ---------------------

---------------------
The Foucault pendulum ... A brass ball of 25 kilograms hangs from a 15 metre steel wire ...
---------------------

Given the context and provided history information and not prior knowledge,
reply to the user comment. If the answer is not in the context, inform
the user that you can't answer the question.
```

1. The question, unchanged.
2. The retrieved chunks, between two lines of dashes.
3. Instructions: answer from the context, not from prior knowledge, and say so when the answer is not there.

:::diagram{name="ai-rag"}
The question is embedded and searched; the closest chunks are added to the prompt; the model answers from them.
:::

Registered with `defaultAdvisors(...)`, it applies to every call of the `ChatClient`:

```java
ChatClient chat = builder
        .defaultAdvisors(QuestionAnswerAdvisor.builder(vectorStore)
                .searchRequest(SearchRequest.builder().topK(3).similarityThreshold(0.35).build())
                .build())
        .build();
```

`topK(3)` keeps the prompt short (every chunk costs input tokens); `0.35` is the threshold chosen from the real scores
measured in chapter 13.
:::

:::step{type=task task=rag_answer title="Your turn: answer from the cards" file="14-rag/src/main/java/com/atlas/AskController.java" line="33"}
In `14-rag`, add a `QuestionAnswerAdvisor` built on the vector store to the `ChatClient`'s default advisors, retrieving
the **3** closest chunks with a similarity of at least **0.35**. (The ETL from chapter 13 is already in place.)

```bash run
cd 14-rag && mvn -q -o spring-boot:run
```

Wait for the `ETL:` line, then:

```bash run
curl -s -G localhost:8080/ask --data-urlencode "q=How much is a ticket for a child?"; echo
```

Press **Check**.
:::

:::step{type=try title="From I don't know to 60 rupees"}
In chapter 2 Atlas answered the ticket question honestly, and uselessly: "I'm sorry, but I don't know the ticket
prices." With RAG:

```text
$ curl -s -G localhost:8080/ask --data-urlencode "q=How much is a ticket for a child?"; echo
A ticket for a child aged 5 to 15 costs 60 rupees. Children under 5 can enter for free. Planetarium shows are an extra 80 rupees.
```

Right, complete, and from the museum's own card.
:::

:::step{type=example title="Worked example: what was retrieved" file="14-rag/src/main/java/com/atlas/AskController.java" line="47"}
A visitor (or a curator checking Atlas) may ask: where did that come from? The advisor leaves the documents it
retrieved in the response's **context**, under the key `QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS`. To read it, end the
chain with `chatClientResponse()` instead of `content()`:

```java
ChatClientResponse response = chat.prompt()
        .user(q)
        .call()
        .chatClientResponse();
List<Document> used = (List<Document>) response.context().get(QuestionAnswerAdvisor.RETRIEVED_DOCUMENTS);
String answer = response.chatResponse().getResult().getOutput().getText();
```

1. `chatClientResponse()` returns the model's response **and** the advisor context.
2. The retrieved documents carry their metadata, so `d.getMetadata().get("file")` names each card.
3. One card can give several chunks: keep each file once (`distinct()`).
:::

:::step{type=task task=cite_sources title="Your turn: answers with sources" file="14-rag/src/main/java/com/atlas/AskController.java" line="48"}
Finish `GET /ask/sourced?q=...`: return the answer and the list of files of the retrieved chunks, each file once.

```bash run
curl -s -G localhost:8080/ask/sourced --data-urlencode "q=What did India find on the Moon?" | jq .
```

Press **Check**.
:::

:::step{type=try title="Answers you can check"}
Real answers, with their sources:

```text
$ curl -s -G localhost:8080/ask/sourced --data-urlencode "q=How long would the pendulum take to turn a full circle here in Pune?" | jq .
{
  "answer": "In Pune, the pendulum takes about 76 hours to make a full circle. This happens because the Earth is turning underneath it as it swings. You can see the brass ball knocking over small pegs along the way!",
  "sources": [
    "foucault-pendulum.md"
  ]
}
$ curl -s -G localhost:8080/ask/sourced --data-urlencode "q=What did India find on the Moon?" | jq .
{
  "answer": "India found sulphur in the lunar soil during the Chandrayaan-3 mission. The Vikram lander successfully landed near the Moon's south pole on 23 August 2023, and the rover Pragyan drove about 100 metres to make this discovery. This makes India the fourth country to land softly on the Moon!",
  "sources": [
    "chandrayaan-3.md",
    "mangalyaan.md"
  ]
}
$ curl -s -G localhost:8080/ask/sourced --data-urlencode "q=Do you have a T-rex?" | jq .
{
  "answer": "I'm sorry, but we do not have a T-rex at the museum. However, we do have a cast of the skull of Rajasaurus narmadensis in our Life Gallery! It's a fascinating dinosaur that lived around 67 million years ago.",
  "sources": [
    "rajasaurus.md"
  ]
}
```

"76 hours" is on the pendulum card, worked out for Pune's latitude. The T-rex answer is the best of all: no invented
exhibit, an honest no, and a real alternative. Compare chapter 5, where Atlas invented a "Jurassic Journey".

And one honest failure:

```text
$ curl -s -G localhost:8080/ask --data-urlencode "q=Which exhibits do you have?"; echo
I'm sorry, but I can't answer that question about the exhibits. If you have any other questions about the museum or science, feel free to ask!
```

A broad question is close to **every** card a little and to none strongly, so nothing passed the threshold, and the
advisor's instructions told the model to say it cannot answer. Retrieval is for specific questions. Questions about the
whole collection need a different tool: a list of all exhibits (from a database, or a `@Tool` like chapter 7's).
:::

:::step{type=predict title="Guess first"}
:::question
A card changes: the child ticket now costs 70 rupees. What do you need to do for Atlas to answer correctly?
:::
- [ ] Retrain the model
- [x] Update the card and run the ETL again, so the store holds the new chunk
- [ ] Nothing: the model will notice
:::explain
That is RAG's great strength: knowledge lives in your documents, not in the model. Change the document, re-index it, and
the next answer is right.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `QuestionAnswerAdvisor` add to the request?
:::
- [ ] A new system prompt that replaces yours
- [x] The retrieved chunks and instructions to answer from them, added to the user message
- [ ] The whole vector store
:::explain
Your system prompt stays; the advisor augments the user message with the context and a rule to use it, and to say so
when the answer is not there.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why return sources with an answer?
:::
- [x] People can check the answer, and you can see which document caused a wrong one
- [ ] It makes the answer shorter
- [ ] The model needs them
:::explain
Sources build trust and make debugging possible: a wrong answer with its source shows whether the card was wrong, the
retrieval was wrong, or the model misread the card.
:::
:::

:::step{type=deep-dive title="Go deeper: modular RAG"}
**`RetrievalAugmentationAdvisor`.** For more control, Spring AI's modular RAG advisor is built from parts you choose: a
query transformer (rewrite "and on Sunday?" into a full question using the conversation; translate the question), a
document retriever (`VectorStoreDocumentRetriever`, with filters), a document joiner (merge results from several
sources) and a query augmenter (how the context is put into the prompt, and what happens when nothing is found:
`ContextualQueryAugmenter` can allow an empty context and let the model answer from general knowledge).

**Hybrid search.** Combine semantic search with keyword search, so exact names, prices and codes are found too.

**Re-ranking.** Retrieve 20 candidates cheaply, then let a stronger model (or a dedicated re-ranker) pick the best 3.

**Memory and RAG together.** With session memory (chapter 6) as well, a follow-up like "and for adults?" needs the
conversation to make sense; a query-rewriting transformer turns it into "How much is a ticket for an adult?" before
searching.
:::

:::step{type=recap}
You can now:

- explain RAG (retrieve, augment, generate) and why it beats training knowledge into a model for changing facts;
- add `QuestionAnswerAdvisor` to a `ChatClient`, with `topK` and a threshold chosen from real scores;
- read the retrieved documents from `chatClientResponse()` and return answers with their sources;
- recognise the limits: broad questions, exact numbers, and follow-ups need more than plain retrieval.

That ends Part 3. Next, Part 4: beyond text, and production. Chapter 15 starts with pictures.

:::photo{src="/lesson-images/spring-ai/springai-14-notes.webp" alt="Handwritten notes about RAG: retrieve, augment, generate; QuestionAnswerAdvisor; topK 3, threshold 0.35; answer + sources; change the card, not the model" ai="true"}
One page of notes for this chapter.
:::
:::
