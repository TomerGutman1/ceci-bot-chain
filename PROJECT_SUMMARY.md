# 📑 PROJECT SUMMARY – CECI AI Bot-Chain

Lightweight overview *with* full data folded away.

---

## 1 · What the System Does ⏩

Answers Hebrew questions on Israeli gov-decisions
via **Frontend → FastAPI → Bot-Chain → Supabase PG**.

1. `POST /api/process-query` (frontend)
2. Container `BOT_CHAIN` (port 8002) runs:
   `1_UNIFIED_INTENT → 2X_ROUTER → 2C_CLARIFY? → 2Q_SQL → 2E_EVAL → 3Q_RANK → 4_LLM_FORMATTER`
3. Source tables: `israeli_government_decisions_*`.

---

## 2 · Directory Landmarks 📂

| Path                        | What lives here     | When to read     |
| --------------------------- | ------------------- | ---------------- |
| `bot_chain/ARCHITECTURE.md` | Full system diagram | Skim for context |

| Path                              | What lives here      | When to read             |
| --------------------------------- | -------------------- | ------------------------ |
| `bot_chain/LAYERS_SPECS/`         | **Per-bot specs**    | Load only layer in focus |
|                                   |                      |                          |
| `bot_chain/UNIFIED_INTENT_BOT_1/` | Entry bot impl       | When editing entry       |
| `bot_chain/LLM_FORMATTER_BOT_4/`  | Formatter impl       | When editing formatter   |
| `bot_chain/MIGRATION_GUIDE.md`    | Step-by-step rollout | Migration tasks          |
| `TEST_RESULTS_HEBREW.md`          | 25+ test queries     | Validate behaviour       |
| `ROUTE_TEST_REPORT.md`            | Route analysis       | Debug routing            |
| `UNIFIED_ARCHITECTURE_REPORT.md`  | Migration details    | Understand changes       |
| `bot_chain/test_all_routes.py`    | Python tester        | Full route tests         |
| `bot_chain/test_routes.sh`        | Bash tester          | Quick sanity check       |
| `PRODUCTION_DEPLOYMENT_GUIDE.md`  | **Deploy guide**     | Production updates       |

---

## 3 · Token-Saving Guidelines 🪙

1. **Minimal context** – load only docs you touch.
2. **Layer isolation** – specs are self-contained.
3. Track `debug_info.token_usage`.

* Unified-Intent removed one GPT call (~100 tokens saved).
* Prompt shrinks deliver 75 % average reduction.

---

## 4 · Quick Reference ✏️

| Need            | Open                                |
| --------------- | ----------------------------------- |
| REST contract   | `ARCHITECTURE.md` §5                |
| Tune prompt     | `LAYERS_SPECS/<layer>.md`           |
| DB columns      | `SQL_DB_SPEC.md` + `*_DB_SCHEME.md` |
| Cost table      | `ARCHITECTURE.md` §8                |
| Migration guide | `MIGRATION_GUIDE.md`                |

---

## 5 · Testing Docs 🧪

Current **status 12 Jul 2025**: *6 pass · 2 warn*.

| Doc                      | Purpose                 | Key insights   |
| ------------------------ | ----------------------- | -------------- |
| `TEST_RESULTS_HEBREW.md` | Hebrew scenarios & cost | \$0.002-0.020  |
| `ROUTE_TEST_REPORT.md`   | Intent→Bot mapping      | Clarify now OK |
| …                        | …                       | …              |

**Failures ❌** – OpenAI quota; renew key or wait.

---

## 6 · Optimisation Tracker

*P1 Quick Wins* & *P2 Smart Routing* complete
(cost ↓ 85 %, p95 latency ≤ 4 s)‏

* Model downgrades: SQL\_GEN → gpt-3.5 (-83 %).
* 11 SQL templates cover 90 % queries.
* Cache: resp 4 h, SQL 24 h.
* Prompt trims 50-80 % each bot.

---

## 7 · Ports & Health

Backend 5001 · Bots 8011-17 · PG 5433 · Redis 6380
Health: `/api/chat/health` + `/health` per bot.

---

## 8 · Production Status (13 Jul 2025) 🚀

- **Live at**: https://ceci-ai.ceci.org.il
- **Server**: DigitalOcean droplet (178.62.39.248)
- **Branch**: `production-deploy`
- **SSL**: Let's Encrypt (auto-renewal)
- **Deployment Guide**: See `PRODUCTION_DEPLOYMENT_GUIDE.md`

### Recent Updates:
- ✅ Fixed LLM formatter validation errors
- ✅ Prevented fake data generation
- ✅ Added date display (DD/MM/YYYY) to results
- ✅ Configured automated backups
- ✅ Created comprehensive deployment guide

---

## 9 · Contact

**Maintainer:** Tomer · [tomer@example.com](mailto:tomer@example.com)

Domain for deployment in digital ocean droplet : [https://ceci-ai.ceci.org.il/](https://ceci-ai.ceci.org.il/)