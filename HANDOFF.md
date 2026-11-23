# Handoff: where the work stands (23 November 2026)

Read this first when a session starts. `AGENTS.md` has the rules and how to run and test, `ROADMAP.md`
the status of every lab and phase, `CHANGELOG.md` the history (newest first), `CONTENT_STANDARD.md` what a
course must be, and `COURSE_PRODUCTION.md` how one is built. This file is only the short "resume here" note:
update it at the end of every session. Earlier, longer versions of it are in git history.

## Resume here

- **State:** the working tree is clean after each commit; local commits wait for the owner to push.
  Last full run green (24 November, after Rust from zero): 283 backend tests on Postgres and Redis (29 minutes),
  27 browser tests (the visitor home test failed once under 4 workers and passed on its own), 22 labs valid,
  `scripts/labbox admin list` empty.
- **Just finished:** Rust from zero (`rust-basics`, owner 24 November: "make a complete full standard lab on Rust";
  project name rule: software gets a plain English name for its job, so Windwatch). Complete: 28 chapters in 6 parts,
  56 tasks; Part 6 is a clap CLI, Box/Rc/RefCell, threads and channels, Tokio, speed against Python and an axum
  capstone. Checks: tests/run_checks.py (modes run, test, own) with one shared target dir prebuilt in the image, so a
  check compiles only the learner's crate. Next: the full test run, then wait for the owner's next course.
- **Working files:** the session scratchpad was lost when the laptop restarted (23 November, 19:16; /tmp is RAM), so
  the generator drafts are gone; the committed folders are the record. Part 5 is written straight into the lab.
  Captures need a new gateway token for the author account `navin-author` (tools/authoring/author_token.py).

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
`diagram-themes.spec.ts` (arrowhead check). A blank lab page with `net::ERR_NETWORK_CHANGED` is this laptop.

## Editing CHANGELOG.md safely

Add new entries at the top, under `# Changelog`. Never open a file for writing and reading in one
expression (Python's `open(f, "w").write(open(f).read())` empties the file first).

## Known gaps

- The VS Code explorer shows the lab name as a heading with `workspace` one level below (from the per-lab
  workspace file). Harmless; could be flattened later.
- Handwritten notes pages are stored as generated (1536 by 1024, about 1.7 MB each); they could be shrunk.
