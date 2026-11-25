:::step{type=story title="A photo instead of a question"}
Children at the museum do not always know what to call what they see. A boy stands under a brass ball swinging on a
long wire and asks his father "what is this?", and his father does not know either. He could read the label, if he
found it. Or he could point his phone at the ball and ask Atlas.

Until now, everything Atlas understood was text. This chapter gives it eyes. Modern language models read pictures as
well as words: you send a photo **and** a question in the same message, and the model answers in text, about the
photo.

:::photo{src="/lesson-images/spring-ai/pendulum-photo.webp" alt="Looking down on a golden pendulum bob above a circular floor with a star pattern of coloured marble, ringed by glass" credit="Tengo las llaves" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Foucault_pendulum_in_Katsushika_City_Museum,_02.jpg"}
The Foucault pendulum of the Katsushika City Museum, Tokyo. You will send this photo to Atlas in a minute.
:::

:::mission
Let visitors send a photo with their question, recognise which of the museum's exhibits a photo shows, and keep
each photo's cost under control.
:::
:::

:::step{type=history title="Fifty years to teach computers to see"}
In the summer of **1966**, Seymour Papert at MIT wrote a memo called "The Summer Vision Project". It gave a group of
students one summer to make a computer recognise objects in pictures. The problem turned out to take about fifty
years.

:::before{title="One model per task"}
For decades, vision was its own field, with its own models: one to find faces, another to read handwriting, another to
sort photos of cats from photos of dogs. Each needed thousands of labelled examples, and none of them could talk
about what it saw.
:::

In **2012**, a neural network called AlexNet, by Alex Krizhevsky, Ilya Sutskever and Geoffrey Hinton, won the ImageNet
competition by a wide margin, and deep learning took over computer vision. Then language models learned to read
pictures too: GPT-4 with vision in **2023**, and in **2024** GPT-4o, built from the start to take text, pictures and
sound in one model.

:::solved
**One model that sees and talks.** The same model that answers questions about the pendulum can now look at a photo of
it, name it, and explain it, without a separate vision system. Spring AI calls this **multimodality**: more than one
kind of input in one request.
:::
:::

:::step{type=concept title="A message with a picture in it"}
So far every user message carried text. In Spring AI a user message can also carry **media**: one or more pictures
(and, for some models, sound or video), each with its MIME type:

```java
chat.prompt()
        .user(u -> u.text("What is this exhibit?")
                .media(MimeTypeUtils.IMAGE_JPEG, picture))
        .call()
        .content();
```

1. `.user(u -> ...)` is the same user spec you used for templates in chapter 2.
2. `.text(...)` is the question; `.media(type, picture)` adds the picture, here a `Resource` holding the bytes.
3. The answer is still text: models read pictures, but they write words.

On the way to OpenAI, Spring AI turns this into one message with **two parts**, the picture travelling inside the JSON
as a data URL (the bytes in base64):

```json
{"role": "user", "content": [
  {"type": "text", "text": "What is this exhibit?"},
  {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."}}
]}
```

:::diagram{name="ai-vision"}
The real pendulum photo from this chapter (26 November), with the token counts from the gateway's log.
:::
:::

:::step{type=concept title="What a picture costs"}
Pictures are not free. The model turns a picture into tokens, like text, and you pay for them. How many? This
course measured it, through the gateway, with the pendulum photo at 800 by 600 pixels:

```text
$ lab requests
time (UTC)           model           kind           in    out     ms     cost $  status
2026-11-22 21:38:38  ai-chat         chat        25596     51   2676   0.003870  ok
```

**25,596 input tokens** for one photo and a five-word question; the question alone would have been about 30. At
gpt-4o-mini's price that is about 0.4 US cents a photo: 1,000 visitor photos a day would cost about 4 dollars, every
day, before Atlas says a word.

The reason is in OpenAI's rule for pictures: a detailed picture is cut into **tiles of 512 by 512 pixels**, and each
tile costs a fixed number of tokens. For gpt-4o-mini a picture costs 2,833 tokens, plus 5,667 for each tile. 800 by 600
pixels needs 2 tiles across and 2 down, 4 tiles: 2,833 + 4 x 5,667 = 25,501, plus the question's own tokens, gives the
25,596 measured. Shrink the photo so it fits in one tile, and it
costs about a third (2,833 + 5,667 = 8,500, plus the question):

```text
$ lab requests
time (UTC)           model           kind           in    out     ms     cost $  status
2026-11-23 00:39:11  ai-chat         chat         8595     42   1529   0.001314  ok
```

That is why the `15-vision` project already has a small helper, `Photos.shrink(bytes, 512)`, that every endpoint uses
before sending a photo: the longer side becomes at most 512 pixels, as a JPEG. An exhibit is still easy to recognise
at that size. (Your lab account's daily budget is 50,000 tokens: about five photos a day, so choose them well.)
:::

:::step{type=task task=image_question title="Your turn: a question about a photo" file="15-vision/src/main/java/com/atlas/LookController.java" line="47"}
In `15-vision`, finish `POST /look`: send the question `q` and the picture together in one user message. The picture
is ready, already shrunk, in `picture`, and its type in `type`:

1. `.user(u -> u.text(q).media(type, picture))`
2. `.call().content()` and return it.

The usual slip: sending the original upload instead of `picture`. It works, and costs three times as many tokens.

```bash run
cd 15-vision && mvn -q -o spring-boot:run
```

In a second terminal, send one of the photos in `15-vision/photos/`:

```bash run
cd 15-vision && curl -s -F image=@photos/pendulum.jpg -F q="What is this exhibit?" localhost:8080/look; echo
```

Press **Check**.
:::

:::step{type=try title="Atlas sees"}
Two real answers, each from a photo and a question (our re-run on 26 November gave the same two, in other words, at
8,595 tokens each):

```text
$ curl -s -F image=@photos/pendulum.jpg -F q="What is this exhibit?" localhost:8080/look; echo
This exhibit is likely a Foucault pendulum. It demonstrates the Earth's rotation by showing how the direction of the pendulum's swing changes over time. It’s a fascinating way to see physics in action!
$ curl -s -F image=@photos/prism.jpg -F q="Why does this happen?" localhost:8080/look; echo
This happens due to refraction when light passes through the prism. Different colors of light bend at different angles, creating a rainbow effect. This is called dispersion.
```

Atlas named the pendulum from the photo alone, and explained the rainbow from a picture of a prism. Nothing in the
question said "pendulum" or "prism".
:::

:::step{type=example title="Worked example: a picture into a record" file="15-vision/src/main/java/com/atlas/LookController.java" line="58"}
The museum's website wants more than a sentence: when a visitor sends a photo, it wants to open that exhibit's page.
That needs the exhibit's **name**, exactly as the museum spells it, as data. Two things you already know do it:

```java
String names = String.join(", ", EXHIBITS);
Sighting s = chat.prompt()
        .user(u -> u.text("Which of these exhibits does the photo show: " + names
                + "? If it shows none of them, answer none.").media(type, picture))
        .call()
        .entity(Sighting.class);
```

1. Listing the museum's own names turns an open question ("what is this?") into a choice, so the model answers
   "Rajasaurus skull", not "a dinosaur fossil".
2. "If it shows none of them, answer none" gives the model an honest way out: without it, a photo of the gift shop would
   still be matched to some exhibit.
3. `.entity(Sighting.class)` is chapter 5's structured output, working the same with a picture in the message.
:::

:::step{type=task task=exhibit_from_photo title="Your turn: which exhibit is it?" file="15-vision/src/main/java/com/atlas/LookController.java" line="59"}
Finish `POST /identify`: ask which of `EXHIBITS` the photo shows (or none), with the picture, and return the answer as
a `Sighting`:

1. Join the names: `String.join(", ", EXHIBITS)`.
2. The question with the names and "If it shows none of them, answer none.", plus `.media(type, picture)`.
3. `.call().entity(Sighting.class)`.

The usual slip: leaving out "answer none". Then a photo of something else is still matched to one of the exhibits.

```bash run
cd 15-vision && curl -s -F image=@photos/skull.jpg localhost:8080/identify | jq .
```

Press **Check**.
:::

:::step{type=try title="Three exhibits, and one that is not"}
Real answers for two of the photos in `photos/`:

```text
$ curl -s -F image=@photos/skull.jpg localhost:8080/identify | jq .
{
  "exhibit": "Rajasaurus skull",
  "clue": "Rajasaurus skull"
}
$ curl -s -F image=@photos/engine.jpg localhost:8080/identify | jq .
{
  "exhibit": "none",
  "clue": "This is a vintage steam engine."
}
```

The second photo is a steam engine outside another museum, Bengaluru's Visvesvaraya Industrial and Technological
Museum. It is not one of Atlas's exhibits, and Atlas said so, because the question allowed it.

The skull's `clue` is weak: it repeats the name. (Our re-run on 26 November gave "Fossil of a dinosaur": a vague
field gets a different answer each run.) The field's name was all the model had to go on, and "clue" was not
clear enough. A clearer name (`whatGaveItAway`) or one sentence in the question ("and say what in the photo gave it
away") fixes it. In structured output, your field names are part of the prompt.

(8,595 and 8,815 tokens each: these four photos used most of a day's budget for this course's author. Pictures are the
most expensive thing you can send.)
:::

:::step{type=predict title="Guess first"}
:::question
Shrinking from 800 to 512 pixels cut the cost to about a third. Would shrinking further, to 256 pixels, cut it
again?
:::
- [ ] Yes, to about a third again
- [x] No: the cost is counted in whole tiles, and a 256 pixel picture is still one tile; you would only lose detail
- [ ] The model refuses pictures that small
:::explain
One tile is the smallest unit you pay for. 512 pixels is the sweet spot: the most detail for the price of one tile.
Shrinking on your side is the one lever you control, and it also makes the request smaller and faster to send.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
How does the picture travel to the model in this chapter's requests?
:::
- [ ] As a separate file upload, before the question
- [x] Inside the same user message as the question, as a data URL (base64 bytes)
- [ ] As a link the model downloads
:::explain
Spring AI puts the text and the picture in one message with two parts. (A public URL also works with some models; a
data URL works for any picture you have, including one a visitor just uploaded.)
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does the identify question list every exhibit's name?
:::
- [x] So the model picks one of the museum's own names, which the website can use, or says none
- [ ] Because the model cannot see without a list
- [ ] To make the answer longer
:::explain
A closed list turns recognition into a choice, with names you control. It is the same idea as an enum in structured
output: the model's freedom is limited to what your program can handle.
:::
:::

:::step{type=deep-dive title="Go deeper: more than pictures"}
**Other media.** The same `media(...)` call carries audio for models that hear (`audio/wav`, `audio/mp3`) and, for some
providers, video or PDF files. Spring AI also has separate models for speech: `TranscriptionModel` (speech to text)
and `TextToSpeechModel`, and an `ImageModel` that draws pictures from text.

**Privacy.** Photos carry more than you think: faces of other visitors, and often the location where they were taken in
their metadata. Shrinking and re-encoding as JPEG, as `Photos.shrink` does, drops that metadata. Say on the screen
that photos are sent to an AI service, and do not keep them.

**Limits.** Models can misread small text, count objects badly, and be fooled by pictures made to fool them. For a
museum guide that is fine; for reading a medicine label, it is not.
:::

:::step{type=recap}
You can now:

- explain multimodality: one model that reads text and pictures together;
- send a question and a picture in one user message with `.user(u -> u.text(...).media(type, picture))`;
- turn a picture into a record, with a closed list of names and an honest "none";
- measure what a picture costs, and cut it by shrinking it to one 512 pixel tile.

Next, chapter 16: how do you know Atlas is right? Evaluation.

:::photo{src="/lesson-images/spring-ai/springai-15-notes.webp" alt="Sketchnote, Atlas sees (a photo and a question in one message): Modern models read pictures as well as words. Send the photo with the question; the answer comes back in words. The flow: Photo, Shrink to 512 px, Text + image, Model, Answer. What we measured: 800 x 600: 4 tiles, 25,596 tokens; 512 px: 1 tile, 8,595 tokens; the steam engine: none, an honest answer; name every field clearly: it is part of the prompt." ai="true"}
One page of notes for this chapter.
:::
:::
