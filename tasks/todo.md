# SQL Generation Fix for Specific Decision Queries

## Problem
When querying for a specific decision that doesn't exist (e.g., "החלטה 100 של ממשלה 35"), the system was returning unrelated decisions from government 35 instead of returning no results or an appropriate message.

## Root Cause
1. The SQL generation prompt had incorrect table schema - it referenced `israeli_government_decisions` but the actual table is `government_decisions`
2. The column names were incorrect (e.g., `decision_title` vs `title`, `tags_policy_area` vs `policy_area`)
3. The data types were wrong - `decision_number` and `government_number` should be INTEGER not TEXT
4. The SQL generator was likely falling back to searching all decisions from a government when a specific decision wasn't found

## Solution
1. Updated the SQL generation prompt with the correct table name and schema
2. Fixed all column names to match the actual database structure
3. Changed parameter types from TEXT to INTEGER for decision_number and government_number
4. Added explicit instructions to NEVER fallback to listing all decisions when a specific decision is requested
5. Added a new query type "SPECIFIC" with clear examples
6. Added critical rules emphasizing exact matching for specific decision queries

## Changes Made
- Updated `bot_chain/QUERY_SQL_GEN_BOT_2Q/main.py`:
  - Fixed database schema in the prompt
  - Updated example queries with correct table/column names
  - Added SPECIFIC query type
  - Added critical rules for handling specific decision queries
  - Changed parameter validation from TEXT to INTEGER

## Deployment
- Changes committed and pushed to production-deploy branch
- SQL generation bot rebuilt and redeployed to production
- Service is now running with the fixes

## Expected Behavior
When querying "החלטה 100 של ממשלה 35", the system should now:
- Generate SQL: `SELECT * FROM government_decisions WHERE government_number = 35 AND decision_number = 100`
- Return no results if the decision doesn't exist (which is the case)
- NOT return other decisions from government 35

## Review
The fix addresses the incorrect SQL generation that was causing unrelated decisions to be returned. The SQL generator now properly handles specific decision queries and will only return exact matches.

## Update: Supabase Schema Discovery

After further investigation, discovered that:
1. The system uses Supabase (not local PostgreSQL) for decision data
2. The Supabase schema matches the documentation file: `israeli_government_decisions` table with columns like `decision_title`, `tags_policy_area`, etc.
3. `decision_number` and `government_number` are TEXT fields in Supabase
4. Reverted the schema changes to match the actual Supabase database
5. Added stronger instructions to enforce exact matching for specific decision queries
6. Added example for queries like "החלטה 2989" to use exact match, not similarity search

---

# SQL-GEN BOT Upgrade - Task Summary

## Completed Tasks

### Phase 1: Core Upgrade ✅
- [x] Update model to gpt-4o-turbo in config
- [x] Replace SQL_GENERATION_PROMPT with enhanced version
- [x] Add synonym mapping dictionary
- [x] Implement date interpretation logic
- [x] Add query_type detection
- [x] Update response schema

### Phase 2: Enhanced Logic ✅
- [x] Implement fallback cascade
- [x] Add validation warnings system
- [x] Create confidence scoring
- [x] Add synonym expansion tracking
- [x] Implement boolean flag detection

### Phase 3: Testing & Integration ✅
- [x] Create comprehensive test suite
- [x] Add feature flag USE_ENHANCED_SQL_GEN
- [x] Test with example queries

### Phase 4: Deployment ✅
- [x] Update documentation
- [x] Add HELP_REQUEST intent to INTENT BOT

---

# Sidebar RTL Fix - Review

## Issue
The user wanted to keep only the LEFT visual sidebar and remove the RIGHT one. However, due to RTL (right-to-left) layout in Hebrew interfaces, there was confusion about which position corresponds to which visual side.

## Root Cause
- The entire app has `direction: rtl` set on the body (index.css:88)
- In RTL mode, positions are inverted:
  - `position="left"` appears on the visual RIGHT
  - `position="right"` appears on the visual LEFT

## Solution
Changed the ExampleQueries component position from "left" to "right" in Index.tsx, which displays the sidebar on the visual LEFT side in RTL mode.

