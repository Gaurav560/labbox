# Handoff: where the work stands (21 November 2026)

Read this first if a session ends mid-work. It lists what was done, file by file, what is left and how to
pick it up. `AGENTS.md` (rules, how to run and test), `ROADMAP.md` (status) and `CHANGELOG.md` (history,
newest first) are the long-term record; this file is the short "resume here" note. Update it at the end of
every session.

## Resume here

1. Start the stack (see AGENTS.md). For the **local dev server only**, start the backend with a bigger
   sign-up allowance so browser tests do not hit the 60-per-hour limit:
   `cd backend && SIGNUPS_PER_IP_HOUR=1000 .venv/bin/uvicorn app.main:app --port 8000 --workers 4`.
   Frontend: `cd frontend && npm run dev`. Database and Redis: `scripts/devdb.sh`.
2. Check the state: `git log --oneline -12`, `scripts/labbox validate --strict` (17 labs valid).
3. **Next task: step 5 of the owner's UX review** (below). Plan first, wait for the owner's OK.
4. The working tree was clean at handoff. (The audit-entry question is settled: the owner let me decide,
   and the entry was kept.)

## The owner's goals (20 to 21 November)

- Content must be world class yet calm and confidence-building; learners should feel it is worth paying
  **100 dollars for 6 months**.
- Visuals rules (in `CONTENT_STANDARD.md`): architecture and conceptual diagrams yes; **execution
  visualizations (interactive "watch it run" traces) high priority**; real code always, never code as an
  image; decorative images rarely. The validator enforces where pictures may go.
- Course order: Python, Java, Spring Boot, SQL, Postgres, JavaScript, Express, FastAPI, Go, Linux, Git,
  system design. Done: Python, Go, Java, JavaScript from zero. Next course: Python in practice (with a
  story). Platform phases after that: K (AWS, ask first), H4 (OAuth), I (payments after AWS), AI labs last.

## The owner's UX review (21 November): steps and status

| Step | What | Status | Commit |
|---|---|---|---|
| 1 | Pictures only where an idea is taught, one per idea; traces instead | done | `e9a0105` |
| bug | VS Code reopened the previous lab's files | fixed | `0cbab3b` |
| 2 | Coming-up tasks not failures; Continue / Start here card; `/` goes to the dashboard | done | `146d375` |
| 3 | No VS Code white flash; Machine menu; one Check; no ligatures; trace keeps its place | done | `c436f64` |
| 4 | Phones: reading mode, no machine started | done | `440249f` |
| 5a | A trace on every worked example in Python, Go and Java from zero (23 new, 49 in all) | done | see git log |
| 5b | Redis (0 pictures, traces, task cards) and the other labs up to the standard | **next** | |
| idea | "Run this example" on worked examples and "run your file" on task steps (the owner likes Run in terminal) | proposed | |

## What was done, file by file (commits `3ffe955` to `ebcde82`)

### Courses (labs/)

- `labs/java-basics/` (`3ffe955`, `5bcb6b4`): **Java from zero**, 13 chapters, 26 tasks, written in the
  "explain, do not just state" style. `lab.yaml` (chapters, tasks, 3 hints each, task `examples`),
  `chapters/01-13*.md`, one package per chapter in `starter/` and `solution/` (types, decisions, loops,
  words, arrays, objects, shapes, collections, errors, streams, files, capstone), `expenses.csv`,
  `tests/run_checks.sh` (chapter table, honours `LABBOX_CHAPTER`), `tests/common/T.java` (pass messages,
  "Not yet:" failures), `tests/pkg/<dir>/Check*.java`, `tests/CheckGreeter.java`.
- `labs/javascript-basics/` (`4c5ddbd`, then `d656a70` by another session, then `e9a0105`): **JavaScript
  from zero**, new lab, 13 chapters, 26 tasks. `lab.yaml`, `chapters/`, one folder per chapter in
  `starter/` and `solution/`, `tests/check.js` (all checks, `LABBOX_CHAPTER`, pass messages, typical-mistake
  advice), `tests/run_checks.sh`, `Dockerfile` (`FROM labbox/node:v1`), `.dockerignore` (keeps solution and
  tests out of the image), `cover.svg`. In `e9a0105` its pictures went from 114 to 39 (one per concept) and
  7 worked examples gained traces (ch 2, 6, 7, 9, 10, 11, 13).
- `labs/python-basics/`, `labs/go-basics/` (`5bcb6b4`): task card `examples` on every task in `lab.yaml`,
  pictures and traces placed in chapters.
- `tracks/languages.yaml`: Java nodes after java-methods (`3ffe955`), six JavaScript nodes (`4c5ddbd`).

### Lesson rendering (frontend/src/lesson/)

- `Pictures.tsx`: hand-drawn everyday pictures (`:::picture{name=... code='...'}`), Caveat lettering,
  theme-aware; registry `PICTURES`; unused drawings removed in `e9a0105`.
