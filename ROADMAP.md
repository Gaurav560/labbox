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

### Labs: 15 live (batch 1: 11, batch 2: 4)

| Track | Labs |
|---|---|
| Languages | python-basics, python-collections, java-basics, java-collections, javascript-inside-out, go-basics |
| Frameworks | fastapi-first-api, spring-boot-first-api, express-api |
| Databases | sql-from-zero, postgres-indexing-incident, **redis-in-practice**, **postgres-transactions-and-locks** |
| DevOps | **linux-on-call**, **git-without-fear** |

Skill maps: `tracks/languages.yaml`, `tracks/databases.yaml`, `tracks/devops.yaml`.
You chose to stop at 15 labs for now and build the platform phases next.

Every lab passes `validate --strict` and `test-lab` (the starter fails, the solution passes).

### The lab pipeline

- Base images: base, python, java, node, go, checker.
- Six templates: python, java, node, go, service-incident, preview-app.
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
  - the AI track (Phase E)
  - Docker and Kubernetes labs (Phase F)
  - system design labs (Phase G)

**Launch set still missing (spec 8.8):**
- spring-boot-on-fire
- postgres-in-depth
- rag-from-zero
- build-your-own-gpt
- rate-limiter
- docker-start-to-ship

The flagship labs should reach 8 to 12 chapters; today's labs have 1 or 2.

### 3. Platform phases not started

| Phase | What | Needs from you |
|---|---|---|
| E | LLM gateway, AI labs, AI tutor (spec 6) | Which LLM provider and key to use (the OpenAI key is approved for covers only) |
| F | Docker and Kubernetes inside labs, with Sysbox (spec 4) | sudo on this machine to install Sysbox |
| G | System design labs with k6 load tests and rubric grading (spec 7) | Nothing |
| H | Real app foundations: Postgres instead of SQLite, Redis, Google login, workers, disk quotas (spec 10) | A Google OAuth client id and secret |
| I | Payments with Razorpay in test mode: 2 free chapters, paid unlocks the rest | Razorpay test keys |
| J | Admin dashboard and funnel analytics | Nothing |
| K | Launch-set labs complete, deploy to AWS | AWS access, and your approval before anything runs there |

### 4. Smaller items put off by agreement

- A spoken voiceover or a recorded demo video for the hero tour (needs your recording, or approval for a paid text-to-speech service)
- Share card images for streaks and levels, and a public profile at `/u/{username}`
- Gauges for live check numbers (shown as plain numbers today)
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
ROADMAP.md, then propose the next phase (E) and wait for my OK."** The agent reads `AGENTS.md` by itself.
