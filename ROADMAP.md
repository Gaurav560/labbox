# LabBox by Telusko: project status

Last updated 23 November 2026. **Part A** is what is done, **part B** is what is left, in order.
The detail of every step is in `CHANGELOG.md` and `git log`; the full plan is
`labbox-v2-upgrade-spec.md` (section numbers below point there). How to work on the repo:
`AGENTS.md`.

Rules that always apply: plan first and wait for an OK, one commit per step, all old tests stay
green, and ask before deleting data, touching AWS, or using anything that needs a paid API key.

**Positioning (your decision, 19 November):** LabBox is marketed as **AI labs**: a track of 20 to 25
deeply crafted AI labs. System design, programming languages, DevOps, databases and challenges are
the additional tracks. Every lab is built to the Redis course's standard (see "Content standard").

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

- **Read mode and Action mode** (25 November): a Read / Action switch in the lab's top bar. Read shows the lesson alone
  (no editor, terminal or machine; a step's code read-only; a card at task steps); Action is the split screen. Last
  mode remembered, Read on a first visit; the machine starts one step before a task. Read mode lists the chapter's
  scenes on the left (closed by default); Action mode can hide the lesson panel; lesson steps are called scenes;
  Start machine is in the Machine menu.
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

- **Text size per area** (lab top bar, Aa): presets and sliders for lesson, tasks, editor and terminal.
- **Task stepper** in the lesson footer, and **each chapter opens its own code** (Lite and VS Code).

### Labs: 24, sixteen at the full standard

"Full" means every item of the full standard (`CONTENT_STANDARD.md`, the list at the top): a running
project, history, real photos, notes on every recap, playing diagrams, real captured output, two real
tasks a chapter. Photos count real photos only (not the notes pages).

| Lab | Course | Track | Chapters | Tasks | Hours | Running project | Photos | Standard |
|---|---|---|---|---|---|---|---|---|
| spring-ai | Spring AI | ai | 20 | 40 | 16.5 | Atlas, a science museum's guide (Spring Boot 4.2, Spring AI 2.1) | 22 | full (23 Nov) |
| langchain4j | LangChain4j | ai | 30 | 60 | 22.3 | Setu, a hill railway's help desk (LangChain4j 1.24) | 18 | full (23 Nov) |
| langchain | LangChain | ai | 27 | 54 | 19.4 | Navin, a farmers' co-op help desk (LangChain 1.5) | 13 | full (23 Nov) |
| langgraph | LangGraph | ai | 24 | 48 | 17.3 | Harsh, a water board's complaint-to-repair desk (LangGraph 1.2) | 18 | full (24 Nov) |
| rag-vector-databases | RAG and vector databases | ai | 13 | 26 | 9.3 | Fieldbook, a wildlife sanctuary's rangers' assistant (fastembed, FAISS, Qdrant) | 14 | full (24 Nov); rewritten and fact-checked 25 Nov |
| forward-deployed-engineer | Forward Deployed Engineer | ai | 22 | 44 | 17 | Claimdesk, a motor insurer's claims assistant (Python, FastAPI, MCP; real model outputs through the gateway) | 20 | full (27 Nov, new course) |
| rust-basics | Rust from zero | languages | 28 | 56 | 21.7 | Windwatch, a wind farm's turbine monitor (Rust 1.100) | 21 | full (24 Nov) |
| spring-boot-first-api | Spring Boot | frameworks | 31 | 61 | 20 | the Shop API | 12 | full, the template (21 Nov); rewritten and fact-checked 28 Nov |
| python-basics | Python from zero | languages | 19 | 39 | 13.5 | Pocket, a money tracker | 14 | full (22 Nov) |
| java-basics | Java from zero | languages | 18 | 36 | 13.5 | Shelf, a library app | 12 | full (22 Nov) |
| javascript-basics | JavaScript from zero | languages | 18 | 36 | 13 | Mixtape, a playlist app | 10 | full (22 Nov) |
| go-basics | Go from zero | languages | 18 | 36 | 13.5 | Parcel, a parcel tracker | 11 | full (22 Nov) |
| redis-in-practice | Redis in practice | databases | 17 | 39 | 13 | Basket, 10-minute grocery delivery in Pune | 15 | full (22 Nov) |
| sql-from-zero | SQL from zero | databases | 14 | 28 | 10.5 | Safar, bus ticket booking | 9 | full (22 Nov) |
| linux-on-call | Linux on call | devops | 15 | 31 | 11.3 | Tara, a radio telescope observatory | 17 | full (23 Nov) |
| git-without-fear | Git without fear | devops | 14 | 28 | 10 | Trails, a trekking website | 10 | full (22 Nov) |
| python-collections | Python collections | languages | 2 | 4 | 0.5 | | 0 | short, to rewrite |
| java-collections | Java collections | languages | 2 | 4 | 0.5 | | 0 | short, to rewrite |
| javascript-inside-out | JavaScript inside out | languages | 2 | 4 | 0.5 | | 0 | short, to rewrite |
| fastapi-first-api | FastAPI: your first API | frameworks | 1 | 2 | 0.25 | | 0 | short, to rewrite |
| express-api | Express: an order tracking API | frameworks | 1 | 2 | 0.3 | | 0 | short, to rewrite |
| postgres-indexing-incident | Postgres: the slow checkout | databases | 1 | 1 | 0.3 | | 0 | short, to rewrite |
| postgres-transactions-and-locks | Postgres: transactions and locks | databases | 2 | 4 | 0.7 | | 0 | short, to rewrite |
| rate-limiter | System design: a rate limiter | system-design | 2 | 2 | 0.7 | | 0 | short, to rewrite (not on the home grid) |

**Left in the content, by lab:**
- The eight short labs: each needs a syllabus (`COURSE_PRODUCTION.md` step 1), the owner's OK, then the full
  rebuild.
- Drink examples: none left (owner, 23 November: rewritten in every lab, the app, drills, templates and specs).
  One internal task id stays, `q_paid_coffee` in sql-from-zero (learner progress is stored under it; it shows only
  in a code comment). Renaming it needs a data migration: ask first. The owner's own spec files were not touched.
- The `ai` onboarding goal still starts with python-basics; spring-ai is the natural first lab (owner to decide).

Track skill map data (API only since 22 November; each lab shows its own skill map on its course page):
`tracks/languages.yaml`, `tracks/frameworks.yaml`, `tracks/databases.yaml`, `tracks/devops.yaml`,
`tracks/system-design.yaml`, `tracks/ai.yaml`.

Every lab passes `validate --strict` and `test-lab` (the starter fails, the solution passes).

### The lab pipeline

- Base images: base, python, java, node, go, checker, ai-python.
- Eight templates: python, java, node, go, service-incident, preview-app, ai, system-design.
- A lab starts as one spec file (`specs/<lab>.yaml`), then `new-lab --from-spec`.
- The quality gate (`validate --strict`) checks the lesson shape and refuses hints that give away the solution.
- CI runs the tests and `test-lab` on every changed lab.

### Content standard and how courses are made

- `CONTENT_STANDARD.md`: what every course must be. The full standard is the list at its top; the Spring Boot
  course is the template for the voice (section 0); curiosity first for beginners.
- `COURSE_PRODUCTION.md`: how a course is built, in 12 steps from the syllabus to the commit, including real
  captures (AI output through the gateway with an author account), Wikimedia photos, playing diagrams and
  handwritten notes.
- `CONTENT_STANDARD.md` section 7 (24 November, the owner's review): full lessons not summaries, photo leads that make
  the link obvious, more photos in long courses, notes pages in plain sentences, a detailed `before_you_start` in every
  `lab.yaml` (shown on the course page as "Before you start"), photos that always load.
- `tools/authoring/`: the scripts those steps use (`commons_search.py`, `commons_fetch.py`, `insert_photos.py`,
  `add_diagrams.py`, `notes.py`, `author_token.py`, `capture.sh`, `runcheck.sh`).

### Website and brand

- **Name:** "LabBox by Telusko". LabBox is the product and Telusko the parent company. The contact is
  connect@telusko.com. Names live in `frontend/src/site.ts`.
- **Home page (AI first):** hero "Learn AI by building it, not watching it", the pill "New: the Forward Deployed
  Engineer course", then the **AI labs** right under the hero (27 November: the FDE course in a spotlight with a playing
  claim demo and new AI art, the five other AI labs as rows with small logos that open each course's public intro page; `HomeAiLabs.tsx`, the same file on both designs), **Inside a lab** (a real lab screenshot in a framed window, a different one of 26, from all 16 labs, on each visit, framed in that lab's colour, six
  one-line features), the lab grid, "Also on LabBox" tracks, the red closing panel, then
  **FAQs just above the footer** (heading on the left, one numbered list that opens smoothly) (the home footer no longer links to them).
- **Pricing page (27 November, UI only):** `/pricing`, Free, Pro and Teams; Pro and Teams "Coming soon" with no price
  and no payment. Linked from the home menu and public footers.
- **Home page look:**
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

- **Dashboard by category** (23 November): `/labs` groups labs as AI, Languages, Frameworks, System design,
  Databases, DevOps, then Cloud and AWS (coming soon), with jump chips; full courses first in each.
- **Design comparison, "Ukiyo"** (24 and 25 November, owner): a second frontend on branch `design/ukiyo`, served at
  http://localhost:5174 beside the current one; reworked with the owner on 25 November (woodblock prints for every
  lab and category, a new home page with the "start a lab" container, a new login picture). Waiting for the owner to
  keep one; checks before merging are in HANDOFF (Resume here); the design is described in `DESIGN_UKIYO.md`.
