:::step{type=story title="What happens to the shelf when the server restarts?"}
Every chapter so far kept the found items in a Python dictionary, in the server's memory. Save `main.py`, the server
restarts, and every item you logged is gone. Run two copies of Lostdesk to share the load, and each has its own,
different shelf. A real lost-property office cannot work like that.

Keeping data safely outside a program's memory is one of computing's oldest problems. In 1956 IBM shipped the first
hard disk drive, the IBM 350, as part of its RAMAC computer: fifty metal disks, each 24 inches across, holding five
million characters in all.

:::photo{src="/lesson-images/fastapi/ramac-disk.webp" alt="The IBM 350 disk unit behind glass in a museum: a tall stack of large metal platters in a cylindrical housing, with an access arm mechanism and wiring on its left" credit="ArnoldReinhold" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:IBM_350_RAMAC_disk_mechanism.agr.jpg"}
The disk mechanism of an IBM 350, at the Computer History Museum.
:::

Today Lostdesk moves its found items into a **database**: a file on disk, managed by a program built to store,
find and protect data, which every copy of the server can share.

:::mission
Save found items as rows in a SQLite database with SQLModel: `POST /items` adds a row, and `GET /items/{item_id}`
reads one back.
:::
:::

:::step{type=concept title="Tables, rows, and SQLite"}
A **relational database** keeps data in **tables**: a table has named **columns**, and each thing is one **row**.
Lostdesk's item table looks like this:

| id | title | station | status |
|---|---|---|---|
| 1 | red scarf | University | held |
| 2 | black umbrella | Riverside | held |

Programs talk to it in **SQL** (Structured Query Language): `INSERT INTO item ...` adds a row, `SELECT ... FROM item
WHERE id = 1` reads one.

Lostdesk uses **SQLite**, a database that lives in a single file (`lostdesk.db`) and runs inside your program, with no
separate server. D. Richard Hipp wrote it in 2000, and Python has it built in. Its own website calls it the most
widely deployed database in the world: it is inside every phone and every major browser. For learning, and for many
small real services, it is exactly right; chapter 21 shows how the same code points at a bigger database.
:::

:::step{type=concept title="SQLModel: one class, two jobs" file="12-database/main.py" line="9-22"}
Writing SQL by hand for every query is slow and easy to get wrong. **SQLModel**, written in 2021 by FastAPI's own
author, lets one Python class be a Pydantic model **and** a database table:

```python
class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    station: str
    status: str = "held"
```

- `table=True` makes it a table, named `item`.
- `primary_key=True`: `id` is the row's unique number. It is `None` until the database chooses it, which is why its
  type is `int | None`.
- `index=True` asks the database to keep an **index** on `title`: a sorted lookup list, so searching by title does
  not mean reading every row.
- `status` has a default: new rows start as `"held"`.

`ItemCreate`, just above it, is the input model: what staff may send (a title of 3 to 60 characters and a station).
It is a plain `SQLModel` without `table=True`, so it is only a Pydantic model. Under the hood SQLModel uses
**SQLAlchemy**, Python's standard database toolkit since 2006.
:::

:::step{type=concept title="The engine, the session, and yield" file="12-database/main.py" line="25-33"}
Three pieces connect Lostdesk to the file:

```python
engine = create_engine("sqlite:///lostdesk.db", connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

- The **engine** knows where the database is: `sqlite:///lostdesk.db` means "the SQLite file lostdesk.db, in the
  folder the server runs in". One engine for the whole app.
- A **session** is one conversation with the database: you add and change objects in it, then `commit` to save them
  all at once.
- `get_session` is a dependency (chapter 11) with `yield` instead of `return`. FastAPI runs it up to the `yield`,
  hands the session to the route, and after the response has been sent, runs the rest: the `with` block ends and
  the session is closed. Every request gets its own session, and none is ever left open.

:::diagram{name="fastapi-session"}
Each request gets a session from get_session; the code after yield closes it once the answer has gone.
:::

(`check_same_thread: False` lets SQLite be used from the different threads FastAPI may run your routes in; the docs'
SQL tutorial uses the same line.)
:::

:::step{type=concept title="Creating the tables at start-up" file="12-database/main.py" line="36-42"}
A new database file is empty: no tables. Someone has to say `CREATE TABLE` once. Lostdesk does it when the server
starts, in a **lifespan** function:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)  # create the tables, once, when the server starts
    yield


