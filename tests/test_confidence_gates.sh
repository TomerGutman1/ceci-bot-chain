#!/bin/bash

# === Test Confidence Gates ===
# Tests the confidence thresholds in intent detection and SQL conversion

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# API endpoint
CHAT_API="http://localhost:8080/api/chat"

# Counters
total_tests=0
passed_tests=0
failed_tests=0

# === Header ===
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Testing Confidence Gates${NC}"
echo -e "${BLUE}================================================${NC}"

# === Test Function ===
test_unclear_query() {
    local query="$1"
    local description="$2"
    
    ((total_tests++))
    
    echo -e "\n${YELLOW}Test $total_tests:${NC} $description"
    echo "Query: \"$query\""
    echo "Expected: Should return guidance/unclear message"
    
    # Call Chat API
    response=$(curl -s -X POST "$CHAT_API" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test-confidence\"}" \
        --no-buffer 2>/dev/null)
    
    # Extract content
    content=$(echo "$response" | grep '^data:' | tail -1 | sed 's/^data: //')
    
    # Check for guidance or unclear indicators
    if echo "$content" | grep -q "לא ברור\|לא הבנתי\|נסה\|פרט\|guidance\|unclear"; then
        echo -e "Result: ${GREEN}✓${NC} Returned guidance as expected"
        ((passed_tests++))
    else
        echo -e "Result: ${RED}✗${NC} Did not return proper guidance"
        echo "Response snippet: $(echo "$content" | head -c 200)..."
        ((failed_tests++))
    fi
}

test_clear_query() {
    local query="$1"
    local description="$2"
    
    ((total_tests++))
    
    echo -e "\n${YELLOW}Test $total_tests:${NC} $description"
    echo "Query: \"$query\""
    echo "Expected: Should process normally (high confidence)"
    
    # Call Chat API
    response=$(curl -s -X POST "$CHAT_API" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test-confidence\"}" \
        --no-buffer 2>/dev/null)
    
    # Extract content
    content=$(echo "$response" | grep '^data:' | tail -1 | sed 's/^data: //')
    
    # Check for actual results (not guidance)
    if echo "$content" | grep -q "נמצאו\|החלטה\|תאריך\|decision"; then
        echo -e "Result: ${GREEN}✓${NC} Processed query normally"
        ((passed_tests++))
    else
        echo -e "Result: ${RED}✗${NC} Failed to process clear query"
        echo "Response snippet: $(echo "$content" | head -c 200)..."
        ((failed_tests++))
    fi
}

# === Run Tests ===
echo -e "\n${CYAN}=== Testing Unclear/Low Confidence Queries ===${NC}"

test_unclear_query \
    "xyz" \
    "Gibberish - should trigger UNCLEAR"

test_unclear_query \
    "???" \
    "Just question marks - should trigger UNCLEAR"

test_unclear_query \
    "משהו" \
    "Too vague - should trigger guidance"

test_unclear_query \
    "תחבורה 2023 מאז אבל לא" \
    "Confusing structure - should trigger low confidence"

echo -e "\n${CYAN}=== Testing Clear/High Confidence Queries ===${NC}"

test_clear_query \
    "החלטות בנושא חינוך" \
    "Clear topic query"

test_clear_query \
    "החלטה 660 של ממשלה 37" \
    "Specific decision query"

test_clear_query \
    "כמה החלטות יש משנת 2023" \
    "Clear count query"

test_clear_query \
    "החלטות מאז 1.1.2023 בנושא בריאות" \
    "Clear date+topic query"

# === Summary ===
echo -e "\n${BLUE}=== Test Summary ===${NC}"
echo -e "Total tests: ${total_tests}"
echo -e "Passed: ${GREEN}${passed_tests}${NC}"
echo -e "Failed: ${RED}${failed_tests}${NC}"

if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}All confidence gate tests passed! 🎉${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Check confidence thresholds.${NC}"
    exit 1
fi
