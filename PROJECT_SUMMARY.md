# 📑 PROJECT SUMMARY – CECI AI Bot-Chain

Lightweight overview *with* full data folded away.

---

## 1 · What the System Does ⏩

Answers Hebrew questions on Israeli gov-decisions
via **Frontend → FastAPI → Bot-Chain → Supabase PG**.

1. `POST /api/process-query` (frontend)
2. Container `BOT_CHAIN` (port 8002) runs:
   `1_UNIFIED_INTENT → 2X_ROUTER → 2C_CLARIFY? → 2Q_SQL → 2E_EVAL? → 3Q_RANK? → 4_LLM_FORMATTER`
3. **PRODUCTION DATA**: Supabase table `israeli_government_decisions`
4. **⚠️ NOT FOR QUERIES**: Local PostgreSQL (port 5433) - test fixtures only!

**Unified Architecture**: Merged Rewrite+Intent bots, upgraded to LLM formatter for Hebrew quality.

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

## 4 · Unified Architecture Changes 🚀

| What Changed | Details |
| ------------ | ------- |
| **Merged Bots** | `0_REWRITE` + `1_INTENT` → `1_UNIFIED_INTENT` (GPT-4o-turbo) |
| **LLM Formatter** | Code-based → `4_LLM_FORMATTER` (GPT-4o-mini) |
| **Performance** | -200-300ms (one less API call), 40% latency reduction |
| **Quality** | Superior Hebrew handling, plural-gender agreement |
| **Cost** | ~$0.016/query typical, ~$0.031/analysis (3x increase) |
| **Status** | ✅ 100% traffic on new architecture |

---

## 5 · Quick Reference ✏️

| Need            | Open                                |
| --------------- | ----------------------------------- |
| REST contract   | `ARCHITECTURE.md` §5                |
| Tune prompt     | `LAYERS_SPECS/<layer>.md`           |
| DB columns      | `SQL_DB_SPEC.md` + `*_DB_SCHEME.md` |
| Cost table      | `ARCHITECTURE.md` §8                |
| Migration guide | `MIGRATION_GUIDE.md`                |

---

## 6 · Testing Docs 🧪

Current **status 15 Jul 2025**: ✅ **All tests passing** (unified architecture)

| Doc                      | Purpose                 | Key insights        |
| ------------------------ | ----------------------- | ------------------- |
| `TEST_RESULTS_HEBREW.md` | Hebrew scenarios & cost | \$0.016-0.031/query |
| `ROUTE_TEST_REPORT.md`   | Intent→Bot mapping      | 100% success rate   |
| `UNIFIED_ARCHITECTURE_REPORT.md` | Migration results | Full deployment complete |

**Cost Structure**: ~3x increase for 40% latency reduction + superior Hebrew handling

---

## 7 · Optimisation Tracker

*P1 Quick Wins* & *P2 Smart Routing* complete
(cost ↓ 85 %, p95 latency ≤ 4 s)‏

* Model downgrades: SQL\_GEN → gpt-3.5 (-83 %).
* 11 SQL templates cover 90 % queries.
* Cache: resp 4 h, SQL 24 h.
* Prompt trims 50-80 % each bot.

---

## 8 · Ports & Health

| Service | Port | Notes |
| ------- | ---- | ----- |
| Backend | 5001 | |
| Unified Intent | 8011 | Merged Rewrite+Intent |
| SQL-Gen | 8012 | |
| Context Router | 8013 | |
| Evaluator | 8014 | |
| Clarify | 8015 | |
| Ranker | 8016 | Currently disabled |
| LLM Formatter | 8017 | Replaced code formatter |
| Decision Guide | 8018 | NEW service |
| Postgres | 5433 | ⚠️ TEST ONLY - not for production queries! |
| Redis | 6380 | |

Health: `/api/chat/health` + `/health` per bot.

---

## 9 · Production Status (15 Jul 2025) 🚀

