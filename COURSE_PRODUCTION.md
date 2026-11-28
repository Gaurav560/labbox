# How a LabBox course is made

`CONTENT_STANDARD.md` says what a finished course must be. This page says how one is built, from the
syllabus to the commit, the way the ten full-standard courses were built (20 to 23 November). Follow the
steps in order. The helper scripts are in `tools/authoring/`; each one explains itself when run without
arguments.

| Step | What | Output |
|---|---|---|
| 1 | Decide the course and write the syllabus | a syllabus in `HANDOFF.md`, the owner's OK |
| 2 | Build the lab folder and its image | `labs/<lab>/` with `lab.yaml`, `Dockerfile`, `warm/` |
| 3 | Write the chapter projects | `starter/NN-name/` and `solution/NN-name/` |
| 4 | Write the hidden checks | `tests/run_checks.sh` and one check per chapter |
| 5 | Write the chapters | `chapters/NN-id.md` |
| 6 | Capture every output for real | the `try` steps, the error messages, the numbers |
| 7 | Photos | `frontend/public/lesson-images/<course>/*.webp` |
| 8 | Diagrams | playing diagrams in `frontend/src/lesson/Diagrams.tsx` |
| 9 | Handwritten notes | one page per recap |
| 10 | Cover, colour, track | `cover.svg`, `LAB_TONES`, `tracks/<track>.yaml` |
| 11 | Prove it | validate, test-lab, the full tests, the browser |
| 12 | Record it | `ROADMAP.md`, `CHANGELOG.md`, `HANDOFF.md`, one commit per part |

## 1. Decide the course

Answer these before writing a line, and write the answers into `HANDOFF.md` as the syllabus.

1. **Is the learner new to this technology?** Then the course is plain: no characters, no story, one
   running project that grows chapter by chapter (this holds for a first framework too, like Spring Boot).
   Stories and scenarios are only for advanced courses: production, incidents, system design.
2. **The running project.** One small, named, distinctive project for the whole course. It must not repeat
   another course's project, and it must never be:
   - chai, tea, coffee or any drink, a stall or a cafe;
   - Dabba Express or tiffin delivery;
   - anything that resembles the Chai aur Code platform: its themes or its usual tutorial projects (a video
     site, a blog, a todo app, a weather app, a currency converter, a password generator, a shop clone).

   Projects in use: Pocket (Python, a money tracker), Shelf (Java, a library), Mixtape (JavaScript, playlists),
   Parcel (Go, a parcel tracker), the Shop API (Spring Boot), Basket (Redis, 10-minute grocery delivery in
   Pune), Safar (SQL, bus ticket booking), Trails (Git, a trekking website), Tara (Linux, a radio telescope
   observatory), Atlas (Spring AI, the guide of a science museum in Pune).
3. **The syllabus follows the official documentation** for a framework or library: map every chapter to a
   section of the reference, and use the version the docs show as current (Spring AI: docs.spring.io's
   reference, 2.1.0 with Spring Boot 4.2.0). Re-read the docs' contents page before adding chapters.
4. **Size by the topic, not by a number.** Parts of 4 to 6 chapters; two tasks per chapter; 35 to 60
   minutes a chapter (the validator allows 10 to 60). The full courses are 14 to 31 chapters.
5. **For a technology that exists for speed or scale** (Redis, databases, caches), plan where the course
   measures it: real latency, real throughput, the money it saves, with honest arithmetic.
6. **Rewriting an existing lab:** keep every chapter id and every task id (learner progress hangs on them);
   new ones are added. Task ids are unique across the whole lab.
7. **Before you start.** Write the lab's `before_you_start` (CONTENT_STANDARD.md section 7): who it is for, what to
   know first, why, and which LabBox lab and chapters teach it; check every chapter you point to against that lab's
   real chapter list.

Write the syllabus as: parts, then per chapter its number, id, title, the idea it teaches, its two task ids,
and the docs section. Then wait for the owner's OK, unless the owner said to build without asking.

