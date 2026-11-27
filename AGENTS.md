# Notes for coding agents working on LabBox by Telusko

Read this first, then `REWRITE_LIST.md` (which labs are rewritten, which are next), then `HANDOFF.md` (where the last session stopped, file by file), then `ROADMAP.md` (status: what is done and what is left), `CHANGELOG.md` (what is done, newest first) and
`labbox-v2-upgrade-spec.md` (the full spec). **Every course follows `CONTENT_STANDARD.md`** (the full-standard
list is at its top) **and is built the way `COURSE_PRODUCTION.md` describes** (helpers in `tools/authoring/`). `README.md` explains how to run, test and author labs.

Naming: **LabBox** is the product, **Telusko** the parent company. Write "LabBox by Telusko" in
titles, "LabBox" in product text, "Telusko" for the company (legal pages, copyright). All names and
the contact address (connect@telusko.com) live in `frontend/src/site.ts`. Technical names stay
lowercase `labbox` (CLI, Docker labels and images, browser storage keys, systemd unit).

## The owner's rules (always apply)

1. **Plan first.** For every phase or batch: say which files you will add or change, then wait for an
   explicit OK before building.
2. Build it, run **all old tests plus the new acceptance checks**, then **one commit per step** with a
   clear message, then show what changed and how to try it in the browser, and stop.
3. **Ask before** deleting data, touching AWS, or adding anything that needs a paid API key.
4. Secrets live in `backend/.env` (written by the owner). Never print it, never ask for keys in chat.
   `OPENAI_API_KEY` there is approved for cover art (`labbox cover --generate`, medium quality, 3 candidates per
   lab), notes pages, and (owner, 25 November) lesson work in general: re-running model outputs to check lessons,
   through the lab gateway with a test account. Ask before any other paid API.
5. Golden Rules from spec section 1: extend, do not rewrite; stay backward compatible; keep the
   `@@RESULT` protocol; only add routes; Alembic migrations are additive only (downgrade disabled);
   every phase shippable; security never regresses.
6. **No em dashes anywhere** (code, docs, lab content, commit messages).
7. After each step, update `ROADMAP.md` and add a `CHANGELOG.md` entry.

## Machine

Ubuntu, Docker Engine, Python 3.12, Node 22. `VOLUMES_DIR=/srv/labbox/volumes`, owner uid 1000.
Backend venv: `backend/.venv`. Frontend: `frontend/`. Playwright uses the system Chrome.

## Running and testing

- Backend: `cd backend && .venv/bin/uvicorn app.main:app --port 8000 --workers 4` (4 workers only with `REDIS_URL`; otherwise 1) (restart it after changing any
  `lab.yaml`, lab content, tracks, drills or onboarding; content is loaded at startup).
- Worker (Phase H3): `cd backend && .venv/bin/arq app.worker.WorkerSettings` (images, networks, nightly
  backup to /srv/labbox/backups); `scripts/labbox jobs` shows the last runs.
