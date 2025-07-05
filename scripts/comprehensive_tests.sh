#!/bin/bash
# Comprehensive test suite for bot chain improvements
# Tests routing, token efficiency, and response quality

echo "🧪 CECI Bot Chain - Comprehensive Test Suite"
echo "==========================================="
echo "Testing Date: $(date)"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# API endpoint
API_URL="http://localhost:5001/api/chat/test-bot-chain"
PASSED=0
FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local query="$2"
    local expected_intent="$3"
    local should_use_context="$4"
    local should_use_evaluator="$5"
    local max_tokens="$6"
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Test: $test_name${NC}"
    echo -e "Query: \"$query\""
    echo -e "Expected Intent: $expected_intent | Context Router: $should_use_context | Evaluator: $should_use_evaluator"
    echo ""
    
    # Send request
    start_time=$(date +%s%N)
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"sessionId\": \"test-$(date +%s)\"}" 2>&1)
    end_time=$(date +%s%N)
    
    # Calculate response time
    response_time=$(( ($end_time - $start_time) / 1000000 ))
    
    # Parse response
    success=$(echo "$response" | jq -r '.success // false')
    intent=$(echo "$response" | jq -r '.metadata.intent_type // .metadata.intent // ""')
    total_tokens=$(echo "$response" | jq -r '.metadata.token_usage.total_tokens // 0')
    cost=$(echo "$response" | jq -r '.metadata.token_usage.estimated_cost_usd // 0')
    bot_breakdown=$(echo "$response" | jq -r '.metadata.token_usage.bot_breakdown // {}')
    
    # Check which bots were used
    context_used="false"
    if echo "$bot_breakdown" | grep -q "CONTEXT_ROUTER"; then
        context_used="true"
    fi
    
    evaluator_used="false"
    if echo "$bot_breakdown" | grep -q "EVALUATOR"; then
        evaluator_used="true"
    fi
    
    # Validate results
    test_passed=true
    
    if [ "$success" != "true" ]; then
        echo -e "${RED}✗ Request failed${NC}"
        test_passed=false
    fi
    
    if [ "$intent" != "$expected_intent" ]; then
        echo -e "${RED}✗ Intent mismatch: got '$intent', expected '$expected_intent'${NC}"
        test_passed=false
    else
        echo -e "${GREEN}✓ Intent correct: $intent${NC}"
    fi
    
    if [ "$should_use_context" != "$context_used" ]; then
        echo -e "${RED}✗ Context Router usage mismatch: used=$context_used, expected=$should_use_context${NC}"
        test_passed=false
    else
        echo -e "${GREEN}✓ Context Router usage correct: $context_used${NC}"
    fi
    
    if [ "$should_use_evaluator" != "$evaluator_used" ]; then
        echo -e "${RED}✗ Evaluator usage mismatch: used=$evaluator_used, expected=$should_use_evaluator${NC}"
        test_passed=false
    else
        echo -e "${GREEN}✓ Evaluator usage correct: $evaluator_used${NC}"
    fi
    
    if [ "$total_tokens" -gt "$max_tokens" ]; then
        echo -e "${YELLOW}⚠ Token usage high: $total_tokens (max expected: $max_tokens)${NC}"
    else
        echo -e "${GREEN}✓ Token usage efficient: $total_tokens tokens${NC}"
    fi
    
    # Print metrics
    echo ""
    echo "📊 Metrics:"
    echo "   Response Time: ${response_time}ms"
    echo "   Total Tokens: $total_tokens"
    echo "   Estimated Cost: \$$cost"
    echo "   Bots Used:"
    echo "$bot_breakdown" | jq -r 'to_entries[] | "     - \(.key): \(.value.tokens) tokens"' 2>/dev/null || echo "     (no breakdown available)"
    
    # Update counters
    if [ "$test_passed" = true ]; then
        ((PASSED++))
        echo -e "\n${GREEN}✅ TEST PASSED${NC}"
    else
        ((FAILED++))
        echo -e "\n${RED}❌ TEST FAILED${NC}"
    fi
}

# Start testing
echo "🚀 Starting comprehensive test suite..."
echo ""

# Category 1: Simple Queries (should skip Context Router)
echo -e "\n${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}CATEGORY 1: Simple Queries (No Context Router Expected)${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"

run_test "Simple Topic Search" \
    "החלטות בנושא חינוך" \
    "QUERY" "false" "false" 1500

run_test "Limit Query" \
    "3 החלטות בנושא בריאות" \
    "QUERY" "false" "false" 1500

run_test "Government Query" \
    "החלטות ממשלה 37" \
    "QUERY" "false" "false" 1500

run_test "Ministry Query" \
    "החלטות משרד הביטחון" \
    "QUERY" "false" "false" 1500

run_test "Statistical Query" \
    "כמה החלטות יש בנושא תחבורה?" \
    "STATISTICAL" "false" "false" 1200

# Category 2: Hebrew Number Recognition
echo -e "\n${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}CATEGORY 2: Hebrew Number Recognition${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"

run_test "Hebrew Number - 37" \
    "ממשלה שלושים ושבע" \
    "QUERY" "false" "false" 1500

run_test "Hebrew Number - 21" \
    "החלטות ממשלה עשרים ואחת" \
    "QUERY" "false" "false" 1500

# Category 3: Context-Required Queries
echo -e "\n${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}CATEGORY 3: Context-Required Queries (Context Router Expected)${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"

run_test "Previous Reference" \
    "מה אמרתי קודם?" \
    "CLARIFICATION" "true" "false" 1800

run_test "Reference to Sent" \
    "ההחלטה ששלחת לי קודם" \
    "QUERY" "true" "false" 1800

run_test "Follow-up Query" \
    "עוד החלטות כמו ששאלתי קודם" \
    "QUERY" "true" "false" 1800

# Category 4: EVAL Queries (Evaluator Expected)
echo -e "\n${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}CATEGORY 4: Analysis Queries (Evaluator Expected)${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"

run_test "Direct Analysis Request" \
    "נתח את החלטה 2983" \
    "EVAL" "false" "true" 3000

run_test "Deep Analysis Request" \
    "אני רוצה ניתוח מעמיק של החלטה 1234" \
    "EVAL" "false" "true" 3000

run_test "Analysis with Context" \
    "נתח לי את ההחלטה האחרונה ששלחת" \
    "EVAL" "true" "true" 3500

# Category 5: Complex Queries
echo -e "\n${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}CATEGORY 5: Complex Queries${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"

run_test "Multi-Filter Query" \
    "החלטות ממשלה 37 בנושא חינוך מינואר 2024" \
    "QUERY" "false" "false" 1800

run_test "Multiple Ministries" \
    "החלטות משרד החינוך ומשרד הבריאות" \
    "QUERY" "false" "false" 1600

run_test "Date Range Query" \
    "החלטות בין ינואר למרץ 2024" \
    "QUERY" "false" "false" 1600

# Category 6: Edge Cases
echo -e "\n${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}CATEGORY 6: Edge Cases${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"

run_test "Typo Correction" \
    "החלטות בנושא חנוך" \
    "QUERY" "false" "false" 1500

run_test "Vague Query" \
    "מה עם הבריאות?" \
    "CLARIFICATION" "false" "false" 1200

run_test "Mixed Numbers" \
    "37 החלטות אחרונות" \
    "QUERY" "false" "false" 1500

# Summary
echo -e "\n${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST SUMMARY${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review the results above.${NC}"
    exit 1
fi
