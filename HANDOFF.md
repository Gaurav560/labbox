# Handoff: where the work stands (25 November 2026)

Read this first when a session starts. `AGENTS.md` has the rules and how to run and test, `ROADMAP.md`
the status of every lab and phase, `CHANGELOG.md` the history (newest first), `CONTENT_STANDARD.md` what a
course must be, and `COURSE_PRODUCTION.md` how one is built. This file is only the short "resume here" note:
update it at the end of every session. Earlier, longer versions of it are in git history.

## Resume here

- **Design comparison (owner, 24 and 25 November): two copies of the site, same backend.** The current design on
  `master` at http://localhost:5173; the "Ukiyo" design (Japanese woodblock prints and Swiss editorial layout) on
  branch `design/ukiyo` in the worktree `../labs_poc_ukiyo`, at http://localhost:5174 (start it with
  `cd ../labs_poc_ukiyo/frontend && npx vite --port 5174 --strictPort`; restart it when a page goes blank with
  "export not found", which happened several times). About 75 commits there; `DESIGN_UKIYO.md` on that branch is
  the full record. On 25 November the owner reworked Ukiyo screen by screen: every lab has its own woodblock print;
  calm public-domain Hiroshige prints for the six categories; a new home page (hero "The AI wave is here. Learn to
  build AI apps, or get left behind." with "No fluff. No tutorial hell. Only action."; a "start a lab" section where
  a Docker-style container loads a lab's real stack and starts, picked from nine options and refined at length; a
  folding screen of categories; Mount Hira closing panel); Plum Garden on login; a classy profile panel; real logos.
  The branch is not pushed yet (owner pushes: `git push -u origin design/ukiyo`). **Waiting for the owner to keep
  one.** Keep: merge `design/ukiyo` into `master` (frontend only). Before merging, check: the Docker whale's brand
  use; the "58 s / about a minute" claim measured on the AWS server (5 s on this laptop, images cached); whether
  "AI code assistant" should say "AI tutor" (editor completion is still off). Drop: `git worktree remove
  ../labs_poc_ukiyo` and delete the branch. Until then, frontend changes on `master` need the same change on the
  branch (they were copied by hand all through 25 November).
- **Also on 25 November, on both copies:** pages open at their top; the AI labs link logs in first and lands on the
  AI labs (`/login?next=`); a light and dark switch on the login page; the sign-up "first win" line and the footer's
  Premium Reads link are gone; the course page map is headed "Skill map"; the lesson's faint logo stands straight.
  Premium Reads: the papers open with the history of language models (migration 0012), sharp 800 px book covers,
  no "Start here" label. Master is pushed (last: bb06176).
- **State:** the working tree is clean after each commit; local commits wait for the owner to push.
  Last full run green (24 November, after RAG and vector databases): 284 backend tests on Postgres and Redis
  (30 minutes), 27 browser tests, 23 labs valid, `scripts/labbox admin list` empty. On 25 November: 235 backend
  tests without Docker on Postgres and Redis after migration 0012, and the browser tests for each change on both
  copies (a few failed only while Vite reloaded mid-test and passed on rerun).
- **Latest (25 November, night):** the LangChain lab rewritten, all 27 chapters, the same way as RAG (one commit per
  chapter, each on `design/ukiyo` too). Lab valid, test-lab green, test machines cleaned, no admins. Real findings are
  in CHANGELOG (for example: a misspelled tool name in `interrupt_on` books without the manager; the gateway's 20 calls
  a minute stops a second eval run). REWRITE_LIST: 2 of 23 labs done. Ukiyo's logo now reads "by TELUSKO". Waiting
  for the owner's small tasks, then the next lab (owner picks; LangChain4j is next in the list).
- **Latest (25 November, evening):** steps are "scenes"; Read mode's scene list (closed by default); Action mode
  hides the lesson panel; Start machine in the Machine menu. Waiting for the owner's next small task or next lab.
- **Latest (25 November, after the RAG rewrite):** Read mode and Action mode in every lab (CHANGELOG has the
  details); browser tests clean up their own machines (`scripts/labbox test-accounts`).
