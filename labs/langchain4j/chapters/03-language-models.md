:::step{type=story title="Hearing the announcements"}
Stand on platform one at Pune for an hour and you will hear the same sentences again and again: "The Ghat Express to
Lonavala will leave from platform one." "The Konkan Breeze is running twenty minutes late." After a while you can
finish them yourself. Hear "The Ghat Express is running..." and your brain has already guessed "late".

That guess is exactly what a **language model** does. Given some words, it predicts the next one. ChatGPT does it with
a neural network of billions of parameters trained on a large part of the internet; you will do it today with a
`Map` and eight station announcements. The idea is the same, and once you have built the small one, the big one stops
being magic.

:::mission
Turn text into words and count them, the way computers handled language for decades. Then build a bigram model that
predicts the next word, and let it write its own announcement.
:::
:::

:::step{type=concept title="How computers learned to handle language"}
**Natural language processing** (NLP) is the part of computer science that makes programs work with human language:
translation, search, spam filters, voice assistants, chatbots. It has been rebuilt four times, and each time the rules
got smaller and the data bigger:

| Era | How it worked | Its weakness |
|---|---|---|
| **Rules** (1950s to 1980s) | Grammars and dictionaries written by linguists | Endless exceptions; every language rebuilt by hand |
| **Statistics** (1990s to 2000s) | Count words and word pairs in large text; pick the likeliest | Knows nothing about meaning; "bank" is one word |
| **Neural networks** (2010s) | Learn vectors of numbers for words, so similar words are close (chapter 5) | Read text one word at a time, and forget early words |
| **Transformers and LLMs** (2017 on) | One huge network reads all the words at once, with attention (chapter 6) | Expensive; can sound right and be wrong (chapter 11) |

Two ideas survived every era, and you will build both today. First, text must be cut into units a program can count:
**words** (and later, tokens). Second, the most useful single thing to know about language is **what tends to come
next**.

**Check yourself:** a spam filter that counts how often "lottery" and "winner" appear in an email: which era is it
from? (Statistics: it counts words, without knowing what they mean.)
:::

:::step{type=history title="Counting letters in a poem"}
In **1913** the Russian mathematician **Andrey Markov** sat down with the first 20,000 letters of Pushkin's poem *Eugene
Onegin* and counted, by hand, how often a vowel followed a vowel, a vowel followed a consonant, and so on. He showed
that the next letter depends on the one before, in a way you can measure. Sequences where the next step depends on the
current one are still called **Markov chains**.

