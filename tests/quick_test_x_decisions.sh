#!/bin/bash

# Quick test for X decisions by topic and year
# Focused test on key variations

API_URL="http://localhost:8080/api/chat"
SESSION_ID="test-$(date +%s)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Quick Test: X Decisions by Topic and Year ===${NC}\n"

test_query() {
    local query="$1"
    local desc="$2"
    
    echo -e "${YELLOW}Test:${NC} $desc"
    echo -e "${BLUE}Query:${NC} $query"
    echo -e "${GREEN}Response:${NC}"
    
    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"$SESSION_ID\"}" \
        --no-buffer | grep -o '"content":"[^"]*"' | sed 's/"content":"//g' | sed 's/"$//g' | sed 's/\\n/\n/g' | head -20
    
    echo -e "\n${BLUE}========================================${NC}\n"
    sleep 1
}

# Key test cases
test_query "החלטה אחת בנושא בריאות מ2024" "Single decision - health 2024"
test_query "5 החלטות בנושא חינוך משנת 2023" "5 decisions - education 2023"
test_query "הבא 10 החלטות בנושא תחבורה מ2022" "10 decisions - transportation 2022"
test_query "תן לי 20 החלטות בנושא כלכלה משנת 2024" "20 decisions - economy 2024"
test_query "3 החלטות בנושא ביטחון פנים מ2023" "3 decisions - internal security 2023"
test_query "החלטה בנושא קורונה משנת 2020" "Single decision - COVID 2020"
test_query "15 החלטות בנושא דיור מ2024" "15 decisions - housing 2024"

echo -e "${GREEN}Test completed!${NC}"
