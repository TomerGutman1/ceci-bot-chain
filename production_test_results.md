# Production Test Results - Example Queries
**Test Date**: 2025-07-17
**System**: https://ceci-ai.ceci.org.il/api/chat

## Summary

✅ **All 6 example queries succeeded!**
- No timeouts
- Count queries working correctly
- Response times: 2.2s - 7.7s (average ~3.2s)

## Detailed Test Results

### 1. "החלטות בנושא חינוך ממשלה 37"
- **Status**: ✅ SUCCESS
- **Response Time**: 2.77s
- **Results**: 10 decisions returned
- **Quality**: Correctly filtered for education topic and government 37
- **Intent**: DATA_QUERY
- **Entities**: `{"topic":"חינוך","government_number":"37"}`

### 2. "החלטה 2989"
- **Status**: ✅ SUCCESS
- **Response Time**: 2.61s
- **Results**: 1 decision returned (correct specific decision)
- **Quality**: Exact match for decision number 2989
- **Intent**: DATA_QUERY
- **Entities**: `{"decision_number":2989,"government_number":37}`

### 3. "כמה החלטות בנושא ביטחון קיבלה ממשלה 37"
- **Status**: ✅ SUCCESS
- **Response Time**: 2.31s
- **Results**: Count query returned **426** decisions
- **Quality**: Correct count format (not returning list), reasonable number
- **Intent**: DATA_QUERY
- **Entities**: `{"topic":"ביטחון","government_number":"37","count_only":true}`

### 4. "הראה החלטות אחרונות בנושא סביבה"
- **Status**: ✅ SUCCESS
- **Response Time**: 7.68s (longer due to 586 total results)
- **Results**: 10 recent environment decisions displayed (out of 586 total)
- **Quality**: Correctly sorted by date, showing most recent first
- **Intent**: DATA_QUERY
- **Entities**: `{"topic":"סביבה","limit":"אחרונות"}`

### 5. "החלטות של משרד החינוך"
- **Status**: ✅ SUCCESS
- **Response Time**: 2.18s
- **Results**: 10 decisions related to Ministry of Education
- **Quality**: Correctly filtered for ministry involvement
- **Intent**: DATA_QUERY
- **Entities**: `{"ministries":["משרד החינוך"]}`

### 6. "החלטות ממשלה ב2024 בנושא בריאות"
- **Status**: ✅ SUCCESS
- **Response Time**: 2.86s
- **Results**: 10 health decisions from 2024
- **Quality**: Correctly filtered by date range and topic
- **Intent**: DATA_QUERY
- **Entities**: `{"topic":"בריאות","date_range":{"start":"2024-01-01","end":"2024-12-31"}}`

## Key Observations

1. **Count Query Fixed**: Query #3 correctly returns a count (426) instead of a list
2. **No Timeouts**: All queries completed successfully within reasonable time
3. **Unified Intent Working**: All queries correctly identified as DATA_QUERY
4. **Entity Extraction**: Excellent extraction of topics, dates, ministries, and government numbers
5. **Response Times**: Generally fast (2-3s), with only the large result set (586 environment decisions) taking longer

## Performance Metrics

- **Average Response Time**: 3.24s
- **Fastest Query**: 2.18s (Ministry query)
- **Slowest Query**: 7.68s (Recent environment decisions - 586 total results)
- **Success Rate**: 100% (6/6)

## Cost Analysis

- **Average Cost per Query**: ~$0.0086
- **Total Test Cost**: ~$0.052
- **Token Usage**: ~1500-1550 tokens per query

## Conclusion

The production system is functioning well with all example queries working correctly. The critical issues mentioned in CLAUDE.md appear to have been resolved:
- ✅ Count queries work properly
- ✅ Specific decision lookups work
- ✅ Recent decisions queries work
- ✅ Ministry searches work
- ✅ No timeouts observed

The system is ready for production use with these example queries.