- **Premium Reads** (the Library; 24 November, owner): `/library`, public, "Premium reads.": Books, Research papers and Tech
  blogs with real pictures stored in LabBox (covers, first pages, blog views), a featured pick per section, topic
  filters, levels, "Last updated" dates, and a lab chip linking to the lab for every item; whole cards open the item.
  Linked as "Premium Reads" from the home page menu and the dashboard. Admins edit everything, including
  pictures, in Admin > Premium Reads. The papers open with the history of language models (Attention, word2vec,
  GPT-1, BERT, Scaling Laws, GPT-3, InstructGPT, Chain-of-Thought). The
  starting list (21 books, 20 papers, 39 blogs) is `library/seed.yaml` with `library/images/`, loaded by
  migrations 0009 to 0012.

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
- **AI provider:** OpenAI for everything (23 November: "use open ai"; Ollama stopped to save memory): the tutor,
  design grading, AI labs and Spring AI use gpt-4o-mini and text-embedding-3-small through the gateway, with the
  daily budgets on. Editor ghost-text completion is off until you pick a fill-in-the-middle model.
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
- [x] Decide whether the GitHub repository should be private: **public for a while** (owner, 27 November; GitHub
      Actions minutes are free on public repositories). Revisit before payments.
- [ ] Push the latest commits (`git push`): local commits wait for you to push them.
- [ ] Serve the IDE (`/ide`) and Preview (`/preview`) from their own web address (for example
      `ide.<domain>`), so code there cannot read the learner's login token. Today they share the app's origin.
