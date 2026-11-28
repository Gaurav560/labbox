:::step{type=story title="From the shelf to its owner"}
Here is the journey Lostdesk exists for. A cleaner finds a grey laptop bag at Tech Park and the desk logs it. That
evening its owner files a report. The next morning a clerk sees the two match and records a **claim**. Two days later
the owner comes to the desk with ID, collects the bag, and the claim is closed.

Every chapter so far built one piece of that journey. Today you build the last two steps, the claim and the
collection, in an app that uses a database, settings and a guard on every route, and then you learn what changes
when Lostdesk runs for real.

:::mission
Add `POST /claims`, which matches an item to a report in one safe step, and `POST /claims/{claim_id}/collect`, which
records the owner collecting it.
:::
:::

:::step{type=concept title="The capstone app" file="21-capstone/main.py" line="11-68"}
This chapter's `main.py` brings together what the course built:

| Piece | Chapter | In this file |
|---|---|---|
| settings from the environment | 19 | `Settings`: `LOSTDESK_DATABASE_URL`, `LOSTDESK_DESK_KEY` |
| tables with SQLModel | 12, 13 | `Item`, `Report` and the new `Claim` |
| a session per request | 12 | `get_session`, `SessionDep` |
| a guard as a dependency | 11 | `require_desk`, applied to **every** route at once: `FastAPI(dependencies=[...])` |
| status codes and errors | 8 | 201, 404, 409 |

Each thing has a **status** that only moves forward:

| | starts as | after a claim | after collection |
|---|---|---|---|
| item | `held` | `claimed` | `returned` |
| report | `open` | `matched` | `matched` |
| claim | | created, `collected_on` is null | `collected_on` is the date |

A claim points at an item and a report with **foreign keys**, `Field(foreign_key="item.id")`: a column whose value
must be the id of a row in another table. The database itself then guards the link.
:::

:::step{type=concept title="All or nothing: one commit"}
A claim changes three rows: the item becomes `claimed`, the report `matched`, and a new `Claim` row is added. What if
the server stopped after the first change? An item marked claimed with no claim row to explain it.

Databases solve this with **transactions**: changes made in one session are saved together by one `commit`, or not
at all. So the route makes every change first, and commits once:

```python
item.status, report.status = "claimed", "matched"
db_claim = Claim(item_id=item.id, report_id=report.id)
session.add_all([item, report, db_claim])
session.commit()
```

The checks come **before** any change: 404 if the item or report does not exist, 409 if the item is not `held` or the
report not `open`. Check first, then change: the rule from chapter 14 of the JavaScript course and chapter 8 here.
:::

:::step{type=task task=claim_flow title="Your turn: POST /claims" file="21-capstone/main.py" line="94-96"}
Add `POST /claims`, taking a `ClaimIn`:

- an unknown item or report gives 404;
- an item that is not `held`, or a report that is not `open`, gives 409 with a clear `detail`;
- otherwise change both statuses, add a `Claim`, commit once, and give back the claim with status 201.

