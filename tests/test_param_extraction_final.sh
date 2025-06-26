#!/bin/bash

# Test parameter extraction from SQL engine - FINAL VERSION
echo "======================================"
echo "Parameter Extraction Test Summary"
echo "======================================"

API_URL="http://localhost:8002/api/process-query"
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_TESTS=0

# Function to test a query
test_query() {
    local test_name="$1"
    local query="$2"
    local expected_field="$3"
    local expected_value="$4"
    local check_type="${5:-exact}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Make the API call
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    if [ -z "$response" ]; then
        echo "✗ $test_name: No response from API"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    
    # Check if response is valid JSON
    if ! echo "$response" | jq empty 2>/dev/null; then
        echo "✗ $test_name: Invalid JSON response"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    
    # Extract the value based on expected field
    actual_value=""
    
    # First check if it's in metadata.params array
    if [[ "$expected_field" == "params[0]" ]]; then
        actual_value=$(echo "$response" | jq -r '.metadata.params[0] // empty' 2>/dev/null)
    elif [[ "$expected_field" == "params[1]" ]]; then
        actual_value=$(echo "$response" | jq -r '.metadata.params[1] // empty' 2>/dev/null)
    elif [[ "$expected_field" == "params[2]" ]]; then
        actual_value=$(echo "$response" | jq -r '.metadata.params[2] // empty' 2>/dev/null)
    elif [[ "$expected_field" == "template_used" ]]; then
        actual_value=$(echo "$response" | jq -r '.metadata.template_used // empty' 2>/dev/null)
    elif [[ "$expected_field" == "type" ]]; then
        actual_value=$(echo "$response" | jq -r '.type // empty' 2>/dev/null)
    elif [[ "$expected_field" == "sql_contains" ]]; then
        # Check if SQL contains expected pattern
        sql=$(echo "$response" | jq -r '.metadata.sql_query // empty' 2>/dev/null)
        if [[ "$sql" == *"$expected_value"* ]]; then
            actual_value="found"
            expected_value="found"
        fi
    elif [[ "$expected_field" == "any_param_contains" ]]; then
        # Check if any param contains the expected value
        params=$(echo "$response" | jq -r '.metadata.params[]' 2>/dev/null)
        if echo "$params" | grep -q "$expected_value"; then
            actual_value="found"
            expected_value="found"
        fi
    else
        # Try regular metadata field
        actual_value=$(echo "$response" | jq -r ".metadata.$expected_field // empty" 2>/dev/null)
    fi
    
    # Perform the check
    if [ "$check_type" = "exact" ]; then
        if [ "$actual_value" = "$expected_value" ]; then
            echo "✓ $test_name: $expected_field = $expected_value"
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            echo "✗ $test_name: Expected $expected_field=$expected_value, got $actual_value"
            FAIL_COUNT=$((FAIL_COUNT + 1))
            # Debug info
            if [ "$DEBUG" = "1" ]; then
                echo "  Full metadata: $(echo "$response" | jq '.metadata' 2>/dev/null)"
            fi
        fi
    elif [ "$check_type" = "contains" ]; then
        if [[ "$actual_value" == *"$expected_value"* ]]; then
            echo "✓ $test_name: $expected_field contains $expected_value"
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            echo "✗ $test_name: Expected $expected_field to contain $expected_value, got $actual_value"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    elif [ "$check_type" = "exists" ]; then
        if [ -n "$actual_value" ]; then
            echo "✓ $test_name: $expected_field exists with value: $actual_value"
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            echo "✗ $test_name: Expected $expected_field to exist"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    fi
}

echo "Running tests..."
echo

# Time parameter tests
echo "=== Time Tests ==="
test_query "Date normalize DD/MM/YYYY" "החלטות מ-15/03/2023" "params[0]" "2023-03-15"
test_query "Date normalize DD.MM.YYYY" "החלטות מ-15.03.2023" "params[0]" "2023-03-15"
test_query "Year exact" "החלטות משנת 2023" "sql_contains" "EXTRACT(YEAR"

# Topic tests
echo
echo "=== Topic Tests ==="
test_query "Fuzzy topic match" "החלטות בנושא סביבה" "params[0]" "%סביבה%" "contains"
# Fixed test - check that חינוך appears in ANY param
test_query "Topic with date" "החלטות בנושא חינוך מ-2023" "any_param_contains" "חינוך"

# Government tests
echo
echo "=== Government Tests ==="
test_query "Gov number template" "החלטות של ממשלה 36" "template_used" "החלטות לפי ממשלה"
test_query "Gov number params" "החלטות של ממשלה 36" "params[0]" "36"

# Quantity tests
echo
echo "=== Quantity Tests ==="
test_query "Count query type" "כמה החלטות" "type" "count"
test_query "Limit query" "5 החלטות" "sql_contains" "LIMIT 5"

# Content tests
echo
echo "=== Content Tests ==="
test_query "Text search" "שמכילות תקציב" "params[0]" "%תקציב%" "contains"
test_query "Urgent decisions" "החלטות דחופות" "params[0]" "%דחופ%" "contains"

echo
echo "======================================"
echo "Results: $PASS_COUNT passed, $FAIL_COUNT failed out of $TOTAL_TESTS tests"
echo "======================================"

if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi