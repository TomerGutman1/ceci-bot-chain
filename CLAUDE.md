# 🧠 CLAUDE MAIN MEMORY – CECI Bot Chain

<small>Last updated: **30 Jun 2025 (Rev‑2)**</small>

---

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.

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

* [x] **P1** Model selector ✓ / SQL templates ✓ / Cache boost ✓ / Cost logs ✓
* [ ] **P2** Router rules ✓ / Prompt trims ⬜ / Intent‑pattern cache ⬜
* [ ] **P3** Batch processing ✓ / A/B testing ✓ / Fallback chain ✓
* [ ] **P4** Threshold tuning ✓ / Post‑mortems ✓

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


### 🔴 Critical Cache Bug Discovery

**Entity Persistence Issue**: System returns stale results when querying different decision numbers. Even with all cache layers disabled, the same decision (e.g., 2989) is returned for different queries.

**INCORRECTLY DISABLED** (need restoration):
* `checkIntentPatternCache()` - server/src/services/botChainService.ts:~200-250
* `storeIntentPattern()` - server/src/services/botChainService.ts:~250-300
* `normalizeQueryPattern()` - server/src/services/botChainService.ts:~300-350
* `checkResponseCache()` - server/src/services/botChainService.ts:~500-550
* `storeInCache()` - server/src/services/botChainService.ts:~550-600
* `generateCacheKey()` - server/src/services/botChainService.ts:~600-650

**IMMEDIATE ACTIONS**:
1. Restore Intent Pattern Cache (only caches patterns, not entities)
2. Restore SQL Template Cache (only caches templates, not parameters)
3. Find the actual cache layer causing entity persistence
4. Test with different decision numbers to verify fix

### 🚨 UPDATED STATUS (4 Jul 2025) - CRITICAL PRODUCTION ISSUES

**EVALUATOR Bot Timeout Crisis**:
- Analysis requests (`נתח את התוכן`) fail with 30-second timeouts
- Backend logs show: `timeout of 30000ms exceeded`
- User increased max_tokens to 20,000 but issue persists
- **Result**: Empty responses for analysis requests

**Full Content Bug**:
- Requests for `תוכן מלא` show unclear repeated messages
- Users report confusing duplicate responses
- **Status**: Root cause unknown, needs formatter investigation

**Fixes Applied**:
1. ✓ Intent detection fixed - EVAL path now triggered correctly
2. ✓ EVALUATOR bot field mapping fixed (original_query, decision_number)
3. ✓ Token limits increased to 20,000
4. ✓ Memory context features disabled to prevent entity persistence
5. ✓ **URL Generation Fix** - Decision URLs now come ONLY from database `decision_url` field
6. ✓ **SQL Template Cleanup** - Removed duplicate `specific_decision` templates
7. ✓ **Multiple Decision Support** - System correctly shows all decisions when multiple exist for same number

**URGENT TODO**:
1. Fix EVALUATOR timeout issue (Priority 1)
2. Debug full content response duplication (Priority 2)
3. Restore cache systems safely (Priority 3)
4. Implement Reference Resolution integration (Priority 2)

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

### 📋 Log Summary (4 Jul 2025)

**Backend Logs Analysis**:
- EVALUATOR bot timeouts causing empty analysis responses
- Error: `timeout of 30000ms exceeded` 
- Decision 2766 analysis fails after 30+ seconds
- Bot processes but exceeds timeout limit

**System Status**:
- All containers healthy and running
- Intent detection working correctly
- EVALUATOR integration fixed but timeouts remain
- Memory context features disabled as temporary fix

**Next Actions Required**:
1. Increase EVALUATOR timeout limit beyond 30s
2. Investigate full content duplication in formatter
3. Test system with different decision numbers

### 🎯 URL Generation Fix - COMPLETED (4 Jul 2025)

**Problem**: System was generating decision URLs instead of using actual URLs from database.

**Solution Implemented**:
- **MAIN_FORMATTER_4**: Modified to use ONLY `decision_url` from database field
- **SQL Templates**: Cleaned up duplicate `specific_decision` templates that caused conflicts
- **Database Integration**: All URLs now come from `government_decisions.decision_url` column
- **Multiple Results**: System correctly handles cases where government publishes multiple decisions with same number

**Files Modified**:
- `bot_chain/QUERY_SQL_GEN_BOT_2Q/sql_templates.py` - Removed duplicate template (lines 300-320)
- `bot_chain/MAIN_FORMATTER_4/main.py` - Line 308-312: URL from DB only, no fallback generation

**Validation**:
- ✓ URLs come exclusively from database `decision_url` field
- ✓ No URL generation or format assumptions
- ✓ Multiple decisions with same number display correctly
- ✓ Container rebuilt to apply SQL template changes

### 🔗 Reference Resolution Integration - READY FOR IMPLEMENTATION

**Status**: Integration guide prepared at `MAIN_CTX_ROUTER_BOT_2X/REFERENCE_RESOLUTION_INTEGRATION_GUIDE.md`

**Key Features**:
- **Implicit Reference Detection**: "תן לי את זה" resolves to specific decision from conversation history
- **Cross-Turn Entity Resolution**: Combines info from multiple user messages
- **Hebrew Clarification Generation**: Natural Hebrew when context unclear
- **Performance**: <100ms p95 latency, >90% success rate
- **Bot Response Filtering**: Ignores bot messages, processes only user input

**Integration Points**:
- `reference_config.py` - Hebrew patterns & configuration
- `reference_resolver.py` - Main resolution logic
- `main.py` - Updated with integration hooks
- Backend clarification handling for `reference_resolution` type

### 📊 Macro Filter View Dashboard - IMPLEMENTED (6 Jul 2025)

**Status**: Fully functional statistics dashboard with zero impact on chat system

**Implementation Summary**:
1. ✓ Created complete statistics service with direct DB queries (no GPT costs)
2. ✓ Fixed all data transformation issues causing frontend crashes
3. ✓ Added missing API endpoints for data optimization
4. ✓ Updated navigation - "מבט מאקרו" button now leads to dashboard
5. ✓ Enhanced export functionality - "ייצוא דוח" with chart support

**Key Fixes Applied**:
- **Timeline Data**: Hebrew month names now properly converted to Date objects
- **Filter Options**: Government/committee/policy area data structures aligned
- **NULL Handling**: All statistics endpoints now filter out invalid/null data
- **Date Validation**: Decisions with dates before 1990 or null are excluded
- **Field Mapping**: Fixed mismatches (operativeCount→operationalCount, name→area/committee)

**New Features**:
- **Statistics API Endpoints**:
  - GET /api/statistics/overview
  - GET /api/statistics/timeline
  - GET /api/statistics/policy-areas
  - GET /api/statistics/committees
  - GET /api/statistics/governments
  - GET /api/statistics/filter-options
  - POST /api/statistics/decisions/paginated
  - POST /api/statistics/optimized
  - POST /api/statistics/export

- **Dashboard Components**:
  - KPI Cards with real-time stats
  - Timeline charts with month/year granularity
  - Policy distribution pie charts
  - Committee activity analysis
  - Government comparison tools
  - Data optimizer for large datasets
  - Smart alerts and predictions
  - Report sharing with export options

**Environment Variables Added**:
- `VITE_SHOW_MACRO_BUTTON=false` - Toggle macro buttons in example queries

**Files Modified**:
- `server/src/services/statisticsService.ts` - Core statistics logic
- `server/src/routes/statistics.ts` - REST API endpoints
- `src/macro_filter_view/services/api.ts` - Frontend API transformations
- `src/components/layout/Layout.tsx` - Navigation update
- `src/components/chat/ExampleQueries.tsx` - Optional macro buttons
- `src/macro_filter_view/components/shared/ReportSharing.tsx` - Enhanced export

**Access**: http://localhost/dashboard/statistics

---

*(End of main memory – keep additions succinct yet complete. Refresh only on real changes.)*
