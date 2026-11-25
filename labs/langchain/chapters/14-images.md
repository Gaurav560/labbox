:::step{type=story title="A photo instead of a description"}
"There are white patches under my grape leaves. What is it?" is hard to answer in words, and members are farmers, not
plant scientists. Most of them carry a phone with a camera. Sending a photo is easier than describing one.

gpt-4o-mini, the model behind Navin, reads images as well as text. In LangChain an image is one more **content block** (one typed piece of a message: some text, an image, a file) inside
a `HumanMessage`, next to the text. And combined with chapter 13's structured output, a photo can come
back as a checked report.

This chapter is also a lesson in responsibility. A wrong answer about a sick vine can cost a season's harvest, and the
model's first answer here was confidently wrong in exactly that way.

:::mission
Put a photo and a question into one message, then get a structured first-look report about a sick grape leaf, with
rules that keep Navin from recommending chemicals.
:::
:::

:::step{type=concept title="Content blocks: text and images in one message" file="14-images/leaf.py" line="22-27"}
Until now a message's content was a string. It can also be a **list of blocks**:

```python
HumanMessage(content=[
    {"type": "text", "text": "These spots appeared on my grape leaves. What could it be?"},
    {"type": "image", "base64": "/9j/4AAQSkZJRg...", "mime_type": "image/jpeg"},
])
```

These are LangChain's **standard content blocks**: the same shape for every provider. LangChain translates them; for
OpenAI the image becomes a data URL (`data:image/jpeg;base64,...`) in an `image_url` part. An image block can also
point to a `url` instead of carrying the bytes.

Base64 turns bytes into text (A to Z, a to z, 0 to 9, `+` and `/`) so they can travel inside JSON; it makes the data
about a third larger.
:::

:::step{type=task task=image_message title="Your turn: a message with a photo" file="14-images/leaf.py" line="22-27"}
Finish `image_message(question, image, mime_type)`. `image` is the photo's raw bytes.

1. Return a `HumanMessage` whose `content` is a list of two blocks.
2. First `{"type": "text", "text": question}`.
3. Then `{"type": "image", "base64": base64.b64encode(image).decode(), "mime_type": mime_type}`. `b64encode` gives
   bytes; `.decode()` turns them into the text JSON needs. The **MIME type** names the file format (`image/jpeg`).

The usual slip: forgetting `.decode()`, which sends `b'...'` instead of plain text.

Press **Check**.
:::

:::step{type=history title="Models that can see, and a disease from overseas"}
:::before{title="Text only"}
Until 2023 the most widely used language models read only text (research models such as DeepMind's Flamingo, 2022,
could already talk about images). Image recognition was mostly a separate field, with separate models that could label
a picture but not talk about it.
:::

In **January 2021** OpenAI's **CLIP** learned to connect images and text from 400 million captioned pictures. In
**September 2023** GPT-4 gained vision, and in **May 2024** **GPT-4o** was trained on text, images and audio together;
gpt-4o-mini, Navin's model, followed in **July 2024**.

The leaf in this chapter has its own history. Grape **downy mildew** (*Plasmopara viticola*) is native to North America
and reached French vineyards around **1878**, destroying harvests. In **1885** the botanist Pierre-Marie-Alexis
Millardet showed that a copper mixture, later called Bordeaux mixture, protected the vines. Diagnosing it still takes a
trained eye, which is the point of this chapter's rules.

:::solved
**Show, don't describe.** A member's photo carries details no description would. The model's reading of it is a first
look, and must be treated as one.
:::

:::timeline
- **1878** Downy mildew reaches French vineyards.
- **2021** CLIP: images and text in one model.
- **2024** GPT-4o (May) and gpt-4o-mini (July): one model for text and images.
:::

**Pierre-Marie-Alexis Millardet** (1838 to 1902), the botanist who showed in 1885 that a copper mixture protected vines from downy mildew.

