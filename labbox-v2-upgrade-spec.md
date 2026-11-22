# LabBox v2: From POC to a Real Product

> **How to use this file:** Put it in the root of the existing `labbox-poc` repo, open Claude Code and say:
> "Read `labbox-v2-upgrade-spec.md`. This upgrades the existing POC, it is not a rewrite. Follow the Golden Rules in section 1. Build phase by phase, run each phase's acceptance checks, show me the result, then continue. Ask me before anything that touches AWS, payments in live mode, or deletes data."

---

## 0. The goal in one paragraph

LabBox becomes a paid, hands-on learning platform where people learn **anything technical** (programming languages, frameworks, databases, DevOps, system design, and AI in depth) by **doing**, not watching. Every few minutes the learner reads a little, predicts, tries, fails with a clear reason, and wins. Things break, timers run, stories pull them forward, and their progress is visible. The experience must feel calm and beautiful to read, and impossible to put down.

### What exists today (do not throw away)

- FastAPI backend: auth (JWT), labs loader, per-user-per-lab containers, safe file API, WebSocket terminal, checker in a fresh container, idle reaper, SQLite.
- React + Vite frontend: Login, Labs list, Lab page (chapter markdown, file tree, Monaco, xterm, Check results).
- Two labs: `python-basics`, `java-basics`. 40 passing tests.

### What changes

1. **Lesson experience redesign** (the left panel is cluttered and hard to read).
2. **Content format v2**: chapters made of short steps, with predict questions, hints, stories, XP.
3. **Lab engine upgrades**: multi-service labs (Postgres, Redis, Kafka...), web preview of the learner's app, live state checks, failure injection, Docker and Kubernetes inside labs, AI gateway, load testing for system design.
4. **Engagement layer**: XP, streaks, levels, skill map, daily drill, boss incidents, recap cards.
5. **Real-app hardening**: Postgres, Redis, Google/GitHub login, payments (Razorpay), admin, analytics, backups, abuse controls.
6. **Catalog**: tracks for every domain, with authoring tools so new labs are fast to make.

---

## 1. Golden Rules (minimal-change upgrade)

Claude Code must follow these in every phase:

1. **Extend, do not rewrite.** Keep the existing module layout (`containers.py`, `checker.py`, `terminal.py`, `workspace_files.py`, routers, React pages). Add new modules next to them. Refactor only when a phase explicitly says so.
2. **Backward compatible.** Existing `lab.yaml` files (v1) and chapter `.md` files must keep working with no edits. v2 fields are optional. A chapter without step markers renders as one step.
3. **Same check protocol.** `@@RESULT {...}` stays. New fields are optional additions. Old check scripts keep working.
4. **Same API routes.** Do not rename or remove existing routes. Add new ones under the same prefixes.
5. **Additive database changes only**, through migrations (Alembic). Never drop a column with user data.
6. **Every phase is shippable.** After each phase the app still runs end to end and all old tests pass, plus new tests for the phase.
7. **Security never regresses.** Every rule in the POC security checklist still holds after every phase.
8. **No em dashes** in any code comment, doc, UI copy or lab content.

---

## 2. Lesson experience redesign (Phase A, highest priority)

The current left panel is a long wall of markdown with everything at one size. Learners skim, get lost, and leave. Replace it with **one step at a time**, beautiful typography, and a clear mission.

