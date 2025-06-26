#!/bin/bash

# Test script for Enhanced Parameter Extraction mechanism
# Tests the comprehensive parameter map implementation

API_URL="http://localhost:8002/api/process-query"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Counters
total_tests=0
passed_tests=0
failed_tests=0

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Testing Enhanced Parameter Extraction${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to test parameter extraction
test_params() {
    local query="$1"
    local expected_param="$2"
    local expected_value="$3"
    local test_name="$4"
    
    ((total_tests++))
    
    echo -n -e "${YELLOW}$test_name:${NC} "
    
    # Make request
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    
    if [ "$success" = "false" ]; then
        echo -e "${RED}❌ API Error${NC}"
        error=$(echo "$response" | jq -r '.error' 2>/dev/null | cut -c1-50)
        echo "  Error: $error..."
        ((failed_tests++))
        return
    fi
    
    # Check if parameter was extracted correctly
    # First try direct access
    extracted=$(echo "$response" | jq -r ".metadata.extracted_params.$expected_param" 2>/dev/null)
    
    # If null, try the nested structure (fallback)
    if [ "$extracted" = "null" ] || [ -z "$extracted" ]; then
        # Try nested structure for different categories
        case $expected_param in
            date_from|date_to|year_exact|relative_period)
                extracted=$(echo "$response" | jq -r '.metadata.extracted_params["TIME PARAMETERS"].'"$expected_param" 2>/dev/null)
                ;;
            tags_policy_area|topic*)
                extracted=$(echo "$response" | jq -r '.metadata.extracted_params["TOPIC PARAMETERS"].'"$expected_param" 2>/dev/null)
                ;;
            government_number|prime_minister|committee)
                extracted=$(echo "$response" | jq -r '.metadata.extracted_params["GOVERNMENT/POLITICAL"].'"$expected_param" 2>/dev/null)
                ;;
            tags_location|region_type)
                extracted=$(echo "$response" | jq -r '.metadata.extracted_params["GEOGRAPHY"].'"$expected_param" 2>/dev/null)
                ;;
            count_only|limit|single_result)
                extracted=$(echo "$response" | jq -r '.metadata.extracted_params["QUANTITY/AGGREGATION"].'"$expected_param" 2>/dev/null)
                ;;
            *)
                extracted="null"
                ;;
        esac
    fi
    
    if [ "$extracted" = "null" ] || [ -z "$extracted" ]; then
        echo -e "${RED}❌ Parameter not extracted${NC}"
        echo "  Expected: $expected_param = $expected_value"
        ((failed_tests++))
    elif [[ "$extracted" == *"$expected_value"* ]]; then
        echo -e "${GREEN}✅ $expected_param = $extracted${NC}"
        ((passed_tests++))
    else
        echo -e "${RED}❌ Wrong value${NC}"
        echo "  Expected: $expected_value"
        echo "  Got: $extracted"
        ((failed_tests++))
    fi
}

# Quick validation function (for summary mode)
quick_validate() {
    local query="$1"
    local check_sql="$2"
    local test_name="$3"
    
    ((total_tests++))
    echo -n "$test_name: "
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null | head -1)
    
    if echo "$sql" | grep -q "$check_sql"; then
        echo -e "${GREEN}✅${NC}"
        ((passed_tests++))
    else
        echo -e "${RED}❌${NC}"
        ((failed_tests++))
    fi
}

echo -e "\n${CYAN}=== Test Group 1: Time Parameters ===${NC}"
test_params "החלטות מאז 15/03/2023" "date_from" "2023-03-15" "Date from DD/MM/YYYY"
test_params "החלטות מאז 1.1.2023" "date_from" "2023-01-01" "Date from D.M.YYYY"
test_params "החלטות עד סוף 2023" "date_to" "2023-12-31" "Date to end of year"
test_params "החלטות בין 2021 ל-2023" "date_range" "2021.*2023" "Date range"
test_params "החלטות בשנת 2022" "year_exact" "2022" "Exact year"
test_params "החלטות בחודש מרץ 2023" "month_year" "month.*3.*year.*2023" "Month and year"
test_params "החלטות בחצי השנה האחרונה" "relative_period" "חצי השנה" "Relative period"

