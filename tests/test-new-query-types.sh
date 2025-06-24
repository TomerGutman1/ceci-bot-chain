#!/bin/bash

# Test script for new SQL Engine query types
# Version 2.3.2 - Testing 9 new query types

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API endpoint
API_URL="${API_URL:-https://localhost/api}"

# Counter for test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test a query
test_query() {
    local test_name="$1"
    local query="$2"
    local expected_type="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}Testing: ${test_name}${NC}"
    echo "Query: $query"
    
    # Send request
    response=$(curl -s -k -X POST "$API_URL/chat/message" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test-session-new-queries\"}")
    
    # Check if response is valid
    if [ -z "$response" ]; then
        echo -e "${RED}✗ FAILED - No response${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Extract intent and response
    intent=$(echo "$response" | jq -r '.intent // empty' 2>/dev/null)
    message=$(echo "$response" | jq -r '.response // empty' 2>/dev/null)
    
    # Check if it's a data query
    if [ "$intent" != "data_query" ]; then
        echo -e "${RED}✗ FAILED - Intent: $intent (expected: data_query)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Check for specific patterns based on expected type
    case "$expected_type" in
        "count")
            if echo "$message" | grep -qE "נמצאו|מצאתי|יש|קיימות|התקבלו|[0-9]+ החלטות"; then
                echo -e "${GREEN}✓ PASSED - Found count result${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${RED}✗ FAILED - No count found in response${NC}"
                FAILED_TESTS=$((FAILED_TESTS + 1))
            fi
            ;;
        "multiple")
            if echo "$message" | grep -qE "נמצאו [0-9]+ החלטות|החלטה מס'|📊.*החלטות"; then
                echo -e "${GREEN}✓ PASSED - Found multiple results${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${RED}✗ FAILED - No results list found${NC}"
                FAILED_TESTS=$((FAILED_TESTS + 1))
            fi
            ;;
        "aggregate")
            if echo "$message" | grep -qE "סטטיסטיקה|התפלגות|השוואה|ועדות|חודש"; then
                echo -e "${GREEN}✓ PASSED - Found aggregate results${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${RED}✗ FAILED - No aggregate data found${NC}"
                FAILED_TESTS=$((FAILED_TESTS + 1))
            fi
            ;;
    esac
    
    # Show truncated response
    echo "Response preview: $(echo "$message" | head -n 3 | tr '\n' ' ')"
}

echo "=========================================="
echo "Testing New SQL Engine Query Types v2.3.2"
echo "=========================================="
echo "API URL: $API_URL"
echo "Date: $(date)"
echo ""

# Test 1: Decisions by Committee
echo -e "\n${YELLOW}=== 1. DECISIONS BY COMMITTEE ===${NC}"
test_query "Committee with year" "החלטות ועדת השרים לענייני חקיקה ב-2023" "multiple"
test_query "Committee without year" "החלטות של ועדת הכספים" "multiple"
test_query "Committee variations" "החלטות ועדה לענייני ביטחון" "multiple"

# Test 2: Count by Operativity
echo -e "\n${YELLOW}=== 2. COUNT BY OPERATIVITY ===${NC}"
test_query "Declarative with year" "כמה החלטות דקלרטיביות היו ב-2024?" "count"
test_query "Operative without year" "כמה החלטות אופרטיביות?" "count"
test_query "Declarative 2023" "כמה החלטות דקלרטיביות היו ב-2023?" "count"

# Test 3: Decisions by Location
echo -e "\n${YELLOW}=== 3. DECISIONS BY LOCATION ===${NC}"
test_query "Jerusalem since 2020" "החלטות על ירושלים שהתקבלו מאז 2020" "multiple"
test_query "Tel Aviv from 2022" "החלטות לגבי תל אביב מ-2022" "multiple"
test_query "Haifa decisions" "החלטות בנושא חיפה מאז 2021" "multiple"

# Test 4: Monthly Trend
echo -e "\n${YELLOW}=== 4. MONTHLY TREND ===${NC}"
test_query "Monthly 2023" "כמה החלטות היו בכל חודש ב-2023?" "aggregate"
test_query "Monthly 2024" "כמה החלטות היו בכל חודש ב-2024?" "aggregate"

# Test 5: PM and Topic
echo -e "\n${YELLOW}=== 5. PRIME MINISTER + TOPIC ===${NC}"
test_query "Netanyahu education" "מה עשה נתניהו בנושא חינוך?" "multiple"
test_query "Netanyahu security" "מה עשה נתניהו בנושא ביטחון?" "multiple"
test_query "Bennett economy" "מה עשה בנט בנושא כלכלה?" "multiple"

# Test 6: Recent Decisions (Relative Dates)
echo -e "\n${YELLOW}=== 6. RECENT DECISIONS - RELATIVE DATES ===${NC}"
test_query "Last 7 days" "החלטות מה-7 הימים האחרונים" "multiple"
test_query "Last 30 days" "החלטות מ-30 הימים האחרונים" "multiple"
test_query "Last 14 days" "החלטות מ-14 הימים האחרונים" "multiple"

# Test 7: Compare Topics
echo -e "\n${YELLOW}=== 7. COMPARE TOPICS ===${NC}"
test_query "Education vs Health 2024" "כמה החלטות חינוך לעומת בריאות ב-2024?" "aggregate"
test_query "Security vs Economy" "כמה החלטות ביטחון לעומת כלכלה?" "aggregate"
test_query "Transport vs Environment 2023" "כמה החלטות תחבורה לעומת סביבה ב-2023?" "aggregate"

# Test 8: Top Committees
echo -e "\n${YELLOW}=== 8. TOP COMMITTEES ===${NC}"
test_query "Top 3 committees" "3 הוועדות שהנפיקו הכי הרבה החלטות" "aggregate"
test_query "Top 5 committees" "5 הוועדות שהנפיקו הכי הרבה החלטות" "aggregate"
test_query "Top 10 committees" "10 הוועדות שהנפיקו הכי הרבה החלטות" "aggregate"

# Test 9: Content Search with Date Range
echo -e "\n${YELLOW}=== 9. CONTENT SEARCH WITH DATE RANGE ===${NC}"
test_query "Corona 2020-2021" "'קורונה' בין 2020-2021" "multiple"
test_query "Education 2022-2023" "'חינוך' בין 2022-2023" "multiple"
test_query "Budget 2023-2024" "'תקציב' בין 2023-2024" "multiple"

# Test 10: Edge Cases and Variations
echo -e "\n${YELLOW}=== 10. EDGE CASES & VARIATIONS ===${NC}"
test_query "Empty result" "החלטות על מאדים מ-2025" "multiple"
test_query "Hebrew month in range" "כמה החלטות בנושא רפואה היו מפברואר 2000 עד מרץ 2010?" "count"
test_query "Contextual year query" "וב2021?" "count"

# Summary
echo -e "\n${YELLOW}=========================================="
echo "TEST SUMMARY"
echo "==========================================${NC}"
echo -e "Total tests: ${TOTAL_TESTS}"
echo -e "Passed: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! 🎉${NC}"
    exit 0
else
    success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "\nSuccess rate: ${success_rate}%"
    exit 1
fi
