# Lesson rewrite list

Every lab is rewritten to the owner's lesson rules (25 November): easy and a little detailed, plain, every term and
number explained where it first appears, model- or data-specific facts labelled, every claim recomputed with the lab's
real code and data, still pictures with real numbers, new notes pages. The rules: `memory: lesson-rewrite-rules`.
After each lab: stop, tell the owner, do the owner's small tasks, then the next lab. What was wrong and fixed in each
chapter is in `CHANGELOG.md`.

Status: **3 of 23 labs done** (60 of 319 chapters).

| # | Lab | Title | Chapters | Status | Done on |
|---|---|---|---|---|---|
| 1 | rag-vector-databases | RAG and vector databases | 13 | done (13 of 13) | 25 Nov |
| 2 | langchain | LangChain | 27 | done (27 of 27) | 25 Nov |
| 3 | langchain4j | LangChain4j | 30 | in progress (23 of 30) | |
| 4 | langgraph | LangGraph | 24 | not started | |
| 5 | spring-ai | Spring AI | 20 | done (20 of 20) | 26 Nov |
| 6 | spring-boot-first-api | Spring Boot | 31 | not started | |
| 7 | python-basics | Python from zero | 19 | not started | |
| 8 | java-basics | Java from zero | 18 | not started | |
| 9 | javascript-basics | JavaScript from zero | 18 | not started | |
| 10 | go-basics | Go from zero | 18 | not started | |
| 11 | rust-basics | Rust from zero | 28 | not started | |
| 12 | redis-in-practice | Redis in practice | 17 | not started | |
| 13 | linux-on-call | Linux on call | 15 | not started | |
| 14 | sql-from-zero | SQL from zero | 14 | not started | |
| 15 | git-without-fear | Git without fear | 14 | not started | |
| 16 | python-collections | Python collections (short) | 2 | not started | |
| 17 | java-collections | Java collections (short) | 2 | not started | |
| 18 | javascript-inside-out | JavaScript inside out (short) | 2 | not started | |
| 19 | postgres-transactions-and-locks | Postgres: transactions and locks (short) | 2 | not started | |
| 20 | rate-limiter | System design: a rate limiter (short) | 2 | not started | |
| 21 | fastapi-first-api | FastAPI: your first API (short) | 1 | not started | |
| 22 | express-api | Express: an order tracking API (short) | 1 | not started | |
| 23 | postgres-indexing-incident | Postgres: the slow checkout (short) | 1 | not started | |

The order above is a suggestion (AI labs first, as LabBox is marketed as AI labs); the owner picks the next lab.

## Log (newest first)

Updated as work happens (owner, 26 November: "keep noting what we are doing"). One line per finished chapter, per
finding that changed code or content, and per small task. Details of each chapter are in `CHANGELOG.md`.