echo -e "\n${CYAN}=== Test Group 2: Topic Parameters ===${NC}"
test_params "החלטות בנושא חינוך" "tags_policy_area" "חינוך" "Official tag"
test_params "החלטות על רובוטיקה בחינוך" "topic_free" "רובוטיקה" "Free text topic"
test_params "החלטות בנושא איכות הסביבה" "topic_fuzzy" "סביבה" "Fuzzy match topic"
test_params "החלטות בעניין תחבורה ציבורית" "topic_context" "תחבורה" "Topic with context"

echo -e "\n${CYAN}=== Test Group 3: Government/Political ===${NC}"
test_params "החלטות של ממשלה 36" "government_number" "36" "Government number"
test_params "החלטות בתקופת נתניהו" "prime_minister" "נתניהו" "Prime minister"
test_params "החלטות של ועדת השרים לענייני ביטחון" "committee" "ביטחון" "Committee"

echo -e "\n${CYAN}=== Test Group 4: Geography ===${NC}"
test_params "החלטות בירושלים" "tags_location" "ירושלים" "Specific location"
test_params "החלטות באזור הצפון" "region_type" "צפון" "Region type"

echo -e "\n${CYAN}=== Test Group 5: Quantity/Aggregation ===${NC}"
test_params "כמה החלטות יש בנושא בריאות" "count_only" "true" "Count query"
test_params "הבא 5 החלטות אחרונות" "limit" "5" "Limit extraction"
test_params "החלטה אחת בנושא חינוך" "single_result" "true" "Single result"

echo -e "\n${CYAN}=== Test Group 6: Content Filters ===${NC}"
test_params "החלטות שמכילות את המילה תקציב" "full_text_query" "תקציב" "Full text search"
test_params "החלטות אופרטיביות בלבד" "operativity_filter" "אופרטיבי" "Operativity filter"
test_params "החלטה מספר 660" "decision_number" "660" "Decision number"

echo -e "\n${CYAN}=== Test Group 7: Display Type ===${NC}"
test_params "הצג רק כותרות של החלטות" "fields_subset" "כותרות" "Fields subset"
test_params "החלטות הכי חדשות קודם" "order_by" "decision_date DESC" "Order by"

echo -e "\n${CYAN}=== Test Group 8: Context/Clarity ===${NC}"
test_params "xyz" "clarification_needed" "true" "Unclear query detection"
test_params "וב-2021?" "follow_up_ref" "true" "Follow-up detection"

echo -e "\n${CYAN}=== Quick Validation: Complex Queries ===${NC}"
quick_validate "החלטות מאז 1.1.2023 בנושא חינוך" "decision_date >= .* AND.*חינוך" "Date + Topic"
quick_validate "5 החלטות אחרונות של ממשלה 37" "government_number.*37.*LIMIT 5" "Gov + Limit"
quick_validate "כמה החלטות בירושלים מ-2022" "COUNT.*ירושלים.*2022" "Count + Location + Year"

# Summary
echo -e "\n${BLUE}=== Summary ===${NC}"
echo -e "Total: ${total_tests}"
echo -e "Passed: ${GREEN}${passed_tests}${NC}"
echo -e "Failed: ${RED}${failed_tests}${NC}"

# Calculate pass rate
if [ $total_tests -gt 0 ]; then
    pass_rate=$((passed_tests * 100 / total_tests))
    echo -e "Pass Rate: ${pass_rate}%"
fi

# Exit code
if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}All parameter extraction tests passed! 🎉${NC}"
    exit 0
else
    echo -e "${RED}Some parameter extraction tests failed${NC}"
    exit 1
fi
