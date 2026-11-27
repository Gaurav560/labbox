# Changelog

## 27 November: the FDE spotlight, picture first; compact AI rows with a Micro tag

- "Before you start" on Ukiyo course pages in two soft reds (owner: "two tone shallow red"): a pale red wash, a bar that
  fades from red, light red check boxes with a red tick and red links. The sign-in buttons are back to plain boxes (owner:
  "earlier one was good").
- Once the home page's machine is running, it offers the next two labs to spin up ("Your LangChain machine is ready.
  Spin up another:" with `docker run spring-ai` and `docker run rag` buttons), so visitors find the other labs by
  playing (owner: "how do I show there are other labs to test via a Docker container").
- Ukiyo's FDE spotlight shows a real print, not AI art (owner: "try this"): Utagawa Hiroshige, View toward Kasumigaseki
  in Edo, about 1830 (public domain, Wikimedia Commons), wide so the whole print shows. The lab picker is a dock of logos.
- The hero wave is the plain picture in both themes: no animation, no fade, no border (owner: "only the normal image").
  (A two-layer animation was tried the same day and removed.)
- Ukiyo's hero shows the wave (owner: "yes, build on Ukiyo"): "The AI wave is here. Learn to ride it." beside the engineer
  riding a wave of light, large and wide, with no frame; its edges fade into the page (a short fade in the light
  theme). The typing terminal is gone. The FDE spotlight now shows "Summit" (an engineer on a peak at dawn, lines of
  light to the city). The start-a-lab heading is short: "One click. Your lab is ready." The note under the share
  options is gone (both designs).
- "Explore more AI labs" heads the rows under the FDE spotlight; the FDE tag line "The hottest job in AI." is red;
  the share options are one quiet line of coloured marks and names (owner: "try something else"); a little more space
  between the certificate's date, stamp and QR code.
- The certificate section's share options are a ruled grid of three columns, each the platform's mark in its own
  colour and its name, instead of round buttons (owner: "some other design, not circular").
- The FDE tag line is now just "New · The hottest job in AI." (owner: "remove learn it by doing it").
- Premium Reads: Tech blogs first, then Research papers, then Books; Tech blogs open by default (owner).
- "Lab", not "course", in visitor-facing text (owner): the Premium Reads page ("behind every LabBox lab", "the books
  our labs are built on"), the home page's AI section ("Each AI lab", "New lab", "AI labs live") and master's hero pill.
- The "start a lab" picker is a printed index under "Pick a lab to try": three ruled columns, each cell a logo on paper,
  the lab's serif name and an arrow on hover; the picked one has a vermilion bar and a soft tint (owner: "some learners
  will miss that these are real buttons"; round buttons "look out of this page"). The FDE "New" label is red again. The red line under the machine's lid shows
  before Run too (owner: "keep it").
- Ukiyo's "AI labs" menu link jumps to the home page's AI section (smooth scroll, below the sticky header) instead of
  the AI labs list (owner, 27 November).
- Pricing: the Teams plan is greyed out, and Pro's button reads "Join the waitlist" (owner, 27 November).
- The certificate's share picture (LinkedIn, X, WhatsApp) has the same round stamp as the page, drawn in Pillow, between
  the date and the QR code, which moved to the corner; the lab's name on it is upright (owner: "yes, update the stamp").
- Wording: nothing says "on your own machine" any more (owner: "this is wrong wording"; the machine runs on LabBox and
  opens in the browser). Ukiyo's hero line: "Build real AI apps in your browser. A lab machine with an editor, a
  terminal and real models is ready in about a minute."; the AI lead, course pages, pricing and FAQ say "a lab machine
  in your browser". The FDE button reads "Explore the lab" ("Open the lab" when signed in).
- Certificates: the share list shows each platform's logo in its own colour with the name under it, no boxes (owner:
  "logos"); the "One click to LinkedIn" point is gone. The little LabBox square became a round rubber stamp on the
  certificate (owner: "this style"): two rings, LABBOX BY TELUSKO over the top, HANDS-ON LAB along the bottom,
  COMPLETED and the year across the middle, slightly worn ink, upright, between the date and the QR code. The lab's
  name on a Ukiyo certificate is upright, not italic.
- The AI section's lead no longer counts the courses (owner: "remove 6"): "Each AI course is a real build on your own
  machine: model calls, RAG search, agents and evals, through the LabBox gateway."
- Ukiyo's AI rows hover calmly (owner: "the colour i dont like"): no fill and no shift; the picture lifts a little,
  the arrow moves and a thin gold line draws in under the row.
- The claim email demo is off for now (owner: "remove this email animation for now"); the spotlight's big picture
  takes its place on the right, with no caption on it. Beside it only the tag line, the course name and the button
  remain (owner: the description and the chapters, tasks and hours line are gone too). The tag line
  reads "New · The hottest job in AI. Learn it by doing it." (picked by the owner), large and in the
  hero's voice, on two lines: the first in ink, the second in italic (Ukiyo: indigo; master: yellow), "New" as a gold
  label. Ukiyo's AI section uses gold and indigo instead of red (owner: "why do you always have to use red everywhere");
  the one red button stays.
- Ukiyo's hero, rewritten (owner: "fix this way of writing"; picked "ride the wave"): "The AI wave is here. *Learn to
  ride it.*", then "Build real AI apps on your own machine: an editor, a terminal and real models, ready in about a
  minute." and "No videos to sit through. *You learn by building.*" Ink and indigo; red only on the Start button.
- No italic display type on the Ukiyo home page (owner: "the part i dont like is cursive", and the font size): the
  emphasised half of every heading is upright, in indigo; the hero and the section headings are a size smaller.
- The "start a lab" section: one line under its heading, "Nothing to install. You go straight to the challenge."
  (owner: "keep it just" that), and the lab picker is a row of words, the picked one in ink with a vermilion
  underline, instead of boxes (owner: "do something with these rectangle boxes", "keep red some parts").
- Every main red button on Ukiyo (Start free, See the course and the rest) is a seal: a thin paper-white line just
  inside its edge, like the machine's Open button (owner: "start free. white lines", "whichever suits best"). `ClaimDemo` stays in `HomeAiLabs.tsx`.
- The AI rows are compact (smaller pictures, type and spacing), and a course of 15 chapters or fewer is marked
  "Micro" (owner: "write micro in front of small courses"); today that is RAG and vector databases.
- Ukiyo's art, made with OpenAI image generation in a woodblock style (four concepts for the spotlight, five row
  pictures, about $0.36 in all): the spotlight shows "Arrival", an engineer at the prow of a small boat riding a great
  wave of light points toward a modern city under a snow-capped mountain; each AI row shows a picture made for its
  course (a museum's bronze horse, a hill train on a viaduct, a farmer in a wheat field, a canal that branches like a
  graph, a ranger and a tiger). Files in `frontend/public/home/`.


## 27 November: public intro pages for the AI courses, a pricing page, new art for the FDE spotlight

- **The AI courses' intro pages are public** (owner: "do not send them to login signup page directly", "actual intro
  page where skill map is present", "only the AI courses"). `/courses/<lab>` opens for visitors for the six AI courses:
  cover, description, Before you start and the skill map, with "Start free" (sign-up, then back to the course)
  instead of Start, and no links into the lessons. One new public route, `GET /api/courses/{lab_id}`, AI track only
  (404 otherwise), titles only: parts, chapters, subtopics and task titles, never lessons, hints, task cards, tests or
  solutions. Any other course still sends a visitor to log in, then back. The public catalog also lists each course's
  part names (`parts`).
- **Home page AI rows:** no numbers, a small logo per lab like the dashboard's list, and each row opens the course's
  intro page; the spotlight's button reads "See the course" (or "Open the course" when signed in) and its parts are
  listed under the description. The real LangChain, LangChain4j and LangGraph logos (and the logo lookup that reads
  "Logo: ...") come to master from Ukiyo.
- **New art for the FDE spotlight** (owner: "a big image ... cool one"): made with OpenAI image generation (medium
  quality, 3 candidates per design, about $0.25): a woodblock-style scene for Ukiyo (an engineer at an insurer, a
  river of data from the claim forms into the laptop) and a neon diorama for master. Shown big above the course name,
  slowly drifting, credited as an AI illustration. The other candidates stay out of the repo.
- **Pricing page, UI only** (`/pricing`, owner: "plans, no prices yet"): Free (what every account has today), Pro and
  Teams marked "Coming soon" with no price and no buy button, four questions; linked from the home menu and every
  public page's footer, on both designs (Ukiyo: fine rules, serif, a vermilion rule on Free).
- Tests: a backend test for the public course route (AI only, titles only, nothing hidden leaks); browser tests for
  visitors on a course page, the rows' links and logos, and the pricing page.

## 27 November: AI labs first on the home page, the Forward Deployed Engineer course in the spotlight

