:::step{type=story title="A shelf you can search, fix and clear"}
Chapter 12 could save a found item and read it back. A real desk needs more every hour: "anything from Riverside?",
"anything with umbrella in its title?", "mark the phone as returned, its owner just collected it", "that entry was a
mistake, remove it". Four kinds of work, known everywhere by their initials: **CRUD**, Create, Read, Update, Delete.

There is a second problem hiding in chapter 12. One class, `Item`, was the table **and** the answer, so whatever the
table holds would be shown, and a client could try to send its own `id` or `status`. Today Lostdesk gets a small
family of models, one for each direction, and lets the database do the searching.

:::mission
Make `GET /items` filter by `station` and by words in the title, in SQL, and add `PATCH /items/{item_id}`, which
changes only the fields that were sent and saves them.
:::
:::

:::step{type=concept title="A family of models" file="13-crud/main.py" line="9-33"}
`main.py` follows the pattern of FastAPI's own SQL tutorial:

```python
class ItemBase(SQLModel):                 # the fields everyone shares
    title: str = Field(min_length=3, max_length=60, index=True)
    category: str
    station: str = Field(index=True)


class Item(ItemBase, table=True):         # the table: adds id and status
    id: int | None = Field(default=None, primary_key=True)
    status: str = "held"


class ItemCreate(ItemBase):               # what staff send: exactly the shared fields
    pass


class ItemPublic(ItemBase):               # what everyone sees: id and status are always there
    id: int
    status: str


class ItemUpdate(SQLModel):               # PATCH: every field optional
    title: str | None = Field(default=None, min_length=3, max_length=60)
    category: str | None = None
    station: str | None = None
    status: str | None = None
```

| Model | Table? | Used for |
|---|---|---|
| `ItemBase` | no | not used directly; the others inherit its fields |
| `Item` | yes | rows in the database |
| `ItemCreate` | no | the body of `POST`: no `id`, no `status` |
| `ItemPublic` | no | the response model: `id` is a plain `int` here, never `None` |
| `ItemUpdate` | no | the body of `PATCH` |

Every field is written once, and each direction gets exactly what it should: chapter 7's idea, now with a database.
:::

:::step{type=concept title="Searching in SQL with where" file="13-crud/main.py" line="72-84"}
To filter, add conditions to the query before running it:

```python
query = select(Item)
if station:
    query = query.where(Item.station == station)
if q:
    query = query.where(col(Item.title).contains(q))
items = session.exec(query.order_by(Item.id).offset(offset).limit(limit)).all()
```

`Item.station == station` does not compare two values in Python: on a table column it **builds a piece of SQL**.
`col(...)` (from sqlmodel) marks a column so that methods like `.contains()` are available, and `.contains(q)`
becomes SQL's `LIKE`. We switched on `echo` and asked for `?q=UMBRELLA&station=Airport`; SQLModel sent:

```text
SELECT item.title, item.category, item.station, item.id, item.status
FROM item
WHERE item.station = ? AND (item.title LIKE '%' || ? || '%') ORDER BY item.id
 LIMIT ? OFFSET ?
[generated in 0.00009s] ('Airport', 'UMBRELLA', 100, 0)
```

Two `where` calls became `AND`. `offset` and `limit` became SQL's own `OFFSET` and `LIMIT`, so the database sends back
only one page instead of everything. And the answer was the green umbrella, although we searched in capitals: SQLite's
`LIKE` ignores the difference between capital and small letters, for English letters. (PostgreSQL's `LIKE` does not;
it has `ILIKE` for that. Behaviour like this is worth checking whenever you change databases.)
:::

:::step{type=example title="Worked example: why let the database search?"}
You could read every row into Python and filter with a list comprehension, as chapter 3 did. Why not?

1. **Less data travels.** With `where` and `limit`, the database sends back 20 rows, not 200,000.
2. **Indexes.** The database can use an index (the `index=True` on `station` and `title`) to jump straight to the
   matching rows instead of reading them all; the deep dive measures the difference.
3. **One place for the rules.** Sorting, paging and filtering happen in one query, in one order.

The pattern is always the same: start with `select(Item)`, add a `where` for each filter that was **given**, then
`order_by`, `offset`, `limit`, and run it with `session.exec(...).all()`.
:::

:::step{type=predict title="Guess first"}
:::question
Lostdesk has a "green umbrella". On SQLite, does `?q=UMBRELLA` find it?
:::
- [x] Yes
- [ ] No, the capitals differ
:::explain
SQLite's `LIKE` ignores the case of English letters, so `UMBRELLA` matches `umbrella`. We saw the green umbrella come
back. On PostgreSQL the same query would find nothing.
:::
:::

