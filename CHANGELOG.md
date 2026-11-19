# Changelog

## The app in GitHub greys

- The app-wide theme moves from the old blue (`#7c9cff`) to the GitHub greys of the home and login
  pages: charcoal `#111512` background, grey panels, white primary buttons (black in light mode), and
  GitHub's green, red and amber for pass, fail and warnings. Light mode uses GitHub's light greys.
- The editor gets matching `labbox-dark` and `labbox-light` Monaco themes (same background, quieter
  line numbers, grey ghost text), and the terminal uses the same greys, so the lab reads as one surface.
- The login page's blue and purple showcase is unchanged (it has its own colours).

## AI completion: fixes from trying it for real

- An empty text after the cursor made Ollama answer like a chat model (a markdown rewrite of the whole
  file) instead of filling in the middle; at least a newline is now always sent.
- Markdown fences are stripped from suggestions, and a suggestion stops at the first blank line.
- The solution guard now compares code with spaces and quotes removed but symbols kept, so
  `HSET menu "filter coffee" 30` still matches an unquoted copy, while similar but different code
  (`n % 2 != 0` next to the solution `n % 2 == 0`) is no longer blocked.

## Editor: AI code completion

- Grey ghost-text suggestions at the cursor once typing pauses (400 ms); Tab accepts, typing on
  ignores. A "✦ AI on/off" switch in the editor bar, remembered per browser, on by default.
- New alias `lab-code` (default `ollama/qwen2.5-coder:1.5b`, a fill-in-the-middle code model, free
  and local; `scripts/ollama.sh` pulls it). The gateway gained OpenAI-style `/llm/v1/completions`
  with `suffix`.
- Route `POST /api/labs/{lab}/complete` sends the code around the cursor (2,000 characters before,
  600 after), trims the suggestion to at most 6 lines, and drops any suggestion that would write a
  line of the task's reference solution (the tutor's guard).
- Completions have their own limits (30 a minute, 200,000 tokens a day, `LLM_COMPLETION_*`), so
  typing never uses up the tutor's budget. `AI_COMPLETION=false` turns the feature off server-side.

## Editor: offline code completion