- **The AI labs sit right under the hero on both designs** (owner: "ai section labs at the forefront on the homepage,
  with cool animation, so the forward deployed engineer gets the max visibility"). One shared component,
  `frontend/src/components/HomeAiLabs.tsx`: a spotlight for the Forward Deployed Engineer course (chapters, tasks,
  hours, Start) with a playing demo, then the five other AI labs as ruled index rows (number, title, one line,
  chapters and hours), which rise in one after another as the section scrolls into view. No pictures in the section
  (owner: "i dont want cards for this", "too many images on the home page"): the demo is its only picture.
- **The demo is a real run** (chapter 17's attack A): a claim email for Rs 15,750 types in with a hidden note to record
  Rs 1,00,000; the model's six fields fill in one by one, amount_rs 100000 marked; code checks the Rs 50,000 pilot
  limit and stamps "Refer to an adjuster". It plays only while on screen and shows the last frame with reduced motion.
- **Current design:** a slow light runs round the spotlight's border; a red rule slides along a row on hover; the hero pill reads "New: the Forward Deployed Engineer course" and jumps to the section; the old "24 labs
  launching" block is gone, and the numbers row counts the live AI courses.
- **Ukiyo:** paper and fine rules, a ruled claim ledger, a straight vermilion seal for the decision, a vermilion rule
  that draws across the spotlight and under a row on hover. The hero terminal now types
  the course's real eval gate and smoke test. The menu's "AI labs" still opens the AI labs (owner, 25 November).
- Browser tests: the home test checks the spotlight, the five rows, no pictures, the demo's last frame and that the section comes
  right after the hero.

## 27 November: a new course, Forward Deployed Engineer

- **New AI course, `forward-deployed-engineer`** (owner, before sleeping: "scrape the whole internet for the Forward
  Deployed Engineer role and build a lab course on it, full standard"; built unattended). Research first: the role's
  history (Palantir), OpenAI's and Anthropic's FDE postings, a16z on the role, and the syllabi of the paid courses on it.
  The course follows one engagement: Claimdesk, a claims assistant for Deccan Shield Insurance in Pune. 22 chapters,
  44 tasks, six parts: the role (baseline, discovery, scoping), the customer's data (messy CSV, SQL and injection, an old
  XML system with backoff, a data contract), building with models (the gateway and cost in rupees, extraction with a
  strict schema, cited answers, tools, an MCP server, the day-five demo), proving it works (golden set, evals and a
  regression gate, failure analysis), ready for real claims (privacy and prompt injection, pacing and caching, shadow
  mode and a go-live check, monitoring with drift alerts), leaving well (settings, smoke test, CI, runbook; a second
  customer through an adapter and per-customer config).
- **Every model output is real**, captured through the LabBox gateway with an author account: dates without a year came
  back as 2023 (and still did when the prompt gave today's date); the model called a policy "not in force" on a date
  inside its period; 15 of 30 unpaced calls hit the rate limit (paced: 0 of 30, 93 s); a prompt change raised all-fields
  accuracy from 73.3% to 80.0% but lowered dates from 83.3% to 80.0%, and the gate refused it; two quiet prompt
  injections made the model record Rs 1,00,000, stopped only by the pilot limit in code. Chapter 20's request log is a
  simulation built from the 109 real calls' latencies and tokens, and says so.
- Checks run with a fake OpenAI server (no network); test-lab green: every starter fails, every solution passes.
  20 photos (public domain or CC, credited), 22 handwritten notes pages, 9 playing diagrams (`fde-*` in
  `Diagrams.tsx`), `before_you_start`, a lab tone, the AI track's six FDE nodes, and the lab in `test_test_lab`.
- Consistency fix: chapter 8 sized the model cost as if the Pune pilot handled 80 claims a day (it is about 57 a
  quarter); it now sizes it for a rollout to every office, and chapter 20 is set in December, after that rollout.

## 27 November: sign in with Google and GitHub

- **Google and GitHub only** (owner: "remove the username and password signup and login; all sign-ups and logins via
  Google and GitHub"). The login page shows the two buttons and nothing else (both designs); the first sign-in makes the
  account. `PASSWORD_LOGIN` (default off) refuses the username and password API; development and tests turn it on, as
  browser tests cannot use real Google (`e2e/signin.ts`). `labbox link-email <username> <email>` gives an existing account
  an email so Google or GitHub opens it (the owner's `gaurav`, with all its progress and admin rights);
  `labbox invite <email>` makes an account in advance on an invite-only site (`deploy/laptop/prod invite`, replacing
  `adduser`).
- **Continue with Google / Continue with GitHub** on the login page (both designs), shown only when a provider's keys are
  in `.env` (`/api/auth/options` lists `providers`). The flow (`backend/app/oauth.py`): a server-side state bound to a
  short HttpOnly cookie, PKCE for Google, the identity fetched from the provider, then the LabBox account: the same
  provider account, else a verified email match (so Google and GitHub with one address share an account), else a new
  account while sign-up is open (invite-only sites refuse and say why). The browser gets a one-time code (60 s) that
  `/api/auth/oauth/exchange` swaps for the usual login, never the token in an address; new accounts go to onboarding.
  `user.email` and `user_identity` (migration 0015). Admin's Learners show and search emails. Privacy policy line.
  9 backend tests with faked providers; a browser test on each design. Also fixed: master's login page called a React
  hook conditionally.

## 27 November: certificates to share on LinkedIn and X

- **QR code to verify** a certificate: it opens `/verify/<id>`, which shows what the server's database holds for that id
  (verified with the name, lab, date and tasks; genuine but private; unknown; or the home page's sample), and takes a
  typed id. The share image carries it too. The seal is a small stamp. The home section keeps LinkedIn, the QR and where
  to share; the rest moved to the FAQ with a question on checking a certificate. Ukiyo: LangChain's certificate print is
  Hiroshige's Lake Biwa and Ishiyama Temple, 1853 (San Diego Museum of Art, public domain).
- Ukiyo home, the container: no more cardboard crates; each piece of the lab's stack is its logo alone, large, with a
  shadow under it (owner: "try only logos, large logos inside the container"). Logos that would melt into the blue get
  lighter colours of their own, the container unchanged (owner: "only change the logo colours"): LangChain's dark pill
  turns pale; Python, Java, PostgreSQL and FastAPI brighten. The whale on the glass fades further while they load. The
  logos sit closer, larger and brighter, and every piece has one: GNU Bash for the editor and terminal, Hugging Face for
  the embedding models (Simple Icons 16.37.0, CC0, `public/logos/LICENSE-simple-icons`), a torii gate drawn for the model
  gateway, the LabBox mark for its tutor, a small code window for the editor (OpenAI's logo is left out: Simple Icons
  removed it and OpenAI limits its use). Laid out by count so they never overlap: up to 3 on the floor right of the
  status plate, the rest in a row above that uses the whole width.
- **Home page: a Certificates section** ("Finish a lab. Share the proof."): a sample certificate drawn by the same
  component as the real page (`CertificateSheet`), its own link, what happens when a lab is finished, and where it can
  be shared (LinkedIn, X, WhatsApp, Facebook, email, a CV, any page). Both designs; checked in the home browser test.
- Ukiyo home: the lab terminal is back over the Hiroshige print, typing its session on a loop, on thin see-through
  glass so the print shows behind it (owner: "very shallow").
- **Certificates** (owner: "a certificate automatically, with a URL shareable on LinkedIn, X and other social media,
  once a lab is passed and completed"). Earned at 80% of a lab's tasks; the first asks for the full name once
  (`user_profile.certificate_name`), later ones come by themselves with the check that finishes a lab (the check's
  answer gains `certificate`; the lab shows a note). Public page `/certificates/<id>`; the address to share is `/c/<id>`,
  whose HTML carries the Open Graph and X card tags and a 1200 x 627 JPEG drawn with Pillow in the site's fonts
  (Fraunces and Inter, OFL, in `backend/app/assets/fonts`), with Ukiyo's woodblock print of the lab. Share bar:
  LinkedIn "Add to profile" (the certification form filled in), LinkedIn post, X, WhatsApp, Facebook, copy link,
  download. Hide a certificate, or correct its name once. My certificates (profile menu), a certificate box on every
  course page, a line in the privacy policy. Caddy, nginx and Vite send `/c/` to the backend. Migration 0014.
  5 backend tests, a browser test on each design.
- `scripts/restart_backend.sh` matched any `uvicorn app.main:app`, the live site's backend included; it now only
  touches the development backend on port 8000.

## 27 November: the live site on the laptop, and the Deploy button

- **Invite-only login page**: `GET /api/auth/options` says whether sign-up is open; when it is not (the live site,
  `ALLOW_SIGNUP=false`), the login page says "Sign-up is by invitation for now" instead of a Sign up link, and "Start
  free" lands on the login form (both designs). One test.
- **`labbox password <username>`**: sets a new password (asked twice, never shown; 6 to 72 characters, as at sign-up).
  On the live site: `deploy/laptop/prod labbox password <username>`. There is no reset by email yet. One test.
- **`INSTANCE` setting** (backend): a second LabBox on the same Docker names its lab machines, check containers and
  lab networks with its own word (`INSTANCE=prod`: `lab-prod-u1-...`, `labnet-prod-u1-...`) and labels them
  `labbox.instance=prod`; idle stop, check cleanup, network cleanup, the running-labs limit and `labbox test-accounts
  cleanup` see only their own instance's. Empty (development, the default): the names of before. `/api/health`
  reports `release` (the deployed commit). 6 tests (`tests/test_instance.py`, one with a real container); 316 backend
  tests green on Postgres and Redis.
- **`deploy/laptop/`** (the live site on this laptop, owner 27 November): `setup.sh` (Caddy 2.11.9 and cloudflared
  2026.10.7 pinned by checksum, `/srv/labbox/prod`, database `labbox_prod`, the live `.env` with fresh secrets,
  sign-up off, systemd user services; `setup.sh tunnel <host>` for Cloudflare), `release.sh` (each commit in its own
  folder: packages, frontend build, `validate --strict`, changed lab images, migrations, switch, health check on
  the release and the page, switch back on failure; refuses commits older than `INSTANCE`), `pull_deploy.sh` and a
  one-minute timer that follow the `production` branch, a `Caddyfile` (the app's paths to :8100, `/metrics` kept
  local, the learner's address from Cloudflare for rate limits), and the `prod` helper (status, logs, deploy,
  rollback, restart, labbox, adduser, images).
- **The Deploy button** (`.github/workflows/deploy.yml`): Run workflow with a branch (default `design/ukiyo`), CI's
  checks on that commit (`labs.yml` is now also callable), the `production` branch moves, and the run waits until
  `/api/health` on the live site reports the commit. GitHub never runs anything on the laptop.

## 26 November: Ukiyo home, the print without the terminal box

- The Ukiyo home hero shows Hiroshige's Kinryuzan print on its own: the lab-terminal box laid over it is gone (owner:
  "can you remove this?"). The home browser test now checks that the box is absent.
- In the dark theme the print is one shade darker (`brightness(.82)`), so its pale snow does not glare; the light
  theme shows it as it is.

## 26 November: the Lab access tab in Admin, and the lab limit on both designs

- Admin has a **Lab access** tab (owner: "more easy to use, good looking, minimal, expressive"): the rule in one
  sentence ("Each learner works in 3 labs at a time."), a switch (Every lab / A few at a time) and a minus and plus
  stepper; a change shows what it will become and waits for Save or Undo. Below: the three rules (Unlock, Finish at
  80%, Swap on Mondays), faded while every lab is open, and **Exceptions**, the learners with their own number,
  changed in place, removed, or added by searching a username. The Learners tab keeps a limit on each row, its
  default named ("Default (3 labs)").
- Frontend of the lab limit (master and Ukiyo): the locked course page with Unlock, the slot note and Monday swap on
  an unlocked lab, the dashboard's slot strip with Locked and Unlocked marks (Ukiyo: on its lab rows), the lab page
  sending a locked lab to its course page, a skill map without links on a locked lab.
- `scripts/labbox lab-limit [N|off] [--plain]` shows or sets the limit for everyone. Browser-test runs switch the limit
  off while they run and put the owner's setting back (a stopped run gives it back at the start of the next), and
  `test-accounts cleanup` clears test accounts' own limits, so Exceptions lists only real learners.
- Fixed: a stray `}` in `styles.css` (since 21 November) made browsers skip the `.course-page` rule after it; it
  showed up only now, when a style with an inline picture made Vite check the whole file.

## 26 November: at most a few labs at a time (backend, master and Ukiyo)

- The owner's rule, so learners focus: an admin sets how many labs a learner may have unlocked at once (Admin,
  Learners, "Lab access": every lab open, the default, or N at a time) and can give one learner their own number or
  every lab. Admins are never limited.
- A locked lab opens only its course page, with an **Unlock this lab** button while a slot is free. Its lessons,
  machine, terminal, files, checks, hints, tutor, preview and VS Code answer 403 on the server, and the lab page sends
  a lesson link back to the course page. The skill map of a locked lab has no links.
- A lab is finished when 80% of its tasks have passed at least once: its slot frees at once and it stays open. On
  Mondays (India time) a learner may swap an unfinished lab out (its machine stops, progress stays).
- The dashboard shows the slots in use and a lock or "Unlocked" badge on each lab while a limit is on; the Continue
  card picks up in an open lab and shows no lesson text from a locked one.
- New: `app/slots.py`, `routers/slot_routes.py` (`GET /api/slots`, `POST /api/labs/<lab>/unlock` and `/swap`),
  admin routes `/api/admin/lab-access` and `/api/admin/learners/<id>/lab-limit`, migration 0013 (`lab_slot`,
  `site_setting`, `user.lab_limit`), `tests/test_slots.py` (12 tests), `e2e/lab-slots.spec.ts`.

## 26 November: LangGraph chapter 24 rewritten: the whole desk re-run on a server, every slip tried

- Ran the capstone on a fresh `langgraph dev`: the same three paths (status from the tickets, the tanker rule from the
  rulebook, the burst main paused at Rs 65,000) and, after the engineer's approval over HTTP, the same Thursday
  booking for a flooding road. 10,469 tokens for the whole conversation. A new still picture shows the conversation.
- Tried: the quiz (`Intent(kind="complaint")` raises a `ValidationError`); `state["intent"].kind` (`AttributeError`,
  the first task's slip, because the intent is stored as a dictionary); the approval sent as `input=` instead of
  `command=` (no error, and the thread still waiting at `repair`, the second task's slip).
- A new sketchnote.

## 26 November: LangGraph chapter 23 rewritten: the review's second exit seen for real, facts checked

- Every fact the lesson quotes was checked against the sources (design pressure 2.5 bar, 5 then 14 complaints,
  rainfall 102%, roadworks in March), and the citation check was run on the table's five paragraphs: the same results.
- Re-ran the team on a fresh test account: 85 seconds, 8,068 tokens, six questions (the prompt asks for three or
  four). The review rejected both drafts because the recommendation cited no source, and the run ended with the
  problem kept for a person, the quiz's scenario for real. The report tied the pressure rise to the complaints; again
  no finding gave the design pressure. The lesson adds this run.
- Both tasks list their steps and a slip (node names instead of `Send`, as in chapter 6; dropping `if name not in
  known`). The animation is now a still picture of this run; a new sketchnote.

## 26 November: LangGraph chapter 22 rewritten: the plan checked again, the quiz corrected, virtual_mode tried

- Re-ran the deep agent: the analyst counted street by street this time (8 calls); every complaint count was right
  again, and the planner made the same three pipe-age mistakes (38, 51, 12) plus crew-day errors (20 for 1.2 km and for
  0.8 km). The lesson shows this run and the corrected error list; planner calls carried 1,835 to 3,258 tokens in.
- Corrected: the quiz said that without the permission the planner would read the 149 rows itself. We tried it: it
  still asked the analyst, because the prompt says so. The answer now teaches that a prompt is a request and a
  permission a rule.
- Tried `FilesystemBackend` both ways: with `virtual_mode=True`, `/etc/hostname` is "not found"; without it, the backend
  read `/etc/hostname` and could not find `/pipes.csv`. That is the first task's slip and the second quick check's
  evidence. An untested sentence about giving the tool to the planner was reworded.
- The animation is now a still picture of the run and four checked numbers; a new sketchnote.

## 26 November: LangGraph chapter 21 rewritten: a quiz answer corrected, the server's refusal reproduced

- Ran `langgraph dev` and the client in a lab machine: the server answered on one thread; this time the agent listed
  the tickets and asked before fetching statuses (chapter 13's other path, 6 messages instead of 9). The lesson says so.
- Corrected: the quiz said a restarted `langgraph dev` loses its threads. We restarted it: `threads.search()` found the
  thread with all 6 messages, loaded from `.langgraph_api/store.pckl`. The quiz and the concept step now say where
  `langgraph dev` keeps threads.
- Reproduced: the starter graph with its own checkpointer is refused with the lesson's "Heads up! ... includes a custom
  checkpointer" message, and the server does not start.
- Both tasks list their steps and a slip (the leftover `InMemorySaver()` after removing its import; `.content` on a
  message that arrives as a dictionary). The animation is now a still picture of the run and the restart. A new
  sketchnote.

## 26 November: LangGraph chapter 20 rewritten: the real test grid pictured, the quiz's weak test run

- Re-ran pytest: 3 passed in 0.19 s; with the planted `TEAMS` change, only the routing test failed, with the same
  assertion. A new still picture shows four tests on the correct desk and with the bug.
- Tried the quiz's weak test (kind only): it passed with the bug ("1 passed in 0.17s"). `app.nodes["route"].invoke(...)`
  from the table was tried: `{'team': 'health team'}`.
- Both tasks list their steps and a slip (the weak assertion; no checkpointer, with chapter 10's measured error).
- A new sketchnote.

## 26 November: LangGraph chapter 19 rewritten: J-301's resume pictured, every slip tried

- Re-ran every command on a new `jobs.db`: the same results and the same record (one crew, one order, one SMS per job).
  A new still picture compares J-301's crashed run with the resume that replays saved task results.
- Tried: the quiz (`board.order_parts` called outside a task: two orders after the resume); no `.result()`
  (`TypeError: Type is not msgpack serializable: Future`, the first task's slip); `interrupt` without the early return
  (a refused job booked a crew, the second task's slip).
- Both tasks list their steps. A new sketchnote.

## 26 November: LangGraph chapter 18 rewritten: a time line of a real run, every slip tried

- Re-ran it twice: the progress events at 0.00 s and 0.50 s again, the first token at 2.27 s and 2.50 s, the end at
  3.09 s and 3.39 s (73 and 72 chunks). The lesson gives the three runs; a new still picture puts one on a time line.
- Found: calling a node that uses `get_stream_writer` directly (as a unit test might) fails with `RuntimeError: Called
  get_config outside of a runnable context`; the lesson warns about it before chapter 20.
- Tried: the quiz (`invoke` returns the normal state, no events); a plain string to the writer (`TypeError: string
  indices must be integers`, the first task's slip); no empty-content check (4 empty chunks in one run, the second
  task's slip).
- A new sketchnote.

## 26 November: LangGraph chapter 17 rewritten: runs compared, the suggested fix tried and found to bend a fact

- Re-ran the team twice: once clean (one hold, one visit), once with the case sent to billing twice. Neither run
  repeated the lesson's double booking; the lesson now reports all three runs.
- Tried the lesson's suggested fix (the supervisor writes a one-sentence task; each specialist sees only its task):
  nobody did another's work, but the supervisor invented a helpline number, "1800-123-4567", and repairs booked the
  visit for that number. The lesson now says so, and that facts the code knows should be passed in code.
- Slips tried with stand-in nodes: `Command(goto="FINISH")` only prints a warning ("wrote to unknown channel
  branch:to:FINISH, ignoring it") and the run ends silently; a specialist returning a plain update ends the run after
  itself.
- A new still picture of the clean run with the other runs noted; a new sketchnote. Note: the idle reaper stopped one
  test machine mid-run; the runs were redone on a fresh machine.

## 26 November: LangGraph chapter 16 rewritten: two tickets pictured, every subgraph mistake tried

- Re-ran the solution: the same output, line for line. A new still picture shows T-4490 through the billing graph
  (shared keys) and T-4492 through the translating repairs function.
- Tried: `build_billing` without brackets (`TypeError: build_billing() takes 0 positional arguments but 1 was given`,
  the first task's slip); the repair graph added directly (`KeyError: 'job'`, the second task's slip); the quiz's
  renamed key (the desk's `verdict` came back `None`, with no error).
- Corrected: "four times normal" became 3.9 times (2,410 against 611), over the rule's limit of three.
- A new sketchnote.

## 26 November: LangGraph chapter 15 rewritten: four real paths pictured, the rewrite counter's cost measured

- Re-ran the four questions with the real model: the same four paths (tanker and roof searched once and answered,
  bottled water rewritten once and answered honestly, thank-you with no search). The lesson now shows this run; the
  bottled water's second search found the tanker rule again this time.
- Tried with a stand-in model that always grades "not relevant": the solution makes 6 model calls; without
  `"rewrites"` in the update the loop ran until a recursion limit of 40 stopped it, after 27 calls. That is the rewrite
  task's slip; the grade task's slip (no `rewrites` test) points to the same cost, and the quiz now gives chapter 3's
  measured default limit.
- The animation is now a still picture of the four paths; a new sketchnote.

## 26 November: LangGraph chapter 14 rewritten: both questions handed over, three fixes tried, one worked

- Re-ran both questions with the real model: both were handed to a person. The water answer said "tomorrow" in all
  three drafts (the tools say Wednesday); in the drinking answer the checker caught "tomorrow" and the unsourced advice,
  then wrongly flagged a fact from the tools. The lesson now shows these runs (the first version had the water answer
  pass at once).
- Tried the lesson's own advice and two more, one run each: "Today is Tuesday." for the writer only (the writer wrote
  "tomorrow (Wednesday)", the checker rejected it: still handed over); the same for the checker too (still handed over,
  because the checker's rule calls "tomorrow" a new claim); "Write days exactly as the tool results give them" for the
  writer (both answers sent). The try step teaches all three, and the recap now says "an unclear instruction, a
  missing fact".
- A new still picture of the real three-draft run; both tasks list steps and slips. A new sketchnote.

## 26 November: LangGraph chapter 13 rewritten: the agent's two paths measured, a wrong default corrected

- Re-ran the agent three times at temperature 0: once exactly the lesson's run (both statuses fetched in one message,
  advice not to drink the water); twice it stopped after `find_tickets`, asked whether to fetch the statuses, and
  refused the safety question ("I cannot provide health or safety advice"). The lesson now shows both paths and why.
- Corrected: the deep dive said `ToolNode` turns a tool's exception into a message by default. In 1.2.24 only bad
  arguments become a `ToolMessage`; a `ValueError` raised inside the tool stops the run; `handle_tool_errors=True`
  turns it into "Error: ValueError('database down') Please fix your mistakes." All three were tried.
- Tried: no `bind_tools` (the model asked for the phone number already given), `messages[0]` in the router
  (`AttributeError: 'HumanMessage' object has no attribute 'tool_calls'`), and the quiz (no edge back: the run ends on
  the tool result).
- The animation is now a still picture of the real run with the other path noted; a new sketchnote.

## 26 November: LangGraph chapter 12 rewritten: what a store search really embeds, measured

- Re-ran the solution with the real model: the same behaviour (Marathi in both threads of 98220, English for 70300,
  one stored fact) and the same search scores, 0.59 and 0.27.
- Found by computing the cosine by hand: the store's score is the similarity with the whole value as JSON
  (`{"text": ...}`, 0.59), not with the note's text (0.63). With `index={"fields": ["text"]}` the scores became 0.63
  and 0.30. The lesson now explains this and shows the option.
- Slips tried: a bare string value (`ValueError: dictionary update sequence element #0...`), `item["language"]`
  (`TypeError: 'Item' object is not subscriptable`), no `None` check (`AttributeError`).
- The animation is now a still picture of the three threads and the one stored fact; a new sketchnote.

## 26 November: LangGraph chapter 11 rewritten: the real history pictured as two branches, slips tried

- Re-ran the solution: the same output, line for line. The animation is now a still picture of thread C-311's eight
  checkpoints: the first run and the branch made by the correction.
- Tried: comparing `.next` with the string "route" finds nothing (the first task's slip); `invoke(fields,
  snapshot.config)` instead of `update_state` starts over and puts "other" back (the second task's slip); the quiz's
  `as_node="route"` stops with `KeyError: 'team'` (as the lesson already said). Found: here `as_node` may be left out,
  because LangGraph takes the update as triage's; the lesson notes it and keeps `as_node` for clarity.
  `delete_thread` exists on the checkpointer.
- Both tasks list their steps. A new sketchnote.

## 26 November: LangGraph chapter 10 rewritten: J-201 pictured, the brief fix tried, resume mistakes quoted

- Re-ran the five commands on a new `repairs.db`: the same results, and the first brief again invented "due to frequent
  leaks and reduced water pressure". The lesson's suggested fix was tried with the real model ("Use only the facts
  given. If no reason is given, write: No reason given."): the brief then said "No reason given." Quoted.
- Found: without a checkpointer the interrupt still stops the run, but the resume fails with `RuntimeError: Cannot use
  Command(resume=...) without checkpointer`; the lesson's "a checkpointer is required" now says exactly where.
- Tried (fake model): resuming with a plain dictionary starts the job again from START and pauses again (the resume
  task's slip); a resume sent to an unknown thread fails with `KeyError: 'work'`.
- The animation is now a still picture of J-201's two processes; both tasks list steps and slips. A new sketchnote.

## 26 November: LangGraph chapter 9 rewritten: retry waits measured, both jobs pictured, the quiz tried

- Re-ran all four commands on a new `jobs.db`: the same output, word for word, including J-103's double booking. A new
  still picture compares J-102 (resumed with `invoke(None, config)`) and J-103 (started over).
- Measured: the waits between SMS attempts were 1.08 s and 1.70 s, not 0.5 s and 1 s; `RetryPolicy` adds a random 0 to
  1 second by default (`jitter=True`, read in the source). The table now has the jitter row and the measurement; it
  also says `max_attempts=3` and `initial_interval=0.5` are the defaults in 1.2.24.
- Tried: a `ValueError` with `retry_on=SmsTimeout` fails after one attempt; the policy on the wrong node crashes on the
  first timeout (the retry task's slip); the quiz's step that fails after ordering placed two orders on resume.
  `durability` defaults to "async" (read in the source).
- A new sketchnote.

## 26 November: LangGraph chapter 8 rewritten: a still token chart from a new run, slips tried with a fake model

- Re-ran both graphs with the real model: the same pattern (trimmed asked for the address again, summarised read it
  back). The lesson now shows this run, with its numbers in a new still chart (tokens per turn and messages kept).
  New in this run: the summarised Harsh promised "I will request the tanker to come after 6 PM"; the lesson points it
  out. The deep dive's quote of the summary's bent fact now uses this run's summary.
- Found by testing `trim_messages`: with `start_on="human"` it can keep three messages instead of four (the fourth from
  the end was a reply); the lesson says so.
- Slips tried: `strategy="first"` keeps the start and drops the newest message; no `token_counter` is a `TypeError`;
  removing every message in `summarise` (fake model) leaves the state empty, the new answer included.
- A new sketchnote.

## 26 November: LangGraph chapter 7 rewritten: three real processes pictured, every slip tried

- Re-ran the three commands on a new `harsh.db`: the same answers (the first now ends "with updates shortly"),
  including the invented "a crew is still working" and the ignored brown water that the lesson discusses.
- Tried: the quiz (InMemorySaver in a new process: 2 messages); no config with a checkpointer (`ValueError:
  Checkpointer requires one or more of the following 'configurable' keys`, the first task's slip); no
  `check_same_thread=False` (`ProgrammingError: SQLite objects created in a thread...`, the second task's slip).
- Found: LangGraph 1.2.24 also accepts a top-level `{"thread_id": ...}` and saves to the same thread; the lesson
  mentions the short form and keeps the full one.
- The animation is now a still picture of the three processes; a new sketchnote.

## 26 November: LangGraph chapter 6 rewritten: the storm night pictured, Send and Command mistakes tried

- Re-ran the solution: the same output. A new still picture shows the five Sends in one step and the Command for each
  repair, with the urgent brown water scheduled for tomorrow (the lesson's point).
- Tried: the quiz (no reducer on `tickets`: `InvalidUpdateError`); node names instead of `Send` (`KeyError: 'text'`,
  the first task's slip); `Command(goto="schedule")` without the update (`KeyError: 'status'`, the second task's
  slip); `plan` without its `Command[Literal[...]]` annotation (it still runs, but the diagram draws `plan -->
  __end__`), which backs the lesson's claim about the return type.
- Both tasks list their steps. A new sketchnote.

## 26 November: LangGraph chapter 5 rewritten: a wrong weekday fixed, the grader's miss measured

- Fixed in the lab: the notice facts said "Thursday 28 November", which is a Saturday in 2026; starter and solution
  now say "Thursday 3 December" (a Thursday), and the lesson notes the change.
- Re-ran the notice loop with the real model four times: in the run shown the grader caught the missing area; in the
  other three it passed a final notice that never named Old Market. The lesson now gives that count instead of one run.
- Measured the join claims with plain nodes: separate edges with uneven branches ran `assign` twice, the list join
  once; two one-second nodes in the same step took 1.00 seconds; two parallel writes to one key raise
  `InvalidUpdateError` (the quiz). The Station Road run was reproduced.
- Both tasks list their steps and a slip (a missing START edge, tried: no error, no plan; `and` instead of `or`).
- The animation is now a still picture of the real run and the measured facts; a new sketchnote.

## 26 November: LangGraph chapter 4 rewritten: two real model calls pictured, a slip I expected disproved

- Re-ran the solution with the real model: the same four triages; the replies the same except the first, which now
  names Tilak Nagar too (the lesson quotes it). Triage calls were about 180 tokens in, replies about 90.
- Tried and found: returning the `Triage` object without `.model_dump()` works in LangGraph 1.2.24 (a node may return
  a Pydantic object), so it is not taught as a slip. Real slips, tried: no `with_structured_output` (the message's
  fields are ignored and the next node stops with `KeyError: 'kind'`), and no `.content` (the state holds a whole
  `AIMessage`).
- The quiz's claim was tried: "critical" raises a Pydantic `ValidationError` on `severity`. `retry_policy` and the
  other `add_node` options were checked in 1.2.24. Pydantic models and `Literal` are explained at first use.
- The animation is now a still picture of the Hindi complaint through both model calls; a new sketchnote.

## 26 November: LangGraph chapter 3 rewritten: the four real paths pictured, the recursion limit measured

- Re-ran the solution: the same four lines. A still picture now shows each street's tries and where it ended.
- The quiz's loop without a limit was tried: LangGraph 1.2.24 stopped it with `GraphRecursionError: Recursion limit
  of 10007 reached` after 1.5 seconds (the default is 10,007 in this version, settable per run; 25 stopped it in
  0.01 seconds). The explanation now gives the numbers and the cost of a model call in such a loop.
- Tried: a misspelled target stops the build (`found unknown target 'health_teem'`); with no target list the diagram
  draws a wrong `route --> __end__`; a router returning "health team" stops with `KeyError`; `<=` gives 3 tries; a
  router returning two nodes that both write `team` stops with `InvalidUpdateError` (the deep dive now says so).
- Both tasks list their steps and a tried slip. A new sketchnote.

## 26 November: LangGraph chapter 2 rewritten: a still picture of both reducers, every slip tried

- Re-ran the solution: the same three lines. Tried the quiz and the claims: without the log reducer only
  check_location's line is left; without the severity reducer urgent became high.
- Found by logging the reducer's calls: LangGraph's first call is `higher("", "urgent")` (current starts as the empty
  string), so leaving out the empty check stops the run with `ValueError: '' is not in list`; the lesson now says
  this, and it is the second task's usual slip. The first task's slip (`operator.add()` with brackets) was tried:
  `TypeError: add expected 2 arguments, got 0`.
- `Annotated` is explained at first use; `input_schema` and `output_schema` checked in 1.2.24.
- The animation is now a still picture of the two real updates with and without reducers; a new sketchnote.

## 26 November: LangGraph chapter 1 rewritten: a still picture of the state after each node, slips tried

- Re-ran the solution in a lab machine (LangGraph 1.2.24): the same output, word for word.
- Tried the claims: an edge to a misspelled node stops `compile()` with `ValueError: Found edge ending at unknown
  node 'clasify'`; without the middle edge the graph compiles and runs but has no `reply` (the first task's usual
  slip); `stream_mode="values"` gives whole states, not node names (the second task's slip). `create_agent`'s graph
  was listed: `['__start__', 'model', 'tools', '__end__']`.
- `TypedDict` and `total=False` are explained at first use. Both tasks list their steps.
- The animation is now a still picture of the real run; a new sketchnote.

## 26 November: LangChain4j chapter 30 rewritten: the live app re-run word for word, the guardrail bug pictured

- Ran the capstone app in a lab machine and sent the lesson's five requests: every answer the same, word for word,
  and `/usage` again 4 calls, 1,968 tokens in, 145 out.
- Reproduced the guardrail bug with chapter 25's `QuestionLimit` put back: the 59-character bicycle question was
  refused, 24- and 22-character questions were answered. The gateway's log shows the refused question's embedding
  (17 tokens) was paid for and no chat call followed: retrieval runs before input guardrails. A new still picture
  compares the old and new guard on two 59-character questions.
- Both tasks list their steps and a slip: no splitter (chapter 23's slip) and no `.distinct()`, tried: the landslide
  question's sources came back as `["refunds.txt","monsoon.txt","refunds.txt"]`.
- `Result` methods (`content`, `sources`, `tokenUsage`, `toolExecutions`) checked in the jar; the price is labelled
  as gpt-4o-mini's. A new sketchnote.

## 26 November: LangChain4j chapter 29 rewritten: all seven calls pictured, both answers reproduced

- Re-ran both versions: without `supervisorContext`, "420 rupees" for two adults again, word for word; with it, "840
  rupees" again. The gateway's log shows exactly seven calls, as the lesson counted; the three planner calls are the
  biggest (434, 552, 667 tokens in). The animation is now a still picture of the seven calls with their tokens.
- The quiz's `LAST` claim was tried: the whole answer was `420`.
- Tried the fare agent without `.tools(...)`: it apologised that it has no fare tool, the text could not be parsed as
  an `int`, and the run stopped with `OutputParsingException`; this is the task's usual slip now. The supervisor
  task's slip is the missing context (the try step shows it).
- The planner's instruction sentence was found in the 1.24 jar (`PlannerAgent`); `SupervisorResponseStrategy`
  (`LAST`, `SUMMARY`, `SCORED`), `maxAgentsInvocations`, `contextGenerationStrategy`, `supervisorBuilder(Class)`,
  `@SupervisorAgent` and `a2aBuilder` checked. A new sketchnote.

## 26 November: LangChain4j chapter 28 rewritten: a still picture of real paths, a quiz answer corrected

- Re-ran the solution: the refund path was the same word for word; this time the Monsoon Mail reply passed review at
  once (9 calls, not 11), as the lesson's second lesson says can happen. The bad reply again scored 0.8 after one
  edit. A rate-limit stop (20 calls a minute) happened again during the probes.
- Corrected: the quick check said that with two true conditions "the second's reply replaces the first's". In five
  runs both desks ran every time, and the kept reply was sometimes the first's, sometimes the second's, in either
  order. The answer now says you pay for both and cannot count on which is kept.
- Tried: a scorer that can never pass stops after exactly 6 calls; a topic with no desk gives a `null` answer with no
  error (now the conditional task's usual slip). Read in the jar: without `.maxIterations(...)` the ceiling is
  `Integer.MAX_VALUE` (now the loop task's slip).
- The workflow builders and methods in the lesson (`parallelBuilder`, `executor`, `output`, `errorHandler`,
  `testExitAtLoopEnd`, `parallelMapperBuilder`, `humanInTheLoopBuilder`) were checked in the jar. The parallel
  example's timing ("about one second") became "about the time of the slower one".
- The animation is now a still picture of four real runs; a new sketchnote.

## 26 November: LangChain4j chapter 27 rewritten: a still picture of the scope, both slips and the quiz tried

- Re-ran the solution: the classifier said `REFUND` again; the replies were worded a little differently and the
  capital "REFUND team" leaked again, as the lesson says. The gateway's log gives the cost of each step (classifier
  56 and 63 tokens in, 2 and 3 out; writer 270 and 278 in); the lesson quotes it.
- The quiz's claim was tried: without `.outputKey("topic")` the run stops with `Missing argument: topic`. Putting the
  writer first gives the same error. Both are the tasks' usual slips now, with steps.
- `agentAction`, `invokeWithAgenticScope`, `readState`, `@SequenceAgent` and `UntypedAgent` checked in the agentic
  jar, which is still a beta module (`1.24.0-beta34`); the lesson says so.
- The animation is now a still picture of the scope after each step, with real token counts. A new sketchnote.

## 26 November: LangChain4j chapter 26 rewritten: the regression re-run four times, a false alarm found

- Re-ran the eval: 100%, and exactly the same counts and cost (6 calls, 1,418 in, 98 out, $0.000272).
- The regression did not reproduce as written. Removing only the "I don't know" sentence gave an honest answer
  (which still failed the check). The lesson's 1,238 tokens matched removing two rule sentences (we measured 1,244);
  with both removed, four runs all scored 5 of 6: two invented the lesson's exact "does not offer wi-fi services",
  two answered honestly in other words and failed the "contains" rule. The lesson now says what was removed, gives the
  real counts, and teaches that a miss can be a real mistake or new wording: read every MISSED line.
- A new still picture of the five eval runs.
- The listener contexts were checked in the 1.24 jar (`chatRequest`, `chatResponse`, `error`, `attributes`); the
  deep dive's AI Service events now list only the event classes that exist.
- Both tasks list their steps and a slip (counting in `onRequest`, which has no response; integer division making
  5 of 6 print as 0%). The price ratio is labelled as gpt-4o-mini's. A new sketchnote.

## 26 November: LangChain4j chapter 25 rewritten: a still picture of three real messages, every claim tried

- Re-ran the solution: the same three lines; the gateway's log shows two model calls (238 and 255 tokens in), so the
  refused message never reached the model. A new still picture shows each message through both guardrails.
- The guardrail-off claim was re-run four times: three answers copied the number, one said "I don't know"; with the
  guardrail on, every number was removed. The lesson now says "usually".
- Corrected: the short injection is 47 characters, not 48. We sent it: it passes the limit (the system message held
  this time; the lesson says that is not a guarantee).
- Checked in a probe: after `failure` the next guardrail still runs and the exception lists both messages; `fatal`
  stops at once; a message rewritten with `successWith` is what the next guardrail sees; `MAX_RETRIES_DEFAULT = 2`.
- The regex was tried on six strings (a booking number starting with 4 is left alone). Both tasks list their steps
  and a slip (`>=` instead of `>`; `matches()` instead of `find()`, tried: `false` on a real answer).
- History: "days later" became "that same week" for Willison naming prompt injection. The 7,500-token estimate and the
  price are labelled (about 4 characters per token; gpt-4o-mini's price). A new sketchnote.

## 26 November: LangChain4j chapter 24 rewritten: local model and routes re-run, the default route corrected

- Started the stopped Ollama container for this check only (Qwen 2.5 0.5B, 397 MB), joined it to a test machine's
  network, ran the chapter, then disconnected and stopped it again. The local model's sentence and the "Hi!" answer
  were the same word for word. The long complaint's answer differed (no temperature is set) and this time named
  "Indian Railways", a guess; the lesson says so.
- The gateway's log proved the router's choices (`max_tokens` 60 for "Hi!", 400 for the complaint); the lesson notes
  that `Setu.java` prints the route from its own test. A new still picture shows both routes with real token counts.
- Corrected: the lesson said the default route is used "whenever the router cannot decide". In 1.24 it is used when
  the router returns `ChatModelRoutingResult.defaultRoute()`; an unknown route name is an error. Tried and quoted:
  `The router selected the unknown route 'Complex'. Available routes: [simple, complex]`.
- Corrected: the deep dive named `TypeSafeDecisionModel`, which is not in 1.24; it now describes
  `DecisionModelChatModelRouter`'s `minProbability` and `FallbackStrategy` (both checked in the jar).
- Both tasks list their steps and a tried slip (an Ollama `/v1` address gives `404 page not found`; a mis-cased
  route name). `@Experimental` on `RoutingChatModel` checked. A new sketchnote.

## 26 November: LangChain4j chapter 23 rewritten: a still picture of one real RAG run, both slips tried

- Re-ran the solution in a lab machine: the same three answers, word for word; the guitar request was 107 tokens
  again. New measured facts in the lesson: the five rule files (1,772 characters) became 12 pieces, some only a
  heading; indexing took one embedding call of 412 tokens; the landslide question had four pieces over 0.7 and sent
  three (253 tokens); the wifi question's "Monsoon travel" heading scored 0.702, just over the line.
- The splitter chain was checked in the 1.24 jar: paragraphs, then lines, then sentences, then words (the lesson
  left out lines).
- Both tasks list their steps and a tried slip: no splitter (whole files; the guitar question found nothing and lost
  the 1.5-metre rule) and no content retriever (the landslide question got "I don't have information on refund
  policies").
- History: "when chat models arrived in 2023" became "after ChatGPT arrived (November 2022)".
- `file_name` and `absolute_directory_path`, the static `EmbeddingStoreIngestor.ingest(...)` and `Result.sources()`
  were checked in the jars.
- The animation is now a still picture with the run's real numbers; a new sketchnote.

## 26 November: LangChain4j chapter 22 rewritten: a still chart of every card's real score, both slips tried

- Re-ran the solution in a lab machine: the same four answers and every score the same to three decimals. The
  animation is now a still bar chart of all six cards' scores for the bicycle and France questions, with the 0.7
  line.
- Checked `RelevanceScore.fromCosineSimilarity` in the 1.24 jar: cosine 0 gives 0.5, cosine 0.424 gives 0.712, as
  the lesson says. `metadataKey(...)` and `add(...)` returning an id exist.
- Both tasks list their steps and a tried slip: no metadata (search still works, every title is `null`), and
  `minScore(0.5)` (two cards for every question, two for France).
- "30+ implementations" (not checked) became "many"; the deep dive no longer says LangChain4j's pgvector store uses
  HNSW (pgvector offers HNSW and IVFFlat). The 1,536 numbers and the price are labelled as this model's.
- A new sketchnote.

## 26 November: LangChain4j chapter 21 rewritten: the real wire traffic, a quiz answer corrected, every slip tried

- The "Guess first" quiz said a stray `System.out.println` in the server breaks the connection. We tried it: LangChain4j
  1.24's client skipped the line and the run worked. The quiz now says so, and that the MCP specification ("MUST NOT
  write anything to its stdout that is not a valid MCP message") and LangChain4j's server guide still forbid it.
- New step "What travels between them": the real JSON-RPC lines of one run, captured with `tee` on both streams,
  and a new still picture of them. It explains the failed `server/discover` request (the client tries protocol
  2026-07-28 first, then falls back to `initialize` with 2025-11-25), ids and the tool list.
- stdin, stdout, stdio and JSON-RPC are explained at first use.
- The classpath timeout reproduced word for word; running the server command by hand shows `ClassNotFoundException`
  (inside `exec:java`, `java.class.path` is Maven's `plexus-classworlds` jar). A missing `join()` and a typo in the
  class name give the same timeout; both are now the tasks' usual slips.
- Compiling without `-parameters` was tried: the client sees `arg0` and the tool gets `null`. Spring Boot's parent
  does turn it on (checked in the class file).
- The deep dive's list of Java server projects now matches LangChain4j's server guide (Tachyon added).
- A new sketchnote.

## 26 November: LangChain4j chapter 20 rewritten: a still fourteen-against-two picture, both slips tried

- Re-ran both versions in a lab machine: all fourteen tools gave the wrong answer again ("There are no notices
  related to any planned work"), 1,222 tokens in, after `search_files` on file names; two tools gave the right answer
  again (40 minutes late on 29 and 30 November), 305 tokens in, then 382 and 655. The lesson now says so.
- The animation is now a still picture of the two runs, from the gateway's log.
- Both tasks list the usual slip, each tried: no folder for the server (it starts and lists its tools, but every read
  is refused: "I'm unable to access the notices directly"), and a misspelled tool name in `filterToolNames` (no
  error; Setu lists the three notices but cannot read them).
- A new sketchnote.

## 26 November: LangChain4j chapter 19 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips (`nextOrSame` instead of `next`; a fresh `new RailTools()` that ignores the check's
  fixed clock).
- The tool-call animation is now a still picture of the real exchange (194 tokens, two tool requests, Java's results,
  263 tokens, the answer).
- Checked in a lab machine: the same answers and the same token counts as the lesson; the Mumbai question took one call
  and no tool. Checked in the lab's 1.24: `ReturnBehavior`, `@ToolMemoryId`, `toolExecutionErrorHandler(...)`. A new
  sketchnote.

## 26 November: LangChain4j chapter 18 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips, both tried: `@AiService` missing (the startup error is now quoted)
  and `@RequestBody` missing (a 500 error, "The value of parameter 'passenger' annotated with @MemoryId ... must not be
  null"; the first draft of this slip said Setu would get a `null` question, which was wrong).
- Checked in a lab machine: the three requests gave the same answers word for word. A new sketchnote.

## 26 November: LangChain4j chapter 17 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips, both checked: a new memory per call; one `.chatMemory(...)` with `@MemoryId` in the
  interface (tried: it builds and runs with no error, and every passenger shares one history).
- The memory animation is now a still picture of a real `MessageWindowChatMemory(10)`.
- Corrected: the system message counts as one of the N. With a system message and 6 questions and answers, 13 messages
  go into 10 and the oldest three are evicted (not two), so the kept history starts with an answer whose question is
  gone; the quiz and the concept now say so.
- Checked in a lab machine: Meera, Ravi and Asha gave the same answers word for word. A new sketchnote.

## 26 November: LangChain4j chapter 16 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips (completing the future in `onPartialResponse`; no `start()`).
- The streaming animation is now a still timeline from the measured run (first piece 905 ms, all 2,103 ms).
- Checked in a lab machine, twice: 55 pieces, first after 1,325 and 1,160 ms, all after 2,188 and 1,964 ms (now in the
  lesson). Checked in the lab's 1.24: `LambdaStreamingResponseHandler` and `StreamingHandle.cancel()` exist. A new
  sketchnote.

## 26 November: LangChain4j chapter 15 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips (keeping `String` and parsing yourself; returning `String` instead of the enum). A
  slip I first wrote was tested and dropped: `{{message}}` instead of `{{it}}` works in this project, which is compiled
  with parameter names; the lesson now says so.
- A new still picture of the real extraction, with the wrong date marked.
- Checked in a lab machine, twice: exactly the lesson's output, the wrong date (2026-11-26, a Thursday, for "this
  coming Saturday") included; the gateway's log shows the enum schema, `"strict": true` and `{"value":"TIMETABLE"}`.
  A new sketchnote.

## 26 November: LangChain4j chapter 14 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips (returning the `Prompt` object; a `@V` name that does not match its blank).
- Checked in a lab machine: the template run again (English and Marathi, new wording for both stations; the distances
  changed between runs, which the lesson now points out). Tried on the real `PromptTemplate`: a missing value fails with
  "Value for the variable 'question' is missing", a typed blank stays literal, and a missing `@V` gives the error now
  quoted in full. A new sketchnote.

## 26 November: LangChain4j chapter 13 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips (`new Assistant()`; importing the message class instead of the annotation).
- The AI Service animation is now a still picture of the real call: the proxy (`jdk.proxy3.$Proxy28`), the resource
  file, the messages, the answer.
- Checked in a lab machine: the same two lines, the proxy's name included; the gateway's log shows the system message
  exactly as the resource file holds it, final line break included. A new sketchnote.

## 26 November: LangChain4j chapter 12 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (`totalTokenCount()` for one side; integer division). The code line
  uses the real record's accessors.
- Corrected: this chapter's system message is 24 tokens (counted with o200k_base), not "about 40"; the 10,000-token
  rules book makes a question about 25 times dearer (the input part 56 times), not "fifty-fold". The arithmetic is now
  shown.
- Checked in a lab machine: the greeting was 37 in and 9 out again; the long question 48 in and 81 out. A new
  sketchnote.

## 26 November: LangChain4j chapter 11 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips ("do not guess" with nowhere to send the passenger; facts in the
  user message).
- A new still picture: each question's real answer without and with the timetable, against `timetable.txt`.
- Checked in a lab machine at temperature 0: word for word the same wrong "6:00 AM" and "Yes ... on Tuesdays" as
  when the lesson was written; the lesson now says a hallucination at temperature 0 is repeatable (so a test can catch
  it). The two court cases (New York 2023, Air Canada 2024) were checked. A new sketchnote.

## 26 November: LangChain4j chapter 10 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (`.temperature(0)` with an `int` does not compile; returning only the
  text loses the finish reason).
- Checked in a lab machine: at temperature 0 the slogan was word for word the one in the lesson, days later; three new
  slogans at 1.5; the 20-token answer was cut with `LENGTH`. The gateway's log shows what LangChain4j sent
  (`"temperature": 0.0`, `"max_tokens": 20`). A new sketchnote.

## 26 November: LangChain4j chapter 9 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (the real model name instead of the alias; returning the message
  object instead of its text).
- Checked in a lab machine: the same two introductions. Checked in the lab's LangChain4j 1.24: `chat(String)`,
  `chat(ChatMessage...)`, `chat(ChatRequest)` and `chatAsync` exist; the unverified "experimental" label was removed.
  A new sketchnote.

## 26 November: LangChain4j chapter 8 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (a base URL that already ends in `/chat/completions`;
  `.content().get()`).
- Checked in a lab machine: two more runs named no trains and both sent the passenger to "our website"; the lesson
  now says the invention comes and goes, which makes it easy to miss in a quick test. A new sketchnote (redrawn twice:
  the image model kept turning "the same HTTP POST" into a label).

## 26 November: LangChain4j chapter 7 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips, both tried: the key without `Bearer ` (401, "Invalid lab key");
  `path(0)` left out (an empty string, no error).
- The HTTP-call animation is now a still picture of the real call, from the program and the gateway's log.
- Checked in a lab machine: the real call (62 tokens in, 55 out, an answer just as vague); the HTTP/2 surprise
  reproduced exactly by putting `HttpClient.newHttpClient()` back; `gpt-99` gives a 400 with the message now quoted.
  A new sketchnote.

## 26 November: LangChain4j chapter 6 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips (multiplying by the temperature; `sqrt` of the number of keys instead of the vector
  length).
- Both animations are now still pictures: the real attention weights of "it" (0.46, 0.36, 0.18), and the six steps of
  an answer with the course's real numbers (9 tokens, about 200,000 scores, 0.73 at temperature 1); the picture says a
  generating model looks at the tokens before each token (causal masking), not "every other token".
- Checked: the softmax worked examples by hand (0.665, 0.245, 0.090; 0.867, 0.117, 0.016) and the solution's output in
  a lab machine (exactly the lesson's). A new sketchnote.

## 26 November: LangChain4j chapter 5 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (the dot product alone; comparing with the answers instead of the
  FAQ questions). The steps follow the real code (`ENTRIES` is a `Map`).
- The embedding-space animation is now a still bar chart of the real cosine scores (0.862, 0.763, 0.612, 0.564).
- Checked in a lab machine: the solution's output is exactly the lesson's; "Is there a canteen on board?" returned the
  pantry-car answer and "What is the capital of France?" the luggage answer, as the quiz says. A new sketchnote.

## 26 November: LangChain4j chapter 4 rewritten (easy, a little detailed, checked)

- All tasks list their steps or the usual slips (`text.length()`; skipping a message that does not fit; returning
  newest first).
- The context-window animation is now a still picture of the real chat, counted with o200k_base: 9, then 25 (34), and
  14 would make 48, over the budget of 40.
- Checked: every token split and id in the lesson, re-run with o200k_base (identical); the solution's output is exactly
  the lesson's. A new sketchnote.

## 26 November: LangChain4j chapter 3 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (a `HashMap`; `>=` on a tie, which makes "running" predict
  "twenty").
- A new still picture: the generated sentence step by step, with the count that chose each word (counted from the
  eight real announcements: "ghat" 3 of 7 after "the", "lonavala" 3 of 6 after "to", and so on).
- Checked in a lab machine: the solution's output is exactly the lesson's; the bigram table was recounted from the
  announcements. The history (Markov 1913, Shannon 1948, the 1954 IBM demonstration) was checked. A new sketchnote.

## 26 November: LangChain4j chapter 2 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (`>= 0`; forgetting the bias update, which makes some mornings
  impossible to get right).
- The neuron animation is now a still picture with the trained weights on one real morning.
- Checked in a lab machine: the solution's output is exactly the lesson's; the XOR experiment was run with the
  chapter's real `train` and gave the same four lines. Added: the weights after 10 epochs equal those after 1,000
  ([0.0, -0.1], bias 0.1), which shows why more training cannot help. A new sketchnote (one draft redrawn for a
  half-true line, one for a wrong bracket).

## 26 November: LangChain4j chapter 1 rewritten (easy, a little detailed, checked)

- Both tasks list the usual slips (checking before lower-casing; the constant's name in quotes; `<=` on a tie).
- The circles animation is now a still picture, with Setu's own example of each field.
- Checked in a lab machine: the solution's output is exactly the lesson's. Added what the numbers hide: 18 minutes also
  makes just 1 mistake, so 12 wins only by the tie rule, a choice a person made. The history (Turing 1950, Dartmouth
  1956, Samuel 1959, AlexNet 2012, the transformer 2017) was checked. A new sketchnote.

## 26 November: Spring AI chapter 20 rewritten; a real guard bug fixed; the Spring AI lab is done (20 of 20)

- Found and fixed a real bug in the assembled Atlas: the privacy guard had order 0, but the session advisors run at
  about minus two billion, so they saved "my phone number is ..." in the visitor's session before the guard refused
  it, and since `SafeGuardAdvisor` searches the whole prompt, every later question from that visitor was refused
  too (another visitor was fine). The guard now has `Ordered.HIGHEST_PRECEDENCE` in the solution (and the starter
  imports `Ordered`); re-tested: the number is refused, never stored (checked in the gateway's log), and the next
  question is answered. The lesson teaches it ("Test guards with a second message"); chapter 17's sentence that
  order 0 runs "before the session" was corrected.
- Both tasks list their steps and the usual slips (the session list inside the same `defaultAdvisors`).
- The animation is now a still picture of one real message through every piece.
- Checked in a lab machine: the same Moon, Saturday and shows answers with the same sources and seats. The follow-up
  "And when did it land there?" was answered this time (the lesson's run refused it); the lesson now says the pull
  between memory and retrieval goes either way. `CompressionQueryTransformer` and `RetrievalAugmentationAdvisor` exist
  in the lab's Spring AI; an unverified class name became the JDBC starter of chapter 6. A new sketchnote.

## 26 November: Spring AI chapter 19 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (asking for the desk and the answer in one call; a review loop with
  no count). The label task's steps now start the `drafts` counter, which the starter does not have.
- The workflows animation is now a still picture of both real workflows.
- Checked in a lab machine: the same three desks (the booking link comes from the BOOKING desk's own prompt), and the
  pendulum answer again explained an ordinary swing; the label loop again ran 3 drafts without approval, and the last
  review again said "more than 40 words" for a label of about 30: the lesson's lesson, reproduced. A new sketchnote.

## 26 November: Spring AI chapter 18 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (integer division before the price; `management.endpoint`
  singular, which leaves `/actuator/metrics` at 404).
- The cost-meter animation is now a still picture of the real meter and metrics, with the arithmetic shown.
- Checked in a lab machine: 95, 96 and 105 tokens in again; the metric gave input 296, output 131, total 427, and 854
  untagged, which confirms the lesson's "counted twice"; the same four metric names. The black-hole answer this time
  refused the detail but gave one sentence anyway. The tool-description cost now comes from chapter 7's real request
  (4 tools, about 170 tokens). An unverified detail about `getUsage()` and cached tokens became "the provider's
  usage data". A new sketchnote.

## 26 November: Spring AI chapter 17 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (calling the chain after building the refusal; a word list that is
  too broad).
- The guardrails animation is now a still picture of three real questions with the tokens the gateway counted.
- Checked in a lab machine: the three attacks were refused again (this time the pirate attempt still got a proper Moon
  answer); the gateway's token counter proved the two guards cost nothing (2,286 before and after) and that "my number
  is" reached the model (132 tokens); `SafeGuardAdvisor` ignores case (tried with capitals); `GuardrailRefusal`,
  `GuardrailRefusalException` and `OpenAiModerationModel` exist in the lab's Spring AI. A new sketchnote.

## 26 November: Spring AI chapter 16 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (comparing with the first result only; the judge on Atlas's own
  builder).
- The evaluation animation is now a still picture of both measurements with the real numbers.
- Checked in a lab machine (with the corrected pendulum card): retrieval gave exactly 10 of 15 and the same five
  misses; the judge's prompt in the gateway's log is word for word the lesson's; `RelevancyEvaluator.Builder` has
  `promptTemplate`. Found and taught: on the re-run the T-rex answer came out vaguer and the judge said false, where
  the lesson's run said true; the lesson now shows both, which is its own point about reading rates, not single
  verdicts. A new sketchnote.

## 26 November: Spring AI chapter 15 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (sending the unshrunk upload; no "answer none").
- The vision animation is now a still picture of the real pendulum photo with its token counts.
- Checked in a lab machine with the four real photos: the same answers, and exactly 8,595 tokens per `/look` and 8,815
  per `/identify`. The tile cost is now explained with OpenAI's numbers for gpt-4o-mini (2,833 + 5,667 per tile:
  25,501 for 4 tiles, 8,500 for one, plus the question), which match the measured 25,596 and 8,595. The skull's clue
  came out as "Fossil of a dinosaur" this time; the lesson now says a vague field gets a different answer each run.
  A new sketchnote.

## 26 November: Spring AI chapter 14 rewritten (easy, a little detailed, checked); the pendulum card corrected

- Both tasks list their steps and the usual slips (no threshold; no `distinct()`).
- The RAG animation is now a still picture of the real ticket question, read in the gateway's log (one chunk passed
  the threshold, 0.407).
- Checked in a lab machine: the augmented user message is word for word the lesson's, now read through the real
  model; the ticket, Moon and T-rex answers gave the same facts and sources. Found and fixed: the pendulum card said
  a full turn in Pune takes "about 76 hours"; a sidereal day over sin(18.5 degrees) is 75.4, so the card now says
  about 75 hours in all ten copies (starter and solution, chapters 12, 13, 14, 16 and 20), and the lesson shows the
  new real answer. Taught: the re-run said Vikram landed "on" the south pole where the card says "near"; read
  answers against their sources. The other card facts (Chandrayaan-3, Mangalyaan, Rajasaurus, Foucault 1851) were
  checked and are right. A new sketchnote.

## 26 November: Spring AI chapter 13 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (a config without the file; storing the documents instead of the
  chunks).
- The ETL animation is now a still picture of the real pipeline counts and the ticket search.
- Checked in a lab machine: the same 12 cards, 14 documents and 23 chunks, and scores within 0.003 of the lesson's
  (the ticket chunk 0.407, first). Corrected: "before the headings, the best ticket chunk scored 0.22" now says what was
  measured (the whole card, 0.219, in chapter 12). Added what learners will see in the real text: the reader joins the
  gallery line and the first paragraph without a space. A new sketchnote.

## 26 November: Spring AI chapter 12 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (adding cards one at a time; no threshold).
- Fixed a real lesson bug: the task said to wait for "Loaded 12 exhibit cards...", but that line was only in the
  solution, so a learner would never see it; printing it is now step 2 of the task.
- The vector-store animation is now a still picture of the real start-up and one real search.
- Checked in a lab machine: the same four searches with exactly the same scores (embeddings are deterministic). Measured
  without the threshold: good matches 0.54 and 0.64, unrelated cards 0.02 to 0.29 (the lesson said 0.1 to 0.3), the
  ticket card only 0.219. Counted in the backend's log: twelve embedding requests for twelve cards, about 0.4 s
  apart, which confirms "one request each". A new sketchnote.

## 26 November: Spring AI chapter 11 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (returning the dot product alone; one request per exhibit).
- The embeddings animation is now a still picture of real scores: one question against the six exhibits.
- Checked through the gateway: the `/embed` example's numbers and 1,536 dimensions; the four questions found the same
  four exhibits. Corrected: "a good match 0.5 to 0.7, unrelated 0.1 to 0.3" was too high for this model; measured,
  the right exhibit scored 0.37 to 0.55 and the others 0.02 to 0.37 (the dinosaur question was a narrow win, 0.367
  against 0.323). The same text embedded twice gave cosine 1.0. The cost of embedding the cards is now worked out
  from their real size (1,152 words). A new sketchnote.

## 26 November: Spring AI chapter 10 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips, both tried: a misspelled protocol value (`STREAMING`) starts the
  app with no error but no MCP server (`/mcp` gives 404); a provider method without `@Bean` gives `{"tools":[]}`.
- The MCP animation is now a still picture of the real session: four messages and Atlas's answers.
- Checked in a lab machine: initialize, the 202 for `notifications/initialized`, the same four tools and Saturday's
  seats, word for word; added the real "Session ID missing" error for a call without the header. A new sketchnote.

## 26 November: Spring AI chapter 9 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (counting before `chain.nextCall`; replacing the system message).
- The advisor-chain animation is now a still picture of the real Marathi call as boxes inside boxes (104 in, 50 out,
  154 counted).
- Checked in a lab machine: three languages again, the meter `{"calls":3,"tokens":463}` (matching the gateway's
  log), and "Answer in Marathi." as the system message's last line. The quiz's claim was tried: an advisor that
  returns `null` fails `/ask` with a `NullPointerException`, and no model call happens. `ChatClientMessageAggregator`
  exists in the lab's Spring AI. Corrected: `SimpleLoggerAdvisor` is not used in chapter 19 (now explained in place);
  the picture no longer claims which of two equal-order advisors is outside. A new sketchnote.

## 26 November: Spring AI chapter 8 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (`requiresConfirmation` on `@ToolParam`; a different context key).
- Both animations are now still pictures from real runs: the booking proposed, paused, confirmed and run; and the
  "for my friend Sam" request, with the model's arguments, the app's tool context and the tool's real result.
- Checked in a lab machine: the pending call and the yes, the improved deny message, 7 seats refused without a tool
  call. Found and taught: asked as Ria to book "for my friend Sam", the booking was Ria's (the tool context worked)
  but the model's sentence said "for your friend Sam"; a real app shows the booking from the tool's result. The
  thrown-error path is now a real run ("Only 5 seats are free for the 16:00 show", and Atlas offered 5); the made-up
  example ("Only 4 seats ... 11:00") is gone, and the lesson says the service starts each show at 20 seats. Checked in
  the lab's Spring AI: `ToolCallConfirmationPolicy`, `spring.ai.tools.confirmation.tools`, and `spring.ai.tools.limits`.
  An unverified "refuses to resume" was removed; agents are chapter 19 (not 20). A new sketchnote.

## 26 November: Spring AI chapter 7 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (comparing a date with "Monday"; tools never offered with
  `.tools(...)`; passing the `String` to `showsOn`).
- The tool-calling animation is now a still picture of the real "this Saturday" conversation from the gateway's log.
- Checked in a lab machine on 26 November: "next Monday" went through `nextDay` and `openingHours` to "closed";
  "this Saturday" through `nextDay` (2026-11-28) and `planetariumShows` to 4, 0 and 11 seats; three model calls per
  question. The tool description is now marked as shortened (the real one also has `$schema`,
  `additionalProperties` and `strict`). Corrected: chapter 8 covers confirmation and the tool context (not "limits and
  errors"); the Tool Search Tool is in the Spring AI 2 reference, not in this lab's image. A new sketchnote.

## 26 November: Spring AI chapter 6 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (no session id, tried: "No session ID found in advisor context";
  the id in quotes; the compaction numbers swapped).
- The memory animation is now a still picture of the real tenth request, read in the gateway's log: the system
  message, turns 6 to 9 and question 10, exactly as the quiz says.
- Checked in a lab machine: Ria, Sam and the delete gave the same results. Checked in the lab's Spring AI: the
  60-day default expiry, `asyncCompaction`, `lastTurns`, `tokenBudget`, `TokenCountTrigger`, and that
  `MessageChatMemoryAdvisor` is deprecated. Corrected: the JDBC repository's databases now follow the Spring AI 2.1
  reference (PostgreSQL, MySQL, MariaDB, H2; SQL Server removed); an unverified docs quote ("for tests and demos")
  became plain words; cross-references: logging is chapter 18 (not 19), retrieval chapter 14 (not 10). A new
  sketchnote.

## 25 November: Spring AI chapter 5 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (`.content()` with a `String` return; `.entity(List.class)`).
- The structured-output animation is now a still picture of the real tour request and answer.
- Checked in a lab machine: the instructions Spring AI adds were read in the gateway's log and match the lesson word
  for word; a new tour (5 stops adding up to 60, all invented). Found and taught: the bare `List<String>` version
  failed 1 time of 3 on the re-run (worse than always failing); Spring AI's converter strips ```json fences, but a
  sentence before the JSON fails (`StreamReadException`), tested on the converter directly. Checked that
  `useProviderStructuredOutput()` and `validateSchema()` exist in the lab's Spring AI, and that the retry limit
  (`maxRepeatAttempts`) is 3; two unverified details (usage of all attempts, a quiet fallback) were removed.
  Cross-references fixed: real data in chapters 11 to 14 (not 8 to 10), retrieval chapter 14 (not 10). A new
  sketchnote.

## 25 November: Spring AI chapter 4 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (`.call()` wrapped in `Flux.just`; events with no name; a `done`
  built inside `map`).
- The streaming animation is now a still timeline from one measured run (first byte 0.96 s, all 1.94 s).
- Checked in a lab machine: three more timings (first byte 0.96 to 1.5 s, all 1.9 to 3.2 s). Corrected: the event
  stream's format in Spring Boot 4 is `data: The` (a space after the colon, so a token's own space shows as two),
  and both printed streams are now real output; the vague "studies of web pages" became Nielsen's one-second and
  ten-second rule of thumb (1993); usage in streams is now said exactly (the LabBox gateway always asks for it, as
  its code shows). A new sketchnote.

## 25 November: Spring AI chapter 3 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (only one of the two options; keeping `.content()`).
- The temperature animation is now a still picture with real numbers: the model's own probabilities for the first
  piece of a robot's name (Muse 77%, Art 22.1%, Museum 0.3%, from the gateway with `logprobs`) and the real runs.
  The invented "blue 70%, clear 10%" example is gone.
- Checked through the gateway: temperature 0 gave MuseBot three times, though one sentence was worded differently
  (so 0 is not perfectly repeatable); 1.5 gave three names; the 12-token cap gave the same cut and `length`; the
  costed answer was 96 tokens in again (79 the system prompt's text, 6 the question, the rest message format, now
  said exactly instead of "about 85"). Cross-references fixed: caching and the cost meter are chapter 18 (not 13),
  retrieved documents chapter 14 (not 10). Price ratios now "often ten times or more". A new sketchnote.

## 25 November: Spring AI chapter 2 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (rules in `.user(...)`; `defaultSystem` on the built client; a
  placeholder name that does not match).
- The roles animation is now a still picture of one real request's three messages.
- Checked in a lab machine through the gateway, with the improved prompt and with the first draft rebuilt: the
  improved prompt gave the same three kinds of answer. Corrected: the first draft refused Saturn "every time" when the
  course was written, but 2 times of 3 on the re-run (and the answer it gave invented "our space exhibit"); the adult
  refusal also came 2 times of 3. The lesson now says an unclear rule fails some of the time. The missing-placeholder
  error is now quoted from a real run. Cross-references fixed: safety is chapter 17 (not 12), automated tests chapter
  16 (not 11). The cost note now uses the real prompt: 79 tokens, about $1.19 per 100,000 requests. A new sketchnote.

## 25 November: Spring AI chapter 1 rewritten (easy, a little detailed, checked); notes pages become sketchnotes

- Notes pages are now tall sketchnotes (owner, 25 November night): title, a definition box, a flow of boxes and a
  highlighted list, from a "sketch" job in `tools/authoring/notes.py`. Read mode keeps notes pages at full height.
- Both tasks list their steps and the usual slips (`.user("q")` in quotes; the real model name, tried: the gateway
  refuses `gpt-4o-mini` too).
- The request animation is now a still picture of one real question with the gateway's numbers.
- Checked in a lab machine through the gateway: "planetarium" is 2 tokens (planet + arium); the black hole answer
  was 449 tokens in 6.7 seconds (about 67 a second, $0.000271); the cost table now uses those numbers and shows its
  arithmetic. Corrected: the error's alias list (no `lab-code` now), embeddings are chapter 11 (not 8), cost is
  chapter 18 (not 13), the LabBox tutor no longer runs on an open model, and "ten to a hundred times" became "often
  ten times or more". Added: the gateway caps answers at 1,024 tokens (`max_tokens` in its log).

## 25 November: LangChain chapter 27 rewritten; the LangChain lab is done (27 of 27)

- Store, namespace, key and FastAPI are explained where they first appear; both tasks list their steps and the usual
  slips, tried on the store and the agent: a string namespace is read letter by letter, a plain-text value raises
  `ValueError`, one fixed key overwrites, and a missing `context=` fails with `AttributeError` before any model call.
- A new still picture: one member, two threads, one store, from the real run.
- Checked through the lab gateway: `try.sh` gave the same six results, the Monday and Friday threads the same
  Rs 1,50,000 from the saved fact (`remember` on Monday, only `search_rules` on Friday), and the Aadhaar message was
  saved masked and kept out of the store. Corrected: the history table no longer says chapter 24 covers prompt
  injection (no chapter does). A new notes page.
## 25 November: Ukiyo logo, "by" in lowercase

- The logo's byline reads "by TELUSKO": the company name stays in capitals, "by" is lowercase (owner's request).
  Ukiyo only; master already writes "by Telusko".

## 25 November: LangChain chapter 26 rewritten (easy, a little detailed, checked)

- Evals, golden set, pass rate and judge are explained where they first appear, with a table of unit tests against
  evals; both tasks list their steps and the usual slips (lower-casing only the answer; a count instead of a share;
  `invoke` without `with_structured_output`).
- Checked through the lab gateway, three times: 67% every run, the same two failures (80 crates, the joining fee) and
  the same verdicts from the judge. One run is 16 chat calls and 6 embedding calls (from the backend's log), about
  $0.001; the cost of 200 questions is now worked out (about $0.04). Found and taught: the lab allows 20 model calls a
  minute, so a second run straight after the first stops with a 429; wait a minute. The LLM-as-a-judge study is now
  stated with its numbers (over 80% agreement, as often as two humans) and its three biases; SUnit is "published in
  1994". A new notes page.

## 25 November: LangChain chapter 25 rewritten (easy, a little detailed, checked)

- Human in the loop, the checkpointer, `interrupt_on` and `__interrupt__` are explained where they first appear; both
  tasks list their steps and the usual slips, all tried: a misspelled tool name (no pause, and the booking was made
  without the manager), `resume=decision` without the wrapper (`KeyError: 'decisions'`), a different thread id.
- The booking animation is now a still picture of Ravi's real booking (80 asked, paused, edited to 50, B-101).
- Checked through the lab gateway: the same three pauses and bookings, and the same invented "try another crop". The
  lesson now quotes what the model really receives after an edit and a reject (from LangChain's source and the run),
  and the suggested fix was tried: a reject message that says what to do gave that answer 3 times of 3, with nothing
  added. Added the fourth decision (`respond`) and `interrupt_mode`. Corrected the vault photo: the lock was in use
  from 1856 to 1885 (not "an 1883 bank"), and the two-person rule is now said of vaults in general. A new notes page.

## 25 November: LangChain chapter 24 rewritten (easy, a little detailed, checked)

- PII, the regular expression (piece by piece), state and the Verhoeff check digit are explained where they first
  appear; both tasks list their steps and the usual slips (`search` finds only the first number; `len()` of a message
  object; leaving out `jump_to`, tried: the model was called anyway and the member got two answers).
- A new still picture: the chapter's two real messages through both guards, with the gateway's token counts.
- Checked in the lab: all four strategies give the table's outputs; the gateway's request held only `****1176`; no
  request at all for the 717-character message. Corrected: the length guard runs first because `before_agent` hooks
  run before `before_model` hooks (`PIIMiddleware` is one), not because of its place in the list. The history now
  says the Aadhaar Act "set rules" (and the 2018 Supreme Court limit), adds UIDAI's masked Aadhaar, and drops "land
  records". The example number fails the Verhoeff check, so it cannot be anyone's. A new notes page.

## 25 November: LangChain chapter 23 rewritten (easy, a little detailed, checked)

- Decorator, `ModelRequest` and `ToolCallRequest` are explained where they first appear; both tasks list their steps and
  the usual slips (a lost space between the two prompt sentences; `request.tool_call.name` on a dict).
- A new still picture: `audit_tools` around one real tool call (25 x 8 x 2 = 400).
- Checked through the lab gateway: Marathi for Ravi, English for Asha, 400 both times, the same two audit lines. Found
  and taught: a wrapper that returns nothing stops the run with `NotImplementedError: Unsupported message type`; to
  block a call, return a `ToolMessage` (tried: the model told the member bookings are closed). The order of hooks was
  checked with two middleware (before in list order, after in reverse, wraps nested). The history now says Kiczales
  "described" cross-cutting needs (the name came later). A new notes page.

## 25 November: LangChain chapter 22 rewritten (easy, a little detailed, checked)

- Middleware and hooks are explained where they first appear; both tasks list their steps and the usual slips
  (sending every exception's text to the model; passing `on_tool_error()` with brackets).
- The middleware animation is now a still picture of one run's hooks, with what this chapter's middleware does at each.
- Checked through the lab gateway: the six-turn conversation kept 2, 4, 8, 8, 8 and 6 messages, and the thread starts
  with a summary message. Corrected: "grows to 8 and then stays there" became "stays at 8 or below" (older messages
  are replaced by one summary plus the newest 4). The tool-error trace now names the real question and was reproduced
  (1850, then garlic's error as a message). "The docs put it plainly" became the lab's checked behaviour (without the
  middleware, a tool exception stops the run, as chapter 11 showed). A new notes page.

## 25 November: LangChain chapter 21 rewritten (easy, a little detailed, checked)

- Protocol and JSON-RPC are explained where they first appear; both tasks list their steps and the usual slips
  (checked: FastMCP 4.2.5 accepts both `@mcp.tool` and `@mcp.tool()`).
- The MCP animation is now a still picture of the real run, across two processes.
- Checked through the lab gateway: the beta warning, the two tools, 4,600 and 120 again. Added what learners really
  see: FastMCP's banner and its "Starting MCP server" line, on standard error, which ties to the quiz on printing to
  standard output. Corrected: "supported by most AI apps within months" became "OpenAI, Google, Microsoft and many
  frameworks". A new notes page.

## 25 November: LangChain chapter 20 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (changing a chunk in place spoils the comparison).
- Checked through the lab gateway: every line of the output again, both query rewrites included (the confident
  "costs of joining the cooperative" and the right "cost to store onions"). Added the honest limit of eight questions:
  one question moves a hit rate by 12.5 points, and 88% is 7 of 8. A new notes page.

## 25 November: LangChain chapter 19 rewritten (easy, a little detailed, checked)

- RAG is explained where it first appears; both tasks list their steps and the usual slips.
- The RAG animation is now a still picture of the storage question with the real query and scores.
- Checked through the lab gateway: the storage answer is wrong the same way again ("50 need to be booked at the
  counter"), so the half-rule cause is steady; the run showed the real query and chunks. A new real mistake found and
  added: the spraying answer said "wait until the following Monday", but ten days after a Monday is the Thursday of the
  week after next (date arithmetic). "The most widely used pattern" became "one of". A new notes page.

## 25 November: LangChain chapter 18 rewritten (easy, a little detailed, checked)

- Vector store is explained where it first appears; both tasks list their steps and the usual slips.
- Checked through the lab gateway: every score word for word, 1,536-number vectors, and 9 embedding calls for one run
  (one batch for the chunks, eight for the questions). Corrected: "real matches score about 0.4 to 0.7" became the
  measured range (0.298 to 0.609, labelled as this model and rule book); "a store always returns k results" now says
  "its k nearest (if it holds that many)". A new notes page.

## 25 November: LangChain chapter 17 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (the whole path as the source; split_text losing the metadata).
- Checked in a lab machine: the output word for word, including the heading chunk and the rule cut at "Bookings of
  more than 50"; 2,000 characters really gives one chunk per file (5), now in the quiz. Corrected: Dense Passage
  Retrieval's gain is now the paper's own figure (9 to 19 points more often than BM25 among the top 20), not "far
  better"; "langchain-community is being retired" (not confirmed) became "many loaders live in langchain-community
  (0.4.2 in the lab) or in separate packages". A new notes page.

## 25 November: LangChain chapter 16 rewritten (easy, a little detailed, checked)

- Both tasks list their steps and the usual slips (calling on_line only at the end; no node filter).
- Checked through the lab gateway twice: the same steps every time, tools asked for after 2.0 and 1.5 s and answers at
  3.6 and 3.1 s (the lesson's run: 2.35 and 3.95), now given as a range. Corrected: Myers (1985) found that people
  prefer progress indicators (the lesson said more); "the docs now recommend stream_events v3" became what the lab's
  LangGraph has (versions v1, v2 the default, and v3). A new notes page.

## 25 November: LangChain chapter 15 rewritten (easy, a little detailed, checked)

- Stateless, checkpointer, thread and config are explained where they first appear; both tasks list their steps and
  the usual slips (a new saver per message; one thread id for everyone).
- The threads animation is now a still picture of the real run: Ravi's thread and Asha's, side by side.
- Checked through the lab gateway: the same behaviour in slightly different words (Ravi remembered, 1,200 rupees,
  Asha asked for her crates, Ravi's name kept); chapter 27 does cover the long-term store. Corrected: ChatGPT's memory
  is described as OpenAI describes it (saved memories the app brings into later chats). A new notes page.

## 25 November: LangChain chapter 14 rewritten (easy, a little detailed, checked)

- Content block, MIME type and tile are explained where they first appear; both tasks list their steps and the usual
  slips (the leaf report's slip now matches what the check tests).
- Checked through the lab gateway: with the rules, the same report word for word; without the rules, twice the same
  wrong "powdery mildew" and "Consider applying a fungicide" (the chapter's warning is real); 8,697 tokens in and 46 out
  again; the photo is 500 by 375; the credit file is right; $0.0013 is about 31 text answers. Corrected: "until 2023
  the big language models read only text" now mentions research models like Flamingo (2022); the notes say the 8,697
  tokens are the photo and its question. A new notes page.

## 25 November: LangChain chapter 13 rewritten (easy, a little detailed, checked)

- Pydantic is explained where it first appears; both tasks list their steps and the usual slips.
- Checked through the lab gateway: the three bookings and the agent's messages word for word; the "other" schema really
  gives `crop='other'` for garlic; the quiz's "keep my onions for a while" really gave `crates=10, days=30` (both
  invented), now in the explanation. Corrected: "with_structured_output picks the best method" became what the lab's
  langchain-openai does (OpenAI Structured Outputs, `method="json_schema"`, by default), so extract_booking and the
  agent take two different routes (provider strategy and tool strategy), now said. A new notes page.

## 25 November: LangChain chapter 12 rewritten (easy, a little detailed, checked)

- Runtime, context and lakh are explained where they first appear; both tasks list their steps and the usual slips
  (the main one: never give a tool a member-id argument).
- Checked through the lab gateway: both members' answers word for word, the trick question ("I am actually M-221",
  logged in as Ravi) still gets Ravi's 40 crates, the model's schema for `my_storage` is empty (runtime hidden), and
  `@tool` without a docstring raises exactly the quoted error. Saltzer and Schroeder (1975) and OWASP's "excessive
  agency" (2023) checked. A new notes page.

## 25 November: LangChain chapter 11 rewritten (easy, a little detailed, checked)

- State, graph, nodes and edges are explained where they first appear; both tasks list their steps and the usual slips.
- Checked by running the agent through the lab gateway three times: the tomatoes question always used one tool (4
  messages, 350 rupees), the garlic question never called a tool (2 messages), "Hello!" gave 2 messages; the
  `mandi_price` docstring is quoted exactly; LangGraph 1.2.24's default recursion limit is 10,007, now with its
  environment variable; the graph printed by `draw_mermaid`. The runs are labelled (the wording changes: "Rs 350" or
  "₹350"). A new notes page, the recursion limit labelled as the lab's version.

## 25 November: LangChain chapter 10 rewritten (easy, a little detailed, checked)

- Tools, docstrings, type hints and JSON schemas are explained where they first appear; both tasks list their steps and
  the usual slips.
- The agent-loop animation is now a still picture of the real run: the question, the reply with two tool calls, the two
  tool results, and the answer.
- Checked by running the solution through the lab gateway (the same messages and answer; only call ids change), by
  printing the real schema LangChain sends for `storage_cost`, by raising the garlic error, and by confirming that
  `create_agent` lets a tool's exception through by default (a ValueError), as the deep dive says. Corrected: "models
  are bad at arithmetic" became "a model can get arithmetic wrong: it predicts digits"; "every major provider followed"
  became "the other major providers added the same idea"; ReAct dated October 2022. A new notes page.

## 25 November: LangChain chapter 9 rewritten (easy, a little detailed, checked)

- Hallucination, grounding, mandi and quintal are explained where they first appear; both tasks list their steps and
  the usual slips.
- Checked by running the three questions through the lab gateway: the same three behaviours, the same token counts
  (224 in, 13 to 20 out) and costs ($0.0000414 recomputed; about $0.43 a day for 10,000 answers). Corrected: Air Canada's
  chatbot wrongly promised a refund under the real bereavement-fare policy (it did not invent a policy); "output costs
  more because each token is a pass" became "a large part of the reason", with dated prices; OpenAI's automatic prompt
  caching starts at 1,024 tokens, so it does not yet help Navin's 224-token card. A new notes page.

## 25 November: LangChain chapter 8 rewritten (easy, a little detailed, checked)

- Parameters and chunks are explained where they first appear; both tasks list their steps and the usual slips.
- Checked by streaming through the lab gateway four times and opening a stream's chunks: the text was the same every
  time (149 characters, 38 chunks), but the first piece came after 0.8 to 1.3 s and the whole answer after 1.2 to 1.9 s,
  so the lesson now gives that range instead of one exact time (769 ms). Corrected: the end chunks are one with the
  finish reason, one with the token usage and one empty; `data: [DONE]` is OpenAI's own ending, not every API's; the
  task's "usual slip" now matches what the check really tests. The check's success message said "the passenger reads"
  (a word from another course): it now says "the member". A new notes page.

## 25 November: LangChain chapter 7 rewritten (easy, a little detailed, checked)

- Interface and integration package are explained where they first appear; both tasks list their steps and the usual
  slips.
- Checked by running the solution through the lab gateway: the same words as the lesson (temperature 0), a
  `ChatOpenAI`, an `AIMessage` with usage, and the lab's versions (langchain 1.5.2, langchain-core 1.8.4,
  langchain-openai 1.8.5). Corrected: "grew faster than almost any open-source project of its time" became "one of the
  fastest-growing open-source projects of 2023"; "switch provider: change one string" now adds installing that
  provider's package (as the quiz already said). A new notes page.

## 25 November: LangChain chapter 6 rewritten (easy, a little detailed, checked)

- SDK, client, retries and async are explained where they first appear; both tasks list their steps and the usual slips.
- Checked by running the solution through the lab gateway and reading the installed SDK itself (openai 3.57.0): the
  default is 2 retries, and the SDK retries lost connections, timeouts and HTTP 408, 409, 429 and 500 and above, never
  401; the co-op's Rs 2 a crate a day for cold storage is in its handbook (chapter 9). A second run gave the same
  confident wrong "no" (61 tokens in, 28 out), now noted. Corrected: "every provider ships an SDK" became "most"; the
  retry list is now exactly the SDK's. A new notes page.

## 25 November: LangChain chapter 5 rewritten (easy, a little detailed, checked)

- Web API, HTTP request, POST, JSON, header and environment variable are explained where they first appear; both
  tasks list their steps and the usual slips.
- The request animation is now a still picture of the real request, there and back, with the gateway's numbers.
- Checked by running the real request through the lab gateway (approved) and reading `lab requests --last`: 61 tokens
  in, 38 out, max_tokens 1024 added, 42 + 8 tokens counted locally. A second run guessed "closed on public holidays"
  too, now in the lesson. Corrected: "a chat model is a web API" became "a hosted chat model" (models can run locally);
  "nearly every provider, from Mistral to ..." became "many providers and servers, including Ollama and vLLM". A new
  notes page.

## 25 November: LangChain chapter 4 rewritten (easy, a little detailed, checked)

- Logit, softmax, exp, temperature, query, key, value, heads and parameters are explained where they first appear;
  tasks list their steps and the usual slips.
- The next-token animation is now a still picture of the real 13 tokens of Navin's answer, one pass per token.
- Checked by running the solution and the tokenizer in a lab machine. Corrected: "Today's" is one token, not "Today" and
  "'s"; "the model did not plan that sentence" is not established (planning inside models is still researched);
  the four next-word scores are said to be made up; "spray never" is 0.03%; temperature 0 is steady, not perfectly
  repeatable on a hosted API; "every model behind Navin is a transformer" became what OpenAI says (GPT-4 is
  "Transformer-style"; gpt-4o-mini's design is unpublished); the "it rained" example no longer claims what a good model
  would attend to (that "it" refers to nothing); the transformer's eight authors were most, not all, at Google. A new
  notes page.

## 25 November: LangChain chapter 3 rewritten (easy, a little detailed, checked)

- Embedding model, vector, dimensions, cosine similarity and dot product are explained where they first appear, with a
  cosine worked by hand; tasks list their steps and the usual slips.
- A new still picture, `lc-cosine-matrix`: the real cosines of the five new questions against the five FAQ questions.
  It replaces an invented two-dimensional table.
- Checked by running the solution in a lab machine: every printed score, the quoted vector values and 85 tokens
  (cl100k_base). Corrected: "the model understands Marathi in English letters far less well" (a guess) became what we
  measured (a weak match, 0.043 above the next); the lesson now shows that a non-match (0.34) can score higher than a
  real match (0.155), so there is no fixed "related" number; the embedding price is dated. A new notes page.

## 25 November: LangChain chapter 2 rewritten (easy, a little detailed, checked)

- Tokenizer, vocabulary, bytes, context window and budget are explained where they first appear; the tiktoken code is
  read line by line; tasks list their steps and the usual slips.
- A new still picture, `lc-tokens`: the real o200k_base pieces of the same question in English (7), Devanagari (8)
  and Marathi in English letters (11).
- Checked by running the solution in a lab machine: the counts, the trace (10, 9, 8, 10 tokens), the vocabulary
  (200,019 entries) and 131 tokens per 100 English words on chapter 1's story. Corrected: 11 against 7 is about 57%
  more, not 40%; the story no longer says people guess English is cheapest (it is); the output limit (16,384 tokens)
  is added; the price ratio is dated (gpt-4o-mini $0.15 and $0.60 per million, November 2026). A new notes page.

## 25 November: LangChain chapter 1 rewritten (easy, a little detailed, checked)

- Language model, neural network, layers, threshold and accuracy are explained where they first appear; the worked
  rule is read line by line; tasks list their steps and the usual slips.
- The circles animation is now a still picture: each field inside the one before, with this course's own example.
- Checked by running the solution in a lab machine (outputs and every threshold's accuracy recomputed; the table now
  shows five real rows). Corrected: the definition "without being explicitly programmed" is a later paraphrase, not
  a sentence from Samuel's 1959 paper; ChatGPT's hundred million users is a UBS estimate about two months after launch,
  not "within weeks"; Hinton's Nobel is now quoted as the citation says, shared with Hopfield; "the most used Python
  library" became "one of the most widely used"; the name AI comes from McCarthy's 1955 proposal for the 1956
  workshop. A new notes page.

## 25 November: Action mode can hide the lesson panel

- The same sidebar button as in Read mode, at the top right of the lesson panel, hides the whole panel: the editor and
  terminal take the page. A slim rail on the left keeps "Show the lesson" and Check (so work can still be checked).
  The choice is remembered. New browser test `lesson-panel.spec.ts`; 33 browser tests pass.

## 25 November: Start machine lives in the Machine menu

- No separate "Start machine" button beside the Machine menu (owner): the menu now has Start, Stop and Reset, each
  enabled only when it makes sense; the status dot still shows Running or Stopped. The banner that says why a
  machine stopped keeps its own Start button. Check results say "coming up in scene N".

## 25 November: lesson steps are called scenes

- The owner's choice: "Scene 7 of 14" above each lesson, in the dot labels, the Read-mode list ("Scenes in this
  chapter"), the dashboard's Continue card, the course page and the home page tour. Counters inside diagrams, traces
  and onboarding still say "step". The browser tests follow the new name.

## 25 November: Read mode lists the chapter's steps on the left

- On screens 1,000 px and wider, Read mode shows every step of the chapter by name in a column on the left (the current
  step highlighted, tasks and quick checks labelled, any step one click away). A sidebar button (a panel icon in a
  rounded square, as in the Telusko admin) opens it and closes it entirely; it starts closed (owner) and the choice is remembered. The rest of Read mode is unchanged. Browser test extended.

## 25 November: Read mode and Action mode in every lab

- A Read / Action switch in the lab's top bar (owner, 25 November). Read mode shows the lesson alone in a calm centred
  column (68 characters a line, larger pictures), with no editor, terminal or machine controls, and starts no machine.
  Action mode is the split screen as before. The last mode used is remembered; a first visit reads. Phones always read.
- In Read mode a step about a file shows those lines read-only under the step, from the learner's own files (new route
  `GET /api/labs/{lab}/chapters/{chapter}/steps/{n}/code`, no machine needed), with the step's lines marked. A task
  step shows a card, "Your turn: open the lab", whose button opens Action mode; "Run in terminal" opens Action mode and
  pastes the command once the terminal is connected. The machine starts quietly one step before a task, so the wait is
  mostly over by then.
- Tests: a backend test for the route, a browser test for both modes and the switch; Playwright's default storage
  starts the other browser tests in Action mode. 237 backend tests on Postgres and Redis, 32 browser tests.

## 25 November: RAG chapters 11 and 13, the model's answers re-checked

- With the owner's OK, the chapter 11 questions (five) and the chapter 13 `/ask` requests were run again through the
  lab's model gateway, in a test account's lab machine started the normal way. Every answer matched the lessons word for
  word; the lessons now say so. The test account's machines, network and folder were removed afterwards.

## 25 November: browser tests clean up after themselves

- New `scripts/labbox test-accounts max-id | cleanup [--since-id N] [--dry-run]`: removes the lab machines, lab networks
  and workspace folders of browser-test accounts (named a prefix plus 6 or more digits, never id 1, never an admin);
  account rows stay. Playwright's global setup notes the highest account id and the global teardown cleans only the
  accounts that run signed up (`LABBOX_E2E_KEEP=1` keeps them for debugging). Unit test in `test_cli.py`.
- One-time cleanup, approved by the owner: 356 stopped test machines and 2,704 test folders removed (volumes 66 GB to
  962 MB); the owner's 30 machines and folder untouched. A full browser run (31 passed) then left no test machine.
## 25 November: Ukiyo home, the container's name plate no longer cut

- The plate ("LOADING 3/5", "RUNNING") sat on the container's bottom edge, which hid the lower half of its letters. It
  now sits 10 units higher, fully on the wall (checked at 390 and 1280 px wide).

## 25 November: RAG chapter 13 rewritten (easy, a little detailed, checked); the RAG lab rewrite is complete

- Web services, HTTP, endpoints, GET and POST, query strings, JSON and the 422 code are explained where they first
  appear; tasks list their steps and the usual slips.
- A new still picture, `rag-service`: one POST /ask through the service, with the times measured on 2 CPUs.
- Checked by running the real service in the lab image: both searches return exactly the lesson's results and scores,
  the 422 matches, and the entry-fee question came back NOT_FOUND with the model gateway unreachable (proof that the
  gate makes no model call). Corrected: the first request took 6.2 s in one run and 8.5 s in another (now both), repeats
  0.5 to 0.9 s; `find` only filters hybrid search's at most 40 candidates (now said, with the fix); the course table's
  "full recall after rescoring" is 99.8% on synthetic vectors, and each measured number names its data. A new notes
  page ("a real service usually keeps its vectors in a database"). Chapter 2 now says 512 tokens, about 380 words,
  like chapter 4 (it said about 400).

## 25 November: RAG chapter 12 rewritten (easy, a little detailed, checked)

- Golden sets, hit rate, reciprocals and MRR are explained where they first appear, with a real worked example (dense:
  24 / 26 = 92% at 5, 20 / 26 = 77% first); tasks list their steps and the usual slips.
- A new still picture, `rag-eval`: hit@1 and hit@5 of the four pipelines from the real run, with their times.
- Checked by re-running `evaluate.py` on 2 CPUs: every percentage and MRR matches; the times now show this run (4, 20,
  23 and 1,696 ms) and are labelled as the lab machine's. Corrected: keyword search misses CT-112 because seven chunks
  share one word each ("record", "did" or "ct-112") and ties keep the documents' order (R-0301 6th), not only because
  of "record"; hybrid brings the codes to 2nd place, not first; "the model reads the first source most carefully"
  replaced by what is known (the gate checks the first source); "75 times slower" is about 80 times in this run; the
  conclusions are labelled as holding for these questions and documents. A new notes page.

## 25 November: RAG chapter 11 rewritten (easy, a little detailed, checked)

- Grounded answers, the system message, NOT_FOUND, the model gateway's `lab-chat` name and temperature are explained where
  they first appear; tasks list their steps and the usual slips.
- A new still picture, `rag-gate`: all 34 real best reranker scores on one number line (26 answered questions, 8 that
  the documents do not answer) with the gate at -9.0.
- Checked by re-running the two-stage search in the lab image (no paid model call: the answers in the lesson are now
  labelled as one real run whose wording may vary). The 26 answered scores match exactly. Corrected: the original eight
  unanswerable questions were never saved, so the table is now a measured, named set (-11.0 to 3.3); the deep dive's
  garbled "first and last-but-not-least" became the "Lost in the Middle" finding (2023) with Fieldbook's real chunk sizes
  (19 to 95 words); footnotes date from the 1500s and were common by the 1700s; WebGPT collected references while
  searching; the quiz's arithmetic for a gate at 0 (6 of 8 blocked, 3 of 26 real ones lost); -9.0 is labelled as this
  reranker's and these documents' value. A new notes page.

## 25 November: RAG chapter 10 rewritten (easy, a little detailed, checked)

- Bi-encoders and cross-encoders, transformers and layers, MS MARCO, unbounded scores and the two dials are explained
  where they first appear; tasks list their steps and the usual slips.
- The two-stage animation is now a still picture of the real jeep question: FM-6.2 8th of hybrid's 20 candidates, then
  first after reranking (-6.6), with the real times.
- Checked by re-running the demo in the lab image on 2 CPUs (the lab's size m). Corrected: "raise first to 55, every
  chunk" was impossible (`hybrid()` fuses two top-20 lists, at most 40 candidates, 35 for the test questions; the quiz
  now raises it to 30); a pair costs about 70 ms here, not "tens of milliseconds"; hybrid search takes under 0.1 s, not
  "about 20 ms"; the first question's time includes loading the model (0.8 s); score guidance now measured (right chunks
  about 4, wrong about -11, the jeep's right chunk -6.6); Nogueira and Cho's gain stated as the paper does (27%
  relative); the GPU claim is now the model documentation's figure (about 1,800 passages a second on a V100); R-0403
  described from its text. A new notes page.

## 25 November: RAG chapter 9 rewritten (easy, a little detailed, checked)

- Dense search, BM25 (term, df, tf, idf, k1, b), tokens, reciprocal rank fusion and sparse vectors are explained where
  they first appear; the BM25 gain is read part by part; tasks list their steps and the usual slips.
- A new still picture, `rag-rrf`: the real CT-112 rankings (dense 11th, BM25 1st) and the fused scores, worked out.
- Checked by recomputing in the lab image (idf table, ranks, fused scores, score ranges, the P-7 question). Corrected:
  R-0301 is not "below ten other camera trap reports" (only the first five mention camera traps); FM-6.2 shares only
  "the" and "to" with the jeep question (it never says "photograph"), BM25 rank 41; R-0305 has no title "Vehicle off the
  road"; stemming would not rescue FM-6.2 (it joins forms of one word, not "tourists" and "visitors"); BM25 was "among
  the best" at TREC-3, not simply "best"; the claim about the 26 questions is now measured: first place dense 20,
  hybrid 15, BM25 12; top 5 dense 24, hybrid 24; hybrid lifts CT-112 (14th to 2nd) and CT-104 (7th to 2nd) but reaches
  first on neither. A new notes page ("embeddings often miss exact codes", not "miss").

## 25 November: RAG chapter 8 rewritten (easy, a little detailed, checked)

- Clients, local mode, collections, points, ids, UUIDs, payloads and JSON, distance, upsert and filters are explained
  where they first appear; the store code is read line by line; tasks list their steps and the usual slips (each slip
  tested in the lab image: a text id is refused as "not a valid UUID", `MatchValue(value=None)` raises a ValidationError).
- A new still picture, `rag-filter`: the chapter's real question filtered after a top-3 search (1 result, R-0410) and
  inside the search (3 results, the third a weaker gaur report).
- Checked by re-running `store.py`, counting the payloads (31 manual sections with zone "all"; 24 reports: 15 core, 6
  buffer, 3 tourism) and searching the history. Corrected: "vectors go in as lists because the client sends JSON" (client
  1.20 accepts NumPy arrays; local mode sends no JSON); manual chunks have no beat or date; Weaviate is open source since
  2016 (1.0 in 2021), not "2019"; hnswlib's year (not confirmed) dropped; Lucene 9 added. Also chapter 4's last line:
  IVF is not "inside every vector database" (Qdrant uses HNSW only). A new notes page.

## 25 November: RAG chapter 7 rewritten (easy, a little detailed, checked)

- float32, bits and bytes, RAM, int8, columns and scales, codes, XOR, the Hamming distance, shortlists and rescoring are
  explained where they first appear; `quantize_int8` and `hamming` are read line by line; tasks list their steps and slips.
- The binary animation is now a still picture with real rows from the benchmark's first question: the 16 rows closest by
  bits (7 of the true 10 in the first 10; the third best by exact score is 16th by bits) joined to the exact top 10, and
  the real recall for shortlists of 10, 50 and 200.
- Checked by re-running the benchmark in the lab image. Corrected: rescoring 200 gives 99.8%, not 100% (`quant_bench.py`
  now prints one decimal); the vectors are synthetic (now said); the NumPy bit search is slower than the float search
  here (19 against 5 ms), since it unpacks bits instead of using popcount (now said); Qdrant's documentation recommends
  binary quantization for vectors of many numbers (1,536 and up in its list), so measure with a 384-number model;
  "every vector database offers both" became Qdrant, Weaviate, Elasticsearch and others; int8 at 100 million vectors
  fills about 30% of a 128 GiB server, not a third; history dates checked (Qdrant 1.1 and 1.5 in 2023, Elasticsearch in
  2024, Cohere's int8 and binary embeddings in 2024); Charikar's signs are of random projections, ours of the numbers
  themselves; the price ($0.8568 an hour) checked on 25 November. A new notes page; the CD photo's caption fixed (CDs
  and DVDs). The task examples in `lab.yaml` show 99.2% and 99.8%.

## 25 November: RAG chapter 6 rewritten (easy, a little detailed, checked)

- Graphs, nodes and links, greedy walks, layers, M, efConstruction and efSearch are explained where they first appear;
  the search loop is read line by line; tasks list their steps and the usual slips.
- The HNSW animation is now a still picture: three layers, the walk from the entry point down to the question, and the
  real result (recall 98.9%, 0.19 ms a question at efSearch 64, brute force 6.57 ms).
- Checked by re-running the benchmark in the lab image: recall 87.7 / 94.9 / 98.9 / 99.8 / 100.0% and 181 MB.
  Corrected: HNSW is not "the default in pgvector" (it is one of pgvector's two index types; the main index of
  Qdrant, Weaviate and Elasticsearch; one of Milvus's options); the data is 100,000 synthetic vectors; the IVF and
  HNSW timings are not comparable (Python versus C++), now said so; upper layers keep M links, the bottom 2M. A claim
  about the check that could not be verified was removed. A new notes page.

## 25 November: RAG chapter 5 rewritten (easy, a little detailed, checked)

- ANN, centroids and clusters, k-means step by step, Voronoi cells, inverted lists, the transpose and `argmax(axis=1)`
  (read line by line), nprobe and candidates are explained where they first appear; tasks list their steps and slips.
- The IVF animation is now a still sketch (in two dimensions, said so): cells around centroids, the question's probed
  cell, a true neighbour missed just across a border, and the real recall at nprobe 1, 4, 16, 64.
- A new history photo: Georgy Voronoy (public domain), whose 1908 cells are exactly what the IVF lists hold.
- Checked by re-running the benchmark in the lab image: recall 52 / 73.6 / 91.8 / 99.6%, lists of 155 to 483, and the
  quiz's 632 lists at nprobe 16 (0.5 ms, 90.2%). Corrected: the benchmark runs on 100,000 synthetic vectors (the
  lesson never said so); nprobe 64 is 99.6%, not exactly the brute-force answer; "about the square root" is one rule of
  thumb among several (pgvector: rows / 1000 up to a million; FAISS: several times the square root). A new notes page.

## 25 November: RAG chapter 4 rewritten (easy, a little detailed, checked)

- Why documents are cut (the model reads at most 512 tokens, about 380 words, for bge-small; one vector cannot stand
  for many topics), tokens, overlap, Markdown headings, `partition`, `split()` and metadata are explained where they
  first appear; the section cutter is read line by line; tasks list their steps and the usual slips.
- A new still picture, `rag-chunks`: three real sections (FM-4.1 59 words, FM-4.2 66, FM-4.3 66) drawn to scale and cut
  four ways, with each method's real hit@1 from the comparison (73%, 77%, 77%, 91%).
- Checked against the code and data: section sizes 52 to 95 words, 2,008 words in all; a window gets credit for every
  section it touches; 864 / 45 = 19 times. Results are labelled as this manual's and these 22 questions', and the lesson
  now says that with 22 questions one question is about 4.5 points, so 86% against 91% is a hint, not a proof. A new
  notes page, checked letter by letter.

## 25 November: RAG chapter 3 rewritten (easy, a little detailed, checked)

- Nearest-neighbour search, brute force, normalizing, `axis=-1` and `keepdims` (read line by line), the matrix product
  `@`, BLAS, `argpartition` and the processor's cache are each explained where they first appear.
- A new still picture, `rag-matrix`: five section rows times the "big cat" question give five real cosines, and the top
  3 (FM-4.2 0.595, FM-7.3 0.565, FM-4.1 0.551). The `top_k` trace now uses those real scores (it used made-up ones).
- Checked and corrected: `bench.py` averages 20 questions with k = 10 (the lesson said one question); all timings are
  labelled as measured on this lesson's lab machine; "15 MB fit in the cache" is given as the likely reason, not a
  fact; "points become almost equally far apart" is said to hold for random data, not for real embeddings; verified in
  the lab image that bge-small already returns vectors of length 1 (the quick check now says so plainly). The tiger
  photo's lead says why it is there. A new notes page, with "rows x dimension x 4 bytes" (not "x 384").

## 25 November: RAG chapter 1 rewritten (easy, a little detailed, checked)

- Part of rewriting the whole RAG course to the owner's rules (memory: lesson-rewrite-rules). Titles, story, tasks and
  ids unchanged; 2,823 words became about 4,100.
- Every term is explained where it first appears: language model, cut-off date, prompt, hallucination, fine-tuning,
  the AI gateway and the `lab-chat` name (gpt-4o-mini in this course), `temperature=0`, messages and roles, `words()`
  read step by step (lower case, the hyphen-keeping pattern, short and common words, a set), set intersection.
- The RAG flow is a still picture now (it was a step animation): the real question, the three sections keyword search
  really found (FM-3.2, FM-3.1, FM-7.1), the prompt, and the real answer naming FM-3.2.
- Checked against the real code and manual, and corrected: the reworded big-cat question finds FM-4.7 and FM-5.3 through
  "ahead" and FM-8.2 through "about" (the chapter said "ahead, right and about"; "right" matches nothing). The trace now
  shows FM-7.1 "Snares and traps" scoring 2 on "often" and "traps", the noise of word matching. Salton built SMART at
  Harvard and then Cornell. "Rarely says I don't know" became "often does not say". The tiger photo's lead says why it
  belongs (FM-4.2, a dangerous procedure), the catalogue photo's lead ties it to the big-cat failure; the made-up
  sanctuary is said to be made up. A new notes page in six plain sentences, checked letter by letter.

## 25 November: RAG chapter 2, 384 is the model's size, not every embedding's

- Owner: "is 384 model specific or model agnostic?" Model specific, but the recap ("a fixed list of 384 numbers") and the
  notes page read like a general rule. The lesson now says 384 belongs to bge-small and every model has its own fixed
  size; the recap says "a fixed-length list of numbers (384 with this course's model)"; the picture's caption names the
  model; the notes page is redrawn ("Our model turns any text into 384 numbers. Each model has its own fixed size."
  and "Unrelated texts do not score 0." instead of the model-specific 0.4), checked letter by letter.

## 25 November: RAG chapter 2 explains 384 where it first appears

- Owner: "have you explained in the lesson with clarity what 384 is?" Not well enough: the explanation came four
  paragraphs after 384 first appeared and used "layers" without explaining it. Step 2 now explains it right under the
  picture: "What are the 384 numbers?" (each a measurement the model learned; none means anything alone) and "Why exactly
  384?" (the size the builders chose; it is called the dimension; other models' sizes; the two rules that follow), then
  why this helps Fieldbook. The check-yourself line asks what "384-dimensional" means.

## 25 November: RAG chapter 2 explains 384

- Owner: "what is 384 in that lesson?" The lesson said "384 numbers" everywhere but never why. Step 2 now explains it:
  the size the model's makers chose (its layers are 384 numbers wide), called the vector's dimension, with a table of
  other models (bge-base 768, bge-large 1,024, OpenAI text-embedding-3-small 1,536), the trade-off (more room for
  meaning against memory and speed), and the two rules that follow (same model, same length; different models never
  compare).

## 25 November: RAG chapter 2, plainer, with a clear text-to-vector picture

- Owner on the sample: "a little more easy to understand; not too analogy oriented, but written so the concept is easy
  to grasp; text to vector embedding could be shown more clearly via an image; the animation is hard to understand".
  The first concept now says plainly what an embedding model does (text in, 384 numbers out), why that helps (similar
  meanings get similar vectors), the three steps of searching by meaning, how the model learned it and that no single
  number means anything; the map-and-towns comparison is gone from the whole chapter.
- The playing `rag-embed` animation is now one still picture: three real sentences, an arrow through the bge-small model,
  and each one's first 4 numbers (the model's real output, computed in the lab's image), then the real cosine scores
  (tiger vs big cat 0.69, tiger vs batteries 0.42). Drawn tall, so it shows at full size in the lab's lesson panel.

## 25 November: RAG chapter 2 rewritten to the 24 November review (the sample)

- Owner: "write each lesson more practical, eloquent, easy to understand, yet maintaining the standard; images connected
  to the content; the handwritten notes more elaborate". As a sample before the rest of the course, chapter 2 of RAG and
  vector databases ("Text as numbers") follows CONTENT_STANDARD section 7 in full; titles, story, tasks and ids are
  unchanged. 1,906 words became 3,908:
  - the first concept starts from a paper map (a town is two numbers; a text is 384), explains how the model learned its
    map (training pairs, weights) and why no single number means anything, with a new playable diagram, `rag-embed`;
  - a new step reads `model()` and `embed()` line by line (the model's name, fastembed, `@lru_cache`, the matrix shape,
    the generator, `float32` and its 1,536 bytes);
  - a new history step, "Before embeddings: synonyms written by hand", with a public-domain portrait of Peter Mark Roget
    and a caption that says why he belongs here; the Mikolov photo's lead now says what word2vec did and how it leads
    to the learner's own model; the timeline starts at 1852;
  - cosine is worked by hand ([3, 4] and [4, 3] give 24 / 25 = 0.96; [-4, 3] gives 0; [6, 8] gives 1.0, which is why
    it divides by the lengths), with check-yourself lines; tasks list their steps and the usual slips;
  - a new notes page in six plain sentences ("An embedding turns any text into 384 numbers." ... "Embeddings barely
    notice the word not."), checked letter by letter.
## 25 November (Ukiyo): a new picture for AI

- Owner: "I don't like this image, change it" (the eagle). AI now shows Hiroshige's Asakusa Ricefields and Torinomachi
  Festival (One Hundred Famous Views of Edo, 1857; public domain): a white cat on a windowsill gazing out at Fuji and
  the rice fields under a sunset sky. Fireworks at Ryogoku was tried too but looked dull when the panel opens.

## 25 November (Ukiyo): a public-domain print for AI

- Owner: since the 1951 pagoda print may still be in copyright, "use an entirely cool, soothing image for AI". AI now
  shows Hiroshige's Fukagawa Susaki and Jumantsubo (One Hundred Famous Views of Edo, 1857; public domain, Rijksmuseum):
  an eagle gliding over a calm snowy bay under a deep blue sky. Every category picture is now public domain.

## 25 November (Ukiyo): "No tutorial hell."

- Owner chose "tutorial hell" over "video hell". The hero line is "No fluff. No tutorial hell. Only action."

## 25 November (Ukiyo): "No fluff. No video hell. Only action." in the hero

- Owner: "add No fluff No video hell only call to action". A serif line between the hero's lead and Start free:
  "No fluff. No video hell. Only action." (the last in vermilion italic). The lead now says "a code editor" instead
  of "VS Code" (owner: the editor may change).

## 25 November (Ukiyo): the container run slower still

- Owner: "still fast". 1.6 s per piece (was 1.15), and the flight, slide, doors, locks, sealing and starting stretched
  to match. A LangChain run now takes about 14 s from first view to running.

## 25 November (Ukiyo): the container run a little slower

- Owner: "the animation is happening too fast, slow it just a little". Everything is about a quarter slower and moves
  together: 1.15 s per piece instead of 0.9 s (one `PIECE_MS`), the flight, the crate's slide, the doors, the locks,
  sealing and starting. A LangChain run takes about 10 s from first view to running, instead of about 8.

## 25 November (Ukiyo): the first run plays by itself

- Owner: "whenever someone visits the page, new or old user, the first animation should auto start". On every visit
  the LangChain run starts by itself once the section is mostly in view (on desktop when you scroll to it, on phones
  the same). After that, picking another lab waits for Run or a tap, and "Spin it up again" replays.

## 25 November (Ukiyo): the run command's border in the theme's grey

- Owner: "this green border is looking off the vibe with the whole page theme". The command's outline is the warm grey
  of the page's rules, and the pulsing ring is a faint line in the page's ink (cream on dark, ink on light); green is
  left only on the Run key and the $ prompt.

## 25 November (Ukiyo): no tap badge; the plate says TAP TO START

- Owner: "very bad placing" (the badge above the container), then left the choice to me. The badge is gone; the
  "Try it: tap Run" command is the call to action, the container stays tappable anywhere, and its status plate
  reads "▶ TAP TO START" in softly pulsing green until it runs.

## 25 November (Ukiyo): "Tap to spin it up" above the container

- Owner: "place this tap to spin it up somewhere else". It sits centred in the space above the container (where the
  pieces appear once it starts), clear of the whale and the status plate; ink on light pages, cream on dark ones.

## 25 November (Ukiyo): nine labs in the container section, AI first

- Owner: "keep three AI labs, one Spring Boot, one Python, one DB, one Linux, FastAPI, Redis". The tabs are now
  LangChain, Spring AI, RAG, Spring Boot, Python, Postgres, Linux, FastAPI and Redis (System design is out), and the
  section opens on LangChain. The new stacks come from each lab's setup: Spring AI (Java 21, Spring Boot 4.2,
  Spring AI 2.1, the model gateway), RAG (Python, two local embedding models, FAISS and Qdrant, the gateway), Python,
  and Linux (a whole server with Bash and the classic tools), each with its real first challenge.

## 25 November (Ukiyo): "One click, and a container spins up for you"

- Owner: "remove we". The heading is now "One click, and a container spins up for you with everything the lab needs."

## 25 November (Ukiyo): the whale leads, the crates step back

- Owner: "the whale logo should be a little bit more dominant and the item boxes a little less". The whale stays on the
  glass wall at half strength (it faded to almost nothing before) and is drawn in front of the crates; the crates are
  about a fifth smaller and slightly softer in colour.

## 25 November (Ukiyo): the pieces ride in as crates you can see

- Owner: "these small item logos going inside the container don't do justice; show a more expressive, cool way of
  items going inside the container and staying there". When loading starts the front wall turns to glass (the
  corrugation, stencils and whale fade; the frame stays solid) and the inside shows: far wall, end wall, a plank
  floor and a warm ceiling light. Each piece flies to the doors, then rides in as a cardboard crate (top, side, tape,
  a label with its logo) and slides along the floor to its place, in stacks two high from the far end. The crates
  stay there; when the container runs, the ceiling light turns green and a small LED lights on every crate. The
  status plate moved to the bottom rail.

## 25 November (Ukiyo): the run command, and how people know to press it

- Owner picked the terminal design, then: "how will users know they have to click here? They mostly open it on a phone
  first". The command (`$ docker run spring-boot`, short enough for a phone) types itself with a cursor when the page
  opens; it ends in a solid green "Run ▶" key; a label above says "Try it: tap Run"; a green ring pulses around it.
  The container itself is tappable too, with a "▶ Tap to spin it up" badge on it. The other five designs and the
  `?buttons` switcher are removed.

## 25 November (Ukiyo): six designs to try for Spin up (?buttons)

- Owner: "I still don't like any colour and design for this". Instead of colours, six designs to try live at
  `/?buttons`: 1 a terminal command (`$ docker run labbox/<lab> ↵`, the default), 2 Docker blue with the whale,
  3 the site's red like Start free, 4 an ink outline, 5 a round power switch, 6 an underlined link. The colour
  swatches are gone; the switcher goes once a design is picked.

## 25 November (Ukiyo): the clock is back

- Owner: "where has the timer gone when adding the labs to the container? add it". The lid counts up smoothly from
  the click, "20 s · 4/7 loaded", "44 s · sealing", "50 s · starting", and turns green at "58 s · running".

## 25 November (Ukiyo): pieces appear one by one, only after Spin up

- Owner: the dock of chips "should not be present from the start; when I spin the container it should be present one
  by one". Before the click only the empty container shows. After it, each piece appears on its own just above the
  container, rises a little and flies into the open doors, where it stays stacked; then the next one comes.

## 25 November (Ukiyo): no empty space under the prompt

- Owner: "why is this space left below learner". The log no longer reserves room for every line and the Start row is
  not laid out until the machine runs, so before the click the box ends under the `learner:~$` prompt; it grows as
  the lines arrive.

## 25 November (Ukiyo): Spin up moves out of the box

- Owner: the Spin up button "could be placed somewhere else, it is ruining the entire show". It now sits in the left
  column under the words, as the section's call to action (after a run, "Spin it up again" takes its place), so the
  box shows only the dock, the container and the log. On phones it wraps to fit.

## 25 November (Ukiyo): a proper container; the items go in, then it starts

- Owner: "this Docker container could be way more cool looking ... show the items which are going in the container,
  and after all the items go inside, start the container"; then "make the container a little big".
- The container is redrawn: corrugated walls in two blues with ridge highlights, a corrugated roof, top and bottom
  frame rails, corner posts and seven corner castings, stencilled "LABBOX / LBXU 240 017 3 · 22G1", a spec plate, the
  Docker whale, a status plate on the wall, and end doors that stand open (one leaf folded back on the wall, one swung
  out) showing the dark inside. It is drawn tight to its frame, so it fills the box's width.
- The sequence: every piece waits on a loading dock above the container; after Spin up each one lifts off, travels
  into the open doors and stays stacked inside (its dock place turns dashed, its log line appears, the container
  bumps); then the doors swing shut and the bars' handles lock; `docker start labbox-<lab>` runs while the roof lamp
  blinks amber ("STARTING"); then the lamp, a light strip along the bottom rail and the shadow glow green, the plate
  reads "RUNNING", the container hums, the log says "running", and the tick and Start appear. Reduced motion skips
  straight to running.

## 25 November (Ukiyo): a real Docker-style shipping container

- Owner: the rust box was "the most rubbish image"; "I need an original Docker container". The CSS box is gone. In
  its place an SVG illustration in the Docker docs' hand-drawn style (`Container` in `components/UkiyoMachine.tsx`):
  a light-blue corrugated container with the Docker whale logo on its side, a lighter roof, thick ink outlines and a
  soft shadow. Its end doors stand open (dark) while it loads; each piece appears above the doors and drops in, the
  container bumps as it lands and the log line appears; when full the ribbed doors close and the green tick lands.
  The Spin up button sits below the container so the whale stays visible.

## 25 November (Ukiyo): the machine box as a shipping container

- Owner: "isn't it cool if the container looks like this instead of the plain one" (a Docker-style shipping container).
  Drawn in the theme, not copied: a rust-red container shell (#9b4a34) framing the open front where the pieces load,
  a roof edge in perspective, a ribbed side with two doors, four door bars and handles, dark corner castings, an ink
  outline and a soft shadow underneath. CSS only (`ukiyo.css` section 15); the animation inside is unchanged.

## 25 November (Ukiyo): try colours for the Spin up button (?colors)

- Owner: "try another colour, see how many vibrant colours are in this image ... keep on trying one by one". Eight
  colours from the home page prints, to try live: open `/?colors` and click a swatch under the box (1 Hiroshige
  blue, now the default, 2 sea teal, 3 wisteria violet, 4 pine green, 5 ochre gold, 6 blossom pink, 7 dawn coral,
  8 brick). The swatches are temporary and go once a colour is picked.

## 25 November (Ukiyo): the earlier Spin up button, in a softer red

- Owner: "that design was good, you just have to change the colour, shade, aesthetic". Back to the hanko-style
  rectangle (inner cream line, cream play circle), now in a muted brick red (#a9533e on washi, #94493a on sumi)
  with cream text and a gentler ring; no "pieces" line.

## 25 November (Ukiyo): a calmer Spin up button

- Owner: remove "5 pieces, 6 pieces" and "this red colour is too hard on the eyes". The button is now a cream pill
  with ink text and a small vermilion play circle, a faint ink ring pulsing around it; the pieces line is gone.

## 25 November (Ukiyo): the container spins up when you click

- Owner: "better if the user clicks and sees the animation". The box now waits with its slots empty, a dim
  `learner:~$` prompt and one red button, "▶ Spin up the Spring Boot machine" (with a soft pulsing ring). Clicking
  it plays the packing; switching labs resets the box and waits for a new click; "↺ Spin it up again" replays.

## 25 November (Ukiyo): "start a lab" on the home page

- Owner: "it is ready, now you can integrate this on the main home page". The packing box is a component
  (`components/UkiyoMachine.tsx`) and a home page section between the hero and "Pick a lab". Start opens the chosen
  lab's course page (logged out: through login, `next=`). The review page `/ukiyo/machine`, the three directions not
  picked and the screen recording are removed. `home.spec.ts` watches it pack Spring Boot and Redis.

## 25 November (Ukiyo): Start with the hanko's white line; a vibrant green tick

- Owner: the Start button should keep the inner white line the READY seal had; "this green colour of the tick
  should be vibrant". Start has an inset cream line like a hanko; the tick's circle is a bright green (#16a34a).

## 25 November (Ukiyo): a green tick instead of the READY seal

- Owner: "instead of READY, a green tick mark will be much better". When the machine is ready, a jade green circle
  with a white rim stamps onto the lid's corner and its tick draws itself in.

## 25 November (Ukiyo): direction A's words

- Owner: "write like: one click and we will spin a container for you with all the required ...". The heading is now
  "One click, and we spin up a container for you with everything the lab needs." and the line under it: "Linux, the
  language, the framework, the databases, an editor and terminal, and an AI code assistant: set up and running in
  about a minute. Nothing to install. You go straight to the first challenge."

## 25 November (Ukiyo): direction A in the theme's colours

- Owner: "the design and colour of the animated box feel off the theme". Same animation, new dress: a paper card
  ruled in ink instead of Docker blue; a sumi ink lid with a vermilion progress line; dashed ink slots that pulse
  vermilion; tiles on washi with a fine rule; the log under a heavy ink rule with vermilion ticks; and when the
  machine is ready, a red hanko seal "READY" stamps onto the lid's corner instead of the box turning green. The
  terminal and AI icons use vermilion and indigo. Works in washi and sumi.

## 25 November (Ukiyo): direction A refined, packed step by step

- Owner liked "real logos in a box" but wanted a more refined animation, "Editor and terminal" instead of VS Code
  (the editor may change if VS Code is too heavy), an "AI code assistant", and each step shown line by line. Now the
  box shows empty slots; the next one pulses; each piece flies in, settles with a small bounce and a ring, and its
  line appears in a log under the tiles ("✓ Java 21 the JDK the course uses"); a progress bar and a clock run in
  the lid; when the last piece is in, the box turns green ("ready") and the first challenge with Start slides up.
  It starts when scrolled into view, replays on a lab change, keeps its height, and stays still with reduced motion.

## 25 November (Ukiyo): four new directions for "start a lab" at /ukiyo/machine

- Owner did not like the first five ("tbh I didn't like any of it", then "show me all"). The review page now has
  four different directions: A real logos flying into one Docker container that seals and lights up Start (six
  labs' real stacks); B a real screen recording, made on this laptop, of pressing Start on the FastAPI course until
  VS Code opens with the task (12 s, 185 KB, `public/ukiyo/demo/`); C one big sentence with the real logos; D a
  before and after slider between a laptop full of install errors and the real lab.

## 25 November (Ukiyo): five ways to show "start a lab" at /ukiyo/machine

- Owner: show on the home page that starting a lab spins up a container with Linux, the language, the framework and
  the databases, so there is no manual setup and you go straight to the challenges; "show me all, then I decide".
  A review page (not linked from the app): 1 the machine builds itself (layers stack, a timer, the first
  challenge), 2 the setup you skip (manual steps crossed out beside one Start), 3 the chest of drawers (a tansu,
  one drawer per layer), 4 the boot log (a terminal, then the challenge card), 5 three moves. Options 1 to 4 switch
  between FastAPI, Spring Boot, Redis, Postgres and LangChain, with each lab's real layers and first task.

## 25 November (Ukiyo): "AI labs" opens the AI labs (after logging in); Mount Hira; FAQs without numbers

- Owner: "when I click on AI labs in the navbar, it should open the AI labs if logged in; if not, log in and redirect
  to the AI labs". The menu link goes to `/labs?category=ai`: the dashboard opens with only the AI category shown
  and scrolls to it. Logged out, every page behind login now sends you to `/login?next=<that page>` and back there
  after logging in or signing up (`next` must be a path on this site; anything else goes to the dashboard).
  New browser test `e2e/ai-labs-link.spec.ts`.
- Owner: another image for the closing panel. Hiroshige's Evening Snow on Mount Hira (Eight Views of Omi, about 1834,
  public domain): soft snow on the mountains, a quiet village, a little blue water.
- Owner: "remove numbers from FAQ". The 01 to 08 before each question are gone.

## 25 November (Ukiyo): Autumn Moon at Ishiyama, and a shorter closing panel

- Owner: "na, some other image, and keep the height a little less". The closing panel shows Hiroshige's Autumn
  Moon at Ishiyama (a full moon over Lake Biwa in blues and greys, public domain), cropped to a wide strip; the
  panel's padding and heading are smaller, so it is about 370 px tall instead of about 520 on a laptop screen.

## 25 November (Ukiyo): a calmer print in the closing panel

- Owner: "change this image to something eye soothing". The "Your machine is ready when you are." panel now shows
  Hiroshige's Returning Sails at Yabase (Eight Views of Omi, about 1834, public domain): a golden sky over a still
  blue lake with sailboats, instead of the busy Nihonbashi street scene.

## 25 November (Ukiyo): calm Hiroshige prints for five categories

- Owner: "now I need cool images that soothe the eyes for the rest 5". Languages, Frameworks, System design,
  Databases and DevOps now show real public-domain Hiroshige prints instead of drawn ones, each keeping its motif:
  cherry blossoms on the Tama River, the bamboo yards at Kyobashi by moonlight, the drum bridge under wisteria at
  Kameido, a boat on the Sumida with Azuma Bridge and Fuji, the Monkey Bridge by moonlight. They fill the home
  page's folding screen and the dashboard's category tiles. The brush-sun picture is no longer used.

## 25 November (Ukiyo): "Learn to build AI apps, or get left behind."

- Owner: change "Learn to build on it." to something like "Learn to build AI applications or get left behind", keeping
  the fear of being left behind. The headline is now three lines: "The AI wave is here." / "Learn to build AI apps,"
  (vermilion italic) / "or get left behind." (muted, the sting on its own line).

## 25 November (Ukiyo): the new home hero

- Owner picked from eight options: option 6's layout with option 7's picture, and new words. Two lines, each on
  its own: "The AI wave is here." and, in vermilion italic, "Learn to build on it." Under them: "Open a lab and a
  Linux machine starts for you in about a minute, with VS Code, a terminal and a model gateway." and Start free. On
  the right, a real lab session (labbox start, an agent's answer, task passed) over Hiroshige's Kinryuzan Temple at
  Asakusa in snow (1856, CC0). Red Fuji, the brush underline and the old headline are gone; `/ukiyo/heroes` and its
  two unused prints are removed.

## 25 November (Ukiyo): eight hero options to compare at /ukiyo/heroes

- Owner: "this image and this text look off ... how many ways, new design, new images, new text, I want to see it".
  A review page (not linked from the app) shows eight complete heroes, each with its own layout, picture and words:
  1 type only, 2 tall print (Moon Pine), 3 full-bleed Great Wave, 4 triptych (three Hiroshige prints), 5 the seal,
  6 terminal over rain (Sudden Shower), 7 magazine cover (Kinryuzan), 8 mosaic of the category prints. Three new
  public-domain prints in `public/ukiyo/heroes/`. The owner picks one; the rest and the page then go.

## 25 November (Ukiyo): folding screen panels without numbers

- Owner: "remove 01 02 03 and so on". The red number tags are gone from the panels.

## 25 November (Ukiyo): home page without the AI section, for now

- Owner: "remove this for now, but keep in memory, might use later". The AI section (the pagoda picture, "AI labs ·
  Launching", "24 labs, from your first model call to your own GPT.") is off the home page; to bring it back,
  restore it from commit 3b89404 (`HomePage.tsx`, the `uh-ai` styles stay in `ukiyo.css`). The menu's "AI labs"
  link now jumps to the labs, whose folding screen starts with AI.

## 25 November (Ukiyo): the folding screen on the home page

- Owner picked layout 2 of the eight ("done this"). The home page's categories are now a folding screen: six tall
  panels, one per category, each with its print, a red number and its name written vertically; the panel under the
  pointer opens wider and lists up to five of its labs. On phones the panels stack as rows. The review page
  `/ukiyo/layouts` is removed.

## 25 November (Ukiyo): eight category layouts to compare at /ukiyo/layouts

- Owner: "in how many ways can you put this content? ... I want to see all one by one". A review page (not linked
  from the app) shows the same live categories eight ways, numbered, with a jump menu and the theme switch: 1 card
  grid (the home page now), 2 folding screen, 3 editorial index, 4 feature and list, 5 gallery wall, 6 hand scroll,
  7 tabs, 8 uneven grid. The owner picks one for the home page; the page then goes.

## 25 November: a light and dark switch on the login page

- Owner: "give the option of light and dark theme on this page". The login and sign-up card has the same switch as
  every top bar, next to "Home". The switch is now a plain button (`type="button"`), so inside the form it never
  submits it. Done on master and `design/ukiyo`.

## 25 November: sharp book covers in Premium Reads

- Owner: the book covers "feel very low quality". They were 240 to 500 pixels tall thumbnails shown about 370 px
  wide. All 21 are now 800 px wide (full-size publisher covers; Fluent Python's English 2nd edition from its own
  site; A Philosophy of Software Design's 2nd edition cover, the only clean one; Speech and Language Processing
  redrawn from the official draft PDF with its whole title block). The cover frame is 3:4 instead of 2:3, the shape
  of most real covers, so their edges are no longer cut. Same file names, so no migration.

## 25 November (Ukiyo): Plum Garden on login; no numbers strip on the home page

- Owner: the Great Wave "does not suit" the login page. It now shows Hiroshige's Plum Garden at Kameido (1857,
  public domain): a calm vermilion sky, and a dark lower half where the words and the terminal sit.
- Owner: "remove this data also". The four numbers under the home page hero are gone.

## 25 November (Ukiyo): home page with one card per category; Red Fuji behind the hero; the Great Wave on login

- Owner: "you have put all the labs on the home page ... remove most of them, find a different way". The home page
  shows one card per category (its print, how many labs, three titles) and "See all 23 labs"; the full list stays
  on the dashboard.
- Owner: "maybe this image in hero section background". Red Fuji now fills the hero's width behind the headline and
  fades into the paper on the left (and under the text on phones), with its credit in the corner.
- Owner: "change this image on login page". The login and sign-up page shows the Great Wave instead of Red Fuji.

## 25 November (Ukiyo): home page without "Inside a lab" and the AI stage ladder

- Owner: "remove this portion" (the whole Inside a lab section: heading, screenshot, tour and features, so the hero's
  "See inside a lab" link went too) and "this one also" (the four AI stages). The AI section keeps the pagoda
  picture, the heading and one line.

## 25 November (Ukiyo): home page without the logo strip

- Owner: "remove this from home page" (the moving row of technology logos). The numbers now sit right under the hero,
  between two fine rules.

## 25 November (Ukiyo): the home page redesigned to match the inside

- Owner: "redesign the home page. The inside part looks cool; the home page looks off". It mixed the old design's
  pieces (yellow highlights, rounded cards, a pink gradient banner, cover-art lab cards) with the new colours.
  Now: a framed Red Fuji (Hokusai, public domain) beside the headline with a vermilion brush underline; logos on
  paper chips; the numbers between fine rules; the lab screenshot, then the tour beside six ruled features (no
  icon bubbles); the AI track as a ladder of four stages under the pagoda picture, every planned lab listed; the
  dashboard's own category tiles and lab rows (one shared component, `UkiyoDirectory.tsx`), replacing both "Pick
  a lab" and "Also on LabBox"; a closing paper panel with Hiroshige's Nihonbashi ("Your machine is ready when you
  are", no "first win" line); FAQs with a thin plus and minus. Fixed on the way: the home page's colour variables
  referred to themselves, which hid the selected "All labs" label in dark mode.

## 25 November (Ukiyo): AI shows the pagoda, Languages the brushed sun

- Owner: "for ai use kathmandu image". The two category pictures swap: AI is the vermilion pagoda, Languages the
  brushed red sun over an ink wave.
## 25 November: Premium Reads papers tell the history of language models

- Owner: "add word2vec, GPT-1 + BERT, scaling laws + GPT-3, InstructGPT, chain of thought ... check if these exist,
  and if not add them on top after Attention Is All You Need". word2vec, BERT, GPT-3 and Chain-of-Thought were
  already there; GPT-1 ("Improving Language Understanding by Generative Pre-Training", OpenAI 2018), Scaling Laws
  for Neural Language Models (2020) and InstructGPT ("Training language models to follow instructions with human
  feedback", 2022) are new, each with its first page as the picture and a link to the LangChain chapter that
  practises it. The papers now start: Attention, word2vec, GPT-1, BERT, Scaling Laws, GPT-3, InstructGPT,
  Chain-of-Thought, then the rest (20 papers).
- `library/seed.yaml` for fresh databases; migration 0012 (additive) adds the three to existing databases and sets
  that order, keeping any admin-added papers after the seeded ones. New test in `test_migrations.py`.

## 25 November: Premium Reads featured card without "Start here"

- Owner: "remove start here from this card". The first pick of each section (AI Engineering, Attention Is All You
  Need, Lil'Log) keeps its big card, without the "Start here" label. Done on master and `design/ukiyo`.

## 25 November (Ukiyo): the owner's pictures for AI and Languages

- Owner: "use this image for ai" and the pagoda saved as `~/Pictures/kathmandu.jpeg`. The AI tile shows the brushed
  red sun over an ink wave; Languages shows the vermilion pagoda among snowy cedars. Cropped to the print shape and
  stored in `public/ukiyo/tracks/`. Licences to confirm before launch (see DESIGN_UKIYO.md).

## 25 November (Ukiyo): new AI and Languages prints

- Owner: "this ai and language should get a more cool classy logo ... the red one ... is pretty awesome", with
  reference images. Redrawn as original SVG in their style: AI is a brushed red sun over one sweep of sumi ink;
  Languages is a vermilion pagoda among snow-laden cedars behind a stone wall. System design, which had the pagoda,
  is now a red arched bridge over still water. The reference images are not used (stock, AI-made or in copyright).

## 25 November (Ukiyo): real lab logos, straight icons, a classy profile panel

- Owner: "use real logo of the respective labs". LangChain, LangChain4j, LangGraph and Rust showed a letter: their
  credits say "Logo: LangChain4j" and `labBrand` only read "Logos: ...". It reads both now, and their logo files
  (already in `tools/logos/`) are served from `public/logos/`. Logos sit on a paper chip in both themes, so dark
  marks (Rust, LangGraph) read on sumi too.
- Owner: "do not tilt it or any icon. keep it straight and fixed", "for all". The hanko seal and the logo stamp on
  the course print stand straight.
- Owner: "make this classy and same theme" (the profile panel). Paper card with a vermilion top rule, a hanko seal
  for the initial (also the top bar button), "Level 2" as a small vermilion kicker, a fine ink progress line, serif
  numbers for the streak and stars (no emoji), the streak note in italic serif, a quiet Exit row.

## 25 November: pages open at their top; sign-up without the first-win line; footer without Premium Reads

- Same changes as on master: `ScrollToTop` and no jump to "You are here"; the sign-up form's first-win line is gone;
  the footer links are FAQs, Privacy policy and Terms of Service; the lesson's faint logo stands straight.

## 25 November: home page menu: AI labs, Premium Reads, FAQs

- Owner: "remove Inside a lab and Labs from the navbar. AI labs is good enough". The sections stay on the page
  ("See inside a lab" in the hero still jumps to the demo). Done on master and `design/ukiyo`.

## 25 November (Ukiyo): a real woodblock print for every lab

- Owner: "for every language, there is this same image, pick some classy unique images for each one of the lab. and
  one common image for the dashboard". Each of the 23 labs now has its own print by Hokusai or Hiroshige (public
  domain, mostly CC0 from the Metropolitan Museum of Art), chosen to echo its project, on the course page (with a
  credit line) and on the dashboard's Continue feature. The category tiles keep one shared print per category;
  "All labs" shows the Great Wave. Credits in DESIGN_UKIYO.md.

## 25 November: course page heading "Skill map"; no "Start free" next to "Log in"

- Owner: "remove what you will learn and write title as Skill map", and "remove start free button as it also takes
  me to login/signup page". Same change as on master.

## 24 November: the rule book after the owner's review, and Before you start on every lab

- Owner, after reading the RAG and Rust courses: "cutting corners"; lessons "more elaborative, easy to understand,
  expressive" while keeping the titles and voice ("fantastic"); photo leads that make the link easy to understand; more
  photos in long labs; notes pages a beginner can read ("like rocket science" now); detailed prerequisites for every lab.
- `CONTENT_STANDARD.md` section 7 (new) and the full-standard table, `COURSE_PRODUCTION.md` (syllabus item 7, photos,
  notes) now say all of that, with examples.
- **Before you start** on every course page: `before_you_start` in all 23 `lab.yaml` files (a plain summary, then each
  thing to know, why the lab needs it, and the LabBox lab and chapters that teach it, checked against those labs' real
  chapter lists; courses from zero say "Nothing."). The lab API sends it with each needed lab's title; the validator
  warns when a lab has none (an error with `--strict`) and refuses a lab that does not exist.
- Test: `tests/test_before_you_start.py`.

## 24 November: lesson photos that always load

- Owner: images sometimes did not show ("why don't you download images instead of embedding url ... sometimes it fetches
  on my machine sometimes it does not"). Every lesson photo already was a file inside LabBox
  (`frontend/public/lesson-images/`; the Wikimedia link under a photo is only its credit), so the fix is in loading:
  - photos load at once (`loading="eager"`) instead of only when scrolled into view;
  - a chapter fetches all of its photos in the background as soon as it opens (`LabPage.tsx`);
  - a photo whose load fails is tried again by itself twice, then shows "Try again" (`LessonMarkdown.tsx`).
- Test: `e2e/photos.spec.ts` makes the first two requests for a lesson photo fail and checks that it still appears, and
  that the chapter's last photo (the recap's notes page) is requested as soon as the chapter opens.

## 24 November: the Library (books, research papers, tech blogs), a public page

- Owner's later changes: the headline is now "Premium reads."; the row of counts under it is gone; books and blogs show
  no description (papers keep theirs; the text stays saved, and Admin > Library says "shown for research papers only").
- Then: the long "Practise it hands-on" line on each card became one small chip in the lab's colour (the chapter shows
  on hover; the Start here card keeps the full line); book cards show only the cover (it already shows the title and
  authors), and the cover opens the book; whole paper and blog cards open the item, while their lab chip still opens
  the lab; "Free to read" and the topic badge are gone from the cards (the topic filter stays).
- Then: paper and blog cards lost their "Read the paper" and "Visit the blog" buttons (the whole card opens the item;
  the Start here card keeps its button); blogs now open with OpenAI News, Hacker News, Anthropic Engineering, Claude blog
  (owner's order; seed.yaml and the development database).
- Then (owner): the Library is called Premium Reads in the app (dashboard button, home page, footer, Admin tab; the
  address stays /library); the kicker reads "Hand-picked by the LabBox team"; a plain "Last updated 24 Nov 2026" sits
  beside the heading and a "Last updated" pill on each section tile (the newest change in that section); picking a
  section puts the other two tiles out of focus; the Start here card lost its read button and opens the item as a
  whole (its lab chip replaces the long "Practise it hands-on" line); Attention Is All You Need is the papers' Start
  here pick; blogs run Lil'Log, Anthropic Engineering, OpenAI News, Hacker News, Claude blog.
- Then (owner: "more cool design", "try something different"): the three section tiles became dark cards filled
  with a tilted wall of the section's real pictures, the words on a shade at the left; the picked section has a
  ring and glow in its colour, the other two blur and dim until pointed at.

- Owner: "add an entire new section like Books Recommended to Read, and admin can change with time, Research Papers to
  Read, and Tech Blogs to Read"; after the first version, "rubbish ui ... i want to market my lab via these sources",
  then "use the real images for book, papers and blogs". Owner's choices: public, real pictures.
- `/library` is public (no account needed; linked from the home page header, every footer and the dashboard), titled
  "Read what the builders read.": counts, three section tabs, a big "Start here" pick per section, topic filters with
  colours, and a closing "Start free" panel. Every item has a plain "why read it" note, its level, whether it is free to
  read, and a "Practise it hands-on" link to the LabBox lab and chapter that builds the idea (to sign-up for visitors).
- Real pictures, all stored in LabBox (`library/images/`, 77 WebP files): the 21 book covers (Open Library's cover
  service, current editions by ISBN; the free Speech and Language Processing draft shows its real title page), the first
  page of each of the 17 papers (rendered from the PDFs), and a view of each of the 39 blogs (home page screenshots
  cropped above any cookie banner, nothing clicked; share images or logos where a site blocks automated visits or shows
  a pop-up: OpenAI, NVIDIA, the Substack newsletters, and Netflix's logo from Wikimedia Commons, public domain).
- Owner asked for more: blogs from OpenAI, Claude and Anthropic, Google DeepMind and Research, Meta, Microsoft Research,
  NVIDIA, Karpathy, Eugene Yan, Ahead of AI, Netflix, Uber, Stripe, Spotify, LinkedIn, Dropbox, Slack, Shopify, Werner
  Vogels, Zerodha, PhonePe, ByteByteGo, The Pragmatic Engineer and Hacker News (Jay Alammar's entry now points to his
  Substack), and ten more books (System Design Interview, A Philosophy of Software Design, Site Reliability Engineering,
  The Linux Command Line, Pro Git, Python Crash Course, Effective Java, Grokking Algorithms, NLP with Transformers, Spring
  in Action). Airbnb's, Razorpay's and Swiggy's blogs could not be pictured (bot checks, time-outs) and are left out.
- Admin > Library: add, edit, reorder, remove (with a confirmation), set the "Start here" pick (one per section), the
  lab link, level, "free to read", and upload a picture (JPEG, PNG or WebP up to 6 MB; checked, resized and stored as
  WebP in `LIBRARY_UPLOADS_DIR`, default `/srv/labbox/library`). Only admins; every change logged with the admin's name.
- Data: table `library_item` (migrations 0009 to 0011, additive), filled once from `library/seed.yaml`. `db-copy`
  replaces the seeded rows in a fresh target instead of refusing it (found by the full test run).
- Tests: `tests/test_library.py` (seeding once, public list, pictures served safely, uploads, admin-only changes, one
  "Start here" per section, known labs only, bad input) and `e2e/library.spec.ts` (a visitor, a learner and an admin).

## 24 November (night): RAG and vector databases, a new 13-chapter AI lab

- Owner, going to sleep: "build a micro lab in python for rag and vector databases ... world class ... full standard".
  Syllabus in `HANDOFF.md` after a scan of what others teach (DeepLearning.AI, IBM, Udemy, O'Reilly): this lab builds
  every piece by hand, measures it, then uses the real tool.
- Fieldbook, the rangers' assistant of the fictional Vanrai Hills Wildlife Sanctuary: a 31-section field manual and 24
  patrol reports written for the course, plus 26 test questions in the rangers' own words.
- Everything offline and free: BAAI/bge-small-en-v1.5 embeddings and the ms-marco-MiniLM-L-6-v2 reranker through
  fastembed 0.9.1, baked into `labbox/rag-vector-databases:v1`; FAISS 1.16; Qdrant's client 1.20 in local mode. Only
  chapters 1, 11 and 13 call the model (lab-chat through the gateway); the checks use the fake server. The image limits
  OpenMP and OpenBLAS to 2 threads (a 2-CPU machine sees every host core: brute force took 44 ms instead of 7).
- Measured, not claimed: "closed" and "open" score 0.834, above a true paraphrase (0.796); chunking along sections with
  titles finds the right section first 91% of the time against 73% for 15-word windows; IVF at nprobe 16 keeps 92% recall
  4.5 times faster than brute force; HNSW keeps 98.9% 35 times faster; int8 keeps 99% recall in a quarter of the memory,
  binary bits plus rescoring 100% in a 32nd; hybrid search fixes code questions (CT-112) and loses paraphrases, so its
  hit@1 drops below dense (58% against 77%); reranking reaches 88% first time and 100% in the top 5, at 1.7 s a question.
  The model, asked alone, said camera trap batteries need changing every 1 to 3 months (the manual: 21 days).
- 26 tasks with checks that recognise common mistakes (rows divided by one norm, argpartition left unsorted, an extra
  tail window, summing every right rank in MRR); a task that needs an unfinished one says which. Five playing diagrams,
  13 notes pages, 14 photos (Spärck Jones still to come: Commons 429), three track nodes, a Python and FastAPI cover.

## 24 November: Rust from zero, Part 6 (real programs); the course is complete

- Six chapters, twelve tasks, every output and compiler message captured from real runs: a command-line tool (clap
  derive with `--turbine` and `--low-kw`, a CSV log read with csv and serde; real errors for a bad row, a missing
  file and a mistyped option), smart pointers (an escalation chain in a `Box`, one crew shared by two turbines with
  `Rc<RefCell<..>>`, owner counts 3 then 2, the "RefCell already borrowed" panic), threads (scoped threads, one
  against forty: 15.9 against 3.6 ms on 16 CPU threads, the lesson says learners have 2; alerts over a channel;
  E0277 for an `Rc` sent to a thread), async with Tokio (39 turbines polled at once in 0.14 s, ten one after another
  in 1.36 s; a 500 ms timeout for the far turbine), speed (518,400 log lines: Rust release 27 ms, Python 182 ms,
  Rust debug 177 ms, and Rust written the copying way 62 ms), and an axum capstone (POST readings with 201 and 422,
  a summary with 404; the checks drive the router in memory with tower's `oneshot`).
- Six playing diagrams, six notes pages, one photo (Ryan Dahl, cropped so no cup shows), one track node. The course
  ends with a table of what each part taught and where to go next.
- Rust from zero: 28 chapters, 56 tasks, about 21.7 hours; `test-lab` passes every chapter.
- Ten more real photos across the course (owner: "add more photos to the other chapters too"; drinks that happen to
  be in a real photo are fine): the IBM 704, Niklaus Wirth, Alexander Stepanov, Philip Wadler, Guy Steele, Ken
  Thompson with Brian Kernighan, rope-access technicians on a turbine blade, Rob Pike, a data centre and Tim
  Berners-Lee. 21 real photos in all. Simon Peyton Jones and Bjarne Stroustrup are still to come (Commons 429).

## 24 November: Rust from zero, Part 5 (abstractions without cost)

- Six chapters, twelve tasks, every output and compiler message captured from real runs: generics (one `largest` for
  f64, u16 and char; E0369 asking for the `PartialOrd` bound), traits (`Display` for people, a `Sensor` trait with a
  default method, two sensor types in one `Vec<Box<dyn Sensor>>`; the demo is an example, `cargo run --example
  sensors`, so an unfinished starter does not stop the hidden tests from building), lifetimes (E0106 fixed with
  `'a`; a zero-copy `LogLine` whose fields borrow from the line; E0597 when it outlives it), closures (a rule that
  remembers its limit with `move`, E0373 without it; three boxed rules raised two false alarms for a turbine stopped
  for a storm, and the lesson says so), iterators (2.1 million readings totalled in about 4 ms by both an iterator and a
  loop in release; in debug the iterator was slower, 13.0 against 9.6 ms), and tests (the learner's own tests run on a
  reference library and must catch a planted bug: `>=` turned into `>` at the storm cut-off).
- The check runner has an "own" mode for learner-written tests; the helper's result function is `emit_result`, so it
  never shadows a learner's function (a chapter's own `report` was hidden by it).
- Six playing diagrams, six notes pages (page 19 redrawn: the first lost the apostrophe of `'a`), two photos (Barbara
  Liskov, Kent Beck, reused), one track node.

## 24 November: Rust from zero, Part 4 (collections and errors)

- Four chapters, eight tasks, every output and compiler message captured from real runs: vectors and strings (a
  moving average that smooths an 840 kW gust to a 223 kW swing; `sort()` on `f64` refused with E0277, sorted with
  `total_cmp`; ids joined into a sentence), maps and sets (energy per turbine with `entry().or_insert()`; two runs
  printed the HashMap in different orders, which the lesson shows; 36 of 40 turbines silent in the sample), Result
  and `?` (every broken line of a real log file explained in words; a missing file is an `Err`, not a crash), and
  error types (a thiserror enum with a `TooMuchPower` variant; anyhow's two-layer messages for a 9,999 kW glitch on
  line 3 and for a missing file). Chapter 16 is the first to use crates (anyhow, thiserror), prebuilt in the image.
- The check helper converts `String` errors into failures (`impl From<String> for Fail`).
- Four playing diagrams, four notes pages, one track node.

## 24 November: Rust from zero, Part 3 (shaping data)

- Four chapters, eight tasks, every output and compiler message captured from real runs: structs and methods (a
  Reading from a log line; the power curve flags T12 making 140 kW where 312 are expected), enums and Option (four
  statuses carrying their data; an empty day's peak is None, not a made-up zero), pattern matching (a guard, a range
  of urgent fault codes, E0004 for a forgotten case, the unreachable-arm warning checked for real; `let else` skips
  three broken lines out of six, including `22O0` with a letter O), and modules (E0603 for a private function, `pub
  use` for a short path).
- The check runner can build one hidden test per task (`check_<task>.rs`), so a missing `pub use` does not hide the
  other task's result, and it now says "your code compiles, but the check cannot use it" when only the check's import
  fails.
- Three playing diagrams, four notes pages (page 11 redrawn: the first said `500...=599`), two photos (Grace Hopper,
  Tony Hoare; a Niklaus Wirth photo was left out because it shows a drinks bottle), one track node. Chapter 11's task
  id is `describe_status` (task ids are unique across the lab; chapter 3 has `describe`).

## 24 November: Rust from zero, Part 2 (ownership)

- Three chapters, six tasks, every output and compiler message captured from real runs: ownership and moves (E0382
  with the compiler's own `.clone()` suggestion; a backup vector that is really a copy; a log moved into a function
  and back), borrowing (`&` and `&mut`; E0502 when `push` meets a live reference, E0106 for a reference to a local;
  one meter glitch pushed T07's average to 4,082 kW, capped it is 2,208), and slices and strings (`String` versus
  `&str`, a turbine id sliced out of a log line without copying, the last hour of readings, and a real panic for
  slicing inside `₹`, which is three bytes).
- Three playing diagrams (a move, many readers or one writer, a slice), three notes pages, two photos (John McCarthy,
  the Heartbleed logo), one track node.

## 24 November: Rust from zero, Part 1 (first steps): a new language course on Windwatch, a wind farm's monitor

- New base image `labbox/rust:v1` (Rust 1.100.0 with rustfmt and clippy, gcc as the linker, python3 for the checks)
  and lab image `labbox/rust-basics:v1`: every crate the course uses (anyhow, axum, clap, csv, http-body-util, serde,
  serde_json, thiserror, tokio, tower) downloaded and compiled in advance into one shared build folder
  (`CARGO_TARGET_DIR=/opt/rust-target`, `CARGO_NET_OFFLINE=true`), so the lab needs no internet and a check
  compiles only the learner's crate (about 0.4 s a chapter).
- One Cargo workspace for the course; every chapter folder is its own crate (`members = ["[0-9][0-9]-*"]`), so an
  unfinished chapter never breaks another. Chapters pin their crates' exact versions in their own Cargo.toml (a
  shared `[workspace.dependencies]` list made Cargo 1.100 print ten warnings on every run).
- Checks (`tests/run_checks.py`): a "run" mode that builds and runs a chapter's programs and compares the output, and
  a "test" mode that adds a hidden integration test; `todo!()` and panics become kind "not yet" messages, and the
  compiler's own errors are shown in Output.
- Five chapters, ten tasks, every output captured from real runs: Cargo and the compiler's three real errors, `let`,
  `mut`, `const` and shadowing (whole-number division turned one turbine's 2.5 MW into 2), types (3.05 m/s printed as
  3.0; 250 + 10 in a `u8` panics in debug and is 4 in release), functions and the semicolon error, and control flow
  over a day of wind.
- Running project: **Windwatch**, the turbine monitor of the fictional Kutch Coast Wind Farm (40 turbines, 100 MW).
- Five playing diagrams, five notes pages, four photos (the Gujarat coast's wind turbines, Ferris, Ariane 5,
  Dijkstra), a cover from the Rust logo (Simple Icons, CC0), Rust and TOML highlighting in the classic editor, one
  track node. `tools/authoring/add_diagrams.py` now quotes titles and intros too.

## 24 November: LangGraph, Part 4 (production): the course is complete

- Five chapters, ten tasks, every output captured through the gateway: testing graphs (learners write pytest tests;
  the checks run them on the correct desk and with a planted bug, mutation-testing style), a local server
  (`langgraph.json`, `langgraph dev`, the SDK; the server's real refusal of a graph with its own checkpointer is the
  first task), Deep Agents (a monsoon planner with a FilesystemBackend, a data-analyst subagent and a read permission;
  every count from Python was exact and every number the planner worked out itself was wrong, as the lesson shows), a
  research team (Send fan-out, structured findings, citations checked in Python; the first run's parser rejected the
  writer's `[a, b]` lists and the planner missed the pressure log, both shown and fixed; the report still never links
  the 2.5 bar design pressure to the 3.0 bar raise), and the capstone (intake, two `create_agent` agents as nodes, an
  approval resumed over HTTP; a flooding main still waits for approval and is booked for Thursday, the lesson of
  chapter 6 again).
- The image adds `langgraph-cli[inmem]` (pinned, 29 packages) so labs can run `langgraph dev`. Chapters 22 to 24 share
  an `InMemoryRateLimiter` (0.3 calls a second) to stay under the gateway's 20 calls a minute.
- The author account's daily budget ran out mid-part; the owner approved raising it for this session (backend started
  with LLM_DAILY_TOKENS=400000 and LLM_RPM=60 in its environment only, restored afterwards; backend/.env untouched).
- Five playing diagrams, five notes pages, three photos (the 1947 moth log page, EDSAC, Marvin Minsky; also placed in
  chapters 16 and 17), one AI-track node. LangGraph: 24 chapters, 48 tasks, about 17 hours, 18 real photos.
- Full run green after the course: 282 backend tests on Postgres and Redis (29 minutes), 27 browser tests, 21 labs
  valid.
- Open product question: a learner's daily budget is 50,000 tokens across all labs; a deep agent or research run can
  use a large part of it.

## 23 November: LangGraph, Part 3 (agents in graphs)

- Seven chapters, fourteen tasks, every output captured through the gateway: an agent loop by hand (`bind_tools`,
  `ToolNode`, one conditional edge; two status calls ran in one step; safety advice still came from nowhere),
  reflection (the first one-question checker rejected correct facts and every "I don't know", for real; the final
  checker labels each sentence and Python decides; one answer sent, one handed to a person after "tomorrow" came back
  three times, and the lesson names the cause: the model was never told today's date), agentic RAG (grade, rewrite
  once, search again; the bottled-water question ends in an honest "I will ask a person"), subgraphs (shared keys and a
  translating function; a renamed shared key was tried and silently stays empty, as the lesson says), a supervisor with
  two `create_agent` specialists (the repairs agent read billing's report and booked a second visit: send a task, not
  everything), streaming (progress events and tokens: first token at 2.22 s, done at 3.73 s), and the Functional API
  (a crash resumed without repeating tasks, and an approval with `interrupt`).
- `main.py` in chapters 14 and 15 takes one question per run: a reflection run can make a dozen model calls and the
  gateway allows 20 a minute.
- Seven playing diagrams, seven notes pages, four photos (Shakey, a 1943 library desk, a Teletype Model 33, Barbara
  Liskov), one AI-track node.

## 23 November: LangGraph, Part 2 (persistence and people)

- Six chapters, twelve tasks, every output captured through the gateway: checkpointers and threads (one thread per
  phone, kept in SQLite across processes; the model also invented "a crew is still working" and ignored brown water,
  and the lesson says memory is not facts), long chats (the same six messages trimmed and summarised: the trimmed chat
  forgot the address, the summarised one read it back; the summary also bent a fact), durable execution (a retry
  policy for a flaky SMS gateway; a crashed job resumed with `invoke(None, config)`, and the start-over version booked
  the crew and the Rs 18,000 parts twice, for real), interrupts (big repairs wait for the engineer across processes;
  the approval node visibly runs twice; the brief invented "frequent leaks" as a reason), time travel (a rust complaint
  mis-triaged by the rules, its history, and a correction that branches from the step after triage; `as_node="route"`
  was tried and fails with KeyError, as the lesson says), and stores (a reply language kept across threads per phone,
  and crew notes searched by meaning).
- Seven playing diagrams, six notes pages, five photos (an IBM System/360, the Central Telegraph Office in Kolkata, the
  first Type G loom, a flight data recorder, a Rolodex), one AI-track node.

## 23 November: LangGraph, Part 1 (thinking in graphs): a new AI course on Harsh, a water board's repair desk

- New lab `langgraph` (image `labbox/langgraph:v1`, built on `labbox/langchain:v1` with LangGraph 1.2.24 pinned).
  Running project: **Harsh**, the complaint-to-repair desk of the fictional Ujjwal Nagar Water Board. Checks are
  pytest with the fake OpenAI server from the LangChain lab, about a second a chapter.
- Six chapters, twelve tasks, every output captured through the gateway: a first graph and its stream of steps,
  reducers (a log that grows; severity that never goes down, so brown water near a hospital stays urgent), branches
  and a spelling retry loop with a limit, model nodes (four messy complaints triaged right, including Hinglish; the
  reply to "my children drank it" had no health advice, and the lesson says that belongs in code), the workflow
  patterns (a parallel join; a grader that rejected a notice for the right reason, then passed one that missed the
  area names), and `Send` and `Command` (a storm night: five triages in one step; urgent dirty water was scheduled for
  tomorrow because `plan` only checked the cost).
- Six playing diagrams, six notes pages, six photos (an overhead water tank in Raichur, Euler, Konigsberg on the
  Pregel, Lillian Gilbreth, Dijkstra, a 1900s mail sorting room), a cover from the LangGraph logo, one AI-track node.

## 23 November: LangChain, Part 5 (production): the course is complete

- Six chapters, twelve tasks, every output captured through the gateway: built-in middleware (an opt-in tool-error
  handler, a 5-call limit, a thread summarised once it passed 8 messages), custom middleware (a prompt per member:
  Ravi answered in Marathi, Asha in English; an audit of every tool call), guardrails (Aadhaar numbers masked to
  `****1176` by a custom detector; a 717-character message refused with no model call; the "block" strategy turned out
  to raise an error, and the lesson says so), human in the loop (the manager edits, approves and rejects real
  bookings), evals (a golden set scored 67% and a judge model found two real bugs: the half 50-crate rule and a missed
  joining fee), and the capstone (FastAPI with tools, the fixed rule book, PII masking, approvals, and long-term facts
  per member that reached a new thread).
- The capture account's daily budget ran out mid-part; the owner approved raising it for this session (backend started
  with LLM_DAILY_TOKENS=300000 and LLM_RPM=60 in its environment only, restored afterwards; backend/.env untouched).
- Two diagrams (middleware around a run, a booking waiting for the manager), six notes pages, four photos (Xerox PARC,
  a two-key vault lock, Kent Beck, onion grading), two AI-track nodes. LangChain: 27 chapters, 54 tasks, about 19
  hours, 13 real photos.

## 23 November: LangChain, Part 4 (knowledge and MCP)

- Five chapters, ten tasks, every output captured through the gateway: documents and chunking (a plain-Python loader,
  because `langchain-community` is being retired; the splitter left the heading "Cold storage" alone and cut the
  50-crate rule in half), vector stores (real cosine scores, 0.6 for matches and 0.09 for France; the 0.3 threshold also
  dropped a right answer at 0.298), RAG as a tool (three real failures shown: the agent never searched, then searched
  for one word, then answered wrongly from half a rule), retrieval quality (a golden set; titled chunks raised hit@1
  from 75% to 88%; splitting at sentences kept the rule whole; a naive query rewrite mistranslated the Marathi question
  and a better prompt fixed it), and MCP (a FastMCP server and LangChain's `MCPAdapter`, beta).
- The co-op's rule book (five files); the fake OpenAI server reads token ids and has more keywords.
- Two diagrams (agentic RAG, MCP), five notes pages, two photos (metal type for chapter 2, Cranfield's library), one
  AI-track node.

## 23 November: LangChain, Part 3 (agents)

- Seven chapters, fourteen tasks, every output captured through the gateway: an agent loop by hand (two tool calls in
  one turn), `create_agent` (the garlic question needed no tool; we found that a tool's exception stops a
  `create_agent` run and that the default recursion limit is 10,007, and the lessons say so), tools with docstrings and
  `ToolRuntime` context (logged in as Ravi, "I am actually M-221" still got Ravi's 40 crates), structured output
  (a strict `Literal` turned garlic into an onion booking; an "other" choice fixed it), images (a real downy mildew
  photo was called "powdery mildew" with fungicide advice until a rules message sent members to the agronomist; one
  photo cost 8,697 tokens), short-term memory with a checkpointer and one thread per member, and streaming an agent's
  steps and words (the first version printed every step at the end; it now reports each one as it arrives).
- Two diagrams (the agent loop, memory threads), seven notes pages, three photos (the IBM 701 for chapter 1, a slide
  rule, Alexis Millardet), two AI-track nodes.

## 23 November: LangChain, Parts 1 and 2 (a new AI course: Navin, a farmers' co-op help desk)

- New lab `langchain` (image `labbox/langchain:v1`: LangChain 1.5.2, LangGraph 1.2.24, OpenAI SDK 3.57, all 109
  packages pinned and installed offline). Syllabus from docs.langchain.com plus a scan of what LangChain Academy,
  DeepLearning.AI, Udemy, Coursera and freeCodeCamp teach; owner chose two labs (LangChain, then LangGraph) and the
  names Navin and Harsh.
- Part 1 "How language models work" (4 chapters, plain Python): rules against a learned threshold (8 mm), tokens with
  tiktoken (English 7, Devanagari 8, Marathi in English letters 11), real 256-dimension embeddings ("kanda bhav" found
  the onion rate with a cosine of only 0.155), softmax and attention.
- Part 2 "Calling a model" (5 chapters): raw HTTP (the gateway's real request log), the OpenAI SDK (a real hallucination:
  "No, we do not store tomatoes"), init_chat_model and messages, temperature and streaming (first piece after 769 ms),
  an honest prompt with facts ("I don't know" for garlic) and the cost of each answer.
- Checks are pytest with a fake OpenAI server (`tests/common/fake_openai.py`), about a second per chapter.
- Cover with the real LangChain mark (Simple Icons, CC0), colour #4fd1a5, the nested-oval AI circles, two more playing
  diagrams, nine notes pages, four photos; two AI-track nodes; `test_test_lab` includes the lab.

## 23 November: lesson images 11 times lighter

- The handwritten-notes pages were saved exactly as the image service returned them, about 2 MB each. 47 images over
  400 KB (30 LangChain4j notes, 15 Spring AI, one Go, one Spring) are now WebP quality 80: 82 MB down to 7 MB, the
  handwriting still sharp. A recap page now loads about 180 KB instead of 2 MB.
- `tools/authoring/notes.py` saves new pages the same way, so this does not come back.

## 23 November: LangChain4j, more photos and diagrams (owner: "it will be better as the lab is large")

- Six more real photos (Tomas Mikolov, Douglas Crockford, telephone switchboard operators in 1915, Facebook's
  Prineville data centre, a library card catalogue, a level-crossing gate in Kerala): 18 in all. One candidate (a
  Great Indian Peninsula Railway ghat, 1860s) was left out: its licence is "no known restrictions", not one of ours.
- Six more playing diagrams, each with this course's real numbers: one streamed answer (905 ms, 2103 ms), a sliding
  memory window, an MCP client and a stdio server, one embedding-store search (0.712, threshold 0.7), guardrails
  around one call, and the supervisor's real plan (420, then 840): 18 diagrams in all.

## 23 November: nested-oval diagrams (owner: "wasn't this better as a Venn diagram animation?")

- A new playing diagram, `SketchNested` (`frontend/src/lesson/Sketch.tsx`): sets inside sets drawn as hand-drawn
  ovals, lit from the biggest to the smallest with Play, Back and Next; the current oval is outlined and bold, the
  ones not reached yet stay faint; one soft colour per depth, in both themes. LangChain4j chapter 1's "AI, machine
  learning, deep learning, generative AI, LLM" now uses it instead of a list.
- Browser test `e2e/nested-diagram.spec.ts` (27 browser tests).
- Full run: 280 backend tests on Postgres and Redis; 27 browser tests on 4 workers (two flaky under load, green on
  rerun).

## 23 November: LangChain4j, Part 5 (production and agents): the course is complete

- Part 5, "Production and agents" (6 chapters, 12 tasks), every model output captured through the gateway:
  - guardrails: an input guardrail that refuses questions over 300 characters before any token is paid for, and an
    output guardrail that removes mobile numbers (the real answer without it repeated "98220 12345");
  - observability: a `ChatModelListener` counting calls and tokens, and a golden set of six questions; removing the
    "I don't know" sentence from the prompt made the model invent "the Ghat Express does not offer wi-fi" (83%);
  - agents (`langchain4j-agentic`): a classifier agent with an output key, and a sequence with a reply writer;
  - workflows: a conditional route to three desk agents and a scored review loop capped at three rounds; three jobs
    took 11 model calls, and the gateway's rate limit (20 a minute) stopped the first attempt;
  - a supervisor over a fare agent and a date agent: its first real summary said two adults pay 420 (the fare for
    one); `supervisorContext` fixed it (840), and the lesson says why a tool is the sturdier fix;
  - the capstone, a Spring Boot app with tools, RAG, memory, guardrails, a listener and answers with sources; a real
    bug found on the way: input guardrails see the message after RAG adds the rules, so the capstone's guard measures
    `userMessageTemplate()`.
- Two more playing diagrams (a sequence, a routed review), six notes pages, two AI-track nodes.
- LangChain4j now has 30 chapters, 60 tasks, about 22 hours.
- Seven more real photos (Weizenbaum, Gosling, Lonavla station, a Teletype Model 33, Kalman, an IBM flowchart
  template, the Konkan Railway): 12 in all, so the course is at the full standard.

## 23 November: LangChain4j, Part 4 (tools, MCP and knowledge)

- Part 4, "Tools, MCP and knowledge" (6 chapters, 12 tasks), every model output captured through the gateway:
  - tools: a Java date tool fixed chapter 15's wrong Saturday (the model called `nextDate` and `fare` in one reply);
  - an MCP client for the reference filesystem server (Node.js, pinned, offline in the image): with all 14 tools the
    model searched file names and wrongly said there were no notices (1,222 tokens a call); filtered to two reading
    tools it found the track work (305 tokens);
  - our own MCP server in Java (`langchain4j-community-mcp-server`), with a real misleading timeout whose cause was the
    classpath under `exec:java`;
  - embedding stores with OpenAI embeddings: LangChain4j scores are (cosine + 1) / 2, so the 0.5 threshold matched
    "capital of France"; 0.7, chosen from real scores, does not;
  - RAG over five rule documents (the real augmented prompt is quoted; for wifi the retriever brought only a heading,
    and the "answer only from the information" instruction kept Setu honest);
  - a local model through Ollama (Qwen 2.5 0.5B, captured on this machine, Ollama stopped again) and `RoutingChatModel`.
- The fake OpenAI server's toy embeddings use railway keywords.
- Two more playing diagrams (a tool call, RAG), six notes pages, two AI-track nodes.

## 23 November: LangChain4j, Part 3 (AI Services)

- Part 3, "AI Services" (6 chapters, 12 tasks), every model output captured from gpt-4o-mini through the gateway: an
  AI Service as an interface implemented by a proxy (`jdk.proxy3.$Proxy28`), instructions from a resource file with
  `@SystemMessage(fromResource = ...)`; prompt templates with `PromptTemplate.apply` and `@UserMessage`/`@V`; structured
  output into a record and an enum with strict JSON schemas (the real schema is quoted, and the model's real wrong date,
  a Thursday for "this coming Saturday", leads to tools); streaming with a handler and a `TokenStream` (first piece
  after 905 ms, all after 2103 ms); chat memory, shared and per passenger with `@MemoryId`; and Setu as a Spring Boot 4
  web API with `@AiService` and `POST /chat`.
- The check runner names the cause when the Spring app cannot start for lack of an `@AiService` bean.
- One more playing diagram (inside an AI Service), six notes pages, two AI-track nodes.

## 23 November: LangChain4j's cover uses its real logo

- Owner: "use LangChain4j's real logo". The cover now shows LangChain4j's own parrot logo (from the project's Apache 2.0
  repository, `tools/logos/langchain4j.svg`) on a deep green, credited to the LangChain4j project; the lab's accent
  colour follows the logo's orange.

## 23 November: LangChain4j, Part 2 (calling a model from Java)

- Part 2, "Calling a model from Java" (6 chapters, 12 tasks), every model output captured from gpt-4o-mini through the
  gateway with a separate author account: a chat completion over Java's own HttpClient (with a real HTTP/2 upgrade error
  and its fix), the official OpenAI Java SDK (whose first real answer invented two trains), the first LangChain4j app
  (`OpenAiChatModel` behind the `ChatModel` interface, system and user messages), parameters (temperature 1.5 against
  0.0, a 20-token limit ending in finish reason LENGTH), open and closed models and hallucinations (without the
  timetable the model said the 7:15 leaves at 6:00 and that a Tuesday-less train runs on Tuesdays; with it, every
  answer was right, and it said "I don't know" about wifi), and token usage turned into a yearly bill.
- The fake OpenAI server used by the checks also records each request's Authorization and Content-Type headers.
- One more playing diagram (a model call through the gateway), six notes pages, two AI-track nodes.

## 23 November: LangChain4j, Part 1 (a new AI course: Setu, the help desk of a hill railway)

- New lab `langchain4j`, built from the owner's syllabus (the Telusko LangChain4j video's chapter list) and the
  official documentation at docs.langchain4j.dev, at LangChain4j 1.24.0. Running project: **Setu**, the passenger help
  desk of Sahyadri Rail, a fictional hill railway from Pune through the Western Ghats. 30 chapters are planned in five
  parts (`HANDOFF.md`); this commit is Part 1.
- Part 1, "How language models work" (6 chapters, 12 tasks), in plain Java with nothing calling a model: rules versus a
  threshold learned from examples; a neuron trained with Rosenblatt's perceptron rule (and why it cannot learn XOR);
  a bag of words and a bigram model that writes station announcements; tokens counted with gpt-4o-mini's real tokenizer
  (Marathi takes twice the tokens of English) and a context window; embeddings from a real model running inside the
  program (BGE small, offline) with cosine similarity and search by meaning; softmax with temperature and attention
  weights. Every output in the lessons was captured from the real programs.
- New image `labbox/langchain4j:v1` (Java 21, an offline Maven repository with LangChain4j, the OpenAI Java SDK, agents,
  MCP, easy RAG, Ollama and the Spring Boot 4 starters; Node for the filesystem MCP server; the local embedding
  model's tokenizer cached in the image). The image pre-fetches each chapter's exact dependencies.
- Checks are JUnit tests copied into each chapter's project; from chapter 7 on they use a fake OpenAI server.
- 5 real photos (the Bhor Ghat railway, Alan Turing, the Mark I Perceptron, Andrey Markov, the transformer), 6 playing
  diagrams, 6 handwritten notes pages, two AI-track nodes.
- The cover uses the Java logo for now: LangChain4j's own logo shows a cup of coffee (owner to decide).

## 23 November: the AI tutor uses OpenAI; Ollama stopped to free memory

- Owner: "I am not using Ollama in the AI tutor, use OpenAI", and "do all the required to free up memory".
- `LLM_MODELS` now maps every alias to OpenAI: `lab-chat`, `lab-chat-smart` (the tutor and the design-review
  grader) and `ai-chat` to gpt-4o-mini; `lab-embed` and `ai-embed` to text-embedding-3-small. Budgets and the
  request log are unchanged. Checked: a real tutor answer came back from gpt-4o-mini through the gateway.
- Editor ghost-text completion (`lab-code`) is off: it needs a fill-in-the-middle model, which gpt-4o-mini is not.
- The Ollama container is stopped and no longer starts at boot (`scripts/ollama.sh` brings it back).
- The privacy policy now says that the tutor, design reviews and AI labs send the question and code to OpenAI
  through our gateway, with no name or email.
- Memory on the laptop: 30 lab machines left by browser tests stopped, Ollama stopped, old temp files removed
  (`/tmp` lives in RAM here). Available memory went from 2.6 GB to 6 GB.

## 23 November: the dashboard shows labs by category

- `/labs` groups the lab cards by category, in the owner's order: AI, Languages, Frameworks, System design,
  Databases, DevOps, then Cloud and AWS (shown as "coming soon" until they have labs). Chips at the top jump to
  a category and show how many labs it has; inside a category, full courses come first. Browser test:
  `e2e/categories.spec.ts`. A trial "paper notes" look was built, shown and removed at the owner's request.
- The drink rewrite also renamed Dabba Express (Express and Python collections) to Thali House, a cloud kitchen,
  and fixed a Spring Boot check that compared merchant names without spaces.

## 23 November: no drinks anywhere (owner: "yes rewrite the drink examples")

- Every drink example is rewritten, in all 13 labs that had one, the app, the drills, the lab templates and the specs.
  Replacements keep the same length and the same alphabetical place, so sorted output, padded columns, slices and
  quoted outputs stay true without recapturing:
  - Spring Boot: Mango lassi becomes Mango kulfi, Filter coffee becomes Fruit custard, Rose milk becomes Rasmalai
    (SKUs KUL-1, CUS-1, RAS-1), the `drinks` category becomes `sweets`, Brew Point becomes Book Point.
  - Python, JavaScript, Go and Java from zero, Redis: juice becomes jelly, milk becomes mint, coffee becomes cookie.
    Java's printed HashMap orders were checked against Java's hashing: unchanged.
  - Go from zero, chapter 8: the UTF-8 example "café" becomes the name "José" (same bytes: 5 bytes, 4 runes, the
    accent at byte 3); `cafe.go` is now `jose.go`, its output was rerun in the lab image, and the chapter's notes
    page was redrawn and checked letter by letter.
  - Small labs: Ravi's Tapri (a tea stall) becomes Ravi's Snack Corner (FastAPI, JavaScript inside out), Tapri
    Counter becomes Dosa Counter, Brew Point (a coffee chain) becomes Book Point, a bookshop (Java collections, rate
    limiter, Postgres transactions); the Postgres labs' database `tapri` is now `shop` (a learner who already
    opened one of them needs Reset lab); the ai template's barista bot is a bookshop assistant.
  - App: the home page tour, the login terminal, a drill, the CLI help, and the tests that quoted the old text.
- Java from zero's history now says the name Java was "borrowed from the island of Java in Indonesia".
- Left on purpose: the SQL task id `q_paid_coffee` (learner progress is stored under it), and the owner's spec files.

## 23 November: the full standard and how courses are made, written down

- `COURSE_PRODUCTION.md` (new): how a LabBox course is built, in 12 steps from the syllabus to the commit, the
  way the ten full courses were built: deciding plain or story and the running project (and the banned
  examples), following the official docs, the lab folder and its offline image, the chapter projects and
  their TODOs, the hidden checks, writing the chapters, capturing every output for real (AI output through
  the gateway with a separate author account and its own budget), photos from Wikimedia Commons, playing
  diagrams, the handwritten notes and how to check them, cover and track, the tests, and the records.
- `tools/authoring/` (new): the helper scripts that until now lived only in a session's scratchpad, cleaned
  up and with no hard-coded paths: `commons_search.py`, `commons_fetch.py`, `insert_photos.py`,
  `add_diagrams.py`, `notes.py`, `author_token.py`, `capture.sh` (a capture machine from the lab's image) and
  `runcheck.sh` (one chapter's fresh checks on the starter or solution).
- `CONTENT_STANDARD.md`: the full standard as one list at the top (what every course has, and which course to
  look at); course length, history per chapter, measured speed and money, and official references added to
  section 1; the drink examples it still held up as good examples replaced.
- `ROADMAP.md`: a table of all 18 labs (chapters, tasks, hours, running project, photos, standard), what is left
  per lab (the eight short labs, the drink words still in older examples, by lab), the AI track's first course,
  and current pick-up instructions.
- `HANDOFF.md`: cut to a short resume note (state, what waits for the owner, how to start, how each full
  course is checked, ideas, flaky tests); the older file-by-file notes stay in git history and this changelog.
- `README.md` and `AGENTS.md`: point to the new guide; the chapter-format example no longer uses Dabba Express,
  and the cover examples no longer use a coffee stall.

## 23 November: Spring AI, Part 4 (pictures, evaluation, guardrails, cost, agents, Atlas goes live): course complete

- Owner, going to sleep again: "please finish this spring ai completely". Part 4, Beyond text, and production (6
  chapters, 12 tasks), following the official reference:
  - Pictures in, words out: a question and a photo in one message, and a photo turned into a record with a closed list
    of exhibits and an honest "none". Measured: one 800 by 600 photo cost 25,596 input tokens with gpt-4o-mini; shrunk
    to one 512 pixel tile (a provided `Photos.shrink`), 8,595. The photos learners send ship in the project, credited.
  - Evaluation: a golden set of 15 questions and a retrieval hit rate (real: 10 of 15, each miss explained), then
    `RelevancyEvaluator` as a judge on a fresh `ChatClient` (it rightly flagged the useless answer to a broad question).
  - Guardrails: prompt injection's history, three real attacks (resisted, but with over-refusals), a length-limit
    advisor returning a `GuardrailRefusal`, `SafeGuardAdvisor` as a privacy guard, and a real bypass of its word list.
  - Cost, speed and metrics: usage metadata priced per answer (about 95 tokens in, 0.003 to 0.005 US cents), Actuator
    and `gen_ai.client.token.usage` (the untagged total counts tokens twice: filter by type).
  - Workflows and agents, after "Building Effective Agents": routing (three right desks) and a write, review and
    rewrite loop that always ends. Real: the reviewer rejected a 32-word label as "46 words", so counting belongs in Java.
  - Atlas goes live: every piece in one `ChatClient` behind a lobby screen page (a second preview). Real: a follow-up
    ("And when did it land there?") was refused because retrieval found nothing; the lesson teaches query rewriting.
- The course is complete: 20 chapters, 40 tasks, about 16.5 hours. Every quoted model output came from the real model
  through the gateway, within the author account's daily budget (it stayed on; the last captures waited for midnight UTC).
- Photos (a Foucault pendulum, a prism, a Rajasaurus skull cast, a steam engine, hallmarks, a ghat road, an electricity
  meter, a 1907 switchboard, Bengaluru's Visvesvaraya museum), notes on all 20 recaps, 6 more playing diagrams, three
  more ai track nodes.

## 23 November: Spring AI, Parts 2 and 3 (memory, tools, MCP, embeddings, vector stores, ETL, RAG)

- Owner, going to sleep: "please finish complete spring ai. and fyi, spring ai has different logo". The syllabus
  follows the official reference (docs.spring.io/spring-ai/reference, 2.1.0), so the course moved to **Spring Boot
  4.2.0 and Spring AI 2.1.0** (Part 1's text and projects updated: the timeline, the structured output deep dive).
- Part 2, Conversations and tools (5 chapters, 10 tasks): session memory with the new Session API (per visitor, a
  turn-count compaction window), tools (`@Tool`, with the real date mistake the model made and the `nextDay` tool that
  fixed it), tools you can trust (tool call confirmation, a deny message the model cannot embellish, identity in the
  `ToolContext`), advisors (a usage counter and a language advisor, with real Marathi and Hindi answers), and MCP
  (Atlas's tools served over Streamable HTTP, called by a real MCP client in the check).
- Part 3, Knowledge (4 chapters, 8 tasks): embeddings and cosine similarity (by hand, then in Java), a vector store with
  real similarity scores and an honest miss, the ETL pipeline (Markdown reader, token splitter: the miss fixed by giving
  the visitor card headings), and RAG with sources. Every threshold was set from real measured scores.
- The museum's 12 exhibit cards are real science (Foucault's pendulum, Mangalyaan, Chandrayaan-3, Rajasaurus...).
- LLM gateway: embeddings have their own limits (`LLM_EMBED_RPM` 300, `LLM_EMBED_DAILY_TOKENS` 500,000), because
  `SimpleVectorStore` embeds one document per request and hit the 20-a-minute chat limit at start-up.
- The Spring AI logo (a leaf in a brain) replaces the Spring leaf on the cover; brand colour `#7eb050`.
- Photos (Samuel Parris's 1817 journal, a reading room desk, a cheque signed by Dickens, the Fort Augustus locks,
  USB-C, Mercator's 1569 map, the Graz subject catalogue, the Plantin-Moretus presses, an open book), handwritten notes
  on all 14 recaps, 10 more playing diagrams; the ai track has six Spring AI nodes.

## 23 November: Spring AI, Part 1 (a new course: Atlas, the museum guide)

- Owner, going to sleep after Linux: "once done, move to Spring AI". OpenAI is the course's model, only through the
  LLM gateway: two new aliases, `ai-chat` (gpt-4o-mini) and `ai-embed` (text-embedding-3-small), added to the default
  `LLM_MODELS`; the tutor and other labs stay on Ollama. The key stays in `backend/.env`; budgets and logs apply.
- New lab `spring-ai` (track `ai`): Java 21, **Spring Boot 4.0.10 and Spring AI 2.0.3** (the current major line; 2.1.0
  was four days old), every library in an offline Maven repository in the image. The running project is **Atlas**,
  the visitor guide of a fictional science museum in Pune. One Maven project per chapter, like the Spring Boot course.
- Part 1, First steps (5 chapters, 10 tasks): why AI in your app (LLMs, tokens, ELIZA to ChatGPT to Spring AI, what
  answers cost), prompts (system prompts and templates, with the real failures of a first-draft prompt), options and
  token usage, streaming with server-sent events, structured output into records (including the real "bare list"
  failure and its fix). Every model answer quoted in the lessons came from the real model through the gateway.
- Checks never call a model: hidden JUnit checks start a fake OpenAI-compatible server, point the learner's app at it,
  and grade the requests the app sends (system prompt, options, schema, streaming) and how it handles the replies.

## 23 November: Linux on call rewritten to the full standard (15 chapters, Tara)

- Owner's order after Git: Linux, then a new Spring AI course. The old course was 2 chapters and 5 tasks about a lunchbox
  delivery company; at the owner's request (never Dabba Express, nothing that resembles the Chai aur Code platform)
  it now follows **Tara**, a small radio telescope observatory near Pune whose Linux server records the sky every
  night. 15 chapters, 31 tasks, about 11 hours. The old ids (`01-reading-logs`, `02-disk-and-permissions` and their
  five tasks) are kept, as chapters 5 and 9.
- Part 1 Starting out: why Linux (Unix 1969, GNU 1983, Linus Torvalds 1991, why servers run it and what it saves),
  files and folders with globs, reading files and man pages, pipes and redirection. Part 2 Everyday tools: logs with
  grep and awk, find and grep -r, users and permissions, processes and signals, a full disk (a deleted file that is
  still open, shown for real with lsof). Part 3 Automating: scripts in strict mode (the 2015 Steam `rm -rf` accident),
  loops with dry runs, the environment and PATH. Part 4 Servers: networking with ss and curl, systemd units and cron,
  and a capstone on the night of a lunar eclipse (three planted faults, then a watchdog).
- Live checks (read-only workspace); scripts run in scratch copies on inputs the learner has never seen: a stop.sh is
  tested on real processes (one ignores TERM, and pkill -f stopping itself is caught), a background job must survive a
  hang-up, a health check must say DOWN for a 500, a closed port and a slow answer. The lab image now has man pages,
  tree, lsof, ss, jq, htop, psmisc and nc. Every quoted output was captured on the lab machine (systemctl status from a
  real Ubuntu server).
- Real photos (Ken Thompson and Dennis Ritchie, a young Linus Torvalds, Jocelyn Bell Burnell in 1967, a radio
  telescope near Pune, the IBM 350 disk, a 1786 ship's log, a Jacquard loom and more), handwritten notes on all 15
  recaps, 11 playing diagrams; the devops track has five Linux nodes.

## 22 November: Git without fear rewritten to the full standard (14 chapters, Trails)

- Owner's order: Git, then Linux, then a new Spring AI course (OpenAI as its model). For Git: "you decide best. It
  should be world class at the same time easy to understand". The old course was 2 chapters and 5 tasks about a
  coffee shop; it is now 14 chapters, 28 tasks, about 10 hours, around **Trails**, a small website about treks in
  the Sahyadri hills, written by Asha, Ravi and Meera. The old ids (`01-commit-branch-merge`, `02-undo-without-fear`
  and their five tasks) are kept, retitled.
- Part 1 Starting out: why version control exists (BitKeeper, Linus Torvalds in April 2005, Junio Hamano, every copy
  a full copy), commits and the staging area, reading history (log, show, blame, log -S), branches and merging,
  merge conflicts. Part 2 Undo without fear: undoing local work (restore, amend, reset), undoing shared history
  (revert, the reflog), stash and clean. Part 3 Working with others: remotes (a rejected push, handled), a pull
  request end to end, rebase and squash, what is inside .git (blobs, trees, commits, a hash computed with sha1sum).
  Part 4: good habits (.gitignore, annotated tags) and a capstone (clean a leaked file from unpushed history, then
  merge, tag and push a release).
- Every chapter has its own practice repository, built by its setup with fixed authors and dates, so every learner
  gets the same hashes; chapters 7, 9, 10 and 14 add a bare "server" repository. The check reads the repositories with
  read-only git commands; typical mistakes (deleting a secret in a new commit, markers left in, a lightweight release
  tag, `git clean -fd` taking a keeper, an unpushed revert) get their own messages. Every output quoted in the
  lessons was captured from the lab image (git 2.43).
- 10 real photos (Rajmachi fort, Linus Torvalds, a Domesday Book page, Darwin's 1837 tree sketch, a merge sign, the
  Svalbard seed vault, Proust's corrected proofs, a fingerprint card, Nagpur's Zero Mile Stone, a mountain rescue
  team), handwritten notes on all 14 recaps, 11 playing diagrams; the devops track lists the new chapters.

## 22 November: SQL from zero rewritten to the full standard (14 chapters, Safar)

- Owner: "once redis is finished, start with SQL". The old course was 2 chapters and 4 tasks about a tea and coffee
  stall ("Tapri Counter", database `tapri`). It is now a full course on a new running project, **Safar**, a bus
  ticket booking app (8 cities, 16 routes, 16 buses, 480 trips, 2,000 passengers, 12,005 bookings in November
  2026), in a database called `safar` (the setup creates it on machines that only have the old one).
- 14 chapters in four parts, 28 tasks, about 10.5 hours; the old ids (`01-select-and-where`, `02-group-by`) and
  tasks (`q_paid_coffee`, `q_count_refunds`, `q_revenue_by_outlet`, `q_top_item`) are kept, retitled.
  Part 1 Starting out: why databases exist (Codd, SEQUEL, Oracle, Stonebraker's Postgres), asking for rows,
  sorting and shaping, text, dates and NULL. Part 2 Many tables: joins, totals, subqueries and CTEs, window
  functions. Part 3 Changing data: tables and constraints, changing data safely (the missing WHERE, inside a
  transaction), transactions (two sessions, all or nothing). Part 4 Fast and safe: indexes measured with EXPLAIN
  ANALYZE (two million searches: 84 ms to 0.7 ms, and what that is worth in CPU), designing tables
  (normalising operators), and a capstone report.
- Every output quoted in the lessons was captured from the lab's Postgres 16. Each chapter has its own folder;
  query tasks are checked against a reference query (order-sensitive when the task asks for an order); tasks that
  change data are checked from the database's state, with rule tests run inside a transaction that is rolled
  back. Typical mistakes get their own messages (wrong order, unnamed column, one index per column, deleted
  instead of cancelled).
- 9 real photos (an MSRTC Shivneri coach, Don Chamberlin, Michael Stonebraker, an Indian Railways reservation chart
  board, an 1870 railway map of India, an IBM 407, Luca Pacioli, the index of a 1655 atlas, Bradshaw's 1840 railway
  guide), handwritten notes on all 14 recaps, a playing left-join diagram, traces for GROUP BY and running totals.
  `test_focus.py` follows the new layout; `test_progress.py` finds a task without a card in any lab.

## 22 November: Redis in practice revamped to the full standard (17 chapters, Basket)

- Owner, going out: "revamp redis to the full standard ... why redis came, what was the problem, how much money it
  can actually save in a high performance application, performance impact ... real images, handwritten images,
  animations, tables, and much more", and "remember this for every lab". Built without stopping, as asked.
- A new running project, **Basket**, a 10-minute grocery delivery app in Pune (two dark stores, a slow catalogue
  service at 1.5 s and Rs 0.10 a call), replaces the Brew Point coffee shop: no drinks anywhere.
- 17 chapters in three parts (Starting out, Redis in an app, Redis in production), 39 tasks, about 13 hours. Every
  old chapter id and task id is kept; numbering is by position. Four new chapters: 1 Why Redis exists (the latency
  ladder, memcached and LLOOGG, Google's half second, Stack Overflow's 5.8 billion Redis hits in 2.8 hours against
  505 million SQL queries in 168 hours, what a hit rate is worth in money, `redis-cli --latency` and
  `redis-benchmark`; tasks `measure_latency`, `measure_redis`), 8 What the cache saves (hit and miss counters and a
  `/savings` report in seconds and rupees, about 124 bytes per cached price measured; tasks `hit_counter`,
  `savings_report`), 9 The stampede (`stampede_lock` moved here, new `jitter_ttl`), 13 Measuring Redis (throughput
  four ways, Big O, `INFO commandstats`, the slow log read correctly; tasks `slow_key_found`, `slowlog_config`).
- Every other chapter rewritten in the curiosity-first teacher's voice, every quoted output captured from the lab
  image (1.5 s to under 1 ms on the learner's own app, a coin race at minus 1,500, 30 catalogue calls to 1).
- App chapters each have a folder (`06-redis-from-python/` to `11-locks/`, `17-capstone/`) with their own app,
  plus small scripts to see each bug (`compare.py`, `stampede.py`, `race.py`, `book_race.py`). The check runs only
  the chapter's tasks (`LABBOX_TASKS`) and names the folder to start; a 404 from another chapter's app says so.
  `solution/apply.sh` serves every chapter's solution from one combined app.
- Fixes found on the way: the coin race now fails the starter every time (a 100 ms payments check), the slow log
  holds three entries with the slowest one oldest, chapter 14 seeds its own carts for the "deleted too much" check.
- 15 real photos, each on the step that teaches its idea: Salvatore Sanfilippo and Brad Fitzpatrick (history),
  Grace Hopper's nanosecond wires (the latency ladder), an open hard disk, an hourglass (expiry), the Augusta
  leaderboard (sorted sets), a log cache in Alaska (where the word cache comes from), wildebeest crossing the Mara
  (the stampede), a Stockholm turnstile (rate limits), a Tyer's tablet instrument (one token, one train: locks),
  Edison's stock ticker (streams), a memory module, a flight data recorder (the append-only file), Wikimedia's
  servers (replication) and Apollo 9 Mission Control (the capstone). Wikimedia rate-limited two originals; real
  thumbnails (and, for Hopper, the Navy's own photo of the wires) were used instead. A handwritten notes page on
  all 17 recaps, every line checked.
- Eight new playing diagrams (latency ladder, hit rate savings, one command at a time, cache-aside, stampede, lock,
  slow command, eviction); the old Redis diagrams relabelled for Basket. Tests moved to the new layout
  (`test_focus.py`, `test_tutor.py`, `chapter-focus.spec.ts`, `editor.spec.ts`); the databases track lists the new
  chapters.

## 22 November: real photos spread through every course (10 to 15 each), starting with Spring Boot

- Owner: photos sat at the start of each lab and almost vanished in the middle and the end. New rule: 10 to 15 real,
  credited photos per lab, spread through the whole course, each on the step where its idea is taught, never filler.
- Spring Boot: 2 photos became 12. Tim Berners-Lee (chapter 0), Douglas Crockford for JSON (3), Roy Fielding for REST
  and a 1975 telephone switchboard for the DispatcherServlet (10), the IBM 350 RAMAC disk (19), a library card
  catalogue for paging (22), the Enfield bank of the first cash machine for transactions (23), a crash test dummy
  for tests (25), the Belgica's ship's log for logging (27), an Enigma machine for security (28). No freely licensed
  photo of Rod Johnson exists, so his story stays in the text.
- Python from zero, 7 to 14: Ada Lovelace (functions), a Jacquard loom (loops), the Rosetta Stone (strings), a jukebox
  (lists), an IBM card sorter (sorting by key), the Mars Climate Orbiter (raise), Margaret Hamilton (testing).
- Java from zero, 7 to 12: a blueprint (classes), Ariane 5 (an unhandled exception), punched-card storage (files), a
  container ship (packages and jars), Hubble's mirror (who tests the tests).
- JavaScript from zero, 5 to 10: the Patriot clock drift (0.1 in binary), upper and lower type cases (toUpperCase),
  Hollerith's tabulating machine (counting), Ford's assembly line (chaining methods), a NASA wind tunnel (testing).
- Go from zero, 5 to 11: an odometer rolling over (int8), a lottery machine (random map order), a signpost (pointers),
  travel adapters (interfaces), matryoshka dolls (wrapped errors), the Tacoma Narrows Bridge (testing).
- Owner, same evening: photos at the bottom of a long step were easy to miss (the Rosetta Stone). Each of the 33 new
  photos now sits near the top of its step (median line 8, at most 14), with its lead sentence: after the step's
  first paragraph, or at the very top when that paragraph introduces code, so no example is split from its output.
- Owner asked for an in-depth check: is each photo there because it belongs, or forced to the top? Every real photo
  in the five courses was read with the paragraph before and after it. Seven were moved to sit right after the text
  that sets up their idea: the odometer (Go 3, after the int8 wrap), Hubble (Java 17, after "a test that checks
  lateFee(0)"), the crash test dummy (Spring 25, after "a test that passes no matter what"), Ford's assembly line
  (JavaScript 11, after the walkthrough, no longer between code and its explanation), the lottery machine (Go 10, after
  "made it random on purpose"), the first web server (Spring 1, before "Let's look at one", which now leads into the
  request). The switchboard lead (Spring 10) now introduces the DispatcherServlet itself, and Go 13 uses one picture,
  the dolls, instead of envelopes and dolls.
- Second pass, same question per photo: does its step teach the photo's idea, or was a sentence written to tie it
  on? Two were tied on and moved to the step that teaches them: the Rosetta Stone (Python 7) from the indexing step
  to the top of "Go deeper: characters from every language" (Unicode), and the RAMAC disk (Spring 19) from the
  tables step to the Part 3 opener, "data that survives", after "survive restarts". Ada Lovelace's lead (Python 2)
  now says her program was written once and followed again for every number, which is what the step is about.
- The Mango lassi row in the product tables of Spring 19 and 21 was one space wider than its column; aligned.
- Every photo checked by eye before use (two were dropped: a "pigeonhole" that was a dessert in a teacup, and beanbags
  that did not explain the event loop). Downloads are paced to stay within Wikimedia's rate limits.

## 22 November: Go from zero rewrite, Part 4 "Capstone" (chapter 18); the course is complete

- 18. **Capstone: a depot report** (new, ids `capstone`, `depot_report`, `busiest_depot`): size up `deliveries.csv`
  with `wc` and `uniq -c`, a `Report` struct already designed, a plan in words, line numbers counted through blank
  lines, empty (not nil) results, and a fair tie rule over a randomly ordered map. Checked by `tests/pkg/report`.
- Go from zero: 18 chapters, 36 tasks, about 13.5 hours, in four parts, with three real photos (Ken Thompson and Dennis
  Ritchie, the Gopher, Rob Pike), 18 handwritten notes pages and four playing diagrams. All four language courses
  (Python, Java, JavaScript, Go) are now rewritten in the same curiosity-first style.

## 22 November: Go from zero rewrite, Part 3 "Real programs" (chapters 13 to 17)

- 13. **Errors in depth**: an error wrapped twice and still found by `errors.Is` (`%w` versus `%v`), sentinel errors,
  `defer` running last in, first out.
- 14. **Packages, modules and JSON** (new): `go.mod` and import paths, `json.Marshal` and `json.Unmarshal`, struct tags
  and `omitempty`, a lower-case field JSON cannot see, a wrong-shape JSON error. Tasks `save_manifest` and
  `load_manifest`, checked by `tests/pkg/manifest`.
- 15. **Files and a command-line program**: `bufio.Scanner`, flags must come before file names (run for real), errors
  to `os.Stderr`, and `go run` turning exit code 2 into 1. The summary tool moves from `cmd/summary` to
  `15-files-and-cli/summary` and imports its package by path.
- 16. **Goroutines and channels**: goroutines that vanish when `main` returns, a WaitGroup (900 ms becomes 300 ms),
  channels (new playing diagram `go-channels`), and a real "fatal error: concurrent map writes". Rob Pike's photo
  (Chlor, CC BY-SA 3.0).
- 17. **Testing with go test** (new): `fix_next_stop` red to green, and `test_eta`, a table-driven test that must
  catch three planted bugs (`tests/gotest/`, run with `go test` in a scratch module).
- Five notes pages (chapter 14's regenerated twice: the image model kept writing "Umarshal", so that line is now in
  words). Chapter and task ids kept; the old `cmd` folder is gone.

## 22 November: Go from zero rewrite, Part 2 "Working with data" (chapters 7 to 12)

- The shared root package `till.go` is split in two: `07-slices-and-errors/till.go` (package `till`: `Total`,
  `ParseAmount`) and `10-maps-and-structs/orders.go` (package `orders`: `CountByItem`, `Busiest`), each with its own
  check (`tests/pkg/till`, `tests/pkg/orders`); `cmd/main.go` is gone. Words, slice tools, wallet and shapes move to
  numbered folders, and pointers now come before methods and interfaces. Chapter and task ids kept.
- Each chapter opens with a real puzzle run in the lab image: where Go's exceptions are (errors are values), why
  `len("café")` is 5 (bytes and runes, UTF-8 drawn on a diner placemat), how changing one slice changes another (a
  shared array and `append`), why map order changes every run (random on purpose, so tie rules matter), why a function
  cannot make a parcel heavier (copies and pointers, a nil pointer panic), and how a bike and a van share one loop
  (implicit interfaces, `fmt.Stringer`).
- Six handwritten notes pages, checked letter by letter.

## 22 November: Go from zero rewrite, Part 1 "Starting out" (chapters 1 to 6)

- Same treatment as Python, Java and JavaScript: curiosity-first openings, a running project (**Parcel**, a small
  parcel tracker), a folder per chapter, every output captured in `labbox/go-basics:v1`, credited photos, a notes page
  on every recap, playing diagrams. Chapter and task ids kept.
- Demo programs sit beside each chapter's package with `//go:build ignore`, so `go run demo.go` runs them while the
  package, `go vet` and the checks never see them; each task package has a `run.go` that calls it.
  1. **Your first Go program** (new `hello-go`): why Go exists (a 45-minute C++ build), Ken Thompson and Dennis
     Ritchie (public domain), the Go Gopher (Renee French, CC BY 3.0), `go run`, a panic, and Go refusing an unused
     import and an unused variable (new playing diagram `go-runs-a-file`). Tasks `hello_parcel` and
     `fix_first_errors`, checked by `tests/gorun/check.go`, which runs the learner's programs.
  2. **Functions**: two results at once, the blank `_`, a missing argument caught before running, capital means
     public.
  3. **Numbers and text**: `0.1 + 0.2` is exactly 0.3 as a constant and not as variables, `7/2` is 3, an `int8`
     wrapping to -128, `int + string` refused.
  4. **Decisions**: a shipping price from the top down, `switch` that never falls through, `if 0` refused.
  5. **Loops**: one loop, `for`, in three shapes, and a trace.
  6. **Finding bugs** (new): a real Go panic read from the top (new diagram `go-panic-trace`), labelled prints, a
     tiny `ask.go` instead of a REPL. Tasks `fix_total_weight` and `fix_can_load` (planted bugs).

## 22 November: JavaScript from zero rewrite, Parts 3 and 4 (chapters 13 to 18); the course is complete

- Part 3 "Real programs": 13 **Errors** (one broken saved playlist does not stop the others, the quiet failures
  `NaN` and `undefined`, `?.`, `finally` running before the error leaves); 14 **Classes** (a private `#plays`, the
  lost-`this` surprise run for real, `extends` and `super`); 15 **Promises and async** ("which line prints first?"
  answered 1, 4, 3, 2 with a new playing diagram `js-event-loop`, a forgotten `await`, all at once with
  `Promise.all`); 16 **Files and a command-line program** (new, Ryan Dahl and Node.js, David Calhoun, CC BY 2.0,
  cropped; tasks `read_playlist` and `playlist_cli` with usage line, `File not found` and exit codes); 17 **Testing
  with node:test** (new: `fix_skip` red to green, and `test_duration`, where the learner's own tests must catch three
  planted bugs in `tests/testing/`, run with `node --test`).
- Part 4 "Capstone": 18 the monthly report (`18-capstone/`): size up the file with `wc` and `uniq -c`, a plan in
  words, line numbers kept through blank lines, the real output.
- JavaScript from zero: 18 chapters, 36 tasks, about 13 hours, in four parts, with three real photos, 18 handwritten
  notes pages and four playing diagrams. Chapter and task ids kept.

## 22 November: JavaScript from zero rewrite, Part 2 "Working with data" (chapters 7 to 12)

- Chapters 7 to 11 moved into numbered folders and rewritten curiosity-first around Mixtape, each opening with a
  real puzzle run in the lab image: why one emoji has length 2 (strings), why `[10, 9, 1].sort()` gives
  `[1, 10, 9]` (arrays), how a `const` object can change (objects), why `1` and `"1"` are the same object key and
  what Map and Set do (counting), and the famous `["10", "10", "10"].map(parseInt)` giving `[10, NaN, 2]` (array
  methods). Chapter and task ids kept.
- 12. **Modules and JSON** (new): `module.exports` and `require` (what is not exported stays private), CommonJS
  versus ES modules, `JSON.stringify` and `JSON.parse`, JSON's strict rules and a real parse error. Tasks
  `save_playlist` and `load_playlist`.
- Six handwritten notes pages, every one checked letter by letter.

## 22 November: JavaScript from zero rewrite, Part 1 "Starting out" (chapters 1 to 6)

- Same treatment as Python and Java (owner: "the same tone and style"): curiosity-first openings, a running project
  (**Mixtape**, a small playlist app), a folder per chapter, a runnable demo in every file, every output captured
  in `labbox/javascript-basics:v1`, credited photos, a handwritten notes page on every recap, playing diagrams.
  Chapter and task ids kept.
  1. **Your first JavaScript program** (new `hello-js`): `node file.js`, top to bottom, the history (Brendan Eich,
     CC BY-SA 3.0; Netscape Navigator 2, CC0, cropped), a TypeError while running versus a SyntaxError where nothing
     runs (new playing diagram `node-runs-a-file`). Tasks `hello_mixtape` and `fix_first_errors`.
  2. **Functions** (`01-first-program`): a missing argument gives `NaN min`, not an error; the missing-`return` bug.
  3. **Values and types**: five surprising lines run for real (`0.1 + 0.2`, `"5" + 5`, `typeof null`, `==`,
     `Infinity` and `NaN`), each explained.
  4. **Decisions**: a ticket price from the top down, truthy and falsy (an empty list is truthy), Pope Gregory XIII.
  5. **Loops**: a running total song by song, the counting `for` and `for...of`, a trace.
  6. **Finding bugs** (new): a real Node stack trace read from the top (new diagram `js-stack-trace`), labelled
     `console.log`, the Node REPL. Tasks `fix_total_length` and `fix_can_add` (planted bugs).
- Checks: `tests/check.js` runs `node` on the learner's file for chapter 1 (exact output, a kind message for each
  error kind). The JavaScript pictures browser test now allows concept steps without a picture (at most one, never
  repeated), as in the Python and Java rewrites.

## 22 November: Spring Boot gets handwritten notes on every recap and two real photos

- 31 handwritten notes pages (`frontend/public/lesson-images/spring/spring-00-notes.webp` to `spring-30-notes.webp`),
  one on each chapter's recap, made with the approved OpenAI key and checked letter by letter (chapter 25's page
  regenerated once: it showed code in curly quotes).
- Real photos (Wikimedia, credited): the NeXT computer at CERN that ran the first web server, with its "DO NOT POWER
  IT DOWN" label (chapter 1, Coolcaesar, CC BY-SA 3.0), and a CERN server room for "seeing a server you cannot see"
  (chapter 27, Florian Hirzinger, CC BY-SA 3.0).
- Photo alt texts must not contain curly braces: the block's attribute list ends at the first one.

## 22 November: the dashboard's Continue card shows a retro computer for coding labs

- The owner chose a split: labs where you write code (tracks `languages`, `frameworks` and the future `ai`) show a
  retro computer in the lab's colour; the rest (databases, DevOps, system design) keep the cassette. The rule is
  `labDeck(track)` in `brand.ts`, so new labs follow it by their track.
- The computer (`RetroComputer.tsx`, drawn in CSS, no image files) shows on its screen the lab and chapter, a
  chapter:step clock, the step's title, the first lines of its code (or the chapter as a comment) and a blinking
  `> continue`. The round play key and the screen are Continue, the power button opens the course page, and the
  bar is the place in the chapter. It scales to the dashboard's narrow column and stops moving for people who turn
  animations off.
- Owner, same day: the first version shrank the computer to 80% in the dashboard's narrow column (about 250px), which
  blurred the tilted screen text. Now a compact computer is drawn at its true size there (container query, gentler
  tilt, 9px screen text), never scaled, so it is as sharp as the sample.
- `/api/me/next` also returns the lab's `track`, the step's `step_title` and up to 5 lines of `code` (additive).
- Tests: a backend test for the new fields; the course browser test checks the computer for Go and the cassette
  for SQL; the next-step test clicks the new Continue key.

## 22 November: Java from zero rewrite, Part 4 "Capstone" (chapter 18); the course is complete

- 18. **Capstone**: Shelf's previous developer left a `Book` whose `equals` has no matching `hashCode` (a HashSet
  keeps two equal books) and a half-finished monthly report. Rewritten curiosity-first: a real run that shows the
  bug, the Long Room of Trinity College Dublin (Diliff, CC BY-SA 4.0) whose lettered bays explain "hashCode picks
  the bay, equals picks the book", a plan in words, the line-number trace, `wc` and `uniq -c` on the real file, and
  the real report output. Files moved to `18-capstone/` (with `expenses.csv`), packages dropped, mains added.
- Java from zero now has 18 chapters, 36 tasks and about 13.5 hours, in four parts (Starting out, Working with data,
  Real programs, Capstone), with 4 real photos plus reused ones, 18 handwritten notes pages and 5 playing diagrams.

## 22 November: finished chapters show a green tick; test data removed from the owner's account

- On a course page's skill map, a finished stop (every task of the chapter passed Check) is now filled green (the
  app's success colour) instead of the lab's own colour, so "done" reads the same on every lab. Visiting a chapter
  or answering its quizzes never ticks it; the current chapter keeps its pulsing "You are here" dot.
- The owner saw Java "methods" ticked without doing it: on 17 November a test run (before the 20 November fix that
  gave test accounts 8-digit ids and their own database) had checked as asha (id 1). With the owner's OK, its 13
  check runs (10 Python, 3 Java) and a solved `Greeter.java` it wrote into asha's Java workspace were deleted.
  asha's own Python runs are kept.

## 22 November: Java from zero rewrite, Part 3 "Real programs" (chapters 13 to 17)

- Exceptions, lambdas and streams, files and the command line moved into `13-exceptions` to `15-files-and-cli`
  without packages, rewritten curiosity-first with captured outputs: an exception's journey (new playing diagram
  `java-try-catch`), `Caused by:`, Java's unusual checked exceptions (a real "unreported exception" error),
  `finally` running before the exception leaves; one rule in three eras of Java (anonymous class, lambda, method
  reference), a stream pipeline over Shelf's books, lazy streams; `members.txt`, the `split(",", -1)` trap, `args`,
  `System.err` and exit codes. Summary now runs as `java -cp out Summary`.
- 16. **Packages, jar files and Maven** (new): Shelf becomes a Maven project. Tasks `package_catalog` (move Catalog
  into `shelf.catalog` so `mvn -o -q package` builds) and `runnable_jar` (fill in `<mainClass>`), checked by
  `SelfCheckMaven`.
- 17. **Testing with JUnit** (new): red to green (`fix_renewal`), then `test_late_fee`: the learner's own tests must
  pass on the real `lateFee` and catch three planted bugs (mutation testing), checked by `SelfCheckTesting` with
  JUnit's console launcher.
- The Java image (`labbox/java-basics:v1`) now carries an offline Maven repository (`warm/` pom: JUnit 5.11.4,
  the console launcher, the jar plugin); builds take 5 to 7 seconds at half a CPU. Check timeout 200 s.
- Pass messages for `loan_record` and `genre_enum` (chapter 12 said only "ok") and the four new tasks. Five
  handwritten notes pages.

## 22 November: Java from zero rewrite, Part 2 "Working with data" (chapters 7 to 12)

- Chapters 7 to 11 moved into numbered folders (`07-strings` to `11-collections`), `package` lines dropped, a
  `main` in every task file and new demo files, every output captured in `labbox/java-basics:v1`. Chapter and
  task ids kept.
  7. **Strings**: the `==` puzzle (`"riya" == new String("riya")` is false), immutability, the `split("\\s+")`
     empty-string trap, StringBuilder.
  8. **Arrays**: what `[I@4e50df2e` means, default values, two names for one array, copy before you change.
  9. **Classes and objects**: Shelf's first `Book` class, encapsulation, a playing `java-object-creation`
     diagram, records.
  10. **Interfaces and inheritance**: a `Lendable` book and DVD in one loop, polymorphism, compiling several
      files with `javac -d out *.java` and `java -cp out`, `extends` and `super`.
  11. **Lists, maps and sets**: ArrayList, `List<Integer>` and the `remove(1)` trap, sort a copy, HashMap and
      HashSet with the phone-book picture.
  12. **Generics, records and enums** (new): a generic record, compact constructors, enums with switch
      expressions, a sealed family with pattern-matching switch (Java 21). Tasks `loan_record` and `genre_enum`,
      checked by `tests/pkg/modern/CheckModern.java`.
- Six handwritten notes pages (chapter 7's regenerated once: the first showed `\s+` with one backslash).
- The picture-code validator test now uses chapter 11.

## 22 November: Java from zero rewrite, Part 1 "Starting out" (chapters 1 to 6)

- The owner approved the Java syllabus (18 chapters, running project **Shelf**, a small library app) and the
  OpenAI key for Java's handwritten notes. Same treatment as Python: curiosity-first voice, a folder per chapter,
  every output captured in `labbox/java-basics:v1`, photos, notes and playing diagrams.
- Design: no `package` lines until the packages chapter; every chapter file has a small `main`, run with
  `java File.java`; `run_checks.sh` maps chapter, folder, check folder, check class and tasks; a check named
  `Self...` compiles the learner's files itself (chapter 1 checks Hello.java and the broken FixMe.java apart).
  1. **Your first Java program** (new): the terminal, a class and main, why Java needs `;`, compile errors (Java
     shows the first one, then the next) versus exceptions, `javac` and the class file's real `ca fe ba be`
     bytes. Photos: Duke (BSD), James Gosling (Peter Campbell, CC BY-SA 4.0), a California oak for Java's first
     name (Daniel Lu, CC BY-SA 4.0), the VT100. Tasks `hello_shelf`, `fix_first_errors`.
  2. **Methods** (`01-methods`): typed methods, a playing call (`java-method-call`), Java's compile-time type
     errors (real messages), void vs return, the shortest-word trace.
  3. **Variables and types** (`02-variables-and-types`): types table, integer division and casts, int overflow
     (2147483647 + 1 = -2147483648), money in paise, `"5" + 5 + 5` vs `5 + 5 + "5"`, String.format.
  4. **Making decisions** (`03-decisions`): booleans, if / else if, `=` in a condition does not compile, switch
     expressions, the ternary; Pope Gregory XIII.
  5. **Loops** (`04-loops`): for-each, the counting for, a running total trace, a real
     ArrayIndexOutOfBoundsException, characters of a string.
  6. **Finding bugs** (new): a Java stack trace read from the top (`java-stack-trace` diagram; Python reads its
     traceback the other way), println with labels, a real jshell session. Tasks `fix_total_fines`,
     `fix_can_borrow`. The 1947 moth.
- New playing diagrams `java-runs-a-file`, `java-method-call`, `java-stack-trace`; six handwritten notes pages
  (the doodle is never a cup or a drink, so nothing looks like chai). Tests follow the new chapter 1.

## 22 November: no chai or tea examples anywhere

- The owner: "dont use masala chai and chai related stuff as an example. in any of the lesson, task, lab or
  anywhere." Saved as a standing rule. Chai means tea, so tea went too.
- **Spring Boot:** the Shop API's "Masala tea" (SKU TEA-1) is now "Mango lassi" (SKU LAS-1) in data, starters,
  solutions, checks, lessons and diagrams; same price and the same alphabetical place, so every quoted output and
  sort order holds. Chapter 20's brand-new product, which already used LAS-1, became "Rose milk" (ROS-1).
- **Java, JavaScript, Go, Redis:** juice, toast, pen, red cup, a veg sandwich and lemon rice instead; map print
  orders taken from real Java (HashMap) and Go runs. Shared pictures redrawn: the recipe card says "Lemon rice",
  the beads spell "red cup", the form card and cart say juice, and the string-equals diagram shows "riya" like
  its chapter.
- CONTENT_STANDARD and the v2 spec's example world updated. Every changed lab passes validate --strict and
  test-lab (starter fails every task, solution passes every task).

## 22 November: four more real photos in Python from zero; the snake opens chapter 1

- Also: no chai examples anywhere (owner: "dont use masala chai and chai related stuff as an example ... anywhere").
  Python from zero now uses juice, rice, bread, books, pen, pav, toast, a paneer roll, a veg sandwich and दाल (dal)
  instead, keeping every output, length and sort order the same (books still ties with lunch and sorts first). The
  handwritten notes for chapters 7 to 9 were redrawn, and the object-creation animation uses a pen. Every example
  file was rerun in the lab image and each printed line checked against its lesson.

- The owner loved the images, asked for at least three more where they genuinely fit, and the snake on the first
  page instead of next to Guido. Added (Wikimedia Commons, credited): a DEC VT100 terminal from 1978 in "Meet the
  terminal" (Jason Scott, CC BY 2.0), Pope Gregory XIII with the leap-year question (public domain; his 1582
  reform made the 100 and 400 rule), John Venn's stained-glass window after the set maths (CC BY-SA 2.5), and an
  opened hard drive in "Where does your data go?" (Evan-Amos, CC BY-SA 3.0). The ball python moved to chapter 1's
  first step. Python from zero now has 7 real photos and 19 pages of handwritten notes.

## 22 November: Python from zero rewrite, Part 4 "Capstone" (chapter 19); the course is complete

- **19. Capstone: a monthly report** (`13-capstone`), in its own folder: fix inherited code first (a real
  KeyError and a None from `.sort()`, three bugs in all), then build `monthly_report` from a written contract
  (a table of every key), with a plan that maps each step to the chapter that taught it, and a "where to go
  from here" Go deeper. Nothing is left at the top of the workspace: every chapter has its own folder.
- **Python from zero is complete:** 19 chapters in four parts (Starting out, Working with data, Real programs,
  Capstone), 39 tasks, about 13.5 hours (815 minutes), Pocket as the running project, curiosity-first voice,
  7 playing diagrams, 3 real photos and 19 pages of handwritten notes. Every chapter id and task id from before
  is kept, so learners' progress carries over.

## 22 November: Python from zero rewrite, Part 3 "Real programs" (chapters 13 to 18)

- Overnight, at the owner's request. Each chapter in its own folder, every output captured in the lab image:
  13. **Errors** (`10-errors`): a table of every exception met so far, raise with helpful messages, catching
      only what you expect, and a new playing diagram (`try-except-flow`).
  14. **Files** (`11-files`): modes table, Pocket's diary (`diary.py`, "w" vs "a" seen by running it twice),
      why CSV is never split by hand, csv.DictReader on a real month with two broken rows.
  15. **Classes and objects** (new, tasks `expense_class`, `pocket_class`): blueprint and objects, `self`, a
      playing diagram of object creation (`object-creation`), and the class-body shared list trap (the check
      catches it).
  16. **Modules, packages and pip** (new, tasks `money_module`, `median_spend`): refactoring Pocket into
      `money.py`, how Python finds a module (`import-search` diagram), the standard library table, venv and pip
      with the real proof that a venv is private.
  17. **Testing your code** (new, tasks `first_tests`, `edge_tests`): pytest, a real failure report, boundaries.
      The learner's own tests must pass on correct code and fail on planted bugs (no thousands separator,
      one-decimal rounding, `>=`, off by one rupee).
  18. **Running a program** (`12-running-a-program`): sys.argv, argparse and its free help page, exit codes,
      stderr, and `if __name__ == "__main__":`; ships with a finished `file_tools.py` so it never depends on
      chapter 14.
- Checks for the new chapters in `checks.py` (wrong answers run: class-body list, int() truncation in to_paise,
  weak tests, a test expecting the wrong answer, median without statistics); `check.py` reads chapters 13, 14 and
  18 from their folders.

## 22 November: Python from zero rewrite, Part 2 "Working with data" (chapters 7 to 12)

- Overnight, at the owner's request ("finish all parts of python ... do not ask"). Chapters 7 to 12 rewritten in
  the curiosity-first voice, every output captured in the lab image, each in its own folder with a runnable
  example file:
  7. **Strings** (`05-strings`): a table of positions from both ends, methods tidying a real receipt line,
     immutability, split with and without an argument, join, Hindi text in Unicode.
  8. **Lists** (`06-lists`): a cart, the list toolbox table, building a new list, sort vs sorted, two names for
     one list (`same_list.py`, the shared-list diagram).
  9. **Dictionaries** (`07-dictionaries`): a price list with a real KeyError, get / in / items, the counting
     pattern traced with Play, records as dictionaries.
  10. **Tuples and sets** (`08-tuples-and-sets`): unpacking, returning two answers, set maths on shop visitors,
      and a timing table (1,000 lookups: 0.015 ms in a set, 421 ms in a list).
  11. **Sorting and comprehensions** (new, tasks `large_expenses`, `by_amount`): key=, lambda, two-rule sorts,
      list comprehensions with a new playing diagram (`comprehension-steps`).
  12. **Functions in depth** (`09-functions-in-depth`): defaults, named and name-only arguments, *args, scope,
      and the mutable default trap.
- Task ids and behaviour kept; task order follows the lessons. Each recap ends with its handwritten notes.
- Checks: chapter 11 in `checks.py` (with a tie case, since a stable sort hid the missing tie rule); `check.py`
  reads the other moved chapters from their folders. Tests follow the new layout (top-up, diagram themes).

## 22 November: real photos and handwritten notes in lessons

- The owner: "why can't we show a photo of a snake, a photo of Guido van Rossum", then "hand written notes ai
  generated". New lesson block `:::photo{src alt credit license source}` (or `ai="true"`), drawn as a figure with
  a caption and a credit line (`LessonMarkdown.tsx`, `styles.css`). Images live in
  `frontend/public/lesson-images/<course>/` as WebP (55 to 160 KB).
- Python from zero gets three freely licensed Wikimedia Commons photos: Guido van Rossum (Daniel Stroud, CC BY-SA
  4.0) in "The story of Python", a ball python (Holger Krisp, CC BY 3.0) in the fun fact, and the 1947 Harvard
  Mark II logbook page with the moth (public domain) in chapter 6. Each chapter's recap ends with an AI-drawn page
  of handwritten notes (19 pages, OpenAI image model, medium quality, owner-approved for Python lessons; every page
  checked letter by letter, including the 15 zeros of 0.30000000000000004).
- The validator checks photos: a file in frontend/public, alt text, and credit, licence and source (or
  `ai="true"`); never on task or quick-check steps; one per step, two on a history step. CONTENT_STANDARD's old
  "no photos" rule is replaced. Tests: `test_photos_need_a_file_alt_text_and_a_credit`, and `lab.spec.ts` checks
  Guido's photo loads with its credit.

## 22 November: no line legend above skill maps; full test runs on Postgres and Redis

- The owner: remove the line legend ("Starting out 1/6 ...") above the skill map everywhere. `MetroLegend`
  and its styles are gone; each part still names its line on the map itself.
- The owner: test completely on Postgres and Redis, as in production. Full runs now use
  `LABBOX_TEST_DATABASE_URL` and `LABBOX_TEST_REDIS_URL`; the SQLite and in-memory pass runs only when a change
  touches the database, migrations or the no-Redis fallbacks (AGENTS.md "Running and testing").

## 22 November: Python from zero rewrite, Part 1 "Starting out" (chapters 1 to 6)

- The owner: rewrite the language courses, starting with Python, "always with curiosity, like teaching a child
  one on one. interesting, animated, cool images, tasks". New CONTENT_STANDARD section "Curiosity first".
- **Part 1, Starting out**, as full lessons with every output captured from the lab image, a running project
  (**Pocket**, a money tracker) and a folder per chapter:
  1. **Your first program** (new): what a program is, the terminal (`pwd`, `ls`, `cd`), `print`, strings vs
     calculations, Python's story, a playing timeline of how Python runs a file, a SyntaxError and a NameError
     read from the bottom. Tasks `hello_pocket`, `fix_first_errors` (new).
  2. **Your first functions** (id `01-functions`, moved from 1st): def, parameters, arguments, return, a
     playing timeline of one call, print vs return seen with real output, `%` and `==`. Tasks unchanged.
  3. **Numbers and text** (id `02-numbers-and-text`): variables, int and float, the five ways to divide,
     `0.1 + 0.2`, conversions, f-string formats. `average` no longer takes an empty list (chapter 6 uses that
     crash to teach tracebacks).
  4. **Making decisions** (`03-decisions`): booleans, comparisons (text vs numbers), if/elif/else, and/or/not.
  5. **Loops** (`04-loops`): for, a running total traced with Play, range and positions from 0, early return.
  6. **Finding bugs** (new): errors vs bugs, a three-frame traceback played bottom-up, print and `f"{x=}"`
     debugging, a real pdb session. Tasks `fix_daily_total` (off by one), `fix_over_budget` (`<=` vs `<`) (new).
- Chapter ids and task ids are kept; chapters 1 to 6 moved into numbered folders (`01-first-program/` ...
  `06-finding-bugs/`), chapters 7 to 15 keep their files at the top until their part is rewritten. New
  optional `folder:` on a chapter (the tutor reads only that folder). Type hints left out of the beginner
  starters (introduced in chapter 2's Go deeper).
- New playing diagrams: `python-runs-a-file`, `function-call`, `traceback-bottom-up`.
- New checks in `tests/checks.py` (per chapter, kind failure messages; print-instead-of-return is named);
  `check.py` keeps the chapters not rewritten yet.
- A chapter now opens on its **first task's** file (`focus.py`), not whichever TODO file sorts first.
- Tests: backend and browser tests follow the new chapter 1 (lab, engagement, editor, text size, top-up,
  admin, focus, tutor folder); new `test_a_chapter_with_its_own_folder_name_sends_that_folder`.

## 22 November: the Spring Boot voice, written down

- The owner asked whether the way Spring Boot lessons and tasks are written was recorded. The rules were
  (CONTENT_STANDARD sections 0, 3 to 5); the voice itself was not. New "The voice, by example" in section 0:
  real excerpts from chapter 14 showing how a story opens, how a concept states its rule, how try and task
  steps read, task titles, the hint ladder, starter TODOs, check failure and pass messages, quick checks, the
  recap, and the everyday world (Rs, paise, the Shop API).

## 22 November: the dashboard's progress card is gone (it lives in the profile panel)

- The owner first asked for the level, streak and today's XP card on the right, stacked (built in 5d6c72b), then
  to remove it, since the profile panel shows the same: level and XP to the next, the streak and best, and today's
  streak goal. The daily drill has the full width again; the card's styles are removed.

## 22 November: Focus only where it works; three and xyflow removed

- The owner: "Exit focus" did nothing in VS Code. Focus hides LabBox's own file tree, which only the Lite editor has,
  so the button now shows only in Lite (VS Code hides its own sidebar with Ctrl+B). `editor.spec.ts` checks both.
- `three`, `@types/three` and `@xyflow/react` uninstalled (no longer used after the Skill maps section went).

## 22 November: the skill map lives on the course page; the Skill maps section is gone

- The owner: a "Skill map" title on the course page, under "What you will learn", and no separate Skill maps
  section now that each lab's map is on its course page. Removed: the dashboard's "Skill maps" button, the `/skills`
  landing page, the per-lab map pages and the track maps (`SkillsPage`, `LabMapPage`, `TrackPage`) with their styles
  and the old react-flow skill-node styles. Old links still land: `/skills/<lab>` opens the course page,
  `/skills` and `/tracks/<track>` the dashboard. The deck's ■ key opens the course page.
- Kept: the track data (`tracks/*.yaml`) and `GET /api/tracks/<track>/skills` (routes are only added, never removed),
  so a track view can come back. `@xyflow/react` and `three` are no longer used by the app.
- Tests: `roadmap.spec.ts` and `skillmaps.spec.ts` removed; their checks (parts as lines, subtopic to lesson step)
  moved into `course.spec.ts` with the redirects; `engagement.spec.ts` sees chapter 1 light up on the course page.

## 22 November: a profile panel; Exit instead of Log out

- The owner: level, streak and stars go in a profile section, and an Exit button replaces "Log out". Every top bar
  now shows one profile button (the learner's initial in a ring that fills towards the next level) instead of the
  badges. It opens a panel: name and level, XP to the next level, the streak (and best), total stars (XP), today's
  streak goal and the streak freeze, and Exit (signs out). `ProfileMenu.tsx` replaces `StatsBadges.tsx`.
- Tests: new `profile.spec.ts`; `engagement.spec.ts` reads the streak, XP and level from the panel.

## 22 November: a page for every lab; the deck in the lab's colour

- The owner: a lab card should open a page for that lab, then the lab. New `/courses/<lab>` (`CoursePage.tsx`):
  the cover with the lab's colour, track and level, subtitle, progress, one button into the lab ("Continue:
  Chapter N" or "Start: Chapter N", with the chapter and step), the description, a few facts,
  and the chapters as a metro map (the skill map's component: a line per course part, "You are here" on the chapter
  the learner was last in, every subtopic a link to its lesson step). The owner found a plain chapter list too
  dense; `labLines` and `MetroLegend` now live in `MetroMap.tsx` and the skill map page uses them too. Lab cards on the dashboard
  and on the home page (signed in) open it; Continue, chapter lists and skill maps still go straight into the lab.
- The dashboard's tape deck takes the colour of the lab it continues (Go cyan, Spring green, Redis red...): the
  edge bands, the initial, the play key, the LED, the cassette and the rail's current chapter. Text on bright tones
  turns dark. Lab colours moved to `brand.ts` (`LAB_TONES`, `labTone`, `mix`, `inkOn`) and the home page uses them.
- `GET /api/me/next?lab=<id>` (new query, additive): where to pick up in that lab, or its first chapter; 404 for an
  unknown lab. The course page uses it.
- Tests: `test_next_starts_new_learners_and_continues_the_rest` covers `?lab=`; new browser test `course.spec.ts`
  (the deck in Go's colour, card to course page, Continue lands on the saved step, a chapter row opens its chapter).

## 22 November: Continue follows the last chapter opened

- The dashboard's Continue card picked the lab where the learner last moved a step, so opening a lab
  and reading without pressing Next never counted (Redis opened last, Spring Boot still shown).
  Opening a chapter now marks it as the latest (`progress.opened`), and Continue follows it.
- Test: `test_next_starts_new_learners_and_continues_the_rest` opens a chapter without moving and
  expects Continue to point there.

## Dashboard: the Continue card as a tape deck; no course times on lab cards

- The owner: lab cards no longer show a course's total time (a long one can feel overwhelming); the dashboard
  and home page tiles show track and level only. Chapter minutes on skill maps stay.
- The next-step card is styled after a red-and-silver cassette design the owner shared: a dark dotted panel
  with red and grey bands on its edge, a bold title with a red italic initial, and a silver tape deck playing a
  red cassette. The tape winds from the left reel to the right as the chapter goes on, and the reels turn while
  you are mid-chapter. The keys work: previous chapter, the lab's skill map, Continue (the red play key) and next
  chapter. It stays a dark device in the light theme. The chapter rail's current chapter is red to match.
- The dashboard loads the next lab once and shares it between the card and the rail.


## Skill maps: every subtopic opens its lesson step; more depth

- The owner: subtopics a little bigger, more 3D, and every subtopic clickable. Each subtopic on a station card is
  now a link to that exact lesson step (`/labs/<lab>?chapter=<id>&step=<n>`); the card title opens the chapter,
  and "+N more" shows the rest of the subtopics in place (the map makes room). On track maps, each topic's
  chapters are links into the lab.
- The lab page reads `?step=` once on arrival (with `?chapter=`); jumping back keeps later steps open.
- The lab API's chapter `topics` are now `{title, step}` (the concept step and its index).
- More depth: thicker tube tracks with a deeper shadow, bigger glossy stations, cards as raised tiles with a
  coloured edge underneath that lift on hover; subtopics at 13.5 px, titles at 15.5 px.


## Skill maps: a metro map

- The owner found the plain timeline "not cool" and chose a **metro map** from four directions, then asked for
  more room, the subtopics of every chapter, and a little 3D. Every course part is its own coloured line and
  every chapter a station; the route snakes down the page, up to four roomy stations a row, turning down at each
  end with rounded corners outside the cards; where one part ends the colour blends into the next line's. Line
  names sit at each line's first station, and a legend on top shows each line's progress ("Foundations 5/10").
- **Every station has a card with the chapter's subtopics** (its concept steps, up to four, then "+N more"),
  tasks done and minutes. Every card opens its chapter.
- **A light 3D finish:** tube-like tracks with a highlight and a soft shadow, glossy sphere stations, cards with
  depth that tilt towards the mouse (off with reduced motion).
- The route you have travelled is solid, the rest is faded; done stations are filled with a tick, the station you
  are at is bigger, pulses, and says "You are here". Phones get each line as a vertical list of the same cards.
- Track maps are metro maps too, in stages of six topics; each card lists the topic's chapters, and choosing a
  station shows them below the map with Open links.
- **Course parts in `lab.yaml`:** a chapter can say `part: <name>` (optional, additive); it starts that part, and
  the chapters after it stay in it. The lab API returns `part` and `topics` (the concept step titles, cached per
  file) on every chapter. The Spring course has four parts: Foundations, REST APIs, Data, Production basics.
  Labs without parts get one line.
- The dashboard's progress card no longer lists skill map counts (owner); it shows level, streak and today's XP.
- The plain timeline (Roadmap) is removed. New test: `test_chapters_carry_their_course_part`.

## Skill maps: a plain, simple roadmap (no 3D)

- The owner: "ignore 3D, a plain cool roadmap, simple". Every lab map (`/skills/<lab>`) and track map
  (`/tracks/<track>`) is now one vertical timeline: a numbered dot per chapter (or topic) on a single line, and a
  card beside each, alternating left and right on wide screens, one column on phones.
- Done steps are green with a tick and the line behind them turns green; the step you are on pulses gently and
  says "You are here" (the page scrolls to it); every card opens its chapter. Track cards list the lab chapters
  that teach the topic, each a link into the lab.
- A short header on top: a progress ring, the title, "N of M chapters done, next: ...", and Continue.
- The Skill maps landing page is plain too (no synthwave hero); cards say "N chapters".
- The 3D worlds (IslandWorld) are removed; three.js is no longer imported, so `three` and `@types/three` can be
  uninstalled from `frontend/package.json` when convenient.

## Skill maps: sky islands instead of the neon road

- The owner found the neon road's 3D design rubbish and asked for the best 3D roadmap I can make, free, not GTA.
  The world is now **sky islands**: every chapter (or topic) is a floating island with a wavy grass cap, a sandy lip
  and a rocky underside, trees, rocks and soft shadows; glowing stepping stones climb from island to island
  through drifting clouds. Finished islands fly a waving flag; the island you are on has a spinning crystal.
- **Bit**, our own character (red hoodie, yellow scarf, blue backpack, big eyes), hops stone by stone to the
  island you choose; the camera swoops in on arrival and follows. Labels are real HTML (crisp, clickable) that fade
  with distance. Dawn colours in the light theme, twilight with stars and glow in the dark one.
- The neon road (NeonWorld) is removed; lab and track maps both use the islands.

## Skill maps: a separate section, and a neon 3D road for every lab

- The owner: "keep a skill map section entirely separate, for each lab", in an open-world game style, "when a
  new learner sees it says wow". An original world (no game's characters, logo or art), drawn in code with
  three.js: a coastal highway at sunset with a striped sun on the horizon, the sea, palm trees, a lit city, stars,
  neon pink and teal lane lines and bloom glow; by day in the light theme.
- **Every lab has its own road** (`/skills/<lab>`): one roadside sign per chapter (number, title, state), a glow
  ring on the road, and a light beam at "you are here". Our own rider on a scooter (helmet, LabBox backpack) waits
  at your first unfinished chapter; choosing a stop (sign or list) rides there with a chase camera; the panel shows
  the chapter with "Enter chapter". An intro swoop on arrival; no motion for people who turn motion off.
- **The section** (`/skills`, "Skill maps" in the dashboard's top bar): a synthwave banner and a card per lab and
  per track. Track maps use the same world (topics as stops). The earlier tile board is removed.
- Tests: a browser test from the landing page to a lab's road and into a chapter.

## Skill maps become a 3D roadmap, and every topic opens its lab

- The owner: "turn these into a real 3D fun roadmap, and every topic connects to the actual lab and can open it,
  for all labs". With three.js (installed by the owner), every skill map is a 3D journey: topics in learning
  order stand as raised tiles along a winding road that leads away from the camera; the camera starts low behind
  the topic you are on. Done tiles are green (and the road behind them), the ones you can start float and pulse,
  locked ones are grey, coming-soon ones see-through. Drag to turn, scroll to zoom, right-drag to pan, Reset view.
- A side panel lists every topic; choosing one (on the board or in the list) flies the camera there and shows its
  chapters ("Spring Boot · Ch 21"), each with an Open button into the lab at that chapter, plus "Best after" for
  unfinished prerequisites (locked topics can still be opened).
- Phones and browsers without WebGL get the list alone. three.js loads only on skill-map pages. Colours follow the
  light and dark themes; no motion for people who turn motion off.
- The skill-map API adds each chapter's lab title and its number as the lab's menu shows it (additive).
- Tests: the skill-map API's new fields, and a browser test that chooses a topic and opens its chapter.

## Dashboard: the next step in a left sidebar on wide screens

- Then, at the owner's request ("long vertical bar, cool aesthetic"): the sidebar is a full-height rail. Under the
  Continue card, every chapter of the lab you are in, as a vertical timeline (done ticked, the current one
  glowing, upcoming faint), each opening its chapter; it scrolls inside itself and the current chapter is in view.

- The owner: "place this vertically on left side, there is ample of space". On screens 1200 px and wider, the
  "Continue where you left off" (or "Start here") card is a vertical card in a sticky left sidebar, next to the
  progress, drill and labs; on narrower screens it stays on top, as before.

## The Spring Boot course is the template for every course

- The owner: "this one is much better. save it as template for rest". CONTENT_STANDARD.md gets a new section 0:
  the Spring Boot course is the template, with the ten things that make it so (self-sufficient, a teacher's voice,
  full lessons, parts and a running project, the code following the lesson, only real captured output, see it /
  break it / fix it, playing timelines, two real tasks per chapter, honest depth). AGENTS.md points to it.

## Spring Boot rewrite, Parts 3 and 4: data and production basics (chapters 19 to 30); the course is complete

- **Part 3, Data**, rewritten as full lessons with every SQL statement captured from the real projects: 19 a real
  database (tables, SQL, ORM/JPA/Hibernate, JDBC URLs, the connection pool, entities, the SQL Hibernate writes,
  constraints), 20 derived queries (the naming language, existsBy and 409), 21 relationships (foreign keys, owning
  side, lazy loading, the N+1 problem seen as 6 queries, JOIN FETCH), 22 paging and JPQL, 23 transactions (the
  half-done order seen with curl, checked exceptions, the proxy rule; a new HTTP endpoint to watch it), 24 Flyway.
- **Part 4, Production basics**: 25 testing controllers (slices, mocks, MockMvc, reading a failure), 26 testing
  queries (what a mock cannot test, data that proves something, containsExactly), 27 logs and Actuator (a new
  endpoint to trigger the warning), 28 security (the locked default, Basic, the filter chain, CSRF, roles), 29
  calling services (a fake supplier the learner runs in its own terminal: 404, 3 s delays and a 1 s timeout seen
  for real), 30 the capstone checkout, written as a contract first.
- Starter TODOs in chapters 19 and 21 now describe the goal instead of dictating the annotations.
- The course: 31 chapters (0 to 30), 61 tasks, every starter fails and every solution passes.

## Spring Boot rewrite, Part 2: REST APIs (chapters 10 to 18), as full lessons

- **Tutor fix:** in a lab where each chapter has its own folder, the tutor now sees only that chapter's files.
  Before, files were read alphabetically up to a size limit, so a learner stuck in chapter 20 got a tutor that saw
  chapters 0 to 2, and every question used the maximum context (20 tutor questions then ran past the daily token
  budget). A new test covers it.

- **10 How Spring handles a request** (new): the journey of one request (a playing timeline: Tomcat thread,
  DispatcherServlet, handler mapping, arguments, your method, message converter), Spring's own TRACE log
  read line by line, 404 vs 405 vs 406 and content negotiation, a class-level `/api/v1` prefix, one path
  with two methods, one controller object shared by every thread.
- Rewritten in a teacher's voice, every output captured from the real projects: **11** reading the request
  (path variables, query parameters, headers, conversion and its 400s, Optional and orElseThrow, Comparator),
  **12** request bodies and DTOs (the cost-price leak, 415 and 400, mass assignment, output DTOs, money in
  paise), **13** status codes and ResponseEntity, **14** layers (why, a fat controller made thin, data
  questions vs business questions), **16** validation (the annotations, null and @Valid traps, the real
  MethodArgumentNotValidException, regular expressions), **17** errors (500 for a missing product,
  @RestControllerAdvice, ProblemDetail and RFC 9457, field errors, safe 500s).
- **15 Updating and deleting** (new): PUT replaces everything (a missing field becomes 0), PATCH with nullable
  fields changes only what is sent, idempotency, soft deletes, the full REST picture.
- **18 Filters and interceptors** (new): where each sits in the journey, OncePerRequestFilter and the chain,
  a request id (X-Request-Id, UUID or the caller's), HandlerInterceptor and HandlerMethod, WebMvcConfigurer
  with path patterns.

## Spring Boot rewrite, Part 1: the foundations (chapters 0 to 9), as full lessons

- The owner: "rewrite the whole Spring lab, more elaborative, more human-like, self-sufficient: no need of
  videos, Google or ChatGPT after it". The course becomes **31 chapters in four parts**, numbered from 0, and
  every chapter is rewritten as a full lesson in a teacher's voice (why before how, every line read, what
  you will see on screen, the mistakes beginners make), with each step opening its own file.
- **Part 1, Foundations:** 0 What Spring Boot is (history), **1 How the web works** (new: HTTP, URLs, status
  codes, methods, REST, JSON, curl against a running menu API; the learner records the real answers),
  **2 Maven and the pom.xml** (new: coordinates, the parent, starters and transitive dependencies, folders,
  phases, the fat jar; add the Actuator, name the project), 3 First endpoints, 4 How the app starts (real
  log read line by line, the scanning rule), 5 Beans and the application context, **6 Dependency
  injection in depth** (new: interfaces, Spring's real "2 beans found" error, @Primary, @Qualifier, lists),
  7 Configuration and profiles (YAML, typed settings, sources and their order, profiles), **8 How
  auto-configuration works** (new: @Bean, a small library with its own auto-configuration, conditions, the
  --debug report), **9 The life of a bean** (new: @PostConstruct, scopes, the shared-receipt bug,
  @PreDestroy). Every quoted log and curl output was captured from the real projects.
- Chapters, folders and checks renamed to their new numbers; task ids kept. Each chapter is its own Maven
  project (the root project is split into chapters 0 and 3). A playing timeline for the bean lifecycle.
- **Terminal tabs:** + opens up to three terminals (one runs the server, one sends requests); x closes one.
- Courses with a chapter 0 number chapters by their ids, in the menu and on the dashboard.
- Tests: chapter numbering by id, terminal tabs (browser), and the updated Spring browser tests.

## Calmer playing diagrams, and lessons without a word limit

- The owner wanted the playing diagram "cool, minimal, soothing". It is now a quiet vertical timeline:
  a thin rail with one small circle per step and the words beside it; the rail fills as the steps
  run, a soft band slides to the step being run, finished steps get a tick, the rest stay faint, and
  the current circle breathes gently (no motion when motion is turned off).
- "Make every lesson an actual lesson": the 120-word limit on concept and example steps is gone
  (validator, CONTENT_STANDARD, README), and a chapter may take up to 60 minutes.

## Hand-drawn diagrams: calmer to read

- The owner found the handwriting font and the hatched fills tiring. Diagrams keep the hand-drawn
  outlines and arrows, but boxes get plain light fills and labels use the normal text font; the
  Caveat font is no longer loaded.

## A hand-drawn diagram that plays: the sample (Excalidraw look)

- The owner asked for diagrams that look drawn in Excalidraw or eraser.io, and for the six steps of
  `SpringApplication.run` to animate. `roughjs` (MIT, installed by the owner) draws wobbly outlines,
  hachure fills and arrows; labels are handwritten (Caveat), code stays in the code font; CSS colours
  follow the light and dark themes (`lesson/Sketch.tsx`).
- `SketchSteps`: Play lights the steps one at a time (1.6 s each), a dot moves to the current step, a
  line under the drawing says what Spring is doing; Back, Next and Restart step by hand. No motion
  for people who turn motion off. Spring Boot chapter 2's start-up diagram is the first one.
- Browser test `sketch.spec.ts`: Next, Back and Play light the right steps, without page errors.

## The lesson and the code stay in sync: each step opens its own file

- The owner, reading Spring Boot as a beginner would: the lesson explained `SpringApplication.run` while
  the editor showed another file. Now a lesson step can name its file and lines
  (`file="..." line="10"` or `line="9-12"`); reaching the step opens that file in VS Code or the Lite
  editor and selects those lines. A task step opens its own task's TODO, not the chapter's first one.
- The focus route takes an optional step number (an addition; old calls work as before). It only opens
  paths named in the lab's own content, checked to stay inside the workspace or the starter.
- The VS Code extension (`tools/vscode-defaults`) selects the step's lines; `scripts/openvscode.sh`
  reinstalls it. The validator fails a step whose file is not in `starter/` or whose line is past the end.
- `CONTENT_STANDARD.md`: "talk to one learner" and "the lesson and the code stay in sync".
- Spring Boot chapter 2 names its files on every step about code. A content test now allows up to 14
  concept or example steps and 30 steps a chapter, for the smaller steps of the new voice.
- Tests: step attributes and bad paths, task steps open their own TODO, the focus route by step, and a
  browser test that moving through chapter 2 opens and highlights the right files.
- Moving quickly through steps switches files fast, and Monaco then rejects one of its own timers
  ("Canceled"); the page now drops that one harmless error (`main.tsx`).

## The light and dark switch on every page

- The dashboard, skill maps, onboarding and admin pages get the same light and dark button as the lab
  page (`components/ThemeButton.tsx`); before, the owner could only switch themes inside a lab.

## Lesson tables render as tables (remark-gfm)

- The owner installed `remark-gfm`; lessons now render markdown tables as real tables (bordered, a
  header row, scroll sideways on narrow screens). Single tildes stay plain text. "Watch it run" traces
  read GFM tables too and work as before.
- The diagram-themes browser test now waits for the phone reading mode to settle before it measures.

## Dark theme: the login page's charcoal with a very faint grid

- In the dark theme, every app page now sits on the login page's charcoal (`#111512`) with a very faint
  32 px grid (`#151916` lines), as the owner asked. The light theme is unchanged.

## Spring Boot, block D: chapters 17 to 22; the course is complete

- **Chapter 17, testing the web layer:** `@WebMvcTest`, `MockMvc`, `@MockitoBean`. **Chapter 18, testing the
  data layer:** `@DataJpaTest` against a real in-memory database, `containsExactly`. In both, the learner
  writes the tests: the check runs them on the correct code (they must pass) and on a planted bug (they
  must fail), with a clear message for each case (`tests/<chapter>/own.env`, `tests/<chapter>/bug/`).
- **Chapter 19:** SLF4J logging and levels, Actuator health and info. **Chapter 20:** Spring Security, a
  `SecurityFilterChain`, HTTP Basic, 401 versus 403, roles, CSRF. **Chapter 21:** `RestClient`, a 404 that
  means "not stocked", a 1 second read timeout and 503 (the check runs a fake supplier, with a slow item).
  **Chapter 22, capstone:** `POST /checkout`, validated, one transaction, 201 with a Location, 409 and 400
  as ProblemDetail, and a failed checkout changes nothing.
- Five new diagrams (test slices, Actuator, the security chain, a service call with a timeout, the
  checkout flow); seven older Spring diagrams got shorter labels so nothing spills out of its box (all 20
  checked in the browser).
- **Skill map:** `tracks/frameworks.yaml` (Backend frameworks), the track the "backend job" goal already
  pointed to: 12 Spring nodes, FastAPI and Express, and "Spring Boot in production" as coming soon.
- The course: 23 chapters, 45 tasks, about 7 hours (`estimated_minutes` 440).

## Spring Boot, block C: chapters 11 to 16 (a real database)

- **Chapter 11:** JPA entities on H2 (`@Entity`, `@Id`, a unique SKU column). **Chapter 12:** repositories,
  derived queries, 409 for a duplicate SKU. **Chapter 13:** one-to-many relationships and the N+1 problem,
  fixed with `JOIN FETCH` (the check counts SQL statements). **Chapter 14:** paging and sorting with
  `Pageable`, a price range with `@Query`. **Chapter 15:** `@Transactional`, and why checked exceptions
  commit unless listed in `rollbackFor`. **Chapter 16:** Flyway migrations, V2 adds a column, V3 sets data.
- Four new diagrams: ORM mapping, one-to-many, a transaction rolling back, Flyway versions.
- The Spring checks now show the deepest cause when an app does not start (for example
  "Schema-validation: missing column [category] in table [product]") instead of "Application run failed".

## Spring Boot, block B: chapters 6 to 10 (the API grows up)

- **Chapter 6, request bodies and DTOs:** `@RequestBody`, JSON to a record and back, a `ProductView`
  that hides the cost price. **Chapter 7, status codes:** `ResponseEntity`, 201 with a Location header,
  204 and 404 for DELETE. **Chapter 8, validation:** Bean Validation on records (`@NotBlank`, `@Size`,
  `@Positive`, `@Email`, `@Pattern`) and `@Valid`. **Chapter 9, errors:** one `@RestControllerAdvice`
  answering `ProblemDetail` (RFC 9457) for a missing product and for validation errors.
  **Chapter 10, configuration:** typed `@ConfigurationProperties`, `application.yml`, a `prod` profile.
- Three new diagrams: JSON binding, the error flow, profile layering. Every chapter is its own Maven
  project with hidden JUnit checks; every starter compiles and fails with a kind message.

## Spring Boot, block A: an introduction chapter and chapters 1 to 5, in plain style

- The Spring lab becomes **Spring Boot**, a plain course (no story) around one running Shop API. The old
  PaySetu story is gone; task ids `hello` and `merchants` are kept, and their checks still accept the old
  greeting and the old `com.paysetu` package, so nobody loses progress.
- **Chapter 0, "What a framework is, and why Spring Boot":** inversion of control, what a backend must
  do, Spring versus Spring Boot (starters, auto-configuration, embedded Tomcat), the history of Spring
  with a timeline drawing, where it is used; first task: name the app in `application.properties`.
- **Chapters 2 to 5:** how the app starts (component scanning, `@Value`), beans and dependency injection
  (a bean injected, one bean shared by two controllers), layers (controller, service, repository; the
  check spies on the service to confirm the controller delegates), and reading the request (path
  variables, optional query parameters). Each chapter is its own Maven project folder.
- Seven technical diagrams (library versus framework, the backend stack, the Spring timeline, the start-up
  sequence, the container, the layers, request mapping). Plain technical explanations, analogies rarely.
- **Checks:** hidden JUnit and MockMvc tests copied into a copy of the chapter's project and run offline;
  one `@@RESULT` per task, compile errors and start-up failures named per chapter. The image now caches
  JPA, H2, validation, Flyway, Actuator, security and the test runner for later chapters. About 4
  seconds per chapter check.
- The validator allows pictures on history steps (the owner asked for pictures of history).

## Redis in practice, chapters 7 to 13, and a "watch it run" player

- **Redis chapters 7 to 13 up to the standard:** three diagrams (a consumer group with its pending
  list, RDB versus AOF on a time line, a primary with replicas), seven worked examples (a login rate
  limit, a report lock, a delivery stream, sizing a key, a restart-safety check, a replica's health, a
  slow log entry), seven traces (a Lua script spending points, why a release checks its token, riders
  sharing a group, volatile-lru eviction, real Redis Cluster hash slots, one KEYS call freezing
  everyone), two quick checks per chapter and 15 task cards. The whole course now has 32 task cards.
- **Every trace control does something:** "▶ Watch it run" is now a Play button (one row every 1.5 s,
  ⏸ to pause), stepping by hand pauses it, and at the end "↻ Watch again" plays it again instead of a
  disabled "Done". Found by the owner.
- **Trace cells show exactly what the chapter says:** tables are read from the chapter's source text.
  Before, markdown read `customer:7:cart` as text plus a `:cart` directive and dropped part of it. A
  browser walk compared all 60 traces in five courses with their source, cell by cell: no differences.

## Redis in practice, chapters 1 to 6, brought up to the standard

- **The story of Redis** in chapter 1: memcached and disk-bound databases before it, Salvatore Sanfilippo
  in 2009, REmote DIctionary Server, Redis Cluster, streams, the 2024 licence change and the Valkey fork,
  Redis 8, where it is used; the Tcl prototype.
- **Three architecture diagrams:** one Redis shared by every outlet (Postgres on disk), round trips
  versus a pipeline, and cache-aside (hit, miss, store with a TTL).
- **Five worked examples** (a key from start to finish, a sliding session, stock in a hash, a tasting set,
  a customer as Python sees it, caching the menu) and **five traces** (two outlets racing on a counter
  versus INCR, a sliding session timer, a print queue, a snack leaderboard, a cache stampede with a lock).
- **Two quick checks** per chapter, and **task cards** on all 17 tasks, matched to what the checks expect.

## A "watch it run" trace on every worked example

- 23 new traces in Python, Go and Java from zero (all worked examples except the three one-line "a
  function that builds text" ones): remainders, a bill total, set union, a safe default, a caught error,
  writing and reading a file, command-line arguments, CSV line numbers, parsing with errors, int versus
  float division, tidying text, a sorted copy, a method through an interface, a wrapped error, reading a
  file line by line, goroutines filling their own slots, a record's method, an interface loop, a stream
  pipeline, counting rows per category. Every value was worked out with the languages' own arithmetic.
- The four from-zero courses now have 49 traces; a browser walk through all of them found every row
  with the same number of cells as its header.

## Phones: a reading mode

- On screens narrower than 760 px the lab page becomes a reading mode: the lesson fills the screen and
  the header keeps only the logo, Labs, the chapter picker and the theme, so nothing runs off the edge.
- No editor, VS Code or terminal is shown, and **no machine is started** (it would cost a machine for
  nothing on a phone). Guess-first questions, pictures and "watch it run" traces all work as usual.
- Task steps say "Reading mode. Writing and checking code works on a laptop or tablet; your place is
  saved", instead of a Check button; Run buttons are hidden (there is no terminal). The keys hint is hidden.
- A browser test at 390 px checks the fit, the missing editor and buttons, and that no machine starts.

## The lab page, polished

- **No white flash:** VS Code stays behind "Opening VS Code..." until it is drawn in its dark theme with the
  chapter's file open (about 4 seconds on a first open), instead of showing a white, empty window first.
- **A quieter header:** Stop machine and Reset lab moved into a small Machine menu, each with one line
  on what it does. Reset (which deletes the learner's files) is no longer a red button one slip away from
  Stop, and still asks to confirm. Start machine stays in view whenever the machine is stopped.
- **One Check button:** the task box no longer repeats the Check button that is always in the bar below.
- **Code shows exactly what to type:** ligatures are off in VS Code and the Lite editor, so `===` and
  `>=` stay separate characters, as in the lessons.
- **Traces keep their place:** the lesson's markdown components are now stable between renders, so a
  "watch it run" trace no longer jumps back to row 1 when the lab page re-renders (the audit's open issue).

## A confident start: one clear next step, and checks that never fail tasks not reached yet

- **Coming-up tasks are not failures.** A check runs every task of the chapter, so pressing Check early
  used to show "0 of 2 passed" in red for tasks the learner had not even reached. Those tasks now show in
  grey as "Coming up in step N. Nothing to fix yet."; the headline counts only reached tasks ("1 of 1
  passed so far"), and the task dots stay neutral for them.
- **One clear next step.** The dashboard opens with "Continue where you left off" (lab, chapter, step and
  a progress bar, from the most recently touched chapter; the next chapter once one is complete) or, for a
  new learner, a single "Start here" card with the lab their onboarding goal picked. New read-only route
  `GET /api/me/next`; lab links take `?chapter=` so Continue lands on the exact step.
- **Signed-in learners land on their dashboard** at `/`; the marketing page stays at `/?home`.

## VS Code remembers open files per lab

- Opening the Java lab after the Go lab used to reopen the Go files in VS Code: every lab's folder is
  `/workspace` on the same address, so VS Code saw one project. Each lab now opens VS Code through its
  own workspace file (`/home/learner/.labbox/<lab>.code-workspace`, the same `/workspace` folder), so
  tabs are remembered per lab. Files, paths and the terminal are unchanged. Found by the owner.

## Fewer, better pictures: one per idea, where it is taught

- JavaScript from zero went from 114 pictures (9 per chapter, on tasks, recaps and try steps too) to
  39: one per concept, on the step that teaches it, plus two cooks on the async example. Pictures on
  task steps pushed the task and its Check button out of view; three drawings per idea repeated it.
- Seven worked examples gained a "watch it run" trace instead (the average, a sorted copy, a cart
  total, filter then map, three inputs to parseQuantity, a class refusing a bad step, line numbers).
- The validator enforces where pictures go (concept and example steps; diagrams also on try steps;
  one per step), and `CONTENT_STANDARD.md` explains why. 75 unused drawings were removed.

## Product and architecture audit (20 November 2026)

- Reviewed the learning workflow, execution environments, progress tracking and visualizations across 17 labs, 85 chapters and 176 tasks.
- Reproduced an open issue in the JavaScript loop walkthrough. Re-rendering the same lesson Markdown returned the trace from row 2 to row 1.
- Saved the audit and a Word summary of the completed changes in `~/Documents/LabBox/`.

## Lesson diagrams in light and dark themes

- Lesson pictures and technical diagrams now share an opaque charcoal or warm off-white canvas, colored shapes and visible connectors. Printed Inter labels and monospace code keep the same layout in both themes.
- Branch diagrams place each outcome in its own labeled box. SVG arrowheads belong to their individual drawing.
- Verified all 158 lesson figure placements in both themes. The production build and strict validation of 17 labs passed. Backend tests passed on Postgres and Redis (266) and SQLite (262, with 4 skipped).
- All 18 browser tests passed across two runs. The dev server completed 17 before reaching its signup limit. The text-size test passed against the production build with an isolated test database.

## JavaScript from zero: three pictures per concept

- Each of the 38 concepts now has three distinct captioned drawings, spread across the existing steps in all 13 chapters. The 114 pictures include 15 existing drawings, 26 from the preview, and 73 drawn for this sample.
- In the JavaScript light theme the notebook drawings use printed Inter labels, aligned numeric columns and monospace code.
- Chapter 7 shows how two names reach one object, what a copy preserves, and why changing a discounted copy leaves the original price alone.
- A browser check walks the JavaScript course, counts each concept's pictures, and checks captions, accessible descriptions, label fit and both themes on the lesson page.
- Checks passed on 20 November: 266 backend tests on Postgres and Redis, 262 on SQLite (4 skipped), 17 browser tests, the frontend production build, and strict validation of all 17 labs.

## JavaScript from zero: a new course (13 chapters, 26 tasks)

- New lab `javascript-basics`, plain style for beginners: functions, values and types (the `"2" + "2"`
  trap), decisions (`===`, never `==`), loops, strings, arrays (sharing versus copying, sorting numbers),
  objects (copy then change), counting with objects and Sets, array methods and arrow functions,
  errors (`TypeError`, `RangeError`, and the quiet `NaN`), classes with private fields, promises and
  async/await (the event loop, `Promise.all`, retrying), and a capstone report from messy CSV data.
- "The story of JavaScript" in chapter 1: static pages and round trips before it, Brendan Eich's ten
  days at Netscape in 1995, ECMAScript and TC39, Ajax, Node.js, ES2015; Mocha and LiveScript.
- Pictures, task cards and "watch it run" traces from the start. One folder per chapter; each chapter's
  check loads only its own file. Every task has a pass message that teaches, and typical mistakes
  (sorting numbers as text, sorting the caller's array, `>` at a boundary, missing lower-casing,
  `Number("")` being 0, awaiting in a loop, a blank line shifting line numbers) get their own advice.
- Six nodes on the languages skill map. 17 labs.

## Pictures everywhere: Python, Go and Java from zero

- **Task cards on all 79 tasks** of the three from-zero courses ("What your code should do": a call
  and what it gives back, with a short note where it matters). The 50 Python examples that can run
  were run against the solution; Go and Java examples repeat their task texts, which the checks enforce.
- **18 hand-drawn pictures** (15 new: labelled jars, a fork in the road, a running track, beads on a
  thread, an egg box, a guest list, a blueprint and houses, a plug and socket, a fire alarm, a result
  and an error note, envelopes with one address, a conveyor belt, a file cut into fields, two cooks,
  library shelves), placed in 33 chapters (Python 10, Go 12, Java 11 plus the pilot's three).
- **16 "watch it run" traces** in worked examples: the ticket price, counting passing marks, keeping
  the passing marks, tidying a product code, counting words, the smallest mark, and a pointer counter.
- A picture that shows code now gets it from the chapter (`code='...'`) instead of a manifest, so one
  drawing serves every language; the validator still checks the code is in a code block of the step.
  Trace cells keep their spaces.

## Hand-drawn pictures: a sketch in the dark theme, notebook paper in the light theme

- The lesson pictures are now hand drawn: handwritten words (Caveat, bundled with the app like the
  other fonts), slightly wobbly ink, a hatched band and a violet circle in the dark theme; blue pen
  and a yellow highlighter on cream paper in the light theme. Chosen by the owner from four styles.
- Code inside a picture stays in the code font. `pictures.json` lists it, and the validator checks
  that the same code is in a code block of the step, so learners always copy from a real code block.
  Java chapter 9's HashMap step now uses the phone book in its code too (`phones.get("Riya")`).

## Pictures in lessons: task cards, small drawings and "watch it run" (Java pilot)

- **Task cards**: a task can list up to three `examples` in `lab.yaml` (`call`, `gives`, an optional
  `note`); the task box draws them as "What your code should do", `greet("Asha")` -> `"Hello, Asha!"`.
  Additive: tasks without examples look as before (`examples` is an empty list in the API).
- **Small pictures** (`:::picture{name}`, new `Pictures.tsx`): line drawings in one style and the
  theme's colours for the everyday comparison a step uses. First three: the recipe card (the parts of
  a method), a form versus a notebook (array versus ArrayList), the phone book (HashMap).
- **Watch it run** (`:::trace{title}`, new `Trace.tsx`): a small table the learner steps through with
  Back and Next, one row at a time, the values that just changed highlighted and a note saying what
  happened. First two: `shortestWord("big kirana store")` and a map of totals filling up.
- Pilot in Java chapters 1 and 9. `CONTENT_STANDARD.md` gains the rules (small, consistent, one per
  step, never decoration). The validator rejects unknown picture or diagram names and traces without
  a table or with more than 12 rows; table lines no longer count as prose words.
- A new browser test drives the picture, the trace and the task card.

## Java from zero: the whole course (13 chapters, 26 tasks)

- `java-basics` is now **Java from zero** (same id, chapter 1 and its tasks kept, so progress is safe):
  methods, variables and types, decisions, loops, strings, arrays, classes and objects, interfaces,
  ArrayList and HashMap, exceptions, lambdas and streams, files and a command-line program, and a
  capstone (fix an inherited `Book` class with equals but no hashCode, then a monthly report from
  messy CSV data).
- **"The story of Java"** in chapter 1: before Java (C and C++, one build per machine, raw memory),
  Gosling's team at Sun, "write once, run anywhere", the JVM and garbage collector, a timeline from
  1991 to the six-month releases, Oracle and OpenJDK, where it is used, Duke.
- Written in the new **"explain, do not just state"** style (`CONTENT_STANDARD.md` section 3, after the
  owner's feedback on Go): each idea gets why it exists, an everyday picture (a recipe card, a phone
  book, a fire alarm, a conveyor belt, library shelves), the code walked through slowly and the common
  confusion, in more and smaller steps. Every chapter has a worked example, an easy-win warm-up, a
  try-it, two quick checks, a deep-dive and a recap.
- Two new pictures: `==` versus `equals` on two String objects, and two variables sharing one object.
- One package per chapter (`types/`, `decisions/`, ... `capstone/`), compiled on its own, so a compile
  error fails only that chapter; the runner honours `LABBOX_CHAPTER`. Every task has a pass message
  that teaches; failures start with "Not yet" and point the way (sorting the caller's list, missing
  lower-casing, a lost cause, ties without an order).
- Skill map: five new Java nodes after "Java methods". Tests: 261 on Postgres and Redis, 257 on
  SQLite, 15 browser tests, 16 labs valid.

## The teaching standard, applied to all of Python from zero and Go from zero

- Every chapter of both courses now has a **worked example** before its first task (a different problem
  solved line by line), an **easy-win first task** (task order changed where the harder one came first:
  Python chapters 5, 11 and 13, Go chapter 6), and **two quick checks** before the recap.
- **"The story of Go"** in chapter 1: before Go (Google, 2007), Griesemer, Pike and Thompson, the problem
  it solved, a timeline from 2007 to generics in 2022, who maintains it, where it is used, the gopher.
- **Pictures** for invisible ideas: the shared default list (Python), a slice's shared array, the error
  chain, copy versus pointer and goroutines side by side (Go).
- **Checks that teach**: every one of the 53 tasks has a pass message that says what went right; Python
  failures say "Not yet" with advice for the known mistakes (`//` instead of `/`, `>` at a boundary, the
  1900 rule, `split(" ")`, a missing `return`), always pointing the way rather than giving the answer;
  Go failures start with "Not yet".
- Tests updated for the longer chapters (the lesson flow walks 13 steps in chapter 1). Tests: 261 on
  Postgres and Redis, 257 on SQLite, 15 browser tests, 16 labs valid.

## The LabBox teaching standard, and its pilot in Python from zero

- `CONTENT_STANDARD.md`: the owner's bar (world class, yet calm and confidence-building) as a checklist:
  plain style for beginner courses and a simple story for advanced ones; **history in every course**
  (the world before, who built it and when, the problem it solved, a timeline, who maintains it, where
  it is used, a fun fact; accurate facts only); each chapter as why, idea, **worked example**, guess
  first, try it, **easy-win task**, next idea with a **picture**, stretch task, **two quick checks**, go
  deeper, recap; failures that say what happened, why and what to try; passes that teach.
- New `history` step type (additive) with blocks `:::before`, `:::solved`, `:::timeline` (a list drawn
  as a timeline), `:::usedby` (chips) and `:::funfact`; `:::diagram{name}` draws built-in pictures in
  the theme's colours (the first: "two names, one list").
- The results drawer shows a pass message when a check wrote one (green edge), not only failures.
- Lesson code shows exactly what to type: font ligatures off, so `>=` never turns into one symbol.
- Pilot: Python chapter 1 gains "The story of Python"; chapter 6 (Lists) is rewritten to the standard
  (worked example, warm-up first, the diagram, two quick checks, kinder checks that recognise a set
  losing the order, a list that still has duplicates, sorting the caller's list, smallest first, and
  a missing return). Tests now find lesson steps by type instead of by number, so lessons can grow.
  Tests: 261 on Postgres and Redis, 257 on SQLite, 15 browser tests, 16 labs valid.

## Go from zero: the whole course in one go (13 chapters, 26 tasks)

- `go-basics` is now **Go from zero** (same id; plain style, everyday examples, no story). The two
  original chapters keep their ids and tasks and sit at positions 5 (slices and errors) and 8 (maps and
  structs), where they belong in a from-zero course; their story intros became plain, and both gained a
  Go deeper card.
- New chapters, each in its **own package** (so code that does not compile in one chapter never breaks
  another chapter's check): 1. first program (`hello`), 2. numbers and text (`Percent` with the integer
  division trap, `FormatRupees`), 3. decisions, 4. loops (runes), 6. strings, 7. more slices (shared
  backing arrays: `TopN` must not sort the caller's slice), 9. methods and interfaces (`shapes`),
  10. errors in depth (`%w`, `errors.Is`, `errors.As`), 11. pointers (fix a value-receiver `Deposit`),
  12. files and a CLI (`encoding/csv`, `cmd/summary` with `-top`, stderr and exit code 1),
  13. goroutines (`FetchAll` concurrent in order, timed; `CountWords` safe under 200 goroutines).
- Checks: `LABBOX_CHAPTER` and `LABBOX_TASKS` now reach check scripts (additive; `checker.py`), so a
  big course checks only the chapter asked for: about 1.5 s a check instead of compiling 13 packages.
  The Go runner fails a chapter that does not compile with the compiler's message, and when a fatal
  error kills the tests (two goroutines writing one map) it names the crash on every task it left
  unreported instead of leaving them blank.
- Typical wrong answers were run and fail with their lesson (integer division, no zero padding, sorting
  the caller's slice, nil instead of empty, `%v` instead of `%w`, a lost strconv error, results out of
  order, a map without a lock).
- Skill map: Go is now a chain of 7 nodes from first steps to files and goroutines. Home screenshot
  retaken on chapter 13. Tests: 261 on Postgres and Redis, 257 on SQLite, 15 browser tests, 16 labs valid.

## Python from zero, chapters 10 to 13: the course is complete

- 10. Errors (`to_number` raising a clear `ValueError` that names the bad text, `safe_sum` returning the
  total and the bad values), 11. Files (`read_totals` from a CSV with the csv module, `save_lines`),
  12. Running a program (`summary.py` with argparse: the top categories, a friendly "File not found"
  on stderr with exit code 1, nothing printed on import), 13. Capstone (`monthly_report`: total, count,
  average, biggest, per category and the real line numbers of bad rows; fix the inherited `budget.py`,
  which crashes on a category nobody spent on, counts "on budget" as over and returns `None`).
- A real `expenses.csv` (a month, 6 categories, about 40 good rows) with the messy parts of a real
  export: a blank line, a missing amount, a word for an amount, an empty category.
- The checks run `summary.py` as a real program (stdout, stderr, exit code, import) and test files in a
  temporary folder, including a quoted value with a comma (catches `split(",")`) and a blank line before
  a bad row (catches counting rows instead of `reader.line_num`). Every typical wrong answer was run;
  one passed (`(0, [])` for an empty `safe_sum`) and the check now requires a float total.
- The finished course: 13 chapters, 27 tasks, about 220 minutes, plain style with everyday examples.
  Skill map: errors and files, then programs and the capstone. Tests: 261 on Postgres and Redis, 257 on
  SQLite, 15 browser tests, 16 labs valid.

## Lab page: a violet Check button

- Check is the one violet button on the lab page: first #6b5ffd from the owner's reference, which was
  too bright, then the muted #5048b8 the owner picked from three rendered options. White text, no glow;
  hover, pressed, focus and disabled states included. Same in the dark and light themes.

## Python from zero, chapters 6 to 9

- 6. Lists (`top_n` without changing the caller's list, `remove_duplicates` keeping the order),
  7. Dictionaries (`count_letters`, `total_by_category` over a list of expense records),
  8. Tuples and sets (`common_items`, `min_max` with `(None, None)` for an empty list),
  9. Functions in depth (fix the classic shared default list in `add_item`, which the starter really
  has; `total(*prices, discount=0)` with a keyword-only discount). 9 chapters, 19 tasks, about 140
  minutes.
- Checks written for the real mistakes: `top_n` that sorts the caller's list says "use sorted(), not
  .sort()"; `add_item` that shares one basket names the trap, and one that returns a copy says the
  caller's basket did not change; `total_by_category` accepts 200 and 200.0 alike; `total(100, 10)` must
  treat 10 as a price. Every typical wrong answer was run and fails with its lesson.
- Skill map: lists and dictionaries, then sets, tuples and functions. The browser test no longer counts
  skill nodes exactly. Tests: 261 on Postgres and Redis, 257 on SQLite, 15 browser tests, 16 labs valid.

## Python from zero, chapters 2 to 5 (the first lab growing into a full course)

- `python-basics` is now **Python from zero** (same id, so progress, XP and streaks stay): plain style
  with everyday examples, no story (the owner's choice for beginner courses). Chapter 1 keeps its tasks
  and tests; only its old story card became a short plain intro.
- New chapters, each with a "guess first", a terminal try, two tasks, a Go deeper card and a recap:
  2. Numbers and text (`average`, `format_price`), 3. Making decisions (`grade`, `is_leap_year`),
  4. Loops (`count_above`, `first_negative`), 5. Strings (`clean_name`, `count_words`). One file per
  chapter, so a broken file never breaks another chapter's check.
- Hidden tests cover the edges beginners miss (an empty list, `999.999` rounding to `₹1,000.00`, 1900
  and 2000, the limit itself, zero, extra spaces, tabs); typical wrong answers were run and each fails
  with the exact call, the wrong value and the right one.
- Labs that grow: learners who opened a lab before it gained chapters now get the new starter files
  when they next open it (`containers.top_up`). Their own files are never overwritten, a file they
  deleted stays deleted (a record next to their folder, outside /workspace), and a link they made out of
  their folder is never followed.
- Lite editor: the chapter's own file is no longer replaced by "the first file" (which became
  `decisions.py` once the lab had more files); chapter 1's starter TODOs now name their tasks.
- Skill map: two new nodes (numbers and decisions, loops and strings). Home screenshot retaken on
  chapter 2. Tests updated for a 5-chapter course (chapter 1 now earns the chapter's XP, not the whole
  lab's bonus; the lab reopens on chapter 2 once chapter 1 is done).

## Phase J, part 2: the admin page

- `/admin` (lazy-loaded; only admins ever download it) with six tabs: Funnel (bars with the share kept
  at each step, 7 to 90 days or all), Labs (every lab, then one lab's tasks ranked by confusion and each
  chapter's steps with "stopped here", average time and views), Learners (newest 50 or a username
  search), Machines (running now; Stop and Kill ask first and say what happens to the learner), AI spend
  (per day with bars, by model, top learners) and Errors (latest server errors with request ids).
- An Admin link on /labs for admins only; a learner opening /admin lands back on /labs.
- Browser test `e2e/admin.spec.ts`: a learner is kept out; an admin (granted with the CLI and revoked
  again at the end, even when the test fails) walks the tabs, opens a lab report and stops a learner's
  machine, whose lab page then says an admin stopped it.
- Tests: 257 passed on Postgres and Redis, 253 (plus 4 skipped) on SQLite, 15 browser tests.

## Phase J, part 1: admin data and routes

- `user.is_admin` and a new `analytics_event` table (migration 0008, additive). `scripts/labbox admin
  list|grant <name>|revoke <name>` decides who may open /admin; `/api/me` says `is_admin`.
- `app/analytics.py`, mostly from tables LabBox already keeps, so it covers the past:
  - funnel: signed up, opened a lab, passed a first check, finished a chapter 1, finished a chapter 2
    (7, 30, 90 days or all). On the dev data: 418, 336, 168, 164, 0.
  - per lab: where learners stopped (the step an unfinished chapter was left on for 2+ days), time per
    step (from "step" events, recorded from now on whenever a learner moves to another step), and tasks
    ranked by confusion (low pass rate, failed checks and hint use per learner).
  - learners (search), AI spend per day, by model and top learners.
- `/api/admin/*` (403 for everyone else): funnel, labs, one lab, learners, AI spend, recent server errors
  (the middleware keeps the last 200 in Redis), running machines with Stop and Kill (files stay; logged
  with the admin's name; the learner's lab page says an admin stopped it).

## Phase H6: operations (metrics, logs, health, error reports, CI)

- `GET /metrics` (Prometheus text format, no extra library): counters in Redis so all workers add up
  (requests by route template and status, response times, checks by result and time, logins, sign-ups,
  rate limits hit, machines stopped by reason, AI requests), and live numbers read when asked (machines
  running, learners active in 15 minutes and 24 hours, accounts, each background job's last run and
  result). Only the machine itself or a request with `METRICS_TOKEN` gets it; Vite and nginx never pass
  it on.
- `deploy/monitoring/`: a Prometheus scrape config and a Grafana dashboard (12 panels: active learners,
  machines, requests and errors, p95 by route, checks, stops by reason, rate limits, logins, AI, hours
  since the last good backup).
- Request ids (`X-Request-ID`, kept from a proxy or made new) in every response and log line;
  `LOG_FORMAT=json` for one JSON object a line; failed and slow requests logged as warnings.
- `/api/health` also reports the database and shared state (additive; `ok` keeps its meaning). The old
  test that compared the whole answer now checks the original fields are unchanged.
- Sentry error reports, off unless `SENTRY_DSN` is set; no cookies, headers, bodies or addresses are
  sent. The Privacy policy needs a line before it is turned on (pre-launch list).
- CI runs the fast tests on Postgres 16 and Redis 7.4 too.
- Tests: 249 passed on Postgres and Redis, 245 (plus 4 skipped) on SQLite; 14 browser tests (one hit the
  laptop's `ERR_NETWORK_CHANGED` once and passed 4 of 4 on repeat).

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
