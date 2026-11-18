# Changelog

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
  1200 px WebP. All five labs have a scene.
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
