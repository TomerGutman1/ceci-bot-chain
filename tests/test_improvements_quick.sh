#!/bin/bash

# Quick test for the new improvements - CONCISE VERSION WITH ERROR DETAILS

echo "=================================="
echo "Quick Test - New Improvements"
echo "=================================="
echo ""

API_URL="http://localhost:8002/api/process-query"
PASSED=0
FAILED=0

# Function to test and report concisely
test_feature() {
    local test_name="$1"
    local query="$2"
    local check_field="$3"
    local expected_pattern="$4"
    
    echo -n "Testing $test_name... "
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Check if request succeeded
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    
    if [ "$success" = "false" ]; then
        echo "❌ FAILED"
        error=$(echo "$response" | jq -r '.error' 2>/dev/null)
        formatted=$(echo "$response" | jq -r '.formatted' 2>/dev/null | head -1)
        echo "  Error: ${error:-$formatted}"
        ((FAILED++))
        return
    fi
    
    # Extract only the relevant field
    if [ "$check_field" = "metadata.sql_query" ]; then
        value=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null | head -3)
    elif [ "$check_field" = "metadata" ]; then
        value=$(echo "$response" | jq '.metadata' 2>/dev/null)
    else
        value=$(echo "$response" | jq -r ".$check_field" 2>/dev/null)
    fi
    
    # Check if pattern exists
    if echo "$value" | grep -q "$expected_pattern" 2>/dev/null; then
        echo "✅ PASSED"
        echo "  Found: $expected_pattern"
        ((PASSED++))
    else
        echo "❌ FAILED"
        echo "  Expected pattern: $expected_pattern"
        echo "  Got: $(echo "$value" | head -1 | cut -c1-60)..."
        ((FAILED++))
    fi
    echo ""
}

echo "1. Date Normalizer Tests:"
echo "-------------------------"
test_feature "מרץ 2023 normalization" \
    "החלטות ממרץ 2023" \
    "metadata.sql_query" \
    "2023-03"

echo "2. Fuzzy Matcher Tests:"
echo "------------------------"
test_feature "איכות הסביבה → סביבה" \
    "החלטות בנושא איכות הסביבה" \
    "metadata.sql_query" \
    "סביבה"

echo "3. Entity Extraction Tests:"
echo "---------------------------"
test_feature "Limit extraction" \
    "הבא 5 החלטות בנושא חינוך" \
    "metadata.sql_query" \
    "LIMIT 5"

echo "4. Metrics Tests:"
echo "-----------------"
test_feature "Execution time tracking" \
    "החלטה 660" \
    "metadata" \
    "execution_time"

test_feature "Query ID generation" \
    "החלטה 660" \
    "metadata" \
    "query_id"

echo "=================================="
echo "Summary:"
echo "=================================="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All quick tests passed!"
else
    echo "⚠️  Some tests failed. Check error details above."
fi