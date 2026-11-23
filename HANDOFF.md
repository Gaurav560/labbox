# Handoff: where the work stands (23 November 2026)

Read this first when a session starts. `AGENTS.md` has the rules and how to run and test, `ROADMAP.md`
the status of every lab and phase, `CHANGELOG.md` the history (newest first), `CONTENT_STANDARD.md` what a
course must be, and `COURSE_PRODUCTION.md` how one is built. This file is only the short "resume here" note:
update it at the end of every session. Earlier, longer versions of it are in git history.

## Resume here

- **State:** the working tree is clean after each commit; local commits wait for the owner to push.
  Last full run green: 279 backend tests on Postgres and Redis, 25 browser tests, 18 labs valid,
  `scripts/labbox admin list` empty.
- **Last work (23 November):** the Spring AI course is complete (20 chapters, 40 tasks, about 16.5 hours,
  commits `7584fbe`, `3c4e98c`, `34d2f53`). Then the way courses are made was written down:
  `COURSE_PRODUCTION.md`, the full-standard list at the top of `CONTENT_STANDARD.md`, the per-lab table in
  `ROADMAP.md`, and the helper scripts in `tools/authoring/`.
- **Nothing is half-built.** No capture machine is running.

## Waiting for the owner

1. **Drink words in older examples** (coffee, juice, milk, lassi or tea): 137 files across 13 labs (counted with a wider word list than before),
   most in spring-boot-first-api (71) and python-basics (22); the per-lab counts are in `ROADMAP.md`. Rewrite
   them? (The rule is never drinks; these were written before it.)
2. **The `ai` onboarding goal** still starts with python-basics. Start it with spring-ai?
3. **Next step:** the roadmap order is K (the AWS deploy, needs the owner), then H4 (Google and GitHub login),
   then I (payments). The eight short labs and the rest of the AI track wait for a syllabus and an OK each.

## How to start the stack

1. `scripts/devdb.sh` (Postgres on 55432, Redis on 56379).
2. Backend, for the **local dev server only** with a bigger sign-up allowance so browser tests do not hit the
   60-an-hour limit: `cd backend && SIGNUPS_PER_IP_HOUR=1000 .venv/bin/uvicorn app.main:app --port 8000 --workers 4`.
3. Frontend: `cd frontend && npm run dev`, then http://localhost:5173.
4. Check: `git log --oneline -8`, `scripts/labbox validate --strict`.

## How each full course is checked (for whoever edits one)

| Course | Checks | Notes |
|---|---|---|
| Python from zero | `tests/checks.py` (rewritten chapters) and `tests/check.py` (older ones) | a folder per chapter |
| Java from zero | `tests/run_checks.sh` table, a check class per chapter in `tests/pkg/` | `Self...` classes compile the learner's files; chapters 16 and 17 are Maven projects (offline `/opt/m2`, `warm/`) |
| JavaScript from zero | `tests/check.js` | chapter 17's planted bugs in `tests/testing/` |
| Go from zero | `tests/run_checks.sh`, `tests/gorun/`, `tests/gotest/` | demos carry `//go:build ignore`; planted bugs in `tests/gotest/fines/` |
| Spring Boot | JUnit (MockMvc) per chapter folder in `tests/` | chapters 17 and 18 run the learner's tests on a planted bug (`own.env`) |
| Spring AI | JUnit per chapter with a fake OpenAI server (`tests/common/FakeOpenAi.java`) | the `CHAPTERS` table in `tests/run_checks.sh` |
| Redis in practice | live: `tests/check.py` reads Redis and calls the learner's app | `solution/apply.sh` serves every chapter's solution |
| SQL from zero | live: runs the learner's `.sql` files read-only | Postgres 16 service |
| Git without fear | live: plain git on the learner's repos | `mount_workspace: ro`; setups build each repo (`setup_user: learner`) |
| Linux on call | live: scripts run in scratch copies | setups build each chapter folder |

## Ideas the owner liked, not built

- "Run this example" on worked examples and "run your file" on task steps (the owner likes Run in terminal).
- "Python in practice" (with a story) and "Spring Boot in production" (a story and incident scenarios).
- Spring AI after opening day: query rewriting (`RetrievalAugmentationAdvisor` with a
  `CompressionQueryTransformer`) and a follow-up question in the golden set.

## The owner's goals

- Content world class yet calm and confidence-building; worth **100 dollars for 6 months** to a learner.
- LabBox is marketed as AI labs; the other tracks are additional.

## Flaky tests (pass on rerun)

`phase-d.spec.ts` under full load, `engagement.spec.ts` (drill), `javascript-pictures.spec.ts`,
`diagram-themes.spec.ts` (arrowhead check). A blank lab page with `net::ERR_NETWORK_CHANGED` is this laptop.

## Editing CHANGELOG.md safely

Add new entries at the top, under `# Changelog`. Never open a file for writing and reading in one
expression (Python's `open(f, "w").write(open(f).read())` empties the file first).

## Known gaps

- The VS Code explorer shows the lab name as a heading with `workspace` one level below (from the per-lab
  workspace file). Harmless; could be flattened later.
- Handwritten notes pages are stored as generated (1536 by 1024, about 1.7 MB each); they could be shrunk.
