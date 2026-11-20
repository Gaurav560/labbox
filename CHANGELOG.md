# Changelog

## Fix: the rate-limiter lab's load checks were borderline by design

- Both checks average over a 3-second run, but a run rarely starts on a whole second, so it touches 4
  one-second windows: a correct solution may let up to 4/3 of its limit through (66.7 a second for the
  global 50, 13.3 for alice's 10). The cut-offs were 60 and 14, so the solution failed whenever the run
  started early in a second. The cut-offs now come from that worst case plus a small margin (69.7 and
  14.3). Broken solutions still fail clearly (80 a second with no global limit, 20 for alice when each
  server counts on its own). Starter fails and solution passes, 5 runs out of 5.

## Fix: the worker's schedule is in UTC

- arq reads cron times in the machine's own zone unless told otherwise, so on this laptop (India time)
  the "21:00 UTC" backup was set for 21:00 India time and the daily image check for 03:00 India time.
  `WorkerSettings.timezone` is now UTC: the backup runs at 21:00 UTC, which is 02:30 in India, as
  documented. A test pins it.

## Phase H5: safety limits

- `app/limits.py`, every limit a setting (0 turns it off):
  - Disk: a learner's own files, all labs together, up to 500 MB; each lab's databases up to 1 GB
    (seeded lab data such as the 316 MB Postgres incident data does not count against the learner).
    Over it: the machine stops, starting and saving are refused, deleting and Reset lab still work.
  - At most 2 running labs per learner: starting a third stops the least recently used one.
  - A machine running 4 hours stops; one using all its CPU for 10 minutes (an endless loop) stops.
    CPU comes from the kernel's per-container counters, compared round by round.
  - Per-address limits: 60 sign-ups an hour, 30 wrong passwords a minute (10 per username), 120
    checks a minute. Only wrong passwords count, so logging in often is never slowed down.
- The reaper's round enforces them; a stopped machine keeps its files and the lab page shows why it
  stopped, with a Start machine button (`stopped_reason` in the workspace status, additive).
- This laptop has no filesystem quotas, so disk is measured each minute; hard XFS quotas on the server
  are on the pre-launch list.
- Tests: 240 passed on Postgres and Redis; 236 on SQLite plus the rate-limiter lab's load test, which
  sits right at its 60-a-second cut-off and fails when the machine is busy (it passed on rerun with
  every limit on and with each switched off; not caused by H5). 14 browser tests pass on 4 workers.

## Phase H3: background worker

- `app/jobs.py` with three jobs, scheduled by arq in `app/worker.py` (a second process, needs
  `REDIS_URL`; arq runs each scheduled job once even with several workers or servers):
  - images (at start, daily): every image the labs use is here; public ones are pulled when missing,
    unbuilt lab images are reported. 21 images on this laptop, all present.
  - networks (at start, hourly): removes lab networks that no container of that lab group uses, running
    or stopped, older than an hour, under the machine's lock. On this laptop: 85 networks, all in use.
  - backup (nightly, 21:00 UTC): `pg_dump` in a container of the server's own Postgres version into
    `/srv/labbox/backups` (owner-only), checked with `pg_restore --list` before it is kept, newest 14
    kept; SQLite gets a checked copy. The first backup was restored into a scratch database: every row
    count matched the live one (393 accounts, 496 workspaces, 854 XP events).
- `scripts/labbox jobs` shows when each job last ran; `--run <job>` runs one now.
- `deploy/labbox-worker.service` for a server. Tests use their own backup folder, never the real one.
- Tests: 232 passed on Postgres and Redis, 229 (plus 3 skipped) on SQLite.

## Phase H2: Redis for shared state, several workers

- `app/shared.py`: what the backend used to keep in one process now lives in Redis when `REDIS_URL` is
  set (in memory without it, exactly as before): the lock on each lab machine (start, stop, reset,
  chapter setup), the one-check-per-learner slot, the AI requests-per-minute counters and the reaper's
  lease (one worker reaps; another takes over within three rounds if it dies). Locks free themselves if a
  worker dies and are renewed while the work runs.
- The first copy of a lab's starter files now happens under its own lock: with two workers, both first
  requests copied the files at the same moment.
- Every worker serves the AI gateway on port 9000 (`SO_REUSEPORT`); migrations wait their turn on a
  Postgres advisory lock when several workers start at once.
- Lite editor: the file asked for last is the one shown, so the chapter's file is not replaced by the
  first-file open when the two answers come back in the other order.
- `deploy/labbox.service` runs 4 workers (needs `REDIS_URL`), and the dev app does too: `REDIS_URL` was
  appended to `backend/.env` with the owner's OK.
- If a page's code fails to download (Chrome drops downloads when the network changes; after a deploy the
  old files are gone), the app tries again and then reloads the page once, instead of staying blank.