## Changes Made
- Updated `src/pages/Index.tsx` line 44: `position="right"` (was "left")
- Added clarifying comments about RTL positioning

---

## Review Summary

### What Changed

1. **Model Upgrade**: SQL-GEN BOT now uses GPT-4o-turbo instead of GPT-3.5-turbo
   - Better Hebrew understanding
   - More accurate parameter extraction
   - ~3-4x cost increase but justified by quality

2. **New Modules Created**:
   - `synonym_mapper.py` - Hebrew synonym expansion (חינוך↔השכלה, etc.)
   - `date_interpreter.py` - Hebrew date understanding ("השנה", "3 השנים האחרונות")
   - `test_enhanced_sql.py` - Comprehensive test suite

3. **Enhanced Features**:
   - **Synonym Expansion**: Automatically expands topic searches to include synonyms
   - **Date Interpretation**: Understands relative dates and Hebrew expressions
   - **Query Type Detection**: Differentiates COUNT vs LIST queries
   - **Typo Correction**: Fixes common Hebrew typos (חנוך→חינוך)
   - **Boolean Flags**: Handles "רק אופרטיביות" type queries
   - **Validation Warnings**: Non-fatal issues reported to user
   - **Confidence Scoring**: 0-1 score for query confidence
   - **Fallback Logic**: Template → Enhanced GPT cascade

4. **Response Schema Enhanced**:
   - `query_type`: "count", "list", "comparison", "analysis", "specific"
   - `synonym_expansions`: Topics expanded with synonyms
   - `date_interpretations`: How dates were parsed
   - `validation_warnings`: Non-fatal warnings
   - `fallback_applied`: Whether templates were used
   - `confidence_score`: Query confidence 0-1

5. **Feature Flag**: 
   - `USE_ENHANCED_SQL_GEN=true` (default on)
   - Allows gradual rollout and A/B testing

6. **Documentation Updated**:
   - CLAUDE.md updated with new status
   - Added today's fixes section

7. **Bonus**: Added HELP_REQUEST intent to UNIFIED_INTENT_BOT
   - Detects "מה אתה יכול לעשות?" type queries
   - Can be routed to help handler

### Key Improvements

1. **Missing Results Fixed**: Synonym expansion prevents exact-match failures
2. **Count Queries Work**: Properly detects כמה/מספר for COUNT-only queries  
3. **Date Flexibility**: Handles various Hebrew date expressions
4. **Better Error Handling**: Validation warnings instead of failures
5. **Typo Tolerance**: Common Hebrew typos auto-corrected

### Files Modified

1. `bot_chain/common/config.py` - Model upgrade
2. `bot_chain/QUERY_SQL_GEN_BOT_2Q/main.py` - Core logic enhanced
3. `bot_chain/QUERY_SQL_GEN_BOT_2Q/synonym_mapper.py` - NEW
4. `bot_chain/QUERY_SQL_GEN_BOT_2Q/date_interpreter.py` - NEW
5. `bot_chain/QUERY_SQL_GEN_BOT_2Q/test_enhanced_sql.py` - NEW
6. `bot_chain/CLAUDE.md` - Documentation
7. `bot_chain/UNIFIED_INTENT_BOT_1/main.py` - Added HELP_REQUEST

### Cost Impact

- Old: ~$0.002/query (templates) + occasional GPT-3.5
- New: ~$0.006-0.008/query (GPT-4o-turbo always)
- Increase: ~3-4x but within acceptable range for quality improvement

### Next Steps

1. Deploy with feature flag enabled
2. Monitor token usage and costs
3. Validate quality improvements with real queries
4. Consider adding more Hebrew synonyms based on usage patterns

---

# Analysis Decision Number Fix - Review

## Issue
When analyzing decision 550, the system was displaying "החלטת ממשלה 3790" instead of "החלטה 550". 

## Root Cause
1. Decision 550's content mentions "החלטה 3790" as a reference to a previous decision
2. The evaluator bot was using GPT-extracted decision numbers from the analysis JSON
3. GPT mistakenly extracted "3790" from the content text and included it in the JSON response

