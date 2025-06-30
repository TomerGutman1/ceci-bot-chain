# 🧠 CLAUDE MAIN MEMORY – CECI Bot Chain

<small>Last updated: **30 Jun 2025 (Rev‑2)**</small>

---

## 1 · Mission

Answer Hebrew questions about Israeli government decisions through a 7‑layer GPT pipeline, while **minimising cost** and **maintaining ≥ 95 % accuracy**.

---

## 2 · Must‑Read Files

1. **PROJECT\_SUMMARY.md** – current status & ports
2. **OPTIMIZATION\_PLAN.md** – step‑by‑step cost/perf roadmap
3. **MICRO\_LEVEL\_GUIDE.md** – cross‑layer coding rules

*(Open only the layer spec you are actively editing – nothing more.)*

---

## 3 · Cost & Testing Constraints

* **Budget cap**: \$10/day, \$0.10/query (enforced by `CostController`).
* **🛑 CI tests suspended** until budget is restored – **do not run** unit/E2E scripts.
* Prefer **GPT‑3.5‑turbo**; escalate to GPT‑4‑turbo only via fallback chain.

### Schema‑Integrity Rule  🔒

> **NEVER change fundamental data types** again – e.g. the `id` field **must stay `UUID4` *as string***. All future PRs touching DB schema require explicit approval.

---

## 4 · Work Plan & Priorities  (from *OPTIMIZATION\_PLAN.md*)

| 🔢 Priority                        | Key Actions                                                                                               |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **P1 · Quick Wins**                | • Downgrade INTENT & SQL‑GEN to 3.5‑turbo  \• Add 10 SQL templates  \• Extend caches (resp 4 h, SQL 24 h) |
| **P2 · Smart Routing**             | • Conditional bot activation  \• Parallel pre‑processing  \• 300‑token → 150‑token prompts                |
| **P3 · Advanced Optimisation**     | • Batch up to 5 queries  \• Hybrid decision tree by confidence  \• CostController hooks                   |
| **P4 · Intelligence Preservation** | • Live quality dashboards  \• Smart fallback chain  \• Context enrichment helpers                         |

> **Target Outcome**: cut **cost × 8.4** and **latency × 3**.

---

## 5 · Implementation Checklist (progress‑ordered)

* [ ] **P1** Model selector ✓ / SQL templates ⬜ / Cache boost ⬜ / Cost logs ⬜
* [ ] **P2** Router rules ⬜ / Prompt trims ⬜ / Intent‑pattern cache ⬜
* [ ] **P3** Batch processing ⬜ / A/B testing ⬜ / Fallback chain ⬜
* [ ] **P4** Threshold tuning ⬜ / Post‑mortems ⬜

*(Tick boxes as soon as a task is merged; Claude reloads fresh memory each convo.)*

---

## 6 · Current Project Status (30 Jun 2025)

### Critical Fixes

1. **Evaluator Bot (2E)** disabled on QUERY path – save GPT‑4 tokens.
2. **Ranker Bot (3Q)** skipped; results currently ordered by date.
3. **UUID4 bug fixed** – all `id` columns restored to `VARCHAR(36)`; migrations locked.
4. **OpenAI quota exceeded** – obtain new API Key **or** wait for reset.

### Urgent Recommendations

* Swap GPT‑4‑turbo → GPT‑3.5‑turbo where quality unaffected.
* Shrink prompt bodies; reuse examples via `{{examples}}` placeholder.
* Add global response cache + rate‑limit (≤ 30 req/min).

### Service Ports (reference)

| Component   | Port  |                   |               |                |
| ----------- | ----- | ----------------- | ------------- | -------------- |
| Backend     |  5001 |                   |               |                |
| Rewrite     |  8010 | Intent 8011       | SQL‑Gen 8012  | Ctx 8013       |
| Evaluator   |  8014 | Clarify 8015      | Ranker 8016   | Formatter 8017 |
| Frontend    |  3001 | Nginx 80/443/8080 | Postgres 5433 | Redis 6380     |

---

## 7 · Temporary Overrides & Monitoring

* **Evaluator & Ranker** remain OFF unless explicitly required.
* Log `token_usage` & daily spend; alert > \$10 or p95 latency > 2 s.
* Use `SKIP_RANKER=true` env flag for truncating ranker until optimised.

---

*(End of main memory – keep additions succinct yet complete. Refresh only on real changes.)*