:::photo{src="/lesson-images/langchain/alexis-millardet.webp" alt="A black and white portrait of Alexis Millardet, a bearded man in a dark coat" credit="Unknown author" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AAlexis_Millardet.jpg"}
Alexis Millardet.
:::
:::

:::step{type=concept title="A report, with rules" file="14-images/leaf.py" line="9-19"}
`LeafReport` (chapter 13's idea) has four fields: crop, problem, confidence, and next step. And `RULES` is a system
message that sets limits on what Navin may say:

```text
You give a first look at a photo, never a diagnosis. Never recommend a chemical, a spray or a dose: the next step is
always to show the leaf to the co-op's agronomist, Mrs. Kulkarni.
```

Why such a strict rule? Because of what happened when we first ran this chapter without it (next step but one).
:::

:::step{type=task task=leaf_report title="Your turn: the leaf report" file="14-images/leaf.py" line="30-34"}
Finish `leaf_report(question, image)`: return
`model.with_structured_output(LeafReport).invoke([SystemMessage(RULES), image_message(question, image)])`.

The usual slip: leaving out `SystemMessage(RULES)`. The check looks for `RULES` as the system message, because
without it the real model's next step was spraying advice (see below).

```bash run
cd /workspace/14-images && python main.py
```

Press **Check**.
:::

:::step{type=try title="Careful: a confident wrong diagnosis"}
`leaf.jpg` is a real photo of grape **downy mildew**: the white, downy growth on the underside of a leaf (photo by Jerzy
Opioła, CC BY-SA 4.0; credit in `leaf-credit.txt`). When we first wrote this chapter, `leaf_report` sent the photo **without** the rules. The real answer (we ran it twice
more on 25 November and got the same advice both times):

```text
$ python main.py
leaf.jpg: 47,208 bytes
crop        Grapes
problem     Possible powdery mildew or leaf spot disease
confidence  medium
next_step   Consider applying a fungicide and improving air circulation around the plants.
```

The crop is right. The disease is not: powdery mildew is a different fungus, and the treatments differ. And the next
step tells a farmer to spray, with "medium" confidence. A member who trusted it could spray the wrong product, at the
wrong time, before the co-op's 10-day harvest rule. With `RULES` as the system message, the same photo:

```text
$ python main.py
leaf.jpg: 47,208 bytes
crop        Grapes
problem     Spots on leaves, possibly indicating a fungal issue or nutrient deficiency.
confidence  medium
next_step   Please show this leaf to Mrs. Kulkarni for a detailed analysis.
```

We ran it again with the rules on 25 November and got exactly this. Vaguer, and much safer: it says what it can see and sends the member to a person who can diagnose. For an assistant
whose words can cost a harvest, that is the right trade.
:::

:::step{type=try title="What a photo costs"}
The gateway's log for that call:

```text
$ lab requests --last
2026-11-23 13:02:00 UTC  ai-chat -> openai/gpt-4o-mini  8697 in, 46 out
```

**8,697 input tokens** for one 500 by 375 photo and two short sentences, against about 220 for a text question in
chapter 9 (we got 8,697 again on 25 November). OpenAI counts images for gpt-4o-mini at a high token rate: a fixed
part plus a part for each **tile** (a square piece of the image); this small photo fits in one tile. So this one photo
cost about $0.0013 (8,697 x $0.15 per million), as much as about 30 text answers from chapter 9.
Photos are worth it when they replace a long, uncertain description; resize them before sending (this one is 500
pixels wide), and never send them by default.
:::

:::step{type=predict title="Guess first"}
:::question
You send the same photo at 2,000 pixels wide instead of 500. What happens to the cost?
:::
- [ ] Nothing: an image is one token
- [x] It can rise: larger images are cut into more tiles, each with its own tokens
- [ ] It falls: more detail, fewer guesses
:::explain
Providers price images by size (tiles). Resize to what the question needs.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
How does an image travel inside a JSON request?
:::
- [ ] As a file attachment
- [x] As base64 text in a content block (or as a URL the provider downloads)
- [ ] As a separate HTTP request
:::explain
Base64 turns bytes into characters JSON can carry, at about a third more size.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does `RULES` forbid recommending chemicals?
:::
- [ ] The model cannot name chemicals
- [x] A wrong diagnosis plus spraying advice can harm the crop and the member; diagnosis belongs to the agronomist
- [ ] It saves tokens
:::explain
The model's first answer named the wrong disease and advised a fungicide. Rules limit what a mistake can cost.
:::
:::

:::step{type=deep-dive title="Go deeper: images in production"}
**Privacy.** Photos can contain faces, documents and locations (in the file's metadata). Strip metadata before
sending, and keep only what the question needs.

**URLs instead of bytes.** For large or reused images, store them and send `{"type": "image", "url": ...}`; the
provider fetches it.

**Measure on real photos.** A golden set (chapter 26) of photos with known diagnoses, checked by the agronomist, tells you
how often the first look is right, before members rely on it.
:::

:::step{type=recap}
You can now:

- put text and an image into one `HumanMessage` with content blocks;
- get a structured report from a photo;
- write system rules that limit what a wrong answer can cost;
- read an image's real token cost and decide when a photo is worth it.

Next, chapter 15: memory. Navin remembers what each member said earlier.

:::photo{src="/lesson-images/langchain/lc-14-notes.webp" alt="Handwritten notes about images: A photo is one more content block in a HumanMessage. Base64 turns its bytes into text, about a third larger. Without rules, Navin named the wrong disease and advised a spray. With rules, it sent the member to the agronomist. Our 500 by 375 photo and its question took 8,697 input tokens. Resize photos, and send them only when they help." ai="true"}
One page of notes for this chapter.
:::
:::