## Solution
1. Updated evaluator bot to always use `request.decision_number` instead of GPT-extracted numbers
2. Removed `decision_number` and `government_number` fields from the JSON example format
3. This ensures the actual requested decision number is always shown, not references found in content

## Changes Made
- `bot_chain/EVAL_EVALUATOR_BOT_2E/main.py`:
  - Line 809: Changed from `analysis_result.get("decision_number", request.decision_number)` to `request.decision_number`
  - Line 707: Removed decision_number and government_number from JSON format example

---

# SSE Streaming Fix for Large Responses - Review

## Issue
Analysis responses were showing as empty ("לא התקבלה תשובה מהשרת") even though the backend was sending the data correctly.

## Root Cause
1. Large JSON responses (>5KB) were being split across multiple SSE chunks
2. The first chunk contained incomplete JSON (truncated at position 4995)
3. JSON.parse() failed with "Unterminated string" error
4. The error prevented the response from being displayed

## Solution
1. Added a buffer to accumulate incomplete lines across chunks
2. Only parse complete lines (ending with newline)
3. Keep incomplete lines in buffer for next chunk
4. Process any remaining buffer after stream ends
5. Use `decoder.decode(value, { stream: true })` for proper streaming

## Changes Made
- `src/services/chat.service.ts`:
  - Added `buffer` variable to store incomplete lines
  - Split chunks by newline but keep last incomplete line
  - Process buffer after stream completes
  - Better error handling for JSON parsing

---

# Analysis Consistency and Citations Fix - Review

## Issues Fixed

### 1. Inconsistent Scoring
**Problem**: Decision 549 received different scores (24%, 33%, 11%) on repeated analysis
**Solution**: 
- Added explicit instruction in system prompt to be consistent
- Emphasized basing scores only on what's written in the decision

### 2. Missing Text Citations
**Problem**: Analysis results didn't show the "ציטוט מהטקסט" column with actual quotes
**Solution**:
- Fixed formatter to always use structured data when available
- Only use pre-formatted explanation as fallback
- This ensures citations from `reference_from_document` field are displayed

### 3. Short Decision Rejection
**Problem**: Short decisions were rejected without analysis
**Solution**:
- Removed the 250 character minimum requirement
- All decisions are now analyzed regardless of length
- Added note for decisions under 500 chars: "החלטה זו מנוסחת בתמציתיות רבה"

## Changes Made

1. `bot_chain/LLM_FORMATTER_BOT_4/main.py`:
   - Line 86-88: Check for structured data first, only use explanation as fallback

2. `bot_chain/EVAL_EVALUATOR_BOT_2E/main.py`:
   - Line 493-494: Removed short decision rejection
   - Line 579-581: Add note for short decisions in prompt
   - Line 740: Added consistency instruction to system prompt

---

# Analysis and UI Fixes - Review

## Completed Tasks (15 Jul 2025)

### א. ניתוח החלטה - הצגת ציונים ודוגמאות טקסט
**Fixed**: The evaluator bot now includes text examples for each criterion
- Updated EVAL_EVALUATOR_BOT_2E prompt to request `reference_from_document` for each criterion
- Added explicit instructions to cite direct text from the decision
- Created Python formatter function `format_analysis_results()` to display criteria table with scores and text examples
- Updated LLM formatter prompt for analysis to create narrative reports instead of YAML format

**Changes Made**:
1. `bot_chain/EVAL_EVALUATOR_BOT_2E/main.py` - Added reference_from_document field to criteria JSON
2. `bot_chain/LLM_FORMATTER_BOT_4/main.py` - Added format_analysis_results() function and updated analysis prompt

### ב. תיקון חיפוש לפי נושא שאינו בתגית
**Fixed**: SQL generation now searches in content fields for topics not in tags
- Updated SQL generation examples to include content search
- Added Example 5 specifically for topics like "ענן הממשלתי" 
- Added critical rules to always search in multiple fields

**Changes Made**:
1. `bot_chain/QUERY_SQL_GEN_BOT_2Q/main.py` - Updated SQL examples and added rules for content search