- Frontend: `cd frontend && npm run dev` (http://localhost:5173).
- Images: `scripts/build_lab_images.sh` (bases first, then every lab).
- VS Code in labs: `scripts/openvscode.sh` once (downloads to /srv/labbox/openvscode). Browser tests
  that drive the classic editor set `localStorage["labbox.editor"] = "classic"` first.
- AI: every alias maps to OpenAI (owner, 23 November: "use open ai" for the tutor; Ollama is stopped to save
  memory). `lab-chat`, `lab-chat-smart` (tutor, design grader) and `ai-chat` are openai/gpt-4o-mini; `lab-embed`
  and `ai-embed` are openai/text-embedding-3-small. Editor ghost-text completion (`lab-code`) is off until the
  owner picks a fill-in-the-middle model. The backend serves the LLM gateway on 9000 at the Docker bridge
  address; the daily budgets stay on. Tests use the `fake` provider (set in conftest). Any other paid model
  needs the owner's approval. `scripts/ollama.sh` still works if local models are wanted again.
- Tests: **full runs use Postgres and Redis, as in production** (owner, 22 November): `cd backend &&
  LABBOX_TEST_DATABASE_URL=... LABBOX_TEST_REDIS_URL=... .venv/bin/pytest` (see README; about 275 tests,
  Docker ones included, about 11 minutes). Plain `.venv/bin/pytest` runs on SQLite and in-memory locks (the
  quick-start mode); run it only when a change touches the database, migrations or the no-Redis fallbacks;
  `.venv/bin/pytest -m "not docker"` for the fast set; `cd frontend && npm run test:e2e` (29 tests,
  needs backend, Vite and Docker running); `scripts/labbox validate --strict` (all labs must pass).
- Last known state: green (27 November, after the Forward Deployed Engineer course: lab valid, test-lab green, 337 backend tests on Postgres and Redis in 30 minutes; 26 November, after the LangGraph lab rewrite: lab valid, test-lab green; after the LangChain4j lab rewrite: lab valid, test-lab green; after the Spring AI lab rewrite: lab valid, test-lab green; after LangChain: lab valid, test-lab green; after the RAG rewrite: 232 fast backend tests, 31 browser tests; the last full Postgres run was 24 November) (284 backend tests on Postgres and
  Redis, about 30 minutes with every lab's test-lab, 27 browser tests on 4 workers, 23 labs valid). Metrics: `curl -s localhost:8000/metrics`.

## How a lab is made

The full recipe, with commands, is `COURSE_PRODUCTION.md`. In short:
`specs/<lab>.yaml` -> `scripts/labbox new-lab --from-spec specs/<lab>.yaml` -> write chapters
(every step about project code names it: `file="..." line="..."`, see CONTENT_STANDARD section 3),
starter, solution and tests -> `scripts/labbox validate <lab> --strict` -> `scripts/labbox test-lab
<lab>` (starter must fail, solution must pass) -> `scripts/labbox cover <lab> --logo <tech>[,<tech>]`
(real logo on brand colours; add a missing logo to `tools/logos/` and `BRANDS` in `tools/logo_cover.py`) -> write `before_you_start` in `lab.yaml` (CONTENT_STANDARD section 7) -> name each course part on its first chapter (`part: ...`, the lines of the lab's skill map) -> add the lab's
chapters to a track in `tracks/` (data only since 22 November; the app no longer shows track maps) -> add the lab to the `test_test_lab`
parametrize list in `backend/tests/test_cli.py`. Templates: python, java, node, go, rust (labs/rust-basics: one Cargo workspace, a crate per chapter),
service-incident, preview-app, ai, system-design. Labs are written one at a time in chat. There are 24 (sixteen at the full
standard, eight short; see the table in `ROADMAP.md`).

## Where we are (keep this current)

- Done: phases A to E and G, 24 labs (Redis is a 13-chapter course; Python from zero is a 19-chapter course rewritten curiosity-first with photos and handwritten notes (22 November); Java from zero is an 18-chapter course rewritten the same way (22 November: Shelf the library app, Maven and JUnit offline in the image); JavaScript from zero was rewritten the same way (22 November: 18 chapters, Mixtape the playlist app, node:test for testing); Go from zero was rewritten the same way (22 November: 18 chapters, Parcel the parcel tracker, go test for testing); Spring Boot is a 31-chapter course, 0 to 30; Redis, SQL from zero and Git without fear were rebuilt to the full standard the same night; Linux on call followed on 23 November, 15 chapters about Tara, a radio telescope observatory; then a new Spring AI course, Atlas the museum guide (Spring Boot 4.2, Spring AI 2.1): complete, 20 chapters, 40 tasks; then LangChain4j, Setu the hill railway's help desk (LangChain4j 1.24): complete, 30 chapters, 60 tasks; then LangChain (Python), Navin a farmers' co-op help desk (LangChain 1.5): complete, 27 chapters, 54 tasks; then LangGraph, Harsh a water board's complaint-to-repair desk (LangGraph 1.2): complete, 24 chapters, 48 tasks; then Rust from zero, Windwatch a wind farm's turbine monitor (Rust 1.100): complete, 28 chapters, 56 tasks; then RAG and vector databases, Fieldbook a wildlife sanctuary's rangers' assistant (fastembed, FAISS, Qdrant local mode): complete, 13 chapters, 26 tasks; then a new course, Forward Deployed Engineer (27 November, built unattended at the owner's request): Claimdesk at Deccan Shield Insurance, 22 chapters, 44 tasks, every model output captured through the gateway), real VS Code in labs (IDE | Lite, no marketplace), GitHub-grey theme, AI-first home page.
- App shape (owner, 22 November): `/labs` is the dashboard (a Continue card in the colour of the lab last opened: a retro
  computer showing the step for coding labs, a tape deck for the rest; the chapter rail, the daily drill, lab cards); a lab card opens `/courses/<lab>` (cover, Continue, the
  lab's skill map as a metro map, every subtopic a link to its lesson step); that opens `/labs/<lab>` (lesson,
  editor, terminal). Level, streak and XP sit in the profile panel (top right) with Exit. The separate Skill maps
  section is gone (`/skills...` and `/tracks/...` redirect). Lab colours: `frontend/src/brand.ts` (`LAB_TONES`).
- Two designs side by side (owner, 24 and 25 November): the current one on `master` (:5173) and "Ukiyo" on branch
  `design/ukiyo` in the worktree `../labs_poc_ukiyo` (:5174, `DESIGN_UKIYO.md`). The owner picked Ukiyo for now
  (25 November) and makes the final call about a week after the deploy; keep both. Until then, a
  frontend change on master needs the same change on the branch. Pictures must be public domain (or licensed).
- Phase F (Docker/Kubernetes in labs via Sysbox) is skipped on this laptop and moves to the AWS server.
- Examples (owner, 22 November): never chai, tea or any drink, never Dabba Express, and nothing that resembles the Chai aur Code
  platform (its themes or its usual tutorial projects). Pick distinctive running projects.
- Positioning: LabBox is marketed as **AI labs** (20 to 25 AI labs); other tracks are additional.
- **`spring-boot-first-api` is the template for every course** (owner, 21 November: "save it as template for rest"): see CONTENT_STANDARD section 0. Rewrite or build every other course to that standard.
- Phase J (admin and funnel) done. Phase H: H1, H2, H3, H5, H6 done; H4's Google and GitHub sign-in done (27 November; the
  session cookie and websocket ticket still to do). The owner's order since 27 November (memory `next-steps-order`): AWS
  deploy (waiting for the owner's budget answer), then the Forward Deployed Engineer course (done 27 November), then every
  course to the full standard, then a pricing page (UI only; done 27 November, `/pricing`, plans without prices). The
  AI courses' intro pages are public (`GET /api/courses/{lab_id}`, AI track only, titles only).
- AI track (later) (`ROADMAP.md` section B.2): two owner decisions first (which model, build
  order), then stage 1. Phase H's plan is in section B.4, also waiting for an OK.
- Pre-launch items (separate origin for /ide and /preview, self-hosted VS Code webview files, a real
  websocket proxy) are listed in `ROADMAP.md` section B.1.

## Gotchas learned the hard way

- Vite sometimes serves a stale module after edits ("export not found" in the page). Kill the
  process on port 5173 (`ss -ltnp | grep :5173`) and restart `npm run dev`.
- Never `pkill -f` with a pattern that also matches your own shell command; it kills your shell.
  Same for `pgrep -f` inside `sh -c`: write the pattern as `[s]erver-main.js` so it cannot match itself.
- Dev Postgres and Redis (`scripts/devdb.sh`) use ports 55432 and 56379: this laptop already runs its
  own Postgres on 5432 and Redis on 6379; leave those alone.
- A browser test that shows a blank lab page with `net::ERR_NETWORK_CHANGED` in its trace is this
  laptop, not the app: Chrome drops downloads when Docker adds a lab network, and the Vite dev server
  serves the editor as about 230 files. Rerun it. The app retries a failed page load, then reloads once.
- Load checks over fixed one-second windows: a run of N seconds touches N + 1 windows, so a correct
  limiter may pass up to limit * (N + 1) / N a second. Base cut-offs on that (see rate-limiter's check.py).
- Admin rights: never leave a test account as admin (`scripts/labbox admin list` must show only `gaurav` after
  tests); the admin browser test revokes in a finally block. The owner's account (id 1) was renamed from asha to
  `gaurav` and made admin at the owner's request (26 November); grant admin to no one else unless the owner asks.
- Check scripts get `LABBOX_CHAPTER` and `LABBOX_TASKS`: big courses test only that chapter (see
  `labs/go-basics/tests/run_checks.sh`). Task ids must be unique across the whole lab.
- Growing a lab: keep every existing chapter id and task id (learner progress hangs on them); new
  starter files reach existing learners through `containers.top_up` (never overwrites).
- Chapter folders appear one chapter at a time (plan A, 27 November): a workspace gets a chapter's top-level starter
  folder (`folder:` or the chapter id) only once the learner reaches it; files outside chapter folders come at once.
  `reveal: all` in lab.yaml shows everything. Plan B (one growing codebase per course) is in ROADMAP B 2b. Mark every
  starter TODO with its task (`# TODO (task <id>): ...`) so each chapter opens its own file.
- Test accounts must never get small ids: a test machine `lab-u1-...` is the owner's machine (`gaurav`,
  id 1, formerly asha). `tests/conftest.py` starts test ids at a random 8-digit number; keep it that way.
- Restarting a multi-worker backend: stop the uvicorn main process (not a worker, it is replaced) and wait
  until port 8000 is free; open terminals make shutdown take a few seconds, sometimes minutes. Use `scripts/restart_backend.sh`: it
  sends a second stop signal (which forces shutdown), starts a fresh backend and prints its start time. It only touches
  the dev backend on port 8000; never stop a `uvicorn app.main:app` by pattern, the live site's backend (:8100) runs the same command.
- Per-user Docker networks: Docker's default pool runs out after about 30 (/16 each); lab networks use
  /28s from `LAB_SUBNET_POOL`.
- `validate` refuses hints that contain a solution line (10+ characters, not in the starter). Reword
  the hint; do not weaken the rule.
- Specs are written back with `yaml.safe_dump`, so hint text is unquoted; match that when editing.
- Tests must not assume a fixed number of labs (use subset checks).
- `copy_workspace` ignores `.git`; live checks cannot see processes inside the workspace.
- Chapter setup runs as root with every capability dropped, so root cannot write the learner's
  files. Setups that build files in `/workspace` (like a git repo) use `setup_user: learner`.
- Git labs: use live checks with `mount_workspace: ro` (fresh checks copy without `.git`).
- Postgres services need small memory tuning (see `postgres-indexing-incident/lab.yaml`, 768m).
- Go images pre-warm `GOCACHE=/opt/gocache`; Spring labs build offline from the Maven repo in `/opt/m2`.
- Spring Boot chapters where the task is to write tests (17, 18) are checked by running the learner's own tests
  twice: on the correct code, then with the planted bug from `tests/<chapter>/bug/` (settings in `own.env`).
  A new Maven dependency must be added to `warm/pom.xml` and the image rebuilt, or the offline build fails.

- Sign-in is Google and GitHub only (owner, 27 November). Browser tests make accounts through the API with
  `e2e/signin.ts` (`PASSWORD_LOGIN=true` in `backend/.env`, development only); never put a username form back.
- Every browser test signs up a fresh account, and the app allows 60 sign-ups per address per hour
  (`SIGNUPS_PER_IP_HOUR`). A busy evening of test runs hits it ("Too many new accounts", tests stuck
  at login or onboarding). For the local dev server only, start uvicorn with `SIGNUPS_PER_IP_HOUR=1000`
  in its environment; never raise the default in code or touch `backend/.env` for this.
- Labs open in Read mode on a first visit (no editor, no machine). Playwright's default `storageState` sets
  `labbox.mode` to "action" so tests that drive the editor work; a test about Read mode clears it (`read-mode.spec.ts`).
- Browser tests clean up after themselves (Playwright global teardown runs `scripts/labbox test-accounts cleanup
  --since-id N`); set `LABBOX_E2E_KEEP=1` to keep a run's machines when looking into a failure.
- Lab limit (owner, 26 November): with a limit on, a fresh account's labs are locked (403 on lessons, machine,
  checks). Browser runs switch it off in global setup and restore it in teardown (`scripts/labbox lab-limit`);
  backend tests set a per-learner `lab_limit` instead and must leave the site's setting as they found it.
- Phones (under 760 px) get a reading mode that starts no machine (`usePhone`); browser tests that
  resize to phone width will find no editor area.
- **The live site runs on this laptop** (owner, 27 November; `deploy/laptop/README.md`): `/srv/labbox/prod`, backend
  :8100, Caddy :8180, Cloudflare Tunnel to `labbox.gauravships.systems`, database `labbox_prod`, Redis db 2,
  `INSTANCE=prod` (machines `lab-prod-u...`). Never point tests, browser tests or `test-accounts cleanup` at it, never
  edit `/srv/labbox/prod` by hand, and never touch `labbox_prod`; use `deploy/laptop/prod ...` (status, logs,
  deploy, rollback, labbox, adduser). Lab images are shared with it: after building an image from unfinished work,
  rebuild it from the live release (`deploy/laptop/prod images <lab>`). Deploys go through GitHub (Actions, Deploy).

## POC deviations still in place (intentional)

`tests/check.py` instead of `test_chapter1.py`; Node 22; `.env` comments on their own lines;
containers run with `init=True`; shells are killed with `pkill -s`; the Java image renames the uid
1000 user to `learner`.