- New `frontend/src/completions.ts`: completion for Python, Java, Go, SQL and shell (JavaScript and
  TypeScript already had Monaco's full language service). Keywords, built-ins, the library calls the
  labs use (redis-py, FastAPI, Spring, Postgres functions), and snippets (`def`, `for`, `ifmain`,
  `sout`, `iferr`, `@app.get`...). Names from every open file are suggested too.
- `.go` and `.sql` files now get syntax colouring. No AI and no network: instant and free, and it only
  finishes names, never a task's solution. AI completion is planned for AI labs, behind a per-lab switch.
- New browser test `e2e/editor.spec.ts`.

## Tutor: easy to find, harder to trick

- "✦ Ask AI" in the lab footer next to Check and Hint, on every step, for the current task (it turns
  into "✦ Review" once the task passes). The tutor is available before the first Check too.
- Replies render as formatted text. Code blocks are removed from tutor replies (the tutor gives
  nudges, not code); a reply with almost nothing left becomes the safe nudge.
- The leak guard now compares words (quotes and punctuation do not hide a copied line) and also
  covers the commands in `solution/apply.sh`, minus anything the lesson text already shows. Found
  live: the local model handed out the full `HSET menu ...` command; that reply is now blocked.

## Phase E: the ai lab template

- `scripts/labbox new-lab <id> --template ai`: a Python lab with `llm.enabled`, `FROM labbox/ai-python`,
  a first "barista bot" chapter, and a deterministic check that hands the learner's code a fake
  OpenAI client and grades the request (model alias, messages) and the returned text.
- Commented pgvector and qdrant service examples for RAG labs in the template's `lab.yaml`.
- README: the gateway, the models, the budget settings, the tutor and how AI labs are checked.

## Phase E: labs talk to the gateway

- `llm: {enabled: true}` in a lab is now allowed (it was refused until Phase E). Such a lab gets a
  private network and a tiny relay container (`alpine/socat`, read-only, no capabilities, user
  65534) that answers as `gateway:9000` and forwards only to the LLM gateway.
- The workspace gets `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY`
  and `LABBOX_GATEWAY`; the key is a lab token for that user and lab only. Real provider keys never
  enter a container.
- `lab requests` (and `lab requests --last`) in every image built from the new base.
- New image `labbox/ai-python` (OpenAI and Anthropic SDKs).
- Docker acceptance tests: the OpenAI SDK reaches `lab-chat` with only the injected env vars, a
  used-up budget shows a clear 429 inside the lab, and the server's provider key is nowhere in the
  container (env, files, process list).

## Phase E: AI tutor and code review

- "✦ Ask the tutor" under a task once a check has failed: a Socratic nudge built from the task text,
  the hints already revealed (never the unrevealed ones), the last check result and the learner's
  files (capped). "✦ Review my code" once the task passes: a short PR-style review, no XP.
- Both go through the LLM gateway as `lab-chat-smart` and count against the learner's daily budget.
- Leak guard: if a reply contains any line of the reference solution (whitespace-insensitive), it is
  replaced by a safe nudge that only repeats a hint the learner already paid for. Tested on 20 tasks
  with a model that tries to paste the solution: nothing gets through.
- New routes `POST .../tasks/{task}/tutor` and `.../review`; the lab browser test asks the tutor.

## Phase E, step 1: the LLM gateway

- New `backend/app/llm_gateway.py`, its own small app on port 9000 (`LLM_GATEWAY_PORT`), started by
  the backend and bound to the Docker bridge address. OpenAI-style `/llm/v1/chat/completions`
  (with streaming), `/llm/v1/embeddings`, `/llm/v1/models`; Anthropic-style
  `/llm/anthropic/v1/messages`; and `/llm/requests` (the learner's last 10 calls, or `?last=true`).
- Labs ask for aliases (`lab-chat`, `lab-chat-smart`, `lab-embed`); `LLM_MODELS` maps them to a
  provider and model. Providers: `ollama` (free, local, the default), `openai`, `gemini`, `fake`
  (tests). Real keys stay on the server; paid providers are only used if the owner maps an alias to one.
- Lab keys are tokens scoped to one user and lab; login and preview tokens are refused, and the
  other way round. Budgets per user: 50,000 tokens a day, 20 requests a minute, replies capped at
  1,024 tokens, with clear 429 messages. Every call is logged in the new `llm_request` table
  (migration 0006, additive) with tokens, cost and latency.
- `scripts/ollama.sh` runs Ollama in Docker on localhost and pulls `qwen2.5:0.5b`, `qwen2.5:1.5b`
  and `nomic-embed-text`. 12 new tests use the fake provider.

## Batch 2, lab 4: Postgres transactions and locks

- New lab `postgres-transactions-and-locks` (databases, intermediate, 2 chapters, 4 tasks). Chapter 1:
  fix a negative wallet, add a CHECK constraint, and write an all-or-nothing `transfer()` function
  (overdrafts and unknown wallets must raise and change nothing). Chapter 2, an incident: a forgotten
  "nightly-report" transaction locks order 42; end it with `pg_terminate_backend` and set
  `idle_in_transaction_session_timeout` on the database.
- The checker tries the learner's database only inside transactions it rolls back, with a 2 s
  `lock_timeout`, so a Check never changes their data and never hangs.
- The home grid stays at 15 cards: 13 live labs, plus Docker and Kubernetes as "coming soon"
  (the Nginx card is dropped until that lab exists).

## Batch 2, lab 3: Git without fear

- New lab `git-without-fear` (devops, beginner, 2 chapters, 5 tasks). Chapter 1 builds a real `shop`
  repo: commit, branch, merge. Chapter 2 builds `kitchen` plus a bare `kitchen-origin.git`: amend a
  secret out of an unpushed commit, then `git revert` a pushed typo without rewriting history.
- Setup commits use fixed authors and dates, so every learner gets the same hashes; the live check
  reads the repo read-only and verifies the pushed commits are still in `main`.
- New chapter option `setup_user: learner` (default `root`, unchanged for existing labs): lab
  containers drop every capability, so root cannot write the learner's files.

## Batch 2, lab 2: Linux on call

- New lab `linux-on-call` (devops, beginner, 2 chapters, 5 tasks). Chapter 1: three log tools
  (`count_5xx.sh`, `top_ips.sh`, `slowest.sh`) built from awk, sort, uniq and head. Chapter 2: empty a
  runaway log without deleting it, and `fix_perms.sh` (executable scripts, a 600 secrets file).
- Checks run the learner's scripts on logs and server folders they have never seen (generated in the
  checker), so hardcoded answers fail.
- New skill map `tracks/devops.yaml`. The "Learn DevOps" goal now starts with this lab. The home
  grid shows it live; the home test checks that DevOps has labs and AI is "Soon".

## Batch 2, lab 1: Redis in practice

- New lab `redis-in-practice` (databases, intermediate, 2 chapters, 5 tasks) with a real Redis 7.4
  service next to the workspace. Chapter 1 in `redis-cli`: a hash, a key with a TTL, a sorted set.
  Chapter 2 in a FastAPI app: a cache-aside price cache (60 s TTL) and an OTP rate limiter (3 a minute).
- Live checks read Redis and call the learner's running app over HTTP (cold call slow, warm call
  under 0.3 s; 200, 200, 200, 429). No learner code runs in the checker.
