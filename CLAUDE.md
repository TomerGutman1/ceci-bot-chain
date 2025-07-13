# 🧠 CLAUDE MAIN MEMORY – CECI Bot Chain

<small>Last updated: **10 Jul 2025 (Rev‑4 - Route Testing Complete)**</small>

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
2. **bot_chain/ARCHITECTURE.md** – unified GPT-4o architecture design
3. **bot_chain/MICRO\_LEVEL\_GUIDE.md** – cross‑layer coding rules
4. **bot_chain/MIGRATION\_GUIDE.md** – step-by-step migration to new architecture
5. **TEST\_RESULTS\_HEBREW.md** – comprehensive test results with costs
6. **ROUTE\_TEST\_REPORT.md** – detailed route testing analysis
7. **UNIFIED\_ARCHITECTURE\_REPORT.md** – implementation report

*(Open only the layer spec you are actively editing – nothing more.)*

## 2.5 · Testing & Results Documentation

- **TEST\_RESULTS\_HEBREW.md** – 25+ test queries with costs & coverage (✅ 100% success rate)
- **ROUTE\_TEST\_REPORT.md** – comprehensive route testing & bot sequence verification
- **bot_chain/TESTING\_RESULTS\_PHASE1.md** – individual bot test results
- **bot_chain/MAIN\_CTX\_ROUTER\_BOT\_2X/REFERENCE\_RESOLUTION\_INTEGRATION\_GUIDE.md** – context handling guide

---

## 3 · Cost & Testing Constraints

* **Budget restored**: Allows GPT-4o usage on critical layers
* **New cost structure**: ~\$0.016/query (typical), ~\$0.031/analysis 
* **Architecture tradeoff**: 3x cost increase for 40% latency reduction and superior quality
* **Feature flags**: Enable gradual rollout with `USE_UNIFIED_INTENT` and `USE_LLM_FORMATTER`

### Schema‑Integrity Rule  🔒

> **NEVER change fundamental data types** again – e.g. the `id` field **must stay `UUID4` *as string***. All future PRs touching DB schema require explicit approval.

---

## 4 · Unified Architecture Changes (10 Jul 2025)

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

## 5 · Implementation Checklist (progress‑ordered)

* [x] **Unified Intent Bot** Created ✓ / Tested ✓ / Deployed ⬜
* [x] **LLM Formatter Bot** Created ✓ / Tested ✓ / Deployed ⬜
* [x] **Feature Flags** Added ✓ / A/B testing setup ✓
* [x] **Documentation** Architecture ✓ / Micro Guide ✓ / CLAUDE.md ✓
* [ ] **Migration** Phase 1 ⬜ / Phase 2 ⬜ / Phase 3 ⬜ / Phase 4 ⬜

*(Tick boxes as soon as a task is merged; Claude reloads fresh memory each convo.)*

---

## 6 · Current Project Status (10 Jul 2025)

### 🆕 Unified Architecture Implementation

**Completed**:
1. ✓ Created `UNIFIED_INTENT_BOT_1` combining rewrite + intent (GPT-4o-turbo)
2. ✓ Created `LLM_FORMATTER_BOT_4` for flexible Hebrew formatting (GPT-4o-mini)
3. ✓ Updated `botChainService.ts` with feature flags for gradual rollout
4. ✓ Created comprehensive test suites for both new bots
5. ✓ Updated documentation: ARCHITECTURE.md, MICRO_LEVEL_GUIDE.md
6. ✓ Created new branch `unified-gpt-architecture` with all changes
7. ✓ Fixed statistical queries - count_only flag now working correctly
8. ✓ Removed old bot containers and directories (rewrite-bot, intent-bot)

**Feature Flags** (currently enabled):
- `USE_UNIFIED_INTENT=true` - Enable unified intent bot ✅
- `USE_LLM_FORMATTER=true` - Enable LLM formatter ✅
- `UNIFIED_INTENT_ROLLOUT_PERCENTAGE=10` - Gradual rollout control

### Route Testing Results (10 Jul 2025)

**✅ Working Correctly:**
- Statistical queries (count_only) - "כמה החלטות בנושא X" returns count not list
- ANALYSIS routes trigger Evaluator correctly
- Basic DATA_QUERY routes use proper SQL templates

**⚠️ Issues Found:**
- UNCLEAR routes don't trigger Clarify bot (returns recent decisions instead)
- RESULT_REF routes don't retrieve conversation context properly

### Critical Fixes (from previous)

1. **Evaluator Bot (2E)** disabled on QUERY path – save GPT‑4 tokens.
2. **Ranker Bot (3Q)** skipped; results currently ordered by date.
3. **UUID4 bug fixed** – all `id` columns restored to `VARCHAR(36)`; migrations locked.

### 🔴 Critical Cache Bug Discovery

**Entity Persistence Issue**: System returns stale results when querying different decision numbers. Even with all cache layers disabled, the same decision (e.g., 2989) is returned for different queries.

**INCORRECTLY DISABLED** (need restoration):
* `checkIntentPatternCache()` - server/src/services/botChainService.ts:~200-250
* `storeIntentPattern()` - server/src/services/botChainService.ts:~250-300
* `normalizeQueryPattern()` - server/src/services/botChainService.ts:~300-350
* `checkResponseCache()` - server/src/services/botChainService.ts:~500-550
* `storeInCache()` - server/src/services/botChainService.ts:~550-600
* `generateCacheKey()` - server/src/services/botChainService.ts:~600-650

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
| Backend     |  5001 |                   |               |                |
| ~~Rewrite~~ |  ~~8010~~ | **Unified Intent** 8011 | SQL‑Gen 8012  | Ctx 8013       |
| Evaluator   |  8014 | Clarify 8015      | Ranker 8016   | **LLM Formatter** 8017 |
| Frontend    |  3001 | Nginx 80/443/8080 | Postgres 5433 | Redis 6380     |

**Note**: Rewrite Bot (8010) deprecated - functionality merged into Unified Intent Bot (8011)

---

## 7 · Temporary Overrides & Monitoring

* **Evaluator & Ranker** remain OFF unless explicitly required.
* Log `token_usage` & daily spend; alert > \$10 or p95 latency > 2 s.
* Use `SKIP_RANKER=true` env flag for truncating ranker until optimised.
* **NEW**: Monitor unified intent accuracy with `unified_intent_accuracy` metric
* **NEW**: Track formatter quality with `formatter_quality_score` metric

---

### 📋 Log Summary (7 Jul 2025)

**Unified Architecture Implementation**:
- New branch `unified-gpt-architecture` created
- All changes committed and ready for testing
- Documentation fully updated
- Feature flags configured for gradual rollout

**Backend Integration**:
- `botChainService.ts` updated with dual-flow support
- Old and new flows can run in parallel
- Percentage-based traffic splitting ready

**Next Actions Required**:
1. Deploy new bots to staging environment
2. Test with 10% traffic split
3. Monitor quality metrics and token usage
4. Gradually increase traffic percentage

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