:::step{type=task task=filter_db title="Your turn: filter in the database" file="13-crud/main.py" line="80-82"}
In `list_items`, add a `where` for `station` when it is given, and one for `q` (title contains) when it is given.
They combine: `?q=umbrella&station=Airport` gives only the green umbrella.

Start this chapter's server from `/workspace/13-crud`, log a few items in `/docs`, and try the filters. Then press
**Check**: it fills the table with four items and tries each filter.

The usual slip: writing `if station: query.where(Item.station == station)` without `query = ...`. `where` does not
change the query; it gives back a **new**, narrower one. Without storing it, the filter is thrown away and every
item comes back.
:::

:::step{type=concept title="Updating a row" file="13-crud/main.py" line="91-92"}
Chapter 9's `PATCH` merged a dictionary. With a row, SQLModel has a method that does the same,
`sqlmodel_update`:

```python
db_item = find(session, item_id)                              # the row, or 404
db_item.sqlmodel_update(changes.model_dump(exclude_unset=True))
session.add(db_item)
session.commit()
session.refresh(db_item)
```

`exclude_unset=True` is as important as in chapter 9: only the fields that were sent are copied onto the row. Then
the same save as `POST`: add, commit, refresh. The solution's answer to `PATCH /items/2 {"status": "returned"}`:

```json
{"title":"silver phone","category":"phone","station":"Tech Park","id":2,"status":"returned"}
```

Because `ItemUpdate` has `Field(min_length=3, ...)` on `title`, a two-letter title is still refused with 422: rules
written once apply to every route that uses the model.
:::

:::step{type=task task=update_db title="Your turn: PATCH a row" file="13-crud/main.py" line="91-92"}
Add `PATCH /items/{item_id}`: take an `ItemUpdate`, change only the fields that were sent, save, and give back the
`ItemPublic`; an unknown id gives 404 (`find` does that). Afterwards, `GET /items/2` shows the new status. Then press
**Check**.
:::

:::step{type=concept title="Deleting a row" file="13-crud/main.py" line="95-99"}
The last letter of CRUD is already in the file:

```python
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: SessionDep):
    session.delete(find(session, item_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

`session.delete` marks the row; `commit` runs the `DELETE` statement. We tried it: `204`, and then `GET /items/4`
answered `{"detail":"No item with that id"}`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why does `ItemPublic` declare `id: int` when `Item` has `id: int | None`?
:::
- [ ] It is a mistake
- [x] Anything sent to a client has been saved, so it always has an id
- [ ] Public ids must be numbers, private ones need not
:::explain
`None` only exists before the first save. The response model promises clients an id every time.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`query.where(Item.station == station)` is called, but its result is not stored. What happens?
:::
- [ ] The query is filtered anyway
- [x] Nothing: where gives back a new query, and it was thrown away
- [ ] An error
:::explain
Like a string method (chapter 7 of the Python course), `where` makes a new object. Write `query = query.where(...)`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What do the letters CRUD stand for?
:::
- [ ] Copy, Run, Undo, Delete
- [x] Create, Read, Update, Delete
:::explain
The four things almost every API does with its data: POST, GET, PATCH or PUT, and DELETE.
:::
:::

:::step{type=deep-dive title="Go deeper: what an index is worth, measured"}
We filled a SQLite table in the course image with 200,000 items spread over 200 stations, and timed
`SELECT id FROM item WHERE station = 'Station 7'` (best of 20 runs; 1,004 rows match):

| | Time | What SQLite did (`EXPLAIN QUERY PLAN`) |
|---|---|---|
| no index on `station` | 6.11 ms | `SCAN item`: read all 200,000 rows |
| with an index | 0.187 ms | `SEARCH item USING COVERING INDEX ix_item_station` |

About 30 times faster, and the gap grows with the table. Indexes are not free: every `INSERT` and `UPDATE` must also
update each index, and they take disk space. Index the columns you search and filter by (`station`, `title`), not
every column. Your numbers will differ on another machine; the ratio is what matters.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Design a family of SQLModel models: a shared base, the table, and create, public and update models.
- Filter in SQL with `select(...).where(...)`, `col(...).contains(...)`, `order_by`, `offset` and `limit`.
- Update a row with `sqlmodel_update` and `exclude_unset=True`, and delete one with `session.delete`.
- Explain what an index does, and what it costs.

:::photo{src="/lesson-images/fastapi/fa-13-sketch.webp" alt="Sketchnote: Create, read, update, delete. A family of models gives each direction its own shape, and the database does the searching in SQL. Flow: select(Item), a where for each filter given, order_by, offset and limit, exec(...).all(). Remember: where gives back a new query: store it; sqlmodel_update with exclude_unset changes only what was sent; session.delete, then commit, removes a row; An index makes searches fast and writes a little slower." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 14: Lostdesk outgrows one file, and becomes a package with routers.
:::