### 2.1 New lab page layout

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ ← Labs   Java Basics  ›  Ch 1 · Your first methods        ▓▓▓▓▓░░░ 5/8   🔥 4  ⭐ 120 │  top bar
├──────────────────────────────┬─────────────────────────────────────────────────────┤
│  LESSON (step card)          │  Files │ Greeter.java ×                    Saved ✓  │
│                              │        │                                             │
│  ●●●●○○○○  Step 5 of 8       │        │   Monaco editor                             │
│                              │        │                                             │
│  ┌─ 🎯 Mission ────────────┐ │        │                                             │
│  │ Kabir needs greetings   │ │        │                                             │
│  │ for 600 merchants/day.  │ │        │                                             │
│  └─────────────────────────┘ │        │                                             │
│                              ├────────┴─────────────────────────────────────────────┤
│  Methods return values       │  Terminal  │  Preview  │  Output                     │
│                              │  learner@java-basics:/workspace$                     │
│  A method is a named block   │                                                      │
│  that lives inside a class.  │                                                      │
│                              │                                                      │
│  ┌ code ───────── [Copy] ─┐  │                                                      │
│  │ static int square(..)  │  │                                                      │
│  └────────────────────────┘  │                                                      │
│                              │                                                      │
│  💡 Tip  ...                  │                                                      │
│                              │                                                      │
│  [ ← Back ]    [ Continue → ]│                                                      │
├──────────────────────────────┤                                                      │
│ TASKS  ✓ greet  ▶ longest_word│                                                      │
│ [ Check ]   Hint (2 left)    │                                                      │
└──────────────────────────────┴──────────────────────────────────────────────────────┘
```

### 2.2 Step types (each step is a card)

| Type | Purpose | UI |
|---|---|---|
| `story` | Sets the scene: a company, a person, a problem | Character avatar + name + 2 to 4 lines, mission box |
| `concept` | One idea, max ~120 words | Heading + short paragraphs + optional code block |
| `example` | Show working code | Code block with **Copy** and **Run in terminal** buttons |
| `predict` | Learner guesses before seeing | Multiple choice; reveal explanation; +XP if right first time |
| `try` | Small experiment in the terminal or editor | Instruction + command with **Run in terminal** button |
| `task` | Graded work | Task title, goal, acceptance in plain words, hints ladder, links to Check |
| `incident` | Something is broken, timer runs | Red alert card with pager text, countdown, Check |
| `recap` | End of chapter | 3 bullet takeaways, XP earned, streak, "Next chapter" |
| `deep-dive` | Optional extra depth | Collapsed by default: "Go deeper (2 min)" |

Rules:
- One step on screen at a time. **Continue** moves forward; **Back** moves back. Arrow keys work.
- A `task` step does not block Continue (learner can read ahead), but the chapter is only "complete" when all tasks pass.
- Progress dots at the top of the card; clicking a dot jumps to that step.
- The current step is remembered per user (resume exactly where they left).

### 2.3 Typography and visual design tokens

Implement as CSS variables in `styles.css` (dark theme default, light theme available).

```css
:root {
  --font-text: "Inter", system-ui, sans-serif;
  --font-code: "JetBrains Mono", ui-monospace, monospace;

  --text-size: 16px;
  --text-line: 1.7;
  --h1: 26px;   --h2: 20px;   --h3: 17px;
  --measure: 62ch;               /* max line length for lesson text */

  --bg: #0f1115;  --panel: #161922;  --card: #1c2030;
  --text: #e6e8ee; --muted: #9aa3b2; --border: #2a2f3d;
  --accent: #7c9cff; --success: #3ecf8e; --danger: #ff6b6b; --warn: #f5b84b;

  --radius: 12px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px; --space-6: 24px; --space-8: 32px;
}
```

Rules:
- Lesson text max width `var(--measure)`, generous padding (24px), paragraphs separated by 12px.
- Headings bold, never all caps. Body text never smaller than 15px.
- Inline code: subtle background chip, same size as text, no harsh borders.
- Code blocks: rounded card, language label top-left, **Copy** button top-right, horizontal scroll (never wrap).
- Callouts as soft colored cards: `tip` (accent), `warning` (warn), `why` ("Why this matters", success), `mistake` ("Common mistake", danger).
- Load Inter and JetBrains Mono locally (bundle the font files; do not depend on a font CDN at runtime).
- Smooth 150ms transitions between steps. Respect `prefers-reduced-motion`.
- Focus mode: a button that hides the file tree and widens the lesson + editor.
- Panels are resizable and sizes are remembered in localStorage.

### 2.4 Hint ladder

Each task has up to 3 hints:
1. A nudge (what to look at)
2. A direction (what approach)
3. Almost there (a near-complete pointer, never the full solution)

Hints reveal one at a time. Each revealed hint reduces the XP for that task (100% → 80% → 60% → 40%). Show "Hint (2 left)".

### 2.5 Check results redesign

- Results slide up in a bottom drawer: big "3 of 3 passed 🎉" or "1 of 3 passed".
- Each failed task shows: the message, and when available, **Expected vs Got** side by side.
- Confetti (small, tasteful, once) when a chapter is fully passed, then the `recap` card.
- "Ask the tutor" button on failed tasks (Phase E), disabled until then.

### 2.6 Small fixes from the POC

- Terminal shows the bash prompt twice after Start machine. Find the cause (likely an extra newline or a second exec on reconnect) and fix.
- The **Run in terminal** button pastes the command into the terminal and focuses it, but does **not** press Enter. The learner presses Enter (they stay in control).

### Phase A acceptance

- [ ] Existing `python-basics` and `java-basics` chapters still render (as a single step, since they have no markers).
- [ ] Convert both chapters to the v2 step format (section 3.2) and they render as 6 to 9 steps each with at least one `story`, `predict`, `task` and `recap`.
- [ ] Lighthouse accessibility score of the lab page ≥ 90. Text contrast passes WCAG AA.
- [ ] Step position, panel sizes and theme persist across reloads.
- [ ] Playwright test: open lab, step through all steps with the keyboard, answer a predict, reveal a hint, pass Check, see recap.
- [ ] Double prompt bug fixed.

---

## 3. Content format v2

### 3.1 `lab.yaml` v2 (all new fields optional)

```yaml
id: spring-boot-on-fire
version: 2
title: "Spring Boot on fire"
subtitle: "Fix 10 real production incidents in a Spring Boot service"
track: frameworks                 # languages | frameworks | databases | devops | system-design | ai | interview
tags: [java, spring-boot, postgres, redis]
level: intermediate               # beginner | intermediate | advanced
estimated_minutes: 240
free_chapters: 2
prerequisites: [core-java]        # other lab ids (recommendation only, not enforced)
story:
  company: "Tapri Counter"
  character: { name: "Meera", role: "CTO", avatar: "meera.png" }
  pitch: "Tapri Counter's ordering service keeps falling over at lunch rush. You are the new backend engineer."