- `JavaScriptPictures.tsx`, `PicturePrimitives.tsx`: added by another session (`d656a70`, `0b5d260`);
  trimmed to the drawings still used in `e9a0105`.
- `Diagrams.tsx`: `string-equals`, `object-reference` (`3ffe955`); light and dark themes by another
  session (`0b5d260`).
- `Trace.tsx`: "watch it run" step-through tables (`:::trace{title='...'}` around a pipe table).
- `TaskCard.tsx`: "What your code should do" from task `examples`.
- `LessonMarkdown.tsx`: picture, trace and diagram blocks; trace tables parsed from text (no remark-gfm);
  components memoised so interactive blocks keep their state across renders (`c436f64`).
- `StepCard.tsx`: task card in the task box; no duplicate Check button (`c436f64`); `onRun` optional and
  reading-mode text on phones (`440249f`).

### App pages and components (frontend/src/)

- `components/CheckDrawer.tsx`, `components/TaskList.tsx`: tasks on steps not reached yet are "coming up",
  never failures (`146d375`).
- `pages/LabsPage.tsx`: `NextCard` (Continue where you left off / Start here) (`146d375`).
- `App.tsx`: `/` sends signed-in learners to `/labs`; `/?home` shows the marketing page (`146d375`).
- `pages/LabPage.tsx`: `?chapter=` link support (`146d375`); `upcoming` tasks; phone reading mode
  (`usePhone`, no work area, no machine start; lab load and machine start are separate effects) (`440249f`).
- `components/IdePane.tsx`: VS Code hidden behind "Opening VS Code..." until drawn in its dark theme
  (`c436f64`).
- `components/MachineMenu.tsx` (new), `components/StatusBar.tsx`: Stop machine and Reset lab in a Machine
  menu (`c436f64`).
- `components/EditorPane.tsx`: ligatures off (`c436f64`).
- `usePhone.ts` (new): phone breakpoint, 760 px (`440249f`).
- `api.ts`: `TaskExample`, `NextStep`, `api.next()`.
- `styles.css`: pictures, traces, task cards, next card, coming-up results, Machine menu, IDE holder,
  phone mode. (Dark-theme lighter surfaces were tried in `f218df8` and reverted in `e5b03ed` by the owner.)
- `main.tsx`: Caveat font (`@fontsource/caveat`, installed by the owner).

### Backend (backend/app/)

- `labs.py`: `TaskExample`, optional `Task.examples` (up to 3).
- `routers/lab_routes.py`: task `examples` in the lab detail.
- `routers/engagement_routes.py`: `GET /api/me/next` (continue or start) (`146d375`).
- `ide.py`: per-lab VS Code workspace file `/home/learner/.labbox/<lab>.code-workspace` (`0cbab3b`);
  `editor.fontLigatures` off (`c436f64`).
- `routers/preview_routes.py`: VS Code URL opens `&workspace=<that file>` (`0cbab3b`).

### Tools and standards

- `tools/labbox_cli.py`: validator checks unknown picture and diagram names, traces (a table, at most 12
  rows), code shown in a picture must be in a code block of the step, picture placement (pictures on
  concept or example steps, diagrams also on try steps, one per step); table lines do not count as prose.
- `CONTENT_STANDARD.md`: section 3 "Explain, do not just state"; pictures rules; the owner's visuals
  table (`e9a0105`).

### Tests

- Backend: `tests/test_cli.py` (pictures, traces, placement, code in pictures, `javascript-basics` in
  test-lab), `tests/test_labs.py` (examples limits), `tests/test_progress.py` (examples served, `/api/me/next`),
  `tests/test_engagement.py`, `tests/test_lessons.py` (longer chapters), `tests/test_ide_docker.py`
  (workspace file).
- Browser (`frontend/e2e/`): `next-step.spec.ts`, `phone.spec.ts` (new), `lab.spec.ts` (Machine menu,
  pictures, traces, task cards), `home.spec.ts` (`/` for signed-in), `javascript-pictures.spec.ts` (one per
  concept), `diagram-themes.spec.ts` (phone width has no editor area).
- Last run (21 November, after step 4): 268 backend tests on Postgres and Redis, 264 on SQLite, 20 browser
  tests, 17 labs valid. `diagram-themes.spec.ts` sometimes fails its arrowhead check once and passes on a
  rerun; `ERR_NETWORK_CHANGED` blank pages are this laptop (rerun).

## Editing CHANGELOG.md safely

Add new entries at the top, under `# Changelog`. Never open a file for writing and reading in one
expression (Python's `open(f, "w").write(open(f).read())` empties the file first).

## Known gaps

- Lesson tables (the capstone field tables) show as raw `|` text: `remark-gfm` is not installed and
  installing npm packages is blocked for the agent; ask the owner to run
  `cd frontend && npm install --save-exact remark-gfm@4.0.1`.
- The VS Code explorer shows the lab name as a heading with `workspace` one level below (from the per-lab
  workspace file). Harmless; could be flattened later.
