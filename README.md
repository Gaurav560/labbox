# LabBox by Telusko

LabBox (a product of Telusko) is a "hands-on coding labs" platform. Each user gets their own Docker container per lab,
with a Monaco editor, a real terminal (xterm.js) and a Check button that grades their code with hidden
tests in a fresh, network-less container. Lessons are shown one step at a time (story, concept, predict,
try, task, recap), with a hint ladder per task. Learners earn XP, keep a daily streak, climb levels,
answer a daily drill and watch a skill map light up. See `CHANGELOG.md` for what changed in each phase.

```
Browser (React: Monaco + xterm)
   │  HTTP /api        │  WebSocket /ws/terminal
   ▼                   ▼
FastAPI backend ── docker-py ──► Docker (+ gVisor)
   │                              ├─ lab-u1-python-basics  (/workspace = host volume)
   │                              ├─ lab-u2-java-basics
   │                              └─ check-u1-...          (temporary, no network)
   └─ Postgres, or SQLite for a quick start (users, workspaces, check runs)
```

- One container per **user + lab**: `lab-u{user_id}-{lab_id}`. Files live on the host in
  `VOLUMES_DIR/u{user_id}/{lab_id}` and are bind-mounted at `/workspace`, so they survive container
  stops, restarts and recreation.
- Idle containers are stopped by a background reaper and started again when the user comes back.
- Check copies the workspace and the lab's hidden `tests/` into a throwaway container
  (`network_mode=none`, tests mounted read-only), runs the lab's check command and parses
  `@@RESULT` lines.

## 1. Local development

### Prerequisites

- **Linux:** Docker Engine. **Mac/Windows:** Docker Desktop.
  **Windows:** run the backend inside WSL2 so host volume paths and `chown` work.
- Python 3.12
- Node 22 (Node 20 also works)
- Your user can run `docker` without sudo.

### Run it

```bash
# 1. Build the lab images (once, and again after changing a lab's Dockerfile)
bash scripts/build_lab_images.sh

# 2. Folders for user files and check runs (Linux; any folder you own works, set it in .env)
sudo mkdir -p /srv/labbox/volumes /srv/labbox/checks && sudo chown -R "$USER" /srv/labbox

# 3. Backend
cd backend
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # then set JWT_SECRET to a long random string
.venv/bin/uvicorn app.main:app --reload     # http://localhost:8000

# 4. Frontend (second terminal)
cd frontend
npm ci
npm run dev                     # http://localhost:5173
```

Open http://localhost:5173 for the public home page, then **Start free** to sign up. Vite proxies `/api`
and `/ws` to the backend. The only routes that work without logging in are sign up, log in, health and
`GET /api/catalog` (lab titles and catalog fields for the home page, never chapters, tests, hints or
solutions).

`scripts/create_user.py <username> [password]` creates a user from the command line (useful when
`ALLOW_SIGNUP=false`).

### Tests

```bash
cd backend
.venv/bin/pytest -m "not docker"   # fast: path safety, lab.yaml, lesson steps, migrations, progress API
.venv/bin/pytest -m docker         # end to end: needs Docker running and the lab images built

cd frontend
npm run test:e2e                   # browser flow in your installed Chrome; needs the backend, Vite and Docker running
```

The browser tests sign up fresh users. One walks a lab with the keyboard, answers a predict, reveals a
hint, passes Check and checks that step, panel sizes and theme survive a reload. The other goes through
onboarding into a lab, solves the daily drill and completes a chapter to light up the skill map. They
remove the containers they created when they finish.

### Postgres (Phase H1)

SQLite works for a quick start; Postgres is the real database (many learners writing at once).

```bash
scripts/devdb.sh              # LabBox's own Postgres 16 and Redis 7 in Docker, localhost ports 55432 and 56379
scripts/devdb.sh url          # the DATABASE_URL and REDIS_URL lines for backend/.env
```

Moving existing data from SQLite: stop the backend, copy, put `DATABASE_URL` in `backend/.env`, start
the backend. The copy only reads the SQLite file (it stays as a backup), refuses a target that already
has rows, and compares row counts per table:

```bash
LABBOX_COPY_TO="<the DATABASE_URL>" scripts/labbox db-copy
```

The tests run on SQLite. The same suite on Postgres, in a database whose name ends in `_test` (it is
emptied first):

```bash
docker exec labbox-postgres psql -U labbox -c "CREATE DATABASE labbox_test"
LABBOX_TEST_DATABASE_URL="postgresql+psycopg://labbox:<password>@127.0.0.1:55432/labbox_test" .venv/bin/pytest
```