image: labbox/spring-boot-on-fire:v1
resources: { cpus: 1, memory: 1536m, pids_limit: 512, disk_mb: 1024 }
runtime: default                  # default | gvisor | sysbox  (see section 4.5)
workspace:
  mount_path: /workspace
  shell: /bin/bash
  network: lab                    # none | bridge | lab (private per-user network, see 4.1)
  sudo: false                     # give learner sudo inside the container (DevOps labs)
services:                         # extra containers started with the workspace (section 4.1)
  - name: db
    image: postgres:16
    env: { POSTGRES_PASSWORD: labpass, POSTGRES_DB: tapri }
    resources: { cpus: 0.5, memory: 512m }
  - name: cache
    image: redis:7
preview:                          # expose learner's app in the Preview tab (section 4.2)
  - { name: "App", port: 8080, path: "/" }
llm:                              # AI gateway access (section 6)
  enabled: false
check:
  mode: fresh                     # fresh (POC behaviour) | live (section 4.3)
  command: ["bash", "/check/tests/run_checks.sh"]
  timeout_seconds: 60
  network: none
chapters:
  - id: 01-slow-checkout
    title: "Checkout takes 9 seconds"
    file: chapters/01-slow-checkout.md
    minutes: 15
    setup: ["bash", "/lab/setup/01.sh"]   # optional: runs once when chapter opens (failure injection, 4.4)
    tasks:
      - id: add_index
        title: "Make /checkout respond in under 200 ms"
        xp: 50
        hints:
          - "Look at what the endpoint does on every request."
          - "Run EXPLAIN ANALYZE on the query from the logs."
          - "The orders table is scanned fully. Which column is filtered on?"
```

v1 files keep working: `track` defaults to `languages`, `free_chapters` to 2, `xp` to 20 per task, `check.mode` to `fresh`, `services` to none.

### 3.2 Chapter markdown v2 (steps and directives)

Steps are separated by `:::step` blocks. Use `remark-directive` (frontend) to parse. Backend serves raw markdown plus a parsed JSON outline.

```markdown
:::step{type=story}
:::character{name="Meera" role="CTO"}
Lunch rush starts in 15 minutes. Checkout is taking **9 seconds**. Customers are leaving.
:::
:::mission
Make `/checkout` respond in under 200 ms before lunch.
:::
:::

:::step{type=concept title="Why queries get slow"}
A database finds rows in one of two ways ...

:::tip
`EXPLAIN ANALYZE` shows you the plan Postgres actually used.
:::
:::

:::step{type=predict}
:::question
The `orders` table has 2 million rows and no index on `customer_id`. What does Postgres do for `WHERE customer_id = 42`?
:::
- [ ] Jumps straight to the row
- [x] Reads every row and filters
- [ ] Uses the primary key index
:::explain
Without an index on `customer_id`, the only option is a sequential scan.
:::
:::

:::step{type=try}
Run this and read the plan:
```bash run
psql -h db -U postgres tapri -c "EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;"
```
:::

:::step{type=task task=add_index}
Fix it so `/checkout` responds in under 200 ms. Your fix must survive a restart.
:::

:::step{type=recap}
- Slow endpoints usually hide a slow query.
- `EXPLAIN ANALYZE` tells you what the database really did.
- An index turns a full scan into a direct lookup.
:::
```

Supported directives: `step`, `character`, `mission`, `tip`, `warning`, `why`, `mistake`, `deep-dive`, `question`, `explain`, `incident{minutes=15}`. Code fence attribute `run` adds the **Run in terminal** button.

### 3.3 Check protocol v2 (backward compatible)

```
@@RESULT {"task": "add_index", "passed": false,
          "message": "/checkout took 1840 ms (target 200 ms)",
          "expected": "< 200 ms", "actual": "1840 ms"}
