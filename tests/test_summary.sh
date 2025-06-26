#!/bin/bash

# Ultra-concise test script - shows only summary with error tracking

echo "======================================"
echo "SQL Engine Test Summary"
echo "======================================"

API_URL="http://localhost:8002/api/process-query"

# Test groups
declare -A test_groups
test_groups[date_normalizer]=0
test_groups[fuzzy_matcher]=0
test_groups[entity_extraction]=0
test_groups[metrics]=0
test_groups[templates]=0
test_groups[formatter]=0
test_groups[error_handling]=0

# Track errors
declare -A errors

# Silent test function with error tracking
silent_test() {
    local group="$1"
    local query="$2"
    local expected="$3"
    local test_name="$4"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    
    if [ "$success" = "false" ]; then
        error=$(echo "$response" | jq -r '.error' 2>/dev/null)
        if [ -z "${errors[$group]}" ]; then
            errors[$group]="$test_name: $error"
        fi
        return 1
    fi
    
    if echo "$response" | grep -q "$expected" 2>/dev/null; then
        ((test_groups[$group]++))
        return 0
    else
        if [ -z "${errors[$group]}" ]; then
            errors[$group]="$test_name: Pattern '$expected' not found"
        fi
        return 1
    fi
}

# Run tests silently
echo -n "Running tests"

# Date normalizer tests
echo -n "."
silent_test "date_normalizer" "החלטות מאז 15/03/2023" "2023-03-15" "DD/MM/YYYY"
silent_test "date_normalizer" "החלטות מאז 1.1.2023" "2023-01-01" "DD.MM.YYYY"
silent_test "date_normalizer" "החלטות ממרץ 2023" "2023-03" "Hebrew month"

# Fuzzy matcher tests
echo -n "."
silent_test "fuzzy_matcher" "החלטות בנושא איכות הסביבה" "סביבה" "Environment"
silent_test "fuzzy_matcher" "החלטות בנושא פנסיה" "ותיקים" "Pension"
silent_test "fuzzy_matcher" "החלטות בנושא חנוך" "חינוך" "Typo"

# Entity extraction tests
echo -n "."
silent_test "entity_extraction" "הבא 20 החלטות" "LIMIT 20" "Limit"
silent_test "entity_extraction" "החלטות של נתניהו" "prime_minister" "PM"
silent_test "entity_extraction" "החלטות מ2023" "2023" "Year"

# Metrics tests
echo -n "."
silent_test "metrics" "החלטה 660" "execution_time" "Exec time"
silent_test "metrics" "החלטה 660" "query_id" "Query ID"

# Template tests
echo -n "."
silent_test "templates" "כמה החלטות בנושא חינוך בשנת 2023" "COUNT" "Count template"
silent_test "templates" "הבא החלטות של בנט בנושא קורונה" "בנט.*קורונה" "PM+Topic"

# Formatter tests
echo -n "."
silent_test "formatter" "כמה החלטות קיבלה ממשלה 37" "ממשלה 37" "Gov format"

# Error handling
echo -n "."
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "אבגדהוז"}' 2>/dev/null)
if echo "$response" | grep -q "לא הבנתי" 2>/dev/null; then
    ((test_groups[error_handling]++))
else
    errors[error_handling]="Unclear query: Expected guidance message"
fi

echo " Done!"
echo ""

# Display results
echo "Test Results:"
echo "============="
printf "%-20s %s\n" "Category" "Passed"
echo "------------------------------"
printf "%-20s %d/3\n" "Date Normalizer" "${test_groups[date_normalizer]}"
printf "%-20s %d/3\n" "Fuzzy Matcher" "${test_groups[fuzzy_matcher]}"
printf "%-20s %d/3\n" "Entity Extraction" "${test_groups[entity_extraction]}"
printf "%-20s %d/2\n" "Metrics" "${test_groups[metrics]}"
printf "%-20s %d/2\n" "Templates" "${test_groups[templates]}"
printf "%-20s %d/1\n" "Formatter" "${test_groups[formatter]}"
printf "%-20s %d/1\n" "Error Handling" "${test_groups[error_handling]}"
echo "------------------------------"

# Calculate total
total_passed=0
total_tests=15
for group in "${!test_groups[@]}"; do
    total_passed=$((total_passed + test_groups[$group]))
done

printf "%-20s %d/%d\n" "TOTAL" "$total_passed" "$total_tests"
echo ""

# Final verdict
if [ $total_passed -eq $total_tests ]; then
    echo "✅ All improvements working correctly!"
else
    echo "⚠️  Some improvements need attention."
    echo ""
    
    # Show first error from each failed category
    if [ ${#errors[@]} -gt 0 ]; then
        echo "First error in each category:"
        echo "=============================="
        for category in "${!errors[@]}"; do
            echo "$category: ${errors[$category]}"
        done
        echo ""
    fi
    
    echo "Run ./test_improvements_quick.sh for more details."
fi