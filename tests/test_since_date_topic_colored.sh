#!/bin/bash

# Test script for "decisions since date + topic" queries with colored output
# Tests the new templates: DECISIONS_SINCE_DATE_BY_TOPIC and DECISIONS_SINCE_YEAR_BY_TOPIC

API_URL="http://localhost:8080/api/chat"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Testing 'Since Date + Topic' Pattern${NC}"
echo -e "${BLUE}================================================${NC}"

# Summary counters
total_tests=0
passed_tests=0
failed_tests=0

# Function to test a query
test_query() {
    local query="$1"
    local expected_desc="$2"
    local check_date="$3"
    local check_topic="$4"
    
    ((total_tests++))
    
    echo -e "${YELLOW}Testing:${NC} $query"
    echo "Expected: $expected_desc"
    
    # Make the API call
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test-session\"}")
    
    # Extract count from response
    count=$(echo "$response" | grep -o '"decision_number"' | wc -l)
    
    # Track if test passed
    test_passed=true
    
    # Color for count
    if [ $count -gt 0 ]; then
        count_display="${GREEN}Found $count decisions${NC}"
    else
        count_display="${RED}Found 0 decisions${NC}"
        test_passed=false
    fi
    
    # Extract years and topics for validation
    if [ -n "$check_date" ]; then
        # Count decisions after the check date
        valid_dates=$(echo "$response" | grep -o '"decision_date":"[0-9-]*"' | \
                     grep -E "\"($(echo $check_date | cut -d'-' -f1))-" | wc -l)
        if [ $valid_dates -gt 0 ]; then
            date_check="Date ${GREEN}✓${NC} ($valid_dates after $check_date)"
        else
            date_check="Date ${RED}✗${NC} (0 after $check_date)"
            test_passed=false
        fi
    else
        date_check="No date check"
    fi
    
    if [ -n "$check_topic" ]; then
        # Check if responses contain the topic
        topic_found=$(echo "$response" | grep -i "$check_topic" | wc -l)
        if [ $topic_found -gt 0 ]; then
            topic_check="Topic ${GREEN}✓${NC}"
        else
            topic_check="Topic ${RED}✗${NC}"
            test_passed=false
        fi
    else
        topic_check="No topic check"
    fi
    
    # Update counters
    if [ "$test_passed" = true ] && [ $count -gt 0 ]; then
        ((passed_tests++))
        status="${GREEN}[PASS]${NC}"
    else
        ((failed_tests++))
        status="${RED}[FAIL]${NC}"
    fi
    
    echo -e "Results: $count_display, $date_check, $topic_check $status"
    
    # If we got an error, show it
    if echo "$response" | grep -q '"error"'; then
        error=$(echo "$response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo -e "${RED}Error: $error${NC}"
    fi
    
    echo "---"
}

echo -e "\n${CYAN}=== Test Group 1: Full Date Format (DD.MM.YYYY) ===${NC}"
test_query "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך" \
           "Decisions since 01/01/2023 about חינוך" \
           "2023-01-01" "חינוך"

test_query "החלטות מאז 15.6.2022 בנושא בריאות" \
           "Decisions since 15/06/2022 about בריאות" \
           "2022-06-15" "בריאות"

test_query "חפש החלטות החל מ-1/7/2021 שקשורות לתחבורה" \
           "Decisions since 01/07/2021 about תחבורה" \
           "2021-07-01" "תחבורה"

test_query "הבא לי החלטות מאז ה-30.12.2020 שעוסקות בכלכלה" \
           "Decisions since 30/12/2020 about כלכלה" \
           "2020-12-30" "כלכלה"

echo -e "\n${CYAN}=== Test Group 2: Year Only Format ===${NC}"
test_query "תמצא החלטות מ2023 שעוסקות בחינוך" \
           "Decisions since 2023 about חינוך" \
           "2023" "חינוך"

test_query "החלטות משנת 2022 ואילך בנושא בריאות" \
           "Decisions since 2022 about בריאות" \
           "2022" "בריאות"

test_query "חפש לי כל החלטות מ2021 שקשורות לסביבה" \
           "Decisions since 2021 about סביבה" \
           "2021" "סביבה"

test_query "הבא החלטות מ2024 בנושא דיור" \
           "Decisions since 2024 about דיור" \
           "2024" "דיור"

echo -e "\n${CYAN}=== Test Group 3: Topics in Content/Summary ===${NC}"
test_query "תמצא לי החלטות מאז 2022 שעוסקות בקורונה" \
           "Decisions since 2022 about קורונה (in content)" \
           "2022" "קורונה"

test_query "החלטות מ-1.1.2023 שקשורות למשבר" \
           "Decisions since 01/01/2023 about משבר (in content)" \
           "2023-01-01" "משבר"

test_query "חפש החלטות מאז 2021 שמזכירות תקציב" \
           "Decisions since 2021 mentioning תקציב" \
           "2021" "תקציב"

echo -e "\n${CYAN}=== Test Group 4: Different Date Formats ===${NC}"
test_query "החלטות מאז ה-1-1-2023 בנושא ביטחון" \
           "Decisions since 01-01-2023 about ביטחון" \
           "2023-01-01" "ביטחון"

test_query "תמצא החלטות החל מ-15/06/23 שעוסקות ברווחה" \
           "Decisions since 15/06/2023 about רווחה" \
           "2023-06-15" "רווחה"

test_query "הבא החלטות מ-1.7.22 בנושא חקלאות" \
           "Decisions since 01/07/2022 about חקלאות" \
           "2022-07-01" "חקלאות"

echo -e "\n${CYAN}=== Test Group 5: Comprehensive Topic Search ===${NC}"
test_query "תמצא לי החלטות שעוסקות בחינוך" \
           "All decisions about חינוך (comprehensive)" \
           "" "חינוך"

test_query "חפש החלטות על תחבורה משנת 2023" \
           "Decisions about תחבורה since 2023" \
           "2023" "תחבורה"

test_query "הבא כל החלטות שקשורות לסביבה" \
           "All decisions related to סביבה" \
           "" "סביבה"

echo -e "\n${BLUE}=== Test Summary ===${NC}"
echo -e "Total tests: ${total_tests}"
echo -e "Passed: ${GREEN}${passed_tests}${NC}"
echo -e "Failed: ${RED}${failed_tests}${NC}"
if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! 🎉${NC}"
else
    echo -e "\n${RED}Some tests failed. Check the patterns above.${NC}"
fi
echo -e "${BLUE}================================================${NC}"