- [ ] Host VS Code's webview files ourselves: openvscode loads them from Microsoft's `vscode-cdn.net`,
      which contradicts "no third party" in the Privacy policy (`webviewContentExternalBaseUrlTemplate`
      in its product.json).
- [ ] VS Code reopens the previous lab's tabs in the next lab: every lab opens `/workspace` from the same
      browser origin, so they share VS Code's saved editor state. A per-lab IDE origin (for example
      `<lab>.ide.<domain>`, together with the item above) or a per-lab folder path fixes it.
- [ ] Put a real proxy (nginx or Traefik) in front of IDE and Preview websockets instead of the Python
      backend carrying every keystroke.
- [ ] Before turning on Sentry (`SENTRY_DSN`): add it to the Privacy policy (a third party receives error
      reports, without personal data). Run Prometheus and Grafana on the server with `deploy/monitoring/`.
- [ ] Hard disk quotas on the server: XFS project quotas on the volumes folder (this laptop's ext4 has none,
      so H5 measures usage each minute and stops machines over the quota).
- [ ] Pin and test openvscode-server upgrades (today v1.109.5 in `scripts/openvscode.sh`).
- [ ] Rebuild all images once the Ubuntu mirror works again (`scripts/build_lab_images.sh`), so every
      lab image gets the `lab requests` helper from the new base image.

### 1a. Live on the laptop through Cloudflare Tunnel (owner, 27 November)

A server costs too much before launch (AWS about $150 to $300 a month for 16 to 32 GB), so the live site runs on
this laptop beside development (`deploy/laptop/README.md`), at `https://labbox.gauravships.systems`, invite only.
- [x] `INSTANCE` setting: a second LabBox on the same Docker names and labels its own machines, checks and networks
      (`lab-prod-u1-...`), and each instance's cleanup sees only its own; `/api/health` reports the release.