@@METRIC {"name": "p95_ms", "value": 1840, "target": 200, "better": "lower"}
```

- `expected` and `actual` are optional; when present, the UI shows them side by side.
- `@@METRIC` is optional; used by system design and performance labs to draw a small gauge.
- Same anti-cheat rule as POC: if a task is reported more than once, any failure wins.
- New: for `live` mode, results come from the checker container, not from user code (section 4.3), which closes the "print a fake @@RESULT" hole for those labs.

### 3.4 Authoring tools (`labbox` CLI, Python, in `tools/labbox_cli.py`)

- `labbox new-lab <id> --track <track> --template <python|java|node|go|multi-service|incident|ai|system-design>`: scaffolds a lab folder.
- `labbox validate [lab_id]`: schema check, every task referenced in a chapter, every hint present, image exists, chapter files parse, no em dashes in content.
- `labbox test-lab <lab_id>`: builds the image, runs Check against `starter/` (every task must FAIL) and against `solution/` (every task must PASS). Used in CI.
- `labbox preview <lab_id>`: opens the lab locally with a dev user.

Every lab must include a `solution/` folder. It is used **only** by `test-lab` and CI; it is never mounted into user containers, never served by any route.

### Phase B acceptance

- [ ] v1 labs still load and pass their old tests.
- [ ] `labbox validate` and `labbox test-lab` work on both existing labs (add their `solution/` folders).
- [ ] New API: `GET /api/labs/{lab}/chapters/{ch}/outline` returns `{steps: [{type, title, task?}...]}`.
- [ ] Predict answers are checked server side (`POST /api/labs/{lab}/chapters/{ch}/predict`), so the right answer is not in the page source before answering.

---

## 4. Lab engine upgrades

### 4.1 Multi-service labs (per-user private network)

Many real labs need more than one process: app + Postgres + Redis + Kafka, or nginx + 3 app replicas.

Implementation (docker-py, no docker compose):
- On `ensure_workspace`, if the lab has `services` or `network: lab`, create a Docker network `labnet-u{user}-{lab}` (internal by default; attach to egress only if `workspace.network_egress: true`).
- Start each service container `lab-u{user}-{lab}-{service}` on that network with the network alias `{service.name}` (so the learner connects to `db:5432`, `cache:6379`).
- Same security options as the workspace (cap_drop ALL except what an official image strictly needs, no-new-privileges, limits). Postgres and Redis official images need to run as their own user; allow `user: default` per service.
- Service data on a per-user volume folder `{VOLUMES_DIR}/u{user}/{lab}/.services/{service}` so DB data survives restarts.
- Stop and start services together with the workspace. The reaper treats the group as one unit.
- `Reset lab` also resets service data.
- New status API returns each service's state, shown as small dots under the top-bar status.

### 4.2 Web preview (see the learner's running app)

- New route: `/preview/{lab_id}/{port}/{path:path}` (HTTP and WebSocket), authenticated by a short-lived, HttpOnly, SameSite=Strict cookie set when the lab page loads.
- The backend reverse-proxies to the workspace container's IP on that port over the lab network (backend host can reach container IPs on the bridge). Use `httpx.AsyncClient` streaming for HTTP and a websocket pass-through for WS.
- Only ports listed in `preview` are allowed.
- Frontend: a **Preview** tab next to Terminal with an iframe, a URL bar, reload button and "Open in new tab".
- Production: serve previews from a separate origin (`preview.<domain>`) so learner-written JavaScript cannot touch the main app's cookies or localStorage. Document this; in dev, same origin is acceptable.

### 4.3 Live checks (check the real system, not just printed output)

`check.mode: live` is for incidents, DevOps, databases and system design, where the state of the running system matters.

- Start a **checker container** from a dedicated image `labbox/checker:v1` (curl, psql client, redis-cli, kubectl, k6, python3 with requests and pytest).
- Attach it to the user's lab network. Mount the lab's `tests/` read-only. **Do not** mount the user's workspace (unless the lab sets `check.mount_workspace: ro`).
- It inspects the live system: hits endpoints, queries the DB, counts pods, measures latency. It prints `@@RESULT` and `@@METRIC`.
- Since user code never runs inside the checker, user code cannot print fake results.
- Same timeout, cleanup (`try/finally remove`), one-check-at-a-time lock.

`fresh` mode (POC behaviour) stays the default for pure coding labs.

### 4.4 Failure injection (incidents)

- A chapter may define `setup`: a script run **once** when the user first opens that chapter (tracked in DB per user per chapter).
- Runs via `docker exec` as root inside the workspace or a service container (`setup_target: workspace|<service>`), from `/lab/setup/` which is baked into the image (not in `/workspace`).
- Examples: drop an index, fill disk to 95%, break an nginx config, set a wrong env var, start a memory-leaking process, kill a pod repeatedly.
- `incident` steps show a countdown (`minutes=15`). The timer is cosmetic (no penalty except bonus XP for finishing in time) so it stays fun, not stressful.

### 4.5 Docker and Kubernetes inside a lab

Plain containers cannot safely run Docker or Kubernetes inside them. Use **Sysbox** (`sysbox-runc` runtime):
- Labs with `runtime: sysbox` get a container that can run `dockerd`, `kind` or `k3s` inside it, without `--privileged`.
- Images: `labbox/docker-lab:v1` (dockerd inside), `labbox/k8s-lab:v1` (k3s or kind + kubectl + helm).
- Bigger resources (2 CPU, 4 GB) and a longer idle timeout for these labs.
- `runtime: gvisor` remains the default for everything else in production.
- Install script for Sysbox goes into `deploy/ec2_setup.sh`; local dev instructions in README.

### 4.6 Resource tiers and fairness

| Tier | CPU | RAM | Used for |
|---|---|---|---|
| `xs` | 0.5 | 512m | single-language basics |
| `s` | 1 | 1g | frameworks, single DB |
| `m` | 2 | 2g | multi-service, system design |
| `l` | 2 | 4g | Docker, Kubernetes, AI with local models |

Labs can name a tier instead of raw numbers. Free users get the same tier (the product must feel good on day one), but free users get a shorter idle timeout (10 min vs 30 min) and a daily check limit (50/day).

### 4.7 Image strategy

Layered base images so 100+ labs do not mean 100+ GB:

```
labbox/base            (Ubuntu 24.04, bash, git, curl, nano, vim, less, procps, learner uid 1000)
 ├── labbox/python     (Python 3.12, pip, uv, pytest)
 ├── labbox/java       (Temurin 21, Maven, Gradle)
 ├── labbox/node       (Node 22, npm, pnpm)
 ├── labbox/go         (Go)
 ├── labbox/rust       (Rust)
 ├── labbox/ai-python  (python + openai, anthropic, numpy, pandas, torch-cpu, sentence-transformers small)
 ├── labbox/devops     (docker cli, kubectl, helm, terraform, aws cli + localstack client)
 └── labbox/checker    (curl, psql, redis-cli, kubectl, k6, python requests/pytest)
