#!/bin/bash

# Test SQL Engine directly
# Tests the SQL engine API endpoints

SQL_ENGINE_URL="http://localhost:8002/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Testing SQL Engine Direct API${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Function to test a query
test_query() {
    local query="$1"
    local desc="$2"
    
    echo -e "${YELLOW}Test:${NC} $desc"
    echo -e "${BLUE}Query:${NC} $query"
    echo -e "${GREEN}Response:${NC}"
    
    response=$(curl -s -X POST "$SQL_ENGINE_URL/process-query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"sessionId\": \"test-session\"}")
    
    # Pretty print the response
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    
    echo -e "\n${BLUE}========================================${NC}\n"
    sleep 1
}

# Test health first
echo -e "${YELLOW}Testing SQL Engine Health...${NC}"
curl -s "$SQL_ENGINE_URL/health" | jq '.'
echo -e "\n${BLUE}========================================${NC}\n"

# Test various query patterns
test_query "החלטה אחת בנושא בריאות מ2024" "Single decision - health 2024"
test_query "5 החלטות בנושא חינוך משנת 2023" "5 decisions - education 2023"
test_query "הבא 10 החלטות בנושא תחבורה מ2022" "10 decisions - transportation 2022"
test_query "תן לי 20 החלטות בנושא כלכלה משנת 2024" "20 decisions - economy 2024"

# Test if pattern is being matched correctly
echo -e "${YELLOW}Testing Pattern Matching...${NC}"
test_query "החלטות בנושא בריאות מ2024" "Decisions about health from 2024"
test_query "החלטות על ירושלים מ2024" "Decisions about Jerusalem from 2024"

echo -e "${GREEN}Test completed!${NC}"