- [x] `deploy/laptop/`: one-time `setup.sh` (Caddy and cloudflared pinned, database `labbox_prod`, live `.env`,
      user services), `release.sh` (build per commit, validate, changed lab images, migrate, switch, health check,
      switch back on failure), the deploy timer, and the `prod` helper (status, logs, deploy, rollback, adduser).
- [x] The Deploy button (`.github/workflows/deploy.yml`): CI's checks, then the `production` branch moves, then the
      run waits until the live site reports the commit. GitHub never runs anything on the laptop.
- [ ] Owner: the domain on Cloudflare (nameservers at Hostinger), `sudo loginctl enable-linger gaurav`, the
      Cloudflare login for `setup.sh tunnel labbox.gauravships.systems`, the OpenAI key in the live `.env`, the
      laptop set never to sleep.
- [ ] Move to a rented server when sign-ups open (Hetzner about EUR 16 a month for 16 GB; same scripts).

### 1c. Done: certificates to share (owner, 27 November)

"A certificate automatically, with a URL shareable on LinkedIn, X and other social media, once a lab is passed and
completed" (rules in `backend/app/certificates.py`):
- [x] Earned at **80% of a lab's tasks** (the moment its slot frees). The first certificate asks for the **full name**
      once; after that the check that finishes a lab issues the next one by itself, and the lab says so.
- [x] A public page `/certificates/<id>` (8-character id), and the address to share `/c/<id>`, with the card tags
      LinkedIn, X, WhatsApp and Facebook read and a 1200 x 627 picture drawn by the backend (the lab's woodblock
      print, the name, the lab, the task count, the date, the id, a red seal).
- [x] Share: LinkedIn "Add to profile" (Licenses and certifications, filled in), a LinkedIn post, X, WhatsApp,
      Facebook, copy the link, download the picture. My certificates in the profile menu; a box on each course page.
- [x] The learner may hide a certificate and correct its name once. The privacy policy says the page is public.
- [x] Both designs: Ukiyo a paper certificate framed by the lab's print; the current design a dark card in the lab's
      colour. Migration 0014; 5 backend tests; one browser test on each design.
- [x] A QR code on every certificate (and its share image) that opens `/verify/<id>`: the server's own record for that
      id, so an edited picture shows up as a mismatch; hidden ones are confirmed genuine but private.
- [ ] Later: a PDF to print, and LinkedIn's company page id (`organizationId`) so the issuer links to Telusko's page.

### 1b. Done: at most a few labs at a time (owner, 25 and 26 November)

So learners are not overwhelmed by the number of labs and study nothing (rules in `backend/app/slots.py`):
- [x] An admin sets the limit in Admin, **Lab access** tab (or `scripts/labbox lab-limit N|off`): **every lab open** (the default, until the owner
      turns it on) or **N labs at a time**; one learner can get their own number (or every lab) on their row.
      Admins are never limited.
- [x] A learner unlocks a lab with the **Unlock this lab** button on its course page. A locked lab opens nothing but
      that page (cover, description, before you start, the skill map without links): its lessons, machine, terminal,
      editor, files, checks, tutor, preview and VS Code all answer 403, and a lesson link lands on the course page.
- [x] **Finished = 80% of the lab's tasks passed at least once**: the slot frees at once and the lab stays open.
- [x] **Mondays (00:00 to 24:00 India time)** a learner may swap an unfinished lab out (its machine stops; progress
      and files stay). Lowering the limit keeps unlocked labs open; nothing new unlocks until a slot is free.
- [x] Migration 0013 (`lab_slot`, `site_setting`, `user.lab_limit`); 12 backend tests (`tests/test_slots.py`); one
      browser test (`e2e/lab-slots.spec.ts`); the dashboard's slot strip and lock badges, on both designs.

### 2. Next: the AI track (24 labs), waiting for your OK on the plan

This is the product's headline. **Its first course is done: Spring AI** (23 November, OpenAI through the
gateway, your choice). Planned labs, in four stages (shown on the home page):
- **Foundations:** How LLMs work, Prompts that hold up, Structured output, Tool calling, Streaming
  responses, Cost and latency budgets.
- **Retrieval:** Embeddings and similarity, Vector search with pgvector, RAG from zero, Chunking and
  ranking, Hybrid search and rerankers, Evaluating RAG.
