# Lesson rewrite list

Every lab is rewritten to the owner's lesson rules (25 November): easy and a little detailed, plain, every term and
number explained where it first appears, model- or data-specific facts labelled, every claim recomputed with the lab's
real code and data, still pictures with real numbers, new notes pages. The rules: `memory: lesson-rewrite-rules`.
After each lab: stop, tell the owner, do the owner's small tasks, then the next lab. What was wrong and fixed in each
chapter is in `CHANGELOG.md`.

Status: **7 of 23 labs done** (164 of 319 chapters).

| # | Lab | Title | Chapters | Status | Done on |
|---|---|---|---|---|---|
| 1 | rag-vector-databases | RAG and vector databases | 13 | done (13 of 13) | 25 Nov |
| 2 | langchain | LangChain | 27 | done (27 of 27) | 25 Nov |
| 3 | langchain4j | LangChain4j | 30 | done (30 of 30) | 26 Nov |
| 4 | langgraph | LangGraph | 24 | done (24 of 24) | 26 Nov |
| 5 | spring-ai | Spring AI | 20 | done (20 of 20) | 26 Nov |
| 6 | spring-boot-first-api | Spring Boot | 31 | done (31 of 31) | 28 Nov |
| 7 | python-basics | Python from zero | 19 | done (19 of 19) | 28 Nov |
| 8 | java-basics | Java from zero | 18 | in progress (1 of 18) |  |
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

