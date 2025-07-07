# REWRITE Bot Enhancement Report

## Summary

Attempted to enhance the REWRITE bot to solve multiple query processing issues by transforming queries before they reach the intent detector. However, GPT-3.5-turbo is not reliably following the transformation instructions for Hebrew text.

## Changes Implemented

### 1. Enhanced REWRITE Bot Prompt
- Added query restructuring rules for:
  - Date range normalization (2010-2020 → בין 2010 ל-2020)
  - Year-only count simplification (כמה החלטות ממשלה היו בשנת X → כמה החלטות בשנת X)
  - Operational decision standardization (אופרטיביים → אופרטיביות)
  - Query structure simplification (removing filler words)

### 2. Enhanced Intent Keyword Corrections
- Added typo corrections: החלתות → החלטות
- Added operational variations
- Added topic/subject variations

### 3. Configuration Updates
- Maintained token limit at 250 for GPT-3.5-turbo
- Added debugging logs to see GPT responses

## Issues Encountered

### GPT-3.5 Non-Compliance
Despite multiple attempts with different prompt structures:
1. Complex structured prompt with detailed rules
2. Simplified prompt with examples
3. Ultra-simple prompt with exact string replacements

GPT-3.5-turbo consistently returns the original text without applying transformations.

## Alternative Solutions

### Option 1: Upgrade to GPT-4
- GPT-4 is better at following complex instructions
- Cost: ~10x more expensive than GPT-3.5
- Would likely solve the transformation issues

### Option 2: Deterministic Pre-Processor
Create a simple JavaScript/Python function that applies transformations without GPT:
```javascript
function preprocessQuery(query) {
  // Year-only counts
  query = query.replace(/כמה החלטות ממשלה היו בשנת (\d+)/, 'כמה החלטות בשנת $1');
  
  // Date ranges
  query = query.replace(/(\d{4})-(\d{4})/, '$1 ל-$2');
  
  // Operational decisions
  query = query.replace(/אופרטיביים/g, 'אופרטיביות');
  query = query.replace(/אופרטיבי/g, 'אופרטיביות');
  
  return query;
}
```

### Option 3: Fix Intent Detector Directly
Instead of preprocessing, fix the root issues in the intent detector:
1. Add better year-only count detection
2. Improve topic extraction to avoid capturing "ממשלה" incorrectly
3. Ensure operational decision type persists through pipeline

## Recommendation

Given that GPT-3.5 is not following Hebrew transformation instructions reliably, I recommend:

1. **Immediate**: Implement Option 3 - Fix the intent detector patterns directly
2. **Future**: Consider Option 2 - Add a deterministic preprocessor for common patterns
3. **If budget allows**: Test Option 1 - GPT-4 for complex query understanding

## Files Modified

1. `/bot_chain/MAIN_REWRITE_BOT_0/main.py`
   - Updated REWRITE_PROMPT multiple times
   - Enhanced intent keyword corrections
   - Added debugging logs

2. `/bot_chain/common/config.py`
   - Maintained max_tokens at 250

## Next Steps

1. Revert REWRITE bot to original simple spelling/grammar correction
2. Focus on fixing intent detector patterns
3. Consider adding deterministic preprocessing layer