#!/bin/bash

# Comprehensive route testing for CECI Bot Chain
# Tests all possible routes and verifies correct bot sequence

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:5001/api/chat"
LOG_FILE="route_test_results.log"

# Initialize log
echo "CECI Bot Chain Route Testing - $(date)" > $LOG_FILE

# Function to test a query
test_query() {
    local test_name=$1
    local query=$2
    local expected_intent=$3
    local expected_route=$4
    local conv_id=$5
    local context_query=$6
    
    echo -e "\n${BOLD}========================================${NC}"
    echo -e "${BOLD}Test: ${test_name}${NC}"
    echo -e "Query: ${CYAN}${query}${NC}"
    echo -e "Expected Intent: ${BLUE}${expected_intent}${NC}"
    echo -e "Expected Route: ${BLUE}${expected_route}${NC}"
    
    # Set up context if needed
    if [ ! -z "$context_query" ]; then
        echo -e "\n${YELLOW}Setting up context...${NC}"
        echo -e "Context Query: ${CYAN}${context_query}${NC}"
        
        # Send context query
        curl -s -X POST $BASE_URL \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"$context_query\", \"conv_id\": \"$conv_id\", \"includeContext\": true}" \
            -N 2>/dev/null | grep -A 1 "metadata" | head -20
        
        sleep 2
    fi
    
    echo -e "\n${YELLOW}Sending main query...${NC}"
    
    # Send query and capture response
    response=$(curl -s -X POST $BASE_URL \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"conv_id\": \"$conv_id\", \"includeContext\": true}" \
        -N 2>/dev/null)
    
    # Extract metadata
    metadata=$(echo "$response" | grep -o '"metadata":{[^}]*}' | head -1)
    intent=$(echo "$metadata" | grep -o '"intent":"[^"]*"' | cut -d'"' -f4)
    
    # Log results
    echo -e "\n${BOLD}Results:${NC}"
    echo "Actual Intent: $intent"
    echo "$response" | grep -A 1 "content" | head -5
    
    # Check if intent matches
    if [ "$intent" == "$expected_intent" ]; then
        echo -e "\n${GREEN}✓ Intent PASSED${NC}"
        echo "✓ $test_name - Intent PASSED" >> $LOG_FILE
    else
        echo -e "\n${RED}✗ Intent FAILED - Expected: $expected_intent, Got: $intent${NC}"
        echo "✗ $test_name - Intent FAILED - Expected: $expected_intent, Got: $intent" >> $LOG_FILE
    fi
    
    # Brief pause
    sleep 2
}

# Function to check specific bot logs
check_bot_logs() {
    local bot_name=$1
    local search_term=$2
    
    echo -e "\n${YELLOW}Checking $bot_name logs for: $search_term${NC}"
    docker compose logs $bot_name --tail 50 | grep -A 2 -B 2 "$search_term" | tail -10
}

echo -e "${BOLD}${BLUE}CECI Bot Chain Route Testing${NC}"
echo -e "${BOLD}========================================${NC}"

# Test 1: Basic DATA_QUERY
echo -e "\n${BOLD}${YELLOW}1. BASIC DATA_QUERY TESTS${NC}"

test_query "Simple Decision Lookup" \
    "החלטה 2989" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-1"

test_query "Government Queries" \
    "החלטות ממשלה 37" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-2"

test_query "Topic Queries" \
    "החלטות בנושא חינוך" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-3"

# Test 2: Statistical Queries
echo -e "\n${BOLD}${YELLOW}2. STATISTICAL QUERY TESTS${NC}"

test_query "Count by Topic" \
    "כמה החלטות בנושא בריאות" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-4"

# Check if count_only flag was set
check_bot_logs "unified-intent-bot" "count_only"
check_bot_logs "sql-gen-bot" "count_decisions_by_topic"

test_query "Count by Government" \
    "כמה החלטות קיבלה ממשלה 36" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-5"

test_query "Count by Topic and Government" \
    "כמה החלטות בנושא תחבורה קיבלה ממשלה 37" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-6"

# Test 3: ANALYSIS Routes
echo -e "\n${BOLD}${YELLOW}3. ANALYSIS ROUTE TESTS${NC}"

test_query "Simple Analysis" \
    "נתח את החלטה 2989" \
    "ANALYSIS" \
    "UNIFIED_INTENT → SQL_GEN → EVALUATOR → LLM_FORMATTER" \
    "test-7"

# Check if evaluator was called
check_bot_logs "evaluator-bot" "evaluate"

test_query "Deep Analysis" \
    "נתח לעומק את החלטה 2983 מכל ההיבטים" \
    "ANALYSIS" \
    "UNIFIED_INTENT → SQL_GEN → EVALUATOR → LLM_FORMATTER" \
    "test-8"

# Test 4: UNCLEAR Routes
echo -e "\n${BOLD}${YELLOW}4. UNCLEAR ROUTE TESTS${NC}"

test_query "Ambiguous Query" \
    "מה?" \
    "UNCLEAR" \
    "UNIFIED_INTENT → CLARIFY" \
    "test-9"

# Check if clarify bot was called
check_bot_logs "clarify-bot" "clarify"

test_query "Incomplete Query" \
    "תראה לי החלטות" \
    "UNCLEAR" \
    "UNIFIED_INTENT → CLARIFY" \
    "test-10"

# Test 5: RESULT_REF Routes (with context)
echo -e "\n${BOLD}${YELLOW}5. RESULT_REF ROUTE TESTS (Context-Dependent)${NC}"

test_query "Pronoun Reference" \
    "ספר לי עוד על זה" \
    "RESULT_REF" \
    "UNIFIED_INTENT → CONTEXT_ROUTER → SQL_GEN → LLM_FORMATTER" \
    "test-11" \
    "החלטה 2989"

# Check if context router was called
check_bot_logs "context-router-bot" "route"

test_query "Ordinal Reference" \
    "מה ההחלטה השנייה?" \
    "RESULT_REF" \
    "UNIFIED_INTENT → CONTEXT_ROUTER → SQL_GEN → LLM_FORMATTER" \
    "test-12" \
    "החלטות בנושא חינוך"

# Test 6: Complex Cases
echo -e "\n${BOLD}${YELLOW}6. COMPLEX EDGE CASES${NC}"

test_query "Date Range Query" \
    "החלטות חינוך ב-2024" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-13"

test_query "Full Content Request" \
    "תן לי את התוכן המלא של החלטה 2989" \
    "DATA_QUERY" \
    "UNIFIED_INTENT → SQL_GEN → LLM_FORMATTER" \
    "test-14"

# Summary
echo -e "\n${BOLD}========================================${NC}"
echo -e "${BOLD}TEST SUMMARY${NC}"
echo -e "${BOLD}========================================${NC}"

passed=$(grep -c "✓" $LOG_FILE)
failed=$(grep -c "✗" $LOG_FILE)
total=$((passed + failed))

echo -e "Total Tests: $total"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"

echo -e "\nDetailed results in: $LOG_FILE"

# Check overall bot health
echo -e "\n${BOLD}${YELLOW}Bot Health Status:${NC}"
docker compose ps | grep -E "unified-intent-bot|sql-gen-bot|evaluator-bot|clarify-bot|context-router-bot|llm-formatter-bot" | awk '{print $1, $4}'