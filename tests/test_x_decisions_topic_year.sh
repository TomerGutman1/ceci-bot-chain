#!/bin/bash

# Test script for X decisions by topic and year pattern
# Tests the new comprehensive pattern for requesting specific number of decisions

API_URL="http://localhost:8002/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Testing X Decisions by Topic and Year Pattern${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Function to test a query
test_query() {
    local query="$1"
    local expected_count="$2"
    local expected_topic="$3"
    local expected_year="$4"
    
    echo -e "${YELLOW}Testing:${NC} $query"
    echo -e "${YELLOW}Expected:${NC} $expected_count decisions about $expected_topic from $expected_year"
    
    response=$(curl -s -X POST "$API_URL/process-query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"sessionId\": \"test-session\"}")
    
    # Extract actual count from response
    actual_count=$(echo "$response" | grep -o '"decision_number"' | wc -l)
    
    # Check if response contains the year
    if echo "$response" | grep -q "decision_date.*$expected_year"; then
        year_check="${GREEN}✓${NC}"
    else
        year_check="${RED}✗${NC}"
    fi
    
    # Check if response contains the topic
    if echo "$response" | grep -qi "$expected_topic"; then
        topic_check="${GREEN}✓${NC}"
    else
        topic_check="${RED}✗${NC}"
    fi
    
    echo -e "Results: Count check (found $actual_count), Year check $year_check, Topic check $topic_check"
    echo -e "${BLUE}---${NC}\n"
}

# Test 1: Single decision requests (החלטה אחת)
echo -e "${GREEN}=== Test Group 1: Single Decision Requests ===${NC}\n"

test_query "החלטה אחת בנושא בריאות מ2024" "1" "בריאות" "2024"
test_query "החלטה בנושא חינוך משנת 2023" "1" "חינוך" "2023"
test_query "הבא החלטה אחת בנושא תחבורה מ2022" "1" "תחבורה" "2022"
test_query "תן לי החלטה בנושא ביטחון משנת 2021" "1" "ביטחון" "2021"

# Test 2: Specific small numbers (2-5)
echo -e "${GREEN}=== Test Group 2: Small Number Requests (2-5) ===${NC}\n"

test_query "2 החלטות בנושא כלכלה מ2024" "2" "כלכלה" "2024"
test_query "3 החלטות בנושא רווחה משנת 2023" "3" "רווחה" "2023"
test_query "הבא 4 החלטות בנושא משפט מ2022" "4" "משפט" "2022"
test_query "תן לי 5 החלטות בנושא דיור משנת 2024" "5" "דיור" "2024"

# Test 3: Medium numbers (6-10)
echo -e "${GREEN}=== Test Group 3: Medium Number Requests (6-10) ===${NC}\n"

test_query "6 החלטות בנושא תעסוקה מ2023" "6" "תעסוקה" "2023"
test_query "7 החלטות בנושא איכות הסביבה משנת 2022" "7" "איכות הסביבה" "2022"
test_query "הבא 8 החלטות בנושא חקלאות מ2024" "8" "חקלאות" "2024"
test_query "תן לי 9 החלטות בנושא מדע משנת 2023" "9" "מדע" "2023"
test_query "10 החלטות בנושא תרבות מ2022" "10" "תרבות" "2022"

# Test 4: Larger numbers (11-20)
echo -e "${GREEN}=== Test Group 4: Large Number Requests (11-20) ===${NC}\n"

test_query "11 החלטות בנושא ספורט מ2024" "11" "ספורט" "2024"
test_query "15 החלטות בנושא תקשורת משנת 2023" "15" "תקשורת" "2023"
test_query "הבא 18 החלטות בנושא אנרגיה מ2022" "18" "אנרגיה" "2022"
test_query "תן לי 20 החלטות בנושא פנסיה משנת 2024" "20" "פנסיה" "2024"

# Test 5: Different topic variations
echo -e "${GREEN}=== Test Group 5: Topic Variations ===${NC}\n"

test_query "5 החלטות בנושא בריאות הציבור מ2024" "5" "בריאות הציבור" "2024"
test_query "3 החלטות בנושא חינוך מיוחד משנת 2023" "3" "חינוך מיוחד" "2023"
test_query "הבא 7 החלטות בנושא תחבורה ציבורית מ2022" "7" "תחבורה ציבורית" "2022"
test_query "תן לי 4 החלטות בנושא ביטחון פנים משנת 2021" "4" "ביטחון פנים" "2021"

# Test 6: Different year ranges
echo -e "${GREEN}=== Test Group 6: Different Years ===${NC}\n"

test_query "10 החלטות בנושא כלכלה מ2020" "10" "כלכלה" "2020"
test_query "8 החלטות בנושא בריאות משנת 2021" "8" "בריאות" "2021"
test_query "12 החלטות בנושא חינוך מ2022" "12" "חינוך" "2022"
test_query "15 החלטות בנושא תשתיות משנת 2023" "15" "תשתיות" "2023"
test_query "20 החלטות בנושא סביבה מ2024" "20" "סביבה" "2024"

# Test 7: Edge cases
echo -e "${GREEN}=== Test Group 7: Edge Cases ===${NC}\n"

test_query "1 החלטות בנושא מים מ2024" "1" "מים" "2024"  # 1 with plural form
test_query "החלטה אחת בנושא קורונה משנת 2020" "1" "קורונה" "2020"  # COVID topic
test_query "20 החלטות בנושא חירום מ2023" "20" "חירום" "2023"  # Max number

# Test 8: Natural language variations
echo -e "${GREEN}=== Test Group 8: Natural Language Variations ===${NC}\n"

test_query "תציג 5 החלטות בנושא רפואה מ2024" "5" "רפואה" "2024"
test_query "הצג לי 3 החלטות בנושא חינוך משנת 2023" "3" "חינוך" "2023"
test_query "הבא לי 7 החלטות בנושא ביטחון מ2022" "7" "ביטחון" "2022"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Test completed!${NC}"
echo -e "${BLUE}================================================${NC}"

# Bonus: Test actual chat endpoint with streaming
echo -e "\n${YELLOW}Bonus: Testing actual chat endpoint with streaming...${NC}\n"

test_chat_query() {
    local query="$1"
    echo -e "${BLUE}Chat Query:${NC} $query"
    
    # Note: This will show streaming response
    curl -X POST "http://localhost:8080/api/chat" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test-session\"}" \
        --no-buffer
    
    echo -e "\n${BLUE}---${NC}\n"
}

# Test a few queries via chat
test_chat_query "החלטה אחת בנושא בריאות מ2024"
test_chat_query "5 החלטות בנושא חינוך משנת 2023"
test_chat_query "הבא 10 החלטות בנושא תחבורה מ2022"