### Redis: several workers (Phase H2)

With `REDIS_URL` in `backend/.env` (from `scripts/devdb.sh url`), the workers share what used to live
in one process (`app/shared.py`): the lock on each lab machine (start, stop, reset, chapter setup,
first copy of the starter files), the one-check-per-learner slot, the AI requests-per-minute counters
and the reaper (only the worker holding its lease reaps; another takes over within three rounds if it
dies). Every worker also serves the AI gateway on the same port. Then:

```bash
.venv/bin/uvicorn app.main:app --port 8000 --workers 4
```

Without `REDIS_URL` it all stays in memory, exactly as before: run one worker. Tests run in memory;
`LABBOX_TEST_REDIS_URL=redis://127.0.0.1:56379/15` runs them on Redis (a database other than 0, emptied
first).

### Background worker (Phase H3)

A second process next to the backend runs scheduled jobs (`app/jobs.py`, scheduled by arq in
`app/worker.py`; needs `REDIS_URL`):

| Job | When (UTC) | What |
|---|---|---|
| images | at start, daily 03:00 | every image the labs use is on this machine; public ones (postgres:16, redis:7.4, nginx, socat) are pulled if missing, lab images are reported if not built |
| networks | at start, hourly at :15 | removes lab networks no container of that lab group uses (running or stopped) and older than an hour |
| backup | daily at `BACKUP_HOUR_UTC` (21:00, 02:30 in India) | `pg_dump` (in a `postgres:<server version>` container) to `BACKUP_DIR` (`/srv/labbox/backups`, only the owner can read it), checked with `pg_restore --list`; the newest `BACKUP_KEEP` (14) kept. SQLite: a checked copy of the file |

```bash
cd backend && .venv/bin/arq app.worker.WorkerSettings   # the worker (deploy/labbox-worker.service on a server)
scripts/labbox jobs                                     # when each job last ran, and how it went
scripts/labbox jobs --run backup                        # run one now (images, networks or backup)
```

Restoring a backup into a new database:

```bash
docker exec labbox-postgres psql -U labbox -c "CREATE DATABASE labbox_restored"
PGPASSWORD=... docker run --rm -i --network host -e PGPASSWORD postgres:16 \
  pg_restore --no-owner -h 127.0.0.1 -p 55432 -U labbox -d labbox_restored < /srv/labbox/backups/labbox-<time>.dump
```

### Safety limits (Phase H5)

`app/limits.py`; every limit is a setting in `backend/.env` (0 turns it off):

| Setting | Default | What happens |
|---|---|---|
| `DISK_QUOTA_MB` | 500 | A learner's own files, all labs together. Over it: the machine stops, starting and saving are refused (deleting files and Reset lab still work). Lab databases do not count here. |
| `SERVICE_DATA_MAX_MB` | 1024 | One lab's databases (seeded data included). Over it: the machine stops; Reset lab starts fresh. |
| `MAX_RUNNING_LABS` | 2 | Per learner. Starting a third stops the least recently used one. |
| `SESSION_HOURS` | 4 | A machine running this long stops; start it again to continue. |
| `CPU_STUCK_MINUTES` | 10 | A machine using all its CPU this long (an endless loop) stops. |
| `SIGNUPS_PER_IP_HOUR` | 60 | New accounts per address (a classroom shares one). |
| `LOGIN_FAILS_PER_IP_MINUTE`, `LOGIN_FAILS_PER_USER_MINUTE` | 30, 10 | Wrong passwords only; logging in often is never slowed down. |
| `CHECKS_PER_IP_MINUTE` | 120 | Checks per address (one per learner at a time already). |

The reaper's round (every minute, one worker) checks running machines. A machine stopped by a limit
keeps its files, and the lab page shows why it stopped, with a Start button.

### Operations: metrics, logs, errors (Phase H6)

- **Metrics:** `GET /metrics` in Prometheus' text format, only for the machine itself or with
  `Authorization: Bearer <METRICS_TOKEN>` (nginx never passes it on). Counters live in Redis, so all
  workers add up: requests by route and status, response times, checks by result and time, logins,
  sign-ups, rate limits hit, machines stopped by reason (idle, room, session, cpu, disk, database), AI
  requests. Read when asked: machines running, learners active (15 minutes, 24 hours), accounts, and
  each background job's last run.
