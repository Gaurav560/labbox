# Roadmap: what is left

What is done is in `CHANGELOG.md` and `git log`. This file is what is still to do, in order. The full
detail of every phase is in `labbox-v2-upgrade-spec.md` (section numbers below point there).

Rules that still apply: plan first and wait for an OK, one commit per step, all old tests stay green,
and ask before deleting data, touching AWS, or using anything that needs a paid API key.

## 1. Labs: 11 of 100+

Done (11): python-basics, java-basics, python-collections, java-collections, javascript-inside-out,
go-basics, sql-from-zero, fastapi-first-api, spring-boot-first-api, express-api,
postgres-indexing-incident.

Next batch (proposed, waiting for OK):
- Postgres transactions and isolation
- Postgres locks and deadlocks
- Redis in practice (needs a Redis service variant in the `service-incident` template)
- FastAPI CRUD with Postgres
- Linux on call
- SQL traps

Then, by track (spec section 8):
- Languages: Python traps, async Python, Java concurrency traps, JVM and memory incidents, Modern
  Java, TypeScript for real code, How Node really works, Go concurrency, Rust basics, Rust ownership
- Frameworks: Spring Data JPA, Spring validation and errors, Spring security with JWT, Spring testing,
  Spring Boot on fire (10 incidents), mini Spring (DI from scratch), NestJS, React, Next.js
- Databases: Postgres partitioning, replication basics, Redis caching, streams, pub/sub, MongoDB
  basics, database incidents (pool exhaustion, migrations gone wrong)
- DevOps: Git without fear, Git disasters, Nginx and networking (502/504), CI with `act`, Terraform
  and AWS basics on LocalStack, observability (Prometheus, Grafana, OpenTelemetry), on-call incidents
- Interview: Python, Java, JavaScript traps; Java/Spring interview incidents
- Needs a later phase first: AI track (Phase E), Docker and Kubernetes labs (Phase F), system design
  labs (Phase G)

Launch set still missing (spec 8.8): spring-boot-on-fire, postgres-in-depth (grows from the
indexing incident), linux-on-call, rag-from-zero (E), build-your-own-gpt, rate-limiter (G),
docker-start-to-ship (F). Each flagship should reach 8 to 12 chapters; today's labs have 1 or 2.

Every lab: spec in `specs/` -> `new-lab --from-spec` -> content -> `validate --strict` ->
`test-lab` -> logo cover (`labbox cover <lab> --logo <tech>`, free).

## 2. Phases not started

| Phase | What | Needs from you |
|---|---|---|
| E | LLM gateway, AI labs, AI tutor (spec 6) | Which provider and key to use for the gateway (the OpenAI key is approved for covers only) |
| F | Sysbox runtime: Docker and Kubernetes inside labs (spec 4) | sudo on the host to install Sysbox |
| G | System design labs with k6 load tests and rubric grading (spec 7) | Nothing |
| H | Real app foundations: Postgres instead of SQLite, Redis, Google OAuth, workers, disk quotas, ops (spec 10) | Google OAuth client id and secret |
| I | Payments with Razorpay in test mode: free = 2 chapters, paid = the rest | Razorpay test keys |
| J | Admin dashboard and funnel analytics | Nothing |
| K | Launch-set labs complete, deploy to AWS | AWS access, and approval before anything runs there |

## 3. Smaller items deferred by agreement

- Share card image for streaks and levels, and a public profile at `/u/{username}` (Phase C)
- Gauges for live check metrics in the results drawer (Phase D; shown as numbers today)
- Previews on a separate origin, egress allowlist (spec 12 security list; with Phase H/K)

## 4. Definition of done for v2 (spec 12)

- [ ] Sign up with Google, pick "Learn DevOps", typing in a terminal within 60 seconds (Google login: H)
- [x] Calm, one-step-at-a-time lesson panel (Phase A)
- [ ] Launch-set labs pass `labbox test-lab` in CI (CI is ready; the labs are not all written)
- [ ] Incidents, previews, live checks, Docker/Kubernetes in labs, AI gateway, k6 checks work on AWS
  (the first three work locally)
- [ ] Free users finish 2 chapters; Razorpay test payment unlocks the rest (Phase I)
- [ ] Admin dashboard with the funnel and the worst tasks (Phase J)
- [ ] POC security checklist plus: separate preview origin, egress allowlist, disk quotas, provider keys
  never inside containers
