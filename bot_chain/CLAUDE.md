# 🧠 CLAUDE MAIN MEMORY – CECI Bot Chain

<small>Last updated: **12 Jul 2025 (Rev‑5 - Optimized)**</small>

---

## 📋 Work Instructions
1. First think through the problem, read relevant files, write plan to tasks/todo.md
2. Get plan approval before starting
3. Work on todos, mark complete as you go
4. Give high-level explanations of changes
5. Keep changes simple and minimal
6. Add review section to todo.md when done

---

## 1 · Mission
Answer Hebrew questions about Israeli government decisions through **unified GPT pipeline** with improved quality.

---

## 2 · Key Documentation
- **PROJECT_SUMMARY.md** – current status & ports
- **ARCHITECTURE.md** – unified GPT-4o design
- **MICRO_LEVEL_GUIDE.md** – coding rules
- **MIGRATION_GUIDE.md** – migration steps
- **TESTING_PLAN.md** – testing strategy

---

## 3 · Current Status (12 Jul 2025)

### Architecture
- **Unified Intent Bot** (8011) - Merged rewrite+intent with GPT-4o-turbo
- **LLM Formatter Bot** (8017) - GPT-4o-mini for Hebrew formatting
- **Feature Flags**: `USE_UNIFIED_INTENT`, `USE_LLM_FORMATTER`
- **Cost**: ~$0.007-0.011/query (3x original, acceptable for quality)

### Service Health
| Service | Port | Status | Notes |
|---------|------|--------|-------|
| Backend | 5001 | ✅ | Main API |
| Unified Intent | 8011 | ✅ | GPT-4o-turbo |
| SQL Gen | 8012 | ✅ | **UPGRADED: GPT-4o-turbo + synonyms** |
| Context Router | 8013 | ✅ | Memory service |
| Evaluator | 8014 | ✅ | EVAL routes only |
| Clarify | 8015 | ✅ | Fixed enum issue |
| Ranker | 8016 | ⚠️ | Disabled (SKIP_RANKER=true) |
| LLM Formatter | 8017 | ✅ | GPT-4o-mini |

### Today's Fixes (14 Jul)
1. ✅ **SQL Gen Upgrade** - GPT-4o-turbo with synonym expansion, date interpretation, query type detection
2. ✅ **Hebrew Synonyms** - Maps חינוך↔השכלה, ביטחון↔בטחון, auto-expands searches
3. ✅ **Date Understanding** - "השנה", "3 השנים האחרונות", "בין 2020 ל-2023" 
4. ✅ **Count vs List** - Detects כמה/מספר for COUNT queries vs full results
5. ✅ **Feature Flag** - USE_ENHANCED_SQL_GEN=true (default on)

### Known Issues
- Analysis sometimes uses wrong decision (evaluator fetch logic)
- RESULT_REF routes don't retrieve context properly

---

## 4 · Performance Metrics
- **Response Time**: 5-50s (complexity dependent)
- **Token Usage**: 1.4K-25K per query
- **Cost**: $0.007-0.011 typical
- **Success Rate**: ~90%
- **Query Types**: Search, count, compare, analyze, trends, date ranges

---

## 5 · Critical Rules
- **Schema Lock**: NEVER change `id` field type (UUID4 string)
- **Budget**: $10/day cap, prefer GPT-3.5 where possible
- **Testing**: No CI tests (budget), use local tests only
- **Monitoring**: Alert if >$10/day or >2s p95 latency
- **⚠️ DATABASE WARNING**: Local PostgreSQL (port 5433) is TEST ONLY! Production data is in Supabase (israeli_government_decisions)

---

## 6 · Common Commands
```bash
# Services
docker compose up -d
docker compose ps
docker compose logs -f [service]

# Testing
./tests/run_bot_chain_tests.sh
curl http://localhost:8011/health

# Debug specific query
docker compose logs unified-intent-bot --tail 50
```

---

## 7 · Bot Directory Structure
**Active Bots:**
- `UNIFIED_INTENT_BOT_1/` - Intent + rewrite (GPT-4o)
- `QUERY_SQL_GEN_BOT_2Q/` - SQL with templates
- `MAIN_CTX_ROUTER_BOT_2X/` - Context & memory
- `CLARIFY_CLARIFY_BOT_2C/` - Clarifications
- `EVAL_EVALUATOR_BOT_2E/` - Deep analysis
- `QUERY_RANKER_BOT_3Q/` - Ranking (disabled)
- `LLM_FORMATTER_BOT_4/` - Formatting (GPT-4o-mini)

**Deprecated:**
- ~~MAIN_REWRITE_BOT_0~~
- ~~INTENT_RCGNZR_0~~
- ~~MAIN_FORMATTER_4~~

---

*(End of memory - update only when changes occur)*