- 26 Nov: LangChain4j ch 23 done: answers and 107 tokens reproduced; no splitter tried (it lost the guitar rule); splitter chain corrected (lines).
- 26 Nov: LangChain4j ch 22 done: every score reproduced to 3 decimals; still score chart; two unchecked claims softened (store count, pgvector index type).
- 26 Nov: LangChain4j ch 21 done: quiz corrected (a stray stdout line did not break LangChain4j's client, but the spec forbids it); real wire traffic pictured; three slips that all give the same timeout.
- 26 Nov: LangChain4j ch 20 done: 14 tools wrong and 2 tools right, reproduced; both slips tried (a misspelled tool name gives no error).
- 26 Nov: LangChain4j ch 19 done: still tool-call picture from the real log; same token counts as the lesson.
- 26 Nov: LangChain4j ch 18 done: both slips tried; my first guess about @RequestBody was wrong and is corrected.
- 26 Nov: LangChain4j ch 17 done: found the system message counts toward the window (3 evicted, not 2); fixed the quiz.
- 26 Nov: LangChain4j ch 16 done: still streaming timeline; two fresh timings; API names checked.
- 26 Nov: LangChain4j ch 15 done: wrong date reproduced twice; a slip I wrote was tested and dropped ({{message}} works here).
- 26 Nov: LangChain4j ch 14 done: three template behaviours tried and quoted from real runs.
- 26 Nov: LangChain4j ch 13 done: still AI Service picture; output reproduced, proxy name included.
- 26 Nov: LangChain4j ch 12 done: corrected the system prompt size (24 tokens) and the quiz's cost ratio (25x, not 50x).
- 26 Nov: LangChain4j ch 11 done: the same wrong answers reproduced word for word at temperature 0; new still comparison picture.
- 26 Nov: LangChain4j ch 10 done: temperature 0 reproduced the lesson's slogan word for word, days later.
- 26 Nov: LangChain4j ch 9 done: API names checked in the 1.24 jar; steps and slips added.
- 26 Nov: LangChain4j ch 8 done: two more real runs; invention comes and goes, now said.
- 26 Nov: LangChain4j ch 7 done: still HTTP-call picture; the HTTP/2 failure, 401 and 400 all reproduced.
- 26 Nov: LangChain4j ch 6 done: two still pictures (attention weights, the six steps of an answer).
- 26 Nov: LangChain4j ch 5 done: still bar chart of real cosine scores; both quiz claims re-run.
- 26 Nov: LangChain4j ch 4 done: still context-window picture with real token counts; every token split re-checked.
- 26 Nov: LangChain4j ch 3 done: new still picture of the generated sentence with real counts.
- 26 Nov: LangChain4j ch 2 done: still neuron picture; XOR re-run (weights after 10 and 1,000 epochs are identical).
- 26 Nov: LangChain4j ch 1 done: still circles picture; found that 12 and 18 minutes tie (the tie rule picks 12).
- 26 Nov, 01:00 IST: Spring AI done (20 of 20); test-lab green; test machines removed. Next: LangChain4j (owner's
  order).
- 26 Nov: Spring AI ch 20: real bug fixed in the solution (privacy guard ran after session memory; a refused phone
  number was stored and then blocked every later question). Ch 17's sentence about order 0 corrected.
- 26 Nov: Spring AI ch 14: the pendulum card said 76 hours for Pune; the physics gives 75.4. Fixed in all ten copies.
- 26 Nov: Spring AI ch 12: the task asked learners to wait for a log line only the solution printed; now part of the
  task.
- 26 Nov: Spring AI ch 1 to 19 rewritten, one commit each, each copied to Ukiyo.
- 25 Nov, night: owner picked Ukiyo for now (final call after the deploy; keep both designs in sync).
- 25 Nov, night: notes pages become tall sketchnotes (owner's sample "What is RAG?"); `notes.py` "sketch" jobs; Read
  mode shows notes pages at full height. RAG and LangChain keep the older notes (40 pages to redraw on request).
- 25 Nov, night: Ukiyo logo reads "by TELUSKO" (owner).
- 25 Nov, night: LangChain done (27 of 27); test-lab green.
- 25 Nov: RAG done (13 of 13); small tasks: Read and Action modes, scenes, the scene list, Start machine in the menu.

## Checks in every rewrite

- Notes pages are tall sketchnotes (owner, 25 November night): title, subtitle, a definition box, a flow of 4 to 5
  boxes, a highlighted list of 3 to 4 lessons, made with a "sketch" job in `tools/authoring/notes.py`; every word
  checked. RAG and LangChain still have the older one-page notes (40 pages) to redraw.

- No drinks in any example (owner: never chai, tea or any drink): scan the lab's chapters, starter, solution, tests and
  data with `grep -rliwE "coffee|juice|tea|chai|latte|soda|espresso|cappuccino|lemonade|smoothie|milkshake" labs/<lab>`.
  On 25 November all 23 labs scanned clean. Note: a learner's workspace keeps the starter files it was created with
  (the owner's own JavaScript workspace still has the old "juice" and "Coffee" examples from before the 22 November
  rewrite); only "Reset lab" or a new account shows the current starter.

## Small tasks after each lab

- After RAG (25 Nov): the Ukiyo "LOADING" plate fixed; browser tests now clean up their machines; old test machines
  and folders removed; the model's answers in RAG chapters 11 and 13 re-run and matched; Read mode and Action mode added to every lab. Then: lesson steps renamed scenes; Read mode's
  scene list on the left (closed by default, sidebar button); Action mode can hide the lesson panel; Start machine
  moved into the Machine menu. Not kept: the three-column Read layout (reverted) and text size S at 95% (back to 90%).