- **Live at**: https://ceci-ai.ceci.org.il
- **Server**: DigitalOcean droplet (178.62.39.248)
- **Branch**: `production-deploy`
- **SSL**: Let's Encrypt (auto-renewal)
- **Deployment Guide**: See `PRODUCTION_DEPLOYMENT_GUIDE.md`

### Latest Updates (17 Jul) 🆕:
- ✅ **ALL PRODUCTION ISSUES RESOLVED** - System fully operational!
  - ✅ Count queries now return correct formatted counts (e.g., "426 החלטות")
  - ✅ Specific decision lookups working with ~2s response time
  - ✅ Recent decisions queries return 10 results as expected
  - ✅ Ministry searches functioning correctly (~4s response)
  - ✅ No more timeouts - all query types working smoothly
  - ✅ Response times averaging 2-4 seconds
- ✅ **GitHub Repository Sync** - Successfully synchronized local changes to Lovable repo
  - Force pushed local `production-deploy` branch to `ceci-project/ceci-ai` main branch
  - Repository now fully updated at https://github.com/ceci-project/ceci-ai
  - Added SSH remote configuration for seamless future updates
  - Committed enhanced SQL mode fixes before push

### Previous Updates (16 Jul):
- ⚠️ **Example Queries Testing** - Found critical issues (NOW RESOLVED)
  - ✅ Basic search working (10 results for "חינוך ממשלה 37")
  - ✅ Count queries fixed - now return proper counts
  - ✅ Specific decision lookup fixed
  - ✅ Recent decisions query fixed
  - ✅ Ministry-based searches fixed
- 🔧 **Attempted Fixes**:
  - Added `entities.count_only` check to count detection
  - Added SQL query logging for debugging
  - Fixed environment variables (USE_UNIFIED_INTENT=true, USE_ENHANCED_SQL_GEN=true)
  - Added debug logging (not showing in production logs)
- 🐛 **Root Issues**:
  - Count query execution path returning wrong format
  - Production logging suppressed (NODE_ENV=production)
  - Multiple query types experiencing timeouts

### Previous Updates (15 Jul):
- ✅ **Analysis Display Redesigned** - Improved formatting for better readability
  - Compact 3-column table (קריטריון | משקל | ציון) that fits chat window
  - Text citations moved to separate section at end
  - Added extra line spacing throughout
  - Removed visual score bars for cleaner look
  - Set evaluator temperature to 0.0 for consistent scoring
- ✅ Enhanced SQL search to include content fields for topics like "ענן הממשלתי"
- ✅ Updated UI text (welcome message, decision guide title, example queries)
- ✅ **Decision Guide Bot** - Fixed weight calculation instability
  - Set temperature to 0.0 for consistent scoring
  - Fixed criterion name mismatches causing 0% weights
  - Added file upload click handler fix

### Previous Updates (14 Jul):
- ✅ Fixed full content display - only shows when explicitly requested "תוכן מלא"
- ✅ Fixed analysis functionality - now properly formats and displays evaluator results
- ✅ Increased LLM formatter MAX_TOKENS to 4000 (prevents cut-off responses)
- ✅ **Decision Guide Export** - Added PDF and CSV export functionality
  - PDF: Visual score bars, color-coded criteria, English text
  - CSV/Excel: All criteria data with Hebrew headers, recommendations sheet
- ✅ **SQL-GEN BOT UPGRADED** - Now uses GPT-4o-turbo with enhanced capabilities
  - Hebrew synonym expansion (חינוך↔השכלה, ביטחון↔בטחון)
  - Date interpretation ("השנה", "3 השנים האחרונות")
  - Query type detection (COUNT vs LIST)
  - Typo correction (חנוך→חינוך)

---

## 10 · Contact

**Maintainer:** Tomer · [tomer@example.com](mailto:tomer@example.com)

Domain for deployment in digital ocean droplet : [https://ceci-ai.ceci.org.il/](https://ceci-ai.ceci.org.il/)