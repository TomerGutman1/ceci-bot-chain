# 🛠️ CECI‑AI End‑to‑End Pipeline – **Build → Test → Promote** Work Plan

> **Audience:** senior developer who wants crisp boundaries & clear Definition‑of‑Done.
> **Quality Rule:** *No component may promote to the next stage until its test‑suite passes green in CI.*
>
> **Priorities:** P0 (critical) … P5 (low‑priority niceties).
>
> **Cycle for every component**
>
> 1. **Build** feature code
> 2. **Validate** – add/extend unit & integration tests, run locally → CI
> 3. **Gate ✅** – CI workflow `component‑name.yml` must turn green; only then unlock next task via dependency.
>
> The tables below already separate *implementation tasks* (`Build`) from *validation tasks* (`Test`).  Each **Test task is P0 or same priority as its sibling Build task** to make sure quality isn’t postponed.

---

## Legend

| Field                  | Meaning                                        |
| ---------------------- | ---------------------------------------------- |
| **Priority**           | `P0`‑`P5` (lower = sooner)                     |
| **Stage**              | **B** = Build, **T** = Test/Gate               |
| **Deps**               | tasks that must be ✅ before starting           |
| **Success Indicators** | measurable criteria to mark task **DONE**      |
| **Gate Checks**        | automated job(s) that freeze/unfreeze pipeline |

---

## 📦 Phase 0 – Repository & CI Skeleton *(all P0)*

| ID    | Stage | Task                                                   | Deps  | Success Indicators      | Gate Checks             |
| ----- | ----- | ------------------------------------------------------ | ----- | ----------------------- | ----------------------- |
| 0.1‑B | B     | Init mono‑repo skeleton (`src/`, `tests/`, `.github/`) | —     | repo pushed             | CI: `setup.yml` passes  |
| 0.1‑T | T     | CI lint & license checker                              | 0.1‑B | `pre‑commit` hooks run  | `lint.yml` green        |
| 0.2‑B | B     | Core shared libs (`logging.py`, `config.py`)           | 0.1‑T | libs import w/out error | —                       |
| 0.2‑T | T     | Unit tests for shared libs                             | 0.2‑B | ≥ 90 % coverage         | `pytest ‑q` green       |
| 0.3‑B | B     | GitHub Actions matrix (Py ∧ Node)                      | 0.2‑T | workflow files merged   | —                       |
| 0.3‑T | T     | Smoke job (echo + exit 0)                              | 0.3‑B | job passes              | `ci‑skeleton.yml` green |

---

## 📝 Phase 1 – `0_REWRITE_BOT`

| ID    | Stage | Task                              | Priority | Deps  | Success Indicators     | Gate Checks            |
| ----- | ----- | --------------------------------- | -------- | ----- | ---------------------- | ---------------------- |
| 1.1‑B | B     | OpenAPI contract `/rewrite`       | **P0**   | 0.3‑T | spec committed         | `swagger‑lint` green   |
| 1.1‑T | T     | Contract tests via `schemathesis` | **P0**   | 1.1‑B | 100 % endpoints hit    | `rewrite‑contract.yml` |
| 1.2‑B | B     | Implementation (GPT‑3.5)          | **P0**   | 1.1‑T | endpoint returns 200   | —                      |
| 1.2‑T | T     | Unit + golden tests               | **P0**   | 1.2‑B | ≥ 95 % pass            | `pytest tests/rewrite` |
| 1.3‑B | B     | Metrics & logging hooks           | **P1**   | 1.2‑T | Prom counter exposed   | —                      |
| 1.3‑T | T     | Prometheus scrape test            | **P1**   | 1.3‑B | `/metrics` returns 200 | `prom‑check.yml`       |

---

## 🔍 Phase 2 – `1_INTENT_BOT`

| ID    | Stg | Task                           | Pri    | Deps  | Success Indicators   | Gate Checks            |
| ----- | --- | ------------------------------ | ------ | ----- | -------------------- | ---------------------- |
| 2.1‑B | B   | Param taxonomy YAML            | **P0** | 1.2‑T | taxonomy file merged | —                      |
| 2.1‑T | T   | YAML schema lint               | **P0** | 2.1‑B | `yamllint` green     | `taxonomy‑lint.yml`    |
| 2.2‑B | B   | GPT‑4 prompt & examples        | **P0** | 2.1‑T | prompt file merged   | —                      |
| 2.2‑T | T   | Precision ≥ 95 % on golden     | **P0** | 2.2‑B | tests pass           | `tests/intent/golden`  |
| 2.3‑B | B   | Confidence gate + Clarify hook | **P1** | 2.2‑T | code merged          | —                      |
| 2.3‑T | T   | Unclear query scenarios        | **P1** | 2.3‑B | tests pass           | `tests/intent/unclear` |

---

## 🗺️ Phase 3 – `2X_CTX_ROUTER_BOT`

| ID    | Stg | Task                      | Pri    | Deps  | Success Indicators    | Gate Checks          |
| ----- | --- | ------------------------- | ------ | ----- | --------------------- | -------------------- |
| 3.1‑B | B   | Redis context cache       | **P1** | 2.3‑T | cache interface ready | —                    |
| 3.1‑T | T   | Cache hit ratio test      | **P1** | 3.1‑B | ≥ 60 % hit in replay  | `tests/router/cache` |
| 3.2‑B | B   | Routing rules engine YAML | **P1** | 3.1‑T | rules merged          | —                    |
| 3.2‑T | T   | Replay 100 chat logs      | **P1** | 3.2‑B | 100 % correct branch  | `router‑replay.yml`  |