- Tests: `LABBOX_TEST_REDIS_URL` runs them on Redis (a database other than 0). Checked with 4 workers on
  Postgres and Redis: all 14 browser tests pass; a killed worker is replaced and the reaper moves to a
  live worker. Backend: 226 passed on Postgres and Redis, 224 (plus 2 skipped) on SQLite.
- Fixed a test bug from H1: on Postgres, test accounts got ids 1, 2, 3, so the Docker tests reused the
  machine names of real dev accounts (id 1 is the owner's). No files were changed (checked), but 23
  machines and 8 networks pointed at deleted test folders; they were removed with the owner's OK. Test
  account ids now start at a random 8-digit number on both databases.

## Phase H1: Postgres

- `scripts/devdb.sh`: LabBox's own Postgres 16 and Redis 7 in Docker, on localhost only and on their own
  ports (55432, 56379), so they never clash with a Postgres or Redis already on the machine. The password
  is made once at random (`/srv/labbox/devdb.password`, only the owner can read it); `devdb.sh url`
  prints the lines for `backend/.env`.
- The backend runs on Postgres when `DATABASE_URL` points at it (`psycopg` 3 driver, a pool with
  pre-ping). Without it, SQLite as before. All migrations run unchanged on Postgres.
- `scripts/labbox db-copy`: copies SQLite to an empty Postgres, table by table in foreign-key order,
  keeps the ids, moves the id sequences past the highest copied id, and compares row counts. The source
  is opened read-only, and targets that already hold rows are refused. A practice copy of the dev database
  moved 3054 rows in 11 tables with every count matching and the SQLite file byte for byte unchanged.
- Tests stay on SQLite; `LABBOX_TEST_DATABASE_URL` runs the whole suite on Postgres (only a database
  named `*_test`). Both runs green: 219 passed on SQLite (plus 1 Postgres-only test skipped), 220 on
  Postgres.
- Switched the dev app over (owner's OK): backend stopped, 3054 rows copied with every count matching,
  `DATABASE_URL` appended to `backend/.env` (the old SQLite line stays above it; delete the new line to go
  back), SQLite kept as `/srv/labbox/labbox-sqlite-before-h1.db`. All 14 browser tests pass on Postgres;
  new accounts continue at id 319.

## Home: fresh lab screenshots, now from all 16 labs

- All shots retaken with the current lab page (task stepper, icon Hint and Ask AI, Aa menu), and five
  labs added: Spring Boot, Express, FastAPI, Java basics and Python basics. 26 shots in all.
- `tools/home-shots.mjs`: an optional wait per shot (Spring Boot needs its build to finish), and it
  types the file name into VS Code's Quick Open box itself, never into the editor that the chapter
  now opens on its own.

## Home: the screenshot frame glows in the lab's own colour

- The glow and border around the "Inside a lab" screenshot follow the lab shown: Redis red, Spring
  green, Postgres blue, Go cyan, Java orange, and so on (`TONES` in `HomeSections.tsx`, taken from each
  lab's cover; dark covers use their bright accent). A new lab without a colour falls back to red.

## Home: a cleaner, smoother FAQ section

- The heading and a short line with the contact address sit on the left (they stay in view while you
  scroll); the 8 questions run down the right as one numbered list with thin dividers.
- Answers slide open smoothly, the round + turns into an x, the open row gets a red edge and a faint
  glow, and only one answer is open at a time (`details name`). Motion is off for reduced-motion users.

## Lab page: a calmer task area, and each chapter opens its own code

- The task area is a quiet stepper: "Task 1 of 3", one dot per task (a pill for the current one, green
  when passed), and the task's real title instead of its id. Check is the one big button; Hint (with
  the hints left as a small badge) and Ask AI are icon buttons beside it.
- Switching chapters opens that chapter's code: the learner's files stay, and the chapter's file opens
  at its section (Redis chapter 6: `app.py` at `# ---------- chapter 6`). It finds the TODO that names
  one of the chapter's tasks, else a `chapter <n>` marker, else the README, else the first TODO
  (`backend/app/focus.py`, route `POST /api/labs/{lab}/chapters/{chapter}/focus`). Works in Lite and in
  real VS Code: the `labbox-defaults` extension (now 1.3.0, with a small `extension.js`) opens the file
  the backend names in `/tmp/labbox-open.json`. On another server, run `scripts/openvscode.sh` once.

## Lab page: text size per area (the Aa menu)

- An **Aa** button in the lab's top bar opens "Text size": presets **S / M / L / XL** (90, 100, 115,
  130%) and a slider per area from 80 to 150%: **Lesson**, **Tasks** (task cards, incident pagers,
  the task bar, the tutor), **Code editor** and **Terminal**. Reset goes back to 100%. Saved on this
  device (`labbox.textSize`).
- Lesson and tasks resize at once (CSS zoom), and so do the terminal and the Lite editor. Real VS Code
  reads font sizes only when it starts, so a new size reloads the IDE frame (files and tabs stay); the
  sizes reach it through the start page (`lb_fs`, `lb_ts`).
- VS Code's font sizes are no longer fixed in the machine `settings.json` or the `labbox-defaults`
  extension (now 1.2.0), which would have overridden the learner's choice. On another server, run
  `scripts/openvscode.sh` once to install the new extension.

## Home page: a different real lab on every visit

- "Inside a lab" now picks one of **21 real screenshots** at random on each page load: 12 labs, from
  Redis caching and the Postgres checkout incident to the rate limiter's load balancer, a Go till, a
  git history graph and Linux logs. The window title names the lab and chapter.
- `frontend/tools/home-shots.mjs` captures them (demo learner `riya`, a fresh browser profile and a
  reset per lab, a real terminal command each); `frontend/tools/home-shots.py` turns them into
  `public/images/labs/*.webp` (about 110 KB each, only one is loaded) and `src/homeShots.json`.
- IDE: VS Code no longer offers to install "recommended" extensions (there is no marketplace in labs,
  so the Install button led nowhere).

## Home page: a real lab screenshot and a calmer AI track

- **Inside a lab** is now one large, real screenshot of a lab (Redis chapter 6: the lesson, VS Code
  with `app.py`, a terminal talking to a live Redis) in a framed window with a soft red glow, and
  under it six features, each an icon, a title and one sentence. The six dense mock cards are gone.
- **AI labs**: four quiet stage cards (a large faint stage number, the title, one sentence, "6 labs"
  with three example labs and "+ 3 more") instead of four numbered lists of all 24 labs.
- Fix: leaving a chapter while its setup was still running left the "Setting up this chapter" banner
  and a disabled Check button behind for good.

## Home page: AI labs first, "Inside a lab", FAQs above the footer

- Positioning: LabBox is marketed as AI labs, with system design, languages, databases and DevOps
  around them. Hero: "Learn AI by building it, not watching it." The pill says "AI track launching",
  honestly, because no AI lab is live yet.
- "How a lab works" (predict, checks, hints, streaks) is replaced by **Inside a lab: not exercises,
  real systems.** Six cards, each with a real artifact: a model call with its `lab requests` cost
  table and a grounded JSON answer, load-test gauges, a live incident pager, the tutor asking
  instead of telling, a graded design review, and your own machine's services.
- New **AI labs** section: the planned 24-lab track in four stages (Foundations, Retrieval, Agents,
  Production), marked "Launching". The other tracks follow as "Also on LabBox".
- **FAQs** as a section just above the footer (two AI questions plus the main ones, "All questions"
  links to /faq); the home footer no longer links to the FAQ. New meta description and page title.
- The IDE has no extension marketplace any more (read-only extensions, no confusing search).

## Redis in practice, block 3: production Redis (chapters 9 to 13)

- 9. **Streams and consumer groups:** why pub/sub loses messages; an order stream; a kitchen group
  that acknowledges work; reclaiming a crashed worker's payments with `XAUTOCLAIM`. Go deeper:
  trimming, at-least-once delivery, poison messages, when Kafka fits better.
- 10. **Memory and eviction**, a timed incident: Redis at its 64 MB limit refuses writes with the real
  OOM error. Find the runaway key (`--bigkeys`, `MEMORY USAGE`) and remove only it; choose a
  `volatile-*` policy (an `allkeys-*` policy is refused: it may evict carts and sessions).
- 11. **Persistence:** someone switched durability off; enable AOF with `everysec`, take a fresh
  `BGSAVE`; a graded design review on RDB plus AOF and on `appendfsync always`.
- 12. **Replication and clusters:** a second Redis server (new service `replica`) becomes a live
  replica (`REPLICAOF`); customer 42's cart and wishlist named with a hash tag so a cluster keeps them
  in one slot (the check computes real cluster slots: 10688 and 6132 without the tag, 4672 with it).
- 13. **Capstone, production is slow:** the ops dashboard's `KEYS` replaced with `SCAN` (verified with
  `INFO commandstats`), the culprit found in `SLOWLOG` and removed with `UNLINK` (a blocking `DEL`
  shows up in the slow log and is refused); a final graded design review.
