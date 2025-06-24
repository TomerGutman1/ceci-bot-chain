#!/bin/bash

# Quick test for the 9 new query types
# Version 2.3.2

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if we should use SQL Engine directly or through the main API
if [ "$USE_SQL_ENGINE_DIRECT" = "true" ]; then
    API_URL="${API_URL:-http://localhost:8002/api}"
    ENDPOINT="/process-query"
    REQUEST_FIELD="query"
else
    API_URL="${API_URL:-http://localhost/api}"
    ENDPOINT="/chat"
    REQUEST_FIELD="message"
fi

echo -e "${YELLOW}Testing 9 New Query Types - Quick Version${NC}"
echo "========================================"

# Simple test function
test_query() {
    local num="$1"
    local query="$2"
    
    echo -e "\n${YELLOW}[$num/9]${NC} $query"
    
    if [ "$USE_SQL_ENGINE_DIRECT" = "true" ]; then
        response=$(curl -s -X POST "$API_URL$ENDPOINT" \
            -H "Content-Type: application/json" \
            -d "{\"$REQUEST_FIELD\": \"$query\"}" \
            --max-time 10)
    else
        response=$(curl -s -k -X POST "$API_URL$ENDPOINT" \
            -H "Content-Type: application/json" \
            -d "{\"$REQUEST_FIELD\": \"$query\", \"sessionId\": \"quick-test\"}" \
            --max-time 10)
    fi
    
    if [ -z "$response" ]; then
        echo -e "${RED}✗ No response${NC}"
        return
    fi
    
    if [ "$USE_SQL_ENGINE_DIRECT" = "true" ]; then
        # Check SQL Engine response
        success=$(echo "$response" | jq -r '.success // false' 2>/dev/null)
        if [ "$success" = "true" ]; then
            echo -e "${GREEN}✓ SQL query successful${NC}"
            row_count=$(echo "$response" | jq -r '.metadata.row_count // 0' 2>/dev/null)
            echo "Rows returned: $row_count"
        else
            error=$(echo "$response" | jq -r '.error // "Unknown error"' 2>/dev/null)
            echo -e "${RED}✗ Error: $error${NC}"
        fi
    else
        # Check main API response
        intent=$(echo "$response" | jq -r '.intent // empty' 2>/dev/null)
        
        if [ "$intent" = "data_query" ]; then
            echo -e "${GREEN}✓ Recognized as data query${NC}"
            # Show first 150 chars of response
            message=$(echo "$response" | jq -r '.response // empty' 2>/dev/null | head -c 150)
            echo "Response: $message..."
        else
            echo -e "${RED}✗ Intent: $intent${NC}"
        fi
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
