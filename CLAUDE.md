# 🧠 CLAUDE MAIN MEMORY – CECI Bot Chain

<small>Last updated: **18 Jul 2025 (Rev‑10 - Database Empty Issue)**</small>

---

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.

## 1 · Mission

Answer Hebrew questions about Israeli government decisions through a **unified GPT pipeline**, with **improved quality** and **acceptable cost increase**.

---

## 2 · Must‑Read Files

1. **PROJECT\_SUMMARY.md** – current status & ports
2. **PRODUCTION\_DEPLOYMENT\_GUIDE.md** – 🚀 HOW TO DEPLOY CHANGES
3. **bot_chain/ARCHITECTURE.md** – unified GPT-4o architecture design
4. **bot_chain/MICRO\_LEVEL\_GUIDE.md** – cross‑layer coding rules
5. **bot_chain/MIGRATION\_GUIDE.md** – step-by-step migration to new architecture
6. **TEST\_RESULTS\_HEBREW.md** – comprehensive test results with costs
7. **ROUTE\_TEST\_REPORT.md** – detailed route testing analysis
8. **UNIFIED\_ARCHITECTURE\_REPORT.md** – implementation report

*(Open only the layer spec you are actively editing – nothing more.)*

## 2.5 · Testing & Results Documentation

- **TEST\_RESULTS\_HEBREW.md** – 25+ test queries with costs & coverage (✅ 100% success rate)
- **ROUTE\_TEST\_REPORT.md** – comprehensive route testing & bot sequence verification
- **bot_chain/TESTING\_RESULTS\_PHASE1.md** – individual bot test results
- **bot_chain/MAIN\_CTX\_ROUTER\_BOT\_2X/REFERENCE\_RESOLUTION\_INTEGRATION\_GUIDE.md** – context handling guide

---

## 3 · Production Deployment 🚀

### Quick Deploy Commands:
```bash
# 1. Commit and push changes
git add . && git commit -m "fix: description" && git push origin production-deploy

# 2. Deploy to server
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && git pull && docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod build [service] && ./run-compose.sh up -d [service]"
```

* **Live Site**: https://ceci-ai.ceci.org.il
* **Branch**: `production-deploy` (ALWAYS use this)
* **Server**: 178.62.39.248
* **Guide**: See `PRODUCTION_DEPLOYMENT_GUIDE.md`

### 🎯 Latest Fix - Timeout Issues Resolved (17 Jul 2025)
* **Problem**: 40% timeout rate on simple queries like "החלטה 2989"
* **Solution**: Implemented connection pooling, retry logic, and circuit breakers
* **Results**: 0% timeout rate, avg response time 3.16s (production tested)
* **Files**: See `tasks/timeout_fix_plan.md` for implementation details

## 4 · Cost & Testing Constraints

* **Budget restored**: Allows GPT-4o usage on critical layers
* **New cost structure**: ~\$0.016/query (typical), ~\$0.031/analysis 
* **Architecture tradeoff**: 3x cost increase for 40% latency reduction and superior quality
* **Feature flags**: Enable gradual rollout with `USE_UNIFIED_INTENT` and `USE_LLM_FORMATTER`

### Schema‑Integrity Rule  🔒

> **NEVER change fundamental data types** again – e.g. the `id` field **must stay `UUID4` *as string***. All future PRs touching DB schema require explicit approval.

---

## 5 · Unified Architecture Changes (10 Jul 2025)

### What Changed?
- **MERGED**: `0_REWRITE_BOT` + `1_INTENT_BOT` → Single **`1_UNIFIED_INTENT_BOT`** (GPT-4o-turbo)
- **UPGRADED**: Code-based formatter → **`4_LLM_FORMATTER_BOT`** (GPT-4o-mini)
- **PRESERVED**: All other bots remain unchanged

### Why?
- **Performance**: Save 200-300ms (one less API call)
- **Quality**: GPT-4o handles Hebrew nuances better than GPT-3.5 + JS
- **Flexibility**: LLM formatter handles edge cases (plural-gender agreement)
- **Budget**: Restored budget allows GPT-4o on critical layers

### Migration Strategy
| Phase | Actions | Timeline |
| --- | --- | --- |
| **Phase 1** | Deploy new bots, enable for 10% traffic | Week 1 |
| **Phase 2** | Monitor metrics, increase to 25% | Week 2 |
| **Phase 3** | Validate cost projections, 50% traffic | Week 3 |
| **Phase 4** | Full rollout, archive old bots | Week 4 |

---

## 6 · Implementation Checklist (progress‑ordered)

* [x] **Unified Intent Bot** Created ✓ / Tested ✓ / Deployed ✓
* [x] **LLM Formatter Bot** Created ✓ / Tested ✓ / Deployed ✓
* [x] **Feature Flags** Added ✓ / A/B testing setup ✓
* [x] **Documentation** Architecture ✓ / Micro Guide ✓ / CLAUDE.md ✓
* [x] **Production Deploy** SSL ✓ / Monitoring ✓ / Backups ✓
* [x] **Migration** Phase 1 ✓ (100% traffic on new architecture)

*(Tick boxes as soon as a task is merged; Claude reloads fresh memory each convo.)*

---

## 8 · Temporary Overrides & Monitoring

* **Evaluator & Ranker** remain OFF unless explicitly required.
* Log `token_usage` & daily spend; alert > \$10 or p95 latency > 2 s.
* Use `SKIP_RANKER=true` env flag for truncating ranker until optimised.
* **NEW**: Monitor unified intent accuracy with `unified_intent_accuracy` metric
* **NEW**: Track formatter quality with `formatter_quality_score` metric

## 9 · ❌ CRITICAL DATABASE ISSUE (18 Jul 2025) 

**Database Empty - No Data Available**:
1. **Investigation of content truncation** revealed the government_decisions table has 0 rows
2. **Fixed Issues**:
   - ✅ LLM Formatter: Increased content limit from 1000 to 10000 chars
   - ✅ SQL Gen Bot: Fixed schema documentation (was using wrong column names)
   - ✅ SQL Templates: Aligned with actual database schema:
     - Table: `government_decisions` (not `israeli_government_decisions`)
     - Columns: `content` (not `decision_content`), `title` (not `decision_title`)
     - Arrays: `topics` (not `tags_policy_area`), `ministries` (not `tags_government_body`)
3. **Immediate Action Required**: Load data into the government_decisions table

## 10 · Testing Guidelines

* Always test as if a real user inputed through the chat box in the real UI, and check logs