- New skill map `tracks/databases.yaml`. The home grid shows the lab live instead of "coming soon".
- `test_skill_map_lights_up` now checks the languages map is in the list, not that it is the only one.

## Hero product tour

- The hero subtitle is rewritten to paint the picture: a real Linux machine in the browser, code on
  one side, a terminal on the other, and a guide checking every step.
- The hero terminal is replaced by a product tour (`frontend/src/components/HeroTour.tsx`): a small
  copy of a lab playing the four moves of every lesson (Read, Guess, Code, Check). Each loop shows
  a different one of the 11 labs, in a shuffled order per visitor.
- Tabs jump to a step and pause; a play/pause button; still frames for reduced motion.
- Opt-in sound (off by default): soft key ticks, a pick sound and a chime on pass, generated with
  Web Audio. No audio files, no paid service.

## No more "chai"

- Every "chai" in the app is replaced (165 places in 56 files: lab stories, starters, solutions,
  hidden tests, the SQL lab's sample data, a drill, the home page demo and hero terminal, templates,
  specs, backend and browser tests): masala chai -> filter coffee, cutting chai -> cold coffee,
  chai stall -> coffee stall, Chai Point -> Brew Point, chai -> coffee. The SQL task id
  `q_paid_chai` is now `q_paid_coffee`. Words like "chain" are untouched; the two spec documents and
  older changelog entries keep their history.
- The JavaScript lab's ordering check expected prices from the old item name; updated.
- All lab images rebuilt; every lab passes `test-lab` again.

## SQL gets its own cover

- SQL from zero no longer shares the Postgres elephant: it has our own generic SQL mark (an amber
  database with "SQL" on indigo, `tools/logos/sql.svg`), since SQL is a language, not a product.
  The elephant stays on the Postgres lab. Use `--logo sql`.

## Home page: hand-picked lab cards

- "Pick a lab" shows a chosen 5 x 3 set instead of the first six labs: Express, FastAPI, Go, Java
  basics, Spring Boot, JavaScript, Python basics, SQL from zero, the Postgres incident, then six
  "Coming soon" cards (Redis, Git, Docker, Kubernetes, Linux, Nginx; not links until the labs exist).
  A "See all labs" button below opens the labs page (sign up first for visitors). The lists are
  `FEATURED` and `COMING_SOON` in `HomePage.tsx`; a coming-soon card hides itself once that lab is
  live. Covers for the coming-soon cards are in `frontend/public/covers/`.
