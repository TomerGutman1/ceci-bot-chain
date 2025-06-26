#!/bin/bash

# Test all improvements made to the SQL Engine
# This script tests the improvements based on the recommendations in paste.txt

echo "============================================"
echo "SQL Engine Improvements Test Suite"
echo "Testing all improvements from version 2.4.8"
echo "============================================"
echo ""

# Base URL for the API
API_URL="http://localhost:8002/api/process-query"

# Counter for passed/failed tests
PASSED=0
FAILED=0

# Function to test a query - CONCISE VERSION WITH ERROR DETAILS
test_query() {
    local test_name="$1"
    local query="$2"
    local expected_pattern="$3"
    
    echo -n "🧪 $test_name: "
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract only SQL and success status
    sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null | head -1)
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    error=$(echo "$response" | jq -r '.error' 2>/dev/null)
    formatted=$(echo "$response" | jq -r '.formatted' 2>/dev/null | head -1)
    
    # Check if response contains expected pattern
    if [ "$success" = "true" ] && echo "$response" | grep -q "$expected_pattern" 2>/dev/null; then
        echo "✅ PASSED"
        ((PASSED++))
    else
        echo "❌ FAILED"
        echo "   Expected: $expected_pattern"
        if [ "$success" = "false" ]; then
            # Show the actual error message
            if [ "$error" != "null" ] && [ "$error" != "" ]; then
                echo "   Error: $error"
            elif [ "$formatted" != "null" ] && [ "$formatted" != "" ]; then
                echo "   Message: $formatted"
            fi
        else
            # Show truncated SQL if no error
            echo "   SQL: $(echo "$sql" | cut -c1-80)..."
        fi
        ((FAILED++))
    fi
}

# Function to test performance metrics - CONCISE VERSION
test_metrics() {
    local test_name="$1"
    local query="$2"
    
    echo -n "📊 $test_name: "
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract metrics
    exec_time=$(echo "$response" | jq -r '.metadata.execution_time' 2>/dev/null)
    query_id=$(echo "$response" | jq -r '.metadata.query_id' 2>/dev/null | cut -c1-8)
    
    # Check if response contains metadata with timing
    if [ "$exec_time" != "null" ] && [ "$exec_time" != "" ]; then
        echo "✅ PASSED (${exec_time}ms, id: ${query_id}...)"
        ((PASSED++))
    else
        echo "❌ FAILED (no metrics)"
        ((FAILED++))
    fi
}

echo "=========================================="
echo "1. Testing Date Normalizer Improvements"
echo "=========================================="

test_query "DD/MM/YYYY format" \
    "החלטות מאז 15/03/2023 בנושא חינוך" \
    "2023-03-15"

test_query "DD.MM.YYYY format" \
    "החלטות מאז 1.1.2023 בנושא בריאות" \
    "2023-01-01"

test_query "Hebrew month + year" \
    "החלטות ממרץ 2023" \
    "2023-03"

test_query "Hebrew month variant (מארס)" \
    "החלטות ממארס 2023" \
    "2023-03"

echo "=========================================="
echo "2. Testing Fuzzy Matcher (Synonyms)"
echo "=========================================="

test_query "Fuzzy: איכות הסביבה → סביבה" \
    "החלטות בנושא איכות הסביבה" \
    "סביבה"

test_query "Fuzzy: פנסיה → אזרחים ותיקים" \
    "החלטות בנושא פנסיה" \
    "ותיקים"

test_query "Fuzzy: מדע → מחקר" \
    "החלטות בנושא מדע" \
    "מחקר"

test_query "Fuzzy: חנוך → חינוך (typo)" \
    "החלטות בנושא חנוך" \
    "חינוך"

echo "=========================================="
echo "3. Testing Entity Extraction"
echo "=========================================="

test_query "Extract limit from query" \
    "הבא 20 החלטות בנושא תחבורה" \
    "LIMIT 20"

test_query "Extract PM and topic" \
    "החלטות של נתניהו בנושא ביטחון" \
    "prime_minister.*נתניהו"

test_query "Extract date range" \
    "החלטות בין 2020 ל2022" \
    "2020.*2022"

echo "=========================================="
echo "4. Testing Query Templates"
echo "=========================================="

test_query "COUNT_BY_TAG_AND_YEAR template" \
    "כמה החלטות בנושא חינוך בשנת 2023" \
    "COUNT.*חינוך.*2023"

test_query "LIST_BY_PM_AND_TOPIC template" \
    "הבא החלטות של בנט בנושא קורונה" \
    "בנט.*קורונה"

test_query "DECISIONS_SINCE_DATE_BY_TOPIC template" \
    "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך" \
    "2023-01-01.*חינוך"

echo "=========================================="
echo "5. Testing Metrics and Logging"
echo "=========================================="

test_metrics "Simple query metrics" \
    "החלטה 660"

test_metrics "Complex query metrics" \
    "החלטות בנושא בריאות משנת 2023"

echo "=========================================="
echo "6. Testing Formatter Improvements"
echo "=========================================="

test_query "Count format with context" \
    "כמה החלטות קיבלה ממשלה 37" \
    "ממשלה 37.*החלטות"

test_query "Count with topic and year" \
    "כמה החלטות בנושא חינוך היו ב2023" \
    "2023.*חינוך"

test_query "Aggregate formatting" \
    "כמה החלטות היו בכל חודש ב-2023" \
    "התפלגות.*חודש"

echo "=========================================="
echo "7. Testing Confidence Gates"
echo "=========================================="

# Test unclear query (should get helpful message)
test_query "Unclear query handling" \
    "אבגדהוז" \
    "לא הבנתי"

# Test low confidence query
test_query "Low confidence handling" \
    "משהו לא ברור לגמרי" \
    "נסה"

echo "=========================================="
echo "8. Testing Comprehensive Search"
echo "=========================================="

test_query "Search in tags + content" \
    "תמצא החלטות שעוסקות בחינוך" \
    "tags_policy_area.*summary.*decision_content"

test_query "Topic not in tags (fallback search)" \
    "החלטות בנושא קורונה" \
    "summary.*decision_content"

echo "=========================================="
echo "9. Testing Edge Cases"
echo "=========================================="

test_query "Single decision as array fix" \
    "החלטה אחת בנושא חינוך מ2024" \
    "formatted"

test_query "Empty results handling" \
    "החלטות בנושא אבגדהוז" \
    "לא נמצאו"

test_query "No government filter by default" \
    "החלטות בנושא חינוך" \
    "^((?!government_number = '37').)*$"

echo "=========================================="
echo "10. Testing Mixed Queries"
echo "=========================================="

test_query "Multiple conditions" \
    "20 החלטות בנושא בריאות מ2023 של ממשלה 37" \
    "LIMIT 20.*בריאות.*2023.*37"

test_query "Date + topic + limit" \
    "5 החלטות מאז 1.1.2023 בנושא תחבורה" \
    "5.*2023-01-01.*תחבורה"

echo "============================================"
echo "Test Summary:"
echo "============================================"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed! The improvements are working correctly."
else
    echo "⚠️  Some tests failed. Please review the failures above."
fi

echo ""
echo "💡 Note: Make sure the SQL Engine is running on port 8002"
echo "   You can start it with: cd sql-engine && npm start"