## 2. The lab folder and its image

```text
labs/<lab>/
  lab.yaml              chapters, tasks, hints, examples, image, resources, previews, check settings
  Dockerfile            the lab image, FROM a base image (labbox/python:v1, java, node, go)
  warm/                 a project that pulls every dependency at build time (Java and Go)
  chapters/NN-id.md     one file per chapter
  starter/NN-name/      what the learner gets, one folder per chapter
  solution/NN-name/     the same folders, finished (only test-lab sees them)
  tests/run_checks.sh   the hidden checks, plus a folder per chapter
  cover.svg             the card cover
```

- A small lab starts from a spec: `scripts/labbox new-lab --from-spec specs/<lab>.yaml` (see `specs/README.md`).
  A full course is easier to build by hand from an existing full course of the same language.
- **The image works offline.** Checks run with no network, so every dependency is in the image: Maven
  repositories in `/opt/m2` filled from `warm/pom.xml` (a new dependency goes into `warm/pom.xml` and the
  image is rebuilt, or the offline build fails), `GOCACHE=/opt/gocache` for Go, npm packages baked in.
- **`lab.yaml`, per chapter:** `id`, `title`, `file`, `minutes`, `folder` (its project folder), `part` on the
  first chapter of each part (the course page draws each part as a metro line), `tasks`. Per task: `id`, a
  short lowercase `title` (`connect /ask to the model`), `xp`, three `hints` that climb (what is wrong now,
  where to work, nearly the answer, never a solution line), and two or three `examples` (`call`, `gives`,
  `note`) drawn on the task card.
- Chapter setups (`setup:`) run as root with every capability dropped; use `setup_user: learner` when the
  setup builds files in `/workspace` (a git repository, a log folder).
- Postgres services need the small memory tuning in `postgres-indexing-incident/lab.yaml`.

## 3. The chapter projects

- One folder per chapter, named like the chapter (`07-tools/`), so a learner can open any chapter at any
  time. Each folder is a complete project that builds and runs on its own.
- The starter is the solution of the chapter before, plus this chapter's new files, with a TODO for each
  task: `// TODO (task opening_hours_tool): ...`. A TODO says the goal, never the code. Reaching a task step
  opens its TODO in the editor.
- **For a big course, write a generator** (a Python script in the session scratchpad) that writes
  `starter/` and `solution/` from one table: for each chapter folder, each path maps to its starter text and
  its solution text, or one text for both. Changing a shared file then changes every chapter that has it.
  The committed folders are the record; the generator is a writing aid.
- Every line a lesson points at (`file="..." line="..."`) must stay where the lesson says. After any change
  to a starter file, check the line numbers of the steps that point into it (the validator only catches a
  line past the end of the file).

## 4. The hidden checks

- `tests/run_checks.sh` prints one `@@RESULT {"task": ..., "passed": ..., "message": ...}` line per task, never
  fails as a whole, and runs only the current chapter when `LABBOX_CHAPTER` is set (see
  `labs/spring-ai/tests/run_checks.sh`: a `CHAPTERS` table of `id|folder|tasks`).
- Checks test behaviour, not text: run the learner's code (JUnit, pytest, `node:test`, `go test`, psql, a
  running service). AI labs give the code a fake model server (`labs/spring-ai/tests/common/FakeOpenAi.java`)
  and check the request the code builds, so checks are free and always give the same result.
- Chapters where the task is to write tests run the learner's tests twice: on the correct code, then with
  a planted bug (`tests/<chapter>/bug/`, Spring Boot chapters 17 and 18).
