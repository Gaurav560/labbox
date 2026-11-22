# Changelog

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