:::photo{src="/lesson-images/langchain4j/andrey-markov.webp" alt="An oval portrait of Andrey Markov as a young man, with dark swept-back hair and a full beard, in a dark suit" credit="Unknown photographer" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AAndrei_Markov.jpg"}
Andrey Markov as a young mathematician. In 1913 he counted letters in Pushkin.
:::

:::before{title="Language by hand"}
In **1954** an IBM computer translated about sixty Russian sentences into English for a public demonstration, using
250 words and six grammar rules. The organisers predicted that machine translation would be solved within a few
years. It took sixty, because language does not fit in rules: idioms, ambiguity, words that change meaning with their
neighbours.
:::

In **1948** **Claude Shannon**, founding information theory at Bell Labs, used Markov's idea on words: he picked each
next word by how often it followed the previous one in real English text, and got sentences that sounded almost like
English. That is a **bigram** (two-word) model, the one you will build. Statistical models like it ran machine
translation and phone keyboards' next-word suggestions for decades.

:::solved
**Predict the next word.** Every modern language model, up to the largest, is trained on the same single job Markov
and Shannon measured: given the text so far, how likely is each possible next piece? What changed is how much of the
text the model looks at, and how cleverly.
:::

:::timeline
- **1913** Markov counts letter pairs in *Eugene Onegin*.
- **1948** Shannon generates English-like text from word pairs.
- **1954** IBM's rule-based Russian translation demonstration.
- **1990s** Statistical translation and speech recognition.
- **2013** word2vec: words as vectors.
- **2018** GPT-1: a transformer trained to predict the next word.
:::

:::funfact
Your phone keyboard's three suggested words above the letters are a small language model, running on the phone,
updated with the words you type most.
:::
:::

:::step{type=example title="Worked example: text to words" file="03-language-models/src/main/java/com/setu/Words.java" line="15-24"}
`Words.split` is already written. It is the first step of almost every language program, old and new: turn text into
units:

```java
for (String w : text.toLowerCase(Locale.ROOT).split("[^\\p{L}\\p{N}]+")) {
    if (!w.isEmpty()) {
        out.add(w);
    }
}
```

1. `toLowerCase`: "The" and "the" are the same word for counting.
2. `split("[^\\p{L}\\p{N}]+")`: cut wherever there is something that is not a letter (`\p{L}`, in any alphabet,
   so Marathi works too) or a digit (`\p{N}`). Commas, spaces and "!" all become cuts.
3. Skip empty pieces (a text that starts with punctuation gives one).

To count things in Java, `Map.merge` does it in one line (only to read; it is not in your project):

```java
Map<String, Integer> trains = new TreeMap<>();
for (String t : List.of("ghat", "konkan", "ghat")) {
    trains.merge(t, 1, Integer::sum);   // new key: put 1; existing key: add 1
}
// {ghat=2, konkan=1}
```

A `TreeMap` keeps its keys sorted A to Z, which makes counts easy to read and to compare.
:::

:::step{type=task task=count_words title="Your turn: a bag of words" file="03-language-models/src/main/java/com/setu/Words.java" line="26-29"}
Finish `Words.count(text)`: split the text with `split`, and count how often each word appears, in a map sorted A to Z.
An empty text has no words.

1. `Map<String, Integer> counts = new TreeMap<>();`
2. For each word of `split(text)`: `counts.merge(word, 1, Integer::sum);`
3. `return counts;`

The usual slip: a `HashMap`. The counts are right, but the words come out in no particular order, and the Check
expects them A to Z.

This is called a **bag of words**: you keep the counts and throw away the order, as if the words were shaken in a
bag. For years, search engines and spam filters saw text exactly like this.

Press **Check**.
:::

:::step{type=concept title="A model that predicts the next word"}
A bag of words loses the one thing a language model needs: order. A **bigram model** keeps a little of it. For every
word, it counts which words came **right after** it:

| After this word | came | times |
|---|---|---|
| the | ghat | 3 |
| the | konkan | 2 |
| the | train, monsoon | 1 each |
| running | ten, on, twenty | 1 each |

To predict the next word after "the", look up the row for "the" and take the word with the biggest count: "ghat". To
**generate** text, predict a word, then predict the word after that one, and so on.

In `Bigram.java`, `train` is already written: it fills `follows`, a map from each word to its own `TreeMap` of
followers and counts. `generate` is written too, and calls `next`, which is your task. When two followers have the
same count, pick the first A to Z, so the model gives the same answer every time.

This is a real language model, with real limits. It looks back **one** word. "The train to Lonavala will stop at" and
"Please keep your luggage with you at" end in the same word, "at", so it cannot tell them apart. Large language models
look back thousands of tokens, which is the whole difference, and the subject of chapter 6.

**Check yourself:** what will `next("late")` return, if "late" was only ever the last word of a sentence? (Nothing ever
came after it, so there is no prediction: `null`.)
:::

:::step{type=task task=next_word title="Your turn: predict the next word" file="03-language-models/src/main/java/com/setu/Bigram.java" line="24-28"}
Finish `Bigram.next(word)`:

1. get the followers of the word from `follows`; if there are none, return `null`;
2. return the follower with the biggest count; on a tie, the one that comes first A to Z.

The followers are in a `TreeMap`, so a loop already visits them A to Z: keep a follower only when its count is
**greater than** the best so far. The usual slip: `>=`, which keeps the last of a tie, so "running" would predict
"twenty" instead of "on".

```bash run
cd /workspace/03-language-models && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="A model that writes announcements"}
`Setu.java` trains your model on the eight announcements in `announcements.txt`, then asks it to predict and generate:

```text
$ mvn -q compile exec:java
== A bag of words
{all=1, at=2, breeze=2, express=3, for=1, from=2, ghat=3, is=3, karjat=1, keep=1, konkan=2, late=2, leave=2, lonavala=3, luggage=1, mail=1, minutes=2, monsoon=1, move=1, on=1, one=2, passengers=1, platform=3, please=2, ratnagiri=1, running=3, stop=1, talegaon=1, ten=1, the=7, time=1, times=1, to=6, train=1, twenty=1, two=1, will=3, with=1, you=1, your=1}

== A bigram model, trained on 8 station announcements
after 'the' comes 'ghat'
after 'ghat' comes 'express'
after 'running' comes 'on'
after 'platform' comes 'one'
after 'lonavala' comes 'will'

the ghat express to lonavala will leave from platform one
```

(We ran the solution again on 26 November: exactly this output.)

:::diagram{name="l4j-bigram-chain"}
The generated sentence, step by step, with the count that chose each next word in the eight announcements.
:::

Read the last line: "the ghat express to lonavala will leave from platform one". Your model wrote a correct station
announcement. It does not know what a train is; it has only counted which word follows which. And it could not get
past "one": "one" was only ever the last word of a sentence, so the model had nothing to say next.

Notice too what it cannot do. Ask it anything about "the konkan breeze" and it will still say "ghat" after "the",
because "ghat" is simply more frequent. A language model predicts the **likely** continuation, not the **true** one.
Keep that sentence in mind: it explains hallucinations in chapter 11.
:::

:::step{type=predict title="Guess first"}
:::question
You train the bigram model on 10,000 announcements instead of 8. What happens?
:::
- [x] Its predictions get better, but it still only looks at one word back
- [ ] It starts to understand trains
- [ ] It gets worse, because there is too much data
:::explain
More data gives better counts, so more natural sentences. But the model's view, one word, stays the same. Bigger
language models improved in both ways at once: more data, and a far longer view of the text.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does a bag of words throw away?
:::
- [ ] The words
- [ ] How often each word appears
- [x] The order of the words
:::explain
"Dog bites man" and "man bites dog" have the same bag of words. Order carries meaning, which is why language models
predict words in sequence.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What single task is a modern LLM trained on?
:::
- [ ] Answering questions from a database
- [x] Predicting the next piece of text, given the text before it
- [ ] Translating between languages
:::explain
Answering, translating and summarising all come out of that one skill, learned at enormous scale. Chat models get
extra training on top (chapter 11) so the continuation is a helpful answer.
:::
:::

:::step{type=deep-dive title="Go deeper: n-grams, smoothing and why they stopped"}
**N-grams.** A trigram model looks at two words back, a 5-gram at four. Each extra word makes predictions sharper and
the table vastly bigger: most 5-word sequences appear once or never, even in billions of words.

**Smoothing.** A plain counting model gives zero probability to anything it never saw, so one unseen word breaks a
sentence. Statistical NLP spent twenty years on smoothing tricks that give unseen sequences a small chance.

**Why neural models won.** Counts treat "train" and "rail" as unrelated symbols. Neural models represent words as
vectors, so what they learn about "train" partly carries over to "rail". That idea, embeddings, is chapter 5.

**Probabilities, not one word.** A real model does not return one word: it returns a probability for every possible
next token, and the program chooses. Choosing is where temperature comes in (chapter 6).
:::

:::step{type=recap}
You can now:

- describe the four eras of NLP: rules, statistics, neural networks, transformers;
- turn text into words and count them as a bag of words;
- build a bigram language model that predicts and generates text;
- explain why a language model produces the likely continuation, not necessarily the true one.

Next, chapter 4: models do not read words, they read tokens. What tokens are, why they decide your bill, and how much
text a model can read at once.

:::photo{src="/lesson-images/langchain4j/l4j-03-notes.webp" alt="Sketchnote, A tiny language model (count which word comes next): A language model predicts the next word from the words before. Ours counts word pairs in eight announcements. The flow: Announcements, Count word pairs, Pick the likeliest, Repeat. What we found: after the came ghat 3 times in 7; it wrote a correct announcement; it stopped at one: nothing ever followed; likely is not the same as true." ai="true"}
One page of notes for this chapter.
:::
:::