- **Agents:** The agent loop, Memory and state, Planning multi-step work, Prompt injection and
  guardrails, Build an MCP server, Multi-agent workflows.
- **Production:** Evals and LLM judges, Tracing and observability, Caching and rate limits for LLMs,
  Local models with Ollama, Fine-tuning basics, Build your own GPT.

Already built for it: the LLM gateway (aliases, budgets, `lab requests`), the `ai` lab template with
deterministic checks (a fake client), graded design reviews, services (pgvector, qdrant as lab
services). Decisions needed from you before building:
1. **Which model the AI labs use.** The free local models (qwen2.5 0.5B and 1.5B) work, but are weak
   at tool calling, JSON and agents; a premium AI course needs a capable model. Mapping `lab-chat` to a
   paid provider (OpenAI, Gemini or Anthropic) needs your approval and your key in `backend/.env`.
2. **Build order and size:** suggested first release is stage 1 (6 Foundations labs), then one
   stage at a time, each lab to the content standard above.

### 2b. Later: one codebase that grows through the course (owner, 27 November: "we will be doing it in future")

Today most big labs keep **one folder per chapter** in `starter/` (`01-the-role/`, `02-discovery/`, ...): each chapter is a
small separate program. Plan A (done 27 November) only shows those folders one at a time. Plan B changes how the code
is built: **one project that every chapter adds to**, so the learner grows a tiny codebase into a real app and knows
every file because they wrote it.

Example, the Forward Deployed Engineer lab:

```
chapter 1    claimdesk/  baseline.py, data/claims.csv
chapter 4    claimdesk/  baseline.py, clean.py (new), data/...
chapter 9    claimdesk/  ... extract.py (new: read a claim email with the model)
chapter 13   claimdesk/  ... app.py (new: uses clean.py and extract.py together)
chapter 22   claimdesk/  about 15 files, one real app
```

What it takes, per course:
- **Starter:** one project folder. Each chapter adds files or a TODO in an existing file (`# TODO (task <id>)`), never
  a new copy of the project. Later chapters must import and call earlier chapters' code, so it truly grows.
- **Solution:** the finished project after each chapter (a git-like series: `solution/after-01/`, `after-02/`, ... or
  one solution plus per-chapter patches), so `test-lab` can check that each chapter's starter fails and its
  solution passes on top of the previous chapters' solutions.
- **Checks:** `run_checks.sh` tests only the current chapter's tasks (`LABBOX_CHAPTER`), but on the whole project.
- **Lessons:** name the growing files ("open `clean.py`, the file you wrote in chapter 4"), every step with
  `file="..." line="..."` as CONTENT_STANDARD section 3 asks.
- **Learners already in the course:** keep their folders; `containers.top_up` never overwrites. Plan B applies to new
  workspaces, or to a new lab id if the change is too big to merge.
- **Effort:** about a day per big course. Do it as part of "every course to the full standard", course by course,
  starting with the Forward Deployed Engineer (Claimdesk).
- Rust from zero already works close to this (one Cargo workspace, a crate per chapter); Spring Boot is also one app
  per chapter. Look at both first.

### 2c. Later: custom labs (owner, 28 November: "custom labs", a future plan)

- Labs made to order, beyond the catalogue. The owner named the idea only; the details (who orders one, for
  example a company that wants a lab on its own stack or data, or a learner who picks a topic; how one is built and
  priced) are to be decided with the owner before any work. Nothing is built yet.

### 2d. Later: short videos for the hard lessons (owner, 28 November: "60 sec to 4 min videos", "not topics but lessons")