- **Dashboard:** `deploy/monitoring/prometheus.yml` (scrape config) and
  `deploy/monitoring/grafana-labbox.json` (import into Grafana: 12 panels, including hours since the last
  good backup).
- **Logs:** every request gets an id (`X-Request-ID`, kept from a proxy or made new), returned in the
  response and added to every log line. `LOG_FORMAT=json` writes one JSON object a line. Failed (5xx) and
  slow (over 2 s) requests are logged as warnings.
- **Health:** `GET /api/health` reports Docker, the database and shared state separately.
- **Errors:** `SENTRY_DSN` turns on Sentry error reports (no cookies, headers, bodies or addresses are
  sent). Without it nothing is sent anywhere. Turning it on means a third party receives error reports,
  so the Privacy policy needs a line first.
- **CI:** `.github/workflows/labs.yml` also runs the fast tests on Postgres 16 and Redis 7.4.

```bash
curl -s localhost:8000/metrics | grep -v '^#' | head      # on the server
```

### Admin and funnel analytics (Phase J)

`/admin` is for accounts with admin rights; everyone else gets 403 from `/api/admin/*` (the page sends
them back to /labs). Grant and revoke with the CLI:

```bash
scripts/labbox admin grant <username>    # then log in as that account: an Admin link appears on /labs
scripts/labbox admin list
scripts/labbox admin revoke <username>
```

Tabs: **Funnel** (signed up, opened a lab, passed a first check, finished a chapter 1, finished a
chapter 2; 7, 30, 90 days or all), **Labs** (per lab: where learners stopped, time per step, tasks
ranked by confusion), **Learners** (search), **Machines** (running now, Stop and Kill; files are kept),
**AI spend** (per day, model and learner) and **Errors** (the last 200 server errors with request ids).
Most numbers come from the tables LabBox already keeps, so they cover the past; time per step comes
from `analytics_event` "step" rows, recorded from Phase J on.

### Database migrations

The schema is managed with Alembic (`backend/migrations/`). The backend upgrades the database by itself
at start-up; a POC database (made before migrations existed) is recognised and stamped first, so no data
is touched. Migrations only ever add tables or columns, and downgrades are disabled on purpose.

```bash
cd backend
.venv/bin/alembic revision --autogenerate -m "add something"   # after changing app/models.py
```

`tests/test_migrations.py` fails if a model changes without a matching migration.

### Configuration (`backend/.env`)

| Key | Meaning |
|---|---|
| `JWT_SECRET` | Required, at least 16 characters. Never commit it. |
| `JWT_EXPIRE_MINUTES` | Login lifetime (default 720). |
| `LABS_DIR` | Folder with lab definitions (relative paths are relative to `backend/`). |
| `VOLUMES_DIR` | Host folder for user files. |
| `CHECKS_DIR` | Host folder for temporary check copies (default `/srv/labbox/checks`). |
| `DATABASE_URL` | Postgres (`postgresql+psycopg://...`, see "Postgres" below) or a SQLite file (default `backend/data/labbox.db`). |
| `CONTAINER_RUNTIME` | Empty for runc; `runsc` for gVisor. |
| `IDLE_STOP_MINUTES` / `REAPER_INTERVAL_SECONDS` | Idle reaper timing. |
| `MAX_FILE_BYTES` | Max file size for the editor API. |
| `CORS_ORIGINS` | Comma-separated origins. |
| `ALLOW_SIGNUP` | `true` or `false`. |
| `LLM_MODELS` | Model aliases for the LLM gateway: `alias=provider/model,...` (default: local Ollama). |
| `OLLAMA_URL` | Where Ollama answers (default `http://127.0.0.1:11434`, started by `scripts/ollama.sh`). |
| `LLM_DAILY_TOKENS` / `LLM_RPM` / `LLM_MAX_TOKENS` | Per-user AI budget: tokens a day, requests a minute, reply cap. |
| `LLM_GATEWAY_PORT` / `LLM_GATEWAY_HOST` | Gateway port (9000); host defaults to the Docker bridge address. |

Keep comments in `.env` on their own lines: systemd's `EnvironmentFile` does not strip inline comments.

## 2. How to add a new lab

