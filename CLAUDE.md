# 🧠 CLAUDE MAIN MEMORY – CECI Bot Chain

<small>Last updated: **15 Jul 2025 (Rev‑7 - Analysis Display Enhanced)**</small>

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

## 7 · Current Project Status (15 Jul 2025)

### 🚀 Production Deployment Complete (15 Jul 2025)

**System is LIVE at**: https://ceci-ai.ceci.org.il

**Latest Deployment (15 Jul 2025 - 09:26 UTC)** 🆕:
1. ✅ **Analysis Display Redesigned** - Improved formatting for better readability
   - Changed from wide table to compact 3-column table (קריטריון | משקל | ציון)
   - Moved text citations to separate section at the end
   - Added extra line spacing between sections
   - Removed visual score bars for cleaner look
   - Set evaluator temperature to 0.0 for consistent scoring
   - Ensures analysis fits within chat window width

**Earlier Today (15 Jul 2025)** 🆕:
1. ✅ **Analysis Display Fixed** - Evaluator now shows scores and text examples for each criterion
   - Added `reference_from_document` field to show text citations
   - Created narrative formatting instead of YAML output
   - Python formatter for analysis results with criteria table
2. ✅ **Topic Search Enhanced** - SQL queries now search in content fields
   - Added content search for topics like "ענן הממשלתי"
   - Always searches in title, summary, and decision_content fields
3. ✅ **UI Text Updates**
   - Welcome message: "לנתח את רמת היישום של ההחלטות"
   - Decision Guide title: "שיפור ניסוח ישימות החלטת ממשלה"
   - Example queries: Filtered to show only 6 basic queries

**Earlier Deployment (14 Jul 2025 - 18:32 UTC)**:
1. ✅ **SQL-GEN BOT UPGRADED** - Now uses GPT-4o-turbo with enhanced capabilities
   - Hebrew synonym expansion (חינוך↔השכלה, ביטחון↔בטחון)
   - Date interpretation ("השנה", "3 השנים האחרונות")
   - Query type detection (COUNT vs LIST)
   - Typo correction (חנוך→חינוך)
   - Feature flag: `USE_ENHANCED_SQL_GEN=true`
   - Cost: ~$0.006-0.008/query (3-4x increase, acceptable)
2. ✅ **UNIFIED INTENT BOT** - Added HELP_REQUEST intent
   - Detects "מה אתה יכול לעשות?" queries
   - Ready for help/capabilities responses

**Earlier Today (14 Jul 2025)**:
1. ✓ Fixed full content display - only shows when explicitly requested "תוכן מלא"
2. ✓ Fixed analysis functionality - now properly formats and displays evaluator results
3. ✓ Increased LLM formatter MAX_TOKENS to 4000 (prevents cut-off responses)
4. ✓ **Decision Guide Export** - Added PDF and CSV export functionality
   - PDF: Visual score bars, color-coded criteria, English text
   - CSV/Excel: All criteria data with Hebrew headers, recommendations sheet

**Previous Fixes (13 Jul)**:
1. ✓ Fixed LLM formatter DataType enum error (500 errors)
2. ✓ Fixed FormatterResponse validation errors 
3. ✓ Prevented LLM from generating fake data
4. ✓ Added date display (DD/MM/YYYY) to all query results
5. ✓ URL validation - only gov.il URLs shown

**Unified Architecture Status**:
1. ✓ `UNIFIED_INTENT_BOT_1` deployed (GPT-4o-turbo) + HELP_REQUEST intent
2. ✓ `QUERY_SQL_GEN_BOT_2Q` deployed (GPT-4o-turbo) + enhanced features 🆕
3. ✓ `LLM_FORMATTER_BOT_4` deployed (GPT-4o-mini)
4. ✓ All services running healthy on production
5. ✓ SSL certificate active (Let's Encrypt)
6. ✓ Automated backups configured (3 AM daily)
7. ✓ Log rotation enabled

**Feature Flags** (currently enabled):
- `USE_UNIFIED_INTENT=true` - Enable unified intent bot ✅
- `USE_LLM_FORMATTER=true` - Enable LLM formatter ✅
- `USE_ENHANCED_SQL_GEN=true` - Enable enhanced SQL generation ✅ 🆕
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

### ✅ RESOLVED ISSUES (14 Jul 2025)

**Previously Critical Issues - NOW FIXED**:
1. ✓ **Analysis Functionality** - Fixed empty responses, proper formatting
2. ✓ **Full Content Display** - Only shows when explicitly requested
3. ✓ **Token Limits** - Increased to 4000 for complete responses
4. ✓ **URL Generation** - Uses only database URLs
5. ✓ **Multiple Decisions** - Correctly handles same decision numbers

**Remaining TODO**:
1. Restore cache systems safely (Priority 3)
2. Implement Reference Resolution integration (Priority 2)
3. Fix UNCLEAR routes (don't trigger Clarify bot)
4. Fix RESULT_REF routes (context retrieval)

### Service Ports (reference)

| Component   | Port  |                   |               |                |
| ----------- | ----- | ----------------- | ------------- | -------------- |
| Backend     |  5001 |                   |               |                |
| ~~Rewrite~~ |  ~~8010~~ | **Unified Intent** 8011 | SQL‑Gen 8012  | Ctx 8013       |
| Evaluator   |  8014 | Clarify 8015      | Ranker 8016   | **LLM Formatter** 8017 |
| Frontend    |  3001 | Nginx 80/443/8080 | Postgres 5433 | Redis 6380     |
| **Decision Guide** | 8018 |             |               |                |

**Note**: Rewrite Bot (8010) deprecated - functionality merged into Unified Intent Bot (8011)

---

## 8 · Temporary Overrides & Monitoring

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

### 🚀 Production Deployment Summary (13 Jul 2025)

**Deployment Complete**:
- Application live at https://ceci-ai.ceci.org.il
- All services deployed to DigitalOcean droplet (178.62.39.248)
- SSL certificate configured and auto-renewal enabled
- Database backups scheduled daily at 3 AM
- Log rotation configured for all containers
- Production deployment guide created at `PRODUCTION_DEPLOYMENT_GUIDE.md`

**Critical Fixes Applied**:
1. ✓ LLM formatter no longer generates fake data
2. ✓ Date formatting (DD/MM/YYYY) added to all results
3. ✓ Invalid URLs filtered out - only gov.il URLs shown
4. ✓ Empty results handled gracefully ("לא נמצאו תוצאות")

**Deployment Workflow**:
- Always use `production-deploy` branch
- Quick deploy: `ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && git pull && ./run-compose.sh up -d [service]"`
- See `PRODUCTION_DEPLOYMENT_GUIDE.md` for detailed instructions

---

*(End of main memory – keep additions succinct yet complete. Refresh only on real changes.)*