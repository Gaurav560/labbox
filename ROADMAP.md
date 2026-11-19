# LabBox by Telusko: project status

Last updated 19 November 2026. **Part A** is what is done, **part B** is what is left, in order.
The detail of every step is in `CHANGELOG.md` and `git log`; the full plan is
`labbox-v2-upgrade-spec.md` (section numbers below point there). How to work on the repo:
`AGENTS.md`.

Rules that always apply: plan first and wait for an OK, one commit per step, all old tests stay
green, and ask before deleting data, touching AWS, or using anything that needs a paid API key.

---

## A. What is done

### The platform (v2 spec, phases A to D)

| Phase | What it gave us |
|---|---|
| POC | Login, one Docker container per user per lab, Monaco editor, real terminal, hidden checks with the `@@RESULT` protocol |
| A | One-step-at-a-time lessons: story, concept, predict, try, recap; a hint ladder |
| B | Content format v2, the authoring CLI (`scripts/labbox`), reference solutions |
| C | XP, levels, streaks with a weekly freeze, onboarding, skill map, daily drill |
| D | Services next to the workspace (Postgres), the Preview tab for web apps, live checks, timed incidents with a bonus |
| E | LLM gateway (aliases, lab tokens, budgets, request log, OpenAI and Anthropic shapes), labs reach it through a locked-down relay, `lab requests`, AI tutor and code review with a solution leak guard, the `ai` lab template, "✦ Ask AI" in the lab footer, offline editor completion and AI code completion (ghost text, `lab-code`, own limits). Free local models via Ollama (`scripts/ollama.sh`). Real VS Code in labs (openvscode-server, `scripts/openvscode.sh`). |
| G | System design: k6 load tests in live checks, metric gauges, `design` steps graded by the tutor model against a hidden rubric, the `rate-limiter` lab (two app copies behind nginx, Redis), the `system-design` template. |

### The lab page, editor and AI (after Phase E)

