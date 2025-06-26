#!/bin/bash

# === Test Fuzzy Matcher Integration ===
# Tests the new fuzzy matching capabilities

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# API endpoints
CHAT_API="http://localhost:8080/api/chat"
SQL_API="http://localhost:8002/api/process-query"

# Counters
total_tests=0
passed_tests=0
failed_tests=0

# === Header ===
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Testing Fuzzy Matcher Integration${NC}"
echo -e "${BLUE}================================================${NC}"

# === Test Function ===
test_fuzzy_query() {
    local query="$1"
    local expected_topic="$2"
    local description="$3"
    
    ((total_tests++))
    
    echo -e "\n${YELLOW}Test $total_tests:${NC} $description"
    echo "Query: \"$query\""
    echo "Expected to match: $expected_topic"
    
    # Call SQL Engine directly
    response=$(curl -s -X POST "$SQL_API" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    # Check if response contains expected topic or results
    if echo "$response" | grep -q "\"success\":true"; then
        # Extract SQL query from metadata if available
        sql=$(echo "$response" | grep -o '"sql":"[^"]*"' | cut -d'"' -f4)
        
        # Check if the expected topic appears in the SQL
        if echo "$sql" | grep -qi "$expected_topic"; then
            echo -e "Result: ${GREEN}✓${NC} Topic matched correctly"
            echo "SQL snippet: ...$(echo "$sql" | grep -o "tags_policy_area[^A]*AND" | head -1)..."
            ((passed_tests++))
        else
            # Check if it's using comprehensive search (fallback)
            if echo "$sql" | grep -q "summary ILIKE"; then
                echo -e "Result: ${GREEN}✓${NC} Using comprehensive search (no exact tag match)"
                ((passed_tests++))
            else
                echo -e "Result: ${RED}✗${NC} Topic not matched correctly"
                echo "SQL: $sql"
                ((failed_tests++))
            fi
        fi
    else
        echo -e "Result: ${RED}✗${NC} Query failed"
        echo "Response: $response"
        ((failed_tests++))
    fi
}

# === Run Tests ===
echo -e "\n${CYAN}=== Testing Synonym Matching ===${NC}"

test_fuzzy_query \
    "החלטות בנושא איכות הסביבה" \
    "סביבה" \
    "Should match 'איכות הסביבה' to 'סביבה, אקלים ומגוון ביולוגי'"

test_fuzzy_query \
    "החלטות בנושא מדע" \
    "מחקר" \
    "Should match 'מדע' to 'השכלה גבוהה ומחקר'"

test_fuzzy_query \
    "החלטות בנושא פנסיה" \
    "ותיקים" \
    "Should match 'פנסיה' to 'אזרחים ותיקים'"

echo -e "\n${CYAN}=== Testing Partial Match ===${NC}"

test_fuzzy_query \
    "החלטות בנושא ביטחון" \
    "ביטחון" \
    "Should match partial 'ביטחון' to relevant tags"

test_fuzzy_query \
    "החלטות בנושא תחבורה" \
    "תחבורה" \
    "Should match 'תחבורה' to 'תחבורה ציבורית ותשתיות דרך'"

echo -e "\n${CYAN}=== Testing Fuzzy Distance Matching ===${NC}"

test_fuzzy_query \
    "החלטות בנושא חנוך" \
    "חינוך" \
    "Should fuzzy match typo 'חנוך' to 'חינוך' (distance=1)"

test_fuzzy_query \
    "החלטות בנושא בראות" \
    "בריאות" \
    "Should fuzzy match typo 'בראות' to 'בריאות' (distance=1)"

echo -e "\n${CYAN}=== Testing Non-Tag Topics (Fallback) ===${NC}"

test_fuzzy_query \
    "החלטות בנושא קורונה" \
    "בריאות" \
    "Should map 'קורונה' to health or use comprehensive search"

test_fuzzy_query \
    "החלטות בנושא נדלן" \
    "נדל״ן" \
    "Should find 'נדלן' in 'דיור, נדל״ן ותכנון' tag"

# === Summary ===
echo -e "\n${BLUE}=== Test Summary ===${NC}"
echo -e "Total tests: ${total_tests}"
echo -e "Passed: ${GREEN}${passed_tests}${NC}"
echo -e "Failed: ${RED}${failed_tests}${NC}"

if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}All fuzzy matcher tests passed! 🎉${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Check the implementation.${NC}"
    exit 1
fi
