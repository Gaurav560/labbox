# Notes for coding agents working on LabBox by Telusko

Read this first, then `ROADMAP.md` (status: what is done and what is left), `CHANGELOG.md` (what is done, newest first) and
`labbox-v2-upgrade-spec.md` (the full spec). `README.md` explains how to run, test and author labs.

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
   `OPENAI_API_KEY` there is approved **only** for cover art (`labbox cover --generate`, medium quality,
   3 candidates per lab). Ask before using it for anything else (for example the Phase E gateway).
5. Golden Rules from spec section 1: extend, do not rewrite; stay backward compatible; keep the
   `@@RESULT` protocol; only add routes; Alembic migrations are additive only (downgrade disabled);
   every phase shippable; security never regresses.
6. **No em dashes anywhere** (code, docs, lab content, commit messages).
7. After each step, update `ROADMAP.md` and add a `CHANGELOG.md` entry.

## Machine

Ubuntu, Docker Engine, Python 3.12, Node 22. `VOLUMES_DIR=/srv/labbox/volumes`, owner uid 1000.
Backend venv: `backend/.venv`. Frontend: `frontend/`. Playwright uses the system Chrome.

## Running and testing

- Backend: `cd backend && .venv/bin/uvicorn app.main:app --port 8000` (restart it after changing any
  `lab.yaml`, lab content, tracks, drills or onboarding; content is loaded at startup).
- Frontend: `cd frontend && npm run dev` (http://localhost:5173).
- Images: `scripts/build_lab_images.sh` (bases first, then every lab).
- VS Code in labs: `scripts/openvscode.sh` once (downloads to /srv/labbox/openvscode). Browser tests
  that drive the classic editor set `localStorage["labbox.editor"] = "classic"` first.
- AI: `scripts/ollama.sh` once (Ollama in Docker, free local models). The backend serves the LLM
  gateway on 9000 at the Docker bridge address. Tests use the `fake` provider (set in conftest).
  Mapping an alias to a paid provider (`LLM_MODELS`) needs the owner's approval.
- Tests: `cd backend && .venv/bin/pytest` (about 216 tests, Docker ones included, about 2 minutes);
  `.venv/bin/pytest -m "not docker"` for the fast set; `cd frontend && npm run test:e2e` (14 tests,
  needs backend, Vite and Docker running); `scripts/labbox validate --strict` (all labs must pass).
- Last known state: everything green (19 November, after the task stepper and chapter focus) (216 backend tests, 14 browser tests, 16 labs valid).

## How a lab is made

`specs/<lab>.yaml` -> `scripts/labbox new-lab --from-spec specs/<lab>.yaml` -> write chapters,
starter, solution and tests -> `scripts/labbox validate <lab> --strict` -> `scripts/labbox test-lab
<lab>` (starter must fail, solution must pass) -> `scripts/labbox cover <lab> --logo <tech>[,<tech>]`
(real logo on brand colours; add a missing logo to `tools/logos/` and `BRANDS` in `tools/logo_cover.py`) -> add the lab's chapters to a skill map in `tracks/` -> add the lab to the `test_test_lab`
parametrize list in `backend/tests/test_cli.py`. Templates: python, java, node, go,
service-incident, preview-app, ai, system-design. Labs are written one at a time in chat. There are 16; the owner
said about 15 is enough for now, so the platform phases come next.

## Where we are (keep this current)

- Done: phases A to E and G, 16 labs (Redis is a 13-chapter course), real VS Code in labs (IDE | Lite, no marketplace), GitHub-grey theme, AI-first home page.
- Phase F (Docker/Kubernetes in labs via Sysbox) is skipped on this laptop and moves to the AWS server.
- Positioning: LabBox is marketed as **AI labs** (20 to 25 AI labs); other tracks are additional.
- `redis-in-practice` is the content standard for flagship labs (13 chapters, zero to senior).
- **Next: the AI track** (`ROADMAP.md` section B.2): two owner decisions first (which model, build
  order), then stage 1. Phase H's plan is in section B.4, also waiting for an OK.
- Pre-launch items (separate origin for /ide and /preview, self-hosted VS Code webview files, a real
  websocket proxy) are listed in `ROADMAP.md` section B.1.

## Gotchas learned the hard way

- Vite sometimes serves a stale module after edits ("export not found" in the page). Kill the
  process on port 5173 (`ss -ltnp | grep :5173`) and restart `npm run dev`.
- Never `pkill -f` with a pattern that also matches your own shell command; it kills your shell.
  Same for `pgrep -f` inside `sh -c`: write the pattern as `[s]erver-main.js` so it cannot match itself.
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

## POC deviations still in place (intentional)

`tests/check.py` instead of `test_chapter1.py`; Node 22; `.env` comments on their own lines;
containers run with `init=True`; shells are killed with `pkill -s`; the Java image renames the uid
1000 user to `learner`.