- Fixed while testing: Redis checks `maxmemory` only when a script starts, so the incident fill runs in
  batches (one script filled 200 MB and the container was killed); the replica gets a writable `--dir`
  and the primary `--repl-diskless-sync-delay 0`. Verified tempting wrong answers fail with the right
  lesson. The course: 13 chapters, 32 tasks, 4 graded design reviews, about 5 hours.

## Redis in practice, block 2: Redis inside a real app (chapters 5 to 8)

- 5. **Redis from Python:** the client and its connection pool, strings back from Redis, `{}` for a
  missing hash; a profile API from a hash; a 2000-row import made fast with a pipeline. The check
  counts round trips (Redis's `total_reads_processed`): one by one is about 2000, a pipeline about 5.
- 6. **Caching for real:** cache-aside with a TTL, invalidation on a price change (delete, do not
  update), and a cache stampede: 30 requests at once on an empty cache must make at most 2 calls to
  the slow billing system (`SET NX` with a TTL). Go deeper: jitter, early refresh, negative caching.
- 7. **Atomic operations:** check-then-act races; the OTP limiter; loyalty redemptions made atomic
  with a Lua script (20 redemptions at once from 500 points: exactly 5 succeed, balance 0).
- 8. **Distributed locks:** `SET NX PX` with a token; 30 people booking one table at once, exactly one
  wins; release only your own lock (compare and delete in Lua); a graded design review on lock
  expiry during slow work, failover, and fencing tokens.
- The app's TODOs follow the chapters; every check exercises the running app with real concurrency.
  Verified on the running starter: each task fails for its intended reason (2000 round trips, 30
  billing calls, 20 redemptions, 30 bookings, a stolen lock). 21 tasks in 8 chapters, about 3 hours.

## The Labs page uses the home page's tiles

- After login, labs were shown as heavier cards (paragraph, three chips, a progress bar, an Open
  button) that did not match the home page. They are now the same tiles as the home page grid: the
  cover, the title, one quiet line (track, level, minutes), the whole tile clickable, plus a thin
  progress line ("2 tasks · 1 chapter", "1 / 3 tasks", or "✓ Done"), aligned at the bottom.
- The rate limiter's cover is now nginx with Redis, so it no longer looks like the Redis lab.

## One logo colour everywhere

- The LabBox mark took the page's accent colour: red on the home page, blue on the login page, white
  in the app. It now always uses the brand red (`--brand-red`: `#d1605a`, `#b8463f` in light mode)
  with a white prompt, and the favicon is red too.

## Redis in practice, block 1: from zero (chapters 1 to 4)

- The Redis lab becomes a course from "what is Redis" to production. Block 1, the beginner chapters:
  1. **What Redis is:** a shared dictionary in memory; `SET`, `GET`, `DEL`, `EXISTS`; atomic
     counters (`INCR`, `DECRBY`) and the race condition they prevent; key naming; `SCAN` not `KEYS`.
  2. **Keys that expire:** `EX`, `EXPIRE`, `TTL` (-1 and -2), `PERSIST`; plain `SET` dropping a
     timer and `KEEPTTL`; sliding sessions; how Redis actually expires keys.
  3. **Hashes and lists:** a menu and a customer profile as hashes (`HINCRBY`), why a hash beats a
     JSON string, a first-in first-out order queue, and why `LMOVE` keeps work safe.
  4. **Sets and sorted sets:** unique visitors, `SINTERSTORE`, a live leaderboard, and HyperLogLog
     for counting distinct visitors in 12 KB.
  Each chapter: story, concept cards under 120 words, a guess, a try, 3 tasks, a "Go deeper" card
  for experienced engineers, a recap. 12 new tasks, each with a 3-step hint ladder.
- Chapter setups seed real data to work on (bean stock, leftover temp keys, a session without a
  timer, a promo about to expire, two outlets' customers). Checks read the real Redis and refuse
  shortcuts (deleting the stock, overwriting the session, changing the outlet sets).
- The caching and rate limiting chapter stays as chapter 5 until blocks 2 and 3 replace it.
- The chapter shape test now checks the spec's rule (1 to 3 concept or example steps, at most 4
  tasks) instead of a 9-step cap. Task cards in live labs no longer say "fix the running system".

## Phase G, step 5: the system-design template

- `scripts/labbox new-lab <id> --template system-design`: two app copies behind nginx (service `lb`),
  Redis, a k6 live check with gauges and a graded design review, based on the rate-limiter lab, built
  from `labbox/python:v1` only. A lab made from it builds and passes `test-lab`.

## Phase G, step 4: the rate-limiter lab (lab 16)

- New lab `rate-limiter` (system-design, intermediate, 2 chapters). The learner's FastAPI app runs as
  two copies (`bash run.sh`, ports 8001 and 8002) behind a real nginx load balancer
  (`nginxinc/nginx-unprivileged`, service `lb`, resolving the workspace per request so it can start
  first), with Redis. The starter's in-memory limiter lets a client through at about twice its limit.
- Chapter 1: a per-key limit in Redis across both copies. Chapter 2: a global limit, then a design
  review (Redis down, why two servers broke it, bursts at window edges) graded with `tests/rubric.yaml`.
- The live check runs k6 through the load balancer with fresh API keys each run: one key at 30
  requests a second must get about 10 through while another at 4 a second is never blocked, p95
  under 50 ms; ten keys at 80 a second in total must be held to about 50. Gauges show the rates and
  latency. Verified: the running starter fails with "got 23 a second through. Each server counts on
  its own"; a half solution passes chapter 1 only.
- System design skill map (`tracks/system-design.yaml`). The home page grid stays at 15 cards; the
  lab is in the catalog. Browser test for the design review (answers, scores, feedback, reload).

## Phase G, step 3: design review steps, graded against a rubric

- New step type `design`: 1 to 5 short written questions (`:::ask{id=...}` blocks), with a rubric in
  `tests/rubric.yaml` that never reaches the browser. The tutor model grades each answer, asking for
  JSON; replies are matched to the rubric and clamped (a model cannot give more points than a
  criterion has, or invent criteria), a bad reply is retried once, and if grading still fails the
  learner sees "could not grade right now" instead of a made-up score. Answers under 20 characters
  are scored 0 without a model call.
- Every attempt is stored in the new `design_answer` table (migration 0007, additive) and the last
  one comes back with the chapter progress. +30 XP once, at half the points; never blocks completion.
- `POST /api/labs/{lab}/chapters/{chapter}/design`; the lab page shows the questions, a score per
  question and a line of feedback per rubric point, and lets the learner improve and resend.
- `labbox validate` refuses a design question without criteria. Tests with a scripted fake model.

## Phase G, step 2: gauges for check metrics

- `@@METRIC` values are now gauges in the results drawer: a bar for the value and a tick for the
  target, green when met, red when missed, grey without a target. Friendly names and units for the
  usual metrics (`p95_ms` is "p95 latency, ms", `error_rate` is "errors, %", `rps` is
  "throughput, req/s"). The Postgres incident browser test checks the gauge turns from red to green.

## Phase G, step 1: load tests in checks (k6)

- The checker image now has k6 v0.55.0 (Grafana's load tester, copied from the `grafana/k6` image)
  and `labbox_k6`, a small helper for live checks: `labbox_k6.run(script, env)` runs a k6 script and
  returns p50, p95, p99 and max latency, requests, requests per second, error rate, and every custom
  counter; `labbox_k6.report_metric(name, value, target, better)` prints the `@@METRIC` line.
- Docker test: a 40-request load test against a tiny server inside the checker, as uid 1000 with no
  capabilities.

## The lab's logo behind the lesson

- Every lab shows its own technology logo (from its cover: Redis bricks, Python snakes, Duke for Java,
  the Git mark...) very faintly behind the lesson, large, low on the right and slightly tilted, with
  a soft glow of the brand's colour from the top-right corner. Pure CSS in the lesson panel, behind
  every card and never clickable; about 6.5% opacity (7% in light mode). No animation.
- `frontend/src/brand.ts` picks the logo from the lab's cover credit and the colour from the same
  brand palette as the covers. The Duke, SQL, Express and Nginx logos were added to `public/logos`.

## A premium IDE: LabBox Dark, JetBrains Mono, IDE | Lite

- "LabBox Dark", a VS Code colour theme in the labbox-defaults extension (now 1.1.0): the app's greys
  around the code, GitHub's code colours (purple functions, orange types and parameters, red keywords,
  blue strings), a green accent on the active tab, activity bar and badges, white buttons.
- JetBrains Mono (OFL) inside the IDE's editor and terminal: `scripts/openvscode.sh` copies the font
  files to `/srv/labbox/openvscode/fonts`, the backend serves a fixed list of them at `/ide-fonts/`, and
  the proxy adds the `@font-face` rules to the IDE's start page.
- A machine whose IDE is already running restarts it when the shared setup changes (new extension,
  theme or settings), so everyone gets updates without a Reset.
- The switch now reads "IDE | Lite" ("VS Code" is Microsoft's trademark; the IDE is OpenVSCode
  Server). Screens under 900px always get Lite.

## Typing in VS Code keeps the machine awake

- The idle reaper only saw plain HTTP requests through the proxy, not websocket traffic, so a learner
  working only in VS Code could have their machine stopped after 15 minutes. Browser-to-machine
  websocket messages of 64 bytes or more now count as activity (at most one database write a minute);
  smaller keep-alives do not, so an abandoned tab still lets the machine stop. Test added.

## VS Code: upgrade machines made before it

- Machines created before VS Code was set up had no VS Code mount, so VS Code could not start in them
  ("VS Code is taking longer than usual to start"). Opening VS Code now recreates such a machine (and
  gives a no-network lab its private network): `/workspace` lives on the host, and the learner's home
  folder is copied into the new machine, so nothing is lost. Docker test added.

## Real VS Code in the lab

- Labs now open in real VS Code: openvscode-server (Gitpod's open-source VS Code, MIT) runs inside the
  learner's own machine, as the learner, and shows in the editor area through the signed-in proxy at
  `/ide/{lab}/` (HTTP and websockets). Explorer, tabs, command palette, VS Code's terminal, and Python
  IntelliSense from the free Python extension (Open VSX). A "VS Code | Classic" switch in the bottom
  bar goes back to the built-in editor (which keeps AI completion); Classic reopens files fresh.
- `scripts/openvscode.sh` downloads it once to `/srv/labbox/openvscode` (mounted read-only into every
  machine, so no image rebuild) with the Python extensions and `labbox-defaults`, a tiny extension of
  default settings (`tools/vscode-defaults`).
- Defaults (Dark Modern, 15px, auto-save so Check sees the latest code, no telemetry, no workspace
  trust prompt, no Copilot chat panel) are added to VS Code's start page by the proxy, early enough
  for workspace trust.
- VS Code starts only when the lab page opens it (Classic users never pay for it); each machine gets
  `IDE_EXTRA_MEMORY_MB` (512) more memory while it is on; a per-user, per-lab connection token, so
  requests that skip the proxy are refused; labs without a network get a private one (still no internet).
- Found while testing: Docker's default address pool gives every lab network a /16 and runs out after
  about 30 networks ("all predefined address pools have been fully subnetted"). Lab networks now get a
  /28 each from `LAB_SUBNET_POOL` (10.88.0.0/16): room for 4,096.
- Tests: `test_ide_docker.py` (proxy, defaults, learner user, no capabilities, read-only mount, token,
  isolation, private network and subnet) and a browser test for VS Code and the switch. The older
  browser tests pin the classic editor.

## A VS Code-style editor

- Code at 15px JetBrains Mono with ligatures and a 24px line height, GitHub's code colours (red
  keywords, blue strings and numbers, orange types, purple built-ins, italic comments) on the app's
  greys, and VS Code's gold, purple and blue bracket pairs.
- Minimap, indent and bracket guides, sticky scroll, smooth cursor and scrolling, Ctrl+wheel zoom.
- Tabs with file-type icons, a green top line on the active tab and VS Code's dirty dot; the same
  icons in the file tree; a breadcrumb path above the code; a status bar with save state, line and
  column (and selection size), spaces, encoding, language and the AI on/off switch.
- A friendlier empty state with the shortcuts when no file is open.

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
