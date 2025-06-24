#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="https://localhost/api/chat"

echo -e "${YELLOW}=== בדיקת תיקוני SQL Engine ===${NC}\n"

# Function to test a query
test_query() {
    local test_name="$1"
    local query="$2"
    local session_id="$3"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    echo "Query: $query"
    
    # Make the request and capture response
    response=$(curl -s -k -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "Accept: text/event-stream" \
        -d "{\"message\": \"$query\", \"sessionId\": \"$session_id\"}" \
        --max-time 10)
    
    # Check if response contains data
    if echo "$response" | grep -q "data:"; then
        echo -e "${GREEN}✓ Response received${NC}"
        # Extract and show first few lines
        echo "$response" | grep "^data:" | head -5
    else
        echo -e "${RED}✗ No valid response${NC}"
        echo "Response: $response"
    fi
    
    echo -e "\n---\n"
}

# Test 1: Committee query (should use high priority pattern)
test_query "ועדת הכספים" \
    "החלטות של ועדת הכספים" \
    "test-committee-fix"

# Test 2: Location query (should use tags_location field)
test_query "מיקום - ירושלים" \
    "החלטות על ירושלים שהתקבלו מאז 2020" \
    "test-location-fix"

# Test 3: Simple text search with quotes
test_query "חיפוש טקסט פשוט" \
    "\"קורונה\"" \
    "test-simple-text"

# Test 4: Committee with year
test_query "ועדה עם שנה" \
    "החלטות ועדת השרים לענייני חקיקה ב-2023" \
    "test-committee-year"

# Test 5: PM query (should have lower priority than committee)
test_query "ראש ממשלה" \
    "החלטות של נתניהו" \
    "test-pm-priority"

# Test 6: Count operativity
test_query "ספירת אופרטיביות" \
    "כמה החלטות דקלרטיביות היו ב-2024?" \
    "test-operativity"

# Test 7: Monthly trend
test_query "מגמה חודשית" \
    "כמה החלטות היו בכל חודש ב-2023?" \
    "test-monthly-trend"

# Test 8: Content search with date range
test_query "חיפוש עם טווח תאריכים" \
    "'קורונה' בין 2020-2021" \
    "test-content-daterange"

echo -e "${YELLOW}=== סיום בדיקות ===${NC}"