- **Just finished (25 November):** the RAG lab rewritten chapter by chapter to `memory: lesson-rewrite-rules` (easy, a
  little detailed, every number recomputed in the lab image, model-specific facts labelled, still pictures with real
  numbers, new notes pages). Errors found and fixed are listed per chapter in CHANGELOG. Checks: lab valid, test-lab
  green, 232 fast backend tests, 31 browser tests (one flaky, passed on rerun). The owner's rule now: stop after each
  lab and wait for small tasks. Next lab: the owner chooses (estimate: about 50 hours for all, or 12 to 15 for a
  correctness-only pass).
- **Before that:** RAG and vector databases (`rag-vector-databases`, owner 24 November night, built without waiting
  for an OK as asked): 13 chapters in 3 parts, 26 tasks, Fieldbook. Syllabus and design below. Generator drafts in the
  session scratchpad (`rag/gen.py`, `blocks.py`, `scripts.py`); the committed folders are the record. Before it: Rust
  from zero, complete (28 chapters). Photos still to add: Spärck Jones (RAG ch 9), Peyton Jones and Stroustrup (Rust);
  see ROADMAP B.5. Next: wait for the owner.
- **Parked by the owner (24 November, "keep it saved, we will think about it later"):** lesson readability. Proposed:
  move the lab-logo watermark (`.lesson-watermark`) out from behind the text; soften dark-theme text from `#f0f3f1` to an
  off-white; tables at 15px with roomier cells; fold the task bar to one line on reading steps; more space between
  paragraphs; 17px by default on large screens. Show before and after screenshots in both themes when it comes back.
- **Working files:** the session scratchpad was lost when the laptop restarted (23 November, 19:16; /tmp is RAM), so
  the generator drafts are gone; the committed folders are the record. Part 5 is written straight into the lab.
  Captures need a new gateway token for the author account `navin-author` (tools/authoring/author_token.py).

## RAG and vector databases (new lab `rag-vector-databases`, owner 24 November night): Fieldbook, complete

Owner, going to sleep: "build a micro lab in python for rag and vector databases. easy to understand, world class.
... draft a world class syllabus and then start implementing it. with full standard." Built without waiting for an OK.

Research (24 November): DeepLearning.AI's short courses (Vector Databases with Weaviate, Advanced Retrieval with
Chroma), IBM's RAG: Vector Databases and Retrievers, Udemy and O'Reilly courses on HNSW, IVF, PQ, hybrid search and
reranking. They split into "use a vector store" courses and "index internals" courses; few do both, and fewer measure
anything. This lab builds each piece by hand first, measures it, then uses the real tool. The LangChain course
already uses vector stores through LangChain; this lab goes underneath.

Running project: **Fieldbook**, the question-answering assistant for rangers of the fictional Vanrai Hills Wildlife
Sanctuary in the Western Ghats: its field manual (zones, patrols, camera traps, encounters, fire, permits) and
patrol reports. Everything runs offline and free: embeddings with BAAI/bge-small-en-v1.5 and reranking with
Xenova/ms-marco-MiniLM-L-6-v2 through fastembed 0.9.1 (both in the image), FAISS 1.16, Qdrant's Python client
1.20 in local mode; only answers call the model (lab-chat through the gateway; checks use the fake server).

| Part | Ch | id | Idea | Tasks |
|---|---|---|---|---|
| Retrieval from scratch | 1 | why-rag | a model does not know your documents; keyword search; context in the prompt | keyword_search, context_prompt |
| | 2 | embeddings | text as 384 numbers, on your own CPU; cosine similarity | embed_texts, cosine |
| | 3 | vector-search | brute-force nearest neighbours with one matrix product; measured to 300,000 vectors | normalize, top_k |
| | 4 | chunking | word windows with overlap, sections with titles; hit rate by chunk size | word_chunks, section_chunks |
| Inside a vector database | 5 | ivf | clusters first: k-means and inverted lists; recall against nprobe | build_lists, ivf_search |
| | 6 | hnsw | graphs: HNSW with FAISS; recall, efSearch, build time and memory | recall_at_k, tune_ef |
| | 7 | quantization | int8 and binary vectors, rescoring; memory and money | quantize_int8, binary_rescore |
| | 8 | qdrant | a real vector database: collections, points, payloads, filters | make_store, filtered_search |
| RAG that works | 9 | hybrid | BM25 by hand, reciprocal rank fusion | bm25_scores, rrf_fuse |
| | 10 | rerank | a cross-encoder reads question and chunk together | rerank, two_stage |
| | 11 | grounded-answers | numbered sources, citations, refusing when retrieval is weak | grounded_prompt, refuse_unsure |
| | 12 | evaluation | golden questions, hit rate and MRR for four pipelines | hit_rate, mrr |
| | 13 | capstone | Fieldbook as a FastAPI service: /search with filters, /ask with sources | search_endpoint, ask_endpoint |