- 28 Nov: Java ch 1 done: every output re-run on a lab machine; terms explained; slips with javac's real messages; sketchnote.
- 28 Nov: Python ch 19 done: a promised non-existent course replaced by real ones; the enumerate line-number slip found ([15, 23, 31]); sketchnote. PYTHON LAB DONE (19 of 19); validate passes; test-lab green.
- 28 Nov: Python ch 18 done: argparse outputs and exit codes re-run; slips tried; sketchnote (redrawn once). Part 3 complete.
- 28 Nov: Python ch 17 done: Apollo 11 alarms made exact; pytest output re-run; slips (which amounts catch which planted bug); sketchnote.
- 28 Nov: Python ch 16 done: to_paise rounding pointed at the real trap (0.29); pip and venv tried on the machine; slips; sketchnote.
- 28 Nov: Python ch 15 done: class slips tried with real messages; Java pointer exact; sketchnote (redrawn once: underscores).
- 28 Nov: Python ch 14 done: the empty-category row (line 32) found and explained; CSV lines accounted for; TypeError for short rows taught; sketchnote (redrawn once).
- 28 Nov: Python ch 13 done: Mars Climate Orbiter made exact; from None shown; the 1,200 answered; slips; sketchnote.
- 28 Nov: Python ch 12 done: rule errors quoted; three-calls-one-list curiosity taught; slips tried (rupees vs percent, if not basket); sketchnote. Part 2 complete.
- 28 Nov: Python ch 11 done: card sorter explained; the lucky reverse=True sort found and taught (stable sort); slips tried; sketchnote.
- 28 Nov: Python ch 10 done: set-vs-list timing re-measured and explained (0.025 ms vs 827 ms); set order claim qualified; slips tried; sketchnote.
- 28 Nov: Python ch 9 done: speed claim measured (0.020 s vs 0.026 s per million lookups); slips tried; sketchnote (redrawn once).
- 28 Nov: Python ch 8 done: jukebox corrected; errors quoted; shallow copy shown; slips tried (incl. [-0:]); sketchnote.
- 28 Nov: Python ch 7 done: upper and replace taught (the recap promised them); outputs re-run; slips tried; UTF-8 bytes counted; sketchnote (redrawn once).
- 28 Nov: Python ch 6 done: relays explained; pdb session re-run line by line; slips tried; sketchnote. Part 1 complete.
- 28 Nov: Python ch 5 done: Jacquard loom explained; outputs re-run; slips tried (>=, return in loop, else: return None); sketchnote.
- 28 Nov: Python ch 4 done: Unicode order explained; precedence shown; calendar drift made exact; slips tried; sketchnote.
- 28 Nov: Python ch 3 done: every number and format re-run; floating-point and // explained plainly; slips with real messages; sketchnote.
- 28 Nov: Python ch 2 done: story order fixed; Ada claims hedged; outputs re-run; -7 % 2 and unchecked type hints taught; slips; sketchnote.
- 28 Nov: Python ch 1 done: every output re-run on a lab machine; terms explained at first use; timeline made exact; slips with real messages; diagram step 2 qualified; sketchnote.
- 28 Nov: Spring Boot lab DONE: 31 of 31; validate passes; test-lab green; ROADMAP and HANDOFF updated.
- 28 Nov: Spring Boot ch 30 done: checkout answers quoted; five promises of a non-existent 'production course' (ch 15, 22, 23, 28, 30) reworded; sketchnote. SPRING BOOT LAB DONE (31 of 31).
- 28 Nov: Spring Boot ch 29 done: supplier calls re-run (120, 0, 503 in 1.005 s, 503 when down); 200 threads made exact; slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 28 done: CSRF-on DELETE is 401 not 403 (tried; text, tip, quick check fixed); anyRequest order and {noop} tried; full 401 headers quoted; sketchnote.
- 28 Nov: Spring Boot ch 27 done: println, WARN line and Actuator answers quoted from real runs; 8082 sample line replaced; health-path explained; slips; sketchnote.
- 28 Nov: Spring Boot ch 26 done: data test run; slice start 1.563 s; AssertJ's real failure quoted; slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 25 done: starter/solution tests run; slice start 1.282 s; the real failure output quoted; slips; sketchnote.
- 28 Nov: Spring Boot ch 24 done: Flyway lines quoted; one-underscore file tried (silently skipped, V3 fails); stale target/ copy found and taught (clean after rename); sketchnote (redrawn once). Part 3 complete.
- 28 Nov: Spring Boot ch 23 done: half-done order and declined card re-run before and after; key order said; proxy explained; slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 22 done: page JSON, both queries, price range quoted from real runs; VIA_DTO setting explained; slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 21 done: N+1 measured (6 queries -> 1); Hibernate 6 'distinct' behaviour corrected (tried); lazy 'by default'; n-plus-one picture; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 20 done: starter 500 + H2 message, solution queries and 409/201, misspelling error all quoted from real runs; index explained; slips; sketchnote.
- 28 Nov: Spring Boot ch 19 done: starter failure, Hikari lines, create table and query quoted from real runs; RAMAC comparison made exact; slips; sketchnote.
- 28 Nov: Spring Boot ch 18 done: headers re-run; quick check 'no handler for unmapped path' corrected (interceptor on /** ran via BasicErrorController); slips; sketchnote (redrawn once). Part 2 complete.
- 28 Nov: Spring Boot ch 17 done: 500/404/400 answers re-run; 'any unhandled exception is 500' corrected; field order varies (3 runs); slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 16 done: starter/solution re-run; real validation log; '400 with every field' corrected (only the log has them); slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 15 done: PUT/PATCH answers and 404s re-run; a false forward reference (ch 21 soft delete) replaced by the reason; slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 14 done: outputs confirmed; average()/OptionalDouble and repository-query slips added (checked against Ch14's check); sketchnote.
- 28 Nov: Spring Boot ch 13 done: starter/solution statuses quoted; the missing-.build() compile error quoted exactly; slips; sketchnote.
- 28 Nov: Spring Boot ch 12 done: every body case re-run; real 415/400 log lines quoted; missing-field default shown; slips; sketchnote.
- 28 Nov: Spring Boot ch 11 done: all searches and errors quoted; null -> 200 empty and int+required=false -> 500 tried; hidden 404 message explained; slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 10 done: TRACE routes and request lines quoted from a real run; 406 headers; 200 threads made exact (lesson and animation); slips; sketchnote.
- 28 Nov: Spring Boot ch 9 done: ApplicationRunner order corrected (after Started); starter/solution/shutdown outputs quoted; capital-P scope slip tried (500); sketchnote.
- 28 Nov: Spring Boot ch 8 done: failure, replies and debug entries quoted from real runs; 153 auto-configurations counted; exposure.include wording fixed; slips; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 7 done: every settings source re-run; env var quick check fixed (SHOP_ prefix); both env spellings tried; Map key order said; Dunzo -> made-up Pheri Couriers; slips; sketchnote.
- 28 Nov: Spring Boot ch 6 done: real failure block incl. the parameter-name line (explained, tried); two-@Primary error checked; recap's 'more than one stops start-up' qualified; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 5 done: 158 beans measured (6 ours); real missing-bean error; starter/solution answers confirmed; slips added; 'by default' kept on singleton; sketchnote (redrawn once).
- 28 Nov: Spring Boot ch 4 done: animation's 'sees the starter in your pom' corrected (classpath); real start-up log; real placeholder error; real debug report wording; slips added; sketchnote (redrawn once for a lost qualifier).
- 28 Nov: Spring Boot ch 3 done: 'path must start with /' corrected (Spring adds it); browsers-send-only-GET corrected; records' accessors named; slips added; first-endpoint picture; sketchnote.
- 28 Nov: Spring Boot ch 2 done: dependency:tree command fixed (-Dscope=compile; -Dexcludes did not hide the test starter); phases said honestly; jar and Actuator re-measured; port-in-use slip added; fat-jar picture; sketchnote.
- 28 Nov: Spring Boot ch 1 done: every curl re-run; 405's Allow header corrected (DELETE, GET); search URL answers 400 (said); double-POST slip warned; new http-conversation picture; sketchnote.
- 28 Nov: Spring Boot ch 0 done: versions, start-up lines, 404 reply re-measured on a lab machine; three half-true claims fixed (support length, old code runs, Pivotal/VMware); timeline + Boot 3.4; sketchnote.
- 27 Nov, morning: FDE Part 6 (chapters 21 and 22: handover, second customer). Course complete: 22 chapters, 44 tasks. Real runs: the smoke test passes 3 of 3 through the gateway, and a limit of 10,000 fails it on E-01 (exit 1); a bad start lists every problem with no secret shown. Chapter 22 needs no model (the second insurer sends CSV): an adapter plus rules from per-customer config. 2 photos (relay baton, container port), 2 notes; test-lab green (44 tasks).
- 27 Nov, morning: FDE Part 5 (chapters 17 to 20: privacy and prompt injection, reliability, shadow mode, monitoring). Real findings: E-30's loud injection failed but two quiet ones made the model record Rs 1,00,000 (and turn an accident into a fire), stopped only by the pilot limit in code; a paced batch of 30 had 0 failures in 93 s (15 of 30 failed unpaced), cached rerun 0 calls; shadow drafts from the real run found an unspoken rule (thefts always go to investigation). Monitoring log simulated from the 109 real call latencies. 4 photos (blue box, Wilkes, Model 299, Mission Control), 4 notes; test-lab green (40 tasks).
- 27 Nov, morning: FDE Part 4 (chapters 14 to 16: golden set, evals and a regression gate, failure analysis) built on two real 30-email runs. Findings taught: prompt v2 raised all-fields 73.3% to 80.0% but dropped dates 83.3% to 80.0% (the gate refuses it); telling the model today's date did not fix the 2023 years and made it invent dates from "yesterday"; code fixes lift v1 to 93.3% with nothing worse. 3 photos (NIST kilograms, go/no-go gauge, Nightingale), 3 notes; test-lab green (32 tasks).
- 27 Nov, morning: FDE Part 3 (chapters 8 to 13: gateway and cost, extraction, cited answers, tools, MCP server, day-five demo) built and captured against the real model through the gateway (author account). Real findings now taught: dates without a year came back as 2023; the model said a policy was not in force on a date inside its period; 15 of 30 calls hit the gateway's rate limit. 4 photos, 6 notes; test-lab green.
- 27 Nov, 05:30 IST: live site deployed (aec912d: Google and GitHub only, certificates); the owner's live account linked to their email. FDE Part 2 (chapters 4 to 7: messy data, database and SQL injection, legacy XML with backoff, data contract) built with 4 photos and 4 notes; test-lab green.
- 27 Nov, night: NEW COURSE Forward Deployed Engineer (owner asleep, approved unattended): research done (Wikipedia, a16z, OpenAI and Anthropic postings, Udemy/fde.academy/FDE Masters syllabi); 22 chapters planned; Part 1 (chapters 1 to 3) built: code, checks, lessons, 3 photos, 3 notes pages; test-lab green.
- 26 Nov, 04:20 IST: LangGraph done (24 of 24), unattended (owner asleep); test-lab green; test machines removed; no
  admins; nothing pushed.
- 26 Nov: LangGraph ch 24 done: the desk re-run on a server (same Thursday booking); quiz and both slips tried.
- 26 Nov: LangGraph ch 23 done: facts checked in the sources; re-run hit the review's second exit (uncited recommendation twice), now taught.
- 26 Nov: LangGraph ch 22 done: same wrong ages reproduced; quiz corrected (no permission: it still asked the analyst); virtual_mode off could read /etc.
- 26 Nov: LangGraph ch 21 done: quiz corrected (langgraph dev keeps threads across a restart, in .langgraph_api); server refusal reproduced.
- 26 Nov: LangGraph ch 20 done: tests and the planted bug reproduced; the weak test passes with the bug.
- 26 Nov: LangGraph ch 19 done: runs reproduced; quiz and both slips tried (Future not serializable; refused job still booked).
- 26 Nov: LangGraph ch 18 done: timings re-measured (first token 2.22 to 2.50 s); a node with a stream writer fails outside a run; slips tried.
- 26 Nov: LangGraph ch 17 done: double booking not reproduced in 2 runs; the suggested task-only fix tried: it invented a phone number (now taught).
- 26 Nov: LangGraph ch 16 done: output reproduced; quiz and two slips tried; 'four times' corrected to 3.9.
- 26 Nov: LangGraph ch 15 done: four paths reproduced; a missing rewrite counter tried (27 calls until stopped).
- 26 Nov: LangGraph ch 14 done: both runs handed over; three fixes tried (date for writer, date for both, copy days from tools: only the last worked).
- 26 Nov: LangGraph ch 13 done: agent took 2 different paths in 3 runs (now taught); ToolNode error default corrected; slips tried.
- 26 Nov: LangGraph ch 12 done: found store search embeds the value's JSON (0.59 vs 0.63); fields option taught; three slips tried.
- 26 Nov: LangGraph ch 11 done: history reproduced and pictured as branches; two slips tried; as_node optional here, noted.
- 26 Nov: LangGraph ch 10 done: invented brief reproduced and the fix tried; resume needs the checkpointer, not the pause; plain-dict resume tried.
- 26 Nov: LangGraph ch 9 done: retry waits measured (jitter adds up to 1 s, now taught); runs reproduced; quiz and slip tried.
- 26 Nov: LangGraph ch 8 done: re-run shown with a token chart; start_on can keep 3 of 4; three slips tried.
- 26 Nov: LangGraph ch 7 done: conversation reproduced; both slips tried and quoted; a top-level thread_id works in 1.2.24.
- 26 Nov: LangGraph ch 6 done: output reproduced; quiz and four Send/Command mistakes tried; the Literal return type shown to fix the diagram.
- 26 Nov: LangGraph ch 5 done: fixed a wrong weekday in the lab's notice facts; grader missed the area 3 of 4 runs; joins measured.
- 26 Nov: LangGraph ch 4 done: run reproduced with the real model; found returning a Pydantic object works; two real slips tried.
- 26 Nov: LangGraph ch 3 done: default recursion limit is 10,007 in 1.2.24 (measured); five branch mistakes tried and quoted.
- 26 Nov: LangGraph ch 2 done: found the reducer's first call gets an empty string; both slips tried.
- 26 Nov: LangGraph ch 1 done: output reproduced; a missing middle edge gives no error and no reply; values vs updates tried.
- 26 Nov, 02:50 IST: LangChain4j done (30 of 30); test-lab green (every starter fails, every solution passes); test
  machines removed (26 machines, 13 networks); no admins; Ollama stopped again. Owner: Setu keeps its name.
- 26 Nov: LangChain4j ch 30 done: live app reproduced word for word (usage identical); guardrail bug reproduced; distinct slip tried.
- 26 Nov: LangChain4j ch 29 done: 420 and 840 reproduced, 7 calls confirmed; LAST and a missing tool tried (OutputParsingException).
- 26 Nov: LangChain4j ch 28 done: overlap quiz corrected (either reply may win, 5 runs); null answer with no desk and the 6-call ceiling tried; default ceiling is Integer.MAX_VALUE.
- 26 Nov: LangChain4j ch 27 done: run reproduced (the REFUND capitals leak again); quiz and both slips tried (Missing argument: topic); module is beta, now said.
- 26 Nov: LangChain4j ch 26 done: regression re-run 4 times (2 invented, 2 honest but failed the check); what was removed and the token counts corrected.
- 26 Nov: LangChain4j ch 25 done: guardrail-off case re-run 4 times (3 copied the number); 48 corrected to 47; failure, fatal and successWith chaining checked.
- 26 Nov: LangChain4j ch 24 done: Ollama started for the check and stopped again; local answer reproduced; default-route claim and a missing class name corrected.
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
