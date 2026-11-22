# Handoff: where the work stands (22 November 2026)

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
3. **Owner's standing order (22 November, about 11:45, going to nap): "finish springboot, rest of current Java,
   and other programming languages".** Order: finish Java (Parts 2 to 4), then Spring Boot photos and handwritten
   notes (31 recaps and a few genuine photos), then the JavaScript from zero and Go from zero rewrites (same
   treatment as Python; write each syllabus here first, then build without asking). OpenAI key approved for notes.
   Notes doodles are never a cup or a drink; no chai or tea anywhere.
   **Now: Java from zero rewrite** (owner approved the syllabus on 22 November, 10:30: "start building the Java
   one"; OpenAI key OK for Java's handwritten notes). 18 chapters, running project **Shelf** (a small library app),
   same treatment as Python (curiosity-first, folder per chapter, photos, notes, playing diagrams). Design: each
   chapter folder holds default-package classes (no `package` line until chapter 16 teaches packages), each with
   a small `main`, run with `java File.java`; `tests/run_checks.sh` maps chapter | folder | check folder | check
   class | tasks; a check class named `Self...` compiles the learner's files itself (chapter 1 checks Hello.java
   and the deliberately broken FixMe.java separately). Java photos are in `frontend/public/lesson-images/java/`
   (Duke, James Gosling, a California oak for the "Oak" name). Part 1 (chapters 1 to 6) DONE. Part 2 (7 strings,
   8 arrays, 9 classes and objects, 10 interfaces, 11 collections, 12 generics, records and enums new) DONE: chapter 10
   teaches `javac -d out *.java && java -cp out Shapes` (Java 21 has no multi-file launcher). Part 3 "Real
   programs" (13 exceptions, 14 lambdas and streams, 15 files and a CLI, 16 packages, jars and Maven new, 17 testing
   with JUnit new) DONE: the Java image now has an offline Maven repository in /opt/m2 (`labs/java-basics/warm/`,
   keep its versions in step with the chapter poms: JUnit 5.11.4, jar plugin 3.4.2); chapters 16 and 17 are Maven
   projects checked by `SelfCheckMaven` (offline `mvn package`, then `java -jar`) and `SelfCheckTesting` (the
   learner's FinesTest must pass on the real lateFee and fail on three planted bugs in `tests/pkg/testing/fines/`,
   run with JUnit's console launcher). Self checks get 170 s, the lab's check 200 s. Next: Part 4 (18 capstone). After Java: Spring Boot gets photos and handwritten notes (owner chose
   Java first). Python from zero is complete (19 chapters); its review reminder fires at 18:07 today.
4. The working tree was clean at handoff. Last run: 274 backend tests on Postgres and Redis, 270 on SQLite,
   25 browser tests, 17 labs valid, `scripts/labbox admin list` empty.

## 22 November: UI session with the owner (commits `29b27e6` to `b2ad178`)

The owner gave screenshot feedback and each change was built, tested and committed on its own.

- **Continue follows the last chapter opened** (`29b27e6`): opening a chapter now counts, not only moving a
  step. `backend/app/progress.py` (`opened`), `routers/progress_routes.py` (GET progress calls it),
  `tests/test_progress.py`.
- **Course page and lab colours** (`e87838f`): `frontend/src/pages/CoursePage.tsx` (new, `/courses/<lab>`), lab
  cards on the dashboard and home page open it; `brand.ts` (`LAB_TONES`, `labTone`, `mix`, `inkOn`, moved from
  `HomeSections.tsx`); the dashboard tape deck, cassette and chapter rail take the lab's colour
  (`LabsPage.tsx`, `styles.css`); `GET /api/me/next?lab=<id>` (`routers/engagement_routes.py`); `MetroMap.tsx`
  gained `labLines` and `MetroLegend`; `e2e/course.spec.ts` (new).
- **Profile panel** (`68daeaf`): `components/ProfileMenu.tsx` replaces `StatsBadges.tsx` in every top bar (an
  initial in a level ring; the panel has level, XP to next, streak and best, stars, today's goal, Exit).
  `e2e/profile.spec.ts` (new), `e2e/engagement.spec.ts` reads stats from the panel.
- **Skill maps section removed** (`718e52c`): `SkillsPage`, `LabMapPage`, `TrackPage`, `roadmap.spec.ts`,
  `skillmaps.spec.ts` deleted; `App.tsx` redirects `/skills/<lab>` to the course page and `/skills`,
  `/tracks/<track>` to `/labs`; the course page has a "Skill map" title. Track data and the skills API stay.
- **Packages** (`753a6fa`): `three`, `@types/three`, `@xyflow/react` uninstalled.
- **Focus only in Lite** (`594a3b8`): `StatusBar.tsx` `canFocus`, `LabPage.tsx` passes `!useIde`;
  `e2e/editor.spec.ts` checks it.
- **Dashboard progress card removed** (`5d6c72b` moved it, `b2ad178` removed it): its numbers are in the
  profile panel; the daily drill is full width.
- Earlier the same day (before `29b27e6`): the metro-map skill maps with course parts (`part:` in `lab.yaml`,
  chapter `topics` in the lab detail), subtopics deep-linking to `?chapter=...&step=n`, and the tape deck.

Flaky browser tests seen today (pass on rerun): `engagement.spec.ts` (drill), `javascript-pictures.spec.ts`
(times out under full parallel load).

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
| 5b | Redis chapters 1 to 6 up to the standard (history, 3 diagrams, worked examples, traces, quick checks, task cards) | done | see git log |
| 5c | Redis chapters 7 to 13, the same; traces get a Play button; trace cells read from the source | done | see git log |
| done | **Spring Boot rewrite** (owner, 21 November) COMPLETE: 31 chapters 0 to 30 in four parts, full lessons in a teacher's voice, every step about code names its file (`file=` `line=`), outputs captured from the real projects. New chapters need a project in starter/ and solution/, a check in tests/<ch>/, a CHAPTERS row in tests/run_checks.sh, a lab.yaml entry and a skill-map node. | **done** | |
| next | Python in practice (story: propose the story and syllabus first), then a later "Spring Boot in production" lab with a story and scenarios (owner: in depth, as many chapters as it needs) | | |
| later | The other short labs get the standard when each grows into a full course (owner agreed) | | |
| idea | "Run this example" on worked examples and "run your file" on task steps (the owner likes Run in terminal) | proposed | |

## 21 November: what was done, file by file (commits `3ffe955` to `ebcde82`)

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
- `LessonMarkdown.tsx`: picture, trace and diagram blocks; remark-gfm renders tables; trace rows are read from the chapter source;
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

- The VS Code explorer shows the lab name as a heading with `workspace` one level below (from the per-lab
  workspace file). Harmless; could be flattened later.