- **Editor: real VS Code by default** ("IDE"): openvscode-server (Gitpod's open-source VS Code, MIT)
  runs inside each learner's machine, as the learner, and shows through the signed-in proxy at
  `/ide/{lab}/`. A "IDE | Lite" switch in the bottom bar; Lite is our Monaco editor (offline completion,
  AI ghost-text completion) and is forced on screens under 900px.
  - Setup on any machine: `scripts/openvscode.sh` (downloads to `/srv/labbox/openvscode`, adds the
    Python extensions, the `labbox-defaults` extension with the "LabBox Dark" theme and settings, and
    the JetBrains Mono font files).
  - VS Code starts only when the lab page opens it; machines made before it are recreated on open
    (home folder kept); a running IDE restarts itself when the shared setup changes.
  - Typing in the IDE counts as activity for the idle reaper (websocket traffic of 64+ bytes).
- **AI (Phase E):** `scripts/ollama.sh` runs Ollama with free local models (`lab-chat`,
  `lab-chat-smart`, `lab-embed`, `lab-code`). "✦ Ask AI" in the lab footer (tutor), "✦ Review" after a
  pass, AI completion in Lite. Paid providers only with your approval.
- **Look:** the whole app uses GitHub greys (`#111512`), white primary buttons, GitHub's code colours.
- **Lab networks** get a /28 each from `LAB_SUBNET_POOL` (10.88.0.0/16); Docker's default pool ran out
  at about 30 networks.

### Labs: 16 live (batch 1: 11, batch 2: 4, Phase G: 1)

| Track | Labs |
|---|---|
| Languages | python-basics, python-collections, java-basics, java-collections, javascript-inside-out, go-basics |
| Frameworks | fastapi-first-api, spring-boot-first-api, express-api |
| Databases | sql-from-zero, postgres-indexing-incident, **redis-in-practice** (a full course: 13 chapters, 32 tasks, zero to production), **postgres-transactions-and-locks** |
| DevOps | **linux-on-call**, **git-without-fear** |
| System design | **rate-limiter** (not on the home grid, which keeps its 15 cards) |

Skill maps: `tracks/languages.yaml`, `tracks/databases.yaml`, `tracks/devops.yaml`, `tracks/system-design.yaml`.
You chose to stop at 15 labs for now and build the platform phases next.

Every lab passes `validate --strict` and `test-lab` (the starter fails, the solution passes).

### The lab pipeline

- Base images: base, python, java, node, go, checker, ai-python.
- Eight templates: python, java, node, go, service-incident, preview-app, ai, system-design.
- A lab starts as one spec file (`specs/<lab>.yaml`), then `new-lab --from-spec`.
- The quality gate (`validate --strict`) checks the lesson shape and refuses hints that give away the solution.
- CI runs the tests and `test-lab` on every changed lab.

### Website and brand

- **Name:** "LabBox by Telusko". LabBox is the product and Telusko the parent company. The contact is
  connect@telusko.com. Names live in `frontend/src/site.ts`.
- **Home page:**
  - Colours: GitHub charcoal (`#111512`) with a faint tile grid, black panels, white buttons, a muted brick red for small accents, and a little yellow.
  - Hero product tour: Read, Guess, Code, Check scenes for all 15 labs, in a random order for each visitor, with opt-in sound.
  - Below the hero: a colour logo strip, the lab cards, the tracks, and a red closing panel.
- **Login and signup:**
  - Left side: the blue and purple showcase with a typing terminal.
  - Right side: GitHub charcoal with a grid, and a black card.
- **New pages:** FAQs (`/faq`), Privacy policy (`/privacy`) and Terms of Service (`/terms`), linked from
  the footer and under the login card.
- **Lab covers:**
  - The real technology logo, large, on its brand colour (made with `scripts/labbox cover <lab> --logo <tech>`, free).
  - The Java labs show Duke, the Java mascot.
  - Cover addresses carry a version, so a new cover always shows up.

### Repository

- Code is on GitHub at https://github.com/Gaurav560/labbox (branch `master`).
- `backend/.env` (your keys) is never committed.

### Choices you made (keep them)

- **Home page:**
  - Keep: the GitHub charcoal, the tile grid, the red closing panel and white buttons.
  - Rejected: neon red (`#ff2e4d`), topographic lines, film grain, dancing logos.
- **Login page:**
  - Keep: the blue and purple showcase.
  - Rejected: the red and black version, and anything near white.
- **Covers:** real logos, not AI art.
- **Editor:** real VS Code (not a lookalike) as the default, Lite as the fallback. "VS Code" is not
  used as a label (Microsoft trademark): the switch says "IDE | Lite".
- **App colours:** GitHub greys everywhere, not the old blue `#7c9cff`.
- **AI provider:** Ollama (free, local) for now. The OpenAI key stays approved for cover art only.
- **Capacity target:** at most about 100 learners at once. Plan about 1 GB of RAM per running machine
  with the IDE (about 1.5 GB for Java and Spring labs): one 128 GB server or two 64 GB servers.
- **Phase F (Docker and Kubernetes in labs) is skipped on this laptop** (its kernel 7.0 is newer than
  Sysbox supports) and moves to the AWS server in Phase K.
- **How labs are written:** one at a time in chat, in batches of 6. No multi-agent workflow unless you
  say "use a workflow".

---

## B. What is left

### 1. Before going public

- [ ] Have the Privacy policy and Terms reviewed by someone qualified. They are drafts and not legal
      advice, so this matters most before payments arrive.
- [ ] Decide whether the GitHub repository should be private. It is probably public now, including the
      product spec.
- [ ] Push the latest commits (`git push`). The last commits from 19 November are only on this machine.
- [ ] Serve the IDE (`/ide`) and Preview (`/preview`) from their own web address (for example
      `ide.<domain>`), so code there cannot read the learner's login token. Today they share the app's origin.
- [ ] Host VS Code's webview files ourselves: openvscode loads them from Microsoft's `vscode-cdn.net`,
      which contradicts "no third party" in the Privacy policy (`webviewContentExternalBaseUrlTemplate`
      in its product.json).
- [ ] Put a real proxy (nginx or Traefik) in front of IDE and Preview websockets instead of the Python
      backend carrying every keystroke.
- [ ] Pin and test openvscode-server upgrades (today v1.109.5 in `scripts/openvscode.sh`).
- [ ] Rebuild all images once the Ubuntu mirror works again (`scripts/build_lab_images.sh`), so every
      lab image gets the `lab requests` helper from the new base image.

### 2. More labs: 15 written, more later (on hold by your choice)

**Left over from the batch 2 proposal:** FastAPI CRUD with Postgres, SQL traps.

**Then, by track (spec section 8):**
- **Languages:** Python traps, async Python, Java concurrency traps, JVM and memory incidents, Modern
  Java, TypeScript, How Node really works, Go concurrency, Rust basics, Rust ownership.
- **Frameworks:** Spring Data JPA, Spring validation, Spring security with JWT, Spring testing,
  Spring Boot on fire (10 incidents), mini Spring, NestJS, React, Next.js.
- **Databases:** Postgres partitioning, replication, Redis caching, streams and pub/sub, MongoDB,
  database incidents.
- **DevOps:** Git disasters, Nginx and 502/504 debugging, CI with `act`,
  Terraform and AWS on LocalStack, observability, on-call incidents.
- **Interview:** traps for Python, Java and JavaScript; Java and Spring interview incidents.
- **Needs a later phase first:**
  - the AI track (Phase E is built; the labs themselves are not written yet)
  - Docker and Kubernetes labs (Phase F, moved to the AWS server in Phase K)
  - more system design labs (Phase G is built: URL shortener, cache stampede, idempotency, queues, news feed)

**Launch set still missing (spec 8.8):**
- spring-boot-on-fire
- postgres-in-depth
- rag-from-zero
- build-your-own-gpt
- docker-start-to-ship

The flagship labs should reach 8 to 12 chapters; today's labs have 1 or 2.

### 3. Platform phases not started (E and G are done)

**Phase G is done** (19 November): k6 and the `labbox_k6` helper in the checker, metric gauges in the
results drawer, graded `design` steps (`tests/rubric.yaml`, table `design_answer`), the `rate-limiter`
lab (lab 16) and the `system-design` template.

**Next: Phase H. The plan below was proposed on 19 November and is waiting for your OK.**
1. **H1 Postgres:** `scripts/devdb.sh` (Postgres 16 and Redis 7 in Docker on localhost);
   `DATABASE_URL` on Postgres; a one-time copy of the SQLite data (row counts compared, the SQLite
   file kept); fast tests stay on SQLite, plus one full run on Postgres.
2. **H2 Redis for app state:** check lock, machine locks, AI rate counters and a reaper leader lock in
   Redis, so uvicorn can run several workers; in memory when `REDIS_URL` is empty.
3. **H3 worker (arq):** pre-pull lab images, hourly cleanup of unused lab networks, nightly Postgres
   dump to `/srv/labbox/backups`.
4. **H4 login:** HttpOnly session cookie with CSRF protection, a 60 s websocket ticket instead of the
   token in the terminal URL, Google and GitHub sign-in (buttons only when keys are in `.env`;
   accounts linked by verified email). Email verification and password reset wait for Phase K.
5. **H5 safety:** disk quota per learner (default 500 MB), stop machines at 100% CPU for 10+ minutes,
   4 h session limit, at most 2 running labs per learner, per-IP rate limits on signup, login, check.
6. **H6 operations:** `/metrics` for Prometheus and a Grafana dashboard file, JSON logs option, CI on
   Postgres, Sentry built in but off unless a DSN is added.

| Phase | What | Needs from you |
|---|---|---|
| F | Docker and Kubernetes inside labs, with Sysbox (spec 4). Skipped here; do it on the AWS server in K | sudo on that server |
| H | Real app foundations: Postgres instead of SQLite, Redis, Google login, workers, disk quotas (spec 10) | A Google OAuth client id and secret |
| I | Payments with Razorpay in test mode: 2 free chapters, paid unlocks the rest | Razorpay test keys |
| J | Admin dashboard and funnel analytics | Nothing |
| K | Launch-set labs complete, deploy to AWS | AWS access, and your approval before anything runs there |

### 4. Smaller items put off by agreement

- A spoken voiceover or a recorded demo video for the hero tour (needs your recording, or approval for a paid text-to-speech service)
- Share card images for streaks and levels, and a public profile at `/u/{username}`
- Previews on a separate web address, and an allowlist for outbound internet (with Phase H or K)

### 5. Definition of done for v2 (spec 12)

- [ ] Sign up with Google, pick "Learn DevOps", typing in a terminal within 60 seconds (Google login needs Phase H)
- [x] Calm, one-step-at-a-time lesson panel
- [ ] Launch-set labs pass `labbox test-lab` in CI (CI is ready; the labs are not all written)
- [ ] Incidents, previews, live checks, Docker and Kubernetes in labs, the AI gateway and k6 checks all
      work on AWS. The first three work locally.
- [ ] Free users finish 2 chapters, and a Razorpay test payment unlocks the rest
- [ ] Admin dashboard with the funnel and the worst tasks
- [ ] Security checklist passes, plus a separate preview address, the outbound allowlist, disk quotas,
      and provider keys never inside containers

---

## How to pick up again

Open `/home/gaurav/labs_poc` in Claude Code (or Codex) and say: **"Continue LabBox. Read
ROADMAP.md and AGENTS.md. Phase H's plan is in ROADMAP section B.3: build it if I say OK."**
Claude Code reads `CLAUDE.md` (which loads `AGENTS.md`); Codex reads `AGENTS.md` by itself.

**On a fresh machine, before running anything:**
1. `cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, and write
   `backend/.env` yourself (at least `JWT_SECRET`, 16+ characters).
2. `cd frontend && npm install`.
3. `scripts/build_lab_images.sh` (all lab images), `scripts/ollama.sh` (local AI models),
   `scripts/openvscode.sh` (the IDE).
4. Start the backend (`cd backend && .venv/bin/uvicorn app.main:app --port 8000`) and the frontend
   (`cd frontend && npm run dev`), then open http://localhost:5173.
