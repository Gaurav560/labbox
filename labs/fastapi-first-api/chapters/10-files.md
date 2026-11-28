:::step{type=story title="A photo is worth a long description"}
"A black umbrella" describes a hundred umbrellas. A photo of the actual one, with its bent spoke and wooden handle,
lets its owner say "yes, that one" in a second. So the desk wants to attach a photo to each found item.

And there is a second problem: anyone can log a found item today. A prankster could fill the shelf with imaginary
phones. Until real sign-in arrives in chapter 16, only a desk that knows the **desk key** may log items, and the key
travels in a header.

Headers and bodies are older than the web. A letter has an envelope that the post office reads (the address, the
stamp, the postmark) and a letter inside that only the receiver reads. HTTP works the same way: headers outside,
body inside.

:::photo{src="/lesson-images/fastapi/stamped-envelope.webp" alt="An old cream-coloured envelope addressed in ink handwriting to Lieut. Edwin T. Carrington, with a pink stamp and a round postmark dated Nov 21 in the top right corner" credit="Gladstone Collection, Library of Congress" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Stamped_envelope_addressed_to_Lieut_Edwin_T._Carrington_LCCN2010652109.jpg"}
A stamped envelope from the American Civil War era: the address and postmark outside, the letter inside.
:::

:::mission
Make `POST /items` demand the right `X-Desk-Key` header, and add `POST /items/{item_id}/photo`, which accepts a
JPEG or PNG of up to 2 MB and saves it.
:::
:::

:::step{type=concept title="Reading a header" file="10-files/main.py" line="27-32"}
A header is a parameter like any other, with `Header()` to say where it comes from:

```python
x_desk_key: Annotated[str | None, Header()] = None
```

Python names cannot contain `-`, and HTTP headers usually do. So FastAPI translates: the parameter `x_desk_key` reads
the header `X-Desk-Key` (underscores become hyphens; capitals do not matter in header names). In `/openapi.json` the
solution's parameter is listed as `{"name": "x-desk-key", "in": "header", "required": false, ...}`.

With the default `None`, a missing header is not a 422: your code decides. Here it decides 401 Unauthorized, the
status for "you have not shown who you are" (chapter 17 makes this proper):

```bash
curl -s -i -X POST localhost:8000/items -d "title=red scarf&station=University"
```

```text
HTTP/1.1 401 Unauthorized
...
{"detail":"Only staff at a desk can log items"}
```

and with the header, `-H "X-Desk-Key: riverside-desk-7"`, the same request gives `{"id":3,"title":"red scarf",
"station":"University","photo":null}`. (Both captured from the solution.)
:::

:::step{type=concept title="Form fields instead of JSON" file="10-files/main.py" line="28-30"}
Look at `log_found_item`'s parameters in this chapter: `Annotated[str, Form(min_length=3)]`. The desk's old kiosk
sends a plain web form, not JSON. A web **form** sends its fields as `title=red+scarf&station=University`, with the
header `content-type: application/x-www-form-urlencoded`, the format browsers have used since the early web.
`Form()` tells FastAPI to read a field from there. (`curl -d "a=1&b=2"` sends exactly this.)

Sending JSON to a form route does not work: we posted `{"title": ..., "station": ...}` as JSON to the starter, and both
fields came back `"missing"` in a 422, `"loc":["body","title"]`. FastAPI looked in the form and found nothing. Form
reading needs the package `python-multipart`, which the lab image has; chapter 16's login form uses it again.
:::

:::step{type=task task=desk_header title="Your turn: the desk key" file="10-files/main.py" line="31"}
Add the `X-Desk-Key` header to `log_found_item`. When it is missing or is not `DESK_KEY`, answer **401** with a
`detail`; with the right key, log the item as before (201).

Then press **Check**. The usual slip, tried: naming the parameter `desk_key`. That reads a header called `Desk-Key`,
so the `X-Desk-Key` the desk sends is never seen, and every request gets your 401, even with the right key. The
parameter's name decides the header's name.
:::

:::step{type=concept title="Uploading a file"}
A file cannot travel in a URL-encoded form; it is bytes, not text. Browsers and `curl -F` send files as
`multipart/form-data`: the body is split into parts, one per field, each with its own little headers (its name, its
file name, its type) and then its bytes.

FastAPI hands you an uploaded file as an **`UploadFile`**:

| Attribute or method | Gives |
|---|---|
| `photo.filename` | the name on the client's computer, like `umbrella.png` |
| `photo.content_type` | the type the client **claims**, like `image/png` |
| `await photo.read()` | the bytes |

The parameter name is the form field's name: `photo: UploadFile` reads the part called `photo`. `read()` must be
awaited, so the route is written `async def` (chapter 18 explains `async` and `await` in full; for now: write
`async def` and `await photo.read()`).
:::

:::step{type=try title="Send a photo with curl"}
This chapter's folder has a tiny photo to send, `umbrella.png`: a 16 by 16 grey square, 77 bytes. We sent it to the
solution:

```bash
curl -s -F "photo=@umbrella.png;type=image/png" localhost:8000/items/1/photo
```

```text
{"item_id":1,"filename":"umbrella.png","saved_as":"photos/1.png","size":77}
```

`-F` sends a multipart form; `@umbrella.png` means "the contents of this file"; `;type=image/png` sets its content
type. Then a text file, `curl -s -i -F "photo=@notes.txt" ...`:

```text
HTTP/1.1 415 Unsupported Media Type
...
{"detail":"Send a JPEG or PNG photo"}
```

curl guessed `text/plain` from the `.txt` ending, and the route refused it. **415 Unsupported Media Type** is the
status for "I do not accept this kind of content"; **413 Content Too Large** for "too big".
:::

:::step{type=concept title="Never trust what the client says about a file"}
Three rules for every upload, and the reasons behind them:

1. **Check the type.** `content_type` is only what the client claims, but refusing everything that is not even
   claimed to be an image stops most mistakes. (The deep dive shows how to check the bytes themselves.)
2. **Check the size.** Without a limit, one 4 GB upload fills the server's disk or memory. Lostdesk allows 2 MB:
   `len(data) > MAX_PHOTO_BYTES`.
3. **Choose the file name yourself.** A client's file name can be anything, including `../../main.py`, which would
   overwrite your code if you saved under it. Lostdesk saves as `photos/<item_id>.png`: a name it controls.
:::

:::step{type=task task=upload_photo title="Your turn: a checked upload" file="10-files/main.py" line="38-40"}
Add `POST /items/{item_id}/photo` with a parameter `photo: UploadFile`:

- an unknown item gives **404**;
- anything but `image/jpeg` or `image/png` gives **415** (`PHOTO_TYPES` maps them to `jpg` and `png`);
- more than 2 MB gives **413**;
- otherwise save the bytes as `photos/<item_id>.<ext>`, set the item's `"photo"` to that path, and give back
  `{"item_id": 1, "filename": "umbrella.png", "saved_as": "photos/1.png", "size": 77}`.

```bash run
cd /workspace/10-files && curl -s -F "photo=@umbrella.png;type=image/png" localhost:8000/items/1/photo
```

(with this chapter's server running). Then press **Check**.

The usual slip: `def` instead of `async def` with `await photo.read()`. Python refuses to even load the file:
`'await' outside async function`. Make the route `async def`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which header does the parameter `x_request_id: Annotated[str | None, Header()] = None` read?
:::
- [ ] `x_request_id`
- [x] `X-Request-Id` (in any capitals)
- [ ] `Request-Id`
:::explain
Underscores become hyphens, and header names ignore capitals.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why save an upload as `photos/<item_id>.png` instead of under `photo.filename`?
:::
- [ ] Shorter names are faster
- [x] The client controls `filename`; a name like `../../main.py` could overwrite files
- [ ] PNG files must be named by number
:::explain
Anything from the client is input to check, and that includes a file's name.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
An upload is 5 MB, over the 2 MB limit. Which status fits?
:::
- [ ] 415
- [x] 413
- [ ] 422
:::explain
413 is "content too large"; 415 is "wrong kind of content".
:::
:::

:::step{type=deep-dive title="Go deeper: checking the bytes, and where photos really live"}
**Magic bytes.** Every PNG file starts with the same eight bytes, `89 50 4E 47 0D 0A 1A 0A` (the middle three spell
`PNG`); a JPEG starts with `FF D8 FF`. Checking `data[:8]` catches a text file renamed to `.png` and sent as
`image/png`. Libraries like Pillow go further and actually open the image.

**Big uploads.** `await photo.read()` loads the whole file into memory before you can check its size. For large
files, read in chunks (`await photo.read(64 * 1024)` in a loop) and stop as soon as the limit is passed, or let the
proxy in front of the server refuse oversized bodies first.

**Where photos live.** A folder on the server is fine for learning. Real services put files in object storage (such
as Amazon S3) and keep only the address in the database, so any number of servers can share them.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read a header with `Header()`, knowing that `x_desk_key` means `X-Desk-Key`.
- Read web-form fields with `Form()`, and tell a form body from a JSON body.
- Accept an uploaded file with `UploadFile` in an `async def` route, and send one with `curl -F`.
- Check an upload's type and size (415, 413), and save it under a name you choose.

:::photo{src="/lesson-images/fastapi/fa-10-sketch.webp" alt="Sketchnote: Headers, forms and files. Headers travel outside the body, like an envelope. Forms send fields; files travel as multipart parts. Flow: a header says who sends it, form fields carry text, the file part carries bytes, check type and size, save under your own name. Remember: x_desk_key reads the X-Desk-Key header; UploadFile needs async def and await read(); 415: wrong type. 413: too large; Never trust the client's file name." ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 2. Lostdesk's data has shape, rules and privacy, and it speaks in precise status codes. Next,
Part 3: structure and data, starting with dependencies.
:::
