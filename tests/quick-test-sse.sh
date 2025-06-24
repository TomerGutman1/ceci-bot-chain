#!/bin/bash

# Quick test for the 9 new query types - SSE version
# Version 2.3.4

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost/api}"
ENDPOINT="/chat"

echo -e "${YELLOW}Testing 9 New Query Types - SSE Version${NC}"
echo "========================================"

# Function to test a query and parse SSE response
test_query() {
    local num="$1"
    local query="$2"
    
    echo -e "\n${YELLOW}[$num/9]${NC} $query"
    
    # Make the request and capture the SSE stream
    response=$(curl -s -X POST "$API_URL$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"quick-test\"}" \
        --max-time 10)
    
    if [ -z "$response" ]; then
        echo -e "${RED}✗ No response${NC}"
        return
    fi
    
    # Extract the content from SSE response
    content=$(echo "$response" | grep "^data: " | head -1 | sed 's/^data: //')
    
    if [ -z "$content" ]; then
        echo -e "${RED}✗ Failed to parse response${NC}"
        echo "Raw response: $response"
        return
    fi
    
    # Parse JSON from the content
    if echo "$content" | jq -e . >/dev/null 2>&1; then
        type=$(echo "$content" | jq -r '.type // empty')
        message=$(echo "$content" | jq -r '.content // empty')
        query_type=$(echo "$content" | jq -r '.metadata.query_type // empty')
        service=$(echo "$content" | jq -r '.metadata.service // empty')
        
        if [ "$type" = "response" ] && [ -n "$message" ]; then
            echo -e "${GREEN}✓ Success${NC}"
            echo "Service: $service"
            echo "Query type: $query_type"
            echo "Response: $(echo "$message" | head -c 150)..."
        else
            echo -e "${RED}✗ Unexpected response type: $type${NC}"
        fi
    else
        echo -e "${RED}✗ Invalid JSON response${NC}"
        echo "Content: $content"
    fi
}

# Test all 9 new query types
test_query 1 "החלטות ועדת השרים לענייני חקיקה ב-2023"
test_query 2 "כמה החלטות דקלרטיביות היו ב-2024?"
test_query 3 "החלטות על ירושלים שהתקבלו מאז 2020"
test_query 4 "כמה החלטות היו בכל חודש ב-2023?"
test_query 5 "מה עשה נתניהו בנושא חינוך?"
test_query 6 "החלטות מה-7 הימים האחרונים"
test_query 7 "כמה החלטות חינוך לעומת בריאות ב-2024?"
test_query 8 "3 הוועדות שהנפיקו הכי הרבה החלטות"
test_query 9 "'קורונה' בין 2020-2021"

echo -e "\n${YELLOW}Testing complete!${NC}"