The quick way is the authoring CLI (`scripts/labbox`, it uses the backend's virtualenv):

```bash
scripts/labbox new-lab my-lab --track languages --template python   # or --template java
scripts/labbox validate my-lab            # schema, steps, 3 hints per task, no em dashes, solution/, image built
scripts/labbox test-lab my-lab            # builds the image; starter must FAIL every task, solution must PASS
scripts/labbox preview my-lab             # prints a dev login (fresh password each run) and opens the browser
```

`validate` with no lab id checks every lab; add `--no-docker` to skip the image check, and `--strict` to
turn every warning into an error (CI does). Besides the schema it checks the content standard: a story
first, a predict and a recap in every chapter, concept steps under 120 words, chapters of 10 to 20 minutes,
a cover, no `TODO(author)` left, and that no hint contains a line of the solution.

Templates: `python`, `java`, `node`, `go` (code exercises), `service-incident` (Postgres service, injected
failure, live check) and `preview-app` (FastAPI in the Preview tab). `ai` and `system-design` arrive with
Phases E and G.

**Writing labs at scale.** Describe a lab in a spec (`specs/README.md` has the format: story, chapters,
tasks, hints, cover scene), then `scripts/labbox new-lab --from-spec specs/<lab>.yaml`. It creates the lab
from its template with a chapter skeleton per chapter and an `AUTHORING.md` checklist. The lab is done
when `validate --strict` and `test-lab` pass and it has a cover.

**CI** (`.github/workflows/labs.yml`): backend tests and `validate --strict` on every push, the frontend
build, and `scripts/ci_changed_labs.sh`, which builds the base images and runs `test-lab` on every lab
that changed (all labs when images, templates or the checker change).

Every lab has a `solution/` folder with working code. It is used only by `test-lab`: it is never copied
into a workspace, never served by any route, and `.dockerignore` keeps it (and `tests/`) out of images.

By hand:

1. Copy a lab folder: `cp -r labs/python-basics labs/my-lab`.
2. Edit `labs/my-lab/lab.yaml`:
   - `id` must equal the folder name (lowercase, digits and dashes).
   - Set a new `image` tag, e.g. `labbox/my-lab:v1`.
   - List chapters and tasks. Task ids must be unique within the lab (`a-z`, `0-9`, `_`).
3. Write the `Dockerfile`. The container must work as **uid 1000** and keep running with
   `sleep infinity`. Install everything the checks need: check containers have **no network**.
4. Put starter files in `starter/` (copied once into each new workspace) and chapter text in
   `chapters/*.md` (format below).
5. Put hidden tests in `tests/`. The check command (usually `bash /check/tests/run_checks.sh`) runs
   with the user's files copied to `/check/workspace` (the working dir) and `tests/` mounted read-only
   at `/check/tests`. It must print one line per task:

   ```
   @@RESULT {"task": "greet", "passed": true, "message": "ok"}
   ```

   Missing tasks count as failed. Messages should describe what went wrong without revealing the
   solution. Catch errors per task so one broken file does not hide the other results.
   Optional extra fields `expected` and `actual` are shown side by side in the results drawer:

   ```
   @@RESULT {"task": "greet", "passed": false, "message": "greet('Asha') returned None",
             "expected": "'Hello, Asha!'", "actual": "None"}
   ```
6. Give each task up to 3 `hints` (a nudge, a direction, then almost there, never the full solution)
   and optionally `xp` (default 20). Each revealed hint lowers the task's XP to 80%, 60%, then 40%.

   ```yaml
   tasks:
     - id: greet
       title: "greet.py: return a greeting"
       xp: 20
       hints:
         - "Look at the last line of greet.py."
         - "An f-string puts a variable inside text."
         - "Return an f-string with name between the two pieces of text."
   ```
7. `bash scripts/build_lab_images.sh`, then restart the backend. An invalid `lab.yaml` or chapter stops
   the backend at start-up with a clear error.

### Chapter format (steps)

A chapter is a list of steps. Each step is one card on screen; the learner moves with Continue / Back,
the arrow keys, or the dots. A chapter with no `:::step` markers still works and is shown as one step.

```markdown
:::step{type=story title="Lunch orders at Dabba Express"}
:::character{name="Priya" role="Founder"}
Every morning we deliver 300 tiffins across Pune.
:::
:::mission
Write three small Python functions before the lunch rush.
:::
:::

:::step{type=predict}
:::question
What does a function without `return` give back?
:::
- [ ] `0`
- [x] `None`
:::explain
Without `return`, Python gives back `None`.
:::
:::

:::step{type=try}
```bash run
python3 -c "from greet import greet; print(greet('Asha'))"
```
:::

:::step{type=task task=greet title="Greet a customer"}
Make `greet(name)` return `"Hello, <name>!"`.
:::

:::step{type=recap}
- `def` defines a function; `return` sends a value back.
:::
```

- Step types: `story`, `concept`, `example`, `predict`, `try`, `task`, `incident`, `recap`, `deep-dive`.
  `task` and `incident` steps need `task=<task id>` (a task of that chapter); `incident` can take `minutes=15`
  for a (cosmetic) countdown.
- Directives inside steps: `character{name role}`, `mission`, `tip`, `warning`, `why`, `mistake`,
  `deep-dive`, `incident{minutes}`. Close each with `:::`.
- A code fence with `run` (` ```bash run `) gets a **Run in terminal** button. It pastes the command
  without pressing Enter.
- A predict step needs a `:::question`, at least 2 options and exactly one `- [x]`. The right answer
  and the `:::explain` text stay on the server: the browser gets them only after a correct answer
  (`POST /api/labs/{lab}/chapters/{ch}/predict`), and the raw markdown it receives has them removed.

### Design review steps (system design labs)

A `design` step asks 1 to 5 short written questions. Each `:::ask{id=...}` is a question; the rest of
the step is its intro. The rubric stays hidden in `tests/rubric.yaml`, keyed by chapter and question:

```markdown
:::step{type=design title="Design review"}
Answer in a few sentences.

:::ask{id=redis_down}
What happens to your limiter if Redis goes down?
:::
:::
```

```yaml
02-global-limit:
  redis_down:
    - id: behaviour
      points: 2
      look_for: Says whether requests are allowed or blocked when Redis is down, and why.
```

The tutor model (`lab-chat-smart`) grades each answer against its criteria and returns a score and a
sentence of feedback per criterion; scores are clamped to the rubric. Every attempt is stored
(`design_answer`). +30 XP the first time an attempt reaches half the points; it never blocks finishing
the chapter. `labbox validate` refuses a design question without criteria.

### `lab.yaml` v2 fields

All optional; a v1 `lab.yaml` keeps working. `version: 2`, `subtitle`, `track` (`languages`,
`frameworks`, `databases`, `devops`, `system-design`, `ai`, `interview`; default `languages`), `tags`,
`level` (`beginner`, `intermediate`, `advanced`), `estimated_minutes`, `free_chapters` (default 2),
`prerequisites` (lab ids, a recommendation only), `story` (`company`, `character: {name, role}`,
`pitch`), `cover` (an image in the lab folder: svg, png, jpg or webp, up to 512 KB), and per chapter
`minutes`. Tasks take `xp` (default 20) and `hints`.

Covers show the real technology logos on their brand colours (Redis red, Python blue, Spring green),
built as one small SVG from devicon's original logos (MIT, `tools/logos/`). Main logo first, an
optional second one becomes a badge. Free, no API key:

```bash
scripts/labbox cover fastapi-first-api --logo fastapi,python   # writes cover.svg and the credit
```

To add a technology, copy its devicon `*-original.svg` into `tools/logos/` and its colours into
`BRANDS` in `tools/logo_cover.py`. Logos are trademarks of their owners, used only to say what a lab
teaches.

AI cover art (no longer the default) uses OpenAI (`OPENAI_API_KEY` in `backend/.env`, `gpt-image-2`, about $0.041 per image at
medium quality, $0.165 at `--quality high`) or Gemini (`GEMINI_API_KEY`), in one house style
(neon isometric dioramas, colours per track). Each lab describes its scene in one line:

```yaml
cover_scene: "Ravi's Tapri: a tiny roadside coffee stall at night, a big brass kettle steaming..."
```

```bash
scripts/labbox cover fastapi-first-api --generate   # 3 candidates in tools/.covers/
scripts/labbox cover fastapi-first-api --pick 2     # saves cover.webp (1200 px, under 480 KB)
```

Stock photo covers come from Pexels (free for commercial use; put a free `PEXELS_API_KEY` in
`backend/.env`):

```bash
scripts/labbox cover fastapi-first-api --query "coffee stall india"   # downloads 6 candidates to tools/.covers/
scripts/labbox cover fastapi-first-api --pick 3                     # saves cover.jpg and the credit in lab.yaml
```

The card shows a small "Photo: name / Pexels" credit linking to the photo.

Without a `cover`, the lab card draws one: the track picks the colours and the illustration, and a
pattern seeded from the lab id makes each lab look different. Covers are public
(`GET /api/labs/{lab}/cover`, served with a sandbox CSP so an SVG can never run scripts).

Fields whose engine is not built yet are refused at start-up with a message naming the phase that adds
them, so a lab never silently loses a feature: `llm` (Phase E), `runtime` and `workspace.sudo`
(Phase F), `resources.disk_mb` (Phase H).

### Labs with services, previews, live checks and incidents

`labs/postgres-indexing-incident` shows all of it; `fastapi-first-api` and `spring-boot-first-api` show
previews.

```yaml
resources: s                      # a tier (xs, s, m, l) or cpus / memory / pids_limit
workspace:
  network: lab                    # only the private per-user network (add network_egress: true for internet)
  env: { PGHOST: db, PGPASSWORD: labpass }
services:                         # extra containers, reachable from the workspace by name (db:5432)
  - name: db
    image: postgres:16
    env: { POSTGRES_PASSWORD: labpass }
    resources: { cpus: 1, memory: 768m, pids_limit: 256 }
    data: /var/lib/postgresql/data          # kept across restarts, wiped by Reset lab
    ready: [pg_isready, -h, 127.0.0.1]      # the lab counts as started once this exits 0
preview:
  - { name: "App", port: 8000, path: "/" }  # shown in the Preview tab
check:
  mode: live                      # a checker container inspects the running system
chapters:
  - id: 01-incident
    setup: [bash, /lab/setup/01.sh]         # runs once, as root, when the chapter is first opened
```

- **Services** run as uid 1000 with no capabilities, like the workspace (Postgres and Redis images
  support that). `user: default` keeps the image's own user and only then allows a few `cap_add`
  entries. Service data lives next to the workspace folder (`VOLUMES_DIR/u{id}/{lab}.services/`), never
  inside `/workspace`. Services start before the workspace, stop with it (Stop machine and the idle
  reaper treat the group as one unit), and Reset lab wipes their data.
- **Previews** go through `/preview/{lab}/{port}/{path}` (HTTP and WebSocket). The lab page sets a
  short-lived HttpOnly cookie (SameSite=Strict, path `/preview`) that is only valid for previews, never
  as a login. The URL has no user id: it always reaches the cookie owner's own machine, and only the
  listed ports. Learner apps must listen on `0.0.0.0`. **In production, serve `/preview` from its own
  origin** (for example `preview.labs.example.com`, a second server block in `deploy/nginx.conf` with the
  same `/preview/` location), so JavaScript written by learners cannot reach the main app's storage.
- **Live checks** run in `labbox/checker:v1` (Python with requests, psycopg and redis, plus psql,
  redis-cli and curl) on the learner's lab network, with `tests/` read-only and (only with
  `check.mount_workspace: ro`) the learner's files read-only. No learner code runs in it, so printing a
  fake `@@RESULT` has no effect.
- **Chapter setup** scripts live in the image under `/lab/setup/` (make them unreadable for the learner:
  `chmod -R go-rwx /lab`). `setup_target` runs them in a service instead of the workspace. The time a
  chapter is first opened starts its incident timer: fixing an `incident` step inside `minutes` gives
  +25 XP.
- **`labbox test-lab`** on a live lab starts a throwaway group, runs setup, expects every task to FAIL,
  copies `solution/` in and runs `solution/apply.sh` if there is one, expects every task to PASS, then
  removes everything.

### Base images

`scripts/build_lab_images.sh` builds `images/base` (Ubuntu 24.04, learner uid 1000), then
`images/python` (Python 3.12, pytest), `images/java` (Temurin 21, Maven), `images/checker` and
`images/ai-python` (OpenAI and Anthropic SDKs), then every lab. The base image has the `lab` helper. Lab Dockerfiles start `FROM labbox/python:v1` or `FROM labbox/java:v1` and add a few lines.

### AI labs and the LLM gateway (Phase E)

The backend also serves the LLM gateway on port 9000, bound to the Docker bridge address.
Run `scripts/ollama.sh` once: it starts Ollama in Docker (localhost only) and pulls the free models
behind the default aliases (`lab-chat` = qwen2.5:0.5b, `lab-chat-smart` = qwen2.5:1.5b,
`lab-embed` = nomic-embed-text). To use a paid provider instead, map an alias in `LLM_MODELS`, for
example `lab-chat=openai/gpt-4o-mini` (uses `OPENAI_API_KEY` from `.env`; ask the owner first).

A lab with `llm: {enabled: true}` (template `ai`, image `labbox/ai-python`) gets `OPENAI_BASE_URL`,
`OPENAI_API_KEY` and the `ANTHROPIC_` pair, so the official SDKs work unchanged. The key is a lab
token for that learner and lab; real provider keys never enter a container. `lab requests` inside the
machine shows the last 10 calls (`--last` shows the full request and response). Every call, including
the tutor's, is stored in the `llm_request` table and counts against the learner's daily budget.

AI code completion in the editor (grey ghost text, Tab accepts, "✦ AI on/off" in the editor bar)
uses `lab-code` (qwen2.5-coder, fill in the middle), has its own limits (`LLM_COMPLETION_RPM`,
`LLM_COMPLETION_DAILY_TOKENS`) and never suggests a line of the task's solution. `AI_COMPLETION=false`
turns it off.

The tutor (`✦ Ask the tutor` after a failed check, `✦ Review my code` after a pass) uses
`lab-chat-smart`. A reply that contains a line of the reference solution is replaced by a safe nudge.

AI lab checks stay deterministic: the hidden check gives the learner's code a fake client and grades
the request it builds, not what a model said. For RAG labs, add `pgvector/pgvector` or `qdrant/qdrant`
under `services` (see the commented example in `tools/templates/ai/lab.yaml`).

### VS Code in labs

Run `scripts/openvscode.sh` once: it downloads openvscode-server to `/srv/labbox/openvscode`
(`IDE_DIR`), adds the Python extensions and the `labbox-defaults` settings extension. Every lab
machine gets it mounted read-only at `/opt/openvscode`; the lab page starts it on demand and shows
it through `/ide/{lab}/` (same signed-in proxy as Preview, so in production serve it from its own
origin too). `IDE_ENABLED=false` (or not downloading it) keeps the classic editor. Each machine gets
`IDE_EXTRA_MEMORY_MB` more memory while VS Code is on. Lab networks get a /28 each from
`LAB_SUBNET_POOL` (Docker's default pool runs out after about 30 networks).

### Check output

Besides `@@RESULT`, a check may print `@@METRIC {"name": "p95_ms", "value": 180, "target": 200,
"better": "lower"}`. Metrics are shown in the results drawer (gauges come later).

## 3. XP, streaks, drills, skill maps and onboarding

### Rules

| Earned for | XP |
|---|---|
| A task passing for the first time | the task's `xp` (default 20), lowered by hints: 100%, 80%, 60%, 40% |
| A predict step right on the first try | 10 |
| Completing a chapter (all its tasks pass) | 50 |
| Completing a lab | 200 |
| Solving the daily drill | 20 |

- **Ledger:** every award is a row in `xp_event` with a unique `ref` (for example
  `task:python-basics:greet`), so nothing pays out twice and totals can always be recalculated.
- **Levels:** everyone starts at level 1. Reaching level N needs `round(100 * (N - 1)^1.5)` XP in total:
  level 2 at 100, level 3 at 283, level 4 at 520.
- **Streaks:** a day counts when the learner earns at least 20 XP, using their timezone. The browser
  sends it once, and it can be changed with `PUT /api/me/profile`. Each award stores the local day it
  was earned on, so a later timezone change never rewrites history. Today never breaks a streak. One
  freeze per week (Monday to Sunday) covers a single missed day; two missed days in a row end it.
- **Users from before this phase:** they skip onboarding, and their earlier first passes, completed
  chapters and first-try predicts become XP once, dated when they happened.

### Content files (next to `labs/`)

| Folder | What | Checked by |
|---|---|---|
| `tracks/<track>.yaml` | Skill map: nodes with `requires` and the `chapters` (`lab-id/chapter-id`) that light them up. Nodes without chapters show as "coming soon". | start-up and `labbox validate`: unknown nodes or chapters, loops |
| `drills/<track>.yaml` | Daily drills: multiple choice (`predict`, `bug`, `command`), checked on the server | answer in range, unique ids |
| `onboarding/onboarding.yaml` | The 5 goals (with the track and the lab to start from) and 3 placement questions | each goal starts from an existing lab |

The daily drill is picked per learner and local day from the tracks of the labs they opened plus their goal,
and stays the same for the whole day.

### Routes

`GET /api/me/stats`, `GET` and `PUT /api/me/profile`, `GET /api/drill/today`,
`POST /api/drill/today/answer`, `GET /api/tracks`, `GET /api/tracks/{track}/skills`, `GET` and
`POST /api/onboarding`, `POST /api/onboarding/skip`. Check and predict responses include `xp_awarded`.

## 4. AWS deploy (single EC2 host)

### 4.1 Launch the instance (AWS console)

1. Region **ap-south-1 (Mumbai)**. EC2 > Launch instance.
2. AMI: **Ubuntu Server 24.04 LTS (x86_64)**.
3. Type: **t3.large** for the POC (m6i.xlarge for roughly 30 to 50 concurrent users).
4. Key pair: create one, download the `.pem` (`chmod 400 labbox.pem`).
5. Network: new security group with inbound **22 from My IP only**, **80** and **443** from anywhere.
6. Storage: **40 GB gp3**.
7. Advanced details: **no IAM instance profile**. Metadata version **V2 only**, and metadata
   response hop limit **1** (a second guard so containers cannot reach instance metadata).
8. Launch. Then Elastic IPs > Allocate > Associate with the instance.

### 4.2 Set up the host

```bash
ssh -i labbox.pem ubuntu@<elastic-ip>
git clone <repo> /tmp/labbox-setup && sudo bash /tmp/labbox-setup/deploy/ec2_setup.sh
exit    # log out and back in so the docker group applies
```

`deploy/ec2_setup.sh` installs Docker, gVisor (`runsc`, verified with hello-world), Python 3.12, Node 22,
Nginx and iptables-persistent, blocks containers from `169.254.169.254`, and creates
`/srv/labbox/{volumes,checks}` and `/opt/labbox` owned by `ubuntu`. It is safe to run again.

### 4.3 Install the app

```bash
git clone <repo> /opt/labbox && cd /opt/labbox
bash scripts/build_lab_images.sh
cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # set JWT_SECRET, VOLUMES_DIR=/srv/labbox/volumes, CONTAINER_RUNTIME=runsc, CORS_ORIGINS
cd ../frontend && npm ci && npm run build      # output: frontend/dist
sudo cp ../deploy/labbox.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now labbox
sudo cp ../deploy/nginx.conf /etc/nginx/sites-available/labbox && sudo ln -sf /etc/nginx/sites-available/labbox /etc/nginx/sites-enabled/labbox && sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl reload nginx
```

Check: `curl http://<elastic-ip>/api/health` returns `{"ok":true,"docker":true}`. Logs:
`journalctl -u labbox -f`.

### 4.4 HTTPS (recommended)

Point a domain's A record at the Elastic IP, then:

```bash
sudo apt install -y certbot python3-certbot-nginx && sudo certbot --nginx -d labs.example.com
```

Add `https://labs.example.com` to `CORS_ORIGINS`. The frontend switches to `wss://` by itself.

### 4.5 Cost control

- Stop the instance in the console when you are not testing (you then pay only for storage and the
  Elastic IP).
- Set an AWS Budget alert (for example $20/month) under Billing.

## 5. Security notes

- User and check containers run as uid 1000 with `cap_drop=ALL`, `no-new-privileges`, pids, memory
  (no swap) and CPU limits. Nothing is privileged and the Docker socket is never mounted.
- Check containers have no network and get the tests read-only. Hidden tests and `solution/` are never
  copied into a workspace or an image, or served by the API. Predict answers are checked on the server.
- Service containers get the same limits; lab networks are internal (no internet) unless a lab opts in.
  Live checkers never run learner code. Preview cookies are scoped to previews and to the owner's machine.
- Every route takes the user id from the JWT only. The terminal WebSocket requires a valid JWT.
- The file API rejects absolute paths, `..` escapes and symlinks that leave the workspace.
  Delete and rename act on a symlink itself, never on its target.
- On EC2: gVisor (`CONTAINER_RUNTIME=runsc`) and the metadata-service block.
- The backend talks to Docker, which is root-equivalent: keep the host for LabBox only.

## 6. Known POC limits

- Single host: the lab containers run on the same machine as the backend.
- Without `REDIS_URL`, locks, the one-check-per-learner slot, AI counters and the reaper live in one
  process: run uvicorn with **one worker**. With `REDIS_URL`, several workers are fine (see "Redis").
- Disk quotas are measured, not enforced by the filesystem: a learner can briefly write past the quota
  until the next reaper round (a minute) stops the machine. A server can add hard XFS project quotas.
- SQLite (the default without `DATABASE_URL`): fine for a POC, not for many concurrent writers; use Postgres.
- An open editor tab does not notice when the same file is changed from the terminal. Reopen the file
  to see the new content.
- In `fresh` labs a determined user can still fake a passing check from inside their own process (for
  example by printing a `@@RESULT` line and exiting before the real checks run). `live` labs are not
  affected; graders that must be tamper-proof should use live mode or run user code in a separate
  process from the reporter.
- Previews share the main origin in development (see above for production).