```

Each lab Dockerfile is `FROM` one of these plus a few lines. `scripts/build_lab_images.sh` builds bases first. Production: images built in CI and pushed to **Amazon ECR**; hosts pull and pre-cache all lab images.

### Phase D acceptance

- [ ] A sample multi-service lab `postgres-indexing-incident` works end to end: Postgres service, setup drops an index, live check measures query time, fixing the index passes.
- [ ] Preview tab shows a learner's FastAPI app on port 8000 and a Spring Boot app on 8080.
- [ ] A user cannot open another user's preview (403) or a port not listed in `preview`.
- [ ] Reaper stops the whole group (workspace + services); reopening starts all with data intact.
- [ ] A fake `@@RESULT` printed by user code has no effect in a `live` lab.

### Phase F acceptance (Sysbox)

- [ ] `docker run hello-world` works inside a `runtime: sysbox` lab container.
- [ ] `kind create cluster` or `k3s` works inside the k8s lab image within 90 seconds.
- [ ] Learner in a sysbox lab cannot see host processes or other users' containers.

---

## 5. Engagement layer (Phase C)

### 5.1 XP, levels, streaks

- XP per task (default 20, set in `lab.yaml`), reduced by hints (section 2.4).
- +10 XP for a correct predict on the first try. +25 for finishing an incident inside its timer. +50 for completing a chapter. +200 for completing a lab.
- Levels: level N needs `100 * N^1.5` total XP (rounded). Show level badge next to the username.
- **Streak:** a day counts when the learner earns at least 20 XP (in their timezone). Show 🔥 count in the top bar. One free "streak freeze" per week.
- Store everything as an `xp_events` ledger (never just a counter), so it can be audited and recalculated.

### 5.2 Daily drill (5 minutes)

- `GET /api/drill/today`: one short challenge per day, picked from the tracks the user is studying: a predict question, a 1-line bug to fix, or a "what does this command do".
- Runs inside a tiny shared `drill` container or purely in the browser for predict-only drills.
- Keeps the streak alive on busy days.

### 5.3 Skill map

- Each track has a map of skills (nodes) with prerequisites (edges). Example for DevOps: Linux basics → processes → networking → Docker → Compose → Kubernetes basics → Deployments → Services → Ingress → Helm.
- A node lights up when the related chapters are completed.
- Rendered on the track page as a clean node graph (use `reactflow`).

### 5.4 Onboarding (first 60 seconds)

1. "What do you want to get better at?" (cards: Get a backend job, Learn DevOps, Learn AI engineering, Crack interviews, Learn a new language).
2. "How much do you know?" (3 quick predict questions to place them).
3. Recommended path with the first lab already started. Learner is typing code within 60 seconds of signing up.

### 5.5 Recap and share

- End of chapter: `recap` card with takeaways, XP gained, streak, "Next chapter".
- End of lab: a shareable card image (generated server side with Pillow or Satori): name, lab, chapters, incidents fixed, date, verification link. Public profile page `/u/{username}` lists completed labs and what they built.

### 5.6 Later (do not build yet, keep the data model ready)

Weekly leagues, live "war game" events (same incident for everyone at once, live leaderboard), team incidents.

### Phase C acceptance

- [ ] XP ledger, levels and streaks work with timezone-correct day boundaries (unit tests with fixed clocks).
- [ ] Onboarding flow lands a new user inside a lab with the editor open.
- [ ] Skill map for one track renders and updates after completing a chapter.
- [ ] Daily drill works and counts for the streak.

---

## 6. AI labs and the LLM gateway (Phase E)

AI is a full track, in depth. The platform needs a safe way for learner code to call models.

### 6.1 LLM gateway

- New backend module `llm_gateway.py` exposing an **OpenAI-compatible** API at `/llm/v1/*` (`chat/completions`, `embeddings`, `responses` as needed), plus an Anthropic-compatible `/llm/anthropic/v1/messages`.
- Lab containers with `llm.enabled: true` get env vars:
  - `OPENAI_BASE_URL=http://gateway:9000/llm/v1`, `OPENAI_API_KEY=<per-user lab token>`
  - `ANTHROPIC_BASE_URL=...`, `ANTHROPIC_API_KEY=<same lab token>`
- The gateway is reachable from the lab network under the alias `gateway` (run a tiny gateway container attached to each lab network, or route the alias to the backend).
- **Real provider keys live only on the server**, never in containers.
- **Model aliases** (so labs never hard-code vendor models): `lab-chat`, `lab-chat-smart`, `lab-embed`, `lab-vision`. Mapping lives in config and can point to OpenAI, Anthropic, Gemini, or a local Ollama.
- Per-user budgets: tokens per day, requests per minute, max tokens per request. Free users get a small budget; paid users a larger one.
- **Request log:** every call stored (prompt, response, tokens, cost, latency). A `lab requests` CLI inside the container (calls a gateway endpoint) shows the learner exactly what was sent. This is a great teaching tool.
- Optional "bring your own key" in user settings (encrypted at rest with a server key), used instead of platform budget.

### 6.2 AI tutor (uses the same gateway)

- "Ask the tutor" on a failed task sends: task description, hints already revealed, the check message, the relevant files (size capped), recent terminal output (last 50 lines).
- System prompt rules: Socratic, never paste the full solution, max 120 words, point to one thing to look at, ask one question.
- "Review my code" after a task passes: comments like a senior engineer PR review (naming, edge cases, performance, production concerns). No XP impact; pure learning.

### 6.3 Vector stores and AI services for labs

Available as `services` in `lab.yaml`: `pgvector` (Postgres 16 + pgvector), `qdrant`, `ollama` (small CPU models such as a 0.5B to 3B instruct model and a small embedding model, pre-pulled into the image), `langfuse` (tracing, optional).

### Phase E acceptance

- [ ] An AI lab container can call `lab-chat` via the OpenAI SDK with only the injected env vars.
- [ ] Budget exceeded returns a clear 429 message inside the lab.
- [ ] `lab requests` shows the last 10 calls with tokens and cost.
- [ ] Tutor never returns the full solution in automated tests (run 20 tutor prompts against solution-leak checks: response must not contain the solution file's key lines).
- [ ] Provider keys are not visible anywhere inside a container (`env`, files, process list).

---

## 7. System design labs (Phase G)

System design is taught hands-on: the learner operates a small real distributed system and makes it meet targets, then explains the design.

### 7.1 Lab shape

- `services`: an nginx load balancer, N app replicas (learner's code or provided), Postgres, Redis, optionally a queue (Redis Streams, RabbitMQ or Kafka in KRaft mode with small memory).
- `check.mode: live` with **k6** in the checker container: runs a load profile, reports `@@METRIC` p50, p95, p99 latency, error rate, throughput.
- Tasks are targets: "p95 under 150 ms at 200 req/s with error rate under 0.5%".
- A **design step** at the end: learner answers 3 to 5 short written questions (why this cache key, what happens if Redis dies, how would you shard). Graded by the tutor model with a rubric stored in `tests/rubric.yaml`, returning a score and feedback. This step gives XP but never blocks completion.
- Optional **diagram step**: a simple drag-and-drop component canvas (reactflow) with a fixed palette (Client, LB, App, Cache, DB, Queue, Worker, CDN). Saved as JSON; included in the written-answer grading.

### 7.2 First system design labs

1. **Scale a URL shortener**: add caching, fix hot keys, add read replicas.
2. **Rate limiter**: token bucket in Redis, per-user and global limits, verified by k6.
3. **Cache stampede**: thundering herd on a popular key; fix with locking or early refresh.
4. **Idempotent payments**: duplicate requests and retries; add idempotency keys.
5. **Queue backpressure**: a slow worker and a growing queue; add consumers, batching, DLQ.
6. **Design a news feed**: fan-out on write vs read, measured.

### Phase G acceptance

- [ ] `rate-limiter` lab: starter fails the limits test, solution passes; k6 metrics shown as gauges in the UI.
- [ ] Rubric grading returns structured JSON (score per criterion + feedback) and is stored per attempt.

---

## 8. The catalog (all tracks)

Launch with **flagship labs first** (one great lab per track), then expand. Every lab follows the content standard in section 9.

### 8.1 Programming languages (`languages`)
- Java: Core Java, Java collections in depth, Java concurrency traps, JVM and memory incidents (OOM, GC, thread dumps), Modern Java (records, sealed, streams, virtual threads)
- Python: Python properly, Python traps, async Python
- JavaScript / TypeScript: JavaScript inside out, TypeScript for real code, How Node really works
- Go: Go basics, Go concurrency
- Rust: Rust basics, ownership in practice
- SQL from zero

### 8.2 Frameworks (`frameworks`)
- **Spring Boot** (flagship): REST APIs, Spring Data JPA, validation and errors, security with JWT, testing, **Spring Boot on fire (10 incidents)**, build your own mini Spring (dependency injection from scratch)
- FastAPI, Express, NestJS
- React, Next.js
- Django (later)

### 8.3 Databases (`databases`)
- Postgres in depth (indexes, EXPLAIN, transactions and isolation, locks and deadlocks, partitioning, replication basics)
- Redis in practice (data structures, caching patterns, streams, pub/sub)
- MongoDB basics
- Database incidents (slow queries, connection pool exhaustion, deadlocks, migrations gone wrong)

### 8.4 DevOps (`devops`)
- Linux on call (processes, files, permissions, networking, systemd, logs)
- Git without fear, Git disasters
- Docker start to ship (images, layers, multi-stage, compose)
- Kubernetes from zero (pods, deployments, services, ingress, config, probes, HPA) with k3s or kind (sysbox)
- Nginx and networking (reverse proxy, TLS, load balancing, debugging 502/504)
- CI/CD with GitHub Actions (local runner via `act`)
- Terraform basics (against LocalStack)
- AWS fundamentals (S3, IAM, Lambda, SQS via LocalStack)
- Observability (logs, metrics with Prometheus, dashboards with Grafana, tracing with OpenTelemetry)
- On-call incidents (disk full, memory leak, DNS, certificate expiry, crash loops)

### 8.5 System design (`system-design`)
The six labs in section 7.2, then: chat system, distributed job scheduler, search autocomplete, consistent hashing, leader election basics.

### 8.6 AI engineering, in depth (`ai`)

Foundations (understand the machine):
- **Tokens and tokenizers**: build BPE from scratch
- **Embeddings**: similarity, vector math, visualizing clusters
- **Attention and transformers from scratch** in NumPy, then PyTorch (CPU, tiny model)
- **Build your own GPT** (character level, trains on CPU in minutes)
- **ML fundamentals**: regression, classification, overfitting, evaluation (scikit-learn)

Building with LLMs:
- LLM APIs (chat, streaming, cost, latency, retries)
- Prompting that works (structure, few-shot, system prompts) measured with evals, not vibes
- Structured output and function calling
- RAG from zero to production: chunking, embeddings, pgvector, hybrid search (BM25 + vectors), reranking, citations, evaluation
- Agents from scratch: tool use loop, planning, error recovery
- MCP: build servers and clients
- Memory and multi-agent systems
- LangChain and LangGraph, Pydantic AI, OpenAI Agents SDK, Claude and the Anthropic SDK, Vercel AI SDK
- Voice agents (speech to text, text to speech, turn-taking)

Running AI in production:
- **Evals that catch regressions** (golden sets, LLM-as-judge, CI evals)
- **AI security**: prompt injection attack and defend, data exfiltration, guardrails
- **AI gateway**: routing, caching, fallbacks, budgets
- Observability for LLM apps (tracing with Langfuse)
- Cost and latency optimization (caching, smaller models, batching)
- Local models with Ollama
- Fine-tuning basics (LoRA on a tiny model on CPU; explain when to fine-tune vs RAG)

### 8.7 Interview (`interview`)
Bug cases per language ("traps"), Java/Spring interview incidents, SQL traps, system design interview drills, "defend your code" mock reviews with the tutor.

### 8.8 Launch set (build these first, in this order)
1. `java-basics` and `python-basics` upgraded to v2 (Phase A/B)
2. `spring-boot-on-fire` (frameworks, multi-service, incidents)
3. `postgres-indexing-incident` → grows into `postgres-in-depth`
4. `linux-on-call` (devops)
5. `rag-from-zero` (ai, gateway + pgvector)
6. `build-your-own-gpt` (ai foundations, CPU only)
7. `rate-limiter` (system design, k6)
8. `docker-start-to-ship` (devops, sysbox)

Each flagship: 8 to 12 chapters, fully tested with `labbox test-lab`.

---

## 9. Content quality standard (every chapter)

- **10 to 20 minutes.** If longer, split.
- **Story first:** a company, a person, a real problem. Reuse a small cast across a lab.
- **Shape:** `story` → 1 to 3 `concept`/`example` → at least one `predict` → `try` → 1 to 4 `task` (or one `incident`) → `recap`.
- **Concept steps under 120 words.** Short sentences. One idea per step. Show, then explain.
- **Every task has 3 hints** and a check message that explains what is wrong without giving the answer, with `expected` and `actual` whenever possible.
- **One "aha" per chapter:** a moment where something surprising happens (a race condition appears, a query gets 1000x faster, an injected prompt leaks data).
- **Real tools only:** real Postgres, real Kubernetes, real models. No fake simulations when a real thing can run.
- **Voice:** friendly, direct, no fluff, no em dashes, Indian-English friendly examples (UPI, dabbas, corner shops (never chai: owner, 22 November), cricket scores are welcome).
- **Difficulty curve:** first 2 chapters (free) must give an early win within 3 minutes and a real "I built that" moment by the end of chapter 2.

---

## 10. Making it a real app (Phase H)

### 10.1 Data and infrastructure

- **Postgres** replaces SQLite (SQLModel already supports it). Add **Alembic** migrations; write the first migration from the current models.
- **Redis** for: check locks (replace in-memory set), rate limits, session data, reaper coordination, WebSocket presence.
- Uvicorn with multiple workers behind Nginx (now safe because locks are in Redis).
- Background worker using **arq** (Redis based) for: image pre-pull, share-card rendering, emails, analytics rollups, backups.

### 10.2 Auth

- Keep username/password, add **Google** and **GitHub** OAuth (Authlib).
- Email verification and password reset (AWS SES).
- Move the main session to an HttpOnly cookie; keep JWT for the WebSocket and preview handshake via a short-lived signed ticket endpoint (`POST /api/ws-ticket` returns a 60 s token).

### 10.3 New tables (additive)

```
user_profile(user_id, display_name, timezone, goal, level, xp_total, streak_current, streak_best, last_active_day)
xp_event(id, user_id, kind, amount, lab_id, chapter_id, task_id, created_at)
chapter_progress(user_id, lab_id, chapter_id, current_step, setup_done, completed_at)
task_progress(user_id, lab_id, chapter_id, task_id, passed, hints_used, first_passed_at)
predict_answer(user_id, lab_id, chapter_id, step_index, choice, correct, created_at)
subscription(id, user_id, plan, status, starts_at, ends_at, provider, provider_ref)
payment(id, user_id, amount_paise, currency, status, provider_order_id, provider_payment_id, created_at)
llm_usage(id, user_id, lab_id, model_alias, provider_model, input_tokens, output_tokens, cost_usd, latency_ms, created_at)
analytics_event(id, user_id, name, props_json, created_at)
```

### 10.4 Payments (Phase I)

- **Razorpay** (UPI, cards, net banking) for India; keep the provider behind an interface so Stripe can be added later.
- Plans: Free (first 2 chapters of every lab, smaller limits), 6 months, 1 year. Prices configurable in DB, GST inclusive display.
- Flow: create order on backend → Razorpay Checkout on frontend → **verify signature on backend** → webhook (`payment.captured`) as the source of truth → activate `subscription`. Webhooks must be idempotent.
- **Entitlement check** in one place (`entitlements.py`): `can_open_chapter(user, lab, chapter)`. Used by chapter, workspace, file, terminal and check routes.
- Paywall UX: when a free user finishes chapter 2 (right after the recap and confetti), show the upgrade card with what they unlock. Never interrupt in the middle of a chapter.
- Coupons (percentage or fixed, expiry, max uses).
- Test mode only until I approve live keys.

### 10.5 Admin and analytics (Phase J)

- `/admin` (role `admin`): users, subscriptions, running containers (with kill and stop), check failures per task (to find confusing tasks), LLM spend per day, top errors.
- **Funnel analytics** from `analytics_event`: signup → first lab opened → first check passed → chapter 1 done → chapter 2 done → paywall shown → paid. Per lab: where people quit (step index), average time per step, hint usage per task.
- These numbers drive content fixes. A task with low pass rate and high hint usage is a content bug.

### 10.6 Abuse and safety controls

- Per-user disk quota (`disk_mb`): measure with a periodic `du` job; over quota → files API refuses writes, terminal shows a banner.
- Egress control for labs with internet: route through an allowlisting HTTP proxy (package registries, GitHub, model gateway only). Block mining pools and SMTP.
- CPU abuse: alert and stop containers at sustained 100% CPU for over 10 minutes outside of checks.
- Max session length (4 hours continuous) and max concurrent labs per user (2 for paid, 1 for free).
- Rate limit signups and checks per IP.
- Keep metadata blocking (`169.254.169.254`) and gVisor/sysbox runtimes in production.

### 10.7 Operations

- Structured JSON logs, **Sentry** for errors (backend and frontend), **Prometheus** metrics (`/metrics`: running containers, check durations, terminal sessions, LLM tokens) and a Grafana dashboard.
- Backups: nightly Postgres dump to S3; user volumes on a dedicated EBS volume with daily snapshots (AWS Data Lifecycle Manager).
- CI (GitHub Actions): lint, type-check, backend tests, frontend build, `labbox validate` and `labbox test-lab` for changed labs, build and push images to ECR.

### 10.8 Scaling path (document, build only step 1 now)

1. **One big host** (for example `m7i.2xlarge`, 8 vCPU / 32 GB) runs everything. Enough for a few hundred concurrent learners on light labs.
2. **API host + N lab hosts**: a `lab_host` table; the backend schedules new workspaces on the host with the most free capacity and routes terminal, files, preview and checks to it (each lab host runs a small authenticated agent API).
3. Warm pools of pre-started containers per popular image.

---

## 11. Phases summary (build order)

| Phase | What | Why first |
|---|---|---|
| **A** | Lesson UX redesign | Biggest impact on stickiness, small backend change |
| **B** | Content format v2 + authoring CLI + solutions | Needed before writing many labs |
| **C** | XP, streaks, levels, onboarding, skill map, drill | Habit and motivation |
| **D** | Multi-service, preview, live checks, failure injection | Unlocks frameworks, databases, incidents |
| **E** | LLM gateway, AI labs, tutor | Unlocks the AI track |
| **F** | Sysbox: Docker and Kubernetes labs | Unlocks DevOps depth |
| **G** | System design labs with k6 + rubric grading | Unlocks system design |
| **H** | Postgres, Redis, OAuth, workers, ops | Real app foundations |
| **I** | Payments (Razorpay, test mode) | Revenue |
| **J** | Admin + funnel analytics | Learn what to improve |
| **K** | Launch-set labs (section 8.8), deploy to AWS | Ship |

Rules per phase: keep all previous tests green, add tests for the new behaviour, update the README, write a short `CHANGELOG.md` entry, and stop for my review.

---

## 12. Definition of done for v2

- [ ] A new user signs up with Google, picks "Learn DevOps", and is typing in a terminal within 60 seconds.
- [ ] The lesson panel is calm, readable and one step at a time; no wall of text anywhere.
- [ ] Launch-set labs (section 8.8) all pass `labbox test-lab` in CI.
- [ ] Incidents, previews, live checks, Docker-in-lab, Kubernetes-in-lab, AI gateway and k6 system design checks all work in production on AWS.
- [ ] Free users can finish 2 chapters of any lab; paying in Razorpay test mode unlocks the rest instantly.
- [ ] Admin dashboard shows the funnel and the worst-performing tasks.
- [ ] The POC security checklist still passes, plus: previews on a separate origin, egress allowlist, disk quotas, provider keys never inside containers.
