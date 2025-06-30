#!/bin/bash
# Test specific bot behavior - focused tests

source ./test_runner.sh

# Override API URL for specific bot testing if needed
# API_URL="http://localhost:8002/api/process-query"

echo "Testing Specific Bot Behaviors"
echo "=============================="

# Group: Rewrite Bot Tests
run_test_group "Rewrite Bot - Text Normalization"

run_test "Typo Correction" \
    "החלטות בנושא חנוך" \
    '[ "$success" = "true" ]' \
    "should handle typo and succeed"

run_test "Mixed Format Numbers" \
    "החלטות משנת 2024" \
    '[ "$success" = "true" ]' \
    "should normalize year format"

# Group: SQL Generation Tests
run_test_group "SQL Generation - Date Handling"

run_test "Date From Query" \
    "החלטות מינואר 2024" \
    '[ "$success" = "true" ] && [ "$results_count" -gt "0" ]' \
    "should find decisions from January 2024"

run_test "Date Range Query" \
    "החלטות בין 01/01/2024 ל-31/03/2024" \
    '[ "$success" = "true" ]' \
    "should handle date range"

# Group: Router Tests
run_test_group "Router - Path Selection"

run_test "Query Path" \
    "החלטות בנושא תחבורה" \
    '[ "$intent_type" = "QUERY" ]' \
    "should route to QUERY path"

run_test "Statistical Path" \
    "כמה החלטות התקבלו השנה?" \
    '[ "$intent_type" = "STATISTICAL" ]' \
    "should route to STATISTICAL path"

run_test "Eval Path" \
    "הסבר את החלטה 1234" \
    '[ "$intent_type" = "EVAL" ]' \
    "should route to EVAL path"