app = FastAPI(lifespan=lifespan)
```

Code before `yield` runs at start-up; code after it would run at shutdown. `create_all` creates every table class it
knows about, and skips tables that already exist. (FastAPI's SQL tutorial still uses an older `@app.on_event
("startup")` hook; `lifespan` is the newer, recommended way, from the docs' "Lifespan Events" page.)
:::

:::step{type=try title="The SQL behind your Python" file="12-database/main.py" line="25"}
SQLModel writes SQL for you, but it is not magic. With `echo=True` added to `create_engine`, the engine prints every
statement it sends. We did that with the solution, sent one `POST` and one `GET`, and kept the important lines:

```text
CREATE TABLE item (
	id INTEGER NOT NULL,
	title VARCHAR NOT NULL,
	station VARCHAR NOT NULL,
	status VARCHAR NOT NULL,
	PRIMARY KEY (id)
)
CREATE INDEX ix_item_title ON item (title)
COMMIT
INSERT INTO item (title, station, status) VALUES (?, ?, ?)
[generated in 0.00013s] ('red scarf', 'University', 'held')
COMMIT
SELECT item.id, item.title, item.station, item.status
FROM item
WHERE item.id = ?
[generated in 0.00012s] (1,)
```

The table, the index on `title`, and the row, inserted with its values sent separately (the `?` marks) so that a
title can never be mistaken for SQL. After the commit, `session.refresh` ran a `SELECT` to read back the `id` that
SQLite chose. Try `echo=True` yourself; then take it out again, because it is very talkative.
:::

:::step{type=example title="Worked example: saving a report"}
This is not in your project. Saving a row always follows the same four steps:

```python
@app.post("/reports", status_code=201)
def create_report(report: ReportCreate, session: SessionDep) -> Report:
    db_report = Report.model_validate(report)   # 1. input model -> table row
    session.add(db_report)                       # 2. put it in the session
    session.commit()                             # 3. save: INSERT, then COMMIT
    session.refresh(db_report)                   # 4. read back what the database set (the id)
    return db_report
```

Reading one row by its primary key is one line, `session.get(Report, report_id)`, which gives the row or `None`.
:::

:::step{type=predict title="Guess first"}
:::question
You log a red scarf, then save `main.py` so the server restarts. What does `GET /items` show?
:::
- [ ] An empty list: a restart wipes everything
- [x] The red scarf: it is in lostdesk.db
:::explain
The row is in the file, not in the program's memory. The lifespan's `create_all` skips the existing table, and the
data is still there.
:::
:::

:::step{type=task task=create_found title="Your turn: save a row" file="12-database/main.py" line="50-51"}
Add `POST /items`: it takes an `ItemCreate`, saves it as an `Item` row, and gives back the row with its new id and
status 201. The solution answered:

```text
201 {"title":"red scarf","station":"University","status":"held","id":1}
```

(The keys come back in the order SQLModel stores them: the inherited fields first, `id` last. JSON objects have no
meaningful order, so clients never rely on it.) Start this chapter's server from `/workspace/12-database`, try it in
`/docs`, then press **Check**. The check also opens `lostdesk.db` and looks for your row.

The usual slip, tried: forgetting `session.commit()`. Nothing is saved, and `session.refresh` then has nothing in
the database to read back. The client gets 500, and the terminal ends with:

```text
sqlalchemy.exc.InvalidRequestError: Instance '<Item at 0x781f3e63f750>' is not persistent within this Session
```

"Not persistent" means "not saved in the database yet". (The `0x...` number is a memory address and differs every
run.) Add the commit before the refresh.
:::

:::step{type=task task=read_found title="Your turn: read a row" file="12-database/main.py" line="54"}
Add `GET /items/{item_id}`: `session.get(Item, item_id)`, or 404 when it gives `None`. Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why is `id` typed `int | None` in the table model?
:::
- [ ] Some items have no id
- [x] It is None until the database chooses it on INSERT
- [ ] SQLite cannot store integers
:::explain
A new `Item` object has no id yet. After `commit` and `refresh`, it holds the number SQLite gave the row.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
When does the code after `yield` in `get_session` run?
:::
- [ ] Before the route
- [x] After the response has been sent
- [ ] Only when the server stops
:::explain
A dependency with `yield` wraps the request: set-up before, clean-up after.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `session.commit()` do?
:::
- [ ] Reads the row back
- [x] Saves everything added to the session to the database
- [ ] Closes the session
:::explain
Until the commit, nothing is written to the file. `refresh` reads back; the end of the `with` block closes.
:::
:::

:::step{type=deep-dive title="Go deeper: migrations, and other databases"}
**create_all only creates.** If you add a column to `Item` next month, `create_all` sees that the table exists and
does nothing: the new column is never added. Real projects change their tables with **migrations**, small scripts
that each make one change (`ALTER TABLE item ADD COLUMN shelf ...`), run in order; Alembic is the usual tool for
SQLAlchemy and SQLModel.

**Other databases.** The engine's URL decides the database. `postgresql://user:password@host/lostdesk` points the
same code at PostgreSQL, the usual choice when many servers share one database; only the URL and a driver package
change.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Describe a relational database: tables, columns, rows, a primary key and an index, spoken to in SQL.
- Write a SQLModel table model, and keep a separate input model for what clients send.
- Open one session per request with a `yield` dependency, and create tables in a `lifespan` function.
- Save a row (`add`, `commit`, `refresh`), read one (`session.get`), and see the SQL with `echo=True`.

:::photo{src="/lesson-images/fastapi/fa-12-sketch.webp" alt="Sketchnote: A real database. A relational database keeps data in tables of rows. SQLModel makes one class both a model and a table. Flow: the input model, model_validate makes a row, session.add, session.commit saves it, session.refresh reads the id. Remember: The engine knows where the database is; get_session yields one session per request; The lifespan creates the tables at start-up; session.get finds a row by its primary key." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 13: the full set of create, read, update and delete, and searching with SQL.
:::