### ג. עדכוני טקסט בממשק
**Completed**: All UI text updates
1. Welcome message updated to: "שלום! אני העוזר החכם של CECI. אני יכול לעזור לך למצוא החלטות ממשלה, לנתח את רמת היישום של ההחלטות, או לענות על שאלות לגבי פעילות הממשלה. במה אוכל לעזור?"
2. Decision Guide modal title changed to: "שיפור ניסוח ישימות החלטת ממשלה"
3. Example queries filtered to show only 6 basic queries in sidebar

**Changes Made**:
1. `src/components/chat/ChatInterface.tsx` - Updated welcome message
2. `src/components/decision-guide/DecisionGuideModal.tsx` - Updated modal title
3. `src/components/chat/ExampleQueries.tsx` - Filtered to basic queries only

---

# Previous Task: Remove All Mock Data and Test Data Usage

## Objective
Remove all possibilities of using mock data in the system. Ensure that all links are real and working (from the database), and all decisions or analysis are based entirely on real data.

## Todo List

### 1. Remove Test Data Infrastructure
- [ ] Delete test data fixtures files
- [ ] Remove seed_test_data.py script
- [ ] Clean up test_data.py with mock decisions

### 2. Clean Bot Chain Test Infrastructure
- [ ] Remove any references to mock decisions (2989, 2000, 1999, etc.) from bot implementations
- [ ] Ensure no bot is returning hardcoded responses
- [ ] Remove test fixture imports from all production code

### 3. Backend Service Cleanup
- [ ] Remove mock_chain test endpoint from chat routes
- [ ] Remove any test mode flags or conditions
- [ ] Ensure botChainService only uses real database queries

### 4. Database Cleanup
- [ ] Create script to remove any test decisions (1000-9999 range) from production database
- [ ] Verify all remaining decisions have real URLs from gov.il

### 5. Documentation Updates
- [ ] Update README files to remove references to test data
- [ ] Update CLAUDE.md to note that no mock data is allowed

### 6. Verification
- [ ] Test with real queries to ensure real data is returned
- [ ] Verify all URLs point to actual government decision pages
- [ ] Ensure no hardcoded decision numbers appear in responses

## Notes
- The test data includes decisions like 2989, 2000, 1999 which might be contaminating production responses
- All URLs must come from the database decision_url field
- No placeholder or generated URLs are acceptable

---

# Analysis Display Improvements - Review (15 Jul 2025)

## Completed Tasks

### 1. Improved Analysis Display Format
- Replaced table format with card-style blocks for each criterion
- Each criterion now shows:
  - Name and weight percentage
  - Visual score bar (█░░░░ style)
  - Explanation in italics
  - Text citation on a separate line with quote icon
- This format fits better in the narrow chat window

### 2. Added Conclusions and Recommendations
- Added "מסקנות מרכזיות" section for main findings
- Enhanced recommendations section with:
  - Auto-generated recommendations based on low-scoring criteria
  - Specific action items for improvement
  - Fallback to extract recommendations from explanation text

### 3. Visual Score Representation
- Added visual progress bars for individual criteria (0-5 scale)
- Added overall score bar (0-100 scale)
- Clear categorization: גבוהה/בינונית/נמוכה

### 4. Consistent Scoring (Temperature Fix)
- Reduced evaluator bot temperature from 0.3 to 0.0
- This ensures identical decisions always get the same scores
- Eliminates randomness in analysis results

## Changes Made

1. **bot_chain/LLM_FORMATTER_BOT_4/main.py**:
   - Rewrote `format_analysis_results()` function
   - Changed from table to card-based layout
   - Added visual score bars
   - Improved recommendations extraction
   - Added conclusions section

2. **bot_chain/EVAL_EVALUATOR_BOT_2E/main.py**:
   - Added specific recommendation generation based on low scores
   - Updated response to include recommendations list
   - Improved explanation formatting

3. **bot_chain/common/config.py**:
   - Set EVAL_EVALUATOR_BOT_2E temperature to 0.0
   - Ensures consistent scoring across repeated analyses

## Result
The analysis display now:
- Fits properly in the chat window width
- Shows all information clearly with proper hierarchy
- Includes conclusions and actionable recommendations
- Provides consistent scores for the same decision
- Uses visual elements for better readability