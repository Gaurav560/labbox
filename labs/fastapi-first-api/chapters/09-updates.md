:::step{type=story title="The umbrella moved to another shelf"}
Items on a lost-property shelf do not stay still. The blue school bag moves from shelf B-11 to B-12 to make room. A
title turns out to be wrong ("silver phone" was really grey). An item is collected by its owner and has to leave the
records. So far Lostdesk can create and read; today it learns to **change** and to **remove**.

Records like these have always been kept up to date by hand. This drawer at the Library of Congress holds index cards
typed one by one; correcting a record meant finding its card and changing just that card.

:::photo{src="/lesson-images/fastapi/card-catalog.webp" alt="A long metal drawer full of typed index cards standing on end, pulled out of a cabinet and resting on a wooden table" credit="Michael Holley" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Copyright_Card_Catalog_Drawer.jpg"}
A drawer of copyright catalog cards at the Library of Congress, Washington.
:::

:::mission
Add `PATCH /items/{item_id}`, which changes only the fields that were sent, and `DELETE /items/{item_id}`, which
removes an item and answers 204 No Content.
:::
:::

:::step{type=concept title="PUT replaces; PATCH changes a part" file="09-updates/main.py" line="52-56"}
HTTP has two methods for changing something, and they mean different things:

| Method | The body holds | Fields not sent |
|---|---|---|
| `PUT /items/2` | the **whole** new item | must be sent anyway: PUT replaces everything |
| `PATCH /items/2` | only the fields to change | stay as they were |

`main.py` already has `PUT`:

```python
@app.put("/items/{item_id}")
def replace_item(item_id: int, item: FoundItemIn):
    find(item_id)
    FOUND[item_id] = {"id": item_id, **item.model_dump(mode="json")}
    return FOUND[item_id]
```

It takes a full `FoundItemIn`, so every field is required. We asked it to move the bag with just the shelf,
`PUT /items/2 {"shelf": "B-12"}`, and it refused with 422: `title`, `line` and `station` all `"Field required"`.
To move one bag to one shelf, PUT wants the whole bag described again. That is what PATCH is for.

`find(item_id)` is a small helper at the top: it gives back the item or raises the 404, so every route that needs an
existing item says so in one line.
:::

:::step{type=concept title="A model where everything is optional" file="09-updates/main.py" line="25-31"}
PATCH needs a body in which every field may be left out:

```python
class ItemUpdate(BaseModel):
    title: str | None = None
    line: Line | None = None
    station: str | None = None
    shelf: str | None = None
```

But now there is a puzzle. `{"shelf": "B-12"}` gives an `ItemUpdate` whose `title` is `None`. Did the client mean
"leave the title alone", or "set the title to nothing"? Pydantic remembers which fields were really **set**, and
`model_dump(exclude_unset=True)` gives back only those. Press Play:

:::diagram{name="fastapi-patch-merge"}
exclude_unset keeps only the fields the client sent, so merging them changes nothing else.
:::

We tried the wrong way on purpose: a plain `model_dump()` of `ItemUpdate(shelf="S-1")` merged into item 3 gave
`{'id': 3, 'title': None, 'line': None, 'station': None, 'shelf': 'S-1'}`. One shelf change wiped three fields.
:::

:::step{type=example title="Worked example: merging a dictionary"}
`dict.update` copies keys from one dictionary into another, overwriting the ones that exist:

```python
item = {"id": 2, "title": "blue school bag", "shelf": "B-11"}
item.update({"shelf": "B-12"})
# item is now {"id": 2, "title": "blue school bag", "shelf": "B-12"}
```

1. `shelf` existed, so its value changed.
2. `id` and `title` were not in the second dictionary, so they stayed.
3. `update` changes the dictionary in place and gives back `None`; return `item` itself afterwards.

`FOUND[2]` is that same dictionary object, so changing `item` changes what is stored.
:::

:::step{type=task task=patch_item title="Your turn: PATCH" file="09-updates/main.py" line="59"}
Add `PATCH /items/{item_id}`. It takes an `ItemUpdate`, changes only the fields that were sent, and gives back the
whole item:

```text
PATCH /items/2 {"shelf": "B-12"}
200 {"id":2,"title":"blue school bag","line":"blue","station":"Old Market","shelf":"B-12"}
```

(that is the solution's real answer). `{"line": "purple"}` still gives 422, and an unknown id gives 404. Then press
**Check**.
:::

:::step{type=concept title="DELETE, and an answer with nothing in it"}
Removing is the simplest change of all: `del FOUND[item_id]`. The interesting question is what to answer. There is
nothing left to show, so the right status is **204 No Content**: "it worked, and the body is empty on purpose".

```python
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
```

A 204 must not have a body. FastAPI makes sure: we returned a dictionary from a 204 route by mistake, and the client
still received an empty body. Returning `Response(status_code=204)` (or nothing at all) says what you mean.

And deleting twice? The second `DELETE /items/1` finds nothing, so it answers 404. We checked the solution: `204`,
then `GET /items/1` gives `404 {"detail":"No item with that id"}`, then `DELETE /items/1` again gives 404.
:::

:::step{type=predict title="Guess first"}
:::question
A client sends `PATCH /items/2` with an empty body, `{}`. What happens?
:::
- [ ] 422, because nothing was sent
- [x] 200, and the item is unchanged
- [ ] Every field becomes null
:::explain
Every field of `ItemUpdate` is optional, and `exclude_unset=True` gives an empty dictionary, so the update changes
nothing.
:::
:::

:::step{type=task task=delete_item title="Your turn: DELETE" file="09-updates/main.py" line="62"}
Add `DELETE /items/{item_id}`: it removes the item and answers **204** with no body; an unknown id gives 404 (`find`
does that). Afterwards `GET /items/1` gives 404, while other items are still there.

```bash run
curl -s -i -X DELETE localhost:8000/items/1
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which method moves the bag to shelf B-12 without sending its title, line and station again?
:::
- [ ] PUT
- [x] PATCH
- [ ] POST
:::explain
PATCH changes part of something; PUT replaces all of it.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `model_dump(exclude_unset=True)` leave out?
:::
- [ ] Fields whose value is None
- [x] Fields the client did not send
- [ ] Fields with a default
:::explain
It is about what was set, not about the value. A client may send `"details": null` on purpose, and that is kept.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why 204 for a successful DELETE, not 200?
:::
- [ ] 200 is not allowed for DELETE
- [x] There is nothing to send back, and 204 says the empty body is on purpose
:::explain
200 with an empty body would leave a client wondering whether something went missing.
:::
:::

:::step{type=deep-dive title="Go deeper: idempotent methods, and soft deletes"}
**Idempotent** means "doing it twice has the same effect as doing it once". `PUT` and `DELETE` are idempotent by
design: replacing an item with the same data twice, or deleting it twice, leaves the same state (the second DELETE
says 404, but nothing more changes). `POST` is not: posting the same found item twice logs two items. That is why
browsers and libraries happily retry a failed `PUT` or `DELETE`, but ask before resending a `POST`.

**Soft deletes.** Real lost-property systems rarely forget anything: the law may require them to keep records for
years. Instead of deleting, they set `"status": "returned"` with a date, and the lists hide those items. A `DELETE`
route can do exactly that, and still answer 204.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Tell PUT (replace the whole thing) from PATCH (change a part), and write both.
- Build an update model with every field optional, and merge only what was sent with `exclude_unset=True`.
- Write a DELETE route that answers 204 No Content, and 404 when there is nothing to delete.
- Explain idempotent methods, and why real systems often prefer a soft delete.

:::photo{src="/lesson-images/fastapi/fa-09-sketch.webp" alt="Sketchnote: PUT, PATCH and DELETE. PUT replaces the whole thing. PATCH changes only the fields that were sent. DELETE removes it. Flow: PATCH body arrives, every field optional, keep only the fields sent, merge into the stored item, give back the whole item. Remember: exclude_unset keeps only the fields the client set; A plain model_dump() would wipe the others; DELETE answers 204 with no body; PUT and DELETE are idempotent; POST is not." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 10: headers, forms and files, so a found item can get a photo.
:::