- A video of 60 seconds to 4 minutes for each lesson learners find hard to understand, shown inside that lesson; not
  one per topic, and not for every lesson. Which lessons qualify can come from the data we already have (steps where
  learners stop, tasks with many failed checks or hints). How the videos are made (recorded by a person, or made from
  the lesson's own diagrams and animations) is the owner's call. Nothing is built yet.

### 2e. Jarvis, each learner's realtime voice assistant (owner, 28 November)

Steps 1 to 4 are done (see CHANGELOG, 28 November); his voice and tone are to be tuned later (owner). The owner's brief: an assistant for each learner, with context of
everything about them, that notices when they sign up, log in, study or get stuck, and talks like a human. Realtime
speech to speech only (OpenAI `gpt-realtime-2.1-mini` over WebRTC). Agreed limits: $1.50 a day, a hard stop at $40 a
month (the OpenAI credit is $50), Pro 20 minutes a day, free learners one 3-minute trial (at most 10 a day); all
changeable in Admin, Jarvis. Pro is set by hand in Admin, Learners, until payments (phase I) exist.

- [x] Step 1: talk with Jarvis on any lab page or the dashboard; he knows the learner (name, goal, level, streak, labs
  started, certificates, where they struggled this week, the exact lab, chapter, step and task on screen) and calls
  read-only tools (the step, the task and the hints seen, the learner's code, the last check, progress). Limits, cost
  from OpenAI's reported usage, server-side hangup at a limit, Admin tab, Pro switch, pricing page lines.
- [x] Step 2: notice "stuck" with backend rules (no model, no cost): the same task failing 3 checks in a row, every
  hint used, or 8 minutes on a task step without a check. The orb glows and offers help in a line of text: Pro and
  trial learners tap "Talk it through" (Jarvis is told why and opens with it); a free learner after the trial gets
  "Ask AI (typed)", which opens the tutor. Once per task per 6 hours, never on a passed task. Not done: "code undone
  again and again" (file edits are not recorded on the server yet).
- [x] Step 3: welcome on sign-up and on return, and memory across visits. The dashboard asks once per browser session
  (`GET /api/jarvis/welcome`): a learner with no lab opened yet is welcomed by name with their goal; one away 6 hours or
  more is told where they stopped, with a Continue link. Pro and trial learners can tap Talk to Jarvis, and he opens
  from the welcome. At the end of a Pro conversation Jarvis writes himself a two or three sentence note (a text-only
  reply outside the conversation, about 1 second); the last 3 notes are in his next conversation's context
  (`jarvis_session.summary`, migration 0017).
- [x] Step 4: celebrations, learner settings and what Jarvis can see. After a check the lab page asks
  `GET /api/jarvis/cheer`: a first task ever, a finished chapter (with a link to the next) or a finished lab (with its
  certificate) is celebrated once, in a line; Pro learners can tap Talk. Settings behind the gear on the panel
  (`PUT /api/jarvis/settings`, `user.jarvis_mode`, migration 0018): offer and wait for a tap (the default), talk first
  (Pro: he starts by himself when the browser allows the microphone and sound), or off (no offers, no orb; the profile
  menu turns him back on). Before the first conversation the learner reads "What Jarvis can see" once
  (`user.jarvis_note_seen`). Pro learners can make him forget his notes (`DELETE /api/jarvis/memory`).
- Known limits: a spoken reply cannot be filtered before it is heard (the rules and the tools keep solutions out);
  the browser reports usage, and the server caps the counted seconds by the wall clock and hangs up at a limit.

### 3. More labs in the other tracks (after the AI track)

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
  - the rest of the AI track (Phase E is built; Spring AI is its first course, the others are not written yet)
  - Docker and Kubernetes labs (Phase F, moved to the AWS server in Phase K)
  - more system design labs (Phase G is built: URL shortener, cache stampede, idempotency, queues, news feed)

**Launch set still missing (spec 8.8):**
- spring-boot-on-fire
- postgres-in-depth
- rag-from-zero
- build-your-own-gpt
- docker-start-to-ship

**Every lab becomes a full course, one by one** (owner, 20 to 22 November). Done: the ten in the labs table
(part A). Left: the eight short labs, each after a syllabus and your OK. Ideas recorded for later: "Python in
practice" (with a story), "Spring Boot in production" (a story and incident scenarios), and query rewriting
plus a follow-up golden question for Spring AI's capstone (the lesson already names it as the next step).
How each course is built: `COURSE_PRODUCTION.md`.

### 4. Platform phases not started (E and G are done)

**Phase G is done** (19 November): k6 and the `labbox_k6` helper in the checker, metric gauges in the
results drawer, graded `design` steps (`tests/rubric.yaml`, table `design_answer`), the `rate-limiter`
lab (lab 16) and the `system-design` template.

**Phase H is under way** (OK given on 19 November). Order set by you on 20 November: H5, then H6; H4 (Google and GitHub login with JWT) at the very end; Phase I (payments) after the AWS deploy (K). H1 is done: the app runs on Postgres since 19 November (SQLite copy kept at `/srv/labbox/labbox-sqlite-before-h1.db`).
1. **H1 Postgres (done):** `scripts/devdb.sh` (Postgres 16 and Redis 7 in Docker on localhost);
   `DATABASE_URL` on Postgres; a one-time copy of the SQLite data (row counts compared, the SQLite
   file kept); fast tests stay on SQLite, plus one full run on Postgres.
2. **H2 Redis for app state (done):** check lock, machine locks, AI rate counters and a reaper leader lock in
   Redis, so uvicorn can run several workers; in memory when `REDIS_URL` is empty.
3. **H3 worker (arq) (done):** pre-pull lab images, hourly cleanup of unused lab networks, nightly Postgres
   dump to `/srv/labbox/backups`.
4. **H4 login:** Google and GitHub sign-in **done (27 November)**: buttons only when keys are in `.env`, accounts linked
   by verified email, a one-time code instead of the token in the address, `user.email` saved (`app/oauth.py`, README
   "Sign in with Google and GitHub"). Still to do: link Google or GitHub to an existing username account from the
   profile; password reset by email (needs an email sender); an HttpOnly session cookie with CSRF protection and a
   60 s websocket ticket instead of the token in the terminal URL.
5. **H5 safety (done):** disk quota per learner (default 500 MB), stop machines at 100% CPU for 10+ minutes,
   4 h session limit, at most 2 running labs per learner, per-IP rate limits on signup, login, check.
6. **H6 operations (done):** `/metrics` for Prometheus and a Grafana dashboard file, JSON logs option, CI on
   Postgres, Sentry built in but off unless a DSN is added.

| Phase | What | Needs from you |
|---|---|---|
| F | Docker and Kubernetes inside labs, with Sysbox (spec 4). Skipped here; do it on the AWS server in K | sudo on that server |
| H | Real app foundations: Postgres instead of SQLite, Redis, Google login, workers, disk quotas (spec 10) | A Google OAuth client id and secret |
| I | Payments with Razorpay in test mode: 2 free chapters, paid unlocks the rest | Razorpay test keys |
| J | Admin dashboard and funnel analytics (done 20 November) | Nothing |
| K | Launch-set labs complete, deploy (on the laptop through Cloudflare Tunnel since 27 November; a server later) | The steps in section 1a |

### 5. Smaller items put off by agreement

- A spoken voiceover or a recorded demo video for the hero tour (needs your recording, or approval for a paid text-to-speech service)
- Share card images for streaks and levels, and a public profile at `/u/{username}`
- Previews on a separate web address, and an allowlist for outbound internet (with Phase H or K)
- Photos still to add (Wikimedia Commons refused the downloads on 24 November with 429s): Rust from zero chapter 2
  `File:Professor Simon Peyton Jones FRS (cropped).jpg` (CC BY-SA 4.0, Duncan.Hull) and chapter 17 `File:Bjarne
  Stroustrup (2013).jpg` (CC BY 2.0, ICPCNews), each in the chapter's history step; LangGraph's Jim Gray photo; and Karen Spärck Jones
  (`File:Karen Spärck.jpg`, CC BY 2.5, Markus Kuhn) for chapter 9's history step in RAG and vector databases.
  Fetch with `tools/authoring/commons_fetch.py`, insert with `insert_photos.py`, then validate.

### 6. Definition of done for v2 (spec 12)

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

Open `/home/gaurav/labs_poc` in Claude Code (or Codex) and say: **"Continue LabBox. Read AGENTS.md, then
HANDOFF.md."** HANDOFF lists the decisions waiting for you; this page's part B is the order of the rest
(the AWS deploy K needs you, then H4 login, then I payments; the short labs and the AI track as you choose).
To build or rewrite a course, the agent follows `CONTENT_STANDARD.md` and `COURSE_PRODUCTION.md`.
Claude Code reads `CLAUDE.md` (which loads `AGENTS.md`); Codex reads `AGENTS.md` by itself.

**On a fresh machine, before running anything:**
1. `cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, and write
   `backend/.env` yourself (at least `JWT_SECRET`, 16+ characters).
2. `cd frontend && npm install`.
3. `scripts/build_lab_images.sh` (all lab images), `scripts/ollama.sh` (local AI models),
   `scripts/openvscode.sh` (the IDE).
4. Start the backend (`cd backend && .venv/bin/uvicorn app.main:app --port 8000`) and the frontend
   (`cd frontend && npm run dev`), then open http://localhost:5173.