## LangChain (new lab `langchain`, owner 23 November): Navin, a farmers' co-op help desk

Syllabus from docs.langchain.com (LangChain 1.5.2, langchain-core 1.8.4, langchain-openai 1.8.5, LangGraph 1.2.24,
OpenAI SDK 3.57, Python 3.12) and a scan of what others teach (LangChain Academy, DeepLearning.AI, Udemy, Coursera,
freeCodeCamp). Running project: **Navin**, the help desk of the fictional Pimpalgaon Farmers' Cooperative near Nashik
(onions, grapes, tomatoes; mandi rates, cold storage, crop loans, a spraying rule). Image `labbox/langchain:v1`
(FROM ai-python; `warm/requirements.txt` pins all 109 packages; tiktoken encodings in /opt/tiktoken). Checks are
pytest with a fake OpenAI server, about a second a chapter. Captures use the author account `navin-author`.

- Part 1 "How language models work" (plain Python): 1 `ai-basics`, 2 `tokens`, 3 `embeddings` (real 256-dimension
  vectors in vectors.json), 4 `transformers`. Done.
- Part 2 "Calling a model": 5 `raw-http`, 6 `openai-sdk`, 7 `first-app`, 8 `parameters`, 9 `hallucinations`. Done.
- Part 3 "Agents": 10 an agent loop by hand, 11 `create_agent`, 12 tools and ToolRuntime, 13 structured output,
  14 images (multimodal messages), 15 short-term memory, 16 streaming agents. Done.
- Part 4 "Knowledge and MCP": 17 documents and chunking, 18 vector stores, 19 RAG, 20 retrieval quality, 21 MCP. Done.
- Part 5 "Production": 22 built-in middleware, 23 custom middleware and dynamic agents, 24 guardrails and PII,
  25 human in the loop, 26 tests and evals, 27 capstone (FastAPI, with long-term memory). Done.

LangGraph (new lab `langgraph`, after LangChain): **Harsh**, a city water utility's complaint-to-repair desk. 24
chapters: thinking in graphs (6), persistence and people (6), agents in graphs (7), production (5, with Deep Agents
and a capstone). Full list in the chat of 23 November and CHANGELOG.
Image `labbox/langgraph:v1` (FROM labbox/langchain:v1, `warm/requirements.txt` adds deepagents, the SQLite checkpointer and their dependencies). Checks reuse
`tests/common/fake_openai.py`; `tests/run_checks.sh` has a CHAPTERS table (id|folder|tasks). Captures use a gateway
token for an author account made with `tools/authoring/author_token.py`, and `tools/authoring/capture.sh`.

- Part 1 "Thinking in graphs": 1 `why-graphs`, 2 `state`, 3 `branches`, 4 `model-nodes`, 5 `patterns`,
  6 `send-command`. Done.
- Part 2 "Persistence and people": 7 checkpointers and threads, 8 trimming and summarizing, 9 durable execution,
  10 interrupts, 11 editing state and time travel, 12 stores. Done (folders 07-threads to 12-stores).
- Part 3 "Agents in graphs": 13 an agent graph by hand, 14 reflection, 15 agentic RAG, 16 subgraphs, 17 multi-agent,
  18 streaming, 19 the Functional API. Done (folders 13-agent-graph to 19-functional-api).
- Part 4 "Production": 20 testing graphs, 21 a local server and app structure, 22 Deep Agents, 23 a research team,
  24 capstone. Done (folders 20-testing to 24-capstone; chapters 21 and 24 run `langgraph dev` in the checks).

