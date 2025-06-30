#!/bin/bash
# Test edge cases and error handling

source ./test_runner.sh

echo "Testing Edge Cases and Error Handling"
echo "====================================="

# Group: Edge Cases
run_test_group "Edge Cases"

run_test "Empty Query" \
    "" \
    '[ "$success" = "false" ]' \
    "should fail gracefully on empty query"

run_test "Very Long Query" \
    "אני רוצה לראות את כל ההחלטות של ממשלת ישראל בנושא חינוך והשכלה גבוהה וכל מה שקשור לתקציבים ומלגות לסטודנטים ותוכניות לימודים חדשות ושינויים במערכת החינוך בשנים האחרונות כולל רפורמות ותוכניות חדשות" \
    '[ "$success" = "true" ]' \
    "should handle long queries"

run_test "Numbers Only" \
    "37" \
    '[ "$success" = "true" ]' \
    "should handle number-only query"

run_test "Special Characters" \
    "החלטות @#$% משנת 2024" \
    '[ "$success" = "true" ]' \
    "should handle special characters"

# Group: Ambiguous Queries
run_test_group "Ambiguous Query Handling"

run_test "Ambiguous Number" \
    "37 החלטות" \
    '[ "$limit" = "37" ] || [ "$government" = "37" ]' \
    "should resolve number context"

run_test "Multiple Topics" \
    "החלטות בנושא חינוך ובריאות" \
    '[ "$success" = "true" ]' \
    "should handle multiple topics"

# Group: Performance Tests
run_test_group "Performance Checks"

test_performance() {
    local query="$1"
    local max_time="$2"
    local start_time=$(date +%s.%N)
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>&1)
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    echo -e "\n${BLUE}▶ PERFORMANCE: $query${NC}"
    echo -e "  Max time: ${max_time}s"
    echo -e "  Actual: ${duration}s"
    
    if (( $(echo "$duration < $max_time" | bc -l) )); then
        echo -e "  ${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}✗ FAILED${NC} - Too slow"
        ((FAILED++))
    fi
}

test_performance "3 החלטות אחרונות" 5
test_performance "החלטות בנושא חינוך" 5