Every request needs the header `X-Desk-Key: riverside-desk-7`: in `/docs`, every route now shows an `x-desk-key`
field for it (the app-wide guard's parameter), or use curl with `-H`. The solution, after logging an item and a
report:

```text
POST /claims {"item_id": 1, "report_id": 1}   ->  {"collected_on":null,"item_id":1,"id":1,"report_id":1}
the same claim again                         ->  {"detail":"Item 1 is already claimed"}
```

Then press **Check**: it also looks inside the database for the two new statuses.
:::

:::step{type=task task=collect_item title="Your turn: the owner collects" file="21-capstone/main.py" line="99-100"}
Add `POST /claims/{claim_id}/collect`: an unknown claim gives 404; a claim already collected gives 409; otherwise the
item becomes `returned` and `collected_on` becomes today's date (`date.today()`), saved in one commit. The solution:

```text
POST /claims/1/collect  ->  {"collected_on":"2026-11-28","item_id":1,"id":1,"report_id":1}
again                   ->  {"detail":"Claim 1 was collected on 2026-11-28"}
```

Then press **Check**.
:::

:::step{type=concept title="Going live: fastapi run"}
`fastapi dev` is for working: it watches files and restarts, and listens only inside the machine by default. In
production you start Lostdesk with `fastapi run`, which does neither, and can start several **worker** processes so
that more than one CPU core serves requests:

```bash
fastapi run main.py --port 8000 --workers 2
```

We ran the capstone that way, with a brand-new database file, and saw something worth knowing:

```text
 ⚡️ Starting FastAPI in production mode
...
INFO:     Started parent process [2031]
INFO:     Started server process [2033]
INFO:     Started server process [2034]
...
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) table item already exists
...
ERROR:    Application startup failed. Exiting.
...
ERROR:    Child process [2033] failed to start, stopping the parent process.
```

Each worker is a separate copy of Lostdesk, and each ran the lifespan's `create_all` at the same moment. Both saw "no
item table", both tried to create it, one lost the race, and the whole server stopped. Run it again and it starts,
because the tables now exist: a bug that appears only on a fresh database is exactly the kind that reaches
production. The fix is to create or change tables **once, before** the workers start (with migrations, chapter 12's
deep dive), not inside every worker. And with several workers, use a database built for many writers at once, like
PostgreSQL: `LOSTDESK_DATABASE_URL=postgresql://...`, no code change.
:::

:::step{type=concept title="A checklist for real deployments"}
FastAPI's "Deployment" pages walk through these ideas. As a checklist for Lostdesk:

| Concern | What Lostdesk does |
|---|---|
| HTTPS | a proxy in front (a cloud load balancer, Caddy, Nginx) serves HTTPS and passes requests on |
| settings and secrets | environment variables, read by `Settings` (chapter 19); the token secret never in code |
| start-up | `fastapi run`, tables migrated before it starts |
| more traffic | several workers per machine, several machines behind the load balancer |
| shared data | one database for all of them, never files on one machine |
| health | `GET /health` (chapter 2) for the load balancer |
| restarts | a process manager or container platform restarts a crashed server |

Containers are the usual package. FastAPI's "FastAPI in Containers" page builds an image with a few lines like:

```text
FROM python:3.12
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

(LabBox itself runs every lab machine, including this one, as a container.)
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
The server stops right after `item.status = "claimed"`, before `commit`. What is in the database?
:::
- [ ] The item is claimed, with no claim row
- [x] Nothing changed: without a commit, the transaction is thrown away
:::explain
That is why the route changes everything first and commits once: all or nothing.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why did two workers fail on a fresh database?
:::
- [ ] fastapi run cannot use SQLite
- [x] Both ran create_all at the same moment, and one tried to create a table the other had just made
:::explain
Each worker is its own process with its own lifespan. Schema changes belong before start-up, run once.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Which command belongs in production?
:::
- [ ] `fastapi dev main.py`
- [x] `fastapi run main.py`
:::explain
`dev` watches files and restarts for you while you work; `run` is the steady production server.
:::
:::

:::step{type=deep-dive title="Where to go from here"}
You know the FastAPI that real services are made of. Next steps, in LabBox and beyond:

- **LabBox's Forward Deployed Engineer course** builds Claimdesk, an insurance claims assistant, on FastAPI, with an
  AI model behind it: everything from this course, used on a real-world kind of job.
- **FastAPI's Advanced User Guide** covers what this course left out: WebSockets, custom responses, OpenAPI
  callbacks, sub-applications.
- **Alembic** for migrations, and **PostgreSQL** (LabBox's SQL course) for a database many servers share.

And the shelf of umbrellas from chapter 1? Every one of them now has a way home.
:::

:::step{type=recap title="Course complete"}
You can now:

- Build a FastAPI service from the first route to a tested, secured, documented API with a real database.
- Design a flow with statuses that move forward, checks before changes, and one commit for related changes.
- Run it in production with `fastapi run` and workers, and explain why schema changes happen before start-up.
- Plan a deployment: HTTPS, settings from the environment, a shared database, health checks and containers.

:::photo{src="/lesson-images/fastapi/fa-21-sketch.webp" alt="Sketchnote: Capstone: claims, and going live. Check first, then make every change and commit once: all or nothing. In production, fastapi run with workers. Flow: item held, claim: item claimed, report matched, one commit, owner collects, item returned. Remember: A foreign key links a claim to its item and report; Without a commit, nothing is saved; Create tables once, before the workers start; HTTPS, settings and a shared database for production." ai="true"}
One page of notes for this chapter.
:::

That is FastAPI, all twenty-one chapters. Lostdesk began as two routes over a dictionary; it ends as a service that
follows a lost bag all the way home. Well done.
:::
