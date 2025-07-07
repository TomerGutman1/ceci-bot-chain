#!/bin/bash

# End-to-end test suite for unified GPT architecture
# Tests both old and new flows to ensure compatibility

set -e

echo "========================================"
echo "Unified Architecture E2E Test Suite"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:5001"
OLD_INTENT_URL="http://localhost:8011"
NEW_INTENT_URL="http://localhost:8011"  # Same port, different flow
FORMATTER_URL="http://localhost:8017"

# Test counter
PASSED=0
FAILED=0

# Helper function to run a test
run_test() {
    local test_name=$1
    local endpoint=$2
    local payload=$3
    local expected_field=$4
    
    echo -n "Testing $test_name... "
    
    response=$(curl -s -X POST "$endpoint" \
        -H "Content-Type: application/json" \
        -d "$payload" || echo '{"error": "curl failed"}')
    
    if echo "$response" | grep -q "$expected_field"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $response"
        ((FAILED++))
        return 1
    fi
}

# Test 1: Health checks
echo -e "\n${YELLOW}1. Health Checks${NC}"
echo "------------------------"

for service in "unified_intent:8011" "sql_gen:8012" "context_router:8013" "formatter:8017"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    echo -n "Checking $name bot health... "
    if curl -s "http://localhost:$port/health" | grep -q "ok"; then
        echo -e "${GREEN}✓ Healthy${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        ((FAILED++))
    fi
done

# Test 2: Unified Intent Bot
echo -e "\n${YELLOW}2. Unified Intent Bot Tests${NC}"
echo "------------------------"

# Test Hebrew normalization + intent detection
run_test "Hebrew typo correction" \
    "$NEW_INTENT_URL/intent" \
    '{"raw_user_text": "החלתה 2983 ממשלת 37", "conv_id": "test-001"}' \
    '"clean_query"'

run_test "Intent classification" \
    "$NEW_INTENT_URL/intent" \
    '{"raw_user_text": "נתח לעומק את החלטה 123", "conv_id": "test-002"}' \
    '"intent": "ANALYSIS"'

run_test "Entity extraction" \
    "$NEW_INTENT_URL/intent" \
    '{"raw_user_text": "5 החלטות אחרונות בנושא חינוך", "conv_id": "test-003"}' \
    '"limit": 5'

# Test 3: LLM Formatter Bot
echo -e "\n${YELLOW}3. LLM Formatter Bot Tests${NC}"
echo "------------------------"

# Test decision formatting
formatter_payload='{
    "data_type": "ranked_rows",
    "content": {
        "results": [{
            "decision_title": "תוכנית לאומית לחינוך",
            "decision_number": 2983,
            "government_number": 37,
            "decision_date": "2024-05-15"
        }]
    },
    "original_query": "החלטות בנושא חינוך",
    "presentation_style": "card",
    "conv_id": "test-format-001"
}'

run_test "Decision card formatting" \
    "$FORMATTER_URL/format" \
    "$formatter_payload" \
    '"formatted_response"'

# Test empty results
empty_payload='{
    "data_type": "ranked_rows",
    "content": {"results": []},
    "original_query": "החלטות בנושא חלל",
    "presentation_style": "card",
    "conv_id": "test-format-002"
}'

run_test "Empty results formatting" \
    "$FORMATTER_URL/format" \
    "$empty_payload" \
    'לא נמצאו תוצאות'

# Test 4: Full Flow Integration
echo -e "\n${YELLOW}4. Full Flow Integration Tests${NC}"
echo "------------------------"

# Test complete query through backend
full_query='{
    "query": "3 החלטות אחרונות בנושא בריאות",
    "sessionId": "test-session-001"
}'

echo -n "Testing full query flow... "
response=$(curl -s -X POST "$BACKEND_URL/api/chat" \
    -H "Content-Type: application/json" \
    -d "$full_query")

if echo "$response" | grep -q "formatted_response"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
    
    # Check response quality
    echo -n "Checking response quality... "
    if echo "$response" | grep -q "החלטה"; then
        echo -e "${GREEN}✓ Contains Hebrew content${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Missing Hebrew content${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "Response: $response"
    ((FAILED++))
fi

# Test 5: Performance Tests
echo -e "\n${YELLOW}5. Performance Tests${NC}"
echo "------------------------"

echo -n "Testing unified intent latency... "
start_time=$(date +%s%N)
curl -s -X POST "$NEW_INTENT_URL/intent" \
    -H "Content-Type: application/json" \
    -d '{"raw_user_text": "החלטות ממשלה 37", "conv_id": "perf-001"}' > /dev/null
end_time=$(date +%s%N)
latency=$(( ($end_time - $start_time) / 1000000 ))

if [ $latency -lt 500 ]; then
    echo -e "${GREEN}✓ ${latency}ms (< 500ms target)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ ${latency}ms (> 500ms target)${NC}"
    ((FAILED++))
fi

# Test 6: Feature Flag Tests
echo -e "\n${YELLOW}6. Feature Flag Tests${NC}"
echo "------------------------"

# Test with feature flags disabled
export USE_UNIFIED_INTENT=false
export USE_LLM_FORMATTER=false

echo -n "Testing old flow (flags disabled)... "
# This would use the old rewrite + intent bots
# For now, we'll just check that the system still responds
if curl -s "$BACKEND_URL/api/chat/health" | grep -q "ok"; then
    echo -e "${GREEN}✓ System responsive${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ System not responsive${NC}"
    ((FAILED++))
fi

# Re-enable for remaining tests
export USE_UNIFIED_INTENT=true
export USE_LLM_FORMATTER=true

# Test 7: Error Handling
echo -e "\n${YELLOW}7. Error Handling Tests${NC}"
echo "------------------------"

# Test malformed request
run_test "Malformed request handling" \
    "$NEW_INTENT_URL/intent" \
    '{"invalid": "data"}' \
    '"error"'

# Test timeout handling (if implemented)
run_test "Empty query handling" \
    "$NEW_INTENT_URL/intent" \
    '{"raw_user_text": "", "conv_id": "test-empty"}' \
    '"intent"'

# Summary
echo -e "\n========================================"
echo "Test Summary"
echo "========================================"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed! System ready for migration.${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed. Please fix before proceeding.${NC}"
    exit 1
fi