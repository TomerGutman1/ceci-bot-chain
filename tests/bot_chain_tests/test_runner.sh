#!/bin/bash
# Test Runner for Bot Chain - Clean, Clear, Efficient

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API Configuration
API_URL="http://localhost:5001/api/chat/test-bot-chain"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="test_results_${TIMESTAMP}.log"

# Counters
PASSED=0
FAILED=0

# Function to run a single test
run_test() {
    local test_name="$1"
    local query="$2"
    local expected_check="$3"
    local check_description="$4"
    
    echo -e "\n${BLUE}▶ TEST: ${test_name}${NC}"
    echo -e "  Query: \"${query}\""
    echo -e "  Checking: ${check_description}"
    
    # Execute query using the test endpoint
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"sessionId\": \"test-$(date +%s)\"}" 2>&1)
    
    # Check HTTP response
    if [ $? -ne 0 ]; then
        echo -e "  ${RED}✗ FAILED${NC} - Network error"
        echo "  Error: $response" | head -1
        ((FAILED++))
        return
    fi
    
    # Extract key fields
    success=$(echo "$response" | jq -r '.success // false')
    error=$(echo "$response" | jq -r '.error // ""' | head -1)
    intent_type=$(echo "$response" | jq -r '.metadata.intent_type // ""')
    limit=$(echo "$response" | jq -r '.metadata.entities.limit // ""')
    government=$(echo "$response" | jq -r '.metadata.entities.government_number // ""')
    results_count=$(echo "$response" | jq -r '.results | length // 0')
    
    # Check if success=true
    if [ "$success" != "true" ]; then
        echo -e "  ${RED}✗ FAILED${NC} - Request failed"
        echo "  Error: $error"
        ((FAILED++))
        return
    fi
    
    # Evaluate the expected check
    if eval "$expected_check"; then
        echo -e "  ${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}✗ FAILED${NC}"
        echo "  Expected: $check_description"
        echo "  Got: intent_type=$intent_type, limit=$limit, government=$government, results=$results_count"
        ((FAILED++))
    fi
}

# Function to run a test group
run_test_group() {
    local group_name="$1"
    echo -e "\n${YELLOW}═══ $group_name ═══${NC}"
}

# Start testing
echo "Bot Chain Test Suite - $(date)"
echo "API: $API_URL"
echo "Log: $LOG_FILE"

# Group 1: Intent Recognition - Numbers
run_test_group "Intent Recognition - Numbers"

run_test "Limit Recognition 1" \
    "3 החלטות" \
    '[ "$limit" = "3" ]' \
    "limit should be 3"

run_test "Limit Recognition 2" \
    "תן לי 5 החלטות בנושא חינוך" \
    '[ "$limit" = "5" ]' \
    "limit should be 5"

run_test "Government Recognition 1" \
    "החלטות ממשלה 37" \
    '[ "$government" = "37" ]' \
    "government_number should be 37"

run_test "Government Recognition 2" \
    "ממשלה 36" \
    '[ "$government" = "36" ]' \
    "government_number should be 36"

# Group 2: Intent Type Recognition
run_test_group "Intent Type Recognition"

run_test "Query Intent" \
    "החלטות בנושא חינוך" \
    '[ "$intent_type" = "QUERY" ]' \
    "intent_type should be QUERY"

run_test "Statistical Intent" \
    "כמה החלטות יש בנושא בריאות?" \
    '[ "$intent_type" = "STATISTICAL" ]' \
    "intent_type should be STATISTICAL"

run_test "Eval Intent" \
    "נתח את החלטה 2983" \
    '[ "$intent_type" = "EVAL" ]' \
    "intent_type should be EVAL"

# Group 3: Results Validation
run_test_group "Results Validation"

run_test "Results Count Match Limit" \
    "3 החלטות אחרונות" \
    '[ "$results_count" = "3" ]' \
    "should return exactly 3 results"

run_test "Results Have Data" \
    "החלטות בנושא חינוך" \
    '[ "$results_count" -gt "0" ]' \
    "should return at least 1 result"

# Summary
echo -e "\n${YELLOW}═══ TEST SUMMARY ═══${NC}"
echo -e "Total: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