## LangChain4j (new lab `langchain4j`, owner 23 November): complete, 30 chapters, 60 tasks

All five parts are built, checked (`test-lab`: starter fails all 60 tasks, solution passes all) and committed,
with 12 real photos: at the full standard.

Owner: "start with new ai lab: LangChain4j ... fetch everything from the url (docs.langchain4j.dev) ... create a world
class lab, go on". Syllabus = the Telusko LangChain4j video's chapter list + the official tutorials, at the current
version: LangChain4j 1.24.0 (agentic, MCP, Spring Boot starter, easy RAG: 1.24.0-beta34), OpenAI Java SDK 4.111.0,
Java 21, Spring Boot 4.2 for the web chapters. Models through the gateway: `ai-chat` (gpt-4o-mini), `ai-embed`.
Running project: **Setu**, the passenger help desk of **Sahyadri Rail**, a fictional hill railway from Pune down
the Western Ghats to the Konkan coast (trains, stations, timetables, fares, rules for luggage, refunds and pets).
A folder per chapter (`NN-id/`, Maven), checks are JUnit with a fake model server (no network, no cost).

- Part 1 "How language models work" (plain Java, no AI library, no API calls): 1 AI, ML, deep learning and
  generative AI (`ai-basics`), 2 Neural networks: a neuron in Java (`neurons`), 3 From NLP to language models: a
  bigram model that predicts the next word (`language-models`), 4 Tokens and the context window (`tokens`),
  5 Embeddings, vectors and dimensions (`embeddings`), 6 Transformers and attention, and how an LLM answers
  (`transformers`).
- Part 2 "Calling a model from Java": 7 A model over plain HTTP (`raw-http`), 8 The official OpenAI Java SDK
  (`openai-sdk`), 9 Your first LangChain4j app (`first-app`), 10 Model parameters and messages (`parameters`),
  11 Open and closed models, and hallucinations (`hallucinations`), 12 Response metadata and token usage (`usage`).
- Part 3 "AI Services": 13 AI Services (`ai-services`), 14 Prompt templates (`templates`), 15 Structured output
  (`structured`), 16 Streaming (`streaming`), 17 Chat memory (`memory`), 18 An AI REST API with Spring Boot (`rest-api`).
- Part 4 "Tools, MCP and knowledge": 19 Tools (`tools`), 20 MCP: use a filesystem MCP server (`mcp-client`),
  21 Build your own MCP server in Java (`mcp-server`), 22 Embedding models and stores (`embedding-stores`), 23 RAG
  (`rag`), 24 Local models with Ollama, and model routing (`local-models`).
- Part 5 "Production and agents": 25 Guardrails (`guardrails`), 26 Observability and testing (`observability`),
  27 Agents: your first agent and two agents in sequence (`agents`), 28 Agentic workflows: loop, parallel,
  conditional (`workflows`), 29 Supervisor agents (`supervisor`), 30 Capstone: Setu goes live (`capstone`).

## Waiting for the owner

1. **Drink examples are gone** (rewritten 23 November). Left on purpose: the SQL task id `q_paid_coffee` (progress
   hangs on it; renaming needs a data migration, ask first), the Java name history (now "a name borrowed from the
   island of Java"), and the owner's spec files (`labbox-v2-upgrade-spec.md`, `labbox-poc-spec.md`).
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
`diagram-themes.spec.ts` (arrowhead check), `course.spec.ts` (the `/skills` to `/courses` redirect, 24 November), `home.spec.ts` (expired login), `lab.spec.ts` (java steps, lesson pictures) and `engagement.spec.ts` (24 November, under a full 4-worker run; both pass alone). A blank lab page with `net::ERR_NETWORK_CHANGED` is this laptop.

## Editing CHANGELOG.md safely

Add new entries at the top, under `# Changelog`. Never open a file for writing and reading in one
expression (Python's `open(f, "w").write(open(f).read())` empties the file first).

## Known gaps

- The VS Code explorer shows the lab name as a heading with `workspace` one level below (from the per-lab
  workspace file). Harmless; could be flattened later.
- Handwritten notes pages are stored as generated (1536 by 1024, about 1.7 MB each); they could be shrunk.