- The closing panel has no FREE sticker, and its button says "Start your first lab".

## Duke on the Java covers

- Java basics shows Duke, the Java mascot, waving on Java orange; Java collections shows Duke giving a
  thumbs up on Java navy. Both keep a small Java logo badge.
- Duke artwork: Sun Microsystems released Duke under the BSD license; the SVGs come from Wikimedia
  Commons (`tools/logos/LICENSE-duke` has the sources). Use `--logo duke-waving,java` or
  `--logo duke-thumbsup,java`; the credit then names both sources.

## Cleaner covers and closing panel, new Java cover, softer grid

- Lab covers: the dot pattern and the small dots on the rings are gone (logo, rings and light only).
- Java covers (java-basics, java-collections): Java blue (#1b4f80 to #08172b) instead of orange, so
  the red flame and the blue cup both stand out. Picked from six candidates.
- The red closing panel on the home page has no dot texture now.
- The page grid is fainter (dark #161a17, light #edebe6).

## Home page: the hero terminal shows 11 different labs

- The hero terminal plays short sessions from all 11 live labs (Postgres incident, Python, FastAPI,
  Spring Boot, JavaScript, Go, SQL, Express, Java basics, Java collections, Python collections), using
  each lab's real files, commands and outputs. Every visitor starts on a random one, then they follow
  in a shuffled order. The header shows the lab name (the incident keeps its red INCIDENT and timer).
- The technology logos in the strip are in colour by default.

## Home page: GitHub charcoal, white buttons, muted red, contour lines

- Background: the same charcoal as the login page (#111512), black panels and cards, green-grey
  borders and text.
- Buttons are white with black text, like GitHub (black with white text in light mode).
- Red is a muted brick (#d1605a, light mode #b8463f) used only for small accents: "doing", the live
  dot, section labels, the stats lines. No glows, no red blocks; the yellow is softer too.
- Background: the GitHub tile grid (32 px). Film grain and topographic lines were tried and dropped.
- The closing panel is red again, in calmer brick shades (#e07a72 to #a9443e) with a fine dot
  texture, dark text and a black button. (The yellow FREE sticker was removed on 20 November.)

## LabBox by Telusko, FAQs and legal pages

- Naming: LabBox is the product and Telusko the parent company. The logo shows "LabBox" with a small
  "by Telusko" line, page titles read "LabBox by Telusko", the legal pages say "LabBox is a product of
  Telusko", and the copyright is Telusko's. Names and the contact address (connect@telusko.com) live
  in `frontend/src/site.ts`.
- New public pages: `/faq` (10 questions), `/privacy` and `/terms`, written to match what the app
  really does with data today. Linked from the home footer and under the login card.
- Login page: GitHub-style greys in both themes: the right side is charcoal #111512 with a faint grid,
  and the card is black #000000, with green-grey borders and text.

## Home page redesign (red, black, grey, white, a little yellow)

- New palette for the home page only: black and greys, a cool crimson red for actions, white text and
  a touch of lemon yellow for numbers and wins; a matching light theme.
- Hero: the same headline, with "doing" in red and a yellow underline that draws itself, "watching"
  struck through, a live "N labs live now" pill, and a terminal that types out a real incident (slow
  checkout, add an index, check passes, +325 XP).
- Below: a moving strip of real technology logos, big numbers, a bento grid with the four lesson
  moments (the predict question still works), the live labs as cards with their logo covers, the
  tracks as numbered rows, and a red closing panel.
- Login page: the floating logos are gone (first they danced, then floated; the page is calmer without
  them: the headline and the typing terminal carry the showcase side). In light mode the card and the
  page around it are soft grey-white instead of pure white, easier on the eyes.

## Login page redesign

- Split screen: a showcase side with real technology logos floating over a soft glow and a terminal
  that types out a lab run (still when the browser asks for reduced motion), and the form on the right
  with a gradient border, large fields, a Show/Hide toggle for the password and one big primary button.
- Same fields, button names and behaviour as before (Enter submits; the other action stays one click
  away). On phones the showcase shrinks to a short band above the form.
- Logos for the page are in `frontend/public/logos/` (devicon, MIT).

## Lab covers: real logos on brand colours

- Every lab card now shows the real technology logo on its brand colour: Python blue, Java orange,
  Postgres blue, Go cyan, JavaScript yellow, FastAPI teal, Spring green, Express black, Redis red.
  The logo is the picture: big, in its own colours, on a soft light so a red logo still stands out on
  a red card. Framework labs add the language as a small badge (FastAPI + Python, Spring + Java,
  Express + Node).
- `scripts/labbox cover <lab> --logo <tech>[,<tech>]` builds the cover as one SVG (3 to 19 KB) from
  devicon's original logos (MIT, vendored in `tools/logos/` with 18 technologies ready). Free, no API.
- The AI covers (`cover.webp`) are replaced; `--generate` still works if wanted.
- Every cover is checked to be valid XML (the Go logo needed a namespace the first version dropped).

## Labs batch 1: six new labs (11 in total)

- `python-collections` (lists, dicts, sets, sorting; Dabba Express), `java-collections` (records, List,
  Map, TreeSet, Comparator; PaySetu settlement), `javascript-inside-out` (type traps, equality,
  closures, Promise.all; Ravi's bot), `go-basics` (slices, errors, maps, structs; Tapri Counter tills),
  `sql-from-zero` (SELECT, WHERE, COUNT, JOIN, GROUP BY on a live Postgres; the learner's queries run
  read-only with a 5 s limit and are compared with reference results), `express-api` (GET and POST with
  validation and status codes; Dabba Express order tracking, live in the Preview tab).
- Each made from a spec in `specs/`, passing `validate --strict` and `test-lab`, with an AI cover picked
  from three candidates. The gate caught two hints that quoted solution lines; reworded.
- The languages skill map now links Python, Java, JavaScript, Go and SQL chapters (11 skills).
- Fixes: "1 tasks" on lab cards; browser tests no longer assume a fixed number of labs.

## Lab production pipeline

- Base images `labbox/node` (Node 22.23.5) and `labbox/go` (Go 1.27.4, with a pre-warmed build cache:
  Go checks went from 28 s to under 1 s).
- Templates: `node`, `go`, `service-incident` and `preview-app` next to `python` and `java`; each passes
  `test-lab` (starter fails, solution passes).
- Lab specs (`specs/<lab>.yaml`) and `labbox new-lab --from-spec`: a lab folder from its template with
  chapter skeletons, `TODO(author)` markers and an `AUTHORING.md` checklist.
- `labbox validate` checks the content standard (story first, predict and recap per chapter, concept
  steps under 120 words, chapter length, cover, no `TODO(author)`) and refuses hints that contain a line
  of the solution. `--strict` makes every warning an error. It found three such hints in the existing
  labs, now rewritten.
- CI: GitHub Actions workflow (backend tests, strict validate, frontend build, `test-lab` on changed labs
  via `scripts/ci_changed_labs.sh`).

## Lab cover art

- Every lab card has a cover. Without its own image, a cover is drawn per lab: one of three colour pairs
  per track, an illustration per track (code window, stacked layers, database, containers, node graph,
  neural net, target) and a pattern seeded from the lab id, plus the lab's first tags. Works for any
  number of labs.
- Optional `cover:` in `lab.yaml` (svg, png, jpg or webp in the lab folder, up to 512 KB) for real
  artwork; served publicly at `GET /api/labs/{lab}/cover` with a sandbox CSP and nosniff.
- The language badge next to the card title is gone (the cover shows the tags).
- `scripts/labbox cover <lab> --generate` then `--pick N`: AI cover art (OpenAI `gpt-image-2` or Gemini) in one house style,
  neon isometric dioramas with colours per track, from a one-line `cover_scene` per lab; saved as a
  1200 px WebP. All five labs have a scene and an AI cover (gpt-image-2, picked from 3 candidates each);
  cards show covers at 3:2 so the whole diorama is visible.
- `scripts/labbox cover <lab> --query ...` then `--pick N`: stock photos from Pexels saved as the lab's
  cover with a `cover_credit` (photographer and link), shown as a small credit on the card.

## v2 Phase D: services, preview, live checks, incidents

**Engine**
- Labs with services: a private network per learner and lab (`labnet-u{id}-{lab}`, no internet unless
  the lab opts in), service containers reachable by name (`db:5432`) with the same limits as workspaces
  (uid 1000, no capabilities), readiness commands, data kept next to the workspace folder. Start, Stop
  machine, the idle reaper and Reset lab all treat the group as one unit. Service states show next to
  the machine status.
- Web preview: `/preview/{lab}/{port}/{path}` for HTTP and WebSocket, authenticated by a scoped,
  short-lived HttpOnly cookie; only the cookie owner's machine and only listed ports. A "waiting for your
  app" page retries by itself while the app starts. Preview tab with a path bar, reload and open in a new
  tab. nginx config includes `/preview/` (document: separate origin in production).
- Live checks (`check.mode: live`) in `labbox/checker:v1` on the lab network: learner code never runs
  in the checker, so fake results do nothing.
- Chapter setup: a root script from `/lab/setup/` runs once per learner per chapter (`POST
  .../chapters/{ch}/setup`, called by the lab page with a "setting up" banner). Migration `0005` adds
  `chapter_progress.started_at`; incident timers count from it and fixing inside the timer gives +25 XP.
- Resource tiers (`xs`, `s`, `m`, `l`). Layered base images: `labbox/base`, `python`, `java`,
  `checker`; both existing labs now build on them.
- `labbox test-lab` supports live labs (throwaway group, setup, fail, apply the solution, pass, clean up).

**New labs**
- `postgres-indexing-incident` (databases): a real Postgres with a million orders, an injected missing
  index, a 15 minute incident and a live check on the query plan and time (`@@METRIC lookup_ms`).
- `fastapi-first-api` (frameworks): a menu API for a chai stall, live in the Preview tab on port 8000.
- `spring-boot-first-api` (frameworks): a merchant API in Spring Boot, live on port 8080; Maven
  dependencies are baked into the image so builds work offline (checks have no network).

**Fixes found on the way**
- Postgres in a 512 MB container was killed by the kernel while building an index (default buffers plus
  parallel index workers). The lab tunes Postgres for small containers and gives it 768 MB.
- In live labs the task box and the check spinner no longer talk about "a clean machine".

**Tests**
- 9 new Docker tests (network and security of services, no internet, setup once, setup script hidden,
  fake result ignored, live pass after the fix, incident bonus and its timer, reaper and stop route stop
  the group with data kept, reset wipes data, preview auth, ports, isolation between users, WebSocket)
  plus schema tests and `test-lab` on all five labs. Old tests that listed exactly two labs now check
  that those two are among the labs.
- New browser test: FastAPI and Spring Boot in the Preview tab, the Postgres incident end to end.

## Home page

- New public home page at `/`: hero with a hand-built preview of the lab page, a demo predict question,
  how it works, why it sticks, the 7 tracks (live labs from the server, the rest marked coming soon) and
  a final call to action. Works in both themes and down to phone width.
- Logged-in visitors see **Continue learning** instead of Log in / Start free. An expired login no
  longer sends visitors of public pages to the login screen.
- **Start free** opens the login page in sign-up mode (Enter signs up, "Create your account"); the login
  page links back home.
- New public `GET /api/catalog` (titles and catalog fields only), with a test that nothing hidden leaks.
- Page description and sharing tags in `index.html`, and a `robots.txt` that keeps private pages out of
  search engines.
- Lighthouse on the production build: performance, accessibility, best practices and SEO all 100, in
  dark and light. New browser test for the home page.
- No prices, testimonials or user numbers on the page (none of them exist yet).
- Below the hero: a product showcase in the hero's window frames, alternating sides. Predict (the demo
  question, live), Check (Expected vs Got), Hints (the ladder) and Habit (streak, XP, level and a mini
  skill map). Then the tracks as chips with a live count, and the final call to action.
- Logo: a rounded accent box with a shell prompt (`>_`) plus the LabBox wordmark, in every top bar, on
  the login page and as `favicon.svg`.

## v2 Phase C: XP, streaks, levels, onboarding, skill map, daily drill

**Learner-facing**
- XP for first passes (lowered by hints), first-try predicts, completed chapters and labs, and the daily
  drill. A "+N XP" toast after each award.
- Levels (level 2 at 100 XP, level 3 at 283, then `100 * (N - 1)^1.5`), shown as a badge next to the
  username. 🔥 streak and ⭐ XP in every top bar.
- Streaks counted in the learner's own timezone: a day counts at 20 XP, today never breaks it, one
  freeze per week covers a single missed day.
- Onboarding for new accounts: pick a goal, answer 3 placement questions, then land in the first lab
  with the editor open on its starter file. Goals without labs yet say so and start from Python Basics.
- Daily drill on the labs page: one multiple choice question per day, checked on the server, +20 XP,
  enough to keep the streak on a busy day.
- Skill map page (`/tracks/languages`, React Flow): nodes light up when their chapters are complete.
- The labs page shows level progress, streak, today's XP and the skill map; the recap card shows the XP
  from the chapter, the streak and the level.
- The lab page opens the first file by itself.

**Backend**
- Migration `0004`: `user_profile`, the `xp_event` ledger (unique per user and ref), `drill_answer`.
  Every existing user gets a profile marked as onboarded; their earlier progress becomes XP once.
- `app/engagement.py` (rules as pure functions plus the ledger), `app/drills.py`, `app/content.py`
  (skill maps, drills and onboarding, validated at start-up), `routers/engagement_routes.py`.
- Check and predict responses include `xp_awarded`; chapter progress includes `xp_earned`.
- `labbox validate` also checks tracks, drills and onboarding.

**Content**
- `tracks/languages.yaml` (7 skills), 14 drills in `drills/`, `onboarding/onboarding.yaml`.

**Tests**
- 27 new backend tests, including fixed-clock streak and timezone tests (midnight in India against UTC,
  timezone changes, freezes per week), no double payouts, backfill, drill, skill map, onboarding and
  broken content. A real Docker Check awards XP once.
- New browser test: onboarding to an open editor, drill to streak 1, chapter to a lit skill node.
- Lighthouse accessibility 100 on the labs page, the lab page and the skill map.

**Not built (as agreed)**
- The share card image and public profile page (section 5.5), the incident timer bonus (needs Phase D),
  leagues and events (section 5.6).

## v2 Phase B: content format v2, authoring CLI, solutions

**Content format**
- `lab.yaml` v2 fields (all optional, v1 files unchanged): `version`, `subtitle`, `track`, `tags`, `level`,
  `estimated_minutes`, `free_chapters`, `prerequisites`, `story`, chapter `minutes`. The labs page shows
  track, level and minutes.
- Engine fields from the v2 spec (`services`, `preview`, `llm`, `runtime`, live checks, chapter `setup`,
  `network: lab`, `sudo`, tiers, `disk_mb`) are part of the schema but refused with a clear "needs
  Phase X" message until that phase is built.
- Both labs upgraded to v2 metadata (track, level, minutes, story).
- `@@METRIC` lines are parsed into `metrics` on the check response and listed in the results drawer.
  `@@RESULT` is unchanged.

**Predict answers on the server**
- The chapter response no longer contains predict answers or explanations, in `steps` or in the raw
  `markdown` (answers unticked, `:::explain` removed).
- New `POST /api/labs/{lab}/chapters/{ch}/predict` checks an answer and returns the explanation once it
  is right. Every attempt is stored (`predict_answer` table, migration `0003`), and the progress route
  returns them, so answered predicts stay answered after a reload.
- New `GET /api/labs/{lab}/chapters/{ch}/outline` returns `{steps: [{type, title, task}]}`.

**Authoring CLI** (`scripts/labbox`, code in `tools/labbox_cli.py`)
- `new-lab` (python and java templates), `validate`, `test-lab`, `preview`.
- `test-lab` grades `starter/` and `solution/` with the same function every Check uses
  (`checker.check_folder`, split out of `run_check`).
- Both labs have a `solution/` folder; `.dockerignore` keeps `solution/` and `tests/` out of images.

**Tests**
- 36 new backend tests (v2 schema, refused features, redaction, predict and outline routes, metrics,
  solution privacy, CLI validate and new-lab, test-lab on both labs and on a wrong solution).
- The browser test also checks the page has no predict answer before answering, and that an answered
  predict survives a reload.

## v2 Phase A: lesson experience redesign

Lessons are now shown one step at a time instead of one long page.

**Learner-facing**
- New lab page layout: a step card on the left (progress dots, Back / Continue, arrow keys), tasks and
  Check below it, files and editor on the right, and Terminal / Output tabs at the bottom.
- Step types: story (character and mission), concept, example, predict (multiple choice with an
  explanation), try, task, incident, recap and deep-dive. Tips, warnings, "why this matters" and
  "common mistake" callouts.
- Code blocks have a language label, Copy, and (for ` ```bash run `) Run in terminal, which pastes the
  command and focuses the terminal without pressing Enter.
- Hint ladder: up to 3 hints per task, revealed one at a time from the server. Each hint lowers the task's
  XP (100%, 80%, 60%, 40%).
- Check results slide up in a drawer: "2 of 3 passed", the message per failed task, and Expected vs Got
  side by side when the check reports them. Confetti once when a chapter is fully passed, then the recap.
  "Ask the tutor" is shown but disabled until the tutor exists.
- Dark theme by default with a light theme; Inter and JetBrains Mono bundled with the app; focus mode
  hides the file tree. Step position (per user, on the server), panel sizes, theme and focus mode are
  remembered.
- Both labs' chapters rewritten in the step format (9 and 8 steps) with a story, a predict question and
  3 hints per task.
- Lighthouse accessibility on the lab page: 100 in both themes.

**Fixes**
- The terminal showed two prompts after Stop machine / Start machine: the old session's last prompt stayed
  on screen and the new shell's prompt was printed next to it. The terminal is now cleared when a new
  shell session connects.
- The terminal no longer grabs keyboard focus when it connects, so arrow keys move between steps until
  you click into the terminal.

**Backend**
- Alembic migrations. `0001` is the POC schema (existing databases are stamped, data untouched), `0002`
  adds `chapter_progress` and `task_progress`.
- `lab.yaml` tasks take optional `hints` (max 3) and `xp` (default 20). v1 files load unchanged.
- Chapters are split into steps on the server (`app/lessons.py`); a chapter without step markers is one
  step. Broken steps or steps pointing at unknown tasks stop start-up with a clear error.
- `GET /api/labs/{lab}/chapters/{ch}` also returns `steps` (the `markdown` field is unchanged).
- New: `GET` and `PUT /api/labs/{lab}/chapters/{ch}/progress`,
  `POST /api/labs/{lab}/chapters/{ch}/tasks/{task}/hint`. Lab detail tasks also return `xp`,
  `hint_count` and `hints_used`.
- `@@RESULT` accepts optional `expected` and `actual`; both labs' checks now send them.
- Each Check records the latest pass and the first pass time per task (`task_progress`), ready for XP.

**Tests**
- 25 new backend tests (lesson parsing, v1 compatibility, migrations and model drift, progress and hint
  API, expected/actual in a real check). All 40 POC tests still pass.
- Playwright browser test (`npm run test:e2e`) for the full lesson flow, including the double prompt fix.