- Failure messages say what happened, why, and what to try next; they recognise the common wrong answers.
  A pass says why it matters. A later task in the same chapter that cannot run yet says so kindly ("first
  make /ask call the model ...").
- While writing a chapter, run its checks quickly:

  ```bash
  tools/authoring/runcheck.sh <lab> starter <chapter-id>    # every task fails, kindly
  tools/authoring/runcheck.sh <lab> solution <chapter-id>   # every task passes
  ```

  Then write the typical wrong answers into a copy of the solution and check that each fails with its lesson.

## 5. Writing the chapters

Follow `CONTENT_STANDARD.md` (the step order, the voice, the visuals). The working method:

1. Write the chapter's steps top to bottom in the Spring Boot voice, curiosity first: a question or a
   surprise, guess before telling, the problem seen before it is fixed.
2. Every step about project code names its file and lines: `:::step{type=example title="..." file="19-agents/src/main/java/com/atlas/AgentController.java" line="70"}`
   (`line` is one line or a range like `"9-12"`).
3. Leave a marker where a real output must go, and fill it in step 6. Never type an output from memory.
4. Chapter 1 tells the history of the technology (`history` step: `:::before`, `:::solved`, `:::timeline`,
   `:::usedby`, `:::funfact`); every later chapter has its own short history step when its idea has one
   (who invented it, when, the problem it solved). Every date, name and number must be checkable.
5. Tables for comparisons and checklists; `:::trace` for state that changes step by step; a playing diagram
   for any process the learner cannot see; quick checks that are real decisions; a `deep-dive` that connects
   to production; a recap that starts "You can now".
6. Before finishing, search the chapter for banned words: `grep -niwE "chai|tea|coffee|juice|milk|lassi|dabba|tiffin" chapters/*.md`, and for em dashes (the validator refuses them too).

## 6. Capturing real output

Everything a lesson quotes (a log line, a curl answer, an error, a stack trace, a model's answer, a token
count) is captured by running the chapter's real project in the lab's real image.

```bash
SP=<session scratchpad>/<lab>
tools/authoring/capture.sh start <lab> $SP                 # copies solution/ to $SP/ws, starts "labcap"
tools/authoring/capture.sh run 07-tools 'mvn -q -o test'   # prints "$ cmd" and the output, as the learner
tools/authoring/capture.sh app 07-tools                    # a Spring app in the background, waits for 8080
tools/authoring/capture.sh run 07-tools 'curl -s localhost:8080/ask?q=Hello'
tools/authoring/capture.sh stop
```

- To show a mistake, edit the file in `$SP/ws` into the wrong version, run it, copy the real error, and put
  the solution back.
- Paste outputs as they are. Trim long ones and mark the cut with `...`; never edit what remains.
- **When the capture disagrees with the lesson, the lesson changes.** Spring AI examples: a reviewer model
  called a 32-word label "46 words" (so the lesson now counts words in Java); a follow-up question found no
  cards (so the lesson explains query rewriting); an untagged metric counted tokens twice (so the lesson
  reads the tagged one).
- **AI labs** capture through the real gateway with a separate author account, so captures never touch the
  owner's or a learner's budget:

  ```bash
  cd backend && .venv/bin/python ../tools/authoring/author_token.py <lab>-author <lab> > $SP/token.txt
  tools/authoring/capture.sh start <lab> $SP $SP/token.txt
  tools/authoring/capture.sh run 01-why-ai 'lab requests --last'   # the full request and response
  ```

  The token only works at the gateway; the provider key stays in `backend/.env`. The author account has the
  normal daily budget (50,000 tokens, reset at midnight UTC). Never raise it to finish faster: if it runs
  out, wait for the reset. Photos are the expensive part (one 800 by 600 photo was 25,596 tokens with
  gpt-4o-mini; shrink to 512 px first).
- Remove the capture machine when done (`capture.sh stop`) and check `scripts/labbox admin list` is empty.

## 7. Photos

Real, freely licensed photos of real things: the person who made the technology, a historic machine, the
real-world thing an idea is named after or works like (a 1907 switchboard for routing, hallmarks for
evaluation, a ghat road wall for guardrails). At least one for every chapter or two, so long courses get more (a
28-chapter course well over 20), spread through it, each on the step that teaches its idea, never on task, quick-check
or recap steps. The lead sentence before each photo must make the link obvious to a beginner (CONTENT_STANDARD.md
section 7).

```bash
python3 tools/authoring/commons_search.py $SP/cands.json "switchboard=telephone switchboard operators 1907" "meter=electricity meter"
# open the thumb links in cands.json, choose one per key, check its license
python3 tools/authoring/commons_fetch.py $SP/photos "switchboard=File:Telephone_switchboard_6_Oct_1907_Salt_Lake_City.jpg"
cp $SP/photos/switchboard.webp frontend/public/lesson-images/<course>/
```

- Licenses: CC BY, CC BY-SA, CC0 or public domain only. Credit the author and license exactly as Commons
  states them (`credits.json` has both), and link the file page.
- Write the directive with a lead sentence that says why the learner is looking at it:

  ```text
  In 1907, every telephone call went first to an operator at a switchboard, who asked who you wanted and
  plugged you through to the right line.

  :::photo{src="/lesson-images/spring-ai/switchboard.webp" alt="A long row of telephone operators ..." credit="The Salt Lake Herald" license="Public domain" source="https://commons.wikimedia.org/wiki/File:..."}
  Telephone operators at a newly installed switchboard in Salt Lake City, 6 October 1907.
  :::
  ```

  `tools/authoring/insert_photos.py` places many at once from a JSON list; read the result afterwards.
- `alt` describes what is in the photo for someone who cannot see it. Never an AI image of a real person.
- Commons answers 429 when asked too fast: the scripts pace themselves and skip files already fetched, so
  run them again later. Keep `credits.json` and unused photos out of `frontend/public`.
- Photos a learner sends to their own code (the Spring AI vision chapter) ship in the chapter project
  with a `CREDITS.md` beside them.

## 8. Diagrams

- **Playing diagrams** (a process in time: start-up, a request's journey, RAG, a guard): a quiet vertical
  timeline the learner plays with Play, Back and Next. Write them as data and add them with
  `python3 tools/authoring/add_diagrams.py $SP/diagrams.py` (the format is in the script); the lesson uses
  `:::diagram{name="ai-rag"}` with a one-line caption saying what to notice.
- **Static diagrams** (architecture, memory, references) are components in `frontend/src/lesson/Diagrams.tsx`
  built from `Sketch.tsx`: hand-drawn outlines, plain light fills, the normal font, never handwriting fonts
  or hatching behind text. Copy an existing one.
- **Everyday pictures** (`:::picture{name=...}`) live in `frontend/src/lesson/Pictures.tsx`; use them rarely.
- At most one picture or diagram per step. The validator refuses unknown names. Look at each one in the
  browser, in the light and dark themes.

## 9. Handwritten notes

Each recap ends with one AI-drawn notebook page of the chapter's five or six key lines.

```bash
cat > $SP/notes.json <<'EOF'
[{"name": "springai-19-notes", "lines": ["Start with a workflow", "Route: classify, then answer", "Write, review, rewrite", "Always a limit: 3 drafts", "Every step is a paid call"]}]
EOF
cd backend && .venv/bin/python ../tools/authoring/notes.py $SP/notes.json $SP/notes "a small doodle of a museum building with a planetarium dome"
```

- Five or six short, plain sentences a beginner can read on their own (CONTENT_STANDARD.md section 7): "Embeddings
  capture the topic, not yes or no", never fragments like "Not does not move much"; no formulas, no code longer than a
  name. One doodle per course,
  related to its project; never a drink, an animal, a robot with a face or a logo.
- **Check every page letter by letter.** Image models misspell, drop the last line, repeat a line and change
  digits. A wrong page is redrawn (move it away and run again), or its lines are shortened or merged. Never
  ship a page with a mistake.
- Copy the good page to `frontend/public/lesson-images/<course>/<course>-NN-notes.webp` and end the recap with:

  ```text
  :::photo{src="/lesson-images/spring-ai/springai-19-notes.webp" alt="Handwritten notes about workflows and agents: start with a workflow; ..." ai="true"}
  One page of notes for this chapter.
  :::
  ```

  The `alt` text repeats every line, so the page is readable without the image.

### Sketchnote rules (owner, 28 November, verbatim)

Since 25 November the recap picture is a tall sketchnote page (a `sketch` job in `tools/authoring/notes.py`:
title, subtitle, box, flow, list title, bullets). Write its JSON by these rules. In practice: the box says what the
whole chapter teaches; the flow is the chapter's main idea as a general process (`messy text -> strip -> split ->
capitalise -> join`, never `riya SHARMA -> Riya Sharma`); the bullets are the key takeaways; no sample values, no
names from the running project's data, no numbers that only belong to one example. A code name stays when it is
the concept the chapter teaches (`equals`, `async`).

**1. Focus on the chapter summary.**
- Present only a **general, conceptual summary of the chapter**.
- Capture the main ideas, fundamental concepts, important principles, and key takeaways.
- The reader should understand what the entire chapter is about just by looking at the sketchnote.
- Cover the chapter's core learning objectives without introducing unrelated information.

**2. Do not include example-specific data.**
- Do not include artificial example data, sample values, fictional scenarios, dummy datasets, or illustrative case studies.
- Do not invent examples to fill empty space.
- Do not introduce information that was not part of the chapter.
- Focus on explaining concepts, not demonstrating them through unrelated examples.

**3. Make it a meaningful learning reference.**
- Every element should contribute to understanding the chapter.
- Use concise explanations, keywords, conceptual relationships, and relevant visual representations.
- Highlight how the different concepts connect to one another.
- Avoid unnecessary decorative content or filler.

**4. Content accuracy.**
- Base the sketchnote entirely on the lesson or chapter content.
- Do not hallucinate, expand into unrelated topics, or add external information.
- Preserve the original meaning of the concepts.

**5. Optimize for image generation cost.**
- Image regeneration is expensive.
- Make the first generation as accurate and complete as possible.
- Prioritize content relevance, conceptual clarity, and information density over decorative creativity.

**Golden rule.** The sketchnote must communicate what the entire chapter teaches, not showcase random examples or
invented data. Someone who has never read the chapter should be able to look at the sketchnote and grasp its overall
subject, major concepts, and key takeaways.
- Cost: OpenAI, medium quality, about $0.04 a page; approved by the owner for covers and notes only.

## 10. Cover, colour, track

- Cover: the real logo on its brand colours, `scripts/labbox cover <lab> --logo <tech>[,<tech>]`. A missing
  logo goes into `tools/logos/` with its colours in `BRANDS` (`tools/logo_cover.py`).
- The lab's colour (the Continue card, the course page): `LAB_TONES` in `frontend/src/brand.ts`.
- Track data: add the lab's chapters to its track in `tracks/<track>.yaml`.
- A new lab joins the `test_test_lab` list in `backend/tests/test_cli.py`.

## 11. Prove it

```bash
scripts/labbox validate <lab> --strict         # shape, hints, pictures, files and lines, em dashes
scripts/labbox test-lab <lab>                  # the starter fails every task, the solution passes every task
cd backend && LABBOX_TEST_DATABASE_URL=... LABBOX_TEST_REDIS_URL=... .venv/bin/pytest    # the full run
cd frontend && npm run test:e2e                # the browser tests
```

Then restart the backend (content is loaded at start-up) and read every chapter in the browser: the text
size, both themes, every photo and diagram, every `file=` step opening the right lines, and a phone width
(the reading mode). Check `scripts/labbox admin list` is empty.

## 12. Record it

- One commit per part (or per step), with a clear message ending in the attribution line. Commit locally; the
  owner pushes.
- `CHANGELOG.md`: a dated entry, newest first: what the part teaches, what real measurements it found, the
  photos, notes and diagrams it added.
- `ROADMAP.md`: the course's row in the labs table (chapters, tasks, hours, project, standard).
- `HANDOFF.md`: where the work stopped and what waits for the owner.
- `AGENTS.md`: "Where we are" and the last known test state.