---

## 🗄️ Phase 4 – `2Q_SQL_GEN_BOT`

| ID    | Stg | Task                      | Pri    | Deps        | Success Indicators    | Gate Checks      |
| ----- | --- | ------------------------- | ------ | ----------- | --------------------- | ---------------- |
| 4.1‑B | B   | Import decision DB schema | **P0** | 0.2‑T       | `psql \d` OK          | —                |
| 4.1‑T | T   | Migration CI job          | **P0** | 4.1‑B       | job passes            | `db‑migrate.yml` |
| 4.2‑B | B   | GPT‑4 SQL generator       | **P0** | 4.1‑T,2.2‑T | code merged           | —                |
| 4.2‑T | T   | Template coverage >90 %   | **P0** | 4.2‑B       | `tests/sql_gen` green | —                |
| 4.3‑B | B   | SQL sanitizer & timeouts  | **P0** | 4.2‑T       | guard lib merged      | —                |
| 4.3‑T | T   | Injection & timeout tests | **P0** | 4.3‑B       | attacks blocked       | `sql‑guard.yml`  |

---

## 🧮 Phase 5 – `2E_EVALUATOR_BOT`

| ID    | Stg | Task                       | Pri    | Deps  | Success Indicators         | Gate Checks          |
| ----- | --- | -------------------------- | ------ | ----- | -------------------------- | -------------------- |
| 5.1‑B | B   | Weighted scoring logic     | **P1** | 4.3‑T | code merged                | —                    |
| 5.1‑T | T   | Score reproducibility test | **P1** | 5.1‑B | diff <1 e‑6                | `evaluator‑unit.yml` |
| 5.2‑B | B   | Explainability field       | **P2** | 5.1‑T | JSON `explanation` present | —                    |
| 5.2‑T | T   | Snapshot tests             | **P2** | 5.2‑B | snapshots pass             | `evaluator‑snapshot` |

---

## 🗂️ Phase 6 – `3Q_RANKER_BOT`

| ID    | Stg | Task                 | Pri    | Deps  | Success Indicators | Gate Checks    |
| ----- | --- | -------------------- | ------ | ----- | ------------------ | -------------- |
| 6.1‑B | B   | Ranking heuristics   | **P1** | 5.1‑T | code merged        | —              |
| 6.1‑T | T   | NDCG >0.85 benchmark | **P1** | 6.1‑B | test passes        | `tests/ranker` |

---

## 📄 Phase 7 – `4_FORMATTER`

| ID    | Stg | Task                   | Pri    | Deps  | Success Indicators | Gate Checks       |
| ----- | --- | ---------------------- | ------ | ----- | ------------------ | ----------------- |
| 7.1‑B | B   | Markdown & JSON modes  | **P0** | 6.1‑T | code merged        | —                 |
| 7.1‑T | T   | Formatter unit tests   | **P0** | 7.1‑B | tests pass         | `tests/formatter` |
| 7.2‑B | B   | Context‑aware examples | **P1** | 7.1‑T | examples rendered  | —                 |
| 7.2‑T | T   | Snapshot diff tests    | **P1** | 7.2‑B | diff clean         | `formatter‑snap`  |

---

## 🚦 Phase 8 – E2E Integration

| ID    | Stg | Task                         | Pri    | Deps  | Success Indicators          | Gate Checks       |
| ----- | --- | ---------------------------- | ------ | ----- | --------------------------- | ----------------- |
| 8.1‑B | B   | Docker Compose stack         | **P0** | 7.1‑T | `docker compose up` healthy | —                 |
| 8.1‑T | T   | `./tests/run_tests.sh` quick | **P0** | 8.1‑B | passes green                | `e2e‑quick.yml`   |
| 8.2‑B | B   | Nightly full‑suite job       | **P0** | 8.1‑T | workflow merged             | —                 |
| 8.2‑T | T   | Badge + mail report          | **P0** | 8.2‑B | badge green                 | nightly run green |

---

## 🌟 Phase 9 – Stretch

| ID    | Stg | Task                   | Pri    | Deps  | Success Indicators | Gate Checks        |
| ----- | --- | ---------------------- | ------ | ----- | ------------------ | ------------------ |
| 9.1‑B | B   | JUnit XML export       | **P3** | 8.2‑T | reports visible    | —                  |
| 9.1‑T | T   | GH summary graphs      | **P3** | 9.1‑B | chart rendered     | `junit‑report.yml` |
| 9.2‑B | B   | Grafana SLA dashboard  | **P4** | 8.1‑T | panels visible     | —                  |
| 9.2‑T | T   | Alert rules firing     | **P4** | 9.2‑B | alert test         | `alert‑test.yml`   |
| 9.3‑B | B   | Canary deploy script   | **P5** | 8.2‑T | canary route added | —                  |
| 9.3‑T | T   | Zero 5xx during canary | **P5** | 9.3‑B | log diff clean     | `canary‑check.yml` |

---

### 📌 Next Step

Start with **0.1‑B**, finish its paired **0.1‑T** test, wait for CI green, then proceed.  If any Gate fails, fix before moving on.

Happy hacking 🚀
