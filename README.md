# LabBox POC

LabBox is a small "hands-on coding labs" platform. Each user gets their own Docker container per lab,
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
   └─ SQLite (users, workspaces, check runs)
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
| `DATABASE_URL` | SQLite file (default `backend/data/labbox.db`). |
| `CONTAINER_RUNTIME` | Empty for runc; `runsc` for gVisor. |
| `IDLE_STOP_MINUTES` / `REAPER_INTERVAL_SECONDS` | Idle reaper timing. |
| `MAX_FILE_BYTES` | Max file size for the editor API. |
| `CORS_ORIGINS` | Comma-separated origins. |
| `ALLOW_SIGNUP` | `true` or `false`. |

Keep comments in `.env` on their own lines: systemd's `EnvironmentFile` does not strip inline comments.

## 2. How to add a new lab

The quick way is the authoring CLI (`scripts/labbox`, it uses the backend's virtualenv):

```bash
scripts/labbox new-lab my-lab --track languages --template python   # or --template java
scripts/labbox validate my-lab            # schema, steps, 3 hints per task, no em dashes, solution/, image built
scripts/labbox test-lab my-lab            # builds the image; starter must FAIL every task, solution must PASS
scripts/labbox preview my-lab             # prints a dev login (fresh password each run) and opens the browser
```

`validate` with no lab id checks every lab; add `--no-docker` to skip the image check. Both `validate` and
`test-lab` exit non-zero on problems, so they can run in CI. Templates for node, go, multi-service,
incident, ai and system-design arrive with the phases that build their engines.

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

### `lab.yaml` v2 fields

All optional; a v1 `lab.yaml` keeps working. `version: 2`, `subtitle`, `track` (`languages`,
`frameworks`, `databases`, `devops`, `system-design`, `ai`, `interview`; default `languages`), `tags`,
`level` (`beginner`, `intermediate`, `advanced`), `estimated_minutes`, `free_chapters` (default 2),
`prerequisites` (lab ids, a recommendation only), `story` (`company`, `character: {name, role}`,
`pitch`), and per chapter `minutes`. Tasks take `xp` (default 20) and `hints`.

Fields whose engine is not built yet are refused at start-up with a message naming the phase that adds
them, so a lab never silently loses a feature: `services`, `preview`, `workspace.network: lab`,
`check.mode: live`, chapter `setup` and resource tiers (Phase D), `llm` (Phase E), `runtime` and
`workspace.sudo` (Phase F), `resources.disk_mb` (Phase H).

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
- Every route takes the user id from the JWT only. The terminal WebSocket requires a valid JWT.
- The file API rejects absolute paths, `..` escapes and symlinks that leave the workspace.
  Delete and rename act on a symlink itself, never on its target.
- On EC2: gVisor (`CONTAINER_RUNTIME=runsc`) and the metadata-service block.
- The backend talks to Docker, which is root-equivalent: keep the host for LabBox only.

## 6. Known POC limits

- Single host. Containers, the check lock and the reaper all live on one machine and in one process
  (run uvicorn with **one worker**).
- In-memory locks: "one check per user" is per process.
- No per-user disk quota on workspaces (Check refuses workspaces over 20 MB).
- SQLite: fine for a POC, not for many concurrent writers.
- An open editor tab does not notice when the same file is changed from the terminal. Reopen the file
  to see the new content.
- A determined user can still fake a passing check from inside their own process (for example by
  printing a `@@RESULT` line and exiting before the real checks run). Graders that must be
  tamper-proof should run user code in a separate process from the reporter.
