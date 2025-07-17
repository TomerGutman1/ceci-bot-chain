# Count Query Debug Analysis

## Issue
The query "כמה החלטות בנושא ביטחון קיבלה ממשלה 37" returns:
- "נמצאו 1 החלטות רלוונטיות" (Found 1 relevant decisions)
- Shows an empty result with no title or data

## Expected Behavior
Should return: "נמצאו 23 החלטות" (or whatever the actual count is)

## Investigation Findings

### 1. Intent Detection (✅ Working)
- Unified Intent Bot correctly sets `count_only: True`
- Intent is `DATA_QUERY` with count_only flag

### 2. SQL Generation (❓ Unknown)
- Enhanced SQL Gen should set `query_type: "count"`
- Need to verify this is happening

### 3. Backend Count Detection (✅ Code is correct)
```typescript
const isCountQuery = template_used && (
  template_used.includes('count_') ||
  template_used === 'compare_governments'
) || (entities.operation === 'count' || intent === 'count') || 
(sqlResponse && sqlResponse.query_type === 'count');  // This was added
```

### 4. Count Query Execution (✅ Code exists)
- When `isCountQuery` is true, it executes a count query
- Returns: `[{count: X, decision_count: X}]`

### 5. Formatter Call (✅ Code is correct)
```typescript
if (isCountQuery) {
  dataType = 'count';
  content = mappedResults[0] || { count: 0 };
}
```

### 6. LLM Formatter (✅ Has count logic)
- Has `DataType.COUNT` handling
- Should format as "נמצאו X החלטות"

## Hypothesis
The issue might be:
1. Enhanced SQL Gen is not returning `query_type: "count"`
2. OR the count query detection is failing
3. OR the actual count query is returning a real result instead of a count

## Next Steps
1. Add more logging to backend to trace the exact flow
2. Check what the enhanced SQL gen is actually returning
3. Verify the count query is being executed vs regular query